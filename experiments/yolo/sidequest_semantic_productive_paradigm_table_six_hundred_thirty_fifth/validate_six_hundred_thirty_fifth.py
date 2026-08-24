#!/usr/bin/env python3
"""Validate the compact productive-paradigm table."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    cells = read("SIX_HUNDRED_THIRTY_FIFTH_20_ATTESTED_PARADIGM_CELLS.tsv")
    cards = read("SIX_HUNDRED_THIRTY_FIFTH_22_EXACT_CARD_MEMBERS.tsv")
    gaps = read("SIX_HUNDRED_THIRTY_FIFTH_6_PREDICTED_GAPS.tsv")
    expected = {"OK_GRADE_ENDPOINT": 5, "SH_GRADE_ENDPOINT": 4, "SOLK_GRADE_ENDPOINT": 3, "CHK_GRADE_ENDPOINT": 3, "OT_GRADE_ENDPOINT": 3, "OK_QUANTITY": 2}
    checks = {
        "six_families_twenty_cells": len(cells) == 20 and {family: sum(row["family_id"] == family for row in cells) for family in expected} == expected,
        "all_cells_attested": all(int(row["exact_card_count"]) >= 1 and row["exact_card_nos"] and row["surfaces"] for row in cells),
        "twenty_two_exact_cards": len(cards) == 22 and len({row["card_no"] for row in cards}) == 22,
        "member_counts_match": sum(int(row["exact_card_count"]) for row in cells) == len(cards),
        "all_members_fit": all(row["one_dimension_fit"] == "YES" for row in cards),
        "six_predicted_gaps": len(gaps) == 6,
        "gaps_absent_from_deck": all(row["candidate_surface_hits_in_173_card_deck"] == "NONE" and row["status"] == "PREDICTED_GAP_NOT_NEW_CARD" for row in gaps),
        "quantity_pair_present": {row["semantic_component_parse"] for row in cells if row["family_id"] == "OK_QUANTITY"} == {"OK+AIN", "OK+AIIN"},
        "full_grade_only_closed": all(row["endpoint"] == "DY" for row in cells if row["modifier"] == "EEE"),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_THIRTY_FIFTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
