#!/usr/bin/env python3
"""Idempotently validate the settled GDT395 V5 release artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark"
SCORE = EXP / "artifacts/gdt395_identifiability_scores_v5"
VALIDATION = EXP / "artifacts/gdt395_identifiability_validation_v5.json"
FILES = {
    "architecture_metrics.tsv", "method_stress_tests.tsv", "pair_panel_metrics.tsv",
    "panel_metrics.tsv", "property_decisions.tsv", "summary.json",
    "w10_false_discoveries.tsv", "world_representation_metrics.tsv",
}
CHECKS = {
    "aggregate_only_output", "architecture_diagnostics", "authentic_complete_join",
    "claim_roles_hashes_and_schemas", "entity_reuse_recurring_truth_restriction",
    "exploratory_only_decisions", "no_event_row_or_voynich_leakage",
    "oracle_manifest_binding_and_hashes", "pair_subset_and_all_endpoints_unscored",
    "seed_decoder_representation_two_luna_aggregation",
    "seven_authentic_partitions_recomputed", "ten_interface_holds_preserved",
    "v2_claim_freeze_and_validation", "w10_exact_3125_diagnostics",
}
ROWS = {
    "architecture_metrics.tsv": 25, "method_stress_tests.tsv": 6,
    "pair_panel_metrics.tsv": 10200, "panel_metrics.tsv": 25500,
    "property_decisions.tsv": 17, "w10_false_discoveries.tsv": 42,
    "world_representation_metrics.tsv": 1020,
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


def valid_content(data: dict) -> bool:
    payload = dict(data)
    declared = payload.pop("content_sha256", "")
    return canonical_hash(payload) == declared


def pass_artifact(path: Path, schema: str) -> bool:
    data = json.loads(path.read_text())
    return bool(
        valid_content(data) and data.get("schema") == schema
        and data.get("status") == "PASS" and bool(data.get("checks"))
        and data.get("checks_passed") == data.get("checks_total")
        and all(type(value) is bool and value for value in data["checks"].values())
    )


def main() -> int:
    validation = json.loads(VALIDATION.read_text())
    actual_files = {path.name for path in SCORE.iterdir() if path.is_file()}
    v3_freeze = EXP / "artifacts/gdt395_validation_execution_v3_correction.json"
    v3_check = EXP / "artifacts/gdt395_validation_execution_v3_correction_validation.json"
    v5_freeze = EXP / "artifacts/gdt395_scorer_validator_conformance_v5.json"
    v5_check = EXP / "artifacts/gdt395_scorer_validator_conformance_v5_validation.json"
    checks = {
        "validation_content": valid_content(validation),
        "validation_schema_status": (
            validation.get("schema") == "GDT395_IDENTIFIABILITY_INDEPENDENT_VALIDATION_V1"
            and validation.get("status") == "PASS"
        ),
        "exact_independent_checks": (
            set(validation.get("checks", {})) == CHECKS
            and all(type(value) is bool and value for value in validation["checks"].values())
        ),
        "exact_rows": validation.get("scorer_output_rows") == ROWS,
        "oracle_accounting": validation.get("oracle_rows_read") == 422697,
        "aggregate_seals": (
            validation.get("contains_event_rows") is False
            and validation.get("voynich_rows") == 0
        ),
        "validator_source": (
            validation.get("validator_source_sha256")
            == sha(EXP / "src/validate_identifiability.py")
        ),
        "exact_output_set": actual_files == FILES,
        "exact_output_hashes": (
            set(validation.get("scorer_output_sha256", {})) == FILES
            and all(sha(SCORE / name) == digest
                    for name, digest in validation["scorer_output_sha256"].items())
        ),
        "v3_correction_lineage": (
            pass_artifact(v3_check, "GDT395_VALIDATION_EXECUTION_V3_CORRECTION_VALIDATION_V1")
            and json.loads(v3_check.read_text()).get("freeze_sha256") == sha(v3_freeze)
            and json.loads(v3_freeze.read_text()).get("bindings", {}).get(
                "src/validate_identifiability_v3.py"
            ) == sha(EXP / "src/validate_identifiability_v3.py")
        ),
        "v5_conformance_lineage": (
            pass_artifact(v5_check, "GDT395_SCORER_VALIDATOR_CONFORMANCE_V5_VALIDATION_V1")
            and json.loads(v5_check.read_text()).get("freeze_sha256") == sha(v5_freeze)
            and json.loads(v5_freeze.read_text()).get("bindings", {}).get(
                "src/score_identifiability_v5.py"
            ) == sha(EXP / "src/score_identifiability_v5.py")
        ),
        "f84_seals": (
            json.loads(v3_freeze.read_text()).get("checks", {}).get("f84_opened") is False
            and json.loads(v5_freeze.read_text()).get("checks", {}).get("f84_opened") is False
            and json.loads(v5_freeze.read_text()).get("checks", {}).get("f84r_opened") is False
        ),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    print(json.dumps({
        "schema": "GDT395_IDENTIFIABILITY_RELEASE_VALIDATION_V1",
        "status": status, "checks_passed": sum(checks.values()),
        "checks_total": len(checks), "validation_sha256": sha(VALIDATION),
    }, sort_keys=True))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
