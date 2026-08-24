#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    cards = read("FIVE_HUNDRED_THIRTY_EIGHTH_REVISED_ONE_HUNDRED_SEVENTY_THREE_CARD_DICTIONARY.tsv")
    events = read("FIVE_HUNDRED_THIRTY_EIGHTH_REVISED_THREE_HUNDRED_EIGHTY_ONE_EVENT_EDITION.tsv")
    reanalysis = read("FIVE_HUNDRED_THIRTY_EIGHTH_TWELVE_REMAINDER_REANALYSES.tsv")
    whole = read("FIVE_HUNDRED_THIRTY_EIGHTH_THREE_TRUE_WHOLE_CARDS.tsv")
    partial = read("FIVE_HUNDRED_THIRTY_EIGHTH_FOUR_LEARNED_ATOM_CARDS.tsv")
    card_status = Counter(row["composition_status"] for row in cards)
    event_status = Counter(row["composition_status"] for row in events)
    by_card = defaultdict(set)
    for row in events:
        by_card[row["card_no"]].add(row["revised_card_reading_de"])
    checks = {
        "cards173": len(cards) == 173 and len({row["card_no"] for row in cards}) == 173,
        "events381": len(events) == 381 and [row["event_id"] for row in events] == [f"E{i:03d}" for i in range(1, 382)],
        "reanalyses12": len(reanalysis) == 12,
        "card_counts166_4_3": card_status == Counter({"COMPOSITIONAL": 166, "PARTIAL_WITH_LEARNED_ATOM": 4, "LEARNED_WHOLE_CARD": 3}),
        "event_counts374_4_3": event_status == Counter({"COMPOSITIONAL": 374, "PARTIAL_WITH_LEARNED_ATOM": 4, "LEARNED_WHOLE_CARD": 3}),
        "whole_exact": [row["card_no"] for row in whole] == ["PROC005", "PROC043", "PROC115"],
        "partial_exact": [row["card_no"] for row in partial] == ["PROC028", "PROC124", "PROC155", "PROC169"],
        "all_full_predictions_exact": all(row["invariant_card_reading_de"] == row["predicted_from_other_cards_de"] for row in cards if row["composition_status"] == "COMPOSITIONAL"),
        "event_reading_invariant": all(len(values) == 1 for values in by_card.values()),
        "no_blank_default": all(row["invariant_card_reading_de"] for row in cards),
        "fixed_pages_only": {row["page"] for row in events} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "seal_absent": all(not row["page"].lower().startswith("f84") for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_THIRTY_EIGHTH_VALIDATION.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
