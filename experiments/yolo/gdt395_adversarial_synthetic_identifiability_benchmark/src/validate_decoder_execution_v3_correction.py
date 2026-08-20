#!/usr/bin/env python3
"""Validate the frozen GDT395 V3 execution correction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark"
CORRECTION = EXP / "artifacts/gdt395_decoder_execution_v3_correction.json"
OUT = EXP / "artifacts/gdt395_decoder_execution_v3_correction_validation.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    data = json.loads(CORRECTION.read_text())
    checks = {
        "status": data["status"] == "V3_FROZEN_AFTER_UNFROZEN_PARTIAL_V2_RUN",
        "bindings": all(sha(EXP / rel) == digest for rel, digest in data["bindings"].items()),
        "partial_disclosed": data["v2_partial_claim_files_present"] > 0 and not data["v2_complete_claim_manifest_present"],
        "two_changes": len(data["v3_changes"]) == 2,
        "equivalence": data["cache_equivalence"] == "PASS_35_OF_35_FABRICATED_ONLY",
        "conformance_only": data["scientific_change"] == "NONE_EXECUTION_AND_SCHEMA_CONFORMANCE_ONLY",
        "seal": not data["oracle_opened"] and data["oracle_rows_read"] == data["voynich_rows"] == 0 and not any(data["f84"].values()),
    }
    tmp = dict(data); expected = tmp.pop("content_sha256")
    checks["content_hash"] = hashlib.sha256(json.dumps(tmp, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == expected
    result = {
        "schema": "GDT395_DECODER_EXECUTION_V3_CORRECTION_VALIDATION_V1",
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
