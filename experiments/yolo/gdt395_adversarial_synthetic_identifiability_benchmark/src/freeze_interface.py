#!/usr/bin/env python3
"""Freeze GDT395 schemas, world assignments, seeds, and scoring thresholds."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark"
OUT = EXP / "artifacts/gdt395_interface_freeze.json"

ASSIGNMENTS = [
    ("W01", "TECHNICAL_SCRIBAL_SHORTHAND", "technical natural-language records", True, False, "NONE", "CARRIER_TECHNICAL"),
    ("W02", "ORGANIC_CODEBOOK", "apothecary inventory and preparation", True, False, "PAIR_CODEBOOK", "CARRIER_CODEBOOK_MATCHED"),
    ("W03", "ENGINEERED_CATALOGUE_CODE", "catalogue and stock indexing", False, True, "PAIR_CODEBOOK", "CARRIER_CODEBOOK_MATCHED"),
    ("W04", "PROCEDURAL_RECIPE_NOTATION", "multi-step material transformation", True, False, "NONE", "CARRIER_PROCEDURAL"),
    ("W05", "MNEMONIC_RITUAL_LEGACY", "conservative calendrical ritual procedure", True, False, "NONE", "CARRIER_MNEMONIC"),
    ("W06", "ORGANIC_CATALOGUE_INDEX", "taxonomic collection and cross-reference", True, False, "NONE", "CARRIER_INDEX"),
    ("W07", "HYBRID_WORD_CODE_QUANTITY", "measurement and workshop accounting", True, False, "NONE", "CARRIER_HYBRID"),
    ("W08", "DIVERGED_MULTI_SCHOOL_NOTATION", "medical teaching and case procedure", True, False, "NONE", "CARRIER_SCHOOLS"),
    ("W09", "MEANINGFUL_RELATIONAL_SYSTEM", "route planning and resource allocation", True, False, "PAIR_SEMANTIC", "CARRIER_ADVERSARIAL_MATCHED"),
    ("W10", "SEMANTICS_LIGHT_GENERATOR", "semantics-light structured production", False, False, "PAIR_SEMANTIC", "CARRIER_ADVERSARIAL_MATCHED"),
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    data = {
        "schema": "GDT395_INTERFACE_FREEZE_V1",
        "status": "FROZEN_BEFORE_WORLD_DESIGN",
        "designer_policy": {
            "primary_model": "gpt-5.6-sol",
            "one_isolated_session_per_world": True,
            "fork_turns": "none",
            "forbidden_context": ["other_worlds", "decoder_outputs", "Voynich_semantic_hypotheses", "Voynich_sources"],
        },
        "decoder_policy": {
            "designers_excluded": True,
            "sol_high_capacity": 2,
            "luna_replication_minimum": 3,
            "observation_only": True,
        },
        "world_assignments": [
            {
                "world_id": wid, "broad_family": fam, "practical_domain": domain,
                "organic_required": organic, "clean_control": clean,
                "adversarial_pair_id": pair, "carrier_profile": carrier,
            }
            for wid, fam, domain, organic, clean, pair, carrier in ASSIGNMENTS
        ],
        "corpus_seeds": list(range(20)),
        "target_events_per_seed": 8448,
        "representations": ["FULL_GROUP", "HOST_LIKE", "COMPOSITE_STATE", "INFERRED_COMPONENTS", "CONSTRUCTION_SPAN", "RECORD_TOPOLOGY"],
        "properties": [
            "LEXICAL_IDENTITY", "SEMANTIC_ENTITY_IDENTITY", "HISTORICAL_STEM_ANCESTRY",
            "PRODUCTIVE_MORPHOLOGY", "FOSSILIZED_MORPHOLOGY", "FUNCTION_CLASS",
            "COORDINATOR_RELATION", "ALTERNATIVE_RELATION", "REFERENCE_ANAPHORA",
            "TEMPORAL_STATE_GATE", "SCOPE", "ENTITY_REUSE", "OPERATOR_CLASS",
            "RECORD_SCHEMA", "REGISTER_LOCAL_VARIANT", "SEMANTIC_CATEGORY",
            "ACTUAL_LEXICAL_MEANING",
        ],
        "thresholds": {
            "cluster": {"nmi_min": 0.35, "ari_min": 0.20, "pair_f1_min": 0.35},
            "relation": {"coverage_min": 0.25, "mrr_min": 0.15, "mrr_above_chance_min": 0.05},
            "scope": {"coverage_min": 0.25, "interval_iou_min": 0.35},
            "binary": {"balanced_accuracy_min": 0.65, "mcc_min": 0.20, "fdr_max": 0.40},
            "worlds_for_general": 7,
            "worlds_for_family_specific": 2,
            "semantics_light_false_positive_max": 0.10,
            "median_decoder_required": True,
        },
        "method_stress_tests": [
            "EXACT_COMPOSITE_AS_WORD", "UNIVERSAL_COEFFICIENTS", "RESIDUALIZE_FREQUENCY_POSITION_RECURRENCE",
            "SCALAR_ROLE_BOTTLENECK", "FIXED_SHORT_HORIZON", "MULTI_CONSTRAINT_INTERSECTION",
        ],
        "hashes": {
            str(p.relative_to(ROOT)): sha(p)
            for p in [EXP / "METHOD.md", EXP / "WORLD_DESIGN_CONTRACT.md", EXP / "DECODER_CONTRACT.md", EXP / "src/world_api.py", Path(__file__)]
        },
        "inputs": [],
        "voynich_rows": 0,
        "f84": {"opened": False, "parsed": False, "retained": False, "scored": False},
    }
    raw = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
    data["content_sha256"] = hashlib.sha256(raw).hexdigest()
    OUT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print(OUT.relative_to(ROOT), data["content_sha256"])


if __name__ == "__main__":
    main()
