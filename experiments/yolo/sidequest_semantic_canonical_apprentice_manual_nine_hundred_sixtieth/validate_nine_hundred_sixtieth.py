#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    entries = read_tsv("PASS960_122_ENTRY_MASTER_TABLE.tsv")
    variants = read_tsv("PASS960_126_VARIANT_RECOGNITION_DRILL.tsv")
    lessons = read_tsv("PASS960_10_LESSON_PLAN.tsv")
    types = Counter(row["entry_type"] for row in entries)
    checks = {
        "entries_122": len(entries) == 122,
        "entry_ids_unique": len({row["entry_id"] for row in entries}) == 122,
        "roots_56": types["PRODUCTIVE_ROOT"] == 56,
        "formulas_66": types["LEARNED_FORMULA"] == 66,
        "variants_126": len(variants) == 126,
        "all_66_formula_ids": len({row["formula_card_id"] for row in variants}) == 66,
        "one_primary_per_formula": all(sum(row["is_primary_training_form"] == "YES" for row in variants if row["formula_card_id"] == formula_id) == 1 for formula_id in {row["formula_card_id"] for row in variants}),
        "lessons_10": len(lessons) == 10,
        "all_entries_assigned_once": sum(int(row["entries"]) for row in lessons) == 122,
        "all_short_values_present": all(row["spoken_value_de"] for row in entries),
        "no_sealed_pages": not any("f84" in str(row).lower() for row in entries + variants + lessons),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "PASS960_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
