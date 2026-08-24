#!/usr/bin/env python3
"""Validate Pass 709 terse docket encoder."""

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
    dockets = read("SEVEN_HUNDRED_NINTH_12_DOCKET_ENCODINGS.tsv")
    layers = read("SEVEN_HUNDRED_NINTH_5_INFORMATION_LAYERS.tsv")
    owners = Counter(row["owner_slot"] for row in dockets)
    checks = {
        "dockets_12": len(dockets) == 12,
        "docket_ids_unique": len({row["docket_id"] for row in dockets}) == 12,
        "owners_plant_basin_apparatus": owners == {"PLANT": 6, "BASIN": 4, "APPARATUS": 2},
        "owners_silent_12": all(row["owner_supplied_by_image"] == "YES" for row in dockets),
        "all_templates_attested_or_single": all(row["role_template_support"] == "SINGLE_CARD" or int(row["role_template_support"]) >= 1 for row in dockets),
        "all_have_cards": all(bool(row["selected_card_sequence"]) for row in dockets),
        "all_have_surfaces": all(bool(row["selected_surface_sequence"]) for row in dockets),
        "all_have_backreading": all(bool(row["fluent_owner_filled_reading_de"]) for row in dockets),
        "no_new_cards": all(row["new_card"] == "NO" for row in dockets),
        "no_new_surfaces": all(row["new_surface"] == "NO" for row in dockets),
        "information_layers_5": len(layers) == 5,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_NINTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
