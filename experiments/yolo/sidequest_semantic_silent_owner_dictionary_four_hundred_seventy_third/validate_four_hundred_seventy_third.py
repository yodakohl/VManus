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
    prose = read("FOUR_HUNDRED_SEVENTY_THIRD_116_OWNER_EXPANDED_PROSE_STATEMENTS.tsv")
    astro = read("FOUR_HUNDRED_SEVENTY_THIRD_142_OWNER_EXPANDED_ASTRO_LOCI.tsv")
    units = read("FOUR_HUNDRED_SEVENTY_THIRD_14_OWNER_EXPANDED_UNIT_EDITIONS.tsv")
    dictionary = read("FOUR_HUNDRED_SEVENTY_THIRD_OWNER_CLASS_DICTIONARY.tsv")
    checks = {
        "prose_statements_116": len(prose) == 116,
        "prose_events_381": sum(int(row["events"]) for row in prose) == 381,
        "astro_loci_142": len(astro) == 142,
        "astro_groups_395": sum(int(row["groups"]) for row in astro) == 395,
        "units_14": len(units) == 14,
        "groups_776": sum(int(row["groups"]) for row in units) == 776,
        "statement_ids_unique": len({row["statement_id"] for row in prose}) == 116,
        "loci_unique": len({row["locus"] for row in astro}) == 142,
        "all_prose_have_owner": all(row["concrete_owner_de"] and row["dies_resolves_to_de"] for row in prose),
        "all_astro_have_owner": all(row["concrete_owner_de"] and row["dies_resolves_to_de"] for row in astro),
        "all_classes_defined": {row["owner_class"] for row in prose + astro} == {row["owner_class"] for row in dictionary},
        "fixed_pages_only": {row["page"] for row in prose + astro} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"},
        "no_sealed_pages": all("f84" not in "\t".join(row.values()).lower() for row in prose + astro + units + dictionary),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_SEVENTY_THIRD_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(result["status"])
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
