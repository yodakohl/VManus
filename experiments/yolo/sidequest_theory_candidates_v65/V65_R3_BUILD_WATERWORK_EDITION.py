#!/usr/bin/env python3
"""Build the complete V65 R3 nonmedical waterwork rival."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
YOLO = ROOT / "experiments" / "yolo"

SOURCE_RECORDS = YOLO / "sidequest_theory_candidates_v54" / "V54_SELECTED_SIX_BIO_RECORDS.tsv"
SOURCE_EVENTS = YOLO / "sidequest_theory_candidates_v60" / "V60_SELECTED_381_EVENT_LEDGER.tsv"
SOURCE_STATEMENTS = YOLO / "sidequest_theory_candidates_v61" / "V61_SELECTED_116_SOURCE_STATEMENTS.tsv"
SOURCE_MACHINE = YOLO / "sidequest_theory_candidates_v62" / "V62_SELECTED_116_REGISTER_TRANSITIONS.tsv"
SOURCE_PARSE_EVENTS = YOLO / "sidequest_theory_candidates_v63" / "V63_SELECTED_381_EVENT_TEMPLATE_LEDGER.tsv"
SOURCE_PARSE_FIELDS = YOLO / "sidequest_theory_candidates_v63" / "V63_SELECTED_135_FIELD_SLOT_PARSE.tsv"
SOURCE_PARSE_STATEMENTS = YOLO / "sidequest_theory_candidates_v63" / "V63_SELECTED_116_STATEMENT_SLOT_PARSE.tsv"
SOURCE_V64_SELECTION = YOLO / "sidequest_theory_candidates_v64" / "V64_FOUR_ROLE_SELECTION.md"

OUT_EVENTS = HERE / "V65_R3_281_EVENT_WATERWORK_LEDGER.tsv"
OUT_FIELDS = HERE / "V65_R3_115_FIELD_WATERWORK_EDITION.tsv"
OUT_STATEMENTS = HERE / "V65_R3_97_STATEMENT_COMPARISON.tsv"
OUT_RECORDS = HERE / "V65_R3_6_RECORD_WATERWORK_EDITION.tsv"
OUT_GRAPHS = HERE / "V65_R3_6_RECORD_PROCESS_STATE_GRAPHS.tsv"
OUT_COSTS = HERE / "V65_R3_12_RECORD_MODEL_ASSUMPTION_COSTS.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError(f"empty output: {path.name}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def biological(row: dict[str, str]) -> bool:
    return row["record_unit_id"].startswith("B")


FIXED_VALUE_CLAUSE = {
    "MASS?": "MASS?=vorgesehenen Mengenwert buchen",
    "ANWENDEN?": "ANWENDEN?=aktive Charge am gesetzten Arbeitsziel einsetzen",
    "BEREIT?": "BEREIT?=Freigabestand der aktiven Charge prüfen",
    "ANSATZ?": "ANSATZ?=aktiven Arbeitsansatz aufnehmen",
    "ZIEL?": "ZIEL?=Arbeitsziel setzen oder bestätigen",
    "KLAR?": "KLAR?=Klarzustand der aktiven Charge prüfen",
    "VORIGES?": "VORIGES?=vorige Charge wieder aufnehmen",
    "ANTEIL?": "ANTEIL?=bezeichnete Teilcharge wählen",
    "TEMPERIEREN?": "TEMPERIEREN?=aktive Charge gelinde erwärmen",
    "SPÜLEN?": "SPÜLEN?=aktiven Lauf spülen und abschließen",
    "ABLASSEN?": "ABLASSEN?=aktive Charge ablassen und abschließen",
}

TEMPLATE_CLAUSE = {
    "PARAMETER_ASSIGN": "Mengen-/Parameterslot setzen",
    "TARGET_ASSIGN": "Ziel-/Relationsslot setzen",
    "LINK_ACTIVE": "aktiven Arbeitsstand verknüpfen",
    "STATE_GATE": "Bereit-/Klarstand prüfen",
    "ACTION_APPLY": "aktive Charge an der Station einsetzen",
    "ACTION_TEMPER": "aktive Charge temperieren",
    "TERMINAL_FLUSH": "Leitung spülen und committen",
    "TERMINAL_DRAIN": "Charge ablassen und committen",
    "SELECT_PART": "Teilcharge wählen",
    "SELECT_PREVIOUS": "Vorcharge aufnehmen",
}

PHASES = {
    "SETUP": {
        "sentence": "An {station} Beckenrand, Zulauf und Filteraufnahme prüfen; den Ausgangsstand als lokalen Anlagenposten eröffnen",
        "fillers": ("Beckenrand und Fugen sichten", "Zulauf vorerst schließen", "Filteraufnahme leeren", "Ausgangsstand im Anlagenbuch markieren"),
    },
    "CHARGE": {
        "sentence": "Vorratswasser an {station} bereitstellen, die vorgesehene Charge zuführen und den Füllstand markieren",
        "fillers": ("Vorratscharge bereitstellen", "Zuführung öffnen", "Wasser in das Becken einlassen", "Füllstand am Randzeichen prüfen"),
    },
    "ROUTE": {
        "sentence": "Den Leitungszweig an {station} wählen, den Schieber öffnen und die Charge zur gebuchten Zielstation führen",
        "fillers": ("Leitungszweig wählen", "Schieber am Abgang öffnen", "Fluss zur Zielstation führen", "Leitungsadresse im Register notieren"),
    },
    "HEAT": {
        "sentence": "Die aktive Beckencharge an {station} gelinde erwärmen, mit der Handprobe kontrollieren und warm halten",
        "fillers": ("Wärmequelle am Becken anlegen", "Charge gelinde erwärmen", "Wärme mit der Handprobe prüfen", "warmen Stand halten"),
    },
    "SERVICE": {
        "sentence": "Eine abgeteilte Charge an {station} auf das technische Arbeitsziel geben, den Durchgang beobachten und den Rest auffangen",
        "fillers": ("Arbeitsziel an der Station bereitstellen", "Teilcharge am Ziel einsetzen", "Durchgang beobachten", "Restcharge im Auffanggefäß sammeln"),
    },
    "CIRCULATE": {
        "sentence": "Die Charge von {station} über Rinne und Gefälle umlaufen lassen, den Rücklauf auffangen und erneut zuführen",
        "fillers": ("obere Rinne füllen", "Charge über das Gefälle umlaufen lassen", "Rücklauf im unteren Becken auffangen", "Rücklauf erneut zuführen"),
    },
    "SETTLE": {
        "sentence": "Die Charge an {station} stehen lassen, Klarlauf und Bodensatz trennen und den erreichten Stand buchen",
        "fillers": ("Charge ruhig stehen lassen", "klaren Oberlauf abnehmen", "Bodensatz zurückhalten", "Klarstand im Register buchen"),
    },
    "FILTER": {
        "sentence": "Das Filtertuch an {station} spannen, die Charge hindurchführen, Rückstand abnehmen und Filtrat auffangen",
        "fillers": ("Filtertuch oder Sieb einsetzen", "Charge durch den Filter führen", "Rückstand vom Filter abnehmen", "Filtrat im Zielbecken auffangen"),
    },
    "FLUSH": {
        "sentence": "Frisches Wasser an {station} zuführen, den Leitungsweg bis zum klaren Lauf spülen und den Spülposten schließen",
        "fillers": ("Spülwasser zuführen", "Leitung bis zum klaren Lauf spülen", "Spülrest getrennt auffangen", "Spülgang schließen"),
    },
    "DRAIN": {
        "sentence": "Den unteren Ablauf an {station} öffnen, die Charge in den Sammellauf ablassen, Restlauf prüfen und den Posten schließen",
        "fillers": ("unteren Ablauf öffnen", "Charge in den Sammellauf ablassen", "Restlauf am Auslass beobachten", "Ablauf wieder schließen"),
    },
    "RETURN": {
        "sentence": "Die Rücklaufleitung an {station} öffnen, den Restbestand zur Vorstation zurückführen und die Übergabe buchen",
        "fillers": ("Rücklaufleitung öffnen", "Restcharge zurückführen", "vorigen Arbeitsstand aufnehmen", "Rückgabe an die Vorstation buchen"),
    },
    "MAINTENANCE": {
        "sentence": "Filter, Leitungsöffnung und Beckenrand an {station} reinigen, lose Rückstände entfernen und die Anlage wieder einsetzen",
        "fillers": ("Filter lösen", "Leitungsöffnung ausstreichen", "Beckenrand reinigen", "Bauteil wieder einsetzen"),
    },
    "HANDOFF": {
        "sentence": "Die fertige Charge an {station} markieren, der nächsten Station übergeben und den offenen Arbeitsstand fortschreiben",
        "fillers": ("fertige Charge markieren", "Zielstation bestätigen", "Charge an den nächsten Lauf übergeben", "offenen Arbeitsstand fortschreiben"),
    },
}

ASSUMPTION_WEIGHTS = {
    "EXEMPLAR_FILL": 1,
    "LOCAL_PROCESS": 1,
    "MEDIUM": 1,
    "STATION_OR_TARGET": 1,
    "FILTER_OR_RETURN_MECHANISM": 1,
    "DOMAIN_PURPOSE": 2,
    "HUMAN_ROLE_OR_BODY": 2,
}


RECORD_CONFIG = {
    "B1": {
        "station": "Grundbecken A mit Wärmestelle W1, Rinne R1 und Rücklauf R0",
        "visible": "gemischte Figuren-, Becken- und Laufanlage",
        "phases": ("FLUSH", "SETUP", "CHARGE", "RETURN", "ROUTE", "CHARGE", "HEAT", "CIRCULATE", "SETTLE", "FILTER", "FLUSH", "FLUSH", "SERVICE", "RETURN", "SETTLE", "CIRCULATE", "FILTER", "HEAT", "ROUTE", "DRAIN", "MAINTENANCE", "RETURN", "HANDOFF", "ROUTE"),
        "article": "Grundkreis A zuerst spülen, dann Beckenrand, Zulauf und Filteraufnahme prüfen. Eine gemessene Wassercharge einlassen, mit dem vorhandenen Rücklauf verknüpfen und über die sichtbaren Rinnen führen. Die Charge an W1 gelinde erwärmen, über Gefälle zirkulieren, stehen und klären lassen und durch den Filter zurückführen. Teilgänge an der Station einsetzen, Leitungen erneut spülen, unteren Lauf ablassen und reinigen. Den verbleibenden Bestand über R0 zurückgeben und die fertige Charge an die nächste Station übergeben.",
        "contradiction": "Figuren werden zu Bedienern oder Maßmarken herabgestuft; ein geschlossener hydraulischer Kreis ist nicht vollständig sichtbar.",
    },
    "B2": {
        "station": "Teilbecken B mit Zugängen Z1-Z3, Wärmestelle W2, Filter F2 und Auslass A2",
        "visible": "figurennahe Einzelstation mit mehreren Zugängen und kreuzförmigem Bauteil",
        "phases": ("SETUP", "MAINTENANCE", "CHARGE", "ROUTE", "HEAT", "CHARGE", "CHARGE", "SERVICE", "ROUTE", "FILTER", "SERVICE", "HEAT", "SETTLE", "MAINTENANCE", "HEAT", "DRAIN", "RETURN", "FILTER", "CHARGE", "ROUTE", "FILTER", "MAINTENANCE", "RETURN", "FLUSH", "DRAIN", "HANDOFF"),
        "article": "Teilbecken B und seine drei Zugänge prüfen, Filter F2 einsetzen und eine gemessene Charge zuführen. Die Charge abwechselnd über Z1-Z3 führen, an W2 temperieren, durch F2 klären und an der gebuchten Arbeitsstation einsetzen. Nach jedem Durchgang Rückstand und Filtrat trennen, unten über A2 ablassen, warm nachfüllen und den Rücklauf kontrollieren. Zum Ende Filter und Zugänge warten, den Leitungsweg spülen, Restwasser ablassen und den offenen Stationsposten übergeben.",
        "contradiction": "Die zahlreichen Figuren passen als Benutzer eines Bades besser als als bloße Bedien- oder Maßzeichen einer Anlage.",
    },
    "B3": {
        "station": "Hauptbecken C mit Vorwärmer W3, Leitungen L1-L4, Filter F3, Unterlauf U3 und Rücklauf R3",
        "visible": "lange Figuren-/Röhrenanlage mit zwei offenen Auslässen ohne lokale Figur",
        "phases": ("SETUP", "SETTLE", "DRAIN", "CHARGE", "CHARGE", "ROUTE", "CHARGE", "DRAIN", "SERVICE", "CIRCULATE", "SERVICE", "RETURN", "FLUSH", "FILTER", "DRAIN", "MAINTENANCE", "SETUP", "CHARGE", "CIRCULATE", "DRAIN", "SETTLE", "CHARGE", "DRAIN", "RETURN", "SETTLE", "DRAIN", "MAINTENANCE", "HEAT", "FLUSH", "FLUSH", "SERVICE", "FILTER", "RETURN", "SETTLE", "MAINTENANCE", "FILTER", "RETURN", "HANDOFF"),
        "article": "Hauptbecken C öffnen, Altbestand absetzen und über U3 ablassen. Neue gemessene Chargen über L1-L4 zuführen, am Vorwärmer W3 temperieren und an den gebuchten Stationen einsetzen. Jeden Stationsgang über Rinne und Gefälle zirkulieren, durch F3 klären, Rückstand halten und den Unterlauf getrennt ablassen. Zwischen den Gängen Leitungen spülen, Filter warten und Rückläufe R3 erneut zuführen. Nach mehreren solchen Schleifen die letzte Charge absetzen, Filter und Ausgänge reinigen und den verbleibenden Arbeitsstand an die Folgestation übergeben.",
        "contradiction": "Menschenfiguren und wiederholte Anwendungen bleiben für einen rein unpersönlichen Wasserwerksplan überschüssig.",
    },
    "B4": {
        "station": "Nachklärbecken D mit Warmzulauf W4, Filtertuch F4, Unterlauf U4 und Rückleitung R4",
        "visible": "warmer Nachgang an gemischtem Figur-/Stationsowner",
        "phases": ("SETUP", "FLUSH", "MAINTENANCE", "SERVICE", "RETURN", "FILTER", "MAINTENANCE", "FLUSH", "SETTLE", "RETURN", "CHARGE", "RETURN", "DRAIN", "MAINTENANCE", "SETTLE", "DRAIN", "ROUTE", "HANDOFF", "RETURN", "HANDOFF"),
        "article": "Nachklärbecken D prüfen und den Warmzulauf W4 spülen. Eine bezeichnete Teilcharge temperieren, am technischen Ziel einsetzen und über R4 in den laufenden Ansatz zurücknehmen. Den Bestand durch F4 führen, Filtertuch und Gefäßrand reinigen und einen zweiten Spülgang schließen. Danach gemessene Nachfüllung zuführen, stehen lassen, unten über U4 ablassen und erneut ansetzen. Letzten Rücklauf, Zieladresse und Übergabe als offenen Nachgang buchen.",
        "contradiction": "Auflage, Waschung oder Bad erklären die figurennahe Anwendung natürlicher; der technische Zielowner bleibt still.",
    },
    "B5": {
        "station": "Übergabebecken E mit Wärmeschale W5 und Leitung L5",
        "visible": "kurzer menschenarmer Wärme-/Übergabenachtrag",
        "phases": ("DRAIN", "HEAT", "SETTLE", "ROUTE", "HANDOFF"),
        "article": "Den Altbestand aus Übergabebecken E abziehen, eine Restcharge in W5 einmal erwärmen und für den gebuchten Zeitraum stehen lassen. Danach Ziel L5 setzen, den vorigen Arbeitsstand verknüpfen, die vorgeschriebene Menge nachtragen und die Charge an die nächste Station übergeben.",
        "contradiction": "Nur vier von elf Ereignissen tragen lizenzierte Prompts; Wärmedauer und Übergabeinhalt bleiben lokale Exemplare.",
    },
    "B6": {
        "station": "Kaltbecken F mit einfacher Filteröffnung F6 und Zielstation Z6",
        "visible": "offene menschenarme Gefäß-/Filterstation",
        "phases": ("SETUP", "FILTER"),
        "article": "Den vorhandenen kalten Arbeitsstand in Becken F aufnehmen, ohne Wärmeschritt durch die einfache Öffnung F6 führen, die vorgeschriebene Menge buchen und den laufenden Ansatz mit der Zielstation Z6 verknüpfen. Beide Felder bleiben offen; es gibt keinen beobachteten Abschluss.",
        "contradiction": "Sechs von neun Ereignissen sind opak; Filter, Kälte und Zielstation sind lokale Apparatewerte.",
    },
}

MEDICAL_BODY_MARKERS = ("bad", "bade", "haut", "wund", "auflage", "wasch", "körper", "stelle", "eintauch", "patient", "trink", "brust", "bauch", "schmerz")
MEDICAL_FLOW_MARKERS = ("filter", "tuch", "lauf", "rück", "zuführ", "ablass", "spül", "klär")


def encode_assumptions(counts: Counter[str]) -> str:
    return "|".join(f"{key}:{counts[key]}" for key in ASSUMPTION_WEIGHTS if counts[key]) or "NONE"


def cost(counts: Counter[str]) -> int:
    return sum(ASSUMPTION_WEIGHTS[key] * value for key, value in counts.items())


def select_phase(base_phase: str, parsed_events: list[dict[str, str]]) -> str:
    templates = {row["event_template"] for row in parsed_events}
    mnemonics = {row["selected_exact_mnemonic"] for row in parsed_events}
    if "TERMINAL_FLUSH" in templates:
        return "FLUSH"
    if "TERMINAL_DRAIN" in templates:
        return "DRAIN"
    if "ACTION_TEMPER" in templates:
        return "HEAT"
    if "ACTION_APPLY" in templates:
        return "SERVICE"
    if "KLAR?" in mnemonics:
        return "SETTLE"
    if "BEREIT?" in mnemonics and base_phase not in {"FILTER", "FLUSH", "DRAIN", "RETURN"}:
        return "HANDOFF"
    return base_phase


def local_event_argument(template: str, phase: str, record: str, field_id: str, station: str, event_index: int) -> str:
    if template == "PARAMETER_ASSIGN":
        return f"LOCAL_ARGUMENT[Mengenbuch={record}:{field_id}:M]"
    if template == "TARGET_ASSIGN":
        return f"LOCAL_ARGUMENT[Zieladresse={station}]"
    if template == "LINK_ACTIVE":
        return f"LOCAL_ARGUMENT[aktive Charge/Rücklauf des Feldes {field_id}]"
    if template == "STATE_GATE":
        return f"LOCAL_ARGUMENT[Arbeitsstand der Charge an {station}]"
    if template == "ACTION_APPLY":
        return f"LOCAL_ARGUMENT[aktive Charge an technischem Stationsziel {field_id}]"
    if template == "ACTION_TEMPER":
        return f"LOCAL_ARGUMENT[aktive Charge an der Wärmestelle von {station}]"
    if template == "TERMINAL_FLUSH":
        return f"LOCAL_ARGUMENT[Leitungsweg von {station}]"
    if template == "TERMINAL_DRAIN":
        return f"LOCAL_ARGUMENT[Unterlauf von {station}]"
    if template == "SELECT_PART":
        return f"LOCAL_ARGUMENT[Teilcharge aus {record}:{field_id}]"
    if template == "SELECT_PREVIOUS":
        return f"LOCAL_ARGUMENT[Vorcharge im recordlokalen Register {record}]"
    fillers = PHASES[phase]["fillers"]
    return f"LOCAL_EXEMPLAR[{fillers[event_index % len(fillers)]};keine Kartenbedeutung]"


def field_assumptions(row: dict[str, str], phase: str, iatro_text: str, first_field: bool, model: str) -> Counter[str]:
    counts: Counter[str] = Counter()
    lowered = iatro_text.lower()
    body_or_application_visible = any(marker in lowered for marker in MEDICAL_BODY_MARKERS)
    counts["EXEMPLAR_FILL"] = int(row["exemplar_only_event_count"])
    counts["LOCAL_PROCESS"] = 1
    counts["MEDIUM"] = 1
    if "TARGET_ASSIGN" in row["ordered_event_template_sequence"] or row["field_position_in_statement"] == "FIRST":
        counts["STATION_OR_TARGET"] = 1
    if model == "TECHNICAL_WATERWORK":
        if phase in {"FILTER", "FLUSH", "DRAIN", "RETURN", "CIRCULATE"}:
            counts["FILTER_OR_RETURN_MECHANISM"] = 1
        if first_field:
            counts["DOMAIN_PURPOSE"] = 1
        # A pure plant may not make the visible/locally expanded human role
        # disappear for free: every such B1--B4 cell pays for reinterpreting
        # the person as attendant, scale figure or station marker.
        if body_or_application_visible and row["record_unit_id"] in {"B1", "B2", "B3", "B4"}:
            counts["HUMAN_ROLE_OR_BODY"] = 1
    elif model == "IATROMEDICAL":
        if any(marker in lowered for marker in MEDICAL_FLOW_MARKERS):
            counts["FILTER_OR_RETURN_MECHANISM"] = 1
        if first_field:
            counts["DOMAIN_PURPOSE"] = 1
        if body_or_application_visible:
            counts["HUMAN_ROLE_OR_BODY"] = 1
    else:
        raise ValueError(model)
    return counts


def main() -> None:
    selected_v64 = SOURCE_V64_SELECTION.read_text(encoding="utf-8")
    require("V64 fügt **keine** neue Karte" in selected_v64, "V64 no-new-meaning contract changed")
    source_records = read_tsv(SOURCE_RECORDS)
    all_events = read_tsv(SOURCE_EVENTS)
    all_statements = read_tsv(SOURCE_STATEMENTS)
    all_machine = read_tsv(SOURCE_MACHINE)
    all_parse_events = read_tsv(SOURCE_PARSE_EVENTS)
    all_parse_fields = read_tsv(SOURCE_PARSE_FIELDS)
    all_parse_statements = read_tsv(SOURCE_PARSE_STATEMENTS)
    require((len(source_records), len(all_events), len(all_statements), len(all_machine), len(all_parse_events), len(all_parse_fields), len(all_parse_statements)) == (6, 381, 116, 116, 381, 135, 116), "selected source counts changed")
    require(Counter(row["parse_status"] for row in all_parse_fields) == Counter({"UNIQUE": 14, "AMBIGUOUS": 56, "UNPARSED": 65}), "V63 overall field status changed")

    events = [row for row in all_events if biological(row)]
    statements = [row for row in all_statements if biological(row)]
    machine = [row for row in all_machine if biological(row)]
    parse_events = [row for row in all_parse_events if biological(row)]
    parse_fields = [row for row in all_parse_fields if biological(row)]
    parse_statements = [row for row in all_parse_statements if biological(row)]
    require((len(events), len(statements), len(machine), len(parse_events), len(parse_fields), len(parse_statements)) == (281, 97, 97, 281, 115, 97), "Biological scope changed")
    require(Counter(row["parse_status"] for row in parse_fields) == Counter({"UNIQUE": 14, "AMBIGUOUS": 41, "UNPARSED": 60}), "Bio field status changed")
    require(Counter(row["parse_status"] for row in parse_statements) == Counter({"UNIQUE": 12, "AMBIGUOUS": 35, "UNPARSED": 50}), "Bio statement status changed")

    record_source_by_id = {row["record_id"]: row for row in source_records}
    source_event_by_serial = {row["event_serial"]: row for row in events}
    parse_event_by_serial = {row["event_serial"]: row for row in parse_events}
    source_statement_by_id = {row["statement_id"]: row for row in statements}
    machine_by_id = {row["statement_id"]: row for row in machine}
    parse_statement_by_id = {row["statement_id"]: row for row in parse_statements}
    parse_field_by_id = {row["field_id"]: row for row in parse_fields}

    fields_by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    events_by_field: dict[str, list[dict[str, str]]] = defaultdict(list)
    statements_by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for field in parse_fields:
        fields_by_record[field["record_unit_id"]].append(field)
    for event in events:
        events_by_field[event["field_id"]].append(event)
    for statement in statements:
        statements_by_record[statement["record_unit_id"]].append(statement)
    require(set(RECORD_CONFIG) == set(fields_by_record) == set(record_source_by_id), "record configuration mismatch")
    for record, config in RECORD_CONFIG.items():
        require(len(config["phases"]) == len(fields_by_record[record]), f"phase schedule mismatch: {record}")

    # The local phase is fixed by record/field order, with only already selected
    # exact action/state triggers allowed to override it.
    phase_by_field: dict[str, str] = {}
    local_state_by_field: dict[str, tuple[str, str]] = {}
    first_field_by_record: dict[str, str] = {}
    for record, record_fields in fields_by_record.items():
        first_field_by_record[record] = record_fields[0]["field_id"]
        for ordinal, field in enumerate(record_fields, 1):
            parsed = [parse_event_by_serial[serial] for serial in field["event_serials"].split("|")]
            phase = select_phase(RECORD_CONFIG[record]["phases"][ordinal - 1], parsed)
            phase_by_field[field["field_id"]] = phase
            local_state_by_field[field["field_id"]] = (f"{record}:Q{ordinal - 1:03d}", f"{record}:Q{ordinal:03d}:{phase}")

    event_rows: list[dict[str, str]] = []
    for event in events:
        parsed = parse_event_by_serial[event["event_serial"]]
        field = parse_field_by_id[event["field_id"]]
        record = event["record_unit_id"]
        phase = phase_by_field[event["field_id"]]
        mnemonic = parsed["selected_exact_mnemonic"]
        formal = parsed["strict_formal_prompt"]
        exact_clause = FIXED_VALUE_CLAUSE.get(mnemonic, "NONE")
        formal_clause = f"{formal}=FORMAL_OPAQUE_SLOT_OPERATION" if formal != "NONE" else "NONE"
        index = events_by_field[event["field_id"]].index(event)
        local_argument = local_event_argument(parsed["event_template"], phase, record, event["field_id"], RECORD_CONFIG[record]["station"], index)
        clauses = [clause for clause in (exact_clause, formal_clause, local_argument) if clause != "NONE"]
        if mnemonic != "UNKNOWN" and formal != "NONE":
            source_class = "V60_EXACT+V63_FORMAL_SEPARATE+LOCAL_APPARATUS_ARGUMENT"
        elif mnemonic != "UNKNOWN":
            source_class = "V60_EXACT+LOCAL_APPARATUS_ARGUMENT"
        elif formal != "NONE":
            source_class = "V63_FORMAL_NO_SEMANTIC_WORD+LOCAL_APPARATUS_ARGUMENT"
        else:
            source_class = "V54_VISIBLE_APPARATUS_OR_V65_LOCAL_EXEMPLAR;NOT_CARD_MEANING"
        event_rows.append(
            {
                "event_serial": event["event_serial"],
                "page": event["page"],
                "locus": event["locus"],
                "record_unit_id": record,
                "field_id": event["field_id"],
                "statement_id": field["statement_id"],
                "joint_tuple_id_opaque": event["joint_tuple_id"],
                "surface_display_only": event["surface"],
                "formal_formula_opaque": event["formal_formula_opaque"],
                "terminal_status": event["terminal_status"],
                "fixed_exact_mnemonic": mnemonic,
                "strict_formal_prompt": formal,
                "event_template": parsed["event_template"],
                "event_parse_status": parsed["event_parse_status"],
                "local_phase": phase,
                "fixed_value_clause": exact_clause,
                "formal_clause_no_semantic_inheritance": formal_clause,
                "local_apparatus_argument": local_argument,
                "complete_layered_technical_reading": " ; ".join(clauses),
                "local_argument_source_class": source_class,
                "local_pre_state": local_state_by_field[event["field_id"]][0],
                "local_post_state": local_state_by_field[event["field_id"]][1],
                "v62_statement_pre_state": machine_by_id[field["statement_id"]]["pre_state"],
                "v62_statement_post_state": machine_by_id[field["statement_id"]]["post_state"],
                "iatromedical_comparator_event": event["LOCAL_IATROMEDICAL_EXPANSION"],
                "opaque_roundtrip_atom": parsed["opaque_roundtrip_atom"],
                "layer_contract": "EXACT_TUPLE_ATOMIC;V60_VALUE_FIXED;V63_STATUS_FIXED;LOCAL_NOUN_NEVER_CARD_GLOSS",
                "source_lineage": "V54_SELECTED_RECORD+V60_EVENT+V61/V62+V63_PARSE>V65_R3_WATERWORK_EVENT",
            }
        )

    field_rows: list[dict[str, str]] = []
    field_costs: dict[tuple[str, str], Counter[str]] = {}
    for field in parse_fields:
        record = field["record_unit_id"]
        phase = phase_by_field[field["field_id"]]
        phase_sentence = PHASES[phase]["sentence"].format(station=RECORD_CONFIG[record]["station"])
        licensed = [template for template in field["ordered_event_template_sequence"].split(" > ") if template != "EXEMPLAR_ONLY"]
        license_clause = "; ".join(TEMPLATE_CLAUSE[template] for template in licensed) if licensed else "keine lizenzierte Slotoperation"
        terminal = any(source_event_by_serial[serial]["terminal_status"] == "TERMINAL" for serial in field["event_serials"].split("|"))
        exact_terminal = any(parse_event_by_serial[serial]["event_template"] in {"TERMINAL_FLUSH", "TERMINAL_DRAIN"} for serial in field["event_serials"].split("|"))
        commit = "EXACT_TERMINAL_ACTION_COMMIT" if exact_terminal else "OPAQUE_FIELD_COMMIT_ONLY" if terminal else "OPEN_CARRY"
        iatro_text = " ; ".join(source_event_by_serial[serial]["LOCAL_IATROMEDICAL_EXPANSION"] for serial in field["event_serials"].split("|"))
        first_field = field["field_id"] == first_field_by_record[record]
        technical_assumptions = field_assumptions(field, phase, iatro_text, first_field, "TECHNICAL_WATERWORK")
        medical_assumptions = field_assumptions(field, phase, iatro_text, first_field, "IATROMEDICAL")
        field_costs[(field["field_id"], "TECHNICAL_WATERWORK")] = technical_assumptions
        field_costs[(field["field_id"], "IATROMEDICAL")] = medical_assumptions
        technical_cost = cost(technical_assumptions)
        medical_cost = cost(medical_assumptions)
        winner = "TECHNICAL" if technical_cost < medical_cost else "IATROMEDICAL" if medical_cost < technical_cost else "TIE"
        contradiction = (
            "Das ganze Feld ist UNPARSED; die konkrete Anlagenhandlung kommt nur aus dem lokalen Phasenplan."
            if field["parse_status"] == "UNPARSED"
            else "Die lizenzierte Slotfolge bestimmt weder Becken, Wasser, Leitung noch technischen Zweck."
        )
        if terminal and not exact_terminal:
            contradiction += " CLOSE trägt nur Commit und lizenziert weder Spülen noch Ablassen."
        if "ACTION_APPLY > TARGET_ASSIGN" in field["ordered_event_template_sequence"]:
            contradiction += " ACTION steht vor TARGET; die Zieladresse muss als Nachtrag gelesen werden."
        complete = f"{phase_sentence}. Lizenzierte Slotfolge: {license_clause}. " + ("Feldbuchung schließen." if terminal else "Arbeitsstand offen weitertragen.")
        field_rows.append(
            {
                "field_id": field["field_id"],
                "record_unit_id": record,
                "page": field["page"],
                "locus": field["locus"],
                "statement_id": field["statement_id"],
                "field_position_in_statement": field["field_position_in_statement"],
                "event_count": field["event_count"],
                "event_serials": field["event_serials"],
                "v63_primary_template": field["primary_template"],
                "v63_ordered_template_sequence": field["ordered_event_template_sequence"],
                "v63_parse_status_fixed": field["parse_status"],
                "recognized_event_count": field["recognized_event_count"],
                "exemplar_only_event_count": field["exemplar_only_event_count"],
                "local_phase": phase,
                "local_pre_state": local_state_by_field[field["field_id"]][0],
                "complete_technical_field_reading": complete,
                "local_post_state": local_state_by_field[field["field_id"]][1],
                "commit_class": commit,
                "v62_pre_state_statement_envelope": field["register_pre_state_statement_envelope"],
                "v62_post_state_statement_envelope": field["register_post_state_statement_envelope"],
                "iatromedical_field_comparator": iatro_text,
                "technical_assumptions": encode_assumptions(technical_assumptions),
                "technical_weighted_cost": str(technical_cost),
                "iatromedical_assumptions": encode_assumptions(medical_assumptions),
                "iatromedical_weighted_cost": str(medical_cost),
                "field_coherence_winner": winner,
                "strongest_technical_contradiction": contradiction,
                "opaque_roundtrip_trace": field["opaque_roundtrip_trace"],
                "roundtrip_status": field["roundtrip_status"],
                "layer_contract": "V62_ENVELOPE_UNCHANGED;V63_STATUS_UNCHANGED;PHASE_AND_NOUNS_LOCAL_ONLY",
                "source_lineage": "V60_SELECTED_EVENTS>V63_SELECTED_FIELD_PARSE>V65_R3_WATERWORK_FIELD",
            }
        )

    fields_out_by_id = {row["field_id"]: row for row in field_rows}
    statement_rows: list[dict[str, str]] = []
    for statement in statements:
        statement_id = statement["statement_id"]
        machine_row = machine_by_id[statement_id]
        parsed = parse_statement_by_id[statement_id]
        constituent = statement["constituent_fields"].split("|")
        unit_fields = [fields_out_by_id[field_id] for field_id in constituent]
        technical_counts: Counter[str] = Counter()
        medical_counts: Counter[str] = Counter()
        for field_id in constituent:
            technical_counts.update(field_costs[(field_id, "TECHNICAL_WATERWORK")])
            medical_counts.update(field_costs[(field_id, "IATROMEDICAL")])
        technical_cost = cost(technical_counts)
        medical_cost = cost(medical_counts)
        winner = "TECHNICAL" if technical_cost < medical_cost else "IATROMEDICAL" if medical_cost < technical_cost else "TIE"
        statement_rows.append(
            {
                "statement_id": statement_id,
                "record_unit_id": statement["record_unit_id"],
                "page": statement["page"],
                "constituent_fields": statement["constituent_fields"],
                "event_count": statement["event_count"],
                "event_serials": statement["event_serials"],
                "closure_sequence": statement["closure_sequence"],
                "v63_parse_status_fixed": parsed["parse_status"],
                "v63_ordered_template_sequence": parsed["ordered_event_template_sequence"],
                "local_phase_path": " > ".join(field["local_phase"] for field in unit_fields),
                "pre_state": machine_row["pre_state"],
                "owner_operation": machine_row["owner_operation"],
                "active_item_preparation_operation": machine_row["active_item_preparation_operation"],
                "target_station_operation": machine_row["target_station_operation"],
                "previous_item_operation": machine_row["previous_item_operation"],
                "post_state": machine_row["post_state"],
                "complete_technical_waterwork_reading": " || ".join(field["complete_technical_field_reading"] for field in unit_fields),
                "complete_iatromedical_comparator": statement["concrete_workshop_reading"],
                "technical_assumptions": encode_assumptions(technical_counts),
                "technical_weighted_cost": str(technical_cost),
                "iatromedical_assumptions": encode_assumptions(medical_counts),
                "iatromedical_weighted_cost": str(medical_cost),
                "statement_coherence_winner": winner,
                "comparison_reason": "Lower symmetric local-assumption cost wins; equal cost remains TIE. This is process-description economy, not semantic evidence.",
                "strongest_technical_contradiction": "Local apparatus nouns and phase operations are not card meanings; visible human figures remain unexplained by a purely impersonal plant.",
                "opaque_roundtrip_trace": parsed["opaque_roundtrip_trace"],
                "roundtrip_status": parsed["roundtrip_status"],
                "comparison_contract": "SAME_SOURCE_STATEMENT+V60_VALUES+V62_STATE+V63_STATUS;ONLY_LOCAL_DOMAIN_EXPANSION_DIFFERS",
                "source_lineage": "V61_STATEMENT>V62_MACHINE>V63_PARSE>V65_R3_DUAL_STATEMENT",
            }
        )

    statements_out_by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    fields_out_by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    events_out_by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in statement_rows:
        statements_out_by_record[row["record_unit_id"]].append(row)
    for row in field_rows:
        fields_out_by_record[row["record_unit_id"]].append(row)
    for row in event_rows:
        events_out_by_record[row["record_unit_id"]].append(row)

    record_rows: list[dict[str, str]] = []
    graph_rows: list[dict[str, str]] = []
    cost_rows: list[dict[str, str]] = []
    for source_record in source_records:
        record = source_record["record_id"]
        config = RECORD_CONFIG[record]
        record_fields = fields_out_by_record[record]
        record_statements = statements_out_by_record[record]
        record_events = events_out_by_record[record]
        technical_total = sum(int(field["technical_weighted_cost"]) for field in record_fields)
        medical_total = sum(int(field["iatromedical_weighted_cost"]) for field in record_fields)
        winner = "TECHNICAL" if technical_total < medical_total else "IATROMEDICAL" if medical_total < technical_total else "TIE"
        field_status = Counter(field["v63_parse_status_fixed"] for field in record_fields)
        statement_status = Counter(statement["v63_parse_status_fixed"] for statement in record_statements)
        statement_winners = Counter(statement["statement_coherence_winner"] for statement in record_statements)
        commit_fields = [field["field_id"] for field in record_fields if field["commit_class"] != "OPEN_CARRY"]
        record_rows.append(
            {
                "record_unit_id": record,
                "folio": source_record["folio"],
                "visible_owner_argument": config["visible"],
                "local_apparatus_inventory": config["station"],
                "field_count": str(len(record_fields)),
                "statement_count": str(len(record_statements)),
                "event_count": str(len(record_events)),
                "recognized_event_count": str(sum(event["event_template"] != "EXEMPLAR_ONLY" for event in record_events)),
                "field_status_summary": ";".join(f"{key}={field_status[key]}" for key in ("UNIQUE", "AMBIGUOUS", "UNPARSED")),
                "statement_status_summary": ";".join(f"{key}={statement_status[key]}" for key in ("UNIQUE", "AMBIGUOUS", "UNPARSED")),
                "complete_technical_waterwork_article": config["article"],
                "complete_iatromedical_article": source_record["complete_working_translation_German"],
                "observed_commit_fields": "|".join(commit_fields) if commit_fields else "NONE",
                "statement_winner_summary": ";".join(f"{key}={statement_winners[key]}" for key in ("TECHNICAL", "IATROMEDICAL", "TIE")),
                "technical_weighted_assumption_cost": str(technical_total),
                "iatromedical_weighted_assumption_cost": str(medical_total),
                "record_coherence_winner_by_fixed_cost": winner,
                "strongest_medical_rival": source_record["selected_working_role"],
                "strongest_technical_contradiction": config["contradiction"],
                "domain_judgment": "Pure waterwork explains apparatus workflow; selected therapeutic-balneology hybrid additionally explains figures and therefore remains the broader comparator.",
                "layer_contract": "APPARATUS_AND_HUMAN_ROLES_LOCAL_ONLY;NO_NEW_CARD_MEANING",
                "source_lineage": "V54_SELECTED_RECORD+V60-V64_SELECTED_CONTRACT>V65_R3_RECORD_EDITION",
            }
        )
        graph_rows.append(
            {
                "record_unit_id": record,
                "field_path": "|".join(field["field_id"] for field in record_fields),
                "phase_path": " > ".join(f"{field['field_id']}:{field['local_phase']}" for field in record_fields),
                "local_state_path": " > ".join(field["local_post_state"] for field in record_fields),
                "v62_statement_transition_path": " > ".join(f"{statement['statement_id']}[{statement['owner_operation']}/{statement['active_item_preparation_operation']}/{statement['target_station_operation']}/{statement['previous_item_operation']}]" for statement in record_statements),
                "commit_fields": "|".join(commit_fields) if commit_fields else "NONE",
                "initial_v62_state": record_statements[0]["pre_state"],
                "final_v62_state": record_statements[-1]["post_state"],
                "deterministic_execution_rule": "FOLLOW_FIELDS;SELECT_FROZEN_LOCAL_PHASE;OVERRIDE_ONLY_BY_LICENSED_TERMINAL/TEMPER/APPLY/STATE;APPLY_V62_ENVELOPE;COMMIT_ONLY_OBSERVED_TERMINAL",
                "backward_trace": "FIELD_ID+PHASE+OPAQUE_EVENT_IDS reconstruct complete source order; local phase does not reconstruct semantics",
                "graph_status": "COMPLETE_LOCAL_PROCESS_GRAPH_NOT_DECIPHERMENT",
                "source_lineage": "V61_ORDER+V62_STATE+V63_TEMPLATE>V65_R3_PROCESS_STATE_GRAPH",
            }
        )
        for model, total in (("TECHNICAL_WATERWORK", technical_total), ("IATROMEDICAL", medical_total)):
            combined: Counter[str] = Counter()
            for field in record_fields:
                combined.update(field_costs[(field["field_id"], model)])
            cost_rows.append(
                {
                    "record_unit_id": record,
                    "model": model,
                    "weight_contract": "EXEMPLAR=1;LOCAL_PROCESS=1;MEDIUM=1;STATION/TARGET=1;FILTER/RETURN=1;DOMAIN_PURPOSE=2;HUMAN_ROLE/BODY=2",
                    "assumption_counts": encode_assumptions(combined),
                    "weighted_cost": str(total),
                    "cost_scope": "SUM_OF_115_FIELD_LOCAL_FILLERS;V60_EXACT+V63_FORMAL+V62_REGISTERS_COST_ZERO",
                    "interpretation": "SYMMETRIC_DESCRIPTION_LENGTH_PROXY_NOT_PROBABILITY",
                    "source_lineage": "V65_R3_FIXED_PREOUTPUT_COST_RULE",
                }
            )

    require((len(event_rows), len(field_rows), len(statement_rows), len(record_rows), len(graph_rows), len(cost_rows)) == (281, 115, 97, 6, 6, 12), "output counts changed")
    write_tsv(OUT_EVENTS, event_rows)
    write_tsv(OUT_FIELDS, field_rows)
    write_tsv(OUT_STATEMENTS, statement_rows)
    write_tsv(OUT_RECORDS, record_rows)
    write_tsv(OUT_GRAPHS, graph_rows)
    write_tsv(OUT_COSTS, cost_rows)
    print("PASS V65 R3 build")
    print("records=6 statements=97 fields=115 events=281 graphs=6 costs=12")
    print("Bio field status=UNIQUE:14;AMBIGUOUS:41;UNPARSED:60")
    print("Bio statement status=UNIQUE:12;AMBIGUOUS:35;UNPARSED:50")
    print("event coverage=90 licensed;191 EXEMPLAR_ONLY")
    print("statement winners=" + ";".join(f"{key}:{value}" for key, value in sorted(Counter(row['statement_coherence_winner'] for row in statement_rows).items())))
    print("cost totals=technical:" + str(sum(int(row['technical_weighted_assumption_cost']) for row in record_rows)) + ";iatromedical:" + str(sum(int(row['iatromedical_weighted_assumption_cost']) for row in record_rows)))


if __name__ == "__main__":
    main()
