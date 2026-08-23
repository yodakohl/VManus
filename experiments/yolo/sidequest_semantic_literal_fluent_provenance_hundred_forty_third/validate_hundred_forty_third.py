#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    lessons = rows("HUNDRED_FORTY_THIRD_TEN_LITERAL_FLUENT_LESSONS.tsv")
    provenance = rows("HUNDRED_FORTY_THIRD_EXPANSION_PROVENANCE.tsv")
    repairs = rows("HUNDRED_FORTY_THIRD_FLUENT_OVERREACH_REPAIRS.tsv")
    checks = {
        "lessons_10": len(lessons) == 10,
        "all_lessons_have_provenance": {r["lesson_id"] for r in lessons} == {r["lesson_id"] for r in provenance},
        "source_layers_complete": {r["source_layer"] for r in provenance} == {"CARD_CONTENT", "PICTURE_OWNER", "ACTIVE_REGISTER", "ACTIVE_REGISTER_PLUS_CARD", "BRACKET_FORMULA", "MOULD_GRAMMAR"},
        "overreach_repairs_8": len(repairs) == 8,
        "water_narrowed": any(r["withdraw_or_narrow"] == "water" for r in repairs),
        "patient_narrowed": any(r["withdraw_or_narrow"] == "patient or disease" for r in repairs),
        "no_empty_cells": all(all(v for v in r.values()) for table in (lessons, provenance, repairs) for r in table),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
