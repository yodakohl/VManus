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
    tokens = read("HUNDRED_EIGHTIETH_29_TOKEN_SLOT_PARSE.tsv")
    slots = read("HUNDRED_EIGHTIETH_6_SHARED_SLOTS.tsv")
    registers = read("HUNDRED_EIGHTIETH_4_STATE_REGISTERS.tsv")
    fields = read("HUNDRED_EIGHTIETH_9_FIELD_GRAMMAR_TRACES.tsv")
    states = read("HUNDRED_EIGHTIETH_9_FIELD_STATE_TRACES.tsv")
    exercises = sorted({row["exercise"] for row in tokens})
    cards_by_exercise = {
        exercise: {row["master_card_id"] for row in tokens if row["exercise"] == exercise}
        for exercise in exercises
    }
    rebuilt = {
        exercise: [
            " ".join(row["surface"] for row in tokens if row["exercise"] == exercise and int(row["field"]) == field)
            for field in sorted({int(row["field"]) for row in tokens if row["exercise"] == exercise})
        ]
        for exercise in exercises
    }
    table_fields = {
        exercise: [row["visible_sequence"] for row in fields if row["exercise"] == exercise]
        for exercise in exercises
    }
    checks = {
        "twenty_nine_tokens": len(tokens) == 29 and [int(row["global_token_order"]) for row in tokens] == list(range(1, 30)),
        "thirteen_plus_sixteen": [sum(row["exercise"] == exercise for row in tokens) for exercise in exercises] == [13, 16],
        "twenty_four_card_union": len({row["master_card_id"] for row in tokens}) == 24,
        "exact_three_card_overlap": set.intersection(*cards_by_exercise.values()) == {"MC026", "MC142", "MC147"},
        "six_slots": [row["slot_id"] for row in slots] == [f"G{i}" for i in range(1, 7)],
        "every_token_has_one_slot": all(row["grammar_slot"] in {slot["slot_id"] for slot in slots} for row in tokens),
        "both_exercises_use_all_slots": all({row["grammar_slot"] for row in tokens if row["exercise"] == exercise} == {slot["slot_id"] for slot in slots} for exercise in exercises),
        "four_registers": len(registers) == 4 and len({row["register_id"] for row in registers}) == 4,
        "nine_fields": len(fields) == 9 and [sum(row["exercise"] == exercise for row in fields) for exercise in exercises] == [5, 4],
        "field_sequences_rebuild": rebuilt == table_fields,
        "nine_state_traces": len(states) == 9 and {(row["exercise"], row["field"]) for row in states} == {(row["exercise"], row["field"]) for row in fields},
        "loop_and_branch_present": any(row["visible_sequence"] == "shckhedy" for row in fields) and any("ykain" in row["visible_sequence"] for row in fields) and any("ykan" in row["visible_sequence"] for row in fields),
        "no_new_semantic_cards": all(row["dictionary_value_de"] for row in tokens),
        "sealed_absent": all("f84" not in "\t".join(row.values()).lower() for table in [tokens, slots, registers, fields, states] for row in table),
    }
    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "grammar": "G1 context -> G2 selection -> G3 condition -> G4 operation / G5 target -> G6 commit",
        "note": "G4 and G5 may exchange order when a learned action card already carries its target relation.",
    }
    (HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
