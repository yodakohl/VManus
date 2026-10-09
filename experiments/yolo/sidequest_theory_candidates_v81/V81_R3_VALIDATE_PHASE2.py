#!/usr/bin/env python3
"""Validate the complete bounded V81 R3 Phase-2 audit."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
PROTOCOL = BASE.parent / "SIDEQUEST_V81_ATOMIC_CODEBOOK_VOCABULARY_PROTOCOL.md"
SOURCE_INVENTORY = BASE / "V81_R3_SOURCE_INVENTORY.tsv"
SOURCE_REPORT = BASE / "V81_R3_PHASE1_SOURCE_REPORT.md"
SOURCE_FREEZE = BASE / "V81_R3_SOURCE_FREEZE.json"
TARGET_FREEZE = BASE / "V81_TARGET_FREEZE.json"
TARGET_MANIFEST = BASE / "V81_TARGET_MANIFEST.tsv"
TARGET_OCCURRENCES = BASE / "V81_TARGET_OCCURRENCE_PACKET.tsv"
TARGET_STATEMENTS = BASE / "V81_TARGET_AFFECTED_STATEMENTS.tsv"
DECISIONS = BASE / "V81_R3_PHASE2_DECISIONS.tsv"
OCCURRENCE_AUDIT = BASE / "V81_R3_PHASE2_OCCURRENCE_AUDIT.tsv"
STATEMENT_REVISIONS = BASE / "V81_R3_PHASE2_STATEMENT_REVISIONS.tsv"
REPORT = BASE / "V81_R3_PHASE2_REPORT.md"
BUILDER = BASE / "V81_R3_BUILD_PHASE2.py"
VALIDATOR = Path(__file__).resolve()
VALIDATION = BASE / "V81_R3_PHASE2_VALIDATION.json"

EXPECTED_INPUT_HASHES = {
    PROTOCOL: "45ec0cfed64cea2fc4488a89a053fa94e04c320fea321d37f24d4d4821437d92",
    SOURCE_INVENTORY: "6ac100560aa5d0ebba24494cb513972e02a63b809e9d7fd0e2f251c2ae356ac2",
    SOURCE_REPORT: "e3db0da9b9ac864fbc20c753e72f31396b89aefa5bdb15991adf572a2c681153",
    SOURCE_FREEZE: "89faaeb866ced5ac12da4c4e1b214470f81fa7bff5076faa16bf077f3c2376ff",
    TARGET_FREEZE: "76b102a61f30ca9aa507a6c42b5315f6c43e75628d19c0ebe10ef835ec44a06d",
    TARGET_MANIFEST: "c2c2ad1bd6418ed7a332d6ed948192f469ce8fd64e6cd4c5c5c87e33b76e2b04",
    TARGET_OCCURRENCES: "b6cc5afd9421a64aaec6644f095160a42f8e7999bd63ea3151a05860dd9896ee",
    TARGET_STATEMENTS: "8a0b627902605ca59a7f25f1d148d1fdc0b00f63e53a1f5617409e0af25ca2b7",
}

ADVISORY = (
    "DISCLOSED_OLD_V77_LINES__DOCUMENTARY_ELIGIBLE__"
    "STRICT_INDEPENDENCE_ADVISORY"
)

CANDIDATES = {
    "C01_NICCOLO_FORTIBRACCIO": (
        "Niccolo Fortibraccio",
        "SI1_001",
        "NICCOLO FORTIBRACCIO",
    ),
    "C02_DUCA_DI_MILANO": (
        "Duca di Milano",
        "SI1_002",
        "HERZOG VON MAILAND",
    ),
    "C03_SERENISSIMUS": (
        "Serenissimus",
        "SI1_003A|SI1_003B|SI1_003C",
        "HÖCHST DURCHLAUCHT",
    ),
}

ALLOWED_PAGES = {
    "f10r", "f11r", "f55v", "f56r",
    "f81v", "f82r", "f83r",
    "f67r2", "f68r1", "f69v",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        rows = list(reader)
        return list(reader.fieldnames or []), rows


class Audit:
    def __init__(self) -> None:
        self.checks: list[dict[str, object]] = []

    def check(self, name: str, condition: bool, detail: str) -> None:
        self.checks.append(
            {"name": name, "passed": bool(condition), "detail": detail}
        )

    @property
    def passed(self) -> bool:
        return all(bool(item["passed"]) for item in self.checks)


def main() -> int:
    audit = Audit()

    for path, expected in EXPECTED_INPUT_HASHES.items():
        actual = sha256(path) if path.exists() else "MISSING"
        audit.check(
            f"frozen_hash_{path.name}",
            actual == expected,
            f"expected={expected};actual={actual}",
        )

    required_outputs = [
        DECISIONS,
        OCCURRENCE_AUDIT,
        STATEMENT_REVISIONS,
        REPORT,
        BUILDER,
    ]
    audit.check(
        "required_outputs_exist",
        all(path.exists() for path in required_outputs),
        "|".join(path.name for path in required_outputs),
    )
    if not all(path.exists() for path in required_outputs):
        result = build_result(audit, {}, {})
        write_validation(result)
        return 1

    manifest_header, manifest = read_tsv(TARGET_MANIFEST)
    occurrence_header, occurrences = read_tsv(TARGET_OCCURRENCES)
    statement_header, statements = read_tsv(TARGET_STATEMENTS)
    decision_header, decisions = read_tsv(DECISIONS)
    occurrence_audit_header, occurrence_audit = read_tsv(OCCURRENCE_AUDIT)
    revision_header, revisions = read_tsv(STATEMENT_REVISIONS)

    audit.check("target_count_30", len(manifest) == 30, f"actual={len(manifest)}")
    audit.check(
        "visible_occurrence_count_217",
        len(occurrences) == 217,
        f"actual={len(occurrences)}",
    )
    audit.check(
        "affected_statement_count_94",
        len(statements) == 94,
        f"actual={len(statements)}",
    )

    target_ids = [row["anonymous_target_id"] for row in manifest]
    decisions_by_id = {row["anonymous_target_id"]: row for row in decisions}
    audit.check(
        "decision_panel_complete",
        len(decisions) == 30 and set(decisions_by_id) == set(target_ids),
        f"rows={len(decisions)};unique={len(decisions_by_id)}",
    )

    occurrence_counts = Counter(row["anonymous_target_id"] for row in occurrences)
    decision_rows_valid = True
    for target in manifest:
        target_id = target["anonymous_target_id"]
        row = decisions_by_id.get(target_id)
        if row is None:
            decision_rows_valid = False
            continue
        expected_visible = int(target["visible_occurrences"])
        decision_rows_valid &= (
            row["target_rank"] == target["target_rank"]
            and row["joint_tuple_id"] == target["joint_tuple_id"]
            and int(row["visible_occurrences"]) == expected_visible
            and occurrence_counts[target_id] == expected_visible
            and int(row["tested_candidate_occurrences"]) == expected_visible * 3
            and int(row["compatible_candidate_occurrences"]) == 0
            and int(row["improved_complete_statements"]) == 0
            and row["decision"] == "REJECT"
            and row["new_portable_word"] == "NO"
            and row["source_freeze_sha256"] == EXPECTED_INPUT_HASHES[SOURCE_FREEZE]
            and row["source_inventory_sha256"]
            == EXPECTED_INPUT_HASHES[SOURCE_INVENTORY]
            and row["target_freeze_sha256"] == EXPECTED_INPUT_HASHES[TARGET_FREEZE]
            and row["strict_independence_advisory"] == ADVISORY
        )
    audit.check(
        "all_30_decisions_reject_with_zero_improvements",
        decision_rows_valid,
        "all decision gates, hashes, and advisories checked",
    )

    decision_statuses = Counter(row["decision"] for row in decisions)
    audit.check(
        "no_promote_or_near",
        decision_statuses == {"REJECT": 30},
        json.dumps(decision_statuses, sort_keys=True),
    )

    central_occurrences = {
        (
            row["anonymous_target_id"],
            row["occurrence_ordinal"],
            row["event_serial"],
            row["event_id"],
        ): row
        for row in occurrences
    }
    audit_groups: dict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in occurrence_audit:
        key = (
            row["anonymous_target_id"],
            row["occurrence_ordinal"],
            row["event_serial"],
            row["event_id"],
        )
        audit_groups[key].append(row)

    audit.check(
        "occurrence_audit_651_rows",
        len(occurrence_audit) == 651,
        f"actual={len(occurrence_audit)}",
    )
    audit.check(
        "every_central_occurrence_has_three_candidate_audits",
        set(audit_groups) == set(central_occurrences)
        and all(len(rows) == 3 for rows in audit_groups.values()),
        f"central={len(central_occurrences)};audit_groups={len(audit_groups)}",
    )

    copied_fields = [
        "page",
        "record_unit_id",
        "locus",
        "field_id",
        "statement_id",
        "image_owner_id",
        "owner_break_before",
        "source_position_id",
        "autonomous_operational_readback",
        "formal_nonword_channel",
        "master_memorized_selected_token",
        "master_memorized_source_expansion_de",
        "terminal_status",
        "line_crossing",
    ]
    occurrence_rows_valid = True
    for key, rows in audit_groups.items():
        central = central_occurrences.get(key)
        if central is None:
            occurrence_rows_valid = False
            continue
        candidate_ids = {row["candidate_id"] for row in rows}
        occurrence_rows_valid &= candidate_ids == set(CANDIDATES)
        for row in rows:
            expected_candidate = CANDIDATES.get(row["candidate_id"])
            occurrence_rows_valid &= expected_candidate is not None
            if expected_candidate is not None:
                occurrence_rows_valid &= (
                    row["source_entry"] == expected_candidate[0]
                    and row["source_inventory_rows"] == expected_candidate[1]
                    and row["atomic_default_de"] == expected_candidate[2]
                )
            occurrence_rows_valid &= all(row[field] == central[field] for field in copied_fields)
            occurrence_rows_valid &= (
                row["packet_strongest_contradiction"]
                == central["strongest_contradiction"]
                and row["source_category_referent_observed"] == "NO"
                and row["core_sense_usable"] == "NO"
                and row["statement_improved"] == "NO"
                and row["occurrence_decision"] == "REJECT"
                and row["source_freeze_sha256"] == EXPECTED_INPUT_HASHES[SOURCE_FREEZE]
                and row["strict_independence_advisory"] == ADVISORY
            )
    audit.check(
        "all_651_occurrence_rows_exact_and_rejected",
        occurrence_rows_valid,
        "candidate identity, copied packet fields, gates, and seals checked",
    )

    central_statements = {row["statement_id"]: row for row in statements}
    revision_by_id = {row["statement_id"]: row for row in revisions}
    audit.check(
        "statement_revision_panel_complete",
        len(revisions) == 94
        and len(revision_by_id) == 94
        and set(revision_by_id) == set(central_statements),
        f"rows={len(revisions)};unique={len(revision_by_id)}",
    )
    revision_rows_valid = True
    for statement_id, central in central_statements.items():
        row = revision_by_id.get(statement_id)
        if row is None:
            revision_rows_valid = False
            continue
        revision_rows_valid &= (
            row["promoted_or_near_targets"] == "NONE"
            and row["r3_revision_required"] == "NO"
            and row["r3_revised_operational_formal_order"]
            == central["operational_formal_order"]
            and row["r3_revised_continuous_reading_de"]
            == central["master_memorized_statement_content"]
            and row["r3_revision_status"]
            == "UNCHANGED__NO_PROMOTED_OR_NEAR_CANDIDATE"
            and row["source_freeze_sha256"] == EXPECTED_INPUT_HASHES[SOURCE_FREEZE]
            and row["strict_independence_advisory"] == ADVISORY
        )
    audit.check(
        "all_94_statements_unchanged",
        revision_rows_valid,
        "continuous readings and formal order equal the frozen central packet",
    )

    pages = {row["page"] for row in occurrences} | {row["page"] for row in statements}
    audit.check(
        "fixed_pages_only",
        pages <= ALLOWED_PAGES,
        "|".join(sorted(pages)),
    )
    audit.check(
        "sealed_pages_absent",
        "f84" not in pages and "f84r" not in pages,
        "f84=absent;f84r=absent",
    )

    target_freeze = json.loads(TARGET_FREEZE.read_text(encoding="utf-8"))
    audit.check(
        "target_freeze_carries_r3_advisory",
        target_freeze["blinding"]["r3_old_v77_line_incident"]
        == "DISCLOSED__DOCUMENTARY_SOURCE_ELIGIBLE__STRICT_INDEPENDENCE_ADVISORY",
        target_freeze["blinding"]["r3_old_v77_line_incident"],
    )
    audit.check(
        "target_freeze_preserves_seals",
        target_freeze["seals"]
        == {"f84": "SEALED_NOT_ACCESSED", "f84r": "SEALED_NOT_ACCESSED"},
        json.dumps(target_freeze["seals"], sort_keys=True),
    )

    report_text = REPORT.read_text(encoding="utf-8")
    report_markers = [
        "NEW portable word: **NO**",
        "651",
        "94",
        "STRICT_INDEPENDENCE_ADVISORY",
        "T004",
        "CLOSE",
    ]
    audit.check(
        "report_carries_result_counts_rival_and_advisory",
        all(marker in report_text for marker in report_markers),
        "|".join(report_markers),
    )

    forbidden_output_columns = {
        "surface",
        "eva",
        "component_coordinates",
        "page_host_meaning",
    }
    all_output_headers = set(decision_header) | set(occurrence_audit_header) | set(revision_header)
    audit.check(
        "no_surface_or_component_fields_added",
        not (all_output_headers & forbidden_output_columns),
        "intersection=" + "|".join(sorted(all_output_headers & forbidden_output_columns)),
    )

    output_hashes = {
        path.name: sha256(path)
        for path in [
            BUILDER,
            DECISIONS,
            OCCURRENCE_AUDIT,
            STATEMENT_REVISIONS,
            REPORT,
            VALIDATOR,
        ]
    }
    counts = {
        "target_cards": len(decisions),
        "central_occurrences": len(occurrences),
        "source_categories_tested": len(CANDIDATES),
        "candidate_occurrence_audits": len(occurrence_audit),
        "affected_statements_carried": len(revisions),
        "promoted": 0,
        "near": 0,
        "new_portable_words": 0,
    }
    result = build_result(audit, counts, output_hashes)
    write_validation(result)
    print(json.dumps({"status": result["status"], "passed": result["passed"], "total": result["total"]}, sort_keys=True))
    return 0 if audit.passed else 1


def build_result(
    audit: Audit,
    counts: dict[str, int],
    output_hashes: dict[str, str],
) -> dict[str, object]:
    return {
        "schema": "V81_R3_PHASE2_VALIDATION_V1",
        "status": "PASS" if audit.passed else "FAIL",
        "passed": sum(bool(item["passed"]) for item in audit.checks),
        "total": len(audit.checks),
        "checks": audit.checks,
        "counts": counts,
        "input_hashes": {path.name: value for path, value in EXPECTED_INPUT_HASHES.items()},
        "output_hashes": output_hashes,
        "source_freeze_sha256": EXPECTED_INPUT_HASHES[SOURCE_FREEZE],
        "source_inventory_sha256": EXPECTED_INPUT_HASHES[SOURCE_INVENTORY],
        "target_freeze_sha256": EXPECTED_INPUT_HASHES[TARGET_FREEZE],
        "strict_independence_advisory": ADVISORY,
        "documentary_eligibility": "PRESERVED_SEPARATELY_FROM_STRICT_INDEPENDENCE",
        "seals": {
            "f84": "SEALED_NOT_ACCESSED",
            "f84r": "SEALED_NOT_ACCESSED",
        },
        "conclusion": "NO_NEW_PORTABLE_WORD",
    }


def write_validation(result: dict[str, object]) -> None:
    temporary = VALIDATION.with_suffix(VALIDATION.suffix + ".tmp")
    temporary.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(VALIDATION)


if __name__ == "__main__":
    sys.exit(main())
