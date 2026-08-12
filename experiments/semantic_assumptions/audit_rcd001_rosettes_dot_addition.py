#!/usr/bin/env python3
"""Record the frozen RCD001 native-visual judgment."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
METHOD = BASE / "RCD001_ROSETTES_DOT_ADDITION_METHOD.md"
SELECTION = BASE / "results/rcd001_rosettes_dot_addition_selection.json"
SELECTION_VALIDATION = BASE / "results/rcd001_rosettes_dot_addition_selection_validation.json"
OUT = BASE / "results/rcd001_rosettes_dot_addition_result.json"
REPORT = BASE / "results/rcd001_rosettes_dot_addition_result_report.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    selection = json.loads(SELECTION.read_text(encoding="utf-8"))
    validation = json.loads(SELECTION_VALIDATION.read_text(encoding="utf-8"))
    if validation["status"] != "PASS_9_CHECK_SOURCE_ONLY_RECONSTRUCTION":
        raise SystemExit("selection validation mismatch")
    outcome = "UNRESOLVED_SOURCE_IMAGE"
    gates = {
        "registered_label_and_target_glyph_located": True,
        "independent_e_like_base_curve_plausibly_visible": True,
        "bounded_authorial_dot_visible_not_wash_or_stain": True,
        "later_intervention_proved_by_overlap_or_ink_boundary": False,
        "base_to_completed_source_glyph_description_available": True,
    }
    result = {
        "experiment": "RCD001_ROSETTES_DOT_ADDITION",
        "status": "STOP_UNRESOLVED_SOURCE_IMAGE_NO_VISIBLE_CHRONOLOGY",
        "decision": "RETAIN_HUMAN_NOTE_AS_UNRESOLVED_PALEOGRAPHIC_PROPOSAL_ONLY",
        "inputs": {
            "method_sha256": sha(METHOD),
            "selection_sha256": sha(SELECTION),
            "selection_validation_sha256": sha(SELECTION_VALIDATION),
            "official_full_image_sha256": "4b08afeee514691b0a511099ca299aed544d6fd1782b7dee8df163dfc06354ed",
        },
        "source": {
            "canvas_id": "1006231",
            "target_locus": "fRos.116",
            "target_region_url": "https://collections.library.yale.edu/iiif/2/1006231/1500,6420,550,260/full/90/default.jpg",
            "target_region_sha256": "d035a8cee65f8729080c0a6bc9465f3d5d9250693ca76e8c2432fdda1fddab82",
            "official_full_image_hash_verified_during_inspection": True,
        },
        "native_visual_judgment": {
            "outcome": outcome,
            "gates": gates,
            "basis": (
                "The registered word and the glyph after the tall f-like sign are locatable on the official "
                "foldout. A compact dark dot is visibly bounded and a faint lower e-like curve is plausible. "
                "However, the source image exposes neither a superposition boundary nor a separable ink overlap "
                "that establishes that the dot postdates the curve. One current complex glyph and a later dot "
                "addition remain observationally indistinguishable."
            ),
        },
        "counts": {
            "official_canvases_inspected": 1,
            "physical_folios": 1,
            "target_glyphs": 1,
            "visible_bounded_dots": 1,
            "recoverable_before_after_pairs": 0,
            "formal_associations_scored": 0,
        },
        "access": {
            "official_image_pixels_opened": True,
            "manual_native_visual_inspection": True,
            "source_native_iiif_regions_and_rotation_used": True,
            "neighbor_transcriptions_used_for_locus_localization_only": True,
            "ocr_clip_embedding_or_automated_image_recognition_used": False,
            "enhancement_or_contrast_transformation_used": False,
        },
        "claim_ceiling": (
            "The official source shows a bounded dot and a plausible faint e-like curve in one current glyph, "
            "but not their chronology. This establishes no correction, character equivalence, sound, word, "
            "language, cipher, plaintext, meaning, or translation."
        ),
    }
    if outcome not in selection["allowed_outcomes"] or gates["later_intervention_proved_by_overlap_or_ink_boundary"]:
        raise SystemExit("frozen decision mismatch")
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# RCD001 Rosettes dot-addition result\n\n"
        "Status: **STOP_UNRESOLVED_SOURCE_IMAGE_NO_VISIBLE_CHRONOLOGY**\n\n"
        "The registered word and target glyph are locatable on the official Yale foldout. A compact bounded dot "
        "is visible, and a faint lower e-like curve is plausible. The frozen positive gate nevertheless fails: "
        "the image shows no separable overlap or ink boundary proving that the dot was applied after the curve. "
        "The pixels are equally compatible with one current complex glyph.\n\n"
        "The human old-e/new-dot note therefore remains an unresolved paleographic proposal, not a recoverable "
        "before/after correction pair.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
