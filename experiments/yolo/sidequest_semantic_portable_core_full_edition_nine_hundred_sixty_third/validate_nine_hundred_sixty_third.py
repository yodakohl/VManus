#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    events = read_tsv("PASS963_2010_PORTABLE_CORE_INTERLINEAR.tsv")
    clauses = read_tsv("PASS963_354_PORTABLE_CORE_CLAUSES.tsv")
    pages = read_tsv("PASS963_14_PAGE_PORTABLE_EDITION.tsv")
    event_ids = {row["event_id"] for row in events}
    clause_event_ids = [event_id for row in clauses for event_id in row["event_ids"].split("|")]
    checks = {
        "events_2010": len(events) == 2010,
        "events_unique": len(event_ids) == 2010,
        "clauses_354": len(clauses) == 354,
        "clause_membership_exact": len(clause_event_ids) == 2010 and set(clause_event_ids) == event_ids and len(set(clause_event_ids)) == 2010,
        "pages_14": len(pages) == 14,
        "all_event_readings_present": all(row["portable_core_de"] and row["owner_filled_reading_de"] for row in events),
        "all_clause_readings_present": all(row["portable_core_clause_de"] and row["owner_filled_clause_de"] for row in clauses),
        "no_placeholder_values": not any(any(token in row["owner_filled_reading_de"] for token in ("UNKNOWN", "EXEMPLAR_VALUE_UNKNOWN", "FORMAL_LABEL_NOT_WORD")) for row in events),
        "no_sealed_pages": not any("f84" in str(row).lower() for row in events + clauses + pages),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "PASS963_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
