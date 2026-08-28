#!/usr/bin/env python3
"""Validate GDT587 exact carrier projection, packet reader, and full editions."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt587_action_conditioned_carrier_nouns"
OUT = BASE / "artifacts"
G582 = ROOT / "experiments/yolo/gdt582_concrete_stem_default_fill/artifacts"
G584 = ROOT / "experiments/yolo/gdt584_statement_collocation_polish/artifacts"
G585 = ROOT / "experiments/yolo/gdt585_learned_name_compound_atlas/artifacts"
G586 = ROOT / "experiments/yolo/gdt586_complete_name_layer_reader/artifacts"

INPUTS = {
    "complete_defaults": G582 / "gdt582_15889_complete_default_ledger.tsv",
    "statements_582": G582 / "gdt582_793_concrete_statement_edition.tsv",
    "local_cards_582": G582 / "gdt582_744_concrete_local_card_edition.tsv",
    "action_revisions_584": G584 / "gdt584_target_occurrence_revisions.tsv",
    "hosts_584": G584 / "gdt584_statement_wide_host_phrases.tsv",
    "statements_584": G584 / "gdt584_591_polished_statement_edition.tsv",
    "local_cards_584": G584 / "gdt584_158_polished_local_card_edition.tsv",
    "name_assignments_585": G585 / "gdt585_109_owner_content_slot_assignments.tsv",
    "name_labels_585": G585 / "gdt585_89_concrete_name_label_edition.tsv",
    "statements_586": G586 / "gdt586_793_complete_statement_reader.tsv",
    "local_cards_586": G586 / "gdt586_744_complete_local_card_reader.tsv",
}

OUTPUTS = {
    "assignments": OUT / "gdt587_1243_action_conditioned_carrier_assignments.tsv",
    "cells": OUT / "gdt587_136_observed_action_root_cells.tsv",
    "hosts": OUT / "gdt587_candidate_statement_host_phrases.tsv",
    "candidate_statements": OUT / "gdt587_379_candidate_statement_edition.tsv",
    "candidate_local": OUT / "gdt587_70_candidate_local_card_edition.tsv",
    "statements": OUT / "gdt587_793_complete_statement_reader.tsv",
    "local_cards": OUT / "gdt587_744_complete_local_card_reader.tsv",
    "pages": OUT / "gdt587_30_page_reader_profiles.tsv",
    "manual": OUT / "gdt587_25_manual_passage_audit.tsv",
    "book": OUT / "GDT587_COMPLETE_THIRTY_PAGE_READER.md",
    "manual_book": OUT / "GDT587_MANUAL_PASSAGE_AUDIT.md",
    "result": OUT / "gdt587_result.json",
}

STATUS = (
    "PASS_1243_ACTION_CONDITIONED_CARRIERS__953_EXACT_ACTION_HOSTS__"
    "136_OBSERVED_ACTION_ROOT_CELLS__793_STATEMENTS__744_LOCAL_CARDS__"
    "ZERO_GLOBAL_ROOT_CHANGE"
)
ROOTS = {"Y", "AIIN", "AIN", "OR"}
CORE = {"Y": "POSTEN", "AIIN": "WERT", "AIN": "ANTEIL", "OR": "EINHEIT"}
AUDIT_IDS = {
    "G407-S003", "G515-S037", "G515-S048", "G515-S059",
    "G407-S696", "G407-S689", "G407-S688", "G407-S699",
    "G407-S047", "G407-S045", "G407-S058", "G407-S061",
    "G407-S151", "G407-S440", "G407-S621", "G407-S384",
    "G407-S663", "G407-S664", "G407-S667", "G407-S666",
    "G407-S572", "G407-S115", "G407-S526", "G407-S001", "G407-S653",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def trace_ids(text: str) -> list[str]:
    return re.findall(r"\[([^=\]]+)=", text)


def main() -> int:
    source = {name: read_tsv(path) for name, path in INPUTS.items()}
    rows = {
        name: read_tsv(path)
        for name, path in OUTPUTS.items()
        if path.suffix == ".tsv"
    }
    result = json.loads(OUTPUTS["result"].read_text(encoding="utf-8"))
    book = OUTPUTS["book"].read_text(encoding="utf-8")
    manual_book = OUTPUTS["manual_book"].read_text(encoding="utf-8")
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

    assignments = rows["assignments"]
    cells = rows["cells"]
    hosts = rows["hosts"]
    candidate_statements = rows["candidate_statements"]
    candidate_local = rows["candidate_local"]
    statements = rows["statements"]
    local = rows["local_cards"]
    pages = rows["pages"]
    manual = rows["manual"]

    complete_by_slot = {row["slot_id"]: row for row in source["complete_defaults"]}
    action_by_key = {row["primary_governor_key"]: row for row in source["action_revisions_584"]}
    names_by_slot = {row["slot_id"]: row for row in source["name_assignments_585"]}
    old_statement_584 = {row["statement_id"]: row for row in source["statements_584"]}
    old_local_584 = {row["source_event_id"]: row for row in source["local_cards_584"]}
    old_statement_586 = {row["statement_id"]: row for row in source["statements_586"]}
    old_local_586 = {row["source_event_id"]: row for row in source["local_cards_586"]}
    statement_582 = {row["statement_id"]: row for row in source["statements_582"]}
    candidate_statement_by_id = {row["statement_id"]: row for row in candidate_statements}
    candidate_local_by_id = {row["source_event_id"]: row for row in candidate_local}
    statement_by_id = {row["statement_id"]: row for row in statements}
    local_by_id = {row["source_event_id"]: row for row in local}

    exact_candidates = {
        row["slot_id"] for row in source["complete_defaults"]
        if row["slot_value"] in ROOTS and row["primary_governor_key"] in action_by_key
    }
    assignment_ids = {row["carrier_slot_id"] for row in assignments}

    check("RESULT_STATUS", result["status"] == STATUS, result["status"])
    check("INPUT_HASHES", result["input_sha256"] == {name: sha256(path) for name, path in INPUTS.items()}, "all eleven source hashes")
    check("ASSIGNMENT_COUNT", len(assignments) == 1243, str(len(assignments)))
    check("UNIQUE_ASSIGNMENT_SLOT_IDS", len(assignment_ids) == 1243, str(len(assignment_ids)))
    check("EXACT_CANDIDATE_SET", assignment_ids == exact_candidates, f"{len(exact_candidates)} exact joined slots")
    check("ACTION_HOST_COUNT", len({row["primary_governor_key"] for row in assignments}) == 953, "953")
    check("HOST_ROOT_CELL_COUNT", len({(row["primary_governor_key"], row["carrier_root"]) for row in assignments}) == 1111, "1111")
    check("GLOBAL_ROOT_POPULATION", sum(row["slot_value"] in ROOTS for row in source["complete_defaults"]) == 3254, "3254")
    check("OUTSIDE_CANDIDATE_ROOT_SLOTS", 3254 - len(assignments) == 2011, "2011 untouched global root slots")
    check("ROOT_COUNTS", Counter(row["carrier_root"] for row in assignments) == {"Y": 842, "AIIN": 200, "OR": 124, "AIN": 77}, str(Counter(row["carrier_root"] for row in assignments)))
    check("REGISTER_COUNTS", Counter(row["register"] for row in assignments) == {"BIOLOGICAL": 550, "HERBAL": 289, "CELESTIAL": 175, "SOURCE_SECTION_T": 118, "PHARMA": 111}, str(Counter(row["register"] for row in assignments)))
    check("LAYER_COUNTS", Counter(row["layer"] for row in assignments) == {"RUNNING_ATOM": 1163, "LOCAL_COMPONENT": 80}, str(Counter(row["layer"] for row in assignments)))
    check("PORTABLE_CORES_UNCHANGED", all(row["portable_carrier_core"] == CORE[row["carrier_root"]] for row in assignments), "Y/AIIN/AIN/OR retain POSTEN/WERT/ANTEIL/EINHEIT")
    check("SOURCE_SLOT_PROJECTION", all(complete_by_slot[row["carrier_slot_id"]]["slot_value"] == row["carrier_root"] and complete_by_slot[row["carrier_slot_id"]]["primary_governor_key"] == row["primary_governor_key"] for row in assignments), "1243 exact ledger projections")
    check("ACTION_SLOT_PROJECTION", all(action_by_key[row["primary_governor_key"]]["slot_id"] == row["action_slot_id"] and action_by_key[row["primary_governor_key"]]["gdt584_rule_id"] == row["gdt584_rule_id"] for row in assignments), "1243 exact target-action joins")
    check("NO_EMPTY_NOUN_FORMS", all(all(row[field] not in {"", "NONE"} for field in ("gdt587_lemma_de", "gdt587_object_form_de", "gdt587_genitive_form_de")) for row in assignments), "1243 lemma/object/genitive triples")
    check("DISPOSITION_PROFILE", Counter(row["gdt587_disposition"] for row in assignments) == {"BASE_RETAINED": 632, "ACTION_NARROWED": 526, "PACKET_NARROWED": 85}, str(Counter(row["gdt587_disposition"] for row in assignments)))
    check("BODY_READING_BOUNDED", sum(row["gdt587_lemma_de"] == "Körper" for row in assignments) == 61 and sum(row["gdt587_lemma_de"] == "Teil" for row in assignments) == 5, "61 Körper atoms plus 5 Teil atoms")
    remote = sum(row["layer"] == "RUNNING_ATOM" and complete_by_slot[row["carrier_slot_id"]]["source_event_or_card_id"] != action_by_key[row["primary_governor_key"]]["source_event_or_card_id"] for row in assignments)
    check("REMOTE_RUNNING_CARRIERS", remote == 384, str(remote))
    zero_rules = {"T_BIO_RELATION_REGULATE", "T_HP_LIQUID_TEMPER", "S_BIO_CHD_CARRIER_SELECT", "S_HP_TAKE_OFF_AFTER_WET_STEP"}
    check("NO_INVENTED_CARRIER_RULES", not (zero_rules & {row["gdt584_rule_id"] for row in assignments}), "four zero-carrier action rules remain empty")
    check("NO_EXACT_NAME_SLOT_OVERLAP", not (assignment_ids & set(names_by_slot)), "0 exact slots")
    check("NO_NAME_GOVERNOR_OVERLAP", not ({row["primary_governor_key"] for row in assignments} & {row["primary_governor_key"] for row in source["name_assignments_585"]}), "0 governor keys")
    shared_name_cards = {row["source_event_or_card_id"] for row in assignments} & {row["source_event_or_card_id"] for row in source["name_assignments_585"]}
    check("ONE_SHARED_NAMED_LOCAL_CARD", shared_name_cards == {"P1003-E0414"}, "P1003-E0414 only")

    check("CELL_COUNT", len(cells) == 136, str(len(cells)))
    source_cells = {(row["register"], row["gdt584_rule_id"], row["carrier_root"]) for row in assignments}
    output_cells = {(row["register"], row["gdt584_rule_id"], row["carrier_root"]) for row in cells}
    check("CELL_SET_EXACT", output_cells == source_cells, "136 observed cells, no matrix fill")
    check("CELL_SLOT_TOTAL", sum(int(row["written_slot_count"]) for row in cells) == 1243, str(sum(int(row["written_slot_count"]) for row in cells)))
    check("CELL_COUNTS_EXACT", all(int(row["written_slot_count"]) == sum(a["register"] == row["register"] and a["gdt584_rule_id"] == row["gdt584_rule_id"] and a["carrier_root"] == row["carrier_root"] for a in assignments) for row in cells), "136 recomputed slot counts")

    running_statement_ids = {row["statement_or_record_id"] for row in assignments if row["layer"] == "RUNNING_ATOM"}
    local_event_ids = {row["source_event_or_card_id"] for row in assignments if row["layer"] == "LOCAL_COMPONENT"}
    check("CANDIDATE_STATEMENT_COUNT", len(candidate_statements) == 379 and set(candidate_statement_by_id) == running_statement_ids, "379 exact IDs")
    check("CANDIDATE_LOCAL_COUNT", len(candidate_local) == 70 and set(candidate_local_by_id) == local_event_ids, "70 exact IDs")
    local_records = {row["statement_or_record_id"] for row in assignments if row["layer"] == "LOCAL_COMPONENT" and row["statement_or_record_id"] != "NOT_APPLICABLE"}
    local_unrecorded_cards = {row["source_event_or_card_id"] for row in assignments if row["layer"] == "LOCAL_COMPONENT" and row["statement_or_record_id"] == "NOT_APPLICABLE"}
    check("LOCAL_RECORD_PROFILE", local_records == {"LOCAL_RECORD:G475-R025", "LOCAL_RECORD:G475-R095", "LOCAL_RECORD:G475-R126"} and len(local_unrecorded_cards) == 67, "3 named records plus 67 unrecorded cards")
    check("CANDIDATE_STATEMENT_BASES", all(row["gdt584_polished_paragraph_de"] == old_statement_584[row["statement_id"]]["gdt584_polished_paragraph_de"] for row in candidate_statements), "379 exact GDT584 bases")
    check("CANDIDATE_LOCAL_BASES", all(row["gdt584_polished_local_clause_de"] == old_local_584[row["source_event_id"]]["gdt584_polished_local_clause_de"] for row in candidate_local), "70 exact GDT584 bases")

    hosts_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in hosts:
        hosts_by_statement[row["statement_id"]].append(row)
    check("HOST_STATEMENT_SET", set(hosts_by_statement) == running_statement_ids, "379 exact statement host partitions")
    expected_slots_by_statement: dict[str, list[str]] = defaultdict(list)
    statement_for_event: dict[str, str] = {}
    for row in source["statements_582"]:
        for event_id in row["event_ids"].split("|"):
            statement_for_event[event_id] = row["statement_id"]
    for row in source["complete_defaults"]:
        sid = statement_for_event.get(row["source_event_or_card_id"])
        if sid in running_statement_ids:
            expected_slots_by_statement[sid].append(row["slot_id"])
    host_partition_ok = True
    for sid in running_statement_ids:
        projected = [slot for row in hosts_by_statement[sid] for slot in row["written_packet_slot_ids"].split("|")]
        host_partition_ok &= Counter(projected) == Counter(expected_slots_by_statement[sid])
    check("HOST_PARTITION_ALL_COMPLETE_SLOTS", host_partition_ok, "all 379 statement slot multisets")
    host_carrier_ids = {slot for row in hosts for slot in row["carrier_slot_ids"].split("|") if slot != "NONE"}
    running_carrier_ids = {row["carrier_slot_id"] for row in assignments if row["layer"] == "RUNNING_ATOM"}
    check("HOST_CARRIERS_EXACT", host_carrier_ids == running_carrier_ids, "1163 exact running carrier slots")
    check("STATEMENT_TRACE_COMPLETENESS", all(Counter(trace_ids(row["gdt587_exact_slot_trace_de"])) == Counter(expected_slots_by_statement[row["statement_id"]]) for row in candidate_statements), "379 exact traces")

    expected_local_slots: dict[str, list[str]] = defaultdict(list)
    for row in source["complete_defaults"]:
        if row["source_event_or_card_id"] in local_event_ids:
            expected_local_slots[row["source_event_or_card_id"]].append(row["slot_id"])
    check("LOCAL_TRACE_COMPLETENESS", all(Counter(trace_ids(row["gdt587_exact_slot_trace_de"])) == Counter(expected_local_slots[row["source_event_id"]]) for row in candidate_local), "70 exact local traces")

    check("FULL_STATEMENT_COUNT", len(statements) == 793, str(len(statements)))
    check("FULL_LOCAL_COUNT", len(local) == 744, str(len(local)))
    check("FULL_STATEMENT_ORDER", [row["statement_id"] for row in statements] == [row["statement_id"] for row in source["statements_586"]], "793 ordered IDs")
    check("FULL_LOCAL_ORDER", [row["source_event_id"] for row in local] == [row["source_event_id"] for row in source["local_cards_586"]], "744 ordered IDs")
    check("FULL_STATEMENT_BASE_CHANNEL", all(row["gdt587_base_reader_de"] == old_statement_586[row["statement_id"]]["gdt586_primary_reader_de"] for row in statements), "793 GDT586 base readings")
    check("FULL_LOCAL_BASE_CHANNEL", all(row["gdt587_base_reader_de"] == old_local_586[row["source_event_id"]]["gdt586_primary_reader_de"] for row in local), "744 GDT586 base readings")
    noncandidate_statement_exact = sum(row["gdt587_primary_reader_de"] == old_statement_586[row["statement_id"]]["gdt586_primary_reader_de"] for row in statements if row["statement_id"] not in running_statement_ids)
    noncandidate_local_exact = sum(row["gdt587_primary_reader_de"] == old_local_586[row["source_event_id"]]["gdt586_primary_reader_de"] for row in local if row["source_event_id"] not in local_event_ids)
    check("NONCANDIDATE_STATEMENTS_BYTE_EXACT", noncandidate_statement_exact == 414, str(noncandidate_statement_exact))
    check("NONCANDIDATE_LOCAL_BYTE_EXACT", noncandidate_local_exact == 674, str(noncandidate_local_exact))
    check("CANDIDATE_STATEMENT_PROJECTION", all(statement_by_id[sid]["gdt587_primary_reader_de"] == row["gdt587_action_noun_paragraph_de"] for sid, row in candidate_statement_by_id.items()), "379 candidate paragraphs")
    check("CANDIDATE_LOCAL_PROJECTION", all(local_by_id[event]["gdt587_primary_reader_de"] == (row["gdt587_named_carrier_primary_de"] if row["gdt587_named_carrier_primary_de"] != "NOT_APPLICABLE" else row["gdt587_action_noun_local_clause_de"]) for event, row in candidate_local_by_id.items()), "70 candidate cards")
    changed_statements = sum(row["gdt587_reader_changed"] == "YES" for row in statements)
    changed_local = sum(row["gdt587_reader_changed"] == "YES" for row in local)
    check("CHANGED_STATEMENT_COUNT", changed_statements == result["changed_complete_statements"] == 227, str(changed_statements))
    check("CHANGED_LOCAL_COUNT", changed_local == result["changed_complete_local_cards"] == 14, str(changed_local))
    check("CHANGED_HOST_COUNT", sum(row["reader_clause_changed"] == "YES" for row in hosts) == result["changed_host_clauses"] == 499, str(result["changed_host_clauses"]))

    name_card_ids = {row["source_event_or_card_id"] for row in source["name_assignments_585"] if row["source_kind"] == "GDT581_NAME_SPAN"}
    unchanged_named_cards = sum(local_by_id[event]["gdt587_primary_reader_de"] == old_local_586[event]["gdt586_primary_reader_de"] for event in name_card_ids if event != "P1003-E0414")
    check("UNCHANGED_NAME_CARDS", unchanged_named_cards == 88, str(unchanged_named_cards))
    special = local_by_id["P1003-E0414"]["gdt587_primary_reader_de"]
    check("NAMED_CARRIER_COMPOSITION", "dunkle Faserwurzeldroge [cheo]" in special and special.count("Drogenmaterial") == 2 and "Essig" not in special and "Drogenposten" not in special, special)
    check("RUNNING_HEILMITTEL_REAPPLIED", "Heilmittel" in statement_by_id["G515-S050"]["gdt587_primary_reader_de"] and "Heilmittel oder Heilwirkung" not in statement_by_id["G515-S050"]["gdt587_primary_reader_de"], "G515-S050")
    check("RUNNING_BESCHWERDE_RETAINED", statement_by_id["G515-S046"]["gdt587_primary_reader_de"] == old_statement_586["G515-S046"]["gdt586_primary_reader_de"], "G515-S046 byte exact")

    check("PACKET_SOURCE_PART", "Lege die Teilmenge des Arbeitsmaterials fest" in statement_by_id["G407-S003"]["gdt587_primary_reader_de"], "G407-S003")
    check("PACKET_CELESTIAL", "Ringposition des Ringsegments auf den Positionswert" in statement_by_id["G407-S047"]["gdt587_primary_reader_de"], "G407-S047")
    check("PACKET_BIO_FLOW", "angegebene Menge des Beckeninhalts" in statement_by_id["G407-S440"]["gdt587_primary_reader_de"], "G407-S440")
    check("PACKET_BODY_PART", "Behandle den Körperteil" in statement_by_id["G407-S621"]["gdt587_primary_reader_de"], "G407-S621")
    check("PACKET_STRAIN_PORTION", "Auszug aus der Zutatenportion" in statement_by_id["G407-S667"]["gdt587_primary_reader_de"], "G407-S667")
    check("DRY_STATE_IN_VERBS_ONLY", "Trockne das Pflanzenmaterial" in statement_by_id["G407-S696"]["gdt587_primary_reader_de"] and "Zerreibe das Pflanzenmaterial" in statement_by_id["G407-S696"]["gdt587_primary_reader_de"], "G407-S696")
    check("BODY_CLEAN_PACKET", "Halte den Körper im Bad" in statement_by_id["G407-S151"]["gdt587_primary_reader_de"] and "Lass den Körper anschließend abkühlen" in statement_by_id["G407-S151"]["gdt587_primary_reader_de"], "G407-S151")
    check("BODY_NEGATIVE_CONTROL_572", statement_by_id["G407-S572"]["gdt587_primary_reader_de"] == old_statement_586["G407-S572"]["gdt586_primary_reader_de"], "G407-S572 unchanged")
    check("BODY_NEGATIVE_CONTROL_115", statement_by_id["G407-S115"]["gdt587_primary_reader_de"] == old_statement_586["G407-S115"]["gdt586_primary_reader_de"], "G407-S115 unchanged")

    check("PAGE_COUNT", len(pages) == 30 and len({row["physical_page"] for row in pages}) == 30, "30")
    check("PAGE_READER_TOTALS", sum(int(row["statement_count"]) for row in pages) == 793 and sum(int(row["local_card_count"]) for row in pages) == 744 and sum(int(row["carrier_assignment_count"]) for row in pages) == 1243, "793 + 744 units, 1243 carriers")
    check("MANUAL_AUDIT_COUNT", len(manual) == 25 and {row["statement_id"] for row in manual} == AUDIT_IDS, "25 exact passages")
    check("BOOK_ALL_UNITS", sum(book.count(f"#### {row['statement_id']} —") for row in statements) == 793 and sum(book.count(f"#### {row['source_event_id']} —") for row in local) == 744, "1537 headings")
    check("MANUAL_BOOK_ALL_IDS", all(manual_book.count(f"## {sid} —") == 1 for sid in AUDIT_IDS), "25 headings")
    check("FORBIDDEN_PAGE_ABSENT", all(not row.get("physical_page", "").lower().startswith("f84") for table in rows.values() for row in table) and "f84r" not in book.lower() and "f84v" not in book.lower(), "no f84/f84r/f84v")

    failed = [row for row in checks if row["status"] != "PASS"]
    validation = {
        "experiment_id": "GDT587",
        "status": f"PASS_{len(checks)}_OF_{len(checks)}" if not failed else f"FAIL_{len(failed)}_OF_{len(checks)}",
        "check_count": len(checks),
        "pass_count": len(checks) - len(failed),
        "fail_count": len(failed),
        "checks": checks,
        "output_sha256": {name: sha256(path) for name, path in OUTPUTS.items()},
    }
    path = OUT / "gdt587_validation.json"
    path.write_text(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
