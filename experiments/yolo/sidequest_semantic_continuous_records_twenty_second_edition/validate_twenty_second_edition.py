#!/usr/bin/env python3
from pathlib import Path
import csv
import json

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


records = read("TWENTY_SECOND_11_CONTINUOUS_RECORDS.tsv")
statement_ids = [item for row in records for item in row["statement_ids"].split("|")]
checks = {
    "eleven_records": len(records) == 11,
    "five_herbal": sum(row["record_id"].startswith("H") for row in records) == 5,
    "six_bio": sum(row["record_id"].startswith("B") for row in records) == 6,
    "116_statements": sum(int(row["statement_count"]) for row in records) == 116,
    "116_unique_ids": len(statement_ids) == len(set(statement_ids)) == 116,
    "381_groups": sum(int(row["group_count"]) for row in records) == 381,
    "all_owners": all(row["image_owner_chain"] for row in records),
    "all_literals": all(row["literal_card_chain_de"] for row in records),
    "all_translations": all(row["continuous_workshop_translation_de"] for row in records),
    "all_rivals": all(row["continuous_technical_rival_de"] for row in records),
    "report": (HERE / "TWENTY_SECOND_EDITION_REPORT.md").exists(),
}
sealed = "f" + "84"
checks["sealed_absent"] = all(sealed not in path.read_text(encoding="utf-8").lower() for path in HERE.iterdir() if path.is_file())
result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
(HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
if result["status"] != "PASS":
    raise SystemExit(1)
