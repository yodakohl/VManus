#!/usr/bin/env python3
"""Freeze GDT280 before scoring the fine edge-component family."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parent
METHOD = R / "GDT280_EDGE_COMPILER_FINE_DECOMPOSITION_METHOD.md"
MANIFEST = R / "gdt280_gdt279_freeze_manifest.tsv"
DESIGN = R / "gdt280_design.json"
FROZEN = [
    "GDT279_NATIVE_ORDER_COMPILER_DECOMPOSITION_METHOD.md",
    "GDT279_NATIVE_ORDER_COMPILER_DECOMPOSITION_REPORT.md",
    "gdt279_design.json",
    "gdt279_design_validation.json",
    "gdt279_gdt278_freeze_manifest.tsv",
    "gdt279_intermediate_event_inventory.tsv",
    "gdt279_view_scores.tsv",
    "gdt279_block_shapley.tsv",
    "gdt279_view_contrasts.tsv",
    "gdt279_folio_scores.tsv",
    "gdt279_null_results.tsv",
    "gdt279_counterexamples.tsv",
    "gdt279_result.json",
    "gdt279_validation.json",
    "run_gdt279_native_order_compiler_decomposition.py",
    "validate_gdt279_native_order_compiler_decomposition.py",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value: dict) -> str:
    q = dict(value)
    q.pop("content_sha256", None)
    return hashlib.sha256(json.dumps(q, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def main() -> None:
    parent = json.loads((R / "gdt279_result.json").read_text())
    validation = json.loads((R / "gdt279_validation.json").read_text())
    assert parent["status"] == "NATIVE_EXCESS_SHARED_OPPORTUNITY_INTERACTION_LEAD"
    assert parent["content_sha256"] == csha(parent)
    assert validation["status"] == "PASS" and validation["result_sha256"] == sha(R / "gdt279_result.json")
    manifest = [{"artifact": name, "frozen_sha256": sha(R / name)} for name in FROZEN]
    with MANIFEST.open("w", encoding="utf8", newline="") as handle:
        writer = csv.DictWriter(handle, ["artifact", "frozen_sha256"], delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(manifest)
    design = {
        "schema": "GDT280_EDGE_COMPILER_FINE_DECOMPOSITION_DESIGN_V1",
        "status": "FROZEN_BEFORE_GDT280_EDGE_SCORING",
        "parent_result_sha256": sha(R / "gdt279_result.json"),
        "parent_content_sha256": parent["content_sha256"],
        "method_sha256": sha(METHOD),
        "freeze_manifest_sha256": sha(MANIFEST),
        "views": ["LENGTH_MATCHED_OVERLAY", "MATCHED_SAMPLE_NATIVE_LAYOUT", "NATIVE_ORDER"],
        "fixed_base": ["register", "record_ordinal", "field_ordinal", "within_field_position", "dy_closure", "b3", "line_close", "paragraph_close"],
        "edge_blocks": {
            "OUTER_WRAPPER": ["wrapper", "q_flag"],
            "LOCAL_FRAME": ["local_frame", "inner_d"],
            "RIGHT_FAMILY": ["right_family"],
            "DISPLAY_RENDERER": ["known_label_renderer"],
        },
        "subset_count": 16,
        "context_bucket_count": 256,
        "null_worlds": 64,
        "null_seed_family": "GDT276_MATCHED_CONTEXT_V1",
        "null_strata": ["register", "record_ordinal", "within_field_position", "host_length"],
        "endpoint": "NULL_MEAN_MINUS_OBSERVED_COMPILER_CHARACTER_BITS_PER_EVENT",
        "allocation": "EXACT_FOUR_BLOCK_SHAPLEY_INCREMENT_OVER_FIXED_OPPORTUNITY_CLOSURE_BASE",
        "primary_representation": "FROZEN_GDT279_PUBLISHED",
        "leakage_sensitivity": "GDT279_LOFO_SAFE_OBSERVED_ALL_SUBSETS_WITH_INHERITED_FULL_NULL",
        "headline_native_controls": ["LATIN_SCHOLASTIC_GRAPHEMATIC", "LATIN_MEDICAL_GRAPHEMATIC", "LATIN_15C_GRAPHEMATIC", "VOYNICH_REFERENCE"],
        "tie_order": ["OUTER_WRAPPER", "LOCAL_FRAME", "RIGHT_FAMILY", "DISPLAY_RENDERER"],
        "new_control_corpora": 0,
        "semantic_assignments": 0,
        "hpr1_semantics_used": 0,
        "voynich_substrings_mined": 0,
        "f84": {"input_files": 0, "opened": False, "parsed": False, "retained": False, "joined": False, "scored": False},
        "claim_ceiling": "Fine allocation of exposed edge-conditioned character compression only; no abbreviation morphology language code notation meaning plaintext or translation.",
        "implementation_sha256": sha(Path(__file__)),
    }
    design["content_sha256"] = csha(design)
    DESIGN.write_text(json.dumps(design, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": design["status"], "frozen_files": len(manifest)}, sort_keys=True))


if __name__ == "__main__":
    main()
