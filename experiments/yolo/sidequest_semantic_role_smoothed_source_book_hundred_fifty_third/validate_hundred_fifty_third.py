#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    clauses = rows("HUNDRED_FIFTY_THIRD_116_LITERAL_AND_SMOOTH_CLAUSES.tsv")
    records = rows("HUNDRED_FIFTY_THIRD_ELEVEN_SMOOTH_RECORDS.tsv")
    checks = {
        "clauses_116": len(clauses) == 116,
        "records_11": len(records) == 11,
        "terminal_90": sum(row["terminal_status"] == "TERMINAL" for row in clauses) == 90,
        "one_close_per_terminal": all(row["smoothed_workshop_clause_de"].count("Schritt schließen") == (1 if row["terminal_status"] == "TERMINAL" else 0) for row in clauses),
        "literal_chains_present": all(row["literal_card_chain_de"] for row in clauses),
        "role_sequences_present": all(row["spoken_role_sequence"] for row in clauses),
        "smoothing_not_dictionary": all(row["smoothing_is_dictionary_value"] == "NO" for row in clauses),
        "dictionary_unchanged": all(row["dictionary_values_changed"] == "NO" for row in records),
        "statement_totals": sum(int(row["statement_count"]) for row in records) == 116,
        "no_empty_cells": all(all(v for v in row.values()) for table in (clauses, records) for row in table),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
