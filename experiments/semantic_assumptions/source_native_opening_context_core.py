#!/usr/bin/env python3
"""Target-free stratified context-concordance engine for NONE/DA geometry."""

from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass
from pathlib import Path

import numpy as np


PANEL_FIELDS = ("unit_id", "base_id", "physical_folio", "section", "currier", "kind", "group_count", "locus_role", "left_context", "right_context")
QUOTA_FIELDS = ("base_id", "physical_folio", "none_count", "da_count", "total_count")


@dataclass
class ContextPanel:
    rows: list[dict]
    strata: tuple[tuple[str, str], ...]
    stratum_indices: tuple[np.ndarray, ...]
    da_counts: np.ndarray
    row_probabilities: np.ndarray
    folios: tuple[str, ...]
    folio_index: np.ndarray
    folio_currier: tuple[str, ...]
    base_ids: tuple[str, ...]
    base_index: np.ndarray
    position: np.ndarray
    neighbor: np.ndarray
    position_names: tuple[str, ...]
    neighbor_names: tuple[str, ...]


def stable64(text: str) -> int:
    return int.from_bytes(hashlib.sha256(text.encode()).digest()[:8], "little")


def splitmix(values):
    mask = np.uint64(0xFFFFFFFFFFFFFFFF)
    z = (values + np.uint64(0x9E3779B97F4A7C15)) & mask
    z = ((z ^ (z >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)) & mask
    z = ((z ^ (z >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)) & mask
    return z ^ (z >> np.uint64(31))


def one_hot(values, names=None):
    names = tuple(sorted(set(values))) if names is None else tuple(names)
    index = {value: offset for offset, value in enumerate(names)}
    matrix = np.zeros((len(values), len(names)), dtype=np.float64)
    for row, value in enumerate(values):
        matrix[row, index[value]] = 1.0
    return matrix, names


def center_by_stratum(matrix, strata_indices):
    answer = matrix.astype(np.float64, copy=True)
    for indices in strata_indices:
        answer[indices] -= answer[indices].mean(axis=0, keepdims=True)
    return answer


def standardize(matrix, names):
    rms = np.sqrt(np.mean(matrix * matrix, axis=0))
    keep = rms > 1e-10
    return matrix[:, keep] / rms[keep], tuple(value for value, retained in zip(names, keep) if retained)


def load_panel(panel_path: Path, quota_path: Path) -> ContextPanel:
    with panel_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if tuple(reader.fieldnames or ()) != PANEL_FIELDS:
            raise ValueError("panel schema")
        all_rows = list(reader)
    with quota_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if tuple(reader.fieldnames or ()) != QUOTA_FIELDS:
            raise ValueError("quota schema")
        quota_rows = list(reader)
    if len(all_rows) != 5826 or len({row["unit_id"] for row in all_rows}) != 5826 or len({row["base_id"] for row in all_rows}) != 53:
        raise ValueError("panel identity")
    quotas = {(row["base_id"], row["physical_folio"]): (int(row["none_count"]), int(row["da_count"]), int(row["total_count"])) for row in quota_rows}
    if len(quotas) != 1763:
        raise ValueError("quota identity")
    grouped = {}
    for index, row in enumerate(all_rows):
        grouped.setdefault((row["base_id"], row["physical_folio"]), []).append(index)
    if set(grouped) != set(quotas) or any(len(grouped[key]) != quotas[key][2] or quotas[key][0] + quotas[key][1] != quotas[key][2] for key in quotas):
        raise ValueError("quota geometry")
    mixed_keys = tuple(sorted(key for key, value in quotas.items() if value[0] and value[1]))
    selected_old = [index for key in mixed_keys for index in grouped[key]]
    if len(mixed_keys) != 197 or len(selected_old) != 1207:
        raise ValueError("mobility")
    rows = [all_rows[index] for index in selected_old]
    old_to_new = {old: new for new, old in enumerate(selected_old)}
    stratum_indices = tuple(np.asarray([old_to_new[index] for index in grouped[key]], dtype=np.int64) for key in mixed_keys)
    da_counts = np.asarray([quotas[key][1] for key in mixed_keys], dtype=np.int64)
    row_probabilities = np.empty(len(rows), dtype=np.float64)
    for indices, count in zip(stratum_indices, da_counts):
        row_probabilities[indices] = count / len(indices)
    folios = tuple(sorted({row["physical_folio"] for row in rows}, key=lambda value: int(value[1:])))
    bases = tuple(sorted({row["base_id"] for row in rows}))
    folio_map = {value: index for index, value in enumerate(folios)}
    base_map = {value: index for index, value in enumerate(bases)}
    folio_index = np.asarray([folio_map[row["physical_folio"]] for row in rows], dtype=np.int64)
    base_index = np.asarray([base_map[row["base_id"]] for row in rows], dtype=np.int64)
    if len(folios) != 59 or len(bases) != 44:
        raise ValueError("informative support")
    folio_currier = []
    for value in folios:
        registers = {row["currier"] for row in rows if row["physical_folio"] == value}
        if len(registers) != 1 or not registers <= {"A", "B"}:
            raise ValueError("folio register")
        folio_currier.append(next(iter(registers)))
    position_raw, position_names = one_hot([row["locus_role"] for row in rows], ("FIRST", "LAST", "MIDDLE", "SINGLE"))
    count_raw, count_names = one_hot([row["group_count"] for row in rows])
    left_raw, left_names = one_hot([row["left_context"] for row in rows])
    right_raw, right_names = one_hot([row["right_context"] for row in rows])
    position_centered = center_by_stratum(position_raw, stratum_indices)
    position, position_names = standardize(position_centered, position_names)
    nuisance = center_by_stratum(np.column_stack((position_raw, count_raw)), stratum_indices)
    neighbor_raw = center_by_stratum(np.column_stack((left_raw, right_raw)), stratum_indices)
    if nuisance.shape[1]:
        neighbor_raw -= nuisance @ np.linalg.lstsq(nuisance, neighbor_raw, rcond=None)[0]
    neighbor_names = tuple("L:" + value for value in left_names) + tuple("R:" + value for value in right_names)
    neighbor, neighbor_names = standardize(neighbor_raw, neighbor_names)
    if not np.isfinite(position).all() or not np.isfinite(neighbor).all() or position.shape[1] < 2 or neighbor.shape[1] < 10:
        raise ValueError("feature geometry")
    return ContextPanel(rows, mixed_keys, stratum_indices, da_counts, row_probabilities, folios, folio_index, tuple(folio_currier), bases, base_index, position, neighbor, position_names, neighbor_names)


def null_orbit(panel: ContextPanel, assignments: int, domain: str):
    if assignments < 128 or assignments > 8192:
        raise ValueError("assignments")
    output = np.zeros((assignments, len(panel.rows)), dtype=np.float64)
    clock = np.arange(assignments, dtype=np.uint64)[:, None] * np.uint64(0xD1342543DE82EF95)
    for key, indices, count in zip(panel.strata, panel.stratum_indices, panel.da_counts):
        seeds = np.asarray([stable64(f"SNOCCTX1|{domain}|{key[0]}|{key[1]}|{panel.rows[index]['unit_id']}") for index in indices], dtype=np.uint64)
        ranks = splitmix(clock ^ seeds[None, :])
        selected = np.argpartition(ranks, len(indices) - int(count), axis=1)[:, -int(count):]
        row_numbers = np.arange(assignments)[:, None]
        output[row_numbers, indices[selected]] = 1.0
    return output


def hashed_weights(names, domain):
    return np.asarray([((stable64(f"SNOCCTX1|{domain}|{name}") + 0.5) / (1 << 64)) * 2.0 - 1.0 for name in names], dtype=np.float64)


def planted_labels(panel: ContextPanel, mode: str, world: int, strength: float = 0.82):
    if mode not in {"NULL", "POSITION", "NEIGHBOR", "ONE_FOLIO", "FOLIO_RANDOM", "ONE_BASE"}:
        raise ValueError("mode")
    noise = np.asarray([((stable64(f"SNOCCTX1|PLANT|{mode}|{world}|{row['unit_id']}") + 0.5) / (1 << 64)) * 2.0 - 1.0 for row in panel.rows])
    if mode == "NULL":
        signal = np.zeros(len(panel.rows), dtype=np.float64)
    elif mode == "POSITION":
        signal = panel.position @ hashed_weights(panel.position_names, f"POSITION|{world}")
    elif mode in {"NEIGHBOR", "ONE_FOLIO", "ONE_BASE"}:
        signal = panel.neighbor @ hashed_weights(panel.neighbor_names, f"NEIGHBOR|{world}")
        if mode == "ONE_FOLIO":
            signal *= panel.folio_index == (world % len(panel.folios))
        elif mode == "ONE_BASE":
            signal *= panel.base_index == (world % len(panel.base_ids))
    else:
        signal = np.empty(len(panel.rows), dtype=np.float64)
        for folio_index in range(len(panel.folios)):
            mask = panel.folio_index == folio_index
            signal[mask] = panel.neighbor[mask] @ hashed_weights(panel.neighbor_names, f"FOLIO_RANDOM|{world}|{folio_index}")
    scale = np.sqrt(np.mean(signal * signal))
    if scale > 0:
        signal = signal / scale
    ranking = strength * signal + (1.0 - strength) * noise
    labels = np.zeros(len(panel.rows), dtype=np.float64)
    for indices, count in zip(panel.stratum_indices, panel.da_counts):
        order = np.argsort(ranking[indices], kind="mergesort")
        labels[indices[order[-int(count):]]] = 1.0
    return labels


def score_orbit(panel: ContextPanel, feature_matrix, labels, xp=np):
    features = xp.asarray(feature_matrix, dtype=xp.float64)
    y = xp.asarray(labels, dtype=xp.float64) - xp.asarray(panel.row_probabilities, dtype=xp.float64)[None, :]
    folio_covariances = []
    for folio in range(len(panel.folios)):
        indices = np.flatnonzero(panel.folio_index == folio)
        folio_covariances.append((y[:, indices] @ features[indices]) / len(indices))
    covariances = xp.stack(folio_covariances, axis=1)
    total = covariances.sum(axis=1)
    squared_total = (total * total).sum(axis=1)
    squared_parts = (covariances * covariances).sum(axis=(1, 2))
    folio_count = len(panel.folios)
    statistic = (squared_total - squared_parts) / (folio_count * (folio_count - 1))
    return statistic, covariances


def pairwise_statistic(covariances, xp=np):
    count = covariances.shape[0]
    combined = covariances.sum(axis=0)
    return ((combined * combined).sum() - (covariances * covariances).sum()) / (count * (count - 1))


def currier_statistics(panel: ContextPanel, covariances, xp=np):
    result = {}
    labels = np.asarray(panel.folio_currier)
    for currier in ("A", "B"):
        result[currier] = pairwise_statistic(covariances[labels == currier], xp=xp)
    return result


def summarize(panel: ContextPanel, feature_matrix, labels, xp=np):
    statistic, covariances = score_orbit(panel, feature_matrix, labels, xp=xp)
    null = statistic[1:]
    observed = statistic[0]
    total = covariances[0].sum(axis=0)
    contributions = xp.asarray([(covariances[0, folio] * (total - covariances[0, folio]) / (len(panel.folios) - 1)).sum() for folio in range(len(panel.folios))])
    register = currier_statistics(panel, covariances[0], xp=xp)
    denominator = xp.abs(contributions).sum()
    deletions = []
    for folio in range(len(panel.folios)):
        kept = xp.concatenate((covariances[0, :folio], covariances[0, folio + 1:]), axis=0)
        count = kept.shape[0]
        combined = kept.sum(axis=0)
        deletions.append(((combined * combined).sum() - (kept * kept).sum()) / (count * (count - 1)))
    result = {
        "observed": float(observed.get() if hasattr(observed, "get") else observed),
        "null_mean": float(null.mean().get() if hasattr(null, "get") else null.mean()),
        "null_sd": float(null.std().get() if hasattr(null, "get") else null.std()),
        "upper_p": float((statistic >= observed).mean().get() if hasattr(statistic, "get") else np.mean(statistic >= observed)),
        "positive_folios": int((contributions > 0).sum().get() if hasattr(contributions, "get") else np.sum(contributions > 0)),
        "max_abs_contribution_fraction": float((xp.abs(contributions).max() / denominator).get() if hasattr(denominator, "get") and float(denominator.get()) else (np.max(np.abs(contributions)) / float(denominator) if float(denominator) else 1.0)),
        "minimum_deletion_statistic": float(xp.min(xp.asarray(deletions)).get() if hasattr(xp.asarray(deletions), "get") else np.min(deletions)),
        "currier_A_statistic": float(register["A"].get() if hasattr(register["A"], "get") else register["A"]),
        "currier_B_statistic": float(register["B"].get() if hasattr(register["B"], "get") else register["B"]),
    }
    result["z"] = (result["observed"] - result["null_mean"]) / result["null_sd"] if result["null_sd"] > 0 else 0.0
    return result


def summarize_batch(panel: ContextPanel, feature_matrix, observed_labels, null_labels, xp=np):
    observed_count = len(observed_labels)
    combined = np.vstack((observed_labels, null_labels[1:]))
    statistics, covariances = score_orbit(panel, feature_matrix, combined, xp=xp)
    null = statistics[observed_count:]
    null_mean = float(null.mean().get() if hasattr(null, "get") else null.mean())
    null_sd = float(null.std().get() if hasattr(null, "get") else null.std())
    results = []
    for observed_index in range(observed_count):
        observed = statistics[observed_index]
        observed_value = float(observed.get() if hasattr(observed, "get") else observed)
        current = covariances[observed_index]
        total = current.sum(axis=0)
        contributions = xp.stack([(current[folio] * (total - current[folio]) / (len(panel.folios) - 1)).sum() for folio in range(len(panel.folios))])
        register = currier_statistics(panel, current, xp=xp)
        denominator = xp.abs(contributions).sum()
        denominator_value = float(denominator.get() if hasattr(denominator, "get") else denominator)
        deletions = []
        for folio in range(len(panel.folios)):
            kept = xp.concatenate((current[:folio], current[folio + 1:]), axis=0)
            count = kept.shape[0]
            combined_covariance = kept.sum(axis=0)
            deletions.append(((combined_covariance * combined_covariance).sum() - (kept * kept).sum()) / (count * (count - 1)))
        tail_count = int((null >= observed).sum().get() if hasattr(null, "get") else np.sum(null >= observed))
        results.append({
            "observed": observed_value,
            "null_mean": null_mean,
            "null_sd": null_sd,
            "upper_p": (1 + tail_count) / (1 + len(null)),
            "positive_folios": int((contributions > 0).sum().get() if hasattr(contributions, "get") else np.sum(contributions > 0)),
            "max_abs_contribution_fraction": float((xp.abs(contributions).max() / denominator).get() if hasattr(denominator, "get") and denominator_value else (np.max(np.abs(contributions)) / denominator_value if denominator_value else 1.0)),
            "minimum_deletion_statistic": float(xp.min(xp.asarray(deletions)).get() if hasattr(xp.asarray(deletions), "get") else np.min(deletions)),
            "currier_A_statistic": float(register["A"].get() if hasattr(register["A"], "get") else register["A"]),
            "currier_B_statistic": float(register["B"].get() if hasattr(register["B"], "get") else register["B"]),
            "z": (observed_value - null_mean) / null_sd if null_sd > 0 else 0.0,
        })
    return results


def passes(summary, p_limit):
    return summary["upper_p"] <= p_limit and summary["z"] >= 3.0 and summary["positive_folios"] >= 35 and summary["max_abs_contribution_fraction"] <= 0.25 and summary["minimum_deletion_statistic"] > 0 and min(summary["currier_A_statistic"], summary["currier_B_statistic"]) >= 0.01
