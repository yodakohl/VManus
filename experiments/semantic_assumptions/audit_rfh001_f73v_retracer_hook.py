#!/usr/bin/env python3
"""Record the frozen RFH001 native-visual judgment."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
METHOD = BASE / "RFH001_F73V_RETRACER_HOOK_METHOD.md"
SELECTION = BASE / "results/rfh001_f73v_retracer_hook_selection.json"
SELECTION_VALIDATION = BASE / "results/rfh001_f73v_retracer_hook_selection_validation.json"
OUT = BASE / "results/rfh001_f73v_retracer_hook_result.json"
REPORT = BASE / "results/rfh001_f73v_retracer_hook_result_report.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    selection = json.loads(SELECTION.read_text(encoding="utf-8"))
    validation = json.loads(SELECTION_VALIDATION.read_text(encoding="utf-8"))
    if validation["status"] != "PASS_9_CHECK_SOURCE_ONLY_RECONSTRUCTION":
        raise SystemExit("selection validation mismatch")

    outcome = "ORIGINAL_HOOK_VISIBLE_BENEATH_HOOKLESS_RETRACING"
    gates = {
        "grove_8_outer_band_label_and_f_like_second_glyph_localized": True,
        "bounded_hook_shaped_authorial_ink_feature_visible": True,
        "hook_continuous_with_lighter_target_understroke_not_neighbor_or_artifact": True,
        "darker_retracing_stroke_independently_traceable_and_omits_hook": True,
        "ink_density_boundary_and_shared_stem_support_understroke_precedence": True,
    }
    result = {
        "experiment": "RFH001_F73V_RETRACER_HOOK",
        "status": "PASS_ONE_VISIBLE_HOOK_BEARING_UNDERSTROKE_AND_HOOKLESS_RETRACING",
        "decision": "RETAIN_ONE_SOURCE_BOUND_RETRACING_LAYER_FEATURE_OMISSION",
        "inputs": {
            "method_sha256": sha(METHOD),
            "selection_sha256": sha(SELECTION),
            "selection_validation_sha256": sha(SELECTION_VALIDATION),
            "official_full_image_sha256": "4227e5261bb5986e605ddb4f58fa1526640955d778c06916a1c34734bb431141",
        },
        "source": {
            "canvas_id": "1006207",
            "target_locus": "f73v.15",
            "target_region_url": "https://collections.library.yale.edu/iiif/2/1006207/2390,2170,300,330/2400,/225/default.jpg",
            "target_region_sha256": "df90c7044b7e72d0eabe98649779af0dd38078b70e14d58dc379db0de539efab",
            "official_full_image_hash_verified_during_inspection": True,
        },
        "native_visual_judgment": {
            "outcome": outcome,
            "gates": gates,
            "basis": (
                "The Grove-8 outer-band yfaiin label and its f-like second glyph are securely localized on the "
                "official f73v canvas. In source-native 225-degree rotation, a pale bounded hook rises from and "
                "returns toward the lighter target stem. A materially darker retracing stroke follows the main "
                "vertical stem but terminates without following the hook. The hook is attached to the target "
                "glyph rather than a neighboring letter or figure line. Shared stem alignment plus the sharp "
                "ink-density transition supports a hook-bearing under-stroke predating a hookless retracing."
            ),
        },
        "counts": {
            "official_canvases_inspected": 1,
            "physical_folios": 1,
            "target_glyphs": 1,
            "visible_hook_bearing_understroke_hookless_retracing_pairs": 1,
            "character_identity_changes_established": 0,
            "formal_associations_scored": 0,
        },
        "access": {
            "official_image_pixels_opened": True,
            "manual_native_visual_inspection": True,
            "source_native_iiif_regions_and_rotation_used": True,
            "human_position_and_neighbor_transcriptions_used_for_localization_only": True,
            "ocr_clip_embedding_or_automated_image_recognition_used": False,
            "enhancement_or_contrast_transformation_used": False,
        },
        "claim_ceiling": (
            "One official-source glyph preserves a pale hook-bearing under-stroke beneath a darker hookless "
            "retracing. This establishes one retracing-layer feature omission, not correction intent, a different "
            "character, character equivalence, sound, morphology, word, language, cipher, plaintext, meaning, or translation."
        ),
    }
    if outcome not in selection["allowed_outcomes"] or not all(gates.values()):
        raise SystemExit("frozen positive decision mismatch")

    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# RFH001 f73v retracer-hook result\n\n"
        "Status: **PASS_ONE_VISIBLE_HOOK_BEARING_UNDERSTROKE_AND_HOOKLESS_RETRACING**\n\n"
        "The Grove-8 outer-band `yfaiin` label and its f-like second glyph are securely localized on the official "
        "Yale f73v canvas. In source-native rotation, a pale bounded hook is continuous with the lighter target "
        "stem. A materially darker retracing stroke follows the main vertical stem but stops without following "
        "the hook. The attached geometry, shared stem, and ink-density boundary satisfy all five frozen gates.\n\n"
        "This is one source-bound retracing-layer feature omission. It does not establish a character change or reading.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
