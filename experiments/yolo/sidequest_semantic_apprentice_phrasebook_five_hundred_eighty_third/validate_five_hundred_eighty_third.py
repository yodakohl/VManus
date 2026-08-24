#!/usr/bin/env python3
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    phrases = read("FIVE_HUNDRED_EIGHTY_THIRD_RECURRENT_TWO_THREE_COMPONENT_PHRASES.tsv")
    macros = read("FIVE_HUNDRED_EIGHTY_THIRD_FIFTEEN_APPRENTICE_MACROS.tsv")
    mapping = read("FIVE_HUNDRED_EIGHTY_THIRD_ONE_HUNDRED_SIXTEEN_PHRASEBOOK_MAP.tsv")
    checks = {
        "phrases187": len(phrases) == 187,
        "bigrams118_trigrams69": sum(r["n"] == "2" for r in phrases) == 118 and sum(r["n"] == "3" for r in phrases) == 69,
        "recurrent": all(int(r["occurrences"]) >= 2 for r in phrases),
        "macros15": len(macros) == 15 and len({r["macro_id"] for r in macros}) == 15,
        "macro_values": all(r["constituent_values_preserved"] == "YES" for r in macros),
        "statements116": len(mapping) == 116 and len({r["statement_id"] for r in mapping}) == 116,
        "partition73_43": sum(r["phrasebook_mode"] == "USE_TAUGHT_MACRO" for r in mapping) == 73 and sum(r["phrasebook_mode"] == "COMPOSE_ONCE_FROM_CORE" for r in mapping) == 43,
        "values_preserved": all(r["values_preserved"] == "YES" and r["compact_formula_or_expansion_de"] for r in mapping),
        "fixed_pages": {r["page"] for r in mapping} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "seal_absent": all(not r["page"].lower().startswith("f84") for r in mapping),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_EIGHTY_THIRD_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
