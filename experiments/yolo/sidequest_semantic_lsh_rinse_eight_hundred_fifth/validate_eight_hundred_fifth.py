#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_fifth.py")], check=True)
    events = read("EIGHT_HUNDRED_FIFTH_3_LSH_EVENTS.tsv")
    candidates = read("EIGHT_HUNDRED_FIFTH_3_MEANING_CANDIDATES.tsv")
    statements = read("EIGHT_HUNDRED_FIFTH_2_REVISED_STATEMENTS.tsv")
    grid = read("EIGHT_HUNDRED_FIFTH_6_LSH_GRADE_CELLS.tsv")
    summary = json.loads((HERE / "EIGHT_HUNDRED_FIFTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "three_events_two_cards_two_statements": len(events) == 3 and len({row["surface"] for row in events}) == 2 and len(statements) == 2,
        "two_recipes": {row["component_recipe"] for row in events} == {"LSH+O", "LSH+E+DY"},
        "spuelen_selected": len(candidates) == 3 and next(row for row in candidates if row["decision"] == "SELECT")["candidate"] == "SPUELEN",
        "all_events_spuelen": all(row["selected_reading_de"].startswith("SPUELEN") for row in events),
        "six_grade_cells": len(grid) == 6,
        "one_attested_five_predicted": summary["attested_grade_cells"] == 1 and summary["predicted_grade_cells"] == 5,
        "no_prediction_collisions": summary["prediction_collisions"] == 0,
        "core22_strip9": summary["new_core_size"] == 22 and summary["remaining_recurrent_strip_values"] == 9,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "EIGHT_HUNDRED_FIFTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
