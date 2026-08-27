#!/usr/bin/env python3
"""Validate the complete GDT562 actionless state-card reader."""

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
BASE = ROOT / "experiments/yolo/gdt562_thirty_page_actionless_state_role_reader"
OUT = BASE / "artifacts"
RUNNER = BASE / "src/run.py"
VALIDATION_OUT = OUT / "gdt562_validation.json"

INPUTS = {
    "old_context": ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts/gdt416_4576_imperative_clauses.tsv",
    "current_context": ROOT / "experiments/yolo/gdt539_four_page_contextual_statement_edition/artifacts/gdt539_546_contextual_prose_events.tsv",
    "typed_cards": ROOT / "experiments/yolo/gdt561_typed_state_card_composition_reader/artifacts/gdt561_1656_typed_state_cards.tsv",
    "state_dictionary": ROOT / "experiments/yolo/gdt561_typed_state_card_composition_reader/artifacts/gdt561_36_state_atom_dictionary.tsv",
}
ARTIFACTS = {
    "gdt562_706_actionless_state_reader.tsv": OUT / "gdt562_706_actionless_state_reader.tsv",
    "gdt562_693_action_provenance.tsv": OUT / "gdt562_693_action_provenance.tsv",
    "gdt562_459_inherited_argument_provenance.tsv": OUT / "gdt562_459_inherited_argument_provenance.tsv",
    "gdt562_19_nonfull_operation_cards.tsv": OUT / "gdt562_19_nonfull_operation_cards.tsv",
    "gdt562_6_completeness_roles.tsv": OUT / "gdt562_6_completeness_roles.tsv",
    "gdt562_7_state_sequence_roles.tsv": OUT / "gdt562_7_state_sequence_roles.tsv",
    "gdt562_9_inherited_action_profiles.tsv": OUT / "gdt562_9_inherited_action_profiles.tsv",
    "GDT562_ACTIONLESS_STATE_BOOK.md": OUT / "GDT562_ACTIONLESS_STATE_BOOK.md",
    "gdt562_result.json": OUT / "gdt562_result.json",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_roots(value: str) -> list[str]:
    return [] if value in ("", "NONE") else value.split("|")


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    old_context = read_tsv(INPUTS["old_context"])
    current_context = read_tsv(INPUTS["current_context"])
    typed = read_tsv(INPUTS["typed_cards"])
    dictionary = read_tsv(INPUTS["state_dictionary"])
    cards = read_tsv(ARTIFACTS["gdt562_706_actionless_state_reader.tsv"])
    actions = read_tsv(ARTIFACTS["gdt562_693_action_provenance.tsv"])
    arguments = read_tsv(ARTIFACTS["gdt562_459_inherited_argument_provenance.tsv"])
    residuals = read_tsv(ARTIFACTS["gdt562_19_nonfull_operation_cards.tsv"])
    roles = read_tsv(ARTIFACTS["gdt562_6_completeness_roles.tsv"])
    sequences = read_tsv(ARTIFACTS["gdt562_7_state_sequence_roles.tsv"])
    roots = read_tsv(ARTIFACTS["gdt562_9_inherited_action_profiles.tsv"])
    result = json.loads(ARTIFACTS["gdt562_result.json"].read_text(encoding="utf-8"))

    input_counts = tuple(map(len, (old_context, current_context, typed, dictionary)))
    check("input_counts", input_counts == (4576, 546, 1656, 36), input_counts)
    source_actionless = [row for row in typed if row["action_atom_count"] == "0"]
    check("source_actionless_count", len(source_actionless) == 706, len(source_actionless))
    check("source_pages_exclude_f84", not any(row["physical_page"].startswith("f84") for row in source_actionless), sorted({row["physical_page"] for row in source_actionless if row["physical_page"].startswith("f84")}))
    observed_counts = tuple(map(len, (cards, actions, arguments, residuals, roles, sequences, roots)))
    check("artifact_row_counts", observed_counts == (706, 693, 459, 19, 6, 7, 9), observed_counts)

    source_by_id = {row["event_id"]: row for row in source_actionless}
    card_by_id = {row["event_id"]: row for row in cards}
    check("card_ids_unique_and_complete", len(card_by_id) == 706 and set(card_by_id) == set(source_by_id), [len(card_by_id), len(set(card_by_id) ^ set(source_by_id))])
    check("actionless_ordinals", [int(row["actionless_ordinal"]) for row in cards] == list(range(1, 707)), [cards[0]["actionless_ordinal"], cards[-1]["actionless_ordinal"]])
    check("recipes_unchanged", all(card_by_id[event_id]["recipe"] == source["recipe"] for event_id, source in source_by_id.items()), [])
    check("surfaces_unchanged", all(card_by_id[event_id]["surface"] == source["surface"] for event_id, source in source_by_id.items()), [])
    check("source_has_no_explicit_actions", all(row["explicit_action_roots"] == "NONE" and row["action_atom_count"] == "0" for row in source_actionless), [])

    atom_fragments = {row["atom"]: row["default_fragment_de"] for row in dictionary}
    alignment_failures = []
    for row in cards:
        expected = " | ".join(
            f"{index}:{atom}={atom_fragments[atom]}"
            for index, atom in enumerate(row["recipe"].split("+"), 1)
        )
        if row["written_atom_alignment"] != expected or row["all_written_atoms_retained"] != "YES":
            alignment_failures.append(row["event_id"])
    check("all_atom_alignments_exact", not alignment_failures, alignment_failures[:10])
    check("all_microphrases_nonempty", all(row["owner_free_resolved_microphrase_de"].endswith(".") for row in cards), [])
    check("context_clauses_retained", all(card_by_id[event_id]["current_owner_context_clause_de"] == source["contextual_clause_de"] for event_id, source in source_by_id.items()), [])

    # Independently reconstruct previous visible action and argument states.
    normalized: list[dict[str, str]] = []
    for row in old_context:
        normalized.append({
            "cohort": "OLD26_GDT407", "event_id": row["global_running_event_id"],
            "statement_id": row["global_statement_id"], "ordinal": row["card_ordinal_in_statement"],
            "explicit_action": row["explicit_action_roots"], "explicit_argument": row["explicit_argument_roots"],
        })
    for row in current_context:
        normalized.append({
            "cohort": "CURRENT4_GDT539", "event_id": row["event_id"],
            "statement_id": row["statement_id"], "ordinal": row["card_ordinal_in_statement"],
            "explicit_action": row["explicit_action_roots"], "explicit_argument": row["explicit_argument_roots"],
        })
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in normalized:
        by_statement[row["statement_id"]].append(row)
    expected_provenance: dict[str, tuple[str, str, object, str, str, object]] = {}
    for material in by_statement.values():
        material.sort(key=lambda row: int(row["ordinal"]))
        last_action = last_action_event = "NONE"
        last_action_ordinal = 0
        last_argument = last_argument_event = "NONE"
        last_argument_ordinal = 0
        for context in material:
            event_id = context["event_id"]
            if event_id in source_by_id:
                source = source_by_id[event_id]
                inherited_action = source["inherited_action_root"]
                if inherited_action == "NONE":
                    action_tuple = ("NO_ACTIVE_ACTION", "NONE", "NOT_APPLICABLE")
                elif inherited_action == last_action:
                    action_tuple = (
                        "SAME_STATEMENT_VISIBLE_ACTION", last_action_event,
                        int(context["ordinal"]) - last_action_ordinal,
                    )
                else:
                    action_tuple = ("OWNER_CONTEXT_DEFAULT_ACTION", "OWNER_DEFAULT", "NOT_APPLICABLE")
                    if last_action != "NONE":
                        raise RuntimeError(f"Unexpected action mismatch {event_id}")
                explicit_argument = split_roots(source["explicit_argument_roots"])
                inherited_argument = source["inherited_argument_root"]
                if explicit_argument:
                    argument_tuple = ("VISIBLE_ARGUMENT_IN_CARD", event_id, 0)
                elif inherited_argument == "NONE":
                    argument_tuple = ("NO_ACTIVE_ARGUMENT", "NONE", "NOT_APPLICABLE")
                elif inherited_argument == last_argument:
                    argument_tuple = (
                        "SAME_STATEMENT_VISIBLE_ARGUMENT", last_argument_event,
                        int(context["ordinal"]) - last_argument_ordinal,
                    )
                else:
                    argument_tuple = ("OWNER_CONTEXT_DEFAULT_ARGUMENT", "OWNER_DEFAULT", "NOT_APPLICABLE")
                    if last_argument != "NONE":
                        raise RuntimeError(f"Unexpected argument mismatch {event_id}")
                expected_provenance[event_id] = (*action_tuple, *argument_tuple)
            explicit_actions = split_roots(context["explicit_action"])
            if explicit_actions:
                last_action = explicit_actions[-1]
                last_action_event = event_id
                last_action_ordinal = int(context["ordinal"])
            explicit_arguments = split_roots(context["explicit_argument"])
            if explicit_arguments:
                last_argument = explicit_arguments[-1]
                last_argument_event = event_id
                last_argument_ordinal = int(context["ordinal"])

    provenance_failures = []
    for event_id, expected in expected_provenance.items():
        row = card_by_id[event_id]
        observed = (
            row["action_source_type"], row["action_source_event_id"],
            int(row["action_source_card_distance"]) if row["action_source_card_distance"].isdigit() else row["action_source_card_distance"],
            row["argument_source_type"], row["argument_source_event_id"],
            int(row["argument_source_card_distance"]) if row["argument_source_card_distance"].isdigit() else row["argument_source_card_distance"],
        )
        if observed != expected:
            provenance_failures.append((event_id, observed, expected))
    check("all_provenance_reconstructed", len(expected_provenance) == 706 and not provenance_failures, [len(expected_provenance), provenance_failures[:5]])

    action_source_counts = Counter(row["action_source_type"] for row in cards)
    expected_action_sources = Counter({
        "SAME_STATEMENT_VISIBLE_ACTION": 544,
        "OWNER_CONTEXT_DEFAULT_ACTION": 149,
        "NO_ACTIVE_ACTION": 13,
    })
    check("action_source_partition", action_source_counts == expected_action_sources, action_source_counts)
    action_distances = [int(row["action_source_card_distance"]) for row in cards if row["action_source_type"] == "SAME_STATEMENT_VISIBLE_ACTION"]
    check("action_distance_profile", (action_distances.count(1), sum(value > 1 for value in action_distances), max(action_distances)) == (376, 168, 8), [action_distances.count(1), sum(value > 1 for value in action_distances), max(action_distances)])
    check("action_provenance_rows_exact", {row["event_id"] for row in actions} == {row["event_id"] for row in cards if row["effective_action_root"] != "NONE"}, [len({row["event_id"] for row in actions}), sum(row["effective_action_root"] != "NONE" for row in cards)])

    argument_source_counts = Counter(row["argument_source_type"] for row in cards)
    expected_argument_sources = Counter({
        "VISIBLE_ARGUMENT_IN_CARD": 233,
        "SAME_STATEMENT_VISIBLE_ARGUMENT": 355,
        "OWNER_CONTEXT_DEFAULT_ARGUMENT": 104,
        "NO_ACTIVE_ARGUMENT": 14,
    })
    check("argument_source_partition", argument_source_counts == expected_argument_sources, argument_source_counts)
    argument_distances = [int(row["argument_source_card_distance"]) for row in cards if row["argument_source_type"] == "SAME_STATEMENT_VISIBLE_ARGUMENT"]
    check("argument_distance_profile", (argument_distances.count(1), sum(value > 1 for value in argument_distances), max(argument_distances)) == (238, 117, 5), [argument_distances.count(1), sum(value > 1 for value in argument_distances), max(argument_distances)])
    check("argument_provenance_rows_exact", {row["event_id"] for row in arguments} == {row["event_id"] for row in cards if row["argument_source_type"] in {"SAME_STATEMENT_VISIBLE_ARGUMENT", "OWNER_CONTEXT_DEFAULT_ARGUMENT"}}, [len({row["event_id"] for row in arguments}), sum(row["argument_source_type"] in {"SAME_STATEMENT_VISIBLE_ARGUMENT", "OWNER_CONTEXT_DEFAULT_ARGUMENT"} for row in cards)])

    check("current_context_partition", Counter(row["cohort"] for row in cards) == Counter({"OLD26_GDT407": 652, "CURRENT4_GDT539": 54}), Counter(row["cohort"] for row in cards))
    current_cards = [row for row in cards if row["cohort"] == "CURRENT4_GDT539"]
    check("all_current_source_pointers_match", len(current_cards) == 54 and all(row["action_pointer_match"] == "YES" and row["argument_pointer_match"] == "YES" for row in current_cards), [len(current_cards), sum(row["action_pointer_match"] == "YES" and row["argument_pointer_match"] == "YES" for row in current_cards)])
    old_cards = [row for row in cards if row["cohort"] == "OLD26_GDT407"]
    check("old_pointer_absence_explicit", len(old_cards) == 652 and all(row["action_pointer_match"] == "NOT_STORED" and row["argument_pointer_match"] == "NOT_STORED" for row in old_cards), len(old_cards))

    role_counts = Counter(row["completeness_role"] for row in cards)
    expected_roles = Counter({
        "FULL_INHERITED_OPERATION": 687,
        "OBJECTLESS_INHERITED_OPERATION": 6,
        "ARGUMENT_REFERENCE_INITIALIZER": 5,
        "FORMAL_RELATION_PROLOGUE": 4,
        "STANDALONE_GRADED_CLOSE": 3,
        "PURE_CONTINUATION": 1,
    })
    check("six_completeness_roles_exact", role_counts == expected_roles, role_counts)
    role_table = {row["completeness_role"]: int(row["event_count"]) for row in roles}
    check("role_summary_exact", role_table == expected_roles, role_table)
    check("full_operation_flags", sum(row["operation_complete"] == "YES" for row in cards) == 687 and all((row["operation_complete"] == "YES") == (row["completeness_role"] == "FULL_INHERITED_OPERATION") for row in cards), sum(row["operation_complete"] == "YES" for row in cards))

    expected_residual_ids = {
        "G407-E1097", "G407-E1137", "G407-E1179", "G407-E1219", "G407-E1260",
        "G407-E1286", "G407-E1389", "G407-E2195", "G407-E2394", "G407-E3970",
        "G407-E4293", "G515-E0004", "G515-E0100", "G515-E0190", "G515-E0240",
        "G515-E0336", "G515-E0406", "G515-E0461", "G515-E0503",
    }
    check("nineteen_residual_ids_exact", {row["event_id"] for row in residuals} == expected_residual_ids, sorted({row["event_id"] for row in residuals} ^ expected_residual_ids))
    check("residual_roles_complete", all(row["residual_status"] == "COMPLETE_BOUNDED_ROLE__NO_MISSING_ROOT_ASSUMED" and row["resolved_microphrase_de"] for row in residuals), [])

    sequence_counts = Counter(row["state_marker_sequence"] for row in cards)
    expected_sequences = Counter({"OL": 317, "OT": 230, "OT+DY": 76, "DY": 38, "OT+OL": 21, "OL+DY": 19, "OL+OL": 5})
    check("seven_state_sequences_exact", sequence_counts == expected_sequences, sequence_counts)
    sequence_table = {row["state_marker_sequence"]: int(row["event_count"]) for row in sequences}
    check("sequence_summary_exact", sequence_table == expected_sequences, sequence_table)
    sequence_roles = {row["state_marker_sequence"]: row["state_sequence_role"] for row in sequences}
    check("sequence_roles_distinct", len(set(sequence_roles.values())) == 7, sequence_roles)

    root_counts = Counter(row["effective_action_root"] for row in cards if row["effective_action_root"] != "NONE")
    expected_root_counts = Counter({"OK": 166, "SH": 131, "K": 85, "CH": 83, "S": 71, "CHD": 71, "T": 52, "P": 18, "R": 16})
    check("nine_inherited_action_roots_exact", root_counts == expected_root_counts, root_counts)
    root_table = {row["inherited_action_root"]: int(row["actionless_event_count"]) for row in roots}
    check("root_profile_summary_exact", root_table == expected_root_counts, root_table)
    check("effective_argument_count", sum(row["effective_argument_roots"] != "NONE" for row in cards) == 692, sum(row["effective_argument_roots"] != "NONE" for row in cards))

    expected_result = {
        "source_typed_state_card_count": 1656,
        "actionless_state_card_count": 706,
        "inherited_action_card_count": 693,
        "same_statement_visible_action_source_count": 544,
        "immediate_visible_action_source_count": 376,
        "delayed_visible_action_source_count": 168,
        "maximum_visible_action_source_distance": 8,
        "owner_context_default_action_source_count": 149,
        "no_active_action_count": 13,
        "visible_argument_in_card_count": 233,
        "inherited_argument_card_count": 459,
        "same_statement_visible_argument_source_count": 355,
        "immediate_visible_argument_source_count": 238,
        "delayed_visible_argument_source_count": 117,
        "maximum_visible_argument_source_distance": 5,
        "owner_context_default_argument_source_count": 104,
        "no_active_argument_count": 14,
        "cards_with_effective_argument_count": 692,
        "full_inherited_operation_count": 687,
        "nonfull_operation_count": 19,
        "completeness_role_count": 6,
        "residual_role_count": 5,
        "state_sequence_role_count": 7,
        "inherited_action_root_count": 9,
        "current_pointer_checked_card_count": 54,
        "current_pointer_match_count": 54,
    }
    check("result_metrics_exact", all(result.get(key) == value for key, value in expected_result.items()), {key: result.get(key) for key in expected_result})
    check("result_completion_flags", all(result.get(key) is True for key in (
        "all_action_sources_resolved", "all_argument_sources_resolved",
        "all_cards_have_microphrase", "all_written_atoms_retained",
    )), {key: result.get(key) for key in ("all_action_sources_resolved", "all_argument_sources_resolved", "all_cards_have_microphrase", "all_written_atoms_retained")})
    check("zero_scope_mutation", all(result.get(key) == 0 for key in (
        "new_pages", "new_surfaces", "new_recipes", "new_root_values", "new_written_atoms"
    )), {key: result.get(key) for key in ("new_pages", "new_surfaces", "new_recipes", "new_root_values", "new_written_atoms")})

    book = ARTIFACTS["GDT562_ACTIONLESS_STATE_BOOK.md"].read_text(encoding="utf-8")
    needles = ("693", "692", "687", "97,31%", "19 Nicht-Volloperationen", "Keine verlangt einen neuen Stamm")
    check("book_core_findings_present", all(needle in book for needle in needles), [needle for needle in needles if needle not in book])

    before = {name: sha256(path) for name, path in ARTIFACTS.items()}
    replay = subprocess.run(
        [sys.executable, str(RUNNER)], cwd=ROOT, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    after = {name: sha256(path) for name, path in ARTIFACTS.items()}
    check("deterministic_replay_exit", replay.returncode == 0, replay.stderr)
    check("deterministic_artifact_hashes", before == after, {name: [before[name], after[name]] for name in before if before[name] != after[name]})

    payload = {
        "status": "PASS" if all(item["passed"] for item in checks) else "FAIL",
        "check_count": len(checks),
        "passed_count": sum(item["passed"] for item in checks),
        "failed_count": sum(not item["passed"] for item in checks),
        "input_sha256": {name: sha256(path) for name, path in INPUTS.items()},
        "artifact_sha256": {name: sha256(path) for name, path in ARTIFACTS.items()},
        "checks": checks,
    }
    VALIDATION_OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
