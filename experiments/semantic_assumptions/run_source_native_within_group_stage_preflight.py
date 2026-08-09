#!/usr/bin/env python3
"""Run target-free calibration for the source-native stage parser."""

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

from source_native_within_group_stage_core import evaluate, latent_pass, load_panel, positional_pass, synthetic_sequences


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
PANEL_PATH = RESULTS / "source_native_within_group_stage_masked.tsv"
CAPACITY_VALIDATION = RESULTS / "source_native_within_group_stage_capacity_validation.json"
CORE = BASE / "source_native_within_group_stage_core.py"
SPEC = BASE / "SOURCE_NATIVE_WITHIN_GROUP_STAGE_TEST_SPEC.md"
RUNNER = Path(__file__).resolve()
TARGET_SOURCE = RESULTS / "source_sta_family_consensus_groups.tsv"
TARGET_OUT = RESULTS / "source_native_within_group_stage_target.json"
TARGET_REPORT = RESULTS / "source_native_within_group_stage_target_report.md"
OUT = RESULTS / "source_native_within_group_stage_preflight.json"
REPORT = RESULTS / "source_native_within_group_stage_preflight_report.md"
FROZEN = {
    PANEL_PATH: "16d7395ae0410c8fc72b5e5462d6d425cd3a2685e7ea70eee0677bd936106ae5",
    CAPACITY_VALIDATION: "2a95ce3183b72540f39a8ef0f68129d1f7ccf2e688683a9f2989360f84c20007",
    CORE: "ce1cd0854426b34e8b3e9ba0e6057352f9a5b99737e9e148e791e02979bc65dc",
    SPEC: "e3758d2a4c8d5d306b38602e8a1663ebc42a78db2abecd5905fe191a5d983d47",
}
PANEL = None


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compact(result: dict) -> dict:
    return {
        "selected_model": result["selected_model"],
        "best_fixed_model": result["best_fixed_model"],
        "candidate_diagnostics": result["candidate_diagnostics"],
        "test_groups": result["test_groups"], "test_symbols": result["test_symbols"],
        "gain_equal_symbol": result["gain_equal_symbol"],
        "gain_vs_fixed_equal_symbol": result["gain_vs_fixed_equal_symbol"],
        "gain": result["gain"], "gain_vs_fixed": result["gain_vs_fixed"],
        "unseen": result["unseen"], "currier": result["currier"],
        "POSITIONAL_PASS": positional_pass(result), "LATENT_STAGE_PASS": latent_pass(result),
    }


def task(payload: tuple[str, int]) -> dict:
    mode, world = payload
    result = evaluate(PANEL, synthetic_sequences(PANEL, world, mode))
    return {"mode": mode, "world": world, **compact(result)}


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


def main() -> None:
    global PANEL
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing to overwrite within-group stage preflight")
    if TARGET_OUT.exists() or TARGET_REPORT.exists():
        raise SystemExit("target output exists before stage preflight")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen stage preflight input mismatch: {path.name}")
    if json.loads(CAPACITY_VALIDATION.read_text())["status"] != "PASS_INDEPENDENT_SCORE_BLIND_STAGE_CAPACITY_RECONSTRUCTION":
        raise SystemExit("stage capacity validation is not PASS")
    if not TARGET_SOURCE.exists():
        raise SystemExit("target source is unexpectedly absent")
    PANEL = load_panel(PANEL_PATH)
    tasks = (
        [("NULL", world) for world in range(32)]
        + [("LATENT", 100 + world) for world in range(8)]
        + [("FIXED", 200 + world) for world in range(8)]
        + [("CURRIER_ONE", 300 + world) for world in range(8)]
        + [("ONE_FOLIO", 400 + world) for world in range(8)]
    )
    with mp.get_context("fork").Pool(32) as pool:
        records = pool.map(task, tasks)
    records.sort(key=lambda row: (tasks.index((row["mode"], row["world"]))))
    for record in records:
        values = []
        stack = [record]
        while stack:
            value = stack.pop()
            if isinstance(value, dict): stack.extend(value.values())
            elif isinstance(value, list): stack.extend(value)
            elif isinstance(value, float): values.append(value)
        if not all(np.isfinite(values)):
            raise ValueError("nonfinite stage preflight output")

    latent_reference = synthetic_sequences(PANEL, 100, "LATENT")
    reference = compact(evaluate(PANEL, latent_reference))
    permutation = np.asarray([(7 * value + 3) % 24 for value in range(24)], dtype=np.int64)
    relabeled = compact(evaluate(PANEL, [tuple(int(permutation[value]) for value in sequence) for sequence in latent_reference]))
    reversed_result = compact(evaluate(PANEL, [tuple(reversed(sequence)) for sequence in latent_reference]))
    relabel_delta = numeric_max(reference, relabeled)
    reversal_delta = numeric_max(reference, reversed_result)

    mutations = {}
    for name, altered in (
        ("missing_sequence", latent_reference[:-1]),
        ("length_mismatch", [tuple()] + latent_reference[1:]),
        ("invalid_symbol", [(-1,) + latent_reference[0][1:]] + latent_reference[1:]),
    ):
        try:
            evaluate(PANEL, altered)
        except ValueError:
            mutations[name] = True
        else:
            mutations[name] = False
    identifiers = [row["unit_id"] for row in PANEL.rows]
    mutations["duplicate_unit_id"] = len(set(identifiers + [identifiers[0]])) != len(identifiers) + 1

    by_mode = {mode: [record for record in records if record["mode"] == mode] for mode in ("NULL", "LATENT", "FIXED", "CURRIER_ONE", "ONE_FOLIO")}
    counts = {
        mode: {
            "worlds": len(values),
            "positional_passes": sum(record["POSITIONAL_PASS"] for record in values),
            "latent_stage_passes": sum(record["LATENT_STAGE_PASS"] for record in values),
        }
        for mode, values in by_mode.items()
    }
    gates = {
        "null_at_most_1_of_32": counts["NULL"]["positional_passes"] <= 1,
        "latent_at_least_7_of_8_both": counts["LATENT"]["positional_passes"] >= 7 and counts["LATENT"]["latent_stage_passes"] >= 7,
        "fixed_at_least_7_positional_zero_latent": counts["FIXED"]["positional_passes"] >= 7 and counts["FIXED"]["latent_stage_passes"] == 0,
        "currier_one_zero_positional": counts["CURRIER_ONE"]["positional_passes"] == 0,
        "one_folio_zero_positional": counts["ONE_FOLIO"]["positional_passes"] == 0,
        "label_relabel_invariance": relabel_delta <= 1e-10,
        "complete_reversal_invariance": reversal_delta <= 1e-10,
        "mutation_guards": all(mutations.values()),
        "exact_capacity": len(PANEL.rows) == 21899 and sum(PANEL.splits == "TEST") == 5630 and len(set(PANEL.folios)) == 94,
        "target_absent": not TARGET_OUT.exists() and not TARGET_REPORT.exists(),
    }
    passed = all(gates.values())
    status = "PASS_TARGET_FREE_WITHIN_GROUP_STAGE_PREFLIGHT" if passed else "STOP_WITHIN_GROUP_STAGE_PREFLIGHT"
    decision = "GO_FREEZE_ONE_STAGE_GRAMMAR_TARGET" if passed else "STOP_BEFORE_STAGE_GRAMMAR_TARGET"
    result = {
        "experiment": "SOURCE_NATIVE_WITHIN_GROUP_STAGE_PREFLIGHT",
        "status": status, "decision": decision,
        "inputs": {path.name: sha(path) for path in (*FROZEN, RUNNER)},
        "workers": 32, "records": records, "counts": counts,
        "invariance": {"label_relabel_max_abs": relabel_delta, "complete_reversal_max_abs": reversal_delta},
        "mutations": mutations, "gates": gates,
        "target_source_opened": False, "target_sequences_accessed": 0,
        "target_scores_computed": 0, "target_outputs_absent": not TARGET_OUT.exists() and not TARGET_REPORT.exists(),
        "english_glosses": 0,
        "claim_ceiling": "Synthetic calibration only. A future pass can establish complete source-native positional structure and, under the stronger gate, flexible neutral stages; no prefix, root, suffix, sound, word, meaning, plaintext, or translation follows.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(f"""# Source-native within-group stage synthetic preflight

Status: **{status}**

The 32-worker target-free grid produced **{counts['NULL']['positional_passes']}/32**
positional null passes, **{counts['LATENT']['latent_stage_passes']}/8** latent-stage
plant passes, **{counts['FIXED']['positional_passes']}/8** fixed-position passes
with **{counts['FIXED']['latent_stage_passes']}/8** false latent-stage calls,
**{counts['CURRIER_ONE']['positional_passes']}/8** one-register passes, and
**{counts['ONE_FOLIO']['positional_passes']}/8** one-folio passes.

Label relabeling, complete reversal, capacity, finite-score, mutation,
isolation, and target-absence gates are **{'all passing' if passed else 'not all passing'}**.
The target source was existence-tested only; zero target family sequences or
scores were opened.

Decision: **{decision}**. Calibration supplies no prefix, root, suffix, sound,
word, language, meaning, plaintext, or translation.
""")
    print(json.dumps({"status": status, "counts": counts, "gates": gates, "decision": decision}, sort_keys=True))


if __name__ == "__main__":
    main()
