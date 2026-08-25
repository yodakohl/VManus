#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    lexicon = read("PASS976_137_TEACHING_UNIT_LEXICON.tsv")
    cards = read("PASS976_68_EXACT_SPECIALIST_CARDS.tsv")
    lessons = read("PASS976_EIGHT_LESSON_CURRICULUM.tsv")
    checks = {
        "teaching_units_137": len(lexicon) == 137,
        "teaching_ids_unique": len({r["teaching_unit_id"] for r in lexicon}) == 137,
        "specialist_cards_68": len(cards) == 68,
        "lessons_8": len(lessons) == 8,
        "new_specialist_units_51": sum(r["layer"] == "E_LOCAL_SPECIALIST_HEADWORD" for r in lexicon) == 51,
        "common_formula_local_units_86": sum(r["layer"] != "E_LOCAL_SPECIALIST_HEADWORD" for r in lexicon) == 86,
        "all_values_present": all(r["spoken_value_de"] and r["concrete_context_values_de"] for r in lexicon),
        "no_unknown_placeholder": all("UNKNOWN" not in r["spoken_value_de"].upper() for r in lexicon),
        "sealed_absent": all("f84" not in r["pages"].lower() for r in lexicon + cards),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "PASS976_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
