#!/usr/bin/env python3
"""Validate RBR002 bindings, census completeness, and frozen capacity logic."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent
METHOD = BASE / "RBR002_F67R2_COMPLETE_UNDERLAYER_CAPACITY_METHOD.md"
SELECTION = BASE / "results/rbr002_complete_underlayer_capacity_selection.json"
SELECTION_VALIDATION = BASE / "results/rbr002_complete_underlayer_capacity_selection_validation.json"
RESULT = BASE / "results/rbr002_complete_underlayer_capacity_result.json"
OUT = BASE / "results/rbr002_complete_underlayer_capacity_validation.json"
REPORT = BASE / "results/rbr002_complete_underlayer_capacity_validation_report.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    selection = json.loads(SELECTION.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    records = result["records"]
    recovery = {
        "MULTIPLE_UNDERSTROKE_SHAPES_RECOVERABLE",
        "ONE_UNDERSTROKE_SHAPE_RECOVERABLE",
    }
    total = sum(r["state"] in recovery for r in records)
    new = sum(r["state"] in recovery and not r["previously_exposed_for_underlayer_question"] for r in records)
    multiple = sum(r["state"] == "MULTIPLE_UNDERSTROKE_SHAPES_RECOVERABLE" for r in records)
    expected_loci = [r["locus"] for r in selection["records"]]
    expected_clocks = [r["clock_position"] for r in selection["records"]]
    expected_exposure = [r["previously_exposed_for_underlayer_question"] for r in selection["records"]]
    expected_regions = [
        ("https://collections.library.yale.edu/iiif/2/1006194/2450,1600,600,600/3000,/0/default.jpg", "b623e9cc70f6a1d2c78362d8e510934ce9256233989399670bdaeaad217b1b4f"),
        ("https://collections.library.yale.edu/iiif/2/1006194/2400,950,600,650/3000,/0/default.jpg", "644cb6cfee8056effa279ffcbd8b7373972a87a3ce5f09788332c9e9d7e9a083"),
        ("https://collections.library.yale.edu/iiif/2/1006194/2700,300,850,500/3000,/0/default.jpg", "2eb5f418ae3a421fcf6bcad18b9b656d6b3f90cf2a79707d98d2415808c34004"),
        ("https://collections.library.yale.edu/iiif/2/1006194/3300,300,520,300/2600,/0/default.jpg", "444be4f33c60fb92fca8620235eb2b4dc1adbacb9d48c04a9586c69061ea4c5c"),
        ("https://collections.library.yale.edu/iiif/2/1006194/3550,350,700,300/3000,/0/default.jpg", "452ff8d000b9a4c67a6eab101dbb64fc6c649d913d491c74a75eede295c44451"),
        ("https://collections.library.yale.edu/iiif/2/1006194/4050,550,750,350/3000,/0/default.jpg", "92657caff59ce100d72d1a683a6cb438e0b3d9ba588315bf52094a2a3650d740"),
        ("https://collections.library.yale.edu/iiif/2/1006194/4450,950,500,500/3000,/90/default.jpg", "10d638cdc5687b3afc0bfa934376f7436a2709645ee79966c105e0cd0ceaec0d"),
        ("https://collections.library.yale.edu/iiif/2/1006194/4600,1480,372,650/2604,/90/default.jpg", "16e167b489b8f05a663db3ce8a0d610d9eb1f5fd2ae6d76c395562bb2091b131"),
        ("https://collections.library.yale.edu/iiif/2/1006194/4200,1800,750,600/3000,/0/default.jpg", "f4f8e293ef786dfd2e4a2fd8762a84ba969b9c39d90b01ba2cd51f9bfeb198fe"),
        ("https://collections.library.yale.edu/iiif/2/1006194/3700,2350,750,400/3000,/0/default.jpg", "364d254824adb9643f91454ea6da01e4d3b29974451774d329a2228af81103a3"),
        ("https://collections.library.yale.edu/iiif/2/1006194/3350,2680,520,400/2600,/0/default.jpg", "22b68b44229729b847de57af019bee9a592f1ca395dcf9938ac4849d9a03003c"),
        ("https://collections.library.yale.edu/iiif/2/1006194/2700,2200,900,500/3000,/0/default.jpg", "6ae5c515de7b9c404c8fcfb3aa309b59cf4a64e4cab350d2113fc88cee8df0a1"),
    ]
    states = Counter(r["state"] for r in records)
    checks = {
        "canonical_result": RESULT.read_bytes() == (json.dumps(result, indent=2, sort_keys=True) + "\n").encode(),
        "method_bound": result["inputs"]["method_sha256"] == sha(METHOD),
        "selection_bound": result["inputs"]["selection_sha256"] == sha(SELECTION),
        "selection_validation_bound": result["inputs"]["selection_validation_sha256"] == sha(SELECTION_VALIDATION),
        "official_image_bound": result["inputs"]["official_full_image_sha256"] == selection["source"]["official_full_image_sha256"],
        "complete_frozen_order": len(records) == 12 and [r["locus"] for r in records] == expected_loci and [r["clock_position"] for r in records] == expected_clocks,
        "exposure_pattern_preserved": [r["previously_exposed_for_underlayer_question"] for r in records] == expected_exposure and sum(expected_exposure) == 3,
        "exact_region_bindings_preserved": [(r["target_region_url"], r["target_region_sha256"]) for r in records] == expected_regions,
        "state_partition_reconstructed": states == Counter({"NO_VISIBLE_UNDERLAYER_OR_UNRESOLVED": 6, "LAYERING_VISIBLE_SHAPES_NOT_RECOVERABLE": 4, "MULTIPLE_UNDERSTROKE_SHAPES_RECOVERABLE": 1, "ONE_UNDERSTROKE_SHAPE_RECOVERABLE": 1}),
        "recovery_counts_reconstructed": total == 2 and new == 0 and multiple == 1,
        "capacity_gates_reconstructed": result["capacity_gates"] == {
            "total_recovery_records": {"minimum": 8, "observed": 2, "passed": False},
            "previously_unexamined_recovery_records": {"minimum": 4, "observed": 0, "passed": False},
            "multiple_position_records": {"minimum": 3, "observed": 1, "passed": False},
        } and result["all_capacity_gates_passed"] is False,
        "stop_and_zero_identity_reconstructed": result["status"] == "STOP_INSUFFICIENT_COMPLETE_UNDERLAYER_RECOVERY_CAPACITY" and result["decision"] == "DO_NOT_BUILD_CORRECTED_RING_TRANSCRIPTION_METHOD_FROM_CURRENT_VISIBLE_IMAGE" and result["counts"]["correct_character_identities_established"] == 0 and result["counts"]["corrected_text_groups_produced"] == 0 and result["counts"]["formal_associations_scored"] == 0,
        "source_only_access_reconstructed": result["access"]["all_twelve_records_inspected"] is True and result["access"]["coordinate_correction_completed_before_any_new_record_state_assignment"] is True and result["access"]["ocr_clip_embedding_or_automated_image_recognition_used"] is False and result["access"]["enhancement_or_contrast_transformation_used"] is False,
    }
    if not all(checks.values()):
        raise SystemExit("validation failed: " + ", ".join(k for k, v in checks.items() if not v))
    validation = {
        "experiment": "RBR002_RESULT_VALIDATION",
        "status": "PASS_13_CHECK_SOURCE_CENSUS_AND_CAPACITY_DECISION_RECONSTRUCTION",
        "source_result_sha256": sha(RESULT),
        "check_count": len(checks),
        "checks": checks,
        "scope_note": "The validator reconstructs source bindings, complete-census accounting, and frozen thresholds from the recorded native-visual judgments; it does not claim a second machine reinspection.",
        "claim_ceiling": result["claim_ceiling"],
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# RBR002 result validation\n\n"
        "Status: **PASS_13_CHECK_SOURCE_CENSUS_AND_CAPACITY_DECISION_RECONSTRUCTION**\n\n"
        "Compact independent code binds the method, selection, prior validation, official image, exact twelve-record "
        "order, exposure pattern, four-state partition, recovery counts, all three failed thresholds, canonical result, "
        "zero-identity/score stop, and source-only access declaration. It reconstructs provenance and logic rather "
        "than re-inspecting pixels.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
