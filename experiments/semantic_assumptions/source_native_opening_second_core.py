#!/usr/bin/env python3
"""Core scoring for the incremental second-member opening test."""

from __future__ import annotations

import csv
import hashlib
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np


FIELDS = ("unit_id", "base_id", "physical_folio", "currier", "onset_id", "onset_consensus", "second_id", "second_consensus", "second_eligible")


@dataclass
class Panel:
    rows: list[dict]
    cell_keys: tuple[tuple[str, str], ...]
    cell_rows: tuple[np.ndarray, ...]
    da_counts: np.ndarray
    folios: tuple[str, ...]
    folio_index: np.ndarray
    target_folios: tuple[str, ...]
    target_folio_index: np.ndarray
    target_currier: np.ndarray
    baselines: tuple[tuple[str, str], ...]
    baseline_index: np.ndarray
    refinements: tuple[tuple[str, str, str], ...]
    refinement_index: np.ndarray
    refinement_baseline: np.ndarray
    eligible: np.ndarray
    target_bases: tuple[str, ...]
    eligible_base_index: np.ndarray


def stable(text: str) -> int:
    return int.from_bytes(hashlib.sha256(text.encode()).digest()[:8], "little")


def mix64(values: np.ndarray) -> np.ndarray:
    mask = np.uint64(0xFFFFFFFFFFFFFFFF)
    x = (values + np.uint64(0x9E3779B97F4A7C15)) & mask
    x = ((x ^ (x >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)) & mask
    x = ((x ^ (x >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)) & mask
    return x ^ (x >> np.uint64(31))


def load_panel(panel_path: Path, quota_path: Path) -> Panel:
    with panel_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    with quota_path.open(encoding="utf-8", newline="") as handle:
        quota_rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 1207 or len({row["unit_id"] for row in rows}) != 1207 or any(tuple(row) != FIELDS for row in rows):
        raise ValueError("panel identity")
    quota = {(row["base_id"], row["physical_folio"]): (int(row["da_count"]), int(row["total_count"])) for row in quota_rows if int(row["none_count"]) and int(row["da_count"])}
    grouped: dict[tuple[str, str], list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        grouped[(row["base_id"], row["physical_folio"])].append(index)
    if len(quota_rows) != 1763 or len(quota) != 197 or set(grouped) != set(quota):
        raise ValueError("quota geometry")
    cell_keys = tuple(sorted(grouped))
    cell_rows = tuple(np.asarray(grouped[key], dtype=np.int64) for key in cell_keys)
    da_counts = np.asarray([quota[key][0] for key in cell_keys], dtype=np.int64)
    if any(len(indices) != quota[key][1] for key, indices in zip(cell_keys, cell_rows)):
        raise ValueError("quota size")
    baseline_seconds: dict[tuple[str, str], set[str]] = defaultdict(set)
    refinement_folios: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    for row in rows:
        if row["second_id"] != "NA":
            baseline = row["base_id"], row["onset_id"]
            baseline_seconds[baseline].add(row["second_id"])
            refinement_folios[(*baseline, row["second_id"])].add(row["physical_folio"])
    preliminary = {
        index for index, row in enumerate(rows)
        if row["second_id"] != "NA"
        and len(baseline_seconds[(row["base_id"], row["onset_id"])]) >= 2
        and len(refinement_folios[(row["base_id"], row["onset_id"], row["second_id"])]) >= 2
    }
    folio_preliminary = Counter(rows[index]["physical_folio"] for index in preliminary)
    reconstructed = {index for index in preliminary if folio_preliminary[rows[index]["physical_folio"]] >= 3}
    declared = {index for index, row in enumerate(rows) if row["second_eligible"] == "1"}
    if reconstructed != declared or any(row["second_eligible"] not in {"0", "1"} for row in rows):
        raise ValueError("eligibility drift")
    folios = tuple(sorted({row["physical_folio"] for row in rows}, key=lambda value: int(value[1:])))
    fmap = {value: index for index, value in enumerate(folios)}
    folio_index = np.asarray([fmap[row["physical_folio"]] for row in rows], dtype=np.int64)
    target_folios = tuple(sorted({rows[index]["physical_folio"] for index in declared}, key=lambda value: int(value[1:])))
    tfmap = {value: index for index, value in enumerate(target_folios)}
    target_folio_index = np.asarray([tfmap.get(row["physical_folio"], -1) for row in rows], dtype=np.int64)
    target_currier = []
    for folio in target_folios:
        values = {row["currier"] for row in rows if row["physical_folio"] == folio}
        if len(values) != 1 or not values <= {"A", "B"}:
            raise ValueError("folio register")
        target_currier.append(next(iter(values)))
    baselines = tuple(sorted({(row["base_id"], row["onset_id"]) for row in rows}))
    bmap = {value: index for index, value in enumerate(baselines)}
    baseline_index = np.asarray([bmap[(row["base_id"], row["onset_id"])] for row in rows], dtype=np.int64)
    refinements = tuple(sorted({(row["base_id"], row["onset_id"], row["second_id"]) for row in rows if row["second_id"] != "NA"}))
    rmap = {value: index for index, value in enumerate(refinements)}
    refinement_index = np.asarray([rmap.get((row["base_id"], row["onset_id"], row["second_id"]), -1) for row in rows], dtype=np.int64)
    refinement_baseline = np.asarray([bmap[(base, onset)] for base, onset, _ in refinements], dtype=np.int64)
    eligible = np.asarray([index in declared for index in range(len(rows))], dtype=bool)
    target_bases = tuple(sorted({rows[index]["base_id"] for index in declared}))
    ebmap = {value: index for index, value in enumerate(target_bases)}
    eligible_base_index = np.asarray([ebmap.get(row["base_id"], -1) for row in rows], dtype=np.int64)
    if (int(eligible.sum()), len(target_folios), len(target_bases), len({baseline_index[index] for index in declared}), len({refinement_index[index] for index in declared}), len({rows[index]["second_id"] for index in declared})) != (639, 41, 16, 26, 40, 13):
        raise ValueError("capacity")
    return Panel(rows, cell_keys, cell_rows, da_counts, folios, folio_index, target_folios, target_folio_index, np.asarray(target_currier), baselines, baseline_index, refinements, refinement_index, refinement_baseline, eligible, target_bases, eligible_base_index)


def quota_labels(panel: Panel, assignments: int, domain: str) -> np.ndarray:
    output = np.zeros((assignments, len(panel.rows)), dtype=np.float64)
    clock = np.arange(assignments, dtype=np.uint64)[:, None] * np.uint64(0xD1342543DE82EF95)
    for key, indices, count in zip(panel.cell_keys, panel.cell_rows, panel.da_counts):
        seed = np.asarray([stable(f"SNOSECOND1|{domain}|{key[0]}|{key[1]}|{panel.rows[int(index)]['unit_id']}") for index in indices], dtype=np.uint64)
        rank = mix64(clock ^ seed[None, :])
        chosen = np.argpartition(rank, len(indices) - int(count), axis=1)[:, -int(count):]
        output[np.arange(assignments)[:, None], indices[chosen]] = 1.0
    return output


def plant(panel: Panel, mode: str, world: int, strength: float = .80) -> np.ndarray:
    if mode not in {"NULL", "GLOBAL_SECOND", "BASELINE_ONLY", "ONE_FOLIO", "FOLIO_RANDOM", "ONE_BASE"}:
        raise ValueError("mode")
    active_folio = panel.target_folios[world % len(panel.target_folios)]
    active_base = panel.target_bases[world % len(panel.target_bases)]
    rank = np.empty(len(panel.rows), dtype=np.float64)
    for index, row in enumerate(panel.rows):
        noise = ((stable(f"SNOSECOND1|NOISE|{mode}|{world}|{row['unit_id']}") + .5) / (1 << 64)) * 2 - 1
        signal = 0.0
        if mode == "GLOBAL_SECOND" and row["second_id"] != "NA":
            key = f"SECOND|{world}|{row['base_id']}|{row['onset_id']}|{row['second_id']}"
        elif mode == "BASELINE_ONLY":
            key = f"BASELINE|{world}|{row['base_id']}|{row['onset_id']}"
        elif mode == "ONE_FOLIO" and row["physical_folio"] == active_folio and row["second_id"] != "NA":
            key = f"SECOND|{world}|{row['base_id']}|{row['onset_id']}|{row['second_id']}"
        elif mode == "FOLIO_RANDOM" and row["second_id"] != "NA":
            key = f"FOLIO|{world}|{row['physical_folio']}|{row['base_id']}|{row['onset_id']}|{row['second_id']}"
        elif mode == "ONE_BASE" and row["base_id"] == active_base and row["second_id"] != "NA":
            key = f"SECOND|{world}|{row['base_id']}|{row['onset_id']}|{row['second_id']}"
        else:
            key = None
        if key is not None:
            signal = ((stable("SNOSECOND1|SIGNAL|" + key) + .5) / (1 << 64)) * 2 - 1
        rank[index] = noise if mode == "NULL" else strength * signal + (1 - strength) * noise
    output = np.zeros(len(panel.rows), dtype=np.float64)
    for indices, count in zip(panel.cell_rows, panel.da_counts):
        order = np.argsort(rank[indices], kind="mergesort")
        output[indices[order[-int(count):]]] = 1.0
    return output


def category_counts(labels: np.ndarray, index: np.ndarray, size: int) -> np.ndarray:
    output = np.zeros((len(labels), size), dtype=np.float64)
    for value in range(size):
        output[:, value] = labels[:, index == value].sum(axis=1)
    return output


def score(panel: Panel, labels: np.ndarray) -> dict[str, np.ndarray]:
    labels = np.asarray(labels, dtype=np.float64)
    if labels.ndim != 2 or labels.shape[1] != len(panel.rows) or not np.isfinite(labels).all() or not np.isin(labels, (0., 1.)).all():
        raise ValueError("labels")
    for indices, count in zip(panel.cell_rows, panel.da_counts):
        if not np.all(labels[:, indices].sum(axis=1) == count):
            raise ValueError("quota")
    baseline_n = np.bincount(panel.baseline_index, minlength=len(panel.baselines)).astype(np.float64)
    refinement_n = np.bincount(panel.refinement_index[panel.refinement_index >= 0], minlength=len(panel.refinements)).astype(np.float64)
    baseline_d = category_counts(labels, panel.baseline_index, len(panel.baselines))
    refinement_d = category_counts(labels[:, panel.refinement_index >= 0], panel.refinement_index[panel.refinement_index >= 0], len(panel.refinements))
    folio_scores = np.empty((len(labels), len(panel.target_folios)), dtype=np.float64)
    row_scores = np.empty((len(labels), int(panel.eligible.sum())), dtype=np.float64)
    eligible_indices = np.flatnonzero(panel.eligible)
    eligible_position = {int(value): index for index, value in enumerate(eligible_indices)}
    for held, folio in enumerate(panel.target_folios):
        held_mask = panel.folio_index == panel.folios.index(folio)
        test = panel.eligible & held_mask
        held_baseline_n = np.bincount(panel.baseline_index[held_mask], minlength=len(panel.baselines)).astype(np.float64)
        held_refinement_mask = held_mask & (panel.refinement_index >= 0)
        held_refinement_n = np.bincount(panel.refinement_index[held_refinement_mask], minlength=len(panel.refinements)).astype(np.float64)
        held_baseline_d = category_counts(labels[:, held_mask], panel.baseline_index[held_mask], len(panel.baselines))
        held_refinement_d = category_counts(labels[:, held_refinement_mask], panel.refinement_index[held_refinement_mask], len(panel.refinements))
        p0 = (baseline_d - held_baseline_d + .5) / (baseline_n[None, :] - held_baseline_n[None, :] + 1.)
        p1 = (refinement_d - held_refinement_d + 4. * p0[:, panel.refinement_baseline]) / (refinement_n[None, :] - held_refinement_n[None, :] + 4.)
        target = np.flatnonzero(test)
        y = labels[:, target]
        baseline = p0[:, panel.baseline_index[target]]
        refined = p1[:, panel.refinement_index[target]]
        gain = y * np.log(refined / baseline) + (1 - y) * np.log((1 - refined) / (1 - baseline))
        folio_scores[:, held] = gain.mean(axis=1)
        row_scores[:, [eligible_position[int(value)] for value in target]] = gain
    base_scores = np.empty((len(labels), len(panel.target_bases)), dtype=np.float64)
    eligible_base = panel.eligible_base_index[eligible_indices]
    for value in range(len(panel.target_bases)):
        base_scores[:, value] = row_scores[:, eligible_base == value].mean(axis=1)
    if not np.isfinite(folio_scores).all() or not np.isfinite(base_scores).all():
        raise ValueError("finite")
    return {"primary": folio_scores.mean(axis=1), "folio_scores": folio_scores, "base_scores": base_scores}


def summaries(panel: Panel, observed: np.ndarray, null: np.ndarray) -> list[dict]:
    values = score(panel, np.vstack((observed, null[1:])))
    count = len(observed)
    reference = values["primary"][count:]
    mean, sd = float(reference.mean()), float(reference.std())
    output = []
    for index in range(count):
        primary, folios, bases = float(values["primary"][index]), values["folio_scores"][index], values["base_scores"][index]
        output.append({
            "observed": primary, "null_mean": mean, "null_sd": sd,
            "upper_p": (1 + int(np.sum(reference >= primary))) / (1 + len(reference)),
            "z": (primary - mean) / sd if sd else 0.,
            "positive_folios": int(np.sum(folios > 0)),
            "max_abs_folio_fraction": float(np.max(np.abs(folios)) / np.abs(folios).sum()) if np.abs(folios).sum() else 1.,
            "minimum_folio_deletion_mean": float(((folios.sum() - folios) / 40).min()),
            "currier_A_mean": float(folios[panel.target_currier == "A"].mean()),
            "currier_B_mean": float(folios[panel.target_currier == "B"].mean()),
            "positive_bases": int(np.sum(bases > 0)),
            "max_abs_base_fraction": float(np.max(np.abs(bases)) / np.abs(bases).sum()) if np.abs(bases).sum() else 1.,
            "minimum_base_deletion_mean": float(((bases.sum() - bases) / 15).min()),
        })
    return output


def passes(row: dict, alpha: float) -> bool:
    return row["upper_p"] <= alpha and row["z"] >= 3 and row["observed"] >= .01 and row["positive_folios"] >= 28 and row["max_abs_folio_fraction"] <= .15 and row["minimum_folio_deletion_mean"] > 0 and min(row["currier_A_mean"], row["currier_B_mean"]) >= .005 and row["positive_bases"] >= 10 and row["max_abs_base_fraction"] <= .25 and row["minimum_base_deletion_mean"] > 0


def digest(array: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(array, dtype="<f8").tobytes()).hexdigest()
