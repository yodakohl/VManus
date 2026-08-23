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
    cards = rows("TWO_HUNDRED_FORTY_FOURTH_25_OPERATION_CARDS.tsv")
    occurrences = rows("TWO_HUNDRED_FORTY_FOURTH_28_OPERATION_OCCURRENCES.tsv")
    revised = rows("TWO_HUNDRED_FORTY_FOURTH_REVISED_66_CARD_DICTIONARY.tsv")
    cc, ec = Counter(r["composition_status"] for r in cards), Counter(r["composition_status"] for r in occurrences)
    checks = {
        "25_operation_cards": len(cards) == 25,
        "28_occurrences": len(occurrences) == 28,
        "66_revised_cards": len(revised) == 66,
        "card_split_16_3_6": cc == {"FULL_COMPOSITION": 16, "PARTIAL_COMPOSITION": 3, "LEARNED_WHOLE_OPERATION": 6},
        "event_split_18_4_6": ec == {"FULL_COMPOSITION": 18, "PARTIAL_COMPOSITION": 4, "LEARNED_WHOLE_OPERATION": 6},
        "all_revised_values_concrete": all(r["revised_default_de"].strip() for r in revised),
        "all_25_mapped_once": len({r["master_card_id"] for r in cards}) == 25,
        "expected_whole_six": {r["master_card_id"] for r in cards if r["composition_status"] == "LEARNED_WHOLE_OPERATION"} == {"MC037", "MC068", "MC099", "MC100", "MC129", "MC156"},
        "only_fixed_herbal_pages": {r["page"] for r in occurrences} <= {"f10r", "f11r", "f55v", "f56r"},
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
