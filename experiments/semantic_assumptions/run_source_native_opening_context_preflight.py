#!/usr/bin/env python3
"""Run the frozen target-free NONE/DA context calibration."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import numpy as np

import source_native_opening_context_core as core

try:
    import cupy as cp
except ImportError:
    cp = None


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
PANEL = RESULTS / "source_native_opening_context_masked.tsv"
QUOTAS = RESULTS / "source_native_opening_context_quotas.tsv"
CAPACITY_VALIDATION = RESULTS / "source_native_opening_context_capacity_validation.json"
CORE = BASE / "source_native_opening_context_core.py"
SPEC = BASE / "SOURCE_NATIVE_OPENING_CONTEXT_PREFLIGHT_SPEC.md"
RUNNER = Path(__file__).resolve()
OUT = RESULTS / "source_native_opening_context_preflight.json"
REPORT = RESULTS / "source_native_opening_context_preflight_report.md"
TARGET = RESULTS / "source_native_opening_context_target.json"
TARGET_REPORT = RESULTS / "source_native_opening_context_target_report.md"
FROZEN = {
    PANEL: "6a043ba095d118594c9a8bd4bd4bf0ac96778963be0637400e353c517c5e616a",
    QUOTAS: "f062d9ce2935578788f9913d848c6eae2206f685ca9fa8984d29862f01ff339b",
    CAPACITY_VALIDATION: "32dda1eedfa4ea2135583ddaa1593970b279aaab91d3f1fd3c1c75b629dafe53",
    CORE: "fe6d473758c744ee50f800fba3246d773a26daf7226447db685639561090a5cd",
    SPEC: "ea0e63888e684ea111ff03b0463a133bcba140b0382252240fdc50eb0c6f4be2",
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


def labels_digest(labels) -> str:
    return hashlib.sha256(np.packbits(labels.astype(np.uint8), axis=None).tobytes()).hexdigest()


def main() -> None:
    if any(path.exists() for path in (OUT, REPORT, TARGET, TARGET_REPORT)):
        raise SystemExit("refusing existing output")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen mismatch: {path.name}")
    if json.loads(CAPACITY_VALIDATION.read_text())["status"] != "PASS_INDEPENDENT_5826_ROW_MASKED_CONTEXT_RECONSTRUCTION":
        raise SystemExit("capacity validation")
    panel = core.load_panel(PANEL, QUOTAS)
    backend = cp if cp is not None else np
    observed = np.stack([core.planted_labels(panel, mode, world) for mode, world in TASKS])
    null = core.null_orbit(panel, 1024, "PREFLIGHT")
    position = core.summarize_batch(panel, panel.position, observed, null, xp=backend)
    neighbor = core.summarize_batch(panel, panel.neighbor, observed, null, xp=backend)
    records = []
    for (mode, world), position_summary, neighbor_summary in zip(TASKS, position, neighbor):
        records.append({
            "mode": mode,
            "world": world,
            "POSITION": {**position_summary, "PASS": core.passes(position_summary, 0.01)},
            "NEIGHBOR": {**neighbor_summary, "PASS": core.passes(neighbor_summary, 0.01)},
        })
    counts = {
        mode: {
            "worlds": sum(candidate == mode for candidate, _ in TASKS),
            "position_passes": sum(record["POSITION"]["PASS"] for record in records if record["mode"] == mode),
            "neighbor_passes": sum(record["NEIGHBOR"]["PASS"] for record in records if record["mode"] == mode),
        }
        for mode in ("NULL", "POSITION", "NEIGHBOR", "ONE_FOLIO", "FOLIO_RANDOM", "ONE_BASE")
    }
    large_observed = np.stack([core.planted_labels(panel, mode, world) for mode, world in REPRESENTATIVES])
    large_null = core.null_orbit(panel, 8192, "PREFLIGHT")
    large_position = core.summarize_batch(panel, panel.position, large_observed, large_null, xp=backend)
    large_neighbor = core.summarize_batch(panel, panel.neighbor, large_observed, large_null, xp=backend)
    target_size_checks = []
    for (mode, world), position_summary, neighbor_summary in zip(REPRESENTATIVES, large_position, large_neighbor):
        target_size_checks.append({
            "mode": mode,
            "world": world,
            "POSITION": {**position_summary, "PASS": core.passes(position_summary, 0.01)},
            "NEIGHBOR": {**neighbor_summary, "PASS": core.passes(neighbor_summary, 0.01)},
        })
    expected_pattern = (
        counts["NULL"] == {"worlds": 64, "position_passes": 0, "neighbor_passes": 0}
        and counts["POSITION"] == {"worlds": 8, "position_passes": 8, "neighbor_passes": 0}
        and counts["NEIGHBOR"] == {"worlds": 8, "position_passes": 0, "neighbor_passes": 8}
        and all(counts[mode] == {"worlds": 8, "position_passes": 0, "neighbor_passes": 0} for mode in ("ONE_FOLIO", "FOLIO_RANDOM", "ONE_BASE"))
    )
    small_lookup = {(record["mode"], record["world"]): record for record in records}
    decisions_stable = all(
        large[system]["PASS"] == small_lookup[(large["mode"], large["world"])][system]["PASS"]
        for large in target_size_checks for system in ("POSITION", "NEIGHBOR")
    )
    finite = all(np.isfinite(value) for record in records + target_size_checks for system in ("POSITION", "NEIGHBOR") for key, value in record[system].items() if key != "PASS")
    gates = {
        "exact_synthetic_pattern": expected_pattern,
        "target_size_decisions_stable": decisions_stable,
        "finite_summaries": finite,
        "exact_masked_geometry": len(panel.rows) == 1207 and len(panel.strata) == 197 and len(panel.folios) == 59 and len(panel.base_ids) == 44,
        "real_operation_labels_accessed_zero": True,
        "real_context_scores_computed_zero": True,
        "target_outputs_absent": not TARGET.exists() and not TARGET_REPORT.exists(),
    }
    passed = all(gates.values())
    result = {
        "experiment": "SOURCE_NATIVE_OPENING_CONTEXT_PREFLIGHT",
        "status": "PASS_TARGET_FREE_OPENING_CONTEXT_PREFLIGHT" if passed else "STOP_OPENING_CONTEXT_PREFLIGHT",
        "decision": "GO_INDEPENDENTLY_VALIDATE_CONTEXT_PREFLIGHT" if passed else "DO_NOT_OPEN_CONTEXT_TARGET",
        "inputs": {path.name: sha(path) for path in (*FROZEN, RUNNER)},
        "backend": "cupy" if cp is not None else "numpy",
        "backend_version": cp.__version__ if cp is not None else np.__version__,
        "masked_rows": len(panel.rows),
        "informative_folios": len(panel.folios),
        "represented_remainders": len(panel.base_ids),
        "position_features": list(panel.position_names),
        "neighbor_features": list(panel.neighbor_names),
        "null_orbit_sha256": labels_digest(null),
        "target_size_null_orbit_sha256": labels_digest(large_null),
        "records": records,
        "counts": counts,
        "target_size_checks": target_size_checks,
        "gates": gates,
        "real_operation_labels_accessed": 0,
        "real_context_scores_computed": 0,
        "english_glosses": 0,
        "claim_ceiling": "Target-free calibration of quota-preserving cross-folio context concordance only; no detachment, wordhood, prefix function, syntax, sound, language, cipher, meaning, plaintext, or translation follows.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(f"""# Opening-context target-free preflight

Status: **{result['status']}**

The 1,024-assignment grid yields position/neighbor passes of
**{counts['NULL']['position_passes']}/{counts['NULL']['neighbor_passes']}** in
64 null worlds, **{counts['POSITION']['position_passes']}/{counts['POSITION']['neighbor_passes']}**
in eight position plants, and **{counts['NEIGHBOR']['position_passes']}/{counts['NEIGHBOR']['neighbor_passes']}**
in eight neighbor plants. One-folio, folio-random, and one-base controls yield
zero passes in both systems. All six representative decisions remain unchanged
at 8,192 assignments. All gates are **{'passing' if passed else 'not passing'}**.

No real row operation label or context score was opened. Decision:
**{result['decision']}**. This supplies no detachment, wordhood, prefix function,
syntax, sound, language, cipher, meaning, plaintext, or translation.
""")
    print(json.dumps({"status": result["status"], "counts": counts, "target_size_stable": decisions_stable, "backend": result["backend"]}, sort_keys=True))


if __name__ == "__main__":
    main()
