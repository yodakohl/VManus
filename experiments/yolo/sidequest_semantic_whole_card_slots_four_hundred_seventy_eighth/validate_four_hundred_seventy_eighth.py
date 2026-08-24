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
    dictionary = read("FOUR_HUNDRED_SEVENTY_EIGHTH_173_SLOT_REVISED_DICTIONARY.tsv")
    events = read("FOUR_HUNDRED_SEVENTY_EIGHTH_381_SLOT_REVISED_EVENTS.tsv")
    statements = read("FOUR_HUNDRED_SEVENTY_EIGHTH_116_SLOT_REVISED_STATEMENTS.tsv")
    units = read("FOUR_HUNDRED_SEVENTY_EIGHTH_14_SLOT_REVISED_UNIT_EDITIONS.tsv")
    whole = read("FOUR_HUNDRED_SEVENTY_EIGHTH_SIX_WHOLE_CARD_SLOT_DECISIONS.tsv")
    profiles = read("FOUR_HUNDRED_SEVENTY_EIGHTH_130_REMAINDER_CARD_SLOT_PROFILES.tsv")
    checks = {
        "dictionary_173": len(dictionary) == 173,
        "dictionary_ids_unique": len({row["joint_tuple_id"] for row in dictionary}) == 173,
        "events_381": len(events) == 381,
        "event_ids_unique": len({row["event_id"] for row in events}) == 381,
        "statements_116": len(statements) == 116,
        "statement_event_sum_381": sum(int(row["events"]) for row in statements) == 381,
        "whole_cards_6": len(whole) == 6,
        "whole_events_9": sum(int(row["events"]) for row in whole) == 9,
        "remainder_profiles_130": len(profiles) == 130,
        "two_values_revised": sum(row["decision"] == "REVISE" for row in whole) == 2,
        "five_statements_revised": sum(int(row["revised_whole_cards"]) > 0 for row in statements) == 5,
        "units_14": len(units) == 14,
        "groups_776": sum(int(row["groups"]) for row in units) == 776,
        "fixed_pages_only": {row["page"] for row in events + units} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"},
        "sealed_pages_absent": all(not row.get("page", "").startswith("f84") for row in events + statements + units),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_SEVENTY_EIGHTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(result["status"])
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
