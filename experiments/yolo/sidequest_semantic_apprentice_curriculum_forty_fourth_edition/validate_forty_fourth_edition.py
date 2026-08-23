#!/usr/bin/env python3
"""Consistency checks for the eight-day apprentice curriculum."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    lessons = read("FORTY_FOURTH_24_LESSON_CURRICULUM.tsv")
    exercises = read("FORTY_FOURTH_32_DAILY_EXERCISES.tsv")
    exam = read("FORTY_FOURTH_FINAL_EXAM.tsv")
    per_day = Counter(int(row["day"]) for row in lessons)
    exercise_days = Counter(int(row["day"]) for row in exercises)
    checks = {
        "eight_days": set(per_day) == set(range(1, 9)),
        "three_lessons_per_day": all(per_day[day] == 3 for day in range(1, 9)),
        "twenty_four_lessons": len(lessons) == 24,
        "lesson_ids_ordered": [row["lesson_id"] for row in lessons] == [f"L{i:02d}" for i in range(1, 25)],
        "forty_hours": sum(int(row["minutes"]) for row in lessons) == 2400,
        "thirty_two_exercises": len(exercises) == 32,
        "four_exercises_per_day": all(exercise_days[day] == 4 for day in range(1, 9)),
        "eight_exam_tasks": len(exam) == 8,
        "sixty_exam_points": sum(int(row["points"]) for row in exam) == 60,
        "all_lessons_have_completion": all(row["apprentice_completion_de"] for row in lessons),
        "all_exercises_have_correction": all("CORRECTION" in row["required_outputs"] for row in exercises),
        "manual_exists": (OUT / "FORTY_FOURTH_EIGHT_DAY_APPRENTICE_MANUAL.md").exists(),
        "sealed_absent": not any("f84" in path.name.lower() for path in OUT.iterdir()),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
