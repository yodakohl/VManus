#!/usr/bin/env python3
"""Publish CPU/CUDA crossover measurements for the discrete language search."""

from __future__ import annotations

import json
import time

import numpy as np

from gdt001_core import ROOT, canonical, load_lattice
from gdt001_language_models import cpu_population_scores, gpu_population_scores, initial_population, train_pack


def main():
    _, lines = load_lattice(); paths = [line.paths[0] for line in lines]
    lm = train_pack("latin", 2); rows = []
    for population in (1024, 8192, 32768, 65536):
        mappings = initial_population(population, np.random.default_rng(441 + population), True)
        start = time.perf_counter(); cpu = cpu_population_scores(lm, paths, mappings, False); cpu_s = time.perf_counter() - start
        start = time.perf_counter(); gpu = gpu_population_scores(lm, paths, mappings, False); gpu_s = time.perf_counter() - start
        delta = float(np.max(np.abs(cpu - gpu)))
        if delta > 2e-6: raise AssertionError(delta)
        rows.append({"population": population, "cpu_seconds": cpu_s, "cuda_seconds": gpu_s, "speedup_cpu_over_cuda": cpu_s / gpu_s, "max_exact_score_delta_bits": delta})
    import torch
    payload = {"schema": "GDT001_GPU_BENCHMARK_V2", "status": "EXPLORATORY_PERFORMANCE_ONLY", "device": torch.cuda.get_device_name(0), "torch": torch.__version__, "cuda": torch.version.cuda, "language": "latin", "source_paths": len(paths), "precision": "float64 exact-score kernel", "measurements": rows, "policy": "CUDA used for learned search only when population crossover is material; CPU reconstructs retained keys."}
    (ROOT / "gdt001_gpu_benchmark.json").write_bytes(canonical(payload)); print(json.dumps(rows))


if __name__ == "__main__": main()
