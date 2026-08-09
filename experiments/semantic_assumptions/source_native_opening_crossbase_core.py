#!/usr/bin/env python3
"""Core scoring for cross-base opening-member transfer."""

from __future__ import annotations

import csv
import hashlib
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np


EXPECTED_FIELDS = (
    "unit_id", "base_id", "physical_folio", "currier", "onset_id",
    "onset_consensus", "onset_family_id", "crossbase_eligible",
)


@dataclass
class Panel:
    rows: list[dict]
    cell_keys: tuple[tuple[str, str], ...]
    cell_rows: tuple[np.ndarray, ...]
    da_counts: np.ndarray
    quota_by_row: np.ndarray
    base_by_row: np.ndarray
    folio_by_row: np.ndarray
    onset_by_row: np.ndarray
    family_by_row: np.ndarray
    eligible: np.ndarray
    target_cells: tuple[int, ...]
    target_rows: tuple[np.ndarray, ...]
    target_bases: tuple[str, ...]
    target_base_index: np.ndarray
    target_currier: np.ndarray
    target_families: tuple[str, ...]
    target_family_index: np.ndarray


def stable(text: str) -> int:
    return int.from_bytes(hashlib.sha256(text.encode()).digest()[:8], "little")


def mix64(values: np.ndarray) -> np.ndarray:
    mask = np.uint64(0xFFFFFFFFFFFFFFFF)
    answer = (values + np.uint64(0x9E3779B97F4A7C15)) & mask
    answer = ((answer ^ (answer >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)) & mask
    answer = ((answer ^ (answer >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)) & mask
    return answer ^ (answer >> np.uint64(31))


def load_panel(panel_path: Path, quota_path: Path) -> Panel:
    with panel_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    with quota_path.open(encoding="utf-8", newline="") as handle:
        quota_rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 1207 or len({row["unit_id"] for row in rows}) != 1207 or any(tuple(row) != EXPECTED_FIELDS for row in rows):
        raise ValueError("panel identity")
    if any(row["crossbase_eligible"] not in {"0", "1"} or row["onset_consensus"] not in {"0", "1"} for row in rows):
        raise ValueError("binary metadata")
    quota = {
        (row["base_id"], row["physical_folio"]):
        (int(row["da_count"]), int(row["total_count"]))
        for row in quota_rows if int(row["none_count"]) and int(row["da_count"])
    }
    grouped: dict[tuple[str, str], list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        grouped[(row["base_id"], row["physical_folio"])].append(index)
    if len(quota_rows) != 1763 or len(quota) != 197 or set(grouped) != set(quota):
        raise ValueError("quota identity")
    cell_keys = tuple(sorted(grouped))
    cell_rows = tuple(np.asarray(grouped[key], dtype=np.int64) for key in cell_keys)
    da_counts = np.asarray([quota[key][0] for key in cell_keys], dtype=np.int64)
    if any(len(indices) != quota[key][1] for key, indices in zip(cell_keys, cell_rows)):
        raise ValueError("quota size")
    q = np.empty(len(rows), dtype=np.float64)
    for key, indices in zip(cell_keys, cell_rows):
        q[indices] = quota[key][0] / quota[key][1]
    bases = tuple(sorted({row["base_id"] for row in rows}))
    folios = tuple(sorted({row["physical_folio"] for row in rows}, key=lambda value: int(value[1:])))
    onsets = tuple(sorted({row["onset_id"] for row in rows}))
    families = tuple(sorted({row["onset_family_id"] for row in rows}))
    bmap = {value: index for index, value in enumerate(bases)}
    fmap = {value: index for index, value in enumerate(folios)}
    omap = {value: index for index, value in enumerate(onsets)}
    fammap = {value: index for index, value in enumerate(families)}
    base_by_row = np.asarray([bmap[row["base_id"]] for row in rows], dtype=np.int64)
    folio_by_row = np.asarray([fmap[row["physical_folio"]] for row in rows], dtype=np.int64)
    onset_by_row = np.asarray([omap[row["onset_id"]] for row in rows], dtype=np.int64)
    family_by_row = np.asarray([fammap[row["onset_family_id"]] for row in rows], dtype=np.int64)
    eligible = np.asarray([row["crossbase_eligible"] == "1" for row in rows], dtype=bool)
    base_folios: dict[str, set[str]] = defaultdict(set)
    onset_locations: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for row in rows:
        base_folios[row["base_id"]].add(row["physical_folio"])
        onset_locations[row["onset_id"]].add((row["base_id"], row["physical_folio"]))
    preliminary: set[int] = set()
    for index, row in enumerate(rows):
        base, folio, onset = row["base_id"], row["physical_folio"], row["onset_id"]
        other_bases = {candidate_base for candidate_base, candidate_folio in onset_locations[onset] if candidate_base != base and candidate_folio != folio}
        if base_folios[base] - {folio} and len(other_bases) >= 2:
            preliminary.add(index)
    reconstructed: set[int] = set()
    for indices in cell_rows:
        candidates = [int(index) for index in indices if int(index) in preliminary]
        if len({rows[index]["onset_id"] for index in candidates}) >= 2:
            reconstructed.update(candidates)
    if set(np.flatnonzero(eligible)) != reconstructed:
        raise ValueError("eligibility drift")
    target_cells = tuple(index for index, indices in enumerate(cell_rows) if eligible[indices].any())
    target_rows = tuple(indices[eligible[indices]] for index, indices in enumerate(cell_rows) if index in target_cells)
    target_base_values = tuple(sorted({cell_keys[index][0] for index in target_cells}))
    target_family_values = tuple(sorted({rows[int(indices[0])]["onset_family_id"] for indices in target_rows}))
    tbmap = {value: index for index, value in enumerate(target_base_values)}
    tfmap = {value: index for index, value in enumerate(target_family_values)}
    target_base_index = np.asarray([tbmap[cell_keys[index][0]] for index in target_cells], dtype=np.int64)
    target_currier = np.asarray([rows[int(indices[0])]["currier"] for indices in target_rows])
    target_family_index = np.empty(len(target_cells), dtype=np.int64)
    for output_index, indices in enumerate(target_rows):
        values = {rows[int(index)]["onset_family_id"] for index in indices}
        curriers = {rows[int(index)]["currier"] for index in cell_rows[target_cells[output_index]]}
        if len(values) != 1 or len(curriers) != 1:
            raise ValueError("target cell metadata")
        target_family_index[output_index] = tfmap[next(iter(values))]
    if (int(eligible.sum()), len(target_cells), len(target_base_values), len({folios[folio_by_row[index]] for index in np.flatnonzero(eligible)}), len({onsets[onset_by_row[index]] for index in np.flatnonzero(eligible)}), len(target_family_values)) != (658, 101, 24, 41, 14, 6):
        raise ValueError("target capacity")
    return Panel(rows, cell_keys, cell_rows, da_counts, q, base_by_row, folio_by_row, onset_by_row, family_by_row, eligible, target_cells, target_rows, target_base_values, target_base_index, target_currier, target_family_values, target_family_index)


def quota_labels(panel: Panel, assignments: int, domain: str) -> np.ndarray:
    if assignments <= 0:
        raise ValueError("assignments")
    answer = np.zeros((assignments, len(panel.rows)), dtype=np.float64)
    clock = np.arange(assignments, dtype=np.uint64)[:, None] * np.uint64(0xD1342543DE82EF95)
    for key, indices, count in zip(panel.cell_keys, panel.cell_rows, panel.da_counts):
        seeds = np.asarray([stable(f"SNOCROSS1|{domain}|{key[0]}|{key[1]}|{panel.rows[int(index)]['unit_id']}") for index in indices], dtype=np.uint64)
        ranks = mix64(clock ^ seeds[None, :])
        chosen = np.argpartition(ranks, len(indices) - int(count), axis=1)[:, -int(count):]
        answer[np.arange(assignments)[:, None], indices[chosen]] = 1.0
    return answer


def plant(panel: Panel, mode: str, world: int, strength: float = 0.80) -> np.ndarray:
    if mode not in {"NULL", "GLOBAL_SHARED", "BASE_RANDOM", "FOLIO_RANDOM", "ONE_BASE", "ONE_FAMILY"} or not 0 <= strength <= 1:
        raise ValueError("plant mode")
    active_base = panel.target_bases[world % len(panel.target_bases)]
    active_family = panel.target_families[world % len(panel.target_families)]
    ranks = np.empty(len(panel.rows), dtype=np.float64)
    for index, row in enumerate(panel.rows):
        noise = ((stable(f"SNOCROSS1|NOISE|{mode}|{world}|{row['unit_id']}") + 0.5) / (1 << 64)) * 2 - 1
        signal = 0.0
        if mode == "GLOBAL_SHARED":
            key = f"GLOBAL|{world}|{row['onset_id']}"
        elif mode == "BASE_RANDOM":
            key = f"BASE|{world}|{row['base_id']}|{row['onset_id']}"
        elif mode == "FOLIO_RANDOM":
            key = f"FOLIO|{world}|{row['physical_folio']}|{row['onset_id']}"
        elif mode == "ONE_BASE" and row["base_id"] == active_base:
            key = f"GLOBAL|{world}|{row['onset_id']}"
        elif mode == "ONE_FAMILY" and row["onset_family_id"] == active_family:
            key = f"GLOBAL|{world}|{row['onset_id']}"
        else:
            key = None
        if key is not None:
            signal = ((stable("SNOCROSS1|SIGNAL|" + key) + 0.5) / (1 << 64)) * 2 - 1
        ranks[index] = noise if mode == "NULL" else strength * signal + (1 - strength) * noise
    output = np.zeros(len(panel.rows), dtype=np.float64)
    for indices, count in zip(panel.cell_rows, panel.da_counts):
        order = np.argsort(ranks[indices], kind="mergesort")
        output[indices[order[-int(count):]]] = 1.0
    return output


def score(panel: Panel, labels: np.ndarray) -> dict[str, np.ndarray]:
    labels = np.asarray(labels, dtype=np.float64)
    if labels.ndim != 2 or labels.shape[1] != len(panel.rows) or not np.isfinite(labels).all() or not np.isin(labels, (0.0, 1.0)).all():
        raise ValueError("labels")
    for indices, expected in zip(panel.cell_rows, panel.da_counts):
        if not np.all(labels[:, indices].sum(axis=1) == expected):
            raise ValueError("quota drift")
    residual = labels - panel.quota_by_row[None, :]
    cell_scores = np.empty((len(labels), len(panel.target_cells)), dtype=np.float64)
    for output_index, (cell_index, target_indices) in enumerate(zip(panel.target_cells, panel.target_rows)):
        target_base = panel.base_by_row[target_indices[0]]
        target_folio = panel.folio_by_row[target_indices[0]]
        training = (panel.base_by_row != target_base) & (panel.folio_by_row != target_folio)
        p0 = panel.quota_by_row[target_indices]
        gain = np.zeros((len(labels), len(target_indices)), dtype=np.float64)
        for onset in np.unique(panel.onset_by_row[target_indices]):
            train_indices = np.flatnonzero(training & (panel.onset_by_row == onset))
            if len(train_indices) == 0:
                raise ValueError("onset support")
            delta = residual[:, train_indices].sum(axis=1) / (len(train_indices) + 8.0)
            positions = np.flatnonzero(panel.onset_by_row[target_indices] == onset)
            p1 = np.clip(p0[positions][None, :] + delta[:, None], 1e-6, 1 - 1e-6)
            y = labels[:, target_indices[positions]]
            baseline = p0[positions][None, :]
            gain[:, positions] = y * np.log(p1 / baseline) + (1 - y) * np.log((1 - p1) / (1 - baseline))
        cell_scores[:, output_index] = gain.mean(axis=1)
    base_scores = np.empty((len(labels), len(panel.target_bases)), dtype=np.float64)
    for index in range(len(panel.target_bases)):
        base_scores[:, index] = cell_scores[:, panel.target_base_index == index].mean(axis=1)
    family_scores = np.empty((len(labels), len(panel.target_families)), dtype=np.float64)
    for index in range(len(panel.target_families)):
        family_scores[:, index] = cell_scores[:, panel.target_family_index == index].mean(axis=1)
    currier_A = cell_scores[:, panel.target_currier == "A"].mean(axis=1)
    currier_B = cell_scores[:, panel.target_currier == "B"].mean(axis=1)
    if not all(np.isfinite(value).all() for value in (cell_scores, base_scores, family_scores, currier_A, currier_B)):
        raise ValueError("nonfinite score")
    return {
        "primary": base_scores.mean(axis=1),
        "base_scores": base_scores,
        "family_scores": family_scores,
        "currier_A": currier_A,
        "currier_B": currier_B,
    }


def summaries(panel: Panel, observed: np.ndarray, null: np.ndarray) -> list[dict]:
    observed = np.asarray(observed, dtype=np.float64)
    combined = score(panel, np.vstack((observed, null[1:])))
    count = len(observed)
    reference = combined["primary"][count:]
    null_mean = float(reference.mean())
    null_sd = float(reference.std())
    output = []
    for index in range(count):
        primary = float(combined["primary"][index])
        bases = combined["base_scores"][index]
        families = combined["family_scores"][index]
        base_denominator = float(np.abs(bases).sum())
        family_denominator = float(np.abs(families).sum())
        output.append({
            "observed": primary,
            "null_mean": null_mean,
            "null_sd": null_sd,
            "upper_p": (1 + int(np.sum(reference >= primary))) / (1 + len(reference)),
            "z": (primary - null_mean) / null_sd if null_sd else 0.0,
            "positive_bases": int(np.sum(bases > 0)),
            "max_abs_base_fraction": float(np.max(np.abs(bases)) / base_denominator) if base_denominator else 1.0,
            "minimum_base_deletion_mean": float(((bases.sum() - bases) / (len(bases) - 1)).min()),
            "currier_A_mean": float(combined["currier_A"][index]),
            "currier_B_mean": float(combined["currier_B"][index]),
            "positive_families": int(np.sum(families > 0)),
            "max_abs_family_fraction": float(np.max(np.abs(families)) / family_denominator) if family_denominator else 1.0,
        })
    return output


def passes(row: dict, alpha: float) -> bool:
    return (
        row["upper_p"] <= alpha
        and row["z"] >= 3.0
        and row["observed"] >= 0.01
        and row["positive_bases"] >= 16
        and row["max_abs_base_fraction"] <= 0.15
        and row["minimum_base_deletion_mean"] > 0
        and min(row["currier_A_mean"], row["currier_B_mean"]) >= 0.005
        and row["positive_families"] >= 4
        and row["max_abs_family_fraction"] <= 0.45
    )


def digest(array: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(array, dtype="<f8").tobytes()).hexdigest()
