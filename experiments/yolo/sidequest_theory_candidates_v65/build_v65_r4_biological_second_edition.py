#!/usr/bin/env python3
"""Build the independent V65 R4 creative Biological edition."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
V54 = ROOT / "experiments/yolo/sidequest_theory_candidates_v54"
V61 = ROOT / "experiments/yolo/sidequest_theory_candidates_v61"
V63 = ROOT / "experiments/yolo/sidequest_theory_candidates_v63"
BIO = {"f81v", "f82r", "f83r"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


TEMPLATE_READING = {
    "ACTION_APPLY": "den aktiven Arbeitsstand am vorgesehenen Platz einsetzen",
    "ACTION_TEMPER": "den aktiven Arbeitsstand lauwarm temperieren",
    "LINK_ACTIVE": "den Posten mit dem aktiven Arbeitsstand verbinden",
    "PARAMETER_ASSIGN": "den vorgeschriebenen Wert oder Anteil setzen",
    "SELECT_PART": "den bezeichneten Anteil auswählen",
    "SELECT_PREVIOUS": "den vorigen recordlokalen Posten wiederaufnehmen",
    "STATE_GATE": "bis zum geforderten Arbeitszustand fortfahren",
    "TARGET_ASSIGN": "den nächsten Ziel- oder Stationsslot setzen",
    "TERMINAL_DRAIN": "den Schritt mit einem Ablauf-/Abführvorgang abschließen",
    "TERMINAL_FLUSH": "den Schritt mit einem Spülvorgang abschließen",
}


RECORD_TEXT = {
    "B1": {
        "role": "GRUNDKREISLAUF_MIT_GEMEINSAMEM_BAD",
        "medical": (
            "Setze im unteren Becken einen milden Kräuterzusatz an. Teile mehrere Portionen nach örtlicher Vorgabe ab, "
            "führe sie nacheinander in den gemeinsamen warmen Lauf und verbinde jeden neuen Posten mit dem aktiven Bad. "
            "Halte die Mischung lauwarm, rühre sie, lasse sie ruhen und prüfe den Zustand; fülle frischen Ansatz nach. "
            "Leite die gebrauchsfertige Portion zur nächsten sichtbaren Badestelle, spüle den Weg und lasse verbrauchte Flüssigkeit ab."
        ),
        "technical": (
            "Beschicke den unteren Sammelbehälter, dosiere mehrere Chargen, verbinde sie mit dem laufenden Kreislauf, "
            "temperiere und kläre sie, speise nach und übergib den Bestand über die erste Leitung; spüle und entleere die Teilstrecken."
        ),
        "graph": "OWNER/BASIN -> CHARGE* -> LINK -> TEMPER -> MIX -> REST -> GATE -> REFILL -> TRANSFER -> FLUSH/DRAIN",
        "revision": "Nicht jede kurze geschlossene Zelle ist eine neue Therapie; sie ist zunächst eine lokale Chargen- oder Stationsbuchung.",
    },
    "B2": {
        "role": "EINZELBAD_ODER_LOKALE_ANWENDUNGSSTATION",
        "medical": (
            "Gib eine bemessene Portion in das einzelne Becken und bringe sie auf milde Wärme. Führe die Flüssigkeit zwischen den "
            "sichtbaren Zugängen, lasse sie durch ein Tuch oder Sieb, fange sie wieder auf und erneuere den warmen Anteil. "
            "Wasche oder bade die bezeichnete Stelle mit der klaren Portion; nimm Rückstände als kurze Auflage, danach spüle und lasse ab. "
            "Die Folge der kurzen Schlusszellen notiert alternative Wiederholungen desselben Stationsgangs."
        ),
        "technical": (
            "Beschicke eine Mehrkammerstation, temperiere die Charge, schalte die Zugänge, filtere, fange auf, speise nach und führe "
            "mehrere standardisierte Spül-/Entleerungsvarianten aus."
        ),
        "graph": "INLET -> MEASURE -> TEMPER -> ROUTE_A/B -> FILTER -> CATCH -> REFILL -> USE_OR_TEST -> VARIANT_CLOSE*",
        "revision": "Figurnähe genügt nicht für Körpersemantik; Bad, Waschung und Auflage bleiben lokale medizinische Expansionen.",
    },
    "B3": {
        "role": "LANGER_IRRIGATIONS_UND_RUECKLAUFZYKLUS",
        "medical": (
            "Lasse den vorhandenen warmen Ansatz zunächst stehen und ziehe die klare obere Flüssigkeit ab. Gib frische warme Portionen "
            "hinzu, mische und führe sie in mehreren Gängen durch die sichtbaren Becken und Öffnungen. Benetze oder bade die jeweils "
            "bezeichnete Stelle, fange den Rücklauf unten auf, kläre ihn erneut und verwende nur den geeigneten Anteil weiter. "
            "Zwischen den Gängen werden Leitungen gespült, verbrauchter Bestand abgelassen und brauchbarer Rückstand recordlokal wiederaufgenommen."
        ),
        "technical": (
            "Fahre einen mehrstufigen Becken-, Filter- und Rücklaufprozess: setzen, dekantieren, warm nachspeisen, mischen, verteilen, "
            "unten sammeln, klären, rückführen, Teilstrecken spülen und entleeren."
        ),
        "graph": "SETTLE -> DECANT -> WARM_FEED -> MIX -> ROUTE* -> CONTACT/TEST -> LOWER_CATCH -> CLARIFY -> RETURN -> FLUSH/DRAIN*",
        "revision": "Die 38 Felder sind Phasen und Varianten eines langen Betriebsprotokolls, nicht 38 selbständige Sätze oder Beschwerden.",
    },
    "B4": {
        "role": "WARMER_NACHGANG_MIT_FILTER_UND_REINIGUNG",
        "medical": (
            "Spüle den bezeichneten Teil mit einer lauwarmen Portion. Nimm davon einen Anteil, führe ihn durch Tuch und verwende die "
            "gereinigte Flüssigkeit noch warm als Waschung oder Auflage. Reinige danach Gefäß und unteren Lauf, lasse die gebrauchte "
            "Flüssigkeit ab, setze einen frischen Posten an und gieße warmes Wasser nach."
        ),
        "technical": (
            "Führe einen zweiten Klär- und Transfergang aus, reinige Behälter und Leitung, entleere unten und speise die Station warm neu."
        ),
        "graph": "WARM_RINSE -> SELECT_PART -> FILTER -> USE_OR_TEST -> CLEAN_VESSEL -> CLEAN_RUN -> DRAIN -> RECHARGE",
        "revision": "Auflage ist kein Kartenwert; ohne Patient ergibt dieselbe Folge eine vollständige Wartungsroutine.",
    },
    "B5": {
        "role": "KURZER_WAERME_UND_UEBERGABENACHTRAG",
        "medical": (
            "Ziehe eine kleine Portion aus dem aktiven Ansatz ab, erwärme sie einmal und halte sie für die im Exemplar angegebene Zeit. "
            "Verbinde sie mit dem vorigen recordlokalen Posten und führe das vorgeschriebene Maß zur nächsten sichtbaren Stelle."
        ),
        "technical": "Ziehe eine Teilcharge ab, temperiere und halte sie, verknüpfe sie mit dem Vorposten und übergib sie an die Folgestation.",
        "graph": "DRAW_PART -> TEMPER_ONCE -> HOLD -> SELECT_PREVIOUS -> LINK -> MEASURE -> HANDOFF",
        "revision": "Der kurze Record liefert keinen Körper oder Zweck; medizinische Anwendung bleibt schwächer als technische Übergabe.",
    },
    "B6": {
        "role": "KALTER_OFFENER_FILTERGANG",
        "medical": (
            "Führe den vorhandenen Ansatz ohne erneutes Erhitzen weiter. Miss eine kleine Portion ab, gib sie durch eine einfache Öffnung "
            "oder ein Tuch und bringe sie an die im Bild bezeichnete Stelle."
        ),
        "technical": "Führe eine kalte Restcharge offen weiter, dosiere, filtere und übergib sie an den Zielslot.",
        "graph": "RESUME_COLD -> MEASURE -> SIMPLE_FILTER -> TARGET_HANDOFF -> OPEN_END",
        "revision": "Beide Felder sind offen; weder Abschluss noch Anwendung dürfen ergänzt werden.",
    },
}


def main() -> None:
    events = [r for r in read_tsv(V63 / "V63_SELECTED_381_EVENT_TEMPLATE_LEDGER.tsv") if r["page"] in BIO]
    fields = [r for r in read_tsv(V63 / "V63_SELECTED_135_FIELD_SLOT_PARSE.tsv") if r["page"] in BIO]
    statements = [r for r in read_tsv(V63 / "V63_SELECTED_116_STATEMENT_SLOT_PARSE.tsv") if r["page"] in BIO]
    v61 = {r["statement_id"]: r for r in read_tsv(V61 / "V61_SELECTED_116_SOURCE_STATEMENTS.tsv") if r["page"] in BIO}
    old_records = {r["record_id"]: r for r in read_tsv(V54 / "V54_SELECTED_SIX_BIO_RECORDS.tsv")}

    phrase_by_serial: dict[str, str] = {}
    for field in fields:
        serials = field["event_serials"].split("|")
        phrases = [x.strip() for x in field["local_exemplar_reading"].split(" ; ")]
        if len(serials) != len(phrases):
            raise ValueError(f"phrase/event mismatch in {field['field_id']}")
        phrase_by_serial.update(zip(serials, phrases))

    event_rows = []
    for row in events:
        template = row["event_template"]
        if row["selected_exact_mnemonic"] != "UNKNOWN":
            layer = "EXACT_CARD_DEFAULT"
        elif template != "EXEMPLAR_ONLY":
            layer = "FORMAL_SLOT_EXPANSION"
        else:
            layer = "LOCAL_EXEMPLAR"
        default = TEMPLATE_READING.get(template, phrase_by_serial[row["event_serial"]])
        event_rows.append({
            "event_serial": row["event_serial"],
            "page": row["page"],
            "locus": row["locus"],
            "record_id": row["record_unit_id"],
            "field_id": row["field_id"],
            "statement_id": row["statement_id"],
            "joint_tuple_id": row["joint_tuple_id"],
            "surface_display_only": row["surface_display_only"],
            "event_template": template,
            "selected_exact_mnemonic": row["selected_exact_mnemonic"],
            "interpretive_layer": layer,
            "complete_default_reading_de": default,
            "semantic_ceiling": "CREATIVE_LOCAL_DEFAULT_NOT_CARD_TRANSLATION",
        })

    event_by_field = defaultdict(list)
    for row in event_rows:
        event_by_field[row["field_id"]].append(row)
    field_rows = []
    for field in fields:
        event_defaults = " ; ".join(r["complete_default_reading_de"] for r in event_by_field[field["field_id"]])
        field_rows.append({
            "field_id": field["field_id"],
            "record_id": field["record_unit_id"],
            "page": field["page"],
            "locus": field["locus"],
            "statement_id": field["statement_id"],
            "event_count": field["event_count"],
            "parse_status": field["parse_status"],
            "licensed_sequence": field["licensed_primitive_sequence"],
            "complete_field_default_de": event_defaults,
            "field_close": "CLOSED" if any(r["event_template"].startswith("TERMINAL_") for r in event_by_field[field["field_id"]]) else "OPEN",
            "interpretive_limit": "LOCAL_EXPANSION_PRESERVES_EXACT_EVENT_ORDER",
        })

    fields_by_statement = defaultdict(list)
    for field in field_rows:
        fields_by_statement[field["statement_id"]].append(field)
    statement_rows = []
    for statement in statements:
        sid = statement["statement_id"]
        field_defaults = " | ".join(r["complete_field_default_de"] for r in fields_by_statement[sid])
        statement_rows.append({
            "statement_id": sid,
            "record_id": statement["record_unit_id"],
            "page": statement["page"],
            "statement_ordinal": statement["statement_ordinal_in_record"],
            "field_ids": statement["constituent_fields"],
            "event_count": statement["event_count"],
            "parse_status": statement["parse_status"],
            "register_transition": statement["parser_register_update_trace"],
            "complete_statement_default_de": field_defaults,
            "prior_v61_source_expansion": v61[sid]["concrete_workshop_reading"],
            "interpretive_limit": "NO_NEW_CARD_MEANING",
        })

    record_rows = []
    graph_rows = []
    for rid in ["B1", "B2", "B3", "B4", "B5", "B6"]:
        cfg = RECORD_TEXT[rid]
        old = old_records[rid]
        record_rows.append({
            "record_id": rid,
            "page": old["folio"],
            "field_count": old["field_count"],
            "event_count": old["event_count"],
            "statement_count": sum(1 for r in statement_rows if r["record_id"] == rid),
            "selected_role": cfg["role"],
            "complete_iatromedical_default_de": cfg["medical"],
            "complete_technical_rival_de": cfg["technical"],
            "revision_from_v54": cfg["revision"],
            "confidence": "LOW_TO_MEDIUM_CREATIVE",
        })
        graph_rows.append({
            "record_id": rid,
            "page": old["folio"],
            "process_graph": cfg["graph"],
            "medical_instantiation": cfg["medical"],
            "technical_instantiation": cfg["technical"],
            "shared_formal_core": "ORDERED_STATE_AND_TRANSFER_WORKFLOW",
        })

    write_tsv(HERE / "V65_R4_281_EVENT_BIO_INTERLINEAR.tsv", event_rows, list(event_rows[0]))
    write_tsv(HERE / "V65_R4_115_FIELD_BIO_EDITION.tsv", field_rows, list(field_rows[0]))
    write_tsv(HERE / "V65_R4_97_STATEMENT_BIO_EDITION.tsv", statement_rows, list(statement_rows[0]))
    write_tsv(HERE / "V65_R4_6_RECORD_BIO_EDITION.tsv", record_rows, list(record_rows[0]))
    write_tsv(HERE / "V65_R4_PROCESS_GRAPHS.tsv", graph_rows, list(graph_rows[0]))

    checks = {
        "events_281": len(event_rows) == 281,
        "fields_115": len(field_rows) == 115,
        "statements_97": len(statement_rows) == 97,
        "records_6": len(record_rows) == 6,
        "all_event_defaults_nonempty": all(r["complete_default_reading_de"].strip() for r in event_rows),
        "event_serials_101_to_381": [int(r["event_serial"]) for r in event_rows] == list(range(101, 382)),
        "record_event_counts": Counter(r["record_id"] for r in event_rows) == Counter({"B1": 66, "B2": 62, "B3": 86, "B4": 47, "B5": 11, "B6": 9}),
        "record_field_counts": Counter(r["record_id"] for r in field_rows) == Counter({"B1": 24, "B2": 26, "B3": 38, "B4": 20, "B5": 5, "B6": 2}),
        "field_status": Counter(r["parse_status"] for r in field_rows) == Counter({"UNIQUE": 14, "AMBIGUOUS": 41, "UNPARSED": 60}),
        "statement_status": Counter(r["parse_status"] for r in statement_rows) == Counter({"UNIQUE": 12, "AMBIGUOUS": 35, "UNPARSED": 50}),
        "sealed_pages_absent": all(not r["page"].startswith("f84") for r in event_rows),
    }
    payload = {
        "artifact": "V65_R4_BIOLOGICAL_SECOND_EDITION",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "counts": {"events": len(event_rows), "fields": len(field_rows), "statements": len(statement_rows), "records": len(record_rows)},
        "event_layers": dict(Counter(r["interpretive_layer"] for r in event_rows)),
        "checks": checks,
        "interpretive_limit": "Coverage validates editorial completeness, not any medical, technical, lexical, or semantic assignment.",
    }
    (HERE / "V65_R4_VALIDATION.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if payload["status"] != "PASS":
        raise SystemExit(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
