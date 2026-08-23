#!/usr/bin/env python3
"""Validate selected values for all divergent source slots."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    decisions = read_tsv("SEVENTY_FIFTH_26_DIVERGENT_SLOT_DECISIONS.tsv")
    lexicon = read_tsv("SEVENTY_FIFTH_54_SELECTED_SOURCE_LEXICON.tsv")
    programs = read_tsv("SEVENTY_FIFTH_14_SELECTED_SOURCE_PROGRAMS.tsv")
    binding = read_tsv("SEVENTY_FIFTH_776_SELECTED_SOURCE_BINDING.tsv")
    checks = {
        "twenty_six_decisions": len(decisions) == 26 and len({row["source_slot"] for row in decisions}) == 26,
        "fifty_four_selected_words": len(lexicon) == 54 and len({row["source_slot"] for row in lexicon}) == 54,
        "all_selected_values_nonempty": all(row["selected_source_value_de"] for row in lexicon),
        "all_divergent_slots_decided": {row["source_slot"] for row in decisions} == {row["source_slot"] for row in lexicon if row["medical_or_iatromedical_expansion_de"] != row["nonmedical_expansion_de"]},
        "fourteen_programs": len(programs) == 14 and len({row["unit_id"] for row in programs}) == 14,
        "no_unrestricted_nouns": all(row["unrestricted_nouns"] == "NONE" for row in programs),
        "776_bindings": len(binding) == 776 and len({row["unified_serial"] for row in binding}) == 776,
        "all_bindings_selected": all(row["content_selection_status"] == "FINITE_SELECTED_LEXICON" for row in binding),
        "unit_group_counts": sum(int(row["group_count"]) for row in programs) == 776,
        "sealed_pages_absent": all("f84" not in "\t".join(row.values()).lower() for row in decisions + lexicon + programs + binding),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
