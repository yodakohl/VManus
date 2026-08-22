#!/usr/bin/env python3
"""Validate completeness and layer separation of the V65 R1 edition."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from V65_R1_BUILDER import (
    ALLOWED_PAGES,
    ALLOWED_RECORDS,
    OUT,
    P60,
    P61,
    P63,
    read_bio_guarded,
    read_tsv,
)


def load(name: str) -> list[dict[str, str]]:
    return read_tsv(OUT / name)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    events = load("V65_R1_281_EVENT_INTERLINEAR.tsv")
    fields = load("V65_R1_115_FIELD_EDITION.tsv")
    statements = load("V65_R1_97_STATEMENT_EDITION.tsv")
    records = load("V65_R1_6_RECORD_EDITION.tsv")
    graph = load("V65_R1_PROCESS_GRAPH_EDGES.tsv")
    deck_freeze = load("V65_R1_V60_DECK_FREEZE.tsv")
    dictionary_delta = load("V65_R1_DICTIONARY_DELTA.tsv")

    source_events = read_bio_guarded(P60 / "V60_SELECTED_381_EVENT_LEDGER.tsv")
    source_fields = read_bio_guarded(P63 / "V63_SELECTED_135_FIELD_SLOT_PARSE.tsv")
    source_statements = read_bio_guarded(P61 / "V61_SELECTED_116_SOURCE_STATEMENTS.tsv")
    source_statement_parse = read_bio_guarded(P63 / "V63_SELECTED_116_STATEMENT_SLOT_PARSE.tsv")
    source_deck = read_tsv(P60 / "V60_SELECTED_EXACT_CARD_DECISIONS.tsv")

    require(len(events) == 281, "event count must be 281")
    require(len(fields) == 115, "field count must be 115")
    require(len(statements) == 97, "Bio statement count must be 97")
    require(len(records) == 6, "record count must be 6")
    require(len(graph) == 103, "graph must contain 97 statement executions plus 6 record-end edges")
    require(len(deck_freeze) == 11, "deck freeze must contain all eleven V60 cards")
    require(len(dictionary_delta) == 0, "dictionary delta must be empty")

    require({row["page"] for row in events} == set(ALLOWED_PAGES), "event page scope mismatch")
    require({row["page"] for row in fields} == set(ALLOWED_PAGES), "field page scope mismatch")
    require({row["page"] for row in statements} == set(ALLOWED_PAGES), "statement page scope mismatch")
    require({row["page"] for row in records} == set(ALLOWED_PAGES), "record page scope mismatch")
    for table_name, rows in (("events", events), ("fields", fields), ("statements", statements), ("records", records)):
        require(all(not row["page"].startswith("f84") for row in rows), f"forbidden page in {table_name}")
        require(all("page_host" not in key.lower() for key in rows[0]), f"PAGE_HOST column in {table_name}")

    require([int(row["event_serial"]) for row in events] == list(range(101, 382)), "event serial coverage is not 101--381")
    require([row["field_id"] for row in fields] == [f"F{i:03d}" for i in range(21, 136)], "field coverage is not F021--F135")
    require(len({row["statement_id"] for row in statements}) == 97, "duplicate statement ID")
    require([row["record_unit_id"] for row in records] == list(ALLOWED_RECORDS), "record order/scope mismatch")

    src_event = {row["event_serial"]: row for row in source_events}
    require(set(src_event) == {row["event_serial"] for row in events}, "event identities differ from V60 source")
    for row in events:
        src = src_event[row["event_serial"]]
        require(row["joint_tuple_id"] == src["joint_tuple_id"], f"joint tuple changed at {row['event_serial']}")
        require(row["formal_value"] == src["FORMAL_VALUE"], f"formal value changed at {row['event_serial']}")
        require(
            row["v60_exact_mnemonic"] == src["ATOMIC_OR_WHOLE_CARD_MNEMONIC"],
            f"V60 mnemonic changed at {row['event_serial']}",
        )
        require(row["medical_exemplar_expansion"].startswith("[EXEMPLAR_MED; KEIN_KARTENWERT]"), f"unmarked medical event {row['event_serial']}")
        require(row["apparative_exemplar_expansion"].startswith("[EXEMPLAR_APPARAT; KEIN_KARTENWERT]"), f"unmarked apparatus event {row['event_serial']}")
        require(row["semantic_accounting"] in {"EXEMPLAR_ONLY_COMPLETE", "LICENSED_ANCHOR_PLUS_EXEMPLAR_FILL"}, f"empty event accounting {row['event_serial']}")
        require("NO_DICTIONARY_FEEDBACK" in row["layer_contract"], f"missing no-feedback contract {row['event_serial']}")

    canonical_deck = {
        row["joint_tuple_id"]: (row["card"], row["selected_short_mnemonic"], row["source_class"], row["binding"])
        for row in source_deck
    }
    frozen_deck = {
        row["joint_tuple_id"]: (
            row["card"],
            row["v65_selected_short_mnemonic"],
            row["source_class"],
            row["binding"],
        )
        for row in deck_freeze
    }
    require(frozen_deck == canonical_deck, "V60 deck freeze differs from canonical selected deck")
    require(all(row["v60_selected_short_mnemonic"] == row["v65_selected_short_mnemonic"] for row in deck_freeze), "deck value changed")
    require(all(row["v65_action"] == "UNCHANGED" for row in deck_freeze), "deck action not UNCHANGED")

    exact_event_counts = Counter(row["v60_exact_mnemonic"] for row in events if row["v60_exact_mnemonic"] != "UNKNOWN")
    require(sum(exact_event_counts.values()) == 61, "Bio exact-card occurrence count must be 61")
    require(
        exact_event_counts
        == Counter(
            {
                "MASS?": 11,
                "ANWENDEN?": 7,
                "BEREIT?": 4,
                "ANSATZ?": 2,
                "ZIEL?": 9,
                "KLAR?": 3,
                "VORIGES?": 1,
                "ANTEIL?": 1,
                "TEMPERIEREN?": 7,
                "SPÜLEN?": 8,
                "ABLASSEN?": 8,
            }
        ),
        "Bio exact-card distribution mismatch",
    )

    src_field = {row["field_id"]: row for row in source_fields}
    for row in fields:
        src = src_field[row["field_id"]]
        require(row["event_serials"] == src["event_serials"], f"field events changed in {row['field_id']}")
        require(row["statement_id"] == src["statement_id"], f"field statement changed in {row['field_id']}")
        require(row["v63_parse_status"] == src["parse_status"], f"field parse status changed in {row['field_id']}")
        require(row["medical_field_default"].startswith("[EXEMPLAR_MED; KEIN_KARTENWERT]"), f"unmarked field medical fill {row['field_id']}")
        require(row["apparative_field_default"].startswith("[EXEMPLAR_APPARAT; KEIN_KARTENWERT]"), f"unmarked field apparatus fill {row['field_id']}")
        require("NO_CARD_FEEDBACK" in row["exemplar_contract"], f"field feedback contract missing {row['field_id']}")

    src_statement = {row["statement_id"]: row for row in source_statements}
    src_statement_status = {row["statement_id"]: row["parse_status"] for row in source_statement_parse}
    for row in statements:
        src = src_statement[row["statement_id"]]
        require(row["constituent_fields"] == src["constituent_fields"], f"statement fields changed in {row['statement_id']}")
        require(row["event_serials"] == src["event_serials"], f"statement events changed in {row['statement_id']}")
        require(row["entry_boundary_class"] == src["entry_boundary_class"], f"entry boundary changed in {row['statement_id']}")
        require(row["exit_boundary_class"] == src["exit_boundary_class"], f"exit boundary changed in {row['statement_id']}")
        require(row["v63_parse_status"] == src_statement_status[row["statement_id"]], f"statement parse status changed in {row['statement_id']}")
        require(row["medical_default_clause"].startswith("[EXEMPLAR_MED; KEIN_KARTENWERT]"), f"unmarked statement medical fill {row['statement_id']}")
        require(row["apparative_default_clause"].startswith("[EXEMPLAR_APPARAT; KEIN_KARTENWERT]"), f"unmarked statement apparatus fill {row['statement_id']}")
        require(row["register_pre_state"] and row["register_post_state"], f"missing register state {row['statement_id']}")

    require(
        "f82r.3→f82r.4=CONTINUE_SAME_CLAUSE" in next(row for row in statements if row["statement_id"] == "B2-S005")["reflow_highlight"],
        "f82r.3→4 carry not highlighted",
    )
    require(
        next(row for row in statements if row["statement_id"] == "B2-S011")["entry_boundary_class"] == "UNRESOLVED",
        "selected unresolved f82r boundary lost",
    )
    require(next(row for row in statements if row["statement_id"] == "B5-S003")["constituent_fields"] == "F131|F132|F133", "B5 three-field carry lost")
    require(next(row for row in statements if row["statement_id"] == "B6-S001")["constituent_fields"] == "F134|F135", "B6 two-field carry lost")

    by_record_statements: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_record_events = Counter(row["record_unit_id"] for row in events)
    by_record_fields = Counter(row["record_unit_id"] for row in fields)
    for row in statements:
        by_record_statements[row["record_unit_id"]].append(row)
    record_map = {row["record_unit_id"]: row for row in records}
    for record in ALLOWED_RECORDS:
        row = record_map[record]
        local_statements = by_record_statements[record]
        require(int(row["event_count"]) == by_record_events[record], f"record event count mismatch {record}")
        require(int(row["field_count"]) == by_record_fields[record], f"record field count mismatch {record}")
        require(int(row["statement_count"]) == len(local_statements), f"record statement count mismatch {record}")
        require(row["complete_medical_default_text"].startswith("[B"), f"missing full medical text {record}")
        require(row["complete_apparative_rival_text"].startswith("[B"), f"missing full apparatus text {record}")
        for statement in local_statements:
            tag = f"[{statement['statement_id']}]"
            require(tag in row["complete_medical_default_text"], f"medical record text omits {tag}")
            require(tag in row["complete_apparative_rival_text"], f"apparatus record text omits {tag}")
        require(row["revision_against_v54"] and row["strongest_contradiction"], f"record audit incomplete {record}")
        require("DICTIONARY_DELTA_ZERO" in row["edition_status"], f"record dictionary status missing {record}")

    graph_targets = Counter(row["to_node"] for row in graph if row["to_node"] != "END")
    require(graph_targets == Counter({row["statement_id"]: 1 for row in statements}), "graph does not execute each statement exactly once")
    for record in ALLOWED_RECORDS:
        local = sorted((row for row in graph if row["record_unit_id"] == record), key=lambda r: int(r["edge_ordinal"]))
        require(local[0]["from_node"] == "START", f"graph lacks START for {record}")
        require(local[-1]["to_node"] == "END", f"graph lacks END for {record}")
        require(local[-1]["post_state"] == "RESET_BEFORE_NEXT_RECORD", f"graph does not reset {record}")
    unresolved = [row for row in graph if row["boundary_class"] == "UNRESOLVED"]
    require(len(unresolved) == 1 and unresolved[0]["to_node"] == "B2-S011", "unresolved graph branch mismatch")

    event_status = Counter(row["v63_event_parse_status"] for row in events)
    field_status = Counter(row["v63_parse_status"] for row in fields)
    statement_status = Counter(row["v63_parse_status"] for row in statements)
    require(event_status == Counter({"UNIQUE_EXACT": 56, "UNIQUE_FORMAL_ONLY": 29, "UNIQUE_CONVERGENT_CHANNELS": 5, "UNPARSED_EXEMPLAR": 191}), "event status counts mismatch")
    require(field_status == Counter({"UNIQUE": 14, "AMBIGUOUS": 41, "UNPARSED": 60}), "field status counts mismatch")
    require(statement_status == Counter({"UNIQUE": 12, "AMBIGUOUS": 35, "UNPARSED": 50}), "statement status counts mismatch")

    deck_hash = hashlib.sha256(
        "\n".join(f"{row['joint_tuple_id']}\t{row['selected_short_mnemonic']}" for row in source_deck).encode("utf-8")
    ).hexdigest()
    validation = {
        "status": "PASS",
        "pages": list(ALLOWED_PAGES),
        "records": len(records),
        "fields": len(fields),
        "events": len(events),
        "statements": len(statements),
        "process_graph_edges": len(graph),
        "exact_card_occurrences_in_bio": sum(exact_event_counts.values()),
        "exact_card_occurrence_counts": dict(exact_event_counts),
        "event_parse_counts": dict(event_status),
        "field_parse_counts": dict(field_status),
        "statement_parse_counts": dict(statement_status),
        "dictionary_delta_rows": len(dictionary_delta),
        "v60_deck_rows_unchanged": len(deck_freeze),
        "v60_deck_sha256": deck_hash,
        "reflow_checks": {
            "f82r.3_to_f82r.4": "PASS_CONTINUE_SAME_CLAUSE",
            "B5_three_field_statement": "PASS",
            "B6_two_field_statement": "PASS",
            "unresolved_edges_retained": len(unresolved),
        },
        "layer_checks": {
            "event_exemplars_marked": len(events),
            "field_exemplars_marked": len(fields),
            "statement_exemplars_marked": len(statements),
            "PAGE_HOST_columns": 0,
            "dictionary_feedback_rows": 0,
        },
    }
    (OUT / "V65_R1_VALIDATION.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(validation, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
