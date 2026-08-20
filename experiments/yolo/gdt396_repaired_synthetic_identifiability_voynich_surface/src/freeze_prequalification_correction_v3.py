#!/usr/bin/env python3
"""Seal the final fail-closed W10 qualification correction."""

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
OUT = EXP / "artifacts/gdt396_prequalification_correction_freeze_v3.json"
EXPECTED_V2_DRIFT = {
    "src/freeze_decoder_panel.py", "src/qualify_decoders.py", "src/run.py",
    "src/test_instrument_contract.py", "src/validate.py", "src/validate_decoder_panel.py",
}


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
        raise RuntimeError("future observations already exist")
    v2_path = EXP / "artifacts/gdt396_prequalification_correction_freeze_v2.json"
    v2 = json.loads(v2_path.read_text(encoding="utf-8"))
    drift = [
        {"relpath": rel, "v2_sha256": digest, "v3_sha256": sha256(EXP / rel)}
        for rel, digest in v2["bindings"].items() if sha256(EXP / rel) != digest
    ]
    if {row["relpath"] for row in drift} != EXPECTED_V2_DRIFT:
        raise RuntimeError(f"unexpected V2 correction drift: {drift}")
    fixed = (
        "PREQUALIFICATION_W10_CORRECTION.md", "src/phase_authority.py",
        "src/generate_paired_corpora.py", "src/run_blind_decoders.py",
        "src/score_decoder_phase.py", "src/qualify_decoders.py", "src/freeze_claims.py",
        "src/validate_phase_corpora.py", "src/test_instrument_contract.py",
        "src/freeze_decoder_panel.py", "src/validate_decoder_panel.py", "src/run.py", "src/validate.py",
        "src/freeze_prequalification_correction_v3.py", "src/validate_prequalification_correction_v3.py",
        "artifacts/gdt396_prequalification_correction_freeze.json",
        "artifacts/gdt396_prequalification_correction_validation.json",
        "artifacts/gdt396_prequalification_correction_freeze_v2.json",
        "artifacts/gdt396_prequalification_correction_validation_v2.json",
        ".work/corpora/gdt396_legacy_paired_manifest_v2.tsv",
        ".work/corpora/gdt396_development_paired_manifest_v2.tsv",
    )
    result = {
        "schema": "GDT396_PREQUALIFICATION_CORRECTION_FREEZE_V3",
        "status": "FROZEN_BEFORE_QUALIFICATION_GENERATION",
        "v2_freeze_sha256": sha256(v2_path), "v2_postfreeze_drift": drift,
        "v3_reason": "require a complete five-seed W10 false-positive guard for every semantic qualification route",
        "qualification_observations_generated": False, "confirmation_observations_generated": False,
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
