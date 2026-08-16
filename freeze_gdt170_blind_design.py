#!/usr/bin/env python3
"""Freeze the GDT170 blind parser and diagnostic family before execution."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parent
OBS_FREEZE = R / "gdt170_observation_oracle_freeze.json"
METHOD = R / "GDT170_FULL_OBSERVATION_INSTRUMENT_METHOD.md"
OUT = R / "gdt170_blind_design.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def main() -> None:
    design = {
        "schema": "GDT170_BLIND_INSTRUMENT_DESIGN_V1",
        "status": "FROZEN_BEFORE_BLIND_SURFACE_PARSE",
        "observation_freeze_sha256": sha(OBS_FREEZE),
        "method_sha256": sha(METHOD),
        "blind_levels": ["SURFACE_ONLY", "VMANUS_ANNOTATION_ASSISTED"],
        "operation_discovery": {
            "surface_contrast": "EXACT_PREFIX_OR_SUFFIX_ADDITION",
            "operation_codepoint_lengths": [1, 2, 3],
            "minimum_distinct_hosts": 8,
            "minimum_synthetic_folios": 5,
            "maximum_selected_operations_per_side": 12,
            "maximum_total_stripped_layers": 3,
            "maximum_stripped_layers_per_side": 2,
            "residual_support": "VISIBLE_TOKEN_RECURRENCE_OR_TWO_ENVELOPE_TYPES",
            "training_scope": "ONE_ANONYMOUS_WORLD_AND_WITNESS_RENDERER",
        },
        "surface_parse_rank": [
            "DESC_VISIBLE_RESIDUAL_OCCURRENCES_PLUS_POINT25_ENVELOPE_TYPES",
            "ASC_TOTAL_STRIPPED_LAYERS", "DESC_RESIDUAL_LENGTH", "LEXICAL_TIEBREAK",
        ],
        "annotation_assisted_rank": {
            "base": "SURFACE_PARSE_RANK",
            "left_bonus": "POINT5_TIMES_LOG2_LAPLACE_PARAGRAPH_START_LIFT",
            "right_bonus": "POINT25_TIMES_LOG2_LAPLACE_LINE_END_LIFT_PLUS_POINT5_TIMES_LOG2_LAPLACE_PARAGRAPH_END_LIFT",
            "stability_penalty": "POINT25_TIMES_VARIANCE_OF_REGISTER_HAND_LOG_LIFTS",
            "allowed_annotations": ["register", "hand", "paragraph_start", "paragraph_end", "right_separator"],
        },
        "diagnostics": [
            "GDT113_INFERRED_CLOSURE_AND_RECURRENCE",
            "GDT160_OPERATION_COMPATIBILITY",
            "GDT162_SHORT_HOST_STRUCTURE",
            "GDT163_SAME_GROUP_SUBSTITUTION_DELTAS",
            "GDT164_EXTERNAL_CONTEXT_SUBSTITUTION_DELTAS",
            "GDT165_HELD_FOLIO_NEXT_HOST",
            "GDT166_HELD_FOLIO_UNORDERED_LINE_CONTEXT",
            "GDT167_REGISTER_HAND_GEOMETRY_ALIGNMENT",
        ],
        "context_smoothing": {"global_alpha": 16.0, "host_beta": 8.0},
        "operation_null_worlds": 1024,
        "alignment_host_panel": 100,
        "renderer_views_are_sensitivities_not_replications": True,
        "blind_output_freeze_before_oracle_unblinding": True,
        "forbidden_inputs": [
            "gdt170_sealed_oracle.json.gz", "gdt168_synthetic_ground_truth.json.gz",
            "gdt168_codebook_truth.tsv", "gdt168_blind_synthetic_corpora.json.gz",
        ],
        "forbidden_fields": [
            "system", "concept_index", "plaintext_form", "source_unit_full", "canonical_a_code",
            "canonical_host", "rendered_host", "true_record_id", "true_record_slot", "true_record_length",
            "true_wrapper", "true_local_frame", "true_right_family", "true_closure_value",
            "true_dy_closure", "true_b3", "wrapper_digit", "right_digit", "closure_digit",
        ],
        "no_voynich_tuning": True,
        "voynich_inputs": 0,
        "f84r_access": False,
        "claim_ceiling": "Blind synthetic instrument outputs only; no Voynich word, code value, language, meaning, plaintext, or translation.",
    }
    design["implementation"] = {Path(__file__).name: sha(Path(__file__))}
    design["design_content_sha256"] = csha(design)
    OUT.write_text(json.dumps(design, indent=2, sort_keys=True) + "\n")
    print(design["status"])


if __name__ == "__main__":
    main()
