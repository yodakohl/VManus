#!/usr/bin/env python3
"""Validate the complete pocket-core statement projection."""

from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python3", str(HERE / "build_six_hundred_ninetieth.py")], check=True)
    statements = read("SIX_HUNDRED_NINETIETH_116_STATEMENT_CORE_PROJECTION.tsv")
    events = read("SIX_HUNDRED_NINETIETH_381_EVENT_CORE_PROJECTION.tsv")
    records = read("SIX_HUNDRED_NINETIETH_11_RECORD_CORE_BURDEN.tsv")
    specialists = read("SIX_HUNDRED_NINETIETH_26_SPECIALIST_USAGE.tsv")
    classes = Counter(row["statement_class"] for row in statements)
    event_classes = Counter(row["event_class"] for row in events)
    checks = {
        "one_hundred_sixteen_statements": len(statements) == 116,
        "three_hundred_eighty_one_events": len(events) == 381 and len({row["event_id"] for row in events}) == 381,
        "eight_hundred_fifty_tokens": sum(int(row["component_tokens"]) for row in statements) == 850,
        "six_hundred_eight_core": sum(int(row["pocket_core_tokens"]) for row in statements) == 608,
        "two_hundred_forty_two_specialist": sum(int(row["specialist_tokens"]) for row in statements) == 242,
        "statement_classes": classes == Counter({"POCKET_ONLY": 17, "ONE_SPECIALIST_TYPE": 39, "MULTI_SPECIALIST": 60}),
        "event_classes": event_classes == Counter({"CORE_CARD": 180, "MIXED_OR_SPECIALIST_CARD": 201}),
        "eleven_records": len(records) == 11 and sum(int(row["events"]) for row in records) == 381,
        "twenty_six_specialists": len(specialists) == 26,
        "fixed_pages_only": {row["page"] for row in events} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "passed": sum(checks.values()), "total": len(checks)}
    (HERE / "SIX_HUNDRED_NINETIETH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
