#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def hashes() -> dict[str, str]:
    names = ["TWO_HUNDRED_TWENTY_FIFTH_363_PARSE_UNITS.tsv", "TWO_HUNDRED_TWENTY_FIFTH_116_ABA_INTEGRATED_STATEMENTS.tsv", "TWO_HUNDRED_TWENTY_FIFTH_READABLE_ABA_EDITION.md", "BUILD_SUMMARY.json"]
    return {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in names}


def main() -> None:
    units = read("TWO_HUNDRED_TWENTY_FIFTH_363_PARSE_UNITS.tsv")
    statements = read("TWO_HUNDRED_TWENTY_FIFTH_116_ABA_INTEGRATED_STATEMENTS.tsv")
    readable = (OUT / "TWO_HUNDRED_TWENTY_FIFTH_READABLE_ABA_EDITION.md").read_text(encoding="utf-8")
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    event_ids = [event for row in units for event in row["source_event_ids"].split("|")]
    kinds = Counter(row["unit_kind"] for row in units)
    checks = {
        "363_units": len(units) == 363 and len({row["parse_unit_id"] for row in units}) == 363,
        "354_atomic_9_aba": kinds == {"ATOMIC_CARD": 354, "ABA_RETURN_FRAME": 9},
        "381_events_exact_once": len(event_ids) == 381 and len(set(event_ids)) == 381 and set(event_ids) == {f"E{i:03d}" for i in range(1, 382)},
        "116_statements": len(statements) == 116 and len({row["statement_id"] for row in statements}) == 116,
        "nine_rewritten": sum(row["revision_status"] == "ABA_REWRITTEN" for row in statements) == 9,
        "nine_statements_have_frame": sum(int(row["aba_frame_count"]) > 0 for row in statements) == 9,
        "counts_reduce_by_18": sum(int(row["source_event_count"]) for row in statements) - sum(int(row["parse_unit_count"]) for row in statements) == 18,
        "all_records_readable": all(f"## {record}" in readable for record in ("H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6")),
        "sealed_not_accessed": summary["sealed_pages_accessed"] is False,
        "sealed_absent": "f84" not in readable.lower() and not any("f84" in value.lower() for table in (units, statements) for row in table for value in row.values()),
    }
    first = hashes()
    subprocess.run(["python3", str(OUT / "build_two_hundred_twenty_fifth.py")], check=True)
    second = hashes()
    checks["deterministic_rebuild"] = first == second
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary, "artifact_sha256": second}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
