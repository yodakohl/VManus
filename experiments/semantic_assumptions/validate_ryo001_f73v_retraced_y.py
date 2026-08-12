#!/usr/bin/env python3
"""Validate RYO001's source bindings and frozen unresolved decision."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
METHOD = BASE / "RYO001_F73V_RETRACED_Y_METHOD.md"
SELECTION = BASE / "results/ryo001_f73v_retraced_y_selection.json"
SELECTION_VALIDATION = BASE / "results/ryo001_f73v_retraced_y_selection_validation.json"
RESULT = BASE / "results/ryo001_f73v_retraced_y_result.json"
OUT = BASE / "results/ryo001_f73v_retraced_y_validation.json"
REPORT = BASE / "results/ryo001_f73v_retraced_y_validation_report.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    selection = json.loads(SELECTION.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    gates = result["native_visual_judgment"]["gates"]
    checks = {
        "canonical_result": RESULT.read_bytes() == (json.dumps(result, indent=2, sort_keys=True) + "\n").encode(),
        "method_bound": result["inputs"]["method_sha256"] == sha(METHOD),
        "selection_bound": result["inputs"]["selection_sha256"] == sha(SELECTION),
        "selection_validation_bound": result["inputs"]["selection_validation_sha256"] == sha(SELECTION_VALIDATION),
        "official_full_image_bound": result["inputs"]["official_full_image_sha256"] == selection["source"]["official_full_image_sha256"],
        "target_locus_exact": result["source"]["target_locus"] == selection["selected"]["locus"] == "f73v.32",
        "outcome_registered": result["native_visual_judgment"]["outcome"] in selection["allowed_outcomes"],
        "unresolved_gate_pattern": len(gates) == 5 and sum(bool(value) for value in gates.values()) == 3 and gates["closed_o_like_base_independently_traceable"] is False and gates["later_intervention_proved_by_overlap_boundary_or_interruption"] is False,
        "zero_recoverable_pairs_and_scores": result["counts"]["recoverable_before_after_pairs"] == 0 and result["counts"]["formal_associations_scored"] == 0,
        "decision_reconstructed": result["status"] == "STOP_UNRESOLVED_SOURCE_IMAGE_NO_RECOVERABLE_TWO_STATE_CHRONOLOGY" and result["decision"] == "RETAIN_HUMAN_RETRACED_Y_POSSIBLE_O_NOTE_AS_UNRESOLVED_PALEOGRAPHIC_PROPOSAL_ONLY",
    }
    if not all(checks.values()):
        raise SystemExit("validation failed")
    validation = {
        "experiment": "RYO001_RESULT_VALIDATION",
        "status": "PASS_10_CHECK_SOURCE_AND_DECISION_RECONSTRUCTION",
        "source_result_sha256": sha(RESULT),
        "check_count": len(checks),
        "checks": checks,
        "scope_note": (
            "The validator reconstructs source bindings and decision logic from the recorded native-visual "
            "judgment; it does not claim an independent machine reinspection."
        ),
        "claim_ceiling": result["claim_ceiling"],
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# RYO001 result validation\n\n"
        "Status: **PASS_10_CHECK_SOURCE_AND_DECISION_RECONSTRUCTION**\n\n"
        "Independent compact code binds the method, selection, prior validation, official full image, exact "
        "locus, registered outcome, three-of-five gate pattern, zero pair/score counts, canonical result, and "
        "stop decision. It reconstructs provenance and logic rather than claiming a second visual inspection.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
