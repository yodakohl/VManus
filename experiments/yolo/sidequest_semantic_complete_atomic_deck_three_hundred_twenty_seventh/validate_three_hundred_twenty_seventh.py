#!/usr/bin/env python3
"""Validate the complete 173-card atomic workshop deck."""

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
    components = read("THREE_HUNDRED_TWENTY_SEVENTH_40_COMPONENTS.tsv")
    whole = read("THREE_HUNDRED_TWENTY_SEVENTH_23_WHOLE_CARDS.tsv")
    dictionary = read("THREE_HUNDRED_TWENTY_SEVENTH_173_ATOMIC_DICTIONARY.tsv")
    events = read("THREE_HUNDRED_TWENTY_SEVENTH_381_ATOMIC_EVENTS.tsv")
    statements = read("THREE_HUNDRED_TWENTY_SEVENTH_116_ATOMIC_STATEMENTS.tsv")
    event_counts = Counter(x["joint_tuple_id"] for x in events)
    checks = {
        "forty_components": len(components) == 40,
        "twenty_three_whole_cards": len(whole) == 23,
        "one_hundred_seventy_three_cards": len(dictionary) == 173 and len({x["joint_tuple_id"] for x in dictionary}) == 173,
        "one_hundred_fifty_productive_cards": sum(x["deck_class"] == "PRODUCTIVE_COMPOSITION" for x in dictionary) == 150,
        "all_values_one_word": all(x["one_word_value"] == "YES" for x in dictionary),
        "three_hundred_eighty_one_events": len(events) == 381 and len({x["event_id"] for x in events}) == 381,
        "event_counts_reconcile": all(event_counts[x["joint_tuple_id"]] == int(x["occurrences"]) for x in dictionary),
        "one_hundred_sixteen_statements": len(statements) == 116 and sum(int(x["event_count"]) for x in statements) == 381,
        "all_events_have_values": all(x["atomic_value_de"] for x in events),
        "no_unknown_placeholder": all(not any(term in x["atomic_value_de"].upper() for term in ["UNKNOWN", "EXEMPLAR", "FORMAL"]) for x in dictionary),
        "no_sealed_page": all("f84" not in x["pages"].lower() for x in dictionary)
        and all("f84" not in x["page"].lower() for x in events)
        and all("f84" not in x["page"].lower() for x in statements),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "THREE_HUNDRED_TWENTY_SEVENTH_VALIDATION.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
