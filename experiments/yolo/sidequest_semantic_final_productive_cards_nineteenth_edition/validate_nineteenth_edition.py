#!/usr/bin/env python3
from pathlib import Path
import csv
import json

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


surfaces = read("NINETEENTH_487_SURFACE_DICTIONARY.tsv")
ledger = read("NINETEENTH_776_SPEAKABLE_LEDGER.tsv")
units = read("NINETEENTH_258_READING_UNITS.tsv")
classes = read("NINETEENTH_RECLASSIFIED_487_SURFACES.tsv")
autonomy = read("NINETEENTH_776_GROUP_AUTONOMY.tsv")
paradigm = read("FINAL_PRODUCTIVE_7_SURFACES.tsv")
checks = {
    "487": len(surfaces) == 487,
    "776": len(ledger) == 776,
    "258": len(units) == 258,
    "seven_surfaces": len(paradigm) == 7,
    "eleven_groups": sum(int(row["prose_groups"]) + int(row["astro_groups"]) for row in paradigm) == 11,
    "eleven_ledger_rows": sum(row["lookup_mode"] == "FINAL_PRODUCTIVE_BODY_OR_REGISTER_SPLIT" for row in ledger) == 11,
    "full_769": sum(row["autonomy"] == "FULL" for row in autonomy) == 769,
    "whole_7": sum(row["autonomy"] == "NONE" for row in autonomy) == 7,
    "types_482_2": (
        sum(row["composition_autonomy"].startswith("FULL") for row in classes) == 482
        and sum(row["composition_autonomy"] == "NONE" for row in classes) == 2
    ),
    "three_splits": sum(row["composition_autonomy"] == "REGISTER_SPLIT" for row in classes) == 3,
    "only_two_whole_types": {row["visible_surface"] for row in classes if row["composition_autonomy"] == "NONE"} == {"dl", "talam"},
    "report": (HERE / "NINETEENTH_EDITION_REPORT.md").exists(),
}
sealed = "f" + "84"
checks["sealed_absent"] = all(sealed not in path.read_text(encoding="utf-8").lower() for path in HERE.iterdir() if path.is_file())
result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
(HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
if result["status"] != "PASS":
    raise SystemExit(1)
