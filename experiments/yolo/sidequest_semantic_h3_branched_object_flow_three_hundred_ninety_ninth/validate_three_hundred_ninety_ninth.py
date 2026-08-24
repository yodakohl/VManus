#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    trace = read("THREE_HUNDRED_NINETY_NINTH_17_EVENT_BRANCH_TRACE.tsv")
    nodes = read("THREE_HUNDRED_NINETY_NINTH_12_MATERIAL_NODES.tsv")
    edges = read("THREE_HUNDRED_NINETY_NINTH_11_BRANCH_EDGES.tsv")
    contrast = read("THREE_HUNDRED_NINETY_NINTH_H3_H4_OBJECT_FLOW_CONTRAST.tsv")
    checks = {
        "seventeen_events": len(trace) == 17,
        "events_complete": {row["event_id"] for row in trace} == {f"E{number:03d}" for number in range(39, 56)},
        "four_statements": {row["statement_id"] for row in trace} == {"H3-S001", "H3-S002", "H3-S003", "H3-S004"},
        "branch_counts": Counter(row["branch"] for row in trace) == {"MAIN": 7, "RESERVED_SECOND_USE": 10},
        "twelve_nodes": len(nodes) == 12,
        "eleven_edges": len(edges) == 11,
        "two_root_edges": sum(row["from_node"] == "OWNER_PLANT" for row in edges) == 2,
        "reserved_edge": any(row["relation"] == "RESERVE_BRANCH" for row in edges),
        "two_contrast_rows": len(contrast) == 2,
        "owner_constant": {row["owner"] for row in trace} == {"H3_PICTURED_PLANT"},
        "all_readings": all(row["working_reading_de"] for row in trace),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_NINETY_NINTH_VALIDATION.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if status != "PASS":
        raise SystemExit(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
