#!/usr/bin/env python3
"""Validate all-card OK valency composition."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    recipes = rows("SIX_HUNDRED_FIFTY_SEVENTH_20_OK_RECIPES.tsv")
    arguments = rows("SIX_HUNDRED_FIFTY_SEVENTH_7_ARGUMENT_SLOTS.tsv")
    events = rows("SIX_HUNDRED_FIFTY_SEVENTH_79_OK_EVENT_READINGS.tsv")
    predictions = rows("SIX_HUNDRED_FIFTY_SEVENTH_5_COMPOSITION_PREDICTIONS.tsv")
    checks = {
        "twenty_recipes": len(recipes) == 20,
        "twenty_three_cards": sum(int(row["card_types"]) for row in recipes) == 23,
        "seventy_nine_events": len(events) == 79 and sum(int(row["events"]) for row in recipes) == 79,
        "seven_argument_slots": len(arguments) == 7,
        "nine_direct_argument_cards": sum(int(row["direct_card_types"]) for row in arguments) == 9,
        "thirty_nine_direct_argument_events": sum(int(row["direct_events"]) for row in arguments) == 39,
        "all_ok_values_invariant": all(row["ok_value_invariant"] == "YES" for row in events),
        "twenty_six_closed_ok_events": sum(row["contains_close"] == "YES" for row in events) == 26,
        "all_closed_ok_events_final": all(row["statement_final"] == "YES" for row in events if row["contains_close"] == "YES"),
        "five_predictions": len(predictions) == 5,
        "event_ids_unique": len({row["event_id"] for row in events}) == 79,
        "no_empty_composed_commands": all(row["composed_command_de"] for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_FIFTY_SEVENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, passed in checks.items():
        print(f"{name}\t{'PASS' if passed else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
