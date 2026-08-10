#!/usr/bin/env python3
"""Blockwise-intersection v2 scorer for cho/che co-switching."""

from __future__ import annotations

import itertools
from dataclasses import dataclass

import numpy as np

from cho_che_coswitch_core import (
    BLOCKS, BLOCK_DIMS, LEAVES, READINGS, Score, _mean_pairwise, _unit, score as score_v1,
)


@dataclass(frozen=True)
class ScoreV2:
    base: Score
    block_primary: tuple[float, ...]
    block_p_value: tuple[float, ...]
    exact_block_passes: int
    passes: bool


def score(block_vectors: tuple[np.ndarray, ...]) -> ScoreV2:
    base = score_v1(block_vectors)
    primaries = []
    p_values = []
    for values, dim in zip(block_vectors, BLOCK_DIMS):
        array = np.asarray(values, dtype=np.float64)
        if array.shape != (len(READINGS), len(LEAVES), dim):
            raise ValueError("block shape")
        units = _unit(array)
        primary = min(_mean_pairwise(units[edition]) for edition in range(len(READINGS)))
        null = []
        for signs in itertools.product((-1.0, 1.0), repeat=len(LEAVES)):
            sign = np.asarray(signs, dtype=np.float64)[None, :, None]
            null.append(min(_mean_pairwise((units * sign)[edition]) for edition in range(len(READINGS))))
        null_array = np.asarray(null)
        primaries.append(primary)
        p_values.append(float(np.count_nonzero(null_array >= primary - 1e-15) / len(null_array)))
    exact = sum(primary >= .10 and p_value <= .01 for primary, p_value in zip(primaries, p_values))
    passes = bool(
        base.primary >= .10
        and base.p_value <= .01
        and min(base.positive_held) >= 7
        and min(base.min_deletion) > 0
        and min(base.orientation_cross) > 0
        and min(base.domain_cross) > 0
        and base.reading_agreement >= .40
        and max(base.max_concentration) <= .30
        and exact >= 2
    )
    return ScoreV2(base, tuple(primaries), tuple(p_values), exact, passes)


def compact(value: ScoreV2) -> dict:
    from cho_che_coswitch_core import compact as compact_v1
    result = compact_v1(value.base)
    result["v1_passes"] = result.pop("passes")
    result.update({
        "block_primary": list(value.block_primary),
        "block_p_value": list(value.block_p_value),
        "exact_block_passes": value.exact_block_passes,
        "passes": value.passes,
    })
    return result
