#!/usr/bin/env python3
"""Bind final method-conformance corrections before GDT379 publication."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt379_f1_orthogonal_behavior"
ART = BASE / "artifacts"
RUNNER = BASE / "src/run_gdt379.py"

obj = {
    "schema": "GDT379_FINAL_IMPLEMENTATION_CORRECTION_V1",
    "chronology": "AFTER_SECOND_COMPLETE_UNPUBLISHED_RESULT_BEFORE_FINAL_METHOD_CONFORMANT_RUN",
    "superseded_runner_sha256": "3f4188549a83bdd9c7453f433ae21d3432af5035dfc14ad3b5c384c57f713f45",
    "superseded_result_sha256": "63f8030974af24c8f246f80930fab62a561ab4468cd787d08b05b82a624e4852",
    "superseded_family_results_sha256": "ce25edcb43eaf5d3cd7770c5e5ad7b967f6deba57744b2aafd525bb8a80eb892",
    "superseded_submetric_results_sha256": "2bf2538531d19f47403b4420e704115e4a49d40c79d1cc5b66d911330c419a0b",
    "superseded_null_sha256": "556cb3877a02b3da3e3b3d333cdbb1cf9043a3827b53af0e6102a91ea45fdb75",
    "corrected_runner_sha256": hashlib.sha256(RUNNER.read_bytes()).hexdigest(),
    "corrections": [
        "USE_THE_SAME_ACTUAL_OUTER_FOLD_COUNT_IN_OBSERVED_AND_NULL_F2_NORMALIZATION",
        "RECHECK_F2_THREE_FOLIO_TWO_REGISTER_SUPPORT_AFTER_REMOVING_EACH_HELD_FOLIO",
        "EXCLUDE_F1_ITSELF_FROM_THE_SECOND_FORM_F2_SEARCH",
        "COMPUTE_FOLIO_REGISTER_STABILITY_FROM_EXACT_FROZEN_NUISANCE_STRATUM_RESIDUALS_ON_MOBILE_EVENTS"
    ],
    "candidate_or_threshold_changed": False,
    "full_4096_world_rerun_required": True,
    "previous_results_published": False,
    "semantic_state": "UNASSIGNED"
}
obj["content_hash"] = hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
(ART / "gdt379_final_implementation_correction.json").write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")
