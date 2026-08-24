#!/usr/bin/env python3
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    statements = read("FIVE_HUNDRED_SIXTY_THIRD_ONE_HUNDRED_SIXTEEN_STATEMENT_TRANSLATIONS.tsv")
    interlinear = read("FIVE_HUNDRED_SIXTY_THIRD_THREE_HUNDRED_EIGHTY_ONE_INTERLINEAR.tsv")
    records = read("FIVE_HUNDRED_SIXTY_THIRD_ELEVEN_CONTINUOUS_RECORDS.tsv")
    checks = {
        "statements116": len(statements) == 116 and len({row["statement_id"] for row in statements}) == 116,
        "events381": len(interlinear) == 381 and len({row["event_id"] for row in interlinear}) == 381,
        "records11": len(records) == 11 and len({row["record"] for row in records}) == 11,
        "statement_links": {row["statement_id"] for row in interlinear} == {row["statement_id"] for row in statements},
        "statement_sum": sum(int(row["statements"]) for row in records) == 116,
        "complete_translations": all(row["fluent_working_translation_de"].strip() and row["translation_status"] == "CONCRETE_WORKING_READING" for row in statements),
        "complete_event_meaning": all(row["complete_meaning"] == "YES" and row["atomic_card_value_de"].strip() for row in interlinear),
        "fixed_pages": {row["page"] for row in interlinear} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "seal_absent": all(not row["page"].lower().startswith("f84") for row in interlinear),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_SIXTY_THIRD_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for name, value in checks.items():
        print(f"{name}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
