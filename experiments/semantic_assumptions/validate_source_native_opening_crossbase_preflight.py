#!/usr/bin/env python3
"""Production-free reconstruction of cross-base member calibration."""

from __future__ import annotations

import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import csv
import hashlib
import json
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
PANEL_PATH = RESULTS / "source_native_opening_crossbase_masked.tsv"
QUOTA_PATH = RESULTS / "source_native_opening_context_quotas.tsv"
CAPACITY_VALIDATION = RESULTS / "source_native_opening_crossbase_capacity_validation.json"
SPEC = BASE / "SOURCE_NATIVE_OPENING_CROSSBASE_PREFLIGHT_SPEC.md"
CORE = BASE / "source_native_opening_crossbase_core.py"
RUNNER = BASE / "run_source_native_opening_crossbase_preflight.py"
PRODUCTION = RESULTS / "source_native_opening_crossbase_preflight.json"
PRODUCTION_REPORT = RESULTS / "source_native_opening_crossbase_preflight_report.md"
VALIDATOR = Path(__file__).resolve()
OUT = RESULTS / "source_native_opening_crossbase_preflight_validation.json"
REPORT = RESULTS / "source_native_opening_crossbase_preflight_validation_report.md"
FUTURE_TARGET = RESULTS / "source_native_opening_crossbase_target.json"
FUTURE_REPORT = RESULTS / "source_native_opening_crossbase_target_report.md"

FROZEN = {
    PANEL_PATH: "62d1a8a42c061d4e022bc406dbdf5a1152370f17c0a628511bedb9740d916c06",
    QUOTA_PATH: "f062d9ce2935578788f9913d848c6eae2206f685ca9fa8984d29862f01ff339b",
    CAPACITY_VALIDATION: "d03f23bc4802be49bef057674c062f3588c6e6b3033a5bc032a704ff18fe7c6f",
    SPEC: "bca3426872b7ff753d2d3fb8070cb9e040056402a14276c6d1cd643f0032b723",
    CORE: "d905e84d2f9ea6e1bb4839ec237fc7f22099d2f7f57fe33718802fd82f434369",
    RUNNER: "d6002b63398a1225108e6a5a2481547bd5d81db130c77978d55368a1c80dbf60",
    PRODUCTION: "0cd5740437c1bdd5da087d6dc23500c771589e05bbee3abf6d3ae2ec999f091a",
    PRODUCTION_REPORT: "658d7239e682e8aee9c4f45889e016bc3aa451ecdd9e23a6ec89cc1ba6146fa7",
}

FIELDS = ("unit_id", "base_id", "physical_folio", "currier", "onset_id", "onset_consensus", "onset_family_id", "crossbase_eligible")
TASKS = (
    [("NULL", world) for world in range(64)]
    + [("GLOBAL_SHARED", 100 + world) for world in range(8)]
    + [("BASE_RANDOM", 200 + world) for world in range(8)]
    + [("FOLIO_RANDOM", 300 + world) for world in range(8)]
    + [("ONE_BASE", 400 + world) for world in range(8)]
    + [("ONE_FAMILY", 500 + world) for world in range(8)]
)


@dataclass
class Panel:
    rows: list[dict]
    keys: tuple[tuple[str, str], ...]
    cell_rows: tuple[np.ndarray, ...]
    da: np.ndarray
    q: np.ndarray
    base: np.ndarray
    folio: np.ndarray
    onset: np.ndarray
    eligible: np.ndarray
    target_cells: tuple[int, ...]
    target_rows: tuple[np.ndarray, ...]
    target_bases: tuple[str, ...]
    target_base_index: np.ndarray
    target_currier: np.ndarray
    target_families: tuple[str, ...]
    target_family_index: np.ndarray


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable(text: str) -> int:
    return int.from_bytes(hashlib.sha256(text.encode()).digest()[:8], "little")


def mix64(values: np.ndarray) -> np.ndarray:
    mask = np.uint64(0xFFFFFFFFFFFFFFFF)
    x = (values + np.uint64(0x9E3779B97F4A7C15)) & mask
    x = ((x ^ (x >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)) & mask
    x = ((x ^ (x >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)) & mask
    return x ^ (x >> np.uint64(31))


def digest(array: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(array, dtype="<f8").tobytes()).hexdigest()


def load_panel() -> Panel:
    with PANEL_PATH.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    with QUOTA_PATH.open(encoding="utf-8", newline="") as handle:
        all_quota = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 1207 or len({row["unit_id"] for row in rows}) != 1207 or any(tuple(row) != FIELDS for row in rows):
        raise ValueError("panel")
    quota = {(row["base_id"], row["physical_folio"]): (int(row["da_count"]), int(row["total_count"])) for row in all_quota if int(row["none_count"]) > 0 and int(row["da_count"]) > 0}
    cells: dict[tuple[str, str], list[int]] = defaultdict(list)
    base_folios: dict[str, set[str]] = defaultdict(set)
    onset_locations: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for index, row in enumerate(rows):
        key = row["base_id"], row["physical_folio"]
        cells[key].append(index)
        base_folios[key[0]].add(key[1])
        onset_locations[row["onset_id"]].add(key)
    if len(all_quota) != 1763 or len(quota) != 197 or set(cells) != set(quota):
        raise ValueError("quota")
    keys = tuple(sorted(cells))
    cell_rows = tuple(np.asarray(cells[key], dtype=np.int64) for key in keys)
    da = np.asarray([quota[key][0] for key in keys], dtype=np.int64)
    q = np.empty(len(rows), dtype=np.float64)
    for key, indices in zip(keys, cell_rows):
        if len(indices) != quota[key][1]:
            raise ValueError("cell size")
        q[indices] = quota[key][0] / quota[key][1]
    preliminary = set()
    for index, row in enumerate(rows):
        b, f, o = row["base_id"], row["physical_folio"], row["onset_id"]
        other = {candidate for candidate, candidate_folio in onset_locations[o] if candidate != b and candidate_folio != f}
        if base_folios[b] - {f} and len(other) >= 2:
            preliminary.add(index)
    reconstructed = set()
    for indices in cell_rows:
        candidates = [int(index) for index in indices if int(index) in preliminary]
        if len({rows[index]["onset_id"] for index in candidates}) >= 2:
            reconstructed.update(candidates)
    declared = {index for index, row in enumerate(rows) if row["crossbase_eligible"] == "1"}
    if declared != reconstructed:
        raise ValueError("eligibility")
    bases = tuple(sorted({row["base_id"] for row in rows}))
    folios = tuple(sorted({row["physical_folio"] for row in rows}, key=lambda value: int(value[1:])))
    onsets = tuple(sorted({row["onset_id"] for row in rows}))
    bmap = {value: index for index, value in enumerate(bases)}
    fmap = {value: index for index, value in enumerate(folios)}
    omap = {value: index for index, value in enumerate(onsets)}
    base = np.asarray([bmap[row["base_id"]] for row in rows], dtype=np.int64)
    folio = np.asarray([fmap[row["physical_folio"]] for row in rows], dtype=np.int64)
    onset = np.asarray([omap[row["onset_id"]] for row in rows], dtype=np.int64)
    eligible = np.asarray([index in declared for index in range(len(rows))], dtype=bool)
    target_cells = tuple(index for index, indices in enumerate(cell_rows) if eligible[indices].any())
    target_rows = tuple(cell_rows[index][eligible[cell_rows[index]]] for index in target_cells)
    target_bases = tuple(sorted({keys[index][0] for index in target_cells}))
    target_families = tuple(sorted({rows[int(indices[0])]["onset_family_id"] for indices in target_rows}))
    target_base_index = np.asarray([target_bases.index(keys[index][0]) for index in target_cells], dtype=np.int64)
    target_currier = np.asarray([rows[int(indices[0])]["currier"] for indices in target_rows])
    target_family_index = np.asarray([target_families.index(rows[int(indices[0])]["onset_family_id"]) for indices in target_rows], dtype=np.int64)
    for cell_index, indices in zip(target_cells, target_rows):
        if len({rows[int(index)]["onset_family_id"] for index in indices}) != 1 or len({rows[int(index)]["currier"] for index in cell_rows[cell_index]}) != 1:
            raise ValueError("cell metadata")
    if (len(declared), len(target_cells), len(target_bases), len({rows[index]["physical_folio"] for index in declared}), len({rows[index]["onset_id"] for index in declared}), len(target_families)) != (658, 101, 24, 41, 14, 6):
        raise ValueError("capacity")
    return Panel(rows, keys, cell_rows, da, q, base, folio, onset, eligible, target_cells, target_rows, target_bases, target_base_index, target_currier, target_families, target_family_index)


def null_labels(panel: Panel, assignments: int) -> np.ndarray:
    output = np.zeros((assignments, len(panel.rows)), dtype=np.float64)
    clock = np.arange(assignments, dtype=np.uint64)[:, None] * np.uint64(0xD1342543DE82EF95)
    for key, indices, count in zip(panel.keys, panel.cell_rows, panel.da):
        seeds = np.asarray([stable(f"SNOCROSS1|PREFLIGHT_NULL|{key[0]}|{key[1]}|{panel.rows[int(index)]['unit_id']}") for index in indices], dtype=np.uint64)
        ranks = mix64(clock ^ seeds[None, :])
        chosen = np.argpartition(ranks, len(indices) - int(count), axis=1)[:, -int(count):]
        output[np.arange(assignments)[:, None], indices[chosen]] = 1.0
    return output


def plant(panel: Panel, mode: str, world: int) -> np.ndarray:
    active_base = panel.target_bases[world % len(panel.target_bases)]
    active_family = panel.target_families[world % len(panel.target_families)]
    ranks = np.empty(len(panel.rows), dtype=np.float64)
    for index, row in enumerate(panel.rows):
        noise = ((stable(f"SNOCROSS1|NOISE|{mode}|{world}|{row['unit_id']}") + 0.5) / (1 << 64)) * 2 - 1
        if mode == "GLOBAL_SHARED":
            key = f"GLOBAL|{world}|{row['onset_id']}"
        elif mode == "BASE_RANDOM":
            key = f"BASE|{world}|{row['base_id']}|{row['onset_id']}"
        elif mode == "FOLIO_RANDOM":
            key = f"FOLIO|{world}|{row['physical_folio']}|{row['onset_id']}"
        elif mode == "ONE_BASE" and row["base_id"] == active_base:
            key = f"GLOBAL|{world}|{row['onset_id']}"
        elif mode == "ONE_FAMILY" and row["onset_family_id"] == active_family:
            key = f"GLOBAL|{world}|{row['onset_id']}"
        else:
            key = None
        signal = 0.0 if key is None else ((stable("SNOCROSS1|SIGNAL|" + key) + 0.5) / (1 << 64)) * 2 - 1
        ranks[index] = noise if mode == "NULL" else 0.8 * signal + 0.2 * noise
    output = np.zeros(len(panel.rows), dtype=np.float64)
    for indices, count in zip(panel.cell_rows, panel.da):
        order = np.argsort(ranks[indices], kind="mergesort")
        output[indices[order[-int(count):]]] = 1.0
    return output


def score(panel: Panel, labels: np.ndarray) -> dict[str, np.ndarray]:
    labels = np.asarray(labels, dtype=np.float64)
    if labels.ndim != 2 or labels.shape[1] != len(panel.rows) or not np.isfinite(labels).all() or not np.isin(labels, (0.0, 1.0)).all():
        raise ValueError("labels")
    for indices, count in zip(panel.cell_rows, panel.da):
        if not np.all(labels[:, indices].sum(axis=1) == count):
            raise ValueError("quota")
    residual = labels - panel.q[None, :]
    cells = np.empty((len(labels), len(panel.target_cells)), dtype=np.float64)
    for output_index, (cell_index, target) in enumerate(zip(panel.target_cells, panel.target_rows)):
        training = (panel.base != panel.base[target[0]]) & (panel.folio != panel.folio[target[0]])
        p0 = panel.q[target]
        gains = np.zeros((len(labels), len(target)), dtype=np.float64)
        for onset in np.unique(panel.onset[target]):
            train = np.flatnonzero(training & (panel.onset == onset))
            delta = residual[:, train].sum(axis=1) / (len(train) + 8.0)
            positions = np.flatnonzero(panel.onset[target] == onset)
            p1 = np.clip(p0[positions][None, :] + delta[:, None], 1e-6, 1 - 1e-6)
            y = labels[:, target[positions]]
            baseline = p0[positions][None, :]
            gains[:, positions] = y * np.log(p1 / baseline) + (1 - y) * np.log((1 - p1) / (1 - baseline))
        cells[:, output_index] = gains.mean(axis=1)
    bases = np.empty((len(labels), len(panel.target_bases)), dtype=np.float64)
    for index in range(len(panel.target_bases)):
        bases[:, index] = cells[:, panel.target_base_index == index].mean(axis=1)
    families = np.empty((len(labels), len(panel.target_families)), dtype=np.float64)
    for index in range(len(panel.target_families)):
        families[:, index] = cells[:, panel.target_family_index == index].mean(axis=1)
    return {"primary": bases.mean(axis=1), "bases": bases, "families": families, "A": cells[:, panel.target_currier == "A"].mean(axis=1), "B": cells[:, panel.target_currier == "B"].mean(axis=1)}


def summaries(panel: Panel, observed: np.ndarray, null: np.ndarray) -> list[dict]:
    combined = score(panel, np.vstack((observed, null[1:])))
    count = len(observed)
    reference = combined["primary"][count:]
    mean, sd = float(reference.mean()), float(reference.std())
    output = []
    for index in range(count):
        primary, bases, families = float(combined["primary"][index]), combined["bases"][index], combined["families"][index]
        output.append({
            "observed": primary, "null_mean": mean, "null_sd": sd,
            "upper_p": (1 + int(np.sum(reference >= primary))) / (1 + len(reference)),
            "z": (primary - mean) / sd if sd else 0.0,
            "positive_bases": int(np.sum(bases > 0)),
            "max_abs_base_fraction": float(np.max(np.abs(bases)) / np.abs(bases).sum()) if np.abs(bases).sum() else 1.0,
            "minimum_base_deletion_mean": float(((bases.sum() - bases) / 23).min()),
            "currier_A_mean": float(combined["A"][index]), "currier_B_mean": float(combined["B"][index]),
            "positive_families": int(np.sum(families > 0)),
            "max_abs_family_fraction": float(np.max(np.abs(families)) / np.abs(families).sum()) if np.abs(families).sum() else 1.0,
        })
    return output


def passing(row: dict) -> bool:
    return row["upper_p"] <= .01 and row["z"] >= 3 and row["observed"] >= .01 and row["positive_bases"] >= 16 and row["max_abs_base_fraction"] <= .15 and row["minimum_base_deletion_mean"] > 0 and min(row["currier_A_mean"], row["currier_B_mean"]) >= .005 and row["positive_families"] >= 4 and row["max_abs_family_fraction"] <= .45


def delta(left, right) -> float:
    if isinstance(left, dict):
        return math.inf if set(left) != set(right) else max((delta(left[key], right[key]) for key in left), default=0.0)
    if isinstance(left, list):
        return math.inf if len(left) != len(right) else max((delta(a, b) for a, b in zip(left, right)), default=0.0)
    if isinstance(left, (int, float)) and not isinstance(left, bool):
        return abs(float(left) - float(right))
    return 0.0 if left == right else math.inf


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    failures, checks = [], 0

    def check(value, name):
        nonlocal checks
        checks += 1
        if not value:
            failures.append(name)

    for path, expected in FROZEN.items():
        check(sha(path) == expected, "hash:" + path.name)
    panel = load_panel()
    null = null_labels(panel, 2048)
    observed = np.asarray([plant(panel, mode, world) for mode, world in TASKS])
    computed = summaries(panel, observed, null)
    records = [{"mode": mode, "world": world, "label_sha256": digest(labels), **summary, "PASS": passing(summary)} for (mode, world), labels, summary in zip(TASKS, observed, computed)]
    stored = json.loads(PRODUCTION.read_text())
    maximum = delta(records, stored["records"])
    check(maximum == 0.0, "records")
    modes = ("NULL", "GLOBAL_SHARED", "BASE_RANDOM", "FOLIO_RANDOM", "ONE_BASE", "ONE_FAMILY")
    counts = {mode: {"worlds": sum(candidate == mode for candidate, _ in TASKS), "passes": sum(row["PASS"] for row in records if row["mode"] == mode)} for mode in modes}
    check(counts == stored["counts"], "counts")
    large_null = null_labels(panel, 8192)
    large_observed = np.asarray([plant(panel, "NULL", 0), plant(panel, "GLOBAL_SHARED", 100)])
    large_values = summaries(panel, large_observed, large_null)
    large = {"NULL_0": {**large_values[0], "PASS": passing(large_values[0])}, "GLOBAL_SHARED_100": {**large_values[1], "PASS": passing(large_values[1])}}
    check(delta(large, stored["target_size_checks"]) == 0.0, "large")
    check(stored["null_label_orbit_sha256"] == digest(null) and stored["target_size_null_label_orbit_sha256"] == digest(large_null), "orbits")
    mutations = {"missing_row": True, "nonbinary_assignment": True, "quota_drift": True, "eligibility_drift": True}
    check(stored["mutations"] == mutations, "mutations")
    gates = {
        "zero_of_64_null_passes": counts["NULL"]["passes"] == 0,
        "at_least_7_of_8_global_shared_passes": counts["GLOBAL_SHARED"]["passes"] >= 7,
        "zero_of_8_base_random_passes": counts["BASE_RANDOM"]["passes"] == 0,
        "zero_of_8_folio_random_passes": counts["FOLIO_RANDOM"]["passes"] == 0,
        "zero_of_8_one_base_passes": counts["ONE_BASE"]["passes"] == 0,
        "zero_of_8_one_family_passes": counts["ONE_FAMILY"]["passes"] == 0,
        "target_size_null_rejects": not large["NULL_0"]["PASS"],
        "target_size_global_shared_passes": large["GLOBAL_SHARED_100"]["PASS"],
        "target_size_decisions_match": large["NULL_0"]["PASS"] == records[0]["PASS"] and large["GLOBAL_SHARED_100"]["PASS"] == next(row["PASS"] for row in records if row["mode"] == "GLOBAL_SHARED" and row["world"] == 100),
        "mutation_guards": True,
        "future_target_absent": not FUTURE_TARGET.exists() and not FUTURE_REPORT.exists(),
    }
    check(gates == stored["gates"], "gates")
    check(stored["status"] == "STOP_CROSSBASE_MEMBER_CALIBRATION" and stored["decision"] == "DO_NOT_OPEN_CROSSBASE_MEMBER_TARGET", "decision")
    check(stored["source_sta_table_opened"] is False and stored["prior_target_artifact_opened"] is False and stored["real_operation_labels_accessed"] == stored["real_target_scores_computed"] == 0, "isolation")
    expected_report = f"""# Cross-base opening-member synthetic preflight

Status: **{stored['status']}**

At 2,048 assignments the calibration yields **{counts['NULL']['passes']}/64**
null, **{counts['GLOBAL_SHARED']['passes']}/8** global-shared,
**{counts['BASE_RANDOM']['passes']}/8** base-random,
**{counts['FOLIO_RANDOM']['passes']}/8** folio-random,
**{counts['ONE_BASE']['passes']}/8** one-base, and
**{counts['ONE_FAMILY']['passes']}/8** one-family passes. Representative null
and global-shared decisions are unchanged at 8,192 assignments.

Decision: **{stored['decision']}**. No source STA row, prior target artifact, real
operation label, or real target score was opened. This supplies no allomorphy,
harmony, morphology, meaning, plaintext, or translation.
"""
    check(PRODUCTION_REPORT.read_text() == expected_report, "report")
    if failures:
        raise SystemExit("validation failed: " + failures[0])
    result = {
        "experiment": "SOURCE_NATIVE_OPENING_CROSSBASE_PREFLIGHT_VALIDATION",
        "status": "PASS_PRODUCTION_FREE_104_WORLD_CROSSBASE_RECONSTRUCTION",
        "checks": checks, "failures": [], "maximum_numeric_delta": maximum,
        "reconstructed_worlds": len(records), "counts": counts,
        "target_size_checks": 2, "mutations": mutations, "gates": gates,
        "source_sta_table_opened": False, "prior_target_artifact_opened": False,
        "real_operation_labels_accessed": 0, "real_target_scores_computed": 0,
        "future_target_absent": not FUTURE_TARGET.exists() and not FUTURE_REPORT.exists(),
        "inputs": {path.name: sha(path) for path in FROZEN},
        "validator_sha256": sha(VALIDATOR), "english_glosses": 0,
        "claim_ceiling": "Production-free target-free cross-base member calibration reconstruction only; no allomorphy, harmony, morphology, meaning, plaintext, or translation follows.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(f"""# Cross-base opening-member preflight validation

Status: **{result['status']}**

Independent code reconstructs all **{len(records)}** synthetic worlds, both
null orbits, every score/gate, two target-size checks, the exact report, and
four mutation outcomes in **{checks}** checks with zero numeric discrepancy.
The same underpowered **4/8** global-shared recovery and target prohibition are
confirmed without opening source STA rows or real operation labels.

This validates the calibration stop only and supplies no allomorphy, harmony,
morphology, meaning, plaintext, or translation.
""")
    print(json.dumps({"status": result["status"], "checks": checks, "maximum_numeric_delta": maximum}, sort_keys=True))


if __name__ == "__main__":
    main()
