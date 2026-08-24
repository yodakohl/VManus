#!/usr/bin/env python3
"""Validate the seven-head Biological clause grammar."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> None:
    templates = read("THREE_HUNDRED_FIFTEENTH_SEVEN_CLAUSE_TEMPLATES.tsv")
    runs = read("THREE_HUNDRED_FIFTEENTH_240_CLAUSE_RUNS.tsv")
    statements = read("THREE_HUNDRED_FIFTEENTH_97_TEMPLATE_STATEMENTS.tsv")
    summary = json.loads((HERE / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "templates_7": len(templates) == summary["templates"] == 7,
        "runs_240": len(runs) == summary["clause_runs"] == 240,
        "events_281": sum(int(row["event_count"]) for row in runs) == summary["events"] == 281,
        "statements_97": len(statements) == summary["statements"] == 97,
        "single_46": sum(int(row["run_count"]) == 1 for row in statements) == summary["single_mode_statements"] == 46,
        "compound_51": sum(int(row["run_count"]) > 1 for row in statements) == summary["compound_statements"] == 51,
        "all_modes_known": {row["mode"] for row in runs} == {row["operating_mode"] for row in templates},
        "event_ids_unique": len({event for row in runs for event in row["event_ids"].split("|")}) == 281,
        "compact_not_longer": summary["compact_words"] < summary["old_words"],
        "no_empty_readings": all(row["compact_template_reading_de"] for row in statements),
        "no_sealed_page": not any(row["page"].startswith("f84") for row in runs + statements),
    }
    failed = [name for name, passed in checks.items() if not passed]
    result = {"status": "PASS" if not failed else "FAIL", "checks": checks, "failed": failed}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
