#!/usr/bin/env python3
"""Validate the complete SH hold grid."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    cards = read("SIX_HUNDRED_SIXTY_SEVENTH_20_SH_CARDS.tsv")
    events = read("SIX_HUNDRED_SIXTY_SEVENTH_25_SH_EVENT_CONTEXTS.tsv")
    grid = read("SIX_HUNDRED_SIXTY_SEVENTH_8_HOLD_GRID_CELLS.tsv")
    checks = {
        "twenty_cards": len(cards) == 20,
        "twenty_five_events": len(events) == 25 and sum(int(row["events"]) for row in cards) == 25,
        "nineteen_recipes": len({row["component_recipe"] for row in cards}) == 19,
        "invariant_hold": all(row["portable_sh_value_de"] == "HALTEN" for row in cards),
        "eight_grid_cells": len(grid) == 8,
        "four_grid_cells_attested": sum(row["status"] == "attested" for row in grid) == 4,
        "eight_close_events": sum(row["contains_close"] == "YES" for row in events) == 8,
        "all_closes_terminal": all(row["statement_position"] in {"FINAL", "WHOLE"} for row in events if row["contains_close"] == "YES"),
        "cheey_shey_is_long_hold": all(row["component_recipe"] == "SH+EE+Y" for row in cards if row["card_no"] in {"PROC031", "PROC157"}),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_SIXTY_SEVENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, passed in checks.items():
        print(f"{name}\t{'PASS' if passed else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
