#!/usr/bin/env python3
"""Validate one-slot compatible substitutions."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    jobs = read("SIX_HUNDRED_THIRTY_FOURTH_11_JOB_SUBSTITUTIONS.tsv")
    orders = read("SIX_HUNDRED_THIRTY_FOURTH_49_LEGAL_WRITTEN_ORDERS.tsv")
    backward = read("SIX_HUNDRED_THIRTY_FOURTH_294_STEP_BACKWARD_READ.tsv")
    expected_orders = {"C1": 16, "C2": 15, "C3": 12, "C4": 2, "C5": 4}
    checks = {
        "eleven_jobs": len(jobs) == 11,
        "five_base_six_new": sum(row["variant_kind"] == "BASE" for row in jobs) == 5 and sum(row["variant_kind"] == "SUBSTITUTED" for row in jobs) == 6,
        "one_slot_per_case": {row["case_id"]: row["slot_function"] for row in jobs} == {"C1": "HOLD_GRADE", "C2": "CLOSE_GRADE", "C3": "HOLD_GRADE", "C4": "QUANTITY", "C5": "QUANTITY"},
        "all_replacements_existing_unique": all(row["existing_word"] == row["existing_card"] == row["existing_surface"] == "YES" and row["replacement_surface_card_candidates"] == "1" for row in jobs),
        "forty_nine_orders": len(orders) == 49,
        "expected_case_orders": {case: sum(row["case_id"] == case for row in orders) for case in expected_orders} == expected_orders,
        "unique_written_orders": len({row["surface_sequence"] for row in orders}) == 49,
        "all_select_correctly": all(row["selector_correct"] == "YES" and row["selected_case_id"] == row["case_id"] for row in orders),
        "all_surfaces_unique": all(row["all_surfaces_unique_to_card"] == "YES" for row in orders),
        "all_orders_source_new": all(row["source_sequence_occurrences"] == "0" for row in orders),
        "two_hundred_ninety_four_steps": len(backward) == 294,
        "all_backward_exact": all(row["exact_backward_read"] == "YES" for row in backward),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_THIRTY_FOURTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
