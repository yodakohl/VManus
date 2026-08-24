#!/usr/bin/env python3
"""Validate the 173-card semantic learning-burden classification."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    cards = read("SIX_HUNDRED_THIRTY_SIXTH_173_CARD_LEARNING_BURDEN.tsv")
    events = read("SIX_HUNDRED_THIRTY_SIXTH_381_EVENT_LEARNING_BURDEN.tsv")
    summary = read("SIX_HUNDRED_THIRTY_SIXTH_4_CLASS_SUMMARY.tsv")
    words = read("SIX_HUNDRED_THIRTY_SIXTH_39_WORD_BURDEN.tsv")
    expected_cards = {
        "FULLY_COMPOSITIONAL_CARD": 33,
        "COMPOSITIONAL_MEANING_LEARNED_EXACT_SURFACE": 132,
        "PARTIAL_COMPOSITION_ONE_LEARNED_CORE": 5,
        "TRUE_LEARNED_WHOLE_CARD": 3,
    }
    expected_events = {
        "FULLY_COMPOSITIONAL_CARD": 159,
        "COMPOSITIONAL_MEANING_LEARNED_EXACT_SURFACE": 213,
        "PARTIAL_COMPOSITION_ONE_LEARNED_CORE": 5,
        "TRUE_LEARNED_WHOLE_CARD": 4,
    }
    checks = {
        "one_hundred_seventy_three_cards": len(cards) == 173 and len({row["card_no"] for row in cards}) == 173,
        "three_hundred_eighty_one_events": len(events) == 381 and len({row["event_id"] for row in events}) == 381,
        "four_classes": len(summary) == 4,
        "expected_card_counts": {row["burden_class"]: int(row["exact_cards"]) for row in summary} == expected_cards,
        "expected_event_counts": {row["burden_class"]: int(row["occurrences"]) for row in summary} == expected_events,
        "events_match_cards": all(next(card for card in cards if card["card_no"] == event["card_no"])["burden_class"] == event["burden_class"] for event in events),
        "thirty_nine_words": len(words) == 39,
        "word_burden_31_5_3": sum(row["semantic_word_burden"] == "RECURRENT_PRODUCTIVE_COMPONENT" for row in words) == 31 and sum(row["semantic_word_burden"] == "ONE_USE_EMBEDDED_CORE" for row in words) == 5 and sum(row["semantic_word_burden"] == "ONE_USE_WHOLE_CARD_WORD" for row in words) == 3,
        "no_unknown_components": all(row["unknown_components"] == "NONE" for row in cards),
        "whole_cards_are_expected": {row["semantic_component_parse"] for row in cards if row["burden_class"] == "TRUE_LEARNED_WHOLE_CARD"} == {"OS", "RESUME_CARD", "TALAM"},
        "partial_cores_are_expected": {row["rare_one_use_components"] for row in cards if row["burden_class"] == "PARTIAL_COMPOSITION_ONE_LEARNED_CORE"} == {"AN", "CFH", "DA", "LD", "S"},
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_THIRTY_SIXTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
