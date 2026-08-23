#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent
ARTIFACTS = [
    "TWO_HUNDRED_THIRTY_SECOND_NINE_GRAPH_NODES.tsv",
    "TWO_HUNDRED_THIRTY_SECOND_TEN_GRAPH_EDGES.tsv",
    "TWO_HUNDRED_THIRTY_SECOND_ONE_HUNDRED_FIFTY_THREE_EVENTS.tsv",
    "TWO_HUNDRED_THIRTY_SECOND_FIFTY_FOUR_STATEMENTS.tsv",
    "TWO_HUNDRED_THIRTY_SECOND_READABLE_LOCAL_GRAPH.md",
    "TWO_HUNDRED_THIRTY_SECOND_REPORT.md",
    "BUILD_SUMMARY.json",
]


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def hashes() -> dict[str, str]:
    return {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in ARTIFACTS}


def main() -> None:
    nodes = read(ARTIFACTS[0])
    edges = read(ARTIFACTS[1])
    events = read(ARTIFACTS[2])
    statements = read(ARTIFACTS[3])
    readable = (OUT / ARTIFACTS[4]).read_text(encoding="utf-8")
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "nine_nodes": len(nodes) == 9 and {row["node_id"] for row in nodes} == {f"N{i}" for i in range(1, 10)},
        "ten_edges": len(edges) == 10,
        "one_hundred_fifty_three_events": len(events) == 153 and len({row["event_id"] for row in events}) == 153,
        "exact_event_bounds": {row["event_id"] for row in events} == {f"E{i:03d}" for i in range(229, 382)},
        "fifty_four_statements": len(statements) == 54 and len({row["statement_id"] for row in statements}) == 54,
        "all_events_once_in_statements": sorted(event for row in statements for event in row["event_ids"].split("|")) == sorted(row["event_id"] for row in events),
        "three_owner_break_statements": {row["statement_id"] for row in statements if int(row["owner_break_count"]) > 0} == {"B3-S016", "B3-S026", "B4-S015"},
        "two_direct_visible_edges": sum(row["edge_class"] == "VISIBLE_UNDIRECTED_CONTACT" for row in edges) == 2 and sum(row["visible_contact"] == "YES" for row in edges) == 2,
        "all_directions_blocked": all(row["direction_status"] == "NO_DIRECTION_INFERRED" for row in nodes),
        "no_global_cycle": "kein geschlossener Kreislauf" in readable,
        "summary_counts": summary["nodes"] == 9 and summary["edges"] == 10 and summary["events"] == 153 and summary["statements"] == 54 and summary["owner_break_statements"] == 3,
        "sealed_not_accessed": summary["sealed_pages_accessed"] is False,
        "sealed_absent": "f84" not in " ".join((OUT / name).read_text(encoding="utf-8").lower() for name in ARTIFACTS),
    }
    first = hashes()
    subprocess.run(["python3", str(OUT / "build_two_hundred_thirty_second.py")], check=True)
    second = hashes()
    checks["deterministic_rebuild"] = first == second
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary, "artifact_sha256": second}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
