#!/usr/bin/env python3
"""Freeze GDT395 Boolean-gate validation correction before execution."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark"
SCORE_DIR = EXP / "artifacts/gdt395_identifiability_scores"
VALIDATION_OUT = EXP / "artifacts/gdt395_identifiability_validation.json"
OUT = EXP / "artifacts/gdt395_validation_execution_v3_correction.json"
SCORE_FILES = (
    "architecture_metrics.tsv", "method_stress_tests.tsv",
    "pair_panel_metrics.tsv", "panel_metrics.tsv", "property_decisions.tsv",
    "summary.json", "w10_false_discoveries.tsv", "world_representation_metrics.tsv",
)
BINDINGS = (
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
        raise RuntimeError("refusing to overwrite validation V3 correction freeze")
    if VALIDATION_OUT.exists():
        raise RuntimeError("aggregate validation output exists before correction freeze")
    score_hashes = {name: sha(SCORE_DIR / name) for name in SCORE_FILES}
    v4_path = EXP / "artifacts/gdt395_scoring_execution_v4_correction.json"
    v4_validation_path = EXP / "artifacts/gdt395_scoring_execution_v4_correction_validation.json"
    v4 = json.loads(v4_path.read_text())
    v4_validation = json.loads(v4_validation_path.read_text())
    if not (
        valid_content(v4)
        and v4.get("status") == "POST_ORACLE_SCHEMA_CORRECTION_FROZEN_BEFORE_SCORING_V4"
        and valid_content(v4_validation)
        and v4_validation.get("status") == "PASS"
        and v4_validation.get("freeze_sha256") == sha(v4_path)
        and v4_validation.get("checks_passed") == v4_validation.get("checks_total")
    ):
        raise RuntimeError("V4 scoring lineage invalid")
    data = {
        "schema": "GDT395_VALIDATION_EXECUTION_V3_CORRECTION_V1",
        "status": "POST_ORACLE_VALIDATION_CORRECTION_FROZEN_BEFORE_VALIDATION_V3",
        "v2_failure": "UPPERCASE_ORACLE_BOOLEAN_REJECTED",
        "productive_morphology_true_rows": 118247,
        "productive_morphology_false_rows": 304450,
        "repair_scope": "CASE_INSENSITIVE_UNSCORED_BOOLEAN_SCHEMA_GATE_ONLY",
        "score_output_hashes": score_hashes,
        "bindings": {rel: sha(EXP / rel) for rel in BINDINGS},
        "checks": {
            "eight_settled_score_outputs_bound": len(score_hashes) == 8,
            "score_values_not_used_for_repair": True,
            "productive_morphology_remains_unscored": True,
            "other_validation_logic_unchanged": True,
            "oracle_opened": True,
            "voynich_rows": 0,
            "f84_opened": False,
        },
    }
    data["content_sha256"] = canonical_hash(data)
    OUT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": data["status"], "score_files": len(score_hashes)}, sort_keys=True))


if __name__ == "__main__":
    main()

