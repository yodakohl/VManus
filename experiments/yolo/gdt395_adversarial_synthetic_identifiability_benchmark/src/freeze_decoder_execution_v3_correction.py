#!/usr/bin/env python3
"""Freeze V3 after an unfrozen partial V2 run and before a complete manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark"
OUT = EXP / "artifacts/gdt395_decoder_execution_v3_correction.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists():
        raise RuntimeError("refusing to overwrite V3 correction")
    claim_root = EXP / ".work/claims"
    partial_files = sum(path.is_file() for path in claim_root.rglob("*")) if claim_root.exists() else 0
    complete_manifest = claim_root / "blind_claim_manifest_all.tsv"
    if complete_manifest.exists():
        raise RuntimeError("complete V2 manifest exists; V3 correction is too late")
    equivalence = json.loads((EXP / "artifacts/gdt395_runner_cache_equivalence_validation.json").read_text())
    if equivalence["status"] != "PASS" or equivalence["checks_passed"] != equivalence["checks_total"]:
        raise RuntimeError("cache equivalence did not pass")
    bindings = {}
    for rel in (
        "artifacts/gdt395_decoder_panel_freeze.json",
        "artifacts/gdt395_decoder_execution_correction.json",
        "artifacts/gdt395_decoder_execution_correction_validation.json",
        "artifacts/gdt395_runner_cache_equivalence_validation.json",
        "src/run_blind_decoders.py", "src/run_blind_decoders_v2.py",
        "src/run_blind_decoders_v3.py", "src/validate_runner_cache_equivalence.py",
        "src/freeze_decoder_execution_v3_correction.py",
        "src/validate_decoder_execution_v3_correction.py",
    ):
        bindings[rel] = sha(EXP / rel)
    data = {
        "schema": "GDT395_DECODER_EXECUTION_V3_CORRECTION_V1",
        "status": "V3_FROZEN_AFTER_UNFROZEN_PARTIAL_V2_RUN",
        "v2_partial_claim_files_present": partial_files,
        "v2_complete_claim_manifest_present": False,
        "v2_failure": "D03 emitted schema-invalid UNRESOLVED confidence before V2 completion",
        "v3_changes": [
            "memoize pure train-only fitted objects for identical training-list object and representation",
            "map only schema-invalid UNRESOLVED confidence to numeric 0.0",
        ],
        "cache_equivalence": f"PASS_{equivalence['checks_passed']}_OF_{equivalence['checks_total']}_FABRICATED_ONLY",
        "scientific_change": "NONE_EXECUTION_AND_SCHEMA_CONFORMANCE_ONLY",
        "oracle_opened": False, "oracle_rows_read": 0, "voynich_rows": 0,
        "f84": {"opened": False, "parsed": False, "retained": False, "scored": False},
        "bindings": bindings,
    }
    raw = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
    data["content_sha256"] = hashlib.sha256(raw).hexdigest()
    OUT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": data["status"], "partial_files": partial_files}, sort_keys=True))


if __name__ == "__main__":
    main()
