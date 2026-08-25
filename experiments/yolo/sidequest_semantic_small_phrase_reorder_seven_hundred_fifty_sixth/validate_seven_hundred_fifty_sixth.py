#!/usr/bin/env python3
"""Validate Pass 756 small phrase reorderings."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    rules = read("SEVEN_HUNDRED_FIFTY_SIXTH_3_SMALL_PHRASE_RULES.tsv")
    occurrences = read("SEVEN_HUNDRED_FIFTY_SIXTH_3_TRIGGER_OCCURRENCES.tsv")
    audit = read("SEVEN_HUNDRED_FIFTY_SIXTH_116_PACKING_AUDIT.tsv")
    fixed = read("SEVEN_HUNDRED_FIFTY_SIXTH_3_NEWLY_FIXED.tsv")
    residual = read("SEVEN_HUNDRED_FIFTY_SIXTH_7_LARGE_FORMULA_RESIDUALS.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_FIFTY_SIXTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "counts_3_3_116_3_7": (len(rules), len(occurrences), len(audit), len(fixed), len(residual)) == (3, 3, 116, 3, 7),
        "one_trigger_each": all(row["trigger_count"] == "1" for row in rules),
        "all_fix_no_harm": all((row["newly_fixed"], row["newly_harmed"], row["retain_rule"]) == ("1", "0", "YES") for row in rules),
        "fixed_ids": {row["statement_id"] for row in fixed} == {"H4-S001", "H5-S003", "B3-S032"},
        "residual_ids": {row["statement_id"] for row in residual} == {"H1-S001", "H2-S001", "H3-S001", "H5-S001", "B1-S002", "B3-S021", "B6-S001"},
        "exact_106_to_109": (sum(row["baseline_exact"] == "YES" for row in audit), sum(row["candidate_exact"] == "YES" for row in audit)) == (106, 109),
        "equal_stays_109": (sum(int(row["baseline_cards"]) == int(row["observed_cards"]) for row in audit), sum(int(row["candidate_cards"]) == int(row["observed_cards"]) for row in audit)) == (109, 109),
        "cards_stay_365_of_381": (sum(int(row["baseline_cards"]) for row in audit), sum(int(row["candidate_cards"]) for row in audit), sum(int(row["observed_cards"]) for row in audit)) == (365, 365, 381),
        "no_harms": all(row["newly_harmed"] == "NO" for row in audit),
        "fixed_pages_only": {row["page"] for row in audit} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_pages_absent": all("f84" not in "\t".join(row.values()).lower() for rows in (rules, occurrences, audit, fixed, residual) for row in rows),
        "no_semantic_or_deck_change": summary["semantic_changes"] == 0 and summary["deck_changes"] == 0,
        "summary_pass": summary["status"] == "PASS",
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_FIFTY_SIXTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
