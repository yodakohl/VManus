#!/usr/bin/env python3
"""Explicit RECORD_NOTATION and manuscript-driven procedural hybrid models."""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from typing import Any, Sequence

from gdt001_core import (
    LETTERS, SOURCE_ALPHABET, LatticeLine, PathObservation, categorical_bits,
    fixed_costs, score_record, universal_uint_bits,
)


PREFIXES = ("q", "d", "s", "l", "r", "k", "p", "t", "f")
SUFFIXES = ("y", "n", "r", "l", "m", "s", "d", "g")


def decompose(word: str) -> tuple[str, str, str]:
    prefix = word[0] if len(word) > 1 and word[0] in PREFIXES else ""
    rest = word[len(prefix):]
    suffix = rest[-1] if len(rest) > 1 and rest[-1] in SUFFIXES else ""
    core = rest[:len(rest) - len(suffix)] if suffix else rest
    return prefix, core, suffix


def record_tokens(path: PathObservation, role_sensitive: bool) -> tuple[list[str], list[dict[str, Any]]]:
    tokens: list[str] = []
    records: list[dict[str, Any]] = []
    for position, word in enumerate(path.words):
        prefix, core, suffix = decompose(word)
        role = "ENTRY" if position == 0 else "FIELD"
        if role_sensitive:
            tokens.append(f"ROLE:{role}")
        tokens.extend((f"PRE:{prefix or '_'}", f"CORE:{core or '_'}", f"SUF:{suffix or '_'}"))
        records.append({"source": word, "record_position": position + 1, "role": role, "prefix": prefix, "core": core, "suffix": suffix})
    return tokens, records


def integrated_token_bits(sequences: Sequence[Sequence[str]]) -> float:
    vocabulary = sorted({token for sequence in sequences for token in sequence})
    index = {token: i for i, token in enumerate(vocabulary)}
    counts = Counter(index[token] for sequence in sequences for token in sequence)
    return categorical_bits([counts[i] for i in range(len(vocabulary))]) + universal_uint_bits(len(vocabulary))


def record_path_bits(path: PathObservation, probabilities: dict[str, float], role_sensitive: bool) -> float:
    tokens, _ = record_tokens(path, role_sensitive)
    fallback = max(probabilities.values(), default=math.log2(2)) + 8.0
    return sum(probabilities.get(token, fallback) for token in tokens)


def fit_record_notation(lines: Sequence[LatticeLine], role_sensitive: bool = True, seed: int = 0) -> dict[str, Any]:
    selected = [line.paths[0] for line in lines]
    for _ in range(5):
        counts = Counter(token for path in selected for token in record_tokens(path, role_sensitive)[0])
        vocabulary = sorted(counts)
        denominator = sum(counts.values()) + 0.5 * len(vocabulary)
        probabilities = {token: -math.log2((counts[token] + 0.5) / denominator) for token in vocabulary}
        updated = []
        for line in lines:
            candidates = [(record_path_bits(path, probabilities, role_sensitive) + path.fixed_bits, path.path_id, path) for path in line.paths]
            updated.append(min(candidates, key=lambda item: (item[0], item[1]))[2])
        if [p.path_id for p in updated] == [p.path_id for p in selected]:
            selected = updated
            break
        selected = updated
    sequences = [record_tokens(path, role_sensitive)[0] for path in selected]
    latent = integrated_token_bits(sequences)
    fixed = fixed_costs(selected)
    cores = Counter(); prefixes = Counter(); suffixes = Counter(); role_cores: dict[str, Counter[str]] = defaultdict(Counter)
    line_records = []
    for line, path in zip(lines, selected):
        _, records = record_tokens(path, role_sensitive)
        for record in records:
            prefixes[record["prefix"] or "_"] += 1; cores[record["core"] or "_"] += 1; suffixes[record["suffix"] or "_"] += 1
            role_cores[record["role"]][record["core"] or "_"] += 1
        line_records.append({"locus": line.locus, "section": line.section, "currier": line.currier, "records": records})
    core_ids = {core: f"VALUE_{index:04d}" for index, (core, _) in enumerate(cores.most_common(), 1)}
    # The dictionary pays for every source-side string exactly once. Occurrences
    # are then encoded as anonymous latent IDs; reconstruction is deterministic.
    dictionary_bits = sum(
        universal_uint_bits(len(value)) + len(value) * math.log2(len(LETTERS))
        for inventory in (prefixes, cores, suffixes) for value in inventory if value != "_"
    )
    decoder = {
        "schema": "GDT001_RECORD_NOTATION_V1", "word_rule": "optional one-character prefix + nonempty core + optional one-character suffix",
        "prefix_inventory": PREFIXES, "suffix_inventory": SUFFIXES,
        "record_rule": "ENTRY field then zero or more FIELD fields per physical line",
        "anonymous_values": [{"source_core": core, "latent_value": core_ids[core], "occurrences": count} for core, count in cores.most_common()],
        "anonymous_operators": [{"source_prefix": prefix, "latent_operator": f"OP_{i:02d}", "occurrences": count} for i, (prefix, count) in enumerate(prefixes.most_common(), 1)],
        "anonymous_states": [{"source_suffix": suffix, "latent_state": f"STATE_{i:02d}", "occurrences": count} for i, (suffix, count) in enumerate(suffixes.most_common(), 1)],
        "line_records": line_records,
    }
    return score_record(
        candidate_id="record_notation_entry_fields" if role_sensitive else "record_notation_fields",
        model_class="RECORD_NOTATION", system="ENTRY_PREFIX_CORE_SUFFIX", seed=seed,
        config={"stage": 1, "role_sensitive": role_sensitive, "prefix_inventory": PREFIXES, "suffix_inventory": SUFFIXES},
        paths=selected, key_bits=universal_uint_bits(len(PREFIXES)) + universal_uint_bits(len(SUFFIXES)) + dictionary_bits,
        latent_bits=latent, reconstruction_bits=sum(fixed.values()), exception_bits=0.0,
        decoder=decoder,
    )


def fit_dual_channel_hybrid(lines: Sequence[LatticeLine], seed: int = 0) -> dict[str, Any]:
    """Own theory: line-entry state plus reusable body stem/modifier programs."""
    selected = [line.paths[0] for line in lines]
    # Frozen manuscript-driven state: first word prefix; body retains fields.
    state_counts = Counter()
    body_sequences = []
    for path in selected:
        if path.words:
            state_counts[decompose(path.words[0])[0] or "_"] += 1
        body_sequences.append([component for word in path.words[1:] for component in (f"C:{decompose(word)[1]}", f"S:{decompose(word)[2] or '_'}")])
    latent = categorical_bits([state_counts[key] for key in sorted(state_counts)]) + integrated_token_bits(body_sequences)
    fixed = fixed_costs(selected)
    transitions: Counter[tuple[str, str]] = Counter()
    by_page: dict[str, list[str]] = defaultdict(list)
    line_programs = []
    for line, path in zip(lines, selected):
        first = decompose(path.words[0])[0] or "_" if path.words else "EMPTY"
        prior = by_page[line.page][-1] if by_page[line.page] else "BOS"
        transitions[(prior, first)] += 1; by_page[line.page].append(first)
        body = []
        for word in path.words[1:]:
            prefix, core, suffix = decompose(word)
            body.append({"source": word, "program": [f"STEM({core})", f"MOD_PREFIX({prefix or '_'})", f"MOD_SUFFIX({suffix or '_'})"]})
        line_programs.append({"locus": line.locus, "entry_state": f"ENTRY_{first}", "body": body})
    latent += sum(categorical_bits([count for (_, _), count in group]) for _, group in _group_transitions(transitions).items())
    stems = {decompose(word)[1] for path in selected for word in path.words}
    dictionary_bits = sum(universal_uint_bits(len(stem)) + len(stem) * math.log2(len(LETTERS)) for stem in stems)
    decoder = {
        "schema": "GDT001_DUAL_CHANNEL_PROCEDURAL_V1",
        "theory_origin": "CODEX_SELF_ORIGINATED",
        "entry_channel": "first source group prefix defines line-entry state; page-order Markov transitions",
        "body_channel": "later groups decompose into reusable STEM + PREFIX/SUFFIX modifier program",
        "entry_states": [{"state": f"ENTRY_{key}", "occurrences": value} for key, value in sorted(state_counts.items())],
        "transition_counts": [{"from": a, "to": b, "count": n} for (a, b), n in sorted(transitions.items())],
        "line_programs": line_programs,
        "risky_mechanistic_prediction": "entry-state distributions should transfer across sections more strongly than complete word identities",
    }
    return score_record(
        candidate_id="hybrid_dual_channel_entry_body", model_class="HYBRID",
        system="ENTRY_STATE_PLUS_STEM_MODIFIER", seed=seed,
        config={"stage": 1, "self_originated": True, "entry_position": 1, "page_transition": True},
        paths=selected, key_bits=universal_uint_bits(len(PREFIXES)) + 12.0 + dictionary_bits,
        latent_bits=latent, reconstruction_bits=sum(fixed.values()), exception_bits=0.0,
        decoder=decoder,
    )


def fit_record_dictionary(lines: Sequence[LatticeLine], order: int = 1, seed: int = 0) -> dict[str, Any]:
    """Anonymous record-value dictionary with an exact line-reset Markov code.

    This is deliberately a real alternative to character language: complete
    source groups are reusable opaque VALUEs, and their ordering is generated
    by a compact record-state model.  The dictionary is paid once in full.
    """
    if order not in (0, 1, 2):
        raise ValueError(order)
    selected = [line.paths[0] for line in lines]
    inventory = sorted({word for line in lines for path in line.paths for word in path.words})
    value_id = {word: index for index, word in enumerate(inventory)}
    bos = len(inventory)
    contexts: dict[tuple[int, ...], Counter[int]] = defaultdict(Counter)
    for path in selected:
        history = [bos] * order
        for word in path.words:
            token = value_id[word]
            contexts[tuple(history)][token] += 1
            if order:
                history = history[1:] + [token]
    latent = sum(
        # Exact Dirichlet-1/2 categorical code; zero-count members contribute
        # zero to the member sum, so do not materialize K entries per context.
        -(
            math.lgamma(0.5 * len(inventory))
            - math.lgamma(sum(counter.values()) + 0.5 * len(inventory))
            + sum(math.lgamma(count + 0.5) - math.lgamma(0.5) for count in counter.values())
        ) / math.log(2.0)
        for counter in contexts.values()
    )
    dictionary_bits = universal_uint_bits(len(inventory)) + sum(
        universal_uint_bits(len(word)) + len(word) * math.log2(len(LETTERS))
        for word in inventory
    )
    fixed = fixed_costs(selected)
    counts = Counter(word for path in selected for word in path.words)
    decoder = {
        "schema": "GDT001_ANONYMOUS_RECORD_DICTIONARY_V1",
        "theory_origin": "CODEX_SELF_ORIGINATED",
        "segmentation_rule": "manual source groups are complete anonymous record values",
        "line_reset": True,
        "markov_order": order,
        "dictionary": [
            {"source_group": word, "latent_value": f"VALUE_{value_id[word]:05d}", "occurrences": counts[word]}
            for word in inventory
        ],
        "line_records": [
            {"locus": line.locus, "values": [f"VALUE_{value_id[word]:05d}" for word in path.words]}
            for line, path in zip(lines, selected)
        ],
    }
    return score_record(
        candidate_id=f"record_notation_dictionary_o{order}", model_class="RECORD_NOTATION",
        system=f"ANONYMOUS_VALUE_DICTIONARY_{order}GRAM", seed=seed,
        config={"stage": 2, "self_originated": True, "record_markov_order": order},
        paths=selected, key_bits=dictionary_bits + universal_uint_bits(order),
        latent_bits=latent, reconstruction_bits=sum(fixed.values()), exception_bits=0.0,
        decoder=decoder,
    )


def _group_transitions(transitions: Counter[tuple[str, str]]) -> dict[str, list[tuple[tuple[str, str], int]]]:
    output: dict[str, list[tuple[tuple[str, str], int]]] = defaultdict(list)
    for pair, count in transitions.items():
        output[pair[0]].append((pair, count))
    return output
