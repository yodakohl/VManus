#!/usr/bin/env python3
"""Freeze the one-time clean LRG001 target recovery."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "LRG001_RECOVERY_FREEZE.json"
FILES = [
    "experiments/semantic_assumptions/LRG001_TARGET_FREEZE.json",
    "experiments/semantic_assumptions/LRG001_OFFICIAL_ALPHABET_RECOVERY_SPEC.md",
    "experiments/semantic_assumptions/reconcile_lrg001_official_alphabet.py",
    "experiments/semantic_assumptions/results/lrg001_official_alphabet_reconciliation.json",
    "experiments/semantic_assumptions/results/lrg001_target_blind_calibration_v2.json",
    "experiments/semantic_assumptions/validate_lrg001_target_blind_calibration_v2.py",
    "experiments/semantic_assumptions/lrg001_core.py",
    "experiments/semantic_assumptions/results/lrg001_label_register_capacity.tsv",
    "experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv",
    "experiments/semantic_assumptions/recover_lrg001_label_register_target.py",
    "experiments/semantic_assumptions/validate_lrg001_label_register_target_recovered.py",
    "experiments/semantic_assumptions/freeze_lrg001_recovery.py",
]
RESULTS = [
    "experiments/semantic_assumptions/results/lrg001_label_register_target_recovered.json",
    "experiments/semantic_assumptions/results/lrg001_label_register_target_recovered_report.md",
    "experiments/semantic_assumptions/results/lrg001_label_register_target_recovered_validation.json",
    "experiments/semantic_assumptions/results/lrg001_label_register_target_recovered_validation_report.md",
]
ORIGINAL_RESULTS = [
    "experiments/semantic_assumptions/results/lrg001_label_register_target.json",
    "experiments/semantic_assumptions/results/lrg001_label_register_target_report.md",
    "experiments/semantic_assumptions/results/lrg001_label_register_target_validation.json",
    "experiments/semantic_assumptions/results/lrg001_label_register_target_validation_report.md",
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists() or any((ROOT / path).exists() for path in RESULTS):
        raise RuntimeError("recovery artifact exists")
    if any((ROOT / path).exists() for path in ORIGINAL_RESULTS):
        raise RuntimeError("original target artifact exists")
    if subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True):
        raise RuntimeError("working tree dirty")
    reconciliation = json.loads(
        (ROOT / "experiments/semantic_assumptions/results/lrg001_official_alphabet_reconciliation.json").read_text(encoding="utf-8")
    )
    if reconciliation["status"] != "PASS_EXACT_OFFICIAL_ALPHABET_SYNTHETIC_INVARIANCE" or reconciliation["discrepancies"] != 0:
        raise RuntimeError("reconciliation did not pass")
    value = {
        "status": "FROZEN_LRG001_CLEAN_RECOVERY",
        "code_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "frozen_files": {path: digest(ROOT / path) for path in FILES},
        "result_paths": RESULTS, "result_paths_absent": True,
        "original_result_paths": ORIGINAL_RESULTS, "original_result_paths_absent": True,
        "claim_ceiling": "Recovered clean score may establish only a label-associated structural profile, never an identifier, name, noun, meaning, plaintext, or translation.",
    }
    temporary = OUT.with_suffix(".json.tmp"); temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"); temporary.replace(OUT)
    print(json.dumps(value, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
