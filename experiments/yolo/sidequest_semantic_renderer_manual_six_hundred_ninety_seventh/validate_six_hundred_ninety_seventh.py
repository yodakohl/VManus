#!/usr/bin/env python3
"""Validate the seven-rule renderer manual."""

from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python3", str(HERE / "build_six_hundred_ninety_seventh.py")], check=True)
    plans = read("SIX_HUNDRED_NINETY_SEVENTH_230_RENDERER_PLANS.tsv")
    rules = read("SIX_HUNDRED_NINETY_SEVENTH_7_RENDERER_RULES.tsv")
    patterns = read("SIX_HUNDRED_NINETY_SEVENTH_BOUNDARY_PATTERNS.tsv")
    repairs = read("SIX_HUNDRED_NINETY_SEVENTH_CHK_FRAGMENT_REPAIR.tsv")
    families = Counter(int(row["rule_families_used"]) for row in plans)
    rule_counts = {row["rule_id"]: int(row["observed_gap_chunks"]) for row in rules}
    checks = {
        "two_thirty_plans": len(plans) == 230,
        "seven_rules": len(rules) == 7,
        "family_distribution": families == Counter({1: 129, 0: 80, 2: 21}),
        "no_three_rule_forms": not any(int(row["rule_families_used"]) > 2 for row in plans),
        "one_seventy_one_chunks": sum(int(row["observed_gap_chunks"]) for row in rules) == 171,
        "rule_counts": rule_counts == {"ENTRY_FRAME": 110, "CHD_JOINT": 22, "ITEM_CONTINUATION_CARRIER": 14, "ADDRESS_HINGE": 11, "TRANSFER_LINKER": 7, "IIN_STRETCH": 4, "TERMINAL_ECHO": 3},
        "patterns_cover_chunks": sum(int(row["surface_forms"]) for row in patterns) == 171,
        "chk_two_repairs": len(repairs) == 2 and {row["surface"] for row in repairs} == {"chkeey", "chkeedy"},
        "all_exact_reconstructions": all(row["exact_reconstruction"] == "YES" for row in plans),
        "no_empty_instructions": all(row["instruction_de"] for row in rules),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "passed": sum(checks.values()), "total": len(checks)}
    (HERE / "SIX_HUNDRED_NINETY_SEVENTH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
