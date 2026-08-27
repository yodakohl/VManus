#!/usr/bin/env python3
"""Render all seventeen outer/inner pairs without collapsing either scope slot."""

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
STATUS = (
    "PASS_17_SCOPE_PAIRS__7_ADJACENT_FACTORIZED__10_INTERRUPTED_SLOT_EXPLICIT__"
    "34_SCOPE_SLOTS__15_INTERVENING_ATOMS__27_ORDERED_MODIFIER_FRAGMENTS__"
    "5122_EXACT_ROUNDTRIPS"
)

ACTIONS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
ARGUMENTS = {"Y", "AIIN", "AIN", "OR"}
STATE_CONTROLS = {"OT", "OL", "DY"}
FIXED_FOCUS_ROOTS = {"E", "AR", "AL", "L"}
OUTER_SUFFIX = " im äußeren Zweig"
INNER_SUFFIX = " im inneren Zweig"
ACTIVE_CONTEXT_EXCEPTION_EVENT = "G515-E0385"
ACTIVE_CONTEXT_SOURCE_EVENT = "G515-E0383"

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

RELATION_FRAGMENTS = {
    "SOURCE_SECTION_T": {
        "AL": "zur Zielspalte",
        "AR": "von der Ausgangszeile",
        "L": "über die Eintragsverbindung",
        "AIR": "entlang der Lesebahn",
    },
    "HERBAL": {
        "AL": "zur Zielstelle",
        "AR": "vom Ausgangsmaterial",
        "L": "über die Verbindung im Pflanzenartikel",
        "AIR": "entlang der Verarbeitungsbahn",
    },
    "BIOLOGICAL": {
        "AL": "zur Zielstation",
        "AR": "von der Ausgangsstation",
        "L": "über die sichtbare Verbindung",
        "AIR": "entlang der Stationsbahn",
    },
    "CELESTIAL": {
        "AL": "zur Zielposition",
        "AR": "von der Ausgangsposition",
        "L": "über die Ringverbindung",
        "AIR": "entlang der Ringbahn",
    },
    "PHARMA": {
        "AL": "zum Zielgefäß",
        "AR": "vom Ausgangsgefäß",
        "L": "über die Gefäßverbindung",
        "AIR": "entlang der Transferbahn",
    },
}

BASE_FRAGMENTS = {
    "E": "auf Grad I",
    "EE": "auf Grad II",
    "EEE": "auf Grad III",
    "IIN": "auf der bezeichneten Stufe",
    "DA": "auf der zweiten Stufe",
    "O": "als Ausführung",
    "CARRIER_Q": "als neuen Einsatz",
    "D_ADDR": "an der D-Stelle",
    "A_ADDR": "an der A-Stelle",
    "AM_ADDR": "an der AM-Stelle",
    "S_ADDR": "an der S-Stelle",
    "LOCAL_CHAR_F": "bei der f-Kennmarke",
    "M_LOCAL": "bei der m-Ortsmarke",
    "D_LABEL": "beim d-Vermerk",
    "LOCAL_CHAR_I": "mit der i-Variante",
    "LOCAL_CHAR_G": "mit der g-Variante",
    "G_LABEL": "beim G-Vermerk",
    "LOCAL_CHAR_B": "mit der b-Variante",
    "LOCAL_CHAR_J": "mit der j-Variante",
    "AN": "in der bezeichneten Klasse",
    "HO": "in der bezeichneten Klasse",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty table {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0]),
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def base_fragment(register: str, atom: str) -> str:
    if atom in BASE_FRAGMENTS:
        return BASE_FRAGMENTS[atom]
    if atom in RELATION_FRAGMENTS[register]:
        return RELATION_FRAGMENTS[register][atom]
    raise RuntimeError(f"No modifier voice for {register}:{atom}")


def scope_base(register: str, atom: str) -> str:
    # Scoped O already has the licensed directional voice "zur Ausführung";
    # unscoped O remains GDT578's "als Ausführung" outside these pair events.
    # D_ADDR retains GDT576's learned siglum instead of GDT575's older generic
    # address wording.
    if atom == "O":
        return "zur Ausführung"
    return base_fragment(register, atom)


def target_modifier_base(register: str, atom: str) -> str:
    # The lone non-pair O tail in G515-E0157 already belongs to the same current
    # directional scope voice and must remain "zur Ausführung".
    return scope_base(register, atom) if atom == "O" else base_fragment(register, atom)


def fixed_attachment_map() -> dict[tuple[str, int], dict[str, str]]:
    result: dict[tuple[str, int], dict[str, str]] = {}
    for row in read_tsv(INPUTS["old_attachments"]):
        key = (row["global_running_event_id"], int(row["focus_atom_ordinal"]) - 1)
        result[key] = {
            "assignment_source": "GDT407_FIXED_FOCUS_ATTACHMENT",
            "selector_rule": row["selector_rule"],
            "source_geometry": row["attachment_geometry"],
            "head_kind": row["head_kind"],
            "head_event_id": row["selected_action_global_event_id"],
            # VISIBLE_OWNER has raw ordinal 0 and therefore the required -1
            # normalized sentinel; never feed it to the action-cell lookup.
            "head_atom_position_zero_based": str(int(row["selected_action_atom_ordinal"]) - 1),
            "head_root": row["action_core"],
            "duplicate_mode": row["duplicate_mode"],
            "duplicate_role": row["duplicate_role"],
        }
    for row in read_tsv(INPUTS["new_attachments"]):
        key = (row["event_id"], int(row["focus_atom_ordinal"]) - 1)
        result[key] = {
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


def active_head_before(events: list[dict[str, str]]) -> dict[str, tuple[str, int, str] | None]:
    active: dict[tuple[str, str], tuple[str, int, str]] = {}
    before: dict[str, tuple[str, int, str] | None] = {}
    for row in events:
        key = (row["physical_page"], row["owner_id"])
        before[row["event_id"]] = active.get(key)
        for position, token in enumerate(row["final_context_recipe"].split("+")):
            if token in ACTIONS:
                active[key] = (row["event_id"], position, token)
    return before


def exploratory_visible_head(event: dict[str, str], slot_position: int) -> dict[str, str]:
    tokens = event["final_context_recipe"].split("+")
    left_controls = [
        position
        for position, token in enumerate(tokens)
        if token in STATE_CONTROLS and position < slot_position
    ]
    right_controls = [
        position
        for position, token in enumerate(tokens)
        if token in STATE_CONTROLS and position > slot_position
    ]
    left_boundary = max(left_controls) if left_controls else -1
    right_boundary = min(right_controls) if right_controls else len(tokens)
    actions = [
        position
        for position, token in enumerate(tokens)
        if token in ACTIONS and left_boundary < position < right_boundary
    ]
    if not actions:
        raise RuntimeError(f"No visible action for O scope slot {event['event_id']}:{slot_position}")
    head_position = min(
        actions,
        key=lambda position: (
            abs(position - slot_position),
            0 if position < slot_position else 1,
            position,
        ),
    )
    return {
        "assignment_source": "GDT577_EXPLORATORY_NEAREST_VISIBLE_ACTION",
        "selector_rule": "VISIBLE_ACTION_INSIDE_OT_OL_DY_INTERVAL",
        "source_geometry": "SAME_CARRIER_DISTANCE_MINIMUM__LEFT_TIE",
        "head_kind": "ORDINARY_ACTION_HEAD",
        "head_event_id": event["event_id"],
        "head_atom_position_zero_based": str(head_position),
        "head_root": tokens[head_position],
        "duplicate_mode": "ANALYTICAL_SCOPE_SLOT",
        "duplicate_role": "CANDIDATE_LOCAL_HEAD",
    }


def placement(
    event_id: str,
    slot_position: int,
    head_event_id: str,
    head_position: int,
    head_kind: str,
) -> str:
    if head_kind == "VISIBLE_OWNER" or head_event_id != event_id:
        return "CONTEXT_HEAD"
    if head_position < slot_position:
        return "POST_HEAD"
    if head_position > slot_position:
        return "PRE_HEAD"
    raise RuntimeError(f"Head and scope slot coincide at {event_id}:{slot_position}")


def action_cell_map(rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    cells = {(row["register"], row["action_root"]): row for row in rows}
    if len(cells) != 45:
        raise RuntimeError(f"Expected 45 GDT568 action cells, found {len(cells)}")
    return cells


def selected_head_nominal(
    assignment: dict[str, str],
    register: str,
    action_cells: dict[tuple[str, str], dict[str, str]],
    event_by_id: dict[str, dict[str, str]],
) -> str:
    if assignment["head_kind"] == "VISIBLE_OWNER" or assignment["head_root"] == "OWNER":
        return "sichtbaren Owner"
    cell = action_cells[(register, assignment["head_root"])]
    nominal = ACTION_NOMINAL_BY_CARD[cell["action_voice_card_id"]]
    head_event = event_by_id[assignment["head_event_id"]]
    positions = [
        position
        for position, atom in enumerate(head_event["final_context_recipe"].split("+"))
        if atom == assignment["head_root"]
    ]
    head_position = int(assignment["head_atom_position_zero_based"])
    if len(positions) > 1 and head_position in positions:
        ordinal = positions.index(head_position) + 1
        labels = {1: "ersten", 2: "zweiten", 3: "dritten", 4: "vierten"}
        nominal = f"{labels.get(ordinal, str(ordinal) + '.')} {nominal}"
    return nominal


def topology(assignments: list[dict[str, str]], event_id: str) -> str:
    head_keys = {
        (
            row["head_kind"],
            row["head_event_id"],
            row["head_atom_position_zero_based"],
        )
        for row in assignments
    }
    places = {row["placement"] for row in assignments}
    if len(head_keys) > 1:
        return "DISTINCT_ACTION_OCCURRENCES"
    if {"PRE_HEAD", "POST_HEAD"}.issubset(places):
        return "BRACKETING_SAME_HEAD"
    if "CONTEXT_HEAD" in places:
        return "ACTIVE_CONTEXT_HEAD"
    return "SAME_HEAD_SAME_SIDE"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    source_events = read_tsv(INPUTS["events"])
    source_statements = read_tsv(INPUTS["statements"])
    source_pages = read_tsv(INPUTS["pages"])
    scope_pairs = read_tsv(INPUTS["scope_pairs"])
    action_cells = action_cell_map(read_tsv(INPUTS["action_cells"]))
    old_events = read_tsv(INPUTS["gdt574_events"])
    old_statements = read_tsv(INPUTS["gdt574_statements"])
    if [len(source_events), len(source_statements), len(source_pages), len(scope_pairs)] != [5122, 793, 30, 17]:
        raise RuntimeError("GDT578/GDT575 input count drift")
    if len(old_events) != 5122 or len(old_statements) != 793:
        raise RuntimeError("GDT574 baseline count drift")
    if any(row["physical_page"].startswith("f84") for row in source_events + source_statements + source_pages):
        raise RuntimeError("Forbidden f84 material reached GDT579")

    event_by_id = {row["event_id"]: row for row in source_events}
    fixed = fixed_attachment_map()
    active_before = active_head_before(source_events)
    pair_by_event = {row["event_id"]: row for row in scope_pairs}
    if len(pair_by_event) != 17:
        raise RuntimeError("Scope-pair event identity drift")
    if any(event_by_id[event_id]["attachment_voice_status"] != "UNCHANGED_NON_TARGET" for event_id in pair_by_event):
        raise RuntimeError("A GDT579 scope event overlaps a GDT578 target event")

    assignments_by_event: dict[str, list[dict[str, str]]] = defaultdict(list)
    runtime_by_event: dict[str, dict[str, object]] = {}
    intervening_rows: list[dict[str, object]] = []
    assignment_source_counts: Counter[str] = Counter()

    for pair in scope_pairs:
        pair_ordinal = int(pair["scope_pair_ordinal"])
        event_id = pair["event_id"]
        event = event_by_id[event_id]
        tokens = event["final_context_recipe"].split("+")
        outer_position = int(pair["outer_atom_position_zero_based"])
        inner_position = int(pair["inner_atom_position_zero_based"])
        root = pair["underlying_atom"]
        if not (0 <= outer_position < inner_position < len(tokens)):
            raise RuntimeError(f"Invalid scope positions at {event_id}")
        if tokens[outer_position] != root or tokens[inner_position] != root:
            raise RuntimeError(f"Scope-root drift at {event_id}")
        route = "ADJACENT_FACTORIZATION" if inner_position == outer_position + 1 else "INTERRUPTED_SLOT_EXPLICIT"

        local_assignments: list[dict[str, str]] = []
        for scope, position in (("OUTER", outer_position), ("INNER", inner_position)):
            if root in FIXED_FOCUS_ROOTS:
                try:
                    assignment = dict(fixed[(event_id, position)])
                except KeyError as exc:
                    raise RuntimeError(f"Missing fixed scope head at {event_id}:{position}") from exc
            elif root == "O":
                assignment = exploratory_visible_head(event, position)
            elif root == "D_ADDR" and event_id == ACTIVE_CONTEXT_EXCEPTION_EVENT:
                active = active_before[event_id]
                if active is None:
                    raise RuntimeError("Missing active head for G515-E0385")
                head_event_id, head_position, head_root = active
                if (head_event_id, head_position, head_root) != (ACTIVE_CONTEXT_SOURCE_EVENT, 3, "R"):
                    raise RuntimeError(f"Active R context drift: {active}")
                assignment = {
                    "assignment_source": "EXPLICIT_G515_E0385_ACTIVE_R_CONTEXT_CARD",
                    "selector_rule": "SAME_PAGE_OWNER_ACTIVE_R_HEAD",
                    "source_geometry": "OWNER_ACTIVE_ACTION_CONTEXT",
                    "head_kind": "ORDINARY_ACTION_HEAD",
                    "head_event_id": head_event_id,
                    "head_atom_position_zero_based": str(head_position),
                    "head_root": head_root,
                    "duplicate_mode": "ANALYTICAL_SCOPE_SLOT",
                    "duplicate_role": "EXPLICIT_CONTEXT_HEAD",
                }
            else:
                raise RuntimeError(f"No scope-head route for {event_id}:{root}")
            assignment.update({
                "scope_pair_ordinal": str(pair_ordinal),
                "scope_pair_id": f"GDT579-P{pair_ordinal:02d}",
                "event_id": event_id,
                "scope": scope,
                "scope_atom_position_zero_based": str(position),
                "scope_root": root,
            })
            assignment["placement"] = placement(
                event_id,
                position,
                assignment["head_event_id"],
                int(assignment["head_atom_position_zero_based"]),
                assignment["head_kind"],
            )
            assignment["head_identity"] = (
                f"{assignment['head_kind']}:{assignment['head_event_id']}@"
                f"{assignment['head_atom_position_zero_based']}:{assignment['head_root']}"
            )
            assignment["head_nominal_de"] = selected_head_nominal(
                assignment,
                event["register"],
                action_cells,
                event_by_id,
            )
            assignment_source_counts[assignment["assignment_source"]] += 1
            assignments_by_event[event_id].append(assignment)
            local_assignments.append(assignment)

        local_topology = topology(local_assignments, event_id)
        runtime_by_event[event_id] = {
            "pair": pair,
            "route": route,
            "topology": local_topology,
            "outer_position": outer_position,
            "inner_position": inner_position,
            "intervening_atom_count": inner_position - outer_position - 1,
        }

        if route == "INTERRUPTED_SLOT_EXPLICIT":
            for position in range(outer_position + 1, inner_position):
                atom = tokens[position]
                if atom in ACTIONS:
                    atom_class = "ACTION"
                    probe = {
                        "head_kind": "ORDINARY_ACTION_HEAD",
                        "head_event_id": event_id,
                        "head_atom_position_zero_based": str(position),
                        "head_root": atom,
                    }
                    voice = selected_head_nominal(probe, event["register"], action_cells, event_by_id)
                elif atom in ARGUMENTS:
                    atom_class = "ARGUMENT"
                    voice = "RETAINED_IN_ACTION_ARGUMENT_BLOCK"
                elif atom in STATE_CONTROLS:
                    atom_class = "STATE_CONTROL"
                    voice = "RETAINED_SEQUENCE_CONTROL"
                else:
                    atom_class = "MODIFIER_OR_SIGLUM"
                    voice = target_modifier_base(event["register"], atom)
                intervening_rows.append({
                    "intervening_atom_ordinal": len(intervening_rows) + 1,
                    "scope_pair_id": f"GDT579-P{pair_ordinal:02d}",
                    "event_id": event_id,
                    "statement_id": event["statement_id"],
                    "register": event["register"],
                    "surface": event["surface"],
                    "final_context_recipe": event["final_context_recipe"],
                    "atom_position_zero_based": position,
                    "atom": atom,
                    "atom_class": atom_class,
                    "retained_voice_de": voice,
                    "guard": "STRICTLY_BETWEEN_OUTER_AND_INNER__RAW_POSITION_RETAINED",
                })

    if Counter(runtime["route"] for runtime in runtime_by_event.values()) != Counter({"ADJACENT_FACTORIZATION": 7, "INTERRUPTED_SLOT_EXPLICIT": 10}):
        raise RuntimeError("Seven/ten route split drift")
    if len(intervening_rows) != 15:
        raise RuntimeError(f"Expected fifteen intervening atoms, found {len(intervening_rows)}")
    intervening_classes = Counter(row["atom_class"] for row in intervening_rows)
    if intervening_classes != Counter({"ACTION": 10, "MODIFIER_OR_SIGLUM": 5}):
        raise RuntimeError(f"Intervening atom classes drift: {intervening_classes}")
    if assignment_source_counts != Counter({
        "GDT407_FIXED_FOCUS_ATTACHMENT": 20,
        "GDT515_FIXED_FOCUS_ATTACHMENT": 8,
        "GDT577_EXPLORATORY_NEAREST_VISIBLE_ACTION": 4,
        "EXPLICIT_G515_E0385_ACTIVE_R_CONTEXT_CARD": 2,
    }):
        raise RuntimeError(f"Scope-head source drift: {assignment_source_counts}")

    placement_counts = Counter(
        row["placement"] for assignments in assignments_by_event.values() for row in assignments
    )
    if placement_counts != Counter({"POST_HEAD": 25, "PRE_HEAD": 3, "CONTEXT_HEAD": 6}):
        raise RuntimeError(f"Scope placement drift: {placement_counts}")
    adjacent_topologies = Counter(
        str(runtime["topology"])
        for runtime in runtime_by_event.values()
        if runtime["route"] == "ADJACENT_FACTORIZATION"
    )
    interrupted_topologies = Counter(
        str(runtime["topology"])
        for runtime in runtime_by_event.values()
        if runtime["route"] == "INTERRUPTED_SLOT_EXPLICIT"
    )
    if adjacent_topologies != Counter({"SAME_HEAD_SAME_SIDE": 5, "ACTIVE_CONTEXT_HEAD": 2}):
        raise RuntimeError(f"Adjacent topology drift: {adjacent_topologies}")
    if interrupted_topologies != Counter({
        "DISTINCT_ACTION_OCCURRENCES": 7,
        "BRACKETING_SAME_HEAD": 2,
        "ACTIVE_CONTEXT_HEAD": 1,
    }):
        raise RuntimeError(f"Interrupted topology drift: {interrupted_topologies}")

    target_by_event: dict[str, str] = {}
    factorization_rows: list[dict[str, object]] = []
    fragment_rows: list[dict[str, object]] = []
    slot_rows_unordered: list[dict[str, object]] = []
    event_card_rows: list[dict[str, object]] = []
    event_rows: list[dict[str, object]] = []

    for source in source_events:
        event_id = source["event_id"]
        source_clause = source["attachment_voice_working_clause_de"]
        runtime = runtime_by_event.get(event_id)
        if runtime is None:
            target_clause = source_clause
            route = "NONE"
            pair_id = "NONE"
        else:
            pair = runtime["pair"]
            assert isinstance(pair, dict)
            route = str(runtime["route"])
            pair_id = f"GDT579-P{int(pair['scope_pair_ordinal']):02d}"
            root = pair["underlying_atom"]
            base = scope_base(source["register"], root)
            outer_phrase = base + OUTER_SUFFIX
            inner_phrase = base + INNER_SUFFIX
            assignments = sorted(
                assignments_by_event[event_id],
                key=lambda row: int(row["scope_atom_position_zero_based"]),
            )

            if route == "ADJACENT_FACTORIZATION":
                source_pair_phrase = f"{outer_phrase} und {inner_phrase}"
                factorized_phrase = f"{base} im äußeren und im inneren Zweig"
                if source_clause.count(source_pair_phrase) != 1:
                    raise RuntimeError(f"Adjacent source phrase drift at {event_id}: {source_pair_phrase}")
                target_clause = source_clause.replace(source_pair_phrase, factorized_phrase, 1)
                phrase_start = target_clause.index(factorized_phrase)
                shared_start = phrase_start
                shared_end = shared_start + len(base)
                outer_start = phrase_start + factorized_phrase.index("äußeren")
                inner_start = phrase_start + factorized_phrase.index("inneren")
                factorization_rows.append({
                    "factorization_ordinal": len(factorization_rows) + 1,
                    "scope_pair_id": pair_id,
                    "event_id": event_id,
                    "statement_id": source["statement_id"],
                    "register": source["register"],
                    "surface": source["surface"],
                    "final_context_recipe": source["final_context_recipe"],
                    "outer_atom_position_zero_based": pair["outer_atom_position_zero_based"],
                    "inner_atom_position_zero_based": pair["inner_atom_position_zero_based"],
                    "source_pair_phrase_de": source_pair_phrase,
                    "factorized_phrase_de": factorized_phrase,
                    "shared_base_de": base,
                    "shared_base_start": shared_start,
                    "shared_base_end": shared_end,
                    "outer_scope_start": outer_start,
                    "outer_scope_end": outer_start + len("äußeren"),
                    "inner_scope_start": inner_start,
                    "inner_scope_end": inner_start + len("inneren"),
                    "guard": "ONE_SHARED_BASE__TWO_ORDERED_SCOPE_SPANS__NO_COUNT_VOICE",
                })
                scope_span_by_name = {
                    "OUTER": (outer_start, outer_start + len("äußeren")),
                    "INNER": (inner_start, inner_start + len("inneren")),
                }
                for assignment in assignments:
                    scope_start, scope_end = scope_span_by_name[assignment["scope"]]
                    slot_rows_unordered.append({
                        **assignment,
                        "route": route,
                        "attachment_topology": runtime["topology"],
                        "rendered_fragment_de": factorized_phrase,
                        "root_expression_de": base,
                        "root_expression_start": shared_start,
                        "root_expression_end": shared_end,
                        "root_expression_shared": "YES",
                        "scope_marker_de": "äußeren" if assignment["scope"] == "OUTER" else "inneren",
                        "scope_marker_start": scope_start,
                        "scope_marker_end": scope_end,
                        "guard": "WRITTEN_SCOPE_SLOT_RETAINED__SHARED_BASE_ONLY_IN_ADJACENT_ROUTE",
                    })
            else:
                action_block = source_clause.removesuffix(".").split("; ", 1)[0]
                atoms = source["final_context_recipe"].split("+")
                assignment_by_position = {
                    int(row["scope_atom_position_zero_based"]): row for row in assignments
                }
                local_fragments: list[dict[str, object]] = []
                for position, atom in enumerate(atoms):
                    if atom in ACTIONS or atom in ARGUMENTS or atom in STATE_CONTROLS:
                        continue
                    assignment = assignment_by_position.get(position)
                    if assignment:
                        fragment_base = scope_base(source["register"], atom)
                        scope_suffix = OUTER_SUFFIX if assignment["scope"] == "OUTER" else INNER_SUFFIX
                        display = fragment_base + scope_suffix
                        if assignment["placement"] == "CONTEXT_HEAD":
                            rendered = f"beim fortgeführten {assignment['head_nominal_de']}: {display}"
                        else:
                            rendered = f"beim {assignment['head_nominal_de']}: {display}"
                        binding_status = "SCOPE_SLOT_HEAD_BOUND"
                    else:
                        fragment_base = target_modifier_base(source["register"], atom)
                        rendered = fragment_base
                        binding_status = "UNBOUND_MODIFIER_IN_RAW_ORDER"
                    local_fragments.append({
                        "atom_position_zero_based": position,
                        "atom": atom,
                        "base_fragment_de": fragment_base,
                        "rendered_fragment_de": rendered,
                        "binding_status": binding_status,
                        "assignment": assignment,
                    })
                segments = [action_block] + [str(row["rendered_fragment_de"]) for row in local_fragments]
                if "DY" in atoms:
                    segments.append("schließe den Schritt")
                target_clause = "; ".join(segments) + "."

                cursor = len(action_block)
                outer_position = int(runtime["outer_position"])
                inner_position = int(runtime["inner_position"])
                for local_ordinal, fragment in enumerate(local_fragments, 1):
                    cursor += 2
                    rendered = str(fragment["rendered_fragment_de"])
                    start = cursor
                    end = start + len(rendered)
                    fragment_base = str(fragment["base_fragment_de"])
                    base_offset = rendered.find(fragment_base)
                    if base_offset < 0 or rendered.find(fragment_base, base_offset + 1) >= 0:
                        raise RuntimeError(f"Modifier span ambiguity at {event_id}:{fragment['atom_position_zero_based']}")
                    root_start = start + base_offset
                    root_end = root_start + len(fragment_base)
                    position = int(fragment["atom_position_zero_based"])
                    fragment_rows.append({
                        "fragment_ordinal": len(fragment_rows) + 1,
                        "scope_pair_id": pair_id,
                        "event_id": event_id,
                        "statement_id": source["statement_id"],
                        "register": source["register"],
                        "surface": source["surface"],
                        "final_context_recipe": source["final_context_recipe"],
                        "fragment_ordinal_in_event": local_ordinal,
                        "atom_position_zero_based": position,
                        "atom": fragment["atom"],
                        "base_fragment_de": fragment_base,
                        "rendered_fragment_de": rendered,
                        "target_fragment_start": start,
                        "target_fragment_end": end,
                        "root_expression_start": root_start,
                        "root_expression_end": root_end,
                        "scope_slot": "YES" if fragment["assignment"] else "NO",
                        "between_pair_positions": "YES" if outer_position < position < inner_position else "NO",
                        "binding_status": fragment["binding_status"],
                        "guard": "RAW_MODIFIER_ATOM_ORDER__NO_PRE_POST_PROCESS_CHRONOLOGY",
                    })
                    assignment = fragment["assignment"]
                    if assignment:
                        marker = "äußeren" if assignment["scope"] == "OUTER" else "inneren"
                        marker_offset = rendered.find(marker)
                        if marker_offset < 0 or rendered.find(marker, marker_offset + 1) >= 0:
                            raise RuntimeError(f"Scope marker ambiguity at {event_id}:{position}")
                        slot_rows_unordered.append({
                            **assignment,
                            "route": route,
                            "attachment_topology": runtime["topology"],
                            "rendered_fragment_de": rendered,
                            "root_expression_de": fragment_base,
                            "root_expression_start": root_start,
                            "root_expression_end": root_end,
                            "root_expression_shared": "NO",
                            "scope_marker_de": marker,
                            "scope_marker_start": start + marker_offset,
                            "scope_marker_end": start + marker_offset + len(marker),
                            "guard": "WRITTEN_SCOPE_SLOT_RETAINED__FULL_BASE_IN_INTERRUPTED_ROUTE",
                        })
                    cursor = end
                if "DY" in atoms:
                    cursor += 2 + len("schließe den Schritt")
                if cursor + 1 != len(target_clause):
                    raise RuntimeError(f"Interrupted target cursor drift at {event_id}")

            if target_clause == source_clause:
                raise RuntimeError(f"Scope event did not change: {event_id}")
            event_card_rows.append({
                "event_card_ordinal": len(event_card_rows) + 1,
                "scope_pair_id": pair_id,
                "event_id": event_id,
                "statement_id": source["statement_id"],
                "physical_page": source["physical_page"],
                "register": source["register"],
                "surface": source["surface"],
                "final_context_recipe": source["final_context_recipe"],
                "state_status": source["state_status"],
                "route": route,
                "attachment_topology": runtime["topology"],
                "gdt578_source_clause_de": source_clause,
                "gdt578_source_clause_sha256": text_sha256(source_clause),
                "target_clause_de": target_clause,
                "target_clause_sha256": text_sha256(target_clause),
                "outer_atom_position_zero_based": pair["outer_atom_position_zero_based"],
                "inner_atom_position_zero_based": pair["inner_atom_position_zero_based"],
                "intervening_atom_count": runtime["intervening_atom_count"],
                "inverse_key": event_id,
                "guard": "EXPLICIT_EVENT_ID_INVERSE__NEVER_TEXT_KEYED",
            })

        target_by_event[event_id] = target_clause
        # The inverse is deliberately keyed by event identity.  No lookup by
        # source or target wording is ever performed.
        roundtrip = source_clause
        event_rows.append({
            "edition_event_ordinal": source["edition_event_ordinal"],
            "event_id": event_id,
            "statement_id": source["statement_id"],
            "card_ordinal_in_statement": source["card_ordinal_in_statement"],
            "physical_page": source["physical_page"],
            "register": source["register"],
            "owner_id": source["owner_id"],
            "surface": source["surface"],
            "final_context_recipe": source["final_context_recipe"],
            "state_status": source["state_status"],
            "state_marker_sequence": source["state_marker_sequence"],
            "gdt578_attachment_voice_clause_de": source_clause,
            "mixed_scope_voice_working_clause_de": target_clause,
            "gdt578_source_roundtrip_de": roundtrip,
            "scope_voice_status": "CHANGED_EVENT_KEYED_SCOPE_CARD" if runtime else "UNCHANGED_NON_SCOPE_EVENT",
            "scope_pair_id": pair_id,
            "scope_route": route,
            "guard": "EVENT_ID_KEYED_EDITION__GDT578_SOURCE_ROUNDTRIP_EXACT",
        })

    if len(event_rows) != 5122 or len(event_card_rows) != 17:
        raise RuntimeError("Complete event output drift")
    if len(factorization_rows) != 7 or len(fragment_rows) != 27:
        raise RuntimeError("Seven factorization / twenty-seven fragment count drift")
    if sum(row["scope_slot"] == "YES" for row in fragment_rows) != 20:
        raise RuntimeError("Interrupted scope-slot fragment count drift")
    if sum(row["scope_slot"] == "NO" for row in fragment_rows) != 7:
        raise RuntimeError("Interrupted non-pair modifier count drift")

    slot_rows_unordered.sort(
        key=lambda row: (
            int(str(row["scope_pair_ordinal"])),
            int(str(row["scope_atom_position_zero_based"])),
        )
    )
    slot_rows: list[dict[str, object]] = []
    for ordinal, row in enumerate(slot_rows_unordered, 1):
        slot_rows.append({"scope_slot_ordinal": ordinal, **row})
    if len(slot_rows) != 34:
        raise RuntimeError("Scope-slot output drift")
    if Counter(row["root_expression_shared"] for row in slot_rows) != Counter({"NO": 20, "YES": 14}):
        raise RuntimeError("Shared/full scope root span drift")

    event_card_by_id = {row["event_id"]: row for row in event_card_rows}
    for row in event_rows:
        inverse = event_card_by_id.get(row["event_id"])
        recovered = inverse["gdt578_source_clause_de"] if inverse else row["mixed_scope_voice_working_clause_de"]
        if recovered != row["gdt578_attachment_voice_clause_de"]:
            raise RuntimeError(f"Event-ID inverse failed at {row['event_id']}")

    changed_event_ids = set(pair_by_event)
    statement_rows: list[dict[str, object]] = []
    overlap_rows: list[dict[str, object]] = []
    for source in source_statements:
        event_ids = source["event_ids"].split("|")
        source_rebuilt = " ".join(event_by_id[event_id]["attachment_voice_working_clause_de"] for event_id in event_ids)
        if source_rebuilt != source["attachment_voice_working_reading_de"]:
            raise RuntimeError(f"GDT578 statement source drift at {source['statement_id']}")
        target = " ".join(target_by_event[event_id] for event_id in event_ids)
        changed_members = [event_id for event_id in event_ids if event_id in changed_event_ids]
        prior_changed = [] if source["changed_event_ids"] == "NONE" else source["changed_event_ids"].split("|")
        if changed_members and prior_changed:
            overlap_rows.append({
                "overlap_statement_ordinal": len(overlap_rows) + 1,
                "statement_id": source["statement_id"],
                "register": source["register"],
                "scope_event_ids": "|".join(changed_members),
                "retained_gdt578_event_ids": "|".join(prior_changed),
                "retained_gdt578_event_count": len(prior_changed),
                "gdt578_source_reading_sha256": text_sha256(source["attachment_voice_working_reading_de"]),
                "target_reading_sha256": text_sha256(target),
                "guard": "STATEMENT_REBUILT_FROM_EVENT_IDS__PRIOR_GDT578_EVENTS_RETAINED",
            })
        statement_rows.append({
            "edition_statement_ordinal": source["edition_statement_ordinal"],
            "statement_id": source["statement_id"],
            "physical_page": source["physical_page"],
            "register": source["register"],
            "owner_id": source["owner_id"],
            "event_count": source["event_count"],
            "state_card_count": source["state_card_count"],
            "nonstate_card_count": source["nonstate_card_count"],
            "statement_mode": source["statement_mode"],
            "event_ids": source["event_ids"],
            "surface_sequence": source["surface_sequence"],
            "gdt578_attachment_voice_reading_de": source["attachment_voice_working_reading_de"],
            "mixed_scope_voice_working_reading_de": target,
            "gdt578_source_roundtrip_de": source["attachment_voice_working_reading_de"],
            "scope_statement_changed": "YES" if changed_members else "NO",
            "scope_changed_event_count": len(changed_members),
            "scope_changed_event_ids": "|".join(changed_members) or "NONE",
            "retained_gdt578_changed_event_ids": "|".join(prior_changed) or "NONE",
            "end_mode": source["end_mode"],
            "guard": "STATEMENT_REBUILT_ONLY_FROM_EVENT_IDS__GDT578_SOURCE_ROUNDTRIP_EXACT",
        })

    if len(statement_rows) != 793:
        raise RuntimeError("Complete statement output drift")
    if len(overlap_rows) != 3 or sum(int(row["retained_gdt578_event_count"]) for row in overlap_rows) != 4:
        raise RuntimeError("Three-statement/four-event overlap drift")
    if {row["statement_id"] for row in overlap_rows} != {"G407-S055", "G407-S064", "G407-S650"}:
        raise RuntimeError("Overlap statement identity drift")

    changed_statement_ids = {
        row["statement_id"] for row in statement_rows if row["scope_statement_changed"] == "YES"
    }
    page_rows: list[dict[str, object]] = []
    for source in source_pages:
        page = source["physical_page"]
        page_events = [row for row in event_rows if row["physical_page"] == page]
        page_statements = [row for row in statement_rows if row["physical_page"] == page]
        scope_changed_events = [row for row in page_events if row["scope_voice_status"] == "CHANGED_EVENT_KEYED_SCOPE_CARD"]
        scope_changed_statements = [row for row in page_statements if row["scope_statement_changed"] == "YES"]
        page_rows.append({
            "page_ordinal": source["page_ordinal"],
            "physical_page": page,
            "registers": source["registers"],
            "event_count": source["event_count"],
            "statement_count": source["statement_count"],
            "state_event_count": source["state_event_count"],
            "nonstate_event_count": source["nonstate_event_count"],
            "prior_gdt578_changed_event_count": source["changed_event_count"],
            "prior_gdt578_changed_statement_count": source["changed_statement_count"],
            "scope_changed_event_count": len(scope_changed_events),
            "scope_changed_statement_count": len(scope_changed_statements),
            "page_scope_changed": "YES" if scope_changed_events else "NO",
            "page_status": source["page_status"],
            "guard": "SOURCE_PAGE_ORDER_MEMBERSHIP_AND_COUNTS_UNCHANGED",
        })
    if len(page_rows) != 30:
        raise RuntimeError("Complete page output drift")

    pair_profile_rows: list[dict[str, object]] = []
    for pair in scope_pairs:
        event_id = pair["event_id"]
        runtime = runtime_by_event[event_id]
        assignments = sorted(
            assignments_by_event[event_id],
            key=lambda row: int(row["scope_atom_position_zero_based"]),
        )
        pair_profile_rows.append({
            "pair_profile_ordinal": int(pair["scope_pair_ordinal"]),
            "scope_pair_id": f"GDT579-P{int(pair['scope_pair_ordinal']):02d}",
            "event_id": event_id,
            "statement_id": pair["statement_id"],
            "register": pair["register"],
            "surface": pair["surface"],
            "final_context_recipe": pair["final_context_recipe"],
            "scope_root": pair["underlying_atom"],
            "outer_atom_position_zero_based": pair["outer_atom_position_zero_based"],
            "inner_atom_position_zero_based": pair["inner_atom_position_zero_based"],
            "intervening_atom_count": runtime["intervening_atom_count"],
            "route": runtime["route"],
            "attachment_topology": runtime["topology"],
            "head_identity_trace": " | ".join(row["head_identity"] for row in assignments),
            "placement_trace": "+".join(row["placement"] for row in assignments),
            "gdt578_source_clause_de": event_by_id[event_id]["attachment_voice_working_clause_de"],
            "target_clause_de": target_by_event[event_id],
            "guard": "OUTER_AND_INNER_SLOT_IDENTITIES_RETAINED__NO_SCOPE_COUNT",
        })

    route_rows = [
        {
            "route_ordinal": 1,
            "route_id": "GDT579-R01",
            "route": "ADJACENT_FACTORIZATION",
            "pair_count": 7,
            "scope_slot_count": 14,
            "intervening_atom_count": 0,
            "ordered_modifier_fragment_count": 0,
            "voice_frame_de": "{BASE} im äußeren und im inneren Zweig",
            "guard": "SHARED_BASE_WITH_TWO_SEPARATE_SCOPE_SPANS__NO_COUNT",
        },
        {
            "route_ordinal": 2,
            "route_id": "GDT579-R02",
            "route": "INTERRUPTED_SLOT_EXPLICIT",
            "pair_count": 10,
            "scope_slot_count": 20,
            "intervening_atom_count": 15,
            "ordered_modifier_fragment_count": 27,
            "voice_frame_de": "beim {KOPF}: {BASE} im {SCOPE} Zweig; rohe Modifierfragmente bleiben geordnet",
            "guard": "FULL_BASE_PER_SCOPE_SLOT__NO_PRE_POST_PROCESS_CHRONOLOGY",
        },
    ]

    old_event_by_id = {row["event_id"]: row for row in old_events}
    old_statement_by_id = {row["statement_id"]: row for row in old_statements}
    cumulative_changed_event_count = sum(
        row["mixed_scope_voice_working_clause_de"]
        != old_event_by_id[row["event_id"]]["action_count_working_clause_de"]
        for row in event_rows
    )
    cumulative_changed_statement_count = sum(
        row["mixed_scope_voice_working_reading_de"]
        != old_statement_by_id[row["statement_id"]]["action_count_working_reading_de"]
        for row in statement_rows
    )
    cumulative_changed_pages = {
        row["physical_page"]
        for row in event_rows
        if row["mixed_scope_voice_working_clause_de"]
        != old_event_by_id[row["event_id"]]["action_count_working_clause_de"]
    }

    write_tsv(OUT / "gdt579_2_scope_voice_routes.tsv", route_rows)
    write_tsv(OUT / "gdt579_17_scope_pair_profiles.tsv", pair_profile_rows)
    write_tsv(OUT / "gdt579_34_scope_slot_assignments.tsv", slot_rows)
    write_tsv(OUT / "gdt579_15_intervening_atoms.tsv", intervening_rows)
    write_tsv(OUT / "gdt579_27_interrupted_modifier_fragments.tsv", fragment_rows)
    write_tsv(OUT / "gdt579_7_adjacent_factorizations.tsv", factorization_rows)
    write_tsv(OUT / "gdt579_17_event_cards.tsv", event_card_rows)
    write_tsv(OUT / "gdt579_3_overlap_statements.tsv", overlap_rows)
    write_tsv(OUT / "gdt579_5122_mixed_scope_event_edition.tsv", event_rows)
    write_tsv(OUT / "gdt579_793_mixed_scope_statement_edition.tsv", statement_rows)
    write_tsv(OUT / "gdt579_30_page_mixed_scope_profiles.tsv", page_rows)

    topology_counts = Counter(str(runtime["topology"]) for runtime in runtime_by_event.values())
    slot_topology_counts = Counter(str(row["attachment_topology"]) for row in slot_rows)
    result = {
        "experiment_id": "GDT579",
        "status": STATUS,
        "input_sha256": {key: sha256(path) for key, path in INPUTS.items()},
        "event_count": len(event_rows),
        "statement_count": len(statement_rows),
        "page_count": len(page_rows),
        "route_count": len(route_rows),
        "scope_pair_count": len(pair_profile_rows),
        "scope_slot_count": len(slot_rows),
        "outer_scope_slot_count": sum(row["scope"] == "OUTER" for row in slot_rows),
        "inner_scope_slot_count": sum(row["scope"] == "INNER" for row in slot_rows),
        "adjacent_factorized_pair_count": len(factorization_rows),
        "adjacent_shared_base_slot_count": sum(row["root_expression_shared"] == "YES" for row in slot_rows),
        "interrupted_pair_count": sum(runtime["route"] == "INTERRUPTED_SLOT_EXPLICIT" for runtime in runtime_by_event.values()),
        "interrupted_scope_slot_count": sum(row["root_expression_shared"] == "NO" for row in slot_rows),
        "intervening_atom_count": len(intervening_rows),
        "intervening_action_count": intervening_classes["ACTION"],
        "intervening_modifier_or_siglum_count": intervening_classes["MODIFIER_OR_SIGLUM"],
        "ordered_interrupted_modifier_fragment_count": len(fragment_rows),
        "interrupted_pair_modifier_fragment_count": sum(row["scope_slot"] == "YES" for row in fragment_rows),
        "interrupted_nonpair_modifier_fragment_count": sum(row["scope_slot"] == "NO" for row in fragment_rows),
        "assignment_source_counts": dict(sorted(assignment_source_counts.items())),
        "placement_counts": dict(sorted(placement_counts.items())),
        "adjacent_pair_topology_counts": dict(sorted(adjacent_topologies.items())),
        "interrupted_pair_topology_counts": dict(sorted(interrupted_topologies.items())),
        "pair_topology_counts": dict(sorted(topology_counts.items())),
        "slot_topology_counts": dict(sorted(slot_topology_counts.items())),
        "changed_event_count_against_gdt578": len(changed_event_ids),
        "changed_nonstate_event_count_against_gdt578": sum(event_by_id[event_id]["state_status"] == "NONSTATE_CARD" for event_id in changed_event_ids),
        "changed_state_event_count_against_gdt578": sum(event_by_id[event_id]["state_status"] == "STATE_CARD" for event_id in changed_event_ids),
        "changed_statement_count_against_gdt578": len(changed_statement_ids),
        "changed_page_count_against_gdt578": sum(row["page_scope_changed"] == "YES" for row in page_rows),
        "cumulative_changed_event_count_against_gdt574": cumulative_changed_event_count,
        "cumulative_changed_statement_count_against_gdt574": cumulative_changed_statement_count,
        "cumulative_changed_page_count_against_gdt574": len(cumulative_changed_pages),
        "gdt578_target_event_overlap_count": sum(
            event_by_id[event_id]["attachment_voice_status"] == "CHANGED_EVENT_KEYED_CARD"
            for event_id in changed_event_ids
        ),
        "overlap_statement_count": len(overlap_rows),
        "retained_gdt578_event_count_in_overlap_statements": sum(int(row["retained_gdt578_event_count"]) for row in overlap_rows),
        "exact_event_id_roundtrip_count": sum(
            row["gdt578_source_roundtrip_de"] == row["gdt578_attachment_voice_clause_de"]
            for row in event_rows
        ),
        "exact_statement_id_roundtrip_count": sum(
            row["gdt578_source_roundtrip_de"] == row["gdt578_attachment_voice_reading_de"]
            for row in statement_rows
        ),
        "no_new_page": True,
        "no_new_event": True,
        "no_new_statement": True,
        "no_root_change": True,
        "no_recipe_change": True,
        "no_scope_count_voice": True,
        "pre_post_process_chronology_added": False,
    }
    if result["exact_event_id_roundtrip_count"] != 5122 or result["exact_statement_id_roundtrip_count"] != 793:
        raise RuntimeError("Complete event/statement roundtrip drift")
    (OUT / "gdt579_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    statements_by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in statement_rows:
        statements_by_page[str(row["physical_page"])].append(row)
    lines = [
        "# GDT579 mixed outer/inner scope edition",
        "",
        f"Status: `{STATUS}`",
        "",
    ]
    for page in page_rows:
        page_id = str(page["physical_page"])
        lines.extend([f"## {page_id} · {page['registers']}", ""])
        for statement in statements_by_page[page_id]:
            marker = " · Scope-Stimme" if statement["scope_statement_changed"] == "YES" else ""
            lines.extend([
                f"### {statement['statement_id']}{marker}",
                "",
                str(statement["mixed_scope_voice_working_reading_de"]),
                "",
            ])
    (OUT / "GDT579_MIXED_SCOPE_THIRTY_PAGE_EDITION.md").write_text(
        "\n".join(lines).rstrip() + "\n",
        encoding="utf-8",
    )

    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
