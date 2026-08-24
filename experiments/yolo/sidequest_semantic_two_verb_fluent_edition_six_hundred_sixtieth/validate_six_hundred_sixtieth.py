#!/usr/bin/env python3
"""Validate the complete two-verb fluent edition."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    readings = rows("SIX_HUNDRED_SIXTIETH_18_FLUENT_STATEMENT_READINGS.tsv")
    teaching = rows("SIX_HUNDRED_SIXTIETH_5_TEACHING_EXCERPTS.tsv")
    checks = {
        "eighteen_readings": len(readings) == 18,
        "ninety_four_events": sum(int(row["event_count"]) for row in readings) == 94,
        "nine_clean": sum(row["reading_quality"] == "CLEAN" for row in readings) == 9,
        "eight_workable": sum(row["reading_quality"] == "WORKABLE" for row in readings) == 8,
        "one_dense": sum(row["reading_quality"] == "DENSE_BUT_COMPLETE" for row in readings) == 1,
        "all_events_retained": all(row["all_visible_events_retained"] == "YES" for row in readings),
        "no_added_content_nouns": all(row["added_content_nouns"] == "NONE" for row in readings),
        "five_teaching_excerpts": len(teaching) == 5,
        "teaching_ids_unique": len({row["statement_id"] for row in teaching}) == 5,
        "all_have_source_and_translation": all(row["source_surface"] and row["fluent_workshop_reading_de"] for row in readings),
        "no_placeholders": all("UNKNOWN" not in row["fluent_workshop_reading_de"] and "EXEMPLAR" not in row["fluent_workshop_reading_de"] for row in readings),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_SIXTIETH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, passed in checks.items():
        print(f"{name}\t{'PASS' if passed else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
