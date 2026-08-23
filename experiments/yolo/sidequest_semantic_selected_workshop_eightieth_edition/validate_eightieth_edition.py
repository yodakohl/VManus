#!/usr/bin/env python3
"""Validate the consolidated selected workshop edition."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    dictionary = read_tsv("EIGHTIETH_43_MINIMAL_CARD_DICTIONARY.tsv")
    lexicon = read_tsv("EIGHTIETH_54_SELECTED_SOURCE_LEXICON.tsv")
    licenses = read_tsv("EIGHTIETH_43_CARD_SOURCE_LICENSES.tsv")
    units = read_tsv("EIGHTIETH_14_CONTROLLED_UNIT_EDITION.tsv")
    binding = read_tsv("EIGHTIETH_776_CURRENT_BINDING.tsv")
    profiles = read_tsv("EIGHTIETH_4_SCRIBE_PROFILES.tsv")
    manual = read_tsv("EIGHTIETH_12_STEP_WORKSHOP_MANUAL.tsv")
    checks = {
        "dictionary_43": len(dictionary) == 43 and len({row["entry_id"] for row in dictionary}) == 43,
        "source_lexicon_54": len(lexicon) == 54 and len({row["source_slot"] for row in lexicon}) == 54,
        "licenses_match_dictionary": len(licenses) == 43 and {row["entry_id"] for row in licenses} == {row["entry_id"] for row in dictionary},
        "units_14": len(units) == 14 and len({row["unit_id"] for row in units}) == 14,
        "pages_10": len({row["page"] for row in units}) == 10,
        "bindings_776": len(binding) == 776 and len({row["unified_serial"] for row in binding}) == 776,
        "unit_group_sum_776": sum(int(row["group_count"]) for row in units) == 776,
        "four_profiles": len(profiles) == 4,
        "manual_12": len(manual) == 12,
        "no_direct_rich_noun_license": all(row["direct_rich_noun_license"] == "NO" for row in licenses),
        "no_free_unit_noun": all(row["free_content_nouns_added"] == "NONE" for row in units),
        "sealed_pages_absent": all(not row["page"].lower().startswith("f84") for row in units + binding),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
