#!/usr/bin/env python3
"""Validate Pass 748 context-bound formula completion."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    rules = read("SEVEN_HUNDRED_FORTY_EIGHTH_3_CONTEXT_RULES.tsv")
    audit = read("SEVEN_HUNDRED_FORTY_EIGHTH_116_FORMULA_PACKING_AUDIT.tsv")
    fixed = read("SEVEN_HUNDRED_FORTY_EIGHTH_3_NEWLY_FIXED.tsv")
    residual = read("SEVEN_HUNDRED_FORTY_EIGHTH_29_RESIDUAL_ERRORS.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_FORTY_EIGHTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "counts_3_116_3_29": (len(rules), len(audit), len(fixed), len(residual)) == (3, 116, 3, 29),
        "one_trigger_each": all(row["trigger_count"] == "1" for row in rules),
        "all_rules_fix_without_harm": all((row["newly_fixed"], row["newly_harmed"], row["retain_rule"]) == ("1", "0", "YES") for row in rules),
        "fixed_ids_exact": {row["statement_id"] for row in fixed} == {"B3-S003", "B2-S010", "B4-S003"},
        "exact_84_to_87": (sum(row["baseline_exact"] == "YES" for row in audit), sum(row["formula_exact"] == "YES" for row in audit)) == (84, 87),
        "equal_count_95_to_98": (sum(int(row["baseline_cards"]) == int(row["observed_cards"]) for row in audit), sum(int(row["formula_cards"]) == int(row["observed_cards"]) for row in audit)) == (95, 98),
        "cards_345_to_348_of_381": (sum(int(row["baseline_cards"]) for row in audit), sum(int(row["formula_cards"]) for row in audit), sum(int(row["observed_cards"]) for row in audit)) == (345, 348, 381),
        "no_harms": all(row["newly_harmed"] == "NO" for row in audit),
        "fixed_pages_only": {row["page"] for row in audit} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_pages_absent": all("f84" not in "\t".join(row.values()).lower() for rows in (rules, audit, fixed, residual) for row in rows),
        "no_semantic_or_deck_change": summary["semantic_changes"] == 0 and summary["deck_changes"] == 0,
        "summary_pass": summary["status"] == "PASS",
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_FORTY_EIGHTH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
