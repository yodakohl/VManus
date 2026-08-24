#!/usr/bin/env python3
"""Validate the B1-S002 microstep edition."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> None:
    events = read("THREE_HUNDRED_SIXTEENTH_19_EVENT_RESEGMENTATION.tsv")
    steps = read("THREE_HUNDRED_SIXTEENTH_FIVE_MICROSTEPS.tsv")
    summary = json.loads((HERE / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "events_19": len(events) == summary["events"] == 19,
        "steps_5": len(steps) == summary["microsteps"] == 5,
        "sizes_3_5_6_3_2": [int(row["event_ordinals"].split("-")[1]) - int(row["event_ordinals"].split("-")[0]) + 1 for row in steps] == summary["step_sizes"] == [3, 5, 6, 3, 2],
        "events_unique": len({row["event_id"] for row in events}) == 19,
        "ordinals_complete": [int(row["event_ordinal"]) for row in events] == list(range(1, 20)),
        "one_line_crossing": sum(row["crosses_physical_line"] == "YES" for row in steps) == summary["line_crossing_microsteps"] == 1,
        "one_field_crossing": sum(row["crosses_field_boundary"] == "YES" for row in steps) == summary["field_crossing_microsteps"] == 1,
        "one_terminal_at_end": summary["terminal_events"] == 1 and events[-1]["terminal_scope"] == "TERMINAL",
        "all_target_statement": all(row["microstep_id"].startswith("B1-S002") for row in events),
        "no_sealed_page": not any(row["page"].startswith("f84") or row["locus"].startswith("f84") for row in events),
    }
    failed = [name for name, passed in checks.items() if not passed]
    result = {"status": "PASS" if not failed else "FAIL", "checks": checks, "failed": failed}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
