#!/usr/bin/env python3
"""Validate the eighty-eighth function-class repair."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    repairs = rows("EIGHTY_EIGHTH_8_MASTER_WORD_REPAIRS.tsv")
    words = rows("EIGHTY_EIGHTH_REVISED_44_SOURCE_WORDS.tsv")
    candidates = rows("EIGHTY_EIGHTH_CARD_NEIGHBOR_CANDIDATES.tsv")
    units = rows("EIGHTY_EIGHTH_14_REPAIRED_CODEX_UNITS.tsv")
    binding = rows("EIGHTY_EIGHTH_776_REPAIRED_BINDING.tsv")
    old_words = {row["old_exact_guess_de"] for row in repairs}
    herbal_text = " ".join(row["concrete_reading_de"] for row in units if row["unit_id"].startswith("H"))
    checks = {
        "repairs_8": len(repairs) == 8,
        "revised_words_44": len(words) == 44,
        "candidate_rows_64": len(candidates) == 64,
        "eight_candidates_each": all(sum(row["codex_word_id"] == word["codex_word_id"] for row in candidates) == 8 for word in repairs),
        "units_14": len(units) == 14,
        "groups_776": len(binding) == 776,
        "serial_complete": [int(row["unified_serial"]) for row in binding] == list(range(1, 777)),
        "exact_old_words_removed_from_primary_herbal": not any(word in herbal_text for word in old_words),
        "all_repairs_function_class": all(row["working_status"] == "REVISED_TO_PREDICTABLE_FUNCTION_CLASS" for row in words if row["codex_word_id"] in {r["codex_word_id"] for r in repairs}),
        "no_candidate_promoted": all(row["decision"] == "NO_EXACT_NOUN_PROMOTION__ASSOCIATION_ONLY" for row in candidates),
        "fixed_pages_only": set(row["page"] for row in binding) == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"},
        "sealed_absent": all("f84" not in "\t".join(row.values()).lower() for row in words + units + binding),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
