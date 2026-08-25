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
    codebook = read("PASS985_159_CODEBOOK.tsv")
    events = read("PASS985_2511_EVENT_INTERLINEAR.tsv")
    roots = read("PASS985_53_ROOT_DICTIONARY.tsv")
    clauses = read("PASS985_354_COMPLETE_CLAUSE_EDITION.tsv")
    addresses = read("PASS985_501_LOCAL_ADDRESS_LEDGER.tsv")
    pages = read("PASS985_14_PAGE_READABLE_EDITION.tsv")
    clause_ids = [event for row in clauses for event in row["event_ids"].split("|")]
    address_ids = [row["event_id"] for row in addresses]
    text = (HERE / "PASS985_CURRENT_WORKING_THEORY.md").read_text(encoding="utf-8")
    checks = {
        "codebook_159": len(codebook) == 159,
        "codebook_ids_unique": len({r["teaching_unit_id"] for r in codebook}) == 159,
        "roots_53": len(roots) == 53,
        "events_2511": len(events) == 2511,
        "event_ids_unique": len({r["event_id"] for r in events}) == 2511,
        "clauses_354": len(clauses) == 354,
        "clause_event_ids_2010": len(clause_ids) == len(set(clause_ids)) == 2010,
        "addresses_501": len(address_ids) == len(set(address_ids)) == 501,
        "event_partitions_disjoint": not set(clause_ids) & set(address_ids),
        "event_partitions_complete": set(clause_ids) | set(address_ids) == {r["event_id"] for r in events},
        "pages_14": len(pages) == 14 and len({r["physical_page"] for r in pages}) == 14,
        "page_events_2511": sum(int(r["events"]) for r in pages) == 2511,
        "all_events_read": all(r["complete_working_reading_de"] for r in events),
        "all_clauses_read": all(r["complete_working_translation_de"] for r in clauses),
        "anchor_recipe": all(word in text for word in ["Blütenkraut", "Sudansatz", "auswringen", "Stehzeit", "nachseihen", "Klarlauf", "kalt stellen"]),
        "sealed_absent": all("f84" not in r["physical_page"].lower() for r in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "PASS985_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
