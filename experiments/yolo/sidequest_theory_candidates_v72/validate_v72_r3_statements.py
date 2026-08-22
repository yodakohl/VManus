#!/usr/bin/env python3
"""Independent validator for the V72 R3 116-statement edition."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OUT = HERE / "V72_R3_116_STATEMENTS.tsv"
REVISIONS = HERE / "V72_R3_REVISIONS.tsv"
REPORT = HERE / "V72_R3_TECHNICAL_REPORT.md"
STATEMENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v69/V69_R4_FINAL_116_STATEMENT_EDITION.tsv"
FIELDS = ROOT / "experiments/yolo/sidequest_theory_candidates_v69/V69_R4_FINAL_135_FIELD_EDITION.tsv"
EVENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v69/V69_R4_FINAL_381_PROSE_EVENT_INTERLINEAR.tsv"
OWNERS = ROOT / "experiments/yolo/sidequest_theory_candidates_v71/V71_SELECTED_OWNER_LEDGER.tsv"
VALIDATION = HERE / "V72_R3_VALIDATION.json"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def gate(name: str, passed: bool, detail: object) -> dict[str, object]:
    return {"gate": name, "status": "PASS" if passed else "FAIL", "detail": detail}


def main() -> None:
    rows = read(OUT)
    statements = read(STATEMENTS)
    fields = read(FIELDS)
    events = read(EVENTS)
    owners = [r for r in read(OWNERS) if r["unit_kind"] == "PROSE_FIELD"]
    revisions = read(REVISIONS)
    report = REPORT.read_text(encoding="utf-8")
    source_by_sid = {r["statement_id"]: r for r in statements}
    field_by_id = {r["field_id"]: r for r in fields}
    owner_by_field = {r["unit_id"]: r for r in owners}
    event_by_serial = {r["event_serial"]: r for r in events}

    required = {
        "statement_id", "record_unit_id", "page", "statement_ordinal_in_record",
        "constituent_fields", "event_count", "event_serials", "v69_primary_template",
        "v69_primitive_sequence", "v69_parse_status", "v71_field_owner_bindings",
        "exact_v71_owner_transition", "literal_owner_known_card_exemplar_layer",
        "source_class", "technical_source_class_paraphrase",
        "strongest_medical_or_formal_rival", "repair_cost_0_4", "repair_reason",
        "line_crossing", "contact_direction_constraint", "hardest_contradiction",
        "v69_pre_state", "v69_post_state", "semantic_ceiling",
    }
    gates = []
    gates.append(gate("schema_complete", set(rows[0]) == required, sorted(set(rows[0]) ^ required)))
    gates.append(gate("exact_116_statements", len(rows) == 116, len(rows)))
    gates.append(gate("statement_identity_and_order", [r["statement_id"] for r in rows] == [r["statement_id"] for r in statements], [rows[0]["statement_id"], rows[-1]["statement_id"]]))
    gates.append(gate("eleven_records", Counter(r["record_unit_id"] for r in rows) == Counter(r["record_unit_id"] for r in statements), dict(Counter(r["record_unit_id"] for r in rows))))
    gates.append(gate("event_sum_381", sum(int(r["event_count"]) for r in rows) == 381, sum(int(r["event_count"]) for r in rows)))

    output_event_serials = []
    output_field_ids = []
    source_metadata_ok = True
    owner_bindings_ok = True
    line_crossing_ok = True
    literal_complete = True
    literal_known_tags = True
    for row in rows:
        source = source_by_sid[row["statement_id"]]
        for key_out, key_source in (
            ("record_unit_id", "record_unit_id"), ("page", "page"),
            ("statement_ordinal_in_record", "statement_ordinal_in_record"),
            ("constituent_fields", "constituent_fields"), ("event_count", "event_count"),
            ("event_serials", "event_serials"), ("v69_primary_template", "primary_template"),
            ("v69_primitive_sequence", "licensed_primitive_sequence"),
            ("v69_parse_status", "parse_status"), ("v69_pre_state", "pre_state"),
            ("v69_post_state", "post_state"),
        ):
            if row[key_out] != source[key_source]:
                source_metadata_ok = False
        field_ids = row["constituent_fields"].split("|")
        output_field_ids.extend(field_ids)
        expected_bindings = " > ".join(
            f"{fid}={owner_by_field[fid]['owner_status']}:{owner_by_field[fid]['selected_visible_owner']}"
            for fid in field_ids
        )
        if row["v71_field_owner_bindings"] != expected_bindings:
            owner_bindings_ok = False
        loci = []
        for fid in field_ids:
            locus = field_by_id[fid]["locus"]
            if locus not in loci:
                loci.append(locus)
        expected_crossing = f"NO:{loci[0]}" if len(loci) == 1 else "YES:" + "→".join(loci) + "; CLAUSE_CONTINUES_ACROSS_PHYSICAL_LINES"
        if row["line_crossing"] != expected_crossing:
            line_crossing_ok = False
        serials = row["event_serials"].split("|")
        output_event_serials.extend(serials)
        literal = row["literal_owner_known_card_exemplar_layer"]
        for serial in serials:
            event = event_by_serial[serial]
            if f"E{int(serial):03d}[" not in literal:
                literal_complete = False
            mnemonic = event["selected_exact_mnemonic"]
            prompt = event["strict_formal_prompt"]
            if mnemonic != "UNKNOWN" and f"CARD={mnemonic}" not in literal:
                literal_known_tags = False
            if prompt != "NONE" and f"FORMAL={prompt}" not in literal:
                literal_known_tags = False
            if mnemonic == "UNKNOWN" and prompt == "NONE":
                required_unknown = "EXEMPLAR_VALUE_UNKNOWN" if event["event_template"] == "EXEMPLAR_ONLY" else "EXACT_VALUE_UNKNOWN"
                if required_unknown not in literal:
                    literal_known_tags = False

    gates.append(gate("v69_statement_metadata_exact", source_metadata_ok, "all bound columns"))
    gates.append(gate("all_135_fields_once", output_field_ids == [r["field_id"] for r in fields] and len(set(output_field_ids)) == 135, len(output_field_ids)))
    gates.append(gate("all_381_events_once", output_event_serials == [r["event_serial"] for r in events] and len(set(output_event_serials)) == 381, len(output_event_serials)))
    gates.append(gate("exact_selected_v71_field_bindings", owner_bindings_ok, "135/135 central selections"))
    gates.append(gate("literal_layer_has_every_event", literal_complete, "381 event markers"))
    gates.append(gate("literal_known_and_unknown_tags", literal_known_tags, "frozen mnemonic/prompt or explicit unknown"))
    gates.append(gate("line_crossing_exact", line_crossing_ok, sum(r["line_crossing"].startswith("YES:") for r in rows)))
    gates.append(gate("repair_cost_range", all(r["repair_cost_0_4"] in {"0", "1", "2", "3", "4"} for r in rows), dict(Counter(r["repair_cost_0_4"] for r in rows))))
    gates.append(gate("one_concrete_paraphrase_each", all(r["statement_id"] in r["technical_source_class_paraphrase"] for r in rows), "116 statement-addressed paraphrases"))
    gates.append(gate("one_typed_rival_each", all(r["strongest_medical_or_formal_rival"].startswith(("MEDICAL_RIVAL:", "FORMAL_RIVAL:")) and " || " not in r["strongest_medical_or_formal_rival"] for r in rows), "116 single rivals"))
    gates.append(gate("contradiction_and_constraint_each", all(r["hardest_contradiction"].strip() and r["contact_direction_constraint"].strip() for r in rows), "116/116"))
    gates.append(gate("semantic_ceiling_constant", {r["semantic_ceiling"] for r in rows} == {"CREATIVE_SOURCE_CLASS_NOT_WORD_CARD_STEM_SOUND_OR_TRANSLATION"}, sorted({r["semantic_ceiling"] for r in rows})))
    gates.append(gate("fixed_pages_only", {r["page"] for r in rows} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}, sorted({r["page"] for r in rows})))
    gates.append(gate("sealed_pages_absent", not any(r["page"].startswith("f84") for r in rows), "no f84/f84r selector"))

    critical = {r["statement_id"]: r for r in rows}
    gates.append(gate("b2_s012_gap_reset", "F058=UNRESOLVED:B2_MIDDLE_RIGHT_AMBIGUOUS_STATION" in critical["B2-S012"]["v71_field_owner_bindings"] and "BREAK_VISIBLE_GAP" in critical["B2-S012"]["exact_v71_owner_transition"] and critical["B2-S012"]["repair_cost_0_4"] == "4", critical["B2-S012"]["exact_v71_owner_transition"]))
    gates.append(gate("b3_s016_gap_reset", "BREAK_VISIBLE_GAP" in critical["B3-S016"]["exact_v71_owner_transition"] and critical["B3-S016"]["repair_cost_0_4"] == "4", critical["B3-S016"]["exact_v71_owner_transition"]))
    gates.append(gate("b3_s026_gap_reset", "BREAK_VISIBLE_GAP" in critical["B3-S026"]["exact_v71_owner_transition"] and critical["B3-S026"]["repair_cost_0_4"] == "4", critical["B3-S026"]["exact_v71_owner_transition"]))
    gates.append(gate("b4_s015_left_right_reset", "B4_MAIN_LEFT_OPEN_FRINGE_STATION" in critical["B4-S015"]["v71_field_owner_bindings"] and "B4_MAIN_RIGHT_S_RUN_MULTIPORT_STATION" in critical["B4-S015"]["v71_field_owner_bindings"] and "BREAK_VISIBLE_GAP" in critical["B4-S015"]["exact_v71_owner_transition"], critical["B4-S015"]["exact_v71_owner_transition"]))
    gates.append(gate("b5_b6_record_reset", "RESET_AT_RECORD_END" in critical["B5-S003"]["exact_v71_owner_transition"] and critical["B6-S001"]["exact_v71_owner_transition"].startswith("RESET_RECORD"), {"B5": critical["B5-S003"]["exact_v71_owner_transition"], "B6": critical["B6-S001"]["exact_v71_owner_transition"]}))
    gates.append(gate("all_bio_constraints_block_direction", all("NO_" in r["contact_direction_constraint"] for r in rows if r["record_unit_id"].startswith("B")), "97 Biological statements"))

    report_records = all(f"### {record} —" in report for record in ("H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"))
    gates.append(gate("report_all_11_records", report_records, "H1-H5+B1-B6"))
    gates.append(gate("report_all_116_statement_ids", all(r["statement_id"] in report for r in rows), "116/116"))
    gates.append(gate("revision_table_15_rows", len(revisions) == 15, len(revisions)))

    passed = all(g["status"] == "PASS" for g in gates)
    payload = {
        "status": "PASS" if passed else "FAIL",
        "gate_count": len(gates),
        "passed_gates": sum(g["status"] == "PASS" for g in gates),
        "statements": len(rows),
        "fields": len(output_field_ids),
        "events": len(output_event_serials),
        "repair_cost_counts": dict(sorted(Counter(r["repair_cost_0_4"] for r in rows).items())),
        "gates": gates,
        "sealed": ["f84", "f84r"],
    }
    VALIDATION.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
