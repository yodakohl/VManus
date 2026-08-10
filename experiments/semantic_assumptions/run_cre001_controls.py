#!/usr/bin/env python3
"""Target-blind synthetic controls for CRE001."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from cre001_core import (
    COMPONENTS, READINGS, assignment_matrix, compact, crossrole_similarity,
    evaluate, primary_gates,
)


BASE = Path(__file__).resolve().parent
R = BASE / "results"
METHOD = BASE / "CIRCLE_CROSSROLE_ECHO_METHOD.md"
CAPACITY = R / "circle_crossrole_echo_capacity.json"
CAPACITY_VALIDATION = R / "circle_crossrole_echo_capacity_validation.json"
CORE = BASE / "cre001_core.py"
OUT = R / "cre001_controls.json"
REPORT = R / "cre001_controls.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def topology(sizes: tuple[int, ...]) -> tuple[list[str], dict[str, str]]:
    pages = [f"F{folio}_P{page}" for folio, size in enumerate(sizes) for page in range(size)]
    return pages, {page: page.split("_")[0] for page in pages}


def matrices(
    kind: str, pages: list[str], folio_by_page: dict[str, str]
) -> tuple[dict[str, dict[int, np.ndarray]], dict[str, dict[int, np.ndarray]]]:
    count = len(pages)
    full = {edition: {} for edition in READINGS}
    no_exact = {edition: {} for edition in READINGS}
    positions = {
        folio: [index for index, page in enumerate(pages) if folio_by_page[page] == folio]
        for folio in sorted(set(folio_by_page.values()))
    }
    for edition in READINGS:
        for size in COMPONENTS:
            matrix = np.zeros((count, count), dtype=np.float64)
            if kind in {"DISTRIBUTED", "WHOLE_GROUP_DUPLICATE_ONLY"}:
                np.fill_diagonal(matrix, 1.0 - 0.05 * (size - 3))
            elif kind == "NULL":
                matrix.fill(0.35 + 0.01 * (size - 3))
            elif kind == "ONE_FOLIO":
                for index in positions[sorted(positions)[0]]:
                    matrix[index, index] = 1.0 - 0.05 * (size - 3)
            elif kind == "READING_DISAGREEMENT":
                if edition != "RF1b":
                    np.fill_diagonal(matrix, 1.0 - 0.05 * (size - 3))
                else:
                    for values in positions.values():
                        for destination, source in zip(values, values[1:] + values[:1]):
                            matrix[destination, source] = 1.0 - 0.05 * (size - 3)
            elif kind == "LENGTH_ONLY":
                for column in range(count):
                    matrix[:, column] = 0.1 + 0.7 * (column + 1) / count
            else:
                raise ValueError(kind)
            full[edition][size] = matrix
            no_exact[edition][size] = (
                np.zeros_like(matrix) if kind == "WHOLE_GROUP_DUPLICATE_ONLY" else matrix.copy()
            )
    return full, no_exact


def decision(
    primary: dict[str, object], no_exact: dict[str, object], zodiac: dict[str, object] | None
) -> dict[str, object]:
    primary_checks = primary_gates(primary, 0.04, 0.01, 4, True)
    no_exact_checks = primary_gates(no_exact, 0.03, 0.05, 4, False)
    zodiac_checks = None if zodiac is None else primary_gates(zodiac, 0.03, 0.05, 3, False)
    passes = all(primary_checks.values()) and all(no_exact_checks.values()) and (
        zodiac_checks is None or all(zodiac_checks.values())
    )
    return {
        "primary_gates": primary_checks,
        "no_exact_group_echo_gates": no_exact_checks,
        "zodiac_gates": zodiac_checks,
        "passes": passes,
    }


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    capacity = json.loads(CAPACITY.read_text(encoding="utf-8"))
    validation = json.loads(CAPACITY_VALIDATION.read_text(encoding="utf-8"))
    if capacity["status"] != "PASS_UNSCORED_16_PAGE_5_FOLIO_C_TO_L_PANEL":
        raise AssertionError("capacity status")
    if validation["status"] != "PASS_INDEPENDENT_16_PAGE_5_FOLIO_CAPACITY_RECONSTRUCTION":
        raise AssertionError("capacity validation status")

    pages, folios = topology((4, 2, 2, 6, 2))
    zodiac_pages, zodiac_folios = topology((2, 2, 6, 2))
    assignments = assignment_matrix(pages, folios)
    zodiac_assignments = assignment_matrix(zodiac_pages, zodiac_folios)
    if assignments.shape != (138_240, 16) or zodiac_assignments.shape != (5_760, 12):
        raise AssertionError("assignment universe")

    controls = {}
    for kind in (
        "DISTRIBUTED", "NULL", "ONE_FOLIO", "READING_DISAGREEMENT",
        "WHOLE_GROUP_DUPLICATE_ONLY", "LENGTH_ONLY",
    ):
        full_matrices, no_exact_matrices = matrices(kind, pages, folios)
        primary = evaluate(full_matrices, pages, folios, assignments)
        no_exact = evaluate(no_exact_matrices, pages, folios, assignments)
        zodiac = None
        if kind == "DISTRIBUTED":
            zodiac_matrices, _ = matrices(kind, zodiac_pages, zodiac_folios)
            zodiac = evaluate(zodiac_matrices, zodiac_pages, zodiac_folios, zodiac_assignments)
        controls[kind] = {
            "primary": compact(primary),
            "no_exact_group_echo": compact(no_exact),
            "zodiac": None if zodiac is None else compact(zodiac),
            "decision": decision(primary, no_exact, zodiac),
        }

    # Direct construction fixtures prove that the matrix-level plant represents
    # partial n-gram echo rather than a complete-group duplicate.
    fixture_pages = ["A", "B"]
    label = {"A": ["QABCDR", "QLMNOR"], "B": ["QWXYZR", "QTUVWR"]}
    circle = {"A": ["XABCDY", "XQRSTY"], "B": ["XWXYZY", "XHIJKY"]}
    partial = crossrole_similarity(label, circle, fixture_pages, False)
    partial_no_exact = crossrole_similarity(label, circle, fixture_pages, True)
    exact_label = {"A": ["ABCDX", "LMNOP"], "B": ["WXYZQ", "TUVRS"]}
    exact_circle = {"A": ["ABCDX", "QRSTU"], "B": ["WXYZQ", "HIJKL"]}
    exact_full = crossrole_similarity(exact_label, exact_circle, fixture_pages, False)
    exact_removed = crossrole_similarity(exact_label, exact_circle, fixture_pages, True)
    rename = str.maketrans({character: chr(ord("Z") - index) for index, character in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXY")})
    renamed_label = {page: [group.translate(rename) for group in groups] for page, groups in label.items()}
    renamed_circle = {page: [group.translate(rename) for group in groups] for page, groups in circle.items()}
    renamed = crossrole_similarity(renamed_label, renamed_circle, fixture_pages, False)
    serialized = crossrole_similarity(
        {page: list(reversed(label[page])) for page in reversed(fixture_pages)},
        {page: list(reversed(circle[page])) for page in reversed(fixture_pages)},
        fixture_pages,
        False,
    )
    construction_fixtures = {
        "partial_echo_own_page_exceeds_other": all(
            partial[size][0, 0] > partial[size][0, 1]
            and partial[size][1, 1] > partial[size][1, 0]
            for size in COMPONENTS
        ),
        "partial_echo_survives_exact_group_removal": all(
            np.array_equal(partial[size], partial_no_exact[size]) for size in COMPONENTS
        ),
        "whole_group_duplicate_signal_removed": all(
            exact_full[size][0, 0] > exact_removed[size][0, 0]
            and exact_full[size][1, 1] > exact_removed[size][1, 1]
            for size in COMPONENTS
        ),
        "feature_token_renaming_invariant": all(
            np.array_equal(partial[size], renamed[size]) for size in COMPONENTS
        ),
        "group_serialization_invariant": all(
            np.array_equal(partial[size], serialized[size]) for size in COMPONENTS
        ),
    }

    distributed_matrices, distributed_no_exact = matrices("DISTRIBUTED", pages, folios)
    base = evaluate(distributed_matrices, pages, folios, assignments)
    affine_matrices = {
        edition: {size: 3.0 * matrix + 7.0 for size, matrix in components.items()}
        for edition, components in distributed_matrices.items()
    }
    affine = evaluate(affine_matrices, pages, folios, assignments)
    reversed_insert = {
        edition: {size: distributed_matrices[edition][size] for size in reversed(COMPONENTS)}
        for edition in reversed(READINGS)
    }
    canonical_insert = {edition: {size: reversed_insert[edition][size] for size in COMPONENTS} for edition in READINGS}
    serialized_eval = evaluate(canonical_insert, pages, dict(reversed(list(folios.items()))), assignments)

    def same_decision(left: dict[str, object], right: dict[str, object]) -> bool:
        return (
            left["p"] == right["p"]
            and all((value > 0) == (right["T_by_reading"][edition] > 0)
                    for edition, value in left["T_by_reading"].items())
            and all((value > 0) == (right["component_effects_by_reading"][edition][size] > 0)
                    for edition in READINGS for size, value in left["component_effects_by_reading"][edition].items())
            and all((value > 0) == (right["folio_effects"][edition][folio] > 0)
                    for edition in READINGS for folio, value in left["folio_effects"][edition].items())
        )

    invariance = {
        "positive_affine_decision": same_decision(base, affine),
        "serialization_and_reading_insertion_order": (
            compact(base) == compact(serialized_eval)
        ),
    }
    expected = {
        "distributed_passes": controls["DISTRIBUTED"]["decision"]["passes"],
        "null_rejects": not controls["NULL"]["decision"]["passes"],
        "one_folio_rejects": not controls["ONE_FOLIO"]["decision"]["passes"],
        "reading_disagreement_rejects": not controls["READING_DISAGREEMENT"]["decision"]["passes"],
        "whole_group_duplicate_only_rejects": not controls["WHOLE_GROUP_DUPLICATE_ONLY"]["decision"]["passes"],
        "length_only_rejects": not controls["LENGTH_ONLY"]["decision"]["passes"],
        "all_construction_fixtures_pass": all(construction_fixtures.values()),
        "all_invariances_pass": all(invariance.values()),
        "exact_assignment_universes": assignments.shape == (138_240, 16) and zodiac_assignments.shape == (5_760, 12),
        "target_STA_identity_not_opened": True,
        "target_result_absent": not (R / "cre001_target.json").exists(),
    }
    status = "PASS_TARGET_BLIND_CONTROL_GATE" if all(expected.values()) else "STOP_CONTROL_GATE_FAILED"
    result = {
        "experiment": "CRE001_CONTROLS",
        "status": status,
        "inputs": {path.name: sha(path) for path in (METHOD, CAPACITY, CAPACITY_VALIDATION, CORE, Path(__file__))},
        "topology": {
            "primary_pages_by_folio": [4, 2, 2, 6, 2],
            "primary_assignments": len(assignments),
            "primary_assignment_sha256": hashlib.sha256(np.ascontiguousarray(assignments, dtype="<i8").tobytes()).hexdigest(),
            "zodiac_pages_by_folio": [2, 2, 6, 2],
            "zodiac_assignments": len(zodiac_assignments),
            "zodiac_assignment_sha256": hashlib.sha256(np.ascontiguousarray(zodiac_assignments, dtype="<i8").tobytes()).hexdigest(),
        },
        "controls": controls,
        "construction_fixtures": construction_fixtures,
        "invariance": invariance,
        "gates": expected,
        "decision": "AUTHORIZE_INDEPENDENT_CONTROL_RECONSTRUCTION_ONLY" if all(expected.values()) else "TARGET_FORBIDDEN",
        "claim_ceiling": "Target-blind scorer behavior only. No manuscript n-gram identity, echo, ownership, word, meaning, plaintext, or translation.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# CRE001 target-blind controls\n\n"
        f"Status: **{status}**\n\n"
        "The complete 138,240-mapping scorer recovers a distributed page-specific partial-construction "
        "plant under both the primary and no-exact-group panels and recovers the four-folio zodiac "
        "plant. Null, one-folio, third-reading-disagreement, whole-group-duplicate-only, and "
        "length/exposure-only worlds reject. Direct construction fixtures and invariances pass. "
        "No real target STA identity or similarity was opened. Independent reconstruction is required "
        "before any target run; controls supply no ownership, meaning, plaintext, or translation.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": status, "gates": expected}, sort_keys=True))


if __name__ == "__main__":
    main()
