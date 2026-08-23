#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    audit = rows("HUNDRED_TWENTY_THIRD_57_OBSERVED_REGISTER_PARSES.tsv")
    templates = rows("HUNDRED_TWENTY_THIRD_EIGHT_SOURCE_TEMPLATES.tsv")
    exercises = rows("HUNDRED_TWENTY_THIRD_TWELVE_SOURCE_TO_CARD_EXERCISES.tsv")
    checks = {
        "observed_parses_57": len(audit) == 57,
        "templates_8": len(templates) == 8,
        "exercises_12": len(exercises) == 12,
        "all_shared_cards_known": all(len(row["compiled_master_card_ids"].split()) == len(row["compiled_master_cards"].split()) for row in exercises),
        "two_registers_present": {row["register_grammar"] for row in audit} == {"HERBAL_ARTICLE", "BIOLOGICAL_CELL"},
        "direct_plus_one_at_least_50": sum(int(row["local_order_inversions"]) <= 1 for row in audit) >= 50,
        "paired_frame_present": any("PAIRED_MEASURE_FRAME" in row["collapsed_units"] for row in audit),
        "carry_frame_present": any("CARRY_BATCH_FRAME" in row["collapsed_units"] for row in audit),
        "novel_exercises_present": any(row["manuscript_status"] == "NEW_WORKSHOP_COMBINATION" for row in exercises),
        "no_empty_cells": all(all(value for value in row.values()) for table in (audit, templates, exercises) for row in table),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
