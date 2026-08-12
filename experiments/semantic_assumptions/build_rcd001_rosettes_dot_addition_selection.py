#!/usr/bin/env python3
"""Freeze the unique unhedged old-glyph/new-dot annotation before image access."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
METHOD = BASE / "RCD001_ROSETTES_DOT_ADDITION_METHOD.md"
ANNOTATIONS = BASE / "results/existing_human_exact_locus_annotations.tsv"
OUT = BASE / "results/rcd001_rosettes_dot_addition_selection.json"
REPORT = BASE / "results/rcd001_rosettes_dot_addition_selection_report.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    with ANNOTATIONS.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    selected = [
        row for row in rows
        if row["certainty"] == "UNHEDGED"
        and "old @e with a new dot" in row["local_comment"]
    ]
    if len(selected) != 1:
        raise SystemExit("selection is not unique")
    row = selected[0]
    if row["locus"] != "fRos.116" or row["old_locus"] != "f85v2.X7.51":
        raise SystemExit("registered locus mismatch")
    result = {
        "experiment": "RCD001_ROSETTES_DOT_ADDITION_SELECTION",
        "status": "FROZEN_ONE_UNHEDGED_TWO_STATE_ANNOTATION_TARGET_REGION_UNOPENED",
        "decision": "AUTHORIZE_ONE_NATIVE_VISUAL_SOURCE_INSPECTION",
        "inputs": {
            "method_sha256": sha(METHOD),
            "human_annotation_tsv_sha256": sha(ANNOTATIONS),
        },
        "selection_rule": (
            "Unique UNHEDGED exact-locus row whose local comment contains the literal old @e with a new dot."
        ),
        "selected": {
            "page": row["page"], "locus": row["locus"], "old_locus": row["old_locus"],
            "unit": row["unit"], "unit_description": row["unit_description"],
            "local_comment": row["local_comment"], "certainty": row["certainty"],
            "source_path": row["source_path"],
        },
        "source": {
            "canvas_id": "1006231",
            "official_full_image_sha256": "4b08afeee514691b0a511099ca299aed544d6fd1782b7dee8df163dfc06354ed",
            "official_full_image_dimensions": [7925, 7268],
        },
        "prior_overlap": {
            "processed_correction_pair_instances": ["f16r.2", "f24v.6", "f26r.1"],
            "selected_locus_in_prior_instance_set": False,
        },
        "allowed_outcomes": [
            "TWO_STATE_BASE_PLUS_LATER_DOT_VISIBLE", "CURRENT_COMPLEX_GLYPH_ONLY", "UNRESOLVED_SOURCE_IMAGE"
        ],
        "access": {
            "target_region_opened_before_freeze": False,
            "formal_features_or_associations_scored": False,
            "ocr_clip_embedding_or_automated_recognition_used": False,
        },
        "claim_ceiling": (
            "Selection authorizes one source-bound physical-glyph inspection only; it supplies no character "
            "sound, equivalence, word, language, cipher, plaintext, meaning, or translation."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# RCD001 Rosettes dot-addition selection\n\n"
        "Status: **FROZEN_ONE_UNHEDGED_TWO_STATE_ANNOTATION_TARGET_REGION_UNOPENED**\n\n"
        "The unique source row selected by the frozen rule is fRos.116. Its human comment explicitly alleges an "
        "old e-like glyph with a new dot. This locus was not part of the prior four-instance correction screen. "
        "The target region remains unopened for this question.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
