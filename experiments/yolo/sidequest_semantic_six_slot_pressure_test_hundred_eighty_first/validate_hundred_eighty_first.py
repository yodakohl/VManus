#!/usr/bin/env python3
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
    events = read("HUNDRED_EIGHTY_FIRST_381_EVENT_SIX_SLOT_PARSE.tsv")
    fields = read("HUNDRED_EIGHTY_FIRST_135_FIELD_PRESSURE_TEST.tsv")
    statements = read("HUNDRED_EIGHTY_FIRST_116_STATEMENT_PRESSURE_TEST.tsv")
    restarts = read("HUNDRED_EIGHTY_FIRST_34_PACKET_RESTARTS.tsv")
    rules = read("HUNDRED_EIGHTY_FIRST_5_GRAMMAR_REVISIONS.tsv")
    packet_histogram = Counter(int(row["micro_packets"]) for row in fields)
    checks = {
        "381_events_once": len(events) == 381 and [row["event_id"] for row in events] == [f"E{i:03d}" for i in range(1, 382)],
        "135_fields_once": len(fields) == 135 and len({row["field_id"] for row in fields}) == 135,
        "116_statements_once": len(statements) == 116 and len({row["statement_id"] for row in statements}) == 116,
        "event_field_counts_reconcile": sum(int(row["event_count"]) for row in fields) == 381,
        "event_statement_counts_reconcile": sum(int(row["event_count"]) for row in statements) == 381,
        "all_six_slots_used": {row["primary_grammar_slot"] for row in events} == {f"G{i}" for i in range(1, 7)},
        "all_events_have_value": all(row["atomic_value_de"] for row in events),
        "169_micro_packets": sum(int(row["micro_packets"]) for row in fields) == 169,
        "34_restarts": len(restarts) == 34 and sum(int(row["restart_count"]) for row in fields) == 34,
        "field_packet_histogram": packet_histogram == Counter({1: 107, 2: 24, 3: 2, 4: 2}),
        "13_target_action_swaps": sum(int(row["target_before_operation_swaps"]) for row in fields) == 13,
        "89_field_final_closes": sum(int(row["close_count"]) for row in fields) == 89 and {row["close_is_field_final"] for row in fields} == {"YES"},
        "no_seventh_slot": {row["grammar_result"] for row in fields} == {"FITS_SIX_SLOTS_WITHOUT_SEVENTH"} and {row["six_slot_result"] for row in statements} == {"PASS_NO_SEVENTH_SLOT"},
        "five_revision_rules": [row["rule_id"] for row in rules] == [f"C{i}" for i in range(1, 6)],
        "sealed_absent": all("f84" not in "\t".join(row.values()).lower() for table in [events, fields, statements, restarts, rules] for row in table),
    }
    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "decision": "KEEP_SIX_SEMANTIC_SLOTS__ADD_MICRO_PACKET_REOPEN_CONTROL",
    }
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
