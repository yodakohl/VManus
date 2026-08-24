#!/usr/bin/env python3
"""Validate the three-person apprentice workday."""

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    people = read("SIX_HUNDRED_FIFTH_THREE_PERSON_WORKSHOP.tsv")
    rules = read("SIX_HUNDRED_FIFTH_FIFTEEN_APPRENTICE_RULES.tsv")
    trace = read("SIX_HUNDRED_FIFTH_122_STEP_WORKDAY_TRACE.tsv")
    errors = read("SIX_HUNDRED_FIFTH_TWELVE_COMMON_ERRORS.tsv")
    prep = [row for row in trace if row["task_phase"] == "PREPARE_PRODUCT"]
    astro = [row for row in trace if row["task_phase"] == "OPTIONAL_ASTRO_CONDITION"]
    operate = [row for row in trace if row["task_phase"] == "OPERATE_OR_APPLY"]
    prose = prep + operate
    checks = {
        "three_people": len(people) == 3 and {row["person_id"] for row in people} == {"P1", "P2", "P3"},
        "fifteen_rules": len(rules) == 15,
        "twelve_errors": len(errors) == 12,
        "trace122": len(trace) == 122 and [int(row["workday_step"]) for row in trace] == list(range(1, 123)),
        "prep19": len(prep) == 19,
        "astro6": len(astro) == 6,
        "operate97": len(operate) == 97,
        "prose_statements116": len({row["source_id"] for row in prose}) == 116,
        "prose_groups381": sum(int(row["written_group_count"]) for row in prose) == 381,
        "all_six_cases": {row["case_id"] for row in trace} == {f"C{i}" for i in range(1, 7)},
        "all_steps_instructed": all(row["spoken_instruction_de"] and row["master_check_de"] for row in trace),
        "only_master_selects": next(row for row in people if row["person_id"] == "P1")["may_change_meaning"].startswith("YES") and all(row["may_change_meaning"].startswith("NO") for row in people if row["person_id"] != "P1"),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_FIFTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
