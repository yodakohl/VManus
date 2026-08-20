#!/usr/bin/env python3
"""Freeze the five oracle-blind GDT395 decoder implementations before use."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark"
OUT = EXP / "artifacts/gdt395_decoder_panel_freeze.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decoder_meta(path: Path) -> dict:
    tree = ast.parse(path.read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "DECODER_META" for target in node.targets):
            return ast.literal_eval(node.value)
    raise RuntimeError(f"DECODER_META missing in {path}")


def main() -> None:
    if OUT.exists():
        raise RuntimeError(f"refusing to overwrite existing decoder freeze: {OUT}")
    claim_root = EXP / ".work/claims"
    claim_file_count = sum(path.is_file() for path in claim_root.rglob("*")) if claim_root.exists() else 0
    if claim_file_count:
        raise RuntimeError("decoder claims already exist; pre-execution freeze is no longer possible")
    rows = []
    for directory in sorted((EXP / "decoders").glob("d[0-9][0-9]_*/")):
        source = directory / "decoder.py"
        attestation = directory / "ATTESTATION.md"
        if not source.is_file() or not attestation.is_file():
            raise RuntimeError(f"incomplete decoder directory: {directory}")
        meta = decoder_meta(source)
        rows.append({
            "directory": str(directory.relative_to(ROOT)),
            "source_sha256": sha(source),
            "attestation_sha256": sha(attestation),
            "meta": meta,
            "executed_before_freeze": False,
            "observation_rows_seen_by_designer": 0,
            "oracle_rows_seen_by_designer": 0,
        })
    if len(rows) != 5:
        raise RuntimeError(f"expected five decoders, got {len(rows)}")
    bindings = {}
    for relative in (
        "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark/DECODER_CONTRACT.md",
        "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark/DECODER_IMPLEMENTATION_API.md",
        "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark/src/decoder_api.py",
        "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark/artifacts/gdt395_interface_freeze.json",
        "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark/artifacts/gdt395_corpus_generation_audit.json",
        "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark/artifacts/gdt395_corpus_manifest.tsv",
        "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark/artifacts/gdt395_pair_blind_manifest.tsv",
        "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark/artifacts/gdt395_pair_protocol_amendment.json",
        "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark/src/freeze_decoder_panel.py",
        "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark/src/run_blind_decoders.py",
        "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark/src/validate_decoder_panel.py",
    ):
        bindings[relative] = sha(ROOT / relative)
    data = {
        "schema": "GDT395_DECODER_PANEL_FREEZE_V1",
        "status": "FROZEN_BEFORE_DECODER_EXECUTION",
        "decoders": rows,
        "bindings": bindings,
        "policy": {"sol_high_capacity": 2, "luna_replication": 3, "designers_excluded": True, "oracle_blind": True},
        "decoder_claims_generated": 0,
        "pre_execution_evidence": {
            "claim_root_file_count": claim_file_count,
            "freeze_output_absent_on_entry": True,
            "one_shot_overwrite_guard": True,
        },
        "oracle_scoring_performed": False,
        "voynich_rows": 0,
        "f84": {"opened": False, "parsed": False, "retained": False, "scored": False},
    }
    raw = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
    data["content_sha256"] = hashlib.sha256(raw).hexdigest()
    OUT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print({"status": data["status"], "decoders": len(rows)})


if __name__ == "__main__":
    main()
