#!/usr/bin/env python3
"""One-shot frozen manuscript score for CMR001."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

import numpy as np

from cmr001_core import READINGS, array_sha, evaluate_panel, fit_nb, primary_gates


BASE = Path(__file__).resolve().parent
R = BASE / "results"
FREEZE = BASE / "CMR001_TARGET_FREEZE.json"
ALIGN = R / "source_sta_group_alignment.tsv"
META = R / "source_separator_transcription.tsv"
CAPACITY = R / "circle_marker_reset_capacity.json"
PREFLIGHT = R / "cmr001_preflight.json"
PREFLIGHT_VALIDATION = R / "cmr001_preflight_validation.json"
OUT = R / "cmr001_target.json"
REPORT = R / "cmr001_target.md"
VALIDATION_OUT = R / "cmr001_target_validation.json"
VALIDATION_REPORT = R / "cmr001_target_validation.md"
TARGET_FOLIOS = {f"f{number}" for number in range(67, 74)}
FROZEN_FILES = (
    "CIRCLE_MARKER_RESET_METHOD.md",
    "SOURCE_SEPARATOR_TRANSCRIPTION_SPEC.md",
    "SOURCE_STA_ALIGNMENT_SPEC.md",
    "audit_public_circle_seam_coordinates.py",
    "validate_public_circle_seam_coordinates.py",
    "audit_circle_marker_reset_capacity.py",
    "validate_circle_marker_reset_capacity.py",
    "build_source_separator_transcription.py",
    "validate_source_separator_transcription.py",
    "build_source_sta_alignment.py",
    "validate_source_sta_alignment.py",
    "cmr001_core.py",
    "run_cmr001_preflight.py",
    "validate_cmr001_preflight.py",
    "run_cmr001_target.py",
    "validate_cmr001_target.py",
    "results/public_voynich_nu_page_annotations_v2.tsv",
    "results/public_circle_seam_coordinate_audit.tsv",
    "results/public_circle_seam_coordinate_audit.json",
    "results/public_circle_seam_coordinate_audit.md",
    "results/public_circle_seam_coordinate_audit_validation.json",
    "results/public_circle_seam_coordinate_audit_validation.md",
    "results/source_separator_transcription.tsv",
    "results/source_separator_transcription.json",
    "results/source_separator_transcription_report.md",
    "results/source_separator_transcription_validation.json",
    "results/source_separator_transcription_validation_report.md",
    "results/source_sta_group_alignment.tsv",
    "results/source_sta_group_alignment.json",
    "results/source_sta_group_alignment_report.md",
    "results/source_sta_group_alignment_validation.json",
    "results/source_sta_group_alignment_validation_report.md",
    "results/circle_marker_reset_capacity.json",
    "results/circle_marker_reset_capacity.md",
    "results/circle_marker_reset_capacity_validation.json",
    "results/circle_marker_reset_capacity_validation.md",
    "results/cmr001_preflight_attempt1.json",
    "results/cmr001_preflight_attempt1.md",
    "results/cmr001_preflight.json",
    "results/cmr001_preflight.md",
    "results/cmr001_preflight_validation.json",
    "results/cmr001_preflight_validation.md",
    "results/pre_grounding_interlinear.tsv",
    "../../transcription/sources/ZL3b-n.txt",
    "../../transcription/sources/IT2a-n.txt",
    "../../transcription/sources/RF1b-e.txt",
    "../../transcription/sources/Stolfi_text25e1-52.evt",
    "../../transcription/sources/sta/ZL3b.txt",
    "../../transcription/sources/sta/IT2a.txt",
    "../../transcription/sources/sta/RF1b.txt",
    "../../transcription/sources/sta/STA-Eva_def.bit",
    "../../transcription/sources/sta/STA-EvaT_def.bit",
    "../../transcription/sources/sta/STA-Eva_Bint.bit",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def table(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def verify_freeze() -> dict[str, object]:
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    if freeze.get("experiment") != "CMR001_TARGET_FREEZE" or freeze.get("status") != "FROZEN_TARGET_UNOPENED":
        raise AssertionError("invalid freeze status")
    expected_absent = {
        "results/cmr001_target.json",
        "results/cmr001_target.md",
        "results/cmr001_target_validation.json",
        "results/cmr001_target_validation.md",
    }
    if set(freeze.get("required_absent_outputs", [])) != expected_absent:
        raise AssertionError("freeze output set drift")
    if set(freeze.get("frozen_files", {})) != set(FROZEN_FILES):
        raise AssertionError("freeze file allowlist drift")
    for relative, expected in freeze.get("frozen_files", {}).items():
        path = BASE / relative
        if not path.is_file() or sha(path) != expected:
            raise AssertionError(f"frozen file drift: {relative}")
    if any((BASE / relative).exists() for relative in expected_absent):
        raise SystemExit("target or validation artifact already exists")
    return freeze


def compact(panel: dict[str, object], score_arrays: dict[str, dict[str, np.ndarray]]) -> dict[str, object]:
    payload = {
        key: panel[key] for key in (
            "loci", "folios", "T_by_reading", "M", "p", "folio_effects",
            "positive_folios_by_reading", "leave_one_folio_out_M",
            "concentration_by_reading", "digests",
        )
    }
    loci = payload["loci"]
    payload["digests"] = dict(payload["digests"])
    payload["digests"].update({
        "score_arrays_sha256": hashlib.sha256("".join(
            array_sha(score_arrays[edition][locus]) for edition in READINGS for locus in loci
        ).encode("ascii")).hexdigest(),
        "folio_effects_sha256": canonical_sha(payload["folio_effects"]),
    })
    payload["digests"]["compact_evaluation_sha256"] = canonical_sha({
        key: value for key, value in payload.items() if key != "digests"
    })
    return payload


def panel_arrays(
    loci: list[str],
    aligned: dict[tuple[str, str], list[dict[str, str]]],
    models: dict[str, object],
) -> dict[str, dict[str, np.ndarray]]:
    arrays: dict[str, dict[str, np.ndarray]] = {edition: {} for edition in READINGS}
    for edition in READINGS:
        for locus in loci:
            rows = aligned[(edition, locus)]
            arrays[edition][locus] = np.asarray(
                [models[edition].score(row["primary_sta_families"]) for row in rows],
                dtype=np.float64,
            )
    return arrays


def report_text(result: dict[str, object]) -> str:
    all_panel = result["panels"]["all_markers"]
    conservative = result["panels"]["conservative_markers"]
    negative = result["panels"]["no_obvious_start"]
    return (
        "# CMR001 drawn circle-marker reset result\n\n"
        f"Status: **{result['status']}**\n\n"
        "The frozen line-initial-likeness test scored the 22 public drawn-marker seams once. "
        f"The weakest-reading statistic is M={all_panel['M']:.6f} with exact synchronized-phase "
        f"p={all_panel['p']:.6f}; reading statistics are "
        + ", ".join(f"{edition} {all_panel['T_by_reading'][edition]:.6f}" for edition in READINGS)
        + ". The 18-marker conservative panel has "
        f"M={conservative['M']:.6f}, p={conservative['p']:.6f}. The disjoint 25-locus "
        f"no-obvious-start panel has M={negative['M']:.6f}, p={negative['p']:.6f}; the "
        f"registered marker-minus-negative contrast is {result['marker_minus_no_obvious_M']:.6f}.\n\n"
        f"The frozen statistical gates {'PASS' if result['statistical_gates_pass'] else 'DO NOT PASS'}. "
        "This result is provisional until a nonimporting implementation reconstructs every score, "
        "orbit, digest, and gate. Even a validated pass establishes only aggregate local "
        "line-initial-like selection at human-described drawn seams. It establishes no global start, "
        "direction, degree, number, word, meaning, plaintext, or translation.\n"
    )


def main() -> None:
    freeze = verify_freeze()
    capacity = json.loads(CAPACITY.read_text(encoding="utf-8"))
    preflight = json.loads(PREFLIGHT.read_text(encoding="utf-8"))
    preflight_validation = json.loads(PREFLIGHT_VALIDATION.read_text(encoding="utf-8"))
    if capacity["status"] != "PASS_UNSCORED_22_MARKERS_18_CONSERVATIVE_6_FOLIOS":
        raise AssertionError("capacity drift")
    if preflight["status"] != "PASS_TARGET_BLIND_PREFLIGHT":
        raise AssertionError("preflight drift")
    if preflight_validation["status"] != "PASS_INDEPENDENT_CALIBRATION_AND_5_CONTROL_RECONSTRUCTION":
        raise AssertionError("preflight validation drift")
    if preflight_validation["decision"] != "AUTHORIZE_ONE_HASH_FROZEN_TARGET_RUN":
        raise AssertionError("target not authorized")

    meta_rows = table(META)
    meta = {row["source_group_id"]: row for row in meta_rows}
    if len(meta) != len(meta_rows):
        raise AssertionError("duplicate source-group metadata")
    alignment_rows = table(ALIGN)
    training: dict[str, list[tuple[str, int]]] = {edition: [] for edition in READINGS}
    target_loci = set(capacity["marker_loci"]) | set(capacity["no_obvious_start_loci"])
    aligned: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in alignment_rows:
        info = meta[row["source_group_id"]]
        edition = row["edition"]
        if edition not in READINGS:
            continue
        if row["locus"] in target_loci:
            aligned[(edition, row["locus"])].append(row)
        if info["grammar_scope"] != "CONFIRMED_PROSE" or info["kind"] != "P":
            continue
        match = re.match(r"^(f\d+)", info["page"])
        if not match or match.group(1) in TARGET_FOLIOS:
            continue
        training[edition].append((row["primary_sta_families"], int(row["source_group_index"]) == 1))
    expected_cells = {(edition, locus) for edition in READINGS for locus in target_loci}
    if set(aligned) != expected_cells:
        raise AssertionError("target reading-locus coverage drift")
    for key, rows in aligned.items():
        rows.sort(key=lambda row: int(row["source_group_index"]))
        if [int(row["source_group_index"]) for row in rows] != list(range(1, len(rows) + 1)):
            raise AssertionError(f"target group order drift {key}")
        if not all(row["primary_sta_families"] for row in rows):
            raise AssertionError(f"empty target STA sequence {key}")
    models = {edition: fit_nb(training[edition]) for edition in READINGS}

    folio_by_locus = {}
    for locus in sorted(target_loci):
        page = meta[aligned[(READINGS[0], locus)][0]["source_group_id"]]["page"]
        match = re.match(r"^(f\d+)", page)
        if not match:
            raise AssertionError(f"unparseable target folio {page}")
        folio_by_locus[locus] = match.group(1)
    panels = {}
    raw_arrays = {}
    for name, loci in (
        ("all_markers", capacity["marker_loci"]),
        ("conservative_markers", capacity["conservative_marker_loci"]),
        ("no_obvious_start", capacity["no_obvious_start_loci"]),
    ):
        loci = sorted(loci)
        arrays = panel_arrays(loci, aligned, models)
        panel = evaluate_panel(arrays, {locus: folio_by_locus[locus] for locus in loci})
        raw_arrays[name] = arrays
        panels[name] = compact(panel, arrays)

    all_gates = primary_gates(panels["all_markers"], 0.10)
    conservative_gates = primary_gates(panels["conservative_markers"], 0.08)
    negative = panels["no_obvious_start"]
    negative_rejects = not (negative["M"] >= 0.10 and negative["p"] <= 0.05)
    contrast = panels["all_markers"]["M"] - negative["M"]
    gates = {
        "preflight_and_independent_validation_bound": True,
        "all_marker_primary_gates": all(all_gates.values()),
        "conservative_marker_primary_gates": all(conservative_gates.values()),
        "no_obvious_start_does_not_pass_magnitude_and_p": negative_rejects,
        "marker_minus_no_obvious_M_at_least_005": contrast >= 0.05,
        "training_excludes_f67_through_f73": True,
        "exact_target_locus_and_reading_coverage": set(aligned) == expected_cells,
        "all_outputs_finite": all(
            np.isfinite(value).all()
            for arrays in raw_arrays.values() for rows in arrays.values() for value in rows.values()
        ),
        "frozen_hashes_and_target_isolation_pass": True,
    }
    statistical_pass = all(gates.values())
    result = {
        "experiment": "CMR001_TARGET",
        "status": (
            "PROVISIONAL_CONFIRMATION_PENDING_INDEPENDENT_RECONSTRUCTION"
            if statistical_pass else "PROVISIONAL_NONCONFIRMATION_PENDING_INDEPENDENT_RECONSTRUCTION"
        ),
        "freeze_sha256": sha(FREEZE),
        "frozen_git_commit": freeze["git_commit"],
        "inputs": {relative: sha(BASE / relative) for relative in freeze["frozen_files"]},
        "training": {
            edition: {
                "rows": len(training[edition]),
                "positive": sum(label for _, label in training[edition]),
                "negative": sum(not label for _, label in training[edition]),
            }
            for edition in READINGS
        },
        "panels": panels,
        "all_marker_primary_gates": all_gates,
        "conservative_marker_primary_gates": conservative_gates,
        "marker_minus_no_obvious_M": contrast,
        "gates": gates,
        "statistical_gates_pass": statistical_pass,
        "target_score_opened": True,
        "independent_reconstruction_pending": True,
        "decision": "REQUIRE_INDEPENDENT_RECONSTRUCTION_BEFORE_INTERPRETATION",
        "claim_ceiling": (
            "Pending independent reconstruction. On a validated pass only: public drawn circle markers "
            "preferentially select locally line-initial-like groups at this aggregate panel. No global "
            "start, direction, degree, number, word, meaning, plaintext, or translation."
        ),
    }
    report = report_text(result)
    # Recheck the exact one-shot destinations immediately before writing.
    if any(path.exists() for path in (OUT, REPORT, VALIDATION_OUT, VALIDATION_REPORT)):
        raise SystemExit("target or validation artifact appeared during run")
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "M": panels["all_markers"]["M"],
        "p": panels["all_markers"]["p"],
        "statistical_gates_pass": statistical_pass,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
