#!/usr/bin/env python3
"""Validate the complete long-statement microstep edition."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> None:
    events = read("THREE_HUNDRED_SEVENTEENTH_105_LONG_STATEMENT_EVENTS.tsv")
    steps = read("THREE_HUNDRED_SEVENTEENTH_32_MICROSTEPS.tsv")
    summary = json.loads((HERE / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "long_statements_12": len({row["statement_id"] for row in events}) == summary["long_statements"] == 12,
        "events_105": len(events) == summary["visible_events"] == 105,
        "source_operations_104": sum(int(row["source_operation_count"]) for row in steps) == summary["source_operations"] == 104,
        "steps_32": len(steps) == summary["microsteps"] == 32,
        "events_unique": len({row["event_id"] for row in events}) == 105,
        "max_size_6": max(int(row["visible_event_count"]) for row in steps) == summary["max_step_size"] == 6,
        "one_six_card_step": sum(int(row["visible_event_count"]) == 6 for row in steps) == summary["six_card_steps"] == 1,
        "no_hidden_owner_reset": all(row["owner_resets_inside"] == "NONE" for row in steps) and summary["owner_resets_inside_steps"] == 0,
        "one_read_once_step": sum(row["read_once_pair"] != "NONE" for row in steps) == summary["read_once_steps"] == 1,
        "all_readings_present": all(row["concrete_reading_de"] for row in steps),
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
