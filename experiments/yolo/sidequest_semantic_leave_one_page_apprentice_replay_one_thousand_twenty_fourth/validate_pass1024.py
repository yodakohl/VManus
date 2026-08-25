#!/usr/bin/env python3
"""Consistency checks for the Pass-1024 twenty-two-door replay."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    attachments = read_tsv(OUT / "PASS1024_4345_ATTACHMENT_REPLAY.tsv")
    events = read_tsv(OUT / "PASS1024_3888_EVENT_REPLAY.tsv")
    pages = read_tsv(OUT / "PASS1024_22_PAGE_REPLAY.tsv")
    rules = read_tsv(OUT / "PASS1024_RULE_SUPPORT.tsv")
    micro = read_tsv(OUT / "PASS1024_MICROFORM_SUPPORT.tsv")

    checks: dict[str, bool] = {}
    checks["release_counts"] = [len(attachments), len(events), len(pages), len(rules)] == [4345, 3888, 22, 9]
    checks["unique_attachment_ids"] = len({row["attachment_id"] for row in attachments}) == 4345
    checks["unique_event_ids"] = len({row["event_id"] for row in events}) == 3888
    checks["unique_pages"] = len({row["physical_page"] for row in pages}) == 22
    checks["visible_group_partition"] = sum(int(row["visible_group_count"]) for row in pages) == 4581
    checks["running_event_partition"] = sum(int(row["running_event_count"]) for row in pages) == 3888
    checks["local_group_partition"] = sum(int(row["local_address_or_label_count"]) for row in pages) == 693
    checks["statement_partition"] = sum(int(row["statement_count"]) for row in pages) == 627
    checks["attachment_partition"] = sum(int(row["focus_attachment_count"]) for row in pages) == 4345
    checks["direct_stack_partition"] = (
        sum(int(row["direct_local_attachment_count"]) for row in pages) == 3100
        and sum(int(row["owner_package_stack_attachment_count"]) for row in pages) == 1245
    )
    checks["resolved_changed_partition"] = (
        sum(int(row["pass1023_resolved_attachment_count"]) for row in pages) == 328
        and sum(int(row["pass1023_changed_attachment_count"]) for row in pages) == 143
    )
    checks["all_atoms_on_sheet"] = all(row["all_atoms_on_apprentice_sheet"] == "YES" for row in events)
    checks["all_coarse_rules_cross_page"] = (
        all(row["survives_every_page_holdout"] == "YES" for row in rules)
        and all(int(row["support_page_count"]) >= 2 for row in rules)
        and all(row["unsupported_rule_families_when_page_held"] == "NONE" for row in pages)
    )
    checks["two_label_only_pages"] = {
        row["physical_page"]
        for row in pages
        if row["leave_one_page_replay_result"] == "LOCAL_ADDRESS_COPY_ONLY"
    } == {"f69v", "f70v"}
    checks["page_private_microforms_are_covered"] = (
        {row["micro_signature"] for row in micro if row["page_private_microform"] == "YES"}
        == {"AL_AR_RIGHT_FALLBACK_NO_LEFT", "EQUAL_LEFT+R_HEAD", "EQUAL_RIGHT", "R_NESTED"}
        and all(row["covered_by_cross_page_rule_family"] == "YES" for row in micro)
    )
    checks["page_result_partition"] = Counter(row["leave_one_page_replay_result"] for row in pages) == Counter(
        {
            "RULE_FAMILIES_TRANSFER_DIRECTLY": 17,
            "RULE_FAMILIES_TRANSFER__NEW_MICROFORM_COVERED": 3,
            "LOCAL_ADDRESS_COPY_ONLY": 2,
        }
    )
    checks["no_private_coarse_rule"] = all(row["replay_result"] == "TRANSFERRED_RULE_FAMILY" for row in attachments)
    checks["surface_recipe_counts"] = (
        sum(row["surface_page_private"] == "YES" for row in events) == 1029
        and sum(row["recipe_page_private"] == "YES" for row in events) == 548
    )

    outputs = [
        OUT / "PASS1024_4345_ATTACHMENT_REPLAY.tsv",
        OUT / "PASS1024_3888_EVENT_REPLAY.tsv",
        OUT / "PASS1024_22_PAGE_REPLAY.tsv",
        OUT / "PASS1024_RULE_SUPPORT.tsv",
        OUT / "PASS1024_MICROFORM_SUPPORT.tsv",
        OUT / "PASS1024_BUILD_SUMMARY.json",
    ]
    before = {path.name: sha(path) for path in outputs}
    subprocess.run([sys.executable, str(OUT / "build_pass1024.py")], check=True)
    after = {path.name: sha(path) for path in outputs}
    checks["deterministic_rebuild"] = before == after

    failed = [name for name, value in checks.items() if not value]
    result = {
        "result": "PASS" if not failed else "FAIL",
        "check_count": len(checks),
        "failed_checks": failed,
        "checks": checks,
        "output_hashes": after,
    }
    (OUT / "PASS1024_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if failed:
        raise SystemExit("failed: " + ", ".join(failed))


if __name__ == "__main__":
    main()
