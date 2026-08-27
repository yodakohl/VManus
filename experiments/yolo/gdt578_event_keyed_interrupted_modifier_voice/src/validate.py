#!/usr/bin/env python3
"""Independent reconstruction checks for the GDT578 event-keyed voice edition."""

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
BASE = ROOT / "experiments/yolo/gdt578_event_keyed_interrupted_modifier_voice"
OUT = BASE / "artifacts"
G568 = ROOT / "experiments/yolo/gdt568_twenty_owner_action_voice_frames/artifacts"
G575 = ROOT / "experiments/yolo/gdt575_repeated_relation_modifier_scope_atlas/artifacts"
G576 = ROOT / "experiments/yolo/gdt576_learned_local_sigla_voice/artifacts"
G577 = ROOT / "experiments/yolo/gdt577_interrupted_modifier_attachment_topology/artifacts"

INPUTS = {
    "events": G576 / "gdt576_5122_learned_sigla_event_edition.tsv",
    "statements": G576 / "gdt576_793_learned_sigla_statement_edition.tsv",
    "pages": G576 / "gdt576_30_page_sigla_profiles.tsv",
    "sigla": G576 / "gdt576_773_sigla_voice_assignments.tsv",
    "slots": G577 / "gdt577_125_slot_head_assignments.tsv",
    "groups": G577 / "gdt577_62_interrupted_group_topology.tsv",
    "profiles": G577 / "gdt577_59_event_sequence_profiles.tsv",
    "scope_pairs": G575 / "gdt575_17_outer_inner_scope_pairs.tsv",
    "all_duplicate_groups": G575 / "gdt575_96_exact_duplicate_phrase_groups.tsv",
    "action_cells": G568 / "gdt568_45_register_action_cells.tsv",
}
OUTPUTS = {
    "heads": OUT / "gdt578_20_action_head_voice_cards.tsv",
    "templates": OUT / "gdt578_5_attachment_voice_templates.tsv",
    "prose_frames": OUT / "gdt578_3_prose_voice_frames.tsv",
    "fragments": OUT / "gdt578_173_ordered_modifier_fragments.tsv",
    "voice_slots": OUT / "gdt578_121_repeat_slot_voice_assignments.tsv",
    "particles": OUT / "gdt578_61_repeat_particle_spans.tsv",
    "respun_sigla": OUT / "gdt578_35_respun_sigla_spans.tsv",
    "event_cards": OUT / "gdt578_58_event_cards.tsv",
    "events": OUT / "gdt578_5122_attachment_voice_event_edition.tsv",
    "statements": OUT / "gdt578_793_attachment_voice_statement_edition.tsv",
    "pages": OUT / "gdt578_30_page_attachment_voice_profiles.tsv",
}

STATUS = (
    "PASS_5_ATTACHMENT_CLASSES__3_PROSE_FRAMES__20_HEAD_VOICES__58_EVENT_CARDS__60_GROUPS__"
    "121_REPEAT_SLOTS__173_ORDERED_MODIFIER_FRAGMENTS__61_PARTICLES__"
    "5122_EXACT_ROUNDTRIPS__ONE_CONFLICT_UNCHANGED"
)
CONFLICT_EVENT = "G407-E1755"
CONFLICT_STATEMENT = "G407-S149"
CONFLICT_PAGE = "f75r"
OVERLAPPING_RENDER_EVENTS = {"G407-E0966", "G407-E3605"}
TEXT_COLLISION_EVENTS = {"G407-E1955", "G407-E2638"}

ACTIONS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
ARGUMENTS = {"Y", "AIIN", "AIN", "OR"}
STATE_CONTROLS = {"OT", "OL", "DY"}
EXPECTED_READY_GROUP_TOPOLOGIES = Counter({
    "DISTINCT_ACTION_OCCURRENCES": 35,
    "BRACKETING_SAME_HEAD": 15,
    "SAME_HEAD_SAME_SIDE": 3,
    "ACTIVE_CONTEXT_HEAD": 6,
    "ACTION_PLUS_SEQUENCE_HEAD": 1,
})
EXPECTED_PARTICLES = Counter({
    "ebenfalls": 32,
    "erneut": 20,
    "wieder": 8,
    "nochmals": 1,
})
EXPECTED_PROSE_FRAMES = {
    "ACTION_HEAD": "beim {head}: {display}",
    "ACTIVE_CONTEXT_HEAD": "beim fortgeführten {head}: {display}",
    "SEQUENCE_HEAD": "bei der Fortsetzung: {display}",
}
EXPECTED_CLASS_FRAMES = {
    "DISTINCT_ACTION_OCCURRENCES": "ACTION_HEAD",
    "BRACKETING_SAME_HEAD": "ACTION_HEAD",
    "SAME_HEAD_SAME_SIDE": "ACTION_HEAD",
    "ACTIVE_CONTEXT_HEAD": "ACTIVE_CONTEXT_HEAD",
    "ACTION_PLUS_SEQUENCE_HEAD": "ACTION_HEAD|SEQUENCE_HEAD",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def unique_index(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    index = {row[key]: row for row in rows}
    if len(index) != len(rows):
        raise RuntimeError(f"Duplicate {key} in validation input")
    return index


def expected_particle(
    slot: dict[str, str],
    group: dict[str, str],
    slots_in_group: list[dict[str, str]],
) -> str:
    """Recompute the bounded repeat-particle rule from GDT577 columns."""
    occurrence = int(slot["slot_occurrence_in_group"])
    if occurrence == 1:
        return "NONE"
    if occurrence >= 3:
        return "nochmals"
    if slot["repeat_root"] in {"D_ADDR", "AR"}:
        return "wieder"
    first = min(slots_in_group, key=lambda row: int(row["slot_occurrence_in_group"]))
    if (
        group["attachment_topology"] == "DISTINCT_ACTION_OCCURRENCES"
        and slot["head_identity"] != first["head_identity"]
    ):
        return "ebenfalls"
    return "erneut"


def main() -> int:
    source_events = read_tsv(INPUTS["events"])
    source_statements = read_tsv(INPUTS["statements"])
    source_pages = read_tsv(INPUTS["pages"])
    source_sigla = read_tsv(INPUTS["sigla"])
    source_slots = read_tsv(INPUTS["slots"])
    source_groups = read_tsv(INPUTS["groups"])
    source_profiles = read_tsv(INPUTS["profiles"])
    source_scope_pairs = read_tsv(INPUTS["scope_pairs"])
    source_duplicate_groups = read_tsv(INPUTS["all_duplicate_groups"])
    source_action_cells = read_tsv(INPUTS["action_cells"])

    heads = read_tsv(OUTPUTS["heads"])
    templates = read_tsv(OUTPUTS["templates"])
    prose_frames = read_tsv(OUTPUTS["prose_frames"])
    fragments = read_tsv(OUTPUTS["fragments"])
    voice_slots = read_tsv(OUTPUTS["voice_slots"])
    particles = read_tsv(OUTPUTS["particles"])
    respun_sigla = read_tsv(OUTPUTS["respun_sigla"])
    event_cards = read_tsv(OUTPUTS["event_cards"])
    events = read_tsv(OUTPUTS["events"])
    statements = read_tsv(OUTPUTS["statements"])
    pages = read_tsv(OUTPUTS["pages"])
    result = json.loads((OUT / "gdt578_result.json").read_text(encoding="utf-8"))

    source_event_by_id = unique_index(source_events, "event_id")
    source_statement_by_id = unique_index(source_statements, "statement_id")
    source_page_by_id = unique_index(source_pages, "physical_page")
    source_profile_by_id = unique_index(source_profiles, "event_id")
    source_sigla_by_key = {
        (row["event_id"], int(row["atom_position_zero_based"])): row
        for row in source_sigla
    }
    if len(source_sigla_by_key) != len(source_sigla):
        raise RuntimeError("Duplicate source sigla position")

    event_by_id = unique_index(events, "event_id")
    statement_by_id = unique_index(statements, "statement_id")
    page_by_id = unique_index(pages, "physical_page")
    card_by_event = unique_index(event_cards, "event_id")

    ready_groups = [row for row in source_groups if row["renderer_ready"] == "YES"]
    ready_group_by_id = {
        row["gdt575_duplicate_group_id"]: row for row in ready_groups
    }
    ready_group_ids = set(ready_group_by_id)
    ready_profiles = [row for row in source_profiles if row["renderer_ready"] == "YES"]
    ready_event_ids = {row["event_id"] for row in ready_profiles}
    ready_slots = [
        row for row in source_slots
        if row["gdt575_duplicate_group_id"] in ready_group_ids
    ]
    ready_slot_by_ordinal = {row["slot_ordinal"]: row for row in ready_slots}
    if len(ready_slot_by_ordinal) != len(ready_slots):
        raise RuntimeError("Duplicate source ready-slot ordinal")
    ready_slots_by_group: dict[str, list[dict[str, str]]] = defaultdict(list)
    ready_slots_by_event: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in ready_slots:
        ready_slots_by_group[row["gdt575_duplicate_group_id"]].append(row)
        ready_slots_by_event[row["event_id"]].append(row)

    fragments_by_event: dict[str, list[dict[str, str]]] = defaultdict(list)
    fragment_by_key: dict[tuple[str, int], dict[str, str]] = {}
    for row in fragments:
        key = (row["event_id"], int(row["atom_position_zero_based"]))
        if key in fragment_by_key:
            raise RuntimeError(f"Duplicate modifier fragment {key}")
        fragment_by_key[key] = row
        fragments_by_event[row["event_id"]].append(row)

    voice_slot_by_ordinal = {row["gdt577_slot_ordinal"]: row for row in voice_slots}
    if len(voice_slot_by_ordinal) != len(voice_slots):
        raise RuntimeError("Duplicate rendered slot ordinal")
    particles_by_key = {
        (row["event_id"], row["gdt575_duplicate_group_id"], row["slot_occurrence_in_group"]): row
        for row in particles
    }
    if len(particles_by_key) != len(particles):
        raise RuntimeError("Duplicate repeat-particle key")
    respun_sigla_by_key = {
        (row["event_id"], int(row["atom_position_zero_based"])): row
        for row in respun_sigla
    }
    if len(respun_sigla_by_key) != len(respun_sigla):
        raise RuntimeError("Duplicate respun sigla position")

    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, observed: object, expected: object) -> None:
        checks.append({
            "check": name,
            "status": "PASS" if passed else "FAIL",
            "observed": observed,
            "expected": expected,
        })

    check("status", result.get("status") == STATUS, result.get("status"), STATUS)
    check(
        "source_counts",
        [len(source_events), len(source_statements), len(source_pages)] == [5122, 793, 30],
        [len(source_events), len(source_statements), len(source_pages)],
        [5122, 793, 30],
    )
    check(
        "edition_counts",
        [len(events), len(statements), len(pages)] == [5122, 793, 30],
        [len(events), len(statements), len(pages)],
        [5122, 793, 30],
    )
    check(
        "artifact_counts",
        [len(heads), len(templates), len(prose_frames), len(event_cards), len(fragments), len(voice_slots), len(particles), len(respun_sigla)]
        == [20, 5, 3, 58, 173, 121, 61, 35],
        [len(heads), len(templates), len(prose_frames), len(event_cards), len(fragments), len(voice_slots), len(particles), len(respun_sigla)],
        [20, 5, 3, 58, 173, 121, 61, 35],
    )
    expected_hashes = {key: sha256(path) for key, path in INPUTS.items()}
    check("input_hashes", result.get("input_sha256") == expected_hashes, result.get("input_sha256"), expected_hashes)

    check(
        "event_id_order_and_uniqueness",
        [row["event_id"] for row in events] == [row["event_id"] for row in source_events],
        len(event_by_id),
        5122,
    )
    check(
        "statement_id_order_and_uniqueness",
        [row["statement_id"] for row in statements] == [row["statement_id"] for row in source_statements],
        len(statement_by_id),
        793,
    )
    check(
        "page_order_and_uniqueness",
        [row["physical_page"] for row in pages] == [row["physical_page"] for row in source_pages],
        len(page_by_id),
        30,
    )

    event_metadata_columns = [
        "edition_event_ordinal", "event_id", "statement_id", "card_ordinal_in_statement",
        "physical_page", "register", "owner_id", "surface", "final_context_recipe",
        "state_status", "state_marker_sequence",
    ]
    event_metadata_exact = all(
        all(row[column] == source_event_by_id[row["event_id"]][column] for column in event_metadata_columns)
        for row in events
    )
    check("event_metadata_exact", event_metadata_exact, "all" if event_metadata_exact else "mismatch", "all")
    event_inverse_count = sum(
        row["gdt576_learned_sigla_clause_de"] == source_event_by_id[row["event_id"]]["learned_sigla_working_clause_de"]
        and row["gdt576_source_roundtrip_de"] == source_event_by_id[row["event_id"]]["learned_sigla_working_clause_de"]
        for row in events
    )
    check("event_byte_exact_inverse", event_inverse_count == 5122, event_inverse_count, 5122)

    changed_event_ids = {
        row["event_id"] for row in events
        if row["attachment_voice_status"] == "CHANGED_EVENT_KEYED_CARD"
    }
    check("ready_source_counts", [len(ready_groups), len(ready_slots), len(ready_event_ids)] == [60, 121, 58], [len(ready_groups), len(ready_slots), len(ready_event_ids)], [60, 121, 58])
    check("changed_event_set", changed_event_ids == ready_event_ids == set(card_by_event), len(changed_event_ids), 58)
    check(
        "changed_targets_really_change",
        all(event_by_id[event_id]["attachment_voice_working_clause_de"] != source_event_by_id[event_id]["learned_sigla_working_clause_de"] for event_id in changed_event_ids),
        "all",
        "all",
    )
    unchanged_exact = all(
        row["attachment_voice_working_clause_de"] == source_event_by_id[row["event_id"]]["learned_sigla_working_clause_de"]
        for row in events if row["event_id"] not in changed_event_ids
    )
    check("unchanged_event_targets_exact", unchanged_exact, "all" if unchanged_exact else "mismatch", "all")
    changed_state = Counter(event_by_id[event_id]["state_status"] for event_id in changed_event_ids)
    check("changed_state_split", changed_state == Counter({"NONSTATE_CARD": 44, "STATE_CARD": 14}), dict(changed_state), {"NONSTATE_CARD": 44, "STATE_CARD": 14})

    inverse_keys = [row["inverse_key"] for row in event_cards]
    check("inverse_keys_are_event_ids", inverse_keys == [row["event_id"] for row in event_cards], len(set(inverse_keys)), 58)
    source_text_groups: dict[str, set[str]] = defaultdict(set)
    target_text_groups: dict[str, set[str]] = defaultdict(set)
    for row in event_cards:
        source_text_groups[row["gdt576_source_clause_de"]].add(row["event_id"])
        target_text_groups[row["target_clause_de"]].add(row["event_id"])
    duplicate_source_sets = {frozenset(ids) for ids in source_text_groups.values() if len(ids) > 1}
    duplicate_target_sets = {frozenset(ids) for ids in target_text_groups.values() if len(ids) > 1}
    expected_text_collision = {frozenset(TEXT_COLLISION_EVENTS)}
    check("known_source_text_collision_retained", duplicate_source_sets == expected_text_collision, [sorted(ids) for ids in duplicate_source_sets], [sorted(TEXT_COLLISION_EVENTS)])
    check("known_target_text_collision_retained", duplicate_target_sets == expected_text_collision, [sorted(ids) for ids in duplicate_target_sets], [sorted(TEXT_COLLISION_EVENTS)])
    check(
        "text_collision_isolated_by_distinct_event_keys",
        {card_by_event[event_id]["inverse_key"] for event_id in TEXT_COLLISION_EVENTS} == TEXT_COLLISION_EVENTS,
        sorted(card_by_event[event_id]["inverse_key"] for event_id in TEXT_COLLISION_EVENTS),
        sorted(TEXT_COLLISION_EVENTS),
    )

    card_integrity = True
    for event_id, card in card_by_event.items():
        source = source_event_by_id[event_id]
        output = event_by_id[event_id]
        action_block = source["learned_sigla_working_clause_de"].removesuffix(".").split("; ", 1)[0]
        card_integrity &= card["gdt576_source_clause_de"] == source["learned_sigla_working_clause_de"]
        card_integrity &= card["target_clause_de"] == output["attachment_voice_working_clause_de"]
        card_integrity &= card["gdt576_source_clause_sha256"] == text_sha256(card["gdt576_source_clause_de"])
        card_integrity &= card["target_clause_sha256"] == text_sha256(card["target_clause_de"])
        card_integrity &= card["retained_action_block_de"] == action_block
        card_integrity &= card["repeat_group_ids"] == source_profile_by_id[event_id]["duplicate_group_ids"]
        card_integrity &= int(card["repeat_group_count"]) == len(card["repeat_group_ids"].split("|"))
        card_integrity &= int(card["repeat_slot_count"]) == len(ready_slots_by_event[event_id])
    check("event_card_source_target_hashes", card_integrity, "all" if card_integrity else "mismatch", "all")

    expected_fragment_keys = {
        (event_id, position)
        for event_id in ready_event_ids
        for position, atom in enumerate(source_event_by_id[event_id]["final_context_recipe"].split("+"))
        if atom not in ACTIONS | ARGUMENTS | STATE_CONTROLS
    }
    check("fragment_position_set", set(fragment_by_key) == expected_fragment_keys, len(fragment_by_key), 173)
    fragment_atom_exact = all(
        row["atom"] == source_event_by_id[row["event_id"]]["final_context_recipe"].split("+")[int(row["atom_position_zero_based"])]
        for row in fragments
    )
    check("fragment_atoms_exact", fragment_atom_exact, "all" if fragment_atom_exact else "mismatch", "all")

    fragment_spans_exact = True
    fragment_orders_exact = True
    rebuilt_events_exact = True
    card_counts_exact = True
    for event_id in ready_event_ids:
        target = event_by_id[event_id]["attachment_voice_working_clause_de"]
        rows = sorted(fragments_by_event[event_id], key=lambda row: int(row["fragment_ordinal_in_event"]))
        positions = [int(row["atom_position_zero_based"]) for row in rows]
        starts = [int(row["target_fragment_start"]) for row in rows]
        fragment_orders_exact &= positions == sorted(positions)
        fragment_orders_exact &= [int(row["fragment_ordinal_in_event"]) for row in rows] == list(range(1, len(rows) + 1))
        fragment_orders_exact &= starts == sorted(starts)
        for row in rows:
            start, end = int(row["target_fragment_start"]), int(row["target_fragment_end"])
            root_start, root_end = int(row["root_expression_start"]), int(row["root_expression_end"])
            fragment_spans_exact &= target[start:end] == row["rendered_fragment_de"]
            fragment_spans_exact &= target[root_start:root_end] == row["base_fragment_de"]
            fragment_spans_exact &= start <= root_start < root_end <= end
            fragment_spans_exact &= row["rendered_fragment_de"].count(row["base_fragment_de"]) == 1
        card = card_by_event[event_id]
        segments = [card["retained_action_block_de"], *(row["rendered_fragment_de"] for row in rows)]
        if "DY" in source_event_by_id[event_id]["final_context_recipe"].split("+"):
            segments.append("schließe den Schritt")
        rebuilt_events_exact &= "; ".join(segments) + "." == target == card["target_clause_de"]
        bound_count = sum(row["binding_status"] == "GDT577_HEAD_BOUND_REPEAT_SLOT" for row in rows)
        unbound_count = sum(row["binding_status"] == "UNBOUND_MODIFIER_IN_RAW_ORDER" for row in rows)
        particle_count = sum(row["repeat_particle_de"] != "NONE" for row in rows)
        card_counts_exact &= int(card["modifier_fragment_count"]) == len(rows)
        card_counts_exact &= int(card["bound_fragment_count"]) == bound_count
        card_counts_exact &= int(card["unbound_fragment_count"]) == unbound_count
        card_counts_exact &= int(card["repeat_particle_count"]) == particle_count
    check("fragment_order_exact", fragment_orders_exact, "all" if fragment_orders_exact else "mismatch", "all")
    check("fragment_and_root_spans_exact", fragment_spans_exact, "all" if fragment_spans_exact else "mismatch", "all")
    check("event_targets_rebuilt_from_fragments", rebuilt_events_exact, "all" if rebuilt_events_exact else "mismatch", "all")
    check("event_card_fragment_counts", card_counts_exact, "all" if card_counts_exact else "mismatch", "all")

    expected_ready_slot_ordinals = set(ready_slot_by_ordinal)
    check("voice_slot_source_set", set(voice_slot_by_ordinal) == expected_ready_slot_ordinals, len(voice_slot_by_ordinal), 121)
    rendered_group_ids = {row["gdt575_duplicate_group_id"] for row in voice_slots}
    check("rendered_group_set", rendered_group_ids == ready_group_ids, len(rendered_group_ids), 60)
    bound_fragment_keys = {
        (row["event_id"], int(row["atom_position_zero_based"]))
        for row in fragments if row["binding_status"] == "GDT577_HEAD_BOUND_REPEAT_SLOT"
    }
    expected_bound_keys = {
        (row["event_id"], int(row["slot_atom_position_zero_based"])) for row in ready_slots
    }
    check("bound_fragment_slot_set", bound_fragment_keys == expected_bound_keys, len(bound_fragment_keys), 121)
    check("unbound_fragment_count", len(fragments) - len(bound_fragment_keys) == 52, len(fragments) - len(bound_fragment_keys), 52)

    slot_fields_exact = True
    slot_spans_exact = True
    slot_head_cards_exact = True
    source_action_cell_by_key = {
        (row["register"], row["action_root"]): row for row in source_action_cells
    }
    head_by_card_id = {row["gdt568_action_voice_card_id"]: row for row in heads}
    for ordinal, row in voice_slot_by_ordinal.items():
        source = ready_slot_by_ordinal[ordinal]
        group = ready_group_by_id[source["gdt575_duplicate_group_id"]]
        fragment = fragment_by_key[(source["event_id"], int(source["slot_atom_position_zero_based"]))]
        for column in [
            "gdt575_duplicate_group_id", "event_id", "statement_id", "physical_page",
            "register", "surface", "final_context_recipe", "repeat_root",
            "slot_occurrence_in_group", "slot_atom_position_zero_based", "head_identity", "placement",
        ]:
            slot_fields_exact &= row[column] == source[column]
        slot_fields_exact &= row["attachment_topology"] == group["attachment_topology"]
        slot_fields_exact &= row["rendered_fragment_de"] == fragment["rendered_fragment_de"]
        slot_fields_exact &= row["root_expression_de"] == fragment["base_fragment_de"]
        target = event_by_id[row["event_id"]]["attachment_voice_working_clause_de"]
        root_start, root_end = int(row["root_expression_start"]), int(row["root_expression_end"])
        slot_spans_exact &= target[root_start:root_end] == row["root_expression_de"]
        if source["head_kind"] == "SEQUENCE":
            slot_head_cards_exact &= row["head_nominal_de"] == "Fortsetzen"
        else:
            cell = source_action_cell_by_key[(row["register"], source["head_root"])]
            base_nominal = head_by_card_id[cell["action_voice_card_id"]]["head_nominal_de"]
            slot_head_cards_exact &= row["head_nominal_de"] == base_nominal or row["head_nominal_de"].endswith(" " + base_nominal)
    check("voice_slot_fields_exact", slot_fields_exact, "all" if slot_fields_exact else "mismatch", "all")
    check("voice_slot_root_spans_exact", slot_spans_exact, "all" if slot_spans_exact else "mismatch", "all")
    check("voice_slot_heads_use_twenty_card_deck", slot_head_cards_exact, "all" if slot_head_cards_exact else "mismatch", "all")

    expected_particle_by_ordinal = {
        row["slot_ordinal"]: expected_particle(
            row,
            ready_group_by_id[row["gdt575_duplicate_group_id"]],
            ready_slots_by_group[row["gdt575_duplicate_group_id"]],
        )
        for row in ready_slots
    }
    particle_assignments_exact = all(
        voice_slot_by_ordinal[ordinal]["repeat_particle_de"] == particle
        for ordinal, particle in expected_particle_by_ordinal.items()
    )
    observed_particle_counts = Counter(
        particle for particle in expected_particle_by_ordinal.values() if particle != "NONE"
    )
    check("particle_rule_recomputed", particle_assignments_exact, "all" if particle_assignments_exact else "mismatch", "all")
    check("particle_counts_recomputed", observed_particle_counts == EXPECTED_PARTICLES, dict(observed_particle_counts), dict(EXPECTED_PARTICLES))

    particle_rows_exact = True
    expected_particle_keys: set[tuple[str, str, str]] = set()
    for ordinal, particle in expected_particle_by_ordinal.items():
        if particle == "NONE":
            continue
        source = ready_slot_by_ordinal[ordinal]
        key = (source["event_id"], source["gdt575_duplicate_group_id"], source["slot_occurrence_in_group"])
        expected_particle_keys.add(key)
        output = particles_by_key.get(key)
        if output is None:
            particle_rows_exact = False
            continue
        target = event_by_id[source["event_id"]]["attachment_voice_working_clause_de"]
        start, end = int(output["particle_start"]), int(output["particle_end"])
        root_start, root_end = int(output["root_expression_start"]), int(output["root_expression_end"])
        particle_rows_exact &= output["particle_de"] == particle
        particle_rows_exact &= target[start:end] == particle
        particle_rows_exact &= end <= root_start or root_end <= start
    check("particle_row_set_and_spans", set(particles_by_key) == expected_particle_keys and particle_rows_exact, len(particles_by_key), 61)

    template_by_topology = {row["attachment_topology"]: row for row in templates}
    ready_topology_counts = Counter(row["attachment_topology"] for row in ready_groups)
    check("ready_group_topology_counts", ready_topology_counts == EXPECTED_READY_GROUP_TOPOLOGIES, dict(ready_topology_counts), dict(EXPECTED_READY_GROUP_TOPOLOGIES))
    check("template_topology_set", set(template_by_topology) == set(EXPECTED_READY_GROUP_TOPOLOGIES), sorted(template_by_topology), sorted(EXPECTED_READY_GROUP_TOPOLOGIES))
    template_counts_exact = True
    for topology, row in template_by_topology.items():
        members = [group for group in ready_groups if group["attachment_topology"] == topology]
        member_ids = {group["gdt575_duplicate_group_id"] for group in members}
        template_counts_exact &= int(row["group_count"]) == len(members)
        template_counts_exact &= int(row["event_count"]) == len({group["event_id"] for group in members})
        template_counts_exact &= int(row["repeat_slot_count"]) == sum(len(ready_slots_by_group[group_id]) for group_id in member_ids)
    check("template_counts_from_source", template_counts_exact, "all" if template_counts_exact else "mismatch", "all")
    prose_frame_by_id = {row["prose_frame_id"]: row for row in prose_frames}
    prose_frames_exact = (
        set(prose_frame_by_id) == set(EXPECTED_PROSE_FRAMES)
        and all(prose_frame_by_id[frame_id]["prose_frame_de"] == voice for frame_id, voice in EXPECTED_PROSE_FRAMES.items())
        and all(template_by_topology[topology]["prose_frame_ids"] == frame_ids for topology, frame_ids in EXPECTED_CLASS_FRAMES.items())
    )
    check("five_classes_map_to_three_prose_frames", prose_frames_exact, {topology: template_by_topology[topology]["prose_frame_ids"] for topology in template_by_topology}, EXPECTED_CLASS_FRAMES)
    chronology_leaks = [
        (row["event_id"], row["atom_position_zero_based"], row["rendered_fragment_de"])
        for row in fragments
        if row["binding_status"] == "GDT577_HEAD_BOUND_REPEAT_SLOT"
        and (" vor dem " in row["rendered_fragment_de"] or " nach dem " in row["rendered_fragment_de"])
    ]
    check("pre_post_geometry_not_voiced_as_chronology", not chronology_leaks, chronology_leaks, [])

    action_cells_by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in source_action_cells:
        action_cells_by_card[row["action_voice_card_id"]].append(row)
    head_card_fields_exact = set(head_by_card_id) == set(action_cells_by_card)
    for card_id, members in action_cells_by_card.items():
        if card_id not in head_by_card_id:
            continue
        row = head_by_card_id[card_id]
        head_card_fields_exact &= row["action_root"] == members[0]["action_root"]
        head_card_fields_exact &= row["register_scope"] == "|".join(member["register"] for member in members)
        head_card_fields_exact &= row["source_owner_expansions"] == "|".join(member["gdt415_owner_local_expansion_de"] for member in members)
        head_card_fields_exact &= bool(row["head_nominal_de"])
    check("twenty_head_cards_rebuilt_from_45_cells", len(source_action_cells) == 45 and len(action_cells_by_card) == 20 and head_card_fields_exact, [len(source_action_cells), len(action_cells_by_card), len(heads)], [45, 20, 20])

    expected_respun_keys = expected_fragment_keys & set(source_sigla_by_key)
    check("respun_sigla_position_set", set(respun_sigla_by_key) == expected_respun_keys, len(respun_sigla_by_key), 35)
    respun_sigla_exact = True
    for key, row in respun_sigla_by_key.items():
        source = source_sigla_by_key[key]
        fragment = fragment_by_key[key]
        source_clause = source_event_by_id[key[0]]["learned_sigla_working_clause_de"]
        target_clause = event_by_id[key[0]]["attachment_voice_working_clause_de"]
        respun_sigla_exact &= row["gdt576_assignment_ordinal"] == source["assignment_ordinal"]
        respun_sigla_exact &= row["atom"] == source["atom"] == fragment["atom"]
        respun_sigla_exact &= row["sigla_card_id"] == source["sigla_card_id"]
        respun_sigla_exact &= row["old_target_fragment_de"] == source["target_fragment_de"]
        respun_sigla_exact &= source_clause[int(row["old_target_start"]):int(row["old_target_end"])] == row["old_target_fragment_de"]
        respun_sigla_exact &= row["new_target_fragment_de"] == fragment["base_fragment_de"]
        respun_sigla_exact &= target_clause[int(row["new_target_start"]):int(row["new_target_end"])] == row["new_target_fragment_de"]
    check("respun_sigla_old_and_new_spans_exact", respun_sigla_exact, "all" if respun_sigla_exact else "mismatch", "all")
    unchanged_sigla_keys = set(source_sigla_by_key) - expected_respun_keys
    unchanged_sigla_exact = all(
        event_by_id[event_id]["attachment_voice_working_clause_de"] == source_event_by_id[event_id]["learned_sigla_working_clause_de"]
        and event_by_id[event_id]["attachment_voice_working_clause_de"][int(source_sigla_by_key[(event_id, position)]["target_start"]):int(source_sigla_by_key[(event_id, position)]["target_end"])]
        == source_sigla_by_key[(event_id, position)]["target_fragment_de"]
        for event_id, position in unchanged_sigla_keys
    )
    check("unchanged_sigla_count_and_spans", len(unchanged_sigla_keys) == 738 and unchanged_sigla_exact, len(unchanged_sigla_keys), 738)
    repeat_or_sigla_keys = expected_bound_keys | expected_respun_keys
    check("repeat_or_sigla_union", len(repeat_or_sigla_keys) == 140, len(repeat_or_sigla_keys), 140)

    statement_metadata_columns = [
        "edition_statement_ordinal", "statement_id", "physical_page", "register", "owner_id",
        "event_count", "state_card_count", "nonstate_card_count", "statement_mode",
        "event_ids", "surface_sequence", "end_mode",
    ]
    statement_integrity = True
    statement_inverse_count = 0
    for row in statements:
        source = source_statement_by_id[row["statement_id"]]
        statement_integrity &= all(row[column] == source[column] for column in statement_metadata_columns)
        rebuilt = " ".join(event_by_id[event_id]["attachment_voice_working_clause_de"] for event_id in row["event_ids"].split("|"))
        changed_members = [event_id for event_id in row["event_ids"].split("|") if event_id in changed_event_ids]
        statement_integrity &= row["attachment_voice_working_reading_de"] == rebuilt
        statement_integrity &= row["attachment_statement_changed"] == ("YES" if changed_members else "NO")
        statement_integrity &= int(row["changed_event_count"]) == len(changed_members)
        statement_integrity &= row["changed_event_ids"] == ("|".join(changed_members) or "NONE")
        if (
            row["gdt576_learned_sigla_reading_de"] == source["learned_sigla_working_reading_de"]
            and row["gdt576_source_roundtrip_de"] == source["learned_sigla_working_reading_de"]
        ):
            statement_inverse_count += 1
    check("statements_rebuilt_from_event_ids", statement_integrity, "all" if statement_integrity else "mismatch", "all")
    check("statement_byte_exact_inverse", statement_inverse_count == 793, statement_inverse_count, 793)
    changed_statement_ids = {row["statement_id"] for row in statements if row["attachment_statement_changed"] == "YES"}
    check("changed_statement_count", len(changed_statement_ids) == 48, len(changed_statement_ids), 48)

    page_integrity = True
    changed_page_ids: set[str] = set()
    events_by_page: dict[str, list[dict[str, str]]] = defaultdict(list)
    statements_by_page: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        events_by_page[row["physical_page"]].append(row)
    for row in statements:
        statements_by_page[row["physical_page"]].append(row)
    for row in pages:
        source = source_page_by_id[row["physical_page"]]
        for column in [
            "page_ordinal", "physical_page", "registers", "event_count", "statement_count",
            "state_event_count", "nonstate_event_count", "page_status",
        ]:
            page_integrity &= row[column] == source[column]
        expected_changed_events = sum(event["event_id"] in changed_event_ids for event in events_by_page[row["physical_page"]])
        expected_changed_statements = sum(statement["statement_id"] in changed_statement_ids for statement in statements_by_page[row["physical_page"]])
        page_integrity &= int(row["changed_event_count"]) == expected_changed_events
        page_integrity &= int(row["changed_statement_count"]) == expected_changed_statements
        page_integrity &= row["page_voice_changed"] == ("YES" if expected_changed_events else "NO")
        if expected_changed_events:
            changed_page_ids.add(row["physical_page"])
    check("page_profiles_recomputed", page_integrity, "all" if page_integrity else "mismatch", "all")
    check("changed_page_count", len(changed_page_ids) == 24, len(changed_page_ids), 24)
    check("sealed_pages_absent", not any(row["physical_page"].startswith("f84") for row in pages), "none", "none")

    conflict_event = event_by_id[CONFLICT_EVENT]
    conflict_statement = statement_by_id[CONFLICT_STATEMENT]
    conflict_page = page_by_id[CONFLICT_PAGE]
    check(
        "conflict_event_exact_and_quarantined",
        conflict_event["attachment_voice_working_clause_de"] == source_event_by_id[CONFLICT_EVENT]["learned_sigla_working_clause_de"]
        and conflict_event["attachment_voice_status"] == "QUARANTINED_RENDERER_HISTORY_CONFLICT"
        and CONFLICT_EVENT not in card_by_event,
        conflict_event["attachment_voice_status"],
        "QUARANTINED_RENDERER_HISTORY_CONFLICT",
    )
    check(
        "conflict_statement_exact",
        conflict_statement["attachment_voice_working_reading_de"] == source_statement_by_id[CONFLICT_STATEMENT]["learned_sigla_working_reading_de"]
        and conflict_statement["attachment_statement_changed"] == "NO",
        conflict_statement["attachment_statement_changed"],
        "NO",
    )
    check(
        "conflict_page_exact",
        conflict_page["page_voice_changed"] == "NO"
        and int(conflict_page["changed_event_count"]) == 0
        and int(conflict_page["changed_statement_count"]) == 0,
        [conflict_page["page_voice_changed"], conflict_page["changed_event_count"], conflict_page["changed_statement_count"]],
        ["NO", "0", "0"],
    )

    scope_event_ids = {row["event_id"] for row in source_scope_pairs}
    scope_events_exact = all(
        event_by_id[event_id]["attachment_voice_working_clause_de"] == source_event_by_id[event_id]["learned_sigla_working_clause_de"]
        and event_id not in card_by_event
        for event_id in scope_event_ids
    )
    check("seventeen_scope_pair_events_unchanged", len(source_scope_pairs) == len(scope_event_ids) == 17 and scope_events_exact, len(scope_event_ids), 17)
    adjacent_event_ids = {
        row["event_id"] for row in source_duplicate_groups
        if row["duplicate_topology"] == "SAME_ROOT_RAW_ADJACENT"
    }
    adjacent_events_exact = all(
        event_by_id[event_id]["attachment_voice_working_clause_de"] == source_event_by_id[event_id]["learned_sigla_working_clause_de"]
        and event_id not in card_by_event
        for event_id in adjacent_event_ids
    )
    check("three_raw_adjacent_repeat_events_unchanged", len(adjacent_event_ids) == 3 and adjacent_events_exact, len(adjacent_event_ids), 3)

    card_counts = Counter(row["event_id"] for row in event_cards)
    overlap_once = all(card_counts[event_id] == 1 for event_id in OVERLAPPING_RENDER_EVENTS)
    overlap_two_groups = all(int(card_by_event[event_id]["repeat_group_count"]) == 2 for event_id in OVERLAPPING_RENDER_EVENTS)
    check("overlapping_events_rendered_once", overlap_once and overlap_two_groups, {event_id: card_counts[event_id] for event_id in sorted(OVERLAPPING_RENDER_EVENTS)}, {event_id: 1 for event_id in sorted(OVERLAPPING_RENDER_EVENTS)})

    cumulative_event_changes = sum(
        row["attachment_voice_working_clause_de"] != source_event_by_id[row["event_id"]]["gdt574_action_count_clause_de"]
        for row in events
    )
    cumulative_statement_changes = sum(
        row["attachment_voice_working_reading_de"] != source_statement_by_id[row["statement_id"]]["gdt574_action_count_reading_de"]
        for row in statements
    )
    cumulative_page_changes = len({
        row["physical_page"] for row in events
        if row["attachment_voice_working_clause_de"] != source_event_by_id[row["event_id"]]["gdt574_action_count_clause_de"]
    })
    check("cumulative_gdt574_changes", [cumulative_event_changes, cumulative_statement_changes, cumulative_page_changes] == [750, 305, 28], [cumulative_event_changes, cumulative_statement_changes, cumulative_page_changes], [750, 305, 28])

    expected_result_values = {
        "event_count": 5122,
        "statement_count": 793,
        "page_count": 30,
        "changed_event_count": 58,
        "unchanged_event_count": 5064,
        "changed_nonstate_event_count": 44,
        "changed_state_event_count": 14,
        "changed_statement_count": 48,
        "changed_page_count": 24,
        "event_card_count": 58,
        "rendered_group_count": 60,
        "rendered_repeat_slot_count": 121,
        "ordered_modifier_fragment_count": 173,
        "bound_modifier_fragment_count": 121,
        "unbound_modifier_fragment_count": 52,
        "repeat_particle_count": 61,
        "respun_sigla_span_count": 35,
        "unchanged_sigla_span_count": 738,
        "repeat_or_sigla_unique_atom_position_count": 140,
        "cumulative_changed_event_count_against_gdt574": 750,
        "cumulative_changed_statement_count_against_gdt574": 305,
        "cumulative_changed_page_count_against_gdt574": 28,
        "attachment_class_count": 5,
        "prose_frame_count": 3,
    }
    result_values_exact = all(result.get(key) == value for key, value in expected_result_values.items())
    check("result_summary_recomputed", result_values_exact, {key: result.get(key) for key in expected_result_values}, expected_result_values)
    check("result_particle_counts", result.get("repeat_particle_counts") == dict(sorted(EXPECTED_PARTICLES.items())), result.get("repeat_particle_counts"), dict(sorted(EXPECTED_PARTICLES.items())))
    check(
        "result_boolean_guards",
        all(result.get(key) is True for key in [
            "scope_pair_events_unchanged", "raw_adjacent_repeat_events_unchanged",
            "conflict_event_unchanged", "conflict_statement_unchanged", "conflict_page_unchanged",
            "no_new_page", "no_root_change", "no_recipe_change",
        ]),
        "all",
        "all",
    )

    guard_checks = {
        "heads": all(row["guard"] == "NOMINAL_HEAD_VOICE_ONLY__ACTION_ROOT_UNCHANGED" for row in heads),
        "templates": all(row["guard"] == "ATTACHMENT_CLASS_TO_PROSE_FRAME_ONLY__PRE_POST_RETAINED_IN_SLOT_TABLE" for row in templates),
        "prose_frames": all(row["guard"] == "HEAD_BINDING_VOICE_ONLY__NO_PROCESS_CHRONOLOGY_FROM_PRE_POST" for row in prose_frames),
        "fragments": all(row["guard"] == "RAW_ATOM_ORDER__ROOT_EXPRESSION_SPAN_EXCLUDES_REPEAT_PARTICLE" for row in fragments),
        "voice_slots": all(row["guard"] == "ONE_ROOT_EXPRESSION_PER_WRITTEN_REPEAT_SLOT__PARTICLE_SEPARATE" for row in voice_slots),
        "particles": all(row["guard"] == "EDITORIAL_REPEAT_PARTICLE__NOT_PART_OF_ROOT_EXPRESSION" for row in particles),
        "respun_sigla": all(row["guard"] == "SIGLA_ATOM_POSITION_RETAINED__NEW_EVENT_SPAN_RECOMPUTED" for row in respun_sigla),
        "event_cards": all(row["guard"] == "EXPLICIT_EVENT_CARD__NEVER_LOOK_UP_BY_SOURCE_TEXT" for row in event_cards),
        "events": all(row["guard"] == "EVENT_ID_KEYED_EDITION__GDT576_SOURCE_ROUNDTRIP_EXACT" for row in events),
        "statements": all(row["guard"] == "STATEMENT_REBUILT_ONLY_FROM_FIXED_EVENT_IDS__SOURCE_ROUNDTRIP_EXACT" for row in statements),
        "pages": all(row["guard"] == "SOURCE_PAGE_ORDER_AND_MEMBERSHIP_UNCHANGED" for row in pages),
    }
    check("artifact_guards", all(guard_checks.values()), guard_checks, {key: True for key in guard_checks})

    failures = [row for row in checks if row["status"] != "PASS"]
    validation = {
        "experiment_id": "GDT578",
        "status": "PASS" if not failures else "FAIL",
        "check_count": len(checks),
        "pass_count": len(checks) - len(failures),
        "fail_count": len(failures),
        "checks": checks,
    }
    (OUT / "gdt578_validation.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
