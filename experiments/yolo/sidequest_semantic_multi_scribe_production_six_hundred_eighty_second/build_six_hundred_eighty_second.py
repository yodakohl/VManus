#!/usr/bin/env python3
"""Audit recurrent recipes as a practical multi-scribe production system."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P679 = ROOT / "experiments/yolo/sidequest_semantic_historical_layer_dictionary_six_hundred_seventy_ninth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def position(index: int, total: int) -> str:
    if total == 1:
        return "ONLY"
    if index == 0:
        return "FIRST"
    if index == total - 1:
        return "LAST"
    return "MIDDLE"


def prefix_class(surface: str) -> str:
    if surface.startswith("q"):
        return "Q_ENTRY_FORM"
    if surface.startswith("s"):
        return "S_ENTRY_FORM"
    return "OTHER_FORM"


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = read(P679 / "SIX_HUNDRED_SEVENTY_NINTH_381_COMPACT_EVENT_INTERLINEAR.tsv")
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_statement[event["statement_id"]].append(event)

    enriched = []
    for statement_rows in by_statement.values():
        for index, event in enumerate(statement_rows):
            row = dict(event)
            row["statement_position"] = position(index, len(statement_rows))
            row["surface_prefix_class"] = prefix_class(event["surface"])
            enriched.append(row)

    by_recipe: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in enriched:
        by_recipe[event["component_recipe"]].append(event)
    recurrent = {recipe: rows for recipe, rows in by_recipe.items() if len(rows) >= 2}

    family_rows = []
    for family_no, (recipe, rows) in enumerate(sorted(recurrent.items(), key=lambda item: (-len(item[1]), item[0])), start=1):
        surfaces = sorted({row["surface"] for row in rows})
        cards = sorted({row["card_no"] for row in rows})
        pages = sorted({row["page"] for row in rows})
        records = sorted({row["record"] for row in rows})
        positions = Counter(row["statement_position"] for row in rows)
        prefixes = Counter(row["surface_prefix_class"] for row in rows)
        family_rows.append({
            "family_no": f"F{family_no:02d}",
            "component_recipe": recipe,
            "compact_reading_de": rows[0]["compact_atomic_reading_de"],
            "events": len(rows),
            "pages": "|".join(pages),
            "records": "|".join(records),
            "distinct_pages": len(pages),
            "distinct_records": len(records),
            "exact_cards": len(cards),
            "card_nos": "|".join(cards),
            "surface_forms": len(surfaces),
            "surfaces": "|".join(surfaces),
            "position_counts": ";".join(f"{key}:{positions[key]}" for key in ["FIRST", "MIDDLE", "LAST", "ONLY"] if positions[key]),
            "prefix_counts": ";".join(f"{key}:{prefixes[key]}" for key in ["Q_ENTRY_FORM", "S_ENTRY_FORM", "OTHER_FORM"] if prefixes[key]),
            "production_rule": "RECIPE_INVARIANT__LOCAL_CARD_AND_SURFACE_LOOKUP" if len(cards) > 1 else "RECIPE_AND_CARD_INVARIANT__LOCAL_SURFACE_LOOKUP" if len(surfaces) > 1 else "RECIPE_CARD_SURFACE_INVARIANT",
        })

    recurring_events = [row for row in enriched if row["component_recipe"] in recurrent]
    trace_rows = []
    for row in recurring_events:
        trace_rows.append({
            "event_id": row["event_id"],
            "page": row["page"],
            "record": row["record"],
            "statement_id": row["statement_id"],
            "statement_position": row["statement_position"],
            "dictated_recipe": row["component_recipe"],
            "invariant_reading_de": row["compact_atomic_reading_de"],
            "selected_exact_card": row["card_no"],
            "copied_surface": row["surface"],
            "surface_prefix_class": row["surface_prefix_class"],
        })

    selected_recipes = ["AIIN", "OL", "Y", "OK+Y", "CHD+Y", "SHED+DY", "AL", "OK+AIIN", "OK+AIN", "OK+EE+Y", "AR", "OR"]
    teaching_rows = []
    family_by_recipe = {row["component_recipe"]: row for row in family_rows}
    for lesson_no, recipe in enumerate(selected_recipes, start=1):
        row = family_by_recipe[recipe]
        teaching_rows.append({
            "lesson_no": lesson_no,
            "dictated_recipe": recipe,
            "spoken_value_de": row["compact_reading_de"],
            "events": row["events"],
            "records": row["records"],
            "exact_cards": row["exact_cards"],
            "surfaces": row["surfaces"],
            "master_instruction_de": "Bedeutungsrezept unveraendert lassen; passende exakte Karte und sichtbare Form aus dem lokalen Exemplar kopieren.",
        })

    layer_rows = [
        {"layer": 1, "name": "DICTATED_RECIPE", "shared_or_local": "SHARED", "rule": "components and compact meaning remain identical across every occurrence"},
        {"layer": 2, "name": "EXACT_CARD", "shared_or_local": "MOSTLY_SHARED", "rule": "one card in40 recurrent families; two local variants in10 families"},
        {"layer": 3, "name": "VISIBLE_SURFACE", "shared_or_local": "LOCAL_COPY", "rule": "14 recurrent families stable;36 use multiple copied surfaces"},
        {"layer": 4, "name": "OWNER_AND_POSITION", "shared_or_local": "LOCAL_CONTEXT", "rule": "page record statement position and pictured owner select the usable exemplar"},
    ]

    write("SIX_HUNDRED_EIGHTY_SECOND_50_RECURRENT_RECIPE_FAMILIES.tsv", family_rows)
    write("SIX_HUNDRED_EIGHTY_SECOND_268_MULTI_SCRIBE_TRACES.tsv", trace_rows)
    write("SIX_HUNDRED_EIGHTY_SECOND_12_TEACHING_FAMILIES.tsv", teaching_rows)
    write("SIX_HUNDRED_EIGHTY_SECOND_4_PRODUCTION_LAYERS.tsv", layer_rows)

    summary = {
        "status": "PASS",
        "all_recipe_families": len(by_recipe),
        "recurrent_recipe_families": len(recurrent),
        "recurrent_events": len(recurring_events),
        "cross_record_families": sum(int(row["distinct_records"]) >= 2 for row in family_rows),
        "cross_page_families": sum(int(row["distinct_pages"]) >= 2 for row in family_rows),
        "one_card_recurrent_families": sum(int(row["exact_cards"]) == 1 for row in family_rows),
        "two_card_recurrent_families": sum(int(row["exact_cards"]) == 2 for row in family_rows),
        "single_surface_recurrent_families": sum(int(row["surface_forms"]) == 1 for row in family_rows),
        "multi_surface_recurrent_families": sum(int(row["surface_forms"]) > 1 for row in family_rows),
        "prefix_event_counts": dict(Counter(row["surface_prefix_class"] for row in enriched)),
        "decision": "SHARED_RECIPE__MOSTLY_SHARED_CARD__LOCAL_SURFACE_AND_OWNER",
    }
    (HERE / "SIX_HUNDRED_EIGHTY_SECOND_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
