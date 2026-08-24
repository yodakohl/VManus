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
    lexicon = read("FOUR_HUNDRED_EIGHTY_FIRST_DIRECTION_TRIAD_LEXICON.tsv")
    contexts = read("FOUR_HUNDRED_EIGHTY_FIRST_156_DIRECTION_CONTEXTS.tsv")
    dictionary = read("FOUR_HUNDRED_EIGHTY_FIRST_173_DIRECTION_REVISED_DICTIONARY.tsv")
    prose = read("FOUR_HUNDRED_EIGHTY_FIRST_381_DIRECTION_REVISED_PROSE_EVENTS.tsv")
    astro = read("FOUR_HUNDRED_EIGHTY_FIRST_395_DIRECTION_REVISED_ASTRO_GROUPS.tsv")
    statements = read("FOUR_HUNDRED_EIGHTY_FIRST_116_DIRECTION_REVISED_STATEMENTS.tsv")
    formulas = read("FOUR_HUNDRED_EIGHTY_FIRST_116_SOURCE_QUANTITY_PATH_TARGET_FORMULAS.tsv")
    units = read("FOUR_HUNDRED_EIGHTY_FIRST_14_DIRECTION_REVISED_UNIT_EDITIONS.tsv")
    checks = {
        "triad_3": len(lexicon) == 3 and {row["root"] for row in lexicon} == {"AR", "AL", "AIR"},
        "contexts_156": len(contexts) == 156,
        "prose_direction_events_58": sum(row["domain"] == "PROSE" for row in contexts) == 58,
        "astro_direction_groups_98": sum(row["domain"] == "ASTRO" for row in contexts) == 98,
        "dictionary_173": len(dictionary) == 173,
        "prose_381": len(prose) == 381,
        "astro_395": len(astro) == 395,
        "statements_116": len(statements) == 116,
        "formulas_116": len(formulas) == 116,
        "strict_formula_1": sum(row["strict_four_slot_formula"] == "YES" for row in formulas) == 1,
        "extended_formulas_2": sum(row["four_slot_with_receiver"] == "YES" for row in formulas) == 2,
        "units_14": len(units) == 14,
        "groups_776": sum(int(row["groups"]) for row in units) == 776,
        "fixed_pages_only": {row["page"] for row in prose + astro} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"},
        "sealed_pages_absent": all(not row.get("page", "").startswith("f84") for row in prose + statements + astro + units),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_EIGHTY_FIRST_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(result["status"])
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
