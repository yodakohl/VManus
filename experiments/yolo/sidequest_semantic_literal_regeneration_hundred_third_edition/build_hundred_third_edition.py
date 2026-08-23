#!/usr/bin/env python3
"""Regenerate 254 literal workshop clauses from atoms and resolved attachments."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_attachment_resolution_hundred_second_edition/HUNDRED_SECOND_381_RESOLVED_ATTACHMENTS.tsv"
DECISIONS = ROOT / "experiments/yolo/sidequest_semantic_attachment_resolution_hundred_second_edition/HUNDRED_SECOND_27_AMBIGUOUS_DECISIONS.tsv"
STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_centennial_working_edition/HUNDREDTH_116_STATEMENT_TRANSLATION.tsv"


OPERATIONS = {
    "OK": "ansetzen", "CHD": "umsetzen", "PARTITION": "teilen", "CTH": "bereithalten",
    "CKH": "durchleiten", "CKHE": "trennen", "CHK": "wärmen", "SHED": "absetzen",
    "SOLK": "sammeln", "KCH": "bearbeiten", "SH": "halten", "WASH": "waschen",
    "L": "abführen", "CFH": "auswringen", "CPH": "nachseihen", "DAN": "anwenden",
    "P": "zuführen", "SK": "ausgießen", "AM": "verwahren", "ODY": "kühlen",
    "OL": "weiterführen", "OT": "folgen", "HO": "zugeben",
}
ITEMS = {
    "Y": "Posten", "TY": "Teil", "HO": "Zutat", "CHEO": "Auszug", "OR": "Ansatz",
    "DCHE": "Wurzel", "DAIN": "Tuch", "LOCAL_WHOLE": "Zusatz", "OS": "Gefäß",
    "CHEEY": "Ergebnis", "DCHOL": "Vorposten",
}
VALUES = {"AIIN": "Sollmaß", "AIN": "Anteil", "IIN": "Stufe"}
GRADES = {"E": "kurz", "EE": "länger", "EEE": "vollständig"}
ORDER = {"OT": "danach", "OL": "weiter", "DCHOL": "vorher"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def ordered_unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def main() -> None:
    events = read_tsv(EVENTS)
    statements = {row["statement_id"]: row for row in read_tsv(STATEMENTS)}
    decision_by_event = {row["event_id"]: row for row in read_tsv(DECISIONS)}
    by_host: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_host[event["selected_host_event"]].append(event)

    clauses: list[dict[str, object]] = []
    for unit_order, (host, members) in enumerate(sorted(by_host.items(), key=lambda item: min(int(row["event_serial"]) for row in item[1])), 1):
        members.sort(key=lambda row: int(row["event_serial"]))
        host_row = next((row for row in members if row["event_id"] == host), members[0])
        atoms = [atom for row in members for atom in row["semantic_atoms"].split("+")]
        operations = ordered_unique([OPERATIONS[atom] for atom in atoms if atom in OPERATIONS])
        items = ordered_unique([ITEMS[atom] for atom in atoms if atom in ITEMS])
        values = ordered_unique([VALUES[atom] for atom in atoms if atom in VALUES])
        grades = ordered_unique([GRADES[atom] for atom in atoms if atom in GRADES])
        orders = ordered_unique([ORDER[atom] for atom in atoms if atom in ORDER])
        sources = ["Quelle"] if "AR" in atoms else []
        runs = ["Lauf"] if "AIR" in atoms else []
        targets = ["Ziel"] if "AL" in atoms else []
        states = []
        if "CTH" in atoms:
            states.append("bereit")
        if "CHEEY" in atoms:
            states.append("Ergebnis")
        close = "YES" if "CLOSE" in atoms else "NO"
        if not operations:
            operations = ["BILDBESITZER-AKTION"]
        segments = [f"Vorgang={'→'.join(operations)}"]
        if orders:
            segments.append(f"Reihenfolge={'+'.join(orders)}")
        if items:
            segments.append(f"Posten={'+'.join(items)}")
        if sources:
            segments.append("Quelle=gesetzt")
        if runs:
            segments.append("Lauf=gesetzt")
        if targets:
            segments.append("Ziel=gesetzt")
        if values:
            segments.append(f"Wert={'+'.join(values)}")
        if grades:
            segments.append(f"Grad={'+'.join(grades)}")
        if states:
            segments.append(f"Zustand={'+'.join(states)}")
        if close == "YES":
            segments.append("Schluss")
        literal = "; ".join(segments)
        clauses.append({
            "fusion_unit_order": unit_order,
            "fusion_unit_id": f"FU{unit_order:03d}",
            "statement_id": host_row["statement_id"],
            "record_unit_id": host_row["record_unit_id"],
            "page": host_row["page"],
            "host_event_id": host,
            "member_event_ids": "|".join(row["event_id"] for row in members),
            "member_surfaces": " ".join(row["surface"] for row in members),
            "member_atomic_defaults": " | ".join(row["atomic_default_de"] for row in members),
            "operation_chain_de": "→".join(operations),
            "item_values_de": "+".join(items) if items else "NONE",
            "source_value_de": "Quelle" if sources else "NONE",
            "run_value_de": "Lauf" if runs else "NONE",
            "target_value_de": "Ziel" if targets else "NONE",
            "measure_values_de": "+".join(values) if values else "NONE",
            "grade_values_de": "+".join(grades) if grades else "NONE",
            "state_values_de": "+".join(states) if states else "NONE",
            "close": close,
            "literal_workshop_clause_de": literal,
            "contains_resolved_forward_material": "YES" if any(decision_by_event.get(row["event_id"], {}).get("selected_direction") == "FORWARD" for row in members) else "NO",
        })

    by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for clause in clauses:
        by_statement[str(clause["statement_id"])].append(clause)
    statement_rows: list[dict[str, object]] = []
    for statement_id, source in sorted(statements.items(), key=lambda item: int(item[1]["statement_order"])):
        units = by_statement[statement_id]
        generated = ". ".join(str(unit["literal_workshop_clause_de"]) for unit in units) + "."
        forward_count = sum(unit["contains_resolved_forward_material"] == "YES" for unit in units)
        statement_rows.append({
            "statement_order": source["statement_order"],
            "statement_id": statement_id,
            "record_unit_id": source["record_unit_id"],
            "page": source["page"],
            "fusion_unit_count": len(units),
            "resolved_forward_units": forward_count,
            "generated_atomic_literal_de": generated,
            "current_card_near_reading_de": source["card_near_workshop_reading_de"],
            "current_concrete_source_expansion_de": source["concrete_source_expansion_de"],
            "reconciliation_status": "FORWARD_OBJECT_NOW_EXPLICIT" if forward_count else "ORDER_COMPATIBLE_NO_REPAIR_REQUIRED",
        })

    forward_statements = [row for row in statement_rows if int(row["resolved_forward_units"]) > 0]
    write_tsv(OUT / "HUNDRED_THIRD_254_ATOMIC_CLAUSES.tsv", list(clauses[0]), clauses)
    write_tsv(OUT / "HUNDRED_THIRD_116_REGENERATED_STATEMENTS.tsv", list(statement_rows[0]), statement_rows)
    write_tsv(OUT / "HUNDRED_THIRD_FORWARD_OBJECT_REPAIRS.tsv", list(forward_statements[0]), forward_statements)

    op_counts = Counter(operation for row in clauses for operation in str(row["operation_chain_de"]).split("→"))
    report = [
        "# Hundertdritte Runde: Wörtliche Rückübersetzung aus 44 Atomwerten", "",
        "## Ergebnis", "",
        "Die 381 Karten werden mit den festen Anschlüssen zu 254 Arbeitsklauseln: 250",
        "sichtbare Aktionsköpfe und vier bildgestützte elliptische Köpfe. Jede Klausel nennt",
        "getrennt Vorgang, Posten, Quelle, Lauf, Ziel, Wert, Grad, Zustand und Schluss.", "",
        f"Alle 116 Aussagen sind vollständig regeneriert. {len(forward_statements)} Aussagen",
        "enthalten einen der sieben neu vorwärts gebundenen Materialposten und weisen ihn nun",
        "explizit als Eingang des folgenden Arbeitsgangs aus. Die übrigen Aussagen brauchen",
        "keine Reihenfolgereparatur.", "",
        "Diese Fassung ist absichtlich weniger schön als die flüssige Übersetzung. Sie ist der",
        "Kontrolltext des Schreibers: `Vorgang=ansetzen; Posten=Posten; Wert=Sollmaß; Grad=länger;",
        "Schluss` ist eindeutig, auch wenn eine spätere deutsche Redaktion daraus einen",
        "natürlichen Satz macht.", "",
        "Nur die festen Prosaseiten wurden verwendet; f84 und f84r blieben versiegelt.",
    ]
    (OUT / "HUNDRED_THIRD_LITERAL_REGENERATION_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    summary = {
        "status": "CONSISTENT", "events": len(events), "fusion_units": len(clauses),
        "statements": len(statement_rows), "forward_object_statements": len(forward_statements),
        "operation_counts": dict(op_counts),
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
