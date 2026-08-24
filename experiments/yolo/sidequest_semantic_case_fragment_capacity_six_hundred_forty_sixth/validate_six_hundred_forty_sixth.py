#!/usr/bin/env python3
"""Validate exhaustive five-case ordered-fragment capacity."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    fragments = read("SIX_HUNDRED_FORTY_SIXTH_315_ORDERED_FRAGMENTS.tsv")
    ambiguous = read("SIX_HUNDRED_FORTY_SIXTH_AMBIGUOUS_FRAGMENTS.tsv")
    thresholds = read("SIX_HUNDRED_FORTY_SIXTH_5_CASE_THRESHOLDS.tsv")
    signatures = read("SIX_HUNDRED_FORTY_SIXTH_SIGNATURE_CARDS.tsv")
    sizes = read("SIX_HUNDRED_FORTY_SIXTH_30_SIZE_COUNTS.tsv")
    threshold_map = {row["case_id"]: int(row["worst_case_guaranteed_survivors"]) for row in thresholds}
    checks = {
        "three_hundred_fifteen_fragments": len(fragments) == 315,
        "sixty_three_each_case": all(sum(row["source_case"] == case for row in fragments) == 63 for case in {"C1", "C2", "C3", "C4", "C5"}),
        "thirty_size_rows": len(sizes) == 30,
        "all_full_sequences_unique": all(row["unique_case_recovery"] == "YES" for row in fragments if row["surviving_cards"] == "6"),
        "thresholds_expected": threshold_map == {"C1": 5, "C2": 2, "C3": 5, "C4": 3, "C5": 3},
        "seventeen_signature_cards": len(signatures) == 17 and all(row["single_card_identifies_case"] == "YES" for row in signatures),
        "ambiguous_rows_match": len(ambiguous) == sum(row["unique_case_recovery"] == "NO" for row in fragments),
        "largest_ambiguous_size_four": max(int(row["surviving_cards"]) for row in ambiguous) == 4,
        "shared_c1_c3_backbone": any(row["surface_fragment"] == "qokaiin qokal shey shedy" and set(row["matching_cases"].split("|")) == {"C1", "C3"} for row in ambiguous),
        "owner_needed_only_when_ambiguous": all((row["owner_or_margin_needed"] == "YES") == (row["unique_case_recovery"] == "NO") for row in fragments),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_FORTY_SIXTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
