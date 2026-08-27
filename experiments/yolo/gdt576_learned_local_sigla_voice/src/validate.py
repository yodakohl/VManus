#!/usr/bin/env python3
"""Independent validation for GDT576 learned local-sigla voice."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt576_learned_local_sigla_voice"
OUT = BASE / "artifacts"
G574 = ROOT / "experiments/yolo/gdt574_adjacent_action_count_voice/artifacts"
G575 = ROOT / "experiments/yolo/gdt575_repeated_relation_modifier_scope_atlas/artifacts"
SOURCE_EVENTS = G574 / "gdt574_5122_action_count_event_edition.tsv"
SOURCE_STATEMENTS = G574 / "gdt574_793_action_count_statement_edition.tsv"
SOURCE_PAGES = G574 / "gdt574_30_page_action_count_profiles.tsv"
SOURCE_GROUPS = G575 / "gdt575_96_exact_duplicate_phrase_groups.tsv"
STATUS = (
    "PASS_4_FAMILY_FRAMES__12_LEARNED_SIGLA_CARDS__773_LOCAL_SLOTS__"
    "715_CLAUSES_DIFFERENTIATED__31_COLLISIONS_RESOLVED__"
    "5122_EXACT_ROUNDTRIPS__ZERO_ROOT_CHANGE"
)
EXPECTED = {
    "D_ADDR": ("an der D-Stelle", 519),
    "A_ADDR": ("an der A-Stelle", 63),
    "AM_ADDR": ("an der AM-Stelle", 74),
    "S_ADDR": ("an der S-Stelle", 16),
    "LOCAL_CHAR_F": ("bei der f-Kennmarke", 48),
    "M_LOCAL": ("bei der m-Ortsmarke", 14),
    "D_LABEL": ("beim d-Vermerk", 2),
    "LOCAL_CHAR_I": ("mit der i-Variante", 18),
    "LOCAL_CHAR_G": ("mit der g-Variante", 12),
    "G_LABEL": ("beim G-Vermerk", 4),
    "LOCAL_CHAR_B": ("mit der b-Variante", 2),
    "LOCAL_CHAR_J": ("mit der j-Variante", 1),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    source_events = read_tsv(SOURCE_EVENTS)
    source_statements = read_tsv(SOURCE_STATEMENTS)
    source_pages = read_tsv(SOURCE_PAGES)
    source_groups = read_tsv(SOURCE_GROUPS)
    frames = read_tsv(OUT / "gdt576_4_local_function_frames.tsv")
    cards = read_tsv(OUT / "gdt576_12_learned_sigla_cards.tsv")
    assignments = read_tsv(OUT / "gdt576_773_sigla_voice_assignments.tsv")
    changed = read_tsv(OUT / "gdt576_715_changed_sigla_clauses.tsv")
    collisions = read_tsv(OUT / "gdt576_31_resolved_surface_collisions.tsv")
    events = read_tsv(OUT / "gdt576_5122_learned_sigla_event_edition.tsv")
    statements = read_tsv(OUT / "gdt576_793_learned_sigla_statement_edition.tsv")
    pages = read_tsv(OUT / "gdt576_30_page_sigla_profiles.tsv")
    result = json.loads((OUT / "gdt576_result.json").read_text(encoding="utf-8"))

    source_event_by_id = {row["event_id"]: row for row in source_events}
    event_by_id = {row["event_id"]: row for row in events}
    source_statement_by_id = {row["statement_id"]: row for row in source_statements}
    card_by_atom = {row["atom"]: row for row in cards}
    assignment_by_event_position = {
        (row["event_id"], int(row["atom_position_zero_based"])): row for row in assignments
    }
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, observed: object, expected: object) -> None:
        checks.append({
            "check": name,
            "status": "PASS" if passed else "FAIL",
            "observed": observed,
            "expected": expected,
        })

    check("status", result["status"] == STATUS, result["status"], STATUS)
    check("source_event_rows", len(source_events) == 5122, len(source_events), 5122)
    check("source_statement_rows", len(source_statements) == 793, len(source_statements), 793)
    check("source_page_rows", len(source_pages) == 30, len(source_pages), 30)
    check("frame_rows", len(frames) == 4, len(frames), 4)
    check("card_rows", len(cards) == 12, len(cards), 12)
    check("assignment_rows", len(assignments) == 773, len(assignments), 773)
    check("changed_rows", len(changed) == 715, len(changed), 715)
    check("collision_rows", len(collisions) == 31, len(collisions), 31)
    check("event_rows", len(events) == 5122, len(events), 5122)
    check("statement_rows", len(statements) == 793, len(statements), 793)
    check("page_rows", len(pages) == 30, len(pages), 30)
    check("input_hash", sha256(SOURCE_EVENTS) == result["event_input_sha256"], sha256(SOURCE_EVENTS), result["event_input_sha256"])
    check("event_id_order", [row["event_id"] for row in events] == [row["event_id"] for row in source_events], "same" if [row["event_id"] for row in events] == [row["event_id"] for row in source_events] else "different", "same")
    check("statement_id_order", [row["statement_id"] for row in statements] == [row["statement_id"] for row in source_statements], "same" if [row["statement_id"] for row in statements] == [row["statement_id"] for row in source_statements] else "different", "same")
    check("page_order", [row["physical_page"] for row in pages] == [row["physical_page"] for row in source_pages], "same" if [row["physical_page"] for row in pages] == [row["physical_page"] for row in source_pages] else "different", "same")
    check("event_recipes", all(row["final_context_recipe"] == source_event_by_id[row["event_id"]]["final_context_recipe"] for row in events), "all", "all")
    check("event_surfaces", all(row["surface"] == source_event_by_id[row["event_id"]]["surface"] for row in events), "all", "all")
    check("event_roundtrips", all(row["gdt574_source_roundtrip_de"] == source_event_by_id[row["event_id"]]["action_count_working_clause_de"] for row in events), sum(row["gdt574_source_roundtrip_de"] == source_event_by_id[row["event_id"]]["action_count_working_clause_de"] for row in events), 5122)
    check("event_source_columns", all(row["gdt574_action_count_clause_de"] == source_event_by_id[row["event_id"]]["action_count_working_clause_de"] for row in events), "all", "all")
    check("changed_event_set", {row["event_id"] for row in changed} == {row["event_id"] for row in events if row["sigla_voice_changed"] == "YES"}, len({row["event_id"] for row in changed}), 715)
    check("unchanged_clauses", all(row["learned_sigla_working_clause_de"] == row["gdt574_action_count_clause_de"] for row in events if row["sigla_voice_changed"] == "NO"), "all", "all")
    check("generic_address_removed", sum(int(row["remaining_generic_address_phrase_count"]) for row in events) == 0, sum(int(row["remaining_generic_address_phrase_count"]) for row in events), 0)
    check("generic_variant_removed", sum(int(row["remaining_generic_variant_phrase_count"]) for row in events) == 0, sum(int(row["remaining_generic_variant_phrase_count"]) for row in events), 0)

    atom_counts = Counter()
    for source in source_events:
        atom_counts.update(token for token in source["final_context_recipe"].split("+") if token in EXPECTED)
    check("source_atom_total", sum(atom_counts.values()) == 773, sum(atom_counts.values()), 773)
    check("assignment_atom_counts", Counter(row["atom"] for row in assignments) == atom_counts, dict(Counter(row["atom"] for row in assignments)), dict(atom_counts))
    check("card_atom_set", set(card_by_atom) == set(EXPECTED), sorted(card_by_atom), sorted(EXPECTED))
    check("card_occurrence_counts", all(int(card_by_atom[atom]["occurrence_count"]) == count for atom, (_, count) in EXPECTED.items()), {atom: int(card_by_atom[atom]["occurrence_count"]) for atom in card_by_atom}, {atom: count for atom, (_, count) in EXPECTED.items()})
    check("card_target_phrases", all(card_by_atom[atom]["rendered_phrase_de"] == phrase for atom, (phrase, _) in EXPECTED.items()), {atom: card_by_atom[atom]["rendered_phrase_de"] for atom in card_by_atom}, {atom: phrase for atom, (phrase, _) in EXPECTED.items()})
    check("assignment_atom_positions", all(source_event_by_id[row["event_id"]]["final_context_recipe"].split("+")[int(row["atom_position_zero_based"])] == row["atom"] for row in assignments), "all", "all")
    check("assignment_target_cards", all(row["target_fragment_de"].casefold().startswith(EXPECTED[row["atom"]][0].casefold()) for row in assignments), "all", "all")
    check("assignment_source_forms", all(re.match(r"(?i)^(?:an der bezeichneten Stelle|mit der lokalen Variante(?: i)?)(?: im (?:äußeren|inneren) Zweig)?$", row["source_fragment_de"]) for row in assignments), "all", "all")
    check("assignment_spans", all(source_event_by_id[row["event_id"]]["action_count_working_clause_de"][int(row["source_start"]):int(row["source_end"])] == row["source_fragment_de"] and event_by_id[row["event_id"]]["learned_sigla_working_clause_de"][int(row["target_start"]):int(row["target_end"])] == row["target_fragment_de"] for row in assignments), "all", "all")
    check("assignment_keys_unique", len(assignment_by_event_position) == 773, len(assignment_by_event_position), 773)

    different_source = [row for row in source_groups if row["duplicate_topology"].startswith("DIFFERENT_ROOTS")]
    check("different_root_source_groups", len(different_source) == 31, len(different_source), 31)
    check("collision_source_ids", {row["gdt575_duplicate_group_id"] for row in collisions} == {row["duplicate_group_id"] for row in different_source}, len({row["gdt575_duplicate_group_id"] for row in collisions}), 31)
    check("collision_all_resolved", all(row["collision_resolved"] == "YES" for row in collisions), "all", "all")
    check("collision_targets_distinct", all(len(set(part.casefold() for part in row["target_distinct_phrases_de"].split("|"))) == int(row["distinct_target_phrase_count"]) == len(row["underlying_atom_sequence"].split("+")) for row in collisions), "all", "all")
    check("collision_target_clauses", all(row["target_clause_de"] == event_by_id[row["event_id"]]["learned_sigla_working_clause_de"] for row in collisions), "all", "all")
    check("same_root_groups_retained", sum(row["duplicate_topology"].startswith("SAME_ROOT") for row in source_groups) == result["remaining_same_root_duplicate_group_count"] == 65, result["remaining_same_root_duplicate_group_count"], 65)

    statement_ok = True
    for row in statements:
        source = source_statement_by_id[row["statement_id"]]
        members = [event_by_id[event_id] for event_id in row["event_ids"].split("|")]
        statement_ok &= row["gdt574_action_count_reading_de"] == source["action_count_working_reading_de"]
        statement_ok &= row["gdt574_source_roundtrip_de"] == source["action_count_working_reading_de"]
        statement_ok &= row["learned_sigla_working_reading_de"] == " ".join(member["learned_sigla_working_clause_de"] for member in members)
    check("statement_rebuilds", statement_ok, "all" if statement_ok else "mismatch", "all")
    check("changed_statements", sum(row["sigla_statement_changed"] == "YES" for row in statements) == 294, sum(row["sigla_statement_changed"] == "YES" for row in statements), 294)
    check("changed_pages", sum(int(row["changed_event_count"]) > 0 for row in pages) == 28, sum(int(row["changed_event_count"]) > 0 for row in pages), 28)
    check("changed_state_events", result["changed_state_event_count"] == 123, result["changed_state_event_count"], 123)
    check("changed_nonstate_events", result["changed_nonstate_event_count"] == 592, result["changed_nonstate_event_count"], 592)
    check("address_assignments", result["address_assignment_count"] == 736, result["address_assignment_count"], 736)
    check("variant_assignments", result["variant_assignment_count"] == 37, result["variant_assignment_count"], 37)
    check("frame_members", sum(int(row["member_card_count"]) for row in frames) == 12, sum(int(row["member_card_count"]) for row in frames), 12)
    check("frame_occurrences", sum(int(row["occurrence_count"]) for row in frames) == 773, sum(int(row["occurrence_count"]) for row in frames), 773)
    check("scope_preserved", Counter(row["scope"] for row in assignments) == Counter({"PLAIN": 771, "OUTER": 1, "INNER": 1}), dict(Counter(row["scope"] for row in assignments)), {"PLAIN": 771, "OUTER": 1, "INNER": 1})
    check("no_new_pages", not any(row["physical_page"].startswith("f84") for row in events), "none", "none")
    check("assignment_guards", all(row["guard"] == "LEARNED_SIGLUM_VOICE_ONLY__SOURCE_ATOM_POSITION_RETAINED" for row in assignments), "all", "all")
    check("event_guards", all(row["guard"] == "COMPLETE_EVENT_ORDER__GDT574_SOURCE_ROUNDTRIP_EXACT" for row in events), "all", "all")
    check("statement_guards", all(row["guard"] == "STATEMENT_ORDER_AND_BOUNDARIES_UNCHANGED__SOURCE_ROUNDTRIP_EXACT" for row in statements), "all", "all")

    failures = [row for row in checks if row["status"] != "PASS"]
    validation = {
        "experiment_id": "GDT576",
        "status": "PASS" if not failures else "FAIL",
        "check_count": len(checks),
        "pass_count": len(checks) - len(failures),
        "fail_count": len(failures),
        "checks": checks,
    }
    (OUT / "gdt576_validation.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
