#!/usr/bin/env python3
from pathlib import Path
import csv
import json

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


surfaces = read("NINTH_487_SURFACE_DICTIONARY.tsv")
ledger = read("NINTH_776_SPEAKABLE_LEDGER.tsv")
units = read("NINTH_258_READING_UNITS.tsv")
classes = read("NINTH_RECLASSIFIED_487_SURFACES.tsv")
autonomy = read("NINTH_776_GROUP_AUTONOMY.tsv")
paradigm = read("YD_4_SURFACE_PARADIGM.tsv")
checks = {
    "487_surfaces": len(surfaces) == 487,
    "776_groups": len(ledger) == 776,
    "258_units": len(units) == 258,
    "four_yd_surfaces": len(paradigm) == 4,
    "five_yd_groups": sum(int(row["astro_groups"]) for row in paradigm) == 5,
    "five_yd_ledger_groups": sum(
        row["lookup_mode"] == "ASTRO_LOCAL_YD_ACTIVE_ROW" for row in ledger
    ) == 5,
    "full_597": sum(row["autonomy"] == "FULL" for row in autonomy) == 597,
    "partial_117": sum(row["autonomy"] == "PARTIAL" for row in autonomy) == 117,
    "whole_62": sum(row["autonomy"] == "NONE" for row in autonomy) == 62,
    "three_splits": sum(
        row["composition_autonomy"] == "REGISTER_SPLIT" for row in classes
    ) == 3,
    "report_present": (HERE / "NINTH_EDITION_REPORT.md").exists(),
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
