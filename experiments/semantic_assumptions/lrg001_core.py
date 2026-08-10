#!/usr/bin/env python3
"""Scientific core for the LRG001 two-parity label-register test."""

from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass
from pathlib import Path

import numpy as np


ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWX"
INDEX = {value: index for index, value in enumerate(ALPHABET)}
DIMENSION = 24 + 24 + 24 + 24 * 24
ASSIGNMENTS = 8192
SEED = 17012026


@dataclass(frozen=True)
class Geometry:
    cell_ids: np.ndarray
    pages: np.ndarray
    folios: np.ndarray
    sections: np.ndarray
    lengths: np.ndarray
    labels_per_cell: dict[str, int]
    row_ids: np.ndarray


def sha256_array(value: np.ndarray) -> str:
    array = np.ascontiguousarray(value)
    return hashlib.sha256(array.tobytes(order="C")).hexdigest()


def load_geometry(path: Path) -> Geometry:
    with path.open(encoding="utf-8", newline="") as handle:
        cells = list(csv.DictReader(handle, delimiter="\t"))
    cell_ids: list[str] = []
    pages: list[str] = []
    folios: list[str] = []
    sections: list[str] = []
    lengths: list[int] = []
    row_ids: list[str] = []
    labels_per_cell: dict[str, int] = {}
    for cell in cells:
        if cell["section"] not in {"B", "P"}:
            continue
        identifier = cell["cell_id"]
        labels_per_cell[identifier] = int(cell["label_rows"])
        total = int(cell["total_rows"])
        for index in range(total):
            cell_ids.append(identifier)
            pages.append(cell["page"])
            folios.append(cell["physical_folio"])
            sections.append(cell["section"])
            lengths.append(int(cell["symbol_count"]))
            row_ids.append(f"{identifier}|R{index + 1:03d}")
    geometry = Geometry(
        cell_ids=np.asarray(cell_ids, dtype="U16"),
        pages=np.asarray(pages, dtype="U16"),
        folios=np.asarray(folios, dtype="U8"),
        sections=np.asarray(sections, dtype="U1"),
        lengths=np.asarray(lengths, dtype=np.int16),
        labels_per_cell=labels_per_cell,
        row_ids=np.asarray(row_ids, dtype="U32"),
    )
    if len(geometry.row_ids) != 2767 or len(set(geometry.folios)) != 13:
        raise RuntimeError("LRG001 primary geometry drift")
    return geometry


def feature_matrix(sequences: list[str], lengths: np.ndarray) -> np.ndarray:
    if len(sequences) != len(lengths):
        raise RuntimeError("sequence/length mismatch")
    matrix = np.zeros((len(sequences), DIMENSION), dtype=np.float64)
    for row_index, (sequence, expected_length) in enumerate(zip(sequences, lengths, strict=True)):
        if len(sequence) != int(expected_length) or not sequence or any(value not in INDEX for value in sequence):
            raise RuntimeError(f"invalid sequence at row {row_index}")
        values = [INDEX[value] for value in sequence]
        for value in values:
            matrix[row_index, value] += 1.0 / len(values)
        matrix[row_index, 24 + values[0]] = 1.0
        matrix[row_index, 48 + values[-1]] = 1.0
        if len(values) > 1:
            scale = 1.0 / (len(values) - 1)
            for left, right in zip(values, values[1:]):
                matrix[row_index, 72 + 24 * left + right] += scale
    if not np.isfinite(matrix).all():
        raise RuntimeError("nonfinite feature matrix")
    return matrix


def cell_indices(geometry: Geometry, mask: np.ndarray) -> list[np.ndarray]:
    return [
        np.flatnonzero(mask & (geometry.cell_ids == cell))
        for cell in sorted(set(geometry.cell_ids[mask]))
    ]


def learn_profile(matrix: np.ndarray, labels: np.ndarray, geometry: Geometry, train_mask: np.ndarray) -> np.ndarray:
    folio_vectors = []
    for folio in sorted(set(geometry.folios[train_mask])):
        current = train_mask & (geometry.folios == folio)
        contrasts = []
        for indices in cell_indices(geometry, current):
            high = indices[labels[indices] == 1]
            low = indices[labels[indices] == 0]
            if not len(high) or not len(low):
                raise RuntimeError("nonmixed training cell")
            contrasts.append(matrix[high].mean(axis=0) - matrix[low].mean(axis=0))
        folio_vectors.append(np.mean(np.stack(contrasts), axis=0))
    vector = np.mean(np.stack(folio_vectors), axis=0)
    norm = float(np.linalg.norm(vector))
    if not np.isfinite(norm) or norm <= 1e-12:
        raise RuntimeError("degenerate training profile")
    return vector / norm


def held_effects(scores: np.ndarray, labels: np.ndarray, geometry: Geometry, held_mask: np.ndarray) -> tuple[float, dict[str, float], dict[str, float]]:
    folio_values: dict[str, float] = {}
    section_folios: dict[str, list[float]] = {"B": [], "P": []}
    for folio in sorted(set(geometry.folios[held_mask])):
        current = held_mask & (geometry.folios == folio)
        contrasts = []
        for indices in cell_indices(geometry, current):
            high = indices[labels[indices] == 1]
            low = indices[labels[indices] == 0]
            contrasts.append(float(scores[high].mean() - scores[low].mean()))
        value = float(np.mean(contrasts))
        folio_values[folio] = value
        section = str(geometry.sections[np.flatnonzero(current)[0]])
        section_folios[section].append(value)
    section_values = {key: float(np.mean(values)) for key, values in section_folios.items()}
    return float(np.mean(list(folio_values.values()))), folio_values, section_values


def assignment_coefficients(geometry: Geometry, held_mask: np.ndarray, assignments: int = ASSIGNMENTS) -> tuple[np.ndarray, np.ndarray]:
    held_indices = np.flatnonzero(held_mask)
    local = {int(global_index): local_index for local_index, global_index in enumerate(held_indices)}
    coefficient = np.zeros((assignments, len(held_indices)), dtype=np.float32)
    rng = np.random.default_rng(SEED + (0 if int(geometry.folios[held_indices[0]][1:]) % 2 == 0 else 1))
    held_folios = sorted(set(geometry.folios[held_mask]))
    for folio in held_folios:
        current = held_mask & (geometry.folios == folio)
        cells = cell_indices(geometry, current)
        for indices in cells:
            cell = str(geometry.cell_ids[indices[0]])
            high_count = geometry.labels_per_cell[cell]
            if not 0 < high_count < len(indices):
                raise RuntimeError("invalid held quota")
            base = -1.0 / (len(held_folios) * len(cells) * (len(indices) - high_count))
            selected = 1.0 / (len(held_folios) * len(cells) * high_count)
            columns = np.asarray([local[int(index)] for index in indices], dtype=np.int64)
            coefficient[:, columns] = base
            random_ranks = rng.random((assignments, len(columns)))
            chosen_local = np.argpartition(random_ranks, high_count - 1, axis=1)[:, :high_count]
            chosen = columns[chosen_local]
            coefficient[np.arange(assignments)[:, None], chosen] = selected
    return held_indices, coefficient


def evaluate(matrix: np.ndarray, labels: np.ndarray, geometry: Geometry, coefficient_even: tuple[np.ndarray, np.ndarray], coefficient_odd: tuple[np.ndarray, np.ndarray]) -> dict[str, object]:
    if matrix.shape != (len(labels), DIMENSION) or set(np.unique(labels)) - {0, 1}:
        raise RuntimeError("invalid target arrays")
    folio_number = np.asarray([int(value[1:]) for value in geometry.folios])
    odd = folio_number % 2 == 1
    even = ~odd
    profile_odd = learn_profile(matrix, labels, geometry, odd)
    profile_even = learn_profile(matrix, labels, geometry, even)
    cosine = float(profile_odd @ profile_even)
    directions = {}
    for name, profile, held, coefficients, positive_required in (
        ("ODD_TO_EVEN", profile_odd, even, coefficient_even, 5),
        ("EVEN_TO_ODD", profile_even, odd, coefficient_odd, 4),
    ):
        scores = matrix @ profile
        effect, folios, sections = held_effects(scores, labels, geometry, held)
        held_indices, coefficient = coefficients
        null = np.asarray(coefficient @ scores[held_indices], dtype=np.float64)
        p = (1 + int(np.count_nonzero(null >= effect))) / (len(null) + 1)
        deletions = {
            folio: float(np.mean([value for key, value in folios.items() if key != folio]))
            for folio in folios
        }
        concentration = max(abs(value) for value in folios.values()) / sum(abs(value) for value in folios.values())
        gates = {
            "p_at_most_001": p <= 0.01,
            "effect_at_least_005": effect >= 0.05,
            "positive_folio_support": sum(value > 0 for value in folios.values()) >= positive_required,
            "both_sections_at_least_005": all(value >= 0.05 for value in sections.values()),
            "all_deletions_positive": min(deletions.values()) > 0,
            "concentration_at_most_035": concentration <= 0.35,
        }
        directions[name] = {
            "effect": effect,
            "p": p,
            "positive_folios": sum(value > 0 for value in folios.values()),
            "folio_count": len(folios),
            "folio_effects": folios,
            "section_effects": sections,
            "minimum_deletion": min(deletions.values()),
            "maximum_absolute_folio_concentration": concentration,
            "null_sha256": sha256_array(null),
            "gates": gates,
            "passes": all(gates.values()),
        }
    gates = {
        "odd_to_even": bool(directions["ODD_TO_EVEN"]["passes"]),
        "even_to_odd": bool(directions["EVEN_TO_ODD"]["passes"]),
        "profile_cosine_at_least_010": cosine >= 0.10,
    }
    return {
        "profile_cosine": cosine,
        "odd_profile_sha256": sha256_array(profile_odd),
        "even_profile_sha256": sha256_array(profile_even),
        "directions": directions,
        "gates": gates,
        "passes": all(gates.values()),
    }
