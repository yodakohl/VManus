#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    modules = read("SIX_HUNDRED_NINETEENTH_8_WORKSHOP_MODULES.tsv")
    statements = read("SIX_HUNDRED_NINETEENTH_116_STATEMENT_MODULE_MAP.tsv")
    matrix = read("SIX_HUNDRED_NINETEENTH_48_CASE_MODULE_MATRIX.tsv")
    ngrams = read("SIX_HUNDRED_NINETEENTH_17_EXACT_CROSS_CASE_NGRAMS.tsv")
    checks = {
        "modules8": len(modules) == 8 and len({row["module_id"] for row in modules}) == 8,
        "statements116": len(statements) == 116 and sum(int(row["event_count"]) for row in statements) == 381,
        "all_statements_covered": all(int(row["module_count"]) >= 1 for row in statements),
        "matrix48": len(matrix) == 48,
        "six_cases": {row["case_id"] for row in matrix} == {f"C{i}" for i in range(1, 7)},
        "ngrams17": len(ngrams) == 17,
        "two_trigrams": sum(row["ngram_length"] == "3" for row in ngrams) == 2,
        "all_ngrams_cross_case": all(int(row["case_count"]) >= 2 for row in ngrams),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_NINETEENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
