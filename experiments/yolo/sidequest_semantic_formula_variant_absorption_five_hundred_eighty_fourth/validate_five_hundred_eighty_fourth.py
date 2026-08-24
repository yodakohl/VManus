#!/usr/bin/env python3
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    oneoffs = read("FIVE_HUNDRED_EIGHTY_FOURTH_FORTY_THREE_ONE_OFF_NEAREST_FORMULAS.tsv")
    rules = read("FIVE_HUNDRED_EIGHTY_FOURTH_SIMPLE_VARIANT_RULES.tsv")
    mapping = read("FIVE_HUNDRED_EIGHTY_FOURTH_REVISED_ONE_HUNDRED_SIXTEEN_FORMULA_MAP.tsv")
    checks = {
        "oneoffs43": len(oneoffs) == 43 and len({r["statement_id"] for r in oneoffs}) == 43,
        "statements116": len(mapping) == 116 and len({r["statement_id"] for r in mapping}) == 116,
        "partition73_21_10_12": sum(r["revised_learning_mode"] == "TAUGHT_MACRO" for r in mapping) == 73 and sum(r["revised_learning_mode"] == "SIMPLE_ONE_EDIT_VARIANT" for r in mapping) == 21 and sum(r["revised_learning_mode"] == "EXTENDED_TWO_EDIT_VARIANT" for r in mapping) == 10 and sum(r["revised_learning_mode"] == "FREE_COMPOSITION" for r in mapping) == 12,
        "distance_matches": all((int(r["edit_distance"]) == 1) == (r["learning_mode"] == "SIMPLE_ONE_EDIT_VARIANT") for r in oneoffs),
        "rules_nonempty": len(rules) > 0 and sum(int(r["statements"]) for r in rules) == 21,
        "coverage94": sum(r["revised_learning_mode"] in {"TAUGHT_MACRO", "SIMPLE_ONE_EDIT_VARIANT"} for r in mapping) == 94,
        "values_preserved": all(r["values_preserved"] == "YES" for r in mapping),
        "fixed_pages": {r["page"] for r in mapping} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "seal_absent": all(not r["page"].lower().startswith("f84") for r in mapping),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_EIGHTY_FOURTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
