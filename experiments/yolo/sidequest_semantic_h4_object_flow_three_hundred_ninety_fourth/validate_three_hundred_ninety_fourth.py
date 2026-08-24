#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    trace = read("THREE_HUNDRED_NINETY_FOURTH_18_EVENT_OBJECT_TRACE.tsv")
    nodes = read("THREE_HUNDRED_NINETY_FOURTH_NINE_MATERIAL_NODES.tsv")
    edges = read("THREE_HUNDRED_NINETY_FOURTH_EIGHT_MATERIAL_EDGES.tsv")
    handoffs = read("THREE_HUNDRED_NINETY_FOURTH_THREE_STATEMENT_HANDOFFS.tsv")
    checks = {
        "eighteen_events": len(trace) == 18,
        "events_complete": {row["event_id"] for row in trace} == {f"E{number:03d}" for number in range(56, 74)},
        "nine_nodes": len(nodes) == 9,
        "eight_edges": len(edges) == 8,
        "three_handoffs": len(handoffs) == 3,
        "owner_constant": {row["owner_register"] for row in trace} == {"H4_PICTURED_PLANT"},
        "trace_continuity": all(trace[index]["active_after"] == trace[index + 1]["active_before"] for index in range(len(trace) - 1)),
        "four_statements": {row["statement_id"] for row in trace} == {"H4-S001", "H4-S002", "H4-S003", "H4-S004"},
        "all_cues": all(row["component_cue"] and row["working_reading_de"] for row in trace),
        "node_chain": all(edges[index]["from_node"] == nodes[index]["material_node"] and edges[index]["to_node"] == nodes[index + 1]["material_node"] for index in range(8)),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_NINETY_FOURTH_VALIDATION.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if status != "PASS":
        raise SystemExit(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
