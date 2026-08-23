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
    dictionary = read("HUNDRED_SEVENTY_FIFTH_173_CARD_DICTIONARY.tsv")
    prose = read("HUNDRED_SEVENTY_FIFTH_381_PROSE_MASTER_EDITION.tsv")
    astro = read("HUNDRED_SEVENTY_FIFTH_395_ASTRO_MASTER_EDITION.tsv")
    unified = read("HUNDRED_SEVENTY_FIFTH_776_UNIFIED_MASTER_LEDGER.tsv")
    units = read("HUNDRED_SEVENTY_FIFTH_14_UNIT_MASTER_SUMMARY.tsv")
    lessons = read("HUNDRED_SEVENTY_FIFTH_12_LESSON_CURRICULUM.tsv")
    pages = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}
    checks = {
        "dictionary_173": len(dictionary) == 173 and len({row["master_card_id"] for row in dictionary}) == 173,
        "prose_381": len(prose) == 381 and [int(row["event_serial"]) for row in prose] == list(range(1, 382)),
        "astro_395": len(astro) == 395 and len({row["source_group_id"] for row in astro}) == 395,
        "unified_776": len(unified) == 776 and [int(row["unified_order"]) for row in unified] == list(range(1, 777)),
        "ten_pages": {row["page"] for row in unified} == pages,
        "fourteen_units": len(units) == 14 and sum(int(row["group_count"]) for row in units) == 776,
        "twelve_lessons": len(lessons) == 12 and [int(row["lesson"]) for row in lessons] == list(range(1, 13)),
        "all_prose_concrete": all(row["complete_workshop_expansion_de"].strip() for row in prose),
        "all_astro_concrete": all(row["concrete_workshop_value_de"].strip() for row in astro),
        "all_unified_concrete": all(row["complete_workshop_expansion_de"].strip() for row in unified),
        "sections_exact": [sum(row["section"] == section for row in unified) for section in ["PROSE", "ASTRO"]] == [381, 395],
        "sealed_absent": all(not row["page"].startswith("f84") for row in unified),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
