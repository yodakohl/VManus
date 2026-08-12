#!/usr/bin/env python3
"""Record the frozen one-pass F69VSD001 native-visual judgment."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
METHOD = BASE / "F69VSD001_AUTHOR_VISIBLE_START_DIRECTION_METHOD.md"
SELECTION = BASE / "results/f69vsd001_start_direction_selection.json"
SELECTION_VALIDATION = BASE / "results/f69vsd001_start_direction_selection_validation.json"
OUT = BASE / "results/f69vsd001_start_direction_result.json"
REPORT = BASE / "results/f69vsd001_start_direction_result_report.md"

METHOD_SHA = "677c1468618781dcc6416015b2f917f8accd62cecc2d53b7dae309c9bd0d892b"
FULL_SHA = "709419c3c6861c216b1746261884e08a38f1b5a2b052ad129e78cdd73697b5e9"
FULL_SIZE = [8886, 3876]
SCALED_SHA = "99d824d8d5491a2f4511a0c0f719f9f165063335f53540c63d12b3bbe6c73edf"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    selection = json.loads(SELECTION.read_text())
    validation = json.loads(SELECTION_VALIDATION.read_text())
    if sha(METHOD) != METHOD_SHA or selection["method_sha256"] != METHOD_SHA:
        raise SystemExit("method mismatch")
    if validation["status"] != "PASS_7_CHECK_SOURCE_ONLY_RECONSTRUCTION":
        raise SystemExit("selection validation mismatch")
    if selection["source"]["frozen_2000px_image_sha256"] != SCALED_SHA:
        raise SystemExit("scaled image binding mismatch")

    qualifying = {
        "unique_radial_leader_or_spoke": False,
        "arrowhead_or_continuous_directed_trail": False,
        "deliberate_band_break_with_unique_endpoint_mark": False,
        "slot_owned_plain_alphabet_or_numeral_start_mark": False,
        "uniquely_differentiated_slot_plus_independent_direction_cue": False,
    }
    exclusions_observed = {
        "repeated_central_star_spokes": True,
        "alternating_long_blue_and_short_pale_logs": True,
        "irregular_hand_drawn_spacing_or_paint_fading": True,
        "editorial_clock_or_grove_origin_required_to_name_first_slot": True,
    }
    outcome = "NONE"
    status = "STOP_NO_AUTHOR_VISIBLE_START_OR_DIRECTION_DEVICE"
    result = {
        "experiment": "F69VSD001_AUTHOR_VISIBLE_START_DIRECTION",
        "status": status,
        "decision": "CLOSE_F69V_VISUAL_START_DIRECTION_ROUTE",
        "inputs": {
            "method_sha256": sha(METHOD),
            "selection_sha256": sha(SELECTION),
            "selection_validation_sha256": sha(SELECTION_VALIDATION),
            "official_full_image_sha256": FULL_SHA,
            "official_2000px_image_sha256": SCALED_SHA,
        },
        "source": {
            "canvas_id": "1006199",
            "selected_panel": "f69v",
            "official_full_image_url": "https://collections.library.yale.edu/iiif/2/1006199/full/full/0/default.jpg",
            "official_2000px_image_url": "https://collections.library.yale.edu/iiif/2/1006199/full/2000,/0/default.jpg",
            "official_full_image_dimensions": FULL_SIZE,
            "official_full_image_hash_verified_during_inspection": True,
            "official_2000px_hash_verified_during_inspection": True,
        },
        "native_visual_judgment": {
            "outcome": outcome,
            "qualifying_devices": qualifying,
            "excluded_as_nondirectional": exclusions_observed,
            "basis": (
                "The 28 capped radial logs form a hand-drawn alternating long/short ring around a central star. "
                "The star has repeated spokes, not one unique leader. No arrowhead, directed trail, marked band "
                "junction, slot-owned plain/numeral start mark, or uniquely differentiated slot paired with an "
                "independent direction cue is visible."
            ),
        },
        "counts": {
            "official_canvases_inspected": 1,
            "selected_panels_inspected": 1,
            "qualifying_devices": sum(qualifying.values()),
            "author_visible_start_devices": 0,
            "author_visible_direction_devices": 0,
            "voynich_strings_loaded_or_transcribed": 0,
            "formal_features_or_associations_scored": 0,
        },
        "gates": {
            "source_hashes_verified": True,
            "frozen_rubric_used": True,
            "outcome_is_allowed": outcome in selection["allowed_outcomes"],
            "positive_device_present": any(qualifying.values()),
            "text_identity_excluded": True,
            "grove_editorial_origin_excluded": True,
        },
        "access": {
            "official_image_pixels_opened": True,
            "manual_native_visual_inspection": True,
            "ocr_clip_embedding_or_automated_image_recognition_used": False,
            "voynich_transcription_or_formal_table_opened": False,
        },
        "claim_ceiling": (
            "The f69v 28-slot ring has no author-visible physical start or traversal-direction device under the "
            "frozen rubric. Its X1.1 origin remains editorial. This establishes no slot value, roster, word, "
            "sound, language, cipher, plaintext, meaning, or translation."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# F69VSD001 author-visible start/direction result\n\n"
        f"Status: **{status}**\n\n"
        "Direct inspection of the hash-bound official Yale canvas records `NONE`. The 28 capped radial logs "
        "alternate long/short around a central star, but no unique spoke, arrowhead, directed trail, marked "
        "junction, owned numeral/plain mark, or differentiated slot with an independent direction cue is visible. "
        "Repeated star spokes, paint/fading differences, hand-drawn spacing, clock position, and Grove's numbering "
        "do not qualify.\n\n"
        "The current `X1.1--X1.28` sequence therefore remains an editorial cyclic coordinate without a visible "
        "authorial origin or traversal direction. No Voynich string or formal feature was opened.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
