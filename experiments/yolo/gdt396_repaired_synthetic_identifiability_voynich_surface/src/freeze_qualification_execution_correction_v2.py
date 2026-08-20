#!/usr/bin/env python3
"""Freeze validator provenance for the GDT396 qualifier correction."""

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
OUTPUT = EXP / "artifacts/gdt396_qualification_execution_correction_freeze_v2.json"


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
    if (EXP / "artifacts/gdt396_decoder_qualification.json").exists():
        raise RuntimeError("qualification result must remain absent before V2 freeze")
    relative = [
        "QUALIFICATION_EXECUTION_CORRECTION.md",
        "QUALIFICATION_EXECUTION_VALIDATOR_PROVENANCE_CORRECTION.md",
        "src/qualify_decoders_v2.py",
        "src/freeze_qualification_execution_correction.py",
        "src/validate_qualification_execution_correction.py",
        "src/freeze_qualification_execution_correction_v2.py",
        "src/validate_qualification_execution_correction_v2.py",
        "artifacts/gdt396_qualification_execution_correction_freeze.json",
        "artifacts/gdt396_qualification_execution_correction_validation.json",
    ]
    bindings = {path: sha256(EXP / path) for path in relative}
    prior_freeze = json.loads((EXP / relative[-2]).read_text(encoding="utf-8"))
    prior_validation = json.loads((EXP / relative[-1]).read_text(encoding="utf-8"))
    if prior_validation.get("status") != "PASS" or prior_freeze.get("content_sha256") is None:
        raise RuntimeError("V1 correction lineage is not settled")
    result = {
        "schema": "GDT396_QUALIFICATION_EXECUTION_CORRECTION_FREEZE_V2",
        "status": "VALIDATOR_PROVENANCE_CORRECTION_FROZEN_BEFORE_REQUALIFICATION",
        "prior_freeze_sha256": bindings[relative[-2]],
        "prior_validation_sha256": bindings[relative[-1]],
        "metrics_sha256": prior_freeze["metrics_sha256"],
        "metrics_rows": prior_freeze["metrics_rows"],
        "qualification_result_absent_at_freeze": True,
        "scientific_logic_changed_from_v1": False,
        "bindings": bindings,
        "voynich_rows": 0,
        "f84": {"accessed": False, "rows": 0},
        "f84r": {"accessed": False, "rows": 0},
    }
    result["content_sha256"] = content_hash(result)
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(OUTPUT, sha256(OUTPUT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
