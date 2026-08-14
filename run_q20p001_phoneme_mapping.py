#!/usr/bin/env python3
"""Run the frozen Q20P001 source-native phonotactic mapping screen."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "experiments/semantic_assumptions/results"
ALIGNMENT = RESULTS / "source_sta_group_alignment.tsv"
METHOD = ROOT / "Q20P001_PHONEME_MAPPING_METHOD.md"
AUDIT = ROOT / "Q20P001_EXTERNAL_PHONOTACTIC_SOURCE_AUDIT.md"
CORPUS = ROOT / "q20p001_asjp_v21_core40.tsv"
MANIFEST = ROOT / "q20p001_language_manifest.tsv"
PROVENANCE = ROOT / "q20p001_source_provenance.json"

OUT_FOLDS = ROOT / "q20p001_fold_scores.tsv"
OUT_MAPS = ROOT / "q20p001_mappings.tsv"
OUT_STABILITY = ROOT / "q20p001_mapping_stability.tsv"
OUT_MODULES = ROOT / "q20p001_module_realizations.tsv"
OUT_BASELINES = ROOT / "q20p001_baselines.tsv"
OUT_COUNTER = ROOT / "q20p001_counterexamples.tsv"
OUT_RESULT = ROOT / "q20p001_result.json"
OUT_REPORT = ROOT / "Q20P001_PHONEME_MAPPING_REPORT.md"

EDITIONS = ("ZL3b", "IT2a", "RF1b")
Q20_FOLIOS = tuple(f"f{x}" for x in (*range(103, 109), *range(111, 117)))
TARGETS = ("GEORGIAN", "MINGRELIAN", "LAZ", "SVAN")
CONTROLS = ("ARMENIAN", "CHECHEN", "AVAR", "BASQUE", "TURKISH", "GREEK", "ARABIC_QURANIC", "FINNISH")
LANGUAGES = TARGETS + CONTROLS
ALPHA = 0.5
RESTARTS = 3
MAX_SWEEPS = 10
RANDOM_MAPS = 128
FREQUENT_MIN = 20
MODULES = {
    "q-": ("D1",),
    "d-": ("B1",),
    "s-": ("C2",),
    "-dy": ("B1", "A2"),
    "-dal": ("B1", "A3", "B2"),
    "-dar": ("B1", "A3", "C1"),
}
FREEZE_COMMIT = "effd6c9"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def canonical_sha(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def seed_for(*parts: object) -> int:
    return int(hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest()[:16], 16)


def physical_folio(locus: str) -> str:
    match = re.match(r"(f\d+)", locus)
    if not match:
        raise RuntimeError(f"unroutable locus: {locus}")
    return match.group(1)


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    if fields is None:
        fields = []
        for row in rows:
            for key in row:
                if key not in fields:
                    fields.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_language_data() -> tuple[dict[str, list[tuple[str, ...]]], dict[str, tuple[str, ...]], dict[str, str]]:
    sequences: dict[str, list[tuple[str, ...]]] = defaultdict(list)
    # Only these two fields are retained. Glosses and source words never enter a model.
    with CORPUS.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            language = row["language_id"]
            if language in LANGUAGES:
                sequences[language].append(tuple(row["phoneme_segments"].split()))
    inventories: dict[str, tuple[str, ...]] = {}
    panels: dict[str, str] = {}
    with MANIFEST.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            language = row["language_id"]
            if language in LANGUAGES:
                inventories[language] = tuple(row["phoneme_inventory"].split())
                panels[language] = row["panel"]
    if set(sequences) != set(LANGUAGES) or set(inventories) != set(LANGUAGES):
        raise RuntimeError("frozen language panel is incomplete")
    for language in LANGUAGES:
        observed = {token for sequence in sequences[language] for token in sequence}
        if observed != set(inventories[language]):
            raise RuntimeError(f"inventory mismatch: {language}")
    return sequences, inventories, panels


def load_q20_groups() -> tuple[list[dict[str, object]], int]:
    grouped: dict[tuple[str, int], dict[str, dict[str, str]]] = defaultdict(dict)
    rejected = 0
    with ALIGNMENT.open(encoding="utf-8", newline="") as handle:
        header = handle.readline().rstrip("\r\n").split("\t")
        locus_i = header.index("locus")
        edition_i = header.index("edition")
        for raw in handle:
            values = raw.rstrip("\r\n").split("\t")
            locus = values[locus_i]
            route = re.match(r"(f\d+)", locus)
            if not route:
                continue
            folio = route.group(1)
            if folio not in Q20_FOLIOS:
                continue
            if locus.startswith("f84r"):
                raise RuntimeError("sealed f84r reached Q20 routing")
            row = dict(zip(header, values, strict=True))
            grouped[(locus, int(row["source_group_index"]))][values[edition_i]] = row
    records: list[dict[str, object]] = []
    for (locus, group_index), edition_rows in sorted(grouped.items()):
        if set(edition_rows) != set(EDITIONS):
            rejected += 1
            continue
        signatures = {
            (
                row["primary_sta_codes"],
                row["source_group_count"],
            )
            for row in edition_rows.values()
        }
        if len(signatures) != 1:
            rejected += 1
            continue
        zl = edition_rows["ZL3b"]
        codes = tuple(zl["primary_sta_codes"].split())
        if not codes or int(zl["primary_sta_symbol_count"]) != len(codes):
            raise RuntimeError(f"bad source sequence at {locus} G{group_index}")
        records.append(
            {
                "locus": locus,
                "folio": physical_folio(locus),
                "group_index": group_index,
                "codes": codes,
                "left_separator": zl["left_separator"],
                "right_separator": zl["right_separator"],
            }
        )
    if {row["folio"] for row in records} != set(Q20_FOLIOS):
        raise RuntimeError("Q20 folio census mismatch")
    return records, rejected


def kt_log_table(sequences: list[tuple[str, ...]], inventory: tuple[str, ...]) -> np.ndarray:
    index = {token: i for i, token in enumerate(inventory)}
    m = len(inventory)
    counts = np.zeros((m + 1, m + 1, m + 1), dtype=np.float64)
    for sequence in sequences:
        a = b = m
        for token in sequence:
            c = index[token]
            counts[a, b, c] += 1.0
            a, b = b, c
        counts[a, b, m] += 1.0
    totals = counts.sum(axis=2, keepdims=True)
    return -np.log2((counts + ALPHA) / (totals + ALPHA * (m + 1)))


def event_counts(groups: list[dict[str, object]], code_index: dict[str, int]) -> tuple[np.ndarray, np.ndarray, int, int]:
    counter: Counter[tuple[int, int, int]] = Counter()
    symbols = 0
    for row in groups:
        a = b = -1
        codes = row["codes"]
        assert isinstance(codes, tuple)
        for code in codes:
            c = code_index[code]
            counter[(a, b, c)] += 1
            a, b = b, c
            symbols += 1
        counter[(a, b, -2)] += 1
    triples = np.array(sorted(counter), dtype=np.int16)
    weights = np.array([counter[tuple(map(int, triple))] for triple in triples], dtype=np.float64)
    return triples, weights, symbols, len(groups)


def mapped_event_bits(triples: np.ndarray, weights: np.ndarray, mapping: np.ndarray, logp: np.ndarray) -> float:
    m = logp.shape[0] - 1
    a = np.where(triples[:, 0] < 0, m, mapping[triples[:, 0]])
    b = np.where(triples[:, 1] < 0, m, mapping[triples[:, 1]])
    c = np.where(triples[:, 2] < 0, m, mapping[triples[:, 2]])
    return float(np.dot(weights, logp[a, b, c]))


def mapping_hash(language: str, codes: tuple[str, ...], inventory: tuple[str, ...], mapping: np.ndarray) -> str:
    return canonical_sha({"language": language, "mapping": [[code, inventory[int(mapping[i])]] for i, code in enumerate(codes)]})


def optimize_mapping(
    language: str,
    held_folio: str,
    restart: int,
    triples: np.ndarray,
    weights: np.ndarray,
    codes: tuple[str, ...],
    inventory: tuple[str, ...],
    logp: np.ndarray,
) -> dict[str, object]:
    rng = random.Random(seed_for("Q20P001", language, held_folio, restart))
    g, m = len(codes), len(inventory)
    mapping = np.array([rng.randrange(m) for _ in range(g)], dtype=np.int16)
    impacted = [np.flatnonzero((triples == gene).any(axis=1)) for gene in range(g)]
    current = mapped_event_bits(triples, weights, mapping, logp)
    sweeps = 0
    proposals = 0
    for sweep in range(MAX_SWEEPS):
        sweeps += 1
        changed = False
        order = list(range(g))
        rng.shuffle(order)
        for gene in order:
            indices = impacted[gene]
            old = int(mapping[gene])
            old_sub = mapped_event_bits(triples[indices], weights[indices], mapping, logp) if len(indices) else 0.0
            best_value = old
            best_total = current
            for value in range(m):
                proposals += 1
                if value == old:
                    continue
                mapping[gene] = value
                new_sub = mapped_event_bits(triples[indices], weights[indices], mapping, logp) if len(indices) else 0.0
                total = current - old_sub + new_sub
                if total < best_total - 1e-10 or (abs(total - best_total) <= 1e-10 and value < best_value):
                    best_total = total
                    best_value = value
            mapping[gene] = best_value
            if best_value != old:
                changed = True
            current = best_total
        exact = mapped_event_bits(triples, weights, mapping, logp)
        if abs(exact - current) > 1e-7:
            raise RuntimeError("coordinate sufficient-statistic score drift")
        current = exact
        if not changed:
            break
    return {
        "restart": restart,
        "mapping": mapping.copy(),
        "training_bits": current,
        "sweeps": sweeps,
        "proposals": proposals,
        "mapping_hash": mapping_hash(language, codes, inventory, mapping),
    }


def source_kt_model(train_groups: list[dict[str, object]], codes: tuple[str, ...], code_index: dict[str, int]) -> np.ndarray:
    g = len(codes)
    counts = np.zeros((g + 1, g + 1, g + 1), dtype=np.float64)
    for row in train_groups:
        a = b = g
        sequence = row["codes"]
        assert isinstance(sequence, tuple)
        for code in sequence:
            c = code_index[code]
            counts[a, b, c] += 1.0
            a, b = b, c
        counts[a, b, g] += 1.0
    totals = counts.sum(axis=2, keepdims=True)
    return -np.log2((counts + ALPHA) / (totals + ALPHA * (g + 1)))


def source_bits(groups: list[dict[str, object]], logp: np.ndarray, code_index: dict[str, int]) -> float:
    g = logp.shape[0] - 1
    total = 0.0
    for row in groups:
        a = b = g
        sequence = row["codes"]
        assert isinstance(sequence, tuple)
        for code in sequence:
            c = code_index[code]
            total += float(logp[a, b, c])
            a, b = b, c
        total += float(logp[a, b, g])
    return total


def dictionary_bits(
    train_groups: list[dict[str, object]], held_groups: list[dict[str, object]], source_logp: np.ndarray, code_index: dict[str, int]
) -> float:
    frequencies = Counter(row["codes"] for row in train_groups)
    n = sum(frequencies.values())
    denominator = n + ALPHA * (len(frequencies) + 1)
    total = 0.0
    for row in held_groups:
        sequence = row["codes"]
        assert isinstance(sequence, tuple)
        if sequence in frequencies:
            total += -math.log2((frequencies[sequence] + ALPHA) / denominator)
        else:
            total += -math.log2(ALPHA / denominator)
            total += source_bits([row], source_logp, code_index)
    return total


def pairwise_mapping_agreement(mappings: list[np.ndarray], indices: np.ndarray) -> float:
    if len(mappings) < 2 or len(indices) == 0:
        return float("nan")
    values = []
    for left, right in itertools.combinations(mappings, 2):
        values.append(float(np.mean(left[indices] == right[indices])))
    return float(np.mean(values))


def fmt(value: float, digits: int = 6) -> str:
    return f"{value:.{digits}f}"


def main() -> None:
    sequences, inventories, panels = load_language_data()
    language_logp = {language: kt_log_table(sequences[language], inventories[language]) for language in LANGUAGES}
    records, rejected = load_q20_groups()
    codes = tuple(sorted({code for row in records for code in row["codes"]}))  # type: ignore[union-attr]
    code_index = {code: i for i, code in enumerate(codes)}
    global_counts = Counter(code for row in records for code in row["codes"])  # type: ignore[union-attr]
    frequent_indices = np.array([i for i, code in enumerate(codes) if global_counts[code] >= FREQUENT_MIN], dtype=np.int16)
    if len(records) != 4671 or len(codes) != 36:
        raise RuntimeError(f"unexpected frozen Q20 capacity: groups={len(records)} codes={len(codes)}")

    fold_rows: list[dict[str, object]] = []
    mapping_rows: list[dict[str, object]] = []
    baseline_rows: list[dict[str, object]] = []
    best_mappings: dict[str, list[np.ndarray]] = defaultdict(list)
    best_hashes: dict[str, list[str]] = defaultdict(list)
    restart_maps: dict[tuple[str, str], list[np.ndarray]] = {}
    held_totals: dict[str, float] = Counter()
    held_symbols_total: dict[str, int] = Counter()
    random_beats: dict[str, int] = Counter()
    source_total_bits = 0.0
    source_total_symbols = 0
    dictionary_total_bits = 0.0

    for held_folio in Q20_FOLIOS:
        train = [row for row in records if row["folio"] != held_folio]
        held = [row for row in records if row["folio"] == held_folio]
        train_triples, train_weights, train_symbols, train_group_count = event_counts(train, code_index)
        held_triples, held_weights, held_symbols, held_group_count = event_counts(held, code_index)
        source_model = source_kt_model(train, codes, code_index)
        source_held = source_bits(held, source_model, code_index)
        dictionary_held = dictionary_bits(train, held, source_model, code_index)
        source_total_bits += source_held
        dictionary_total_bits += dictionary_held
        source_total_symbols += held_symbols
        baseline_rows.extend(
            [
                {
                    "held_folio": held_folio,
                    "baseline": "SOURCE_STA_ORDER2_KT",
                    "held_bits": fmt(source_held, 9),
                    "held_symbols": held_symbols,
                    "held_bits_per_member": fmt(source_held / held_symbols, 9),
                    "training_only": 1,
                },
                {
                    "held_folio": held_folio,
                    "baseline": "WHOLE_GROUP_KT_ESCAPE_SOURCE_ORDER2",
                    "held_bits": fmt(dictionary_held, 9),
                    "held_symbols": held_symbols,
                    "held_bits_per_member": fmt(dictionary_held / held_symbols, 9),
                    "training_only": 1,
                },
            ]
        )

        for language in LANGUAGES:
            inventory = inventories[language]
            logp = language_logp[language]
            starts = [
                optimize_mapping(language, held_folio, restart, train_triples, train_weights, codes, inventory, logp)
                for restart in range(RESTARTS)
            ]
            starts.sort(key=lambda row: (float(row["training_bits"]), str(row["mapping_hash"])))
            best = starts[0]
            mapping = best["mapping"]
            assert isinstance(mapping, np.ndarray)
            held_bits = mapped_event_bits(held_triples, held_weights, mapping, logp)
            key_bits = len(codes) * math.log2(len(inventory))
            random_scores: list[float] = []
            for random_index in range(RANDOM_MAPS):
                rng = random.Random(seed_for("Q20P001_RANDOM", language, held_folio, random_index))
                random_mapping = np.array([rng.randrange(len(inventory)) for _ in codes], dtype=np.int16)
                random_scores.append(mapped_event_bits(held_triples, held_weights, random_mapping, logp) / held_symbols)
            random_scores.sort()
            random_median = float(np.median(random_scores))
            optimized_bps = held_bits / held_symbols
            if optimized_bps < random_median:
                random_beats[language] += 1
            held_totals[language] += held_bits
            held_symbols_total[language] += held_symbols
            best_mappings[language].append(mapping.copy())
            best_hashes[language].append(str(best["mapping_hash"]))
            restart_maps[(language, held_folio)] = [row["mapping"].copy() for row in starts]  # type: ignore[union-attr]
            fold_rows.append(
                {
                    "held_folio": held_folio,
                    "language_id": language,
                    "panel": panels[language],
                    "train_groups": train_group_count,
                    "train_source_members": train_symbols,
                    "held_groups": held_group_count,
                    "held_source_members": held_symbols,
                    "training_phonotactic_bits": fmt(float(best["training_bits"]), 9),
                    "mapping_key_bits": fmt(key_bits, 9),
                    "held_phonotactic_bits": fmt(held_bits, 9),
                    "held_bits_per_member": fmt(optimized_bps, 9),
                    "held_bits_per_member_plus_full_key": fmt((held_bits + key_bits) / held_symbols, 9),
                    "random_map_median_bps": fmt(random_median, 9),
                    "random_map_q05_bps": fmt(float(np.quantile(random_scores, 0.05)), 9),
                    "random_map_q95_bps": fmt(float(np.quantile(random_scores, 0.95)), 9),
                    "beats_random_median": int(optimized_bps < random_median),
                    "best_restart": best["restart"],
                    "coordinate_sweeps": best["sweeps"],
                    "coordinate_proposals": best["proposals"],
                    "retained_mapping_hash": best["mapping_hash"],
                    "retained_score_exact": 1,
                    "global_optimum_claimed": 0,
                }
            )
            held_counts = Counter(code for row in held for code in row["codes"])  # type: ignore[union-attr]
            train_counts = Counter(code for row in train for code in row["codes"])  # type: ignore[union-attr]
            for i, code in enumerate(codes):
                mapping_rows.append(
                    {
                        "held_folio": held_folio,
                        "language_id": language,
                        "source_sta_code": code,
                        "mapped_phoneme": inventory[int(mapping[i])],
                        "train_occurrences": train_counts[code],
                        "held_occurrences": held_counts[code],
                        "global_occurrences": global_counts[code],
                        "frequent_code": int(global_counts[code] >= FREQUENT_MIN),
                        "mapping_hash": best["mapping_hash"],
                    }
                )

    aggregate_bps = {language: held_totals[language] / held_symbols_total[language] for language in LANGUAGES}
    aggregate_random_bps = {
        language: sum(
            float(row["random_map_median_bps"]) * int(row["held_source_members"])
            for row in fold_rows
            if row["language_id"] == language
        )
        / held_symbols_total[language]
        for language in LANGUAGES
    }
    aggregate_adjusted_bps = {
        language: sum(
            float(row["held_phonotactic_bits"]) + float(row["mapping_key_bits"])
            for row in fold_rows
            if row["language_id"] == language
        )
        / held_symbols_total[language]
        for language in LANGUAGES
    }
    random_gain = {language: aggregate_random_bps[language] - aggregate_bps[language] for language in LANGUAGES}
    target_mean = float(np.mean([aggregate_bps[x] for x in TARGETS]))
    control_mean = float(np.mean([aggregate_bps[x] for x in CONTROLS]))
    observed_family_effect = target_mean - control_mean
    subset_effects = []
    for subset in itertools.combinations(LANGUAGES, 4):
        remainder = tuple(language for language in LANGUAGES if language not in subset)
        subset_effects.append(float(np.mean([aggregate_bps[x] for x in subset]) - np.mean([aggregate_bps[x] for x in remainder])))
    subset_p = sum(effect <= observed_family_effect + 1e-12 for effect in subset_effects) / len(subset_effects)

    stability_rows: list[dict[str, object]] = []
    module_rows: list[dict[str, object]] = []
    frequent_module_counts: dict[str, int] = {}
    all_indices = np.arange(len(codes), dtype=np.int16)
    for language in LANGUAGES:
        maps = best_mappings[language]
        within_restart = [pairwise_mapping_agreement(restart_maps[(language, folio)], all_indices) for folio in Q20_FOLIOS]
        stability_rows.append(
            {
                "language_id": language,
                "panel": panels[language],
                "aggregate_held_bits": fmt(held_totals[language], 9),
                "aggregate_held_source_members": held_symbols_total[language],
                "aggregate_held_bits_per_member": fmt(aggregate_bps[language], 9),
                "rank_all_languages": 1 + sorted(aggregate_bps.values()).index(aggregate_bps[language]),
                "cross_fold_all_code_exact_agreement": fmt(pairwise_mapping_agreement(maps, all_indices), 9),
                "cross_fold_frequent_code_exact_agreement": fmt(pairwise_mapping_agreement(maps, frequent_indices), 9),
                "frequent_code_count": len(frequent_indices),
                "unique_retained_mapping_hashes": len(set(best_hashes[language])),
                "within_fold_restart_exact_agreement_mean": fmt(float(np.mean(within_restart)), 9),
                "folds_beating_random_map_median": random_beats[language],
            }
        )
        inventory = inventories[language]
        for module, source_sequence in MODULES.items():
            if any(code not in code_index for code in source_sequence):
                raise RuntimeError(f"registered module unavailable: {module}")
            realizations = [" ".join(inventory[int(mapping[code_index[code]])] for code in source_sequence) for mapping in maps]
            mode, mode_count = Counter(realizations).most_common(1)[0]
            frequent_module_counts.setdefault(language, 0)
            frequent_module_counts[language] += int(mode_count >= 9)
            for held_folio, realization in zip(Q20_FOLIOS, realizations, strict=True):
                module_rows.append(
                    {
                        "language_id": language,
                        "panel": panels[language],
                        "module": module,
                        "source_sta_sequence": " ".join(source_sequence),
                        "held_folio": held_folio,
                        "mapped_phoneme_sequence": realization,
                        "modal_realization": mode,
                        "modal_fold_count": mode_count,
                        "stable_9_of_12": int(mode_count >= 9),
                    }
                )

    source_bps = source_total_bits / source_total_symbols
    dictionary_bps = dictionary_total_bits / source_total_symbols
    target_ranks = [1 + sorted(aggregate_bps.values()).index(aggregate_bps[x]) for x in TARGETS]
    median_control = float(np.median([aggregate_bps[x] for x in CONTROLS]))
    target_above_control_median = sum(aggregate_bps[x] < median_control for x in TARGETS)
    best_target = min(TARGETS, key=aggregate_bps.get)
    best_control = min(CONTROLS, key=aggregate_bps.get)
    best_target_stability = next(row for row in stability_rows if row["language_id"] == best_target)
    supported = (
        target_mean < control_mean
        and subset_p <= 0.05
        and target_above_control_median >= 3
        and float(best_target_stability["cross_fold_frequent_code_exact_agreement"]) >= 0.75
        and sum(random_beats[x] == len(Q20_FOLIOS) for x in TARGETS) >= 3
        and frequent_module_counts[best_target] >= 4
    )
    if len(Q20_FOLIOS) < 10 or sum(len(sequences[x]) >= 35 for x in TARGETS) < 3:
        decision = "INSUFFICIENT_PHONOTACTIC_CAPACITY"
    elif target_mean >= control_mean or aggregate_bps[best_control] < min(aggregate_bps[x] for x in TARGETS):
        decision = "KARTVELIAN_PHONOTACTIC_FIT_NOT_ABOVE_CONTROLS"
    elif supported:
        decision = "KARTVELIAN_PHONOTACTIC_ADVANTAGE_SUPPORTED"
    else:
        decision = "KARTVELIAN_PHONOTACTIC_FIT_WEAK_OR_UNSTABLE"

    counter_rows: list[dict[str, object]] = []
    counter_rows.append({
        "counterexample_id": "Q20P001_C01",
        "test": "BEST_UNRELATED_CONTROL",
        "finding": f"{best_control}={aggregate_bps[best_control]:.9f}; best_target={best_target}={aggregate_bps[best_target]:.9f}",
        "effect": "CONTROL_BETTER_THAN_TARGET" if aggregate_bps[best_control] < aggregate_bps[best_target] else "TARGET_BETTER",
    })
    counter_rows.append({
        "counterexample_id": "Q20P001_C02",
        "test": "SOURCE_STRING_BASELINE",
        "finding": f"source_KT2={source_bps:.9f}; best_external={aggregate_bps[best_target]:.9f}; whole_group={dictionary_bps:.9f}",
        "effect": "SOURCE_REFERENCE_CODE_LENGTH_LOWER_NOT_DIRECT_LIKELIHOOD_RATIO"
        if min(source_bps, dictionary_bps) < aggregate_bps[best_target]
        else "EXTERNAL_NUMERIC_SCORE_LOWER",
    })
    counter_rows.append({
        "counterexample_id": "Q20P001_C03",
        "test": "CROSS_FOLD_MAPPING_STABILITY",
        "finding": f"best_target={best_target}; frequent_code_agreement={best_target_stability['cross_fold_frequent_code_exact_agreement']}; unique_hashes={best_target_stability['unique_retained_mapping_hashes']}",
        "effect": "UNSTABLE" if float(best_target_stability["cross_fold_frequent_code_exact_agreement"]) < 0.75 else "STABLE",
    })
    counter_rows.append({
        "counterexample_id": "Q20P001_C04",
        "test": "NAMED_MODULE_STABILITY",
        "finding": f"best_target={best_target}; stable_modules_9_of_12={frequent_module_counts[best_target]}/6",
        "effect": "UNSTABLE" if frequent_module_counts[best_target] < 4 else "STABLE",
    })

    baseline_rows.extend(
        [
            {"held_folio": "ALL_12", "baseline": "SOURCE_STA_ORDER2_KT", "held_bits": fmt(source_total_bits, 9), "held_symbols": source_total_symbols, "held_bits_per_member": fmt(source_bps, 9), "training_only": 1},
            {"held_folio": "ALL_12", "baseline": "WHOLE_GROUP_KT_ESCAPE_SOURCE_ORDER2", "held_bits": fmt(dictionary_total_bits, 9), "held_symbols": source_total_symbols, "held_bits_per_member": fmt(dictionary_bps, 9), "training_only": 1},
        ]
    )

    write_tsv(OUT_FOLDS, fold_rows)
    write_tsv(OUT_MAPS, mapping_rows)
    write_tsv(OUT_STABILITY, stability_rows)
    write_tsv(OUT_MODULES, module_rows)
    write_tsv(OUT_BASELINES, baseline_rows)
    write_tsv(OUT_COUNTER, counter_rows)

    result = {
        "schema": "Q20P001_PHONEME_MAPPING_RESULT_V1",
        "status": decision,
        "exploratory": True,
        "freeze_commit": FREEZE_COMMIT,
        "question": "Source-native Q20 grapheme-to-phoneme mappings evaluated by held-folio phonotactic fit only.",
        "capacity": {
            "physical_folios": list(Q20_FOLIOS),
            "folds": len(Q20_FOLIOS),
            "strict_all_reading_groups": len(records),
            "rejected_uncertain_groups": rejected,
            "source_sta_member_inventory": list(codes),
            "source_sta_member_count": len(codes),
            "frequent_source_sta_members": [codes[int(i)] for i in frequent_indices],
            "source_members": sum(global_counts.values()),
            "f84r_rows_retained_joined_or_scored": 0,
        },
        "model": {
            "mapping": "one_source_STA_member_to_one_named_external_phoneme; many_to_one_allowed",
            "deletion_insertion_context_keys_exceptions": False,
            "external_order": 2,
            "alpha": ALPHA,
            "restarts": RESTARTS,
            "max_coordinate_sweeps": MAX_SWEEPS,
            "random_maps_per_fold_language": RANDOM_MAPS,
            "retained_score": "cpu_exact_local_optimum_not_global_optimum",
        },
        "aggregate": {
            "language_bits_per_member": {language: aggregate_bps[language] for language in LANGUAGES},
            "language_bits_per_member_plus_full_key_each_fold": aggregate_adjusted_bps,
            "language_random_map_median_bits_per_member": aggregate_random_bps,
            "language_gain_over_random_map_median_bits_per_member": random_gain,
            "language_rank": {language: 1 + sorted(aggregate_bps.values()).index(aggregate_bps[language]) for language in LANGUAGES},
            "kartvelian_mean_bits_per_member": target_mean,
            "control_mean_bits_per_member": control_mean,
            "kartvelian_minus_control_bits_per_member": observed_family_effect,
            "exact_4_of_12_subset_diagnostic_p": subset_p,
            "subset_worlds": len(subset_effects),
            "target_profiles_better_than_control_median": target_above_control_median,
            "best_target": best_target,
            "best_control": best_control,
            "target_ranks": target_ranks,
            "source_sta_order2_kt_bits_per_member": source_bps,
            "whole_group_kt_escape_bits_per_member": dictionary_bps,
            "best_target_frequent_code_cross_fold_agreement": float(best_target_stability["cross_fold_frequent_code_exact_agreement"]),
            "best_target_unique_mapping_hashes": int(best_target_stability["unique_retained_mapping_hashes"]),
            "best_target_stable_named_modules_9_of_12": frequent_module_counts[best_target],
            "target_languages_beating_random_median_all_folds": sum(random_beats[x] == len(Q20_FOLIOS) for x in TARGETS),
        },
        "decision_gates": {
            "kartvelian_mean_lower_than_controls": target_mean < control_mean,
            "subset_diagnostic_p_le_0_05": subset_p <= 0.05,
            "three_targets_better_than_control_median": target_above_control_median >= 3,
            "frequent_code_agreement_ge_0_75": float(best_target_stability["cross_fold_frequent_code_exact_agreement"]) >= 0.75,
            "three_targets_beat_random_all_folds": sum(random_beats[x] == len(Q20_FOLIOS) for x in TARGETS) >= 3,
            "four_named_modules_stable_9_of_12": frequent_module_counts[best_target] >= 4,
        },
        "negative_claims": [
            "No Georgian, Mingrelian, Laz, or Svan language identification.",
            "No phoneme value is inferred for any Voynich sign.",
            "No word, morpheme, POS, plaintext, meaning, translation, authorship, or origin is inferred.",
            "Mapped outputs are not searched for recognizable external words.",
        ],
        "inputs": {path.name: sha256(path) for path in (METHOD, AUDIT, CORPUS, MANIFEST, PROVENANCE, ALIGNMENT)},
        "implementation": {Path(__file__).name: sha256(Path(__file__))},
        "outputs": {path.name: sha256(path) for path in (OUT_FOLDS, OUT_MAPS, OUT_STABILITY, OUT_MODULES, OUT_BASELINES, OUT_COUNTER)},
    }
    OUT_RESULT.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")

    ranked = sorted(LANGUAGES, key=aggregate_bps.get)
    table = "\n".join(
        f"| {rank} | {language} | {panels[language]} | {aggregate_bps[language]:.6f} | {random_beats[language]}/12 |"
        for rank, language in enumerate(ranked, 1)
    )
    report = f"""# Q20P001 Q20 phoneme-mapping report

Status: **{decision}**

This frozen experiment fitted explicit many-to-one mappings from 36 source-native
STA member codes on eleven Q20 folios and evaluated each mapping on the twelfth.
It used 4,671 groups from twelve physical folios. ZL3b, IT2a, and RF1b supplied
one strict consensus sequence, never three samples. f84r remained sealed.

## Held-folio result

| rank | external profile | panel | aggregate held bits/member | folds beating random-map median |
|---:|---|---|---:|---:|
{table}

The frozen Kartvelian mean is **{target_mean:.6f}** bits/member and the control
mean is **{control_mean:.6f}**, for Kartvelian-minus-control
**{observed_family_effect:+.6f}**. The exact 4-of-12 panel diagnostic is
**p={subset_p:.6f}** over 495 subsets. This diagnostic does not make the twelve
languages an exchangeable population sample.

The best target profile is **{best_target}** ({aggregate_bps[best_target]:.6f});
the best unrelated control is **{best_control}** ({aggregate_bps[best_control]:.6f}).
The source-native order-2 KT baseline scores **{source_bps:.6f}** and the
whole-group KT/escape baseline **{dictionary_bps:.6f}** bits/member.
Because the phoneme map is many-to-one and has no reverse-ambiguity channel,
these reversible source-code lengths are reference baselines rather than a
direct MDL likelihood ratio against the external mapping.
Relative to each profile's own random-map median, the four target profiles gain
**{float(np.mean([random_gain[x] for x in TARGETS])):.6f}** bits/member versus
**{float(np.mean([random_gain[x] for x in CONTROLS])):.6f}** for controls. Thus
the result is not rescued by normalizing the different phoneme-inventory sizes.

## Stability and registered operations

The best target's frequent-code cross-fold direct phoneme agreement is
**{float(best_target_stability['cross_fold_frequent_code_exact_agreement']):.6f}**,
with **{best_target_stability['unique_retained_mapping_hashes']}** distinct
mapping hashes in twelve folds. Exactly **{frequent_module_counts[best_target]}/6**
registered `q-`, `d-`, `s-`, `-dy`, `-dal`, `-dar` source sequences retain the
same mapped phoneme sequence in at least 9/12 folds. This is direct named-label
agreement; no phoneme relabeling was allowed.

## Interpretation

The mapping family is flexible and the external profiles contain only 39--40
modern basic-vocabulary forms. A low score would show compatibility with that
small phonotactic model, not a decoded language. The decision follows every
frozen family-specificity, random-map, mapping-stability, and module-stability
gate. Exact fold scores, mappings, controls, and counterexamples are published
in the TSV artifacts.

No output was optimized for recognizable words. Nothing here assigns a sound,
word, morpheme, POS, plaintext, meaning, translation, authorship, or origin.
"""
    OUT_REPORT.write_text(report, encoding="utf-8")
    print(json.dumps({"status": decision, "best_target": best_target, "best_control": best_control, "target_mean": target_mean, "control_mean": control_mean, "subset_p": subset_p}, indent=2))


if __name__ == "__main__":
    main()
