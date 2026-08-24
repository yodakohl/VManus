#!/usr/bin/env python3

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def rows(name):
    with (HERE / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


programs = rows("THREE_HUNDRED_THIRTY_FOURTH_12_PROGRAM_PREPARATION_COMPARISON.tsv")
events = rows("THREE_HUNDRED_THIRTY_FOURTH_100_HERBAL_PROGRAM_EVENTS.tsv")
statements = rows("THREE_HUNDRED_THIRTY_FOURTH_19_HERBAL_PROGRAM_STATEMENTS.tsv")
handoffs = rows("THREE_HUNDRED_THIRTY_FOURTH_FIVE_PROGRAM_HANDOFFS.tsv")
checks = {
    "twelve_programs": len(programs) == 12,
    "eleven_begin_in_herbal": sum(int(row["herbal_event_count"]) > 0 for row in programs) == 11,
    "one_bio_introduction": sum(row["workflow_status"] == "INTRODUCED_AT_BIO_STATION" for row in programs) == 1,
    "one_hundred_herbal_events": len(events) == 100 and len({row["event_id"] for row in events}) == 100,
    "event_counts_reconcile": sum(int(row["herbal_event_count"]) for row in programs) == 100,
    "nineteen_statements": len(statements) == 19 and len({row["statement_id"] for row in statements}) == 19,
    "five_handoffs": len(handoffs) == 5 and len({row["herbal_record"] for row in handoffs}) == 5,
    "every_handoff_carries_program": all(row["programs_carried_across"] for row in handoffs),
    "no_empty_program": all(row["program_id"] for row in events),
    "fixed_pages_only": {row["page"] for row in events} == {"f10r", "f11r", "f55v", "f56r"},
    "sealed_absent": all(row["page"] not in {"f84", "f84r"} for row in events),
}
result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
(HERE / "THREE_HUNDRED_THIRTY_FOURTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
if result["status"] != "PASS":
    raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
print("PASS", len(checks), "checks")
