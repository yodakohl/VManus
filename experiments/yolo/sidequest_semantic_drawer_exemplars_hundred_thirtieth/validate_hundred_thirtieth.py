#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    exemplars = rows("HUNDRED_THIRTIETH_EIGHT_DRAWER_EXEMPLARS.tsv")
    functions = rows("HUNDRED_THIRTIETH_DRAWER_FUNCTION_COMPARISON.tsv")
    checks = {
        "exemplars_8": len(exemplars) == 8,
        "functions_8": len(functions) == 8,
        "drawers_unique": len({row["drawer"] for row in exemplars}) == 8,
        "each_exemplar_contains_its_drawer": all(int(row["drawer_card_count"]) >= 1 for row in exemplars),
        "statement_ids_unique": len({row["statement_id"] for row in exemplars}) == 8,
        "all_reconstructions_substantial": all(len(row["drawer_reconstructed_instruction_de"].split()) >= 8 for row in exemplars),
        "no_empty_cells": all(all(value for value in row.values()) for table in (exemplars, functions) for row in table),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
