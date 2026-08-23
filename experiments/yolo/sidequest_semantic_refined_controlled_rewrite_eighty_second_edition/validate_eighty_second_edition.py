#!/usr/bin/env python3
"""Validate propagation of the refined source words."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    units = read_tsv("EIGHTY_SECOND_14_REFINED_CONTROLLED_UNITS.tsv")
    comparisons = read_tsv("EIGHTY_SECOND_14_BEFORE_AFTER_READINGS.tsv")
    bindings = read_tsv("EIGHTY_SECOND_776_REFINED_BINDING.tsv")
    old_terms = {"Auszugsmedium", "Endprodukt", "Himmelslabel", "Witterungswert", "Lichtwert", "Zeitwert", "Qualitätswert", "Filtern"}
    combined = " ".join(row["selected_source_words_de"] + " " + row["controlled_unit_reading_de"] for row in units)
    checks = {
        "fourteen_units": len(units) == 14 and len({row["unit_id"] for row in units}) == 14,
        "thirteen_changed": sum(row["source_revision_status"] == "REVISED" for row in units) == 13,
        "one_unchanged": sum(row["source_revision_status"] == "UNCHANGED" for row in units) == 1,
        "comparisons_14": len(comparisons) == 14,
        "bindings_776": len(bindings) == 776 and len({row["unified_serial"] for row in bindings}) == 776,
        "all_bindings_refined": all(row["controlled_rewrite_status"] == "REFINED_SELECTED_SOURCE" for row in bindings),
        "old_terms_removed": not any(term in combined for term in old_terms),
        "group_sum_776": sum(int(row["group_count"]) for row in units) == 776,
        "sealed_pages_absent": all(not row["page"].lower().startswith("f84") for row in units + bindings),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
