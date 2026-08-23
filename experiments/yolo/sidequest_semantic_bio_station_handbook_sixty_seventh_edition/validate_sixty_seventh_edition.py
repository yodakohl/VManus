#!/usr/bin/env python3
"""Validate the compact Biological station handbook."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent
ALLOWED = {"f81v", "f82r", "f83r"}


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    groups = read_tsv("SIXTY_SEVENTH_281_BIO_GROUP_EDITION.tsv")
    statements = read_tsv("SIXTY_SEVENTH_97_BIO_STATEMENTS.tsv")
    stations = read_tsv("SIXTY_SEVENTH_16_LOCAL_STATIONS.tsv")
    records = read_tsv("SIXTY_SEVENTH_6_COMPACT_BIO_RECORDS.tsv")
    checks = {
        "three_pages": {row["page"] for row in groups} == ALLOWED,
        "281_groups": len(groups) == 281 and len({row["source_group_id"] for row in groups}) == 281,
        "ninety_seven_statements": len(statements) == 97 and len({row["unit_id"] for row in statements}) == 97,
        "sixteen_local_stations": len(stations) == 16 and len({row["owner_id"] for row in stations}) == 16,
        "six_records": len(records) == 6 and {row["record_id"] for row in records} == {"B1", "B2", "B3", "B4", "B5", "B6"},
        "115_fields": sum(int(row["field_count"]) for row in records) == 115,
        "statement_counts_reconcile": sum(int(row["statement_count"]) for row in records) == 97,
        "group_counts_reconcile": sum(int(row["group_count"]) for row in records) == 281,
        "no_global_network": all(row["global_connection"] == "NONE" for row in stations) and all(row["global_flow_claim"] == "NONE" for row in records),
        "all_statements_have_reset_rule": all(row["station_reset_rule"] for row in statements),
        "sealed_pages_absent": all("f84" not in "\t".join(row.values()).lower() for row in groups + statements + stations + records),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
