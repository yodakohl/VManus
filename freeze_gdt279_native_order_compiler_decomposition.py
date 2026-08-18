#!/usr/bin/env python3
"""Freeze GDT279 before any compiler-block decomposition is scored."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parent
METHOD = R / "GDT279_NATIVE_ORDER_COMPILER_DECOMPOSITION_METHOD.md"
MANIFEST = R / "gdt279_gdt278_freeze_manifest.tsv"
DESIGN = R / "gdt279_design.json"

FROZEN = [
    "GDT278_GDT277_MAGNITUDE_CALIBRATION_METHOD.md",
    "GDT278_CONTROL_SOURCE_AUDIT.md",
    "GDT278_GDT277_MAGNITUDE_CALIBRATION_REPORT.md",
    "gdt278_magnitude_design.json",
    "gdt278_magnitude_design_validation.json",
    "gdt278_control_source_freeze.json",
    "gdt278_control_source_validation.json",
    "gdt278_control_manifest.tsv",
    "gdt278_control_capacity.tsv",
    "gdt278_reference_magnitude.tsv",
    "gdt278_magnitude_scores.tsv",
    "gdt278_null_results.tsv",
    "gdt278_folio_scores.tsv",
    "gdt278_matched_event_inventory.tsv",
    "gdt278_native_event_inventory.tsv",
    "gdt278_counterexamples.tsv",
    "gdt278_result.json",
    "gdt278_validation.json",
    "run_gdt278_magnitude_calibration.py",
    "validate_gdt278_magnitude_calibration.py",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def content_hash(value: dict) -> str:
    q = dict(value)
    q.pop("content_sha256", None)
    return hashlib.sha256(
        json.dumps(q, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    ).hexdigest()


def main() -> None:
    old = json.loads((R / "gdt278_result.json").read_text())
    assert old["status"] == "VOYNICH_MAGNITUDE_ORDER_OR_MATCHING_SENSITIVE"
    assert old["content_sha256"] == content_hash(old)
    assert old["f84"] == {
        "input_files": 0,
        "joined": False,
        "opened": False,
        "parsed": False,
        "retained": False,
        "scored": False,
    }
    assert not any((R / p).name.startswith("gdt279_result") for p in FROZEN)
    rows = [{"artifact": p, "frozen_sha256": sha(R / p)} for p in FROZEN]
    with MANIFEST.open("w", encoding="utf8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            ["artifact", "frozen_sha256"],
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)

    design = {
        "schema": "GDT279_NATIVE_ORDER_COMPILER_DECOMPOSITION_DESIGN_V1",
        "status": "FROZEN_BEFORE_GDT279_BLOCK_SCORING",
        "parent_experiment": "GDT278_GDT277_MAGNITUDE_CALIBRATION",
        "parent_result_sha256": sha(R / "gdt278_result.json"),
        "parent_content_sha256": old["content_sha256"],
        "method_sha256": sha(METHOD),
        "freeze_manifest_sha256": sha(MANIFEST),
        "views": [
            "LENGTH_MATCHED_OVERLAY",
            "MATCHED_SAMPLE_NATIVE_LAYOUT",
            "NATIVE_ORDER",
        ],
        "blocks": {
            "OPPORTUNITY": [
                "register",
                "record_ordinal",
                "field_ordinal",
                "within_field_position",
            ],
            "EDGE_COMPILER": [
                "wrapper",
                "q_flag",
                "local_frame",
                "inner_d",
                "right_family",
                "known_label_renderer",
            ],
            "CLOSURE_BOUNDARY": [
                "dy_closure",
                "b3",
                "line_close",
                "paragraph_close",
            ],
        },
        "subset_count": 8,
        "context_bucket_count": 256,
        "null_worlds": 64,
        "null_seed_family": "GDT276_MATCHED_CONTEXT_V1",
        "null_strata": [
            "register",
            "record_ordinal",
            "within_field_position",
            "host_length",
        ],
        "endpoint": "NULL_MEAN_MINUS_OBSERVED_COMPILER_CHARACTER_BITS_PER_EVENT",
        "allocation": "EXACT_THREE_BLOCK_SHAPLEY",
        "layout_delta": "MATCHED_SAMPLE_NATIVE_LAYOUT_MINUS_LENGTH_MATCHED_OVERLAY",
        "selection_delta": "NATIVE_ORDER_MINUS_MATCHED_SAMPLE_NATIVE_LAYOUT",
        "primary_representation": "FROZEN_GDT278_PUBLISHED",
        "leakage_sensitivity": "GDT278_LOFO_SAFE_FULL_NULL_AND_OBSERVED_ALL_SUBSETS",
        "headline_population": "GDT278_NATIVE_REPRODUCTIONS_WITH_MATCHED_VIEW_FOR_LAYOUT",
        "tie_order": ["OPPORTUNITY", "EDGE_COMPILER", "CLOSURE_BOUNDARY"],
        "semantic_assignments": 0,
        "hpr1_semantics_used": 0,
        "voynich_substrings_mined": 0,
        "new_control_corpora": 0,
        "f84": {
            "input_files": 0,
            "opened": False,
            "parsed": False,
            "retained": False,
            "joined": False,
            "scored": False,
        },
        "claim_ceiling": (
            "Exposed compiler-context compression decomposition only; no language, "
            "abbreviation, code, notation, meaning, plaintext, or translation."
        ),
        "implementation_sha256": sha(Path(__file__)),
    }
    design["content_sha256"] = content_hash(design)
    DESIGN.write_text(json.dumps(design, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": design["status"], "frozen_files": len(rows)}, sort_keys=True))


if __name__ == "__main__":
    main()
