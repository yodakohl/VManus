#!/usr/bin/env python3
from pathlib import Path
import csv
import json

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


surfaces = read("TENTH_487_SURFACE_DICTIONARY.tsv")
ledger = read("TENTH_776_SPEAKABLE_LEDGER.tsv")
units = read("TENTH_258_READING_UNITS.tsv")
classes = read("TENTH_RECLASSIFIED_487_SURFACES.tsv")
autonomy = read("TENTH_776_GROUP_AUTONOMY.tsv")
paradigm = read("ASTRO_EE_21_SURFACE_PARADIGM.tsv")
checks = {
    "487_surfaces": len(surfaces) == 487,
    "776_groups": len(ledger) == 776,
    "258_units": len(units) == 258,
    "twenty_one_grade_surfaces": len(paradigm) == 21,
    "twenty_one_grade_groups": sum(int(row["astro_groups"]) for row in paradigm) == 21,
    "twenty_one_ledger_groups": sum(
        row["lookup_mode"] == "ASTRO_BOUND_EE_GRADE" for row in ledger
    ) == 21,
    "full_618": sum(row["autonomy"] == "FULL" for row in autonomy) == 618,
    "partial_108": sum(row["autonomy"] == "PARTIAL" for row in autonomy) == 108,
    "whole_50": sum(row["autonomy"] == "NONE" for row in autonomy) == 50,
    "types_348_100_36": (
        sum(row["composition_autonomy"].startswith("FULL") for row in classes) == 348
        and sum(row["composition_autonomy"] == "PARTIAL" for row in classes) == 100
        and sum(row["composition_autonomy"] == "NONE" for row in classes) == 36
    ),
    "three_splits": sum(
        row["composition_autonomy"] == "REGISTER_SPLIT" for row in classes
    ) == 3,
    "report_present": (HERE / "TENTH_EDITION_REPORT.md").exists(),
}
sealed = "f" + "84"
checks["sealed_token_absent"] = all(
    sealed not in path.read_text(encoding="utf-8").lower()
    for path in HERE.iterdir()
    if path.is_file()
)
result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
(HERE / "VALIDATION.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps(result, ensure_ascii=False, indent=2))
if result["status"] != "PASS":
    raise SystemExit(1)
