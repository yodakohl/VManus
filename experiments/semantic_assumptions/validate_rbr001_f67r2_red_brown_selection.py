#!/usr/bin/env python3
"""Validate RBR001 source-only selection without image access."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
METHOD = BASE / "RBR001_F67R2_RED_BROWN_RETRACING_METHOD.md"
HUMAN = BASE.parent.parent / "transcription/sources/Stolfi_text25e1-52.evt"
SOURCE = BASE / "results/source_sta_group_alignment.tsv"
RESULT = BASE / "results/rbr001_f67r2_red_brown_selection.json"
OUT = BASE / "results/rbr001_f67r2_red_brown_selection_validation.json"
REPORT = BASE / "results/rbr001_f67r2_red_brown_selection_validation_report.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    loci = [row["locus"] for row in result["selected"]]
    checks = {
        "canonical_result": RESULT.read_bytes() == (json.dumps(result, indent=2, sort_keys=True) + "\n").encode(),
        "method_bound": result["inputs"]["method_sha256"] == sha(METHOD),
        "human_source_bound": result["inputs"]["human_source_sha256"] == sha(HUMAN),
        "reading_source_bound": result["inputs"]["source_sta_group_alignment_sha256"] == sha(SOURCE),
        "exact_three_loci": loci == ["f67r2.3", "f67r2.7", "f67r2.10"],
        "all_readings_cover_each_locus": all(set(row["alternate_reading_witnesses"]) == {"ZL3b", "IT2a", "RF1b"} for row in result["selected"]),
        "two_nonrecoverable_comments_excluded": [row["locus"] for row in result["excluded_nonrecoverable_comments"]] == ["f67r2.6", "f67r2.11"],
        "official_canvas_bound": result["source"] == {"canvas_id": "1006194", "official_full_image_dimensions": [4972, 3738], "official_full_image_sha256": "0518312a566ee713a46c9887d8b8b9d7141d14095e360661789c1dad9b5c0d1c"},
        "target_and_formal_access_sealed": not any(result["access"].values()),
        "panel_gate_frozen": result["panel_pass_minimum_positive_loci"] == 2,
    }
    if not all(checks.values()):
        raise SystemExit("validation failed")
    validation = {
        "experiment": "RBR001_SELECTION_VALIDATION",
        "status": "PASS_10_CHECK_SOURCE_ONLY_RECONSTRUCTION",
        "source_result_sha256": sha(RESULT), "check_count": len(checks), "checks": checks,
        "claim_ceiling": result["claim_ceiling"],
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# RBR001 selection validation\n\n"
        "Status: **PASS_10_CHECK_SOURCE_ONLY_RECONSTRUCTION**\n\n"
        "Independent compact code binds the method, human and reading sources, exact three selected loci, "
        "three-reading coverage, two excluded nonrecoverable comments, official canvas, canonical selection, "
        "sealed access, and two-of-three panel threshold.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
