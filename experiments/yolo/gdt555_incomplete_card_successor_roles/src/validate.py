#!/usr/bin/env python3
"""Validate GDT555 gap roles against exact GDT539 source pointers."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt555_incomplete_card_successor_roles"
OUT = BASE / "artifacts"
G539 = ROOT / "experiments/yolo/gdt539_four_page_contextual_statement_edition/artifacts"
G554 = ROOT / "experiments/yolo/gdt554_statement_semantic_template_audit/artifacts"

SOURCE = G539 / "gdt539_546_contextual_prose_events.tsv"
EVENT_INPUT = G554 / "gdt554_546_event_semantic_templates.tsv"
STATEMENT_INPUT = G554 / "gdt554_78_statement_template_atlas.tsv"
UNION = OUT / "gdt555_64_unique_gap_events.tsv"
ACTIONLESS = OUT / "gdt555_16_actionless_successor_roles.tsv"
ARGUMENTLESS = OUT / "gdt555_57_argumentless_successor_roles.tsv"
LINKS = OUT / "gdt555_exact_initializer_links.tsv"
PROFILES = OUT / "gdt555_gap_surface_role_profiles.tsv"
SUMMARY = OUT / "gdt555_role_summary.tsv"
BOOK = OUT / "GDT555_GAP_ROLE_BOOK.md"
RESULT = OUT / "gdt555_result.json"
VALIDATION = OUT / "gdt555_validation.json"
RUNNER = BASE / "src/run.py"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    source = read_tsv(SOURCE)
    event_input = read_tsv(EVENT_INPUT)
    statement_input = read_tsv(STATEMENT_INPUT)
    union = read_tsv(UNION)
    actionless = read_tsv(ACTIONLESS)
    argumentless = read_tsv(ARGUMENTLESS)
    links = read_tsv(LINKS)
    profiles = read_tsv(PROFILES)
    summary = read_tsv(SUMMARY)
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    book = BOOK.read_text(encoding="utf-8")

    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    check("input_counts", (len(source), len(event_input), len(statement_input)) == (546, 546, 78), [len(source), len(event_input), len(statement_input)])
    source_by_id = {row["event_id"]: row for row in source}
    input_by_id = {row["event_id"]: row for row in event_input}
    check("input_event_identity_exact", set(source_by_id) == set(input_by_id), len(source_by_id))

    expected_actionless = {row["event_id"] for row in event_input if row["resolved_action_roots"] == "NONE"}
    expected_argumentless = {row["event_id"] for row in event_input if row["resolved_argument_roots"] == "NONE"}
    expected_overlap = expected_actionless & expected_argumentless
    expected_union = expected_actionless | expected_argumentless
    check("gap_partition_recomputed", (len(expected_actionless), len(expected_argumentless), len(expected_overlap), len(expected_union)) == (16, 57, 9, 64), [len(expected_actionless), len(expected_argumentless), len(expected_overlap), len(expected_union)])
    check("output_gap_counts", (len(union), len(actionless), len(argumentless)) == (64, 16, 57), [len(union), len(actionless), len(argumentless)])
    check("union_set_exact", {row["event_id"] for row in union} == expected_union, [])
    check("actionless_set_exact", {row["event_id"] for row in actionless} == expected_actionless, [])
    check("argumentless_set_exact", {row["event_id"] for row in argumentless} == expected_argumentless, [])
    check("overlap_flags_exact", {row["event_id"] for row in union if row["overlap_gap"] == "YES"} == expected_overlap, [])

    check("all_recipes_macros_clauses_retained", all(row["final_recipe"] == input_by_id[row["event_id"]]["final_recipe"] and row["portable_semantic_macro"] == input_by_id[row["event_id"]]["portable_semantic_macro"] and row["current_clause_de"] == input_by_id[row["event_id"]]["contextual_clause_de"] for row in union), [])
    check("all_gap_roles_populated", all(row["primary_gap_role"] and row["primary_gap_role_de"] for row in union), [])
    check("all_retention_guards_exact", all(row["retention"] == "EXACT_GDT554_RECIPE_MACRO_AND_CLAUSE_RETAINED" for row in union), [])

    link_errors: list[str] = []
    for link in links:
        source_row = source_by_id[link["source_event_id"]]
        consumer = source_by_id[link["consumer_event_id"]]
        pointer_field = (
            "inherited_action_source_event_id"
            if link["state_dimension"] == "ACTION_STATE"
            else "inherited_argument_source_event_id"
        )
        distance = int(consumer["card_ordinal_in_statement"]) - int(source_row["card_ordinal_in_statement"])
        if consumer[pointer_field] != source_row["event_id"]:
            link_errors.append(link["link_ordinal"] + ":pointer")
        if consumer["statement_id"] != source_row["statement_id"]:
            link_errors.append(link["link_ordinal"] + ":statement")
        if distance != int(link["card_distance"]) or distance <= 0:
            link_errors.append(link["link_ordinal"] + ":distance")
        if (distance == 1) != (link["immediate_successor"] == "YES"):
            link_errors.append(link["link_ordinal"] + ":immediate")
    check("all_initializer_links_exact_source_pointers", not link_errors, link_errors)
    check("initializer_link_counts", (len(links), sum(row["immediate_successor"] == "YES" for row in links), sum(row["immediate_successor"] == "NO" for row in links)) == (22, 11, 11), [len(links), sum(row["immediate_successor"] == "YES" for row in links), sum(row["immediate_successor"] == "NO" for row in links)])
    check("initializer_dimension_counts", Counter(row["state_dimension"] for row in links) == Counter({"ACTION_STATE": 15, "ARGUMENT_STATE": 7}), Counter(row["state_dimension"] for row in links))
    check("initializer_max_distance_five", max(int(row["card_distance"]) for row in links) == 5, max(int(row["card_distance"]) for row in links))
    check("all_links_same_statement", all(row["same_statement"] == "YES" and row["source_pointer_exact"] == "YES" for row in links), [])
    check("paired_readings_only_join_existing_clauses", all(row["paired_reading_de"] == input_by_id[row["source_event_id"]]["contextual_clause_de"] + " → " + input_by_id[row["consumer_event_id"]]["contextual_clause_de"] for row in links), [])

    initializer_sources = {row["source_event_id"] for row in links}
    action_initializer_ids = {row["event_id"] for row in argumentless if row["argumentless_role"] == "ACTION_INITIALIZER"}
    argument_initializer_ids = {row["event_id"] for row in actionless if row["actionless_role"] == "ARGUMENT_INITIALIZER"}
    check("initializer_source_partition", initializer_sources == action_initializer_ids | argument_initializer_ids and not action_initializer_ids & argument_initializer_ids, [len(initializer_sources), len(action_initializer_ids), len(argument_initializer_ids)])
    check("initializer_event_counts", (len(action_initializer_ids), len(argument_initializer_ids)) == (8, 3), [len(action_initializer_ids), len(argument_initializer_ids)])
    check("every_initializer_has_immediate_consumer", all(any(link["source_event_id"] == event_id and link["immediate_successor"] == "YES" for link in links) for event_id in initializer_sources), [])

    unique_role_counts = Counter(row["primary_gap_role"] for row in union)
    expected_roles = Counter({
        "OBJECTLESS_CLOSURE_OR_STATEMENT_BOUNDARY": 19,
        "OBJECTLESS_ACTION_BEFORE_EXPLICIT_RESET": 17,
        "ACTION_INITIALIZER": 8,
        "PRE_ACTION_SCOPE_PROLOGUE": 7,
        "CARRIED_ACTION_OBJECTLESS_CONTROL": 4,
        "ARGUMENT_INITIALIZER": 3,
        "CLOSURE_BOUNDARY": 3,
        "NOMINAL_CONTROL_PROLOGUE": 2,
        "CONTINUATION_PROLOGUE": 1,
    })
    check("unique_role_distribution_exact", unique_role_counts == expected_roles, unique_role_counts)
    check("role_summary_partitions", sum(int(row["event_count"]) for row in summary if row["gap_dimension"] == "UNIQUE_GAP") == 64 and sum(int(row["event_count"]) for row in summary if row["gap_dimension"] == "ACTIONLESS") == 16 and sum(int(row["event_count"]) for row in summary if row["gap_dimension"] == "ARGUMENTLESS") == 57, [sum(int(row["event_count"]) for row in summary if row["gap_dimension"] == dimension) for dimension in ("UNIQUE_GAP", "ACTIONLESS", "ARGUMENTLESS")])

    check("surface_profile_count", len(profiles) == 50 and {row["surface"] for row in profiles} == {row["surface"] for row in union}, len(profiles))
    multi_role = [row for row in profiles if int(row["primary_role_count"]) > 1]
    check("only_ol_has_context_role_variation", [row["surface"] for row in multi_role] == ["ol"], [row["surface"] for row in multi_role])
    check("profile_event_counts_sum", sum(int(row["gap_event_count"]) for row in profiles) == 64, sum(int(row["gap_event_count"]) for row in profiles))

    expected_result = {
        "status": "PASS_64_UNIQUE_GAPS_CLASSIFIED__EXACT_SOURCE_POINTERS_ONLY",
        "actionless_event_count": 16,
        "argumentless_event_count": 57,
        "overlap_gap_event_count": 9,
        "unique_gap_event_count": 64,
        "gap_surface_count": 50,
        "action_initializer_event_count": 8,
        "argument_initializer_event_count": 3,
        "initializer_source_event_count": 11,
        "initializer_link_count": 22,
        "immediate_initializer_link_count": 11,
        "delayed_initializer_link_count": 11,
        "maximum_initializer_distance": 5,
        "action_state_link_count": 15,
        "argument_state_link_count": 7,
        "multi_role_gap_surface_count": 1,
        "all_gap_roles_populated": True,
        "new_pages": 0,
        "new_recipes": 0,
        "root_meaning_changes": 0,
        "german_reading_changes": 0,
    }
    check("result_metrics_exact", result == expected_result, {key: result.get(key) for key in expected_result if result.get(key) != expected_result[key]})
    check("book_contains_all_gap_events", all(f"### {row['event_id']} " in book for row in union), len(book))
    check("book_states_overlap_and_scope", "64, nicht 73" in book and "keine neuen Wortbedeutungen" in book, len(book))

    deterministic = [UNION, ACTIONLESS, ARGUMENTLESS, LINKS, PROFILES, SUMMARY, BOOK, RESULT]
    before = {path.name: digest(path) for path in deterministic}
    replay = subprocess.run(
        [sys.executable, str(RUNNER)], cwd=ROOT, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    after = {path.name: digest(path) for path in deterministic}
    check("deterministic_replay_exit", replay.returncode == 0, replay.stderr[-1000:])
    check("deterministic_artifact_hashes", before == after, {name: [before[name], after[name]] for name in before if before[name] != after[name]})

    passed = sum(bool(item["passed"]) for item in checks)
    validation = {
        "status": "PASS" if passed == len(checks) else "FAIL",
        "check_count": len(checks),
        "passed_count": passed,
        "failed_count": len(checks) - passed,
        "input_sha256": {
            SOURCE.name: digest(SOURCE),
            EVENT_INPUT.name: digest(EVENT_INPUT),
            STATEMENT_INPUT.name: digest(STATEMENT_INPUT),
        },
        "artifact_sha256": after,
        "checks": checks,
    }
    VALIDATION.write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0 if validation["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
