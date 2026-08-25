#!/usr/bin/env python3
"""Validate the Pass 1004 continuous creative edition."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    events = read("PASS1004_657_REVISED_EVENT_INTERLINEAR.tsv")
    decisions = read("PASS1004_13_VARIANT_DECISIONS.tsv")
    surfaces = read("PASS1004_393_REVISED_SURFACE_DICTIONARY.tsv")
    loci = read("PASS1004_111_REVISED_LOCUS_READINGS.tsv")
    statements = read("PASS1004_110_CONTINUOUS_STATEMENTS.tsv")
    combined = read("PASS1004_3168_COMBINED_EVENT_INTERLINEAR.tsv")
    summary = json.loads((HERE / "PASS1004_BUILD_SUMMARY.json").read_text(encoding="utf-8"))

    checks: dict[str, bool] = {}
    checks["657 fresh events"] = len(events) == 657
    checks["608 running events"] = sum(row["kind"] != "L" for row in events) == 608
    checks["49 labels"] = sum(row["kind"] == "L" for row in events) == 49
    checks["393 surfaces"] = len(surfaces) == 393
    checks["111 loci"] = len(loci) == 111
    checks["13 resolutions"] = len(decisions) == 13
    checks["all decisions resolved"] = {row["decision"] for row in decisions} == {
        "RESOLVED_WITH_EXISTING_ROOTS"
    }
    checks["no tentative events"] = all(
        row["transfer_class"] != "TENTATIVE_ROOTED_VARIANT" for row in events
    )
    checks["110 statements"] = len(statements) == 110
    checks["statement page counts"] = Counter(row["physical_page"] for row in statements) == Counter(
        {"f17r": 9, "f77r": 83, "f88v": 13, "f71v": 5}
    )
    checks["40 cross-line statements"] = sum(
        row["crosses_physical_line"] == "YES" for row in statements
    ) == 40
    checks["103 closed statements"] = sum(
        row["end_reason"] == "LICENSED_DY_CLOSE" for row in statements
    ) == 103
    checks["7 open statements"] = sum(
        row["end_reason"] != "LICENSED_DY_CLOSE" for row in statements
    ) == 7
    checks["closed end in DY"] = all(
        row["component_sequence"].split(" | ")[-1].split("+")[-1] == "DY"
        for row in statements
        if row["end_reason"] == "LICENSED_DY_CLOSE"
    )
    checks["open do not end in DY"] = all(
        row["component_sequence"].split(" | ")[-1].split("+")[-1] != "DY"
        for row in statements
        if row["end_reason"] != "LICENSED_DY_CLOSE"
    )
    event_order = [row["fresh_event_id"] for row in events if row["kind"] != "L"]
    event_index = {event_id: number for number, event_id in enumerate(event_order)}
    covered: list[str] = []
    for row in statements:
        start = event_index[row["first_event_id"]]
        end = event_index[row["last_event_id"]]
        covered.extend(event_order[start : end + 1])
    checks["all running events assigned once"] = covered == event_order and len(set(covered)) == 608
    checks["statement group sum"] = sum(int(row["groups"]) for row in statements) == 608
    checks["locus group sum"] = sum(int(row["groups"]) for row in loci) == 657
    checks["surface event sum"] = sum(int(row["events"]) for row in surfaces) == 657
    checks["3168 combined events"] = len(combined) == 3168
    checks["18 combined pages"] = len({row["physical_page"] for row in combined}) == 18
    checks["657 new combined rows"] = sum(
        row["edition_source"] == "PASS1004_FRESH_CONTINUOUS" for row in combined
    ) == 657
    checks["no blank event meaning"] = all(row["portable_default_de"].strip() for row in events)
    checks["no blank statement reading"] = all(
        row["continuous_workshop_reading_de"].strip() for row in statements
    )
    checks["summary agrees"] = (
        summary["fresh_groups"] == 657
        and summary["running_groups"] == 608
        and summary["continuous_statements"] == 110
        and summary["tentative_variants_remaining"] == 0
    )
    checks["exact resolution IDs"] = {row["event_id"] for row in decisions} == set(
        [
            "P1003-E0001", "P1003-E0032", "P1003-E0049", "P1003-E0053",
            "P1003-E0057", "P1003-E0064", "P1003-E0228", "P1003-E0312",
            "P1003-E0464", "P1003-E0493", "P1003-E0508", "P1003-E0526",
            "P1003-E0648",
        ]
    )
    checks["fresh page scope exact"] = {row["physical_page"] for row in events} == {
        "f17r", "f77r", "f88v", "f71v"
    }

    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "failures": [name for name, passed in checks.items() if not passed],
    }
    (HERE / "PASS1004_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
