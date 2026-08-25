#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python3", str(OUT / "build_nine_hundred_fifty_third.py")], check=True)
    entries = rows("PASS953_135_ENTRY_APPRENTICE_CODEBOOK.tsv")
    variants = rows("PASS953_155_FORMULA_SURFACE_VARIANTS.tsv")
    lessons = rows("PASS953_10_LESSON_PLAN.tsv")
    tiers = Counter(row["entry_tier"] for row in entries)
    checks = [
        ("entries_135", len(entries) == 135, len(entries)),
        ("abbreviations_56", tiers["PRODUCTIVE_ABBREVIATION"] == 56, tiers),
        ("formulas_79", tiers["LEARNED_FORMULA_CARD"] == 79, tiers),
        ("variants_155", len(variants) == 155, len(variants)),
        ("lessons_10", len(lessons) == 10, len(lessons)),
        ("all_entries_once", len({row["apprentice_entry_id"] for row in entries}) == 135, "unique"),
        ("all_lessons_used", {int(row["lesson"]) for row in entries} == set(range(1, 11)), "1-10"),
        ("lesson_sum", sum(int(row["entries"]) for row in lessons) == 135, "sum"),
        ("all_values", all(row["workshop_value_de"].strip() and row["image_value_de"].strip() for row in entries), "values"),
        ("sealed_absent", "f84" not in "".join(str(row) for row in entries).lower(), "sealed"),
    ]
    result = {"status": "PASS" if all(ok for _, ok, _ in checks) else "FAIL", "checks": [{"name": name, "pass": ok, "detail": str(detail)} for name, ok, detail in checks]}
    (OUT / "PASS953_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
