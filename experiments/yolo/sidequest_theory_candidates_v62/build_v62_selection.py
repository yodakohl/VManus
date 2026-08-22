#!/usr/bin/env python3
"""Bind V62's selected anonymous four-register machine."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def rows(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    validations = [HERE / f"V62_R{i}_VALIDATION.json" for i in range(1, 5)]
    sources = {
        "transitions": HERE / "V62_R3_116_STATE_TRANSITIONS.tsv",
        "inventory": HERE / "V62_R3_REGISTER_INVENTORY.tsv",
        "models": HERE / "V62_R3_REDUCED_REGISTER_MODELS.tsv",
        "errors": HERE / "V62_R3_IRREDUCIBLE_ERROR_AUDIT.tsv",
    }
    outputs = {
        "transitions": HERE / "V62_SELECTED_116_REGISTER_TRANSITIONS.tsv",
        "inventory": HERE / "V62_SELECTED_REGISTER_INVENTORY.tsv",
        "models": HERE / "V62_SELECTED_REDUCED_REGISTER_MODELS.tsv",
        "errors": HERE / "V62_SELECTED_ERROR_AUDIT.tsv",
    }
    for key in sources:
        shutil.copyfile(sources[key], outputs[key])
    transition_rows = rows(sources["transitions"])
    model_rows = rows(sources["models"])
    error_rows = rows(sources["errors"])
    model_text = "\n".join("\t".join(row.values()) for row in model_rows)
    checks = {
        "four_role_validations_pass": all(json.loads(path.read_text(encoding="utf-8"))["status"] == "PASS" for path in validations),
        "transitions_116": len(transition_rows) == 116,
        "all_11_records": len({row["record_unit_id"] for row in transition_rows}) == 11,
        "reduced_model_curve_present": all(value in model_text for value in ("9", "27", "88", "107", "116")),
        "error_audit_122": len(error_rows) == 122,
        "no_f84": not any("f84" in "\t".join(row.values()) for row in transition_rows),
    }
    validation = {
        "schema": "SIDEQUEST_V62_FOUR_ROLE_SELECTION_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "selected_model": "R3_ANONYMOUS_OWNER_ACTIVE_TARGET_PREVIOUS_MACHINE",
        "role_validation_hashes": {str(path.relative_to(ROOT)): sha(path) for path in validations},
        "outputs": {str(path.relative_to(ROOT)): sha(path) for path in outputs.values()},
    }
    (HERE / "V62_SELECTION_VALIDATION.json").write_text(json.dumps(validation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if validation["status"] != "PASS":
        raise SystemExit(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
