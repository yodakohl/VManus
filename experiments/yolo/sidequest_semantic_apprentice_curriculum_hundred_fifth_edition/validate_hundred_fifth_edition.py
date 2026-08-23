#!/usr/bin/env python3
"""Validate the apprentice curriculum and coverage trace."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    lessons = rows("HUNDRED_FIFTH_24_DAY_CURRICULUM.tsv")
    coverage = rows("HUNDRED_FIFTH_STAGE_COVERAGE.tsv")
    exercises = rows("HUNDRED_FIFTH_12_APPRENTICE_EXERCISES.tsv")
    stage = {row["stage_id"]: row for row in coverage}
    checks = {
        "lessons_9": len(lessons) == 9,
        "days_1_to_24": int(lessons[0]["day_start"]) == 1 and int(lessons[-1]["day_end"]) == 24,
        "stages_6": len(coverage) == 6,
        "exercises_12": len(exercises) == 12,
        "three_astro_exercises": sum(row["mode"] == "LOCAL_ASTRO_NOMENCLATOR" for row in exercises) == 3,
        "coverage_monotonic_core_bridge": int(stage["S2"]["decoded_prose_events"]) >= int(stage["S1"]["decoded_prose_events"]),
        "full_atoms_44": int(stage["S4"]["known_atom_count"]) == 44,
        "full_events_381": int(stage["S4"]["decoded_prose_events"]) == 381,
        "full_statements_116": int(stage["S4"]["fully_decoded_statements"]) == 116,
        "sealed_absent": all("f84" not in "\t".join(row.values()).lower() for row in exercises),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
