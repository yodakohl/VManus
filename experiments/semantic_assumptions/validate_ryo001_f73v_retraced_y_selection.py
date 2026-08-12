#!/usr/bin/env python3
"""Validate RYO001 source-only selection without image access."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
METHOD = BASE / "RYO001_F73V_RETRACED_Y_METHOD.md"
ANNOTATIONS = BASE / "results/existing_human_exact_locus_annotations.tsv"
SOURCE = BASE / "results/source_sta_group_alignment.tsv"
RESULT = BASE / "results/ryo001_f73v_retraced_y_selection.json"
OUT = BASE / "results/ryo001_f73v_retraced_y_selection_validation.json"
REPORT = BASE / "results/ryo001_f73v_retraced_y_selection_validation_report.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    with ANNOTATIONS.open(newline="", encoding="utf-8") as handle:
        rows = [row for row in csv.DictReader(handle, delimiter="\t") if "is retraced and may have been @o" in row["local_comment"]]
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        readings = {row["edition"]: row["nearest_basic_eva_primary"] for row in csv.DictReader(handle, delimiter="\t") if row["locus"] == "f73v.32"}
    checks = {
        "canonical_result": RESULT.read_bytes() == (json.dumps(result, indent=2, sort_keys=True) + "\n").encode(),
        "method_bound": result["inputs"]["method_sha256"] == sha(METHOD),
        "annotation_bound": result["inputs"]["human_annotation_tsv_sha256"] == sha(ANNOTATIONS),
        "reading_source_bound": result["inputs"]["source_sta_group_alignment_sha256"] == sha(SOURCE),
        "unique_selection": len(rows) == 1 and rows[0]["locus"] == "f73v.32",
        "exact_reading_witnesses": readings == result["alternate_reading_witnesses"] == {"ZL3b": "ypal", "IT2a": "ypal", "RF1b": "apal"},
        "official_canvas_bound": result["source"]["canvas_id"] == "1006207" and result["source"]["official_full_image_sha256"] == "4227e5261bb5986e605ddb4f58fa1526640955d778c06916a1c34734bb431141",
        "prior_screen_nonoverlap": result["prior_overlap"]["selected_locus_in_prior_instance_set"] is False,
        "target_and_formal_access_sealed": not any(result["access"].values()),
    }
    if not all(checks.values()):
        raise SystemExit("validation failed")
    validation = {
        "experiment": "RYO001_SELECTION_VALIDATION",
        "status": "PASS_9_CHECK_SOURCE_ONLY_RECONSTRUCTION",
        "source_result_sha256": sha(RESULT), "check_count": len(checks), "checks": checks,
        "claim_ceiling": result["claim_ceiling"],
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# RYO001 selection validation\n\n"
        "Status: **PASS_9_CHECK_SOURCE_ONLY_RECONSTRUCTION**\n\n"
        "Independent compact code reconstructs the unique retraced-y/may-have-been-o annotation, exact locus, "
        "three alternate-reading witnesses, source hashes, official canvas, prior-screen nonoverlap, canonical "
        "selection, and sealed target/formal access.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
