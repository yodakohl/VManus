#!/usr/bin/env python3
"""Validate the graded SOLK collect grid."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    cards = rows("SIX_HUNDRED_SIXTY_SIXTH_5_SOLK_CARDS.tsv")
    events = rows("SIX_HUNDRED_SIXTY_SIXTH_7_SOLK_EVENT_CONTEXTS.tsv")
    grid = rows("SIX_HUNDRED_SIXTY_SIXTH_8_COLLECT_GRID_CELLS.tsv")
    predictions = rows("SIX_HUNDRED_SIXTY_SIXTH_5_SOLK_PREDICTIONS.tsv")
    checks = {
        "five_cards": len(cards) == 5,
        "seven_events": len(events) == 7 and sum(int(row["events"]) for row in cards) == 7,
        "five_recipes": len({row["component_recipe"] for row in cards}) == 5,
        "eight_grid_cells": len(grid) == 8,
        "four_attested_cells": sum(row["status"] == "attested" for row in grid) == 4,
        "four_predicted_cells": sum(row["status"] == "predicted_missing" for row in grid) == 4,
        "one_measure_event": sum(int(row["events"]) for row in cards if row["component_recipe"] == "SOLK+AIIN") == 1,
        "three_close_events": sum(row["contains_close"] == "YES" for row in events) == 3,
        "all_closes_final": all(row["statement_final"] == "YES" for row in events if row["contains_close"] == "YES"),
        "all_values_invariant": all(row["short_solk_value_de"] == "AUFFANGEN" for row in cards),
        "five_predictions": len(predictions) == 5,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_SIXTY_SIXTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, passed in checks.items():
        print(f"{name}\t{'PASS' if passed else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
