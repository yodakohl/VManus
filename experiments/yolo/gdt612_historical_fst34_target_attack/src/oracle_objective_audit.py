#!/usr/bin/env python3
from __future__ import annotations

import csv
import itertools
import json
import math
from pathlib import Path

EXP = Path(__file__).resolve().parents[1]
ART = EXP / "artifacts"


def read_tsv(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


class CharacterModel:
    def __init__(self, words):
        size = 27
        ids = []
        for index, word in enumerate(words):
            if index:
                ids.append(26)
            ids.extend(ord(char) - 97 for char in word)
        unigram = [0.0] * size
        for value in ids:
            unigram[value] += 1
        total = sum(unigram)
        conditional = [(value + 1) / (total + size) for value in unigram]
        for order in range(1, 4):
            context_size = size ** order
            counts = [0.0] * (context_size * size)
            if len(ids) > order:
                context = 0
                for value in ids[:order]:
                    context = context * size + value
                for value in ids[order:]:
                    counts[context * size + value] += 1
                    context = (context * size + value) % context_size
            lower_rows = len(conditional) // size
            following = [0.0] * (context_size * size)
            strength = 0.25 * size
            for context in range(context_size):
                row_total = sum(counts[context * size:(context + 1) * size])
                lower = context % lower_rows
                for symbol in range(size):
                    following[context * size + symbol] = (
                        counts[context * size + symbol]
                        + strength * conditional[lower * size + symbol]
                    ) / (row_total + strength)
            conditional = following
        self.log_probability = [math.log2(value) for value in conditional]

    def score(self, words):
        letters = sum(map(len, words))
        if not letters:
            return -25.0, 0
        context = 26 * 27 * 27 + 26 * 27 + 26
        modulus = 27 ** 3
        total = 0.0
        for index, word in enumerate(words):
            if index:
                total += self.log_probability[context * 27 + 26]
                context = (context * 27 + 26) % modulus
            for char in word:
                symbol = ord(char) - 97
                total += self.log_probability[context * 27 + symbol]
                context = (context * 27 + symbol) % modulus
        total += self.log_probability[context * 27 + 26]
        return total, letters


units = {int(row["unit_id"]): row for row in read_tsv(ART / "units.tsv")}
primitives = {int(row["primitive_id"]): row for row in read_tsv(ART / "primitives.tsv")}
chunks = [
    (float(row["weight"]), [int(value) for value in row["units"].split(",")])
    for row in read_tsv(ART / "synthetic_train_chunks.tsv")
]
real_words = (ART / "latin_real_words.txt").read_text(encoding="ascii").splitlines()
destroyed_words = (ART / "latin_destroyed_words.txt").read_text(encoding="ascii").splitlines()
positive_model = CharacterModel(real_words)
negative_model = CharacterModel(destroyed_words)
lexicon = set(real_words)
core_roles = {"literal_carrier", "syllabic_carrier"}


def load_key(directory):
    mapping = {
        int(row["primitive_id"]): (
            row["role"],
            "" if row["output"] == "<EMPTY>" else row["output"],
        )
        for row in read_tsv(Path(directory) / "primitive_mapping.tsv")
    }
    overrides = {
        int(row["unit_id"]): (row["type"], row["output"])
        for row in read_tsv(Path(directory) / "merge_overrides.tsv")
    }
    return mapping, overrides


def unit_pieces(uid, mapping, overrides, memo):
    if uid in memo:
        return memo[uid]
    unit = units[uid]
    if uid in overrides:
        kind, output = overrides[uid]
        value = [
            (
                "wholeform_logogram" if kind == "wholeform" else "syllabic_carrier",
                output,
            )
        ]
    elif unit["is_primitive"] == "1":
        value = [mapping[int(unit["primitive_id"])]]
    else:
        value = (
            unit_pieces(int(unit["left_unit_id"]), mapping, overrides, memo)
            + unit_pieces(int(unit["right_unit_id"]), mapping, overrides, memo)
        )
    memo[uid] = value
    return value


def decode(sequence, mapping, overrides):
    memo = {}
    words = []
    current = ""
    roles = []
    violations = 0

    def flush():
        nonlocal current, roles, violations
        if roles:
            cores = [index for index, role in enumerate(roles) if role in core_roles]
            if not cores:
                violations += len(roles)
            else:
                first, last = cores[0], cores[-1]
                for index, role in enumerate(roles):
                    if role == "prefix_operator" and index > first:
                        violations += 1
                    if role == "suffix_operator" and index < last:
                        violations += 1
                    if role == "context_abbreviation_mark":
                        left_core = index > 0 and roles[index - 1] in core_roles
                        right_core = index + 1 < len(roles) and roles[index + 1] in core_roles
                        if not left_core and not right_core:
                            violations += 1
                    if (
                        role
                        in core_roles
                        | {"context_abbreviation_mark", "prefix_operator"}
                        and index > last
                        and "suffix_operator" in roles[last + 1:index]
                    ):
                        violations += 1
            if current:
                words.append(current)
        current = ""
        roles = []

    for uid in sequence:
        for role, output in unit_pieces(uid, mapping, overrides, memo):
            if role == "null_layout" or not output:
                continue
            if role in {"wholeform_logogram", "connector"}:
                flush()
                words.append(output)
            else:
                current += output
                roles.append(role)
    flush()
    return words, violations


def key_prior(mapping, overrides):
    value = 0.0
    for pid, (role, output) in mapping.items():
        primitive = primitives[pid]
        directional = (
            float(primitive["direct_chunk_initial_rate"])
            - float(primitive["direct_chunk_final_rate"])
        )
        if role == "prefix_operator":
            value += 0.8 * directional
        if role == "suffix_operator":
            value -= 0.8 * directional
        if primitive["primitive"] in {"C", "d", "q"} and role == "prefix_operator":
            value += 0.30
        if primitive["primitive"] == "y" and role == "suffix_operator":
            value += 0.30
        if primitive["primitive"] == "o" and role == "connector":
            value += 0.30
        if role in {
            "syllabic_carrier",
            "prefix_operator",
            "suffix_operator",
            "connector",
            "context_abbreviation_mark",
        }:
            value -= 0.08 * max(0, len(output) - 1)
        if role == "wholeform_logogram":
            value -= 0.35 + 0.08 * len(output)
    for kind, output in overrides.values():
        if kind == "short":
            value -= 6.0 + 0.5 * len(output)
        else:
            value -= 10.0 + 0.75 * len(output)
    return value


def objective(mapping, overrides):
    prior = key_prior(mapping, overrides)
    total = prior
    total_weight = 0.0
    for weight, sequence in chunks:
        words, violations = decode(sequence, mapping, overrides)
        letters = sum(map(len, words))
        if not letters:
            score = -25.0
        else:
            positive, _ = positive_model.score(words)
            negative, _ = negative_model.score(words)
            known = sum(
                len(word) for word in words if len(word) >= 2 and word in lexicon
            )
            overlong = sum(
                (len(word) - 12) ** 2 for word in words if len(word) > 12
            )
            score = (
                (positive - negative) / letters
                + 0.12 * known / letters
                - 0.03 * overlong / letters
                - 0.12 * violations
            )
        total += weight * score
        total_weight += weight
    return {
        "objective_per_sqrt_weight": total / total_weight,
        "score_without_prior_per_sqrt_weight": (total - prior) / total_weight,
        "key_prior": prior,
        "key_prior_per_sqrt_weight": prior / total_weight,
    }


def compute_rows():
    truth_mapping = {
        int(row["primitive_id"]): (
            row["role"],
            "" if row["output"] == "<EMPTY>" else row["output"],
        )
        for row in read_tsv(ART / "synthetic_truth_primitives.tsv")
    }
    truth_overrides = {
        int(row["unit_id"]): (row["type"], row["output"])
        for row in read_tsv(ART / "synthetic_truth_overrides.tsv")
    }
    keys = [("TRUTH", truth_mapping, truth_overrides)]
    for seed in range(7001, 7007):
        mapping, overrides = load_key(ART / f"keys/synthetic/seed_{seed}")
        keys.append((str(seed), mapping, overrides))

    raw = []
    for name, mapping, overrides in keys:
        scores = objective(mapping, overrides)
        raw.append(
            {
                "key": name,
                **scores,
                "primitive_role_exact_of_34": sum(
                    mapping[pid][0] == truth_mapping[pid][0] for pid in range(34)
                ),
                "primitive_role_output_exact_of_34": sum(
                    mapping[pid] == truth_mapping[pid] for pid in range(34)
                ),
                "truth_override_exact_of_8": sum(
                    overrides.get(uid) == value
                    for uid, value in truth_overrides.items()
                ),
            }
        )
    truth_score = raw[0]["objective_per_sqrt_weight"]
    ranks = {
        row["key"]: rank
        for rank, row in enumerate(
            sorted(raw, key=lambda row: (-row["objective_per_sqrt_weight"], row["key"])),
            1,
        )
    }
    for row in raw:
        row["delta_vs_truth"] = row["objective_per_sqrt_weight"] - truth_score
        row["objective_rank_of_7"] = ranks[row["key"]]
    return raw


def main():
    rows = compute_rows()
    recorded = {
        row["seed"]: float(row["train_objective"])
        for row in read_tsv(ART / "synthetic_recovery.tsv")
    }
    for row in rows[1:]:
        if abs(row["objective_per_sqrt_weight"] - recorded[row["key"]]) > 1e-10:
            raise RuntimeError("Python/C++ objective mismatch for seed " + row["key"])
    fields = list(rows[0])
    with (ART / "oracle_objective_audit.tsv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: f"{value:.12f}" if isinstance(value, float) else value
                    for key, value in row.items()
                }
            )
    print(json.dumps(rows, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
