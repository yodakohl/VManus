#!/usr/bin/env python3
"""Lay out the 173-card master as a practical recipe-indexed copybook."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P672 = ROOT / "experiments/yolo/sidequest_semantic_integrated_dictionary_six_hundred_seventy_second"
P679 = ROOT / "experiments/yolo/sidequest_semantic_historical_layer_dictionary_six_hundred_seventy_ninth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    compact = {row["card_no"]: row for row in read(P679 / "SIX_HUNDRED_SEVENTY_NINTH_173_COMPACT_CARD_TABLET.tsv")}
    original = read(P672 / "SIX_HUNDRED_SEVENTY_SECOND_173_CARD_DICTIONARY.tsv")
    roots = {row["component"]: row for row in read(P679 / "SIX_HUNDRED_SEVENTY_NINTH_39_LAYER_DICTIONARY.tsv")}

    by_recipe: dict[str, list[dict[str, str]]] = defaultdict(list)
    for card in original:
        by_recipe[card["component_recipe"]].append(card)

    recipe_rows: list[dict[str, object]] = []
    for address_no, recipe in enumerate(sorted(by_recipe, key=lambda value: (value.split("+")[0], len(value.split("+")), value)), start=1):
        cards = by_recipe[recipe]
        compact_card = compact[cards[0]["card_no"]]
        recipe_rows.append({
            "recipe_address": f"A{address_no:03d}",
            "first_tab": recipe.split("+")[0],
            "recipe_length": len(recipe.split("+")),
            "component_recipe": recipe,
            "compact_reading_de": compact_card["compact_atomic_reading_de"],
            "historical_layers": compact_card["historical_layers"],
            "exact_card_variants": len(cards),
            "card_nos": "|".join(card["card_no"] for card in cards),
            "surfaces_to_copy": "; ".join(card["surfaces"] for card in cards),
            "surface_exemplars": sum(len(card["surfaces"].split("|")) for card in cards),
            "page_record_selector": "; ".join(f"{card['pages']}::{card['records']}" for card in cards),
            "lookup_result": "DIRECT_CARD" if len(cards) == 1 else "CHOOSE_LOCAL_CARD_VARIANT",
            "total_events": sum(int(card["events"]) for card in cards),
        })

    by_tab: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in recipe_rows:
        by_tab[str(row["first_tab"])].append(row)
    tab_rows = []
    running = 1
    for tab_no, component in enumerate(sorted(by_tab), start=1):
        rows = by_tab[component]
        root = roots[component]
        tab_rows.append({
            "tab_no": f"T{tab_no:02d}",
            "first_component": component,
            "spoken_value_de": root["compact_table_value_de"],
            "historical_layer": root["historical_layer"],
            "recipe_rows": len(rows),
            "exact_cards": sum(int(row["exact_card_variants"]) for row in rows),
            "surface_exemplars": sum(int(row["surface_exemplars"]) for row in rows),
            "address_start": f"A{running:03d}",
            "address_end": f"A{running + len(rows) - 1:03d}",
        })
        running += len(rows)

    variant_rows = []
    for row in recipe_rows:
        if int(row["exact_card_variants"]) > 1:
            cards = by_recipe[str(row["component_recipe"])]
            for variant_no, card in enumerate(cards, start=1):
                variant_rows.append({
                    "recipe_address": row["recipe_address"],
                    "component_recipe": row["component_recipe"],
                    "variant_no": variant_no,
                    "card_no": card["card_no"],
                    "surfaces": card["surfaces"],
                    "pages": card["pages"],
                    "records": card["records"],
                    "events": card["events"],
                    "selection_rule": "match page record and local entry exemplar; never choose by invented meaning",
                })

    sheet_rows = [
        {"sheet": 1, "title": "EIGHT_TRAYS", "content": "eight historical layers and39 spoken entries", "learner_action": "memorize the short value and whether it is free bound deictic or whole"},
        {"sheet": 2, "title": "THIRTY_FOUR_TABS", "content": "first-component index with at most20 recipe rows behind one tab", "learner_action": "open the tab named by the first component of the intended recipe"},
        {"sheet": 3, "title": "ONE_HUNDRED_SIXTY_THREE_RECIPES", "content": "one ordered address per observed component recipe", "learner_action": "match the full component sequence longest and exactly"},
        {"sheet": 4, "title": "TEN_DOUBLE_ROWS", "content": "ten recipes with two distinct exact-card variants", "learner_action": "choose by page record and local exemplar not by new semantics"},
        {"sheet": 5, "title": "TWO_HUNDRED_THIRTY_SURFACE_EXEMPLARS", "content": "all visible spellings grouped beneath their exact card", "learner_action": "copy the shown positional form; do not spell freely"},
        {"sheet": 6, "title": "THREE_WHOLE_COMMANDS", "content": "FACH WIEDERAUFNEHMEN VERWAHREN", "learner_action": "learn as indivisible nomenclator entries"},
    ]

    write("SIX_HUNDRED_EIGHTY_FIRST_163_RECIPE_COPYBOOK.tsv", recipe_rows)
    write("SIX_HUNDRED_EIGHTY_FIRST_34_FIRST_COMPONENT_TABS.tsv", tab_rows)
    write("SIX_HUNDRED_EIGHTY_FIRST_20_DOUBLE_RECIPE_VARIANTS.tsv", variant_rows)
    write("SIX_HUNDRED_EIGHTY_FIRST_6_COPYBOOK_SHEETS.tsv", sheet_rows)

    summary = {
        "status": "PASS",
        "semantic_entries": len(roots),
        "exact_cards": len(original),
        "unique_recipe_addresses": len(recipe_rows),
        "direct_recipe_addresses": sum(row["lookup_result"] == "DIRECT_CARD" for row in recipe_rows),
        "double_recipe_addresses": sum(row["lookup_result"] == "CHOOSE_LOCAL_CARD_VARIANT" for row in recipe_rows),
        "double_recipe_card_variants": len(variant_rows),
        "surface_exemplars": sum(len(card["surfaces"].split("|")) for card in original),
        "first_component_tabs": len(tab_rows),
        "largest_tab_rows": max(int(row["recipe_rows"]) for row in tab_rows),
        "recipe_length_distribution": dict(sorted(Counter(len(recipe.split("+")) for recipe in by_recipe).items())),
        "whole_commands_to_memorize": sum(card["composition_mode"] == "MEMORIZED_WHOLE_COMMAND" for card in original),
    }
    (HERE / "SIX_HUNDRED_EIGHTY_FIRST_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
