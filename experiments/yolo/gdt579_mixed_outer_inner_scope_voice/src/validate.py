#!/usr/bin/env python3
"""Independent reconstruction checks for the GDT579 mixed-scope edition."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt579_mixed_outer_inner_scope_voice"
OUT = BASE / "artifacts"
G574 = ROOT / "experiments/yolo/gdt574_adjacent_action_count_voice/artifacts"
G575 = ROOT / "experiments/yolo/gdt575_repeated_relation_modifier_scope_atlas/artifacts"
G578 = ROOT / "experiments/yolo/gdt578_event_keyed_interrupted_modifier_voice/artifacts"

INPUTS = {
    "events": G578 / "gdt578_5122_attachment_voice_event_edition.tsv",
    "statements": G578 / "gdt578_793_attachment_voice_statement_edition.tsv",
    "pages": G578 / "gdt578_30_page_attachment_voice_profiles.tsv",
    "scope_pairs": G575 / "gdt575_17_outer_inner_scope_pairs.tsv",
    "old_attachments": ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts/gdt407_5051_attachment_edition.tsv",
    "new_attachments": ROOT / "experiments/yolo/gdt515_second_random_four_page_full_admission/artifacts/gdt515_factorized_attachments.tsv",
    "action_cells": ROOT / "experiments/yolo/gdt568_twenty_owner_action_voice_frames/artifacts/gdt568_45_register_action_cells.tsv",
    "gdt574_events": G574 / "gdt574_5122_action_count_event_edition.tsv",
    "gdt574_statements": G574 / "gdt574_793_action_count_statement_edition.tsv",
}
OUTPUTS = {
    "routes": OUT / "gdt579_2_scope_voice_routes.tsv",
    "profiles": OUT / "gdt579_17_scope_pair_profiles.tsv",
    "slots": OUT / "gdt579_34_scope_slot_assignments.tsv",
    "intervening": OUT / "gdt579_15_intervening_atoms.tsv",
    "fragments": OUT / "gdt579_27_interrupted_modifier_fragments.tsv",
    "factorizations": OUT / "gdt579_7_adjacent_factorizations.tsv",
    "cards": OUT / "gdt579_17_event_cards.tsv",
    "overlaps": OUT / "gdt579_3_overlap_statements.tsv",
    "events": OUT / "gdt579_5122_mixed_scope_event_edition.tsv",
    "statements": OUT / "gdt579_793_mixed_scope_statement_edition.tsv",
    "pages": OUT / "gdt579_30_page_mixed_scope_profiles.tsv",
}

STATUS = (
    "PASS_17_SCOPE_PAIRS__7_ADJACENT_FACTORIZED__10_INTERRUPTED_SLOT_EXPLICIT__"
    "34_SCOPE_SLOTS__15_INTERVENING_ATOMS__27_ORDERED_MODIFIER_FRAGMENTS__"
    "5122_EXACT_ROUNDTRIPS"
)
ACTIONS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
ARGUMENTS = {"Y", "AIIN", "AIN", "OR"}
STATE_CONTROLS = {"OT", "OL", "DY"}
FIXED_FOCUS_ROOTS = {"E", "AR", "AL", "L"}
REPEAT_OR_COUNT_WORDS = {"zweimal", "ebenfalls", "erneut", "wieder", "nochmals"}
OVERLAP_STATEMENTS = {"G407-S055", "G407-S064", "G407-S650"}
RETAINED_GDT578_EVENTS = {"G407-E1059", "G407-E1182", "G407-E1188", "G407-E3870"}
ACTIVE_CONTEXT_EVENT = "G515-E0385"
ACTIVE_CONTEXT_HEAD_EVENT = "G515-E0383"

ACTION_NOMINAL_BY_CARD = {
    "GDT568-A01": "Eintragen",
    "GDT568-A02": "Ansetzen",
    "GDT568-A03": "Setzen",
    "GDT568-A04": "Ansetzen",
    "GDT568-A05": "Ansetzen",
    "GDT568-A06": "Entnehmen",
    "GDT568-A07": "Nehmen",
    "GDT568-A08": "Aufnehmen",
    "GDT568-A09": "Festhalten",
    "GDT568-A10": "Halten",
    "GDT568-A11": "Zuordnen",
    "GDT568-A12": "Zugeben",
    "GDT568-A13": "Zuführen",
    "GDT568-A14": "Wählen",
    "GDT568-A15": "Bearbeiten",
    "GDT568-A16": "Festlegen",
    "GDT568-A17": "Einstellen",
    "GDT568-A18": "Kennzeichnen",
    "GDT568-A19": "Markieren",
    "GDT568-A20": "Einsetzen",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def unique_index(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    index = {row[key]: row for row in rows}
    if len(index) != len(rows):
        raise RuntimeError(f"Duplicate {key} in validation input")
    return index


def fixed_attachment_map(
    old_rows: list[dict[str, str]], new_rows: list[dict[str, str]]
) -> dict[tuple[str, int], dict[str, str]]:
    result: dict[tuple[str, int], dict[str, str]] = {}
    for row in old_rows:
        result[(row["global_running_event_id"], int(row["focus_atom_ordinal"]) - 1)] = {
            "assignment_source": "GDT407_FIXED_FOCUS_ATTACHMENT",
            "selector_rule": row["selector_rule"],
            "source_geometry": row["attachment_geometry"],
            "head_kind": row["head_kind"],
            "head_event_id": row["selected_action_global_event_id"],
            "head_atom_position_zero_based": str(int(row["selected_action_atom_ordinal"]) - 1),
            "head_root": row["action_core"],
            "duplicate_mode": row["duplicate_mode"],
            "duplicate_role": row["duplicate_role"],
        }
    for row in new_rows:
        result[(row["event_id"], int(row["focus_atom_ordinal"]) - 1)] = {
            "assignment_source": "GDT515_FIXED_FOCUS_ATTACHMENT",
            "selector_rule": row["selector_rule"],
            "source_geometry": row["attachment_geometry"],
            "head_kind": row["head_kind"],
            "head_event_id": row["selected_action_event_id"],
            "head_atom_position_zero_based": str(int(row["selected_action_atom_ordinal"]) - 1),
            "head_root": row["action_core"],
            "duplicate_mode": row["duplicate_mode"],
            "duplicate_role": row["duplicate_role"],
        }
    return result


def active_before(
    events: list[dict[str, str]],
) -> dict[str, tuple[str, int, str] | None]:
    active: dict[tuple[str, str], tuple[str, int, str]] = {}
    result: dict[str, tuple[str, int, str] | None] = {}
    for event in events:
        owner_key = (event["physical_page"], event["owner_id"])
        result[event["event_id"]] = active.get(owner_key)
        for position, atom in enumerate(event["final_context_recipe"].split("+")):
            if atom in ACTIONS:
                active[owner_key] = (event["event_id"], position, atom)
    return result


def nearest_visible_action(event: dict[str, str], slot_position: int) -> tuple[int, str]:
    atoms = event["final_context_recipe"].split("+")
    left_boundary = max(
        (position for position, atom in enumerate(atoms) if atom in STATE_CONTROLS and position < slot_position),
        default=-1,
    )
    right_boundary = min(
        (position for position, atom in enumerate(atoms) if atom in STATE_CONTROLS and position > slot_position),
        default=len(atoms),
    )
    candidates = [
        position for position, atom in enumerate(atoms)
        if atom in ACTIONS and left_boundary < position < right_boundary
    ]
    if not candidates:
        raise RuntimeError(f"No visible action at {event['event_id']}:{slot_position}")
    selected = min(
        candidates,
        key=lambda position: (abs(position - slot_position), 0 if position < slot_position else 1, position),
    )
    return selected, atoms[selected]


def expected_placement(
    event_id: str, slot_position: int, assignment: dict[str, str]
) -> str:
    if assignment["head_kind"] == "VISIBLE_OWNER" or assignment["head_event_id"] != event_id:
        return "CONTEXT_HEAD"
    head_position = int(assignment["head_atom_position_zero_based"])
    if head_position < slot_position:
        return "POST_HEAD"
    if head_position > slot_position:
        return "PRE_HEAD"
    raise RuntimeError(f"Scope slot coincides with its head at {event_id}:{slot_position}")


def expected_head_nominal(
    assignment: dict[str, str],
    register: str,
    action_cells: dict[tuple[str, str], dict[str, str]],
    events: dict[str, dict[str, str]],
) -> str:
    if assignment["head_kind"] == "VISIBLE_OWNER" or assignment["head_root"] == "OWNER":
        return "sichtbaren Owner"
    cell = action_cells[(register, assignment["head_root"])]
    nominal = ACTION_NOMINAL_BY_CARD[cell["action_voice_card_id"]]
    head_event = events[assignment["head_event_id"]]
    positions = [
        position
        for position, atom in enumerate(head_event["final_context_recipe"].split("+"))
        if atom == assignment["head_root"]
    ]
    head_position = int(assignment["head_atom_position_zero_based"])
    if len(positions) > 1 and head_position in positions:
        ordinal = positions.index(head_position) + 1
        ordinal_word = {1: "ersten", 2: "zweiten", 3: "dritten", 4: "vierten"}.get(
            ordinal, f"{ordinal}."
        )
        nominal = f"{ordinal_word} {nominal}"
    return nominal


def classify_topology(assignments: list[dict[str, str]]) -> str:
    heads = {
        (row["head_kind"], row["head_event_id"], row["head_atom_position_zero_based"])
        for row in assignments
    }
    placements = {row["placement"] for row in assignments}
    if len(heads) > 1:
        return "DISTINCT_ACTION_OCCURRENCES"
    if {"PRE_HEAD", "POST_HEAD"}.issubset(placements):
        return "BRACKETING_SAME_HEAD"
    if "CONTEXT_HEAD" in placements:
        return "ACTIVE_CONTEXT_HEAD"
    return "SAME_HEAD_SAME_SIDE"


def main() -> int:
    source_events = read_tsv(INPUTS["events"])
    source_statements = read_tsv(INPUTS["statements"])
    source_pages = read_tsv(INPUTS["pages"])
    source_pairs = read_tsv(INPUTS["scope_pairs"])
    old_attachments = read_tsv(INPUTS["old_attachments"])
    new_attachments = read_tsv(INPUTS["new_attachments"])
    action_cell_rows = read_tsv(INPUTS["action_cells"])
    gdt574_events = read_tsv(INPUTS["gdt574_events"])
    gdt574_statements = read_tsv(INPUTS["gdt574_statements"])

    routes = read_tsv(OUTPUTS["routes"])
    profiles = read_tsv(OUTPUTS["profiles"])
    slots = read_tsv(OUTPUTS["slots"])
    intervening = read_tsv(OUTPUTS["intervening"])
    fragments = read_tsv(OUTPUTS["fragments"])
    factorizations = read_tsv(OUTPUTS["factorizations"])
    cards = read_tsv(OUTPUTS["cards"])
    overlaps = read_tsv(OUTPUTS["overlaps"])
    events = read_tsv(OUTPUTS["events"])
    statements = read_tsv(OUTPUTS["statements"])
    pages = read_tsv(OUTPUTS["pages"])
    result = json.loads((OUT / "gdt579_result.json").read_text(encoding="utf-8"))

    source_event_by_id = unique_index(source_events, "event_id")
    source_statement_by_id = unique_index(source_statements, "statement_id")
    source_page_by_id = unique_index(source_pages, "physical_page")
    pair_by_event = unique_index(source_pairs, "event_id")
    profile_by_event = unique_index(profiles, "event_id")
    card_by_event = unique_index(cards, "event_id")
    event_by_id = unique_index(events, "event_id")
    statement_by_id = unique_index(statements, "statement_id")
    page_by_id = unique_index(pages, "physical_page")
    old_event_by_id = unique_index(gdt574_events, "event_id")
    old_statement_by_id = unique_index(gdt574_statements, "statement_id")
    fixed = fixed_attachment_map(old_attachments, new_attachments)
    active = active_before(source_events)
    action_cells = {(row["register"], row["action_root"]): row for row in action_cell_rows}
    if len(action_cells) != 45:
        raise RuntimeError("GDT568 action-cell key drift")

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
        [len(source_events), len(source_statements), len(source_pages), len(source_pairs)] == [5122, 793, 30, 17],
        [len(source_events), len(source_statements), len(source_pages), len(source_pairs)],
        [5122, 793, 30, 17],
    )
    check(
        "output_counts",
        [len(events), len(statements), len(pages), len(routes), len(profiles), len(slots), len(intervening), len(fragments), len(factorizations), len(cards), len(overlaps)]
        == [5122, 793, 30, 2, 17, 34, 15, 27, 7, 17, 3],
        [len(events), len(statements), len(pages), len(routes), len(profiles), len(slots), len(intervening), len(fragments), len(factorizations), len(cards), len(overlaps)],
        [5122, 793, 30, 2, 17, 34, 15, 27, 7, 17, 3],
    )
    expected_hashes = {key: sha256(path) for key, path in INPUTS.items()}
    check("input_hashes", result.get("input_sha256") == expected_hashes, result.get("input_sha256"), expected_hashes)

    route_by_event: dict[str, str] = {}
    expected_pair_id: dict[str, str] = {}
    expected_positions: dict[str, tuple[int, int]] = {}
    for pair in source_pairs:
        event_id = pair["event_id"]
        outer = int(pair["outer_atom_position_zero_based"])
        inner = int(pair["inner_atom_position_zero_based"])
        atoms = source_event_by_id[event_id]["final_context_recipe"].split("+")
        root = pair["underlying_atom"]
        if not (0 <= outer < inner < len(atoms)) or atoms[outer] != root or atoms[inner] != root:
            raise RuntimeError(f"Invalid GDT575 scope positions for {event_id}")
        route_by_event[event_id] = "ADJACENT_FACTORIZATION" if inner == outer + 1 else "INTERRUPTED_SLOT_EXPLICIT"
        expected_pair_id[event_id] = f"GDT579-P{int(pair['scope_pair_ordinal']):02d}"
        expected_positions[event_id] = (outer, inner)
    route_counts = Counter(route_by_event.values())
    check("route_split_from_atom_positions", route_counts == Counter({"ADJACENT_FACTORIZATION": 7, "INTERRUPTED_SLOT_EXPLICIT": 10}), dict(route_counts), {"ADJACENT_FACTORIZATION": 7, "INTERRUPTED_SLOT_EXPLICIT": 10})

    expected_assignments: dict[tuple[str, str], dict[str, str]] = {}
    for pair in source_pairs:
        event_id = pair["event_id"]
        event = source_event_by_id[event_id]
        root = pair["underlying_atom"]
        for scope, position in (
            ("OUTER", int(pair["outer_atom_position_zero_based"])),
            ("INNER", int(pair["inner_atom_position_zero_based"])),
        ):
            if root in FIXED_FOCUS_ROOTS:
                assignment = dict(fixed[(event_id, position)])
            elif root == "O":
                head_position, head_root = nearest_visible_action(event, position)
                assignment = {
                    "assignment_source": "GDT577_EXPLORATORY_NEAREST_VISIBLE_ACTION",
                    "selector_rule": "VISIBLE_ACTION_INSIDE_OT_OL_DY_INTERVAL",
                    "source_geometry": "SAME_CARRIER_DISTANCE_MINIMUM__LEFT_TIE",
                    "head_kind": "ORDINARY_ACTION_HEAD",
                    "head_event_id": event_id,
                    "head_atom_position_zero_based": str(head_position),
                    "head_root": head_root,
                    "duplicate_mode": "ANALYTICAL_SCOPE_SLOT",
                    "duplicate_role": "CANDIDATE_LOCAL_HEAD",
                }
            elif root == "D_ADDR" and event_id == ACTIVE_CONTEXT_EVENT:
                if active[event_id] != (ACTIVE_CONTEXT_HEAD_EVENT, 3, "R"):
                    raise RuntimeError(f"Active R context drift: {active[event_id]}")
                assignment = {
                    "assignment_source": "EXPLICIT_G515_E0385_ACTIVE_R_CONTEXT_CARD",
                    "selector_rule": "SAME_PAGE_OWNER_ACTIVE_R_HEAD",
                    "source_geometry": "OWNER_ACTIVE_ACTION_CONTEXT",
                    "head_kind": "ORDINARY_ACTION_HEAD",
                    "head_event_id": ACTIVE_CONTEXT_HEAD_EVENT,
                    "head_atom_position_zero_based": "3",
                    "head_root": "R",
                    "duplicate_mode": "ANALYTICAL_SCOPE_SLOT",
                    "duplicate_role": "EXPLICIT_CONTEXT_HEAD",
                }
            else:
                raise RuntimeError(f"No independently licensed assignment for {event_id}:{position}:{root}")
            assignment.update({
                "scope_pair_ordinal": pair["scope_pair_ordinal"],
                "scope_pair_id": expected_pair_id[event_id],
                "event_id": event_id,
                "scope": scope,
                "scope_atom_position_zero_based": str(position),
                "scope_root": root,
            })
            assignment["placement"] = expected_placement(event_id, position, assignment)
            assignment["head_identity"] = (
                f"{assignment['head_kind']}:{assignment['head_event_id']}@"
                f"{assignment['head_atom_position_zero_based']}:{assignment['head_root']}"
            )
            assignment["head_nominal_de"] = expected_head_nominal(
                assignment, event["register"], action_cells, source_event_by_id
            )
            expected_assignments[(event_id, scope)] = assignment

    slot_by_key = {(row["event_id"], row["scope"]): row for row in slots}
    check("scope_slot_keys", len(slot_by_key) == len(slots) == 34 and set(slot_by_key) == set(expected_assignments), len(slot_by_key), 34)
    check("outer_inner_slot_counts", Counter(row["scope"] for row in slots) == Counter({"OUTER": 17, "INNER": 17}), dict(Counter(row["scope"] for row in slots)), {"OUTER": 17, "INNER": 17})
    assignment_fields = [
        "assignment_source", "selector_rule", "source_geometry", "head_kind", "head_event_id",
        "head_atom_position_zero_based", "head_root", "duplicate_mode", "duplicate_role",
        "scope_pair_ordinal", "scope_pair_id", "event_id", "scope",
        "scope_atom_position_zero_based", "scope_root", "placement", "head_identity", "head_nominal_de",
    ]
    assignments_exact = all(
        all(slot_by_key[key][field] == expected[field] for field in assignment_fields)
        for key, expected in expected_assignments.items()
    )
    check("scope_assignments_rebuilt", assignments_exact, "all" if assignments_exact else "mismatch", "all")
    assignment_source_counts = Counter(row["assignment_source"] for row in slots)
    expected_source_counts = Counter({
        "GDT407_FIXED_FOCUS_ATTACHMENT": 20,
        "GDT515_FIXED_FOCUS_ATTACHMENT": 8,
        "GDT577_EXPLORATORY_NEAREST_VISIBLE_ACTION": 4,
        "EXPLICIT_G515_E0385_ACTIVE_R_CONTEXT_CARD": 2,
    })
    check("assignment_source_counts", assignment_source_counts == expected_source_counts, dict(assignment_source_counts), dict(expected_source_counts))
    placement_counts = Counter(row["placement"] for row in slots)
    check("placement_counts", placement_counts == Counter({"POST_HEAD": 25, "PRE_HEAD": 3, "CONTEXT_HEAD": 6}), dict(placement_counts), {"POST_HEAD": 25, "PRE_HEAD": 3, "CONTEXT_HEAD": 6})

    owner_slots = [row for row in slots if row["event_id"] == "G407-E4142"]
    owner_sentinel_exact = len(owner_slots) == 2 and all(
        row["head_kind"] == "VISIBLE_OWNER"
        and row["head_event_id"] == "OWNER::G407-S671"
        and row["head_atom_position_zero_based"] == "-1"
        and row["head_root"] == "OWNER"
        and row["placement"] == "CONTEXT_HEAD"
        for row in owner_slots
    )
    check("e4142_visible_owner_sentinel", owner_sentinel_exact, [(row["head_kind"], row["head_event_id"], row["head_atom_position_zero_based"], row["head_root"]) for row in owner_slots], [("VISIBLE_OWNER", "OWNER::G407-S671", "-1", "OWNER")] * 2)
    active_slots = [row for row in slots if row["event_id"] == ACTIVE_CONTEXT_EVENT]
    e0385_atoms = source_event_by_id[ACTIVE_CONTEXT_EVENT]["final_context_recipe"].split("+")
    active_r_exact = (
        e0385_atoms[1] == "AR"
        and active[ACTIVE_CONTEXT_EVENT] == (ACTIVE_CONTEXT_HEAD_EVENT, 3, "R")
        and len(active_slots) == 2
        and all(
            row["head_event_id"] == ACTIVE_CONTEXT_HEAD_EVENT
            and row["head_atom_position_zero_based"] == "3"
            and row["head_root"] == "R"
            and row["placement"] == "CONTEXT_HEAD"
            for row in active_slots
        )
    )
    check("e0385_active_r_not_intervening_ar", active_r_exact, [(row["head_event_id"], row["head_atom_position_zero_based"], row["head_root"]) for row in active_slots], [(ACTIVE_CONTEXT_HEAD_EVENT, "3", "R")] * 2)

    slots_by_event: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in slots:
        slots_by_event[row["event_id"]].append(row)
    topology_by_event = {
        event_id: classify_topology(rows) for event_id, rows in slots_by_event.items()
    }
    topology_exact = all(
        row["attachment_topology"] == topology_by_event[row["event_id"]]
        and row["route"] == route_by_event[row["event_id"]]
        for row in slots
    )
    check("slot_topologies_rebuilt", topology_exact, "all" if topology_exact else "mismatch", "all")

    expected_intervening: dict[tuple[str, int], tuple[str, str]] = {}
    for event_id, route in route_by_event.items():
        if route != "INTERRUPTED_SLOT_EXPLICIT":
            continue
        outer, inner = expected_positions[event_id]
        atoms = source_event_by_id[event_id]["final_context_recipe"].split("+")
        for position in range(outer + 1, inner):
            atom = atoms[position]
            atom_class = (
                "ACTION" if atom in ACTIONS else
                "ARGUMENT" if atom in ARGUMENTS else
                "STATE_CONTROL" if atom in STATE_CONTROLS else
                "MODIFIER_OR_SIGLUM"
            )
            expected_intervening[(event_id, position)] = (atom, atom_class)
    intervening_by_key = {
        (row["event_id"], int(row["atom_position_zero_based"])): row for row in intervening
    }
    intervening_exact = (
        len(intervening_by_key) == len(intervening)
        and set(intervening_by_key) == set(expected_intervening)
        and all(
            intervening_by_key[key]["atom"] == value[0]
            and intervening_by_key[key]["atom_class"] == value[1]
            and intervening_by_key[key]["scope_pair_id"] == expected_pair_id[key[0]]
            for key, value in expected_intervening.items()
        )
    )
    check("intervening_atoms_from_raw_positions", intervening_exact, len(intervening_by_key), 15)
    intervening_classes = Counter(row["atom_class"] for row in intervening)
    check("intervening_class_counts", intervening_classes == Counter({"ACTION": 10, "MODIFIER_OR_SIGLUM": 5}), dict(intervening_classes), {"ACTION": 10, "MODIFIER_OR_SIGLUM": 5})

    profile_integrity = True
    for pair in source_pairs:
        event_id = pair["event_id"]
        profile = profile_by_event[event_id]
        expected_rows = sorted(slots_by_event[event_id], key=lambda row: int(row["scope_atom_position_zero_based"]))
        outer, inner = expected_positions[event_id]
        for source_field, target_field in [
            ("event_id", "event_id"), ("statement_id", "statement_id"),
            ("register", "register"), ("surface", "surface"),
            ("final_context_recipe", "final_context_recipe"), ("underlying_atom", "scope_root"),
            ("outer_atom_position_zero_based", "outer_atom_position_zero_based"),
            ("inner_atom_position_zero_based", "inner_atom_position_zero_based"),
        ]:
            profile_integrity &= profile[target_field] == pair[source_field]
        profile_integrity &= profile["scope_pair_id"] == expected_pair_id[event_id]
        profile_integrity &= profile["route"] == route_by_event[event_id]
        profile_integrity &= int(profile["intervening_atom_count"]) == inner - outer - 1
        profile_integrity &= profile["attachment_topology"] == topology_by_event[event_id]
        profile_integrity &= profile["head_identity_trace"] == " | ".join(row["head_identity"] for row in expected_rows)
        profile_integrity &= profile["placement_trace"] == "+".join(row["placement"] for row in expected_rows)
    check("pair_profiles_rebuilt", profile_integrity, "all" if profile_integrity else "mismatch", "all")

    expected_fragment_keys = {
        (event_id, position)
        for event_id, route in route_by_event.items()
        if route == "INTERRUPTED_SLOT_EXPLICIT"
        for position, atom in enumerate(source_event_by_id[event_id]["final_context_recipe"].split("+"))
        if atom not in ACTIONS | ARGUMENTS | STATE_CONTROLS
    }
    fragment_by_key = {
        (row["event_id"], int(row["atom_position_zero_based"])): row for row in fragments
    }
    check("interrupted_fragment_position_set", len(fragment_by_key) == len(fragments) == 27 and set(fragment_by_key) == expected_fragment_keys, len(fragment_by_key), 27)
    interrupted_scope_keys = {
        (row["event_id"], int(row["scope_atom_position_zero_based"]))
        for row in slots if row["route"] == "INTERRUPTED_SLOT_EXPLICIT"
    }
    fragment_structure_exact = True
    fragments_by_event: dict[str, list[dict[str, str]]] = defaultdict(list)
    for key, row in fragment_by_key.items():
        event_id, position = key
        atoms = source_event_by_id[event_id]["final_context_recipe"].split("+")
        outer, inner = expected_positions[event_id]
        target = event_by_id[event_id]["mixed_scope_voice_working_clause_de"]
        start, end = int(row["target_fragment_start"]), int(row["target_fragment_end"])
        root_start, root_end = int(row["root_expression_start"]), int(row["root_expression_end"])
        is_scope = key in interrupted_scope_keys
        fragment_structure_exact &= row["atom"] == atoms[position]
        fragment_structure_exact &= row["scope_pair_id"] == expected_pair_id[event_id]
        fragment_structure_exact &= row["scope_slot"] == ("YES" if is_scope else "NO")
        fragment_structure_exact &= row["binding_status"] == ("SCOPE_SLOT_HEAD_BOUND" if is_scope else "UNBOUND_MODIFIER_IN_RAW_ORDER")
        fragment_structure_exact &= row["between_pair_positions"] == ("YES" if outer < position < inner else "NO")
        fragment_structure_exact &= target[start:end] == row["rendered_fragment_de"]
        fragment_structure_exact &= target[root_start:root_end] == row["base_fragment_de"]
        fragment_structure_exact &= start <= root_start < root_end <= end
        fragment_structure_exact &= row["rendered_fragment_de"].count(row["base_fragment_de"]) == 1
        fragments_by_event[event_id].append(row)
    check("interrupted_fragment_atoms_bindings_and_spans", fragment_structure_exact, "all" if fragment_structure_exact else "mismatch", "all")
    check("interrupted_fragment_split", Counter(row["scope_slot"] for row in fragments) == Counter({"YES": 20, "NO": 7}), dict(Counter(row["scope_slot"] for row in fragments)), {"YES": 20, "NO": 7})
    check("five_intervening_modifier_fragments", sum(row["between_pair_positions"] == "YES" for row in fragments) == 5, sum(row["between_pair_positions"] == "YES" for row in fragments), 5)

    interrupted_rebuild_exact = True
    raw_fragment_order_exact = True
    for event_id, rows in fragments_by_event.items():
        rows.sort(key=lambda row: int(row["fragment_ordinal_in_event"]))
        positions = [int(row["atom_position_zero_based"]) for row in rows]
        raw_fragment_order_exact &= positions == sorted(positions)
        raw_fragment_order_exact &= [int(row["fragment_ordinal_in_event"]) for row in rows] == list(range(1, len(rows) + 1))
        source_clause = source_event_by_id[event_id]["attachment_voice_working_clause_de"]
        action_block = source_clause.removesuffix(".").split("; ", 1)[0]
        segments = [action_block, *(row["rendered_fragment_de"] for row in rows)]
        if "DY" in source_event_by_id[event_id]["final_context_recipe"].split("+"):
            segments.append("schließe den Schritt")
        interrupted_rebuild_exact &= "; ".join(segments) + "." == event_by_id[event_id]["mixed_scope_voice_working_clause_de"]
    check("interrupted_fragment_raw_order", raw_fragment_order_exact, "all" if raw_fragment_order_exact else "mismatch", "all")
    check("interrupted_events_rebuilt_from_fragments", interrupted_rebuild_exact, "all" if interrupted_rebuild_exact else "mismatch", "all")

    factorization_by_event = unique_index(factorizations, "event_id")
    adjacent_event_ids = {event_id for event_id, route in route_by_event.items() if route == "ADJACENT_FACTORIZATION"}
    factorization_exact = set(factorization_by_event) == adjacent_event_ids
    omitted_base_count = 0
    for event_id in adjacent_event_ids:
        row = factorization_by_event[event_id]
        pair = pair_by_event[event_id]
        source_clause = source_event_by_id[event_id]["attachment_voice_working_clause_de"]
        target_clause = event_by_id[event_id]["mixed_scope_voice_working_clause_de"]
        outer_phrase = pair["source_outer_phrase_de"]
        inner_phrase = pair["source_inner_phrase_de"]
        expected_source_pair = f"{outer_phrase} und {inner_phrase}"
        outer_suffix = " im äußeren Zweig"
        inner_suffix = " im inneren Zweig"
        if not outer_phrase.endswith(outer_suffix) or not inner_phrase.endswith(inner_suffix):
            factorization_exact = False
            continue
        base = outer_phrase.removesuffix(outer_suffix)
        factorized_phrase = f"{base} im äußeren und im inneren Zweig"
        factorization_exact &= inner_phrase.removesuffix(inner_suffix) == base
        factorization_exact &= row["source_pair_phrase_de"] == expected_source_pair
        factorization_exact &= row["factorized_phrase_de"] == factorized_phrase
        factorization_exact &= row["shared_base_de"] == base
        factorization_exact &= source_clause.count(expected_source_pair) == 1
        factorization_exact &= target_clause == source_clause.replace(expected_source_pair, factorized_phrase, 1)
        factorization_exact &= expected_source_pair.count(base) == 2
        factorization_exact &= factorized_phrase.count(base) == 1
        omitted_base_count += expected_source_pair.count(base) - factorized_phrase.count(base)
        shared_start, shared_end = int(row["shared_base_start"]), int(row["shared_base_end"])
        outer_start, outer_end = int(row["outer_scope_start"]), int(row["outer_scope_end"])
        inner_start, inner_end = int(row["inner_scope_start"]), int(row["inner_scope_end"])
        factorization_exact &= target_clause[shared_start:shared_end] == base
        factorization_exact &= target_clause[outer_start:outer_end] == "äußeren"
        factorization_exact &= target_clause[inner_start:inner_end] == "inneren"
        factorization_exact &= shared_end <= outer_start < outer_end < inner_start < inner_end
        pair_slots = sorted(slots_by_event[event_id], key=lambda slot: int(slot["scope_atom_position_zero_based"]))
        factorization_exact &= len(pair_slots) == 2
        factorization_exact &= all(slot["root_expression_shared"] == "YES" for slot in pair_slots)
        factorization_exact &= len({(slot["root_expression_start"], slot["root_expression_end"]) for slot in pair_slots}) == 1
        factorization_exact &= {(slot["scope_marker_de"], slot["scope_marker_start"], slot["scope_marker_end"]) for slot in pair_slots} == {
            ("äußeren", row["outer_scope_start"], row["outer_scope_end"]),
            ("inneren", row["inner_scope_start"], row["inner_scope_end"]),
        }
    check("seven_adjacent_factorizations_exact", factorization_exact, len(factorization_by_event), 7)
    check("seven_base_omissions_with_fourteen_scope_slots", omitted_base_count == 7 and sum(row["root_expression_shared"] == "YES" for row in slots) == 14, [omitted_base_count, sum(row["root_expression_shared"] == "YES" for row in slots)], [7, 14])

    interrupted_slot_spans_exact = True
    for row in slots:
        target = event_by_id[row["event_id"]]["mixed_scope_voice_working_clause_de"]
        root_start, root_end = int(row["root_expression_start"]), int(row["root_expression_end"])
        marker_start, marker_end = int(row["scope_marker_start"]), int(row["scope_marker_end"])
        interrupted_slot_spans_exact &= target[root_start:root_end] == row["root_expression_de"]
        interrupted_slot_spans_exact &= target[marker_start:marker_end] == row["scope_marker_de"]
        interrupted_slot_spans_exact &= row["scope_marker_de"] == ("äußeren" if row["scope"] == "OUTER" else "inneren")
        interrupted_slot_spans_exact &= row["root_expression_shared"] == ("YES" if row["route"] == "ADJACENT_FACTORIZATION" else "NO")
        if row["route"] == "INTERRUPTED_SLOT_EXPLICIT":
            fragment = fragment_by_key[(row["event_id"], int(row["scope_atom_position_zero_based"]))]
            interrupted_slot_spans_exact &= row["rendered_fragment_de"] == fragment["rendered_fragment_de"]
            interrupted_slot_spans_exact &= (row["root_expression_start"], row["root_expression_end"]) == (fragment["root_expression_start"], fragment["root_expression_end"])
    check("all_scope_root_and_marker_spans_exact", interrupted_slot_spans_exact, "all" if interrupted_slot_spans_exact else "mismatch", "all")

    no_chronology = not any(
        re.search(r"\b(?:vor|nach) dem\b", row["rendered_fragment_de"], flags=re.IGNORECASE)
        for row in fragments
    )
    particle_occurrences = {
        word: sum(
            len(re.findall(rf"\b{re.escape(word)}\b", row["target_clause_de"], flags=re.IGNORECASE))
            for row in cards
        )
        for word in REPEAT_OR_COUNT_WORDS
    }
    check("pre_post_not_voiced_as_chronology", no_chronology, "none" if no_chronology else "found", "none")
    check("no_repeat_or_count_particles", sum(particle_occurrences.values()) == 0, particle_occurrences, {word: 0 for word in REPEAT_OR_COUNT_WORDS})

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
        row["gdt578_attachment_voice_clause_de"] == source_event_by_id[row["event_id"]]["attachment_voice_working_clause_de"]
        and row["gdt578_source_roundtrip_de"] == source_event_by_id[row["event_id"]]["attachment_voice_working_clause_de"]
        for row in events
    )
    check("event_byte_exact_gdt578_inverse", event_inverse_count == 5122, event_inverse_count, 5122)
    changed_event_ids = {row["event_id"] for row in events if row["scope_voice_status"] == "CHANGED_EVENT_KEYED_SCOPE_CARD"}
    check("changed_event_set", changed_event_ids == set(pair_by_event) == set(card_by_event), len(changed_event_ids), 17)
    check("changed_event_state_split", Counter(event_by_id[event_id]["state_status"] for event_id in changed_event_ids) == Counter({"NONSTATE_CARD": 17}), dict(Counter(event_by_id[event_id]["state_status"] for event_id in changed_event_ids)), {"NONSTATE_CARD": 17})
    unchanged_event_exact = all(
        row["mixed_scope_voice_working_clause_de"] == source_event_by_id[row["event_id"]]["attachment_voice_working_clause_de"]
        for row in events if row["event_id"] not in changed_event_ids
    )
    check("unchanged_events_exact", unchanged_event_exact, "all" if unchanged_event_exact else "mismatch", "all")

    card_integrity = True
    for event_id, card in card_by_event.items():
        source = source_event_by_id[event_id]
        pair = pair_by_event[event_id]
        card_integrity &= card["scope_pair_id"] == expected_pair_id[event_id]
        card_integrity &= card["gdt578_source_clause_de"] == source["attachment_voice_working_clause_de"]
        card_integrity &= card["gdt578_source_clause_sha256"] == text_sha256(card["gdt578_source_clause_de"])
        card_integrity &= card["target_clause_de"] == event_by_id[event_id]["mixed_scope_voice_working_clause_de"]
        card_integrity &= card["target_clause_sha256"] == text_sha256(card["target_clause_de"])
        card_integrity &= card["route"] == route_by_event[event_id]
        card_integrity &= card["attachment_topology"] == topology_by_event[event_id]
        card_integrity &= card["outer_atom_position_zero_based"] == pair["outer_atom_position_zero_based"]
        card_integrity &= card["inner_atom_position_zero_based"] == pair["inner_atom_position_zero_based"]
        card_integrity &= card["inverse_key"] == event_id
    check("event_cards_are_id_keyed_and_hashed", card_integrity and len({row["inverse_key"] for row in cards}) == 17, "all" if card_integrity else "mismatch", "all")

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
        event_ids = row["event_ids"].split("|")
        rebuilt = " ".join(event_by_id[event_id]["mixed_scope_voice_working_clause_de"] for event_id in event_ids)
        changed_members = [event_id for event_id in event_ids if event_id in changed_event_ids]
        statement_integrity &= row["mixed_scope_voice_working_reading_de"] == rebuilt
        statement_integrity &= row["scope_statement_changed"] == ("YES" if changed_members else "NO")
        statement_integrity &= int(row["scope_changed_event_count"]) == len(changed_members)
        statement_integrity &= row["scope_changed_event_ids"] == ("|".join(changed_members) or "NONE")
        statement_integrity &= row["retained_gdt578_changed_event_ids"] == source["changed_event_ids"]
        if (
            row["gdt578_attachment_voice_reading_de"] == source["attachment_voice_working_reading_de"]
            and row["gdt578_source_roundtrip_de"] == source["attachment_voice_working_reading_de"]
        ):
            statement_inverse_count += 1
    check("statements_rebuilt_from_event_ids", statement_integrity, "all" if statement_integrity else "mismatch", "all")
    check("statement_byte_exact_gdt578_inverse", statement_inverse_count == 793, statement_inverse_count, 793)
    changed_statement_ids = {row["statement_id"] for row in statements if row["scope_statement_changed"] == "YES"}
    check("changed_statement_count", len(changed_statement_ids) == 17, len(changed_statement_ids), 17)

    expected_overlap_rows: dict[str, tuple[list[str], list[str]]] = {}
    for source in source_statements:
        event_ids = source["event_ids"].split("|")
        scope_members = [event_id for event_id in event_ids if event_id in changed_event_ids]
        prior_members = [] if source["changed_event_ids"] == "NONE" else source["changed_event_ids"].split("|")
        if scope_members and prior_members:
            expected_overlap_rows[source["statement_id"]] = (scope_members, prior_members)
    overlap_by_statement = unique_index(overlaps, "statement_id")
    overlap_exact = set(overlap_by_statement) == set(expected_overlap_rows) == OVERLAP_STATEMENTS
    for statement_id, (scope_members, prior_members) in expected_overlap_rows.items():
        row = overlap_by_statement[statement_id]
        overlap_exact &= row["scope_event_ids"] == "|".join(scope_members)
        overlap_exact &= row["retained_gdt578_event_ids"] == "|".join(prior_members)
        overlap_exact &= int(row["retained_gdt578_event_count"]) == len(prior_members)
        overlap_exact &= row["gdt578_source_reading_sha256"] == text_sha256(source_statement_by_id[statement_id]["attachment_voice_working_reading_de"])
        overlap_exact &= row["target_reading_sha256"] == text_sha256(statement_by_id[statement_id]["mixed_scope_voice_working_reading_de"])
    retained_set = {event_id for _, prior in expected_overlap_rows.values() for event_id in prior}
    retained_events_exact = retained_set == RETAINED_GDT578_EVENTS and all(
        event_by_id[event_id]["mixed_scope_voice_working_clause_de"] == source_event_by_id[event_id]["attachment_voice_working_clause_de"]
        for event_id in retained_set
    )
    check("three_overlap_statements_rebuilt", overlap_exact, sorted(overlap_by_statement), sorted(OVERLAP_STATEMENTS))
    check("four_prior_gdt578_events_preserved", retained_events_exact, sorted(retained_set), sorted(RETAINED_GDT578_EVENTS))

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
        scope_events = sum(event["event_id"] in changed_event_ids for event in events_by_page[row["physical_page"]])
        scope_statements = sum(statement["statement_id"] in changed_statement_ids for statement in statements_by_page[row["physical_page"]])
        page_integrity &= row["prior_gdt578_changed_event_count"] == source["changed_event_count"]
        page_integrity &= row["prior_gdt578_changed_statement_count"] == source["changed_statement_count"]
        page_integrity &= int(row["scope_changed_event_count"]) == scope_events
        page_integrity &= int(row["scope_changed_statement_count"]) == scope_statements
        page_integrity &= row["page_scope_changed"] == ("YES" if scope_events else "NO")
        if scope_events:
            changed_page_ids.add(row["physical_page"])
    check("page_profiles_recomputed", page_integrity, "all" if page_integrity else "mismatch", "all")
    check("changed_page_count", len(changed_page_ids) == 10, len(changed_page_ids), 10)
    no_f84 = not any(
        row["physical_page"].startswith("f84")
        for row in events + statements + pages + source_pairs
    )
    check("forbidden_pages_absent", no_f84, "none" if no_f84 else "found", "none")

    cumulative_event_changes = sum(
        row["mixed_scope_voice_working_clause_de"] != old_event_by_id[row["event_id"]]["action_count_working_clause_de"]
        for row in events
    )
    cumulative_statement_changes = sum(
        row["mixed_scope_voice_working_reading_de"] != old_statement_by_id[row["statement_id"]]["action_count_working_reading_de"]
        for row in statements
    )
    cumulative_page_changes = len({
        row["physical_page"] for row in events
        if row["mixed_scope_voice_working_clause_de"] != old_event_by_id[row["event_id"]]["action_count_working_clause_de"]
    })
    check("cumulative_gdt574_changes_recomputed", [cumulative_event_changes, cumulative_statement_changes, cumulative_page_changes] == [763, 309, 28], [cumulative_event_changes, cumulative_statement_changes, cumulative_page_changes], [763, 309, 28])

    expected_result_values = {
        "event_count": 5122,
        "statement_count": 793,
        "page_count": 30,
        "route_count": 2,
        "scope_pair_count": 17,
        "scope_slot_count": 34,
        "outer_scope_slot_count": 17,
        "inner_scope_slot_count": 17,
        "adjacent_factorized_pair_count": 7,
        "adjacent_shared_base_slot_count": 14,
        "interrupted_pair_count": 10,
        "interrupted_scope_slot_count": 20,
        "intervening_atom_count": 15,
        "intervening_action_count": 10,
        "intervening_modifier_or_siglum_count": 5,
        "ordered_interrupted_modifier_fragment_count": 27,
        "interrupted_pair_modifier_fragment_count": 20,
        "interrupted_nonpair_modifier_fragment_count": 7,
        "changed_event_count_against_gdt578": 17,
        "changed_nonstate_event_count_against_gdt578": 17,
        "changed_state_event_count_against_gdt578": 0,
        "changed_statement_count_against_gdt578": 17,
        "changed_page_count_against_gdt578": 10,
        "cumulative_changed_event_count_against_gdt574": 763,
        "cumulative_changed_statement_count_against_gdt574": 309,
        "cumulative_changed_page_count_against_gdt574": 28,
        "gdt578_target_event_overlap_count": 0,
        "overlap_statement_count": 3,
        "retained_gdt578_event_count_in_overlap_statements": 4,
        "exact_event_id_roundtrip_count": 5122,
        "exact_statement_id_roundtrip_count": 793,
    }
    check(
        "result_counts_recomputed",
        all(result.get(key) == value for key, value in expected_result_values.items()),
        {key: result.get(key) for key in expected_result_values},
        expected_result_values,
    )
    check("result_assignment_counts", result.get("assignment_source_counts") == dict(sorted(expected_source_counts.items())), result.get("assignment_source_counts"), dict(sorted(expected_source_counts.items())))
    check("result_placement_counts", result.get("placement_counts") == dict(sorted(placement_counts.items())), result.get("placement_counts"), dict(sorted(placement_counts.items())))
    check(
        "result_boolean_guards",
        all(result.get(key) is True for key in [
            "no_new_page", "no_new_event", "no_new_statement", "no_root_change",
            "no_recipe_change", "no_scope_count_voice",
        ]) and result.get("pre_post_process_chronology_added") is False,
        "all",
        "all",
    )

    route_by_name = unique_index(routes, "route")
    route_rows_exact = (
        set(route_by_name) == {"ADJACENT_FACTORIZATION", "INTERRUPTED_SLOT_EXPLICIT"}
        and [int(route_by_name["ADJACENT_FACTORIZATION"][field]) for field in ["pair_count", "scope_slot_count", "intervening_atom_count", "ordered_modifier_fragment_count"]] == [7, 14, 0, 0]
        and [int(route_by_name["INTERRUPTED_SLOT_EXPLICIT"][field]) for field in ["pair_count", "scope_slot_count", "intervening_atom_count", "ordered_modifier_fragment_count"]] == [10, 20, 15, 27]
    )
    check("route_cards_recomputed", route_rows_exact, "exact" if route_rows_exact else "mismatch", "exact")

    guard_checks = {
        "routes": all(row["guard"] in {"SHARED_BASE_WITH_TWO_SEPARATE_SCOPE_SPANS__NO_COUNT", "FULL_BASE_PER_SCOPE_SLOT__NO_PRE_POST_PROCESS_CHRONOLOGY"} for row in routes),
        "profiles": all(row["guard"] == "OUTER_AND_INNER_SLOT_IDENTITIES_RETAINED__NO_SCOPE_COUNT" for row in profiles),
        "slots": all(row["guard"] in {"WRITTEN_SCOPE_SLOT_RETAINED__SHARED_BASE_ONLY_IN_ADJACENT_ROUTE", "WRITTEN_SCOPE_SLOT_RETAINED__FULL_BASE_IN_INTERRUPTED_ROUTE"} for row in slots),
        "intervening": all(row["guard"] == "STRICTLY_BETWEEN_OUTER_AND_INNER__RAW_POSITION_RETAINED" for row in intervening),
        "fragments": all(row["guard"] == "RAW_MODIFIER_ATOM_ORDER__NO_PRE_POST_PROCESS_CHRONOLOGY" for row in fragments),
        "factorizations": all(row["guard"] == "ONE_SHARED_BASE__TWO_ORDERED_SCOPE_SPANS__NO_COUNT_VOICE" for row in factorizations),
        "cards": all(row["guard"] == "EXPLICIT_EVENT_ID_INVERSE__NEVER_TEXT_KEYED" for row in cards),
        "overlaps": all(row["guard"] == "STATEMENT_REBUILT_FROM_EVENT_IDS__PRIOR_GDT578_EVENTS_RETAINED" for row in overlaps),
        "events": all(row["guard"] == "EVENT_ID_KEYED_EDITION__GDT578_SOURCE_ROUNDTRIP_EXACT" for row in events),
        "statements": all(row["guard"] == "STATEMENT_REBUILT_ONLY_FROM_EVENT_IDS__GDT578_SOURCE_ROUNDTRIP_EXACT" for row in statements),
        "pages": all(row["guard"] == "SOURCE_PAGE_ORDER_MEMBERSHIP_AND_COUNTS_UNCHANGED" for row in pages),
    }
    check("artifact_guards", all(guard_checks.values()), guard_checks, {key: True for key in guard_checks})

    failures = [row for row in checks if row["status"] != "PASS"]
    validation = {
        "experiment_id": "GDT579",
        "status": "PASS" if not failures else "FAIL",
        "check_count": len(checks),
        "pass_count": len(checks) - len(failures),
        "fail_count": len(failures),
        "checks": checks,
    }
    (OUT / "gdt579_validation.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
