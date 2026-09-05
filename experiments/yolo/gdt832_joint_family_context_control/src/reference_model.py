#!/usr/bin/env python3
"""Reference-only word/context model for the GDT832 control.

Inputs are JSONL arrays of normalized historical words and a JSON mapping
forms to lemma|UPOS strings. This module does not read control plaintext,
ciphertext, keys, candidate inventories, or Voynich data.
"""

from __future__ import annotations

import argparse
from array import array
from collections import Counter, defaultdict
import csv
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import random
import re
import sys
from typing import Iterable, Sequence


DISCOUNT = 0.5
WORD_WEIGHT = 0.97
CHAR_WEIGHT = 0.03
CHAR_ALPHA = 0.1
EOS = 26
BOS = 27
CONTEXT_BASE = 28
OUTPUT_COUNT = 27
CONTEXT_COUNT = CONTEXT_BASE ** 3
REWIRE_SEED = 83217
REWIRE_ATTEMPTS_PER_EDGE = 20
WORD_RE = re.compile(r"[a-z]+\Z")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _word(value: object, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str) or not (
        (allow_empty and value == "") or WORD_RE.fullmatch(value)
    ):
        raise ValueError("words must contain only lowercase a-z")
    return value


def _reference_counts(path: Path):
    words: Counter[str] = Counter()
    pairs: Counter[tuple[str, str]] = Counter()
    sentences = 0
    with path.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            sentence = json.loads(line)
            if not isinstance(sentence, list):
                raise ValueError(f"reference line {line_number} must be an array")
            sentence = [_word(token) for token in sentence]
            if not sentence:
                continue
            words.update(sentence)
            pairs.update(zip(sentence, sentence[1:]))
            sentences += 1
    if not words:
        raise ValueError("reference contains no words")
    return words, pairs, sentences


def _char_counts(words: Counter[str]):
    counts: dict[tuple[int, ...], Counter[int]] = defaultdict(Counter)
    for word, frequency in words.items():
        history = (BOS, BOS, BOS)
        for output in [*(ord(character) - ord("a") for character in word), EOS]:
            for order in range(4):
                context = history[-order:] if order else ()
                counts[context][output] += frequency
            history = (*history[1:], output)
    return counts


def _dense_char_logp(words: Counter[str]) -> array:
    counts = _char_counts(words)
    distributions = {}
    for context, outputs in counts.items():
        denominator = sum(outputs.values()) + OUTPUT_COUNT * CHAR_ALPHA
        distributions[context] = tuple(
            math.log((outputs.get(output, 0) + CHAR_ALPHA) / denominator)
            for output in range(OUTPUT_COUNT)
        )
    values = array("f")
    for first in range(CONTEXT_BASE):
        for second in range(CONTEXT_BASE):
            for third in range(CONTEXT_BASE):
                history = (first, second, third)
                for order in (3, 2, 1, 0):
                    context = history[-order:] if order else ()
                    if context in distributions:
                        values.extend(distributions[context])
                        break
    assert len(values) == CONTEXT_COUNT * OUTPUT_COUNT
    return values


def rewire_edges(
    edges: Iterable[tuple[int, int]],
    *,
    seed: int = REWIRE_SEED,
    attempts_per_edge: int = REWIRE_ATTEMPTS_PER_EDGE,
):
    """Swap endpoints while preserving every form and lemma degree exactly."""
    original = set(edges)
    ordered = sorted(original)
    current = set(original)
    generator = random.Random(seed)
    attempts = attempts_per_edge * len(ordered)
    successful = 0
    for _ in range(attempts):
        if len(ordered) < 2:
            continue
        first, second = generator.sample(range(len(ordered)), 2)
        word_a, lemma_a = ordered[first]
        word_b, lemma_b = ordered[second]
        if word_a == word_b or lemma_a == lemma_b:
            continue
        new_a, new_b = (word_a, lemma_b), (word_b, lemma_a)
        if new_a in current or new_b in current:
            continue
        current.remove(ordered[first])
        current.remove(ordered[second])
        current.add(new_a)
        current.add(new_b)
        ordered[first], ordered[second] = new_a, new_b
        successful += 1
    assert Counter(word for word, _ in original) == Counter(word for word, _ in current)
    assert Counter(lemma for _, lemma in original) == Counter(lemma for _, lemma in current)
    changed = len(original - current)
    return sorted(current), {
        "seed": seed,
        "attempts_per_edge": attempts_per_edge,
        "attempted_swaps": attempts,
        "successful_swaps": successful,
        "edge_count": len(original),
        "changed_edges": changed,
        "fraction_changed": changed / len(original) if original else 0.0,
        "fraction_definition": "original edges absent from rewired graph / original edge count",
        "rng": "random.Random(seed).sample(range(edge_count), 2)",
    }


def _write_tsv(path: Path, header: Sequence[str], rows: Iterable[Sequence[object]]):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)


def build(reference_jsonl: str | Path, families_json: str | Path, outdir: str | Path):
    """Build a deterministic model exclusively from the supplied references."""
    reference, families_path, destination = map(
        Path, (reference_jsonl, families_json, outdir)
    )
    if any("sealed" in path.parts for path in (reference, families_path, destination)):
        raise ValueError("reference model must not access a sealed directory")
    words, pairs, sentence_count = _reference_counts(reference)
    families = json.loads(families_path.read_text(encoding="utf-8"))
    if not isinstance(families, dict):
        raise ValueError("families must be a form-to-lemma-list JSON object")
    for form, lemmas in families.items():
        _word(form)
        if not isinstance(lemmas, list) or not all(
            isinstance(lemma, str) and lemma and "\n" not in lemma and "\t" not in lemma
            for lemma in lemmas
        ):
            raise ValueError("family values must be lists of nonempty lemma strings")
    vocabulary = sorted(words)
    identifiers = {word: index for index, word in enumerate(vocabulary)}
    lemma_names = sorted({lemma for word in vocabulary for lemma in families.get(word, [])})
    lemma_ids = {lemma: index for index, lemma in enumerate(lemma_names)}
    edges = {
        (identifiers[word], lemma_ids[lemma])
        for word in vocabulary for lemma in families.get(word, [])
    }
    rewired, rewire_meta = rewire_edges(edges)
    outgoing = Counter()
    distinct = Counter()
    for (previous, _), count in pairs.items():
        outgoing[previous] += count
        distinct[previous] += 1
    destination.mkdir(parents=True, exist_ok=True)
    _write_tsv(
        destination / "vocab.tsv",
        ("word_id", "word", "count", "outcount", "distinct"),
        ((identifiers[word], word, words[word], outgoing[word], distinct[word])
         for word in vocabulary),
    )
    _write_tsv(
        destination / "bigrams.tsv", ("prev_id", "next_id", "count"),
        ((identifiers[a], identifiers[b], count) for (a, b), count in sorted(pairs.items())),
    )
    values = _dense_char_logp(words)
    if values.itemsize != 4:
        raise RuntimeError("platform float array must use 32-bit values")
    if sys.byteorder != "little":
        values.byteswap()
    (destination / "char_logp.bin").write_bytes(values.tobytes())
    for filename, family_edges in (("family_real.tsv", sorted(edges)),
                                    ("family_rewired.tsv", rewired)):
        memberships = defaultdict(list)
        for word_id, lemma_id in family_edges:
            memberships[word_id].append(lemma_id)
        _write_tsv(
            destination / filename, ("word_id", "lemma_ids"),
            ((word_id, ",".join(map(str, sorted(memberships[word_id]))))
             for word_id in range(len(vocabulary))),
        )
    output_names = ("vocab.tsv", "bigrams.tsv", "char_logp.bin",
                    "family_real.tsv", "family_rewired.tsv")
    metadata = {
        "format_version": 1,
        "N": sum(words.values()),
        "sentence_count": sentence_count,
        "vocabulary_size": len(vocabulary),
        "bigram_type_count": len(pairs),
        "bigram_token_count": sum(pairs.values()),
        "D": DISCOUNT,
        "discount": DISCOUNT,
        "word_weight": WORD_WEIGHT,
        "char_weight": CHAR_WEIGHT,
        "char_alpha": CHAR_ALPHA,
        "character_order": 4,
        "character_history_length": 3,
        "character_alphabet": "abcdefghijklmnopqrstuvwxyz",
        "eos": EOS,
        "bos": BOS,
        "character_output_count": OUTPUT_COUNT,
        "character_context_base": CONTEXT_BASE,
        "character_context_count": CONTEXT_COUNT,
        "character_table_layout": "little-endian float32 [28**3,27]; ((a*28+b)*28+c)*27+out",
        "character_backoff": "longest observed suffix context, lengths 3,2,1,0",
        "character_word_termination": "EOS after every word; BOS,BOS,BOS initial history; empty string has character-model mass",
        "word_boundaries": "within-sentence bigrams only; no word EOS; unigram at BOS or unseen previous word",
        "lemma_names_by_id": lemma_names,
        "family_form_scope": "observed reference vocabulary only",
        "family_forms_outside_reference": sum(form not in identifiers for form in families),
        "family_rewiring": rewire_meta,
        "input_hashes": {"reference_jsonl_sha256": _sha256(reference),
                         "families_json_sha256": _sha256(families_path)},
        "output_sha256": {name: _sha256(destination / name) for name in output_names},
        "score_units": "natural logarithm",
    }
    (destination / "model_meta.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return metadata


class ReferenceModel:
    """Independent Python reader for the canonical exported model tables."""

    def __init__(self, outdir: str | Path):
        directory = Path(outdir)
        if "sealed" in directory.parts:
            raise ValueError("reference model must not access a sealed directory")
        self.metadata = json.loads((directory / "model_meta.json").read_text(encoding="utf-8"))
        if self.metadata.get("format_version") != 1:
            raise ValueError("unsupported reference-model format")
        for name, expected_hash in self.metadata["output_sha256"].items():
            if Path(name).name != name or _sha256(directory / name) != expected_hash:
                raise ValueError(f"invalid model artifact hash: {name}")
        with (directory / "vocab.tsv").open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream, delimiter="\t"))
        self.words = [row["word"] for row in rows]
        if [int(row["word_id"]) for row in rows] != list(range(len(rows))):
            raise ValueError("word IDs must be contiguous")
        self.ids = {word: index for index, word in enumerate(self.words)}
        self.counts = {row["word"]: int(row["count"]) for row in rows}
        self.outcounts = {row["word"]: int(row["outcount"]) for row in rows}
        self.distinct = {row["word"]: int(row["distinct"]) for row in rows}
        with (directory / "bigrams.tsv").open(encoding="utf-8", newline="") as stream:
            self.bigrams = {
                (self.words[int(row["prev_id"])], self.words[int(row["next_id"])]): int(row["count"])
                for row in csv.DictReader(stream, delimiter="\t")
            }
        self.char_logp = array("f")
        self.char_logp.frombytes((directory / "char_logp.bin").read_bytes())
        if sys.byteorder != "little":
            self.char_logp.byteswap()
        if len(self.char_logp) != CONTEXT_COUNT * OUTPUT_COUNT:
            raise ValueError("invalid character-table size")

    @lru_cache(maxsize=131072)
    def log_character(self, word: str) -> float:
        word = _word(word, allow_empty=True)
        first = second = third = BOS
        score = 0.0
        for output in [*(ord(character) - ord("a") for character in word), EOS]:
            context = (first * CONTEXT_BASE + second) * CONTEXT_BASE + third
            score += self.char_logp[context * OUTPUT_COUNT + output]
            first, second, third = second, third, output
        return score

    @lru_cache(maxsize=131072)
    def log_unigram(self, word: str) -> float:
        character_score = math.log(self.metadata["char_weight"]) + self.log_character(word)
        count = self.counts.get(word, 0)
        if not count:
            return character_score
        empirical_score = math.log(self.metadata["word_weight"] * count / self.metadata["N"])
        larger, smaller = max(empirical_score, character_score), min(empirical_score, character_score)
        return larger + math.log1p(math.exp(smaller - larger))

    def log_conditional(self, previous: str | None, word: str) -> float:
        base_score = self.log_unigram(word)
        total = self.outcounts.get(previous, 0)
        if previous is None or not total:
            return base_score
        discount = self.metadata["discount"]
        backoff_score = math.log(discount * self.distinct[previous] / total) + base_score
        observed_count = self.bigrams.get((previous, word), 0)
        if not observed_count:
            return backoff_score
        observed_score = math.log((observed_count - discount) / total)
        larger, smaller = max(observed_score, backoff_score), min(observed_score, backoff_score)
        return larger + math.log1p(math.exp(smaller - larger))

    def paragraph_score(self, words: Sequence[str], cutmask: Sequence[bool] | None = None) -> float:
        """Score one word sequence; optional cuts reset context before a word."""
        if cutmask is not None and len(cutmask) != len(words):
            raise ValueError("cutmask must have one entry per word")
        previous = None
        score = 0.0
        for index, word in enumerate(words):
            if cutmask is not None and cutmask[index]:
                previous = None
            score += self.log_conditional(previous, word)
            previous = word
        return score


def load(outdir: str | Path) -> ReferenceModel:
    return ReferenceModel(outdir)


load_model = load


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", required=True)
    parser.add_argument("--families", required=True)
    parser.add_argument("--out", required=True)
    arguments = parser.parse_args()
    result = build(arguments.reference, arguments.families, arguments.out)
    print(json.dumps({"status": "REFERENCE_MODEL_BUILT", "N": result["N"],
                      "vocabulary_size": result["vocabulary_size"],
                      "family_rewiring": result["family_rewiring"]}, sort_keys=True))


if __name__ == "__main__":
    main()
