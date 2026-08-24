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
    matrix = read("FOUR_HUNDRED_EIGHTY_SECOND_116_ELLIPSIS_MATRIX.tsv")
    counts = read("FOUR_HUNDRED_EIGHTY_SECOND_SLOT_SUPPLY_COUNTS.tsv")
    classes = read("FOUR_HUNDRED_EIGHTY_SECOND_COMPLETION_CLASSES.tsv")
    units = read("FOUR_HUNDRED_EIGHTY_SECOND_14_ELLIPSIS_EXPANDED_UNITS.tsv")
    checks = {
        "statements_116": len(matrix) == 116,
        "event_sum_381": sum(int(row["events"]) for row in matrix) == 381,
        "statement_ids_unique": len({row["statement_id"] for row in matrix}) == 116,
        "supply_rows_24": len(counts) == 24,
        "each_slot_sums_116": all(sum(int(row["statements"]) for row in counts if row["slot"] == slot) == 116 for slot in {"SOURCE", "QUANTITY", "PATH", "TARGET"}),
        "class_sum_116": sum(int(row["statements"]) for row in classes) == 116,
        "all_required_slots_filled": all(row[f"{slot}_status"] != "NOT_REQUIRED" and row[f"{slot}_value_de"] != "—" for row in matrix for slot in ("source", "quantity", "path", "target") if row[f"{slot}_required"] == "YES"),
        "units_14": len(units) == 14,
        "groups_776": sum(int(row["groups"]) for row in units) == 776,
        "fixed_pages_only": {row["page"] for row in matrix + units} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"},
        "sealed_pages_absent": all(not row.get("page", "").startswith("f84") for row in matrix + units),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_EIGHTY_SECOND_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(result["status"])
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
