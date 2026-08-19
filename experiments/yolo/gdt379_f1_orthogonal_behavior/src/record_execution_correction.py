#!/usr/bin/env python3
"""Record the sole post-score mechanical correction before the GDT379 rerun."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt379_f1_orthogonal_behavior"
ART = BASE / "artifacts"
RUNNER = BASE / "src/run_gdt379.py"

obj = {
    "schema": "GDT379_EXECUTION_CORRECTION_V1",
    "chronology": "AFTER_ALL_4096_NULL_WORLDS_COMPUTED_BEFORE_ANY_RESULT_OR_SCORE_OUTPUT_WAS_WRITTEN",
    "failure": "RESULT_ROW_ASSEMBLY_KEYERROR_INTEGER_ZERO",
    "superseded_runner_sha256": "2c8822ae2fb49771bd56b484d8736fcccb028bdc1bbb69b633b0597dc6471ae0",
    "corrected_runner_sha256": hashlib.sha256(RUNNER.read_bytes()).hexdigest(),
    "exact_change": "observed[j]_TO_observed[name]",
    "scientific_definitions_changed": False,
    "candidate_changed": False,
    "statistics_changed": False,
    "thresholds_changed": False,
    "null_worlds_or_seed_changed": False,
    "pre_correction_scientific_outputs_written": [],
    "outcomes_exposed_before_correction": True,
    "rerun_authorized": "BYTE_IDENTICAL_FROZEN_COMPUTATION_WITH_RESULT_LOOKUP_FIX_ONLY",
}
obj["content_hash"] = hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
(ART / "gdt379_execution_correction.json").write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")
