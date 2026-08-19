#!/usr/bin/env python3
"""Freeze GDT374 before any operator-form enumeration or scoring."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt374_common_functional_operator_discovery"
ART = BASE / "artifacts"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    ART.mkdir(parents=True, exist_ok=True)
    inputs = [
        ROOT / "gdt327_joint_tuple_interlinear.tsv",
        ROOT / "experiments/semantic_assumptions/results/drawing_reset_segment_atlas.tsv",
        ROOT / "experiments/yolo/gdt373_functional_operator_roadmap/artifacts/gdt373_hypothesis_registry.tsv",
        ROOT / "experiments/yolo/gdt373_functional_operator_roadmap/artifacts/gdt373_candidate_signature_schema.tsv",
    ]
    freeze = {
        "schema": "GDT374_FREEZE_V1",
        "status": "FROZEN_NOT_RUN",
        "date": "2026-08-19",
        "seed": 37420260819,
        "permutation_worlds": 4096,
        "record_scopes": ["FIELD", "DRAWING_RESET_SEGMENT", "PHYSICAL_LINE"],
        "primary_endpoint": "FIELD_ONE_TUPLE_INSERTION_CLASS_HELD_PHYSICAL_FOLIO",
        "rewrite_library": [
            "PREFIX_INSERT_DELETE_ONE_ATOMIC_TUPLE",
            "SUFFIX_INSERT_DELETE_ONE_ATOMIC_TUPLE",
            "INTERNAL_INSERT_DELETE_ONE_ATOMIC_TUPLE",
            "PREFIX_REPLACE_ONE_ATOMIC_TUPLE_WITH_ANCHOR",
            "SUFFIX_REPLACE_ONE_ATOMIC_TUPLE_WITH_ANCHOR",
            "INTERNAL_REPLACE_ONE_ATOMIC_TUPLE_WITH_ANCHOR",
            "PAIRED_TWO_SITE_REPLACE_WITH_ANCHOR",
            "ADJACENT_EXACT_TUPLE_DUPLICATION",
            "BOUNDARY_SPLIT_JOIN_IDENTICAL_TUPLE_SEQUENCE",
            "PRIOR_RECORD_SHORTEN_RESUME_ONE_OR_TWO_DELETIONS"
        ],
        "baseline_features": ["SECTION", "REGISTER", "CURRIER", "HAND", "SOURCE_LENGTH", "FIELD_ORDINAL_BUCKET", "LINE_ENTRY", "RECORD_ORDINAL_BUCKET"],
        "full_additional_features": ["ATOMIC_TUPLE_BAG", "FIRST_ATOMIC_TUPLE", "LAST_ATOMIC_TUPLE"],
        "forbidden_features": ["HOST_ID", "PAGE_HOST", "COORDINATE_ID", "GLYPH", "SURFACE", "SUBSTRING", "TARGET_STATE", "VISUAL", "SEMANTIC"],
        "null_strata": ["SCOPE", "REWRITE_POSITION", "SECTION", "REGISTER", "CURRIER", "HAND", "SOURCE_LENGTH", "FIELD_ORDINAL_BUCKET", "LINE_ENTRY"],
        "minimum_mobile_events_for_null": 50,
        "minimum_candidate_base_sequences": 3,
        "minimum_candidate_physical_folios": 2,
        "f84_policy": "RAW_PAGE_GUARD_BEFORE_ROW_PARSE_REJECT_ALL_F84_PREFIXES",
        "candidate_forms_enumerated": 0,
        "scores_computed": 0,
        "semantic_roles_assigned": 0,
        "inputs": {str(path.relative_to(ROOT)): sha(path) for path in inputs},
        "documents": {str((BASE / "METHOD.md").relative_to(ROOT)): sha(BASE / "METHOD.md")},
        "implementation": {str((BASE / "src/freeze.py").relative_to(ROOT)): sha(BASE / "src/freeze.py")},
        "claim_ceiling": "ANONYMOUS_RECORD_CONDITIONED_FORMAL_REWRITE_BEHAVIOR_ONLY",
        "f84_accessed": False,
    }
    freeze["content_hash"] = hashlib.sha256(json.dumps(freeze, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    (ART / "gdt374_freeze.json").write_text(json.dumps(freeze, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
