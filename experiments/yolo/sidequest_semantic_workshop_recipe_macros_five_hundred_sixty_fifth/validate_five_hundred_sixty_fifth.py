#!/usr/bin/env python3
import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    phases = read("FIVE_HUNDRED_SIXTY_FIFTH_TEN_WORKSHOP_PHASES.tsv")
    macros = read("FIVE_HUNDRED_SIXTY_FIFTH_RECURRENT_MACRO_DECK.tsv")
    statements = read("FIVE_HUNDRED_SIXTY_FIFTH_ONE_HUNDRED_SIXTEEN_MACRO_MAP.tsv")
    events = read("FIVE_HUNDRED_SIXTY_FIFTH_THREE_HUNDRED_EIGHTY_ONE_PHASE_EVENTS.tsv")
    frequencies = Counter(row["phase_signature"] for row in statements)
    checks = {
        "ten_phases": len(phases) == 10 and len({row["phase"] for row in phases}) == 10,
        "events381": len(events) == 381 and len({row["event_id"] for row in events}) == 381,
        "actions237": sum(row["event_role"] == "ACTION" for row in events) == 237,
        "arguments144": sum(row["event_role"] == "ARGUMENT_OR_STATE" for row in events) == 144,
        "statements116": len(statements) == 116 and len({row["statement_id"] for row in statements}) == 116,
        "macros_are_recurrent": all(int(row["statements"]) >= 2 and frequencies[row["phase_signature"]] == int(row["statements"]) for row in macros),
        "unique_are_composed": all((frequencies[row["phase_signature"]] >= 2) == (row["macro_status"] == "TAUGHT_RECURRENT_MACRO") for row in statements),
        "macro_refs": {row["macro_id"] for row in statements if row["macro_id"] != "NONE"} == {row["macro_id"] for row in macros},
        "actions_preserved": all(row["actions_preserved"] == "YES" for row in statements),
        "phase_assignments": all(row["phase_assignment_complete"] == "YES" and row["workshop_phase"].strip() for row in events),
        "fixed_pages": {row["page"] for row in events} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "seal_absent": all(not row["page"].lower().startswith("f84") for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_SIXTY_FIFTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for name, value in checks.items():
        print(f"{name}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
