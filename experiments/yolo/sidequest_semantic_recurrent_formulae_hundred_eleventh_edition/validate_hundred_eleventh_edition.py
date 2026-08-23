#!/usr/bin/env python3
import csv
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    formulae = rows("HUNDRED_ELEVENTH_TEN_WORKSHOP_FORMULAE.tsv")
    occ = rows("HUNDRED_ELEVENTH_FORMULA_OCCURRENCES.tsv")
    statements = rows("HUNDRED_ELEVENTH_116_FORMULA_ANNOTATED_STATEMENTS.tsv")
    checks = {
        "formulae_10": len(formulae) == 10,
        "occurrences_22": len(occ) == 22,
        "statements_116": len(statements) == 116,
        "formula_ids_unique": len({r["formula_id"] for r in formulae}) == 10,
        "occurrence_formula_known": {r["formula_id"] for r in occ} == {r["formula_id"] for r in formulae},
        "wf01_two_records": next(r for r in formulae if r["formula_id"] == "WF01")["record_count"] == "2",
        "wf04_four_occurrences": next(r for r in formulae if r["formula_id"] == "WF04")["occurrence_count"] == "4",
        "longest_no_overlap": all(len(r["formula_tags"].split("|")) == len(r["formula_card_spans"].split("|")) for r in statements),
        "sealed_absent": all("f84" not in "\t".join(r.values()).lower() for r in occ),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
