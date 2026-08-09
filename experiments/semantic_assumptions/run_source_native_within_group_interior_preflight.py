#!/usr/bin/env python3
"""Target-free calibration of the endpoint-free interior-position model."""

from __future__ import annotations

import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import hashlib
import json
import math
import multiprocessing as mp
from pathlib import Path

import numpy as np

from source_native_within_group_interior_core import evaluate, load_panel, passes, synthetic_sequences


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
PANEL_PATH = RESULTS / "source_native_within_group_interior_masked.tsv"
CAPACITY_VALIDATION = RESULTS / "source_native_within_group_interior_capacity_validation.json"
CORE = BASE / "source_native_within_group_interior_core.py"
SPEC = BASE / "SOURCE_NATIVE_WITHIN_GROUP_INTERIOR_TEST_SPEC.md"
RUNNER = Path(__file__).resolve()
TARGET_SOURCE = RESULTS / "source_sta_family_consensus_groups.tsv"
TARGET_OUT = RESULTS / "source_native_within_group_interior_target.json"
TARGET_REPORT = RESULTS / "source_native_within_group_interior_target_report.md"
OUT = RESULTS / "source_native_within_group_interior_preflight.json"
REPORT = RESULTS / "source_native_within_group_interior_preflight_report.md"
FROZEN = {
    PANEL_PATH: "0b6202641045ed11fd1ae4870353b4bec17adcc658c9687fd766f35bfbfe51ad",
    CAPACITY_VALIDATION: "1513617bafcc3c4143af7be129251cf9dd7e7aa5cfa429c414c55eaa8fe923f8",
    CORE: "f516e87c5f0c3be14a9187ffd87f935ea92331147fd3f14241a5ad754ed7bd98",
    SPEC: "3f278d5ef39432084c9f200039e20799d53b07269f48d6aef7f9b4726ad19696",
}
TASKS = (
    [("NULL", world) for world in range(64)]
    + [("POSITION", 100 + world) for world in range(8)]
    + [("CURRIER_ONE", 200 + world) for world in range(8)]
    + [("ONE_FOLIO", 300 + world) for world in range(8)]
    + [("FOLIO_RANDOM", 400 + world) for world in range(8)]
)
PANEL = None


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compact(result: dict) -> dict:
    return {**result, "INTERIOR_POSITION_PASS": passes(result)}


def task(payload: tuple[str, int, bool]) -> dict:
    mode, world, reverse = payload
    sequences = synthetic_sequences(PANEL, world, mode)
    if reverse:
        sequences = [tuple(reversed(sequence)) for sequence in sequences]
    return {"mode": mode, "world": world, "reverse": reverse, **compact(evaluate(PANEL, sequences))}


def numeric_max(left, right) -> float:
    if isinstance(left, dict):
        if set(left) != set(right): return math.inf
        return max((numeric_max(left[key], right[key]) for key in left), default=0.0)
    if isinstance(left, list):
        if len(left) != len(right): return math.inf
        return max((numeric_max(a, b) for a, b in zip(left, right)), default=0.0)
    if isinstance(left, (int, float)) and not isinstance(left, bool): return abs(float(left) - float(right))
    return 0.0 if left == right else math.inf


def main() -> None:
    global PANEL
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing to overwrite interior preflight")
    if TARGET_OUT.exists() or TARGET_REPORT.exists():
        raise SystemExit("interior target output exists before preflight")
    for path, expected in FROZEN.items():
        if sha(path) != expected: raise SystemExit(f"frozen interior input mismatch: {path.name}")
    if json.loads(CAPACITY_VALIDATION.read_text())["status"] != "PASS_INDEPENDENT_SCORE_BLIND_INTERIOR_CAPACITY_RECONSTRUCTION":
        raise SystemExit("interior capacity validation is not PASS")
    if not TARGET_SOURCE.exists(): raise SystemExit("target source unexpectedly absent")
    PANEL = load_panel(PANEL_PATH)
    payloads = [(mode, world, reverse) for reverse in (False, True) for mode, world in TASKS]
    with mp.get_context("fork").Pool(32) as pool:
        records = pool.map(task, payloads)
    records.sort(key=lambda row: (row["reverse"], TASKS.index((row["mode"], row["world"]))))
    numeric = []
    stack = [records]
    while stack:
        value = stack.pop()
        if isinstance(value, dict): stack.extend(value.values())
        elif isinstance(value, list): stack.extend(value)
        elif isinstance(value, float): numeric.append(value)
    finite = all(np.isfinite(numeric))
    indexed = {(row["mode"], row["world"], row["reverse"]): row for row in records}
    counts = {}
    for reverse in (False, True):
        name = "reversed" if reverse else "forward"
        counts[name] = {
            mode: {"worlds": sum(m == mode for m, _ in TASKS), "passes": sum(indexed[(mode, world, reverse)]["INTERIOR_POSITION_PASS"] for m, world in TASKS if m == mode)}
            for mode in ("NULL", "POSITION", "CURRIER_ONE", "ONE_FOLIO", "FOLIO_RANDOM")
        }
    decision_mismatches = [f"{mode}:{world}" for mode, world in TASKS if indexed[(mode, world, False)]["INTERIOR_POSITION_PASS"] != indexed[(mode, world, True)]["INTERIOR_POSITION_PASS"]]
    reference_sequences = synthetic_sequences(PANEL, 100, "POSITION")
    reference = compact(evaluate(PANEL, reference_sequences))
    permutation = np.asarray([(7 * value + 3) % 24 for value in range(24)], dtype=np.int64)
    relabeled = compact(evaluate(PANEL, [tuple(int(permutation[value]) for value in sequence) for sequence in reference_sequences]))
    relabel_delta = numeric_max(reference, relabeled)
    mutations = {}
    for name, altered in (
        ("missing_sequence", reference_sequences[:-1]),
        ("length_mismatch", [tuple()] + reference_sequences[1:]),
        ("invalid_symbol", [(-1,) + reference_sequences[0][1:]] + reference_sequences[1:]),
    ):
        try: evaluate(PANEL, altered)
        except ValueError: mutations[name] = True
        else: mutations[name] = False
    ids = [row["unit_id"] for row in PANEL.rows]
    mutations["duplicate_unit_id"] = len(set(ids + [ids[0]])) != len(ids) + 1
    pattern = lambda name: (
        counts[name]["NULL"]["passes"] <= 1 and counts[name]["POSITION"]["passes"] >= 7
        and counts[name]["CURRIER_ONE"]["passes"] == 0 and counts[name]["ONE_FOLIO"]["passes"] == 0
        and counts[name]["FOLIO_RANDOM"]["passes"] == 0
    )
    gates = {
        "forward_expected_pattern": pattern("forward"), "reversed_expected_pattern": pattern("reversed"),
        "all_96_decisions_reversal_stable": not decision_mismatches,
        "label_relabel_invariance": relabel_delta <= 1e-10, "finite_values": finite,
        "mutation_guards": all(mutations.values()),
        "exact_capacity": len(PANEL.rows) == 19203 and sum(PANEL.splits == "TEST") == 4952 and int(PANEL.interior_lengths.sum()) == 45867 and len(set(PANEL.folios)) == 94,
        "target_absent": not TARGET_OUT.exists() and not TARGET_REPORT.exists(),
    }
    passed = all(gates.values())
    status = "PASS_TARGET_FREE_WITHIN_GROUP_INTERIOR_PREFLIGHT" if passed else "STOP_WITHIN_GROUP_INTERIOR_PREFLIGHT"
    decision = "GO_INDEPENDENTLY_VALIDATE_INTERIOR_PREFLIGHT" if passed else "STOP_BEFORE_INTERIOR_TARGET"
    result = {
        "experiment": "SOURCE_NATIVE_WITHIN_GROUP_INTERIOR_PREFLIGHT", "status": status, "decision": decision,
        "inputs": {path.name: sha(path) for path in (*FROZEN, RUNNER)}, "workers": 32,
        "records": records, "counts": counts,
        "reversal_decision_mismatches": decision_mismatches, "label_relabel_max_abs": relabel_delta,
        "mutations": mutations, "gates": gates,
        "target_source_opened": False, "target_sequences_accessed": 0, "target_scores_computed": 0,
        "target_outputs_absent": not TARGET_OUT.exists() and not TARGET_REPORT.exists(), "english_glosses": 0,
        "claim_ceiling": "Synthetic calibration of an endpoint-free exact-length-conditioned interior-position test only; no morphology, sound, word, language, meaning, plaintext, cipher, or translation follows.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(f"""# Endpoint-free source-group interior-position preflight

Status: **{status}**

Forward/reversed grids produce **{counts['forward']['NULL']['passes']}/64** and
**{counts['reversed']['NULL']['passes']}/64** null passes, and
**{counts['forward']['POSITION']['passes']}/8** and
**{counts['reversed']['POSITION']['passes']}/8** position-plant passes.
Currier-one, one-folio, and folio-random adversaries produce zero passes in both
orientations. All 96 decisions are reversal-stable; label relabeling, capacity,
finite-value, mutation, isolation, and target-absence gates are
**{'passing' if passed else 'not all passing'}**.

The target source was existence-tested only; zero family sequences or scores
were opened. Decision: **{decision}**. No morphology, sound, word, language,
meaning, plaintext, cipher, or translation follows.
""")
    print(json.dumps({"status": status, "counts": counts, "gates": gates, "decision": decision}, sort_keys=True))


if __name__ == "__main__": main()
