#!/usr/bin/env python3
"""Record the frozen RBR001 three-locus native-visual panel."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
METHOD = BASE / "RBR001_F67R2_RED_BROWN_RETRACING_METHOD.md"
SELECTION = BASE / "results/rbr001_f67r2_red_brown_selection.json"
SELECTION_VALIDATION = BASE / "results/rbr001_f67r2_red_brown_selection_validation.json"
OUT = BASE / "results/rbr001_f67r2_red_brown_result.json"
REPORT = BASE / "results/rbr001_f67r2_red_brown_result_report.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    selection = json.loads(SELECTION.read_text(encoding="utf-8"))
    validation = json.loads(SELECTION_VALIDATION.read_text(encoding="utf-8"))
    if validation["status"] != "PASS_10_CHECK_SOURCE_ONLY_RECONSTRUCTION":
        raise SystemExit("selection validation mismatch")

    loci = [
        {
            "locus": "f67r2.3",
            "clock_position": "11:30",
            "outcome": "RECOVERABLE_RED_OVER_BROWN_SHAPE_CHANGE",
            "target_region_url": "https://collections.library.yale.edu/iiif/2/1006194/3300,300,520,300/2600,/0/default.jpg",
            "target_region_sha256": "444be4f33c60fb92fca8620235eb2b4dc1adbacb9d48c04a9586c69061ea4c5c",
            "gates": {
                "registered_sector_locus_and_target_localized": True,
                "red_and_brown_ink_visually_separable": True,
                "bounded_brown_understroke_geometry_independently_traceable": True,
                "bounded_red_geometry_visibly_diverges_from_brown_geometry": True,
                "overlap_continuity_or_boundary_supports_red_after_brown": True,
            },
            "basis": (
                "The registered three-word 11:30 label is localized. Dense red replacements sit inside and "
                "across paler circular and curved brown strokes. At the first-word round members, the pale "
                "circumferences and projecting curve remain traceable beyond the compact red fills, while shared "
                "centres and overlap bind both states to the same glyph positions."
            ),
        },
        {
            "locus": "f67r2.7",
            "clock_position": "03:30",
            "outcome": "VISIBLE_LAYERING_NO_RECOVERABLE_SHAPE_PAIR",
            "target_region_url": "https://collections.library.yale.edu/iiif/2/1006194/4600,1480,372,650/2604,/90/default.jpg",
            "target_region_sha256": "16e167b489b8f05a663db3ce8a0d610d9eb1f5fd2ae6d76c395562bb2091b131",
            "gates": {
                "registered_sector_locus_and_target_localized": True,
                "red_and_brown_ink_visually_separable": True,
                "bounded_brown_understroke_geometry_independently_traceable": False,
                "bounded_red_geometry_visibly_diverges_from_brown_geometry": False,
                "overlap_continuity_or_boundary_supports_red_after_brown": True,
            },
            "basis": (
                "The right-edge 03:30 label and red-over-brown layering are locatable, but the earlier left side "
                "and final-glyph shapes named in the human note cannot be traced independently through the weak "
                "brown residues. Layering is visible without a defensible before/after shape pair."
            ),
        },
        {
            "locus": "f67r2.10",
            "clock_position": "06:30",
            "outcome": "RECOVERABLE_RED_OVER_BROWN_SHAPE_CHANGE",
            "target_region_url": "https://collections.library.yale.edu/iiif/2/1006194/3350,2680,520,400/2600,/0/default.jpg",
            "target_region_sha256": "22b68b44229729b847de57af019bee9a592f1ca395dcf9938ac4849d9a03003c",
            "gates": {
                "registered_sector_locus_and_target_localized": True,
                "red_and_brown_ink_visually_separable": True,
                "bounded_brown_understroke_geometry_independently_traceable": True,
                "bounded_red_geometry_visibly_diverges_from_brown_geometry": True,
                "overlap_continuity_or_boundary_supports_red_after_brown": True,
            },
            "basis": (
                "The registered three-word 06:30 label is localized. At the end of the first word, a thin brown "
                "descending plume remains visible beyond the compact red a-like terminal. Brown and red share the "
                "terminal body, while the red stops before the continuing brown curve, exposing both geometry and chronology."
            ),
        },
    ]
    positives = sum(row["outcome"] == "RECOVERABLE_RED_OVER_BROWN_SHAPE_CHANGE" for row in loci)
    result = {
        "experiment": "RBR001_F67R2_RED_BROWN_RETRACING",
        "status": "PASS_MULTIPLE_RECOVERABLE_RED_OVER_BROWN_SHAPE_STATES",
        "decision": "RETAIN_TWO_SOURCE_BOUND_RED_OVER_BROWN_SHAPE_PAIRS_AND_ONE_LAYERING_ONLY_LOCUS",
        "inputs": {
            "method_sha256": sha(METHOD),
            "selection_sha256": sha(SELECTION),
            "selection_validation_sha256": sha(SELECTION_VALIDATION),
            "official_full_image_sha256": "0518312a566ee713a46c9887d8b8b9d7141d14095e360661789c1dad9b5c0d1c",
        },
        "source": {"canvas_id": "1006194", "official_full_image_hash_verified_during_inspection": True},
        "loci": loci,
        "counts": {
            "registered_loci": 3,
            "positive_recoverable_shape_pairs": positives,
            "layering_only_loci": 1,
            "unresolved_loci": 0,
            "physical_folios": 1,
            "correct_character_identities_established": 0,
            "formal_associations_scored": 0,
        },
        "panel_gate": {"minimum_positive_loci": selection["panel_pass_minimum_positive_loci"], "observed_positive_loci": positives, "passed": positives >= selection["panel_pass_minimum_positive_loci"]},
        "access": {
            "official_image_pixels_opened": True,
            "manual_native_visual_inspection": True,
            "source_native_iiif_regions_and_rotation_used": True,
            "alternate_readings_used_for_localization_only": True,
            "ocr_clip_embedding_or_automated_image_recognition_used": False,
            "enhancement_or_contrast_transformation_used": False,
        },
        "claim_ceiling": (
            "Two registered f67r2 outer-ring loci preserve visually separable brown under-stroke geometry and "
            "divergent red retracing, while a third shows layering without a recoverable shape pair. This "
            "establishes multiple physical red-over-brown shape states, not correction intent, correct "
            "transcription, character identity or equivalence, sound, morphology, word, language, cipher, "
            "plaintext, meaning, or translation."
        ),
    }
    if positives != 2 or not result["panel_gate"]["passed"]:
        raise SystemExit("frozen panel decision mismatch")
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# RBR001 f67r2 red/brown result\n\n"
        "Status: **PASS_MULTIPLE_RECOVERABLE_RED_OVER_BROWN_SHAPE_STATES**\n\n"
        "Two of three prospectively selected outer-ring loci satisfy all five physical-state gates. At "
        "f67r2.3, pale circular and curved under-strokes remain around and beyond compact red replacements. At "
        "f67r2.10, a thin brown terminal plume continues beyond the red a-like ending at the same word endpoint. "
        "f67r2.7 shows red/brown layering but not an independently traceable earlier shape, so it is not counted positive.\n\n"
        "The two-of-three panel threshold passes. No brown form is assigned a character identity.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
