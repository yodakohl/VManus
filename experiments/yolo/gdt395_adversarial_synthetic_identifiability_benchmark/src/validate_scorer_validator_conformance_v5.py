#!/usr/bin/env python3
"""Validate the frozen GDT395 V5 conformance correction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark"
OLD_SCORE = EXP / "artifacts/gdt395_identifiability_scores"
NEW_SCORE = EXP / "artifacts/gdt395_identifiability_scores_v5"
FREEZE = EXP / "artifacts/gdt395_scorer_validator_conformance_v5.json"
OUT = EXP / "artifacts/gdt395_scorer_validator_conformance_v5_validation.json"
EXPECTED_FILES = {
    "architecture_metrics.tsv", "method_stress_tests.tsv", "pair_panel_metrics.tsv",
    "panel_metrics.tsv", "property_decisions.tsv", "summary.json",
    "w10_false_discoveries.tsv", "world_representation_metrics.tsv",
}
EXPECTED_BINDINGS = {
    "SCORING_DESIGN.md", "VALIDATION_DESIGN.md",
    "SCORER_VALIDATOR_CONFORMANCE_CORRECTION_V5.md",
    "artifacts/gdt395_blind_claims_freeze.json",
    "artifacts/gdt395_blind_claims_validation.json",
    "artifacts/gdt395_corpus_manifest.tsv",
    "artifacts/gdt395_scoring_execution_v4_correction.json",
    "artifacts/gdt395_scoring_execution_v4_correction_validation.json",
    "artifacts/gdt395_validation_execution_v3_correction.json",
    "artifacts/gdt395_validation_execution_v3_correction_validation.json",
    "src/score_identifiability.py", "src/score_identifiability_v3.py",
    "src/score_identifiability_v4.py", "src/score_identifiability_v5.py",
    "src/run_identifiability_scoring_v5.py", "src/validate_identifiability.py",
    "src/validate_identifiability_v2.py", "src/validate_identifiability_v3.py",
    "src/freeze_scorer_validator_conformance_v5.py",
    "src/validate_scorer_validator_conformance_v5.py",
}


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    ).encode("ascii")).hexdigest()


def main() -> None:
    if OUT.exists():
        raise RuntimeError("refusing to overwrite V5 correction validation")
    data = json.loads(FREEZE.read_text())
    payload = dict(data)
    declared = payload.pop("content_sha256", "")
    old = data.get("superseded_v4_output_sha256", {})
    bindings = data.get("bindings", {})
    checks = {
        "content_hash": canonical_hash(payload) == declared,
        "schema_status": (
            data.get("schema") == "GDT395_SCORER_VALIDATOR_CONFORMANCE_V5_FREEZE_V1"
            and data.get("status")
            == "POST_ORACLE_CONFORMANCE_CORRECTION_FROZEN_BEFORE_SCORING_V5"
            and data.get("failure_gate") == "PANEL_METRICS_MISMATCH_GATE"
            and data.get("repair_basis") == "PRE_ORACLE_INDEPENDENT_VALIDATION_DESIGN"
        ),
        "old_outputs_bound": (
            set(old) == EXPECTED_FILES
            and all((OLD_SCORE / name).is_file() and sha(OLD_SCORE / name) == digest
                    for name, digest in old.items())
        ),
        "implementation_bindings": (
            set(bindings) == EXPECTED_BINDINGS
            and all((EXP / rel).is_file() and sha(EXP / rel) == digest
                    for rel, digest in bindings.items())
        ),
        "freeze_checks": data.get("checks") == {
            "eight_v4_outputs_bound_before_v5": True,
            "v5_output_absent_at_freeze": True,
            "validator_spec_predates_oracle_access": True,
            "no_metric_or_threshold_selected_from_v4_values": True,
            "post_oracle_chronology_disclosed": True,
            "voynich_rows": 0,
            "f84_opened": False,
            "f84r_opened": False,
        },
        "v5_output_absent": not NEW_SCORE.exists(),
    }
    result = {
        "schema": "GDT395_SCORER_VALIDATOR_CONFORMANCE_V5_VALIDATION_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks, "checks_passed": sum(checks.values()),
        "checks_total": len(checks), "freeze_sha256": sha(FREEZE),
        "validator_sha256": sha(Path(__file__)),
    }
    result["content_sha256"] = canonical_hash(result)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"],
                      "checks": f"{result['checks_passed']}/{result['checks_total']}"}, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
