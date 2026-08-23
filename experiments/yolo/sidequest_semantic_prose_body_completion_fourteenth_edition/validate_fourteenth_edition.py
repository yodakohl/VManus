#!/usr/bin/env python3
from pathlib import Path
import csv
import json

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


surfaces = read("FOURTEENTH_487_SURFACE_DICTIONARY.tsv")
ledger = read("FOURTEENTH_776_SPEAKABLE_LEDGER.tsv")
units = read("FOURTEENTH_258_READING_UNITS.tsv")
classes = read("FOURTEENTH_RECLASSIFIED_487_SURFACES.tsv")
autonomy = read("FOURTEENTH_776_GROUP_AUTONOMY.tsv")
cards = read("PROSE_12_REMAINING_CARDS.tsv")
checks = {
    "487": len(surfaces) == 487,
    "776": len(ledger) == 776,
    "258": len(units) == 258,
    "twelve_cards": len(cards) == 12,
    "twelve_composed_groups": sum(
        row["lookup_mode"] == "COMPOSED_LEARNED_PROSE_BODY" for row in ledger
    ) == 12,
    "one_whole_command": sum(
        row["lookup_mode"] == "MEMORIZED_WHOLE_COMMAND" for row in ledger
    ) == 1,
    "no_partial_groups": not any(row["autonomy"] == "PARTIAL" for row in autonomy),
    "full_727": sum(row["autonomy"] == "FULL" for row in autonomy) == 727,
    "whole_49": sum(row["autonomy"] == "NONE" for row in autonomy) == 49,
    "types_449_0_35": (
        sum(row["composition_autonomy"].startswith("FULL") for row in classes) == 449
        and not any(row["composition_autonomy"] == "PARTIAL" for row in classes)
        and sum(row["composition_autonomy"] == "NONE" for row in classes) == 35
    ),
    "three_splits": sum(row["composition_autonomy"] == "REGISTER_SPLIT" for row in classes) == 3,
    "talam_not_aspect": next(
        row for row in classes if row["visible_surface"] == "talam"
    )["common_atom_sequences"] == "TALAM",
    "report": (HERE / "FOURTEENTH_EDITION_REPORT.md").exists(),
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
