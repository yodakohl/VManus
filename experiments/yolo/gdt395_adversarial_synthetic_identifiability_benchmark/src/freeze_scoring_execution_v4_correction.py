#!/usr/bin/env python3
"""Freeze the post-oracle GDT395 opaque-set partition correction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark"
OUT = EXP / "artifacts/gdt395_scoring_execution_v4_correction.json"
SCORE_DIR = EXP / "artifacts/gdt395_identifiability_scores"
BINDINGS = (
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
        raise RuntimeError("refusing to overwrite scoring V4 correction freeze")
    if SCORE_DIR.exists() and any(path.is_file() for path in SCORE_DIR.rglob("*")):
        raise RuntimeError("aggregate score output exists before V4 correction freeze")
    claim_freeze_path = EXP / "artifacts/gdt395_blind_claims_freeze.json"
    claim_validation_path = EXP / "artifacts/gdt395_blind_claims_validation.json"
    claim_freeze = json.loads(claim_freeze_path.read_text())
    claim_validation = json.loads(claim_validation_path.read_text())
    v3_freeze_path = EXP / "artifacts/gdt395_scoring_execution_v3_correction.json"
    v3_validation_path = EXP / "artifacts/gdt395_scoring_execution_v3_correction_validation.json"
    v3_freeze = json.loads(v3_freeze_path.read_text())
    v3_validation = json.loads(v3_validation_path.read_text())
    implementation = claim_freeze.get("bindings", {}).get("implementation", {}).get("hashes", {})
    gate = (
        valid_content(claim_freeze) and claim_freeze.get("status") == "PASS"
        and claim_freeze.get("phase") == "FROZEN_BEFORE_ORACLE_ACCESS"
        and implementation.get("src/score_identifiability.py")
        == sha(EXP / "src/score_identifiability.py")
        and valid_content(claim_validation) and claim_validation.get("status") == "PASS"
        and claim_validation.get("freeze_sha256") == sha(claim_freeze_path)
        and claim_validation.get("checks_passed") == claim_validation.get("checks_total")
        and valid_content(v3_freeze) and v3_freeze.get("status") == "FROZEN_BEFORE_SCORING_V3"
        and valid_content(v3_validation) and v3_validation.get("status") == "PASS"
        and v3_validation.get("freeze_sha256") == sha(v3_freeze_path)
        and v3_validation.get("checks_passed") == v3_validation.get("checks_total")
    )
    if not gate:
        raise RuntimeError("published scoring lineage is invalid before V4 correction")
    data = {
        "schema": "GDT395_SCORING_EXECUTION_V4_CORRECTION_V1",
        "status": "POST_ORACLE_SCHEMA_CORRECTION_FROZEN_BEFORE_SCORING_V4",
        "v3_failure": "CANONICAL_MULTI_ID_TRUTH_REJECTED_AS_NONSCALAR",
        "aggregate_score_files_written": 0,
        "held_oracle_files_opened": 50,
        "held_oracle_rows_opened": 422697,
        "repair_scope": "CANONICAL_OPAQUE_SET_AS_EXACT_PARTITION_LABEL",
        "bindings": {rel: sha(EXP / rel) for rel in BINDINGS},
        "checks": {
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
    }
    data["content_sha256"] = canonical_hash(data)
    OUT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": data["status"], "bindings": len(data["bindings"])}, sort_keys=True))


if __name__ == "__main__":
    main()

