#!/usr/bin/env python3
"""Validate RD5X3-001 source bindings and frozen topology decision."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
METHOD = BASE / "RD5X3001_ROSETTES_DOORWAY_TOPOLOGY_METHOD.md"
SELECTION = BASE / "results/rd5x3001_rosettes_doorway_selection.json"
SELECTION_VALIDATION = BASE / "results/rd5x3001_rosettes_doorway_selection_validation.json"
RESULT = BASE / "results/rd5x3001_rosettes_doorway_topology_result.json"
OUT = BASE / "results/rd5x3001_rosettes_doorway_topology_validation.json"
REPORT = BASE / "results/rd5x3001_rosettes_doorway_topology_validation_report.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    selection = json.loads(SELECTION.read_text())
    result = json.loads(RESULT.read_text())
    judgment = result["native_visual_judgment"]
    gates = judgment["gates"]
    checks = {
        "canonical_result": RESULT.read_bytes() == (json.dumps(result, indent=2, sort_keys=True) + "\n").encode(),
        "method_bound": result["inputs"]["method_sha256"] == sha(METHOD),
        "selection_bound": result["inputs"]["selection_sha256"] == sha(SELECTION),
        "selection_validation_bound": result["inputs"]["selection_validation_sha256"] == sha(SELECTION_VALIDATION),
        "official_image_hash_exact": result["inputs"]["official_full_image_sha256"] == selection["source"]["official_full_image_sha256"] == "4b08afeee514691b0a511099ca299aed544d6fd1782b7dee8df163dfc06354ed",
        "outcome_registered": judgment["outcome"] in selection["allowed_outcomes"],
        "all_five_geometry_gates": len(gates) == 5 and all(gates.values()),
        "five_by_three_counts": result["counts"]["author_visible_doorway_records"] == 5 and result["counts"]["positions_per_record"] == 3 and result["counts"]["frozen_text_loci"] == 15,
        "zero_filler_or_formal_use": result["counts"]["voynich_fillers_used_for_judgment"] == 0 and result["counts"]["formal_features_or_associations_scored"] == 0,
        "decision_reconstructed": result["status"] == "PASS_LOCAL_FIVE_BY_THREE_AUTHOR_VISIBLE_SCHEMA" and result["decision"] == "RETAIN_FIVE_DOORWAY_OWNED_THREE_ROW_LAYOUT_ONLY",
    }
    if not all(checks.values()):
        raise SystemExit("validation failed")
    validation = {
        "experiment": "RD5X3001_TOPOLOGY_VALIDATION",
        "status": "PASS_10_CHECK_SOURCE_AND_DECISION_RECONSTRUCTION",
        "source_result_sha256": sha(RESULT), "check_count": len(checks), "checks": checks,
        "reconstructed_outcome": judgment["outcome"],
        "scope_note": (
            "This validator reconstructs source bindings and the frozen decision from the recorded native-visual "
            "judgment; it does not claim an independent machine reinspection."
        ),
        "claim_ceiling": result["claim_ceiling"],
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(
        "# RD5X3-001 topology validation\n\n"
        "Status: **PASS_10_CHECK_SOURCE_AND_DECISION_RECONSTRUCTION**\n\n"
        "The validator binds the exact method, selection, selection validation, official image hash, registered "
        "outcome, five geometry gates, 5×3 counts, zero filler/formal use, canonical result, and final decision. "
        "It reconstructs provenance and logic from the recorded visual judgment rather than claiming a second "
        "visual inspection.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
