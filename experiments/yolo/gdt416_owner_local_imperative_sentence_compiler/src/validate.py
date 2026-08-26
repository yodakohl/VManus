#!/usr/bin/env python3
"""Validate the GDT416 imperative sentence compiler."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler"
OUT = BASE / "artifacts"


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    subprocess.run(["python3", str(BASE / "src/run.py")], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    clauses = rows("gdt416_4576_imperative_clauses.tsv")
    statements = rows("gdt416_715_imperative_statements.tsv")
    templates = rows("gdt416_template_inventory.tsv")
    inherited = rows("gdt416_inherited_action_audit.tsv")
    inherited_arguments = rows("gdt416_inherited_argument_audit.tsv")
    result = json.loads((OUT / "gdt416_result.json").read_text(encoding="utf-8"))
    statement_event_ids = [event_id for row in statements for event_id in row["event_ids"].split("|")]
    template_counts = Counter(row["template"] for row in clauses)
    checks = {
        "clauses_4576": len(clauses) == 4576,
        "clauses_unique": len({r["global_running_event_id"] for r in clauses}) == 4576,
        "statements_715": len(statements) == 715,
        "statements_unique": len({r["global_statement_id"] for r in statements}) == 715,
        "statement_event_cover": len(statement_event_ids) == len(set(statement_event_ids)) == 4576,
        "statement_event_counts": all(int(r["event_count"]) == len(r["event_ids"].split("|")) for r in statements),
        "imperatives_nonempty": all(r["imperative_clause_de"].endswith(".") for r in clauses),
        "statement_readings_nonempty": all(r["imperative_reading_de"] for r in statements),
        "roundtrip_exact": all(r["roundtrip_exact"] == "YES" for r in clauses),
        "templates_complete": sum(int(r["event_count"]) for r in templates) == 4576,
        "template_counts_exact": all(template_counts[r["template"]] == int(r["event_count"]) for r in templates),
        "template_inventory_unique": len({r["template"] for r in templates}) == len(templates),
        "inheritance_ids_known": {r["global_running_event_id"] for r in inherited} <= {r["global_running_event_id"] for r in clauses},
        "inheritance_roots_nonempty": all(r["inherited_action_root"] != "NONE" for r in inherited),
        "argument_inheritance_ids_known": {r["global_running_event_id"] for r in inherited_arguments} <= {r["global_running_event_id"] for r in clauses},
        "argument_inheritance_roots_nonempty": all(r["inherited_argument_root"] != "NONE" for r in inherited_arguments),
        "no_forbidden_page": all(not r["physical_page"].startswith("f84") for r in clauses),
        "no_new_pages": result["new_pages"] == 0,
        "no_new_roots": result["new_roots"] == 0,
        "no_new_meanings": result["new_portable_meanings"] == 0,
        "edition_exists": (OUT / "COMPLETE_26_PAGE_IMPERATIVE_WORKING_READING.md").is_file(),
    }
    tracked = [
        OUT / "gdt416_4576_imperative_clauses.tsv",
        OUT / "gdt416_715_imperative_statements.tsv",
        OUT / "gdt416_template_inventory.tsv",
        OUT / "gdt416_inherited_action_audit.tsv",
        OUT / "gdt416_inherited_argument_audit.tsv",
        OUT / "COMPLETE_26_PAGE_IMPERATIVE_WORKING_READING.md",
        OUT / "gdt416_result.json",
    ]
    before = {p.name: digest(p) for p in tracked}
    subprocess.run(["python3", str(BASE / "src/run.py")], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    checks["deterministic_rebuild"] = before == {p.name: digest(p) for p in tracked}
    report = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "check_count": len(checks),
        "failure_count": sum(not value for value in checks.values()),
        "checks": checks,
    }
    (OUT / "gdt416_validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
