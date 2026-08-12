#!/usr/bin/env python3
"""Record the frozen PIP001 direct native-visual panel result."""

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
OUT = BASE / "results/pip001_plume_intervention_result.json"
REPORT = BASE / "results/pip001_plume_intervention_result_report.md"

GATE_NAMES = [
    "registered_locus_and_annotated_target_securely_localized",
    "bounded_plume_materially_above_baseline",
    "unique_author_visible_baseline_host",
    "separable_ink_density_stroke_edge_or_placement_boundary",
    "baseline_host_physically_coherent_without_plume",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def target(
    locus: str,
    page: str,
    outcome: str,
    gates: list[bool],
    exposed: bool,
    full_sha256: str,
    region_url: str | None,
    region_sha256: str | None,
    basis: str,
) -> dict:
    return {
        "locus": locus,
        "page": page,
        "outcome": outcome,
        "gates": dict(zip(GATE_NAMES, gates, strict=True)),
        "all_five_gates_passed": all(gates),
        "previously_exposed_and_outcome_fixed": exposed,
        "official_full_image_sha256": full_sha256,
        "target_region_url": region_url,
        "target_region_sha256": region_sha256,
        "basis": basis,
    }


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    selection = json.loads(SELECTION.read_text(encoding="utf-8"))
    validation = json.loads(SELECTION_VALIDATION.read_text(encoding="utf-8"))
    if validation["status"] != "PASS_8_CHECK_SOURCE_ONLY_RECONSTRUCTION":
        raise SystemExit("selection validation mismatch")

    targets = [
        target(
            "f26r.1",
            "f26r",
            "VISIBLE_PLUME_CHRONOLOGY_UNRESOLVED",
            [True, True, True, False, True],
            True,
            "70dfb0d5a5d60c18190333b152e9498729e08e527ad962e00d4a5a60ba047ca7",
            None,
            None,
            (
                "The fixed processed-correction result securely localizes two plume-bearing forms, but the "
                "visible source does not preserve a separable earlier host plus later plume boundary. The prior "
                "outcome is carried forward without reinspection or reclassification."
            ),
        ),
        target(
            "f31r.7",
            "f31r",
            "SECURE_VISIBLE_SEPARABLE_PLUME_INTERVENTION",
            [True, True, True, True, True],
            True,
            "3968b083d7346a556796d60e97a9ea66a4bb911fa1d085cfa046e9e0b37edc64",
            "https://collections.library.yale.edu/iiif/2/1006134/900,850,190,120/2717,/0/default.jpg",
            "40354b1901fbb141b44743ca8c711c783f8a76b6f5decb9b3fd9edef153fd66b",
            (
                "The fixed SIA001 result preserves a compact dark plume materially above a coherent baseline "
                "word, with a narrow return to one host and a separable density and placement boundary. The "
                "prior outcome is carried forward without reclassification."
            ),
        ),
        target(
            "f37v.22",
            "f37v",
            "VISIBLE_PLUME_CHRONOLOGY_UNRESOLVED",
            [True, True, True, False, True],
            False,
            "56d2086b7ce7a126a494d472276b0f5fe025775604a9afd55e5bd8e2ef6f8649",
            "https://collections.library.yale.edu/iiif/2/1006147/300,2250,1500,140/2882,/0/default.jpg",
            "2bb75e737fcbccd8905a4b7da59a80cd77b632865be855dd13bf8072cf435137",
            (
                "The final word of the registered penultimate prose line and its plume-bearing complex are "
                "securely localized. A bounded high loop belongs to one baseline host, and the remaining host "
                "strokes are spatially coherent, but the loop is continuous with the current form and exposes no "
                "defensible density, edge, or placement boundary proving a separate intervention."
            ),
        ),
        target(
            "f81v.13",
            "f81v",
            "VISIBLE_PLUME_CHRONOLOGY_UNRESOLVED",
            [True, True, True, False, True],
            False,
            "bb1a2316e7fc2966f5761f591d79339c75dcfbc6c2c9ab2b88a37e800266d4bf",
            "https://collections.library.yale.edu/iiif/2/1006221/700,1150,650,160/2835,/0/default.jpg",
            "7628d8cacb40a1187a9c19f4d0506ee3a4b25f94fd7f96da985639a7bbb7782c",
            (
                "The annotated second word and raised compact mark above its e-like baseline position are "
                "securely localized. The mark is bounded and has one host, but the squashed strokes meet the "
                "current form without a recoverable overlap, ink-density, or noncontinuous-placement boundary "
                "that establishes a later plume state."
            ),
        ),
        target(
            "f81v.19",
            "f81v",
            "SECURE_VISIBLE_SEPARABLE_PLUME_INTERVENTION",
            [True, True, True, True, True],
            False,
            "bb1a2316e7fc2966f5761f591d79339c75dcfbc6c2c9ab2b88a37e800266d4bf",
            "https://collections.library.yale.edu/iiif/2/1006221/1500,1520,600,160/2835,/0/default.jpg",
            "fb500e1016317d8bc00782143cb1eadd4ff0225f9c54a6b47c283bf82ce0974b",
            (
                "The annotated first sh-complex in the sixth word is securely localized. Its compact upper "
                "plume is materially darker than the lighter baseline host, remains bounded above that host, and "
                "has a visible density boundary while the lower host sequence remains coherent without it. This "
                "supports a separable physical plume intervention, not a corrected character identity."
            ),
        ),
    ]
    positives = [target for target in targets if target["all_five_gates_passed"]]
    new_positives = [target for target in positives if not target["previously_exposed_and_outcome_fixed"]]
    positive_folios = sorted({target["page"] for target in positives})
    thresholds = selection["panel_gates"]
    panel_pass = (
        len(positives) >= thresholds["minimum_total_positives"]
        and len(new_positives) >= thresholds["minimum_new_target_positives"]
        and len(positive_folios) >= thresholds["minimum_positive_physical_folios"]
    )
    result = {
        "experiment": "PIP001_COMPLETE_PLUME_INTERVENTION_RESULT",
        "schema": "PIP001_RESULT_V1",
        "status": (
            "PASS_MAJORITY_VISIBLE_SEPARABLE_PLUME_INTERVENTION"
            if panel_pass
            else "STOP_NO_MAJORITY_VISIBLE_SEPARABLE_PLUME_INTERVENTION"
        ),
        "decision": "RETAIN_DESCRIPTIVE_LOCUS_OUTCOMES_ONLY" if not panel_pass else "RETAIN_COMPACT_PHYSICAL_INTERVENTION_PANEL",
        "inputs": {
            "method_sha256": sha(METHOD),
            "selection_sha256": sha(SELECTION),
            "selection_validation_sha256": sha(SELECTION_VALIDATION),
            "sia001_result_sha256": sha(SIA_RESULT),
            "processed_correction_screen_sha256": sha(CORRECTION_SCREEN),
        },
        "targets": targets,
        "counts": {
            "registered_targets": len(targets),
            "new_targets": 3,
            "physical_folios": 4,
            "all_five_gate_positives": len(positives),
            "new_target_positives": len(new_positives),
            "positive_physical_folios": len(positive_folios),
            "correct_character_identities_established": 0,
            "formal_associations_scored": 0,
        },
        "positive_loci": [target["locus"] for target in positives],
        "positive_physical_folios": positive_folios,
        "thresholds": thresholds,
        "threshold_passes": {
            "minimum_total_positives": len(positives) >= thresholds["minimum_total_positives"],
            "minimum_new_target_positives": len(new_positives) >= thresholds["minimum_new_target_positives"],
            "minimum_positive_physical_folios": len(positive_folios) >= thresholds["minimum_positive_physical_folios"],
        },
        "panel_passed": panel_pass,
        "access": {
            "official_source_native_iiif_pixels_used": True,
            "direct_native_visual_inspection_used": True,
            "one_classification_per_new_registered_target": True,
            "prior_outcomes_fixed_without_reinspection": True,
            "target_regions_first_opened_after_selection_publication": True,
            "ocr_clip_embeddings_automated_segmentation_or_recognition_used": False,
            "enhancement_or_contrast_transformation_used": False,
            "alternate_readings_treated_as_independent_replicates": False,
        },
        "claim_ceiling": (
            "Two of five human plume-intervention comments correspond to source-visible separable physical "
            "plumes, but the prospectively frozen majority, new-target, and folio thresholds all fail. Retain the "
            "two physical examples and three unresolved visible plume states only. This establishes no corrected "
            "character identity, correction intent, sound, morpheme, word, language, cipher, plaintext, meaning, "
            "or translation."
        ),
    }
    if panel_pass or any(result["threshold_passes"].values()):
        raise SystemExit("frozen stop decision mismatch")
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# PIP001 plume-intervention result\n\n"
        "Status: **STOP_NO_MAJORITY_VISIBLE_SEPARABLE_PLUME_INTERVENTION**\n\n"
        "Only f31r.7 (fixed from SIA001) and the newly inspected f81v.19 pass all five physical gates. "
        "The current forms at f26r.1, f37v.22, and f81v.13 contain visible plume-like writing, but no "
        "defensible ink, edge, overlap, or placement boundary separates a later plume state from the baseline "
        "host. The panel therefore reaches 2/5 total positives, 1/3 among new targets, and two positive folios; "
        "all three frozen thresholds fail.\n\n"
        "This is a clean limit on the visible-light method, not a finding that the human comments are false. "
        "The two physical interventions remain useful writing-process examples, while the other three require "
        "new physical-layer or spectral evidence before chronology can be claimed. No transcription is silently "
        "corrected.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
