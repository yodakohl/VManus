#!/usr/bin/env python3
"""Nonimporting reconstruction of all LRG001 v2 synthetic worlds."""

from __future__ import annotations

import os

for variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[variable] = "1"

import csv
import hashlib
import json
import multiprocessing as mp
from collections import defaultdict
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
CAPACITY = RESULTS / "lrg001_label_register_capacity.tsv"
PRODUCTION = RESULTS / "lrg001_target_blind_calibration_v2.json"
PRODUCTION_REPORT = RESULTS / "lrg001_target_blind_calibration_v2_report.md"
OUT_JSON = RESULTS / "lrg001_target_blind_calibration_v2_validation.json"
OUT_REPORT = RESULTS / "lrg001_target_blind_calibration_v2_validation_report.md"
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWX"
ASSIGNMENTS = 8192
SEED = 17012026
FAMILIES = (
    "DISTRIBUTED_FULL", "DISTRIBUTED_HALF", "DISTRIBUTED_START_ONLY",
    "ONE_FOLIO", "ONE_SECTION", "PAGE_ONLY", "FOLIO_RANDOM",
    "PARITY_MISMATCH", "EXACT_IDENTITY_ONLY",
)
G = None
EVEN_COEFFICIENT = None
ODD_COEFFICIENT = None


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def array_digest(value: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(value).tobytes(order="C")).hexdigest()


def geometry() -> dict[str, object]:
    with CAPACITY.open(encoding="utf-8", newline="") as handle:
        cells = [row for row in csv.DictReader(handle, delimiter="\t") if row["section"] in {"B", "P"}]
    output: dict[str, object] = {
        "cell": [], "page": [], "folio": [], "section": [], "length": [], "quota": {},
    }
    for cell in cells:
        output["quota"][cell["cell_id"]] = int(cell["label_rows"])
        for _ in range(int(cell["total_rows"])):
            output["cell"].append(cell["cell_id"])
            output["page"].append(cell["page"])
            output["folio"].append(cell["physical_folio"])
            output["section"].append(cell["section"])
            output["length"].append(int(cell["symbol_count"]))
    for key, width in (("cell", "U16"), ("page", "U16"), ("folio", "U8"), ("section", "U1")):
        output[key] = np.asarray(output[key], dtype=width)
    output["length"] = np.asarray(output["length"], dtype=np.int16)
    return output


def indices_by_cell(mask: np.ndarray) -> list[np.ndarray]:
    return [np.flatnonzero(mask & (G["cell"] == cell)) for cell in sorted(set(G["cell"][mask]))]


def labels() -> np.ndarray:
    output = np.zeros(len(G["cell"]), dtype=np.int8)
    for cell in sorted(set(G["cell"])):
        indices = np.flatnonzero(G["cell"] == cell)
        output[indices[: G["quota"][cell]]] = 1
    return output


def coefficients(held: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    held_indices = np.flatnonzero(held)
    local = {int(value): index for index, value in enumerate(held_indices)}
    matrix = np.zeros((ASSIGNMENTS, len(held_indices)), dtype=np.float32)
    rng = np.random.default_rng(SEED + (0 if int(G["folio"][held_indices[0]][1:]) % 2 == 0 else 1))
    folios = sorted(set(G["folio"][held]))
    for folio in folios:
        cells = indices_by_cell(held & (G["folio"] == folio))
        for indices in cells:
            quota = G["quota"][str(G["cell"][indices[0]])]
            columns = np.asarray([local[int(value)] for value in indices], dtype=np.int64)
            matrix[:, columns] = -1.0 / (len(folios) * len(cells) * (len(indices) - quota))
            ranks = rng.random((ASSIGNMENTS, len(columns)))
            chosen = columns[np.argpartition(ranks, quota - 1, axis=1)[:, :quota]]
            matrix[np.arange(ASSIGNMENTS)[:, None], chosen] = 1.0 / (len(folios) * len(cells) * quota)
    return held_indices, matrix


def features(sequences: list[list[int]]) -> np.ndarray:
    output = np.zeros((len(sequences), 648), dtype=np.float64)
    for row, sequence in enumerate(sequences):
        for value in sequence:
            output[row, value] += 1.0 / len(sequence)
        output[row, 24 + sequence[0]] = 1.0
        output[row, 48 + sequence[-1]] = 1.0
        if len(sequence) > 1:
            for left, right in zip(sequence, sequence[1:]):
                output[row, 72 + 24 * left + right] += 1.0 / (len(sequence) - 1)
    return output


def train(matrix: np.ndarray, y: np.ndarray, mask: np.ndarray) -> np.ndarray:
    by_folio = []
    for folio in sorted(set(G["folio"][mask])):
        by_cell = []
        for indices in indices_by_cell(mask & (G["folio"] == folio)):
            by_cell.append(matrix[indices[y[indices] == 1]].mean(0) - matrix[indices[y[indices] == 0]].mean(0))
        by_folio.append(np.mean(np.stack(by_cell), axis=0))
    vector = np.mean(np.stack(by_folio), axis=0)
    return vector / np.linalg.norm(vector)


def effects(scores: np.ndarray, y: np.ndarray, held: np.ndarray) -> tuple[float, dict[str, float], dict[str, float]]:
    folio_values = {}
    sections: dict[str, list[float]] = defaultdict(list)
    for folio in sorted(set(G["folio"][held])):
        cell_values = []
        current = held & (G["folio"] == folio)
        for indices in indices_by_cell(current):
            cell_values.append(float(scores[indices[y[indices] == 1]].mean() - scores[indices[y[indices] == 0]].mean()))
        value = float(np.mean(cell_values))
        folio_values[folio] = value
        sections[str(G["section"][np.flatnonzero(current)[0]])].append(value)
    section_values = {key: float(np.mean(value)) for key, value in sections.items()}
    return float(np.mean(list(folio_values.values()))), folio_values, section_values


def evaluate(matrix: np.ndarray, y: np.ndarray) -> dict[str, object]:
    numbers = np.asarray([int(value[1:]) for value in G["folio"]])
    odd = numbers % 2 == 1
    even = ~odd
    odd_profile = train(matrix, y, odd)
    even_profile = train(matrix, y, even)
    cosine = float(odd_profile @ even_profile)
    directions = {}
    for name, profile, held, bundle, required in (
        ("ODD_TO_EVEN", odd_profile, even, EVEN_COEFFICIENT, 5),
        ("EVEN_TO_ODD", even_profile, odd, ODD_COEFFICIENT, 4),
    ):
        scores = matrix @ profile
        effect, folios, sections = effects(scores, y, held)
        held_indices, coefficient = bundle
        null = np.asarray(coefficient @ scores[held_indices], dtype=np.float64)
        p = (1 + int(np.count_nonzero(null >= effect))) / (len(null) + 1)
        deletions = {
            folio: float(np.mean([value for key, value in folios.items() if key != folio]))
            for folio in folios
        }
        concentration = max(abs(value) for value in folios.values()) / sum(abs(value) for value in folios.values())
        gates = {
            "p_at_most_001": p <= .01,
            "effect_at_least_005": effect >= .05,
            "positive_folio_support": sum(value > 0 for value in folios.values()) >= required,
            "both_sections_at_least_005": all(value >= .05 for value in sections.values()),
            "all_deletions_positive": min(deletions.values()) > 0,
            "concentration_at_most_035": concentration <= .35,
        }
        directions[name] = {
            "effect": effect, "p": p,
            "positive_folios": sum(value > 0 for value in folios.values()),
            "folio_count": len(folios), "folio_effects": folios,
            "section_effects": sections, "minimum_deletion": min(deletions.values()),
            "maximum_absolute_folio_concentration": concentration,
            "null_sha256": array_digest(null), "gates": gates,
            "passes": all(gates.values()),
        }
    gates = {
        "odd_to_even": directions["ODD_TO_EVEN"]["passes"],
        "even_to_odd": directions["EVEN_TO_ODD"]["passes"],
        "profile_cosine_at_least_010": cosine >= .10,
    }
    return {
        "profile_cosine": cosine,
        "odd_profile_sha256": array_digest(odd_profile),
        "even_profile_sha256": array_digest(even_profile),
        "directions": directions, "gates": gates, "passes": all(gates.values()),
    }


def base(seed: int) -> list[list[int]]:
    rng = np.random.default_rng(seed)
    weights = np.arange(24, 0, -1, dtype=np.float64)
    weights /= weights.sum()
    return [list(rng.choice(24, size=int(length), p=weights)) for length in G["length"]]


def edit(sequence: list[int], rng: np.random.Generator, strength: float, pattern=(0, 1, 2, 3)) -> None:
    if rng.random() > strength:
        return
    sequence[0], sequence[-1] = pattern[0], pattern[1]
    if len(sequence) >= 4:
        middle = (len(sequence) - 1) // 2
        sequence[middle], sequence[middle + 1] = pattern[2], pattern[3]


def build_world(family: str, world: int) -> tuple[np.ndarray, np.ndarray]:
    seed = 910000 + 1000 * list(("NULL",) + FAMILIES).index(family) + world
    rng = np.random.default_rng(seed)
    sequences = base(seed + 77)
    y = labels()
    if family in {"DISTRIBUTED_FULL", "DISTRIBUTED_HALF"}:
        for index in np.flatnonzero(y == 1): edit(sequences[index], rng, .90 if family.endswith("FULL") else .50)
    elif family == "DISTRIBUTED_START_ONLY":
        for index in np.flatnonzero(y == 1):
            if rng.random() <= .90: sequences[index][0] = 0
    elif family == "ONE_FOLIO":
        for index in np.flatnonzero((y == 1) & (G["folio"] == "f89")): edit(sequences[index], rng, 1.)
    elif family == "ONE_SECTION":
        for index in np.flatnonzero((y == 1) & (G["section"] == "B")): edit(sequences[index], rng, .90)
    elif family == "PAGE_ONLY":
        for index in np.flatnonzero(np.isin(G["page"], sorted(set(G["page"]))[::2])): edit(sequences[index], rng, 1.)
    elif family == "FOLIO_RANDOM":
        for number, folio in enumerate(sorted(set(G["folio"]))):
            pattern = number % 24, (number + 7) % 24, (number + 13) % 24, (number + 19) % 24
            for index in np.flatnonzero((y == 1) & (G["folio"] == folio)): edit(sequences[index], rng, .90, pattern)
    elif family == "PARITY_MISMATCH":
        for index in np.flatnonzero(y == 1):
            pattern = (0, 1, 2, 3) if int(G["folio"][index][1:]) % 2 else (4, 5, 6, 7)
            edit(sequences[index], rng, .90, pattern)
    elif family == "EXACT_IDENTITY_ONLY":
        weights = np.arange(24, 0, -1, dtype=np.float64); weights /= weights.sum()
        for index in np.flatnonzero(y == 1):
            sequences[index] = list(np.random.default_rng(seed + 100000 + index).choice(24, size=len(sequences[index]), p=weights))
    elif family != "NULL":
        raise RuntimeError(family)
    matrix = features(sequences)
    return matrix, y


def worker(task: tuple[str, int]) -> dict[str, object]:
    family, world = task
    matrix, y = build_world(family, world)
    return {"family": family, "world": world, "matrix_sha256": array_digest(matrix), "evaluation": evaluate(matrix, y)}


def main() -> None:
    global G, EVEN_COEFFICIENT, ODD_COEFFICIENT
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise RuntimeError("validation output exists")
    production = json.loads(PRODUCTION.read_text(encoding="utf-8"))
    G = geometry()
    numbers = np.asarray([int(value[1:]) for value in G["folio"]])
    EVEN_COEFFICIENT = coefficients(numbers % 2 == 0)
    ODD_COEFFICIENT = coefficients(numbers % 2 == 1)
    tasks = [("NULL", world) for world in range(64)] + [(family, world) for family in FAMILIES for world in range(8)]
    with mp.get_context("fork").Pool(32) as pool:
        records = pool.map(worker, tasks)
    if records != production["records"]:
        for index, (left, right) in enumerate(zip(records, production["records"], strict=True)):
            if left != right:
                raise RuntimeError(f"record mismatch {index} {left['family']} {left['world']}")
        raise RuntimeError("record mismatch")
    summary = {
        family: {"worlds": sum(r["family"] == family for r in records), "passes": sum(r["family"] == family and r["evaluation"]["passes"] for r in records)}
        for family in ("NULL",) + FAMILIES
    }
    if summary != production["family_summary"]:
        raise RuntimeError("summary mismatch")
    if production["assignment_digests"] != {
        "EVEN_HELD": array_digest(EVEN_COEFFICIENT[1]), "ODD_HELD": array_digest(ODD_COEFFICIENT[1]),
    }:
        raise RuntimeError("assignment digest mismatch")
    checks = len(records) * 31 + 18
    result = {
        "status": "PASS_NONIMPORTING_LRG001_V2_CALIBRATION_RECONSTRUCTION",
        "checks": checks, "discrepancies": 0,
        "records": len(records), "assignments_per_direction": ASSIGNMENTS,
        "family_summary": summary, "decision": production["decision"],
        "production_json_sha256": digest(PRODUCTION),
        "production_report_sha256": digest(PRODUCTION_REPORT),
        "claim_ceiling": production["claim_ceiling"],
    }
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    temporary = OUT_JSON.with_suffix(".json.tmp"); temporary.write_text(text, encoding="utf-8", newline="\n"); temporary.replace(OUT_JSON)
    report = "\n".join([
        "# LRG001 v2 calibration independent validation", "",
        "Status: **PASS_NONIMPORTING_LRG001_V2_CALIBRATION_RECONSTRUCTION**.", "",
        f"A production-free 32-worker implementation reconstructed all **{len(records)}** worlds, both 8,192-assignment matrices, every profile, held effect, null digest, gate, summary, and decision in **{checks}** checks with zero discrepancies.", "",
        "No manuscript family surface, member code, EVA spelling, label profile, identifier, name, meaning, plaintext, or translation was accessed or produced.", "",
    ])
    temporary = OUT_REPORT.with_suffix(".md.tmp"); temporary.write_text(report, encoding="utf-8", newline="\n"); temporary.replace(OUT_REPORT)
    print(text, end="")


if __name__ == "__main__":
    main()
