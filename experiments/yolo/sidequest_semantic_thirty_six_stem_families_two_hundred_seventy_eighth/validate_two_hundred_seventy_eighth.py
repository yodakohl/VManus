#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    mapping = read("TWO_HUNDRED_SEVENTY_EIGHTH_40_TO_36_MAPPING.tsv")
    families = read("TWO_HUNDRED_SEVENTY_EIGHTH_36_STEM_FAMILIES.tsv")
    corrections = read("TWO_HUNDRED_SEVENTY_EIGHTH_FIVE_PORTABLE_CORRECTIONS.tsv")
    inventory = read("TWO_HUNDRED_SEVENTY_EIGHTH_REVISED_APPRENTICE_INVENTORY.tsv")
    expected = {"HERBAL_BIO_ASTRO_CORE": 16, "HERBAL_ASTRO_BRIDGE": 3, "BIO_ASTRO_BRIDGE": 1, "HERBAL_BIO_PROSE_CORE": 2, "HERBAL_SPECIALIST": 7, "BIO_SPECIALIST": 7}
    values = {r["family_id"]: r["short_value_de"] for r in families}
    checks = {
        "40_mapping_rows": len(mapping) == 40,
        "36_families": len(families) == 36,
        "orders_1_36": [int(r["family_order"]) for r in families] == list(range(1, 37)),
        "all_old_once": len({r["old_component_id"] for r in mapping}) == 40,
        "three_merges": {r["new_family_id"] for r in mapping if r["old_component_id"] != r["new_family_id"]} == {"E_GRADE", "CHED_TRANSFER", "CHO_INPUT"},
        "reach_counts": Counter(r["reach_class"] for r in families) == expected,
        "common_16": sum(r["teaching_layer"] == "COMMON_SIXTEEN" for r in families) == 16,
        "portable_corrections": values["DY"] == "FESTSETZEN" and values["CHK"] == "ZUSTAND_JUSTIEREN" and values["CHO_INPUT"] == "EINGABE",
        "five_correction_rows": len(corrections) == 5,
        "memorized_105": next(r for r in inventory if r["layer"] == "TOTAL_MEMORIZED")["memorized_entries"] == "105",
        "all_values_nonempty": all(r["short_value_de"].strip() for r in families),
        "all_supported": all(int(r["herbal_events"]) + int(r["bio_events"]) + int(r["astro_groups"]) > 0 for r in families),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    (OUT / "VALIDATION.json").write_text(json.dumps({"status": status, "checks": checks}, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
