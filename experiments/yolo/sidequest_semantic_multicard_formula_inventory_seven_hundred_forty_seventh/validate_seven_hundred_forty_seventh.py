#!/usr/bin/env python3
"""Validate Pass 747 recurring formula inventory."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    formulas = read("SEVEN_HUNDRED_FORTY_SEVENTH_14_FORMULA_INVENTORY.tsv")
    occurrences = read("SEVEN_HUNDRED_FORTY_SEVENTH_32_FORMULA_OCCURRENCES.tsv")
    coverage = read("SEVEN_HUNDRED_FORTY_SEVENTH_32_RESIDUAL_FORMULA_COVERAGE.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_FORTY_SEVENTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    lookup = {row["cards"]: row for row in formulas}
    checks = {
        "inventory_14_occurrences_32_coverage_32": (len(formulas), len(occurrences), len(coverage)) == (14, 32, 32),
        "twelve_bigrams_two_trigrams": (sum(row["card_length"] == "2" for row in formulas), sum(row["card_length"] == "3" for row in formulas)) == (12, 2),
        "all_recur_in_two_statements": all(int(row["residual_statements"]) >= 2 for row in formulas),
        "measured_item_bracket_exact": lookup["Y | AIIN | Y"]["residual_statement_ids"] == "B3-S003,H2-S001",
        "staged_activation_exact": lookup["OK+EE+Y | OK+Y | OL"]["residual_statement_ids"] == "B2-S010,B4-S003",
        "covered_18": sum(row["used_formula_ids"] != "NONE" for row in coverage) == 18,
        "teaching_compression_205_to_181": (sum(int(row["observed_cards"]) for row in coverage), sum(int(row["formula_units"]) for row in coverage)) == (205, 181),
        "saved_24": sum(int(row["saved_teaching_units"]) for row in coverage) == 24,
        "twelve_active_two_overlapped": (sum(row["greedy_status"] == "ACTIVE_MACRO" for row in formulas), sum(row["greedy_status"] == "OVERLAPPED_FRAGMENT_ONLY" for row in formulas)) == (12, 2),
        "fixed_pages_only": {row["page"] for row in occurrences} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_pages_absent": all("f84" not in "\t".join(row.values()).lower() for rows in (formulas, occurrences, coverage) for row in rows),
        "no_semantic_or_deck_change": summary["semantic_changes"] == 0 and summary["deck_changes"] == 0,
        "summary_pass": summary["status"] == "PASS",
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_FORTY_SEVENTH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
