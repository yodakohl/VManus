#!/usr/bin/env python3
"""Recover one missing train-only world claim and the final V3 manifest."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark"
SRC = EXP / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
import run_blind_decoders as v1

CLAIMS = EXP / ".work/claims"
FREEZE = EXP / "artifacts/gdt395_v3_interruption_recovery_freeze.json"
RESULT = EXP / "artifacts/gdt395_v3_interruption_recovery_result.json"
MANIFEST = CLAIMS / "blind_claim_manifest_all.tsv"
MISSING = Path("world_claims/W05/D01_MULTIVIEW_GRAPH/train_seeds_00_14.json")
REPS = tuple(v1.REPRESENTATIONS)
HELD = tuple(v1.HELD_SEEDS)


def sha(path: Path) -> str:
    return v1.sha(path)


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def claim_map() -> dict[str, str]:
    return {
        path.relative_to(CLAIMS).as_posix(): sha(path)
        for path in sorted(CLAIMS.rglob("*")) if path.is_file() and path != MANIFEST
    }


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("gdt395_recovery_d01", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen D01 decoder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def rows_in_gzip(path: Path) -> int:
    import gzip
    with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    if RESULT.exists() or MANIFEST.exists() or (CLAIMS / MISSING).exists():
        raise RuntimeError("recovery outputs already exist")
    freeze = json.loads(FREEZE.read_text())
    tmp = dict(freeze)
    expected = tmp.pop("content_sha256")
    if canonical_hash(tmp) != expected or freeze["status"] != "FROZEN_BEFORE_RECOVERY_EXECUTION":
        raise RuntimeError("recovery freeze is invalid")
    for rel, digest in freeze["bindings"].items():
        if sha(EXP / rel) != digest:
            raise RuntimeError("recovery binding changed")
    before = claim_map()
    if len(before) != 2149 or canonical_hash(before) != freeze["prestate_claim_map_sha256"]:
        raise RuntimeError("claim prestate changed after recovery freeze")

    # Authenticate every observation input before loading even one training row.
    # This preserves the same input gate as the frozen V3 runner and makes the
    # narrow recovery fail closed if either public manifest or blind packet moved.
    corpus = v1.manifest_rows(v1.CORPUS_MANIFEST)
    pairs = v1.manifest_rows(v1.PAIR_MANIFEST)
    v1.validate_observation_inputs(corpus, pairs)

    decoder_freeze = json.loads((EXP / "artifacts/gdt395_decoder_panel_freeze.json").read_text())
    row = next(item for item in decoder_freeze["decoders"]
               if item["meta"]["decoder_id"] == "D01_MULTIVIEW_GRAPH")
    decoder_path = ROOT / row["directory"] / "decoder.py"
    if sha(decoder_path) != row["source_sha256"]:
        raise RuntimeError("D01 decoder hash changed")
    module = load_module(decoder_path)
    if module.DECODER_META != row["meta"]:
        raise RuntimeError("D01 decoder metadata changed")
    train_rows = []
    for seed in v1.TRAIN_SEEDS:
        train_rows.extend(v1.corpus_rows("authentic", "", "W05", seed))
    claim = module.classify_world(train_rows)
    _, world_fields, _ = v1.claim_api()
    if set(claim) != set(world_fields) or claim["decoder_id"] != "D01_MULTIVIEW_GRAPH":
        raise RuntimeError("recovered world claim violates frozen schema")
    confidence = float(claim["confidence"])
    if not 0.0 <= confidence <= 1.0:
        raise RuntimeError("recovered world-claim confidence outside [0,1]")
    target = CLAIMS / MISSING
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(claim, indent=2, sort_keys=True) + "\n")

    corpus_events = {(r["world_id"], int(r["corpus_seed"])): int(r["events"]) for r in corpus}
    pair_events = {
        (r["pair_id"], r["world_id"], int(r["corpus_seed"])): int(r["events"])
        for r in pairs
    }
    decoders = tuple(sorted(item["meta"]["decoder_id"] for item in decoder_freeze["decoders"]))
    outputs = []
    for world in sorted({r["world_id"] for r in corpus}):
        for seed in HELD:
            for decoder in decoders:
                for rep in REPS:
                    rel = Path("authentic") / world / decoder / f"seed_{seed:02d}_{rep}.tsv.gz"
                    path = CLAIMS / rel
                    outputs.append({
                        "mode": "authentic", "pair_id": "NONE", "world_id": world,
                        "held_seed": seed, "decoder_id": decoder, "representation": rep,
                        "events": corpus_events[(world, seed)], "claim_relpath": rel.as_posix(),
                        "claim_sha256": sha(path),
                    })
    for pair_id, world in sorted({(r["pair_id"], r["world_id"]) for r in pairs}):
        for seed in HELD:
            for decoder in decoders:
                for rep in REPS:
                    rel = Path("pair") / pair_id / world / decoder / f"seed_{seed:02d}_{rep}.tsv.gz"
                    path = CLAIMS / rel
                    outputs.append({
                        "mode": "pair", "pair_id": pair_id, "world_id": world,
                        "held_seed": seed, "decoder_id": decoder, "representation": rep,
                        "events": pair_events[(pair_id, world, seed)], "claim_relpath": rel.as_posix(),
                        "claim_sha256": sha(path),
                    })
    for world in sorted({r["world_id"] for r in corpus}):
        for decoder in decoders:
            rel = Path("world_claims") / world / decoder / "train_seeds_00_14.json"
            outputs.append({
                "mode": "world_claim", "pair_id": "NONE", "world_id": world,
                "held_seed": "NONE", "decoder_id": decoder,
                "representation": "ALL_TRAIN_OBSERVATIONS", "events": 1,
                "claim_relpath": rel.as_posix(), "claim_sha256": sha(CLAIMS / rel),
            })
    outputs.sort(key=lambda item: (
        item["mode"], item["pair_id"], item["world_id"],
        -1 if item["held_seed"] == "NONE" else int(item["held_seed"]),
        item["decoder_id"], item["representation"],
    ))
    fields = (
        "mode", "pair_id", "world_id", "held_seed", "decoder_id",
        "representation", "events", "claim_relpath", "claim_sha256",
    )
    if len(outputs) != 2150 or len({item["claim_relpath"] for item in outputs}) != 2150:
        raise RuntimeError("recovered manifest matrix is incomplete")
    with MANIFEST.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(outputs)
    after = claim_map()
    if len(after) != 2150:
        raise RuntimeError("recovered claim file count is not 2150")
    unchanged = all(after.get(rel) == digest for rel, digest in before.items())
    result = {
        "schema": "GDT395_V3_INTERRUPTION_RECOVERY_RESULT_V1",
        "status": "RECOVERED_EXACT_MISSING_WORLD_CLAIM_AND_MANIFEST",
        "recovery_freeze_sha256": sha(FREEZE),
        "preexisting_claims_unchanged": unchanged,
        "claim_files": len(after),
        "claim_map_sha256": canonical_hash(after),
        "recovered_world_claim": MISSING.as_posix(),
        "recovered_world_claim_sha256": sha(target),
        "claim_manifest_sha256": sha(MANIFEST),
        "oracle_opened": False,
        "voynich_rows": 0,
        "f84_opened": False,
    }
    if not unchanged:
        raise RuntimeError("a pre-existing claim changed during recovery")
    result["content_sha256"] = canonical_hash(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "claim_files": len(after)}, sort_keys=True))


if __name__ == "__main__":
    main()
