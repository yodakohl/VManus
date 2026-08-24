#!/usr/bin/env python3
"""Validate the six complete workshop cases."""

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    cases = read("SIX_HUNDRED_THIRD_SIX_COMPLETE_CASES.tsv")
    statements = read("SIX_HUNDRED_THIRD_116_STATEMENT_CASE_EDITION.tsv")
    events = read("SIX_HUNDRED_THIRD_381_EVENT_CASE_BINDING.tsv")
    inputs = read("SIX_HUNDRED_THIRD_SIXTEEN_INTERCHANGEABLE_INPUTS.tsv")
    checks = {
        "six_cases": len(cases) == 6 and {row["case_id"] for row in cases} == {f"C{i}" for i in range(1, 7)},
        "five_preparation_sources": {row["herbal_source_record"] for row in cases if row["herbal_source_record"].startswith("H")} == {f"H{i}" for i in range(1, 6)},
        "six_bio_programs": {row["biological_program_record"] for row in cases} == {f"B{i}" for i in range(1, 7)},
        "sixteen_stations": len(inputs) == 16 and len({row["station_id"] for row in inputs}) == 16,
        "statements116": len(statements) == 116 and len({row["statement_id"] for row in statements}) == 116,
        "events381": len(events) == 381 and len({row["event_id"] for row in events}) == 381,
        "all_events_bound_to_statement": {row["statement_id"] for row in events} == {row["statement_id"] for row in statements},
        "all_cases_have_steps": {row["case_id"] for row in statements} == {row["case_id"] for row in cases},
        "all_products_used": {f"H{i}" for i in range(1, 6)} <= {row["main_product_id"] for row in cases} | {x for row in inputs for x in row["interchangeable_product_ids"].split("|")},
        "teaching_not_hidden_key": all(row["hidden_one_to_one_key_claim"] == "NO__SELECTED_TEACHING_EXAMPLE_ONLY" for row in cases),
        "all_steps_concrete": all(row["concrete_case_step_de"] for row in statements),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_THIRD_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
