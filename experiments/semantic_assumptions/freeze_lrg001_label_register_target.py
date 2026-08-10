#!/usr/bin/env python3
"""Create the exact LRG001 one-shot target freeze after code publication."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FREEZE = HERE / "LRG001_TARGET_FREEZE.json"
FILES = [
    "experiments/semantic_assumptions/LRG001_SOURCE_NATIVE_LABEL_REGISTER_CAPACITY_SPEC.md",
    "experiments/semantic_assumptions/build_lrg001_label_register_capacity.py",
    "experiments/semantic_assumptions/validate_lrg001_label_register_capacity.py",
    "experiments/semantic_assumptions/results/lrg001_label_register_capacity.tsv",
    "experiments/semantic_assumptions/results/lrg001_label_register_capacity.json",
    "experiments/semantic_assumptions/results/lrg001_label_register_capacity_validation.json",
    "experiments/semantic_assumptions/LRG001_TARGET_BLIND_CALIBRATION_SPEC.md",
    "experiments/semantic_assumptions/lrg001_core.py",
    "experiments/semantic_assumptions/run_lrg001_target_blind_calibration.py",
    "experiments/semantic_assumptions/validate_lrg001_target_blind_calibration_v2.py",
    "experiments/semantic_assumptions/results/lrg001_target_blind_calibration_v2.json",
    "experiments/semantic_assumptions/results/lrg001_target_blind_calibration_v2_validation.json",
    "experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv",
    "experiments/semantic_assumptions/results/source_sta_family_consensus.json",
    "experiments/semantic_assumptions/results/source_sta_family_consensus_validation.json",
    "experiments/semantic_assumptions/LRG001_LABEL_REGISTER_TARGET_METHOD.md",
    "experiments/semantic_assumptions/run_lrg001_label_register_target.py",
    "experiments/semantic_assumptions/validate_lrg001_label_register_target.py",
    "experiments/semantic_assumptions/freeze_lrg001_label_register_target.py",
]
RESULTS = [
    "experiments/semantic_assumptions/results/lrg001_label_register_target.json",
    "experiments/semantic_assumptions/results/lrg001_label_register_target_report.md",
    "experiments/semantic_assumptions/results/lrg001_label_register_target_validation.json",
    "experiments/semantic_assumptions/results/lrg001_label_register_target_validation_report.md",
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if FREEZE.exists() or any((ROOT / value).exists() for value in RESULTS):
        raise RuntimeError("freeze or target artifact exists")
    if subprocess.run(["git", "diff", "--quiet"], cwd=ROOT).returncode != 0 or subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT).returncode != 0:
        raise RuntimeError("working tree must be clean")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    frozen = {value: digest(ROOT / value) for value in FILES}
    value = {
        "status": "FROZEN_LRG001_SINGLE_TARGET",
        "code_commit": commit,
        "frozen_files": frozen,
        "result_paths": RESULTS,
        "result_paths_absent": True,
        "claim_ceiling": "One target run may establish only a transferable label-associated structural profile, not an identifier, name, noun, word meaning, language, plaintext, or translation.",
    }
    temporary = FREEZE.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    temporary.replace(FREEZE)
    print(json.dumps(value, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
