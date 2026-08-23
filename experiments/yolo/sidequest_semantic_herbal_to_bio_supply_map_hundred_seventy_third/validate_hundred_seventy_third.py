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
    matrix = read("HUNDRED_SEVENTY_THIRD_24_PRODUCT_STATION_MATRIX.tsv")
    plan = read("HUNDRED_SEVENTY_THIRD_6_RECORD_SUPPLY_PLAN.tsv")
    clauses = read("HUNDRED_SEVENTY_THIRD_97_BIO_CLAUSE_SUPPLY_EDITION.tsv")
    checks = {
        "complete_4x6_matrix": len(matrix) == 24 and len({(row["job_id"], row["bio_record"]) for row in matrix}) == 24,
        "seven_selected_links": sum(row["selection"] != "NOT_SELECTED" for row in matrix) == 7,
        "all_selected_have_bridge": all(int(row["exact_bridge_count"]) > 0 for row in matrix if row["selection"] != "NOT_SELECTED"),
        "six_record_plan": len(plan) == 6 and {row["bio_record"] for row in plan} == {f"B{i}" for i in range(1, 7)},
        "all_97_bio_clauses": len(clauses) == 97,
        "all_records_covered": {row["record_unit_id"] for row in clauses} == {f"B{i}" for i in range(1, 7)},
        "all_clauses_concrete": all(row["product_supplied_clause_de"].strip() for row in clauses),
        "no_dictionary_change": {row["dictionary_change"] for row in clauses} == {"NO"},
        "only_fixed_pages": {row["page"] for row in clauses} == {"f81v", "f82r", "f83r"},
        "no_visible_pointer_claim": {row["cross_page_status"] for row in plan} == {"WORKSHOP_SUPPLY_PLAN_NOT_VISIBLE_POINTER"},
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
