#!/usr/bin/env python3
"""Validate Pass 915."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path


BASE = Path(__file__).resolve().parent
OUT = BASE / "PASS915_VALIDATION.json"


def rows(name: str) -> list[dict[str, str]]:
    with (BASE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


checks = []


def check(name: str, condition: bool, detail: object) -> None:
    checks.append({"name": name, "pass": bool(condition), "detail": detail})


def main() -> None:
    prose = rows("PASS915_2010_PROSE_EVENT_SLOTS.tsv")
    clauses = rows("PASS915_354_CLAUSE_EDITION.tsv")
    transitions = rows("PASS915_SLOT_TRANSITIONS.tsv")
    grammar = rows("PASS915_CLAUSE_GRAMMAR.tsv")
    event_ids = [event for row in clauses for event in range(int(row["start_event"].removeprefix("P912-E")), int(row["end_event"].removeprefix("P912-E")) + 1)]

    check("prose_2010", len(prose) == 2010, len(prose))
    check("prose_ids_unique", len({row["event_id"] for row in prose}) == 2010, "2010")
    check("clauses_354", len(clauses) == 354, len(clauses))
    check("clause_event_sum", sum(int(row["events"]) for row in clauses) == 2010, sum(int(row["events"]) for row in clauses))
    check("cross_lines_121", sum(row["crosses_physical_line"] == "YES" for row in clauses) == 121, Counter(row["crosses_physical_line"] for row in clauses))
    check("dy_closes_331", sum(row["end_reason"] == "LICENSED_DY_CLOSE" for row in clauses) == 331, Counter(row["end_reason"] for row in clauses))
    check("nonprose_15", sum(row["end_reason"] == "NONPROSE_OWNER_OR_DIAGRAM_BOUNDARY" for row in clauses) == 15, Counter(row["end_reason"] for row in clauses))
    check("page_end_8", sum(row["end_reason"] == "PAGE_END_OPEN" for row in clauses) == 8, Counter(row["end_reason"] for row in clauses))
    check("grammar_9", len(grammar) == 9, len(grammar))
    check("grammar_order", [int(row["order"]) for row in grammar] == list(range(1, 10)), "1..9")
    check("transitions_nonempty", len(transitions) >= 20, len(transitions))
    check("all_canonical", all(row["canonical_spoken_order_de"] for row in clauses), "354/354")
    check("all_surface", all(row["surface_sequence"] for row in clauses), "354/354")
    check("sealed_absent", all("f84" not in "\t".join(row.values()).lower() for row in prose + clauses), "sealed")

    before = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in BASE.glob("PASS915_*") if path.name != OUT.name}
    subprocess.run(["python", str(BASE / "build_nine_hundred_fifteenth.py")], check=True, cwd=BASE.parents[2])
    after = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in BASE.glob("PASS915_*") if path.name != OUT.name}
    check("deterministic_rebuild", before == after, len(before))

    result = {"status": "PASS" if all(row["pass"] for row in checks) else "FAIL", "checks_passed": sum(bool(row["pass"]) for row in checks), "checks_total": len(checks), "checks": checks}
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
