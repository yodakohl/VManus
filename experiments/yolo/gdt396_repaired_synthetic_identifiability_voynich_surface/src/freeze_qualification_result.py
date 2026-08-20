#!/usr/bin/env python3
"""Freeze the settled negative GDT396 qualification result."""

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
OUTPUT = EXP / "artifacts/gdt396_result_freeze.json"


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
    confirmation_patterns = [
        EXP / "artifacts/gdt396_confirmation_claim_freeze.json",
        EXP / "artifacts/gdt396_confirmation_result.json",
        EXP / ".work/corpora/gdt396_confirmation_paired_manifest_v2.tsv",
        EXP / ".work/claims/gdt396_confirmation_claim_manifest.tsv",
        EXP / ".work/claims/gdt396_confirmation_metrics.tsv",
    ]
    if any(path.exists() for path in confirmation_patterns):
        raise RuntimeError("confirmation artifacts must remain absent")
    result = json.loads((EXP / "artifacts/gdt396_result.json").read_text(encoding="utf-8"))
    qualification = json.loads((EXP / "artifacts/gdt396_decoder_qualification.json").read_text(encoding="utf-8"))
    if result.get("status") != "NO_CONFIRMATION_ELIGIBLE_PROPERTY" or qualification.get("status") != "NO_CONFIRMATION_ELIGIBLE_PROPERTY":
        raise RuntimeError("qualification stop is not settled")
    relative = [
        "GDT396_REPAIRED_SYNTHETIC_IDENTIFIABILITY_REPORT.md",
        "QUALIFICATION_RESULT_METHOD.md",
        "QUALIFICATION_RESULT_EXECUTION_CORRECTION.md",
        "src/run_v2.py",
        "src/build_qualification_outputs.py",
        "src/freeze_qualification_result.py",
        "src/validate_qualification_result.py",
        "artifacts/gdt396_decoder_qualification.json",
        "artifacts/gdt396_qualification_identifiability_matrix.tsv.gz",
        "artifacts/gdt396_qualification_route_matrix.tsv",
        "artifacts/gdt396_property_decisions.tsv",
        "artifacts/gdt396_result.json",
        "artifacts/gdt396_qualification_execution_correction_freeze_v2.json",
        "artifacts/gdt396_qualification_execution_correction_validation_v2.json",
    ]
    bindings = {path: sha256(EXP / path) for path in relative}
    frozen = {
        "schema": "GDT396_RESULT_FREEZE_V1",
        "status": "NO_CONFIRMATION_ELIGIBLE_PROPERTY_FROZEN",
        "qualification_metrics_sha256": result["qualification_metrics_sha256"],
        "qualification_metrics_rows": result["qualification_metrics_rows"],
        "qualification_result_sha256": bindings["artifacts/gdt396_decoder_qualification.json"],
        "result_sha256": bindings["artifacts/gdt396_result.json"],
        "confirmation_generated": False,
        "confirmation_artifacts_absent_at_freeze": True,
        "bindings": bindings,
        "voynich_rows": 0,
        "f84": {"accessed": False, "rows": 0},
        "f84r": {"accessed": False, "rows": 0},
    }
    frozen["content_sha256"] = content_hash(frozen)
    OUTPUT.write_text(json.dumps(frozen, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(OUTPUT, sha256(OUTPUT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
