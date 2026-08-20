#!/usr/bin/env python3
"""Validate GDT396 qualifier correction validator provenance."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


def repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("repository root not found")


ROOT = repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt396_repaired_synthetic_identifiability_voynich_surface"
FREEZE = EXP / "artifacts/gdt396_qualification_execution_correction_freeze_v2.json"
OUTPUT = EXP / "artifacts/gdt396_qualification_execution_correction_validation_v2.json"


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
    checks["schema_status_content"] = (
        frozen.get("schema") == "GDT396_QUALIFICATION_EXECUTION_CORRECTION_FREEZE_V2"
        and frozen.get("status") == "VALIDATOR_PROVENANCE_CORRECTION_FROZEN_BEFORE_REQUALIFICATION"
        and frozen.get("content_sha256") == content_hash(frozen)
    )
    checks["bindings_exact"] = all(sha256(EXP / path) == digest for path, digest in frozen.get("bindings", {}).items())
    checks["self_validator_bound"] = frozen.get("bindings", {}).get("src/validate_qualification_execution_correction_v2.py") == sha256(Path(__file__).resolve())
    prior_freeze_path = EXP / "artifacts/gdt396_qualification_execution_correction_freeze.json"
    prior_validation_path = EXP / "artifacts/gdt396_qualification_execution_correction_validation.json"
    prior_freeze = json.loads(prior_freeze_path.read_text(encoding="utf-8"))
    prior_validation = json.loads(prior_validation_path.read_text(encoding="utf-8"))
    checks["prior_hashes"] = frozen.get("prior_freeze_sha256") == sha256(prior_freeze_path) and frozen.get("prior_validation_sha256") == sha256(prior_validation_path)
    checks["prior_content_and_pass"] = prior_freeze.get("content_sha256") == content_hash(prior_freeze) and prior_validation.get("content_sha256") == content_hash(prior_validation) and prior_validation.get("status") == "PASS" and prior_validation.get("passed") == prior_validation.get("total") == 13
    checks["prior_bindings_recursive"] = all(sha256(EXP / path) == digest for path, digest in prior_freeze.get("bindings", {}).items())
    checks["v1_validator_bound_by_v2"] = frozen.get("bindings", {}).get("src/validate_qualification_execution_correction.py") == sha256(EXP / "src/validate_qualification_execution_correction.py")
    checks["metrics_inherited_exact"] = frozen.get("metrics_sha256") == prior_freeze.get("metrics_sha256") and frozen.get("metrics_rows") == prior_freeze.get("metrics_rows") == 117100
    checks["qualification_still_absent"] = frozen.get("qualification_result_absent_at_freeze") is True and not (EXP / "artifacts/gdt396_decoder_qualification.json").exists()
    checks["no_scientific_change"] = frozen.get("scientific_logic_changed_from_v1") is False
    checks["seals"] = frozen.get("voynich_rows") == 0 and not frozen["f84"]["accessed"] and not frozen["f84r"]["accessed"]
    validator_hash = sha256(Path(__file__).resolve())
    result = {
        "schema": "GDT396_QUALIFICATION_EXECUTION_CORRECTION_VALIDATION_V2",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "passed": sum(checks.values()),
        "total": len(checks),
        "freeze_sha256": sha256(FREEZE),
        "validator_sha256": validator_hash,
    }
    result["content_sha256"] = content_hash(result)
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(OUTPUT, result["status"], f"{result['passed']}/{result['total']}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
