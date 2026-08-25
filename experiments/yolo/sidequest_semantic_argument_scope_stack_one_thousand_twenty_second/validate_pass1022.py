#!/usr/bin/env python3
"""Validate the complete Pass-1022 creative scope release."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


checks: list[dict[str, object]] = []


def check(name: str, condition: bool, detail: object) -> None:
    checks.append({"check": name, "pass": bool(condition), "detail": detail})


def main() -> None:
    generated = [
        HERE / "PASS1022_3888_EVENT_SCOPE_BINDINGS.tsv",
        HERE / "PASS1022_627_STATEMENT_SCOPE_EDITION.tsv",
        HERE / "PASS1022_EIGHT_SCOPE_RULES.tsv",
        HERE / "PASS1022_BUILD_SUMMARY.json",
    ]
    before = {path.name: digest(path) for path in generated}
    subprocess.run(["python3", str(HERE / "build_pass1022.py")], cwd=ROOT, check=True)
    after = {path.name: digest(path) for path in generated}
    check("deterministic_rebuild", before == after, after)

    events = rows("PASS1022_3888_EVENT_SCOPE_BINDINGS.tsv")
    statements = rows("PASS1022_627_STATEMENT_SCOPE_EDITION.tsv")
    rules = rows("PASS1022_EIGHT_SCOPE_RULES.tsv")
    focus = rows("SCOPE_STACK_ATTACHMENTS.tsv")
    ambiguities = rows("SCOPE_STACK_AMBIGUITIES.tsv")
    manual = rows("MANUAL_SCOPE_12_STATEMENT_AUDIT.tsv")
    duplicates = rows("../sidequest_semantic_repeated_core_operator_one_thousand_twenty_first/PASS1021_ADJUDICATED_DOUBLING.tsv")

    check("event_count", len(events) == 3888, len(events))
    check("event_ordinals", [int(row["running_event_ordinal"]) for row in events] == list(range(1, 3889)), "1..3888")
    check("event_ids_unique", len({row["event_id"] for row in events}) == 3888, len({row["event_id"] for row in events}))
    check("statement_count", len(statements) == 627, len(statements))
    check("statement_ids_unique", len({row["statement_id"] for row in statements}) == 627, len({row["statement_id"] for row in statements}))
    check("statement_event_sum", sum(int(row["event_count"]) for row in statements) == 3888, sum(int(row["event_count"]) for row in statements))
    check("eight_rules", [int(row["rule"]) for row in rules] == list(range(1, 9)), [row["name"] for row in rules])
    check("all_statements_complete", all(row["scope_result"] == "COMPLETE_SCOPE_READING" and row["unbound_modifier_count"] == "0" for row in statements), Counter(row["scope_result"] for row in statements))
    check("all_events_scoped", all(row["scope_status"] in {"SELF_CONTAINED", "CARRIED_SCOPE"} for row in events), Counter(row["scope_status"] for row in events))
    check("no_pending_trace", not any("OFFEN" in row["binding_trace_de"] or "PENDING" in row["binding_trace_de"] for row in events), "none")
    check("surface_and_recipe_present", all(row["surface"] and row["component_recipe"] for row in events), "3888/3888")
    check("focus_attachment_count", len(focus) == 4345, len(focus))
    check("focus_event_inventory", len({row["event_id"] for row in focus}) == 3285, len({row["event_id"] for row in focus}))
    check("ambiguity_rows", len(ambiguities) == 329, len(ambiguities))
    check("ambiguous_focus_occurrences", len({row["attachment_id"] for row in ambiguities}) == 328, len({row["attachment_id"] for row in ambiguities}))
    check("ambiguity_classes", Counter(row["ambiguity_class"] for row in ambiguities) == Counter({"EQUAL_DISTANCE_TWO_HEADS": 120, "OWNER_OR_NEXT_CARD_ACTION": 146, "R_HEAD_OR_TAIL": 63}), Counter(row["ambiguity_class"] for row in ambiguities))
    check("manual_context_count", len(manual) == 12, len(manual))
    check("manual_page_balance", Counter(row["page"] for row in manual) == Counter({"f75r": 4, "f67r2": 4, "f88r": 4}), Counter(row["page"] for row in manual))
    check("manual_event_sum", sum(int(row["event_count"]) for row in manual) == 306, sum(int(row["event_count"]) for row in manual))
    check("duplicate_inventory", len(duplicates) == 40, len(duplicates))
    check("duplicate_annotations", sum(row["duplicate_rule"] != "NONE" for row in events) == 40, sum(row["duplicate_rule"] != "NONE" for row in events))
    check("register_coverage", Counter(row["register"] for row in events) == Counter({"BIOLOGICAL": 2161, "HERBAL": 601, "PHARMA": 603, "CELESTIAL": 523}), Counter(row["register"] for row in events))
    check("owner_always_present", all(row["owner_de"] for row in events), "3888/3888")
    page_token = re.compile(r"(?<![0-9a-z])f84[rv]?(?![0-9a-z])", re.I)
    scanned = [path for path in HERE.iterdir() if path.is_file() and path.suffix in {".md", ".tsv"}]
    check("no_sealed_page_token", not any(page_token.search(path.read_text(encoding="utf-8")) for path in scanned), "none")

    result = {
        "result": "PASS" if all(item["pass"] for item in checks) else "FAIL",
        "checks_passed": sum(bool(item["pass"]) for item in checks),
        "checks_total": len(checks),
        "checks": checks,
        "output_hashes": {path.name: digest(path) for path in sorted(HERE.iterdir()) if path.is_file() and path.name != "PASS1022_VALIDATION.json"},
    }
    (HERE / "PASS1022_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["result"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps({"result": result["result"], "checks": f"{result['checks_passed']}/{result['checks_total']}"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
