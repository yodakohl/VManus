#!/usr/bin/env python3
"""Record the frozen RYO001 native-visual judgment."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
METHOD = BASE / "RYO001_F73V_RETRACED_Y_METHOD.md"
SELECTION = BASE / "results/ryo001_f73v_retraced_y_selection.json"
SELECTION_VALIDATION = BASE / "results/ryo001_f73v_retraced_y_selection_validation.json"
OUT = BASE / "results/ryo001_f73v_retraced_y_result.json"
REPORT = BASE / "results/ryo001_f73v_retraced_y_result_report.md"


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
        "grove_9_inner_band_label_and_initial_localized": True,
        "closed_o_like_base_independently_traceable": False,
        "bounded_authorial_y_defining_stroke_visible": True,
        "later_intervention_proved_by_overlap_boundary_or_interruption": False,
        "o_like_y_like_description_source_glyph_only": True,
    }
    result = {
        "experiment": "RYO001_F73V_RETRACED_Y",
        "status": "STOP_UNRESOLVED_SOURCE_IMAGE_NO_RECOVERABLE_TWO_STATE_CHRONOLOGY",
        "decision": "RETAIN_HUMAN_RETRACED_Y_POSSIBLE_O_NOTE_AS_UNRESOLVED_PALEOGRAPHIC_PROPOSAL_ONLY",
        "inputs": {
            "method_sha256": sha(METHOD),
            "selection_sha256": sha(SELECTION),
            "selection_validation_sha256": sha(SELECTION_VALIDATION),
            "official_full_image_sha256": "4227e5261bb5986e605ddb4f58fa1526640955d778c06916a1c34734bb431141",
        },
        "source": {
            "canvas_id": "1006207",
            "target_locus": "f73v.32",
            "target_region_url": "https://collections.library.yale.edu/iiif/2/1006207/1030,2450,230,150/1840,/0/default.jpg",
            "target_region_sha256": "e0b3794679e8b50f33544bce76c44523b983f99d163998761515a28cd5a3db71",
            "official_full_image_hash_verified_during_inspection": True,
        },
        "native_visual_judgment": {
            "outcome": outcome,
            "gates": gates,
            "basis": (
                "The Grove-9 inner-band label and its initial glyph are securely localized on the official "
                "f73v canvas. The current initial has a bounded long y-like stroke and a darker compact lower "
                "junction. A loop-like lower mass can be perceived, but it is not independently traceable as a "
                "complete closed o-like base. The source image also exposes no overlap boundary, interruption, "
                "or separable ink edge proving that the long stroke was added later. Retracing of one current "
                "y-like glyph and transformation of an earlier o-like glyph remain observationally indistinguishable."
            ),
        },
        "counts": {
            "official_canvases_inspected": 1,
            "physical_folios": 1,
            "target_glyphs": 1,
            "recoverable_before_after_pairs": 0,
            "formal_associations_scored": 0,
        },
        "access": {
            "official_image_pixels_opened": True,
            "manual_native_visual_inspection": True,
            "source_native_iiif_regions_used": True,
            "human_position_and_neighbor_transcriptions_used_for_localization_only": True,
            "ocr_clip_embedding_or_automated_image_recognition_used": False,
            "enhancement_or_contrast_transformation_used": False,
        },
        "claim_ceiling": (
            "The official source shows one current retraced y-like initial, but not a separately recoverable "
            "o-like base or the chronology of its strokes. This establishes no correction, character "
            "equivalence, sound, morphology, word, language, cipher, plaintext, meaning, or translation."
        ),
    }
    if outcome not in selection["allowed_outcomes"]:
        raise SystemExit("unregistered outcome")
    if sum(bool(value) for value in gates.values()) != 3:
        raise SystemExit("frozen gate mismatch")
    if gates["closed_o_like_base_independently_traceable"] or gates["later_intervention_proved_by_overlap_boundary_or_interruption"]:
        raise SystemExit("positive physical-state gate unexpectedly passed")

    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# RYO001 f73v retraced-y result\n\n"
        "Status: **STOP_UNRESOLVED_SOURCE_IMAGE_NO_RECOVERABLE_TWO_STATE_CHRONOLOGY**\n\n"
        "The Grove-9 inner-band label and its initial glyph are securely localized on the official Yale f73v "
        "canvas. The initial has a bounded long y-like stroke and a darker compact lower junction. A loop-like "
        "lower mass is perceptible, but it cannot be traced independently as a complete closed o-like base. "
        "There is also no visible overlap boundary, interruption, or separable ink edge proving that the long "
        "stroke was added later. The frozen positive gates therefore fail.\n\n"
        "The human retraced-y/possible-o note remains an unresolved paleographic proposal, not a recoverable "
        "before/after glyph pair.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
