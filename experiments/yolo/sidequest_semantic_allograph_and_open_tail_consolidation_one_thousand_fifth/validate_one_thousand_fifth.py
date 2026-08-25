#!/usr/bin/env python3
"""Validate Pass 1005."""

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
    events = read("PASS1005_657_CONSOLIDATED_EVENT_INTERLINEAR.tsv")
    decisions = read("PASS1005_34_ALLOGRAPH_DECISIONS.tsv")
    surfaces = read("PASS1005_393_CONSOLIDATED_SURFACE_DICTIONARY.tsv")
    statements = read("PASS1005_108_CONSOLIDATED_STATEMENTS.tsv")
    tails = read("PASS1005_7_OPEN_TAIL_DECISIONS.tsv")
    loci = read("PASS1005_111_CONSOLIDATED_LOCUS_READINGS.tsv")
    combined = read("PASS1005_3168_COMBINED_EVENT_INTERLINEAR.tsv")
    summary = json.loads((HERE / "PASS1005_BUILD_SUMMARY.json").read_text(encoding="utf-8"))

    checks: dict[str, bool] = {}
    checks["657 events"] = len(events) == 657
    checks["608 running"] = sum(row["kind"] != "L" for row in events) == 608
    checks["49 labels"] = sum(row["kind"] == "L" for row in events) == 49
    checks["393 surfaces"] = len(surfaces) == 393
    checks["111 loci"] = len(loci) == 111
    checks["34 decisions"] = len(decisions) == 34
    checks["29 compositions"] = sum(row["decision_class"] == "VISIBLE_COMPOSITION" for row in decisions) == 29
    checks["5 allographs"] = sum(row["decision_class"] == "LICENSED_ALLOGRAPH" for row in decisions) == 5
    checks["no nearest forms"] = all(row["transfer_class"] != "NEAR_REGISTERED_ALLOGRAPH" for row in events)
    checks["108 statements"] = len(statements) == 108
    checks["page statement counts"] = Counter(row["physical_page"] for row in statements) == Counter(
        {"f17r": 8, "f77r": 82, "f88v": 13, "f71v": 5}
    )
    checks["101 licensed closes"] = sum(row["end_mode"] == "LICENSED_DY_CLOSE" for row in statements) == 101
    checks["7 tails"] = len(tails) == 7
    checks["7 nonclose statements"] = sum(row["end_mode"] != "LICENSED_DY_CLOSE" for row in statements) == 7
    checks["39 cross-line"] = sum(row["crosses_physical_line"] == "YES" for row in statements) == 39
    checks["closed recipes end DY"] = all(
        row["component_sequence"].split(" | ")[-1].split("+")[-1] == "DY"
        for row in statements
        if row["end_mode"] == "LICENSED_DY_CLOSE"
    )
    checks["open recipes do not end DY"] = all(
        row["component_sequence"].split(" | ")[-1].split("+")[-1] != "DY"
        for row in statements
        if row["end_mode"] != "LICENSED_DY_CLOSE"
    )
    checks["no invented tail close"] = {row["invented_close"] for row in tails} == {"NO"}
    checks["tail modes distinct enough"] = len({row["tail_mode"] for row in tails}) == 7
    event_order = [row["fresh_event_id"] for row in events if row["kind"] != "L"]
    event_index = {event_id: number for number, event_id in enumerate(event_order)}
    covered: list[str] = []
    for row in statements:
        covered.extend(
            event_order[event_index[row["first_event_id"]] : event_index[row["last_event_id"]] + 1]
        )
    checks["running coverage exact"] = covered == event_order and len(set(covered)) == 608
    checks["statement group sum"] = sum(int(row["groups"]) for row in statements) == 608
    checks["locus group sum"] = sum(int(row["groups"]) for row in loci) == 657
    checks["surface group sum"] = sum(int(row["events"]) for row in surfaces) == 657
    checks["fluent text complete"] = all(row["fluent_workshop_de"].strip() for row in statements)
    checks["3168 combined"] = len(combined) == 3168
    checks["18 pages combined"] = len({row["physical_page"] for row in combined}) == 18
    checks["657 current combined"] = sum(
        row["edition_source"] == "PASS1005_ALLOGRAPH_TAIL_CONSOLIDATION" for row in combined
    ) == 657
    checks["summary agrees"] = (
        summary["allograph_decisions"] == 34
        and summary["statements"] == 108
        and summary["licensed_closes"] == 101
        and summary["explicit_open_or_owner_ends"] == 7
        and summary["nearest_allographs_remaining"] == 0
    )
    checks["page scope exact"] = {row["physical_page"] for row in events} == {
        "f17r", "f77r", "f88v", "f71v"
    }

    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "failures": [name for name, passed in checks.items() if not passed],
    }
    (HERE / "PASS1005_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
