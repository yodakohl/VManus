#!/usr/bin/env python3
"""Compare compact recipe and root transfer between H3 and B1 commissions."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P679 = ROOT / "experiments/yolo/sidequest_semantic_historical_layer_dictionary_six_hundred_seventy_ninth"
P686 = ROOT / "experiments/yolo/sidequest_semantic_first_scribe_commission_six_hundred_eighty_sixth"


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
    logs = read(P686 / "SIX_HUNDRED_EIGHTY_SIXTH_83_COMMISSION_LOOKUP_LOG.tsv")
    roots = {row["component"]: row for row in read(P679 / "SIX_HUNDRED_SEVENTY_NINTH_39_LAYER_DICTIONARY.tsv")}
    by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in logs:
        by_record[row["record"]].append(row)

    recipe_sets = {record: {row["component_recipe"] for row in rows} for record, rows in by_record.items()}
    root_sets = {record: {component for row in rows for component in row["component_recipe"].split("+")} for record, rows in by_record.items()}
    shared_recipes = recipe_sets["H3"] & recipe_sets["B1"]
    shared_roots = root_sets["H3"] & root_sets["B1"]

    root_rows = []
    for component in sorted(root_sets["H3"] | root_sets["B1"]):
        h3 = [row for row in by_record["H3"] if component in row["component_recipe"].split("+")]
        b1 = [row for row in by_record["B1"] if component in row["component_recipe"].split("+")]
        root_rows.append({
            "component": component,
            "compact_value_de": roots[component]["compact_table_value_de"],
            "historical_layer": roots[component]["historical_layer"],
            "H3_events_with_root": len(h3),
            "B1_events_with_root": len(b1),
            "transfer_class": "SHARED_ROOT" if h3 and b1 else "H3_LOCAL_ROOT" if h3 else "B1_LOCAL_ROOT",
            "H3_recipes": "|".join(sorted({row["component_recipe"] for row in h3})) or "NONE",
            "B1_recipes": "|".join(sorted({row["component_recipe"] for row in b1})) or "NONE",
            "owner_expansion_de": f"H3: Wert innerhalb der Kronenpflanze; B1: Wert innerhalb des zweireihigen Beckens" if h3 and b1 else "nur im lokalen Auftrag belegt",
        })

    recipe_rows = []
    for recipe in sorted(shared_recipes):
        h3 = [row for row in by_record["H3"] if row["component_recipe"] == recipe]
        b1 = [row for row in by_record["B1"] if row["component_recipe"] == recipe]
        recipe_rows.append({
            "component_recipe": recipe,
            "compact_reading_de": h3[0]["master_dictation_de"],
            "H3_events": len(h3),
            "H3_surfaces": "|".join(sorted({row["copied_surface"] for row in h3})),
            "H3_owner": h3[0]["owner_noun_de"],
            "B1_events": len(b1),
            "B1_surfaces": "|".join(sorted({row["copied_surface"] for row in b1})),
            "B1_owner": b1[0]["owner_noun_de"],
            "transfer_reading_de": "MASS bleibt Mass; konkrete Messgroesse folgt dem Owner" if recipe == "AIIN" else "DIES bleibt deiktisch; der referierte Posten wechselt mit dem Owner",
        })

    event_rows = []
    for row in logs:
        tokens = set(row["component_recipe"].split("+"))
        if row["component_recipe"] in shared_recipes:
            transfer_class = "EXACT_RECIPE_TRANSFER"
        elif tokens & shared_roots:
            transfer_class = "SHARED_ROOT_RECOMBINATION"
        else:
            transfer_class = "OWNER_LOCAL_ROOT_RECIPE"
        event_rows.append({
            "event_id": row["event_id"],
            "record": row["record"],
            "page": row["page"],
            "owner_noun_de": row["owner_noun_de"],
            "component_recipe": row["component_recipe"],
            "compact_reading_de": row["master_dictation_de"],
            "shared_components": "+".join(component for component in row["component_recipe"].split("+") if component in shared_roots) or "NONE",
            "transfer_class": transfer_class,
            "copied_surface": row["copied_surface"],
        })

    layer_rows = [
        {"rank": 1, "transfer_unit": "ROOT_VALUE", "H3_inventory": len(root_sets["H3"]), "B1_inventory": len(root_sets["B1"]), "shared": len(shared_roots), "interpretation": "primary portable workshop vocabulary"},
        {"rank": 2, "transfer_unit": "EXACT_RECIPE", "H3_inventory": len(recipe_sets["H3"]), "B1_inventory": len(recipe_sets["B1"]), "shared": len(shared_recipes), "interpretation": "mostly owner-local recombination"},
        {"rank": 3, "transfer_unit": "EXACT_CARD", "H3_inventory": len({row["selected_card_no"] for row in by_record["H3"]}), "B1_inventory": len({row["selected_card_no"] for row in by_record["B1"]}), "shared": len({row["selected_card_no"] for row in by_record["H3"]} & {row["selected_card_no"] for row in by_record["B1"]}), "interpretation": "same as shared recipes in these commissions"},
        {"rank": 4, "transfer_unit": "VISIBLE_SURFACE", "H3_inventory": len({row["copied_surface"] for row in by_record["H3"]}), "B1_inventory": len({row["copied_surface"] for row in by_record["B1"]}), "shared": len({row["copied_surface"] for row in by_record["H3"]} & {row["copied_surface"] for row in by_record["B1"]}), "interpretation": "least portable layer; local copy form"},
    ]

    write("SIX_HUNDRED_EIGHTY_SEVENTH_31_ROOT_TRANSFER.tsv", root_rows)
    write("SIX_HUNDRED_EIGHTY_SEVENTH_2_EXACT_RECIPE_TRANSFERS.tsv", recipe_rows)
    write("SIX_HUNDRED_EIGHTY_SEVENTH_83_EVENT_TRANSFER_CLASSES.tsv", event_rows)
    write("SIX_HUNDRED_EIGHTY_SEVENTH_4_TRANSFER_LEVELS.tsv", layer_rows)

    counts = Counter(row["transfer_class"] for row in event_rows)
    summary = {
        "status": "PASS",
        "H3_roots": len(root_sets["H3"]),
        "B1_roots": len(root_sets["B1"]),
        "shared_roots": len(shared_roots),
        "H3_recipes": len(recipe_sets["H3"]),
        "B1_recipes": len(recipe_sets["B1"]),
        "shared_exact_recipes": len(shared_recipes),
        "event_transfer_classes": dict(counts),
        "events_with_any_shared_root": sum(bool(set(row["component_recipe"].split("+")) & shared_roots) for row in logs),
        "decision": "ROOTS_TRANSFER__FULL_RECIPES_MOSTLY_OWNER_LOCAL__SURFACES_LOCAL",
    }
    (HERE / "SIX_HUNDRED_EIGHTY_SEVENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
