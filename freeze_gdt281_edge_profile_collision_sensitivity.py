#!/usr/bin/env python3
"""Freeze GDT281 before collision-free edge-profile scoring."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parent
METHOD = R / "GDT281_EDGE_PROFILE_COLLISION_SENSITIVITY_METHOD.md"
MANIFEST = R / "gdt281_gdt280_freeze_manifest.tsv"
DESIGN = R / "gdt281_design.json"
FROZEN = [
    "GDT280_EDGE_COMPILER_FINE_DECOMPOSITION_METHOD.md",
    "GDT280_EDGE_COMPILER_FINE_DECOMPOSITION_REPORT.md",
    "gdt280_design.json", "gdt280_design_validation.json", "gdt280_gdt279_freeze_manifest.tsv",
    "gdt280_edge_scores.tsv", "gdt280_edge_shapley.tsv", "gdt280_edge_profiles.tsv",
    "gdt280_null_results.tsv", "gdt280_folio_scores.tsv", "gdt280_counterexamples.tsv",
    "gdt280_result.json", "gdt280_validation.json",
    "run_gdt280_edge_compiler_fine_decomposition.py", "validate_gdt280_edge_compiler_fine_decomposition.py",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value: dict) -> str:
    q = dict(value); q.pop("content_sha256", None)
    return hashlib.sha256(json.dumps(q, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def main() -> None:
    parent = json.loads((R / "gdt280_result.json").read_text())
    validation = json.loads((R / "gdt280_validation.json").read_text())
    assert parent["status"] == "VOYNICH_EDGE_PROFILE_DIFFERS_FROM_LATIN_RIGHT_FAMILY_LEAD"
    assert parent["content_sha256"] == csha(parent)
    assert validation["status"] == "PASS" and validation["result_sha256"] == sha(R / "gdt280_result.json")
    rows = [{"artifact": name, "frozen_sha256": sha(R / name)} for name in FROZEN]
    with MANIFEST.open("w", encoding="utf8", newline="") as handle:
        writer = csv.DictWriter(handle, ["artifact", "frozen_sha256"], delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)
    design = {
        "schema": "GDT281_EDGE_PROFILE_COLLISION_SENSITIVITY_DESIGN_V1",
        "status": "FROZEN_BEFORE_GDT281_EXACT_CONTEXT_SCORING",
        "parent_result_sha256": sha(R / "gdt280_result.json"),
        "parent_content_sha256": parent["content_sha256"],
        "method_sha256": sha(METHOD), "freeze_manifest_sha256": sha(MANIFEST),
        "primary_native_panels": ["LATIN_SCHOLASTIC_GRAPHEMATIC", "LATIN_MEDICAL_GRAPHEMATIC", "LATIN_15C_GRAPHEMATIC", "VOYNICH_REFERENCE"],
        "layout_bridge_panels": ["LATIN_MEDICAL_GRAPHEMATIC", "LATIN_15C_GRAPHEMATIC", "VOYNICH_REFERENCE"],
        "views": ["LENGTH_MATCHED_OVERLAY", "MATCHED_SAMPLE_NATIVE_LAYOUT", "NATIVE_ORDER"],
        "fixed_base": ["register", "record_ordinal", "field_ordinal", "within_field_position", "dy_closure", "b3", "line_close", "paragraph_close"],
        "edge_blocks": {"OUTER_WRAPPER": ["wrapper", "q_flag"], "LOCAL_FRAME": ["local_frame", "inner_d"], "RIGHT_FAMILY": ["right_family"], "DISPLAY_RENDERER": ["known_label_renderer"]},
        "subset_count": 16, "context_representation": "EXACT_IMMUTABLE_TUPLE_NO_HASH", "null_worlds": 64,
        "null_seed_family": "GDT276_MATCHED_CONTEXT_V1", "null_strata": ["register", "record_ordinal", "within_field_position", "host_length"],
        "constant_renderer_tolerance": 1e-10,
        "primary_representation": "PUBLISHED_EXACT_CONTEXT_WITH_LOFO_SAFE_SENSITIVITY",
        "new_control_corpora": 0, "semantic_assignments": 0, "hpr1_semantics_used": 0, "voynich_substrings_mined": 0,
        "f84": {"input_files": 0, "opened": False, "parsed": False, "retained": False, "joined": False, "scored": False},
        "claim_ceiling": "Collision sensitivity of an exposed edge-compression profile only; no abbreviation morphology language code notation meaning plaintext or translation.",
        "implementation_sha256": sha(Path(__file__)),
    }
    design["content_sha256"] = csha(design)
    DESIGN.write_text(json.dumps(design, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": design["status"], "frozen_files": len(rows)}, sort_keys=True))


if __name__ == "__main__":
    main()
