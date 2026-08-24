#!/usr/bin/env python3
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    events = read("FIVE_HUNDRED_TWENTY_SEVENTH_H3_SEVENTEEN_EVENT_REVERSE_BUILD.tsv")
    statements = read("FIVE_HUNDRED_TWENTY_SEVENTH_FOUR_H3_STATEMENTS.tsv")
    stages = read("FIVE_HUNDRED_TWENTY_SEVENTH_EIGHT_STAGE_H3_RECIPE.tsv")
    additions = read("FIVE_HUNDRED_TWENTY_SEVENTH_H3_EXPANSION_LEDGER.tsv")
    staged_events = [event for row in stages for event in row["selected_event_ids"].split("|")]
    checks = {
        "events17": len(events) == 17 and [row["event_id"] for row in events] == [f"E{i:03d}" for i in range(39, 56)],
        "statements4": len(statements) == 4
        and [row["statement_id"] for row in statements] == ["H3-S001", "H3-S002", "H3-S003", "H3-S004"],
        "stages8": len(stages) == 8,
        "stage_event_partition": len(staged_events) == 17 and set(staged_events) == {row["event_id"] for row in events},
        "every_card_has_source_clause": all(row["minimum_source_clause_de"] for row in events),
        "owner_consistent": {row["owner_source"] for row in events} == {"IMAGE_H3_WHOLE_DENSE_CROWN_PLANT"},
        "surface_count17": sum(len(row["surfaces"].split()) for row in statements) == 17,
        "line_not_sentence": all(row["sentence_ends_at_physical_line"] == "NO" for row in statements),
        "withholds_species_medium_disease": {row["item"] for row in additions if row["working_status"] == "WITHHELD"}
        == {"Pflanzenart", "Wasser/Wein/Öl", "Krankheit/Körperteil"},
        "seal_absent": all(not row["locus"].lower().startswith("f84") for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_TWENTY_SEVENTH_VALIDATION.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
