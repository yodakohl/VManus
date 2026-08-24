#!/usr/bin/env python3

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def rows(name):
    with (HERE / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


dialogue = rows("THREE_HUNDRED_FORTY_EIGHTH_47_DIALOGUE_TURNS.tsv")
errors = rows("THREE_HUNDRED_FORTY_EIGHTH_FIVE_APPRENTICE_ERRORS.tsv")
event_ids = [event for row in dialogue for event in row["event_ids"].split("|")]
checks = {
    "forty_seven_turns": len(dialogue) == 47 and [int(row["turn"]) for row in dialogue] == list(range(1, 48)),
    "seventy_nine_events": len(event_ids) == 79 and len(set(event_ids)) == 79,
    "twenty_six_statements": len({row["statement_id"] for row in dialogue}) == 26,
    "two_records": {row["record_unit_id"] for row in dialogue} == {"H3", "B2"},
    "all_backreadings_match": all(row["identity_value_slot_thread_match"] == "YES" for row in dialogue),
    "all_master_prompts_concrete": all(row["master_dictation_de"] for row in dialogue),
    "all_apprentice_answers_concrete": all(row["apprentice_surface_answer"] and row["apprentice_explanation_de"] for row in dialogue),
    "five_error_lessons": len(errors) == 5 and len({row["layer"] for row in errors}) == 5,
}
result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
(HERE / "THREE_HUNDRED_FORTY_EIGHTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
if result["status"] != "PASS":
    raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
print("PASS", len(checks), "checks")
