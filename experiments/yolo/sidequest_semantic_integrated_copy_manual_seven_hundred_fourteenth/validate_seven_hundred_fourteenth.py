#!/usr/bin/env python3
"""Validate Pass 714 integrated copy manual."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    families = read("SEVEN_HUNDRED_FOURTEENTH_163_FAMILY_MANUAL.tsv")
    events = read("SEVEN_HUNDRED_FOURTEENTH_381_INTEGRATED_COPY_TRACE.tsv")
    exceptions = read("SEVEN_HUNDRED_FOURTEENTH_10_DISTINCT_EXCEPTION_SLIPS.tsv")
    inventory = read("SEVEN_HUNDRED_FOURTEENTH_6_LAYER_INVENTORY.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_FOURTEENTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    layers = Counter(row["exact_card_selection_layer"] for row in events)
    checks = {
        "families_163": len(families) == 163,
        "events_381_unique": len(events) == 381 and len({row["event_id"] for row in events}) == 381,
        "family_cover_exact": {row["semantic_family"] for row in events} == {row["semantic_family"] for row in families},
        "exact_cards_173": len({row["observed_exact_card"] for row in events}) == 173,
        "layers_310_36_30_5": layers == {"UNIQUE_EXACT_CARD": 310, "OWNER_RECORD_SUBFAMILY": 36, "LOCUS_BOUNDARY_PRIOR": 30, "BOUNDARY_CARD_OVERRIDE": 5},
        "card_defaults_376": sum(row["card_default_correct"] == "YES" for row in events) == 376,
        "surface_defaults_376": sum(row["surface_default_correct"] == "YES" for row in events) == 376,
        "initial_chain_371": sum(row["card_default_correct"] == "YES" and row["surface_default_correct"] == "YES" for row in events) == 371,
        "exceptions_10_unique": len(exceptions) == 10 and len({row["event_id"] for row in exceptions}) == 10,
        "exceptions_5_plus_5": Counter(row["exception_kind"] for row in exceptions) == {"CARD_SUBFAMILY_OVERRIDE": 5, "SURFACE_OVERRIDE": 5},
        "no_overlap": all("+" not in row["exception_kind"] for row in exceptions),
        "six_inventory_layers": len(inventory) == 6,
        "all_final_values_present": all(row["semantic_reading_de"] and row["observed_exact_card"] and row["observed_surface"] for row in events),
        "summary_pass": summary["status"] == "PASS" and summary["final_exact_reconstructions"] == 381,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_FOURTEENTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
