#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt362_remaining_complete_array"
OUT = BASE / "artifacts/gdt362_canvas_correction.json"

import sys
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import canonical_json_bytes, sha256_file  # noqa: E402


def main() -> None:
    original = BASE / "artifacts/gdt362_freeze.json"
    catalogue = ROOT / "experiments/semantic_assumptions/cache/public_voynich_nu_catalogue/q19.html"
    payload = {
        "schema": "GDT362_CANVAS_CORRECTION_V1",
        "status": "CORRECTED_AFTER_LEFT_CANVAS_REVIEW_BEFORE_RIGHT_CANVAS_REVIEW_OR_FORMAL_QUERY",
        "superseded_selection_field": "single_canvas_1006250",
        "corrected_canvases": [
            {"canvas_id": "1006250", "dimensions": [2698, 3779],
             "image_sha256": "1122f1b13afdf1509402334816f95e5e9baa2b6c94aa9e347b04aa2e4e54f36b",
             "role": "F101V_LEFT_PART"},
            {"canvas_id": "1006251", "dimensions": [8176, 3864],
             "image_sha256": "30fd529fc6bf8999d5be48024ee6a1676af55e8d66dc0a4f77993fe2565e9d94",
             "role": "F101V_CONTINUATION_AT_LEFT_PLUS_F102R"},
        ],
        "locus_canvas_scope": {
            "f101v2.10": ["1006250"], "f101v2.11": ["1006250"],
            "f101v2.12": ["1006250"], "f101v2.13": ["1006250", "1006251"],
            "f101v2.14": ["1006251"], "f101v2.15": ["1006251"],
            "f101v2.16": ["1006251"], "f101v2.17": ["1006251"],
            "f101v2.18": ["1006251"],
        },
        "unchanged": ["unit", "loci", "visual_rubric", "AQ_predicate", "direction", "uncertain_rule", "null"],
        "access_at_correction": {
            "canvas_1006250_full_and_crops_displayed": True,
            "preliminary_left_target_visual_impressions_formed": True,
            "visual_state_artifact_frozen": False,
            "canvas_1006251_pixels_displayed": False,
            "canvas_1006251_hash_and_dimensions_checked_without_pixel_display": True,
            "target_formal_values_queried": False,
            "f84_accessed": False,
        },
        "inputs": {
            str(original.relative_to(ROOT)): sha256_file(original),
            str(catalogue.relative_to(ROOT)): sha256_file(catalogue),
            "experiments/yolo/gdt362_remaining_complete_array/CORRECTION.md": sha256_file(BASE / "CORRECTION.md"),
            "experiments/yolo/gdt362_remaining_complete_array/src/freeze_correction.py": sha256_file(Path(__file__)),
        },
        "claim_ceiling": "CANVAS_SCOPE_AND_ACCESS_CORRECTION_ONLY_NO_RESULT_OR_SEMANTIC_CLAIM",
    }
    OUT.write_bytes(canonical_json_bytes(payload))


if __name__ == "__main__":
    main()
