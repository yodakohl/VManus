#!/usr/bin/env python3
"""Validate RBR001's source bindings and panel decision."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
METHOD = BASE / "RBR001_F67R2_RED_BROWN_RETRACING_METHOD.md"
SELECTION = BASE / "results/rbr001_f67r2_red_brown_selection.json"
SELECTION_VALIDATION = BASE / "results/rbr001_f67r2_red_brown_selection_validation.json"
RESULT = BASE / "results/rbr001_f67r2_red_brown_result.json"
OUT = BASE / "results/rbr001_f67r2_red_brown_validation.json"
REPORT = BASE / "results/rbr001_f67r2_red_brown_validation_report.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    selection = json.loads(SELECTION.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    positives = [row for row in result["loci"] if row["outcome"] == "RECOVERABLE_RED_OVER_BROWN_SHAPE_CHANGE"]
    checks = {
        "canonical_result": RESULT.read_bytes() == (json.dumps(result, indent=2, sort_keys=True) + "\n").encode(),
        "method_bound": result["inputs"]["method_sha256"] == sha(METHOD),
        "selection_bound": result["inputs"]["selection_sha256"] == sha(SELECTION),
        "selection_validation_bound": result["inputs"]["selection_validation_sha256"] == sha(SELECTION_VALIDATION),
        "official_full_image_bound": result["inputs"]["official_full_image_sha256"] == selection["source"]["official_full_image_sha256"],
        "exact_locus_order": [row["locus"] for row in result["loci"]] == ["f67r2.3", "f67r2.7", "f67r2.10"],
        "two_all_gate_positives": len(positives) == 2 and all(all(value is True for value in row["gates"].values()) for row in positives),
        "middle_locus_layering_only": result["loci"][1]["outcome"] == "VISIBLE_LAYERING_NO_RECOVERABLE_SHAPE_PAIR" and sum(result["loci"][1]["gates"].values()) == 3,
        "panel_threshold_reconstructed": result["panel_gate"] == {"minimum_positive_loci": 2, "observed_positive_loci": 2, "passed": True},
        "decision_and_zero_identity_score_reconstructed": result["status"] == "PASS_MULTIPLE_RECOVERABLE_RED_OVER_BROWN_SHAPE_STATES" and result["counts"]["correct_character_identities_established"] == 0 and result["counts"]["formal_associations_scored"] == 0,
    }
    if not all(checks.values()):
        raise SystemExit("validation failed")
    validation = {
        "experiment": "RBR001_RESULT_VALIDATION",
        "status": "PASS_10_CHECK_SOURCE_AND_PANEL_DECISION_RECONSTRUCTION",
        "source_result_sha256": sha(RESULT), "check_count": len(checks), "checks": checks,
        "scope_note": "The validator reconstructs source bindings and panel logic from the recorded native-visual judgments; it does not claim an independent machine reinspection.",
        "claim_ceiling": result["claim_ceiling"],
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# RBR001 result validation\n\n"
        "Status: **PASS_10_CHECK_SOURCE_AND_PANEL_DECISION_RECONSTRUCTION**\n\n"
        "Independent compact code binds the method, selection, prior validation, official image, exact locus "
        "order, two all-gate positives, one layering-only locus, two-of-three panel threshold, canonical result, "
        "and zero-identity/score ceiling. It reconstructs provenance and logic rather than re-inspecting pixels.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
