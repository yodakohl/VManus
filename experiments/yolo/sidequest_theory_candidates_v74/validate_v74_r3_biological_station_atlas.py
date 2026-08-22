#!/usr/bin/env python3
"""Validate V74 R3's bounded Biological station-atlas edition."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
V69 = ROOT / "experiments/yolo/sidequest_theory_candidates_v69"
V71 = ROOT / "experiments/yolo/sidequest_theory_candidates_v71"
V72 = ROOT / "experiments/yolo/sidequest_theory_candidates_v72"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


checks: list[dict[str, object]] = []


def check(name: str, condition: bool, detail: object) -> None:
    checks.append({"name": name, "pass": bool(condition), "detail": detail})


def main() -> None:
    event_path = OUT / "V74_R3_281_EVENT_INTERLINEAR.tsv"
    field_path = OUT / "V74_R3_115_FIELD_EDITION.tsv"
    statement_path = OUT / "V74_R3_97_STATEMENT_EDITION.tsv"
    record_path = OUT / "V74_R3_SIX_RECORD_EDITION.tsv"
    station_path = OUT / "V74_R3_STATION_COMPARISON.tsv"
    graph_path = OUT / "V74_R3_LOCAL_PROCESS_GRAPHS.tsv"
    report_path = OUT / "V74_R3_TECHNICAL_REPORT.md"
    summary_path = OUT / "V74_R3_BUILD_SUMMARY.json"
    required = [event_path, field_path, statement_path, record_path, station_path, graph_path, report_path, summary_path]
    check("all_required_outputs_exist", all(path.is_file() for path in required), [path.name for path in required])

    events = read_tsv(event_path)
    fields = read_tsv(field_path)
    statements = read_tsv(statement_path)
    records = read_tsv(record_path)
    stations = read_tsv(station_path)
    graph = read_tsv(graph_path)
    source_events = {
        int(row["event_serial"]): row
        for row in read_tsv(V69 / "V69_R4_FINAL_381_PROSE_EVENT_INTERLINEAR.tsv")
        if 101 <= int(row["event_serial"]) <= 381
    }
    source_fields = {
        row["field_id"]: row
        for row in read_tsv(V69 / "V69_R4_FINAL_135_FIELD_EDITION.tsv")
        if row["record_unit_id"].startswith("B")
    }
    source_owners = {
        row["unit_id"]: row
        for row in read_tsv(V71 / "V71_SELECTED_OWNER_LEDGER.tsv")
        if row["section"] == "BIOLOGICAL" and row["unit_kind"] == "PROSE_FIELD"
    }
    source_statements = {
        row["statement_id"]: row
        for row in read_tsv(V72 / "V72_SELECTED_116_STATEMENTS.tsv")
        if row["record_unit_id"].startswith("B")
    }

    check("exact_281_events", len(events) == 281, len(events))
    check("event_serials_101_through_381_once", [int(row["event_serial"]) for row in events] == list(range(101, 382)), [events[0]["event_serial"], events[-1]["event_serial"]])
    check("exact_115_fields", len(fields) == 115, len(fields))
    check("field_ids_F021_through_F135_once", [row["field_id"] for row in fields] == [f"F{i:03d}" for i in range(21, 136)], [fields[0]["field_id"], fields[-1]["field_id"]])
    check("exact_97_statements", len(statements) == 97, len(statements))
    check("statement_ids_match_frozen_v72", {row["statement_id"] for row in statements} == set(source_statements), len(source_statements))
    check("exact_six_records", len(records) == 6 and [row["record_unit_id"] for row in records] == ["B1", "B2", "B3", "B4", "B5", "B6"], [row["record_unit_id"] for row in records])
    check("only_f81v_f82r_f83r", {row["page"] for row in events} == {"f81v", "f82r", "f83r"}, sorted({row["page"] for row in events}))

    check("all_event_cells_nonblank", all(all(value.strip() for value in row.values()) for row in events), "281 complete rows")
    check("all_field_cells_nonblank", all(all(value.strip() for value in row.values()) for row in fields), "115 complete rows")
    check("all_statement_cells_nonblank", all(all(value.strip() for value in row.values()) for row in statements), "97 complete rows")
    check("all_record_cells_nonblank", all(all(value.strip() for value in row.values()) for row in records), "6 complete rows")
    check("all_station_cells_nonblank", all(all(value.strip() for value in row.values()) for row in stations), "station comparison complete")
    check("all_graph_cells_nonblank", all(all(value.strip() for value in row.values()) for row in graph), "graph complete")

    immutable_columns = [
        "page", "locus", "record_unit_id", "field_id", "statement_id", "joint_tuple_id",
        "surface_display_only", "formal_formula_opaque", "terminal_status", "parse_status",
        "selected_exact_mnemonic", "strict_formal_prompt", "event_template",
    ]
    identity_ok = True
    for row in events:
        source = source_events[int(row["event_serial"])]
        identity_ok &= all(row[column] == source[column] for column in immutable_columns)
    check("exact_opaque_event_and_control_identity_retained", identity_ok, immutable_columns)

    field_identity_ok = True
    for row in fields:
        source = source_fields[row["field_id"]]
        field_identity_ok &= all(row[column] == source[column] for column in ["record_unit_id", "page", "locus", "statement_id", "event_count", "event_serials"])
    check("exact_field_membership_retained", field_identity_ok, "115/115")

    owner_ok = all(
        row["local_visible_or_inherited_owner"] == source_owners[row["field_id"]]["selected_visible_owner"]
        and row["local_owner_status"] == source_owners[row["field_id"]]["owner_status"]
        for row in events
    )
    check("all_event_owners_match_v71", owner_ok, "281/281")
    owner_status_by_field = Counter(row["local_owner_status"] for row in fields)
    check("frozen_owner_status_distribution", owner_status_by_field == Counter({"INHERITED_VISIBLE": 87, "UNRESOLVED": 14, "DIRECT_VISIBLE": 13, "PAGE_OWNER_ONLY": 1}), dict(owner_status_by_field))

    literal_ok = True
    for row in events:
        fragments = [
            f"E{row['event_serial']}:[TUPLE:{row['joint_tuple_id']}",
            f"SURFACE_DISPLAY_ONLY:{row['surface_display_only']}",
            f"FORMULA:{row['formal_formula_opaque']}",
            f"CARD:{row['selected_exact_mnemonic']}",
            f"PROMPT:{row['strict_formal_prompt']}",
            f"TEMPLATE:{row['event_template']}",
            "FROZEN_V72_SEGMENT:",
            f"TERMINAL:{row['terminal_status']}",
        ]
        literal_ok &= all(fragment in row["literal_exact_card_formal_exemplar_layer"] for fragment in fragments)
    check("complete_literal_layer_every_event", literal_ok, "8 immutable fragments per event")

    parse_counts = Counter(row["parse_status"] for row in events)
    exemplar_count = parse_counts["UNPARSED_EXEMPLAR"]
    check("frozen_191_exemplar_90_supported_split", exemplar_count == 191 and len(events) - exemplar_count == 90, {"exemplar": exemplar_count, "supported": len(events) - exemplar_count})
    check("source_class_marks_all_exemplar_events", all((row["source_class"] == "OCCURRENCE_EXEMPLAR_ONLY") == (row["parse_status"] == "UNPARSED_EXEMPLAR") for row in events), Counter(row["source_class"] for row in events))

    check("every_event_has_concrete_german_default", all(row["concrete_german_operational_default"].endswith(".") and len(row["concrete_german_operational_default"]) >= 45 for row in events), min(len(row["concrete_german_operational_default"]) for row in events))
    check("all_event_confidences_low_and_bounded", all(0.0 < float(row["operational_default_confidence"]) < 0.55 for row in events), sorted({row["operational_default_confidence"] for row in events}))
    check("every_event_has_medical_rival", all(row["strongest_medical_rival"].startswith("MEDICAL_RIVAL:") for row in events), "281/281")
    check("every_event_has_formal_rival", all(row["strongest_iconographic_or_formal_rival"].startswith("FORMAL_RIVAL:") for row in events), "281/281")
    check("every_event_has_substantial_contradiction", all(len(row["hardest_contradiction"]) >= 120 for row in events), min(len(row["hardest_contradiction"]) for row in events))
    check("semantic_ceiling_every_event", all("NOT_WORD_CARD_STEM_SOUND_LANGUAGE_OR_TRANSLATION" in row["semantic_ceiling"] for row in events), "281/281")

    unresolved_fields = {"F057", "F058"} | {f"F{i:03d}" for i in range(87, 99)}
    actual_unresolved = {row["field_id"] for row in fields if row["local_owner_status"] == "UNRESOLVED"}
    check("exact_unresolved_field_set", actual_unresolved == unresolved_fields, sorted(actual_unresolved))
    unresolved_events = [row for row in events if row["local_owner_status"] == "UNRESOLVED"]
    check("unresolved_events_quarantined", all("QUARANTINE_OWNER;BLOCK_PHYSICAL_CARRY" in row["operational_register_effect"] for row in unresolved_events), len(unresolved_events))
    check("unresolved_events_forbid_material_state_carry", all("NO_MATERIAL_OR_STATE_CARRY" in row["contact_direction_constraint"] for row in unresolved_events), len(unresolved_events))

    changed_owner_first_fields = {"F053", "F057", "F059", "F062", "F075", "F080", "F087", "F099", "F120", "F126"}
    changed_owner_ok = all(
        next(row for row in fields if row["field_id"] == field_id)["incoming_contact_and_reset"].startswith("BREAK_VISIBLE_OWNER")
        for field_id in changed_owner_first_fields
    )
    check("all_ten_in_record_owner_changes_break_physical_carry", changed_owner_ok, sorted(changed_owner_first_fields))

    critical_break_statements = {"B2-S012", "B3-S016", "B3-S026", "B4-S015"}
    critical_rows = {row["statement_id"]: row for row in statements if row["statement_id"] in critical_break_statements}
    check("four_cross_statement_gaps_retained", set(critical_rows) == critical_break_statements and all(row["contact_direction_constraint"] == "BREAK_ENFORCED" and "BREAK_VISIBLE_GAP" in row["owner_transition"] for row in critical_rows.values()), sorted(critical_rows))

    statement_exact_ok = True
    for row in statements:
        source = source_statements[row["statement_id"]]
        for column in ["record_unit_id", "page", "constituent_fields", "event_count", "event_serials", "owner_bindings", "owner_transition", "source_class", "literal_owner_card_exemplar_layer", "repair_cost_0_4", "repair_reason", "line_crossing", "hardest_contradiction"]:
            target_column = "frozen_v72_technical_paraphrase" if column == "selected_concrete_paraphrase" else column
            statement_exact_ok &= row.get(target_column, "") == source[column]
        statement_exact_ok &= row["frozen_v72_technical_paraphrase"] == source["selected_concrete_paraphrase"]
    check("v72_statement_structure_and_paraphrase_retained", statement_exact_ok, "97/97")

    record_counts = {
        "B1": (66, 24, 21), "B2": (62, 26, 22), "B3": (86, 38, 34),
        "B4": (47, 20, 16), "B5": (11, 5, 3), "B6": (9, 2, 1),
    }
    record_count_ok = all(
        (int(row["event_count"]), int(row["field_count"]), int(row["statement_count"])) == record_counts[row["record_unit_id"]]
        for row in records
    )
    check("record_event_field_statement_counts_exact", record_count_ok, record_counts)
    b5 = next(row for row in records if row["record_unit_id"] == "B5")
    b6 = next(row for row in records if row["record_unit_id"] == "B6")
    check("B5_B6_hard_reset_in_record_rules", "NO_B5_TO_B6_CARRY" in b5["record_reset_rule"] and "NO_B5_TO_B6_CARRY" in b6["record_reset_rule"], [b5["record_reset_rule"], b6["record_reset_rule"]])

    check("exact_16_station_comparisons", len(stations) == 16 and len({row["station_owner"] for row in stations}) == 16, len(stations))
    check("station_comparison_has_three_readings", all(row["technical_operational_reading"] and row["medical_reading"] and row["iconographic_or_formal_reading"] for row in stations), "16/16")
    check("unresolved_stations_have_formal_quarantine_lead", all(row["r3_local_lead"] == "FORMAL_QUARANTINE_LEAD" for row in stations if "UNRESOLVED" in row["station_owner"] or "AMBIGUOUS" in row["station_owner"]), [row["station_owner"] for row in stations if row["r3_local_lead"] == "FORMAL_QUARANTINE_LEAD"])

    check("graph_has_18_frozen_edges", len(graph) == 18, len(graph))
    check("graph_never_has_directed_edge", {row["directedness"] for row in graph} <= {"UNDIRECTED", "NONE"}, sorted({row["directedness"] for row in graph}))
    check("graph_prohibits_global_flow_everywhere", all(row["prohibited_inference"].startswith("NO_GLOBAL_FLOW") for row in graph), "18/18")
    required_graph_statuses = {"VISIBLE_LOCAL_CONTACT", "NO_VISIBLE_EDGE", "CONTACT_UNRESOLVED", "RECORD_RESET", "VISIBLE_LOCAL_ATTACHMENT_BUT_TEXT_OWNER_RESET"}
    check("graph_contains_contacts_gaps_unresolved_and_reset", required_graph_statuses <= {row["edge_status"] for row in graph}, sorted({row["edge_status"] for row in graph}))
    reset_edges = [row for row in graph if row["record_scope"] == "B5_TO_B6"]
    check("graph_has_explicit_B5_to_B6_no_carry", len(reset_edges) == 1 and reset_edges[0]["edge_status"] == "RECORD_RESET" and reset_edges[0]["permitted_register_or_material_carry"] == "FORBID_ALL_REGISTER_CARRY", reset_edges)
    pair_edges = [row for row in graph if row["edge_status"] == "VISIBLE_LOCAL_CONTACT" and "MAIN_PAIR" in row["endpoint_a"]]
    check("both_B3_and_B4_main_pairs_visible_and_undirected", {row["record_scope"] for row in pair_edges} == {"B3", "B4"} and all(row["directedness"] == "UNDIRECTED" for row in pair_edges), [(row["record_scope"], row["directedness"]) for row in pair_edges])

    terminal_events = [row for row in events if row["terminal_status"] == "TERMINAL"]
    check("frozen_85_terminal_forms", len(terminal_events) == 85, len(terminal_events))
    physical_terminal = [row for row in events if row["event_template"] in {"TERMINAL_FLUSH", "TERMINAL_DRAIN"}]
    check("only_16_typed_flush_or_drain_events", len(physical_terminal) == 16, Counter(row["event_template"] for row in physical_terminal))
    generic_terminal = [row for row in terminal_events if row["event_template"] not in {"TERMINAL_FLUSH", "TERMINAL_DRAIN"}]
    check("generic_close_not_promoted_to_physical_operation", all("FORMAL_CLOSE_ONLY" in row["operational_register_effect"] for row in generic_terminal), len(generic_terminal))

    check("no_global_direction_in_event_constraints", all("NO_GLOBAL_FLOW_DIRECTION" in row["contact_direction_constraint"] for row in events), "281/281")
    dangerous_positive_direction = [
        row["event_serial"] for row in events
        if any(term in row["concrete_german_operational_default"].lower() for term in ["im uhrzeigersinn", "gegen den uhrzeigersinn", "stromaufwärts", "stromabwärts", "globaler rücklauf", "quelle speist"])
    ]
    check("no_positive_global_direction_language", not dangerous_positive_direction, dangerous_positive_direction)

    events_by_field: dict[str, list[int]] = defaultdict(list)
    for row in events:
        events_by_field[row["field_id"]].append(int(row["event_serial"]))
    field_roundtrip = all(
        row["event_serials"] == "|".join(str(value) for value in events_by_field[row["field_id"]])
        and int(row["event_count"]) == len(events_by_field[row["field_id"]])
        for row in fields
    )
    check("field_event_sequences_roundtrip", field_roundtrip, "115/115")
    check("statement_event_total_281", sum(int(row["event_count"]) for row in statements) == 281, sum(int(row["event_count"]) for row in statements))

    report = report_path.read_text(encoding="utf-8")
    required_report_phrases = [
        "281 Ereignisse", "115 Felder", "97 Aussagen", "6 Records", "191", "90",
        "Ausführbare Registerregel", "Kontaktgraph und harte Sperren", "B5 -> B6",
        "F057–F058", "F087–F098", "keine Entzifferung oder Übersetzung", "f84 und f84r",
    ]
    check("report_contains_complete_scope_gaps_and_ceiling", all(phrase in report for phrase in required_report_phrases), required_report_phrases)

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    expected_summary_counts = {
        "events": 281, "fields": 115, "statements": 97, "records": 6,
        "station_owners": 16, "graph_edges": 18, "recognized_or_formal_events": 90,
        "exemplar_only_events": 191, "unresolved_fields": 14,
    }
    check("build_summary_counts_exact", summary["counts"] == expected_summary_counts, summary["counts"])
    check("build_summary_denies_global_direction", summary["global_direction"] == "NOT_INFERRED", summary["global_direction"])
    check("f84_and_f84r_declared_sealed", summary["sealed"] == ["f84", "f84r"], summary["sealed"])

    failed = [item for item in checks if not item["pass"]]
    result = {
        "experiment": "V74_R3_BIOLOGICAL_STATION_ATLAS_THIRD_EDITION",
        "status": "PASS" if not failed else "FAIL",
        "passed": len(checks) - len(failed),
        "total": len(checks),
        "failed": [item["name"] for item in failed],
        "dimensions": {"events": len(events), "fields": len(fields), "statements": len(statements), "records": len(records), "stations": len(stations), "graph_edges": len(graph)},
        "checks": checks,
        "global_direction": "NOT_INFERRED",
        "sealed": ["f84", "f84r"],
    }
    (OUT / "V74_R3_VALIDATION.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if failed:
        for item in failed:
            print(f"FAIL {item['name']}: {item['detail']}")
        raise SystemExit(1)
    print(f"PASS {len(checks)}/{len(checks)} checks")


if __name__ == "__main__":
    main()
