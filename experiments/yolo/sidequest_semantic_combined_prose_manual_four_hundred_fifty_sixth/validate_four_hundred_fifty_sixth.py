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
    events = read("FOUR_HUNDRED_FIFTY_SIXTH_381_EVENT_COMBINED_EDITION.tsv")
    cards = read("FOUR_HUNDRED_FIFTY_SIXTH_173_CARD_COMBINED_DICTIONARY.tsv")
    statements = read("FOUR_HUNDRED_FIFTY_SIXTH_116_STATEMENT_COMBINED_EDITION.tsv")
    shared = read("FOUR_HUNDRED_FIFTY_SIXTH_17_CROSS_REGISTER_CARDS.tsv")
    components = read("FOUR_HUNDRED_FIFTY_SIXTH_35_COMPONENT_MANUAL.tsv")
    wholes = read("FOUR_HUNDRED_FIFTY_SIXTH_TEN_WHOLE_CARDS.tsv")
    aliases = read("FOUR_HUNDRED_FIFTY_SIXTH_VALUE_ALIAS_FAMILIES.tsv")
    by_id = {row["joint_tuple_id"]: row for row in cards}
    checks = {
        "events_381": len(events) == 381,
        "event_order": [row["event_id"] for row in events] == [f"E{n:03d}" for n in range(1, 382)],
        "herbal_biological_counts": [sum(row["register"] == register for row in events) for register in ("HERBAL", "BIOLOGICAL")] == [100, 281],
        "cards_173": len(cards) == 173 and len(by_id) == 173,
        "statements_116": len(statements) == 116,
        "components_35": len(components) == 35,
        "productive_cards_163": sum(row["lexicon_class"] == "PRODUCTIVE_COMPOSITION" for row in cards) == 163,
        "productive_events_363": sum(row["lexicon_class"] == "PRODUCTIVE_COMPOSITION" for row in events) == 363,
        "whole_cards_10": len(wholes) == 10,
        "whole_events_18": sum(row["lexicon_class"] == "MEMORIZED_WHOLE_CARD" for row in events) == 18,
        "cross_register_cards_17": len(shared) == 17,
        "cross_register_counts": [sum(int(row[key]) for row in shared) for key in ("herbal_events", "biological_events")] == [44, 92],
        "cross_register_no_collision": all(row["value_collision"] == "NO" for row in shared),
        "event_dictionary_match": all(by_id[row["joint_tuple_id"]]["small_value_de"] == row["small_value_de"] and by_id[row["joint_tuple_id"]]["component_parse"] == row["component_parse"] for row in events),
        "statement_events_once": sorted((event for row in statements for event in row["event_ids"].split("|")), key=lambda item: int(item[1:])) == [f"E{n:03d}" for n in range(1, 382)],
        "all_components_used": all(int(row["combined_support_cards"]) > 0 for row in components),
        "only_new_components_herbal_only": {row["component"] for row in components if row["register_scope"] == "HERBAL_ONLY"} == {"HO", "CHEO"},
        "alias_rows_real": all(int(row["cards"]) >= 2 for row in aliases),
        "fixed_pages": {row["page"] for row in events} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_absent": all("f84" not in (row["page"] + row["locus"]).lower() for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_FIFTY_SIXTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
