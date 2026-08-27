#!/usr/bin/env python3
"""Validate GDT554 independently against GDT539 and GDT553 sources."""

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
BASE = ROOT / "experiments/yolo/gdt554_statement_semantic_template_audit"
OUT = BASE / "artifacts"
G539 = ROOT / "experiments/yolo/gdt539_four_page_contextual_statement_edition/artifacts"
G553 = ROOT / "experiments/yolo/gdt553_zero_rest_145_reader/artifacts"

SOURCE_EVENTS = G539 / "gdt539_546_contextual_prose_events.tsv"
SOURCE_STATEMENTS = G539 / "gdt539_78_contextual_statements.tsv"
SOURCE_READER = G553 / "gdt553_145_zero_rest_reader.tsv"
EVENTS = OUT / "gdt554_546_event_semantic_templates.tsv"
STATEMENTS = OUT / "gdt554_78_statement_template_atlas.tsv"
TARGETS = OUT / "gdt554_145_target_surface_reinsertion.tsv"
SLOTS = OUT / "gdt554_slot_transition_templates.tsv"
EVENT_TEMPLATES = OUT / "gdt554_recurrent_event_templates.tsv"
FRAMES = OUT / "gdt554_recurrent_statement_frames.tsv"
WHOLE = OUT / "gdt554_recurrent_whole_statement_templates.tsv"
CONSISTENCY = OUT / "gdt554_repeated_context_consistency.tsv"
NOMINAL = OUT / "gdt554_16_nominal_fragments.tsv"
SUMMARY = OUT / "gdt554_template_summary.tsv"
BOOK = OUT / "GDT554_STATEMENT_TEMPLATE_BOOK.md"
RESULT = OUT / "gdt554_result.json"
VALIDATION = OUT / "gdt554_validation.json"
RUNNER = BASE / "src/run.py"

ACTION_ROOTS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
ARGUMENT_ROOTS = {"Y", "AIIN", "AIN", "OR"}
CONTROL_LABEL = {
    "AL": "REL:AL", "AR": "REL:AR", "L": "REL:L", "AIR": "REL:AIR",
    "E": "GRADE:I", "EE": "GRADE:II", "EEE": "GRADE:III", "O": "EXEC",
    "D_ADDR": "ADDR:D", "AM_ADDR": "ADDR:AM", "A_ADDR": "ADDR:A",
    "S_ADDR": "ADDR:S", "LOCAL_CHAR_F": "LOCAL:F",
    "LOCAL_CHAR_I": "LOCAL:I", "LOCAL_X": "LOCAL:X", "M_LOCAL": "LOCAL:M",
    "HO": "CLASS", "IIN": "STAGE", "DA": "STAGE:II", "OL": "CONTINUE",
    "OT": "THEN", "DY": "CLOSE", "CARRIER_Q": "BEGIN",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_roots(value: str) -> list[str]:
    return [] if value in {"", "NONE"} else value.split("|")


def source_state(explicit: list[str], inherited: str, role: str) -> str:
    if explicit:
        return f"SET_{role}{len(explicit)}"
    return f"KEEP_{role}1" if inherited != "NONE" else f"EMPTY_{role}"


def main() -> int:
    source_events = read_tsv(SOURCE_EVENTS)
    source_statements = read_tsv(SOURCE_STATEMENTS)
    source_reader = read_tsv(SOURCE_READER)
    events = read_tsv(EVENTS)
    statements = read_tsv(STATEMENTS)
    targets = read_tsv(TARGETS)
    slots = read_tsv(SLOTS)
    event_templates = read_tsv(EVENT_TEMPLATES)
    frames = read_tsv(FRAMES)
    whole = read_tsv(WHOLE)
    consistency = read_tsv(CONSISTENCY)
    nominal = read_tsv(NOMINAL)
    summary = read_tsv(SUMMARY)
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    book = BOOK.read_text(encoding="utf-8")

    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    check("source_counts", (len(source_events), len(source_statements), len(source_reader)) == (546, 78, 145), [len(source_events), len(source_statements), len(source_reader)])
    check("output_core_counts", (len(events), len(statements), len(targets)) == (546, 78, 145), [len(events), len(statements), len(targets)])
    check("event_id_order_exact", [row["event_id"] for row in events] == [row["event_id"] for row in source_events], len(events))
    check("statement_id_order_exact", [row["statement_id"] for row in statements] == [row["statement_id"] for row in source_statements], len(statements))

    source_event_by_id = {row["event_id"]: row for row in source_events}
    event_by_id = {row["event_id"]: row for row in events}
    source_statement_by_id = {row["statement_id"]: row for row in source_statements}
    reader_by_surface = {row["surface"]: row for row in source_reader}
    target_events = [row for row in events if row["gdt553_target_member"] == "YES"]
    check("target_occurrence_count", len(target_events) == 149, len(target_events))
    check("target_surface_set_exact", {row["surface"] for row in targets} == set(reader_by_surface), len(targets))
    check("all_target_recipe_matches", all(row["gdt553_recipe_match"] == "YES" for row in target_events), [])
    check("all_target_context_matches", all(row["gdt553_context_reading_match"] == "YES" for row in target_events), [])
    check("target_recipes_equal_reader", all(row["final_recipe"] == reader_by_surface[row["surface"]]["final_recipe"] for row in target_events), [])
    check("target_clauses_in_reader", all(row["contextual_clause_de"] in reader_by_surface[row["surface"]]["known_contextual_readings_de"].split(" || ") for row in target_events), [])
    check("all_source_recipe_and_clause_copied", all(row["final_recipe"] == source_event_by_id[row["event_id"]]["final_context_recipe"] and row["contextual_clause_de"] == source_event_by_id[row["event_id"]]["contextual_clause_de"] for row in events), [])
    check("repaired_target_event_count", sum(row["gdt553_resolution_generation"] != "BASE_GDT548" for row in target_events) == 23, sum(row["gdt553_resolution_generation"] != "BASE_GDT548" for row in target_events))

    multi_state_targets = [row for row in targets if int(row["incoming_state_count"]) > 1]
    check("only_qokees_has_multiple_incoming_states", [row["surface"] for row in multi_state_targets] == ["qokees"], [row["surface"] for row in multi_state_targets])
    check("all_145_reinsertions_green", all(row["recipe_match_all_events"] == "YES" and row["context_reading_match_all_events"] == "YES" for row in targets), [])

    expected_slots: Counter[str] = Counter()
    expected_macros: dict[str, str] = {}
    for source in source_events:
        actions = split_roots(source["explicit_action_roots"])
        arguments = split_roots(source["explicit_argument_roots"])
        slot = "__".join([
            source_state(actions, source["inherited_action_root"], "A"),
            source_state(arguments, source["inherited_argument_root"], "X"),
        ])
        expected_slots[slot] += 1
        atoms = source["final_context_recipe"].split("+")
        action = "+".join(actions) if actions else ("^" + source["inherited_action_root"] if source["inherited_action_root"] != "NONE" else "-")
        argument = "+".join(arguments) if arguments else ("^" + source["inherited_argument_root"] if source["inherited_argument_root"] != "NONE" else "-")
        controls = [CONTROL_LABEL[atom] for atom in atoms if atom in CONTROL_LABEL]
        expected_macros[source["event_id"]] = f"A:{action};X:{argument};C:{'>'.join(controls) or '-'}"
    observed_slots = {row["slot_transition_template"]: int(row["event_count"]) for row in slots}
    check("slot_template_counts_recomputed", observed_slots == dict(expected_slots), observed_slots)
    check("slot_template_count_18", len(slots) == 18 and sum(int(row["event_count"]) for row in slots) == 546, [len(slots), sum(int(row["event_count"]) for row in slots)])
    check("portable_macros_recomputed", all(row["portable_semantic_macro"] == expected_macros[row["event_id"]] for row in events), [])

    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        events_by_statement[row["statement_id"]].append(row)
    for rows in events_by_statement.values():
        rows.sort(key=lambda row: int(row["card_ordinal_in_statement"]))
    check("all_statement_event_counts_exact", all(len(events_by_statement[row["statement_id"]]) == int(row["event_count"]) for row in source_statements), [])
    check("statement_macro_sequences_exact", all(row["portable_semantic_macro_sequence"] == " || ".join(event["portable_semantic_macro"] for event in events_by_statement[row["statement_id"]]) for row in statements), [])
    check("statement_readings_copied", all(row["contextual_working_reading_de"] == source_statement_by_id[row["statement_id"]]["contextual_working_reading_de"] for row in statements), [])

    check("event_template_metrics", (len(event_templates), sum(int(row["event_count"]) for row in event_templates)) == (71, 370), [len(event_templates), sum(int(row["event_count"]) for row in event_templates)])
    check("recurrent_event_templates_cross_statement", all(int(row["statement_count"]) >= 2 for row in event_templates), [])
    check("frame_partition", (len(frames), Counter(row["frame_layer"] for row in frames)) == (12, Counter({"ABSTRACT_ROLE": 8, "EXACT_PORTABLE": 4})), [len(frames), Counter(row["frame_layer"] for row in frames)])
    check("all_recurrent_frames_are_bigrams", all(row["frame_length"] == "2" for row in frames), sorted({row["frame_length"] for row in frames}))
    check("frame_statement_ids_exist", all(set(row["statement_ids"].split("|")) <= set(source_statement_by_id) for row in frames), [])
    check("frame_guards_statement_bounded", all(row["guard"] == "CONTIGUOUS_WITHIN_STATEMENT_FRAME__NO_CROSS_BOUNDARY_JOIN" for row in frames), [])

    check("whole_statement_template_metrics", (len(whole), sum(int(row["statement_count"]) for row in whole), max(int(row["event_length"]) for row in whole)) == (5, 14, 2), [len(whole), sum(int(row["statement_count"]) for row in whole), max(int(row["event_length"]) for row in whole)])
    check("whole_template_statement_ids_exist", all(set(row["statement_ids"].split("|")) <= set(source_statement_by_id) for row in whole), [])

    check("repeated_context_family_count", len(consistency) == 142, len(consistency))
    check("zero_exact_context_contradictions", all(row["status"] == "CONSISTENT_PORTABLE_READING" and row["portable_macro_variant_count"] == "1" for row in consistency), [])
    check("surface_families_single_recipe", all(row["recipe_variant_count"] == "1" for row in consistency if row["family_type"] == "SURFACE_PLUS_INCOMING_STATE"), [])

    nominal_ids = {row["event_id"] for row in nominal}
    expected_nominal = {row["event_id"] for row in events if row["resolved_action_roots"] == "NONE"}
    check("nominal_fragment_set_exact", nominal_ids == expected_nominal and len(nominal) == 16, sorted(nominal_ids ^ expected_nominal))
    check("fourteen_nominals_statement_initial", sum(row["statement_initial"] == "YES" for row in nominal) == 14, sum(row["statement_initial"] == "YES" for row in nominal))
    check("nominal_decision_retained", all(row["decision"] == "KEEP_NOMINAL_OR_CONTROL_READING__DO_NOT_INVENT_VERB" for row in nominal), [])

    expected_result = {
        "status": "PASS_78_STATEMENT_TEMPLATE_ATLAS__ZERO_EXACT_CONTEXT_CONTRADICTIONS",
        "physical_page_count": 4,
        "register_count": 2,
        "statement_count": 78,
        "prose_event_count": 546,
        "gdt553_target_surface_count": 145,
        "gdt553_target_event_count": 149,
        "gdt553_recipe_match_count": 149,
        "gdt553_context_reading_match_count": 149,
        "gdt553_repaired_target_event_count": 23,
        "gdt553_multi_incoming_state_surface_count": 1,
        "slot_transition_template_count": 18,
        "cross_register_slot_transition_template_count": 16,
        "event_template_count": 243,
        "recurrent_event_template_count": 71,
        "recurrent_event_template_event_count": 370,
        "cross_register_recurrent_event_template_count": 44,
        "recurrent_frame_count": 12,
        "exact_portable_recurrent_frame_count": 4,
        "abstract_recurrent_frame_count": 8,
        "cross_page_recurrent_frame_count": 9,
        "cross_register_recurrent_frame_count": 6,
        "cross_register_exact_portable_frame_count": 1,
        "longest_recurrent_frame_length": 2,
        "recurrent_three_plus_frame_count": 0,
        "repeated_context_family_count": 142,
        "exact_context_contradiction_count": 0,
        "nominal_fragment_count": 16,
        "statement_initial_nominal_fragment_count": 14,
        "exact_abstract_statement_peer_count": 38,
        "recurrent_whole_statement_template_count": 5,
        "abstract_whole_statement_template_count": 69,
        "statements_in_recurrent_whole_template_count": 14,
        "cross_page_whole_statement_template_count": 2,
        "longest_recurrent_whole_statement_event_count": 2,
        "new_pages": 0,
        "new_recipes": 0,
        "root_meaning_changes": 0,
        "german_reading_changes": 0,
    }
    check("result_metrics_exact", result == expected_result, {key: result.get(key) for key in expected_result if result.get(key) != expected_result[key]})
    summary_map = {row["metric"]: row["value"] for row in summary}
    check("summary_matches_result", all(summary_map.get(key) == str(value) for key, value in result.items()), len(summary_map))
    check("book_contains_all_statements", all(f"### {row['statement_id']} " in book for row in source_statements), len(book))
    check("book_states_scope_limit", "keine behauptete historische Syntax" in book and "Null exakte Kontextwidersprüche" in book, len(book))

    deterministic_paths = [EVENTS, STATEMENTS, TARGETS, SLOTS, EVENT_TEMPLATES, FRAMES, WHOLE, CONSISTENCY, NOMINAL, SUMMARY, BOOK, RESULT]
    before = {path.name: digest(path) for path in deterministic_paths}
    replay = subprocess.run(
        [sys.executable, str(RUNNER)], cwd=ROOT, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    after = {path.name: digest(path) for path in deterministic_paths}
    check("deterministic_replay_exit", replay.returncode == 0, replay.stderr[-1000:])
    check("deterministic_artifact_hashes", before == after, {name: [before[name], after[name]] for name in before if before[name] != after[name]})

    passed = sum(bool(item["passed"]) for item in checks)
    validation = {
        "status": "PASS" if passed == len(checks) else "FAIL",
        "check_count": len(checks),
        "passed_count": passed,
        "failed_count": len(checks) - passed,
        "input_sha256": {
            SOURCE_EVENTS.name: digest(SOURCE_EVENTS),
            SOURCE_STATEMENTS.name: digest(SOURCE_STATEMENTS),
            SOURCE_READER.name: digest(SOURCE_READER),
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
