#!/usr/bin/env python3
"""Independent validator for the R1 V64 five-record Herbal second edition."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r"}
ALLOWED_RECORDS = {"H1", "H2", "H3", "H4", "H5"}
EXPECTED_RECORD_COUNTS = {
    "H1": (2, 2, 14),
    "H2": (3, 3, 24),
    "H3": (4, 4, 17),
    "H4": (4, 4, 18),
    "H5": (6, 7, 27),
}

V53_ARTICLES = ROOT / "experiments/yolo/sidequest_theory_candidates_v53/V53_SELECTED_FIVE_ARTICLES.tsv"
V60_DICTIONARY = ROOT / "experiments/yolo/sidequest_theory_candidates_v60/V60_SELECTED_173_CARD_DICTIONARY.tsv"
V60_EVENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v60/V60_SELECTED_381_EVENT_LEDGER.tsv"
V61_STATEMENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v61/V61_SELECTED_116_SOURCE_STATEMENTS.tsv"
V63_EVENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v63/V63_SELECTED_381_EVENT_TEMPLATE_LEDGER.tsv"
V63_STATEMENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v63/V63_SELECTED_116_STATEMENT_SLOT_PARSE.tsv"
V63_FIELDS = ROOT / "experiments/yolo/sidequest_theory_candidates_v63/V63_SELECTED_135_FIELD_SLOT_PARSE.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def check(condition: bool, label: str, checks: list[dict[str, object]], detail: object) -> None:
    checks.append({"check": label, "pass": bool(condition), "detail": detail})


def split_pipe(value: str) -> list[str]:
    if not value or value == "NONE":
        return []
    return [item.strip() for item in value.split("|") if item.strip()]


def main() -> None:
    events = read_tsv(OUT / "V64_R1_100_EVENT_INTERLINEAR.tsv")
    clauses = read_tsv(OUT / "V64_R1_19_CLAUSE_EDITION.tsv")
    fields = read_tsv(OUT / "V64_R1_20_FIELD_EDITION.tsv")
    records = read_tsv(OUT / "V64_R1_5_RECORD_EDITION.tsv")
    delta = read_tsv(OUT / "V64_R1_DICTIONARY_DELTA.tsv")
    build_summary = json.loads((OUT / "V64_R1_BUILD_SUMMARY.json").read_text(encoding="utf-8"))

    v53 = {row["article_id"]: row for row in read_tsv(V53_ARTICLES)}
    v60_dictionary = read_tsv(V60_DICTIONARY)
    v60_events = {
        int(row["event_serial"]): row
        for row in read_tsv(V60_EVENTS)
        if row["page"] in ALLOWED_PAGES
    }
    v61_statements = {
        row["statement_id"]: row
        for row in read_tsv(V61_STATEMENTS)
        if row["page"] in ALLOWED_PAGES
    }
    v63_events = {
        int(row["event_serial"]): row
        for row in read_tsv(V63_EVENTS)
        if row["page"] in ALLOWED_PAGES
    }
    v63_statements = {
        row["statement_id"]: row
        for row in read_tsv(V63_STATEMENTS)
        if row["page"] in ALLOWED_PAGES
    }
    v63_fields = {
        row["field_id"]: row
        for row in read_tsv(V63_FIELDS)
        if row["page"] in ALLOWED_PAGES
    }

    checks: list[dict[str, object]] = []
    check(len(v60_dictionary) == 173, "selected_dictionary_input_rows", checks, len(v60_dictionary))
    check(len(events) == 100, "event_interlinear_rows", checks, len(events))
    check(len(clauses) == 19, "clause_edition_rows", checks, len(clauses))
    check(len(fields) == 20, "field_edition_rows", checks, len(fields))
    check(len(records) == 5, "record_edition_rows", checks, len(records))
    check(len(delta) == 0, "dictionary_delta_rows_zero", checks, len(delta))

    event_serials = [int(row["event_serial"]) for row in events]
    check(event_serials == list(range(1, 101)), "event_serial_order_and_completeness", checks, f"{event_serials[0]}..{event_serials[-1]}")
    check({row["page"] for row in events} == ALLOWED_PAGES, "event_pages_exact", checks, sorted({row["page"] for row in events}))
    check({row["record_unit_id"] for row in events} == ALLOWED_RECORDS, "event_records_exact", checks, sorted({row["record_unit_id"] for row in events}))
    check(len({row["joint_tuple_id"] + "@" + row["event_serial"] for row in events}) == 100, "event_identity_rows_unique", checks, 100)

    event_copy_fields = [
        ("page", "page"),
        ("locus", "locus"),
        ("record_unit_id", "record_unit_id"),
        ("field_id", "field_id"),
        ("joint_tuple_id", "joint_tuple_id"),
        ("surface_display_only", "surface"),
        ("formal_formula_opaque", "formal_formula_opaque"),
        ("terminal_status", "terminal_status"),
        ("selected_exact_mnemonic_unchanged", "ATOMIC_OR_WHOLE_CARD_MNEMONIC"),
    ]
    copy_mismatches = []
    v63_mismatches = []
    for row in events:
        serial = int(row["event_serial"])
        old = v60_events[serial]
        selected = v63_events[serial]
        for output_column, input_column in event_copy_fields:
            if row[output_column] != old[input_column]:
                copy_mismatches.append(f"E{serial}:{output_column}")
        for output_column, input_column in [
            ("statement_id", "statement_id"),
            ("strict_formal_prompt", "strict_formal_prompt"),
            ("v63_event_template", "event_template"),
            ("v63_event_parse_status", "event_parse_status"),
        ]:
            if row[output_column] != selected[input_column]:
                v63_mismatches.append(f"E{serial}:{output_column}")
    check(not copy_mismatches, "v60_visible_and_card_channels_byte_preserved", checks, copy_mismatches or "100/100")
    check(not v63_mismatches, "v63_event_templates_preserved", checks, v63_mismatches or "100/100")
    check(all(row["v64_local_source_expansion"].strip() for row in events), "every_event_has_local_default", checks, "100/100")
    check(all(row["local_expansion_level"] == "CREATIVE_HERBAL_EXEMPLAR;NOT_CARD_VALUE" for row in events), "every_event_expansion_separated", checks, "100/100")

    raw_event_status = Counter(row["v63_event_parse_status"] for row in events)
    support_event_status = Counter(row["v64_support_class"] for row in events)
    check(
        raw_event_status == {
            "UNPARSED_EXEMPLAR": 71,
            "UNIQUE_EXACT": 18,
            "UNIQUE_CONVERGENT_CHANNELS": 6,
            "UNIQUE_FORMAL_ONLY": 5,
        },
        "selected_event_status_counts",
        checks,
        dict(raw_event_status),
    )
    check(
        support_event_status == {"EXEMPLAR_ONLY": 71, "UNIQUE_EVENT_TEMPLATE;LOCAL_WORDING_AMBIGUOUS": 29},
        "event_support_class_counts",
        checks,
        dict(support_event_status),
    )

    clause_status = Counter(row["v64_support_class"] for row in clauses)
    field_status = Counter(row["v64_support_class"] for row in fields)
    check(clause_status == {"AMBIGUOUS": 14, "EXEMPLAR_ONLY": 5}, "clause_status_counts", checks, dict(clause_status))
    check(field_status == {"AMBIGUOUS": 15, "EXEMPLAR_ONLY": 5}, "field_status_counts", checks, dict(field_status))
    check(all(row["v64_support_class"] != "UNIQUE" for row in clauses), "no_unique_herbal_clause", checks, "0/19 UNIQUE")
    check(all(row["v64_support_class"] != "UNIQUE" for row in fields), "no_unique_herbal_field", checks, "0/20 UNIQUE")

    clause_mismatches = []
    clause_event_serials: list[int] = []
    for row in clauses:
        source = v61_statements[row["statement_id"]]
        selected = v63_statements[row["statement_id"]]
        for column in ["record_unit_id", "page", "constituent_loci", "constituent_fields", "event_count", "event_serials", "entry_boundary_class", "exit_boundary_class", "internal_cross_line_boundaries"]:
            if row[column] != source[column]:
                clause_mismatches.append(f"{row['statement_id']}:{column}")
        if row["v63_parse_status"] != selected["parse_status"]:
            clause_mismatches.append(f"{row['statement_id']}:v63_parse_status")
        clause_event_serials.extend(int(value) for value in split_pipe(row["event_serials"]))
    check(not clause_mismatches, "v61_clause_map_and_v63_status_preserved", checks, clause_mismatches or "19/19")
    check(sorted(clause_event_serials) == list(range(1, 101)), "clauses_partition_100_events", checks, len(clause_event_serials))
    h5s1 = next(row for row in clauses if row["statement_id"] == "H5-S001")
    check(
        h5s1["constituent_fields"] == "F014|F015" and h5s1["internal_cross_line_boundaries"] == "H5-LB01",
        "h5_cross_line_clause_preserved",
        checks,
        f"{h5s1['constituent_fields']}:{h5s1['internal_cross_line_boundaries']}",
    )

    field_mismatches = []
    field_event_serials: list[int] = []
    for row in fields:
        selected = v63_fields[row["field_id"]]
        for column in ["record_unit_id", "page", "locus", "statement_id", "field_position_in_statement", "event_count", "event_serials", "primary_template", "licensed_primitive_sequence"]:
            if row[column] != selected[column]:
                field_mismatches.append(f"{row['field_id']}:{column}")
        if row["v63_parse_status"] != selected["parse_status"]:
            field_mismatches.append(f"{row['field_id']}:v63_parse_status")
        field_event_serials.extend(int(value) for value in split_pipe(row["event_serials"]))
    check(not field_mismatches, "v63_field_map_preserved", checks, field_mismatches or "20/20")
    check(sorted(field_event_serials) == list(range(1, 101)), "fields_partition_100_events", checks, len(field_event_serials))
    f14 = next(row for row in fields if row["field_id"] == "F014")
    f15 = next(row for row in fields if row["field_id"] == "F015")
    check("CONTINUES" in f14["continuation_role"] and "RESUMES" in f15["continuation_role"], "field_level_cross_line_marking", checks, f"{f14['continuation_role']}|{f15['continuation_role']}")

    record_mismatches = []
    for row in records:
        record = row["record_unit_id"]
        statement_count, field_count, event_count = EXPECTED_RECORD_COUNTS[record]
        if (int(row["clause_count"]), int(row["field_count"]), int(row["event_count"])) != (statement_count, field_count, event_count):
            record_mismatches.append(f"{record}:counts")
        if row["v53_visual_owner_freeze"] != v53[record]["pictured_owner_default"]:
            record_mismatches.append(f"{record}:visual_owner")
        if row["v53_visual_owner_rival_freeze"] != v53[record]["pictured_owner_rival"]:
            record_mismatches.append(f"{record}:visual_rival")
        required_nonempty = [
            "pictured_owner_description",
            "proposed_article_genre",
            "complete_second_edition_german",
            "strongest_alternative_plant_identity",
            "strongest_nonmedical_procedure_reading",
            "exact_unsupported_nouns",
            "revisions_from_v59_v53",
            "strongest_contradiction",
            "apprentice_writing_reading_steps",
        ]
        for column in required_nonempty:
            if not row[column].strip():
                record_mismatches.append(f"{record}:{column}")
        if row["dictionary_decision"] != "NO_CHANGE_TO_V60_CARD_VALUES":
            record_mismatches.append(f"{record}:dictionary_decision")
    check(not record_mismatches, "five_record_required_content_and_counts", checks, record_mismatches or "5/5")

    check(build_summary["dictionary_delta_rows"] == 0, "build_summary_zero_dictionary_delta", checks, build_summary["dictionary_delta_rows"])
    dictionary_hash = hashlib.sha256(V60_DICTIONARY.read_bytes()).hexdigest()
    check(build_summary["v60_dictionary_sha256"] == dictionary_hash, "v60_dictionary_hash_recorded", checks, dictionary_hash)

    artifact_paths = [
        OUT / "V64_R1_100_EVENT_INTERLINEAR.tsv",
        OUT / "V64_R1_19_CLAUSE_EDITION.tsv",
        OUT / "V64_R1_20_FIELD_EDITION.tsv",
        OUT / "V64_R1_5_RECORD_EDITION.tsv",
        OUT / "V64_R1_DICTIONARY_DELTA.tsv",
        OUT / "V64_R1_HERBAL_SECOND_EDITION_REPORT.md",
        OUT / "V64_R1_BUILD_SUMMARY.json",
    ]
    all_text = "\n".join(path.read_text(encoding="utf-8") for path in artifact_paths)
    page_tokens = set(re.findall(r"\bf\d+[rv]\d?\b", all_text))
    check(page_tokens <= ALLOWED_PAGES, "no_out_of_scope_page_tokens", checks, sorted(page_tokens))
    local_home_prefix = "/" + "home" + "/"
    check(local_home_prefix not in all_text, "no_absolute_local_paths", checks, "clean")
    check("PAGE_HOST" not in all_text, "no_host_semantics_token", checks, "clean")

    failed = [item for item in checks if not item["pass"]]
    result = {
        "status": "PASS" if not failed else "FAIL",
        "scope": {
            "pages": 4,
            "records": 5,
            "clauses": 19,
            "fields": 20,
            "events": 100,
            "recognized_events": 29,
            "exemplar_only_events": 71,
            "unique_clauses": 0,
            "ambiguous_clauses": 14,
            "exemplar_only_clauses": 5,
            "unique_fields": 0,
            "ambiguous_fields": 15,
            "exemplar_only_fields": 5,
            "dictionary_delta_rows": 0,
        },
        "event_status_counts": dict(raw_event_status),
        "checks": checks,
        "failed_checks": [item["check"] for item in failed],
    }
    (OUT / "V64_R1_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if failed:
        raise SystemExit("validation failed: " + ", ".join(item["check"] for item in failed))
    print(json.dumps(result["scope"], ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
