#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    trace = read("FOUR_HUNDRED_SEVENTY_FOURTH_381_REFERENT_TRACE.tsv")
    statements = read("FOUR_HUNDRED_SEVENTY_FOURTH_116_REFERENT_RESOLVED_STATEMENTS.tsv")
    astro = read("FOUR_HUNDRED_SEVENTY_FOURTH_142_ASTRO_LOCUS_REFERENTS.tsv")
    units = read("FOUR_HUNDRED_SEVENTY_FOURTH_14_REFERENT_RESOLVED_UNIT_EDITIONS.tsv")
    checks = {
        "events_381": len(trace) == 381,
        "event_ids_unique": len({row["event_id"] for row in trace}) == 381,
        "statements_116": len(statements) == 116,
        "statement_event_sum_381": sum(int(row["events"]) for row in statements) == 381,
        "astro_loci_142": len(astro) == 142,
        "astro_groups_395": sum(int(row["groups"]) for row in astro) == 395,
        "units_14": len(units) == 14,
        "unit_groups_776": sum(int(row["groups"]) for row in units) == 776,
        "all_references_replaced": all(not re.search(r"\b(?:dies|dort)\b", row["referent_resolved_value_de"], flags=re.I) for row in trace if int(row["reference_tokens_resolved"])),
        "every_record_starts_with_reset": all(next(row for row in trace if row["record_unit_id"] == record)["owner_reset"] == "YES" for record in {row["record_unit_id"] for row in trace}),
        "astro_resets_each_locus": all(row["referent_rule"] == "RESET_AT_EACH_VISIBLE_LOCUS" for row in astro),
        "fixed_pages_only": {row["page"] for row in trace + astro} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"},
        "sealed_pages_absent": all(not row.get("page", "").lower().startswith("f84") for row in trace + statements + astro + units),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_SEVENTY_FOURTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(result["status"])
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
