#!/usr/bin/env python3
"""Validate the compact S104 recovery stop without importing its producer."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
RESULT = BASE / "results/s104_visual_panel_recovery_check.json"
OUT = BASE / "results/s104_visual_panel_recovery_check_validation.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists():
        raise SystemExit("refusing overwrite")
    result = json.loads(RESULT.read_text())
    paths = result["registered_paths"]
    current = [rel for rel in paths if (BASE / rel).exists()]
    history = subprocess.run(
        ["git", "log", "--all", "--name-only", "--pretty=format:"], cwd=ROOT,
        check=True, capture_output=True, text=True,
    ).stdout.splitlines()
    historical = sorted({line for line in history if line in paths})
    archive = ROOT / "archive_pre_reset_2026-08-06"
    archive_hits = sorted(
        str(path.relative_to(ROOT)) for path in archive.rglob("*")
        if path.is_file() and any(path.name == Path(rel).name for rel in paths)
    )
    checks = {
        "canonical_result": RESULT.read_bytes() == (json.dumps(result, indent=2, sort_keys=True) + "\n").encode(),
        "four_registered_paths": len(paths) == 4 and len(set(paths)) == 4,
        "zero_current_paths": current == result["present_registered_paths"] == [],
        "zero_reachable_history_paths": historical == result["reachable_git_history_paths"] == [],
        "zero_retained_archive_paths": archive_hits == result["retained_archive_paths"] == [],
        "decision_exact": result["status"] == result["decision"] == "STOP_UNRECOVERABLE_REGISTERED_PANEL_ARTIFACTS",
        "no_image_or_text_access": not result["gates"]["image_or_voynich_text_opened"],
    }
    if not all(checks.values()):
        raise SystemExit("validation failed")
    validation = {
        "experiment": "S104_NATIVE_VISUAL_PANEL_RECOVERY_VALIDATION",
        "status": "PASS_7_CHECK_PROVENANCE_STOP_RECONSTRUCTION",
        "source_result_sha256": sha(RESULT),
        "check_count": len(checks),
        "checks": checks,
        "claim_ceiling": result["claim_ceiling"],
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
