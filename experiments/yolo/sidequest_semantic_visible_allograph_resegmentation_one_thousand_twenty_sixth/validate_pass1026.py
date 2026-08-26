#!/usr/bin/env python3
"""Validate Pass 1026 outputs and deterministic rebuild."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PASS1008 = (
    ROOT
    / "experiments/yolo/sidequest_semantic_four_page_template_transfer_one_thousand_eighth"
    / "PASS1008_1413_EVENT_TRANSFER.tsv"
)
PASS1025 = (
    ROOT
    / "experiments/yolo/sidequest_semantic_leave_one_register_replay_one_thousand_twenty_fifth"
    / "PASS1025_3888_REGISTER_EVENT_REPLAY.tsv"
)
OUTPUTS = [
    "PASS1026_271_ONE_EDIT_EVENT_AUDIT.tsv",
    "PASS1026_226_SURFACE_RESEGMENTATION.tsv",
    "PASS1026_EDIT_RULE_COUNTS.tsv",
    "PASS1026_3888_CORRECTED_EVENT_LEDGER.tsv",
    "PASS1026_AFFECTED_STATEMENTS.tsv",
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    checks: dict[str, bool] = {}
    audits = read_tsv(HERE / OUTPUTS[0])
    surfaces = read_tsv(HERE / OUTPUTS[1])
    rules = read_tsv(HERE / OUTPUTS[2])
    events = read_tsv(HERE / OUTPUTS[3])
    statements = read_tsv(HERE / OUTPUTS[4])
    source1008 = [
        row for row in read_tsv(PASS1008) if row["transfer_class"] == "ONE_EDIT_REGISTERED_ALLOGRAPH"
    ]
    source1025 = read_tsv(PASS1025)

    checks["audit_271"] = len(audits) == len(source1008) == 271
    checks["surfaces_226"] = len(surfaces) == len({row["surface"] for row in source1008}) == 226
    checks["events_3888"] = len(events) == len(source1025) == 3888
    checks["statements_96"] = len(statements) == 96
    checks["changed_events_239"] = sum(row["pass1026_change"] == "RESEGMENTED" for row in events) == 239
    checks["surface_decisions_203_21_2"] = Counter(row["audit_decision"] for row in surfaces) == {
        "RESEGMENT_VISIBLE_EDIT": 203,
        "LICENSED_SAME_RECIPE": 21,
        "CURRENT_ALREADY_REPAIRED": 2,
    }

    checks["audit_source_event_alignment"] = [row["event_id"] for row in audits] == [
        row["event_id"] for row in source1008
    ]
    checks["audit_surface_alignment"] = [row["surface"] for row in audits] == [
        row["surface"] for row in source1008
    ]
    checks["event_source_alignment"] = [row["source_event_id"] for row in events] == [
        row["event_id"] for row in source1025
    ]
    checks["event_surface_alignment"] = [row["surface"] for row in events] == [
        row["surface"] for row in source1025
    ]
    checks["event_statement_alignment"] = [row["statement_id"] for row in events] == [
        row["statement_id"] for row in source1025
    ]

    surface_recipe: dict[str, set[str]] = defaultdict(set)
    for row in events:
        surface_recipe[row["surface"]].add(row["pass1026_recipe"])
    checks["one_surface_one_recipe"] = all(len(recipes) == 1 for recipes in surface_recipe.values())
    checks["no_empty_recipe_or_reading"] = all(
        row["pass1026_recipe"] and row["literal_core_reading_de"] for row in events
    )
    checks["only_audited_surfaces_changed"] = all(
        row["one_edit_audit_surface"] == "YES"
        for row in events
        if row["pass1026_change"] == "RESEGMENTED"
    )
    checks["cheo_fixed"] = surface_recipe["cheo"] == {"CH+E+O"}
    checks["okeor_fixed"] = surface_recipe["okeor"] == {"OK+E+OR"}
    checks["visible_examples_fixed"] = all(
        surface_recipe[surface] == {recipe}
        for surface, recipe in {
            "aiiny": "AIIN+Y",
            "olain": "OL+AIN",
            "otees": "OT+EE+S",
            "chokaiin": "OK+AIIN",
            "chekaiin": "CH+K+AIIN",
            "qokas": "OK+A_ADDR+S",
            "teo": "T+E+O",
        }.items()
    )

    allowed_pages = {
        "f10r", "f11r", "f13r", "f17r", "f18r", "f55v", "f56r",
        "f67r2", "f68r1", "f71v", "f72r", "f75r", "f76r", "f77r",
        "f81v", "f82r", "f83r", "f88r", "f88v", "f89r",
    }
    checks["fixed_twenty_page_scope"] = {row["physical_page"] for row in events} == allowed_pages
    checks["sealed_pages_absent"] = all(
        "f84" not in "\t".join(row.values()).lower()
        for table in (audits, surfaces, events, statements)
        for row in table
    )
    checks["rule_counts_sum_271"] = sum(int(row["audited_event_count"]) for row in rules) == 271
    checks["rule_surface_counts_sum_226"] = sum(int(row["surface_count"]) for row in rules) == 226

    statement_events: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        statement_events[row["statement_id"]].append(row)
    affected = {
        statement_id
        for statement_id, rows in statement_events.items()
        if any(row["pass1026_change"] == "RESEGMENTED" for row in rows)
    }
    checks["affected_statement_identity"] = {row["statement_id"] for row in statements} == affected
    checks["statement_event_counts"] = all(
        int(row["event_count"]) == len(statement_events[row["statement_id"]]) for row in statements
    )
    checks["statement_surface_sequences"] = all(
        row["surface_sequence"]
        == " ".join(event["surface"] for event in statement_events[row["statement_id"]])
        for row in statements
    )

    before = {name: sha256(HERE / name) for name in OUTPUTS}
    subprocess.run(
        ["python3", str(HERE / "build_pass1026.py")],
        cwd=ROOT,
        check=True,
        stdout=subprocess.DEVNULL,
    )
    after = {name: sha256(HERE / name) for name in OUTPUTS}
    checks["deterministic_rebuild"] = before == after

    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "check_count": len(checks),
        "failed_checks": [name for name, value in checks.items() if not value],
        "checks": checks,
        "output_hashes": after,
    }
    (HERE / "PASS1026_VALIDATION.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
