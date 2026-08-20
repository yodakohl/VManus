#!/usr/bin/env python3
"""Publish the GDT392 source-materialization access correction."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


def root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("repository root not found")


ROOT = root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt392_special_circle_start_direction_census"
ART = BASE / "artifacts"
FREEZE = ART / "gdt392_pre_image_freeze.json"
INVENTORY = ROOT / "experiments/semantic_assumptions/results/special_circle_text_blind_array_inventory.tsv"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(obj: object) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> int:
    correction = {
        "schema": "GDT392_ACCESS_CORRECTION_V1",
        "status": "SOURCE_COMMENT_MATERIALIZATION_DISCLOSED",
        "superseded_freeze_sha256": sha(FREEZE),
        "source_inventory_sha256": sha(INVENTORY),
        "superseded_literal": {"voynich_surface_or_formal_rows_read": 0},
        "corrected_access": {
            "source_inventory_full_rows_materialized_before_review": 504,
            "source_catalogue_comments_may_contain_diplomatic_glyph_notes": True,
            "post_visual_review_search_displayed_some_catalogue_rows_with_diplomatic_notation": True,
            "formal_family_page_host_joint_tuple_or_renderer_rows_read": 0,
            "formal_identity_or_score_used_for_array_selection": False,
            "formal_identity_or_score_used_for_visual_direction_judgment": False,
            "source_comments_used_post_review_to_attribute_visible_start_boundaries": True,
            "formal_scoring_run": False,
            "f84_opened_parsed_retained_displayed_or_scored": False,
        },
        "chronology": [
            "The complete array frame and outcomes were frozen and publicly committed before focused image review.",
            "All 14 allow-listed canvases were directly reviewed before the focused source-comment search.",
            "The later source-comment search refined attribution of six already visible start-only boundaries and confirmed that clockwise wording was editorial; it did not supply a direction marker.",
            "No formal feature identity or score was opened at any stage.",
        ],
        "scientific_effect": "NONE_COUNTS_STATES_GATES_AND_DECISION_UNCHANGED",
    }
    correction["content_hash"] = digest(correction)
    (ART / "gdt392_access_correction.json").write_text(json.dumps(correction, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": correction["status"], "scientific_effect": correction["scientific_effect"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
