#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    tokens = rows("HUNDRED_FIFTY_EIGHTH_1905_TOKEN_COPIES.tsv")
    statements = rows("HUNDRED_FIFTY_EIGHTH_580_STATEMENT_COPIES.tsv")
    variation = rows("HUNDRED_FIFTY_EIGHTH_116_STATEMENT_VARIATION.tsv")
    records = rows("HUNDRED_FIFTY_EIGHTH_55_RECORD_COPIES.tsv")
    checks = {
        "tokens_1905": len(tokens) == 1905,
        "statements_580": len(statements) == 580,
        "variation_116": len(variation) == 116,
        "records_55": len(records) == 55,
        "profiles_5": len({row["profile"] for row in tokens}) == 5,
        "all_tokens_roundtrip": all(row["roundtrip"] == "PASS" and row["master_card_id"] == row["recovered_master_card_id"] for row in tokens),
        "all_statements_roundtrip": all(row["roundtrip"] == "PASS" for row in statements),
        "all_records_roundtrip": all(row["roundtrip"] == "PASS" for row in records),
        "statement_token_totals": sum(len(row["master_card_sequence"].split("|")) for row in statements) == 1905,
        "variation_partition": sum(row["visibly_variable"] == "YES" for row in variation) + sum(row["visibly_variable"] == "NO" for row in variation) == 116,
        "no_empty_cells": all(all(v for v in row.values()) for table in (tokens, statements, variation, records) for row in table),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
