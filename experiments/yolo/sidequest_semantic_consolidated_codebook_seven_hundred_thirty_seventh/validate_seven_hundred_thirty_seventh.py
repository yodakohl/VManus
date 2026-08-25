#!/usr/bin/env python3
"""Validate Pass 737 consolidated creative codebook."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    components = read("SEVEN_HUNDRED_THIRTY_SEVENTH_39_COMPONENT_DICTIONARY.tsv")
    classes = read("SEVEN_HUNDRED_THIRTY_SEVENTH_3_COMPOSITION_CLASSES.tsv")
    remainders = read("SEVEN_HUNDRED_THIRTY_SEVENTH_8_REMAINDER_CARDS.tsv")
    cards = read("SEVEN_HUNDRED_THIRTY_SEVENTH_173_REBUILT_CARD_DICTIONARY.tsv")
    events = read("SEVEN_HUNDRED_THIRTY_SEVENTH_381_EVENT_INTERLINEAR.tsv")
    statements = read("SEVEN_HUNDRED_THIRTY_SEVENTH_116_STATEMENT_EDITION.tsv")
    records = read("SEVEN_HUNDRED_THIRTY_SEVENTH_11_RECORD_EDITION.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_THIRTY_SEVENTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    class_counts = {row["composition_status"]: (int(row["cards"]), int(row["events"])) for row in classes}
    checks = {
        "components_39_categories_31_5_3": len(components) == 39 and sum(row["category"] == "RECURRENT_PRODUCTIVE_ROOT" for row in components) == 31 and sum(row["category"] == "SINGLETON_COMPONENT_GUESS" for row in components) == 5 and sum(row["category"] == "MEMORIZED_WHOLE_COMMAND" for row in components) == 3,
        "classes_exact": class_counts == {"FULLY_COMPOSED_FROM_RECURRENT_ROOTS": (165, 372), "HAS_SINGLETON_COMPONENT_GUESS": (5, 5), "HAS_MEMORIZED_WHOLE_COMMAND": (3, 4)},
        "remainders_eight": len(remainders) == 8 and sum(int(row["events"]) for row in remainders) == 9,
        "cards_173_all_exact": len(cards) == 173 and len({row["exact_card_id"] for row in cards}) == 173 and all(row["exact_rebuild"] == "YES" for row in cards),
        "events_381_unique": len(events) == 381 and len({row["event_id"] for row in events}) == 381,
        "statements_116_records_11": len(statements) == 116 and len(records) == 11,
        "event_card_readings_match": all(next(card["rebuilt_reading_de"] for card in cards if card["exact_card_id"] == row["card_no"]) == row["rebuilt_reading_de"] for row in events),
        "all_meanings_nonempty": all(row["short_value_de"].strip() for row in components) and all(row["rebuilt_reading_de"].strip() for row in cards + events),
        "statement_event_totals_381": sum(int(row["events"]) for row in statements) == 381,
        "record_event_totals_381": sum(int(row["events"]) for row in records) == 381,
        "form_fixed": summary["form_changes"] == 0 and all(row["form_owner_boundary_status"] == "UNCHANGED" for row in events + statements),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_THIRTY_SEVENTH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
