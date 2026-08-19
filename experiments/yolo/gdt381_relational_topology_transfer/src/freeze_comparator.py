#!/usr/bin/env python3
"""Freeze GDT381 topology design before hidden-oracle evaluation."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt381_relational_topology_transfer"
ART = BASE / "artifacts"
G378 = ROOT / "experiments/yolo/gdt378_cross_corpus_construction_transfer/artifacts"
G380 = ROOT / "experiments/yolo/gdt380_identity_free_functional_transfer/artifacts"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def content(obj: dict) -> str:
    clone = dict(obj)
    clone.pop("content_hash", None)
    return hashlib.sha256(json.dumps(clone, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def write(path: Path, obj: dict) -> None:
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
            G378 / "gdt378_comparator_design_freeze.json",
            G380 / "gdt380_result.json",
            G380 / "gdt380_validation.json",
        ]
    }
    design = {
        "schema": "GDT381_COMPARATOR_TOPOLOGY_FREEZE_V1",
        "status": "FROZEN_BEFORE_HIDDEN_ORACLE_EVALUATION",
        "chronology": "AFTER_GDT380_CLOSE_BEFORE_GDT381_ORACLE_OUTCOME_OR_ANY_VOYNICH_TARGET_ACCESS",
        "route_deduplication": {
            "gdt378_to_380_local_or_identity_search_reopened": False,
            "gdt345_to_347_coordinate_operator_manifold_reopened": False,
            "new_endpoint": "SEMANTIC_FUNCTION_RELATION_TOPOLOGY_OVER_CORPUS_LOCAL_LATENT_CLASSES",
        },
        "latent_classes": {
            "scope": "LEARNED_INDEPENDENTLY_WITHIN_EACH_COMPARATOR_DOMAIN",
            "type": "OPAQUE_FORM_STRUCTURAL_CONTEXT_EQUIVALENCE",
            "features": ["position_histogram", "record_length_histogram", "boundary_rates", "recurrence_return", "neighbor_diversity_degree", "record_collection_coverage", "local_equality_geometry"],
            "standardization": "WITHIN_DOMAIN",
            "algorithm": "DETERMINISTIC_KMEANS_20_RESTARTS",
            "seed_base": 381001,
            "k_grid": [4, 6, 8, 12, 16, 24],
            "k_rule": "SMALLEST_K_REACHING_80_PERCENT_OF_K24_INERTIA_REDUCTION_FROM_K1",
            "cross_domain_class_alignment": False,
            "oracle_labels_used": False,
        },
        "anonymous_topologies": [
            {"id": "CMP_TOPOLOGY_01", "endpoint": "UNTIL_STATE_GATE", "family": "PERSISTENT_STATE_GATE_EXIT"},
            {"id": "CMP_TOPOLOGY_02", "endpoint": "ALTERNATIVE_OR", "family": "BRANCH_ALTERNATIVES_RECONVERGENCE"},
            {"id": "CMP_TOPOLOGY_03", "endpoint": "POLARITY_EXCLUSION", "family": "MARKED_COUNTERPART_INVERSE_DELTA"},
            {"id": "CMP_TOPOLOGY_04", "endpoint": "COORDINATOR", "family": "HOMOGENEOUS_LINK_VARIABLE_ARITY"},
            {"id": "CMP_TOPOLOGY_05", "endpoint": "NEXT_RESUME", "family": "LOCAL_RESET_RESUME_NEXT"},
        ],
        "horizons": [1, 2, 4, 8],
        "models": ["NUISANCE", "TRIVIAL_MOTIF_BASELINE", "FULL_RELATIONAL_TOPOLOGY", "FULL_WITHOUT_ONE_STEP_EQUALITY"],
        "outer_fold": "LEAVE_ONE_COMPARATOR_DOMAIN_OUT",
        "model": "L2_LOGISTIC_FIXED_LAMBDA_4_DOMAIN_BALANCED",
        "null": {
            "worlds": 2048,
            "seed": 381101,
            "shuffle": "ENDPOINT_WITHIN_DOMAIN_COLLECTION_RECORD_LENGTH_POSITION_BOUNDARY_RECURRENCE_CLASS_SIZE_QUARTILE",
            "preserves": ["record_topology", "latent_class_assignment", "latent_class_size_distribution", "record_length", "position", "boundary", "recurrence_opportunity"],
            "maxT": "FIVE_TOPOLOGIES_ALL_HORIZONS_ALL_REPORTED_COMPONENTS",
            "deterministic_membership": "UNIDENTIFIABLE_EXCLUDED_FROM_MAXT_SEARCH_REMAINS_CHARGED",
        },
        "comparator_gate": {
            "transfer_auc_floor_min": 0.62,
            "positive_gain_vs_nuisance_domains_min": 3,
            "positive_gain_vs_trivial_domains_min": 3,
            "pceec2_auc_min": 0.60,
            "pceec2_both_gains_positive": True,
            "procedural_auc_min": 0.62,
            "procedural_both_gains_positive": True,
            "max_family_p_max": 0.05,
            "one_step_equality_deletion_positive_domains_min": 3,
        },
        "target_if_authorized": {
            "source": "GDT327_F84_FREE_ATOMIC_JOINT_TUPLE_GRAMMAR",
            "latent_classes": "INDEPENDENT_WITHIN_POWERED_REGISTER_SECTION_STRATA_NO_CROSS_STRATUM_ALIGNMENT",
            "forbidden_inputs": ["EXACT_TUPLE_ID", "EXACT_GROUP_ID", "PAGE_HOST", "SUBSTRING", "GLYPH", "SURFACE"],
            "outer_fold": "LEAVE_ONE_PHYSICAL_FOLIO_OUT",
            "direction_folio_fraction_min": 0.60,
            "powered_registers_min": 3,
            "formal_realizations_inspected_only_after_pass": True,
        },
        "inputs": inputs,
        "hidden_oracle_evaluated": False,
        "voynich_rows_read": 0,
        "voynich_scored": False,
        "semantic_state": "UNASSIGNED",
        "forbidden_interpretations": ["AND", "OR", "NOT", "UNTIL", "POS", "MEANING", "LANGUAGE", "PLAINTEXT", "TRANSLATION"],
        "f84": {"opened": False, "parsed": False, "retained": False, "scored": False},
        "claim_ceiling": "SCORE_FREE_CORPUS_LOCAL_CLASS_AND_RELATION_TOPOLOGY_DESIGN",
    }
    write(ART / "gdt381_comparator_topology_freeze.json", design)
    result = {
        "schema": "GDT381_COMPARATOR_FREEZE_RESULT_V1", "status": "FROZEN_NOT_RUN",
        "inputs": inputs,
        "documents": {str((BASE / name).relative_to(ROOT)): sha(BASE / name) for name in ["METHOD.md", "README.md", "experiment.json"]},
        "implementation": {str((BASE / "src/freeze_comparator.py").relative_to(ROOT)): sha(BASE / "src/freeze_comparator.py")},
        "outputs": {str((ART / "gdt381_comparator_topology_freeze.json").relative_to(ROOT)): sha(ART / "gdt381_comparator_topology_freeze.json")},
        "hidden_oracle_evaluated": False, "voynich_rows_read": 0,
        "f84": {"opened": False, "parsed": False, "retained": False, "scored": False},
        "claim_ceiling": "PREORACLE_TOPOLOGY_FREEZE_ONLY",
    }
    write(ART / "gdt381_comparator_freeze_result.json", result)


if __name__ == "__main__":
    main()
