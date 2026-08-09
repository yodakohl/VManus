#!/usr/bin/env python3
"""Run target-free calibration of the opening-onset compatibility statistic."""

from __future__ import annotations

import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import hashlib
import json
from pathlib import Path

import numpy as np

import source_native_opening_onset_core as core


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
PANEL = RESULTS / "source_native_opening_onset_masked.tsv"
QUOTAS = RESULTS / "source_native_opening_context_quotas.tsv"
CAPACITY = RESULTS / "source_native_opening_onset_capacity.json"
CAPACITY_VALIDATION = RESULTS / "source_native_opening_onset_capacity_validation.json"
CORE = BASE / "source_native_opening_onset_core.py"
SPEC = BASE / "SOURCE_NATIVE_OPENING_ONSET_PREFLIGHT_SPEC.md"
RUNNER = Path(__file__).resolve()
OUT = RESULTS / "source_native_opening_onset_preflight.json"
REPORT = RESULTS / "source_native_opening_onset_preflight_report.md"
TARGET_OUT = RESULTS / "source_native_opening_onset_target.json"
TARGET_REPORT = RESULTS / "source_native_opening_onset_target_report.md"

FROZEN = {
    PANEL: "628d2f657db080b975f2e201d6d684f3dab7ede75b19be6cc4e4c4b3f580e4a2",
    QUOTAS: "f062d9ce2935578788f9913d848c6eae2206f685ca9fa8984d29862f01ff339b",
    CAPACITY: "086718ac1bb1563dbcf212b349cd95d1875d481e08be01662ab4a31d8d1975e4",
    CAPACITY_VALIDATION: "bdb86a58e5ee0ef9850554d7b65685c9cf0a35f1af06cefd30f676e17ec6abed",
    CORE: "33c1870c0e8f80516a02573a279f78b2eba4b12a2b2225bfe864525d18bc2adf",
    SPEC: "121aab44a4ec43a6b0da15487604d4a0463bea761f0845c930d0d076bc8ef657",
}

TASKS = (
    [("NULL", world) for world in range(64)]
    + [("GLOBAL_ONSET", 100 + world) for world in range(8)]
    + [("ONE_FOLIO", 200 + world) for world in range(8)]
    + [("FOLIO_RANDOM", 300 + world) for world in range(8)]
    + [("ONE_BASE", 400 + world) for world in range(8)]
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(array) -> str:
    return hashlib.sha256(np.ascontiguousarray(array, dtype="<f8").tobytes()).hexdigest()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    if TARGET_OUT.exists() or TARGET_REPORT.exists():
        raise SystemExit("target output already exists")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen mismatch: {path.name}")
    capacity = json.loads(CAPACITY.read_text())
    validation = json.loads(CAPACITY_VALIDATION.read_text())
    if capacity["status"] != "PASS_TARGET_MASKED_OPENING_ONSET_CAPACITY" or validation["status"] != "PASS_INDEPENDENT_1207_ROW_OPENING_ONSET_CAPACITY_RECONSTRUCTION":
        raise ValueError("capacity authorization")
    panel = core.load_panel(PANEL, QUOTAS)
    null = core.quota_labels(panel, 2048, "PREFLIGHT_NULL")
    observed = np.asarray([core.planted_labels(panel, mode, world, 0.80) for mode, world in TASKS], dtype=np.float64)
    summaries = core.summarize(panel, observed, null)
    records = []
    for (mode, world), labels, summary in zip(TASKS, observed, summaries):
        records.append({"mode": mode, "world": world, "label_sha256": digest(labels), **summary, "PASS": core.passes(summary, 0.01)})
    counts = {
        mode: {
            "worlds": sum(candidate == mode for candidate, _ in TASKS),
            "passes": sum(row["PASS"] for row in records if row["mode"] == mode),
        }
        for mode in ("NULL", "GLOBAL_ONSET", "ONE_FOLIO", "FOLIO_RANDOM", "ONE_BASE")
    }
    large_null = core.quota_labels(panel, 8192, "PREFLIGHT_NULL")
    large_labels = np.asarray([core.planted_labels(panel, "NULL", 0, 0.80), core.planted_labels(panel, "GLOBAL_ONSET", 100, 0.80)])
    large_summaries = core.summarize(panel, large_labels, large_null)
    target_size_checks = {
        "NULL_0": {**large_summaries[0], "PASS": core.passes(large_summaries[0], 0.01)},
        "GLOBAL_ONSET_100": {**large_summaries[1], "PASS": core.passes(large_summaries[1], 0.01)},
    }
    small_null = next(row for row in records if row["mode"] == "NULL" and row["world"] == 0)
    small_global = next(row for row in records if row["mode"] == "GLOBAL_ONSET" and row["world"] == 100)
    mutations = {}
    reference = observed[:1].copy()
    for name, altered in (
        ("missing_row", reference[:, :-1]),
        ("nonbinary_label", np.where(np.arange(reference.shape[1])[None, :] == 0, 0.5, reference)),
        ("quota_drift", np.where(np.arange(reference.shape[1])[None, :] == panel.stratum_indices[0][0], 1.0 - reference, reference)),
    ):
        try:
            core.score_assignments(panel, altered)
        except ValueError:
            mutations[name] = True
        else:
            mutations[name] = False
    gates = {
        "zero_of_64_null_passes": counts["NULL"]["passes"] == 0,
        "at_least_7_of_8_global_onset_passes": counts["GLOBAL_ONSET"]["passes"] >= 7,
        "zero_of_8_one_folio_passes": counts["ONE_FOLIO"]["passes"] == 0,
        "zero_of_8_folio_random_passes": counts["FOLIO_RANDOM"]["passes"] == 0,
        "zero_of_8_one_base_passes": counts["ONE_BASE"]["passes"] == 0,
        "target_size_null_rejects": not target_size_checks["NULL_0"]["PASS"],
        "target_size_global_onset_passes": target_size_checks["GLOBAL_ONSET_100"]["PASS"],
        "target_size_decisions_match": target_size_checks["NULL_0"]["PASS"] == small_null["PASS"] and target_size_checks["GLOBAL_ONSET_100"]["PASS"] == small_global["PASS"],
        "mutation_guards": all(mutations.values()),
        "target_outputs_absent": not TARGET_OUT.exists() and not TARGET_REPORT.exists(),
    }
    passed = all(gates.values())
    result = {
        "experiment": "SOURCE_NATIVE_OPENING_ONSET_PREFLIGHT",
        "status": "PASS_TARGET_FREE_OPENING_ONSET_PREFLIGHT" if passed else "STOP_OPENING_ONSET_PREFLIGHT",
        "decision": "GO_INDEPENDENTLY_VALIDATE_OPENING_ONSET_PREFLIGHT" if passed else "DO_NOT_OPEN_REAL_OPENING_ONSET_LABELS",
        "inputs": {path.name: sha(path) for path in (*FROZEN, RUNNER)},
        "assignments": 2048,
        "target_size_assignments": 8192,
        "strength": 0.80,
        "records": records,
        "counts": counts,
        "null_label_orbit_sha256": digest(null),
        "target_size_null_label_orbit_sha256": digest(large_null),
        "target_size_checks": target_size_checks,
        "mutations": mutations,
        "gates": gates,
        "target_source_opened": False,
        "real_operation_labels_accessed": 0,
        "real_target_scores_computed": 0,
        "target_outputs_absent": not TARGET_OUT.exists() and not TARGET_REPORT.exists(),
        "english_glosses": 0,
        "claim_ceiling": "Target-free calibration of one held-folio exact-member onset compatibility statistic only; no detachment, allography, morphology, sound, wordhood, syntax, language, cipher, meaning, plaintext, or translation follows.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    OUT_REPORT = "passing" if passed else "stopped"
    REPORT.write_text(f"""# Opening-onset compatibility preflight

Status: **{result['status']}**

At 2,048 assignments the grid yields **{counts['NULL']['passes']}/64** null,
**{counts['GLOBAL_ONSET']['passes']}/8** distributed global-onset,
**{counts['ONE_FOLIO']['passes']}/8** one-folio,
**{counts['FOLIO_RANDOM']['passes']}/8** folio-random, and
**{counts['ONE_BASE']['passes']}/8** one-base passes. The representative null
and global-onset decisions are unchanged at 8,192 assignments. Calibration is
**{OUT_REPORT}**.

No real operation label or target score was opened. Decision:
**{result['decision']}**. This supplies no morphology, meaning, or translation.
""")
    print(json.dumps({"status": result["status"], "decision": result["decision"], "counts": counts, "gates": gates}, sort_keys=True))


if __name__ == "__main__":
    main()
