#!/usr/bin/env python3
"""Validate the five-case phase alignment."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    phases = read("SIX_HUNDRED_TWENTY_FIFTH_40_CASE_PHASE_ALIGNMENT.tsv")
    core = read("SIX_HUNDRED_TWENTY_FIFTH_19_COMMON_CORE_COMPONENTS.tsv")
    branches = read("SIX_HUNDRED_TWENTY_FIFTH_16_BRANCH_COMPONENTS.tsv")
    cases = read("SIX_HUNDRED_TWENTY_FIFTH_5_CASE_BRANCH_SUMMARY.tsv")
    universal = {"M01", "M02", "M03", "M04", "M06", "M08"}
    optional = {"M05", "M07"}
    present_by_module = {
        module: {row["case_id"] for row in phases if row["module_id"] == module and row["phase_present"] == "YES"}
        for module in universal | optional
    }
    checks = {
        "five_cases": len(cases) == 5 and {row["case_id"] for row in cases} == {f"C{i}" for i in range(1, 6)},
        "forty_phase_rows": len(phases) == 40 and len({(row["case_id"], row["module_id"]) for row in phases}) == 40,
        "eight_modules": {row["module_id"] for row in phases} == {f"M{i:02d}" for i in range(1, 9)},
        "six_universal_modules": all(present_by_module[module] == {f"C{i}" for i in range(1, 6)} for module in universal),
        "collect_missing_only_c5": present_by_module["M05"] == {"C1", "C2", "C3", "C4"},
        "ready_present_only_c1_c3": present_by_module["M07"] == {"C1", "C2", "C3"},
        "nineteen_common_components": len(core) == 19 and all(row["core_status"] == "PRESENT_IN_ALL_FIVE_COMPLETE_CASES" for row in core),
        "sixteen_branch_components": len(branches) == 16,
        "nine_single_case_components": sum(row["unique_to_one_case"] == "YES" for row in branches) == 9,
        "all_cases_have_core": all(row["six_module_core_present"] == "YES" for row in cases),
        "all_branch_cues_concrete": all(row["branch_cues_de"] and row["case_specific_reading_de"] for row in cases),
        "c1_unique_lsh_os": next(row for row in cases if row["case_id"] == "C1")["exclusive_components"] == "LSH|OS",
        "c2_unique_s": next(row for row in cases if row["case_id"] == "C2")["exclusive_components"] == "S",
        "c3_unique_cfh": next(row for row in cases if row["case_id"] == "C3")["exclusive_components"] == "CFH",
        "c4_unique_an_ld_talam": next(row for row in cases if row["case_id"] == "C4")["exclusive_components"] == "AN|LD|TALAM",
        "c5_unique_da_ho": next(row for row in cases if row["case_id"] == "C5")["exclusive_components"] == "DA|HO",
        "covered_main_statements": sum(int(row["statements"]) for row in cases) == 115,
        "covered_main_events": sum(int(row["events"]) for row in cases) == 372,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_TWENTY_FIFTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
