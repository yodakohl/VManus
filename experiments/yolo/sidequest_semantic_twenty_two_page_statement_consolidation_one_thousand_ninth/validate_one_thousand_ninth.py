#!/usr/bin/env python3
"""Validate the complete Pass-1009 statement and ellipsis consolidation."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
STATEMENTS = HERE / "PASS1009_627_STATEMENT_EDITION.tsv"
EVENTS = HERE / "PASS1009_4581_EVENT_LEDGER.tsv"
PAGES = HERE / "PASS1009_22_PAGE_PROFILE.tsv"
ELLIPSES = HERE / "PASS1009_27_ELLIPSIS_RESOLUTIONS.tsv"
PREDICATES = HERE / "PASS1009_PREDICATE_REALIZATION_PROFILE.tsv"
READABLE = HERE / "PASS1009_TWENTY_TWO_PAGE_READABLE_EDITION.md"
REPORT = HERE / "PASS1009_REPORT.md"
SUMMARY = HERE / "PASS1009_BUILD_SUMMARY.json"
BUILDER = HERE / "build_one_thousand_ninth.py"

PASS996 = (
    ROOT
    / "experiments/yolo/sidequest_semantic_canonical_scribe_workshop_sixth_edition_nine_hundred_ninety_sixth"
    / "PASS996_53_PORTABLE_ROOTS.tsv"
)
PASS1006 = ROOT / "experiments/yolo/sidequest_semantic_eighteen_page_unified_workshop_edition_one_thousand_sixth"
OLD_STATEMENTS = PASS1006 / "PASS1006_462_UNIFIED_STATEMENT_EDITION.tsv"
PASS1008 = ROOT / "experiments/yolo/sidequest_semantic_four_page_template_transfer_one_thousand_eighth"
NEW_STATEMENTS = PASS1008 / "PASS1008_STATEMENT_TEMPLATE_EDITION.tsv"
SOURCE_EVENTS = PASS1008 / "PASS1008_4581_UNIFIED_EVENT_LEDGER.tsv"

PAGE_ORDER = [
    "f10r", "f11r", "f13r", "f17r", "f18r", "f55v", "f56r",
    "f67r2", "f68r1", "f69v", "f70v", "f71v", "f72r",
    "f75r", "f76r", "f77r", "f81v", "f82r", "f83r",
    "f88r", "f88v", "f89r",
]

EXPECTED_TEMPLATES = {
    "T01": 102, "T02": 23, "T03": 71, "T04": 36, "T05": 15,
    "T06": 98, "T07": 125, "T08": 116, "T09": 41,
}
EXPECTED_PREDICATES = {
    "ANAPHORIC_ACTION_INHERITANCE": 24,
    "EXPLICIT_OPERATION_ROOT": 588,
    "FUSED_PATH_OPERATION": 9,
    "PREPARATION_INHERITANCE": 1,
    "SELF_PREDICATING_CONTINUATION": 3,
    "TARGET_LIST_INHERITANCE": 2,
}
ELLIPSE_KINDS = {
    "ANAPHORIC_ACTION_INHERITANCE",
    "PREPARATION_INHERITANCE",
    "TARGET_LIST_INHERITANCE",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def main() -> int:
    statements = read_tsv(STATEMENTS)
    events = read_tsv(EVENTS)
    pages = read_tsv(PAGES)
    ellipses = read_tsv(ELLIPSES)
    predicates = read_tsv(PREDICATES)
    old = read_tsv(OLD_STATEMENTS)
    new = read_tsv(NEW_STATEMENTS)
    source_events = read_tsv(SOURCE_EVENTS)
    roots = read_tsv(PASS996)
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

    checks: dict[str, bool] = {}
    checks["627 statements"] = len(statements) == 627
    checks["4581 events"] = len(events) == 4581
    checks["22 page profiles"] = len(pages) == 22
    checks["27 ellipses"] = len(ellipses) == 27
    checks["6 predicate rows"] = len(predicates) == 6
    checks["statement IDs unique"] = len({row["statement_id"] for row in statements}) == 627
    checks["event IDs unique"] = len({row["event_id"] for row in events}) == 4581
    checks["statement ordinals contiguous"] = [int(row["book_statement_ordinal"]) for row in statements] == list(range(1, 628))
    checks["event ordinals contiguous"] = [int(row["book_event_ordinal"]) for row in events] == list(range(1, 4582))
    checks["page order exact"] = [row["physical_page"] for row in pages] == PAGE_ORDER

    checks["old/new statement sources exact"] = Counter(row["legacy_statement_id"] for row in statements) == Counter(
        [row["statement_id"] for row in old] + [row["statement_id"] for row in new]
    )
    source_statement = {row["statement_id"]: row for row in old + new}
    checks["statement surfaces preserved"] = all(
        row["surface_sequence"] == source_statement[row["legacy_statement_id"]]["surface_sequence"]
        for row in statements
    )
    checks["statement components preserved"] = all(
        row["component_sequence"] == source_statement[row["legacy_statement_id"]]["component_sequence"]
        for row in statements
    )
    checks["statement event lists preserved"] = all(
        row["event_ids"] == source_statement[row["legacy_statement_id"]]["event_ids"]
        for row in statements
    )

    checks["template counts exact"] = Counter(row["template_id"] for row in statements) == Counter(EXPECTED_TEMPLATES)
    checks["all nine templates used"] = {row["template_id"] for row in statements} == {f"T{i:02d}" for i in range(1, 10)}
    checks["predicate counts exact"] = Counter(row["predicate_realization"] for row in statements) == Counter(EXPECTED_PREDICATES)
    checks["predicate profile agrees"] = {
        row["predicate_realization"]: int(row["statements"]) for row in predicates
    } == EXPECTED_PREDICATES
    checks["all predicates named"] = all(row["predicate_operation_de"] for row in statements)

    by_statement = {row["statement_id"]: row for row in statements}
    checks["ellipse table IDs exact"] = {row["statement_id"] for row in ellipses} == {
        row["statement_id"] for row in statements if row["predicate_realization"] in ELLIPSE_KINDS
    }
    checks["ellipse kinds exact"] = {row["resolution_kind"] for row in ellipses} == ELLIPSE_KINDS
    checks["ellipse operations present"] = all(row["inherited_operation_de"] for row in ellipses)
    checks["ellipse source present"] = all(row["inheritance_source_statement_id"] in by_statement for row in ellipses)
    checks["ellipse source earlier"] = all(
        int(by_statement[row["inheritance_source_statement_id"]]["book_statement_ordinal"])
        < int(by_statement[row["statement_id"]]["book_statement_ordinal"])
        for row in ellipses
    )
    checks["ellipse source same page"] = all(
        by_statement[row["inheritance_source_statement_id"]]["physical_page"] == row["physical_page"]
        for row in ellipses
    )
    checks["ellipse source same owner"] = all(
        by_statement[row["inheritance_source_statement_id"]]["owner_id"] == row["owner_id"]
        for row in ellipses
    )
    checks["ellipse operation agrees with source"] = all(
        by_statement[row["inheritance_source_statement_id"]]["predicate_operation_de"] == row["inherited_operation_de"]
        for row in ellipses
    )
    checks["ellipse backlink agrees"] = all(
        by_statement[row["statement_id"]]["inheritance_source_statement_id"] == row["inheritance_source_statement_id"]
        and by_statement[row["statement_id"]]["inherited_operation_de"] == row["inherited_operation_de"]
        for row in ellipses
    )
    checks["nonellipses have no inheritance"] = all(
        not row["inheritance_source_statement_id"] and not row["inherited_operation_de"]
        for row in statements if row["predicate_realization"] not in ELLIPSE_KINDS
    )
    checks["resolved readings complete"] = all(row["resolved_workshop_de"] for row in statements)
    checks["27 resolved readings in readable edition"] = all(
        row["resolved_workshop_de"] in READABLE.read_text(encoding="utf-8") for row in ellipses
    )

    checks["566 licensed closes"] = sum(row["end_mode"] == "LICENSED_DY_CLOSE" for row in statements) == 566
    checks["10 open ends"] = sum(
        row["end_mode"] in {"PAGE_END_OPEN", "TRUE_OPEN_ARTICLE_END", "TRUE_OPEN_FINAL_RING"}
        for row in statements
    ) == 10
    checks["51 visible boundaries"] = sum(
        row["end_mode"] not in {"LICENSED_DY_CLOSE", "PAGE_END_OPEN", "TRUE_OPEN_ARTICLE_END", "TRUE_OPEN_FINAL_RING"}
        for row in statements
    ) == 51
    checks["199 cross-line statements"] = sum(row["crosses_physical_line"] == "YES" for row in statements) == 199

    statement_event_ids = [event_id for row in statements for event_id in row["event_ids"].split("|")]
    running = [row for row in events if row["event_role"] == "RUNNING_STATEMENT"]
    local = [row for row in events if row["event_role"] != "RUNNING_STATEMENT"]
    checks["3888 running events"] = len(running) == 3888
    checks["693 local events"] = len(local) == 693
    checks["running events partition statements"] = Counter(statement_event_ids) == Counter(row["event_id"] for row in running)
    checks["running statement backlinks exact"] = all(row["statement_id"] in by_statement for row in running)
    checks["local events outside statements"] = all(not row["statement_id"] for row in local)
    checks["event statement legacy mapping exact"] = all(
        (not row["statement_id"] and not row["legacy_statement_id"])
        or by_statement[row["statement_id"]]["legacy_statement_id"] == row["legacy_statement_id"]
        for row in events
    )

    source_by_id = {row["event_id"]: row for row in source_events}
    checks["event inventory preserved"] = {row["event_id"] for row in events} == set(source_by_id)
    checks["event surfaces preserved"] = all(row["surface"] == source_by_id[row["event_id"]]["surface"] for row in events)
    checks["event components preserved"] = all(row["component_recipe"] == source_by_id[row["event_id"]]["component_recipe"] for row in events)
    checks["event defaults preserved"] = all(row["portable_default_de"] == source_by_id[row["event_id"]]["portable_default_de"] for row in events)

    allowed_roots = {row["recognition_form"] for row in roots}
    used_roots = {
        root
        for row in events if row["event_role"] == "RUNNING_STATEMENT"
        for root in row["component_recipe"].split("+")
    }
    checks["53 portable roots"] = len(allowed_roots) == 53
    checks["no new portable root"] = used_roots <= allowed_roots

    checks["page group totals"] = sum(int(row["groups"]) for row in pages) == 4581
    checks["page running totals"] = sum(int(row["running_groups"]) for row in pages) == 3888
    checks["page local totals"] = sum(int(row["address_or_marker_groups"]) for row in pages) == 693
    checks["page statement totals"] = sum(int(row["statements"]) for row in pages) == 627
    checks["address-only pages exact"] = {
        row["physical_page"] for row in pages if row["template_profile"] == "ADDRESS_ONLY"
    } == {"f69v", "f70v"}

    checks["summary core exact"] = (
        summary["physical_pages"] == 22
        and summary["groups"] == 4581
        and summary["running_groups"] == 3888
        and summary["local_groups"] == 693
        and summary["statements"] == 627
        and summary["ellipses"] == 27
        and summary["template_counts"] == EXPECTED_TEMPLATES
        and summary["predicate_counts"] == EXPECTED_PREDICATES
        and summary["new_portable_roots"] == 0
    )
    checks["report counts present"] = all(
        token in REPORT.read_text(encoding="utf-8") for token in ["627 Aussagen", "4.581 Gruppen", "27 echte Werkstattellipsen"]
    )
    checks["readable edition covers all statements"] = all(
        row["statement_id"] in READABLE.read_text(encoding="utf-8") for row in statements
    )

    artifacts = [STATEMENTS, EVENTS, PAGES, ELLIPSES, PREDICATES, READABLE, REPORT]
    before = {path.name: digest(path) for path in artifacts}
    subprocess.run(["python3", str(BUILDER)], cwd=ROOT, check=True)
    after = {path.name: digest(path) for path in artifacts}
    checks["deterministic rebuild byte-identical"] = before == after
    checks["summary hashes exact"] = json.loads(SUMMARY.read_text(encoding="utf-8"))["output_sha256"] == after

    blob = b"\n".join(path.read_bytes() for path in artifacts)
    checks["sealed folios absent"] = b"f84" not in blob.lower()
    checks["absolute workspace path absent"] = str(ROOT).encode() not in blob

    failures = [name for name, passed in checks.items() if not passed]
    result = {
        "status": "PASS" if not failures else "FAIL",
        "checks_total": len(checks),
        "checks_passed": sum(checks.values()),
        "checks_failed": failures,
        "counts": {
            "pages": len(pages), "groups": len(events), "running_groups": len(running),
            "local_groups": len(local), "statements": len(statements), "ellipses": len(ellipses),
        },
        "template_counts": dict(sorted(Counter(row["template_id"] for row in statements).items())),
        "predicate_counts": dict(sorted(Counter(row["predicate_realization"] for row in statements).items())),
        "checks": checks,
    }
    (HERE / "PASS1009_VALIDATION.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print(f"PASS: {len(checks)}/{len(checks)} checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
