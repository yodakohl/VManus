#!/usr/bin/env python3
"""Frozen scoring core for the cho/che independent co-switch route."""

from __future__ import annotations

import itertools
from dataclasses import dataclass

import numpy as np

READINGS = ("ZL3b", "IT2a", "RF1b")
LEAVES = ("f39", "f55", "f68", "f73", "f87", "f89", "f90", "f96")
BLOCKS = ("FAMILY_RATE", "ENDPOINT_RATE", "BIGRAM_RATE")
BLOCK_DIMS = (24, 48, 576)
HIGH_RECTO = np.asarray([False, True, True, False, True, False, True, True], dtype=bool)
DIAGNOSTIC = np.asarray([False, False, True, True, False, True, False, False], dtype=bool)


@dataclass(frozen=True)
class Score:
    primary: float
    p_value: float
    reading_alignment: tuple[float, ...]
    positive_held: tuple[int, ...]
    min_deletion: tuple[float, ...]
    orientation_cross: tuple[float, ...]
    domain_cross: tuple[float, ...]
    reading_agreement: float
    max_concentration: tuple[float, ...]
    positive_blocks: tuple[int, ...]
    passes: bool


def _unit(values: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(values, axis=-1, keepdims=True)
    if not np.isfinite(values).all() or np.any(norms <= 0):
        raise ValueError("nonfinite or zero vector")
    return values / norms


def _mean_pairwise(units: np.ndarray) -> float:
    count = units.shape[0]
    values = [float(units[i] @ units[j]) for i in range(count) for j in range(i + 1, count)]
    return float(np.mean(values))


def _cosine(left: np.ndarray, right: np.ndarray) -> float:
    ln, rn = float(np.linalg.norm(left)), float(np.linalg.norm(right))
    if ln <= 0 or rn <= 0:
        return -1.0
    return float(left @ right / (ln * rn))


def score(block_vectors: tuple[np.ndarray, ...]) -> Score:
    if len(block_vectors) != len(BLOCKS):
        raise ValueError("block count")
    units_by_block = []
    for block, dim in zip(block_vectors, BLOCK_DIMS):
        values = np.asarray(block, dtype=np.float64)
        if values.shape != (len(READINGS), len(LEAVES), dim):
            raise ValueError("block shape")
        units_by_block.append(_unit(values))
    combined = np.concatenate([values / np.sqrt(len(BLOCKS)) for values in units_by_block], axis=2)
    combined = _unit(combined)

    alignments = tuple(_mean_pairwise(combined[e]) for e in range(len(READINGS)))
    primary = min(alignments)
    null_values = []
    for signs in itertools.product((-1.0, 1.0), repeat=len(LEAVES)):
        sign = np.asarray(signs, dtype=np.float64)[None, :, None]
        null_values.append(min(_mean_pairwise((combined * sign)[e]) for e in range(len(READINGS))))
    null_array = np.asarray(null_values, dtype=np.float64)
    p_value = float(np.count_nonzero(null_array >= primary - 1e-15) / len(null_array))

    positive_held = []
    min_deletion = []
    orientation_cross = []
    domain_cross = []
    max_concentration = []
    positive_blocks = []
    for edition in range(len(READINGS)):
        values = combined[edition]
        held = []
        deletions = []
        for index in range(len(LEAVES)):
            other = np.delete(values, index, axis=0)
            held.append(_cosine(values[index], np.mean(other, axis=0)))
            deletions.append(_mean_pairwise(other))
        positive_held.append(sum(value > 0 for value in held))
        min_deletion.append(min(deletions))
        orientation_cross.append(_cosine(np.mean(values[HIGH_RECTO], axis=0), np.mean(values[~HIGH_RECTO], axis=0)))
        domain_cross.append(_cosine(np.mean(values[DIAGNOSTIC], axis=0), np.mean(values[~DIAGNOSTIC], axis=0)))
        leaf_alignment = np.asarray([np.mean([float(values[i] @ values[j]) for j in range(len(LEAVES)) if j != i]) for i in range(len(LEAVES))])
        positive_mass = np.maximum(leaf_alignment, 0.0)
        max_concentration.append(float(np.max(positive_mass) / np.sum(positive_mass)) if np.sum(positive_mass) > 0 else 1.0)
        positive_blocks.append(sum(_mean_pairwise(block[edition]) > 0 for block in units_by_block))

    agreement_values = []
    for leaf in range(len(LEAVES)):
        for left in range(len(READINGS)):
            for right in range(left + 1, len(READINGS)):
                agreement_values.append(float(combined[left, leaf] @ combined[right, leaf]))
    reading_agreement = float(np.mean(agreement_values))
    passes = bool(
        primary >= .10
        and p_value <= .01
        and min(positive_held) >= 7
        and min(min_deletion) > 0
        and min(orientation_cross) > 0
        and min(domain_cross) > 0
        and reading_agreement >= .40
        and max(max_concentration) <= .30
        and min(positive_blocks) >= 2
    )
    return Score(
        primary=primary,
        p_value=p_value,
        reading_alignment=alignments,
        positive_held=tuple(positive_held),
        min_deletion=tuple(min_deletion),
        orientation_cross=tuple(orientation_cross),
        domain_cross=tuple(domain_cross),
        reading_agreement=reading_agreement,
        max_concentration=tuple(max_concentration),
        positive_blocks=tuple(positive_blocks),
        passes=passes,
    )


def compact(value: Score) -> dict:
    return {
        "primary": value.primary,
        "p_value": value.p_value,
        "reading_alignment": list(value.reading_alignment),
        "positive_held": list(value.positive_held),
        "min_deletion": list(value.min_deletion),
        "orientation_cross": list(value.orientation_cross),
        "domain_cross": list(value.domain_cross),
        "reading_agreement": value.reading_agreement,
        "max_concentration": list(value.max_concentration),
        "positive_blocks": list(value.positive_blocks),
        "passes": value.passes,
    }
