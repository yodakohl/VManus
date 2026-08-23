#!/usr/bin/env python3
from pathlib import Path
import csv
import json

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


surfaces = read("SIXTEENTH_487_SURFACE_DICTIONARY.tsv")
ledger = read("SIXTEENTH_776_SPEAKABLE_LEDGER.tsv")
units = read("SIXTEENTH_258_READING_UNITS.tsv")
classes = read("SIXTEENTH_RECLASSIFIED_487_SURFACES.tsv")
autonomy = read("SIXTEENTH_776_GROUP_AUTONOMY.tsv")
paradigm = read("SH_HOLD_6_SURFACE_PARADIGM.tsv")
checks = {
    "487": len(surfaces) == 487,
    "776": len(ledger) == 776,
    "258": len(units) == 258,
    "six_surfaces": len(paradigm) == 6,
    "six_groups": sum(int(row["prose_groups"]) + int(row["astro_groups"]) for row in paradigm) == 6,
    "six_ledger_rows": sum(row["lookup_mode"] == "CROSS_REGISTER_SH_HOLD_ROOT" for row in ledger) == 6,
    "full_745": sum(row["autonomy"] == "FULL" for row in autonomy) == 745,
    "whole_31": sum(row["autonomy"] == "NONE" for row in autonomy) == 31,
    "types_462_22": (
        sum(row["composition_autonomy"].startswith("FULL") for row in classes) == 462
        and sum(row["composition_autonomy"] == "NONE" for row in classes) == 22
    ),
    "three_splits": sum(row["composition_autonomy"] == "REGISTER_SPLIT" for row in classes) == 3,
    "report": (HERE / "SIXTEENTH_EDITION_REPORT.md").exists(),
}
sealed = "f" + "84"
checks["sealed_absent"] = all(sealed not in path.read_text(encoding="utf-8").lower() for path in HERE.iterdir() if path.is_file())
result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
(HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
if result["status"] != "PASS":
    raise SystemExit(1)
