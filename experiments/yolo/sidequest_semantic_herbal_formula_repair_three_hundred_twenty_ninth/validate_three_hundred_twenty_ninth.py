#!/usr/bin/env python3
"""Validate Herbal formula/value consistency repairs."""

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
    repairs = read("THREE_HUNDRED_TWENTY_NINTH_24_FORMULA_REPAIRS.tsv")
    dictionary = read("THREE_HUNDRED_TWENTY_NINTH_173_GLOBAL_DICTIONARY.tsv")
    events = read("THREE_HUNDRED_TWENTY_NINTH_381_GLOBAL_EVENTS.tsv")
    herbal_dictionary = read("THREE_HUNDRED_TWENTY_NINTH_HERBAL_DICTIONARY.tsv")
    herbal_events = read("THREE_HUNDRED_TWENTY_NINTH_100_HERBAL_EVENTS.tsv")
    statements = read("THREE_HUNDRED_TWENTY_NINTH_19_HERBAL_STATEMENTS.tsv")
    event_counts = Counter(x["joint_tuple_id"] for x in events)
    checks = {
        "twenty_four_repairs": len(repairs) == 24,
        "one_restored_whole": sum(x["decision"] == "RESTORE_SHARED_WHOLE_CARD" for x in repairs) == 1,
        "one_hundred_seventy_three_cards": len(dictionary) == 173,
        "one_hundred_fifty_seven_productive": sum(x["deck_class"] == "PRODUCTIVE_COMPOSITION" for x in dictionary) == 157,
        "sixteen_whole": sum(x["deck_class"] == "MEMORIZED_WHOLE_CARD" for x in dictionary) == 16,
        "three_hundred_eighty_one_events": len(events) == 381,
        "event_counts_reconcile": all(event_counts[x["joint_tuple_id"]] == int(x["occurrences"]) for x in dictionary),
        "sixty_six_herbal_cards": len(herbal_dictionary) == 66,
        "one_hundred_herbal_events": len(herbal_events) == 100,
        "nineteen_herbal_statements": len(statements) == 19 and sum(int(x["event_count"]) for x in statements) == 100,
        "all_values_one_word": all(not any(mark in x["atomic_value_de"] for mark in [" ", "/", ";"]) for x in dictionary),
        "no_superseded_herbal_glosses": not any(x["atomic_value_de"] in {"Geschwür", "Trank", "Blütebeginn", "Pflanzenspitzen", "Grobzerreiben", "Abseihen", "Waschen"} for x in herbal_dictionary),
        "no_sealed_page": all("f84" not in x["pages"].lower() for x in dictionary) and all("f84" not in x["page"].lower() for x in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "THREE_HUNDRED_TWENTY_NINTH_VALIDATION.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
