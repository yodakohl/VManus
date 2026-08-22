#!/usr/bin/env python3
"""Validate completeness and layer separation of the V64 R3 edition."""

from __future__ import annotations

import csv
import hashlib
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
YOLO = ROOT / "experiments" / "yolo"

SOURCES = {
    YOLO / "sidequest_theory_candidates_v53" / "V53_SELECTED_FIVE_ARTICLES.tsv": "0408d726d4b3e910abb789e8eb427a82cb4ae13a5586a061b22d289f8e915fa6",
    YOLO / "sidequest_theory_candidates_v60" / "V60_SELECTED_EXACT_CARD_DECISIONS.tsv": "288cc769cd7bf22ed17987f93c640b94513e71b211b473979023c13829cb6fee",
    YOLO / "sidequest_theory_candidates_v60" / "V60_SELECTED_381_EVENT_LEDGER.tsv": "51d69e33c7a02111c79322fb8c1537e34a61fb91c3f885ea48373c20be890f45",
    YOLO / "sidequest_theory_candidates_v61" / "V61_SELECTED_116_SOURCE_STATEMENTS.tsv": "6083ba9ec5bd2122f953bbcbb4d733fc3cee2c24f7fff75543a73e764c813fc3",
    YOLO / "sidequest_theory_candidates_v62" / "V62_SELECTED_116_REGISTER_TRANSITIONS.tsv": "2ee7d0ef2a5abe49388ba0dc2bc650c1677f3747537059ccd486cac335ca7139",
    YOLO / "sidequest_theory_candidates_v63" / "V63_SELECTED_381_EVENT_TEMPLATE_LEDGER.tsv": "f009982934532f1ad02d427feba65017edd93cee1b0819b870c537034278e2c4",
    YOLO / "sidequest_theory_candidates_v63" / "V63_SELECTED_135_FIELD_SLOT_PARSE.tsv": "c6b724d450f999eec873159dc48656e5994f37ffca41d1bcbb4f3f386c8e9680",
    YOLO / "sidequest_theory_candidates_v63" / "V63_SELECTED_116_STATEMENT_SLOT_PARSE.tsv": "09789240ec65a32e36f12d0839335a8f6c5c3a5b8637dfdbe91e88adadd5ab65",
}

OUTS = {
    "events": HERE / "V64_R3_100_EVENT_PLANT_LEDGER.tsv",
    "fields": HERE / "V64_R3_20_FIELD_PLANT_EDITION.tsv",
    "statements": HERE / "V64_R3_19_STATEMENT_COMPARISON.tsv",
    "records": HERE / "V64_R3_5_RECORD_PLANT_EDITION.tsv",
    "graphs": HERE / "V64_R3_5_RECORD_PROCESS_GRAPHS.tsv",
    "costs": HERE / "V64_R3_10_RECORD_MODEL_ASSUMPTION_COSTS.tsv",
}

FIXED = {
    "MASS?": "MASS?=vorgesehenen Mengenwert buchen",
    "ANWENDEN?": "ANWENDEN?=aktive Charge am gesetzten Arbeitsziel einsetzen",
    "BEREIT?": "BEREIT?=Freigabestand der aktiven Charge prüfen",
    "ANSATZ?": "ANSATZ?=aktiven Arbeitsansatz aufnehmen",
    "ZIEL?": "ZIEL?=Arbeitsziel setzen oder bestätigen",
    "KLAR?": "KLAR?=Klarzustand der aktiven Charge prüfen",
    "VORIGES?": "VORIGES?=vorige Charge wieder aufnehmen",
    "ANTEIL?": "ANTEIL?=bezeichnete Fraktion wählen",
}

WEIGHTS = {
    "PART_OR_HARVEST": 1,
    "PROCESS_STEP": 1,
    "MEDIUM_OR_ADDITIVE": 1,
    "CONTAINER_OR_TARGET": 1,
    "STORAGE_CONDITION": 1,
    "PRODUCT_FUNCTION": 2,
    "DISEASE_OR_BODY": 2,
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


def decode_cost(text: str) -> tuple[dict[str, int], int]:
    if text == "NONE":
        return {}, 0
    counts: dict[str, int] = {}
    for item in text.split("|"):
        key, raw_count = item.split(":")
        require(key in WEIGHTS and key not in counts, f"invalid cost token: {item}")
        counts[key] = int(raw_count)
    return counts, sum(WEIGHTS[key] * count for key, count in counts.items())


def main() -> None:
    for path, expected in SOURCES.items():
        require(sha256(path) == expected, f"selected source drift: {path.name}")

    articles = source_named("V53_SELECTED_FIVE_ARTICLES.tsv")
    source_events_all = source_named("V60_SELECTED_381_EVENT_LEDGER.tsv")
    source_statements_all = source_named("V61_SELECTED_116_SOURCE_STATEMENTS.tsv")
    source_machine_all = source_named("V62_SELECTED_116_REGISTER_TRANSITIONS.tsv")
    parse_events_all = source_named("V63_SELECTED_381_EVENT_TEMPLATE_LEDGER.tsv")
    parse_fields_all = source_named("V63_SELECTED_135_FIELD_SLOT_PARSE.tsv")
    parse_statements_all = source_named("V63_SELECTED_116_STATEMENT_SLOT_PARSE.tsv")
    require(Counter(row["parse_status"] for row in parse_fields_all) == Counter({"UNIQUE": 14, "AMBIGUOUS": 56, "UNPARSED": 65}), "overall V63 status constraint drift")

    source_events = [row for row in source_events_all if row["record_unit_id"].startswith("H")]
    source_statements = [row for row in source_statements_all if row["record_unit_id"].startswith("H")]
    source_machine = [row for row in source_machine_all if row["record_unit_id"].startswith("H")]
    parse_events = [row for row in parse_events_all if row["record_unit_id"].startswith("H")]
    parse_fields = [row for row in parse_fields_all if row["record_unit_id"].startswith("H")]
    parse_statements = [row for row in parse_statements_all if row["record_unit_id"].startswith("H")]

    events = read_tsv(OUTS["events"])
    fields = read_tsv(OUTS["fields"])
    statements = read_tsv(OUTS["statements"])
    records = read_tsv(OUTS["records"])
    graphs = read_tsv(OUTS["graphs"])
    costs = read_tsv(OUTS["costs"])
    require((len(events), len(fields), len(statements), len(records), len(graphs), len(costs)) == (100, 20, 19, 5, 5, 10), "output counts changed")
    require((len(source_events), len(source_statements), len(source_machine), len(parse_events), len(parse_fields), len(parse_statements)) == (100, 19, 19, 100, 20, 19), "selected Herbal scope changed")
    require({row["page"] for row in events} == {"f10r", "f11r", "f55v", "f56r"}, "page scope changed")
    require({row["record_unit_id"] for row in events} == {"H1", "H2", "H3", "H4", "H5"}, "record scope changed")

    source_by_serial = {row["event_serial"]: row for row in source_events}
    parse_by_serial = {row["event_serial"]: row for row in parse_events}
    require(list(row["event_serial"] for row in events) == list(source_by_serial), "event identity/order drift")
    require(Counter(row["event_template"] for row in events) == Counter({"EXEMPLAR_ONLY": 71, "PARAMETER_ASSIGN": 10, "LINK_ACTIVE": 8, "STATE_GATE": 4, "ACTION_APPLY": 3, "TARGET_ASSIGN": 2, "SELECT_PREVIOUS": 1, "SELECT_PART": 1}), "Herbal event-template drift")
    require(Counter(row["fixed_exact_mnemonic"] for row in events) == Counter({"UNKNOWN": 76, "MASS?": 9, "ANSATZ?": 5, "ANWENDEN?": 3, "BEREIT?": 3, "VORIGES?": 1, "KLAR?": 1, "ZIEL?": 1, "ANTEIL?": 1}), "fixed exact values drift")
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
            require(source[source_col] == row[output_col], f"event source projection drift E{row['event_serial']}:{output_col}")
        for parse_col, output_col in (
            ("selected_exact_mnemonic", "fixed_exact_mnemonic"),
            ("strict_formal_prompt", "strict_formal_prompt"),
            ("event_template", "event_template"),
            ("event_parse_status", "event_parse_status"),
            ("opaque_roundtrip_atom", "opaque_roundtrip_atom"),
        ):
            require(parsed[parse_col] == row[output_col], f"V63 event layer drift E{row['event_serial']}:{output_col}")
        mnemonic = row["fixed_exact_mnemonic"]
        require(row["fixed_value_clause"] == FIXED.get(mnemonic, "NONE"), f"fixed mnemonic clause drift E{row['event_serial']}")
        require(row["complete_layered_technical_reading"] and row["v64_local_plant_filler"], f"incomplete event reading E{row['event_serial']}")
        require(row["noninheritance_contract"] == "EXACT_TUPLE_ATOMIC;EXACT_VALUE_FIXED;FORMAL_PROMPT_NO_SEMANTIC_WORD;LOCAL_FILLER_NEVER_CARD_GLOSS", f"binding contract drift E{row['event_serial']}")
        if mnemonic == "UNKNOWN":
            require(row["fixed_value_clause"] == "NONE", f"UNKNOWN received exact value E{row['event_serial']}")
        if row["strict_formal_prompt"] != "NONE" and mnemonic == "UNKNOWN":
            require(row["local_filler_source_class"].startswith("V63_FORMAL_CHANNEL_NO_SEMANTIC_WORD"), f"formal-only inheritance E{row['event_serial']}")
        if row["event_template"] == "EXEMPLAR_ONLY":
            require("NOT_CARD_MEANING" in row["local_filler_source_class"], f"exemplar promoted to card meaning E{row['event_serial']}")

    parse_field_by_id = {row["field_id"]: row for row in parse_fields}
    events_by_field: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        events_by_field[row["field_id"]].append(row)
    require(Counter(row["v63_parse_status_fixed"] for row in fields) == Counter({"AMBIGUOUS": 15, "UNPARSED": 5}), "Herbal field status drift")
    require({row["field_id"] for row in fields} == set(events_by_field) == set(parse_field_by_id), "field partition drift")
    for row in fields:
        parsed = parse_field_by_id[row["field_id"]]
        unit_events = events_by_field[row["field_id"]]
        require(row["event_serials"].split("|") == [event["event_serial"] for event in unit_events], f"field event order drift {row['field_id']}")
        for source_col, output_col in (
            ("statement_id", "statement_id"),
            ("parse_status", "v63_parse_status_fixed"),
            ("primary_template", "v63_primary_template"),
            ("ordered_event_template_sequence", "v63_ordered_template_sequence"),
            ("register_pre_state_statement_envelope", "register_pre_state_statement_envelope"),
            ("register_post_state_statement_envelope", "register_post_state_statement_envelope"),
            ("opaque_roundtrip_trace", "opaque_roundtrip_trace"),
            ("roundtrip_status", "roundtrip_status"),
        ):
            require(parsed[source_col] == row[output_col], f"field parser layer drift {row['field_id']}:{output_col}")
        require(row["complete_technical_field_reading"] and row["local_plant_input"] and row["local_plant_output"], f"incomplete field {row['field_id']}")

    source_statement_by_id = {row["statement_id"]: row for row in source_statements}
    machine_by_id = {row["statement_id"]: row for row in source_machine}
    parse_statement_by_id = {row["statement_id"]: row for row in parse_statements}
    require(list(row["statement_id"] for row in statements) == list(source_statement_by_id), "statement identity/order drift")
    require(Counter(row["v63_parse_status_fixed"] for row in statements) == Counter({"AMBIGUOUS": 14, "UNPARSED": 5}), "Herbal statement status drift")
    require(Counter(row["coherence_winner"] for row in statements) == Counter({"TECHNICAL": 8, "IATROMEDICAL": 5, "TIE": 6}), "statement comparison drift")
    for row in statements:
        source = source_statement_by_id[row["statement_id"]]
        machine = machine_by_id[row["statement_id"]]
        parsed = parse_statement_by_id[row["statement_id"]]
        require(row["event_serials"] == source["event_serials"] and row["constituent_fields"] == source["constituent_fields"], f"statement source scope drift {row['statement_id']}")
        require(row["complete_iatromedical_comparator"] == source["concrete_workshop_reading"], f"iatromedical statement changed {row['statement_id']}")
        require(row["v63_parse_status_fixed"] == parsed["parse_status"] and row["v63_ordered_template_sequence"] == parsed["ordered_event_template_sequence"], f"statement parser drift {row['statement_id']}")
        for column in ("pre_state", "owner_operation", "active_item_preparation_operation", "target_station_operation", "previous_item_operation", "post_state"):
            require(row[column] == machine[column], f"statement register drift {row['statement_id']}:{column}")
        require(row["opaque_roundtrip_trace"] == parsed["opaque_roundtrip_trace"] and row["roundtrip_status"] == parsed["roundtrip_status"], f"statement roundtrip drift {row['statement_id']}")
        _, tech_cost = decode_cost(row["technical_assumptions"])
        _, medical_cost = decode_cost(row["iatromedical_assumptions"])
        require(tech_cost == int(row["technical_weighted_cost"]), f"technical cost drift {row['statement_id']}")
        require(medical_cost == int(row["iatromedical_weighted_cost"]), f"medical cost drift {row['statement_id']}")

    article_by_id = {row["article_id"]: row for row in articles}
    records_by_id = {row["record_unit_id"]: row for row in records}
    graph_by_id = {row["record_unit_id"]: row for row in graphs}
    require(set(records_by_id) == set(graph_by_id) == set(article_by_id) == {"H1", "H2", "H3", "H4", "H5"}, "record/graph identity drift")
    expected_record_counts = {"H1": (2, 2, 14, 4), "H2": (3, 3, 24, 10), "H3": (4, 4, 17, 3), "H4": (4, 4, 18, 6), "H5": (7, 6, 27, 6)}
    expected_record_winners = {"H1": "IATROMEDICAL", "H2": "TECHNICAL_INTERNAL_ONLY", "H3": "IATROMEDICAL", "H4": "TECHNICAL_INTERNAL_ONLY", "H5": "TIE"}
    for record, row in records_by_id.items():
        article = article_by_id[record]
        observed = tuple(int(row[column]) for column in ("field_count", "statement_count", "event_count", "recognized_event_count"))
        require(observed == expected_record_counts[record], f"record counts drift {record}")
        require(row["best_visible_plant_category_fixed"] == article["pictured_owner_default"] and row["strongest_visual_rival_fixed"] == article["pictured_owner_rival"], f"fixed visual inventory drift {record}")
        require(row["complete_iatromedical_article"] == article["selected_complete_working_translation_German"], f"iatromedical article changed {record}")
        require(row["record_coherence_winner"] == expected_record_winners[record], f"record winner drift {record}")
        record_fields = [field["field_id"] for field in fields if field["record_unit_id"] == record]
        require(graph_by_id[record]["field_path"].split("|") == record_fields, f"process graph field path drift {record}")
        require(graph_by_id[record]["execution_rule"] == "FOLLOW_FIELD_PATH;APPLY_V62_STATEMENT_TRANSITION;EXECUTE_LICENSED_V63_TEMPLATE;EXPAND_EXEMPLAR_LOCALLY;COMMIT_ONLY_OBSERVED_TERMINAL", f"graph execution rule drift {record}")

    require(sum(int(row["technical_weighted_cost"]) for row in statements) == 113, "technical total assumption cost drift")
    require(sum(int(row["iatromedical_weighted_cost"]) for row in statements) == 107, "iatromedical total assumption cost drift")
    require(Counter(row["model"] for row in costs) == Counter({"TECHNICAL_PLANT_REGISTER": 5, "IATROMEDICAL": 5}), "cost model rows drift")
    for row in costs:
        _, cost = decode_cost(row["assumption_counts"])
        require(cost == int(row["weighted_cost"]), f"record cost recomputation failed {row['record_unit_id']}/{row['model']}")
    require(not any("PAGE_HOST" in value for rows in (events, fields, statements, records, graphs, costs) for row in rows for value in row.values()), "PAGE_HOST leakage")
    print("PASS V64_R3 technical plant edition")
    print("coverage=5_records/19_statements/20_fields/100_events")
    print("Herbal_status=0_unique/15_ambiguous/5_unparsed_fields;14_ambiguous/5_unparsed_statements")
    print("statement_comparison=8_technical/5_iatromedical/6_tie")
    print("weighted_assumption_cost=113_technical/107_iatromedical")
    print("roundtrip_and_selected_layers=PASS")


if __name__ == "__main__":
    main()
