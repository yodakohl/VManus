#!/usr/bin/env python3
"""Nonimporting clean-room reconstruction of the CMR001 preflight."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


BASE = Path(__file__).resolve().parent
R = BASE / "results"
ALIGN = R / "source_sta_group_alignment.tsv"
META = R / "source_separator_transcription.tsv"
METHOD = BASE / "CIRCLE_MARKER_RESET_METHOD.md"
CAP = R / "circle_marker_reset_capacity.json"
CAPV = R / "circle_marker_reset_capacity_validation.json"
CORE = BASE / "cmr001_core.py"
RUNNER = BASE / "run_cmr001_preflight.py"
PROD = R / "cmr001_preflight.json"
PROD_MD = R / "cmr001_preflight.md"
ATTEMPT1 = R / "cmr001_preflight_attempt1.json"
OUT = R / "cmr001_preflight_validation.json"
OUT_MD = R / "cmr001_preflight_validation.md"
READINGS = ("ZL3b", "IT2a", "RF1b")
A = 65_536
EXCLUDED = {f"f{i}" for i in range(67, 74)}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def features(word: str) -> tuple[str, ...]:
    return (
        f"LEN={min(len(word), 12)}",
        f"P1={word[:1]}", f"P2={word[:2]}", f"P3={word[:3]}",
        f"S1={word[-1:]}", f"S2={word[-2:]}", f"S3={word[-3:]}",
    )


def fit(examples: list[tuple[str, int]]) -> tuple[list[int], list[set[str]], list[list[Counter[str]]]]:
    class_n = [0, 0]
    vocabulary = [set() for _ in range(7)]
    counts = [[Counter() for _ in range(7)] for _ in range(2)]
    for word, label in examples:
        class_n[label] += 1
        for field, value in enumerate(features(word)):
            vocabulary[field].add(value)
            counts[label][field][value] += 1
    if not all(class_n):
        raise AssertionError("degenerate training")
    return class_n, vocabulary, counts


def predict(model: tuple[list[int], list[set[str]], list[list[Counter[str]]]], word: str) -> float:
    class_n, vocabulary, counts = model
    score = 0.0
    for field, value in enumerate(features(word)):
        k = len(vocabulary[field]) + 1
        score += math.log((counts[1][field].get(value, 0) + 1.0) / (class_n[1] + k))
        score -= math.log((counts[0][field].get(value, 0) + 1.0) / (class_n[0] + k))
    return score


def auc(labels: list[int], scores: list[float]) -> float:
    pos = sum(labels)
    neg = len(labels) - pos
    order = sorted(range(len(scores)), key=scores.__getitem__)
    rank_sum = 0.0
    rank = 1
    cursor = 0
    while cursor < len(order):
        end = cursor + 1
        while end < len(order) and scores[order[end]] == scores[order[cursor]]:
            end += 1
        rank_sum += ((rank + rank + end - cursor - 1) / 2.0) * sum(labels[order[i]] for i in range(cursor, end))
        rank += end - cursor
        cursor = end
    return (rank_sum - pos * (pos + 1) / 2.0) / (pos * neg)


def centered(values: np.ndarray) -> np.ndarray:
    return np.array([
        (np.sum(values < value) + 0.5 * np.sum(values == value)) / len(values) - 0.5
        for value in values
    ], dtype=np.float64)


def us(locus: str) -> np.ndarray:
    answer = np.empty(A, dtype=np.float64)
    for a in range(A):
        integer = int.from_bytes(hashlib.sha256(f"CMR001_PHASE_V1|{a}|{locus}".encode("ascii")).digest()[:8], "big")
        answer[a] = integer / float(2**64)
    return answer


def f8hash(x: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(x, dtype="<f8").tobytes()).hexdigest()


def i8hash(x: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(x, dtype="<i8").tobytes()).hexdigest()


def evaluate(arrays: dict[str, dict[str, np.ndarray]], folio_map: dict[str, str], starts=None) -> dict[str, object]:
    loci = sorted(folio_map)
    folios = sorted(set(folio_map.values()))
    if starts is None:
        starts = {edition: {locus: 0 for locus in loci} for edition in READINGS}
    by_folio = {folio: [locus for locus in loci if folio_map[locus] == folio] for folio in folios}
    u = {locus: us(locus) for locus in loci}
    null = np.empty((A, 3), dtype=np.float64)
    folio_effects = {edition: {} for edition in READINGS}
    canonical_hashes = []
    relative_index_hashes = []
    for ei, edition in enumerate(READINGS):
        selected_null = {}
        for locus in loci:
            ranks = centered(np.asarray(arrays[edition][locus], dtype=np.float64))
            start = starts[edition][locus]
            chosen = (start + np.floor(u[locus] * len(ranks)).astype(np.int64)) % len(ranks)
            selected_null[locus] = ranks[chosen]
            canonical_hashes.append(f8hash(np.roll(ranks, -start)))
            relative_index_hashes.append(i8hash((chosen - start) % len(ranks)))
            folio_effects[edition].setdefault(folio_map[locus], []).append(float(ranks[start]))
        folio_effects[edition] = {folio: float(np.mean(values)) for folio, values in folio_effects[edition].items()}
        null[:, ei] = np.mean(np.vstack([
            np.mean(np.vstack([selected_null[locus] for locus in by_folio[folio]]), axis=0)
            for folio in folios
        ]), axis=0)
    T = {edition: float(np.mean(list(folio_effects[edition].values()))) for edition in READINGS}
    M = min(T.values())
    null_M = np.min(null, axis=1)
    p = (1 + int(np.sum(null_M >= M - 1e-15))) / (A + 1)
    positive = {edition: sum(value > 0 for value in folio_effects[edition].values()) for edition in READINGS}
    loo = {
        deleted: min(float(np.mean([value for folio, value in folio_effects[edition].items() if folio != deleted])) for edition in READINGS)
        for deleted in folios
    }
    concentration = {}
    for edition in READINGS:
        vals = [abs(value) for value in folio_effects[edition].values()]
        concentration[edition] = max(vals) / sum(vals) if sum(vals) else 1.0
    return {
        "loci": loci, "folios": folios, "T_by_reading": T, "M": M, "p": p,
        "folio_effects": folio_effects, "positive_folios_by_reading": positive,
        "leave_one_folio_out_M": loo, "concentration_by_reading": concentration,
        "digests": {
            "null_M_sha256": f8hash(null_M),
            "null_by_reading_sha256": f8hash(null),
            "canonical_percentile_arrays_sha256": hashlib.sha256("".join(canonical_hashes).encode("ascii")).hexdigest(),
            "relative_assignment_indices_sha256": hashlib.sha256("".join(relative_index_hashes).encode("ascii")).hexdigest(),
        },
    }


def gates(panel: dict[str, object]) -> dict[str, bool]:
    return {
        "magnitude": panel["M"] >= 0.10,
        "p": panel["p"] <= 0.05,
        "all_readings_positive": all(value > 0 for value in panel["T_by_reading"].values()),
        "five_of_six_folios_each_reading": all(value >= 5 for value in panel["positive_folios_by_reading"].values()),
        "all_leave_one_folio_out_above_005": all(value > 0.05 for value in panel["leave_one_folio_out_M"].values()),
        "concentration_at_most_035": all(value <= 0.35 for value in panel["concentration_by_reading"].values()),
    }


def synthetic(kind: str):
    loci = [f"SYN_F{f}_L{l}" for f in range(6) for l in range(3)]
    folios = {locus: f"SYN_F{locus.split('_')[1][1:]}" for locus in loci}
    arrays = {edition: {} for edition in READINGS}
    for ei, edition in enumerate(READINGS):
        for li, locus in enumerate(loci):
            x = np.zeros(11 + li % 7 + ei)
            folio = int(locus.split("_")[1][1:])
            if kind == "DISTRIBUTED": x[0] = 10
            elif kind == "ONE_FOLIO" and folio == 0: x[0] = 10
            elif kind == "READING_DISAGREEMENT": x[0] = 10 if edition != "RF1b" else -10
            elif kind not in ("NULL", "NO_OBVIOUS", "ONE_FOLIO"): raise ValueError(kind)
            arrays[edition][locus] = x
    return arrays, folios


def main() -> None:
    if OUT.exists() or OUT_MD.exists():
        raise SystemExit("refusing overwrite")
    checks = 0
    def verify(value: bool, label: str) -> None:
        nonlocal checks
        if not value: raise AssertionError(label)
        checks += 1

    prod = json.loads(PROD.read_text(encoding="utf-8"))
    attempt = json.loads(ATTEMPT1.read_text(encoding="utf-8"))
    verify(attempt["status"] == "STOP_PREFLIGHT_FAILED", "attempt1 status")
    verify(attempt["invariance"] == {"positive_affine": True, "serialization_and_reading_order": True, "simultaneous_cyclic_rotation": False}, "attempt1 exact failure")
    metadata_rows = list(csv.DictReader(META.open(encoding="utf-8"), delimiter="\t"))
    metadata = {row["source_group_id"]: row for row in metadata_rows}
    verify(len(metadata) == len(metadata_rows), "unique metadata IDs")
    examples = {edition: [] for edition in READINGS}
    for row in csv.DictReader(ALIGN.open(encoding="utf-8"), delimiter="\t"):
        info = metadata[row["source_group_id"]]
        m = re.match(r"^(f\d+)", info["page"])
        if row["edition"] in READINGS and info["grammar_scope"] == "CONFIRMED_PROSE" and info["kind"] == "P" and m and m.group(1) not in EXCLUDED:
            examples[row["edition"]].append((m.group(1), row["primary_sta_families"], int(row["source_group_index"]) == 1))
    calibration = {}
    passmap = {}
    for edition in READINGS:
        by_folio = defaultdict(list)
        for folio, word, label in examples[edition]: by_folio[folio].append((word, label))
        aucs = {}
        for held in sorted(by_folio):
            held_rows = by_folio[held]
            if not any(y for _, y in held_rows) or all(y for _, y in held_rows): continue
            model = fit([item for folio, values in by_folio.items() if folio != held for item in values])
            aucs[held] = auc([y for _, y in held_rows], [predict(model, word) for word, _ in held_rows])
        vals = list(aucs.values())
        calibration[edition] = {
            "training_rows": len(examples[edition]),
            "positive_rows": sum(y for _, _, y in examples[edition]),
            "negative_rows": sum(not y for _, _, y in examples[edition]),
            "eligible_held_folios": len(vals),
            "equal_folio_mean_auc": float(np.mean(vals)),
            "median_folio_auc": float(np.median(vals)),
            "fraction_folios_auc_at_least_055": sum(v >= .55 for v in vals) / len(vals),
            "folio_auc": aucs,
        }
        passmap[edition] = calibration[edition]["equal_folio_mean_auc"] >= .65 and calibration[edition]["median_folio_auc"] >= .65 and calibration[edition]["fraction_folios_auc_at_least_055"] >= .75
    verify(calibration == prod["calibration"], "calibration exact")
    verify(passmap == prod["calibration_pass"], "calibration decisions exact")

    controls = {}
    evaluations = {}
    for kind in ("DISTRIBUTED", "NULL", "ONE_FOLIO", "READING_DISAGREEMENT", "NO_OBVIOUS"):
        arrays, folios = synthetic(kind)
        evaluations[kind] = evaluate(arrays, folios)
        controls[kind] = {"evaluation": evaluations[kind], "primary_gates": gates(evaluations[kind])}
    verify(controls == prod["controls"], "all control checkpoints exact")
    negative = {kind: not all(gates(evaluations[kind]).values()) for kind in ("NULL", "ONE_FOLIO", "READING_DISAGREEMENT", "NO_OBVIOUS")}
    verify(negative == prod["negative_control_rejection"], "negative decisions exact")

    base_arrays, folios = synthetic("DISTRIBUTED")
    base = evaluations["DISTRIBUTED"]
    affine = evaluate({e: {l: 7*x+19 for l,x in d.items()} for e,d in base_arrays.items()}, folios)
    shifts = {locus: i % 5 + 1 for i, locus in enumerate(sorted(folios))}
    rotated = {e: {} for e in READINGS}; starts = {e: {} for e in READINGS}
    for e in READINGS:
        for locus, x in base_arrays[e].items():
            shift = shifts[locus] % len(x); rotated[e][locus] = np.roll(x, shift); starts[e][locus] = shift
    rotation = evaluate(rotated, folios, starts)
    serialized = evaluate({e: {l: base_arrays[e][l] for l in reversed(list(base_arrays[e]))} for e in READINGS}, dict(reversed(list(folios.items()))))
    invariance = {
        "positive_affine": base == affine,
        "simultaneous_cyclic_rotation": base == rotation,
        "serialization_and_reading_order": base == serialized,
    }
    verify(invariance == prod["invariance"], "invariances exact")
    verify(all(prod["gates"].values()), "all preflight gates")
    verify(prod["status"] == "PASS_TARGET_BLIND_PREFLIGHT", "status exact")
    verify(prod["decision"] == "AUTHORIZE_INDEPENDENT_PREFLIGHT_RECONSTRUCTION_ONLY", "decision exact")
    for path in (ALIGN, META, METHOD, CAP, CAPV, CORE, RUNNER):
        verify(prod["inputs"][path.name] == sha(path), f"hash {path.name}")
    verify(not (R / "cmr001_target.json").exists(), "target absent")
    verify("No marker target score was loaded" in PROD_MD.read_text(encoding="utf-8"), "report ceiling")

    result = {
        "experiment": "CMR001_PREFLIGHT_VALIDATION",
        "status": "PASS_INDEPENDENT_CALIBRATION_AND_5_CONTROL_RECONSTRUCTION",
        "checks": checks,
        "failures": [],
        "bindings": {
            "preflight_sha256": sha(PROD), "report_sha256": sha(PROD_MD),
            "attempt1_sha256": sha(ATTEMPT1), "validator_sha256": sha(Path(__file__)),
        },
        "calibration_pass": passmap,
        "control_count": 5,
        "assignments_per_control": A,
        "target_score_opened": False,
        "decision": "AUTHORIZE_ONE_HASH_FROZEN_TARGET_RUN",
        "claim_ceiling": prod["claim_ceiling"],
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# CMR001 preflight validation\n\n"
        "Status: **PASS_INDEPENDENT_CALIBRATION_AND_5_CONTROL_RECONSTRUCTION**\n\n"
        f"A nonimporting implementation passed {checks:,} checks and exactly reconstructed the three "
        "94-folio calibration panels, every AUC, all five 65,536-assignment controls, canonical digests, "
        "negative decisions, invariances, hashes, and the attempt-1 diagnosis. The marker target remained "
        "absent. One hash-frozen target run is authorized; no reset or semantic result exists yet.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": result["status"], "checks": checks}, sort_keys=True))


if __name__ == "__main__":
    main()
