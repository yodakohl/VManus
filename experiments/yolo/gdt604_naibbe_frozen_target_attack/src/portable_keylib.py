#!/usr/bin/env python3
"""Self-contained capacity-constrained homophone-key annealer for GDT604."""
from __future__ import annotations

import math
from collections import Counter, defaultdict

import numpy as np


ALPHABET = "abcdefghijklmnopqrstuvwxyz "
SPACE_ID = ALPHABET.index(" ")
LATIN_LETTERS = "abcdefghilmnopqrstuvxyz"
LATIN_IDS = np.array([ALPHABET.index(c) for c in LATIN_LETTERS], dtype=np.int64)
CAPACITY = 6


def build_stream(lines):
    counts = Counter(unit for line in lines for unit in line)
    vocab = [unit for unit, _ in counts.most_common()]
    ids = {unit: i for i, unit in enumerate(vocab)}
    obs = []
    for line_no, line in enumerate(lines):
        if line_no:
            obs.append(len(vocab))
        obs.extend(ids[unit] for unit in line)
    return vocab, counts, np.asarray(obs, dtype=np.int64)


class IncrementalKey:
    def __init__(self, obs, n_codes, lm, key):
        self.obs = obs
        self.lm = lm
        self.order = lm.order
        self.key = key.copy()
        self.decoded = self.key[self.obs]
        self.padded = np.concatenate((
            np.full(self.order - 1, SPACE_ID, dtype=np.int64), self.decoded
        ))
        self.positions = [np.flatnonzero(obs == i) for i in range(n_codes)]
        n = len(obs)
        self.affected = []
        for positions in self.positions:
            if len(positions):
                endpoints = np.unique(np.concatenate([
                    np.arange(p, min(n, p + self.order), dtype=np.int64)
                    for p in positions
                ]))
            else:
                endpoints = np.empty(0, dtype=np.int64)
            self.affected.append(endpoints)
        endpoints = np.arange(len(obs), dtype=np.int64)
        self.endpoint_scores = self._scores(endpoints)
        self.total = float(self.endpoint_scores.sum())

    def _scores(self, endpoints):
        index = np.zeros(len(endpoints), dtype=np.int64)
        for offset in range(self.order):
            index = index * len(ALPHABET) + self.padded[endpoints + offset]
        return self.lm.logp[index]

    def try_set(self, code, letter, commit=False):
        old = int(self.key[code])
        if old == letter:
            return 0.0
        endpoints = self.affected[code]
        before = float(self.endpoint_scores[endpoints].sum())
        positions = self.positions[code]
        self.key[code] = letter
        self.decoded[positions] = letter
        self.padded[positions + self.order - 1] = letter
        new_scores = self._scores(endpoints)
        delta = float(new_scores.sum() - before)
        if commit:
            self.endpoint_scores[endpoints] = new_scores
            self.total += delta
        else:
            self.key[code] = old
            self.decoded[positions] = old
            self.padded[positions + self.order - 1] = old
        return delta

    def try_swap(self, a, b, commit=False):
        la, lb = int(self.key[a]), int(self.key[b])
        if la == lb:
            return 0.0
        endpoints = np.union1d(self.affected[a], self.affected[b])
        before = float(self.endpoint_scores[endpoints].sum())
        pa, pb = self.positions[a], self.positions[b]
        self.key[a], self.key[b] = lb, la
        self.decoded[pa], self.decoded[pb] = lb, la
        self.padded[pa + self.order - 1], self.padded[pb + self.order - 1] = lb, la
        new_scores = self._scores(endpoints)
        delta = float(new_scores.sum() - before)
        if commit:
            self.endpoint_scores[endpoints] = new_scores
            self.total += delta
        else:
            self.key[a], self.key[b] = la, lb
            self.decoded[pa], self.decoded[pb] = la, lb
            self.padded[pa + self.order - 1], self.padded[pb + self.order - 1] = la, lb
        return delta


def initial_key(vocab, rng):
    key = np.empty(len(vocab) + 1, dtype=np.int64)
    groups = defaultdict(list)
    for i, code in enumerate(vocab):
        groups[code[0]].append(i)
    for codes in groups.values():
        slots = np.repeat(LATIN_IDS, CAPACITY)
        rng.shuffle(slots)
        if len(codes) > len(slots):
            raise RuntimeError("segmentation exceeds public key capacity")
        key[np.asarray(codes)] = slots[:len(codes)]
    key[-1] = SPACE_ID
    return key


def solve(obs, vocab, lm, iterations, restarts, seed):
    rng = np.random.default_rng(seed)
    groups = defaultdict(list)
    for i, code in enumerate(vocab):
        groups[code[0]].append(i)
    group_names = sorted(groups)
    best = None
    for _ in range(restarts):
        state = IncrementalKey(obs, len(vocab), lm, initial_key(vocab, rng))
        allocations = {
            name: {
                int(letter): sum(int(state.key[i]) == int(letter) for i in codes)
                for letter in LATIN_IDS
            }
            for name, codes in groups.items()
        }
        best_total, best_key = state.total, state.key.copy()
        for iteration in range(iterations):
            fraction = iteration / max(1, iterations - 1)
            temperature = 30.0 * (0.03 / 30.0) ** fraction
            name = group_names[int(rng.integers(len(group_names)))]
            codes = groups[name]
            if rng.random() < 0.72:
                a, b = rng.choice(codes, 2, replace=False)
                delta = state.try_swap(int(a), int(b))
                if delta >= 0 or rng.random() < math.exp(delta / temperature):
                    state.try_swap(int(a), int(b), commit=True)
            else:
                code = int(rng.choice(codes))
                old = int(state.key[code])
                available = [
                    int(letter) for letter in LATIN_IDS
                    if int(letter) != old and allocations[name][int(letter)] < CAPACITY
                ]
                if not available:
                    continue
                letter = int(rng.choice(available))
                delta = state.try_set(code, letter)
                if delta >= 0 or rng.random() < math.exp(delta / temperature):
                    state.try_set(code, letter, commit=True)
                    allocations[name][old] -= 1
                    allocations[name][letter] += 1
            if state.total > best_total:
                best_total, best_key = state.total, state.key.copy()
        state = IncrementalKey(obs, len(vocab), lm, best_key)
        allocations = {
            name: {
                int(letter): sum(int(state.key[i]) == int(letter) for i in codes)
                for letter in LATIN_IDS
            }
            for name, codes in groups.items()
        }
        for _ in range(8):
            changed = False
            for name in group_names:
                codes = groups[name]
                rng.shuffle(codes)
                for code in codes:
                    old = int(state.key[code])
                    options = [
                        (state.try_set(code, int(letter)), int(letter))
                        for letter in LATIN_IDS
                        if int(letter) == old or allocations[name][int(letter)] < CAPACITY
                    ]
                    delta, letter = max(options)
                    if delta > 1e-9 and letter != old:
                        state.try_set(code, letter, commit=True)
                        allocations[name][old] -= 1
                        allocations[name][letter] += 1
                        changed = True
                for code in codes:
                    options = [(state.try_swap(code, other), other) for other in codes]
                    delta, other = max(options)
                    if delta > 1e-9:
                        state.try_swap(code, other, commit=True)
                        changed = True
            if not changed:
                break
        if best is None or state.total > best[0]:
            best = state.total, state.key.copy()
    return best

