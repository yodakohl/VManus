#!/usr/bin/env python3
"""Validate the OK duration/endpoint paradigm."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    inventory = rows("SIX_HUNDRED_FIFTY_SIXTH_23_OK_CARD_INVENTORY.tsv")
    grid = rows("SIX_HUNDRED_FIFTY_SIXTH_8_DURATION_ENDPOINT_CELLS.tsv")
    predictions = rows("SIX_HUNDRED_FIFTY_SIXTH_2_PREDICTED_CELLS.tsv")
    choices = rows("SIX_HUNDRED_FIFTY_SIXTH_4_M09_GRID_CHOICES.tsv")
    active = [row for row in grid if row["endpoint"] == "ACTIVE_Y"]
    closed = [row for row in grid if row["endpoint"] == "CLOSED_DY"]
    checks = {
        "twenty_three_ok_cards": len(inventory) == 23,
        "seventy_nine_ok_events": sum(int(row["events"]) for row in inventory) == 79,
        "eight_grid_cells": len(grid) == 8,
        "seven_core_card_types": sum(int(row["card_types"]) for row in grid) == 7,
        "forty_one_core_events": sum(int(row["events"]) for row in grid) == 41,
        "six_attested_cells": sum(row["status"] == "attested" for row in grid) == 6,
        "two_predictions": len(predictions) == 2 and sum(row["status"] == "predicted_missing" for row in grid) == 2,
        "twenty_two_active_events": sum(int(row["events"]) for row in active) == 22,
        "nineteen_closed_events": sum(int(row["events"]) for row in closed) == 19,
        "all_nineteen_closed_final": sum(int(row["statement_final_events"]) for row in closed) == 19,
        "no_active_cell_has_close": all("SCHLIESSEN" not in row["reading_de"] for row in active),
        "all_closed_cells_close": all("SCHLIESSEN" in row["reading_de"] for row in closed),
        "four_m09_choices": len(choices) == 4,
        "m09_two_open_two_closed": sum(row["workshop_choice"] == "WEITERARBEITEN" for row in choices) == 2 and sum(row["workshop_choice"] == "ABSCHLIESSEN" for row in choices) == 2,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_FIFTY_SIXTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, passed in checks.items():
        print(f"{name}\t{'PASS' if passed else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
