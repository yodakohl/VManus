#!/usr/bin/env python3
"""Validate ZST002 bindings, complete judgments, and stop arithmetic."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
RES = BASE / "results"
METHOD = BASE / "ZST002_F70V2_COMPLETE_STAR_TAIL_CENSUS_METHOD.md"
SELECTION = RES / "zst002_f70v2_complete_star_tail_census_selection.json"
SELECTION_VALIDATION = RES / "zst002_f70v2_complete_star_tail_census_selection_validation.json"
PRODUCER = BASE / "audit_zst002_f70v2_complete_star_tail_census_result.py"
PROJECTION = RES / "zst002_f70v2_complete_star_tail_census_projection.tsv"
RESULT = RES / "zst002_f70v2_complete_star_tail_census_result.json"
REPORT = RES / "zst002_f70v2_complete_star_tail_census_result_report.md"
OUT = RES / "zst002_f70v2_complete_star_tail_census_result_validation.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists():
        raise SystemExit("refusing overwrite")
    selection = json.loads(SELECTION.read_text())
    result = json.loads(RESULT.read_text())
    with PROJECTION.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    strict = [row for row in rows if row["strict_eligible"] == "1"]
    strict_by_ring = {ring: dict(sorted(Counter(r["tail_state"] for r in strict if r["ring"] == ring).items())) for ring in ("OUTER", "INNER")}
    expected_ids = [row["source_record_id"] for row in selection["rows"]]
    checks = {
        "canonical_result": RESULT.read_bytes() == (json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n").encode(),
        "projection_exactly_covers_frozen_order": len(rows) == 29 and [row["source_record_id"] for row in rows] == expected_ids,
        "all_29_recorded_no_tail": Counter(row["tail_state"] for row in rows) == {"NO_TAIL": 29},
        "exact_strict_mask_carried_forward": [row["strict_eligible"] == "1" for row in rows] == [row["strict_eligible"] for row in selection["rows"]],
        "strict_25_all_no_tail_by_ring": len(strict) == 25 and strict_by_ring == {"OUTER": {"NO_TAIL": 16}, "INNER": {"NO_TAIL": 9}},
        "zero_mixed_ring_and_failed_target_gates": result["counts"]["mixed_strict_rings"] == [] and result["gates"]["at_least_one_mixed_strict_ring"] is False and result["gates"]["at_least_two_strict_tail_and_two_strict_no_tail_across_mixed_rings"] is False,
        "exact_full_image_binding": result["image_binding"]["canvas_id"] == "1006200" and result["image_binding"]["full_image_sha256"] == "062ff6a9f14d0c16eb12dc8f6dc480771b7c19746ebdb20302b998e66181ccea",
        "all_inputs_bound": result["inputs"] == {str(p.relative_to(ROOT)): sha(p) for p in (METHOD, SELECTION, SELECTION_VALIDATION, PROJECTION)},
        "access_and_provenance_explicit": result["access"]["official_source_native_pixels_used"] is True and result["access"]["label_text_used_in_grade"] is False and result["access"]["preflight_console_incidentally_displayed_machine_readable_source_transcriptions_before_selection_publication"] is True,
        "formal_target_remained_closed": result["counts"]["formal_features_constructed"] == result["counts"]["formal_associations_scored"] == 0 and result["access"]["formal_family_member_root_parser_role_or_association_opened"] is False,
        "stop_and_ceiling": result["status"] == "STOP_ZERO_TAIL_IN_COMPLETE_F70V2_PANEL" and "translation" in result["claim_ceiling"],
        "report_present": REPORT.is_file() and "29 NO_TAIL" in REPORT.read_text(),
    }
    if not all(checks.values()):
        raise SystemExit({key: value for key, value in checks.items() if not value})
    output = {
        "experiment": "ZST002_F70V2_COMPLETE_STAR_TAIL_CENSUS_RESULT_VALIDATION",
        "schema": "ZST002_RESULT_VALIDATION_V1",
        "status": "PASS_12_CHECK_BINDING_AND_STOP_RECONSTRUCTION",
        "check_count": len(checks), "checks": list(checks),
        "producer_sha256": sha(PRODUCER), "validated_result_sha256": sha(RESULT),
        "reconstructed": {"graded": 29, "states": {"NO_TAIL": 29}, "strict": 25, "strict_by_ring": strict_by_ring, "mixed_rings": []},
        "claim_ceiling": "Validation reconstructs the recorded native-visual judgments and stop arithmetic rather than claiming a second image inspection. It supplies no word meaning plaintext or translation.",
    }
    OUT.write_text(json.dumps(output, sort_keys=True, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
