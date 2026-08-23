#!/usr/bin/env python3
from pathlib import Path
import csv
import json

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


surfaces = read("ELEVENTH_487_SURFACE_DICTIONARY.tsv")
ledger = read("ELEVENTH_776_SPEAKABLE_LEDGER.tsv")
units = read("ELEVENTH_258_READING_UNITS.tsv")
classes = read("ELEVENTH_RECLASSIFIED_487_SURFACES.tsv")
autonomy = read("ELEVENTH_776_GROUP_AUTONOMY.tsv")
paradigm = read("IIN_AIIN_8_ALLOGRAPHS.tsv")
checks = {
    "487": len(surfaces) == 487,
    "776": len(ledger) == 776,
    "258": len(units) == 258,
    "eight_allographs": len(paradigm) == 8,
    "eight_revised_groups": sum(
        row["lookup_mode"] == "ASTRO_REGISTERED_IIN_AIIN_ALLOGRAPH" for row in ledger
    ) == 8,
    "full_626": sum(row["autonomy"] == "FULL" for row in autonomy) == 626,
    "partial_102": sum(row["autonomy"] == "PARTIAL" for row in autonomy) == 102,
    "whole_48": sum(row["autonomy"] == "NONE" for row in autonomy) == 48,
    "types_356_94_34": (
        sum(row["composition_autonomy"].startswith("FULL") for row in classes) == 356
        and sum(row["composition_autonomy"] == "PARTIAL" for row in classes) == 94
        and sum(row["composition_autonomy"] == "NONE" for row in classes) == 34
    ),
    "three_splits": sum(row["composition_autonomy"] == "REGISTER_SPLIT" for row in classes) == 3,
    "report": (HERE / "ELEVENTH_EDITION_REPORT.md").exists(),
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
