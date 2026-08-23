#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent
ARTIFACTS = [
    "TWO_HUNDRED_THIRTY_FOURTH_TWENTY_ADDENDUM_EVENTS.tsv",
    "TWO_HUNDRED_THIRTY_FOURTH_FOUR_REVISED_STATEMENTS.tsv",
    "TWO_HUNDRED_THIRTY_FOURTH_LEFT_RIGHT_LINEAGE.tsv",
    "TWO_HUNDRED_THIRTY_FOURTH_READABLE_BRANCH_ADDENDA.md",
    "TWO_HUNDRED_THIRTY_FOURTH_REPORT.md",
    "BUILD_SUMMARY.json",
]


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def hashes() -> dict[str, str]:
    return {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in ARTIFACTS}


def main() -> None:
    events = read(ARTIFACTS[0])
    statements = read(ARTIFACTS[1])
    lineage = read(ARTIFACTS[2])
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "twenty_unique_events": len(events) == 20 and {row["event_id"] for row in events} == {f"E{i:03d}" for i in range(362, 382)},
        "eleven_nine_split": summary["b5_events"] == 11 and summary["b6_events"] == 9,
        "four_statements": len(statements) == 4 and {row["statement_id"] for row in statements} == {"B5-S001", "B5-S002", "B5-S003", "B6-S001"},
        "all_events_once": sorted(event for row in statements for event in row["event_ids"].split("|")) == sorted(row["event_id"] for row in events),
        "four_zero_exact_parent": summary["b5_exact_parent_occurrences"] == 4 and summary["b6_exact_parent_occurrences"] == 0,
        "two_lineages": {row["selected_relation"] for row in lineage} == {"LEFT_BRANCH_OPERATIONAL_CONTINUATION", "RIGHT_BRANCH_ENDPOINT_SUMMARY"},
        "readings_nonempty": all(row["revised_addendum_reading_de"].strip() for row in statements),
        "sealed_not_accessed": summary["sealed_pages_accessed"] is False,
        "sealed_absent": "f84" not in " ".join((OUT / name).read_text(encoding="utf-8").lower() for name in ARTIFACTS[:-1]),
    }
    first = hashes()
    subprocess.run(["python3", str(OUT / "build_two_hundred_thirty_fourth.py")], check=True)
    second = hashes()
    checks["deterministic_rebuild"] = first == second
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary, "artifact_sha256": second}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
