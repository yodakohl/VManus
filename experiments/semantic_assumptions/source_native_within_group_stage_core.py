#!/usr/bin/env python3
"""Target-blind monotone-stage grammar core for complete source groups."""

from __future__ import annotations

import csv
import hashlib
import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations_with_replacement
from pathlib import Path

import numpy as np


ALPHABET = tuple("ABCDEFGHJKLMNPQRSTUVWXYZ")
INDEX = {value: index for index, value in enumerate(ALPHABET)}
ALPHA = 0.5
FIELDS = ("unit_id", "locus", "page", "physical_folio", "section", "currier", "hand", "kind", "symbol_count", "split")
CANDIDATES = ("K1", "FIXED_2", "FIXED_3", "FIXED_4", "FIXED_5", "LATENT_2", "LATENT_3", "LATENT_4", "LATENT_5")


def stable_u64(text: str) -> int:
    return int.from_bytes(hashlib.sha256(text.encode()).digest()[:8], "little")


@dataclass
class Panel:
    rows: list[dict]
    lengths: np.ndarray
    splits: np.ndarray
    curriers: np.ndarray
    folios: np.ndarray


def load_panel(path: Path) -> Panel:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("within-group stage panel schema drift")
        rows = list(reader)
    if len(rows) != 21899 or len({row["unit_id"] for row in rows}) != 21899:
        raise ValueError("within-group stage panel row drift")
    if Counter(row["split"] for row in rows) != {"TRAIN": 10753, "CAL": 5516, "TEST": 5630}:
        raise ValueError("within-group stage split drift")
    lengths = np.asarray([int(row["symbol_count"]) for row in rows], dtype=np.int64)
    if lengths.min() != 1 or lengths.max() != 11:
        raise ValueError("within-group stage length drift")
    return Panel(rows, lengths, np.asarray([row["split"] for row in rows]), np.asarray([row["currier"] for row in rows]), np.asarray([row["physical_folio"] for row in rows]))


@lru_cache(maxsize=None)
def paths_for(length: int, stages: int) -> np.ndarray:
    paths = []
    for cuts in combinations_with_replacement(range(length + 1), stages - 1):
        boundaries = (0, *cuts, length)
        path = []
        for state in range(stages):
            path.extend([state] * (boundaries[state + 1] - boundaries[state]))
        paths.append(path)
    return np.asarray(paths, dtype=np.int8)


def fixed_path(length: int, stages: int) -> np.ndarray:
    return np.minimum(stages - 1, (np.arange(length, dtype=np.int64) * stages) // length)


def _initial_theta(sequences: Counter[tuple[int, ...]], stages: int) -> np.ndarray:
    counts = np.full((stages, len(ALPHABET)), ALPHA, dtype=np.float64)
    for sequence, multiplicity in sequences.items():
        path = np.minimum(stages - 1, ((np.arange(len(sequence)) + .5) * stages / len(sequence)).astype(np.int64))
        for state, symbol in zip(path, sequence):
            counts[state, symbol] += multiplicity
    return counts / counts.sum(axis=1, keepdims=True)


def latent_log_probability(sequence: tuple[int, ...], theta: np.ndarray) -> float:
    log_theta = np.log(theta)
    forward = log_theta[:, sequence[0]].copy()
    for symbol in sequence[1:]:
        forward = log_theta[:, symbol] + np.logaddexp.accumulate(forward)
    return float(np.logaddexp.reduce(forward) - math.log(math.comb(len(sequence) + len(theta) - 1, len(theta) - 1)))


def fit_latent(sequences: Counter[tuple[int, ...]], stages: int, max_iter: int = 40) -> tuple[np.ndarray, int, float]:
    theta = _initial_theta(sequences, stages)
    last_ll = -math.inf
    for iteration in range(1, max_iter + 1):
        counts = np.full_like(theta, ALPHA)
        log_theta = np.log(theta)
        ll = 0.0
        for sequence, multiplicity in sequences.items():
            length = len(sequence)
            forward = np.empty((length, stages), dtype=np.float64)
            backward = np.empty((length, stages), dtype=np.float64)
            forward[0] = log_theta[:, sequence[0]]
            for position in range(1, length):
                forward[position] = log_theta[:, sequence[position]] + np.logaddexp.accumulate(forward[position - 1])
            backward[-1] = 0.0
            for position in range(length - 2, -1, -1):
                continuation = log_theta[:, sequence[position + 1]] + backward[position + 1]
                backward[position] = np.logaddexp.accumulate(continuation[::-1])[::-1]
            log_z = float(np.logaddexp.reduce(forward[-1]))
            ll += multiplicity * (log_z - math.log(math.comb(length + stages - 1, stages - 1)))
            for position, symbol in enumerate(sequence):
                counts[:, symbol] += multiplicity * np.exp(forward[position] + backward[position] - log_z)
        updated = counts / counts.sum(axis=1, keepdims=True)
        delta = float(np.max(np.abs(updated - theta)))
        theta = updated
        if delta < 1e-11 or (iteration > 2 and abs(ll - last_ll) / max(1, sum(map(len, sequences))) < 1e-12):
            return theta, iteration, ll
        last_ll = ll
    return theta, max_iter, ll


def fit_fixed(sequences: Counter[tuple[int, ...]], stages: int) -> np.ndarray:
    counts = np.full((stages, len(ALPHABET)), ALPHA, dtype=np.float64)
    for sequence, multiplicity in sequences.items():
        for state, symbol in zip(fixed_path(len(sequence), stages), sequence):
            counts[state, symbol] += multiplicity
    return counts / counts.sum(axis=1, keepdims=True)


def probability(sequence: tuple[int, ...], candidate: str, theta: np.ndarray) -> float:
    if candidate == "K1":
        return float(np.log(theta[0, np.asarray(sequence)]).sum())
    family, value = candidate.split("_")
    if family == "LATENT":
        return latent_log_probability(sequence, theta)
    path = fixed_path(len(sequence), int(value))
    return float(np.log(theta[path, np.asarray(sequence)]).sum())


def _counter(panel: Panel, sequences: list[tuple[int, ...]], split: str, currier: str) -> Counter[tuple[int, ...]]:
    return Counter(sequence for sequence, row in zip(sequences, panel.rows) if row["split"] == split and row["currier"] == currier)


def fit_candidates(panel: Panel, sequences: list[tuple[int, ...]]) -> tuple[dict, dict, str, str]:
    models = {}
    diagnostics = {}
    for candidate in CANDIDATES:
        models[candidate] = {}
        diagnostics[candidate] = {"iterations": {}, "train_log_likelihood": {}}
        stages = 1 if candidate == "K1" else int(candidate.split("_")[1])
        for currier in ("A", "B"):
            counter = _counter(panel, sequences, "TRAIN", currier)
            if candidate.startswith("LATENT"):
                theta, iterations, ll = fit_latent(counter, stages)
            else:
                theta = fit_fixed(counter, stages)
                iterations = 1
                ll = sum(count * probability(sequence, candidate, theta) for sequence, count in counter.items())
            models[candidate][currier] = theta
            diagnostics[candidate]["iterations"][currier] = iterations
            diagnostics[candidate]["train_log_likelihood"][currier] = ll
        ll = 0.0
        symbols = 0
        for sequence, row in zip(sequences, panel.rows):
            if row["split"] == "CAL":
                ll += probability(sequence, candidate, models[candidate][row["currier"]])
                symbols += len(sequence)
        diagnostics[candidate]["cal_log_likelihood_per_symbol"] = ll / symbols
    order = {candidate: index for index, candidate in enumerate(CANDIDATES)}
    selected = max(CANDIDATES, key=lambda candidate: (diagnostics[candidate]["cal_log_likelihood_per_symbol"], -order[candidate]))
    fixed = max((candidate for candidate in CANDIDATES if candidate.startswith("FIXED")), key=lambda candidate: (diagnostics[candidate]["cal_log_likelihood_per_symbol"], -order[candidate]))
    return models, diagnostics, selected, fixed


def exact_sign_p(positive: int, total: int) -> float:
    return sum(math.comb(total, k) for k in range(positive, total + 1)) / (2 ** total)


def _summary(values: dict[str, list[tuple[float, int]]]) -> dict:
    effects = []
    for folio in sorted(values, key=lambda value: int(value[1:])):
        numerator = sum(value for value, _ in values[folio])
        denominator = sum(length for _, length in values[folio])
        effects.append(numerator / denominator)
    array = np.asarray(effects, dtype=np.float64)
    deletion = (array.sum() - array) / (len(array) - 1)
    total_abs = float(np.abs(array).sum())
    return {
        "effect_equal_folio": float(array.mean()),
        "positive_folios": int((array > 0).sum()),
        "folios": len(array),
        "sign_p": exact_sign_p(int((array > 0).sum()), len(array)),
        "minimum_leave_one_folio_out": float(deletion.min()),
        "max_abs_contribution_fraction": float(np.abs(array).max() / total_abs) if total_abs else 1.0,
    }


def evaluate(panel: Panel, sequences: list[tuple[int, ...]]) -> dict:
    if len(sequences) != len(panel.rows) or any(len(sequence) != length for sequence, length in zip(sequences, panel.lengths)):
        raise ValueError("within-group stage sequence geometry mismatch")
    if any(not sequence or any(symbol < 0 or symbol >= len(ALPHABET) for symbol in sequence) for sequence in sequences):
        raise ValueError("within-group stage invalid sequence")
    models, diagnostics, selected, best_fixed = fit_candidates(panel, sequences)
    by_folio: dict[str, list[tuple[float, int]]] = defaultdict(list)
    adaptive_by_folio: dict[str, list[tuple[float, int]]] = defaultdict(list)
    unseen_by_folio: dict[str, list[tuple[float, int]]] = defaultdict(list)
    currier_folios: dict[str, dict[str, list[tuple[float, int]]]] = {"A": defaultdict(list), "B": defaultdict(list)}
    adaptive_currier: dict[str, dict[str, list[tuple[float, int]]]] = {"A": defaultdict(list), "B": defaultdict(list)}
    train_surfaces = {(row["currier"], sequence) for row, sequence in zip(panel.rows, sequences) if row["split"] == "TRAIN"}
    test_groups = test_symbols = unseen_groups = unseen_symbols = 0
    total_gain = total_adaptive = total_unseen = 0.0
    for sequence, row in zip(sequences, panel.rows):
        if row["split"] != "TEST":
            continue
        base = probability(sequence, "K1", models["K1"][row["currier"]])
        chosen = probability(sequence, selected, models[selected][row["currier"]])
        fixed = probability(sequence, best_fixed, models[best_fixed][row["currier"]])
        gain, adaptive = chosen - base, chosen - fixed
        length = len(sequence)
        folio = row["physical_folio"]
        by_folio[folio].append((gain, length))
        adaptive_by_folio[folio].append((adaptive, length))
        currier_folios[row["currier"]][folio].append((gain, length))
        adaptive_currier[row["currier"]][folio].append((adaptive, length))
        test_groups += 1; test_symbols += length; total_gain += gain; total_adaptive += adaptive
        if (row["currier"], sequence) not in train_surfaces:
            unseen_by_folio[folio].append((gain, length))
            unseen_groups += 1; unseen_symbols += length; total_unseen += gain
    result = {
        "selected_model": selected, "best_fixed_model": best_fixed,
        "candidate_diagnostics": diagnostics,
        "test_groups": test_groups, "test_symbols": test_symbols,
        "gain_equal_symbol": total_gain / test_symbols,
        "gain_vs_fixed_equal_symbol": total_adaptive / test_symbols,
        "gain": _summary(by_folio), "gain_vs_fixed": _summary(adaptive_by_folio),
        "unseen": {"groups": unseen_groups, "symbols": unseen_symbols, "gain_equal_symbol": total_unseen / unseen_symbols, **_summary(unseen_by_folio)},
        "currier": {},
    }
    for currier in ("A", "B"):
        result["currier"][currier] = {"gain": _summary(currier_folios[currier]), "gain_vs_fixed": _summary(adaptive_currier[currier])}
    return result


def positional_pass(result: dict) -> bool:
    return (
        result["selected_model"] != "K1"
        and result["test_groups"] == 5630
        and result["gain"]["folios"] == 24
        and result["gain"]["effect_equal_folio"] >= .02
        and result["gain"]["positive_folios"] >= 18
        and result["gain"]["sign_p"] <= .01
        and result["gain"]["minimum_leave_one_folio_out"] > 0
        and result["gain"]["max_abs_contribution_fraction"] <= .15
        and result["unseen"]["groups"] >= 500
        and result["unseen"]["effect_equal_folio"] >= .015
        and result["unseen"]["minimum_leave_one_folio_out"] > 0
        and all(
            result["currier"][currier]["gain"]["effect_equal_folio"] >= .01
            and result["currier"][currier]["gain"]["minimum_leave_one_folio_out"] > 0
            and result["currier"][currier]["gain"]["positive_folios"] / result["currier"][currier]["gain"]["folios"] >= .70
            for currier in ("A", "B")
        )
    )


def latent_pass(result: dict) -> bool:
    return (
        positional_pass(result)
        and result["selected_model"].startswith("LATENT_")
        and result["gain_vs_fixed"]["effect_equal_folio"] >= .005
        and result["gain_vs_fixed"]["positive_folios"] >= 17
        and result["gain_vs_fixed"]["minimum_leave_one_folio_out"] > 0
        and all(result["currier"][currier]["gain_vs_fixed"]["effect_equal_folio"] > 0 for currier in ("A", "B"))
    )


def synthetic_sequences(panel: Panel, world: int, mode: str, strength: float = .65) -> list[tuple[int, ...]]:
    output = []
    active_folio = sorted(set(panel.folios), key=lambda value: int(value[1:]))[world % len(set(panel.folios))]
    stage_maps = {}
    for currier in ("A", "B"):
        stage_maps[currier] = tuple(sorted(range(len(ALPHABET)), key=lambda symbol: stable_u64(f"SNWG001|{world}|MAP|{currier}|{symbol}"))[:3])
    for row, length in zip(panel.rows, panel.lengths):
        bucket = stable_u64(f"SNWG001|BUCKET|{row['unit_id']}") % 128
        base_order = sorted(range(len(ALPHABET)), key=lambda symbol: stable_u64(f"SNWG001|{world}|BASEMAP|{row['currier']}|{symbol}"))
        if mode == "LATENT":
            paths = paths_for(int(length), 3)
            stage_path = paths[stable_u64(f"SNWG001|{world}|PATH|{row['split']}|{row['currier']}|{length}|{bucket}") % len(paths)]
        else:
            stage_path = fixed_path(int(length), 3)
        sequence = []
        for position in range(int(length)):
            u = (stable_u64(f"SNWG001|{world}|U|{row['split']}|{row['currier']}|{length}|{bucket}|{position}") + .5) / (1 << 64)
            if u < .36:
                symbol = base_order[0]
            elif u < .57:
                symbol = base_order[1]
            else:
                symbol = stable_u64(f"SNWG001|{world}|R|{row['split']}|{row['currier']}|{length}|{bucket}|{position}") % len(ALPHABET)
            active = mode in {"LATENT", "FIXED", "CURRIER_ONE", "ONE_FOLIO"}
            active = active and (mode != "CURRIER_ONE" or row["currier"] == "B")
            active = active and (mode != "ONE_FOLIO" or row["physical_folio"] == active_folio)
            if active and u < strength:
                symbol = stage_maps[row["currier"]][int(stage_path[position])]
            sequence.append(int(symbol))
        output.append(tuple(sequence))
    if mode not in {"NULL", "LATENT", "FIXED", "CURRIER_ONE", "ONE_FOLIO"}:
        raise ValueError("unknown within-group stage synthetic mode")
    return output
