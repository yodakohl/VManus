#!/usr/bin/env python3
"""Production-free reconstruction of opening-onset calibration."""

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
PANEL_PATH = RESULTS / "source_native_opening_onset_masked.tsv"
QUOTA_PATH = RESULTS / "source_native_opening_context_quotas.tsv"
CAPACITY = RESULTS / "source_native_opening_onset_capacity.json"
CAPACITY_VALIDATION = RESULTS / "source_native_opening_onset_capacity_validation.json"
SPEC = BASE / "SOURCE_NATIVE_OPENING_ONSET_PREFLIGHT_SPEC.md"
CORE = BASE / "source_native_opening_onset_core.py"
RUNNER = BASE / "run_source_native_opening_onset_preflight.py"
PRODUCTION = RESULTS / "source_native_opening_onset_preflight.json"
PRODUCTION_REPORT = RESULTS / "source_native_opening_onset_preflight_report.md"
VALIDATOR = Path(__file__).resolve()
OUT = RESULTS / "source_native_opening_onset_preflight_validation.json"
REPORT = RESULTS / "source_native_opening_onset_preflight_validation_report.md"
TARGET = RESULTS / "source_native_opening_onset_target.json"
TARGET_REPORT = RESULTS / "source_native_opening_onset_target_report.md"

FROZEN = {
    PANEL_PATH: "628d2f657db080b975f2e201d6d684f3dab7ede75b19be6cc4e4c4b3f580e4a2",
    QUOTA_PATH: "f062d9ce2935578788f9913d848c6eae2206f685ca9fa8984d29862f01ff339b",
    CAPACITY: "086718ac1bb1563dbcf212b349cd95d1875d481e08be01662ab4a31d8d1975e4",
    CAPACITY_VALIDATION: "bdb86a58e5ee0ef9850554d7b65685c9cf0a35f1af06cefd30f676e17ec6abed",
    SPEC: "121aab44a4ec43a6b0da15487604d4a0463bea761f0845c930d0d076bc8ef657",
    CORE: "33c1870c0e8f80516a02573a279f78b2eba4b12a2b2225bfe864525d18bc2adf",
    RUNNER: "2e525f5098e3d734c0dcedac8bec270d0b8c38418c609f2556a7b38173c68425",
    PRODUCTION: "412cd477eb96a9679cc7d9273f3eeb3fbf547c790138fb95099cc10650c963a5",
    PRODUCTION_REPORT: "30d1c21b20a7a2f6bf05a7a5aca3a90c62078d06afe25664fd24dbee1c190879",
}

TASKS = (
    [("NULL", world) for world in range(64)]
    + [("GLOBAL_ONSET", 100 + world) for world in range(8)]
    + [("ONE_FOLIO", 200 + world) for world in range(8)]
    + [("FOLIO_RANDOM", 300 + world) for world in range(8)]
    + [("ONE_BASE", 400 + world) for world in range(8)]
)


@dataclass
class Panel:
    rows: list[dict]
    strata: tuple[tuple[str, str], ...]
    strata_rows: tuple[np.ndarray, ...]
    quota: np.ndarray
    folios: tuple[str, ...]
    folio_index: np.ndarray
    registers: tuple[str, ...]
    bases: tuple[str, ...]
    base_index: np.ndarray
    pairs: tuple[tuple[str, str], ...]
    pair_index: np.ndarray
    pair_base: np.ndarray
    eligible: np.ndarray


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable(text):
    return int.from_bytes(hashlib.sha256(text.encode()).digest()[:8], "little")


def mix64(values):
    mask = np.uint64(0xFFFFFFFFFFFFFFFF)
    answer = (values + np.uint64(0x9E3779B97F4A7C15)) & mask
    answer = ((answer ^ (answer >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)) & mask
    answer = ((answer ^ (answer >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)) & mask
    return answer ^ (answer >> np.uint64(31))


def load_panel():
    with PANEL_PATH.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    with QUOTA_PATH.open(encoding="utf-8", newline="") as handle:
        quota_rows = list(csv.DictReader(handle, delimiter="\t"))
    quota_map = {(row["base_id"], row["physical_folio"]): (int(row["none_count"]), int(row["da_count"]), int(row["total_count"])) for row in quota_rows}
    grouped = defaultdict(list)
    for index, row in enumerate(rows):
        grouped[(row["base_id"], row["physical_folio"])].append(index)
    mixed = tuple(sorted(key for key, values in quota_map.items() if values[0] and values[1]))
    if len(rows) != 1207 or len({row["unit_id"] for row in rows}) != 1207 or len(quota_map) != 1763 or set(grouped) != set(mixed) or len(mixed) != 197:
        raise ValueError("panel")
    if any(len(grouped[key]) != quota_map[key][2] or quota_map[key][0] + quota_map[key][1] != quota_map[key][2] for key in mixed):
        raise ValueError("quotas")
    folios = tuple(sorted({row["physical_folio"] for row in rows}, key=lambda value: int(value[1:])))
    bases = tuple(sorted({row["base_id"] for row in rows}))
    pairs = tuple(sorted({(row["base_id"], row["onset_id"]) for row in rows}))
    fmap = {value: index for index, value in enumerate(folios)}
    bmap = {value: index for index, value in enumerate(bases)}
    pmap = {value: index for index, value in enumerate(pairs)}
    fi = np.asarray([fmap[row["physical_folio"]] for row in rows], dtype=np.int64)
    bi = np.asarray([bmap[row["base_id"]] for row in rows], dtype=np.int64)
    pi = np.asarray([pmap[(row["base_id"], row["onset_id"])] for row in rows], dtype=np.int64)
    pair_base = np.asarray([bmap[base] for base, _ in pairs], dtype=np.int64)
    support = {pair: {row["physical_folio"] for row in rows if (row["base_id"], row["onset_id"]) == pair} for pair in pairs}
    eligible = np.asarray([len(support[(row["base_id"], row["onset_id"])]) >= 2 for row in rows], dtype=bool)
    registers = []
    for folio in folios:
        values = {row["currier"] for row in rows if row["physical_folio"] == folio}
        if len(values) != 1 or not values <= {"A", "B"}:
            raise ValueError("register")
        registers.append(next(iter(values)))
    if len(folios) != 59 or len(bases) != 44 or len(pairs) != 95 or int(eligible.sum()) != 1141:
        raise ValueError("capacity")
    return Panel(rows, mixed, tuple(np.asarray(grouped[key], dtype=np.int64) for key in mixed), np.asarray([quota_map[key][1] for key in mixed], dtype=np.int64), folios, fi, tuple(registers), bases, bi, pairs, pi, pair_base, eligible)


def labels_from_ranks(panel, assignments, domain):
    answer = np.zeros((assignments, len(panel.rows)), dtype=np.float64)
    clock = np.arange(assignments, dtype=np.uint64)[:, None] * np.uint64(0xD1342543DE82EF95)
    for key, indices, count in zip(panel.strata, panel.strata_rows, panel.quota):
        seeds = np.asarray([stable(f"SNOONSET1|{domain}|{key[0]}|{key[1]}|{panel.rows[index]['unit_id']}") for index in indices], dtype=np.uint64)
        ranks = mix64(clock ^ seeds[None, :])
        chosen = np.argpartition(ranks, len(indices) - int(count), axis=1)[:, -int(count):]
        answer[np.arange(assignments)[:, None], indices[chosen]] = 1.0
    return answer


def plant(panel, mode, world):
    active_folio = world % len(panel.folios)
    active_base = world % len(panel.bases)
    rank = np.empty(len(panel.rows), dtype=np.float64)
    for index, row in enumerate(panel.rows):
        noise = ((stable(f"SNOONSET1|NOISE|{mode}|{world}|{row['unit_id']}") + 0.5) / (1 << 64)) * 2 - 1
        signal = 0.0
        if mode == "GLOBAL_ONSET":
            domain = f"GLOBAL|{world}|{row['base_id']}|{row['onset_id']}"
        elif mode == "FOLIO_RANDOM":
            domain = f"FOLIO|{world}|{row['physical_folio']}|{row['base_id']}|{row['onset_id']}"
        elif mode == "ONE_FOLIO" and panel.folio_index[index] == active_folio:
            domain = f"GLOBAL|{world}|{row['base_id']}|{row['onset_id']}"
        elif mode == "ONE_BASE" and panel.base_index[index] == active_base:
            domain = f"GLOBAL|{world}|{row['base_id']}|{row['onset_id']}"
        else:
            domain = None
        if domain is not None:
            signal = ((stable("SNOONSET1|SIGNAL|" + domain) + 0.5) / (1 << 64)) * 2 - 1
        rank[index] = noise if mode == "NULL" else 0.8 * signal + 0.2 * noise
    output = np.zeros(len(panel.rows), dtype=np.float64)
    for indices, count in zip(panel.strata_rows, panel.quota):
        order = np.argsort(rank[indices], kind="mergesort")
        output[indices[order[-int(count):]]] = 1.0
    return output


def count_categories(labels, index, size):
    output = np.zeros((len(labels), size), dtype=np.float64)
    for value in range(size):
        output[:, value] = labels[:, index == value].sum(axis=1)
    return output


def score(panel, labels):
    labels = np.asarray(labels, dtype=np.float64)
    if labels.ndim != 2 or labels.shape[1] != len(panel.rows) or not np.isfinite(labels).all() or not np.isin(labels, (0.0, 1.0)).all():
        raise ValueError("labels")
    for indices, count in zip(panel.strata_rows, panel.quota):
        if not np.all(labels[:, indices].sum(1) == count):
            raise ValueError("label quota")
    base_n = np.bincount(panel.base_index, minlength=len(panel.bases)).astype(np.float64)
    pair_n = np.bincount(panel.pair_index, minlength=len(panel.pairs)).astype(np.float64)
    base_d = count_categories(labels, panel.base_index, len(panel.bases))
    pair_d = count_categories(labels, panel.pair_index, len(panel.pairs))
    folio_scores = np.zeros((len(labels), 59), dtype=np.float64)
    for held in range(59):
        held_mask = panel.folio_index == held
        test = held_mask & panel.eligible
        held_base_n = np.bincount(panel.base_index[held_mask], minlength=len(panel.bases)).astype(np.float64)
        held_pair_n = np.bincount(panel.pair_index[held_mask], minlength=len(panel.pairs)).astype(np.float64)
        held_base_d = count_categories(labels[:, held_mask], panel.base_index[held_mask], len(panel.bases))
        held_pair_d = count_categories(labels[:, held_mask], panel.pair_index[held_mask], len(panel.pairs))
        pb = (base_d - held_base_d + 0.5) / (base_n[None, :] - held_base_n[None, :] + 1.0)
        pp = (pair_d - held_pair_d + 4.0 * pb[:, panel.pair_base]) / (pair_n[None, :] - held_pair_n[None, :] + 4.0)
        y = labels[:, test]
        p0 = pb[:, panel.base_index[test]]
        p1 = pp[:, panel.pair_index[test]]
        folio_scores[:, held] = (y * np.log(p1 / p0) + (1 - y) * np.log((1 - p1) / (1 - p0))).mean(1)
    if not np.isfinite(folio_scores).all():
        raise ValueError("finite")
    return folio_scores.mean(1), folio_scores


def summaries(panel, observed, null):
    count = len(observed)
    statistic, folds = score(panel, np.vstack((observed, null[1:])))
    reference = statistic[count:]
    mean = float(reference.mean())
    sd = float(reference.std())
    registers = np.asarray(panel.registers)
    output = []
    for index in range(count):
        values = folds[index]
        observed_value = float(statistic[index])
        denominator = float(np.abs(values).sum())
        output.append({
            "observed": observed_value, "null_mean": mean, "null_sd": sd,
            "upper_p": (1 + int(np.sum(reference >= observed_value))) / (1 + len(reference)),
            "z": (observed_value - mean) / sd if sd else 0.0,
            "positive_folios": int(np.sum(values > 0)),
            "max_abs_contribution_fraction": float(np.max(np.abs(values)) / denominator) if denominator else 1.0,
            "minimum_deletion_mean": float(((values.sum() - values) / 58).min()),
            "currier_A_mean": float(values[registers == "A"].mean()),
            "currier_B_mean": float(values[registers == "B"].mean()),
        })
    return output


def passing(row):
    return row["upper_p"] <= 0.01 and row["z"] >= 3 and row["observed"] >= 0.01 and row["positive_folios"] >= 36 and row["max_abs_contribution_fraction"] <= 0.15 and row["minimum_deletion_mean"] > 0 and min(row["currier_A_mean"], row["currier_B_mean"]) >= 0.005


def digest(array):
    return hashlib.sha256(np.ascontiguousarray(array, dtype="<f8").tobytes()).hexdigest()


def numeric_delta(left, right):
    if isinstance(left, dict):
        return math.inf if set(left) != set(right) else max((numeric_delta(left[key], right[key]) for key in left), default=0.0)
    if isinstance(left, list):
        return math.inf if len(left) != len(right) else max((numeric_delta(a, b) for a, b in zip(left, right)), default=0.0)
    if isinstance(left, (int, float)) and not isinstance(left, bool):
        return abs(float(left) - float(right))
    return 0.0 if left == right else math.inf


def main():
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    failures = []
    checks = 0

    def check(value, name):
        nonlocal checks
        checks += 1
        if not value:
            failures.append(name)

    for path, expected in FROZEN.items():
        check(sha(path) == expected, "hash:" + path.name)
    panel = load_panel()
    null = labels_from_ranks(panel, 2048, "PREFLIGHT_NULL")
    observed = np.asarray([plant(panel, mode, world) for mode, world in TASKS])
    rebuilt_summaries = summaries(panel, observed, null)
    records = [{"mode": mode, "world": world, "label_sha256": digest(labels), **summary, "PASS": passing(summary)} for (mode, world), labels, summary in zip(TASKS, observed, rebuilt_summaries)]
    stored = json.loads(PRODUCTION.read_text())
    maximum = numeric_delta(records, stored["records"])
    check(maximum == 0, "records")
    counts = {mode: {"worlds": sum(candidate == mode for candidate, _ in TASKS), "passes": sum(row["PASS"] for row in records if row["mode"] == mode)} for mode in ("NULL", "GLOBAL_ONSET", "ONE_FOLIO", "FOLIO_RANDOM", "ONE_BASE")}
    check(counts == stored["counts"], "counts")
    large_null = labels_from_ranks(panel, 8192, "PREFLIGHT_NULL")
    large_observed = np.asarray([plant(panel, "NULL", 0), plant(panel, "GLOBAL_ONSET", 100)])
    large_values = summaries(panel, large_observed, large_null)
    large = {"NULL_0": {**large_values[0], "PASS": passing(large_values[0])}, "GLOBAL_ONSET_100": {**large_values[1], "PASS": passing(large_values[1])}}
    check(numeric_delta(large, stored["target_size_checks"]) == 0, "large")
    check(stored["null_label_orbit_sha256"] == digest(null) and stored["target_size_null_label_orbit_sha256"] == digest(large_null), "orbits")
    small_null = records[0]
    small_global = next(row for row in records if row["mode"] == "GLOBAL_ONSET" and row["world"] == 100)
    mutations = {}
    reference = observed[:1]
    candidates = {
        "missing_row": reference[:, :-1],
        "nonbinary_label": reference.copy(),
        "quota_drift": reference.copy(),
    }
    candidates["nonbinary_label"][0, 0] = 0.5
    candidates["quota_drift"][0, panel.strata_rows[0][0]] = 1 - candidates["quota_drift"][0, panel.strata_rows[0][0]]
    for name, candidate in candidates.items():
        try: score(panel, candidate)
        except ValueError: mutations[name] = True
        else: mutations[name] = False
    check(mutations == stored["mutations"] and all(mutations.values()), "mutations")
    gates = {
        "zero_of_64_null_passes": counts["NULL"]["passes"] == 0,
        "at_least_7_of_8_global_onset_passes": counts["GLOBAL_ONSET"]["passes"] >= 7,
        "zero_of_8_one_folio_passes": counts["ONE_FOLIO"]["passes"] == 0,
        "zero_of_8_folio_random_passes": counts["FOLIO_RANDOM"]["passes"] == 0,
        "zero_of_8_one_base_passes": counts["ONE_BASE"]["passes"] == 0,
        "target_size_null_rejects": not large["NULL_0"]["PASS"],
        "target_size_global_onset_passes": large["GLOBAL_ONSET_100"]["PASS"],
        "target_size_decisions_match": large["NULL_0"]["PASS"] == small_null["PASS"] and large["GLOBAL_ONSET_100"]["PASS"] == small_global["PASS"],
        "mutation_guards": all(mutations.values()),
        "target_outputs_absent": not TARGET.exists() and not TARGET_REPORT.exists(),
    }
    check(stored["gates"] == gates and all(gates.values()), "gates")
    check(stored["status"] == "PASS_TARGET_FREE_OPENING_ONSET_PREFLIGHT" and stored["decision"] == "GO_INDEPENDENTLY_VALIDATE_OPENING_ONSET_PREFLIGHT", "decision")
    check(stored["target_source_opened"] is False and stored["real_operation_labels_accessed"] == 0 and stored["real_target_scores_computed"] == 0 and stored["target_outputs_absent"] is True, "isolation")
    expected_report = f"""# Opening-onset compatibility preflight

Status: **{stored['status']}**

At 2,048 assignments the grid yields **{counts['NULL']['passes']}/64** null,
**{counts['GLOBAL_ONSET']['passes']}/8** distributed global-onset,
**{counts['ONE_FOLIO']['passes']}/8** one-folio,
**{counts['FOLIO_RANDOM']['passes']}/8** folio-random, and
**{counts['ONE_BASE']['passes']}/8** one-base passes. The representative null
and global-onset decisions are unchanged at 8,192 assignments. Calibration is
**passing**.

No real operation label or target score was opened. Decision:
**{stored['decision']}**. This supplies no morphology, meaning, or translation.
"""
    check(PRODUCTION_REPORT.read_text() == expected_report, "report")
    if failures:
        raise SystemExit("validation failed: " + failures[0])
    result = {
        "experiment": "SOURCE_NATIVE_OPENING_ONSET_PREFLIGHT_VALIDATION",
        "status": "PASS_PRODUCTION_FREE_96_WORLD_ONSET_CALIBRATION_RECONSTRUCTION",
        "checks": checks, "failures": [], "maximum_numeric_delta": maximum,
        "reconstructed_worlds": len(records), "counts": counts,
        "target_size_checks": 2, "mutations": mutations,
        "target_source_opened": False, "real_operation_labels_accessed": 0,
        "real_target_scores_computed": 0, "target_outputs_absent": not TARGET.exists() and not TARGET_REPORT.exists(),
        "inputs": {path.name: sha(path) for path in FROZEN},
        "validator_sha256": sha(VALIDATOR), "english_glosses": 0,
        "claim_ceiling": "Production-free target-free onset calibration reconstruction only; no morphology, meaning, or translation follows.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(f"""# Opening-onset preflight validation

Status: **{result['status']}**

A production-free implementation reconstructs all **{len(records)}** synthetic
worlds, both complete null orbits, two target-size checks, every score and
gate, report, and three mutations in **{checks}** checks with zero numeric
discrepancy. Real operation labels and target scores remain unopened.

This validates one future frozen target only and supplies no morphology,
meaning, or translation.
""")
    print(json.dumps({"status": result["status"], "checks": checks, "maximum_numeric_delta": maximum}, sort_keys=True))


if __name__ == "__main__":
    main()
