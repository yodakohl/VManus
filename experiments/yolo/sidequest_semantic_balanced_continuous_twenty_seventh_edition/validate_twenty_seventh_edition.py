#!/usr/bin/env python3
from pathlib import Path
import csv
import json

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


rows = read("TWENTY_SEVENTH_11_BALANCED_RECORDS.tsv")
statement_ids = [item for row in rows for item in row["statement_ids"].split("|")]
checks = {
    "eleven_records": len(rows) == 11,
    "five_herbal": sum(row["record_id"].startswith("H") for row in rows) == 5,
    "six_bio": sum(row["record_id"].startswith("B") for row in rows) == 6,
    "116_statements": sum(int(row["statement_count"]) for row in rows) == 116,
    "116_unique_statement_ids": len(statement_ids) == len(set(statement_ids)) == 116,
    "381_groups": sum(int(row["group_count"]) for row in rows) == 381,
    "all_balanced": all(row["balanced_continuous_reading_de"] for row in rows),
    "all_bets_explicit": all(row["retained_creative_bets"] for row in rows),
    "all_withdrawals_explicit": all(row["withdrawn_overdetail"] for row in rows),
    "all_baselines": all(row["lean_clause_baseline_de"] for row in rows),
    "readable": (HERE / "TWENTY_SEVENTH_BALANCED_CONTINUOUS_EDITION.md").exists(),
    "report": (HERE / "TWENTY_SEVENTH_EDITION_REPORT.md").exists(),
}
sealed = "f" + "84"
checks["sealed_absent"] = all(
    sealed not in path.read_text(encoding="utf-8").lower()
    for path in HERE.iterdir()
    if path.is_file()
)
result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
(HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
if result["status"] != "PASS":
    raise SystemExit(1)
