#!/usr/bin/env python3
"""Validate RBR002 complete inventory without image access."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
METHOD = BASE / "RBR002_F67R2_COMPLETE_UNDERLAYER_CAPACITY_METHOD.md"
HUMAN = BASE.parent.parent / "transcription/sources/Stolfi_text25e1-52.evt"
RESULT = BASE / "results/rbr002_complete_underlayer_capacity_selection.json"
OUT = BASE / "results/rbr002_complete_underlayer_capacity_selection_validation.json"
REPORT = BASE / "results/rbr002_complete_underlayer_capacity_selection_validation_report.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    records = result["records"]
    checks = {
        "canonical_result": RESULT.read_bytes() == (json.dumps(result, indent=2, sort_keys=True) + "\n").encode(),
        "method_bound": result["inputs"]["method_sha256"] == sha(METHOD),
        "human_source_bound": result["inputs"]["human_source_sha256"] == sha(HUMAN),
        "twelve_unique_records": len(records) == 12 and len({row["locus"] for row in records}) == 12,
        "fixed_clock_order": [(row["locus"], row["clock_position"]) for row in records] == [("f67r2.12", "08:30")] + [(f"f67r2.{i}", f"{(i+8)%12:02d}:30") for i in range(1, 12)],
        "exact_three_exposed": [row["locus"] for row in records if row["previously_exposed_for_underlayer_question"]] == ["f67r2.3", "f67r2.7", "f67r2.10"],
        "official_canvas_bound": result["source"] == {"canvas_id": "1006194", "official_full_image_dimensions": [4972, 3738], "official_full_image_sha256": "0518312a566ee713a46c9887d8b8b9d7141d14095e360661789c1dad9b5c0d1c"},
        "capacity_gates_exact": result["capacity_gates"] == {"minimum_records_with_multiple_recoverable_positions": 3, "minimum_previously_unexamined_records_with_recovery": 4, "minimum_records_with_recovery": 8},
        "nine_new_regions_sealed": result["access"]["nine_other_sector_regions_opened_before_freeze"] is False,
        "identity_and_automation_sealed": result["access"]["character_identities_or_corrected_text_scored"] is False and result["access"]["ocr_clip_embedding_or_automated_recognition_used"] is False,
    }
    if not all(checks.values()):
        raise SystemExit("validation failed")
    validation = {
        "experiment": "RBR002_SELECTION_VALIDATION",
        "status": "PASS_10_CHECK_SOURCE_ONLY_RECONSTRUCTION",
        "source_result_sha256": sha(RESULT), "check_count": len(checks), "checks": checks,
        "claim_ceiling": result["claim_ceiling"],
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# RBR002 selection validation\n\n"
        "Status: **PASS_10_CHECK_SOURCE_ONLY_RECONSTRUCTION**\n\n"
        "Independent compact code binds the method and human source, reconstructs twelve unique clock-ordered "
        "records, exact three-sector exposure, official canvas, all thresholds, sealed nine new regions, and "
        "zero identity/automation access.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
