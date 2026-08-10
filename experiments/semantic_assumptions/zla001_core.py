#!/usr/bin/env python3
"""Scientific core for ZLA001 cyclic label-adjacency scoring."""

from __future__ import annotations

import csv
import hashlib
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np


READINGS = ("ZL3b", "IT2a", "RF1b")
VIEWS = ("FAMILY_ONLY", "BOUNDARY_AWARE")
N_WORLDS = 65_536
TOL = 1e-15


@dataclass(frozen=True)
class Ring:
    ring_id: str
    page: str
    folio: str
    scope: str
    loci: tuple[str, ...]

    @property
    def n(self) -> int:
        return len(self.loci)

    @property
    def distances(self) -> tuple[int, ...]:
        return tuple(range(2, self.n // 2 + 1))


@dataclass(frozen=True)
class Geometry:
    rings: tuple[Ring, ...]
    pages: tuple[str, ...]
    folios: tuple[str, ...]


def sha256_array(array: np.ndarray) -> str:
    value = np.ascontiguousarray(array)
    return hashlib.sha256(value.tobytes(order="C")).hexdigest()


def load_geometry(path: Path) -> Geometry:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 235 or len({row["current_locus"] for row in rows}) != 235:
        raise AssertionError("geometry row contract")
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(row["ring_id"], []).append(row)
    rings = []
    for ring_id in sorted(grouped):
        values = sorted(grouped[ring_id], key=lambda row: int(row["grove_ordinal"]))
        if [int(row["grove_ordinal"]) for row in values] != list(range(1, len(values) + 1)):
            raise AssertionError("ordinal contract")
        if len({(row["page"], row["physical_folio"], row["ring_scope"]) for row in values}) != 1:
            raise AssertionError("ring metadata drift")
        rings.append(Ring(
            ring_id=ring_id,
            page=values[0]["page"],
            folio=values[0]["physical_folio"],
            scope=values[0]["ring_scope"],
            loci=tuple(row["current_locus"] for row in values),
        ))
    geometry = Geometry(
        rings=tuple(rings),
        pages=tuple(sorted({ring.page for ring in rings})),
        folios=tuple(sorted({ring.folio for ring in rings})),
    )
    if len(geometry.rings) != 21 or len(geometry.pages) != 11 or len(geometry.folios) != 4:
        raise AssertionError("geometry aggregate contract")
    if any(not ring.distances for ring in geometry.rings):
        raise AssertionError("ring lacks nonadjacent distance")
    return geometry


def assignment_matrix(geometry: Geometry) -> tuple[np.ndarray, dict[str, int | str]]:
    radices = [len(ring.distances) for ring in geometry.rings]
    total = math.prod(radices)
    if total <= N_WORLDS:
        raise AssertionError("insufficient complete distance space")
    domain = b"ZLA001|NONADJACENT_DISTANCE_ORBIT|v1"
    start = int.from_bytes(hashlib.sha256(domain + b"|start").digest(), "big") % total
    step = int.from_bytes(hashlib.sha256(domain + b"|step").digest(), "big") % total
    if step == 0:
        step = 1
    while math.gcd(step, total) != 1:
        step += 1
    matrix = np.empty((N_WORLDS, len(radices)), dtype="<u2")
    seen = set()
    for world in range(N_WORLDS):
        rank = (start + world * step) % total
        if rank in seen:
            raise AssertionError("duplicate mixed-radix rank")
        seen.add(rank)
        value = rank
        for column in range(len(radices) - 1, -1, -1):
            digit = value % radices[column]
            value //= radices[column]
            matrix[world, column] = geometry.rings[column].distances[digit]
    if len({row.tobytes() for row in matrix}) != N_WORLDS:
        raise AssertionError("duplicate assignment row")
    return matrix, {
        "complete_space": total,
        "start": start,
        "step": step,
        "sha256": sha256_array(matrix),
    }


def levenshtein(a: tuple[str, ...], b: tuple[str, ...]) -> int:
    if len(a) < len(b):
        a, b = b, a
    previous = list(range(len(b) + 1))
    for i, left in enumerate(a, 1):
        current = [i]
        for j, right in enumerate(b, 1):
            current.append(min(
                current[-1] + 1,
                previous[j] + 1,
                previous[j - 1] + (left != right),
            ))
        previous = current
    return previous[-1]


def pair_score(a: tuple[str, ...], b: tuple[str, ...]) -> float:
    if not a or not b:
        raise AssertionError("empty sequence")
    maximum = max(len(a), len(b))
    similarity = 1.0 - levenshtein(a, b) / maximum
    ceiling = min(len(a), len(b)) / maximum
    value = similarity - ceiling
    if value > TOL or value < -1.0 - TOL or not math.isfinite(value):
        raise AssertionError("pair score bounds")
    return min(value, 0.0)


def _ring_table(
    view_sequences: list[tuple[str, ...]],
    boundary_sequences: list[tuple[str, ...]],
    ring: Ring,
    no_exact: bool,
) -> dict[int, float]:
    output = {}
    for distance in range(1, ring.n // 2 + 1):
        values = []
        for index in range(ring.n):
            other = (index + distance) % ring.n
            if no_exact and boundary_sequences[index] == boundary_sequences[other]:
                continue
            values.append(pair_score(view_sequences[index], view_sequences[other]))
        output[distance] = float(np.mean(values)) if len(values) >= 3 else float("nan")
    return output


def _aggregate_ring_matrix(matrix: np.ndarray, geometry: Geometry) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    if matrix.shape[1] != len(geometry.rings):
        raise AssertionError("ring matrix width")
    page_scores: dict[str, np.ndarray] = {}
    for page in geometry.pages:
        columns = [index for index, ring in enumerate(geometry.rings) if ring.page == page]
        with np.errstate(invalid="ignore"):
            page_scores[page] = np.nanmean(matrix[:, columns], axis=1)
    folio_scores: dict[str, np.ndarray] = {}
    for folio in geometry.folios:
        pages = [page for page in geometry.pages if any(ring.page == page and ring.folio == folio for ring in geometry.rings)]
        with np.errstate(invalid="ignore"):
            folio_scores[folio] = np.nanmean(np.stack([page_scores[page] for page in pages]), axis=0)
    with np.errstate(invalid="ignore"):
        aggregate = np.nanmean(np.stack([folio_scores[folio] for folio in geometry.folios]), axis=0)
    return aggregate, folio_scores


def _score_view(
    geometry: Geometry,
    assignments: np.ndarray,
    sequences: dict[str, dict[str, list[tuple[str, ...]]]],
    reading: str,
    view: str,
    no_exact: bool,
) -> tuple[np.ndarray, dict[str, np.ndarray], int, tuple[str, ...]]:
    ring_columns = []
    eligible_observed = []
    for column, ring in enumerate(geometry.rings):
        view_values = sequences[reading][view][column]
        boundary_values = sequences[reading]["BOUNDARY_AWARE"][column]
        table = _ring_table(view_values, boundary_values, ring, no_exact)
        observed = table[1]
        values = np.empty(N_WORLDS + 1, dtype=np.float64)
        values[0] = observed
        for distance in ring.distances:
            mask = assignments[:, column] == distance
            values[1:][mask] = table[distance]
        ring_columns.append(values)
        if math.isfinite(observed):
            eligible_observed.append(ring.ring_id)
    ring_matrix = np.stack(ring_columns, axis=1)
    aggregate, folio = _aggregate_ring_matrix(ring_matrix, geometry)
    return aggregate, folio, len(eligible_observed), tuple(eligible_observed)


def joint_summary(scores: dict[str, np.ndarray]) -> dict[str, object]:
    z_observed = {}
    z_null = {}
    effects = {}
    for reading in READINGS:
        values = scores[reading]
        null = values[1:]
        if not np.isfinite(values).all():
            raise AssertionError("nonfinite aggregate")
        mean = float(np.mean(null))
        sd = float(np.std(null, ddof=0))
        if not sd > 0:
            raise AssertionError("zero null SD")
        effects[reading] = float(values[0] - mean)
        z_observed[reading] = float((values[0] - mean) / sd)
        z_null[reading] = (null - mean) / sd
    observed_joint = min(z_observed.values())
    null_joint = np.min(np.stack([z_null[reading] for reading in READINGS]), axis=0)
    exceed = int(np.count_nonzero(null_joint >= observed_joint - TOL))
    return {
        "effect_by_reading": effects,
        "minimum_effect": min(effects.values()),
        "z_by_reading": z_observed,
        "joint_z": observed_joint,
        "exceedances": exceed,
        "p_plus_one": (1 + exceed) / (N_WORLDS + 1),
        "null_joint_sha256": sha256_array(null_joint.astype("<f8")),
        "score_sha256_by_reading": {reading: sha256_array(scores[reading].astype("<f8")) for reading in READINGS},
    }


def evaluate(
    geometry: Geometry,
    assignments: np.ndarray,
    sequences: dict[str, dict[str, list[list[tuple[str, ...]]]]],
) -> dict[str, object]:
    if assignments.shape != (N_WORLDS, len(geometry.rings)) or assignments.dtype != np.dtype("<u2"):
        raise AssertionError("assignment matrix contract")
    if len({row.tobytes() for row in assignments}) != N_WORLDS:
        raise AssertionError("duplicate assignment row")
    for column, ring in enumerate(geometry.rings):
        if not set(np.unique(assignments[:, column])).issubset(set(ring.distances)):
            raise AssertionError("illegal ring distance")
    # Normalize the nested lists and enforce the complete geometry contract.
    normalized: dict[str, dict[str, list[list[tuple[str, ...]]]]] = {}
    for reading in READINGS:
        normalized[reading] = {}
        for view in VIEWS:
            rings = sequences[reading][view]
            if len(rings) != len(geometry.rings):
                raise AssertionError("sequence ring count")
            clean = []
            for ring, values in zip(geometry.rings, rings):
                if len(values) != ring.n or any(not value for value in values):
                    raise AssertionError("sequence slot contract")
                clean.append([tuple(token for token in value) for value in values])
            normalized[reading][view] = clean

    full_scores: dict[str, dict[str, np.ndarray]] = {view: {} for view in VIEWS}
    noexact_scores: dict[str, dict[str, np.ndarray]] = {view: {} for view in VIEWS}
    full_folios: dict[str, dict[str, dict[str, np.ndarray]]] = {view: {} for view in VIEWS}
    noexact_coverage: dict[str, dict[str, object]] = {}
    for reading in READINGS:
        noexact_coverage[reading] = {}
        for view in VIEWS:
            full, folios, _, _ = _score_view(geometry, assignments, normalized, reading, view, False)
            noexact, _, count, ring_ids = _score_view(geometry, assignments, normalized, reading, view, True)
            full_scores[view][reading] = full
            noexact_scores[view][reading] = noexact
            full_folios[view][reading] = folios
            noexact_coverage[reading][view] = {"rings": count, "ring_ids": ring_ids}

    composite = {
        reading: (full_scores["FAMILY_ONLY"][reading] + full_scores["BOUNDARY_AWARE"][reading]) / 2.0
        for reading in READINGS
    }
    noexact_composite = {
        reading: (noexact_scores["FAMILY_ONLY"][reading] + noexact_scores["BOUNDARY_AWARE"][reading]) / 2.0
        for reading in READINGS
    }
    primary = joint_summary(composite)
    noexact = joint_summary(noexact_composite)
    components = {view: joint_summary(full_scores[view]) for view in VIEWS}

    folio_effects: dict[str, dict[str, float]] = {}
    support: dict[str, int] = {}
    concentration: dict[str, float] = {}
    deletion_effects: dict[str, dict[str, float]] = {folio: {} for folio in geometry.folios}
    for reading in READINGS:
        folio_effects[reading] = {}
        for folio in geometry.folios:
            values = (
                full_folios["FAMILY_ONLY"][reading][folio]
                + full_folios["BOUNDARY_AWARE"][reading][folio]
            ) / 2.0
            folio_effects[reading][folio] = float(values[0] - np.mean(values[1:]))
        support[reading] = sum(value > 0 for value in folio_effects[reading].values())
        absolute = sum(abs(value) for value in folio_effects[reading].values())
        concentration[reading] = max(abs(value) for value in folio_effects[reading].values()) / absolute if absolute else 1.0
        for deleted in geometry.folios:
            remaining = [folio for folio in geometry.folios if folio != deleted]
            deletion_effects[deleted][reading] = float(np.mean([folio_effects[reading][folio] for folio in remaining]))

    noexact_ring_counts = {
        reading: min(int(noexact_coverage[reading][view]["rings"]) for view in VIEWS)
        for reading in READINGS
    }
    noexact_folios = {
        reading: len({
            ring.folio
            for ring in geometry.rings
            if ring.ring_id in set(noexact_coverage[reading]["FAMILY_ONLY"]["ring_ids"])
            and ring.ring_id in set(noexact_coverage[reading]["BOUNDARY_AWARE"]["ring_ids"])
        })
        for reading in READINGS
    }
    gates = {
        "joint_p_at_most_001": float(primary["p_plus_one"]) <= 0.01,
        "minimum_effect_at_least_0015": float(primary["minimum_effect"]) >= 0.015,
        "both_components_at_least_0010": all(float(components[view]["minimum_effect"]) >= 0.010 for view in VIEWS),
        "noexact_coverage_at_least_18_rings_all_four_folios": min(noexact_ring_counts.values()) >= 18 and min(noexact_folios.values()) == 4,
        "noexact_effect_at_least_0010_and_p_at_most_005": float(noexact["minimum_effect"]) >= 0.010 and float(noexact["p_plus_one"]) <= 0.05,
        "at_least_three_positive_folios_every_reading": min(support.values()) >= 3,
        "every_folio_deletion_positive_every_reading": all(value > 0 for item in deletion_effects.values() for value in item.values()),
        "maximum_folio_concentration_at_most_060": max(concentration.values()) <= 0.60,
    }
    return {
        "primary": primary,
        "components": components,
        "noexact": noexact,
        "noexact_ring_counts": noexact_ring_counts,
        "noexact_folio_counts": noexact_folios,
        "folio_effects": folio_effects,
        "positive_folio_counts": support,
        "folio_concentration": concentration,
        "deletion_effects": deletion_effects,
        "gates": gates,
        "confirmed": all(gates.values()),
    }


def rotate_sequences(
    sequences: dict[str, dict[str, list[list[tuple[str, ...]]]]], shifts: Iterable[int]
) -> dict[str, dict[str, list[list[tuple[str, ...]]]]]:
    values = list(shifts)
    output = {reading: {view: [] for view in VIEWS} for reading in READINGS}
    for reading in READINGS:
        for view in VIEWS:
            for ring_values, shift in zip(sequences[reading][view], values):
                k = shift % len(ring_values)
                output[reading][view].append(ring_values[-k:] + ring_values[:-k] if k else list(ring_values))
    return output


def reflect_sequences(
    sequences: dict[str, dict[str, list[list[tuple[str, ...]]]]]
) -> dict[str, dict[str, list[list[tuple[str, ...]]]]]:
    return {
        reading: {view: [list(reversed(values)) for values in sequences[reading][view]] for view in VIEWS}
        for reading in READINGS
    }
