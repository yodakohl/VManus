#!/usr/bin/env python3
"""Independent count and license validator for the R1 V63 slot grammar."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent
ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}
TEMPLATES = {
    "PARAMETER_ASSIGNMENT",
    "TARGET_ASSIGNMENT",
    "RELATION_LINK",
    "STATE_CHECK_GATE",
    "ACTION",
    "TERMINAL_ACTION",
    "SELECTION_REFERENCE",
}
EXPECTED_TEMPLATE_INSTANCES = {
    "PARAMETER_ASSIGNMENT": 29,
    "TARGET_ASSIGNMENT": 16,
    "RELATION_LINK": 19,
    "STATE_CHECK_GATE": 11,
    "ACTION": 17,
    "TERMINAL_ACTION": 16,
    "SELECTION_REFERENCE": 18,
}


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def check(condition: bool, label: str, checks: list[dict[str, object]], detail: object) -> None:
    checks.append({"check": label, "pass": bool(condition), "detail": detail})


def main() -> None:
    templates = read_tsv("V63_R1_TEMPLATE_INVENTORY.tsv")
    channels = read_tsv("V63_R1_LICENSED_CHANNELS.tsv")
    statements = read_tsv("V63_R1_116_STATEMENT_TEMPLATE_MAP.tsv")
    fields = read_tsv("V63_R1_135_FIELD_TEMPLATE_MAP.tsv")
    examples = read_tsv("V63_R1_EXECUTABLE_EXAMPLES.tsv")
    report_path = OUT / "V63_R1_SLOT_GRAMMAR_REPORT.md"

    checks: list[dict[str, object]] = []
    check(len(templates) == 7, "template_row_count", checks, len(templates))
    check({row["template_id"] for row in templates} == TEMPLATES, "template_inventory_exact", checks, sorted(row["template_id"] for row in templates))
    check(len(channels) == 19, "licensed_channel_inventory_rows", checks, len(channels))
    check(sum(row["channel_kind"] == "EXACT_CARD_MNEMONIC" for row in channels) == 11, "exact_channel_count", checks, 11)
    check(sum(row["channel_kind"] == "FORMAL_OPERATION" for row in channels) == 4, "formal_channel_count", checks, 4)
    check(sum(row["channel_kind"] == "ANONYMOUS_REGISTER" for row in channels) == 4, "register_channel_count", checks, 4)
    check(
        all(row["anchor_permission"] == "NO" for row in channels if row["channel_kind"] == "ANONYMOUS_REGISTER"),
        "registers_never_license_templates",
        checks,
        [row["channel_id"] for row in channels if row["channel_kind"] == "ANONYMOUS_REGISTER"],
    )
    check(
        sum(int(row["event_occurrence_count"]) for row in channels if row["channel_kind"] == "EXACT_CARD_MNEMONIC") == 85,
        "exact_anchor_occurrences",
        checks,
        85,
    )
    check(
        sum(int(row["event_occurrence_count"]) for row in channels if row["channel_kind"] == "FORMAL_OPERATION") == 41,
        "formal_anchor_occurrences",
        checks,
        41,
    )

    check(len(statements) == 116, "statement_map_rows", checks, len(statements))
    check(len({row["statement_id"] for row in statements}) == 116, "statement_ids_unique", checks, len({row["statement_id"] for row in statements}))
    check({row["page"] for row in statements} == ALLOWED_PAGES, "statement_pages_exact", checks, sorted({row["page"] for row in statements}))
    check(sum(int(row["event_count"]) for row in statements) == 381, "statement_event_partition", checks, sum(int(row["event_count"]) for row in statements))
    check(sum(int(row["licensed_anchor_event_count"]) for row in statements) == 126, "statement_anchor_partition", checks, sum(int(row["licensed_anchor_event_count"]) for row in statements))
    check(sum(int(row["unlicensed_exemplar_event_count"]) for row in statements) == 255, "statement_exemplar_partition", checks, sum(int(row["unlicensed_exemplar_event_count"]) for row in statements))
    statement_status = Counter(row["mapping_status"] for row in statements)
    check(statement_status == {"TEMPLATE_ANCHORED_NO_TOTAL_PARSE": 64, "EXEMPLAR_ONLY": 52}, "statement_mapping_status_counts", checks, dict(statement_status))
    check(
        all((row["template_sequence"] == "EXEMPLAR_ONLY") == (row["mapping_status"] == "EXEMPLAR_ONLY") for row in statements),
        "statement_null_mapping_consistent",
        checks,
        "all rows",
    )
    check(
        sum(row["all_events_channel_anchored"] == "YES_BUT_NOT_A_TOTAL_PARSE" for row in statements) == 12,
        "fully_anchored_statements_still_not_total_parse",
        checks,
        12,
    )

    check(len(fields) == 135, "field_map_rows", checks, len(fields))
    check(len({row["field_id"] for row in fields}) == 135, "field_ids_unique", checks, len({row["field_id"] for row in fields}))
    check({row["page"] for row in fields} == ALLOWED_PAGES, "field_pages_exact", checks, sorted({row["page"] for row in fields}))
    check(sum(int(row["event_count"]) for row in fields) == 381, "field_event_partition", checks, sum(int(row["event_count"]) for row in fields))
    check(sum(int(row["licensed_anchor_event_count"]) for row in fields) == 126, "field_anchor_partition", checks, sum(int(row["licensed_anchor_event_count"]) for row in fields))
    check(sum(int(row["unlicensed_exemplar_event_count"]) for row in fields) == 255, "field_exemplar_partition", checks, sum(int(row["unlicensed_exemplar_event_count"]) for row in fields))
    field_status = Counter(row["mapping_status"] for row in fields)
    check(field_status == {"TEMPLATE_ANCHORED_NO_TOTAL_PARSE": 74, "EXEMPLAR_ONLY": 61}, "field_mapping_status_counts", checks, dict(field_status))
    check(
        all(row["statement_id"] in {statement["statement_id"] for statement in statements} for row in fields),
        "every_field_maps_to_statement",
        checks,
        "135/135",
    )
    check(
        sum(row["all_events_channel_anchored"] == "YES_BUT_NOT_A_TOTAL_PARSE" for row in fields) == 14,
        "fully_anchored_fields_still_not_total_parse",
        checks,
        14,
    )

    instance_counts: Counter[str] = Counter()
    for row in statements:
        if row["template_sequence"] == "EXEMPLAR_ONLY":
            continue
        for item in row["template_sequence"].split(" | "):
            _, template = item.split(":", 1)
            instance_counts[template] += 1
    check(dict(instance_counts) == EXPECTED_TEMPLATE_INSTANCES, "template_instance_counts", checks, dict(instance_counts))

    check(len(examples) == 15, "executable_example_rows", checks, len(examples))
    check({row["template_id"] for row in examples} == TEMPLATES, "every_template_has_example", checks, sorted({row["template_id"] for row in examples}))
    check(sum(row["anchor_channel"].startswith("EXACT:") for row in examples) == 11, "all_exact_anchor_classes_exemplified", checks, 11)
    check(sum(row["anchor_channel"].startswith("FORMAL:") for row in examples) == 4, "all_formal_anchor_classes_exemplified", checks, 4)
    check(all("local expansion is an exemplar" in row["separation_rule"] for row in examples), "example_level_separation_explicit", checks, "15/15")

    artifact_paths = [
        OUT / "V63_R1_TEMPLATE_INVENTORY.tsv",
        OUT / "V63_R1_LICENSED_CHANNELS.tsv",
        OUT / "V63_R1_116_STATEMENT_TEMPLATE_MAP.tsv",
        OUT / "V63_R1_135_FIELD_TEMPLATE_MAP.tsv",
        OUT / "V63_R1_EXECUTABLE_EXAMPLES.tsv",
        report_path,
        OUT / "V63_R1_BUILD_SUMMARY.json",
    ]
    all_text = "\n".join(path.read_text(encoding="utf-8") for path in artifact_paths)
    page_tokens = set(re.findall(r"\bf\d+[rv]\d?\b", all_text))
    check(page_tokens <= ALLOWED_PAGES, "no_out_of_scope_page_tokens", checks, sorted(page_tokens))
    local_home_marker = "/" + "home" + "/"
    check(local_home_marker not in all_text, "no_absolute_local_paths", checks, "clean")
    check("PAGE_HOST" not in all_text, "no_host_semantics_token", checks, "clean")
    check("surface" not in "\t".join(statements[0]) and "surface" not in "\t".join(fields[0]), "no_surface_column_in_maps", checks, "clean")

    failed = [item for item in checks if not item["pass"]]
    result = {
        "status": "PASS" if not failed else "FAIL",
        "scope": {
            "pages": 7,
            "records": 11,
            "events": 381,
            "statements": 116,
            "fields": 135,
            "templates": 7,
            "licensed_anchor_events": 126,
            "unlicensed_exemplar_events": 255,
            "template_anchored_statements": 64,
            "exemplar_only_statements": 52,
            "template_anchored_fields": 74,
            "exemplar_only_fields": 61,
            "executable_examples": 15,
        },
        "template_instance_counts": dict(instance_counts),
        "checks": checks,
        "failed_checks": [item["check"] for item in failed],
    }
    (OUT / "V63_R1_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if failed:
        raise SystemExit("validation failed: " + ", ".join(item["check"] for item in failed))
    print(json.dumps(result["scope"], ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
