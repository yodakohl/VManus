#!/usr/bin/env python3
"""Build V74 R2, the complete Biological local-station third edition.

The German occurrence readings reuse the frozen V69 iatromedical exemplar
segments, but V71 local owners and V72 visible-gap resets override every old
page-wide process implication.  No surface spelling or tuple decomposition is
used to select content.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
V69 = ROOT / "experiments/yolo/sidequest_theory_candidates_v69"
V70 = ROOT / "experiments/yolo/sidequest_theory_candidates_v70"
V71 = ROOT / "experiments/yolo/sidequest_theory_candidates_v71"
V72 = ROOT / "experiments/yolo/sidequest_theory_candidates_v72"
OUT = ROOT / "experiments/yolo/sidequest_theory_candidates_v74"

EVENTS_IN = V69 / "V69_R4_FINAL_381_PROSE_EVENT_INTERLINEAR.tsv"
FIELDS_IN = V69 / "V69_R4_FINAL_135_FIELD_EDITION.tsv"
CARDS_IN = V69 / "V69_R4_FINAL_173_CARD_DICTIONARY.tsv"
V70_IMAGES = V70 / "V70_SELECTED_TEN_PAGE_IMAGE_REVISION.tsv"
V71_OWNERS = V71 / "V71_SELECTED_OWNER_LEDGER.tsv"
V72_STATEMENTS = V72 / "V72_SELECTED_116_STATEMENTS.tsv"

EVENTS_OUT = OUT / "V74_R2_281_BIO_EVENTS.tsv"
FIELDS_OUT = OUT / "V74_R2_115_BIO_FIELDS.tsv"
STATEMENTS_OUT = OUT / "V74_R2_97_BIO_STATEMENTS.tsv"
RECORDS_OUT = OUT / "V74_R2_SIX_CONTINUOUS_RECORDS.tsv"
NOUNS_OUT = OUT / "V74_R2_UNSUPPORTED_NOUNS.tsv"
REPORT_OUT = OUT / "V74_R2_BIOLOGICAL_STATION_ATLAS_REPORT.md"


R2_BACKGROUND = [
    "Du kennst zeitgenössische Herbarien, Materia medica, Rezeptbücher, Abkürzungen und kompilierte Sammelhandschriften.",
    "Du vergleichst Namen, Beschreibungen, Qualitäten, Habitate, Zubereitungen, Anwendungen und Rezeptfortsetzungen.",
    "Du unterscheidest überlieferte Textpraxis von modernen Tabellen-, Datenbank- oder Übersetzungsannahmen.",
    "Du darfst historische Quellen recherchieren, aber niemals Voynich-Formen über Klang oder Buchstabenähnlichkeit zuordnen.",
    "Du lieferst die historisch plausibelste Quelltextstruktur samt Gegenbelegen und eng begrenzter Pseudoübersetzung.",
]


OWNER_LABELS = {
    "B1_SHARED_TWO_ROW_POOL": "gemeinsames zweireihiges Figuren-/Beckenfeld",
    "B2_UPPER_PAIRED_BASINS_AND_CYLINDER": "obere Paarbecken-/Zylinderstation",
    "B2_MIDDLE_LEFT_DEVICE_AND_INLINE_NODE": "mittlere linke Geräte-/Inline-Knotenstation",
    "B2_MIDDLE_RIGHT_AMBIGUOUS_STATION": "ungelöste mittlere rechte Linie-/Liegepodeststation",
    "B2_LOWER_GREEN_MULTI_FIGURE_POOL": "unteres grünes Mehrfigurenfeld",
    "B2_LOWER_POOL_EDGE_STATIONS": "lokale Randstationen des unteren Feldes",
    "B3_UPPER_MARGIN_OPEN_FAN_STATION": "obere offene Fächer-Randstation",
    "B3_MIDDLE_MARGIN_ROUND_VESSEL_STATION": "mittlere runde Gefäß-Randstation",
    "B3_LOWER_MARGIN_BASKET_VESSEL_STATION": "untere korbartige Gefäß-Randstation",
    "B3_MARGIN_TO_MAIN_GAP_UNRESOLVED": "ungelöster Zwischenposten zwischen Randstapel und Hauptpaar",
    "B3_MAIN_ARCH_LINKED_PAIR": "Hauptpaar am sichtbaren ungerichteten Bogen",
    "B4_MAIN_ARCH_LINKED_PAIR": "Hauptpaar am sichtbaren ungerichteten Bogen",
    "B4_MAIN_LEFT_OPEN_FRINGE_STATION": "linke offene Fransen-/Unterlaufstation",
    "B4_MAIN_RIGHT_S_RUN_MULTIPORT_STATION": "rechte S-Lauf-/Mehrarmknotenstation",
    "B5_LEFT_OPEN_FRINGE_STATION": "linker offener Fransen-Endposten",
    "B6_RIGHT_S_RUN_MULTIPORT_STATION": "rechter S-Lauf-/Mehrarm-Endposten",
}


RECORD_SYNOPSIS = {
    "B1": "Ein gemeinsames Badefeld erhält ein lokales Regimen aus Bereitstellen, Bemessen, Temperieren, Baden/Waschen, Spülen, Absetzen und Abschluss. Die zwei Figurenreihen sind keine zeitliche Vorher-/Nachher-Folge.",
    "B2": "Ein Stationskatalog führt nacheinander obere Paarbecken/Zylinder, eine mittlere Gerätefigur, einen ungelösten Linie-/Liegeposten, das untere Mehrfigurenfeld und dessen Randplätze. Jeder Wechsel setzt Stoff und Richtung zurück.",
    "B3": "Drei getrennte Randstationen tragen kurze Bade-/Waschartikel; danach folgt ein eigentümerloser Zwischenbereich und erst nach erneutem Reset das tatsächlich durch einen Bogen gekoppelte Hauptpaar.",
    "B4": "Das Hauptbogenpaar trägt lokale Wasch-/Auflagehandlungen; anschließend folgen getrennt die linke offene Fransenstation und die rechte S-Lauf-/Mehrarmstation. Zwischen links und rechts besteht keine Kante.",
    "B5": "Der linke offene Endposten trägt einen kurzen eigenständigen Wärme-, Maß- und Zielartikel; er reicht nicht zum rechten Apparat.",
    "B6": "Der rechte S-Lauf-/Mehrarm-Endposten trägt einen eigenen Einrichtungs-, Maß-, Filter- und Zielartikel; die offenen Arme liefern keine Bewegungsrichtung.",
}


RECORD_STRUCTURE = {
    "B1": "communal balneum regimen -> local measure/temperature -> immersion/wash -> rinse/settle -> local close",
    "B2": "upper paired station -> RESET -> middle device -> RESET unresolved station -> RESET lower pool -> RESET edge stations",
    "B3": "upper/middle/lower margin station articles -> RESET unresolved prose gap -> RESET visibly arch-linked pair",
    "B4": "arch-linked pair regimen -> RESET left open-fringe station -> RESET right S-run/multiport station",
    "B5": "left open-fringe terminal article only",
    "B6": "right S-run/multiport terminal article only",
}


# Canonical audit term, regex, support class.  These are source-exemplar nouns,
# never proposed Voynich lexical values.
NOUN_PATTERNS = [
    ("Waschflotte", r"\bWaschflotte\w*\b", "UNPICTURED_SUBSTANCE_OR_PREPARATION"),
    ("Badeflüssigkeit", r"\bBadeflüssigkeit\w*\b", "UNPICTURED_SUBSTANCE_OR_PREPARATION"),
    ("Flüssigkeit", r"\bFlüssigkeit\w*\b", "UNPICTURED_SUBSTANCE_OR_PREPARATION"),
    ("Wasser", r"\bWasser\w*\b", "UNPICTURED_SUBSTANCE_OR_PREPARATION"),
    ("Mischung", r"\bMischung\w*\b", "UNPICTURED_SUBSTANCE_OR_PREPARATION"),
    ("Charge", r"\bCharge\w*\b", "UNPICTURED_SUBSTANCE_OR_PREPARATION"),
    ("Ansatz", r"\bAnsatz\w*\b", "UNPICTURED_SUBSTANCE_OR_PREPARATION"),
    ("Posten", r"\bPosten\w*\b", "UNPICTURED_SUBSTANCE_OR_PREPARATION"),
    ("Portion", r"\bPortion\w*\b", "UNPICTURED_SUBSTANCE_OR_PREPARATION"),
    ("Anteil", r"\bAnteil\w*\b", "UNPICTURED_SUBSTANCE_OR_PREPARATION"),
    ("Bade-/Waschzusatz", r"Bade- oder Waschzusatz|Bade- oder Waschposten", "UNPICTURED_SUBSTANCE_OR_PREPARATION"),
    ("Rückstand", r"\bRückstand\w*\b", "UNPICTURED_SUBSTANCE_OR_PREPARATION"),
    ("Tuch", r"\bTuch\w*\b", "UNPICTURED_IMPLEMENT"),
    ("Gefäß", r"\bGefäß\w*\b|Auffanggefäß", "LOCAL_VISIBLE_FORM_FUNCTION_UNCERTAIN"),
    ("Becken", r"\bBecken\w*\b|Teilbad", "LOCAL_VISIBLE_FORM_FUNCTION_UNCERTAIN"),
    ("Lauf", r"\bLauf\w*\b|Läufe", "LOCAL_VISIBLE_FORM_FUNCTION_UNCERTAIN"),
    ("Öffnung", r"\bÖffnung\w*\b", "LOCAL_VISIBLE_FORM_FUNCTION_UNCERTAIN"),
    ("Station", r"\bStation\w*\b|Stelle", "LOCAL_VISIBLE_FORM_FUNCTION_UNCERTAIN"),
    ("Badende", r"\bBadende\w*\b", "VISIBLE_FIGURE_THERAPEUTIC_STATUS_UNCERTAIN"),
    ("Körperbereich", r"Körper- oder Beckenbereich|Körperbereich|benetzte Körperbereich", "VISIBLE_FIGURE_THERAPEUTIC_STATUS_UNCERTAIN"),
    ("Haut-/Wundstelle", r"Haut- oder Wundstelle|Hautstelle|Wundstelle|äußere Stelle", "VISIBLE_FIGURE_THERAPEUTIC_STATUS_UNCERTAIN"),
    ("Waschung/Bad", r"Waschung|wasche|Waschen|bade|Bad", "VISIBLE_FIGURE_THERAPEUTIC_STATUS_UNCERTAIN"),
    ("Auflage", r"Auflage", "VISIBLE_FIGURE_THERAPEUTIC_STATUS_UNCERTAIN"),
    ("Maß/Menge", r"Maß|Menge|abgemessen|gleichen Teilen|gleiche Anteile", "UNPICTURED_PARAMETER_OR_STATE"),
    ("Dauer", r"Dauer|Zeitabschnitt", "UNPICTURED_PARAMETER_OR_STATE"),
    ("Wärme/Temperatur", r"warm|erwärm|temperier|abkühl|ohne Kochen|sanfter Wärme", "UNPICTURED_PARAMETER_OR_STATE"),
    ("Klarzustand", r"klar|Klarheit", "UNPICTURED_PARAMETER_OR_STATE"),
    ("Bereitschaft", r"Bereitschaft|bereit", "UNPICTURED_PARAMETER_OR_STATE"),
    ("Spülen", r"spül", "UNMARKED_OPERATION_OR_DIRECTION"),
    ("Ablassen/Ablauf", r"ablass|ablauf|Ablauf|abführen|ziehe .* ab", "UNMARKED_OPERATION_OR_DIRECTION"),
    ("Strom/Flussrichtung", r"Strom|zurücklauf|einlauf|gieße .* ein|zum unteren|zum oberen|verbundenen Läufe", "UNMARKED_OPERATION_OR_DIRECTION"),
    ("erste/zweite Richtung", r"erste Öffnung|zweite Öffnung|oberen Lauf|unteren Lauf", "UNMARKED_OPERATION_OR_DIRECTION"),
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def ordered_unique(items: list[str]) -> list[str]:
    return list(dict.fromkeys(items))


def extract_exemplar(source: str) -> str:
    match = re.search(r"\[EXEMPLAR:[^:]+:(.*?)\]", source)
    if not match:
        raise ValueError(f"missing exemplar payload: {source}")
    text = re.sub(r"\s+", " ", match.group(1)).strip()
    if text:
        text = text[0].upper() + text[1:]
    if not text.endswith((".", "!", "?")):
        text += "."
    return text


def exemplar_role(text: str) -> str:
    t = text.casefold()
    if any(k in t for k in ("ziel", "station", "stelle", "bereich", "öffnung", "becken", "lauf")):
        return "LOCAL_TARGET_OR_STATION"
    if any(k in t for k in ("maß", "menge", "anteil", "portion", "teilen")):
        return "LOCAL_PARAMETER"
    if any(k in t for k in ("warm", "temper", "abkühl", "klar", "bereit", "dauer", "zeitabschnitt")):
        return "LOCAL_CONDITION_OR_STATE"
    if any(k in t for k in ("flüssigkeit", "wasser", "mischung", "zusatz", "tuch", "gefäß", "charge", "ansatz")):
        return "LOCAL_SUBSTANCE_OR_OBJECT"
    if any(k in t for k in ("vorigen", "daraus", "aktiven posten", "arbeitsgang")):
        return "RECORD_LOCAL_LINK"
    return "LOCAL_ACTION_OR_SOURCE_ARGUMENT"


def literal_layer(event: dict[str, str], owner: str, role: str) -> str:
    pieces = [f"[OWNER:{owner}]", f"[OPAQUE_CARD:{event['joint_tuple_id']}]"]
    if event["selected_exact_mnemonic"] != "UNKNOWN":
        pieces.append(f"[CARD:{event['selected_exact_mnemonic']}]")
    if event["strict_formal_prompt"] != "NONE":
        pieces.append(f"[FORMAL:{event['strict_formal_prompt']}]")
    pieces.append(f"[CONTEXT_EXEMPLAR:{role}]")
    if event["terminal_status"] == "TERMINAL":
        pieces.append("[CLOSE]")
    return " > ".join(pieces)


def support_class(event: dict[str, str]) -> str:
    mnemonic = event["selected_exact_mnemonic"] != "UNKNOWN"
    formal = event["strict_formal_prompt"] != "NONE"
    if mnemonic and formal:
        return "EXACT_MNEMONIC_AND_STRICT_FORMAL_PROMPT"
    if mnemonic:
        return "EXACT_WORKING_MNEMONIC"
    if formal:
        return "STRICT_FORMAL_PROMPT_NO_WORD_VALUE"
    return "UNKNOWN_EXEMPLAR_WHOLE_CARD"


def context_confidence(owner_status: str, event: dict[str, str]) -> float:
    base = {
        "DIRECT_VISIBLE": 0.40,
        "INHERITED_VISIBLE": 0.34,
        "PAGE_OWNER_ONLY": 0.36,
        "UNRESOLVED": 0.18,
    }[owner_status]
    if event["selected_exact_mnemonic"] != "UNKNOWN" or event["strict_formal_prompt"] != "NONE":
        base = max(base, 0.46 if owner_status != "UNRESOLVED" else 0.24)
    if event["terminal_status"] == "TERMINAL":
        base = max(base, 0.40 if owner_status != "UNRESOLVED" else 0.22)
    return base


def scan_nouns(text: str) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    for noun, pattern, klass in NOUN_PATTERNS:
        if re.search(pattern, text, flags=re.I):
            found.append((noun, klass))
    return found


def contradiction(owner_row: dict[str, str], nouns: list[tuple[str, str]]) -> str:
    clauses: list[str] = []
    if owner_row["owner_status"] == "UNRESOLVED":
        clauses.append("Selbst der lokale Bildbesitzer ist an dieser Lücke unaufgelöst")
    classes = {klass for _, klass in nouns}
    if "UNPICTURED_SUBSTANCE_OR_PREPARATION" in classes:
        clauses.append("Stoff oder Zubereitung ist nicht sichtbar bestimmt")
    if "UNMARKED_OPERATION_OR_DIRECTION" in classes:
        clauses.append("keine Kontur trägt einen Pfeil oder eine Flussrichtung")
    if "VISIBLE_FIGURE_THERAPEUTIC_STATUS_UNCERTAIN" in classes:
        clauses.append("eine nackte Figur ist nicht automatisch Patientin oder therapeutisches Ziel")
    if "LOCAL_VISIBLE_FORM_FUNCTION_UNCERTAIN" in classes:
        clauses.append("die sichtbare Form beweist ihre Gefäß-, Becken- oder Leitungsfunktion nicht")
    if "UNPICTURED_PARAMETER_OR_STATE" in classes:
        clauses.append("Maß, Dauer, Wärme oder Zustand ist unbebilderter Quellenwert")
    if not clauses:
        clauses.append("die konkrete Handlung ist nur occurrence-gebundener Exemplarwert, keine Kartenbedeutung")
    return "; ".join(clauses) + "."


def clean_technical_rival(text: str, unresolved: bool) -> str:
    if unresolved:
        return "Formaler Rivale: opaker Exemplar-/Zellwert ohne rekonstruierbare Stationshandlung."
    matches = re.findall(r"LOCAL_(?:ARGUMENT|EXEMPLAR)\[(.*?)\]", text)
    value = "; ".join(matches) if matches else re.sub(r"\[[^\]]*\]", "", text)
    value = re.sub(r"\bB[1-6](?::|[-:])[A-Z0-9:_/-]+", "lokaler Posten", value)
    value = value.replace(";keine Kartenbedeutung", "")
    value = re.sub(r"\s+", " ", value).strip(" ;.")
    return f"Badehaus-technischer Rivale am selben Besitzer: {value}; keine Vererbung über einen Stationswechsel."


def aggregate_nouns(rows: list[dict[str, str]]) -> str:
    values: list[str] = []
    for row in rows:
        if row["unsupported_nouns"] != "NONE__ACTION_ONLY":
            values.extend(row["unsupported_nouns"].split("|"))
    return "|".join(ordered_unique(values)) if values else "NONE__ACTION_ONLY"


def render_local_sequence(rows: list[dict[str, str]], include_event_ids: bool) -> str:
    output: list[str] = []
    previous_owner = None
    for row in rows:
        owner = row["local_image_owner"]
        if owner != previous_owner:
            if previous_owner is None:
                output.append(f"[[LOKALER BESITZER: {OWNER_LABELS[owner]}]]")
            else:
                output.append(
                    f"[[STATIONSWECHSEL: {OWNER_LABELS[previous_owner]} -> {OWNER_LABELS[owner]}; "
                    "STOFF, ZIEL UND RICHTUNG WERDEN NICHT VERERBT]]"
                )
            previous_owner = owner
        prefix = f"E{row['event_serial']}=" if include_event_ids else ""
        output.append(prefix + row["concrete_german_meaning_in_context"])
    return " ".join(output)


def build() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    source_events = [row for row in read_tsv(EVENTS_IN) if int(row["event_serial"]) >= 101]
    source_fields = {
        row["field_id"]: row
        for row in read_tsv(FIELDS_IN)
        if row["field_id"].startswith("F") and int(row["field_id"][1:]) >= 21
    }
    cards = {row["joint_tuple_id"]: row for row in read_tsv(CARDS_IN)}
    owners = {
        row["unit_id"]: row
        for row in read_tsv(V71_OWNERS)
        if row["unit_kind"] == "PROSE_FIELD" and row["section"] == "BIOLOGICAL"
    }
    statements_source = {
        row["statement_id"]: row
        for row in read_tsv(V72_STATEMENTS)
        if row["record_unit_id"].startswith("B")
    }
    image_rows = {
        row["page"]: row
        for row in read_tsv(V70_IMAGES)
        if row["section"] == "BIOLOGICAL"
    }

    event_rows: list[dict[str, str]] = []
    previous_owner_by_record: dict[str, str] = {}
    for event in source_events:
        owner_row = owners[event["field_id"]]
        owner = owner_row["selected_visible_owner"]
        meaning = extract_exemplar(event["iatromedical_source_segment"])
        role = exemplar_role(meaning)
        noun_hits = scan_nouns(meaning)
        record = event["record_unit_id"]
        previous = previous_owner_by_record.get(record)
        if previous is None:
            break_status = "RECORD_START__RESET_ALL_LOCAL_STATE"
        elif previous != owner:
            break_status = "BREAK_VISIBLE_GAP__RESET_SUBSTANCE_TARGET_DIRECTION"
        else:
            break_status = "SAME_LOCAL_OWNER__NO_NEW_GEOMETRIC_CLAIM"
        previous_owner_by_record[record] = owner

        card = cards[event["joint_tuple_id"]]
        if card["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] != event["selected_exact_mnemonic"]:
            raise ValueError(f"card/event mnemonic mismatch at E{event['event_serial']}")
        event_rows.append({
            "event_serial": event["event_serial"],
            "record_unit_id": record,
            "page": event["page"],
            "locus": event["locus"],
            "field_id": event["field_id"],
            "statement_id": event["statement_id"],
            "joint_tuple_id": event["joint_tuple_id"],
            "local_image_owner": owner,
            "local_owner_label": OWNER_LABELS[owner],
            "owner_status": owner_row["owner_status"],
            "owner_confidence": owner_row["confidence"],
            "owner_break_before": break_status,
            "exact_literal_card_formal_exemplar_layer": literal_layer(event, owner, role),
            "v69_source_status": support_class(event),
            "concrete_german_meaning_in_context": meaning,
            "meaning_in_context_confidence": f"{context_confidence(owner_row['owner_status'], event):.2f}",
            "strongest_bathhouse_technical_or_formal_rival": clean_technical_rival(event["practical_source_segment"], owner_row["owner_status"] == "UNRESOLVED"),
            "strongest_contradiction": contradiction(owner_row, noun_hits),
            "unsupported_nouns": "|".join(noun for noun, _ in noun_hits) if noun_hits else "NONE__ACTION_ONLY",
            "carry_policy": "LOCAL_OWNER_ONLY; NEVER_CARRY_SUBSTANCE_TARGET_OR_DIRECTION_ACROSS_OWNER_BREAK",
            "image_geometry_guard": image_rows[event["page"]]["selected_geometry"],
            "terminal_status": event["terminal_status"],
            "semantic_ceiling": "OCCURRENCE_BALNEOLOGICAL_EXEMPLAR_NOT_CARD_STEM_SOUND_LANGUAGE_OR_MEDICAL_FACT",
        })

    by_field: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in event_rows:
        by_field[row["field_id"]].append(row)
        by_statement[row["statement_id"]].append(row)
        by_record[row["record_unit_id"]].append(row)

    field_rows: list[dict[str, str]] = []
    for fid in sorted(source_fields, key=lambda x: int(x[1:])):
        source = source_fields[fid]
        members = by_field[fid]
        field_rows.append({
            "field_id": fid,
            "record_unit_id": source["record_unit_id"],
            "page": source["page"],
            "locus": source["locus"],
            "statement_id": source["statement_id"],
            "event_serials": "|".join(row["event_serial"] for row in members),
            "local_image_owner": members[0]["local_image_owner"],
            "owner_status": members[0]["owner_status"],
            "literal_event_sequence": " || ".join(f"E{r['event_serial']}={r['exact_literal_card_formal_exemplar_layer']}" for r in members),
            "balneological_field_text": render_local_sequence(members, include_event_ids=False),
            "v69_template": source["primary_template"],
            "parse_status": source["parse_status"],
            "strongest_rival": " ".join(r["strongest_bathhouse_technical_or_formal_rival"] for r in members),
            "unsupported_nouns": aggregate_nouns(members),
            "strongest_contradiction": "Der Besitzer ist lokal; Medium, Richtung, Patientstatus und Handlung dürfen nicht über die Feldgrenze hinaus verallgemeinert werden.",
            "semantic_ceiling": "LOCAL_FIELD_STATION_EXEMPLAR_NOT_TRANSLATION",
        })

    statement_rows: list[dict[str, str]] = []
    for sid, source in statements_source.items():
        members = by_statement[sid]
        owners_in_statement = ordered_unique(r["local_image_owner"] for r in members)
        statement_rows.append({
            "statement_id": sid,
            "record_unit_id": source["record_unit_id"],
            "page": source["page"],
            "constituent_fields": source["constituent_fields"],
            "event_serials": "|".join(r["event_serial"] for r in members),
            "local_owner_sequence": "|".join(owners_in_statement),
            "contains_visible_owner_break": "YES" if len(owners_in_statement) > 1 else "NO",
            "balneological_statement_text": render_local_sequence(members, include_event_ids=False),
            "literal_event_sequence": " || ".join(f"E{r['event_serial']}={r['exact_literal_card_formal_exemplar_layer']}" for r in members),
            "v72_selected_technical_statement": source["selected_concrete_paraphrase"],
            "strongest_rival": source["strongest_rival"],
            "unsupported_nouns": aggregate_nouns(members),
            "line_crossing": source["line_crossing"],
            "strongest_contradiction": source["hardest_contradiction"],
            "semantic_ceiling": "OWNER_AWARE_BALNEOLOGICAL_STATEMENT_EXEMPLAR_NOT_TRANSLATION",
        })

    record_rows: list[dict[str, str]] = []
    for record in ("B1", "B2", "B3", "B4", "B5", "B6"):
        members = by_record[record]
        owner_sequence = ordered_unique(r["local_image_owner"] for r in members)
        breaks = [r["event_serial"] for r in members if r["owner_break_before"].startswith("BREAK_VISIBLE_GAP")]
        record_rows.append({
            "record_unit_id": record,
            "page": members[0]["page"],
            "field_ids": "|".join(ordered_unique(r["field_id"] for r in members)),
            "statement_ids": "|".join(ordered_unique(r["statement_id"] for r in members)),
            "event_serials": "|".join(r["event_serial"] for r in members),
            "local_owner_sequence": "|".join(owner_sequence),
            "owner_break_event_serials": "|".join(breaks) if breaks else "NONE",
            "historical_station_article_structure": RECORD_STRUCTURE[record],
            "fluent_record_synopsis": RECORD_SYNOPSIS[record],
            "continuous_event_bound_reading": render_local_sequence(members, include_event_ids=False),
            "event_alignment": render_local_sequence(members, include_event_ids=True),
            "strongest_global_rival": "Badehaus-/Waschhaus-Betriebsregister oder formale Bildlegende mit denselben lokalen Besitzern, ohne therapeutische Patientensemantik.",
            "unsupported_nouns": aggregate_nouns(members),
            "strongest_contradiction": "Die Bildseite trägt lokale Figuren-/Apparatestationen, aber keinen seitenweiten Stoff, keine gemeinsame Richtung und keinen geschlossenen Kreislauf.",
            "semantic_ceiling": "SIX_RECORD_STATION_ATLAS_WORKING_EDITION_NOT_DECIPHERMENT",
        })

    noun_occurrences: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    class_by_noun = {noun: klass for noun, _, klass in NOUN_PATTERNS}
    for row in event_rows:
        if row["unsupported_nouns"] == "NONE__ACTION_ONLY":
            continue
        for noun in row["unsupported_nouns"].split("|"):
            noun_occurrences[(noun, class_by_noun[noun])].append(row)
    rationale = {
        "UNPICTURED_SUBSTANCE_OR_PREPARATION": "Das Bild bestimmt weder Stoff noch Präparation; der Ausdruck stammt aus dem occurrence-gebundenen Badeexemplar.",
        "UNPICTURED_IMPLEMENT": "Das Gerät ist nicht sicher gezeichnet oder dem Ereignis zugeordnet.",
        "LOCAL_VISIBLE_FORM_FUNCTION_UNCERTAIN": "Eine passende lokale Form kann sichtbar sein, doch Gefäß-, Becken-, Öffnungs- oder Leitungsfunktion und Richtung bleiben unbestimmt.",
        "VISIBLE_FIGURE_THERAPEUTIC_STATUS_UNCERTAIN": "Die Figur ist sichtbar; Patientstatus, Körperziel und therapeutische Handlung sind nicht sichtbar festgelegt.",
        "UNPICTURED_PARAMETER_OR_STATE": "Maß, Dauer, Temperatur oder Prüfzustand ist ein unbebilderter Quellenwert.",
        "UNMARKED_OPERATION_OR_DIRECTION": "Keine Pfeile oder Quell-/Senkensignale legen Operation oder Bewegungsrichtung fest.",
    }
    noun_rows: list[dict[str, str]] = []
    for (noun, klass), members in sorted(noun_occurrences.items(), key=lambda x: (x[0][1], x[0][0].casefold())):
        noun_rows.append({
            "unsupported_noun": noun,
            "support_class": klass,
            "event_count": str(len(members)),
            "event_serials": "|".join(r["event_serial"] for r in members),
            "records": "|".join(ordered_unique(r["record_unit_id"] for r in members)),
            "pages": "|".join(ordered_unique(r["page"] for r in members)),
            "owners": "|".join(ordered_unique(r["local_image_owner"] for r in members)),
            "rationale": rationale[klass],
            "semantic_ceiling": "SOURCE_EXEMPLAR_NOUN_NOT_VOYNICH_LEXEME",
        })
    return event_rows, field_rows, statement_rows, record_rows, noun_rows


def md_escape(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def build_report(
    events: list[dict[str, str]],
    fields: list[dict[str, str]],
    statements: list[dict[str, str]],
    records: list[dict[str, str]],
    nouns: list[dict[str, str]],
) -> str:
    support_counts = Counter(r["v69_source_status"] for r in events)
    owner_counts = Counter(r["local_image_owner"] for r in events)
    break_events = [r for r in events if r["owner_break_before"].startswith("BREAK_VISIBLE_GAP")]
    unresolved_events = [r for r in events if r["owner_status"] == "UNRESOLVED"]
    out: list[str] = [
        "# V74 R2 — Biological station-atlas third edition",
        "",
        "Status: vollständige kreative balneologische/therapeutische Arbeitsedition; keine Entzifferung.",
        "",
        "## Unveränderter R2-Hintergrund",
        "",
    ]
    out += [f"{i}. {line}" for i, line in enumerate(R2_BACKGROUND, 1)]
    out += [
        "",
        "## Ergebnis",
        "",
        "Alle 281 Biological-Ereignisse, 115 Felder, 97 Aussagen und sechs Records sind lokal rekonstruiert. Die führende historische Arbeitslesung ist ein bebilderter Atlas von Bade-, Wasch-, Auflage-, Ruhe- und örtlichen Apparate-/Auslassstationen. Sie ist vollständig, aber occurrence-exemplarabhängig.",
        "",
        f"Der Atlas enthält {len(owner_counts)} verschiedene lokale Besitzer-IDs, {len(break_events)} recordinterne Besitzerwechsel und {len(unresolved_events)} Ereignisse an unaufgelösten Besitzern. Von 281 Ereignissen besitzen {281 - support_counts.get('UNKNOWN_EXEMPLAR_WHOLE_CARD', 0)} einen eingefrorenen Mnemonic-/Formalanker; {support_counts.get('UNKNOWN_EXEMPLAR_WHOLE_CARD', 0)} sind reine Exemplar-Ganzkarten.",
        "",
        "Ein Besitzerwechsel ist kein Rohrübergang. An jeder Markierung `STATIONSWECHSEL` werden Stoff, Ziel und Richtung zurückgesetzt. Nur innerhalb desselben lokalen Besitzers darf die Quellenedition einen Badezusatz oder Arbeitsstand fortführen. Selbst dort bleibt die Richtung unbestimmt, sofern kein Pfeil sichtbar ist.",
        "",
        "## Historischer Mechanismus",
        "",
        "Ein spätmittelalterliches Badekapitel kann einen Ort oder eine Station bebildern und im Text Wasserqualität, Wärme, Dauer, Benutzer, Anwendung und Wirkung ergänzen, ohne jeden Gegenstand im Bild zu zeigen. Die Voynich-Seiten passen besonders zu einem Stationsatlas: f81v besitzt ein gemeinsames Figurenfeld; f82r reiht mehrere teilweise getrennte Vignetten; f83r kombiniert getrennte Randstationen mit zwei echten, aber lokal begrenzten Apparateverbindungen.",
        "",
        "Die balneologische Edition wird deshalb nicht als Anatomie, Frauenheilkunde oder geschlossener Kreislauf formuliert. Nacktheit trägt Bad-/Anwendungsgattung, nicht Geschlechtsspezifik; Bogen, S-Lauf und Knoten tragen lokale Verbindung, nicht Medium oder Richtung.",
        "",
        "## Sechs kontinuierliche Recordlesungen",
        "",
    ]
    for record in records:
        out += [
            f"### {record['record_unit_id']} — {record['page']}",
            "",
            f"**Quellenstruktur:** `{record['historical_station_article_structure']}`",
            "",
            f"**Kurzlesung:** {record['fluent_record_synopsis']}",
            "",
            f"**Vollständige ereignisgebundene Lesung:** {record['continuous_event_bound_reading']}",
            "",
            f"**Stärkster Rivale:** {record['strongest_global_rival']}",
            "",
            f"**Härtester Widerspruch:** {record['strongest_contradiction']}",
            "",
        ]

    out += [
        "## Harte sichtbare Brüche",
        "",
        "Die vollständigen Records markieren jeden Besitzerwechsel. Vier Brüche liegen sogar innerhalb einer V72-Aussage:",
        "",
        "- `B2-S012`: ungelöste mittlere Station → unteres grünes Mehrfigurenfeld.",
        "- `B3-S016`: untere Korbgefäß-Randstation → ungelöster Zwischenposten.",
        "- `B3-S026`: ungelöster Zwischenposten → Hauptpaar am Bogen.",
        "- `B4-S015`: linke offene Fransenstation → rechte S-Lauf-/Mehrarmstation.",
        "",
        "Auch die übrigen owner changes sind Resets. Besonders f82r besitzt keine Kante von der oberen Zylindergruppe zum mittleren Gerät oder unteren Grünfeld; auf f83r sind linker und rechter unterer Apparat sichtbar getrennt.",
        "",
        "## Feldcensus",
        "",
        "| Record | Felder | Ereignisse | lokale Besitzer |",
        "|---|---:|---:|---|",
    ]
    for record in records:
        members = [f for f in fields if f["record_unit_id"] == record["record_unit_id"]]
        event_count = sum(len(f["event_serials"].split("|")) for f in members)
        out.append(f"| {record['record_unit_id']} | {len(members)} | {event_count} | {md_escape(record['local_owner_sequence'])} |")

    noun_classes = Counter(r["support_class"] for r in nouns)
    out += [
        "",
        "## Unsupported-noun audit",
        "",
        f"Die Edition weist {len(nouns)} kanonische ungestützte Quellbegriffe aus: " + ", ".join(f"{k}={v}" for k, v in sorted(noun_classes.items())) + ".",
        "",
        "`LOCAL_VISIBLE_FORM_FUNCTION_UNCERTAIN` und `VISIBLE_FIGURE_THERAPEUTIC_STATUS_UNCERTAIN` bedeuten: Die Form oder Figur ist real sichtbar, ihre Gefäßfunktion, Richtung oder Patientenrolle jedoch nicht. Wasser, Waschflotte, Dauer, Wärme, Klarheit und Maß bleiben vollständig unbebilderte Exemplarwerte. Die vollständigen Ereignisbindungen stehen in `V74_R2_UNSUPPORTED_NOUNS.tsv`.",
        "",
        "## Historische Vergleichsquellen",
        "",
        "1. Morgan Library, [MS G.74, f.23r](https://ica.themorgan.org/manuscript/page/22/77063), *De balneis Puteolanis*, ca. 1400 — nackte Benutzer in einem lokal bebilderten Bad.",
        "2. Biblissima/BnF, [Latin 8161, f.23](https://portail.biblissima.fr/en/ark:/43093/ifdata38fe2523aff0ab85012f88057adb9c6897a121d1), *De balneis Puteolanis* — Bad, Becken und Nacktheit als katalogisierte Motivfamilie.",
        "3. Biblioteca Angelica, [MS 1474](https://bibliotecaangelica.cultura.gov.it/de-balneis-puteolanis/), *De balneis Puteolanis* — achtzehn Bäderbilder zu Texten über Thermenwirkungen.",
        "4. BSB/Biblissima, [Clm 197 II](https://iiif.biblissima.fr/collections/manifest/8c98cf397390b92a940c9651dfb9fbfa0546de5c), Taccola, *De ingeneis*, ca. 1427–1441 — zeitnahe hydraulische Apparate als technischer Rivale, nicht als Voynich-Identifikation.",
        "",
        "## Grenze",
        "",
        "Die deutsche Lesung ist ein konsistentes ausgeschriebenes Masterexemplar. Sie bestätigt keine Karte als Wasser, Bad, Ziel, Maß, Ablauf oder Körperwort. Die badehaus-technische und rein formale Bildlegendenlesung bleibt vollständig möglich. Keine Oberfläche, Lautung, Teilzeichenfolge, Stammstruktur, Sprache oder zusätzliche Seite wurde verwendet; f84 und f84r blieben versiegelt.",
        "",
        "## Reproduzierbarkeit",
        "",
        "```bash",
        "python experiments/yolo/sidequest_theory_candidates_v74/build_v74_r2_biological_station_atlas.py",
        "python experiments/yolo/sidequest_theory_candidates_v74/validate_v74_r2_biological_station_atlas.py",
        "```",
        "",
    ]
    return "\n".join(out)


def main() -> None:
    events, fields, statements, records, nouns = build()
    write_tsv(EVENTS_OUT, events)
    write_tsv(FIELDS_OUT, fields)
    write_tsv(STATEMENTS_OUT, statements)
    write_tsv(RECORDS_OUT, records)
    write_tsv(NOUNS_OUT, nouns)
    REPORT_OUT.write_text(build_report(events, fields, statements, records, nouns), encoding="utf-8")
    print(json.dumps({
        "events": len(events),
        "fields": len(fields),
        "statements": len(statements),
        "records": len(records),
        "unsupported_nouns": len(nouns),
        "events_sha256": hashlib.sha256(EVENTS_OUT.read_bytes()).hexdigest(),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
