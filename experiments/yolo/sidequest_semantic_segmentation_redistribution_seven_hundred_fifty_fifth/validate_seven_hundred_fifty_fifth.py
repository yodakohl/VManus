#!/usr/bin/env python3
"""Validate Pass 755 segmentation/redistribution."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    rules = read("SEVEN_HUNDRED_FIFTY_FIFTH_2_REDISTRIBUTION_RULES.tsv")
    occurrences = read("SEVEN_HUNDRED_FIFTY_FIFTH_2_TRIGGER_OCCURRENCES.tsv")
    audit = read("SEVEN_HUNDRED_FIFTY_FIFTH_116_PACKING_AUDIT.tsv")
    fixed = read("SEVEN_HUNDRED_FIFTY_FIFTH_2_NEWLY_FIXED.tsv")
    residual = read("SEVEN_HUNDRED_FIFTY_FIFTH_10_RESIDUAL_ERRORS.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_FIFTY_FIFTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "counts_2_2_116_2_10": (len(rules), len(occurrences), len(audit), len(fixed), len(residual)) == (2, 2, 116, 2, 10),
        "one_trigger_each": all(row["trigger_count"] == "1" for row in rules),
        "all_fix_no_harm": all((row["newly_fixed"], row["newly_harmed"], row["retain_rule"]) == ("1", "0", "YES") for row in rules),
        "fixed_ids": {row["statement_id"] for row in fixed} == {"B1-S006", "B4-S002"},
        "b1_component_delta_none": next(row for row in occurrences if row["statement_id"] == "B1-S006")["component_delta"] == "NONE",
        "b4_component_delta_y": next(row for row in occurrences if row["statement_id"] == "B4-S002")["component_delta"] == "Y",
        "exact_104_to_106": (sum(row["baseline_exact"] == "YES" for row in audit), sum(row["candidate_exact"] == "YES" for row in audit)) == (104, 106),
        "equal_108_to_109": (sum(int(row["baseline_cards"]) == int(row["observed_cards"]) for row in audit), sum(int(row["candidate_cards"]) == int(row["observed_cards"]) for row in audit)) == (108, 109),
        "cards_364_to_365_of_381": (sum(int(row["baseline_cards"]) for row in audit), sum(int(row["candidate_cards"]) for row in audit), sum(int(row["observed_cards"]) for row in audit)) == (364, 365, 381),
        "no_harms": all(row["newly_harmed"] == "NO" for row in audit),
        "fixed_pages_only": {row["page"] for row in audit} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_pages_absent": all("f84" not in "\t".join(row.values()).lower() for rows in (rules, occurrences, audit, fixed, residual) for row in rows),
        "no_semantic_or_deck_change": summary["semantic_changes"] == 0 and summary["deck_changes"] == 0,
        "summary_pass": summary["status"] == "PASS",
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_FIFTY_FIFTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
