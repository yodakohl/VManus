#!/usr/bin/env python3
"""Authoritative GDT396 runner with corrected qualification dispatch."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import run as legacy


EXP = legacy.EXP
SRC = legacy.SRC
PY = legacy.PY


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


def require_correction() -> None:
    freeze_path = EXP / "artifacts/gdt396_qualification_execution_correction_freeze_v2.json"
    validation_path = EXP / "artifacts/gdt396_qualification_execution_correction_validation_v2.json"
    frozen = json.loads(freeze_path.read_text(encoding="utf-8"))
    validation = json.loads(validation_path.read_text(encoding="utf-8"))
    if (
        frozen.get("schema") != "GDT396_QUALIFICATION_EXECUTION_CORRECTION_FREEZE_V2"
        or frozen.get("content_sha256") != content_hash(frozen)
        or validation.get("schema") != "GDT396_QUALIFICATION_EXECUTION_CORRECTION_VALIDATION_V2"
        or validation.get("status") != "PASS"
        or validation.get("content_sha256") != content_hash(validation)
        or validation.get("freeze_sha256") != sha256(freeze_path)
        or validation.get("validator_sha256") != sha256(SRC / "validate_qualification_execution_correction_v2.py")
    ):
        raise RuntimeError("qualification correction lineage is invalid")
    for relpath, expected in frozen.get("bindings", {}).items():
        if sha256(EXP / relpath) != expected:
            raise RuntimeError(f"qualification correction binding drift: {relpath}")


def score_qualification() -> int:
    require_correction()
    claim_freeze = json.loads((EXP / "artifacts/gdt396_qualification_claim_freeze.json").read_text(encoding="utf-8"))
    if claim_freeze.get("status") != "FROZEN_BEFORE_ORACLE_SCORING":
        raise RuntimeError("qualification claims are not frozen")
    metrics = EXP / ".work/claims/gdt396_qualification_metrics.tsv"
    result = EXP / "artifacts/gdt396_decoder_qualification.json"
    if not metrics.exists():
        legacy.call([PY, str(SRC / "score_decoder_phase.py"), "--phase", "QUALIFICATION"])
    if not result.exists():
        legacy.call([PY, str(SRC / "qualify_decoders_v2.py")])
    settled = json.loads(result.read_text(encoding="utf-8"))
    if (
        settled.get("schema") != "GDT396_DECODER_QUALIFICATION_V1"
        or settled.get("content_sha256") != content_hash(settled)
        or settled.get("metrics_sha256") != sha256(metrics)
    ):
        raise RuntimeError("settled qualification result is invalid")
    print(json.dumps({"schema": "GDT396_RUN_V2_QUALIFICATION", "status": settled["status"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "score-qualification":
        raise SystemExit(score_qualification())
    raise SystemExit(legacy.main())
