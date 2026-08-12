#!/usr/bin/env python3
"""Independent compact validation of the F69VSD001 source-only freeze."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
METHOD = BASE / "F69VSD001_AUTHOR_VISIBLE_START_DIRECTION_METHOD.md"
PRIOR = BASE / "results/special_circle_plain_legend_native_visual_screen.json"
RESULT = BASE / "results/f69vsd001_start_direction_selection.json"
OUT = BASE / "results/f69vsd001_start_direction_selection_validation.json"

EXPECTED_METHOD = "677c1468618781dcc6416015b2f917f8accd62cecc2d53b7dae309c9bd0d892b"
EXPECTED_IMAGE = "99d824d8d5491a2f4511a0c0f719f9f165063335f53540c63d12b3bbe6c73edf"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists():
        raise SystemExit("refusing overwrite")
    prior = json.loads(PRIOR.read_text())
    result = json.loads(RESULT.read_text())
    checks = {
        "method_hash": sha(METHOD) == EXPECTED_METHOD == result["method_sha256"],
        "canonical_result": RESULT.read_bytes() == (json.dumps(result, indent=2, sort_keys=True) + "\n").encode(),
        "exact_canvas_mapping": prior["canvas_panels"]["1006199"] == ["f69v", "f70r1", "f70r2"],
        "exact_image_hash": prior["inputs"]["yale_iiif_2000px_canvas_1006199_sha256"] == EXPECTED_IMAGE,
        "selected_panel_only_f69v": result["source"]["selected_panel"] == "f69v",
        "rubric_frozen_image_unopened": result["gates"]["rubric_frozen_before_image_reopen"] and not result["gates"]["image_body_opened_by_builder"],
        "zero_text_access": not result["gates"]["voynich_text_or_formal_features_opened"],
    }
    if not all(checks.values()):
        raise SystemExit("validation failed")
    validation = {
        "experiment": "F69VSD001_SELECTION_VALIDATION",
        "status": "PASS_7_CHECK_SOURCE_ONLY_RECONSTRUCTION",
        "source_result_sha256": sha(RESULT),
        "check_count": len(checks),
        "checks": checks,
        "image_body_opened": False,
        "voynich_text_opened": False,
        "claim_ceiling": result["claim_ceiling"],
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
