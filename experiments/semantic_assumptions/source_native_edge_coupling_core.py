#!/usr/bin/env python3
"""Target-blind scorer for source-native opening/closing edge coupling."""

from __future__ import annotations

import csv
import hashlib
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np


ALPHABET = tuple("ABCDEFGHJKLMNPQRSTUVWXYZ")
ALPHABET_INDEX = {value: index for index, value in enumerate(ALPHABET)}
ALPHA = 0.5
FIELDS = (
    "unit_id", "consensus_group_id", "locus", "page", "physical_folio",
    "section", "currier", "hand", "kind", "locus_position", "symbol_count",
    "length_bin", "opening_family", "core_first_family", "core_last_family",
    "baseline_cell", "full_cell", "masked_family_surface",
    "outside_folio_baseline_support", "outside_folio_full_support", "target_eligible",
)


def stable_u64(text: str) -> int:
    return int.from_bytes(hashlib.sha256(text.encode()).digest()[:8], "little")


@dataclass
class Panel:
    rows: list[dict]
    baseline_index: np.ndarray
    full_index: np.ndarray
    baseline_keys: tuple[str, ...]
    full_keys: tuple[str, ...]
    folio_values: tuple[str, ...]
    folio_rows: tuple[np.ndarray, ...]
    eligible: np.ndarray


def load_panel(path: Path) -> Panel:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("edge-coupling masked schema drift")
        rows = list(reader)
    if len(rows) != 19203 or len({row["unit_id"] for row in rows}) != 19203:
        raise ValueError("edge-coupling masked row drift")
    if any(row["masked_family_surface"].count("#") != 1 for row in rows):
        raise ValueError("edge-coupling mask drift")
    baseline_keys = tuple(sorted({row["baseline_cell"] for row in rows}))
    full_keys = tuple(sorted({row["full_cell"] for row in rows}))
    baseline_map = {key: index for index, key in enumerate(baseline_keys)}
    full_map = {key: index for index, key in enumerate(full_keys)}
    folio_values = tuple(sorted({row["physical_folio"] for row in rows}, key=lambda value: int(value[1:])))
    folio_rows = tuple(np.asarray([i for i, row in enumerate(rows) if row["physical_folio"] == folio], dtype=np.int64) for folio in folio_values)
    return Panel(
        rows=rows,
        baseline_index=np.asarray([baseline_map[row["baseline_cell"]] for row in rows], dtype=np.int64),
        full_index=np.asarray([full_map[row["full_cell"]] for row in rows], dtype=np.int64),
        baseline_keys=baseline_keys, full_keys=full_keys, folio_values=folio_values,
        folio_rows=folio_rows,
        eligible=np.asarray([row["target_eligible"] == "1" for row in rows], dtype=bool),
    )


def exact_sign_p(positive: int, total: int) -> float:
    return sum(math.comb(total, k) for k in range(positive, total + 1)) / (2 ** total)


def score(panel: Panel, outcomes: np.ndarray) -> dict:
    if outcomes.shape != (len(panel.rows),) or outcomes.dtype.kind not in "iu" or np.any((outcomes < 0) | (outcomes >= len(ALPHABET))):
        raise ValueError("invalid closing-family outcome vector")
    base_counts = np.zeros((len(panel.baseline_keys), len(ALPHABET)), dtype=np.int64)
    full_counts = np.zeros((len(panel.full_keys), len(ALPHABET)), dtype=np.int64)
    np.add.at(base_counts, (panel.baseline_index, outcomes), 1)
    np.add.at(full_counts, (panel.full_index, outcomes), 1)

    gains = np.full(len(panel.rows), np.nan, dtype=np.float64)
    folio_effects = []
    folio_counts = []
    currier_gains: dict[str, list[float]] = defaultdict(list)
    folio_currier_effects: dict[str, list[float]] = defaultdict(list)
    for folio, indices in zip(panel.folio_values, panel.folio_rows):
        held_base = np.zeros_like(base_counts)
        held_full = np.zeros_like(full_counts)
        np.add.at(held_base, (panel.baseline_index[indices], outcomes[indices]), 1)
        np.add.at(held_full, (panel.full_index[indices], outcomes[indices]), 1)
        train_base = base_counts - held_base
        train_full = full_counts - held_full
        eligible = indices[panel.eligible[indices]]
        if len(eligible) == 0:
            continue
        local_values = []
        local_currier: dict[str, list[float]] = defaultdict(list)
        for index in eligible:
            outcome = outcomes[index]
            b = panel.baseline_index[index]
            f = panel.full_index[index]
            base_total = int(train_base[b].sum())
            full_total = int(train_full[f].sum())
            if base_total < 20 or full_total < 5:
                raise ValueError("frozen leave-folio support gate drift")
            p_base = (train_base[b, outcome] + ALPHA) / (base_total + ALPHA * len(ALPHABET))
            p_full = (train_full[f, outcome] + ALPHA) / (full_total + ALPHA * len(ALPHABET))
            gain = math.log(p_full / p_base)
            gains[index] = gain
            local_values.append(gain)
            currier = panel.rows[index]["currier"]
            local_currier[currier].append(gain)
            currier_gains[currier].append(gain)
        folio_effects.append(float(np.mean(local_values)))
        folio_counts.append(len(local_values))
        for currier, values in local_currier.items():
            folio_currier_effects[currier].append(float(np.mean(values)))
    folio_effects_array = np.asarray(folio_effects)
    total_abs = float(np.abs(folio_effects_array).sum())
    deletion = (folio_effects_array.sum() - folio_effects_array) / (len(folio_effects_array) - 1)

    currier = {}
    for key in ("A", "B"):
        values = np.asarray(folio_currier_effects[key])
        currier[key] = {
            "effect_equal_folio": float(values.mean()),
            "positive_folios": int((values > 0).sum()),
            "folios": len(values),
            "sign_p": exact_sign_p(int((values > 0).sum()), len(values)),
            "minimum_leave_one_folio_out": float(((values.sum() - values) / (len(values) - 1)).min()),
        }
    return {
        "eligible_rows": int(np.isfinite(gains).sum()),
        "physical_folios": len(folio_effects_array),
        "effect_equal_folio": float(folio_effects_array.mean()),
        "effect_equal_row": float(np.nanmean(gains)),
        "positive_folios": int((folio_effects_array > 0).sum()),
        "sign_p": exact_sign_p(int((folio_effects_array > 0).sum()), len(folio_effects_array)),
        "minimum_leave_one_folio_out": float(deletion.min()),
        "max_abs_contribution_fraction": float(np.abs(folio_effects_array).max() / total_abs) if total_abs else 1.0,
        "currier": currier,
    }


def synthetic_outcomes(panel: Panel, world: int, mode: str, strength: float = 0.0) -> np.ndarray:
    outcomes = np.empty(len(panel.rows), dtype=np.int64)
    for index, row in enumerate(panel.rows):
        base_first = stable_u64(f"EDGE|{world}|BASE1|{row['baseline_cell']}") % len(ALPHABET)
        base_second = stable_u64(f"EDGE|{world}|BASE2|{row['baseline_cell']}") % len(ALPHABET)
        u = (stable_u64(f"EDGE|{world}|BASEU|{row['unit_id']}") + .5) / (1 << 64)
        if u < .45:
            outcome = base_first
        elif u < .70:
            outcome = base_second
        else:
            outcome = stable_u64(f"EDGE|{world}|BASER|{row['unit_id']}") % len(ALPHABET)
        if mode in {"COUPLED", "ONE_FOLIO", "FOLIO_RANDOM"}:
            active = mode != "ONE_FOLIO" or row["physical_folio"] == panel.folio_values[world % len(panel.folio_values)]
            coupling_u = (stable_u64(f"EDGE|{world}|COUPLEU|{row['unit_id']}") + .5) / (1 << 64)
            if active and coupling_u < strength:
                domain = row["opening_family"] if mode != "FOLIO_RANDOM" else f"{row['physical_folio']}|{row['opening_family']}"
                outcome = stable_u64(f"EDGE|{world}|MAP|{domain}") % len(ALPHABET)
        elif mode != "NULL":
            raise ValueError("unknown synthetic edge-coupling mode")
        outcomes[index] = outcome
    return outcomes


def passes(result: dict) -> bool:
    return (
        result["eligible_rows"] == 14955
        and result["physical_folios"] == 94
        and result["effect_equal_folio"] >= 0.02
        and result["positive_folios"] >= 65
        and result["sign_p"] <= 0.01
        and result["minimum_leave_one_folio_out"] > 0.0
        and result["max_abs_contribution_fraction"] <= 0.08
        and all(
            result["currier"][key]["effect_equal_folio"] >= 0.01
            and result["currier"][key]["minimum_leave_one_folio_out"] > 0.0
            and result["currier"][key]["positive_folios"] / result["currier"][key]["folios"] >= 0.60
            for key in ("A", "B")
        )
    )
