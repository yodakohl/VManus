#!/usr/bin/env python3
"""Run the staged GDT001 whole-manuscript global decipherment tournament."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import os
import random
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from gdt001_core import ROOT, canonical, load_lattice, sha256_file
from gdt001_language_models import PACK_NAMES, benchmark, fit_language_candidate
from gdt001_abbreviation_model import fit_abbreviation_candidate
from gdt001_nonsemantic_models import fit_copy_modify, fit_ngram, fit_page_conditioned_unigram
from gdt001_neural_null import train_candidate as fit_neural_null
from gdt001_record_models import fit_dual_channel_hybrid, fit_record_dictionary, fit_record_notation


RUN_DIR = ROOT / ".gdt001/runs"
SUMMARY = ROOT / "gdt001_tournament_runs.json"
BENCHMARK = ROOT / "gdt001_gpu_benchmark.json"
LEDGER = ROOT / "GDT001_YOLO_LEDGER.tsv"
FIELDS = (
    "run_id", "model_class", "language_or_system", "seed", "config_hash",
    "total_bits", "bits_per_symbol", "key_bits", "latent_bits",
    "reconstruction_bits", "exception_bits", "convergence_status", "decoder_hash", "notes",
)


def result_path(candidate_id: str) -> Path:
    return RUN_DIR / f"{candidate_id}.json"


def write_result(result: dict[str, Any]) -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    path = result_path(result["candidate_id"])
    path.write_bytes(canonical(result))


def run_or_load(candidate_id: str, function, *args, **kwargs) -> dict[str, Any]:
    path = result_path(candidate_id)
    if path.exists():
        return json.loads(path.read_text())
    started = time.perf_counter()
    try:
        result = function(*args, **kwargs)
        result["wall_seconds"] = time.perf_counter() - started
        write_result(result)
        return result
    except Exception as exc:
        failure = {
            "candidate_id": candidate_id, "status": "EXPLORATORY_RUN_FAILURE",
            "model_class": kwargs.get("model_class", function.__name__),
            "language_or_system": kwargs.get("language", function.__name__),
            "seed": kwargs.get("seed", 0), "config": kwargs,
            "config_hash": hashlib.sha256(canonical(kwargs)).hexdigest(),
            "total_bits": 1e300, "bits_per_symbol": 1e300, "key_bits": 0.0,
            "latent_bits": 0.0, "reconstruction_bits": 0.0, "exception_bits": 0.0,
            "convergence_status": "FAILED", "decoder_hash": "0" * 64,
            "failure": f"{type(exc).__name__}: {exc}", "wall_seconds": time.perf_counter() - started,
        }
        write_result(failure)
        return failure


def rebuild_ledger(results: list[dict[str, Any]]) -> None:
    with LEDGER.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for result in sorted(results, key=lambda item: item["candidate_id"]):
            writer.writerow({
                "run_id": result["candidate_id"], "model_class": result["model_class"],
                "language_or_system": result["language_or_system"], "seed": result["seed"],
                "config_hash": result["config_hash"], "total_bits": format(result["total_bits"], ".6f"),
                "bits_per_symbol": format(result["bits_per_symbol"], ".9f"),
                "key_bits": format(result["key_bits"], ".6f"), "latent_bits": format(result["latent_bits"], ".6f"),
                "reconstruction_bits": format(result["reconstruction_bits"], ".6f"),
                "exception_bits": format(result["exception_bits"], ".6f"),
                "convergence_status": result["convergence_status"], "decoder_hash": result["decoder_hash"],
                "notes": f"EXPLORATORY; wall_seconds={result.get('wall_seconds', 0):.3f}; {result.get('failure', '')}".rstrip(),
            })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("baselines", "language", "all"), default="all")
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    _, lines = load_lattice()
    results: list[dict[str, Any]] = []
    if not BENCHMARK.exists():
        BENCHMARK.write_bytes(canonical(benchmark(lines)))

    if args.stage in {"baselines", "all"}:
        for order in range(0, 6):
            identifier = f"nonsemantic_ngram_o{order}"
            results.append(run_or_load(identifier, fit_ngram, lines, order))
        for window in (8, 32, 128):
            identifier = f"nonsemantic_copy_w{window}"
            results.append(run_or_load(identifier, fit_copy_modify, lines, window))
        results.append(run_or_load("nonsemantic_page_unigram", fit_page_conditioned_unigram, lines))
        results.append(run_or_load("record_notation_fields", fit_record_notation, lines, False))
        results.append(run_or_load("record_notation_entry_fields", fit_record_notation, lines, True))
        results.append(run_or_load("hybrid_dual_channel_entry_body", fit_dual_channel_hybrid, lines))
        for order in (0, 1, 2):
            results.append(run_or_load(f"record_notation_dictionary_o{order}", fit_record_dictionary, lines, order))
        if "torch" in sys.modules or importlib.util.find_spec("torch") is not None:
            for seed in ((71,) if args.quick else (71, 72, 73)):
                identifier = f"nonsemantic_neural_gru_h48_s{seed:04d}"
                results.append(run_or_load(identifier, fit_neural_null, lines, seed))

    if args.stage in {"language", "all"}:
        seeds = (101, 202, 303) if not args.quick else (101,)
        population = 32768 if not args.quick else 2048
        generations = 60 if not args.quick else 12
        cuda = not args.quick
        for model_class in ("ABBR_LANG", "HOMOPHONIC_CIPHER"):
            for language in PACK_NAMES:
                for seed in seeds:
                    identifier = f"{model_class.lower()}_{language}_s{seed:04d}"
                    results.append(run_or_load(
                        identifier, fit_language_candidate, lines, language, model_class, seed,
                        population_size=population, generations=generations, cuda=cuda,
                    ))
        # Stage-2 abbreviation expansion.  Only the best stage-1 language is
        # expanded, and every retained multigraph/null rule is charged.
        if not args.quick:
            for null_q in (False, True):
                for seed in seeds:
                    identifier = f"abbr_lang_multigraph_middle_high_german_{'nullq' if null_q else 'nonull'}_s{seed:04d}"
                    results.append(run_or_load(
                        identifier, fit_abbreviation_candidate, lines, "middle_high_german", seed, null_q,
                        population_size=population, generations=generations,
                    ))

    # Include earlier cached stages when invoking a subset.
    known = {result["candidate_id"] for result in results}
    for path in sorted(RUN_DIR.glob("*.json")) if RUN_DIR.exists() else []:
        item = json.loads(path.read_text())
        if item["candidate_id"] not in known:
            results.append(item)
    rebuild_ledger(results)
    ordered = sorted(results, key=lambda item: (item["total_bits"], item["candidate_id"]))
    summary = {
        "schema": "GDT001_TOURNAMENT_RUNS_V1", "status": "EXPLORATORY_NOT_CONFIRMED_TRANSLATION",
        "lattice_sha256": sha256_file(ROOT / "gdt001_corpus_lattice.json"),
        "language_pack_manifest_sha256": sha256_file(ROOT / "gdt001_language_pack_manifest.json"),
        "gpu_benchmark_sha256": sha256_file(BENCHMARK), "run_count": len(ordered),
        "leaderboard": [{key: result[key] for key in (
            "candidate_id", "model_class", "language_or_system", "seed", "total_bits",
            "bits_per_symbol", "key_bits", "latent_bits", "reconstruction_bits",
            "exception_bits", "convergence_status", "decoder_hash",
        )} for result in ordered],
    }
    SUMMARY.write_bytes(canonical(summary))
    print(json.dumps({"runs": len(ordered), "leader": ordered[0]["candidate_id"], "bits_per_symbol": ordered[0]["bits_per_symbol"]}, sort_keys=True))


if __name__ == "__main__":
    main()
