#!/usr/bin/env python3
"""Validate the GDT395 case-insensitive Boolean-gate correction."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark"
SCORE_DIR = EXP / "artifacts/gdt395_identifiability_scores"
VALIDATION_OUT = EXP / "artifacts/gdt395_identifiability_validation.json"
FREEZE = EXP / "artifacts/gdt395_validation_execution_v3_correction.json"
OUT = EXP / "artifacts/gdt395_validation_execution_v3_correction_validation.json"
EXPECTED_WRAPPER_SHA256 = "46972cc1253a8c4131a40a75a79ae266fadf34e63a85932e7e2fbb09cd8b5f0a"
EXPECTED_SCORE_FILES = {
    "architecture_metrics.tsv", "method_stress_tests.tsv",
    "pair_panel_metrics.tsv", "panel_metrics.tsv", "property_decisions.tsv",
    "summary.json", "w10_false_discoveries.tsv", "world_representation_metrics.tsv",
}
EXPECTED_BINDINGS = {
    "VALIDATION_DESIGN.md", "VALIDATION_EXECUTION_CORRECTION_V3.md",
    "artifacts/gdt395_blind_claims_freeze.json",
    "artifacts/gdt395_blind_claims_validation.json",
    "artifacts/gdt395_corpus_manifest.tsv",
    "artifacts/gdt395_scoring_execution_v4_correction.json",
    "artifacts/gdt395_scoring_execution_v4_correction_validation.json",
    "src/validate_identifiability.py", "src/validate_identifiability_v2.py",
    "src/validate_identifiability_v3.py",
    "src/freeze_validation_execution_v3_correction.py",
    "src/validate_validation_execution_v3_correction.py",
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
        raise RuntimeError("refusing to overwrite validation correction validation")
    data = json.loads(FREEZE.read_text())
    bindings = data.get("bindings", {})
    wrapper = EXP / "src/validate_identifiability_v3.py"
    tree = ast.parse(wrapper.read_text())
    assignments = {ast.unparse(node) for node in ast.walk(tree) if isinstance(node, ast.Assign)}
    score_hashes = data.get("score_output_hashes", {})
    v4_path = EXP / "artifacts/gdt395_scoring_execution_v4_correction.json"
    v4_validation_path = EXP / "artifacts/gdt395_scoring_execution_v4_correction_validation.json"
    v4 = json.loads(v4_path.read_text())
    v4_validation = json.loads(v4_validation_path.read_text())
    checks = {
        "content_hash": valid_content(data),
        "schema_status": (
            data.get("schema") == "GDT395_VALIDATION_EXECUTION_V3_CORRECTION_V1"
            and data.get("status")
            == "POST_ORACLE_VALIDATION_CORRECTION_FROZEN_BEFORE_VALIDATION_V3"
            and data.get("v2_failure") == "UPPERCASE_ORACLE_BOOLEAN_REJECTED"
            and data.get("repair_scope")
            == "CASE_INSENSITIVE_UNSCORED_BOOLEAN_SCHEMA_GATE_ONLY"
        ),
        "exact_bindings": (
            set(bindings) == EXPECTED_BINDINGS
            and all((EXP / rel).is_file() and sha(EXP / rel) == digest
                    for rel, digest in bindings.items())
        ),
        "exact_wrapper": (
            sha(wrapper) == EXPECTED_WRAPPER_SHA256
            and any("v1.validate_oracle_scalar_fields = validate_oracle_partition_fields_v3"
                    in item for item in assignments)
        ),
        "score_outputs_bound": (
            set(score_hashes) == EXPECTED_SCORE_FILES
            and all((SCORE_DIR / name).is_file() and sha(SCORE_DIR / name) == digest
                    for name, digest in score_hashes.items())
        ),
        "v4_lineage": (
            valid_content(v4)
            and v4.get("status") == "POST_ORACLE_SCHEMA_CORRECTION_FROZEN_BEFORE_SCORING_V4"
            and valid_content(v4_validation) and v4_validation.get("status") == "PASS"
            and v4_validation.get("freeze_sha256") == sha(v4_path)
            and v4_validation.get("checks_passed") == v4_validation.get("checks_total")
            and bool(v4_validation.get("checks"))
            and all(type(value) is bool and value
                    for value in v4_validation.get("checks", {}).values())
        ),
        "exposure_counts": (
            data.get("productive_morphology_true_rows") == 118247
            and data.get("productive_morphology_false_rows") == 304450
            and data.get("productive_morphology_true_rows")
            + data.get("productive_morphology_false_rows") == 422697
        ),
        "freeze_checks": data.get("checks") == {
            "eight_settled_score_outputs_bound": True,
            "score_values_not_used_for_repair": True,
            "productive_morphology_remains_unscored": True,
            "other_validation_logic_unchanged": True,
            "oracle_opened": True,
            "voynich_rows": 0,
            "f84_opened": False,
        },
        "validation_output_absent": not VALIDATION_OUT.exists(),
    }
    result = {
        "schema": "GDT395_VALIDATION_EXECUTION_V3_CORRECTION_VALIDATION_V1",
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

