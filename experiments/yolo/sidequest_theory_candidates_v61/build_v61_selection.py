#!/usr/bin/env python3
"""Bind the selected four-role V61 continuation edition."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    role_validations = [HERE / f"V61_R{i}_VALIDATION.json" for i in range(1, 5)]
    source_boundary = HERE / "V61_R1_46_LINE_BOUNDARY_INVENTORY.tsv"
    source_statements = HERE / "V61_R1_116_STATEMENT_CLAUSE_MAP.tsv"
    source_records = HERE / "V61_R1_11_RECORD_CONTINUATION_SUMMARY.tsv"
    boundaries = read(source_boundary)
    statements = read(source_statements)
    records = read(source_records)
    outputs = {
        "boundaries": HERE / "V61_SELECTED_46_LINE_BOUNDARIES.tsv",
        "statements": HERE / "V61_SELECTED_116_SOURCE_STATEMENTS.tsv",
        "records": HERE / "V61_SELECTED_11_RECORD_CONTINUATIONS.tsv",
    }
    shutil.copyfile(source_boundary, outputs["boundaries"])
    shutil.copyfile(source_statements, outputs["statements"])
    shutil.copyfile(source_records, outputs["records"])
    class_col = "selected_classification"
    if class_col not in boundaries[0]:
        class_col = "classification"
    classes = Counter(row[class_col] for row in boundaries)
    statement_fields = []
    for row in statements:
        for candidate in ("constituent_field_ids", "constituent_fields", "field_ids"):
            if candidate in row:
                statement_fields.extend(x for x in row[candidate].split("|") if x)
                break
    checks = {
        "four_role_validations_pass": all(json.loads(path.read_text(encoding="utf-8"))["status"] == "PASS" for path in role_validations),
        "boundaries_46": len(boundaries) == 46,
        "statements_116": len(statements) == 116,
        "records_11": len(records) == 11,
        "all_135_fields_once": len(statement_fields) == 135 and len(set(statement_fields)) == 135,
        "class_profile": classes == Counter({"CONTINUE_SAME_CLAUSE": 19, "RESUME_ACTIVE_ITEM": 8, "NEXT_PARALLEL_CELL": 10, "START_NEW_CLAUSE": 8, "UNRESOLVED": 1}),
        "f82_carry_selected": any(row.get("from_locus") == "f82r.3" and row.get("to_locus") == "f82r.4" and row[class_col] == "CONTINUE_SAME_CLAUSE" for row in boundaries),
        "no_f84": not any("f84" in "\t".join(row.values()) for row in boundaries + statements + records),
    }
    validation = {
        "schema": "SIDEQUEST_V61_FOUR_ROLE_SELECTION_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "selected_model": "R1_CONSERVATIVE_MIXED_CLAUSE_CELL_MAP",
        "role_validation_hashes": {str(path.relative_to(ROOT)): sha(path) for path in role_validations},
        "outputs": {str(path.relative_to(ROOT)): sha(path) for path in outputs.values()},
    }
    (HERE / "V61_SELECTION_VALIDATION.json").write_text(json.dumps(validation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if validation["status"] != "PASS":
        raise SystemExit(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
