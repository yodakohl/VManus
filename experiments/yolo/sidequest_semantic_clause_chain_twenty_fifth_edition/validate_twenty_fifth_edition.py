#!/usr/bin/env python3
from pathlib import Path
import csv
import json

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


clauses = read("TWENTY_FIFTH_254_SOURCE_CLAUSES.tsv")
statements = read("TWENTY_FIFTH_116_MULTI_CLAUSE_STATEMENTS.tsv")
event_ids = [item for row in clauses for item in row["member_event_ids"].split("|")]
checks = {
    "254_clauses": len(clauses) == 254,
    "116_statements": len(statements) == 116,
    "eleven_records": len({row["record_id"] for row in statements}) == 11,
    "381_groups": sum(int(row["group_count"]) for row in statements) == 381,
    "381_event_members": len(event_ids) == len(set(event_ids)) == 381,
    "clause_member_counts": all(len(row["member_event_ids"].split("|")) == int(row["member_event_count"]) for row in clauses),
    "surface_roundtrip": all(row["surface_chain_matches_current"] == "YES" for row in statements),
    "all_heads_named": all(row["source_clause_family"] and row["latin_like_source_clause"] for row in clauses),
    "all_statement_chains": all(row["latin_like_source_chain"] and row["german_clause_chain_de"] for row in statements),
    "readable": (HERE / "TWENTY_FIFTH_ELEVEN_CLAUSE_RECORDS.md").exists(),
    "report": (HERE / "TWENTY_FIFTH_EDITION_REPORT.md").exists(),
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
