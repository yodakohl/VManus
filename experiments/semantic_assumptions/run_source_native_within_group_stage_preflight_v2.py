#!/usr/bin/env python3
"""Repair only the impossible reversal control in the frozen stage preflight."""

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

from source_native_within_group_stage_core import (
    evaluate,
    latent_pass,
    load_panel,
    positional_pass,
    synthetic_sequences,
)


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
PANEL_PATH = RESULTS / "source_native_within_group_stage_masked.tsv"
V1_RESULT = RESULTS / "source_native_within_group_stage_preflight.json"
V1_REPORT = RESULTS / "source_native_within_group_stage_preflight_report.md"
V1_RUNNER = BASE / "run_source_native_within_group_stage_preflight.py"
V1_SPEC = BASE / "SOURCE_NATIVE_WITHIN_GROUP_STAGE_TEST_SPEC.md"
CORE = BASE / "source_native_within_group_stage_core.py"
AMENDMENT = BASE / "SOURCE_NATIVE_WITHIN_GROUP_STAGE_PREFLIGHT_V2_AMENDMENT.md"
RUNNER = Path(__file__).resolve()
TARGET_SOURCE = RESULTS / "source_sta_family_consensus_groups.tsv"
TARGET_OUT = RESULTS / "source_native_within_group_stage_target.json"
TARGET_REPORT = RESULTS / "source_native_within_group_stage_target_report.md"
OUT = RESULTS / "source_native_within_group_stage_preflight_v2.json"
REPORT = RESULTS / "source_native_within_group_stage_preflight_v2_report.md"
FROZEN = {
    PANEL_PATH: "16d7395ae0410c8fc72b5e5462d6d425cd3a2685e7ea70eee0677bd936106ae5",
    V1_RESULT: "6e11363eb76ec056504b349764fc998a0b9561dbef25c83a095fadc786071b11",
    V1_REPORT: "3ddbcba4868e754a8c63ed27745481f4ff0da79f1370ff0d7a5e7163865912c8",
    V1_RUNNER: "211452815b78c9e01f4548b6a61226730bf36080b5185697dc9ac041f0abceaf",
    V1_SPEC: "e3758d2a4c8d5d306b38602e8a1663ebc42a78db2abecd5905fe191a5d983d47",
    CORE: "ce1cd0854426b34e8b3e9ba0e6057352f9a5b99737e9e148e791e02979bc65dc",
    AMENDMENT: "b0b42cc092c2b97ac919d5ecc471d890a09a7c5e0b21fe10548efb543c02bc80",
}
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


def compact(result: dict) -> dict:
    return {
        "selected_model": result["selected_model"],
        "best_fixed_model": result["best_fixed_model"],
        "candidate_diagnostics": result["candidate_diagnostics"],
        "test_groups": result["test_groups"],
        "test_symbols": result["test_symbols"],
        "gain_equal_symbol": result["gain_equal_symbol"],
        "gain_vs_fixed_equal_symbol": result["gain_vs_fixed_equal_symbol"],
        "gain": result["gain"],
        "gain_vs_fixed": result["gain_vs_fixed"],
        "unseen": result["unseen"],
        "currier": result["currier"],
        "POSITIONAL_PASS": positional_pass(result),
        "LATENT_STAGE_PASS": latent_pass(result),
    }


def task(payload: tuple[str, int]) -> dict:
    mode, world = payload
    sequences = synthetic_sequences(PANEL, world, mode)
    result = evaluate(PANEL, [tuple(reversed(sequence)) for sequence in sequences])
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


def principal_gain(record: dict) -> dict:
    return {
        "test_groups": record["test_groups"],
        "test_symbols": record["test_symbols"],
        "gain_equal_symbol": record["gain_equal_symbol"],
        "gain": record["gain"],
        "unseen": record["unseen"],
        "currier": {
            currier: {"gain": record["currier"][currier]["gain"]}
            for currier in ("A", "B")
        },
    }


def main() -> None:
    global PANEL
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing to overwrite within-group stage v2 preflight")
    if TARGET_OUT.exists() or TARGET_REPORT.exists():
        raise SystemExit("target output exists before stage v2 preflight")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen stage v2 input mismatch: {path.name}")
    if not TARGET_SOURCE.exists():
        raise SystemExit("target source is unexpectedly absent")

    v1 = json.loads(V1_RESULT.read_text())
    expected_v1_gates = {
        "null_at_most_1_of_32",
        "latent_at_least_7_of_8_both",
        "fixed_at_least_7_positional_zero_latent",
        "currier_one_zero_positional",
        "one_folio_zero_positional",
        "label_relabel_invariance",
        "complete_reversal_invariance",
        "mutation_guards",
        "exact_capacity",
        "target_absent",
    }
    if set(v1["gates"]) != expected_v1_gates:
        raise SystemExit("v1 gate schema drift")
    v1_only_impossible_gate_failed = (
        v1["status"] == "STOP_WITHIN_GROUP_STAGE_PREFLIGHT"
        and v1["decision"] == "STOP_BEFORE_STAGE_GRAMMAR_TARGET"
        and not v1["gates"]["complete_reversal_invariance"]
        and all(value for key, value in v1["gates"].items() if key != "complete_reversal_invariance")
        and not v1["target_source_opened"]
        and v1["target_sequences_accessed"] == 0
        and v1["target_scores_computed"] == 0
    )
    if len(v1["records"]) != 64:
        raise SystemExit("v1 synthetic record count drift")
    original = {(row["mode"], row["world"]): row for row in v1["records"]}
    if set(original) != set(TASKS):
        raise SystemExit("v1 synthetic world identity drift")

    PANEL = load_panel(PANEL_PATH)
    with mp.get_context("fork").Pool(32) as pool:
        reversed_records = pool.map(task, TASKS)
    reversed_records.sort(key=lambda row: TASKS.index((row["mode"], row["world"])))

    numeric_values = []
    for record in reversed_records:
        stack = [record]
        while stack:
            value = stack.pop()
            if isinstance(value, dict):
                stack.extend(value.values())
            elif isinstance(value, list):
                stack.extend(value)
            elif isinstance(value, float):
                numeric_values.append(value)
    finite_values = all(np.isfinite(numeric_values))

    by_mode = {
        mode: [record for record in reversed_records if record["mode"] == mode]
        for mode in ("NULL", "LATENT", "FIXED", "CURRIER_ONE", "ONE_FOLIO")
    }
    reversed_counts = {
        mode: {
            "worlds": len(values),
            "positional_passes": sum(record["POSITIONAL_PASS"] for record in values),
            "latent_stage_passes": sum(record["LATENT_STAGE_PASS"] for record in values),
        }
        for mode, values in by_mode.items()
    }
    decision_mismatches = []
    latent_model_mismatches = []
    principal_deltas = {}
    for record in reversed_records:
        key = (record["mode"], record["world"])
        before = original[key]
        if (
            before["POSITIONAL_PASS"] != record["POSITIONAL_PASS"]
            or before["LATENT_STAGE_PASS"] != record["LATENT_STAGE_PASS"]
        ):
            decision_mismatches.append(f"{key[0]}:{key[1]}")
        if record["mode"] == "LATENT":
            if before["selected_model"] != record["selected_model"]:
                latent_model_mismatches.append(str(record["world"]))
            principal_deltas[str(record["world"])] = numeric_max(
                principal_gain(before), principal_gain(record)
            )

    reversed_expected_pattern = (
        reversed_counts["NULL"]["positional_passes"] <= 1
        and reversed_counts["LATENT"]["positional_passes"] >= 7
        and reversed_counts["LATENT"]["latent_stage_passes"] >= 7
        and reversed_counts["FIXED"]["positional_passes"] >= 7
        and reversed_counts["FIXED"]["latent_stage_passes"] == 0
        and reversed_counts["CURRIER_ONE"]["positional_passes"] == 0
        and reversed_counts["ONE_FOLIO"]["positional_passes"] == 0
    )
    gates = {
        "v1_only_impossible_gate_failed": v1_only_impossible_gate_failed,
        "reversed_expected_pattern": reversed_expected_pattern,
        "all_64_decisions_reversal_stable": not decision_mismatches,
        "all_8_latent_models_reversal_stable": not latent_model_mismatches,
        "all_8_latent_principal_gains_reversal_stable": max(principal_deltas.values()) <= 1e-10,
        "all_8_latent_adaptive_gates_pass_both_orientations": all(
            original[("LATENT", world)]["LATENT_STAGE_PASS"]
            and next(row for row in by_mode["LATENT"] if row["world"] == world)["LATENT_STAGE_PASS"]
            for world in range(100, 108)
        ),
        "finite_values": finite_values,
        "exact_capacity": len(PANEL.rows) == 21899 and sum(PANEL.splits == "TEST") == 5630 and len(set(PANEL.folios)) == 94,
        "v1_label_relabel_mutation_isolation_gates": (
            v1["gates"]["label_relabel_invariance"]
            and v1["gates"]["mutation_guards"]
            and v1["gates"]["target_absent"]
        ),
        "target_absent": not TARGET_OUT.exists() and not TARGET_REPORT.exists(),
    }
    passed = all(gates.values())
    status = "PASS_TARGET_FREE_WITHIN_GROUP_STAGE_PREFLIGHT_V2" if passed else "STOP_WITHIN_GROUP_STAGE_PREFLIGHT_V2"
    decision = "GO_INDEPENDENTLY_VALIDATE_STAGE_PREFLIGHT_V2" if passed else "STOP_BEFORE_STAGE_GRAMMAR_TARGET"
    result = {
        "experiment": "SOURCE_NATIVE_WITHIN_GROUP_STAGE_PREFLIGHT_V2",
        "status": status,
        "decision": decision,
        "inputs": {path.name: sha(path) for path in (*FROZEN, RUNNER)},
        "workers": 32,
        "original_counts": v1["counts"],
        "reversed_counts": reversed_counts,
        "reversed_records": reversed_records,
        "reversal": {
            "decision_mismatches": decision_mismatches,
            "latent_model_mismatches": latent_model_mismatches,
            "latent_principal_gain_max_abs_by_world": principal_deltas,
            "allowed_orientation_sensitive_field": "best FIXED_K identity and selected-minus-best-FIXED numeric margin",
        },
        "gates": gates,
        "target_source_opened": False,
        "target_sequences_accessed": 0,
        "target_scores_computed": 0,
        "target_outputs_absent": not TARGET_OUT.exists() and not TARGET_REPORT.exists(),
        "english_glosses": 0,
        "claim_ceiling": "Synthetic calibration only. A future pass can establish complete source-native positional structure and, under the stronger gate, flexible neutral stages; no prefix, root, suffix, sound, word, meaning, plaintext, or translation follows.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(f"""# Source-native within-group stage synthetic preflight v2

Status: **{status}**

The preserved v1 grid had only its mathematically incompatible whole-object
reversal gate fail. Under the corrected predeclared reversal control, all 64
synthetic pass decisions are {'stable' if not decision_mismatches else 'not stable'},
all eight latent plants retain their selected model, and their maximum complete
selected-minus-K1 summary difference is **{max(principal_deltas.values()):.3g}**.

The reversed grid yields **{reversed_counts['NULL']['positional_passes']}/32**
null positional passes, **{reversed_counts['LATENT']['latent_stage_passes']}/8**
latent passes, **{reversed_counts['FIXED']['positional_passes']}/8** fixed
positional passes with **{reversed_counts['FIXED']['latent_stage_passes']}/8**
false latent calls, **{reversed_counts['CURRIER_ONE']['positional_passes']}/8**
one-register passes, and **{reversed_counts['ONE_FOLIO']['positional_passes']}/8**
one-folio passes.

The target source was existence-tested only; zero target sequences or scores
were opened. Decision: **{decision}**. This calibration supplies no prefix,
root, suffix, sound, word, language, meaning, plaintext, or translation.
""")
    print(json.dumps({"status": status, "reversed_counts": reversed_counts, "gates": gates, "decision": decision}, sort_keys=True))


if __name__ == "__main__":
    main()
