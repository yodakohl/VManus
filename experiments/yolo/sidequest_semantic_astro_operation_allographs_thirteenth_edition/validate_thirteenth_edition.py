#!/usr/bin/env python3
from pathlib import Path
import csv
import json

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


surfaces = read("THIRTEENTH_487_SURFACE_DICTIONARY.tsv")
ledger = read("THIRTEENTH_776_SPEAKABLE_LEDGER.tsv")
units = read("THIRTEENTH_258_READING_UNITS.tsv")
classes = read("THIRTEENTH_RECLASSIFIED_487_SURFACES.tsv")
autonomy = read("THIRTEENTH_776_GROUP_AUTONOMY.tsv")
paradigm = read("ASTRO_OPERATIONAL_46_ALLOGRAPHS.tsv")
checks = {
    "487": len(surfaces) == 487,
    "776": len(ledger) == 776,
    "258": len(units) == 258,
    "forty_six_types": len(paradigm) == 46,
    "fifty_two_groups": sum(int(row["astro_groups"]) for row in paradigm) == 52,
    "fifty_two_ledger_rows": sum(
        row["lookup_mode"] == "REGISTERED_ASTRO_OPERATION_ALLOGRAPH" for row in ledger
    ) == 52,
    "no_partial_astro": not any(
        row["register_status"] == "ASTRO_ONLY" and row["composition_autonomy"] == "PARTIAL"
        for row in classes
    ),
    "full_715": sum(row["autonomy"] == "FULL" for row in autonomy) == 715,
    "partial_13": sum(row["autonomy"] == "PARTIAL" for row in autonomy) == 13,
    "whole_48": sum(row["autonomy"] == "NONE" for row in autonomy) == 48,
    "types_438_12_34": (
        sum(row["composition_autonomy"].startswith("FULL") for row in classes) == 438
        and sum(row["composition_autonomy"] == "PARTIAL" for row in classes) == 12
        and sum(row["composition_autonomy"] == "NONE" for row in classes) == 34
    ),
    "three_splits": sum(row["composition_autonomy"] == "REGISTER_SPLIT" for row in classes) == 3,
    "report": (HERE / "THIRTEENTH_EDITION_REPORT.md").exists(),
}
sealed = "f" + "84"
checks["sealed_absent"] = all(
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
