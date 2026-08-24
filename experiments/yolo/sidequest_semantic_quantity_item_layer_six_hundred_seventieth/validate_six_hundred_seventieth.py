#!/usr/bin/env python3
"""Validate the quantity, selection, and active-item layer."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    cards = read("SIX_HUNDRED_SEVENTIETH_88_QUANTITY_ITEM_CARDS.tsv")
    events = read("SIX_HUNDRED_SEVENTIETH_195_QUANTITY_ITEM_EVENTS.tsv")
    roots = read("SIX_HUNDRED_SEVENTIETH_6_ROOT_SUMMARY.tsv")
    contrasts = read("SIX_HUNDRED_SEVENTIETH_5_MINIMAL_CONTRASTS.tsv")
    remaining = read("SIX_HUNDRED_SEVENTIETH_6_REMAINING_CARDS.tsv")
    expected = {"AIN": (8, 18), "AIIN": (10, 39), "IIN": (3, 4), "K": (18, 21), "HO": (5, 8), "Y": (60, 124)}
    checks = {
        "eighty_eight_union_cards": len(cards) == 88,
        "one_hundred_ninety_five_union_events": len(events) == 195,
        "six_roots": len(roots) == 6 and {row["root"] for row in roots} == set(expected),
        "raw_root_counts": all((int(row["card_types"]), int(row["events"])) == expected[row["root"]] for row in roots),
        "five_contrasts": len(contrasts) == 5,
        "all_selected_events_unique": len({row["event_id"] for row in events}) == 195,
        "all_cards_have_contribution": all(row["selected_roots"] and row["portable_contributions_de"] for row in cards),
        "six_remaining_cards": len(remaining) == 6,
        "seven_remaining_events": sum(int(row["events"]) for row in remaining) == 7,
        "expected_remaining_ids": {row["card_no"] for row in remaining} == {"PROC005", "PROC032", "PROC034", "PROC041", "PROC043", "PROC124"},
        "ain_aiin_iin_distinct": len({next(row for row in roots if row["root"] == root)["portable_value_de"] for root in ["AIN", "AIIN", "IIN"]}) == 3,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_SEVENTIETH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, passed in checks.items():
        print(f"{name}\t{'PASS' if passed else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
