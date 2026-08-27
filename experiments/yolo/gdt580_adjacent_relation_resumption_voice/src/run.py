#!/usr/bin/env python3
"""Voice three raw-adjacent relation pairs by explicit modifier resumption."""

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
BASE = ROOT / "experiments/yolo/gdt580_adjacent_relation_resumption_voice"
OUT = BASE / "artifacts"
G574 = ROOT / "experiments/yolo/gdt574_adjacent_action_count_voice/artifacts"
G575 = ROOT / "experiments/yolo/gdt575_repeated_relation_modifier_scope_atlas/artifacts"
G579 = ROOT / "experiments/yolo/gdt579_mixed_outer_inner_scope_voice/artifacts"
G515 = ROOT / "experiments/yolo/gdt515_second_random_four_page_full_admission/artifacts"
INPUTS = {
    "gdt579_events": G579 / "gdt579_5122_mixed_scope_event_edition.tsv",
    "gdt579_statements": G579 / "gdt579_793_mixed_scope_statement_edition.tsv",
    "gdt579_pages": G579 / "gdt579_30_page_mixed_scope_profiles.tsv",
    "gdt575_duplicate_groups": G575 / "gdt575_96_exact_duplicate_phrase_groups.tsv",
    "gdt515_attachments": G515 / "gdt515_factorized_attachments.tsv",
    "gdt574_events": G574 / "gdt574_5122_action_count_event_edition.tsv",
    "gdt574_statements": G574 / "gdt574_793_action_count_statement_edition.tsv",
}
STATUS = (
    "PASS_3_RAW_ADJACENT_RELATION_PAIRS__1_MODIFIER_RESUMPTION_OPERATOR__"
    "3_EXPLICIT_FORMS__6_WRITTEN_SLOTS__3_EVENT_CARDS__5122_EXACT_ROUNDTRIPS"
)


# GDT575 chooses identities and raw positions.  This finite table chooses only
# the German realization of the already selected two-slot construction.
CARDS: dict[str, dict[str, object]] = {
    "G407-E0152": {
        "assignment_id": "GDT580-A01",
        "duplicate_group_id": "GDT575-D004",
        "root": "O",
        "recipe": "D_ADDR+L+O+O",
        "positions": (2, 3),
        "meaning_class": "EXECUTION_EQUIVALENCE",
        "source_phrase": "als Ausführung",
        "source_fragment": "als Ausführung und als Ausführung",
        "first_realization": "als Ausführung",
        "explicit_modifier_realization": "dieselbe Ausführungsangabe nochmals",
        "target_fragment": (
            "als Ausführung; dieselbe Ausführungsangabe nochmals"
        ),
        "slot_expansion_fragment": "als Ausführung; als Ausführung",
        "placement_mode": "IN_PLACE_AFTER_INHERITED_ACTION",
        "expected_source_clause": (
            "Im laufenden Gang wähle denselben laufenden Eintrag; über die "
            "Eintragsverbindung; als Ausführung und als Ausführung; an der D-Stelle."
        ),
        "target_clause": (
            "Im laufenden Gang wähle denselben laufenden Eintrag; über die "
            "Eintragsverbindung; als Ausführung; dieselbe Ausführungsangabe "
            "nochmals; an der D-Stelle."
        ),
        "slot_expansion_clause": (
            "Im laufenden Gang wähle denselben laufenden Eintrag; über die "
            "Eintragsverbindung; als Ausführung; als Ausführung; an der D-Stelle."
        ),
    },
    "G407-E1846": {
        "assignment_id": "GDT580-A02",
        "duplicate_group_id": "GDT575-D041",
        "root": "D_ADDR",
        "recipe": "OT+D_ADDR+D_ADDR+Y+AR",
        "positions": (1, 2),
        "meaning_class": "LOCATIVE_RESUMPTION",
        "source_phrase": "an der D-Stelle",
        "source_fragment": "an der D-Stelle und an der D-Stelle",
        "first_realization": "an der D-Stelle",
        "explicit_modifier_realization": "dieselbe Stellenangabe nochmals",
        "target_fragment": "an der D-Stelle; dieselbe Stellenangabe nochmals",
        "slot_expansion_fragment": "an der D-Stelle; an der D-Stelle",
        "placement_mode": "IN_PLACE_AFTER_INHERITED_ACTION",
        "expected_source_clause": (
            "Danach im laufenden Gang: halte den Stationsposten; an der D-Stelle "
            "und an der D-Stelle; von der Ausgangsstation."
        ),
        "target_clause": (
            "Danach im laufenden Gang: halte den Stationsposten; an der D-Stelle; "
            "dieselbe Stellenangabe nochmals; von der Ausgangsstation."
        ),
        "slot_expansion_clause": (
            "Danach im laufenden Gang: halte den Stationsposten; an der D-Stelle; "
            "an der D-Stelle; von der Ausgangsstation."
        ),
    },
    "G515-E0379": {
        "assignment_id": "GDT580-A03",
        "duplicate_group_id": "GDT575-D093",
        "root": "AL",
        "recipe": "AL+AL+SH+E+DY",
        "positions": (0, 1),
        "meaning_class": "DIRECTIONAL_RESUMPTION",
        "source_phrase": "zur Zielspalte",
        "source_fragment": "zur Zielspalte und zur Zielspalte",
        "first_realization": "zur Zielspalte",
        "explicit_modifier_realization": "dieselbe Zielangabe nochmals",
        "target_fragment": "zur Zielspalte; dieselbe Zielangabe nochmals",
        "slot_expansion_fragment": "zur Zielspalte; zur Zielspalte",
        "placement_mode": "EXPLICIT_PREVIOUS_T_HEAD_BEFORE_CURRENT_SH",
        "expected_source_clause": (
            "Halte denselben laufenden Eintrag fest; zur Zielspalte und zur "
            "Zielspalte; auf Grad I; schließe den Schritt."
        ),
        "target_clause": (
            "Beim vorangehenden Festlegen: zur Zielspalte; dieselbe Zielangabe "
            "nochmals. Halte denselben laufenden Eintrag fest; auf Grad I; "
            "schließe den Schritt."
        ),
        "slot_expansion_clause": (
            "Beim vorangehenden Festlegen: zur Zielspalte; zur Zielspalte. Halte "
            "denselben laufenden Eintrag fest; auf Grad I; schließe den Schritt."
        ),
    },
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise RuntimeError(f"Refusing to write empty table: {path.name}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def occurrence_spans(text: str, needle: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    start = 0
    while True:
        found = text.find(needle, start)
        if found < 0:
            return spans
        spans.append((found, found + len(needle)))
        start = found + len(needle)


def ensure_unique_ids(rows: list[dict[str, str]], key: str, label: str) -> None:
    values = [row[key] for row in rows]
    if len(values) != len(set(values)):
        raise RuntimeError(f"Duplicate {label} identity")


def render_target(source_clause: str, card: dict[str, object]) -> str:
    if source_clause != str(card["expected_source_clause"]):
        raise RuntimeError(f"Current source-clause drift for {card['assignment_id']}")
    if "target_clause" in card:
        return str(card["target_clause"])
    source_fragment = str(card["source_fragment"])
    if source_clause.count(source_fragment) != 1:
        raise RuntimeError(f"Source-fragment ambiguity for {card['assignment_id']}")
    return source_clause.replace(source_fragment, str(card["target_fragment"]), 1)


def render_slot_expansion(source_clause: str, card: dict[str, object]) -> str:
    # The AL pair is fronted because both fixed GDT515 AL attachments select the
    # preceding T head.  Its two-slot expansion keeps raw AL+AL before current
    # SH; the separate inverse channel still recovers GDT579 byte for byte.
    if "slot_expansion_clause" in card:
        return str(card["slot_expansion_clause"])
    source_fragment = str(card["source_fragment"])
    if source_clause.count(source_fragment) != 1:
        raise RuntimeError(f"Source-fragment ambiguity for {card['assignment_id']}")
    return source_clause.replace(
        source_fragment, str(card["slot_expansion_fragment"]), 1
    )


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    source_events = read_tsv(INPUTS["gdt579_events"])
    source_statements = read_tsv(INPUTS["gdt579_statements"])
    source_pages = read_tsv(INPUTS["gdt579_pages"])
    duplicate_groups = read_tsv(INPUTS["gdt575_duplicate_groups"])
    gdt515_attachments = read_tsv(INPUTS["gdt515_attachments"])
    old_events = read_tsv(INPUTS["gdt574_events"])
    old_statements = read_tsv(INPUTS["gdt574_statements"])

    if [len(source_events), len(source_statements), len(source_pages)] != [5122, 793, 30]:
        raise RuntimeError("GDT579 complete-edition input count drift")
    if len(duplicate_groups) != 96:
        raise RuntimeError("GDT575 duplicate inventory count drift")
    if len(old_events) != 5122 or len(old_statements) != 793:
        raise RuntimeError("GDT574 baseline count drift")
    if any(
        row.get("physical_page", "").startswith("f84")
        for row in source_events + source_statements + source_pages
    ):
        raise RuntimeError("Forbidden f84/f84r material reached GDT580")
    ensure_unique_ids(source_events, "event_id", "event")
    ensure_unique_ids(source_statements, "statement_id", "statement")

    event_by_id = {row["event_id"]: row for row in source_events}
    old_event_by_id = {row["event_id"]: row for row in old_events}
    old_statement_by_id = {row["statement_id"]: row for row in old_statements}

    eligible = [
        row for row in duplicate_groups
        if row["duplicate_topology"] == "SAME_ROOT_RAW_ADJACENT"
    ]
    eligible_by_event = {row["event_id"]: row for row in eligible}
    if len(eligible) != 3 or set(eligible_by_event) != set(CARDS):
        raise RuntimeError("The exact-three GDT575 intake drifted")
    for event_id, card in CARDS.items():
        inventory = eligible_by_event[event_id]
        positions = tuple(
            int(value)
            for value in inventory["underlying_atom_positions_zero_based"].split("+")
        )
        expected_positions = tuple(int(value) for value in card["positions"])
        root = str(card["root"])
        if inventory["duplicate_group_id"] != card["duplicate_group_id"]:
            raise RuntimeError(f"GDT575 group identity drift at {event_id}")
        if inventory["underlying_atom_sequence"] != f"{root}+{root}":
            raise RuntimeError(f"GDT575 root identity drift at {event_id}")
        if positions != expected_positions or positions[1] != positions[0] + 1:
            raise RuntimeError(f"GDT575 raw adjacency drift at {event_id}")
        if inventory["scope"] != "PLAIN":
            raise RuntimeError(f"GDT575 plain-scope eligibility drift at {event_id}")
        if inventory["recommended_treatment"] != "COUNT_VOICE_CANDIDATE":
            raise RuntimeError(f"GDT575 eligibility label drift at {event_id}")

    al_head_rows = [
        row for row in gdt515_attachments
        if row["event_id"] == "G515-E0379" and row["focus_core"] == "AL"
    ]
    al_head_rows.sort(key=lambda row: int(row["focus_atom_ordinal"]))
    if len(al_head_rows) != 2:
        raise RuntimeError("Expected exactly two GDT515 AL attachment rows")
    if [row["focus_atom_ordinal"] for row in al_head_rows] != ["1", "2"]:
        raise RuntimeError("GDT515 AL focus positions drifted")
    for peer_ordinal, row in enumerate(al_head_rows, 1):
        required = {
            "selector_rule": "AL_AR_ORDERED_FALLBACK",
            "attachment_geometry": "PREVIOUS_CARD_ACTION",
            "selected_action_event_id": "G515-E0378",
            "selected_action_card_ordinal": "21",
            "selected_action_atom_ordinal": "3",
            "target_card_offset": "-1",
            "action_core": "T",
            "action_value_de": "EINSTELLEN",
            "head_kind": "ORDINARY_ACTION_HEAD",
            "duplicate_mode": "FREE_PLURAL_OR_REPEAT",
            "duplicate_role": f"FREE_PEER_{peer_ordinal}",
            "paired_focus_atom_ordinal": str(3 - peer_ordinal),
        }
        if any(row[key] != value for key, value in required.items()):
            raise RuntimeError(f"GDT515 previous-T binding drift at {row['factorized_id']}")
    if event_by_id["G515-E0378"]["final_context_recipe"] != "SH+CH+T+Y":
        raise RuntimeError("Previous T-head event recipe drift")
    if event_by_id["G515-E0378"]["statement_id"] != "G515-S042":
        raise RuntimeError("Previous T-head statement drift")
    if int(event_by_id["G515-E0378"]["card_ordinal_in_statement"]) + 1 != int(
        event_by_id["G515-E0379"]["card_ordinal_in_statement"]
    ):
        raise RuntimeError("Previous T-head card adjacency drift")

    al_attachment_by_position = {
        int(row["focus_atom_ordinal"]) - 1: row for row in al_head_rows
    }
    target_by_event: dict[str, str] = {}
    slot_expansion_by_event: dict[str, str] = {}
    assignment_rows: list[dict[str, object]] = []
    slot_rows_unordered: list[dict[str, object]] = []
    event_card_rows: list[dict[str, object]] = []

    for assignment_ordinal, (event_id, card) in enumerate(CARDS.items(), 1):
        source = event_by_id[event_id]
        source_clause = source["mixed_scope_voice_working_clause_de"]
        if source["final_context_recipe"] != card["recipe"]:
            raise RuntimeError(f"Current recipe drift at {event_id}")
        if source["scope_voice_status"] != "UNCHANGED_NON_SCOPE_EVENT":
            raise RuntimeError(f"GDT580 target overlaps a GDT579 scope event at {event_id}")
        atoms = source["final_context_recipe"].split("+")
        positions = tuple(int(value) for value in card["positions"])
        if any(atoms[position] != card["root"] for position in positions):
            raise RuntimeError(f"Current raw relation positions drift at {event_id}")

        target = render_target(source_clause, card)
        expansion = render_slot_expansion(source_clause, card)
        target_by_event[event_id] = target
        slot_expansion_by_event[event_id] = expansion
        source_phrase = str(card["source_phrase"])
        source_slot_spans = occurrence_spans(source_clause, source_phrase)
        if len(source_slot_spans) != 2:
            raise RuntimeError(f"Expected two exact source phrases at {event_id}")
        first_voice = str(card["first_realization"])
        second_voice = str(card["explicit_modifier_realization"])
        first_spans = occurrence_spans(target, first_voice)
        second_spans = occurrence_spans(target, second_voice)
        if len(first_spans) != 1 or len(second_spans) != 1:
            raise RuntimeError(f"Target resumption-span ambiguity at {event_id}")
        target_slot_spans = [first_spans[0], second_spans[0]]
        source_pair_start = source_clause.index(str(card["source_fragment"]))
        source_pair_end = source_pair_start + len(str(card["source_fragment"]))
        target_pair_start = target.index(str(card["target_fragment"]))
        target_pair_end = target_pair_start + len(str(card["target_fragment"]))

        attachment_ids: list[str] = []
        head_trace: list[str] = []
        for slot_within_pair, (raw_position, source_span, rendered_span) in enumerate(
            zip(positions, source_slot_spans, target_slot_spans, strict=True), 1
        ):
            attachment = (
                al_attachment_by_position.get(raw_position)
                if event_id == "G515-E0379" else None
            )
            if attachment:
                attachment_ids.append(attachment["factorized_id"])
                head_trace.append(
                    f"{attachment['attachment_geometry']}:"
                    f"{attachment['selected_action_event_id']}@"
                    f"{int(attachment['selected_action_atom_ordinal']) - 1}:"
                    f"{attachment['action_core']}"
                )
            slot_rows_unordered.append({
                "assignment_id": card["assignment_id"],
                "event_id": event_id,
                "statement_id": source["statement_id"],
                "relation_root": card["root"],
                "slot_within_pair": slot_within_pair,
                "raw_atom_position_zero_based": raw_position,
                "source_phrase_de": source_phrase,
                "source_phrase_start": source_span[0],
                "source_phrase_end": source_span[1],
                "target_realization_role": (
                    "LEXICAL_BASE"
                    if slot_within_pair == 1
                    else "EXPLICIT_MODIFIER_RESUMPTION"
                ),
                "target_realization_de": (
                    first_voice if slot_within_pair == 1 else second_voice
                ),
                "target_realization_start": rendered_span[0],
                "target_realization_end": rendered_span[1],
                "expanded_slot_phrase_de": source_phrase,
                "gdt515_attachment_id": (
                    attachment["factorized_id"] if attachment else "NONE"
                ),
                "gdt515_selector_rule": (
                    attachment["selector_rule"] if attachment else "NOT_APPLICABLE"
                ),
                "gdt515_attachment_geometry": (
                    attachment["attachment_geometry"] if attachment else "NOT_APPLICABLE"
                ),
                "selected_head_event_id": (
                    attachment["selected_action_event_id"]
                    if attachment else "INHERITED_CURRENT_VOICE"
                ),
                "selected_head_atom_position_zero_based": (
                    int(attachment["selected_action_atom_ordinal"]) - 1
                    if attachment else "NOT_APPLICABLE"
                ),
                "selected_head_root": (
                    attachment["action_core"] if attachment else "INHERITED_CURRENT_VOICE"
                ),
                "guard": (
                    "RAW_RELATION_SLOT_RETAINED__SECOND_SLOT_REALIZED_BY_"
                    "EXPLICIT_MODIFIER_REFERENCE"
                ),
            })

        assignment_rows.append({
            "assignment_ordinal": assignment_ordinal,
            "assignment_id": card["assignment_id"],
            "duplicate_group_id": card["duplicate_group_id"],
            "event_id": event_id,
            "statement_id": source["statement_id"],
            "physical_page": source["physical_page"],
            "register": source["register"],
            "owner_id": source["owner_id"],
            "surface": source["surface"],
            "final_context_recipe": source["final_context_recipe"],
            "state_status": source["state_status"],
            "relation_root": card["root"],
            "meaning_class": card["meaning_class"],
            "raw_atom_positions_zero_based": "|".join(
                str(position) for position in positions
            ),
            "written_slot_count": 2,
            "source_pair_fragment_de": card["source_fragment"],
            "target_first_phrase_de": first_voice,
            "target_explicit_modifier_form_de": second_voice,
            "target_resumption_fragment_de": card["target_fragment"],
            "full_two_slot_expansion_fragment_de": card["slot_expansion_fragment"],
            "placement_mode": card["placement_mode"],
            "gdt515_attachment_ids": "|".join(attachment_ids) or "NONE",
            "selected_head_trace": "|".join(head_trace) or "INHERITED_CURRENT_VOICE",
            "source_pair_start": source_pair_start,
            "source_pair_end": source_pair_end,
            "target_pair_start": target_pair_start,
            "target_pair_end": target_pair_end,
            "source_clause_de": source_clause,
            "target_clause_de": target,
            "slot_expansion_clause_de": expansion,
            "guard": "GDT575_EXACT_ADJACENT_IDENTITY__TWO_SLOT_RESUMPTION_ONLY",
        })
        event_card_rows.append({
            "event_card_ordinal": assignment_ordinal,
            "event_card_id": f"GDT580-E{assignment_ordinal:02d}",
            "assignment_id": card["assignment_id"],
            "event_id": event_id,
            "statement_id": source["statement_id"],
            "physical_page": source["physical_page"],
            "register": source["register"],
            "surface": source["surface"],
            "final_context_recipe": source["final_context_recipe"],
            "state_status": source["state_status"],
            "state_marker_sequence": source["state_marker_sequence"],
            "relation_root": card["root"],
            "raw_atom_positions_zero_based": "|".join(
                str(position) for position in positions
            ),
            "written_slot_count": 2,
            "gdt579_source_clause_de": source_clause,
            "gdt579_source_clause_sha256": text_sha256(source_clause),
            "target_clause_de": target,
            "target_clause_sha256": text_sha256(target),
            "full_two_slot_expansion_clause_de": expansion,
            "full_two_slot_expansion_sha256": text_sha256(expansion),
            "gdt579_inverse_clause_de": source_clause,
            "inverse_key": event_id,
            "gdt515_attachment_ids": "|".join(attachment_ids) or "NONE",
            "guard": "EVENT_ID_KEYED_INVERSE__TWO_RAW_SLOTS_AND_POSITIONS_RETAINED",
        })

    slot_rows_unordered.sort(
        key=lambda row: (str(row["assignment_id"]), int(row["slot_within_pair"]))
    )
    slot_rows = [
        {"written_slot_ordinal": ordinal, **row}
        for ordinal, row in enumerate(slot_rows_unordered, 1)
    ]
    if len(assignment_rows) != 3 or len(slot_rows) != 6 or len(event_card_rows) != 3:
        raise RuntimeError("Three-pair/six-slot artifact count drift")
    if Counter(row["target_realization_role"] for row in slot_rows) != Counter({
        "LEXICAL_BASE": 3, "EXPLICIT_MODIFIER_RESUMPTION": 3
    }):
        raise RuntimeError("Two-slot realization-role drift")

    operator_rows = [{
        "operator_ordinal": 1,
        "operator_id": "GDT580-R01",
        "operator_class": "TWO_SLOT_EXPLICIT_MODIFIER_RESUMPTION",
        "eligibility": "SAME_ROOT_RAW_ADJACENT_PLAIN_RELATION_MODIFIER_PAIR",
        "written_slot_count_per_assignment": 2,
        "voice_frame_de": (
            "{ERSTE_PHRASE}; dieselbe {MODIFIERKLASSE}-Angabe nochmals"
        ),
        "expansion_frame_de": "{ERSTE_PHRASE}; {ERSTE_PHRASE}",
        "eligible_relation_roots": "O|D_ADDR|AL",
        "meaning_classes": (
            "EXECUTION_EQUIVALENCE|LOCATIVE_RESUMPTION|DIRECTIONAL_RESUMPTION"
        ),
        "explicit_modifier_forms_de": (
            "dieselbe Ausführungsangabe nochmals|"
            "dieselbe Stellenangabe nochmals|"
            "dieselbe Zielangabe nochmals"
        ),
        "assignment_count": 3,
        "written_slot_count": 6,
        "guard": (
            "ONE_EDITORIAL_MODIFIER_OPERATOR__THREE_EXPLICIT_FORMS__"
            "NO_COUNT_VALUE"
        ),
    }]

    assignment_by_event = {row["event_id"]: row for row in assignment_rows}
    event_card_by_event = {row["event_id"]: row for row in event_card_rows}
    event_rows: list[dict[str, object]] = []
    for source in source_events:
        event_id = source["event_id"]
        target = target_by_event.get(
            event_id, source["mixed_scope_voice_working_clause_de"]
        )
        assignment = assignment_by_event.get(event_id)
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
            "gdt579_mixed_scope_voice_clause_de": (
                source["mixed_scope_voice_working_clause_de"]
            ),
            "relation_resumption_voice_working_clause_de": target,
            "gdt579_source_roundtrip_de": source["mixed_scope_voice_working_clause_de"],
            "full_two_slot_expansion_de": slot_expansion_by_event.get(event_id, target),
            "resumption_voice_status": (
                "CHANGED_EVENT_KEYED_MODIFIER_RESUMPTION_CARD"
                if assignment else "UNCHANGED_NON_TARGET"
            ),
            "assignment_id": assignment["assignment_id"] if assignment else "NONE",
            "resumption_root": assignment["relation_root"] if assignment else "NONE",
            "written_slot_count": assignment["written_slot_count"] if assignment else 0,
            "guard": "EVENT_ID_KEYED_EDITION__GDT579_SOURCE_ROUNDTRIP_EXACT",
        })
    if len(event_rows) != 5122:
        raise RuntimeError("Complete event-edition count drift")
    final_event_by_id = {str(row["event_id"]): row for row in event_rows}
    for row in event_rows:
        event_id = str(row["event_id"])
        inverse = (
            event_card_by_event[event_id]["gdt579_inverse_clause_de"]
            if event_id in event_card_by_event
            else row["relation_resumption_voice_working_clause_de"]
        )
        if inverse != row["gdt579_mixed_scope_voice_clause_de"]:
            raise RuntimeError(f"Event identity inverse failed at {event_id}")

    changed_event_ids = set(CARDS)
    statement_rows: list[dict[str, object]] = []
    for source in source_statements:
        event_ids = source["event_ids"].split("|")
        source_rebuilt = " ".join(
            event_by_id[event_id]["mixed_scope_voice_working_clause_de"]
            for event_id in event_ids
        )
        if source_rebuilt != source["mixed_scope_voice_working_reading_de"]:
            raise RuntimeError(f"GDT579 statement source drift at {source['statement_id']}")
        target = " ".join(
            str(final_event_by_id[event_id]["relation_resumption_voice_working_clause_de"])
            for event_id in event_ids
        )
        changed_members = [event_id for event_id in event_ids if event_id in changed_event_ids]
        retained_scope = (
            [] if source["scope_changed_event_ids"] == "NONE"
            else source["scope_changed_event_ids"].split("|")
        )
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
            "gdt579_mixed_scope_voice_reading_de": (
                source["mixed_scope_voice_working_reading_de"]
            ),
            "relation_resumption_voice_working_reading_de": target,
            "gdt579_source_roundtrip_de": source["mixed_scope_voice_working_reading_de"],
            "resumption_statement_changed": "YES" if changed_members else "NO",
            "resumption_changed_event_count": len(changed_members),
            "resumption_changed_event_ids": "|".join(changed_members) or "NONE",
            "retained_gdt579_scope_event_ids": "|".join(retained_scope) or "NONE",
            "end_mode": source["end_mode"],
            "guard": (
                "STATEMENT_REBUILT_ONLY_FROM_EVENT_IDS__"
                "GDT579_SOURCE_ROUNDTRIP_EXACT"
            ),
        })
    if len(statement_rows) != 793:
        raise RuntimeError("Complete statement-edition count drift")

    final_statement_by_id = {
        str(row["statement_id"]): row for row in statement_rows
    }
    changed_statement_ids = {
        str(row["statement_id"])
        for row in statement_rows
        if row["resumption_statement_changed"] == "YES"
    }
    changed_pages = {
        event_by_id[event_id]["physical_page"] for event_id in changed_event_ids
    }
    page_rows: list[dict[str, object]] = []
    for source in source_pages:
        page = source["physical_page"]
        page_events = [row for row in event_rows if row["physical_page"] == page]
        page_statements = [
            row for row in statement_rows if row["physical_page"] == page
        ]
        changed_direct_events = [
            row for row in page_events
            if row["resumption_voice_status"]
            == "CHANGED_EVENT_KEYED_MODIFIER_RESUMPTION_CARD"
        ]
        changed_direct_statements = [
            row for row in page_statements
            if row["resumption_statement_changed"] == "YES"
        ]
        cumulative_events = [
            row for row in page_events
            if row["relation_resumption_voice_working_clause_de"]
            != old_event_by_id[str(row["event_id"])]["action_count_working_clause_de"]
        ]
        cumulative_statements = [
            row for row in page_statements
            if row["relation_resumption_voice_working_reading_de"]
            != old_statement_by_id[str(row["statement_id"])]["action_count_working_reading_de"]
        ]
        page_rows.append({
            "page_ordinal": source["page_ordinal"],
            "physical_page": page,
            "registers": source["registers"],
            "event_count": source["event_count"],
            "statement_count": source["statement_count"],
            "state_event_count": source["state_event_count"],
            "nonstate_event_count": source["nonstate_event_count"],
            "prior_gdt579_scope_changed_event_count": source["scope_changed_event_count"],
            "prior_gdt579_scope_changed_statement_count": (
                source["scope_changed_statement_count"]
            ),
            "resumption_changed_event_count": len(changed_direct_events),
            "resumption_changed_statement_count": len(changed_direct_statements),
            "cumulative_changed_event_count_against_gdt574": len(cumulative_events),
            "cumulative_changed_statement_count_against_gdt574": (
                len(cumulative_statements)
            ),
            "page_resumption_changed": "YES" if changed_direct_events else "NO",
            "page_status": source["page_status"],
            "guard": "SOURCE_PAGE_ORDER_MEMBERSHIP_AND_COUNTS_UNCHANGED",
        })
    if len(page_rows) != 30:
        raise RuntimeError("Complete page-profile count drift")

    cumulative_changed_event_ids = {
        str(row["event_id"])
        for row in event_rows
        if row["relation_resumption_voice_working_clause_de"]
        != old_event_by_id[str(row["event_id"])]["action_count_working_clause_de"]
    }
    cumulative_changed_statement_ids = {
        str(row["statement_id"])
        for row in statement_rows
        if row["relation_resumption_voice_working_reading_de"]
        != old_statement_by_id[str(row["statement_id"])]["action_count_working_reading_de"]
    }
    cumulative_changed_pages = {
        event_by_id[event_id]["physical_page"]
        for event_id in cumulative_changed_event_ids
    }

    write_tsv(OUT / "gdt580_1_resumption_operator.tsv", operator_rows)
    write_tsv(OUT / "gdt580_3_relation_pair_assignments.tsv", assignment_rows)
    write_tsv(OUT / "gdt580_6_written_slot_spans.tsv", slot_rows)
    write_tsv(OUT / "gdt580_3_event_cards.tsv", event_card_rows)
    write_tsv(OUT / "gdt580_5122_resumption_voice_event_edition.tsv", event_rows)
    write_tsv(OUT / "gdt580_793_resumption_voice_statement_edition.tsv", statement_rows)
    write_tsv(OUT / "gdt580_30_page_resumption_voice_profiles.tsv", page_rows)

    source_zweimal = sum(
        row["mixed_scope_voice_working_clause_de"].count("zweimal")
        for row in source_events
    )
    target_zweimal = sum(
        str(row["relation_resumption_voice_working_clause_de"]).count("zweimal")
        for row in event_rows
    )
    source_nochmals = sum(
        row["mixed_scope_voice_working_clause_de"].count("nochmals")
        for row in source_events
    )
    target_nochmals = sum(
        str(row["relation_resumption_voice_working_clause_de"]).count("nochmals")
        for row in event_rows
    )
    result = {
        "experiment_id": "GDT580",
        "status": STATUS,
        "input_sha256": {key: sha256(path) for key, path in INPUTS.items()},
        "event_count": len(event_rows),
        "statement_count": len(statement_rows),
        "page_count": len(page_rows),
        "gdt575_eligible_raw_adjacent_relation_pair_count": len(eligible),
        "resumption_operator_count": len(operator_rows),
        "meaning_class_count": len({row["meaning_class"] for row in assignment_rows}),
        "explicit_modifier_form_count": len({
            row["target_explicit_modifier_form_de"] for row in assignment_rows
        }),
        "relation_pair_assignment_count": len(assignment_rows),
        "written_slot_count": len(slot_rows),
        "lexical_base_slot_count": sum(
            row["target_realization_role"] == "LEXICAL_BASE" for row in slot_rows
        ),
        "explicit_modifier_resumption_slot_count": sum(
            row["target_realization_role"] == "EXPLICIT_MODIFIER_RESUMPTION"
            for row in slot_rows
        ),
        "event_card_count": len(event_card_rows),
        "gdt515_previous_t_head_binding_row_count": len(al_head_rows),
        "gdt515_previous_t_head_event_id": "G515-E0378",
        "changed_event_count_against_gdt579": len(changed_event_ids),
        "changed_nonstate_event_count_against_gdt579": sum(
            event_by_id[event_id]["state_status"] == "NONSTATE_CARD"
            for event_id in changed_event_ids
        ),
        "changed_state_event_count_against_gdt579": sum(
            event_by_id[event_id]["state_status"] == "STATE_CARD"
            for event_id in changed_event_ids
        ),
        "changed_statement_count_against_gdt579": len(changed_statement_ids),
        "changed_page_count_against_gdt579": len(changed_pages),
        "cumulative_changed_event_count_against_gdt574": (
            len(cumulative_changed_event_ids)
        ),
        "cumulative_changed_statement_count_against_gdt574": (
            len(cumulative_changed_statement_ids)
        ),
        "cumulative_changed_page_count_against_gdt574": (
            len(cumulative_changed_pages)
        ),
        "gdt579_scope_event_overlap_count": sum(
            event_by_id[event_id]["scope_voice_status"]
            != "UNCHANGED_NON_SCOPE_EVENT"
            for event_id in changed_event_ids
        ),
        "changed_statement_retained_gdt579_scope_event_count": sum(
            0
            if final_statement_by_id[statement_id]["retained_gdt579_scope_event_ids"]
            == "NONE"
            else len(
                str(final_statement_by_id[statement_id]["retained_gdt579_scope_event_ids"])
                .split("|")
            )
            for statement_id in changed_statement_ids
        ),
        "source_zweimal_occurrence_count": source_zweimal,
        "target_zweimal_occurrence_count": target_zweimal,
        "source_nochmals_occurrence_count": source_nochmals,
        "target_nochmals_occurrence_count": target_nochmals,
        "new_nochmals_occurrence_count": target_nochmals - source_nochmals,
        "exact_event_id_roundtrip_count": sum(
            row["gdt579_source_roundtrip_de"]
            == row["gdt579_mixed_scope_voice_clause_de"]
            for row in event_rows
        ),
        "exact_statement_id_roundtrip_count": sum(
            row["gdt579_source_roundtrip_de"]
            == row["gdt579_mixed_scope_voice_reading_de"]
            for row in statement_rows
        ),
        "no_global_zweimal_added": target_zweimal == source_zweimal,
        "no_new_page": True,
        "no_new_event": True,
        "no_new_statement": True,
        "no_root_change": True,
        "no_recipe_change": True,
        "no_scope_change": True,
        "no_count_value_claim": True,
    }
    expected = {
        "changed_event_count_against_gdt579": 3,
        "changed_statement_count_against_gdt579": 3,
        "changed_page_count_against_gdt579": 3,
        "cumulative_changed_event_count_against_gdt574": 764,
        "cumulative_changed_statement_count_against_gdt574": 309,
        "cumulative_changed_page_count_against_gdt574": 28,
        "exact_event_id_roundtrip_count": 5122,
        "exact_statement_id_roundtrip_count": 793,
        "new_nochmals_occurrence_count": 3,
    }
    for key, value in expected.items():
        if result[key] != value:
            raise RuntimeError(f"Result drift for {key}: {result[key]} != {value}")
    if source_zweimal != 43 or target_zweimal != 43:
        raise RuntimeError("The inherited 43 action-count voices must remain unchanged")
    if result["gdt579_scope_event_overlap_count"] != 0:
        raise RuntimeError("GDT580 must not overlap a GDT579 scope target event")

    (OUT / "gdt580_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    statements_by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in statement_rows:
        statements_by_page[str(row["physical_page"])].append(row)
    lines = [
        "# GDT580 relation resumption voice edition",
        "",
        f"Status: `{STATUS}`",
        "",
    ]
    for page in page_rows:
        page_id = str(page["physical_page"])
        lines.extend([f"## {page_id} · {page['registers']}", ""])
        for statement in statements_by_page[page_id]:
            marker = (
                " · Wiederaufnahme-Stimme"
                if statement["resumption_statement_changed"] == "YES"
                else ""
            )
            lines.extend([
                f"### {statement['statement_id']}{marker}",
                "",
                str(statement["relation_resumption_voice_working_reading_de"]),
                "",
            ])
    (OUT / "GDT580_RESUMPTION_VOICE_THIRTY_PAGE_EDITION.md").write_text(
        "\n".join(lines).rstrip() + "\n", encoding="utf-8"
    )

    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
