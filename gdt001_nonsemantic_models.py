#!/usr/bin/env python3
"""Strong explicit nonsemantic baselines for the GDT001 common MDL tournament."""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from typing import Any, Sequence

from gdt001_core import (
    SOURCE_ALPHABET, LatticeLine, PathObservation, categorical_bits, fixed_costs,
    kt_ngram_bits, kt_ngram_components, levenshtein_program, score_record, train_ngram_logprob,
    universal_uint_bits,
)


def predictive_path_bits(path: PathObservation, table: dict[tuple[int, ...], tuple[float, ...]], order: int) -> float:
    history = [len(SOURCE_ALPHABET)] * order
    total = 0.0
    fallback = math.log2(len(SOURCE_ALPHABET))
    for token in path.source_ids:
        values = table.get(tuple(history))
        total += values[token] if values is not None else fallback
        if order:
            history = history[1:] + [token]
    return total


def fit_ngram(lines: Sequence[LatticeLine], order: int, seed: int = 0) -> dict[str, Any]:
    selected = [line.paths[0] for line in lines]
    for _ in range(5):
        table = train_ngram_logprob([path.source_ids for path in selected], len(SOURCE_ALPHABET), order)
        updated = []
        for line in lines:
            candidates = [
                (predictive_path_bits(path, table, order) + path.fixed_bits, path.path_id, path)
                for path in line.paths
            ]
            updated.append(min(candidates, key=lambda item: (item[0], item[1]))[2])
        if [p.path_id for p in updated] == [p.path_id for p in selected]:
            selected = updated
            break
        selected = updated
    source_bits, context_statistics = kt_ngram_components([path.source_ids for path in selected], len(SOURCE_ALPHABET), order)
    fixed = fixed_costs(selected)
    context_counts: Counter[tuple[int, ...]] = Counter()
    bos = len(SOURCE_ALPHABET)
    for path in selected:
        history = [bos] * order
        for token in path.source_ids:
            context_counts[tuple(history) + (token,)] += 1
            if order:
                history = history[1:] + [token]
    compact = [
        {"context": "".join("^" if value == bos else SOURCE_ALPHABET[value] for value in key[:-1]),
         "next": SOURCE_ALPHABET[key[-1]], "count": count}
        for key, count in sorted(context_counts.items(), key=lambda item: (-item[1], item[0]))
    ]
    decoder = {
        "schema": "GDT001_NONSEMANTIC_NGRAM_GENERATOR_V1",
        "order": order, "alphabet": SOURCE_ALPHABET, "line_reset": True,
        "smoothing": "Dirichlet-1/2 integrated code", "nonzero_counts": compact,
        "context_statistics": context_statistics,
        "decoded_output": "source symbols reproduce themselves; no plaintext asserted",
    }
    return score_record(
        candidate_id=f"nonsemantic_ngram_o{order}", model_class="NONSEMANTIC_GENERATOR",
        system=f"CHAR_{order}GRAM_KT", seed=seed,
        config={"stage": 1, "order": order, "alpha": 0.5, "line_reset": True},
        paths=selected, key_bits=universal_uint_bits(order), latent_bits=0.0,
        reconstruction_bits=source_bits + sum(fixed.values()), exception_bits=0.0,
        decoder=decoder,
    )


def edit_code_bits(program: str) -> float:
    if not program:
        return 1.0
    operations = program.split()
    total = universal_uint_bits(len(operations))
    for op in operations:
        total += 2.0
        if op.startswith("SUB"):
            total += math.log2(len(SOURCE_ALPHABET))
        elif op.startswith("INS"):
            total += math.log2(len(SOURCE_ALPHABET))
    return total


def copy_line_code(
    path: PathObservation, history: list[str], window: int,
) -> tuple[float, list[dict[str, Any]], list[str]]:
    bits = 0.0
    records: list[dict[str, Any]] = []
    next_history = list(history)
    for word in path.words:
        literal = 1.0 + universal_uint_bits(len(word)) + len(word) * math.log2(len(SOURCE_ALPHABET) - 1)
        best = (literal, "LITERAL", "", "")
        candidates = next_history[-window:]
        for reverse_index, source in enumerate(reversed(candidates), 1):
            _, program = levenshtein_program(source, word)
            cost = 1.0 + math.ceil(math.log2(max(1, len(candidates)))) + edit_code_bits(program)
            choice = (cost, "COPY_MODIFY", source, program)
            if choice < best:
                best = choice
        bits += best[0]
        records.append({"word": word, "mode": best[1], "source": best[2], "program": best[3], "bits": best[0]})
        next_history.append(word)
    return bits, records, next_history


def fit_copy_modify(lines: Sequence[LatticeLine], window: int, seed: int = 0) -> dict[str, Any]:
    histories: dict[str, list[str]] = defaultdict(list)
    selected: list[PathObservation] = []
    programs: list[dict[str, Any]] = []
    source_bits = 0.0
    for line in lines:
        candidates = []
        for path in line.paths:
            bits, records, history = copy_line_code(path, histories[line.page], window)
            candidates.append((bits + path.fixed_bits, path.path_id, path, records, history, bits))
        _, _, path, records, history, bits = min(candidates, key=lambda item: (item[0], item[1]))
        selected.append(path)
        programs.append({"locus": line.locus, "path_id": path.path_id, "words": records})
        histories[line.page] = history
        source_bits += bits
    fixed = fixed_costs(selected)
    decoder = {
        "schema": "GDT001_COPY_MODIFY_GENERATOR_V1", "window": window,
        "history_scope": "physical page", "literal_alphabet": SOURCE_ALPHABET[:-1],
        "edit_tie_order": "KEEP,SUBSTITUTE,DELETE,INSERT", "line_programs": programs,
        "decoded_output": "explicit source-copy provenance; no plaintext asserted",
    }
    return score_record(
        candidate_id=f"nonsemantic_copy_w{window}", model_class="NONSEMANTIC_GENERATOR",
        system=f"PAGE_COPY_MODIFY_W{window}", seed=seed,
        config={"stage": 1, "window": window, "history_scope": "page"},
        paths=selected, key_bits=universal_uint_bits(window), latent_bits=0.0,
        reconstruction_bits=source_bits + sum(fixed.values()), exception_bits=0.0,
        decoder=decoder,
    )


def fit_page_conditioned_unigram(lines: Sequence[LatticeLine], seed: int = 0) -> dict[str, Any]:
    selected = [line.paths[0] for line in lines]
    for _ in range(4):
        counts: dict[str, Counter[int]] = defaultdict(Counter)
        for line, path in zip(lines, selected):
            counts[line.page].update(path.source_ids)
        updated = []
        for line in lines:
            page_counts = counts[line.page]
            denominator = sum(page_counts.values()) + 0.5 * len(SOURCE_ALPHABET)
            costs = [-math.log2((page_counts.get(i, 0) + 0.5) / denominator) for i in range(len(SOURCE_ALPHABET))]
            candidates = [(sum(costs[i] for i in path.source_ids) + path.fixed_bits, path.path_id, path) for path in line.paths]
            updated.append(min(candidates, key=lambda item: (item[0], item[1]))[2])
        selected = updated
    by_page: dict[str, Counter[int]] = defaultdict(Counter)
    for line, path in zip(lines, selected):
        by_page[line.page].update(path.source_ids)
    source_bits = sum(categorical_bits([counter.get(i, 0) for i in range(len(SOURCE_ALPHABET))]) for counter in by_page.values())
    fixed = fixed_costs(selected)
    decoder = {
        "schema": "GDT001_PAGE_CONDITIONED_GENERATOR_V1", "alphabet": SOURCE_ALPHABET,
        "smoothing": "Dirichlet-1/2 integrated", "page_counts": {
            page: {SOURCE_ALPHABET[index]: count for index, count in sorted(counter.items())}
            for page, counter in sorted(by_page.items())
        }, "decoded_output": "source symbols only; no plaintext asserted",
    }
    return score_record(
        candidate_id="nonsemantic_page_unigram", model_class="NONSEMANTIC_GENERATOR",
        system="PAGE_CONDITIONED_UNIGRAM", seed=seed,
        config={"stage": 1, "conditioning": "page", "alpha": 0.5},
        paths=selected, key_bits=universal_uint_bits(len(by_page)), latent_bits=0.0,
        reconstruction_bits=source_bits + sum(fixed.values()), exception_bits=0.0,
        decoder=decoder,
    )
