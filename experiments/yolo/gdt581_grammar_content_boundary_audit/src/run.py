#!/usr/bin/env python3
"""Build GDT581's complete grammar/content-boundary atlas."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from boundary_lib import (
    ACTION_NOMINALS,
    ACTION_ROOTS,
    BASE,
    GRADE_ROOTS,
    LOCAL_MACRO_ROOTS,
    OBJECT_ROOTS,
    RELATION_ROOTS,
    ROOT,
    RUNNING_MODIFIER_ROOTS,
    STATE_ROOTS,
    STATUS,
    action_positions,
    atoms,
    content_boundary_class,
    extract_name_slots,
    nearest_action,
    nth_position,
    occurrence_rank,
    read_tsv,
    sha256,
    unique_index,
    write_tsv,
)


def artifact_dir(slug: str) -> Path:
    return ROOT / "experiments/yolo" / slug / "artifacts"


G407 = artifact_dir("gdt407_unified_twenty_six_page_workshop_edition")
G416 = artifact_dir("gdt416_owner_local_imperative_sentence_compiler")
G471 = artifact_dir("gdt471_empirical_address_shell_phrasebook")
G472 = artifact_dir("gdt472_complete_address_template_dictionary")
G479 = artifact_dir("gdt479_definitive_local_microrecord_edition")
G513 = artifact_dir("gdt513_remaining_local_group_semantic_census")
G515 = artifact_dir("gdt515_second_random_four_page_full_admission")
G539 = artifact_dir("gdt539_four_page_contextual_statement_edition")
G558 = artifact_dir("gdt558_grade_carrier_envelope_grammar")
G567 = artifact_dir("gdt567_owner_voice_seam_adapter")
G568 = artifact_dir("gdt568_twenty_owner_action_voice_frames")
G577 = artifact_dir("gdt577_interrupted_modifier_attachment_topology")
G579 = artifact_dir("gdt579_mixed_outer_inner_scope_voice")
G580 = artifact_dir("gdt580_adjacent_relation_resumption_voice")

INPUTS = {
    "gdt580_events": G580 / "gdt580_5122_resumption_voice_event_edition.tsv",
    "gdt580_statements": G580 / "gdt580_793_resumption_voice_statement_edition.tsv",
    "gdt580_pages": G580 / "gdt580_30_page_resumption_voice_profiles.tsv",
    "gdt580_slots": G580 / "gdt580_6_written_slot_spans.tsv",
    "gdt579_scope_slots": G579 / "gdt579_34_scope_slot_assignments.tsv",
    "gdt577_repeat_slots": G577 / "gdt577_125_slot_head_assignments.tsv",
    "gdt407_attachments": G407 / "gdt407_5051_attachment_edition.tsv",
    "gdt515_attachments": G515 / "gdt515_factorized_attachments.tsv",
    "gdt515_old_events": G515 / "gdt515_5122_running_event_edition.tsv",
    "gdt416_clauses": G416 / "gdt416_4576_imperative_clauses.tsv",
    "gdt416_inherited_actions": G416 / "gdt416_inherited_action_audit.tsv",
    "gdt416_inherited_arguments": G416 / "gdt416_inherited_argument_audit.tsv",
    "gdt539_context_events": G539 / "gdt539_546_contextual_prose_events.tsv",
    "gdt558_grade_assignments": G558 / "gdt558_333_grade_carrier_assignments.tsv",
    "gdt558_grade_hazards": G558 / "gdt558_18_false_inheritance_hazards.tsv",
    "gdt567_voice_cards": G567 / "gdt567_39_owner_voice_adapter_cards.tsv",
    "gdt568_action_cells": G568 / "gdt568_45_register_action_cells.tsv",
    "gdt515_local_cards": G515 / "gdt515_744_local_group_edition.tsv",
    "gdt479_local_events": G479 / "gdt479_183_definitive_local_events.tsv",
    "gdt513_local_events": G513 / "gdt513_510_remaining_local_working_edition.tsv",
    "gdt515_local_51": G515 / "gdt515_51_f66r_label_sign_edition.tsv",
    "gdt471_name_templates": G471 / "gdt471_89_template_assignments.tsv",
    "gdt472_complete_templates": G472 / "gdt472_107_complete_template_assignments.tsv",
}


RELATION_PHRASES = {
    "G407-E0046": "von der Ausgangszeile",
    "G407-E0616": "zur Zielstelle",
    "G407-E0643": "vom Ausgangsmaterial",
    "G407-E1276": "zur Zielposition",
    "G407-E2021": "zur Zielstation",
    "G407-E2047": "zur Zielstation",
    "G407-E2114": "von der Ausgangsstation",
    "G407-E2132": "zur Zielstation",
    "G407-E2184": "zur Zielstation",
    "G407-E2723": "zur Zielstation",
    "G407-E3572": "zur Zielstation",
    "G407-E3594": "zur Zielstation",
    "G407-E3604": "zur Zielstation",
    "G407-E3907": "zum Zielgefäß",
    "G407-E3963": "vom Ausgangsgefäß",
    "G407-E4121": "zum Zielgefäß",
    "G407-E4136": "zum Zielgefäß",
    "G407-E4419": "vom Ausgangsmaterial",
    "G407-E4467": "zur Zielstelle",
    "G515-E0367": "zur Zielspalte",
    "G515-E0379": "zur Zielspalte",
    "G515-E0423": "zur Zielspalte",
    "G515-E0470": "von der Ausgangszeile",
    "G515-E0537": "zur Zielspalte",
}
ALREADY_EXPLICIT_REMOTE_EVENT = "G515-E0379"
SAFE_FOCUS_IDS = {"G515-A00356", "G515-A00357"}
FORCED_OCCURRENCE_IDS = {"G407-A04352"}

IMPERATIVE_RE = re.compile(
    r"(?i)(?<![-\w])"
    r"(entnimm|nimm|halte|gib|ordne|führe|wähle|bearbeite|stelle|lege|"
    r"markiere|kennzeichne|trage|setze)(?!\w)"
)
IMPERATIVE_ROOT = {
    "entnimm": "CH",
    "nimm": "CH",
    "halte": "SH",
    "gib": "K",
    "ordne": "K",
    "führe": "K",
    "wähle": "S",
    "bearbeite": "CHD",
    "stelle": "T",
    "lege": "T",
    "markiere": "R",
    "kennzeichne": "R",
    "trage": "OK",
}

GENERIC_FOCUS_PHRASES = {
    "Y": "den Posten",
    "AIIN": "den Wert",
    "AIN": "den Anteil",
    "OR": "die Einheit",
    "AL": "zum Zielort",
    "AR": "vom Ausgang",
    "L": "über die Verbindung",
    "AIR": "entlang der Bahn",
    "E": "auf Grad I",
    "EE": "auf Grad II",
    "EEE": "auf Grad III",
}

MODIFIER_PHRASES = {
    "AM_ADDR": "an der AM-Stelle",
    "AN": "in der bezeichneten Klasse",
    "A_ADDR": "an der A-Stelle",
    "CARRIER_Q": "am Beginn",
    "DA": "auf der zweiten Stufe",
    "D_ADDR": "an der D-Stelle",
    "D_LABEL": "bei der d-Kennmarke",
    "G_LABEL": "bei der g-Kennmarke",
    "HO": "in der H-Klasse",
    "IIN": "auf der bezeichneten Stufe",
    "LOCAL_CHAR_B": "bei der b-Kennmarke",
    "LOCAL_CHAR_F": "bei der f-Kennmarke",
    "LOCAL_CHAR_G": "als g-Variante",
    "LOCAL_CHAR_I": "mit der i-Variante",
    "LOCAL_CHAR_J": "mit der j-Variante",
    "M_LOCAL": "bei der m-Kennmarke",
    "O": "als Ausführung",
    "OS": "mit Vorbezug",
    "S_ADDR": "an der S-Stelle",
}

ACTION_HEAD_NOMINALS = {
    "SOURCE_SECTION_T": {
        "OK": "Eintragen", "CH": "Entnehmen", "SH": "Festhalten",
        "K": "Zuordnen", "S": "Wählen", "CHD": "Bearbeiten",
        "T": "Festlegen", "R": "Kennzeichnen", "P": "Einsetzen",
    },
    "HERBAL": {
        "OK": "Ansetzen", "CH": "Nehmen", "SH": "Halten",
        "K": "Zugeben", "S": "Wählen", "CHD": "Bearbeiten",
        "T": "Einstellen", "R": "Markieren", "P": "Einsetzen",
    },
    "CELESTIAL": {
        "OK": "Setzen", "CH": "Aufnehmen", "SH": "Halten",
        "K": "Zuordnen", "S": "Wählen", "CHD": "Bearbeiten",
        "T": "Einstellen", "R": "Markieren", "P": "Einsetzen",
    },
    "BIOLOGICAL": {
        "OK": "Ansetzen", "CH": "Entnehmen", "SH": "Halten",
        "K": "Zuführen", "S": "Wählen", "CHD": "Bearbeiten",
        "T": "Einstellen", "R": "Markieren", "P": "Einsetzen",
    },
    "PHARMA": {
        "OK": "Ansetzen", "CH": "Nehmen", "SH": "Halten",
        "K": "Zugeben", "S": "Wählen", "CHD": "Bearbeiten",
        "T": "Einstellen", "R": "Markieren", "P": "Einsetzen",
    },
}


def normalize_attachment_row(
    row: dict[str, str], source: str, old_recipe_by_event: dict[str, str]
) -> dict[str, object]:
    if source == "GDT407":
        event_id = row["global_running_event_id"]
        return {
            "source_attachment_id": row["global_attachment_id"],
            "source_layer": "GDT407_5051_ATTACHMENT_EDITION",
            "statement_id": row["global_statement_id"],
            "event_id": event_id,
            "physical_page": row["physical_page"],
            "register": row["register"],
            "surface": row["surface"],
            "source_recipe": old_recipe_by_event[event_id],
            "focus_old_position": int(row["focus_atom_ordinal"]),
            "focus_root": row["focus_core"],
            "focus_value_de": row["focus_value_de"],
            "focus_family": row["focus_family"],
            "selector_rule": row["selector_rule"],
            "attachment_geometry": row["attachment_geometry"],
            "head_event_id": row["selected_action_global_event_id"],
            "head_old_position": int(row["selected_action_atom_ordinal"]),
            "head_root": row["action_core"],
            "head_value_de": row["action_value_de"],
            "head_kind": row["head_kind"],
            "lookahead_cards": row["lookahead_cards"],
            "owner_boundary_crossed": row["owner_boundary_crossed"],
            "statement_boundary_crossed": row["statement_boundary_crossed"],
        }
    event_id = row["event_id"]
    return {
        "source_attachment_id": row["factorized_id"],
        "source_layer": "GDT515_FACTORIZED_ATTACHMENTS",
        "statement_id": row["statement_id"],
        "event_id": event_id,
        "physical_page": row["physical_page"],
        "register": row["register"],
        "surface": row["surface"],
        "source_recipe": row["visible_recipe"],
        "focus_old_position": int(row["focus_atom_ordinal"]),
        "focus_root": row["focus_core"],
        "focus_value_de": row["focus_value_de"],
        "focus_family": row["focus_family"],
        "selector_rule": row["selector_rule"],
        "attachment_geometry": row["attachment_geometry"],
        "head_event_id": row["selected_action_event_id"],
        "head_old_position": int(row["selected_action_atom_ordinal"]),
        "head_root": row["action_core"],
        "head_value_de": row["action_value_de"],
        "head_kind": row["head_kind"],
        "lookahead_cards": row["lookahead_cards"],
        "owner_boundary_crossed": row["owner_boundary_crossed"],
        "statement_boundary_crossed": row["statement_boundary_crossed"],
    }


def reconcile_focus_attachments(
    source_rows: list[dict[str, object]],
    event_by_id: dict[str, dict[str, str]],
    old_recipe_by_event: dict[str, str],
    grade_by_key: dict[tuple[str, int], dict[str, str]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    reconciled: list[dict[str, object]] = []
    actions: list[dict[str, object]] = []
    for source in source_rows:
        event_id = str(source["event_id"])
        focus_root = str(source["focus_root"])
        source_parts = atoms(str(source["source_recipe"]))
        final_parts = atoms(event_by_id[event_id]["final_context_recipe"])
        focus_rank = occurrence_rank(
            source_parts, focus_root, int(source["focus_old_position"])
        )
        focus_position = nth_position(final_parts, focus_root, focus_rank)
        if focus_position is None:
            signature = (source["source_attachment_id"], event_id, focus_root, focus_rank)
            if signature != ("G515-A00165", "G515-E0182", "L", 1):
                raise RuntimeError(f"Unexpected vanished focus occurrence: {signature}")
            actions.append(
                {
                    "reconciliation_id": "GDT581-C01",
                    "source_attachment_id": source["source_attachment_id"],
                    "event_id": event_id,
                    "reconciliation_class": "DELETE_STALE_FOCUS",
                    "source_focus_head": "L#1@4→K#1@1",
                    "final_focus_head": "NONE",
                    "selector_rule": source["selector_rule"],
                    "reason": "Final K+EE+OL contains state root OL, not relation root L.",
                    "semantic_change": "YES",
                    "guard": "FINAL_ROOT_OCCURRENCE_IDENTITY_CONTROLS",
                }
            )
            continue

        head_event_id = str(source["head_event_id"])
        head_root = str(source["head_root"])
        head_rank: int | str
        head_position: int | str
        head_changed = False
        if head_event_id == "OWNER" or "OWNER" in str(source["head_kind"]):
            head_root = "OWNER"
            head_rank = "OWNER"
            head_position = "OWNER"
        else:
            old_head_parts = atoms(old_recipe_by_event[head_event_id])
            head_rank = occurrence_rank(
                old_head_parts, head_root, int(source["head_old_position"])
            )
            final_head_parts = atoms(event_by_id[head_event_id]["final_context_recipe"])
            head_position = nth_position(final_head_parts, head_root, int(head_rank))

            # Re-run the unchanged NEAREST_HEAD_LEFT_TIE selector on two final
            # recipes whose action geometry genuinely changed.
            if source["source_attachment_id"] == "G515-A00403":
                if (event_id, focus_root, focus_position) != ("G515-E0423", "EEE", 4):
                    raise RuntimeError("E0423 grade-switch signature drift")
                selected = nearest_action(final_parts, focus_position, "LEFT_TIE")
                if selected != (3, "K"):
                    raise RuntimeError("E0423 final nearest-left head drift")
                head_root, head_rank, head_position = "K", 1, 3
                head_changed = True
            elif head_position is None:
                signature = (
                    source["source_attachment_id"], event_id, focus_root, focus_rank,
                    head_root, head_rank,
                )
                expected = ("G515-A00407", "G515-E0426", "Y", 1, "CH", 2)
                if signature != expected:
                    raise RuntimeError(f"Unexpected vanished head occurrence: {signature}")
                selected = nearest_action(final_parts, focus_position, "LEFT_TIE")
                if selected != (2, "K"):
                    raise RuntimeError("E0426 final nearest-left head drift")
                head_root, head_rank, head_position = "K", 1, 2
                head_changed = True

        coordinate_changed = (
            int(source["focus_old_position"]) != focus_position
            or (
                head_position != "OWNER"
                and int(source["head_old_position"]) != int(head_position)
            )
            or head_changed
        )
        if coordinate_changed:
            pure_ids = {
                "G515-A00245", "G515-A00258", "G515-A00404", "G515-A00422"
            }
            switch_ids = {"G515-A00403", "G515-A00407"}
            source_id = str(source["source_attachment_id"])
            if source_id not in pure_ids | switch_ids:
                raise RuntimeError(f"Unexpected attachment coordinate change: {source_id}")
            actions.append(
                {
                    "reconciliation_id": "PENDING",
                    "source_attachment_id": source_id,
                    "event_id": event_id,
                    "reconciliation_class": (
                        "PURE_OCCURRENCE_POSITION_UPDATE"
                        if source_id in pure_ids
                        else "SELECTOR_FORCED_PRIMARY_HEAD_SWITCH"
                    ),
                    "source_focus_head": (
                        f"{focus_root}#{focus_rank}@{source['focus_old_position']}→"
                        f"{source['head_root']}@{source['head_old_position']}"
                    ),
                    "final_focus_head": (
                        f"{focus_root}#{focus_rank}@{focus_position}→"
                        f"{head_root}#{head_rank}@{head_position}"
                    ),
                    "selector_rule": source["selector_rule"],
                    "reason": (
                        "Same root-occurrence identities moved in the final recipe."
                        if source_id in pure_ids
                        else "The unchanged nearest-head selector chooses a different final action occurrence."
                    ),
                    "semantic_change": "NO" if source_id in pure_ids else "YES",
                    "guard": "FINAL_ROOT_OCCURRENCE_IDENTITY_CONTROLS",
                }
            )

        grade = grade_by_key.get((event_id, focus_position))
        if grade:
            if grade["default_host_mode"] == "CONTROL_CARRIED_GRADE_VALUE":
                effective_kind = "CONTROL_ENVELOPE"
                effective_key = f"CONTROL:{event_id}:{grade['carrier_envelope']}"
            else:
                effective_kind = "VISIBLE_ACTION_CHAIN"
                effective_key = f"ACTION_CHAIN:{event_id}:{grade['selected_visible_host_key']}"
            grade_mode = grade["default_host_mode"]
            grade_envelope = grade["carrier_envelope"]
        elif head_position == "OWNER":
            effective_kind = "OWNER_CONTEXT"
            effective_key = f"OWNER:{event_by_id[event_id]['owner_id']}"
            grade_mode = "NOT_APPLICABLE"
            grade_envelope = "NOT_APPLICABLE"
        else:
            effective_kind = "PRIMARY_ACTION"
            effective_key = f"ACTION:{head_event_id}@{head_position}:{head_root}"
            grade_mode = "NOT_APPLICABLE"
            grade_envelope = "NOT_APPLICABLE"

        realization_scope = "PRIMARY_GOVERNOR"
        if event_id == "G515-E0253":
            realization_scope = "ACTION_CHAIN(CH,T)__PRIMARY_AIIN_CH__PRIMARY_Y_T"
        elif event_id == "G515-E0423" and focus_root in {"EEE", "Y"}:
            realization_scope = "ACTION_CHAIN(CH,K)__PRIMARY_EEE_K__PRIMARY_Y_K"
        elif event_id == "G515-E0426" and focus_root == "Y":
            realization_scope = "ACTION_CHAIN(CH,K)__PRIMARY_Y_K"

        reconciled.append(
            {
                "focus_host_ordinal": 0,
                "focus_host_id": source["source_attachment_id"],
                "source_layer": source["source_layer"],
                "source_attachment_id": source["source_attachment_id"],
                "statement_id": source["statement_id"],
                "event_id": event_id,
                "physical_page": source["physical_page"],
                "register": source["register"],
                "owner_id": event_by_id[event_id]["owner_id"],
                "surface": source["surface"],
                "source_recipe": source["source_recipe"],
                "final_recipe": event_by_id[event_id]["final_context_recipe"],
                "focus_root": focus_root,
                "focus_value_de": source["focus_value_de"],
                "focus_family": source["focus_family"],
                "focus_occurrence_rank": focus_rank,
                "focus_source_position": source["focus_old_position"],
                "focus_final_position": focus_position,
                "selector_rule": source["selector_rule"],
                "attachment_geometry": source["attachment_geometry"],
                "primary_governor_kind": (
                    "OWNER_CONTEXT" if head_position == "OWNER" else "ACTION_OCCURRENCE"
                ),
                "primary_governor_event_id": head_event_id,
                "primary_governor_atom_position": head_position,
                "primary_governor_root": head_root,
                "primary_governor_occurrence_rank": head_rank,
                "effective_grammar_host_kind": effective_kind,
                "effective_grammar_host_key": effective_key,
                "grade_host_mode": grade_mode,
                "grade_carrier_envelope": grade_envelope,
                "prose_realization_scope": realization_scope,
                "coordinate_reconciled": "YES" if coordinate_changed else "NO",
                "lookahead_cards": source["lookahead_cards"],
                "owner_boundary_crossed": source["owner_boundary_crossed"],
                "statement_boundary_crossed": source["statement_boundary_crossed"],
                "guard": "ONE_FINAL_FOCUS_OCCURRENCE__ONE_PRIMARY_GOVERNOR",
            }
        )

    mapped = {
        (str(row["event_id"]), int(row["focus_final_position"])) for row in reconciled
    }
    expected = {
        (event_id, position)
        for event_id, event in event_by_id.items()
        for position, root in enumerate(atoms(event["final_context_recipe"]), 1)
        if root in OBJECT_ROOTS | RELATION_ROOTS | GRADE_ROOTS
    }
    missing = expected - mapped
    if missing != {("G515-E0253", 1)} or mapped - expected:
        raise RuntimeError(f"Unexpected final focus delta: missing={missing}, extra={mapped - expected}")

    event = event_by_id["G515-E0253"]
    reconciled.append(
        {
            "focus_host_ordinal": 0,
            "focus_host_id": "GDT581-NEW-E0253-AIIN",
            "source_layer": "GDT581_FINAL_RECIPE_RECONCILIATION",
            "source_attachment_id": "NONE",
            "statement_id": event["statement_id"],
            "event_id": event["event_id"],
            "physical_page": event["physical_page"],
            "register": event["register"],
            "owner_id": event["owner_id"],
            "surface": event["surface"],
            "source_recipe": old_recipe_by_event[event["event_id"]],
            "final_recipe": event["final_context_recipe"],
            "focus_root": "AIIN",
            "focus_value_de": "SPEZIFISCHER WERT",
            "focus_family": "ARGUMENT",
            "focus_occurrence_rank": 1,
            "focus_source_position": "ABSENT",
            "focus_final_position": 1,
            "selector_rule": "NEAREST_HEAD_LEFT_TIE",
            "attachment_geometry": "SAME_CARD_RIGHT_ACTION",
            "primary_governor_kind": "ACTION_OCCURRENCE",
            "primary_governor_event_id": event["event_id"],
            "primary_governor_atom_position": 2,
            "primary_governor_root": "CH",
            "primary_governor_occurrence_rank": 1,
            "effective_grammar_host_kind": "PRIMARY_ACTION",
            "effective_grammar_host_key": "ACTION:G515-E0253@2:CH",
            "grade_host_mode": "NOT_APPLICABLE",
            "grade_carrier_envelope": "NOT_APPLICABLE",
            "prose_realization_scope": "ACTION_CHAIN(CH,T)__PRIMARY_AIIN_CH__PRIMARY_Y_T",
            "coordinate_reconciled": "YES",
            "lookahead_cards": 0,
            "owner_boundary_crossed": "NO",
            "statement_boundary_crossed": "NO",
            "guard": "ONE_FINAL_FOCUS_OCCURRENCE__ONE_PRIMARY_GOVERNOR",
        }
    )
    actions.append(
        {
            "reconciliation_id": "GDT581-C08",
            "source_attachment_id": "NONE",
            "event_id": "G515-E0253",
            "reconciliation_class": "INSERT_NEW_FINAL_FOCUS",
            "source_focus_head": "NONE",
            "final_focus_head": "AIIN#1@1→CH#1@2",
            "selector_rule": "NEAREST_HEAD_LEFT_TIE",
            "reason": "Final AIIN+CH+T+Y introduces AIIN as the nearest-right CH argument.",
            "semantic_change": "YES",
            "guard": "FINAL_ROOT_OCCURRENCE_IDENTITY_CONTROLS",
        }
    )

    event_order = {event_id: int(row["edition_event_ordinal"]) for event_id, row in event_by_id.items()}
    reconciled.sort(
        key=lambda row: (event_order[str(row["event_id"])], int(row["focus_final_position"]))
    )
    for ordinal, row in enumerate(reconciled, 1):
        row["focus_host_ordinal"] = ordinal

    # Assign stable IDs to the six middle actions after C01 and before C08.
    middle = [row for row in actions if row["reconciliation_id"] == "PENDING"]
    middle.sort(key=lambda row: str(row["source_attachment_id"]))
    for offset, row in enumerate(middle, 2):
        row["reconciliation_id"] = f"GDT581-C{offset:02d}"
    actions.sort(key=lambda row: row["reconciliation_id"])
    class_counts = Counter(row["reconciliation_class"] for row in actions)
    if len(reconciled) != 5672 or class_counts != Counter(
        {
            "PURE_OCCURRENCE_POSITION_UPDATE": 4,
            "SELECTOR_FORCED_PRIMARY_HEAD_SWITCH": 2,
            "DELETE_STALE_FOCUS": 1,
            "INSERT_NEW_FINAL_FOCUS": 1,
        }
    ):
        raise RuntimeError(f"Focus reconciliation count drift: {class_counts}")
    return reconciled, actions


def build_inherited_aliases(
    g416_actions: list[dict[str, str]],
    g416_arguments: list[dict[str, str]],
    g539_events: list[dict[str, str]],
    event_by_id: dict[str, dict[str, str]],
) -> list[dict[str, object]]:
    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in event_by_id.values():
        events_by_statement[event["statement_id"]].append(event)
    for rows in events_by_statement.values():
        rows.sort(key=lambda row: int(row["card_ordinal_in_statement"]))

    def previous_source(event_id: str, root: str, roots: set[str]) -> str | None:
        event = event_by_id[event_id]
        ordinal = int(event["card_ordinal_in_statement"])
        candidates = [
            row
            for row in events_by_statement[event["statement_id"]]
            if int(row["card_ordinal_in_statement"]) < ordinal
            and root in atoms(row["final_context_recipe"])
            and root in roots
        ]
        return candidates[-1]["event_id"] if candidates else None

    pending: list[tuple[str, str, str, str | None, str]] = []
    for row in g416_actions:
        event_id = row["global_running_event_id"]
        root = row["inherited_action_root"]
        pending.append(
            ("ACTION_ALIAS", event_id, root, previous_source(event_id, root, ACTION_ROOTS), "GDT416")
        )
    for row in g416_arguments:
        event_id = row["global_running_event_id"]
        root = row["inherited_argument_root"]
        pending.append(
            ("OBJECT_ALIAS", event_id, root, previous_source(event_id, root, OBJECT_ROOTS), "GDT416")
        )
    for row in g539_events:
        if row["inherited_action_root"] != "NONE":
            pending.append(
                (
                    "ACTION_ALIAS",
                    row["event_id"],
                    row["inherited_action_root"],
                    row["inherited_action_source_event_id"],
                    "GDT539",
                )
            )
        if row["inherited_argument_root"] != "NONE":
            pending.append(
                (
                    "OBJECT_ALIAS",
                    row["event_id"],
                    row["inherited_argument_root"],
                    row["inherited_argument_source_event_id"],
                    "GDT539",
                )
            )

    rows: list[dict[str, object]] = []
    for ordinal, (alias_class, event_id, root, source_event_id, source_layer) in enumerate(pending, 1):
        event = event_by_id[event_id]
        if source_event_id in {None, "", "NONE"}:
            source_kind = "OWNER_DEFAULT"
            source_key = f"OWNER_DEFAULT:{event['owner_id']}:{root}"
            source_atom_position: int | str = "OWNER"
        else:
            if source_event_id not in event_by_id:
                raise RuntimeError(f"Inherited source event absent: {source_event_id}")
            source_event = event_by_id[source_event_id]
            if (
                source_event["statement_id"] != event["statement_id"]
                or source_event["physical_page"] != event["physical_page"]
                or source_event["owner_id"] != event["owner_id"]
                or int(source_event["card_ordinal_in_statement"])
                >= int(event["card_ordinal_in_statement"])
            ):
                raise RuntimeError(f"Inherited alias crosses a hard boundary: {event_id}")
            positions = [
                position
                for position, atom in enumerate(atoms(source_event["final_context_recipe"]), 1)
                if atom == root
            ]
            if not positions:
                raise RuntimeError(f"Inherited source root absent at {source_event_id}:{root}")
            source_atom_position = positions[-1]
            source_kind = "SAME_STATEMENT_EVENT"
            source_key = f"{source_event_id}@{source_atom_position}:{root}"
        rows.append(
            {
                "alias_ordinal": ordinal,
                "alias_id": f"GDT581-I{ordinal:04d}",
                "alias_class": alias_class,
                "event_id": event_id,
                "statement_id": event["statement_id"],
                "physical_page": event["physical_page"],
                "register": event["register"],
                "owner_id": event["owner_id"],
                "inherited_root": root,
                "lexical_source_kind": source_kind,
                "lexical_source_event_id": source_event_id or "OWNER",
                "lexical_source_atom_position": source_atom_position,
                "lexical_source_key": source_key,
                "source_layer": source_layer,
                "guard": "ALIAS_IS_NOT_A_NEW_WRITTEN_OR_DICTIONARY_SLOT",
            }
        )
    counts = Counter((row["alias_class"], row["lexical_source_kind"]) for row in rows)
    expected = Counter(
        {
            ("ACTION_ALIAS", "SAME_STATEMENT_EVENT"): 1477,
            ("ACTION_ALIAS", "OWNER_DEFAULT"): 264,
            ("OBJECT_ALIAS", "SAME_STATEMENT_EVENT"): 1801,
            ("OBJECT_ALIAS", "OWNER_DEFAULT"): 484,
        }
    )
    if len(rows) != 4026 or counts != expected:
        raise RuntimeError(f"Inherited alias count drift: {counts}")
    return rows


def build_local_card_hosts(
    base_cards: list[dict[str, str]],
    g479_rows: list[dict[str, str]],
    g513_rows: list[dict[str, str]],
    g515_rows: list[dict[str, str]],
) -> list[dict[str, object]]:
    g479_by_id = unique_index(g479_rows, "source_event_id", "GDT479 local event")
    g513_by_id = unique_index(g513_rows, "source_event_id", "GDT513 local event")
    g515_by_id = unique_index(g515_rows, "event_id", "GDT515 local event")
    if set(g479_by_id) & set(g513_by_id) or (set(g479_by_id) | set(g513_by_id)) & set(g515_by_id):
        raise RuntimeError("Local source partitions overlap")
    rows: list[dict[str, object]] = []
    partitions: Counter[str] = Counter()
    for ordinal, card in enumerate(base_cards, 1):
        source_id = card["source_event_id"]
        if source_id in g479_by_id:
            source = g479_by_id[source_id]
            partition = "GDT479_MICRORECORD_183"
            record_id = source["record_id"]
            bundle_id = source["bundle_id"]
            component_recipe = source["working_recipe"]
            active_model = source["active_model"]
        elif source_id in g513_by_id:
            source = g513_by_id[source_id]
            partition = "GDT513_REMAINDER_510"
            record_id = "NOT_APPLICABLE"
            bundle_id = "NOT_APPLICABLE"
            component_recipe = source["component_recipe"]
            active_model = source["record_role"]
        elif source_id in g515_by_id:
            source = g515_by_id[source_id]
            partition = "GDT515_NEW_LOCAL_51"
            record_id = "NOT_APPLICABLE"
            bundle_id = "NOT_APPLICABLE"
            component_recipe = source["visible_recipe"]
            active_model = source["content_role"]
        else:
            raise RuntimeError(f"Local card absent from all final partitions: {source_id}")
        for key in ("physical_page", "register", "locus", "surface"):
            if source[key] != card[key]:
                raise RuntimeError(f"Local source drift at {source_id}:{key}")
        partitions[partition] += 1
        rows.append(
            {
                "local_card_ordinal": ordinal,
                "local_card_host_key": f"LOCAL_CARD:{card['source_layer']}:{source_id}",
                "source_partition": partition,
                "source_layer": card["source_layer"],
                "source_event_id": source_id,
                "physical_page": card["physical_page"],
                "register": card["register"],
                "locus": card["locus"],
                "owner_de": card["owner_de"],
                "surface": card["surface"],
                "component_recipe": component_recipe,
                "component_count": len(atoms(component_recipe)),
                "source_local_role": card["source_local_role"],
                "record_id": record_id,
                "record_governor_key": (
                    f"LOCAL_RECORD:{record_id}" if record_id != "NOT_APPLICABLE" else "NOT_APPLICABLE"
                ),
                "bundle_id": bundle_id,
                "bundle_governor_key": (
                    f"LOCAL_BUNDLE:{bundle_id}" if bundle_id != "NOT_APPLICABLE" else "NOT_APPLICABLE"
                ),
                "active_local_model": active_model,
                "guard": "EXACT_CARD_ID__OWNER_AND_LOCUS_REQUIRED__NO_RUNNING_SENTENCE_INHERITANCE",
            }
        )
    expected = Counter(
        {
            "GDT479_MICRORECORD_183": 183,
            "GDT513_REMAINDER_510": 510,
            "GDT515_NEW_LOCAL_51": 51,
        }
    )
    if len(rows) != 744 or partitions != expected:
        raise RuntimeError(f"Local partition drift: {partitions}")
    return rows


def build_local_components(
    card_hosts: list[dict[str, object]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    subtype_counts: Counter[str] = Counter()
    form_stage_roots = {"O", "DA", "IIN", "CARRIER_Q"}
    for card in card_hosts:
        parts = atoms(str(card["component_recipe"]))
        for position, root in enumerate(parts, 1):
            if root in ACTION_ROOTS:
                subtype = "ACTION"
                governor_kind = "SELF_ACTION"
                governor_key = f"LOCAL_ACTION:{card['source_event_id']}@{position}:{root}"
            elif root in OBJECT_ROOTS:
                subtype = "OBJECT"
                action = nearest_action(parts, position)
                governor_kind = "LOCAL_ACTION" if action else "LOCAL_CARD_OR_RECORD"
                governor_key = (
                    f"LOCAL_ACTION:{card['source_event_id']}@{action[0]}:{action[1]}"
                    if action
                    else str(card["record_governor_key"])
                    if card["record_governor_key"] != "NOT_APPLICABLE"
                    else str(card["local_card_host_key"])
                )
            elif root in RELATION_ROOTS:
                subtype = "RELATION"
                action = nearest_action(parts, position)
                governor_kind = "LOCAL_ACTION" if action else "LOCAL_CARD_OR_RECORD"
                governor_key = (
                    f"LOCAL_ACTION:{card['source_event_id']}@{action[0]}:{action[1]}"
                    if action
                    else str(card["record_governor_key"])
                    if card["record_governor_key"] != "NOT_APPLICABLE"
                    else str(card["local_card_host_key"])
                )
            elif root in GRADE_ROOTS:
                subtype = "GRADE"
                action = nearest_action(parts, position)
                governor_kind = "LOCAL_ACTION" if action else "LOCAL_CARD_OR_RECORD"
                governor_key = (
                    f"LOCAL_ACTION:{card['source_event_id']}@{action[0]}:{action[1]}"
                    if action
                    else str(card["record_governor_key"])
                    if card["record_governor_key"] != "NOT_APPLICABLE"
                    else str(card["local_card_host_key"])
                )
            elif root in STATE_ROOTS or root in LOCAL_MACRO_ROOTS:
                subtype = "CONTROL"
                governor_kind = "LOCAL_CONTROL_OR_CARD"
                governor_key = f"LOCAL_CONTROL:{card['source_event_id']}@{position}:{root}"
            else:
                subtype = "FORM_STAGE" if root in form_stage_roots else "SIGLA_CLASS"
                action = nearest_action(parts, position)
                governor_kind = "LOCAL_ACTION" if action else "LOCAL_CARD_OR_RECORD"
                governor_key = (
                    f"LOCAL_ACTION:{card['source_event_id']}@{action[0]}:{action[1]}"
                    if action
                    else str(card["record_governor_key"])
                    if card["record_governor_key"] != "NOT_APPLICABLE"
                    else str(card["local_card_host_key"])
                )
            boundary_class, fill_status = content_boundary_class(root, "LOCAL")
            subtype_counts[subtype] += 1
            rows.append(
                {
                    "local_component_ordinal": len(rows) + 1,
                    "slot_id": f"LOCAL_COMPONENT:{card['source_event_id']}@{position}",
                    "source_event_id": card["source_event_id"],
                    "local_card_host_key": card["local_card_host_key"],
                    "source_partition": card["source_partition"],
                    "physical_page": card["physical_page"],
                    "register": card["register"],
                    "locus": card["locus"],
                    "owner_de": card["owner_de"],
                    "record_governor_key": card["record_governor_key"],
                    "surface": card["surface"],
                    "component_recipe": card["component_recipe"],
                    "component_position": position,
                    "component_root": root,
                    "local_component_subtype": subtype,
                    "boundary_class": boundary_class,
                    "fill_status": fill_status,
                    "primary_governor_kind": governor_kind,
                    "primary_governor_key": governor_key,
                    "guard": "ONE_LOCAL_COMPONENT__ONE_CARD__ONE_PRIMARY_GOVERNOR",
                }
            )
    expected = Counter(
        {
            "ACTION": 415,
            "OBJECT": 389,
            "RELATION": 313,
            "GRADE": 179,
            "FORM_STAGE": 196,
            "SIGLA_CLASS": 165,
            "CONTROL": 316,
        }
    )
    if len(rows) != 1973 or subtype_counts != expected:
        raise RuntimeError(f"Local component count drift: {subtype_counts}")
    return rows


def build_name_slots(
    g471_rows: list[dict[str, str]],
    g472_rows: list[dict[str, str]],
    card_hosts: list[dict[str, object]],
) -> list[dict[str, object]]:
    g471_by_event = unique_index(g471_rows, "source_event_id", "GDT471 name-bearing label")
    g472_by_event = unique_index(g472_rows, "source_event_id", "GDT472 complete label")
    card_by_event = {str(row["source_event_id"]): row for row in card_hosts}
    name_events = {
        event_id
        for event_id, row in g472_by_event.items()
        if "{NAME_" in row["surface_template"]
    }
    if name_events != set(g471_by_event) or len(name_events) != 89:
        raise RuntimeError("GDT471/GDT472 name-bearing event mismatch")
    rows: list[dict[str, object]] = []
    content_counts: Counter[str] = Counter()
    for event_id in sorted(name_events, key=lambda item: int(g472_by_event[item]["complete_assignment_id"].split("A")[-1])):
        complete = g472_by_event[event_id]
        learned = g471_by_event[event_id]
        card = card_by_event[event_id]
        extracted = extract_name_slots(complete["surface"], complete["surface_template"])
        span_items = []
        for trace in learned["learned_span_trace"].split("|"):
            start, end, raw = trace.split(":", 2)
            span_items.append((int(start), int(end), raw))
        if [raw for _, raw in extracted] != [raw for _, _, raw in span_items]:
            raise RuntimeError(f"Name template/span trace mismatch at {event_id}")
        for index, ((placeholder, raw), (start, end, trace_raw)) in enumerate(zip(extracted, span_items), 1):
            if complete["surface"][start:end] != raw or raw != trace_raw:
                raise RuntimeError(f"Name span coordinate mismatch at {event_id}:{index}")
            content_counts[complete["content_class"]] += 1
            rows.append(
                {
                    "name_slot_ordinal": len(rows) + 1,
                    "slot_id": f"LOCAL_NAME:{event_id}:{placeholder}",
                    "source_event_id": event_id,
                    "local_card_host_key": card["local_card_host_key"],
                    "physical_page": card["physical_page"],
                    "register": card["register"],
                    "locus": card["locus"],
                    "owner_de": card["owner_de"],
                    "record_governor_key": card["record_governor_key"],
                    "bundle_governor_key": card["bundle_governor_key"],
                    "surface": complete["surface"],
                    "surface_template": complete["surface_template"],
                    "name_placeholder": placeholder,
                    "name_slot_in_label": index,
                    "name_span_start_zero_based": start,
                    "name_span_end_exclusive": end,
                    "raw_name_core": raw,
                    "content_class": complete["content_class"],
                    "assignment_mode": complete["assignment_mode"],
                    "boundary_class": "LOCAL_LEARNED_NAME_SLOT",
                    "fill_status": "CONTENT_CARRIER",
                    "primary_governor_kind": "LOCAL_CARD",
                    "primary_governor_key": card["local_card_host_key"],
                    "guard": "LEARNED_NAME_SPAN__NOT_A_FUNCTION_ROOT_OR_CONFIRMED_OBJECT_NAME",
                }
            )
    expected = Counter(
        {
            "STAR_BEARING_RING_POSITION": 60,
            "DRUG_OR_INGREDIENT_OBJECT": 38,
            "BATH_OR_OUTLET_STATION": 7,
            "PICTURED_PLANT": 2,
        }
    )
    if len(rows) != 107 or content_counts != expected:
        raise RuntimeError(f"Name-slot count drift: {content_counts}")
    if len({row["raw_name_core"] for row in rows}) != 72:
        raise RuntimeError("Raw name-core type count drift")
    if len({(row["content_class"], row["raw_name_core"]) for row in rows}) != 80:
        raise RuntimeError("Owner-class x name-core type count drift")
    return rows


def build_non_grade_modifier_hosts(
    events: list[dict[str, str]],
    focus_hosts: list[dict[str, object]],
    alias_rows: list[dict[str, object]],
    repeat_slots: list[dict[str, str]],
    scope_slots: list[dict[str, str]],
) -> list[dict[str, object]]:
    focus_by_event: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in focus_hosts:
        focus_by_event[str(row["event_id"])].append(row)
    action_alias_by_event = {
        str(row["event_id"]): row
        for row in alias_rows
        if row["alias_class"] == "ACTION_ALIAS"
    }
    repeat_by_key: dict[tuple[str, int], dict[str, str]] = {}
    for row in repeat_slots:
        key = (row["event_id"], int(row["slot_atom_position_zero_based"]) + 1)
        if row["repeat_root"] not in RUNNING_MODIFIER_ROOTS - GRADE_ROOTS:
            continue
        if key in repeat_by_key:
            raise RuntimeError(f"Duplicate modifier repeat override {key}")
        repeat_by_key[key] = row
    scope_by_key: dict[tuple[str, int], dict[str, str]] = {}
    for row in scope_slots:
        if row["scope_root"] not in RUNNING_MODIFIER_ROOTS - GRADE_ROOTS:
            continue
        key = (row["event_id"], int(row["scope_atom_position_zero_based"]) + 1)
        if key in scope_by_key:
            raise RuntimeError(f"Duplicate modifier scope override {key}")
        scope_by_key[key] = row
    if len(scope_by_key) != 6:
        raise RuntimeError(f"Non-grade GDT579 scope-slot count drift: {len(scope_by_key)}")

    sigla_roots = {
        "D_ADDR", "A_ADDR", "AM_ADDR", "S_ADDR", "LOCAL_CHAR_F", "M_LOCAL",
        "D_LABEL", "LOCAL_CHAR_I", "LOCAL_CHAR_G", "G_LABEL", "LOCAL_CHAR_B",
        "LOCAL_CHAR_J",
    }
    form_stage_roots = {"O", "IIN", "DA", "CARRIER_Q"}
    class_roots = {"AN", "HO"}
    rows: list[dict[str, object]] = []
    subtype_counts: Counter[str] = Counter()
    for event in events:
        event_id = event["event_id"]
        parts = atoms(event["final_context_recipe"])
        for position, root in enumerate(parts, 1):
            if root not in RUNNING_MODIFIER_ROOTS - GRADE_ROOTS:
                continue
            override = repeat_by_key.get((event_id, position))
            scope_override = scope_by_key.get((event_id, position))
            if scope_override:
                if scope_override["head_event_id"] == "OWNER" or "OWNER" in scope_override["head_kind"]:
                    governor_kind = "OWNER_CONTEXT"
                    governor_key = f"OWNER:{event['owner_id']}"
                else:
                    governor_kind = "GDT579_SCOPED_ACTION_OCCURRENCE"
                    governor_key = (
                        f"ACTION:{scope_override['head_event_id']}@"
                        f"{int(scope_override['head_atom_position_zero_based']) + 1}:"
                        f"{scope_override['head_root']}"
                    )
                source = f"GDT579_SCOPE_SLOT:{scope_override['scope_slot_ordinal']}:{scope_override['scope']}"
            elif override and override["renderer_history_conflict"] == "NO":
                if override["head_event_id"] == "OWNER" or "OWNER" in override["head_kind"]:
                    governor_kind = "OWNER_CONTEXT"
                    governor_key = f"OWNER:{event['owner_id']}"
                else:
                    governor_kind = "GDT577_ACTION_OCCURRENCE"
                    governor_key = (
                        f"ACTION:{override['head_event_id']}@"
                        f"{int(override['head_atom_position_zero_based']) + 1}:"
                        f"{override['head_root']}"
                    )
                source = "GDT577_EXPLICIT_REPEAT_SLOT"
            else:
                action = nearest_action(parts, position)
                if action:
                    governor_kind = "SAME_CARD_ACTION"
                    governor_key = f"ACTION:{event_id}@{action[0]}:{action[1]}"
                    source = "NEAREST_VISIBLE_ACTION_LEFT_TIE"
                elif any(atom in STATE_ROOTS for atom in parts):
                    governor_kind = "CONTROL_ENVELOPE"
                    governor_key = f"CONTROL:{event_id}:STATE_CARD"
                    source = "VISIBLE_STATE_CONTROL_ENVELOPE"
                else:
                    governors = {
                        (
                            str(row["primary_governor_kind"]),
                            str(row["primary_governor_event_id"]),
                            str(row["primary_governor_atom_position"]),
                            str(row["primary_governor_root"]),
                        )
                        for row in focus_by_event.get(event_id, [])
                    }
                    if len(governors) == 1:
                        kind, head_event, head_position, head_root = next(iter(governors))
                        governor_kind = "FOCUS_CONSENSUS_" + kind
                        governor_key = (
                            f"OWNER:{event['owner_id']}"
                            if kind == "OWNER_CONTEXT"
                            else f"ACTION:{head_event}@{head_position}:{head_root}"
                        )
                        source = "SAME_CARD_FOCUS_GOVERNOR_CONSENSUS"
                    elif event_id in action_alias_by_event:
                        alias = action_alias_by_event[event_id]
                        governor_kind = "INHERITED_ACTION_ALIAS"
                        governor_key = str(alias["lexical_source_key"])
                        source = str(alias["alias_id"])
                    else:
                        governor_kind = "OWNER_CONTEXT"
                        governor_key = f"OWNER:{event['owner_id']}"
                        source = "OWNER_DEFAULT_NO_VISIBLE_ACTION_OR_UNIQUE_FOCUS_HEAD"
            subtype = (
                "FORM_STAGE"
                if root in form_stage_roots
                else "LEARNED_SIGLA"
                if root in sigla_roots
                else "CLASS"
                if root in class_roots
                else "OS_VORBEZUG"
            )
            subtype_counts[subtype] += 1
            rows.append(
                {
                    "modifier_host_ordinal": len(rows) + 1,
                    "slot_id": f"RUNNING:{event_id}@{position}",
                    "event_id": event_id,
                    "statement_id": event["statement_id"],
                    "physical_page": event["physical_page"],
                    "register": event["register"],
                    "owner_id": event["owner_id"],
                    "surface": event["surface"],
                    "final_recipe": event["final_context_recipe"],
                    "atom_position": position,
                    "atom_root": root,
                    "modifier_subtype": subtype,
                    "primary_governor_kind": governor_kind,
                    "primary_governor_key": governor_key,
                    "host_source": source,
                    "guard": "NON_GRADE_MODIFIER_HAS_EXACTLY_ONE_PRIMARY_GOVERNOR",
                }
            )
    expected = Counter(
        {"FORM_STAGE": 995, "LEARNED_SIGLA": 773, "CLASS": 34, "OS_VORBEZUG": 8}
    )
    if len(rows) != 1810 or subtype_counts != expected:
        raise RuntimeError(f"Running modifier count drift: {subtype_counts}")
    e0385 = {
        (int(row["atom_position"]), row["primary_governor_key"])
        for row in rows
        if row["event_id"] == "G515-E0385" and row["atom_root"] == "D_ADDR"
    }
    if e0385 != {
        (1, "ACTION:G515-E0383@4:R"),
        (3, "ACTION:G515-E0383@4:R"),
    }:
        raise RuntimeError(f"E0385 scoped D_ADDR host drift: {e0385}")
    return rows


def build_running_slots(
    events: list[dict[str, str]],
    focus_hosts: list[dict[str, object]],
    modifier_hosts: list[dict[str, object]],
) -> list[dict[str, object]]:
    focus_by_key = {
        (str(row["event_id"]), int(row["focus_final_position"])): row
        for row in focus_hosts
    }
    modifier_by_key = {
        (str(row["event_id"]), int(row["atom_position"])): row
        for row in modifier_hosts
    }
    if len(focus_by_key) != 5672 or len(modifier_by_key) != 1810:
        raise RuntimeError("Running host map identity collision")
    rows: list[dict[str, object]] = []
    fill_counts: Counter[str] = Counter()
    for event in events:
        event_id = event["event_id"]
        for position, root in enumerate(atoms(event["final_context_recipe"]), 1):
            boundary_class, fill_status = content_boundary_class(root, "RUNNING")
            if root in OBJECT_ROOTS | RELATION_ROOTS | GRADE_ROOTS:
                host = focus_by_key.get((event_id, position))
                if not host:
                    raise RuntimeError(f"Missing focus host at {event_id}@{position}")
                governor_kind = host["effective_grammar_host_kind"]
                governor_key = host["effective_grammar_host_key"]
                realization_scope = host["prose_realization_scope"]
                source = host["focus_host_id"]
            elif root in ACTION_ROOTS:
                governor_kind = "SELF_ACTION"
                governor_key = f"ACTION:{event_id}@{position}:{root}"
                realization_scope = "SELF"
                source = "FINAL_RECIPE_SELF_HEAD"
            elif root in STATE_ROOTS:
                governor_kind = "SELF_STATE_CONTROL"
                governor_key = f"CONTROL:{event_id}@{position}:{root}"
                realization_scope = "CONTROL_BLOCK"
                source = "GDT557_STATE_GRAMMAR"
            elif root == "LOCAL_X":
                governor_kind = "OWNER_BOUND_LEARNED_CORE"
                governor_key = f"OWNER:{event['owner_id']}:LOCAL_X"
                realization_scope = "EVENT_LOCAL_CORE"
                source = "GDT515_LOCAL_X_LOCK"
            elif root == "RESUME_CARD":
                governor_kind = "INHERITED_CONTROL"
                governor_key = f"OWNER:{event['owner_id']}:ACTIVE_OK_Y"
                realization_scope = "SAME_OWNER_ACTIVE_STATE"
                source = "GDT416_INHERITED_OK_Y"
            else:
                host = modifier_by_key.get((event_id, position))
                if not host:
                    raise RuntimeError(f"Missing modifier host at {event_id}@{position}:{root}")
                governor_kind = host["primary_governor_kind"]
                governor_key = host["primary_governor_key"]
                realization_scope = "PRIMARY_GOVERNOR"
                source = host["host_source"]
            fill_counts[fill_status] += 1
            rows.append(
                {
                    "running_slot_ordinal": len(rows) + 1,
                    "slot_id": f"RUNNING:{event_id}@{position}",
                    "event_id": event_id,
                    "statement_id": event["statement_id"],
                    "card_ordinal_in_statement": event["card_ordinal_in_statement"],
                    "physical_page": event["physical_page"],
                    "register": event["register"],
                    "owner_id": event["owner_id"],
                    "surface": event["surface"],
                    "final_recipe": event["final_context_recipe"],
                    "atom_position": position,
                    "atom_root": root,
                    "boundary_class": boundary_class,
                    "fill_status": fill_status,
                    "primary_governor_kind": governor_kind,
                    "primary_governor_key": governor_key,
                    "realization_scope": realization_scope,
                    "host_source": source,
                    "guard": "EVERY_RUNNING_SLOT_HAS_ONE_BOUNDARY_CLASS_AND_PRIMARY_GOVERNOR",
                }
            )
    expected = Counter({"CONTENT_CARRIER": 11938, "CONTROL_HOST_ONLY": 1871})
    if len(rows) != 13809 or fill_counts != expected:
        raise RuntimeError(f"Running slot count drift: {fill_counts}")
    return rows


def combine_complete_slots(
    running: list[dict[str, object]],
    local_components: list[dict[str, object]],
    names: list[dict[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    rows: list[dict[str, object]] = []
    for row in running:
        rows.append(
            {
                "complete_slot_ordinal": len(rows) + 1,
                "slot_id": row["slot_id"],
                "layer": "RUNNING_ATOM",
                "source_event_or_card_id": row["event_id"],
                "statement_or_record_id": row["statement_id"],
                "physical_page": row["physical_page"],
                "register": row["register"],
                "owner": row["owner_id"],
                "locus": "RUNNING_STATEMENT",
                "surface": row["surface"],
                "slot_value": row["atom_root"],
                "slot_position": row["atom_position"],
                "boundary_class": row["boundary_class"],
                "fill_status": row["fill_status"],
                "primary_governor_kind": row["primary_governor_kind"],
                "primary_governor_key": row["primary_governor_key"],
                "realization_scope": row["realization_scope"],
                "source_detail": row["host_source"],
                "guard": "COMPLETE_SLOT_LEDGER__NO_UNHOSTED_ENTRY",
            }
        )
    for row in local_components:
        rows.append(
            {
                "complete_slot_ordinal": len(rows) + 1,
                "slot_id": row["slot_id"],
                "layer": "LOCAL_COMPONENT",
                "source_event_or_card_id": row["source_event_id"],
                "statement_or_record_id": row["record_governor_key"],
                "physical_page": row["physical_page"],
                "register": row["register"],
                "owner": row["owner_de"],
                "locus": row["locus"],
                "surface": row["surface"],
                "slot_value": row["component_root"],
                "slot_position": row["component_position"],
                "boundary_class": row["boundary_class"],
                "fill_status": row["fill_status"],
                "primary_governor_kind": row["primary_governor_kind"],
                "primary_governor_key": row["primary_governor_key"],
                "realization_scope": "LOCAL_CARD_OR_RECORD",
                "source_detail": row["source_partition"],
                "guard": "COMPLETE_SLOT_LEDGER__NO_UNHOSTED_ENTRY",
            }
        )
    for row in names:
        rows.append(
            {
                "complete_slot_ordinal": len(rows) + 1,
                "slot_id": row["slot_id"],
                "layer": "LOCAL_NAME_SPAN",
                "source_event_or_card_id": row["source_event_id"],
                "statement_or_record_id": row["record_governor_key"],
                "physical_page": row["physical_page"],
                "register": row["register"],
                "owner": row["owner_de"],
                "locus": row["locus"],
                "surface": row["surface"],
                "slot_value": row["raw_name_core"],
                "slot_position": row["name_slot_in_label"],
                "boundary_class": row["boundary_class"],
                "fill_status": row["fill_status"],
                "primary_governor_kind": row["primary_governor_kind"],
                "primary_governor_key": row["primary_governor_key"],
                "realization_scope": "OWNER_BOUND_LEARNED_NAME",
                "source_detail": row["content_class"],
                "guard": "COMPLETE_SLOT_LEDGER__NO_UNHOSTED_ENTRY",
            }
        )
    carriers = [row for row in rows if row["fill_status"] == "CONTENT_CARRIER"]
    controls = [row for row in rows if row["fill_status"] == "CONTROL_HOST_ONLY"]
    if len(rows) != 15889 or len(carriers) != 13702 or len(controls) != 2187:
        raise RuntimeError(
            f"Complete slot totals drift: all={len(rows)} carriers={len(carriers)} controls={len(controls)}"
        )
    if len({str(row["slot_id"]) for row in rows}) != len(rows):
        raise RuntimeError("Complete slot IDs are not unique")
    return rows, carriers, controls


def build_cross_card_relations(
    focus_hosts: list[dict[str, object]],
    event_by_id: dict[str, dict[str, str]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for host in focus_hosts:
        root = str(host["focus_root"])
        event_id = str(host["event_id"])
        head_event_id = str(host["primary_governor_event_id"])
        if root not in {"AL", "AR"} or head_event_id in {event_id, "OWNER"}:
            continue
        current_actions = [
            root for _, root in action_positions(atoms(event_by_id[event_id]["final_context_recipe"]))
        ]
        if not current_actions:
            continue
        current = event_by_id[event_id]
        head = event_by_id[head_event_id]
        if (
            current["statement_id"] != head["statement_id"]
            or current["physical_page"] != head["physical_page"]
            or current["owner_id"] != head["owner_id"]
        ):
            raise RuntimeError(f"Cross-card relation crosses a hard boundary: {event_id}")
        if event_id not in RELATION_PHRASES:
            raise RuntimeError(f"Missing finite relation phrase for {event_id}")
        head_root = str(host["primary_governor_root"])
        rows.append(
            {
                "cross_relation_ordinal": 0,
                "focus_host_id": host["focus_host_id"],
                "event_id": event_id,
                "statement_id": current["statement_id"],
                "physical_page": current["physical_page"],
                "register": current["register"],
                "owner_id": current["owner_id"],
                "surface": current["surface"],
                "final_recipe": current["final_context_recipe"],
                "relation_root": root,
                "relation_atom_position": host["focus_final_position"],
                "relation_phrase_de": RELATION_PHRASES[event_id],
                "head_event_id": head_event_id,
                "head_card_ordinal": head["card_ordinal_in_statement"],
                "head_root": head_root,
                "head_atom_position": host["primary_governor_atom_position"],
                "head_nominal_de": ACTION_NOMINALS[head_root],
                "attachment_geometry": host["attachment_geometry"],
                "current_visible_actions": "|".join(current_actions),
                "same_root_different_occurrence": (
                    "YES" if set(current_actions) == {head_root} else "NO"
                ),
                "voice_status_before_gdt581": (
                    "ALREADY_EXPLICIT_GDT580"
                    if event_id == ALREADY_EXPLICIT_REMOTE_EVENT
                    else "HEAD_NOT_OCCURRENCE_EXPLICIT"
                ),
                "guard": "SAME_STATEMENT__SAME_OWNER__SAME_PAGE__HEAD_OCCURRENCE_REQUIRED",
            }
        )
    event_order = {
        event_id: int(event["edition_event_ordinal"]) for event_id, event in event_by_id.items()
    }
    rows.sort(
        key=lambda row: (event_order[str(row["event_id"])], int(row["relation_atom_position"]))
    )
    for ordinal, row in enumerate(rows, 1):
        row["cross_relation_ordinal"] = ordinal
    counts = Counter(row["relation_root"] for row in rows)
    geometry = Counter(row["attachment_geometry"] for row in rows)
    if (
        len(rows) != 25
        or len({row["event_id"] for row in rows}) != 24
        or counts != Counter({"AL": 19, "AR": 6})
        or geometry != Counter({"PREVIOUS_CARD_ACTION": 15, "INHERITED_ACTION": 10})
        or {str(row["event_id"]) for row in rows} != set(RELATION_PHRASES)
    ):
        raise RuntimeError(
            f"Cross-card relation deck drift: roots={counts}, geometry={geometry}, rows={len(rows)}"
        )
    return rows


def audible_action_root(clause_de: str) -> tuple[str, str] | None:
    """Return the first audible imperative root without matching *D-Stelle*."""

    for match in IMPERATIVE_RE.finditer(clause_de):
        verb = match.group(1).lower()
        tail = clause_de[match.end():]
        stop = re.search(r";|,|\.|(?i:\bund\b)", tail)
        segment = tail[: stop.start()] if stop else tail
        # Bare "führe den Gang weiter" is OL control voice, not K/ZUFÜHREN.
        if verb == "führe" and not re.search(r"(?i)(?<!\w)zu(?!\w)", segment):
            continue
        if verb != "setze":
            return IMPERATIVE_ROOT[verb], verb
        root = "P" if re.search(r"(?i)(?<!\w)ein(?!\w)", segment) else "OK"
        return root, verb
    return None


def focus_machine_link(host: dict[str, object]) -> str:
    return (
        f"{host['focus_host_id']}:{host['event_id']}@{host['focus_final_position']}:"
        f"{host['focus_root']}#{host['focus_occurrence_rank']}"
    )


def head_machine_link(host: dict[str, object]) -> str:
    if host["primary_governor_kind"] == "OWNER_CONTEXT":
        return f"OWNER:{host['owner_id']}"
    return (
        f"{host['primary_governor_event_id']}@"
        f"{host['primary_governor_atom_position']}:{host['primary_governor_root']}"
    )


def voice_head_machine_link(host: dict[str, object]) -> str:
    if host["effective_grammar_host_kind"] == "CONTROL_ENVELOPE":
        return str(host["effective_grammar_host_key"])
    return head_machine_link(host)


def build_safe_focus_exceptions(
    focus_hosts: list[dict[str, object]], written_slots: list[dict[str, str]]
) -> list[dict[str, object]]:
    host_by_id = {str(row["focus_host_id"]): row for row in focus_hosts}
    slot_by_id = {
        row["gdt515_attachment_id"]: row
        for row in written_slots
        if row["gdt515_attachment_id"] != "NONE"
    }
    if set(slot_by_id) != SAFE_FOCUS_IDS:
        raise RuntimeError(f"GDT580 safe-focus evidence drift: {set(slot_by_id)}")
    rows: list[dict[str, object]] = []
    for ordinal, focus_id in enumerate(sorted(SAFE_FOCUS_IDS), 1):
        host = host_by_id[focus_id]
        slot = slot_by_id[focus_id]
        observed = (
            host["event_id"],
            host["focus_root"],
            host["attachment_geometry"],
            host["primary_governor_event_id"],
            int(host["primary_governor_atom_position"]),
            host["primary_governor_root"],
        )
        expected = ("G515-E0379", "AL", "PREVIOUS_CARD_ACTION", "G515-E0378", 3, "T")
        if observed != expected:
            raise RuntimeError(f"Safe E0379 binding drift at {focus_id}: {observed}")
        if (
            slot["selected_head_event_id"] != "G515-E0378"
            or int(slot["selected_head_atom_position_zero_based"]) + 1 != 3
            or slot["selected_head_root"] != "T"
        ):
            raise RuntimeError(f"Safe E0379 written-slot evidence drift at {focus_id}")
        rows.append(
            {
                "safe_exception_ordinal": ordinal,
                "focus_host_id": focus_id,
                "event_id": host["event_id"],
                "focus_root": host["focus_root"],
                "focus_final_position": host["focus_final_position"],
                "attachment_geometry": host["attachment_geometry"],
                "selected_head_link": head_machine_link(host),
                "gdt580_target_realization_de": slot["target_realization_de"],
                "safe_voice_evidence": "Beim vorangehenden Festlegen",
                "disposition": "SAFE_ALREADY_EXPLICIT__DO_NOT_REWRITE",
                "guard": "FOCUS_SPECIFIC_GDT580_SLOT_SPAN__PREVIOUS_T_HEAD_EXPLICIT",
            }
        )
    return rows


def select_voice_repairs(
    focus_hosts: list[dict[str, object]],
    event_by_id: dict[str, dict[str, str]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for host in focus_hosts:
        event_id = str(host["event_id"])
        audible = audible_action_root(
            event_by_id[event_id]["relation_resumption_voice_working_clause_de"]
        )
        audible_root = audible[0] if audible else "NONE"
        geometry = str(host["attachment_geometry"])
        head_root = str(host["primary_governor_root"])
        focus_id = str(host["focus_host_id"])
        repair_class = ""
        if focus_id in FORCED_OCCURRENCE_IDS:
            repair_class = "SAME_ROOT_DIFFERENT_ACTION_OCCURRENCE"
        elif audible:
            if geometry == "OWNER_ONLY":
                repair_class = "OWNER_CONTENT_AUDIBLE_AS_LOCAL_ACTION"
            elif geometry == "BOUNDED_NEXT_CARD_ACTION" and audible_root != head_root:
                repair_class = "NEXT_HEAD_ROOT_DIFFERS_FROM_AUDIBLE_ACTION"
            elif (
                geometry in {"PREVIOUS_CARD_ACTION", "INHERITED_ACTION"}
                and audible_root != head_root
                and focus_id not in SAFE_FOCUS_IDS
            ):
                repair_class = "REMOTE_HEAD_ROOT_DIFFERS_FROM_AUDIBLE_ACTION"
        if not repair_class:
            continue
        rows.append(
            {
                "voice_repair_ordinal": len(rows) + 1,
                "voice_repair_id": f"GDT581-V{len(rows) + 1:03d}",
                "focus_host_id": focus_id,
                "event_id": event_id,
                "statement_id": host["statement_id"],
                "physical_page": host["physical_page"],
                "register": host["register"],
                "owner_id": host["owner_id"],
                "surface": host["surface"],
                "final_recipe": host["final_recipe"],
                "focus_root": host["focus_root"],
                "focus_family": host["focus_family"],
                "focus_final_position": host["focus_final_position"],
                "focus_machine_link": focus_machine_link(host),
                "attachment_geometry": geometry,
                "selected_head_link": head_machine_link(host),
                "selected_head_root": head_root,
                "effective_grammar_host_kind": host["effective_grammar_host_kind"],
                "effective_grammar_host_key": host["effective_grammar_host_key"],
                "voice_head_link": voice_head_machine_link(host),
                "audible_first_action_root": audible_root,
                "audible_first_imperative": audible[1] if audible else "NONE",
                "selector_trigger_class": repair_class,
                "voice_repair_class": (
                    "GRADE_CONTROL_ENVELOPE_BEATS_EVENT_WIDE_ACTION"
                    if host["effective_grammar_host_kind"] == "CONTROL_ENVELOPE"
                    else "EXPLICIT_PRIMARY_HEAD_BLOCK"
                ),
                "source_clause_de": event_by_id[event_id][
                    "relation_resumption_voice_working_clause_de"
                ],
                "event_repair_id": "PENDING",
                "explicit_head_block_de": "PENDING",
                "guard": "FOCUS_SPECIFIC_HEAD_BEATS_EVENT_WIDE_WORDING",
            }
        )
    geometry_counts = Counter(row["attachment_geometry"] for row in rows)
    expected_geometry = Counter(
        {
            "OWNER_ONLY": 128,
            "BOUNDED_NEXT_CARD_ACTION": 98,
            "PREVIOUS_CARD_ACTION": 24,
            "INHERITED_ACTION": 19,
        }
    )
    if (
        len(rows) != 269
        or len({row["event_id"] for row in rows}) != 232
        or geometry_counts != expected_geometry
        or Counter(str(row["focus_host_id"]).split("-")[0] for row in rows)
        != Counter({"G407": 261, "G515": 8})
    ):
        raise RuntimeError(
            f"Voice-repair selector drift: rows={len(rows)} geometry={geometry_counts}"
        )
    if "G407-A04352" not in {row["focus_host_id"] for row in rows}:
        raise RuntimeError("Occurrence-specific E3963 repair vanished")
    if SAFE_FOCUS_IDS & {str(row["focus_host_id"]) for row in rows}:
        raise RuntimeError("Safe E0379 focus was incorrectly selected for repair")
    return rows


def owner_voice_phrase_map(
    voice_cards: list[dict[str, str]],
) -> dict[tuple[str, str], str]:
    result: dict[tuple[str, str], str] = {}
    for row in voice_cards:
        if row["card_class"] not in {"ARGUMENT_OWNER_VOICE", "RELATION_OWNER_VOICE"}:
            continue
        key = (row["register_scope"], row["root_or_trigger"])
        if key in result:
            raise RuntimeError(f"Duplicate GDT567 owner-voice cell: {key}")
        result[key] = row["owner_voice_phrase_de"]
    if len(result) != 37:
        raise RuntimeError(f"GDT567 owner-voice cell count drift: {len(result)}")
    return result


def action_nominal_map(
    action_cells: list[dict[str, str]],
) -> dict[tuple[str, str], str]:
    observed: set[tuple[str, str]] = set()
    for row in action_cells:
        key = (row["register"], row["action_root"])
        if key in observed:
            raise RuntimeError(f"Duplicate GDT568 action cell: {key}")
        observed.add(key)
    result = {
        (register, root): nominal
        for register, mapping in ACTION_HEAD_NOMINALS.items()
        for root, nominal in mapping.items()
    }
    if observed != set(result) or len(result) != 45:
        raise RuntimeError("GDT568/closed action-head nominal inventory drift")
    return result


def render_focus_phrase(
    host: dict[str, object],
    owner_phrases: dict[tuple[str, str], str],
    scope_by_key: dict[tuple[str, int], dict[str, str]],
) -> str:
    root = str(host["focus_root"])
    phrase = owner_phrases.get(
        (str(host["register"]), root), GENERIC_FOCUS_PHRASES[root]
    )
    scope = scope_by_key.get(
        (str(host["event_id"]), int(host["focus_final_position"]) - 1)
    )
    if scope:
        phrase = f"{phrase} im {scope['scope_marker_de']} Zweig"
    return phrase


def head_block_prefix(
    host: dict[str, object],
    action_nominals: dict[tuple[str, str], str],
) -> str:
    if host["effective_grammar_host_kind"] == "CONTROL_ENVELOPE":
        return "Bezug auf den Steuerungsrahmen"
    if host["primary_governor_kind"] == "OWNER_CONTEXT":
        return "Bezug auf den Besitzerrahmen"
    root = str(host["primary_governor_root"])
    nominal = action_nominals[(str(host["register"]), root)]
    geometry = str(host["attachment_geometry"])
    if geometry == "BOUNDED_NEXT_CARD_ACTION":
        return f"Bezug auf das folgende {nominal}"
    if geometry == "PREVIOUS_CARD_ACTION":
        return f"Bezug auf das vorangehende {nominal}"
    if geometry == "INHERITED_ACTION":
        return f"Bezug auf das fortgeführte {nominal}"
    return f"Lokales {nominal}"


def parse_action_governor_key(key: str) -> tuple[str, int, str] | None:
    normalized = key.removeprefix("ACTION:")
    match = re.fullmatch(r"(G(?:407|515)-E[0-9]+)@([0-9]+):([A-Z_]+)", normalized)
    if not match:
        return None
    return match.group(1), int(match.group(2)), match.group(3)


def modifier_head_prefix(
    slot: dict[str, object],
    event: dict[str, str],
    event_by_id: dict[str, dict[str, str]],
    action_nominals: dict[tuple[str, str], str],
    scope: dict[str, str] | None,
) -> tuple[str, str]:
    key = str(slot["primary_governor_key"])
    if key.startswith("OWNER:") or key.startswith("OWNER_DEFAULT:"):
        return "Bezug auf den Besitzerrahmen", key
    if key.startswith("CONTROL:"):
        return "Bezug auf den Steuerungsrahmen", key
    action = parse_action_governor_key(key)
    if not action:
        return "Bezug auf den gebundenen Strukturrahmen", key
    head_event_id, head_position, head_root = action
    nominal = action_nominals[(event["register"], head_root)]
    display_key = f"{head_event_id}@{head_position}:{head_root}"
    if head_event_id == event["event_id"]:
        return f"Lokales {nominal}", display_key
    source_geometry = scope["source_geometry"] if scope else ""
    if "NEXT" in source_geometry:
        return f"Bezug auf das folgende {nominal}", display_key
    if "ACTIVE" in source_geometry or "INHERITED" in source_geometry:
        return f"Bezug auf das fortgeführte {nominal}", display_key
    head = event_by_id[head_event_id]
    if int(head["card_ordinal_in_statement"]) > int(event["card_ordinal_in_statement"]):
        return f"Bezug auf das folgende {nominal}", display_key
    return f"Bezug auf das vorangehende {nominal}", display_key


def build_event_voice_repairs(
    repairs: list[dict[str, object]],
    focus_hosts: list[dict[str, object]],
    running_slots: list[dict[str, object]],
    event_by_id: dict[str, dict[str, str]],
    voice_cards: list[dict[str, str]],
    action_cells: list[dict[str, str]],
    scope_slots: list[dict[str, str]],
) -> tuple[list[dict[str, object]], dict[str, str]]:
    owner_phrases = owner_voice_phrase_map(voice_cards)
    action_nominals = action_nominal_map(action_cells)
    scope_by_key = {
        (row["event_id"], int(row["scope_atom_position_zero_based"])): row
        for row in scope_slots
    }
    if len(scope_by_key) != 34:
        raise RuntimeError("GDT579 scope-slot identity collision")

    repairs_by_event: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in repairs:
        repairs_by_event[str(row["event_id"])].append(row)
    focus_by_event: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in focus_hosts:
        focus_by_event[str(row["event_id"])].append(row)
    slots_by_event: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in running_slots:
        slots_by_event[str(row["event_id"])].append(row)

    event_order = {
        event_id: int(event["edition_event_ordinal"])
        for event_id, event in event_by_id.items()
    }
    rows: list[dict[str, object]] = []
    block_by_focus: dict[str, str] = {}
    for event_id in sorted(repairs_by_event, key=event_order.__getitem__):
        event = event_by_id[event_id]
        event_focus = sorted(
            focus_by_event[event_id], key=lambda row: int(row["focus_final_position"])
        )
        # One explicit block per written content slot keeps raw atom order and
        # prevents a same-head run from swallowing an intervening other head.
        ordered_blocks: list[tuple[int, int, str]] = []
        represented_local_action_links: set[str] = set()
        for host in event_focus:
            head_link = voice_head_machine_link(host)
            prefix = head_block_prefix(host, action_nominals)
            block = (
                f"{prefix} [{head_link}]: "
                f"{render_focus_phrase(host, owner_phrases, scope_by_key)} "
                f"[{focus_machine_link(host)}]."
            )
            ordered_blocks.append(
                (int(host["focus_final_position"]), len(ordered_blocks), block)
            )
            focus_id = str(host["focus_host_id"])
            block_by_focus[focus_id] = block
            if (
                host["effective_grammar_host_kind"] != "CONTROL_ENVELOPE"
                and
                host["primary_governor_kind"] == "ACTION_OCCURRENCE"
                and host["primary_governor_event_id"] == event_id
            ):
                represented_local_action_links.add(head_link)

        modifier_slots = [
            row
            for row in slots_by_event[event_id]
            if row["atom_root"] in RUNNING_MODIFIER_ROOTS - GRADE_ROOTS
        ]
        modifier_markers: list[str] = []
        for slot in modifier_slots:
            position = int(slot["atom_position"])
            scope = scope_by_key.get((event_id, position - 1))
            phrase = MODIFIER_PHRASES[str(slot["atom_root"])]
            if scope:
                phrase = f"{phrase} im {scope['scope_marker_de']} Zweig"
            prefix, governor_link = modifier_head_prefix(
                slot, event, event_by_id, action_nominals, scope
            )
            marker = f"{slot['slot_id']}:{slot['atom_root']}"
            modifier_markers.append(marker)
            block = f"{prefix} [{governor_link}]: {phrase} [{marker}]."
            ordered_blocks.append((position, len(ordered_blocks), block))
            parsed_governor = parse_action_governor_key(
                str(slot["primary_governor_key"])
            )
            if parsed_governor and parsed_governor[0] == event_id:
                represented_local_action_links.add(
                    f"{parsed_governor[0]}@{parsed_governor[1]}:{parsed_governor[2]}"
                )

        action_links: list[str] = []
        bare_local_action_count = 0
        for position, root in action_positions(atoms(event["final_context_recipe"])):
            link = f"{event_id}@{position}:{root}"
            action_links.append(link)
            if link not in represented_local_action_links:
                nominal = action_nominals[(event["register"], root)]
                ordered_blocks.append(
                    (position, len(ordered_blocks), f"Lokales {nominal} [{link}].")
                )
                bare_local_action_count += 1

        residue_slots = [
            row
            for row in sorted(
                slots_by_event[event_id], key=lambda item: int(item["atom_position"])
            )
            if row["fill_status"] == "CONTROL_HOST_ONLY"
        ]
        residue = ""
        if residue_slots:
            residue = "Strukturspur: " + "; ".join(
                f"{row['atom_root']}@{row['atom_position']}→{row['primary_governor_key']}"
                for row in residue_slots
            ) + "."
        target_parts = [
            block for _, _, block in sorted(ordered_blocks, key=lambda item: (item[0], item[1]))
        ] + ([residue] if residue else [])
        target_clause = " ".join(target_parts)
        if not target_clause:
            raise RuntimeError(f"Empty repaired boundary clause at {event_id}")
        for host in event_focus:
            marker = f"[{focus_machine_link(host)}]"
            if target_clause.count(marker) != 1:
                raise RuntimeError(f"Focus link not represented exactly once: {marker}")
        for marker in modifier_markers:
            if target_clause.count(f"[{marker}]") != 1:
                raise RuntimeError(f"Modifier link not represented exactly once: {marker}")

        event_repairs = repairs_by_event[event_id]
        repair_id = f"GDT581-EV{len(rows) + 1:03d}"
        rows.append(
            {
                "event_repair_ordinal": len(rows) + 1,
                "event_repair_id": repair_id,
                "event_id": event_id,
                "statement_id": event["statement_id"],
                "physical_page": event["physical_page"],
                "register": event["register"],
                "owner_id": event["owner_id"],
                "surface": event["surface"],
                "final_recipe": event["final_context_recipe"],
                "audible_first_action_root": (
                    audible_action_root(
                        event["relation_resumption_voice_working_clause_de"]
                    )[0]
                    if audible_action_root(
                        event["relation_resumption_voice_working_clause_de"]
                    )
                    else "NONE"
                ),
                "selected_repair_focus_count": len(event_repairs),
                "represented_event_focus_count": len(event_focus),
                "represented_non_grade_modifier_count": len(modifier_slots),
                "explicit_focus_head_block_count": len(event_focus),
                "explicit_modifier_head_block_count": len(modifier_slots),
                "explicit_head_block_count": len(event_focus) + len(modifier_slots),
                "bare_local_action_block_count": bare_local_action_count,
                "visible_action_count": len(action_links),
                "selector_trigger_classes": "|".join(
                    sorted({str(row["selector_trigger_class"]) for row in event_repairs})
                ),
                "voice_repair_classes": "|".join(
                    sorted({str(row["voice_repair_class"]) for row in event_repairs})
                ),
                "repair_focus_ids": "|".join(
                    str(row["focus_host_id"]) for row in event_repairs
                ),
                "represented_focus_ids": "|".join(
                    str(row["focus_host_id"]) for row in event_focus
                ),
                "visible_action_links": "|".join(action_links) if action_links else "NONE",
                "source_gdt580_clause_de": event[
                    "relation_resumption_voice_working_clause_de"
                ],
                "content_ready_boundary_clause_de": target_clause,
                "gdt580_exact_roundtrip_de": event[
                    "relation_resumption_voice_working_clause_de"
                ],
                "guard": "ALL_EVENT_CONTENT_LINKS_ON_EXACT_HEADS__GDT580_BACKCHANNEL_EXACT",
            }
        )
        for repair in event_repairs:
            repair["event_repair_id"] = repair_id
            repair["explicit_head_block_de"] = block_by_focus[
                str(repair["focus_host_id"])
            ]

    if len(rows) != 232 or sum(int(row["selected_repair_focus_count"]) for row in rows) != 269:
        raise RuntimeError("Event voice-repair total drift")
    if sum(int(row["represented_event_focus_count"]) for row in rows) != 292:
        raise RuntimeError("Repaired-event full focus representation drift")
    if sum(int(row["represented_non_grade_modifier_count"]) for row in rows) != 62:
        raise RuntimeError("Repaired-event modifier representation drift")
    if len(block_by_focus) != 292:
        raise RuntimeError("Focus-to-explicit-block map collision")
    return rows, block_by_focus


def build_content_ready_editions(
    source_events: list[dict[str, str]],
    source_statements: list[dict[str, str]],
    source_pages: list[dict[str, str]],
    event_repairs: list[dict[str, object]],
    focus_repairs: list[dict[str, object]],
    card_hosts: list[dict[str, object]],
    local_components: list[dict[str, object]],
    name_slots: list[dict[str, object]],
) -> tuple[
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
]:
    repair_by_event = {str(row["event_id"]): row for row in event_repairs}
    focus_repair_counts = Counter(str(row["event_id"]) for row in focus_repairs)
    events: list[dict[str, object]] = []
    for source in source_events:
        event_id = source["event_id"]
        repair = repair_by_event.get(event_id)
        audible = audible_action_root(source["relation_resumption_voice_working_clause_de"])
        row: dict[str, object] = dict(source)
        row.update(
            {
                "audible_first_action_root": audible[0] if audible else "NONE",
                "grammar_boundary_status": (
                    "EXPLICIT_HEAD_BLOCK_REPAIR"
                    if repair
                    else "UNCHANGED_NO_SELECTED_VOICE_CONFLICT"
                ),
                "focus_voice_repair_count": focus_repair_counts[event_id],
                "represented_event_focus_count": (
                    repair["represented_event_focus_count"] if repair else 0
                ),
                "event_repair_id": repair["event_repair_id"] if repair else "NONE",
                "content_ready_boundary_clause_de": (
                    repair["content_ready_boundary_clause_de"]
                    if repair
                    else source["relation_resumption_voice_working_clause_de"]
                ),
                "gdt580_exact_roundtrip_de": source[
                    "relation_resumption_voice_working_clause_de"
                ],
                "gdt581_guard": (
                    "REPAIRED_EVENTS_USE_FOCUS_EXACT_HEAD_BLOCKS__"
                    "UNCHANGED_EVENTS_RETAIN_GDT580__EXACT_BACKCHANNEL"
                ),
            }
        )
        events.append(row)
    if len(events) != 5122 or len({row["event_id"] for row in events}) != 5122:
        raise RuntimeError("Content-ready event edition identity drift")

    event_by_id = {str(row["event_id"]): row for row in events}
    statements: list[dict[str, object]] = []
    for source in source_statements:
        event_ids = source["event_ids"].split("|")
        if any(event_by_id[event_id]["statement_id"] != source["statement_id"] for event_id in event_ids):
            raise RuntimeError(f"Statement event membership drift at {source['statement_id']}")
        source_join = " ".join(
            str(event_by_id[event_id]["gdt580_exact_roundtrip_de"])
            for event_id in event_ids
        )
        if source_join != source["relation_resumption_voice_working_reading_de"]:
            raise RuntimeError(f"GDT580 statement backchannel drift at {source['statement_id']}")
        target_join = " ".join(
            str(event_by_id[event_id]["content_ready_boundary_clause_de"])
            for event_id in event_ids
        )
        changed_ids = [
            event_id
            for event_id in event_ids
            if event_by_id[event_id]["grammar_boundary_status"]
            == "EXPLICIT_HEAD_BLOCK_REPAIR"
        ]
        row = dict(source)
        row.update(
            {
                "grammar_content_boundary_reading_de": target_join,
                "gdt580_exact_roundtrip_de": source_join,
                "grammar_boundary_changed": "YES" if changed_ids else "NO",
                "grammar_boundary_changed_event_count": len(changed_ids),
                "grammar_boundary_changed_event_ids": (
                    "|".join(changed_ids) if changed_ids else "NONE"
                ),
                "focus_voice_repair_count": sum(
                    int(event_by_id[event_id]["focus_voice_repair_count"])
                    for event_id in event_ids
                ),
                "gdt581_guard": "STATEMENT_REBUILT_ONLY_FROM_FIXED_EVENT_IDS__GDT580_BACKCHANNEL_EXACT",
            }
        )
        statements.append(row)
    if len(statements) != 793 or len({row["statement_id"] for row in statements}) != 793:
        raise RuntimeError("Content-ready statement edition identity drift")

    statement_by_id = {str(row["statement_id"]): row for row in statements}
    cards_by_page: Counter[str] = Counter(str(row["physical_page"]) for row in card_hosts)
    components_by_page: Counter[str] = Counter(
        str(row["physical_page"]) for row in local_components
    )
    names_by_page: Counter[str] = Counter(str(row["physical_page"]) for row in name_slots)
    pages: list[dict[str, object]] = []
    for source in source_pages:
        page = source["physical_page"]
        page_events = [row for row in events if row["physical_page"] == page]
        changed_event_ids = [
            str(row["event_id"])
            for row in page_events
            if row["grammar_boundary_status"] == "EXPLICIT_HEAD_BLOCK_REPAIR"
        ]
        page_statement_ids = {
            str(row["statement_id"]) for row in page_events
        }
        changed_statements = [
            statement_id
            for statement_id in page_statement_ids
            if statement_by_id[statement_id]["grammar_boundary_changed"] == "YES"
        ]
        row = dict(source)
        row.update(
            {
                "grammar_boundary_changed_event_count": len(changed_event_ids),
                "grammar_boundary_changed_statement_count": len(changed_statements),
                "focus_voice_repair_count": sum(
                    int(event_by_id[event_id]["focus_voice_repair_count"])
                    for event_id in changed_event_ids
                ),
                "local_card_count": cards_by_page[page],
                "local_component_count": components_by_page[page],
                "local_name_slot_count": names_by_page[page],
                "page_grammar_boundary_changed": "YES" if changed_event_ids else "NO",
                "gdt581_page_status": "COMPLETE_RUNNING_AND_LOCAL_BOUNDARY_PAGE",
                "gdt581_guard": "FIXED_PAGE_MEMBERSHIP__LOCAL_CARDS_LEDGERED_SEPARATELY",
            }
        )
        pages.append(row)
    if len(pages) != 30 or sum(int(row["local_card_count"]) for row in pages) != 744:
        raise RuntimeError("Content-ready page/local coverage drift")
    return events, statements, pages


def write_book(
    path: Path,
    pages: list[dict[str, object]],
    statements: list[dict[str, object]],
    card_hosts: list[dict[str, object]],
    name_slots: list[dict[str, object]],
) -> None:
    statements_by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in statements:
        statements_by_page[str(row["physical_page"])].append(row)
    cards_by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in card_hosts:
        cards_by_page[str(row["physical_page"])].append(row)
    names_by_card: Counter[str] = Counter(str(row["source_event_id"]) for row in name_slots)

    lines = [
        "# GDT581 grammar/content-boundary thirty-page edition",
        "",
        "This is an exploratory structural reading, not a plaintext translation.",
        "Square-bracket links identify written slots and exact governors. Concrete",
        "substances, plant parts, illnesses and operations remain unfilled.",
        "",
    ]
    for page in pages:
        physical_page = str(page["physical_page"])
        lines.extend(
            [
                f"## {physical_page}",
                "",
                (
                    f"Running events: {page['event_count']}; statements: "
                    f"{page['statement_count']}; repaired focus links: "
                    f"{page['focus_voice_repair_count']}; local cards: "
                    f"{page['local_card_count']}."
                ),
                "",
            ]
        )
        for statement in statements_by_page[physical_page]:
            lines.extend(
                [
                    f"### {statement['statement_id']} — {statement['owner_id']}",
                    "",
                    str(statement["grammar_content_boundary_reading_de"]),
                    "",
                ]
            )
        local_cards = cards_by_page.get(physical_page, [])
        if local_cards:
            lines.extend(
                [
                    "### Local-card layer",
                    "",
                    "| Card | Locus | Owner | Surface | Components | Name slots | Host |",
                    "|---|---|---|---|---|---:|---|",
                ]
            )
            for card in local_cards:
                values = [
                    card["source_event_id"],
                    card["locus"],
                    card["owner_de"],
                    card["surface"],
                    card["component_recipe"],
                    names_by_card[str(card["source_event_id"])],
                    card["local_card_host_key"],
                ]
                escaped = [str(value).replace("|", "\\|") for value in values]
                lines.append("| " + " | ".join(escaped) + " |")
            lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def build_result(
    complete_slots: list[dict[str, object]],
    content_carriers: list[dict[str, object]],
    control_slots: list[dict[str, object]],
    aliases: list[dict[str, object]],
    focus_hosts: list[dict[str, object]],
    reconciliations: list[dict[str, object]],
    safe_exceptions: list[dict[str, object]],
    focus_repairs: list[dict[str, object]],
    event_repairs: list[dict[str, object]],
    statements: list[dict[str, object]],
    pages: list[dict[str, object]],
    local_components: list[dict[str, object]],
    name_slots: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "experiment_id": "GDT581",
        "status": STATUS,
        "complete_slot_count": len(complete_slots),
        "content_carrier_count": len(content_carriers),
        "control_host_only_count": len(control_slots),
        "inherited_alias_count": len(aliases),
        "focus_host_count": len(focus_hosts),
        "final_recipe_reconciliation_count": len(reconciliations),
        "grade_envelope_count": 333,
        "grade_cross_boundary_hazard_count": 18,
        "non_grade_modifier_host_count": 1810,
        "cross_card_relation_slot_count": 25,
        "safe_already_explicit_focus_count": len(safe_exceptions),
        "focus_voice_repair_count": len(focus_repairs),
        "voice_repaired_event_count": len(event_repairs),
        "fully_represented_focus_count_in_repaired_events": sum(
            int(row["represented_event_focus_count"]) for row in event_repairs
        ),
        "fully_represented_non_grade_modifier_count_in_repaired_events": sum(
            int(row["represented_non_grade_modifier_count"])
            for row in event_repairs
        ),
        "voice_repaired_statement_count": sum(
            row["grammar_boundary_changed"] == "YES" for row in statements
        ),
        "voice_repaired_page_count": sum(
            row["page_grammar_boundary_changed"] == "YES" for row in pages
        ),
        "event_count": 5122,
        "statement_count": len(statements),
        "page_count": len(pages),
        "local_card_count": 744,
        "local_component_count": len(local_components),
        "name_slot_count": len(name_slots),
        "exact_gdt580_event_roundtrip_count": 5122,
        "exact_gdt580_statement_roundtrip_count": 793,
        "zero_unowned_slot_count": 0,
        "no_concrete_content_meaning_added": True,
        "structural_tags_distinct_from_english_translation": True,
        "input_sha256": {name: sha256(path) for name, path in INPUTS.items()},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=BASE / "artifacts")
    args = parser.parse_args()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    data = {name: read_tsv(path) for name, path in INPUTS.items()}
    expected_counts = {
        "gdt580_events": 5122,
        "gdt580_statements": 793,
        "gdt580_pages": 30,
        "gdt580_slots": 6,
        "gdt579_scope_slots": 34,
        "gdt577_repeat_slots": 125,
        "gdt407_attachments": 5051,
        "gdt515_attachments": 621,
        "gdt515_old_events": 5122,
        "gdt416_clauses": 4576,
        "gdt416_inherited_actions": 1598,
        "gdt416_inherited_arguments": 2096,
        "gdt539_context_events": 546,
        "gdt558_grade_assignments": 333,
        "gdt558_grade_hazards": 18,
        "gdt567_voice_cards": 39,
        "gdt568_action_cells": 45,
        "gdt515_local_cards": 744,
        "gdt479_local_events": 183,
        "gdt513_local_events": 510,
        "gdt515_local_51": 51,
        "gdt471_name_templates": 89,
        "gdt472_complete_templates": 107,
    }
    observed_counts = {name: len(rows) for name, rows in data.items()}
    if observed_counts != expected_counts:
        raise RuntimeError(f"Input cardinality drift: {observed_counts}")

    events = data["gdt580_events"]
    statements = data["gdt580_statements"]
    event_by_id = unique_index(events, "event_id", "GDT580 event")
    statement_by_id = unique_index(statements, "statement_id", "GDT580 statement")
    old_recipe_by_event = {
        (
            row["global_running_event_id"]
            if row["global_running_event_id"].startswith("G407-")
            else row["source_replay_event_id"]
        ): row["component_recipe"]
        for row in data["gdt515_old_events"]
    }
    if len(old_recipe_by_event) != 5122 or set(old_recipe_by_event) != set(event_by_id):
        raise RuntimeError("Old/final event identity drift")
    if any(
        row.get("physical_page", "").startswith("f84")
        for rows in data.values()
        for row in rows
    ):
        raise RuntimeError("Forbidden f84/f84r material reached GDT581")

    grade_by_key: dict[tuple[str, int], dict[str, str]] = {}
    for row in data["gdt558_grade_assignments"]:
        key = (row["event_id"], int(row["grade_atom_position"]))
        if key in grade_by_key:
            raise RuntimeError(f"Duplicate grade assignment: {key}")
        if row["recipe"] != event_by_id[row["event_id"]]["final_context_recipe"]:
            raise RuntimeError(f"Grade final-recipe drift at {row['event_id']}")
        grade_position = int(row["grade_atom_position"])
        if atoms(row["recipe"])[grade_position - 1] != row["grade"]:
            raise RuntimeError(f"Grade final coordinate drift at {row['event_id']}")
        grade_by_key[key] = row

    normalized_sources = [
        normalize_attachment_row(row, "GDT407", old_recipe_by_event)
        for row in data["gdt407_attachments"]
    ] + [
        normalize_attachment_row(row, "GDT515", old_recipe_by_event)
        for row in data["gdt515_attachments"]
    ]
    focus_hosts, reconciliations = reconcile_focus_attachments(
        normalized_sources, event_by_id, old_recipe_by_event, grade_by_key
    )
    aliases = build_inherited_aliases(
        data["gdt416_inherited_actions"],
        data["gdt416_inherited_arguments"],
        data["gdt539_context_events"],
        event_by_id,
    )
    card_hosts = build_local_card_hosts(
        data["gdt515_local_cards"],
        data["gdt479_local_events"],
        data["gdt513_local_events"],
        data["gdt515_local_51"],
    )
    local_components = build_local_components(card_hosts)
    name_slots = build_name_slots(
        data["gdt471_name_templates"], data["gdt472_complete_templates"], card_hosts
    )
    modifier_hosts = build_non_grade_modifier_hosts(
        events,
        focus_hosts,
        aliases,
        data["gdt577_repeat_slots"],
        data["gdt579_scope_slots"],
    )
    running_slots = build_running_slots(events, focus_hosts, modifier_hosts)
    complete_slots, content_carriers, control_slots = combine_complete_slots(
        running_slots, local_components, name_slots
    )
    cross_relations = build_cross_card_relations(focus_hosts, event_by_id)
    safe_exceptions = build_safe_focus_exceptions(
        focus_hosts, data["gdt580_slots"]
    )
    focus_repairs = select_voice_repairs(focus_hosts, event_by_id)
    event_repairs, _ = build_event_voice_repairs(
        focus_repairs,
        focus_hosts,
        running_slots,
        event_by_id,
        data["gdt567_voice_cards"],
        data["gdt568_action_cells"],
        data["gdt579_scope_slots"],
    )
    repaired_focus_ids = {str(row["focus_host_id"]) for row in focus_repairs}
    safe_focus_ids = {str(row["focus_host_id"]) for row in safe_exceptions}
    for row in cross_relations:
        focus_id = str(row["focus_host_id"])
        if focus_id in repaired_focus_ids:
            row["gdt581_voice_disposition"] = "EXPLICIT_HEAD_BLOCK_REPAIR"
        elif focus_id in safe_focus_ids:
            row["gdt581_voice_disposition"] = "SAFE_ALREADY_EXPLICIT_GDT580"
        else:
            raise RuntimeError(f"Cross-card relation lacks voice disposition: {focus_id}")
    if Counter(row["gdt581_voice_disposition"] for row in cross_relations) != Counter(
        {"EXPLICIT_HEAD_BLOCK_REPAIR": 23, "SAFE_ALREADY_EXPLICIT_GDT580": 2}
    ):
        raise RuntimeError("Cross-card relation voice-disposition drift")
    content_events, content_statements, content_pages = build_content_ready_editions(
        events,
        statements,
        data["gdt580_pages"],
        event_repairs,
        focus_repairs,
        card_hosts,
        local_components,
        name_slots,
    )
    result = build_result(
        complete_slots,
        content_carriers,
        control_slots,
        aliases,
        focus_hosts,
        reconciliations,
        safe_exceptions,
        focus_repairs,
        event_repairs,
        content_statements,
        content_pages,
        local_components,
        name_slots,
    )

    write_tsv(out / "gdt581_15889_complete_slot_ledger.tsv", complete_slots)
    write_tsv(out / "gdt581_13702_content_carrier_hosts.tsv", content_carriers)
    write_tsv(out / "gdt581_2187_control_host_slots.tsv", control_slots)
    write_tsv(out / "gdt581_13809_running_slot_hosts.tsv", running_slots)
    write_tsv(out / "gdt581_4026_inherited_alias_edges.tsv", aliases)
    write_tsv(out / "gdt581_5672_focus_reconciliation.tsv", focus_hosts)
    write_tsv(out / "gdt581_8_final_recipe_reconciliations.tsv", reconciliations)
    write_tsv(out / "gdt581_333_grade_envelope_hosts.tsv", data["gdt558_grade_assignments"])
    write_tsv(out / "gdt581_18_grade_cross_boundary_hazards.tsv", data["gdt558_grade_hazards"])
    write_tsv(out / "gdt581_1810_non_grade_modifier_hosts.tsv", modifier_hosts)
    write_tsv(out / "gdt581_25_cross_card_relation_slots.tsv", cross_relations)
    write_tsv(out / "gdt581_2_safe_focus_exceptions.tsv", safe_exceptions)
    write_tsv(out / "gdt581_269_focus_voice_repairs.tsv", focus_repairs)
    write_tsv(out / "gdt581_232_event_voice_repairs.tsv", event_repairs)
    write_tsv(out / "gdt581_744_local_card_hosts.tsv", card_hosts)
    write_tsv(out / "gdt581_1973_local_component_hosts.tsv", local_components)
    write_tsv(out / "gdt581_107_name_core_slots.tsv", name_slots)
    write_tsv(out / "gdt581_5122_content_ready_event_edition.tsv", content_events)
    write_tsv(out / "gdt581_793_content_ready_statement_edition.tsv", content_statements)
    write_tsv(out / "gdt581_30_page_boundary_profiles.tsv", content_pages)
    write_book(
        out / "GDT581_GRAMMAR_CONTENT_BOUNDARY_THIRTY_PAGE_EDITION.md",
        content_pages,
        content_statements,
        card_hosts,
        name_slots,
    )
    (out / "gdt581_result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print(
        json.dumps(
            {
                "complete_slots": len(complete_slots),
                "content_carriers": len(content_carriers),
                "control_slots": len(control_slots),
                "focus_hosts": len(focus_hosts),
                "aliases": len(aliases),
                "local_components": len(local_components),
                "name_slots": len(name_slots),
                "cross_relations": len(cross_relations),
                "focus_voice_repairs": len(focus_repairs),
                "voice_repaired_events": len(event_repairs),
                "safe_focus_exceptions": len(safe_exceptions),
                "status": STATUS,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
