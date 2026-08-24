#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    ladder = read("THREE_HUNDRED_EIGHTY_FOURTH_SIX_CELL_LADDER.tsv")
    occurrences = read("THREE_HUNDRED_EIGHTY_FOURTH_38_REAL_OCCURRENCES.tsv")
    extensions = read("THREE_HUNDRED_EIGHTY_FOURTH_TWO_ENDPOINT_EXTENSIONS.tsv")
    boundaries = read("THREE_HUNDRED_EIGHTY_FOURTH_BOUNDARY_CARDS.tsv")
    counts = Counter(row["composition"] for row in occurrences)
    checks = {
        "six_cells": len(ladder) == 6,
        "thirty_eight_occurrences": len(occurrences) == 38,
        "expected_cell_counts": counts == {"OK+Y": 10, "OK+E+Y": 2, "OK+EE+Y": 7, "OK+E+DY": 8, "OK+EE+DY": 10, "OK+EEE+DY": 1},
        "ladder_counts_match": all(int(row["real_occurrences"]) == int(row["expected_occurrences"]) for row in ladder),
        "grades": {row["e_grade"] for row in ladder} == {"NONE", "SHORT", "LONG", "FULL"},
        "endpoints": {row["endpoint"] for row in ladder} == {"Y_OPEN", "DY_CLOSE"},
        "two_extensions": len(extensions) == 2 and all(int(row["real_occurrences"]) == 1 for row in extensions),
        "six_boundaries": len(boundaries) == 6,
        "all_pages_allowed": {row["page"] for row in occurrences} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "defaults_nonempty": all(row["short_default_de"] for row in occurrences),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_EIGHTY_FOURTH_VALIDATION.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if status != "PASS":
        raise SystemExit(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
