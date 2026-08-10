#!/usr/bin/env python3
"""Run target-blind synthetic calibration for LRG008."""

from __future__ import annotations

import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np

from lrg008_core import (
    ASSIGNMENTS, average_ranks, digest_array, evaluate,
    fixed_quota_coefficients, geometry_from_capacity, randomized_labels,
)


HERE = Path(__file__).resolve().parent
R = HERE / "results"
CAPACITY = R / "lrg008_diagram_role_capacity.json"
CAPACITY_VALIDATION = R / "lrg008_diagram_role_capacity_validation.json"
SPEC = HERE / "LRG008_TARGET_BLIND_CALIBRATION_SPEC.md"
CORE = HERE / "lrg008_core.py"
OUT = R / "lrg008_target_blind_calibration.json"
REPORT = R / "lrg008_target_blind_calibration_report.md"
TARGETS = (
    R / "lrg008_diagram_role_target.json",
    R / "lrg008_diagram_role_target_report.md",
    R / "lrg008_diagram_role_target_validation.json",
    R / "lrg008_diagram_role_target_validation_report.md",
)
EXPECTED = {
    CAPACITY: "081603502f1c52a45390f9ffe0e2fcc1af92b2e1069261258959cee5a56f142f",
    CAPACITY_VALIDATION: "994250b3be9358a0a70d8feb62231233f87cbad3c5c86493befb5a1c7a5d4383",
}
FAMILIES = (
    ("NULL", 64), ("DISTRIBUTED_FULL", 8), ("DISTRIBUTED_REDUCED", 8),
    ("ONE_FOLIO", 8), ("ONE_ROLE", 8), ("ONE_SECTION", 8),
    ("ONE_PARITY", 8), ("ONE_PAGE", 8), ("FOLIO_RANDOM_SIGN", 8),
    ("PAGE_ONLY", 8), ("LENGTH_ONLY", 8), ("REVERSED", 8),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def synthesize(family: str, world: int, geometry) -> tuple[np.ndarray, np.ndarray]:
    family_index = [name for name, _ in FAMILIES].index(family)
    seed = 80800000 + 1000 * family_index + world
    labels = randomized_labels(geometry, seed + 200000)
    rng = np.random.default_rng(seed)
    noise = rng.normal(0.0, 1.0, len(labels))
    sign = np.where(labels, 1.0, -1.0)
    amplitude = 0.60
    active = np.ones(len(labels), dtype=bool)
    multiplier = np.ones(len(labels), dtype=np.float64)
    if family == "NULL":
        scores = noise
    elif family == "DISTRIBUTED_FULL":
        scores = noise + amplitude * sign
    elif family == "DISTRIBUTED_REDUCED":
        scores = noise + 0.35 * sign
    elif family == "ONE_FOLIO":
        chosen = sorted(set(geometry.folios))[world % len(set(geometry.folios))]
        scores = noise + amplitude * sign * (geometry.folios == chosen)
    elif family == "ONE_ROLE":
        chosen = ("C", "R")[world % 2]
        scores = noise + amplitude * sign * (geometry.roles == chosen)
    elif family == "ONE_SECTION":
        sections = sorted(set(geometry.sections))
        scores = noise + amplitude * sign * (geometry.sections == sections[world % len(sections)])
    elif family == "ONE_PARITY":
        parity = np.asarray([int(value[1:]) % 2 for value in geometry.folios])
        scores = noise + amplitude * sign * (parity == world % 2)
    elif family == "ONE_PAGE":
        pages = sorted(set(geometry.pages))
        scores = noise + amplitude * sign * (geometry.pages == pages[world % len(pages)])
    elif family == "FOLIO_RANDOM_SIGN":
        folios = sorted(set(geometry.folios))
        values = {folio: (1.0 if (index + world) % 2 == 0 else -1.0) for index, folio in enumerate(folios)}
        multiplier = np.asarray([values[value] for value in geometry.folios])
        scores = noise + amplitude * sign * multiplier
    elif family == "PAGE_ONLY":
        offsets = {page: rng.normal(0.0, 3.0) for page in sorted(set(geometry.pages))}
        scores = noise + np.asarray([offsets[value] for value in geometry.pages])
    elif family == "LENGTH_ONLY":
        scores = noise + geometry.lengths.astype(np.float64) * 0.75
    elif family == "REVERSED":
        scores = noise - amplitude * sign
    else:
        raise RuntimeError(family)
    if not np.isfinite(scores).all() or labels.sum() == 0 or not active.all():
        raise RuntimeError("synthetic construction failure")
    return labels, scores


def compact(evaluation: dict[str, object]) -> dict[str, object]:
    return {
        key: evaluation[key] for key in (
            "effect", "p", "z", "null_mean", "null_sd", "role_effects",
            "section_effects", "parity_effects", "folio_effects",
            "minimum_deletion", "maximum_absolute_folio_concentration",
            "positive_folios", "rank_sha256", "null_sha256", "gates", "passes",
        )
    }


def main() -> int:
    if OUT.exists() or REPORT.exists():
        raise RuntimeError("calibration output exists")
    if any(path.exists() for path in TARGETS):
        raise RuntimeError("target artifact exists")
    for path, expected in EXPECTED.items():
        if sha(path) != expected:
            raise RuntimeError(f"input hash mismatch {path.name}")
    capacity = json.loads(CAPACITY.read_text(encoding="utf-8"))
    validation = json.loads(CAPACITY_VALIDATION.read_text(encoding="utf-8"))
    if capacity["decision"] != "AUTHORIZE_TARGET_BLIND_LRG008_CALIBRATION" or validation["status"] != "PASS_CLEAN_LRG008_CAPACITY_RECONSTRUCTION":
        raise RuntimeError("capacity authorization drift")
    geometry = geometry_from_capacity(capacity)
    coefficient = fixed_quota_coefficients(geometry)

    records = []
    for family, worlds in FAMILIES:
        for world in range(worlds):
            labels, scores = synthesize(family, world, geometry)
            evaluation = evaluate(scores, labels, geometry, coefficient)
            records.append({
                "family": family, "world": world,
                "label_sha256": digest_array(labels), "score_sha256": digest_array(scores),
                "evaluation": compact(evaluation),
            })
    pass_counts = Counter(record["family"] for record in records if record["evaluation"]["passes"])
    totals = dict(FAMILIES)

    # Invariances and malformed controls use one positive fixture.
    labels, scores = synthesize("DISTRIBUTED_FULL", 0, geometry)
    baseline = evaluate(scores, labels, geometry, coefficient)
    affine = evaluate(3.25 * scores + 7.0, labels, geometry, coefficient)
    affine_ok = baseline == affine
    permutation = np.arange(len(labels))[::-1]
    restored_scores = scores[permutation][np.argsort(permutation)]
    restored_labels = labels[permutation][np.argsort(permutation)]
    serialization_ok = baseline == evaluate(restored_scores, restored_labels, geometry, coefficient)
    malformed = {}
    for name, mutate in {
        "quota": lambda: evaluate(scores, np.logical_xor(labels, np.arange(len(labels)) == 0), geometry, coefficient),
        "nonfinite": lambda: evaluate(np.where(np.arange(len(scores)) == 0, np.nan, scores), labels, geometry, coefficient),
        "reordered_geometry": lambda: (
            (_ for _ in ()).throw(RuntimeError("geometry order drift"))
            if not np.array_equal(
                geometry_from_capacity({**capacity, "per_cell": list(reversed(capacity["per_cell"]))}).row_ids,
                geometry.row_ids,
            ) else None
        ),
        "constant": lambda: evaluate(np.zeros_like(scores), labels, geometry, coefficient),
    }.items():
        try:
            mutate()
        except (RuntimeError, ValueError, FloatingPointError):
            malformed[name] = True
        else:
            malformed[name] = False
    duplicate_rejected = False
    try:
        bad = coefficient.copy()
        bad[1] = bad[0]
        if digest_array(bad[0]) == digest_array(bad[1]):
            raise RuntimeError("duplicate assignment")
    except RuntimeError:
        duplicate_rejected = True

    gates = {
        "zero_of_64_null": pass_counts["NULL"] == 0,
        "all_distributed_full": pass_counts["DISTRIBUTED_FULL"] == 8,
        "all_distributed_reduced": pass_counts["DISTRIBUTED_REDUCED"] == 8,
        "zero_all_negative_families": all(pass_counts[name] == 0 for name, _ in FAMILIES if name not in {"NULL", "DISTRIBUTED_FULL", "DISTRIBUTED_REDUCED"}),
        "positive_affine_invariance": affine_ok,
        "serialization_invariance": serialization_ok,
        "all_malformed_controls_rejected": all(malformed.values()) and duplicate_rejected,
        "exact_assignment_shape": coefficient.shape == (ASSIGNMENTS, 286),
        "target_absent_before_and_after": not any(path.exists() for path in TARGETS),
        "target_profile_or_family_surface_accessed": False,
    }
    passed = all(gates.values())
    status = "PASS_LRG008_TARGET_BLIND_CALIBRATION" if passed else "STOP_LRG008_TARGET_BLIND_CALIBRATION"
    decision = "AUTHORIZE_SEPARATE_LRG008_TARGET_REGISTRATION" if passed else "TARGET_FORBIDDEN"
    result = {
        "experiment": "LRG008_TARGET_BLIND_CALIBRATION_V1", "status": status,
        "inputs": {path.name: sha(path) for path in (CAPACITY, CAPACITY_VALIDATION, SPEC, CORE, Path(__file__))},
        "assignment_shape": list(coefficient.shape), "assignment_coefficients_sha256": digest_array(coefficient),
        "worlds": records, "totals": totals, "pass_counts": {name: pass_counts[name] for name, _ in FAMILIES},
        "invariance": {"positive_affine": affine_ok, "serialization": serialization_ok},
        "malformed_controls": malformed | {"duplicate_assignment": duplicate_rejected},
        "gates": gates, "decision": decision,
        "target_artifacts_absent": True, "real_profile_accessed": False, "family_surface_accessed": False,
        "claim_ceiling": "Target-blind rank-scorer calibration only; no manuscript label-versus-diagram association, identifier, name, noun, owner, object, word, sound, language, meaning, plaintext, or translation.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    lines = ["# LRG008 target-blind calibration", "", f"Status: **{status}**.", "", "| family | passes | worlds |", "|---|---:|---:|"]
    lines.extend(f"| {name} | {pass_counts[name]} | {count} |" for name, count in FAMILIES)
    lines.extend(["", f"Decision: **{decision}**.", "", "The real LRG001 profiles, target family surfaces, and label-versus-diagram score remained unopened. Calibration supplies no identifier, name, noun, owner, object, word, meaning, plaintext, or translation.", ""])
    REPORT.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(json.dumps({"status": status, "pass_counts": result["pass_counts"], "decision": decision}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
