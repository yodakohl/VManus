#!/usr/bin/env python3
"""Validate endpoint and M09 branch separation."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    audit = rows("SIX_HUNDRED_FIFTY_FIFTH_28_ENDPOINT_AUDIT.tsv")
    ends = rows("SIX_HUNDRED_FIFTY_FIFTH_9_STATEMENT_END_MOTIFS.tsv")
    branches = rows("SIX_HUNDRED_FIFTY_FIFTH_4_M09_BRANCHES.tsv")
    checks = {
        "twenty_eight_instances": len(audit) == 28,
        "nine_end_instances": len(ends) == 9,
        "seven_explicit_closes": sum(row["endpoint_class"] == "EXPLICIT_CLOSE_AT_END" for row in audit) == 7,
        "two_unmarked_ends": sum(row["endpoint_class"] == "STATEMENT_END_WITHOUT_CLOSE_CARD" for row in audit) == 2,
        "no_close_before_material": all(row["endpoint_class"] != "CLOSE_CARD_BEFORE_FURTHER_MATERIAL" for row in audit),
        "nineteen_nonterminal": sum(row["endpoint_class"] == "NONTERMINAL_MOTIF" for row in audit) == 19,
        "four_m09_branches": len(branches) == 4,
        "two_open_m09": sum(row["branch"] == "M09O_OPEN_CONTINUATION" for row in branches) == 2,
        "two_closed_m09": sum(row["branch"] == "M09C_SHORT_CLOSE" for row in branches) == 2,
        "open_m09_never_ends": all(row["ends_statement"] == "NO" for row in branches if row["branch"] == "M09O_OPEN_CONTINUATION"),
        "closed_m09_always_ends": all(row["ends_statement"] == "YES" for row in branches if row["branch"] == "M09C_SHORT_CLOSE"),
        "unmarked_ends_are_m01": all(row["motif_id"] == "M01_ITEM_MEASURE_FRAME" for row in ends if row["contains_exact_close_card"] == "NO"),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_FIFTY_FIFTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, passed in checks.items():
        print(f"{name}\t{'PASS' if passed else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
