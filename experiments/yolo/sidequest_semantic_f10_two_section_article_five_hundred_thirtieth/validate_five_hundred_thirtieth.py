#!/usr/bin/env python3
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    events = read("FIVE_HUNDRED_THIRTIETH_F10_THIRTY_EIGHT_EVENT_ARTICLE.tsv")
    statements = read("FIVE_HUNDRED_THIRTIETH_FIVE_F10_STATEMENTS.tsv")
    stages = read("FIVE_HUNDRED_THIRTIETH_EIGHT_STAGE_F10_ARTICLE.tsv")
    models = read("FIVE_HUNDRED_THIRTIETH_TWO_MODEL_COMPARISON.tsv")
    boundary = read("FIVE_HUNDRED_THIRTIETH_H1_H2_BOUNDARY.tsv")
    stage_events = [event for row in stages for event in row["event_ids"].split("|")]
    shared_cards = {"PROC003", "PROC009", "PROC013", "PROC014"}
    h1_cards = {row["card_no"] for row in events if row["record"] == "H1"}
    h2_cards = {row["card_no"] for row in events if row["record"] == "H2"}
    checks = {
        "events38": len(events) == 38 and [row["event_id"] for row in events] == [f"E{i:03d}" for i in range(1, 39)],
        "records14_24": sum(row["record"] == "H1" for row in events) == 14 and sum(row["record"] == "H2" for row in events) == 24,
        "statements5": len(statements) == 5,
        "stages8": len(stages) == 8,
        "stage_partition": len(stage_events) == 38 and set(stage_events) == {row["event_id"] for row in events},
        "owner_split": {row["visible_owner_id"] for row in events}
        == {"IMAGE_H1_ROOT_AXIS_AND_RED_SWELLINGS", "IMAGE_H2_UPPER_STEM_FLOWER_BUD_LEAF_SET"},
        "shared_exact_cards4": h1_cards & h2_cards == shared_cards,
        "no_close_cards": all("CLOSE" not in row["primitive"] for row in events)
        and all(row["licensed_close_present"] == "NO" for row in statements),
        "boundary_one": len(boundary) == 1 and boundary[0]["left_event"] == "E014" and boundary[0]["right_event"] == "E015",
        "model_features6": len(models) == 6,
        "seal_absent": all(not row["locus"].lower().startswith("f84") for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_THIRTIETH_VALIDATION.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
