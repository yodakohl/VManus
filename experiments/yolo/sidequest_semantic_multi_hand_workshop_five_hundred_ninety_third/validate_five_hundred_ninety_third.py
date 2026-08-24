#!/usr/bin/env python3
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    roles = read("FIVE_HUNDRED_NINETY_THIRD_FIVE_TASK_ROLES.tsv")
    lessons = read("FIVE_HUNDRED_NINETY_THIRD_TWELVE_LESSON_CURRICULUM.tsv")
    assignments = read("FIVE_HUNDRED_NINETY_THIRD_FOURTEEN_UNIT_ASSIGNMENTS.tsv")
    workloads = read("FIVE_HUNDRED_NINETY_THIRD_WORKLOAD_LEVELS.tsv")
    errors = read("FIVE_HUNDRED_NINETY_THIRD_TEN_ERROR_DRILLS.tsv")
    staffing = read("FIVE_HUNDRED_NINETY_THIRD_STAFFING_MODELS.tsv")
    checks = {
        "roles5": len(roles) == 5 and len({row["task_role"] for row in roles}) == 5,
        "lessons12": len(lessons) == 12 and [int(row["lesson"]) for row in lessons] == list(range(1, 13)),
        "units14": len(assignments) == 14 and len({row["unit_id"] for row in assignments}) == 14,
        "groups776": sum(int(row["visible_groups"]) for row in assignments) == 776,
        "prose_copy_role": all(row["copy_role"] == "PROSE_SCRIBE" for row in assignments if row["section"] != "ASTRO"),
        "astro_copy_role": all(row["copy_role"] == "DIAGRAM_SCRIBE" for row in assignments if row["section"] == "ASTRO"),
        "all_apprentice_copyable": all(row["apprentice_can_copy_after_basic_course"] == "YES" for row in assignments),
        "workloads4": len(workloads) == 4 and sum(int(row["units"]) for row in workloads if row["workload"].startswith("PROSE")) == 116,
        "prose_workload381": sum(int(row["visible_groups"]) for row in workloads if row["workload"].startswith("PROSE")) == 381,
        "astro_workload395": next(int(row["visible_groups"]) for row in workloads if row["workload"] == "ASTRO_LOCAL_LABELS") == 395,
        "errors10": len(errors) == 10 and len({row["error"] for row in errors}) == 10,
        "staffing3": len(staffing) == 3 and [int(row["working_rank"]) for row in staffing] == [1, 2, 3],
        "minimum3": staffing[0]["shop_model"] == "THREE_PERSON_MINIMUM" and staffing[0]["people"] == "3",
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_NINETY_THIRD_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
