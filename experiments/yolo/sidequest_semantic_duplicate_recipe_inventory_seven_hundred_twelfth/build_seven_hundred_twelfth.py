#!/usr/bin/env python3
"""Build Pass 712: reduce 173 exact cards to semantic recipe families."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P700 = ROOT / "experiments/yolo/sidequest_semantic_apprentice_manual_seven_hundredth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


VARIANT_KIND = {
    "CHD+DY": "E_JOINT_VS_COMPACT",
    "CHD+Y": "ITEM_CARRIER_EXTENSION",
    "CHK+EE+Y": "CORE_SPELLING_ALLOGRAPH",
    "OK+CHD+DY": "E_JOINT_VS_COMPACT",
    "OK+OL": "ENTRY_AND_CARRIER_ALLOGRAPH",
    "OK+Y": "ITEM_CARRIER_EXTENSION",
    "OL": "LOCAL_WHOLE_ALLOGRAPH",
    "OT+CHD+DY": "E_JOINT_VS_COMPACT",
    "OT+Y": "ITEM_CARRIER_EXTENSION",
    "SH+EE+Y": "E_STRETCH_ALLOGRAPH",
}


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    cards = read(P700 / "SEVEN_HUNDREDTH_173_CARD_MANUAL.tsv")
    events = read(P700 / "SEVEN_HUNDREDTH_381_FORWARD_TRACE.tsv")
    cards_by_recipe: dict[str, list[dict[str, str]]] = defaultdict(list)
    events_by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    for card in cards:
        cards_by_recipe[card["component_recipe"]].append(card)
    for event in events:
        events_by_card[event["card_no"]].append(event)

    recipe_order = sorted(cards_by_recipe, key=lambda recipe: min(int(card["card_no"].removeprefix("PROC")) for card in cards_by_recipe[recipe]))
    family_id_by_recipe = {recipe: f"SEM{index:03d}" for index, recipe in enumerate(recipe_order, 1)}
    family_rows = []
    map_rows = []
    duplicate_rows = []
    occurrence_rows = []
    copy_rule_rows = []
    for recipe in recipe_order:
        members = sorted(cards_by_recipe[recipe], key=lambda row: row["card_no"])
        member_ids = [row["card_no"] for row in members]
        readings = {row["compact_atomic_reading_de"] for row in members}
        member_events = [event for card_id in member_ids for event in events_by_card[card_id]]
        owner_cards: dict[str, set[str]] = defaultdict(set)
        for event in member_events:
            owner_cards[event["owner_de"]].add(event["card_no"])
        same_owner_multi = [owner for owner, card_ids in owner_cards.items() if len(card_ids) > 1]
        if len(members) == 1:
            merge_status = "SINGLE_EXACT_CARD"
        elif same_owner_multi:
            merge_status = "PROVISIONAL_SEMANTIC_MERGE__EXEMPLAR_CHOICE_REQUIRED"
        else:
            merge_status = "SEMANTIC_MERGE__OWNER_RECORD_SUBFAMILIES"
        family_rows.append({
            "semantic_family": family_id_by_recipe[recipe], "component_recipe": recipe,
            "working_reading_de": " | ".join(sorted(readings)),
            "exact_card_subfamilies": len(members), "exact_card_ids": "|".join(member_ids),
            "surface_inventory": " || ".join(row["surfaces"] for row in members),
            "events": sum(int(row["events"]) for row in members),
            "pages": "|".join(sorted({event["page"] for event in member_events})),
            "records": "|".join(sorted({event["record"] for event in member_events})),
            "merge_status": merge_status,
            "same_owner_uses_multiple_subfamilies": "YES" if same_owner_multi else "NO",
            "same_owner_examples": " | ".join(same_owner_multi) if same_owner_multi else "NONE",
        })
        for member in members:
            map_rows.append({
                "exact_card_id": member["card_no"], "semantic_family": family_id_by_recipe[recipe],
                "component_recipe": recipe, "working_reading_de": member["compact_atomic_reading_de"],
                "surfaces": member["surfaces"], "events": member["events"],
                "copy_subfamily_preserved": "YES",
            })
        if len(members) <= 1:
            continue
        event_counts = {card_id: len(events_by_card[card_id]) for card_id in member_ids}
        duplicate_rows.append({
            "semantic_family": family_id_by_recipe[recipe], "component_recipe": recipe,
            "working_reading_de": " | ".join(sorted(readings)),
            "exact_card_ids": "|".join(member_ids),
            "event_counts_by_card": "|".join(f"{card_id}:{event_counts[card_id]}" for card_id in member_ids),
            "surfaces_by_card": " || ".join(f"{row['card_no']}:{row['surfaces']}" for row in members),
            "variant_kind": VARIANT_KIND[recipe], "merge_status": merge_status,
            "same_owner_uses_both": "YES" if same_owner_multi else "NO",
            "same_owner_examples": " | ".join(same_owner_multi) if same_owner_multi else "NONE",
            "semantic_split_selected": "NO",
        })
        copy_rule_rows.append({
            "semantic_family": family_id_by_recipe[recipe], "component_recipe": recipe,
            "semantic_rule_de": f"Ein Rezept {recipe}; keine Bedeutungsaufspaltung.",
            "copy_choice_de": "Exakte Unterkarte aus Besitzer-/Locus-Schublade oder Meisterexemplar waehlen.",
            "owner_alone_sufficient": "NO" if same_owner_multi else "YES_IN_FIXED_SCOPE",
            "unseen_owner_rule": "MASTER_EXEMPLAR_REQUIRED",
        })
        for event in sorted(member_events, key=lambda row: int(row["event_id"].removeprefix("E"))):
            occurrence_rows.append({
                "event_id": event["event_id"], "page": event["page"], "record": event["record"],
                "statement_id": event["statement_id"], "locus": event["locus"], "owner_de": event["owner_de"],
                "semantic_family": family_id_by_recipe[recipe], "component_recipe": recipe,
                "exact_card_id": event["card_no"], "surface": event["observed_surface"],
                "renderer_rules": event["renderer_rules"], "surface_selection_layer": event["surface_selection_layer"],
            })

    write("SEVEN_HUNDRED_TWELFTH_163_SEMANTIC_CARD_FAMILIES.tsv", family_rows)
    write("SEVEN_HUNDRED_TWELFTH_173_EXACT_TO_SEMANTIC_MAP.tsv", map_rows)
    write("SEVEN_HUNDRED_TWELFTH_10_DUPLICATE_RECIPE_FAMILIES.tsv", duplicate_rows)
    write("SEVEN_HUNDRED_TWELFTH_71_DUPLICATE_OCCURRENCES.tsv", occurrence_rows)
    write("SEVEN_HUNDRED_TWELFTH_10_COPY_SUBFAMILY_RULES.tsv", copy_rule_rows)

    summary = {
        "status": "PASS", "exact_cards": len(cards), "semantic_families": len(family_rows),
        "composed_semantic_families": sum(all(card["card_class"] != "MEMORIZED_WHOLE_COMMAND" for card in cards_by_recipe[row["component_recipe"]]) for row in family_rows),
        "whole_command_families": sum(any(card["card_class"] == "MEMORIZED_WHOLE_COMMAND" for card in cards_by_recipe[row["component_recipe"]]) for row in family_rows),
        "singleton_families": sum(int(row["exact_card_subfamilies"]) == 1 for row in family_rows),
        "duplicate_recipe_families": len(duplicate_rows),
        "duplicate_exact_cards": sum(len(row["exact_card_ids"].split("|")) for row in duplicate_rows),
        "duplicate_occurrences": len(occurrence_rows),
        "safe_owner_record_merges": sum(row["merge_status"] == "SEMANTIC_MERGE__OWNER_RECORD_SUBFAMILIES" for row in duplicate_rows),
        "provisional_same_owner_merges": sum(row["merge_status"] == "PROVISIONAL_SEMANTIC_MERGE__EXEMPLAR_CHOICE_REQUIRED" for row in duplicate_rows),
        "semantic_splits": sum(row["semantic_split_selected"] == "YES" for row in duplicate_rows),
        "decision": "ONE_HUNDRED_SIXTY_THREE_SEMANTIC_RECIPE_FAMILIES_WITH_ONE_HUNDRED_SEVENTY_THREE_EXACT_COPY_CARDS",
    }
    (HERE / "SEVEN_HUNDRED_TWELFTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
