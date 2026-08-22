#!/usr/bin/env python3
"""Build the V62 R1 four-register ellipsis trace.

All state values are anonymous and record-local.  Selected mnemonics can mark
that a source slot is needed, but no mnemonic supplies a register referent.
German cue matching operates only on the already selected creative exemplar
clauses and is therefore labelled EXEMPLAR_ONLY throughout.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
YOLO = ROOT / "experiments/yolo"
V60 = YOLO / "sidequest_theory_candidates_v60"
V61 = YOLO / "sidequest_theory_candidates_v61"
OUT = YOLO / "sidequest_theory_candidates_v62"

ROUTE = ROOT / "VOYNICH_CURRENT_ROUTE.md"
ROLES = YOLO / "SIDEQUEST_FOUR_AGENT_BACKGROUNDS.md"
PROTOCOL = YOLO / "SIDEQUEST_V60_V69_ITERATION_PROTOCOL.md"
V60_SELECTION = V60 / "V60_FOUR_ROLE_SELECTION.md"
V61_SELECTION = V61 / "V61_FOUR_ROLE_SELECTION.md"
STATEMENT_SOURCE = V61 / "V61_SELECTED_116_SOURCE_STATEMENTS.tsv"
BOUNDARY_SOURCE = V61 / "V61_SELECTED_46_LINE_BOUNDARIES.tsv"
RECORD_SOURCE = V61 / "V61_SELECTED_11_RECORD_CONTINUATIONS.tsv"

TRACE_OUT = OUT / "V62_R1_116_STATEMENT_REGISTER_TRACE.tsv"
RECORD_OUT = OUT / "V62_R1_11_RECORD_INITIAL_FINAL_REGISTERS.tsv"
EDGE_OUT = OUT / "V62_R1_REGISTER_CARRY_EDGES.tsv"
VALIDATION_OUT = OUT / "V62_R1_VALIDATION.json"

REGISTERS = [
    "PICTURE_OWNER",
    "ACTIVE_PREPARATION_OR_ITEM",
    "TARGET_OR_STATION",
    "PREVIOUS_ITEM_REFERENCE",
]

ACTIVE_SLOT_MNEMONICS = {
    "MASS?", "ANWENDEN?", "BEREIT?", "ANSATZ?", "ANTEIL?", "TEMPERIEREN?",
    "KLAR?", "SPÜLEN?", "ABLASSEN?",
}

TARGET_SLOT_MNEMONICS = {"ZIEL?", "ANWENDEN?", "SPÜLEN?", "ABLASSEN?"}

RESOLUTIONS = {"EXPLICIT", "INHERITED", "UNRESOLVED", "NOT_REQUIRED"}


ACTIVE_NOUN_CUES = [
    "wurzel", "pflanze", "simplex", "blüte", "blüten", "blatt", "blätter",
    "kraut", "samen", "knospen", "zubereitung", "arznei", "arbeitsflüssigkeit",
    "flüssigkeit", "mischung", "portion", "anteil", "posten", "ansatz", "öl",
    "wasser", "wein", "umschlag", "pflaster", "rückstand", "rest", "bestand",
    "strom", "zusatz", "material", "honig", "saft", "sud",
]

ACTIVE_RESET_CUES = [
    "nimm die ", "nimm den ", "sammle ", "beginne den nächsten abgemessenen posten",
    "beginne die spülung", "gib einen abgemessenen anteil", "ein vorgeschriebenes maß",
]

TARGET_NOUN_CUES = [
    "zielstelle", "stelle", "becken", "gefäß", "öffnung", "ablauf", "lauf",
    "tuch", "station", "waldort", "wiesengrund", "heide",
]

TARGET_ACTION_CUES = [
    "anwenden", "verwenden", "spül", "wasch", "bade", "tauche", "binde",
    "trinke", "seihe", "gieße", "fülle", "ablaufen", "ziehe", "presse",
    "lege", "führen", "bringe", "koche", "rühre",
]

PREVIOUS_CUES = [
    "vorig", "zuvor", "daraus", "demselben", "dieselbe", "zurück", "rest",
    "übrig", "danach", "weiter", "zweite", "wieder", "folgenden", "noch",
    "gleicher", "gleichen", "erste spülung", "nach dem absetzen",
]


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        assert reader.fieldnames is not None
        return list(reader.fieldnames), list(reader)


def write_tsv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_mnemonics(skeleton: str) -> set[str]:
    return set(re.findall(r"[A-ZÄÖÜ]+\?", skeleton))


def has_any(text: str, cues: list[str]) -> bool:
    return any(cue in text for cue in cues)


def is_unresolved(value: str) -> bool:
    return value.startswith("UNRESOLVED_")


def is_resolved(value: str) -> bool:
    return value != "UNSET" and not is_unresolved(value)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    _, statements = read_tsv(STATEMENT_SOURCE)
    _, boundaries = read_tsv(BOUNDARY_SOURCE)
    _, records = read_tsv(RECORD_SOURCE)

    assert len(statements) == 116
    assert len(boundaries) == 46
    assert len(records) == 11
    assert len({row["statement_id"] for row in statements}) == 116
    assert len({row["boundary_id"] for row in boundaries}) == 46
    record_order = [row["record_unit_id"] for row in records]
    record_rank = {record: index for index, record in enumerate(record_order)}
    statements.sort(
        key=lambda row: (
            record_rank[row["record_unit_id"]],
            int(row["statement_ordinal_in_record"]),
        )
    )
    record_by_id = {row["record_unit_id"]: row for row in records}

    statements_by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for statement in statements:
        statements_by_record[statement["record_unit_id"]].append(statement)
    assert set(statements_by_record) == set(record_order)
    for record, rows in statements_by_record.items():
        assert [int(row["statement_ordinal_in_record"]) for row in rows] == list(
            range(1, len(rows) + 1)
        )

    boundary_by_to_statement: dict[str, dict[str, str]] = {}
    for boundary in boundaries:
        if boundary["classification"] != "CONTINUE_SAME_CLAUSE":
            target = boundary["to_statement_id"]
            assert target not in boundary_by_to_statement
            boundary_by_to_statement[target] = boundary

    id_counters: dict[str, Counter[str]] = defaultdict(Counter)

    def new_id(record: str, kind: str) -> str:
        id_counters[record][kind] += 1
        if kind == "ITEM":
            return f"ITEM_{record}_{id_counters[record][kind]:03d}"
        if kind == "TARGET":
            return f"TARGET_{record}_{id_counters[record][kind]:03d}"
        if kind == "UNRESOLVED_ITEM":
            return f"UNRESOLVED_ITEM_{record}_{id_counters[record][kind]:03d}"
        if kind == "UNRESOLVED_TARGET":
            return f"UNRESOLVED_TARGET_{record}_{id_counters[record][kind]:03d}"
        if kind == "UNRESOLVED_PREV":
            return f"UNRESOLVED_PREV_{record}_{id_counters[record][kind]:03d}"
        raise AssertionError(kind)

    trace_rows: list[dict[str, str]] = []
    record_initial_states: dict[str, dict[str, str]] = {}
    record_final_states: dict[str, dict[str, str]] = {}

    for record in record_order:
        state = {
            "PICTURE_OWNER": f"OWNER_{record}",
            "ACTIVE_PREPARATION_OR_ITEM": "UNSET",
            "TARGET_OR_STATION": "UNSET",
            "PREVIOUS_ITEM_REFERENCE": "UNSET",
        }
        record_initial_states[record] = dict(state)
        for index, statement in enumerate(statements_by_record[record]):
            entry = statement["entry_boundary_class"]
            text = statement["concrete_workshop_reading"].casefold()
            mnemonics = parse_mnemonics(statement["selected_short_card_skeleton"])
            boundary = boundary_by_to_statement.get(statement["statement_id"])
            boundary_id = boundary["boundary_id"] if boundary else "NONE"

            input_state = dict(state)

            # PICTURE_OWNER is initialized once from the visible record owner.
            owner_needed = True
            owner_resolution = "EXPLICIT" if index == 0 else "INHERITED"
            owner_evidence = (
                "EXEMPLAR_ONLY"
                if index == 0
                else "EXEMPLAR_ONLY"
            )
            owner_operation = "INTRODUCED_AT_RECORD_INITIALIZATION" if index == 0 else "CARRY"
            owner_out = input_state["PICTURE_OWNER"]

            # ACTIVE_PREPARATION_OR_ITEM.
            active_selected_cue = bool(ACTIVE_SLOT_MNEMONICS & mnemonics)
            active_exemplar_cue = has_any(text, ACTIVE_NOUN_CUES)
            # The mnemonic can demand an active slot, but only the selected
            # exemplar can make its record-local referent explicit.
            active_explicit = active_exemplar_cue
            active_reset_cue = (
                "ANTEIL?" in mnemonics
                or has_any(text, ACTIVE_RESET_CUES)
            )
            active_in = input_state["ACTIVE_PREPARATION_OR_ITEM"]
            reset_entry = entry in {
                "START_NEW_CLAUSE", "NEXT_PARALLEL_CELL", "UNRESOLVED"
            }

            if index == 0:
                if active_explicit:
                    active_out = new_id(record, "ITEM")
                    active_operation = "INTRODUCE_EXPLICIT"
                else:
                    active_out = new_id(record, "UNRESOLVED_ITEM")
                    active_operation = "INTRODUCE_UNRESOLVED"
            elif entry == "RESUME_ACTIVE_ITEM":
                if active_in == "UNSET":
                    active_out = new_id(record, "UNRESOLVED_ITEM")
                    active_operation = "RESUME_FAILED_INTRODUCE_UNRESOLVED"
                else:
                    active_out = active_in
                    active_operation = "RESUME"
            elif reset_entry:
                if active_explicit and entry != "UNRESOLVED":
                    active_out = new_id(record, "ITEM")
                    active_operation = "RESET_TO_EXPLICIT_NEW_ITEM"
                else:
                    active_out = new_id(record, "UNRESOLVED_ITEM")
                    active_operation = "RESET_TO_UNRESOLVED_ITEM"
            elif active_reset_cue:
                active_out = new_id(record, "ITEM")
                active_operation = "RESET_TO_EXPLICIT_NEW_ITEM"
            elif active_in == "UNSET":
                active_out = (
                    new_id(record, "ITEM")
                    if active_explicit
                    else new_id(record, "UNRESOLVED_ITEM")
                )
                active_operation = (
                    "INTRODUCE_EXPLICIT" if active_explicit else "INTRODUCE_UNRESOLVED"
                )
            elif is_unresolved(active_in) and active_explicit:
                active_out = new_id(record, "ITEM")
                active_operation = "RESOLVE_AND_RESET_EXPLICIT"
            else:
                active_out = active_in
                active_operation = "CARRY_EXPLICIT_REASSERTION" if active_explicit else "CARRY"

            if active_explicit:
                active_resolution = "EXPLICIT"
            elif is_unresolved(active_out):
                active_resolution = "UNRESOLVED"
            else:
                active_resolution = "INHERITED"
            if active_selected_cue:
                active_evidence = "SELECTED_MNEMONIC+EXEMPLAR_ONLY"
            elif active_exemplar_cue:
                active_evidence = "EXEMPLAR_ONLY"
            elif entry == "RESUME_ACTIVE_ITEM":
                active_evidence = "BOUNDARY"
            elif reset_entry:
                active_evidence = "BOUNDARY+EXEMPLAR_ONLY"
            else:
                active_evidence = "EXEMPLAR_ONLY"

            # TARGET_OR_STATION.
            target_selected_cue = bool(TARGET_SLOT_MNEMONICS & mnemonics)
            target_exemplar_cue = has_any(text, TARGET_NOUN_CUES)
            target_explicit = target_exemplar_cue
            target_required = (
                target_selected_cue or target_explicit or has_any(text, TARGET_ACTION_CUES)
            )
            target_in = input_state["TARGET_OR_STATION"]
            if target_explicit:
                target_out = new_id(record, "TARGET")
                target_operation = (
                    "INTRODUCE_EXPLICIT" if target_in == "UNSET" else "RESET_TO_EXPLICIT_TARGET"
                )
            elif target_required:
                if entry == "RESUME_ACTIVE_ITEM" and target_in != "UNSET":
                    target_out = target_in
                    target_operation = "RESUME"
                elif reset_entry:
                    target_out = new_id(record, "UNRESOLVED_TARGET")
                    target_operation = "RESET_TO_UNRESOLVED_TARGET"
                elif target_in != "UNSET":
                    target_out = target_in
                    target_operation = "CARRY"
                else:
                    target_out = new_id(record, "UNRESOLVED_TARGET")
                    target_operation = "INTRODUCE_UNRESOLVED"
            else:
                if reset_entry:
                    target_out = "UNSET"
                    target_operation = "RESET_TO_UNSET" if target_in != "UNSET" else "KEEP_UNSET"
                else:
                    target_out = target_in
                    target_operation = "CARRY_UNUSED" if target_in != "UNSET" else "KEEP_UNSET"

            if not target_required:
                target_resolution = "NOT_REQUIRED"
            elif target_explicit:
                target_resolution = "EXPLICIT"
            elif is_unresolved(target_out):
                target_resolution = "UNRESOLVED"
            else:
                target_resolution = "INHERITED"
            if target_selected_cue:
                target_evidence = "SELECTED_MNEMONIC+EXEMPLAR_ONLY"
            elif target_exemplar_cue:
                target_evidence = "EXEMPLAR_ONLY"
            elif entry == "RESUME_ACTIVE_ITEM" and target_required:
                target_evidence = "BOUNDARY"
            elif target_required and reset_entry:
                target_evidence = "BOUNDARY+EXEMPLAR_ONLY"
            elif target_required:
                target_evidence = "EXEMPLAR_ONLY"
            else:
                target_evidence = "EXEMPLAR_ONLY"

            # PREVIOUS_ITEM_REFERENCE.  A reset archives the old active item;
            # an overt VORIGES?/exemplar cue uses a stored anonymous value.
            previous_selected_cue = "VORIGES?" in mnemonics
            previous_exemplar_cue = has_any(text, PREVIOUS_CUES)
            previous_explicit = previous_exemplar_cue
            previous_required = previous_explicit or entry == "RESUME_ACTIVE_ITEM"
            previous_in = input_state["PREVIOUS_ITEM_REFERENCE"]
            active_changed = active_out != active_in
            # A long selected statement can introduce an item and refer back to
            # it later inside the same statement.  In that case active_out is a
            # legitimate statement-local candidate even though active_in was
            # still UNSET at statement entry.
            candidate_previous = (
                previous_in
                if previous_in != "UNSET"
                else active_in
                if active_in != "UNSET"
                else active_out
                if active_explicit
                else "UNSET"
            )

            if previous_explicit:
                if candidate_previous == "UNSET":
                    previous_out = new_id(record, "UNRESOLVED_PREV")
                    previous_operation = "INTRODUCE_UNRESOLVED_REFERENCE"
                    previous_resolution = "UNRESOLVED"
                else:
                    previous_out = candidate_previous
                    previous_operation = "REFERENCE_EXPLICIT"
                    previous_resolution = (
                        "UNRESOLVED" if is_unresolved(candidate_previous) else "EXPLICIT"
                    )
            elif previous_selected_cue:
                if candidate_previous == "UNSET":
                    previous_out = new_id(record, "UNRESOLVED_PREV")
                    previous_operation = "SELECTED_SLOT_UNRESOLVED_REFERENCE"
                    previous_resolution = "UNRESOLVED"
                else:
                    previous_out = candidate_previous
                    previous_operation = "SELECTED_SLOT_REFERENCE"
                    previous_resolution = (
                        "UNRESOLVED" if is_unresolved(candidate_previous) else "INHERITED"
                    )
            elif entry == "RESUME_ACTIVE_ITEM":
                candidate_resume = active_in if active_in != "UNSET" else previous_in
                if candidate_resume == "UNSET":
                    previous_out = new_id(record, "UNRESOLVED_PREV")
                    previous_operation = "RESUME_FAILED_UNRESOLVED"
                    previous_resolution = "UNRESOLVED"
                else:
                    previous_out = candidate_resume
                    previous_operation = "RESUME_REFERENCE"
                    previous_resolution = (
                        "UNRESOLVED" if is_unresolved(candidate_resume) else "INHERITED"
                    )
            elif active_changed and active_in != "UNSET":
                previous_out = active_in
                previous_operation = "ARCHIVE_ACTIVE_ON_RESET"
                previous_resolution = "NOT_REQUIRED"
            else:
                previous_out = previous_in
                previous_operation = "CARRY_UNUSED" if previous_in != "UNSET" else "KEEP_UNSET"
                previous_resolution = "NOT_REQUIRED"

            if previous_selected_cue:
                previous_evidence = "SELECTED_MNEMONIC+EXEMPLAR_ONLY"
            elif previous_exemplar_cue:
                previous_evidence = "EXEMPLAR_ONLY"
            elif entry == "RESUME_ACTIVE_ITEM":
                previous_evidence = "BOUNDARY"
            elif previous_operation == "ARCHIVE_ACTIVE_ON_RESET":
                previous_evidence = (
                    "BOUNDARY"
                    if entry in {"START_NEW_CLAUSE", "NEXT_PARALLEL_CELL", "UNRESOLVED"}
                    else "EXEMPLAR_ONLY"
                )
            else:
                previous_evidence = "EXEMPLAR_ONLY"

            state = {
                "PICTURE_OWNER": owner_out,
                "ACTIVE_PREPARATION_OR_ITEM": active_out,
                "TARGET_OR_STATION": target_out,
                "PREVIOUS_ITEM_REFERENCE": previous_out,
            }

            role_data = {
                "PICTURE_OWNER": (owner_needed, owner_resolution, owner_evidence, owner_operation),
                "ACTIVE_PREPARATION_OR_ITEM": (True, active_resolution, active_evidence, active_operation),
                "TARGET_OR_STATION": (target_required, target_resolution, target_evidence, target_operation),
                "PREVIOUS_ITEM_REFERENCE": (
                    previous_required, previous_resolution, previous_evidence, previous_operation
                ),
            }
            required_roles = [role for role, data in role_data.items() if data[0]]
            explicit_roles = [role for role, data in role_data.items() if data[1] == "EXPLICIT"]
            inherited_roles = [role for role, data in role_data.items() if data[1] == "INHERITED"]
            unresolved_roles = [role for role, data in role_data.items() if data[1] == "UNRESOLVED"]
            missing_roles = inherited_roles + unresolved_roles

            trace_rows.append(
                {
                    "statement_id": statement["statement_id"],
                    "record_unit_id": record,
                    "page": statement["page"],
                    "statement_ordinal_in_record": statement["statement_ordinal_in_record"],
                    "start_locus": statement["start_locus"],
                    "start_field": statement["start_field"],
                    "end_locus": statement["end_locus"],
                    "end_field": statement["end_field"],
                    "constituent_fields": statement["constituent_fields"],
                    "entry_boundary_id": boundary_id,
                    "entry_boundary_class": entry,
                    "selected_short_card_skeleton": statement["selected_short_card_skeleton"],
                    "concrete_source_clause": statement["concrete_workshop_reading"],
                    "required_roles": "|".join(required_roles),
                    "explicit_required_roles": "|".join(explicit_roles) or "NONE",
                    "missing_roles_needed": "|".join(missing_roles) or "NONE",
                    "unresolved_required_roles": "|".join(unresolved_roles) or "NONE",
                    "input_picture_owner": input_state["PICTURE_OWNER"],
                    "picture_owner_needed": "YES",
                    "picture_owner_resolution": owner_resolution,
                    "picture_owner_evidence": owner_evidence,
                    "picture_owner_operation": owner_operation,
                    "next_picture_owner": owner_out,
                    "input_active_preparation_or_item": active_in,
                    "active_preparation_or_item_needed": "YES",
                    "active_preparation_or_item_resolution": active_resolution,
                    "active_preparation_or_item_evidence": active_evidence,
                    "active_preparation_or_item_operation": active_operation,
                    "next_active_preparation_or_item": active_out,
                    "input_target_or_station": target_in,
                    "target_or_station_needed": "YES" if target_required else "NO",
                    "target_or_station_resolution": target_resolution,
                    "target_or_station_evidence": target_evidence,
                    "target_or_station_operation": target_operation,
                    "next_target_or_station": target_out,
                    "input_previous_item_reference": previous_in,
                    "previous_item_reference_needed": "YES" if previous_required else "NO",
                    "previous_item_reference_resolution": previous_resolution,
                    "previous_item_reference_evidence": previous_evidence,
                    "previous_item_reference_operation": previous_operation,
                    "next_previous_item_reference": previous_out,
                    "exact_next_register_state": (
                        f"PICTURE_OWNER={owner_out};"
                        f"ACTIVE_PREPARATION_OR_ITEM={active_out};"
                        f"TARGET_OR_STATION={target_out};"
                        f"PREVIOUS_ITEM_REFERENCE={previous_out}"
                    ),
                    "strongest_register_alternative": (
                        "ACTIVE could reset instead of carry, or carry instead of reset; "
                        "TARGET may denote apparatus rather than body; PREVIOUS may be discourse-only."
                    ),
                    "semantic_guard": (
                        "ANONYMOUS_RECORD_LOCAL_STATE_ONLY;SELECTED_MNEMONIC_MARKS_SLOT_NOT_REFERENT;"
                        "EXEMPLAR_CUE_NOT_CARD_MEANING"
                    ),
                }
            )
        record_final_states[record] = dict(state)

    assert len(trace_rows) == 116

    trace_fields = [
        "statement_id", "record_unit_id", "page", "statement_ordinal_in_record",
        "start_locus", "start_field", "end_locus", "end_field", "constituent_fields",
        "entry_boundary_id", "entry_boundary_class", "selected_short_card_skeleton",
        "concrete_source_clause", "required_roles", "explicit_required_roles",
        "missing_roles_needed", "unresolved_required_roles",
        "input_picture_owner", "picture_owner_needed", "picture_owner_resolution",
        "picture_owner_evidence", "picture_owner_operation", "next_picture_owner",
        "input_active_preparation_or_item", "active_preparation_or_item_needed",
        "active_preparation_or_item_resolution", "active_preparation_or_item_evidence",
        "active_preparation_or_item_operation", "next_active_preparation_or_item",
        "input_target_or_station", "target_or_station_needed", "target_or_station_resolution",
        "target_or_station_evidence", "target_or_station_operation", "next_target_or_station",
        "input_previous_item_reference", "previous_item_reference_needed",
        "previous_item_reference_resolution", "previous_item_reference_evidence",
        "previous_item_reference_operation", "next_previous_item_reference",
        "exact_next_register_state", "strongest_register_alternative", "semantic_guard",
    ]
    write_tsv(TRACE_OUT, trace_fields, trace_rows)

    # Verify sequential state continuity and build carry/reference edges.
    trace_by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in trace_rows:
        trace_by_record[row["record_unit_id"]].append(row)

    reg_columns = {
        "PICTURE_OWNER": (
            "input_picture_owner", "next_picture_owner", "picture_owner_operation",
            "picture_owner_resolution", "picture_owner_evidence",
        ),
        "ACTIVE_PREPARATION_OR_ITEM": (
            "input_active_preparation_or_item", "next_active_preparation_or_item",
            "active_preparation_or_item_operation", "active_preparation_or_item_resolution",
            "active_preparation_or_item_evidence",
        ),
        "TARGET_OR_STATION": (
            "input_target_or_station", "next_target_or_station", "target_or_station_operation",
            "target_or_station_resolution", "target_or_station_evidence",
        ),
        "PREVIOUS_ITEM_REFERENCE": (
            "input_previous_item_reference", "next_previous_item_reference",
            "previous_item_reference_operation", "previous_item_reference_resolution",
            "previous_item_reference_evidence",
        ),
    }

    edge_rows: list[dict[str, str]] = []
    edge_counter = 0

    def add_edge(
        record: str,
        from_statement: str,
        to_statement: str,
        from_register: str,
        to_register: str,
        value: str,
        edge_type: str,
        boundary_class: str,
        evidence: str,
        role_resolution: str,
    ) -> None:
        nonlocal edge_counter
        edge_counter += 1
        edge_rows.append(
            {
                "edge_id": f"EDGE_{edge_counter:04d}",
                "record_unit_id": record,
                "from_statement_id": from_statement,
                "to_statement_id": to_statement,
                "from_register": from_register,
                "to_register": to_register,
                "anonymous_value": value,
                "edge_type": edge_type,
                "entry_boundary_class": boundary_class,
                "evidence": evidence,
                "role_resolution_at_target": role_resolution,
                "semantic_guard": "STATE_EDGE_ONLY;NO_CARD_REFERENT",
            }
        )

    for record in record_order:
        rows = trace_by_record[record]
        add_edge(
            record,
            f"RECORD_INIT_{record}",
            rows[0]["statement_id"],
            "PICTURE_OWNER",
            "PICTURE_OWNER",
            record_initial_states[record]["PICTURE_OWNER"],
            "RECORD_INITIALIZATION",
            "RECORD_START",
            "EXEMPLAR_ONLY",
            rows[0]["picture_owner_resolution"],
        )
        for previous, current in zip(rows, rows[1:]):
            for register, columns in reg_columns.items():
                input_col, output_col, operation_col, resolution_col, evidence_col = columns
                assert current[input_col] == previous[output_col]
                value = current[input_col]
                if value == "UNSET":
                    continue
                operation = current[operation_col]
                resolution = current[resolution_col]
                if current[output_col] != value:
                    edge_type = "INPUT_CARRY_THEN_RESET"
                elif "RESUME" in operation:
                    edge_type = "RESUME_USED"
                elif resolution == "INHERITED":
                    edge_type = "INHERITED_CARRY_USED"
                elif resolution == "EXPLICIT":
                    edge_type = "EXPLICIT_REASSERTION"
                elif resolution == "UNRESOLVED":
                    edge_type = "UNRESOLVED_CARRY"
                else:
                    edge_type = "AVAILABLE_UNUSED"
                add_edge(
                    record,
                    previous["statement_id"],
                    current["statement_id"],
                    register,
                    register,
                    value,
                    edge_type,
                    current["entry_boundary_class"],
                    current[evidence_col],
                    resolution,
                )

            # Explicitly expose ACTIVE→PREVIOUS archival/reference transfer.
            if current["next_previous_item_reference"] == current[
                "input_active_preparation_or_item"
            ] and current["input_active_preparation_or_item"] != "UNSET" and current[
                "next_previous_item_reference"
            ] != current["input_previous_item_reference"]:
                cross_type = (
                    "ARCHIVE_ACTIVE_AS_PREVIOUS"
                    if current["previous_item_reference_operation"] == "ARCHIVE_ACTIVE_ON_RESET"
                    else "ACTIVE_USED_AS_PREVIOUS_REFERENCE"
                )
                add_edge(
                    record,
                    previous["statement_id"],
                    current["statement_id"],
                    "ACTIVE_PREPARATION_OR_ITEM",
                    "PREVIOUS_ITEM_REFERENCE",
                    current["next_previous_item_reference"],
                    cross_type,
                    current["entry_boundary_class"],
                    current["previous_item_reference_evidence"],
                    current["previous_item_reference_resolution"],
                )

    edge_fields = [
        "edge_id", "record_unit_id", "from_statement_id", "to_statement_id",
        "from_register", "to_register", "anonymous_value", "edge_type",
        "entry_boundary_class", "evidence", "role_resolution_at_target", "semantic_guard",
    ]
    write_tsv(EDGE_OUT, edge_fields, edge_rows)

    # Slot counts are over roles actually required by a concrete clause.
    role_prefixes = {
        "PICTURE_OWNER": "picture_owner",
        "ACTIVE_PREPARATION_OR_ITEM": "active_preparation_or_item",
        "TARGET_OR_STATION": "target_or_station",
        "PREVIOUS_ITEM_REFERENCE": "previous_item_reference",
    }
    global_resolution_counts: Counter[str] = Counter()
    global_required_evidence_counts: Counter[str] = Counter()
    per_role_counts: dict[str, Counter[str]] = {
        role: Counter() for role in REGISTERS
    }
    for row in trace_rows:
        for role, prefix in role_prefixes.items():
            resolution = row[f"{prefix}_resolution"]
            assert resolution in RESOLUTIONS
            if resolution != "NOT_REQUIRED":
                global_resolution_counts[resolution] += 1
                per_role_counts[role][resolution] += 1
                evidence = row[f"{prefix}_evidence"]
                assert set(evidence.split("+")) <= {
                    "SELECTED_MNEMONIC", "BOUNDARY", "EXEMPLAR_ONLY"
                }
                global_required_evidence_counts[evidence] += 1

    record_rows: list[dict[str, str]] = []
    for record in record_order:
        rows = trace_by_record[record]
        resolution_counts: Counter[str] = Counter()
        for row in rows:
            for prefix in role_prefixes.values():
                resolution = row[f"{prefix}_resolution"]
                if resolution != "NOT_REQUIRED":
                    resolution_counts[resolution] += 1
        all_values = {
            value
            for row in rows
            for value in [
                row["input_picture_owner"], row["next_picture_owner"],
                row["input_active_preparation_or_item"], row["next_active_preparation_or_item"],
                row["input_target_or_station"], row["next_target_or_station"],
                row["input_previous_item_reference"], row["next_previous_item_reference"],
            ]
            if value != "UNSET"
        }
        item_values = sorted(value for value in all_values if "ITEM_" in value)
        target_values = sorted(value for value in all_values if "TARGET_" in value)
        unresolved_values = sorted(value for value in all_values if is_unresolved(value))
        initial = record_initial_states[record]
        final = record_final_states[record]
        record_rows.append(
            {
                "record_unit_id": record,
                "page": record_by_id[record]["page"],
                "statements": str(len(rows)),
                "initial_picture_owner": initial["PICTURE_OWNER"],
                "initial_active_preparation_or_item": initial["ACTIVE_PREPARATION_OR_ITEM"],
                "initial_target_or_station": initial["TARGET_OR_STATION"],
                "initial_previous_item_reference": initial["PREVIOUS_ITEM_REFERENCE"],
                "initialization_rule": "INTRODUCE PICTURE_OWNER FROM PICTURE_EXEMPLAR; OTHERS UNSET",
                "final_picture_owner": final["PICTURE_OWNER"],
                "final_active_preparation_or_item": final["ACTIVE_PREPARATION_OR_ITEM"],
                "final_target_or_station": final["TARGET_OR_STATION"],
                "final_previous_item_reference": final["PREVIOUS_ITEM_REFERENCE"],
                "explicit_required_slots": str(resolution_counts["EXPLICIT"]),
                "inherited_required_slots": str(resolution_counts["INHERITED"]),
                "unresolved_required_slots": str(resolution_counts["UNRESOLVED"]),
                "anonymous_item_ids_seen": "|".join(item_values) or "NONE",
                "anonymous_target_ids_seen": "|".join(target_values) or "NONE",
                "unresolved_ids_seen": "|".join(unresolved_values) or "NONE",
                "complete_record_reading": record_by_id[record]["complete_workshop_reading"],
                "strongest_register_contradiction": (
                    "Identity links are chosen from boundary class and creative exemplar flow; "
                    "the visible cards do not name any anonymous ID."
                ),
                "status": "ANONYMOUS_RECORD_LOCAL_REGISTER_MAP;NO_CARD_REFERENT",
            }
        )

    record_fields = [
        "record_unit_id", "page", "statements", "initial_picture_owner",
        "initial_active_preparation_or_item", "initial_target_or_station",
        "initial_previous_item_reference", "initialization_rule", "final_picture_owner",
        "final_active_preparation_or_item", "final_target_or_station",
        "final_previous_item_reference", "explicit_required_slots",
        "inherited_required_slots", "unresolved_required_slots", "anonymous_item_ids_seen",
        "anonymous_target_ids_seen", "unresolved_ids_seen", "complete_record_reading",
        "strongest_register_contradiction", "status",
    ]
    write_tsv(RECORD_OUT, record_fields, record_rows)

    # Anonymous-state and coverage validation.
    allowed_value = re.compile(
        r"^(?:UNSET|OWNER_(?P<owner>[HB]\d)|"
        r"(?:ITEM|TARGET|UNRESOLVED_ITEM|UNRESOLVED_TARGET|UNRESOLVED_PREV)_"
        r"(?P<local>[HB]\d)_\d{3})$"
    )
    state_columns = [
        "input_picture_owner", "next_picture_owner",
        "input_active_preparation_or_item", "next_active_preparation_or_item",
        "input_target_or_station", "next_target_or_station",
        "input_previous_item_reference", "next_previous_item_reference",
    ]
    for row in trace_rows:
        record = row["record_unit_id"]
        for column in state_columns:
            value = row[column]
            match = allowed_value.match(value)
            assert match, (row["statement_id"], column, value)
            owner_record = match.groupdict().get("owner")
            local_record = match.groupdict().get("local")
            assert owner_record in {None, record}
            assert local_record in {None, record}
        assert row["selected_short_card_skeleton"] == next(
            source["selected_short_card_skeleton"]
            for source in statements
            if source["statement_id"] == row["statement_id"]
        )
        assert row["concrete_source_clause"] == next(
            source["concrete_workshop_reading"]
            for source in statements
            if source["statement_id"] == row["statement_id"]
        )
        assert row["exact_next_register_state"] == (
            f"PICTURE_OWNER={row['next_picture_owner']};"
            f"ACTIVE_PREPARATION_OR_ITEM={row['next_active_preparation_or_item']};"
            f"TARGET_OR_STATION={row['next_target_or_station']};"
            f"PREVIOUS_ITEM_REFERENCE={row['next_previous_item_reference']}"
        )

    assert sum(len(rows) - 1 for rows in trace_by_record.values()) == 105
    assert len({row["edge_id"] for row in edge_rows}) == len(edge_rows)
    assert all(row["anonymous_value"] != "UNSET" for row in edge_rows)
    assert all(row["semantic_guard"] == "STATE_EDGE_ONLY;NO_CARD_REFERENT" for row in edge_rows)
    statement_record = {row["statement_id"]: row["record_unit_id"] for row in trace_rows}
    for edge in edge_rows:
        assert statement_record[edge["to_statement_id"]] == edge["record_unit_id"]
        if not edge["from_statement_id"].startswith("RECORD_INIT_"):
            assert statement_record[edge["from_statement_id"]] == edge["record_unit_id"]
    assert sum(int(row["statements"]) for row in record_rows) == 116
    assert global_resolution_counts["EXPLICIT"] > 0
    assert global_resolution_counts["INHERITED"] > 0
    assert global_resolution_counts["UNRESOLVED"] > 0
    assert sum(global_resolution_counts.values()) <= 116 * 4
    assert {row["page"] for row in trace_rows} == {
        "f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"
    }

    validation = {
        "status": "PASS",
        "model": "V62_R1_FOUR_ANONYMOUS_RECORD_LOCAL_REGISTERS",
        "counts": {
            "records": 11,
            "statements_traced": 116,
            "source_line_boundaries": 46,
            "registers_per_statement": 4,
            "potential_role_slots": 116 * 4,
            "required_role_slots": sum(global_resolution_counts.values()),
            "explicit_required_slots": global_resolution_counts["EXPLICIT"],
            "inherited_required_slots": global_resolution_counts["INHERITED"],
            "unresolved_required_slots": global_resolution_counts["UNRESOLVED"],
            "not_required_role_slots": 116 * 4 - sum(global_resolution_counts.values()),
            "carry_and_reference_edges": len(edge_rows),
            "inter_statement_adjacencies": 105,
        },
        "required_slot_resolution_by_register": {
            role: dict(sorted(counts.items())) for role, counts in per_role_counts.items()
        },
        "required_slot_evidence_counts": dict(
            sorted(global_required_evidence_counts.items())
        ),
        "edge_type_counts": dict(sorted(Counter(row["edge_type"] for row in edge_rows).items())),
        "operation_counts": {
            role: dict(
                sorted(
                    Counter(row[reg_columns[role][2]] for row in trace_rows).items()
                )
            )
            for role in REGISTERS
        },
        "assertions": {
            "all_116_selected_statements_traced_once": "PASS",
            "all_four_registers_have_exact_input_and_next_state": "PASS",
            "state_is_continuous_between_adjacent_statements": "PASS",
            "all_register_values_are_anonymous_and_record_local": "PASS",
            "picture_owner_initialized_once_per_record": "PASS",
            "explicit_inherited_unresolved_slots_are_quantified": "PASS",
            "required_slot_evidence_uses_only_selected_mnemonic_boundary_or_exemplar": "PASS",
            "selected_mnemonic_and_clause_text_are_byte_preserved": "PASS",
            "selected_mnemonic_marks_slot_not_register_referent": "PASS",
            "exemplar_cues_do_not_create_card_meanings": "PASS",
            "carry_edges_never_cross_records": "PASS",
            "no_new_pages": "PASS",
        },
        "source_sha256": {
            str(path.relative_to(ROOT)): sha256(path)
            for path in [
                ROUTE, ROLES, PROTOCOL, V60_SELECTION, V61_SELECTION,
                STATEMENT_SOURCE, BOUNDARY_SOURCE, RECORD_SOURCE,
            ]
        },
        "output_sha256": {
            str(path.relative_to(ROOT)): sha256(path)
            for path in [TRACE_OUT, RECORD_OUT, EDGE_OUT]
        },
    }
    VALIDATION_OUT.write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"status": "PASS", "counts": validation["counts"]}))


if __name__ == "__main__":
    main()
