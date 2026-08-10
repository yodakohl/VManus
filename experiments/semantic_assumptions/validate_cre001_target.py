#!/usr/bin/env python3
"""Clean-room reconstruction of the one-shot CRE001 target."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import re
from collections import Counter
from pathlib import Path

import numpy as np


BASE = Path(__file__).resolve().parent
R = BASE / "results"
FREEZE = BASE / "CRE001_TARGET_FREEZE.json"
CAPACITY = R / "circle_crossrole_echo_capacity.json"
ALIGN = R / "source_sta_group_alignment.tsv"
META = R / "source_separator_transcription.tsv"
TARGET = R / "cre001_target.json"
TARGET_REPORT = R / "cre001_target.md"
OUT = R / "cre001_target_validation.json"
REPORT = R / "cre001_target_validation.md"
READINGS = ("ZL3b", "IT2a", "RF1b")
SIZES = (3, 4)
TOL = 1e-15
FROZEN_FILES = (
    "CIRCLE_CROSSROLE_ECHO_METHOD.md",
    "SOURCE_SEPARATOR_TRANSCRIPTION_SPEC.md",
    "SOURCE_STA_ALIGNMENT_SPEC.md",
    "audit_circle_crossrole_echo_capacity.py",
    "validate_circle_crossrole_echo_capacity.py",
    "build_public_circle_block_role_atlas.py",
    "validate_public_circle_block_role_atlas.py",
    "build_source_separator_transcription.py",
    "validate_source_separator_transcription.py",
    "build_source_sta_alignment.py",
    "validate_source_sta_alignment.py",
    "cre001_core.py",
    "run_cre001_controls.py",
    "validate_cre001_controls.py",
    "run_cre001_target.py",
    "validate_cre001_target.py",
    "results/public_voynich_nu_page_annotations_v2.tsv",
    "results/public_circle_block_role_atlas.tsv",
    "results/public_circle_block_role_atlas.json",
    "results/public_circle_block_role_atlas_report.md",
    "results/public_circle_block_role_atlas_validation.json",
    "results/public_circle_block_role_atlas_validation.md",
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
    "results/circle_crossrole_echo_capacity.json",
    "results/circle_crossrole_echo_capacity.md",
    "results/circle_crossrole_echo_capacity_validation.json",
    "results/circle_crossrole_echo_capacity_validation.md",
    "results/cre001_controls.json",
    "results/cre001_controls.md",
    "results/cre001_controls_validation_attempt1.json",
    "results/cre001_controls_validation_attempt1.md",
    "results/cre001_controls_validation.json",
    "results/cre001_controls_validation.md",
    "results/pre_grounding_interlinear.tsv",
    "../../transcription/sources/ZL3b-n.txt",
    "../../transcription/sources/IT2a-n.txt",
    "../../transcription/sources/RF1b-e.txt",
    "../../transcription/sources/sta/ZL3b.txt",
    "../../transcription/sources/sta/IT2a.txt",
    "../../transcription/sources/sta/RF1b.txt",
    "../../transcription/sources/sta/STA-Eva_def.bit",
    "../../transcription/sources/sta/STA-EvaT_def.bit",
    "../../transcription/sources/sta/STA-Eva_Bint.bit",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def a_sha(value: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(value, dtype="<f8").tobytes()).hexdigest()


def i_sha(value: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(value, dtype="<i8").tobytes()).hexdigest()


def c_sha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def table(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def grams(group: str, size: int) -> list[str]:
    return [group[index:index + size] for index in range(len(group) - size + 1)]


def similarity(label, circle, pages, remove):
    output = {size: np.empty((len(pages), len(pages)), dtype=np.float64) for size in SIZES}
    circle_surfaces = {page: set(circle[page]) for page in pages}
    label_counts = {}
    circle_sets = {}
    for page in pages:
        selected = [group for group in label[page] if not remove or group not in circle_surfaces[page]]
        label_counts[page] = {
            size: Counter(g for group in selected for g in grams(group, size)) for size in SIZES
        }
        circle_sets[page] = {
            size: {g for group in circle[page] for g in grams(group, size)} for size in SIZES
        }
        if any(not label_counts[page][size] for size in SIZES):
            raise AssertionError(f"empty label ngram bag {page}")
        if any(not circle_sets[page][size] for size in SIZES):
            raise AssertionError(f"empty circle ngram bag {page}")
    for i, lp in enumerate(pages):
        for j, cp in enumerate(pages):
            for size in SIZES:
                counts = label_counts[lp][size]
                output[size][i, j] = sum(
                    count for gram, count in counts.items() if gram in circle_sets[cp][size]
                ) / sum(counts.values())
    return output


def assignments(pages, folios):
    groups = {
        folio: [index for index, page in enumerate(pages) if folios[page] == folio]
        for folio in sorted(set(folios.values()))
    }
    rows = []
    for product in itertools.product(*[list(itertools.permutations(values)) for values in groups.values()]):
        row = list(range(len(pages)))
        for destinations, sources in zip(groups.values(), product):
            for destination, source in zip(destinations, sources):
                row[destination] = source
        rows.append(row)
    matrix = np.asarray(rows, dtype=np.int64)
    if len({tuple(row) for row in matrix.tolist()}) != len(matrix):
        raise AssertionError("duplicate assignments")
    return matrix


def evaluate(components_by_reading, pages, folios, assignment_rows):
    identity = int(np.flatnonzero(np.all(assignment_rows == np.arange(len(pages)), axis=1))[0])
    folio_names = sorted(set(folios.values()))
    positions = {
        folio: [index for index, page in enumerate(pages) if folios[page] == folio]
        for folio in folio_names
    }
    weights = np.asarray([
        1.0 / (len(folio_names) * len(positions[folios[page]])) for page in pages
    ], dtype=np.float64)
    raw_orbits = np.empty((len(assignment_rows), len(READINGS)), dtype=np.float64)
    centered_orbits = np.empty_like(raw_orbits)
    T = {}
    component_effects = {edition: {} for edition in READINGS}
    page_effects = {edition: {} for edition in READINGS}
    folio_effects = {edition: {} for edition in READINGS}
    matrix_hashes = {}
    destinations = np.arange(len(pages))[None, :]
    for edition_index, edition in enumerate(READINGS):
        components = components_by_reading[edition]
        for size in SIZES:
            matrix_hashes[f"{edition}_k{size}"] = a_sha(components[size])
            selected = components[size][destinations, assignment_rows]
            orbit = selected @ weights
            component_effects[edition][str(size)] = float(orbit[identity] - np.mean(orbit))
        combined = np.mean(np.stack([components[size] for size in SIZES], axis=0), axis=0)
        selected = combined[destinations, assignment_rows]
        raw = selected @ weights
        raw_orbits[:, edition_index] = raw
        centered = raw - np.mean(raw)
        centered_orbits[:, edition_index] = centered
        T[edition] = float(centered[identity])
        for page_index, page in enumerate(pages):
            candidates = positions[folios[page]]
            page_effects[edition][page] = float(
                combined[page_index, page_index] - np.mean(combined[page_index, candidates])
            )
        for folio in folio_names:
            folio_effects[edition][folio] = float(np.mean([
                page_effects[edition][pages[index]] for index in positions[folio]
            ]))
    M = min(T.values())
    null_M = np.min(centered_orbits, axis=1)
    p = int(np.sum(null_M >= M - TOL)) / len(assignment_rows)
    support = {
        edition: sum(value > 0 for value in folio_effects[edition].values()) for edition in READINGS
    }
    loo = {
        deleted: min(float(np.mean([
            value for folio, value in folio_effects[edition].items() if folio != deleted
        ])) for edition in READINGS)
        for deleted in folio_names
    }
    concentration = {}
    for edition in READINGS:
        absolute = [abs(value) for value in folio_effects[edition].values()]
        concentration[edition] = max(absolute) / sum(absolute) if sum(absolute) else 1.0
    result = {
        "pages": pages,
        "folios": folio_names,
        "assignment_count": len(assignment_rows),
        "identity_assignment_index": identity,
        "T_by_reading": T,
        "M": M,
        "p": p,
        "component_effects_by_reading": component_effects,
        "page_effects": page_effects,
        "folio_effects": folio_effects,
        "positive_folios_by_reading": support,
        "leave_one_folio_out_M": loo,
        "concentration_by_reading": concentration,
        "digests": {
            "assignments_sha256": i_sha(assignment_rows),
            "similarity_matrices_sha256": c_sha(matrix_hashes),
            "raw_orbits_sha256": a_sha(raw_orbits),
            "centered_orbits_sha256": a_sha(centered_orbits),
            "null_M_sha256": a_sha(null_M),
            "component_effects_sha256": c_sha(component_effects),
            "page_effects_sha256": c_sha(page_effects),
            "folio_effects_sha256": c_sha(folio_effects),
        },
    }
    result["digests"]["result_core_sha256"] = c_sha({key: value for key, value in result.items() if key != "digests"})
    return result


def primary_gates(result):
    return {
        "magnitude": result["M"] >= 0.04,
        "p": result["p"] <= 0.01,
        "all_readings_positive": all(value > 0 for value in result["T_by_reading"].values()),
        "both_components_positive_every_reading": all(
            value > 0 for edition in READINGS for value in result["component_effects_by_reading"][edition].values()
        ),
        "required_positive_folios_each_reading": all(
            value >= 4 for value in result["positive_folios_by_reading"].values()
        ),
        "all_leave_one_folio_out_above_002": all(value > 0.02 for value in result["leave_one_folio_out_M"].values()),
        "concentration_at_most_045": all(value <= 0.45 for value in result["concentration_by_reading"].values()),
    }


def panel_gates(result, magnitude, p_threshold):
    return {
        "magnitude": result["M"] >= magnitude,
        "p": result["p"] <= p_threshold,
        "all_readings_positive": all(value > 0 for value in result["T_by_reading"].values()),
        "both_components_positive_every_reading": all(
            value > 0 for edition in READINGS for value in result["component_effects_by_reading"][edition].values()
        ),
    }


def producer_report(result):
    primary = result["panels"]["primary"]
    removed = result["panels"]["no_exact_group_echo"]
    zodiac = result["panels"]["zodiac_only"]
    return (
        "# CRE001 page-specific circular-to-label echo result\n\n"
        f"Status: **{result['status']}**\n\n"
        f"The frozen 16-page same-folio test gives M={primary['M']:.6f}, exact p={primary['p']:.6f}. "
        "Reading effects are "
        + ", ".join(f"{edition} {primary['T_by_reading'][edition]:.6f}" for edition in READINGS)
        + f". After deleting complete L groups that recur as complete same-page C groups, "
        f"M={removed['M']:.6f}, p={removed['p']:.6f}. The zodiac-only sensitivity gives "
        f"M={zodiac['M']:.6f}, p={zodiac['p']:.6f}.\n\n"
        f"The preregistered gates {'PASS' if result['statistical_gates_pass'] else 'DO NOT PASS'}. "
        "The result remains provisional until nonimporting reconstruction. Even a validated pass "
        "would establish only an anonymous same-page C-to-L partial-construction field; it cannot "
        "assign a label to an object or establish a sign name, word, meaning, plaintext, or translation.\n"
    )


def main():
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    checks = 0

    def check(value, name):
        nonlocal checks
        checks += 1
        if not value:
            raise AssertionError(name)

    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    check(freeze["experiment"] == "CRE001_TARGET_FREEZE", "freeze experiment")
    check(freeze["status"] == "FROZEN_TARGET_UNOPENED", "freeze status")
    check(set(freeze["frozen_files"]) == set(freeze["frozen_file_allowlist"]), "freeze allowlist")
    check(set(freeze["frozen_files"]) == set(FROZEN_FILES), "hardcoded freeze allowlist")
    for relative, expected in freeze["frozen_files"].items():
        check(sha(BASE / relative) == expected, f"hash {relative}")
    stored = json.loads(TARGET.read_text(encoding="utf-8"))
    capacity = json.loads(CAPACITY.read_text(encoding="utf-8"))
    check(stored["freeze_sha256"] == sha(FREEZE), "freeze binding")
    check(stored["frozen_git_commit"] == freeze["git_commit"], "commit binding")
    check(stored["inputs"] == {relative: sha(BASE / relative) for relative in freeze["frozen_files"]}, "input hashes")

    pages = capacity["eligible_pages"]
    zodiac_pages = capacity["zodiac_sensitivity_pages"]
    folios = {row["page"]: row["physical_folio"] for row in capacity["per_page"]}
    meta_rows = table(META)
    meta = {row["source_group_id"]: row for row in meta_rows}
    check(len(meta) == len(meta_rows), "metadata uniqueness")
    bags = {edition: {role: {page: [] for page in pages} for role in ("C", "L")} for edition in READINGS}
    target_rows = 0
    alternative_excluded = 0
    for row in table(ALIGN):
        info = meta[row["source_group_id"]]
        edition, page, role = row["edition"], info["page"], info["kind"]
        if edition not in READINGS or page not in bags[edition]["C"] or role not in ("C", "L"):
            continue
        target_rows += 1
        if int(row["alternative_site_count"]):
            alternative_excluded += 1
            continue
        bags[edition][role][page].append(row["primary_sta_families"])
    for edition in READINGS:
        for role in ("C", "L"):
            for page in pages:
                check(bool(bags[edition][role][page]), f"bag {edition} {role} {page}")
    assignment_rows = assignments(pages, folios)
    zodiac_folios = {page: folios[page] for page in zodiac_pages}
    zodiac_rows = assignments(zodiac_pages, zodiac_folios)
    check(assignment_rows.shape == (138_240, 16), "primary assignments")
    check(zodiac_rows.shape == (5_760, 12), "zodiac assignments")
    full, removed, exact_removed = {}, {}, {}
    for edition in READINGS:
        full[edition] = similarity(bags[edition]["L"], bags[edition]["C"], pages, False)
        removed[edition] = similarity(bags[edition]["L"], bags[edition]["C"], pages, True)
        exact_removed[edition] = {
            page: sum(group in set(bags[edition]["C"][page]) for group in bags[edition]["L"][page])
            for page in pages
        }
    primary = evaluate(full, pages, folios, assignment_rows)
    no_exact = evaluate(removed, pages, folios, assignment_rows)
    selected = [pages.index(page) for page in zodiac_pages]
    zodiac_components = {
        edition: {size: full[edition][size][selected][:, selected] for size in SIZES}
        for edition in READINGS
    }
    zodiac = evaluate(zodiac_components, zodiac_pages, zodiac_folios, zodiac_rows)
    primary_checks = primary_gates(primary)
    removed_checks = panel_gates(no_exact, 0.03, 0.05)
    zodiac_checks = panel_gates(zodiac, 0.03, 0.05)
    zodiac_checks["three_of_four_positive_folios_each_reading"] = all(
        value >= 3 for value in zodiac["positive_folios_by_reading"].values()
    )
    top_gates = {
        "controls_freeze_and_isolation": True,
        "primary": all(primary_checks.values()),
        "no_exact_group_echo": all(removed_checks.values()),
        "zodiac_only": all(zodiac_checks.values()),
        "exact_assignment_counts": len(assignment_rows) == 138_240 and len(zodiac_rows) == 5_760,
        "all_target_bags_nonempty": True,
        "zero_parser_OCR_vision_gloss_or_object_fields": True,
    }
    statistical_pass = all(top_gates.values())
    check(stored["target_scope"]["joined_source_rows_before_alternative_exclusion"] == target_rows, "target row count")
    check(stored["target_scope"]["alternative_site_rows_excluded"] == alternative_excluded, "alternative count")
    check(stored["target_scope"]["complete_same_page_L_groups_removed_in_sensitivity"] == exact_removed, "exact removal")
    check(stored["panels"] == {"primary": primary, "no_exact_group_echo": no_exact, "zodiac_only": zodiac}, "all panels")
    check(stored["primary_gates"] == primary_checks, "primary gates")
    check(stored["no_exact_group_echo_gates"] == removed_checks, "removal gates")
    check(stored["zodiac_only_gates"] == zodiac_checks, "zodiac gates")
    check(stored["gates"] == top_gates, "top gates")
    check(stored["statistical_gates_pass"] is statistical_pass, "decision bool")
    expected_status = (
        "PROVISIONAL_CONFIRMATION_PENDING_INDEPENDENT_RECONSTRUCTION"
        if statistical_pass else "PROVISIONAL_NONCONFIRMATION_PENDING_INDEPENDENT_RECONSTRUCTION"
    )
    check(stored["status"] == expected_status, "status")
    check(TARGET_REPORT.read_text(encoding="utf-8") == producer_report(stored), "producer report")
    decision = (
        "CONFIRMED_PAGE_SPECIFIC_C_TO_L_PARTIAL_CONSTRUCTION_FIELD"
        if statistical_pass else "FINAL_NONCONFIRMATION_FIXED_C_TO_L_ECHO_REPRESENTATION"
    )
    validation = {
        "experiment": "CRE001_TARGET_VALIDATION",
        "status": "PASS_INDEPENDENT_COMPLETE_TARGET_RECONSTRUCTION",
        "checks": checks,
        "bindings": {
            "freeze_sha256": sha(FREEZE),
            "target_sha256": sha(TARGET),
            "target_report_sha256": sha(TARGET_REPORT),
            "validator_sha256": sha(Path(__file__)),
        },
        "reconstructed": {
            "primary_assignments": len(assignment_rows),
            "zodiac_assignments": len(zodiac_rows),
            "primary_M": primary["M"], "primary_p": primary["p"],
            "no_exact_M": no_exact["M"], "no_exact_p": no_exact["p"],
            "zodiac_M": zodiac["M"], "zodiac_p": zodiac["p"],
            "statistical_gates_pass": statistical_pass,
        },
        "isolation": {
            "retained_parser_or_formal_role_used": False,
            "OCR_or_automated_vision_used": False,
            "English_gloss_sign_or_object_field_used": False,
        },
        "decision": decision,
        "claim_ceiling": stored["claim_ceiling"],
    }
    report = (
        "# CRE001 target validation\n\n"
        "Status: **PASS_INDEPENDENT_COMPLETE_TARGET_RECONSTRUCTION**\n\n"
        f"A nonimporting implementation passed {checks} checks and exactly reconstructed all target "
        f"source-group joins, trigram/four-gram matrices, 138,240-row primary and 5,760-row zodiac "
        f"orbits, complete-group deletion, effects, digests, and gates. Primary M={primary['M']:.6f}, "
        f"p={primary['p']:.6f}. Decision: **{decision}**.\n\n"
        "No retained parser, OCR, automated vision, English gloss, sign identity, object attribute, "
        "or label-to-object assignment entered. The result establishes at most an anonymous same-page "
        "C-to-L partial-construction field; no word, meaning, plaintext, or translation follows.\n"
    )
    if OUT.exists() or REPORT.exists():
        raise SystemExit("validation artifact appeared")
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps({"status": validation["status"], "checks": checks, "decision": decision}, sort_keys=True))


if __name__ == "__main__":
    main()
