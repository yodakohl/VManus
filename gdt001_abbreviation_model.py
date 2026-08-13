#!/usr/bin/env python3
"""Explicit multigraph abbreviation/allography candidates for GDT001.

The GPU proposes a mapping.  The checked result is a deterministic source-unit
tokenizer, an explicit unit-to-letter table, an exact historical character LM,
and a Dirichlet code for reverse allographic ambiguity and fixed null positions.
"""

from __future__ import annotations

import math
import time
from collections import Counter, defaultdict
from typing import Any, Sequence

import numpy as np

from gdt001_core import (
    LETTERS, TARGET_ALPHABET, LatticeLine, PathObservation, categorical_bits,
    fixed_costs, score_record, universal_uint_bits,
)
from gdt001_language_models import PACK_NAMES, TARGET_LETTERS, TARGET_SPACE, TARGET_BOS, train_pack


MULTIGRAPHS = ("ckh", "cth", "cph", "eee", "aiin", "iin", "ch", "sh", "qo", "ee", "ii", "dy")


def make_units() -> tuple[str, ...]:
    return tuple(sorted(set(MULTIGRAPHS) | set(LETTERS), key=lambda value: (-len(value), value)))


def tokenize_word(word: str, units: Sequence[str]) -> list[str]:
    output: list[str] = []
    offset = 0
    while offset < len(word):
        candidates = [unit for unit in units if word.startswith(unit, offset)]
        if not candidates:
            raise ValueError((word, offset))
        unit = candidates[0]  # units are longest-first and then byte-order
        output.append(unit); offset += len(unit)
    return output


def decode_path(path: PathObservation, decoder: dict[str, Any]) -> tuple[list[str], str]:
    mapping = {row["source_unit"]: row["plaintext_unit"] for row in decoder["mapping"]}
    units = tuple(decoder["source_units_longest_first"])
    segmented_words = []; decoded_words = []
    for word in path.words:
        tokens = tokenize_word(word, units)
        segmented_words.append("+".join(tokens))
        decoded_words.append("".join(mapping[token] for token in tokens if mapping[token] != "<NULL>"))
    return segmented_words, " ".join(decoded_words)


def unit_sequences(paths: Sequence[PathObservation], units: Sequence[str], null_units: frozenset[str]) -> tuple[list[list[int]], np.ndarray, int, int]:
    active = tuple(unit for unit in units if unit not in null_units)
    index = {unit: i for i, unit in enumerate(active)}
    sequences: list[list[int]] = []
    all_count = null_count = 0
    for path in paths:
        values: list[int] = []
        for word_index, word in enumerate(path.words):
            if word_index:
                values.append(len(index))  # explicit target space
            for unit in tokenize_word(word, units):
                all_count += 1
                if unit in null_units:
                    null_count += 1
                else:
                    values.append(index[unit])
        sequences.append(values)
    counts = np.zeros(len(index), dtype=np.float64)
    for sequence in sequences:
        for value in sequence:
            if value < len(index): counts[value] += 1
    return sequences, counts, all_count, null_count


def ngram_counts(sequences: Sequence[Sequence[int]], unit_count: int, order: int) -> tuple[np.ndarray, np.ndarray]:
    counter: Counter[tuple[int, ...]] = Counter()
    bos = unit_count + 1
    for sequence in sequences:
        history = [bos] * order
        for value in sequence:
            counter[tuple(history) + (value,)] += 1
            if order: history = history[1:] + [value]
    keys = np.asarray(list(counter), dtype=np.int64)
    frequencies = np.asarray([counter[key] for key in counter], dtype=np.float64)
    return keys, frequencies


def cpu_scores(lm, sequences, mappings: np.ndarray, counts: np.ndarray) -> np.ndarray:
    unit_count = mappings.shape[1]
    keys, frequencies = ngram_counts(sequences, unit_count, lm.order)
    output = np.zeros(len(mappings), dtype=np.float64)
    for row, mapping in enumerate(mappings):
        extended = np.concatenate([mapping, [TARGET_SPACE, TARGET_BOS]])
        targets = extended[keys]
        output[row] = np.sum(lm.costs[tuple(targets[:, axis] for axis in range(targets.shape[1]))] * frequencies)
        groups: dict[int, list[int]] = defaultdict(list)
        for source, target in enumerate(mapping): groups[int(target)].append(source)
        output[row] += sum(categorical_bits([int(counts[source]) for source in sources]) for sources in groups.values())
    return output


def gpu_scores(lm, sequences, mappings: np.ndarray, counts: np.ndarray, batch: int = 512) -> np.ndarray:
    import torch
    unit_count = mappings.shape[1]
    keys_np, frequencies_np = ngram_counts(sequences, unit_count, lm.order)
    keys = torch.as_tensor(keys_np, device="cuda", dtype=torch.long)
    frequencies = torch.as_tensor(frequencies_np, device="cuda", dtype=torch.float64)
    costs = torch.as_tensor(lm.costs, device="cuda", dtype=torch.float64)
    source_counts = torch.as_tensor(counts, device="cuda", dtype=torch.float64)
    result = []
    for start in range(0, len(mappings), batch):
        current = torch.as_tensor(mappings[start:start + batch], device="cuda", dtype=torch.long)
        tail = torch.tensor([TARGET_SPACE, TARGET_BOS], device="cuda").repeat(len(current), 1)
        extended = torch.cat([current, tail], dim=1)
        indices = [extended[:, keys[:, axis]] for axis in range(keys.shape[1])]
        values = (costs[tuple(indices)] * frequencies.unsqueeze(0)).sum(dim=1)
        multiplicities = torch.zeros((len(current), len(TARGET_LETTERS)), device="cuda", dtype=torch.float64)
        totals = torch.zeros_like(multiplicities); member = torch.zeros_like(multiplicities)
        multiplicities.scatter_add_(1, current, torch.ones_like(current, dtype=torch.float64))
        totals.scatter_add_(1, current, source_counts.unsqueeze(0).expand(len(current), -1))
        constants = torch.lgamma(source_counts + 0.5) - torch.lgamma(torch.tensor(0.5, device="cuda", dtype=torch.float64))
        member.scatter_add_(1, current, constants.unsqueeze(0).expand(len(current), -1))
        logp = torch.lgamma(0.5 * multiplicities) - torch.lgamma(totals + 0.5 * multiplicities) + member
        values += torch.where(multiplicities > 0, -logp / math.log(2.0), 0.0).sum(dim=1)
        result.append(values.cpu().numpy())
    return np.concatenate(result)


def fit_abbreviation_candidate(
    lines: Sequence[LatticeLine], language: str, seed: int, null_q: bool = False,
    population_size: int = 32768, generations: int = 60,
) -> dict[str, Any]:
    if language not in PACK_NAMES: raise ValueError(language)
    lm = train_pack(language, 2)
    paths = [line.paths[0] for line in lines]
    units = make_units(); null_units = frozenset({"q"} if null_q else set())
    active_units = tuple(unit for unit in units if unit not in null_units)
    sequences, counts, all_count, null_count = unit_sequences(paths, units, null_units)
    rng = np.random.default_rng(seed)
    population = rng.integers(0, len(TARGET_LETTERS), size=(population_size, len(active_units)), dtype=np.int64)
    trace = []; started = time.perf_counter(); elite_size = 128
    for _ in range(generations):
        scores = gpu_scores(lm, sequences, population, counts)
        order = np.argsort(scores, kind="stable"); elite = population[order[:elite_size]].copy()
        trace.append(float(scores[order[0]]))
        children = elite[rng.integers(0, elite_size, size=population_size - elite_size)].copy()
        rows = np.arange(len(children)); positions = rng.integers(0, len(active_units), size=len(children))
        children[rows, positions] = rng.integers(0, len(TARGET_LETTERS), size=len(children))
        population = np.vstack([elite, children])
    scores = gpu_scores(lm, sequences, population, counts); best = int(np.argmin(scores)); mapping = population[best]
    exact = float(cpu_scores(lm, sequences, mapping[None, :], counts)[0])
    if abs(exact - float(scores[best])) > 2e-6: raise AssertionError("CPU/CUDA abbreviation objective mismatch")
    language_bits = exact
    null_position_bits = categorical_bits([null_count, all_count - null_count]) if null_q else 0.0
    dictionary_bits = universal_uint_bits(len(units)) + sum(universal_uint_bits(len(unit)) + len(unit) * math.log2(len(LETTERS)) for unit in units)
    key_bits = math.log2(len(PACK_NAMES)) + dictionary_bits + len(active_units) * math.log2(len(TARGET_LETTERS)) + 1.0
    fixed = fixed_costs(paths)
    reverse_bits = language_bits - sum(
        # Extract LM-only cost by subtracting the exact ambiguity term below.
        categorical_bits([int(counts[source]) for source, target in enumerate(mapping) if target == value])
        for value in set(map(int, mapping))
    )
    ambiguity_bits = language_bits - reverse_bits
    rows = []
    for source, unit in enumerate(active_units):
        rows.append({"source_unit": unit, "plaintext_unit": TARGET_LETTERS[int(mapping[source])], "mapping_probability": 1.0,
                     "context_restriction": "GREEDY_LONGEST_UNIT", "occurrences": int(counts[source])})
    for unit in sorted(null_units):
        rows.append({"source_unit": unit, "plaintext_unit": "<NULL>", "mapping_probability": 1.0,
                     "context_restriction": "GREEDY_LONGEST_UNIT", "occurrences": null_count})
    decoder = {
        "schema": "GDT001_ABBREVIATION_TRANSDUCER_V1", "language_pack": language,
        "source_units_longest_first": list(units), "segmentation_rule": "greedy longest unit; byte-order tie break",
        "boundary_rule": "manual group boundary emits plaintext space", "null_units": sorted(null_units),
        "mapping": rows, "language_model_order": 2,
    }
    return score_record(
        candidate_id=f"abbr_lang_multigraph_{language}_{'nullq' if null_q else 'nonull'}_s{seed:04d}",
        model_class="ABBR_LANG", system=f"{language}_MULTIGRAPH", seed=seed,
        config={"stage": 2, "multigraphs": MULTIGRAPHS, "null_q": null_q, "population_size": population_size, "generations": generations},
        paths=paths, key_bits=key_bits, latent_bits=reverse_bits,
        reconstruction_bits=ambiguity_bits + null_position_bits + sum(fixed.values()), exception_bits=0.0,
        decoder=decoder,
    ) | {"search": {"backend": "CUDA", "wall_seconds": time.perf_counter() - started, "best_trace": trace,
                              "cpu_reconstruction_score": exact}, "null_position_bits": null_position_bits}
