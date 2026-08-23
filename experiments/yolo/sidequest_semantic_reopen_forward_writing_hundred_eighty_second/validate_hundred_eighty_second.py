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
    tokens = read("HUNDRED_EIGHTY_SECOND_19_TOKEN_REOPEN_ENCODING.tsv")
    fields = read("HUNDRED_EIGHTY_SECOND_3_FIELD_REOPEN_EXERCISE.tsv")
    states = read("HUNDRED_EIGHTY_SECOND_5_PACKET_STATE_TRACE.tsv")
    ambiguities = read("HUNDRED_EIGHTY_SECOND_7_LOCAL_AMBIGUITIES.tsv")
    rebuilt = " | ".join(
        " ".join(row["chosen_visible_surface"] for row in tokens if int(row["field"]) == field)
        for field in range(1, 4)
    )
    expected = " | ".join(row["visible_card_sequence"] for row in fields)
    field_one_slots = [row["grammar_slot"] for row in tokens if row["field"] == "1"]
    checks = {
        "nineteen_tokens": len(tokens) == 19 and [int(row["token_order"]) for row in tokens] == list(range(1, 20)),
        "seventeen_distinct_cards": len({row["master_card_id"] for row in tokens}) == 17,
        "all_registered_surfaces": {row["surface_is_registered"] for row in tokens} == {"YES"},
        "three_new_closed_fields": len(fields) == 3 and {row["sequence_source"] for row in fields} == {"NEW_COMPOSITION"} and {row["field_status"] for row in fields} == {"CLOSED"},
        "field_rebuild_exact": rebuilt == expected,
        "five_micro_packets": len(states) == 5 and sum(int(row["micro_packets"]) for row in fields) == 5,
        "two_internal_reopens": sum(row["reopen_before"] == "YES" for row in tokens) == 2 and sum(row["explicit_reopen"] == "YES" for row in states) == 2,
        "field_one_has_three_packets": [int(row["micro_packet"]) for row in tokens if row["field"] == "1"] == [1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 3, 3],
        "field_one_reopens_after_action": field_one_slots == ["G1", "G2", "G3", "G5", "G4", "G2", "G4", "G5", "G2", "G2", "G3", "G4"],
        "all_steps_roundtrip": all(row["source_instruction_de"] == row["decoded_step_de"] for row in tokens),
        "seven_ambiguities": len(ambiguities) == 7,
        "sealed_absent": all("f84" not in "\t".join(row.values()).lower() for table in [tokens, fields, states, ambiguities] for row in table),
    }
    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "visible_sequence": rebuilt,
        "decision": "MICRO_PACKET_REOPEN_IS_PRODUCTIVE_IN_NEW_COMPOSITION",
    }
    (HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
