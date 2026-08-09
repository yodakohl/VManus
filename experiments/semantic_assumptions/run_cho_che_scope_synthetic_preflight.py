#!/usr/bin/env python3
"""Run the target-free synthetic preflight for the cho/che scope test."""

from __future__ import annotations

import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import csv
import hashlib
import json
import multiprocessing as mp
import tempfile
from pathlib import Path

import numpy as np

from cho_che_scope_core import (
    MASKED_FIELDS,
    READINGS,
    load_panels,
    panel_capacity,
    permutation_summary,
    rotated_batch,
    score_batch,
    synthetic_labels,
)


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
MASKED = RESULTS / "cho_che_scope_masked_events.tsv"
MASKED_VALIDATION = RESULTS / "cho_che_scope_masked_universe_validation.json"
CORE = BASE / "cho_che_scope_core.py"
SPEC = BASE / "CHO_CHE_SCOPE_SYNTHETIC_PREFLIGHT_SPEC.md"
RUNNER = Path(__file__).resolve()
OUT = RESULTS / "cho_che_scope_synthetic_preflight.json"
REPORT = RESULTS / "cho_che_scope_synthetic_preflight_report.md"
TARGET_SOURCE = RESULTS / "source_sta_group_alignment.tsv"
TARGET_RUNNER = BASE / "run_cho_che_scope_target.py"
TARGET_OUT = RESULTS / "cho_che_scope_target.json"
TARGET_REPORT = RESULTS / "cho_che_scope_target_report.md"

FROZEN = {
    MASKED: "41f8b517419d2215a97db9ce245c5639f383b11c41d8c1377a245dea8e37abf3",
    MASKED_VALIDATION: "e7d37a23ca199e421946fab0c42f4547aade0a5fa27579b1e9e69518c0d376ec",
    CORE: "fc57f5b96ea49fc380aabc1fbed81273111a6d3981f1fd46bbbb0aeff05891e4",
}
ASSIGNMENTS = 511
WORKERS = 32
PANELS = None


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local_pass(summaries: dict) -> bool:
    zl = summaries["ZL3b"]["local"]
    if not (
        zl["effect"] >= 0.10
        and max(zl["p_by_ensemble"].values()) <= 0.05
        and zl["minimum_leave_one_folio_out"] >= 0.05
        and zl["positive_folios"] >= 21
        and zl["folios"] == 35
        and zl["max_abs_contribution_fraction"] <= 0.15
    ):
        return False
    for edition in ("IT2a", "RF1b"):
        value = summaries[edition]["local"]
        if not (
            value["effect"] >= 0.05
            and value["minimum_leave_one_folio_out"] > 0.0
            and value["max_abs_contribution_fraction"] <= 0.18
        ):
            return False
    return True


def boundary_pass(summaries: dict) -> bool:
    zl = summaries["ZL3b"]["boundary"]
    if not (
        zl["effect"] >= 0.10
        and max(zl["p_by_ensemble"].values()) <= 0.05
        and zl["minimum_leave_one_folio_out"] >= 0.05
        and zl["positive_folios"] >= 27
        and zl["folios"] == 45
        and zl["max_abs_contribution_fraction"] <= 0.15
    ):
        return False
    for edition in ("IT2a", "RF1b"):
        value = summaries[edition]["boundary"]
        if not (
            value["effect"] >= 0.05
            and value["minimum_leave_one_folio_out"] > 0.0
            and value["max_abs_contribution_fraction"] <= 0.18
        ):
            return False
    return True


def evaluate_world(task: tuple[str, float, int]) -> dict:
    family, amplitude, world = task
    summaries = {}
    for edition in READINGS:
        panel = PANELS[edition]
        planted_folio = None
        if family == "ONE_FOLIO":
            folios = sorted(set(panel.folios))
            planted_folio = folios[world % len(folios)]
        labels = synthetic_labels(panel, world, family, amplitude, planted_folio)
        summary = permutation_summary(
            panel, labels, ASSIGNMENTS,
            f"CHO_CHE_SCOPE_PREFLIGHT|{family}|{amplitude:.1f}|{world}",
            chunk=256,
        )
        if not all(np.isfinite(value) for target in ("local", "boundary") for value in (
            summary[target]["effect"], summary[target]["minimum_leave_one_folio_out"],
            summary[target]["max_abs_contribution_fraction"],
            *summary[target]["p_by_ensemble"].values(),
        )):
            raise ValueError("nonfinite synthetic score")
        summaries[edition] = summary
    return {
        "family": family,
        "amplitude": amplitude,
        "world": world,
        "local_pass": local_pass(summaries),
        "boundary_pass": boundary_pass(summaries),
        "summaries": summaries,
    }


def mutation_controls() -> dict:
    with MASKED.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))

    def rejected(fieldnames: list[str], mutated: list[dict], name: str) -> bool:
        with tempfile.TemporaryDirectory(prefix="cho_che_scope_mutation_") as directory:
            path = Path(directory) / f"{name}.tsv"
            with path.open("x", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
                writer.writeheader()
                writer.writerows(mutated)
            try:
                load_panels(path)
            except (ValueError, KeyError):
                return True
            return False

    duplicate = [dict(row) for row in rows]
    duplicate[-1]["event_id"] = duplicate[-2]["event_id"]
    extra_fields = list(MASKED_FIELDS) + ["outcome"]
    target_column = [dict(row, outcome="0") for row in rows]
    missing_fields = [field for field in MASKED_FIELDS if field != "paragraph_id"]
    missing_column = [{field: row[field] for field in missing_fields} for row in rows]
    return {
        "duplicate_event_id_rejected": rejected(list(MASKED_FIELDS), duplicate, "duplicate"),
        "target_column_rejected": rejected(extra_fields, target_column, "target_column"),
        "missing_paragraph_column_rejected": rejected(missing_fields, missing_column, "missing_column"),
    }


def invariant_controls() -> dict:
    panel = PANELS["ZL3b"]
    labels = synthetic_labels(panel, 0, "PARAGRAPH", 2.0)
    original = permutation_summary(panel, labels, 127, "CHO_CHE_SCOPE_COMPLEMENT", chunk=64)
    complement = permutation_summary(panel, 1 - labels, 127, "CHO_CHE_SCOPE_COMPLEMENT", chunk=64)
    scalar_differences = []
    for target in ("local", "boundary"):
        for field in ("effect", "minimum_leave_one_folio_out", "max_abs_contribution_fraction"):
            scalar_differences.append(abs(original[target][field] - complement[target][field]))
        for ensemble in ("INDEPENDENT_STRATUM", "COUPLED_PAGE"):
            scalar_differences.append(abs(original[target]["p_by_ensemble"][ensemble] - complement[target]["p_by_ensemble"][ensemble]))

    multiset_ok = True
    assignments = np.arange(1, 17, dtype=np.uint64)
    for ensemble in ("INDEPENDENT_STRATUM", "COUPLED_PAGE"):
        rotations = rotated_batch(panel, labels, assignments, ensemble, "CHO_CHE_SCOPE_MULTISET")
        for positions, page, key in panel.rotation_strata:
            if not np.all(rotations[:, positions].sum(axis=1) == labels[positions].sum()):
                multiset_ok = False
    return {
        "complement_max_abs_difference": max(scalar_differences),
        "complement_invariant_within_1e_12": max(scalar_differences) <= 1e-12,
        "rotation_stratum_label_multisets_preserved": multiset_ok,
    }


def install_pair(result_bytes: bytes, report_bytes: bytes) -> None:
    if OUT.exists() or REPORT.exists():
        raise FileExistsError("preflight output already exists")
    with tempfile.TemporaryDirectory(prefix="cho_che_scope_output_", dir=RESULTS) as directory:
        result_stage = Path(directory) / "result.json"
        report_stage = Path(directory) / "report.md"
        result_stage.write_bytes(result_bytes)
        report_stage.write_bytes(report_bytes)
        if OUT.exists() or REPORT.exists():
            raise FileExistsError("preflight output appeared during run")
        os.link(result_stage, OUT)
        try:
            os.link(report_stage, REPORT)
        except Exception:
            OUT.unlink(missing_ok=True)
            raise


def main() -> None:
    global PANELS
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing to overwrite synthetic preflight artifacts")
    if TARGET_OUT.exists() or TARGET_REPORT.exists():
        raise SystemExit("target output exists before preflight")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen input mismatch: {path.name}")
    validation = json.loads(MASKED_VALIDATION.read_text())
    if validation["status"] != "PASS_INDEPENDENT_COMPLETE_MASKED_UNIVERSE_RECONSTRUCTION":
        raise SystemExit("masked-universe validation is not PASS")
    PANELS = load_panels(MASKED)
    capacities = {edition: panel_capacity(PANELS[edition]) for edition in READINGS}
    expected_capacities = {
        "ZL3b": {"events": 9983, "queries": 501, "local_folios": 35, "boundary_pairs": 1299, "boundary_strata": 282, "boundary_folios": 45},
        "IT2a": {"events": 10124, "queries": 501, "local_folios": 36, "boundary_pairs": 1292, "boundary_strata": 282, "boundary_folios": 45},
        "RF1b": {"events": 10053, "queries": 501, "local_folios": 34, "boundary_pairs": 1292, "boundary_strata": 277, "boundary_folios": 44},
    }
    if capacities != expected_capacities:
        raise ValueError(f"scope capacity drift: {capacities}")

    tasks = (
        [("NULL", 1.0, world) for world in range(64)]
        + [("PARAGRAPH", 2.0, world) for world in range(8)]
        + [("PARAGRAPH", 3.5, world) for world in range(8)]
        + [("ONE_FOLIO", 4.0, world) for world in range(8)]
        + [("SEQUENTIAL", 0.9, world) for world in range(8)]
    )
    with mp.get_context("fork").Pool(WORKERS) as pool:
        worlds = pool.map(evaluate_world, tasks)
    worlds.sort(key=lambda row: (row["family"], row["amplitude"], row["world"]))

    def selected(family: str, amplitude: float) -> list[dict]:
        return [row for row in worlds if row["family"] == family and row["amplitude"] == amplitude]

    null = selected("NULL", 1.0)
    local_power = selected("PARAGRAPH", 2.0)
    boundary_power = selected("PARAGRAPH", 3.5)
    one_folio = selected("ONE_FOLIO", 4.0)
    sequential = selected("SEQUENTIAL", 0.9)
    mutations = mutation_controls()
    invariants = invariant_controls()
    gates = {
        "exact_capacity": capacities == expected_capacities,
        "local_null_false_passes_at_most_3_of_64": sum(row["local_pass"] for row in null) <= 3,
        "boundary_null_false_passes_at_most_3_of_64": sum(row["boundary_pass"] for row in null) <= 3,
        "local_power_at_least_7_of_8": sum(row["local_pass"] for row in local_power) >= 7,
        "boundary_power_at_least_7_of_8": sum(row["boundary_pass"] for row in boundary_power) >= 7,
        "one_folio_local_zero_of_8": sum(row["local_pass"] for row in one_folio) == 0,
        "one_folio_boundary_zero_of_8": sum(row["boundary_pass"] for row in one_folio) == 0,
        "sequential_local_zero_of_8": sum(row["local_pass"] for row in sequential) == 0,
        "sequential_boundary_zero_of_8": sum(row["boundary_pass"] for row in sequential) == 0,
        "complement_invariance": invariants["complement_invariant_within_1e_12"],
        "rotation_multiset_preservation": invariants["rotation_stratum_label_multisets_preserved"],
        "mutation_guards": all(mutations.values()),
        "target_outputs_absent_before_and_after": not TARGET_OUT.exists() and not TARGET_REPORT.exists(),
    }
    status = "PASS_TARGET_FREE_SCOPE_PREFLIGHT" if all(gates.values()) else "STOP_SCOPE_PREFLIGHT_FAILED_TARGET_FORBIDDEN"
    result = {
        "experiment": "CHO_CHE_SCOPE_SYNTHETIC_PREFLIGHT",
        "status": status,
        "inputs": {path.name: sha(path) for path in (*FROZEN, SPEC, RUNNER)},
        "numeric_environment": {"OPENBLAS_NUM_THREADS": os.environ["OPENBLAS_NUM_THREADS"], "OMP_NUM_THREADS": os.environ["OMP_NUM_THREADS"], "MKL_NUM_THREADS": os.environ["MKL_NUM_THREADS"], "workers": WORKERS},
        "assignments_per_ensemble": ASSIGNMENTS,
        "capacities": capacities,
        "worlds": worlds,
        "aggregates": {
            "null_worlds": len(null),
            "null_local_passes": sum(row["local_pass"] for row in null),
            "null_boundary_passes": sum(row["boundary_pass"] for row in null),
            "local_power_passes": sum(row["local_pass"] for row in local_power),
            "boundary_power_passes": sum(row["boundary_pass"] for row in boundary_power),
            "one_folio_local_passes": sum(row["local_pass"] for row in one_folio),
            "one_folio_boundary_passes": sum(row["boundary_pass"] for row in one_folio),
            "sequential_local_passes": sum(row["local_pass"] for row in sequential),
            "sequential_boundary_passes": sum(row["boundary_pass"] for row in sequential),
        },
        "invariants": invariants,
        "mutations": mutations,
        "gates": gates,
        "target_isolation": {
            "source_alignment_exists_checked_only": TARGET_SOURCE.exists(),
            "source_alignment_opened": False,
            "target_runner_exists": TARGET_RUNNER.exists(),
            "target_output_exists": TARGET_OUT.exists(),
            "target_report_exists": TARGET_REPORT.exists(),
            "target_outcomes_accessed": 0,
            "target_scores_computed": 0,
        },
        "decision": "GO_FREEZE_ONE_TARGET_RUN" if all(gates.values()) else "STOP_TARGET_FORBIDDEN",
        "claim_ceiling": (
            "Synthetic capacity and error-control validation only. A future pass can establish "
            "marked-span-aligned formal choice persistence and, separately, a distance-controlled "
            "editorial-boundary association. No authorial paragraph, sound, word, language, cipher "
            "operation, meaning, plaintext, or translation follows."
        ),
    }
    report = f"""# `cho/che` paragraph-scope synthetic preflight

Status: **{status}**

Using only the 30,160-row outcome-masked universe, the frozen two-ensemble
scorer produced **{result['aggregates']['null_local_passes']}/64** local and
**{result['aggregates']['null_boundary_passes']}/64** boundary false passes.
It recovered **{result['aggregates']['local_power_passes']}/8** local plants
and **{result['aggregates']['boundary_power_passes']}/8** stronger
distance-controlled boundary plants. One-folio and generic sequential controls
produced **{result['aggregates']['one_folio_local_passes']}/8,
{result['aggregates']['one_folio_boundary_passes']}/8** and
**{result['aggregates']['sequential_local_passes']}/8,
{result['aggregates']['sequential_boundary_passes']}/8** local/boundary passes.

Complement, rotation-multiset, capacity, finite-score, mutation, isolation, and
target-absence gates all {'passed' if all(gates.values()) else 'did not all pass'}.
The source outcome table was existence-tested only; **zero target outcomes and
zero target scores** were accessed.

{result['decision']} authorizes at most one separately frozen target run. No
authorial paragraph, sound, word, language, cipher operation, meaning,
plaintext, or translation follows from this preflight.
"""
    install_pair((json.dumps(result, indent=2, sort_keys=True) + "\n").encode(), report.encode())
    print(json.dumps({"status": status, "aggregates": result["aggregates"], "decision": result["decision"]}, sort_keys=True))


if __name__ == "__main__":
    main()
