#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions/results"
PANEL = BASE / "lm001y_final_residual_leaf_margin_census_selection.tsv"
OBS = BASE / "lm001y_final_residual_leaf_margin_census_result.tsv"
OLD = BASE / "lm001_leaf_margin_visual_held.tsv"
OLD_X = BASE / "lm001x_currier_a_leaf_margin_extension_result.tsv"
RESULT = BASE / "lm001y_final_residual_leaf_margin_census_result.json"
REPORT = BASE / "lm001y_final_residual_leaf_margin_census_result_report.md"
OUT = BASE / "lm001y_final_residual_leaf_margin_census_result_validation.json"


def main() -> None:
    checks = []
    panel = {row["opaque_id"]: row for row in csv.DictReader(PANEL.open(encoding="utf-8"), delimiter="\t")}
    rows = list(csv.DictReader(OBS.open(encoding="utf-8"), delimiter="\t"))
    assert len(rows) == 9 and {row["opaque_id"] for row in rows} == set(panel)
    checks.append("exact_frozen_complete_residual_panel")
    assert all(row["currier"] == "A" and row["quire"] == panel[row["opaque_id"]]["quire"] and row["canvas_id"] == panel[row["opaque_id"]]["canvas_id"] for row in rows)
    checks.append("metadata_bindings")
    for row in rows:
        request = urllib.request.Request(panel[row["opaque_id"]]["review_image_url"], headers={"User-Agent": "VManus-LM001Y-validator/1.0"})
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read()
        assert hashlib.sha256(raw).hexdigest() == row["review_image_sha256"]
    checks.append("live_official_review_image_hashes")
    counts = Counter(row["leaf_margin_state"] for row in rows)
    assert counts == {"SMOOTH": 5, "TOOTHED": 3, "UNCERTAIN": 1}
    checks.append("extension_counts")
    combined = list(csv.DictReader(OLD.open(encoding="utf-8"), delimiter="\t"))
    combined += list(csv.DictReader(OLD_X.open(encoding="utf-8"), delimiter="\t")) + rows
    cc = Counter(row["leaf_margin_state"] for row in combined)
    assert cc == {"SMOOTH": 29, "TOOTHED": 13, "UNCERTAIN": 2}
    assert Counter(row["currier"] for row in combined if row["leaf_margin_state"] == "TOOTHED") == {"A": 9, "B": 4}
    checks.append("combined_state_and_currier_counts")
    by_quire = {state: Counter(row["quire"] for row in combined if row["leaf_margin_state"] == state) for state in ("SMOOTH", "TOOTHED")}
    by_quartile = {state: Counter(row["folio_rank_quartile"] for row in combined if row["leaf_margin_state"] == state) for state in ("SMOOTH", "TOOTHED")}
    by_currier = {state: Counter(row["currier"] for row in combined if row["leaf_margin_state"] == state) for state in ("SMOOTH", "TOOTHED")}
    gates = {
        "at_least_six_each_admitted_state": all(cc[state] >= 6 for state in ("SMOOTH", "TOOTHED")),
        "both_states_at_least_three_in_each_currier": all(by_currier[state][currier] >= 3 for state in ("SMOOTH", "TOOTHED") for currier in ("A", "B")),
        "both_states_in_at_least_three_quartiles": all(len(by_quartile[state]) >= 3 for state in ("SMOOTH", "TOOTHED")),
        "uncertain_no_more_than_four": cc["UNCERTAIN"] <= 4,
        "max_quire_share_no_more_than_point25": all(max(by_quire[state].values()) / cc[state] <= 0.25 for state in ("SMOOTH", "TOOTHED")),
    }
    assert all(gates.values()) and max(by_quire["TOOTHED"].values()) / cc["TOOTHED"] == 3 / 13
    checks.append("all_original_visual_capacity_gates")
    stored = json.loads(RESULT.read_text(encoding="utf-8"))
    assert stored["status"] == "PASS_COMBINED_VISUAL_CAPACITY_ALL_ORIGINAL_GATES"
    assert stored["decision"] == "AUTHORIZE_SEPARATE_TEXT_BLIND_PREREGISTRATION_ONLY"
    assert stored["gates"] == gates and stored["failed_gates"] == []
    assert stored["observations_sha256"] == hashlib.sha256(OBS.read_bytes()).hexdigest()
    checks.append("canonical_pass_decision_and_result_binding")
    assert stored["access"]["voynich_text_features_accessed"] is False
    assert stored["access"]["extension_images_judged_once"] is True
    assert "No Voynich text was opened" in REPORT.read_text(encoding="utf-8")
    checks.append("sealed_text_access_boundary")
    out = {
        "experiment": "LM001Y_FINAL_RESIDUAL_LEAF_MARGIN_CENSUS_RESULT_VALIDATION",
        "status": "PASS_8_CHECK_SOURCE_AND_ALL_GATE_RECONSTRUCTION",
        "check_count": len(checks),
        "checks": checks,
        "validated_result_sha256": hashlib.sha256(RESULT.read_bytes()).hexdigest(),
        "validated_report_sha256": hashlib.sha256(REPORT.read_bytes()).hexdigest(),
        "visual_judgments_reclassified_by_validator": False,
        "claim_ceiling": stored["claim_ceiling"],
    }
    OUT.write_text(json.dumps(out, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
