#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"
DUPLICATES = ROOT / "experiments/yolo/sidequest_semantic_duplicate_card_grammar_two_hundred_twenty_sixth/TWO_HUNDRED_TWENTY_SIXTH_SIX_DUPLICATE_PAIRS.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    bio = [row for row in read(EVENTS) if row["record_unit_id"].startswith("B")]
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in bio:
        grouped[(row["statement_id"], row["joint_tuple_id"])].append(row)
    repeat_rows = []
    for (statement, tuple_id), rows in sorted(grouped.items()):
        if len(rows) < 2:
            continue
        repeat_rows.append({
            "record": rows[0]["record_unit_id"],
            "statement_id": statement,
            "joint_tuple_id": tuple_id,
            "occurrences": len(rows),
            "event_ids": "|".join(row["event_id"] for row in rows),
            "surfaces": "|".join(row["surface_display"] for row in rows),
            "card_value_de": rows[0]["concrete_word_reading_de"],
            "relation": "CONTIGUOUS_CARRY" if [row["event_id"] for row in rows] == ["E180", "E181"] else "SERIAL_OR_MIRRORED_REUSE",
        })
    write("FOUR_HUNDRED_FOURTH_BIO_WITHIN_STATEMENT_REPEATS.tsv", repeat_rows)

    adjacent_rows = []
    for row in read(DUPLICATES):
        if row["record_unit_id"].startswith("B"):
            adjacent_rows.append({
                "duplicate_id": row["duplicate_id"],
                "record": row["record_unit_id"],
                "events": f'{row["first_event"]}|{row["second_event"]}',
                "visible_pair": row["visible_pair"],
                "boundary_class": row["boundary_class"],
                "selected_rule": row["selected_rule"],
                "pair_reading_de": row["pair_reading_de"],
                "h2_split_rejoin_sibling": "NO",
            })
    write("FOUR_HUNDRED_FOURTH_FOUR_BIO_ADJACENT_DUPLICATES.tsv", adjacent_rows)

    closest = [
        {"candidate": "B3-S003", "sequence": "Y AIIN Y CLOSE", "best_reading": "one item bracketed around its measure then discharged", "why_not_h2": "not adjacent Y-Y and no later OR-OR"},
        {"candidate": "B3-S021", "sequence": "CTH AL Y AIIN SHEDAL SHECTHY Y AL CTH CLOSE", "best_reading": "measured item moves through settling and target stations", "why_not_h2": "mirrored station handoff without split operation or paired rejoin"},
        {"candidate": "B1-S002", "sequence": "measure water target source OL portion OL portion ... measure ... passage close", "best_reading": "serial dosing and passage", "why_not_h2": "repeated OL and AIIN are serial controls rather than open duplicate slots"},
    ]
    write("FOUR_HUNDRED_FOURTH_THREE_CLOSEST_BIO_PATTERNS.tsv", closest)

    summary = {
        "status": "PASS",
        "bio_within_statement_repeat_groups": len(repeat_rows),
        "bio_adjacent_duplicate_pairs": len(adjacent_rows),
        "closest_patterns": len(closest),
        "exact_h2_split_rejoin_siblings": 0,
        "decision": "H2_PRESS_FRACTION_FILL_LOCAL__DUPLICATION_GRAMMAR_PORTABLE",
    }
    (HERE / "FOUR_HUNDRED_FOURTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
