#!/usr/bin/env python3
from pathlib import Path
import csv
import json

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


surfaces = read("FIFTEENTH_487_SURFACE_DICTIONARY.tsv")
ledger = read("FIFTEENTH_776_SPEAKABLE_LEDGER.tsv")
units = read("FIFTEENTH_258_READING_UNITS.tsv")
classes = read("FIFTEENTH_RECLASSIFIED_487_SURFACES.tsv")
autonomy = read("FIFTEENTH_776_GROUP_AUTONOMY.tsv")
paradigm = read("ASTRO_PRIMITIVE_10_SURFACES.tsv")
predictions = read("ASTRO_PRIMITIVE_FORWARD_CELLS.tsv")
checks = {
    "487": len(surfaces) == 487,
    "776": len(ledger) == 776,
    "258": len(units) == 258,
    "ten_surfaces": len(paradigm) == 10,
    "fifteen_groups": sum(int(row["astro_groups"]) for row in paradigm) == 15,
    "six_predictions": len(predictions) == 6,
    "fifteen_ledger_rows": sum(
        row["lookup_mode"] == "ASTRO_LOCAL_PRIMITIVE_MICROCODE" for row in ledger
    ) == 15,
    "full_742": sum(row["autonomy"] == "FULL" for row in autonomy) == 742,
    "partial_0": not any(row["autonomy"] == "PARTIAL" for row in autonomy),
    "whole_34": sum(row["autonomy"] == "NONE" for row in autonomy) == 34,
    "types_459_25": (
        sum(row["composition_autonomy"].startswith("FULL") for row in classes) == 459
        and sum(row["composition_autonomy"] == "NONE" for row in classes) == 25
    ),
    "three_splits": sum(row["composition_autonomy"] == "REGISTER_SPLIT" for row in classes) == 3,
    "report": (HERE / "FIFTEENTH_EDITION_REPORT.md").exists(),
}
sealed = "f" + "84"
checks["sealed_absent"] = all(
    sealed not in path.read_text(encoding="utf-8").lower()
    for path in HERE.iterdir()
    if path.is_file()
)
result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
(HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
if result["status"] != "PASS":
    raise SystemExit(1)
