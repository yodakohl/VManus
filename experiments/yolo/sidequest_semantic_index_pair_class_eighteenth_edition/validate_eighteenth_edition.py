#!/usr/bin/env python3
from pathlib import Path
import csv
import json

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


surfaces = read("EIGHTEENTH_487_SURFACE_DICTIONARY.tsv")
ledger = read("EIGHTEENTH_776_SPEAKABLE_LEDGER.tsv")
units = read("EIGHTEENTH_258_READING_UNITS.tsv")
classes = read("EIGHTEENTH_RECLASSIFIED_487_SURFACES.tsv")
autonomy = read("EIGHTEENTH_776_GROUP_AUTONOMY.tsv")
paradigm = read("INDEX_PAIR_CLASS_11_SURFACES.tsv")
checks = {
    "487": len(surfaces) == 487,
    "776": len(ledger) == 776,
    "258": len(units) == 258,
    "eleven_surfaces": len(paradigm) == 11,
    "seven_new": sum(row["previous_autonomy"] == "NONE" for row in paradigm) == 7,
    "eleven_ledger_rows": sum(row["lookup_mode"] == "ASTRO_LOCAL_INDEX_PAIR_CLASS_MICROCODE" for row in ledger) == 11,
    "full_758": sum(row["autonomy"] == "FULL" for row in autonomy) == 758,
    "whole_18": sum(row["autonomy"] == "NONE" for row in autonomy) == 18,
    "types_475_9": (
        sum(row["composition_autonomy"].startswith("FULL") for row in classes) == 475
        and sum(row["composition_autonomy"] == "NONE" for row in classes) == 9
    ),
    "no_light_gloss": not any("licht" in row["short_spoken_value_de"].lower() for row in classes),
    "three_splits": sum(row["composition_autonomy"] == "REGISTER_SPLIT" for row in classes) == 3,
    "report": (HERE / "EIGHTEENTH_EDITION_REPORT.md").exists(),
}
sealed = "f" + "84"
checks["sealed_absent"] = all(sealed not in path.read_text(encoding="utf-8").lower() for path in HERE.iterdir() if path.is_file())
result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
(HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
if result["status"] != "PASS":
    raise SystemExit(1)
