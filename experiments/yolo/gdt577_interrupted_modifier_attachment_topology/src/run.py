#!/usr/bin/env python3
"""Align every interrupted repeated modifier with an explicit local head."""

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
INPUTS = {
    "events": G576 / "gdt576_5122_learned_sigla_event_edition.tsv",
    "groups": G575 / "gdt575_96_exact_duplicate_phrase_groups.tsv",
    "scope_pairs": G575 / "gdt575_17_outer_inner_scope_pairs.tsv",
    "old_attachments": ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts/gdt407_5051_attachment_edition.tsv",
    "new_attachments": ROOT / "experiments/yolo/gdt515_second_random_four_page_full_admission/artifacts/gdt515_factorized_attachments.tsv",
    "old_clauses": ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts/gdt416_4576_imperative_clauses.tsv",
}
ACTIONS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
CONTROLS = {"OT", "OL", "DY"}
EXISTING_FOCUS_ROOTS = {"E", "EE", "AR"}
CANDIDATE_ROOTS = {"O", "D_ADDR"}
CONFLICT_EVENT = "G407-E1755"
CONFLICT_GROUP = "GDT575-D040"
STATUS = (
    "PASS_62_INTERRUPTED_GROUPS__125_SLOTS__75_EXISTING_ATTACHMENTS_REPLAYED__"
    "50_EXPLORATORY_HEAD_CANDIDATES__5_TOPOLOGIES__"
    "ONE_RENDERER_HISTORY_CONFLICT__ZERO_SLOT_COLLAPSE"
)

TOPOLOGY_SPECS = {
    "DISTINCT_ACTION_OCCURRENCES": {
        "short": "D",
        "voice": "Jeden Slot beim eigenen Kopf aussprechen; Grade dürfen lokal in beide Verbrahmen einrücken.",
        "trace": "X₁→A₁ … X₂→A₂",
    },
    "BRACKETING_SAME_HEAD": {
        "short": "B",
        "voice": "Beide Seiten des Kopfes sichtbar halten: X vor A und erneut X nach A.",
        "trace": "X → A → erneut X",
    },
    "SAME_HEAD_SAME_SIDE": {
        "short": "U",
        "voice": "Ein Kopfbündel bilden, die beiden geschriebenen Slots aber in Rohreihenfolge nennen.",
        "trace": "A → X → … → erneut X",
    },
    "ACTIVE_CONTEXT_HEAD": {
        "short": "C",
        "voice": "Den aktiven Kopf nennen und darunter die vollständige Slotfolge sprechen.",
        "trace": "Beim fortgeführten A: X → … → erneut/wieder X",
    },
    "ACTION_PLUS_SEQUENCE_HEAD": {
        "short": "Q",
        "voice": "Ersten Slot beim sichtbaren Kopf, zweiten beim geschriebenen Fortsetzungsträger aussprechen.",
        "trace": "X→A … OL→X",
    },
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty table {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def existing_attachment_map() -> dict[tuple[str, int], dict[str, str]]:
    result: dict[tuple[str, int], dict[str, str]] = {}
    for row in read_tsv(INPUTS["old_attachments"]):
        key = (row["global_running_event_id"], int(row["focus_atom_ordinal"]) - 1)
        result[key] = {
            "source": "GDT407_FIXED_FOCUS_ATTACHMENT",
            "head_event_id": row["selected_action_global_event_id"],
            "head_atom_position": str(int(row["selected_action_atom_ordinal"]) - 1),
            "head_root": row["action_core"],
            "source_geometry": row["attachment_geometry"],
            "selector_rule": row["selector_rule"],
            "duplicate_mode": row["duplicate_mode"],
            "duplicate_role": row["duplicate_role"],
        }
    for row in read_tsv(INPUTS["new_attachments"]):
        key = (row["event_id"], int(row["focus_atom_ordinal"]) - 1)
        result[key] = {
            "source": "GDT515_FIXED_FOCUS_ATTACHMENT",
            "head_event_id": row["selected_action_event_id"],
            "head_atom_position": str(int(row["selected_action_atom_ordinal"]) - 1),
            "head_root": row["action_core"],
            "source_geometry": row["attachment_geometry"],
            "selector_rule": row["selector_rule"],
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


def placement(event_id: str, slot_position: int, head_event_id: str, head_position: int, head_kind: str) -> str:
    if head_kind == "SEQUENCE":
        return "SEQUENCE_CARRY"
    if head_event_id != event_id:
        return "ACTIVE_CONTEXT"
    if head_position < slot_position:
        return "POST_HEAD"
    if head_position > slot_position:
        return "PRE_HEAD"
    raise RuntimeError(f"Head and modifier occupy the same atom at {event_id}:{slot_position}")


def exploratory_assignment(
    event: dict[str, str], slot_position: int, active: tuple[str, int, str] | None
) -> dict[str, str]:
    tokens = event["final_context_recipe"].split("+")
    left_controls = [position for position, token in enumerate(tokens) if token in CONTROLS and position < slot_position]
    right_controls = [position for position, token in enumerate(tokens) if token in CONTROLS and position > slot_position]
    left_boundary = max(left_controls) if left_controls else -1
    right_boundary = min(right_controls) if right_controls else len(tokens)
    local_actions = [
        position
        for position, token in enumerate(tokens)
        if token in ACTIONS and left_boundary < position < right_boundary
    ]
    if local_actions:
        head_position = min(
            local_actions,
            key=lambda position: (
                abs(position - slot_position),
                0 if position < slot_position else 1,
                position,
            ),
        )
        return {
            "source": "EXPLORATORY_NEAREST_VISIBLE_ACTION",
            "head_event_id": event["event_id"],
            "head_atom_position": str(head_position),
            "head_root": tokens[head_position],
            "source_geometry": "SAME_CARRIER_DISTANCE_MINIMUM__LEFT_TIE",
            "selector_rule": "VISIBLE_ACTION_INSIDE_OT_OL_DY_INTERVAL",
            "duplicate_mode": "ANALYTICAL_REPEAT_SLOT",
            "duplicate_role": "CANDIDATE_LOCAL_HEAD",
            "head_kind": "ACTION",
        }
    if left_boundary >= 0:
        return {
            "source": "EXPLORATORY_LEFT_SEQUENCE_CARRIER",
            "head_event_id": event["event_id"],
            "head_atom_position": str(left_boundary),
            "head_root": tokens[left_boundary],
            "source_geometry": "RIGHT_OF_SEQUENCE_CARRIER_WITHOUT_LOCAL_ACTION",
            "selector_rule": "LEFT_OT_OL_DY_INTERVAL_HEAD",
            "duplicate_mode": "ANALYTICAL_REPEAT_SLOT",
            "duplicate_role": "CANDIDATE_SEQUENCE_HEAD",
            "head_kind": "SEQUENCE",
        }
    if active is None:
        raise RuntimeError(f"No visible, sequence, or active head for {event['event_id']}:{slot_position}")
    head_event_id, head_position, head_root = active
    return {
        "source": "EXPLORATORY_ACTIVE_CONTEXT_HEAD",
        "head_event_id": head_event_id,
        "head_atom_position": str(head_position),
        "head_root": head_root,
        "source_geometry": "OWNER_ACTIVE_ACTION_CONTEXT",
        "selector_rule": "SAME_PAGE_AND_OWNER_ACTIVE_HEAD",
        "duplicate_mode": "ANALYTICAL_REPEAT_SLOT",
        "duplicate_role": "CANDIDATE_CONTEXT_HEAD",
        "head_kind": "ACTION",
    }


def topology(assignments: list[dict[str, object]], event_id: str) -> str:
    head_keys = {
        (row["head_kind"], row["head_event_id"], row["head_atom_position_zero_based"])
        for row in assignments
    }
    placements = {str(row["placement"]) for row in assignments}
    if "SEQUENCE_CARRY" in placements:
        return "ACTION_PLUS_SEQUENCE_HEAD"
    if len(head_keys) > 1:
        return "DISTINCT_ACTION_OCCURRENCES"
    if {"PRE_HEAD", "POST_HEAD"}.issubset(placements):
        return "BRACKETING_SAME_HEAD"
    if all(str(row["head_event_id"]) != event_id for row in assignments):
        return "ACTIVE_CONTEXT_HEAD"
    return "SAME_HEAD_SAME_SIDE"


def repeat_marker(root: str, occurrence: int) -> str:
    if occurrence == 1:
        return "FIRST_FULL"
    if occurrence >= 3:
        return "NOCHMALS"
    if root in {"D_ADDR", "AR"}:
        return "WIEDER"
    return "ERNEUT"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    events = read_tsv(INPUTS["events"])
    all_groups = read_tsv(INPUTS["groups"])
    scope_pairs = read_tsv(INPUTS["scope_pairs"])
    old_clauses = {row["global_running_event_id"]: row for row in read_tsv(INPUTS["old_clauses"])}
    if [len(events), len(all_groups), len(scope_pairs)] != [5122, 96, 17]:
        raise RuntimeError("Input count drift")
    groups = [row for row in all_groups if row["duplicate_topology"] == "SAME_ROOT_INTERRUPTED"]
    if len(groups) != 62:
        raise RuntimeError(f"Expected 62 interrupted same-root groups, found {len(groups)}")
    event_by_id = {row["event_id"]: row for row in events}
    fixed = existing_attachment_map()
    active_before = active_head_before(events)

    slot_rows: list[dict[str, object]] = []
    group_rows: list[dict[str, object]] = []
    assignments_by_group: dict[str, list[dict[str, object]]] = defaultdict(list)

    for group in groups:
        event = event_by_id[group["event_id"]]
        positions = [int(value) for value in group["underlying_atom_positions_zero_based"].split("+")]
        roots = group["underlying_atom_sequence"].split("+")
        if len(set(roots)) != 1 or len(positions) != len(roots):
            raise RuntimeError(f"Group identity drift at {group['duplicate_group_id']}")
        root = roots[0]
        tokens = event["final_context_recipe"].split("+")
        for occurrence, position in enumerate(positions, 1):
            if tokens[position] != root:
                raise RuntimeError(f"Position drift at {group['duplicate_group_id']}:{position}")
            if root in EXISTING_FOCUS_ROOTS:
                try:
                    assignment = dict(fixed[(event["event_id"], position)])
                except KeyError as exc:
                    raise RuntimeError(f"Missing fixed focus attachment at {event['event_id']}:{position}") from exc
                assignment["head_kind"] = "ACTION"
            elif root in CANDIDATE_ROOTS:
                assignment = exploratory_assignment(event, position, active_before[event["event_id"]])
            else:
                raise RuntimeError(f"Unexpected interrupted root {root}")
            head_position = int(assignment["head_atom_position"])
            place = placement(
                event["event_id"],
                position,
                assignment["head_event_id"],
                head_position,
                assignment["head_kind"],
            )
            row: dict[str, object] = {
                "slot_ordinal": len(slot_rows) + 1,
                "gdt575_duplicate_group_id": group["duplicate_group_id"],
                "event_id": event["event_id"],
                "statement_id": event["statement_id"],
                "physical_page": event["physical_page"],
                "register": event["register"],
                "surface": event["surface"],
                "final_context_recipe": event["final_context_recipe"],
                "repeat_root": root,
                "repeat_scope": group["scope"],
                "slot_occurrence_in_group": occurrence,
                "slot_atom_position_zero_based": position,
                "repeat_marker_candidate": repeat_marker(root, occurrence),
                "assignment_source": assignment["source"],
                "selector_rule": assignment["selector_rule"],
                "source_geometry": assignment["source_geometry"],
                "head_kind": assignment["head_kind"],
                "head_event_id": assignment["head_event_id"],
                "head_atom_position_zero_based": head_position,
                "head_root": assignment["head_root"],
                "head_identity": f"{assignment['head_kind']}:{assignment['head_event_id']}@{head_position}:{assignment['head_root']}",
                "placement": place,
                "duplicate_mode": assignment["duplicate_mode"],
                "duplicate_role": assignment["duplicate_role"],
                "renderer_history_conflict": "YES" if group["duplicate_group_id"] == CONFLICT_GROUP else "NO",
                "guard": "EVERY_WRITTEN_SLOT_RETAINED__CANDIDATE_HEAD_IS_WORKSHOP_VOICE_ONLY",
            }
            slot_rows.append(row)
            assignments_by_group[group["duplicate_group_id"]].append(row)

    for ordinal, group in enumerate(groups, 1):
        members = assignments_by_group[group["duplicate_group_id"]]
        event = event_by_id[group["event_id"]]
        kind = topology(members, event["event_id"])
        event_quarantine = event["event_id"] == CONFLICT_EVENT
        conflict = group["duplicate_group_id"] == CONFLICT_GROUP
        if conflict:
            renderer_route = "QUARANTINE_PRIOR_OUTER_INNER_VOICE_CONFLICT"
        elif event_quarantine:
            renderer_route = "EVENT_QUARANTINE_COMPANION__KEEP_CURRENT_CLAUSE"
        elif kind == "DISTINCT_ACTION_OCCURRENCES" and group["alignment_key"] in {"E", "EE"}:
            renderer_route = "INLINE_GRADE_AT_EACH_DISTINCT_HEAD"
        else:
            renderer_route = "EXPLICIT_ORDERED_HEAD_TRACE__NO_TWICE_COMPRESSION"
        group_rows.append({
            "group_ordinal": ordinal,
            "gdt575_duplicate_group_id": group["duplicate_group_id"],
            "event_id": event["event_id"],
            "statement_id": event["statement_id"],
            "physical_page": event["physical_page"],
            "register": event["register"],
            "surface": event["surface"],
            "final_context_recipe": event["final_context_recipe"],
            "repeat_root": members[0]["repeat_root"],
            "repeat_scope": members[0]["repeat_scope"],
            "slot_count": len(members),
            "slot_positions_zero_based": "+".join(str(row["slot_atom_position_zero_based"]) for row in members),
            "intervening_atom_sequences": group["intervening_atom_sequences"],
            "attachment_topology": kind,
            "topology_short": TOPOLOGY_SPECS[kind]["short"],
            "head_identity_sequence": " | ".join(str(row["head_identity"]) for row in members),
            "placement_sequence": "+".join(str(row["placement"]) for row in members),
            "assignment_source_sequence": "+".join(str(row["assignment_source"]) for row in members),
            "renderer_route": renderer_route,
            "renderer_ready": "NO" if event_quarantine else "YES",
            "renderer_history_conflict": "YES" if conflict else "NO",
            "current_clause_de": event["learned_sigla_working_clause_de"],
            "recommended_voice_pattern": TOPOLOGY_SPECS[kind]["voice"],
            "guard": "GROUP_TOPOLOGY_ONLY__NO_SLOT_OR_SCOPE_COLLAPSE",
        })

    topology_counts = Counter(row["attachment_topology"] for row in group_rows)
    topology_rows = []
    for ordinal, (kind, spec) in enumerate(TOPOLOGY_SPECS.items(), 1):
        members = [row for row in group_rows if row["attachment_topology"] == kind]
        topology_rows.append({
            "topology_card_ordinal": ordinal,
            "topology_card_id": f"GDT577-T{ordinal:02d}",
            "attachment_topology": kind,
            "topology_short": spec["short"],
            "group_count": len(members),
            "event_count": len({row["event_id"] for row in members}),
            "slot_count": sum(int(row["slot_count"]) for row in members),
            "abstract_trace": spec["trace"],
            "recommended_voice_pattern": spec["voice"],
            "guard": "SMALL_TOPOLOGY_CARD__NOT_A_NEW_ROOT_MEANING",
        })

    groups_by_event: dict[str, list[dict[str, object]]] = defaultdict(list)
    slots_by_event: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in group_rows:
        groups_by_event[str(row["event_id"])].append(row)
    for row in slot_rows:
        slots_by_event[str(row["event_id"])].append(row)
    event_rows = []
    for ordinal, event_id in enumerate(sorted(groups_by_event, key=lambda value: int(value.split("E")[-1])), 1):
        event = event_by_id[event_id]
        event_groups = groups_by_event[event_id]
        event_slots = sorted(slots_by_event[event_id], key=lambda row: (int(row["slot_atom_position_zero_based"]), str(row["repeat_root"])))
        event_rows.append({
            "event_profile_ordinal": ordinal,
            "event_id": event_id,
            "statement_id": event["statement_id"],
            "physical_page": event["physical_page"],
            "register": event["register"],
            "surface": event["surface"],
            "final_context_recipe": event["final_context_recipe"],
            "duplicate_group_ids": "|".join(str(row["gdt575_duplicate_group_id"]) for row in event_groups),
            "repeat_roots": "+".join(str(row["repeat_root"]) for row in event_groups),
            "attachment_topologies": "+".join(str(row["attachment_topology"]) for row in event_groups),
            "ordered_slot_head_trace": " | ".join(
                f"p{row['slot_atom_position_zero_based']}:{row['repeat_root']}→{row['head_identity']}[{row['placement']}]"
                for row in event_slots
            ),
            "overlapping_group_count": len(event_groups),
            "renderer_ready": "NO" if event_id == CONFLICT_EVENT else "YES",
            "current_clause_de": event["learned_sigla_working_clause_de"],
            "next_voice_instruction": (
                "KEEP_CURRENT_CLAUSE__AUDIT_PRIOR_SCOPE_VOICE"
                if event_id == CONFLICT_EVENT
                else "RENDER_WHOLE_EVENT_ONCE_FROM_ORDERED_SLOT_HEAD_TRACE"
            ),
            "guard": "EVENT_LEVEL_OVERLAP_CONTROL__NEVER_RENDER_GROUPS_INDEPENDENTLY",
        })

    old_conflict = old_clauses[CONFLICT_EVENT]
    conflict_group = next(row for row in group_rows if row["gdt575_duplicate_group_id"] == CONFLICT_GROUP)
    conflict_rows = [{
        "conflict_id": "GDT577-CF01",
        "event_id": CONFLICT_EVENT,
        "gdt575_duplicate_group_id": CONFLICT_GROUP,
        "root": "AR",
        "recipe": event_by_id[CONFLICT_EVENT]["final_context_recipe"],
        "gdt416_prior_clause_de": old_conflict["imperative_clause_de"],
        "gdt576_current_clause_de": event_by_id[CONFLICT_EVENT]["learned_sigla_working_clause_de"],
        "fixed_head_identity_sequence": conflict_group["head_identity_sequence"],
        "fixed_duplicate_modes": "+".join(str(row["duplicate_mode"]) for row in assignments_by_group[CONFLICT_GROUP]),
        "conflict_description": "GDT416 generated outer/inner from any repeated relation; the fixed focus rows are SINGLE/SINGLE and GDT565 later emitted plain ordered slots.",
        "decision": "QUARANTINE_EVENT__NEITHER_COMPRESS_NOR_PROMOTE_TO_SCOPE_PAIR",
        "guard": "RENDERER_HISTORY_CONFLICT__ROOT_AND_TWO_WRITTEN_AR_SLOTS_UNCHANGED",
    }]

    write_tsv(OUT / "gdt577_125_slot_head_assignments.tsv", slot_rows)
    write_tsv(OUT / "gdt577_62_interrupted_group_topology.tsv", group_rows)
    write_tsv(OUT / "gdt577_5_attachment_topology_cards.tsv", topology_rows)
    write_tsv(OUT / "gdt577_59_event_sequence_profiles.tsv", event_rows)
    write_tsv(OUT / "gdt577_1_renderer_history_conflict.tsv", conflict_rows)

    source_counts = Counter(row["assignment_source"] for row in slot_rows)
    placement_counts = Counter(row["placement"] for row in slot_rows if str(row["assignment_source"]).startswith("EXPLORATORY"))
    root_counts = Counter(row["repeat_root"] for row in group_rows)
    result = {
        "experiment_id": "GDT577",
        "status": STATUS,
        "input_sha256": {key: sha256(path) for key, path in INPUTS.items()},
        "event_count": len(event_rows),
        "group_count": len(group_rows),
        "slot_count": len(slot_rows),
        "existing_fixed_assignment_count": sum(count for key, count in source_counts.items() if "FIXED" in key),
        "exploratory_candidate_assignment_count": sum(count for key, count in source_counts.items() if key.startswith("EXPLORATORY")),
        "assignment_source_counts": dict(sorted(source_counts.items())),
        "exploratory_placement_counts": dict(sorted(placement_counts.items())),
        "group_root_counts": dict(sorted(root_counts.items())),
        "topology_counts": dict(sorted(topology_counts.items())),
        "renderer_ready_group_count": sum(row["renderer_ready"] == "YES" for row in group_rows),
        "renderer_quarantined_group_count": sum(row["renderer_ready"] == "NO" for row in group_rows),
        "renderer_ready_event_count": sum(row["renderer_ready"] == "YES" for row in event_rows),
        "renderer_quarantined_event_count": sum(row["renderer_ready"] == "NO" for row in event_rows),
        "renderer_history_conflict_count": len(conflict_rows),
        "scope_pair_overlap_count": len(
            {row["event_id"] for row in group_rows} & {row["event_id"] for row in scope_pairs}
        ),
        "no_new_page": True,
        "no_root_change": True,
        "no_slot_collapse": True,
        "historical_voice_analogies": [
            {
                "label": "Hamburger Rezeptbestand Ha1-I, ca. 1463",
                "url": "https://diglib.hab.de/edoc/ed000270/texts/tei-transcription.html",
                "use": "darnach for sequence; wider for return; auch for an analogous added treatment",
            },
            {
                "label": "S 392, ca. 1500",
                "url": "https://d-nb.info/138537974X/34",
                "use": "anderwärt/noch einmal and desgleichen as repeat or analogous-procedure voices",
            },
            {
                "label": "Cennini, Libro dell'arte, chapter 145",
                "url": "https://it.wikisource.org/wiki/Il_libro_dell%27arte/Capitolo_CXLV",
                "use": "local gradi assigned to their places with returns to earlier stages",
            },
        ],
    }
    (OUT / "gdt577_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# GDT577 attachment topology atlas",
        "",
        f"Status: `{STATUS}`",
        "",
        "## Five reusable topologies",
        "",
        "| card | topology | groups | slots | voice |",
        "|---|---|---:|---:|---|",
    ]
    for row in topology_rows:
        lines.append(
            f"| {row['topology_short']} | `{row['attachment_topology']}` | {row['group_count']} | "
            f"{row['slot_count']} | {row['recommended_voice_pattern']} |"
        )
    lines.extend([
        "",
        "## All 62 groups",
        "",
        "| group | event | root | slots | topology | head trace | renderer |",
        "|---|---|---|---|---|---|---|",
    ])
    for row in group_rows:
        lines.append(
            f"| {row['gdt575_duplicate_group_id']} | {row['event_id']} | `{row['repeat_root']}` | "
            f"{row['slot_positions_zero_based']} | {row['topology_short']} | "
            f"{str(row['head_identity_sequence']).replace('|', '<br>')} | {row['renderer_route']} |"
        )
    lines.extend([
        "",
        "## Renderer-history conflict",
        "",
        "`G407-E1755` remains unchanged. GDT416 assigned the two AR occurrences",
        "generic outer/inner labels merely because the relation repeated; GDT565 later",
        "rendered the written order without those labels. Both fixed AR focus rows are",
        "`SINGLE/SINGLE`. The atlas therefore records the common inherited OK head but",
        "does not choose between a repeat voice and a scope voice.",
        "",
        "The atlas is an editorial attachment model. It changes no root, recipe, slot,",
        "surface, scope, event, statement, page, language claim or object identity.",
    ])
    (OUT / "GDT577_ATTACHMENT_TOPOLOGY_ATLAS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
