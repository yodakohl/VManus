#!/usr/bin/env python3
"""Validate the creative owner resolution."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    decisions = rows("HUNDRED_SEVENTH_25_CREATIVE_OWNER_RESOLUTIONS.tsv")
    clauses = rows("HUNDRED_SEVENTH_254_REVISED_OWNER_BINDING.tsv")
    statements = rows("HUNDRED_SEVENTH_116_OWNER_RESOLVED_STATEMENTS.tsv")
    counts = {status: sum(row["resolution_status"] == status for row in decisions) for status in {row["resolution_status"] for row in decisions}}
    checks = {
        "decisions_25": len(decisions) == 25,
        "clauses_254": len(clauses) == 254,
        "statements_116": len(statements) == 116,
        "decision_units_exact": {row["fusion_unit_id"] for row in decisions} == {f"FU{i:03d}" for i in list(range(125, 129)) + list(range(172, 193))},
        "f82_visible_4": counts.get("CREATIVE_VISIBLE_OWNER") == 4,
        "f83_register_20": counts.get("CREATIVE_REGISTER_BATCH") == 20,
        "forward_pair_1": counts.get("FORWARD_TO_NEXT_DIRECT_OWNER") == 1,
        "none_unresolved": all(row["final_owner_status"] != "OWNER_UNRESOLVED" for row in clauses),
        "connection_limits_present": all(row["connection_ceiling"] for row in decisions),
        "sealed_absent": all("f84" not in "\t".join(row.values()).lower() for row in clauses),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
