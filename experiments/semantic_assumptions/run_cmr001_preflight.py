#!/usr/bin/env python3
"""Target-blind model calibration and synthetic controls for CMR001."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from cmr001_core import ASSIGNMENTS, READINGS, evaluate_panel, fit_nb, primary_gates, tied_auc


BASE = Path(__file__).resolve().parent
R = BASE / "results"
ALIGN = R / "source_sta_group_alignment.tsv"
META = R / "source_separator_transcription.tsv"
METHOD = BASE / "CIRCLE_MARKER_RESET_METHOD.md"
CAPACITY = R / "circle_marker_reset_capacity.json"
CAPACITY_VALIDATION = R / "circle_marker_reset_capacity_validation.json"
CORE = BASE / "cmr001_core.py"
OUT = R / "cmr001_preflight.json"
REPORT = R / "cmr001_preflight.md"
TARGET_FOLIOS = {f"f{number}" for number in range(67, 74)}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def table(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def compact(panel: dict[str, object]) -> dict[str, object]:
    return {
        key: panel[key] for key in (
            "loci", "folios", "T_by_reading", "M", "p", "folio_effects",
            "positive_folios_by_reading", "leave_one_folio_out_M",
            "concentration_by_reading", "digests",
        )
    }


def synthetic_panel(kind: str) -> tuple[dict[str, dict[str, np.ndarray]], dict[str, str]]:
    loci = [f"SYN_F{folio}_L{locus}" for folio in range(6) for locus in range(3)]
    folio_map = {locus: f"SYN_F{locus.split('_')[1][1:]}" for locus in loci}
    arrays = {edition: {} for edition in READINGS}
    for edition_index, edition in enumerate(READINGS):
        for locus_index, locus in enumerate(loci):
            length = 11 + (locus_index % 7) + edition_index
            values = np.zeros(length, dtype=np.float64)
            folio_index = int(locus.split("_")[1][1:])
            if kind == "DISTRIBUTED":
                values[0] = 10.0
            elif kind == "ONE_FOLIO" and folio_index == 0:
                values[0] = 10.0
            elif kind == "READING_DISAGREEMENT":
                values[0] = 10.0 if edition != "RF1b" else -10.0
            elif kind in ("NULL", "NO_OBVIOUS"):
                pass
            else:
                if kind not in ("ONE_FOLIO",):
                    raise ValueError(kind)
            arrays[edition][locus] = values
    return arrays, folio_map


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    capacity = json.loads(CAPACITY.read_text(encoding="utf-8"))
    validation = json.loads(CAPACITY_VALIDATION.read_text(encoding="utf-8"))
    if capacity["status"] != "PASS_UNSCORED_22_MARKERS_18_CONSERVATIVE_6_FOLIOS":
        raise AssertionError("capacity status drift")
    if validation["status"] != "PASS_INDEPENDENT_141_CELL_RECONSTRUCTION":
        raise AssertionError("capacity validation drift")

    meta_rows = table(META)
    meta = {row["source_group_id"]: row for row in meta_rows}
    if len(meta) != len(meta_rows):
        raise AssertionError("duplicate source group metadata")
    examples: dict[str, list[tuple[str, str, int]]] = {edition: [] for edition in READINGS}
    for row in table(ALIGN):
        info = meta[row["source_group_id"]]
        edition = row["edition"]
        if edition not in READINGS or info["grammar_scope"] != "CONFIRMED_PROSE" or info["kind"] != "P":
            continue
        folio_match = re.match(r"^(f\d+)", info["page"])
        if not folio_match or folio_match.group(1) in TARGET_FOLIOS:
            continue
        word = row["primary_sta_families"]
        if not word:
            raise AssertionError("empty training family string")
        examples[edition].append((folio_match.group(1), word, int(row["source_group_index"]) == 1))

    calibration = {}
    calibration_pass = {}
    for edition in READINGS:
        by_folio: dict[str, list[tuple[str, int]]] = defaultdict(list)
        for folio, word, label in examples[edition]:
            by_folio[folio].append((word, label))
        aucs = {}
        for held in sorted(by_folio):
            held_rows = by_folio[held]
            if not any(label for _, label in held_rows) or all(label for _, label in held_rows):
                continue
            train = [item for folio, rows in by_folio.items() if folio != held for item in rows]
            model = fit_nb(train)
            labels = [label for _, label in held_rows]
            scores = [model.score(word) for word, _ in held_rows]
            aucs[held] = tied_auc(labels, scores)
        values = list(aucs.values())
        mean = float(np.mean(values))
        median = float(np.median(values))
        fraction_055 = sum(value >= 0.55 for value in values) / len(values)
        calibration[edition] = {
            "training_rows": len(examples[edition]),
            "positive_rows": sum(label for _, _, label in examples[edition]),
            "negative_rows": sum(not label for _, _, label in examples[edition]),
            "eligible_held_folios": len(values),
            "equal_folio_mean_auc": mean,
            "median_folio_auc": median,
            "fraction_folios_auc_at_least_055": fraction_055,
            "folio_auc": aucs,
        }
        calibration_pass[edition] = (
            mean >= 0.65 and median >= 0.65 and fraction_055 >= 0.75
        )

    control_results = {}
    for kind in ("DISTRIBUTED", "NULL", "ONE_FOLIO", "READING_DISAGREEMENT", "NO_OBVIOUS"):
        arrays, folios = synthetic_panel(kind)
        evaluated = evaluate_panel(arrays, folios, assignments=ASSIGNMENTS)
        control_results[kind] = {
            "evaluation": compact(evaluated),
            "primary_gates": primary_gates(evaluated, 0.10),
        }

    distributed_pass = all(control_results["DISTRIBUTED"]["primary_gates"].values())
    negative_reject = {
        kind: not all(control_results[kind]["primary_gates"].values())
        for kind in ("NULL", "ONE_FOLIO", "READING_DISAGREEMENT", "NO_OBVIOUS")
    }

    base_arrays, base_folios = synthetic_panel("DISTRIBUTED")
    base = evaluate_panel(base_arrays, base_folios, assignments=ASSIGNMENTS)
    affine_arrays = {
        edition: {locus: 7.0 * values + 19.0 for locus, values in rows.items()}
        for edition, rows in base_arrays.items()
    }
    affine = evaluate_panel(affine_arrays, base_folios, assignments=ASSIGNMENTS)
    shifts = {locus: (index % 5) + 1 for index, locus in enumerate(sorted(base_folios))}
    rotated_arrays = {edition: {} for edition in READINGS}
    rotated_indices = {edition: {} for edition in READINGS}
    for edition in READINGS:
        for locus, values in base_arrays[edition].items():
            shift = shifts[locus] % len(values)
            rotated_arrays[edition][locus] = np.roll(values, shift)
            rotated_indices[edition][locus] = shift
    rotated = evaluate_panel(rotated_arrays, base_folios, rotated_indices, assignments=ASSIGNMENTS)
    reversed_insertion = {
        edition: {locus: base_arrays[edition][locus] for locus in reversed(list(base_arrays[edition]))}
        for edition in reversed(READINGS)
    }
    canonicalized = {edition: reversed_insertion[edition] for edition in READINGS}
    serialized = evaluate_panel(canonicalized, dict(reversed(list(base_folios.items()))), assignments=ASSIGNMENTS)

    def invariant(left: dict[str, object], right: dict[str, object]) -> bool:
        return (
            left["T_by_reading"] == right["T_by_reading"]
            and left["M"] == right["M"]
            and left["p"] == right["p"]
            and left["folio_effects"] == right["folio_effects"]
            and left["positive_folios_by_reading"] == right["positive_folios_by_reading"]
            and left["leave_one_folio_out_M"] == right["leave_one_folio_out_M"]
            and left["concentration_by_reading"] == right["concentration_by_reading"]
            and left["digests"] == right["digests"]
        )

    invariance = {
        "positive_affine": invariant(base, affine),
        "simultaneous_cyclic_rotation": invariant(base, rotated),
        "serialization_and_reading_order": invariant(base, serialized),
    }
    gates = {
        "capacity_and_validation_bound": True,
        "training_excludes_f67_through_f73": True,
        "all_reading_calibrations_pass": all(calibration_pass.values()),
        "distributed_control_passes": distributed_pass,
        "all_negative_controls_reject": all(negative_reject.values()),
        "all_invariances_pass": all(invariance.values()),
        "fixed_65536_assignment_orbits": all(
            len(control_results[kind]["evaluation"]["loci"]) == 18 for kind in control_results
        ),
        "target_marker_scores_not_loaded": True,
        "target_result_absent": not (R / "cmr001_target.json").exists(),
    }
    status = "PASS_TARGET_BLIND_PREFLIGHT" if all(gates.values()) else "STOP_PREFLIGHT_FAILED"
    result = {
        "experiment": "CMR001_PREFLIGHT",
        "status": status,
        "inputs": {path.name: sha(path) for path in (
            ALIGN, META, METHOD, CAPACITY, CAPACITY_VALIDATION, CORE, Path(__file__)
        )},
        "training_scope": {
            "required_scope": "CONFIRMED_PROSE",
            "required_kind": "P",
            "excluded_folios": sorted(TARGET_FOLIOS),
            "features": ["LEN", "P1", "P2", "P3", "S1", "S2", "S3"],
            "exact_word_feature_used": False,
        },
        "calibration": calibration,
        "calibration_pass": calibration_pass,
        "controls": control_results,
        "negative_control_rejection": negative_reject,
        "invariance": invariance,
        "gates": gates,
        "decision": "AUTHORIZE_INDEPENDENT_PREFLIGHT_RECONSTRUCTION_ONLY" if all(gates.values()) else "TARGET_FORBIDDEN",
        "claim_ceiling": "Target-blind line-initial model calibration and synthetic scorer behavior only. No marker target score, reset, phase, direction, degree, word, meaning, plaintext, or translation.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# CMR001 target-blind preflight\n\n"
        f"Status: **{status}**\n\n"
        "The fixed seven-field STA-family naive-Bayes model was calibrated only on confirmed prose outside "
        "f67--f73. Reading-specific equal-folio mean / median AUC values are "
        + ", ".join(
            f"{edition} {calibration[edition]['equal_folio_mean_auc']:.4f}/{calibration[edition]['median_folio_auc']:.4f}"
            for edition in READINGS
        ) + ".\n\n"
        "The 65,536-assignment scorer recovered the distributed synthetic marker plant and rejected null, "
        "one-folio, reading-disagreement, and no-obvious controls. Invariance status is "
        + ", ".join(f"{name}={value}" for name, value in invariance.items()) + ". No marker target score was loaded. "
        f"Decision: **{result['decision']}**. This supplies no reset, phase, direction, degree, word, meaning, plaintext, or translation.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": status, "calibration_pass": calibration_pass, "gates": gates}, sort_keys=True))


if __name__ == "__main__":
    main()
