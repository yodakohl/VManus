#!/usr/bin/env python3
"""Validate the complete Pass-1007 template drawer."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
PASS1006 = HERE.parent / "sidequest_semantic_eighteen_page_unified_workshop_edition_one_thousand_sixth"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    source = read_tsv(PASS1006 / "PASS1006_462_UNIFIED_STATEMENT_EDITION.tsv")
    source_pages = read_tsv(PASS1006 / "PASS1006_18_PAGE_SUMMARY.tsv")
    drawer = read_tsv(HERE / "PASS1007_9_CLAUSE_TEMPLATE_DRAWER.tsv")
    assignments = read_tsv(HERE / "PASS1007_462_TEMPLATE_ASSIGNMENTS.tsv")
    profiles = read_tsv(HERE / "PASS1007_18_PAGE_TEMPLATE_PROFILE.tsv")
    summary_path = HERE / "PASS1007_BUILD_SUMMARY.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    manual = (HERE / "PASS1007_APPRENTICE_CLAUSE_MANUAL.md").read_text(encoding="utf-8")
    report = (HERE / "PASS1007_REPORT.md").read_text(encoding="utf-8")

    checks: dict[str, bool] = {}
    checks["9 template rows"] = len(drawer) == 9
    checks["template IDs exact"] = [row["template_id"] for row in drawer] == [f"T{i:02d}" for i in range(1, 10)]
    checks["462 assignments"] = len(assignments) == 462
    checks["assignment IDs unique"] = len({row["statement_id"] for row in assignments}) == 462
    checks["source IDs exact"] = {row["statement_id"] for row in assignments} == {row["statement_id"] for row in source}
    checks["18 page profiles"] = len(profiles) == 18
    checks["page set exact"] = {row["physical_page"] for row in profiles} == {row["physical_page"] for row in source_pages}
    checks["2618 running groups"] = sum(int(row["event_count"]) for row in assignments) == 2618
    checks["event IDs total 2618"] = sum(len(row["event_ids"].split("|")) for row in assignments) == 2618
    all_event_ids = [event for row in assignments for event in row["event_ids"].split("|")]
    checks["event IDs unique"] = len(set(all_event_ids)) == 2618
    checks["all templates used"] = set(row["template_id"] for row in assignments) == {f"T{i:02d}" for i in range(1, 10)}
    expected_counts = {"T01": 78, "T02": 19, "T03": 62, "T04": 30, "T05": 6, "T06": 71, "T07": 101, "T08": 76, "T09": 19}
    checks["template distribution exact"] = Counter(row["template_id"] for row in assignments) == Counter(expected_counts)
    checks["drawer counts agree"] = {row["template_id"]: int(row["statement_count"]) for row in drawer} == expected_counts
    checks["432 closes"] = sum(row["end_style"] == "CLOSE" for row in assignments) == 432
    checks["20 visible boundaries"] = sum(row["end_style"] == "VISIBLE_BOUNDARY" for row in assignments) == 20
    checks["10 open ends"] = sum(row["end_style"] == "OPEN" for row in assignments) == 10
    checks["160 line crossings"] = sum(row["crosses_physical_line"] == "YES" for row in assignments) == 160
    checks["117 exact signatures"] = len({row["canonical_slot_signature"] for row in assignments}) == 117
    checks["all role traces present"] = all(row["event_role_trace"] and row["observed_primary_trace"] for row in assignments)
    checks["all fluent readings retained"] = all(row["fluent_workshop_de"] for row in assignments)
    source_by_id = {row["statement_id"]: row for row in source}
    checks["surface sequence unchanged"] = all(row["surface_sequence"] == source_by_id[row["statement_id"]]["surface_sequence"] for row in assignments)
    checks["fluent reading unchanged"] = all(row["fluent_workshop_de"] == source_by_id[row["statement_id"]]["fluent_workshop_de"] for row in assignments)
    checks["event binding unchanged"] = all(row["event_ids"] == source_by_id[row["statement_id"]]["event_ids"] for row in assignments)
    checks["profile statement sum"] = sum(int(row["statements"]) for row in profiles) == 462
    checks["profile group sum"] = sum(int(row["groups"]) for row in profiles) == 3168
    checks["profile running sum"] = sum(int(row["running_groups"]) for row in profiles) == 2618
    checks["profile address sum"] = sum(int(row["address_or_label_groups"]) for row in profiles) == 550
    zero_pages = {row["physical_page"] for row in profiles if int(row["statements"]) == 0}
    checks["address-only pages exact"] = zero_pages == {"f69v", "f70v"}
    checks["address-only profile exact"] = all(row["template_profile"] == "ADDRESS_ONLY" for row in profiles if row["physical_page"] in zero_pages)
    checks["manual names nine drawers"] = "neun Satzschubladen" in manual and all(f"T{i:02d}" in manual for i in range(1, 10))
    checks["report names all counts"] = all(value in report for value in ["462", "2.618", "550", "432", "20", "10"])
    checks["summary status"] = summary["status"] == "PASS"
    checks["summary counts"] = all([
        summary["templates"] == 9,
        summary["statements"] == 462,
        summary["running_groups"] == 2618,
        summary["exact_slot_signatures"] == 117,
        summary["licensed_closes"] == 432,
        summary["visible_boundaries"] == 20,
        summary["open_ends"] == 10,
        summary["cross_line_statements"] == 160,
        summary["address_or_label_groups_outside_grammar"] == 550,
        summary["new_roots"] == 0,
    ])
    checks["source hash exact"] = summary["source_hash"] == sha256(PASS1006 / "PASS1006_462_UNIFIED_STATEMENT_EDITION.tsv")
    checks["output hashes exact"] = all((HERE / name).exists() and sha256(HERE / name) == digest for name, digest in summary["output_hashes"].items())
    checks["no sealed page values"] = not any(row["physical_page"].startswith("f84") for row in assignments + profiles)

    failures = [name for name, passed in checks.items() if not passed]
    result = {
        "status": "PASS" if not failures else "FAIL",
        "checks_total": len(checks),
        "checks_passed": len(checks) - len(failures),
        "failures": failures,
        "checks": checks,
        "template_statement_counts": dict(sorted(Counter(row["template_id"] for row in assignments).items())),
    }
    (HERE / "PASS1007_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
