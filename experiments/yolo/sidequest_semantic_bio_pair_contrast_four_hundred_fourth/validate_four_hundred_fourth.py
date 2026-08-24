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
    repeats = read("FOUR_HUNDRED_FOURTH_BIO_WITHIN_STATEMENT_REPEATS.tsv")
    adjacent = read("FOUR_HUNDRED_FOURTH_FOUR_BIO_ADJACENT_DUPLICATES.tsv")
    closest = read("FOUR_HUNDRED_FOURTH_THREE_CLOSEST_BIO_PATTERNS.tsv")
    checks = {
        "eleven_repeat_groups": len(repeats) == 11,
        "repeat_records_bio_only": all(row["record"].startswith("B") for row in repeats),
        "one_contiguous_carry": sum(row["relation"] == "CONTIGUOUS_CARRY" for row in repeats) == 1,
        "four_adjacent_pairs": len(adjacent) == 4,
        "all_adjacent_not_siblings": {row["h2_split_rejoin_sibling"] for row in adjacent} == {"NO"},
        "one_cross_line_carry": sum(row["boundary_class"] == "OPEN_CROSS_LINE_CARRY" for row in adjacent) == 1,
        "three_closed_repeats": sum(row["boundary_class"] == "ADJACENT_CLOSED_FIELD_REPEAT" for row in adjacent) == 3,
        "zero_open_same_field_bio_pairs": not any(row["boundary_class"] == "OPEN_SAME_FIELD_PAIR" for row in adjacent),
        "three_closest_patterns": len(closest) == 3,
        "all_have_specific_difference": all(row["why_not_h2"] for row in closest),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "FOUR_HUNDRED_FOURTH_VALIDATION.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if status != "PASS":
        raise SystemExit(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
