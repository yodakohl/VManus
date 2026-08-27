#!/usr/bin/env python3
"""Render the GDT577 attachment atlas as an event-keyed complete voice edition."""

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
G576 = ROOT / "experiments/yolo/gdt576_learned_local_sigla_voice/artifacts"
G577 = ROOT / "experiments/yolo/gdt577_interrupted_modifier_attachment_topology/artifacts"
G575 = ROOT / "experiments/yolo/gdt575_repeated_relation_modifier_scope_atlas/artifacts"
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
    "action_cells": ROOT / "experiments/yolo/gdt568_twenty_owner_action_voice_frames/artifacts/gdt568_45_register_action_cells.tsv",
}
STATUS = (
    "PASS_5_ATTACHMENT_CLASSES__3_PROSE_FRAMES__20_HEAD_VOICES__58_EVENT_CARDS__60_GROUPS__"
    "121_REPEAT_SLOTS__173_ORDERED_MODIFIER_FRAGMENTS__61_PARTICLES__"
    "5122_EXACT_ROUNDTRIPS__ONE_CONFLICT_UNCHANGED"
)

ACTIONS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
ARGUMENTS = {"Y", "AIIN", "AIN", "OR"}
STATE_CONTROLS = {"OT", "OL", "DY"}
CONFLICT_EVENT = "G407-E1755"
CONFLICT_STATEMENT = "G407-S149"
CONFLICT_PAGE = "f75r"

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
        "AL": "zur Zielspalte", "AR": "von der Ausgangszeile",
        "L": "über die Eintragsverbindung", "AIR": "entlang der Lesebahn",
    },
    "HERBAL": {
        "AL": "zur Zielstelle", "AR": "vom Ausgangsmaterial",
        "L": "über die Verbindung im Pflanzenartikel", "AIR": "entlang der Verarbeitungsbahn",
    },
    "BIOLOGICAL": {
        "AL": "zur Zielstation", "AR": "von der Ausgangsstation",
        "L": "über die sichtbare Verbindung", "AIR": "entlang der Stationsbahn",
    },
    "CELESTIAL": {
        "AL": "zur Zielposition", "AR": "von der Ausgangsposition",
        "L": "über die Ringverbindung", "AIR": "entlang der Ringbahn",
    },
    "PHARMA": {
        "AL": "zum Zielgefäß", "AR": "vom Ausgangsgefäß",
        "L": "über die Gefäßverbindung", "AIR": "entlang der Transferbahn",
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

PROSE_FRAMES = {
    "ACTION_HEAD": "beim {head}: {display}",
    "ACTIVE_CONTEXT_HEAD": "beim fortgeführten {head}: {display}",
    "SEQUENCE_HEAD": "bei der Fortsetzung: {display}",
}

TOPOLOGY_FRAME_OPTIONS = {
    "DISTINCT_ACTION_OCCURRENCES": "ACTION_HEAD",
    "BRACKETING_SAME_HEAD": "ACTION_HEAD",
    "SAME_HEAD_SAME_SIDE": "ACTION_HEAD",
    "ACTIVE_CONTEXT_HEAD": "ACTIVE_CONTEXT_HEAD",
    "ACTION_PLUS_SEQUENCE_HEAD": "ACTION_HEAD|SEQUENCE_HEAD",
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


def text_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def action_cell_maps(rows: list[dict[str, str]]) -> tuple[dict[tuple[str, str], dict[str, str]], list[dict[str, object]]]:
    cells = {(row["register"], row["action_root"]): row for row in rows}
    if len(cells) != 45:
        raise RuntimeError("GDT568 action-cell drift")
    card_rows: list[dict[str, object]] = []
    by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_card[row["action_voice_card_id"]].append(row)
    for ordinal, card_id in enumerate(sorted(by_card, key=lambda value: int(value.split("A")[-1])), 1):
        members = by_card[card_id]
        card_rows.append({
            "head_voice_ordinal": ordinal,
            "gdt568_action_voice_card_id": card_id,
            "action_root": members[0]["action_root"],
            "register_scope": "|".join(row["register"] for row in members),
            "head_nominal_de": ACTION_NOMINAL_BY_CARD[card_id],
            "source_owner_expansions": "|".join(row["gdt415_owner_local_expansion_de"] for row in members),
            "guard": "NOMINAL_HEAD_VOICE_ONLY__ACTION_ROOT_UNCHANGED",
        })
    if len(card_rows) != 20:
        raise RuntimeError("Expected twenty GDT568 action voice cards")
    return cells, card_rows


def base_fragment(register: str, atom: str) -> str:
    if atom in BASE_FRAGMENTS:
        return BASE_FRAGMENTS[atom]
    if atom in RELATION_FRAGMENTS[register]:
        return RELATION_FRAGMENTS[register][atom]
    raise RuntimeError(f"No modifier voice for {register}:{atom}")


def repeat_particle(
    slot: dict[str, str], group_slots: list[dict[str, str]], topology_name: str
) -> str:
    occurrence = int(slot["slot_occurrence_in_group"])
    if occurrence == 1:
        return ""
    if occurrence >= 3:
        return "nochmals"
    if slot["repeat_root"] in {"D_ADDR", "AR"}:
        return "wieder"
    if topology_name == "DISTINCT_ACTION_OCCURRENCES":
        first = min(group_slots, key=lambda row: int(row["slot_occurrence_in_group"]))
        if first["head_identity"] != slot["head_identity"]:
            return "ebenfalls"
    return "erneut"


def selected_head_nominal(
    slot: dict[str, str],
    register: str,
    action_cells: dict[tuple[str, str], dict[str, str]],
    event_by_id: dict[str, dict[str, str]],
) -> str:
    if slot["head_kind"] == "SEQUENCE":
        return "Fortsetzen"
    cell = action_cells[(register, slot["head_root"])]
    nominal = ACTION_NOMINAL_BY_CARD[cell["action_voice_card_id"]]
    head_event = event_by_id[slot["head_event_id"]]
    positions = [
        position
        for position, atom in enumerate(head_event["final_context_recipe"].split("+"))
        if atom == slot["head_root"]
    ]
    if len(positions) > 1 and int(slot["head_atom_position_zero_based"]) in positions:
        ordinal = positions.index(int(slot["head_atom_position_zero_based"])) + 1
        labels = {1: "ersten", 2: "zweiten", 3: "dritten", 4: "vierten"}
        nominal = f"{labels.get(ordinal, str(ordinal) + '.')} {nominal}"
    return nominal


def render_bound_fragment(
    slot: dict[str, str],
    group: dict[str, str],
    group_slots: list[dict[str, str]],
    action_cells: dict[tuple[str, str], dict[str, str]],
    event_by_id: dict[str, dict[str, str]],
    register: str,
    base: str,
) -> tuple[str, str, str]:
    particle = repeat_particle(slot, group_slots, group["attachment_topology"])
    display = f"{particle} {base}" if particle else base
    head = selected_head_nominal(slot, register, action_cells, event_by_id)
    topology_name = group["attachment_topology"]
    if topology_name == "DISTINCT_ACTION_OCCURRENCES":
        rendered = PROSE_FRAMES["ACTION_HEAD"].format(head=head, display=display)
    elif topology_name in {"BRACKETING_SAME_HEAD", "SAME_HEAD_SAME_SIDE"}:
        # PRE/POST is source geometry, not a licensed process chronology.  It
        # remains explicit in the assignment table while the prose voice names
        # only the shared head and preserves the written slot order.
        rendered = PROSE_FRAMES["ACTION_HEAD"].format(head=head, display=display)
    elif topology_name == "ACTIVE_CONTEXT_HEAD":
        rendered = PROSE_FRAMES["ACTIVE_CONTEXT_HEAD"].format(head=head, display=display)
    elif topology_name == "ACTION_PLUS_SEQUENCE_HEAD":
        if slot["head_kind"] == "SEQUENCE":
            rendered = PROSE_FRAMES["SEQUENCE_HEAD"].format(display=display)
        else:
            rendered = PROSE_FRAMES["ACTION_HEAD"].format(head=head, display=display)
    else:
        raise RuntimeError(f"Unknown topology {topology_name}")
    return rendered, particle, head


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    source_events = read_tsv(INPUTS["events"])
    source_statements = read_tsv(INPUTS["statements"])
    source_pages = read_tsv(INPUTS["pages"])
    sigla = read_tsv(INPUTS["sigla"])
    slots = read_tsv(INPUTS["slots"])
    groups = read_tsv(INPUTS["groups"])
    profiles = read_tsv(INPUTS["profiles"])
    scope_pairs = read_tsv(INPUTS["scope_pairs"])
    all_duplicate_groups = read_tsv(INPUTS["all_duplicate_groups"])
    action_cells_source = read_tsv(INPUTS["action_cells"])
    if [len(source_events), len(source_statements), len(source_pages), len(sigla), len(slots), len(groups), len(profiles)] != [5122, 793, 30, 773, 125, 62, 59]:
        raise RuntimeError("Input count drift")

    event_by_id = {row["event_id"]: row for row in source_events}
    action_cells, head_card_rows = action_cell_maps(action_cells_source)
    profile_by_event = {row["event_id"]: row for row in profiles}
    group_by_id = {row["gdt575_duplicate_group_id"]: row for row in groups}
    slots_by_event: dict[str, list[dict[str, str]]] = defaultdict(list)
    slots_by_group: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in slots:
        slots_by_event[row["event_id"]].append(row)
        slots_by_group[row["gdt575_duplicate_group_id"]].append(row)
    sigla_by_key = {(row["event_id"], int(row["atom_position_zero_based"])): row for row in sigla}
    ready_events = {row["event_id"] for row in profiles if row["renderer_ready"] == "YES"}
    if len(ready_events) != 58 or CONFLICT_EVENT in ready_events:
        raise RuntimeError("Renderer-ready event set drift")

    template_rows: list[dict[str, object]] = []
    for ordinal, topology_name in enumerate(TOPOLOGY_FRAME_OPTIONS, 1):
        ready_groups = [
            row for row in groups
            if row["renderer_ready"] == "YES" and row["attachment_topology"] == topology_name
        ]
        template_rows.append({
            "template_ordinal": ordinal,
            "template_id": f"GDT578-T{ordinal:02d}",
            "attachment_topology": topology_name,
            "prose_frame_ids": TOPOLOGY_FRAME_OPTIONS[topology_name],
            "group_count": len(ready_groups),
            "event_count": len({row["event_id"] for row in ready_groups}),
            "repeat_slot_count": sum(int(row["slot_count"]) for row in ready_groups),
            "guard": "ATTACHMENT_CLASS_TO_PROSE_FRAME_ONLY__PRE_POST_RETAINED_IN_SLOT_TABLE",
        })
    prose_frame_rows = [
        {
            "prose_frame_ordinal": ordinal,
            "prose_frame_id": frame_id,
            "prose_frame_de": frame,
            "guard": "HEAD_BINDING_VOICE_ONLY__NO_PROCESS_CHRONOLOGY_FROM_PRE_POST",
        }
        for ordinal, (frame_id, frame) in enumerate(PROSE_FRAMES.items(), 1)
    ]

    fragment_rows: list[dict[str, object]] = []
    voiced_slot_rows: list[dict[str, object]] = []
    particle_rows: list[dict[str, object]] = []
    respun_sigla_rows: list[dict[str, object]] = []
    event_card_rows: list[dict[str, object]] = []
    event_rows: list[dict[str, object]] = []
    target_by_event: dict[str, str] = {}
    changed_event_ids: set[str] = set()

    for source in source_events:
        event_id = source["event_id"]
        source_clause = source["learned_sigla_working_clause_de"]
        if event_id not in ready_events:
            target_by_event[event_id] = source_clause
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
                "gdt576_learned_sigla_clause_de": source_clause,
                "attachment_voice_working_clause_de": source_clause,
                "gdt576_source_roundtrip_de": source_clause,
                "attachment_voice_status": "QUARANTINED_RENDERER_HISTORY_CONFLICT" if event_id == CONFLICT_EVENT else "UNCHANGED_NON_TARGET",
                "repeat_group_ids": "|".join(row["gdt575_duplicate_group_id"] for row in groups if row["event_id"] == event_id) or "NONE",
                "repeat_slot_count": len(slots_by_event.get(event_id, [])),
                "modifier_fragment_count": 0,
                "repeat_particle_count": 0,
                "guard": "EVENT_ID_KEYED_EDITION__GDT576_SOURCE_ROUNDTRIP_EXACT",
            })
            continue

        changed_event_ids.add(event_id)
        atoms = source["final_context_recipe"].split("+")
        action_block = source_clause.removesuffix(".").split("; ", 1)[0]
        event_slots = {int(row["slot_atom_position_zero_based"]): row for row in slots_by_event[event_id]}
        group_ids = profile_by_event[event_id]["duplicate_group_ids"].split("|")
        local_fragments: list[dict[str, object]] = []
        local_particles: Counter[str] = Counter()
        for position, atom in enumerate(atoms):
            if atom in ACTIONS or atom in ARGUMENTS or atom in STATE_CONTROLS:
                continue
            base = base_fragment(source["register"], atom)
            slot = event_slots.get(position)
            if slot:
                group = group_by_id[slot["gdt575_duplicate_group_id"]]
                rendered, particle, head = render_bound_fragment(
                    slot,
                    group,
                    slots_by_group[slot["gdt575_duplicate_group_id"]],
                    action_cells,
                    event_by_id,
                    source["register"],
                    base,
                )
                binding_status = "GDT577_HEAD_BOUND_REPEAT_SLOT"
                topology_name = group["attachment_topology"]
                group_id = group["gdt575_duplicate_group_id"]
                if particle:
                    local_particles[particle] += 1
            else:
                rendered = base
                particle = ""
                head = "NONE"
                binding_status = "UNBOUND_MODIFIER_IN_RAW_ORDER"
                topology_name = "NOT_APPLICABLE"
                group_id = "NONE"
            local_fragments.append({
                "event_id": event_id,
                "atom_position_zero_based": position,
                "atom": atom,
                "base_fragment_de": base,
                "rendered_fragment_de": rendered,
                "repeat_particle_de": particle or "NONE",
                "head_nominal_de": head,
                "binding_status": binding_status,
                "attachment_topology": topology_name,
                "gdt575_duplicate_group_id": group_id,
            })
        if not local_fragments:
            raise RuntimeError(f"Target event has no modifier trail: {event_id}")

        segments = [action_block] + [str(row["rendered_fragment_de"]) for row in local_fragments]
        if "DY" in atoms:
            segments.append("schließe den Schritt")
        target_clause = "; ".join(segments) + "."
        cursor = len(action_block)
        for local_ordinal, fragment in enumerate(local_fragments, 1):
            cursor += 2
            start = cursor
            rendered = str(fragment["rendered_fragment_de"])
            end = start + len(rendered)
            base = str(fragment["base_fragment_de"])
            base_offset = rendered.find(base)
            if base_offset < 0 or rendered.find(base, base_offset + 1) >= 0:
                raise RuntimeError(f"Root fragment span ambiguity at {event_id}:{fragment['atom_position_zero_based']}")
            base_start = start + base_offset
            base_end = base_start + len(base)
            fragment_row = {
                "fragment_ordinal": len(fragment_rows) + 1,
                "event_id": event_id,
                "statement_id": source["statement_id"],
                "physical_page": source["physical_page"],
                "register": source["register"],
                "surface": source["surface"],
                "final_context_recipe": source["final_context_recipe"],
                "fragment_ordinal_in_event": local_ordinal,
                "atom_position_zero_based": fragment["atom_position_zero_based"],
                "atom": fragment["atom"],
                "base_fragment_de": base,
                "rendered_fragment_de": rendered,
                "target_fragment_start": start,
                "target_fragment_end": end,
                "root_expression_start": base_start,
                "root_expression_end": base_end,
                "repeat_particle_de": fragment["repeat_particle_de"],
                "head_nominal_de": fragment["head_nominal_de"],
                "binding_status": fragment["binding_status"],
                "attachment_topology": fragment["attachment_topology"],
                "gdt575_duplicate_group_id": fragment["gdt575_duplicate_group_id"],
                "guard": "RAW_ATOM_ORDER__ROOT_EXPRESSION_SPAN_EXCLUDES_REPEAT_PARTICLE",
            }
            fragment_rows.append(fragment_row)
            slot = event_slots.get(int(fragment["atom_position_zero_based"]))
            if slot:
                particle = "" if fragment["repeat_particle_de"] == "NONE" else str(fragment["repeat_particle_de"])
                particle_start = rendered.find(particle) + start if particle else -1
                particle_end = particle_start + len(particle) if particle else -1
                voiced_slot_rows.append({
                    "voice_slot_ordinal": len(voiced_slot_rows) + 1,
                    "gdt577_slot_ordinal": slot["slot_ordinal"],
                    "gdt575_duplicate_group_id": slot["gdt575_duplicate_group_id"],
                    "event_id": event_id,
                    "statement_id": source["statement_id"],
                    "physical_page": source["physical_page"],
                    "register": source["register"],
                    "surface": source["surface"],
                    "final_context_recipe": source["final_context_recipe"],
                    "repeat_root": slot["repeat_root"],
                    "slot_occurrence_in_group": slot["slot_occurrence_in_group"],
                    "slot_atom_position_zero_based": slot["slot_atom_position_zero_based"],
                    "attachment_topology": fragment["attachment_topology"],
                    "head_identity": slot["head_identity"],
                    "placement": slot["placement"],
                    "head_nominal_de": fragment["head_nominal_de"],
                    "repeat_particle_de": particle or "NONE",
                    "rendered_fragment_de": rendered,
                    "root_expression_de": base,
                    "root_expression_start": base_start,
                    "root_expression_end": base_end,
                    "particle_start": particle_start,
                    "particle_end": particle_end,
                    "guard": "ONE_ROOT_EXPRESSION_PER_WRITTEN_REPEAT_SLOT__PARTICLE_SEPARATE",
                })
                if particle:
                    particle_rows.append({
                        "particle_ordinal": len(particle_rows) + 1,
                        "event_id": event_id,
                        "gdt575_duplicate_group_id": slot["gdt575_duplicate_group_id"],
                        "repeat_root": slot["repeat_root"],
                        "slot_occurrence_in_group": slot["slot_occurrence_in_group"],
                        "slot_atom_position_zero_based": slot["slot_atom_position_zero_based"],
                        "particle_de": particle,
                        "particle_start": particle_start,
                        "particle_end": particle_end,
                        "root_expression_start": base_start,
                        "root_expression_end": base_end,
                        "guard": "EDITORIAL_REPEAT_PARTICLE__NOT_PART_OF_ROOT_EXPRESSION",
                    })
            siglum = sigla_by_key.get((event_id, int(fragment["atom_position_zero_based"])))
            if siglum:
                respun_sigla_rows.append({
                    "respun_sigla_ordinal": len(respun_sigla_rows) + 1,
                    "gdt576_assignment_ordinal": siglum["assignment_ordinal"],
                    "event_id": event_id,
                    "atom_position_zero_based": fragment["atom_position_zero_based"],
                    "atom": fragment["atom"],
                    "sigla_card_id": siglum["sigla_card_id"],
                    "old_target_fragment_de": siglum["target_fragment_de"],
                    "new_target_fragment_de": base,
                    "old_target_start": siglum["target_start"],
                    "old_target_end": siglum["target_end"],
                    "new_target_start": base_start,
                    "new_target_end": base_end,
                    "guard": "SIGLA_ATOM_POSITION_RETAINED__NEW_EVENT_SPAN_RECOMPUTED",
                })
            cursor = end
        if "DY" in atoms:
            cursor += 2 + len("schließe den Schritt")
        if cursor + 1 != len(target_clause):
            raise RuntimeError(f"Target cursor drift at {event_id}")

        roundtrip = source_clause
        target_by_event[event_id] = target_clause
        event_card_rows.append({
            "event_card_ordinal": len(event_card_rows) + 1,
            "edition_event_ordinal": source["edition_event_ordinal"],
            "event_id": event_id,
            "statement_id": source["statement_id"],
            "physical_page": source["physical_page"],
            "register": source["register"],
            "surface": source["surface"],
            "final_context_recipe": source["final_context_recipe"],
            "state_status": source["state_status"],
            "state_marker_sequence": source["state_marker_sequence"],
            "gdt576_source_clause_de": source_clause,
            "gdt576_source_clause_sha256": text_sha256(source_clause),
            "retained_action_block_de": action_block,
            "target_clause_de": target_clause,
            "target_clause_sha256": text_sha256(target_clause),
            "repeat_group_ids": "|".join(group_ids),
            "repeat_group_count": len(group_ids),
            "repeat_slot_count": len(event_slots),
            "modifier_fragment_count": len(local_fragments),
            "bound_fragment_count": sum(row["binding_status"] == "GDT577_HEAD_BOUND_REPEAT_SLOT" for row in local_fragments),
            "unbound_fragment_count": sum(row["binding_status"] == "UNBOUND_MODIFIER_IN_RAW_ORDER" for row in local_fragments),
            "repeat_particle_count": sum(local_particles.values()),
            "repeat_particle_profile": "|".join(f"{key}:{value}" for key, value in sorted(local_particles.items())) or "NONE",
            "inverse_key": event_id,
            "guard": "EXPLICIT_EVENT_CARD__NEVER_LOOK_UP_BY_SOURCE_TEXT",
        })
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
            "gdt576_learned_sigla_clause_de": source_clause,
            "attachment_voice_working_clause_de": target_clause,
            "gdt576_source_roundtrip_de": roundtrip,
            "attachment_voice_status": "CHANGED_EVENT_KEYED_CARD",
            "repeat_group_ids": "|".join(group_ids),
            "repeat_slot_count": len(event_slots),
            "modifier_fragment_count": len(local_fragments),
            "repeat_particle_count": sum(local_particles.values()),
            "guard": "EVENT_ID_KEYED_EDITION__GDT576_SOURCE_ROUNDTRIP_EXACT",
        })

    if len(event_rows) != 5122 or len(event_card_rows) != 58:
        raise RuntimeError("Event output drift")
    event_output_by_id = {row["event_id"]: row for row in event_rows}

    statement_rows: list[dict[str, object]] = []
    for source in source_statements:
        ids = source["event_ids"].split("|")
        target = " ".join(target_by_event[event_id] for event_id in ids)
        changed_members = [event_id for event_id in ids if event_id in changed_event_ids]
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
            "gdt576_learned_sigla_reading_de": source["learned_sigla_working_reading_de"],
            "attachment_voice_working_reading_de": target,
            "gdt576_source_roundtrip_de": source["learned_sigla_working_reading_de"],
            "attachment_statement_changed": "YES" if changed_members else "NO",
            "changed_event_count": len(changed_members),
            "changed_event_ids": "|".join(changed_members) or "NONE",
            "end_mode": source["end_mode"],
            "guard": "STATEMENT_REBUILT_ONLY_FROM_FIXED_EVENT_IDS__SOURCE_ROUNDTRIP_EXACT",
        })

    changed_statements = {row["statement_id"] for row in statement_rows if row["attachment_statement_changed"] == "YES"}
    page_rows: list[dict[str, object]] = []
    for source in source_pages:
        page = source["physical_page"]
        page_events = [row for row in event_rows if row["physical_page"] == page]
        page_statements = [row for row in statement_rows if row["physical_page"] == page]
        page_rows.append({
            "page_ordinal": source["page_ordinal"],
            "physical_page": page,
            "registers": source["registers"],
            "event_count": source["event_count"],
            "statement_count": source["statement_count"],
            "state_event_count": source["state_event_count"],
            "nonstate_event_count": source["nonstate_event_count"],
            "changed_event_count": sum(row["attachment_voice_status"] == "CHANGED_EVENT_KEYED_CARD" for row in page_events),
            "changed_statement_count": sum(row["attachment_statement_changed"] == "YES" for row in page_statements),
            "page_voice_changed": "YES" if any(row["attachment_voice_status"] == "CHANGED_EVENT_KEYED_CARD" for row in page_events) else "NO",
            "page_status": source["page_status"],
            "guard": "SOURCE_PAGE_ORDER_AND_MEMBERSHIP_UNCHANGED",
        })

    write_tsv(OUT / "gdt578_20_action_head_voice_cards.tsv", head_card_rows)
    write_tsv(OUT / "gdt578_5_attachment_voice_templates.tsv", template_rows)
    write_tsv(OUT / "gdt578_3_prose_voice_frames.tsv", prose_frame_rows)
    write_tsv(OUT / "gdt578_173_ordered_modifier_fragments.tsv", fragment_rows)
    write_tsv(OUT / "gdt578_121_repeat_slot_voice_assignments.tsv", voiced_slot_rows)
    write_tsv(OUT / "gdt578_61_repeat_particle_spans.tsv", particle_rows)
    write_tsv(OUT / "gdt578_35_respun_sigla_spans.tsv", respun_sigla_rows)
    write_tsv(OUT / "gdt578_58_event_cards.tsv", event_card_rows)
    write_tsv(OUT / "gdt578_5122_attachment_voice_event_edition.tsv", event_rows)
    write_tsv(OUT / "gdt578_793_attachment_voice_statement_edition.tsv", statement_rows)
    write_tsv(OUT / "gdt578_30_page_attachment_voice_profiles.tsv", page_rows)

    particle_counts = Counter(row["particle_de"] for row in particle_rows)
    topology_counts = Counter(group_by_id[row["gdt575_duplicate_group_id"]]["attachment_topology"] for row in voiced_slot_rows)
    changed_state = sum(event_output_by_id[event_id]["state_status"] == "STATE_CARD" for event_id in changed_event_ids)
    changed_nonstate = len(changed_event_ids) - changed_state
    scope_event_ids = {row["event_id"] for row in scope_pairs}
    adjacent_event_ids = {
        row["event_id"] for row in all_duplicate_groups
        if row["duplicate_topology"] == "SAME_ROOT_RAW_ADJACENT"
    }
    cumulative_event_changes = sum(
        row["attachment_voice_working_clause_de"] != event_by_id[row["event_id"]]["gdt574_action_count_clause_de"]
        for row in event_rows
    )
    source_statement_by_id = {row["statement_id"]: row for row in source_statements}
    cumulative_statement_changes = sum(
        row["attachment_voice_working_reading_de"] != source_statement_by_id[row["statement_id"]]["gdt574_action_count_reading_de"]
        for row in statement_rows
    )
    cumulative_page_changes = len({
        row["physical_page"] for row in event_rows
        if row["attachment_voice_working_clause_de"] != event_by_id[row["event_id"]]["gdt574_action_count_clause_de"]
    })
    union_repeat_sigla_positions = {
        (row["event_id"], int(row["slot_atom_position_zero_based"])) for row in voiced_slot_rows
    } | {
        (row["event_id"], int(row["atom_position_zero_based"])) for row in respun_sigla_rows
    }
    result = {
        "experiment_id": "GDT578",
        "status": STATUS,
        "input_sha256": {key: sha256(path) for key, path in INPUTS.items()},
        "event_count": len(event_rows),
        "statement_count": len(statement_rows),
        "page_count": len(page_rows),
        "changed_event_count": len(changed_event_ids),
        "unchanged_event_count": len(event_rows) - len(changed_event_ids),
        "changed_state_event_count": changed_state,
        "changed_nonstate_event_count": changed_nonstate,
        "changed_statement_count": len(changed_statements),
        "changed_page_count": sum(row["page_voice_changed"] == "YES" for row in page_rows),
        "event_card_count": len(event_card_rows),
        "attachment_class_count": len(template_rows),
        "prose_frame_count": len(prose_frame_rows),
        "rendered_group_count": len({row["gdt575_duplicate_group_id"] for row in voiced_slot_rows}),
        "rendered_repeat_slot_count": len(voiced_slot_rows),
        "ordered_modifier_fragment_count": len(fragment_rows),
        "bound_modifier_fragment_count": sum(row["binding_status"] == "GDT577_HEAD_BOUND_REPEAT_SLOT" for row in fragment_rows),
        "unbound_modifier_fragment_count": sum(row["binding_status"] == "UNBOUND_MODIFIER_IN_RAW_ORDER" for row in fragment_rows),
        "repeat_particle_count": len(particle_rows),
        "repeat_particle_counts": dict(sorted(particle_counts.items())),
        "repeat_slot_topology_counts": dict(sorted(topology_counts.items())),
        "respun_sigla_span_count": len(respun_sigla_rows),
        "unchanged_sigla_span_count": len(sigla) - len(respun_sigla_rows),
        "repeat_or_sigla_unique_atom_position_count": len(union_repeat_sigla_positions),
        "cumulative_changed_event_count_against_gdt574": cumulative_event_changes,
        "cumulative_changed_statement_count_against_gdt574": cumulative_statement_changes,
        "cumulative_changed_page_count_against_gdt574": cumulative_page_changes,
        "scope_pair_events_unchanged": all(event_id not in changed_event_ids for event_id in scope_event_ids),
        "raw_adjacent_repeat_events_unchanged": all(event_id not in changed_event_ids for event_id in adjacent_event_ids),
        "conflict_event_unchanged": target_by_event[CONFLICT_EVENT] == event_by_id[CONFLICT_EVENT]["learned_sigla_working_clause_de"],
        "conflict_statement_unchanged": next(row for row in statement_rows if row["statement_id"] == CONFLICT_STATEMENT)["attachment_statement_changed"] == "NO",
        "conflict_page_unchanged": next(row for row in page_rows if row["physical_page"] == CONFLICT_PAGE)["page_voice_changed"] == "NO",
        "no_new_page": True,
        "no_root_change": True,
        "no_recipe_change": True,
    }
    (OUT / "gdt578_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# GDT578 event-keyed interrupted-modifier edition",
        "",
        f"Status: `{STATUS}`",
        "",
    ]
    statements_by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in statement_rows:
        statements_by_page[str(row["physical_page"])].append(row)
    for page in page_rows:
        page_id = str(page["physical_page"])
        lines.extend([f"## {page_id} · {page['registers']}", ""])
        for statement in statements_by_page[page_id]:
            marker = " · Anschlussstimme" if statement["attachment_statement_changed"] == "YES" else ""
            lines.extend([
                f"### {statement['statement_id']}{marker}",
                "",
                str(statement["attachment_voice_working_reading_de"]),
                "",
            ])
    (OUT / "GDT578_ATTACHMENT_VOICE_THIRTY_PAGE_EDITION.md").write_text(
        "\n".join(lines).rstrip() + "\n",
        encoding="utf-8",
    )

    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
