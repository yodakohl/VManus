#!/usr/bin/env python3
"""Consistency checks for the small learned nomenclator."""

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
    lessons = read("FORTY_THIRD_15_NOMENCLATOR_LESSONS.tsv")
    surfaces = read("FORTY_THIRD_23_SPECIAL_SURFACES.tsv")
    classes = Counter(row["lesson_kind"] for row in surfaces)
    checks = {
        "fifteen_lessons": len(lessons) == 15,
        "lesson_ids_unique": len({row["lesson_id"] for row in lessons}) == 15,
        "twelve_values_three_splits": sum(row["lesson_kind"] != "REGISTER_SPLIT" for row in lessons) == 12 and sum(row["lesson_kind"] == "REGISTER_SPLIT" for row in lessons) == 3,
        "twenty_three_surfaces": len(surfaces) == 23,
        "surface_ids_unique": len({row["surface_id"] for row in surfaces}) == 23,
        "visible_surfaces_unique": len({row["visible_surface"] for row in surfaces}) == 23,
        "thirty_four_groups": sum(int(row["observed_groups"]) for row in surfaces) == 34,
        "every_surface_one_lesson": all(sum(row["lesson_id"] == lesson["lesson_id"] for lesson in lessons) == 1 for row in surfaces),
        "lesson_surface_counts_match": all(int(lesson["surface_count"]) == sum(row["lesson_id"] == lesson["lesson_id"] for row in surfaces) for lesson in lessons),
        "all_values_short": all(0 < len(row["learned_value_de"].split()) <= 3 for row in lessons),
        "all_have_analogy": all(row["workshop_analogue_de"] for row in lessons),
        "small_book_exists": (OUT / "FORTY_THIRD_SMALL_NOMENCLATOR.md").exists(),
        "sealed_absent": not any("f84" in row["pages"] for row in surfaces),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "surface_lesson_classes": dict(classes)}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
