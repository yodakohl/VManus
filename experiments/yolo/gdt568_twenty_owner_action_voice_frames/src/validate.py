#!/usr/bin/env python3
"""Independently validate the GDT568 owner-action voice frames."""

from __future__ import annotations

import csv
import hashlib
import json
import re
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
BASE = ROOT / "experiments/yolo/gdt568_twenty_owner_action_voice_frames"
OUT = BASE / "artifacts"
RUNNER = BASE / "src/run.py"
VALIDATION_OUT = OUT / "gdt568_validation.json"
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
ARTIFACTS = {
    "cards": OUT / "gdt568_20_owner_action_voice_cards.tsv",
    "cells": OUT / "gdt568_45_register_action_cells.tsv",
    "states": OUT / "gdt568_1656_action_voice_state_clauses.tsv",
    "events": OUT / "gdt568_5122_action_voice_event_edition.tsv",
    "statements": OUT / "gdt568_793_action_voice_statement_edition.tsv",
    "seams": OUT / "gdt568_4329_action_seam_atlas.tsv",
    "directions": OUT / "gdt568_4_action_seam_direction_profiles.tsv",
    "roots": OUT / "gdt568_9_action_root_profiles.tsv",
    "registers": OUT / "gdt568_5_register_action_voice_profiles.tsv",
    "book": OUT / "GDT568_ACTION_VOICE_THIRTY_PAGE_EDITION.md",
    "result": OUT / "gdt568_result.json",
}
STATUS = "PASS_20_OWNER_ACTION_FRAMES__45_REGISTER_CELLS__763_STATE_CLAUSES_HARMONIZED__866_SHARED_ACTION_CONTACTS__FULL_FRAME_517_TO_866__HEAD_730_TO_866__ZERO_ROOT_CHANGE"
REGISTERS = ("SOURCE_SECTION_T", "HERBAL", "CELESTIAL", "BIOLOGICAL", "PHARMA")
ACTIONS = ("OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P")
GENERIC = {
    "OK": ("setze", "setze {argument}"), "CH": ("nimm", "nimm {argument}"),
    "SH": ("halte", "halte {argument}"), "K": ("gib", "gib {argument}"),
    "S": ("wähle", "wähle {argument}"), "CHD": ("bearbeite", "bearbeite {argument}"),
    "T": ("stelle ein", "stelle {argument} ein"), "R": ("markiere", "markiere {argument}"),
    "P": ("setze ein", "setze {argument} ein"),
}
OWNER = {
    "SOURCE_SECTION_T": {"OK": "trage {argument} ein", "CH": "entnimm {argument}", "SH": "halte {argument} fest", "K": "ordne {argument} zu", "S": "wähle {argument}", "CHD": "bearbeite {argument}", "T": "lege {argument} fest", "R": "kennzeichne {argument}", "P": "setze {argument} ein"},
    "HERBAL": {"OK": "setze {argument} im Arbeitsgang an", "CH": "nimm {argument}", "SH": "halte {argument}", "K": "gib {argument} zu", "S": "wähle {argument}", "CHD": "bearbeite {argument}", "T": "stelle {argument} ein", "R": "markiere {argument}", "P": "setze {argument} ein"},
    "CELESTIAL": {"OK": "setze {argument}", "CH": "nimm {argument} auf", "SH": "halte {argument}", "K": "ordne {argument} zu", "S": "wähle {argument}", "CHD": "bearbeite {argument}", "T": "stelle {argument} ein", "R": "markiere {argument}", "P": "setze {argument} ein"},
    "BIOLOGICAL": {"OK": "setze {argument} im Stationsgang an", "CH": "entnimm {argument}", "SH": "halte {argument}", "K": "führe {argument} zu", "S": "wähle {argument}", "CHD": "bearbeite {argument}", "T": "stelle {argument} ein", "R": "markiere {argument}", "P": "setze {argument} ein"},
    "PHARMA": {"OK": "setze {argument} als Ansatz an", "CH": "nimm {argument}", "SH": "halte {argument}", "K": "gib {argument} zu", "S": "wähle {argument}", "CHD": "bearbeite {argument}", "T": "stelle {argument} ein", "R": "markiere {argument}", "P": "setze {argument} ein"},
}
ARGUMENTS = {
    "SOURCE_SECTION_T": {"Y": "den laufenden Eintrag", "AIIN": "den Kennwert", "AIN": "den Teilwert", "OR": "die Eintragseinheit"},
    "HERBAL": {"Y": "den Pflanzenposten", "AIIN": "den Arbeitswert", "AIN": "den Materialanteil", "OR": "die Arbeitseinheit"},
    "CELESTIAL": {"Y": "den Positionsposten", "AIIN": "den Positionswert", "OR": "die Positionseinheit"},
    "BIOLOGICAL": {"Y": "den Stationsposten", "AIIN": "den Stationswert", "AIN": "den Stationsanteil", "OR": "die Stationseinheit"},
    "PHARMA": {"Y": "den Drogenposten", "AIIN": "den Mengenwert", "AIN": "den Drogenanteil", "OR": "die Ansatzeinheit"},
}
DOUBLE_Y = {"SOURCE_SECTION_T": "die beiden laufenden Einträge", "HERBAL": "die beiden Pflanzenposten", "CELESTIAL": "die beiden Positionsposten", "BIOLOGICAL": "die beiden Stationsposten", "PHARMA": "die beiden Drogenposten"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def roots(value: str) -> list[str]:
    return [] if value in ("", "NONE") else value.split("|")


def has(text: str, phrase: str) -> bool:
    return re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", text, re.IGNORECASE) is not None


def render(template: str, argument: str) -> str:
    return " ".join(template.format(argument=argument).split())


def argument_phrase(state: dict[str, str], register: str) -> str:
    values = roots(state["effective_argument_roots"])
    if not values:
        return ""
    if values == ["Y", "Y"]:
        return DOUBLE_Y[register]
    pieces = [ARGUMENTS[register][value] for value in values]
    return pieces[0] if len(pieces) == 1 else ", ".join(pieces[:-1]) + " und " + pieces[-1]


def units(state: dict[str, str]) -> list[tuple[str, int]]:
    values = roots(state["effective_action_roots"])
    if not values:
        return []
    output = []
    index = 0
    for token in state["action_topology"].split("+"):
        count = 1 if token == "A" else int(token[2:])
        group = values[index:index + count]
        if len(group) != count or len(set(group)) != 1:
            raise RuntimeError(f"Topology mismatch at {state['event_id']}")
        output.append((group[0], count))
        index += count
    if index != len(values):
        raise RuntimeError(f"Action root remainder at {state['event_id']}")
    return output


def chain(state: dict[str, str], register: str, owner: bool) -> str:
    argument = argument_phrase(state, register)
    parts = []
    for root, count in units(state):
        template = OWNER[register][root] if owner else GENERIC[root][1] if argument else GENERIC[root][0]
        phrase = render(template, argument)
        if count == 2:
            phrase += " zweimal"
        elif count > 2:
            phrase += f" {count}-mal"
        parts.append(phrase)
    return " und ".join(parts) or "NONE"


def replace_chain(text: str, old: str, new: str) -> str:
    match = re.search(re.escape(old), text, re.IGNORECASE)
    if match is None:
        raise RuntimeError(f"Missing chain {old!r}")
    replacement = new[0].upper() + new[1:] if match.group()[0].isupper() else new
    return text[:match.start()] + replacement + text[match.end():]


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object = None) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    src_events = read_tsv(INPUTS["voice_events"])
    src_statements = read_tsv(INPUTS["voice_statements"])
    src_pages = read_tsv(INPUTS["page_profiles"])
    src_states = read_tsv(INPUTS["state_replay"])
    expansions = read_tsv(INPUTS["register_expansions"])
    old_clauses = read_tsv(INPUTS["old_clauses"])
    current_clauses = read_tsv(INPUTS["current_clauses"])
    cards = read_tsv(ARTIFACTS["cards"])
    cells = read_tsv(ARTIFACTS["cells"])
    states = read_tsv(ARTIFACTS["states"])
    events = read_tsv(ARTIFACTS["events"])
    statements = read_tsv(ARTIFACTS["statements"])
    seams = read_tsv(ARTIFACTS["seams"])
    directions = read_tsv(ARTIFACTS["directions"])
    root_profiles = read_tsv(ARTIFACTS["roots"])
    register_profiles = read_tsv(ARTIFACTS["registers"])
    result = json.loads(ARTIFACTS["result"].read_text(encoding="utf-8"))
    check("input_counts", [len(src_events), len(src_statements), len(src_pages), len(src_states), len(expansions), len(old_clauses), len(current_clauses)] == [5122, 793, 30, 1656, 95, 4576, 546])
    check("artifact_counts", [len(cards), len(cells), len(states), len(events), len(statements), len(seams), len(directions), len(root_profiles), len(register_profiles)] == [20, 45, 1656, 5122, 793, 4329, 4, 9, 5])
    pages_seen = {row["physical_page"] for row in src_pages + states + events + statements}
    check("sealed_pages_absent", not pages_seen.intersection({"f84", "f84r"}), sorted(pages_seen.intersection({"f84", "f84r"})))
    check("event_ordinals", [int(row["edition_event_ordinal"]) for row in events] == list(range(1, 5123)))
    check("state_ordinals", [int(row["state_edition_ordinal"]) for row in states] == list(range(1, 1657)))
    check("statement_ordinals", [int(row["edition_statement_ordinal"]) for row in statements] == list(range(1, 794)))
    check("seam_ordinals", [int(row["seam_ordinal"]) for row in seams] == list(range(1, 4330)))

    state_by_id = {row["event_id"]: row for row in src_states}
    src_event_by_id = {row["event_id"]: row for row in src_events}
    event_by_id = {row["event_id"]: row for row in events}
    output_state_by_id = {row["event_id"]: row for row in states}
    check("keys_unique_exact", len(state_by_id) == len(output_state_by_id) == 1656 and len(src_event_by_id) == len(event_by_id) == 5122 and set(state_by_id) == set(output_state_by_id))
    check("state_partition_exact", set(state_by_id) == {row["event_id"] for row in src_events if row["state_status"] == "STATE_CARD"})
    expansion_by_cell = {(row["root"], row["register"]): row for row in expansions if row["root"] in ACTIONS}
    check("gdt415_action_cells_exact", len(expansion_by_cell) == 45 and set(expansion_by_cell) == {(root, register) for root in ACTIONS for register in REGISTERS})

    expected_card_specs = []
    for root in ACTIONS:
        groups: dict[str, list[str]] = {}
        for register in REGISTERS:
            groups.setdefault(OWNER[register][root], []).append(register)
        expected_card_specs.extend((root, template, scope) for template, scope in groups.items())
    check("twenty_unique_frame_specs", len(expected_card_specs) == 20, len(expected_card_specs))
    check("card_ids_sequential", [row["action_voice_card_id"] for row in cards] == [f"GDT568-A{i:02d}" for i in range(1, 21)])
    card_id_by_cell = {}
    card_errors = []
    state_sources = [row for row in src_events if row["state_status"] == "STATE_CARD"]
    for output, (root, template, scope) in zip(cards, expected_card_specs):
        card_id = output["action_voice_card_id"]
        for register in scope:
            card_id_by_cell[(register, root)] = card_id
        members = [row for row in state_sources if row["register"] in scope and root in roots(state_by_id[row["event_id"]]["effective_action_roots"])]
        lead = template.split()[0]
        support = sum(has(row["owner_bound_control_clause_de"], lead) for row in members)
        occurrences = sum(roots(state_by_id[row["event_id"]]["effective_action_roots"]).count(root) for row in members)
        expected = {
            "action_root": root, "register_scope": "|".join(scope), "register_cell_count": str(len(scope)),
            "generic_no_argument_de": GENERIC[root][0], "generic_with_argument_de": GENERIC[root][1],
            "owner_no_argument_de": render(template, ""), "owner_with_argument_de": template,
            "target_action_head_de": lead, "requires_frame_change": "YES" if template != GENERIC[root][1] else "NO",
            "state_event_count": str(len(members)), "state_action_occurrence_count": str(occurrences),
            "owner_bound_target_head_support_count": str(support), "support_rate": "1.000000000000",
        }
        bad = {field: [output[field], value] for field, value in expected.items() if output[field] != value}
        if support != len(members):
            bad["support"] = [support, len(members)]
        if bad:
            card_errors.append((card_id, bad))
    check("all_twenty_cards_reconstructed", not card_errors and len(card_id_by_cell) == 45, card_errors[:3])
    check("card_application_support_total", sum(int(row["owner_bound_target_head_support_count"]) for row in cards) == 1834)
    check("card_guards_exact", {row["guard"] for row in cards} == {"ACTION_OWNER_VOICE_ONLY__PORTABLE_ROOT_UNCHANGED"})

    cell_errors = []
    for index, output in enumerate(cells, 1):
        register = REGISTERS[(index - 1) // 9]
        root = ACTIONS[(index - 1) % 9]
        members = [row for row in state_sources if row["register"] == register and root in roots(state_by_id[row["event_id"]]["effective_action_roots"])]
        template = OWNER[register][root]
        lead = template.split()[0]
        expansion = expansion_by_cell[(root, register)]
        expected = {
            "register_action_cell_id": f"GDT568-C{index:02d}", "register": register, "action_root": root,
            "action_voice_card_id": card_id_by_cell[(register, root)],
            "portable_default_de": expansion["portable_default_de"],
            "gdt415_owner_local_expansion_de": expansion["owner_local_expansion_de"],
            "generic_with_argument_de": GENERIC[root][1], "owner_with_argument_de": template,
            "target_action_head_de": lead, "frame_already_exact": "YES" if template == GENERIC[root][1] else "NO",
            "action_head_already_exact": "YES" if lead == GENERIC[root][1].split()[0] else "NO",
            "state_event_count": str(len(members)),
            "state_action_occurrence_count": str(sum(roots(state_by_id[row["event_id"]]["effective_action_roots"]).count(root) for row in members)),
            "owner_bound_target_head_support_count": str(sum(has(row["owner_bound_control_clause_de"], lead) for row in members)),
            "gdt415_source_event_count": expansion["event_count"],
        }
        bad = {field: [output[field], value] for field, value in expected.items() if output[field] != value}
        if bad:
            cell_errors.append(((register, root), bad))
    check("all_45_cells_reconstructed", not cell_errors, cell_errors[:3])
    check("all_45_cells_used", all(int(row["state_event_count"]) > 0 for row in cells))
    check("cell_guards_exact", {row["guard"] for row in cells} == {"REGISTER_CELL_OBSERVED_IN_GDT415__STATE_APPLICATION_SEPARATE"})

    def adapt(source: dict[str, str]) -> tuple[str, str, str, list[str]]:
        state = state_by_id.get(source["event_id"])
        if state is None:
            return source["owner_voice_working_clause_de"], "NOT_APPLICABLE", "NOT_APPLICABLE", []
        generic_chain = chain(state, source["register"], False)
        owner_chain = chain(state, source["register"], True)
        text = source["owner_voice_working_clause_de"]
        applied = []
        if generic_chain != "NONE":
            text = replace_chain(text, generic_chain, owner_chain)
            for root, _ in units(state):
                card_id = card_id_by_cell[(source["register"], root)]
                if card_id not in applied:
                    applied.append(card_id)
        return text, generic_chain, owner_chain, applied

    event_errors = []
    for source, output in zip(src_events, events):
        adapted, generic_chain, owner_chain, applied = adapt(source)
        expected = {
            "event_id": source["event_id"], "statement_id": source["statement_id"],
            "card_ordinal_in_statement": source["card_ordinal_in_statement"], "physical_page": source["physical_page"],
            "register": source["register"], "owner_id": source["owner_id"], "surface": source["surface"],
            "final_context_recipe": source["final_context_recipe"], "state_status": source["state_status"],
            "gdt567_owner_voice_clause_de": source["owner_voice_working_clause_de"],
            "action_voice_working_clause_de": adapted, "owner_bound_control_clause_de": source["owner_bound_control_clause_de"],
            "generic_action_chain_de": generic_chain, "owner_action_chain_de": owner_chain,
            "action_voice_changed": "YES" if adapted != source["owner_voice_working_clause_de"] else "NO",
            "action_voice_equals_owner_bound": "YES" if adapted == source["owner_bound_control_clause_de"] else "NO",
            "action_voice_card_count": str(len(applied)), "action_voice_card_ids": "|".join(applied) or "NONE",
            "state_atom_alignment": source["state_atom_alignment"],
        }
        bad = {field: [output[field], value] for field, value in expected.items() if output[field] != value}
        if bad:
            event_errors.append((source["event_id"], bad))
    check("all_5122_events_reconstructed", not event_errors, event_errors[:3])
    check("nonstate_byte_unchanged", all(row["action_voice_working_clause_de"] == row["gdt567_owner_voice_clause_de"] and row["action_voice_card_ids"] == "NONE" for row in events if row["state_status"] == "NONSTATE_CARD"))
    check("state_action_partition", sum(row["effective_action_roots"] != "NONE" for row in states) == 1643 and sum(row["effective_action_roots"] == "NONE" for row in states) == 13)
    check("state_change_partition", Counter(row["action_voice_changed"] for row in states) == Counter({"NO": 893, "YES": 763}), dict(Counter(row["action_voice_changed"] for row in states)))
    check("state_owner_exact_gain", sum(row["gdt567_owner_voice_clause_de"] == row["owner_bound_control_clause_de"] for row in states) == 20 and sum(row["action_voice_equals_owner_bound"] == "YES" for row in states) == 48)
    check("state_phrase_counts", len({row["gdt567_owner_voice_clause_de"] for row in states}) == 808 and len({row["action_voice_working_clause_de"] for row in states}) == 815)
    check("state_action_use_counts", sum(len(set(roots(row["effective_action_roots"]))) for row in src_states) == 1834 and sum(len(roots(row["effective_action_roots"])) for row in src_states) == 1851)
    check("event_guards_exact", {row["guard"] for row in events} == {"EVENT_RECIPE_ROOTS_AND_BOUNDARY_UNCHANGED__ACTION_VOICE_SEPARATE"})

    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        grouped[event["statement_id"]].append(event)
    statement_errors = []
    for source, output in zip(src_statements, statements):
        members = sorted(grouped[source["statement_id"]], key=lambda row: int(row["card_ordinal_in_statement"]))
        before = " ".join(row["gdt567_owner_voice_clause_de"] for row in members)
        after = " ".join(row["action_voice_working_clause_de"] for row in members)
        control = " ".join(row["owner_bound_control_clause_de"] for row in members)
        expected = {
            "statement_id": source["statement_id"], "physical_page": source["physical_page"], "register": source["register"],
            "owner_id": source["owner_id"], "event_count": source["event_count"], "state_card_count": source["state_card_count"],
            "nonstate_card_count": source["nonstate_card_count"], "statement_mode": source["statement_mode"],
            "changed_state_event_count": str(sum(row["action_voice_changed"] == "YES" for row in members)),
            "action_voice_card_application_count": str(sum(int(row["action_voice_card_count"]) for row in members)),
            "event_ids": source["event_ids"], "surface_sequence": source["surface_sequence"],
            "gdt567_owner_voice_reading_de": before, "action_voice_working_reading_de": after,
            "owner_bound_control_reading_de": control,
            "action_voice_statement_changed": "YES" if after != before else "NO",
            "action_voice_equals_owner_bound": "YES" if after == control else "NO", "end_mode": source["end_mode"],
        }
        bad = {field: [output[field], value] for field, value in expected.items() if output[field] != value}
        if before != source["owner_voice_working_reading_de"] or control != source["owner_bound_control_reading_de"]:
            bad["source_reconstruction"] = True
        if bad:
            statement_errors.append((source["statement_id"], bad))
    check("all_793_statements_reconstructed", not statement_errors, statement_errors[:3])
    check("statement_change_partition", Counter(row["action_voice_statement_changed"] for row in statements) == Counter({"YES": 479, "NO": 314}), dict(Counter(row["action_voice_statement_changed"] for row in statements)))
    check("statement_guards_exact", {row["guard"] for row in statements} == {"STATEMENT_EVENT_ORDER_AND_BOUNDARIES_UNCHANGED"})

    old_by_id = {row["global_running_event_id"]: row for row in old_clauses}
    current_by_id = {row["event_id"]: row for row in current_clauses}

    def nonstate_actions(event_id: str) -> list[str]:
        source = old_by_id.get(event_id) or current_by_id.get(event_id)
        explicit = roots(source["explicit_action_roots"])
        return explicit or roots(source["inherited_action_root"])

    expected_pairs = []
    for statement in src_statements:
        ids = statement["event_ids"].split("|")
        expected_pairs.extend(zip(ids, ids[1:]))
    check("all_adjacencies_exact", [(row["left_event_id"], row["right_event_id"]) for row in seams] == expected_pairs)
    direction_map = {("NONSTATE_CARD", "NONSTATE_CARD"): "NONSTATE_TO_NONSTATE", ("NONSTATE_CARD", "STATE_CARD"): "NONSTATE_TO_STATE", ("STATE_CARD", "NONSTATE_CARD"): "STATE_TO_NONSTATE", ("STATE_CARD", "STATE_CARD"): "STATE_TO_STATE"}
    seam_errors = []
    for output, (left_id, right_id) in zip(seams, expected_pairs):
        left, right = event_by_id[left_id], event_by_id[right_id]
        direction = direction_map[(left["state_status"], right["state_status"])]
        mixed = left["state_status"] != right["state_status"]
        contacts = []
        frame_before = frame_after = head_before = head_after = 0
        state_endpoint = None
        if mixed:
            state_endpoint = left if left["state_status"] == "STATE_CARD" else right
            nonstate = right if state_endpoint is left else left
            state_actions = set(roots(state_by_id[state_endpoint["event_id"]]["effective_action_roots"]))
            for root in ACTIONS:
                if root not in state_actions.intersection(nonstate_actions(nonstate["event_id"])):
                    continue
                template = OWNER[state_endpoint["register"]][root]
                target_head = template.split()[0]
                if not has(nonstate["action_voice_working_clause_de"], target_head):
                    continue
                contacts.append(f"{root}:{target_head}")
                frame_before += int(template == GENERIC[root][1])
                frame_after += 1
                head_before += int(target_head == GENERIC[root][1].split()[0])
                head_after += 1
        expected = {
            "direction": direction, "mixed_state_nonstate": "YES" if mixed else "NO",
            "state_endpoint_event_id": state_endpoint["event_id"] if state_endpoint else "NOT_APPLICABLE",
            "state_endpoint_changed": state_endpoint["action_voice_changed"] if state_endpoint else "NOT_APPLICABLE",
            "shared_action_contacts": "|".join(contacts) or "NONE", "shared_action_contact_count": str(len(contacts)),
            "full_action_frame_exact_before": str(frame_before), "full_action_frame_exact_after": str(frame_after),
            "action_head_exact_before": str(head_before), "action_head_exact_after": str(head_after),
            "left_gdt567_clause_de": left["gdt567_owner_voice_clause_de"], "right_gdt567_clause_de": right["gdt567_owner_voice_clause_de"],
            "left_action_voice_clause_de": left["action_voice_working_clause_de"], "right_action_voice_clause_de": right["action_voice_working_clause_de"],
        }
        bad = {field: [output[field], value] for field, value in expected.items() if output[field] != value}
        if bad:
            seam_errors.append((left_id, right_id, bad))
    check("all_4329_seams_reconstructed", not seam_errors, seam_errors[:3])
    direction_counts = Counter(row["direction"] for row in seams)
    check("direction_counts", direction_counts == Counter({"NONSTATE_TO_NONSTATE": 2426, "NONSTATE_TO_STATE": 969, "STATE_TO_NONSTATE": 611, "STATE_TO_STATE": 323}))
    mixed = [row for row in seams if row["mixed_state_nonstate"] == "YES"]
    check("mixed_and_contact_counts", len(mixed) == 1580 and sum(row["shared_action_contacts"] != "NONE" for row in mixed) == 854 and sum(int(row["shared_action_contact_count"]) for row in mixed) == 866)
    check("full_frame_gain", sum(int(row["full_action_frame_exact_before"]) for row in mixed) == 517 and sum(int(row["full_action_frame_exact_after"]) for row in mixed) == 866)
    check("action_head_gain", sum(int(row["action_head_exact_before"]) for row in mixed) == 730 and sum(int(row["action_head_exact_after"]) for row in mixed) == 866)
    check("seam_guards_exact", {row["guard"] for row in seams} == {"ADJACENCY_ONLY__ACTION_FRAME_DOES_NOT_MERGE_EVENTS"})
    direction_lookup = {row["direction"]: row for row in directions}
    check("direction_profiles_exact", set(direction_lookup) == set(direction_counts) and all(int(direction_lookup[key]["seam_count"]) == value for key, value in direction_counts.items()))

    root_lookup = {row["action_root"]: row for row in root_profiles}
    expected_root_contacts = {"OK": (169, 31, 161), "CH": (160, 97, 124), "SH": (136, 113, 136), "K": (114, 0, 33), "S": (81, 81, 81), "CHD": (83, 83, 83), "T": (70, 63, 63), "R": (20, 16, 16), "P": (33, 33, 33)}
    check("root_profile_contacts_exact", set(root_lookup) == set(ACTIONS) and all((int(root_lookup[root]["shared_action_contact_count"]), int(root_lookup[root]["full_action_frame_exact_before"]), int(root_lookup[root]["action_head_exact_before"])) == values for root, values in expected_root_contacts.items()), root_lookup)
    check("root_profile_totals", sum(int(row["shared_action_contact_count"]) for row in root_profiles) == 866 and sum(int(row["full_action_frame_exact_before"]) for row in root_profiles) == 517 and sum(int(row["action_head_exact_before"]) for row in root_profiles) == 730)
    check("register_profiles_exact", [row["register"] for row in register_profiles] == list(REGISTERS) and sum(int(row["state_event_count"]) for row in register_profiles) == 1656 and sum(int(row["changed_state_event_count"]) for row in register_profiles) == 763)

    expected_metrics = {
        "owner_action_voice_card_count": 20, "register_action_cell_count": 45, "gdt415_action_cell_count": 45,
        "state_event_count": 1656, "action_bearing_state_event_count": 1643, "actionless_state_event_count": 13,
        "state_event_root_use_count": 1834, "state_action_occurrence_count": 1851,
        "owner_bound_target_head_supported_event_root_use_count": 1834, "changed_state_event_count": 763,
        "unchanged_state_event_count": 893, "owner_voice_equals_owner_bound_before_count": 20,
        "action_voice_equals_owner_bound_after_count": 48, "distinct_owner_voice_state_clause_count": 808,
        "distinct_action_voice_state_clause_count": 815, "changed_statement_count": 479,
        "unchanged_statement_count": 314, "changed_physical_page_count": 27,
        "complete_event_count": 5122, "complete_statement_count": 793, "within_statement_seam_count": 4329,
        "mixed_state_nonstate_seam_count": 1580, "shared_action_contact_seam_count": 854,
        "shared_action_contact_count": 866, "full_action_frame_exact_before": 517,
        "full_action_frame_exact_after": 866, "action_head_exact_before": 730, "action_head_exact_after": 866,
        "new_pages": 0, "new_events": 0, "new_statements": 0, "new_surfaces": 0,
        "new_recipes": 0, "new_root_values": 0,
    }
    check("result_metrics_exact", all(result.get(key) == value for key, value in expected_metrics.items()), {key: result.get(key) for key in expected_metrics})
    check("result_status_exact", result.get("status") == STATUS, result.get("status"))
    check("input_hashes_exact", result.get("input_sha256") == {name: sha256(path) for name, path in INPUTS.items()})
    book = ARTIFACTS["book"].read_text(encoding="utf-8")
    headings = [line[3:] for line in book.splitlines() if line.startswith("## ")]
    check("book_metrics_present", all(needle in book for needle in ("Zwanzig kleine Verbkarten", "763/1.656", "517 → 866", "730 → 866")))
    check("book_all_pages_once", headings == [row["physical_page"] for row in src_pages], headings)
    check("book_zero_pages", book.count("Lokalregisterseite bleibt sichtbar") == 2)
    check("book_all_statements", all(row["statement_id"] in book for row in statements))

    before = {name: sha256(path) for name, path in ARTIFACTS.items()}
    replay = subprocess.run([sys.executable, str(RUNNER)], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
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
