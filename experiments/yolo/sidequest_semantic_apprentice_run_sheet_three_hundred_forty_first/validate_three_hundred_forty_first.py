#!/usr/bin/env python3

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

with (HERE / "THREE_HUNDRED_FORTY_FIRST_ELEVEN_APPRENTICE_RUN_CARDS.tsv").open(newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle, delimiter="\t"))
checks = {
    "eleven_run_cards": len(rows) == 11 and len({row["record_unit_id"] for row in rows}) == 11,
    "all_381_events": sum(int(row["event_count"]) for row in rows) == 381,
    "all_116_statements": sum(int(row["statement_count"]) for row in rows) == 116,
    "all_205_microcycles": sum(int(row["microcycle_count"]) for row in rows) == 205,
    "five_deliveries": sum(row["receiver_or_shelf"].startswith("B") for row in rows) == 5,
    "six_terminal_shelves": sum(row["receiver_or_shelf"].startswith("TERMINAL") for row in rows) == 6,
    "all_inputs_outputs_concrete": all(row["input_item_de"] and row["output_item_de"] for row in rows),
    "all_preserved": all(row["identity_value_owner_slot_boundary_preserved"] == "YES" for row in rows),
    "four_hands_used": len({row["assigned_hand"] for row in rows}) == 4,
    "fixed_pages_only": {row["page"] for row in rows} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
    "sealed_absent": all(row["page"] not in {"f84", "f84r"} for row in rows),
}
result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
(HERE / "THREE_HUNDRED_FORTY_FIRST_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
if result["status"] != "PASS":
    raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
print("PASS", len(checks), "checks")
