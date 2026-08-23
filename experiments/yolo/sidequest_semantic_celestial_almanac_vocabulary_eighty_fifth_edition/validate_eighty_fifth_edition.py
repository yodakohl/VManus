#!/usr/bin/env python3
"""Validate the concrete three-instrument celestial almanac."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    vocab = read_tsv("EIGHTY_FIFTH_36_MODEL_VOCABULARY_ROWS.tsv")
    comparisons = read_tsv("EIGHTY_FIFTH_9_MODEL_INSTRUMENT_COMPARISONS.tsv")
    words = read_tsv("EIGHTY_FIFTH_16_SELECTED_ALMANAC_WORDS.tsv")
    instruments = read_tsv("EIGHTY_FIFTH_3_COMPLETE_ALMANAC_INSTRUMENTS.tsv")
    loci = read_tsv("EIGHTY_FIFTH_142_LOCAL_ALMANAC_LOCI.tsv")
    groups = read_tsv("EIGHTY_FIFTH_395_ALMANAC_GROUP_BINDING.tsv")
    analogues = read_tsv("EIGHTY_FIFTH_5_HISTORICAL_ALMANAC_ANALOGUES.tsv")
    checks = {
        "three_models_twelve_words": len(vocab) == 36 and len({row["model_id"] for row in vocab}) == 3,
        "nine_comparisons": len(comparisons) == 9,
        "sixteen_selected_words": len(words) == 16 and len({row["almanac_slot"] for row in words}) == 16,
        "three_instruments": len(instruments) == 3 and {row["unit_id"] for row in instruments} == {"A1", "A2", "A3"},
        "instrument_counts": sum(int(row["locus_count"]) for row in instruments) == 142 and sum(int(row["group_count"]) for row in instruments) == 395,
        "142_loci": len(loci) == 142 and sum(int(row["group_count"]) for row in loci) == 395,
        "395_groups": len(groups) == 395 and len({row["group_serial"] for row in groups}) == 395,
        "local_only": all(row["orientation"] == "NONE" and row["crosspage_key"] == "NONE" for row in instruments + loci + groups),
        "no_portable_astro_word": all(row["portable_word_value"] == "NONE__LOCAL_NOMENCLATOR_ONLY" for row in groups),
        "five_analogues": len(analogues) == 5,
        "sealed_pages_absent": all(not row["page"].lower().startswith("f84") for row in instruments + loci + groups),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
