#!/usr/bin/env python3
"""Validate RFH001's source bindings and frozen positive decision."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
METHOD = BASE / "RFH001_F73V_RETRACER_HOOK_METHOD.md"
SELECTION = BASE / "results/rfh001_f73v_retracer_hook_selection.json"
SELECTION_VALIDATION = BASE / "results/rfh001_f73v_retracer_hook_selection_validation.json"
RESULT = BASE / "results/rfh001_f73v_retracer_hook_result.json"
OUT = BASE / "results/rfh001_f73v_retracer_hook_validation.json"
REPORT = BASE / "results/rfh001_f73v_retracer_hook_validation_report.md"


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
        "target_locus_exact": result["source"]["target_locus"] == selection["selected"]["locus"] == "f73v.15",
        "outcome_registered": result["native_visual_judgment"]["outcome"] in selection["allowed_outcomes"],
        "all_five_positive_gates": len(gates) == 5 and all(value is True for value in gates.values()),
        "one_pair_zero_identity_changes_and_scores": result["counts"]["visible_hook_bearing_understroke_hookless_retracing_pairs"] == 1 and result["counts"]["character_identity_changes_established"] == 0 and result["counts"]["formal_associations_scored"] == 0,
        "decision_reconstructed": result["status"] == "PASS_ONE_VISIBLE_HOOK_BEARING_UNDERSTROKE_AND_HOOKLESS_RETRACING" and result["decision"] == "RETAIN_ONE_SOURCE_BOUND_RETRACING_LAYER_FEATURE_OMISSION",
    }
    if not all(checks.values()):
        raise SystemExit("validation failed")
    validation = {
        "experiment": "RFH001_RESULT_VALIDATION",
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
        "# RFH001 result validation\n\n"
        "Status: **PASS_10_CHECK_SOURCE_AND_DECISION_RECONSTRUCTION**\n\n"
        "Independent compact code binds the method, selection, prior validation, official image, exact locus, "
        "registered outcome, all-five gate pattern, one pair with zero identity changes/scores, canonical result, "
        "and positive decision. It reconstructs provenance and logic rather than claiming a second visual inspection.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
