#!/usr/bin/env python3
"""Validate the complete station-bound Biological edition."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> None:
    units = read("THREE_HUNDRED_EIGHTEENTH_118_STATION_WORK_UNITS.tsv")
    stations = read("THREE_HUNDRED_EIGHTEENTH_16_STATION_OPERATING_CARDS.tsv")
    entries = read("THREE_HUNDRED_EIGHTEENTH_16_STATION_ENTRIES.tsv")
    summary = json.loads((HERE / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    all_event_ids = [event for row in units for event in row["event_ids"].split("|")]
    checks = {
        "events_281": len(all_event_ids) == len(set(all_event_ids)) == summary["events"] == 281,
        "statements_97": len({row["statement_id"] for row in units}) == summary["statements"] == 97,
        "microsteps_32": summary["long_microsteps"] == 32,
        "units_118": len(units) == summary["station_work_units"] == 118,
        "stations_16": len(stations) == summary["stations"] == 16,
        "entries_16": len(entries) == summary["station_entries"] == 16,
        "record_starts_6": sum(row["boundary_class"] == "RECORD_START" for row in entries) == summary["record_starts"] == 6,
        "owner_breaks_10": sum(row["boundary_class"] == "VISIBLE_OWNER_BREAK_NO_PHYSICAL_CARRY" for row in entries) == summary["owner_break_entries"] == 10,
        "unresolved_events_32": summary["unresolved_events"] == 32,
        "owner_pure_units": all(len({row["owner_id"]}) == 1 for row in units),
        "no_global_flow": all(row["global_flow_edge"] == "NONE" for row in units) and summary["global_flow_edges"] == 0,
        "all_stations_used": {row["owner_id"] for row in units} == {row["owner_id"] for row in stations},
        "no_sealed_page": not any(row["page"].startswith("f84") for row in units),
    }
    failed = [name for name, passed in checks.items() if not passed]
    result = {"status": "PASS" if not failed else "FAIL", "checks": checks, "failed": failed}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
