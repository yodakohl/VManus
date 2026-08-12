#!/usr/bin/env python3
"""Reconstruct the F69VSD001 provenance and frozen decision from recorded judgment."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
METHOD = BASE / "F69VSD001_AUTHOR_VISIBLE_START_DIRECTION_METHOD.md"
SELECTION = BASE / "results/f69vsd001_start_direction_selection.json"
SELECTION_VALIDATION = BASE / "results/f69vsd001_start_direction_selection_validation.json"
RESULT = BASE / "results/f69vsd001_start_direction_result.json"
OUT = BASE / "results/f69vsd001_start_direction_result_validation.json"
REPORT = BASE / "results/f69vsd001_start_direction_result_validation_report.md"

METHOD_SHA = "677c1468618781dcc6416015b2f917f8accd62cecc2d53b7dae309c9bd0d892b"
FULL_SHA = "709419c3c6861c216b1746261884e08a38f1b5a2b052ad129e78cdd73697b5e9"
SCALED_SHA = "99d824d8d5491a2f4511a0c0f719f9f165063335f53540c63d12b3bbe6c73edf"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    selection = json.loads(SELECTION.read_text())
    selection_validation = json.loads(SELECTION_VALIDATION.read_text())
    result = json.loads(RESULT.read_text())
    judgment = result["native_visual_judgment"]
    qualifying = judgment["qualifying_devices"]
    expected_status = (
        "STOP_NO_AUTHOR_VISIBLE_START_OR_DIRECTION_DEVICE"
        if judgment["outcome"] == "NONE" and not any(qualifying.values())
        else "NONSTOP"
    )
    checks = {
        "method_hash_exact": sha(METHOD) == METHOD_SHA,
        "selection_hash_bound": result["inputs"]["selection_sha256"] == sha(SELECTION),
        "selection_validation_hash_bound": result["inputs"]["selection_validation_sha256"] == sha(SELECTION_VALIDATION),
        "selection_validation_pass": selection_validation["status"] == "PASS_7_CHECK_SOURCE_ONLY_RECONSTRUCTION",
        "source_hashes_exact": result["inputs"]["official_full_image_sha256"] == FULL_SHA and result["inputs"]["official_2000px_image_sha256"] == SCALED_SHA,
        "outcome_registered": judgment["outcome"] in selection["allowed_outcomes"],
        "all_five_devices_negative": len(qualifying) == 5 and not any(qualifying.values()),
        "zero_text_or_formal_access": result["counts"]["voynich_strings_loaded_or_transcribed"] == 0 and result["counts"]["formal_features_or_associations_scored"] == 0,
        "decision_reconstructed": expected_status == result["status"] and result["decision"] == "CLOSE_F69V_VISUAL_START_DIRECTION_ROUTE",
        "canonical_result": RESULT.read_bytes() == (json.dumps(result, indent=2, sort_keys=True) + "\n").encode(),
    }
    if not all(checks.values()):
        raise SystemExit("validation failed")
    validation = {
        "experiment": "F69VSD001_RESULT_VALIDATION",
        "status": "PASS_10_CHECK_SOURCE_AND_DECISION_RECONSTRUCTION",
        "source_result_sha256": sha(RESULT),
        "check_count": len(checks),
        "checks": checks,
        "reconstructed_outcome": judgment["outcome"],
        "reconstructed_qualifying_device_count": sum(qualifying.values()),
        "scope_note": (
            "This validator reconstructs source bindings, the frozen rubric decision, counts, and access seals "
            "from the recorded native-visual judgment; it does not claim an independent machine reinspection."
        ),
        "claim_ceiling": result["claim_ceiling"],
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# F69VSD001 result validation\n\n"
        "Status: **PASS_10_CHECK_SOURCE_AND_DECISION_RECONSTRUCTION**\n\n"
        "The validator binds the exact method, selection, prior validation, official full and 2000-pixel image "
        "hashes, all five negative device fields, zero text/formal access, canonical result, and the frozen `NONE` "
        "decision. It reconstructs provenance and logic from the recorded native-visual judgment; it does not "
        "pretend to perform an independent visual reinspection.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
