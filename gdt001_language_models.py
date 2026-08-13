#!/usr/bin/env python3
"""Explicit ABBR_LANG and HOMOPHONIC_CIPHER proposals with CPU-verifiable scores."""

from __future__ import annotations

import json
import math
import random
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from gdt001_core import (
    LETTERS, SOURCE_ALPHABET, TARGET_ALPHABET, LatticeLine, PathObservation,
    categorical_bits, fixed_costs, score_record, universal_uint_bits,
)


ROOT = Path(__file__).resolve().parent
PACK_DIR = ROOT / ".gdt001/language_packs"
PACK_NAMES = (
    "latin", "middle_high_german", "middle_french", "old_italian_tuscan",
    "medieval_czech", "old_hungarian",
)
TARGET_LETTERS = TARGET_ALPHABET[:-1]
SOURCE_SPACE = len(LETTERS)
TARGET_SPACE = len(TARGET_LETTERS)
SOURCE_BOS = len(SOURCE_ALPHABET)
TARGET_BOS = len(TARGET_ALPHABET)


@dataclass(frozen=True)
class NgramLM:
    language: str
    order: int
    costs: np.ndarray
    corpus_letters: int


def train_pack(language: str, order: int = 2, alpha: float = 0.5) -> NgramLM:
    if language not in PACK_NAMES:
        raise ValueError(language)
    size = len(TARGET_ALPHABET)
    shape = (size + 1,) * order + (size,)
    counts = np.zeros(shape, dtype=np.float64)
    letters = 0
    with (PACK_DIR / f"{language}.txt").open(encoding="utf-8") as handle:
        for raw in handle:
            text = raw.strip()
            if not text:
                continue
            ids = [TARGET_ALPHABET.index(char) for char in text]
            letters += sum(value != TARGET_SPACE for value in ids)
            history = [TARGET_BOS] * order
            for value in ids:
                counts[tuple(history) + (value,)] += 1.0
                if order:
                    history = history[1:] + [value]
    denominators = counts.sum(axis=-1, keepdims=True) + alpha * size
    costs = -np.log2((counts + alpha) / denominators)
    return NgramLM(language=language, order=order, costs=costs, corpus_letters=letters)


def source_ngram_counts(paths: Sequence[PathObservation], order: int) -> tuple[np.ndarray, np.ndarray]:
    counter: Counter[tuple[int, ...]] = Counter()
    for path in paths:
        history = [SOURCE_BOS] * order
        for value in path.source_ids:
            counter[tuple(history) + (value,)] += 1
            if order:
                history = history[1:] + [value]
    keys = np.asarray(list(counter), dtype=np.int64)
    values = np.asarray([counter[key] for key in counter], dtype=np.float64)
    return keys, values


def source_unigrams(paths: Sequence[PathObservation]) -> np.ndarray:
    counts = np.zeros(len(LETTERS), dtype=np.float64)
    for path in paths:
        for value in path.source_ids:
            if value < len(LETTERS):
                counts[value] += 1.0
    return counts


def mapped_ids(mapping: Sequence[int], path: PathObservation) -> list[int]:
    return [TARGET_SPACE if value == SOURCE_SPACE else mapping[value] for value in path.source_ids]


def path_language_bits(lm: NgramLM, mapping: Sequence[int], path: PathObservation) -> float:
    history = [TARGET_BOS] * lm.order
    total = 0.0
    for value in mapped_ids(mapping, path):
        total += float(lm.costs[tuple(history) + (value,)])
        if lm.order:
            history = history[1:] + [value]
    return total


def homophone_reverse_bits(mapping: Sequence[int], counts: np.ndarray) -> float:
    groups: dict[int, list[int]] = defaultdict(list)
    for source, target in enumerate(mapping):
        groups[target].append(source)
    return sum(categorical_bits([int(counts[source]) for source in sources]) for sources in groups.values())


def path_homophone_reverse_bits(mapping: Sequence[int], global_counts: np.ndarray, path: PathObservation) -> float:
    groups: dict[int, list[int]] = defaultdict(list)
    for source, target in enumerate(mapping):
        groups[target].append(source)
    probabilities: dict[int, float] = {}
    for target, sources in groups.items():
        denominator = sum(global_counts[source] + 0.5 for source in sources)
        for source in sources:
            probabilities[source] = -math.log2((global_counts[source] + 0.5) / denominator)
    return sum(probabilities[value] for value in path.source_ids if value < len(LETTERS))


def cpu_population_scores(
    lm: NgramLM, paths: Sequence[PathObservation], mappings: np.ndarray, homophonic: bool,
) -> np.ndarray:
    keys, frequencies = source_ngram_counts(paths, lm.order)
    source_counts = source_unigrams(paths)
    result = np.zeros(len(mappings), dtype=np.float64)
    for row, mapping in enumerate(mappings):
        extended = np.concatenate([mapping, [TARGET_SPACE, TARGET_BOS]])
        target = extended[keys]
        result[row] = np.sum(lm.costs[tuple(target[:, axis] for axis in range(target.shape[1]))] * frequencies)
        if homophonic:
            result[row] += homophone_reverse_bits(mapping, source_counts)
    return result


def gpu_population_scores(
    lm: NgramLM, paths: Sequence[PathObservation], mappings: np.ndarray, homophonic: bool,
    batch: int = 512,
) -> np.ndarray:
    import torch

    keys_np, frequencies_np = source_ngram_counts(paths, lm.order)
    counts_np = source_unigrams(paths)
    device = torch.device("cuda")
    keys = torch.as_tensor(keys_np, device=device, dtype=torch.long)
    frequencies = torch.as_tensor(frequencies_np, device=device, dtype=torch.float64)
    lm_costs = torch.as_tensor(lm.costs, device=device, dtype=torch.float64)
    source_counts = torch.as_tensor(counts_np, device=device, dtype=torch.float64)
    outputs = []
    for start in range(0, len(mappings), batch):
        current = torch.as_tensor(mappings[start:start + batch], device=device, dtype=torch.long)
        fixed = torch.tensor([TARGET_SPACE, TARGET_BOS], device=device, dtype=torch.long).repeat(len(current), 1)
        extended = torch.cat([current, fixed], dim=1)
        indices = [extended[:, keys[:, axis]] for axis in range(keys.shape[1])]
        values = lm_costs[tuple(indices)]
        scores = (values * frequencies.unsqueeze(0)).sum(dim=1)
        if homophonic:
            log_alpha_gamma = torch.lgamma(torch.tensor(0.5, device=device, dtype=torch.float64))
            target_count = len(TARGET_LETTERS)
            multiplicities = torch.zeros((len(current), target_count), device=device, dtype=torch.float64)
            totals = torch.zeros_like(multiplicities)
            member_terms = torch.zeros_like(multiplicities)
            multiplicities.scatter_add_(1, current, torch.ones_like(current, dtype=torch.float64))
            totals.scatter_add_(1, current, source_counts.unsqueeze(0).expand(len(current), -1))
            constants = torch.lgamma(source_counts + 0.5) - log_alpha_gamma
            member_terms.scatter_add_(1, current, constants.unsqueeze(0).expand(len(current), -1))
            log_probability = torch.lgamma(0.5 * multiplicities) - torch.lgamma(totals + 0.5 * multiplicities) + member_terms
            scores += torch.where(multiplicities > 0, -log_probability / math.log(2.0), torch.zeros_like(log_probability)).sum(dim=1)
        outputs.append(scores.cpu().numpy())
    return np.concatenate(outputs)


def initial_population(size: int, rng: np.random.Generator, injective: bool) -> np.ndarray:
    output = np.empty((size, len(LETTERS)), dtype=np.int64)
    for row in range(size):
        if injective:
            output[row] = rng.permutation(len(TARGET_LETTERS))[:len(LETTERS)]
        else:
            output[row] = rng.integers(0, len(TARGET_LETTERS), size=len(LETTERS))
    return output


def evolve_mapping(
    lm: NgramLM, paths: Sequence[PathObservation], *, seed: int, injective: bool,
    population_size: int = 4096, generations: int = 160, elite_size: int = 128,
    cuda: bool = True,
) -> tuple[np.ndarray, float, dict[str, Any]]:
    rng = np.random.default_rng(seed)
    population = initial_population(population_size, rng, injective)
    scorer = gpu_population_scores if cuda else cpu_population_scores
    start = time.perf_counter()
    best_trace: list[float] = []
    for generation in range(generations):
        scores = scorer(lm, paths, population, not injective)
        order = np.argsort(scores, kind="stable")
        elite = population[order[:elite_size]].copy()
        best_trace.append(float(scores[order[0]]))
        parent_indices = rng.integers(0, elite_size, size=population_size - elite_size)
        children = elite[parent_indices].copy()
        mutations = 1 + rng.binomial(2, 0.35, size=len(children))
        for count in range(1, 4):
            rows = np.flatnonzero(mutations >= count)
            if not len(rows):
                continue
            positions = rng.integers(0, len(LETTERS), size=len(rows))
            if injective:
                targets = rng.integers(0, len(TARGET_LETTERS), size=len(rows))
                current = children[rows]
                matches = current == targets[:, None]
                present = matches.any(axis=1)
                match_positions = matches.argmax(axis=1)
                displaced = children[rows, positions].copy()
                children[rows, positions] = targets
                present_rows = rows[present]
                children[present_rows, match_positions[present]] = displaced[present]
            else:
                children[rows, positions] = rng.integers(0, len(TARGET_LETTERS), size=len(rows))
        population = np.vstack([elite, children])
    scores = scorer(lm, paths, population, not injective)
    index = int(np.argmin(scores))
    mapping = population[index].copy()
    cpu_score = float(cpu_population_scores(lm, paths, mapping[None, :], not injective)[0])
    if abs(cpu_score - float(scores[index])) > 2e-6:
        raise AssertionError("CPU/CUDA language objective mismatch")
    return mapping, cpu_score, {
        "backend": "CUDA" if cuda else "CPU", "population_size": population_size,
        "generations": generations, "elite_size": elite_size,
        "wall_seconds": time.perf_counter() - start, "best_trace": best_trace,
        "cpu_reconstruction_score": cpu_score,
    }


def choose_paths(
    lines: Sequence[LatticeLine], lm: NgramLM, mapping: Sequence[int], homophonic: bool,
    source_counts: np.ndarray,
) -> list[PathObservation]:
    selected = []
    for line in lines:
        candidates = []
        for path in line.paths:
            bits = path_language_bits(lm, mapping, path) + path.fixed_bits
            if homophonic:
                bits += path_homophone_reverse_bits(mapping, source_counts, path)
            candidates.append((bits, path.path_id, path))
        selected.append(min(candidates, key=lambda item: (item[0], item[1]))[2])
    return selected


def explicit_mapping(mapping: Sequence[int], homophonic: bool, paths: Sequence[PathObservation]) -> list[dict[str, Any]]:
    counts = source_unigrams(paths)
    target_groups: Counter[int] = Counter(mapping)
    rows = []
    for index, value in enumerate(mapping):
        rows.append({
            "source_unit": LETTERS[index], "latent_unit": TARGET_LETTERS[value],
            "mapping_probability": 1.0, "context_restriction": "ALL",
            "occurrences": int(counts[index]),
            "reverse_ambiguity": target_groups[value] if homophonic else 1,
        })
    rows.append({
        "source_unit": "<MANUAL_GROUP_BOUNDARY>", "latent_unit": " ",
        "mapping_probability": 1.0, "context_restriction": "MANUAL_BOUNDARY_ONLY",
        "occurrences": sum(max(0, len(path.words) - 1) for path in paths), "reverse_ambiguity": 1,
    })
    return rows


def fit_language_candidate(
    lines: Sequence[LatticeLine], language: str, model_class: str, seed: int,
    *, population_size: int = 4096, generations: int = 160, cuda: bool = True,
) -> dict[str, Any]:
    if model_class not in {"ABBR_LANG", "HOMOPHONIC_CIPHER"}:
        raise ValueError(model_class)
    homophonic = model_class == "HOMOPHONIC_CIPHER"
    lm = train_pack(language, order=2)
    selected = [line.paths[0] for line in lines]
    searches = []
    mapping = np.arange(len(LETTERS), dtype=np.int64)
    for em_round in range(3):
        mapping, _, search = evolve_mapping(
            lm, selected, seed=seed + 1009 * em_round, injective=not homophonic,
            population_size=population_size, generations=generations, cuda=cuda,
        )
        searches.append(search)
        counts = source_unigrams(selected)
        new_selected = choose_paths(lines, lm, mapping, homophonic, counts)
        if [p.path_id for p in new_selected] == [p.path_id for p in selected]:
            selected = new_selected
            break
        selected = new_selected
    latent = sum(path_language_bits(lm, mapping, path) for path in selected)
    reverse = homophone_reverse_bits(mapping, source_unigrams(selected)) if homophonic else 0.0
    fixed = fixed_costs(selected)
    key = math.log2(len(PACK_NAMES))
    if homophonic:
        key += len(LETTERS) * math.log2(len(TARGET_LETTERS))
    else:
        key += sum(math.log2(len(TARGET_LETTERS) - index) for index in range(len(LETTERS)))
    key += universal_uint_bits(lm.order)
    reconstruction = reverse + sum(fixed.values())
    decoder = {
        "schema": "GDT001_EXPLICIT_MONOTONIC_MAPPING_V1",
        "language_pack": language, "language_model_order": lm.order,
        "mapping_kind": "HOMOPHONIC" if homophonic else "INJECTIVE_ALLOGRAPHIC",
        "source_boundary_rule": "manual group boundaries emit one latent space",
        "segmentation_rule": "one source letter per unit; manual group boundary preserved",
        "mapping": explicit_mapping(mapping, homophonic, selected),
        "language_model_corpus_letters": lm.corpus_letters,
    }
    candidate_id = f"{model_class.lower()}_{language}_s{seed:04d}"
    return score_record(
        candidate_id=candidate_id, model_class=model_class, system=language, seed=seed,
        config={"stage": 1, "lm_order": 2, "population_size": population_size, "generations": generations, "em_rounds": len(searches), "cuda": cuda},
        paths=selected, key_bits=key, latent_bits=latent,
        reconstruction_bits=reconstruction, exception_bits=0.0, decoder=decoder,
    ) | {"search": searches, "reverse_source_bits": reverse}


def benchmark(lines: Sequence[LatticeLine], language: str = "latin", seed: int = 1) -> dict[str, Any]:
    lm = train_pack(language, order=2)
    paths = [line.paths[0] for line in lines]
    rng = np.random.default_rng(seed)
    mappings = initial_population(1024, rng, True)
    before = time.perf_counter(); cpu = cpu_population_scores(lm, paths, mappings, False); cpu_time = time.perf_counter() - before
    before = time.perf_counter(); gpu = gpu_population_scores(lm, paths, mappings, False); gpu_time = time.perf_counter() - before
    delta = float(np.max(np.abs(cpu - gpu)))
    if delta > 1e-6:
        raise AssertionError(delta)
    return {
        "schema": "GDT001_LANGUAGE_SEARCH_BENCHMARK_V1", "population": len(mappings),
        "source_paths": len(paths), "language": language, "cpu_seconds": cpu_time,
        "cuda_seconds": gpu_time, "speedup": cpu_time / gpu_time, "max_score_delta_bits": delta,
    }
