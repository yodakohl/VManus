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
    components = read("FIVE_HUNDRED_THIRTY_SEVENTH_COMPONENT_INVARIANCE_LEXICON.tsv")
    cards = read("FIVE_HUNDRED_THIRTY_SEVENTH_ONE_HUNDRED_SEVENTY_THREE_CARD_COMPOSITION_DECISIONS.tsv")
    events = read("FIVE_HUNDRED_THIRTY_SEVENTH_THREE_HUNDRED_EIGHTY_ONE_COMPOSITION_EVENT_AUDIT.tsv")
    whole = read("FIVE_HUNDRED_THIRTY_SEVENTH_LEARNED_WHOLE_CARD_DECK.tsv")
    partial = read("FIVE_HUNDRED_THIRTY_SEVENTH_PARTIAL_COMPOSITION_CARDS.tsv")
    card_status = Counter(row["composition_status"] for row in cards)
    event_status = Counter(row["composition_status"] for row in events)
    decisions = {row["card_no"]: row for row in cards}
    checks = {
        "cards173": len(cards) == 173 and len({row["card_no"] for row in cards}) == 173,
        "events381": len(events) == 381 and [row["event_id"] for row in events] == [f"E{i:03d}" for i in range(1, 382)],
        "event_card_partition": Counter(row["card_no"] for row in events) == Counter({row["card_no"]: int(row["occurrences"]) for row in cards}),
        "three_statuses_cover_cards": sum(card_status.values()) == 173 and set(card_status) == {"LEAVE_ONE_CARD_COMPOSITIONAL", "PARTIAL_COMPOSITION_PLUS_LEARNED_REMAINDER", "LEARNED_WHOLE_CARD"},
        "three_statuses_cover_events": sum(event_status.values()) == 381 and set(event_status) == set(card_status),
        "whole_table_exact": len(whole) == card_status["LEARNED_WHOLE_CARD"],
        "partial_table_exact": len(partial) == card_status["PARTIAL_COMPOSITION_PLUS_LEARNED_REMAINDER"],
        "full_predictions_exact": all(row["actual_reading_de"] == row["predicted_reading_from_other_cards_de"] for row in cards if row["composition_status"] == "LEAVE_ONE_CARD_COMPOSITIONAL"),
        "event_status_matches_card": all(row["composition_status"] == decisions[row["card_no"]]["composition_status"] for row in events),
        "productive_stems_have_support": all(int(row["aligned_card_types"]) >= 2 and row["invariant_across_aligned_cards"] == "YES" for row in components if row["status"] == "PRODUCTIVE_STEM"),
        "all_concrete_defaults": all(row["actual_reading_de"] for row in cards),
        "fixed_pages_only": {row["page"] for row in events} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "seal_absent": all(not row["page"].lower().startswith("f84") for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "card_status_counts": dict(card_status), "event_status_counts": dict(event_status)}
    (HERE / "FIVE_HUNDRED_THIRTY_SEVENTH_VALIDATION.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
