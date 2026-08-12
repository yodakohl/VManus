#!/usr/bin/env python3
"""Record the frozen RD5X3-001 native-visual topology judgment."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
METHOD = BASE / "RD5X3001_ROSETTES_DOORWAY_TOPOLOGY_METHOD.md"
SELECTION = BASE / "results/rd5x3001_rosettes_doorway_selection.json"
SELECTION_VALIDATION = BASE / "results/rd5x3001_rosettes_doorway_selection_validation.json"
OUT = BASE / "results/rd5x3001_rosettes_doorway_topology_result.json"
REPORT = BASE / "results/rd5x3001_rosettes_doorway_topology_result_report.md"

FULL_SHA = "4b08afeee514691b0a511099ca299aed544d6fd1782b7dee8df163dfc06354ed"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    selection = json.loads(SELECTION.read_text())
    validation = json.loads(SELECTION_VALIDATION.read_text())
    if validation["status"] != "PASS_8_CHECK_SOURCE_ONLY_RECONSTRUCTION":
        raise SystemExit("selection validation mismatch")
    if selection["source"]["official_full_image_sha256"] != FULL_SHA:
        raise SystemExit("image binding mismatch")
    outcome = "FIVE_DOORWAY_OWNED_THREE_ROW_LABELS"
    gates = {
        "five_distinct_openings_or_intercolumn_compartments": True,
        "three_local_short_baselines_in_at_least_four_openings": True,
        "visible_separation_between_adjacent_bundles": True,
        "no_continuous_baseline_crosses_multiple_openings": True,
        "fifth_opening_no_worse_than_crowded_or_ambiguous": True,
    }
    result = {
        "experiment": "RD5X3001_ROSETTES_DOORWAY_TOPOLOGY",
        "status": "PASS_LOCAL_FIVE_BY_THREE_AUTHOR_VISIBLE_SCHEMA",
        "decision": "RETAIN_FIVE_DOORWAY_OWNED_THREE_ROW_LAYOUT_ONLY",
        "inputs": {
            "method_sha256": sha(METHOD), "selection_sha256": sha(SELECTION),
            "selection_validation_sha256": sha(SELECTION_VALIDATION),
            "official_full_image_sha256": FULL_SHA,
        },
        "source": {
            "canvas_id": "1006231", "selected_panel": "southeast_Rosette_northwest_sector",
            "official_full_image_dimensions": [7925, 7268],
            "official_full_image_hash_verified_during_inspection": True,
            "official_iiif_region_and_rotation_views_used": True,
        },
        "native_visual_judgment": {
            "outcome": outcome,
            "gates": gates,
            "clear_three_row_openings_minimum": 4,
            "crowded_or_ambiguous_openings_maximum": 1,
            "basis": (
                "Five repeated inter-column openings are visibly separated by author-drawn supports beneath the "
                "striped canopy. Short baselines form local three-row stacks inside the openings and restart after "
                "each support; no baseline continues through multiple openings. At least four openings are clear, "
                "while the remaining crowded/faint area does not contradict the repeated bundle geometry."
            ),
        },
        "counts": {
            "official_canvases_inspected": 1, "physical_folios": 1,
            "author_visible_doorway_records": 5, "positions_per_record": 3,
            "frozen_text_loci": 15, "voynich_fillers_used_for_judgment": 0,
            "formal_features_or_associations_scored": 0,
        },
        "access": {
            "official_image_pixels_opened": True, "manual_native_visual_inspection": True,
            "iiif_source_rotation_used_for_geometry_only": True,
            "ocr_clip_embedding_or_automated_image_recognition_used": False,
            "filler_identity_or_formal_feature_used": False,
            "prior_accidental_filler_exposure_disclosed": True,
        },
        "claim_ceiling": (
            "The Rosettes foldout contains one local five-record by three-position author-visible layout. This does "
            "not identify the records as door names or fields and establishes no list identity, word, sound, "
            "language, cipher, plaintext, meaning, or translation."
        ),
    }
    if not all(gates.values()) or outcome not in selection["allowed_outcomes"]:
        raise SystemExit("frozen outcome gate mismatch")
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(
        "# RD5X3-001 Rosettes doorway topology result\n\n"
        "Status: **PASS_LOCAL_FIVE_BY_THREE_AUTHOR_VISIBLE_SCHEMA**\n\n"
        "Direct inspection of the hash-matched official Yale foldout supports the five-label alternative. Five "
        "inter-column openings are separated by drawn supports beneath the striped canopy. The short baselines "
        "form local three-row stacks and restart after each support; none continues across multiple openings. "
        "At least four openings are clear, and the remaining crowded/faint area does not contradict the repeated "
        "bundle geometry.\n\n"
        "This resolves the public human annotation ambiguity in favor of five doorway-owned three-row records, "
        "not one three-line paragraph. The fillers played no role; their prior accidental display remains "
        "disclosed.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
