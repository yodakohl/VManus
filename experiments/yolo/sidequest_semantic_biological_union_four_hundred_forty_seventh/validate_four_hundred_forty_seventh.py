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
    dictionary = read("FOUR_HUNDRED_FORTY_SEVENTH_124_CARD_DICTIONARY.tsv")
    events = read("FOUR_HUNDRED_FORTY_SEVENTH_281_EVENT_EDITION.tsv")
    statements = read("FOUR_HUNDRED_FORTY_SEVENTH_97_STATEMENT_EDITION.tsv")
    fields = read("FOUR_HUNDRED_FORTY_SEVENTH_115_FIELD_EDITION.tsv")
    resets = read("FOUR_HUNDRED_FORTY_SEVENTH_OWNER_RESETS.tsv")
    local = read("FOUR_HUNDRED_FORTY_SEVENTH_31_LOCAL_WHOLE_CARDS.tsv")
    reconciliation = read("FOUR_HUNDRED_FORTY_SEVENTH_VALUE_RECONCILIATION.tsv")
    checks = {
        "records_6": {row["record_unit_id"] for row in events} == {f"B{n}" for n in range(1, 7)},
        "events_281": len(events) == 281,
        "events_e101_e381": [row["event_id"] for row in events] == [f"E{n}" for n in range(101, 382)],
        "record_event_counts": [sum(row["record_unit_id"] == f"B{n}" for row in events) for n in range(1, 7)] == [66, 62, 86, 47, 11, 9],
        "fields_115": len(fields) == 115,
        "field_ids_f021_f135": [row["field_id"] for row in fields] == [f"F{n:03d}" for n in range(21, 136)],
        "statements_97": len(statements) == 97,
        "statement_record_counts": [sum(row["record_unit_id"] == f"B{n}" for row in statements) for n in range(1, 7)] == [21, 22, 34, 16, 3, 1],
        "dictionary_124": len(dictionary) == 124,
        "dictionary_unique": len({row["joint_tuple_id"] for row in dictionary}) == 124,
        "drawer_counts_87_6_31": [sum(row["union_drawer"] == drawer for row in dictionary) for drawer in ("PRODUCTIVE_COMPOSITION", "PORTABLE_LEARNED_WHOLE_CARD", "RECORD_LOCAL_LEARNED_WHOLE_CARD")] == [87, 6, 31],
        "local_31": len(local) == 31,
        "reconciliation_124": len(reconciliation) == 124,
        "no_value_collision": all(row["distinct_selected_values"] == "1" and row["collision"] == "NO" for row in reconciliation),
        "event_dictionary_values_agree": all(next(card for card in dictionary if card["joint_tuple_id"] == row["joint_tuple_id"])["small_value_de"] == row["small_value_de"] for row in events),
        "all_events_once_in_fields": sorted((event_id for row in fields for event_id in row["event_ids"].split("|")), key=lambda event_id: int(event_id[1:])) == [f"E{n}" for n in range(101, 382)],
        "all_events_once_in_statements": sorted((event_id for row in statements for event_id in row["event_ids"].split("|")), key=lambda event_id: int(event_id[1:])) == [f"E{n}" for n in range(101, 382)],
        "record_starts_6": sum(row["reset_kind"] == "RECORD_START" for row in resets) == 6,
        "b6_restart_e373": any(row["event_id"] == "E373" and row["reset_kind"] == "RECORD_START" and row["inherit_previous_state"] == "NO" for row in resets),
        "no_empty_values": all(row["small_value_de"].strip() for row in events),
        "fixed_pages_only": {row["page"] for row in events} == {"f81v", "f82r", "f83r"},
        "sealed_absent": all("f84" not in row["locus"].lower() for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_FORTY_SEVENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
