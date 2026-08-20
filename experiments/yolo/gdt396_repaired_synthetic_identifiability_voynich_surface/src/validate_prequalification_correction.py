#!/usr/bin/env python3
"""Independently validate the GDT396 versioned prequalification correction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt396_repaired_synthetic_identifiability_voynich_surface"
FREEZE = EXP / "artifacts/gdt396_prequalification_correction_freeze.json"
OUT = EXP / "artifacts/gdt396_prequalification_correction_validation.json"
EXPECTED_DRIFT = {"src/decoder_api_v2.py", "src/generate_paired_corpora.py"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def content_hash(value: dict) -> str:
    clean = dict(value); clean.pop("content_sha256", None)
    return hashlib.sha256(json.dumps(clean, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> int:
    frozen = json.loads(FREEZE.read_text(encoding="utf-8"))
    protocol_path = EXP / "artifacts/gdt396_protocol_freeze.json"
    protocol = json.loads(protocol_path.read_text())
    protocol_validation = json.loads((EXP / "artifacts/gdt396_protocol_validation.json").read_text())
    corpus_validation = json.loads((EXP / "artifacts/gdt396_development_corpus_validation.json").read_text())
    drift = frozen.get("disclosed_protocol_drift", [])
    actual_drift = {
        rel for rel, expected in protocol["protocol_hashes"].items()
        if sha256(EXP / rel) != expected
    }
    checks = {
        "schema_status": frozen.get("schema") == "GDT396_PREQUALIFICATION_CORRECTION_FREEZE_V1" and frozen.get("status") == "FROZEN_BEFORE_QUALIFICATION_GENERATION",
        "content_hash": frozen.get("content_sha256") == content_hash(frozen),
        "original_protocol_bound": frozen.get("original_protocol_freeze_sha256") == sha256(protocol_path),
        "exact_drift_set": actual_drift == EXPECTED_DRIFT == {row.get("relpath") for row in drift},
        "drift_hashes_exact": all(row.get("frozen_sha256") == protocol["protocol_hashes"].get(row.get("relpath")) and row.get("corrected_sha256") == sha256(EXP / row["relpath"]) for row in drift),
        "all_bindings": all((EXP / rel).is_file() and sha256(EXP / rel) == expected for rel, expected in frozen.get("bindings", {}).items()),
        "historical_protocol_failure_narrow": protocol_validation.get("status") == "FAIL" and [k for k, v in protocol_validation["checks"].items() if not v] == ["protocol_hashes"],
        "corpus_science_passes": corpus_validation.get("status") == "FAIL" and all(v for k, v in corpus_validation["checks"].items() if k != "protocol_valid") and corpus_validation["checks"].get("protocol_valid") is False,
        "surface_and_worlds_unchanged": frozen.get("scientific_surface_contract_changed") is False and frozen.get("hidden_worlds_or_generators_changed") is False and frozen.get("legacy_or_development_corpora_regenerated") is False,
        "future_blocks_absent": not any((EXP / f".work/corpora/gdt396_{block}_paired_manifest_v2.tsv").exists() for block in ("qualification", "confirmation")),
        "seals": frozen.get("f84", {}).get("opened") is False and frozen.get("f84r", {}).get("opened") is False and frozen.get("voynich_rows") == 0,
    }
    result = {
        "schema": "GDT396_PREQUALIFICATION_CORRECTION_VALIDATION_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks, "checks_passed": sum(checks.values()), "checks_total": len(checks),
        "freeze_sha256": sha256(FREEZE), "validator_sha256": sha256(Path(__file__)),
        "voynich_corpus_files_opened": 0, "voynich_rows": 0,
        "f84": {"allowed": False, "opened": False, "rows": 0},
        "f84r": {"allowed": False, "opened": False, "rows": 0},
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
