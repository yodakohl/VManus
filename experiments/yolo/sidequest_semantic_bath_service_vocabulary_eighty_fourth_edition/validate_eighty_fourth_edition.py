#!/usr/bin/env python3
"""Validate the concrete bath-and-service edition."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    vocab = read_tsv("EIGHTY_FOURTH_33_MODEL_VOCABULARY_ROWS.tsv")
    comparisons = read_tsv("EIGHTY_FOURTH_18_MODEL_RECORD_COMPARISONS.tsv")
    words = read_tsv("EIGHTY_FOURTH_17_SELECTED_BATH_SERVICE_WORDS.tsv")
    records = read_tsv("EIGHTY_FOURTH_6_COMPLETE_BATH_SERVICE_RECORDS.tsv")
    bindings = read_tsv("EIGHTY_FOURTH_281_BATH_SERVICE_BINDING.tsv")
    analogues = read_tsv("EIGHTY_FOURTH_5_HISTORICAL_BATH_ANALOGUES.tsv")
    checks = {
        "three_models_eleven_words": len(vocab) == 33 and len({row["model_id"] for row in vocab}) == 3,
        "eighteen_comparisons": len(comparisons) == 18,
        "seventeen_selected_words": len(words) == 17 and len({row["bath_service_slot"] for row in words}) == 17,
        "six_records": len(records) == 6 and {row["unit_id"] for row in records} == {"B1", "B2", "B3", "B4", "B5", "B6"},
        "record_group_sum_281": sum(int(row["group_count"]) for row in records) == 281,
        "281_bindings": len(bindings) == 281 and len({row["source_group_identity"] for row in bindings}) == 281,
        "four_bath_two_service": sum(row["content_mode"] == "FIGURE_OWNED_BATH" for row in records) == 4 and sum(row["content_mode"] == "FIGURELESS_SERVICE_STATION" for row in records) == 2,
        "no_disease_or_global_network": all(row["disease_or_anatomical_system"] == "UNSPECIFIED" and row["global_water_network"] == "NONE" for row in records),
        "five_analogues": len(analogues) == 5,
        "sealed_pages_absent": all(not row["page"].lower().startswith("f84") for row in records + bindings),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
