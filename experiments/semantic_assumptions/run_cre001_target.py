#!/usr/bin/env python3
"""One-shot frozen target run for CRE001."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

from cre001_core import (
    COMPONENTS, READINGS, assignment_matrix, compact, crossrole_similarity,
    evaluate, primary_gates,
)


BASE = Path(__file__).resolve().parent
R = BASE / "results"
FREEZE = BASE / "CRE001_TARGET_FREEZE.json"
CAPACITY = R / "circle_crossrole_echo_capacity.json"
ALIGN = R / "source_sta_group_alignment.tsv"
META = R / "source_separator_transcription.tsv"
CONTROLS = R / "cre001_controls.json"
CONTROL_VALIDATION = R / "cre001_controls_validation.json"
OUT = R / "cre001_target.json"
REPORT = R / "cre001_target.md"
VALIDATION_OUT = R / "cre001_target_validation.json"
VALIDATION_REPORT = R / "cre001_target_validation.md"
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


def table(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def verify_freeze() -> dict[str, object]:
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    if freeze.get("experiment") != "CRE001_TARGET_FREEZE" or freeze.get("status") != "FROZEN_TARGET_UNOPENED":
        raise AssertionError("freeze status")
    absent = {
        "results/cre001_target.json", "results/cre001_target.md",
        "results/cre001_target_validation.json", "results/cre001_target_validation.md",
    }
    if set(freeze.get("required_absent_outputs", [])) != absent:
        raise AssertionError("output allowlist")
    if set(freeze.get("frozen_files", {})) != set(freeze.get("frozen_file_allowlist", [])):
        raise AssertionError("frozen-file allowlist")
    if set(freeze.get("frozen_files", {})) != set(FROZEN_FILES):
        raise AssertionError("hardcoded frozen-file allowlist")
    for relative, expected in freeze["frozen_files"].items():
        path = BASE / relative
        if not path.is_file() or sha(path) != expected:
            raise AssertionError(f"frozen file drift {relative}")
    if any((BASE / relative).exists() for relative in absent):
        raise SystemExit("target or validation artifact exists")
    return freeze


def panel_gates(result: dict[str, object], magnitude: float, p_threshold: float) -> dict[str, bool]:
    return {
        "magnitude": result["M"] >= magnitude,
        "p": result["p"] <= p_threshold,
        "all_readings_positive": all(value > 0 for value in result["T_by_reading"].values()),
        "both_components_positive_every_reading": all(
            value > 0 for edition in READINGS
            for value in result["component_effects_by_reading"][edition].values()
        ),
    }


def report_text(result: dict[str, object]) -> str:
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


def main() -> None:
    freeze = verify_freeze()
    capacity = json.loads(CAPACITY.read_text(encoding="utf-8"))
    controls = json.loads(CONTROLS.read_text(encoding="utf-8"))
    validation = json.loads(CONTROL_VALIDATION.read_text(encoding="utf-8"))
    if capacity["status"] != "PASS_UNSCORED_16_PAGE_5_FOLIO_C_TO_L_PANEL":
        raise AssertionError("capacity")
    if controls["status"] != "PASS_TARGET_BLIND_CONTROL_GATE":
        raise AssertionError("controls")
    if validation["status"] != "PASS_INDEPENDENT_COMPLETE_CONTROL_RECONSTRUCTION":
        raise AssertionError("control validation")
    if validation["decision"] != "AUTHORIZE_ONE_SEPARATELY_HASH_FROZEN_TARGET_RUN":
        raise AssertionError("authorization")

    pages = capacity["eligible_pages"]
    zodiac_pages = capacity["zodiac_sensitivity_pages"]
    folio_by_page = {
        row["page"]: row["physical_folio"] for row in capacity["per_page"]
    }
    meta_rows = table(META)
    meta = {row["source_group_id"]: row for row in meta_rows}
    if len(meta) != len(meta_rows):
        raise AssertionError("metadata duplicates")
    bags = {
        edition: {role: {page: [] for page in pages} for role in ("C", "L")}
        for edition in READINGS
    }
    target_rows = 0
    alternative_rows_excluded = 0
    for row in table(ALIGN):
        info = meta[row["source_group_id"]]
        edition = row["edition"]
        page = info["page"]
        role = info["kind"]
        if edition not in READINGS or page not in bags[edition]["C"] or role not in ("C", "L"):
            continue
        target_rows += 1
        if int(row["alternative_site_count"]) != 0:
            alternative_rows_excluded += 1
            continue
        group = row["primary_sta_families"]
        if not group:
            raise AssertionError("empty primary STA family group")
        bags[edition][role][page].append(group)
    if any(not bags[edition][role][page] for edition in READINGS for role in ("C", "L") for page in pages):
        raise AssertionError("empty target bag")
    assignments = assignment_matrix(pages, folio_by_page)
    zodiac_folios = {page: folio_by_page[page] for page in zodiac_pages}
    zodiac_assignments = assignment_matrix(zodiac_pages, zodiac_folios)
    if assignments.shape != (138_240, 16) or zodiac_assignments.shape != (5_760, 12):
        raise AssertionError("assignment drift")

    full_components = {}
    removed_components = {}
    exact_groups_removed = {}
    for edition in READINGS:
        full_components[edition] = crossrole_similarity(
            bags[edition]["L"], bags[edition]["C"], pages, False
        )
        removed_components[edition] = crossrole_similarity(
            bags[edition]["L"], bags[edition]["C"], pages, True
        )
        exact_groups_removed[edition] = {
            page: sum(group in set(bags[edition]["C"][page]) for group in bags[edition]["L"][page])
            for page in pages
        }
    primary = evaluate(full_components, pages, folio_by_page, assignments)
    no_exact = evaluate(removed_components, pages, folio_by_page, assignments)
    zodiac_components = {
        edition: {
            size: full_components[edition][size][
                [pages.index(page) for page in zodiac_pages]
            ][:, [pages.index(page) for page in zodiac_pages]]
            for size in COMPONENTS
        }
        for edition in READINGS
    }
    zodiac = evaluate(zodiac_components, zodiac_pages, zodiac_folios, zodiac_assignments)

    primary_registered = primary_gates(primary, 0.04, 0.01, 4, True)
    removed_registered = panel_gates(no_exact, 0.03, 0.05)
    zodiac_registered = panel_gates(zodiac, 0.03, 0.05)
    zodiac_registered["three_of_four_positive_folios_each_reading"] = all(
        value >= 3 for value in zodiac["positive_folios_by_reading"].values()
    )
    gates = {
        "controls_freeze_and_isolation": True,
        "primary": all(primary_registered.values()),
        "no_exact_group_echo": all(removed_registered.values()),
        "zodiac_only": all(zodiac_registered.values()),
        "exact_assignment_counts": len(assignments) == 138_240 and len(zodiac_assignments) == 5_760,
        "all_target_bags_nonempty": True,
        "zero_parser_OCR_vision_gloss_or_object_fields": True,
    }
    statistical_pass = all(gates.values())
    result = {
        "experiment": "CRE001_TARGET",
        "status": (
            "PROVISIONAL_CONFIRMATION_PENDING_INDEPENDENT_RECONSTRUCTION"
            if statistical_pass else "PROVISIONAL_NONCONFIRMATION_PENDING_INDEPENDENT_RECONSTRUCTION"
        ),
        "freeze_sha256": sha(FREEZE),
        "frozen_git_commit": freeze["git_commit"],
        "inputs": {relative: sha(BASE / relative) for relative in freeze["frozen_files"]},
        "target_scope": {
            "pages": pages,
            "folios": sorted(set(folio_by_page.values())),
            "reading_role_bags": len(READINGS) * 2 * len(pages),
            "joined_source_rows_before_alternative_exclusion": target_rows,
            "alternative_site_rows_excluded": alternative_rows_excluded,
            "retained_groups": {
                edition: {role: sum(len(values) for values in bags[edition][role].values()) for role in ("C", "L")}
                for edition in READINGS
            },
            "complete_same_page_L_groups_removed_in_sensitivity": exact_groups_removed,
        },
        "panels": {
            "primary": compact(primary),
            "no_exact_group_echo": compact(no_exact),
            "zodiac_only": compact(zodiac),
        },
        "primary_gates": primary_registered,
        "no_exact_group_echo_gates": removed_registered,
        "zodiac_only_gates": zodiac_registered,
        "gates": gates,
        "statistical_gates_pass": statistical_pass,
        "target_STA_identity_opened": True,
        "independent_reconstruction_pending": True,
        "decision": "REQUIRE_INDEPENDENT_RECONSTRUCTION_BEFORE_INTERPRETATION",
        "claim_ceiling": (
            "Pending independent reconstruction. On a validated pass only: L labels and same-page C "
            "circular text share an anonymous page-specific partial-construction field beyond same-folio "
            "alternatives. No object ownership, sign name, word, meaning, plaintext, or translation."
        ),
    }
    report = report_text(result)
    if any(path.exists() for path in (OUT, REPORT, VALIDATION_OUT, VALIDATION_REPORT)):
        raise SystemExit("target artifact appeared during run")
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps({
        "status": result["status"], "M": primary["M"], "p": primary["p"],
        "no_exact_M": no_exact["M"], "no_exact_p": no_exact["p"],
        "zodiac_M": zodiac["M"], "zodiac_p": zodiac["p"],
        "statistical_gates_pass": statistical_pass,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
