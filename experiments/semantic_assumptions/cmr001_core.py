#!/usr/bin/env python3
"""Scientific core for CMR001 circle-marker reset testing."""

from __future__ import annotations

import hashlib
import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Iterable

import numpy as np


READINGS = ("ZL3b", "IT2a", "RF1b")
ASSIGNMENTS = 65_536
TOL = 1e-15


def token_features(word: str) -> tuple[str, ...]:
    if not word:
        raise ValueError("empty STA family word")
    return (
        f"LEN={min(len(word), 12)}",
        f"P1={word[:1]}", f"P2={word[:2]}", f"P3={word[:3]}",
        f"S1={word[-1:]}", f"S2={word[-2:]}", f"S3={word[-3:]}",
    )


@dataclass(frozen=True)
class NBModel:
    class_counts: tuple[int, int]
    field_vocab: tuple[frozenset[str], ...]
    value_counts: tuple[tuple[Counter[str], ...], tuple[Counter[str], ...]]

    def score(self, word: str) -> float:
        features = token_features(word)
        answer = 0.0
        for field, value in enumerate(features):
            vocab_size = len(self.field_vocab[field]) + 1
            for cls, sign in ((1, 1.0), (0, -1.0)):
                count = self.value_counts[cls][field].get(value, 0)
                denom = self.class_counts[cls] + vocab_size
                answer += sign * math.log((count + 1.0) / denom)
        return answer


def fit_nb(examples: Iterable[tuple[str, int]]) -> NBModel:
    counts = [0, 0]
    value_counts = [[Counter() for _ in range(7)] for _ in range(2)]
    vocab = [set() for _ in range(7)]
    for word, label in examples:
        if label not in (0, 1):
            raise ValueError("binary label required")
        counts[label] += 1
        for field, value in enumerate(token_features(word)):
            value_counts[label][field][value] += 1
            vocab[field].add(value)
    if not counts[0] or not counts[1]:
        raise ValueError("both classes required")
    return NBModel(
        class_counts=(counts[0], counts[1]),
        field_vocab=tuple(frozenset(values) for values in vocab),
        value_counts=(tuple(value_counts[0]), tuple(value_counts[1])),
    )


def tied_auc(labels: list[int], scores: list[float]) -> float:
    if len(labels) != len(scores) or not labels:
        raise ValueError("invalid AUC inputs")
    positives = sum(labels)
    negatives = len(labels) - positives
    if positives == 0 or negatives == 0:
        raise ValueError("AUC needs both classes")
    order = sorted(range(len(scores)), key=lambda i: scores[i])
    rank_sum = 0.0
    rank = 1
    start = 0
    while start < len(order):
        end = start + 1
        while end < len(order) and scores[order[end]] == scores[order[start]]:
            end += 1
        average_rank = (rank + (rank + end - start - 1)) / 2.0
        rank_sum += average_rank * sum(labels[order[i]] for i in range(start, end))
        rank += end - start
        start = end
    return (rank_sum - positives * (positives + 1) / 2.0) / (positives * negatives)


def centered_percentiles(scores: np.ndarray) -> np.ndarray:
    values = np.asarray(scores, dtype=np.float64)
    if values.ndim != 1 or not len(values) or not np.isfinite(values).all():
        raise ValueError("finite nonempty score vector required")
    answer = np.empty(len(values), dtype=np.float64)
    for i, value in enumerate(values):
        answer[i] = (np.sum(values < value) + 0.5 * np.sum(values == value)) / len(values) - 0.5
    return answer


def phase_u(locus: str, assignments: int = ASSIGNMENTS) -> np.ndarray:
    result = np.empty(assignments, dtype=np.float64)
    denom = float(2**64)
    for assignment in range(assignments):
        payload = f"CMR001_PHASE_V1|{assignment}|{locus}".encode("ascii")
        integer = int.from_bytes(hashlib.sha256(payload).digest()[:8], "big", signed=False)
        result[assignment] = integer / denom
    return result


def array_sha(array: np.ndarray) -> str:
    value = np.ascontiguousarray(array, dtype="<f8")
    return hashlib.sha256(value.tobytes(order="C")).hexdigest()


def index_sha(array: np.ndarray) -> str:
    value = np.ascontiguousarray(array, dtype="<i8")
    return hashlib.sha256(value.tobytes(order="C")).hexdigest()


def evaluate_panel(
    score_arrays: dict[str, dict[str, np.ndarray]],
    folio_by_locus: dict[str, str],
    observed_indices: dict[str, dict[str, int]] | None = None,
    assignments: int = ASSIGNMENTS,
) -> dict[str, object]:
    if tuple(score_arrays) != READINGS:
        raise ValueError("canonical reading order required")
    loci = sorted(folio_by_locus)
    if not loci:
        raise ValueError("empty panel")
    if any(set(score_arrays[edition]) != set(loci) for edition in READINGS):
        raise ValueError("reading locus sets differ")
    if observed_indices is None:
        observed_indices = {edition: {locus: 0 for locus in loci} for edition in READINGS}
    if any(set(observed_indices[edition]) != set(loci) for edition in READINGS):
        raise ValueError("observed index sets differ")
    folios = sorted(set(folio_by_locus.values()))
    loci_by_folio = {folio: [locus for locus in loci if folio_by_locus[locus] == folio] for folio in folios}

    percentiles: dict[str, dict[str, np.ndarray]] = {edition: {} for edition in READINGS}
    canonical_percentiles: dict[str, dict[str, np.ndarray]] = {edition: {} for edition in READINGS}
    u = {locus: phase_u(locus, assignments) for locus in loci}
    indices: dict[str, dict[str, np.ndarray]] = {edition: {} for edition in READINGS}
    relative_indices: dict[str, dict[str, np.ndarray]] = {edition: {} for edition in READINGS}
    observed: dict[str, dict[str, float]] = {edition: {} for edition in READINGS}
    null_by_reading = np.empty((assignments, len(READINGS)), dtype=np.float64)
    folio_effects: dict[str, dict[str, float]] = {edition: {} for edition in READINGS}

    for edition_index, edition in enumerate(READINGS):
        locus_null = {}
        for locus in loci:
            scores = np.asarray(score_arrays[edition][locus], dtype=np.float64)
            ranks = centered_percentiles(scores)
            percentiles[edition][locus] = ranks
            start = int(observed_indices[edition][locus])
            if not 0 <= start < len(ranks):
                raise ValueError("observed index out of range")
            observed[edition][locus] = float(ranks[start])
            chosen = (start + np.floor(u[locus] * len(ranks)).astype(np.int64)) % len(ranks)
            indices[edition][locus] = chosen
            canonical_percentiles[edition][locus] = np.roll(ranks, -start)
            relative_indices[edition][locus] = (chosen - start) % len(ranks)
            locus_null[locus] = ranks[chosen]
        for folio in folios:
            values = [observed[edition][locus] for locus in loci_by_folio[folio]]
            folio_effects[edition][folio] = float(np.mean(values))
        null_folios = [
            np.mean(np.vstack([locus_null[locus] for locus in loci_by_folio[folio]]), axis=0)
            for folio in folios
        ]
        null_by_reading[:, edition_index] = np.mean(np.vstack(null_folios), axis=0)

    T = {edition: float(np.mean(list(folio_effects[edition].values()))) for edition in READINGS}
    M = min(T.values())
    null_M = np.min(null_by_reading, axis=1)
    p = (1 + int(np.sum(null_M >= M - TOL))) / (assignments + 1)
    loo = {}
    for deleted in folios:
        loo[deleted] = min(
            float(np.mean([value for folio, value in folio_effects[edition].items() if folio != deleted]))
            for edition in READINGS
        )
    support = {
        edition: sum(value > 0 for value in folio_effects[edition].values())
        for edition in READINGS
    }
    concentration = {}
    for edition in READINGS:
        absolute = [abs(value) for value in folio_effects[edition].values()]
        concentration[edition] = max(absolute) / sum(absolute) if sum(absolute) else 1.0
    return {
        "loci": loci,
        "folios": folios,
        "T_by_reading": T,
        "M": M,
        "p": p,
        "folio_effects": folio_effects,
        "positive_folios_by_reading": support,
        "leave_one_folio_out_M": loo,
        "concentration_by_reading": concentration,
        "null_M": null_M,
        "null_by_reading": null_by_reading,
        "digests": {
            "null_M_sha256": array_sha(null_M),
            "null_by_reading_sha256": array_sha(null_by_reading),
            "canonical_percentile_arrays_sha256": hashlib.sha256("".join(
                array_sha(canonical_percentiles[edition][locus]) for edition in READINGS for locus in loci
            ).encode("ascii")).hexdigest(),
            "relative_assignment_indices_sha256": hashlib.sha256("".join(
                index_sha(relative_indices[edition][locus]) for edition in READINGS for locus in loci
            ).encode("ascii")).hexdigest(),
        },
    }


def primary_gates(panel: dict[str, object], magnitude: float) -> dict[str, bool]:
    return {
        "magnitude": float(panel["M"]) >= magnitude,
        "p": float(panel["p"]) <= 0.05,
        "all_readings_positive": all(value > 0 for value in panel["T_by_reading"].values()),
        "five_of_six_folios_each_reading": all(
            value >= 5 for value in panel["positive_folios_by_reading"].values()
        ),
        "all_leave_one_folio_out_above_005": all(
            value > 0.05 for value in panel["leave_one_folio_out_M"].values()
        ),
        "concentration_at_most_035": all(
            value <= 0.35 for value in panel["concentration_by_reading"].values()
        ),
    }
