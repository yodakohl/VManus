#!/usr/bin/env python3
"""Validate the frozen V63 R3 bounded-slot-parser release."""

from __future__ import annotations

import csv
import hashlib
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
V60 = ROOT / "experiments" / "yolo" / "sidequest_theory_candidates_v60"
V61 = ROOT / "experiments" / "yolo" / "sidequest_theory_candidates_v61"
V62 = ROOT / "experiments" / "yolo" / "sidequest_theory_candidates_v62"

SOURCES = {
    V60 / "V60_SELECTED_381_EVENT_LEDGER.tsv": "51d69e33c7a02111c79322fb8c1537e34a61fb91c3f885ea48373c20be890f45",
    V61 / "V61_SELECTED_116_SOURCE_STATEMENTS.tsv": "6083ba9ec5bd2122f953bbcbb4d733fc3cee2c24f7fff75543a73e764c813fc3",
    V62 / "V62_SELECTED_116_REGISTER_TRANSITIONS.tsv": "2ee7d0ef2a5abe49388ba0dc2bc650c1677f3747537059ccd486cac335ca7139",
    V62 / "V62_SELECTED_REGISTER_INVENTORY.tsv": "191be58f2119fb6525b83c3ef7bbb9e570340c9d365f9c439ad1f9764f440003",
}

OUT_TEMPLATES = HERE / "V63_R3_TEMPLATE_DEFINITIONS.tsv"
OUT_EVENTS = HERE / "V63_R3_381_EVENT_TEMPLATE_LEDGER.tsv"
OUT_FIELDS = HERE / "V63_R3_135_FIELD_SLOT_PARSE.tsv"
OUT_STATEMENTS = HERE / "V63_R3_116_STATEMENT_SLOT_PARSE.tsv"
OUT_BASELINES = HERE / "V63_R3_BASELINE_COMPARISON.tsv"

TEMPLATES = {
    "PARAMETER_ASSIGN",
    "TARGET_ASSIGN",
    "LINK_ACTIVE",
    "STATE_GATE",
    "ACTION_APPLY",
    "ACTION_TEMPER",
    "TERMINAL_FLUSH",
    "TERMINAL_DRAIN",
    "SELECT_PART",
    "SELECT_PREVIOUS",
    "COMPOSITE_SEQUENCE",
    "EXEMPLAR_ONLY",
}

EXACT_TEMPLATE = {
    "MASS?": "PARAMETER_ASSIGN",
    "ZIEL?": "TARGET_ASSIGN",
    "ANSATZ?": "LINK_ACTIVE",
    "BEREIT?": "STATE_GATE",
    "KLAR?": "STATE_GATE",
    "ANWENDEN?": "ACTION_APPLY",
    "TEMPERIEREN?": "ACTION_TEMPER",
    "SPÜLEN?": "TERMINAL_FLUSH",
    "ABLASSEN?": "TERMINAL_DRAIN",
    "ANTEIL?": "SELECT_PART",
    "VORIGES?": "SELECT_PREVIOUS",
}

FORMAL_TEMPLATE = {
    "VORGABEPARAMETER?": "PARAMETER_ASSIGN",
    "STANDARDSLOT_SETZEN": "PARAMETER_ASSIGN",
    "LOKALEN_RELATIONSSLOT_SETZEN": "TARGET_ASSIGN",
    "AKTIVEN_ARBEITSSTAND_VERKNÜPFEN": "LINK_ACTIVE",
}

EXPECTED_EVENT_TEMPLATES = {
    "ACTION_APPLY": 10,
    "ACTION_TEMPER": 7,
    "EXEMPLAR_ONLY": 262,
    "LINK_ACTIVE": 26,
    "PARAMETER_ASSIGN": 29,
    "SELECT_PART": 2,
    "SELECT_PREVIOUS": 2,
    "STATE_GATE": 11,
    "TARGET_ASSIGN": 16,
    "TERMINAL_DRAIN": 8,
    "TERMINAL_FLUSH": 8,
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expected_unit_status(templates: list[str]) -> tuple[str, str]:
    recognized = sum(template != "EXEMPLAR_ONLY" for template in templates)
    if not recognized:
        return "EXEMPLAR_ONLY", "UNPARSED"
    primary = templates[0] if len(templates) == 1 else "COMPOSITE_SEQUENCE"
    return primary, "UNIQUE" if recognized == len(templates) else "AMBIGUOUS"


def validate_roundtrip(row: dict[str, str], source_events: list[dict[str, str]]) -> None:
    serials = row["event_serials"].split("|")
    require(serials == [event["event_serial"] for event in source_events], f"event order changed in {serials}")
    expected_digest = hashlib.sha256(
        "|".join(f"{event['event_serial']}:{event['joint_tuple_id']}" for event in source_events).encode("utf-8")
    ).hexdigest()
    require(row["roundtrip_decoded_event_serials"] == "|".join(serials), f"roundtrip decode failed: {serials}")
    require(row["roundtrip_event_identity_sha256"] == expected_digest, f"roundtrip digest failed: {serials}")
    require(row["roundtrip_status"] == "PASS_EXACT_OPAQUE_ID_SEQUENCE", f"roundtrip status failed: {serials}")


def main() -> None:
    for path, digest in SOURCES.items():
        require(sha256(path) == digest, f"selected source drift: {path.name}")

    source_events = read_tsv(next(path for path in SOURCES if path.name == "V60_SELECTED_381_EVENT_LEDGER.tsv"))
    source_statements = read_tsv(next(path for path in SOURCES if path.name == "V61_SELECTED_116_SOURCE_STATEMENTS.tsv"))
    source_machine = read_tsv(next(path for path in SOURCES if path.name == "V62_SELECTED_116_REGISTER_TRANSITIONS.tsv"))
    source_registers = read_tsv(next(path for path in SOURCES if path.name == "V62_SELECTED_REGISTER_INVENTORY.tsv"))
    templates = read_tsv(OUT_TEMPLATES)
    events = read_tsv(OUT_EVENTS)
    fields = read_tsv(OUT_FIELDS)
    statements = read_tsv(OUT_STATEMENTS)
    baselines = read_tsv(OUT_BASELINES)
    require((len(source_events), len(source_statements), len(source_machine), len(source_registers)) == (381, 116, 116, 4), "source count failure")
    require((len(templates), len(events), len(fields), len(statements), len(baselines)) == (12, 381, 135, 116, 6), "output count failure")
    require({row["template"] for row in templates} == TEMPLATES, "candidate template set changed")
    require(tuple(row["register"] for row in source_registers) == ("OWNER", "ACTIVE_ITEM/PREPARATION", "TARGET/STATION", "PREVIOUS_ITEM"), "register inventory changed")

    source_by_serial = {row["event_serial"]: row for row in source_events}
    parsed_by_serial = {row["event_serial"]: row for row in events}
    require(len(source_by_serial) == len(parsed_by_serial) == 381, "event serial uniqueness failure")
    require(list(source_by_serial) == list(parsed_by_serial), "event serial order changed")
    require(Counter(row["event_template"] for row in events) == Counter(EXPECTED_EVENT_TEMPLATES), "event template count drift")
    require(Counter(row["trigger_origin"] for row in events) == Counter({"NO_LICENSED_TRIGGER": 262, "EXACT_JOINT_TUPLE_MNEMONIC": 74, "STRICT_FORMAL_PROMPT_ONLY": 34, "EXACT_PLUS_FORMAL_CONVERGENT": 11}), "origin count drift")

    semantic_words = tuple(EXACT_TEMPLATE)
    for parsed in events:
        source = source_by_serial[parsed["event_serial"]]
        for source_col, out_col in (
            ("page", "page"),
            ("locus", "locus"),
            ("record_unit_id", "record_unit_id"),
            ("field_id", "field_id"),
            ("joint_tuple_id", "joint_tuple_id"),
            ("surface", "surface_display_only"),
            ("formal_formula_opaque", "formal_formula_opaque"),
            ("terminal_status", "terminal_status"),
            ("strict_control_prompt", "strict_formal_prompt"),
            ("ATOMIC_OR_WHOLE_CARD_MNEMONIC", "selected_exact_mnemonic"),
        ):
            require(source[source_col] == parsed[out_col], f"source projection drift E{parsed['event_serial']}:{out_col}")
        exact = EXACT_TEMPLATE.get(source["ATOMIC_OR_WHOLE_CARD_MNEMONIC"])
        formal = FORMAL_TEMPLATE.get(source["strict_control_prompt"])
        require(not (exact and formal and exact != formal), f"channel conflict E{parsed['event_serial']}")
        expected = exact or formal or "EXEMPLAR_ONLY"
        require(parsed["event_template"] == expected, f"wrong deterministic template E{parsed['event_serial']}")
        require(parsed["binding_contract"] == "EXACT_JOINT_TUPLE_ATOMIC;NO_STRING_OR_COMPONENT_INHERITANCE;STRICT_FORMAL_PROMPT_HAS_NO_SEMANTIC_WORD", f"atomic contract failure E{parsed['event_serial']}")
        require(parsed["opaque_roundtrip_atom"] == f"E{source['event_serial']}@{source['joint_tuple_id']}", f"opaque atom failure E{parsed['event_serial']}")
        if formal and not exact:
            require(source["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] == "UNKNOWN", f"formal-only event has exact mnemonic E{parsed['event_serial']}")
            require("SEMANTIC_VALUE=NONE" in parsed["template_payload"], f"formal-only semantic guard missing E{parsed['event_serial']}")
            require(not any(word in parsed["symbolic_register_effect"] for word in semantic_words), f"formal-only semantic inheritance E{parsed['event_serial']}")
        if parsed["event_template"] in {"TERMINAL_FLUSH", "TERMINAL_DRAIN"}:
            require(source["terminal_status"] == "TERMINAL", f"terminal action position failure E{parsed['event_serial']}")
            require(exact is not None and formal is None, f"CLOSE/form-only selected terminal meaning E{parsed['event_serial']}")
        elif parsed["event_template"] != "EXEMPLAR_ONLY":
            require(source["terminal_status"] == "NONCLOSE", f"nonterminal template moved to CLOSE E{parsed['event_serial']}")

    require(sum(row["selected_exact_mnemonic"] != "UNKNOWN" for row in events) == 85, "exact mnemonic coverage changed")
    require(sum(row["strict_formal_prompt"] != "NONE" for row in events) == 45, "formal prompt coverage changed")
    require(sum(row["event_template"] != "EXEMPLAR_ONLY" for row in events) == 119, "bounded event union changed")

    source_statements_by_id = {row["statement_id"]: row for row in source_statements}
    machine_by_id = {row["statement_id"]: row for row in source_machine}
    source_events_by_field: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in source_events:
        source_events_by_field[event["field_id"]].append(event)
    field_to_statement: dict[str, str] = {}
    for statement in source_statements:
        for field_id in statement["constituent_fields"].split("|"):
            require(field_id not in field_to_statement, f"duplicate field assignment: {field_id}")
            field_to_statement[field_id] = statement["statement_id"]
    require(len(field_to_statement) == len(source_events_by_field) == 135, "135-field partition failure")

    require(Counter(row["parse_status"] for row in fields) == Counter({"AMBIGUOUS": 56, "UNPARSED": 65, "UNIQUE": 14}), "field status drift")
    require(Counter(row["primary_template"] for row in fields) == Counter({"COMPOSITE_SEQUENCE": 59, "EXEMPLAR_ONLY": 65, "TERMINAL_FLUSH": 3, "LINK_ACTIVE": 1, "TARGET_ASSIGN": 1, "TERMINAL_DRAIN": 5, "ACTION_APPLY": 1}), "field primary drift")
    require({row["field_id"] for row in fields} == set(source_events_by_field), "field identity drift")
    for row in fields:
        unit_events = source_events_by_field[row["field_id"]]
        unit_templates = [parsed_by_serial[event["event_serial"]]["event_template"] for event in unit_events]
        expected_primary, expected_status = expected_unit_status(unit_templates)
        require((row["primary_template"], row["parse_status"]) == (expected_primary, expected_status), f"field parse drift: {row['field_id']}")
        require(row["statement_id"] == field_to_statement[row["field_id"]], f"field/statement map drift: {row['field_id']}")
        machine = machine_by_id[row["statement_id"]]
        require(row["register_pre_state_statement_envelope"] == machine["pre_state"] and row["register_post_state_statement_envelope"] == machine["post_state"], f"field state envelope drift: {row['field_id']}")
        validate_roundtrip(row, unit_events)

    require(Counter(row["parse_status"] for row in statements) == Counter({"AMBIGUOUS": 49, "UNPARSED": 55, "UNIQUE": 12}), "statement status drift")
    require(Counter(row["primary_template"] for row in statements) == Counter({"COMPOSITE_SEQUENCE": 51, "EXEMPLAR_ONLY": 55, "TERMINAL_FLUSH": 3, "TARGET_ASSIGN": 1, "TERMINAL_DRAIN": 5, "ACTION_APPLY": 1}), "statement primary drift")
    require(list(row["statement_id"] for row in statements) == list(source_statements_by_id), "statement identity/order drift")
    for row in statements:
        source_statement = source_statements_by_id[row["statement_id"]]
        unit_events = [source_by_serial[serial] for serial in source_statement["event_serials"].split("|")]
        unit_templates = [parsed_by_serial[event["event_serial"]]["event_template"] for event in unit_events]
        expected_primary, expected_status = expected_unit_status(unit_templates)
        require((row["primary_template"], row["parse_status"]) == (expected_primary, expected_status), f"statement parse drift: {row['statement_id']}")
        machine = machine_by_id[row["statement_id"]]
        for column in ("pre_state", "owner_operation", "active_item_preparation_operation", "target_station_operation", "previous_item_operation", "post_state"):
            require(row[column] == machine[column], f"machine envelope drift {row['statement_id']}:{column}")
        require(row["complete_creative_reading"] == source_statement["concrete_workshop_reading"], f"creative reading changed: {row['statement_id']}")
        require(row["strongest_segmentation_or_source_alternative"] == source_statement["strongest_alternative"], f"alternative changed: {row['statement_id']}")
        validate_roundtrip(row, unit_events)

    expected_baselines = {
        ("FIELD", "BOUNDED_SLOT_PARSER"): (119, 14, 56, 65, 135, 135, 1),
        ("FIELD", "MNEMONIC_BAG"): (85, 13, 44, 78, 122, 15, 78),
        ("FIELD", "FORM_ONLY"): (45, 1, 34, 100, 100, 39, 44),
        ("STATEMENT", "BOUNDED_SLOT_PARSER"): (119, 12, 49, 55, 116, 116, 1),
        ("STATEMENT", "MNEMONIC_BAG"): (85, 12, 41, 63, 108, 16, 63),
        ("STATEMENT", "FORM_ONLY"): (45, 0, 31, 85, 86, 34, 40),
    }
    require({(row["unit_level"], row["model"]) for row in baselines} == set(expected_baselines), "baseline identity drift")
    for row in baselines:
        observed = tuple(int(row[column]) for column in ("primitive_event_coverage", "unique_units", "ambiguous_units", "unparsed_units", "primary_template_matches_bounded_parser", "lookup_unique_roundtrip_units", "largest_signature_collision_class"))
        require(observed == expected_baselines[(row["unit_level"], row["model"])], f"baseline result drift: {row['unit_level']}/{row['model']}")

    pages = {row["page"] for row in events}
    records = {row["record_unit_id"] for row in events}
    require(pages == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}, "page scope drift")
    require(records == {"H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"}, "record scope drift")
    require(not any("PAGE_HOST" in value for row in events + fields + statements for value in row.values()), "PAGE_HOST leakage")
    print("PASS V63_R3 bounded slot parser")
    print("sources=381_events/135_fields/116_statements/4_registers")
    print("event_coverage=119_recognized/262_exemplar_only")
    print("field_status=14_unique/56_ambiguous/65_unparsed")
    print("statement_status=12_unique/49_ambiguous/55_unparsed")
    print("roundtrip=135_fields+116_statements exact opaque ID sequence PASS")


if __name__ == "__main__":
    main()
