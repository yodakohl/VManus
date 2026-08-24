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
    events = read("FOUR_HUNDRED_FIFTY_FOURTH_100_EVENT_HERBAL_EDITION.tsv")
    cards = read("FOUR_HUNDRED_FIFTY_FOURTH_66_CARD_HERBAL_DICTIONARY.tsv")
    decisions = read("FOUR_HUNDRED_FIFTY_FOURTH_49_CARD_DECISIONS.tsv")
    statements = read("FOUR_HUNDRED_FIFTY_FOURTH_19_STATEMENT_HERBAL_EDITION.tsv")
    wholes = read("FOUR_HUNDRED_FIFTY_FOURTH_THREE_HERBAL_WHOLE_CARDS.tsv")
    extensions = read("FOUR_HUNDRED_FIFTY_FOURTH_TWO_HERBAL_COMPONENT_EXTENSIONS.tsv")
    by_id = {row["joint_tuple_id"]: row for row in cards}
    checks = {
        "events_100": len(events) == 100,
        "events_exact_order": [row["event_id"] for row in events] == [f"E{n:03d}" for n in range(1, 101)],
        "cards_66": len(cards) == 66 and len(by_id) == 66,
        "statements_19": len(statements) == 19,
        "records_5": {row["record_unit_id"] for row in events} == {f"H{n}" for n in range(1, 6)},
        "decisions_49": len(decisions) == 49,
        "biological_components_39": sum(row["completion_class"] == "BIOLOGICAL_COMPONENTS" for row in decisions) == 39,
        "herbal_extensions_7": sum(row["completion_class"] == "HERBAL_COMPONENT_EXTENSION" for row in decisions) == 7,
        "whole_cards_3": len(wholes) == 3 and {row["small_value_de"] for row in wholes} == {"Gefäß", "auswringen", "verwahren"},
        "extensions_2": {(row["component"], row["value_de"]) for row in extensions} == {("HO", "Zutat"), ("CHEO", "Auszug")},
        "no_pending": all(row["completion_class"] != "HERBAL_LOCAL_CARD_PENDING_REANALYSIS" for row in events),
        "event_dictionary_match": all(by_id[row["joint_tuple_id"]]["small_value_de"] == row["small_value_de"] for row in events),
        "statement_events_once": sorted((event for row in statements for event in row["event_ids"].split("|")), key=lambda item: int(item[1:])) == [f"E{n:03d}" for n in range(1, 101)],
        "picture_owners_4": len({row["picture_owner"] for row in events}) == 4,
        "fixed_pages": {row["page"] for row in events} == {"f10r", "f11r", "f55v", "f56r"},
        "sealed_absent": all("f84" not in (row["page"] + row["locus"]).lower() for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_FIFTY_FOURTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
