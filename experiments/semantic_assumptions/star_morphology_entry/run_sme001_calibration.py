#!/usr/bin/env python3
"""Repeated full-family null and power calibration for SME001."""

from __future__ import annotations

import hashlib
import json
import multiprocessing as mp
import os
from collections import defaultdict
from pathlib import Path

import numpy as np

import run_sme001_anonymous_controls as controls
import sme001_core as core

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OUT = HERE / "sme001_calibration_result.json"
REPORT = ROOT / "experiments/semantic_assumptions/results/sme001_calibration_report.md"
LEVELS = (0.100, 0.149, 0.151, 0.200, 0.300, 0.500)
WORLD_COUNT = 8
NULL_WORLD_COUNT = 64
ROTATION_COUNT = 8192

FIXTURE = None
ROTATIONS_PAGE = None
ROTATIONS_FOLIO = None


def stable_noise(domain: str, world: int, feature: str, edition: str, unit: str) -> float:
    payload = f"{domain}|{world}|{feature}|{edition}|{unit}".encode()
    value = int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")
    return 2.0 * value / ((1 << 64) - 1) - 1.0


def compact(row):
    return {
        key: row[key] for key in (
            "effects", "z", "robust_z", "raw_p", "family_p",
            "material_effect", "ordinal_residual_material_effect",
            "common_folio_support_count", "statistical_gates",
            "statistical_passes",
        )
    }


def row_for(result, target, feature):
    rows = [
        row for row in result["results"]
        if row["target"] == target and row["feature"] == feature
    ]
    if len(rows) != 1:
        raise ValueError("calibration result row mismatch")
    return rows[0]


def evaluate_both(values, features):
    kwargs = {
        "unit_ids": FIXTURE["unit_ids"],
        "pages_by_unit": FIXTURE["pages_by_unit"],
        "folios_by_unit": FIXTURE["folios_by_unit"],
        "ordinals": FIXTURE["ordinals"],
        "values": values,
        "features": features,
        "label_sets": FIXTURE["label_sets"],
        "target_specs": controls.TARGET_SPECS,
        "chunk_size": 2048,
    }
    return (
        core.evaluate(**kwargs, rotations=ROTATIONS_PAGE),
        core.evaluate(**kwargs, rotations=ROTATIONS_FOLIO),
    )


def null_world(world: int):
    features = ["PARA_WORD_COUNT"] + [f"FORMAL_NULL_WORLD_{index:03d}" for index in range(83)]
    values = np.empty((len(FIXTURE["unit_ids"]), len(core.EDITIONS), len(features)))
    for row, unit in enumerate(FIXTURE["unit_ids"]):
        for edition_index, edition in enumerate(core.EDITIONS):
            count_noise = stable_noise("SME001_NULL_WORLD_V1", world, "PARA_WORD_COUNT", edition, unit)
            values[row, edition_index, 0] = 40.0 + int((count_noise + 1.0) * 5.0)
            for feature_index, feature in enumerate(features[1:], 1):
                values[row, edition_index, feature_index] = 0.5 + 0.1 * stable_noise(
                    "SME001_NULL_WORLD_V1", world, feature, edition, unit
                )
    page, folio = evaluate_both(values, features)
    page_pass = {(row["target"], row["feature"]) for row in page["results"] if row["statistical_passes"]}
    folio_pass = {(row["target"], row["feature"]) for row in folio["results"] if row["statistical_passes"]}
    return {
        "kind": "null", "world": world,
        "page_pass_count": len(page_pass), "folio_pass_count": len(folio_pass),
        "joint_passing": [list(value) for value in sorted(page_pass & folio_pass)],
    }


def page_centered_scale(values):
    residual = np.empty_like(values)
    for page in controls.PAGES:
        indices = np.asarray([
            index for index, value in enumerate(FIXTURE["pages_by_unit"])
            if value == page
        ])
        residual[indices] = values[indices] - values[indices].mean(axis=0, keepdims=True)
    return np.sqrt(np.mean(residual * residual, axis=0))


def raw_effect(labels, values, low, high):
    page_effects = {}
    for page in controls.PAGES:
        indices = np.asarray([
            index for index, value in enumerate(FIXTURE["pages_by_unit"])
            if value == page
        ])
        page_labels = np.asarray([labels[index] for index in indices])
        if low not in page_labels or high not in page_labels:
            continue
        page_effects[page] = (
            values[indices[page_labels == high]].mean(axis=0)
            - values[indices[page_labels == low]].mean(axis=0)
        )
    folio_effects = defaultdict(list)
    for page, effect in page_effects.items():
        folio_effects[page[:-1]].append(effect)
    return np.mean([
        np.mean(folio_effects[folio], axis=0) for folio in sorted(folio_effects)
    ], axis=0)


def physical_material(labels, values, low, high):
    effect = raw_effect(labels, values, low, high)
    scale = page_centered_scale(values)
    return float(np.min(np.abs(effect) / scale))


def centered_signal_noise(world: int, target: str):
    labels = FIXTURE["label_sets"][target]
    values = np.empty((len(FIXTURE["unit_ids"]), len(core.EDITIONS)))
    for row, unit in enumerate(FIXTURE["unit_ids"]):
        for edition_index, edition in enumerate(core.EDITIONS):
            values[row, edition_index] = stable_noise(
                "SME001_POWER_GRID_V1", world, target, edition, unit
            )
    low, high = controls.TARGET_SPECS[target]
    for page in controls.PAGES:
        indices = [
            index for index, value in enumerate(FIXTURE["pages_by_unit"])
            if value == page
        ]
        for edition_index in range(len(core.EDITIONS)):
            for label in (low, high):
                group = [index for index in indices if labels[index] == label]
                if group:
                    values[group, edition_index] -= values[group, edition_index].mean()
    return values


def calibrated_signal(world: int, target: str, requested: float):
    labels = FIXTURE["label_sets"][target]
    low, high = controls.TARGET_SPECS[target]
    score = np.asarray([
        -1.0 if label == low else 1.0 if label == high else 0.0
        for label in labels
    ])
    base = centered_signal_noise(world, target)
    lower, upper = 0.0, 10.0
    for _ in range(80):
        middle = (lower + upper) / 2.0
        material = physical_material(labels, base + middle * score[:, None], low, high)
        if material < requested:
            lower = middle
        else:
            upper = middle
    values = base + upper * score[:, None]
    material = physical_material(labels, values, low, high)
    if abs(material - requested) > 1e-6:
        raise ValueError("power-grid bisection failed")
    return values, upper, material


def power_world(task):
    target, world, requested = task
    features = ["PARA_WORD_COUNT", "FORMAL_GRID_SIGNAL"] + [
        f"FORMAL_GRID_NULL_{index:03d}" for index in range(82)
    ]
    values = np.empty((len(FIXTURE["unit_ids"]), len(core.EDITIONS), len(features)))
    signal, amplitude, calibrated_material = calibrated_signal(world, target, requested)
    values[:, :, 1] = signal
    for row, unit in enumerate(FIXTURE["unit_ids"]):
        for edition_index, edition in enumerate(core.EDITIONS):
            count_noise = stable_noise("SME001_POWER_GRID_NULL_V1", world, "PARA_WORD_COUNT", edition, unit)
            values[row, edition_index, 0] = 40.0 + int((count_noise + 1.0) * 5.0)
            for feature_index, feature in enumerate(features[2:], 2):
                values[row, edition_index, feature_index] = 0.5 + 0.1 * stable_noise(
                    "SME001_POWER_GRID_NULL_V1", world, feature, edition, unit
                )
    page, folio = evaluate_both(values, features)
    page_row = row_for(page, target, "FORMAL_GRID_SIGNAL")
    folio_row = row_for(folio, target, "FORMAL_GRID_SIGNAL")
    return {
        "kind": "power", "target": target, "world": world,
        "requested_material": requested, "calibrated_material": calibrated_material,
        "amplitude": amplitude, "page": compact(page_row), "folio": compact(folio_row),
        "joint_pass": bool(page_row["statistical_passes"] and folio_row["statistical_passes"]),
    }


def worker(task):
    if task[0] == "null":
        return null_world(task[1])
    return power_world(task[1:])


def main() -> None:
    global FIXTURE, ROTATIONS_PAGE, ROTATIONS_FOLIO
    FIXTURE = controls.build_fixture()
    lengths = {page: 12 for page in controls.PAGES}
    page_folio = {page: page[:-1] for page in controls.PAGES}
    ROTATIONS_PAGE = core.make_rotations(controls.PAGES, lengths, ROTATION_COUNT)
    ROTATIONS_FOLIO = core.make_folio_phase_rotations(
        controls.PAGES, lengths, page_folio, ROTATION_COUNT
    )
    tasks = [("null", world) for world in range(NULL_WORLD_COUNT)]
    tasks += [
        ("power", target, world, level)
        for target in controls.TARGET_SPECS
        for world in range(WORLD_COUNT)
        for level in LEVELS
    ]
    workers = min(32, os.cpu_count() or 1)
    with mp.get_context("fork").Pool(processes=workers) as pool:
        results = list(pool.imap_unordered(worker, tasks, chunksize=1))

    null_worlds = sorted(
        (row for row in results if row["kind"] == "null"),
        key=lambda row: row["world"],
    )
    power_worlds = sorted(
        (row for row in results if row["kind"] == "power"),
        key=lambda row: (row["target"], row["world"], row["requested_material"]),
    )
    null_joint_worlds = [row["world"] for row in null_worlds if row["joint_passing"]]
    pass_counts = {}
    for target in controls.TARGET_SPECS:
        pass_counts[target] = {
            f"{level:.3f}": sum(
                row["joint_pass"] for row in power_worlds
                if row["target"] == target and row["requested_material"] == level
            ) for level in LEVELS
        }

    checks = {
        "world_counts": len(null_worlds) == 64 and len(power_worlds) == 96,
        "full_family": all(
            not row["joint_passing"] or all(len(pair) == 2 for pair in row["joint_passing"])
            for row in null_worlds
        ),
        "null_world_acceptance": len(null_joint_worlds) <= 8,
        "material_bisection": all(
            abs(row["calibrated_material"] - row["requested_material"]) <= 1e-6
            for row in power_worlds
        ),
        "below_boundary_zero_pass": all(
            not row["joint_pass"] for row in power_worlds
            if row["requested_material"] < 0.15
        ),
        "nondecreasing_ray_power": all(
            pass_counts["RAY_8_MINUS_7"][f"{left:.3f}"]
            <= pass_counts["RAY_8_MINUS_7"][f"{right:.3f}"]
            for left, right in zip(LEVELS, LEVELS[1:])
        ),
        "nondecreasing_tail_power": all(
            pass_counts["TAIL_2_MINUS_1"][f"{left:.3f}"]
            <= pass_counts["TAIL_2_MINUS_1"][f"{right:.3f}"]
            for left, right in zip(LEVELS, LEVELS[1:])
        ),
        "ray_high_power": pass_counts["RAY_8_MINUS_7"]["0.500"] >= 7,
        "tail_high_power": pass_counts["TAIL_2_MINUS_1"]["0.500"] >= 6,
        "target_artifacts_absent": all(not path.exists() for path in controls.TARGET_ARTIFACTS),
        "frozen_target_hashes": all(
            hashlib.sha256((HERE / name).read_bytes()).hexdigest() == expected
            for name, expected in controls.EXPECTED_HASHES.items()
        ),
    }
    failures = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "experiment": "SME001",
        "status": "PASS_TARGET_FREE_NULL_AND_POWER_CALIBRATION" if not failures else "FAIL_TARGET_FREE_NULL_AND_POWER_CALIBRATION",
        "target_join_performed": False,
        "target_files_parsed": False,
        "workers": workers,
        "rotation_count_per_ensemble": ROTATION_COUNT,
        "page_rotation_digest": core.rotation_digest(ROTATIONS_PAGE),
        "folio_rotation_digest": core.rotation_digest(ROTATIONS_FOLIO),
        "null_world_count": len(null_worlds),
        "null_worlds_with_joint_pass": null_joint_worlds,
        "power_worlds_per_level": WORLD_COUNT,
        "levels": list(LEVELS),
        "joint_pass_counts": pass_counts,
        "checks": checks,
        "failures": failures,
        "null_worlds": null_worlds,
        "power_worlds": power_worlds,
        "claim_ceiling": "synthetic familywise and power diagnostics only; no manuscript association or meaning",
    }
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text("\n".join([
        "# SME001 target-free null and power calibration", "", "## Decision", "",
        ("**PASS — repeated full-family null and power calibration passed; the real target remains unjoined.**"
         if not failures else f"**FAIL — {len(failures)} calibration gates failed; target access remains forbidden.**"),
        "", f"Using {workers} CPU workers, the registered engine scored 64 complete 84-feature null worlds and 96 target/strength worlds under both 8,192-assignment phase ensembles. {len(null_joint_worlds)}/64 null worlds contained any joint passing pair.",
        "", "Joint signal pass counts by requested material level:", "",
        f"- ray: {pass_counts['RAY_8_MINUS_7']}",
        f"- tail: {pass_counts['TAIL_2_MINUS_1']}",
        "", ("Failures: none." if not failures else "Failures: " + ", ".join(failures) + "."),
        "", "This calibration measures only synthetic error and power behavior. It supplies no manuscript association, function, meaning, lexeme, plaintext, language, or translation.",
        "", "## Reproduction", "", "```bash",
        "OPENBLAS_NUM_THREADS=1 ./vpy experiments/semantic_assumptions/star_morphology_entry/run_sme001_calibration.py",
        "```",
    ]) + "\n", encoding="utf-8")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
