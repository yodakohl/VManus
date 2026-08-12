#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "experiments/semantic_assumptions/results/lm001_herbal_leaf_margin_visual_selection.tsv"
OBS = ROOT / "experiments/semantic_assumptions/results/lm001_leaf_margin_visual_held.tsv"
RESULT = ROOT / "experiments/semantic_assumptions/results/lm001_leaf_margin_visual_held.json"
OUT = ROOT / "experiments/semantic_assumptions/results/lm001_leaf_margin_visual_held_validation.json"


def main() -> None:
    checks = []
    panel = {
        row["opaque_id"]: row
        for row in csv.DictReader(PANEL.open(encoding="utf-8"), delimiter="\t")
        if row["phase"] == "HELD"
    }
    rows = list(csv.DictReader(OBS.open(encoding="utf-8"), delimiter="\t"))
    assert len(rows) == 16 and {row["opaque_id"] for row in rows} == set(panel)
    checks.append("exact_frozen_held_panel")
    assert all(
        row["currier"] == panel[row["opaque_id"]]["currier"]
        and row["quire"] == panel[row["opaque_id"]]["quire"]
        and row["canvas_id"] == panel[row["opaque_id"]]["canvas_id"]
        for row in rows
    )
    checks.append("metadata_bindings")
    for row in rows:
        request = urllib.request.Request(
            panel[row["opaque_id"]]["review_image_url"],
            headers={"User-Agent": "VManus-LM001-held-validator/1.0"},
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read()
        assert hashlib.sha256(raw).hexdigest() == row["review_image_sha256"]
    checks.append("live_official_review_image_hashes")
    counts = Counter(row["leaf_margin_state"] for row in rows)
    assert counts == {"SMOOTH": 10, "TOOTHED": 5, "UNCERTAIN": 1}
    checks.append("stored_judgment_counts")
    toothed_currier = Counter(row["currier"] for row in rows if row["leaf_margin_state"] == "TOOTHED")
    toothed_quire = Counter(row["quire"] for row in rows if row["leaf_margin_state"] == "TOOTHED")
    assert toothed_currier == {"B": 4, "A": 1} and toothed_quire["q05"] == 3
    checks.append("failed_balance_and_concentration_reconstruction")
    stored = json.loads(RESULT.read_text(encoding="utf-8"))
    assert stored["status"] == "STOP_HELD_VISUAL_CAPACITY_FAILED"
    assert stored["observations_sha256"] == hashlib.sha256(OBS.read_bytes()).hexdigest()
    assert stored["failed_gates"] == [
        "at_least_six_each_admitted_state",
        "both_states_at_least_three_in_each_currier",
        "max_quire_share_no_more_than_point25",
    ]
    checks.append("canonical_stop_and_gate_list")
    assert stored["access"] == {
        "held_images_judged_once": True,
        "machine_authored_source_bound_native_inspection": True,
        "ocr_clip_embedding_or_automated_vision_used": False,
        "voynich_text_features_accessed": False,
    }
    checks.append("access_boundary")
    validation = {
        "experiment": "LM001_LEAF_MARGIN_VISUAL_HELD_CAPACITY_VALIDATION",
        "status": "PASS_7_CHECK_SOURCE_AND_CAPACITY_RECONSTRUCTION",
        "check_count": len(checks),
        "checks": checks,
        "validated_result_sha256": hashlib.sha256(RESULT.read_bytes()).hexdigest(),
        "visual_judgments_reclassified_by_validator": False,
        "claim_ceiling": stored["claim_ceiling"],
    }
    OUT.write_text(
        json.dumps(validation, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
