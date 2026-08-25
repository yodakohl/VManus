#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
BIO_PAGES = {"f75r", "f81v", "f82r", "f83r"}


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    events = read("PASS987_1280_BIOLOGICAL_EVENT_PHRASES.tsv")
    clauses = read("PASS987_318_BIOLOGICAL_NATURAL_CLAUSES.tsv")
    pages = read("PASS987_FOUR_BIOLOGICAL_PAGE_READINGS.tsv")
    bound_ids = [event_id for row in clauses for event_id in row["event_ids"].split("|")]
    checks = {
        "events_1280": len(events) == 1280,
        "event_ids_unique": len({row["event_id"] for row in events}) == 1280,
        "clauses_318": len(clauses) == 318,
        "clause_ids_unique": len({row["clause_id"] for row in clauses}) == 318,
        "clause_event_partition": len(bound_ids) == len(set(bound_ids)) == 1280,
        "event_binding_exact": set(bound_ids) == {row["event_id"] for row in events},
        "pages_four": len(pages) == 4 and {row["physical_page"] for row in pages} == BIO_PAGES,
        "page_event_sum": sum(int(row["events"]) for row in pages) == 1280,
        "manual_fifteen": sum(row["rewrite_mode"] == "MANUAL_LONG_CLAUSE_REWRITE" for row in clauses) == 15,
        "all_events_naturalized": all(row["natural_event_phrase_de"] for row in events),
        "all_clauses_naturalized": all(row["natural_workshop_reading_de"] for row in clauses),
        "all_exact_chains_present": all(row["exact_event_phrase_chain_de"] for row in clauses),
        "local_scope_only": all(row["global_network_claim"] == "NONE_LOCAL_STATION_ONLY" for row in clauses),
        "sealed_absent": all("f84" not in row["physical_page"].lower() for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "PASS987_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
