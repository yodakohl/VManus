#!/usr/bin/env python3
"""Validate Pass 717 continuous master page."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    statements = read("SEVEN_HUNDRED_SEVENTEENTH_12_MASTER_STATEMENTS.tsv")
    events = read("SEVEN_HUNDRED_SEVENTEENTH_27_OWNER_STATE_TRACE.tsv")
    lines = read("SEVEN_HUNDRED_SEVENTEENTH_5_PHYSICAL_LINES.tsv")
    errors = read("SEVEN_HUNDRED_SEVENTEENTH_3_CORRECTOR_CASES.tsv")
    checks = {
        "statements_12": len(statements) == 12 and len({row["docket_id"] for row in statements}) == 12,
        "events_27_ordered": len(events) == 27 and [int(row["global_position"]) for row in events] == list(range(1, 28)),
        "lines_5": len(lines) == 5 and sum(int(row["events"]) for row in lines) == 27,
        "four_cross_line": sum(row["crosses_line"] == "YES" for row in statements) == 4,
        "two_owner_handoffs": sum(row["owner_handoff_before"] == "YES" for row in statements) == 2,
        "owner_order": list(dict.fromkeys(row["owner"] for row in events)) == ["PLANT", "BASIN", "APPARATUS"],
        "all_source_events_once": len({row["source_practice_event"] for row in events}) == 27,
        "three_corrector_cases": len(errors) == 3,
        "no_meaning_change_in_corrections": all(row["meaning_change"].startswith("NO__") for row in errors),
        "line_break_not_statement_rule": any(row["ends_inside_statement"] == "YES" for row in lines),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_SEVENTEENTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
