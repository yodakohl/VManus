#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    cards = rows("HUNDRED_TWENTY_FIFTH_SEVENTEEN_CARD_TEACHING_SHEET.tsv")
    hands = rows("HUNDRED_TWENTY_FIFTH_FOUR_HAND_CARD_TABLE.tsv")
    templates = rows("HUNDRED_TWENTY_FIFTH_EIGHT_TEMPLATE_SHEET.tsv")
    exercises = rows("HUNDRED_TWENTY_FIFTH_TWELVE_EXERCISES_AND_ANSWERS.tsv")
    lessons = rows("HUNDRED_TWENTY_FIFTH_EIGHT_DAY_CURRICULUM.tsv")
    checks = {
        "cards_17": len(cards) == 17,
        "hand_rows_17": len(hands) == 17,
        "templates_8": len(templates) == 8,
        "exercises_12": len(exercises) == 12,
        "lessons_8": len(lessons) == 8,
        "card_ids_unique": len({row["master_card"] for row in cards}) == 17,
        "reverse_keys_complete": {row["reverse_key"] for row in hands} == {row["master_card"] for row in cards},
        "answers_have_four_hand_set": all(len(row["visible_answers"].split(" || ")) >= 3 for row in exercises),
        "no_empty_cells": all(all(value for value in row.values()) for table in (cards, hands, templates, exercises, lessons) for row in table),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
