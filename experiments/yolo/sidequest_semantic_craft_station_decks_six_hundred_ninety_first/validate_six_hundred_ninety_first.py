#!/usr/bin/env python3
"""Validate specialist craft-station and record deck accounting."""

from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python3", str(HERE / "build_six_hundred_ninety_first.py")], check=True)
    roots = read("SIX_HUNDRED_NINETY_FIRST_26_SPECIALIST_ROOT_STATIONS.tsv")
    stations = read("SIX_HUNDRED_NINETY_FIRST_5_CRAFT_STATION_DECKS.tsv")
    records = read("SIX_HUNDRED_NINETY_FIRST_11_MINIMAL_RECORD_DECKS.tsv")
    matrix = read("SIX_HUNDRED_NINETY_FIRST_55_RECORD_STATION_MATRIX.tsv")
    station_counts = Counter(row["station"] for row in roots)
    checks = {
        "twenty_six_roots": len(roots) == 26 and len({row["component"] for row in roots}) == 26,
        "five_stations": len(stations) == 5 and sum(int(row["root_cards"]) for row in stations) == 26,
        "station_root_counts": station_counts == Counter({"PREPARATION_INPUT": 4, "WET_HANDLING": 6, "TRANSFER_EDIT": 4, "STATE_CONTROL": 7, "LOCAL_COMMAND": 5}),
        "two_hundred_forty_two_tokens": sum(int(row["token_uses"]) for row in roots) == 242 and sum(int(row["token_uses"]) for row in stations) == 242,
        "eleven_records": len(records) == 11,
        "deck_range_three_to_fourteen": min(int(row["minimal_specialist_root_cards"]) for row in records) == 3 and max(int(row["minimal_specialist_root_cards"]) for row in records) == 14,
        "largest_B2_B3": {row["record"] for row in records if row["minimal_specialist_root_cards"] == "14"} == {"B2", "B3"},
        "fifty_five_matrix_rows": len(matrix) == 55,
        "matrix_tokens_match": sum(int(row["token_uses"]) for row in matrix) == 242,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "passed": sum(checks.values()), "total": len(checks)}
    (HERE / "SIX_HUNDRED_NINETY_FIRST_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
