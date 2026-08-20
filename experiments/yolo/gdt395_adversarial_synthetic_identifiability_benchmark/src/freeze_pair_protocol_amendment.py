#!/usr/bin/env python3
"""Freeze the pre-decoding correction to the GDT395 adversarial pair view."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark"
OUT = EXP / "artifacts/gdt395_pair_protocol_amendment.json"


def sha(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def main() -> None:
    paths = {
        "original_interface": "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark/artifacts/gdt395_interface_freeze.json",
        "amended_method": "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark/METHOD.md",
        "amendment": "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark/PAIR_PROTOCOL_AMENDMENT.md",
        "selector": "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark/src/build_pair_matched_subpanels.py",
        "pair_view": "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark/src/build_pair_blind_views.py",
        "pair_view_validator": "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark/src/validate_pair_blind_views.py",
        "matches": "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark/artifacts/gdt395_pair_matched_records.tsv",
        "audit": "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark/artifacts/gdt395_pair_matching_audit.tsv",
    }
    interface = json.loads((ROOT / paths["original_interface"]).read_text())
    data = {
        "schema": "GDT395_PAIR_PROTOCOL_AMENDMENT_V1",
        "status": "FROZEN_BEFORE_CORPUS_GENERATION_AND_DECODING",
        "chronology": "CORRECTED_AFTER_INDEPENDENT_CARRIER_AUDIT_BEFORE_ANY_DECODER_DESIGN_OR_EXPOSURE",
        "original_method_sha256": interface["hashes"]["experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark/METHOD.md"],
        "bindings": {name: {"path": path, "sha256": sha(path)} for name, path in paths.items()},
        "pair_view_scope": "RECORD_LINE_LOCAL_ONLY",
        "records_per_world_seed": 10,
        "recurrence_difference_gate": 0.10,
        "exact_match_channels": ["RECORD_LENGTH", "ORDERED_LINE_PROFILE", "WITHIN_RECORD_SEPARATOR_HISTOGRAM", "AMBIGUITY_COUNT"],
        "masked_noncomparable_channels": ["PAGE", "PARAGRAPH", "REGISTER", "HAND", "LAYOUT", "GLYPH_INTERNAL"],
        "authentic_main_corpora_changed": False,
        "oracle_read_by_pair_freezer": False,
        "voynich_rows": 0,
        "f84": {"opened": False, "parsed": False, "retained": False, "scored": False},
    }
    raw = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
    data["content_sha256"] = hashlib.sha256(raw).hexdigest()
    OUT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print({"status": data["status"], "pair_scope": data["pair_view_scope"]})


if __name__ == "__main__":
    main()
