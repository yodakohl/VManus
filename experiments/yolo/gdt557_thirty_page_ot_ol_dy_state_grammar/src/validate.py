#!/usr/bin/env python3
"""Independently validate GDT557 with guarded access to mixed old TSVs."""

from __future__ import annotations

import csv
import hashlib
import io
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
BASE = ROOT / "experiments/yolo/gdt557_thirty_page_ot_ol_dy_state_grammar"
OUT = BASE / "artifacts"
G407 = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts"
G478 = ROOT / "experiments/yolo/gdt478_paired_ot_ol_order_grammar/artifacts"
G539 = ROOT / "experiments/yolo/gdt539_four_page_contextual_statement_edition/artifacts"
G556 = ROOT / "experiments/yolo/gdt556_dy_closure_boundary_scope/artifacts"

OLD_EVENTS = G407 / "gdt407_4576_running_event_edition.tsv"
OLD_STATEMENTS = G407 / "gdt407_715_statement_edition.tsv"
CURRENT_EVENTS = G539 / "gdt539_546_contextual_prose_events.tsv"
CURRENT_STATEMENTS = G539 / "gdt539_78_contextual_statements.tsv"
SEED_RESULT = G478 / "gdt478_result.json"
PRIOR_DY = G556 / "gdt556_all_dy_occurrences.tsv"

OCCURRENCE = OUT / "gdt557_all_state_marker_occurrences.tsv"
SUMMARY = OUT / "gdt557_marker_position_summary.tsv"
PAIR = OUT / "gdt557_marker_pair_order.tsv"
SEQUENCE = OUT / "gdt557_marker_sequence_profiles.tsv"
PAGE = OUT / "gdt557_page_transfer.tsv"
EDGE = OUT / "gdt557_compositional_edge_cases.tsv"
TRANSFER = OUT / "gdt557_seed_to_full_transfer.tsv"
BOOK = OUT / "GDT557_THREE_STATE_GRAMMAR.md"
RESULT = OUT / "gdt557_result.json"
VALIDATION = OUT / "gdt557_validation.json"
RUNNER = BASE / "src/run.py"

OLD_PAGES = (
    "f1r", "f10r", "f11r", "f13r", "f17r", "f18r", "f24v", "f55v",
    "f56r", "f67r2", "f68r1", "f69v", "f70v", "f71v", "f72r", "f75r",
    "f76r", "f77r", "f81r", "f81v", "f82r", "f83r", "f88r", "f88v",
    "f89r", "f95v",
)
MARKERS = ("OT", "OL", "DY")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def guarded(
    path: Path, columns: tuple[str, ...]
) -> tuple[list[dict[str, str]], dict[str, int]]:
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


def marker_sequence(recipe: str) -> str:
    return "+".join(atom for atom in recipe.split("+") if atom in MARKERS) or "NONE"


def pair_relation(recipe: str, first: str, second: str) -> str:
    atoms = recipe.split("+")
    a = [index for index, atom in enumerate(atoms) if atom == first]
    b = [index for index, atom in enumerate(atoms) if atom == second]
    if max(a) < min(b):
        return "FIRST_BEFORE_SECOND"
    if max(b) < min(a):
        return "SECOND_BEFORE_FIRST"
    return "INTERLEAVED"


def main() -> int:
    old_events, old_event_stats = guarded(
        OLD_EVENTS,
        (
            "global_running_ordinal", "global_running_event_id", "source_layer",
            "source_statement_id", "physical_page", "component_recipe",
        ),
    )
    old_statements, old_statement_stats = guarded(
        OLD_STATEMENTS,
        (
            "global_statement_id", "source_layer", "source_statement_id",
            "physical_page", "event_count",
        ),
    )
    current_events = read_tsv(CURRENT_EVENTS)
    current_statements = read_tsv(CURRENT_STATEMENTS)
    occurrence = read_tsv(OCCURRENCE)
    summary = read_tsv(SUMMARY)
    pair = read_tsv(PAIR)
    sequence = read_tsv(SEQUENCE)
    page = read_tsv(PAGE)
    edge = read_tsv(EDGE)
    transfer = read_tsv(TRANSFER)
    prior_dy = read_tsv(PRIOR_DY)
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    seed_result = json.loads(SEED_RESULT.read_text(encoding="utf-8"))
    book = BOOK.read_text(encoding="utf-8")

    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    check("guarded_input_counts", (len(old_events), len(old_statements), len(current_events), len(current_statements)) == (4576, 715, 546, 78), [len(old_events), len(old_statements), len(current_events), len(current_statements)])
    check("old_event_guard_exact", old_event_stats == {"selected": 4576, "skipped_forbidden": 0, "skipped_not_allowed": 0}, old_event_stats)
    check("old_statement_guard_exact", old_statement_stats == {"selected": 715, "skipped_forbidden": 0, "skipped_not_allowed": 0}, old_statement_stats)
    check("no_forbidden_selector_materialized", all(not row["physical_page"].startswith("f84") for row in old_events + old_statements), [])

    events: list[dict[str, object]] = []
    statement_sizes: dict[str, int] = {}
    for row in old_statements:
        key = f"O::{row['source_layer']}::{row['source_statement_id']}"
        statement_sizes[key] = int(row["event_count"])
    for row in old_events:
        events.append({
            "cohort": "OLD26_GDT407", "event_id": row["global_running_event_id"],
            "statement_key": f"O::{row['source_layer']}::{row['source_statement_id']}",
            "physical_page": row["physical_page"], "recipe": row["component_recipe"],
            "order": int(row["global_running_ordinal"]),
        })
    for row in current_statements:
        statement_sizes[f"C::{row['statement_id']}"] = int(row["event_count"])
    for row in current_events:
        events.append({
            "cohort": "CURRENT4_GDT539", "event_id": row["event_id"],
            "statement_key": f"C::{row['statement_id']}",
            "physical_page": row["physical_page"], "recipe": row["final_context_recipe"],
            "order": int(row["context_event_ordinal"]),
        })
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for event in events:
        grouped[str(event["statement_key"])].append(event)
    grouping_errors: list[str] = []
    for key, material in grouped.items():
        material.sort(key=lambda row: int(row["order"]))
        if len(material) != statement_sizes.get(key):
            grouping_errors.append(key)
        for ordinal, event in enumerate(material, 1):
            event["statement_final"] = ordinal == len(material)
    check("statement_grouping_exact", not grouping_errors and len(grouped) == 793, grouping_errors)

    old_pages = {str(event["physical_page"]) for event in events if event["cohort"] == "OLD26_GDT407"}
    current_pages = {str(event["physical_page"]) for event in events if event["cohort"] == "CURRENT4_GDT539"}
    check("running_page_union", len(old_pages) == 24 and current_pages == {"f4r", "f20v", "f31r", "f66r"} and not old_pages & current_pages, [sorted(old_pages), sorted(current_pages)])

    check("artifact_row_counts", (len(occurrence), len(summary), len(pair), len(sequence), len(page), len(edge), len(transfer)) == (1870, 9, 9, 9, 30, 12, 2), [len(occurrence), len(summary), len(pair), len(sequence), len(page), len(edge), len(transfer)])
    occurrence_counts = Counter(row["marker"] for row in occurrence)
    event_counts = {marker: len({row["event_id"] for row in occurrence if row["marker"] == marker}) for marker in MARKERS}
    check("marker_occurrence_counts", occurrence_counts == Counter({"OL": 761, "DY": 705, "OT": 404}), occurrence_counts)
    check("marker_event_counts", event_counts == {"OT": 404, "OL": 747, "DY": 705}, event_counts)

    input_by_id = {str(event["event_id"]): event for event in events}
    position_errors: list[str] = []
    for row in occurrence:
        event = input_by_id.get(row["event_id"])
        if event is None or event["recipe"] != row["recipe"]:
            position_errors.append(row["event_id"])
            continue
        atoms = str(event["recipe"]).split("+")
        position = int(row["marker_atom_position"])
        if position < 1 or position > len(atoms) or atoms[position - 1] != row["marker"] or int(row["recipe_atom_count"]) != len(atoms):
            position_errors.append(row["event_id"])
    check("occurrence_positions_exact", not position_errors, position_errors[:20])

    roles = {marker: Counter(row["recipe_position_role"] for row in occurrence if row["marker"] == marker) for marker in MARKERS}
    check("ot_recipe_roles", roles["OT"] == Counter({"INITIAL": 377, "INTERNAL_BRIDGE": 25, "SINGLE_ATOM": 2}), roles["OT"])
    check("ol_recipe_roles", roles["OL"] == Counter({"TERMINAL": 288, "INITIAL": 199, "SINGLE_ATOM": 189, "INTERNAL_BRIDGE": 85}), roles["OL"])
    check("dy_recipe_roles", roles["DY"] == Counter({"TERMINAL": 700, "INTERNAL_BRIDGE": 5}), roles["DY"])
    right_counts = {marker: sum(row["right_carrier_present"] == "YES" for row in occurrence if row["marker"] == marker) for marker in MARKERS}
    left_counts = {marker: sum(row["left_carrier_present"] == "YES" for row in occurrence if row["marker"] == marker) for marker in MARKERS}
    check("carrier_counts", right_counts == {"OT": 402, "OL": 284, "DY": 5} and left_counts == {"OT": 25, "OL": 373, "DY": 705}, [right_counts, left_counts])

    final_counts = {
        marker: sum(bool(input_by_id[event_id]["statement_final"]) for event_id in {row["event_id"] for row in occurrence if row["marker"] == marker})
        for marker in MARKERS
    }
    check("statement_final_counts", final_counts == {"OT": 91, "OL": 89, "DY": 702}, final_counts)

    expected_sequences = Counter({
        "OL": 619, "DY": 544, "OT": 279, "OT+DY": 86, "OL+DY": 74,
        "OT+OL": 38, "OL+OL": 14, "DY+OL": 1, "OL+OT": 1,
    })
    actual_sequences = Counter(marker_sequence(str(event["recipe"])) for event in events if marker_sequence(str(event["recipe"])) != "NONE")
    output_sequences = Counter({row["marker_sequence"]: int(row["event_count"]) for row in sequence})
    check("nine_marker_sequences_exact", actual_sequences == expected_sequences == output_sequences, [actual_sequences, output_sequences])
    check("marker_bearing_event_count", sum(actual_sequences.values()) == 1656, sum(actual_sequences.values()))
    check("no_three_marker_event", all(len(sequence_name.split("+")) <= 2 for sequence_name in actual_sequences), sorted(actual_sequences))

    ending_dy = [event for event in events if marker_sequence(str(event["recipe"])).endswith("DY")]
    without_dy = [event for event in events if marker_sequence(str(event["recipe"])) != "NONE" and "DY" not in str(event["recipe"]).split("+")]
    dy_then_ol = [event for event in events if marker_sequence(str(event["recipe"])) == "DY+OL"]
    check("dy_closure_switch", (len(ending_dy), sum(bool(event["statement_final"]) for event in ending_dy), len(without_dy), sum(bool(event["statement_final"]) for event in without_dy), len(dy_then_ol), sum(bool(event["statement_final"]) for event in dy_then_ol)) == (704, 702, 951, 20, 1, 0), [len(ending_dy), sum(bool(event["statement_final"]) for event in ending_dy), len(without_dy), sum(bool(event["statement_final"]) for event in without_dy), len(dy_then_ol)])

    pair_expected = {
        ("OT", "OL"): (39, 38, 1, 0),
        ("OT", "DY"): (86, 86, 0, 0),
        ("OL", "DY"): (75, 74, 1, 0),
    }
    pair_actual: dict[tuple[str, str], tuple[int, int, int, int]] = {}
    reverse_ids: set[str] = set()
    for first, second in pair_expected:
        selected = [event for event in events if first in str(event["recipe"]).split("+") and second in str(event["recipe"]).split("+")]
        relations = Counter(pair_relation(str(event["recipe"]), first, second) for event in selected)
        pair_actual[(first, second)] = (len(selected), relations["FIRST_BEFORE_SECOND"], relations["SECOND_BEFORE_FIRST"], relations["INTERLEAVED"])
        reverse_ids.update(str(event["event_id"]) for event in selected if pair_relation(str(event["recipe"]), first, second) == "SECOND_BEFORE_FIRST")
    check("pair_order_counts", pair_actual == pair_expected, {f"{key[0]}+{key[1]}": value for key, value in pair_actual.items()})
    check("two_reverse_compositions", reverse_ids == {"G407-E0034", "G407-E1682"}, sorted(reverse_ids))
    combined_pair = {(row["first_marker"], row["second_marker"]): (int(row["cooccurrence_event_count"]), int(row["first_before_second_count"]), int(row["second_before_first_count"]), int(row["interleaved_count"])) for row in pair if row["cohort"] == "COMBINED30"}
    check("pair_artifact_matches_recount", combined_pair == pair_expected, {f"{key[0]}+{key[1]}": value for key, value in combined_pair.items()})

    sequence_final = {row["marker_sequence"]: int(row["statement_final_event_count"]) for row in sequence}
    check("compound_finality", sequence_final["OT+DY"] == 86 and sequence_final["OL+DY"] == 74 and sequence_final["OT+OL"] == 0 and sequence_final["DY+OL"] == 0, sequence_final)

    edge_categories = Counter(row["category"] for row in edge)
    check("edge_category_counts", edge_categories == Counter({"POST_DY_ATTACHMENT": 5, "INTERNAL_DY_LOCAL_CLOSE": 3, "BARE_OT_CONTEXT_CARRIER": 2, "REVERSE_OL_BEFORE_OT": 1, "REVERSE_DY_BEFORE_OL": 1}), edge_categories)
    check("bare_ot_ids", {row["event_id"] for row in edge if row["category"] == "BARE_OT_CONTEXT_CARRIER"} == {"G407-E0821", "G407-E2027"}, [])
    check("internal_dy_ids", {row["event_id"] for row in edge if row["category"] == "INTERNAL_DY_LOCAL_CLOSE"} == {"G407-E0133", "G407-E0695", "G407-E1682"}, [])

    running_page_rows = [row for row in page if int(row["running_event_count"]) > 0]
    empty_page_rows = [row for row in page if int(row["running_event_count"]) == 0]
    check("all_running_pages_have_triad", len(running_page_rows) == 28 and all("ALL_THREE_OPERATORS_PRESENT" in row["transfer_note"] for row in running_page_rows), len(running_page_rows))
    check("two_local_only_pages", {row["physical_page"] for row in empty_page_rows} == {"f69v", "f70v"}, [row["physical_page"] for row in empty_page_rows])

    combined_summary = {row["marker"]: row for row in summary if row["cohort"] == "COMBINED30"}
    check("summary_combined_counts", {(marker, combined_summary[marker]["occurrence_count"], combined_summary[marker]["event_count"], combined_summary[marker]["right_carrier_count"], combined_summary[marker]["statement_final_event_count"]) for marker in MARKERS} == {("OT", "404", "404", "402", "91"), ("OL", "761", "747", "284", "89"), ("DY", "705", "705", "5", "702")}, combined_summary)
    cohort_occurrences = Counter((row["cohort"], row["marker"]) for row in occurrence)
    check("cohort_occurrence_counts", cohort_occurrences == Counter({("OLD26_GDT407", "OT"): 363, ("OLD26_GDT407", "OL"): 688, ("OLD26_GDT407", "DY"): 639, ("CURRENT4_GDT539", "OT"): 41, ("CURRENT4_GDT539", "OL"): 73, ("CURRENT4_GDT539", "DY"): 66}), {f"{key[0]}::{key[1]}": value for key, value in cohort_occurrences.items()})

    check("seed_values_unchanged", seed_result["order_occurrence_count"] == 69 and seed_result["ot_occurrence_count"] == 41 and seed_result["ol_occurrence_count"] == 28 and seed_result["joint_ot_ol_event_count"] == 7 and seed_result["joint_ot_precedes_ol_count"] == 7, {key: seed_result.get(key) for key in ("order_occurrence_count", "ot_occurrence_count", "ol_occurrence_count", "joint_ot_ol_event_count", "joint_ot_precedes_ol_count")})
    check("transfer_rows_exact", transfer[0]["marker_occurrence_count"] == "69" and transfer[1]["marker_occurrence_count"] == "1870" and transfer[1]["ot_before_ol_count"] == "38" and transfer[1]["ol_before_ot_count"] == "1", transfer)

    current_dy_tuples = {(row["event_id"], row["recipe"], row["marker_atom_position"], row["statement_final"]) for row in occurrence if row["marker"] == "DY"}
    prior_dy_tuples = {(row["event_id"], row["recipe"], row["dy_atom_position"], "NO" if row["closure_scope"] == "INTERNAL_LOCAL_STEP_CLOSURE" else "YES") for row in prior_dy}
    check("gdt556_dy_exact_parity", current_dy_tuples == prior_dy_tuples, [len(current_dy_tuples), len(prior_dy_tuples), len(current_dy_tuples ^ prior_dy_tuples)])

    expected_result = {
        "status": "PASS_OT_RIGHT_402_OF_404__OL_FLEXIBLE__DY_CLOSE_702_OF_705__TWO_REVERSE_COMPOSITIONS",
        "admitted_physical_page_count": 30,
        "running_physical_page_count": 28,
        "old_admitted_page_count": 26,
        "old_running_page_count": 24,
        "current_page_count": 4,
        "statement_count": 793,
        "event_count": 5122,
        "marker_bearing_event_count": 1656,
        "marker_occurrence_count": 1870,
        "marker_sequence_profile_count": 9,
        "ot_event_count": 404,
        "ot_occurrence_count": 404,
        "ot_right_carrier_count": 402,
        "ot_right_carrier_percent": "99.504950",
        "bare_ot_count": 2,
        "ol_event_count": 747,
        "ol_occurrence_count": 761,
        "ol_single_atom_count": 189,
        "ol_initial_count": 199,
        "ol_internal_bridge_count": 85,
        "ol_terminal_nonsingleton_count": 288,
        "ol_statement_nonfinal_event_count": 658,
        "dy_event_count": 705,
        "dy_occurrence_count": 705,
        "dy_recipe_terminal_count": 700,
        "dy_statement_final_count": 702,
        "dy_statement_final_percent": "99.574468",
        "ot_ol_joint_event_count": 39,
        "ot_before_ol_count": 38,
        "ol_before_ot_count": 1,
        "ot_dy_joint_event_count": 86,
        "ot_before_dy_count": 86,
        "dy_before_ot_count": 0,
        "ol_dy_joint_event_count": 75,
        "ol_before_dy_count": 74,
        "dy_before_ol_count": 1,
        "reverse_pair_event_count": 2,
        "compositional_edge_row_count": 12,
        "running_pages_with_all_three_markers": 28,
        "old_guard_selected_event_count": 4576,
        "old_guard_selected_statement_count": 715,
        "old_guard_forbidden_skip_count": 0,
        "new_pages": 0,
        "recipe_changes": 0,
        "root_meaning_changes": 0,
        "statement_boundary_changes": 0,
    }
    check("result_metrics_exact", result == expected_result, {key: result.get(key) for key in expected_result if result.get(key) != expected_result[key]})
    check("book_contains_core_transfer", all(token in book for token in ("402 (99.504950%)", "702/705", "OT→DY 86/86", "G407-E0034", "G407-E1682", "1870 Operatorvorkommen")), len(book))

    deterministic = [OCCURRENCE, SUMMARY, PAIR, SEQUENCE, PAGE, EDGE, TRANSFER, BOOK, RESULT]
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
        "check_count": len(checks), "passed_count": passed,
        "failed_count": len(checks) - passed,
        "input_sha256": {
            OLD_EVENTS.name: digest(OLD_EVENTS), OLD_STATEMENTS.name: digest(OLD_STATEMENTS),
            CURRENT_EVENTS.name: digest(CURRENT_EVENTS), CURRENT_STATEMENTS.name: digest(CURRENT_STATEMENTS),
            SEED_RESULT.name: digest(SEED_RESULT), PRIOR_DY.name: digest(PRIOR_DY),
        },
        "artifact_sha256": after, "checks": checks,
    }
    VALIDATION.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0 if validation["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
