#!/usr/bin/env python3
"""Validate the pre-execution GDT395 world-hypothesis correction."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark"
FREEZE = EXP / "artifacts/gdt395_scoring_execution_v3_correction.json"
OUT = EXP / "artifacts/gdt395_scoring_execution_v3_correction_validation.json"
SCORE_DIR = EXP / "artifacts/gdt395_identifiability_scores"
EXPECTED_WRAPPER_SHA256 = "8a3f8622eded992ce7aaef72f1654a34b76bfd5e6216b8d223579b40ea9a5303"
EXPECTED_BINDINGS = {
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
}


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
        raise RuntimeError("refusing to overwrite scoring V3 correction validation")
    data = json.loads(FREEZE.read_text())
    bindings = data.get("bindings", {})
    wrapper_path = EXP / "src/score_identifiability_v3.py"
    tree = ast.parse(wrapper_path.read_text())
    assignments = {ast.unparse(node) for node in ast.walk(tree) if isinstance(node, ast.Assign)}
    claims_freeze_path = EXP / "artifacts/gdt395_blind_claims_freeze.json"
    claims_validation_path = EXP / "artifacts/gdt395_blind_claims_validation.json"
    claims_freeze = json.loads(claims_freeze_path.read_text())
    claims_validation = json.loads(claims_validation_path.read_text())
    implementation = claims_freeze.get("bindings", {}).get("implementation", {}).get("hashes", {})
    claim_freeze_checks = claims_freeze.get("checks", {})
    claim_validation_checks = claims_validation.get("checks", {})
    v2_freeze_path = EXP / "artifacts/gdt395_scoring_execution_v2_correction.json"
    v2_validation_path = EXP / "artifacts/gdt395_scoring_execution_v2_correction_validation.json"
    v2_freeze = json.loads(v2_freeze_path.read_text())
    v2_validation = json.loads(v2_validation_path.read_text())
    checks = {
        "content_hash": valid_content(data),
        "schema_status": (
            data.get("schema") == "GDT395_SCORING_EXECUTION_V3_CORRECTION_V1"
            and data.get("status") == "FROZEN_BEFORE_SCORING_V3"
            and data.get("v2_failure") == "WORLD_HYPOTHESIS_VALUES_NOT_LITERAL_BOOLEAN"
            and data.get("v2_score_files_written") == 0
            and data.get("repair_scope")
            == "FROZEN_VALIDATOR_WORLD_HYPOTHESIS_SEMANTICS_ONLY"
        ),
        "exact_bindings": (
            set(bindings) == EXPECTED_BINDINGS
            and all((EXP / rel).is_file() and sha(EXP / rel) == digest
                    for rel, digest in bindings.items())
        ),
        "exact_wrapper": (
            sha(wrapper_path) == EXPECTED_WRAPPER_SHA256
            and any("v1.open_tsv = open_tsv_v3" in item for item in assignments)
            and any("v1.parse_bool = parse_world_boolean_v3" in item for item in assignments)
            and any("v1.architecture_scores = architecture_scores_v3" in item
                    for item in assignments)
        ),
        "claim_gate": (
            valid_content(claims_freeze)
            and claims_freeze.get("schema") == "GDT395_BLIND_CLAIMS_FREEZE_V2"
            and claims_freeze.get("status") == "PASS"
            and claims_freeze.get("phase") == "FROZEN_BEFORE_ORACLE_ACCESS"
            and bool(claim_freeze_checks)
            and all(type(value) is bool and value for value in claim_freeze_checks.values())
            and implementation.get("src/score_identifiability.py")
            == sha(EXP / "src/score_identifiability.py")
            and valid_content(claims_validation)
            and claims_validation.get("schema") == "GDT395_BLIND_CLAIMS_VALIDATION_V2"
            and claims_validation.get("status") == "PASS"
            and claims_validation.get("freeze_sha256") == sha(claims_freeze_path)
            and claims_validation.get("checks_passed") == claims_validation.get("checks_total")
            and bool(claim_validation_checks)
            and all(type(value) is bool and value
                    for value in claim_validation_checks.values())
        ),
        "v2_lineage": (
            valid_content(v2_freeze)
            and v2_freeze.get("status") == "FROZEN_BEFORE_SCORING_V2"
            and valid_content(v2_validation)
            and v2_validation.get("status") == "PASS"
            and v2_validation.get("freeze_sha256") == sha(v2_freeze_path)
            and v2_validation.get("checks_passed") == v2_validation.get("checks_total")
            and bool(v2_validation.get("checks"))
            and all(type(value) is bool and value
                    for value in v2_validation.get("checks", {}).values())
        ),
        "freeze_checks": data.get("checks") == {
            "blind_claim_gate_validated": True,
            "v2_lineage_validated": True,
            "event_scoring_unchanged": True,
            "oracle_allowlist_unchanged": True,
            "no_score_output_before_v3": True,
            "oracle_opened": False,
            "voynich_rows": 0,
            "f84_opened": False,
        },
        "no_score_output": (
            not SCORE_DIR.exists()
            or not any(path.is_file() for path in SCORE_DIR.rglob("*"))
        ),
    }
    result = {
        "schema": "GDT395_SCORING_EXECUTION_V3_CORRECTION_VALIDATION_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "freeze_sha256": sha(FREEZE),
        "validator_sha256": sha(Path(__file__)),
    }
    result["content_sha256"] = canonical_hash(result)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "checks": f"{result['checks_passed']}/{result['checks_total']}"}, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

