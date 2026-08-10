#!/usr/bin/env python3
"""Recover the unscored LRG001 target with the frozen clean implementation."""

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
FREEZE = HERE / "LRG001_RECOVERY_FREEZE.json"
CLEAN_SOURCE = HERE / "validate_lrg001_target_blind_calibration_v2.py"
CAPACITY = RESULTS / "lrg001_label_register_capacity.tsv"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
OUT_JSON = RESULTS / "lrg001_label_register_target_recovered.json"
OUT_REPORT = RESULTS / "lrg001_label_register_target_recovered_report.md"
VALIDATION_JSON = RESULTS / "lrg001_label_register_target_recovered_validation.json"
VALIDATION_REPORT = RESULTS / "lrg001_label_register_target_recovered_validation_report.md"
ORIGINAL_PATHS = (
    RESULTS / "lrg001_label_register_target.json",
    RESULTS / "lrg001_label_register_target_report.md",
    RESULTS / "lrg001_label_register_target_validation.json",
    RESULTS / "lrg001_label_register_target_validation_report.md",
)
OFFICIAL = "ABCDEFGHJKLMNPQRSTUVWXYZ"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def atomic_new(path: Path, text: str) -> None:
    if path.exists():
        raise RuntimeError(f"output exists {path.name}")
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    os.link(temporary, path)
    temporary.unlink()


def main() -> None:
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    paths = [OUT_JSON, OUT_REPORT, VALIDATION_JSON, VALIDATION_REPORT]
    if freeze["status"] != "FROZEN_LRG001_CLEAN_RECOVERY" or freeze["result_paths"] != [str(path.relative_to(ROOT)) for path in paths]:
        raise RuntimeError("recovery freeze contract")
    for relative, expected in freeze["frozen_files"].items():
        if digest(ROOT / relative) != expected:
            raise RuntimeError(f"recovery freeze drift {relative}")
    if any(path.exists() for path in paths):
        raise RuntimeError("recovery output exists")
    if any(path.exists() for path in ORIGINAL_PATHS):
        raise RuntimeError("original target artifact exists")
    spec = importlib.util.spec_from_file_location("lrg001_clean_recovery", CLEAN_SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load clean scorer")
    clean = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(clean)
    clean.ALPHABET = OFFICIAL
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
                raise RuntimeError("recovery target count drift")
            for row in rows:
                if len(row["family_surface"]) != int(row["symbol_count"]):
                    raise RuntimeError("recovery target length drift")
                if any(symbol not in OFFICIAL for symbol in row["family_surface"]):
                    raise RuntimeError("nonofficial family")
                sequences.append([OFFICIAL.index(symbol) for symbol in row["family_surface"]])
                labels.append(value)
    matrix = clean.features(sequences)
    y = np.asarray(labels, dtype=np.int8)
    if len(y) != 2767 or int(y.sum()) != 288 or matrix.shape != (2767, 648):
        raise RuntimeError("recovery target geometry drift")
    evaluation = clean.evaluate(matrix, y)
    passed = bool(evaluation["passes"])
    status = (
        "RECOVERED_CONFIRMED_TRANSFERABLE_SOURCE_NATIVE_LABEL_PROFILE" if passed
        else "RECOVERED_FINAL_NONCONFIRMATION_SOURCE_NATIVE_LABEL_PROFILE"
    )
    decision = "PROFILE_PROJECTION_AUTHORIZED_AFTER_RECOVERY_VALIDATION" if passed else "CLOSE_EXACT_LRG001_REPRESENTATION"
    claim = (
        "This is a clean-scorer recovery after the sealed production runner failed before scoring. A pass establishes only a transferable label-associated structural profile under exact page, length, folio-parity, and B/P controls. "
        "Neither outcome supplies an identifier, name, noun, object ownership, part of speech, language, meaning, plaintext, or translation."
    )
    result = {
        "status": status, "decision": decision, "claim_ceiling": claim,
        "recovery_freeze_sha256": digest(FREEZE), "original_production_result_exists": False,
        "target_rows_accessed": True,
        "original_production_failure_stage": "AFTER_TARGET_JOIN_BEFORE_FEATURE_MATRIX",
        "recovery_implementation": "FROZEN_NONIMPORTING_CALIBRATION_VALIDATOR",
        "official_alphabet": OFFICIAL,
        "counts": {"rows": len(y), "labels": int(y.sum()), "prose": int(len(y)-y.sum()), "cells": len(set(clean.G["cell"])), "physical_folios": len(set(clean.G["folio"])), "feature_columns": matrix.shape[1]},
        "target_matrix_sha256": clean.array_digest(matrix), "label_vector_sha256": clean.array_digest(y),
        "assignment_digests": {"EVEN_HELD": clean.array_digest(clean.EVEN_COEFFICIENT[1]), "ODD_HELD": clean.array_digest(clean.ODD_COEFFICIENT[1])},
        "target_sequences_emitted": False, "individual_feature_weights_emitted": False,
        "evaluation": evaluation,
    }
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    report = "\n".join([
        "# LRG001 clean target recovery", "", f"Status: **{status}**.", "",
        "The original sealed production runner failed before feature construction or scoring. This result is recovered once with the previously validated clean scorer and the official 24-family alphabet.", "",
        "| direction | effect | p | positive folios | B effect | P effect | min deletion | concentration | pass |", "|---|---:|---:|---:|---:|---:|---:|---:|---|",
        *[f"| {name} | {value['effect']:+.9f} | {value['p']:.9f} | {value['positive_folios']}/{value['folio_count']} | {value['section_effects']['B']:+.9f} | {value['section_effects']['P']:+.9f} | {value['minimum_deletion']:+.9f} | {value['maximum_absolute_folio_concentration']:.9f} | {value['passes']} |" for name, value in evaluation["directions"].items()],
        "", f"Independent-profile cosine: **{evaluation['profile_cosine']:+.9f}**.", "", f"Decision: **{decision}**.", "",
        "No individual family weight, form, sequence, identifier, name, noun, object ownership, meaning, plaintext, or translation is emitted.", "",
    ])
    if any(path.exists() for path in paths) or any(path.exists() for path in ORIGINAL_PATHS):
        raise RuntimeError("concurrent target artifact")
    atomic_new(OUT_JSON, text)
    try:
        atomic_new(OUT_REPORT, report)
    except Exception:
        OUT_JSON.unlink(missing_ok=True)
        raise
    print(text, end="")


if __name__ == "__main__":
    main()
