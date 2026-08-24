#!/usr/bin/env python3
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    statements = read("FIVE_HUNDRED_EIGHTY_FIFTH_CORRECTED_ONE_HUNDRED_SIXTEEN_FULL_STATEMENTS.tsv")
    events = read("FIVE_HUNDRED_EIGHTY_FIFTH_CORRECTED_THREE_HUNDRED_EIGHTY_ONE_EVENT_BINDING.tsv")
    masters = read("FIVE_HUNDRED_EIGHTY_FIFTH_TWELVE_FREE_MASTER_EXAMPLES.tsv")
    checks = {
        "statements116": len(statements) == 116 and len({r["statement_id"] for r in statements}) == 116,
        "events381": len(events) == 381 and len({r["event_id"] for r in events}) == 381,
        "action237_argument144": sum(int(r["action_events"]) for r in statements) == 237 and sum(int(r["argument_state_events"]) for r in statements) == 144,
        "event_sum381": sum(int(r["event_total"]) for r in statements) == 381,
        "all_spoken": all(r["all_events_spoken"] == "YES" and r["corrected_full_compact_instruction_de"] for r in statements),
        "event_binding_complete": all(r["complete_meaning"] == "YES" and r["corrected_full_compact_instruction_de"] for r in events),
        "masters12": len(masters) == 12 and all(r["formula_mode"] == "FREE_COMPOSITION" for r in masters),
        "supersedes580": all(r["supersedes_pass580_first_event_only"] == "YES" for r in statements),
        "fixed_pages": {r["page"] for r in events} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "seal_absent": all(not r["page"].lower().startswith("f84") for r in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_EIGHTY_FIFTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
