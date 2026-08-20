#!/usr/bin/env python3
"""Freeze GDT395 decoder claims before any sealed truth is opened."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark"
CLAIMS = EXP / ".work/claims"
MANIFEST = CLAIMS / "blind_claim_manifest_all.tsv"
OUT = EXP / "artifacts/gdt395_blind_claims_freeze.json"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    with MANIFEST.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    if len(rows) != 2150:
        raise RuntimeError(f"expected 2150 claim files, got {len(rows)}")
    for row in rows:
        path = CLAIMS / row["claim_relpath"]
        if not path.is_file() or sha(path) != row["claim_sha256"]:
            raise RuntimeError(f"claim hash mismatch: {path}")
    bindings = {}
    for rel in (
        "artifacts/gdt395_decoder_panel_freeze.json",
        "artifacts/gdt395_decoder_panel_validation.json",
        "artifacts/gdt395_corpus_manifest.tsv",
        "artifacts/gdt395_pair_blind_manifest.tsv",
        "src/decoder_api.py",
        "src/run_blind_decoders.py",
        "src/freeze_blind_claims.py",
        "src/validate_blind_claims.py",
    ):
        bindings[rel] = sha(EXP / rel)
    data = {
        "schema": "GDT395_BLIND_CLAIMS_FREEZE_V1",
        "status": "BLIND_CLAIMS_FROZEN_BEFORE_ORACLE_ACCESS",
        "claim_file_count": len(rows),
        "event_claim_file_count": sum(r["mode"] != "world_claim" for r in rows),
        "world_claim_file_count": sum(r["mode"] == "world_claim" for r in rows),
        "claim_manifest_sha256": sha(MANIFEST),
        "bindings": bindings,
        "oracle_opened": False,
        "oracle_rows_read": 0,
        "voynich_rows": 0,
        "f84": {"opened": False, "parsed": False, "retained": False, "scored": False},
    }
    raw = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
    data["content_sha256"] = hashlib.sha256(raw).hexdigest()
    OUT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": data["status"], "claim_files": len(rows)}, sort_keys=True))


if __name__ == "__main__":
    main()
