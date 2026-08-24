#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREV = ROOT / "experiments/yolo/sidequest_semantic_biological_reverse_compiler_four_hundred_fifty_first"
RESET_SOURCE = ROOT / "experiments/yolo/sidequest_semantic_biological_union_four_hundred_forty_seventh/FOUR_HUNDRED_FORTY_SEVENTH_OWNER_RESETS.tsv"

GROUPS = (
    ("B1", 1, 4, "Ansatz und erste Umsetzung"),
    ("B1", 5, 8, "Weiterfuehrung und Abkuehlung"),
    ("B1", 9, 13, "Kurze Ansaetze und Waschgang"),
    ("B1", 14, 18, "Auffangen Fuellen und Zielarbeit"),
    ("B1", 19, 21, "Absetzen Waermen Seihen"),
    ("B2", 1, 6, "Obere Stationen"),
    ("B2", 7, 10, "Seitliches Becken"),
    ("B2", 11, 11, "Zentralgefaess"),
    ("B2", 12, 14, "Zentralgefaess zum unteren Lauf"),
    ("B2", 15, 22, "Untere Abschlussreihe"),
    ("B3", 1, 5, "Obere Paarstation erster Gang"),
    ("B3", 6, 10, "Obere Paarstation Zielgang"),
    ("B3", 11, 16, "Bereitgang zum Mittelteil"),
    ("B3", 17, 21, "Mittlere Station"),
    ("B3", 22, 26, "Mittlere Station zum Unterteil"),
    ("B3", 27, 30, "Untere Station Wasser und Fuellung"),
    ("B3", 31, 34, "Untere Station Schlussgang"),
    ("B4", 1, 4, "Linker oberer Ansatz"),
    ("B4", 5, 8, "Tuch Seihen Waermen"),
    ("B4", 9, 12, "Fortsetzung und Abfuehrung"),
    ("B4", 13, 15, "Wasserlauf zum rechten Besitzer"),
    ("B4", 16, 16, "Rechter Schluss"),
    ("B5", 1, 3, "Warmer Zweistufengang"),
    ("B6", 1, 1, "Rohansatz Tuch und Ziel"),
)


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(name)
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sid(record: str, number: int) -> str:
    return f"{record}-S{number:03d}"


def main() -> None:
    statements = read(PREV / "FOUR_HUNDRED_FIFTY_FIRST_97_STATEMENT_EDITION.tsv")
    events = read(PREV / "FOUR_HUNDRED_FIFTY_FIRST_281_EVENT_EDITION.tsv")
    statement_by_id = {row["statement_id"]: row for row in statements}
    event_by_id = {row["event_id"]: row for row in events}
    visible_changes = [row for row in read(RESET_SOURCE) if row["reset_kind"] == "VISIBLE_OWNER_CHANGE"]

    procedures = []
    statement_ledger = []
    for number, (record, first, last, title) in enumerate(GROUPS, 1):
        procedure_id = f"BP{number:02d}"
        ids = [sid(record, value) for value in range(first, last + 1)]
        rows = [statement_by_id[item] for item in ids]
        event_ids = [event_id for row in rows for event_id in row["event_ids"].split("|")]
        change_ids = [change["event_id"] for change in visible_changes if change["event_id"] in event_ids]
        statement_trace = " ".join(f"[{row['statement_id']}] {row['continuous_reading_de']}" for row in rows)
        transition_note = "NONE" if not change_ids else "HARTER SICHTBARER BESITZERWECHSEL BEI " + "|".join(change_ids)
        procedures.append({
            "procedure_id": procedure_id, "record_unit_id": record, "title_de": title,
            "statements": len(rows), "statement_ids": "|".join(ids), "events": len(event_ids),
            "event_ids": "|".join(event_ids), "owner_zones": "|".join(dict.fromkeys(zone for row in rows for zone in row["owner_zones"].split("|"))),
            "hard_scene_transition_events": "NONE" if not change_ids else "|".join(change_ids),
            "transition_note_de": transition_note, "continuous_workshop_prose_de": statement_trace,
        })
        for position, row in enumerate(rows, 1):
            statement_ledger.append({
                "procedure_id": procedure_id, "procedure_position": position,
                "statement_id": row["statement_id"], "record_unit_id": record,
                "event_ids": row["event_ids"], "owner_zones": row["owner_zones"],
                "owner_break_inside_statement": row["owner_break_inside_statement"],
                "continuous_reading_de": row["continuous_reading_de"],
            })
    write("FOUR_HUNDRED_FIFTY_SECOND_24_PROCEDURES.tsv", procedures)
    write("FOUR_HUNDRED_FIFTY_SECOND_97_STATEMENT_LEDGER.tsv", statement_ledger)

    transitions = []
    for change in visible_changes:
        procedure = next(row for row in procedures if change["event_id"] in row["event_ids"].split("|"))
        event = event_by_id[change["event_id"]]
        transitions.append({
            "event_id": change["event_id"], "record_unit_id": change["record_unit_id"],
            "procedure_id": procedure["procedure_id"], "statement_id": event["statement_id"],
            "from_owner": change["from_owner"], "to_owner": change["to_owner"],
            "inside_statement": next(row for row in statements if row["statement_id"] == event["statement_id"])["owner_break_inside_statement"],
            "reading_rule": "DO_NOT_END_SENTENCE; CHANGE_VISIBLE_OWNER_ONLY",
        })
    write("FOUR_HUNDRED_FIFTY_SECOND_SEVEN_SCENE_TRANSITIONS.tsv", transitions)

    lines = ["# Continuous Biological workshop edition", "", "Physical lines do not end sentences. Bold transition notes mark only visible owner changes.", ""]
    for record in ("B1", "B2", "B3", "B4", "B5", "B6"):
        lines.extend([f"## {record}", ""])
        for procedure in procedures:
            if procedure["record_unit_id"] != record:
                continue
            lines.extend([f"### {procedure['procedure_id']} — {procedure['title_de']}", ""])
            if procedure["transition_note_de"] != "NONE":
                lines.extend([f"**{procedure['transition_note_de']}**", ""])
            lines.extend([procedure["continuous_workshop_prose_de"], ""])
    (HERE / "FOUR_HUNDRED_FIFTY_SECOND_CONTINUOUS_BIOLOGICAL_EDITION.md").write_text("\n".join(lines), encoding="utf-8")

    summary = {
        "status": "PASS", "records": 6, "procedures": len(procedures), "statements": len(statement_ledger),
        "events": sum(int(row["events"]) for row in procedures), "hard_scene_transitions": len(transitions),
        "inside_statement_transitions": sum(row["inside_statement"] == "YES" for row in transitions),
        "procedure_counts_by_record": {record: sum(row["record_unit_id"] == record for row in procedures) for record in ("B1", "B2", "B3", "B4", "B5", "B6")},
    }
    (HERE / "FOUR_HUNDRED_FIFTY_SECOND_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
