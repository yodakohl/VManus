#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent
ARTIFACTS = [
    "TWO_HUNDRED_THIRTY_FIFTH_NINE_NODE_MASTER_SCRIPT.tsv",
    "TWO_HUNDRED_THIRTY_FIFTH_FIFTY_FOUR_DICTATION_TRACES.tsv",
    "TWO_HUNDRED_THIRTY_FIFTH_TWENTY_RULE_MANUAL.tsv",
    "TWO_HUNDRED_THIRTY_FIFTH_READABLE_APPRENTICE_MANUAL.md",
    "TWO_HUNDRED_THIRTY_FIFTH_REPORT.md",
    "BUILD_SUMMARY.json",
]


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def hashes() -> dict[str, str]:
    return {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in ARTIFACTS}


def main() -> None:
    nodes = read(ARTIFACTS[0])
    traces = read(ARTIFACTS[1])
    rules = read(ARTIFACTS[2])
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "nine_nodes": len(nodes) == 9 and {row["node_id"] for row in nodes} == {f"N{i}" for i in range(1, 10)},
        "fifty_four_statements": len(traces) == 54 and len({row["statement_id"] for row in traces}) == 54,
        "one_hundred_fifty_three_events": sum(int(row["event_count"]) for row in traces) == 153,
        "all_events_once": sorted(event for row in traces for event in row["event_ids"].split("|")) == [f"E{i:03d}" for i in range(229, 382)],
        "node_streams_cover_events": sum(int(row["event_count"]) for row in nodes) == 153,
        "twenty_rules": len(rules) == 20 and len({row["rule_id"] for row in rules}) == 20,
        "three_owner_break_traces": sum("OWNER_BREAK" in row["rules_used"] for row in traces) == 3,
        "all_prompts_and_responses_present": all(row["master_says_de"].strip() and row["apprentice_selects_visible_cards"].strip() for row in traces),
        "sealed_not_accessed": summary["sealed_pages_accessed"] is False,
        "sealed_absent": "f84" not in " ".join((OUT / name).read_text(encoding="utf-8").lower() for name in ARTIFACTS[:-1]),
    }
    first = hashes()
    subprocess.run(["python3", str(OUT / "build_two_hundred_thirty_fifth.py")], check=True)
    second = hashes()
    checks["deterministic_rebuild"] = first == second
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary, "artifact_sha256": second}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
