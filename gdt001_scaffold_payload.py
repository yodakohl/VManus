#!/usr/bin/env python3
"""Shared structural-scaffold / latent-payload models for the fast GDT001 follow-up."""

from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from dataclasses import replace
from typing import Any, Sequence

import numpy as np

from gdt001_core import (
    LETTERS, SOURCE_ALPHABET, LatticeLine, PathObservation, categorical_bits,
    fixed_costs, kt_ngram_bits, score_record, universal_uint_bits,
)
from gdt001_language_models import (
    TARGET_LETTERS, evolve_mapping, explicit_mapping, homophone_reverse_bits,
    path_language_bits, source_unigrams, train_pack,
)
from gdt001_record_models import PREFIXES, SUFFIXES, decompose


def common_selected_paths(lines: Sequence[LatticeLine]) -> list[PathObservation]:
    run = json.loads((__import__("pathlib").Path(__file__).parent / ".gdt001/runs/nonsemantic_ngram_o2.json").read_text())
    output = []
    for line, path_id in zip(lines, run["selected_path_ids"]):
        output.append(next(path for path in line.paths if path.path_id == path_id))
    return output


def scaffold_and_payload(paths: Sequence[PathObservation]) -> tuple[float, list[PathObservation], dict[str, Any]]:
    prefix_counts: dict[str, Counter[str]] = defaultdict(Counter)
    suffix_counts: dict[str, Counter[str]] = defaultdict(Counter)
    payloads = []
    rows = []
    for path in paths:
        cores = []; records = []
        for index, word in enumerate(path.words):
            prefix, core, suffix = decompose(word); role = "ENTRY" if index == 0 else "BODY"
            prefix_counts[role][prefix or "_"] += 1; suffix_counts[role][suffix or "_"] += 1
            cores.append(core); records.append({"source": word, "role": role, "prefix": prefix or "_", "core": core, "suffix": suffix or "_"})
        text = " ".join(cores)
        payloads.append(replace(path, words=tuple(cores), source_line=text,
                                source_ids=tuple(SOURCE_ALPHABET.index(char) for char in text),
                                fixed_bits=0.0, choice_bits=0.0, raw_residual_bits=0.0, separator_bits=0.0))
        rows.append(records)
    bits = 0.0
    for counters in (prefix_counts, suffix_counts):
        for role in ("ENTRY", "BODY"):
            values = counters[role]
            bits += categorical_bits([values[key] for key in sorted(values)])
    decoder = {
        "schema": "GDT001_SHARED_SCAFFOLD_V1",
        "word_program": "ROLE + optional one-character PREFIX + PAYLOAD_CORE + optional one-character SUFFIX",
        "roles": ["ENTRY", "BODY"], "prefix_inventory": list(PREFIXES), "suffix_inventory": list(SUFFIXES),
        "prefix_counts": {role: dict(sorted(prefix_counts[role].items())) for role in ("ENTRY", "BODY")},
        "suffix_counts": {role: dict(sorted(suffix_counts[role].items())) for role in ("ENTRY", "BODY")},
        "line_programs": rows,
    }
    return bits, payloads, decoder


def scaffold_rule_bits() -> float:
    return universal_uint_bits(len(PREFIXES)) + universal_uint_bits(len(SUFFIXES)) + sum(
        universal_uint_bits(len(value)) + len(value) * math.log2(len(LETTERS))
        for value in (*PREFIXES, *SUFFIXES)
    )


def fit_scaffold_null(lines: Sequence[LatticeLine], order: int = 2) -> dict[str, Any]:
    selected = common_selected_paths(lines); scaffold_bits, payloads, scaffold = scaffold_and_payload(selected)
    payload_bits = kt_ngram_bits([path.source_ids for path in payloads], len(SOURCE_ALPHABET), order)
    fixed = sum(fixed_costs(selected).values())
    decoder = {"schema": "GDT001_SCAFFOLD_NULL_V1", "scaffold": scaffold,
               "payload_model": {"kind": "SOURCE_KT_NGRAM", "order": order, "line_reset": True},
               "reconstruction": "concatenate scaffold prefix + exact payload core + suffix at every manual group"}
    return score_record(
        candidate_id=f"scaffold_null_payload_o{order}", model_class="NONSEMANTIC_GENERATOR",
        system=f"SHARED_SCAFFOLD_CORE_{order}GRAM", seed=0,
        config={"stage": "FAST_SCAFFOLD", "common_paths": "nonsemantic_ngram_o2", "payload_order": order},
        paths=selected, key_bits=scaffold_rule_bits() + universal_uint_bits(order), latent_bits=scaffold_bits,
        reconstruction_bits=payload_bits + fixed, exception_bits=0.0, decoder=decoder,
    ) | {"scaffold_bits": scaffold_bits, "payload_bits": payload_bits, "common_fixed_bits": fixed}


def fit_scaffold_record(lines: Sequence[LatticeLine]) -> dict[str, Any]:
    selected = common_selected_paths(lines); scaffold_bits, payloads, scaffold = scaffold_and_payload(selected)
    counts = Counter(core for path in payloads for core in path.words); inventory = sorted(counts)
    dictionary_bits = universal_uint_bits(len(inventory)) + sum(
        universal_uint_bits(len(core)) + len(core) * math.log2(len(LETTERS)) for core in inventory
    )
    occurrence_bits = categorical_bits([counts[core] for core in inventory])
    fixed = sum(fixed_costs(selected).values()); values = {core: f"VALUE_{i:05d}" for i, core in enumerate(inventory)}
    decoder = {"schema": "GDT001_SCAFFOLD_RECORD_V1", "scaffold": scaffold,
               "payload_model": {"kind": "ANONYMOUS_CORE_VALUE", "dictionary": [{"core": core, "value": values[core], "occurrences": counts[core]} for core in inventory]},
               "reconstruction": "anonymous value dictionary reverses exactly to core; scaffold supplies affixes"}
    return score_record(
        candidate_id="scaffold_record_payload", model_class="RECORD_NOTATION", system="SHARED_SCAFFOLD_ANONYMOUS_CORE", seed=0,
        config={"stage": "FAST_SCAFFOLD", "common_paths": "nonsemantic_ngram_o2", "payload": "CORE_DICTIONARY"},
        paths=selected, key_bits=scaffold_rule_bits() + dictionary_bits, latent_bits=scaffold_bits + occurrence_bits,
        reconstruction_bits=fixed, exception_bits=0.0, decoder=decoder,
    ) | {"scaffold_bits": scaffold_bits, "payload_bits": occurrence_bits, "common_fixed_bits": fixed}


def fit_scaffold_language(
    lines: Sequence[LatticeLine], seed: int, population_size: int = 32768, generations: int = 40,
) -> dict[str, Any]:
    selected = common_selected_paths(lines); scaffold_bits, payloads, scaffold = scaffold_and_payload(selected)
    lm = train_pack("middle_high_german", 2)
    mapping, _, search = evolve_mapping(lm, payloads, seed=seed, injective=False,
                                         population_size=population_size, generations=generations, cuda=True)
    lm_bits = sum(path_language_bits(lm, mapping, path) for path in payloads)
    reverse = homophone_reverse_bits(mapping, source_unigrams(payloads))
    fixed = sum(fixed_costs(selected).values())
    key = scaffold_rule_bits() + math.log2(6) + len(LETTERS) * math.log2(len(TARGET_LETTERS)) + universal_uint_bits(2)
    decoder = {"schema": "GDT001_SCAFFOLD_LANGUAGE_V1", "scaffold": scaffold,
               "payload_model": {"kind": "HOMOPHONIC_MIDDLE_HIGH_GERMAN_CORE", "mapping": explicit_mapping(mapping, True, payloads), "lm_order": 2},
               "reconstruction": "language LM emits latent core letters; explicit reverse homophone code recovers source core; scaffold supplies affixes"}
    return score_record(
        candidate_id=f"scaffold_language_mhg_s{seed:04d}", model_class="ABBR_LANG", system="SHARED_SCAFFOLD_MHG_CORE", seed=seed,
        config={"stage": "FAST_SCAFFOLD", "common_paths": "nonsemantic_ngram_o2", "population_size": population_size, "generations": generations, "lm_order": 2},
        paths=selected, key_bits=key, latent_bits=scaffold_bits + lm_bits,
        reconstruction_bits=reverse + fixed, exception_bits=0.0, decoder=decoder,
    ) | {"scaffold_bits": scaffold_bits, "payload_language_bits": lm_bits, "payload_reverse_bits": reverse,
         "common_fixed_bits": fixed, "search": search}
