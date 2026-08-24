#!/usr/bin/env python3
"""Derive the shared root core and specialist trays across all eleven records."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P679 = ROOT / "experiments/yolo/sidequest_semantic_historical_layer_dictionary_six_hundred_seventy_ninth"
RECORD_ORDER = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def tier(records: int) -> str:
    if records == 11:
        return "UNIVERSAL_11"
    if records >= 8:
        return "COMMON_8_TO_10"
    if records >= 5:
        return "EXTENDED_5_TO_7"
    return "SPECIALIST_1_TO_4"


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = read(P679 / "SIX_HUNDRED_SEVENTY_NINTH_381_COMPACT_EVENT_INTERLINEAR.tsv")
    roots = {row["component"]: row for row in read(P679 / "SIX_HUNDRED_SEVENTY_NINTH_39_LAYER_DICTIONARY.tsv")}
    by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_record[event["record"]].append(event)
    record_roots = {record: {component for event in by_record[record] for component in event["component_recipe"].split("+")} for record in RECORD_ORDER}
    record_recipes = {record: {event["component_recipe"] for event in by_record[record]} for record in RECORD_ORDER}
    root_record_count = Counter(component for components in record_roots.values() for component in components)

    root_rows = []
    for component in sorted(roots):
        records = [record for record in RECORD_ORDER if component in record_roots[record]]
        matching_events = [event for event in events if component in event["component_recipe"].split("+")]
        root_rows.append({
            "component": component,
            "compact_value_de": roots[component]["compact_table_value_de"],
            "historical_layer": roots[component]["historical_layer"],
            "records_used": len(records),
            "records": "|".join(records),
            "events_with_component": len(matching_events),
            "shared_tier": tier(len(records)),
            "teaching_location": "POCKET_CORE" if len(records) >= 8 else "COMMON_DESK_TRAY" if len(records) >= 5 else "RECORD_SPECIALIST_TRAY",
        })

    tray_rows = []
    for record in RECORD_ORDER:
        components = record_roots[record]
        tray_rows.append({
            "record": record,
            "page": by_record[record][0]["page"],
            "events": len(by_record[record]),
            "exact_recipes": len(record_recipes[record]),
            "total_roots": len(components),
            "universal_roots": " ".join(sorted(component for component in components if root_record_count[component] == 11)),
            "pocket_core_roots": " ".join(sorted(component for component in components if root_record_count[component] >= 8)),
            "extended_roots": " ".join(sorted(component for component in components if 5 <= root_record_count[component] <= 7)) or "NONE",
            "specialist_roots": " ".join(sorted(component for component in components if root_record_count[component] <= 4)) or "NONE",
            "record_unique_roots": " ".join(sorted(component for component in components if root_record_count[component] == 1)) or "NONE",
        })

    by_recipe: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_recipe[event["component_recipe"]].append(event)
    recipe_rows = []
    for recipe in sorted(by_recipe):
        rows = by_recipe[recipe]
        records = [record for record in RECORD_ORDER if recipe in record_recipes[record]]
        recipe_rows.append({
            "component_recipe": recipe,
            "compact_reading_de": rows[0]["compact_atomic_reading_de"],
            "events": len(rows),
            "records_used": len(records),
            "records": "|".join(records),
            "recipe_tier": tier(len(records)),
        })

    unique_rows = []
    for row in root_rows:
        if int(row["records_used"]) == 1:
            unique_rows.append({
                "record": row["records"],
                "component": row["component"],
                "compact_value_de": row["compact_value_de"],
                "events_with_component": row["events_with_component"],
                "workshop_role_de": "lokale Spezialkarte; allgemeine Grammatik bleibt unveraendert",
            })

    tier_rows = []
    for order, name in enumerate(["UNIVERSAL_11", "COMMON_8_TO_10", "EXTENDED_5_TO_7", "SPECIALIST_1_TO_4"], start=1):
        members = [row for row in root_rows if row["shared_tier"] == name]
        tier_rows.append({
            "tier_order": order,
            "tier": name,
            "root_count": len(members),
            "components": " ".join(str(row["component"]) for row in members),
            "values_de": " | ".join(str(row["compact_value_de"]) for row in members),
            "apprentice_storage": members[0]["teaching_location"],
        })

    write("SIX_HUNDRED_EIGHTY_EIGHTH_39_ROOT_ECOLOGY.tsv", root_rows)
    write("SIX_HUNDRED_EIGHTY_EIGHTH_11_RECORD_SPECIALIST_TRAYS.tsv", tray_rows)
    write("SIX_HUNDRED_EIGHTY_EIGHTH_163_RECIPE_ECOLOGY.tsv", recipe_rows)
    write("SIX_HUNDRED_EIGHTY_EIGHTH_9_UNIQUE_ROOTS.tsv", unique_rows)
    write("SIX_HUNDRED_EIGHTY_EIGHTH_4_SHARED_TIERS.tsv", tier_rows)

    root_tiers = Counter(row["shared_tier"] for row in root_rows)
    recipe_record_counts = Counter(int(row["records_used"]) for row in recipe_rows)
    summary = {
        "status": "PASS",
        "records": len(RECORD_ORDER),
        "events": len(events),
        "roots": len(root_rows),
        "root_tiers": dict(root_tiers),
        "universal_roots": [row["component"] for row in root_rows if row["shared_tier"] == "UNIVERSAL_11"],
        "pocket_core_roots_at_least_8_records": sum(int(row["records_used"]) >= 8 for row in root_rows),
        "record_unique_roots": len(unique_rows),
        "recipes": len(recipe_rows),
        "universal_exact_recipes": sum(int(row["records_used"]) == 11 for row in recipe_rows),
        "recipe_record_count_distribution": dict(sorted(recipe_record_counts.items())),
    }
    (HERE / "SIX_HUNDRED_EIGHTY_EIGHTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
