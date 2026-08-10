#!/usr/bin/env python3
"""Create the public target freeze for ZLA001 after control validation."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import zla001_core as core


BASE = Path(__file__).resolve().parent
ROOT = BASE.parent.parent
R = BASE / "results"
OUT = ROOT / "ZLA001_TARGET_FREEZE.json"
TARGETS = (
    R / "zla001_target.json", R / "zla001_target.md",
    R / "zla001_target_validation.json", R / "zla001_target_validation.md",
)
FILES = (
    ROOT / "ZODIAC_LABEL_ADJACENCY_METHOD.md",
    R / "zodiac_label_cycle_capacity.tsv",
    R / "zodiac_label_cycle_capacity.json",
    R / "zodiac_label_cycle_capacity_validation.json",
    R / "source_sta_group_alignment.tsv",
    R / "source_sta_group_alignment.json",
    R / "source_sta_group_alignment_validation.json",
    BASE / "zla001_core.py",
    BASE / "run_zla001_controls.py",
    BASE / "validate_zla001_controls.py",
    R / "zla001_controls_attempt1.json",
    R / "zla001_controls_attempt1.md",
    R / "zla001_controls.json",
    R / "zla001_controls.md",
    R / "zla001_controls_validation.json",
    R / "zla001_controls_validation.md",
    BASE / "run_zla001_target.py",
    BASE / "validate_zla001_target.py",
    Path(__file__),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists():
        raise SystemExit("refusing overwrite")
    if any(path.exists() for path in TARGETS):
        raise AssertionError("target artifact exists")
    controls = json.loads((R / "zla001_controls.json").read_text())
    validation = json.loads((R / "zla001_controls_validation.json").read_text())
    if controls.get("status") != "PASS" or not all(controls["gates"].values()):
        raise AssertionError("controls not passed")
    if validation.get("status") != "PASS":
        raise AssertionError("control validation not passed")
    if any(not path.is_file() for path in FILES):
        raise AssertionError("frozen input absent")
    geometry = core.load_geometry(R / "zodiac_label_cycle_capacity.tsv")
    assignments, orbit = core.assignment_matrix(geometry)
    if orbit["sha256"] != controls["orbit"]["sha256"]:
        raise AssertionError("orbit drift")
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    result = {
        "experiment": "ZLA001_TARGET_FREEZE",
        "status": "FROZEN_TARGET_AND_VALIDATION_ABSENT",
        "source_commit": commit,
        "files": {str(path.relative_to(ROOT)): sha(path) for path in FILES},
        "orbit": orbit,
        "target_absence": {str(path.relative_to(ROOT)): True for path in TARGETS},
        "controls": {"status": controls["status"], "validation_status": validation["status"], "pass_counts": controls["pass_counts"]},
        "claim_ceiling": "One aggregate ZLA001 target and one production-free reconstruction only; no ownership, serial code, number, degree, word, meaning, plaintext, or translation.",
    }
    OUT.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "source_commit": commit, "files": len(FILES), "orbit_sha256": orbit["sha256"]}, sort_keys=True))


if __name__ == "__main__":
    main()
