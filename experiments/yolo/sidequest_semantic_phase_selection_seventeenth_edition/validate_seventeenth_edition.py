#!/usr/bin/env python3
from pathlib import Path
import csv
import json

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


surfaces = read("SEVENTEENTH_487_SURFACE_DICTIONARY.tsv")
ledger = read("SEVENTEENTH_776_SPEAKABLE_LEDGER.tsv")
units = read("SEVENTEENTH_258_READING_UNITS.tsv")
classes = read("SEVENTEENTH_RECLASSIFIED_487_SURFACES.tsv")
autonomy = read("SEVENTEENTH_776_GROUP_AUTONOMY.tsv")
paradigm = read("PHASE_SELECTION_6_SURFACES.tsv")
checks = {
    "487": len(surfaces) == 487,
    "776": len(ledger) == 776,
    "258": len(units) == 258,
    "six_surfaces": len(paradigm) == 6,
    "six_ledger_rows": sum(row["lookup_mode"] == "ASTRO_LOCAL_PHASE_SELECTION_MICROCODE" for row in ledger) == 6,
    "full_751": sum(row["autonomy"] == "FULL" for row in autonomy) == 751,
    "whole_25": sum(row["autonomy"] == "NONE" for row in autonomy) == 25,
    "types_468_16": (
        sum(row["composition_autonomy"].startswith("FULL") for row in classes) == 468
        and sum(row["composition_autonomy"] == "NONE" for row in classes) == 16
    ),
    "three_splits": sum(row["composition_autonomy"] == "REGISTER_SPLIT" for row in classes) == 3,
    "report": (HERE / "SEVENTEENTH_EDITION_REPORT.md").exists(),
}
sealed = "f" + "84"
checks["sealed_absent"] = all(sealed not in path.read_text(encoding="utf-8").lower() for path in HERE.iterdir() if path.is_file())
result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
(HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
if result["status"] != "PASS":
    raise SystemExit(1)
