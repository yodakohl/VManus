#!/usr/bin/env python3
"""Freeze the narrow GDT396 post-oracle qualifier correction."""

from __future__ import annotations

import csv
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
METRICS = EXP / ".work/claims/gdt396_qualification_metrics.tsv"
RESULT = EXP / "artifacts/gdt396_decoder_qualification.json"
OUTPUT = EXP / "artifacts/gdt396_qualification_execution_correction_freeze.json"


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
    if not METRICS.is_file() or RESULT.exists():
        raise RuntimeError("requires completed metrics and absent qualification result")
    with METRICS.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    target = [
        row for row in rows
        if row["decoder_id"] == "D396S01"
        and row["property_id"] == "ALTERNATIVE_RELATION"
        and row["representation_id"] == "FULL_GROUP"
        and row["surface_id"] == "FREE_SURFACE"
        and row["world_id"] == "W10"
        and row["method_variant"] == "PRIMARY"
    ]
    if len(target) != 5 or {row["status"] for row in target} != {"UNSUPPORTED"}:
        raise RuntimeError("the observed unsupported-route failure is not reconstructed")
    relative = [
        "QUALIFICATION_EXECUTION_CORRECTION.md",
        "CLAIM_RETENTION_PLAN.md",
        "DECODER_QUALIFICATION_SPEC.md",
        "PREQUALIFICATION_W10_CORRECTION.md",
        "src/qualify_decoders.py",
        "src/qualify_decoders_v2.py",
        "src/freeze_qualification_execution_correction.py",
        "artifacts/gdt396_decoder_panel_freeze.json",
        "artifacts/gdt396_decoder_panel_validation.json",
        "artifacts/gdt396_qualification_claim_freeze.json",
        "artifacts/gdt396_qualification_corpus_validation.json",
    ]
    bindings = {path: sha256(EXP / path) for path in relative}
    result = {
        "schema": "GDT396_QUALIFICATION_EXECUTION_CORRECTION_FREEZE_V1",
        "status": "POST_ORACLE_QUALIFIER_ELIGIBILITY_CORRECTION_FROZEN_BEFORE_REQUALIFICATION",
        "metrics_sha256": sha256(METRICS),
        "metrics_rows": len(rows),
        "failed_qualifier_output_written": False,
        "qualification_oracle_opened_before_correction": True,
        "correction_scope": "ONLY_COMPLETE_FIVE_SEED_ALL_UNSUPPORTED_W10_ROUTES_SKIP_EVENT_RATE",
        "supported_routes_remain_fail_closed": True,
        "blind_claims_changed": False,
        "metrics_changed": False,
        "thresholds_changed": False,
        "confirmation_generated": False,
        "bindings": bindings,
        "voynich_rows": 0,
        "f84": {"accessed": False, "rows": 0},
        "f84r": {"accessed": False, "rows": 0},
    }
    result["content_sha256"] = content_hash(result)
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(OUTPUT, sha256(OUTPUT), len(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
