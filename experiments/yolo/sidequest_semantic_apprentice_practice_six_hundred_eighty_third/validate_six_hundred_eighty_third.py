#!/usr/bin/env python3
"""Validate the twelve-family apprentice practice page."""

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
    subprocess.run(["python3", str(HERE / "build_six_hundred_eighty_third.py")], check=True)
    practice = read("SIX_HUNDRED_EIGHTY_THIRD_12_FAMILY_PRACTICE_PAGE.tsv")
    drills = read("SIX_HUNDRED_EIGHTY_THIRD_48_FOUR_STAGE_DRILLS.tsv")
    manual = read("SIX_HUNDRED_EIGHTY_THIRD_6_MASTER_APPRENTICE_STEPS.tsv")
    checks = {
        "twelve_families": len(practice) == 12 and len({row["component_recipe"] for row in practice}) == 12,
        "twenty_four_examples": len({value.split(":", 1)[0] for row in practice for value in [row["example_a"], row["example_b"]]}) == 24,
        "all_examples_from_fixed_pages": all(value.split(":")[1] in {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"} for row in practice for value in [row["example_a"], row["example_b"]]),
        "forty_eight_drills": len(drills) == 48,
        "four_stages_each": all(sum(row["lesson_no"] == str(lesson) for row in drills) == 4 for lesson in range(1, 13)),
        "six_manual_steps": len(manual) == 6,
        "all_mistakes_and_corrections": all(row["common_mistake_de"] and row["master_correction_de"] for row in practice),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "passed": sum(checks.values()), "total": len(checks)}
    (HERE / "SIX_HUNDRED_EIGHTY_THIRD_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
