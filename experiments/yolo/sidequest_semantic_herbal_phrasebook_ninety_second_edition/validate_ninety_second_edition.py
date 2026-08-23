#!/usr/bin/env python3
"""Validate the Herbal phrasebook and cross-section comparison."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    primitives = rows("NINETY_SECOND_15_HERBAL_PRIMITIVES.tsv")
    statements = rows("NINETY_SECOND_19_HERBAL_STATEMENT_PHRASEBOOK.tsv")
    macros = rows("NINETY_SECOND_5_HERBAL_MACROS.tsv")
    cross = rows("NINETY_SECOND_HERBAL_BIO_PRIMITIVE_CROSSWALK.tsv")
    checks = {
        "primitives_15": len(primitives) == 15,
        "statements_19": len(statements) == 19,
        "events_100": sum(int(row["event_count"]) for row in statements) == 100,
        "all_statements_parsed": all(row["primitive_sequence"] and int(row["primitive_count"]) >= 1 for row in statements),
        "macros_5": len(macros) == 5,
        "all_macros_used": all(int(row["statement_count"]) > 0 for row in macros),
        "macro_sum_19": sum(int(row["statement_count"]) for row in macros) == 19,
        "crosswalk_15": len(cross) == 15,
        "crosswalk_relations_complete": set(row["relation"] for row in cross) == {"SHARED_CORE", "PARTIAL_SHARED", "HERBAL_ONLY"},
        "fixed_pages_only": set(row["page"] for row in statements) == {"f10r", "f11r", "f55v", "f56r"},
        "sealed_absent": all("f84" not in "\t".join(row.values()).lower() for row in statements + primitives),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
