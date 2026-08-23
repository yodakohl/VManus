#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    cards = rows("TWO_HUNDRED_FIFTY_SECOND_19_QUANTITY_AND_CONTROL_CARDS.tsv")
    occurrences = rows("TWO_HUNDRED_FIFTY_SECOND_58_OCCURRENCES.tsv")
    grades = rows("TWO_HUNDRED_FIFTY_SECOND_THREE_QUANTITY_ENDINGS.tsv")
    false = rows("TWO_HUNDRED_FIFTY_SECOND_TWO_FALSE_FRIENDS.tsv")
    cc, ec = Counter(r["quantity_ending"] for r in cards), Counter(r["quantity_ending"] for r in occurrences)
    checks = {
        "19_cards": len(cards) == 19,
        "58_occurrences": len(occurrences) == 58,
        "three_endings": len(grades) == 3,
        "two_false_friends": len(false) == 2,
        "card_split_10_6_1_2": cc == {"AIIN": 10, "AIN": 6, "AN": 1, "FALSE_FRIEND": 2},
        "event_split_39_15_1_3": ec == {"AIIN": 39, "AIN": 15, "AN": 1, "FALSE_FRIEND": 3},
        "expected_false_friends": {r["master_card_id"] for r in false} == {"MC059", "MC068"},
        "all_values_concrete": all(r["family_value_de"].strip() and r["card_value_de"].strip() for r in cards),
        "fixed_prose_pages_only": {r["page"] for r in occurrences} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_pages_absent": all("f84" not in "\t".join(r.values()).lower() for r in occurrences),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        print(json.dumps(result, indent=2, ensure_ascii=False))
        raise SystemExit(1)
    print(f"PASS {sum(checks.values())}/{len(checks)}")


if __name__ == "__main__":
    main()
