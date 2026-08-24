#!/usr/bin/env python3
"""Validate minimal mixed correction and hand preservation."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    positions = read("SIX_HUNDRED_FORTY_SECOND_6_POSITION_MIXED_AUDIT.tsv")
    stages = read("SIX_HUNDRED_FORTY_SECOND_4_STAGE_CORRECTION_TRACE.tsv")
    policies = read("SIX_HUNDRED_FORTY_SECOND_4_POLICY_MINIMALITY.tsv")
    selected = next(row for row in policies if row["selected"] == "YES")
    checks = {
        "six_positions": len(positions) == 6,
        "four_stages": [row["stage"] for row in stages] == ["MASTER_EXPECTATION", "APPRENTICE_MIXED_COPY", "ORDER_REPAIRED", "MINIMAL_SEMANTIC_CORRECTION"],
        "one_harmless_foreign_hand": sum(row["diagnosis"] == "HARMLESS_FOREIGN_HAND" for row in positions) == 1,
        "foreign_hand_not_rewritten": positions[0]["apprentice_surface"] == "okaiin" and positions[0]["corrected_surface"] == "okaiin" and positions[0]["surface_changed_by_master"] == "NO",
        "wrong_order_repaired": stages[2]["operation_from_previous"] == "SWAP_POSITIONS_3_AND_4",
        "wrong_card_repaired": stages[3]["operation_from_previous"] == "REPLACE_POSITION_5_SHEY_WITH_TSHEY",
        "final_cards_equal_master": stages[3]["card_strip"] == stages[0]["card_strip"],
        "final_surface_differs_from_master": stages[3]["surface_strip"] != stages[0]["surface_strip"],
        "semantic_sequence_restored": stages[1]["semantic_sequence_correct"] == "NO" and stages[3]["semantic_sequence_correct"] == "YES",
        "minimal_policy_selected": selected["policy"] == "MINIMAL_SEMANTIC_CORRECTION" and selected["harmless_allographs_erased"] == "0",
        "partial_repairs_fail": all(row["semantic_sequence_correct"] == "NO" for row in policies if row["policy"] in {"FIX_CARD_ONLY", "FIX_ORDER_ONLY"}),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_FORTY_SECOND_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
