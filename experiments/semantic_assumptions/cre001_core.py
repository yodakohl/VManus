#!/usr/bin/env python3
"""Scientific core for CRE001 page-specific C-to-L echoes."""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter

import numpy as np


READINGS = ("ZL3b", "IT2a", "RF1b")
COMPONENTS = (3, 4)
TOL = 1e-15


def array_sha(array: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(array, dtype="<f8").tobytes(order="C")).hexdigest()


def index_sha(array: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(array, dtype="<i8").tobytes(order="C")).hexdigest()


def canonical_sha(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def ngrams(group: str, size: int) -> list[str]:
    if size <= 0:
        raise ValueError("positive n-gram size required")
    return [group[index:index + size] for index in range(len(group) - size + 1)]


def crossrole_similarity(
    label_groups: dict[str, list[str]],
    circle_groups: dict[str, list[str]],
    pages: list[str],
    remove_exact_group_echo: bool,
) -> dict[int, np.ndarray]:
    if set(label_groups) != set(pages) or set(circle_groups) != set(pages):
        raise ValueError("page bags differ")
    result = {size: np.empty((len(pages), len(pages)), dtype=np.float64) for size in COMPONENTS}
    circle_surfaces = {page: set(circle_groups[page]) for page in pages}
    label_ngram_counts = {}
    circle_ngram_sets = {}
    for page in pages:
        selected_labels = [
            group for group in label_groups[page]
            if not remove_exact_group_echo or group not in circle_surfaces[page]
        ]
        label_ngram_counts[page] = {
            size: Counter(gram for group in selected_labels for gram in ngrams(group, size))
            for size in COMPONENTS
        }
        circle_ngram_sets[page] = {
            size: {gram for group in circle_groups[page] for gram in ngrams(group, size)}
            for size in COMPONENTS
        }
        if any(not label_ngram_counts[page][size] for size in COMPONENTS):
            raise ValueError(f"no eligible label n-grams on {page}")
        if any(not circle_ngram_sets[page][size] for size in COMPONENTS):
            raise ValueError(f"no eligible circle n-grams on {page}")
    for label_index, label_page in enumerate(pages):
        for circle_index, circle_page in enumerate(pages):
            for size in COMPONENTS:
                counts = label_ngram_counts[label_page][size]
                present = circle_ngram_sets[circle_page][size]
                result[size][label_index, circle_index] = (
                    sum(count for gram, count in counts.items() if gram in present) / sum(counts.values())
                )
    return result


def assignment_matrix(pages: list[str], folio_by_page: dict[str, str]) -> np.ndarray:
    if pages != sorted(pages) or set(pages) != set(folio_by_page):
        raise ValueError("canonical page panel required")
    folios = sorted(set(folio_by_page.values()))
    positions = {
        folio: [index for index, page in enumerate(pages) if folio_by_page[page] == folio]
        for folio in folios
    }
    if any(len(values) < 2 for values in positions.values()):
        raise ValueError("every folio must have at least two pages")
    permutations = [list(itertools.permutations(positions[folio])) for folio in folios]
    rows = []
    for product in itertools.product(*permutations):
        row = list(range(len(pages)))
        for destination_positions, source_positions in zip(positions.values(), product):
            for destination, source in zip(destination_positions, source_positions):
                row[destination] = source
        rows.append(row)
    matrix = np.asarray(rows, dtype=np.int64)
    if len({tuple(row) for row in matrix.tolist()}) != len(matrix):
        raise AssertionError("duplicate assignment row")
    identity = tuple(range(len(pages)))
    if sum(tuple(row) == identity for row in matrix.tolist()) != 1:
        raise AssertionError("identity assignment multiplicity")
    return matrix


def evaluate(
    component_matrices: dict[str, dict[int, np.ndarray]],
    pages: list[str],
    folio_by_page: dict[str, str],
    assignments: np.ndarray | None = None,
) -> dict[str, object]:
    if tuple(component_matrices) != READINGS:
        raise ValueError("canonical reading order required")
    if assignments is None:
        assignments = assignment_matrix(pages, folio_by_page)
    assignments = np.asarray(assignments, dtype=np.int64)
    if assignments.ndim != 2 or assignments.shape[1] != len(pages):
        raise ValueError("assignment shape")
    identity_rows = np.flatnonzero(np.all(assignments == np.arange(len(pages)), axis=1))
    if len(identity_rows) != 1:
        raise ValueError("one identity row required")
    identity_index = int(identity_rows[0])
    folios = sorted(set(folio_by_page.values()))
    page_positions = {
        folio: [index for index, page in enumerate(pages) if folio_by_page[page] == folio]
        for folio in folios
    }
    page_weights = np.asarray([
        1.0 / (len(folios) * len(page_positions[folio_by_page[page]])) for page in pages
    ], dtype=np.float64)
    raw_orbits = np.empty((len(assignments), len(READINGS)), dtype=np.float64)
    centered_orbits = np.empty_like(raw_orbits)
    T_by_reading = {}
    component_effects = {edition: {} for edition in READINGS}
    page_effects = {edition: {} for edition in READINGS}
    folio_effects = {edition: {} for edition in READINGS}
    similarity_digests = {}
    destinations = np.arange(len(pages))[None, :]
    for edition_index, edition in enumerate(READINGS):
        components = component_matrices[edition]
        if set(components) != set(COMPONENTS):
            raise ValueError("component set")
        for size in COMPONENTS:
            matrix = np.asarray(components[size], dtype=np.float64)
            if matrix.shape != (len(pages), len(pages)) or not np.isfinite(matrix).all():
                raise ValueError("similarity matrix")
            similarity_digests[f"{edition}_k{size}"] = array_sha(matrix)
            selected_component = matrix[destinations, assignments]
            component_raw = selected_component @ page_weights
            component_effects[edition][str(size)] = float(
                component_raw[identity_index] - np.mean(component_raw)
            )
        combined = np.mean(np.stack([components[size] for size in COMPONENTS], axis=0), axis=0)
        selected = combined[destinations, assignments]
        raw = selected @ page_weights
        raw_orbits[:, edition_index] = raw
        centered = raw - np.mean(raw)
        centered_orbits[:, edition_index] = centered
        T_by_reading[edition] = float(centered[identity_index])
        for page_index, page in enumerate(pages):
            folio = folio_by_page[page]
            candidates = page_positions[folio]
            page_effects[edition][page] = float(
                combined[page_index, page_index] - np.mean(combined[page_index, candidates])
            )
        for folio in folios:
            folio_effects[edition][folio] = float(np.mean([
                page_effects[edition][pages[index]] for index in page_positions[folio]
            ]))
        if abs(T_by_reading[edition] - np.mean(list(folio_effects[edition].values()))) > 2e-15:
            raise AssertionError("folio effect aggregation drift")
    M = min(T_by_reading.values())
    null_M = np.min(centered_orbits, axis=1)
    p = int(np.sum(null_M >= M - TOL)) / len(assignments)
    support = {
        edition: sum(value > 0 for value in folio_effects[edition].values())
        for edition in READINGS
    }
    loo = {
        deleted: min(float(np.mean([
            value for folio, value in folio_effects[edition].items() if folio != deleted
        ])) for edition in READINGS)
        for deleted in folios
    }
    concentration = {}
    for edition in READINGS:
        absolute = [abs(value) for value in folio_effects[edition].values()]
        concentration[edition] = max(absolute) / sum(absolute) if sum(absolute) else 1.0
    result = {
        "pages": pages,
        "folios": folios,
        "assignment_count": len(assignments),
        "identity_assignment_index": identity_index,
        "T_by_reading": T_by_reading,
        "M": M,
        "p": p,
        "component_effects_by_reading": component_effects,
        "page_effects": page_effects,
        "folio_effects": folio_effects,
        "positive_folios_by_reading": support,
        "leave_one_folio_out_M": loo,
        "concentration_by_reading": concentration,
        "digests": {
            "assignments_sha256": index_sha(assignments),
            "similarity_matrices_sha256": canonical_sha(similarity_digests),
            "raw_orbits_sha256": array_sha(raw_orbits),
            "centered_orbits_sha256": array_sha(centered_orbits),
            "null_M_sha256": array_sha(null_M),
            "component_effects_sha256": canonical_sha(component_effects),
            "page_effects_sha256": canonical_sha(page_effects),
            "folio_effects_sha256": canonical_sha(folio_effects),
        },
    }
    result["digests"]["result_core_sha256"] = canonical_sha({
        key: value for key, value in result.items() if key != "digests"
    })
    result["_arrays"] = {
        "raw_orbits": raw_orbits,
        "centered_orbits": centered_orbits,
        "null_M": null_M,
    }
    return result


def compact(result: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in result.items() if key != "_arrays"}


def primary_gates(
    result: dict[str, object],
    magnitude: float,
    p_threshold: float,
    required_positive_folios: int,
    require_loo: bool,
) -> dict[str, bool]:
    gates = {
        "magnitude": float(result["M"]) >= magnitude,
        "p": float(result["p"]) <= p_threshold,
        "all_readings_positive": all(value > 0 for value in result["T_by_reading"].values()),
        "both_components_positive_every_reading": all(
            value > 0
            for edition in READINGS
            for value in result["component_effects_by_reading"][edition].values()
        ),
        "required_positive_folios_each_reading": all(
            value >= required_positive_folios
            for value in result["positive_folios_by_reading"].values()
        ),
    }
    if require_loo:
        gates.update({
            "all_leave_one_folio_out_above_002": all(
                value > 0.02 for value in result["leave_one_folio_out_M"].values()
            ),
            "concentration_at_most_045": all(
                value <= 0.45 for value in result["concentration_by_reading"].values()
            ),
        })
    return gates
