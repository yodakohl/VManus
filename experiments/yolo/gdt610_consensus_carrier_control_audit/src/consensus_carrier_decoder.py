#!/usr/bin/env python3
"""Anchor-first, consensus-coupled decoder for the frozen 98-unit corpus.

The planted-key control chooses the coupling weight.  Target held records are
not touched by fitting or hyperparameter selection.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import statistics
import unicodedata
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path

ACTIVE = "abcdefghilmnopqrstuvxyz"
ALPHABET = "abcdefghijklmnopqrstuvwxyz "
UNIT_SHA256 = "3ee0841e211314b72719acbbf79ed3a6dc7bfc3c157734f54dbdac92ac458fdf"
CATEGORY_COUNTS = {"L": 42, "D": 4, "S": 34, "N": 7, "W": 11}
LAMBDA_GRID = (0.0, 0.03, 0.10, 0.30, 1.00)
MEMBERS = 6
REFERENCE_HASHES = {
    "caesar_la.txt": "84ac8411841a4d8f5f4a49b6a2cd1f466917c6a5af72916d5e0b2b1ecb2f659c",
    "divina_commedia.txt": "aafa15bbc0644dac7680ce3d0e4494b99775fbc83394cb7ad88145a0f8d6b31e",
    "mhg/Erec-conll.txt": "367cc2e9d0b60aadee501c187864dea97c77af41303f216986cfa35575f43675",
    "mhg/Iwein-conll.txt": "5b43f962da24d5b438ff93f64f30036087fe37d1cd5863c0bd29e764957b6a6f",
    "mhg/Parzival-conll.txt": "9d7ef5fd1842f6197121b654eb3c57a307ff01a9698768e27be069732afdf5cf",
    "mhg/Rolandslied-conll.txt": "46b078128c6932759d56a6a4bf13f9c3bf84d88f7a8d0e35fca31670cc0191fa",
    "mhg/Willehalm-conll.txt": "abee7d5d1aee54fa944e0d311d4645455503d4fc0bbd9ef919c46a9cfd10e7fe",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable_int(text: str) -> int:
    return int(hashlib.sha256(text.encode()).hexdigest()[:16], 16)


def normalize_word(word: str) -> str:
    value = word.lower().replace("æ", "ae").replace("œ", "oe").replace("ß", "ss")
    value = "".join(
        char for char in unicodedata.normalize("NFKD", value)
        if not unicodedata.combining(char)
    )
    value = value.replace("j", "i").replace("k", "c").replace("w", "uu")
    return "".join(char for char in value if char in ACTIVE)


def words_from_text(text: str) -> list[str]:
    words, buf = [], []
    for char in text:
        if char.isalpha() or char in "æœß":
            buf.append(char)
        elif buf:
            word = normalize_word("".join(buf))
            if word:
                words.append(word)
            buf = []
    if buf:
        word = normalize_word("".join(buf))
        if word:
            words.append(word)
    return words


def entropy(counter: Counter) -> float:
    total = sum(counter.values())
    if total <= 1 or len(counter) <= 1:
        return 0.0
    value = -sum((n / total) * math.log2(n / total) for n in counter.values())
    return value / math.log2(len(counter))


class NgramModel:
    def __init__(self, order: int = 4, alpha: float = 0.20):
        self.order = order
        self.alpha = alpha
        self.counts = [defaultdict(Counter) for _ in range(order)]
        self.totals = [Counter() for _ in range(order)]

    def fit(self, words: list[str]):
        for word in words:
            text = " " * (self.order - 1) + word + " "
            for index in range(self.order - 1, len(text)):
                nxt = text[index]
                for size in range(self.order):
                    context = text[index - size:index] if size else ""
                    self.counts[size][context][nxt] += 1
                    self.totals[size][context] += 1
        return self

    def log_score_word(self, word: str) -> tuple[float, int]:
        text = " " * (self.order - 1) + word + " "
        total = 0.0
        scored = 0
        vocab = len(ALPHABET)
        for index in range(self.order - 1, len(text)):
            nxt = text[index]
            context = text[index - self.order + 1:index]
            count = self.counts[self.order - 1][context][nxt]
            denom = self.totals[self.order - 1][context]
            # Interpolated unigram backoff makes unseen contexts finite.
            back_count = self.counts[0][""][nxt]
            back_total = self.totals[0][""]
            back = (back_count + 1.0) / (back_total + vocab)
            probability = (count + self.alpha * vocab * back) / (
                denom + self.alpha * vocab
            )
            total += math.log2(probability)
            scored += 1
        return total, scored


def destroy_words(words: list[str], language: str) -> list[str]:
    output = []
    for index, word in enumerate(words):
        chars = list(word)
        random.Random(stable_int(f"consensus-null|{language}|{index}")).shuffle(chars)
        output.append("".join(chars))
    return output


def ranked_candidates(counts: Counter):
    word_pool = [
        word for word, count in counts.most_common()
        if 2 <= len(word) <= 9 and count >= 2
    ][:64]
    grams = Counter()
    for word, count in counts.items():
        for size in (2, 3):
            for index in range(len(word) - size + 1):
                grams[word[index:index + size]] += count
    syllables = [value for value, _ in sorted(
        grams.items(), key=lambda item: (-item[1], len(item[0]), item[0])
    )[:64]]
    return word_pool, syllables, grams


def load_references(reference_dir: Path):
    for relative, expected in REFERENCE_HASHES.items():
        path = reference_dir / relative
        if sha256(path) != expected:
            raise RuntimeError(f"reference binding failed: {relative}")
    caesar = (reference_dir / "caesar_la.txt").read_text(errors="strict")
    start = caesar.find("GALLIA est omnis")
    if start >= 0:
        caesar = caesar[start:]
    footer = "*** END OF THE PROJECT GUTENBERG"
    if footer in caesar:
        caesar = caesar[:caesar.find(footer)]
    italian = (reference_dir / "divina_commedia.txt").read_text(errors="strict")
    mhg = []
    for relative in REFERENCE_HASHES:
        if relative.startswith("mhg/"):
            for line in (reference_dir / relative).read_text(errors="strict").splitlines():
                if line.strip():
                    token = normalize_word(line.split("\t", 1)[0])
                    if token:
                        mhg.append(token)
    raw = {
        "latin": words_from_text(caesar),
        "old_italian": words_from_text(italian),
        "middle_high_german": mhg,
    }
    packs = {}
    for language, words in raw.items():
        # Fixed prefix only.  No cipher alignment or key is consulted.
        train, chars = [], 0
        for word in words:
            if chars >= 240_000:
                break
            train.append(word)
            chars += len(word) + 1
        destroyed = destroy_words(train, language)
        counts = Counter(train)
        null_counts = Counter(destroyed)
        word_pool, syllables, grams = ranked_candidates(counts)
        null_word_pool, null_syllables, _ = ranked_candidates(null_counts)
        letter_counts = Counter("".join(train))
        double_counts = Counter(
            char for word in train for char in ACTIVE if char * 2 in word
        )
        length_counts = Counter(map(len, train))
        packs[language] = {
            "words": words,
            "train_words": train,
            "counts": counts,
            "model": NgramModel().fit(train),
            "null_counts": null_counts,
            "null_model": NgramModel().fit(destroyed),
            "candidates": {
                "L": list(ACTIVE),
                "D": [char * 2 for char in ACTIVE],
                "S": syllables,
                "N": [""],
                "W": word_pool,
            },
            "null_candidates": {"S": null_syllables, "W": null_word_pool},
            "letter_counts": letter_counts,
            "double_counts": double_counts,
            "gram_counts": grams,
            "length_counts": length_counts,
            "meta": {
                "source_words": len(words),
                "model_words": len(train),
                "model_characters": sum(map(len, train)),
                "model_text_sha256": hashlib.sha256(" ".join(train).encode()).hexdigest(),
                "word_candidates": len(word_pool),
                "syllable_candidates": len(syllables),
            },
        }
    return packs


def anchor_categories(units: list[str], records: list[dict]):
    occurrences = Counter()
    standalone = Counter()
    starts = Counter()
    ends = Counter()
    internal = Counter()
    left = {unit: Counter() for unit in units}
    right = {unit: Counter() for unit in units}
    for record in records:
        seq = record["units"]
        for index, unit in enumerate(seq):
            occurrences[unit] += 1
            if len(seq) == 1:
                standalone[unit] += 1
            if index == 0:
                starts[unit] += 1
            if index == len(seq) - 1:
                ends[unit] += 1
            if 0 < index < len(seq) - 1:
                internal[unit] += 1
            left[unit][seq[index - 1] if index else "<B>"] += 1
            right[unit][seq[index + 1] if index + 1 < len(seq) else "<E>"] += 1
    frequencies = [occurrences[unit] for unit in units]

    def percentile(value):
        return sum(other <= value for other in frequencies) / len(frequencies)

    features = {}
    for unit in units:
        n = occurrences[unit]
        features[unit] = {
            "occurrences": n,
            "frequency_quantile": percentile(n),
            "standalone_fraction": standalone[unit] / n,
            "start_fraction": starts[unit] / n,
            "end_fraction": ends[unit] / n,
            "internal_fraction": internal[unit] / n,
            "left_entropy": entropy(left[unit]),
            "right_entropy": entropy(right[unit]),
        }
        f = features[unit]
        # Whole-word anchors are a boundary claim, never a frequency bucket.
        # Frequency enters only as a tiny negative tie-break so a frequent
        # carrier cannot outrank a genuinely standalone carrier.
        f["word_anchor_score"] = (
            4.0 * f["standalone_fraction"]
            + 0.30 * min(f["start_fraction"], f["end_fraction"])
            - 0.02 * f["frequency_quantile"]
        )
        f["null_anchor_score"] = (
            0.9 * (f["left_entropy"] + f["right_entropy"])
            + 0.35 * f["internal_fraction"]
            - 1.2 * f["standalone_fraction"]
            - 0.20 * f["frequency_quantile"]
        )
        f["double_anchor_score"] = (
            0.55 * f["frequency_quantile"]
            + 0.35 * f["internal_fraction"]
            - 0.15 * (f["left_entropy"] + f["right_entropy"])
        )
        f["syllable_anchor_score"] = (
            0.75 * f["frequency_quantile"]
            + 0.25 * f["internal_fraction"]
            + 0.10 * (f["left_entropy"] + f["right_entropy"])
        )
    remaining = set(units)
    categories = {}
    ranking = {}
    for category, field in (
        ("W", "word_anchor_score"),
        ("N", "null_anchor_score"),
        ("D", "double_anchor_score"),
        ("S", "syllable_anchor_score"),
    ):
        ranked = sorted(remaining, key=lambda u: (-features[u][field], u))
        selected = ranked[:CATEGORY_COUNTS[category]]
        for rank, unit in enumerate(selected, 1):
            categories[unit] = category
            ranking[unit] = rank
            remaining.remove(unit)
    for rank, unit in enumerate(sorted(remaining), 1):
        categories[unit] = "L"
        ranking[unit] = rank
    if Counter(categories.values()) != Counter(CATEGORY_COUNTS):
        raise AssertionError("anchor count failure")
    return categories, features, ranking


def letter_slots(letter_counts: Counter) -> list[str]:
    # A control sign is never planted for a letter absent from the independent
    # reference corpus: such a key component would be unrecoverable by design.
    observed_letters = [char for char in ACTIVE if letter_counts[char] > 0]
    allocation = Counter({char: 1 for char in observed_letters})
    while sum(allocation.values()) < CATEGORY_COUNTS["L"]:
        choice = max(
            observed_letters,
            key=lambda char: (
                letter_counts[char] / (allocation[char] + 0.75),
                -allocation[char], char,
            ),
        )
        if allocation[choice] >= 6:
            available = [char for char in observed_letters if allocation[char] < 6]
            choice = max(available, key=lambda char: letter_counts[char] / (allocation[char] + 0.75))
        allocation[choice] += 1
    slots = []
    for char in observed_letters:
        slots.extend([char] * allocation[char])
    slots.sort(key=lambda char: (-letter_counts[char] / allocation[char], char))
    return slots


def expected_output_rank(pack, category: str):
    candidates = pack["candidates"][category]
    if category == "L":
        return sorted(candidates, key=lambda x: (-pack["letter_counts"][x], x))
    if category == "D":
        return sorted(candidates, key=lambda x: (-pack["double_counts"][x[0]], x))
    if category == "S":
        return sorted(candidates, key=lambda x: (-pack["gram_counts"][x], x))
    if category == "W":
        return sorted(candidates, key=lambda x: (-pack["counts"][x], x))
    return [""]


def planted_mapping(units, categories, target_frequency, pack):
    mapping = {}
    doubled_outputs = set()
    for category in "LDSNW":
        cat_units = sorted(
            [u for u in units if categories[u] == category],
            key=lambda u: (-target_frequency[u], u),
        )
        if category == "N":
            for unit in cat_units:
                mapping[unit] = ""
        elif category == "L":
            for unit, output in zip(cat_units, letter_slots(pack["letter_counts"])):
                mapping[unit] = output
        else:
            ranked = expected_output_rank(pack, category)
            if category == "S":
                ranked = [output for output in ranked if output not in doubled_outputs]
            outputs = ranked[:len(cat_units)]
            for unit, output in zip(cat_units, outputs):
                mapping[unit] = output
            if category == "D":
                doubled_outputs.update(outputs)
    return mapping


def build_output_units(mapping, categories):
    result = defaultdict(list)
    for unit, output in mapping.items():
        if categories[unit] != "N":
            result[(categories[unit], output)].append(unit)
    return result


def segmentation_options(word, output_units, maximum_tokens):
    paths = {0: [()]}
    for position in range(len(word)):
        if position not in paths:
            continue
        for path in paths[position]:
            if len(path) >= maximum_tokens:
                continue
            options = []
            if position == 0 and ("W", word) in output_units:
                options.append((len(word), "W", word))
            for category in ("S", "D"):
                for size in (3, 2):
                    text = word[position:position + size]
                    if len(text) == size and (category, text) in output_units:
                        options.append((size, category, text))
            char = word[position]
            if ("L", char) in output_units:
                options.append((1, "L", char))
            for size, category, text in options:
                endpoint = position + size
                paths.setdefault(endpoint, []).append(path + ((category, text),))
                # Bounded beam, deterministic and category-diverse.
                paths[endpoint] = sorted(
                    set(paths[endpoint]),
                    key=lambda p: (
                        len(p),
                        -sum({"W": 4, "S": 2, "D": 1, "L": 0}[c] for c, _ in p),
                        p,
                    ),
                )[:96]
    return [path for path in paths.get(len(word), []) if len(path) <= maximum_tokens]


def choose_segmentation(options, length, serial):
    if not options:
        return None
    scored = []
    for path in options:
        nulls = length - len(path)
        diversity = len(set(category for category, _ in path))
        multi = sum({"W": 4.0, "S": 2.0, "D": 2.5, "L": 0.0}[c] for c, _ in path)
        # Hash only breaks equivalent designs; no target output is consulted.
        jitter = stable_int(f"control-path|{serial}|{path}") / 2**64
        score = 1.25 * multi + 0.30 * diversity - 0.55 * nulls + 0.03 * jitter
        scored.append((score, path))
    return max(scored, key=lambda item: (item[0], item[1]))[1]


def make_synthetic_control(data, categories, pack):
    units = data["inventory"]
    target_frequency = Counter(data["frequency"]["train"])
    oracle = planted_mapping(units, categories, target_frequency, pack)
    output_units = build_output_units(oracle, categories)
    null_units = sorted([u for u in units if categories[u] == "N"])
    usage = Counter()
    desired = {u: max(1.0, target_frequency[u]) for u in units}
    words = pack["words"]
    # A later source region supplies plaintext; wrap only if the source is short.
    source_cursor = min(len(words) // 2, 30_000)
    option_cache = {}

    def assign_unit(category, output):
        choices = output_units[(category, output)]
        return min(choices, key=lambda u: (usage[u] / desired[u], usage[u], u))

    def encode_split(template_records, split):
        nonlocal source_cursor
        generated = []
        failures = 0
        for index, template in enumerate(template_records):
            length = len(template["units"])
            chosen_word = None
            chosen_path = None
            for attempt in range(min(len(words), 20_000)):
                word = words[source_cursor % len(words)]
                source_cursor += 1
                key = (word, length)
                if key not in option_cache:
                    option_cache[key] = segmentation_options(word, output_units, length)
                path = choose_segmentation(option_cache[key], length, f"{split}|{index}|{word}")
                if path is not None:
                    chosen_word, chosen_path = word, path
                    break
            if chosen_path is None:
                failures += 1
                # Every language has one-letter words; this should not execute.
                chosen_word = next(char for char in ACTIVE if ("L", char) in output_units)
                chosen_path = (("L", chosen_word),)
            encoded = []
            for category, output in chosen_path:
                unit = assign_unit(category, output)
                usage[unit] += 1
                encoded.append(unit)
            while len(encoded) < length:
                unit = min(null_units, key=lambda u: (usage[u] / desired[u], usage[u], u))
                usage[unit] += 1
                position = stable_int(f"control-null|{split}|{index}|{len(encoded)}") % (len(encoded) + 1)
                encoded.insert(position, unit)
            generated.append({
                "chunk_index": template["chunk_index"],
                "locus": f"control_{split}_{index}",
                "page": f"control_{template['page']}",
                "physical_folio": f"control_{template['physical_folio']}",
                "section": "CONTROL",
                "units": encoded,
                "plaintext": chosen_word,
            })
        return generated, failures

    train, fail_train = encode_split(data["sequences"]["train"], "train")
    held, fail_held = encode_split(data["sequences"]["held"], "held")
    observed_before_relabel = Counter(u for record in train for u in record["units"])
    # Labels carry no information in a synthetic code.  Pair the observed
    # control-frequency ranks to the frozen target-frequency ranks.  This
    # preserves every category count and plaintext while making the control a
    # faithful rank-frequency analogue rather than only a length analogue.
    source_rank = sorted(units, key=lambda u: (-observed_before_relabel[u], u))
    target_ranked_labels = sorted(units, key=lambda u: (-target_frequency[u], u))
    rename = dict(zip(source_rank, target_ranked_labels))
    for record in train + held:
        record["units"] = [rename[unit] for unit in record["units"]]
    oracle = {rename[unit]: output for unit, output in oracle.items()}
    control_categories = {rename[unit]: category for unit, category in categories.items()}
    usage = Counter({rename[unit]: count for unit, count in usage.items()})
    observed = Counter(u for record in train for u in record["units"])
    target_values = [target_frequency[u] for u in units]
    observed_values = [observed[u] for u in units]
    target_total, observed_total = sum(target_values), sum(observed_values)
    target_p = [v / target_total for v in target_values]
    observed_p = [v / observed_total for v in observed_values]
    midpoint = [(a + b) / 2 for a, b in zip(target_p, observed_p)]
    js = 0.5 * sum(a * math.log2(a / m) for a, m in zip(target_p, midpoint) if a) + 0.5 * sum(
        b * math.log2(b / m) for b, m in zip(observed_p, midpoint) if b
    )
    target_rank = {u: i for i, u in enumerate(sorted(units, key=lambda x: (target_frequency[x], x)))}
    observed_rank = {u: i for i, u in enumerate(sorted(units, key=lambda x: (observed[x], x)))}
    n = len(units)
    rho = 1.0 - 6.0 * sum((target_rank[u] - observed_rank[u]) ** 2 for u in units) / (n * (n * n - 1))
    return {
        "sequences": {"train": train, "held": held},
        "oracle": oracle,
        "categories": control_categories,
        "usage": dict(usage),
        "meta": {
            "exact_chunk_length_sequence": True,
            "encoding_failures": fail_train + fail_held,
            "train_inventory_coverage": sum(observed[u] > 0 for u in units) / len(units),
            "train_frequency_js_divergence_bits": js,
            "train_frequency_rank_spearman": rho,
            "frequency_rank_relabeling": "descending control counts paired to descending frozen-target counts",
            "train_chunks": len(train),
            "held_chunks": len(held),
        },
    }


def decode_words(sequence, categories, mapping):
    words, buffer = [], []
    for unit in sequence:
        category = categories[unit]
        output = mapping[unit]
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


def chunk_score(sequence, categories, mapping, pack):
    words = decode_words(sequence, categories, mapping)
    if not words:
        return -18.0
    letters = sum(map(len, words))
    lm_total = 0.0
    transitions = 0
    length_score = 0.0
    length_total = sum(pack["length_counts"].values())
    for word in words:
        value, count = pack["model"].log_score_word(word)
        lm_total += value
        transitions += count
        length_score += math.log2((pack["length_counts"][len(word)] + 1) / (length_total + 24))
    overlong = sum(max(0, len(word) - 12) ** 2 for word in words)
    return (
        lm_total / max(1, transitions)
        + 0.040 * length_score / len(words)
        - 0.08 * max(0, len(words) - 2)
        - 0.01 * overlong
    )


def build_view(records, member, units):
    selected = [
        record for record in records
        if stable_int(record["physical_folio"]) % MEMBERS != member
    ]
    counter = Counter(tuple(record["units"]) for record in selected)
    chunks = list(counter)
    weights = [counter[chunk] for chunk in chunks]
    affected = {unit: set() for unit in units}
    for index, chunk in enumerate(chunks):
        for unit in set(chunk):
            affected[unit].add(index)
    frequency = Counter(unit for record in selected for unit in record["units"])
    return {
        "records": len(selected), "chunks": chunks, "weights": weights,
        "total_weight": sum(weights), "affected": affected, "frequency": frequency,
    }


def initialize_mapping(units, categories, view, pack, member, ensemble_seed):
    mapping = {}
    for category in "LDSNW":
        cat_units = sorted(
            [u for u in units if categories[u] == category],
            key=lambda u: (-view["frequency"][u], u),
        )
        if category == "N":
            for unit in cat_units:
                mapping[unit] = ""
            continue
        if category == "L":
            outputs = letter_slots(pack["letter_counts"])
        else:
            outputs = expected_output_rank(pack, category)[:len(cat_units)]
        rng = random.Random(stable_int(f"init|{ensemble_seed}|{member}|{category}"))
        # Frequency matching remains dominant; rotations create deterministic starts.
        block = max(1, len(outputs) // 7)
        permuted = []
        for start in range(0, len(outputs), block):
            part = outputs[start:start + block]
            rng.shuffle(part)
            permuted.extend(part)
        for unit, output in zip(cat_units, permuted):
            mapping[unit] = output
    return mapping


def modal_mapping(mappings, units):
    result = {}
    for unit in units:
        counts = Counter(mapping[unit] for mapping in mappings)
        result[unit] = min(counts, key=lambda output: (-counts[output], output))
    return result


def mapping_stability(mappings, units, frequency):
    total_weight = sum(frequency[u] for u in units)
    stable_types = 0
    stable_weight = 0
    mean_modal = 0.0
    for unit in units:
        count = Counter(mapping[unit] for mapping in mappings).most_common(1)[0][1]
        mean_modal += count / len(mappings)
        if count == len(mappings):
            stable_types += 1
            stable_weight += frequency[unit]
    return {
        "all_member_exact_type_fraction": stable_types / len(units),
        "all_member_exact_occurrence_weighted_fraction": stable_weight / total_weight,
        "mean_modal_type_fraction": mean_modal / len(units),
    }


class ViewOptimizer:
    def __init__(self, units, categories, mapping, view, pack):
        self.units = units
        self.categories = categories
        self.mapping = mapping
        self.view = view
        self.pack = pack
        self.scores = [chunk_score(chunk, categories, mapping, pack) for chunk in view["chunks"]]
        # Two-part MDL: plaintext typicality above plus a literal spelling cost
        # for every output stored in the codebook.  This makes a long W output
        # pay length even though all W candidates happen to be dictionary rows.
        self.key_mdl_bits = sum(
            (1 + len(mapping[unit])) * math.log2(len(ALPHABET))
            for unit in units if categories[unit] != "N"
        )
        self.objective = (
            sum(w * s for w, s in zip(view["weights"], self.scores))
            - self.key_mdl_bits
        ) / view["total_weight"]

    def proposal(self, unit, candidate):
        category = self.categories[unit]
        current = self.mapping[unit]
        if candidate == current:
            return None
        changed = {unit: candidate}
        if category in {"D", "S", "W"}:
            owner = next((u for u in self.units if u != unit and self.categories[u] == category and self.mapping[u] == candidate), None)
            if owner is not None:
                changed[owner] = current
        elif category == "L":
            owners = [u for u in self.units if self.categories[u] == "L" and self.mapping[u] == candidate]
            if len(owners) >= 6:
                owner = min(owners, key=lambda u: (self.view["frequency"][u], u))
                changed[owner] = current
        affected = set()
        for changed_unit in changed:
            affected.update(self.view["affected"][changed_unit])
        before = sum(self.view["weights"][i] * self.scores[i] for i in affected)
        old = {u: self.mapping[u] for u in changed}
        self.mapping.update(changed)
        new_scores = {i: chunk_score(self.view["chunks"][i], self.categories, self.mapping, self.pack) for i in affected}
        after = sum(self.view["weights"][i] * score for i, score in new_scores.items())
        self.mapping.update(old)
        key_delta_bits = sum(
            (len(output) - len(old[changed_unit])) * math.log2(len(ALPHABET))
            for changed_unit, output in changed.items()
        )
        delta = (after - before - key_delta_bits) / self.view["total_weight"]
        return changed, new_scores, delta

    def sweep(self, consensus, coupling, coupling_weights, reverse=False):
        candidates = self.pack["candidates"]
        ordered = sorted(self.units, key=lambda u: (-self.view["frequency"][u], u), reverse=reverse)
        accepted = 0
        for unit in ordered:
            category = self.categories[unit]
            if category == "N":
                continue
            best = None
            for candidate in candidates[category]:
                proposal = self.proposal(unit, candidate)
                if proposal is None:
                    continue
                changed, scores, language_delta = proposal
                coupling_delta = 0.0
                for changed_unit, output in changed.items():
                    before = self.mapping[changed_unit] == consensus[changed_unit]
                    after = output == consensus[changed_unit]
                    coupling_delta += coupling_weights[changed_unit] * (after - before)
                total_delta = language_delta + coupling * coupling_delta
                signature = tuple(sorted(changed.items()))
                if best is None or (total_delta, tuple(reversed(signature))) > (best[0], tuple(reversed(best[3]))):
                    best = (total_delta, changed, scores, signature, language_delta)
            if best is not None and best[0] > 1e-12:
                _, changed, scores, _, language_delta = best
                self.mapping.update(changed)
                for index, value in scores.items():
                    self.scores[index] = value
                self.objective += language_delta
                accepted += 1
        return accepted


def fit_ensemble(records, units, categories, pack, coupling, ensemble_seed, warmup_sweeps=2, coupled_rounds=4):
    views = [build_view(records, member, units) for member in range(MEMBERS)]
    optimizers = [
        ViewOptimizer(
            units, categories,
            initialize_mapping(units, categories, views[member], pack, member, ensemble_seed),
            views[member], pack,
        )
        for member in range(MEMBERS)
    ]
    all_frequency = Counter(unit for record in records for unit in record["units"])
    raw_weights = {unit: 1.0 + math.log2(1 + all_frequency[unit]) for unit in units}
    weight_total = sum(raw_weights.values())
    coupling_weights = {unit: raw_weights[unit] / weight_total for unit in units}
    trace = []
    # No consensus reward during warm-up.
    for sweep in range(warmup_sweeps):
        for member, optimizer in enumerate(optimizers):
            consensus = optimizer.mapping
            accepted = optimizer.sweep(consensus, 0.0, coupling_weights, reverse=bool(sweep % 2))
            trace.append({"phase": "warmup", "round": sweep, "member": member, "accepted": accepted, "objective": optimizer.objective})
    for round_index in range(coupled_rounds):
        consensus = modal_mapping([optimizer.mapping for optimizer in optimizers], units)
        for member, optimizer in enumerate(optimizers):
            accepted = optimizer.sweep(consensus, coupling, coupling_weights, reverse=bool(round_index % 2))
            trace.append({"phase": "coupled", "round": round_index, "member": member, "accepted": accepted, "objective": optimizer.objective})
    mappings = [deepcopy(optimizer.mapping) for optimizer in optimizers]
    return {
        "mappings": mappings,
        "consensus": modal_mapping(mappings, units),
        "stability": mapping_stability(mappings, units, all_frequency),
        "objectives": [optimizer.objective for optimizer in optimizers],
        "trace": trace,
        "view_record_counts": [view["records"] for view in views],
    }


def levenshtein(left: str, right: str) -> int:
    previous = list(range(len(right) + 1))
    for i, a in enumerate(left, 1):
        current = [i]
        for j, b in enumerate(right, 1):
            current.append(min(current[-1] + 1, previous[j] + 1, previous[j - 1] + (a != b)))
        previous = current
    return previous[-1]


def evaluate_control(ensemble, held_records, categories, oracle, units):
    held_frequency = Counter(u for record in held_records for u in record["units"])
    total_occ = sum(held_frequency.values())
    metrics = []
    decodes = []
    for member, mapping in enumerate(ensemble["mappings"]):
        exact_types = sum(mapping[u] == oracle[u] for u in units) / len(units)
        exact_weight = sum(held_frequency[u] for u in units if mapping[u] == oracle[u]) / total_occ
        correct, possible = 0, 0
        member_decodes = []
        for record in held_records:
            decoded = " ".join(decode_words(record["units"], categories, mapping))
            truth = record["plaintext"]
            distance = levenshtein(decoded, truth)
            possible += max(len(decoded), len(truth), 1)
            correct += max(len(decoded), len(truth), 1) - distance
            member_decodes.append(decoded)
        metrics.append({
            "member": member,
            "type_key_accuracy": exact_types,
            "held_occurrence_weighted_key_accuracy": exact_weight,
            "held_plaintext_character_accuracy": correct / possible,
        })
        decodes.append(member_decodes)
    consensus = ensemble["consensus"]
    consensus_type = sum(consensus[u] == oracle[u] for u in units) / len(units)
    consensus_weight = sum(held_frequency[u] for u in units if consensus[u] == oracle[u]) / total_occ
    return {
        "members": metrics,
        "mean_type_key_accuracy": statistics.mean(x["type_key_accuracy"] for x in metrics),
        "mean_held_occurrence_weighted_key_accuracy": statistics.mean(x["held_occurrence_weighted_key_accuracy"] for x in metrics),
        "mean_held_plaintext_character_accuracy": statistics.mean(x["held_plaintext_character_accuracy"] for x in metrics),
        "consensus_type_key_accuracy": consensus_type,
        "consensus_held_occurrence_weighted_key_accuracy": consensus_weight,
        "decodes": decodes,
    }


def evaluate_target(ensemble, records, categories, pack):
    rows = []
    for member, mapping in enumerate(ensemble["mappings"]):
        real_total = null_total = chars = known = 0
        decoded = []
        for record in records:
            words = decode_words(record["units"], categories, mapping)
            decoded.append(" ".join(words))
            for word in words:
                real, n = pack["model"].log_score_word(word)
                null, _ = pack["null_model"].log_score_word(word)
                real_total += real
                null_total += null
                chars += n
                if word in pack["counts"] and len(word) >= 2:
                    known += len(word)
        rows.append({
            "member": member,
            "real_minus_destroyed_bits_per_transition": (real_total - null_total) / max(1, chars),
            "reference_lexicon_character_fraction": known / max(1, sum(len(text.replace(" ", "")) for text in decoded)),
            "decoded": decoded,
        })
    return rows


def stable_carrier_fragments(ensemble, held_records, categories, pack, language, coupling_label):
    mappings = ensemble["mappings"]
    rows = []
    for record in held_records:
        seq = record["units"]
        position = 0
        while position < len(seq):
            unit = seq[position]
            outputs = [mapping[unit] for mapping in mappings]
            if len(set(outputs)) != 1 or categories[unit] == "N":
                position += 1
                continue
            end = position
            text_parts = []
            units = []
            while end < len(seq):
                current = seq[end]
                values = [mapping[current] for mapping in mappings]
                if len(set(values)) != 1 or categories[current] == "N":
                    break
                value = values[0]
                if categories[current] == "W" and text_parts:
                    break
                text_parts.append(value)
                units.append(current)
                end += 1
                if categories[current] == "W":
                    break
            text = "".join(text_parts)
            if len(text) >= 4:
                rows.append({
                    "language": language,
                    "coupling": coupling_label,
                    "page": record["page"],
                    "physical_folio": record["physical_folio"],
                    "locus": record["locus"],
                    "chunk_index": record["chunk_index"],
                    "unit_start": position,
                    "unit_end_exclusive": end,
                    "source_units": " ".join(units),
                    "fragment": text,
                    "length": len(text),
                    "exact_reference_word": int(text in pack["counts"]),
                    "reference_count": pack["counts"][text],
                })
            position = max(end, position + 1)
    return rows


def write_tsv(path: Path, rows: list[dict], fieldnames=None):
    if fieldnames is None:
        fieldnames = list(rows[0]) if rows else []
    with path.open("w", newline="") as handle:
        if fieldnames:
            writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)


def json_ready_ensemble(ensemble):
    return {key: value for key, value in ensemble.items() if key not in {"mappings", "consensus", "trace"}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--unit-sequences", type=Path, required=True)
    parser.add_argument("--reference-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    if sha256(args.unit_sequences) != UNIT_SHA256:
        raise RuntimeError("unit sequence binding failed")
    data = json.loads(args.unit_sequences.read_text())
    units = data["inventory"]
    if len(units) != 98:
        raise RuntimeError("expected 98 units")
    categories, features, anchor_rank = anchor_categories(units, data["sequences"]["train"])
    anchor_rows = []
    for unit in units:
        anchor_rows.append({
            "unit": unit, "category": categories[unit], "category_rank": anchor_rank[unit],
            **features[unit],
        })
    write_tsv(out / "anchor_categories.tsv", anchor_rows)
    packs = load_references(args.reference_dir)
    (out / "reference_metadata.json").write_text(json.dumps({
        "hashes": REFERENCE_HASHES,
        "languages": {language: pack["meta"] for language, pack in packs.items()},
    }, indent=2, sort_keys=True) + "\n")

    print("building Latin planted-key control", flush=True)
    control = make_synthetic_control(data, categories, packs["latin"])
    control_categories = control["categories"]
    (out / "synthetic_control_meta.json").write_text(json.dumps(control["meta"], indent=2, sort_keys=True) + "\n")
    write_tsv(out / "synthetic_oracle_mapping.tsv", [
        {"unit": unit, "category": control_categories[unit], "oracle_output": control["oracle"][unit],
         "train_usage": control["usage"].get(unit, 0)} for unit in units
    ])
    calibration = []
    calibration_ensembles = {}
    calibration_mapping_rows = []
    calibration_decode_rows = []
    rounds = 2 if args.quick else 4
    for coupling in LAMBDA_GRID:
        print(f"control coupling={coupling:.2f}", flush=True)
        ensemble = fit_ensemble(
            control["sequences"]["train"], units, control_categories, packs["latin"],
            coupling, ensemble_seed=1701, warmup_sweeps=1 if args.quick else 2,
            coupled_rounds=rounds,
        )
        evaluation = evaluate_control(
            ensemble, control["sequences"]["held"], control_categories, control["oracle"], units
        )
        utility = (
            evaluation["mean_held_plaintext_character_accuracy"]
            + evaluation["mean_held_occurrence_weighted_key_accuracy"]
            + evaluation["mean_type_key_accuracy"]
            + ensemble["stability"]["all_member_exact_type_fraction"]
        )
        row = {
            "coupling": coupling,
            "selection_eligible": int(coupling > 0),
            "selection_utility": utility,
            **ensemble["stability"],
            **{key: value for key, value in evaluation.items() if key not in {"members", "decodes"}},
            "mean_train_objective": statistics.mean(ensemble["objectives"]),
        }
        calibration.append(row)
        calibration_ensembles[coupling] = (ensemble, evaluation)
        for member, mapping in enumerate(ensemble["mappings"]):
            for unit in units:
                calibration_mapping_rows.append({
                    "coupling": coupling, "member": member, "unit": unit,
                    "category": control_categories[unit], "output": mapping[unit],
                    "oracle_output": control["oracle"][unit],
                    "oracle_exact": int(mapping[unit] == control["oracle"][unit]),
                })
        for index, record in enumerate(control["sequences"]["held"]):
            item = {
                "locus": record["locus"], "chunk_index": record["chunk_index"],
                "units": " ".join(record["units"]), "oracle_plaintext": record["plaintext"],
            }
            for member in range(MEMBERS):
                item[f"decoded_lambda_{coupling:.2f}_member_{member}"] = evaluation["decodes"][member][index]
            calibration_decode_rows.append(item)
    eligible = [row for row in calibration if row["selection_eligible"]]
    selected = max(eligible, key=lambda row: (row["selection_utility"], -row["coupling"]))
    selected_lambda = selected["coupling"]
    write_tsv(out / "calibration_grid.tsv", calibration)
    write_tsv(out / "calibration_complete_mappings.tsv", calibration_mapping_rows)
    # One row per held chunk, columns for every lambda/member would be unwieldy;
    # emit one long table instead.
    long_control_decodes = []
    for coupling, (_ensemble, evaluation) in calibration_ensembles.items():
        for index, record in enumerate(control["sequences"]["held"]):
            for member in range(MEMBERS):
                long_control_decodes.append({
                    "coupling": coupling, "member": member, "locus": record["locus"],
                    "chunk_index": record["chunk_index"], "units": " ".join(record["units"]),
                    "oracle_plaintext": record["plaintext"],
                    "decoded": evaluation["decodes"][member][index],
                })
    write_tsv(out / "calibration_held_decodes.tsv", long_control_decodes)
    freeze = {
        "selected_coupling": selected_lambda,
        "selection_rule": "maximum unweighted sum of four metrics among positive grid weights; smaller weight breaks exact ties",
        "grid": list(LAMBDA_GRID),
        "selected_row": selected,
        "target_held_opened_after_this_freeze": True,
    }
    (out / "CALIBRATION_FREEZE.json").write_text(json.dumps(freeze, indent=2, sort_keys=True) + "\n")
    print(f"frozen coupling={selected_lambda:.2f}; beginning target fits", flush=True)

    target_summary = {}
    mapping_rows = []
    decode_files = []
    fragment_rows = []
    for language in ("latin", "old_italian", "middle_high_german"):
        pack = packs[language]
        language_summary = {}
        decoded_by_condition = {}
        for label, coupling in (("uncoupled", 0.0), ("coupled", selected_lambda)):
            print(f"target {language} {label} coupling={coupling:.2f}", flush=True)
            ensemble = fit_ensemble(
                data["sequences"]["train"], units, categories, pack,
                coupling, ensemble_seed=stable_int(f"target|{language}") % 1_000_000,
                warmup_sweeps=1 if args.quick else 2, coupled_rounds=rounds,
            )
            evaluated = evaluate_target(ensemble, data["sequences"]["held"], categories, pack)
            decoded_by_condition[label] = evaluated
            language_summary[label] = {
                **json_ready_ensemble(ensemble),
                "held_metrics": [{key: value for key, value in row.items() if key != "decoded"} for row in evaluated],
                "mean_real_minus_destroyed_bits_per_transition": statistics.mean(
                    row["real_minus_destroyed_bits_per_transition"] for row in evaluated
                ),
                "mean_reference_lexicon_character_fraction": statistics.mean(
                    row["reference_lexicon_character_fraction"] for row in evaluated
                ),
            }
            for member, mapping in enumerate(ensemble["mappings"]):
                for unit in units:
                    mapping_rows.append({
                        "language": language, "condition": label, "coupling": coupling,
                        "member": member, "unit": unit, "category": categories[unit],
                        "output": mapping[unit],
                        "train_occurrences": data["frequency"]["train"][unit],
                        "held_occurrences": data["frequency"]["held"].get(unit, 0),
                    })
            fragment_rows.extend(stable_carrier_fragments(
                ensemble, data["sequences"]["held"], categories, pack, language, label
            ))
        target_summary[language] = language_summary
        decode_rows = []
        for index, record in enumerate(data["sequences"]["held"]):
            item = {
                "page": record["page"], "physical_folio": record["physical_folio"],
                "locus": record["locus"], "chunk_index": record["chunk_index"],
                "section": record["section"], "units": " ".join(record["units"]),
            }
            for condition in ("uncoupled", "coupled"):
                for member in range(MEMBERS):
                    item[f"{condition}_member_{member}"] = decoded_by_condition[condition][member]["decoded"][index]
            decode_rows.append(item)
        filename = f"held_decodes_{language}.tsv"
        write_tsv(out / filename, decode_rows)
        decode_files.append(filename)

    write_tsv(out / "target_complete_mappings.tsv", mapping_rows)
    fragment_rows.sort(key=lambda row: (
        row["language"], row["coupling"], -row["length"],
        row["physical_folio"], row["locus"], row["chunk_index"], row["unit_start"],
    ))
    write_tsv(out / "carrier_aligned_held_fragments.tsv", fragment_rows)
    concrete = [row for row in fragment_rows if row["coupling"] == "coupled" and row["exact_reference_word"]]
    (out / "target_summary.json").write_text(json.dumps(target_summary, indent=2, sort_keys=True) + "\n")
    result = {
        "schema": "gdt605-consensus-carrier-result-v1",
        "input_unit_sha256": UNIT_SHA256,
        "anchor_category_counts": dict(Counter(categories.values())),
        "control": control["meta"],
        "calibration_selected_coupling": selected_lambda,
        "calibration_selected_metrics": selected,
        "target": target_summary,
        "coupled_carrier_aligned_exact_reference_rows": len(concrete),
        "coupled_carrier_aligned_exact_reference_folios": len({(row["language"], row["physical_folio"]) for row in concrete}),
        "interpretation": "pending validator and hard comparison",
    }
    # Hard interpretation: coupling is validated only if control recovery is
    # nontrivial and stability does not merely replace recovery.
    control_ok = (
        selected["mean_held_plaintext_character_accuracy"] >= 0.50
        and selected["mean_held_occurrence_weighted_key_accuracy"] >= 0.50
        and selected["all_member_exact_type_fraction"] >= 0.40
    )
    if not control_ok:
        decision = "FAIL: decoder cannot recover the planted control key reliably; target consensus is not semantic evidence"
    elif not concrete:
        decision = "FAIL: control-calibrated coupling yields no carrier-aligned held dictionary fragment"
    else:
        # Still provisional: reference fitting can manufacture words.  Require
        # a positive real-vs-destroyed held language signal in every member.
        language_pass = {
            language: all(
                row["real_minus_destroyed_bits_per_transition"] > 0
                for row in target_summary[language]["coupled"]["held_metrics"]
            ) for language in target_summary
        }
        if not any(language_pass.values()):
            decision = "FAIL: stable carrier fragments do not survive the independent order-destroyed language comparison"
        else:
            decision = "PROVISIONAL ONLY: stable carrier-aligned dictionary rows exist, but language competition is unresolved"
        result["language_all_member_positive_signal"] = language_pass
    result["decision"] = decision
    (out / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

    artifact_names = [
        "PREORACLE_FREEZE.md", "consensus_carrier_decoder.py", "anchor_categories.tsv",
        "reference_metadata.json", "synthetic_control_meta.json", "synthetic_oracle_mapping.tsv",
        "calibration_grid.tsv", "calibration_complete_mappings.tsv", "calibration_held_decodes.tsv",
        "CALIBRATION_FREEZE.json", "target_complete_mappings.tsv",
        "carrier_aligned_held_fragments.tsv", "target_summary.json", "result.json",
        *decode_files,
    ]
    inventory = {
        name: {"sha256": sha256(out / name), "bytes": (out / name).stat().st_size}
        for name in artifact_names if (out / name).exists()
    }
    (out / "binding_inventory.json").write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n")
    print(decision, flush=True)


if __name__ == "__main__":
    main()
