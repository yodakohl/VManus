#!/usr/bin/env python3
"""Run LRG001 calibration on synthetic sequences and feature-blind geometry."""

from __future__ import annotations

import os

for variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[variable] = "1"

import hashlib
import json
import multiprocessing as mp
import time
from pathlib import Path

import numpy as np

from lrg001_core import (
    ALPHABET, ASSIGNMENTS, assignment_coefficients, evaluate, feature_matrix,
    load_geometry, sha256_array,
)


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
CAPACITY = RESULTS / "lrg001_label_register_capacity.tsv"
CAPACITY_JSON = RESULTS / "lrg001_label_register_capacity.json"
CAPACITY_VALIDATION = RESULTS / "lrg001_label_register_capacity_validation.json"
SPEC = HERE / "LRG001_TARGET_BLIND_CALIBRATION_SPEC.md"
CORE = HERE / "lrg001_core.py"
OUT_JSON = RESULTS / "lrg001_target_blind_calibration_v2.json"
OUT_REPORT = RESULTS / "lrg001_target_blind_calibration_v2_report.md"

EXPECTED = {
    "capacity": "abec3385838cf9218db34bda108288f680a9b8482c7b7e47d3fb83c711998536",
    "capacity_json": "a6d7d64d1752d710853cd083c8c7bfd9643ef206499a5bad65ebee9e63ba87f8",
}
FAMILIES = (
    "DISTRIBUTED_FULL", "DISTRIBUTED_HALF", "DISTRIBUTED_START_ONLY",
    "ONE_FOLIO", "ONE_SECTION", "PAGE_ONLY", "FOLIO_RANDOM",
    "PARITY_MISMATCH", "EXACT_IDENTITY_ONLY",
)
GEOMETRY = None
COEFFICIENT_EVEN = None
COEFFICIENT_ODD = None


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def labels_for_geometry() -> np.ndarray:
    labels = np.zeros(len(GEOMETRY.row_ids), dtype=np.int8)
    for cell in sorted(set(GEOMETRY.cell_ids)):
        indices = np.flatnonzero(GEOMETRY.cell_ids == cell)
        labels[indices[: GEOMETRY.labels_per_cell[cell]]] = 1
    return labels


def base_sequences(seed: int) -> list[list[int]]:
    rng = np.random.default_rng(seed)
    weights = np.arange(24, 0, -1, dtype=np.float64)
    weights /= weights.sum()
    return [list(rng.choice(24, size=int(length), p=weights)) for length in GEOMETRY.lengths]


def shared_edit(sequence: list[int], rng: np.random.Generator, strength: float, pattern=(0, 1, 2, 3)) -> None:
    if rng.random() > strength:
        return
    sequence[0] = pattern[0]
    sequence[-1] = pattern[1]
    if len(sequence) >= 4:
        middle = (len(sequence) - 1) // 2
        sequence[middle] = pattern[2]
        sequence[middle + 1] = pattern[3]


def make_world(family: str, world: int) -> tuple[list[str], np.ndarray]:
    seed = 910000 + 1000 * list(("NULL",) + FAMILIES).index(family) + world
    rng = np.random.default_rng(seed)
    sequences = base_sequences(seed + 77)
    labels = labels_for_geometry()
    if family == "NULL":
        pass
    elif family in {"DISTRIBUTED_FULL", "DISTRIBUTED_HALF"}:
        strength = 0.90 if family == "DISTRIBUTED_FULL" else 0.50
        for index in np.flatnonzero(labels == 1):
            shared_edit(sequences[index], rng, strength)
    elif family == "DISTRIBUTED_START_ONLY":
        for index in np.flatnonzero(labels == 1):
            if rng.random() <= 0.90:
                sequences[index][0] = 0
    elif family == "ONE_FOLIO":
        for index in np.flatnonzero((labels == 1) & (GEOMETRY.folios == "f89")):
            shared_edit(sequences[index], rng, 1.0)
    elif family == "ONE_SECTION":
        for index in np.flatnonzero((labels == 1) & (GEOMETRY.sections == "B")):
            shared_edit(sequences[index], rng, 0.90)
    elif family == "PAGE_ONLY":
        selected_pages = sorted(set(GEOMETRY.pages))[::2]
        for index in np.flatnonzero(np.isin(GEOMETRY.pages, selected_pages)):
            shared_edit(sequences[index], rng, 1.0)
    elif family == "FOLIO_RANDOM":
        for folio_index, folio in enumerate(sorted(set(GEOMETRY.folios))):
            pattern = (
                folio_index % 24, (folio_index + 7) % 24,
                (folio_index + 13) % 24, (folio_index + 19) % 24,
            )
            for index in np.flatnonzero((labels == 1) & (GEOMETRY.folios == folio)):
                shared_edit(sequences[index], rng, 0.90, pattern)
    elif family == "PARITY_MISMATCH":
        for index in np.flatnonzero(labels == 1):
            parity = int(GEOMETRY.folios[index][1:]) % 2
            shared_edit(sequences[index], rng, 0.90, (0, 1, 2, 3) if parity else (4, 5, 6, 7))
    elif family == "EXACT_IDENTITY_ONLY":
        weights = np.arange(24, 0, -1, dtype=np.float64)
        weights /= weights.sum()
        for index in np.flatnonzero(labels == 1):
            local = np.random.default_rng(seed + 100000 + index)
            sequences[index] = list(local.choice(24, size=len(sequences[index]), p=weights))
    else:
        raise RuntimeError(family)
    return ["".join(ALPHABET[value] for value in sequence) for sequence in sequences], labels


def worker(task: tuple[str, int]) -> dict[str, object]:
    family, world = task
    sequences, labels = make_world(family, world)
    matrix = feature_matrix(sequences, GEOMETRY.lengths)
    evaluation = evaluate(matrix, labels, GEOMETRY, COEFFICIENT_EVEN, COEFFICIENT_ODD)
    return {
        "family": family,
        "world": world,
        "matrix_sha256": sha256_array(matrix),
        "evaluation": evaluation,
    }


def main() -> None:
    global GEOMETRY, COEFFICIENT_EVEN, COEFFICIENT_ODD
    observed = {
        "capacity": digest(CAPACITY),
        "capacity_json": digest(CAPACITY_JSON),
    }
    if observed != EXPECTED:
        raise RuntimeError(f"LRG001 calibration input drift {observed}")
    capacity_validation = json.loads(CAPACITY_VALIDATION.read_text(encoding="utf-8"))
    if capacity_validation["status"] != "PASS_INDEPENDENT_LRG001_CAPACITY_RECONSTRUCTION":
        raise RuntimeError("capacity validation absent")
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise RuntimeError("calibration output already exists")
    GEOMETRY = load_geometry(CAPACITY)
    folio_numbers = np.asarray([int(value[1:]) for value in GEOMETRY.folios])
    COEFFICIENT_EVEN = assignment_coefficients(GEOMETRY, folio_numbers % 2 == 0)
    COEFFICIENT_ODD = assignment_coefficients(GEOMETRY, folio_numbers % 2 == 1)
    assignment_digests = {
        "EVEN_HELD": sha256_array(COEFFICIENT_EVEN[1]),
        "ODD_HELD": sha256_array(COEFFICIENT_ODD[1]),
    }
    tasks = [("NULL", world) for world in range(64)] + [
        (family, world) for family in FAMILIES for world in range(8)
    ]
    started = time.time()
    context = mp.get_context("fork")
    with context.Pool(processes=min(32, len(tasks))) as pool:
        records = pool.map(worker, tasks)
    elapsed = time.time() - started
    by_family = {}
    for family in ("NULL",) + FAMILIES:
        subset = [record for record in records if record["family"] == family]
        by_family[family] = {
            "worlds": len(subset),
            "passes": sum(bool(record["evaluation"]["passes"]) for record in subset),
        }
    gates = {
        "zero_of_64_null": by_family["NULL"]["passes"] == 0,
        "eight_of_eight_distributed_full": by_family["DISTRIBUTED_FULL"]["passes"] == 8,
        "six_of_eight_distributed_half": by_family["DISTRIBUTED_HALF"]["passes"] >= 6,
        "eight_of_eight_distributed_start_only": by_family["DISTRIBUTED_START_ONLY"]["passes"] == 8,
        "zero_all_adversaries": all(
            by_family[family]["passes"] == 0 for family in (
                "ONE_FOLIO", "ONE_SECTION", "PAGE_ONLY", "FOLIO_RANDOM",
                "PARITY_MISMATCH", "EXACT_IDENTITY_ONLY",
            )
        ),
        "all_records_finite": all(
            np.isfinite(record["evaluation"]["profile_cosine"]) and all(
                np.isfinite(direction["effect"]) and np.isfinite(direction["p"])
                for direction in record["evaluation"]["directions"].values()
            )
            for record in records
        ),
    }
    status = "PASS_TARGET_BLIND_LABEL_PROFILE_CALIBRATION" if all(gates.values()) else "STOP_TARGET_BLIND_CALIBRATION_FAILED"
    decision = "GO_INDEPENDENT_RECONSTRUCTION_ONLY" if all(gates.values()) else "TARGET_FORBIDDEN"
    result = {
        "status": status,
        "decision": decision,
        "claim_ceiling": (
            "Synthetic calibration can authorize independent reconstruction and then one separately frozen manuscript target only. "
            "It supplies no manuscript label profile, identifier, name, noun, object ownership, language, meaning, plaintext, or translation."
        ),
        "inputs": observed,
        "source_identity_fields_accessed": [],
        "spec_sha256": digest(SPEC),
        "core_sha256": digest(CORE),
        "assignments": ASSIGNMENTS,
        "assignment_digests": assignment_digests,
        "geometry": {
            "rows": len(GEOMETRY.row_ids),
            "cells": len(set(GEOMETRY.cell_ids)),
            "folios": len(set(GEOMETRY.folios)),
            "sections": sorted(set(GEOMETRY.sections)),
        },
        "family_summary": by_family,
        "gates": gates,
        "records": records,
        "runtime_seconds": elapsed,
    }
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    temporary = OUT_JSON.with_suffix(".json.tmp")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    temporary.replace(OUT_JSON)
    report = "\n".join([
        "# LRG001 target-blind calibration",
        "",
        f"Status: **{status}**.",
        "",
        f"The 32-worker run evaluated **{len(records)}** synthetic worlds on the exact "
        f"2,767-row, 109-cell, 13-folio B/P geometry with **{ASSIGNMENTS}** fixed-count "
        f"held assignments per parity direction in **{elapsed:.2f} seconds**.",
        "",
        "| family | passes / worlds |",
        "|---|---:|",
        *[f"| {family} | {values['passes']} / {values['worlds']} |" for family, values in by_family.items()],
        "",
        f"Decision: **{decision}**.",
        "",
        "No manuscript family surface, STA member code, EVA spelling, label profile, "
        "identifier, name, noun, meaning, plaintext, or translation was accessed or produced.",
        "",
    ])
    temporary = OUT_REPORT.with_suffix(".md.tmp")
    temporary.write_text(report, encoding="utf-8", newline="\n")
    temporary.replace(OUT_REPORT)
    print(text[:4000], end="")


if __name__ == "__main__":
    main()
