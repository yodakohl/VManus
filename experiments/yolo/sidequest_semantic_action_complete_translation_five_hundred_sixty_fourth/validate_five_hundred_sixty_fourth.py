#!/usr/bin/env python3
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    events = read("FIVE_HUNDRED_SIXTY_FOURTH_THREE_HUNDRED_EIGHTY_ONE_EVENT_READINGS.tsv")
    statements = read("FIVE_HUNDRED_SIXTY_FOURTH_ONE_HUNDRED_SIXTEEN_ACTION_COMPLETE_STATEMENTS.tsv")
    records = read("FIVE_HUNDRED_SIXTY_FOURTH_ELEVEN_ACTION_COMPLETE_RECORDS.tsv")
    checks = {
        "events381": len(events) == 381 and len({row["event_id"] for row in events}) == 381,
        "actions237": sum(row["event_role"] == "ACTION" for row in events) == 237,
        "arguments144": sum(row["event_role"] == "ARGUMENT_OR_STATE" for row in events) == 144,
        "statements116": len(statements) == 116 and len({row["statement_id"] for row in statements}) == 116,
        "statement_event_sum": sum(int(row["action_events"]) + int(row["argument_state_events"]) for row in statements) == 381,
        "records11": len(records) == 11 and sum(int(row["statements"]) for row in records) == 116,
        "record_event_sum": sum(int(row["action_events"]) + int(row["argument_state_events"]) for row in records) == 381,
        "all_spoken": all(row["meaning_preserved"] == "YES" and row["revised_event_reading_de"].strip() for row in events) and all(row["all_events_spoken"] == "YES" for row in statements),
        "fixed_pages": {row["page"] for row in events} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "seal_absent": all(not row["page"].lower().startswith("f84") for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_SIXTY_FOURTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for name, value in checks.items():
        print(f"{name}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
