#!/usr/bin/env python3
"""Validate five-case surface/card/order correction school."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    cases = read("SIX_HUNDRED_FORTY_THIRD_5_CASE_CORRECTION_SUMMARY.tsv")
    positions = read("SIX_HUNDRED_FORTY_THIRD_30_POSITION_AUDIT.tsv")
    stages = read("SIX_HUNDRED_FORTY_THIRD_20_STAGE_TRACES.tsv")
    case_ids = {"C1", "C2", "C3", "C4", "C5"}
    checks = {
        "five_cases": len(cases) == 5 and {row["case_id"] for row in cases} == case_ids,
        "thirty_positions": len(positions) == 30 and all(sum(row["case_id"] == case for row in positions) == 6 for case in case_ids),
        "twenty_stages": len(stages) == 20 and all(sum(row["case_id"] == case for row in stages) == 4 for case in case_ids),
        "all_allographs_same_card": all(row["allograph_same_card"] == "YES" for row in cases),
        "five_distinct_wrong_cards": all(row["wrong_card_no"] != row["expected_card_no"] for row in cases) and len({row["wrong_card_change"] for row in cases}) == 5,
        "each_breaks_precedence": all(int(row["violated_precedence_rules"]) >= 1 and row["violated_rule"] for row in cases),
        "all_final_cards_restored": all(row["final_cards_equal_master"] == "YES" for row in cases),
        "all_foreign_hands_preserved": all(row["foreign_hand_preserved"] == "YES" for row in cases),
        "one_each_defect_per_case": all(sum(row["case_id"] == case and row["defect_class"] == "HARMLESS_ALLOGRAPH" for row in positions) == 1 and sum(row["case_id"] == case and row["defect_class"] == "WRONG_EXACT_CARD" for row in positions) == 1 and sum(row["case_id"] == case and row["defect_class"] == "ORDER_SWAP_MEMBER" for row in positions) == 2 for case in case_ids),
        "only_final_and_master_correct": all([row["semantic_sequence_correct"] for row in stages if row["case_id"] == case] == ["YES", "NO", "NO", "YES"] for case in case_ids),
        "no_normalization": all(row["unnecessary_normalizations"] == "0" for row in cases),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_FORTY_THIRD_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
