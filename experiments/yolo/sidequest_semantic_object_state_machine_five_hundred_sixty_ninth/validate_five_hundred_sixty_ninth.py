#!/usr/bin/env python3
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    states = read("FIVE_HUNDRED_SIXTY_NINTH_SIX_OBJECT_STATES.tsv")
    transitions = read("FIVE_HUNDRED_SIXTY_NINTH_ONE_HUNDRED_SIXTEEN_TRANSITIONS.tsv")
    records = read("FIVE_HUNDRED_SIXTY_NINTH_ELEVEN_RECORD_FLOWS.tsv")
    events = read("FIVE_HUNDRED_SIXTY_NINTH_THREE_HUNDRED_EIGHTY_ONE_STATE_EVENTS.tsv")
    state_set = {row["state"] for row in states}
    checks = {
        "states6": len(states) == 6 and len(state_set) == 6,
        "transitions116": len(transitions) == 116 and len({row["statement_id"] for row in transitions}) == 116,
        "records11": len(records) == 11 and sum(int(row["statements"]) for row in records) == 116,
        "events381": len(events) == 381 and len({row["event_id"] for row in events}) == 381,
        "valid_states": all(row["input_object"] in state_set and row["output_object"] in state_set for row in transitions),
        "complete_transitions": all(row["transition_complete"] == "YES" and row["transition_path"].strip() for row in transitions),
        "state_event_binding": all(row["state_binding_complete"] == "YES" and row["input_object"] in state_set and row["output_object"] in state_set for row in events),
        "record_starts": all(any(row["record"] == record["record"] and "RECORD_START" in row["reset_reason"] for row in transitions) for record in records),
        "fixed_pages": {row["page"] for row in events} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "seal_absent": all(not row["page"].lower().startswith("f84") for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_SIXTY_NINTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for name, value in checks.items():
        print(f"{name}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
