#!/usr/bin/env python3
"""Historically scaled mixed-codebook attack on frozen GDT605 units."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import random
import statistics
import unicodedata
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent.parent / "artifacts"
ACTIVE = "abcdefghilmnopqrstuvxyz"
ALPHABET = "abcdefghijklmnopqrstuvwxyz "
SPACE = ALPHABET.index(" ")
CONFIGS = {
    "primary_42L_4D_34S_7N_11W": {"L": 42, "D": 4, "S": 34, "N": 7, "W": 11},
    "sensitivity_36L_4D_40S_7N_11W": {"L": 36, "D": 4, "S": 40, "N": 7, "W": 11},
    "sensitivity_46L_4D_30S_7N_11W": {"L": 46, "D": 4, "S": 30, "N": 7, "W": 11},
}
PRIMARY = "primary_42L_4D_34S_7N_11W"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize_word(word: str) -> str:
    value = word.lower().replace("æ", "ae").replace("œ", "oe").replace("ß", "ss")
    value = "".join(
        char for char in unicodedata.normalize("NFKD", value)
        if not unicodedata.combining(char)
    )
    value = value.replace("j", "i").replace("k", "c").replace("w", "uu")
    return "".join(char for char in value if char in ACTIVE)


def words_from_text(text: str) -> list[str]:
    buffer = []
    words = []
    for char in text:
        if char.isalpha() or char in "æœß":
            buffer.append(char)
        elif buffer:
            word = normalize_word("".join(buffer))
            if word:
                words.append(word)
            buffer = []
    if buffer:
        word = normalize_word("".join(buffer))
        if word:
            words.append(word)
    return words


def load_reference_words(reference_dir: Path):
    expected = {
        "caesar_la.txt": "84ac8411841a4d8f5f4a49b6a2cd1f466917c6a5af72916d5e0b2b1ecb2f659c",
        "divina_commedia.txt": "aafa15bbc0644dac7680ce3d0e4494b99775fbc83394cb7ad88145a0f8d6b31e",
        "mhg/Erec-conll.txt": "367cc2e9d0b60aadee501c187864dea97c77af41303f216986cfa35575f43675",
        "mhg/Iwein-conll.txt": "5b43f962da24d5b438ff93f64f30036087fe37d1cd5863c0bd29e764957b6a6f",
        "mhg/Parzival-conll.txt": "9d7ef5fd1842f6197121b654eb3c57a307ff01a9698768e27be069732afdf5cf",
        "mhg/Rolandslied-conll.txt": "46b078128c6932759d56a6a4bf13f9c3bf84d88f7a8d0e35fca31670cc0191fa",
        "mhg/Willehalm-conll.txt": "abee7d5d1aee54fa944e0d311d4645455503d4fc0bbd9ef919c46a9cfd10e7fe",
    }
    for relative, digest in expected.items():
        if sha(reference_dir / relative) != digest:
            raise RuntimeError(f"reference binding failed: {relative}")
    caesar = (reference_dir / "caesar_la.txt").read_text()
    caesar = caesar[caesar.find("GALLIA est omnis"):]
    footer = "*** END OF THE PROJECT GUTENBERG"
    if footer in caesar:
        caesar = caesar[:caesar.find(footer)]
    italian = (reference_dir / "divina_commedia.txt").read_text()
    mhg = []
    for relative in expected:
        if not relative.startswith("mhg/"):
            continue
        for line in (reference_dir / relative).read_text().splitlines():
            if line.strip():
                token = normalize_word(line.split("\t", 1)[0])
                if token:
                    mhg.append(token)
    return {
        "latin": words_from_text(caesar),
        "old_italian": words_from_text(italian),
        "middle_high_german": mhg,
    }, expected


class CharModel:
    def __init__(self, order=4, alpha=0.25):
        self.order = order
        self.alpha = alpha
        self.logp = None

    def fit(self, text: str):
        size = len(ALPHABET)
        ids = np.fromiter((ALPHABET.index(char) for char in text if char in ALPHABET), dtype=np.int64)
        unigram = np.bincount(ids, minlength=size).astype(float)
        conditional = (unigram + 1.0) / (unigram.sum() + size)
        for context_order in range(1, self.order):
            context_size = size ** context_order
            packed = np.zeros(len(ids) - context_order, dtype=np.int64)
            for offset in range(context_order):
                packed = packed * size + ids[offset:len(ids) - context_order + offset]
            packed = packed * size + ids[context_order:]
            counts = np.bincount(
                packed, minlength=context_size * size
            ).astype(float).reshape(context_size, size)
            totals = counts.sum(axis=1, keepdims=True)
            lower = conditional.reshape(-1, size)
            backoff = np.tile(lower, (context_size // lower.shape[0], 1))
            strength = self.alpha * size
            conditional = (counts + strength * backoff) / (totals + strength)
        self.logp = np.log2(conditional.reshape(-1))
        return self

    def score(self, words: list[str]):
        text = " ".join(words)
        letters = sum(map(len, words))
        if not letters:
            return -25.0, 0
        context = 0
        for _ in range(self.order - 1):
            context = context * len(ALPHABET) + SPACE
        modulus = len(ALPHABET) ** (self.order - 1)
        total = 0.0
        for char in text + " ":
            index = ALPHABET.index(char)
            total += float(self.logp[context * len(ALPHABET) + index])
            context = (context * len(ALPHABET) + index) % modulus
        return total, letters


def destroy_words(words: list[str], language: str) -> list[str]:
    output = []
    for index, word in enumerate(words):
        rng = random.Random(int(hashlib.sha256(
            f"gdt605-mixed-reference-null|{language}|{index}".encode()
        ).hexdigest()[:16], 16))
        chars = list(word)
        rng.shuffle(chars)
        output.append("".join(chars))
    return output


def make_language_pack(words: list[str], language: str):
    # A fixed prefix trains the models.  Full counts only rank candidates;
    # no target string or key chooses reference vocabulary.
    train_words = []
    chars = 0
    for word in words:
        if chars >= 240_000:
            break
        train_words.append(word)
        chars += len(word) + 1
    destroyed_words = destroy_words(train_words, language)
    real_text = " ".join(train_words)
    destroyed_text = " ".join(destroyed_words)
    real_model = CharModel().fit(real_text)
    destroyed_model = CharModel().fit(destroyed_text)
    real_counts = Counter(train_words)
    destroyed_counts = Counter(destroyed_words)

    def candidates(counter):
        word_pool = [
            word for word, count in counter.most_common()
            if 2 <= len(word) <= 9 and count >= 2
        ][:256]
        substrings = {2: Counter(), 3: Counter()}
        for word, count in counter.items():
            for size in (2, 3):
                for index in range(len(word) - size + 1):
                    substrings[size][word[index:index + size]] += count
        syllables = []
        for size in (2, 3):
            syllables.extend(
                value for value, _ in sorted(
                    substrings[size].items(), key=lambda item: (-item[1], item[0])
                )[:128]
            )
        # Interleave lengths so the category cannot collapse to only bigrams.
        syllable_pool = []
        for index in range(128):
            for offset in (index, 128 + index):
                if offset < len(syllables) and syllables[offset] not in syllable_pool:
                    syllable_pool.append(syllables[offset])
        return word_pool, syllable_pool[:256]

    real_word_pool, real_syllables = candidates(real_counts)
    null_word_pool, null_syllables = candidates(destroyed_counts)
    if min(len(real_word_pool), len(null_word_pool)) < 64:
        raise RuntimeError(f"reference word pool too small: {language}")
    return {
        "real_model": real_model,
        "destroyed_model": destroyed_model,
        "real_lexicon": set(real_counts),
        "destroyed_lexicon": set(destroyed_counts),
        "real_candidates": {
            "L": list(ACTIVE), "D": [char * 2 for char in ACTIVE],
            "S": real_syllables, "N": [""], "W": real_word_pool,
        },
        "destroyed_candidates": {
            "L": list(ACTIVE), "D": [char * 2 for char in ACTIVE],
            "S": null_syllables, "N": [""], "W": null_word_pool,
        },
        "reference_meta": {
            "train_words": len(train_words),
            "train_chars": sum(map(len, train_words)),
            "real_text_sha256": hashlib.sha256(real_text.encode()).hexdigest(),
            "destroyed_text_sha256": hashlib.sha256(destroyed_text.encode()).hexdigest(),
            "real_word_candidates": len(real_word_pool),
            "real_syllable_candidates": len(real_syllables),
        },
    }


def decode_sequence(sequence, categories, outputs):
    words = []
    buffer = []
    for unit in sequence:
        category = categories[unit]
        output = outputs[unit]
        if category == "W":
            if buffer:
                words.append("".join(buffer))
                buffer = []
            words.append(output)
        elif category != "N":
            buffer.append(output)
    if buffer:
        words.append("".join(buffer))
    return words


def chunk_objective(words, model, lexicon):
    bits, letters = model.score(words)
    if not letters:
        return -25.0
    known = sum(len(word) for word in words if len(word) >= 2 and word in lexicon)
    overlong = sum(max(0, len(word) - 12) ** 2 for word in words)
    # Per-letter scoring removes the trivial preference for assigning long
    # outputs only to rare units.  Lexical weight is deliberately modest.
    return bits / letters + 0.35 * known / letters - 0.015 * overlong / letters


def mapping_prior(unit, category, output, features, candidate_rank):
    record = features[unit]
    value = 0.0
    if category == "W":
        value += 1.5 * record["standalone_fraction"]
    elif category == "N":
        value += 0.4 * (1.0 - record["frequency_quantile"])
    if category in {"S", "W"}:
        value -= 0.01 * math.log2(2 + candidate_rank[category].get(output, 999))
    return value


def initialize_mapping(rng, units, config, candidates, features):
    remaining = set(units)
    categories = {}
    # Structural weighting only initializes; category swaps remain free.
    word_units = sorted(
        sorted(remaining),
        key=lambda unit: (
            features[unit]["standalone_fraction"] + rng.random() * 0.8,
            rng.random(),
        ), reverse=True,
    )[:config["W"]]
    for unit in word_units:
        categories[unit] = "W"
        remaining.remove(unit)
    null_units = sorted(
        sorted(remaining),
        key=lambda unit: (
            -features[unit]["frequency_quantile"] + rng.random() * 0.8,
            rng.random(),
        ), reverse=True,
    )[:config["N"]]
    for unit in null_units:
        categories[unit] = "N"
        remaining.remove(unit)
    # Sorting before the seeded shuffle prevents process-specific hash order
    # from silently changing a nominally identical key-recovery run.
    shuffled = sorted(remaining)
    rng.shuffle(shuffled)
    cursor = 0
    for category in ("D", "S", "L"):
        for unit in shuffled[cursor:cursor + config[category]]:
            categories[unit] = category
        cursor += config[category]
    outputs = {}
    for category in ("D", "S", "W"):
        assigned = [unit for unit in units if categories[unit] == category]
        selected = rng.sample(candidates[category], len(assigned))
        for unit, output in zip(assigned, selected):
            outputs[unit] = output
    letter_counts = Counter()
    for unit in units:
        if categories[unit] == "L":
            available = [char for char in candidates["L"] if letter_counts[char] < 6]
            output = rng.choice(available)
            outputs[unit] = output
            letter_counts[output] += 1
        elif categories[unit] == "N":
            outputs[unit] = ""
    return categories, outputs


GLOBAL = {}


def anneal(job):
    language = job["language"]
    model_kind = job["model_kind"]
    config_name = job["config"]
    seed = job["seed"]
    iterations = job["iterations"]
    rng = random.Random(seed)
    units = GLOBAL["units"]
    chunks = GLOBAL["train_chunk_types"]
    weights = GLOBAL["train_chunk_weights"]
    affected = GLOBAL["train_affected"]
    features = GLOBAL["features"]
    pack = GLOBAL["packs"][language]
    candidates = pack[f"{model_kind}_candidates"]
    model = pack[f"{model_kind}_model"]
    lexicon = pack[f"{model_kind}_lexicon"]
    config = CONFIGS[config_name]
    candidate_rank = {
        category: {value: index for index, value in enumerate(values)}
        for category, values in candidates.items()
    }
    categories, outputs = initialize_mapping(
        rng, units, config, candidates, features
    )

    def score_chunk(index):
        words = decode_sequence(chunks[index], categories, outputs)
        return chunk_objective(words, model, lexicon)

    chunk_scores = [score_chunk(index) for index in range(len(chunks))]
    prior = sum(
        mapping_prior(unit, categories[unit], outputs[unit], features, candidate_rank)
        for unit in units
    )
    total = sum(weight * value for weight, value in zip(weights, chunk_scores)) + prior
    best = (total, categories.copy(), outputs.copy())
    accepted = 0
    for iteration in range(iterations):
        left = rng.choice(units)
        move = rng.random()
        changed = [left]
        old = [(left, categories[left], outputs[left])]
        if move < 0.72:
            right = rng.choice(units)
            if right == left:
                continue
            changed.append(right)
            old.append((right, categories[right], outputs[right]))
            categories[left], categories[right] = categories[right], categories[left]
            outputs[left], outputs[right] = outputs[right], outputs[left]
        else:
            category = categories[left]
            if category == "N":
                continue
            used = Counter(
                outputs[unit] for unit in units if categories[unit] == category
            )
            possible = []
            for value in candidates[category]:
                if value == outputs[left]:
                    continue
                if category == "L":
                    if used[value] < 6:
                        possible.append(value)
                elif used[value] == 0:
                    possible.append(value)
            if not possible:
                continue
            outputs[left] = rng.choice(possible)
        changed_chunks = set()
        for unit in changed:
            changed_chunks.update(affected[unit])
        before = sum(weights[index] * chunk_scores[index] for index in changed_chunks)
        old_prior = sum(
            mapping_prior(unit, category, output, features, candidate_rank)
            for unit, category, output in old
        )
        new_scores = {index: score_chunk(index) for index in changed_chunks}
        after = sum(weights[index] * value for index, value in new_scores.items())
        new_prior = sum(
            mapping_prior(unit, categories[unit], outputs[unit], features, candidate_rank)
            for unit in changed
        )
        delta = after - before + new_prior - old_prior
        fraction = iteration / max(1, iterations - 1)
        temperature = 20.0 * (0.02 / 20.0) ** fraction
        if delta >= 0 or rng.random() < math.exp(delta / temperature):
            total += delta
            for index, value in new_scores.items():
                chunk_scores[index] = value
            accepted += 1
            if total > best[0]:
                best = (total, categories.copy(), outputs.copy())
        else:
            for unit, category, output in old:
                categories[unit] = category
                outputs[unit] = output
    total, categories, outputs = best
    return {
        **job,
        "train_objective": total / sum(weights),
        "accepted_moves": accepted,
        "mapping": {
            unit: {"category": categories[unit], "output": outputs[unit]}
            for unit in units
        },
    }


def evaluate_mapping(mapping, records, real_model, destroyed_model, real_lexicon):
    categories = {unit: value["category"] for unit, value in mapping.items()}
    outputs = {unit: value["output"] for unit, value in mapping.items()}
    real_bits = destroyed_bits = letters = known = words_total = empty = 0
    decoded = []
    for record in records:
        words = decode_sequence(record["units"], categories, outputs)
        rb, count = real_model.score(words)
        db, _ = destroyed_model.score(words)
        real_bits += rb
        destroyed_bits += db
        letters += count
        known += sum(len(word) for word in words if len(word) >= 2 and word in real_lexicon)
        words_total += len(words)
        empty += not words
        decoded.append(words)
    return {
        "decoded_characters": letters,
        "decoded_words": words_total,
        "empty_chunks": empty,
        "real_bits_per_character": real_bits / letters,
        "destroyed_bits_per_character": destroyed_bits / letters,
        "real_minus_destroyed_bits_per_character": (real_bits - destroyed_bits) / letters,
        "real_lexicon_character_fraction": known / letters,
    }, decoded


def pair_agreement(runs, held_frequency):
    output = []
    for left in range(len(runs)):
        for right in range(left + 1, len(runs)):
            a, b = runs[left]["mapping"], runs[right]["mapping"]
            category_same = {unit for unit in a if a[unit]["category"] == b[unit]["category"]}
            output_same = {
                unit for unit in a
                if a[unit]["category"] == b[unit]["category"]
                and a[unit]["output"] == b[unit]["output"]
            }
            weight = sum(held_frequency.values())
            output.append({
                "left_seed": runs[left]["seed"],
                "right_seed": runs[right]["seed"],
                "category_type_agreement": len(category_same) / len(a),
                "exact_output_type_agreement": len(output_same) / len(a),
                "category_held_weighted_agreement": sum(
                    held_frequency[unit] for unit in category_same
                ) / weight,
                "exact_output_held_weighted_agreement": sum(
                    held_frequency[unit] for unit in output_same
                ) / weight,
            })
    return output


def stable_units(runs, held_frequency):
    rows = []
    for unit in runs[0]["mapping"]:
        categories = [run["mapping"][unit]["category"] for run in runs]
        outputs = [run["mapping"][unit]["output"] for run in runs]
        category, category_count = Counter(categories).most_common(1)[0]
        pair, pair_count = Counter(zip(categories, outputs)).most_common(1)[0]
        rows.append({
            "unit": unit,
            "held_occurrences": held_frequency[unit],
            "modal_category": category,
            "category_consensus_fraction": category_count / len(runs),
            "modal_output": pair[1],
            "exact_mapping_consensus_fraction": pair_count / len(runs),
            "all_categories": ",".join(categories),
            "all_outputs": ",".join(outputs),
        })
    return sorted(rows, key=lambda row: (
        -row["exact_mapping_consensus_fraction"],
        -row["category_consensus_fraction"],
        -row["held_occurrences"], row["unit"],
    ))


def stable_held_words(records, decoded_by_run, lexicon, threshold):
    candidates = []
    for index, record in enumerate(records):
        support = Counter(
            word
            for decoded in decoded_by_run
            for word in set(decoded[index])
            if len(word) >= 3 and word in lexicon
        )
        for word, count in support.items():
            if count >= threshold:
                candidates.append({
                    "page": record["page"],
                    "physical_folio": record["physical_folio"],
                    "locus": record["locus"],
                    "chunk_index": record["chunk_index"],
                    "word": word,
                    "run_support": count,
                    "run_fraction": count / len(decoded_by_run),
                    "units": " ".join(record["units"]),
                })
    return sorted(candidates, key=lambda row: (
        -row["run_support"], row["physical_folio"], row["locus"],
        row["chunk_index"], row["word"],
    ))


def stable_held_fragments(records, decoded_by_run, threshold):
    candidates = []
    for index, record in enumerate(records):
        texts = ["".join(decoded[index]) for decoded in decoded_by_run]
        support = Counter()
        for text in texts:
            seen = set()
            for size in range(4, min(12, len(text)) + 1):
                seen.update(text[start:start + size] for start in range(len(text) - size + 1))
            support.update(seen)
        viable = [(len(fragment), count, fragment) for fragment, count in support.items() if count >= threshold]
        if not viable:
            continue
        best_length = max(length for length, _count, _fragment in viable)
        for length, count, fragment in sorted(viable, key=lambda item: (-item[0], -item[1], item[2])):
            if length != best_length:
                continue
            candidates.append({
                "page": record["page"],
                "physical_folio": record["physical_folio"],
                "locus": record["locus"],
                "chunk_index": record["chunk_index"],
                "fragment": fragment,
                "length": length,
                "run_support": count,
                "run_fraction": count / len(decoded_by_run),
                "units": " ".join(record["units"]),
            })
    return sorted(candidates, key=lambda row: (
        -row["length"], -row["run_support"], row["physical_folio"],
        row["locus"], row["chunk_index"], row["fragment"],
    ))


def write_tsv(path, rows):
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference-dir", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=min(9, os.cpu_count() or 1))
    parser.add_argument("--primary-iterations", type=int, default=30_000)
    parser.add_argument("--sensitivity-iterations", type=int, default=15_000)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    data_path = HERE / "unit_sequences.json"
    if sha(data_path) != "3ee0841e211314b72719acbbf79ed3a6dc7bfc3c157734f54dbdac92ac458fdf":
        raise RuntimeError("unit sequence freeze changed")
    data = json.loads(data_path.read_text())
    units = data["inventory"]
    train_records = data["sequences"]["train"]
    held_records = data["sequences"]["held"]
    train_counter = Counter(tuple(record["units"]) for record in train_records)
    train_chunk_types = list(train_counter)
    train_chunk_weights = [math.sqrt(train_counter[chunk]) for chunk in train_chunk_types]
    train_affected = {unit: set() for unit in units}
    for index, chunk in enumerate(train_chunk_types):
        for unit in set(chunk):
            train_affected[unit].add(index)
    unit_occ = Counter(unit for record in train_records for unit in record["units"])
    unit_standalone = Counter(
        record["units"][0] for record in train_records if len(record["units"]) == 1
    )
    ranked = {unit: index / (len(units) - 1) for index, unit in enumerate(
        sorted(units, key=lambda unit: (-unit_occ[unit], unit))
    )}
    features = {
        unit: {
            "standalone_fraction": unit_standalone[unit] / unit_occ[unit],
            "frequency_quantile": 1.0 - ranked[unit],
        }
        for unit in units
    }
    reference_words, reference_hashes = load_reference_words(args.reference_dir)
    packs = {
        language: make_language_pack(words, language)
        for language, words in reference_words.items()
    }
    GLOBAL.update({
        "units": units, "train_chunk_types": train_chunk_types,
        "train_chunk_weights": train_chunk_weights,
        "train_affected": train_affected, "features": features,
        "packs": packs,
    })
    primary_seeds = (11, 29, 47) if args.quick else (11, 29, 47, 71, 89, 107)
    null_seeds = (211, 229) if args.quick else (211, 229, 247, 271)
    sensitivity_seeds = (311,) if args.quick else (311, 329, 347)
    jobs = []
    for language in sorted(packs):
        for seed in primary_seeds:
            jobs.append({
                "language": language, "model_kind": "real", "config": PRIMARY,
                "seed": seed, "iterations": args.primary_iterations,
            })
        for seed in null_seeds:
            jobs.append({
                "language": language, "model_kind": "destroyed", "config": PRIMARY,
                "seed": seed, "iterations": args.primary_iterations,
            })
        for config in sorted(set(CONFIGS) - {PRIMARY}):
            for seed in sensitivity_seeds:
                jobs.append({
                    "language": language, "model_kind": "real", "config": config,
                    "seed": seed, "iterations": args.sensitivity_iterations,
                })
    results = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(anneal, job) for job in jobs]
        for future in as_completed(futures):
            record = future.result()
            results.append(record)
            print(record["language"], record["model_kind"], record["config"],
                  record["seed"], f"obj={record['train_objective']:.5f}", flush=True)
    results.sort(key=lambda row: (
        row["language"], row["config"], row["model_kind"], row["seed"]
    ))
    held_frequency = Counter(unit for record in held_records for unit in record["units"])
    summaries = {}
    mapping_rows = []
    stable_word_rows = []
    stable_fragment_rows = []
    for language in sorted(packs):
        pack = packs[language]
        lang_runs = [run for run in results if run["language"] == language]
        for run in lang_runs:
            metrics, decoded = evaluate_mapping(
                run["mapping"], held_records, pack["real_model"],
                pack["destroyed_model"], pack["real_lexicon"],
            )
            run["held_metrics"] = metrics
            if run["config"] == PRIMARY and run["model_kind"] == "real":
                run["held_decoded"] = decoded
        primary_real = [
            run for run in lang_runs if run["config"] == PRIMARY and run["model_kind"] == "real"
        ]
        primary_null = [
            run for run in lang_runs if run["config"] == PRIMARY and run["model_kind"] == "destroyed"
        ]
        agreements = pair_agreement(primary_real, held_frequency)
        unit_rows = stable_units(primary_real, held_frequency)
        for row in unit_rows:
            mapping_rows.append({"language": language, **row})
        threshold = math.ceil(0.75 * len(primary_real))
        words = stable_held_words(
            held_records,
            [run["held_decoded"] for run in primary_real],
            pack["real_lexicon"], threshold,
        )
        for row in words:
            stable_word_rows.append({"language": language, **row})
        fragments = stable_held_fragments(
            held_records,
            [run["held_decoded"] for run in primary_real],
            threshold,
        )
        for row in fragments:
            stable_fragment_rows.append({"language": language, **row})
        summaries[language] = {
            "primary_real_runs": [
                {key: value for key, value in run.items() if key not in {"mapping", "held_decoded"}}
                for run in primary_real
            ],
            "primary_destroyed_runs": [
                {key: value for key, value in run.items() if key != "mapping"}
                for run in primary_null
            ],
            "sensitivity_runs": [
                {key: value for key, value in run.items() if key != "mapping"}
                for run in lang_runs if run["config"] != PRIMARY
            ],
            "primary_pair_agreement": agreements,
            "stable_category_units_all_starts": sum(
                row["category_consensus_fraction"] == 1.0 for row in unit_rows
            ),
            "stable_exact_mapping_units_all_starts": sum(
                row["exact_mapping_consensus_fraction"] == 1.0 for row in unit_rows
            ),
            "stable_held_reference_words_at_75pct": len(words),
            "stable_held_reference_word_folios": len({row["physical_folio"] for row in words}),
            "stable_held_fragments_at_75pct": len(fragments),
            "stable_held_fragment_folios": len({row["physical_folio"] for row in fragments}),
        }
        # Complete primary held decodes, one row per physical chunk.
        decode_rows = []
        for index, record in enumerate(held_records):
            item = {
                "page": record["page"], "physical_folio": record["physical_folio"],
                "locus": record["locus"], "chunk_index": record["chunk_index"],
                "section": record["section"], "units": " ".join(record["units"]),
            }
            for run in primary_real:
                decoded_text = " ".join(run["held_decoded"][index])
                item[f"decoded_seed_{run['seed']}"] = decoded_text or "<EMPTY>"
            decode_rows.append(item)
        write_tsv(HERE / f"held_decodes_{language}.tsv", decode_rows)

    # Full mapping for every job, with one row per unit.
    full_mapping_rows = []
    for run in results:
        for unit in units:
            full_mapping_rows.append({
                "language": run["language"], "model_kind": run["model_kind"],
                "config": run["config"], "seed": run["seed"], "unit": unit,
                "category": run["mapping"][unit]["category"],
                "output": run["mapping"][unit]["output"],
                "train_occurrences": data["frequency"]["train"][unit],
                "held_occurrences": data["frequency"]["held"].get(unit, 0),
            })
    write_tsv(HERE / "complete_mappings.tsv", full_mapping_rows)
    write_tsv(HERE / "primary_unit_stability.tsv", mapping_rows)
    write_tsv(HERE / "stable_held_words.tsv", stable_word_rows)
    write_tsv(HERE / "stable_held_fragments.tsv", stable_fragment_rows)

    # Hard candidate gate: every start must be reference-typical, keys stable,
    # and the real attack must dominate the destroyed-reference attack.
    decisions = {}
    for language, summary in summaries.items():
        real_lr = [run["held_metrics"]["real_minus_destroyed_bits_per_character"] for run in summary["primary_real_runs"]]
        null_lr = [run["held_metrics"]["real_minus_destroyed_bits_per_character"] for run in summary["primary_destroyed_runs"]]
        agreements = summary["primary_pair_agreement"]
        gates = {
            "all_real_held_lr_ge_0_10": min(real_lr) >= 0.10,
            "real_median_lr_exceeds_null_by_0_10": statistics.median(real_lr) - statistics.median(null_lr) >= 0.10,
            "min_category_weighted_agreement_ge_0_70": min(pair["category_held_weighted_agreement"] for pair in agreements) >= 0.70,
            "min_exact_weighted_agreement_ge_0_50": min(pair["exact_output_held_weighted_agreement"] for pair in agreements) >= 0.50,
            "stable_words_on_three_held_folios": summary["stable_held_reference_word_folios"] >= 3,
        }
        decisions[language] = {"gates": gates, "all_gates_pass": all(gates.values())}
    passers = [language for language, value in decisions.items() if value["all_gates_pass"]]
    decision = "MIXED_CODEBOOK_READING_CANDIDATE" if len(passers) == 1 else "MIXED_CODEBOOK_UNSTABLE_PSEUDOTEXT"
    for run in results:
        run.pop("mapping", None)
        run.pop("held_decoded", None)
    output = {
        "schema": "gdt606-historical-mixed-codebook-attack-v1",
        "unit_sequences_sha256": sha(data_path),
        "reference_sources": reference_hashes,
        "configuration_grid": CONFIGS,
        "primary_config": PRIMARY,
        "objective": (
            "sqrt-type-weighted train chunk char-4 bits/decoded-char plus 0.35 "
            "known-reference-character fraction and fixed structural/MDL priors"
        ),
        "reference_meta": {language: pack["reference_meta"] for language, pack in packs.items()},
        "summaries": summaries,
        "decisions": decisions,
        "passing_languages": passers,
        "decision": decision,
        "artifacts": {},
        "claim_ceiling": (
            "Exploratory mixed nomenclator attack only. Stable strings are candidates, "
            "not translations, unless every frozen held and key-stability gate passes."
        ),
    }
    for name in (
        "complete_mappings.tsv", "primary_unit_stability.tsv", "stable_held_words.tsv",
        "stable_held_fragments.tsv",
        "held_decodes_latin.tsv", "held_decodes_old_italian.tsv",
        "held_decodes_middle_high_german.tsv",
    ):
        output["artifacts"][name] = sha(HERE / name)
    result_path = HERE / "mixed_attack_result.json"
    result_path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "decision": decision, "passing_languages": passers,
        "summaries": {
            language: {
                "stable_category_units": summary["stable_category_units_all_starts"],
                "stable_exact_units": summary["stable_exact_mapping_units_all_starts"],
                "stable_words": summary["stable_held_reference_words_at_75pct"],
                "stable_word_folios": summary["stable_held_reference_word_folios"],
                "stable_fragments": summary["stable_held_fragments_at_75pct"],
                "stable_fragment_folios": summary["stable_held_fragment_folios"],
            }
            for language, summary in summaries.items()
        },
        "sha256": sha(result_path),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
