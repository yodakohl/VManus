#!/usr/bin/env python3
"""Run target-blind synthetic calibration of the LRG002 slot test."""

from __future__ import annotations

import os
for variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[variable] = "1"

import hashlib
import json
import multiprocessing as mp
from pathlib import Path

import numpy as np

from lrg002_core import ASSIGNMENTS, evaluate, load_geometry, null_coefficients, rotations, sha256_array


HERE = Path(__file__).resolve().parent
RES = HERE / "results"
CAPACITY = RES / "lrg002_prose_slot_capacity.tsv"
OUT = RES / "lrg002_target_blind_calibration.json"
REPORT = RES / "lrg002_target_blind_calibration_report.md"
POSITIVE = ("DISTRIBUTED_FIRST_FULL", "DISTRIBUTED_LAST_FULL", "DISTRIBUTED_EDGE_FULL", "DISTRIBUTED_FIRST_HALF", "DISTRIBUTED_LAST_HALF")
NEGATIVE = ("ONE_FOLIO", "ONE_SECTION", "ONE_PARITY", "FOLIO_RANDOM_DIRECTION", "SECTION_OPPOSITION", "PARITY_OPPOSITION", "PAGE_ONLY", "LENGTH_ONLY", "SEGMENT_ONLY")
GEOMETRY = None
COEFFICIENTS = None


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add_position(raw: np.ndarray, mask: np.ndarray, amount: float) -> None:
    raw[mask] += amount


def synthetic(family: str, world: int) -> np.ndarray:
    seed = 720000 + 1000 * list(("NULL",) + POSITIVE + NEGATIVE).index(family) + world
    rng = np.random.default_rng(seed)
    raw = rng.normal(0.0, 1.0, len(GEOMETRY.row_ids))
    for page in sorted(set(GEOMETRY.pages)):
        raw[GEOMETRY.pages == page] += rng.normal(0.0, 2.0)
    raw += 0.25 * GEOMETRY.lengths
    first = GEOMETRY.primary & (GEOMETRY.positions == "FIRST")
    last = GEOMETRY.primary & (GEOMETRY.positions == "LAST")
    if family == "DISTRIBUTED_FIRST_FULL": add_position(raw, first, 1.4)
    elif family == "DISTRIBUTED_LAST_FULL": add_position(raw, last, 1.4)
    elif family == "DISTRIBUTED_EDGE_FULL": add_position(raw, first | last, 1.1)
    elif family == "DISTRIBUTED_FIRST_HALF": add_position(raw, first, 0.8)
    elif family == "DISTRIBUTED_LAST_HALF": add_position(raw, last, 0.8)
    elif family == "ONE_FOLIO": add_position(raw, first & (GEOMETRY.folios == "f75"), 3.0)
    elif family == "ONE_SECTION": add_position(raw, first & (GEOMETRY.sections == "B"), 1.4)
    elif family == "ONE_PARITY": add_position(raw, first & (GEOMETRY.parities == "ODD"), 1.4)
    elif family == "FOLIO_RANDOM_DIRECTION":
        patterns = ((1.8, 0.0), (-1.8, 0.0), (0.0, 1.8), (0.0, -1.8))
        for index, folio in enumerate(GEOMETRY.folio_names):
            left, right = patterns[(index + world) % len(patterns)]
            add_position(raw, first & (GEOMETRY.folios == folio), left)
            add_position(raw, last & (GEOMETRY.folios == folio), right)
    elif family == "SECTION_OPPOSITION":
        add_position(raw, first & (GEOMETRY.sections == "B"), 1.4)
        add_position(raw, first & (GEOMETRY.sections == "P"), -1.4)
    elif family == "PARITY_OPPOSITION":
        add_position(raw, first & (GEOMETRY.parities == "ODD"), 1.4)
        add_position(raw, first & (GEOMETRY.parities == "EVEN"), -1.4)
    elif family == "PAGE_ONLY":
        for page_index, page in enumerate(sorted(set(GEOMETRY.pages))): raw[GEOMETRY.pages == page] += 20.0 * ((page_index % 5) - 2)
    elif family == "LENGTH_ONLY": raw += 10.0 * GEOMETRY.lengths
    elif family == "SEGMENT_ONLY":
        for segment_index, segment in enumerate(sorted(set(GEOMETRY.segments))): raw[GEOMETRY.segments == segment] += 4.0 * ((segment_index % 7) - 3)
    elif family != "NULL": raise RuntimeError(family)
    return raw


def worker(task: tuple[str, int]) -> dict[str, object]:
    family, world = task; scores = synthetic(family, world)
    return {"family": family, "world": world, "score_sha256": sha256_array(scores), "evaluation": evaluate(scores, GEOMETRY, COEFFICIENTS)}


def main() -> None:
    global GEOMETRY, COEFFICIENTS
    if OUT.exists() or REPORT.exists(): raise RuntimeError("LRG002 calibration output exists")
    GEOMETRY = load_geometry(CAPACITY)
    shift_matrices = {name: rotations(GEOMETRY, name) for name in ("INDEPENDENT_SEGMENT", "COUPLED_FOLIO")}
    COEFFICIENTS = {name: null_coefficients(GEOMETRY, matrix) for name, matrix in shift_matrices.items()}
    tasks = [("NULL", world) for world in range(64)] + [(family, world) for family in POSITIVE + NEGATIVE for world in range(8)]
    with mp.get_context("fork").Pool(32) as pool: records = pool.map(worker, tasks, chunksize=1)
    groups = {family: [record for record in records if record["family"] == family] for family in ("NULL",) + POSITIVE + NEGATIVE}
    pass_counts = {family: sum(bool(record["evaluation"]["passes"]) for record in current) for family, current in groups.items()}
    gates = {
        "zero_of_64_null": pass_counts["NULL"] == 0,
        "all_distributed_plants_pass": all(pass_counts[family] == 8 for family in POSITIVE),
        "all_adversarial_controls_rejected": all(pass_counts[family] == 0 for family in NEGATIVE),
        "rotation_rows_unique": all(len(np.unique(matrix, axis=0)) == ASSIGNMENTS for matrix in shift_matrices.values()),
    }
    status = "PASS_LRG002_TARGET_BLIND_CALIBRATION" if all(gates.values()) else "STOP_LRG002_TARGET_BLIND_CALIBRATION"
    result = {
        "status": status, "decision": "GO_FREEZE_SINGLE_LRG002_TARGET" if all(gates.values()) else "TARGET_FORBIDDEN",
        "counts": {"rows": len(GEOMETRY.row_ids), "primary_rows": int(GEOMETRY.primary.sum()), "segments": len(GEOMETRY.segment_rows), "folios": len(GEOMETRY.folio_names), "assignments_per_ensemble": ASSIGNMENTS, "worlds": len(records)},
        "rotation_digests": {name: sha256_array(matrix) for name, matrix in shift_matrices.items()},
        "coefficient_digests": {name: sha256_array(matrix) for name, matrix in COEFFICIENTS.items()},
        "pass_counts": pass_counts, "gates": gates, "records": records,
        "inputs": {path.name: sha(path) for path in (CAPACITY, HERE / "LRG002_TARGET_BLIND_SLOT_CALIBRATION_SPEC.md", HERE / "lrg002_core.py", Path(__file__))},
        "real_profile_reconstructed": False, "real_position_association_opened": False,
        "claim_ceiling": "Synthetic calibration only; no manuscript slot association, word, identifier, name, POS, meaning, plaintext, or translation is established.",
    }
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"; OUT.write_text(text, encoding="utf-8", newline="\n")
    lines = ["# LRG002 target-blind slot calibration", "", f"Status: **{status}**.", "", "| family | passes | worlds |", "|---|---:|---:|"]
    lines.extend(f"| {family} | {pass_counts[family]} | {len(groups[family])} |" for family in ("NULL",) + POSITIVE + NEGATIVE)
    lines.extend(["", f"Decision: **{result['decision']}**.", "", "The real LRG001 profile and its prose-position association remained unopened. Synthetic calibration supplies no word, identifier, name, POS, meaning, plaintext, or translation.", ""])
    REPORT.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(json.dumps({key: result[key] for key in ("status", "decision", "pass_counts", "gates", "rotation_digests", "real_position_association_opened")}, indent=2, sort_keys=True))


if __name__ == "__main__": main()
