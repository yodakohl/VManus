#!/usr/bin/env python3
"""Render four explicit action/argument carry modes over the GDT568 edition."""

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
BASE = ROOT / "experiments/yolo/gdt569_four_context_carry_voice_frames"
OUT = BASE / "artifacts"
G568 = ROOT / "experiments/yolo/gdt568_twenty_owner_action_voice_frames/artifacts"
G567 = ROOT / "experiments/yolo/gdt567_owner_voice_seam_adapter/artifacts"
G566 = ROOT / "experiments/yolo/gdt566_complete_thirty_page_prose_working_edition/artifacts"
G565 = ROOT / "experiments/yolo/gdt565_state_microphrase_template_generator/artifacts"
G562 = ROOT / "experiments/yolo/gdt562_thirty_page_actionless_state_role_reader/artifacts"
G416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts"
G539 = ROOT / "experiments/yolo/gdt539_four_page_contextual_statement_edition/artifacts"
INPUTS = {
    "action_events": G568 / "gdt568_5122_action_voice_event_edition.tsv",
    "action_statements": G568 / "gdt568_793_action_voice_statement_edition.tsv",
    "page_profiles": G566 / "gdt566_30_page_edition_profiles.tsv",
    "state_replay": G565 / "gdt565_1656_template_replay.tsv",
    "argument_cards": G567 / "gdt567_39_owner_voice_adapter_cards.tsv",
    "action_provenance": G562 / "gdt562_693_action_provenance.tsv",
    "old_context": G416 / "gdt416_4576_imperative_clauses.tsv",
    "current_context": G539 / "gdt539_546_contextual_prose_events.tsv",
}

MODE_BY_CARRY = {
    (False, False): ("GDT569-C01", "LOCAL_EXPLICIT"),
    (False, True): ("GDT569-C02", "ARGUMENT_CARRY"),
    (True, False): ("GDT569-C03", "ACTION_CARRY"),
    (True, True): ("GDT569-C04", "ACTION_AND_ARGUMENT_CARRY"),
}
MODE_DESCRIPTIONS = {
    "LOCAL_EXPLICIT": "Handlung und Argument lokal sichtbar; GDT568-Satz bleibt unverändert",
    "ARGUMENT_CARRY": "lokale Handlung mit demselben bereits aktiven Argument",
    "ACTION_CARRY": "Handlung aus dem laufenden Gang mit lokal sichtbarem Argument",
    "ACTION_AND_ARGUMENT_CARRY": "Handlung aus dem laufenden Gang mit demselben aktiven Argument",
}
SCOPE_FRAMES = {
    "WEITER": ("GDT569-S01", "Weiter im laufenden Gang: {clause}"),
    "DANACH": ("GDT569-S02", "Danach im laufenden Gang: {clause}"),
    "BARE": ("GDT569-S03", "Im laufenden Gang: {clause}"),
}
STATUS = (
    "PASS_4_CONTEXT_MODES__693_ACTION_CARRIES__1208_ARGUMENT_CARRIES__"
    "1348_PRIOR_ARGUMENT_REALIZATIONS__1442_STATE_CLAUSES_CONTEXT_EXPLICIT__"
    "19_CARRIED_ARGUMENT_CELLS__ZERO_ROOT_CHANGE"
)


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


def roots(value: str) -> list[str]:
    return [] if value in ("", "NONE") else value.split("|")


def join_arguments(parts: list[str]) -> str:
    if len(parts) == 1:
        return parts[0]
    return ", ".join(parts[:-1]) + " und " + parts[-1]


def carried_form(phrase: str) -> str:
    if phrase.startswith("die beiden "):
        return "dieselben beiden " + phrase[len("die beiden "):]
    if phrase.startswith("den "):
        return "denselben " + phrase[len("den "):]
    if phrase.startswith("die "):
        return "dieselbe " + phrase[len("die "):]
    raise RuntimeError(f"No carried-argument article rule for {phrase!r}")


def replace_phrase(text: str, old: str, new: str) -> str:
    match = re.search(re.escape(old), text, re.IGNORECASE)
    if match is None:
        raise RuntimeError(f"Phrase not found: {old!r} in {text!r}")
    replacement = new[0].upper() + new[1:] if match.group()[0].isupper() else new
    return text[:match.start()] + replacement + text[match.end():]


def add_action_scope(clause: str) -> tuple[str, str, str]:
    if clause.startswith("Weiter: "):
        kind = "WEITER"
        core = clause[len("Weiter: "):]
        output = "Weiter im laufenden Gang: " + core
    elif clause.startswith("Danach: "):
        kind = "DANACH"
        core = clause[len("Danach: "):]
        output = "Danach im laufenden Gang: " + core
    else:
        kind = "BARE"
        core = clause
        output = "Im laufenden Gang: " + core
    return kind, SCOPE_FRAMES[kind][0], output


def control_action_witness(text: str) -> bool:
    lower = text.lower()
    return any(
        phrase in lower
        for phrase in (
            "im laufenden gang",
            "im laufenden satz",
            "führe fort",
            "führe 2-mal fort",
            "schließe den schritt",
        )
    )


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    source_events = read_tsv(INPUTS["action_events"])
    source_statements = read_tsv(INPUTS["action_statements"])
    pages = read_tsv(INPUTS["page_profiles"])
    state_source = read_tsv(INPUTS["state_replay"])
    adapter_cards = read_tsv(INPUTS["argument_cards"])
    action_provenance = read_tsv(INPUTS["action_provenance"])
    old_context = read_tsv(INPUTS["old_context"])
    current_context = read_tsv(INPUTS["current_context"])
    observed_counts = [
        len(source_events), len(source_statements), len(pages), len(state_source),
        len(adapter_cards), len(action_provenance), len(old_context), len(current_context),
    ]
    if observed_counts != [5122, 793, 30, 1656, 39, 693, 4576, 546]:
        raise RuntimeError(f"Input count drift: {observed_counts}")

    state_by_id = {row["event_id"]: row for row in state_source}
    source_event_by_id = {row["event_id"]: row for row in source_events}
    if set(state_by_id) != {
        row["event_id"] for row in source_events if row["state_status"] == "STATE_CARD"
    }:
        raise RuntimeError("State partition drift")

    metadata: dict[str, tuple[str, dict[str, str]]] = {
        row["global_running_event_id"]: ("OLD26_GDT407", row) for row in old_context
    }
    metadata.update({row["event_id"]: ("CURRENT4_GDT515", row) for row in current_context})
    if any(event_id not in metadata for event_id in state_by_id):
        raise RuntimeError("Missing context metadata")

    argument_cards = [row for row in adapter_cards if row["card_class"] == "ARGUMENT_OWNER_VOICE"]
    argument_by_cell = {(row["register_scope"], row["root_or_trigger"]): row for row in argument_cards}
    if len(argument_cards) != 19 or len(argument_by_cell) != 19:
        raise RuntimeError("Argument-card inventory drift")

    action_provenance_by_id = {row["event_id"]: row for row in action_provenance}
    inherited_action_ids = {
        event_id for event_id, (_, row) in metadata.items()
        if event_id in state_by_id and row["inherited_action_root"] not in ("", "NONE")
    }
    inherited_argument_ids = {
        event_id for event_id, (_, row) in metadata.items()
        if event_id in state_by_id and row["inherited_argument_root"] not in ("", "NONE")
    }
    if inherited_action_ids != set(action_provenance_by_id) or len(inherited_argument_ids) != 1208:
        raise RuntimeError("Carry provenance drift")

    def argument_phrase(state: dict[str, str], carry: bool) -> str:
        values = roots(state["effective_argument_roots"])
        if not values:
            return ""
        register = state["register"]
        if values == ["Y", "Y"]:
            base = argument_by_cell[(register, "Y")]["double_y_phrase_de"]
            return carried_form(base) if carry else base
        pieces = [argument_by_cell[(register, root)]["owner_voice_phrase_de"] for root in values]
        if carry:
            pieces = [carried_form(piece) for piece in pieces]
        return join_arguments(pieces)

    state_rows: list[dict[str, object]] = []
    for state in state_source:
        event_id = state["event_id"]
        source = source_event_by_id[event_id]
        cohort, meta = metadata[event_id]
        action_carry = meta["inherited_action_root"] not in ("", "NONE")
        argument_carry = meta["inherited_argument_root"] not in ("", "NONE")
        card_id, mode = MODE_BY_CARRY[(action_carry, argument_carry)]
        before = source["action_voice_working_clause_de"]
        after = before
        explicit_argument = argument_phrase(state, False)
        prior_argument = argument_phrase(state, True) if argument_carry else "NOT_APPLICABLE"
        argument_realizations = 0
        new_action_chain = source["owner_action_chain_de"]
        if argument_carry:
            if source["owner_action_chain_de"] in ("", "NONE", "NOT_APPLICABLE"):
                raise RuntimeError(f"Argument carry without action chain at {event_id}")
            argument_realizations = source["owner_action_chain_de"].count(explicit_argument)
            if argument_realizations < 1:
                raise RuntimeError(f"Argument phrase missing from action chain at {event_id}")
            new_action_chain = source["owner_action_chain_de"].replace(explicit_argument, prior_argument)
            after = replace_phrase(after, source["owner_action_chain_de"], new_action_chain)

        scope_kind = scope_card_id = scope_phrase = "NOT_APPLICABLE"
        if action_carry:
            scope_kind, scope_card_id, after = add_action_scope(after)
            scope_phrase = SCOPE_FRAMES[scope_kind][1]
        action_prov = action_provenance_by_id.get(event_id)
        action_source_type = (
            action_prov["action_source_type"] if action_prov is not None
            else "VISIBLE_ACTION_IN_CARD" if state["effective_action_roots"] != "NONE"
            else "NO_ACTION"
        )
        action_source_event_id = action_prov["action_source_event_id"] if action_prov else event_id
        action_source_distance = action_prov["source_card_distance"] if action_prov else "0"
        argument_source_type = "CONTEXT_CARRY" if argument_carry else (
            "VISIBLE_ARGUMENT_IN_CARD" if state["effective_argument_roots"] != "NONE" else "NO_ARGUMENT"
        )
        control = source["owner_bound_control_clause_de"]
        state_rows.append({
            "state_edition_ordinal": len(state_rows) + 1,
            "event_id": event_id,
            "statement_id": state["statement_id"],
            "physical_page": state["physical_page"],
            "register": state["register"],
            "owner_id": source["owner_id"],
            "cohort": cohort,
            "surface": source["surface"],
            "final_context_recipe": source["final_context_recipe"],
            "state_marker_sequence": state["state_marker_sequence"],
            "effective_action_roots": state["effective_action_roots"],
            "effective_argument_roots": state["effective_argument_roots"],
            "context_mode_card_id": card_id,
            "context_mode": mode,
            "action_carry": "YES" if action_carry else "NO",
            "action_source_type": action_source_type,
            "action_source_event_id": action_source_event_id,
            "action_source_card_distance": action_source_distance,
            "action_scope_frame_id": scope_card_id,
            "action_scope_kind": scope_kind,
            "action_scope_phrase_de": scope_phrase,
            "argument_carry": "YES" if argument_carry else "NO",
            "argument_source_type": argument_source_type,
            "inherited_argument_root": meta["inherited_argument_root"],
            "explicit_argument_phrase_de": explicit_argument or "NONE",
            "carried_argument_phrase_de": prior_argument,
            "carried_argument_realization_count": argument_realizations,
            "control_prior_marker_count": control.count("[wie zuvor]"),
            "control_action_context_witness": "YES" if action_carry and control_action_witness(control) else (
                "NOT_APPLICABLE" if not action_carry else "NO"
            ),
            "gdt568_action_voice_clause_de": before,
            "context_voice_working_clause_de": after,
            "owner_bound_control_clause_de": control,
            "gdt568_owner_action_chain_de": source["owner_action_chain_de"],
            "context_voice_action_chain_de": new_action_chain,
            "context_voice_changed": "YES" if after != before else "NO",
            "state_atom_alignment": source["state_atom_alignment"],
            "guard": "CONTEXT_VOICE_ONLY__ROOTS_RECIPES_AND_BOUNDARY_UNCHANGED",
        })

    state_by_output_id = {row["event_id"]: row for row in state_rows}
    mode_rows: list[dict[str, object]] = []
    for flags, (card_id, mode) in MODE_BY_CARRY.items():
        members = [row for row in state_rows if row["context_mode"] == mode]
        mode_rows.append({
            "context_mode_card_id": card_id,
            "context_mode": mode,
            "action_carry": "YES" if flags[0] else "NO",
            "argument_carry": "YES" if flags[1] else "NO",
            "working_reading_rule_de": MODE_DESCRIPTIONS[mode],
            "state_event_count": len(members),
            "statement_count": len({row["statement_id"] for row in members}),
            "physical_page_count": len({row["physical_page"] for row in members}),
            "changed_state_event_count": sum(row["context_voice_changed"] == "YES" for row in members),
            "control_action_context_witness_count": sum(row["control_action_context_witness"] == "YES" for row in members),
            "control_prior_marker_event_count": sum(int(row["control_prior_marker_count"]) > 0 for row in members),
            "guard": "FOUR_WAY_CONTEXT_MODE__NO_NEW_WRITTEN_ATOM",
        })

    scope_rows: list[dict[str, object]] = []
    for kind, (card_id, phrase) in SCOPE_FRAMES.items():
        members = [row for row in state_rows if row["action_scope_kind"] == kind]
        scope_rows.append({
            "action_scope_frame_id": card_id,
            "action_scope_kind": kind,
            "scope_frame_de": phrase,
            "action_carry_event_count": len(members),
            "same_statement_visible_action_count": sum(
                row["action_source_type"] == "SAME_STATEMENT_VISIBLE_ACTION" for row in members
            ),
            "owner_context_default_action_count": sum(
                row["action_source_type"] == "OWNER_CONTEXT_DEFAULT_ACTION" for row in members
            ),
            "control_context_witness_count": sum(row["control_action_context_witness"] == "YES" for row in members),
            "example_event_ids": "|".join(str(row["event_id"]) for row in members[:8]),
            "guard": "ACTION_CARRY_SCOPE_ONLY__ACTION_ROOT_UNCHANGED",
        })

    argument_form_rows: list[dict[str, object]] = []
    for card in argument_cards:
        register = card["register_scope"]
        root = card["root_or_trigger"]
        members = [
            row for row in state_rows
            if row["register"] == register and row["inherited_argument_root"] == root
        ]
        explicit = card["owner_voice_phrase_de"]
        prior = carried_form(explicit)
        argument_form_rows.append({
            "carried_argument_card_id": f"GDT569-A{len(argument_form_rows) + 1:02d}",
            "register": register,
            "argument_root": root,
            "explicit_argument_phrase_de": explicit,
            "carried_argument_phrase_de": prior,
            "argument_carry_event_count": len(members),
            "carried_argument_realization_count": sum(int(row["carried_argument_realization_count"]) for row in members),
            "control_prior_marker_event_count": sum(int(row["control_prior_marker_count"]) > 0 for row in members),
            "control_prior_marker_occurrence_count": sum(int(row["control_prior_marker_count"]) for row in members),
            "example_event_ids": "|".join(str(row["event_id"]) for row in members[:8]),
            "guard": "ARTICLE_REALIZATION_OF_CONTEXT_CARRY__ARGUMENT_ROOT_UNCHANGED",
        })

    action_carry_rows: list[dict[str, object]] = []
    for row in state_rows:
        if row["action_carry"] != "YES":
            continue
        prov = action_provenance_by_id[str(row["event_id"])]
        action_carry_rows.append({
            "action_carry_ordinal": len(action_carry_rows) + 1,
            "event_id": row["event_id"],
            "statement_id": row["statement_id"],
            "physical_page": row["physical_page"],
            "register": row["register"],
            "surface": row["surface"],
            "final_context_recipe": row["final_context_recipe"],
            "inherited_action_root": prov["inherited_action_root"],
            "inherited_action_value_de": prov["inherited_action_value_de"],
            "action_source_type": prov["action_source_type"],
            "action_source_event_id": prov["action_source_event_id"],
            "source_card_distance": prov["source_card_distance"],
            "action_scope_frame_id": row["action_scope_frame_id"],
            "action_scope_kind": row["action_scope_kind"],
            "control_action_context_witness": row["control_action_context_witness"],
            "context_voice_working_clause_de": row["context_voice_working_clause_de"],
            "guard": "GDT562_ACTION_PROVENANCE_RETAINED__SCOPE_RENDERING_ONLY",
        })

    argument_carry_rows: list[dict[str, object]] = []
    for row in state_rows:
        if row["argument_carry"] != "YES":
            continue
        argument_carry_rows.append({
            "argument_carry_ordinal": len(argument_carry_rows) + 1,
            "event_id": row["event_id"],
            "statement_id": row["statement_id"],
            "physical_page": row["physical_page"],
            "register": row["register"],
            "surface": row["surface"],
            "final_context_recipe": row["final_context_recipe"],
            "inherited_argument_root": row["inherited_argument_root"],
            "explicit_argument_phrase_de": row["explicit_argument_phrase_de"],
            "carried_argument_phrase_de": row["carried_argument_phrase_de"],
            "carried_argument_realization_count": row["carried_argument_realization_count"],
            "control_prior_marker_count": row["control_prior_marker_count"],
            "context_voice_working_clause_de": row["context_voice_working_clause_de"],
            "guard": "CONTEXT_ARGUMENT_PROVENANCE_RETAINED__ROOT_UNCHANGED",
        })

    event_rows: list[dict[str, object]] = []
    for source in source_events:
        state = state_by_output_id.get(source["event_id"])
        after = state["context_voice_working_clause_de"] if state else source["action_voice_working_clause_de"]
        event_rows.append({
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
            "gdt568_action_voice_clause_de": source["action_voice_working_clause_de"],
            "context_voice_working_clause_de": after,
            "owner_bound_control_clause_de": source["owner_bound_control_clause_de"],
            "context_mode": state["context_mode"] if state else "NOT_APPLICABLE",
            "action_carry": state["action_carry"] if state else "NOT_APPLICABLE",
            "argument_carry": state["argument_carry"] if state else "NOT_APPLICABLE",
            "context_voice_changed": "YES" if after != source["action_voice_working_clause_de"] else "NO",
            "state_atom_alignment": source["state_atom_alignment"],
            "guard": "COMPLETE_EVENT_ORDER_AND_NONSTATE_TEXT_UNCHANGED",
        })

    events_by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        events_by_statement[str(row["statement_id"])].append(row)
    statement_rows: list[dict[str, object]] = []
    for source in source_statements:
        members = sorted(events_by_statement[source["statement_id"]], key=lambda row: int(row["card_ordinal_in_statement"]))
        before = " ".join(str(row["gdt568_action_voice_clause_de"]) for row in members)
        after = " ".join(str(row["context_voice_working_clause_de"]) for row in members)
        control = " ".join(str(row["owner_bound_control_clause_de"]) for row in members)
        if before != source["action_voice_working_reading_de"] or control != source["owner_bound_control_reading_de"]:
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
            "context_changed_state_event_count": sum(row["context_voice_changed"] == "YES" for row in members),
            "action_carry_event_count": sum(row["action_carry"] == "YES" for row in members),
            "argument_carry_event_count": sum(row["argument_carry"] == "YES" for row in members),
            "event_ids": source["event_ids"],
            "surface_sequence": source["surface_sequence"],
            "gdt568_action_voice_reading_de": before,
            "context_voice_working_reading_de": after,
            "owner_bound_control_reading_de": control,
            "context_voice_statement_changed": "YES" if after != before else "NO",
            "end_mode": source["end_mode"],
            "guard": "STATEMENT_EVENT_ORDER_AND_BOUNDARIES_UNCHANGED",
        })

    page_rows: list[dict[str, object]] = []
    for page in pages:
        page_events = [row for row in event_rows if row["physical_page"] == page["physical_page"]]
        page_states = [row for row in state_rows if row["physical_page"] == page["physical_page"]]
        page_statements = [row for row in statement_rows if row["physical_page"] == page["physical_page"]]
        page_rows.append({
            "page_ordinal": page["page_ordinal"],
            "physical_page": page["physical_page"],
            "registers": page["registers"],
            "event_count": len(page_events),
            "statement_count": len(page_statements),
            "state_event_count": len(page_states),
            "local_explicit_state_event_count": sum(row["context_mode"] == "LOCAL_EXPLICIT" for row in page_states),
            "argument_carry_event_count": sum(row["argument_carry"] == "YES" for row in page_states),
            "action_carry_event_count": sum(row["action_carry"] == "YES" for row in page_states),
            "context_changed_state_event_count": sum(row["context_voice_changed"] == "YES" for row in page_states),
            "page_status": page["page_status"],
            "guard": "ADMITTED_PAGE_ORDER_UNCHANGED",
        })

    mode_counts = Counter(str(row["context_mode"]) for row in state_rows)
    result = {
        "status": STATUS,
        "context_mode_card_count": len(mode_rows),
        "local_explicit_state_event_count": mode_counts["LOCAL_EXPLICIT"],
        "argument_only_carry_event_count": mode_counts["ARGUMENT_CARRY"],
        "action_only_carry_event_count": mode_counts["ACTION_CARRY"],
        "action_and_argument_carry_event_count": mode_counts["ACTION_AND_ARGUMENT_CARRY"],
        "action_carry_event_count": len(action_carry_rows),
        "same_statement_visible_action_carry_count": sum(
            row["action_source_type"] == "SAME_STATEMENT_VISIBLE_ACTION" for row in action_carry_rows
        ),
        "owner_context_default_action_carry_count": sum(
            row["action_source_type"] == "OWNER_CONTEXT_DEFAULT_ACTION" for row in action_carry_rows
        ),
        "action_scope_frame_count": len(scope_rows),
        "argument_carry_event_count": len(argument_carry_rows),
        "carried_argument_cell_count": len(argument_form_rows),
        "carried_argument_realization_count": sum(int(row["carried_argument_realization_count"]) for row in argument_carry_rows),
        "control_prior_marker_event_count": sum(int(row["control_prior_marker_count"]) > 0 for row in state_rows),
        "control_prior_marker_occurrence_count": sum(int(row["control_prior_marker_count"]) for row in state_rows),
        "control_action_context_witness_count": sum(row["control_action_context_witness"] == "YES" for row in state_rows),
        "changed_state_event_count": sum(row["context_voice_changed"] == "YES" for row in state_rows),
        "unchanged_state_event_count": sum(row["context_voice_changed"] == "NO" for row in state_rows),
        "changed_statement_count": sum(row["context_voice_statement_changed"] == "YES" for row in statement_rows),
        "unchanged_statement_count": sum(row["context_voice_statement_changed"] == "NO" for row in statement_rows),
        "changed_physical_page_count": sum(int(row["context_changed_state_event_count"]) > 0 for row in page_rows),
        "distinct_gdt568_state_clause_count": len({row["gdt568_action_voice_clause_de"] for row in state_rows}),
        "distinct_context_voice_state_clause_count": len({row["context_voice_working_clause_de"] for row in state_rows}),
        "state_event_count": len(state_rows),
        "nonstate_event_count": sum(row["state_status"] == "NONSTATE_CARD" for row in event_rows),
        "nonstate_byte_unchanged_count": sum(
            row["state_status"] == "NONSTATE_CARD" and row["gdt568_action_voice_clause_de"] == row["context_voice_working_clause_de"]
            for row in event_rows
        ),
        "complete_event_count": len(event_rows),
        "complete_statement_count": len(statement_rows),
        "complete_page_count": len(page_rows),
        "new_pages": 0,
        "new_events": 0,
        "new_statements": 0,
        "new_surfaces": 0,
        "new_recipes": 0,
        "new_root_values": 0,
        "input_sha256": {name: sha256(path) for name, path in INPUTS.items()},
    }

    write_tsv(OUT / "gdt569_4_context_carry_cards.tsv", mode_rows)
    write_tsv(OUT / "gdt569_3_action_scope_frames.tsv", scope_rows)
    write_tsv(OUT / "gdt569_19_carried_argument_forms.tsv", argument_form_rows)
    write_tsv(OUT / "gdt569_693_action_carry_provenance.tsv", action_carry_rows)
    write_tsv(OUT / "gdt569_1208_argument_carry_provenance.tsv", argument_carry_rows)
    write_tsv(OUT / "gdt569_1656_context_voice_state_clauses.tsv", state_rows)
    write_tsv(OUT / "gdt569_5122_context_voice_event_edition.tsv", event_rows)
    write_tsv(OUT / "gdt569_793_context_voice_statement_edition.tsv", statement_rows)
    write_tsv(OUT / "gdt569_30_page_context_voice_profiles.tsv", page_rows)

    statements_by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in statement_rows:
        statements_by_page[str(row["physical_page"])].append(row)
    book = [
        "# GDT569 – kontextsichtbare 30-Seiten-Arbeitsausgabe",
        "",
        "Vier Kontextlagen machen getragene Handlung und getragenes Argument in der Prosa sichtbar.",
        "",
        "```text",
        "214 lokal explizit | 749 nur Argument getragen | 234 nur Handlung getragen | 459 beides",
        "693 Handlungsträger | 1.208 Argumentträger | 1.442 angepasste Zustandszeilen",
        "```",
        "",
    ]
    for page in pages:
        book += [f"## {page['physical_page']}", ""]
        members = statements_by_page[page["physical_page"]]
        if not members:
            book += ["Keine laufende Prosa; zugelassene Lokalregisterseite bleibt sichtbar.", ""]
            continue
        for statement in members:
            book += [
                f"### {statement['statement_id']} · {statement['statement_mode']} · {statement['event_count']} Karten",
                "",
                f"**Formen:** {statement['surface_sequence']}",
                "",
                str(statement["context_voice_working_reading_de"]),
                "",
            ]
    (OUT / "GDT569_CONTEXT_VOICE_THIRTY_PAGE_EDITION.md").write_text("\n".join(book), encoding="utf-8")
    (OUT / "gdt569_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
