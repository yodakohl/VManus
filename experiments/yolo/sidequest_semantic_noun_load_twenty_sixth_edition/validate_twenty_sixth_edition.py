#!/usr/bin/env python3
from pathlib import Path
import csv
import json

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


rows = read("TWENTY_SIXTH_116_NOUN_LOAD_AUDIT.tsv")
records = read("TWENTY_SIXTH_ELEVEN_LEAN_RECORDS.tsv")
checks = {
    "116_statements": len(rows) == 116,
    "statement_ids_unique": len({row["statement_id"] for row in rows}) == 116,
    "eleven_records": len(records) == 11,
    "381_groups_statements": sum(int(row["group_count"]) for row in rows) == 381,
    "381_groups_records": sum(int(row["group_count"]) for row in records) == 381,
    "all_original": all(row["original_concrete_reading_de"] for row in rows),
    "all_lean": all(row["lean_owner_clause_reading_de"] for row in rows),
    "all_layers": all(row["literal_card_reading_de"] and row["owner_support"] for row in rows),
    "all_record_text": all(row["lean_record_reading_de"] for row in records),
    "readable": (HERE / "TWENTY_SIXTH_LEAN_ELEVEN_RECORD_EDITION.md").exists(),
    "report": (HERE / "TWENTY_SIXTH_EDITION_REPORT.md").exists(),
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
