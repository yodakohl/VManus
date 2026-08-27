#!/usr/bin/env python3
"""Independently validate the GDT564 state-context selector atlas."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt564_state_context_selector_atlas"
OUT = BASE / "artifacts"
RUNNER = BASE / "src/run.py"
SOURCE = ROOT / "experiments/yolo/gdt563_complete_state_microphrase_edition/artifacts/gdt563_1656_complete_state_microphrases.tsv"
VALIDATION_OUT = OUT / "gdt564_validation.json"

ARTIFACTS = {
    "gdt564_402_recipe_selector_routes.tsv": OUT / "gdt564_402_recipe_selector_routes.tsv",
    "gdt564_1010_selector_candidate_tests.tsv": OUT / "gdt564_1010_selector_candidate_tests.tsv",
    "gdt564_415_observed_selector_cells.tsv": OUT / "gdt564_415_observed_selector_cells.tsv",
    "gdt564_10_candidate_selector_profiles.tsv": OUT / "gdt564_10_candidate_selector_profiles.tsv",
    "gdt564_4_portable_route_profiles.tsv": OUT / "gdt564_4_portable_route_profiles.tsv",
    "gdt564_5_empirical_minimal_classes.tsv": OUT / "gdt564_5_empirical_minimal_classes.tsv",
    "GDT564_CONTEXT_SELECTOR_BOOK.md": OUT / "GDT564_CONTEXT_SELECTOR_BOOK.md",
    "gdt564_result.json": OUT / "gdt564_result.json",
}

PHRASE = "owner_free_microphrase_de"
ACTION = "effective_action_roots"
ARGUMENT = "effective_argument_roots"
ARGUMENT_ROOTS = {"Y", "AIIN", "AIN", "OR"}

FIXED = "FIXED_RECIPE"
ARG_ROUTE = "WRITTEN_ACTION__SELECT_ARGUMENT"
ACTION_ROUTE = "WRITTEN_ARGUMENT__SELECT_ACTION"
PAIR_ROUTE = "OPEN_FRAME__SELECT_ACTION_ARGUMENT"
ROUTE_FIELDS = {FIXED: (), ARG_ROUTE: (ARGUMENT,), ACTION_ROUTE: (ACTION,), PAIR_ROUTE: (ACTION, ARGUMENT)}

CANDIDATES = [
    ("RECIPE_ONLY", ()), ("EFFECTIVE_ACTION", (ACTION,)),
    ("EFFECTIVE_ARGUMENT", (ARGUMENT,)), ("ACTION_ARGUMENT", (ACTION, ARGUMENT)),
    ("RESOLUTION_MODE", ("resolution_mode",)),
    ("SOURCE_LAYER", ("microphrase_source_layer",)),
    ("STATEMENT_POSITION", ("statement_position",)),
    ("REGISTER", ("register",)), ("PHYSICAL_PAGE", ("physical_page",)),
    ("COHORT", ("cohort",)),
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split(rows: list[dict[str, str]], fields: tuple[str, ...]) -> dict[tuple[str, ...], list[dict[str, str]]]:
    out: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        out[tuple(row[field] for field in fields)].append(row)
    return dict(out)


def metrics(rows: list[dict[str, str]], fields: tuple[str, ...]) -> dict[str, int | bool]:
    cells = split(rows, fields)
    ambiguous = sum(len({row[PHRASE] for row in members}) > 1 for members in cells.values())
    modal = sum(Counter(row[PHRASE] for row in members).most_common(1)[0][1] for members in cells.values())
    return {"resolved": ambiguous == 0, "cells": len(cells), "ambiguous": ambiguous, "modal": modal}


def has_written_argument(recipe: str) -> bool:
    return bool(ARGUMENT_ROOTS.intersection(recipe.split("+")))


def expected_route(rows: list[dict[str, str]]) -> str:
    if len({row[PHRASE] for row in rows}) == 1:
        return FIXED
    if rows[0]["written_action_roots"] != "NONE":
        return ARG_ROUTE
    if has_written_argument(rows[0]["recipe"]):
        return ACTION_ROUTE
    return PAIR_ROUTE


def expected_minimal_class(rows: list[dict[str, str]]) -> tuple[str, str]:
    action_ok = bool(metrics(rows, (ACTION,))["resolved"])
    argument_ok = bool(metrics(rows, (ARGUMENT,))["resolved"])
    mode_ok = bool(metrics(rows, ("resolution_mode",))["resolved"])
    if action_ok and argument_ok:
        return "EITHER_ACTION_OR_ARGUMENT", "EFFECTIVE_ARGUMENT"
    if argument_ok and mode_ok:
        return "ARGUMENT_OR_RESOLUTION_MODE", "EFFECTIVE_ARGUMENT"
    if argument_ok:
        return "ARGUMENT_ONLY", "EFFECTIVE_ARGUMENT"
    if action_ok:
        return "ACTION_ONLY", "EFFECTIVE_ACTION"
    return "ACTION_ARGUMENT_REQUIRED", "ACTION_ARGUMENT"


def expected_key(fields: tuple[str, ...], values: tuple[str, ...]) -> str:
    labels = {ACTION: "ACTION", ARGUMENT: "ARGUMENT"}
    return " | ".join(f"{labels[field]}={value}" for field, value in zip(fields, values))


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    source = read_tsv(SOURCE)
    recipe_art = read_tsv(ARTIFACTS["gdt564_402_recipe_selector_routes.tsv"])
    tests_art = read_tsv(ARTIFACTS["gdt564_1010_selector_candidate_tests.tsv"])
    cells_art = read_tsv(ARTIFACTS["gdt564_415_observed_selector_cells.tsv"])
    candidates_art = read_tsv(ARTIFACTS["gdt564_10_candidate_selector_profiles.tsv"])
    routes_art = read_tsv(ARTIFACTS["gdt564_4_portable_route_profiles.tsv"])
    minimal_art = read_tsv(ARTIFACTS["gdt564_5_empirical_minimal_classes.tsv"])
    result = json.loads(ARTIFACTS["gdt564_result.json"].read_text(encoding="utf-8"))

    by_recipe: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in source:
        by_recipe[row["recipe"]].append(row)
    variable = {recipe: rows for recipe, rows in by_recipe.items() if len({row[PHRASE] for row in rows}) > 1}
    fixed = {recipe: rows for recipe, rows in by_recipe.items() if len({row[PHRASE] for row in rows}) == 1}

    check("source_count", len(source) == 1656, len(source))
    check("source_event_ids_unique", len({row["event_id"] for row in source}) == 1656, len({row["event_id"] for row in source}))
    check("sealed_pages_absent", not {row["physical_page"] for row in source}.intersection({"f84", "f84r"}), sorted({row["physical_page"] for row in source}.intersection({"f84", "f84r"})))
    check("source_completion_guards", all(row["all_written_atoms_retained"] == "YES" and row["all_written_action_slots_retained"] == "YES" for row in source), None)
    check("source_recipe_partition", len(by_recipe) == 402 and len(fixed) == 301 and len(variable) == 101, [len(by_recipe), len(fixed), len(variable)])
    check("source_event_partition", sum(map(len, fixed.values())) == 379 and sum(map(len, variable.values())) == 1277, [sum(map(len, fixed.values())), sum(map(len, variable.values()))])
    check("artifact_counts", [len(recipe_art), len(tests_art), len(cells_art), len(candidates_art), len(routes_art), len(minimal_art)] == [402, 1010, 415, 10, 4, 5], [len(recipe_art), len(tests_art), len(cells_art), len(candidates_art), len(routes_art), len(minimal_art)])

    recipe_lookup = {row["recipe"]: row for row in recipe_art}
    check("recipe_keys_exact", set(recipe_lookup) == set(by_recipe) and len(recipe_lookup) == len(recipe_art), [len(recipe_lookup), len(set(by_recipe) - set(recipe_lookup))])
    recipe_errors = []
    expected_route_counts = Counter()
    expected_route_events = Counter()
    expected_route_cells = Counter()
    expected_minimal_counts = Counter()
    expected_canonical_counts = Counter()
    for recipe, members in by_recipe.items():
        row = recipe_lookup[recipe]
        route = expected_route(members)
        fields = ROUTE_FIELDS[route]
        cells = split(members, fields)
        phrase_count = len({member[PHRASE] for member in members})
        expected_route_counts[route] += 1
        expected_route_events[route] += len(members)
        expected_route_cells[route] += len(cells)
        expected_equivalence, expected_canonical = ("NOT_NEEDED", "NONE") if phrase_count == 1 else expected_minimal_class(members)
        if phrase_count > 1:
            expected_minimal_counts[expected_equivalence] += 1
            expected_canonical_counts[expected_canonical] += 1
        expected = {
            "event_count": str(len(members)),
            "distinct_microphrase_count": str(phrase_count),
            "recurrence_status": "SINGLETON" if len(members) == 1 else "RECURRENT",
            "variability_status": "FIXED" if phrase_count == 1 else "CONTEXT_VARIABLE",
            "written_action_status": "PRESENT" if members[0]["written_action_roots"] != "NONE" else "ABSENT",
            "written_argument_status": "PRESENT" if has_written_argument(recipe) else "ABSENT",
            "portable_route": route,
            "portable_selector_fields": "+".join(fields) if fields else "NONE",
            "empirical_minimal_equivalence_class": expected_equivalence,
            "canonical_empirical_selector": expected_canonical,
            "selector_cell_count": str(len(cells)),
            "distinct_effective_action_count": str(len({member[ACTION] for member in members})),
            "distinct_effective_argument_count": str(len({member[ARGUMENT] for member in members})),
        }
        if any(row[key] != value for key, value in expected.items()):
            recipe_errors.append((recipe, {key: [row[key], value] for key, value in expected.items() if row[key] != value}))
        if any(len({member[PHRASE] for member in group}) != 1 for group in cells.values()):
            recipe_errors.append((recipe, "portable route ambiguous"))
    check("all_402_recipe_routes_reconstructed", not recipe_errors, recipe_errors[:10])
    check("portable_route_recipe_counts", expected_route_counts == Counter({FIXED: 301, ARG_ROUTE: 54, ACTION_ROUTE: 15, PAIR_ROUTE: 32}), dict(expected_route_counts))
    check("portable_route_event_counts", expected_route_events == Counter({FIXED: 379, ARG_ROUTE: 638, ACTION_ROUTE: 206, PAIR_ROUTE: 433}), dict(expected_route_events))
    check("portable_route_cell_counts", expected_route_cells == Counter({FIXED: 301, ARG_ROUTE: 144, ACTION_ROUTE: 76, PAIR_ROUTE: 195}), dict(expected_route_cells))
    check("empirical_minimal_class_counts", expected_minimal_counts == Counter({"ARGUMENT_ONLY": 49, "ACTION_ONLY": 26, "ACTION_ARGUMENT_REQUIRED": 15, "EITHER_ACTION_OR_ARGUMENT": 6, "ARGUMENT_OR_RESOLUTION_MODE": 5}), dict(expected_minimal_counts))
    check("canonical_selector_counts", expected_canonical_counts == Counter({"EFFECTIVE_ARGUMENT": 60, "EFFECTIVE_ACTION": 26, "ACTION_ARGUMENT": 15}), dict(expected_canonical_counts))

    test_lookup = {(row["recipe"], row["candidate"]): row for row in tests_art}
    expected_test_keys = {(recipe, candidate) for recipe in variable for candidate, _ in CANDIDATES}
    check("candidate_test_grid_exact", set(test_lookup) == expected_test_keys and len(test_lookup) == len(tests_art), [len(test_lookup), len(expected_test_keys - set(test_lookup))])
    candidate_errors = []
    aggregate = defaultdict(Counter)
    for recipe, members in variable.items():
        for candidate, fields in CANDIDATES:
            stat = metrics(members, fields)
            row = test_lookup[(recipe, candidate)]
            expected = {
                "event_count": str(len(members)),
                "distinct_microphrase_count": str(len({member[PHRASE] for member in members})),
                "selector_cell_count": str(stat["cells"]),
                "ambiguous_cell_count": str(stat["ambiguous"]),
                "resolved_status": "RESOLVED" if stat["resolved"] else "AMBIGUOUS",
                "modal_hit_count": str(stat["modal"]),
            }
            if any(row[key] != value for key, value in expected.items()):
                candidate_errors.append((recipe, candidate))
            aggregate[candidate]["recipes"] += 1
            aggregate[candidate]["resolved_recipes"] += int(bool(stat["resolved"]))
            aggregate[candidate]["resolved_events"] += len(members) if stat["resolved"] else 0
            aggregate[candidate]["cells"] += int(stat["cells"])
            aggregate[candidate]["ambiguous"] += int(stat["ambiguous"])
            aggregate[candidate]["modal"] += int(stat["modal"])
            aggregate[candidate]["events"] += len(members)
    check("all_1010_candidate_tests_reconstructed", not candidate_errors, candidate_errors[:20])

    profile_lookup = {row["candidate"]: row for row in candidates_art}
    check("candidate_profile_keys_exact", set(profile_lookup) == {name for name, _ in CANDIDATES}, sorted(set(profile_lookup)))
    profile_errors = []
    for candidate, fields in CANDIDATES:
        row = profile_lookup[candidate]
        values = aggregate[candidate]
        expected = {
            "selector_fields": "+".join(fields) if fields else "NONE",
            "variable_recipe_count": str(values["recipes"]),
            "resolved_recipe_count": str(values["resolved_recipes"]),
            "resolved_event_count": str(values["resolved_events"]),
            "selector_cell_count": str(values["cells"]),
            "ambiguous_cell_count": str(values["ambiguous"]),
            "modal_hit_count": str(values["modal"]),
            "event_count": str(values["events"]),
        }
        if any(row[key] != value for key, value in expected.items()):
            profile_errors.append((candidate, expected, row))
    check("all_10_candidate_profiles_reconstructed", not profile_errors, profile_errors[:3])
    check("recipe_only_baseline_exact", aggregate["RECIPE_ONLY"] == Counter({"events": 1277, "modal": 566, "cells": 101, "ambiguous": 101, "recipes": 101}), dict(aggregate["RECIPE_ONLY"]))
    check("action_selector_exact", aggregate["EFFECTIVE_ACTION"]["resolved_recipes"] == 32 and aggregate["EFFECTIVE_ACTION"]["resolved_events"] == 254 and aggregate["EFFECTIVE_ACTION"]["modal"] == 932, dict(aggregate["EFFECTIVE_ACTION"]))
    check("argument_selector_exact", aggregate["EFFECTIVE_ARGUMENT"]["resolved_recipes"] == 60 and aggregate["EFFECTIVE_ARGUMENT"]["resolved_events"] == 652 and aggregate["EFFECTIVE_ARGUMENT"]["modal"] == 872, dict(aggregate["EFFECTIVE_ARGUMENT"]))
    check("action_argument_selector_complete", aggregate["ACTION_ARGUMENT"]["resolved_recipes"] == 101 and aggregate["ACTION_ARGUMENT"]["resolved_events"] == 1277 and aggregate["ACTION_ARGUMENT"]["cells"] == 415 and aggregate["ACTION_ARGUMENT"]["ambiguous"] == 0 and aggregate["ACTION_ARGUMENT"]["modal"] == 1277, dict(aggregate["ACTION_ARGUMENT"]))
    check("source_layer_not_selector", aggregate["SOURCE_LAYER"]["resolved_recipes"] == 0 and aggregate["SOURCE_LAYER"]["modal"] == 566, dict(aggregate["SOURCE_LAYER"]))

    route_profile_lookup = {row["portable_route"]: row for row in routes_art}
    route_profile_errors = []
    for route in ROUTE_FIELDS:
        row = route_profile_lookup.get(route, {})
        expected = {
            "selector_fields": "+".join(ROUTE_FIELDS[route]) if ROUTE_FIELDS[route] else "NONE",
            "recipe_count": str(expected_route_counts[route]),
            "event_count": str(expected_route_events[route]),
            "selector_cell_count": str(expected_route_cells[route]),
            "distinct_recipe_microphrase_count": str(expected_route_cells[route]),
        }
        if any(row.get(key) != value for key, value in expected.items()):
            route_profile_errors.append((route, expected, row))
    check("four_route_profiles_exact", len(route_profile_lookup) == 4 and not route_profile_errors, route_profile_errors)

    expected_cell_map: dict[tuple[str, str], list[dict[str, str]]] = {}
    for recipe, members in variable.items():
        fields = ROUTE_FIELDS[expected_route(members)]
        for values, group in split(members, fields).items():
            expected_cell_map[(recipe, expected_key(fields, values))] = group
    cell_lookup = {(row["recipe"], row["selector_key"]): row for row in cells_art}
    check("selector_cell_keys_exact", set(cell_lookup) == set(expected_cell_map) and len(cell_lookup) == len(cells_art), [len(cell_lookup), len(set(expected_cell_map) - set(cell_lookup))])
    check("selector_cell_ids_sequential", [row["selector_cell_id"] for row in cells_art] == [f"GDT564-C{i:04d}" for i in range(1, 416)], [cells_art[0]["selector_cell_id"], cells_art[-1]["selector_cell_id"]])
    cell_errors = []
    covered_events = []
    for key, members in expected_cell_map.items():
        row = cell_lookup[key]
        covered_events.extend(member["event_id"] for member in members)
        expected = {
            "portable_route": expected_route(variable[key[0]]),
            "owner_free_microphrase_de": members[0][PHRASE],
            "event_count": str(len(members)),
            "physical_page_count": str(len({member["physical_page"] for member in members})),
            "register_count": str(len({member["register"] for member in members})),
            "cohort_count": str(len({member["cohort"] for member in members})),
            "cross_page_status": "CROSS_PAGE" if len({member["physical_page"] for member in members}) > 1 else "ONE_PAGE",
        }
        if len({member[PHRASE] for member in members}) != 1 or any(row[field] != value for field, value in expected.items()):
            cell_errors.append((key, expected, row))
    check("all_415_selector_cells_reconstructed", not cell_errors, cell_errors[:5])
    expected_variable_events = {row["event_id"] for members in variable.values() for row in members}
    check("selector_cells_partition_all_variable_events", len(covered_events) == 1277 and len(set(covered_events)) == 1277 and set(covered_events) == expected_variable_events, [len(covered_events), len(set(covered_events))])
    recurrent_cells = [members for members in expected_cell_map.values() if len(members) > 1]
    check("recurrent_cell_counts", len(recurrent_cells) == 183 and sum(map(len, recurrent_cells)) == 1045, [len(recurrent_cells), sum(map(len, recurrent_cells))])
    check("cross_context_cell_counts", [sum(len({row["physical_page"] for row in members}) > 1 for members in expected_cell_map.values()), sum(len({row["register"] for row in members}) > 1 for members in expected_cell_map.values()), sum(len({row["cohort"] for row in members}) > 1 for members in expected_cell_map.values())] == [172, 123, 47], None)
    check("maximum_cell_support", max(map(len, expected_cell_map.values())) == 64, max(map(len, expected_cell_map.values())))

    minimal_lookup = {row["minimal_equivalence_class"]: row for row in minimal_art}
    minimal_errors = []
    for name, expected_count in expected_minimal_counts.items():
        members = [(recipe, rows) for recipe, rows in variable.items() if expected_minimal_class(rows)[0] == name]
        row = minimal_lookup.get(name, {})
        expected = {
            "recipe_count": str(expected_count),
            "event_count": str(sum(len(rows) for _, rows in members)),
            "distinct_recipe_microphrase_count": str(sum(len({item[PHRASE] for item in rows}) for _, rows in members)),
        }
        if any(row.get(key) != value for key, value in expected.items()):
            minimal_errors.append((name, expected, row))
    check("five_minimal_profiles_exact", len(minimal_lookup) == 5 and not minimal_errors, minimal_errors)

    expected_result = {
        "source_state_card_count": 1656,
        "exact_recipe_count": 402,
        "fixed_recipe_count": 301,
        "fixed_recipe_event_count": 379,
        "context_variable_recipe_count": 101,
        "context_variable_event_count": 1277,
        "observed_variable_selector_cell_count": 415,
        "observed_variable_recipe_microphrase_count": 415,
        "complete_recipe_plus_context_cell_count": 716,
        "action_argument_resolved_recipe_count": 101,
        "action_argument_ambiguous_cell_count": 0,
        "recipe_only_modal_hit_count": 566,
        "effective_action_modal_hit_count": 932,
        "effective_argument_modal_hit_count": 872,
        "action_argument_modal_hit_count": 1277,
        "recurrent_selector_cell_count": 183,
        "recurrent_selector_cell_event_count": 1045,
        "cross_page_selector_cell_count": 172,
        "cross_register_selector_cell_count": 123,
        "cross_cohort_selector_cell_count": 47,
        "maximum_selector_cell_event_count": 64,
    }
    check("result_metrics_exact", all(result.get(key) == value for key, value in expected_result.items()), {key: result.get(key) for key in expected_result})
    check("result_status_exact", result.get("status") == "PASS_402_RECIPE_SELECTOR_ATLAS__101_VARIABLE_RECIPES_RESOLVED__415_CONTEXT_CELLS__ZERO_AMBIGUITY__THREE_PORTABLE_ROUTES", result.get("status"))
    check("result_boolean_guards", result.get("all_portable_selector_cells_phrase_unique") is True and result.get("owner_page_or_register_required") is False, [result.get("all_portable_selector_cells_phrase_unique"), result.get("owner_page_or_register_required")])
    check("zero_scope_mutation", all(result.get(key) == 0 for key in ("new_pages", "new_surfaces", "new_recipes", "new_root_values")), {key: result.get(key) for key in ("new_pages", "new_surfaces", "new_recipes", "new_root_values")})
    check("input_hash_exact", result.get("input_sha256", {}).get("gdt563_complete_state_microphrases") == sha256(SOURCE), result.get("input_sha256"))

    book = ARTIFACTS["GDT564_CONTEXT_SELECTOR_BOOK.md"].read_text(encoding="utf-8")
    needles = ("301 Rezepte", "101 variablen", "415 beobachtete", "716 vollständige", "60", "26", "15", "null mehrdeutige")
    check("book_core_findings_present", all(needle in book for needle in needles), [needle for needle in needles if needle not in book])

    before = {name: sha256(path) for name, path in ARTIFACTS.items()}
    replay = subprocess.run([sys.executable, str(RUNNER)], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    after = {name: sha256(path) for name, path in ARTIFACTS.items()}
    check("deterministic_replay_exit", replay.returncode == 0, replay.stderr)
    check("deterministic_artifact_hashes", before == after, {name: [before[name], after[name]] for name in before if before[name] != after[name]})

    payload = {
        "status": "PASS" if all(item["passed"] for item in checks) else "FAIL",
        "check_count": len(checks),
        "passed_count": sum(item["passed"] for item in checks),
        "failed_count": sum(not item["passed"] for item in checks),
        "input_sha256": {"gdt563_complete_state_microphrases": sha256(SOURCE)},
        "artifact_sha256": {name: sha256(path) for name, path in ARTIFACTS.items()},
        "checks": checks,
    }
    VALIDATION_OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
