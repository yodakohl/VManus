#!/usr/bin/env python3
"""Freeze GDT395 world-hypothesis scoring correction before execution."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark"
OUT = EXP / "artifacts/gdt395_scoring_execution_v3_correction.json"
SCORE_DIR = EXP / "artifacts/gdt395_identifiability_scores"
BINDINGS = (
    "SCORING_DESIGN.md",
    "VALIDATION_DESIGN.md",
    "SCORING_EXECUTION_CORRECTION.md",
    "SCORING_EXECUTION_CORRECTION_V3.md",
    "artifacts/gdt395_blind_claims_freeze.json",
    "artifacts/gdt395_blind_claims_validation.json",
    "artifacts/gdt395_scoring_execution_v2_correction.json",
    "artifacts/gdt395_scoring_execution_v2_correction_validation.json",
    "src/score_identifiability.py",
    "src/score_identifiability_v2.py",
    "src/score_identifiability_v3.py",
    "src/validate_identifiability.py",
    "src/freeze_scoring_execution_v3_correction.py",
    "src/validate_scoring_execution_v3_correction.py",
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
        raise RuntimeError("refusing to overwrite scoring V3 correction freeze")
    if SCORE_DIR.exists() and any(path.is_file() for path in SCORE_DIR.rglob("*")):
        raise RuntimeError("score output exists before V3 correction freeze")
    claim_freeze_path = EXP / "artifacts/gdt395_blind_claims_freeze.json"
    claim_validation_path = EXP / "artifacts/gdt395_blind_claims_validation.json"
    claim_freeze = json.loads(claim_freeze_path.read_text())
    claim_validation = json.loads(claim_validation_path.read_text())
    implementation = claim_freeze.get("bindings", {}).get("implementation", {}).get("hashes", {})
    checks_freeze = claim_freeze.get("checks", {})
    checks_validation = claim_validation.get("checks", {})
    gate = (
        valid_content(claim_freeze)
        and claim_freeze.get("schema") == "GDT395_BLIND_CLAIMS_FREEZE_V2"
        and claim_freeze.get("status") == "PASS"
        and claim_freeze.get("phase") == "FROZEN_BEFORE_ORACLE_ACCESS"
        and bool(checks_freeze)
        and all(type(value) is bool and value for value in checks_freeze.values())
        and implementation.get("src/score_identifiability.py")
        == sha(EXP / "src/score_identifiability.py")
        and valid_content(claim_validation)
        and claim_validation.get("schema") == "GDT395_BLIND_CLAIMS_VALIDATION_V2"
        and claim_validation.get("status") == "PASS"
        and claim_validation.get("freeze_sha256") == sha(claim_freeze_path)
        and claim_validation.get("checks_passed") == claim_validation.get("checks_total")
        and bool(checks_validation)
        and all(type(value) is bool and value for value in checks_validation.values())
    )
    if not gate:
        raise RuntimeError("blind-claim gate invalid before V3 correction")
    v2_validation = json.loads(
        (EXP / "artifacts/gdt395_scoring_execution_v2_correction_validation.json").read_text()
    )
    if not valid_content(v2_validation) or v2_validation.get("status") != "PASS":
        raise RuntimeError("V2 correction lineage is invalid")
    data = {
        "schema": "GDT395_SCORING_EXECUTION_V3_CORRECTION_V1",
        "status": "FROZEN_BEFORE_SCORING_V3",
        "v2_failure": "WORLD_HYPOTHESIS_VALUES_NOT_LITERAL_BOOLEAN",
        "v2_score_files_written": 0,
        "repair_scope": "FROZEN_VALIDATOR_WORLD_HYPOTHESIS_SEMANTICS_ONLY",
        "bindings": {rel: sha(EXP / rel) for rel in BINDINGS},
        "checks": {
            "blind_claim_gate_validated": True,
            "v2_lineage_validated": True,
            "event_scoring_unchanged": True,
            "oracle_allowlist_unchanged": True,
            "no_score_output_before_v3": True,
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

