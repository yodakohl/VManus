#!/usr/bin/env python3
"""Validate twelve reverse apprentice traces and four absent-card trials."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    steps = read("SIX_HUNDRED_SEVENTY_SEVENTH_73_REVERSE_TRACE_STEPS.tsv")
    statements = read("SIX_HUNDRED_SEVENTY_SEVENTH_12_ROUNDTRIP_STATEMENTS.tsv")
    absent = read("SIX_HUNDRED_SEVENTY_SEVENTH_4_ABSENT_CARD_TRIALS.tsv")
    workflow = read("SIX_HUNDRED_SEVENTY_SEVENTH_6_STEP_WORKFLOW.tsv")
    checks = {
        "twelve_statements": len(statements) == 12 and len({row["statement_id"] for row in statements}) == 12,
        "seventy_three_steps": len(steps) == 73 and sum(int(row["events"]) for row in statements) == 73,
        "all_eleven_records": len({row["record"] for row in statements}) == 11,
        "all_step_matches": all(row["exact_card_match"] == "YES" and row["surface_match"] == "YES" for row in steps),
        "all_statement_roundtrips": all(all(row[field] == "YES" for field in ["component_roundtrip", "card_roundtrip", "surface_roundtrip", "meaning_roundtrip"]) for row in statements),
        "four_absent_trials": len(absent) == 4,
        "all_absent_cards": all(row["semantic_composition_available"] == "YES" and row["exact_card_in_ten_page_table"] == "NO" for row in absent),
        "no_invented_surfaces": all(row["invented_surface"] == "NONE" for row in absent),
        "six_step_workflow": len(workflow) == 6 and [int(row["step"]) for row in workflow] == list(range(1, 7)),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_SEVENTY_SEVENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, passed in checks.items():
        print(f"{name}\t{'PASS' if passed else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
