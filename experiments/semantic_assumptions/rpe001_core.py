#!/usr/bin/env python3
"""Pure scoring core for RPE001 radial endpoint polarity."""

from __future__ import annotations

import hashlib
import itertools
import json
import math
from collections import defaultdict
from typing import Iterable


ALPHABET = tuple("ABCDEFGHJKLMNPQTUVWXZ")
FOLIOS = ("f57", "f67", "f68", "f69", "f70")
DIRECTIONS = ("Ri", "Ro")
TOL = 1e-15


def canonical_sha(value: object) -> str:
    return hashlib.sha256(
        (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode()
    ).hexdigest()


def validate_panel(panel: list[dict[str, str]], expected: list[dict[str, object]]) -> None:
    expected_map = {
        str(row["locus"]): (str(row["physical_folio"]), str(row["direction"]))
        for row in expected
    }
    if len(expected_map) != 60 or len(panel) != 60:
        raise ValueError("panel must contain exactly 60 unique expected loci")
    if len({row.get("locus") for row in panel}) != len(panel):
        raise ValueError("duplicate locus")
    actual = {row.get("locus") for row in panel}
    if actual != set(expected_map):
        raise ValueError("missing or extra locus")
    for row in panel:
        locus = row["locus"]
        if (row.get("physical_folio"), row.get("direction")) != expected_map[locus]:
            raise ValueError("folio or direction drift")
        if row.get("center") not in ALPHABET or row.get("outer") not in ALPHABET:
            raise ValueError("unknown endpoint family")


def _equal_folio_effect(rows: Iterable[dict[str, str]], family: str) -> tuple[float, dict[str, float]]:
    values: dict[str, list[int]] = defaultdict(list)
    for row in rows:
        values[row["physical_folio"]].append((row["center"] == family) - (row["outer"] == family))
    folio_effects = {folio: math.fsum(items) / len(items) for folio, items in sorted(values.items())}
    return math.fsum(folio_effects.values()) / len(folio_effects), folio_effects


def score(panel: list[dict[str, str]], expected: list[dict[str, object]]) -> dict[str, object]:
    validate_panel(panel, expected)
    ordered = sorted(panel, key=lambda row: row["locus"])
    effects: dict[str, float] = {}
    by_family_folio: dict[str, dict[str, float]] = {}
    for family in ALPHABET:
        effects[family], by_family_folio[family] = _equal_folio_effect(ordered, family)
    selected = min(ALPHABET, key=lambda family: (-effects[family], family))
    selected_effect = effects[selected]
    M = selected_effect

    null_M: list[float] = []
    for bits in itertools.product((1, -1), repeat=len(FOLIOS)):
        signs = dict(zip(FOLIOS, bits, strict=True))
        null_M.append(max(math.fsum(signs[f] * by_family_folio[family][f] for f in FOLIOS) / 5 for family in ALPHABET))
    p = sum(value >= M - TOL for value in null_M) / len(null_M)

    direction_effects: dict[str, float] = {}
    direction_folio_effects: dict[str, dict[str, float]] = {}
    for direction in DIRECTIONS:
        subset = [row for row in ordered if row["direction"] == direction]
        direction_effects[direction], direction_folio_effects[direction] = _equal_folio_effect(subset, selected)
    support = {
        direction: sum(value > 0 for value in direction_folio_effects[direction].values())
        for direction in DIRECTIONS
    }
    selected_folio = by_family_folio[selected]
    loo = {
        deleted: math.fsum(selected_folio[f] for f in FOLIOS if f != deleted) / 4
        for deleted in FOLIOS
    }
    denominator = math.fsum(abs(value) for value in selected_folio.values())
    concentration = max(abs(value) for value in selected_folio.values()) / denominator if denominator else 1.0
    gates = {
        "material_and_exact_maxT": M >= .10 - TOL and p <= .05 + TOL,
        "Ri_Ro_physical_direction_coherence": all(direction_effects[d] > 0 for d in DIRECTIONS),
        "Ri_support_at_least_3_of_4_folios": support["Ri"] >= 3,
        "Ro_support_at_least_3_of_4_folios": support["Ro"] >= 3,
        "all_LOO_center_effect_at_least_005": all(value >= .05 - TOL for value in loo.values()),
        "folio_concentration_at_most_050": concentration <= .50 + TOL,
        "finite": all(math.isfinite(value) for value in [*effects.values(), *null_M, *direction_effects.values(), *loo.values(), concentration]),
    }
    return {
        "panel_sha256": canonical_sha(ordered),
        "alphabet": "".join(ALPHABET),
        "selected_family": selected,
        "selected_polarity": "CENTER",
        "selected_effect": selected_effect,
        "M": M,
        "exact_maxT_p": p,
        "all_family_effects": effects,
        "all_family_folio_effects": by_family_folio,
        "direction_effects": direction_effects,
        "direction_folio_effects": direction_folio_effects,
        "direction_support": support,
        "leave_one_folio_out": loo,
        "concentration": concentration,
        "null_M": null_M,
        "null_M_sha256": canonical_sha(null_M),
        "gates": gates,
        "passes": all(gates.values()),
    }


def make_world(expected: list[dict[str, object]], world: int, mode: str) -> list[dict[str, str]]:
    if not 0 <= world < 8:
        raise ValueError("world")
    candidate = ALPHABET[world]
    panel: list[dict[str, str]] = []
    for index, meta in enumerate(sorted(expected, key=lambda row: str(row["locus"]))):
        background = ALPHABET[(world + 1 + index) % len(ALPHABET)]
        if background == candidate:
            background = ALPHABET[(ALPHABET.index(background) + 1) % len(ALPHABET)]
        center = outer = background
        direction = str(meta["direction"])
        folio = str(meta["physical_folio"])
        if mode == "DISTRIBUTED_CENTER":
            center = candidate
        elif mode == "NULL":
            pass
        elif mode == "ONE_FOLIO":
            if folio == "f68":
                center = candidate
        elif mode == "TEXT_START_ONLY":
            if direction == "Ro":
                center = candidate
            else:
                outer = candidate
        elif mode == "TEXT_END_ONLY":
            if direction == "Ri":
                center = candidate
            else:
                outer = candidate
        elif mode == "ONE_DIRECTION_ONLY":
            if direction == "Ri":
                center = candidate
        else:
            raise ValueError(mode)
        panel.append({
            "locus": str(meta["locus"]),
            "physical_folio": folio,
            "direction": direction,
            "center": center,
            "outer": outer,
        })
    validate_panel(panel, expected)
    return panel
