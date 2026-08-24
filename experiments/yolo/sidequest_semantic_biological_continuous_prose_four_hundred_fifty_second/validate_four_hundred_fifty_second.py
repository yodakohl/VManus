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
    procedures = read("FOUR_HUNDRED_FIFTY_SECOND_24_PROCEDURES.tsv")
    statements = read("FOUR_HUNDRED_FIFTY_SECOND_97_STATEMENT_LEDGER.tsv")
    transitions = read("FOUR_HUNDRED_FIFTY_SECOND_SEVEN_SCENE_TRANSITIONS.tsv")
    checks = {
        "procedures_24": len(procedures) == 24,
        "records_6": {row["record_unit_id"] for row in procedures} == {f"B{n}" for n in range(1, 7)},
        "procedure_counts_5_5_7_5_1_1": [sum(row["record_unit_id"] == f"B{n}" for row in procedures) for n in range(1, 7)] == [5, 5, 7, 5, 1, 1],
        "statements_97": len(statements) == 97,
        "statement_ids_unique": len({row["statement_id"] for row in statements}) == 97,
        "statement_record_counts": [sum(row["record_unit_id"] == f"B{n}" for row in statements) for n in range(1, 7)] == [21, 22, 34, 16, 3, 1],
        "events_281": sum(int(row["events"]) for row in procedures) == 281,
        "event_ids_once": sorted((event_id for row in procedures for event_id in row["event_ids"].split("|")), key=lambda event_id: int(event_id[1:])) == [f"E{n}" for n in range(101, 382)],
        "transitions_7": len(transitions) == 7,
        "transition_ids_exact": {row["event_id"] for row in transitions} == {"E189", "E198", "E203", "E212", "E264", "E291", "E356"},
        "inside_statement_transitions_4": sum(row["inside_statement"] == "YES" for row in transitions) == 4,
        "line_end_never_rule": all(row["reading_rule"] == "DO_NOT_END_SENTENCE; CHANGE_VISIBLE_OWNER_ONLY" for row in transitions),
        "no_empty_prose": all(row["continuous_workshop_prose_de"].strip() for row in procedures),
        "sealed_absent": all("f84" not in row["continuous_workshop_prose_de"].lower() for row in procedures),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_FIFTY_SECOND_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
