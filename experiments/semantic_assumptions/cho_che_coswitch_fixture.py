#!/usr/bin/env python3
"""Frozen target-free geometry and synthetic worlds for co-switch calibration."""

from __future__ import annotations

import csv
import hashlib
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from cho_che_coswitch_core import BLOCK_DIMS, DIAGNOSTIC, HIGH_RECTO, LEAVES, READINGS

FIELDS = (
    "source_group_id", "edition", "locus", "page", "collapsed_page",
    "physical_folio", "side", "page_state", "section", "currier", "hand",
    "kind", "grammar_scope", "primary_sta_symbol_count",
    "page_position_quartile", "group_position_class",
)
NUISANCE = (
    "section", "currier", "hand", "kind", "grammar_scope",
    "primary_sta_symbol_count", "page_position_quartile", "group_position_class",
)
FAMILIES = {
    "NULL": (64, 0.0),
    "DISTRIBUTED_THREE_BLOCK": (8, .75),
    "DISTRIBUTED_TWO_BLOCK": (8, .75),
    "ONE_LEAF": (8, 1.0),
    "ONE_READING": (8, 1.0),
    "OPPOSITE_READING": (8, 1.0),
    "SIDE_ONLY": (8, 1.0),
    "DIAGNOSTIC_ONLY": (8, 1.0),
    "PROSE_ONLY": (8, 1.0),
    "ONE_BLOCK": (8, 1.0),
}


def stable_seed(*parts: object) -> int:
    return int.from_bytes(hashlib.sha256("|".join(map(str, parts)).encode()).digest()[:8], "little")


def geometry(panel: Path) -> tuple[np.ndarray, dict, Counter]:
    with panel.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("panel schema")
        rows = list(reader)
    if len(rows) != 5012 or len({row["source_group_id"] for row in rows}) != len(rows):
        raise ValueError("panel identity")
    grouped = defaultdict(list)
    for row in rows:
        cell = tuple(row[field] for field in NUISANCE)
        grouped[(row["edition"], row["physical_folio"], row["side"], cell)].append(row["source_group_id"])
    shared = {}
    scale = np.zeros((len(READINGS), len(LEAVES)), dtype=np.float64)
    side_rows = Counter()
    for edition_index, edition in enumerate(READINGS):
        for leaf_index, leaf in enumerate(LEAVES):
            recto = {key[3] for key, values in grouped.items() if key[:3] == (edition, leaf, "r") and len(values) >= 2}
            verso = {key[3] for key, values in grouped.items() if key[:3] == (edition, leaf, "v") and len(values) >= 2}
            cells = sorted(recto & verso)
            if not cells:
                raise ValueError("empty nuisance overlap")
            shared[(edition, leaf)] = cells
            variance = 0.0
            for cell in cells:
                nr, nv = len(grouped[(edition, leaf, "r", cell)]), len(grouped[(edition, leaf, "v", cell)])
                side_rows[(edition, leaf, "r")] += nr
                side_rows[(edition, leaf, "v")] += nv
                variance += 1 / nr + 1 / nv
            scale[edition_index, leaf_index] = np.sqrt(variance / len(cells) ** 2)
    if len(shared) != 24 or sum(map(len, shared.values())) != 272 or sum(side_rows.values()) != 2730:
        raise ValueError("frozen geometry")
    return scale, shared, side_rows


def make_world(noise_scale: np.ndarray, family: str, world: int, strength: float) -> tuple[np.ndarray, ...]:
    directions = []
    for block_index, dim in enumerate(BLOCK_DIMS):
        rng = np.random.default_rng(stable_seed("CCSW001", family, world, "DIRECTION", block_index))
        direction = rng.normal(size=dim)
        direction /= np.linalg.norm(direction)
        directions.append(direction)
    vectors = []
    for block_index, dim in enumerate(BLOCK_DIMS):
        block = np.zeros((len(READINGS), len(LEAVES), dim), dtype=np.float64)
        for leaf_index, leaf in enumerate(LEAVES):
            shared_rng = np.random.default_rng(stable_seed("CCSW001", family, world, "SHARED", block_index, leaf))
            shared_noise = shared_rng.normal(size=dim)
            for edition_index, edition in enumerate(READINGS):
                own_rng = np.random.default_rng(stable_seed("CCSW001", family, world, "READING", block_index, leaf, edition))
                noise = np.sqrt(.8) * shared_noise + np.sqrt(.2) * own_rng.normal(size=dim)
                scale = noise_scale[edition_index, leaf_index]
                block[edition_index, leaf_index] = scale * noise
                active, sign = True, 1.0
                if family == "NULL": active = False
                elif family == "ONE_LEAF": active = leaf_index == 0
                elif family == "ONE_READING": active = edition_index == 0
                elif family == "OPPOSITE_READING": sign = -1.0 if edition_index == 2 else 1.0
                elif family == "SIDE_ONLY": sign = 1.0 if HIGH_RECTO[leaf_index] else -1.0
                elif family == "DIAGNOSTIC_ONLY": active = bool(DIAGNOSTIC[leaf_index])
                elif family == "PROSE_ONLY": active = not bool(DIAGNOSTIC[leaf_index])
                elif family == "ONE_BLOCK": active = block_index == 0
                elif family == "DISTRIBUTED_TWO_BLOCK": active = block_index in (0, 2)
                elif family == "DISTRIBUTED_THREE_BLOCK": active = True
                else: raise ValueError("world family")
                if active:
                    block[edition_index, leaf_index] += sign * strength * scale * np.sqrt(dim) * directions[block_index]
        vectors.append(block)
    return tuple(vectors)
