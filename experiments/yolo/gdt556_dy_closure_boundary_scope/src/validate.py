#!/usr/bin/env python3
"""Validate GDT556, guarding the mixed GDT407 TSVs before row parsing."""

from __future__ import annotations

import csv
import hashlib
import io
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
BASE = ROOT / "experiments/yolo/gdt556_dy_closure_boundary_scope"
OUT = BASE / "artifacts"
G407 = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts"
G539 = ROOT / "experiments/yolo/gdt539_four_page_contextual_statement_edition/artifacts"

OLD_EVENTS = G407 / "gdt407_4576_running_event_edition.tsv"
OLD_STATEMENTS = G407 / "gdt407_715_statement_edition.tsv"
CURRENT_EVENTS = G539 / "gdt539_546_contextual_prose_events.tsv"
CURRENT_STATEMENTS = G539 / "gdt539_78_contextual_statements.tsv"
DY = OUT / "gdt556_all_dy_occurrences.tsv"
STATEMENT = OUT / "gdt556_dy_statement_profiles.tsv"
MARKER = OUT / "gdt556_marker_finality_comparison.tsv"
RECIPE = OUT / "gdt556_dy_recipe_scope_profiles.tsv"
TAIL = OUT / "gdt556_nonterminal_dy_tail_profiles.tsv"
COHORT = OUT / "gdt556_cohort_closure_summary.tsv"
BOOK = OUT / "GDT556_DY_CLOSURE_BOOK.md"
RESULT = OUT / "gdt556_result.json"
VALIDATION = OUT / "gdt556_validation.json"
RUNNER = BASE / "src/run.py"

OLD_PAGES = (
    "f1r", "f10r", "f11r", "f13r", "f17r", "f18r", "f24v", "f55v",
    "f56r", "f67r2", "f68r1", "f69v", "f70v", "f71v", "f72r", "f75r",
    "f76r", "f77r", "f81r", "f81v", "f82r", "f83r", "f88r", "f88v",
    "f89r", "f95v",
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def guarded(path: Path, columns: tuple[str, ...]) -> tuple[list[dict[str, str]], dict[str, int]]:
    command = [
        str(ROOT / "vmanus-exp"), "query-tsv", str(path.relative_to(ROOT)),
        "--selector", "physical_page",
    ]
    for page in OLD_PAGES:
        command.extend(["--allow", page])
    command.extend(["--columns", ",".join(columns), "--forbid-prefix", "f84"])
    completed = subprocess.run(
        command, cwd=ROOT, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=False,
    )
    if completed.returncode:
        raise RuntimeError(completed.stderr)
    stat_line = next(line for line in completed.stderr.splitlines() if line.startswith("GUARD_STATS "))
    return (
        list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t")),
        json.loads(stat_line.removeprefix("GUARD_STATS ")),
    )


def main() -> int:
    old_events, old_event_stats = guarded(
        OLD_EVENTS,
        ("global_running_event_id", "physical_page", "component_recipe"),
    )
    old_statements, old_statement_stats = guarded(
        OLD_STATEMENTS,
        ("global_statement_id", "physical_page", "event_count", "end_mode"),
    )
    current_events = read_tsv(CURRENT_EVENTS)
    current_statements = read_tsv(CURRENT_STATEMENTS)
    dy = read_tsv(DY)
    statement = read_tsv(STATEMENT)
    marker = read_tsv(MARKER)
    recipe = read_tsv(RECIPE)
    tail = read_tsv(TAIL)
    cohort = read_tsv(COHORT)
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    book = BOOK.read_text(encoding="utf-8")

    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    check("guarded_input_counts", (len(old_events), len(old_statements), len(current_events), len(current_statements)) == (4576, 715, 546, 78), [len(old_events), len(old_statements), len(current_events), len(current_statements)])
    check("old_event_guard_exact", old_event_stats == {"selected": 4576, "skipped_forbidden": 0, "skipped_not_allowed": 0}, old_event_stats)
    check("old_statement_guard_exact", old_statement_stats == {"selected": 715, "skipped_forbidden": 0, "skipped_not_allowed": 0}, old_statement_stats)
    check("no_forbidden_selector_materialized", all(not row["physical_page"].startswith("f84") for row in old_events + old_statements), [])
    check("page_sets_disjoint", not ({row["physical_page"] for row in old_events} & {row["physical_page"] for row in current_events}), [])
    check("running_page_counts", (len({row["physical_page"] for row in old_events}), len({row["physical_page"] for row in current_events})) == (24, 4), [len({row["physical_page"] for row in old_events}), len({row["physical_page"] for row in current_events})])

    check("artifact_row_counts", (len(dy), len(statement), len(marker), len(recipe), len(tail), len(cohort)) == (705, 703, 24, 151, 3, 3), [len(dy), len(statement), len(marker), len(recipe), len(tail), len(cohort)])
    check("every_dy_row_contains_one_dy", all(row["recipe"].split("+").count("DY") == 1 for row in dy), [])
    position_errors = [row["event_id"] for row in dy if row["recipe"].split("+")[int(row["dy_atom_position"]) - 1] != "DY" or int(row["recipe_atom_count"]) != len(row["recipe"].split("+"))]
    check("dy_atom_positions_exact", not position_errors, position_errors)
    scope_counts = Counter(row["closure_scope"] for row in dy)
    check("closure_scope_counts", scope_counts == Counter({"STATEMENT_FINAL_STEP_CLOSURE": 487, "SINGLETON_STATEMENT_CLOSURE": 215, "INTERNAL_LOCAL_STEP_CLOSURE": 3}), scope_counts)
    check("all_current_dy_statement_final", all(row["closure_scope"] != "INTERNAL_LOCAL_STEP_CLOSURE" for row in dy if row["cohort"] == "CURRENT4_GDT539"), [])
    internal = [row for row in dy if row["closure_scope"] == "INTERNAL_LOCAL_STEP_CLOSURE"]
    check("three_exact_internal_events", [row["event_id"] for row in internal] == ["G407-E0133", "G407-E0695", "G407-E1682"], [row["event_id"] for row in internal])
    check("internal_events_have_successors", all(row["successor_event_id"] != "NONE" and int(row["distance_to_statement_end"]) > 0 for row in internal), [])

    terminal_count = sum(row["dy_recipe_terminal"] == "YES" for row in dy)
    nonterminal = [row for row in dy if row["dy_recipe_terminal"] == "NO"]
    check("recipe_terminal_counts", (terminal_count, len(nonterminal)) == (700, 5), [terminal_count, len(nonterminal)])
    check("five_exact_nonterminal_events", [row["event_id"] for row in nonterminal] == ["G407-E0133", "G407-E0695", "G407-E1682", "G407-E2009", "G407-E2236"], [row["event_id"] for row in nonterminal])
    tail_counts = {row["post_dy_tail"]: int(row["event_count"]) for row in tail}
    check("post_dy_tail_counts", tail_counts == {"D_LABEL": 2, "L": 2, "OL": 1}, tail_counts)

    combined_marker = {row["marker"]: row for row in marker if row["cohort"] == "COMBINED30"}
    check("combined_marker_inventory", set(combined_marker) == {"DY", "OL", "OT", "E", "EE", "EEE", "O", "DA"}, sorted(combined_marker))
    check("dy_marker_metrics", combined_marker["DY"]["event_count"] == "705" and combined_marker["DY"]["statement_final_event_count"] == "702" and combined_marker["DY"]["statement_final_percent"] == "99.574468", combined_marker["DY"])
    check("dy_highest_finality_marker", float(combined_marker["DY"]["statement_final_percent"]) > max(float(row["statement_final_percent"]) for marker_name, row in combined_marker.items() if marker_name != "DY"), {key: value["statement_final_percent"] for key, value in combined_marker.items()})
    check("non_dy_final_rate", cohort[-1]["non_dy_final_percent"] == "2.060222", cohort[-1]["non_dy_final_percent"])
    check("cohort_totals", [(row["cohort"], row["event_count"], row["dy_occurrence_count"]) for row in cohort] == [("OLD26_GDT407", "4576", "639"), ("CURRENT4_GDT539", "546", "66"), ("COMBINED30", "5122", "705")], [(row["cohort"], row["event_count"], row["dy_occurrence_count"]) for row in cohort])

    local_scope_recipes = [row for row in recipe if "LOCAL_STEP" in row["scope_levels"]]
    mixed_level_recipes = [row for row in recipe if int(row["scope_level_count"]) > 1]
    check("three_unique_internal_recipes", len(local_scope_recipes) == 3 and all(row["dy_occurrence_count"] == "1" for row in local_scope_recipes), [(row["recipe"], row["dy_occurrence_count"]) for row in local_scope_recipes])
    check("no_recipe_switches_local_and_statement_scope", not mixed_level_recipes, [(row["recipe"], row["scope_levels"]) for row in mixed_level_recipes])
    check("statement_profile_counts", len(statement) == len({f"{row['cohort']}::{row['statement_id']}" for row in dy}), len(statement))

    expected_result = {
        "status": "PASS_DY_702_OF_705_STATEMENT_FINAL__THREE_LOCAL_STEP_CLOSURES",
        "physical_page_count": 30,
        "old_page_count": 26,
        "current_page_count": 4,
        "statement_count": 793,
        "event_count": 5122,
        "dy_occurrence_count": 705,
        "dy_statement_count": 703,
        "dy_final_or_singleton_count": 702,
        "dy_internal_local_step_count": 3,
        "dy_final_or_singleton_percent": "99.574468",
        "non_dy_final_percent": "2.060222",
        "all_dy_recipe_terminal": False,
        "dy_recipe_terminal_count": 700,
        "dy_nonterminal_recipe_count": 5,
        "dy_recipe_terminal_percent": "99.290780",
        "dy_recipe_count": 151,
        "dy_local_and_statement_scope_recipe_count": 0,
        "dy_singleton_final_variant_recipe_count": 41,
        "nonterminal_dy_tail_type_count": 3,
        "dy_statement_profile_count": 703,
        "current_internal_dy_count": 0,
        "old_guard_selected_event_count": 4576,
        "old_guard_selected_statement_count": 715,
        "old_guard_forbidden_skip_count": 0,
        "new_pages": 0,
        "recipe_changes": 0,
        "root_meaning_changes": 0,
        "statement_boundary_changes": 0,
    }
    check("result_metrics_exact", result == expected_result, {key: result.get(key) for key in expected_result if result.get(key) != expected_result[key]})
    check("book_contains_internal_events", all(row["event_id"] in book for row in internal), len(book))
    check("book_states_scope_limit", "keine vorhandene Aussagegrenze" in book and "700/705" in book, len(book))

    deterministic = [DY, STATEMENT, MARKER, RECIPE, TAIL, COHORT, BOOK, RESULT]
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
            OLD_EVENTS.name: digest(OLD_EVENTS),
            OLD_STATEMENTS.name: digest(OLD_STATEMENTS),
            CURRENT_EVENTS.name: digest(CURRENT_EVENTS),
            CURRENT_STATEMENTS.name: digest(CURRENT_STATEMENTS),
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
