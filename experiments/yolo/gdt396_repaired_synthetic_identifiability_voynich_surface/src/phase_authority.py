#!/usr/bin/env python3
"""Action-time authentication of frozen GDT396 phase instruments."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def content_hash(value: dict) -> str:
    clean = dict(value); clean.pop("content_sha256", None)
    return hashlib.sha256(json.dumps(clean, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def require_instrument(exp: Path, phase: str) -> dict:
    """Reject a stale PASS artifact or any post-freeze bound-file drift."""
    normalized = phase.upper()
    if normalized == "DEVELOPMENT":
        return {}
    stem = "decoder_panel" if normalized == "QUALIFICATION" else "confirmation_instrument"
    freeze_path = exp / f"artifacts/gdt396_{stem}_freeze.json"
    validation_path = exp / f"artifacts/gdt396_{stem}_validation.json"
    if not freeze_path.is_file() or not validation_path.is_file():
        raise RuntimeError(f"{normalized} instrument authority is absent")
    frozen = json.loads(freeze_path.read_text(encoding="utf-8"))
    validation = json.loads(validation_path.read_text(encoding="utf-8"))
    if validation.get("status") != "PASS" or validation.get("freeze_sha256") != sha256(freeze_path):
        raise RuntimeError(f"{normalized} instrument validation is stale or not PASS")
    if frozen.get("content_sha256") != content_hash(frozen):
        raise RuntimeError(f"{normalized} instrument content hash failed")
    for relpath, expected in frozen.get("bindings", {}).items():
        path = exp / relpath
        if not path.is_file() or sha256(path) != expected:
            raise RuntimeError(f"{normalized} instrument binding drift: {relpath}")
    for decoder in frozen.get("decoders", []):
        for path_key, hash_key in (("decoder_relpath", "decoder_sha256"), ("attestation_relpath", "attestation_sha256")):
            path = exp / decoder[path_key]
            if not path.is_file() or sha256(path) != decoder[hash_key]:
                raise RuntimeError(f"{normalized} decoder binding drift: {path}")
    return frozen
