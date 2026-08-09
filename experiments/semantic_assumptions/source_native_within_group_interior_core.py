#!/usr/bin/env python3
"""Target-blind exact-length-conditioned interior-position model."""

from __future__ import annotations

import csv
import hashlib
import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np


ALPHABET = tuple("ABCDEFGHJKLMNPQRSTUVWXYZ")
ALPHA = 0.5
CANDIDATES = ("K1", "FIXED_2", "FIXED_3", "FIXED_4", "FIXED_5")
FIELDS = ("unit_id", "locus", "page", "physical_folio", "section", "currier", "hand", "kind", "original_symbol_count", "interior_symbol_count", "split")


@dataclass
class Panel:
    rows: list[dict]
    original_lengths: np.ndarray
    interior_lengths: np.ndarray
    splits: np.ndarray
    curriers: np.ndarray
    folios: np.ndarray


def stable_u64(text: str) -> int:
    return int.from_bytes(hashlib.sha256(text.encode()).digest()[:8], "little")


def load_panel(path: Path) -> Panel:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("interior panel schema drift")
        rows = list(reader)
    if len(rows) != 19203 or len({row["unit_id"] for row in rows}) != 19203:
        raise ValueError("interior panel identity drift")
    if Counter(row["split"] for row in rows) != {"TRAIN": 9364, "CAL": 4887, "TEST": 4952}:
        raise ValueError("interior split drift")
    original = np.asarray([int(row["original_symbol_count"]) for row in rows], dtype=np.int64)
    interior = np.asarray([int(row["interior_symbol_count"]) for row in rows], dtype=np.int64)
    if original.min() != 3 or original.max() != 11 or not np.array_equal(interior, original - 2):
        raise ValueError("interior length drift")
    return Panel(rows, original, interior, np.asarray([row["split"] for row in rows]), np.asarray([row["currier"] for row in rows]), np.asarray([row["physical_folio"] for row in rows]))


def fixed_path(length: int, stages: int) -> np.ndarray:
    return np.minimum(stages - 1, (np.arange(length, dtype=np.int64) * stages) // length)


def fit(panel: Panel, sequences: list[tuple[int, ...]], candidate: str) -> dict[tuple[str, int], np.ndarray]:
    stages = 1 if candidate == "K1" else int(candidate.split("_")[1])
    counts = {(currier, length): np.full((stages, len(ALPHABET)), ALPHA, dtype=np.float64) for currier in ("A", "B") for length in range(3, 12)}
    for row, sequence, original_length in zip(panel.rows, sequences, panel.original_lengths):
        if row["split"] != "TRAIN":
            continue
        path = np.zeros(len(sequence), dtype=np.int64) if candidate == "K1" else fixed_path(len(sequence), stages)
        cell = counts[(row["currier"], int(original_length))]
        for state, symbol in zip(path, sequence):
            cell[state, symbol] += 1.0
    return {key: value / value.sum(axis=1, keepdims=True) for key, value in counts.items()}


def probability(sequence: tuple[int, ...], original_length: int, currier: str, candidate: str, models: dict) -> float:
    theta = models[(currier, original_length)]
    path = np.zeros(len(sequence), dtype=np.int64) if candidate == "K1" else fixed_path(len(sequence), int(candidate.split("_")[1]))
    return float(np.log(theta[path, np.asarray(sequence)]).sum())


def sign_p(positive: int, total: int) -> float:
    return sum(math.comb(total, k) for k in range(positive, total + 1)) / (2 ** total)


def summarize(values: dict[str, list[tuple[float, int]]]) -> dict:
    effects = []
    for folio in sorted(values, key=lambda value: int(value[1:])):
        effects.append(sum(value for value, _ in values[folio]) / sum(length for _, length in values[folio]))
    array = np.asarray(effects, dtype=np.float64)
    deletion = (array.sum() - array) / (len(array) - 1)
    total_abs = float(np.abs(array).sum())
    return {
        "effect_equal_folio": float(array.mean()), "positive_folios": int((array > 0).sum()),
        "folios": len(array), "sign_p": sign_p(int((array > 0).sum()), len(array)),
        "minimum_leave_one_folio_out": float(deletion.min()),
        "max_abs_contribution_fraction": float(np.abs(array).max() / total_abs) if total_abs else 1.0,
    }


def evaluate(panel: Panel, sequences: list[tuple[int, ...]]) -> dict:
    if len(sequences) != len(panel.rows) or any(len(sequence) != length for sequence, length in zip(sequences, panel.interior_lengths)):
        raise ValueError("interior sequence geometry mismatch")
    if any(not sequence or any(symbol < 0 or symbol >= len(ALPHABET) for symbol in sequence) for sequence in sequences):
        raise ValueError("interior invalid sequence")
    models = {candidate: fit(panel, sequences, candidate) for candidate in CANDIDATES}
    diagnostics = {}
    for candidate in CANDIDATES:
        ll = 0.0; symbols = 0
        for row, sequence, original_length in zip(panel.rows, sequences, panel.original_lengths):
            if row["split"] == "CAL":
                ll += probability(sequence, int(original_length), row["currier"], candidate, models[candidate])
                symbols += len(sequence)
        diagnostics[candidate] = {"cal_log_likelihood_per_symbol": ll / symbols}
    order = {candidate: index for index, candidate in enumerate(CANDIDATES)}
    selected = max(CANDIDATES, key=lambda candidate: (diagnostics[candidate]["cal_log_likelihood_per_symbol"], -order[candidate]))
    by_folio, unseen_by_folio = defaultdict(list), defaultdict(list)
    currier_folios = {"A": defaultdict(list), "B": defaultdict(list)}
    train_surfaces = {(row["currier"], int(length), sequence) for row, length, sequence in zip(panel.rows, panel.original_lengths, sequences) if row["split"] == "TRAIN"}
    total = unseen_total = 0.0; test_groups = test_symbols = unseen_groups = unseen_symbols = 0
    for row, sequence, original_length in zip(panel.rows, sequences, panel.original_lengths):
        if row["split"] != "TEST":
            continue
        base = probability(sequence, int(original_length), row["currier"], "K1", models["K1"])
        chosen = probability(sequence, int(original_length), row["currier"], selected, models[selected])
        gain, length, folio = chosen - base, len(sequence), row["physical_folio"]
        by_folio[folio].append((gain, length)); currier_folios[row["currier"]][folio].append((gain, length))
        total += gain; test_groups += 1; test_symbols += length
        if (row["currier"], int(original_length), sequence) not in train_surfaces:
            unseen_by_folio[folio].append((gain, length)); unseen_total += gain; unseen_groups += 1; unseen_symbols += length
    return {
        "selected_model": selected, "candidate_diagnostics": diagnostics,
        "test_groups": test_groups, "test_symbols": test_symbols, "gain_equal_symbol": total / test_symbols,
        "gain": summarize(by_folio),
        "unseen": {"groups": unseen_groups, "symbols": unseen_symbols, "gain_equal_symbol": unseen_total / unseen_symbols, **summarize(unseen_by_folio)},
        "currier": {currier: {"gain": summarize(currier_folios[currier])} for currier in ("A", "B")},
    }


def passes(result: dict) -> bool:
    return (
        result["selected_model"] != "K1" and result["test_groups"] == 4952 and result["gain"]["folios"] == 24
        and result["gain"]["effect_equal_folio"] >= 0.015 and result["gain"]["positive_folios"] >= 18
        and result["gain"]["sign_p"] <= 0.01 and result["gain"]["minimum_leave_one_folio_out"] > 0
        and result["gain"]["max_abs_contribution_fraction"] <= 0.15
        and result["unseen"]["groups"] >= 500 and result["unseen"]["effect_equal_folio"] >= 0.01
        and result["unseen"]["minimum_leave_one_folio_out"] > 0
        and all(result["currier"][currier]["gain"]["effect_equal_folio"] >= 0.005
                and result["currier"][currier]["gain"]["minimum_leave_one_folio_out"] > 0
                and result["currier"][currier]["gain"]["positive_folios"] / result["currier"][currier]["gain"]["folios"] >= 0.65
                for currier in ("A", "B"))
    )


def synthetic_sequences(panel: Panel, world: int, mode: str, strength: float = 0.55) -> list[tuple[int, ...]]:
    if mode not in {"NULL", "POSITION", "CURRIER_ONE", "ONE_FOLIO", "FOLIO_RANDOM"}:
        raise ValueError("unknown interior synthetic mode")
    folios = sorted(set(panel.folios), key=lambda value: int(value[1:]))
    active_folio = folios[world % len(folios)]
    maps = {currier: tuple(sorted(range(24), key=lambda symbol: stable_u64(f"SNWGI001|{world}|MAP|{currier}|{symbol}"))[:5]) for currier in ("A", "B")}
    output = []
    for row, original_length, interior_length in zip(panel.rows, panel.original_lengths, panel.interior_lengths):
        original_length, interior_length = int(original_length), int(interior_length)
        bucket = stable_u64(f"SNWGI001|BUCKET|{row['unit_id']}") % 128
        base_order = sorted(range(24), key=lambda symbol: stable_u64(f"SNWGI001|{world}|BASE|{row['currier']}|{original_length}|{symbol}"))
        stage_map = maps[row["currier"]]
        if mode == "FOLIO_RANDOM":
            stage_map = tuple(sorted(range(24), key=lambda symbol: stable_u64(f"SNWGI001|{world}|FMAP|{row['physical_folio']}|{row['currier']}|{symbol}"))[:5])
        path = fixed_path(interior_length, 5)
        sequence = []
        for position in range(interior_length):
            u = (stable_u64(f"SNWGI001|{world}|U|{row['split']}|{row['currier']}|{original_length}|{bucket}|{position}") + 0.5) / (1 << 64)
            if u < 0.36: symbol = base_order[0]
            elif u < 0.57: symbol = base_order[1]
            else: symbol = stable_u64(f"SNWGI001|{world}|R|{row['split']}|{row['currier']}|{original_length}|{bucket}|{position}") % 24
            active = mode in {"POSITION", "CURRIER_ONE", "ONE_FOLIO", "FOLIO_RANDOM"}
            active = active and (mode != "CURRIER_ONE" or row["currier"] == "B")
            active = active and (mode != "ONE_FOLIO" or row["physical_folio"] == active_folio)
            if active and u < strength:
                symbol = stage_map[int(path[position])]
            sequence.append(int(symbol))
        output.append(tuple(sequence))
    return output
