#!/usr/bin/env python3
"""Validate the rare-recipe teaching map."""

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
    subprocess.run(["python3", str(HERE / "build_six_hundred_eighty_fourth.py")], check=True)
    lessons = read("SIX_HUNDRED_EIGHTY_FOURTH_113_RARE_RECIPE_LESSONS.tsv")
    groups = read("SIX_HUNDRED_EIGHTY_FOURTH_TEACHING_GROUPS.tsv")
    hard = read("SIX_HUNDRED_EIGHTY_FOURTH_12_HARDEST_RARE_CARDS.tsv")
    checks = {
        "one_hundred_thirteen_lessons": len(lessons) == 113 and len({row["rare_recipe"] for row in lessons}) == 113,
        "one_event_each": len({row["event_id"] for row in lessons}) == 113,
        "eighty_eight_recurrent_anchors": sum(row["teaching_method"] == "RECURRENT_SAME_HEAD_ANCHOR" for row in lessons) == 88,
        "twenty_three_root_extensions": sum(row["teaching_method"] == "KNOWN_ROOT_TRAY_EXTENSION" for row in lessons) == 23,
        "two_whole_entries": sum(row["teaching_method"] == "WHOLE_NOMENCLATOR_ENTRY" for row in lessons) == 2,
        "distance_distribution": {distance: sum(row["teaching_method"] == "RECURRENT_SAME_HEAD_ANCHOR" and row["edit_distance"] == distance for row in lessons) for distance in ["1", "2", "3"]} == {"1": 43, "2": 35, "3": 10},
        "no_new_roots": all(row["new_root_required"] == "NO" for row in lessons),
        "groups_cover_lessons": sum(int(row["rare_recipes"]) for row in groups) == 113,
        "twelve_hard_cards": len(hard) == 12,
        "fixed_pages_only": {row["page"] for row in lessons} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "passed": sum(checks.values()), "total": len(checks)}
    (HERE / "SIX_HUNDRED_EIGHTY_FOURTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
