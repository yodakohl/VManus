#!/usr/bin/env python3
"""Build the V61 R3 technical transaction/clause map.

The only segmentation operation is over canonical fields: TERMINAL commits the
active transaction, while OPEN carries it into the next field.  Physical loci
are observed boundaries, not automatic statement boundaries.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
V60 = ROOT / "experiments" / "yolo" / "sidequest_theory_candidates_v60"
V59 = ROOT / "experiments" / "yolo" / "sidequest_theory_candidates_v59"

SOURCE_DECK = V60 / "V60_SELECTED_173_CARD_DICTIONARY.tsv"
SOURCE_EVENTS = V60 / "V60_SELECTED_381_EVENT_LEDGER.tsv"
SOURCE_FIELDS = V59 / "V59_R1_FINAL_135_FIELD_EDITION.tsv"
SOURCE_RECORDS = V59 / "V59_R1_FINAL_14_RECORD_DIAGRAM_TEXTS.tsv"

OUT_BOUNDARIES = HERE / "V61_R3_PHYSICAL_LOCUS_BOUNDARIES.tsv"
OUT_STATEMENTS = HERE / "V61_R3_98_TRANSACTION_STATEMENTS.tsv"
OUT_ASSIGNMENT = HERE / "V61_R3_135_FIELD_ASSIGNMENT.tsv"

PROSE_RECORDS = ("H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6")
PARAMETER_MNEMONICS = {"MASS?"}
INPUT_MNEMONICS = {"ANSATZ?", "ANTEIL?"}
OPERATION_MNEMONICS = {"ANWENDEN?", "SPÜLEN?", "TEMPERIEREN?", "ABLASSEN?"}
STATE_MNEMONICS = {"BEREIT?", "KLAR?"}
RELATION_MNEMONICS = {"VORIGES?", "ZIEL?"}
EXPLICIT_CARRY_PROMPT = "AKTIVEN_ARBEITSSTAND_VERKNÜPFEN"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError(f"refusing empty output: {path.name}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0]),
            delimiter="\t",
            lineterminator="\n",
            extrasaction="raise",
        )
        writer.writeheader()
        writer.writerows(rows)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def ordered_unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    answer: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            answer.append(value)
    return answer


def slot_list(events: list[dict[str, str]], allowed: set[str]) -> str:
    slots = [
        f"E{event['event_serial']}:{event['ATOMIC_OR_WHOLE_CARD_MNEMONIC']}"
        for event in events
        if event["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] in allowed
    ]
    return " | ".join(slots) if slots else "NONE"


def selected_slots(events: list[dict[str, str]]) -> str:
    slots = [
        f"E{event['event_serial']}:{event['joint_tuple_id']}:{event['ATOMIC_OR_WHOLE_CARD_MNEMONIC']}"
        for event in events
        if event["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] != "UNKNOWN"
    ]
    return " | ".join(slots) if slots else "NONE"


def formal_slots(events: list[dict[str, str]]) -> str:
    slots = [
        f"E{event['event_serial']}:{event['strict_control_prompt']}"
        for event in events
        if event["strict_control_prompt"] != "NONE"
    ]
    return " | ".join(slots) if slots else "NONE"


def final_local_clause(field: dict[str, str]) -> str:
    parts = [part.strip() for part in field["LOCAL_IATROMEDICAL_EXPANSION"].split(";") if part.strip()]
    return parts[-1] if parts else "LOCAL_EXEMPLAR_RESULT"


def classify_inputs(record: str, events: list[dict[str, str]]) -> str:
    mnemonics = {event["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] for event in events}
    prompts = {event["strict_control_prompt"] for event in events}
    owner = "PICTURED_PLANT_OWNER" if record.startswith("H") else "PICTURED_WORKCELL_OWNER"
    inputs = [owner, "LOCAL_EXEMPLAR_ARGUMENTS"]
    if "ANSATZ?" in mnemonics:
        inputs.append("ACTIVE_PREPARATION:ANSATZ?")
    if "ANTEIL?" in mnemonics:
        inputs.append("SELECTED_SHARE:ANTEIL?")
    if "VORIGES?" in mnemonics or EXPLICIT_CARRY_PROMPT in prompts:
        inputs.append("PREVIOUS_ACTIVE_STATE")
    return " | ".join(inputs)


def full_reading(record: str, fields: list[dict[str, str]], committed: bool) -> str:
    owner = "PICTURED_PLANT_OWNER" if record.startswith("H") else "PICTURED_WORKCELL_OWNER"
    pieces = [f"LOAD {owner}"]
    for field in fields:
        pieces.append(
            f"[{field['field_id']}@{field['locus']}:{field['closure_status']}] "
            f"{field['LOCAL_IATROMEDICAL_EXPANSION']}"
        )
    pieces.append("COMMIT TRANSACTION" if committed else "HOLD ACTIVE STATE OPEN AT RECORD END")
    return " -> ".join(pieces)


def main() -> None:
    for source in (SOURCE_DECK, SOURCE_EVENTS, SOURCE_FIELDS, SOURCE_RECORDS):
        require(source.is_file(), f"missing source: {source.name}")

    deck = read_tsv(SOURCE_DECK)
    events = read_tsv(SOURCE_EVENTS)
    fields = read_tsv(SOURCE_FIELDS)
    records = read_tsv(SOURCE_RECORDS)
    require((len(deck), len(events), len(fields), len(records)) == (173, 381, 135, 14), "canonical source counts changed")
    require(tuple(ordered_unique([row["record_unit_id"] for row in fields])) == PROSE_RECORDS, "prose record order changed")

    record_context = {row["unit_id"]: row for row in records if row["unit_id"] in PROSE_RECORDS}
    require(set(record_context) == set(PROSE_RECORDS), "eleven prose record contexts missing")
    event_by_field: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        event_by_field[event["field_id"]].append(event)
    require(set(event_by_field) == {row["field_id"] for row in fields}, "event-to-field coverage changed")
    require(sum(len(event_by_field[row["field_id"]]) for row in fields) == 381, "event coverage must be 381")

    deck_by_id = {row["joint_tuple_id"]: row for row in deck}
    require(len(deck_by_id) == 173, "deck exact IDs not unique")
    for event in events:
        require(event["joint_tuple_id"] in deck_by_id, f"event exact ID absent from deck: E{event['event_serial']}")
        require(
            event["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] == deck_by_id[event["joint_tuple_id"]]["ATOMIC_OR_WHOLE_CARD_MNEMONIC"],
            f"event/deck mnemonic mismatch: E{event['event_serial']}",
        )

    fields_by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for field in fields:
        fields_by_record[field["record_unit_id"]].append(field)

    statement_groups: list[tuple[str, int, list[dict[str, str]]]] = []
    for record in PROSE_RECORDS:
        active: list[dict[str, str]] = []
        ordinal = 0
        for field in fields_by_record[record]:
            active.append(field)
            if field["closure_status"] == "TERMINAL":
                ordinal += 1
                statement_groups.append((record, ordinal, active))
                active = []
        if active:
            ordinal += 1
            statement_groups.append((record, ordinal, active))

    require(len(statement_groups) == 98, "closure/open segmentation must yield 98 statements")

    statement_rows: list[dict[str, str]] = []
    statement_id_by_field: dict[str, str] = {}
    statement_fields_by_id: dict[str, list[dict[str, str]]] = {}
    for serial, (record, ordinal, members) in enumerate(statement_groups, start=1):
        statement_id = f"S{serial:03d}"
        for field in members:
            require(field["field_id"] not in statement_id_by_field, f"field assigned twice: {field['field_id']}")
            statement_id_by_field[field["field_id"]] = statement_id
        statement_fields_by_id[statement_id] = members
        statement_events = [event for field in members for event in event_by_field[field["field_id"]]]
        loci = ordered_unique([field["locus"] for field in members])
        committed = members[-1]["closure_status"] == "TERMINAL"
        prompts = {event["strict_control_prompt"] for event in statement_events}
        mnemonics = {event["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] for event in statement_events}
        prior_link = "VORIGES?" in mnemonics or EXPLICIT_CARRY_PROMPT in prompts
        carry_in_parts = ["RECORD_OWNER_ACTIVE"]
        if ordinal > 1:
            carry_in_parts.append("PREVIOUS_COMMITTED_RESULT_AVAILABLE")
        if prior_link:
            carry_in_parts.append("EXPLICIT_PREVIOUS_ACTIVE_STATE_LINK")
        if committed:
            output = f"COMMITTED_RESULT:{final_local_clause(members[-1])}"
            carry_out = "COMMITTED_RESULT_AVAILABLE_TO_NEXT_STATEMENT"
            status = "COMMITTED"
        else:
            output = f"OPEN_RESULT:{final_local_clause(members[-1])}"
            carry_out = "OPEN_ACTIVE_STATE_DEFERRED_AT_RECORD_END"
            status = "OPEN_DEFERRED_AT_RECORD_END"
        if [field["field_id"] for field in members] == ["F050", "F051"]:
            rival = "SPLIT_AT_F82R_3_TO_4_REPEATED_EXACT_SETUP_AND_INFER_LEFT_IMPLICIT_COMMIT"
            evidence = "F050 is OPEN and F051 is TERMINAL, but the same exact SET(<ARG_AIIN>) card closes the left locus and reopens the right; this supports resumptive carry while also furnishing the strongest line-reset rival."
        elif len(members) > 1:
            rival = "SPLIT_AT_EACH_PHYSICAL_LOCUS_AND_INFER_IMPLICIT_LINE_END_COMMIT"
            evidence = "All prefinal fields are OPEN; the terminal final field commits, or the record ends with the state explicitly unresolved."
        elif committed:
            rival = "MERGE_WITH_ADJACENT_PARALLEL_CELL_AND_TREAT_CLOSE_AS_INTERNAL_CHECKPOINT"
            evidence = "The sole field is TERMINAL and therefore forms one committed transaction under the fixed rule."
        else:
            rival = "INFER_IMPLICIT_COMMIT_AT_RECORD_END"
            evidence = "The sole final field is OPEN; no later field inside the record supplies a commit."
        context = record_context[record]
        statement_rows.append(
            {
                "statement_serial": str(serial),
                "source_statement_id": statement_id,
                "record_unit_id": record,
                "page": members[0]["page"],
                "statement_ordinal_in_record": str(ordinal),
                "transaction_status": status,
                "field_ids": "|".join(field["field_id"] for field in members),
                "field_count": str(len(members)),
                "loci": "|".join(loci),
                "locus_count": str(len(loci)),
                "crosses_physical_locus": "YES" if len(loci) > 1 else "NO",
                "event_count": str(len(statement_events)),
                "event_serials": ",".join(f"E{event['event_serial']}" for event in statement_events),
                "source_surface_sequence_display_only": " || ".join(field["surface_sequence"] for field in members),
                "selected_exact_mnemonic_slots": selected_slots(statement_events),
                "inputs": classify_inputs(record, statement_events),
                "parameter_slots": slot_list(statement_events, PARAMETER_MNEMONICS),
                "operation_slots": slot_list(statement_events, OPERATION_MNEMONICS),
                "state_slots": slot_list(statement_events, STATE_MNEMONICS),
                "relation_slots": slot_list(statement_events, RELATION_MNEMONICS),
                "formal_control_slots": formal_slots(statement_events),
                "output": output,
                "carry_in": " | ".join(carry_in_parts),
                "carry_out": carry_out,
                "full_executable_reading": full_reading(record, members, committed),
                "segmentation_evidence": evidence,
                "strongest_rival_segmentation": rival,
                "record_default_context": context["LOCAL_IATROMEDICAL_EXPANSION"],
                "record_nonmedical_rival_context": context["NONMEDICAL_RIVAL"],
                "binding_contract": "EXACT_JOINT_TUPLE_ID_ONLY;NO_COMPONENT_OR_STRING_INHERITANCE;LOCAL_EXPANSION_IS_NOT_CARD_MEANING",
                "source_lineage": "V60_SELECTED_DECK+EVENT_LEDGER>V59_R1_FIELDS+RECORD_TEXTS>V61_R3_TRANSACTION_MAP",
            }
        )

    require(len(statement_id_by_field) == 135, "all 135 fields must receive one statement")

    assignment_rows: list[dict[str, str]] = []
    for field in fields:
        statement_id = statement_id_by_field[field["field_id"]]
        members = statement_fields_by_id[statement_id]
        index = next(i for i, member in enumerate(members) if member["field_id"] == field["field_id"])
        if len(members) == 1:
            position = "ONLY"
        elif index == 0:
            position = "FIRST"
        elif index == len(members) - 1:
            position = "LAST"
        else:
            position = "MIDDLE"
        field_events = event_by_field[field["field_id"]]
        if index == 0:
            state_before = "NEW_ACTIVE_TRANSACTION"
            reason = "START_AFTER_RECORD_RESET_OR_PREVIOUS_COMMIT"
        else:
            state_before = "ACTIVE_TRANSACTION_CARRIED_FROM_PREVIOUS_OPEN_FIELD"
            reason = "ASSIGN_TO_SAME_STATEMENT_BECAUSE_PREVIOUS_FIELD_IS_OPEN"
        if field["closure_status"] == "TERMINAL":
            state_after = "TRANSACTION_COMMITTED"
        elif int(field["field_ordinal_in_record"]) == len(fields_by_record[field["record_unit_id"]]):
            state_after = "ACTIVE_STATE_OPEN_AT_RECORD_END"
        else:
            state_after = "ACTIVE_STATE_CARRIES_TO_NEXT_FIELD"
        assignment_rows.append(
            {
                "field_serial": field["field_serial"],
                "field_id": field["field_id"],
                "page": field["page"],
                "record_unit_id": field["record_unit_id"],
                "locus": field["locus"],
                "field_ordinal_in_locus": field["field_ordinal_in_locus"],
                "field_ordinal_in_record": field["field_ordinal_in_record"],
                "source_statement_id": statement_id,
                "statement_field_position": position,
                "field_closure_status": field["closure_status"],
                "event_count": field["event_count"],
                "event_serials": ",".join(f"E{event['event_serial']}" for event in field_events),
                "source_surface_sequence_display_only": field["surface_sequence"],
                "selected_exact_mnemonic_slots": selected_slots(field_events),
                "formal_control_slots": formal_slots(field_events),
                "active_state_before_field": state_before,
                "active_state_after_field": state_after,
                "assignment_reason": reason,
                "full_local_field_reading": field["LOCAL_IATROMEDICAL_EXPANSION"],
                "field_nonmedical_rival": field["NONMEDICAL_RIVAL"],
                "binding_contract": "EXACT_JOINT_TUPLE_ID_ONLY;LOCAL_EXPANSION_IS_NOT_CARD_MEANING",
                "source_lineage": field["source_lineage"] + ">V61_R3_FIELD_ASSIGNMENT",
            }
        )

    boundary_rows: list[dict[str, str]] = []
    boundary_serial = 0
    for record in PROSE_RECORDS:
        record_fields = fields_by_record[record]
        loci = ordered_unique([field["locus"] for field in record_fields])
        fields_by_locus = {locus: [field for field in record_fields if field["locus"] == locus] for locus in loci}
        for ordinal, (left_locus, right_locus) in enumerate(zip(loci, loci[1:]), start=1):
            boundary_serial += 1
            left = fields_by_locus[left_locus][-1]
            right = fields_by_locus[right_locus][0]
            left_events = event_by_field[left["field_id"]]
            right_events = event_by_field[right["field_id"]]
            tail = left_events[-1]
            head = right_events[0]
            continues = left["closure_status"] == "OPEN"
            left_statement = statement_id_by_field[left["field_id"]]
            right_statement = statement_id_by_field[right["field_id"]]
            if continues:
                classification = "CONTINUE_OPEN_TRANSACTION"
                before = "ACTIVE_TRANSACTION_OPEN_AT_LEFT_LOCUS_END"
                after = "RESUME_SAME_ACTIVE_TRANSACTION_AT_RIGHT_LOCUS_HEAD"
                if right["closure_status"] == "TERMINAL":
                    pattern = "OPEN_TAIL_CLOSED_BY_NEXT_LOCUS_HEAD"
                else:
                    pattern = "OPEN_TAIL_EXTENDED_BY_NEXT_OPEN_HEAD"
                evidence = "Left final field is OPEN; identical source statement ID continues across the physical locus boundary."
                if tail["joint_tuple_id"] == head["joint_tuple_id"]:
                    rival = "RESUMPTIVE_DUPLICATE_HEADER_SPLIT: infer an implicit left-line commit and read the repeated exact setup as a new transaction."
                else:
                    rival = "PHYSICAL_LINE_RESET_SPLIT: infer an unmarked commit after the OPEN tail and start a new transaction at the right locus."
            else:
                classification = "RESET_AFTER_COMMIT"
                before = "TRANSACTION_COMMITTED_AT_LEFT_LOCUS_END"
                after = "START_NEW_ACTIVE_TRANSACTION_AT_RIGHT_LOCUS_HEAD"
                pattern = "CLOSED_PARALLEL_CELL_SEQUENCE" if len(fields_by_locus[left_locus]) > 1 else "SINGLE_CLOSED_CELL"
                evidence = "Left final field is TERMINAL; the next locus starts a different source statement ID."
                rival = "CROSS_LOCUS_MERGE: treat formal CLOSE as an internal checkpoint and continue one larger statement."
            focus = "GENERAL_BOUNDARY"
            if record == "B2" and left_locus == "f82r.3" and right_locus == "f82r.4":
                focus = "PRIMARY_F82R_3_TO_4"
            elif left["page"] == "f83r":
                focus = "F83R_PRESSURE_SET"
            boundary_rows.append(
                {
                    "boundary_serial": str(boundary_serial),
                    "boundary_id": f"LBOUND{boundary_serial:03d}",
                    "record_unit_id": record,
                    "page": left["page"],
                    "boundary_ordinal_in_record": str(ordinal),
                    "left_locus": left_locus,
                    "right_locus": right_locus,
                    "left_last_field_id": left["field_id"],
                    "right_first_field_id": right["field_id"],
                    "left_field_closure_status": left["closure_status"],
                    "boundary_classification": classification,
                    "same_source_statement": "YES" if continues else "NO",
                    "left_source_statement_id": left_statement,
                    "right_source_statement_id": right_statement,
                    "active_state_before_boundary": before,
                    "boundary_transition": after,
                    "parallel_cell_pattern": pattern,
                    "left_tail_exact_id": tail["joint_tuple_id"],
                    "left_tail_selected_mnemonic": tail["ATOMIC_OR_WHOLE_CARD_MNEMONIC"],
                    "left_tail_formal_control": tail["strict_control_prompt"],
                    "right_head_exact_id": head["joint_tuple_id"],
                    "right_head_selected_mnemonic": head["ATOMIC_OR_WHOLE_CARD_MNEMONIC"],
                    "right_head_formal_control": head["strict_control_prompt"],
                    "repeated_exact_joint_tuple_across_boundary": "YES" if tail["joint_tuple_id"] == head["joint_tuple_id"] else "NO",
                    "decision_evidence": evidence,
                    "strongest_rival_segmentation": rival,
                    "focus_status": focus,
                    "line_statement_contract": "PHYSICAL_LOCUS_BOUNDARY_IS_NOT_AUTOMATIC_STATEMENT_BOUNDARY",
                    "source_lineage": "V60_SELECTED_EVENT_LEDGER>V59_R1_FIELD_CLOSURE>V61_R3_BOUNDARY_CLASSIFICATION",
                }
            )

    require((len(boundary_rows), len(statement_rows), len(assignment_rows)) == (46, 98, 135), "output counts changed")
    require(Counter(row["boundary_classification"] for row in boundary_rows) == Counter({"CONTINUE_OPEN_TRANSACTION": 37, "RESET_AFTER_COMMIT": 9}), "boundary class counts changed")

    write_tsv(OUT_BOUNDARIES, boundary_rows)
    write_tsv(OUT_STATEMENTS, statement_rows)
    write_tsv(OUT_ASSIGNMENT, assignment_rows)
    print("PASS build")
    print("boundaries=46 continuations=37 resets=9 statements=98 fields=135 events=381")


if __name__ == "__main__":
    main()
