#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    choices = rows("HUNDRED_THIRTY_THIRD_THIRTEEN_WHEN_CHOICES.tsv")
    jobs = rows("HUNDRED_THIRTY_THIRD_FOUR_WHAT_HOW_WHEN_JOBS.tsv")
    menu = rows("HUNDRED_THIRTY_THIRD_395_ASTRO_JOB_MENU.tsv")
    ledger = rows("HUNDRED_THIRTY_THIRD_776_JOB_LEDGER.tsv")
    active = rows("HUNDRED_THIRTY_THIRD_402_ACTIVE_JOB_GROUPS.tsv")
    checks = {
        "choices_13": len(choices) == 13,
        "jobs_4": len(jobs) == 4,
        "menu_395": len(menu) == 395,
        "ledger_776": len(ledger) == 776,
        "active_402": len(active) == 402,
        "selected_astro_21": sum(row["menu_status"] == "SELECTED_FOR_SAMPLE_JOB" for row in menu) == 21,
        "unselected_astro_374": sum(row["menu_status"] == "UNSELECTED_REFERENCE_OPTION" for row in menu) == 374,
        "all_astro_orientation_none": all(row["orientation"].startswith("NONE") for row in menu),
        "all_astro_crosspage_none": all(row["crosspage_key"] == "NONE" for row in menu),
        "unified_serials_unique": len({row["unified_serial"] for row in ledger}) == 776,
        "no_empty_cells": all(all(value for value in row.values()) for table in (choices, jobs, menu, ledger, active) for row in table),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
