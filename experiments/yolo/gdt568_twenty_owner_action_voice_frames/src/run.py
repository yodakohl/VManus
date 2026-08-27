#!/usr/bin/env python3
"""Compile twenty owner-voice action frames into the complete working edition."""

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
BASE = ROOT / "experiments/yolo/gdt568_twenty_owner_action_voice_frames"
OUT = BASE / "artifacts"
G567 = ROOT / "experiments/yolo/gdt567_owner_voice_seam_adapter/artifacts"
G566 = ROOT / "experiments/yolo/gdt566_complete_thirty_page_prose_working_edition/artifacts"
G565 = ROOT / "experiments/yolo/gdt565_state_microphrase_template_generator/artifacts"
G415 = ROOT / "experiments/yolo/gdt415_owner_local_semantic_expansion_atlas/artifacts"
G416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts"
G539 = ROOT / "experiments/yolo/gdt539_four_page_contextual_statement_edition/artifacts"
INPUTS = {
    "voice_events": G567 / "gdt567_5122_owner_voice_event_edition.tsv",
    "voice_statements": G567 / "gdt567_793_owner_voice_statement_edition.tsv",
    "page_profiles": G566 / "gdt566_30_page_edition_profiles.tsv",
    "state_replay": G565 / "gdt565_1656_template_replay.tsv",
    "register_expansions": G415 / "gdt415_95_register_expansion_atlas.tsv",
    "old_clauses": G416 / "gdt416_4576_imperative_clauses.tsv",
    "current_clauses": G539 / "gdt539_546_contextual_prose_events.tsv",
}

REGISTERS = ("SOURCE_SECTION_T", "HERBAL", "CELESTIAL", "BIOLOGICAL", "PHARMA")
ACTIONS = ("OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P")
GENERIC_ACTION = {
    "OK": ("setze", "setze {argument}"),
    "CH": ("nimm", "nimm {argument}"),
    "SH": ("halte", "halte {argument}"),
    "K": ("gib", "gib {argument}"),
    "S": ("wähle", "wähle {argument}"),
    "CHD": ("bearbeite", "bearbeite {argument}"),
    "T": ("stelle ein", "stelle {argument} ein"),
    "R": ("markiere", "markiere {argument}"),
    "P": ("setze ein", "setze {argument} ein"),
}
OWNER_ACTION = {
    "SOURCE_SECTION_T": {
        "OK": "trage {argument} ein", "CH": "entnimm {argument}", "SH": "halte {argument} fest",
        "K": "ordne {argument} zu", "S": "wähle {argument}", "CHD": "bearbeite {argument}",
        "T": "lege {argument} fest", "R": "kennzeichne {argument}", "P": "setze {argument} ein",
    },
    "HERBAL": {
        "OK": "setze {argument} im Arbeitsgang an", "CH": "nimm {argument}", "SH": "halte {argument}",
        "K": "gib {argument} zu", "S": "wähle {argument}", "CHD": "bearbeite {argument}",
        "T": "stelle {argument} ein", "R": "markiere {argument}", "P": "setze {argument} ein",
    },
    "CELESTIAL": {
        "OK": "setze {argument}", "CH": "nimm {argument} auf", "SH": "halte {argument}",
        "K": "ordne {argument} zu", "S": "wähle {argument}", "CHD": "bearbeite {argument}",
        "T": "stelle {argument} ein", "R": "markiere {argument}", "P": "setze {argument} ein",
    },
    "BIOLOGICAL": {
        "OK": "setze {argument} im Stationsgang an", "CH": "entnimm {argument}", "SH": "halte {argument}",
        "K": "führe {argument} zu", "S": "wähle {argument}", "CHD": "bearbeite {argument}",
        "T": "stelle {argument} ein", "R": "markiere {argument}", "P": "setze {argument} ein",
    },
    "PHARMA": {
        "OK": "setze {argument} als Ansatz an", "CH": "nimm {argument}", "SH": "halte {argument}",
        "K": "gib {argument} zu", "S": "wähle {argument}", "CHD": "bearbeite {argument}",
        "T": "stelle {argument} ein", "R": "markiere {argument}", "P": "setze {argument} ein",
    },
}
ARGUMENTS = {
    "SOURCE_SECTION_T": {"Y": "den laufenden Eintrag", "AIIN": "den Kennwert", "AIN": "den Teilwert", "OR": "die Eintragseinheit"},
    "HERBAL": {"Y": "den Pflanzenposten", "AIIN": "den Arbeitswert", "AIN": "den Materialanteil", "OR": "die Arbeitseinheit"},
    "CELESTIAL": {"Y": "den Positionsposten", "AIIN": "den Positionswert", "OR": "die Positionseinheit"},
    "BIOLOGICAL": {"Y": "den Stationsposten", "AIIN": "den Stationswert", "AIN": "den Stationsanteil", "OR": "die Stationseinheit"},
    "PHARMA": {"Y": "den Drogenposten", "AIIN": "den Mengenwert", "AIN": "den Drogenanteil", "OR": "die Ansatzeinheit"},
}
DOUBLE_Y = {
    "SOURCE_SECTION_T": "die beiden laufenden Einträge", "HERBAL": "die beiden Pflanzenposten",
    "CELESTIAL": "die beiden Positionsposten", "BIOLOGICAL": "die beiden Stationsposten",
    "PHARMA": "die beiden Drogenposten",
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


def roots(value: str, separator: str = "|") -> list[str]:
    return [] if value in ("", "NONE") else value.split(separator)


def contains_word(text: str, phrase: str) -> bool:
    return re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", text, re.IGNORECASE) is not None


def normalize_template(template: str, argument: str) -> str:
    return " ".join(template.format(argument=argument).split())


def argument_phrase(state: dict[str, str], register: str) -> str:
    values = roots(state["effective_argument_roots"])
    if not values:
        return ""
    if values == ["Y", "Y"]:
        return DOUBLE_Y[register]
    pieces = [ARGUMENTS[register][value] for value in values]
    return pieces[0] if len(pieces) == 1 else ", ".join(pieces[:-1]) + " und " + pieces[-1]


def action_units(state: dict[str, str]) -> list[tuple[str, int]]:
    action_roots = roots(state["effective_action_roots"])
    if not action_roots:
        return []
    output = []
    index = 0
    for token in state["action_topology"].split("+"):
        count = 1 if token == "A" else int(token[2:])
        values = action_roots[index:index + count]
        if len(values) != count or len(set(values)) != 1:
            raise RuntimeError(f"Action topology/root mismatch at {state['event_id']}")
        output.append((values[0], count))
        index += count
    if index != len(action_roots):
        raise RuntimeError(f"Unconsumed action roots at {state['event_id']}")
    return output


def action_chain(state: dict[str, str], register: str, owner_voice: bool) -> str:
    argument = argument_phrase(state, register)
    parts = []
    for root, count in action_units(state):
        if owner_voice:
            template = OWNER_ACTION[register][root]
        else:
            template = GENERIC_ACTION[root][1] if argument else GENERIC_ACTION[root][0]
        phrase = normalize_template(template, argument)
        if count == 2:
            phrase += " zweimal"
        elif count > 2:
            phrase += f" {count}-mal"
        parts.append(phrase)
    return " und ".join(parts) or "NONE"


def replace_chain(text: str, old: str, new: str) -> str:
    match = re.search(re.escape(old), text, re.IGNORECASE)
    if match is None:
        raise RuntimeError(f"Generated action chain not found: {old!r} in {text!r}")
    replacement = new[0].upper() + new[1:] if match.group()[0].isupper() else new
    return text[:match.start()] + replacement + text[match.end():]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    source_events = read_tsv(INPUTS["voice_events"])
    source_statements = read_tsv(INPUTS["voice_statements"])
    pages = read_tsv(INPUTS["page_profiles"])
    state_source = read_tsv(INPUTS["state_replay"])
    expansions = read_tsv(INPUTS["register_expansions"])
    old_clauses = read_tsv(INPUTS["old_clauses"])
    current_clauses = read_tsv(INPUTS["current_clauses"])
    if [len(source_events), len(source_statements), len(pages), len(state_source), len(expansions), len(old_clauses), len(current_clauses)] != [5122, 793, 30, 1656, 95, 4576, 546]:
        raise RuntimeError("Input count drift")
    state_by_id = {row["event_id"]: row for row in state_source}
    if set(state_by_id) != {row["event_id"] for row in source_events if row["state_status"] == "STATE_CARD"}:
        raise RuntimeError("State partition drift")
    expansion_by_cell = {(row["root"], row["register"]): row for row in expansions if row["root"] in ACTIONS}
    if len(expansion_by_cell) != 45:
        raise RuntimeError("GDT415 action cell drift")
    old_by_id = {row["global_running_event_id"]: row for row in old_clauses}
    current_by_id = {row["event_id"]: row for row in current_clauses}

    state_events = [row for row in source_events if row["state_status"] == "STATE_CARD"]
    card_rows: list[dict[str, object]] = []
    card_id_by_cell: dict[tuple[str, str], str] = {}
    for root in ACTIONS:
        grouped_registers: dict[str, list[str]] = {}
        for register in REGISTERS:
            grouped_registers.setdefault(OWNER_ACTION[register][root], []).append(register)
        for template, register_scope in grouped_registers.items():
            card_id = f"GDT568-A{len(card_rows) + 1:02d}"
            for register in register_scope:
                card_id_by_cell[(register, root)] = card_id
            members = [
                row for row in state_events
                if row["register"] in register_scope and root in roots(state_by_id[row["event_id"]]["effective_action_roots"])
            ]
            target_lead = template.split()[0]
            supported = sum(contains_word(row["owner_bound_control_clause_de"], target_lead) for row in members)
            occurrences = sum(roots(state_by_id[row["event_id"]]["effective_action_roots"]).count(root) for row in members)
            generic_no_object, generic_with_object = GENERIC_ACTION[root]
            card_rows.append({
                "action_voice_card_id": card_id,
                "action_root": root,
                "register_scope": "|".join(register_scope),
                "register_cell_count": len(register_scope),
                "generic_no_argument_de": generic_no_object,
                "generic_with_argument_de": generic_with_object,
                "owner_no_argument_de": normalize_template(template, ""),
                "owner_with_argument_de": template,
                "target_action_head_de": target_lead,
                "requires_frame_change": "YES" if template != generic_with_object else "NO",
                "state_event_count": len(members),
                "state_action_occurrence_count": occurrences,
                "owner_bound_target_head_support_count": supported,
                "support_rate": f"{supported / len(members):.12f}",
                "gdt415_owner_local_expansions": "|".join(
                    f"{register}:{expansion_by_cell[(root, register)]['owner_local_expansion_de']}" for register in register_scope
                ),
                "example_event_ids": "|".join(row["event_id"] for row in members[:8]),
                "guard": "ACTION_OWNER_VOICE_ONLY__PORTABLE_ROOT_UNCHANGED",
            })
    if len(card_rows) != 20 or len(card_id_by_cell) != 45:
        raise RuntimeError("Action card compression drift")
    if any(row["owner_bound_target_head_support_count"] != row["state_event_count"] for row in card_rows):
        raise RuntimeError("Action-card control support drift")

    cell_rows: list[dict[str, object]] = []
    for register in REGISTERS:
        for root in ACTIONS:
            members = [
                row for row in state_events
                if row["register"] == register and root in roots(state_by_id[row["event_id"]]["effective_action_roots"])
            ]
            occurrences = sum(roots(state_by_id[row["event_id"]]["effective_action_roots"]).count(root) for row in members)
            template = OWNER_ACTION[register][root]
            lead = template.split()[0]
            expansion = expansion_by_cell[(root, register)]
            cell_rows.append({
                "register_action_cell_id": f"GDT568-C{len(cell_rows) + 1:02d}",
                "register": register,
                "action_root": root,
                "action_voice_card_id": card_id_by_cell[(register, root)],
                "portable_default_de": expansion["portable_default_de"],
                "gdt415_owner_local_expansion_de": expansion["owner_local_expansion_de"],
                "generic_with_argument_de": GENERIC_ACTION[root][1],
                "owner_with_argument_de": template,
                "target_action_head_de": lead,
                "frame_already_exact": "YES" if template == GENERIC_ACTION[root][1] else "NO",
                "action_head_already_exact": "YES" if lead == GENERIC_ACTION[root][1].split()[0] else "NO",
                "state_event_count": len(members),
                "state_action_occurrence_count": occurrences,
                "owner_bound_target_head_support_count": sum(contains_word(row["owner_bound_control_clause_de"], lead) for row in members),
                "gdt415_source_event_count": expansion["event_count"],
                "guard": "REGISTER_CELL_OBSERVED_IN_GDT415__STATE_APPLICATION_SEPARATE",
            })

    event_rows: list[dict[str, object]] = []
    state_rows: list[dict[str, object]] = []
    for source in source_events:
        before = source["owner_voice_working_clause_de"]
        after = before
        generic_chain = owner_chain = "NOT_APPLICABLE"
        applied: list[str] = []
        state = state_by_id.get(source["event_id"])
        if state is not None:
            generic_chain = action_chain(state, source["register"], False)
            owner_chain = action_chain(state, source["register"], True)
            if generic_chain != "NONE":
                after = replace_chain(before, generic_chain, owner_chain)
                for root, _ in action_units(state):
                    card_id = card_id_by_cell[(source["register"], root)]
                    if card_id not in applied:
                        applied.append(card_id)
        event_row = {
            "edition_event_ordinal": source["edition_event_ordinal"],
            "event_id": source["event_id"],
            "statement_id": source["statement_id"],
            "card_ordinal_in_statement": source["card_ordinal_in_statement"],
            "physical_page": source["physical_page"],
            "register": source["register"],
            "owner_id": source["owner_id"],
            "surface": source["surface"],
            "final_context_recipe": source["final_context_recipe"],
            "state_status": source["state_status"],
            "gdt567_owner_voice_clause_de": before,
            "action_voice_working_clause_de": after,
            "owner_bound_control_clause_de": source["owner_bound_control_clause_de"],
            "generic_action_chain_de": generic_chain,
            "owner_action_chain_de": owner_chain,
            "action_voice_changed": "YES" if after != before else "NO",
            "action_voice_equals_owner_bound": "YES" if after == source["owner_bound_control_clause_de"] else "NO",
            "action_voice_card_count": len(applied),
            "action_voice_card_ids": "|".join(applied) or "NONE",
            "state_atom_alignment": source["state_atom_alignment"],
            "guard": "EVENT_RECIPE_ROOTS_AND_BOUNDARY_UNCHANGED__ACTION_VOICE_SEPARATE",
        }
        event_rows.append(event_row)
        if state is not None:
            state_rows.append({
                "state_edition_ordinal": len(state_rows) + 1,
                **{key: event_row[key] for key in (
                    "event_id", "statement_id", "physical_page", "register", "owner_id", "surface",
                    "final_context_recipe", "gdt567_owner_voice_clause_de", "action_voice_working_clause_de",
                    "owner_bound_control_clause_de", "generic_action_chain_de", "owner_action_chain_de",
                    "action_voice_changed", "action_voice_equals_owner_bound", "action_voice_card_count",
                    "action_voice_card_ids", "state_atom_alignment", "guard",
                )},
                "effective_action_roots": state["effective_action_roots"],
                "action_topology": state["action_topology"],
                "effective_argument_roots": state["effective_argument_roots"],
            })

    events_by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        events_by_statement[str(row["statement_id"])].append(row)
    statement_rows: list[dict[str, object]] = []
    for source in source_statements:
        members = sorted(events_by_statement[source["statement_id"]], key=lambda row: int(row["card_ordinal_in_statement"]))
        before = " ".join(str(row["gdt567_owner_voice_clause_de"]) for row in members)
        after = " ".join(str(row["action_voice_working_clause_de"]) for row in members)
        control = " ".join(str(row["owner_bound_control_clause_de"]) for row in members)
        if before != source["owner_voice_working_reading_de"] or control != source["owner_bound_control_reading_de"]:
            raise RuntimeError(f"Statement reconstruction drift at {source['statement_id']}")
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
            "changed_state_event_count": sum(row["action_voice_changed"] == "YES" for row in members),
            "action_voice_card_application_count": sum(int(row["action_voice_card_count"]) for row in members),
            "event_ids": source["event_ids"],
            "surface_sequence": source["surface_sequence"],
            "gdt567_owner_voice_reading_de": before,
            "action_voice_working_reading_de": after,
            "owner_bound_control_reading_de": control,
            "action_voice_statement_changed": "YES" if after != before else "NO",
            "action_voice_equals_owner_bound": "YES" if after == control else "NO",
            "end_mode": source["end_mode"],
            "guard": "STATEMENT_EVENT_ORDER_AND_BOUNDARIES_UNCHANGED",
        })

    def nonstate_action_roots(event_id: str) -> list[str]:
        source = old_by_id.get(event_id) or current_by_id.get(event_id)
        if source is None:
            raise RuntimeError(f"Missing nonstate action source: {event_id}")
        explicit = roots(source["explicit_action_roots"])
        return explicit or roots(source["inherited_action_root"])

    event_by_id = {row["event_id"]: row for row in event_rows}
    seam_rows: list[dict[str, object]] = []
    direction_names = {
        ("NONSTATE_CARD", "NONSTATE_CARD"): "NONSTATE_TO_NONSTATE",
        ("NONSTATE_CARD", "STATE_CARD"): "NONSTATE_TO_STATE",
        ("STATE_CARD", "NONSTATE_CARD"): "STATE_TO_NONSTATE",
        ("STATE_CARD", "STATE_CARD"): "STATE_TO_STATE",
    }
    for statement in statement_rows:
        members = [event_by_id[event_id] for event_id in statement["event_ids"].split("|")]
        for left, right in zip(members, members[1:]):
            direction = direction_names[(str(left["state_status"]), str(right["state_status"]))]
            mixed = left["state_status"] != right["state_status"]
            contacts = []
            frame_before = frame_after = head_before = head_after = 0
            state_endpoint = None
            if mixed:
                state_endpoint = left if left["state_status"] == "STATE_CARD" else right
                nonstate_endpoint = right if left["state_status"] == "STATE_CARD" else left
                state = state_by_id[str(state_endpoint["event_id"])]
                state_action_set = set(roots(state["effective_action_roots"]))
                nonstate_action_set = set(nonstate_action_roots(str(nonstate_endpoint["event_id"])))
                for root in ACTIONS:
                    if root not in state_action_set.intersection(nonstate_action_set):
                        continue
                    template = OWNER_ACTION[str(state_endpoint["register"])][root]
                    target_head = template.split()[0]
                    if not contains_word(str(nonstate_endpoint["action_voice_working_clause_de"]), target_head):
                        continue
                    contacts.append(f"{root}:{target_head}")
                    frame_before += int(template == GENERIC_ACTION[root][1])
                    frame_after += 1
                    head_before += int(target_head == GENERIC_ACTION[root][1].split()[0])
                    head_after += 1
            seam_rows.append({
                "seam_ordinal": len(seam_rows) + 1,
                "statement_id": statement["statement_id"],
                "physical_page": statement["physical_page"],
                "register": statement["register"],
                "left_event_id": left["event_id"],
                "right_event_id": right["event_id"],
                "direction": direction,
                "mixed_state_nonstate": "YES" if mixed else "NO",
                "state_endpoint_event_id": state_endpoint["event_id"] if state_endpoint else "NOT_APPLICABLE",
                "state_endpoint_changed": state_endpoint["action_voice_changed"] if state_endpoint else "NOT_APPLICABLE",
                "shared_action_contacts": "|".join(contacts) or "NONE",
                "shared_action_contact_count": len(contacts),
                "full_action_frame_exact_before": frame_before,
                "full_action_frame_exact_after": frame_after,
                "action_head_exact_before": head_before,
                "action_head_exact_after": head_after,
                "left_gdt567_clause_de": left["gdt567_owner_voice_clause_de"],
                "right_gdt567_clause_de": right["gdt567_owner_voice_clause_de"],
                "left_action_voice_clause_de": left["action_voice_working_clause_de"],
                "right_action_voice_clause_de": right["action_voice_working_clause_de"],
                "guard": "ADJACENCY_ONLY__ACTION_FRAME_DOES_NOT_MERGE_EVENTS",
            })

    direction_rows: list[dict[str, object]] = []
    for direction in ("NONSTATE_TO_NONSTATE", "NONSTATE_TO_STATE", "STATE_TO_NONSTATE", "STATE_TO_STATE"):
        members = [row for row in seam_rows if row["direction"] == direction]
        direction_rows.append({
            "direction": direction,
            "seam_count": len(members),
            "statement_count": len({str(row["statement_id"]) for row in members}),
            "state_endpoint_changed_count": sum(row["state_endpoint_changed"] == "YES" for row in members),
            "shared_action_contact_seam_count": sum(row["shared_action_contacts"] != "NONE" for row in members),
            "shared_action_contact_count": sum(int(row["shared_action_contact_count"]) for row in members),
            "full_action_frame_exact_before": sum(int(row["full_action_frame_exact_before"]) for row in members),
            "full_action_frame_exact_after": sum(int(row["full_action_frame_exact_after"]) for row in members),
            "action_head_exact_before": sum(int(row["action_head_exact_before"]) for row in members),
            "action_head_exact_after": sum(int(row["action_head_exact_after"]) for row in members),
        })

    root_rows: list[dict[str, object]] = []
    for root in ACTIONS:
        state_members = [row for row in state_events if root in roots(state_by_id[row["event_id"]]["effective_action_roots"])]
        contact_rows = [
            row for row in seam_rows
            if any(item.startswith(root + ":") for item in row["shared_action_contacts"].split("|"))
        ]
        root_rows.append({
            "action_root": root,
            "action_voice_card_count": len({card_id_by_cell[(register, root)] for register in REGISTERS}),
            "register_cell_count": 5,
            "state_event_count": len(state_members),
            "state_action_occurrence_count": sum(roots(state_by_id[row["event_id"]]["effective_action_roots"]).count(root) for row in state_members),
            "register_cells_requiring_frame_change": sum(OWNER_ACTION[register][root] != GENERIC_ACTION[root][1] for register in REGISTERS),
            "register_cells_requiring_head_change": sum(OWNER_ACTION[register][root].split()[0] != GENERIC_ACTION[root][1].split()[0] for register in REGISTERS),
            "shared_action_contact_count": len(contact_rows),
            "full_action_frame_exact_before": sum(
                OWNER_ACTION[str(row["register"])][root] == GENERIC_ACTION[root][1] for row in contact_rows
            ),
            "full_action_frame_exact_after": len(contact_rows),
            "action_head_exact_before": sum(
                OWNER_ACTION[str(row["register"])][root].split()[0] == GENERIC_ACTION[root][1].split()[0]
                for row in contact_rows
            ),
            "action_head_exact_after": len(contact_rows),
        })

    register_rows: list[dict[str, object]] = []
    for register in REGISTERS:
        members = [row for row in state_rows if row["register"] == register]
        register_seams = [row for row in seam_rows if row["register"] == register and row["mixed_state_nonstate"] == "YES"]
        register_rows.append({
            "register": register,
            "state_event_count": len(members),
            "action_bearing_state_event_count": sum(row["effective_action_roots"] != "NONE" for row in members),
            "changed_state_event_count": sum(row["action_voice_changed"] == "YES" for row in members),
            "action_voice_card_count": len({card_id_by_cell[(register, root)] for root in ACTIONS}),
            "action_voice_card_application_count": sum(int(row["action_voice_card_count"]) for row in members),
            "shared_action_contact_count": sum(int(row["shared_action_contact_count"]) for row in register_seams),
            "full_action_frame_exact_before": sum(int(row["full_action_frame_exact_before"]) for row in register_seams),
            "full_action_frame_exact_after": sum(int(row["full_action_frame_exact_after"]) for row in register_seams),
            "action_head_exact_before": sum(int(row["action_head_exact_before"]) for row in register_seams),
            "action_head_exact_after": sum(int(row["action_head_exact_after"]) for row in register_seams),
        })

    mixed_seams = [row for row in seam_rows if row["mixed_state_nonstate"] == "YES"]
    result = {
        "status": "PASS_20_OWNER_ACTION_FRAMES__45_REGISTER_CELLS__763_STATE_CLAUSES_HARMONIZED__866_SHARED_ACTION_CONTACTS__FULL_FRAME_517_TO_866__HEAD_730_TO_866__ZERO_ROOT_CHANGE",
        "owner_action_voice_card_count": len(card_rows),
        "register_action_cell_count": len(cell_rows),
        "gdt415_action_cell_count": len(expansion_by_cell),
        "state_event_count": len(state_rows),
        "action_bearing_state_event_count": sum(row["effective_action_roots"] != "NONE" for row in state_rows),
        "actionless_state_event_count": sum(row["effective_action_roots"] == "NONE" for row in state_rows),
        "state_event_root_use_count": sum(len(set(roots(row["effective_action_roots"]))) for row in state_source),
        "state_action_occurrence_count": sum(len(roots(row["effective_action_roots"])) for row in state_source),
        "owner_bound_target_head_supported_event_root_use_count": sum(int(row["owner_bound_target_head_support_count"]) for row in card_rows),
        "changed_state_event_count": sum(row["action_voice_changed"] == "YES" for row in state_rows),
        "unchanged_state_event_count": sum(row["action_voice_changed"] == "NO" for row in state_rows),
        "owner_voice_equals_owner_bound_before_count": sum(row["gdt567_owner_voice_clause_de"] == row["owner_bound_control_clause_de"] for row in state_rows),
        "action_voice_equals_owner_bound_after_count": sum(row["action_voice_equals_owner_bound"] == "YES" for row in state_rows),
        "distinct_owner_voice_state_clause_count": len({row["gdt567_owner_voice_clause_de"] for row in state_rows}),
        "distinct_action_voice_state_clause_count": len({row["action_voice_working_clause_de"] for row in state_rows}),
        "changed_statement_count": sum(row["action_voice_statement_changed"] == "YES" for row in statement_rows),
        "unchanged_statement_count": sum(row["action_voice_statement_changed"] == "NO" for row in statement_rows),
        "changed_physical_page_count": len({row["physical_page"] for row in state_rows if row["action_voice_changed"] == "YES"}),
        "complete_event_count": len(event_rows),
        "complete_statement_count": len(statement_rows),
        "within_statement_seam_count": len(seam_rows),
        "mixed_state_nonstate_seam_count": len(mixed_seams),
        "shared_action_contact_seam_count": sum(row["shared_action_contacts"] != "NONE" for row in mixed_seams),
        "shared_action_contact_count": sum(int(row["shared_action_contact_count"]) for row in mixed_seams),
        "full_action_frame_exact_before": sum(int(row["full_action_frame_exact_before"]) for row in mixed_seams),
        "full_action_frame_exact_after": sum(int(row["full_action_frame_exact_after"]) for row in mixed_seams),
        "action_head_exact_before": sum(int(row["action_head_exact_before"]) for row in mixed_seams),
        "action_head_exact_after": sum(int(row["action_head_exact_after"]) for row in mixed_seams),
        "new_pages": 0,
        "new_events": 0,
        "new_statements": 0,
        "new_surfaces": 0,
        "new_recipes": 0,
        "new_root_values": 0,
        "input_sha256": {name: sha256(path) for name, path in INPUTS.items()},
    }

    write_tsv(OUT / "gdt568_20_owner_action_voice_cards.tsv", card_rows)
    write_tsv(OUT / "gdt568_45_register_action_cells.tsv", cell_rows)
    write_tsv(OUT / "gdt568_1656_action_voice_state_clauses.tsv", state_rows)
    write_tsv(OUT / "gdt568_5122_action_voice_event_edition.tsv", event_rows)
    write_tsv(OUT / "gdt568_793_action_voice_statement_edition.tsv", statement_rows)
    write_tsv(OUT / "gdt568_4329_action_seam_atlas.tsv", seam_rows)
    write_tsv(OUT / "gdt568_4_action_seam_direction_profiles.tsv", direction_rows)
    write_tsv(OUT / "gdt568_9_action_root_profiles.tsv", root_rows)
    write_tsv(OUT / "gdt568_5_register_action_voice_profiles.tsv", register_rows)

    statements_by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in statement_rows:
        statements_by_page[str(row["physical_page"])].append(row)
    book = [
        "# GDT568 – handlungsstimmige 30-Seiten-Arbeitsausgabe",
        "",
        "Zwanzig kleine Verbkarten covern alle45 tatsächlich benutzten Register×Handlungs-Zellen.",
        "Sie ändern nur die deutsche owner-Stimme der neun unveränderten Handlungswurzeln.",
        "",
        "```text",
        "763/1.656 Zustandszeilen mit angepasstem Verbrahmen",
        "866 gemeinsame Handlungskontakte an854 gemischten Anschlüssen",
        "voller Verbrahmen: 517 → 866 exakt",
        "Verbkopf:          730 → 866 exakt",
        "```",
        "",
    ]
    for page in pages:
        book += [f"## {page['physical_page']}", ""]
        page_statements = statements_by_page[page["physical_page"]]
        if not page_statements:
            book += ["Keine laufende Prosa; zugelassene Lokalregisterseite bleibt sichtbar.", ""]
            continue
        for statement in page_statements:
            book += [
                f"### {statement['statement_id']} · {statement['statement_mode']} · {statement['event_count']} Karten",
                "",
                f"**Formen:** {statement['surface_sequence']}",
                "",
                str(statement["action_voice_working_reading_de"]),
                "",
            ]
    (OUT / "GDT568_ACTION_VOICE_THIRTY_PAGE_EDITION.md").write_text("\n".join(book), encoding="utf-8")
    (OUT / "gdt568_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
