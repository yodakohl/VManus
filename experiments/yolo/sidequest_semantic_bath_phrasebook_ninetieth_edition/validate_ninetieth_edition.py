#!/usr/bin/env python3
"""Validate the ninetieth Biological phrasebook."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    primitives = rows("NINETIETH_16_BATH_SERVICE_PRIMITIVES.tsv")
    statements = rows("NINETIETH_97_STATEMENT_PHRASEBOOK.tsv")
    macros = rows("NINETIETH_8_MACRO_SUMMARY.tsv")
    repeated = rows("NINETIETH_REPEATED_EXACT_PHRASES.tsv")
    checks = {
        "primitives_16": len(primitives) == 16,
        "primitive_ids_unique": len({row["primitive_id"] for row in primitives}) == 16,
        "statements_97": len(statements) == 97,
        "statement_ids_unique": len({row["statement_id"] for row in statements}) == 97,
        "all_statements_parsed": all(row["primitive_sequence"] and int(row["primitive_count"]) >= 1 for row in statements),
        "macros_8": len(macros) == 8,
        "macro_sum_97": sum(int(row["statement_count"]) for row in macros) == 97,
        "all_macros_used": all(int(row["statement_count"]) > 0 for row in macros),
        "repeated_are_repeated": all(int(row["occurrence_count"]) >= 2 for row in repeated),
        "owner_rule_fixed": all(row["owner_rule"] == "KEEP_LOCAL_VISIBLE_OWNER__DO_NOT_MERGE_STATIONS" for row in statements),
        "fixed_pages_only": set(row["page"] for row in statements) == {"f81v", "f82r", "f83r"},
        "sealed_absent": all("f84" not in "\t".join(row.values()).lower() for row in statements + primitives),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
