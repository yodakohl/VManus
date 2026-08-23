#!/usr/bin/env python3
"""Validate Pass 292 production squares."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> None:
    squares = read("TWO_HUNDRED_NINETY_SECOND_FIVE_PRODUCTION_SQUARES.tsv")
    traces = read("TWO_HUNDRED_NINETY_SECOND_25_LETTER_TRACES.tsv")
    types = Counter(row["composition_type"] for row in squares)
    checks = {
        "five_squares": len(squares) == 5,
        "five_unique_predictions": len({row["predicted_surface"] for row in squares}) == 5,
        "three_techniques": set(types) == {"SLOT_SUBSTITUTION", "SHARED_CORE_OVERLAY", "GRADE_LENGTHENING"},
        "three_grade_members": types["GRADE_LENGTHENING"] == 3,
        "twenty_five_trace_steps": len(traces) == 25,
        "five_steps_each": all(sum(row["square"] == square for row in traces) == 5 for square in {row["square"] for row in squares}),
        "parents_present": all(row["parent_a_events"] != "0" and row["parent_b_events"] != "0" for row in squares),
        "all_currently_new": all(row["already_visible_on_ten_pages"] == "NO" for row in squares),
        "no_empty_instruction": all(row["apprentice_rule_de"] and row["failure_sign"] for row in squares),
        "fixed_pages_only": not any("f" + "84" in path.read_text(encoding="utf-8").lower() for path in [HERE / "TWO_HUNDRED_NINETY_SECOND_FIVE_PRODUCTION_SQUARES.tsv", HERE / "TWO_HUNDRED_NINETY_SECOND_APPRENTICE_COPY_SHEET.md", HERE / "TWO_HUNDRED_NINETY_SECOND_REPORT.md"]),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "failed": [key for key, value in checks.items() if not value]}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
