#!/usr/bin/env python3
"""Validate Pass 715 exception compression."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    events = read("SEVEN_HUNDRED_FIFTEENTH_35_REFINED_CARD_CHOICES.tsv")
    rules = read("SEVEN_HUNDRED_FIFTEENTH_4_CARD_FAMILY_RULES.tsv")
    surface_events = read("SEVEN_HUNDRED_FIFTEENTH_5_SURFACE_TRAY_EVENTS.tsv")
    trays = read("SEVEN_HUNDRED_FIFTEENTH_3_LOCAL_SURFACE_TRAYS.tsv")
    checks = {
        "card_events_35": len(events) == 35,
        "four_recipes": {row["component_recipe"] for row in events} == {"OK+Y", "CHD+Y", "CHD+DY", "OK+CHD+DY"},
        "four_rules": len(rules) == 4 and {row["rule_id"] for row in rules} == {"CR1", "CR2", "CR3", "CR4"},
        "card_rules_35_of_35": all(row["refined_correct"] == "YES" for row in events) and sum(int(row["correct"]) for row in rules) == 35,
        "zero_card_errors": all(row["errors"] == "0" for row in rules),
        "five_surface_events": len(surface_events) == 5 and len({row["event_id"] for row in surface_events}) == 5,
        "three_trays": len(trays) == 3 and sum(int(row["events"]) for row in trays) == 5,
        "b1_tray_has_three": next(row for row in trays if row["tray_id"] == "ST3")["events"] == "3",
        "no_meaning_change": all(row["status"] == "LOCAL_COPY_TRAY__NO_MEANING_CHANGE" for row in trays),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_FIFTEENTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
