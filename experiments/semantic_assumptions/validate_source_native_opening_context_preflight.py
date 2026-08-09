#!/usr/bin/env python3
"""CPU clean-room reconstruction of opening-context synthetic calibration."""

from __future__ import annotations

import os

os.environ["OPENBLAS_NUM_THREADS"] = "32"
os.environ["OMP_NUM_THREADS"] = "32"
os.environ["MKL_NUM_THREADS"] = "32"

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
PANEL = RESULTS / "source_native_opening_context_masked.tsv"
QUOTAS = RESULTS / "source_native_opening_context_quotas.tsv"
CAPACITY_VALIDATION = RESULTS / "source_native_opening_context_capacity_validation.json"
CORE = BASE / "source_native_opening_context_core.py"
SPEC = BASE / "SOURCE_NATIVE_OPENING_CONTEXT_PREFLIGHT_SPEC.md"
RUNNER = BASE / "run_source_native_opening_context_preflight.py"
PRODUCTION = RESULTS / "source_native_opening_context_preflight.json"
PRODUCTION_REPORT = RESULTS / "source_native_opening_context_preflight_report.md"
TARGET = RESULTS / "source_native_opening_context_target.json"
TARGET_REPORT = RESULTS / "source_native_opening_context_target_report.md"
OUT = RESULTS / "source_native_opening_context_preflight_validation.json"
REPORT = RESULTS / "source_native_opening_context_preflight_validation_report.md"
FROZEN = {
    PANEL: "6a043ba095d118594c9a8bd4bd4bf0ac96778963be0637400e353c517c5e616a",
    QUOTAS: "f062d9ce2935578788f9913d848c6eae2206f685ca9fa8984d29862f01ff339b",
    CAPACITY_VALIDATION: "32dda1eedfa4ea2135583ddaa1593970b279aaab91d3f1fd3c1c75b629dafe53",
    CORE: "fe6d473758c744ee50f800fba3246d773a26daf7226447db685639561090a5cd",
    SPEC: "ea0e63888e684ea111ff03b0463a133bcba140b0382252240fdc50eb0c6f4be2",
    RUNNER: "b02d83e6a9530bb32de522e62def68768095f0fd2394de3b0150fc6485425f01",
    PRODUCTION: "c78534f1bf10c6e901c7dea896119eaa9e82b3a4c8229f61ea2903f7cb6c3f68",
    PRODUCTION_REPORT: "27e6815d6ce292814959f9eda172e5cb406e5efa278d86ef166499512d08a0ba",
}
TASKS = (
    [("NULL", world) for world in range(64)]
    + [("POSITION", 100 + world) for world in range(8)]
    + [("NEIGHBOR", 200 + world) for world in range(8)]
    + [("ONE_FOLIO", 300 + world) for world in range(8)]
    + [("FOLIO_RANDOM", 400 + world) for world in range(8)]
    + [("ONE_BASE", 500 + world) for world in range(8)]
)
REPRESENTATIVES = (("NULL", 0), ("POSITION", 100), ("NEIGHBOR", 200), ("ONE_FOLIO", 300), ("FOLIO_RANDOM", 400), ("ONE_BASE", 500))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable(text: str) -> int:
    return int.from_bytes(hashlib.sha256(text.encode()).digest()[:8], "little")


def splitmix(values):
    mask = np.uint64(0xFFFFFFFFFFFFFFFF)
    z = (values + np.uint64(0x9E3779B97F4A7C15)) & mask
    z = ((z ^ (z >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)) & mask
    z = ((z ^ (z >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)) & mask
    return z ^ (z >> np.uint64(31))


def one_hot(values, names=None):
    names = tuple(sorted(set(values))) if names is None else tuple(names)
    lookup = {value: index for index, value in enumerate(names)}
    answer = np.zeros((len(values), len(names)), dtype=np.float64)
    answer[np.arange(len(values)), [lookup[value] for value in values]] = 1.0
    return answer, names


def center(matrix, strata):
    answer = matrix.copy()
    for indices in strata:
        answer[indices] -= answer[indices].mean(axis=0)
    return answer


def standardize(matrix, names):
    scale = np.sqrt(np.mean(matrix * matrix, axis=0))
    keep = scale > 1e-10
    return matrix[:, keep] / scale[keep], tuple(value for value, flag in zip(names, keep) if flag)


def load():
    with PANEL.open(encoding="utf-8", newline="") as handle:
        all_rows = list(csv.DictReader(handle, delimiter="\t"))
    with QUOTAS.open(encoding="utf-8", newline="") as handle:
        quota_rows = list(csv.DictReader(handle, delimiter="\t"))
    quota = {(row["base_id"], row["physical_folio"]): (int(row["none_count"]), int(row["da_count"]), int(row["total_count"])) for row in quota_rows}
    grouped = defaultdict(list)
    for index, row in enumerate(all_rows):
        grouped[(row["base_id"], row["physical_folio"])].append(index)
    if len(all_rows) != 5826 or len(quota) != 1763 or set(grouped) != set(quota):
        raise ValueError("geometry")
    keys = tuple(sorted(key for key, value in quota.items() if value[0] and value[1]))
    old_indices = [index for key in keys for index in grouped[key]]
    rows = [all_rows[index] for index in old_indices]
    remap = {old: new for new, old in enumerate(old_indices)}
    strata = tuple(np.asarray([remap[index] for index in grouped[key]], dtype=np.int64) for key in keys)
    da_counts = np.asarray([quota[key][1] for key in keys], dtype=np.int64)
    probabilities = np.empty(len(rows))
    for indices, count in zip(strata, da_counts):
        probabilities[indices] = count / len(indices)
    folios = tuple(sorted({row["physical_folio"] for row in rows}, key=lambda value: int(value[1:])))
    bases = tuple(sorted({row["base_id"] for row in rows}))
    folio_index = np.asarray([folios.index(row["physical_folio"]) for row in rows])
    base_index = np.asarray([bases.index(row["base_id"]) for row in rows])
    folio_currier = tuple(next(iter({row["currier"] for row in rows if row["physical_folio"] == folio})) for folio in folios)
    pos_raw, pos_names = one_hot([row["locus_role"] for row in rows], ("FIRST", "LAST", "MIDDLE", "SINGLE"))
    count_raw, _ = one_hot([row["group_count"] for row in rows])
    left_raw, left_names = one_hot([row["left_context"] for row in rows])
    right_raw, right_names = one_hot([row["right_context"] for row in rows])
    position, pos_names = standardize(center(pos_raw, strata), pos_names)
    nuisance = center(np.column_stack((pos_raw, count_raw)), strata)
    neighbor = center(np.column_stack((left_raw, right_raw)), strata)
    neighbor -= nuisance @ np.linalg.lstsq(nuisance, neighbor, rcond=None)[0]
    neighbor_names = tuple("L:" + value for value in left_names) + tuple("R:" + value for value in right_names)
    neighbor, neighbor_names = standardize(neighbor, neighbor_names)
    if len(rows) != 1207 or len(strata) != 197 or len(folios) != 59 or len(bases) != 44 or position.shape != (1207, 3) or neighbor.shape != (1207, 25):
        raise ValueError("feature capacity")
    return rows, keys, strata, da_counts, probabilities, folios, folio_index, folio_currier, bases, base_index, position, neighbor, pos_names, neighbor_names


def orbit(rows, keys, strata, counts, assignments, domain):
    result = np.zeros((assignments, len(rows)))
    clock = np.arange(assignments, dtype=np.uint64)[:, None] * np.uint64(0xD1342543DE82EF95)
    for key, indices, count in zip(keys, strata, counts):
        seeds = np.asarray([stable(f"SNOCCTX1|{domain}|{key[0]}|{key[1]}|{rows[index]['unit_id']}") for index in indices], dtype=np.uint64)
        ranks = splitmix(clock ^ seeds[None])
        selected = np.argpartition(ranks, len(indices) - int(count), axis=1)[:, -int(count):]
        result[np.arange(assignments)[:, None], indices[selected]] = 1.0
    return result


def weights(names, domain):
    return np.asarray([((stable(f"SNOCCTX1|{domain}|{name}") + 0.5) / (1 << 64)) * 2 - 1 for name in names])


def plant(data, mode, world):
    rows, _, strata, counts, _, folios, folio_index, _, bases, base_index, position, neighbor, pos_names, neighbor_names = data
    noise = np.asarray([((stable(f"SNOCCTX1|PLANT|{mode}|{world}|{row['unit_id']}") + 0.5) / (1 << 64)) * 2 - 1 for row in rows])
    if mode == "NULL":
        signal = np.zeros(len(rows))
    elif mode == "POSITION":
        signal = position @ weights(pos_names, f"POSITION|{world}")
    elif mode in {"NEIGHBOR", "ONE_FOLIO", "ONE_BASE"}:
        signal = neighbor @ weights(neighbor_names, f"NEIGHBOR|{world}")
        if mode == "ONE_FOLIO":
            signal *= folio_index == world % len(folios)
        elif mode == "ONE_BASE":
            signal *= base_index == world % len(bases)
    else:
        signal = np.empty(len(rows))
        for index in range(len(folios)):
            mask = folio_index == index
            signal[mask] = neighbor[mask] @ weights(neighbor_names, f"FOLIO_RANDOM|{world}|{index}")
    rms = np.sqrt(np.mean(signal * signal))
    if rms:
        signal /= rms
    ranking = .82 * signal + .18 * noise
    labels = np.zeros(len(rows))
    for indices, count in zip(strata, counts):
        order = np.argsort(ranking[indices], kind="mergesort")
        labels[indices[order[-int(count):]]] = 1
    return labels


def pairwise(values):
    count = len(values)
    total = values.sum(axis=0)
    return ((total * total).sum() - (values * values).sum()) / (count * (count - 1))


def summaries(data, features, observed, null):
    rows, _, _, _, probabilities, folios, folio_index, folio_currier, _, _, _, _, _, _ = data
    labels = np.vstack((observed, null[1:])) - probabilities
    covariances = np.stack([(labels[:, folio_index == index] @ features[folio_index == index]) / np.sum(folio_index == index) for index in range(len(folios))], axis=1)
    statistics = np.asarray([pairwise(value) for value in covariances])
    null_statistics = statistics[len(observed):]
    mean = float(null_statistics.mean())
    sd = float(null_statistics.std())
    answer = []
    curriers = np.asarray(folio_currier)
    for index in range(len(observed)):
        current = covariances[index]
        total = current.sum(axis=0)
        contributions = np.asarray([current[f] @ ((total - current[f]) / (len(folios) - 1)) for f in range(len(folios))])
        deletions = [pairwise(np.delete(current, f, axis=0)) for f in range(len(folios))]
        observed_value = statistics[index]
        answer.append({
            "observed": float(observed_value), "null_mean": mean, "null_sd": sd,
            "upper_p": (1 + int(np.sum(null_statistics >= observed_value))) / (1 + len(null_statistics)),
            "positive_folios": int(np.sum(contributions > 0)),
            "max_abs_contribution_fraction": float(np.max(np.abs(contributions)) / np.sum(np.abs(contributions))) if np.sum(np.abs(contributions)) else 1.0,
            "minimum_deletion_statistic": float(min(deletions)),
            "currier_A_statistic": float(pairwise(current[curriers == "A"])),
            "currier_B_statistic": float(pairwise(current[curriers == "B"])),
            "z": (float(observed_value) - mean) / sd if sd else 0.0,
        })
    return answer


def passes(value):
    return value["upper_p"] <= .01 and value["z"] >= 3 and value["positive_folios"] >= 35 and value["max_abs_contribution_fraction"] <= .25 and value["minimum_deletion_statistic"] > 0 and min(value["currier_A_statistic"], value["currier_B_statistic"]) >= .01


def numeric_max(left, right):
    if isinstance(left, dict):
        return math.inf if set(left) != set(right) else max((numeric_max(left[key], right[key]) for key in left), default=0.0)
    if isinstance(left, list):
        return math.inf if len(left) != len(right) else max((numeric_max(a, b) for a, b in zip(left, right)), default=0.0)
    if isinstance(left, (int, float)) and not isinstance(left, bool):
        return abs(float(left) - float(right))
    return 0.0 if left == right else math.inf


def digest(labels):
    return hashlib.sha256(np.packbits(labels.astype(np.uint8), axis=None).tobytes()).hexdigest()


def expected_report(stored):
    counts = stored["counts"]
    return f"""# Opening-context target-free preflight

Status: **{stored['status']}**

The 1,024-assignment grid yields position/neighbor passes of
**{counts['NULL']['position_passes']}/{counts['NULL']['neighbor_passes']}** in
64 null worlds, **{counts['POSITION']['position_passes']}/{counts['POSITION']['neighbor_passes']}**
in eight position plants, and **{counts['NEIGHBOR']['position_passes']}/{counts['NEIGHBOR']['neighbor_passes']}**
in eight neighbor plants. One-folio, folio-random, and one-base controls yield
zero passes in both systems. All six representative decisions remain unchanged
at 8,192 assignments. All gates are **passing**.

No real row operation label or context score was opened. Decision:
**{stored['decision']}**. This supplies no detachment, wordhood, prefix function,
syntax, sound, language, cipher, meaning, plaintext, or translation.
"""


def main():
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    failures = []
    checks = 0

    def check(condition, name):
        nonlocal checks
        checks += 1
        if not condition:
            failures.append(name)

    for path, expected in FROZEN.items():
        check(sha(path) == expected, f"hash:{path.name}")
    data = load()
    observed = np.stack([plant(data, mode, world) for mode, world in TASKS])
    null = orbit(data[0], data[1], data[2], data[3], 1024, "PREFLIGHT")
    position = summaries(data, data[10], observed, null)
    neighbor = summaries(data, data[11], observed, null)
    rebuilt = [{"mode": mode, "world": world, "POSITION": {**p, "PASS": passes(p)}, "NEIGHBOR": {**n, "PASS": passes(n)}} for (mode, world), p, n in zip(TASKS, position, neighbor)]
    stored = json.loads(PRODUCTION.read_text())
    maximum = 0.0
    for expected, actual in zip(rebuilt, stored["records"]):
        delta = numeric_max(expected, actual)
        maximum = max(maximum, delta)
        check(delta <= 1e-12, f"record:{expected['mode']}:{expected['world']}")
    large_observed = np.stack([plant(data, mode, world) for mode, world in REPRESENTATIVES])
    large_null = orbit(data[0], data[1], data[2], data[3], 8192, "PREFLIGHT")
    large_position = summaries(data, data[10], large_observed, large_null)
    large_neighbor = summaries(data, data[11], large_observed, large_null)
    large = [{"mode": mode, "world": world, "POSITION": {**p, "PASS": passes(p)}, "NEIGHBOR": {**n, "PASS": passes(n)}} for (mode, world), p, n in zip(REPRESENTATIVES, large_position, large_neighbor)]
    for expected, actual in zip(large, stored["target_size_checks"]):
        delta = numeric_max(expected, actual)
        maximum = max(maximum, delta)
        check(delta <= 1e-12, f"large:{expected['mode']}")
    counts = {mode: {"worlds": sum(candidate == mode for candidate, _ in TASKS), "position_passes": sum(row["POSITION"]["PASS"] for row in rebuilt if row["mode"] == mode), "neighbor_passes": sum(row["NEIGHBOR"]["PASS"] for row in rebuilt if row["mode"] == mode)} for mode in ("NULL", "POSITION", "NEIGHBOR", "ONE_FOLIO", "FOLIO_RANDOM", "ONE_BASE")}
    check(stored["counts"] == counts, "counts")
    check(stored["null_orbit_sha256"] == digest(null) and stored["target_size_null_orbit_sha256"] == digest(large_null), "orbit-digests")
    check(stored["position_features"] == list(data[12]) and stored["neighbor_features"] == list(data[13]), "features")
    check(stored["gates"] == {"exact_synthetic_pattern": True, "target_size_decisions_stable": True, "finite_summaries": True, "exact_masked_geometry": True, "real_operation_labels_accessed_zero": True, "real_context_scores_computed_zero": True, "target_outputs_absent": True}, "gates")
    check(stored["status"] == "PASS_TARGET_FREE_OPENING_CONTEXT_PREFLIGHT" and stored["decision"] == "GO_INDEPENDENTLY_VALIDATE_CONTEXT_PREFLIGHT", "decision")
    check(stored["real_operation_labels_accessed"] == 0 and stored["real_context_scores_computed"] == 0 and stored["english_glosses"] == 0 and not TARGET.exists() and not TARGET_REPORT.exists(), "isolation")
    check(PRODUCTION_REPORT.read_text() == expected_report(stored), "report")
    if failures:
        raise SystemExit("validation failed: " + failures[0])
    result = {"experiment": "SOURCE_NATIVE_OPENING_CONTEXT_PREFLIGHT_VALIDATION", "status": "PASS_INDEPENDENT_104_WORLD_CONTEXT_CALIBRATION_RECONSTRUCTION", "checks": checks, "failures": [], "maximum_numeric_delta": maximum, "reconstructed_worlds": 104, "target_size_checks": 6, "counts": counts, "real_operation_labels_accessed": 0, "real_context_scores_computed": 0, "target_outputs_absent": True, "inputs": {path.name: sha(path) for path in FROZEN}, "english_glosses": 0, "claim_ceiling": "Independent CPU reconstruction of target-free context calibration only; no detachment, wordhood, prefix function, syntax, sound, language, cipher, meaning, plaintext, or translation follows."}
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(f"""# Opening-context preflight validation

Status: **{result['status']}**

A production-free CPU implementation reconstructs all **104** synthetic worlds,
six 8,192-assignment checks, both quota orbits, every summary, gate, decision,
and exact report in **{checks}** checks. Maximum GPU-versus-CPU numeric delta is
**{maximum:.3g}**. No real operation label or context score was opened.

This validates calibration only and supplies no detachment, wordhood, prefix
function, syntax, sound, language, cipher, meaning, plaintext, or translation.
""")
    print(json.dumps({"status": result["status"], "checks": checks, "maximum_numeric_delta": maximum}, sort_keys=True))


if __name__ == "__main__":
    main()
