#!/usr/bin/env python3
"""Validate complementary-copy collation across C1-C5."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    copies = read("SIX_HUNDRED_FORTY_FOURTH_10_COMPLEMENTARY_COPIES.tsv")
    collations = read("SIX_HUNDRED_FORTY_FOURTH_5_COLLATIONS.tsv")
    provenance = read("SIX_HUNDRED_FORTY_FOURTH_30_CARD_PROVENANCE.tsv")
    cases = {"C1", "C2", "C3", "C4", "C5"}
    checks = {
        "ten_copies": len(copies) == 10 and all(sum(row["case_id"] == case for row in copies) == 2 for case in cases),
        "five_collations": len(collations) == 5 and {row["case_id"] for row in collations} == cases,
        "thirty_provenance_positions": len(provenance) == 30,
        "both_copies_select_case": all(row["case_selected"] == row["case_id"] for row in copies),
        "a_order_correct_inventory_wrong": all(row["card_order_equals_hidden_master"] == "NO" and row["card_multiset_equals_hidden_master"] == "NO" for row in copies if row["copy_id"] == "COPY_A_ORDER_WITNESS"),
        "b_inventory_correct_order_wrong": all(row["card_multiset_equals_hidden_master"] == "YES" and row["card_order_equals_hidden_master"] == "NO" for row in copies if row["copy_id"] == "COPY_B_INVENTORY_WITNESS"),
        "one_missing_one_extra": all(row["extra_card_in_copy_a"] != "UNRESOLVED" and row["missing_card_from_copy_a"] != "UNRESOLVED" and row["extra_card_in_copy_a"] != row["missing_card_from_copy_a"] for row in collations),
        "all_exact_recovery": all(row["exact_card_recovery"] == "YES" and row["collated_card_strip"] == row["hidden_master_card_strip"] for row in collations),
        "all_foreign_hands_preserved": all(row["foreign_hand_preserved"] == "YES" for row in collations),
        "no_visible_master": all(row["master_strip_visible_to_collator"] == "NO" for row in copies) and all(row["visible_master_used"] == "NO" for row in collations),
        "five_donor_cards": sum(row["source_copy"] == "COPY_B_INVENTORY_WITNESS" for row in provenance) == 5,
        "all_positions_match": all(row["matches_hidden_master_card"] == "YES" for row in provenance),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_FORTY_FOURTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
