#!/usr/bin/env python3
"""Nonimporting reconstruction of CRE001 target-blind controls."""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

import numpy as np


BASE = Path(__file__).resolve().parent
R = BASE / "results"
METHOD = BASE / "CIRCLE_CROSSROLE_ECHO_METHOD.md"
CAPACITY = R / "circle_crossrole_echo_capacity.json"
CAPACITY_VALIDATION = R / "circle_crossrole_echo_capacity_validation.json"
CORE = BASE / "cre001_core.py"
RUNNER = BASE / "run_cre001_controls.py"
PRODUCTION = R / "cre001_controls.json"
PRODUCTION_REPORT = R / "cre001_controls.md"
OUT = R / "cre001_controls_validation.json"
REPORT = R / "cre001_controls_validation.md"
READINGS = ("ZL3b", "IT2a", "RF1b")
SIZES = (3, 4)
TOL = 1e-15


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def a_sha(value: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(value, dtype="<f8").tobytes()).hexdigest()


def i_sha(value: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(value, dtype="<i8").tobytes()).hexdigest()


def c_sha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def topology(sizes: tuple[int, ...]) -> tuple[list[str], dict[str, str]]:
    pages = [f"F{folio}_P{page}" for folio, size in enumerate(sizes) for page in range(size)]
    return pages, {page: page.split("_")[0] for page in pages}


def assignment_matrix(pages: list[str], folios: dict[str, str]) -> np.ndarray:
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
    return np.asarray(rows, dtype=np.int64)


def matrices(kind: str, pages: list[str], folios: dict[str, str]):
    count = len(pages)
    full = {edition: {} for edition in READINGS}
    removed = {edition: {} for edition in READINGS}
    groups = {
        folio: [index for index, page in enumerate(pages) if folios[page] == folio]
        for folio in sorted(set(folios.values()))
    }
    for edition in READINGS:
        for size in SIZES:
            matrix = np.zeros((count, count), dtype=np.float64)
            if kind in {"DISTRIBUTED", "WHOLE_GROUP_DUPLICATE_ONLY"}:
                np.fill_diagonal(matrix, 1.0 - 0.05 * (size - 3))
            elif kind == "NULL":
                matrix.fill(0.35 + 0.01 * (size - 3))
            elif kind == "ONE_FOLIO":
                for index in groups[sorted(groups)[0]]:
                    matrix[index, index] = 1.0 - 0.05 * (size - 3)
            elif kind == "READING_DISAGREEMENT":
                if edition != "RF1b":
                    np.fill_diagonal(matrix, 1.0 - 0.05 * (size - 3))
                else:
                    for values in groups.values():
                        for destination, source in zip(values, values[1:] + values[:1]):
                            matrix[destination, source] = 1.0 - 0.05 * (size - 3)
            elif kind == "LENGTH_ONLY":
                for column in range(count):
                    matrix[:, column] = 0.1 + 0.7 * (column + 1) / count
            else:
                raise AssertionError(kind)
            full[edition][size] = matrix
            removed[edition][size] = np.zeros_like(matrix) if kind == "WHOLE_GROUP_DUPLICATE_ONLY" else matrix.copy()
    return full, removed


def evaluate(matrices_by_reading, pages, folios, assignments):
    identity = int(np.flatnonzero(np.all(assignments == np.arange(len(pages)), axis=1))[0])
    folio_names = sorted(set(folios.values()))
    positions = {
        folio: [index for index, page in enumerate(pages) if folios[page] == folio]
        for folio in folio_names
    }
    weights = np.asarray([
        1.0 / (len(folio_names) * len(positions[folios[page]])) for page in pages
    ], dtype=np.float64)
    raw_orbits = np.empty((len(assignments), len(READINGS)), dtype=np.float64)
    centered_orbits = np.empty_like(raw_orbits)
    reading_T = {}
    component_effects = {edition: {} for edition in READINGS}
    page_effects = {edition: {} for edition in READINGS}
    folio_effects = {edition: {} for edition in READINGS}
    matrix_hashes = {}
    destinations = np.arange(len(pages))[None, :]
    for edition_index, edition in enumerate(READINGS):
        components = matrices_by_reading[edition]
        for size in SIZES:
            matrix_hashes[f"{edition}_k{size}"] = a_sha(components[size])
            selected = components[size][destinations, assignments]
            orbit = selected @ weights
            component_effects[edition][str(size)] = float(orbit[identity] - np.mean(orbit))
        combined = np.mean(np.stack([components[size] for size in SIZES], axis=0), axis=0)
        selected = combined[destinations, assignments]
        raw = selected @ weights
        raw_orbits[:, edition_index] = raw
        centered = raw - np.mean(raw)
        centered_orbits[:, edition_index] = centered
        reading_T[edition] = float(centered[identity])
        for page_index, page in enumerate(pages):
            candidates = positions[folios[page]]
            page_effects[edition][page] = float(
                combined[page_index, page_index] - np.mean(combined[page_index, candidates])
            )
        for folio in folio_names:
            folio_effects[edition][folio] = float(np.mean([
                page_effects[edition][pages[index]] for index in positions[folio]
            ]))
    M = min(reading_T.values())
    null_M = np.min(centered_orbits, axis=1)
    p = int(np.sum(null_M >= M - TOL)) / len(assignments)
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
        "assignment_count": len(assignments),
        "identity_assignment_index": identity,
        "T_by_reading": reading_T,
        "M": M,
        "p": p,
        "component_effects_by_reading": component_effects,
        "page_effects": page_effects,
        "folio_effects": folio_effects,
        "positive_folios_by_reading": support,
        "leave_one_folio_out_M": loo,
        "concentration_by_reading": concentration,
        "digests": {
            "assignments_sha256": i_sha(assignments),
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


def gates(result, magnitude, p_threshold, support, loo):
    value = {
        "magnitude": result["M"] >= magnitude,
        "p": result["p"] <= p_threshold,
        "all_readings_positive": all(item > 0 for item in result["T_by_reading"].values()),
        "both_components_positive_every_reading": all(
            item > 0 for edition in READINGS for item in result["component_effects_by_reading"][edition].values()
        ),
        "required_positive_folios_each_reading": all(
            item >= support for item in result["positive_folios_by_reading"].values()
        ),
    }
    if loo:
        value["all_leave_one_folio_out_above_002"] = all(item > 0.02 for item in result["leave_one_folio_out_M"].values())
        value["concentration_at_most_045"] = all(item <= 0.45 for item in result["concentration_by_reading"].values())
    return value


def control_decision(primary, removed, zodiac):
    p_gates = gates(primary, 0.04, 0.01, 4, True)
    r_gates = gates(removed, 0.03, 0.05, 4, False)
    z_gates = None if zodiac is None else gates(zodiac, 0.03, 0.05, 3, False)
    return {
        "primary_gates": p_gates,
        "no_exact_group_echo_gates": r_gates,
        "zodiac_gates": z_gates,
        "passes": all(p_gates.values()) and all(r_gates.values()) and (z_gates is None or all(z_gates.values())),
    }


def grams(group, size):
    return [group[i:i + size] for i in range(len(group) - size + 1)]


def similarity(label, circle, pages, remove):
    result = {size: np.empty((len(pages), len(pages)), dtype=np.float64) for size in SIZES}
    circle_surfaces = {page: set(circle[page]) for page in pages}
    label_counts = {}
    circle_sets = {}
    for page in pages:
        selected = [group for group in label[page] if not remove or group not in circle_surfaces[page]]
        label_counts[page] = {size: Counter(g for group in selected for g in grams(group, size)) for size in SIZES}
        circle_sets[page] = {size: {g for group in circle[page] for g in grams(group, size)} for size in SIZES}
    for i, lp in enumerate(pages):
        for j, cp in enumerate(pages):
            for size in SIZES:
                counts = label_counts[lp][size]
                result[size][i, j] = sum(n for g, n in counts.items() if g in circle_sets[cp][size]) / sum(counts.values())
    return result


def main():
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    stored = json.loads(PRODUCTION.read_text(encoding="utf-8"))
    checks = 0

    def check(value, name):
        nonlocal checks
        checks += 1
        if not value:
            raise AssertionError(name)

    check(stored["status"] == "PASS_TARGET_BLIND_CONTROL_GATE", "status")
    expected_inputs = {path.name: sha(path) for path in (METHOD, CAPACITY, CAPACITY_VALIDATION, CORE, RUNNER)}
    check(stored["inputs"] == expected_inputs, "input bindings")
    pages, folios = topology((4, 2, 2, 6, 2))
    zodiac_pages, zodiac_folios = topology((2, 2, 6, 2))
    assignments = assignment_matrix(pages, folios)
    zodiac_assignments = assignment_matrix(zodiac_pages, zodiac_folios)
    check(assignments.shape == (138_240, 16), "primary shape")
    check(zodiac_assignments.shape == (5_760, 12), "zodiac shape")
    check(len({tuple(row) for row in assignments.tolist()}) == len(assignments), "primary unique")
    check(len({tuple(row) for row in zodiac_assignments.tolist()}) == len(zodiac_assignments), "zodiac unique")
    check(stored["topology"]["primary_assignment_sha256"] == i_sha(assignments), "primary assignment digest")
    check(stored["topology"]["zodiac_assignment_sha256"] == i_sha(zodiac_assignments), "zodiac assignment digest")

    reconstructed = {}
    for kind in ("DISTRIBUTED", "NULL", "ONE_FOLIO", "READING_DISAGREEMENT", "WHOLE_GROUP_DUPLICATE_ONLY", "LENGTH_ONLY"):
        full, removed = matrices(kind, pages, folios)
        primary = evaluate(full, pages, folios, assignments)
        removal = evaluate(removed, pages, folios, assignments)
        zodiac = None
        if kind == "DISTRIBUTED":
            z_full, _ = matrices(kind, zodiac_pages, zodiac_folios)
            zodiac = evaluate(z_full, zodiac_pages, zodiac_folios, zodiac_assignments)
        reconstructed[kind] = {
            "primary": primary,
            "no_exact_group_echo": removal,
            "zodiac": zodiac,
            "decision": control_decision(primary, removal, zodiac),
        }
        check(stored["controls"][kind] == reconstructed[kind], f"complete control {kind}")

    fixture_pages = ["A", "B"]
    label = {"A": ["QABCDR", "QLMNOR"], "B": ["QWXYZR", "QTUVWR"]}
    circle = {"A": ["XABCDY", "XQRSTY"], "B": ["XWXYZY", "XHIJKY"]}
    partial = similarity(label, circle, fixture_pages, False)
    partial_removed = similarity(label, circle, fixture_pages, True)
    exact_label = {"A": ["ABCDX", "LMNOP"], "B": ["WXYZQ", "TUVRS"]}
    exact_circle = {"A": ["ABCDX", "QRSTU"], "B": ["WXYZQ", "HIJKL"]}
    exact_full = similarity(exact_label, exact_circle, fixture_pages, False)
    exact_removed = similarity(exact_label, exact_circle, fixture_pages, True)
    rename = str.maketrans({character: chr(ord("Z") - index) for index, character in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXY")})
    renamed = similarity(
        {page: [group.translate(rename) for group in rows] for page, rows in label.items()},
        {page: [group.translate(rename) for group in rows] for page, rows in circle.items()},
        fixture_pages, False,
    )
    serialized = similarity(
        {page: list(reversed(label[page])) for page in reversed(fixture_pages)},
        {page: list(reversed(circle[page])) for page in reversed(fixture_pages)},
        fixture_pages, False,
    )
    fixtures = {
        "partial_echo_own_page_exceeds_other": all(partial[size][0, 0] > partial[size][0, 1] and partial[size][1, 1] > partial[size][1, 0] for size in SIZES),
        "partial_echo_survives_exact_group_removal": all(np.array_equal(partial[size], partial_removed[size]) for size in SIZES),
        "whole_group_duplicate_signal_removed": all(exact_full[size][0, 0] > exact_removed[size][0, 0] and exact_full[size][1, 1] > exact_removed[size][1, 1] for size in SIZES),
        "feature_token_renaming_invariant": all(np.array_equal(partial[size], renamed[size]) for size in SIZES),
        "group_serialization_invariant": all(np.array_equal(partial[size], serialized[size]) for size in SIZES),
    }
    check(stored["construction_fixtures"] == fixtures, "construction fixtures")
    distributed, _ = matrices("DISTRIBUTED", pages, folios)
    base = evaluate(distributed, pages, folios, assignments)
    affine = evaluate({
        edition: {size: 3.0 * matrix + 7.0 for size, matrix in components.items()}
        for edition, components in distributed.items()
    }, pages, folios, assignments)
    reverse_insert = {
        edition: {size: distributed[edition][size] for size in reversed(SIZES)}
        for edition in reversed(READINGS)
    }
    serialized_eval = evaluate({
        edition: {size: reverse_insert[edition][size] for size in SIZES} for edition in READINGS
    }, pages, dict(reversed(list(folios.items()))), assignments)

    def same_decision(left, right):
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
        "serialization_and_reading_insertion_order": base == serialized_eval,
    }
    check(stored["invariance"] == invariance, "invariance reconstruction")
    expected_gates = {
        "distributed_passes": reconstructed["DISTRIBUTED"]["decision"]["passes"],
        "null_rejects": not reconstructed["NULL"]["decision"]["passes"],
        "one_folio_rejects": not reconstructed["ONE_FOLIO"]["decision"]["passes"],
        "reading_disagreement_rejects": not reconstructed["READING_DISAGREEMENT"]["decision"]["passes"],
        "whole_group_duplicate_only_rejects": not reconstructed["WHOLE_GROUP_DUPLICATE_ONLY"]["decision"]["passes"],
        "length_only_rejects": not reconstructed["LENGTH_ONLY"]["decision"]["passes"],
        "all_construction_fixtures_pass": all(fixtures.values()),
        "all_invariances_pass": all(invariance.values()),
        "exact_assignment_universes": assignments.shape == (138_240, 16) and zodiac_assignments.shape == (5_760, 12),
        "target_STA_identity_not_opened": True,
        "target_result_absent": not (R / "cre001_target.json").exists(),
    }
    check(stored["gates"] == expected_gates, "all gates")
    check(stored["decision"] == "AUTHORIZE_INDEPENDENT_CONTROL_RECONSTRUCTION_ONLY", "decision")
    check(not (R / "cre001_target.json").exists(), "target absent")
    validation = {
        "experiment": "CRE001_CONTROL_VALIDATION",
        "status": "PASS_INDEPENDENT_COMPLETE_CONTROL_RECONSTRUCTION",
        "checks": checks,
        "bindings": {
            "production_sha256": sha(PRODUCTION),
            "production_report_sha256": sha(PRODUCTION_REPORT),
            "validator_sha256": sha(Path(__file__)),
        },
        "reconstructed": {
            "control_worlds": len(reconstructed),
            "primary_assignments": len(assignments),
            "zodiac_assignments": len(zodiac_assignments),
            "complete_control_records_exact": len(reconstructed),
        },
        "target_STA_identity_opened": False,
        "decision": "AUTHORIZE_ONE_SEPARATELY_HASH_FROZEN_TARGET_RUN",
        "claim_ceiling": stored["claim_ceiling"],
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# CRE001 control validation\n\n"
        "Status: **PASS_INDEPENDENT_COMPLETE_CONTROL_RECONSTRUCTION**\n\n"
        f"A nonimporting implementation passed {checks} aggregate checks and exactly reconstructed "
        "all six complete 138,240-assignment control records, the 5,760-assignment zodiac plant, "
        "assignment and numeric digests, construction fixtures, decisions, and bindings. The real "
        "STA target remained absent. One separately hash-frozen target run is authorized; no echo, "
        "ownership, word, meaning, plaintext, or translation exists yet.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": validation["status"], "checks": checks}, sort_keys=True))


if __name__ == "__main__":
    main()
