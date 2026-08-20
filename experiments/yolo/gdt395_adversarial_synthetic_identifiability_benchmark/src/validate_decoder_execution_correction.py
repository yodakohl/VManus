#!/usr/bin/env python3
"""Validate the frozen GDT395 V1-to-V2 execution correction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark"
CORRECTION = EXP / "artifacts/gdt395_decoder_execution_correction.json"
OUT = EXP / "artifacts/gdt395_decoder_execution_correction_validation.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    data = json.loads(CORRECTION.read_text())
    checks = {
        "status": data["status"] == "V2_FROZEN_AFTER_ZERO_CLAIM_V1_FAILURE",
        "bindings": all(sha(EXP / rel) == digest for rel, digest in data["bindings"].items()),
        "zero_claim_failure": data["failed_attempt_claim_files_written"] == 0,
        "failure_disclosed": data["failed_attempt_loaded_blind_observations"] and data["failed_attempt_decoder_functions_started"],
        "path_only": data["scientific_change"] == "NONE_PATH_ASSEMBLY_ONLY",
        "seal": not data["oracle_opened"] and data["oracle_rows_read"] == data["voynich_rows"] == 0 and not any(data["f84"].values()),
    }
    tmp = dict(data); expected = tmp.pop("content_sha256")
    checks["content_hash"] = hashlib.sha256(json.dumps(tmp, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == expected
    result = {
        "schema": "GDT395_DECODER_EXECUTION_CORRECTION_VALIDATION_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks, "checks_passed": sum(checks.values()), "checks_total": len(checks),
        "correction_sha256": sha(CORRECTION),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "checks": f"{result['checks_passed']}/{result['checks_total']}"}, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
