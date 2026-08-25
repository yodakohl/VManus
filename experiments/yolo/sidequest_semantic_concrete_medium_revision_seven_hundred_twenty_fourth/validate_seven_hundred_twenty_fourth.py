#!/usr/bin/env python3
"""Validate Pass 724 second semantic wave and AIR readings."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    components = read("SEVEN_HUNDRED_TWENTY_FOURTH_39_COMPONENTS.tsv")
    recipes = read("SEVEN_HUNDRED_TWENTY_FOURTH_163_RECIPES.tsv")
    cards = read("SEVEN_HUNDRED_TWENTY_FOURTH_173_CARDS.tsv")
    events = read("SEVEN_HUNDRED_TWENTY_FOURTH_381_EVENTS.tsv")
    statements = read("SEVEN_HUNDRED_TWENTY_FOURTH_116_STATEMENTS.tsv")
    records = read("SEVEN_HUNDRED_TWENTY_FOURTH_11_RECORDS.tsv")
    air = read("SEVEN_HUNDRED_TWENTY_FOURTH_5_AIR_WATER_READINGS.tsv")
    values = {row["component"]: row["pass724_value_de"] for row in components}
    checks = {
        "counts_39_163_173_381_116_11_5": (len(components), len(recipes), len(cards), len(events), len(statements), len(records), len(air)) == (39, 163, 173, 381, 116, 11, 5),
        "second_values": values["S"] == "TEIL" and values["CTH"] == "BEREITEN" and values["O"] == "ARBEITSGANG" and values["AIR"] == "WASSER",
        "first_values_preserved": values["T"] == "ANWENDEN" and values["CH"] == "ENTNEHMEN" and values["K"] == "ZUGEBEN",
        "recipe_composition": all(row["pass724_reading_de"] == " · ".join(values[part] for part in row["component_recipe"].split("+")) for row in recipes),
        "card_composition": all(row["pass724_reading_de"] == " · ".join(values[part] for part in row["component_recipe"].split("+")) for row in cards),
        "second_counts_29_37_28_9": sum(row["second_wave_revision"] == "YES" for row in recipes) == 29 and sum(row["second_wave_revision"] == "YES" for row in events) == 37 and sum(row["second_wave_revision"] == "YES" for row in statements) == 28 and sum(int(row["second_wave_statements"]) > 0 for row in records) == 9,
        "total_revised_recipes_59": sum(row["total_revision_from_pass721"] == "YES" for row in recipes) == 59,
        "air_five_recipes": {row["component_recipe"] for row in air} == {"CH+AIR", "K+AIR", "OK+AIR", "CHD+AIR", "AIR+Y+DY"},
        "air_all_coherent": all(row["coherent_as_water"] == "YES" and "WASSER" in row["atomic_reading_de"] for row in air),
        "form_invariant": all(row["surface_unchanged"] == row["owner_unchanged"] == row["boundary_unchanged"] == "YES" for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_TWENTY_FOURTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
