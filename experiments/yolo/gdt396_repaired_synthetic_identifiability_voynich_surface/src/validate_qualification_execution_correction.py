#!/usr/bin/env python3
"""Independent validation of the GDT396 qualification execution correction."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path


def repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("repository root not found")


ROOT = repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt396_repaired_synthetic_identifiability_voynich_surface"
FREEZE = EXP / "artifacts/gdt396_qualification_execution_correction_freeze.json"
METRICS = EXP / ".work/claims/gdt396_qualification_metrics.tsv"
OUTPUT = EXP / "artifacts/gdt396_qualification_execution_correction_validation.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def content_hash(value: dict) -> str:
    payload = dict(value)
    payload.pop("content_sha256", None)
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> int:
    if OUTPUT.exists():
        raise RuntimeError(f"refusing to overwrite {OUTPUT}")
    frozen = json.loads(FREEZE.read_text(encoding="utf-8"))
    checks: dict[str, bool] = {}
    checks["freeze_schema_status_content"] = (
        frozen.get("schema") == "GDT396_QUALIFICATION_EXECUTION_CORRECTION_FREEZE_V1"
        and frozen.get("status") == "POST_ORACLE_QUALIFIER_ELIGIBILITY_CORRECTION_FROZEN_BEFORE_REQUALIFICATION"
        and frozen.get("content_sha256") == content_hash(frozen)
    )
    checks["bindings_exact"] = all(sha256(EXP / path) == digest for path, digest in frozen.get("bindings", {}).items())
    checks["metrics_exact"] = METRICS.is_file() and sha256(METRICS) == frozen.get("metrics_sha256")
    with METRICS.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    checks["metric_count"] = len(rows) == frozen.get("metrics_rows") == 117100

    semantic = {
        "SEMANTIC_ENTITY_IDENTITY", "CURRENT_PRODUCTIVE_COMPONENT", "CURRENT_SHARED_MEANING",
        "FUNCTION_OPERATOR_CLASS", "SEMANTIC_CATEGORY", "PRODUCTIVE_MORPHOLOGY",
        "TEMPORAL_STATE_GATE", "GENERIC_RELATION", "COORDINATOR_RELATION",
        "ALTERNATIVE_RELATION", "REFERENCE_ANAPHORA", "ENTITY_REUSE_ANTECEDENT",
    }
    groups = defaultdict(list)
    for row in rows:
        if row["world_id"] == "W10" and row["method_variant"] == "PRIMARY" and row["property_id"] in semantic:
            groups[(row["decoder_id"], row["property_id"], row["representation_id"], row["surface_id"])].append(row)
    complete = True
    supported_rates = True
    unsupported_seen = False
    for values in groups.values():
        complete &= len(values) == 5 and len({row["corpus_seed"] for row in values}) == 5
        if {row["status"] for row in values} == {"UNSUPPORTED"}:
            unsupported_seen = True
            continue
        for row in values:
            detail = json.loads(row["metrics_json"])
            supported_rates &= "resolved_without_truth_rate" in detail or "positive_prediction_rate" in detail
    checks["all_w10_routes_complete"] = complete
    checks["unsupported_routes_present"] = unsupported_seen
    checks["all_nonunsupported_semantic_routes_have_rates"] = supported_rates

    sys.path.insert(0, str(EXP / "src"))
    spec = importlib.util.spec_from_file_location("qualify_decoders_v2_audit", EXP / "src/qualify_decoders_v2.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    base_row = {
        "decoder_id": "D", "property_id": "ALTERNATIVE_RELATION", "representation_id": "FULL_GROUP",
        "surface_id": "FREE_SURFACE", "world_id": "W10", "method_variant": "PRIMARY",
    }
    unsupported = [{**base_row, "corpus_seed": str(seed), "status": "UNSUPPORTED", "metrics_json": "{}"} for seed in range(5)]
    checks["unsupported_fixture_exempt"] = module.semantic_w10_false_rates(unsupported, "D", "ALTERNATIVE_RELATION", "FULL_GROUP", "FREE_SURFACE") == []
    failed_missing = False
    try:
        supported = [{**row, "status": "NO_CAPACITY"} for row in unsupported]
        module.semantic_w10_false_rates(supported, "D", "ALTERNATIVE_RELATION", "FULL_GROUP", "FREE_SURFACE")
    except ValueError:
        failed_missing = True
    checks["supported_missing_rate_fails_closed"] = failed_missing
    failed_absent = False
    try:
        module.semantic_w10_false_rates([], "D", "ALTERNATIVE_RELATION", "FULL_GROUP", "FREE_SURFACE")
    except ValueError:
        failed_absent = True
    checks["absent_w10_fails_closed"] = failed_absent
    checks["chronology_disclosed"] = frozen.get("qualification_oracle_opened_before_correction") is True and frozen.get("failed_qualifier_output_written") is False
    checks["scientific_scope_unchanged"] = all(frozen.get(key) is False for key in ("blind_claims_changed", "metrics_changed", "thresholds_changed", "confirmation_generated"))
    checks["seals"] = frozen.get("voynich_rows") == 0 and not frozen["f84"]["accessed"] and not frozen["f84r"]["accessed"]

    result = {
        "schema": "GDT396_QUALIFICATION_EXECUTION_CORRECTION_VALIDATION_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "passed": sum(checks.values()),
        "total": len(checks),
        "freeze_sha256": sha256(FREEZE),
    }
    result["content_sha256"] = content_hash(result)
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(OUTPUT, result["status"], f"{result['passed']}/{result['total']}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
