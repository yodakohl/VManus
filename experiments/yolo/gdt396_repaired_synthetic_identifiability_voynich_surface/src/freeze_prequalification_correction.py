#!/usr/bin/env python3
"""Seal the disclosed GDT396 prequalification implementation correction."""

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
OUT = EXP / "artifacts/gdt396_prequalification_correction_freeze.json"
DRIFT = ("src/decoder_api_v2.py", "src/generate_paired_corpora.py")


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
    if OUT.exists():
        raise RuntimeError(f"refusing to overwrite {OUT}")
    if any((EXP / f".work/corpora/gdt396_{block}_paired_manifest_v2.tsv").exists() for block in ("qualification", "confirmation")):
        raise RuntimeError("qualification/confirmation observations already exist")
    protocol_path = EXP / "artifacts/gdt396_protocol_freeze.json"
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    differences = []
    for relpath, expected in sorted(protocol["protocol_hashes"].items()):
        actual = sha256(EXP / relpath)
        if actual != expected:
            differences.append({"relpath": relpath, "frozen_sha256": expected, "corrected_sha256": actual})
    if tuple(row["relpath"] for row in differences) != DRIFT:
        raise RuntimeError(f"unexpected protocol drift: {differences}")
    old_protocol_validation = json.loads((EXP / "artifacts/gdt396_protocol_validation.json").read_text())
    old_corpus_validation = json.loads((EXP / "artifacts/gdt396_development_corpus_validation.json").read_text())
    if old_protocol_validation.get("status") != "FAIL" or [k for k, v in old_protocol_validation["checks"].items() if not v] != ["protocol_hashes"]:
        raise RuntimeError("historical protocol failure is not the disclosed single check")
    if old_corpus_validation.get("status") != "FAIL" or [k for k, v in old_corpus_validation["checks"].items() if not v] != ["protocol_valid"]:
        raise RuntimeError("historical corpus failure is not protocol-validation-only")
    fixed = (
        "PREQUALIFICATION_INSTRUMENT_CORRECTION.md", "RUNNER_INTEGRATION_CORRECTION.md",
        "src/decoder_api_v2.py", "src/generate_paired_corpora.py",
        "src/freeze_prequalification_correction.py", "src/validate_prequalification_correction.py",
        "src/test_instrument_contract.py", "artifacts/gdt396_protocol_freeze.json",
        "artifacts/gdt396_protocol_validation.json", "artifacts/gdt396_development_corpus_validation.json",
        ".work/corpora/gdt396_legacy_paired_manifest_v2.tsv",
        ".work/corpora/gdt396_development_paired_manifest_v2.tsv",
    )
    result = {
        "schema": "GDT396_PREQUALIFICATION_CORRECTION_FREEZE_V1",
        "status": "FROZEN_BEFORE_QUALIFICATION_GENERATION",
        "original_protocol_freeze_sha256": sha256(protocol_path),
        "disclosed_protocol_drift": differences,
        "drift_reasons": {
            "src/decoder_api_v2.py": "reject string truth values and require Python booleans before canonical TSV serialization",
            "src/generate_paired_corpora.py": "enforce decoder-panel and confirmation-instrument phase authority before untouched block generation",
        },
        "scientific_surface_contract_changed": False,
        "hidden_worlds_or_generators_changed": False,
        "legacy_or_development_corpora_regenerated": False,
        "qualification_observations_generated": False,
        "confirmation_observations_generated": False,
        "bindings": {rel: sha256(EXP / rel) for rel in fixed},
        "voynich_corpus_files_opened": 0, "voynich_rows": 0,
        "f84": {"allowed": False, "opened": False, "rows": 0},
        "f84r": {"allowed": False, "opened": False, "rows": 0},
    }
    result["content_sha256"] = content_hash(result)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(OUT, sha256(OUT), result["content_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
