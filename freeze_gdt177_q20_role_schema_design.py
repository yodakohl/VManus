#!/usr/bin/env python3
"""Freeze the GDT177 design and input hashes before source-native scoring."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

FILES = (
    "GDT177_Q20_ROLE_SCHEMA_VALIDATION_METHOD.md",
    "gdt176_result.json",
    "gdt176_q20_role_like_projection.tsv",
    "gdt127_q20_field_inventory.tsv",
)

def sha(p: str) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

design = {
    "experiment": "GDT177_Q20_ROLE_SCHEMA_VALIDATION",
    "status": "FROZEN_BEFORE_UNUSED_Q20_FEATURE_SCORING",
    "primary_edition": "ZL3b",
    "alternate_readings": ["IT2a", "RF1b"],
    "tests": ["T1_FINAL_FIELD_B3", "T2_CROSS_FOLIO_HOST_RECURRENCE", "T3_COMPILER_STATE_DENSITY", "T4_HELD_FOLIO_HOST_ROLE_UPDATE"],
    "permutation_worlds": 4096,
    "permutation_seed": 17720260817,
    "host_update_pseudocount": 4,
    "inputs": {p: sha(p) for p in FILES},
    "f84r_accessed": False,
    "claim_ceiling": "source-native abstract record-schema association only; no word role meaning language plaintext or translation",
}
payload = json.dumps(design, sort_keys=True, separators=(",", ":")).encode()
design["content_hash"] = hashlib.sha256(payload).hexdigest()
Path("gdt177_design.json").write_text(json.dumps(design, indent=2, sort_keys=True) + "\n")
print(design["content_hash"])
