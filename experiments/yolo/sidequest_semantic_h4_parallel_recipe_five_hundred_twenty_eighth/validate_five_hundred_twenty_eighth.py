#!/usr/bin/env python3
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    events = read("FIVE_HUNDRED_TWENTY_EIGHTH_H4_EIGHTEEN_EVENT_REVERSE_BUILD.tsv")
    statements = read("FIVE_HUNDRED_TWENTY_EIGHTH_FOUR_H4_STATEMENTS.tsv")
    stages = read("FIVE_HUNDRED_TWENTY_EIGHTH_EIGHT_STAGE_H4_RECIPE.tsv")
    comparison = read("FIVE_HUNDRED_TWENTY_EIGHTH_H3_H4_PROCESS_COMPARISON.tsv")
    staged_events = [event for row in stages for event in row["selected_event_ids"].split("|")]
    shared_primitives = [row for row in comparison if row["shared"] == "YES" and not row["comparison_unit"].startswith("EXACT")]
    shared_cards = [row["comparison_unit"] for row in comparison if row["comparison_unit"].startswith("EXACT")]
    checks = {
        "events18": len(events) == 18 and [row["event_id"] for row in events] == [f"E{i:03d}" for i in range(56, 74)],
        "statements4": len(statements) == 4,
        "stages8": len(stages) == 8,
        "stage_event_partition": len(staged_events) == 18 and set(staged_events) == {row["event_id"] for row in events},
        "every_card_has_source_clause": all(row["minimum_source_clause_de"] for row in events),
        "owner_consistent": {row["owner_source"] for row in events} == {"IMAGE_H4_WHOLE_BROAD_LEAF_PLANT"},
        "surface_count18": sum(len(row["surfaces"].split()) for row in statements) == 18,
        "shared_primitives6": len(shared_primitives) == 6,
        "shared_exact_cards2": set(shared_cards) == {"EXACT_CARD_PROC009", "EXACT_CARD_PROC019"},
        "line_not_sentence": all(row["sentence_ends_at_physical_line"] == "NO" for row in statements),
        "seal_absent": all(not row["locus"].lower().startswith("f84") for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_TWENTY_EIGHTH_VALIDATION.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
