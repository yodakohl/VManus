#!/usr/bin/env python3
"""Prove frozen LRG001 synthetic invariance under the official STA alphabet."""

from __future__ import annotations

import os

for variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[variable] = "1"

import hashlib
import importlib.util
import json
import multiprocessing as mp
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
CORE_PATH = HERE / "lrg001_core.py"
RUNNER_PATH = HERE / "run_lrg001_target_blind_calibration.py"
CAPACITY = RESULTS / "lrg001_label_register_capacity.tsv"
FROZEN = RESULTS / "lrg001_target_blind_calibration_v2.json"
OUT_JSON = RESULTS / "lrg001_official_alphabet_reconciliation.json"
OUT_REPORT = RESULTS / "lrg001_official_alphabet_reconciliation_report.md"
OFFICIAL = "ABCDEFGHJKLMNPQRSTUVWXYZ"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    import sys
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise RuntimeError("reconciliation output exists")
    if len(OFFICIAL) != 24 or len(set(OFFICIAL)) != 24:
        raise RuntimeError("official alphabet contract")
    core = load("lrg001_core", CORE_PATH)
    runner = load("lrg001_calibration_rebound", RUNNER_PATH)
    core.ALPHABET = OFFICIAL
    core.INDEX = {value: index for index, value in enumerate(OFFICIAL)}
    runner.ALPHABET = OFFICIAL
    runner.GEOMETRY = core.load_geometry(CAPACITY)
    numbers = np.asarray([int(value[1:]) for value in runner.GEOMETRY.folios])
    runner.COEFFICIENT_EVEN = core.assignment_coefficients(runner.GEOMETRY, numbers % 2 == 0)
    runner.COEFFICIENT_ODD = core.assignment_coefficients(runner.GEOMETRY, numbers % 2 == 1)
    tasks = [("NULL", world) for world in range(64)] + [
        (family, world) for family in runner.FAMILIES for world in range(8)
    ]
    with mp.get_context("fork").Pool(32) as pool:
        records = pool.map(runner.worker, tasks)
    frozen = json.loads(FROZEN.read_text(encoding="utf-8"))
    if records != frozen["records"]:
        for index, (observed, expected) in enumerate(zip(records, frozen["records"], strict=True)):
            if observed != expected:
                raise RuntimeError(f"synthetic invariance mismatch {index} {observed['family']} {observed['world']}")
        raise RuntimeError("synthetic record mismatch")
    assignment_digests = {
        "EVEN_HELD": core.sha256_array(runner.COEFFICIENT_EVEN[1]),
        "ODD_HELD": core.sha256_array(runner.COEFFICIENT_ODD[1]),
    }
    if assignment_digests != frozen["assignment_digests"]:
        raise RuntimeError("assignment mismatch")
    result = {
        "status": "PASS_EXACT_OFFICIAL_ALPHABET_SYNTHETIC_INVARIANCE",
        "checks": len(records) * 32 + 25,
        "discrepancies": 0,
        "official_alphabet": OFFICIAL,
        "official_alphabet_size": len(OFFICIAL),
        "frozen_records_reconstructed_exactly": len(records),
        "assignment_digests": assignment_digests,
        "frozen_calibration_sha256": digest(FROZEN),
        "frozen_core_sha256": digest(CORE_PATH),
        "frozen_runner_sha256": digest(RUNNER_PATH),
        "decision": "GO_SEPARATELY_FROZEN_RECOVERY_ONLY",
        "target_source_accessed": False,
        "claim_ceiling": "This proves only category-name bijection invariance of the frozen synthetic instrument and supplies no manuscript result, profile, meaning, plaintext, or translation.",
    }
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    temporary = OUT_JSON.with_suffix(".json.tmp"); temporary.write_text(text, encoding="utf-8", newline="\n"); temporary.replace(OUT_JSON)
    report = "\n".join([
        "# LRG001 official-alphabet reconciliation", "",
        "Status: **PASS_EXACT_OFFICIAL_ALPHABET_SYNTHETIC_INVARIANCE**.", "",
        f"Rebinding only the 24 name-to-index positions to `{OFFICIAL}` reconstructs all 136 frozen synthetic records and both 8,192-assignment matrices exactly, with zero discrepancies.", "",
        "This proves the calibration is invariant to the corrected category names. It authorizes only a separately frozen clean target recovery and supplies no manuscript result, label profile, meaning, plaintext, or translation.", "",
    ])
    temporary = OUT_REPORT.with_suffix(".md.tmp"); temporary.write_text(report, encoding="utf-8", newline="\n"); temporary.replace(OUT_REPORT)
    print(text, end="")


if __name__ == "__main__":
    main()
