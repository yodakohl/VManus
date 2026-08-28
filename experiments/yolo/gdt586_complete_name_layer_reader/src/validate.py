#!/usr/bin/env python3
"""Validate GDT586 artifacts and the running/local separation contract."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt586_complete_name_layer_reader"
OUT = BASE / "artifacts"
G582 = ROOT / "experiments/yolo/gdt582_concrete_stem_default_fill/artifacts"
G584 = ROOT / "experiments/yolo/gdt584_statement_collocation_polish/artifacts"
G585 = ROOT / "experiments/yolo/gdt585_learned_name_compound_atlas/artifacts"

INPUTS = {
    "complete_defaults": G582 / "gdt582_15889_complete_default_ledger.tsv",
    "statements_582": G582 / "gdt582_793_concrete_statement_edition.tsv",
    "local_cards_582": G582 / "gdt582_744_concrete_local_card_edition.tsv",
    "statements_584": G584 / "gdt584_591_polished_statement_edition.tsv",
    "local_cards_584": G584 / "gdt584_158_polished_local_card_edition.tsv",
    "assignments_585": G585 / "gdt585_109_owner_content_slot_assignments.tsv",
    "labels_585": G585 / "gdt585_89_concrete_name_label_edition.tsv",
    "groups_585": G585 / "gdt585_19_compound_and_pair_readings.tsv",
}

OUTPUTS = {
    "injections": OUT / "gdt586_109_exact_name_injections.tsv",
    "statements": OUT / "gdt586_793_complete_statement_reader.tsv",
    "local_cards": OUT / "gdt586_744_complete_local_card_reader.tsv",
    "groups": OUT / "gdt586_19_full_context_group_readings.tsv",
    "pages": OUT / "gdt586_30_page_reader_profiles.tsv",
    "book": OUT / "GDT586_COMPLETE_THIRTY_PAGE_READER.md",
    "manual_audit": OUT / "GDT586_MANUAL_CONTEXT_AUDIT.md",
    "result": OUT / "gdt586_result.json",
}

STATUS = (
    "PASS_109_EXACT_NAME_OVERRIDES__793_RUNNING_STATEMENTS__744_LOCAL_CARDS__"
    "107_LOCAL_NAMES_PLUS_2_LOCAL_X__19_CONTEXT_REREADINGS__"
    "SOURCE_ORDER_AND_STAR_RIVAL_REPAIRS"
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    source = {name: read_tsv(path) for name, path in INPUTS.items()}
    rows = {
        name: read_tsv(path)
        for name, path in OUTPUTS.items()
        if path.suffix == ".tsv"
    }
    result = json.loads(OUTPUTS["result"].read_text(encoding="utf-8"))
    book = OUTPUTS["book"].read_text(encoding="utf-8")
    manual = OUTPUTS["manual_audit"].read_text(encoding="utf-8")
    checks: list[dict[str, Any]] = []

    def check(check_id: str, condition: bool, detail: str) -> None:
        checks.append(
            {
                "check_ordinal": len(checks) + 1,
                "check_id": check_id,
                "status": "PASS" if condition else "FAIL",
                "detail": detail,
            }
        )

    injections = rows["injections"]
    statements = rows["statements"]
    local = rows["local_cards"]
    groups = rows["groups"]
    pages = rows["pages"]
    complete_by_slot = {row["slot_id"]: row for row in source["complete_defaults"]}
    assignment_by_slot = {row["slot_id"]: row for row in source["assignments_585"]}
    statement_582 = {row["statement_id"]: row for row in source["statements_582"]}
    statement_584 = {row["statement_id"]: row for row in source["statements_584"]}
    local_582 = {row["source_event_id"]: row for row in source["local_cards_582"]}
    local_584 = {row["source_event_id"]: row for row in source["local_cards_584"]}
    labels_585 = {row["source_event_id"]: row for row in source["labels_585"]}
    statement_by_id = {row["statement_id"]: row for row in statements}
    local_by_event = {row["source_event_id"]: row for row in local}
    group_by_id = {row["compound_id"]: row for row in groups}

    check("RESULT_STATUS", result["status"] == STATUS, result["status"])
    check("INJECTION_COUNT", len(injections) == 109, str(len(injections)))
    check("STATEMENT_COUNT", len(statements) == 793, str(len(statements)))
    check("LOCAL_CARD_COUNT", len(local) == 744, str(len(local)))
    check("GROUP_COUNT", len(groups) == 19, str(len(groups)))
    check("PAGE_COUNT", len(pages) == 30, str(len(pages)))
    check(
        "COMPLETE_READER_UNIT_COUNT",
        len(statements) + len(local) == 1537,
        str(len(statements) + len(local)),
    )
    check(
        "INPUT_HASHES",
        result["input_sha256"] == {name: sha256(path) for name, path in INPUTS.items()},
        "all eight source hashes",
    )
    check(
        "UNIQUE_INJECTION_SLOT_IDS",
        len({row["slot_id"] for row in injections}) == 109,
        "109/109",
    )
    check(
        "INJECTION_SET_EQUALS_GDT585",
        {row["slot_id"] for row in injections} == set(assignment_by_slot),
        "exact slot_id set",
    )
    check(
        "INJECTION_OLD_VALUES_FROM_EXACT_LEDGER",
        all(
            row["gdt582_exact_legacy_default_de"]
            == complete_by_slot[row["slot_id"]]["gdt582_concrete_default_de"]
            for row in injections
        ),
        "109 occurrence-level joins",
    )
    check(
        "INJECTION_NEW_VALUES_FROM_GDT585",
        all(
            row["gdt585_primary_default_de"]
            == assignment_by_slot[row["slot_id"]]["gdt585_primary_default_de"]
            for row in injections
        ),
        "109 occurrence-level joins",
    )
    kind_counts = Counter(row["reader_unit_kind"] for row in injections)
    check("LOCAL_NAME_SLOT_COUNT", kind_counts == {"LOCAL_CARD": 107, "RUNNING_STATEMENT": 2}, str(kind_counts))
    local_host_counts = Counter(
        row["reader_unit_join_key"]
        for row in injections
        if row["reader_unit_kind"] == "LOCAL_CARD"
    )
    check("NAME_BEARING_LOCAL_HOST_COUNT", len(local_host_counts) == 89, str(len(local_host_counts)))
    check(
        "NAME_SLOTS_PER_CARD_PROFILE",
        Counter(local_host_counts.values()) == {1: 72, 2: 16, 3: 1},
        str(Counter(local_host_counts.values())),
    )
    restored = [
        row for row in injections
        if row["legacy_alias_reconciliation"]
        == "RESTORED_EXACT_GDT582_VALUE_WHERE_GDT585_DECLARED_NONE"
    ]
    check("RESTORED_STAR_RIVAL_COUNT", len(restored) == 60, str(len(restored)))
    check(
        "RESTORED_STAR_RIVALS_ARE_EXACT",
        all(
            row["content_class"] == "STAR_BEARING_RING_POSITION"
            and row["gdt585_declared_legacy_alias_de"] == "NONE"
            and row["gdt582_exact_legacy_default_de"].startswith("Sternringstelle ")
            for row in restored
        ),
        "60 exact numbered GDT582 values",
    )
    check(
        "REMAINING_DECLARED_RIVALS_EXACT",
        sum(row["legacy_alias_reconciliation"] == "GDT585_DECLARED_ALIAS_EXACT" for row in injections) == 49,
        "49 exact declared aliases",
    )

    check(
        "STATEMENT_ID_ORDER_RETAINED",
        [row["statement_id"] for row in statements]
        == [row["statement_id"] for row in source["statements_582"]],
        "793 ordered IDs",
    )
    statement_layers = Counter(row["base_reader_source"] for row in statements)
    check(
        "STATEMENT_LAYER_SPLIT",
        statement_layers == {"GDT584_POLISHED_STATEMENT": 591, "GDT582_CONCRETE_STATEMENT": 202},
        str(statement_layers),
    )
    changed_statements = {
        row["statement_id"] for row in statements if int(row["name_override_count"])
    }
    check(
        "EXACT_CHANGED_STATEMENTS",
        changed_statements == {"G515-S046", "G515-S050"},
        "|".join(sorted(changed_statements)),
    )
    check(
        "RUNNING_SLOT_IDS_EXACT",
        statement_by_id["G515-S046"]["name_override_slot_ids"] == "RUNNING:G515-E0410@2"
        and statement_by_id["G515-S050"]["name_override_slot_ids"] == "RUNNING:G515-E0438@2",
        "two exact LOCAL_X slots",
    )
    check(
        "RUNNING_BASE_LAYER_MIX",
        statement_by_id["G515-S046"]["base_reader_source"] == "GDT582_CONCRETE_STATEMENT"
        and statement_by_id["G515-S050"]["base_reader_source"] == "GDT584_POLISHED_STATEMENT",
        "one fallback plus one polished",
    )
    unchanged_statement_count = 0
    changed_statement_ok = True
    for row in statements:
        sid = row["statement_id"]
        base = (
            statement_584[sid]["gdt584_polished_paragraph_de"]
            if sid in statement_584
            else statement_582[sid]["concrete_working_reading_de"]
        )
        if int(row["name_override_count"]):
            old = row["gdt582_legacy_default_sequence"]
            new = row["gdt585_primary_default_sequence"]
            changed_statement_ok &= row["legacy_reader_de"] == base
            changed_statement_ok &= old not in row["gdt586_primary_reader_de"]
            changed_statement_ok &= row["gdt586_primary_reader_de"].count(new) == 1
        else:
            unchanged_statement_count += row["gdt586_primary_reader_de"] == base
    check("UNCHANGED_STATEMENTS_BYTE_EXACT", unchanged_statement_count == 791, str(unchanged_statement_count))
    check("CHANGED_STATEMENT_CHANNELS_EXACT", changed_statement_ok, "legacy and primary channels")

    check(
        "LOCAL_EVENT_ORDER_RETAINED",
        [row["source_event_id"] for row in local]
        == [row["source_event_id"] for row in source["local_cards_582"]],
        "744 ordered IDs",
    )
    local_base_layers = Counter(row["base_reader_source"] for row in local)
    check(
        "LOCAL_BASE_LAYER_SPLIT",
        local_base_layers == {"GDT584_POLISHED_LOCAL_CARD": 158, "GDT582_CONCRETE_LOCAL_CARD": 586},
        str(local_base_layers),
    )
    local_primary_layers = Counter(row["primary_reader_source"] for row in local)
    check(
        "LOCAL_PRIMARY_LAYER_SPLIT",
        local_primary_layers
        == {
            "GDT585_GRAMMAR_AWARE_NAME_LABEL": 89,
            "GDT584_POLISHED_LOCAL_CARD": 148,
            "GDT582_CONCRETE_LOCAL_CARD": 507,
        },
        str(local_primary_layers),
    )
    name_card_ids = {
        row["source_event_id"] for row in local if int(row["name_override_count"])
    }
    check("NAME_CARD_SET_EQUALS_GDT585_LABELS", name_card_ids == set(labels_585), "89 exact event IDs")
    name_base_layers = Counter(local_by_event[event_id]["base_reader_source"] for event_id in name_card_ids)
    check(
        "NAME_CARD_BASE_SPLIT",
        name_base_layers == {"GDT582_CONCRETE_LOCAL_CARD": 79, "GDT584_POLISHED_LOCAL_CARD": 10},
        str(name_base_layers),
    )
    unchanged_local_count = 0
    named_local_ok = True
    for row in local:
        event_id = row["source_event_id"]
        base = (
            local_584[event_id]["gdt584_polished_local_clause_de"]
            if event_id in local_584
            else local_582[event_id]["concrete_working_clause_de"]
        )
        if int(row["name_override_count"]):
            named_local_ok &= row["legacy_reader_de"] == base
            named_local_ok &= row["gdt586_primary_reader_de"] == labels_585[event_id]["gdt585_primary_reading_de"]
        else:
            unchanged_local_count += row["gdt586_primary_reader_de"] == base
    check("UNCHANGED_LOCAL_CARDS_BYTE_EXACT", unchanged_local_count == 655, str(unchanged_local_count))
    check("NAMED_LOCAL_CHANNELS_EXACT", named_local_ok, "89 specialized primary plus legacy base")
    check(
        "LOCAL_RUNNING_LINKS_ALL_FORBIDDEN",
        all(row["running_statement_link_status"].startswith("NONE__") for row in local),
        "744/744",
    )
    running_event_ids = {
        event_id
        for row in source["statements_582"]
        for event_id in row["event_ids"].split("|")
    }
    check(
        "LOCAL_NAME_EVENTS_DISJOINT_FROM_RUNNING_EVENTS",
        not (name_card_ids & running_event_ids),
        "0 intersections",
    )

    check(
        "GROUP_ID_SET_RETAINED",
        set(group_by_id) == {row["compound_id"] for row in source["groups_585"]},
        "19 exact IDs",
    )
    group_source_events = {
        event_id for row in source["groups_585"] for event_id in row["source_event_ids"].split("|")
    }
    check("GROUP_SOURCE_EVENT_COUNT", len(group_source_events) == 21, str(len(group_source_events)))
    check(
        "GROUP_EVENTS_ALL_LOCAL",
        group_source_events <= set(local_by_event) and not (group_source_events & running_event_ids),
        "21 local, 0 running",
    )
    group_slot_count = sum(
        len(row["gdt585_primary_default_sequence"].split("|")) for row in groups
    )
    check("GROUP_NAME_SLOT_COUNT", group_slot_count == 39, str(group_slot_count))
    check(
        "GROUP_EXACT_LEGACY_VALUES_NONEMPTY",
        all(
            all(value != "NONE" for value in row["gdt582_exact_legacy_default_sequence"].split("|"))
            for row in groups
        ),
        "39/39 exact GDT582 values",
    )
    check(
        "GROUP_RUNNING_LINKS_NONE",
        all(row["running_statement_ids"] == "NONE" for row in groups),
        "19/19",
    )
    c001 = group_by_id["GDT585-C001"]
    check(
        "C001_SOURCE_ORDER_REPAIR",
        c001["declared_event_ids"] == "P1003-E0080|P1003-E0079"
        and c001["source_order_event_ids"] == "P1003-E0079|P1003-E0080"
        and c001["source_order_status"] == "GDT585_VISUAL_ORDER_DIFFERS__SOURCE_ORDER_RESTORED",
        c001["source_order_event_ids"],
    )
    check(
        "C001_GRAMMAR_BEGINS_WITH_SOURCE_FIRST",
        c001["source_order_grammar_primary_de"].startswith("Pflanzenname »rechte Blütenform"),
        "right form with OT before left form",
    )
    c007 = group_by_id["GDT585-C007"]
    check(
        "C007_FULL_RECORD_CONTEXT",
        c007["context_event_ids"]
        == "P1008-E0421|P1008-E0422|P1008-E0423|P1008-E0424"
        and c007["context_bundle_ids"] == "G474-B081|G474-B082|G474-B083",
        c007["context_event_ids"],
    )
    c010 = group_by_id["GDT585-C010"]
    check(
        "C010_FULL_RECORD_CONTEXT",
        c010["context_event_ids"] == "P1003-E0081|P1003-E0082"
        and c010["context_bundle_ids"] == "G474-B091|G474-B092",
        c010["context_event_ids"],
    )
    c019 = group_by_id["GDT585-C019"]
    check(
        "C019_INTERVENING_RECORD_VISIBLE",
        c019["source_record_ids"] == "G475-R129|G475-R131"
        and c019["context_record_ids"] == "G475-R129|G475-R130|G475-R131"
        and c019["intervening_event_ids"] == "P1008-E1408",
        c019["context_record_ids"],
    )
    check(
        "C019_VISUAL_ONLY_DISPOSITION",
        c019["gdt586_disposition"] == "VISUAL_PAIR_ONLY__TEXTUAL_COMPOUND_REJECTED",
        c019["gdt586_disposition"],
    )
    check(
        "C017_GRAMMAR_DOMINATES",
        group_by_id["GDT585-C017"]["context_effect"] == "GRAMMAR_DOMINATES",
        group_by_id["GDT585-C017"]["gdt586_disposition"],
    )
    check(
        "ONE_SOURCE_ORDER_REPAIR",
        sum(row["source_order_status"] == "GDT585_VISUAL_ORDER_DIFFERS__SOURCE_ORDER_RESTORED" for row in groups) == 1,
        "C001 only",
    )
    check(
        "ONE_VISUAL_ONLY_GROUP",
        sum(row["gdt586_disposition"] == "VISUAL_PAIR_ONLY__TEXTUAL_COMPOUND_REJECTED" for row in groups) == 1,
        "C019 only",
    )

    check(
        "PAGE_PROFILE_TOTALS",
        sum(int(row["running_statement_count"]) for row in pages) == 793
        and sum(int(row["local_card_count"]) for row in pages) == 744
        and sum(int(row["running_name_override_slot_count"]) for row in pages) == 2
        and sum(int(row["local_name_override_slot_count"]) for row in pages) == 107,
        "793+744 units, 2+107 overrides",
    )
    all_page_values = [
        row.get("physical_page", "")
        for table in [injections, statements, local, groups, pages]
        for row in table
    ]
    check(
        "SEALED_PAGES_EXCLUDED",
        all(not value.lower().startswith("f84") for value in all_page_values),
        "no f84/f84r page value",
    )
    check(
        "BOOK_CONTAINS_ALL_STATEMENTS",
        sum(1 for row in statements if f"#### {row['statement_id']}\n" in book) == 793,
        "793 headings",
    )
    check(
        "BOOK_CONTAINS_ALL_LOCAL_CARDS",
        sum(1 for row in local if f"#### {row['source_event_id']} — " in book) == 744,
        "744 headings",
    )
    check(
        "MANUAL_AUDIT_NAMES_REPAIRS",
        "C001" in manual and "C019" in manual and "60 Sternslots" in manual,
        "order, visual pair, star rivals",
    )
    check(
        "RESULT_COUNTS_MATCH",
        result["complete_reader_units"] == 1537
        and result["exact_name_overrides"] == 109
        and result["restored_exact_star_legacy_values"] == 60
        and result["group_name_slots"] == 39,
        "result summary",
    )

    failures = [row for row in checks if row["status"] != "PASS"]
    validation = {
        "experiment_id": "GDT586",
        "status": "PASS" if not failures else "FAIL",
        "check_count": len(checks),
        "passed_checks": len(checks) - len(failures),
        "failed_checks": len(failures),
        "checks": checks,
        "output_sha256": {name: sha256(path) for name, path in OUTPUTS.items()},
    }
    (OUT / "gdt586_validation.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
