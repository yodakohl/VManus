#!/usr/bin/env python3
"""Run the frozen GDT395 oracle-blind decoder panel.

This program reads observation packets only.  It deliberately has no oracle
path, argument, loader, or scoring code.  One worker loads seeds 0--14 for one
decoder and one world/view, then applies the unchanged decoder separately to
each held seed 15--19 at all six frozen representations.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import importlib.util
import io
import json
import os
import re
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark"
CORPUS_ROOT = EXP / ".work/corpora"
PAIR_ROOT = EXP / ".work/pair_blind"
CLAIM_ROOT = EXP / ".work/claims"
FREEZE = EXP / "artifacts/gdt395_decoder_panel_freeze.json"
CORPUS_MANIFEST = EXP / "artifacts/gdt395_corpus_manifest.tsv"
PAIR_MANIFEST = EXP / "artifacts/gdt395_pair_blind_manifest.tsv"
TRAIN_SEEDS = tuple(range(15))
HELD_SEEDS = tuple(range(15, 20))
SAFE_ID = re.compile(r"^[A-Z0-9_]+$")
REPRESENTATIONS = (
    "FULL_GROUP", "HOST_LIKE", "COMPOSITE_STATE", "INFERRED_COMPONENTS",
    "CONSTRUCTION_SPAN", "RECORD_TOPOLOGY",
)


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_tsv(path: Path) -> list[dict]:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write_tsv_gz(path: Path, fields: tuple[str, ...], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, compresslevel=9, mtime=0) as zipped:
            with io.TextIOWrapper(zipped, encoding="utf-8", newline="") as fh:
                writer = csv.DictWriter(fh, fieldnames=fields, delimiter="\t", lineterminator="\n")
                writer.writeheader()
                writer.writerows(rows)


def load_decoder(path: Path, decoder_id: str):
    if str(EXP) not in sys.path:
        sys.path.insert(0, str(EXP))
    spec = importlib.util.spec_from_file_location(f"gdt395_blind_{decoder_id}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load decoder {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def claim_api():
    if str(EXP) not in sys.path:
        sys.path.insert(0, str(EXP))
    from src.decoder_api import CLAIM_FIELDS, WORLD_CLAIM_FIELDS, validate_claims
    return CLAIM_FIELDS, WORLD_CLAIM_FIELDS, validate_claims


def corpus_rows(mode: str, pair_id: str, world_id: str, seed: int) -> list[dict]:
    if mode == "authentic":
        path = CORPUS_ROOT / "blind" / world_id / f"seed_{seed:02d}.tsv.gz"
    else:
        path = PAIR_ROOT / pair_id / world_id / f"seed_{seed:02d}.tsv.gz"
    rows = read_tsv(path)
    if any(row.get("world_id") != world_id or int(row.get("corpus_seed", -1)) != seed for row in rows):
        raise RuntimeError(f"row provenance mismatch in {path}")
    return rows


def decoder_job(job: tuple) -> list[dict]:
    mode, pair_id, world_id, decoder_path_text, expected_sha, expected_meta = job
    decoder_path = Path(decoder_path_text)
    if sha(decoder_path) != expected_sha:
        raise RuntimeError(f"decoder changed after freeze: {decoder_path}")
    module = load_decoder(decoder_path, decoder_path.parent.name)
    if module.DECODER_META != expected_meta:
        raise RuntimeError(f"decoder metadata changed after freeze: {decoder_path}")
    claim_fields, world_fields, validate_claims = claim_api()
    train_rows: list[dict] = []
    for seed in TRAIN_SEEDS:
        train_rows.extend(corpus_rows(mode, pair_id, world_id, seed))
    outputs = []
    for held_seed in HELD_SEEDS:
        held_rows = corpus_rows(mode, pair_id, world_id, held_seed)
        for representation in REPRESENTATIONS:
            claims = module.decode(train_rows, held_rows, representation)
            validate_claims(module.DECODER_META, held_rows, representation, claims)
            rel = Path(mode)
            if pair_id:
                rel /= pair_id
            rel /= world_id / module.DECODER_META["decoder_id"] / f"seed_{held_seed:02d}_{representation}.tsv.gz"
            out = CLAIM_ROOT / rel
            write_tsv_gz(out, claim_fields, claims)
            outputs.append({
                "mode": mode, "pair_id": pair_id or "NONE", "world_id": world_id,
                "held_seed": held_seed, "decoder_id": module.DECODER_META["decoder_id"],
                "representation": representation, "events": len(claims),
                "claim_relpath": str(out.relative_to(CLAIM_ROOT)), "claim_sha256": sha(out),
            })
    if mode == "authentic":
        world_claim = module.classify_world(train_rows)
        if set(world_claim) != set(world_fields):
            raise RuntimeError(f"bad world-claim fields from {module.DECODER_META['decoder_id']}")
        if world_claim["decoder_id"] != module.DECODER_META["decoder_id"]:
            raise RuntimeError("world-claim decoder mismatch")
        confidence = float(world_claim["confidence"])
        if not 0.0 <= confidence <= 1.0:
            raise RuntimeError("world-claim confidence outside [0,1]")
        world_path = CLAIM_ROOT / "world_claims" / world_id / module.DECODER_META["decoder_id"] / "train_seeds_00_14.json"
        world_path.parent.mkdir(parents=True, exist_ok=True)
        world_path.write_text(json.dumps(world_claim, indent=2, sort_keys=True) + "\n")
        outputs.append({
            "mode": "world_claim", "pair_id": "NONE", "world_id": world_id,
            "held_seed": "NONE", "decoder_id": module.DECODER_META["decoder_id"],
            "representation": "ALL_TRAIN_OBSERVATIONS", "events": 1,
            "claim_relpath": str(world_path.relative_to(CLAIM_ROOT)), "claim_sha256": sha(world_path),
        })
    return outputs


def manifest_rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def validate_freeze(data: dict) -> None:
    tmp = dict(data)
    expected = tmp.pop("content_sha256")
    actual = hashlib.sha256(json.dumps(tmp, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if actual != expected:
        raise RuntimeError("decoder freeze content hash mismatch")
    for rel, digest in data["bindings"].items():
        if sha(ROOT / rel) != digest:
            raise RuntimeError(f"decoder freeze binding mismatch: {rel}")


def validate_observation_inputs(corpus: list[dict], pairs: list[dict]) -> None:
    for row in corpus:
        world = row["world_id"]
        if not SAFE_ID.fullmatch(world):
            raise RuntimeError(f"unsafe world id: {world}")
        expected = Path("blind") / world / f"seed_{int(row['corpus_seed']):02d}.tsv.gz"
        if Path(row["observation_relpath"]) != expected:
            raise RuntimeError(f"unexpected corpus observation path: {row['observation_relpath']}")
        if sha(CORPUS_ROOT / expected) != row["observation_sha256"]:
            raise RuntimeError(f"corpus observation hash mismatch: {expected}")
    for row in pairs:
        pair_id, world = row["pair_id"], row["world_id"]
        if not SAFE_ID.fullmatch(pair_id) or not SAFE_ID.fullmatch(world):
            raise RuntimeError(f"unsafe pair/world id: {pair_id}/{world}")
        expected = Path(pair_id) / world / f"seed_{int(row['corpus_seed']):02d}.tsv.gz"
        if Path(row["observation_relpath"]) != expected:
            raise RuntimeError(f"unexpected pair observation path: {row['observation_relpath']}")
        if sha(PAIR_ROOT / expected) != row["observation_sha256"]:
            raise RuntimeError(f"pair observation hash mismatch: {expected}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=min(4, os.cpu_count() or 1))
    parser.add_argument("--mode", choices=("all", "authentic", "pair"), default="all")
    args = parser.parse_args()
    frozen = json.loads(FREEZE.read_text())
    if frozen["status"] != "FROZEN_BEFORE_DECODER_EXECUTION":
        raise RuntimeError("decoder panel is not frozen")
    validate_freeze(frozen)
    corpus_manifest = manifest_rows(CORPUS_MANIFEST)
    pair_manifest = manifest_rows(PAIR_MANIFEST)
    validate_observation_inputs(corpus_manifest, pair_manifest)
    decoders = []
    for row in frozen["decoders"]:
        path = ROOT / row["directory"] / "decoder.py"
        decoders.append((path, row["source_sha256"], row["meta"]))
    jobs = []
    if args.mode in ("all", "authentic"):
        worlds = sorted({r["world_id"] for r in corpus_manifest})
        for world_id in worlds:
            for path, digest, meta in decoders:
                jobs.append(("authentic", "", world_id, str(path), digest, meta))
    if args.mode in ("all", "pair"):
        pairs = sorted({(r["pair_id"], r["world_id"]) for r in pair_manifest})
        for pair_id, world_id in pairs:
            for path, digest, meta in decoders:
                jobs.append(("pair", pair_id, world_id, str(path), digest, meta))
    outputs = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(decoder_job, job): job for job in jobs}
        for done, future in enumerate(as_completed(futures), 1):
            batch = future.result()
            outputs.extend(batch)
            if done % 10 == 0 or done == len(futures):
                print(json.dumps({"jobs_complete": done, "jobs_total": len(futures), "files": len(outputs)}), flush=True)
    outputs.sort(key=lambda r: (
        r["mode"], r["pair_id"], r["world_id"],
        -1 if r["held_seed"] == "NONE" else int(r["held_seed"]),
        r["decoder_id"], r["representation"],
    ))
    manifest = CLAIM_ROOT / f"blind_claim_manifest_{args.mode}.tsv"
    fields = ("mode", "pair_id", "world_id", "held_seed", "decoder_id", "representation", "events", "claim_relpath", "claim_sha256")
    with manifest.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(outputs)
    print(json.dumps({"status": "BLIND_CLAIMS_WRITTEN", "jobs": len(jobs), "rows": len(outputs), "manifest_sha256": sha(manifest)}, sort_keys=True))


if __name__ == "__main__":
    main()
