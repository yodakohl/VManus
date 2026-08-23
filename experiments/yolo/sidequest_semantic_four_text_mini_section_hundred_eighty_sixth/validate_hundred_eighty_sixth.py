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
    tokens = read("HUNDRED_EIGHTY_SIXTH_73_TOKEN_MINI_SECTION.tsv")
    fields = read("HUNDRED_EIGHTY_SIXTH_18_FIELD_MINI_SECTION.tsv")
    handoffs = read("HUNDRED_EIGHTY_SIXTH_4_OWNER_HANDOFFS.tsv")
    states = read("HUNDRED_EIGHTY_SIXTH_18_FIELD_REGISTER_TRACE.tsv")
    sections = read("HUNDRED_EIGHTY_SIXTH_4_SECTION_SUMMARY.tsv")
    maximum_order = {}
    for row in tokens:
        maximum_order[row["global_field_id"]] = max(maximum_order.get(row["global_field_id"], 0), int(row["global_token_order"]))
    terminal_bad = [row for row in tokens if row["finality_rule"] == "ALWAYS_FIELD_FINAL" and int(row["global_token_order"]) != maximum_order[row["global_field_id"]]]
    checks = {
        "73_tokens": len(tokens) == 73 and [int(row["global_token_order"]) for row in tokens] == list(range(1, 74)),
        "45_distinct_cards": len({row["master_card_id"] for row in tokens}) == 45,
        "18_fields": len(fields) == 18 and [row["global_field_id"] for row in fields] == [f"N{i:02d}" for i in range(1, 19)],
        "field_event_counts": sum(int(row["event_count"]) for row in fields) == 73,
        "four_sections_13_19_16_25": [int(row["tokens"]) for row in sections] == [13, 19, 16, 25],
        "field_counts_5_3_5_5": [int(row["fields"]) for row in sections] == [5, 3, 5, 5],
        "20_micro_packets": sum(int(row["micro_packets"]) for row in fields) == 20,
        "three_open_fifteen_closed": Counter(row["field_status"] for row in fields) == Counter({"CLOSED": 15, "OPEN": 3}),
        "all_terminal_cards_final": not terminal_bad,
        "four_owner_handoffs": len(handoffs) == 4 and [row["handoff_id"] for row in handoffs] == [f"H{i}" for i in range(4)],
        "18_state_rows": len(states) == 18 and [row["global_field_id"] for row in states] == [f"N{i:02d}" for i in range(1, 19)],
        "a_to_c_explicit_previous": next(row for row in handoffs if row["handoff_id"] == "H1")["visible_carrier"] == "dchol",
        "c_to_b_stored_previous": next(row for row in handoffs if row["handoff_id"] == "H2")["visible_carrier"] == "talam dchol",
        "b_to_d_owner_reset_marked": next(row for row in handoffs if row["handoff_id"] == "H3")["handoff_type"] == "OWNER_RESET_REQUIRES_MASTER_OR_PICTURE",
        "all_six_slots": {row["grammar_slot"] for row in tokens} == {f"G{i}" for i in range(1, 7)},
        "sealed_absent": all("f84" not in "\t".join(row.values()).lower() for table in [tokens, fields, handoffs, states, sections] for row in table),
    }
    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "decision": "FOUR_GENERATED_TEXTS_FORM_ONE_EXPLICITLY_HANDED_OFF_MINI_SECTION",
    }
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
