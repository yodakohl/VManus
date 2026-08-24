#!/usr/bin/env python3
"""Validate five new branch-specific apprentice orders."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    steps = read("SIX_HUNDRED_THIRTY_FIRST_30_STEP_FIVE_BRANCH_ORDERS.tsv")
    orders = read("SIX_HUNDRED_THIRTY_FIRST_5_ORDER_SUMMARY.tsv")
    backward = read("SIX_HUNDRED_THIRTY_FIRST_30_STEP_BACKWARD_READ.tsv")
    bigrams = read("SIX_HUNDRED_THIRTY_FIRST_25_BIGRAM_NOVELTY_AUDIT.tsv")
    checks = {
        "five_orders": len(orders) == 5 and {row["intended_case_id"] for row in orders} == {f"C{i}" for i in range(1, 6)},
        "thirty_steps": len(steps) == 30 and len(backward) == 30,
        "six_steps_each": all(sum(row["case_id"] == case for row in steps) == 6 for case in {f"C{i}" for i in range(1, 6)}),
        "all_select_correctly": all(row["selector_correct"] == "YES" and row["intended_case_id"] == row["selected_case_id"] for row in orders),
        "all_orders_new": all(row["full_sequence_source_occurrences"] == "0" for row in orders),
        "all_surfaces_unique": all(row["surface_card_candidate_count"] == "1" for row in steps),
        "no_new_inventory": all(row["new_word"] == row["new_card"] == row["new_surface"] == "NO" for row in steps),
        "all_backward_exact": all(row["exact_backward_read"] == "YES" for row in backward),
        "twenty_five_bigrams": len(bigrams) == 25,
        "some_novel_bigrams": sum(row["source_occurrences"] == "0" for row in bigrams) >= 15,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_THIRTY_FIRST_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
