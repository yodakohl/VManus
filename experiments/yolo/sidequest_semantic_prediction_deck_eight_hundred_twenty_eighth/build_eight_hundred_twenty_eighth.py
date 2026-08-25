#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_seventh_workshop_grammar_eight_hundred_twenty_seventh"
PREDICTIONS = BASE / "EIGHT_HUNDRED_TWENTY_SEVENTH_76_UNATTESTED_PREDICTIONS.tsv"

HIGH = [
    ("CFH+DY", "close the observed pressing operation"),
    ("CFH+E+Y", "nearest short open pressing cell"),
    ("CFH+E+DY", "nearest short closed pressing cell"),
    ("CHK+E+DY", "missing short closed warming cell"),
    ("OK+EEE+Y", "missing open counterpart to full activation"),
    ("SH+EEE+Y", "full open hold counterpart"),
    ("SH+EEE+DY", "full closed hold counterpart"),
    ("EE+T+Y", "fills middle work grade between short and full"),
    ("LSH+E+Y", "short open rinse counterpart"),
    ("LSH+EE+DY", "long closed rinse counterpart"),
    ("SOLK+E+DY", "short closed collect counterpart"),
    ("OT+EEE+DY", "full next-step close counterpart"),
    ("CHD+AIIN", "transfer to prescribed measure"),
    ("K+AIIN", "add to prescribed measure"),
    ("L+AIN", "guide one working portion"),
    ("CH+O+AIN", "take a process portion"),
    ("CTH+AIN", "prepare one portion"),
    ("OR+AIIN", "batch with prescribed measure"),
    ("SOLK+AIN", "collect one portion"),
    ("OL+K+AIIN", "continue adding to prescribed measure"),
    ("CHD+AR", "transfer from source"),
    ("L+AL", "guide to target"),
    ("L+AIR", "guide water"),
    ("K+HO+AL", "add ingredient at target"),
]
HIGH_RANK = {recipe: i + 1 for i, (recipe, _) in enumerate(HIGH)}
HIGH_REASON = dict(HIGH)


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def parked_reason(recipe: str) -> tuple[str, str]:
    tokens = recipe.split("+")
    if "EEE" in tokens:
        return "PARKED_GRADE_LEAP", "full-grade extrapolation without enough neighboring cells"
    if "AR" in tokens or "AL" in tokens:
        return "PARKED_ADDRESS_STACK", "address order is harder to read than selected directional recipes"
    if tokens.count("E") + tokens.count("EE") + tokens.count("EEE") > 0:
        return "PARKED_REDUNDANT_GRID", "useful grid completion but lower value than selected nearest gaps"
    return "PARKED_LOW_VALUE", "formally composable but not needed in compact teaching deck"


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    predictions = read(PREDICTIONS)
    by_recipe: dict[str, list[dict[str, str]]] = defaultdict(list)
    all_rows = []
    for row in predictions:
        recipe = row["component_recipe"]
        if recipe in HIGH_RANK:
            status = "HIGH_VALUE_DECK"
            reason = HIGH_REASON[recipe]
            rank = HIGH_RANK[recipe]
        else:
            status, reason = parked_reason(recipe)
            rank = 0
        item = dict(row)
        item.update({"selection_status": status, "recipe_rank": rank or "NONE", "selection_reason": reason})
        all_rows.append(item)
        by_recipe[recipe].append(item)

    recipe_rows = []
    for recipe, rows in sorted(by_recipe.items(), key=lambda pair: (HIGH_RANK.get(pair[0], 999), pair[0])):
        first = rows[0]
        recipe_rows.append(
            {
                "component_recipe": recipe,
                "reading_de": first["reading_de"],
                "surface_candidates": "|".join(sorted(row["predicted_surface"] for row in rows)),
                "surface_candidates_n": len(rows),
                "selection_status": first["selection_status"],
                "recipe_rank": first["recipe_rank"],
                "selection_reason": first["selection_reason"],
                "source_passes": ",".join(sorted({source for row in rows for source in row["sources"].split(",")})),
            }
        )
    high_recipes = [row for row in recipe_rows if row["selection_status"] == "HIGH_VALUE_DECK"]
    high_surfaces = [row for row in all_rows if row["selection_status"] == "HIGH_VALUE_DECK"]

    write("EIGHT_HUNDRED_TWENTY_EIGHTH_76_PREDICTION_AUDIT.tsv", all_rows, ["predicted_surface", "component_recipe", "reading_de", "sources", "attested_on_fixed_pages", "use_status", "edition", "selection_status", "recipe_rank", "selection_reason"])
    write("EIGHT_HUNDRED_TWENTY_EIGHTH_68_RECIPE_DECISIONS.tsv", recipe_rows, ["component_recipe", "reading_de", "surface_candidates", "surface_candidates_n", "selection_status", "recipe_rank", "selection_reason", "source_passes"])
    write("EIGHT_HUNDRED_TWENTY_EIGHTH_24_HIGH_VALUE_RECIPES.tsv", high_recipes, ["component_recipe", "reading_de", "surface_candidates", "surface_candidates_n", "selection_status", "recipe_rank", "selection_reason", "source_passes"])
    write("EIGHT_HUNDRED_TWENTY_EIGHTH_30_HIGH_VALUE_SURFACES.tsv", high_surfaces, ["predicted_surface", "component_recipe", "reading_de", "sources", "attested_on_fixed_pages", "use_status", "edition", "selection_status", "recipe_rank", "selection_reason"])
    status_counts = {status: sum(row["selection_status"] == status for row in recipe_rows) for status in sorted({row["selection_status"] for row in recipe_rows})}
    summary = {
        "status": "PASS",
        "decision": "SEVENTY_SIX_SURFACE_PREDICTIONS_REDUCED_TO_TWENTY_FOUR_HIGH_VALUE_RECIPES",
        "input_surfaces": len(predictions),
        "input_recipes": len(recipe_rows),
        "high_value_recipes": len(high_recipes),
        "high_value_surfaces": len(high_surfaces),
        "parked_recipes": len(recipe_rows) - len(high_recipes),
        "parked_surfaces": len(predictions) - len(high_surfaces),
        "status_counts": status_counts,
        "dictionary_revisions": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / "EIGHT_HUNDRED_TWENTY_EIGHTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
