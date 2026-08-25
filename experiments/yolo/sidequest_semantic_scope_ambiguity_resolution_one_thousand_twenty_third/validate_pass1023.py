#!/usr/bin/env python3
"""Consistency checks for the integrated Pass-1023 scope edition."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent
P1022 = OUT.parent / "sidequest_semantic_argument_scope_stack_one_thousand_twenty_second"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    checks: dict[str, object] = {}

    source_attachments = read_tsv(P1022 / "SCOPE_STACK_ATTACHMENTS.tsv")
    source_ambiguities = read_tsv(P1022 / "SCOPE_STACK_AMBIGUITIES.tsv")
    source_statements = read_tsv(P1022 / "PASS1022_627_STATEMENT_SCOPE_EDITION.tsv")
    resolved = read_tsv(OUT / "PASS1023_328_RESOLVED_ATTACHMENTS.tsv")
    full = read_tsv(OUT / "PASS1023_4345_SCOPE_ATTACHMENTS.tsv")
    statements = read_tsv(OUT / "PASS1023_627_STATEMENT_SCOPE_EDITION.tsv")
    rules = read_tsv(OUT / "PASS1023_SIX_SCOPE_RULES.tsv")
    generalization = read_tsv(OUT / "EQUAL_DISTANCE_GENERALIZATION_AUDIT.tsv")

    checks["source_counts"] = [len(source_attachments), len(source_ambiguities), len(source_statements)] == [4345, 329, 627]
    checks["release_counts"] = [len(resolved), len(full), len(statements), len(rules)] == [328, 4345, 627, 6]
    checks["unique_resolution_ids"] = len({row["resolution_id"] for row in resolved}) == 328
    checks["unique_attachment_ids"] = len({row["attachment_id"] for row in full}) == 4345
    checks["unique_statement_ids"] = len({row["statement_id"] for row in statements}) == 627

    source_by_attachment = {row["attachment_id"]: row for row in source_attachments}
    full_by_attachment = {row["attachment_id"]: row for row in full}
    checks["attachment_inventory_preserved"] = set(source_by_attachment) == set(full_by_attachment)
    checks["attachment_identity_preserved"] = all(
        all(
            source_by_attachment[key][field] == full_by_attachment[key][field]
            for field in ["focus_core", "focus_value_de", "event_id", "statement_id", "surface_card", "component_recipe"]
        )
        for key in source_by_attachment
    )

    source_amb_ids = {row["ambiguity_id"] for row in source_ambiguities}
    release_amb_ids = [
        ambiguity_id
        for row in resolved
        for ambiguity_id in row["ambiguity_ids"].split("|")
    ]
    checks["all_329_ambiguity_rows_consumed_once"] = (
        len(release_amb_ids) == 329
        and len(set(release_amb_ids)) == 329
        and set(release_amb_ids) == source_amb_ids
    )
    checks["all_328_attachments_resolved"] = (
        len({row["attachment_id"] for row in source_ambiguities}) == 328
        and {row["attachment_id"] for row in resolved}
        == {row["attachment_id"] for row in source_ambiguities}
        and all(row["resolution_status"] == "SELECTED_WORKSHOP_SCOPE" for row in resolved)
    )
    checks["no_empty_final_selection"] = all(
        row["pass1023_selected_target_de"] and row["pass1023_scope_de"]
        for row in resolved
    )
    checks["full_status_partition"] = Counter(row["pass1023_resolution_status"] for row in full) == Counter(
        {"ALREADY_UNAMBIGUOUS": 4017, "RESOLVED_BY_WORKSHOP_RULE": 328}
    )
    checks["changed_attachment_count"] = sum(row["changed_from_pass1022"] == "YES" for row in resolved) == 143
    checks["no_open_statement_scope"] = all(
        row["pass1023_scope_result"] == "COMPLETE_SELECTED_SCOPE__NO_OPEN_ATTACHMENTS"
        for row in statements
    )
    checks["statement_resolution_sum"] = sum(
        int(row["pass1023_resolved_attachment_count"]) for row in statements
    ) == 328
    checks["statement_changed_sum"] = sum(
        int(row["pass1023_changed_attachment_count"]) for row in statements
    ) == 143

    decision_counts = Counter(
        decision
        for row in resolved
        for decision in row["pass1023_decisions"].split("+")
    )
    checks["decision_counts"] = decision_counts == Counter(
        {
            "BOUNDED_FORWARD": 127,
            "EQUAL_LEFT": 119,
            "EQUAL_RIGHT": 1,
            "OWNER_ONLY": 19,
            "R_HEAD": 46,
            "R_NESTED": 1,
            "R_TAIL": 16,
        }
    )
    overlap = [row for row in resolved if "|" in row["ambiguity_classes"]]
    checks["sole_overlap_consistent"] = (
        len(overlap) == 1
        and overlap[0]["attachment_id"] == "SA03062"
        and "R=MARKIEREN" in overlap[0]["pass1023_selected_target_de"]
    )
    checks["fixed_values_unchanged"] = all(
        source_by_attachment[row["attachment_id"]]["focus_value_de"] == row["focus_value_de"]
        for row in resolved
    )
    checks["generalization_inventory"] = (
        len(generalization) == 4345
        and {row["attachment_id"] for row in generalization} == set(source_by_attachment)
    )
    checks["blanket_left_rule_rejected"] = Counter(
        row["strict_rule_verdict"] for row in generalization
    ) == Counter(
        {
            "CONSISTENT": 2859,
            "OUTSIDE_LOCAL_RULE": 1454,
            "POSITIONALLY_UNRESOLVED_SAME_VALUE": 28,
            "CLEAR_CONTRADICTION": 4,
        }
    )
    checks["nearest_safe_rule_matches_all_local_tests"] = Counter(
        row["safe_trace_match"] for row in generalization
    ) == Counter({"MATCH": 3100, "NOT_LOCALLY_TESTED": 1245})

    outputs = [
        OUT / "PASS1023_328_RESOLVED_ATTACHMENTS.tsv",
        OUT / "PASS1023_4345_SCOPE_ATTACHMENTS.tsv",
        OUT / "PASS1023_627_STATEMENT_SCOPE_EDITION.tsv",
        OUT / "PASS1023_SIX_SCOPE_RULES.tsv",
        OUT / "PASS1023_BUILD_SUMMARY.json",
    ]
    before = {path.name: sha(path) for path in outputs}
    subprocess.run([sys.executable, str(OUT / "build_pass1023.py")], check=True)
    after = {path.name: sha(path) for path in outputs}
    checks["deterministic_rebuild"] = before == after

    failed = [name for name, value in checks.items() if value is not True]
    result = {
        "result": "PASS" if not failed else "FAIL",
        "check_count": len(checks),
        "failed_checks": failed,
        "checks": checks,
        "output_hashes": after,
    }
    (OUT / "PASS1023_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if failed:
        raise SystemExit("failed: " + ", ".join(failed))


if __name__ == "__main__":
    main()
