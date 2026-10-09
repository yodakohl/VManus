#!/usr/bin/env python3
"""Validate only the authorized V81 R1 Phase-2 packet and its frozen inputs."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "experiments/yolo/sidequest_theory_candidates_v81"

PATHS = {
    "protocol": ROOT / "experiments/yolo/SIDEQUEST_V81_ATOMIC_CODEBOOK_VOCABULARY_PROTOCOL.md",
    "source_inventory": BASE / "V81_R1_SOURCE_INVENTORY.tsv",
    "source_report": BASE / "V81_R1_SOURCE_REPORT.md",
    "source_freeze": BASE / "V81_R1_SOURCE_FREEZE.json",
    "target_freeze": BASE / "V81_TARGET_FREEZE.json",
    "target_manifest": BASE / "V81_TARGET_MANIFEST.tsv",
    "target_occurrences": BASE / "V81_TARGET_OCCURRENCE_PACKET.tsv",
    "target_statements": BASE / "V81_TARGET_AFFECTED_STATEMENTS.tsv",
    "decisions": BASE / "V81_R1_30_CARD_DECISIONS.tsv",
    "audit": BASE / "V81_R1_OCCURRENCE_AUDIT.tsv",
    "revisions": BASE / "V81_R1_AFFECTED_STATEMENT_REVISIONS.tsv",
    "report": BASE / "V81_R1_PHASE2_REPORT.md",
    "validator": BASE / "V81_R1_VALIDATE.py",
    "validation": BASE / "V81_R1_VALIDATION.json",
}

EXPECTED_INPUT_HASHES = {
    "protocol": "45ec0cfed64cea2fc4488a89a053fa94e04c320fea321d37f24d4d4821437d92",
    "source_inventory": "9ef4d4e265aa2d39042773b2ffa91a82e01787dfcff93e1a5ab88fc189eeb549",
    "source_report": "0eed2a082f791ba78cc7b2f7d09239bae93b7009aafd568e707303bb9ed41ebe",
    "source_freeze": "fe42fec87f56e88c381e29443abad2654898e350744668c2fde717f0cb497e2a",
    "target_freeze": "76b102a61f30ca9aa507a6c42b5315f6c43e75628d19c0ebe10ef835ec44a06d",
    "target_manifest": "c2c2ad1bd6418ed7a332d6ed948192f469ce8fd64e6cd4c5c5c87e33b76e2b04",
    "target_occurrences": "b6cc5afd9421a64aaec6644f095160a42f8e7999bd63ea3151a05860dd9896ee",
    "target_statements": "8a0b627902605ca59a7f25f1d148d1fdc0b00f63e53a1f5617409e0af25ca2b7",
}

TESTED = {
    "T002": ("C01_QUE_TO_UND", "R1-MO1-002", "Que", "UND", 19),
    "T008": ("C02_QUI_TO_HIER", "R1-MO1-003", "Qui", "HIER", 10),
    "T010": ("C03_E_DUPLICATUM_TO_DOPPELT", "R1-MO1-005", "e duplicatum", "DOPPELT", 9),
    "T014": ("C04_S_DUPLICATUM_TO_WIEDERHOLEN", "R1-MO1-006", "s duplicatum", "WIEDERHOLEN", 7),
    "T026": ("C05_QUO_TO_WOHIN", "R1-MO1-004", "Quo", "WOHIN", 3),
}

FORMAL_CONTROLS = {
    "T001": "RETAIN_FORMAL_PARAMETER_CHANNEL",
    "T002": "RETAIN_FORMAL_LINK_OR_SLOT__ET_OPTIONAL",
    "T010": "RETAIN_FORMAL_RELATION_OR_ENTRY__PER_OPTIONAL",
    "T016": "RETAIN_FORMAL_RELATION_SLOT_CHANNEL",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        rows = list(reader)
        return list(reader.fieldnames or []), rows


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


class Checks:
    def __init__(self) -> None:
        self.passed = 0
        self.failed: list[str] = []

    def require(self, condition: bool, label: str) -> None:
        if condition:
            self.passed += 1
        else:
            self.failed.append(label)


def main() -> int:
    checks = Checks()

    for name, path in PATHS.items():
        checks.require(path.is_file(), f"missing_file:{name}:{path}")
    if checks.failed:
        print(json.dumps({"status": "FAIL", "passed": checks.passed, "failed": checks.failed}, indent=2))
        return 1

    for name, expected in EXPECTED_INPUT_HASHES.items():
        checks.require(sha256(PATHS[name]) == expected, f"input_hash_mismatch:{name}")

    source_freeze = read_json(PATHS["source_freeze"])
    target_freeze = read_json(PATHS["target_freeze"])
    validation = read_json(PATHS["validation"])

    checks.require(source_freeze.get("status") == "FROZEN_BEFORE_V81_TARGET_MANIFEST", "source_freeze_status")
    checks.require(source_freeze.get("target_manifest_opened") is False, "phase1_target_flag_changed")
    checks.require(source_freeze.get("inventory", {}).get("sha256") == EXPECTED_INPUT_HASHES["source_inventory"], "source_inventory_binding")
    checks.require(source_freeze.get("source_report", {}).get("sha256") == EXPECTED_INPUT_HASHES["source_report"], "source_report_binding")
    checks.require(target_freeze.get("status") == "PASS__FROZEN_AFTER_FOUR_SOURCE_FIRST_FREEZES", "target_freeze_status")
    checks.require(target_freeze.get("source_freeze_hashes", {}).get("R1") == EXPECTED_INPUT_HASHES["source_freeze"], "central_r1_freeze_binding")
    checks.require(target_freeze.get("source_inventory_hashes", {}).get("R1") == EXPECTED_INPUT_HASHES["source_inventory"], "central_r1_inventory_binding")
    checks.require(target_freeze.get("output_hashes", {}).get("V81_TARGET_MANIFEST.tsv") == EXPECTED_INPUT_HASHES["target_manifest"], "central_manifest_binding")
    checks.require(target_freeze.get("output_hashes", {}).get("V81_TARGET_OCCURRENCE_PACKET.tsv") == EXPECTED_INPUT_HASHES["target_occurrences"], "central_occurrence_binding")
    checks.require(target_freeze.get("output_hashes", {}).get("V81_TARGET_AFFECTED_STATEMENTS.tsv") == EXPECTED_INPUT_HASHES["target_statements"], "central_statement_binding")
    checks.require(target_freeze.get("seals", {}).get("f84") == "SEALED_NOT_ACCESSED", "central_f84_seal")
    checks.require(target_freeze.get("seals", {}).get("f84r") == "SEALED_NOT_ACCESSED", "central_f84r_seal")

    source_header, source_rows = read_tsv(PATHS["source_inventory"])
    manifest_header, manifest_rows = read_tsv(PATHS["target_manifest"])
    occurrence_header, occurrence_rows = read_tsv(PATHS["target_occurrences"])
    statement_header, statement_rows = read_tsv(PATHS["target_statements"])
    decision_header, decision_rows = read_tsv(PATHS["decisions"])
    audit_header, audit_rows = read_tsv(PATHS["audit"])
    revision_header, revision_rows = read_tsv(PATHS["revisions"])

    checks.require(len(source_rows) == 6, "source_row_count")
    checks.require(all(row["row_status"] == "EXACT_ENTRY_CODE_PAIR" for row in source_rows), "source_exact_pair_statuses")
    source_ids = {row["row_id"] for row in source_rows}
    checks.require(source_ids == {f"R1-MO1-{i:03d}" for i in range(1, 7)}, "source_row_ids")

    manifest_by_id = {row["anonymous_target_id"]: row for row in manifest_rows}
    occurrence_by_event = {row["event_id"]: row for row in occurrence_rows}
    decision_by_id = {row["anonymous_target_id"]: row for row in decision_rows}
    expected_ids = {f"T{i:03d}" for i in range(1, 31)}

    checks.require(len(manifest_rows) == 30 and set(manifest_by_id) == expected_ids, "manifest_30_targets")
    checks.require(len(occurrence_rows) == 217, "occurrence_count_217")
    checks.require(sum(int(row["source_position_contribution"]) for row in occurrence_rows) == 216, "independent_positions_216")
    checks.require(len(statement_rows) == 94, "affected_statement_count_94")
    checks.require(len({row["statement_id"] for row in statement_rows}) == 94, "affected_statement_ids_unique")

    occurrence_counts = Counter(row["anonymous_target_id"] for row in occurrence_rows)
    independent_counts = Counter()
    for row in occurrence_rows:
        independent_counts[row["anonymous_target_id"]] += int(row["source_position_contribution"])
    for target_id, manifest in manifest_by_id.items():
        checks.require(occurrence_counts[target_id] == int(manifest["visible_occurrences"]), f"manifest_occurrence_count:{target_id}")
        checks.require(independent_counts[target_id] == int(manifest["independent_source_positions"]), f"manifest_independent_count:{target_id}")

    checks.require(len(decision_rows) == 30 and set(decision_by_id) == expected_ids, "decision_30_targets")
    checks.require(all(row["decision"] == "REJECT" for row in decision_rows), "all_new_word_decisions_reject")
    checks.require(not any(row["decision"] in {"PROMOTE", "NEAR"} for row in decision_rows), "zero_promote_near")
    checks.require(all(row["reason"] and row["strongest_contradiction_or_repair"] for row in decision_rows), "decision_reasons_complete")
    checks.require(all(0 <= int(row["ordinary_word_count"]) <= 3 for row in decision_rows), "atomic_word_count_ceiling")

    for target_id, decision in decision_by_id.items():
        manifest = manifest_by_id[target_id]
        for field in ("target_rank", "joint_tuple_id", "visible_occurrences", "independent_source_positions", "distinct_pages", "distinct_records"):
            checks.require(decision[field] == manifest[field], f"decision_manifest_field:{target_id}:{field}")
        if decision["historical_row_id"] != "NONE":
            checks.require(decision["historical_row_id"] in source_ids, f"unknown_historical_row:{target_id}")

    tested_decisions = {row["anonymous_target_id"] for row in decision_rows if row["tested_candidate"] == "true"}
    checks.require(tested_decisions == set(TESTED), "tested_target_set")
    for target_id, baseline in FORMAL_CONTROLS.items():
        checks.require(decision_by_id[target_id]["baseline_disposition"] == baseline, f"formal_control:{target_id}")

    expected_audit_events = {
        row["event_id"]
        for row in occurrence_rows
        if row["anonymous_target_id"] in TESTED
    }
    actual_audit_events = {row["event_id"] for row in audit_rows}
    checks.require(len(audit_rows) == 48, "audit_row_count_48")
    checks.require(len(actual_audit_events) == 48, "audit_event_ids_unique")
    checks.require(actual_audit_events == expected_audit_events, "all_tested_occurrences_audited")
    checks.require(all(row["occurrence_decision"] == "REJECT" for row in audit_rows), "audit_all_reject")
    checks.require(Counter(row["anonymous_target_id"] for row in audit_rows) == Counter({key: value[4] for key, value in TESTED.items()}), "audit_candidate_counts")

    copied_fields = (
        "anonymous_target_id",
        "occurrence_ordinal",
        "event_id",
        "page",
        "record_unit_id",
        "locus",
        "field_id",
        "statement_id",
        "source_position_id",
        "source_position_contribution",
        "terminal_status",
        "strongest_contradiction",
    )
    for row in audit_rows:
        source = occurrence_by_event[row["event_id"]]
        for field in copied_fields:
            checks.require(row[field] == source[field], f"audit_copy:{row['event_id']}:{field}")
        checks.require(row["baseline_readback"] == source["autonomous_operational_readback"], f"audit_readback:{row['event_id']}")
        checks.require(row["master_source_expansion_de"] == source["master_memorized_source_expansion_de"], f"audit_expansion:{row['event_id']}")
        candidate_id, row_id, entry, category, _ = TESTED[row["anonymous_target_id"]]
        checks.require(row["candidate_id"] == candidate_id, f"audit_candidate_id:{row['event_id']}")
        checks.require(row["historical_row_id"] == row_id, f"audit_source_row:{row['event_id']}")
        checks.require(row["exact_source_entry"] == entry, f"audit_source_entry:{row['event_id']}")
        checks.require(row["proposed_atomic_category_de"] == category, f"audit_category:{row['event_id']}")

    checks.require(len(revision_rows) == 0, "zero_revision_rows_when_no_promote_near")
    checks.require(bool(revision_header), "revision_header_present")
    forbidden_header_fragments = ("surface", "eva", "component_coordinate", "spelling")
    output_headers = [name.lower() for name in decision_header + audit_header + revision_header]
    checks.require(not any(fragment in name for fragment in forbidden_header_fragments for name in output_headers), "no_surface_or_component_output_fields")

    checks.require(validation.get("status") == "PASS", "validation_status")
    checks.require(validation.get("new_portable_word_survives") is False, "validation_zero_survivor")
    checks.require(validation.get("counts", {}).get("target_cards") == 30, "validation_target_count")
    checks.require(validation.get("counts", {}).get("visible_occurrences") == 217, "validation_occurrence_count")
    checks.require(validation.get("counts", {}).get("independent_source_positions") == 216, "validation_position_count")
    checks.require(validation.get("counts", {}).get("tested_candidate_occurrences_audited") == 48, "validation_audit_count")
    checks.require(validation.get("counts", {}).get("promoted") == 0, "validation_promoted_zero")
    checks.require(validation.get("counts", {}).get("near") == 0, "validation_near_zero")
    checks.require(validation.get("counts", {}).get("affected_statement_revisions") == 0, "validation_revision_zero")
    checks.require(validation.get("seals", {}).get("f84") == "SEALED_NOT_ACCESSED", "validation_f84_seal")
    checks.require(validation.get("seals", {}).get("f84r") == "SEALED_NOT_ACCESSED", "validation_f84r_seal")
    checks.require(validation.get("blinding", {}).get("sibling_outputs_opened") is False, "validation_sibling_blind")
    checks.require(validation.get("blinding", {}).get("v80_directly_opened") is False, "validation_v80_blind")
    checks.require(validation.get("blinding", {}).get("manuscript_pages_images_or_transcriptions_opened") is False, "validation_manuscript_blind")

    for name, expected in validation.get("input_hashes", {}).items():
        checks.require(name in EXPECTED_INPUT_HASHES and expected == EXPECTED_INPUT_HASHES[name], f"validation_input_hash:{name}")
    for name, expected in validation.get("output_hashes", {}).items():
        checks.require(name in PATHS and sha256(PATHS[name]) == expected, f"validation_output_hash:{name}")

    result = {
        "status": "PASS" if not checks.failed else "FAIL",
        "passed": checks.passed,
        "failed_count": len(checks.failed),
        "failed": checks.failed,
        "counts": {
            "target_cards": len(decision_rows),
            "visible_occurrences": len(occurrence_rows),
            "independent_source_positions": sum(int(row["source_position_contribution"]) for row in occurrence_rows),
            "tested_candidate_occurrences_audited": len(audit_rows),
            "affected_statement_revisions": len(revision_rows),
            "promoted": sum(row["decision"] == "PROMOTE" for row in decision_rows),
            "near": sum(row["decision"] == "NEAR" for row in decision_rows),
        },
        "new_portable_word_survives": False,
        "seals": {"f84": "SEALED_NOT_ACCESSED", "f84r": "SEALED_NOT_ACCESSED"},
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not checks.failed else 1


if __name__ == "__main__":
    sys.exit(main())
