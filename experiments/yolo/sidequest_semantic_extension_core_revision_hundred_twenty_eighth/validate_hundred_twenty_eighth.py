#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    decisions = rows("HUNDRED_TWENTY_EIGHTH_TWENTY_FOUR_EXTENSION_DECISIONS.tsv")
    occurrences = rows("HUNDRED_TWENTY_EIGHTH_103_EXTENSION_OCCURRENCES.tsv")
    cards = rows("HUNDRED_TWENTY_EIGHTH_173_CARD_OVERLAY.tsv")
    events = rows("HUNDRED_TWENTY_EIGHTH_381_EVENT_OVERLAY.tsv")
    statements = rows("HUNDRED_TWENTY_EIGHTH_116_LITERAL_STATEMENTS.tsv")
    checks = {
        "decisions_24": len(decisions) == 24,
        "occurrences_103": len(occurrences) == 103,
        "cards_173": len(cards) == 173,
        "events_381": len(events) == 381,
        "statements_116": len(statements) == 116,
        "decision_counts_sum": sum(int(row["event_count"]) for row in decisions) == 103,
        "revised_cards_41": sum(row["current_layer"] != "UNCHANGED_LEARNED_SECTION_CARD" for row in cards) == 41,
        "revised_events_239": sum(int(row["event_count"]) for row in cards if row["current_layer"] != "UNCHANGED_LEARNED_SECTION_CARD") == 239,
        "remaining_cards_132": sum(row["current_layer"] == "UNCHANGED_LEARNED_SECTION_CARD" for row in cards) == 132,
        "all_defaults_short": all(len(row["revised_short_default_de"].split()) <= 4 for row in decisions),
        "no_empty_cells": all(all(value for value in row.values()) for table in (decisions, occurrences, cards, events, statements) for row in table),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
