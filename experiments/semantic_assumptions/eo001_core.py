#!/usr/bin/env python3
"""Core scorer for EO001 exact-form same-folio continuation concordance."""

from __future__ import annotations

import csv
import hashlib
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np


ALPHABET = tuple("ABCDEFGHJKLMNPQRSTUVWXYZ")
INDEX = {value: index for index, value in enumerate(ALPHABET)}
FORMS = ("AQKA", "BLJBA", "CAF", "CAG", "DAQKA", "DAQKBA", "LA", "QAC", "QKJBA")
STATES = ("FIRST", "CORE")
BLOCK_DIMS = {"EDGE_48": 48, "BAG_24": 24, "BIGRAM_576": 576}
FIELDS = (
    "anonymous_event_id", "trigger_family_surface", "trigger_state",
    "physical_folio", "section", "currier", "hand", "code", "kind",
    "trigger_group_index", "locus_group_count", "remaining_groups_after_trigger",
)
RIDGE = 1e-3
ASSIGNMENTS = 32768
TOL = 1e-12


@dataclass
class Panel:
    rows: list[dict[str, str]]
    forms: np.ndarray
    states: np.ndarray
    folios: np.ndarray
    curriers: np.ndarray
    design: np.ndarray
    informative: dict[str, tuple[int, ...]]
    permutations: dict[str, np.ndarray]


def load_panel(path: Path) -> Panel:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("EO001 panel schema drift")
        rows = list(reader)
    if len(rows) != 1295 or len({row["anonymous_event_id"] for row in rows}) != 1295:
        raise ValueError("EO001 panel identity drift")
    if tuple(sorted({row["trigger_family_surface"] for row in rows})) != FORMS:
        raise ValueError("EO001 form inventory drift")
    if Counter(row["trigger_state"] for row in rows) != {"FIRST": 316, "CORE": 979}:
        raise ValueError("EO001 state count drift")
    for row in rows:
        index, count, remaining = (int(row[key]) for key in ("trigger_group_index", "locus_group_count", "remaining_groups_after_trigger"))
        if remaining != count - index or remaining < 2:
            raise ValueError("EO001 successor-position geometry drift")
        if (row["trigger_state"] == "FIRST") != (index == 1):
            raise ValueError("EO001 trigger-state geometry drift")
        if row["kind"] != "P":
            raise ValueError("EO001 prose-kind drift")

    form_index = {value: index for index, value in enumerate(FORMS)}
    forms = np.asarray([form_index[row["trigger_family_surface"]] for row in rows], dtype=np.int64)
    states = np.asarray([0 if row["trigger_state"] == "FIRST" else 1 for row in rows], dtype=np.int8)
    folios = np.asarray([row["physical_folio"] for row in rows])
    curriers = np.asarray([row["currier"] for row in rows])
    design = nuisance_design(rows)

    informative: dict[str, tuple[int, ...]] = {}
    for folio in sorted(set(folios), key=lambda value: int(value[1:])):
        present = []
        for form in range(len(FORMS)):
            mask = (folios == folio) & (forms == form)
            if np.any(mask & (states == 0)) and np.any(mask & (states == 1)):
                present.append(form)
        if len(present) >= 2:
            informative[folio] = tuple(present)
    if len(informative) != 38 or sum(map(len, informative.values())) != 112:
        raise ValueError("EO001 informative-folio geometry drift")
    permutations = {folio: permutation_matrix(folio, present) for folio, present in informative.items()}
    return Panel(rows, forms, states, folios, curriers, design, informative, permutations)


def nuisance_design(rows: list[dict[str, str]]) -> np.ndarray:
    columns: list[np.ndarray] = [np.ones(len(rows), dtype=np.float64)]
    for field in ("currier", "section", "hand", "code"):
        values = sorted({row[field] for row in rows})
        for value in values:
            columns.append(np.asarray([float(row[field] == value) for row in rows]))
    count = np.asarray([float(row["locus_group_count"]) for row in rows])
    index = np.asarray([float(row["trigger_group_index"]) for row in rows])
    remaining = np.asarray([float(row["remaining_groups_after_trigger"]) for row in rows])
    numeric = (np.log1p(count), index / (count - 1.0), np.log1p(remaining))
    for base in numeric:
        columns.extend((base, base * base, base * base * base))
    design = np.column_stack(columns).astype(np.float64)
    for column in range(1, design.shape[1]):
        mean = float(design[:, column].mean())
        sd = float(design[:, column].std(ddof=0))
        if not np.isfinite(sd) or sd <= 0:
            raise ValueError("EO001 zero-variance nuisance column")
        design[:, column] = (design[:, column] - mean) / sd
    if design.shape != (1295, 32) or not np.isfinite(design).all():
        raise ValueError(f"EO001 nuisance design drift: {design.shape}")
    return design


def permutation_matrix(folio: str, present: tuple[int, ...], assignments: int = ASSIGNMENTS) -> np.ndarray:
    size = len(present)
    result = np.empty((assignments, size), dtype=np.int16)
    result[0] = np.arange(size, dtype=np.int16)
    names = [FORMS[index] for index in present]
    for assignment in range(1, assignments):
        order = sorted(
            range(size),
            key=lambda index: hashlib.sha256(
                f"EO001-PERM|{assignment}|{folio}|{names[index]}".encode()
            ).digest(),
        )
        result[assignment] = np.asarray(order, dtype=np.int16)
    return result


def fingerprint(sequence: str) -> dict[str, np.ndarray]:
    if not sequence or any(value not in INDEX for value in sequence):
        raise ValueError("EO001 invalid successor sequence")
    edge = np.zeros(48, dtype=np.float64)
    edge[INDEX[sequence[0]]] = 1.0
    edge[24 + INDEX[sequence[-1]]] = 1.0
    bag = np.zeros(24, dtype=np.float64)
    for value in sequence:
        bag[INDEX[value]] += 1.0 / len(sequence)
    bigram = np.zeros(576, dtype=np.float64)
    denominator = max(1, len(sequence) - 1)
    for left, right in zip(sequence, sequence[1:]):
        bigram[24 * INDEX[left] + INDEX[right]] += 1.0 / denominator
    return {"EDGE_48": edge, "BAG_24": bag, "BIGRAM_576": bigram}


def fingerprint_matrix(sequences: list[str]) -> dict[str, np.ndarray]:
    if len(sequences) != 1295:
        raise ValueError("EO001 successor sequence count drift")
    blocks = {name: np.empty((len(sequences), size), dtype=np.float64) for name, size in BLOCK_DIMS.items()}
    for row, sequence in enumerate(sequences):
        values = fingerprint(sequence)
        for name in blocks:
            blocks[name][row] = values[name]
    return blocks


def held_residuals(panel: Panel, response: np.ndarray) -> np.ndarray:
    if response.ndim != 2 or response.shape[0] != len(panel.rows) or not np.isfinite(response).all():
        raise ValueError("EO001 response geometry/nonfinite failure")
    residual = np.empty_like(response, dtype=np.float64)
    penalty = np.eye(panel.design.shape[1], dtype=np.float64) * RIDGE
    penalty[0, 0] = 0.0
    for state in (0, 1):
        state_mask = panel.states == state
        for folio in panel.informative:
            held = state_mask & (panel.folios == folio)
            if not np.any(held):
                continue
            train = state_mask & (panel.folios != folio)
            z_train, z_held = panel.design[train], panel.design[held]
            gram = z_train.T @ z_train + penalty
            beta = np.linalg.solve(gram, z_train.T @ response[train])
            residual[held] = response[held] - z_held @ beta
    used = np.isin(panel.folios, tuple(panel.informative))
    if not np.isfinite(residual[used]).all():
        raise ValueError("EO001 held residual nonfinite")
    return residual


def similarities(panel: Panel, response: np.ndarray) -> dict[str, np.ndarray]:
    residual = held_residuals(panel, response)
    result = {}
    for folio, present in panel.informative.items():
        vectors = []
        for state in (0, 1):
            means = []
            for form in present:
                mask = (panel.folios == folio) & (panel.states == state) & (panel.forms == form)
                means.append(residual[mask].mean(axis=0))
            matrix = np.asarray(means, dtype=np.float64)
            matrix -= matrix.mean(axis=0, keepdims=True)
            norms = np.linalg.norm(matrix, axis=1)
            matrix = np.divide(matrix, norms[:, None], out=np.zeros_like(matrix), where=norms[:, None] > 1e-15)
            vectors.append(matrix)
        result[folio] = vectors[0] @ vectors[1].T
    return result


def block_orbit(panel: Panel, response: np.ndarray) -> dict:
    sims = similarities(panel, response)
    orbit = np.zeros(ASSIGNMENTS, dtype=np.float64)
    folio_effects = {}
    form_values: dict[int, list[float]] = defaultdict(list)
    for folio, present in panel.informative.items():
        sim = sims[folio]
        perm = panel.permutations[folio]
        rows = np.arange(len(present), dtype=np.int64)[None, :]
        values = sim[rows, perm].mean(axis=1)
        orbit += values / len(panel.informative)
        diagonal = float(np.diag(sim).mean())
        wrong = float((sim.sum() - np.trace(sim)) / (len(present) * (len(present) - 1)))
        folio_effects[folio] = diagonal - wrong
        for local, form in enumerate(present):
            row_wrong = (sim[local].sum() - sim[local, local]) / (len(present) - 1)
            form_values[form].append(float(sim[local, local] - row_wrong))
    null = orbit[1:]
    mean, sd = float(null.mean()), float(null.std(ddof=0))
    if not np.isfinite(sd) or sd <= 0:
        raise ValueError("EO001 degenerate null orbit")
    observed = float(orbit[0])
    p = (1 + int(np.count_nonzero(null >= observed - TOL))) / ASSIGNMENTS
    return {
        "orbit": orbit, "observed": observed, "null_mean": mean, "null_sd": sd,
        "raw_effect": observed - mean, "z": (observed - mean) / sd, "p": p,
        "folio_effects": folio_effects,
        "form_effects": {FORMS[form]: float(np.mean(values)) for form, values in sorted(form_values.items())},
    }


def evaluate(panel: Panel, blocks: dict[str, np.ndarray]) -> dict:
    if tuple(blocks) != tuple(BLOCK_DIMS):
        raise ValueError("EO001 block order/name drift")
    for name, size in BLOCK_DIMS.items():
        if blocks[name].shape != (1295, size):
            raise ValueError(f"EO001 {name} dimension drift")
    raw = {name: block_orbit(panel, blocks[name]) for name in BLOCK_DIMS}
    standardized = np.vstack([
        (raw[name]["orbit"] - raw[name]["null_mean"]) / raw[name]["null_sd"]
        for name in BLOCK_DIMS
    ])
    combined_orbit = standardized.mean(axis=0)
    observed = float(combined_orbit[0])
    combined_p = (1 + int(np.count_nonzero(combined_orbit[1:] >= observed - TOL))) / ASSIGNMENTS
    folio_contributions = {}
    for folio in panel.informative:
        folio_contributions[folio] = float(np.mean([
            raw[name]["folio_effects"][folio] / raw[name]["null_sd"] for name in BLOCK_DIMS
        ]))
    form_contributions = {}
    for form in FORMS:
        form_contributions[form] = float(np.mean([
            raw[name]["form_effects"][form] / raw[name]["null_sd"] for name in BLOCK_DIMS
        ]))
    values = np.asarray(list(folio_contributions.values()), dtype=np.float64)
    deletion = (values.sum() - values) / (len(values) - 1)
    total_abs = float(np.abs(values).sum())
    currier = {}
    for value in ("A", "B"):
        selected = [effect for folio, effect in folio_contributions.items() if panel.curriers[np.flatnonzero(panel.folios == folio)[0]] == value]
        currier[value] = {"folios": len(selected), "mean": float(np.mean(selected))}
    blocks_out = {
        name: {key: value for key, value in raw[name].items() if key not in ("orbit", "folio_effects", "form_effects")}
        for name in BLOCK_DIMS
    }
    summary = {
        "combined_observed": observed,
        "combined_p": combined_p,
        "positive_folios": int((values > 0).sum()),
        "informative_folios": len(values),
        "positive_forms": sum(value > 0 for value in form_contributions.values()),
        "minimum_delete_one_folio_mean": float(deletion.min()),
        "max_abs_folio_contribution_fraction": float(np.abs(values).max() / total_abs) if total_abs else 1.0,
        "currier": currier,
        "folio_contributions": folio_contributions,
        "form_contributions": form_contributions,
    }
    gates = {
        "exact_geometry": len(panel.rows) == 1295 and len(set(panel.folios)) == 92 and len(panel.informative) == 38,
        "combined_material": observed >= 1.5,
        "combined_p_at_most_001": combined_p <= .01,
        "all_blocks_positive": all(blocks_out[name]["raw_effect"] > 0 for name in BLOCK_DIMS),
        "two_blocks_p_at_most_005": sum(blocks_out[name]["p"] <= .05 for name in BLOCK_DIMS) >= 2,
        "positive_folio_support": summary["positive_folios"] >= 24,
        "positive_form_support": summary["positive_forms"] >= 7,
        "both_curriers_positive": all(currier[value]["folios"] >= 10 and currier[value]["mean"] > 0 for value in ("A", "B")),
        "all_folio_deletions_positive": summary["minimum_delete_one_folio_mean"] > 0,
        "no_folio_concentration": summary["max_abs_folio_contribution_fraction"] <= .20,
    }
    return {"blocks": blocks_out, "summary": summary, "gates": gates, "passes": all(gates.values())}
