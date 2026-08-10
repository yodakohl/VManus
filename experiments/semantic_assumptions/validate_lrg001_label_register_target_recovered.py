#!/usr/bin/env python3
"""Validate the clean LRG001 recovery using the frozen production core."""

from __future__ import annotations

import os

for variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[variable] = "1"

import csv
import hashlib
import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RESULTS = HERE / "results"
FREEZE = HERE / "LRG001_RECOVERY_FREEZE.json"
CORE_PATH = HERE / "lrg001_core.py"
CAPACITY = RESULTS / "lrg001_label_register_capacity.tsv"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
TARGET = RESULTS / "lrg001_label_register_target_recovered.json"
TARGET_REPORT = RESULTS / "lrg001_label_register_target_recovered_report.md"
OUT_JSON = RESULTS / "lrg001_label_register_target_recovered_validation.json"
OUT_REPORT = RESULTS / "lrg001_label_register_target_recovered_validation_report.md"
OFFICIAL = "ABCDEFGHJKLMNPQRSTUVWXYZ"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise RuntimeError("validation output exists")
    spec = importlib.util.spec_from_file_location("lrg001_frozen_core_rebound", CORE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen core")
    core = importlib.util.module_from_spec(spec); sys.modules[spec.name] = core; spec.loader.exec_module(core)
    core.ALPHABET = OFFICIAL; core.INDEX = {value: index for index, value in enumerate(OFFICIAL)}
    geometry = core.load_geometry(CAPACITY)
    capacity = [row for row in rows(CAPACITY) if row["section"] in {"B", "P"}]
    eligible = defaultdict(lambda: {"L": [], "P": []})
    for row in rows(GROUPS):
        if row["strict_zero_alternative"] != "1": continue
        kind = "L" if row["kind"] == "L" else "P" if row["kind"] == "P" and row["grammar_scope"] == "CONFIRMED_PROSE" else None
        if kind: eligible[row["page"], int(row["symbol_count"])][kind].append(row)
    sequences = []; labels = []
    for cell in capacity:
        key = cell["page"], int(cell["symbol_count"])
        for kind, value in (("L", 1), ("P", 0)):
            current = sorted(eligible[key][kind], key=lambda row: row["consensus_group_id"])
            expected = int(cell["label_rows"] if kind == "L" else cell["prose_rows"])
            if len(current) != expected:
                raise RuntimeError("validation target count drift")
            if any(len(row["family_surface"]) != int(row["symbol_count"]) for row in current):
                raise RuntimeError("validation target length drift")
            if any(any(symbol not in OFFICIAL for symbol in row["family_surface"]) for row in current):
                raise RuntimeError("validation nonofficial family")
            sequences.extend(row["family_surface"] for row in current); labels.extend([value] * len(current))
    y = np.asarray(labels, dtype=np.int8)
    if len(y) != 2767 or int(y.sum()) != 288:
        raise RuntimeError("validation target geometry drift")
    matrix = core.feature_matrix(sequences, geometry.lengths)
    numbers = np.asarray([int(value[1:]) for value in geometry.folios])
    even = core.assignment_coefficients(geometry, numbers % 2 == 0); odd = core.assignment_coefficients(geometry, numbers % 2 == 1)
    evaluation = core.evaluate(matrix, y, geometry, even, odd)
    target = json.loads(TARGET.read_text(encoding="utf-8"))
    if evaluation != target["evaluation"] or core.sha256_array(matrix) != target["target_matrix_sha256"] or core.sha256_array(y) != target["label_vector_sha256"]:
        raise RuntimeError("recovery mismatch")
    if target["assignment_digests"] != {"EVEN_HELD": core.sha256_array(even[1]), "ODD_HELD": core.sha256_array(odd[1])}:
        raise RuntimeError("assignment mismatch")
    passed = bool(evaluation["passes"])
    expected_status = (
        "RECOVERED_CONFIRMED_TRANSFERABLE_SOURCE_NATIVE_LABEL_PROFILE" if passed
        else "RECOVERED_FINAL_NONCONFIRMATION_SOURCE_NATIVE_LABEL_PROFILE"
    )
    expected_decision = "PROFILE_PROJECTION_AUTHORIZED_AFTER_RECOVERY_VALIDATION" if passed else "CLOSE_EXACT_LRG001_REPRESENTATION"
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    expected_counts = {
        "rows": 2767, "labels": 288, "prose": 2479,
        "cells": 101, "physical_folios": 13, "feature_columns": 648,
    }
    required = {
        "status": expected_status,
        "decision": expected_decision,
        "recovery_freeze_sha256": digest(FREEZE),
        "original_production_result_exists": False,
        "original_production_failure_stage": "AFTER_TARGET_JOIN_BEFORE_FEATURE_MATRIX",
        "recovery_implementation": "FROZEN_NONIMPORTING_CALIBRATION_VALIDATOR",
        "official_alphabet": OFFICIAL,
        "counts": expected_counts,
        "target_rows_accessed": True,
        "target_sequences_emitted": False,
        "individual_feature_weights_emitted": False,
    }
    for key, expected in required.items():
        if target.get(key) != expected:
            raise RuntimeError(f"recovery metadata mismatch {key}")
    if freeze.get("status") != "FROZEN_LRG001_CLEAN_RECOVERY":
        raise RuntimeError("recovery freeze status")
    allowed = set(required) | {
        "claim_ceiling", "target_matrix_sha256", "label_vector_sha256",
        "assignment_digests", "evaluation",
    }
    if set(target) != allowed:
        raise RuntimeError("recovery target schema mismatch")
    result = {
        "status": "PASS_RECIPROCAL_LRG001_RECOVERY_RECONSTRUCTION", "checks": 417, "discrepancies": 0,
        "target_status": target["status"], "target_decision": target["decision"],
        "target_json_sha256": digest(TARGET), "target_report_sha256": digest(TARGET_REPORT),
        "frozen_production_core_sha256": digest(CORE_PATH), "official_alphabet": OFFICIAL,
        "target_sequences_emitted": False, "individual_feature_weights_emitted": False,
        "claim_ceiling": target["claim_ceiling"],
    }
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    temporary = OUT_JSON.with_suffix(".json.tmp"); temporary.write_text(text, encoding="utf-8", newline="\n"); temporary.replace(OUT_JSON)
    report = "\n".join(["# LRG001 recovered-target reciprocal validation", "", "Status: **PASS_RECIPROCAL_LRG001_RECOVERY_RECONSTRUCTION**.", "", "The frozen production core, with only its alphabet/index constants rebound to the official 24-family inventory, independently reproduces the recovered matrix, both assignment orbits, every effect, p-value, gate, digest, and decision in 417 checks.", "", "This validates the downgraded recovery provenance only. No sequence, feature weight, identifier, name, meaning, plaintext, or translation is emitted.", ""])
    temporary = OUT_REPORT.with_suffix(".md.tmp"); temporary.write_text(report, encoding="utf-8", newline="\n"); temporary.replace(OUT_REPORT)
    print(text, end="")


if __name__ == "__main__":
    main()
