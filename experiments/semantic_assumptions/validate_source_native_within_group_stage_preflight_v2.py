#!/usr/bin/env python3
"""Production-free reconstruction of both within-group stage preflights."""

from __future__ import annotations

import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import csv
import hashlib
import json
import math
import multiprocessing as mp
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations_with_replacement
from pathlib import Path

import numpy as np


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
PANEL_PATH = RESULTS / "source_native_within_group_stage_masked.tsv"
V1_RESULT = RESULTS / "source_native_within_group_stage_preflight.json"
V1_REPORT = RESULTS / "source_native_within_group_stage_preflight_report.md"
V1_RUNNER = BASE / "run_source_native_within_group_stage_preflight.py"
V1_SPEC = BASE / "SOURCE_NATIVE_WITHIN_GROUP_STAGE_TEST_SPEC.md"
CORE = BASE / "source_native_within_group_stage_core.py"
AMENDMENT = BASE / "SOURCE_NATIVE_WITHIN_GROUP_STAGE_PREFLIGHT_V2_AMENDMENT.md"
V2_RUNNER = BASE / "run_source_native_within_group_stage_preflight_v2.py"
V2_RESULT = RESULTS / "source_native_within_group_stage_preflight_v2.json"
V2_REPORT = RESULTS / "source_native_within_group_stage_preflight_v2_report.md"
TARGET_SOURCE = RESULTS / "source_sta_family_consensus_groups.tsv"
TARGET_OUT = RESULTS / "source_native_within_group_stage_target.json"
TARGET_REPORT = RESULTS / "source_native_within_group_stage_target_report.md"
OUT = RESULTS / "source_native_within_group_stage_preflight_v2_validation.json"
REPORT = RESULTS / "source_native_within_group_stage_preflight_v2_validation_report.md"
FROZEN = {
    PANEL_PATH: "16d7395ae0410c8fc72b5e5462d6d425cd3a2685e7ea70eee0677bd936106ae5",
    V1_RESULT: "6e11363eb76ec056504b349764fc998a0b9561dbef25c83a095fadc786071b11",
    V1_REPORT: "3ddbcba4868e754a8c63ed27745481f4ff0da79f1370ff0d7a5e7163865912c8",
    V1_RUNNER: "211452815b78c9e01f4548b6a61226730bf36080b5185697dc9ac041f0abceaf",
    V1_SPEC: "e3758d2a4c8d5d306b38602e8a1663ebc42a78db2abecd5905fe191a5d983d47",
    CORE: "ce1cd0854426b34e8b3e9ba0e6057352f9a5b99737e9e148e791e02979bc65dc",
    AMENDMENT: "b0b42cc092c2b97ac919d5ecc471d890a09a7c5e0b21fe10548efb543c02bc80",
    V2_RUNNER: "ac7d4d985a264296373649b17b7d4dbc4193ba12dff32f84378d41b67a7d5805",
    V2_RESULT: "a619c087692b27dd3dac062412238388d717fcfe7c5f213fbfa28b0fe0c586c2",
    V2_REPORT: "7e834bb66b451a2f7080b17ead34b192617ffabdc95f739a599c10c46df967a5",
}
FIELDS = ("unit_id", "locus", "page", "physical_folio", "section", "currier", "hand", "kind", "symbol_count", "split")
ALPHABET = tuple("ABCDEFGHJKLMNPQRSTUVWXYZ")
ALPHA = 0.5
CANDIDATES = ("K1", "FIXED_2", "FIXED_3", "FIXED_4", "FIXED_5", "LATENT_2", "LATENT_3", "LATENT_4", "LATENT_5")
TASKS = (
    [("NULL", world) for world in range(32)]
    + [("LATENT", 100 + world) for world in range(8)]
    + [("FIXED", 200 + world) for world in range(8)]
    + [("CURRIER_ONE", 300 + world) for world in range(8)]
    + [("ONE_FOLIO", 400 + world) for world in range(8)]
)
PANEL = None


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable_u64(text: str) -> int:
    return int.from_bytes(hashlib.sha256(text.encode()).digest()[:8], "little")


@dataclass
class Panel:
    rows: list[dict]
    lengths: np.ndarray
    splits: np.ndarray
    curriers: np.ndarray
    folios: np.ndarray


def load_panel() -> Panel:
    with PANEL_PATH.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("panel schema")
        rows = list(reader)
    if len(rows) != 21899 or len({row["unit_id"] for row in rows}) != 21899:
        raise ValueError("panel identity")
    if Counter(row["split"] for row in rows) != {"TRAIN": 10753, "CAL": 5516, "TEST": 5630}:
        raise ValueError("panel split")
    lengths = np.asarray([int(row["symbol_count"]) for row in rows], dtype=np.int64)
    if (int(lengths.min()), int(lengths.max())) != (1, 11):
        raise ValueError("panel length")
    return Panel(rows, lengths, np.asarray([row["split"] for row in rows]), np.asarray([row["currier"] for row in rows]), np.asarray([row["physical_folio"] for row in rows]))


@lru_cache(maxsize=None)
def paths_for(length: int, stages: int) -> np.ndarray:
    paths = []
    for cuts in combinations_with_replacement(range(length + 1), stages - 1):
        boundaries = (0, *cuts, length)
        path = []
        for stage in range(stages):
            path.extend([stage] * (boundaries[stage + 1] - boundaries[stage]))
        paths.append(path)
    return np.asarray(paths, dtype=np.int8)


def fixed_path(length: int, stages: int) -> np.ndarray:
    return np.minimum(stages - 1, (np.arange(length, dtype=np.int64) * stages) // length)


def initial_theta(sequences: Counter, stages: int) -> np.ndarray:
    counts = np.full((stages, len(ALPHABET)), ALPHA, dtype=np.float64)
    for sequence, multiplicity in sequences.items():
        path = np.minimum(stages - 1, ((np.arange(len(sequence)) + 0.5) * stages / len(sequence)).astype(np.int64))
        for state, symbol in zip(path, sequence):
            counts[state, symbol] += multiplicity
    return counts / counts.sum(axis=1, keepdims=True)


def latent_probability(sequence: tuple[int, ...], theta: np.ndarray) -> float:
    log_theta = np.log(theta)
    forward = log_theta[:, sequence[0]].copy()
    for symbol in sequence[1:]:
        forward = log_theta[:, symbol] + np.logaddexp.accumulate(forward)
    return float(np.logaddexp.reduce(forward) - math.log(math.comb(len(sequence) + len(theta) - 1, len(theta) - 1)))


def fit_latent(sequences: Counter, stages: int) -> tuple[np.ndarray, int, float]:
    theta = initial_theta(sequences, stages)
    last_ll = -math.inf
    unique_size = sum(map(len, sequences))
    for iteration in range(1, 41):
        counts = np.full_like(theta, ALPHA)
        log_theta = np.log(theta)
        ll = 0.0
        for sequence, multiplicity in sequences.items():
            length = len(sequence)
            forward = np.empty((length, stages), dtype=np.float64)
            backward = np.empty((length, stages), dtype=np.float64)
            forward[0] = log_theta[:, sequence[0]]
            for position in range(1, length):
                forward[position] = log_theta[:, sequence[position]] + np.logaddexp.accumulate(forward[position - 1])
            backward[-1] = 0.0
            for position in range(length - 2, -1, -1):
                continuation = log_theta[:, sequence[position + 1]] + backward[position + 1]
                backward[position] = np.logaddexp.accumulate(continuation[::-1])[::-1]
            log_z = float(np.logaddexp.reduce(forward[-1]))
            ll += multiplicity * (log_z - math.log(math.comb(length + stages - 1, stages - 1)))
            for position, symbol in enumerate(sequence):
                counts[:, symbol] += multiplicity * np.exp(forward[position] + backward[position] - log_z)
        updated = counts / counts.sum(axis=1, keepdims=True)
        delta = float(np.max(np.abs(updated - theta)))
        theta = updated
        if delta < 1e-11 or (iteration > 2 and abs(ll - last_ll) / max(1, unique_size) < 1e-12):
            return theta, iteration, ll
        last_ll = ll
    return theta, 40, ll


def fit_fixed(sequences: Counter, stages: int) -> np.ndarray:
    counts = np.full((stages, len(ALPHABET)), ALPHA, dtype=np.float64)
    for sequence, multiplicity in sequences.items():
        for state, symbol in zip(fixed_path(len(sequence), stages), sequence):
            counts[state, symbol] += multiplicity
    return counts / counts.sum(axis=1, keepdims=True)


def probability(sequence: tuple[int, ...], candidate: str, theta: np.ndarray) -> float:
    if candidate == "K1":
        return float(np.log(theta[0, np.asarray(sequence)]).sum())
    family, value = candidate.split("_")
    if family == "LATENT":
        return latent_probability(sequence, theta)
    path = fixed_path(len(sequence), int(value))
    return float(np.log(theta[path, np.asarray(sequence)]).sum())


def counter(panel: Panel, sequences: list[tuple[int, ...]], split: str, currier: str) -> Counter:
    return Counter(sequence for sequence, row in zip(sequences, panel.rows) if row["split"] == split and row["currier"] == currier)


def fit_candidates(panel: Panel, sequences: list[tuple[int, ...]]) -> tuple[dict, dict, str, str]:
    models, diagnostics = {}, {}
    for candidate in CANDIDATES:
        models[candidate] = {}
        diagnostics[candidate] = {"iterations": {}, "train_log_likelihood": {}}
        stages = 1 if candidate == "K1" else int(candidate.split("_")[1])
        for currier in ("A", "B"):
            values = counter(panel, sequences, "TRAIN", currier)
            if candidate.startswith("LATENT"):
                theta, iterations, ll = fit_latent(values, stages)
            else:
                theta = fit_fixed(values, stages)
                iterations = 1
                ll = sum(count_value * probability(sequence, candidate, theta) for sequence, count_value in values.items())
            models[candidate][currier] = theta
            diagnostics[candidate]["iterations"][currier] = iterations
            diagnostics[candidate]["train_log_likelihood"][currier] = ll
        ll, symbols = 0.0, 0
        for sequence, row in zip(sequences, panel.rows):
            if row["split"] == "CAL":
                ll += probability(sequence, candidate, models[candidate][row["currier"]])
                symbols += len(sequence)
        diagnostics[candidate]["cal_log_likelihood_per_symbol"] = ll / symbols
    order = {candidate: index for index, candidate in enumerate(CANDIDATES)}
    selected = max(CANDIDATES, key=lambda candidate: (diagnostics[candidate]["cal_log_likelihood_per_symbol"], -order[candidate]))
    best_fixed = max((candidate for candidate in CANDIDATES if candidate.startswith("FIXED")), key=lambda candidate: (diagnostics[candidate]["cal_log_likelihood_per_symbol"], -order[candidate]))
    return models, diagnostics, selected, best_fixed


def sign_p(positive: int, total: int) -> float:
    return sum(math.comb(total, k) for k in range(positive, total + 1)) / (2 ** total)


def summarize(values: dict[str, list[tuple[float, int]]]) -> dict:
    effects = []
    for folio in sorted(values, key=lambda value: int(value[1:])):
        effects.append(sum(value for value, _ in values[folio]) / sum(length for _, length in values[folio]))
    array = np.asarray(effects, dtype=np.float64)
    deletion = (array.sum() - array) / (len(array) - 1)
    total_abs = float(np.abs(array).sum())
    return {
        "effect_equal_folio": float(array.mean()),
        "positive_folios": int((array > 0).sum()),
        "folios": len(array),
        "sign_p": sign_p(int((array > 0).sum()), len(array)),
        "minimum_leave_one_folio_out": float(deletion.min()),
        "max_abs_contribution_fraction": float(np.abs(array).max() / total_abs) if total_abs else 1.0,
    }


def evaluate(panel: Panel, sequences: list[tuple[int, ...]]) -> dict:
    if len(sequences) != len(panel.rows) or any(len(sequence) != length for sequence, length in zip(sequences, panel.lengths)):
        raise ValueError("geometry")
    if any(not sequence or any(symbol < 0 or symbol >= len(ALPHABET) for symbol in sequence) for sequence in sequences):
        raise ValueError("symbol")
    models, diagnostics, selected, best_fixed = fit_candidates(panel, sequences)
    by_folio, adaptive_by_folio, unseen_by_folio = defaultdict(list), defaultdict(list), defaultdict(list)
    currier_folios = {"A": defaultdict(list), "B": defaultdict(list)}
    adaptive_currier = {"A": defaultdict(list), "B": defaultdict(list)}
    train_surfaces = {(row["currier"], sequence) for row, sequence in zip(panel.rows, sequences) if row["split"] == "TRAIN"}
    test_groups = test_symbols = unseen_groups = unseen_symbols = 0
    total_gain = total_adaptive = total_unseen = 0.0
    for sequence, row in zip(sequences, panel.rows):
        if row["split"] != "TEST":
            continue
        base = probability(sequence, "K1", models["K1"][row["currier"]])
        chosen = probability(sequence, selected, models[selected][row["currier"]])
        fixed = probability(sequence, best_fixed, models[best_fixed][row["currier"]])
        gain, adaptive = chosen - base, chosen - fixed
        length, folio = len(sequence), row["physical_folio"]
        by_folio[folio].append((gain, length)); adaptive_by_folio[folio].append((adaptive, length))
        currier_folios[row["currier"]][folio].append((gain, length)); adaptive_currier[row["currier"]][folio].append((adaptive, length))
        test_groups += 1; test_symbols += length; total_gain += gain; total_adaptive += adaptive
        if (row["currier"], sequence) not in train_surfaces:
            unseen_by_folio[folio].append((gain, length)); unseen_groups += 1; unseen_symbols += length; total_unseen += gain
    result = {
        "selected_model": selected,
        "best_fixed_model": best_fixed,
        "candidate_diagnostics": diagnostics,
        "test_groups": test_groups,
        "test_symbols": test_symbols,
        "gain_equal_symbol": total_gain / test_symbols,
        "gain_vs_fixed_equal_symbol": total_adaptive / test_symbols,
        "gain": summarize(by_folio),
        "gain_vs_fixed": summarize(adaptive_by_folio),
        "unseen": {"groups": unseen_groups, "symbols": unseen_symbols, "gain_equal_symbol": total_unseen / unseen_symbols, **summarize(unseen_by_folio)},
        "currier": {},
    }
    for currier in ("A", "B"):
        result["currier"][currier] = {"gain": summarize(currier_folios[currier]), "gain_vs_fixed": summarize(adaptive_currier[currier])}
    return result


def positional_pass(result: dict) -> bool:
    return (
        result["selected_model"] != "K1" and result["test_groups"] == 5630 and result["gain"]["folios"] == 24
        and result["gain"]["effect_equal_folio"] >= 0.02 and result["gain"]["positive_folios"] >= 18
        and result["gain"]["sign_p"] <= 0.01 and result["gain"]["minimum_leave_one_folio_out"] > 0
        and result["gain"]["max_abs_contribution_fraction"] <= 0.15 and result["unseen"]["groups"] >= 500
        and result["unseen"]["effect_equal_folio"] >= 0.015 and result["unseen"]["minimum_leave_one_folio_out"] > 0
        and all(result["currier"][c]["gain"]["effect_equal_folio"] >= 0.01
                and result["currier"][c]["gain"]["minimum_leave_one_folio_out"] > 0
                and result["currier"][c]["gain"]["positive_folios"] / result["currier"][c]["gain"]["folios"] >= 0.70 for c in ("A", "B"))
    )


def latent_pass(result: dict) -> bool:
    return (
        positional_pass(result) and result["selected_model"].startswith("LATENT_")
        and result["gain_vs_fixed"]["effect_equal_folio"] >= 0.005
        and result["gain_vs_fixed"]["positive_folios"] >= 17
        and result["gain_vs_fixed"]["minimum_leave_one_folio_out"] > 0
        and all(result["currier"][c]["gain_vs_fixed"]["effect_equal_folio"] > 0 for c in ("A", "B"))
    )


def synthetic(panel: Panel, world: int, mode: str) -> list[tuple[int, ...]]:
    output = []
    folios = sorted(set(panel.folios), key=lambda value: int(value[1:]))
    active_folio = folios[world % len(folios)]
    stage_maps = {c: tuple(sorted(range(24), key=lambda symbol: stable_u64(f"SNWG001|{world}|MAP|{c}|{symbol}"))[:3]) for c in ("A", "B")}
    for row, length_value in zip(panel.rows, panel.lengths):
        length = int(length_value)
        bucket = stable_u64(f"SNWG001|BUCKET|{row['unit_id']}") % 128
        base_order = sorted(range(24), key=lambda symbol: stable_u64(f"SNWG001|{world}|BASEMAP|{row['currier']}|{symbol}"))
        if mode == "LATENT":
            paths = paths_for(length, 3)
            stage_path = paths[stable_u64(f"SNWG001|{world}|PATH|{row['split']}|{row['currier']}|{length}|{bucket}") % len(paths)]
        else:
            stage_path = fixed_path(length, 3)
        sequence = []
        for position in range(length):
            u = (stable_u64(f"SNWG001|{world}|U|{row['split']}|{row['currier']}|{length}|{bucket}|{position}") + 0.5) / (1 << 64)
            if u < 0.36:
                symbol = base_order[0]
            elif u < 0.57:
                symbol = base_order[1]
            else:
                symbol = stable_u64(f"SNWG001|{world}|R|{row['split']}|{row['currier']}|{length}|{bucket}|{position}") % 24
            active = mode in {"LATENT", "FIXED", "CURRIER_ONE", "ONE_FOLIO"}
            active = active and (mode != "CURRIER_ONE" or row["currier"] == "B")
            active = active and (mode != "ONE_FOLIO" or row["physical_folio"] == active_folio)
            if active and u < 0.65:
                symbol = stage_maps[row["currier"]][int(stage_path[position])]
            sequence.append(int(symbol))
        output.append(tuple(sequence))
    return output


def compact(result: dict) -> dict:
    return {
        "selected_model": result["selected_model"], "best_fixed_model": result["best_fixed_model"],
        "candidate_diagnostics": result["candidate_diagnostics"], "test_groups": result["test_groups"],
        "test_symbols": result["test_symbols"], "gain_equal_symbol": result["gain_equal_symbol"],
        "gain_vs_fixed_equal_symbol": result["gain_vs_fixed_equal_symbol"], "gain": result["gain"],
        "gain_vs_fixed": result["gain_vs_fixed"], "unseen": result["unseen"], "currier": result["currier"],
        "POSITIONAL_PASS": positional_pass(result), "LATENT_STAGE_PASS": latent_pass(result),
    }


def worker(payload: tuple[str, int, bool]) -> tuple[str, int, bool, dict]:
    mode, world, reverse = payload
    sequences = synthetic(PANEL, world, mode)
    if reverse:
        sequences = [tuple(reversed(sequence)) for sequence in sequences]
    return mode, world, reverse, compact(evaluate(PANEL, sequences))


def numeric_max(left, right) -> float:
    if isinstance(left, dict):
        if set(left) != set(right):
            return math.inf
        return max((numeric_max(left[key], right[key]) for key in left), default=0.0)
    if isinstance(left, list):
        if len(left) != len(right):
            return math.inf
        return max((numeric_max(a, b) for a, b in zip(left, right)), default=0.0)
    if isinstance(left, (int, float)) and not isinstance(left, bool):
        return abs(float(left) - float(right))
    return 0.0 if left == right else math.inf


def principal(record: dict) -> dict:
    return {
        "test_groups": record["test_groups"], "test_symbols": record["test_symbols"],
        "gain_equal_symbol": record["gain_equal_symbol"], "gain": record["gain"], "unseen": record["unseen"],
        "currier": {c: {"gain": record["currier"][c]["gain"]} for c in ("A", "B")},
    }


def expected_v1_report(counts: dict, status: str, decision: str) -> str:
    return f"""# Source-native within-group stage synthetic preflight

Status: **{status}**

The 32-worker target-free grid produced **{counts['NULL']['positional_passes']}/32**
positional null passes, **{counts['LATENT']['latent_stage_passes']}/8** latent-stage
plant passes, **{counts['FIXED']['positional_passes']}/8** fixed-position passes
with **{counts['FIXED']['latent_stage_passes']}/8** false latent-stage calls,
**{counts['CURRIER_ONE']['positional_passes']}/8** one-register passes, and
**{counts['ONE_FOLIO']['positional_passes']}/8** one-folio passes.

Label relabeling, complete reversal, capacity, finite-score, mutation,
isolation, and target-absence gates are **not all passing**.
The target source was existence-tested only; zero target family sequences or
scores were opened.

Decision: **{decision}**. Calibration supplies no prefix, root, suffix, sound,
word, language, meaning, plaintext, or translation.
"""


def expected_v2_report(counts: dict, status: str, decision: str, delta: float) -> str:
    return f"""# Source-native within-group stage synthetic preflight v2

Status: **{status}**

The preserved v1 grid had only its mathematically incompatible whole-object
reversal gate fail. Under the corrected predeclared reversal control, all 64
synthetic pass decisions are stable,
all eight latent plants retain their selected model, and their maximum complete
selected-minus-K1 summary difference is **{delta:.3g}**.

The reversed grid yields **{counts['NULL']['positional_passes']}/32**
null positional passes, **{counts['LATENT']['latent_stage_passes']}/8**
latent passes, **{counts['FIXED']['positional_passes']}/8** fixed
positional passes with **{counts['FIXED']['latent_stage_passes']}/8**
false latent calls, **{counts['CURRIER_ONE']['positional_passes']}/8**
one-register passes, and **{counts['ONE_FOLIO']['positional_passes']}/8**
one-folio passes.

The target source was existence-tested only; zero target sequences or scores
were opened. Decision: **{decision}**. This calibration supplies no prefix,
root, suffix, sound, word, language, meaning, plaintext, or translation.
"""


def main() -> None:
    global PANEL
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing to overwrite stage v2 validation")
    if TARGET_OUT.exists() or TARGET_REPORT.exists():
        raise SystemExit("target output exists before stage validation")
    failures, checks = [], 0

    def check(condition: bool, name: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            failures.append(name)

    for path, expected in FROZEN.items():
        check(sha(path) == expected, f"hash:{path.name}")
    check(TARGET_SOURCE.exists(), "target source existence only")
    PANEL = load_panel()
    check(len(PANEL.rows) == 21899, "panel rows")
    check(len(set(PANEL.folios)) == 94, "panel folios")

    payloads = [(mode, world, reverse) for reverse in (False, True) for mode, world in TASKS]
    with mp.get_context("fork").Pool(32) as pool:
        rebuilt = pool.map(worker, payloads)
    indexed = {(mode, world, reverse): record for mode, world, reverse, record in rebuilt}
    v1, v2 = json.loads(V1_RESULT.read_text()), json.loads(V2_RESULT.read_text())
    stored_original = {(row["mode"], row["world"]): row for row in v1["records"]}
    stored_reversed = {(row["mode"], row["world"]): row for row in v2["reversed_records"]}
    check(set(stored_original) == set(TASKS), "v1 record identities")
    check(set(stored_reversed) == set(TASKS), "v2 record identities")
    max_record_delta = 0.0
    for mode, world in TASKS:
        for reverse, stored in ((False, stored_original[(mode, world)]), (True, stored_reversed[(mode, world)])):
            expected = {"mode": mode, "world": world, **indexed[(mode, world, reverse)]}
            delta = numeric_max(expected, stored)
            max_record_delta = max(max_record_delta, delta)
            check(delta <= 1e-12, f"record:{mode}:{world}:{reverse}")

    def counts(reverse: bool) -> dict:
        return {
            mode: {
                "worlds": len([w for m, w in TASKS if m == mode]),
                "positional_passes": sum(indexed[(mode, world, reverse)]["POSITIONAL_PASS"] for m, world in TASKS if m == mode),
                "latent_stage_passes": sum(indexed[(mode, world, reverse)]["LATENT_STAGE_PASS"] for m, world in TASKS if m == mode),
            }
            for mode in ("NULL", "LATENT", "FIXED", "CURRIER_ONE", "ONE_FOLIO")
        }

    original_counts, reversed_counts = counts(False), counts(True)
    check(v1["counts"] == original_counts, "v1 counts")
    check(v2["original_counts"] == original_counts, "v2 original counts")
    check(v2["reversed_counts"] == reversed_counts, "v2 reversed counts")
    decision_mismatches, latent_model_mismatches, principal_deltas = [], [], {}
    for mode, world in TASKS:
        before, after = indexed[(mode, world, False)], indexed[(mode, world, True)]
        if before["POSITIONAL_PASS"] != after["POSITIONAL_PASS"] or before["LATENT_STAGE_PASS"] != after["LATENT_STAGE_PASS"]:
            decision_mismatches.append(f"{mode}:{world}")
        if mode == "LATENT":
            if before["selected_model"] != after["selected_model"]:
                latent_model_mismatches.append(str(world))
            principal_deltas[str(world)] = numeric_max(principal(before), principal(after))
    check(v2["reversal"]["decision_mismatches"] == decision_mismatches, "decision mismatch payload")
    check(v2["reversal"]["latent_model_mismatches"] == latent_model_mismatches, "latent mismatch payload")
    check(numeric_max(v2["reversal"]["latent_principal_gain_max_abs_by_world"], principal_deltas) <= 1e-12, "principal deltas")

    reference_sequences = synthetic(PANEL, 100, "LATENT")
    reference = compact(evaluate(PANEL, reference_sequences))
    permutation = np.asarray([(7 * value + 3) % 24 for value in range(24)], dtype=np.int64)
    relabeled = compact(evaluate(PANEL, [tuple(int(permutation[value]) for value in sequence) for sequence in reference_sequences]))
    reversed_reference = compact(evaluate(PANEL, [tuple(reversed(sequence)) for sequence in reference_sequences]))
    label_delta = numeric_max(reference, relabeled)
    reversal_delta = numeric_max(reference, reversed_reference)
    check(abs(v1["invariance"]["label_relabel_max_abs"] - label_delta) <= 1e-12, "v1 label delta")
    check(math.isinf(v1["invariance"]["complete_reversal_max_abs"]) and math.isinf(reversal_delta), "v1 reversal contradiction")

    mutations = {}
    for name, altered in (
        ("missing_sequence", reference_sequences[:-1]),
        ("length_mismatch", [tuple()] + reference_sequences[1:]),
        ("invalid_symbol", [(-1,) + reference_sequences[0][1:]] + reference_sequences[1:]),
    ):
        try:
            evaluate(PANEL, altered)
        except ValueError:
            mutations[name] = True
        else:
            mutations[name] = False
    identifiers = [row["unit_id"] for row in PANEL.rows]
    mutations["duplicate_unit_id"] = len(set(identifiers + [identifiers[0]])) != len(identifiers) + 1
    check(v1["mutations"] == mutations and all(mutations.values()), "mutations")

    expected_v1_gates = {
        "null_at_most_1_of_32": original_counts["NULL"]["positional_passes"] <= 1,
        "latent_at_least_7_of_8_both": original_counts["LATENT"]["positional_passes"] >= 7 and original_counts["LATENT"]["latent_stage_passes"] >= 7,
        "fixed_at_least_7_positional_zero_latent": original_counts["FIXED"]["positional_passes"] >= 7 and original_counts["FIXED"]["latent_stage_passes"] == 0,
        "currier_one_zero_positional": original_counts["CURRIER_ONE"]["positional_passes"] == 0,
        "one_folio_zero_positional": original_counts["ONE_FOLIO"]["positional_passes"] == 0,
        "label_relabel_invariance": label_delta <= 1e-10,
        "complete_reversal_invariance": reversal_delta <= 1e-10,
        "mutation_guards": all(mutations.values()),
        "exact_capacity": len(PANEL.rows) == 21899 and sum(PANEL.splits == "TEST") == 5630 and len(set(PANEL.folios)) == 94,
        "target_absent": not TARGET_OUT.exists() and not TARGET_REPORT.exists(),
    }
    check(v1["gates"] == expected_v1_gates, "v1 gates")
    check(v1["status"] == "STOP_WITHIN_GROUP_STAGE_PREFLIGHT" and v1["decision"] == "STOP_BEFORE_STAGE_GRAMMAR_TARGET", "v1 stop")
    reversed_pattern = (
        reversed_counts["NULL"]["positional_passes"] <= 1 and reversed_counts["LATENT"]["positional_passes"] >= 7
        and reversed_counts["LATENT"]["latent_stage_passes"] >= 7 and reversed_counts["FIXED"]["positional_passes"] >= 7
        and reversed_counts["FIXED"]["latent_stage_passes"] == 0 and reversed_counts["CURRIER_ONE"]["positional_passes"] == 0
        and reversed_counts["ONE_FOLIO"]["positional_passes"] == 0
    )
    expected_v2_gates = {
        "v1_only_impossible_gate_failed": not expected_v1_gates["complete_reversal_invariance"] and all(value for key, value in expected_v1_gates.items() if key != "complete_reversal_invariance"),
        "reversed_expected_pattern": reversed_pattern,
        "all_64_decisions_reversal_stable": not decision_mismatches,
        "all_8_latent_models_reversal_stable": not latent_model_mismatches,
        "all_8_latent_principal_gains_reversal_stable": max(principal_deltas.values()) <= 1e-10,
        "all_8_latent_adaptive_gates_pass_both_orientations": all(indexed[("LATENT", world, False)]["LATENT_STAGE_PASS"] and indexed[("LATENT", world, True)]["LATENT_STAGE_PASS"] for world in range(100, 108)),
        "finite_values": all(np.isfinite(value) for record in indexed.values() for value in flatten_floats(record)),
        "exact_capacity": len(PANEL.rows) == 21899 and sum(PANEL.splits == "TEST") == 5630 and len(set(PANEL.folios)) == 94,
        "v1_label_relabel_mutation_isolation_gates": expected_v1_gates["label_relabel_invariance"] and expected_v1_gates["mutation_guards"] and expected_v1_gates["target_absent"],
        "target_absent": not TARGET_OUT.exists() and not TARGET_REPORT.exists(),
    }
    check(v2["gates"] == expected_v2_gates, "v2 gates")
    check(all(expected_v2_gates.values()), "v2 all gates")
    check(v2["status"] == "PASS_TARGET_FREE_WITHIN_GROUP_STAGE_PREFLIGHT_V2" and v2["decision"] == "GO_INDEPENDENTLY_VALIDATE_STAGE_PREFLIGHT_V2", "v2 pass")
    check(V1_REPORT.read_text() == expected_v1_report(original_counts, v1["status"], v1["decision"]), "v1 report bytes")
    max_principal_delta = max(principal_deltas.values())
    check(V2_REPORT.read_text() == expected_v2_report(reversed_counts, v2["status"], v2["decision"], max_principal_delta), "v2 report bytes")
    for result in (v1, v2):
        check(result["target_source_opened"] is False, f"{result['experiment']}:target open")
        check(result["target_sequences_accessed"] == 0 and result["target_scores_computed"] == 0, f"{result['experiment']}:target rows")
        check(result["target_outputs_absent"] is True and result["english_glosses"] == 0, f"{result['experiment']}:ceiling")
    check(not TARGET_OUT.exists() and not TARGET_REPORT.exists(), "target outputs final absence")
    if failures:
        raise SystemExit("validation failed: " + failures[0])
    result = {
        "experiment": "SOURCE_NATIVE_WITHIN_GROUP_STAGE_PREFLIGHT_V2_VALIDATION",
        "status": "PASS_INDEPENDENT_WITHIN_GROUP_STAGE_PREFLIGHT_V2_RECONSTRUCTION",
        "checks": checks,
        "failures": [],
        "reconstructed_worlds": {"original": 64, "reversed": 64},
        "original_counts": original_counts,
        "reversed_counts": reversed_counts,
        "max_record_numeric_delta": max_record_delta,
        "max_latent_principal_reversal_delta": max_principal_delta,
        "target_source_opened": False,
        "target_sequences_accessed": 0,
        "target_scores_computed": 0,
        "target_outputs_absent": True,
        "inputs": {path.name: sha(path) for path in FROZEN},
        "claim_ceiling": "Independent synthetic reconstruction only; no prefix, root, suffix, sound, word, language, meaning, plaintext, or translation follows.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(f"""# Source-native within-group stage preflight v2 validation

Status: **{result['status']}**

A production-free implementation reconstructed 64 original and 64 reversed
synthetic worlds in **{checks} checks**. The complete stored world records agree
within **{max_record_delta:.3g}**, all frozen counts and decisions reproduce,
and the largest latent selected-minus-K1 reversal difference is
**{max_principal_delta:.3g}**. The v1 contradiction and the corrected v2 pass
both reproduce exactly.

The target source was never opened; zero target sequences or scores were
accessed and target outputs remain absent. This validation supplies no prefix,
root, suffix, sound, word, language, meaning, plaintext, or translation.
""")
    print(json.dumps({"status": result["status"], "checks": checks, "max_record_numeric_delta": max_record_delta}, sort_keys=True))


def flatten_floats(value):
    if isinstance(value, dict):
        for child in value.values():
            yield from flatten_floats(child)
    elif isinstance(value, list):
        for child in value:
            yield from flatten_floats(child)
    elif isinstance(value, float):
        yield value


if __name__ == "__main__":
    main()
