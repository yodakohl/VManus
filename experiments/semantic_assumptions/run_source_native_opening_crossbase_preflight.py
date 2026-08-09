#!/usr/bin/env python3
"""Run target-free calibration for cross-base member transfer."""

from __future__ import annotations

import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import hashlib
import json
import tempfile
from pathlib import Path

import numpy as np

import source_native_opening_crossbase_core as core


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
PANEL = RESULTS / "source_native_opening_crossbase_masked.tsv"
QUOTAS = RESULTS / "source_native_opening_context_quotas.tsv"
CAPACITY_VALIDATION = RESULTS / "source_native_opening_crossbase_capacity_validation.json"
SPEC = BASE / "SOURCE_NATIVE_OPENING_CROSSBASE_PREFLIGHT_SPEC.md"
CORE = BASE / "source_native_opening_crossbase_core.py"
RUNNER = Path(__file__).resolve()
OUT = RESULTS / "source_native_opening_crossbase_preflight.json"
REPORT = RESULTS / "source_native_opening_crossbase_preflight_report.md"
FUTURE_TARGET = RESULTS / "source_native_opening_crossbase_target.json"
FUTURE_REPORT = RESULTS / "source_native_opening_crossbase_target_report.md"

FROZEN = {
    PANEL: "62d1a8a42c061d4e022bc406dbdf5a1152370f17c0a628511bedb9740d916c06",
    QUOTAS: "f062d9ce2935578788f9913d848c6eae2206f685ca9fa8984d29862f01ff339b",
    CAPACITY_VALIDATION: "d03f23bc4802be49bef057674c062f3588c6e6b3033a5bc032a704ff18fe7c6f",
    SPEC: "bca3426872b7ff753d2d3fb8070cb9e040056402a14276c6d1cd643f0032b723",
    CORE: "d905e84d2f9ea6e1bb4839ec237fc7f22099d2f7f57fe33718802fd82f434369",
}

TASKS = (
    [("NULL", world) for world in range(64)]
    + [("GLOBAL_SHARED", 100 + world) for world in range(8)]
    + [("BASE_RANDOM", 200 + world) for world in range(8)]
    + [("FOLIO_RANDOM", 300 + world) for world in range(8)]
    + [("ONE_BASE", 400 + world) for world in range(8)]
    + [("ONE_FAMILY", 500 + world) for world in range(8)]
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    if path.exists():
        raise FileExistsError(path)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".", delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(data)
    try:
        if path.exists():
            raise FileExistsError(path)
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    if FUTURE_TARGET.exists() or FUTURE_REPORT.exists():
        raise SystemExit("future target exists")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen mismatch: {path.name}")
    capacity = json.loads(CAPACITY_VALIDATION.read_text())
    if capacity["status"] != "PASS_INDEPENDENT_CROSSBASE_ONSET_CAPACITY_RECONSTRUCTION" or not all(capacity["gates"].values()):
        raise ValueError("capacity authorization")

    panel = core.load_panel(PANEL, QUOTAS)
    null = core.quota_labels(panel, 2048, "PREFLIGHT_NULL")
    observed = np.asarray([core.plant(panel, mode, world) for mode, world in TASKS])
    values = core.summaries(panel, observed, null)
    records = [
        {"mode": mode, "world": world, "label_sha256": core.digest(labels), **summary, "PASS": core.passes(summary, 0.01)}
        for (mode, world), labels, summary in zip(TASKS, observed, values)
    ]
    modes = ("NULL", "GLOBAL_SHARED", "BASE_RANDOM", "FOLIO_RANDOM", "ONE_BASE", "ONE_FAMILY")
    counts = {
        mode: {
            "worlds": sum(candidate == mode for candidate, _ in TASKS),
            "passes": sum(row["PASS"] for row in records if row["mode"] == mode),
        }
        for mode in modes
    }

    large_null = core.quota_labels(panel, 8192, "PREFLIGHT_NULL")
    large_observed = np.asarray([core.plant(panel, "NULL", 0), core.plant(panel, "GLOBAL_SHARED", 100)])
    large_values = core.summaries(panel, large_observed, large_null)
    target_size_checks = {
        "NULL_0": {**large_values[0], "PASS": core.passes(large_values[0], 0.01)},
        "GLOBAL_SHARED_100": {**large_values[1], "PASS": core.passes(large_values[1], 0.01)},
    }
    small_null = records[0]
    small_global = next(row for row in records if row["mode"] == "GLOBAL_SHARED" and row["world"] == 100)

    mutations = {}
    candidate = observed[:1, :-1]
    try:
        core.score(panel, candidate)
    except ValueError:
        mutations["missing_row"] = True
    else:
        mutations["missing_row"] = False
    candidate = observed[:1].copy()
    candidate[0, 0] = 0.5
    try:
        core.score(panel, candidate)
    except ValueError:
        mutations["nonbinary_assignment"] = True
    else:
        mutations["nonbinary_assignment"] = False
    candidate = observed[:1].copy()
    candidate[0, panel.cell_rows[0][0]] = 1 - candidate[0, panel.cell_rows[0][0]]
    try:
        core.score(panel, candidate)
    except ValueError:
        mutations["quota_drift"] = True
    else:
        mutations["quota_drift"] = False
    panel_text = PANEL.read_text()
    old = "\t1\n" if "\t1\n" in panel_text else None
    if old is None:
        raise ValueError("eligibility fixture")
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="", dir=RESULTS, prefix="crossbase_mutation_", delete=False) as handle:
        altered = Path(handle.name)
        handle.write(panel_text.replace(old, "\t0\n", 1))
    try:
        try:
            core.load_panel(altered, QUOTAS)
        except ValueError:
            mutations["eligibility_drift"] = True
        else:
            mutations["eligibility_drift"] = False
    finally:
        altered.unlink(missing_ok=True)

    gates = {
        "zero_of_64_null_passes": counts["NULL"]["passes"] == 0,
        "at_least_7_of_8_global_shared_passes": counts["GLOBAL_SHARED"]["passes"] >= 7,
        "zero_of_8_base_random_passes": counts["BASE_RANDOM"]["passes"] == 0,
        "zero_of_8_folio_random_passes": counts["FOLIO_RANDOM"]["passes"] == 0,
        "zero_of_8_one_base_passes": counts["ONE_BASE"]["passes"] == 0,
        "zero_of_8_one_family_passes": counts["ONE_FAMILY"]["passes"] == 0,
        "target_size_null_rejects": not target_size_checks["NULL_0"]["PASS"],
        "target_size_global_shared_passes": target_size_checks["GLOBAL_SHARED_100"]["PASS"],
        "target_size_decisions_match": target_size_checks["NULL_0"]["PASS"] == small_null["PASS"] and target_size_checks["GLOBAL_SHARED_100"]["PASS"] == small_global["PASS"],
        "mutation_guards": all(mutations.values()),
        "future_target_absent": not FUTURE_TARGET.exists() and not FUTURE_REPORT.exists(),
    }
    if all(gates.values()):
        status = "PASS_TARGET_FREE_CROSSBASE_MEMBER_PREFLIGHT"
        decision = "GO_INDEPENDENTLY_VALIDATE_CROSSBASE_MEMBER_PREFLIGHT"
    else:
        status = "STOP_CROSSBASE_MEMBER_CALIBRATION"
        decision = "DO_NOT_OPEN_CROSSBASE_MEMBER_TARGET"
    result = {
        "experiment": "SOURCE_NATIVE_OPENING_CROSSBASE_PREFLIGHT",
        "status": status,
        "decision": decision,
        "inputs": {path.name: sha(path) for path in (*FROZEN, RUNNER)},
        "assignments": 2048,
        "target_size_assignments": 8192,
        "records": records,
        "counts": counts,
        "target_size_checks": target_size_checks,
        "null_label_orbit_sha256": core.digest(null),
        "target_size_null_label_orbit_sha256": core.digest(large_null),
        "mutations": mutations,
        "gates": gates,
        "source_sta_table_opened": False,
        "prior_target_artifact_opened": False,
        "real_operation_labels_accessed": 0,
        "real_target_scores_computed": 0,
        "event_loci_or_pages_stored": 0,
        "english_glosses": 0,
        "claim_ceiling": "Target-free synthetic calibration for cross-base and cross-folio exact-member transfer only; no allomorphy, harmony, orthography, morphology, pronunciation, wordhood, POS, syntax, language, cipher operation, meaning, plaintext, or translation follows.",
    }
    report = f"""# Cross-base opening-member synthetic preflight

Status: **{status}**

At 2,048 assignments the calibration yields **{counts['NULL']['passes']}/64**
null, **{counts['GLOBAL_SHARED']['passes']}/8** global-shared,
**{counts['BASE_RANDOM']['passes']}/8** base-random,
**{counts['FOLIO_RANDOM']['passes']}/8** folio-random,
**{counts['ONE_BASE']['passes']}/8** one-base, and
**{counts['ONE_FAMILY']['passes']}/8** one-family passes. Representative null
and global-shared decisions are unchanged at 8,192 assignments.

Decision: **{decision}**. No source STA row, prior target artifact, real
operation label, or real target score was opened. This supplies no allomorphy,
harmony, morphology, meaning, plaintext, or translation.
"""
    result_bytes = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
    report_bytes = report.encode()
    atomic_write(OUT, result_bytes)
    try:
        atomic_write(REPORT, report_bytes)
    except Exception:
        OUT.unlink(missing_ok=True)
        raise
    print(json.dumps({"status": status, "decision": decision, "counts": counts, "gates": gates}, sort_keys=True))


if __name__ == "__main__":
    main()
