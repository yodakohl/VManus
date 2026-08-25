#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    entries = read_tsv("PASS971_86_ENTRY_DICTIONARY.tsv")
    surfaces = read_tsv("PASS971_1078_SURFACE_DICTIONARY.tsv")
    encoder = read_tsv("PASS971_948_RECIPE_ENCODER.tsv")
    events = read_tsv("PASS971_2511_EVENT_EDITION.tsv")
    prose = read_tsv("PASS971_2010_PROSE_INTERLINEAR.tsv")
    clauses = read_tsv("PASS971_354_CLAUSE_EDITION.tsv")
    local = read_tsv("PASS971_501_LOCAL_ADDRESS_LEDGER.tsv")
    pages = read_tsv("PASS971_14_PAGE_EDITION.tsv")
    wrapper_rules = read_tsv("PASS971_RENDERER_RULES.tsv")
    positions = read_tsv("PASS971_WRAPPER_POSITION_COUNTS.tsv")
    event_ids = {row["event_id"] for row in events}
    prose_ids = {row["event_id"] for row in prose}
    local_ids = {row["event_id"] for row in local}
    clause_ids = [event_id for row in clauses for event_id in row["event_ids"].split("|")]
    checks = {
        "entries_86": len(entries) == 86,
        "entry_partition": Counter(row["entry_type"] for row in entries) == Counter({"ROOT_OR_LOCAL_SIGN": 56, "FORMULA_CARD": 30}),
        "surfaces_1078": len(surfaces) == 1078 and len({row["surface"] for row in surfaces}) == 1078,
        "recipes_948": len(encoder) == 948 and len({row["component_recipe"] for row in encoder}) == 948,
        "events_2511": len(events) == 2511 and len(event_ids) == 2511,
        "prose_2010": len(prose) == 2010 and len(prose_ids) == 2010,
        "local_501": len(local) == 501 and len(local_ids) == 501,
        "prose_local_partition": prose_ids.isdisjoint(local_ids) and prose_ids | local_ids == event_ids,
        "clauses_354": len(clauses) == 354,
        "clause_membership": len(clause_ids) == 2010 and len(set(clause_ids)) == 2010 and set(clause_ids) == prose_ids,
        "pages_14": len(pages) == 14,
        "page_event_sum": sum(int(row["events"]) for row in pages) == 2511,
        "f75_corrections_10": sum(row["correction_status"] == "F75_TRIANGULAR_INSET_CORRECTED" for row in local) == 10,
        "one_f75_corrected_owner": len({row["owner_id"] for row in local if row["correction_status"] == "F75_TRIANGULAR_INSET_CORRECTED"}) == 1,
        "wrapper_rules_7": len(wrapper_rules) == 7,
        "position_wrappers_present": len(positions) >= 6,
        "all_meanings_present": all(row["portable_value_de"] for row in entries) and all(row["portable_core_de"] for row in surfaces),
        "no_surface_conflicts": not any(row["component_recipe"].startswith("CONFLICT:") or row["portable_core_de"].startswith("CONFLICT:") for row in surfaces),
        "no_sealed_pages": not any("f84" in str(row).lower() for row in entries + surfaces + encoder + events + prose + clauses + local + pages),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "PASS971_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
