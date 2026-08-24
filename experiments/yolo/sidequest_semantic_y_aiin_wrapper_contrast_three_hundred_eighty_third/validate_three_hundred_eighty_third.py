#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    occurrences = read("THREE_HUNDRED_EIGHTY_THIRD_38_REAL_OCCURRENCES.tsv")
    surfaces = read("THREE_HUNDRED_EIGHTY_THIRD_11_SURFACE_CONTRAST.tsv")
    shared = read("THREE_HUNDRED_EIGHTY_THIRD_FOUR_SHARED_SHELLS.tsv")
    drills = read("THREE_HUNDRED_EIGHTY_THIRD_ELEVEN_CONTRAST_LINES.tsv")
    checks = {
        "thirty_eight_occurrences": len(occurrences) == 38,
        "y_eighteen": sum(row["family"] == "Y" for row in occurrences) == 18,
        "aiin_twenty": sum(row["family"] == "AIIN" for row in occurrences) == 20,
        "eleven_surfaces": len(surfaces) == 11,
        "surface_counts_sum": sum(int(row["occurrences"]) for row in surfaces) == 38,
        "four_shared_shells": {row["entry_shell"] for row in shared} == {"BARE", "CH", "D", "S"},
        "eleven_drills": len(drills) == 11,
        "all_registered": all(row["surface_registered"] == "YES" for row in drills),
        "positions_known": all(row["field_position"] in {"FIRST", "MIDDLE", "LAST", "ONLY"} for row in occurrences),
        "pages_allowed": {row["page"] for row in occurrences} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "values_fixed": {row["core_value_de"] for row in occurrences if row["family"] == "Y"} == {"Diesposten"} and {row["core_value_de"] for row in occurrences if row["family"] == "AIIN"} == {"Sollmaß"},
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_EIGHTY_THIRD_VALIDATION.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if status != "PASS":
        raise SystemExit(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
