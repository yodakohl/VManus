#!/usr/bin/env python3
"""Validate Pass 296 grade matrix."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> None:
    cards = read("TWO_HUNDRED_NINETY_SIXTH_30_GRADE_CARDS.tsv")
    matrix = read("TWO_HUNDRED_NINETY_SIXTH_20_PARADIGM_MATRIX.tsv")
    predictions = read("TWO_HUNDRED_NINETY_SIXTH_16_RANKED_GRADE_PREDICTIONS.tsv")
    checks = {
        "thirty_cards": len(cards) == 30,
        "seventy_three_events": sum(int(row["event_support"]) for row in cards) == 73,
        "twenty_paradigms": len(matrix) == 20,
        "observed_cells_27": sum(int(row["observed_grade_cells"]) for row in matrix) == 27,
        "missing_cells_33": sum(int(row["missing_grade_cells"]) for row in matrix) == 33,
        "one_complete_family": sum(int(row["observed_grade_cells"]) == 3 for row in matrix) == 1,
        "five_two_grade_families": sum(int(row["observed_grade_cells"]) == 2 for row in matrix) == 5,
        "sixteen_predictions": len(predictions) == 16,
        "all_predictions_new": all(row["already_visible_on_ten_pages"] == "NO" for row in predictions),
        "all_grades_assigned": all(row["grade"] in {"E_SHORT", "EE_LONG", "EEE_FULL"} for row in cards),
        "no_sealed_page": not any("f" + "84" in path.read_text(encoding="utf-8").lower() for path in [HERE / "TWO_HUNDRED_NINETY_SIXTH_30_GRADE_CARDS.tsv", HERE / "TWO_HUNDRED_NINETY_SIXTH_GRADE_MANUAL.md", HERE / "TWO_HUNDRED_NINETY_SIXTH_REPORT.md"]),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "failed": [key for key, value in checks.items() if not value]}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
