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
    true = read("SEVEN_HUNDRED_EIGHTY_SEVENTH_91_TRUE_GRADE_EVENTS.tsv")
    false = read("SEVEN_HUNDRED_EIGHTY_SEVENTH_70_NONGRADE_E_EVENTS.tsv")
    recipes = read("SEVEN_HUNDRED_EIGHTY_SEVENTH_51_GRADED_RECIPES.tsv")
    mechanisms = read("SEVEN_HUNDRED_EIGHTY_SEVENTH_3_NONGRADE_MECHANISMS.tsv")
    grades = read("SEVEN_HUNDRED_EIGHTY_SEVENTH_3_GRADE_LEVELS.tsv")
    exceptions = read("SEVEN_HUNDRED_EIGHTY_SEVENTH_2_CONTRACTED_EE_EVENTS.tsv")
    rules = read("SEVEN_HUNDRED_EIGHTY_SEVENTH_4_GRADE_RULES.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_EIGHTY_SEVENTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    grade = {row["grade"]: row for row in grades}
    mechanism = {row["non_grade_mechanism"]: row for row in mechanisms}
    checks = {
        "counts_91_70_51_3_3_2_4": (len(true), len(false), len(recipes), len(mechanisms), len(grades), len(exceptions), len(rules)) == (91, 70, 51, 3, 3, 2, 4),
        "grade_counts_49_40_2": [int(grade[key]["events"]) for key in ("E", "EE", "EEE")] == [49, 40, 2],
        "matches_49_38_2": [int(grade[key]["matching_run_events"]) for key in ("E", "EE", "EEE")] == [49, 38, 2],
        "false_mechanisms_38_15_17": [int(mechanism[key]["events"]) for key in ("E_EMBEDDED_IN_CHED_CORE", "E_EMBEDDED_IN_SHED_CORE", "E_IN_WRAPPER_OR_OTHER_WHOLE_CORE")] == [38, 15, 17],
        "exceptions_are_shey_ee": {row["surface"] for row in exceptions} == {"shey"} and {row["effective_grade"] for row in exceptions} == {"EE"},
        "false_never_adds_grade": all(row["grade_reading_added"] == "NONE" for row in false),
        "fixed_pages_only": all("f84" not in "\t".join(row.values()).lower() for rows in (true, false, recipes, mechanisms, grades, exceptions, rules) for row in rows),
        "summary_pass": summary["status"] == "PASS" and (summary["true_grade_events"], summary["grade_surface_matches"], summary["nongrade_visible_e_events"]) == (91, 89, 70),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_EIGHTY_SEVENTH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
