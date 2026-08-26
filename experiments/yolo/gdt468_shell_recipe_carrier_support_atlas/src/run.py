#!/usr/bin/env python3
"""Join GDT467 shell recipes to old running and address carriers."""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt468_shell_recipe_carrier_support_atlas"
OUT = BASE / "artifacts"
PHRASEBOOK_PATH = ROOT / "experiments/yolo/gdt467_bounded_shell_composition_atlas/artifacts/gdt467_2760_shell_phrasebook.tsv"
RUNNING_PATH = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts/gdt407_4576_running_event_edition.tsv"
ADDRESS_PATH = ROOT / "experiments/yolo/gdt466_future_address_mixed_dictionary_intake/artifacts/gdt466_107_intake_dictionary.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty table: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def joined(values: set[str]) -> str:
    return "|".join(sorted(values)) or "NONE"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    shells = read_tsv(PHRASEBOOK_PATH)
    running = read_tsv(RUNNING_PATH)
    addresses = read_tsv(ADDRESS_PATH)
    recipes = sorted({row["flattened_recipe_trace"] for row in shells})
    if (len(shells), len(recipes), len(running), len(addresses)) != (2760, 2300, 4576, 107):
        raise RuntimeError("Unexpected source counts")
    recipe_set = set(recipes)

    shell_by_recipe: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in shells:
        shell_by_recipe[row["flattened_recipe_trace"]].append(row)

    running_by_recipe: dict[str, list[dict[str, str]]] = defaultdict(list)
    running_surface_recipe: dict[str, str] = {}
    for row in running:
        previous = running_surface_recipe.setdefault(row["surface"], row["component_recipe"])
        if previous != row["component_recipe"]:
            raise RuntimeError(f"Non-invariant running surface: {row['surface']}")
        if row["component_recipe"] in recipe_set:
            running_by_recipe[row["component_recipe"]].append(row)

    full_by_recipe: dict[str, list[dict[str, str]]] = defaultdict(list)
    hybrid_by_recipe: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in addresses:
        recipe = row["ordered_function_recipe_trace"]
        if recipe not in recipe_set:
            continue
        if row["gdt466_hybrid_status"] == "FULL_FUNCTION_FORMULA":
            full_by_recipe[recipe].append(row)
        elif int(row["known_function_character_count"]) > 0:
            hybrid_by_recipe[recipe].append(row)

    tier_order = {
        "RUNNING_EXACT_RECIPE": 0,
        "ADDRESS_FULL_FORMULA_ONLY": 1,
        "ADDRESS_HYBRID_SHELL_ONLY": 2,
        "COMPOSITION_ONLY": 3,
    }
    raw_rows: list[dict[str, object]] = []
    for ordinal, recipe in enumerate(recipes, start=1):
        recipe_shells = shell_by_recipe[recipe]
        run_rows = running_by_recipe.get(recipe, [])
        full_rows = full_by_recipe.get(recipe, [])
        hybrid_rows = hybrid_by_recipe.get(recipe, [])
        run_surfaces = {row["surface"] for row in run_rows}
        run_pages = {row["physical_page"] for row in run_rows}
        full_surfaces = {row["surface"] for row in full_rows}
        hybrid_surfaces = {row["surface"] for row in hybrid_rows}
        if run_rows:
            tier = "RUNNING_EXACT_RECIPE"
        elif full_rows:
            tier = "ADDRESS_FULL_FORMULA_ONLY"
        elif hybrid_rows:
            tier = "ADDRESS_HYBRID_SHELL_ONLY"
        else:
            tier = "COMPOSITION_ONLY"
        raw_rows.append({
            "recipe_id": f"G468-R{ordinal:04d}", "flattened_recipe_trace": recipe,
            "shell_factorization_count": len(recipe_shells),
            "shell_shapes": joined({row["shell_shape"] for row in recipe_shells}),
            "shell_ids": "|".join(row["shell_id"] for row in recipe_shells),
            "surface_templates": "|".join(row["surface_template"] for row in recipe_shells),
            "exact_channel_signatures": "|".join(row["exact_channel_signature"] for row in recipe_shells),
            "running_surface_type_count": len(run_surfaces), "running_event_count": len(run_rows),
            "running_page_count": len(run_pages), "running_surfaces": joined(run_surfaces),
            "running_pages": joined(run_pages), "running_registers": joined({row["register"] for row in run_rows}),
            "address_full_formula_count": len(full_rows), "address_full_formula_surfaces": joined(full_surfaces),
            "address_full_formula_pages": joined({row["physical_page"] for row in full_rows}),
            "address_hybrid_shell_count": len(hybrid_rows), "address_hybrid_shell_surfaces": joined(hybrid_surfaces),
            "address_hybrid_shell_pages": joined({row["physical_page"] for row in hybrid_rows}),
            "support_tier": tier,
            "old_carrier_surface_count": len(run_surfaces | full_surfaces | hybrid_surfaces),
        })

    ranked = sorted(
        raw_rows,
        key=lambda row: (
            tier_order[str(row["support_tier"])], -int(row["running_page_count"]), -int(row["running_event_count"]),
            -int(row["address_full_formula_count"]), -int(row["address_hybrid_shell_count"]),
            -int(row["shell_factorization_count"]), str(row["flattened_recipe_trace"]),
        ),
    )
    rank_by_recipe = {str(row["flattened_recipe_trace"]): rank for rank, row in enumerate(ranked, start=1)}
    atlas_rows = [{**row, "support_rank": rank_by_recipe[str(row["flattened_recipe_trace"])]} for row in raw_rows]
    write_tsv(OUT / "gdt468_2300_recipe_support_atlas.tsv", atlas_rows)

    carrier_rows: list[dict[str, object]] = []
    for recipe_row in atlas_rows:
        recipe = str(recipe_row["flattened_recipe_trace"])
        run_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in running_by_recipe.get(recipe, []):
            run_groups[row["surface"]].append(row)
        for surface, rows in sorted(run_groups.items()):
            carrier_rows.append({
                "carrier_id": f"G468-C{len(carrier_rows) + 1:04d}", "recipe_id": recipe_row["recipe_id"],
                "flattened_recipe_trace": recipe, "source_layer": "GDT407_RUNNING_EXACT",
                "carrier_surface": surface, "carrier_count": len(rows),
                "pages": joined({row["physical_page"] for row in rows}), "registers_or_classes": joined({row["register"] for row in rows}),
                "carrier_status": "EXACT_CONTIGUOUS_RECIPE",
            })
        for layer, rows in (("GDT466_ADDRESS_FULL", full_by_recipe.get(recipe, [])), ("GDT466_ADDRESS_HYBRID", hybrid_by_recipe.get(recipe, []))):
            for row in sorted(rows, key=lambda item: item["surface"]):
                carrier_rows.append({
                    "carrier_id": f"G468-C{len(carrier_rows) + 1:04d}", "recipe_id": recipe_row["recipe_id"],
                    "flattened_recipe_trace": recipe, "source_layer": layer,
                    "carrier_surface": row["surface"], "carrier_count": 1,
                    "pages": row["physical_page"], "registers_or_classes": row["content_class"],
                    "carrier_status": "EXACT_FULL_ADDRESS_FORMULA" if layer == "GDT466_ADDRESS_FULL" else "FUNCTION_TRACE_ACROSS_LEARNED_CORE",
                })
    if carrier_rows:
        write_tsv(OUT / "gdt468_old_recipe_carriers.tsv", carrier_rows)
    else:
        raise RuntimeError("Expected old recipe carriers")

    shell_support: list[dict[str, object]] = []
    atlas_map = {str(row["flattened_recipe_trace"]): row for row in atlas_rows}
    for shell in shells:
        support = atlas_map[shell["flattened_recipe_trace"]]
        shell_support.append({
            **shell,
            "recipe_id": support["recipe_id"], "support_rank": support["support_rank"],
            "support_tier": support["support_tier"], "running_surface_type_count": support["running_surface_type_count"],
            "running_event_count": support["running_event_count"], "running_page_count": support["running_page_count"],
            "address_full_formula_count": support["address_full_formula_count"],
            "address_hybrid_shell_count": support["address_hybrid_shell_count"],
            "old_carrier_surface_count": support["old_carrier_surface_count"],
        })
    write_tsv(OUT / "gdt468_2760_supported_shell_phrasebook.tsv", shell_support)

    factorization_rows: list[dict[str, object]] = []
    for row in sorted((row for row in atlas_rows if int(row["shell_factorization_count"]) > 1), key=lambda item: int(item["support_rank"])):
        factorization_rows.append({
            "factorization_group_id": f"G468-F{len(factorization_rows) + 1:04d}",
            "recipe_id": row["recipe_id"], "flattened_recipe_trace": row["flattened_recipe_trace"],
            "shell_factorization_count": row["shell_factorization_count"], "shell_shapes": row["shell_shapes"],
            "surface_templates": row["surface_templates"], "exact_channel_signatures": row["exact_channel_signatures"],
            "support_rank": row["support_rank"], "support_tier": row["support_tier"],
            "running_surface_type_count": row["running_surface_type_count"], "running_event_count": row["running_event_count"],
            "running_page_count": row["running_page_count"], "running_surfaces": row["running_surfaces"],
            "address_full_formula_count": row["address_full_formula_count"], "address_full_formula_surfaces": row["address_full_formula_surfaces"],
            "address_hybrid_shell_count": row["address_hybrid_shell_count"], "address_hybrid_shell_surfaces": row["address_hybrid_shell_surfaces"],
            "disposition": "KEEP_ALL_VISIBLE_FACTORIZATIONS__RANK_BY_SHARED_RECIPE_SUPPORT",
        })
    if len(factorization_rows) != 423:
        raise RuntimeError(f"Expected 423 factorization families, got {len(factorization_rows)}")
    write_tsv(OUT / "gdt468_423_factorization_family_support.tsv", factorization_rows)

    tier_counts = Counter(str(row["support_tier"]) for row in atlas_rows)
    shell_tier_counts = Counter(str(row["support_tier"]) for row in shell_support)
    factor_tier_counts = Counter(str(row["support_tier"]) for row in factorization_rows)
    result = {
        "status": "SHELL_RECIPES_SEPARATED_INTO_OLD_CARRIER_AND_COMPOSITION_TIERS",
        "shell_count": len(shells), "recipe_count": len(atlas_rows), "running_event_count": len(running), "address_label_count": len(addresses),
        "recipe_support_tier_counts": dict(sorted(tier_counts.items())),
        "shell_support_tier_counts": dict(sorted(shell_tier_counts.items())),
        "recipe_with_any_old_carrier_count": sum(row["support_tier"] != "COMPOSITION_ONLY" for row in atlas_rows),
        "composition_only_recipe_count": tier_counts["COMPOSITION_ONLY"],
        "matched_running_event_count": sum(len(rows) for rows in running_by_recipe.values()),
        "matched_running_surface_type_count": len({row["surface"] for rows in running_by_recipe.values() for row in rows}),
        "matched_running_page_count": len({row["physical_page"] for rows in running_by_recipe.values() for row in rows}),
        "matched_address_full_label_count": sum(len(rows) for rows in full_by_recipe.values()),
        "matched_address_hybrid_label_count": sum(len(rows) for rows in hybrid_by_recipe.values()),
        "carrier_row_count": len(carrier_rows),
        "factorization_family_count": len(factorization_rows),
        "factorization_support_tier_counts": dict(sorted(factor_tier_counts.items())),
        "top_supported_recipe": ranked[0]["flattened_recipe_trace"],
        "top_supported_running_event_count": ranked[0]["running_event_count"],
        "top_supported_running_page_count": ranked[0]["running_page_count"],
        "new_pages": 0, "new_channels": 0, "new_component_meanings": 0, "surface_predictions": 0, "confirmed_lexemes": 0,
    }
    (OUT / "gdt468_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
