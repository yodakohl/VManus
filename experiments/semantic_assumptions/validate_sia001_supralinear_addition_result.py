#!/usr/bin/env python3
"""Validate SIA001 provenance, gate vector, and frozen panel decision."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
METHOD = BASE / "SIA001_SUPRALINEAR_ADDITION_METHOD.md"
SELECTION = BASE / "results/sia001_supralinear_addition_selection.json"
SELECTION_VALIDATION = BASE / "results/sia001_supralinear_addition_selection_validation.json"
RESULT = BASE / "results/sia001_supralinear_addition_result.json"
OUT = BASE / "results/sia001_supralinear_addition_result_validation.json"
REPORT = BASE / "results/sia001_supralinear_addition_result_validation_report.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    selection = json.loads(SELECTION.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    targets = result["targets"]
    gate_names = [
        "registered_locus_and_target_word_securely_localized",
        "bounded_mark_materially_above_baseline",
        "unique_author_visible_baseline_host_or_gap",
        "separable_ink_or_placement_boundary",
        "baseline_form_physically_coherent_without_mark",
    ]
    expected_regions = [
        (
            "f31r.7",
            "3968b083d7346a556796d60e97a9ea66a4bb911fa1d085cfa046e9e0b37edc64",
            "https://collections.library.yale.edu/iiif/2/1006134/900,850,190,120/2717,/0/default.jpg",
            "40354b1901fbb141b44743ca8c711c783f8a76b6f5decb9b3fd9edef153fd66b",
        ),
        (
            "f50v.8",
            "bbd4d60e069704fdfe91394ac07387022341c6cf08eb7d6d2160a34ea5b7677d",
            "https://collections.library.yale.edu/iiif/2/1006173/2680,770,180,130/2942,/0/default.jpg",
            "8be0b80ecca008f884cb131b55395c99ce06d3cdb153a5549dad71810423e214",
        ),
    ]
    expected_gate_vector = {name: True for name in gate_names}
    checks = {
        "canonical_result": RESULT.read_bytes() == (json.dumps(result, indent=2, sort_keys=True) + "\n").encode(),
        "method_bound": result["inputs"]["method_sha256"] == sha(METHOD),
        "selection_bound": result["inputs"]["selection_sha256"] == sha(SELECTION),
        "selection_validation_bound": result["inputs"]["selection_validation_sha256"] == sha(SELECTION_VALIDATION),
        "complete_target_order": [t["locus"] for t in targets] == [t["locus"] for t in selection["targets"]] == ["f31r.7", "f50v.8"],
        "official_image_and_region_bindings": [
            (t["locus"], t["official_full_image_sha256"], t["target_region_url"], t["target_region_sha256"])
            for t in targets
        ] == expected_regions,
        "all_five_gate_vectors_reconstructed": all(t["gates"] == expected_gate_vector and t["all_five_gates_passed"] is True for t in targets),
        "registered_outcomes_reconstructed": all(t["outcome"] == "SECURE_VISIBLE_SUPRALINEAR_INSERTION" for t in targets),
        "panel_decision_reconstructed": result["panel_rule"] == "BOTH_TWO_TARGETS_PASS_ALL_FIVE_PHYSICAL_GATES" and result["panel_passed"] is True and result["status"] == "PASS_RECURRENT_VISIBLE_SUPRALINEAR_INSERTION_PRACTICE",
        "source_only_zero_semantic_access": result["access"]["official_source_native_iiif_pixels_used"] is True and result["access"]["ocr_clip_embeddings_automated_segmentation_or_recognition_used"] is False and result["access"]["enhancement_or_contrast_transformation_used"] is False and result["counts"]["correct_glyph_identities_established"] == 0 and result["counts"]["correction_intents_established"] == 0 and result["counts"]["formal_associations_scored"] == 0,
    }
    if not all(checks.values()):
        raise SystemExit("validation failed: " + ", ".join(k for k, v in checks.items() if not v))
    validation = {
        "experiment": "SIA001_RESULT_VALIDATION",
        "status": "PASS_10_CHECK_SOURCE_GATE_AND_PANEL_DECISION_RECONSTRUCTION",
        "source_result_sha256": sha(RESULT),
        "check_count": len(checks),
        "checks": checks,
        "scope_note": "The validator reconstructs provenance and the frozen gate/panel logic from recorded native-visual judgments; it does not claim a second visual reinspection.",
        "claim_ceiling": result["claim_ceiling"],
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# SIA001 result validation\n\n"
        "Status: **PASS_10_CHECK_SOURCE_GATE_AND_PANEL_DECISION_RECONSTRUCTION**\n\n"
        "Compact independent code binds the method, selection, prior validation, two official full-image hashes, "
        "two exact source-region hashes, complete locus order, both all-five gate vectors, the two-of-two panel "
        "decision, canonical result, and zero-semantic-access ceiling. It reconstructs provenance and decision "
        "logic rather than claiming an independent visual reinspection.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
