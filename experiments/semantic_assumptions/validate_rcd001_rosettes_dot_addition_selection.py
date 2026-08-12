#!/usr/bin/env python3
"""Validate RCD001's source-only selection without image access."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
METHOD = BASE / "RCD001_ROSETTES_DOT_ADDITION_METHOD.md"
ANNOTATIONS = BASE / "results/existing_human_exact_locus_annotations.tsv"
RESULT = BASE / "results/rcd001_rosettes_dot_addition_selection.json"
OUT = BASE / "results/rcd001_rosettes_dot_addition_selection_validation.json"
REPORT = BASE / "results/rcd001_rosettes_dot_addition_selection_validation_report.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    with ANNOTATIONS.open(newline="", encoding="utf-8") as handle:
        selected = [
            row for row in csv.DictReader(handle, delimiter="\t")
            if row["certainty"] == "UNHEDGED" and "old @e with a new dot" in row["local_comment"]
        ]
    checks = {
        "canonical_result": RESULT.read_bytes() == (json.dumps(result, indent=2, sort_keys=True) + "\n").encode(),
        "method_bound": result["inputs"]["method_sha256"] == sha(METHOD),
        "annotation_source_bound": result["inputs"]["human_annotation_tsv_sha256"] == sha(ANNOTATIONS),
        "unique_selection": len(selected) == 1,
        "exact_locus": len(selected) == 1 and selected[0]["locus"] == result["selected"]["locus"] == "fRos.116",
        "unhedged_two_state_comment": len(selected) == 1 and selected[0]["certainty"] == "UNHEDGED" and "old @e with a new dot" in selected[0]["local_comment"],
        "official_canvas_bound": result["source"]["canvas_id"] == "1006231" and result["source"]["official_full_image_sha256"] == "4b08afeee514691b0a511099ca299aed544d6fd1782b7dee8df163dfc06354ed",
        "prior_screen_nonoverlap": result["prior_overlap"]["selected_locus_in_prior_instance_set"] is False and "fRos.116" not in result["prior_overlap"]["processed_correction_pair_instances"],
        "image_and_formal_access_sealed": not any(result["access"].values()),
    }
    if not all(checks.values()):
        raise SystemExit("validation failed")
    validation = {
        "experiment": "RCD001_SELECTION_VALIDATION",
        "status": "PASS_9_CHECK_SOURCE_ONLY_RECONSTRUCTION",
        "source_result_sha256": sha(RESULT), "check_count": len(checks), "checks": checks,
        "claim_ceiling": result["claim_ceiling"],
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# RCD001 selection validation\n\n"
        "Status: **PASS_9_CHECK_SOURCE_ONLY_RECONSTRUCTION**\n\n"
        "Independent compact code reconstructs the unique unhedged old-glyph/new-dot row, exact locus, source "
        "bindings, prior-screen nonoverlap, official canvas, canonical selection, and sealed image/formal access.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
