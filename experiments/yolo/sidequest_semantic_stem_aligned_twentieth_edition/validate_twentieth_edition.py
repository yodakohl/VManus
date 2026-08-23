#!/usr/bin/env python3
from pathlib import Path
import csv
import json

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


dictionary = read("TWENTIETH_487_CURRENT_DICTIONARY.tsv")
events = read("TWENTIETH_776_EVENT_BINDING.tsv")
units = read("TWENTIETH_258_UNIT_TRANSLATIONS.tsv")
prose = read("TWENTIETH_116_PROSE_STATEMENTS.tsv")
astro = read("TWENTIETH_142_ASTRO_LOCI.tsv")
checks = {
    "487": len(dictionary) == 487,
    "776": len(events) == 776,
    "258": len(units) == 258,
    "116": len(prose) == 116,
    "142": len(astro) == 142,
    "unit_group_sum": sum(int(row["group_count"]) for row in units) == 776,
    "all_surfaces": all(row["surface_sequence"] for row in units),
    "all_atoms": all(row["atom_sequence"] for row in units),
    "all_literals": all(row["literal_card_reading_de"] for row in units),
    "all_expansions": all(row["owner_expansion_de"] for row in units),
    "astro_expansions_current": all(
        row["owner_expansion_de"].endswith(row["literal_card_reading_de"])
        for row in astro
    ),
    "full_769": sum(row["autonomy"] == "FULL" for row in events) == 769,
    "whole_7": sum(row["autonomy"] == "NONE" for row in events) == 7,
    "no_light_gloss": "grundlicht" not in (HERE / "COMPLETE_TEN_PAGE_STEM_ALIGNED_TWENTIETH_EDITION.md").read_text(encoding="utf-8").lower(),
    "report": (HERE / "TWENTIETH_EDITION_REPORT.md").exists(),
}
sealed = "f" + "84"
checks["sealed_absent"] = all(sealed not in path.read_text(encoding="utf-8").lower() for path in HERE.iterdir() if path.is_file())
result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
(HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
if result["status"] != "PASS":
    raise SystemExit(1)
