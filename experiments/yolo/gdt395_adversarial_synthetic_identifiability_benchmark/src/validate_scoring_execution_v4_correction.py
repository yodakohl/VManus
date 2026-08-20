#!/usr/bin/env python3
"""Validate the post-oracle GDT395 opaque-set partition correction."""

from __future__ import annotations

import ast
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark"
FREEZE = EXP / "artifacts/gdt395_scoring_execution_v4_correction.json"
OUT = EXP / "artifacts/gdt395_scoring_execution_v4_correction_validation.json"
SCORE_DIR = EXP / "artifacts/gdt395_identifiability_scores"
EXPECTED_SCORER_SHA = "6cee6679e1768610e18fe6ade5c6d391d13158222e25a0c97724d9cf6f7fb79b"
EXPECTED_VALIDATOR_SHA = "96d19e176b8864a4a09c19dafb797f1e64427d7081e92a4bc7e4ca7a91904e9e"
EXPECTED_BINDINGS = {
    "SCORING_DESIGN.md", "VALIDATION_DESIGN.md",
    "SCORING_EXECUTION_CORRECTION_V3.md", "SCORING_EXECUTION_CORRECTION_V4.md",
    "artifacts/gdt395_blind_claims_freeze.json",
    "artifacts/gdt395_blind_claims_validation.json",
    "artifacts/gdt395_corpus_manifest.tsv",
    "artifacts/gdt395_scoring_execution_v3_correction.json",
    "artifacts/gdt395_scoring_execution_v3_correction_validation.json",
    "src/score_identifiability.py", "src/score_identifiability_v3.py",
    "src/score_identifiability_v4.py", "src/validate_identifiability.py",
    "src/validate_identifiability_v2.py",
    "src/freeze_scoring_execution_v4_correction.py",
    "src/validate_scoring_execution_v4_correction.py",
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


def ast_assignments(path: Path) -> set[str]:
    tree = ast.parse(path.read_text())
    return {ast.unparse(node) for node in ast.walk(tree) if isinstance(node, ast.Assign)}


def main() -> None:
    if OUT.exists():
        raise RuntimeError("refusing to overwrite scoring V4 correction validation")
    data = json.loads(FREEZE.read_text())
    bindings = data.get("bindings", {})
    scorer = EXP / "src/score_identifiability_v4.py"
    validator = EXP / "src/validate_identifiability_v2.py"
    scorer_assignments = ast_assignments(scorer)
    validator_assignments = ast_assignments(validator)
    claim_freeze_path = EXP / "artifacts/gdt395_blind_claims_freeze.json"
    claim_validation_path = EXP / "artifacts/gdt395_blind_claims_validation.json"
    claim_freeze = json.loads(claim_freeze_path.read_text())
    claim_validation = json.loads(claim_validation_path.read_text())
    claim_checks = claim_freeze.get("checks", {})
    validation_checks = claim_validation.get("checks", {})
    implementation = claim_freeze.get("bindings", {}).get("implementation", {}).get("hashes", {})
    v3_freeze_path = EXP / "artifacts/gdt395_scoring_execution_v3_correction.json"
    v3_validation_path = EXP / "artifacts/gdt395_scoring_execution_v3_correction_validation.json"
    v3_freeze = json.loads(v3_freeze_path.read_text())
    v3_validation = json.loads(v3_validation_path.read_text())
    with (EXP / "artifacts/gdt395_corpus_manifest.tsv").open(
        newline="", encoding="utf-8"
    ) as handle:
        held_manifest = [
            row for row in csv.DictReader(handle, delimiter="\t")
            if int(row["corpus_seed"]) in range(15, 20)
        ]
    checks = {
        "content_hash": valid_content(data),
        "schema_status": (
            data.get("schema") == "GDT395_SCORING_EXECUTION_V4_CORRECTION_V1"
            and data.get("status") == "POST_ORACLE_SCHEMA_CORRECTION_FROZEN_BEFORE_SCORING_V4"
            and data.get("v3_failure") == "CANONICAL_MULTI_ID_TRUTH_REJECTED_AS_NONSCALAR"
            and data.get("aggregate_score_files_written") == 0
            and data.get("repair_scope") == "CANONICAL_OPAQUE_SET_AS_EXACT_PARTITION_LABEL"
        ),
        "exact_bindings": (
            set(bindings) == EXPECTED_BINDINGS
            and all((EXP / rel).is_file() and sha(EXP / rel) == digest
                    for rel, digest in bindings.items())
        ),
        "exact_wrappers": (
            sha(scorer) == EXPECTED_SCORER_SHA
            and sha(validator) == EXPECTED_VALIDATOR_SHA
            and any("v1.parse_oracle_scalar = parse_oracle_partition_v4" in item
                    for item in scorer_assignments)
            and any("v1.validate_oracle_scalar_fields = validate_oracle_partition_fields_v2"
                    in item for item in validator_assignments)
        ),
        "claim_gate": (
            valid_content(claim_freeze) and claim_freeze.get("status") == "PASS"
            and claim_freeze.get("phase") == "FROZEN_BEFORE_ORACLE_ACCESS"
            and bool(claim_checks)
            and all(type(value) is bool and value for value in claim_checks.values())
            and implementation.get("src/score_identifiability.py")
            == sha(EXP / "src/score_identifiability.py")
            and valid_content(claim_validation) and claim_validation.get("status") == "PASS"
            and claim_validation.get("freeze_sha256") == sha(claim_freeze_path)
            and claim_validation.get("checks_passed") == claim_validation.get("checks_total")
            and bool(validation_checks)
            and all(type(value) is bool and value for value in validation_checks.values())
        ),
        "v3_lineage": (
            valid_content(v3_freeze) and v3_freeze.get("status") == "FROZEN_BEFORE_SCORING_V3"
            and valid_content(v3_validation) and v3_validation.get("status") == "PASS"
            and v3_validation.get("freeze_sha256") == sha(v3_freeze_path)
            and v3_validation.get("checks_passed") == v3_validation.get("checks_total")
            and bool(v3_validation.get("checks"))
            and all(type(value) is bool and value
                    for value in v3_validation.get("checks", {}).values())
        ),
        "oracle_exposure_accounting": (
            len(held_manifest) == data.get("held_oracle_files_opened") == 50
            and sum(int(row["events"]) for row in held_manifest)
            == data.get("held_oracle_rows_opened") == 422697
            and data.get("checks", {}).get("oracle_opened") is True
        ),
        "freeze_checks": data.get("checks") == {
            "blind_claim_gate_preserved": True,
            "v3_lineage_validated": True,
            "all_events_retained": True,
            "no_atom_selection_or_split": True,
            "event_metrics_and_thresholds_unchanged": True,
            "oracle_allowlist_unchanged": True,
            "aggregate_score_output_absent": True,
            "oracle_opened": True,
            "voynich_rows": 0,
            "f84_opened": False,
        },
        "aggregate_output_absent": (
            not SCORE_DIR.exists()
            or not any(path.is_file() for path in SCORE_DIR.rglob("*"))
        ),
    }
    result = {
        "schema": "GDT395_SCORING_EXECUTION_V4_CORRECTION_VALIDATION_V1",
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

