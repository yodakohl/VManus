#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import canonical_json_bytes, sha256_file  # noqa: E402

BASE = ROOT / "experiments/yolo/gdt362_remaining_complete_array"
FREEZE = BASE / "artifacts/gdt362_freeze.json"
CORRECTION = BASE / "artifacts/gdt362_canvas_correction.json"
SELECTION = BASE / "artifacts/gdt362_selection.tsv"
LOC = BASE / "artifacts/gdt362_localizations.tsv"
OBS = BASE / "artifacts/gdt362_visual_observations.tsv"
OUT = BASE / "artifacts/gdt362_visual_freeze.json"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    frozen = json.loads(FREEZE.read_text())
    correction = json.loads(CORRECTION.read_text())
    sel, loc, obs = read_tsv(SELECTION), read_tsv(LOC), read_tsv(OBS)
    ids = [r["target_id"] for r in sel]
    assert len(ids) == 9
    assert [r["target_id"] for r in loc] == ids == [r["target_id"] for r in obs]
    assert all(r["provenance"] == "AI_DIRECT_VISUAL_OBSERVATION" for r in loc + obs)
    states = Counter(r["visual_state"] for r in obs)
    assert states == Counter({"CLEAR_GAP": 5, "CONTACT": 3, "UNCERTAIN": 1})
    payload = {
        "schema": "GDT362_VISUAL_FREEZE_V1",
        "status": "NINE_VISUAL_CALLS_FROZEN_BEFORE_ANY_TARGET_FORMAL_REVEAL",
        "census": {
            "state": "EXACT_LOCUS_SET_EXHAUSTS_SOURCE_DESCRIBED_NINE_LABEL_ROW",
            "confidence": "MEDIUM",
            "visible_inscription_groups": 9,
            "frozen_loci": 9,
            "fold_ambiguous_loci": ["f101v2.13"],
        },
        "counts": dict(sorted(states.items())),
        "observer": {
            "type": "SINGLE_AI_DIRECT_VISUAL_OBSERVER",
            "independent_second_reviewer": False,
            "source_descriptions_displayed_before_calls": True,
            "canvas_correction_published_before_second_canvas_pixel_display": True,
            "target_formal_values_displayed_before_calls": False,
            "ocr_or_automated_vision_used": False,
        },
        "inputs": {
            str(FREEZE.relative_to(ROOT)): sha256_file(FREEZE),
            str(CORRECTION.relative_to(ROOT)): sha256_file(CORRECTION),
            str(SELECTION.relative_to(ROOT)): sha256_file(SELECTION),
            str(LOC.relative_to(ROOT)): sha256_file(LOC),
            str(OBS.relative_to(ROOT)): sha256_file(OBS),
            "experiments/yolo/gdt362_remaining_complete_array/src/freeze_visual.py": sha256_file(Path(__file__)),
        },
        "prediction_unchanged": frozen["prediction"],
        "correction_status": correction["status"],
        "access": {"f84_accessed": False, "formal_reveal_authorized_after_this_freeze": True},
        "claim_ceiling": frozen["claim_ceiling"],
    }
    OUT.write_bytes(canonical_json_bytes(payload))


if __name__ == "__main__":
    main()
