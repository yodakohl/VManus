#!/usr/bin/env python3
"""Validate the seven-layer teaching dictionary."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    entries = rows("FIFTY_FOURTH_89_HIERARCHICAL_ENTRIES.tsv")
    layers = rows("FIFTY_FOURTH_7_LAYER_RULES.tsv")
    examples = rows("FIFTY_FOURTH_12_BOUNDARY_EXAMPLES.tsv")
    counts = Counter(row["hierarchy_level"] for row in entries)
    expected = Counter({
        "L1_ATOMIC_ROOT": 28,
        "L2_LEARNED_NOMENCLATOR": 15,
        "L2B_SIMULATED_MASTER_SUPPLEMENT": 4,
        "L3_SILENT_MEMORY_REGISTER": 4,
        "L4_PROCESS_MACRO": 20,
        "L5_VISIBLE_OWNER": 5,
        "L6_ASTRO_LOCAL_MODULE": 13,
    })
    checks = {
        "exactly_89_entries": len(entries) == 89,
        "layer_counts_exact": counts == expected,
        "seven_layer_rules": len(layers) == 7 and {row["layer"] for row in layers} == set(expected),
        "twelve_examples": len(examples) == 12,
        "unique_entry_ids_within_layer": len({(row["hierarchy_level"], row["entry_id"]) for row in entries}) == 89,
        "roots_are_card_level": all(row["written_as_manuscript_card"] == "YES_INSIDE_REGISTERED_CARDS" for row in entries if row["hierarchy_level"] == "L1_ATOMIC_ROOT"),
        "memory_is_not_card": all(row["written_as_manuscript_card"] == "NO" for row in entries if row["hierarchy_level"] == "L3_SILENT_MEMORY_REGISTER"),
        "macros_are_not_card": all(row["written_as_manuscript_card"] == "NO_PATTERN_OVER_SEVERAL_CARDS" for row in entries if row["hierarchy_level"] == "L4_PROCESS_MACRO"),
        "master_categories_not_surfaces": all(row["written_as_manuscript_card"] == "NO_NEUTRAL_CATALOG_LABEL_ONLY" for row in entries if row["hierarchy_level"] == "L2B_SIMULATED_MASTER_SUPPLEMENT"),
        "no_empty_values": all(row["short_value_de"].strip() for row in entries),
        "fixed_pages_sealed": all("f84" not in "\t".join(row.values()).lower() for row in entries),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {"status": status, "checks": checks, "layer_counts": dict(counts)}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit(1)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
