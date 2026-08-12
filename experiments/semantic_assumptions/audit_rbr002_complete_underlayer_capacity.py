#!/usr/bin/env python3
"""Record the frozen RBR002 complete outer-ring native-visual census."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
METHOD = BASE / "RBR002_F67R2_COMPLETE_UNDERLAYER_CAPACITY_METHOD.md"
SELECTION = BASE / "results/rbr002_complete_underlayer_capacity_selection.json"
SELECTION_VALIDATION = BASE / "results/rbr002_complete_underlayer_capacity_selection_validation.json"
OUT = BASE / "results/rbr002_complete_underlayer_capacity_result.json"
REPORT = BASE / "results/rbr002_complete_underlayer_capacity_result_report.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def row(
    locus: str,
    clock: str,
    exposed: bool,
    state: str,
    recoverable_positions: int,
    url: str,
    region_sha256: str,
    basis: str,
) -> dict:
    return {
        "locus": locus,
        "clock_position": clock,
        "previously_exposed_for_underlayer_question": exposed,
        "state": state,
        "recoverable_position_lower_bound": recoverable_positions,
        "target_region_url": url,
        "target_region_sha256": region_sha256,
        "basis": basis,
    }


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    selection = json.loads(SELECTION.read_text(encoding="utf-8"))
    validation = json.loads(SELECTION_VALIDATION.read_text(encoding="utf-8"))
    if validation["status"] != "PASS_10_CHECK_SOURCE_ONLY_RECONSTRUCTION":
        raise SystemExit("selection validation mismatch")

    records = [
        row(
            "f67r2.12", "08:30", False, "LAYERING_VISIBLE_SHAPES_NOT_RECOVERABLE", 0,
            "https://collections.library.yale.edu/iiif/2/1006194/2450,1600,600,600/3000,/0/default.jpg",
            "b623e9cc70f6a1d2c78362d8e510934ce9256233989399670bdaeaad217b1b4f",
            "The label crosses the fold-damaged zone. Red and pale brown residues are both visible, but no bounded brown contour can be followed independently at one red glyph position.",
        ),
        row(
            "f67r2.1", "09:30", False, "NO_VISIBLE_UNDERLAYER_OR_UNRESOLVED", 0,
            "https://collections.library.yale.edu/iiif/2/1006194/2400,950,600,650/3000,/0/default.jpg",
            "644cb6cfee8056effa279ffcbd8b7373972a87a3ce5f09788332c9e9d7e9a083",
            "The red label is localized. No same-position brown geometry visibly diverges from or continues beyond a red stroke.",
        ),
        row(
            "f67r2.2", "10:30", False, "NO_VISIBLE_UNDERLAYER_OR_UNRESOLVED", 0,
            "https://collections.library.yale.edu/iiif/2/1006194/2700,300,850,500/3000,/0/default.jpg",
            "2eb5f418ae3a421fcf6bcad18b9b656d6b3f90cf2a79707d98d2415808c34004",
            "The complete red record is visible, but the pale marks outside it belong to ring decoration or neighboring writing; no same-position brown under-stroke is independently traceable.",
        ),
        row(
            "f67r2.3", "11:30", True, "MULTIPLE_UNDERSTROKE_SHAPES_RECOVERABLE", 2,
            "https://collections.library.yale.edu/iiif/2/1006194/3300,300,520,300/2600,/0/default.jpg",
            "444be4f33c60fb92fca8620235eb2b4dc1adbacb9d48c04a9586c69061ea4c5c",
            "RBR001 established at least two first-word positions where pale circular or curved brown geometry remains bounded and traceable around or beyond compact red replacements at shared centers.",
        ),
        row(
            "f67r2.4", "00:30", False, "NO_VISIBLE_UNDERLAYER_OR_UNRESOLVED", 0,
            "https://collections.library.yale.edu/iiif/2/1006194/3550,350,700,300/3000,/0/default.jpg",
            "452ff8d000b9a4c67a6eab101dbb64fc6c649d913d491c74a75eede295c44451",
            "The red record is clear. Brown hatching beyond its upper edge is decorative ring content, not attached same-position glyph geometry; no under-stroke qualifies.",
        ),
        row(
            "f67r2.5", "01:30", False, "NO_VISIBLE_UNDERLAYER_OR_UNRESOLVED", 0,
            "https://collections.library.yale.edu/iiif/2/1006194/4050,550,750,350/3000,/0/default.jpg",
            "92657caff59ce100d72d1a683a6cb438e0b3d9ba588315bf52094a2a3650d740",
            "The red record is localized and several red strokes are lightly applied, but no separable brown contour diverges from the red geometry at a bounded glyph position.",
        ),
        row(
            "f67r2.6", "02:30", False, "LAYERING_VISIBLE_SHAPES_NOT_RECOVERABLE", 0,
            "https://collections.library.yale.edu/iiif/2/1006194/4450,950,500,500/3000,/90/default.jpg",
            "10d638cdc5687b3afc0bfa934376f7436a2709645ee79966c105e0cd0ceaec0d",
            "The damaged red record contains visibly mixed pale and red stroke material, especially near its initial complex, but neither color yields an independently bounded earlier shape pair.",
        ),
        row(
            "f67r2.7", "03:30", True, "LAYERING_VISIBLE_SHAPES_NOT_RECOVERABLE", 0,
            "https://collections.library.yale.edu/iiif/2/1006194/4600,1480,372,650/2604,/90/default.jpg",
            "16e167b489b8f05a663db3ce8a0d610d9eb1f5fd2ae6d76c395562bb2091b131",
            "RBR001 localized red-over-brown layering, but the proposed earlier left-side and terminal forms cannot be traced independently through the weak brown residues.",
        ),
        row(
            "f67r2.8", "04:30", False, "NO_VISIBLE_UNDERLAYER_OR_UNRESOLVED", 0,
            "https://collections.library.yale.edu/iiif/2/1006194/4200,1800,750,600/3000,/0/default.jpg",
            "f4f8e293ef786dfd2e4a2fd8762a84ba969b9c39d90b01ba2cd51f9bfeb198fe",
            "The small red record is visibly abraded, but no bounded brown geometry attached to a red glyph position remains independently traceable.",
        ),
        row(
            "f67r2.9", "05:30", False, "NO_VISIBLE_UNDERLAYER_OR_UNRESOLVED", 0,
            "https://collections.library.yale.edu/iiif/2/1006194/3700,2350,750,400/3000,/0/default.jpg",
            "364d254824adb9643f91454ea6da01e4d3b29974451774d329a2228af81103a3",
            "The red record is complete enough to localize. No same-position brown continuation or divergent bounded contour is visible.",
        ),
        row(
            "f67r2.10", "06:30", True, "ONE_UNDERSTROKE_SHAPE_RECOVERABLE", 1,
            "https://collections.library.yale.edu/iiif/2/1006194/3350,2680,520,400/2600,/0/default.jpg",
            "22b68b44229729b847de57af019bee9a592f1ca395dcf9938ac4849d9a03003c",
            "RBR001 established one first-word terminal where a thin brown descending plume continues beyond a compact red ending while both states share the terminal body.",
        ),
        row(
            "f67r2.11", "07:30", False, "LAYERING_VISIBLE_SHAPES_NOT_RECOVERABLE", 0,
            "https://collections.library.yale.edu/iiif/2/1006194/2700,2200,900,500/3000,/0/default.jpg",
            "6ae5c515de7b9c404c8fcfb3aa309b59cf4a64e4cab350d2113fc88cee8df0a1",
            "Faint pale marks coincide with parts of the red record and the final portion is damaged, but no earlier brown glyph contour can be bounded and followed independently.",
        ),
    ]

    recovery_states = {
        "MULTIPLE_UNDERSTROKE_SHAPES_RECOVERABLE",
        "ONE_UNDERSTROKE_SHAPE_RECOVERABLE",
    }
    total_recovery = sum(r["state"] in recovery_states for r in records)
    new_recovery = sum(r["state"] in recovery_states and not r["previously_exposed_for_underlayer_question"] for r in records)
    multiple = sum(r["state"] == "MULTIPLE_UNDERSTROKE_SHAPES_RECOVERABLE" for r in records)
    gates = {
        "total_recovery_records": {
            "minimum": selection["capacity_gates"]["minimum_records_with_recovery"],
            "observed": total_recovery,
            "passed": total_recovery >= selection["capacity_gates"]["minimum_records_with_recovery"],
        },
        "previously_unexamined_recovery_records": {
            "minimum": selection["capacity_gates"]["minimum_previously_unexamined_records_with_recovery"],
            "observed": new_recovery,
            "passed": new_recovery >= selection["capacity_gates"]["minimum_previously_unexamined_records_with_recovery"],
        },
        "multiple_position_records": {
            "minimum": selection["capacity_gates"]["minimum_records_with_multiple_recoverable_positions"],
            "observed": multiple,
            "passed": multiple >= selection["capacity_gates"]["minimum_records_with_multiple_recoverable_positions"],
        },
    }
    state_counts = {state: sum(r["state"] == state for r in records) for state in [
        "MULTIPLE_UNDERSTROKE_SHAPES_RECOVERABLE",
        "ONE_UNDERSTROKE_SHAPE_RECOVERABLE",
        "LAYERING_VISIBLE_SHAPES_NOT_RECOVERABLE",
        "NO_VISIBLE_UNDERLAYER_OR_UNRESOLVED",
    ]}
    result = {
        "experiment": "RBR002_COMPLETE_UNDERLAYER_CAPACITY",
        "status": "STOP_INSUFFICIENT_COMPLETE_UNDERLAYER_RECOVERY_CAPACITY",
        "decision": "DO_NOT_BUILD_CORRECTED_RING_TRANSCRIPTION_METHOD_FROM_CURRENT_VISIBLE_IMAGE",
        "inputs": {
            "method_sha256": sha(METHOD),
            "selection_sha256": sha(SELECTION),
            "selection_validation_sha256": sha(SELECTION_VALIDATION),
            "official_full_image_sha256": selection["source"]["official_full_image_sha256"],
        },
        "source": {"canvas_id": "1006194", "official_full_image_hash_verified_during_inspection": True},
        "records": records,
        "counts": {
            "registered_records": len(records),
            "previously_exposed_records": sum(r["previously_exposed_for_underlayer_question"] for r in records),
            "previously_unexamined_records": sum(not r["previously_exposed_for_underlayer_question"] for r in records),
            "records_with_recovery": total_recovery,
            "previously_unexamined_records_with_recovery": new_recovery,
            "records_with_multiple_recoverable_positions": multiple,
            "state_counts": state_counts,
            "correct_character_identities_established": 0,
            "corrected_text_groups_produced": 0,
            "formal_associations_scored": 0,
        },
        "capacity_gates": gates,
        "all_capacity_gates_passed": all(g["passed"] for g in gates.values()),
        "access": {
            "all_twelve_records_inspected": True,
            "coordinate_correction_completed_before_any_new_record_state_assignment": True,
            "manual_native_visual_inspection": True,
            "source_native_iiif_regions_and_rotation_used": True,
            "alternate_readings_used_for_localization_only": True,
            "ocr_clip_embedding_or_automated_image_recognition_used": False,
            "enhancement_or_contrast_transformation_used": False,
        },
        "claim_ceiling": (
            "The complete f67r2 outer-ring census retains recoverable divergent brown geometry in two records, "
            "both already exposed in RBR001, and none of the nine newly inspected records. The frozen completeness "
            "gates fail, so the current visible image cannot support a prospective corrected-ring transcription "
            "method. This does not negate the two physical retracing examples and establishes no character identity, "
            "corrected text, correction intent, sound, word, language, cipher, plaintext, meaning, or translation."
        ),
    }
    if total_recovery != 2 or new_recovery != 0 or multiple != 1 or result["all_capacity_gates_passed"]:
        raise SystemExit("frozen capacity decision mismatch")
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# RBR002 complete f67r2 underlayer-capacity result\n\n"
        "Status: **STOP_INSUFFICIENT_COMPLETE_UNDERLAYER_RECOVERY_CAPACITY**\n\n"
        "The fixed twelve-record census retains two records with recoverable divergent brown geometry: "
        "f67r2.3 has multiple positions and f67r2.10 has one. Both were already exposed in RBR001. None of "
        "the nine newly inspected records meets the same-position bounded-geometry rule. Four records show "
        "damage or layering without a defensible earlier shape, and six remain unresolved or show no visible underlayer.\n\n"
        "All three preregistered capacity gates fail: 2/12 versus 8 required, 0/9 new versus 4 required, "
        "and 1 multiple-position record versus 3 required. Do not build a corrected-ring transcription method "
        "from this visible-light image. The two RBR001 physical-state observations remain valid.\n\n"
        "The first broad localization crops used an incorrect equal-radius approximation of the elliptical ring. "
        "No states were assigned from them; the final source-native coordinates were fixed from the full canvas "
        "before classifying any newly opened record.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
