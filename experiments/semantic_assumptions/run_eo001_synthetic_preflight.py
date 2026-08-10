#!/usr/bin/env python3
"""Run EO001 target-free null, power, and adversarial calibration."""

from __future__ import annotations

import csv
import hashlib
import json
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

# Pin numerical libraries before importing NumPy/core.
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import numpy as np

import eo001_core as core


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
PANEL_PATH = RESULTS / "eo001_exact_form_onset_capacity.tsv"
CAPACITY = RESULTS / "eo001_exact_form_onset_capacity.json"
CAPACITY_VALIDATION = RESULTS / "eo001_exact_form_onset_capacity_validation.json"
SOURCE = RESULTS / "source_native_structural_interlinear_v1.tsv"
SPEC = BASE / "EO001_EXACT_FORM_ONSET_TRANSFER_PREREGISTRATION.md"
CORE = BASE / "eo001_core.py"
RUNNER = Path(__file__).resolve()
OUT_JSON = RESULTS / "eo001_synthetic_preflight.json"
OUT_REPORT = RESULTS / "eo001_synthetic_preflight_report.md"

FROZEN = {
    PANEL_PATH: "9bad926ec53532ca118c9bcdee82fbe5ffebe53b328b0716cc85082f72690d4c",
    CAPACITY: "1a54880f334f5d522c23d2fa0ffcae4eb45f285f4d45c89b3e88373ee8c35b85",
    CAPACITY_VALIDATION: "db22634ff99477ee52d57379dc4efc37084c514606866e4b8bda458a548137f4",
    SOURCE: "95a15329c61a11c1c4dc671b4df2b3482af9d25a1108eadac2f69b066d3785af",
}
AMPLITUDES = (.25, .50, .75, 1.00, 1.50, 2.00)
ADVERSARIES = (
    "GENERIC", "POSITION_ONLY", "NUISANCE_ONLY", "ONE_FORM", "ONE_FOLIO",
    "ONE_STATE", "ONE_BLOCK", "REVERSED_STATE", "STATE_REMAPPED", "FOLIO_RANDOM",
)
PANEL = None
DONORS: list[str] = []


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def seed(family: str, world: int, amplitude: float | None) -> int:
    label = "NONE" if amplitude is None else f"{amplitude:.2f}"
    return int.from_bytes(hashlib.sha256(f"EO001|{family}|{world}|{label}".encode()).digest()[:8], "little")


def source_geometry() -> tuple[list[str], int]:
    """Return non-target donor sequences without accessing target-successor surfaces."""
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    by_id = {row["consensus_group_id"]: row for row in rows}
    by_locus_index = {(row["locus"], int(row["group_index"])): row for row in rows}
    panel_ids = {item["anonymous_event_id"] for item in PANEL.rows}
    target_successors = set()
    matched = 0
    for source_id, row in by_id.items():
        if "EO001-" + hashlib.sha256(("EO001|" + source_id).encode()).hexdigest()[:20] not in panel_ids:
            continue
        matched += 1
        successor = by_locus_index[(row["locus"], int(row["group_index"]) + 1)]
        target_successors.add(successor["consensus_group_id"])
    if matched != 1295 or len(target_successors) != 1295:
        raise ValueError("EO001 source target geometry drift")
    donors = []
    for row in rows:
        if row["consensus_group_id"] in target_successors:
            continue
        if row["grammar_scope"] == "CONFIRMED_PROSE":
            donors.append(row["family_surface"])
    if len(donors) != 20604 or any(not value for value in donors):
        raise ValueError(f"EO001 donor pool drift: {len(donors)}")
    return donors, len(target_successors)


def donor_blocks(rng: np.random.Generator) -> dict[str, np.ndarray]:
    choice = rng.choice(len(DONORS), size=len(PANEL.rows), replace=False)
    return core.fingerprint_matrix([DONORS[int(index)] for index in choice])


def gaussian(family: str, world: int, amplitude: float) -> dict[str, np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(seed(family, world, amplitude)))
    blocks = {}
    rel = np.asarray([
        int(row["trigger_group_index"]) / (int(row["locus_group_count"]) - 1.0)
        for row in PANEL.rows
    ])
    for block_index, (name, dimension) in enumerate(core.BLOCK_DIMS.items()):
        signatures = rng.normal(size=(len(core.FORMS), dimension))
        noise = rng.normal(size=(len(PANEL.rows), dimension))
        signal = signatures[PANEL.forms].copy()
        if family == "GENERIC":
            signal[:] = signatures[0]
        elif family == "POSITION_ONLY":
            coefficients = rng.normal(size=(4, dimension))
            signal = np.column_stack((np.ones(len(rel)), rel, rel * rel, rel * rel * rel)) @ coefficients
        elif family == "NUISANCE_ONLY":
            signal = PANEL.design @ rng.normal(size=(PANEL.design.shape[1], dimension))
        elif family == "ONE_FORM":
            signal[PANEL.forms != world % len(core.FORMS)] = 0.0
        elif family == "ONE_FOLIO":
            selected = tuple(PANEL.informative)[world % len(PANEL.informative)]
            signal[PANEL.folios != selected] = 0.0
        elif family == "ONE_STATE":
            signal[PANEL.states == 1] = 0.0
        elif family == "ONE_BLOCK":
            if block_index != world % len(core.BLOCK_DIMS):
                signal[:] = 0.0
        elif family == "REVERSED_STATE":
            signal[PANEL.states == 1] *= -1.0
        elif family == "STATE_REMAPPED":
            mask = PANEL.states == 1
            signal[mask] = signatures[(PANEL.forms[mask] + 1) % len(core.FORMS)]
        elif family == "FOLIO_RANDOM":
            mask = PANEL.states == 1
            for folio in sorted(set(PANEL.folios)):
                shift = 1 + seed(f"FOLIO_SHIFT_{folio}", world, amplitude) % (len(core.FORMS) - 1)
                selected = mask & (PANEL.folios == folio)
                signal[selected] = signatures[(PANEL.forms[selected] + shift) % len(core.FORMS)]
        elif family != "PORTABLE":
            raise ValueError(f"unknown Gaussian family {family}")
        blocks[name] = noise + amplitude * signal
    return blocks


def whole_row(family: str, world: int) -> dict[str, np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(seed(family, world, .60)))
    blocks = donor_blocks(rng)
    if family == "REALISTIC_NULL":
        return blocks
    prototypes = rng.choice(len(DONORS), size=len(core.FORMS), replace=False)
    proto_rows = [core.fingerprint(DONORS[int(index)]) for index in prototypes]
    proto = {
        name: np.asarray([row[name] for row in proto_rows], dtype=np.float64)
        for name in core.BLOCK_DIMS
    }
    selected = rng.random(len(PANEL.rows)) < .60
    for name in core.BLOCK_DIMS:
        blocks[name][selected] = proto[name][PANEL.forms[selected]]
    return blocks


def compact(evaluation: dict) -> dict:
    return {
        "passes": evaluation["passes"], "gates": evaluation["gates"],
        "blocks": evaluation["blocks"], "summary": {
            key: value for key, value in evaluation["summary"].items()
            if key not in ("folio_contributions", "form_contributions")
        },
        "folio_contributions": evaluation["summary"]["folio_contributions"],
        "form_contributions": evaluation["summary"]["form_contributions"],
    }


def task(item: tuple[str, int, float | None]) -> dict:
    family, world, amplitude = item
    if family == "GAUSSIAN_NULL":
        blocks = gaussian("PORTABLE", world, 0.0)
    elif family in ("REALISTIC_NULL", "WHOLE_ROW_PORTABLE"):
        blocks = whole_row(family, world)
    else:
        assert amplitude is not None
        blocks = gaussian(family, world, amplitude)
    return {"family": family, "world": world, "amplitude": amplitude, "evaluation": compact(core.evaluate(PANEL, blocks))}


def main() -> None:
    global PANEL, DONORS
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen input drift: {path}")
    PANEL = core.load_panel(PANEL_PATH)
    DONORS, excluded = source_geometry()
    tasks = [("GAUSSIAN_NULL", world, None) for world in range(64)]
    tasks += [("REALISTIC_NULL", world, None) for world in range(64)]
    tasks += [("PORTABLE", world, amplitude) for amplitude in AMPLITUDES for world in range(8)]
    tasks += [("WHOLE_ROW_PORTABLE", world, .60) for world in range(8)]
    # Adversaries are evaluated at the smallest portable amplitude passing 7/8;
    # first run every positive amplitude, then select without opening target data.
    with ProcessPoolExecutor(max_workers=32) as pool:
        positive_results = list(pool.map(task, tasks, chunksize=1))
    portable_counts = {
        amplitude: sum(row["evaluation"]["passes"] for row in positive_results if row["family"] == "PORTABLE" and row["amplitude"] == amplitude)
        for amplitude in AMPLITUDES
    }
    selected = next((amplitude for amplitude in AMPLITUDES if portable_counts[amplitude] >= 7), None)
    if selected is None:
        selected = AMPLITUDES[-1]
    adversary_tasks = [(family, world, selected) for family in ADVERSARIES for world in range(8)]
    with ProcessPoolExecutor(max_workers=32) as pool:
        adversary_results = list(pool.map(task, adversary_tasks, chunksize=1))
    records = positive_results + adversary_results
    records.sort(key=lambda row: (row["family"], -1 if row["amplitude"] is None else row["amplitude"], row["world"]))
    pass_counts = {}
    for family in ("GAUSSIAN_NULL", "REALISTIC_NULL", "WHOLE_ROW_PORTABLE", *ADVERSARIES):
        pass_counts[family] = sum(row["evaluation"]["passes"] for row in records if row["family"] == family)
    gates = {
        "gaussian_null_zero_of_64": pass_counts["GAUSSIAN_NULL"] == 0,
        "realistic_null_zero_of_64": pass_counts["REALISTIC_NULL"] == 0,
        "portable_at_least_seven_of_eight": portable_counts[selected] >= 7,
        "whole_row_portable_at_least_seven_of_eight": pass_counts["WHOLE_ROW_PORTABLE"] >= 7,
        "all_adversarial_families_zero_of_eight": all(pass_counts[family] == 0 for family in ADVERSARIES),
        "target_successors_excluded_from_donors": excluded == 1295 and len(DONORS) == 20604,
        "all_results_finite": all(np.isfinite(row["evaluation"]["summary"]["combined_observed"]) for row in records),
    }
    status = "PASS_TARGET_FREE_CALIBRATION" if all(gates.values()) else "STOP_TARGET_FREE_CALIBRATION"
    result = {
        "experiment": "EO001_SYNTHETIC_PREFLIGHT", "status": status,
        "inputs": {path.name: sha(path) for path in (*FROZEN, SPEC, CORE, RUNNER)},
        "numerics": {"assignments": core.ASSIGNMENTS, "ridge": core.RIDGE, "tie_tolerance": core.TOL, "workers": 32},
        "donor_pool": {"strict_non_target_groups": len(DONORS), "excluded_target_successors": excluded, "target_successor_surfaces_accessed": 0},
        "portable_amplitude_grid": list(AMPLITUDES), "portable_pass_counts": {f"{key:.2f}": value for key, value in portable_counts.items()},
        "selected_amplitude": selected, "pass_counts": pass_counts, "gates": gates,
        "target_successor_rows_scored": 0, "english_glosses": 0, "worlds": records,
        "decision": "AUTHORIZE_INDEPENDENT_PREFLIGHT_VALIDATION_ONLY" if all(gates.values()) else "STOP_EO001_BEFORE_TARGET",
        "claim_ceiling": "Synthetic calibration only; no manuscript successor association, embedded onset, clause, word, meaning, plaintext, or translation.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_REPORT.write_text(
        "# EO001 synthetic preflight\n\n"
        f"Status: **{status}**.\n\n"
        f"The scorer evaluated **{len(records)}** target-free worlds with 32,768 within-folio assignments. "
        f"The smallest portable amplitude reaching 7/8 was **{selected:.2f}**. Gaussian and realistic null passes were "
        f"{pass_counts['GAUSSIAN_NULL']}/64 and {pass_counts['REALISTIC_NULL']}/64; whole-row portable signals passed "
        f"{pass_counts['WHOLE_ROW_PORTABLE']}/8. All adversarial pass counts were "
        + ", ".join(f"{name}={pass_counts[name]}/8" for name in ADVERSARIES) + ".\n\n"
        "The 1,295 real successors were excluded from the realistic donor pool and zero target successor surfaces were accessed. "
        "Calibration supplies no manuscript association, embedded onset, clause, word, meaning, plaintext, or translation.\n",
        encoding="utf-8",
    )
    if status != "PASS_TARGET_FREE_CALIBRATION":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
