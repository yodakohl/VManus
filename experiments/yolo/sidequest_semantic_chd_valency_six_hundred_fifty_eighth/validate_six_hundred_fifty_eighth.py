#!/usr/bin/env python3
"""Validate CHD/CHED valency composition."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    inventory = rows("SIX_HUNDRED_FIFTY_EIGHTH_22_CHD_CARD_INVENTORY.tsv")
    recipes = rows("SIX_HUNDRED_FIFTY_EIGHTH_18_CHD_RECIPES.tsv")
    slots = rows("SIX_HUNDRED_FIFTY_EIGHTH_5_ARGUMENT_ENDPOINT_SLOTS.tsv")
    prefixes = rows("SIX_HUNDRED_FIFTY_EIGHTH_5_DIRECTION_PREFIXES.tsv")
    events = rows("SIX_HUNDRED_FIFTY_EIGHTH_48_CHD_EVENT_READINGS.tsv")
    predictions = rows("SIX_HUNDRED_FIFTY_EIGHTH_5_COMPOSITION_PREDICTIONS.tsv")
    checks = {
        "twenty_two_cards": len(inventory) == 22,
        "forty_eight_events": len(events) == 48 and sum(int(row["events"]) for row in inventory) == 48,
        "eighteen_recipes": len(recipes) == 18,
        "five_slots": len(slots) == 5,
        "seven_direct_slot_cards": sum(int(row["direct_card_types"]) for row in slots) == 7,
        "twenty_direct_slot_events": sum(int(row["direct_events"]) for row in slots) == 20,
        "five_prefixes": len(prefixes) == 5,
        "all_chd_invariant": all(row["invariant_chd_value"] == "YES" for row in inventory),
        "twenty_eight_closed": sum(row["contains_close"] == "YES" for row in events) == 28,
        "all_closed_final": all(row["statement_final"] == "YES" for row in events if row["contains_close"] == "YES"),
        "five_predictions": len(predictions) == 5,
        "unique_event_ids": len({row["event_id"] for row in events}) == 48,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_FIFTY_EIGHTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, passed in checks.items():
        print(f"{name}\t{'PASS' if passed else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
