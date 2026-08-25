#!/usr/bin/env python3
"""Validate the unified Pass 1006 release."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE_CODEBOOK = (
    ROOT
    / "experiments/yolo/sidequest_semantic_dual_layer_release_one_thousand_second"
    / "PASS1002_175_CURRENT_CODEBOOK.tsv"
)


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    statements = read("PASS1006_462_UNIFIED_STATEMENT_EDITION.tsv")
    events = read("PASS1006_3168_UNIFIED_EVENT_LEDGER.tsv")
    addresses = read("PASS1006_550_LOCAL_ADDRESS_LEDGER.tsv")
    codebook = read("PASS1006_175_APPRENTICE_CODEBOOK.tsv")
    allographs = read("PASS1006_5_SCRIBE_ALLOGRAPH_RULES.tsv")
    compositions = read("PASS1006_29_NEW_COMPOSITION_APPENDIX.tsv")
    pages = read("PASS1006_18_PAGE_SUMMARY.tsv")
    summary = json.loads((HERE / "PASS1006_BUILD_SUMMARY.json").read_text(encoding="utf-8"))

    checks: dict[str, bool] = {}
    checks["462 statements"] = len(statements) == 462
    checks["354 old statements"] = sum(row["source_release"] == "PASS1002" for row in statements) == 354
    checks["108 new statements"] = sum(row["source_release"] == "PASS1005" for row in statements) == 108
    checks["2618 running groups"] = sum(int(row["event_count"]) for row in statements) == 2618
    checks["3168 event rows"] = len(events) == 3168
    checks["event IDs unique"] = len({row["event_id"] for row in events}) == 3168
    checks["2618 statement events"] = sum(row["event_role"] == "RUNNING_STATEMENT" for row in events) == 2618
    checks["550 address events"] = sum(row["event_role"] == "LOCAL_ADDRESS_OR_LABEL" for row in events) == 550
    checks["550 address ledger"] = len(addresses) == 550
    checks["statement IDs complete"] = all(
        row["statement_id"] for row in events if row["event_role"] == "RUNNING_STATEMENT"
    )
    checks["address statement IDs blank"] = all(not row["statement_id"] for row in addresses)
    statement_event_ids: list[str] = []
    for row in statements:
        statement_event_ids.extend(row["event_ids"].split("|"))
    checks["statement event coverage unique"] = (
        len(statement_event_ids) == 2618 and len(set(statement_event_ids)) == 2618
    )
    event_statement_ids = {
        row["event_id"] for row in events if row["event_role"] == "RUNNING_STATEMENT"
    }
    checks["statement/event join exact"] = set(statement_event_ids) == event_statement_ids
    checks["432 licensed closes"] = sum(row["end_mode"] == "LICENSED_DY_CLOSE" for row in statements) == 432
    checks["30 boundary/open ends"] = sum(row["end_mode"] != "LICENSED_DY_CLOSE" for row in statements) == 30
    checks["all fluent readings present"] = all(row["fluent_workshop_de"].strip() for row in statements)
    checks["statement ordinals unique"] = len({row["statement_id"] for row in statements}) == 462
    checks["18 page summaries"] = len(pages) == 18
    checks["18 physical pages"] = len({row["physical_page"] for row in events}) == 18
    checks["page group sums"] = sum(int(row["total_groups"]) for row in pages) == 3168
    checks["page running sums"] = sum(int(row["running_groups"]) for row in pages) == 2618
    checks["page address sums"] = sum(int(row["address_or_label_groups"]) for row in pages) == 550
    checks["page statement sums"] = sum(int(row["statements"]) for row in pages) == 462
    zero_statement_pages = {row["physical_page"] for row in pages if int(row["statements"]) == 0}
    checks["pure address pages exact"] = zero_statement_pages == {"f69v", "f70v"}
    checks["f69 f70 all local"] = all(
        row["event_role"] == "LOCAL_ADDRESS_OR_LABEL"
        for row in events
        if row["physical_page"] in {"f69v", "f70v"}
    )
    checks["175 codebook lines"] = len(codebook) == 175
    checks["codebook byte identical"] = sha(HERE / "PASS1006_175_APPRENTICE_CODEBOOK.tsv") == sha(
        SOURCE_CODEBOOK
    )
    checks["5 allograph rules"] = len(allographs) == 5
    checks["five distinct allograph rules"] = len({row["scribe_rule"] for row in allographs}) == 5
    checks["29 composition appendix"] = len(compositions) == 29
    checks["all compositions are root sums"] = {row["teaching_status"] for row in compositions} == {
        "ROOT_SUM_NOT_NEW_WORD"
    }
    checks["composition statements exist"] = {
        row["statement_id"] for row in compositions
    }.issubset({row["statement_id"] for row in statements})
    checks["summary agrees"] = (
        summary["groups"] == 3168
        and summary["running_groups"] == 2618
        and summary["local_address_or_label_groups"] == 550
        and summary["statements"] == 462
        and summary["codebook_lines"] == 175
        and summary["new_portable_roots"] == 0
    )
    readable = (HERE / "PASS1006_18_PAGE_READABLE_EDITION.md").read_text(encoding="utf-8")
    checks["readable edition lists all statements"] = readable.count("- **P1006-S") == 462
    checks["manual names 462 statements"] = "462 Lauftextaussagen" in (
        HERE / "PASS1006_APPRENTICE_MANUAL.md"
    ).read_text(encoding="utf-8")

    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "failures": [name for name, passed in checks.items() if not passed],
        "cross_line_statements": sum(row["crosses_physical_line"] == "YES" for row in statements),
        "page_statement_counts": dict(Counter(row["physical_page"] for row in statements)),
    }
    (HERE / "PASS1006_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
