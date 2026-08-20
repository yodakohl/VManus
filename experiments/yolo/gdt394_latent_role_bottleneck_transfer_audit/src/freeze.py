#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt394_latent_role_bottleneck_transfer_audit"
ART = BASE / "artifacts"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    inputs = [
        ROOT / "experiments/yolo/gdt382_voynichification_methodology_audit/artifacts/gdt382_voynichified_observation_layer.tsv.gz",
        ROOT / "experiments/yolo/gdt385_corema_parent_link_consequence/artifacts/gdt385_predictions.tsv.gz",
        ROOT / "experiments/yolo/gdt387_cross_domain_parent_link_calibration/artifacts/gdt387_hidden_governor_oracle.tsv.gz",
        ROOT / "experiments/yolo/gdt387_cross_domain_parent_link_calibration/artifacts/gdt387_predictions.tsv.gz",
        ROOT / "experiments/yolo/gdt384_role_specific_relational_consequence/artifacts/gdt384_result.json",
        ROOT / "experiments/yolo/gdt385_corema_parent_link_consequence/artifacts/gdt385_result.json",
        ROOT / "experiments/yolo/gdt387_cross_domain_parent_link_calibration/artifacts/gdt387_result.json",
    ]
    documents = [BASE / "METHOD.md", BASE / "SOURCE_AUDIT.md", BASE / "README.md"]
    implementations = [
        BASE / "src/freeze.py",
        BASE / "src/validate_freeze.py",
        BASE / "src/run.py",
        BASE / "src/validate.py",
    ]
    freeze = {
        "schema": "GDT394_PRE_SCORE_FREEZE_V1",
        "status": "FROZEN_BEFORE_SCORING",
        "domains": ["COREMA", "PCEEC2"],
        "outer_folds": {"COREMA": "COLLECTION", "PCEEC2": "SOURCE_FILE"},
        "bottleneck_dimension": 1,
        "models": [
            "ROLE_BOTTLENECK",
            "LINEAR_ROLE_1D",
            "SUPERVISED_RELATION_1D",
            "PCA_SOURCE_1D",
            "RANDOM_SOURCE_1D",
            "GRAMMAR_SUMMARY_1D",
            "EXACT_JOINT_ROLE_1D",
            "SHUFFLED_ROLE_1D",
        ],
        "source_hash_bins": 64,
        "ridge_lambda": 10.0,
        "downstream_quantile_bins": 8,
        "downstream_dirichlet_strength": 8.0,
        "null_worlds": 512,
        "null_seed": "GDT394_COUPLING_NULL_V1",
        "random_projection_seed": "GDT394_FIXED_RANDOM_PROJECTION_V1",
        "promotion": {
            "positive_gain": True,
            "beats_every_equal_budget_control": True,
            "positive_fold_minimum": {"COREMA": 4, "PCEEC2": 43},
            "beats_every_control_null_excess": True,
            "max8_p_max": 0.05,
            "mrr_margin_over_best_control": 0.001,
            "top1_count_margin": "max(3,ceil(0.001*N))",
            "required_domains": 2,
        },
        "voynich_inputs": 0,
        "f84": {"opened": False, "parsed": False, "retained": False, "scored": False},
        "input_hashes": {str(path.relative_to(ROOT)): sha(path) for path in inputs},
        "document_hashes": {str(path.relative_to(ROOT)): sha(path) for path in documents},
        "implementation_hashes": {
            str(path.relative_to(ROOT)): sha(path) for path in implementations
        },
    }
    encoded = json.dumps(freeze, sort_keys=True, separators=(",", ":")).encode()
    freeze["content_sha256"] = hashlib.sha256(encoded).hexdigest()
    (ART / "gdt394_pre_score_freeze.json").write_text(
        json.dumps(freeze, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
