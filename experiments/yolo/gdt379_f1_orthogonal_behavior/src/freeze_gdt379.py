#!/usr/bin/env python3
"""Freeze GDT379 without enumerating F1 contexts or scoring outcomes."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt379_f1_orthogonal_behavior"
ART = BASE / "artifacts"
SOURCE = ROOT / "gdt327_joint_tuple_interlinear.tsv"
GDT378 = ROOT / "experiments/yolo/gdt378_cross_corpus_construction_transfer"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def content(obj: dict) -> str:
    clone = dict(obj)
    clone.pop("content_hash", None)
    return hashlib.sha256(json.dumps(clone, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def write_json(path: Path, obj: dict) -> None:
    obj["content_hash"] = content(obj)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_tsv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    raw = SOURCE.read_text(encoding="utf-8")
    header = raw.splitlines()[0].split("\t")
    required = {"page", "physical_folio", "locus", "record_ordinal", "field_ordinal", "joint_tuple_id", "observed_wrapper"}
    if not required.issubset(header):
        raise ValueError("source schema mismatch")
    for line in raw.splitlines()[1:]:
        fields = line.split("\t")
        row = dict(zip(header, fields))
        if any(row[key].startswith("f84") for key in ("page", "physical_folio", "locus")):
            raise ValueError("f84 row in sole source")

    source_inputs = {
        "gdt327_joint_tuple_interlinear.tsv": sha(SOURCE),
        "experiments/yolo/gdt378_cross_corpus_construction_transfer/artifacts/gdt378_identity_only_diagnostic_result.json": sha(GDT378 / "artifacts/gdt378_identity_only_diagnostic_result.json"),
        "experiments/yolo/gdt378_cross_corpus_construction_transfer/artifacts/gdt378_identity_only_diagnostic.tsv": sha(GDT378 / "artifacts/gdt378_identity_only_diagnostic.tsv"),
        "experiments/yolo/gdt378_cross_corpus_construction_transfer/artifacts/gdt378_secondary_transfer_signature_freeze.json": sha(GDT378 / "artifacts/gdt378_secondary_transfer_signature_freeze.json"),
        "experiments/yolo/gdt378_cross_corpus_construction_transfer/artifacts/gdt378_voynich_event_scores.tsv.gz": sha(GDT378 / "artifacts/gdt378_voynich_event_scores.tsv.gz"),
        "experiments/yolo/gdt378_cross_corpus_construction_transfer/artifacts/gdt378_voynich_target_result.json": sha(GDT378 / "artifacts/gdt378_voynich_target_result.json"),
    }

    candidate = {
        "schema": "GDT379_F1_CANDIDATE_FREEZE_V1",
        "experiment_id": "GDT379",
        "chronology": "FROZEN_AFTER_GDT378_F1_EXPOSURE_BEFORE_ANY_GDT379_CONTEXT_ENUMERATION_OR_OUTCOME_SCORE",
        "status": "EXPLORATORY_NONPROMOTED_F1_FROZEN",
        "source_signature": "CMP_FUNCTION_04",
        "source_comparator_label_inherited": False,
        "candidate": {
            "anonymous_id": "F1",
            "atomic_joint_tuple_id": "2f1c5e56e8f0ff459065",
            "d_rendered_source_group_id": "c502a1edfafbe3e54262",
            "d_rendered_wrapper": "d",
            "linked_resolutions_are_independent": False,
            "semantic_state": "UNASSIGNED",
        },
        "gdt378_primary_decision_unchanged": True,
        "gdt378_primary_null_retuned": False,
        "gdt378_identity_lead_promoted": False,
        "inputs": source_inputs,
        "f84": {"opened": False, "parsed": False, "retained": False, "scored": False},
        "claim_ceiling": "ANONYMOUS_EXPLORATORY_FORMAL_CANDIDATE_ONLY",
    }
    write_json(ART / "gdt379_f1_candidate_freeze.json", candidate)

    rows = [
        {"diagnostic_id": "F1_D01", "route": "F1", "name": "COORDINATION_SYMMETRY", "prospective_outcome": "left_right_operand_structural_similarity", "search_dimensions": "atomic_and_d_rendered;two_similarity_components", "minimum": "12_events;3_folios;2_registers", "semantic_state": "UNASSIGNED"},
        {"diagnostic_id": "F1_D02", "route": "F1", "name": "VARIABLE_ARITY_CHAIN", "prospective_outcome": "three_plus_homogeneous_operands", "search_dimensions": "all_chain_arities;atomic_and_d_rendered", "minimum": "3_chains;3_folios;2_registers", "semantic_state": "UNASSIGNED"},
        {"diagnostic_id": "F1_D03", "route": "F1", "name": "MUTUAL_EXCLUSION", "prospective_outcome": "held_record_slot_exclusivity", "search_dimensions": "all_operand_pairs", "minimum": "12_pairs;3_folios;2_registers", "semantic_state": "UNASSIGNED"},
        {"diagnostic_id": "F1_D04", "route": "F1", "name": "DOWNSTREAM_DELTA", "prospective_outcome": "next_two_atomic_tuple_and_closure_delta", "search_dimensions": "all_source_matched_contexts", "minimum": "12_matched_pairs;3_folios;2_registers", "semantic_state": "UNASSIGNED"},
        {"diagnostic_id": "F1_D05", "route": "F1", "name": "SCOPE_HORIZON", "prospective_outcome": "downstream_return_diversity_and_boundary_curve", "search_dimensions": "h1,h2,h3,h4,h6,h8;DY,B3,FIELD,LINE", "minimum": "12_events;3_folios;2_registers", "semantic_state": "UNASSIGNED"},
        {"diagnostic_id": "F1_D06", "route": "F1", "name": "PAIRED_OPERATOR", "prospective_outcome": "training_discovered_F2_held_enrichment", "search_dimensions": "all_opaque_forms;spans1_to_8;both_directions", "minimum": "12_training_pairs;3_folios;2_registers", "semantic_state": "UNASSIGNED"},
        {"diagnostic_id": "F1_D07", "route": "F1", "name": "RENDERER_EQUIVALENCE", "prospective_outcome": "d_vs_non_d_external_behavior_vector_cosine", "search_dimensions": "seven_behavior_axes", "minimum": "12_events_each;3_folios;2_registers", "semantic_state": "UNASSIGNED"},
        {"diagnostic_id": "F1_D08", "route": "F1", "name": "POSITION_INDEPENDENCE", "prospective_outcome": "nuisance_adjusted_folio_and_register_direction", "search_dimensions": "all_F1_endpoints;all_deletions", "minimum": "60pct_folios;3_registers", "semantic_state": "UNASSIGNED"},
        {"diagnostic_id": "R1_CMP01", "route": "CMP_FUNCTION_01", "name": "BOUNDARY_RENDERER_PERSISTENCE", "prospective_outcome": "next_boundary_atomic_renderer_persistence", "search_dimensions": "field_and_line_boundary", "minimum": "12_events;3_folios;2_registers", "semantic_state": "UNASSIGNED"},
        {"diagnostic_id": "R2_CMP02", "route": "CMP_FUNCTION_02", "name": "BRANCH_RECONVERGENCE", "prospective_outcome": "adjacent_span_divergence_then_reconvergence_h1_to_h4", "search_dimensions": "h1,h2,h3,h4", "minimum": "12_events;3_folios;2_registers", "semantic_state": "UNASSIGNED"},
        {"diagnostic_id": "R3_CMP03", "route": "CMP_FUNCTION_03", "name": "RECORD_DELTA_REVERSAL", "prospective_outcome": "matched_record_downstream_atomic_state_delta_reversal", "search_dimensions": "all_source_matched_record_pairs", "minimum": "12_pairs;3_folios;2_registers", "semantic_state": "UNASSIGNED"},
    ]
    write_tsv(ART / "gdt379_diagnostic_manifest.tsv", rows)

    null = {
        "schema": "GDT379_NULL_AND_FUTURE_CORRECTION_FREEZE_V1",
        "worlds": 4096,
        "seed": 379001,
        "tails": "TWO_SIDED",
        "charged_diagnostic_families": 11,
        "joint_maxT": True,
        "f1_identity_null": "PERMUTE_F1_LABEL_WITHIN_MOBILE_NUISANCE_STRATA",
        "score_route_null": "CROSS_FIT_NUISANCE_THEN_FREEDMAN_LANE_WITHIN_FOLIO_REGISTER_RECORD_LENGTH",
        "nested_F2_search_replayed_per_world": True,
        "minimum_family_mobile_events": 256,
        "classification": {
            "INTERESTING_EXPLORATORY": "joint_p_le_0.05_and_direction_in_60pct_eligible_folios_and_3_powered_registers_and_atomic_plus_adjusted_direction",
            "WEAK": "local_p_le_0.05_or_positive_effect_without_joint_gate",
            "UNSTABLE": "direction_reversal_or_deletion_failure",
            "NO_SIGNAL": "otherwise",
            "INSUFFICIENT_CAPACITY": "endpoint_below_frozen_minimum",
        },
        "future_slot_null_correction": {
            "gdt378_retroactive_change_authorized": False,
            "rule": "CANDIDATE_DEFINING_VARIABLES_MUST_NOT_BE_EXACTLY_CONDITIONED",
            "allowed": "cross_fitted_nuisance_residualization_or_conditional_randomization_with_mobile_candidate_membership",
            "deterministic_membership_status": "UNIDENTIFIABLE_EXCLUDED_FROM_MAXT_BUT_SEARCH_REMAINS_CHARGED",
        },
        "semantic_state": "UNASSIGNED",
        "forbidden_interpretations": ["AND", "OR", "NOT", "UNTIL", "FUNCTION_WORD", "POS", "MEANING", "LANGUAGE", "PLAINTEXT", "TRANSLATION"],
    }
    write_json(ART / "gdt379_null_and_future_correction_freeze.json", null)

    dedup = [
        {"gdt379_family": "F1_D01_D02", "nearest_closed_route": "GDT374_EXACT_REWRITE", "difference": "fixed_exposed_pivot;tests_span_symmetry_and_chain_consequence_not_rewrite_prediction", "status": "NEW_CONSEQUENCE"},
        {"gdt379_family": "F1_D03_D04", "nearest_closed_route": "GDT345_TARGET_STATE", "difference": "record_matched_exclusivity_and_downstream_consequence;no_target_coordinate_as_input", "status": "NEW_CONSEQUENCE"},
        {"gdt379_family": "F1_D05", "nearest_closed_route": "CHO_CHE_SCOPE", "difference": "fixed_opaque_atomic_candidate;multi_boundary_decay;no_substring_or_glyph_family", "status": "NEW_CONSEQUENCE"},
        {"gdt379_family": "F1_D06", "nearest_closed_route": "GDT373_CORRELATIVE_ROADMAP", "difference": "nested_training_only_F2_discovery_with_held_folio_score", "status": "NEW_PROSPECTIVE_TEST"},
        {"gdt379_family": "F1_D07_D08", "nearest_closed_route": "GDT346_OPERATOR_MANIFOLD", "difference": "renderer_invariance_of_external_behavior;no_target_operator_prediction_or_coordinate_graph", "status": "NEW_CONSEQUENCE"},
        {"gdt379_family": "R1_R2_R3", "nearest_closed_route": "GDT378_IDENTITY_ATLAS", "difference": "continuous_signature_scores_predict_orthogonal_renderer_or_record_behavior;no_identity nomination", "status": "NEW_CONSEQUENCE"},
    ]
    write_tsv(ART / "gdt379_route_dedup.tsv", dedup)

    outputs = [
        ART / "gdt379_f1_candidate_freeze.json",
        ART / "gdt379_diagnostic_manifest.tsv",
        ART / "gdt379_null_and_future_correction_freeze.json",
        ART / "gdt379_route_dedup.tsv",
    ]
    result = {
        "schema": "GDT379_SCORE_FREE_FREEZE_RESULT_V1",
        "status": "FROZEN_NOT_RUN",
        "diagnostic_families": 11,
        "f1_diagnostics": 8,
        "anonymous_signature_routes": 3,
        "outcomes_inspected": 0,
        "f1_contexts_enumerated": 0,
        "inputs": source_inputs,
        "documents": {str((BASE / name).relative_to(ROOT)): sha(BASE / name) for name in ["METHOD.md", "README.md", "experiment.json"]},
        "implementation": {str((BASE / "src/freeze_gdt379.py").relative_to(ROOT)): sha(BASE / "src/freeze_gdt379.py")},
        "outputs": {str(path.relative_to(ROOT)): sha(path) for path in outputs},
        "f84": {"opened": False, "parsed": False, "retained": False, "scored": False},
        "semantic_state": "UNASSIGNED",
        "claim_ceiling": "PROSPECTIVE_BEHAVIORAL_DIAGNOSTIC_FREEZE_ONLY",
    }
    write_json(ART / "gdt379_freeze_result.json", result)


if __name__ == "__main__":
    main()
