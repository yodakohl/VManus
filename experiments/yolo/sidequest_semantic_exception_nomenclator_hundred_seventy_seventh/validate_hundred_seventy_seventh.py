#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    cards = read("HUNDRED_SEVENTY_SEVENTH_19_CARD_NOMENCLATOR.tsv")
    drawers = read("HUNDRED_SEVENTY_SEVENTH_5_NOMENCLATOR_DRAWERS.tsv")
    events = read("HUNDRED_SEVENTY_SEVENTH_24_EXCEPTION_OCCURRENCES.tsv")
    expected_drawers = {
        "N1_MATERIAL_AND_TOOL": 4,
        "N2_CONTAINER_AND_PLACE": 2,
        "N3_SEPARATE_AND_CLARIFY": 6,
        "N4_WASH_AND_CLOSE": 3,
        "N5_LINK_AND_ADMINISTER": 4,
    }
    actual = {}
    for row in cards:
        actual[row["drawer"]] = actual.get(row["drawer"], 0) + 1
    checks = {
        "nineteen_cards": len(cards) == 19 and len({row["master_card_id"] for row in cards}) == 19,
        "lesson_order": [int(row["lesson_order"]) for row in cards] == list(range(1, 20)),
        "five_drawers": len(drawers) == 5 and actual == expected_drawers,
        "drawer_declared_counts": {row["drawer"]: int(row["card_count"]) for row in drawers} == expected_drawers,
        "twenty_four_occurrences": len(events) == 24 and len({int(row["event_serial"]) for row in events}) == 24,
        "all_cards_observed": {row["master_card_id"] for row in events} == {row["master_card_id"] for row in cards},
        "all_gestures_concrete": all(row["master_gesture_de"].strip() for row in cards),
        "all_values_concrete": all(row["concise_nomenclator_value_de"].strip() for row in cards),
        "fixed_pages_only": all(not row["page"].startswith("f84") for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
