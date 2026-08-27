#!/usr/bin/env python3
"""Independent source reconstruction for the GDT577 attachment atlas."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt577_interrupted_modifier_attachment_topology"
OUT = BASE / "artifacts"
G575 = ROOT / "experiments/yolo/gdt575_repeated_relation_modifier_scope_atlas/artifacts"
G576 = ROOT / "experiments/yolo/gdt576_learned_local_sigla_voice/artifacts"
SOURCE_EVENTS = G576 / "gdt576_5122_learned_sigla_event_edition.tsv"
SOURCE_GROUPS = G575 / "gdt575_96_exact_duplicate_phrase_groups.tsv"
SOURCE_SCOPE = G575 / "gdt575_17_outer_inner_scope_pairs.tsv"
SOURCE_OLD_ATTACHMENTS = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts/gdt407_5051_attachment_edition.tsv"
SOURCE_NEW_ATTACHMENTS = ROOT / "experiments/yolo/gdt515_second_random_four_page_full_admission/artifacts/gdt515_factorized_attachments.tsv"
SOURCE_OLD_CLAUSES = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts/gdt416_4576_imperative_clauses.tsv"
INPUTS = {
    "events": SOURCE_EVENTS,
    "groups": SOURCE_GROUPS,
    "scope_pairs": SOURCE_SCOPE,
    "old_attachments": SOURCE_OLD_ATTACHMENTS,
    "new_attachments": SOURCE_NEW_ATTACHMENTS,
    "old_clauses": SOURCE_OLD_CLAUSES,
}
ACTIONS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
CONTROLS = {"OT", "OL", "DY"}
STATUS = (
    "PASS_62_INTERRUPTED_GROUPS__125_SLOTS__75_EXISTING_ATTACHMENTS_REPLAYED__"
    "50_EXPLORATORY_HEAD_CANDIDATES__5_TOPOLOGIES__"
    "ONE_RENDERER_HISTORY_CONFLICT__ZERO_SLOT_COLLAPSE"
)
EXPECTED_TOPOLOGIES = {
    "DISTINCT_ACTION_OCCURRENCES": 35,
    "BRACKETING_SAME_HEAD": 15,
    "SAME_HEAD_SAME_SIDE": 3,
    "ACTIVE_CONTEXT_HEAD": 8,
    "ACTION_PLUS_SEQUENCE_HEAD": 1,
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fixed_map() -> dict[tuple[str, int], tuple[str, int, str, str, str]]:
    result: dict[tuple[str, int], tuple[str, int, str, str, str]] = {}
    for row in read_tsv(SOURCE_OLD_ATTACHMENTS):
        result[(row["global_running_event_id"], int(row["focus_atom_ordinal"]) - 1)] = (
            row["selected_action_global_event_id"],
            int(row["selected_action_atom_ordinal"]) - 1,
            row["action_core"],
            row["duplicate_mode"],
            "GDT407_FIXED_FOCUS_ATTACHMENT",
        )
    for row in read_tsv(SOURCE_NEW_ATTACHMENTS):
        result[(row["event_id"], int(row["focus_atom_ordinal"]) - 1)] = (
            row["selected_action_event_id"],
            int(row["selected_action_atom_ordinal"]) - 1,
            row["action_core"],
            row["duplicate_mode"],
            "GDT515_FIXED_FOCUS_ATTACHMENT",
        )
    return result


def active_before(events: list[dict[str, str]]) -> dict[str, tuple[str, int, str] | None]:
    state: dict[tuple[str, str], tuple[str, int, str]] = {}
    answer: dict[str, tuple[str, int, str] | None] = {}
    for event in events:
        key = (event["physical_page"], event["owner_id"])
        answer[event["event_id"]] = state.get(key)
        for position, atom in enumerate(event["final_context_recipe"].split("+")):
            if atom in ACTIONS:
                state[key] = (event["event_id"], position, atom)
    return answer


def expected_candidate(
    event: dict[str, str], position: int, prior: tuple[str, int, str] | None
) -> tuple[str, int, str, str, str]:
    atoms = event["final_context_recipe"].split("+")
    left = max((index for index, atom in enumerate(atoms) if atom in CONTROLS and index < position), default=-1)
    right = min((index for index, atom in enumerate(atoms) if atom in CONTROLS and index > position), default=len(atoms))
    heads = [index for index, atom in enumerate(atoms) if atom in ACTIONS and left < index < right]
    if heads:
        selected = min(heads, key=lambda index: (abs(index - position), index > position, index))
        placement = "POST_HEAD" if selected < position else "PRE_HEAD"
        return event["event_id"], selected, atoms[selected], placement, "EXPLORATORY_NEAREST_VISIBLE_ACTION"
    if left >= 0:
        return event["event_id"], left, atoms[left], "SEQUENCE_CARRY", "EXPLORATORY_LEFT_SEQUENCE_CARRIER"
    if prior is None:
        raise RuntimeError(f"No candidate head for {event['event_id']}:{position}")
    prior_event, prior_position, prior_root = prior
    return prior_event, prior_position, prior_root, "ACTIVE_CONTEXT", "EXPLORATORY_ACTIVE_CONTEXT_HEAD"


def classify(rows: list[dict[str, str]], event_id: str) -> str:
    keys = {(row["head_kind"], row["head_event_id"], row["head_atom_position_zero_based"]) for row in rows}
    positions = {row["placement"] for row in rows}
    if "SEQUENCE_CARRY" in positions:
        return "ACTION_PLUS_SEQUENCE_HEAD"
    if len(keys) > 1:
        return "DISTINCT_ACTION_OCCURRENCES"
    if "PRE_HEAD" in positions and "POST_HEAD" in positions:
        return "BRACKETING_SAME_HEAD"
    if all(row["head_event_id"] != event_id for row in rows):
        return "ACTIVE_CONTEXT_HEAD"
    return "SAME_HEAD_SAME_SIDE"


def main() -> int:
    events = read_tsv(SOURCE_EVENTS)
    source_groups_all = read_tsv(SOURCE_GROUPS)
    source_groups = [row for row in source_groups_all if row["duplicate_topology"] == "SAME_ROOT_INTERRUPTED"]
    source_scope = read_tsv(SOURCE_SCOPE)
    old_clauses = {row["global_running_event_id"]: row for row in read_tsv(SOURCE_OLD_CLAUSES)}
    slots = read_tsv(OUT / "gdt577_125_slot_head_assignments.tsv")
    groups = read_tsv(OUT / "gdt577_62_interrupted_group_topology.tsv")
    cards = read_tsv(OUT / "gdt577_5_attachment_topology_cards.tsv")
    profiles = read_tsv(OUT / "gdt577_59_event_sequence_profiles.tsv")
    conflicts = read_tsv(OUT / "gdt577_1_renderer_history_conflict.tsv")
    result = json.loads((OUT / "gdt577_result.json").read_text(encoding="utf-8"))
    event_by_id = {row["event_id"]: row for row in events}
    group_by_id = {row["gdt575_duplicate_group_id"]: row for row in groups}
    fixed = fixed_map()
    prior = active_before(events)
    slots_by_group: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in slots:
        slots_by_group[row["gdt575_duplicate_group_id"]].append(row)

    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, observed: object, expected: object) -> None:
        checks.append({
            "check": name,
            "status": "PASS" if passed else "FAIL",
            "observed": observed,
            "expected": expected,
        })

    check("status", result["status"] == STATUS, result["status"], STATUS)
    check("source_event_rows", len(events) == 5122, len(events), 5122)
    check("source_duplicate_rows", len(source_groups_all) == 96, len(source_groups_all), 96)
    check("source_interrupted_rows", len(source_groups) == 62, len(source_groups), 62)
    check("source_scope_rows", len(source_scope) == 17, len(source_scope), 17)
    check("slot_rows", len(slots) == 125, len(slots), 125)
    check("group_rows", len(groups) == 62, len(groups), 62)
    check("card_rows", len(cards) == 5, len(cards), 5)
    check("profile_rows", len(profiles) == 59, len(profiles), 59)
    check("conflict_rows", len(conflicts) == 1, len(conflicts), 1)
    check("input_hashes", result["input_sha256"] == {key: sha256(path) for key, path in INPUTS.items()}, result["input_sha256"], {key: sha256(path) for key, path in INPUTS.items()})

    source_ids = {row["duplicate_group_id"] for row in source_groups}
    check("group_id_set", set(group_by_id) == source_ids, len(set(group_by_id) & source_ids), 62)
    expected_slot_keys = {
        (row["duplicate_group_id"], int(position))
        for row in source_groups
        for position in row["underlying_atom_positions_zero_based"].split("+")
    }
    observed_slot_keys = {(row["gdt575_duplicate_group_id"], int(row["slot_atom_position_zero_based"])) for row in slots}
    check("slot_keys_exact", observed_slot_keys == expected_slot_keys, len(observed_slot_keys), 125)
    check("slot_keys_unique", len(observed_slot_keys) == len(slots), len(observed_slot_keys), 125)
    check("all_scope_plain", set(row["repeat_scope"] for row in slots) == {"PLAIN"}, sorted(set(row["repeat_scope"] for row in slots)), ["PLAIN"])
    check("recipes_preserved", all(row["final_context_recipe"] == event_by_id[row["event_id"]]["final_context_recipe"] for row in slots), "all", "all")
    check("slot_atoms_preserved", all(event_by_id[row["event_id"]]["final_context_recipe"].split("+")[int(row["slot_atom_position_zero_based"])] == row["repeat_root"] for row in slots), "all", "all")
    check("group_root_counts", Counter(row["repeat_root"] for row in groups) == Counter({"E": 35, "O": 16, "D_ADDR": 9, "EE": 1, "AR": 1}), dict(Counter(row["repeat_root"] for row in groups)), {"E": 35, "O": 16, "D_ADDR": 9, "EE": 1, "AR": 1})

    fixed_rows = [row for row in slots if "FIXED" in row["assignment_source"]]
    candidate_rows = [row for row in slots if row["assignment_source"].startswith("EXPLORATORY")]
    check("fixed_count", len(fixed_rows) == 75, len(fixed_rows), 75)
    check("candidate_count", len(candidate_rows) == 50, len(candidate_rows), 50)
    check("fixed_root_set", set(row["repeat_root"] for row in fixed_rows) == {"E", "EE", "AR"}, sorted(set(row["repeat_root"] for row in fixed_rows)), ["AR", "E", "EE"])
    check("candidate_root_set", set(row["repeat_root"] for row in candidate_rows) == {"D_ADDR", "O"}, sorted(set(row["repeat_root"] for row in candidate_rows)), ["D_ADDR", "O"])
    fixed_ok = True
    for row in fixed_rows:
        source = fixed[(row["event_id"], int(row["slot_atom_position_zero_based"]))]
        fixed_ok &= (
            row["head_event_id"] == source[0]
            and int(row["head_atom_position_zero_based"]) == source[1]
            and row["head_root"] == source[2]
            and row["duplicate_mode"] == source[3]
            and row["assignment_source"] == source[4]
        )
    check("fixed_attachments_exact", fixed_ok, "all" if fixed_ok else "mismatch", "all")
    check("fixed_source_counts", Counter(row["assignment_source"] for row in fixed_rows) == Counter({"GDT407_FIXED_FOCUS_ATTACHMENT": 71, "GDT515_FIXED_FOCUS_ATTACHMENT": 4}), dict(Counter(row["assignment_source"] for row in fixed_rows)), {"GDT407_FIXED_FOCUS_ATTACHMENT": 71, "GDT515_FIXED_FOCUS_ATTACHMENT": 4})

    candidate_ok = True
    for row in candidate_rows:
        event = event_by_id[row["event_id"]]
        expected = expected_candidate(event, int(row["slot_atom_position_zero_based"]), prior[event["event_id"]])
        candidate_ok &= (
            row["head_event_id"] == expected[0]
            and int(row["head_atom_position_zero_based"]) == expected[1]
            and row["head_root"] == expected[2]
            and row["placement"] == expected[3]
            and row["assignment_source"] == expected[4]
        )
    check("candidate_rule_exact", candidate_ok, "all" if candidate_ok else "mismatch", "all")
    check("candidate_source_counts", Counter(row["assignment_source"] for row in candidate_rows) == Counter({"EXPLORATORY_NEAREST_VISIBLE_ACTION": 35, "EXPLORATORY_ACTIVE_CONTEXT_HEAD": 14, "EXPLORATORY_LEFT_SEQUENCE_CARRIER": 1}), dict(Counter(row["assignment_source"] for row in candidate_rows)), {"EXPLORATORY_NEAREST_VISIBLE_ACTION": 35, "EXPLORATORY_ACTIVE_CONTEXT_HEAD": 14, "EXPLORATORY_LEFT_SEQUENCE_CARRIER": 1})
    check("candidate_placement_counts", Counter(row["placement"] for row in candidate_rows) == Counter({"POST_HEAD": 21, "PRE_HEAD": 14, "ACTIVE_CONTEXT": 14, "SEQUENCE_CARRY": 1}), dict(Counter(row["placement"] for row in candidate_rows)), {"POST_HEAD": 21, "PRE_HEAD": 14, "ACTIVE_CONTEXT": 14, "SEQUENCE_CARRY": 1})

    group_topology_ok = all(classify(slots_by_group[group_id], group_by_id[group_id]["event_id"]) == group_by_id[group_id]["attachment_topology"] for group_id in group_by_id)
    check("group_topology_recomputed", group_topology_ok, "all" if group_topology_ok else "mismatch", "all")
    check("topology_counts", Counter(row["attachment_topology"] for row in groups) == Counter(EXPECTED_TOPOLOGIES), dict(Counter(row["attachment_topology"] for row in groups)), EXPECTED_TOPOLOGIES)
    check("card_topology_set", {row["attachment_topology"] for row in cards} == set(EXPECTED_TOPOLOGIES), sorted(row["attachment_topology"] for row in cards), sorted(EXPECTED_TOPOLOGIES))
    check("card_group_counts", all(int(row["group_count"]) == EXPECTED_TOPOLOGIES[row["attachment_topology"]] for row in cards), {row["attachment_topology"]: int(row["group_count"]) for row in cards}, EXPECTED_TOPOLOGIES)
    check("group_slot_counts", all(int(group_by_id[group_id]["slot_count"]) == len(rows) for group_id, rows in slots_by_group.items()), "all", "all")

    marker_counts = Counter(row["repeat_marker_candidate"] for row in slots)
    check("repeat_marker_counts", marker_counts == Counter({"FIRST_FULL": 62, "ERNEUT": 52, "WIEDER": 10, "NOCHMALS": 1}), dict(marker_counts), {"FIRST_FULL": 62, "ERNEUT": 52, "WIEDER": 10, "NOCHMALS": 1})
    overlapping = {event_id for event_id, rows in defaultdict(list, {key: [row for row in groups if row["event_id"] == key] for key in {row["event_id"] for row in groups}}).items() if len(rows) > 1}
    check("overlapping_events", overlapping == {"G407-E0966", "G407-E1755", "G407-E3605"}, sorted(overlapping), ["G407-E0966", "G407-E1755", "G407-E3605"])
    check("event_profile_set", {row["event_id"] for row in profiles} == {row["event_id"] for row in groups}, len({row["event_id"] for row in profiles}), 59)
    check("scope_pair_disjoint", not ({row["event_id"] for row in groups} & {row["event_id"] for row in source_scope}), sorted({row["event_id"] for row in groups} & {row["event_id"] for row in source_scope}), [])

    conflict = conflicts[0]
    check("conflict_identity", (conflict["event_id"], conflict["gdt575_duplicate_group_id"], conflict["root"]) == ("G407-E1755", "GDT575-D040", "AR"), [conflict["event_id"], conflict["gdt575_duplicate_group_id"], conflict["root"]], ["G407-E1755", "GDT575-D040", "AR"])
    check("conflict_prior_clause", conflict["gdt416_prior_clause_de"] == old_clauses["G407-E1755"]["imperative_clause_de"] and "[außen]" in conflict["gdt416_prior_clause_de"] and "[innen]" in conflict["gdt416_prior_clause_de"], "matched", "matched with both markers")
    check("conflict_current_clause", conflict["gdt576_current_clause_de"] == event_by_id["G407-E1755"]["learned_sigla_working_clause_de"] and "[außen]" not in conflict["gdt576_current_clause_de"], "matched", "matched without old markers")
    check("conflict_single_modes", conflict["fixed_duplicate_modes"] == "SINGLE+SINGLE", conflict["fixed_duplicate_modes"], "SINGLE+SINGLE")
    check("quarantined_groups", sum(row["renderer_ready"] == "NO" for row in groups) == 2, sum(row["renderer_ready"] == "NO" for row in groups), 2)
    check("quarantined_events", sum(row["renderer_ready"] == "NO" for row in profiles) == 1, sum(row["renderer_ready"] == "NO" for row in profiles), 1)
    check("renderer_ready_counts", (result["renderer_ready_group_count"], result["renderer_ready_event_count"]) == (60, 58), [result["renderer_ready_group_count"], result["renderer_ready_event_count"]], [60, 58])

    check("sealed_pages_absent", not any(row["physical_page"].startswith("f84") for row in slots), "none", "none")
    check("slot_guards", all(row["guard"] == "EVERY_WRITTEN_SLOT_RETAINED__CANDIDATE_HEAD_IS_WORKSHOP_VOICE_ONLY" for row in slots), "all", "all")
    check("group_guards", all(row["guard"] == "GROUP_TOPOLOGY_ONLY__NO_SLOT_OR_SCOPE_COLLAPSE" for row in groups), "all", "all")
    check("profile_guards", all(row["guard"] == "EVENT_LEVEL_OVERLAP_CONTROL__NEVER_RENDER_GROUPS_INDEPENDENTLY" for row in profiles), "all", "all")
    check("result_limits", result["no_new_page"] and result["no_root_change"] and result["no_slot_collapse"], [result["no_new_page"], result["no_root_change"], result["no_slot_collapse"]], [True, True, True])
    check("historical_analogy_count", len(result["historical_voice_analogies"]) == 3, len(result["historical_voice_analogies"]), 3)

    failures = [row for row in checks if row["status"] != "PASS"]
    validation = {
        "experiment_id": "GDT577",
        "status": "PASS" if not failures else "FAIL",
        "check_count": len(checks),
        "pass_count": len(checks) - len(failures),
        "fail_count": len(failures),
        "checks": checks,
    }
    (OUT / "gdt577_validation.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
