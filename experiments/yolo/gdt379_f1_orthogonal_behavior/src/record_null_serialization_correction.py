#!/usr/bin/env python3
"""Record addition of the full retained GDT379 null matrix before final run."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt379_f1_orthogonal_behavior"
ART = BASE / "artifacts"
RUNNER = BASE / "src/run_gdt379.py"

obj = {
    "schema": "GDT379_NULL_SERIALIZATION_CORRECTION_V1",
    "chronology": "AFTER_FINAL_METHOD_CONFORMANCE_RUN_BEFORE_PUBLICATION",
    "superseded_runner_sha256": "67f851a6a020282078f23f779d2311cc6b203ba06a9ea9d033d8cbb6d9d59af4",
    "superseded_result_sha256": "c7c56571e4d92300e45dc86ccd77eea53bea8ef731b9f8a25c5f11164ee41ee3",
    "superseded_global_null_sha256": "3b5121346afd5a1365961ab7b51573cb2070198ba2d231cc879dd280509261de",
    "corrected_runner_sha256": hashlib.sha256(RUNNER.read_bytes()).hexdigest(),
    "change": "ADD_4096_BY_36_RETAINED_NULL_SUBMETRIC_MATRIX_AND_BIND_DOCUMENT_CORRECTION_IMPLEMENTATION_HASHES",
    "scientific_values_or_rules_changed": False,
    "full_deterministic_rerun_required": True,
    "previous_results_published": False,
}
obj["content_hash"] = hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
(ART / "gdt379_null_serialization_correction.json").write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")
