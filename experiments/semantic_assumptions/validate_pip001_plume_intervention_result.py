#!/usr/bin/env python3
"""Validate PIP001 source bindings, gate vectors, and panel stop."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
METHOD = BASE / "PIP001_PLUME_INTERVENTION_PANEL_METHOD.md"
SELECTION = BASE / "results/pip001_plume_intervention_selection.json"
SELECTION_VALIDATION = BASE / "results/pip001_plume_intervention_selection_validation.json"
SIA_RESULT = BASE / "results/sia001_supralinear_addition_result.json"
CORRECTION_SCREEN = BASE / "results/processed_correction_pair_worth_screen.json"
RESULT = BASE / "results/pip001_plume_intervention_result.json"
OUT = BASE / "results/pip001_plume_intervention_result_validation.json"
REPORT = BASE / "results/pip001_plume_intervention_result_validation_report.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    selection = json.loads(SELECTION.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    targets = result["targets"]
    expected_gate_vectors = [
        [True, True, True, False, True],
        [True, True, True, True, True],
        [True, True, True, False, True],
        [True, True, True, False, True],
        [True, True, True, True, True],
    ]
    expected_regions = [
        ("f26r.1", "70dfb0d5a5d60c18190333b152e9498729e08e527ad962e00d4a5a60ba047ca7", None, None),
        ("f31r.7", "3968b083d7346a556796d60e97a9ea66a4bb911fa1d085cfa046e9e0b37edc64", "https://collections.library.yale.edu/iiif/2/1006134/900,850,190,120/2717,/0/default.jpg", "40354b1901fbb141b44743ca8c711c783f8a76b6f5decb9b3fd9edef153fd66b"),
        ("f37v.22", "56d2086b7ce7a126a494d472276b0f5fe025775604a9afd55e5bd8e2ef6f8649", "https://collections.library.yale.edu/iiif/2/1006147/300,2250,1500,140/2882,/0/default.jpg", "2bb75e737fcbccd8905a4b7da59a80cd77b632865be855dd13bf8072cf435137"),
        ("f81v.13", "bb1a2316e7fc2966f5761f591d79339c75dcfbc6c2c9ab2b88a37e800266d4bf", "https://collections.library.yale.edu/iiif/2/1006221/700,1150,650,160/2835,/0/default.jpg", "7628d8cacb40a1187a9c19f4d0506ee3a4b25f94fd7f96da985639a7bbb7782c"),
        ("f81v.19", "bb1a2316e7fc2966f5761f591d79339c75dcfbc6c2c9ab2b88a37e800266d4bf", "https://collections.library.yale.edu/iiif/2/1006221/1500,1520,600,160/2835,/0/default.jpg", "fb500e1016317d8bc00782143cb1eadd4ff0225f9c54a6b47c283bf82ce0974b"),
    ]
    actual_gate_vectors = [list(target["gates"].values()) for target in targets]
    all_five = [all(vector) for vector in actual_gate_vectors]
    positives = [target["locus"] for target, passed in zip(targets, all_five, strict=True) if passed]
    new_positives = [target["locus"] for target, passed in zip(targets[2:], all_five[2:], strict=True) if passed]
    positive_folios = sorted({target["page"] for target, passed in zip(targets, all_five, strict=True) if passed})
    thresholds = selection["panel_gates"]
    threshold_passes = {
        "minimum_total_positives": len(positives) >= thresholds["minimum_total_positives"],
        "minimum_new_target_positives": len(new_positives) >= thresholds["minimum_new_target_positives"],
        "minimum_positive_physical_folios": len(positive_folios) >= thresholds["minimum_positive_physical_folios"],
    }
    checks = {
        "canonical_result": RESULT.read_bytes() == (json.dumps(result, indent=2, sort_keys=True) + "\n").encode(),
        "method_and_prior_artifacts_bound": result["inputs"] == {
            "method_sha256": sha(METHOD),
            "selection_sha256": sha(SELECTION),
            "selection_validation_sha256": sha(SELECTION_VALIDATION),
            "sia001_result_sha256": sha(SIA_RESULT),
            "processed_correction_screen_sha256": sha(CORRECTION_SCREEN),
        },
        "complete_registered_order": [target["locus"] for target in targets] == [target["locus"] for target in selection["targets"]] == ["f26r.1", "f31r.7", "f37v.22", "f81v.13", "f81v.19"],
        "exact_exposure_pattern": [target["previously_exposed_and_outcome_fixed"] for target in targets] == [True, True, False, False, False],
        "official_image_and_region_bindings": [(target["locus"], target["official_full_image_sha256"], target["target_region_url"], target["target_region_sha256"]) for target in targets] == expected_regions,
        "five_gate_vectors_reconstructed": actual_gate_vectors == expected_gate_vectors and [target["all_five_gates_passed"] for target in targets] == all_five,
        "registered_outcomes_reconstructed": [target["outcome"] for target in targets] == ["VISIBLE_PLUME_CHRONOLOGY_UNRESOLVED", "SECURE_VISIBLE_SEPARABLE_PLUME_INTERVENTION", "VISIBLE_PLUME_CHRONOLOGY_UNRESOLVED", "VISIBLE_PLUME_CHRONOLOGY_UNRESOLVED", "SECURE_VISIBLE_SEPARABLE_PLUME_INTERVENTION"],
        "panel_counts_reconstructed": result["counts"]["all_five_gate_positives"] == len(positives) == 2 and result["counts"]["new_target_positives"] == len(new_positives) == 1 and result["counts"]["positive_physical_folios"] == len(positive_folios) == 2 and result["positive_loci"] == positives == ["f31r.7", "f81v.19"] and result["positive_physical_folios"] == positive_folios == ["f31r", "f81v"],
        "all_three_thresholds_fail": result["thresholds"] == thresholds and result["threshold_passes"] == threshold_passes == {"minimum_total_positives": False, "minimum_new_target_positives": False, "minimum_positive_physical_folios": False},
        "stop_decision_reconstructed": result["panel_passed"] is False and result["status"] == "STOP_NO_MAJORITY_VISIBLE_SEPARABLE_PLUME_INTERVENTION" and result["decision"] == "RETAIN_DESCRIPTIVE_LOCUS_OUTCOMES_ONLY",
        "source_only_zero_semantic_access": result["access"]["official_source_native_iiif_pixels_used"] is True and result["access"]["ocr_clip_embeddings_automated_segmentation_or_recognition_used"] is False and result["access"]["enhancement_or_contrast_transformation_used"] is False and result["counts"]["correct_character_identities_established"] == 0 and result["counts"]["formal_associations_scored"] == 0,
    }
    if not all(checks.values()):
        raise SystemExit("validation failed: " + ", ".join(name for name, passed in checks.items() if not passed))
    validation = {
        "experiment": "PIP001_RESULT_VALIDATION",
        "status": "PASS_11_CHECK_SOURCE_GATE_AND_PANEL_STOP_RECONSTRUCTION",
        "source_result_sha256": sha(RESULT),
        "check_count": len(checks),
        "checks": checks,
        "scope_note": "The validator reconstructs source bindings, recorded visual gate vectors, and frozen panel arithmetic; it does not claim an independent visual reinspection.",
        "claim_ceiling": result["claim_ceiling"],
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# PIP001 result validation\n\n"
        "Status: **PASS_11_CHECK_SOURCE_GATE_AND_PANEL_STOP_RECONSTRUCTION**\n\n"
        "Compact independent code binds the method, selection, prior validation and fixed outcomes, exact five-locus "
        "order, exposure pattern, two official full-image hashes, three new target-region hashes, all five gate "
        "vectors, two total positives, one new positive, two positive folios, three failed thresholds, canonical "
        "result, stop decision, and zero-semantic-access ceiling. It reconstructs recorded provenance and logic "
        "rather than claiming a second visual inspection.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
