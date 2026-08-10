#!/usr/bin/env python3
"""Reconcile the frozen DIC001 validator's two byte-digest discrepancies.

The frozen nonimporting validator used repeated multiplication for the squared
and cubed position columns; the producer used the preregistered exponentiation
spelling.  This diagnostic changes only that arithmetic order, reruns the same
independent reconstruction, and does not alter the target or its decision.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
VALIDATOR = HERE / "validate_dic001_drawing_interruption_target.py"
TARGET = HERE / "results" / "dic001_drawing_interruption_target.json"
TARGET_REPORT = HERE / "results" / "dic001_drawing_interruption_target_report.md"
FROZEN_VALIDATION = HERE / "results" / "dic001_drawing_interruption_target_validation.json"
OUT = HERE / "results" / "dic001_target_arithmetic_order_reconciliation.json"
OUT_REPORT = HERE / "results" / "dic001_target_arithmetic_order_reconciliation_report.md"
EXPECTED = {
    VALIDATOR: "4a24b39a626dcec076b1edb0556ffeb8343c065f9a511e0a43d09960d7f7047a",
    TARGET: "6d08072850be1fcfa183f72368a1f7657eb96c40b1b7a5d42b11216e398c12e8",
    TARGET_REPORT: "49aee3741d9e7690c6b463304f903d72e2b321a02da531b05e9dbbdbb67596ab",
}


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def corrected_basis(panel, neighbors):
    n = len(panel); columns = [np.ones(n)]
    pages = sorted({row["page"] for row in panel})
    columns += [np.array([row["page"] == page for row in panel], dtype=float) for page in pages[1:]]
    position = np.array([float(row["normalized_boundary_position"]) for row in panel])
    columns += [position, position ** 2, position ** 3]
    decile = np.minimum((10 * position).astype(np.int64), 9)
    columns += [(decile == value).astype(float) for value in range(1, 10)]
    group_count = np.minimum(np.array([int(row["group_count"]) for row in panel]), 20)
    columns += [(group_count == value).astype(float) for value in sorted(set(group_count))[1:]]
    left = np.array([min(8, len(a["family_surface"])) for a, _ in neighbors])
    right = np.array([min(8, len(b["family_surface"])) for _, b in neighbors])
    cells = sorted(set(zip(left.tolist(), right.tolist())))
    columns += [((left == a) & (right == b)).astype(float) for a, b in cells[1:]]
    return np.column_stack(columns), cells


def main():
    for path, expected in EXPECTED.items():
        if sha(path) != expected: raise SystemExit("input drift: " + path.name)
    frozen = json.loads(FROZEN_VALIDATION.read_text())
    if frozen["discrepancies"] != ["root.null.matrix_sha256: value", "root.transform.residual_score_sha256: value"]:
        raise SystemExit("unexpected frozen validation discrepancy set")
    spec = importlib.util.spec_from_file_location("dic001_frozen_validator", VALIDATOR)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    module.build_basis = corrected_basis
    expected, report = module.reconstruct()
    checks, errors, maximum = module.compare(expected, json.loads(TARGET.read_text()))
    report_exact = report == TARGET_REPORT.read_text()
    if not report_exact: errors.append("target report mismatch")
    result = {
        "experiment": "DIC001_TARGET_ARITHMETIC_ORDER_RECONCILIATION",
        "status": "PASS" if not errors else "FAIL",
        "checks": checks + 1 + len(EXPECTED),
        "discrepancies": errors,
        "maximum_numeric_abs_difference": maximum,
        "corrected_operation": "POSITION_POWER_COLUMNS_USE_EXPONENTIATION_AS_IN_FROZEN_PRODUCER",
        "residual_score_sha256": expected["transform"]["residual_score_sha256"],
        "null_matrix_sha256": expected["null"]["matrix_sha256"],
        "report_exact": report_exact,
        "reconstructed_decision": expected["decision"],
        "scientific_method_or_threshold_changed": False,
        "claim_ceiling": "Arithmetic-order reconciliation of the frozen production-free target reconstruction only; no new manuscript association, word, meaning, plaintext, or translation.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    OUT_REPORT.write_text(
        "# DIC001 target arithmetic-order reconciliation\n\n"
        f"Status: **{result['status']}** with **{result['checks']}** checks and **{len(errors)}** discrepancies.\n\n"
        "Replacing only repeated multiplication with the producer's exponentiation spelling for the preregistered position powers makes every target-result field, both score digests, the complete null-matrix digest, and the report exact with zero numeric difference. No scientific method, threshold, gate, target value, or decision changed.\n"
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    if errors: raise SystemExit(1)


if __name__ == "__main__": main()
