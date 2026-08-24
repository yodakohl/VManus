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
    events = read("FOUR_HUNDRED_SEVENTY_FIFTH_381_READABLE_EVENT_ALIGNMENT.tsv")
    statements = read("FOUR_HUNDRED_SEVENTY_FIFTH_116_READABLE_WORKSHOP_STATEMENTS.tsv")
    astro = read("FOUR_HUNDRED_SEVENTY_FIFTH_142_READABLE_ASTRO_LOCI.tsv")
    units = read("FOUR_HUNDRED_SEVENTY_FIFTH_14_READABLE_UNIT_EDITIONS.tsv")
    listed = [event for row in statements for event in row["event_ids"].split("|")]
    checks = {
        "events_381": len(events) == 381,
        "event_ids_unique": len({row["event_id"] for row in events}) == 381,
        "statements_116": len(statements) == 116,
        "statement_event_alignment_381": len(listed) == 381 and set(listed) == {row["event_id"] for row in events},
        "statement_event_counts": all(len(row["event_ids"].split("|")) == int(row["events"]) for row in statements),
        "astro_loci_142": len(astro) == 142,
        "astro_groups_395": sum(int(row["groups"]) for row in astro) == 395,
        "units_14": len(units) == 14,
        "groups_776": sum(int(row["groups"]) for row in units) == 776,
        "all_readings_nonempty": all(row["readable_workshop_statement_de"] for row in statements) and all(row["readable_locus_de"] for row in astro),
        "fixed_pages_only": {row["page"] for row in events + astro} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"},
        "sealed_pages_absent": all(not row.get("page", "").startswith("f84") for row in events + statements + astro + units),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_SEVENTY_FIFTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(result["status"])
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
