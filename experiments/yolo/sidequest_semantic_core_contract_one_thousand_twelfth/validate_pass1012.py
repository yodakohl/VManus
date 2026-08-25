#!/usr/bin/env python3
"""Validate the constrained Pass-1012 semantic contract."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CODEBOOK = (
    ROOT
    / "experiments/yolo/sidequest_semantic_ot_grade_and_concept_review_one_thousand_tenth"
    / "PASS1010_175_GRADE_REVISED_CODEBOOK.tsv"
)
SOURCE = (
    ROOT
    / "experiments/yolo/sidequest_semantic_manual_optical_passage_audit_one_thousand_eleventh"
    / "PASS1011_627_OPTICALLY_REPAIRED_STATEMENTS.tsv"
)
CONTRACT = HERE / "PASS1012_56_SIGN_SEMANTIC_CONTRACT.tsv"
COMPOSITIONS = HERE / "PASS1012_102_COMPOSITION_CONTRACTS.tsv"
PRESSURE = HERE / "PASS1012_627_SEMANTIC_PRESSURE_MAP.tsv"
SUMMARY = HERE / "PASS1012_BUILD_SUMMARY.json"
OUTPUT = HERE / "PASS1012_VALIDATION.json"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    codebook = rows(CODEBOOK)
    source = rows(SOURCE)
    contract = rows(CONTRACT)
    compositions = rows(COMPOSITIONS)
    pressure = rows(PRESSURE)
    root_rows = [row for row in codebook if row["teaching_unit_id"].startswith("R-")]
    source_by_id = {row["statement_id"]: row for row in source}
    pressure_by_id = {row["statement_id"]: row for row in pressure}
    checks: dict[str, bool] = {}

    checks["codebook_175"] = len(codebook) == 175
    checks["root_entries_56"] = len(root_rows) == 56
    checks["contract_56"] = len(contract) == 56
    checks["unique_contract_signs"] = len({row["sign"] for row in contract}) == 56
    checks["contract_matches_codebook_signs"] = {
        row["sign"] for row in contract
    } == {row["recognition_forms"] for row in root_rows}
    checks["one_core_value_each"] = all(row["single_core_value_de"].strip() for row in contract)
    checks["one_forbidden_rescue_each"] = all(row["forbidden_rescue_de"].strip() for row in contract)
    checks["one_forward_rule_each"] = all(row["forward_rule_de"].strip() for row in contract)
    checks["contract_class_counts"] = Counter(row["pass1012_class"] for row in contract) == Counter(
        {
            "PORTABLE_CORE_MEANING": 18,
            "FORMAL_CONTROL_NOT_CONTENT_WORD": 8,
            "SPECIALIST_MEANING_CANDIDATE": 11,
            "LOCAL_ADDRESS_OR_MEMORIZED_SIGN": 19,
        }
    )
    checks["semantic_kind_counts"] = Counter(row["semantic_kind"] for row in contract) == Counter(
        {
            "CONTENT_OR_OPERATION_CORE": 12,
            "REFERENT_SEQUENCE_OR_RELATION_CORE": 6,
            "GRADE_BOUNDARY_OR_ENTRY_CONTROL": 8,
            "SPECIALIST_OPERATION_CANDIDATE": 11,
            "LOCAL_SIGN_OR_ADDRESS": 19,
        }
    )
    checks["portable_core_exact_inventory"] = {
        row["sign"] for row in contract if row["pass1012_class"] == "PORTABLE_CORE_MEANING"
    } == {
        "Y", "OK", "OL", "OT", "AL", "CH", "SH", "AR", "K", "AIIN", "S", "CHD",
        "OR", "L", "T", "AIN", "R", "P",
    }
    checks["formal_exact_inventory"] = {
        row["sign"] for row in contract if row["pass1012_class"] == "FORMAL_CONTROL_NOT_CONTENT_WORD"
    } == {"E", "EE", "EEE", "DY", "O", "CARRIER_Q", "IIN", "DA"}
    checks["specialist_exact_inventory"] = {
        row["sign"] for row in contract if row["pass1012_class"] == "SPECIALIST_MEANING_CANDIDATE"
    } == {"CTH", "SHED", "CKH", "CHEO", "AIR", "CHK", "SOLK", "LSH", "CPH", "CFH", "LD"}

    checks["compositions_102"] = len(compositions) == 102
    checks["formula_cards_30"] = sum(row["unit_type"] == "FORMULA_CARD" for row in compositions) == 30
    checks["contextual_compositions_72"] = sum(
        row["unit_type"] == "CONTEXTUAL_COMPOSITION_NOT_NEW_WORD" for row in compositions
    ) == 72
    checks["composition_decisions"] = Counter(row["composition_decision"] for row in compositions) == Counter(
        {
            "PORTABLE_COMPOSITION": 73,
            "SPECIALIST_COMPOSITION_CANDIDATE": 19,
            "LOCAL_COMPOSITION_ONLY": 9,
            "FORMAL_COMPOSITION_ONLY": 1,
        }
    )
    checks["formula_decisions"] = Counter(
        row["composition_decision"] for row in compositions if row["unit_type"] == "FORMULA_CARD"
    ) == Counter(
        {
            "PORTABLE_COMPOSITION": 25,
            "SPECIALIST_COMPOSITION_CANDIDATE": 4,
            "LOCAL_COMPOSITION_ONLY": 1,
        }
    )
    contextual = [
        row for row in compositions if row["unit_type"] == "CONTEXTUAL_COMPOSITION_NOT_NEW_WORD"
    ]
    checks["all_72_context_expansions_withdrawn"] = all(
        row["local_expansion_status"]
        == "WITHDRAW_AS_PORTABLE_MEANING_KEEP_ONLY_OWNER_BOUND_PARAPHRASE"
        for row in contextual
    )
    checks["composition_readings_nonempty"] = all(
        row["pass1012_contract_reading_de"].strip() for row in compositions
    )
    checks["composition_recipes_nonempty"] = all(row["component_recipes"].strip() for row in compositions)

    checks["source_627"] = len(source) == 627
    checks["pressure_627"] = len(pressure) == 627
    checks["pressure_unique_ids"] = len(pressure_by_id) == 627
    checks["pressure_same_ids"] = set(pressure_by_id) == set(source_by_id)
    checks["pressure_order_preserved"] = [row["statement_id"] for row in pressure] == [
        row["statement_id"] for row in source
    ]
    preserved = [
        "book_statement_ordinal",
        "statement_id",
        "physical_page",
        "register",
        "owner_id",
        "locus_span",
        "surface_sequence",
        "component_sequence",
        "event_ids",
        "optically_revised_translation",
    ]
    checks["source_binding_preserved"] = all(
        all(pressure_by_id[sid][field] == source_by_id[sid][field] for field in preserved)
        for sid in source_by_id
    )
    checks["event_total_3888"] = sum(int(row["event_count"]) for row in pressure) == 3888
    checks["event_class_total_3888"] = sum(
        int(row[field])
        for row in pressure
        for field in (
            "portable_event_count",
            "formal_only_event_count",
            "specialist_event_count",
            "local_event_count",
        )
    ) == 3888
    event_classes = Counter(
        {
            "PORTABLE_CORE_COMPOSITION": sum(int(row["portable_event_count"]) for row in pressure),
            "FORMAL_CONTROL_ONLY": sum(int(row["formal_only_event_count"]) for row in pressure),
            "SPECIALIST_CANDIDATE_DEPENDENT": sum(int(row["specialist_event_count"]) for row in pressure),
            "LOCAL_OWNER_DEPENDENT": sum(int(row["local_event_count"]) for row in pressure),
        }
    )
    checks["event_class_counts"] = event_classes == Counter(
        {
            "PORTABLE_CORE_COMPOSITION": 2851,
            "FORMAL_CONTROL_ONLY": 55,
            "SPECIALIST_CANDIDATE_DEPENDENT": 498,
            "LOCAL_OWNER_DEPENDENT": 484,
        }
    )
    checks["statement_status_counts"] = Counter(
        row["pass1012_statement_status"] for row in pressure
    ) == Counter(
        {
            "PORTABLE_CORE_READABLE": 274,
            "SPECIALIST_CANDIDATE_REQUIRED": 144,
            "LOCAL_OWNER_REQUIRED": 208,
            "FORMAL_CONTROL_ONLY": 1,
        }
    )
    checks["contract_literals_nonempty"] = all(row["contract_literal_de"].strip() for row in pressure)
    checks["working_translations_nonempty"] = all(
        row["pass1012_working_translation_de"].strip() for row in pressure
    )
    checks["manual_repairs_35"] = sum(
        row["working_translation_status"] == "MANUAL_IMAGE_REPAIR" for row in pressure
    ) == 35
    checks["legacy_unreviewed_592"] = sum(
        row["working_translation_status"] == "LEGACY_FLUENT_READING_NOT_YET_MANUALLY_REPAIRED"
        for row in pressure
    ) == 592
    checks["reports_exist"] = all(
        (HERE / name).is_file()
        for name in ("PASS1012_REPORT.md", "PASS1012_APPRENTICE_CORE_SHEET.md")
    )
    checks["no_absolute_workspace_path"] = all(
        str(ROOT) not in path.read_text(encoding="utf-8")
        for path in (CONTRACT, COMPOSITIONS, PRESSURE, HERE / "PASS1012_REPORT.md")
    )

    tracked = (CONTRACT, COMPOSITIONS, PRESSURE, SUMMARY)
    before = {path.name: sha256(path) for path in tracked}
    subprocess.run(["python3", str(HERE / "build_pass1012.py")], cwd=ROOT, check=True)
    after = {path.name: sha256(path) for path in tracked}
    checks["deterministic_rebuild"] = before == after

    result = {
        "pass": 1012,
        "status": "PASS" if all(checks.values()) else "FAIL",
        "check_count": len(checks),
        "checks": checks,
        "counts": {
            "sign_entries": len(contract),
            "composition_units": len(compositions),
            "statements": len(pressure),
            "events": sum(int(row["event_count"]) for row in pressure),
            "contextual_expansions_withdrawn": len(contextual),
        },
    }
    OUTPUT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise SystemExit("validation failed: " + ", ".join(failed))
    print(f"PASS {len(checks)}/{len(checks)}")


if __name__ == "__main__":
    main()
