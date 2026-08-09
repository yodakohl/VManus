#!/usr/bin/env python3
"""Target-free leave-folio-out onset-compatibility engine."""

from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass
from pathlib import Path

import numpy as np


PANEL_FIELDS = ("unit_id", "base_id", "physical_folio", "currier", "onset_id", "onset_consensus")
QUOTA_FIELDS = ("base_id", "physical_folio", "none_count", "da_count", "total_count")


@dataclass
class OnsetPanel:
    rows: list[dict]
    strata: tuple[tuple[str, str], ...]
    stratum_indices: tuple[np.ndarray, ...]
    da_counts: np.ndarray
    folios: tuple[str, ...]
    folio_index: np.ndarray
    folio_currier: tuple[str, ...]
    bases: tuple[str, ...]
    base_index: np.ndarray
    pairs: tuple[tuple[str, str], ...]
    pair_index: np.ndarray
    pair_base_index: np.ndarray
    eligible: np.ndarray


def stable64(text: str) -> int:
    return int.from_bytes(hashlib.sha256(text.encode()).digest()[:8], "little")


def splitmix(values):
    mask = np.uint64(0xFFFFFFFFFFFFFFFF)
    z = (values + np.uint64(0x9E3779B97F4A7C15)) & mask
    z = ((z ^ (z >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)) & mask
    z = ((z ^ (z >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)) & mask
    return z ^ (z >> np.uint64(31))


def load_panel(panel_path: Path, quota_path: Path) -> OnsetPanel:
    with panel_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if tuple(reader.fieldnames or ()) != PANEL_FIELDS:
            raise ValueError("panel schema")
        rows = list(reader)
    with quota_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if tuple(reader.fieldnames or ()) != QUOTA_FIELDS:
            raise ValueError("quota schema")
        quota_rows = list(reader)
    if len(rows) != 1207 or len({row["unit_id"] for row in rows}) != 1207:
        raise ValueError("panel identity")
    quotas = {(row["base_id"], row["physical_folio"]): (int(row["none_count"]), int(row["da_count"]), int(row["total_count"])) for row in quota_rows}
    if len(quotas) != 1763:
        raise ValueError("quota identity")
    grouped = {}
    for index, row in enumerate(rows):
        grouped.setdefault((row["base_id"], row["physical_folio"]), []).append(index)
    mixed = tuple(sorted(key for key, values in quotas.items() if values[0] and values[1]))
    if len(mixed) != 197 or set(grouped) != set(mixed):
        raise ValueError("mixed identity")
    if any(len(grouped[key]) != quotas[key][2] or quotas[key][0] + quotas[key][1] != quotas[key][2] for key in mixed):
        raise ValueError("quota geometry")
    stratum_indices = tuple(np.asarray(grouped[key], dtype=np.int64) for key in mixed)
    da_counts = np.asarray([quotas[key][1] for key in mixed], dtype=np.int64)
    folios = tuple(sorted({row["physical_folio"] for row in rows}, key=lambda value: int(value[1:])))
    bases = tuple(sorted({row["base_id"] for row in rows}))
    pairs = tuple(sorted({(row["base_id"], row["onset_id"]) for row in rows}))
    if len(folios) != 59 or len(bases) != 44 or len(pairs) != 95:
        raise ValueError("category capacity")
    folio_map = {value: index for index, value in enumerate(folios)}
    base_map = {value: index for index, value in enumerate(bases)}
    pair_map = {value: index for index, value in enumerate(pairs)}
    folio_index = np.asarray([folio_map[row["physical_folio"]] for row in rows], dtype=np.int64)
    base_index = np.asarray([base_map[row["base_id"]] for row in rows], dtype=np.int64)
    pair_index = np.asarray([pair_map[(row["base_id"], row["onset_id"])] for row in rows], dtype=np.int64)
    pair_base_index = np.asarray([base_map[base] for base, _ in pairs], dtype=np.int64)
    pair_folios = {pair: {row["physical_folio"] for row in rows if (row["base_id"], row["onset_id"]) == pair} for pair in pairs}
    eligible = np.asarray([len(pair_folios[(row["base_id"], row["onset_id"])]) >= 2 for row in rows], dtype=bool)
    if int(eligible.sum()) != 1141 or len({row["physical_folio"] for row, keep in zip(rows, eligible) if keep}) != 59:
        raise ValueError("held coverage")
    folio_currier = []
    for value in folios:
        registers = {row["currier"] for row in rows if row["physical_folio"] == value}
        if len(registers) != 1 or not registers <= {"A", "B"}:
            raise ValueError("folio register")
        folio_currier.append(next(iter(registers)))
    return OnsetPanel(rows, mixed, stratum_indices, da_counts, folios, folio_index, tuple(folio_currier), bases, base_index, pairs, pair_index, pair_base_index, eligible)


def quota_labels(panel: OnsetPanel, assignments: int, domain: str):
    if assignments < 128 or assignments > 8192:
        raise ValueError("assignments")
    output = np.zeros((assignments, len(panel.rows)), dtype=np.float64)
    clock = np.arange(assignments, dtype=np.uint64)[:, None] * np.uint64(0xD1342543DE82EF95)
    for key, indices, count in zip(panel.strata, panel.stratum_indices, panel.da_counts):
        seeds = np.asarray([stable64(f"SNOONSET1|{domain}|{key[0]}|{key[1]}|{panel.rows[index]['unit_id']}") for index in indices], dtype=np.uint64)
        ranks = splitmix(clock ^ seeds[None, :])
        selected = np.argpartition(ranks, len(indices) - int(count), axis=1)[:, -int(count):]
        output[np.arange(assignments)[:, None], indices[selected]] = 1.0
    return output


def planted_labels(panel: OnsetPanel, mode: str, world: int, strength: float = 0.80):
    if mode not in {"NULL", "GLOBAL_ONSET", "ONE_FOLIO", "FOLIO_RANDOM", "ONE_BASE"}:
        raise ValueError("mode")
    active_folio = world % len(panel.folios)
    active_base = world % len(panel.bases)
    signal = np.zeros(len(panel.rows), dtype=np.float64)
    noise = np.empty(len(panel.rows), dtype=np.float64)
    for index, row in enumerate(panel.rows):
        noise[index] = ((stable64(f"SNOONSET1|NOISE|{mode}|{world}|{row['unit_id']}") + 0.5) / (1 << 64)) * 2 - 1
        if mode == "GLOBAL_ONSET":
            domain = f"GLOBAL|{world}|{row['base_id']}|{row['onset_id']}"
        elif mode == "FOLIO_RANDOM":
            domain = f"FOLIO|{world}|{row['physical_folio']}|{row['base_id']}|{row['onset_id']}"
        elif mode == "ONE_FOLIO" and panel.folio_index[index] == active_folio:
            domain = f"GLOBAL|{world}|{row['base_id']}|{row['onset_id']}"
        elif mode == "ONE_BASE" and panel.base_index[index] == active_base:
            domain = f"GLOBAL|{world}|{row['base_id']}|{row['onset_id']}"
        else:
            continue
        signal[index] = ((stable64("SNOONSET1|SIGNAL|" + domain) + 0.5) / (1 << 64)) * 2 - 1
    ranking = strength * signal + (1.0 - strength) * noise if mode != "NULL" else noise
    labels = np.zeros(len(panel.rows), dtype=np.float64)
    for indices, count in zip(panel.stratum_indices, panel.da_counts):
        order = np.argsort(ranking[indices], kind="mergesort")
        labels[indices[order[-int(count):]]] = 1.0
    return labels


def category_counts(labels, categories, category_count):
    result = np.zeros((len(labels), category_count), dtype=np.float64)
    for category in range(category_count):
        result[:, category] = labels[:, categories == category].sum(axis=1)
    return result


def score_assignments(panel: OnsetPanel, labels):
    labels = np.asarray(labels, dtype=np.float64)
    if labels.ndim != 2 or labels.shape[1] != len(panel.rows) or not np.isfinite(labels).all() or not np.isin(labels, (0.0, 1.0)).all():
        raise ValueError("labels")
    for indices, count in zip(panel.stratum_indices, panel.da_counts):
        if not np.all(labels[:, indices].sum(axis=1) == count):
            raise ValueError("quota labels")
    base_total_n = np.bincount(panel.base_index, minlength=len(panel.bases)).astype(np.float64)
    pair_total_n = np.bincount(panel.pair_index, minlength=len(panel.pairs)).astype(np.float64)
    base_total_d = category_counts(labels, panel.base_index, len(panel.bases))
    pair_total_d = category_counts(labels, panel.pair_index, len(panel.pairs))
    folio_scores = np.zeros((len(labels), len(panel.folios)), dtype=np.float64)
    for held in range(len(panel.folios)):
        held_mask = panel.folio_index == held
        score_mask = held_mask & panel.eligible
        if not score_mask.any():
            raise ValueError("empty held fold")
        base_held_n = np.bincount(panel.base_index[held_mask], minlength=len(panel.bases)).astype(np.float64)
        pair_held_n = np.bincount(panel.pair_index[held_mask], minlength=len(panel.pairs)).astype(np.float64)
        base_train_n = base_total_n - base_held_n
        pair_train_n = pair_total_n - pair_held_n
        base_held_d = category_counts(labels[:, held_mask], panel.base_index[held_mask], len(panel.bases))
        pair_held_d = category_counts(labels[:, held_mask], panel.pair_index[held_mask], len(panel.pairs))
        base_probability = (base_total_d - base_held_d + 0.5) / (base_train_n[None, :] + 1.0)
        pair_probability = (pair_total_d - pair_held_d + 4.0 * base_probability[:, panel.pair_base_index]) / (pair_train_n[None, :] + 4.0)
        y = labels[:, score_mask]
        p0 = base_probability[:, panel.base_index[score_mask]]
        p1 = pair_probability[:, panel.pair_index[score_mask]]
        gains = y * np.log(p1 / p0) + (1.0 - y) * np.log((1.0 - p1) / (1.0 - p0))
        folio_scores[:, held] = gains.mean(axis=1)
    if not np.isfinite(folio_scores).all():
        raise ValueError("finite scores")
    return folio_scores.mean(axis=1), folio_scores


def summarize(panel: OnsetPanel, observed_labels, null_labels):
    observed_labels = np.asarray(observed_labels, dtype=np.float64)
    null_labels = np.asarray(null_labels, dtype=np.float64)
    observed_count = len(observed_labels)
    combined = np.vstack((observed_labels, null_labels[1:]))
    statistics, folio_scores = score_assignments(panel, combined)
    null = statistics[observed_count:]
    null_mean = float(null.mean())
    null_sd = float(null.std())
    currier = np.asarray(panel.folio_currier)
    results = []
    for index in range(observed_count):
        values = folio_scores[index]
        observed = float(statistics[index])
        denominator = float(np.abs(values).sum())
        deletions = (values.sum() - values) / (len(values) - 1)
        tail = int(np.sum(null >= observed))
        results.append({
            "observed": observed,
            "null_mean": null_mean,
            "null_sd": null_sd,
            "upper_p": (1 + tail) / (1 + len(null)),
            "z": (observed - null_mean) / null_sd if null_sd else 0.0,
            "positive_folios": int(np.sum(values > 0)),
            "max_abs_contribution_fraction": float(np.max(np.abs(values)) / denominator) if denominator else 1.0,
            "minimum_deletion_mean": float(deletions.min()),
            "currier_A_mean": float(values[currier == "A"].mean()),
            "currier_B_mean": float(values[currier == "B"].mean()),
        })
    return results


def passes(summary, p_limit):
    return summary["upper_p"] <= p_limit and summary["z"] >= 3.0 and summary["observed"] >= 0.01 and summary["positive_folios"] >= 36 and summary["max_abs_contribution_fraction"] <= 0.15 and summary["minimum_deletion_mean"] > 0 and min(summary["currier_A_mean"], summary["currier_B_mean"]) >= 0.005
