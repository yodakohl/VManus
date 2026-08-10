#!/usr/bin/env python3
"""Target-independent rank and fixed-quota core for LRG008."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

import numpy as np


ASSIGNMENTS = 8192
SEED = 80082026


@dataclass(frozen=True)
class Geometry:
    row_ids: np.ndarray
    cell_ids: np.ndarray
    pages: np.ndarray
    folios: np.ndarray
    sections: np.ndarray
    roles: np.ndarray
    lengths: np.ndarray
    label_quota: dict[str, int]


def digest_array(value: np.ndarray) -> str:
    array = np.ascontiguousarray(value)
    return hashlib.sha256(array.tobytes(order="C")).hexdigest()


def geometry_from_capacity(capacity: dict[str, object]) -> Geometry:
    rows = {key: [] for key in ("row_ids", "cell_ids", "pages", "folios", "sections", "roles", "lengths")}
    quotas: dict[str, int] = {}
    for cell in capacity["per_cell"]:
        identifier = str(cell["cell_id"])
        quotas[identifier] = int(cell["label_rows"])
        role = "C" if int(cell["C_rows"]) else "R"
        if (int(cell["C_rows"]) > 0) == (int(cell["R_rows"]) > 0):
            raise RuntimeError("cell must have exactly one diagram role")
        for index in range(int(cell["total_rows"])):
            rows["row_ids"].append(f"{identifier}|R{index + 1:03d}")
            rows["cell_ids"].append(identifier)
            rows["pages"].append(str(cell["page"]))
            rows["folios"].append(str(cell["physical_folio"]))
            rows["sections"].append(str(cell["section"]))
            rows["roles"].append(role)
            rows["lengths"].append(int(cell["symbol_count"]))
    geometry = Geometry(
        row_ids=np.asarray(rows["row_ids"], dtype="U20"),
        cell_ids=np.asarray(rows["cell_ids"], dtype="U16"),
        pages=np.asarray(rows["pages"], dtype="U16"),
        folios=np.asarray(rows["folios"], dtype="U8"),
        sections=np.asarray(rows["sections"], dtype="U1"),
        roles=np.asarray(rows["roles"], dtype="U1"),
        lengths=np.asarray(rows["lengths"], dtype=np.int16),
        label_quota=quotas,
    )
    if len(geometry.row_ids) != 286 or len(set(geometry.cell_ids)) != 40 or len(set(geometry.folios)) != 6:
        raise RuntimeError("LRG008 geometry drift")
    return geometry


def cell_indices(geometry: Geometry, mask: np.ndarray | None = None) -> list[np.ndarray]:
    if mask is None:
        mask = np.ones(len(geometry.row_ids), dtype=bool)
    return [np.flatnonzero(mask & (geometry.cell_ids == cell)) for cell in sorted(set(geometry.cell_ids[mask]))]


def validate_labels(labels: np.ndarray, geometry: Geometry) -> None:
    if labels.shape != (len(geometry.row_ids),) or labels.dtype != np.bool_:
        raise RuntimeError("invalid labels")
    for indices in cell_indices(geometry):
        cell = str(geometry.cell_ids[indices[0]])
        if int(labels[indices].sum()) != geometry.label_quota[cell]:
            raise RuntimeError("quota drift")


def randomized_labels(geometry: Geometry, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    labels = np.zeros(len(geometry.row_ids), dtype=bool)
    for indices in cell_indices(geometry):
        cell = str(geometry.cell_ids[indices[0]])
        labels[rng.choice(indices, size=geometry.label_quota[cell], replace=False)] = True
    validate_labels(labels, geometry)
    return labels


def fixed_quota_coefficients(geometry: Geometry) -> np.ndarray:
    rng = np.random.default_rng(SEED)
    assignments = np.zeros((ASSIGNMENTS, len(geometry.row_ids)), dtype=bool)
    for indices in cell_indices(geometry):
        cell = str(geometry.cell_ids[indices[0]])
        count = geometry.label_quota[cell]
        random_values = rng.random((ASSIGNMENTS, len(indices)))
        chosen = np.argpartition(random_values, count - 1, axis=1)[:, :count]
        assignments[np.arange(ASSIGNMENTS)[:, None], indices[chosen]] = True
    packed = np.packbits(assignments, axis=1, bitorder="little")
    if len(np.unique(packed, axis=0)) != ASSIGNMENTS:
        raise RuntimeError("duplicate assignment")
    coefficient = np.zeros(assignments.shape, dtype=np.float64)
    folios = sorted(set(geometry.folios))
    for physical in folios:
        folio_mask = geometry.folios == physical
        pages = sorted(set(geometry.pages[folio_mask]))
        for page in pages:
            page_mask = folio_mask & (geometry.pages == page)
            cells = cell_indices(geometry, page_mask)
            for indices in cells:
                cell = str(geometry.cell_ids[indices[0]])
                high = geometry.label_quota[cell]
                low = len(indices) - high
                weight = 1.0 / len(folios) / len(pages) / len(cells)
                coefficient[:, indices] = -weight / low
                local = assignments[:, indices]
                coefficient[:, indices] = np.where(local, weight / high, coefficient[:, indices])
    if not np.isfinite(coefficient).all() or not np.allclose(coefficient.sum(axis=1), 0.0, atol=1e-14):
        raise RuntimeError("invalid coefficient matrix")
    return coefficient


def average_ranks(scores: np.ndarray, geometry: Geometry) -> np.ndarray:
    if scores.shape != (len(geometry.row_ids),) or not np.isfinite(scores).all():
        raise RuntimeError("invalid scores")
    ranks = np.zeros(len(scores), dtype=np.float64)
    for indices in cell_indices(geometry):
        values = scores[indices]
        order = np.argsort(values, kind="stable")
        sorted_values = values[order]
        start = 0
        while start < len(indices):
            stop = start + 1
            while stop < len(indices) and sorted_values[stop] == sorted_values[start]:
                stop += 1
            value = ((start + stop - 1) / 2.0) / (len(indices) - 1)
            ranks[indices[order[start:stop]]] = value
            start = stop
        if abs(float(ranks[indices].mean()) - 0.5) > 1e-14:
            raise RuntimeError("rank centering drift")
    return ranks


def cell_contrasts(ranks: np.ndarray, labels: np.ndarray, geometry: Geometry, mask: np.ndarray) -> dict[str, float]:
    values = {}
    for indices in cell_indices(geometry, mask):
        high = indices[labels[indices]]
        low = indices[~labels[indices]]
        if not len(high) or not len(low):
            raise RuntimeError("nonmixed cell")
        values[str(geometry.cell_ids[indices[0]])] = float(ranks[high].mean() - ranks[low].mean())
    return values


def hierarchical_effect(ranks: np.ndarray, labels: np.ndarray, geometry: Geometry, mask: np.ndarray) -> tuple[float, dict[str, float]]:
    contrasts = cell_contrasts(ranks, labels, geometry, mask)
    folio_values = {}
    for physical in sorted(set(geometry.folios[mask])):
        page_values = []
        for page in sorted(set(geometry.pages[mask & (geometry.folios == physical)])):
            cells = sorted(set(geometry.cell_ids[mask & (geometry.pages == page)]))
            page_values.append(float(np.mean([contrasts[str(cell)] for cell in cells])))
        folio_values[str(physical)] = float(np.mean(page_values))
    return float(np.mean(list(folio_values.values()))), folio_values


def evaluate(scores: np.ndarray, labels: np.ndarray, geometry: Geometry, coefficient: np.ndarray) -> dict[str, object]:
    validate_labels(labels, geometry)
    if coefficient.shape != (ASSIGNMENTS, len(labels)):
        raise RuntimeError("coefficient shape")
    ranks = average_ranks(scores, geometry)
    all_rows = np.ones(len(labels), dtype=bool)
    effect, folio_effects = hierarchical_effect(ranks, labels, geometry, all_rows)
    null = coefficient @ ranks
    null_mean = float(null.mean())
    null_sd = float(null.std(ddof=0))
    if not np.isfinite(null_sd) or null_sd <= 0:
        raise RuntimeError("degenerate null")
    p = (1 + int(np.count_nonzero(null >= effect - 1e-15))) / (len(null) + 1)
    z = (effect - null_mean) / null_sd
    role_effects = {role: hierarchical_effect(ranks, labels, geometry, geometry.roles == role)[0] for role in ("C", "R")}
    section_effects = {section: hierarchical_effect(ranks, labels, geometry, geometry.sections == section)[0] for section in sorted(set(geometry.sections))}
    folio_numbers = np.asarray([int(value[1:]) for value in geometry.folios])
    parity_effects = {
        "EVEN": hierarchical_effect(ranks, labels, geometry, folio_numbers % 2 == 0)[0],
        "ODD": hierarchical_effect(ranks, labels, geometry, folio_numbers % 2 == 1)[0],
    }
    deletions = {
        physical: float(np.mean([value for key, value in folio_effects.items() if key != physical]))
        for physical in folio_effects
    }
    concentration = max(abs(value) for value in folio_effects.values()) / sum(abs(value) for value in folio_effects.values())
    gates = {
        "effect_at_least_015": effect >= 0.15,
        "p_at_most_001": p <= 0.01,
        "z_at_least_3": z >= 3.0,
        "both_role_effects_at_least_010": min(role_effects.values()) >= 0.10,
        "all_section_effects_at_least_008": min(section_effects.values()) >= 0.08,
        "both_parity_effects_at_least_008": min(parity_effects.values()) >= 0.08,
        "five_of_six_folios_positive": sum(value > 0 for value in folio_effects.values()) >= 5,
        "all_deletions_at_least_010": min(deletions.values()) >= 0.10,
        "concentration_at_most_035": concentration <= 0.35,
    }
    return {
        "effect": effect, "p": p, "z": z, "null_mean": null_mean, "null_sd": null_sd,
        "role_effects": role_effects, "section_effects": section_effects,
        "parity_effects": parity_effects, "folio_effects": folio_effects,
        "minimum_deletion": min(deletions.values()),
        "maximum_absolute_folio_concentration": concentration,
        "positive_folios": sum(value > 0 for value in folio_effects.values()),
        "rank_sha256": digest_array(ranks), "null_sha256": digest_array(null),
        "gates": gates, "passes": all(gates.values()),
    }
