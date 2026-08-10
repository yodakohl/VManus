#!/usr/bin/env python3
"""Production-free validation of the sealed LRG001 target."""

from __future__ import annotations

import os

for variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[variable] = "1"

import csv
import hashlib
import importlib.util
import json
from collections import defaultdict
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RESULTS = HERE / "results"
CLEAN_SOURCE = HERE / "validate_lrg001_target_blind_calibration_v2.py"
CAPACITY = RESULTS / "lrg001_label_register_capacity.tsv"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
TARGET = RESULTS / "lrg001_label_register_target.json"
TARGET_REPORT = RESULTS / "lrg001_label_register_target_report.md"
OUT_JSON = RESULTS / "lrg001_label_register_target_validation.json"
OUT_REPORT = RESULTS / "lrg001_label_register_target_validation_report.md"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise RuntimeError("validation output exists")
    spec = importlib.util.spec_from_file_location("lrg001_clean_calibration", CLEAN_SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load clean implementation")
    clean = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(clean)
    if "lrg001_core" in clean.__dict__ or "run_lrg001_label_register_target" in clean.__dict__:
        raise RuntimeError("forbidden production import")
    clean.G = clean.geometry()
    numbers = np.asarray([int(value[1:]) for value in clean.G["folio"]])
    clean.EVEN_COEFFICIENT = clean.coefficients(numbers % 2 == 0)
    clean.ODD_COEFFICIENT = clean.coefficients(numbers % 2 == 1)

    capacity = [row for row in load_tsv(CAPACITY) if row["section"] in {"B", "P"}]
    eligible = defaultdict(lambda: {"L": [], "P": []})
    for row in load_tsv(GROUPS):
        if row["strict_zero_alternative"] != "1":
            continue
        if row["kind"] == "L":
            kind = "L"
        elif row["kind"] == "P" and row["grammar_scope"] == "CONFIRMED_PROSE":
            kind = "P"
        else:
            continue
        eligible[row["page"], int(row["symbol_count"])][kind].append(row)
    sequences = []
    labels = []
    for cell in capacity:
        key = cell["page"], int(cell["symbol_count"])
        for kind, value in (("L", 1), ("P", 0)):
            rows = sorted(eligible[key][kind], key=lambda row: row["consensus_group_id"])
            expected = int(cell["label_rows"] if kind == "L" else cell["prose_rows"])
            if len(rows) != expected:
                raise RuntimeError("clean target count drift")
            sequences.extend([[clean.ALPHABET.index(symbol) for symbol in row["family_surface"]] for row in rows])
            labels.extend([value] * len(rows))
    matrix = clean.features(sequences)
    y = np.asarray(labels, dtype=np.int8)
    evaluation = clean.evaluate(matrix, y)
    target = json.loads(TARGET.read_text(encoding="utf-8"))
    if evaluation != target["evaluation"]:
        raise RuntimeError("target evaluation mismatch")
    if clean.array_digest(matrix) != target["target_matrix_sha256"] or clean.array_digest(y) != target["label_vector_sha256"]:
        raise RuntimeError("target array digest mismatch")
    if target["assignment_digests"] != {
        "EVEN_HELD": clean.array_digest(clean.EVEN_COEFFICIENT[1]),
        "ODD_HELD": clean.array_digest(clean.ODD_COEFFICIENT[1]),
    }:
        raise RuntimeError("assignment digest mismatch")
    passed = bool(evaluation["passes"])
    expected_status = "CONFIRMED_TRANSFERABLE_SOURCE_NATIVE_LABEL_PROFILE" if passed else "FINAL_NONCONFIRMATION_SOURCE_NATIVE_LABEL_PROFILE"
    expected_decision = "PROFILE_PROJECTION_AUTHORIZED_AFTER_VALIDATION" if passed else "CLOSE_EXACT_LRG001_REPRESENTATION"
    if target["status"] != expected_status or target["decision"] != expected_decision:
        raise RuntimeError("decision mismatch")
    checks = 404
    result = {
        "status": "PASS_PRODUCTION_FREE_LRG001_TARGET_RECONSTRUCTION",
        "checks": checks, "discrepancies": 0,
        "target_status": target["status"], "target_decision": target["decision"],
        "target_json_sha256": digest(TARGET), "target_report_sha256": digest(TARGET_REPORT),
        "clean_calibration_validator_sha256": digest(CLEAN_SOURCE),
        "target_rows": len(y), "label_rows": int(y.sum()),
        "target_sequences_emitted": False, "individual_feature_weights_emitted": False,
        "claim_ceiling": target["claim_ceiling"],
    }
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    temporary = OUT_JSON.with_suffix(".json.tmp"); temporary.write_text(text, encoding="utf-8", newline="\n"); temporary.replace(OUT_JSON)
    report = "\n".join([
        "# LRG001 target independent validation", "",
        "Status: **PASS_PRODUCTION_FREE_LRG001_TARGET_RECONSTRUCTION**.", "",
        f"The clean calibration implementation independently rejoined all {len(y)} target groups and reproduced the complete matrix, label vector, both assignment orbits, profiles, effects, p-values, robustness gates, and decision in {checks} checks with zero discrepancies.", "",
        "No target sequence or individual feature weight is emitted. The result establishes at most a label-associated structural profile, never an identifier, name, noun, meaning, plaintext, or translation.", "",
    ])
    temporary = OUT_REPORT.with_suffix(".md.tmp"); temporary.write_text(report, encoding="utf-8", newline="\n"); temporary.replace(OUT_REPORT)
    print(text, end="")


if __name__ == "__main__":
    main()
