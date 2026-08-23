#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent
ARTIFACTS = [
    "TWO_HUNDRED_THIRTY_THIRD_SEVENTY_ONE_EVENTS.tsv",
    "TWO_HUNDRED_THIRTY_THIRD_THREE_APPARATUS_FUNCTIONS.tsv",
    "TWO_HUNDRED_THIRTY_THIRD_TWENTY_FIVE_STATEMENTS.tsv",
    "TWO_HUNDRED_THIRTY_THIRD_MODEL_COMPETITION.tsv",
    "TWO_HUNDRED_THIRTY_THIRD_READABLE_TWO_ARM_FUNCTION.md",
    "TWO_HUNDRED_THIRTY_THIRD_REPORT.md",
    "BUILD_SUMMARY.json",
]


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def hashes() -> dict[str, str]:
    return {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in ARTIFACTS}


def main() -> None:
    events = read(ARTIFACTS[0])
    functions = read(ARTIFACTS[1])
    statements = read(ARTIFACTS[2])
    models = read(ARTIFACTS[3])
    readable = (OUT / ARTIFACTS[4]).read_text(encoding="utf-8")
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "seventy_one_unique_events": len(events) == 71 and len({row["event_id"] for row in events}) == 71,
        "three_nodes": {row["graph_node_id"] for row in events} == {"N5", "N6", "N7"} and len(functions) == 3,
        "node_event_counts": {row["node_id"]: int(row["event_count"]) for row in functions} == {"N5": 47, "N6": 18, "N7": 6},
        "twenty_five_statements": len(statements) == 25 and len({row["statement_id"] for row in statements}) == 25,
        "all_events_once": sorted(event for row in statements for event in row["event_ids"].split("|")) == sorted(row["event_id"] for row in events),
        "one_cross_branch_statement": sum("→" in row["node_path"] for row in statements) == 1 and next(row for row in statements if "→" in row["node_path"])["statement_id"] == "B4-S015",
        "selected_model_unique": len([row for row in models if row["decision"] == "Select"]) == 1 and next(row for row in models if row["decision"] == "Select")["model_id"] == "M1",
        "no_direction_claim": all(row["direction_claim"] == "NONE" for row in functions) and summary["direction_claims"] == 0,
        "no_closed_cycle": "nicht nach einem zwingenden Kreisfluss" in readable,
        "summary_counts": summary["nodes"] == 3 and summary["events"] == 71 and summary["statements"] == 25,
        "sealed_not_accessed": summary["sealed_pages_accessed"] is False,
        "sealed_absent": "f84" not in " ".join((OUT / name).read_text(encoding="utf-8").lower() for name in ARTIFACTS[:-1]),
    }
    first = hashes()
    subprocess.run(["python3", str(OUT / "build_two_hundred_thirty_third.py")], check=True)
    second = hashes()
    checks["deterministic_rebuild"] = first == second
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary, "artifact_sha256": second}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
