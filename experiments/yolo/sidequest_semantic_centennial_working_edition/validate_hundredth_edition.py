#!/usr/bin/env python3
"""Validate the centennial creative working edition."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    dictionary = rows("HUNDREDTH_CORRECTED_173_CARD_DICTIONARY.tsv")
    prose = rows("HUNDREDTH_381_PROSE_INTERLINEAR.tsv")
    statements = rows("HUNDREDTH_116_STATEMENT_TRANSLATION.tsv")
    astro = rows("HUNDREDTH_395_ASTRO_GROUPS.tsv")
    total = rows("HUNDREDTH_776_TOTAL_LEDGER.tsv")
    words = rows("HUNDREDTH_44_SOURCE_WORDS.tsv")
    manual = rows("HUNDREDTH_14_RULE_APPRENTICE_MANUAL.tsv")
    questions = rows("HUNDREDTH_12_OPEN_WORKING_QUESTIONS.tsv")
    checks = {
        "dictionary_173": len(dictionary) == 173,
        "dictionary_ids_unique": len({row["master_card_id"] for row in dictionary}) == 173,
        "dictionary_defaults_complete": all(row["short_default_de"] and row["imperative_de"] for row in dictionary),
        "prose_381": len(prose) == 381,
        "prose_serials_complete": [int(row["event_serial"]) for row in prose] == list(range(1, 382)),
        "statements_116": len(statements) == 116,
        "statement_event_sum_381": sum(int(row["event_count"]) for row in statements) == 381,
        "astro_395": len(astro) == 395,
        "astro_defaults_complete": all(row["default_local_meaning_de"] for row in astro),
        "unified_776": len(total) == 776,
        "unified_serials_complete": [int(row["unified_serial"]) for row in total] == list(range(1, 777)),
        "source_words_44": len(words) == 44,
        "manual_14": len(manual) == 14,
        "questions_12": len(questions) == 12,
        "no_blank_total_meanings": all(row["default_meaning_de"] and row["continuous_reading_de"] for row in total),
        "taiin_is_aiin": any(row["visible_surface"] == "taiin" and row["semantic_atoms"] == "AIIN" for row in prose),
        "ckhe_not_ckh_grade": all("CKH+E+CLOSE" != row["semantic_atoms"] for row in prose if row["visible_surface"] in {"lcheckhedy", "shckhedy"}),
        "fixed_pages_only": set(row["page"] for row in total) == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"},
        "sealed_absent": all("f84" not in "\t".join(row.values()).lower() for row in total),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
