#!/usr/bin/env python3
"""Validate branch-cue mobility exercises."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    variants = read("SIX_HUNDRED_THIRTY_SECOND_25_CUE_POSITION_VARIANTS.tsv")
    backward = read("SIX_HUNDRED_THIRTY_SECOND_150_STEP_BACKWARD_READ.tsv")
    cases = read("SIX_HUNDRED_THIRTY_SECOND_5_CUE_MOBILITY_SUMMARY.tsv")
    expected_positions = {"C1": "1|2", "C2": "1|2|3|4|5", "C3": "1", "C4": "3", "C5": "1|2"}
    checks = {
        "twenty_five_variants": len(variants) == 25,
        "five_positions_per_case": all(sum(row["case_id"] == case for row in variants) == 5 for case in expected_positions),
        "all_select_correctly": all(row["selector_correct"] == "YES" and row["selected_case_id"] == row["case_id"] for row in variants),
        "eleven_licensed": sum(row["semantic_order_licensed"] == "YES" for row in variants) == 11,
        "six_new_licensed": sum(row["semantic_order_licensed"] == "YES" and row["is_original_631_order"] == "NO" for row in variants) == 6,
        "expected_license_positions": {row["case_id"]: row["licensed_positions"] for row in cases} == expected_positions,
        "all_sequences_source_new": all(row["source_sequence_occurrences"] == "0" for row in variants),
        "all_surfaces_unique": all(row["all_surfaces_unique_to_card"] == "YES" for row in variants),
        "one_hundred_fifty_steps": len(backward) == 150,
        "all_backward_exact": all(row["exact_backward_read"] == "YES" for row in backward),
        "five_case_summaries": len(cases) == 5,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_THIRTY_SECOND_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
