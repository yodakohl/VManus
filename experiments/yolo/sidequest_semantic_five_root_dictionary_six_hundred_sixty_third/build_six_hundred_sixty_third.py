#!/usr/bin/env python3
"""Consolidate five productive roots and inventory the remaining card layer."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P637 = ROOT / "experiments/yolo/sidequest_semantic_complete_surface_curriculum_six_hundred_thirty_seventh"


ROOT_VALUES = {
    "OK": "ANSETZEN",
    "CHD": "UMSETZEN",
    "SHED": "ABSETZEN",
    "CHK": "WAERMEN",
    "CTH": "BEREIT",
}

NEXT_CONTENT = {
    "OR": "ANSATZ_ODER_ZUBEREITUNG",
    "CKH": "DURCHLASS_ODER_KANAL",
    "SOLK": "AUFFANG_ODER_SAMMELSTELLE",
    "LSH": "WASCHEN_ODER_SPUELEN",
    "CFH": "AUSWRINGEN_ODER_ABPRESSEN",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def proc_num(card: str) -> int:
    return int(card.removeprefix("PROC"))


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = read_tsv(P637 / "SIX_HUNDRED_THIRTY_SEVENTH_381_COMPLETE_APPRENTICE_LEDGER.tsv")
    by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_card[event["card_no"]].append(event)
        by_statement[event["statement_id"]].append(event)

    def roots(row: dict[str, str]) -> list[str]:
        atoms = row["semantic_component_parse"].split("+")
        return [root for root in ROOT_VALUES if root in atoms]

    covered_events = [row for row in events if roots(row)]
    covered_ids = {row["card_no"] for row in covered_events}
    dictionary_rows = []
    for card in sorted(covered_ids, key=proc_num):
        rows = by_card[card]
        exemplar = rows[0]
        rs = roots(exemplar)
        dictionary_rows.append({
            "card_no": card,
            "surfaces": "|".join(sorted({row["surface"] for row in rows})),
            "component_recipe": exemplar["semantic_component_parse"],
            "productive_roots": "|".join(rs),
            "root_values_de": "|".join(ROOT_VALUES[root] for root in rs),
            "composed_reading_de": exemplar["standard_command_de"],
            "events": len(rows),
            "pages": "|".join(sorted({row["page"] for row in rows})),
            "contains_close": "YES" if "SCHLUSS" in exemplar["standard_command_de"] else "NO",
        })

    event_rows = []
    for event in covered_events:
        final = by_statement[event["statement_id"]][-1]["event_id"] == event["event_id"]
        event_rows.append({
            "event_id": event["event_id"],
            "page": event["page"],
            "record": event["record"],
            "statement_id": event["statement_id"],
            "card_no": event["card_no"],
            "surface": event["surface"],
            "component_recipe": event["semantic_component_parse"],
            "productive_roots": "|".join(roots(event)),
            "composed_reading_de": event["standard_command_de"],
            "contains_close": "YES" if "SCHLUSS" in event["standard_command_de"] else "NO",
            "statement_final": "YES" if final else "NO",
        })

    root_rows = []
    for root, value in ROOT_VALUES.items():
        cards = [row for row in dictionary_rows if root in str(row["productive_roots"]).split("|")]
        evs = [row for row in event_rows if root in str(row["productive_roots"]).split("|")]
        root_rows.append({
            "root": root,
            "short_value_de": value,
            "card_types": len(cards),
            "events": len(evs),
            "component_recipes": len({row["component_recipe"] for row in cards}),
            "pages": "|".join(sorted({page for row in cards for page in str(row["pages"]).split("|")})),
        })

    recipe_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in dictionary_rows:
        recipe_groups[str(row["component_recipe"])].append(row)
    recipe_rows = []
    for recipe in sorted(recipe_groups):
        cards = recipe_groups[recipe]
        recipe_rows.append({
            "component_recipe": recipe,
            "card_types": len(cards),
            "card_ids": "|".join(sorted((str(row["card_no"]) for row in cards), key=proc_num)),
            "events": sum(int(row["events"]) for row in cards),
            "productive_roots": cards[0]["productive_roots"],
            "composed_reading_de": cards[0]["composed_reading_de"],
        })

    remainder_ids = set(by_card) - covered_ids
    remainder_rows = []
    for card in sorted(remainder_ids, key=proc_num):
        rows = by_card[card]
        exemplar = rows[0]
        remainder_rows.append({
            "card_no": card,
            "surfaces": "|".join(sorted({row["surface"] for row in rows})),
            "component_recipe": exemplar["semantic_component_parse"],
            "current_reading_de": exemplar["standard_command_de"],
            "events": len(rows),
            "pages": "|".join(sorted({row["page"] for row in rows})),
            "next_layer_status": "NOT_YET_IN_FIVE_ROOT_DICTIONARY",
        })

    candidate_rows = []
    for atom, value in NEXT_CONTENT.items():
        cards = [row for row in remainder_rows if atom in str(row["component_recipe"]).split("+")]
        candidate_rows.append({
            "candidate_root": atom,
            "working_value_de": value,
            "remaining_card_types": len(cards),
            "remaining_events": sum(int(row["events"]) for row in cards),
            "card_ids": "|".join(str(row["card_no"]) for row in cards),
            "next_priority": "1" if atom == "OR" else "2" if atom == "CKH" else "3",
        })

    write_tsv(HERE / "SIX_HUNDRED_SIXTY_THIRD_57_FIVE_ROOT_CARDS.tsv", dictionary_rows, list(dictionary_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_SIXTY_THIRD_158_FIVE_ROOT_EVENTS.tsv", event_rows, list(event_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_SIXTY_THIRD_5_ROOT_ENTRIES.tsv", root_rows, list(root_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_SIXTY_THIRD_50_COMPONENT_RECIPES.tsv", recipe_rows, list(recipe_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_SIXTY_THIRD_116_REMAINING_CARDS.tsv", remainder_rows, list(remainder_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_SIXTY_THIRD_5_NEXT_CONTENT_ROOTS.tsv", candidate_rows, list(candidate_rows[0]))

    summary = {
        "status": "PASS",
        "productive_roots": len(root_rows),
        "covered_card_types": len(dictionary_rows),
        "covered_events": len(event_rows),
        "component_recipes": len(recipe_rows),
        "covered_statements": len({row["statement_id"] for row in event_rows}),
        "covered_records": len({row["record"] for row in event_rows}),
        "covered_pages": len({row["page"] for row in event_rows}),
        "closed_covered_events": sum(row["contains_close"] == "YES" for row in event_rows),
        "closed_covered_events_final": sum(row["contains_close"] == "YES" and row["statement_final"] == "YES" for row in event_rows),
        "remaining_card_types": len(remainder_rows),
        "remaining_events": sum(int(row["events"]) for row in remainder_rows),
        "next_content_root": "OR",
        "decision": "FIVE_ROOT_DICTIONARY_COMPOSES_FIFTY_SEVEN_CARDS_AND_ONE_HUNDRED_FIFTY_EIGHT_EVENTS",
    }
    (HERE / "SIX_HUNDRED_SIXTY_THIRD_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
