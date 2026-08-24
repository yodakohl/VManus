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
    dictionary = read("FOUR_HUNDRED_FIFTIETH_124_CARD_DICTIONARY.tsv")
    events = read("FOUR_HUNDRED_FIFTIETH_281_EVENT_EDITION.tsv")
    statements = read("FOUR_HUNDRED_FIFTIETH_97_STATEMENT_EDITION.tsv")
    generator = read("FOUR_HUNDRED_FIFTIETH_117_PRODUCTIVE_CARD_GENERATOR.tsv")
    components = read("FOUR_HUNDRED_FIFTIETH_33_COMPONENT_INVENTORY.tsv")
    wholes = read("FOUR_HUNDRED_FIFTIETH_SEVEN_WHOLE_CARDS.tsv")
    repairs = read("FOUR_HUNDRED_FIFTIETH_TEN_REPAIRS.tsv")
    product_ids = {row["joint_tuple_id"] for row in dictionary if row["union_drawer"] == "PRODUCTIVE_COMPOSITION"}
    whole_ids = {row["joint_tuple_id"] for row in dictionary if row["union_drawer"] != "PRODUCTIVE_COMPOSITION"}
    component_names = {row["component"] for row in components}
    checks = {
        "dictionary_124": len(dictionary) == 124,
        "events_281": len(events) == 281,
        "statements_97": len(statements) == 97,
        "generator_117": len(generator) == 117,
        "whole_cards_7": len(wholes) == 7,
        "components_33": len(components) == 33,
        "repairs_10": len(repairs) == 10,
        "generator_exact_product_set": {row["joint_tuple_id"] for row in generator} == product_ids,
        "whole_exact_nonproduct_set": {row["joint_tuple_id"] for row in wholes} == whole_ids,
        "every_generator_licensed": all(row["licensed_by_manual"] == "YES" for row in generator),
        "every_component_known": all(set(row["normalized_components"].split("+")) <= component_names for row in generator),
        "singleton_bound_signs_exact": {row["component"] for row in components if row["teaching_status"] == "LEARNED_BOUND_SIGN"} == {"IIN", "LDDY", "LS"},
        "drawer_counts_117_3_4": [sum(row["union_drawer"] == drawer for row in dictionary) for drawer in ("PRODUCTIVE_COMPOSITION", "PORTABLE_LEARNED_WHOLE_CARD", "RECORD_LOCAL_LEARNED_WHOLE_CARD")] == [117, 3, 4],
        "event_counts_269_12": [sum(row["union_drawer"] == "PRODUCTIVE_COMPOSITION" for row in events), sum(row["union_drawer"] != "PRODUCTIVE_COMPOSITION" for row in events)] == [269, 12],
        "dictionary_event_agreement": all(next(card for card in dictionary if card["joint_tuple_id"] == row["joint_tuple_id"])["small_value_de"] == row["small_value_de"] for row in events),
        "all_events_once": [row["event_id"] for row in events] == [f"E{n}" for n in range(101, 382)],
        "statement_events_once": sorted((event_id for row in statements for event_id in row["event_ids"].split("|")), key=lambda event_id: int(event_id[1:])) == [f"E{n}" for n in range(101, 382)],
        "stale_inconsistent_values_removed": all(value not in {row["small_value_de"] for row in events} for value in ("voll spülen", "Laufflüssigkeit in Gang setzen", "Laufflüssigkeit weiterführen", "Laufflüssigkeit abschließen", "Waschflüssigkeit an die Stelle", "Folgeüberführung; Schluss")),
        "aiiin_demoted": next(row for row in dictionary if row["joint_tuple_id"] == "fcc1deda9e24ec268eb0")["union_drawer"] == "RECORD_LOCAL_LEARNED_WHOLE_CARD",
        "no_empty_values": all(row["small_value_de"].strip() for row in events),
        "fixed_pages_only": {row["page"] for row in events} == {"f81v", "f82r", "f83r"},
        "sealed_absent": all("f84" not in row["locus"].lower() for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_FIFTIETH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
