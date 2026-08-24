#!/usr/bin/env python3

import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent


def rows(name):
    with (HERE / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


slots = rows("THREE_HUNDRED_THIRTY_FIFTH_6_SLOT_SYNTAX.tsv")
trace = rows("THREE_HUNDRED_THIRTY_FIFTH_381_EVENT_GENERATION_TRACE.tsv")
statements = rows("THREE_HUNDRED_THIRTY_FIFTH_116_STATEMENT_SYNTAX.tsv")
micro = rows("THREE_HUNDRED_THIRTY_FIFTH_205_MICROCYCLES.tsv")
by_statement = defaultdict(list)
for row in trace:
    by_statement[row["statement_id"]].append(row)
monotone = True
for row in micro:
    ranks = [int(part.split("_")[0][1:]) for part in row["slot_sequence"].split(" → ")]
    monotone &= ranks == sorted(ranks)
checks = {
    "six_slots": len(slots) == 6,
    "twelve_programs_once": sum(len(row["program_ids"].split("|")) for row in slots) == 12,
    "all_381_events": len(trace) == 381 and len({row["event_id"] for row in trace}) == 381,
    "all_116_statements": len(statements) == 116 and len(by_statement) == 116,
    "event_counts_reconcile": sum(int(row["event_count"]) for row in statements) == 381,
    "exactly_205_microcycles": len(micro) == 205 and sum(int(row["microcycle_count"]) for row in statements) == 205,
    "all_microcycles_monotone": monotone,
    "every_statement_ends_once": sum(row["statement_end_after_event"] == "YES" for row in trace) == 116,
    "sixty_three_single_cycle": sum(int(row["microcycle_count"]) == 1 for row in statements) == 63,
    "maximum_six_cycles": max(int(row["microcycle_count"]) for row in statements) == 6,
    "fixed_pages_only": {row["page"] for row in trace} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
    "sealed_absent": all(row["page"] not in {"f84", "f84r"} for row in trace),
}
result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
(HERE / "THREE_HUNDRED_THIRTY_FIFTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
if result["status"] != "PASS":
    raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
print("PASS", len(checks), "checks")
