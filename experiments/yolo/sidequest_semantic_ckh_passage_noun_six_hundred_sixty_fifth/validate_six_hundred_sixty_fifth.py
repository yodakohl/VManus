#!/usr/bin/env python3
"""Validate CKH passage-noun composition."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    cards = rows("SIX_HUNDRED_SIXTY_FIFTH_9_CKH_CARDS.tsv")
    events = rows("SIX_HUNDRED_SIXTY_FIFTH_14_CKH_EVENT_CONTEXTS.tsv")
    predictions = rows("SIX_HUNDRED_SIXTY_FIFTH_5_CKH_PREDICTIONS.tsv")
    checks = {
        "nine_cards": len(cards) == 9,
        "fourteen_events": len(events) == 14 and sum(int(row["events"]) for row in cards) == 14,
        "nine_recipes": len({row["component_recipe"] for row in cards}) == 9,
        "one_core_card": sum(row["component_recipe"] == "CKH+Y" for row in cards) == 1,
        "four_core_events": sum(int(row["events"]) for row in cards if row["component_recipe"] == "CKH+Y") == 4,
        "five_close_events": sum(row["contains_close"] == "YES" for row in events) == 5,
        "all_closes_final": all(row["statement_final"] == "YES" for row in events if row["contains_close"] == "YES"),
        "position_partition": {pos: sum(row["position_class"] == pos for row in events) for pos in ("ENTRY", "MEDIAL", "FINAL", "WHOLE_STATEMENT")} == {"ENTRY": 1, "MEDIAL": 8, "FINAL": 3, "WHOLE_STATEMENT": 2},
        "all_values_invariant": all(row["short_ckh_value_de"] == "DURCHLASS" for row in cards),
        "five_predictions": len(predictions) == 5,
        "no_placeholders": all(row["fluent_composition_de"] for row in cards),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_SIXTY_FIFTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, passed in checks.items():
        print(f"{name}\t{'PASS' if passed else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
