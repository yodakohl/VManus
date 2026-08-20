#!/usr/bin/env python3
"""Freeze the V2 path-only runner correction after V1 wrote zero claims."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark"
OUT = EXP / "artifacts/gdt395_decoder_execution_correction.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists():
        raise RuntimeError("refusing to overwrite execution correction")
    claim_root = EXP / ".work/claims"
    claim_files = sum(path.is_file() for path in claim_root.rglob("*")) if claim_root.exists() else 0
    if claim_files:
        raise RuntimeError("V1 produced claim files; plumbing-only correction is not admissible")
    bindings = {}
    for rel in (
        "artifacts/gdt395_decoder_panel_freeze.json",
        "artifacts/gdt395_decoder_panel_validation.json",
        "src/run_blind_decoders.py",
        "src/run_blind_decoders_v2.py",
        "src/freeze_decoder_execution_correction.py",
        "src/validate_decoder_execution_correction.py",
    ):
        bindings[rel] = sha(EXP / rel)
    data = {
        "schema": "GDT395_DECODER_EXECUTION_CORRECTION_V1",
        "status": "V2_FROZEN_AFTER_ZERO_CLAIM_V1_FAILURE",
        "failure": "V1 pathlib expression attempted string / string at claim output path assembly",
        "failed_attempt_loaded_blind_observations": True,
        "failed_attempt_decoder_functions_started": True,
        "failed_attempt_claim_files_written": claim_files,
        "scientific_change": "NONE_PATH_ASSEMBLY_ONLY",
        "bindings": bindings,
        "oracle_opened": False,
        "oracle_rows_read": 0,
        "voynich_rows": 0,
        "f84": {"opened": False, "parsed": False, "retained": False, "scored": False},
    }
    raw = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
    data["content_sha256"] = hashlib.sha256(raw).hexdigest()
    OUT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": data["status"], "claim_files": claim_files}, sort_keys=True))


if __name__ == "__main__":
    main()
