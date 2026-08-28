#!/usr/bin/env python3
"""Recover the Naibbe key blind, conditional on oracle U/P/S segmentation."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import io
import json
import math
import tempfile
import urllib.request
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "artifacts"
CACHE = Path(tempfile.gettempdir()) / "gdt602_naibbe_blind_key_recovery"

spec = importlib.util.spec_from_file_location(
    "gdt601_run", ROOT / "experiments/yolo/gdt601_naibbe_literal_key_attack/src/run.py"
)
G601 = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(G601)

ALPHABET = G601.ALPHABET
SPACE_ID = G601.SPACE
LATIN_LETTERS = "abcdefghilmnopqrstuvxyz"
LATIN_IDS = np.array([ALPHABET.index(char) for char in LATIN_LETTERS], dtype=np.int64)
PLAINTEXT_URL = (
    "https://raw.githubusercontent.com/greshko/naibbe-cipher/"
    f"{G601.GRESHKO_COMMIT}/respaced_plaintext/nathist_pre_encryption_respaced_plaintext.txt"
)
PLAINTEXT_SHA256 = "4979b6826c75dd47b90d6c95ac212a34cd3735b1151ca2a524e9d13b4112e93b"


def fetch_plaintext() -> Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / "nathist_pre_encryption_respaced_plaintext.txt"
    data = path.read_bytes() if path.is_file() else b""
    if hashlib.sha256(data).hexdigest() != PLAINTEXT_SHA256:
        with urllib.request.urlopen(PLAINTEXT_URL, timeout=60) as response:
            data = response.read()
        if hashlib.sha256(data).hexdigest() != PLAINTEXT_SHA256:
            raise RuntimeError("aligned plaintext source hash mismatch")
        path.write_bytes(data)
    return path


def load_oracle_units(paths):
    plaintext_lines = fetch_plaintext().read_text().splitlines()
    cipher_lines = paths["nathist_output_ciphertext.txt"].read_text().splitlines()
    reverse = G601.reverse_tables(paths["naibbe_tables.csv"])
    unit_lines = []
    target_lines = []
    truth = {}
    for plaintext_line, cipher_line in zip(plaintext_lines, cipher_lines):
        plain_tokens = plaintext_line.split()
        cipher_tokens = cipher_line.split()
        if len(plain_tokens) != len(cipher_tokens):
            raise RuntimeError("control alignment is not token-for-token")
        units = []
        target = []
        for plain, cipher in zip(plain_tokens, cipher_tokens):
            if len(plain) == 1:
                if plain not in reverse["unigram"].get(cipher, ()):
                    raise RuntimeError("oracle unigram alignment failed")
                pieces = [("U", cipher, plain)]
            elif len(plain) == 2:
                cuts = [
                    cut
                    for cut in range(1, len(cipher))
                    if plain[0] in reverse["prefix"].get(cipher[:cut], ())
                    and plain[1] in reverse["suffix"].get(cipher[cut:], ())
                ]
                if len(cuts) != 1:
                    raise RuntimeError(f"oracle bigram alignment failed: {plain} {cipher} {cuts}")
                cut = cuts[0]
                pieces = [("P", cipher[:cut], plain[0]), ("S", cipher[cut:], plain[1])]
            else:
                raise RuntimeError("control chunks must be unigrams or bigrams")
            for state, surface, letter in pieces:
                code = f"{state}|{surface}"
                if code in truth and truth[code] != letter:
                    raise RuntimeError("state-specific code is not deterministic")
                truth[code] = letter
                units.append(code)
                target.append(letter)
        if units:
            unit_lines.append(units)
            target_lines.append("".join(target))
    return unit_lines, target_lines, truth


def fit_latin(paths, order=4):
    text = G601.clean_reference(paths["caesar_la.txt"], "GALLIA est omnis")
    chunks = " ".join(text[index : index + 110] for index in range(0, len(text), 110))
    return G601.CharModel(order, 0.25).fit(chunks)


@dataclass(frozen=True)
class BlindProblem:
    vocab: tuple[str, ...]
    counts: dict[str, int]
    obs: np.ndarray
    model: object


def build_blind_problem(unit_lines, model):
    counts = Counter(code for line in unit_lines for code in line)
    vocab = tuple(code for code, _count in counts.most_common())
    code_id = {code: index for index, code in enumerate(vocab)}
    obs = []
    for line_index, line in enumerate(unit_lines):
        if line_index:
            obs.append(len(vocab))
        obs.extend(code_id[code] for code in line)
    return BlindProblem(vocab, dict(counts), np.array(obs, dtype=np.int64), model)


class IncrementalKey:
    def __init__(self, problem: BlindProblem, key: np.ndarray):
        self.problem = problem
        self.key = key.copy()
        self.order = problem.model.order
        self.decoded = self.key[problem.obs]
        self.padded = np.concatenate(
            [np.full(self.order - 1, SPACE_ID, dtype=np.int64), self.decoded]
        )
        n_codes = len(problem.vocab)
        self.positions = [np.flatnonzero(problem.obs == index) for index in range(n_codes)]
        self.affected = []
        n = len(problem.obs)
        for positions in self.positions:
            endpoints = (
                np.unique(
                    np.concatenate(
                        [
                            np.arange(position, min(n, position + self.order), dtype=np.int64)
                            for position in positions
                        ]
                    )
                )
                if len(positions)
                else np.empty(0, dtype=np.int64)
            )
            self.affected.append(endpoints)
        all_endpoints = np.arange(len(problem.obs), dtype=np.int64)
        self.endpoint_scores = self._scores(all_endpoints)
        self.total = float(self.endpoint_scores.sum())

    def _scores(self, endpoints):
        index = np.zeros(len(endpoints), dtype=np.int64)
        for offset in range(self.order):
            index = index * len(ALPHABET) + self.padded[endpoints + offset]
        return self.problem.model.logp[index]

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
        after_scores = self._scores(endpoints)
        delta = float(after_scores.sum() - before)
        if commit:
            self.endpoint_scores[endpoints] = after_scores
            self.total += delta
        else:
            self.key[code] = old
            self.decoded[positions] = old
            self.padded[positions + self.order - 1] = old
        return delta

    def try_swap(self, left, right, commit=False):
        old_left, old_right = int(self.key[left]), int(self.key[right])
        if old_left == old_right:
            return 0.0
        endpoints = np.union1d(self.affected[left], self.affected[right])
        before = float(self.endpoint_scores[endpoints].sum())
        left_positions, right_positions = self.positions[left], self.positions[right]
        self.key[left], self.key[right] = old_right, old_left
        self.decoded[left_positions], self.decoded[right_positions] = old_right, old_left
        self.padded[left_positions + self.order - 1] = old_right
        self.padded[right_positions + self.order - 1] = old_left
        after_scores = self._scores(endpoints)
        delta = float(after_scores.sum() - before)
        if commit:
            self.endpoint_scores[endpoints] = after_scores
            self.total += delta
        else:
            self.key[left], self.key[right] = old_left, old_right
            self.decoded[left_positions], self.decoded[right_positions] = old_left, old_right
            self.padded[left_positions + self.order - 1] = old_left
            self.padded[right_positions + self.order - 1] = old_right
        return delta


def unconstrained_initial(problem, rng):
    key = rng.choice(LATIN_IDS, size=len(problem.vocab))
    return np.concatenate([key, np.array([SPACE_ID], dtype=np.int64)])


def capacity_initial(problem, rng):
    key = np.empty(len(problem.vocab) + 1, dtype=np.int64)
    groups = defaultdict(list)
    for index, code in enumerate(problem.vocab):
        groups[code[0]].append(index)
    for codes in groups.values():
        slots = np.repeat(LATIN_IDS, 6)
        rng.shuffle(slots)
        key[np.asarray(codes)] = slots[: len(codes)]
    key[-1] = SPACE_ID
    return key


def polish(state, rng, capacity):
    groups = defaultdict(list)
    for index, code in enumerate(state.problem.vocab):
        groups[code[0]].append(index)
    allocations = {
        group: {
            int(letter): sum(int(state.key[index]) == int(letter) for index in codes)
            for letter in LATIN_IDS
        }
        for group, codes in groups.items()
    }
    for _sweep in range(8):
        changed = False
        for group, codes in groups.items():
            rng.shuffle(codes)
            for code in codes:
                old = int(state.key[code])
                candidates = [
                    int(letter)
                    for letter in LATIN_IDS
                    if not capacity or int(letter) == old or allocations[group][int(letter)] < 6
                ]
                delta, letter = max((state.try_set(code, letter), letter) for letter in candidates)
                if delta > 1e-9 and letter != old:
                    state.try_set(code, letter, commit=True)
                    allocations[group][old] -= 1
                    allocations[group][letter] += 1
                    changed = True
            if capacity:
                for left in codes:
                    delta, right = max((state.try_swap(left, right), right) for right in codes)
                    if delta > 1e-9:
                        state.try_swap(left, right, commit=True)
                        changed = True
        if not changed:
            break
    return state


def solve(problem, iterations, restarts, seed, capacity):
    """The solver receives no aligned plaintext and no surface-to-letter key."""
    rng = np.random.default_rng(seed)
    groups = defaultdict(list)
    for index, code in enumerate(problem.vocab):
        groups[code[0]].append(index)
    global_best = None
    for _restart in range(restarts):
        initial = capacity_initial(problem, rng) if capacity else unconstrained_initial(problem, rng)
        state = IncrementalKey(problem, initial)
        allocations = {
            group: {
                int(letter): sum(int(state.key[index]) == int(letter) for index in codes)
                for letter in LATIN_IDS
            }
            for group, codes in groups.items()
        }
        best = (state.total, state.key.copy())
        for iteration in range(iterations):
            fraction = iteration / max(1, iterations - 1)
            temperature = 30.0 * (0.03 / 30.0) ** fraction
            group = str(rng.choice(list(groups)))
            codes = groups[group]
            if rng.random() < (0.72 if capacity else 0.25):
                left, right = rng.choice(codes, 2, replace=False)
                delta = state.try_swap(int(left), int(right))
                if delta >= 0 or rng.random() < math.exp(delta / temperature):
                    state.try_swap(int(left), int(right), commit=True)
            else:
                code = int(rng.choice(codes))
                old = int(state.key[code])
                available = [
                    int(letter)
                    for letter in LATIN_IDS
                    if int(letter) != old
                    and (not capacity or allocations[group][int(letter)] < 6)
                ]
                if not available:
                    continue
                letter = int(rng.choice(available))
                delta = state.try_set(code, letter)
                if delta >= 0 or rng.random() < math.exp(delta / temperature):
                    state.try_set(code, letter, commit=True)
                    allocations[group][old] -= 1
                    allocations[group][letter] += 1
            if state.total > best[0]:
                best = (state.total, state.key.copy())
        state = polish(IncrementalKey(problem, best[1]), rng, capacity)
        if global_best is None or state.total > global_best[0]:
            global_best = (state.total, state.key.copy())
    return global_best


def metrics(problem, key, truth):
    correct_types = 0
    correct_events = 0
    rows = []
    for index, code in enumerate(problem.vocab):
        recovered = ALPHABET[int(key[index])]
        expected = truth[code]
        count = problem.counts[code]
        correct = recovered == expected
        correct_types += int(correct)
        correct_events += count * int(correct)
        state, surface = code.split("|", 1)
        rows.append(
            {
                "state": state,
                "surface": surface,
                "events": count,
                "truth": expected,
                "recovered": recovered,
                "correct": int(correct),
            }
        )
    event_total = sum(problem.counts.values())
    return {
        "type_accuracy": correct_types / len(problem.vocab),
        "weighted_character_accuracy": correct_events / event_total,
        "correct_types": correct_types,
        "types": len(problem.vocab),
        "correct_characters": correct_events,
        "characters": event_total,
        "rows": rows,
    }


def markov_typicality(decoded, paths, order):
    model = fit_latin(paths, order)
    padded = np.concatenate(
        [np.full(order - 1, SPACE_ID, dtype=np.int64), decoded]
    )
    endpoints = np.arange(len(decoded), dtype=np.int64)
    index = np.zeros(len(decoded), dtype=np.int64)
    for offset in range(order):
        index = index * len(ALPHABET) + padded[endpoints + offset]
    counts = np.bincount(index, minlength=len(ALPHABET) ** order).reshape(-1, len(ALPHABET))
    row_totals = counts.sum(axis=1)
    log_class = (
        sum(math.lgamma(int(total) + 1) for total in row_totals if total)
        - sum(math.lgamma(int(total) + 1) for total in counts.ravel() if total)
    ) / math.log(2)
    likelihood = float(np.dot(counts.ravel(), model.logp))
    return (likelihood + log_class) / len(decoded)


def tsv_bytes(fields, rows):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode()


def main() -> int:
    paths = G601.fetch_sources()
    unit_lines, target_lines, truth = load_oracle_units(paths)
    problem = build_blind_problem(unit_lines, fit_latin(paths, 4))
    truth_key = np.array(
        [ALPHABET.index(truth[code]) for code in problem.vocab] + [SPACE_ID], dtype=np.int64
    )
    truth_score = IncrementalKey(problem, truth_key).total / len(problem.obs)

    raw_score, raw_key = solve(problem, 100_000, 2, 11, capacity=False)
    raw_metrics = metrics(problem, raw_key, truth)
    raw_metrics.pop("rows")

    seed_results = []
    recovered_keys = []
    for seed in (1, 2, 3):
        score, key = solve(problem, 30_000, 1, seed, capacity=True)
        recovered_keys.append(key)
        measurement = metrics(problem, key, truth)
        measurement.pop("rows")
        seed_results.append(
            {"seed": seed, "score_bits_per_event": score / len(problem.obs), **measurement}
        )
    identical = all(np.array_equal(recovered_keys[0], key) for key in recovered_keys[1:])
    final_key = recovered_keys[0]
    final_metrics = metrics(problem, final_key, truth)
    key_rows = final_metrics.pop("rows")

    typicality = {}
    candidates = {
        "truth": truth_key[problem.obs],
        "unconstrained_ml": raw_key[problem.obs],
        "capacity_mdl": final_key[problem.obs],
    }
    for name, decoded in candidates.items():
        typicality[name] = {
            f"order_{order}_bits_per_event": markov_typicality(decoded, paths, order)
            for order in (2, 3, 4)
        }

    result = {
        "experiment_id": "GDT602",
        "status": "NAIBBE_KEY_RECOVERED_CONDITIONAL_ON_ORACLE_SEGMENTATION",
        "problem": {
            "nonempty_lines": len(unit_lines),
            "characters": sum(len(line) for line in target_lines),
            "lm_events_including_line_boundaries": len(problem.obs),
            "observed_state_specific_types": len(problem.vocab),
            "states": ["U", "P", "S"],
            "alphabet_letters": LATIN_LETTERS,
            "public_capacity": "at most six surface types per state and plaintext letter",
        },
        "data_separation": {
            "solver_receives": [
                "state-tagged oracle-segmented surface IDs",
                "line boundaries",
                "23-letter alphabet",
                "public six-table capacity",
                "independent Caesar char-4 model",
            ],
            "solver_does_not_receive": [
                "aligned plaintext",
                "published surface-to-letter table",
                "true key",
            ],
            "evaluation_only": ["aligned plaintext", "published table", "true key"],
        },
        "truth_key_score_bits_per_event": truth_score,
        "unconstrained_ml": {
            "score_bits_per_event": raw_score / len(problem.obs),
            **raw_metrics,
        },
        "capacity_mdl_seeds": seed_results,
        "capacity_mdl_identical_keys_across_seeds": identical,
        "capacity_mdl_final": final_metrics,
        "typicality": typicality,
        "sources": {
            **G601.SOURCES,
            "nathist_pre_encryption_respaced_plaintext.txt": {
                "url": PLAINTEXT_URL,
                "sha256": PLAINTEXT_SHA256,
            },
        },
        "claim_ceiling": "Demonstrates near-exact unknown-key recovery for the public six-table Naibbe model conditional on oracle U/P/S segmentation. It is not an end-to-end segmentation result and does not decode Voynich.",
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "gdt602_result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    )
    (OUT / "gdt602_recovered_key.tsv").write_bytes(
        tsv_bytes(["state", "surface", "events", "truth", "recovered", "correct"], key_rows)
    )
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
