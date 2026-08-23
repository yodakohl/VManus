#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    copies = rows("HUNDRED_TWENTY_FOURTH_48_FOUR_HAND_COPIES.tsv")
    tokens = rows("HUNDRED_TWENTY_FOURTH_TOKEN_RENDERER_TRACE.tsv")
    exercises = rows("HUNDRED_TWENTY_FOURTH_TWELVE_ROUNDTRIP_SUMMARY.tsv")
    hands = rows("HUNDRED_TWENTY_FOURTH_FOUR_HAND_RESULTS.tsv")
    checks = {
        "copies_48": len(copies) == 48,
        "exercises_12": len(exercises) == 12,
        "hands_4": len(hands) == 4,
        "all_copy_roundtrips": all(row["card_roundtrip"] == "PASS" for row in copies),
        "all_token_roundtrips": all(row["token_roundtrip"] == "PASS" for row in tokens),
        "each_exercise_four_hands": all(sum(row["exercise_id"] == exercise["exercise_id"] for row in copies) == 4 for exercise in exercises),
        "every_exercise_varies": all(int(row["distinct_visible_copies"]) >= 3 for row in exercises),
        "unique_surface_reverse_key": all(row["source_master_card"] == row["recovered_master_card"] for row in tokens),
        "no_empty_cells": all(all(value for value in row.values()) for table in (copies, tokens, exercises, hands) for row in table),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
