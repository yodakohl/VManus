#!/usr/bin/env python3
"""Validate the zero-new-component whole-card attack."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    attacks = read("THREE_HUNDRED_TWENTY_EIGHTH_23_WHOLE_CARD_ATTACKS.tsv")
    retained = read("THREE_HUNDRED_TWENTY_EIGHTH_15_RETAINED_WHOLE_CARDS.tsv")
    dictionary = read("THREE_HUNDRED_TWENTY_EIGHTH_173_REVISED_DICTIONARY.tsv")
    events = read("THREE_HUNDRED_TWENTY_EIGHTH_381_REVISED_EVENTS.tsv")
    statements = read("THREE_HUNDRED_TWENTY_EIGHTH_SIX_REVISED_STATEMENTS.tsv")
    event_counts = Counter(x["joint_tuple_id"] for x in events)
    checks = {
        "twenty_three_attacks": len(attacks) == 23,
        "eight_promotions": sum(x["decision"] == "PROMOTE_WITH_EXISTING_COMPONENTS" for x in attacks) == 8,
        "fifteen_retained": len(retained) == 15,
        "zero_new_components": all(x["new_components_added"] == "0" for x in attacks),
        "one_hundred_fifty_eight_productive": sum(x["deck_class"] == "PRODUCTIVE_COMPOSITION" for x in dictionary) == 158,
        "one_hundred_seventy_three_cards": len(dictionary) == 173,
        "three_hundred_eighty_one_events": len(events) == 381,
        "three_hundred_sixty_one_productive_events": sum(x["deck_class"] == "PRODUCTIVE_COMPOSITION" for x in events) == 361,
        "twenty_whole_events": sum(x["deck_class"] == "MEMORIZED_WHOLE_CARD" for x in events) == 20,
        "six_revised_statements": len(statements) == 6,
        "event_counts_reconcile": all(event_counts[x["joint_tuple_id"]] == int(x["occurrences"]) for x in dictionary),
        "all_values_one_word": all(not any(mark in x["atomic_value_de"] for mark in [" ", "/", ";"]) for x in dictionary),
        "no_sealed_page": all("f84" not in x["pages"].lower() for x in dictionary) and all("f84" not in x["page"].lower() for x in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "THREE_HUNDRED_TWENTY_EIGHTH_VALIDATION.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
