#!/usr/bin/env python3
from pathlib import Path
import csv
import json

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


deck = read("TWENTY_THIRD_COMPONENT_DECK.tsv")
lessons = read("TWENTY_THIRD_FOURTEEN_LESSONS.tsv")
examples = read("TWENTY_THIRD_NINE_ROUNDTRIP_EXAMPLES.tsv")
checks = {
    "deck_56": len(deck) == 56,
    "deck_unique": len({row["symbol"] for row in deck}) == 56,
    "deck_concrete": all(row["atomic_value_de"] and row["owner_expansion_de"] for row in deck),
    "fourteen_lessons": len(lessons) == 14,
    "lesson_order": [int(row["lesson"]) for row in lessons] == list(range(1, 15)),
    "nine_examples": len(examples) == 9,
    "six_prose": sum(row["register"] == "PROSE" for row in examples) == 6,
    "three_astro": sum(row["register"] == "ASTRO" for row in examples) == 3,
    "examples_complete": all(all(row[field] for field in row) for row in examples),
    "roundtrip_same": all(row["roundtrip"] == "SAME_REGISTERED_UNIT" for row in examples),
    "manual": (HERE / "TWENTY_THIRD_MASTER_APPRENTICE_MANUAL.md").exists(),
    "report": (HERE / "TWENTY_THIRD_EDITION_REPORT.md").exists(),
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
