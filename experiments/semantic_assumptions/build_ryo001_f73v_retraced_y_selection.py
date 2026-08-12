#!/usr/bin/env python3
"""Freeze the unique retraced-y/may-have-been-o human annotation."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
METHOD = BASE / "RYO001_F73V_RETRACED_Y_METHOD.md"
ANNOTATIONS = BASE / "results/existing_human_exact_locus_annotations.tsv"
SOURCE = BASE / "results/source_sta_group_alignment.tsv"
OUT = BASE / "results/ryo001_f73v_retraced_y_selection.json"
REPORT = BASE / "results/ryo001_f73v_retraced_y_selection_report.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    with ANNOTATIONS.open(newline="", encoding="utf-8") as handle:
        selected = [
            row for row in csv.DictReader(handle, delimiter="\t")
            if "is retraced and may have been @o" in row["local_comment"]
        ]
    if len(selected) != 1 or selected[0]["locus"] != "f73v.32":
        raise SystemExit("selection mismatch")
    row = selected[0]
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        readings = {
            source_row["edition"]: source_row["nearest_basic_eva_primary"]
            for source_row in csv.DictReader(handle, delimiter="\t")
            if source_row["locus"] == "f73v.32"
        }
    if readings != {"ZL3b": "ypal", "IT2a": "ypal", "RF1b": "apal"}:
        raise SystemExit("reading witness mismatch")
    result = {
        "experiment": "RYO001_F73V_RETRACED_Y_SELECTION",
        "status": "FROZEN_ONE_HEDGED_IDENTITY_CHANGE_ANNOTATION_TARGET_GLYPH_UNOPENED",
        "decision": "AUTHORIZE_ONE_NATIVE_VISUAL_SOURCE_INSPECTION",
        "inputs": {
            "method_sha256": sha(METHOD),
            "human_annotation_tsv_sha256": sha(ANNOTATIONS),
            "source_sta_group_alignment_sha256": sha(SOURCE),
        },
        "selection_rule": "Unique exact-locus comment containing the literal is retraced and may have been @o.",
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
            "selected_locus_in_prior_instance_set": False,
            "page_level_canvas_previously_viewed_for_unrelated_questions": True,
            "target_glyph_previously_viewed_for_this_question": False,
        },
        "allowed_outcomes": [
            "TWO_STATE_O_BASE_RETRACED_AS_Y_VISIBLE", "CURRENT_Y_LIKE_GLYPH_ONLY", "UNRESOLVED_SOURCE_IMAGE"
        ],
        "access": {
            "target_glyph_opened_before_freeze": False,
            "formal_associations_scored": False,
            "ocr_clip_embedding_or_automated_recognition_used": False,
        },
        "claim_ceiling": (
            "Selection authorizes one source-bound physical-state inspection; it supplies no correction intent, "
            "character equivalence, sound, word, language, cipher, plaintext, meaning, or translation."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# RYO001 f73v retraced-y selection\n\n"
        "Status: **FROZEN_ONE_HEDGED_IDENTITY_CHANGE_ANNOTATION_TARGET_GLYPH_UNOPENED**\n\n"
        "The unique source row selected by the frozen rule is f73v.32. Its human note proposes that a retraced "
        "y-like initial may originally have been o-like. ZL/IT read ypal and RF omits the uncertain initial as "
        "apal; these are localization witnesses, not replications. The target glyph remains unopened for this "
        "question.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
