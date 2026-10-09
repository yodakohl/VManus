#!/usr/bin/env python3
"""Validate the blinded V81 R2 Phase-2 deliverables.

The validator reads only the central protocol, R2's own frozen Phase-1
artifacts, the four explicitly authorized central target artifacts, and R2's
own Phase-2 outputs.  It never discovers files by glob and never opens V80,
manuscript, transcription, page/image, or sibling-role material.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


BASE = Path(__file__).resolve().parent
YOLO = BASE.parent

PROTOCOL = YOLO / "SIDEQUEST_V81_ATOMIC_CODEBOOK_VOCABULARY_PROTOCOL.md"
R2_INVENTORY = BASE / "V81_R2_PHASE1_SOURCE_INVENTORY.tsv"
R2_REPORT = BASE / "V81_R2_PHASE1_HISTORICAL_SOURCE_REPORT.md"
R2_FREEZE = BASE / "V81_R2_SOURCE_FREEZE.json"
TARGET_FREEZE = BASE / "V81_TARGET_FREEZE.json"
TARGET_MANIFEST = BASE / "V81_TARGET_MANIFEST.tsv"
TARGET_OCCURRENCES = BASE / "V81_TARGET_OCCURRENCE_PACKET.tsv"
TARGET_STATEMENTS = BASE / "V81_TARGET_AFFECTED_STATEMENTS.tsv"

DECISIONS = BASE / "V81_R2_PHASE2_DECISIONS.tsv"
OCCURRENCE_AUDIT = BASE / "V81_R2_PHASE2_OCCURRENCE_AUDIT.tsv"
REVISIONS = BASE / "V81_R2_PHASE2_AFFECTED_STATEMENT_REVISIONS.tsv"
PHASE2_REPORT = BASE / "V81_R2_PHASE2_REPORT.md"
VALIDATOR = BASE / "V81_R2_PHASE2_VALIDATOR.py"
VALIDATION = BASE / "V81_R2_PHASE2_VALIDATION.json"

EXPECTED_HASHES = {
    "protocol": "45ec0cfed64cea2fc4488a89a053fa94e04c320fea321d37f24d4d4821437d92",
    "r2_inventory": "45d0ed8c3586f018134ce4e9c058c343e368c6e62765205e85f0d5a62f09766c",
    "r2_report": "426036560691beee9e8567a941d6489198ef7ed67b650cd3c70b0aa0ac53b6d8",
    "r2_freeze": "680ad5b17bd5286b4b2ef7e495b3f0ce92cafc402c1531bbccd8d3ca65b29fdb",
    "target_freeze": "76b102a61f30ca9aa507a6c42b5315f6c43e75628d19c0ebe10ef835ec44a06d",
    "target_manifest": "c2c2ad1bd6418ed7a332d6ed948192f469ce8fd64e6cd4c5c5c87e33b76e2b04",
    "target_occurrences": "b6cc5afd9421a64aaec6644f095160a42f8e7999bd63ea3151a05860dd9896ee",
    "target_statements": "8a0b627902605ca59a7f25f1d148d1fdc0b00f63e53a1f5617409e0af25ca2b7",
}

SOURCE_DEPENDENCE = (
    "MEISTER_SIMILAR_TO_KEY13__NO_INDEPENDENT_CUMULATIVE_WEIGHT"
)

ALLOWED_PAGES = {
    "f10r",
    "f11r",
    "f55v",
    "f56r",
    "f81v",
    "f82r",
    "f83r",
    "f67r2",
    "f68r1",
    "f69v",
}

DECISION_FIELDS = [
    "anonymous_target_id",
    "target_rank",
    "joint_tuple_id",
    "visible_occurrences",
    "independent_source_positions",
    "distinct_pages",
    "distinct_records",
    "tested_atomic_category_de",
    "source_row_id",
    "exact_source_entry",
    "exact_source_code",
    "atomic_le3_words_gate",
    "exact_historical_pair_gate",
    "invariant_default_gate",
    "formal_records_ge2_gate",
    "usable_every_occurrence_gate",
    "improves_ge2_complete_statements_gate",
    "silent_formal_or_exemplar_rival",
    "strongest_contradiction",
    "repair_cost",
    "source_dependence_caveat",
    "decision",
    "portable_word_status",
]

REVISION_FIELDS = [
    "statement_id",
    "anonymous_target_ids",
    "decision_classes",
    "atomic_categories_de",
    "source_row_ids",
    "original_master_memorized_statement_content",
    "revised_continuous_reading",
    "revision_status",
    "revision_reason",
]

AUDIT_APPEND_FIELDS = [
    "tested_atomic_category_de",
    "source_row_id",
    "exact_source_entry",
    "exact_source_code",
    "occurrence_fit",
    "null_rival_compared",
    "additional_contradiction_or_repair",
    "card_decision",
    "source_dependence_caveat",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    require(isinstance(value, dict), f"JSON object required: {path.name}")
    return value


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    require(bool(fields), f"TSV header required: {path.name}")
    require(len(fields) == len(set(fields)), f"duplicate TSV fields: {path.name}")
    for ordinal, row in enumerate(rows, 2):
        require(None not in row, f"extra TSV field at {path.name}:{ordinal}")
        require(all(value is not None for value in row.values()), f"missing TSV field at {path.name}:{ordinal}")
    return fields, rows


def verify_fixed_hashes() -> None:
    actual = {
        "protocol": sha256(PROTOCOL),
        "r2_inventory": sha256(R2_INVENTORY),
        "r2_report": sha256(R2_REPORT),
        "r2_freeze": sha256(R2_FREEZE),
        "target_freeze": sha256(TARGET_FREEZE),
        "target_manifest": sha256(TARGET_MANIFEST),
        "target_occurrences": sha256(TARGET_OCCURRENCES),
        "target_statements": sha256(TARGET_STATEMENTS),
    }
    require(actual == EXPECTED_HASHES, f"fixed input hash mismatch: {actual}")


def verify_freeze_chain() -> tuple[dict[str, Any], dict[str, Any]]:
    r2_freeze = read_json(R2_FREEZE)
    target_freeze = read_json(TARGET_FREEZE)
    require(r2_freeze["status"] == "FROZEN_BEFORE_V81_TARGET_MANIFEST", "bad R2 freeze status")
    require(r2_freeze["target_manifest_opened"] is False, "R2 source was not blind")
    require(r2_freeze["inventory_sha256"] == EXPECTED_HASHES["r2_inventory"], "R2 inventory binding mismatch")
    require(r2_freeze["report_sha256"] == EXPECTED_HASHES["r2_report"], "R2 report binding mismatch")
    require(r2_freeze["protocol_sha256"] == EXPECTED_HASHES["protocol"], "R2 protocol binding mismatch")
    require(r2_freeze["inventory_data_rows"] == 37, "unexpected R2 source row count")
    require(r2_freeze["inventory_row_cap"] == 60, "unexpected source row cap")
    require(r2_freeze["historical_key"]["independence_warning"], "source independence warning missing")
    require(all(value is False for value in r2_freeze["blindness_attestation"].values()), "R2 blindness attestation failed")

    require(target_freeze["status"] == "PASS__FROZEN_AFTER_FOUR_SOURCE_FIRST_FREEZES", "bad target freeze status")
    require(target_freeze["source_freeze_hashes"]["R2"] == EXPECTED_HASHES["r2_freeze"], "target does not bind R2 freeze")
    require(target_freeze["source_inventory_hashes"]["R2"] == EXPECTED_HASHES["r2_inventory"], "target does not bind R2 inventory")
    require(target_freeze["input_hashes"][PROTOCOL.name] == EXPECTED_HASHES["protocol"], "target protocol binding mismatch")
    require(target_freeze["output_hashes"][TARGET_MANIFEST.name] == EXPECTED_HASHES["target_manifest"], "manifest binding mismatch")
    require(target_freeze["output_hashes"][TARGET_OCCURRENCES.name] == EXPECTED_HASHES["target_occurrences"], "occurrence binding mismatch")
    require(target_freeze["output_hashes"][TARGET_STATEMENTS.name] == EXPECTED_HASHES["target_statements"], "statement binding mismatch")
    require(target_freeze["seals"] == {"f84": "SEALED_NOT_ACCESSED", "f84r": "SEALED_NOT_ACCESSED"}, "central seals failed")
    return r2_freeze, target_freeze


def verify_targets() -> tuple[
    list[str],
    list[dict[str, str]],
    list[str],
    list[dict[str, str]],
    list[dict[str, str]],
]:
    manifest_fields, manifest = read_tsv(TARGET_MANIFEST)
    occurrence_fields, occurrences = read_tsv(TARGET_OCCURRENCES)
    _, statements = read_tsv(TARGET_STATEMENTS)

    ids = [f"T{number:03d}" for number in range(1, 31)]
    require(len(manifest) == 30, "target panel must contain 30 cards")
    require([row["anonymous_target_id"] for row in manifest] == ids, "target IDs/order mismatch")
    require([int(row["target_rank"]) for row in manifest] == list(range(1, 31)), "target ranks mismatch")
    require(len(occurrences) == 217, "occurrence packet must contain 217 rows")
    require(len(statements) == 94, "target statements must contain 94 rows")
    require(sum(int(row["source_position_contribution"]) for row in occurrences) == 216, "independent source-position count mismatch")

    occurrence_counts = Counter(row["anonymous_target_id"] for row in occurrences)
    contribution_counts = Counter()
    page_sets: dict[str, set[str]] = {target_id: set() for target_id in ids}
    record_sets: dict[str, set[str]] = {target_id: set() for target_id in ids}
    for row in occurrences:
        target_id = row["anonymous_target_id"]
        require(target_id in ids, f"unknown occurrence target: {target_id}")
        contribution_counts[target_id] += int(row["source_position_contribution"])
        page_sets[target_id].add(row["page"])
        record_sets[target_id].add(row["record_unit_id"])
        require(row["page"] in ALLOWED_PAGES, f"out-of-scope or sealed page: {row['page']}")
        require(row["surface_channel"] == "WITHHELD__NO_SURFACE_OR_COMPONENT_SELECTION", "surface channel revealed")

    for row in manifest:
        target_id = row["anonymous_target_id"]
        require(occurrence_counts[target_id] == int(row["visible_occurrences"]), f"visible occurrence count mismatch: {target_id}")
        require(contribution_counts[target_id] == int(row["independent_source_positions"]), f"source-position count mismatch: {target_id}")
        require(len(page_sets[target_id]) == int(row["distinct_pages"]), f"page count mismatch: {target_id}")
        require(len(record_sets[target_id]) == int(row["distinct_records"]), f"record count mismatch: {target_id}")
        require(row["surface_channel"] == "WITHHELD__NO_SURFACE_OR_COMPONENT_SELECTION", "manifest surface channel revealed")

    return manifest_fields, manifest, occurrence_fields, occurrences, statements


def ordinary_german_word_count(category: str) -> int:
    words = category.split()
    require(words and len(words) <= 3, f"atomic word cap failed: {category}")
    require(all(re.fullmatch(r"[A-Za-zÄÖÜäöüß]+", word) for word in words), f"nonordinary atomic category: {category}")
    return len(words)


def verify_decisions(manifest: list[dict[str, str]]) -> tuple[list[dict[str, str]], dict[str, dict[str, str]]]:
    fields, decisions = read_tsv(DECISIONS)
    require(fields == DECISION_FIELDS, "decision header mismatch")
    require(len(decisions) == 30, "decision table must contain 30 rows")
    require([row["anonymous_target_id"] for row in decisions] == [row["anonymous_target_id"] for row in manifest], "decision panel/order mismatch")

    inventory_fields, inventory = read_tsv(R2_INVENTORY)
    require("row_id" in inventory_fields, "R2 source row ID missing")
    source_by_id = {row["row_id"]: row for row in inventory}
    require(len(source_by_id) == 37, "duplicate or missing R2 source rows")

    manifest_by_id = {row["anonymous_target_id"]: row for row in manifest}
    decision_by_id: dict[str, dict[str, str]] = {}
    allowed_decisions = {"PROMOTE", "NEAR", "REJECT"}
    promote_gate_fields = [
        "atomic_le3_words_gate",
        "exact_historical_pair_gate",
        "invariant_default_gate",
        "formal_records_ge2_gate",
        "usable_every_occurrence_gate",
        "improves_ge2_complete_statements_gate",
    ]

    for row in decisions:
        target_id = row["anonymous_target_id"]
        manifest_row = manifest_by_id[target_id]
        for field in (
            "target_rank",
            "joint_tuple_id",
            "visible_occurrences",
            "independent_source_positions",
            "distinct_pages",
            "distinct_records",
        ):
            require(row[field] == manifest_row[field], f"decision/manifest mismatch {target_id}:{field}")
        require(row["decision"] in allowed_decisions, f"bad decision class: {target_id}")
        require(row["source_dependence_caveat"] == SOURCE_DEPENDENCE, f"source-dependence caveat missing: {target_id}")
        require(bool(row["silent_formal_or_exemplar_rival"]), f"null rival missing: {target_id}")
        require(bool(row["strongest_contradiction"]), f"contradiction missing: {target_id}")
        require(bool(row["repair_cost"]), f"repair cost missing: {target_id}")

        source_row_id = row["source_row_id"]
        if source_row_id == "NONE":
            require(row["exact_source_entry"] == "NONE" and row["exact_source_code"] == "NONE", f"unbound source text: {target_id}")
            require(row["tested_atomic_category_de"].startswith("NONE__"), f"category without source row: {target_id}")
        else:
            require(source_row_id in source_by_id, f"unknown source row: {target_id}")
            source_row = source_by_id[source_row_id]
            require(row["exact_source_entry"] == source_row["exact_source_language_entry"], f"source entry mismatch: {target_id}")
            require(row["exact_source_code"] == source_row["exact_opaque_code_or_sign"], f"source code mismatch: {target_id}")
            ordinary_german_word_count(row["tested_atomic_category_de"])

        if row["decision"] == "PROMOTE":
            require(all(row[field] == "PASS" for field in promote_gate_fields), f"PROMOTE without all gates: {target_id}")
            require(row["portable_word_status"] == "NEW", f"PROMOTE not marked NEW: {target_id}")
        else:
            require(row["portable_word_status"] == "NONE", f"nonpromotion marked portable: {target_id}")
        decision_by_id[target_id] = row

    require(decision_by_id["T004"]["source_row_id"] == "R2S032", "pax stress test missing")
    require(decision_by_id["T004"]["tested_atomic_category_de"] == "Frieden", "Frieden stress test mismatch")
    require(decision_by_id["T007"]["source_row_id"] == "R2S018", "regina stress test missing")
    require(decision_by_id["T007"]["tested_atomic_category_de"] == "Königin", "Königin stress test mismatch")
    require(Counter(row["decision"] for row in decisions) == Counter({"REJECT": 30}), "unexpected promotion or near decision")
    return decisions, decision_by_id


def build_expected_occurrence_audit(
    occurrence_fields: list[str],
    occurrences: list[dict[str, str]],
    decision_by_id: dict[str, dict[str, str]],
) -> tuple[list[str], list[dict[str, str]]]:
    fields = occurrence_fields + AUDIT_APPEND_FIELDS
    rows: list[dict[str, str]] = []
    for source in occurrences:
        row = dict(source)
        target_id = source["anonymous_target_id"]
        decision = decision_by_id[target_id]
        if target_id == "T004":
            occurrence_fit = "FAIL__READINESS_AND_STEP_CLOSURE_DO_NOT_DENOTE_FRIEDEN"
            extra = "Core-sense repair required: Frieden would have to mean ready/end; prohibited."
        elif target_id == "T007":
            if "Badende" in source["master_memorized_selected_token"]:
                occurrence_fit = "FAIL__BATHER_CONTEXT_DOES_NOT_LICENSE_ROYAL_TITLE"
                extra = "A bather is not thereby a Königin; royal status is absent."
            else:
                occurrence_fit = "FAIL__NO_PERSON_ROLE_IN_THIS_CLOTH_OR_AREA_OPERATION"
                extra = "Königin would force a person title into a nonperson terminal operation."
        else:
            occurrence_fit = "NO_CANDIDATE__SOURCE_FAMILY_SCREEN_NEGATIVE"
            extra = decision["repair_cost"]

        row.update(
            {
                "tested_atomic_category_de": decision["tested_atomic_category_de"],
                "source_row_id": decision["source_row_id"],
                "exact_source_entry": decision["exact_source_entry"],
                "exact_source_code": decision["exact_source_code"],
                "occurrence_fit": occurrence_fit,
                "null_rival_compared": decision["silent_formal_or_exemplar_rival"],
                "additional_contradiction_or_repair": extra,
                "card_decision": decision["decision"],
                "source_dependence_caveat": SOURCE_DEPENDENCE,
            }
        )
        rows.append(row)
    require(len(rows) == 217, "expected occurrence projection count mismatch")
    return fields, rows


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def verify_occurrence_audit(
    expected_fields: list[str], expected_rows: list[dict[str, str]]
) -> list[dict[str, str]]:
    fields, rows = read_tsv(OCCURRENCE_AUDIT)
    require(fields == expected_fields, "occurrence-audit header mismatch")
    require(rows == expected_rows, "occurrence audit is not the exact full projection")
    require(len(rows) == 217, "occurrence audit must include all 217 tested-card occurrences")
    require(sum(row["anonymous_target_id"] == "T004" for row in rows) == 12, "T004 audit incomplete")
    require(sum(row["anonymous_target_id"] == "T007" for row in rows) == 10, "T007 audit incomplete")
    require(sum("BATHER_CONTEXT" in row["occurrence_fit"] for row in rows) == 5, "T007 bather count mismatch")
    require(sum("NO_PERSON_ROLE" in row["occurrence_fit"] for row in rows) == 5, "T007 nonperson count mismatch")
    return rows


def verify_revisions(
    decisions: list[dict[str, str]], statements: list[dict[str, str]]
) -> list[dict[str, str]]:
    fields, rows = read_tsv(REVISIONS)
    require(fields == REVISION_FIELDS, "revision header mismatch")
    active_ids = {
        row["anonymous_target_id"]
        for row in decisions
        if row["decision"] in {"PROMOTE", "NEAR"}
    }
    expected_statement_ids = {
        row["statement_id"]
        for row in statements
        if active_ids.intersection(row["anonymous_targets_in_order"].split("|"))
    }
    require({row["statement_id"] for row in rows} == expected_statement_ids, "affected-statement coverage mismatch")
    require(len(rows) == len(expected_statement_ids), "duplicate revision statement")
    for row in rows:
        require(bool(row["revised_continuous_reading"]), f"empty revised statement: {row['statement_id']}")
    require(not active_ids and not rows, "current all-REJECT result must have zero revisions")
    return rows


def verify_report() -> None:
    text = PHASE2_REPORT.read_text(encoding="utf-8")
    required_phrases = [
        "NEW portable word: NONE",
        "EXEMPLAR_VALUE_UNKNOWN",
        EXPECTED_HASHES["r2_inventory"],
        EXPECTED_HASHES["r2_freeze"],
        "Sehr ähnlich Nr. 13",
        "T004 → Frieden",
        "T007 → Königin",
        "all 217 target occurrences",
        "zero data rows",
        "f84/f84r remained sealed",
    ]
    for phrase in required_phrases:
        require(phrase in text, f"report disclosure missing: {phrase}")


def validate_core() -> dict[str, Any]:
    verify_fixed_hashes()
    r2_freeze, target_freeze = verify_freeze_chain()
    _, manifest, occurrence_fields, occurrences, statements = verify_targets()
    decisions, decision_by_id = verify_decisions(manifest)
    expected_fields, expected_rows = build_expected_occurrence_audit(
        occurrence_fields, occurrences, decision_by_id
    )
    occurrence_audit = verify_occurrence_audit(expected_fields, expected_rows)
    revisions = verify_revisions(decisions, statements)
    verify_report()

    decision_counts = Counter(row["decision"] for row in decisions)
    phase2_hashes = {
        DECISIONS.name: sha256(DECISIONS),
        OCCURRENCE_AUDIT.name: sha256(OCCURRENCE_AUDIT),
        REVISIONS.name: sha256(REVISIONS),
        PHASE2_REPORT.name: sha256(PHASE2_REPORT),
        VALIDATOR.name: sha256(VALIDATOR),
    }
    return {
        "schema": "V81_R2_PHASE2_VALIDATION_V1",
        "status": "PASS__NO_NEW_PORTABLE_WORD",
        "checks": {
            "fixed_input_hashes": True,
            "r2_phase1_freeze_chain": True,
            "target_freeze_chain": True,
            "target_cards_exactly_30": True,
            "all_30_cards_decided": True,
            "target_occurrences_exactly_217": True,
            "independent_source_positions_exactly_216": True,
            "full_occurrence_audit_exact_projection": True,
            "atomic_word_cap_enforced": True,
            "exact_source_pairs_enforced": True,
            "invariant_default_gate_enforced": True,
            "formal_records_gate_enforced": True,
            "two_statement_improvement_gate_enforced": True,
            "null_rivals_disclosed": True,
            "contradictions_and_repairs_disclosed": True,
            "affected_statement_coverage_complete": True,
            "source_dependence_caveat_preserved": True,
            "surface_and_component_channels_withheld": True,
            "fixed_pages_only": True,
            "sealed_pages_absent": True,
        },
        "counts": {
            "source_rows": r2_freeze["inventory_data_rows"],
            "target_cards": len(manifest),
            "visible_occurrences": len(occurrences),
            "independent_source_positions": sum(
                int(row["source_position_contribution"]) for row in occurrences
            ),
            "occurrence_audit_rows": len(occurrence_audit),
            "target_affected_statements": len(statements),
            "phase2_revised_statements": len(revisions),
        },
        "decisions": {
            "PROMOTE": decision_counts.get("PROMOTE", 0),
            "NEAR": decision_counts.get("NEAR", 0),
            "REJECT": decision_counts.get("REJECT", 0),
        },
        "new_portable_word": "NONE",
        "r2_phase1_binding": {
            "inventory_sha256": EXPECTED_HASHES["r2_inventory"],
            "report_sha256": EXPECTED_HASHES["r2_report"],
            "freeze_sha256": EXPECTED_HASHES["r2_freeze"],
            "source_object_sha256": r2_freeze["source_object"]["sha256"],
            "status": r2_freeze["status"],
        },
        "target_binding": {
            "freeze_sha256": EXPECTED_HASHES["target_freeze"],
            "manifest_sha256": EXPECTED_HASHES["target_manifest"],
            "occurrence_packet_sha256": EXPECTED_HASHES["target_occurrences"],
            "affected_statements_sha256": EXPECTED_HASHES["target_statements"],
            "status": target_freeze["status"],
        },
        "phase2_output_hashes": phase2_hashes,
        "source_dependence_caveat": SOURCE_DEPENDENCE,
        "controls": {
            "default": "EXEMPLAR_VALUE_UNKNOWN",
            "formal_link": "FORMAL_LINK_OR_SLOT__ET_OPTIONAL_CONTROL",
            "formal_relation": "FORMAL_RELATION_OR_ENTRY__PER_OPTIONAL_CONTROL",
            "best_tested_mapping": "T004->Frieden__REJECT",
            "person_title_test": "T007->Königin__REJECT",
        },
        "seals": {
            "f84": "SEALED_NOT_ACCESSED",
            "f84r": "SEALED_NOT_ACCESSED",
        },
    }


def prepare_generation() -> tuple[list[str], list[dict[str, str]]]:
    verify_fixed_hashes()
    verify_freeze_chain()
    _, manifest, occurrence_fields, occurrences, _ = verify_targets()
    _, decision_by_id = verify_decisions(manifest)
    return build_expected_occurrence_audit(
        occurrence_fields, occurrences, decision_by_id
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--emit-occurrence-audit",
        action="store_true",
        help="mechanically write the exact 217-row R2 occurrence projection",
    )
    parser.add_argument(
        "--print-validation-json",
        action="store_true",
        help="validate and print the canonical validation JSON",
    )
    args = parser.parse_args()

    if args.emit_occurrence_audit:
        fields, rows = prepare_generation()
        write_tsv(OCCURRENCE_AUDIT, fields, rows)
        print(f"WROTE {OCCURRENCE_AUDIT.name} rows={len(rows)}")
        return 0

    payload = validate_core()
    if args.print_validation_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return 0

    require(VALIDATION.exists(), f"missing validation artifact: {VALIDATION.name}")
    actual_validation = read_json(VALIDATION)
    require(actual_validation == payload, "validation JSON is stale or noncanonical")
    print(
        "PASS V81 R2 Phase 2: "
        f"cards={payload['counts']['target_cards']} "
        f"occurrences={payload['counts']['occurrence_audit_rows']} "
        "PROMOTE=0 NEAR=0 REJECT=30 NEW=NONE"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
