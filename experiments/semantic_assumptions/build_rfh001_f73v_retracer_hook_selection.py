#!/usr/bin/env python3
"""Freeze the unique original-hook/retracer-omitted-it human annotation."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
METHOD = BASE / "RFH001_F73V_RETRACER_HOOK_METHOD.md"
ANNOTATIONS = BASE / "results/existing_human_exact_locus_annotations.tsv"
SOURCE = BASE / "results/source_sta_group_alignment.tsv"
OUT = BASE / "results/rfh001_f73v_retracer_hook_selection.json"
REPORT = BASE / "results/rfh001_f73v_retracer_hook_selection_report.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    with ANNOTATIONS.open(newline="", encoding="utf-8") as handle:
        selected = [
            row for row in csv.DictReader(handle, delimiter="\t")
            if "original hook" in row["local_comment"] and "Retracer did not do it" in row["local_comment"]
        ]
    if len(selected) != 1 or selected[0]["locus"] != "f73v.15":
        raise SystemExit("selection mismatch")
    row = selected[0]
    readings: dict[str, list[str]] = {}
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        for source_row in csv.DictReader(handle, delimiter="\t"):
            if source_row["locus"] == "f73v.15":
                readings.setdefault(source_row["edition"], []).append(source_row["nearest_basic_eva_primary"])
    if readings != {"ZL3b": ["yfaiin", "y"], "IT2a": ["yfaiin", "y"], "RF1b": ["yfaiiny"]}:
        raise SystemExit("reading witness mismatch")
    result = {
        "experiment": "RFH001_F73V_RETRACER_HOOK_SELECTION",
        "status": "FROZEN_ONE_HEDGED_UNDERSTROKE_FEATURE_ANNOTATION_TARGET_GLYPH_UNOPENED",
        "decision": "AUTHORIZE_ONE_NATIVE_VISUAL_SOURCE_INSPECTION",
        "inputs": {
            "method_sha256": sha(METHOD),
            "human_annotation_tsv_sha256": sha(ANNOTATIONS),
            "source_sta_group_alignment_sha256": sha(SOURCE),
        },
        "selection_rule": "Unique exact-locus comment containing both original hook and Retracer did not do it.",
        "selected": {
            "page": row["page"], "locus": row["locus"], "old_locus": row["old_locus"],
            "unit": row["unit"], "unit_description": row["unit_description"],
            "local_comment": row["local_comment"], "certainty": row["certainty"],
            "source_path": row["source_path"],
        },
        "alternate_reading_witnesses": readings,
        "source": {
            "canvas_id": "1006207",
            "official_full_image_sha256": "4227e5261bb5986e605ddb4f58fa1526640955d778c06916a1c34734bb431141",
            "official_full_image_dimensions": [2979, 3724],
        },
        "prior_overlap": {
            "processed_correction_pair_instances": ["f16r.2", "f24v.6", "f26r.1"],
            "ryo001_instance": "f73v.32",
            "selected_locus_in_prior_instance_sets": False,
            "page_level_canvas_previously_viewed_for_unrelated_questions": True,
            "target_glyph_previously_viewed_for_this_question": False,
        },
        "allowed_outcomes": [
            "ORIGINAL_HOOK_VISIBLE_BENEATH_HOOKLESS_RETRACING",
            "CURRENT_F_LIKE_GLYPH_WITHOUT_SEPARABLE_ORIGINAL_HOOK",
            "UNRESOLVED_SOURCE_IMAGE",
        ],
        "access": {
            "target_glyph_opened_before_freeze": False,
            "formal_associations_scored": False,
            "ocr_clip_embedding_or_automated_recognition_used": False,
        },
        "claim_ceiling": (
            "Selection authorizes one source-bound physical-state inspection; it supplies no correction intent, "
            "character equivalence, sound, morphology, word, language, cipher, plaintext, meaning, or translation."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# RFH001 f73v retracer-hook selection\n\n"
        "Status: **FROZEN_ONE_HEDGED_UNDERSTROKE_FEATURE_ANNOTATION_TARGET_GLYPH_UNOPENED**\n\n"
        "The unique source row selected by the frozen rule is f73v.15. Its hedged human note proposes that an "
        "original hook remains visible although a retracer omitted it. ZL/IT record `yfaiin` plus `y`; RF records "
        "fused `yfaiiny`. These are localization witnesses, not replications. The target glyph remains unopened "
        "for this question.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
