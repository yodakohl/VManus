#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


ROLE_CATEGORY = {
    "literal_carrier": "literal",
    "syllabic_carrier": "syllabic",
    "prefix_operator": "prefix",
    "suffix_operator": "suffix",
    "connector": "connector",
    "context_abbreviation_mark": "context",
    "wholeform_logogram": "whole",
    "null_layout": "null",
}
CORE_ROLES = {"literal_carrier", "syllabic_carrier"}
BREAK_ROLES = {"connector", "wholeform_logogram"}
UNIFORM_27_BPS = math.log2(27.0)
TOL = 1e-12


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def text_sha256(lines: list[str]) -> str:
    payload = ("\n".join(lines) + ("\n" if lines else "")).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, fields: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({field: fmt(row.get(field, "")) for field in fields})


def fmt(value):
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, float):
        if math.isnan(value):
            return "NA"
        return f"{value:.12f}"
    return value


class CharacterModel:
    """GDT612 legacy fit or GDT613 reset-matched fit, always explicitly named."""

    def __init__(self, words: list[str], fit_score_mode: str):
        self.order = 4
        self.size = 27
        self.fit_score_mode = fit_score_mode
        ids: list[int] = []
        for index, word in enumerate(words):
            if fit_score_mode == "LEGACY_CONTINUOUS_CHUNK":
                if index:
                    ids.append(26)
            elif fit_score_mode == "RESET_MATCHED_WORD":
                # Exact fit construction in the current GDT613 fst.py:
                # three start boundaries and one terminal boundary per word.
                ids.extend((26, 26, 26))
            else:
                raise ValueError(f"unknown fit/score mode {fit_score_mode}")
            for char in word:
                if not ("a" <= char <= "z"):
                    raise ValueError(f"non-Latin-model character {char!r}")
                ids.append(ord(char) - 97)
            if fit_score_mode == "RESET_MATCHED_WORD":
                ids.append(26)

        unigram = [0.0] * self.size
        for symbol in ids:
            unigram[symbol] += 1.0
        total = sum(unigram)
        conditional = [
            (count + 1.0) / (total + self.size) for count in unigram
        ]
        for context_order in range(1, self.order):
            context_size = self.size**context_order
            counts = [0.0] * (context_size * self.size)
            if len(ids) > context_order:
                context = 0
                for symbol in ids[:context_order]:
                    context = context * self.size + symbol
                for symbol in ids[context_order:]:
                    counts[context * self.size + symbol] += 1.0
                    context = (context * self.size + symbol) % context_size
            lower_rows = len(conditional) // self.size
            following = [0.0] * (context_size * self.size)
            strength = 0.25 * self.size
            for context in range(context_size):
                start = context * self.size
                row_total = sum(counts[start : start + self.size])
                lower = context % lower_rows
                lower_start = lower * self.size
                denominator = row_total + strength
                for symbol in range(self.size):
                    following[start + symbol] = (
                        counts[start + symbol]
                        + strength * conditional[lower_start + symbol]
                    ) / denominator
            conditional = following
        self.log_probability = [math.log2(value) for value in conditional]

    def score(self, words: list[str]) -> "ChunkStat":
        if self.fit_score_mode == "RESET_MATCHED_WORD":
            return self._score_reset_words(words)
        return self._score_legacy_chunk(words)

    def _score_legacy_chunk(self, words: list[str]) -> "ChunkStat":
        # Unlike GDT612's ad-hoc empty=-25 branch, a pure generative sequence
        # scores its final boundary even when no letters were emitted.
        context = 26 * 27 * 27 + 26 * 27 + 26
        modulus = 27**3
        letter_logp = 0.0
        boundary_logp = 0.0
        letters = 0
        boundaries = 0
        for index, word in enumerate(words):
            if index:
                boundary_logp += self.log_probability[context * 27 + 26]
                context = (context * 27 + 26) % modulus
                boundaries += 1
            for char in word:
                symbol = ord(char) - 97
                letter_logp += self.log_probability[context * 27 + symbol]
                context = (context * 27 + symbol) % modulus
                letters += 1
        boundary_logp += self.log_probability[context * 27 + 26]
        boundaries += 1
        return ChunkStat(
            letter_logp=letter_logp,
            boundary_logp=boundary_logp,
            letters=letters,
            boundaries=boundaries,
            words=len(words),
            empty=int(not words),
        )

    def _score_reset_words(self, words: list[str]) -> "ChunkStat":
        # Every emitted word is evaluated from the same triple-boundary context
        # used during fit.  This is the corrected GDT613 word-reset contract,
        # kept separate from the legacy continuous-fit/chunk-score contract.
        letter_logp = 0.0
        boundary_logp = 0.0
        letters = 0
        boundaries = 0
        for word in words:
            context = 26 * 27 * 27 + 26 * 27 + 26
            modulus = 27**3
            for char in word:
                symbol = ord(char) - 97
                letter_logp += self.log_probability[context * 27 + symbol]
                context = (context * 27 + symbol) % modulus
                letters += 1
            boundary_logp += self.log_probability[context * 27 + 26]
            boundaries += 1
        if not words:
            context = 26 * 27 * 27 + 26 * 27 + 26
            boundary_logp += self.log_probability[context * 27 + 26]
            boundaries = 1
        return ChunkStat(
            letter_logp=letter_logp,
            boundary_logp=boundary_logp,
            letters=letters,
            boundaries=boundaries,
            words=len(words),
            empty=int(not words),
        )


@dataclass(frozen=True)
class ChunkStat:
    letter_logp: float
    boundary_logp: float
    letters: int
    boundaries: int
    words: int
    empty: int


@dataclass
class Aggregate:
    letter_logp: float = 0.0
    boundary_logp: float = 0.0
    letters: float = 0.0
    boundaries: float = 0.0
    words: float = 0.0
    empty_weight: float = 0.0
    source_weight: float = 0.0

    def add(self, stat: ChunkStat, weight: float) -> None:
        self.letter_logp += weight * stat.letter_logp
        self.boundary_logp += weight * stat.boundary_logp
        self.letters += weight * stat.letters
        self.boundaries += weight * stat.boundaries
        self.words += weight * stat.words
        self.empty_weight += weight * stat.empty
        self.source_weight += weight

    def replace(self, old: ChunkStat, new: ChunkStat, weight: float) -> None:
        self.letter_logp += weight * (new.letter_logp - old.letter_logp)
        self.boundary_logp += weight * (new.boundary_logp - old.boundary_logp)
        self.letters += weight * (new.letters - old.letters)
        self.boundaries += weight * (new.boundaries - old.boundaries)
        self.words += weight * (new.words - old.words)
        self.empty_weight += weight * (new.empty - old.empty)

    def copy(self) -> "Aggregate":
        return Aggregate(**self.__dict__)

    def metrics(self) -> dict[str, float]:
        total_logp = self.letter_logp + self.boundary_logp
        symbols = self.letters + self.boundaries
        return {
            "weighted_source_events": self.source_weight,
            "weighted_letters": self.letters,
            "weighted_boundaries": self.boundaries,
            "weighted_words": self.words,
            "weighted_empty_events": self.empty_weight,
            "weighted_symbols": symbols,
            "letter_log2_probability": self.letter_logp,
            "boundary_log2_probability": self.boundary_logp,
            "total_log2_probability": total_logp,
            "total_negative_log2_probability": -total_logp,
            "bits_per_scored_symbol": -total_logp / symbols,
            "bits_per_emitted_letter_including_boundaries": (
                -total_logp / self.letters if self.letters else math.nan
            ),
            "letter_bits_per_letter": (
                -self.letter_logp / self.letters if self.letters else math.nan
            ),
            "boundary_bits_per_boundary": (
                -self.boundary_logp / self.boundaries
                if self.boundaries
                else math.nan
            ),
            "boundary_bits_per_letter": (
                -self.boundary_logp / self.letters if self.letters else math.nan
            ),
            "letters_per_word": (
                self.letters / self.words if self.words else math.nan
            ),
            "symbols_per_source_event": symbols / self.source_weight,
        }


class Decoder:
    def __init__(
        self,
        units: dict[int, dict[str, str]],
        mapping: dict[int, tuple[str, str]],
        overrides: dict[int, tuple[str, str]],
    ):
        self.units = units
        self.mapping = mapping
        self.overrides = overrides
        self.memo: dict[int, list[tuple[str, str]]] = {}

    def pieces(self, uid: int) -> list[tuple[str, str]]:
        if uid in self.memo:
            return self.memo[uid]
        row = self.units[uid]
        if uid in self.overrides:
            kind, output = self.overrides[uid]
            role = "wholeform_logogram" if kind == "wholeform" else "syllabic_carrier"
            value = [(role, output)]
        elif row["is_primitive"] == "1":
            value = [self.mapping[int(row["primitive_id"])]]
        else:
            value = self.pieces(int(row["left_unit_id"])) + self.pieces(
                int(row["right_unit_id"])
            )
        self.memo[uid] = value
        return value

    def decode(self, sequence: tuple[int, ...]) -> list[str]:
        words: list[str] = []
        current = ""

        def flush() -> None:
            nonlocal current
            if current:
                words.append(current)
            current = ""

        for uid in sequence:
            for role, output in self.pieces(uid):
                if role == "null_layout" or not output:
                    continue
                if role in BREAK_ROLES:
                    flush()
                    words.append(output)
                else:
                    current += output
        flush()
        return words


def load_mapping(path: Path) -> dict[int, tuple[str, str]]:
    return {
        int(row["primitive_id"]): (
            row["role"], "" if row["output"] == "<EMPTY>" else row["output"]
        )
        for row in read_tsv(path)
    }


def load_overrides(path: Path) -> dict[int, tuple[str, str]]:
    return {
        int(row["unit_id"]): (row["type"], row["output"])
        for row in read_tsv(path)
    }


def dependency_sets(
    units: dict[int, dict[str, str]], overrides: dict[int, tuple[str, str]]
) -> dict[int, frozenset[int]]:
    memo: dict[int, frozenset[int]] = {}

    def visit(uid: int) -> frozenset[int]:
        if uid in memo:
            return memo[uid]
        row = units[uid]
        if uid in overrides:
            value = frozenset()
        elif row["is_primitive"] == "1":
            value = frozenset({int(row["primitive_id"])})
        else:
            value = visit(int(row["left_unit_id"])) | visit(
                int(row["right_unit_id"])
            )
        memo[uid] = value
        return value

    for uid in units:
        visit(uid)
    return memo


def build_aggregate(
    stats: list[ChunkStat], weights: list[float]
) -> Aggregate:
    aggregate = Aggregate()
    for stat, weight in zip(stats, weights):
        aggregate.add(stat, weight)
    return aggregate


def key_stats(
    decoder: Decoder,
    chunks: list[tuple[int, ...]],
    models: dict[str, CharacterModel],
) -> tuple[list[list[str]], dict[str, list[ChunkStat]]]:
    decoded = [decoder.decode(sequence) for sequence in chunks]
    return decoded, {
        model_name: [model.score(words) for words in decoded]
        for model_name, model in models.items()
    }


METRIC_FIELDS = [
    "weighted_source_events",
    "weighted_letters",
    "weighted_boundaries",
    "weighted_words",
    "weighted_empty_events",
    "weighted_symbols",
    "letter_log2_probability",
    "boundary_log2_probability",
    "total_log2_probability",
    "total_negative_log2_probability",
    "bits_per_scored_symbol",
    "bits_per_emitted_letter_including_boundaries",
    "letter_bits_per_letter",
    "boundary_bits_per_boundary",
    "boundary_bits_per_letter",
    "letters_per_word",
    "symbols_per_source_event",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gdt612", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    exp = args.gdt612.resolve()
    art = exp / "artifacts"
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)

    # Exact allow-list.  No directory walk or wildcard is used for inputs.
    input_paths: dict[str, Path] = {
        "units": art / "units.tsv",
        "primitives": art / "primitives.tsv",
        "train_chunks": art / "synthetic_train_chunks.tsv",
        "truth_primitives": art / "synthetic_truth_primitives.tsv",
        "truth_overrides": art / "synthetic_truth_overrides.tsv",
        "synthetic_held": art / "synthetic_held.tsv",
        "latin_candidates": art / "reference_packs/latin_real_candidates.tsv",
        "latin_words": art / "reference_packs/latin_real_words.txt",
    }
    for seed in range(7001, 7007):
        input_paths[f"seed_{seed}_primitives"] = (
            art / f"keys/synthetic/seed_{seed}/primitive_mapping.tsv"
        )
        input_paths[f"seed_{seed}_overrides"] = (
            art / f"keys/synthetic/seed_{seed}/merge_overrides.tsv"
        )
    forbidden = ("f84", "target", "guarded_rows", "held_run", "best_held")
    for label, path in input_paths.items():
        lowered = path.relative_to(art).as_posix().lower()
        if label != "synthetic_held" and any(token in lowered for token in forbidden):
            raise RuntimeError(f"forbidden input path: {path}")
        if not path.is_file():
            raise FileNotFoundError(path)

    input_manifest = [
        {
            "input_id": label,
            "relative_path": path.relative_to(exp).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for label, path in sorted(input_paths.items())
    ]
    write_tsv(
        out / "input_manifest.tsv",
        ["input_id", "relative_path", "bytes", "sha256"],
        input_manifest,
    )

    units = {int(row["unit_id"]): row for row in read_tsv(input_paths["units"])}
    primitive_rows = {
        int(row["primitive_id"]): row
        for row in read_tsv(input_paths["primitives"])
    }
    truth_mapping = load_mapping(input_paths["truth_primitives"])
    truth_overrides = load_overrides(input_paths["truth_overrides"])
    if sorted(units) != list(range(98)) or sorted(truth_mapping) != list(range(34)):
        raise RuntimeError("unexpected GDT612 capacity")

    chunk_rows = read_tsv(input_paths["train_chunks"])
    chunks = [
        tuple(int(value) for value in row["units"].split(",") if value)
        for row in chunk_rows
    ]
    count_weights = [float(row["count"]) for row in chunk_rows]
    sqrt_weights = [float(row["weight"]) for row in chunk_rows]
    schemes = {"event_count_PRIMARY": count_weights, "sqrt_count_SENSITIVITY": sqrt_weights}

    latin_words = input_paths["latin_words"].read_text(encoding="ascii").splitlines()
    if len(latin_words) != 20522:
        raise RuntimeError("unexpected Latin reference size")
    fit_end = round(0.40 * len(latin_words))
    confirm_end = round(0.60 * len(latin_words))
    lm_fit_words = latin_words[:fit_end]
    lm_confirm_words = latin_words[fit_end:confirm_end]
    held_rows = read_tsv(input_paths["synthetic_held"])
    synthetic_held_words = [row["plaintext"] for row in held_rows]
    partitions = {
        "FULL_REFERENCE": latin_words,
        "LM_FIT_40": lm_fit_words,
        "LM_CONFIRM_20": lm_confirm_words,
        "SYNTHETIC_HELD_ONLY": synthetic_held_words,
    }
    model_specs = {
        f"{mode}__{partition}": (mode, partition, words)
        for mode in ("LEGACY_CONTINUOUS_CHUNK", "RESET_MATCHED_WORD")
        for partition, words in partitions.items()
    }
    models = {
        name: CharacterModel(words, mode)
        for name, (mode, _partition, words) in model_specs.items()
    }

    partition_split_specs = {
        "FULL_REFERENCE": ("ALL", []),
        "LM_FIT_40": ("LM_CONFIRM_20", lm_confirm_words),
        "LM_CONFIRM_20": ("LM_FIT_40", lm_fit_words),
        "SYNTHETIC_HELD_ONLY": ("FULL_REFERENCE", latin_words),
    }
    split_rows = []
    split_checks: dict[str, bool] = {}
    for name, model in models.items():
        mode, partition, fit_words = model_specs[name]
        validation_name, validation_words = partition_split_specs[partition]
        if validation_words:
            stat = model.score(validation_words)
            metric = Aggregate()
            metric.add(stat, 1.0)
            values = metric.metrics()
            validation_bps = values["bits_per_scored_symbol"]
            beats_uniform = validation_bps < UNIFORM_27_BPS
        else:
            validation_bps = math.nan
            beats_uniform = True
        split_checks[name] = beats_uniform
        split_rows.append(
            {
                "model": name,
                "fit_score_mode": mode,
                "fit_partition": partition,
                "fit_words": len(fit_words),
                "fit_letters": sum(map(len, fit_words)),
                "fit_sequence_sha256": text_sha256(fit_words),
                "validation_partition": validation_name,
                "validation_words": len(validation_words),
                "validation_sequence_sha256": (
                    text_sha256(validation_words) if validation_words else "NA"
                ),
                "validation_bits_per_scored_symbol": validation_bps,
                "uniform_27_bits_per_symbol": UNIFORM_27_BPS,
                "beats_uniform": beats_uniform,
            }
        )
    write_tsv(
        out / "reference_split_audit.tsv",
        [
            "model",
            "fit_score_mode",
            "fit_partition",
            "fit_words",
            "fit_letters",
            "fit_sequence_sha256",
            "validation_partition",
            "validation_words",
            "validation_sequence_sha256",
            "validation_bits_per_scored_symbol",
            "uniform_27_bits_per_symbol",
            "beats_uniform",
        ],
        split_rows,
    )

    keys: list[tuple[str, dict[int, tuple[str, str]], dict[int, tuple[str, str]]]] = [
        ("TRUTH", truth_mapping, truth_overrides)
    ]
    for seed in range(7001, 7007):
        keys.append(
            (
                f"seed_{seed}",
                load_mapping(input_paths[f"seed_{seed}_primitives"]),
                load_overrides(input_paths[f"seed_{seed}_overrides"]),
            )
        )

    key_score_rows: list[dict] = []
    key_metrics: dict[tuple[str, str, str], dict[str, float]] = {}
    truth_decoded: list[list[str]] | None = None
    truth_stats: dict[str, list[ChunkStat]] | None = None
    truth_aggregates: dict[tuple[str, str], Aggregate] = {}
    for key_name, mapping, overrides in keys:
        decoder = Decoder(units, mapping, overrides)
        decoded, stats_by_model = key_stats(decoder, chunks, models)
        if key_name == "TRUTH":
            truth_decoded = decoded
            truth_stats = stats_by_model
        for model_name, stats in stats_by_model.items():
            for scheme_name, weights in schemes.items():
                aggregate = build_aggregate(stats, weights)
                if key_name == "TRUTH":
                    truth_aggregates[(model_name, scheme_name)] = aggregate
                metrics = aggregate.metrics()
                key_metrics[(key_name, model_name, scheme_name)] = metrics
                key_score_rows.append(
                    {
                        "key": key_name,
                        "model": model_name,
                        "weight_scheme": scheme_name,
                        **metrics,
                    }
                )
    write_tsv(
        out / "key_scores.tsv",
        ["key", "model", "weight_scheme", *METRIC_FIELDS],
        key_score_rows,
    )

    key_rank_rows = []
    for model_name in models:
        for scheme_name in schemes:
            values = [
                (
                    key_name,
                    key_metrics[(key_name, model_name, scheme_name)][
                        "bits_per_scored_symbol"
                    ],
                )
                for key_name, _mapping, _overrides in keys
            ]
            ordered = sorted(values, key=lambda item: (item[1], item[0]))
            truth_score = dict(values)["TRUTH"]
            bpl_values = [
                (
                    key_name,
                    key_metrics[(key_name, model_name, scheme_name)][
                        "bits_per_emitted_letter_including_boundaries"
                    ],
                )
                for key_name, _mapping, _overrides in keys
            ]
            truth_bpl = dict(bpl_values)["TRUTH"]
            bpl_beating = [
                name for name, score in bpl_values if score < truth_bpl - TOL
            ]
            bpl_tying = [
                name
                for name, score in bpl_values
                if name != "TRUTH" and abs(score - truth_bpl) <= TOL
            ]
            beating = [name for name, score in values if score < truth_score - TOL]
            tying = [
                name
                for name, score in values
                if name != "TRUTH" and abs(score - truth_score) <= TOL
            ]
            best_name, best_score = ordered[0]
            key_rank_rows.append(
                {
                    "model": model_name,
                    "weight_scheme": scheme_name,
                    "truth_bits_per_scored_symbol": truth_score,
                    "truth_rank_of_7": 1 + len(beating),
                    "wrong_keys_beating_truth": len(beating),
                    "wrong_keys_tying_truth": len(tying),
                    "best_key": best_name,
                    "best_bits_per_scored_symbol": best_score,
                    "next_best_wrong_key": min(
                        (item for item in values if item[0] != "TRUTH"),
                        key=lambda item: (item[1], item[0]),
                    )[0],
                    "next_best_wrong_minus_truth_bps": min(
                        score for name, score in values if name != "TRUTH"
                    )
                    - truth_score,
                    "truth_bits_per_emitted_letter_including_boundaries": truth_bpl,
                    "truth_rank_of_7_letter_denominator": 1 + len(bpl_beating),
                    "wrong_keys_beating_truth_letter_denominator": len(bpl_beating),
                    "wrong_keys_tying_truth_letter_denominator": len(bpl_tying),
                    "next_best_wrong_minus_truth_letter_denominator": min(
                        score for name, score in bpl_values if name != "TRUTH"
                    )
                    - truth_bpl,
                }
            )
    write_tsv(
        out / "key_rank_summary.tsv",
        list(key_rank_rows[0]),
        key_rank_rows,
    )

    # Exhaust the declared same-role, same-length candidate mutations.
    candidate_values: dict[str, list[str]] = defaultdict(list)
    for row in read_tsv(input_paths["latin_candidates"]):
        candidate_values[row["category"]].append(row["value"])
    for category in candidate_values:
        candidate_values[category] = sorted(set(candidate_values[category]))

    dependency_by_unit = dependency_sets(units, truth_overrides)
    affected_by_pid: dict[int, list[int]] = {pid: [] for pid in truth_mapping}
    for chunk_index, sequence in enumerate(chunks):
        deps = frozenset().union(*(dependency_by_unit[uid] for uid in sequence))
        for pid in deps:
            affected_by_pid[pid].append(chunk_index)

    mutation_catalog: list[dict] = []
    mutations: list[tuple[str, int, str, str, str]] = []
    for pid in range(34):
        role, old_output = truth_mapping[pid]
        category = ROLE_CATEGORY[role]
        used = {
            output
            for other_pid, (other_role, output) in truth_mapping.items()
            if other_pid != pid and other_role == role
        }
        values = [
            value
            for value in candidate_values.get(category, [])
            if value != old_output
            and len(value) == len(old_output)
            and value not in used
        ]
        for value in values:
            mutation_id = f"P{pid:02d}_{old_output or 'EMPTY'}_TO_{value}"
            mutations.append((mutation_id, pid, role, old_output, value))
            mutation_catalog.append(
                {
                    "mutation_id": mutation_id,
                    "primitive_id": pid,
                    "primitive": primitive_rows[pid]["primitive"],
                    "role": role,
                    "old_output": old_output or "<EMPTY>",
                    "new_output": value or "<EMPTY>",
                    "fixed_output_length": len(old_output),
                    "affected_chunk_types": len(affected_by_pid[pid]),
                    "affected_event_count": sum(
                        count_weights[index] for index in affected_by_pid[pid]
                    ),
                    "affected_sqrt_weight": sum(
                        sqrt_weights[index] for index in affected_by_pid[pid]
                    ),
                }
            )
    write_tsv(
        out / "mutation_catalog.tsv", list(mutation_catalog[0]), mutation_catalog
    )
    mutation_exposed = {
        row["mutation_id"]: row["affected_event_count"] > 0
        for row in mutation_catalog
    }
    zero_exposure_rows = []
    for pid in range(34):
        pid_rows = [row for row in mutation_catalog if row["primitive_id"] == pid]
        if pid_rows and not affected_by_pid[pid]:
            role, output = truth_mapping[pid]
            zero_exposure_rows.append(
                {
                    "primitive_id": pid,
                    "primitive": primitive_rows[pid]["primitive"],
                    "role": role,
                    "truth_output": output or "<EMPTY>",
                    "declared_same_length_mutations": len(pid_rows),
                    "affected_chunk_types": 0,
                    "affected_event_count": 0,
                    "expected_exact_score_ties_per_panel": len(pid_rows),
                }
            )
    write_tsv(
        out / "zero_exposure_tie_audit.tsv",
        list(zero_exposure_rows[0]),
        zero_exposure_rows,
    )

    assert truth_decoded is not None and truth_stats is not None
    mutation_score_rows: list[dict] = []
    mutation_metrics: dict[tuple[str, str, str], dict[str, float]] = {}
    invariant_failures: list[str] = []
    for mutation_id, pid, role, old_output, new_output in mutations:
        changed_mapping = dict(truth_mapping)
        changed_mapping[pid] = (role, new_output)
        decoder = Decoder(units, changed_mapping, truth_overrides)
        affected = affected_by_pid[pid]
        changed_words = {index: decoder.decode(chunks[index]) for index in affected}
        for model_name, model in models.items():
            changed_stats = {
                index: model.score(changed_words[index]) for index in affected
            }
            for scheme_name, weights in schemes.items():
                aggregate = truth_aggregates[(model_name, scheme_name)].copy()
                for index in affected:
                    aggregate.replace(
                        truth_stats[model_name][index], changed_stats[index], weights[index]
                    )
                metrics = aggregate.metrics()
                truth_metric = truth_aggregates[(model_name, scheme_name)].metrics()
                letter_delta = metrics["weighted_letters"] - truth_metric["weighted_letters"]
                boundary_delta = (
                    metrics["weighted_boundaries"]
                    - truth_metric["weighted_boundaries"]
                )
                word_delta = metrics["weighted_words"] - truth_metric["weighted_words"]
                if (
                    abs(letter_delta) > 1e-9
                    or abs(boundary_delta) > 1e-9
                    or abs(word_delta) > 1e-9
                ):
                    invariant_failures.append(
                        f"{mutation_id}:{model_name}:{scheme_name}"
                    )
                mutation_metrics[(mutation_id, model_name, scheme_name)] = metrics
                mutation_score_rows.append(
                    {
                        "mutation_id": mutation_id,
                        "primitive_id": pid,
                        "primitive": primitive_rows[pid]["primitive"],
                        "role": role,
                        "old_output": old_output or "<EMPTY>",
                        "new_output": new_output or "<EMPTY>",
                        "model": model_name,
                        "weight_scheme": scheme_name,
                        **metrics,
                        "delta_bits_per_scored_symbol_vs_truth": (
                            metrics["bits_per_scored_symbol"]
                            - truth_metric["bits_per_scored_symbol"]
                        ),
                        "delta_letter_nll_vs_truth": (
                            -metrics["letter_log2_probability"]
                            + truth_metric["letter_log2_probability"]
                        ),
                        "delta_boundary_nll_vs_truth": (
                            -metrics["boundary_log2_probability"]
                            + truth_metric["boundary_log2_probability"]
                        ),
                        "delta_weighted_letters_vs_truth": letter_delta,
                        "delta_weighted_boundaries_vs_truth": boundary_delta,
                        "delta_weighted_words_vs_truth": word_delta,
                    }
                )
    mutation_fields = [
        "mutation_id",
        "primitive_id",
        "primitive",
        "role",
        "old_output",
        "new_output",
        "model",
        "weight_scheme",
        *METRIC_FIELDS,
        "delta_bits_per_scored_symbol_vs_truth",
        "delta_letter_nll_vs_truth",
        "delta_boundary_nll_vs_truth",
        "delta_weighted_letters_vs_truth",
        "delta_weighted_boundaries_vs_truth",
        "delta_weighted_words_vs_truth",
    ]
    write_tsv(out / "local_mutation_scores.tsv", mutation_fields, mutation_score_rows)

    local_rank_rows = []
    local_pass: dict[tuple[str, str], bool] = {}
    for model_name in models:
        for scheme_name in schemes:
            truth_metric = truth_aggregates[(model_name, scheme_name)].metrics()
            truth_score = truth_metric["bits_per_scored_symbol"]
            panel = [
                (
                    mutation_id,
                    mutation_metrics[(mutation_id, model_name, scheme_name)],
                )
                for mutation_id, *_rest in mutations
            ]
            beating = [
                item
                for item in panel
                if item[1]["bits_per_scored_symbol"] < truth_score - TOL
            ]
            tying = [
                item
                for item in panel
                if abs(item[1]["bits_per_scored_symbol"] - truth_score) <= TOL
            ]
            exposed_panel = [item for item in panel if mutation_exposed[item[0]]]
            unexposed_panel = [item for item in panel if not mutation_exposed[item[0]]]
            exposed_beating = [
                item
                for item in exposed_panel
                if item[1]["bits_per_scored_symbol"] < truth_score - TOL
            ]
            exposed_tying = [
                item
                for item in exposed_panel
                if abs(item[1]["bits_per_scored_symbol"] - truth_score) <= TOL
            ]
            unexposed_tying = [
                item
                for item in unexposed_panel
                if abs(item[1]["bits_per_scored_symbol"] - truth_score) <= TOL
            ]
            best_id, best_metrics = min(
                panel,
                key=lambda item: (item[1]["bits_per_scored_symbol"], item[0]),
            )
            passes = not beating and not tying
            truth_bpl = truth_metric[
                "bits_per_emitted_letter_including_boundaries"
            ]
            bpl_beating = [
                item
                for item in panel
                if item[1]["bits_per_emitted_letter_including_boundaries"]
                < truth_bpl - TOL
            ]
            bpl_tying = [
                item
                for item in panel
                if abs(
                    item[1]["bits_per_emitted_letter_including_boundaries"]
                    - truth_bpl
                )
                <= TOL
            ]
            best_bpl_id, best_bpl_metrics = min(
                panel,
                key=lambda item: (
                    item[1]["bits_per_emitted_letter_including_boundaries"],
                    item[0],
                ),
            )
            local_pass[(model_name, scheme_name)] = passes
            local_rank_rows.append(
                {
                    "model": model_name,
                    "weight_scheme": scheme_name,
                    "declared_mutations": len(panel),
                    "truth_bits_per_scored_symbol": truth_score,
                    "truth_rank_of_truth_plus_local_decoys": 1 + len(beating),
                    "decoys_beating_truth": len(beating),
                    "decoys_tying_truth": len(tying),
                    "exposed_decoys": len(exposed_panel),
                    "unexposed_decoys": len(unexposed_panel),
                    "exposed_decoys_beating_truth": len(exposed_beating),
                    "exposed_decoys_tying_truth": len(exposed_tying),
                    "unexposed_decoys_tying_truth": len(unexposed_tying),
                    "truth_unique_rank_1": passes,
                    "truth_bits_per_emitted_letter_including_boundaries": truth_bpl,
                    "truth_rank_letter_denominator": 1 + len(bpl_beating),
                    "decoys_beating_truth_letter_denominator": len(bpl_beating),
                    "decoys_tying_truth_letter_denominator": len(bpl_tying),
                    "best_decoy_letter_denominator": best_bpl_id,
                    "best_decoy_minus_truth_letter_denominator": (
                        best_bpl_metrics[
                            "bits_per_emitted_letter_including_boundaries"
                        ]
                        - truth_bpl
                    ),
                    "best_decoy": best_id,
                    "best_decoy_bits_per_scored_symbol": best_metrics[
                        "bits_per_scored_symbol"
                    ],
                    "best_decoy_minus_truth_bps": (
                        best_metrics["bits_per_scored_symbol"] - truth_score
                    ),
                    "best_decoy_letter_nll_minus_truth": (
                        -best_metrics["letter_log2_probability"]
                        + truth_metric["letter_log2_probability"]
                    ),
                    "best_decoy_boundary_nll_minus_truth": (
                        -best_metrics["boundary_log2_probability"]
                        + truth_metric["boundary_log2_probability"]
                    ),
                    "best_decoy_weighted_letters_minus_truth": (
                        best_metrics["weighted_letters"]
                        - truth_metric["weighted_letters"]
                    ),
                    "best_decoy_weighted_boundaries_minus_truth": (
                        best_metrics["weighted_boundaries"]
                        - truth_metric["weighted_boundaries"]
                    ),
                }
            )
    write_tsv(
        out / "local_truth_rank_summary.tsv",
        list(local_rank_rows[0]),
        local_rank_rows,
    )

    # Explicit hard falsifier table.  Tying counts as failure.
    primary_scheme = "event_count_PRIMARY"
    key_primary_pass = {
        row["model"]: row["wrong_keys_beating_truth"] == 0
        and row["wrong_keys_tying_truth"] == 0
        for row in key_rank_rows
        if row["weight_scheme"] == primary_scheme
    }
    falsifiers = []
    for model_name in models:
        falsifiers.append(
            {
                "falsifier_id": f"F_LOCAL_{model_name}",
                "condition": "any declared fixed-length local decoy ties or beats truth",
                "triggered": not local_pass[(model_name, primary_scheme)],
                "consequence": "local pure-Latin bridge fails for this model",
            }
        )
        falsifiers.append(
            {
                "falsifier_id": f"F_KEYS_{model_name}",
                "condition": "any archived fitted pseudokey ties or beats truth",
                "triggered": not key_primary_pass[model_name],
                "consequence": "seven-key pure-Latin discrimination fails for this model",
            }
        )
    split_falsifiers = []
    for mode in ("LEGACY_CONTINUOUS_CHUNK", "RESET_MATCHED_WORD"):
        for partition, opposite in (
            ("LM_FIT_40", "LM-confirm 20%"),
            ("LM_CONFIRM_20", "LM-fit 40%"),
        ):
            name = f"{mode}__{partition}"
            split_falsifiers.append(
                {
                    "falsifier_id": f"F_SPLIT_{name}",
                    "condition": f"{name} LM does not beat uniform on {opposite} reference",
                    "triggered": not split_checks[name],
                    "consequence": "this split is non-informative",
                }
            )
    falsifiers.extend(
        [
            {
                "falsifier_id": "F_LOCAL_STRUCTURE_INVARIANCE",
                "condition": "any fixed-length mutation changes emitted letters, boundaries, or words",
                "triggered": bool(invariant_failures),
                "consequence": "implementation invalid",
            },
            {
                "falsifier_id": "F_INPUT_SCOPE",
                "condition": "an input outside the exact synthetic/reference allow-list is read",
                "triggered": False,
                "consequence": "audit invalid",
            },
        ]
        + split_falsifiers
    )
    write_tsv(
        out / "hard_falsifiers.tsv",
        ["falsifier_id", "condition", "triggered", "consequence"],
        falsifiers,
    )

    material_triggers = [row["falsifier_id"] for row in falsifiers if row["triggered"]]
    all_primary_local = all(
        local_pass[(model_name, primary_scheme)] for model_name in models
    )
    all_primary_keys = all(key_primary_pass.values())
    if all_primary_local and all_primary_keys and not invariant_failures:
        decision = "PURE_LATIN_CE_PASSES_DECLARED_LOCAL_BRIDGE"
    else:
        decision = "PURE_LATIN_CE_FAILS_AT_LEAST_ONE_DECLARED_BRIDGE_GATE"
    primary_beating_by_model = {
        model_name: sorted(
            mutation_id
            for mutation_id, *_rest in mutations
            if mutation_metrics[(mutation_id, model_name, primary_scheme)][
                "bits_per_scored_symbol"
            ]
            < truth_aggregates[(model_name, primary_scheme)].metrics()[
                "bits_per_scored_symbol"
            ]
            - TOL
        )
        for model_name in models
    }
    universally_beating = sorted(
        set.intersection(
            *(set(values) for values in primary_beating_by_model.values())
        )
    )
    results = {
        "schema": "gdt613-scratch-pure-latin-ce-v1",
        "decision": decision,
        "claim_ceiling": (
            "Local objective bridge only; no global recovery, historical key, "
            "Voynich language, plaintext, or translation claim."
        ),
        "models": list(models),
        "primary_weight_scheme": primary_scheme,
        "mutation_universe": {
            "count": len(mutations),
            "same_role": True,
            "same_output_length": True,
            "same_overrides": True,
            "candidate_inventory": "published GDT612 latin_real_candidates.tsv",
        },
        "truth_unique_rank1_all_primary_local_panels": all_primary_local,
        "truth_unique_rank1_all_primary_seven_key_panels": all_primary_keys,
        "primary_local_decoys_beating_truth_by_model": primary_beating_by_model,
        "primary_local_decoys_beating_truth_in_every_model": universally_beating,
        "zero_exposure_primitive_count": len(zero_exposure_rows),
        "zero_exposure_mutation_ties_per_panel": sum(
            row["declared_same_length_mutations"] for row in zero_exposure_rows
        ),
        "local_structure_invariance_failures": invariant_failures,
        "triggered_falsifiers": material_triggers,
        "input_count": len(input_paths),
        "train_chunk_types": len(chunks),
        "train_event_count": int(sum(count_weights)),
    }
    (out / "RESULTS.json").write_text(
        json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    validation_checks = {
        "input_allowlist_count_20": len(input_paths) == 20,
        "primitive_capacity_34": len(truth_mapping) == 34,
        "unit_capacity_98": len(units) == 98,
        "seven_keys_scored": len(keys) == 7,
        "eight_explicit_fit_score_models": len(models) == 8,
        "mutation_catalog_nonempty": len(mutations) > 0,
        "mutation_rows_complete": len(mutation_score_rows)
        == len(mutations) * len(models) * len(schemes),
        "local_structure_invariant": not invariant_failures,
        "no_forbidden_path_in_manifest": all(
            "f84" not in row["relative_path"].lower()
            and "target" not in row["relative_path"].lower()
            for row in input_manifest
        ),
        "all_split_models_crosscheck": all(split_checks.values()),
    }
    validation = {
        "status": "VALIDATION_OK" if all(validation_checks.values()) else "VALIDATION_FAILED",
        "checks": validation_checks,
        "check_count": len(validation_checks),
    }
    (out / "VALIDATION.json").write_text(
        json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    if validation["status"] != "VALIDATION_OK":
        raise RuntimeError(validation["status"])

    manifest_files = [
        "input_manifest.tsv",
        "reference_split_audit.tsv",
        "key_scores.tsv",
        "key_rank_summary.tsv",
        "mutation_catalog.tsv",
        "zero_exposure_tie_audit.tsv",
        "local_mutation_scores.tsv",
        "local_truth_rank_summary.tsv",
        "hard_falsifiers.tsv",
        "RESULTS.json",
        "VALIDATION.json",
    ]
    source_path = Path(__file__).resolve()
    companion_paths = [
        ("source", source_path),
        ("validator", source_path.parent / "validate_bridge.py"),
        ("preregistration", source_path.parent / "PREREGISTRATION.md"),
        ("report", source_path.parent / "REPORT.md"),
    ]
    output_manifest = [
        {
            "kind": kind,
            "path": path.name,
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for kind, path in companion_paths
    ] + [
        {
            "kind": "artifact",
            "path": name,
            "bytes": (out / name).stat().st_size,
            "sha256": sha256(out / name),
        }
        for name in manifest_files
    ]
    write_tsv(
        out / "OUTPUT_MANIFEST.tsv",
        ["kind", "path", "bytes", "sha256"],
        output_manifest,
    )
    print(json.dumps(results, sort_keys=True))


if __name__ == "__main__":
    main()
