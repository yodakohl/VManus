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
    forms = read("FOUR_HUNDRED_EIGHTY_THIRD_SEVEN_RECURRENT_FORM_CLASSES.tsv")
    phases = read("FOUR_HUNDRED_EIGHTY_THIRD_EIGHT_RECURRENT_PHASE_SKELETONS.tsv")
    assignments = read("FOUR_HUNDRED_EIGHTY_THIRD_116_FORM_CLASS_ASSIGNMENTS.tsv")
    local = read("FOUR_HUNDRED_EIGHTY_THIRD_65_LOCAL_FORMS.tsv")
    units = read("FOUR_HUNDRED_EIGHTY_THIRD_14_FORM_CLASS_UNIT_EDITIONS.tsv")
    checks = {
        "forms_7": len(forms) == 7,
        "phase_skeletons_8": len(phases) == 8,
        "assignments_116": len(assignments) == 116,
        "assignment_ids_unique": len({row["statement_id"] for row in assignments}) == 116,
        "recurrent_51": sum(row["form_status"] == "RECURRENT_APPRENTICE_FORM" for row in assignments) == 51,
        "local_65": len(local) == 65,
        "herbal_recurrent_zero": sum(row["form_status"] == "RECURRENT_APPRENTICE_FORM" and row["register"] == "HERBAL" for row in assignments) == 0,
        "bio_recurrent_51": sum(row["form_status"] == "RECURRENT_APPRENTICE_FORM" and row["register"] == "BIOLOGICAL" for row in assignments) == 51,
        "event_sum_381": sum(int(row["events"]) for row in assignments) == 381,
        "units_14": len(units) == 14,
        "groups_776": sum(int(row["groups"]) for row in units) == 776,
        "fixed_pages_only": {row["page"] for row in assignments + units} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"},
        "sealed_pages_absent": all(not row.get("page", "").startswith("f84") for row in assignments + local + units),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_EIGHTY_THIRD_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(result["status"])
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
