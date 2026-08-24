#!/usr/bin/env python3
"""Validate the complete 57-line master dictation."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    lines = read_tsv("THREE_HUNDRED_FIFTY_NINTH_FIFTY_SEVEN_LINE_MASTER_DICTATION.tsv")
    records = read_tsv("THREE_HUNDRED_FIFTY_NINTH_ELEVEN_RECORD_DICTATION_SUMMARY.tsv")
    decisions = Counter(row["decision_to_next_line"] for row in lines)
    checks = {
        "57_lines": len(lines) == 57,
        "11_records": len(records) == 11 and len({row["record_unit_id"] for row in records}) == 11,
        "381_visible_events": sum(int(row["visible_event_count"]) for row in lines) == 381,
        "380_source_instructions": sum(int(row["source_instruction_count"]) for row in lines) == 380,
        "116_statements": sum(int(row["statements"]) for row in records) == 116,
        "line_counts_match_records": sum(int(row["physical_lines"]) for row in records) == 57,
        "event_counts_match_records": sum(int(row["visible_events"]) for row in records) == 381,
        "source_counts_match_records": sum(int(row["source_instructions"]) for row in records) == 380,
        "transition_decisions_6_1_39_11": decisions == {"CONTINUE_ACROSS_LINE": 6, "READ_ONCE_CARRY": 1, "REAL_CYCLE_OR_OWNER_RESET": 39, "RECORD_END": 11},
        "one_anticipation_line": sum(row["anticipation_surfaces"] != "NONE" for row in lines) == 1,
        "anticipation_not_spoken_twice": next(row for row in lines if row["anticipation_surfaces"] != "NONE")["source_instruction_count"] == str(int(next(row for row in lines if row["anticipation_surfaces"] != "NONE")["visible_event_count"]) - 1),
        "all_have_owner_state_instruction_surface": all(row["owner_sequence"] and row["incoming_state"] and row["master_instruction_de"] and row["visible_surfaces"] and row["outgoing_state"] for row in lines),
        "fixed_pages_only": {row["page"] for row in lines} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_FIFTY_NINTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit("validation failed")
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
