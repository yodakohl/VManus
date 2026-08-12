#!/usr/bin/env python3
"""Record the frozen SIA001 source-native native-visual result."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
METHOD = BASE / "SIA001_SUPRALINEAR_ADDITION_METHOD.md"
SELECTION = BASE / "results/sia001_supralinear_addition_selection.json"
SELECTION_VALIDATION = BASE / "results/sia001_supralinear_addition_selection_validation.json"
OUT = BASE / "results/sia001_supralinear_addition_result.json"
REPORT = BASE / "results/sia001_supralinear_addition_result_report.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def target(
    locus: str,
    outcome: str,
    gates: list[bool],
    full_sha256: str,
    region_url: str,
    region_sha256: str,
    basis: str,
) -> dict:
    names = [
        "registered_locus_and_target_word_securely_localized",
        "bounded_mark_materially_above_baseline",
        "unique_author_visible_baseline_host_or_gap",
        "separable_ink_or_placement_boundary",
        "baseline_form_physically_coherent_without_mark",
    ]
    return {
        "locus": locus,
        "outcome": outcome,
        "gates": dict(zip(names, gates, strict=True)),
        "all_five_gates_passed": all(gates),
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
    if validation["status"] != "PASS_9_CHECK_SOURCE_ONLY_RECONSTRUCTION":
        raise SystemExit("selection validation mismatch")

    targets = [
        target(
            "f31r.7",
            "SECURE_VISIBLE_SUPRALINEAR_INSERTION",
            [True, True, True, True, True],
            "3968b083d7346a556796d60e97a9ea66a4bb911fa1d085cfa046e9e0b37edc64",
            "https://collections.library.yale.edu/iiif/2/1006134/900,850,190,120/2717,/0/default.jpg",
            "40354b1901fbb141b44743ca8c711c783f8a76b6f5decb9b3fd9edef153fd66b",
            (
                "The registered fourth word of physical line 7 is securely localized. A compact dark plume sits "
                "well above the baseline word and returns through a long narrow stroke to one host position. Its "
                "dark density and noncontinuous high placement are separable from the lighter baseline sequence, "
                "whose letters remain spatially coherent without the plume."
            ),
        ),
        target(
            "f50v.8",
            "SECURE_VISIBLE_SUPRALINEAR_INSERTION",
            [True, True, True, True, True],
            "bbd4d60e069704fdfe91394ac07387022341c6cf08eb7d6d2160a34ea5b7677d",
            "https://collections.library.yale.edu/iiif/2/1006173/2680,770,180,130/2942,/0/default.jpg",
            "8be0b80ecca008f884cb131b55395c99ce06d3cdb153a5549dad71810423e214",
            (
                "The registered final word of physical line 8 is securely localized. A looped mark occupies the "
                "space materially above the gap between the two baseline components and descends to that one gap. "
                "The raised loop and narrow descending attachment have a clear nonbaseline placement boundary, "
                "while the two baseline components remain complete and physically coherent without it."
            ),
        ),
    ]
    panel_pass = len(targets) == 2 and all(t["all_five_gates_passed"] for t in targets)
    result = {
        "experiment": "SIA001_COMPLETE_SUPRALINEAR_ADDITION_RESULT",
        "status": (
            "PASS_RECURRENT_VISIBLE_SUPRALINEAR_INSERTION_PRACTICE"
            if panel_pass else "STOP_NO_RECURRENT_VISIBLE_SUPRALINEAR_INSERTION_PRACTICE"
        ),
        "decision": "RETAIN_TWO_PHYSICAL_SUPRALINEAR_INSERTION_EXAMPLES" if panel_pass else "RETAIN_ONLY_DESCRIPTIVE_LOCUS_RESULTS",
        "inputs": {
            "method_sha256": sha(METHOD),
            "selection_sha256": sha(SELECTION),
            "selection_validation_sha256": sha(SELECTION_VALIDATION),
        },
        "targets": targets,
        "counts": {
            "registered_targets": len(targets),
            "physical_folios": 2,
            "secure_visible_supralinear_insertions": sum(t["all_five_gates_passed"] for t in targets),
            "correct_glyph_identities_established": 0,
            "correction_intents_established": 0,
            "formal_associations_scored": 0,
        },
        "panel_rule": "BOTH_TWO_TARGETS_PASS_ALL_FIVE_PHYSICAL_GATES",
        "panel_passed": panel_pass,
        "access": {
            "official_source_native_iiif_pixels_used": True,
            "manual_native_visual_inspection": True,
            "one_classification_per_registered_target": True,
            "earlier_unrelated_full_page_exposure_disclosed": True,
            "target_regions_first_opened_after_selection_publication": True,
            "ocr_clip_embeddings_automated_segmentation_or_recognition_used": False,
            "enhancement_or_contrast_transformation_used": False,
            "alternate_readings_used_as_independent_replicates": False,
        },
        "claim_ceiling": (
            "Two physical manuscript loci preserve visible supralinear insertions anchored to coherent baseline "
            "writing. This establishes a recurrent physical insertion practice at the resolution of this complete "
            "human-comment panel. It does not establish either mark's correct glyph identity, correction intent, "
            "sound, morpheme, word, language, cipher, plaintext, meaning, or translation."
        ),
    }
    if not panel_pass:
        raise SystemExit("frozen panel decision mismatch")
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# SIA001 supralinear-addition result\n\n"
        "Status: **PASS_RECURRENT_VISIBLE_SUPRALINEAR_INSERTION_PRACTICE**\n\n"
        "Both members of the complete, prospectively frozen two-locus panel pass all five physical gates. "
        "At f31r.7, a compact dark plume is materially above and visually separable from a coherent baseline "
        "word, with a narrow stroke returning to one host position. At f50v.8, a raised loop is anchored by a "
        "narrow descending stroke to the unique gap between two otherwise coherent baseline components.\n\n"
        "The result supports recurrent physical supralinear insertion at these two folios. It does not tell us "
        "what either inserted mark represents or whether either intervention changed meaning. Earlier unrelated "
        "full-page exposure is disclosed; the registered target regions were first opened only after the selection "
        "and its validation were published.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
