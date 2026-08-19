#!/usr/bin/env python3
"""Freeze GDT380 comparator behavior design before any comparator scoring."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt380_identity_free_functional_transfer"
ART = BASE / "artifacts"
G378 = ROOT / "experiments/yolo/gdt378_cross_corpus_construction_transfer/artifacts"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def content(obj: dict) -> str:
    clone = dict(obj)
    clone.pop("content_hash", None)
    return hashlib.sha256(json.dumps(clone, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def write_json(path: Path, obj: dict) -> None:
    obj["content_hash"] = content(obj)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    ART.mkdir(parents=True, exist_ok=True)
    inputs = {
        str(path.relative_to(ROOT)): sha(path)
        for path in [
            G378 / "gdt378_comparator_observation_layer.tsv.gz",
            G378 / "gdt378_hidden_oracle.tsv.gz",
            G378 / "gdt378_oracle_contract.json",
            G378 / "gdt378_secondary_transfer_signature_freeze.json",
            G378 / "gdt378_comparator_design_freeze.json",
            G378 / "gdt378_comparator_result.json",
            ROOT / "experiments/yolo/gdt379_f1_orthogonal_behavior/artifacts/gdt379_result.json",
        ]
    }
    design = {
        "schema": "GDT380_COMPARATOR_BEHAVIOR_FREEZE_V1",
        "status": "FROZEN_BEFORE_COMPARATOR_BEHAVIOR_SCORING",
        "chronology": "AFTER_GDT379_CLOSE_BEFORE_GDT380_COMPARATOR_OUTCOMES_OR_VOYNICH_TARGET_ACCESS",
        "f1": {
            "semantic_route_closed": True,
            "retained_only_as": "EXPOSED_FORMAL_RECURRENCE_ANOMALY_F1_X_F1",
            "used_in_gdt380": False,
            "stability_gate_changed": False,
        },
        "anonymous_families": [
            {"id": "CMP_FUNCTION_01", "comparator_endpoint": "UNTIL_STATE_GATE", "behavior_block": "GATE_TRANSITION"},
            {"id": "CMP_FUNCTION_02", "comparator_endpoint": "ALTERNATIVE_OR", "behavior_block": "BRANCH_RECONVERGENCE"},
            {"id": "CMP_FUNCTION_03", "comparator_endpoint": "POLARITY_EXCLUSION", "behavior_block": "MARKED_INVERSE_DELTA"},
            {"id": "CMP_FUNCTION_04", "comparator_endpoint": "FUNCTION_WORD", "behavior_block": "CLOSED_CLASS_BOTTLENECK"},
        ],
        "domains": ["COREMA", "PCEEC2", "CURIOUS_CURES", "HARLEIAN_COOKERY", "QUINTE_ESSENCE"],
        "identity_policy": {
            "exact_opaque_id_as_feature": False,
            "surface_or_glyph_feature": False,
            "local_equality_predicates": True,
            "aggregate_recurrence_statistics": True,
            "hidden_labels_available_only_at_evaluation": True,
        },
        "horizons": [1, 2, 4, 8],
        "nuisance": [
            "domain_collection_intercept", "record_length_bin", "relative_position_spline",
            "boundary_before_after", "surface_length", "direct_token_count",
            "within_record_recurrence_count",
        ],
        "outer_fold": "LEAVE_ONE_COMPARATOR_DOMAIN_OUT",
        "model": "L2_LOGISTIC_FIXED_LAMBDA_4_DOMAIN_BALANCED",
        "null": {
            "worlds": 1024,
            "seed": 380001,
            "shuffle": "LABEL_WITHIN_DOMAIN_COLLECTION_RECORD_LENGTH_POSITION_BOUNDARY_RECURRENCE",
            "joint_maxT": "FOUR_FAMILIES_ALL_REPORTED_COMPONENTS_HORIZONS",
            "tail": "ONE_SIDED_TRANSFER",
        },
        "comparator_gate": {
            "transfer_auc_floor_min": 0.60,
            "positive_gain_domains_min": 3,
            "pceec2_auc_min": 0.60,
            "pceec2_gain_positive": True,
            "procedural_domain_auc_min": 0.60,
            "procedural_domain_gain_positive": True,
            "max_family_p_max": 0.05,
            "pivot_recurrence_deletion_direction_positive": True,
        },
        "target_if_authorized": {
            "source": "GDT327_F84_FREE_EXACT_JOINT_TUPLES_ONLY",
            "resolutions": ["ATOMIC_CONTEXT", "SOURCE_GROUP_CONTEXT", "FIELD_LOCAL_TRANSITION", "BEHAVIOR_DEFINED_CONSTRUCTION_SLOT"],
            "candidate_definition": "CROSS_FIT_BEHAVIOR_SCORE_OR_TRAINING_FOLIO_CENTROID_NEVER_IDENTITY",
            "outer_fold": "LEAVE_ONE_PHYSICAL_FOLIO_OUT",
            "direction_folio_fraction_min": 0.60,
            "powered_registers_min": 3,
            "deterministic_conditioned_candidate": "UNIDENTIFIABLE_EXCLUDED_FROM_MAXT_SEARCH_STILL_CHARGED",
        },
        "forbidden_voynich_labels": ["AND", "OR", "NOT", "UNTIL", "FUNCTION_WORD", "POS", "MORPHEME", "SOUND", "LANGUAGE", "PLAINTEXT", "MEANING", "TRANSLATION"],
        "inputs": inputs,
        "voynich_scored": False,
        "voynich_target_rows_read": 0,
        "f84": {"opened": False, "parsed": False, "retained": False, "scored": False},
        "claim_ceiling": "COMPARATOR_IDENTITY_FREE_BEHAVIOR_FREEZE_ONLY",
    }
    write_json(ART / "gdt380_comparator_behavior_freeze.json", design)
    result = {
        "schema": "GDT380_COMPARATOR_FREEZE_RESULT_V1",
        "status": "FROZEN_NOT_RUN",
        "inputs": inputs,
        "documents": {
            str((BASE / name).relative_to(ROOT)): sha(BASE / name)
            for name in ["METHOD.md", "README.md", "experiment.json"]
        },
        "implementation": {
            str((BASE / "src/freeze_comparator.py").relative_to(ROOT)): sha(BASE / "src/freeze_comparator.py")
        },
        "outputs": {
            str((ART / "gdt380_comparator_behavior_freeze.json").relative_to(ROOT)): sha(ART / "gdt380_comparator_behavior_freeze.json")
        },
        "voynich_scored": False,
        "f84": {"opened": False, "parsed": False, "retained": False, "scored": False},
        "claim_ceiling": "SCORE_FREE_COMPARATOR_BEHAVIOR_DESIGN",
    }
    write_json(ART / "gdt380_comparator_freeze_result.json", result)


if __name__ == "__main__":
    main()
