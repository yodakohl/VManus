#!/usr/bin/env python3
from pathlib import Path
import csv
import json

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


templates = read("TWENTY_FOURTH_SOURCE_ORDER_TEMPLATES.tsv")
units = read("TWENTY_FOURTH_258_SOURCE_PHRASE_EDITION.tsv")
sections = read("TWENTY_FOURTH_FOURTEEN_SOURCE_SEQUENCES.tsv")
checks = {
    "sixteen_templates": len(templates) == 16,
    "all_templates_used": {row["template_id"] for row in templates} == {row["template_id"] for row in units},
    "258_units": len(units) == 258,
    "116_prose": sum(row["register"] == "PROSE" for row in units) == 116,
    "142_astro": sum(row["register"] == "ASTRO" for row in units) == 142,
    "776_groups": sum(int(row["group_count"]) for row in units) == 776,
    "unit_ids_unique": len({row["unit_id"] for row in units}) == 258,
    "fourteen_sections": len(sections) == 14,
    "section_units": sum(int(row["unit_count"]) for row in sections) == 258,
    "section_groups": sum(int(row["group_count"]) for row in sections) == 776,
    "complete_rows": all(all(row[field] for field in row) for row in units),
    "report": (HERE / "TWENTY_FOURTH_EDITION_REPORT.md").exists(),
    "readable": (HERE / "TWENTY_FOURTH_PLAUSIBLE_SOURCE_PHRASES.md").exists(),
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
