#!/usr/bin/env python3
"""GDT395 blind runner V3: exact fit caching plus confidence contract repair."""

from __future__ import annotations

import argparse
import csv
import json
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import run_blind_decoders as v1
import run_blind_decoders_v2 as v2


def install_training_cache(module):
    """Memoize pure train-only model builders for the same list object."""
    decoder_id = module.DECODER_META["decoder_id"]
    if decoder_id == "D01_MULTIVIEW_GRAPH":
        original = module._fit
        cache = {}
        def cached(rows, representation=None):
            key = (id(rows), representation)
            if key not in cache:
                cache[key] = original(rows, representation)
            return cache[key]
        module._fit = cached
    elif decoder_id in {"D03_frequency_position", "D04_surface_components"}:
        original = module._model
        cache = {}
        def cached(rows):
            key = id(rows)
            if key not in cache:
                cache[key] = original(rows)
            return cache[key]
        module._model = cached
    elif decoder_id in {"D02_MDL_COMPONENTS", "D05"}:
        original = module._Model
        cache = {}
        def cached(rows):
            key = id(rows)
            if key not in cache:
                cache[key] = original(rows)
            return cache[key]
        module._Model = cached
    else:
        raise RuntimeError(f"unregistered cache adapter: {decoder_id}")
    return module


def repair_missing_confidence(claims: list[dict]) -> None:
    """Map only the schema-invalid missing-confidence sentinel to zero."""
    for row in claims:
        if row.get("confidence") == "UNRESOLVED":
            row["confidence"] = 0.0


def decoder_job(job: tuple) -> list[dict]:
    original_load = v1.load_decoder
    original_api = v1.claim_api
    def cached_load(path, decoder_id):
        return install_training_cache(original_load(path, decoder_id))
    def repaired_api():
        claim_fields, world_fields, validate = original_api()
        def repaired_validate(meta, held_rows, representation, claims):
            repair_missing_confidence(claims)
            validate(meta, held_rows, representation, claims)
        return claim_fields, world_fields, repaired_validate
    v1.load_decoder = cached_load
    v1.claim_api = repaired_api
    try:
        return v2.decoder_job(job)
    finally:
        v1.load_decoder = original_load
        v1.claim_api = original_api


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=min(16, os.cpu_count() or 1))
    parser.add_argument("--mode", choices=("all", "authentic", "pair"), default="all")
    args = parser.parse_args()
    correction = json.loads((v1.EXP / "artifacts/gdt395_decoder_execution_v3_correction.json").read_text())
    if correction["status"] != "V3_FROZEN_AFTER_UNFROZEN_PARTIAL_V2_RUN":
        raise RuntimeError("V3 correction is not frozen")
    if v1.sha(Path(__file__)) != correction["bindings"]["src/run_blind_decoders_v3.py"]:
        raise RuntimeError("V3 runner changed after correction freeze")
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
        for world_id in sorted({row["world_id"] for row in corpus_manifest}):
            for path, digest, meta in decoders:
                jobs.append(("authentic", "", world_id, str(path), digest, meta))
    if args.mode in ("all", "pair"):
        for pair_id, world_id in sorted({(row["pair_id"], row["world_id"]) for row in pair_manifest}):
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
