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
    lexicon = read("FOUR_HUNDRED_EIGHTIETH_QUANTITY_TRIAD_LEXICON.tsv")
    contexts = read("FOUR_HUNDRED_EIGHTIETH_101_QUANTITY_TRIAD_CONTEXTS.tsv")
    dictionary = read("FOUR_HUNDRED_EIGHTIETH_173_QUANTITY_REVISED_DICTIONARY.tsv")
    prose = read("FOUR_HUNDRED_EIGHTIETH_381_QUANTITY_REVISED_PROSE_EVENTS.tsv")
    statements = read("FOUR_HUNDRED_EIGHTIETH_116_QUANTITY_REVISED_STATEMENTS.tsv")
    astro = read("FOUR_HUNDRED_EIGHTIETH_395_QUANTITY_REVISED_ASTRO_GROUPS.tsv")
    motifs = read("FOUR_HUNDRED_EIGHTIETH_79_QUANTITY_SPECIFIC_MOTIFS.tsv")
    units = read("FOUR_HUNDRED_EIGHTIETH_14_QUANTITY_REVISED_UNIT_EDITIONS.tsv")
    checks = {
        "triad_3": len(lexicon) == 3 and {row["root"] for row in lexicon} == {"AIN", "AIIN", "IIN"},
        "contexts_101": len(contexts) == 101,
        "prose_contexts_61": sum(row["domain"] == "PROSE" for row in contexts) == 61,
        "astro_contexts_40": sum(row["domain"] == "ASTRO" for row in contexts) == 40,
        "dictionary_173": len(dictionary) == 173,
        "prose_381": len(prose) == 381,
        "statements_116": len(statements) == 116,
        "astro_395": len(astro) == 395,
        "motifs_79": len(motifs) == 79,
        "units_14": len(units) == 14,
        "groups_776": sum(int(row["groups"]) for row in units) == 776,
        "all_triad_prose_measure": all(row["action_phase"] == "MEASURE" for row in prose if row["quantity_root"] != "NONE"),
        "fixed_pages_only": {row["page"] for row in prose + astro} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"},
        "sealed_pages_absent": all(not row.get("page", "").startswith("f84") for row in prose + statements + astro + units),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_EIGHTIETH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(result["status"])
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
