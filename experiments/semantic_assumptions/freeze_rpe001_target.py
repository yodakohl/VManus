#!/usr/bin/env python3
"""Create the one-shot RPE001 target freeze after code publication."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


BASE = Path(__file__).resolve().parent
ROOT = BASE.parent.parent
OUT = BASE / "RPE001_TARGET_FREEZE.json"
FROZEN = (
    "experiments/semantic_assumptions/RADIAL_ENDPOINT_POLARITY_METHOD.md",
    "experiments/semantic_assumptions/audit_radial_endpoint_polarity_capacity.py",
    "experiments/semantic_assumptions/results/radial_endpoint_polarity_capacity.json",
    "experiments/semantic_assumptions/results/radial_endpoint_polarity_capacity.md",
    "experiments/semantic_assumptions/rpe001_core.py",
    "experiments/semantic_assumptions/run_rpe001_controls.py",
    "experiments/semantic_assumptions/results/rpe001_controls.json",
    "experiments/semantic_assumptions/results/rpe001_controls.md",
    "experiments/semantic_assumptions/validate_rpe001_controls.py",
    "experiments/semantic_assumptions/results/rpe001_controls_validation.json",
    "experiments/semantic_assumptions/results/rpe001_controls_validation.md",
    "experiments/semantic_assumptions/run_rpe001_target.py",
    "experiments/semantic_assumptions/validate_rpe001_target.py",
    "experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv",
    "experiments/semantic_assumptions/results/source_sta_family_consensus_validation.json",
    "experiments/semantic_assumptions/results/source_separator_transcription.tsv",
)
TARGETS = (
    "experiments/semantic_assumptions/results/rpe001_target.json",
    "experiments/semantic_assumptions/results/rpe001_target.md",
    "experiments/semantic_assumptions/results/rpe001_target_validation.json",
    "experiments/semantic_assumptions/results/rpe001_target_validation.md",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists():
        raise SystemExit("refusing overwrite")
    if subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT).strip():
        raise SystemExit("working tree must be clean")
    if any((ROOT / name).exists() for name in TARGETS):
        raise SystemExit("target artifacts must be absent")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    payload = {
        "experiment": "RPE001_TARGET_FREEZE",
        "status": "FROZEN_TARGET_AND_VALIDATION_ABSENT",
        "code_commit": commit,
        "frozen_files": {name: sha(ROOT / name) for name in FROZEN},
        "target_outputs": list(TARGETS),
        "target_outputs_absent": {name: not (ROOT / name).exists() for name in TARGETS},
        "authorized_runs": {"target": 1, "independent_validation": 1},
        "claim_ceiling": "Hash freeze only; no manuscript endpoint score, word, meaning, plaintext, or translation is present.",
    }
    if not all(payload["target_outputs_absent"].values()):
        raise AssertionError("target presence")
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "commit": commit, "files": len(FROZEN)}, sort_keys=True))


if __name__ == "__main__":
    main()
