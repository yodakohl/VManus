#!/usr/bin/env python3
"""Bind the post-result enforcement correction for GDT379's frozen stability gate."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt379_f1_orthogonal_behavior"
ART = BASE / "artifacts"
RUNNER = BASE / "src/run_gdt379.py"

obj = {
    "schema": "GDT379_GATE_ENFORCEMENT_CORRECTION_V1",
    "chronology": "AFTER_FIRST_COMPLETE_UNPUBLISHED_RESULT_ASSEMBLY_BEFORE_FINAL_RESULT",
    "defect": "FAMILY_CLASSIFIER_CHECKED_JOINT_MAXT_BUT_DID_NOT_ENFORCE_THE_FROZEN_60_PERCENT_FOLIO_AND_THREE_REGISTER_STABILITY_GATE",
    "superseded_runner_sha256": "c42013db5f2ea60e60631be2996ffcbf3b7f035e2425fea0d9a3d73aec969763",
    "superseded_result_sha256": "08aeb63f43d048b581df3cfb644513161a19f305ac118a5cbda24388345b237c",
    "superseded_family_results_sha256": "3b5407e5af3eea369bc4eba185ec0d14b1ae8fddb591c7d63b8d1926036de206",
    "superseded_submetric_results_sha256": "576e6a7b4786bd2f3a2c5fb74a9b2fb25d6a1233c5d6d4a0c0c68e900f7917fa",
    "superseded_null_sha256": "556cb3877a02b3da3e3b3d333cdbb1cf9043a3827b53af0e6102a91ea45fdb75",
    "corrected_runner_sha256": hashlib.sha256(RUNNER.read_bytes()).hexdigest(),
    "frozen_threshold_changed": False,
    "statistics_or_null_changed": False,
    "required_correction": "REPORT_PER_SUBMETRIC_FOLIO_REGISTER_STABILITY_AND_CLASSIFY_JOINT_SIGNIFICANCE_WITH_FAILED_STABILITY_AS_UNSTABLE",
    "exposed_lead": {
        "submetric": "F1_D05_RETURN_H2",
        "eligible_folios": 69,
        "same_direction_folios": 27,
        "same_direction_fraction": 0.391304347826,
        "eligible_registers": 5,
        "same_direction_registers": 5,
        "frozen_folio_gate": 0.60,
        "correct_classification": "UNSTABLE"
    }
}
obj["content_hash"] = hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
(ART / "gdt379_gate_enforcement_correction.json").write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")
