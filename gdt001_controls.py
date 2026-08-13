#!/usr/bin/env python3
"""Deterministic counterfactual manuscripts and cross-model control scorer."""

from __future__ import annotations

import hashlib
import json
import random
from dataclasses import replace
from typing import Sequence

from gdt001_core import LatticeLine, PathObservation, SOURCE_ALPHABET, canonical


CONTROL_NAMES = (
    "WITHIN_LINE_SYMBOL_SHUFFLE",
    "PAGE_CONDITIONED_SYMBOL_SHUFFLE",
    "BOUNDARY_PRESERVING_IDENTITY_PERMUTATION",
    "SYMBOL_FREQUENCY_PRESERVING_GLOBAL_SHUFFLE",
    "TIMM_COPY_MODIFY_SYNTHETIC",
)


def seed_for(name: str, locus: str, seed: int) -> int:
    data = f"GDT001_CONTROL_V1|{name}|{seed}|{locus}".encode()
    return int.from_bytes(hashlib.sha256(data).digest()[:8], "big")


def with_text(path: PathObservation, text: str) -> PathObservation:
    words = tuple(text.split(" "))
    return replace(
        path, words=words, source_line=text,
        source_ids=tuple(SOURCE_ALPHABET.index(char) for char in text),
        path_id=path.path_id + "|CONTROL",
    )


def transform(lines: Sequence[LatticeLine], paths: Sequence[PathObservation], name: str, seed: int = 9401) -> list[PathObservation]:
    if name not in CONTROL_NAMES:
        raise ValueError(name)
    output: list[PathObservation] = []
    if name == "PAGE_CONDITIONED_SYMBOL_SHUFFLE":
        pools: dict[str, list[str]] = {}
        for line, path in zip(lines, paths):
            pools.setdefault(line.page, []).extend(char for char in path.source_line if char != " ")
        for page, pool in pools.items():
            random.Random(seed_for(name, page, seed)).shuffle(pool)
        offsets = {page: 0 for page in pools}
    elif name == "SYMBOL_FREQUENCY_PRESERVING_GLOBAL_SHUFFLE":
        pool = [char for path in paths for char in path.source_line if char != " "]
        random.Random(seed_for(name, "GLOBAL", seed)).shuffle(pool)
        offset = 0
    elif name == "BOUNDARY_PRESERVING_IDENTITY_PERMUTATION":
        alphabet = list(SOURCE_ALPHABET[:-1]); permuted = list(alphabet)
        random.Random(seed_for(name, "GLOBAL", seed)).shuffle(permuted)
        mapping = dict(zip(alphabet, permuted))
    history: dict[str, list[str]] = {}
    for line, path in zip(lines, paths):
        text = path.source_line
        if name == "WITHIN_LINE_SYMBOL_SHUFFLE":
            symbols = [char for char in text if char != " "]
            random.Random(seed_for(name, line.locus, seed)).shuffle(symbols)
            iterator = iter(symbols); text = "".join(char if char == " " else next(iterator) for char in text)
        elif name == "PAGE_CONDITIONED_SYMBOL_SHUFFLE":
            count = sum(char != " " for char in text); start = offsets[line.page]
            symbols = iter(pools[line.page][start:start + count]); offsets[line.page] += count
            text = "".join(char if char == " " else next(symbols) for char in text)
        elif name == "BOUNDARY_PRESERVING_IDENTITY_PERMUTATION":
            text = "".join(mapping.get(char, char) for char in text)
        elif name == "SYMBOL_FREQUENCY_PRESERVING_GLOBAL_SHUFFLE":
            count = sum(char != " " for char in text); symbols = iter(pool[offset:offset + count]); offset += count
            text = "".join(char if char == " " else next(symbols) for char in text)
        elif name == "TIMM_COPY_MODIFY_SYNTHETIC":
            rng = random.Random(seed_for(name, line.locus, seed)); words = []
            page_history = history.setdefault(line.page, [])
            for source_word in path.words:
                if page_history and rng.random() < 0.78:
                    word = list(rng.choice(page_history[-32:]))
                    operation = rng.randrange(3)
                    if operation == 0 and word: word.pop(rng.randrange(len(word)))
                    elif operation == 1: word.insert(rng.randrange(len(word) + 1), rng.choice(SOURCE_ALPHABET[:-1]))
                    elif word: word[rng.randrange(len(word))] = rng.choice(SOURCE_ALPHABET[:-1])
                    word = "".join(word) or source_word
                else:
                    word = source_word
                words.append(word); page_history.append(word)
            text = " ".join(words)
        output.append(with_text(path, text))
    return output


def manifest(lines: Sequence[LatticeLine], paths: Sequence[PathObservation], seed: int = 9401) -> dict[str, object]:
    return {
        "schema": "GDT001_COUNTERFACTUAL_MANIFEST_V2", "seed": seed,
        "observation_lattice_policy": "transform every alternative path; retain exact original fixed observation cost",
        "controls": [{
            "name": name,
            "path_digest": hashlib.sha256(canonical([path.source_line for path in transform(lines, paths, name, seed)])).hexdigest(),
        } for name in CONTROL_NAMES],
    }
