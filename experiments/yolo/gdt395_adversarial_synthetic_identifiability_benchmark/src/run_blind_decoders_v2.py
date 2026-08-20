#!/usr/bin/env python3
"""GDT395 blind runner V2: plumbing-only correction of V1 path assembly."""

from __future__ import annotations

import argparse
import csv
import json
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import run_blind_decoders as v1


def decoder_job(job: tuple) -> list[dict]:
    """V1 job with only the invalid string/string path expression corrected."""
    mode, pair_id, world_id, decoder_path_text, expected_sha, expected_meta = job
    decoder_path = Path(decoder_path_text)
    if v1.sha(decoder_path) != expected_sha:
        raise RuntimeError(f"decoder changed after freeze: {decoder_path}")
    module = v1.load_decoder(decoder_path, decoder_path.parent.name)
    if module.DECODER_META != expected_meta:
        raise RuntimeError(f"decoder metadata changed after freeze: {decoder_path}")
    claim_fields, world_fields, validate_claims = v1.claim_api()
    train_rows: list[dict] = []
    for seed in v1.TRAIN_SEEDS:
        train_rows.extend(v1.corpus_rows(mode, pair_id, world_id, seed))
    outputs = []
    for held_seed in v1.HELD_SEEDS:
        held_rows = v1.corpus_rows(mode, pair_id, world_id, held_seed)
        for representation in v1.REPRESENTATIONS:
            claims = module.decode(train_rows, held_rows, representation)
            validate_claims(module.DECODER_META, held_rows, representation, claims)
            rel = Path(mode)
            if pair_id:
                rel /= pair_id
            rel /= Path(world_id) / module.DECODER_META["decoder_id"] / f"seed_{held_seed:02d}_{representation}.tsv.gz"
            out = v1.CLAIM_ROOT / rel
            v1.write_tsv_gz(out, claim_fields, claims)
            outputs.append({
                "mode": mode, "pair_id": pair_id or "NONE", "world_id": world_id,
                "held_seed": held_seed, "decoder_id": module.DECODER_META["decoder_id"],
                "representation": representation, "events": len(claims),
                "claim_relpath": str(out.relative_to(v1.CLAIM_ROOT)), "claim_sha256": v1.sha(out),
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
        world_path = v1.CLAIM_ROOT / "world_claims" / world_id / module.DECODER_META["decoder_id"] / "train_seeds_00_14.json"
        world_path.parent.mkdir(parents=True, exist_ok=True)
        world_path.write_text(json.dumps(world_claim, indent=2, sort_keys=True) + "\n")
        outputs.append({
            "mode": "world_claim", "pair_id": "NONE", "world_id": world_id,
            "held_seed": "NONE", "decoder_id": module.DECODER_META["decoder_id"],
            "representation": "ALL_TRAIN_OBSERVATIONS", "events": 1,
            "claim_relpath": str(world_path.relative_to(v1.CLAIM_ROOT)), "claim_sha256": v1.sha(world_path),
        })
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=min(4, os.cpu_count() or 1))
    parser.add_argument("--mode", choices=("all", "authentic", "pair"), default="all")
    args = parser.parse_args()
    correction = json.loads((v1.EXP / "artifacts/gdt395_decoder_execution_correction.json").read_text())
    if correction["status"] != "V2_FROZEN_AFTER_ZERO_CLAIM_V1_FAILURE":
        raise RuntimeError("execution correction is not frozen")
    if v1.sha(Path(__file__)) != correction["bindings"]["src/run_blind_decoders_v2.py"]:
        raise RuntimeError("V2 runner changed after correction freeze")
    frozen = json.loads(v1.FREEZE.read_text())
    v1.validate_freeze(frozen)
    corpus_manifest = v1.manifest_rows(v1.CORPUS_MANIFEST)
    pair_manifest = v1.manifest_rows(v1.PAIR_MANIFEST)
    v1.validate_observation_inputs(corpus_manifest, pair_manifest)
    decoders = []
    for row in frozen["decoders"]:
        path = v1.ROOT / row["directory"] / "decoder.py"
        decoders.append((path, row["source_sha256"], row["meta"]))
    jobs = []
    if args.mode in ("all", "authentic"):
        for world_id in sorted({r["world_id"] for r in corpus_manifest}):
            for path, digest, meta in decoders:
                jobs.append(("authentic", "", world_id, str(path), digest, meta))
    if args.mode in ("all", "pair"):
        for pair_id, world_id in sorted({(r["pair_id"], r["world_id"]) for r in pair_manifest}):
            for path, digest, meta in decoders:
                jobs.append(("pair", pair_id, world_id, str(path), digest, meta))
    outputs = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(decoder_job, job): job for job in jobs}
        for done, future in enumerate(as_completed(futures), 1):
            outputs.extend(future.result())
            if done % 10 == 0 or done == len(futures):
                print(json.dumps({"jobs_complete": done, "jobs_total": len(futures), "files": len(outputs)}), flush=True)
    outputs.sort(key=lambda row: (
        row["mode"], row["pair_id"], row["world_id"],
        -1 if row["held_seed"] == "NONE" else int(row["held_seed"]),
        row["decoder_id"], row["representation"],
    ))
    manifest = v1.CLAIM_ROOT / f"blind_claim_manifest_{args.mode}.tsv"
    fields = ("mode", "pair_id", "world_id", "held_seed", "decoder_id", "representation", "events", "claim_relpath", "claim_sha256")
    with manifest.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(outputs)
    print(json.dumps({"status": "BLIND_CLAIMS_WRITTEN", "jobs": len(jobs), "rows": len(outputs), "manifest_sha256": v1.sha(manifest)}, sort_keys=True))


if __name__ == "__main__":
    main()
