#!/usr/bin/env python3
"""Ciphertext-only U versus P+S factorizer used by GDT604.

This is the path-free library form of the frozen Poisson-deviance method.  It
contains no control plaintext, alignment, table, target folio, or oracle key.
"""
from __future__ import annotations

import math
from collections import Counter, defaultdict


ACTIVE_LATIN = "abcdefghilmnopqrstuvxyz"
TABLES = 6
CAPACITY = len(ACTIVE_LATIN) * TABLES


def cuts(token: str):
    return range(1, len(token))


def greedy_side(side: str, other: set[str], bigram_types: set[str], freq: Counter):
    incidence: dict[str, set[str]] = defaultdict(set)
    for token in bigram_types:
        for cut in cuts(token):
            prefix, suffix = token[:cut], token[cut:]
            if side == "P" and suffix in other:
                incidence[prefix].add(token)
            elif side == "S" and prefix in other:
                incidence[suffix].add(token)
    selected: set[str] = set()
    covered: set[str] = set()
    for _ in range(CAPACITY):
        best = None
        best_key = None
        for component, support in incidence.items():
            new = support - covered
            key = (
                len(new),
                sum(min(freq[token], 5) for token in new),
                -len(component),
                component,
            )
            if best_key is None or key > best_key:
                best, best_key = component, key
        if best is None or best_key[0] == 0:
            break
        selected.add(best)
        covered.update(incidence.pop(best))
    return selected


def initial_suffixes(unigrams: set[str], types: set[str]):
    bigrams = types - unigrams
    prefix_support = Counter()
    suffix_support = Counter()
    for token in bigrams:
        for cut in cuts(token):
            prefix_support[token[:cut]] += 1
            suffix_support[token[cut:]] += 1
    assignment = {}
    for token in bigrams:
        candidates = []
        for cut in cuts(token):
            a = prefix_support[token[:cut]]
            b = suffix_support[token[cut:]]
            harmonic = 2.0 / (1.0 / a + 1.0 / b)
            candidates.append((harmonic, -cut, cut))
        if candidates:
            assignment[token] = max(candidates)[2]
    return {
        component
        for component, _ in Counter(
            token[cut:] for token, cut in assignment.items()
        ).most_common(CAPACITY)
    }


def induce_dictionaries(unigrams, suffixes, types, freq):
    bigrams = types - unigrams
    for _ in range(3):
        prefixes = greedy_side("P", suffixes, bigrams, freq)
        suffixes = greedy_side("S", prefixes, bigrams, freq)
    prefixes = greedy_side("P", suffixes, bigrams, freq)
    return prefixes, suffixes


def fit_cuts(unigrams, prefixes, suffixes, types, freq):
    bigrams = types - unigrams
    assignment = {}
    for token in bigrams:
        viable = [
            cut for cut in cuts(token)
            if token[:cut] in prefixes and token[cut:] in suffixes
        ]
        if viable:
            assignment[token] = viable[0]
    for _ in range(6):
        prefix_count = Counter()
        suffix_count = Counter()
        for token, cut in assignment.items():
            prefix_count[token[:cut]] += freq[token]
            suffix_count[token[cut:]] += freq[token]
        for token in bigrams:
            viable = [
                cut for cut in cuts(token)
                if token[:cut] in prefixes and token[cut:] in suffixes
            ]
            if viable:
                assignment[token] = max(
                    viable,
                    key=lambda cut: (
                        (prefix_count[token[:cut]] + 0.5)
                        * (suffix_count[token[cut:]] + 0.5),
                        -cut,
                    ),
                )
    return assignment, prefix_count, suffix_count


def fit_target_variant(u_size: int, freq: Counter):
    """Fit on training types and retain capacity failures as UNKNOWN."""
    types = set(freq)
    unigrams = {token for token, _ in freq.most_common(u_size)}
    suffixes = initial_suffixes(unigrams, types)
    for _ in range(6):
        prefixes, suffixes = induce_dictionaries(unigrams, suffixes, types, freq)
        assignment, prefix_count, suffix_count = fit_cuts(
            unigrams, prefixes, suffixes, types, freq
        )
        n_bigram = sum(freq[token] for token in assignment)
        evidence = []
        for token, observed in freq.items():
            viable = [
                cut for cut in cuts(token)
                if token[:cut] in prefixes and token[cut:] in suffixes
            ]
            if not viable:
                deviance = float("inf")
            else:
                expected = max(
                    (prefix_count[token[:cut]] + 0.5)
                    * (suffix_count[token[cut:]] + 0.5)
                    / (n_bigram + 0.5 * max(1, len(prefixes)))
                    for cut in viable
                )
                deviance = (
                    observed * math.log(observed / expected) - observed + expected
                    if observed > expected else 0.0
                )
            evidence.append((deviance, token))
        updated = {token for _, token in sorted(evidence, reverse=True)[:u_size]}
        if updated == unigrams:
            break
        unigrams = updated
    prefixes, suffixes = induce_dictionaries(unigrams, suffixes, types, freq)
    assignment, prefix_count, suffix_count = fit_cuts(
        unigrams, prefixes, suffixes, types, freq
    )
    token_map = {}
    for token in sorted(types):
        if token in unigrams:
            token_map[token] = {"state": "U"}
        elif token in assignment:
            token_map[token] = {"state": "B", "cut": assignment[token]}
        else:
            token_map[token] = {"state": "UNKNOWN"}
    return token_map, prefix_count, suffix_count

