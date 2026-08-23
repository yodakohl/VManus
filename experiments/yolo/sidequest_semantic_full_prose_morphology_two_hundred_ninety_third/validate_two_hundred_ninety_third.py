#!/usr/bin/env python3
"""Validate Pass 293 full prose production morphology."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> None:
    cards = read("TWO_HUNDRED_NINETY_THIRD_149_CARD_PRODUCTION_CLASSIFICATION.tsv")
    contexts = read("TWO_HUNDRED_NINETY_THIRD_4_CONTEXTUAL_RENDERER_RULES.tsv")
    summary = read("TWO_HUNDRED_NINETY_THIRD_FOUR_MECHANIC_SUMMARY.tsv")
    counts = Counter(row["production_mechanic"] for row in cards)
    event_counts = Counter()
    for row in cards:
        event_counts[row["production_mechanic"]] += int(row["event_support"])
    expected_cards = {
        "REGISTERED_BASE_FAMILY_CARD": 35,
        "ORDERED_SLOT_FRAME_ASSEMBLY": 64,
        "GRADE_INSERTION_OR_LENGTHENING": 30,
        "SHARED_TRANSFER_CORE_OVERLAY": 20,
    }
    expected_events = {
        "REGISTERED_BASE_FAMILY_CARD": 121,
        "ORDERED_SLOT_FRAME_ASSEMBLY": 115,
        "GRADE_INSERTION_OR_LENGTHENING": 73,
        "SHARED_TRANSFER_CORE_OVERLAY": 43,
    }
    checks = {
        "cards_149": len(cards) == 149,
        "events_352": sum(int(row["event_support"]) for row in cards) == 352,
        "four_mechanics": len(summary) == 4 and set(counts) == set(expected_cards),
        "mechanic_card_counts": dict(counts) == expected_cards,
        "mechanic_event_counts": dict(event_counts) == expected_events,
        "event_crosschecks": all(row["event_support"] == row["event_count_crosscheck"] for row in cards),
        "four_contextual_rules": len(contexts) == 4,
        "recipe_only_145": sum(row["contextual_renderer_override"] == "NO" for row in cards) == 145,
        "all_have_instruction": all(row["production_instruction_de"] and row["ordered_slots"] for row in cards),
        "no_sealed_page": not any("f" + "84" in path.read_text(encoding="utf-8").lower() for path in [HERE / "TWO_HUNDRED_NINETY_THIRD_149_CARD_PRODUCTION_CLASSIFICATION.tsv", HERE / "TWO_HUNDRED_NINETY_THIRD_APPRENTICE_MORPHOLOGY_MANUAL.md", HERE / "TWO_HUNDRED_NINETY_THIRD_REPORT.md"]),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "failed": [key for key, value in checks.items() if not value]}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
