#!/usr/bin/env python3

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def rows(name):
    with (HERE / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


events = rows("THREE_HUNDRED_FORTY_SIXTH_381_TWO_LAYER_EVENT_TRACE.tsv")
matrix = rows("THREE_HUNDRED_FORTY_SIXTH_30_STATE_SLOT_MATRIX.tsv")
links = rows("THREE_HUNDRED_FORTY_SIXTH_41_STATE_LINK_MICROCYCLE_RELATIONS.tsv")
statements = rows("THREE_HUNDRED_FORTY_SIXTH_116_TWO_LAYER_STATEMENTS.tsv")
checks = {
    "all_381_events": len(events) == 381 and len({row["event_id"] for row in events}) == 381,
    "all_116_statements": len(statements) == 116,
    "thirty_matrix_cells": len(matrix) == 30,
    "seventy_nine_markers": sum(row["material_marker_state"] != "NONE" for row in events) == 79,
    "seventy_three_default_slot_fits": sum(row["material_marker_state"] != "NONE" and row["slot_code"] == next(cell["slot_code"] for cell in matrix if cell["state_id"] == row["material_marker_state"] and cell["dominant_slot_for_state"] == "YES") for row in events) == 73,
    "six_slot_override_events": sum(int(row["event_count"]) for row in matrix if row["teaching_action"] == "MEMORIZE_WHOLE_CARD_OVERRIDE") == 6,
    "all_mass_markers_in_s2": all(row["slot_code"] == "S2_MATERIAL_MASS" for row in events if row["material_marker_state"] == "M4_MEASURED_PORTION"),
    "forty_one_links": len(links) == 41,
    "nineteen_same_cycle": sum(row["microcycle_relation"] == "SAME_MICROCYCLE" for row in links) == 19,
    "twenty_two_cross_cycle": sum(row["microcycle_relation"] == "CROSSES_MICROCYCLE_RESET" for row in links) == 22,
    "fixed_pages_only": {row["page"] for row in events} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
    "sealed_absent": all(row["page"] not in {"f84", "f84r"} for row in events),
}
result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
(HERE / "THREE_HUNDRED_FORTY_SIXTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
if result["status"] != "PASS":
    raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
print("PASS", len(checks), "checks")
