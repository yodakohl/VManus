#!/usr/bin/env python3

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def rows(name):
    with (HERE / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


states = rows("THREE_HUNDRED_FORTY_THIRD_FIVE_MATERIAL_STATES.tsv")
transitions = rows("THREE_HUNDRED_FORTY_THIRD_ELEVEN_STATE_TRANSITIONS.tsv")
edges = rows("THREE_HUNDRED_FORTY_THIRD_EIGHT_UNIQUE_STATE_EDGES.tsv")
checks = {
    "five_states": len(states) == 5 and len({row["state_id"] for row in states}) == 5,
    "eleven_transitions": len(transitions) == 11 and len({row["record_unit_id"] for row in transitions}) == 11,
    "eight_unique_edges": len(edges) == 8,
    "two_continuation_loops": sum(row["edge_type"] == "CONTINUATION_LOOP" for row in edges) == 2,
    "no_return_to_raw": all(row["target_state_id"] != "M1_RAW_PART" for row in edges),
    "main_path_present": {("M1_RAW_PART", "M2_PREPARATION"), ("M2_PREPARATION", "M4_MEASURED_PORTION"), ("M2_PREPARATION", "M5_APPLICATION_ITEM")} <= {(row["source_state_ids"], row["target_state_id"]) for row in edges},
    "no_new_card_gloss": all(row["new_card_gloss_added"] == "NO" for row in transitions),
    "all_four_hands": len({row["assigned_hand"] for row in transitions}) == 4,
    "fixed_pages_only": {row["page"] for row in transitions} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
    "sealed_absent": all(row["page"] not in {"f84", "f84r"} for row in transitions),
}
result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
(HERE / "THREE_HUNDRED_FORTY_THIRD_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
if result["status"] != "PASS":
    raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
print("PASS", len(checks), "checks")
