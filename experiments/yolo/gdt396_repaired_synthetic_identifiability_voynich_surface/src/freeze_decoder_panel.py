#!/usr/bin/env python3
"""Freeze the GDT396 decoder/instrument panel before qualification generation."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt396_repaired_synthetic_identifiability_voynich_surface"
OUT = EXP / "artifacts/gdt396_decoder_panel_freeze.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def decoder_meta(path: Path) -> dict:
    spec = importlib.util.spec_from_file_location(f"gdt396_freeze_{path.parent.name}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return dict(module.DECODER_META)


def content_hash(value: dict) -> str:
    payload = dict(value); payload.pop("content_sha256", None)
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> int:
    if OUT.exists():
        raise RuntimeError(f"refusing to overwrite {OUT}")
    for block in ("qualification", "confirmation"):
        if (EXP / f".work/corpora/gdt396_{block}_paired_manifest.tsv").exists():
            raise RuntimeError(f"{block} observations already exist")
        if (EXP / f".work/corpora/gdt396_{block}_paired_manifest_v2.tsv").exists():
            raise RuntimeError(f"{block} corrected manifest already exists")

    protocol = EXP / "artifacts/gdt396_protocol_freeze.json"
    protocol_validation = EXP / "artifacts/gdt396_protocol_validation.json"
    development_validation = EXP / "artifacts/gdt396_development_corpus_validation.json"
    correction_validation = EXP / "artifacts/gdt396_prequalification_correction_validation_v3.json"
    if json.loads(correction_validation.read_text())["status"] != "PASS":
        raise RuntimeError("versioned prequalification correction is not PASS")

    fixed = [
        "CLAIM_INTERFACE.md", "CLAIM_RETENTION_PLAN.md", "DECODER_EXECUTION_SPEC.md", "DECODER_QUALIFICATION_SPEC.md",
        "METHOD.md", "ORACLE_TRUTH_SPEC.md", "PREQUALIFICATION_INSTRUMENT_CORRECTION.md", "PREQUALIFICATION_REAUDIT_CORRECTION.md", "PREQUALIFICATION_W10_CORRECTION.md", "README.md", "RUNNER_INTEGRATION_CORRECTION.md",
        "SCORING_DESIGN.md", "TRACE_DIGEST_CORRECTION.md", "VALIDATION_DESIGN.md",
        "src/decoder_api_v2.py", "src/freeze_claims.py", "src/freeze_decoder_panel.py",
        "src/generate_paired_corpora.py", "src/metrics.py", "src/observation_api.py",
        "src/merge_claim_manifests.py", "src/phase_authority.py", "src/qualify_decoders.py", "src/repair_trace_manifests.py",
        "src/run.py", "src/run_blind_decoders.py", "src/score_decoder_phase.py", "src/surface_channel.py",
        "src/test_instrument_contract.py", "src/freeze_prequalification_correction.py",
        "src/validate.py", "src/validate_decoder_panel.py", "src/validate_paired_corpora.py", "src/validate_phase_corpora.py",
        "src/validate_prequalification_correction.py", "src/freeze_prequalification_correction_v2.py",
        "src/validate_prequalification_correction_v2.py", "src/freeze_prequalification_correction_v3.py",
        "src/validate_prequalification_correction_v3.py",
        "artifacts/gdt396_protocol_freeze.json", "artifacts/gdt396_protocol_validation.json",
        "artifacts/gdt396_development_corpus_validation.json",
        "artifacts/gdt396_prequalification_correction_freeze.json",
        "artifacts/gdt396_prequalification_correction_validation.json",
        "artifacts/gdt396_prequalification_correction_freeze_v2.json",
        "artifacts/gdt396_prequalification_correction_validation_v2.json",
        "artifacts/gdt396_prequalification_correction_freeze_v3.json",
        "artifacts/gdt396_prequalification_correction_validation_v3.json",
        ".work/corpora/gdt396_legacy_paired_manifest_v2.tsv",
        ".work/corpora/gdt396_development_paired_manifest_v2.tsv",
    ]
    review = EXP / "DECODER_PANEL_REVIEW.md"
    if not review.is_file():
        raise RuntimeError("independent decoder-panel review is absent")
    if "Final decision: **GO**" not in review.read_text(encoding="utf-8"):
        raise RuntimeError("independent decoder-panel review has not issued final GO")
    fixed.append("DECODER_PANEL_REVIEW.md")

    decoders = []
    for path in sorted((EXP / "decoders").glob("*/decoder.py")):
        meta = decoder_meta(path)
        attestation = path.with_name("ATTESTATION.md")
        if not attestation.is_file():
            raise RuntimeError(f"missing attestation for {path}")
        if meta.get("api_version") != 2 or meta.get("oracle_blind") is not True or meta.get("fit_scope") != "TRAIN_ONLY_WORLD":
            raise RuntimeError(f"invalid decoder metadata in {path}")
        decoders.append({
            "decoder_id": meta["decoder_id"], "designer_model": meta["designer_model"],
            "method_family": meta["method_family"],
            "supported_representations": meta["supported_representations"],
            "decoder_relpath": str(path.relative_to(EXP)), "decoder_sha256": sha256(path),
            "attestation_relpath": str(attestation.relative_to(EXP)), "attestation_sha256": sha256(attestation),
        })
    if len(decoders) < 4 or len({row["method_family"] for row in decoders}) < 4:
        raise RuntimeError("at least four independent method families are required")
    if len({row["decoder_id"] for row in decoders}) != len(decoders):
        raise RuntimeError("duplicate decoder IDs")

    bindings = {rel: sha256(EXP / rel) for rel in fixed}
    freeze = {
        "schema": "GDT396_DECODER_PANEL_FREEZE_V1", "status": "FROZEN_BEFORE_QUALIFICATION_GENERATION",
        "protocol_freeze_sha256": sha256(protocol), "mapping_salt_commitment": json.loads(protocol.read_text())["mapping_salt_commitment"],
        "qualification_observations_generated": False, "confirmation_observations_generated": False,
        "decoder_count": len(decoders), "method_family_count": len({row["method_family"] for row in decoders}),
        "decoders": decoders, "bindings": bindings,
        "oracle_exposed_to_decoders": False, "voynich_corpus_files_opened": 0, "voynich_rows": 0,
        "f84": {"allowed": False, "opened": False, "rows": 0},
        "f84r": {"allowed": False, "opened": False, "rows": 0},
    }
    freeze["content_sha256"] = content_hash(freeze)
    OUT.write_text(json.dumps(freeze, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(OUT, sha256(OUT), freeze["content_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
