#!/usr/bin/env python3
"""Validate OR preparation-noun composition."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    cards = rows("SIX_HUNDRED_SIXTY_FOURTH_10_OR_CARDS.tsv")
    events = rows("SIX_HUNDRED_SIXTY_FOURTH_18_OR_EVENT_CONTEXTS.tsv")
    predictions = rows("SIX_HUNDRED_SIXTY_FOURTH_5_OR_PREDICTIONS.tsv")
    checks = {
        "ten_cards": len(cards) == 10,
        "eighteen_events": len(events) == 18 and sum(int(row["events"]) for row in cards) == 18,
        "ten_recipes": len({row["component_recipe"] for row in cards}) == 10,
        "one_bare_card": sum(row["component_recipe"] == "OR" for row in cards) == 1,
        "seven_bare_events": sum(int(row["events"]) for row in cards if row["component_recipe"] == "OR") == 7,
        "four_bare_surfaces": len(next(row["surfaces"] for row in cards if row["component_recipe"] == "OR").split("|")) == 4,
        "position_partition": {pos: sum(row["position_class"] == pos for row in events) for pos in ("ENTRY", "MEDIAL", "FINAL")} == {"ENTRY": 6, "MEDIAL": 10, "FINAL": 2},
        "no_or_closes": all(row["contains_close"] == "NO" for row in cards),
        "five_pages": len({row["page"] for row in events}) == 5,
        "eight_records": len({row["record"] for row in events}) == 8,
        "five_predictions": len(predictions) == 5,
        "all_short_values_invariant": all(row["short_or_value_de"] == "ANSATZ_ODER_ZUBEREITUNG" for row in cards),
        "no_placeholders": all(row["fluent_composition_de"] for row in cards),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_SIXTY_FOURTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, passed in checks.items():
        print(f"{name}\t{'PASS' if passed else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
