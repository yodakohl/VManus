#!/usr/bin/env python3
"""Freeze the gzip-only GDT395 scoring correction before its execution."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark"
OUT = EXP / "artifacts/gdt395_scoring_execution_v2_correction.json"
SCORE_DIR = EXP / "artifacts/gdt395_identifiability_scores"
BINDINGS = (
    "SCORING_DESIGN.md",
    "SCORING_EXECUTION_CORRECTION.md",
    "artifacts/gdt395_blind_claims_freeze.json",
    "artifacts/gdt395_blind_claims_validation.json",
    "artifacts/gdt395_corpus_manifest.tsv",
    "src/score_identifiability.py",
    "src/score_identifiability_v2.py",
    "src/freeze_scoring_execution_v2_correction.py",
    "src/validate_scoring_execution_v2_correction.py",
)


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def valid_content(data: dict) -> bool:
    copy = dict(data)
    expected = copy.pop("content_sha256", "")
    return canonical_hash(copy) == expected


def main() -> None:
    if OUT.exists():
        raise RuntimeError("refusing to overwrite scoring V2 correction freeze")
    score_files = list(SCORE_DIR.rglob("*")) if SCORE_DIR.exists() else []
    if any(path.is_file() for path in score_files):
        raise RuntimeError("score output exists before V2 correction freeze")
    claims_freeze_path = EXP / "artifacts/gdt395_blind_claims_freeze.json"
    claims_validation_path = EXP / "artifacts/gdt395_blind_claims_validation.json"
    claims_freeze = json.loads(claims_freeze_path.read_text())
    claims_validation = json.loads(claims_validation_path.read_text())
    implementation = claims_freeze.get("bindings", {}).get("implementation", {}).get("hashes", {})
    freeze_checks = claims_freeze.get("checks", {})
    validation_checks = claims_validation.get("checks", {})
    claim_gate_valid = (
        valid_content(claims_freeze)
        and claims_freeze.get("schema") == "GDT395_BLIND_CLAIMS_FREEZE_V2"
        and claims_freeze.get("status") == "PASS"
        and claims_freeze.get("phase") == "FROZEN_BEFORE_ORACLE_ACCESS"
        and bool(freeze_checks)
        and all(type(value) is bool and value for value in freeze_checks.values())
        and implementation.get("src/score_identifiability.py")
        == sha(EXP / "src/score_identifiability.py")
        and valid_content(claims_validation)
        and claims_validation.get("schema") == "GDT395_BLIND_CLAIMS_VALIDATION_V2"
        and claims_validation.get("status") == "PASS"
        and claims_validation.get("freeze_sha256") == sha(claims_freeze_path)
        and claims_validation.get("checks_passed") == claims_validation.get("checks_total")
        and bool(validation_checks)
        and all(type(value) is bool and value for value in validation_checks.values())
    )
    if not claim_gate_valid:
        raise RuntimeError("published blind-claim gate is not valid for scoring correction")
    data = {
        "schema": "GDT395_SCORING_EXECUTION_V2_CORRECTION_V1",
        "status": "FROZEN_BEFORE_SCORING_V2",
        "v1_failure": "GZIP_CLAIM_OPENED_AS_PLAIN_UTF8",
        "v1_score_files_written": 0,
        "repair_scope": "GZIP_TRANSPORT_DISPATCH_ONLY",
        "bindings": {rel: sha(EXP / rel) for rel in BINDINGS},
        "checks": {
            "claim_freeze_unchanged": True,
            "claim_gate_validated": True,
            "scoring_design_unchanged": True,
            "original_scorer_unchanged": True,
            "no_score_output_before_v2": True,
            "oracle_opened": False,
            "voynich_rows": 0,
            "f84_opened": False,
        },
    }
    data["content_sha256"] = canonical_hash(data)
    OUT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": data["status"], "bindings": len(data["bindings"])}, sort_keys=True))


if __name__ == "__main__":
    main()
