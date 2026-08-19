#!/usr/bin/env python3
"""Run GDT371's frozen untouched-validation capacity simulation."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt371_validation_capacity_extension"
ART = BASE / "artifacts"
SEED = 37120260819
TRIALS = 256
LIBRARY = 81
SELECTOR_COST = math.log2(LIBRARY)
DISCOVERY = (4, 6, 8, 10, 12)
HELD = (2, 4, 6, 8, 10)
ARRAYS = (1, 2)
CELLS = (6, 9, 12)
SCENARIOS = (
    ("NULL", 0.0, "STABLE"),
    ("MEDIUM", 0.9, "STABLE"),
    ("MEDIUM", 0.9, "REVERSING"),
    ("STRONG", 1.3, "STABLE"),
)
INPUT = ROOT / "experiments/yolo/gdt370_grounding_acquisition_power/artifacts/gdt370_result.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def logistic(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def logit(x: np.ndarray) -> np.ndarray:
    return np.log(x / (1.0 - x))


def ll(x: np.ndarray, p: np.ndarray) -> np.ndarray:
    return x * np.log2(p) + (1 - x) * np.log2(1 - p)


def one_trial(rng: np.random.Generator, d: int, h: int, a: int, c: int, beta: float, mode: str) -> dict[str, object]:
    folios = d + h
    n_arrays = folios * a
    folio = np.repeat(np.arange(folios), a * c)
    array = np.repeat(np.arange(n_arrays), c)
    base_state = np.tile(np.arange(3), c // 3)
    state = np.concatenate([rng.permutation(base_state) for _ in range(n_arrays)])

    base_p = np.clip(rng.beta(2.0, 2.0, LIBRARY), .10, .90)
    eta = (
        logit(base_p)[None, :]
        + rng.normal(0, .50, (folios, LIBRARY))[folio]
        + rng.normal(0, .35, (n_arrays, LIBRARY))[array]
    )
    orientation = np.ones(folios)
    if mode == "REVERSING":
        orientation[rng.choice(folios, folios // 2, replace=False)] = -1
    eta[:, 0] += beta * (state - 1) * orientation[folio]
    x = (rng.random(eta.shape) < logistic(eta)).astype(np.int8)

    train = folio < d
    xt, st = x[train], state[train]
    gp = (xt.sum(0) + .5) / (len(xt) + 1)
    sp = np.empty((3, LIBRARY))
    for s in range(3):
        xs = xt[st == s]
        sp[s] = (xs.sum(0) + .5) / (len(xs) + 1)
    discovery_gain = ll(xt, sp[st]).sum(0) - ll(xt, gp[None, :]).sum(0)
    selected = int(np.argmax(discovery_gain))

    gains = []
    for hf in range(d, folios):
        m = folio == hf
        xv, sv = x[m, selected], state[m]
        gains.append(float(ll(xv, sp[sv, selected]).sum() - ll(xv, np.full(len(xv), gp[selected])).sum()))
    raw = float(sum(gains))
    paid = raw - SELECTOR_COST
    required_positive = max(2, math.ceil(.75 * h))
    positive = sum(g > 0 for g in gains)
    passed = paid > 0 and positive >= required_positive
    return {
        "selected_true": selected == 0,
        "passed": passed,
        "detected": passed and selected == 0,
        "wrong_pass": passed and selected != 0,
        "held_positive": positive,
        "raw": raw,
        "paid": paid,
    }


def quantile(xs: list[float], p: float) -> float:
    return float(np.quantile(np.asarray(xs), p))


def run_grid() -> list[dict[str, object]]:
    specs = [
        (d, h, a, c, effect, beta, mode)
        for d in DISCOVERY for h in HELD for a in ARRAYS for c in CELLS
        for effect, beta, mode in SCENARIOS
    ]
    children = np.random.SeedSequence(SEED).spawn(len(specs))
    out = []
    for spec, child in zip(specs, children):
        d, h, a, c, effect, beta, mode = spec
        rng = np.random.default_rng(child)
        trials = [one_trial(rng, d, h, a, c, beta, mode) for _ in range(TRIALS)]
        out.append({
            "discovery_folios": d,
            "held_folios": h,
            "total_folios": d + h,
            "arrays_per_folio": a,
            "cells_per_array": c,
            "discovery_cells": d * a * c,
            "held_cells": h * a * c,
            "total_cells": (d + h) * a * c,
            "effect": effect,
            "beta": beta,
            "direction_mode": mode,
            "required_positive_held_folios": max(2, math.ceil(.75 * h)),
            "trials": TRIALS,
            "selected_true_rate": sum(t["selected_true"] for t in trials) / TRIALS,
            "any_pass_rate": sum(t["passed"] for t in trials) / TRIALS,
            "successful_detection_rate": sum(t["detected"] for t in trials) / TRIALS,
            "wrong_predicate_pass_rate": sum(t["wrong_pass"] for t in trials) / TRIALS,
            "held_transfer_rate": sum(t["held_positive"] >= max(2, math.ceil(.75 * h)) for t in trials) / TRIALS,
            "median_raw_gain_bits": quantile([t["raw"] for t in trials], .5),
            "median_selector_paid_gain_bits": quantile([t["paid"] for t in trials], .5),
            "paid_gain_q10": quantile([t["paid"] for t in trials], .1),
            "paid_gain_q90": quantile([t["paid"] for t in trials], .9),
        })
    return out


def designs(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by = {(r["discovery_folios"], r["held_folios"], r["arrays_per_folio"], r["cells_per_array"], r["effect"], r["direction_mode"]): r for r in rows}
    out = []
    for d in DISCOVERY:
        for h in HELD:
            for a in ARRAYS:
                for c in CELLS:
                    null = by[(d, h, a, c, "NULL", "STABLE")]
                    stable = by[(d, h, a, c, "MEDIUM", "STABLE")]
                    reverse = by[(d, h, a, c, "MEDIUM", "REVERSING")]
                    ok = stable["successful_detection_rate"] >= .80 and null["any_pass_rate"] <= .05 and reverse["any_pass_rate"] <= .10
                    out.append({
                        "discovery_folios": d, "held_folios": h, "total_folios": d + h,
                        "arrays_per_folio": a, "cells_per_array": c,
                        "discovery_cells": d * a * c, "held_cells": h * a * c,
                        "total_cells": (d + h) * a * c,
                        "medium_stable_detection_rate": stable["successful_detection_rate"],
                        "null_any_pass_rate": null["any_pass_rate"],
                        "medium_reversing_any_pass_rate": reverse["any_pass_rate"],
                        "adequate": ok,
                    })
    return out


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader(); w.writerows(rows)


def main() -> None:
    ART.mkdir(parents=True, exist_ok=True)
    grid = run_grid()
    design = designs(grid)
    adequate = [r for r in design if r["adequate"]]
    adequate.sort(key=lambda r: (r["total_cells"], r["total_folios"], r["held_cells"], r["arrays_per_folio"], r["cells_per_array"]))
    grid_path = ART / "gdt371_power_grid.tsv"
    design_path = ART / "gdt371_design_thresholds.tsv"
    write_tsv(grid_path, grid); write_tsv(design_path, design)
    result = {
        "schema": "GDT371_RESULT_V1",
        "status": "ADEQUATE_PROSPECTIVE_DESIGN_IDENTIFIED" if adequate else "NO_TESTED_DESIGN_REACHES_EXTENDED_GATE",
        "simulation": {"seed": SEED, "trials": TRIALS, "candidate_library": LIBRARY, "selector_cost_bits": SELECTOR_COST, "discovery_folios": list(DISCOVERY), "held_folios": list(HELD), "arrays_per_folio": list(ARRAYS), "cells_per_array": list(CELLS)},
        "gate": {"medium_stable_detection_at_least": .80, "null_any_pass_at_most": .05, "medium_reversing_any_pass_at_most": .10, "held_positive_fraction": .75, "minimum_positive_held_folios": 2},
        "adequate_design_count": len(adequate),
        "recommended_design": adequate[0] if adequate else None,
        "claim_ceiling": "SYNTHETIC_PROSPECTIVE_ACQUISITION_CAPACITY_ONLY",
        "new_voynich_rows_loaded": 0, "new_images_accessed": 0, "f84_accessed": False,
        "inputs": {str(INPUT.relative_to(ROOT)): sha(INPUT)},
        "implementation": {str((BASE / 'src/run.py').relative_to(ROOT)): sha(BASE / 'src/run.py')},
        "outputs": {str(p.relative_to(ROOT)): sha(p) for p in (grid_path, design_path)},
    }
    result["content_hash"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    (ART / "gdt371_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
