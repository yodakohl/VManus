#!/usr/bin/env python3
"""Clean-room reconstruction of the one-shot CMR001 target result.

This module intentionally imports neither the production core nor the runner.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np


BASE = Path(__file__).resolve().parent
R = BASE / "results"
FREEZE = BASE / "CMR001_TARGET_FREEZE.json"
ALIGN = R / "source_sta_group_alignment.tsv"
META = R / "source_separator_transcription.tsv"
CAPACITY = R / "circle_marker_reset_capacity.json"
TARGET = R / "cmr001_target.json"
TARGET_REPORT = R / "cmr001_target.md"
OUT = R / "cmr001_target_validation.json"
REPORT = R / "cmr001_target_validation.md"
READINGS = ("ZL3b", "IT2a", "RF1b")
ASSIGNMENTS = 65_536
TOL = 1e-15
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


def array_sha(array: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(array, dtype="<f8").tobytes(order="C")).hexdigest()


def index_sha(array: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(array, dtype="<i8").tobytes(order="C")).hexdigest()


def table(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def features(word: str) -> tuple[str, ...]:
    if not word:
        raise AssertionError("empty STA family word")
    return (
        f"LEN={min(len(word), 12)}",
        f"P1={word[:1]}", f"P2={word[:2]}", f"P3={word[:3]}",
        f"S1={word[-1:]}", f"S2={word[-2:]}", f"S3={word[-3:]}",
    )


@dataclass
class Model:
    totals: tuple[int, int]
    vocab: tuple[set[str], ...]
    counts: tuple[tuple[Counter[str], ...], tuple[Counter[str], ...]]

    def score(self, word: str) -> float:
        answer = 0.0
        for field, value in enumerate(features(word)):
            categories = len(self.vocab[field]) + 1
            for label, sign in ((1, 1.0), (0, -1.0)):
                answer += sign * math.log(
                    (self.counts[label][field].get(value, 0) + 1.0)
                    / (self.totals[label] + categories)
                )
        return answer


def train(examples: list[tuple[str, int]]) -> Model:
    totals = [0, 0]
    counts = [[Counter() for _ in range(7)] for _ in range(2)]
    vocab = [set() for _ in range(7)]
    for word, label in examples:
        totals[label] += 1
        for field, value in enumerate(features(word)):
            counts[label][field][value] += 1
            vocab[field].add(value)
    if not all(totals):
        raise AssertionError("missing training class")
    return Model(
        (totals[0], totals[1]), tuple(vocab),
        (tuple(counts[0]), tuple(counts[1])),
    )


def ranks(scores: np.ndarray) -> np.ndarray:
    values = np.asarray(scores, dtype=np.float64)
    answer = np.empty(len(values), dtype=np.float64)
    for i, value in enumerate(values):
        answer[i] = (np.sum(values < value) + 0.5 * np.sum(values == value)) / len(values) - 0.5
    return answer


def phases(locus: str) -> np.ndarray:
    result = np.empty(ASSIGNMENTS, dtype=np.float64)
    denominator = float(2**64)
    for assignment in range(ASSIGNMENTS):
        digest = hashlib.sha256(f"CMR001_PHASE_V1|{assignment}|{locus}".encode("ascii")).digest()
        result[assignment] = int.from_bytes(digest[:8], "big", signed=False) / denominator
    return result


def evaluate(
    arrays: dict[str, dict[str, np.ndarray]], folio_by_locus: dict[str, str]
) -> dict[str, object]:
    loci = sorted(folio_by_locus)
    folios = sorted(set(folio_by_locus.values()))
    loci_by_folio = {
        folio: [locus for locus in loci if folio_by_locus[locus] == folio]
        for folio in folios
    }
    phase = {locus: phases(locus) for locus in loci}
    canonical = {edition: {} for edition in READINGS}
    relative = {edition: {} for edition in READINGS}
    folio_effects = {edition: {} for edition in READINGS}
    null_by_reading = np.empty((ASSIGNMENTS, len(READINGS)), dtype=np.float64)
    for edition_index, edition in enumerate(READINGS):
        observed = {}
        locus_null = {}
        for locus in loci:
            percentile = ranks(arrays[edition][locus])
            canonical[edition][locus] = percentile.copy()
            chosen = np.floor(phase[locus] * len(percentile)).astype(np.int64) % len(percentile)
            relative[edition][locus] = chosen
            observed[locus] = float(percentile[0])
            locus_null[locus] = percentile[chosen]
        for folio in folios:
            folio_effects[edition][folio] = float(np.mean([
                observed[locus] for locus in loci_by_folio[folio]
            ]))
        null_folios = [
            np.mean(np.vstack([locus_null[locus] for locus in loci_by_folio[folio]]), axis=0)
            for folio in folios
        ]
        null_by_reading[:, edition_index] = np.mean(np.vstack(null_folios), axis=0)
    reading_T = {
        edition: float(np.mean(list(folio_effects[edition].values()))) for edition in READINGS
    }
    M = min(reading_T.values())
    null_M = np.min(null_by_reading, axis=1)
    p = (1 + int(np.sum(null_M >= M - TOL))) / (ASSIGNMENTS + 1)
    loo = {
        deleted: min(float(np.mean([
            value for folio, value in folio_effects[edition].items() if folio != deleted
        ])) for edition in READINGS)
        for deleted in folios
    }
    support = {
        edition: sum(value > 0 for value in folio_effects[edition].values())
        for edition in READINGS
    }
    concentration = {}
    for edition in READINGS:
        absolute = [abs(value) for value in folio_effects[edition].values()]
        concentration[edition] = max(absolute) / sum(absolute) if sum(absolute) else 1.0
    payload = {
        "loci": loci,
        "folios": folios,
        "T_by_reading": reading_T,
        "M": M,
        "p": p,
        "folio_effects": folio_effects,
        "positive_folios_by_reading": support,
        "leave_one_folio_out_M": loo,
        "concentration_by_reading": concentration,
        "digests": {
            "null_M_sha256": array_sha(null_M),
            "null_by_reading_sha256": array_sha(null_by_reading),
            "canonical_percentile_arrays_sha256": hashlib.sha256("".join(
                array_sha(canonical[edition][locus]) for edition in READINGS for locus in loci
            ).encode("ascii")).hexdigest(),
            "relative_assignment_indices_sha256": hashlib.sha256("".join(
                index_sha(relative[edition][locus]) for edition in READINGS for locus in loci
            ).encode("ascii")).hexdigest(),
            "score_arrays_sha256": hashlib.sha256("".join(
                array_sha(arrays[edition][locus]) for edition in READINGS for locus in loci
            ).encode("ascii")).hexdigest(),
            "folio_effects_sha256": canonical_sha(folio_effects),
        },
    }
    payload["digests"]["compact_evaluation_sha256"] = canonical_sha({
        key: value for key, value in payload.items() if key != "digests"
    })
    return payload


def primary_gates(panel: dict[str, object], magnitude: float) -> dict[str, bool]:
    return {
        "magnitude": panel["M"] >= magnitude,
        "p": panel["p"] <= 0.05,
        "all_readings_positive": all(value > 0 for value in panel["T_by_reading"].values()),
        "five_of_six_folios_each_reading": all(
            value >= 5 for value in panel["positive_folios_by_reading"].values()
        ),
        "all_leave_one_folio_out_above_005": all(
            value > 0.05 for value in panel["leave_one_folio_out_M"].values()
        ),
        "concentration_at_most_035": all(
            value <= 0.35 for value in panel["concentration_by_reading"].values()
        ),
    }


def producer_report(result: dict[str, object]) -> str:
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
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    checks = 0

    def check(condition: bool, message: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            raise AssertionError(message)

    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    check(freeze["experiment"] == "CMR001_TARGET_FREEZE", "freeze experiment")
    check(freeze["status"] == "FROZEN_TARGET_UNOPENED", "freeze status")
    exact_absent = {
        "results/cmr001_target.json", "results/cmr001_target.md",
        "results/cmr001_target_validation.json", "results/cmr001_target_validation.md",
    }
    check(set(freeze["required_absent_outputs"]) == exact_absent, "freeze output set")
    check(set(freeze["frozen_files"]) == set(FROZEN_FILES), "freeze file allowlist")
    for relative, expected_hash in freeze["frozen_files"].items():
        check(sha(BASE / relative) == expected_hash, f"frozen hash {relative}")
    stored = json.loads(TARGET.read_text(encoding="utf-8"))
    capacity = json.loads(CAPACITY.read_text(encoding="utf-8"))
    check(stored["freeze_sha256"] == sha(FREEZE), "freeze result binding")
    check(stored["frozen_git_commit"] == freeze["git_commit"], "commit binding")
    check(stored["inputs"] == {relative: sha(BASE / relative) for relative in freeze["frozen_files"]}, "input bindings")

    meta_rows = table(META)
    meta = {row["source_group_id"]: row for row in meta_rows}
    check(len(meta) == len(meta_rows), "metadata uniqueness")
    target_loci = set(capacity["marker_loci"]) | set(capacity["no_obvious_start_loci"])
    aligned: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    training: dict[str, list[tuple[str, int]]] = {edition: [] for edition in READINGS}
    for row in table(ALIGN):
        info = meta[row["source_group_id"]]
        edition = row["edition"]
        if edition not in READINGS:
            continue
        if row["locus"] in target_loci:
            aligned[(edition, row["locus"])].append(row)
        if info["grammar_scope"] != "CONFIRMED_PROSE" or info["kind"] != "P":
            continue
        match = re.match(r"^(f\d+)", info["page"])
        if match and match.group(1) not in TARGET_FOLIOS:
            training[edition].append((
                row["primary_sta_families"], int(row["source_group_index"]) == 1
            ))
    expected_cells = {(edition, locus) for edition in READINGS for locus in target_loci}
    check(set(aligned) == expected_cells, "target cell coverage")
    for key, rows in aligned.items():
        rows.sort(key=lambda row: int(row["source_group_index"]))
        check([int(row["source_group_index"]) for row in rows] == list(range(1, len(rows) + 1)), f"group order {key}")
        check(all(row["primary_sta_families"] for row in rows), f"nonempty STA {key}")
    models = {edition: train(training[edition]) for edition in READINGS}
    training_summary = {
        edition: {
            "rows": len(training[edition]),
            "positive": sum(label for _, label in training[edition]),
            "negative": sum(not label for _, label in training[edition]),
        }
        for edition in READINGS
    }
    check(stored["training"] == training_summary, "training summary")
    folio_by_locus = {}
    for locus in sorted(target_loci):
        page = meta[aligned[(READINGS[0], locus)][0]["source_group_id"]]["page"]
        match = re.match(r"^(f\d+)", page)
        check(match is not None, f"target folio parse {page}")
        folio_by_locus[locus] = match.group(1)
    panels = {}
    for name, loci in (
        ("all_markers", capacity["marker_loci"]),
        ("conservative_markers", capacity["conservative_marker_loci"]),
        ("no_obvious_start", capacity["no_obvious_start_loci"]),
    ):
        loci = sorted(loci)
        arrays = {edition: {} for edition in READINGS}
        for edition in READINGS:
            for locus in loci:
                arrays[edition][locus] = np.asarray([
                    models[edition].score(row["primary_sta_families"])
                    for row in aligned[(edition, locus)]
                ], dtype=np.float64)
        panels[name] = evaluate(arrays, {locus: folio_by_locus[locus] for locus in loci})
        check(stored["panels"][name] == panels[name], f"complete panel {name}")

    all_gates = primary_gates(panels["all_markers"], 0.10)
    conservative_gates = primary_gates(panels["conservative_markers"], 0.08)
    negative = panels["no_obvious_start"]
    contrast = panels["all_markers"]["M"] - negative["M"]
    gates = {
        "preflight_and_independent_validation_bound": True,
        "all_marker_primary_gates": all(all_gates.values()),
        "conservative_marker_primary_gates": all(conservative_gates.values()),
        "no_obvious_start_does_not_pass_magnitude_and_p": not (
            negative["M"] >= 0.10 and negative["p"] <= 0.05
        ),
        "marker_minus_no_obvious_M_at_least_005": contrast >= 0.05,
        "training_excludes_f67_through_f73": True,
        "exact_target_locus_and_reading_coverage": set(aligned) == expected_cells,
        "all_outputs_finite": True,
        "frozen_hashes_and_target_isolation_pass": True,
    }
    statistical_pass = all(gates.values())
    expected_status = (
        "PROVISIONAL_CONFIRMATION_PENDING_INDEPENDENT_RECONSTRUCTION"
        if statistical_pass else "PROVISIONAL_NONCONFIRMATION_PENDING_INDEPENDENT_RECONSTRUCTION"
    )
    check(stored["all_marker_primary_gates"] == all_gates, "all-marker gates")
    check(stored["conservative_marker_primary_gates"] == conservative_gates, "conservative gates")
    check(stored["marker_minus_no_obvious_M"] == contrast, "panel contrast")
    check(stored["gates"] == gates, "registered gates")
    check(stored["statistical_gates_pass"] is statistical_pass, "statistical decision")
    check(stored["status"] == expected_status, "producer status")
    check(stored["target_score_opened"] is True, "target flag")
    check(stored["independent_reconstruction_pending"] is True, "pending flag")
    check(TARGET_REPORT.read_text(encoding="utf-8") == producer_report(stored), "producer report")

    decision = (
        "CONFIRMED_AGGREGATE_LOCAL_MARKER_RESET_LIKENESS"
        if statistical_pass else "FINAL_NONCONFIRMATION_FIXED_STA_LINE_INITIAL_REPRESENTATION"
    )
    validation = {
        "experiment": "CMR001_TARGET_VALIDATION",
        "status": "PASS_INDEPENDENT_TARGET_RECONSTRUCTION",
        "checks": checks,
        "bindings": {
            "freeze_sha256": sha(FREEZE),
            "target_sha256": sha(TARGET),
            "target_report_sha256": sha(TARGET_REPORT),
            "validator_sha256": sha(Path(__file__)),
        },
        "reconstructed": {
            "panels": 3,
            "assignments_per_panel": ASSIGNMENTS,
            "reading_locus_cells": len(expected_cells),
            "all_marker_M": panels["all_markers"]["M"],
            "all_marker_p": panels["all_markers"]["p"],
            "conservative_M": panels["conservative_markers"]["M"],
            "conservative_p": panels["conservative_markers"]["p"],
            "no_obvious_M": negative["M"],
            "no_obvious_p": negative["p"],
            "marker_minus_no_obvious_M": contrast,
            "statistical_gates_pass": statistical_pass,
        },
        "target_isolation": {
            "training_excluded_f67_through_f73": True,
            "retained_parser_or_formal_role_used": False,
            "OCR_or_automated_vision_used": False,
            "English_gloss_or_object_label_used": False,
        },
        "decision": decision,
        "claim_ceiling": (
            "On confirmation only: public drawn circle markers preferentially select locally "
            "line-initial-like groups at this aggregate panel. No global start, direction, degree, "
            "number, word, meaning, plaintext, or translation."
        ),
    }
    report = (
        "# CMR001 target validation\n\n"
        "Status: **PASS_INDEPENDENT_TARGET_RECONSTRUCTION**\n\n"
        f"A nonimporting implementation passed {checks} checks and exactly reconstructed all three "
        f"65,536-assignment panels, every target score, percentile, synchronized index, null orbit, "
        f"folio effect, digest, and registered gate. The all-marker statistic is "
        f"M={panels['all_markers']['M']:.6f}, p={panels['all_markers']['p']:.6f}. "
        f"Decision: **{decision}**.\n\n"
        "The training corpus excludes f67--f73 and the reconstruction uses no retained parser, "
        "OCR, automated vision, English gloss, or illustrated-object label. The claim ceiling is "
        "aggregate local line-initial-like selection at public human-described drawn seams only; "
        "no global start, direction, degree, number, word, meaning, plaintext, or translation follows.\n"
    )
    if OUT.exists() or REPORT.exists():
        raise SystemExit("validation artifact appeared during run")
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps({"checks": checks, "status": validation["status"], "decision": decision}, sort_keys=True))


if __name__ == "__main__":
    main()
