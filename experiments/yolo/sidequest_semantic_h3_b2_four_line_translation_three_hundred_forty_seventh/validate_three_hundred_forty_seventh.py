#!/usr/bin/env python3

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def rows(name):
    with (HERE / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


events = rows("THREE_HUNDRED_FORTY_SEVENTH_79_EVENT_FOUR_LINE_INTERLINEAR.tsv")
statements = rows("THREE_HUNDRED_FORTY_SEVENTH_26_SYNCHRONIZED_STATEMENTS.tsv")
anchor = rows("THREE_HUNDRED_FORTY_SEVENTH_EXACT_KLARAUSZUG_HANDOFF.tsv")
checks = {
    "two_records": {row["record_unit_id"] for row in events} == {"H3", "B2"},
    "seventy_nine_events": len(events) == 79 and len({row["event_id"] for row in events}) == 79,
    "twenty_six_statements": len(statements) == 26 and len({row["statement_id"] for row in statements}) == 26,
    "forty_seven_microcycles": sum(int(row["microcycle_count"]) for row in statements) == 47,
    "twelve_material_markers": sum(row["material_marker_state"] != "NONE" for row in events) == 12,
    "one_hand": {row["hand_id"] for row in events} == {"HAND_B_Q_OPERATIONAL"},
    "one_exact_anchor": len(anchor) == 1 and anchor[0]["atomic_value_de"] == "Klarauszug",
    "anchor_preserved": anchor[0]["same_hand"] == anchor[0]["identity_and_value_preserved"] == "YES",
    "no_empty_lines": all(all(row[key] for key in ("surface_line", "atomic_value_line", "material_owner_line", "slot_line", "fluent_german_line")) for row in statements),
    "fixed_pages_only": {row["page"] for row in events} == {"f11r", "f82r"},
    "sealed_absent": all(row["page"] not in {"f84", "f84r"} for row in events),
}
result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
(HERE / "THREE_HUNDRED_FORTY_SEVENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
if result["status"] != "PASS":
    raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
print("PASS", len(checks), "checks")
