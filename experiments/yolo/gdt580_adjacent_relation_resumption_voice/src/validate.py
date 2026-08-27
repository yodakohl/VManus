#!/usr/bin/env python3
"""Independent validation for GDT580's explicit modifier-resumption voice."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Iterable


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
G577 = ROOT / "experiments/yolo/gdt577_interrupted_modifier_attachment_topology/artifacts"
G579 = ROOT / "experiments/yolo/gdt579_mixed_outer_inner_scope_voice/artifacts"
G515 = ROOT / "experiments/yolo/gdt515_second_random_four_page_full_admission/artifacts"

INPUTS = {
    "events": G579 / "gdt579_5122_mixed_scope_event_edition.tsv",
    "statements": G579 / "gdt579_793_mixed_scope_statement_edition.tsv",
    "pages": G579 / "gdt579_30_page_mixed_scope_profiles.tsv",
    "duplicates": G575 / "gdt575_96_exact_duplicate_phrase_groups.tsv",
    "scope_pairs": G575 / "gdt575_17_outer_inner_scope_pairs.tsv",
    "interrupted": G577 / "gdt577_62_interrupted_group_topology.tsv",
    "gdt515_attachments": G515 / "gdt515_factorized_attachments.tsv",
    "gdt574_events": G574 / "gdt574_5122_action_count_event_edition.tsv",
    "gdt574_statements": G574 / "gdt574_793_action_count_statement_edition.tsv",
}
OUTPUTS = {
    "operator": OUT / "gdt580_1_resumption_operator.tsv",
    "assignments": OUT / "gdt580_3_relation_pair_assignments.tsv",
    "slots": OUT / "gdt580_6_written_slot_spans.tsv",
    "cards": OUT / "gdt580_3_event_cards.tsv",
    "events": OUT / "gdt580_5122_resumption_voice_event_edition.tsv",
    "statements": OUT / "gdt580_793_resumption_voice_statement_edition.tsv",
    "pages": OUT / "gdt580_30_page_resumption_voice_profiles.tsv",
    "book": OUT / "GDT580_RESUMPTION_VOICE_THIRTY_PAGE_EDITION.md",
    "result": OUT / "gdt580_result.json",
}
HASH_INPUTS = {
    "gdt579_events": INPUTS["events"],
    "gdt579_statements": INPUTS["statements"],
    "gdt579_pages": INPUTS["pages"],
    "gdt575_duplicate_groups": INPUTS["duplicates"],
    "gdt515_attachments": INPUTS["gdt515_attachments"],
    "gdt574_events": INPUTS["gdt574_events"],
    "gdt574_statements": INPUTS["gdt574_statements"],
}

STATUS = (
    "PASS_3_RAW_ADJACENT_RELATION_PAIRS__1_MODIFIER_RESUMPTION_OPERATOR__"
    "3_EXPLICIT_FORMS__6_WRITTEN_SLOTS__3_EVENT_CARDS__5122_EXACT_ROUNDTRIPS"
)
TARGET_IDS = ("G407-E0152", "G407-E1846", "G515-E0379")
TARGET_STATEMENTS = {"G407-S005", "G407-S194", "G515-S042"}
TARGET_PAGES = {"f1r", "f76r", "f66r"}
SEALED_FOLIO_RE = re.compile(r"(?<![A-Za-z0-9])f84r?(?![A-Za-z0-9])", re.IGNORECASE)

# Event-specific readings keep the validator independent of the builder's
# renderer and catch accidental text-keyed replacement or head attachment.
SPECS: dict[str, dict[str, object]] = {
    "G407-E0152": {
        "duplicate_id": "GDT575-D004",
        "root": "O",
        "positions": (2, 3),
        "source_base": "als Ausführung",
        "atlas_base": "als Ausführung",
        "source_fragment": "als Ausführung und als Ausführung",
        "target_base": "als Ausführung",
        "explicit_resumption": "dieselbe Ausführungsangabe nochmals",
        "target_fragment": "als Ausführung; dieselbe Ausführungsangabe nochmals",
        "expanded_fragment": "als Ausführung; als Ausführung",
        "target_clause": (
            "Im laufenden Gang wähle denselben laufenden Eintrag; "
            "über die Eintragsverbindung; als Ausführung; "
            "dieselbe Ausführungsangabe nochmals; "
            "an der D-Stelle."
        ),
        "expanded_clause": (
            "Im laufenden Gang wähle denselben laufenden Eintrag; "
            "über die Eintragsverbindung; als Ausführung; als Ausführung; "
            "an der D-Stelle."
        ),
        "placement": "IN_PLACE_AFTER_INHERITED_ACTION",
    },
    "G407-E1846": {
        "duplicate_id": "GDT575-D041",
        "root": "D_ADDR",
        "positions": (1, 2),
        "source_base": "an der D-Stelle",
        "atlas_base": "an der bezeichneten Stelle",
        "source_fragment": "an der D-Stelle und an der D-Stelle",
        "target_base": "an der D-Stelle",
        "explicit_resumption": "dieselbe Stellenangabe nochmals",
        "target_fragment": "an der D-Stelle; dieselbe Stellenangabe nochmals",
        "expanded_fragment": "an der D-Stelle; an der D-Stelle",
        "target_clause": (
            "Danach im laufenden Gang: halte den Stationsposten; "
            "an der D-Stelle; dieselbe Stellenangabe nochmals; "
            "von der Ausgangsstation."
        ),
        "expanded_clause": (
            "Danach im laufenden Gang: halte den Stationsposten; "
            "an der D-Stelle; an der D-Stelle; von der Ausgangsstation."
        ),
        "placement": "IN_PLACE_AFTER_INHERITED_ACTION",
    },
    "G515-E0379": {
        "duplicate_id": "GDT575-D093",
        "root": "AL",
        "positions": (0, 1),
        "source_base": "zur Zielspalte",
        "atlas_base": "zur Zielspalte",
        "source_fragment": "zur Zielspalte und zur Zielspalte",
        "target_base": "zur Zielspalte",
        "explicit_resumption": "dieselbe Zielangabe nochmals",
        "target_fragment": "zur Zielspalte; dieselbe Zielangabe nochmals",
        "expanded_fragment": "zur Zielspalte; zur Zielspalte",
        "target_clause": (
            "Beim vorangehenden Festlegen: zur Zielspalte; "
            "dieselbe Zielangabe nochmals. Halte denselben laufenden Eintrag "
            "fest; auf Grad I; schließe den Schritt."
        ),
        "expanded_clause": (
            "Beim vorangehenden Festlegen: zur Zielspalte; zur Zielspalte. "
            "Halte denselben laufenden Eintrag "
            "fest; auf Grad I; schließe den Schritt."
        ),
        "placement": "EXPLICIT_PREVIOUS_T_HEAD_BEFORE_CURRENT_SH",
    },
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unique_index(rows: Iterable[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    rows = list(rows)
    result = {row[key]: row for row in rows}
    if len(result) != len(rows):
        raise RuntimeError(f"duplicate {key}")
    return result


def positions(text: str, fragment: str) -> list[tuple[int, int]]:
    result: list[tuple[int, int]] = []
    start = 0
    while True:
        index = text.find(fragment, start)
        if index < 0:
            return result
        result.append((index, index + len(fragment)))
        start = index + len(fragment)


def pipe(values: Iterable[object]) -> str:
    return "|".join(str(value) for value in values)


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, observed: object, expected: object) -> None:
        checks.append(
            {
                "check": name,
                "expected": expected,
                "observed": observed,
                "status": "PASS" if observed == expected else "FAIL",
            }
        )

    source_events = read_tsv(INPUTS["events"])
    source_statements = read_tsv(INPUTS["statements"])
    source_pages = read_tsv(INPUTS["pages"])
    duplicate_rows = read_tsv(INPUTS["duplicates"])
    scope_pairs = read_tsv(INPUTS["scope_pairs"])
    interrupted = read_tsv(INPUTS["interrupted"])
    gdt515_attachments = read_tsv(INPUTS["gdt515_attachments"])
    gdt574_events = read_tsv(INPUTS["gdt574_events"])
    gdt574_statements = read_tsv(INPUTS["gdt574_statements"])

    operator = read_tsv(OUTPUTS["operator"])
    assignments = read_tsv(OUTPUTS["assignments"])
    slots = read_tsv(OUTPUTS["slots"])
    cards = read_tsv(OUTPUTS["cards"])
    events = read_tsv(OUTPUTS["events"])
    statements = read_tsv(OUTPUTS["statements"])
    pages = read_tsv(OUTPUTS["pages"])
    result = json.loads(OUTPUTS["result"].read_text(encoding="utf-8"))

    source_event_by_id = unique_index(source_events, "event_id")
    source_statement_by_id = unique_index(source_statements, "statement_id")
    source_page_by_id = unique_index(source_pages, "physical_page")
    event_by_id = unique_index(events, "event_id")
    page_by_id = unique_index(pages, "physical_page")
    old_event_by_id = unique_index(gdt574_events, "event_id")
    old_statement_by_id = unique_index(gdt574_statements, "statement_id")

    check("status", result.get("status"), STATUS)
    check(
        "source_counts",
        [len(source_events), len(source_statements), len(source_pages), len(duplicate_rows), len(scope_pairs), len(interrupted)],
        [5122, 793, 30, 96, 17, 62],
    )
    check(
        "output_counts",
        [len(operator), len(assignments), len(slots), len(cards), len(events), len(statements), len(pages)],
        [1, 3, 6, 3, 5122, 793, 30],
    )
    event_ordinals = [int(row["edition_event_ordinal"]) for row in events]
    statement_ordinals = [int(row["edition_statement_ordinal"]) for row in statements]
    page_ordinals = [int(row["page_ordinal"]) for row in pages]
    check(
        "event_ordinals",
        [len(event_ordinals), event_ordinals[:1], event_ordinals[-1:], event_ordinals == list(range(1, 5123))],
        [5122, [1], [5122], True],
    )
    check(
        "statement_ordinals",
        [len(statement_ordinals), statement_ordinals[:1], statement_ordinals[-1:], statement_ordinals == list(range(1, 794))],
        [793, [1], [793], True],
    )
    check(
        "page_ordinals",
        [len(page_ordinals), page_ordinals[:1], page_ordinals[-1:], page_ordinals == list(range(1, 31))],
        [30, [1], [30], True],
    )

    # Re-derive the target set solely from GDT575, not GDT580 output.
    eligible = [
        row for row in duplicate_rows
        if row["duplicate_topology"] == "SAME_ROOT_RAW_ADJACENT" and row["scope"] == "PLAIN"
    ]
    eligible_by_event = unique_index(eligible, "event_id")
    check("three_gdt575_candidates", tuple(eligible_by_event), TARGET_IDS)
    check(
        "candidate_duplicate_ids",
        {event_id: eligible_by_event[event_id]["duplicate_group_id"] for event_id in TARGET_IDS},
        {event_id: SPECS[event_id]["duplicate_id"] for event_id in TARGET_IDS},
    )
    candidate_source_exact = True
    for event_id, spec in SPECS.items():
        row = eligible_by_event[event_id]
        atoms = row["final_context_recipe"].split("+")
        raw_positions = tuple(int(value) for value in row["underlying_atom_positions_zero_based"].split("+"))
        candidate_source_exact &= raw_positions == spec["positions"]
        candidate_source_exact &= all(atoms[index] == spec["root"] for index in raw_positions)
        candidate_source_exact &= raw_positions[1] == raw_positions[0] + 1
        candidate_source_exact &= row["underlying_atom_sequence"] == f"{spec['root']}+{spec['root']}"
        candidate_source_exact &= row["action_atom_between"] == "NO"
        candidate_source_exact &= int(row["phrase_occurrence_count"]) == 2
        candidate_source_exact &= row["full_phrase_de"] == spec["atlas_base"]
    check("gdt575_candidate_fields_recomputed", candidate_source_exact, True)
    scope_event_ids = {row["event_id"] for row in scope_pairs}
    interrupted_event_ids = {row["event_id"] for row in interrupted}
    check("no_scope_pair_selected", sorted(set(TARGET_IDS) & scope_event_ids), [])
    check("no_interrupted_group_selected", sorted(set(TARGET_IDS) & interrupted_event_ids), [])

    # G515 supplies the authoritative reason for preposing AL before visible SH.
    al_attachments = [
        row for row in gdt515_attachments
        if row["event_id"] == "G515-E0379" and row["focus_core"] == "AL"
        and row["focus_atom_ordinal"] in {"1", "2"}
    ]
    al_attachments.sort(key=lambda row: int(row["focus_atom_ordinal"]))
    check("gdt515_al_attachment_count", len(al_attachments), 2)
    check("gdt515_al_attachment_ids", [row["factorized_id"] for row in al_attachments], ["G515-A00356", "G515-A00357"])
    check("gdt515_al_previous_head", [row["selected_action_event_id"] for row in al_attachments], ["G515-E0378", "G515-E0378"])
    check("gdt515_al_previous_root", [row["action_core"] for row in al_attachments], ["T", "T"])
    check("gdt515_al_selector", [row["selector_rule"] for row in al_attachments], ["AL_AR_ORDERED_FALLBACK", "AL_AR_ORDERED_FALLBACK"])
    check("gdt515_al_geometry", [row["attachment_geometry"] for row in al_attachments], ["PREVIOUS_CARD_ACTION", "PREVIOUS_CARD_ACTION"])
    check("gdt515_al_duplicate_mode", [row["duplicate_mode"] for row in al_attachments], ["FREE_PLURAL_OR_REPEAT", "FREE_PLURAL_OR_REPEAT"])
    check("gdt515_al_peer_roles", [row["duplicate_role"] for row in al_attachments], ["FREE_PEER_1", "FREE_PEER_2"])

    operator_blob = "|".join(operator[0].values())
    check("operator_trigger", "SAME_ROOT_RAW_ADJACENT" in operator_blob, True)
    check("operator_plain_scope", "PLAIN" in operator_blob, True)
    check("operator_class", operator[0]["operator_class"], "TWO_SLOT_EXPLICIT_MODIFIER_RESUMPTION")
    check(
        "operator_three_explicit_forms",
        operator[0]["explicit_modifier_forms_de"],
        "dieselbe Ausführungsangabe nochmals|dieselbe Stellenangabe nochmals|dieselbe Zielangabe nochmals",
    )
    check("deprecated_operator_deictic_field_absent", "deictic_forms_de" in operator[0], False)
    check("operator_not_count_or_scope", all(token not in operator_blob.lower() for token in ["zweimal", "outer", "inner", "außen", "innen"]), True)

    assignment_by_event = unique_index(assignments, "event_id")
    card_by_event = unique_index(cards, "event_id")
    check("assignment_event_set", tuple(assignment_by_event), TARGET_IDS)
    check("card_event_set", tuple(card_by_event), TARGET_IDS)
    check(
        "deprecated_assignment_deictic_field_absent",
        any("target_deictic_form_de" in row for row in assignments),
        False,
    )

    source_expected: dict[str, str] = {}
    target_expected: dict[str, str] = {}
    assignment_exact = True
    card_exact = True
    for event_id, spec in SPECS.items():
        source = source_event_by_id[event_id]["mixed_scope_voice_working_clause_de"]
        source_expected[event_id] = source
        target_expected[event_id] = str(spec["target_clause"])
        assignment = assignment_by_event[event_id]
        card = card_by_event[event_id]
        assignment_exact &= assignment["duplicate_group_id"] == spec["duplicate_id"]
        assignment_exact &= assignment["relation_root"] == spec["root"]
        assignment_exact &= assignment["raw_atom_positions_zero_based"] == pipe(spec["positions"])
        assignment_exact &= assignment["source_pair_fragment_de"] == spec["source_fragment"]
        assignment_exact &= assignment["target_first_phrase_de"] == spec["target_base"]
        assignment_exact &= assignment["target_explicit_modifier_form_de"] == spec["explicit_resumption"]
        assignment_exact &= assignment["target_resumption_fragment_de"] == spec["target_fragment"]
        assignment_exact &= assignment["full_two_slot_expansion_fragment_de"] == spec["expanded_fragment"]
        assignment_exact &= assignment["source_clause_de"] == source
        assignment_exact &= assignment["target_clause_de"] == spec["target_clause"]
        assignment_exact &= assignment["slot_expansion_clause_de"] == spec["expanded_clause"]
        source_pair_start = source.index(str(spec["source_fragment"]))
        target_pair_start = str(spec["target_clause"]).index(str(spec["target_fragment"]))
        assignment_exact &= int(assignment["source_pair_start"]) == source_pair_start
        assignment_exact &= int(assignment["source_pair_end"]) == source_pair_start + len(str(spec["source_fragment"]))
        assignment_exact &= int(assignment["target_pair_start"]) == target_pair_start
        assignment_exact &= int(assignment["target_pair_end"]) == target_pair_start + len(str(spec["target_fragment"]))
        assignment_exact &= int(assignment["written_slot_count"]) == 2
        assignment_exact &= assignment["placement_mode"] == spec["placement"]
        if event_id == "G515-E0379":
            assignment_exact &= assignment["gdt515_attachment_ids"] == "G515-A00356|G515-A00357"
            assignment_exact &= assignment["selected_head_trace"] == (
                "PREVIOUS_CARD_ACTION:G515-E0378@2:T|"
                "PREVIOUS_CARD_ACTION:G515-E0378@2:T"
            )
        else:
            assignment_exact &= assignment["gdt515_attachment_ids"] == "NONE"
        card_exact &= card["gdt579_source_clause_de"] == source
        card_exact &= card["target_clause_de"] == spec["target_clause"]
        card_exact &= card["gdt579_inverse_clause_de"] == source
        card_exact &= card["full_two_slot_expansion_clause_de"] == spec["expanded_clause"]
        card_exact &= card["assignment_id"] == assignment["assignment_id"]
        card_exact &= card["gdt579_source_clause_sha256"] == hashlib.sha256(source.encode("utf-8")).hexdigest()
        card_exact &= card["target_clause_sha256"] == hashlib.sha256(str(spec["target_clause"]).encode("utf-8")).hexdigest()
        card_exact &= card["full_two_slot_expansion_sha256"] == hashlib.sha256(str(spec["expanded_clause"]).encode("utf-8")).hexdigest()
    check("assignment_rows_exact", assignment_exact, True)
    check("event_cards_exact", card_exact, True)
    check(
        "three_explicit_modifier_forms",
        sorted({row["target_explicit_modifier_form_de"] for row in assignments}),
        sorted([
            "dieselbe Ausführungsangabe nochmals",
            "dieselbe Stellenangabe nochmals",
            "dieselbe Zielangabe nochmals",
        ]),
    )
    check("no_target_count_word", all("zweimal" not in target.lower() for target in target_expected.values()), True)
    check(
        "old_deictic_shortcuts_absent",
        all(
            forbidden not in (operator_blob + "|" + "|".join(target_expected.values())).lower()
            for forbidden in ("nochmals ebenso", "nochmals dort", "nochmals dorthin")
        ),
        True,
    )
    al_target = target_expected["G515-E0379"]
    check(
        "al_previous_t_voice_explicit_before_current_sh",
        [
            al_target.startswith("Beim vorangehenden Festlegen: zur Zielspalte; "),
            ". Halte denselben laufenden Eintrag fest" in al_target,
            al_target.index("zur Zielspalte") < al_target.index("Halte"),
            "Halte denselben laufenden Eintrag fest; zur Zielspalte" not in al_target,
        ],
        [True, True, True, True],
    )

    slots_by_event: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in slots:
        slots_by_event[row["event_id"]].append(row)
    slot_exact = set(slots_by_event) == set(TARGET_IDS)
    al_slot_trace_exact = True
    for event_id, spec in SPECS.items():
        event_slots = sorted(slots_by_event[event_id], key=lambda row: int(row["slot_within_pair"]))
        slot_exact &= len(event_slots) == 2
        if len(event_slots) != 2:
            continue
        source_clause = source_expected[event_id]
        target_clause = target_expected[event_id]
        source_occurrences = positions(source_clause, str(spec["source_base"]))
        expected_target_spans = [
            positions(target_clause, str(spec["target_base"]))[0],
            positions(target_clause, str(spec["explicit_resumption"]))[0],
        ]
        for index, row in enumerate(event_slots):
            source_span = (int(row["source_phrase_start"]), int(row["source_phrase_end"]))
            target_span = (int(row["target_realization_start"]), int(row["target_realization_end"]))
            slot_exact &= row["relation_root"] == spec["root"]
            slot_exact &= int(row["raw_atom_position_zero_based"]) == spec["positions"][index]
            slot_exact &= row["target_realization_role"] == ("LEXICAL_BASE" if index == 0 else "EXPLICIT_MODIFIER_RESUMPTION")
            slot_exact &= source_span == source_occurrences[index]
            slot_exact &= target_span == expected_target_spans[index]
            slot_exact &= row["source_phrase_de"] == source_clause[source_span[0] : source_span[1]]
            slot_exact &= row["target_realization_de"] == target_clause[target_span[0] : target_span[1]]
            slot_exact &= row["expanded_slot_phrase_de"].lower() == str(spec["source_base"]).lower()
            if event_id == "G515-E0379":
                old = al_attachments[index]
                al_slot_trace_exact &= row["gdt515_attachment_id"] == old["factorized_id"]
                al_slot_trace_exact &= row["gdt515_selector_rule"] == old["selector_rule"]
                al_slot_trace_exact &= row["gdt515_attachment_geometry"] == old["attachment_geometry"]
                al_slot_trace_exact &= row["selected_head_event_id"] == old["selected_action_event_id"]
                al_slot_trace_exact &= row["selected_head_atom_position_zero_based"] == str(int(old["selected_action_atom_ordinal"]) - 1)
                al_slot_trace_exact &= row["selected_head_root"] == old["action_core"]
    check("six_slot_positions_and_spans", slot_exact, True)
    check("al_slot_attachment_trace", al_slot_trace_exact, True)

    metadata_columns = [
        "edition_event_ordinal", "event_id", "statement_id", "card_ordinal_in_statement",
        "physical_page", "register", "owner_id", "surface", "final_context_recipe",
        "state_status", "state_marker_sequence",
    ]
    event_metadata_exact = True
    event_targets_exact = True
    event_roundtrip_exact = True
    changed_event_ids: list[str] = []
    for source, row in zip(source_events, events, strict=True):
        event_id = source["event_id"]
        expected_target = target_expected.get(event_id, source["mixed_scope_voice_working_clause_de"])
        event_metadata_exact &= all(row[column] == source[column] for column in metadata_columns)
        event_targets_exact &= row["gdt579_mixed_scope_voice_clause_de"] == source["mixed_scope_voice_working_clause_de"]
        event_targets_exact &= row["relation_resumption_voice_working_clause_de"] == expected_target
        event_roundtrip_exact &= row["gdt579_source_roundtrip_de"] == source["mixed_scope_voice_working_clause_de"]
        if event_id in SPECS:
            event_targets_exact &= row["full_two_slot_expansion_de"] == SPECS[event_id]["expanded_clause"]
            event_targets_exact &= row["resumption_voice_status"] == "CHANGED_EVENT_KEYED_MODIFIER_RESUMPTION_CARD"
            event_targets_exact &= row["assignment_id"] == assignment_by_event[event_id]["assignment_id"]
            event_targets_exact &= row["resumption_root"] == SPECS[event_id]["root"]
            event_targets_exact &= row["written_slot_count"] == "2"
        else:
            event_targets_exact &= row["full_two_slot_expansion_de"] == source["mixed_scope_voice_working_clause_de"]
            event_targets_exact &= row["resumption_voice_status"] == "UNCHANGED_NON_TARGET"
            event_targets_exact &= row["assignment_id"] == "NONE"
            event_targets_exact &= row["resumption_root"] == "NONE"
            event_targets_exact &= row["written_slot_count"] == "0"
        if row["relation_resumption_voice_working_clause_de"] != source["mixed_scope_voice_working_clause_de"]:
            changed_event_ids.append(event_id)
    check("event_metadata_exact", event_metadata_exact, True)
    check("event_targets_exact", event_targets_exact, True)
    check("event_roundtrip_5122", event_roundtrip_exact, True)
    check("three_changed_events", changed_event_ids, list(TARGET_IDS))
    check("unchanged_event_count", len(events) - len(changed_event_ids), 5119)
    source_zweimal_count = sum(
        row["mixed_scope_voice_working_clause_de"].count("zweimal")
        for row in source_events
    )
    target_zweimal_count = sum(
        row["relation_resumption_voice_working_clause_de"].count("zweimal")
        for row in events
    )
    check(
        "no_new_zweimal_count_recomputed",
        [source_zweimal_count, target_zweimal_count],
        [43, 43],
    )
    check(
        "old_deictic_shortcuts_absent_from_target_edition",
        {
            forbidden: sum(
                row["relation_resumption_voice_working_clause_de"].lower().count(forbidden)
                for row in events
            )
            for forbidden in ("nochmals ebenso", "nochmals dort", "nochmals dorthin")
        },
        {"nochmals ebenso": 0, "nochmals dort": 0, "nochmals dorthin": 0},
    )

    statement_metadata = [
        "edition_statement_ordinal", "statement_id", "physical_page", "register", "owner_id",
        "event_count", "state_card_count", "nonstate_card_count", "statement_mode",
        "event_ids", "surface_sequence", "end_mode",
    ]
    statement_metadata_exact = True
    statement_targets_exact = True
    statement_roundtrip_exact = True
    changed_statement_ids: list[str] = []
    for source, row in zip(source_statements, statements, strict=True):
        statement_id = source["statement_id"]
        ids = source["event_ids"].split("|")
        rebuilt = " ".join(event_by_id[event_id]["relation_resumption_voice_working_clause_de"] for event_id in ids)
        source_rebuilt = " ".join(source_event_by_id[event_id]["mixed_scope_voice_working_clause_de"] for event_id in ids)
        changed_members = [event_id for event_id in ids if event_id in TARGET_IDS]
        statement_metadata_exact &= all(row[column] == source[column] for column in statement_metadata)
        statement_targets_exact &= row["gdt579_mixed_scope_voice_reading_de"] == source["mixed_scope_voice_working_reading_de"] == source_rebuilt
        statement_targets_exact &= row["relation_resumption_voice_working_reading_de"] == rebuilt
        statement_targets_exact &= row["resumption_statement_changed"] == ("YES" if changed_members else "NO")
        statement_targets_exact &= int(row["resumption_changed_event_count"]) == len(changed_members)
        statement_targets_exact &= row["resumption_changed_event_ids"] == (pipe(changed_members) if changed_members else "NONE")
        if changed_members:
            statement_targets_exact &= row["retained_gdt579_scope_event_ids"] == "NONE"
        statement_roundtrip_exact &= row["gdt579_source_roundtrip_de"] == source["mixed_scope_voice_working_reading_de"]
        if rebuilt != source_rebuilt:
            changed_statement_ids.append(statement_id)
    check("statement_metadata_exact", statement_metadata_exact, True)
    check("statements_rebuilt_from_event_ids", statement_targets_exact, True)
    check("statement_roundtrip_793", statement_roundtrip_exact, True)
    check("three_changed_statements", sorted(set(changed_statement_ids)), sorted(TARGET_STATEMENTS))

    events_by_page: dict[str, list[dict[str, str]]] = defaultdict(list)
    statements_by_page: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        events_by_page[row["physical_page"]].append(row)
    for row in statements:
        statements_by_page[row["physical_page"]].append(row)
    page_metadata_exact = set(page_by_id) == set(source_page_by_id)
    changed_pages: set[str] = set()
    for page_id, row in page_by_id.items():
        source = source_page_by_id[page_id]
        for column in ["page_ordinal", "physical_page", "registers", "event_count", "statement_count", "state_event_count", "nonstate_event_count", "page_status"]:
            page_metadata_exact &= row[column] == source[column]
        event_changes = sum(event["event_id"] in TARGET_IDS for event in events_by_page[page_id])
        statement_changes = sum(statement["statement_id"] in TARGET_STATEMENTS for statement in statements_by_page[page_id])
        page_metadata_exact &= int(row["resumption_changed_event_count"]) == event_changes
        page_metadata_exact &= int(row["resumption_changed_statement_count"]) == statement_changes
        page_metadata_exact &= row["page_resumption_changed"] == ("YES" if event_changes else "NO")
        if event_changes:
            changed_pages.add(page_id)
    check("page_profiles_recomputed", page_metadata_exact, True)
    check("three_changed_pages", sorted(changed_pages), sorted(TARGET_PAGES))

    cumulative_event_changes = sum(
        row["relation_resumption_voice_working_clause_de"] != old_event_by_id[row["event_id"]]["action_count_working_clause_de"]
        for row in events
    )
    cumulative_statement_changes = sum(
        row["relation_resumption_voice_working_reading_de"] != old_statement_by_id[row["statement_id"]]["action_count_working_reading_de"]
        for row in statements
    )
    cumulative_page_changes = len({
        row["physical_page"] for row in events
        if row["relation_resumption_voice_working_clause_de"] != old_event_by_id[row["event_id"]]["action_count_working_clause_de"]
    })
    check("cumulative_gdt574_changes", [cumulative_event_changes, cumulative_statement_changes, cumulative_page_changes], [764, 309, 28])

    result_expected = {
        "event_count": 5122,
        "statement_count": 793,
        "page_count": 30,
        "resumption_operator_count": 1,
        "relation_pair_assignment_count": 3,
        "gdt575_eligible_raw_adjacent_relation_pair_count": 3,
        "explicit_modifier_form_count": 3,
        "meaning_class_count": 3,
        "written_slot_count": 6,
        "lexical_base_slot_count": 3,
        "explicit_modifier_resumption_slot_count": 3,
        "event_card_count": 3,
        "changed_event_count_against_gdt579": 3,
        "changed_nonstate_event_count_against_gdt579": 1,
        "changed_state_event_count_against_gdt579": 2,
        "changed_statement_count_against_gdt579": 3,
        "changed_page_count_against_gdt579": 3,
        "gdt579_scope_event_overlap_count": 0,
        "changed_statement_retained_gdt579_scope_event_count": 0,
        "gdt515_previous_t_head_binding_row_count": 2,
        "gdt515_previous_t_head_event_id": "G515-E0378",
        "cumulative_changed_event_count_against_gdt574": 764,
        "cumulative_changed_statement_count_against_gdt574": 309,
        "cumulative_changed_page_count_against_gdt574": 28,
        "exact_event_id_roundtrip_count": 5122,
        "exact_statement_id_roundtrip_count": 793,
        "source_zweimal_occurrence_count": 43,
        "target_zweimal_occurrence_count": 43,
        "source_nochmals_occurrence_count": 1,
        "target_nochmals_occurrence_count": 4,
        "new_nochmals_occurrence_count": 3,
    }
    check("result_counts_recomputed", {key: result.get(key) for key in result_expected}, result_expected)
    check(
        "deprecated_deictic_result_keys_absent",
        sorted(set(result) & {"deictic_form_count", "deictic_resumption_slot_count"}),
        [],
    )
    boolean_keys = [
        "no_new_page", "no_new_event", "no_new_statement", "no_root_change",
        "no_recipe_change", "no_scope_change", "no_global_zweimal_added",
        "no_count_value_claim",
    ]
    check("result_boolean_guards", {key: result.get(key) for key in boolean_keys}, {key: True for key in boolean_keys})

    scanned_outputs = [path for key, path in OUTPUTS.items() if key != "result"]
    sealed_hits = [
        str(path.relative_to(ROOT))
        for path in scanned_outputs
        if SEALED_FOLIO_RE.search(path.read_text(encoding="utf-8"))
    ]
    check("f84_and_f84r_absent", sealed_hits, [])
    guard_rows = assignments + slots + cards + events + statements + pages + operator
    check("guards_present", all(row.get("guard", "").strip() for row in guard_rows), True)
    check("input_hash_keys", sorted(result.get("input_sha256", {})), sorted(HASH_INPUTS))
    check("input_hashes_exact", result.get("input_sha256"), {key: sha256(path) for key, path in HASH_INPUTS.items()})

    failures = [row for row in checks if row["status"] != "PASS"]
    validation = {
        "experiment_id": "GDT580",
        "status": "PASS" if not failures else "FAIL",
        "check_count": len(checks),
        "pass_count": len(checks) - len(failures),
        "fail_count": len(failures),
        "checks": checks,
    }
    (OUT / "gdt580_validation.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
