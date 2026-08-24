#!/usr/bin/env python3
"""Validate the three-desk allographic rendering exercise."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    rendering = read("SIX_HUNDRED_FORTIETH_18_STEP_THREE_DESK_RENDERING.tsv")
    comparison = read("SIX_HUNDRED_FORTIETH_6_CARD_ALLOGRAPH_COMPARISON.tsv")
    strips = read("SIX_HUNDRED_FORTIETH_3_DESK_STRIPS.tsv")
    expected_cards = "PROC038|PROC048|PROC028|PROC030|PROC122|PROC078"
    checks = {
        "three_desks": len(strips) == 3 and len({row["desk"] for row in strips}) == 3,
        "eighteen_steps": len(rendering) == 18,
        "six_comparison_cards": len(comparison) == 6,
        "six_steps_each": all(sum(row["desk"] == desk for row in rendering) == 6 for desk in {row["desk"] for row in strips}),
        "same_card_strip": all(row["card_strip"] == expected_cards for row in strips),
        "three_distinct_surface_strips": len({row["surface_strip"] for row in strips}) == 3,
        "all_surfaces_licensed": all(row["surface_is_licensed"] == "YES" for row in rendering),
        "all_surfaces_unique_to_cards": all(row["surface_uniquely_backreads_to_card"] == "YES" for row in rendering),
        "all_backreads_exact": all(row["backread_card_no"] == row["card_no"] and row["backread_meaning_unchanged"] == "YES" for row in rendering),
        "meaning_invariant": all(row["meaning_changes"] == "NO" and row["all_surfaces_same_card"] == "YES" for row in comparison),
        "allography_present": sum(int(row["distinct_surfaces"]) > 1 for row in comparison) >= 2,
        "stable_travel_cards": sum(int(row["distinct_surfaces"]) == 1 for row in comparison) >= 3,
        "no_new_inventory": all(set(row["surface"].split("|")) <= set(row["licensed_surfaces"].split("|")) for row in rendering),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_FORTIETH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
