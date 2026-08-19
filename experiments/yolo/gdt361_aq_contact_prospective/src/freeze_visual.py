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

BASE = ROOT / "experiments/yolo/gdt361_aq_contact_prospective"
FREEZE = BASE / "artifacts/gdt361_freeze.json"
SELECTION = BASE / "artifacts/gdt361_selection.tsv"
LOC = BASE / "artifacts/gdt361_localizations.tsv"
OBS = BASE / "artifacts/gdt361_visual_observations.tsv"
OUT = BASE / "artifacts/gdt361_visual_freeze.json"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    frozen = json.loads(FREEZE.read_text())
    sel, loc, obs = read_tsv(SELECTION), read_tsv(LOC), read_tsv(OBS)
    ids = [r["target_id"] for r in sel]
    assert [r["target_id"] for r in loc] == ids == [r["target_id"] for r in obs]
    assert all(r["canvas_id"] == "1006252" for r in loc)
    assert all(r["provenance"] == "AI_DIRECT_VISUAL_OBSERVATION" for r in obs)
    states = Counter(r["visual_state"] for r in obs)
    scored = [r for r in obs if r["prospective_score_eligible"] == "1"]
    scored_states = Counter(r["visual_state"] for r in scored)
    assert states == Counter({"CONTACT": 4, "CLEAR_GAP": 2, "UNCERTAIN": 1})
    assert scored_states == Counter({"CONTACT": 3, "CLEAR_GAP": 2, "UNCERTAIN": 1})
    payload = {
        "schema": "GDT361_VISUAL_FREEZE_V1",
        "status": "VISUAL_CALLS_FROZEN_BEFORE_SIX_ROW_FORMAL_REVEAL",
        "census": {
            "state": "EXACT_LOCUS_SET_EXHAUSTS_VISIBLE_SOURCE_DESCRIBED_ROW",
            "confidence": "MEDIUM",
            "visible_inscription_groups": 7,
            "frozen_loci": 7,
            "note": "Seven source-mapped groups are localized in row order; the seventh is degraded at the crease.",
        },
        "counts_all_seven": dict(sorted(states.items())),
        "counts_six_prospective": dict(sorted(scored_states.items())),
        "observer": {
            "type": "SINGLE_AI_DIRECT_VISUAL_OBSERVER",
            "independent_second_reviewer": False,
            "source_surfaces_displayed_before_calls": True,
            "target_formal_families_11_to_16_displayed_before_calls": False,
            "ocr_or_automated_vision_used": False,
        },
        "inputs": {
            str(FREEZE.relative_to(ROOT)): sha256_file(FREEZE),
            str(SELECTION.relative_to(ROOT)): sha256_file(SELECTION),
            str(LOC.relative_to(ROOT)): sha256_file(LOC),
            str(OBS.relative_to(ROOT)): sha256_file(OBS),
            "experiments/yolo/gdt361_aq_contact_prospective/src/freeze_visual.py": sha256_file(Path(__file__)),
        },
        "prediction_unchanged": frozen["prediction"],
        "access": {"f84_accessed": False, "formal_reveal_authorized_after_this_freeze": True},
        "claim_ceiling": frozen["claim_ceiling"],
    }
    OUT.write_bytes(canonical_json_bytes(payload))


if __name__ == "__main__":
    main()
