#!/usr/bin/env python3
"""Create the one-run EO001 target freeze after all target-blind gates pass."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
FREEZE = BASE / "EO001_TARGET_FREEZE.json"
FILES = (
    BASE / "EO001_EXACT_FORM_ONSET_TRANSFER_CAPACITY_SPEC.md",
    BASE / "EO001_EXACT_FORM_ONSET_TRANSFER_PREREGISTRATION.md",
    BASE / "build_eo001_exact_form_onset_capacity.py",
    BASE / "validate_eo001_exact_form_onset_capacity.py",
    BASE / "eo001_core.py",
    BASE / "run_eo001_synthetic_preflight.py",
    BASE / "validate_eo001_synthetic_preflight_v2.py",
    BASE / "run_eo001_target.py",
    BASE / "validate_eo001_target.py",
    Path(__file__).resolve(),
    RESULTS / "eo001_exact_form_onset_capacity.tsv",
    RESULTS / "eo001_exact_form_onset_capacity.json",
    RESULTS / "eo001_exact_form_onset_capacity_validation.json",
    RESULTS / "eo001_synthetic_preflight_v2.json",
    RESULTS / "eo001_synthetic_preflight_v2_validation.json",
    RESULTS / "source_native_structural_interlinear_v1.tsv",
)
TARGET_OUTPUTS = (
    RESULTS / "eo001_target.json", RESULTS / "eo001_target_report.md",
    RESULTS / "eo001_target_validation.json", RESULTS / "eo001_target_validation_report.md",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def label(path: Path) -> str:
    return str(path.relative_to(BASE))


def main() -> None:
    if FREEZE.exists():
        raise SystemExit("EO001 target freeze already exists")
    missing = [str(path) for path in FILES if not path.is_file()]
    if missing:
        raise SystemExit(f"missing freeze files: {missing}")
    present = [str(path) for path in TARGET_OUTPUTS if path.exists()]
    if present:
        raise SystemExit(f"target artifacts already exist: {present}")
    capacity = json.loads((RESULTS / "eo001_exact_form_onset_capacity_validation.json").read_text())
    preflight = json.loads((RESULTS / "eo001_synthetic_preflight_v2.json").read_text())
    validation = json.loads((RESULTS / "eo001_synthetic_preflight_v2_validation.json").read_text())
    if capacity["status"] != "PASS_INDEPENDENT_SCORE_BLIND_CAPACITY_RECONSTRUCTION":
        raise SystemExit("capacity is not independently valid")
    if preflight["status"] != "PASS_TARGET_FREE_CALIBRATION" or not all(preflight["gates"].values()):
        raise SystemExit("preflight is not PASS")
    if validation["status"] != "PASS_INDEPENDENT_264_WORLD_RECONSTRUCTION" or validation["max_numeric_delta"] != 0:
        raise SystemExit("preflight validation is not exact PASS")
    payload = {
        "experiment": "EO001_EXACT_FORM_ONSET_TRANSFER_TARGET_FREEZE",
        "status": "SEALED_SINGLE_TARGET_AUTHORIZED",
        "frozen_files": {label(path): sha(path) for path in FILES},
        "target_source": "results/source_native_structural_interlinear_v1.tsv",
        "target_source_sha256": sha(RESULTS / "source_native_structural_interlinear_v1.tsv"),
        "target_artifacts_absent": [label(path) for path in TARGET_OUTPUTS],
        "authorized_runs": {"production_target": 1, "production_free_validation": 1},
        "target_rows_authorized": 1295,
        "target_features": ["EDGE_48", "BAG_24", "BIGRAM_576"],
        "claim_ceiling": "Exact-form same-folio continuation-construction transfer only; no clause, word, meaning, plaintext, language, cipher, or translation.",
    }
    FREEZE.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
