#!/usr/bin/env python3
"""Validate the fresh six-record Biological copy."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> None:
    events = read("THREE_HUNDRED_THIRTEENTH_281_FRESH_COPY_EVENTS.tsv")
    statements = read("THREE_HUNDRED_THIRTEENTH_97_FRESH_COPY_STATEMENTS.tsv")
    profiles = read("THREE_HUNDRED_THIRTEENTH_FIVE_RENDERER_HABITS.tsv")
    summary = json.loads((HERE / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "events_281": len(events) == summary["events"] == 281,
        "statements_97": len(statements) == summary["statements"] == 97,
        "records_6": len({row["record_unit_id"] for row in events}) == summary["records"] == 6,
        "lines_40": len({(row["page"], row["locus"]) for row in events}) == summary["physical_lines"] == 40,
        "profiles_5": len(profiles) == summary["renderer_profiles"] == 5,
        "changed_69": sum(row["surface_changed"] == "YES" for row in events) == summary["changed_surfaces"] == 69,
        "unchanged_212": sum(row["surface_changed"] == "NO" for row in events) == summary["unchanged_surfaces"] == 212,
        "reverse_281": sum(row["reverse_identity_match"] == "YES" for row in events) == summary["reverse_identity_matches"] == 281,
        "statements_roundtrip_97": sum(row["roundtrip_match"] == "YES" for row in statements) == summary["statement_roundtrip_matches"] == 97,
        "fresh_values_nonempty": all(row["fresh_surface"] and row["imperative_de"] for row in events),
        "no_sealed_page": not any(row["page"].startswith("f84") or row["locus"].startswith("f84") for row in events),
    }
    failed = [name for name, passed in checks.items() if not passed]
    result = {"status": "PASS" if not failed else "FAIL", "checks": checks, "failed": failed}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
