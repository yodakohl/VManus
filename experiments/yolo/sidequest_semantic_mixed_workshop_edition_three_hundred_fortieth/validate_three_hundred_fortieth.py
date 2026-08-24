#!/usr/bin/env python3

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def rows(name):
    with (HERE / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


events = rows("THREE_HUNDRED_FORTIETH_381_MIXED_HAND_EVENTS.tsv")
statements = rows("THREE_HUNDRED_FORTIETH_116_MIXED_HAND_STATEMENTS.tsv")
records = rows("THREE_HUNDRED_FORTIETH_ELEVEN_RECORD_ASSIGNMENTS.tsv")
profiles = rows("THREE_HUNDRED_FORTIETH_FOUR_LOCAL_HAND_PROFILES.tsv")
handoffs = rows("THREE_HUNDRED_FORTIETH_FIVE_HANDOFF_RELAYS.tsv")
checks = {
    "four_hands": len(profiles) == 4 and len({row["hand_id"] for row in profiles}) == 4,
    "eleven_records": len(records) == 11 and len({row["record_unit_id"] for row in records}) == 11,
    "seven_pages": len({row["page"] for row in events}) == 7,
    "all_381_events": len(events) == 381 and len({row["event_id"] for row in events}) == 381,
    "all_116_statements": len(statements) == 116 and len({row["statement_id"] for row in statements}) == 116,
    "record_event_counts": sum(int(row["event_count"]) for row in records) == 381,
    "record_statement_counts": sum(int(row["statement_count"]) for row in records) == 116,
    "all_identity_matches": all(row["identity_match"] == "YES" for row in events),
    "all_values_slots_boundaries": all(row["value_preserved"] == row["slot_preserved"] == row["boundary_preserved"] == "YES" for row in events),
    "four_same_hand_handoffs": sum(row["handoff_mode"] == "SAME_HAND_CONTINUATION" for row in handoffs) == 4,
    "one_cross_hand_relay": sum(row["handoff_mode"] == "CROSS_HAND_WORKSHOP_RELAY" for row in handoffs) == 1,
    "relay_identity_preserved": all(row["identity_value_preserved_across_hands"] == "YES" for row in handoffs),
    "fixed_pages_only": {row["page"] for row in events} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
    "sealed_absent": all(row["page"] not in {"f84", "f84r"} for row in events),
}
result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
(HERE / "THREE_HUNDRED_FORTIETH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
if result["status"] != "PASS":
    raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
print("PASS", len(checks), "checks")
