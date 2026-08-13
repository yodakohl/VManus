#!/usr/bin/env python3
"""Common deterministic corpus and MDL primitives for GDT001."""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence


ROOT = Path(__file__).resolve().parent
LATTICE_PATH = ROOT / "gdt001_corpus_lattice.json"
LETTERS = "abcdefghijklmnopqrstuvxyz"  # exact 25-symbol modeled source alphabet (no w)
SOURCE_ALPHABET = LETTERS + " "
TARGET_ALPHABET = "abcdefghijklmnopqrstuvwxyz "
LN2 = math.log(2.0)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def canonical(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def universal_uint_bits(value: int) -> float:
    """Simple self-delimiting integer code for nonnegative values."""
    if value < 0:
        raise ValueError(value)
    n = value + 1
    width = n.bit_length()
    return float(2 * width - 1)


def categorical_bits(counts: Iterable[int], alpha: float = 0.5) -> float:
    values = list(counts)
    if not values:
        return 0.0
    total = sum(values)
    k = len(values)
    log_probability = math.lgamma(k * alpha) - math.lgamma(total + k * alpha)
    log_probability += sum(math.lgamma(value + alpha) - math.lgamma(alpha) for value in values)
    return -log_probability / LN2


def kt_ngram_bits(lines: Sequence[Sequence[int]], alphabet_size: int, order: int) -> float:
    """Exact Dirichlet-1/2 integrated n-gram code with line-reset contexts."""
    if order < 0:
        raise ValueError(order)
    contexts: dict[tuple[int, ...], Counter[int]] = defaultdict(Counter)
    bos = alphabet_size
    for line in lines:
        history = [bos] * order
        for token in line:
            contexts[tuple(history)][token] += 1
            if order:
                history = history[1:] + [token]
    return sum(categorical_bits([counter.get(symbol, 0) for symbol in range(alphabet_size)]) for counter in contexts.values())


def train_ngram_logprob(lines: Sequence[Sequence[int]], alphabet_size: int, order: int, alpha: float = 0.5) -> dict[tuple[int, ...], tuple[float, ...]]:
    contexts: dict[tuple[int, ...], Counter[int]] = defaultdict(Counter)
    bos = alphabet_size
    for line in lines:
        history = [bos] * order
        for token in line:
            contexts[tuple(history)][token] += 1
            if order:
                history = history[1:] + [token]
    output: dict[tuple[int, ...], tuple[float, ...]] = {}
    for context, counts in contexts.items():
        denominator = sum(counts.values()) + alpha * alphabet_size
        output[context] = tuple(-math.log2((counts.get(symbol, 0) + alpha) / denominator) for symbol in range(alphabet_size))
    return output


def kt_ngram_components(lines: Sequence[Sequence[int]], alphabet_size: int, order: int) -> tuple[float, list[dict[str, Any]]]:
    """Exact KT total plus canonical per-context sufficient statistics."""
    contexts: dict[tuple[int, ...], Counter[int]] = defaultdict(Counter)
    bos = alphabet_size
    for line in lines:
        history = [bos] * order
        for token in line:
            contexts[tuple(history)][token] += 1
            if order:
                history = history[1:] + [token]
    rows = []
    total = 0.0
    for context in sorted(contexts):
        counts = [contexts[context].get(symbol, 0) for symbol in range(alphabet_size)]
        bits = categorical_bits(counts); total += bits
        rows.append({"context": list(context), "counts": counts, "bits": bits})
    return total, rows


def ngram_cross_bits(lines: Sequence[Sequence[int]], table: dict[tuple[int, ...], tuple[float, ...]], alphabet_size: int, order: int, alpha_fallback: float = 0.5) -> float:
    bos = alphabet_size
    fallback = math.log2(alphabet_size)
    total = 0.0
    for line in lines:
        history = [bos] * order
        for token in line:
            values = table.get(tuple(history))
            total += values[token] if values is not None else fallback
            if order:
                history = history[1:] + [token]
    return total


@dataclass(frozen=True)
class PathObservation:
    path_id: str
    editions: tuple[str, ...]
    words: tuple[str, ...]
    source_line: str
    source_ids: tuple[int, ...]
    fixed_bits: float
    choice_bits: float
    raw_residual_bits: float
    separator_bits: float
    groups: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class LatticeLine:
    locus: str
    page: str
    section: str
    currier: str
    hand: str
    code: str
    kind: str
    grammar_scope: str
    paths: tuple[PathObservation, ...]


def group_raw_bits(group: dict[str, Any]) -> float:
    base = " ".join(group["clean_ascii_fragments"])
    raw = group["ivtff_group_raw"]
    if raw == base:
        return 1.0
    payload = raw.encode("utf-8")
    return 1.0 + universal_uint_bits(len(payload)) + 8.0 * len(payload)


def path_from_json(path: dict[str, Any]) -> PathObservation:
    words: list[str] = []
    groups = tuple(path["groups"])
    for group in groups:
        words.extend(group["clean_ascii_fragments"])
    source_line = " ".join(words)
    invalid = set(source_line) - set(SOURCE_ALPHABET)
    if invalid:
        raise ValueError(f"source alphabet drift at {path['path_id']}: {sorted(invalid)}")
    source_ids = tuple(SOURCE_ALPHABET.index(char) for char in source_line)
    raw = sum(group_raw_bits(group) for group in groups)
    # Each group's outgoing separator is one exact six-state event.
    separators = len(groups) * math.log2(6.0)
    choice = float(path["observation_choice_bits"])
    return PathObservation(
        path_id=path["path_id"], editions=tuple(path["edition_support"]), words=tuple(words),
        source_line=source_line, source_ids=source_ids,
        fixed_bits=raw + separators + choice, choice_bits=choice,
        raw_residual_bits=raw, separator_bits=separators, groups=groups,
    )


def load_lattice(path: Path = LATTICE_PATH) -> tuple[dict[str, Any], list[LatticeLine]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    lines = []
    for item in data["lines"]:
        lines.append(LatticeLine(
            locus=item["locus"], page=item["page"], section=item["section"],
            currier=item["currier"], hand=item["hand"], code=item["code"],
            kind=item["kind"], grammar_scope=item["grammar_scope"],
            paths=tuple(path_from_json(p) for p in item["alternatives"]),
        ))
    return data, lines


def select_paths(lines: Sequence[LatticeLine], scorer) -> tuple[list[PathObservation], float]:
    selected: list[PathObservation] = []
    total = 0.0
    for line in lines:
        scored = [(float(scorer(line, path)) + path.fixed_bits, path.path_id, path) for path in line.paths]
        bits, _, winner = min(scored, key=lambda item: (item[0], item[1]))
        selected.append(winner)
        total += bits
    return selected, total


def source_symbol_count(paths: Sequence[PathObservation]) -> int:
    return sum(sum(char != " " for char in path.source_line) for path in paths)


def physical_line_count(paths: Sequence[PathObservation]) -> int:
    return len(paths)


def fixed_costs(paths: Sequence[PathObservation]) -> dict[str, float]:
    return {
        "observation_choice_bits": sum(path.choice_bits for path in paths),
        "raw_residual_bits": sum(path.raw_residual_bits for path in paths),
        "separator_bits": sum(path.separator_bits for path in paths),
    }


def words(paths: Sequence[PathObservation]) -> list[str]:
    return [word for path in paths for word in path.words]


def lines_by_page(lines: Sequence[LatticeLine], paths: Sequence[PathObservation]) -> dict[str, list[tuple[LatticeLine, PathObservation]]]:
    result: dict[str, list[tuple[LatticeLine, PathObservation]]] = defaultdict(list)
    for line, path in zip(lines, paths):
        result[line.page].append((line, path))
    return result


def levenshtein_program(source: str, target: str) -> tuple[int, str]:
    """Canonical unit-cost edit distance and human-readable tied-preference program."""
    previous = list(range(len(target) + 1))
    back: list[list[str]] = [["I"] * (len(target) + 1) for _ in range(len(source) + 1)]
    back[0][0] = ""
    for i in range(1, len(source) + 1):
        back[i][0] = "D"
    for i, char_s in enumerate(source, 1):
        current = [i]
        for j, char_t in enumerate(target, 1):
            candidates = [
                (previous[j - 1] + (char_s != char_t), "K" if char_s == char_t else "S"),
                (previous[j] + 1, "D"),
                (current[j - 1] + 1, "I"),
            ]
            cost, op = min(candidates, key=lambda item: (item[0], "KSDI".index(item[1])))
            current.append(cost)
            back[i][j] = op
        previous = current
    i, j = len(source), len(target)
    ops: list[str] = []
    while i or j:
        op = back[i][j]
        if op == "K":
            ops.append(f"KEEP({source[i-1]})"); i -= 1; j -= 1
        elif op == "S":
            ops.append(f"SUB({source[i-1]}>{target[j-1]})"); i -= 1; j -= 1
        elif op == "D":
            ops.append(f"DEL({source[i-1]})"); i -= 1
        else:
            ops.append(f"INS({target[j-1]})"); j -= 1
    ops.reverse()
    return previous[-1], " ".join(ops)


def score_record(
    *, candidate_id: str, model_class: str, system: str, seed: int, config: dict[str, Any],
    paths: Sequence[PathObservation], key_bits: float, latent_bits: float,
    reconstruction_bits: float, exception_bits: float, model_class_bits: float = 3.0,
    convergence_status: str = "CONVERGED", decoder: dict[str, Any] | None = None,
) -> dict[str, Any]:
    fixed = fixed_costs(paths)
    total = model_class_bits + key_bits + latent_bits + reconstruction_bits + exception_bits
    decoder = decoder or {}
    return {
        "candidate_id": candidate_id,
        "status": "EXPLORATORY_NOT_CONFIRMED_TRANSLATION",
        "model_class": model_class,
        "language_or_system": system,
        "seed": seed,
        "config": config,
        "config_hash": sha256_bytes(canonical(config)),
        "total_bits": total,
        "bits_per_symbol": total / source_symbol_count(paths),
        "bits_per_physical_line": total / len(paths),
        "model_class_bits": model_class_bits,
        "key_bits": key_bits,
        "latent_bits": latent_bits,
        "reconstruction_bits": reconstruction_bits,
        "exception_bits": exception_bits,
        "observation_choice_bits": fixed["observation_choice_bits"],
        "raw_residual_bits": fixed["raw_residual_bits"],
        "separator_bits": fixed["separator_bits"],
        "source_symbols": source_symbol_count(paths),
        "physical_lines": len(paths),
        "selected_path_ids": [path.path_id for path in paths],
        "selected_path_digest": sha256_bytes(canonical([path.path_id for path in paths])),
        "convergence_status": convergence_status,
        "decoder": decoder,
        "decoder_hash": sha256_bytes(canonical(decoder)),
    }
