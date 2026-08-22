#!/usr/bin/env python3
"""Validate the V65 R3 281/115/97/6 waterwork edition."""

from __future__ import annotations

import csv
import hashlib
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
YOLO = ROOT / "experiments" / "yolo"

SOURCES = {
    YOLO / "sidequest_theory_candidates_v54" / "V54_SELECTED_SIX_BIO_RECORDS.tsv": "10fbf2a27d0fa4e7614a5ff5530d9718ecc006915b260e3da7daf63ba9de93a0",
    YOLO / "sidequest_theory_candidates_v60" / "V60_SELECTED_381_EVENT_LEDGER.tsv": "51d69e33c7a02111c79322fb8c1537e34a61fb91c3f885ea48373c20be890f45",
    YOLO / "sidequest_theory_candidates_v61" / "V61_SELECTED_116_SOURCE_STATEMENTS.tsv": "6083ba9ec5bd2122f953bbcbb4d733fc3cee2c24f7fff75543a73e764c813fc3",
    YOLO / "sidequest_theory_candidates_v62" / "V62_SELECTED_116_REGISTER_TRANSITIONS.tsv": "2ee7d0ef2a5abe49388ba0dc2bc650c1677f3747537059ccd486cac335ca7139",
    YOLO / "sidequest_theory_candidates_v63" / "V63_SELECTED_381_EVENT_TEMPLATE_LEDGER.tsv": "f009982934532f1ad02d427feba65017edd93cee1b0819b870c537034278e2c4",
    YOLO / "sidequest_theory_candidates_v63" / "V63_SELECTED_135_FIELD_SLOT_PARSE.tsv": "c6b724d450f999eec873159dc48656e5994f37ffca41d1bcbb4f3f386c8e9680",
    YOLO / "sidequest_theory_candidates_v63" / "V63_SELECTED_116_STATEMENT_SLOT_PARSE.tsv": "09789240ec65a32e36f12d0839335a8f6c5c3a5b8637dfdbe91e88adadd5ab65",
    YOLO / "sidequest_theory_candidates_v64" / "V64_FOUR_ROLE_SELECTION.md": "def880d426029ff058d845bfb5e72fb38d530731fe60c8294df2dcc6af4438b4",
}

OUTS = {
    "events": HERE / "V65_R3_281_EVENT_WATERWORK_LEDGER.tsv",
    "fields": HERE / "V65_R3_115_FIELD_WATERWORK_EDITION.tsv",
    "statements": HERE / "V65_R3_97_STATEMENT_COMPARISON.tsv",
    "records": HERE / "V65_R3_6_RECORD_WATERWORK_EDITION.tsv",
    "graphs": HERE / "V65_R3_6_RECORD_PROCESS_STATE_GRAPHS.tsv",
    "costs": HERE / "V65_R3_12_RECORD_MODEL_ASSUMPTION_COSTS.tsv",
}

FIXED = {
    "MASS?": "MASS?=vorgesehenen Mengenwert buchen",
    "ANWENDEN?": "ANWENDEN?=aktive Charge am gesetzten Arbeitsziel einsetzen",
    "BEREIT?": "BEREIT?=Freigabestand der aktiven Charge prüfen",
    "ANSATZ?": "ANSATZ?=aktiven Arbeitsansatz aufnehmen",
    "ZIEL?": "ZIEL?=Arbeitsziel setzen oder bestätigen",
    "KLAR?": "KLAR?=Klarzustand der aktiven Charge prüfen",
    "VORIGES?": "VORIGES?=vorige Charge wieder aufnehmen",
    "ANTEIL?": "ANTEIL?=bezeichnete Teilcharge wählen",
    "TEMPERIEREN?": "TEMPERIEREN?=aktive Charge gelinde erwärmen",
    "SPÜLEN?": "SPÜLEN?=aktiven Lauf spülen und abschließen",
    "ABLASSEN?": "ABLASSEN?=aktive Charge ablassen und abschließen",
}

WEIGHTS = {
    "EXEMPLAR_FILL": 1,
    "LOCAL_PROCESS": 1,
    "MEDIUM": 1,
    "STATION_OR_TARGET": 1,
    "FILTER_OR_RETURN_MECHANISM": 1,
    "DOMAIN_PURPOSE": 2,
    "HUMAN_ROLE_OR_BODY": 2,
}

EXPECTED_RECORDS = {
    "B1": (24, 21, 66, 23, 132, 129, "IATROMEDICAL"),
    "B2": (26, 22, 62, 16, 135, 132, "IATROMEDICAL"),
    "B3": (38, 34, 86, 29, 188, 184, "IATROMEDICAL"),
    "B4": (20, 16, 47, 15, 106, 103, "IATROMEDICAL"),
    "B5": (5, 3, 11, 4, 22, 23, "TECHNICAL"),
    "B6": (2, 1, 9, 3, 14, 16, "TECHNICAL"),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_named(name: str) -> list[dict[str, str]]:
    return read_tsv(next(path for path in SOURCES if path.name == name))


def decode_cost(text: str) -> tuple[Counter[str], int]:
    counts: Counter[str] = Counter()
    if text != "NONE":
        for item in text.split("|"):
            key, raw_count = item.split(":")
            require(key in WEIGHTS and not counts[key], f"invalid assumption token: {item}")
            counts[key] = int(raw_count)
    return counts, sum(WEIGHTS[key] * value for key, value in counts.items())


def main() -> None:
    for path, expected in SOURCES.items():
        require(sha256(path) == expected, f"selected source drift: {path.name}")

    source_records = source_named("V54_SELECTED_SIX_BIO_RECORDS.tsv")
    source_events_all = source_named("V60_SELECTED_381_EVENT_LEDGER.tsv")
    source_statements_all = source_named("V61_SELECTED_116_SOURCE_STATEMENTS.tsv")
    source_machine_all = source_named("V62_SELECTED_116_REGISTER_TRANSITIONS.tsv")
    parse_events_all = source_named("V63_SELECTED_381_EVENT_TEMPLATE_LEDGER.tsv")
    parse_fields_all = source_named("V63_SELECTED_135_FIELD_SLOT_PARSE.tsv")
    parse_statements_all = source_named("V63_SELECTED_116_STATEMENT_SLOT_PARSE.tsv")
    require(Counter(row["parse_status"] for row in parse_fields_all) == Counter({"UNIQUE": 14, "AMBIGUOUS": 56, "UNPARSED": 65}), "V63 overall field status drift")

    source_events = [row for row in source_events_all if row["record_unit_id"].startswith("B")]
    source_statements = [row for row in source_statements_all if row["record_unit_id"].startswith("B")]
    source_machine = [row for row in source_machine_all if row["record_unit_id"].startswith("B")]
    parse_events = [row for row in parse_events_all if row["record_unit_id"].startswith("B")]
    parse_fields = [row for row in parse_fields_all if row["record_unit_id"].startswith("B")]
    parse_statements = [row for row in parse_statements_all if row["record_unit_id"].startswith("B")]

    events = read_tsv(OUTS["events"])
    fields = read_tsv(OUTS["fields"])
    statements = read_tsv(OUTS["statements"])
    records = read_tsv(OUTS["records"])
    graphs = read_tsv(OUTS["graphs"])
    costs = read_tsv(OUTS["costs"])
    require((len(events), len(fields), len(statements), len(records), len(graphs), len(costs)) == (281, 115, 97, 6, 6, 12), "output count failure")
    require((len(source_events), len(source_statements), len(source_machine), len(parse_events), len(parse_fields), len(parse_statements)) == (281, 97, 97, 281, 115, 97), "source Bio scope failure")
    require({row["page"] for row in events} == {"f81v", "f82r", "f83r"}, "page scope drift")
    require({row["record_unit_id"] for row in events} == set(EXPECTED_RECORDS), "record scope drift")

    source_by_serial = {row["event_serial"]: row for row in source_events}
    parse_by_serial = {row["event_serial"]: row for row in parse_events}
    require(list(row["event_serial"] for row in events) == list(source_by_serial), "event order/identity drift")
    require(Counter(row["event_template"] for row in events) == Counter({"EXEMPLAR_ONLY": 191, "PARAMETER_ASSIGN": 19, "LINK_ACTIVE": 18, "TARGET_ASSIGN": 14, "TERMINAL_FLUSH": 8, "TERMINAL_DRAIN": 8, "ACTION_APPLY": 7, "ACTION_TEMPER": 7, "STATE_GATE": 7, "SELECT_PREVIOUS": 1, "SELECT_PART": 1}), "event-template count drift")
    require(Counter(row["fixed_exact_mnemonic"] for row in events) == Counter({"UNKNOWN": 220, "MASS?": 11, "ZIEL?": 9, "SPÜLEN?": 8, "ABLASSEN?": 8, "ANWENDEN?": 7, "TEMPERIEREN?": 7, "BEREIT?": 4, "KLAR?": 3, "ANSATZ?": 2, "VORIGES?": 1, "ANTEIL?": 1}), "exact-value count drift")
    require(Counter(row["strict_formal_prompt"] for row in events) == Counter({"NONE": 247, "AKTIVEN_ARBEITSSTAND_VERKNÜPFEN": 16, "STANDARDSLOT_SETZEN": 8, "LOKALEN_RELATIONSSLOT_SETZEN": 5, "VORGABEPARAMETER?": 5}), "formal-prompt count drift")
    for row in events:
        source = source_by_serial[row["event_serial"]]
        parsed = parse_by_serial[row["event_serial"]]
        for source_col, output_col in (
            ("page", "page"),
            ("locus", "locus"),
            ("record_unit_id", "record_unit_id"),
            ("field_id", "field_id"),
            ("joint_tuple_id", "joint_tuple_id_opaque"),
            ("surface", "surface_display_only"),
            ("formal_formula_opaque", "formal_formula_opaque"),
            ("terminal_status", "terminal_status"),
        ):
            require(source[source_col] == row[output_col], f"source projection drift E{row['event_serial']}:{output_col}")
        for parse_col, output_col in (
            ("selected_exact_mnemonic", "fixed_exact_mnemonic"),
            ("strict_formal_prompt", "strict_formal_prompt"),
            ("event_template", "event_template"),
            ("event_parse_status", "event_parse_status"),
            ("opaque_roundtrip_atom", "opaque_roundtrip_atom"),
        ):
            require(parsed[parse_col] == row[output_col], f"V63 event layer drift E{row['event_serial']}:{output_col}")
        require(row["fixed_value_clause"] == FIXED.get(row["fixed_exact_mnemonic"], "NONE"), f"fixed exact value drift E{row['event_serial']}")
        require(row["complete_layered_technical_reading"] and row["local_apparatus_argument"], f"event reading incomplete E{row['event_serial']}")
        require(row["layer_contract"] == "EXACT_TUPLE_ATOMIC;V60_VALUE_FIXED;V63_STATUS_FIXED;LOCAL_NOUN_NEVER_CARD_GLOSS", f"atomic contract drift E{row['event_serial']}")
        if row["event_template"] == "EXEMPLAR_ONLY":
            require(row["fixed_exact_mnemonic"] == "UNKNOWN" and "NOT_CARD_MEANING" in row["local_argument_source_class"], f"exemplar promoted E{row['event_serial']}")
        if row["strict_formal_prompt"] != "NONE" and row["fixed_exact_mnemonic"] == "UNKNOWN":
            require(row["local_argument_source_class"].startswith("V63_FORMAL_NO_SEMANTIC_WORD"), f"formal inheritance E{row['event_serial']}")
        if row["event_template"] in {"TERMINAL_FLUSH", "TERMINAL_DRAIN"}:
            require(row["terminal_status"] == "TERMINAL" and row["fixed_exact_mnemonic"] in {"SPÜLEN?", "ABLASSEN?"}, f"terminal action mismatch E{row['event_serial']}")

    parse_field_by_id = {row["field_id"]: row for row in parse_fields}
    events_by_field: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        events_by_field[row["field_id"]].append(row)
    require(Counter(row["v63_parse_status_fixed"] for row in fields) == Counter({"UNIQUE": 14, "AMBIGUOUS": 41, "UNPARSED": 60}), "Bio field status drift")
    require(Counter(row["commit_class"] for row in fields) == Counter({"EXACT_TERMINAL_ACTION_COMMIT": 16, "OPAQUE_FIELD_COMMIT_ONLY": 69, "OPEN_CARRY": 30}), "commit classification drift")
    require(Counter(row["local_phase"] for row in fields) == Counter({"DRAIN": 16, "FLUSH": 12, "RETURN": 12, "CHARGE": 11, "FILTER": 9, "MAINTENANCE": 9, "ROUTE": 8, "SETTLE": 8, "HEAT": 7, "HANDOFF": 7, "SETUP": 6, "SERVICE": 6, "CIRCULATE": 4}), "phase inventory drift")
    require(Counter(row["field_coherence_winner"] for row in fields) == Counter({"TIE": 75, "IATROMEDICAL": 26, "TECHNICAL": 14}), "field comparison drift")
    require({row["field_id"] for row in fields} == set(parse_field_by_id) == set(events_by_field), "field identity/partition drift")
    for row in fields:
        parsed = parse_field_by_id[row["field_id"]]
        unit_events = events_by_field[row["field_id"]]
        require(row["event_serials"].split("|") == [event["event_serial"] for event in unit_events], f"field event order drift {row['field_id']}")
        for source_col, output_col in (
            ("statement_id", "statement_id"),
            ("parse_status", "v63_parse_status_fixed"),
            ("primary_template", "v63_primary_template"),
            ("ordered_event_template_sequence", "v63_ordered_template_sequence"),
            ("register_pre_state_statement_envelope", "v62_pre_state_statement_envelope"),
            ("register_post_state_statement_envelope", "v62_post_state_statement_envelope"),
            ("opaque_roundtrip_trace", "opaque_roundtrip_trace"),
            ("roundtrip_status", "roundtrip_status"),
        ):
            require(parsed[source_col] == row[output_col], f"field selected layer drift {row['field_id']}:{output_col}")
        terminal = any(source_by_serial[event["event_serial"]]["terminal_status"] == "TERMINAL" for event in unit_events)
        exact_terminal = any(event["event_template"] in {"TERMINAL_FLUSH", "TERMINAL_DRAIN"} for event in unit_events)
        expected_commit = "EXACT_TERMINAL_ACTION_COMMIT" if exact_terminal else "OPAQUE_FIELD_COMMIT_ONLY" if terminal else "OPEN_CARRY"
        require(row["commit_class"] == expected_commit, f"CLOSE/action independence drift {row['field_id']}")
        _, technical_cost = decode_cost(row["technical_assumptions"])
        _, medical_cost = decode_cost(row["iatromedical_assumptions"])
        require(technical_cost == int(row["technical_weighted_cost"]) and medical_cost == int(row["iatromedical_weighted_cost"]), f"field cost drift {row['field_id']}")
        expected_winner = "TECHNICAL" if technical_cost < medical_cost else "IATROMEDICAL" if medical_cost < technical_cost else "TIE"
        require(row["field_coherence_winner"] == expected_winner, f"field winner drift {row['field_id']}")

    source_statement_by_id = {row["statement_id"]: row for row in source_statements}
    machine_by_id = {row["statement_id"]: row for row in source_machine}
    parse_statement_by_id = {row["statement_id"]: row for row in parse_statements}
    require(list(row["statement_id"] for row in statements) == list(source_statement_by_id), "statement identity/order drift")
    require(Counter(row["v63_parse_status_fixed"] for row in statements) == Counter({"UNIQUE": 12, "AMBIGUOUS": 35, "UNPARSED": 50}), "statement status drift")
    require(Counter(row["statement_coherence_winner"] for row in statements) == Counter({"TIE": 59, "IATROMEDICAL": 25, "TECHNICAL": 13}), "statement comparison drift")
    for row in statements:
        source = source_statement_by_id[row["statement_id"]]
        machine = machine_by_id[row["statement_id"]]
        parsed = parse_statement_by_id[row["statement_id"]]
        require(row["event_serials"] == source["event_serials"] and row["constituent_fields"] == source["constituent_fields"], f"statement scope drift {row['statement_id']}")
        require(row["complete_iatromedical_comparator"] == source["concrete_workshop_reading"], f"medical comparator changed {row['statement_id']}")
        require(row["v63_parse_status_fixed"] == parsed["parse_status"] and row["v63_ordered_template_sequence"] == parsed["ordered_event_template_sequence"], f"statement parse drift {row['statement_id']}")
        for column in ("pre_state", "owner_operation", "active_item_preparation_operation", "target_station_operation", "previous_item_operation", "post_state"):
            require(row[column] == machine[column], f"V62 statement drift {row['statement_id']}:{column}")
        require(row["opaque_roundtrip_trace"] == parsed["opaque_roundtrip_trace"] and row["roundtrip_status"] == parsed["roundtrip_status"], f"statement roundtrip drift {row['statement_id']}")
        _, technical_cost = decode_cost(row["technical_assumptions"])
        _, medical_cost = decode_cost(row["iatromedical_assumptions"])
        require((technical_cost, medical_cost) == (int(row["technical_weighted_cost"]), int(row["iatromedical_weighted_cost"])), f"statement cost drift {row['statement_id']}")
        expected_winner = "TECHNICAL" if technical_cost < medical_cost else "IATROMEDICAL" if medical_cost < technical_cost else "TIE"
        require(row["statement_coherence_winner"] == expected_winner, f"statement winner drift {row['statement_id']}")

    source_record_by_id = {row["record_id"]: row for row in source_records}
    record_by_id = {row["record_unit_id"]: row for row in records}
    graph_by_id = {row["record_unit_id"]: row for row in graphs}
    require(set(record_by_id) == set(graph_by_id) == set(source_record_by_id) == set(EXPECTED_RECORDS), "record/graph identity drift")
    for record, expected in EXPECTED_RECORDS.items():
        row = record_by_id[record]
        observed = tuple(int(row[column]) for column in ("field_count", "statement_count", "event_count", "recognized_event_count", "technical_weighted_assumption_cost", "iatromedical_weighted_assumption_cost")) + (row["record_coherence_winner_by_fixed_cost"],)
        require(observed == expected, f"record result drift {record}")
        require(row["complete_iatromedical_article"] == source_record_by_id[record]["complete_working_translation_German"], f"record medical comparator changed {record}")
        record_fields = [field for field in fields if field["record_unit_id"] == record]
        require(graph_by_id[record]["field_path"].split("|") == [field["field_id"] for field in record_fields], f"graph field path drift {record}")
        require(graph_by_id[record]["phase_path"] == " > ".join(f"{field['field_id']}:{field['local_phase']}" for field in record_fields), f"graph phase path drift {record}")
        commits = [field["field_id"] for field in record_fields if field["commit_class"] != "OPEN_CARRY"]
        require(graph_by_id[record]["commit_fields"] == ("|".join(commits) if commits else "NONE"), f"graph commit drift {record}")

    require(sum(int(row["technical_weighted_assumption_cost"]) for row in records) == 597, "technical total cost drift")
    require(sum(int(row["iatromedical_weighted_assumption_cost"]) for row in records) == 587, "medical total cost drift")
    require(Counter(row["model"] for row in costs) == Counter({"TECHNICAL_WATERWORK": 6, "IATROMEDICAL": 6}), "cost-row model drift")
    for row in costs:
        _, observed_cost = decode_cost(row["assumption_counts"])
        require(observed_cost == int(row["weighted_cost"]), f"record cost recomputation drift {row['record_unit_id']}/{row['model']}")
    require(not any("PAGE_HOST" in value for rows in (events, fields, statements, records, graphs, costs) for row in rows for value in row.values()), "PAGE_HOST leakage")
    print("PASS V65_R3 waterwork edition")
    print("coverage=6_records/97_statements/115_fields/281_events")
    print("Bio_status=14_unique/41_ambiguous/60_unparsed_fields;12_unique/35_ambiguous/50_unparsed_statements")
    print("events=90_licensed/191_exemplar_only;commits=16_exact_terminal/69_opaque/30_open")
    print("comparison=13_technical/25_iatromedical/59_tie_statements")
    print("weighted_cost=597_technical/587_iatromedical")
    print("roundtrip_and_selected_layers=PASS")


if __name__ == "__main__":
    main()
