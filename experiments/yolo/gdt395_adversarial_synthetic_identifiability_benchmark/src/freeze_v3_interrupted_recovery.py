#!/usr/bin/env python3
"""Freeze the exact interrupted GDT395 V3 claim state before recovery."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark"
CLAIMS = EXP / ".work/claims"
DECODER_FREEZE = EXP / "artifacts/gdt395_decoder_panel_freeze.json"
PAIR_MANIFEST = EXP / "artifacts/gdt395_pair_blind_manifest.tsv"
OUT = EXP / "artifacts/gdt395_v3_interruption_recovery_freeze.json"
REPS = (
    "FULL_GROUP", "HOST_LIKE", "COMPOSITE_STATE", "INFERRED_COMPONENTS",
    "CONSTRUCTION_SPAN", "RECORD_TOPOLOGY",
)
HELD = range(15, 20)
WORLDS = tuple(f"W{i:02d}" for i in range(1, 11))
MISSING = "world_claims/W05/D01_MULTIVIEW_GRAPH/train_seeds_00_14.json"


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def main() -> None:
    if OUT.exists():
        raise RuntimeError("refusing to overwrite recovery freeze")
    if (CLAIMS / "blind_claim_manifest_all.tsv").exists():
        raise RuntimeError("authoritative claim manifest already exists")
    decoder_freeze = json.loads(DECODER_FREEZE.read_text())
    decoders = tuple(sorted(row["meta"]["decoder_id"] for row in decoder_freeze["decoders"]))
    with PAIR_MANIFEST.open(newline="", encoding="utf-8") as handle:
        pair_rows = list(csv.DictReader(handle, delimiter="\t"))
    pairs = tuple(sorted({(row["pair_id"], row["world_id"]) for row in pair_rows}))
    expected_events = set()
    for world in WORLDS:
        for decoder in decoders:
            for seed in HELD:
                for rep in REPS:
                    expected_events.add(
                        f"authentic/{world}/{decoder}/seed_{seed:02d}_{rep}.tsv.gz"
                    )
    for pair_id, world in pairs:
        for decoder in decoders:
            for seed in HELD:
                for rep in REPS:
                    expected_events.add(
                        f"pair/{pair_id}/{world}/{decoder}/seed_{seed:02d}_{rep}.tsv.gz"
                    )
    expected_world = {
        f"world_claims/{world}/{decoder}/train_seeds_00_14.json"
        for world in WORLDS for decoder in decoders
    }
    actual = {
        path.relative_to(CLAIMS).as_posix()
        for path in CLAIMS.rglob("*") if path.is_file()
    }
    expected_pre = expected_events | (expected_world - {MISSING})
    if actual != expected_pre or len(expected_events) != 2100 or len(expected_pre) != 2149:
        raise RuntimeError("interrupted claim prestate is not the frozen recovery state")
    hashes = {rel: sha(CLAIMS / rel) for rel in sorted(actual)}
    bindings = {}
    for rel in (
        "INTERRUPTION_RECOVERY.md",
        "artifacts/gdt395_corpus_manifest.tsv",
        "artifacts/gdt395_pair_blind_manifest.tsv",
        "artifacts/gdt395_decoder_panel_freeze.json",
        "artifacts/gdt395_decoder_execution_v3_correction.json",
        "src/run_blind_decoders.py",
        "src/run_blind_decoders_v2.py",
        "src/run_blind_decoders_v3.py",
        "src/freeze_v3_interrupted_recovery.py",
        "src/recover_v3_interrupted_completion.py",
        "src/validate_v3_interrupted_completion.py",
        "decoders/d01_multiview_graph/decoder.py",
    ):
        bindings[rel] = sha(EXP / rel)
    data = {
        "schema": "GDT395_V3_INTERRUPTION_RECOVERY_FREEZE_V1",
        "status": "FROZEN_BEFORE_RECOVERY_EXECUTION",
        "reason": "EXTERNAL_CONNECTION_INTERRUPTION_AFTER_EVENT_CLAIMS_BEFORE_FINAL_WORLD_CLAIM_AND_MANIFEST",
        "event_claim_files": 2100,
        "world_claim_files": 49,
        "total_claim_files": 2149,
        "sole_missing_claim": MISSING,
        "prestate_claim_map_sha256": canonical_hash(hashes),
        "bindings": bindings,
        "checks": {
            "all_event_claims_present": True,
            "one_world_claim_missing": True,
            "authoritative_manifest_absent": True,
            "recovery_source_bound": True,
            "oracle_opened": False,
            "voynich_rows": 0,
            "f84_opened": False,
        },
    }
    data["content_sha256"] = canonical_hash(data)
    OUT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": data["status"], "claim_files": len(actual)}, sort_keys=True))


if __name__ == "__main__":
    main()

