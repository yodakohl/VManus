#!/usr/bin/env python3
"""Validate the finite five-job construction grammar."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    edges = read("SIX_HUNDRED_THIRTY_THIRD_25_PRECEDENCE_RULES.tsv")
    orders = read("SIX_HUNDRED_THIRTY_THIRD_22_LEGAL_ORDERS.tsv")
    backward = read("SIX_HUNDRED_THIRTY_THIRD_132_STEP_BACKWARD_READ.tsv")
    bigrams = read("SIX_HUNDRED_THIRTY_THIRD_110_BIGRAM_AUDIT.tsv")
    expected = {"C1": 8, "C2": 5, "C3": 6, "C4": 1, "C5": 2}
    checks = {
        "twenty_five_edges": len(edges) == 25 and all(sum(row["case_id"] == case for row in edges) == 5 for case in expected),
        "twenty_two_orders": len(orders) == 22,
        "expected_case_capacity": {case: sum(row["case_id"] == case for row in orders) for case in expected} == expected,
        "unique_orders": len({row["surface_sequence"] for row in orders}) == 22,
        "all_edges_satisfied": all(row["all_precedence_edges_satisfied"] == "YES" for row in orders),
        "all_select_correctly": all(row["selector_correct"] == "YES" and row["selected_case_id"] == row["case_id"] for row in orders),
        "five_pass631_orders": sum(row["is_pass631_order"] == "YES" for row in orders) == 5,
        "eleven_pass632_orders": sum(row["was_licensed_in_pass632"] == "YES" for row in orders) == 11,
        "eleven_additional_orders": sum(row["was_licensed_in_pass632"] == "NO" for row in orders) == 11,
        "all_orders_source_new": all(row["source_sequence_occurrences"] == "0" for row in orders),
        "one_hundred_thirty_two_steps": len(backward) == 132,
        "all_backward_exact": all(row["exact_backward_read"] == "YES" for row in backward),
        "one_hundred_ten_bigrams": len(bigrams) == 110,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_THIRTY_THIRD_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
