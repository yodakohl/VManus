#!/usr/bin/env python3
"""Run the frozen GDT370 synthetic acquisition-capacity calibration."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt370_grounding_acquisition_power"
ART = BASE / "artifacts"
SEED = 37020260819
TRIALS = 256
LIBRARY = 81
FOLIOS = (4, 6, 8, 10, 12)
ARRAYS_PER_FOLIO = (1, 2)
CELLS_PER_ARRAY = (6, 9)
BETAS = {"NULL": 0.0, "WEAK": 0.5, "MEDIUM": 0.9, "STRONG": 1.3}
MODES = ("STABLE", "REVERSING")
SELECTOR_COST = math.log2(LIBRARY)
INPUTS = (
    ROOT / "experiments/yolo/gdt368_quantitative_component_geometry/artifacts/gdt368_result.json",
    ROOT / "experiments/yolo/gdt369_order_preserving_geometry_null/artifacts/gdt369_result.json",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def logit(p: np.ndarray | float) -> np.ndarray:
    p = np.asarray(p)
    return np.log(p / (1.0 - p))


def logistic(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def ll_binary(x: np.ndarray, p: np.ndarray) -> np.ndarray:
    return x * np.log2(p) + (1 - x) * np.log2(1 - p)


def trial(
    rng: np.random.Generator,
    folios: int,
    arrays_per_folio: int,
    cells_per_array: int,
    beta: float,
    mode: str,
) -> dict[str, float | int | bool]:
    n_arrays = folios * arrays_per_folio
    n = n_arrays * cells_per_array
    folio = np.repeat(np.arange(folios), arrays_per_folio * cells_per_array)
    array = np.repeat(np.arange(n_arrays), cells_per_array)

    # Balanced state counts are independently shuffled inside every array.
    base = np.tile(np.arange(3), cells_per_array // 3)
    state = np.concatenate([rng.permutation(base) for _ in range(n_arrays)])

    base_p = rng.beta(2.0, 2.0, size=LIBRARY)
    base_p = np.clip(base_p, 0.10, 0.90)
    folio_shift = rng.normal(0.0, 0.50, size=(folios, LIBRARY))
    array_shift = rng.normal(0.0, 0.35, size=(n_arrays, LIBRARY))
    eta = logit(base_p)[None, :] + folio_shift[folio] + array_shift[array]

    if mode == "STABLE":
        orientation = np.ones(folios)
    elif mode == "REVERSING":
        orientation = np.ones(folios)
        orientation[rng.choice(folios, size=folios // 2, replace=False)] = -1.0
    else:
        raise ValueError(mode)
    eta[:, 0] += beta * (state - 1) * orientation[folio]
    x = (rng.random((n, LIBRARY)) < logistic(eta)).astype(np.int8)

    held_folios = np.array([folios - 2, folios - 1])
    train = ~np.isin(folio, held_folios)
    held = ~train

    xt = x[train]
    st = state[train]
    n_train = int(train.sum())
    global_p = (xt.sum(axis=0) + 0.5) / (n_train + 1.0)
    state_p = np.empty((3, LIBRARY))
    for s in range(3):
        xs = xt[st == s]
        state_p[s] = (xs.sum(axis=0) + 0.5) / (len(xs) + 1.0)
    discovery_gain = (
        ll_binary(xt, state_p[st]).sum(axis=0)
        - ll_binary(xt, global_p[None, :]).sum(axis=0)
    )
    selected = int(np.argmax(discovery_gain))

    held_gain_by_folio = []
    for hf in held_folios:
        m = folio == hf
        xv = x[m, selected]
        sv = state[m]
        gain = float(
            ll_binary(xv, state_p[sv, selected]).sum()
            - ll_binary(xv, np.full(len(xv), global_p[selected])).sum()
        )
        held_gain_by_folio.append(gain)
    raw = float(sum(held_gain_by_folio))
    paid = raw - SELECTOR_COST
    passed = paid > 0.0 and all(g > 0.0 for g in held_gain_by_folio)
    return {
        "selected_true": selected == 0,
        "passed": passed,
        "detected": passed and selected == 0,
        "wrong_pass": passed and selected != 0,
        "raw_gain": raw,
        "paid_gain": paid,
        "held_positive": sum(g > 0.0 for g in held_gain_by_folio),
    }


def q(values: list[float], quantile: float) -> float:
    return float(np.quantile(np.asarray(values, dtype=float), quantile))


def simulate() -> list[dict[str, object]]:
    master = np.random.SeedSequence(SEED)
    specs = []
    for folios in FOLIOS:
        for arrays in ARRAYS_PER_FOLIO:
            for cells in CELLS_PER_ARRAY:
                specs.append((folios, arrays, cells, "NULL", "STABLE"))
                for effect in ("WEAK", "MEDIUM", "STRONG"):
                    for mode in MODES:
                        specs.append((folios, arrays, cells, effect, mode))
    children = master.spawn(len(specs))
    out = []
    for spec, child in zip(specs, children):
        folios, arrays, cells, effect, mode = spec
        rng = np.random.default_rng(child)
        rows = [trial(rng, folios, arrays, cells, BETAS[effect], mode) for _ in range(TRIALS)]
        out.append(
            {
                "folios": folios,
                "discovery_folios": folios - 2,
                "held_folios": 2,
                "arrays_per_folio": arrays,
                "cells_per_array": cells,
                "total_cells": folios * arrays * cells,
                "effect": effect,
                "beta": BETAS[effect],
                "direction_mode": mode,
                "trials": TRIALS,
                "selected_true_rate": sum(r["selected_true"] for r in rows) / TRIALS,
                "any_pass_rate": sum(r["passed"] for r in rows) / TRIALS,
                "successful_detection_rate": sum(r["detected"] for r in rows) / TRIALS,
                "wrong_predicate_pass_rate": sum(r["wrong_pass"] for r in rows) / TRIALS,
                "both_held_positive_rate": sum(r["held_positive"] == 2 for r in rows) / TRIALS,
                "median_raw_gain_bits": q([r["raw_gain"] for r in rows], 0.5),
                "median_selector_paid_gain_bits": q([r["paid_gain"] for r in rows], 0.5),
                "paid_gain_q10": q([r["paid_gain"] for r in rows], 0.1),
                "paid_gain_q90": q([r["paid_gain"] for r in rows], 0.9),
            }
        )
    return out


def adequate_designs(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by = {(r["folios"], r["arrays_per_folio"], r["cells_per_array"], r["effect"], r["direction_mode"]): r for r in rows}
    out = []
    for folios in FOLIOS:
        for arrays in ARRAYS_PER_FOLIO:
            for cells in CELLS_PER_ARRAY:
                null = by[(folios, arrays, cells, "NULL", "STABLE")]
                stable = by[(folios, arrays, cells, "MEDIUM", "STABLE")]
                rev = by[(folios, arrays, cells, "MEDIUM", "REVERSING")]
                ok = (
                    stable["successful_detection_rate"] >= 0.80
                    and null["any_pass_rate"] <= 0.05
                    and rev["any_pass_rate"] <= 0.10
                )
                out.append(
                    {
                        "folios": folios,
                        "discovery_folios": folios - 2,
                        "held_folios": 2,
                        "arrays_per_folio": arrays,
                        "cells_per_array": cells,
                        "total_cells": folios * arrays * cells,
                        "medium_stable_detection_rate": stable["successful_detection_rate"],
                        "null_any_pass_rate": null["any_pass_rate"],
                        "medium_reversing_any_pass_rate": rev["any_pass_rate"],
                        "adequate": ok,
                    }
                )
    return out


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        for row in rows:
            w.writerow(row)


def main() -> None:
    ART.mkdir(parents=True, exist_ok=True)
    rows = simulate()
    designs = adequate_designs(rows)
    adequate = [r for r in designs if r["adequate"]]
    adequate.sort(key=lambda r: (r["total_cells"], r["folios"], r["arrays_per_folio"], r["cells_per_array"]))
    recommendation = adequate[0] if adequate else None

    grid_path = ART / "gdt370_power_grid.tsv"
    design_path = ART / "gdt370_design_thresholds.tsv"
    write_tsv(grid_path, rows)
    write_tsv(design_path, designs)

    result = {
        "schema": "GDT370_RESULT_V1",
        "status": "ADEQUATE_PROSPECTIVE_DESIGN_IDENTIFIED" if recommendation else "NO_TESTED_DESIGN_REACHES_FROZEN_POWER_GATE",
        "question": "How much independent acquisition capacity is needed to distinguish stable grounding from postselected or reversing associations?",
        "simulation": {
            "seed": SEED,
            "trials_per_design_scenario": TRIALS,
            "candidate_library": LIBRARY,
            "selector_cost_bits": SELECTOR_COST,
            "folios": list(FOLIOS),
            "arrays_per_folio": list(ARRAYS_PER_FOLIO),
            "cells_per_array": list(CELLS_PER_ARRAY),
            "held_folios": 2,
            "betas": BETAS,
        },
        "gate": {
            "medium_stable_detection_at_least": 0.80,
            "null_any_pass_at_most": 0.05,
            "medium_reversing_any_pass_at_most": 0.10,
        },
        "adequate_design_count": len(adequate),
        "recommended_design": recommendation,
        "current_panel_capacity": {
            "folios": 3,
            "arrays": 5,
            "cells": 27,
            "eligible_for_two_held_folios_plus_multi_folio_discovery": False,
            "reason": "Holding two folios leaves one discovery folio; the observed top association reversed in f99 and failed the order-matched null.",
        },
        "claim_ceiling": "SYNTHETIC_PROSPECTIVE_ACQUISITION_CAPACITY_ONLY",
        "new_voynich_rows_loaded": 0,
        "new_images_accessed": 0,
        "f84_accessed": False,
        "inputs": {str(p.relative_to(ROOT)): sha(p) for p in INPUTS},
        "implementation": {str((BASE / "src/run.py").relative_to(ROOT)): sha(BASE / "src/run.py")},
        "outputs": {str(p.relative_to(ROOT)): sha(p) for p in (grid_path, design_path)},
    }
    payload = dict(result)
    result["content_hash"] = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    (ART / "gdt370_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
