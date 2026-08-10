#!/usr/bin/env python3
"""Core geometry, rank transform, rotations, and slot statistic for LRG002."""

from __future__ import annotations

import csv
import hashlib
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np


ASSIGNMENTS = 8192
SEED = 22022026


def sha256_array(value: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(value).tobytes(order="C")).hexdigest()


@dataclass(frozen=True)
class Geometry:
    row_ids: np.ndarray
    segments: np.ndarray
    pages: np.ndarray
    folios: np.ndarray
    sections: np.ndarray
    lengths: np.ndarray
    positions: np.ndarray
    parities: np.ndarray
    primary: np.ndarray
    segment_rows: tuple[np.ndarray, ...]
    segment_folio_indices: np.ndarray
    folio_names: tuple[str, ...]


def load_geometry(path: Path) -> Geometry:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    values = {key: np.asarray([row[key] for row in rows]) for key in ("consensus_group_id", "segment_id", "page", "physical_folio", "section", "segment_position", "folio_parity")}
    lengths = np.asarray([int(row["symbol_count"]) for row in rows], dtype=np.int16)
    primary = np.asarray([row["primary_slot_eligible"] == "1" for row in rows])
    by_segment: dict[str, list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        if primary[index]:
            by_segment[row["segment_id"]].append(index)
    segment_rows = []
    for identifier in sorted(by_segment):
        indices = sorted(by_segment[identifier], key=lambda index: int(rows[index]["segment_group_index"]))
        if len(indices) < 3:
            raise RuntimeError("short primary segment")
        segment_rows.append(np.asarray(indices, dtype=np.int32))
    folio_names = tuple(sorted(set(values["physical_folio"]), key=lambda item: int(item[1:])))
    folio_index = {name: index for index, name in enumerate(folio_names)}
    segment_folio_indices = np.asarray([folio_index[str(values["physical_folio"][indices[0]])] for indices in segment_rows], dtype=np.int16)
    geometry = Geometry(
        row_ids=values["consensus_group_id"], segments=values["segment_id"],
        pages=values["page"], folios=values["physical_folio"],
        sections=values["section"], lengths=lengths,
        positions=values["segment_position"], parities=values["folio_parity"],
        primary=primary, segment_rows=tuple(segment_rows),
        segment_folio_indices=segment_folio_indices, folio_names=folio_names,
    )
    if len(rows) != 5824 or primary.sum() != 5769 or len(segment_rows) != 705 or len(folio_names) != 16:
        raise RuntimeError("LRG002 geometry drift")
    return geometry


def page_length_ranks(scores: np.ndarray, geometry: Geometry) -> np.ndarray:
    if scores.shape != (len(geometry.row_ids),) or not np.isfinite(scores).all():
        raise RuntimeError("invalid score vector")
    output = np.zeros(len(scores), dtype=np.float64)
    cells: dict[tuple[str, int], list[int]] = defaultdict(list)
    for index, key in enumerate(zip(geometry.pages, geometry.lengths, strict=True)):
        cells[(str(key[0]), int(key[1]))].append(index)
    for indices_list in cells.values():
        indices = np.asarray(indices_list, dtype=np.int64)
        values = scores[indices]
        if len(indices) == 1:
            continue
        order = np.argsort(values, kind="mergesort")
        ordered = values[order]
        ranks = np.empty(len(indices), dtype=np.float64)
        start = 0
        while start < len(indices):
            stop = start + 1
            while stop < len(indices) and ordered[stop] == ordered[start]:
                stop += 1
            ranks[order[start:stop]] = (start + stop - 1) / 2.0
            start = stop
        output[indices] = (ranks + 1.0) / (len(indices) + 1.0) - 0.5
    return output


def rotations(geometry: Geometry, ensemble: str) -> np.ndarray:
    rng = np.random.default_rng(SEED + (0 if ensemble == "INDEPENDENT_SEGMENT" else 1))
    lengths = np.asarray([len(indices) for indices in geometry.segment_rows], dtype=np.uint16)
    if ensemble == "INDEPENDENT_SEGMENT":
        shifts = np.floor(rng.random((ASSIGNMENTS, len(lengths))) * lengths[None, :]).astype(np.uint16)
    elif ensemble == "COUPLED_FOLIO":
        clocks = rng.integers(0, 2**31 - 1, size=(ASSIGNMENTS, len(geometry.folio_names)), dtype=np.int64)
        shifts = np.empty((ASSIGNMENTS, len(lengths)), dtype=np.uint16)
        for segment_index, length in enumerate(lengths):
            shifts[:, segment_index] = clocks[:, geometry.segment_folio_indices[segment_index]] % int(length)
    else:
        raise RuntimeError(ensemble)
    if len(np.unique(shifts, axis=0)) != ASSIGNMENTS:
        raise RuntimeError(f"duplicate {ensemble} rotation")
    return shifts


def null_coefficients(geometry: Geometry, shifts: np.ndarray) -> np.ndarray:
    if shifts.shape != (ASSIGNMENTS, len(geometry.segment_rows)):
        raise RuntimeError("rotation shape")
    rows = len(geometry.row_ids); folio_count = len(geometry.folio_names)
    first = np.zeros((ASSIGNMENTS, rows), dtype=np.float64)
    last = np.zeros((ASSIGNMENTS, rows), dtype=np.float64)
    assignment_rows = np.arange(ASSIGNMENTS)
    for folio_index in range(folio_count):
        segment_indices = np.flatnonzero(geometry.segment_folio_indices == folio_index)
        segment_count = len(segment_indices)
        primary_indices = np.concatenate([geometry.segment_rows[index] for index in segment_indices])
        core_count = len(primary_indices) - 2 * segment_count
        if not segment_count or not core_count:
            raise RuntimeError("invalid folio geometry")
        base = -1.0 / (folio_count * core_count)
        first[:, primary_indices] = base
        last[:, primary_indices] = base
        for segment_index in segment_indices:
            positions = geometry.segment_rows[segment_index]
            current = shifts[:, segment_index].astype(np.int64)
            first_indices = positions[current]
            last_indices = positions[(current - 1) % len(positions)]
            first[assignment_rows, first_indices] += 1.0 / (folio_count * segment_count) - base
            first[assignment_rows, last_indices] -= base
            last[assignment_rows, last_indices] += 1.0 / (folio_count * segment_count) - base
            last[assignment_rows, first_indices] -= base
    return np.concatenate((first, last), axis=0)


def cosine(left: np.ndarray, right: np.ndarray) -> float:
    denominator = float(np.linalg.norm(left) * np.linalg.norm(right))
    return float(left @ right / denominator) if denominator > 1e-15 else -1.0


def summarize(ranks: np.ndarray, geometry: Geometry) -> dict[str, object]:
    folio_vectors = {}
    for folio in geometry.folio_names:
        current = geometry.primary & (geometry.folios == folio)
        means = {position: float(ranks[current & (geometry.positions == position)].mean()) for position in ("FIRST", "LAST", "CORE")}
        folio_vectors[folio] = np.asarray([means["FIRST"] - means["CORE"], means["LAST"] - means["CORE"]])
    matrix = np.stack([folio_vectors[folio] for folio in geometry.folio_names])
    overall = matrix.mean(axis=0); norm = float(np.linalg.norm(overall))
    direction = overall / norm if norm > 1e-15 else np.zeros(2)
    folio_projections = matrix @ direction
    sections = {}
    for section in ("B", "P"):
        mask = np.asarray([str(geometry.sections[np.flatnonzero(geometry.folios == folio)[0]]) == section for folio in geometry.folio_names])
        sections[section] = matrix[mask].mean(axis=0)
    parities = {}
    for parity in ("ODD", "EVEN"):
        mask = np.asarray([str(geometry.parities[np.flatnonzero(geometry.folios == folio)[0]]) == parity for folio in geometry.folio_names])
        parities[parity] = matrix[mask].mean(axis=0)
    deletions = np.asarray([(matrix.sum(axis=0) - matrix[index]) / (len(matrix) - 1) @ direction for index in range(len(matrix))])
    denominator = float(np.abs(folio_projections).sum())
    section_projections = {key: float(vector @ direction) for key, vector in sections.items()}
    parity_projections = {key: float(vector @ direction) for key, vector in parities.items()}
    section_max = max(section_projections.values()); parity_max = max(parity_projections.values())
    return {
        "overall_vector": [float(value) for value in overall], "norm": norm,
        "folio_vectors": {folio: [float(value) for value in folio_vectors[folio]] for folio in geometry.folio_names},
        "folio_projections": {folio: float(value) for folio, value in zip(geometry.folio_names, folio_projections, strict=True)},
        "positive_folios": int(np.count_nonzero(folio_projections > 0)),
        "minimum_deletion_projection": float(deletions.min()),
        "maximum_absolute_folio_concentration": float(np.abs(folio_projections).max() / denominator) if denominator else math.inf,
        "section_vectors": {key: [float(value) for value in vector] for key, vector in sections.items()},
        "section_projections": section_projections,
        "section_balance_ratio": min(section_projections.values()) / section_max if section_max > 0 else -math.inf,
        "section_cosine": cosine(sections["B"], sections["P"]),
        "parity_vectors": {key: [float(value) for value in vector] for key, vector in parities.items()},
        "parity_projections": parity_projections,
        "parity_balance_ratio": min(parity_projections.values()) / parity_max if parity_max > 0 else -math.inf,
        "parity_cosine": cosine(parities["ODD"], parities["EVEN"]),
    }


def evaluate(scores: np.ndarray, geometry: Geometry, coefficients: dict[str, np.ndarray]) -> dict[str, object]:
    ranks = page_length_ranks(scores, geometry)
    summary = summarize(ranks, geometry)
    nulls = {}
    pvalues = {}
    for ensemble in ("INDEPENDENT_SEGMENT", "COUPLED_FOLIO"):
        values = coefficients[ensemble] @ ranks
        null = np.hypot(values[:ASSIGNMENTS], values[ASSIGNMENTS:])
        pvalues[ensemble] = (1 + int(np.count_nonzero(null >= summary["norm"]))) / (ASSIGNMENTS + 1)
        nulls[ensemble] = sha256_array(null)
    gates = {
        "both_null_p_at_most_001": all(value <= 0.01 for value in pvalues.values()),
        "norm_at_least_006": summary["norm"] >= 0.06,
        "both_sections_project_at_least_0025": all(value >= 0.025 for value in summary["section_projections"].values()),
        "both_parities_project_at_least_0025": all(value >= 0.025 for value in summary["parity_projections"].values()),
        "section_balance_ratio_at_least_035": summary["section_balance_ratio"] >= 0.35,
        "parity_balance_ratio_at_least_035": summary["parity_balance_ratio"] >= 0.35,
        "section_cosine_at_least_025": summary["section_cosine"] >= 0.25,
        "parity_cosine_at_least_025": summary["parity_cosine"] >= 0.25,
        "positive_folio_support_at_least_12": summary["positive_folios"] >= 12,
        "all_deletions_at_least_0015": summary["minimum_deletion_projection"] >= 0.015,
        "concentration_at_most_025": summary["maximum_absolute_folio_concentration"] <= 0.25,
    }
    return {
        "rank_sha256": sha256_array(ranks), "summary": summary,
        "pvalues": pvalues, "null_sha256": nulls,
        "gates": gates, "passes": all(gates.values()),
    }
