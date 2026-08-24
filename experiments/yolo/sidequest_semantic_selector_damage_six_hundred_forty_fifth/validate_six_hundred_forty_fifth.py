#!/usr/bin/env python3
"""Validate selector-damage reconstruction across five case templates."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    damaged = read("SIX_HUNDRED_FORTY_FIFTH_10_DAMAGED_FRAGMENTS.tsv")
    scores = read("SIX_HUNDRED_FORTY_FIFTH_50_TEMPLATE_SCORES.tsv")
    recon = read("SIX_HUNDRED_FORTY_FIFTH_10_RECONSTRUCTIONS.tsv")
    cases = {"C1", "C2", "C3", "C4", "C5"}
    checks = {
        "ten_fragments": len(damaged) == 10 and all(sum(row["intended_case"] == case for row in damaged) == 2 for case in cases),
        "fifty_scores": len(scores) == 50 and all(sum(row["damage_id"] == damage["damage_id"] for row in scores) == 5 for damage in damaged),
        "ten_reconstructions": len(recon) == 10,
        "primary_and_full_each_case": all({row["damage_kind"] for row in damaged if row["intended_case"] == case} == {"PRIMARY_CUE_REMOVED", "FULL_CUE_FAMILY_REMOVED"} for case in cases),
        "old_selector_mostly_broken": sum(row["old_selector_correct"] == "YES" for row in damaged) <= 1,
        "all_unique_template_recovery": all(row["unique_best_template"] == "YES" and row["exact_case_recovery"] == "YES" for row in recon),
        "all_full_family_recovered": all(row["exact_case_recovery"] == "YES" for row in recon if row["damage_kind"] == "FULL_CUE_FAMILY_REMOVED"),
        "expected_template_complete_fit": all(next(score for score in scores if score["damage_id"] == row["damage_id"] and score["candidate_case"] == row["intended_case"])["complete_subset_fit"] == "YES" for row in recon),
        "no_owner_needed": all(row["visible_owner_or_margin_required"] == "NO" for row in recon),
        "template_dependency_explicit": all(row["case_template_required"] == "YES" for row in recon),
        "three_card_hard_cases_present": sum(int(row["remaining_cards"]) == 3 for row in recon) == 2,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_FORTY_FIFTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
