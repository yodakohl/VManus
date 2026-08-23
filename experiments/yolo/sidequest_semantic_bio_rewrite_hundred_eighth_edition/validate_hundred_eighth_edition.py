#!/usr/bin/env python3
import csv
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    statements = rows("HUNDRED_EIGHTH_56_BIO_STATEMENT_REWRITE.tsv")
    records = rows("HUNDRED_EIGHTH_TWO_CONTINUOUS_BIO_RECORDS.tsv")
    ids = {r["statement_id"] for r in statements}
    checks = {
        "statements_56": len(statements) == 56,
        "B2_22": sum(r["record_unit_id"] == "B2" for r in statements) == 22,
        "B3_34": sum(r["record_unit_id"] == "B3" for r in statements) == 34,
        "records_2": len(records) == 2,
        "ids_unique": len(ids) == 56,
        "all_have_owner": all(r["owner_sequence"] for r in statements),
        "all_have_reading": all(r["creative_practical_reading_de"] for r in statements),
        "transition_not_pipe": all(r["connection_rule"] == "LOCAL_EXEMPLAR_BATCH__NO_DRAWN_CONNECTION" for r in statements if r["statement_id"] in {f"B3-S{i:03d}" for i in range(17, 26)}),
        "mixed_resets_explicit": all(any(word in next(r["creative_practical_reading_de"] for r in statements if r["statement_id"] == sid).lower() for word in ["ohne", "keine"]) for sid in ["B2-S012", "B3-S016", "B3-S026"]),
        "sealed_absent": all("f84" not in "\t".join(r.values()).lower() for r in statements),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
