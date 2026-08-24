#!/usr/bin/env python3
"""Validate surface/card/order error separation."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    diagnostics = read("SIX_HUNDRED_FORTY_FIRST_4_STRIP_DIAGNOSTICS.tsv")
    positions = read("SIX_HUNDRED_FORTY_FIRST_24_POSITION_AUDIT.tsv")
    by_id = {row["variant"]: row for row in diagnostics}
    checks = {
        "four_variants": len(diagnostics) == 4,
        "twenty_four_positions": len(positions) == 24,
        "all_known_surfaces": all(row["all_surfaces_known"] == "YES" for row in diagnostics),
        "master_unchanged": by_id["MASTER"]["error_class"] == "NONE" and by_id["MASTER"]["correction_action"] == "ACCEPT",
        "allograph_same_cards": by_id["HARMLESS_ALLOGRAPH"]["error_class"] == "SURFACE_ONLY_ALLOGRAPHY" and by_id["HARMLESS_ALLOGRAPH"]["exact_card_sequence_preserved"] == "YES",
        "allograph_accepted": by_id["HARMLESS_ALLOGRAPH"]["correction_action"] == "ACCEPT_ALLOGRAPH",
        "lookalike_changes_card": by_id["WRONG_CARD_LOOKALIKE"]["error_class"] == "EXACT_CARD_SUBSTITUTION" and by_id["WRONG_CARD_LOOKALIKE"]["cards_changed"] == "1",
        "lookalike_short_to_long": any(row["variant"] == "WRONG_CARD_LOOKALIKE" and row["expected_surface"] == "tshey" and row["actual_surface"] == "shey" and row["same_exact_card"] == "NO" for row in positions),
        "order_keeps_multiset": by_id["WRONG_PROCESS_ORDER"]["error_class"] == "PROCESS_ORDER_ERROR" and by_id["WRONG_PROCESS_ORDER"]["exact_card_multiset_preserved"] == "YES",
        "order_changes_two_positions": by_id["WRONG_PROCESS_ORDER"]["positions_changed"] == "2",
        "three_distinct_actions": len({by_id[name]["correction_action"] for name in ["HARMLESS_ALLOGRAPH", "WRONG_CARD_LOOKALIKE", "WRONG_PROCESS_ORDER"]}) == 3,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_FORTY_FIRST_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
