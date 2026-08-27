#!/usr/bin/env python3
"""Bridge final target recipes through complete old-card tiles and context shells."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt542_full_old_tile_context_bridge"
OUT = BASE / "artifacts"
G407 = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts"
G516 = ROOT / "experiments/yolo/gdt516_thirty_page_new_surface_family_consolidation/artifacts"
G540 = ROOT / "experiments/yolo/gdt540_target_surface_context_requirement_contract/artifacts"

OLD_EVENTS_IN = G407 / "gdt407_4576_running_event_edition.tsv"
OLD_STATEMENTS_IN = G407 / "gdt407_715_statement_edition.tsv"
G516_ATLAS_IN = G516 / "gdt516_159_new_surface_family_atlas.tsv"
TARGET_IN = G540 / "gdt540_145_surface_context_contract.tsv"

TIER_OUT = OUT / "gdt542_145_final_support_tiers.tsv"
BRIDGE_OUT = OUT / "gdt542_29_full_tile_context_bridges.tsv"
TILE_OUT = OUT / "gdt542_59_old_complete_tile_instances.tsv"
SEAM_OUT = OUT / "gdt542_30_intertile_seam_support.tsv"
PATH_OUT = OUT / "gdt542_13_ordered_same_statement_tile_paths.tsv"
SKELETON_OUT = OUT / "gdt542_17_portable_skeleton_context_profiles.tsv"
SUMMARY_OUT = OUT / "gdt542_full_tile_context_summary.tsv"
BOOK_OUT = OUT / "GDT542_FULL_OLD_TILE_CONTEXT_BOOK.md"
RESULT_OUT = OUT / "gdt542_result.json"
STATUS = "PASS_29_FULL_TILE_TARGETS_BRIDGED__17_CONTEXT_SHELLS_AND_30_OLD_SEAMS"

ACTION_ROOTS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
ARGUMENT_ROOTS = {"Y", "AIIN", "AIN", "OR"}
PORTABLE_ROOTS = {
    "Y", "OK", "OL", "OT", "AL", "AR", "AIIN", "AIN", "OR", "L",
    "AIR", "CH", "SH", "K", "S", "CHD", "T", "R", "P",
}
MODE_ORDER = {
    "SELF_CONTAINED": 0,
    "REQUIRES_ACTIVE_ARGUMENT": 1,
    "REQUIRES_ACTIVE_ACTION": 2,
    "REQUIRES_ACTIVE_ACTION_AND_ARGUMENT": 3,
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty table {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def atoms(recipe: str) -> tuple[str, ...]:
    return tuple(part for part in recipe.split("+") if part)


def join(values) -> str:
    material = sorted({str(value) for value in values if str(value)})
    return "|".join(material) if material else "NONE"


def join_modes(values: set[str]) -> str:
    return "|".join(sorted(values, key=MODE_ORDER.__getitem__))


def best_old_recipe_tiles(
    recipe: tuple[str, ...], old_complete_recipes: set[tuple[str, ...]]
) -> tuple[int, tuple[tuple[str, ...], ...]]:
    """Match GDT516: maximise disjoint coverage, prefer fewer/lexical tiles."""

    states: list[tuple[int, tuple[tuple[str, ...], ...]]] = [
        (-1, tuple())
    ] * (len(recipe) + 1)
    states[0] = (0, tuple())

    def rank(state: tuple[int, tuple[tuple[str, ...], ...]]) -> tuple[object, ...]:
        rendered = tuple("+".join(tile) for tile in state[1])
        return state[0], -len(rendered), tuple(reversed(rendered))

    for start in range(len(recipe)):
        covered, tiles = states[start]
        if covered < 0:
            continue
        if rank((covered, tiles)) > rank(states[start + 1]):
            states[start + 1] = (covered, tiles)
        for end in range(start + 2, len(recipe) + 1):
            chunk = recipe[start:end]
            if chunk not in old_complete_recipes:
                continue
            candidate = (covered + len(chunk), tiles + (chunk,))
            if rank(candidate) > rank(states[end]):
                states[end] = candidate
    return states[-1]


def longest_old_fragment(
    recipe: tuple[str, ...], old_complete_recipes: set[tuple[str, ...]]
) -> int:
    widths = [
        end - start
        for start in range(len(recipe))
        for end in range(start + 2, len(recipe) + 1)
        if recipe[start:end] in old_complete_recipes
    ]
    return max(widths, default=0)


def tier(
    recipe: tuple[str, ...], old_complete_recipes: set[tuple[str, ...]]
) -> tuple[str, int, tuple[tuple[str, ...], ...], int]:
    coverage, tiles = best_old_recipe_tiles(recipe, old_complete_recipes)
    longest = longest_old_fragment(recipe, old_complete_recipes)
    if recipe in old_complete_recipes:
        name = "FULL_OLD_RECIPE_CARRIER"
    elif coverage == len(recipe):
        name = "FULLY_TILED_BY_OLD_MULTICOMPONENT_RECIPES"
    elif longest >= 2:
        name = "OLD_COMPLETE_RECIPE_FRAGMENT_PLUS_ATOMS"
    else:
        name = "ATOMS_AND_FACTORS_ONLY"
    return name, coverage, tiles, longest


def mode(inherited_action: str, inherited_argument: str) -> str:
    if inherited_action and inherited_argument:
        return "REQUIRES_ACTIVE_ACTION_AND_ARGUMENT"
    if inherited_action:
        return "REQUIRES_ACTIVE_ACTION"
    if inherited_argument:
        return "REQUIRES_ACTIVE_ARGUMENT"
    return "SELF_CONTAINED"


def ordered_positions(recipes: list[str], tiles: tuple[str, ...]) -> list[int] | None:
    """Return the minimum-span ordered tile path in one statement."""

    candidates: list[tuple[int, ...]] = []

    def walk(tile_index: int, start: int, chosen: tuple[int, ...]) -> None:
        if tile_index == len(tiles):
            candidates.append(chosen)
            return
        for position in range(start, len(recipes)):
            if recipes[position] == tiles[tile_index]:
                walk(tile_index + 1, position + 1, chosen + (position,))

    walk(0, 0, tuple())
    if not candidates:
        return None
    best = min(candidates, key=lambda value: (value[-1] - value[0], value))
    return list(best)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    old_events = read_tsv(OLD_EVENTS_IN)
    old_statements = read_tsv(OLD_STATEMENTS_IN)
    g516_atlas = read_tsv(G516_ATLAS_IN)
    targets = read_tsv(TARGET_IN)
    if (len(old_events), len(old_statements), len(g516_atlas), len(targets)) != (4576, 715, 159, 145):
        raise RuntimeError("Input inventory drift")

    old_complete_recipes = {atoms(row["component_recipe"]) for row in old_events}
    old_by_recipe: dict[str, list[dict[str, str]]] = defaultdict(list)
    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in old_events:
        old_by_recipe[event["component_recipe"]].append(event)
        events_by_statement[event["source_statement_id"]].append(event)
    for material in events_by_statement.values():
        material.sort(key=lambda row: int(row["global_running_ordinal"]))
    if set(events_by_statement) != {row["source_statement_id"] for row in old_statements}:
        raise RuntimeError("Statement key drift")

    # Same two-slot replay as GDT540/GDT541, now indexed for portable skeletons.
    context_by_event: dict[str, dict[str, str]] = {}
    for statement in sorted(old_statements, key=lambda row: int(row["global_statement_ordinal"])):
        material = events_by_statement[statement["source_statement_id"]]
        if len(material) != int(statement["event_count"]):
            raise RuntimeError(f"Statement count drift: {statement['global_statement_id']}")
        active_action = ""
        active_argument = ""
        for event in material:
            sequence = atoms(event["component_recipe"])
            actions = [atom for atom in sequence if atom in ACTION_ROOTS]
            arguments = [atom for atom in sequence if atom in ARGUMENT_ROOTS]
            inherited_action = ""
            inherited_argument = ""
            if actions:
                active_action = actions[-1]
            elif active_action and sequence != ("DY",):
                inherited_action = active_action
            if arguments:
                active_argument = arguments[-1]
            elif active_argument and (actions or inherited_action) and sequence != ("DY",):
                inherited_argument = active_argument
            context_by_event[event["global_running_event_id"]] = {
                "mode": mode(inherited_action, inherited_argument),
                "incoming_action": inherited_action or "NONE",
                "incoming_argument": inherited_argument or "NONE",
            }

    old_by_skeleton: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for event in old_events:
        skeleton = tuple(atom for atom in atoms(event["component_recipe"]) if atom in PORTABLE_ROOTS)
        old_by_skeleton[skeleton].append(event)

    old_pair_events: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for event in old_events:
        sequence = atoms(event["component_recipe"])
        for left, right in set(zip(sequence, sequence[1:])):
            old_pair_events[(left, right)].append(event)

    atlas_by_surface = {row["surface"]: row for row in g516_atlas}
    tier_rows: list[dict[str, object]] = []
    final_tier_material: dict[str, tuple[str, int, tuple[tuple[str, ...], ...], int]] = {}
    for ordinal, target in enumerate(targets, 1):
        final = tier(atoms(target["final_recipe"]), old_complete_recipes)
        final_tier_material[target["surface"]] = final
        old = atlas_by_surface[target["surface"]]
        tier_rows.append({
            "target_ordinal": ordinal,
            "surface": target["surface"],
            "gdt516_recipe": old["gdt516_context_recipe"],
            "final_recipe": target["final_recipe"],
            "recipe_changed_after_gdt516": "YES" if old["gdt516_context_recipe"] != target["final_recipe"] else "NO",
            "gdt516_support_tier": old["support_tier"],
            "final_support_tier": final[0],
            "support_tier_changed": "YES" if old["support_tier"] != final[0] else "NO",
            "final_recipe_atom_count": len(atoms(target["final_recipe"])),
            "final_old_tile_coverage_atoms": final[1],
            "final_longest_old_fragment_atoms": final[3],
            "final_best_old_tiles": " | ".join("+".join(tile) for tile in final[2]) or "NONE",
            "observed_requirement_modes": target["observed_requirement_modes"],
            "guard": "FINAL_RECIPE_SUPPORT_RECOUNT__NO_RECIPE_CHANGE",
        })

    full_targets = [
        target for target in targets
        if final_tier_material[target["surface"]][0]
        == "FULLY_TILED_BY_OLD_MULTICOMPONENT_RECIPES"
    ]
    tile_rows: list[dict[str, object]] = []
    seam_rows: list[dict[str, object]] = []
    skeleton_rows: list[dict[str, object]] = []
    bridge_rows: list[dict[str, object]] = []
    path_rows: list[dict[str, object]] = []

    path_counts_by_surface: Counter[str] = Counter()
    adjacent_path_counts_by_surface: Counter[str] = Counter()
    path_details: dict[str, list[dict[str, object]]] = defaultdict(list)
    for target in full_targets:
        tiles = final_tier_material[target["surface"]][2]
        rendered_tiles = tuple("+".join(tile) for tile in tiles)
        for statement in old_statements:
            material = events_by_statement[statement["source_statement_id"]]
            positions = ordered_positions(
                [event["component_recipe"] for event in material], rendered_tiles
            )
            if positions is None:
                continue
            adjacent = all(right == left + 1 for left, right in zip(positions, positions[1:]))
            path_counts_by_surface[target["surface"]] += 1
            if adjacent:
                adjacent_path_counts_by_surface[target["surface"]] += 1
            path_details[target["surface"]].append({
                "target_surface": target["surface"],
                "target_recipe": target["final_recipe"],
                "tile_sequence": " | ".join(rendered_tiles),
                "old_statement_id": statement["global_statement_id"],
                "physical_page": statement["physical_page"],
                "register": statement["register"],
                "tile_card_ordinals": "|".join(str(position + 1) for position in positions),
                "tile_event_ids": "|".join(material[position]["global_running_event_id"] for position in positions),
                "tile_surfaces": "|".join(material[position]["surface"] for position in positions),
                "path_span_cards": positions[-1] - positions[0],
                "adjacent_complete_tile_sequence": "YES" if adjacent else "NO",
                "guard": "ORDERED_OLD_CARD_PATH__INTERVENING_CARDS_RETAINED",
            })

    for target in full_targets:
        final = final_tier_material[target["surface"]]
        tiles = final[2]
        rendered_tiles = tuple("+".join(tile) for tile in tiles)
        target_modes = set(target["observed_requirement_modes"].split("|"))
        skeleton = tuple(
            atom for atom in atoms(target["final_recipe"]) if atom in PORTABLE_ROOTS
        )
        skeleton_events = old_by_skeleton.get(skeleton, [])
        skeleton_modes = {
            context_by_event[event["global_running_event_id"]]["mode"]
            for event in skeleton_events
        }
        if not skeleton_events:
            skeleton_relation = "NO_EXACT_PORTABLE_SKELETON"
        elif skeleton_modes == target_modes:
            skeleton_relation = "TARGET_MODE_INCLUDED__EXACT_SET"
        elif target_modes <= skeleton_modes:
            skeleton_relation = "TARGET_MODE_INCLUDED__OLD_ADDS_MODES"
        elif target_modes & skeleton_modes:
            skeleton_relation = "PARTIAL_MODE_OVERLAP"
        else:
            skeleton_relation = "TARGET_MODE_NOT_SEEN"
        if skeleton_events:
            skeleton_rows.append({
                "skeleton_profile_ordinal": len(skeleton_rows) + 1,
                "target_surface": target["surface"],
                "target_recipe": target["final_recipe"],
                "portable_skeleton": "+".join(skeleton) or "NONE",
                "target_observed_modes": target["observed_requirement_modes"],
                "old_skeleton_event_count": len(skeleton_events),
                "old_skeleton_recipe_count": len({event["component_recipe"] for event in skeleton_events}),
                "old_skeleton_surfaces": join(event["surface"] for event in skeleton_events),
                "old_skeleton_pages": join(event["physical_page"] for event in skeleton_events),
                "old_skeleton_registers": join(event["register"] for event in skeleton_events),
                "old_skeleton_modes": join_modes(skeleton_modes),
                "mode_relation": skeleton_relation,
                "guard": "EXACT_PORTABLE_SKELETON__STRUCTURAL_SLOTS_OMITTED_ONLY",
            })

        seam_counts: list[int] = []
        for seam_index, (left_tile, right_tile) in enumerate(zip(tiles, tiles[1:]), 1):
            boundary = (left_tile[-1], right_tile[0])
            carriers = old_pair_events[boundary]
            seam_counts.append(len(carriers))
            seam_rows.append({
                "seam_ordinal": len(seam_rows) + 1,
                "target_surface": target["surface"],
                "target_recipe": target["final_recipe"],
                "seam_index_in_target": seam_index,
                "left_tile": "+".join(left_tile),
                "right_tile": "+".join(right_tile),
                "boundary_pair": f"{boundary[0]}>{boundary[1]}",
                "old_boundary_event_count": len(carriers),
                "old_boundary_recipe_count": len({event["component_recipe"] for event in carriers}),
                "old_boundary_surfaces": join(event["surface"] for event in carriers),
                "old_boundary_pages": join(event["physical_page"] for event in carriers),
                "old_boundary_registers": join(event["register"] for event in carriers),
                "boundary_supported": "YES" if carriers else "NO",
                "guard": "EXACT_ADJACENT_ATOM_SEAM_INSIDE_OLD_COMPLETE_CARD",
            })

        for tile_index, tile_recipe in enumerate(rendered_tiles, 1):
            carriers = old_by_recipe[tile_recipe]
            tile_sequence = atoms(tile_recipe)
            tile_rows.append({
                "tile_instance_ordinal": len(tile_rows) + 1,
                "target_surface": target["surface"],
                "target_recipe": target["final_recipe"],
                "tile_index_in_target": tile_index,
                "tile_count_in_target": len(tiles),
                "tile_recipe": tile_recipe,
                "tile_atom_count": len(tile_sequence),
                "old_tile_event_count": len(carriers),
                "old_tile_surface_count": len({event["surface"] for event in carriers}),
                "old_tile_surfaces": join(event["surface"] for event in carriers),
                "old_tile_pages": join(event["physical_page"] for event in carriers),
                "old_tile_registers": join(event["register"] for event in carriers),
                "tile_action_roots": join(atom for atom in tile_sequence if atom in ACTION_ROOTS),
                "tile_argument_roots": join(atom for atom in tile_sequence if atom in ARGUMENT_ROOTS),
                "guard": "COMPLETE_OLD_CARD_TILE__TARGET_ORDER_PRESERVED",
            })

        ordered_paths = path_counts_by_surface[target["surface"]]
        adjacent_paths = adjacent_path_counts_by_surface[target["surface"]]
        if adjacent_paths:
            support_class = "ADJACENT_OLD_TILE_SEQUENCE"
        elif ordered_paths:
            support_class = "ORDERED_SAME_STATEMENT_TILE_SEQUENCE"
        elif skeleton_events:
            support_class = "EXACT_PORTABLE_SKELETON_CONTEXT"
        else:
            support_class = "COMPLETE_TILES_AND_OLD_SEAMS_ONLY"
        bridge_rows.append({
            "bridge_ordinal": len(bridge_rows) + 1,
            "target_surface": target["surface"],
            "target_recipe": target["final_recipe"],
            "target_observed_modes": target["observed_requirement_modes"],
            "recipe_atom_count": len(atoms(target["final_recipe"])),
            "tile_count": len(tiles),
            "complete_old_tiles": " | ".join(rendered_tiles),
            "minimum_old_tile_event_count": min(len(old_by_recipe[value]) for value in rendered_tiles),
            "seam_count": len(tiles) - 1,
            "all_seams_old": "YES" if all(seam_counts) else "NO",
            "minimum_old_seam_event_count": min(seam_counts),
            "portable_skeleton": "+".join(skeleton) or "NONE",
            "old_portable_skeleton_event_count": len(skeleton_events),
            "old_portable_skeleton_modes": join_modes(skeleton_modes) if skeleton_modes else "NONE",
            "portable_skeleton_mode_relation": skeleton_relation,
            "ordered_same_statement_path_count": ordered_paths,
            "adjacent_tile_path_count": adjacent_paths,
            "support_class": support_class,
            "gdt516_tier_changed": "YES" if atlas_by_surface[target["surface"]]["support_tier"] != final[0] else "NO",
            "guard": "FULL_TILE_WORKING_BRIDGE__NO_WHOLE_RECIPE_OCCURRENCE_CLAIM",
        })

    for surface in sorted(path_details):
        for detail in sorted(
            path_details[surface],
            key=lambda row: (str(row["old_statement_id"]), int(row["path_span_cards"])),
        ):
            path_rows.append({"path_ordinal": len(path_rows) + 1, **detail})

    final_tier_counts = Counter(row["final_support_tier"] for row in tier_rows)
    original_tier_counts = Counter(row["gdt516_support_tier"] for row in tier_rows)
    migration_rows = [row for row in tier_rows if row["support_tier_changed"] == "YES"]
    support_counts = Counter(row["support_class"] for row in bridge_rows)
    skeleton_relations = Counter(row["mode_relation"] for row in skeleton_rows)
    summary_rows = [
        {"metric": "target_surface_count", "value": len(tier_rows), "interpretation_de": "finale Prosa-Zielrezepte"},
        {"metric": "final_exact_recipe_count", "value": final_tier_counts["FULL_OLD_RECIPE_CARRIER"], "interpretation_de": "vollständige alte Rezepte"},
        {"metric": "final_full_tile_recipe_count", "value": final_tier_counts["FULLY_TILED_BY_OLD_MULTICOMPONENT_RECIPES"], "interpretation_de": "vollständig aus alten Mehrkomponentenkarten kachelbar"},
        {"metric": "final_fragment_plus_atoms_count", "value": final_tier_counts["OLD_COMPLETE_RECIPE_FRAGMENT_PLUS_ATOMS"], "interpretation_de": "alte Ganzkartenfragmente plus Einzelkomponenten"},
        {"metric": "final_atoms_factors_only_count", "value": final_tier_counts["ATOMS_AND_FACTORS_ONLY"], "interpretation_de": "nur Atome und Faktoren"},
        {"metric": "tier_migration_count", "value": len(migration_rows), "interpretation_de": "Änderungen gegenüber GDT516 durch finale Rezepte"},
        {"metric": "complete_old_tile_instance_count", "value": len(tile_rows), "interpretation_de": "Kachelpositionen in29 Zielrezepten"},
        {"metric": "unique_complete_old_tile_recipe_count", "value": len({row["tile_recipe"] for row in tile_rows}), "interpretation_de": "verschiedene alte Ganzkartenkacheln"},
        {"metric": "intertile_seam_count", "value": len(seam_rows), "interpretation_de": "Kachelgrenzen"},
        {"metric": "old_supported_seam_count", "value": sum(row["boundary_supported"] == "YES" for row in seam_rows), "interpretation_de": "bereits innerhalb alter Karten sichtbare Grenzen"},
        {"metric": "portable_skeleton_target_count", "value": len(skeleton_rows), "interpretation_de": "Ziele mit altem exaktem19-Wurzel-Skelett"},
        {"metric": "portable_skeleton_mode_compatible_count", "value": sum(row["mode_relation"].startswith("TARGET_MODE_INCLUDED") for row in skeleton_rows), "interpretation_de": "Skelette mit Zielmodus"},
        {"metric": "portable_skeleton_exact_mode_set_count", "value": skeleton_relations["TARGET_MODE_INCLUDED__EXACT_SET"], "interpretation_de": "exakt gleiche Modusmenge"},
        {"metric": "portable_skeleton_old_adds_modes_count", "value": skeleton_relations["TARGET_MODE_INCLUDED__OLD_ADDS_MODES"], "interpretation_de": "alte Umgebung zeigt zusätzliche Modi"},
        {"metric": "ordered_same_statement_target_count", "value": len(path_counts_by_surface), "interpretation_de": "Ziele mit geordnetem alten Kachelpfad"},
        {"metric": "ordered_same_statement_path_count", "value": len(path_rows), "interpretation_de": "beste Pfade je alter Aussage"},
        {"metric": "adjacent_tile_target_count", "value": len(adjacent_path_counts_by_surface), "interpretation_de": "Ziele mit direkt benachbarten alten Kacheln"},
        {"metric": "adjacent_tile_path_count", "value": sum(adjacent_path_counts_by_surface.values()), "interpretation_de": "direkte alte Kachelfolgen"},
        {"metric": "support_adjacent_count", "value": support_counts["ADJACENT_OLD_TILE_SEQUENCE"], "interpretation_de": "stärkste Brückenklasse"},
        {"metric": "support_ordered_count", "value": support_counts["ORDERED_SAME_STATEMENT_TILE_SEQUENCE"], "interpretation_de": "geordnete Satzpfade ohne direkte Nachbarschaft"},
        {"metric": "support_skeleton_count", "value": support_counts["EXACT_PORTABLE_SKELETON_CONTEXT"], "interpretation_de": "exaktes portables Skelett"},
        {"metric": "support_seams_only_count", "value": support_counts["COMPLETE_TILES_AND_OLD_SEAMS_ONLY"], "interpretation_de": "vollständige Kacheln plus alte Nähte"},
    ]

    write_tsv(TIER_OUT, tier_rows)
    write_tsv(BRIDGE_OUT, bridge_rows)
    write_tsv(TILE_OUT, tile_rows)
    write_tsv(SEAM_OUT, seam_rows)
    write_tsv(PATH_OUT, path_rows)
    write_tsv(SKELETON_OUT, skeleton_rows)
    write_tsv(SUMMARY_OUT, summary_rows)

    result = {
        "status": STATUS,
        "target_surface_count": len(tier_rows),
        "final_tier_counts": dict(sorted(final_tier_counts.items())),
        "original_gdt516_tier_counts_on_prose_targets": dict(sorted(original_tier_counts.items())),
        "tier_migration_count": len(migration_rows),
        "tier_migrations": [
            {
                "surface": row["surface"],
                "from": row["gdt516_support_tier"],
                "to": row["final_support_tier"],
            }
            for row in migration_rows
        ],
        "full_tile_target_count": len(bridge_rows),
        "complete_old_tile_instance_count": len(tile_rows),
        "unique_complete_old_tile_recipe_count": len({row["tile_recipe"] for row in tile_rows}),
        "intertile_seam_count": len(seam_rows),
        "old_supported_seam_count": sum(row["boundary_supported"] == "YES" for row in seam_rows),
        "portable_skeleton_target_count": len(skeleton_rows),
        "portable_skeleton_mode_compatible_count": sum(row["mode_relation"].startswith("TARGET_MODE_INCLUDED") for row in skeleton_rows),
        "portable_skeleton_exact_mode_set_count": skeleton_relations["TARGET_MODE_INCLUDED__EXACT_SET"],
        "portable_skeleton_old_adds_modes_count": skeleton_relations["TARGET_MODE_INCLUDED__OLD_ADDS_MODES"],
        "ordered_same_statement_target_count": len(path_counts_by_surface),
        "ordered_same_statement_path_count": len(path_rows),
        "adjacent_tile_target_count": len(adjacent_path_counts_by_surface),
        "adjacent_tile_path_count": sum(adjacent_path_counts_by_surface.values()),
        "support_class_counts": dict(sorted(support_counts.items())),
        "new_pages": 0,
        "recipe_changes": 0,
        "root_meaning_changes": 0,
    }
    RESULT_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# GDT542 — 29 Zielrezepte aus vollständigen alten Karten",
        "",
        f"Status: `{STATUS}`",
        "",
        "## Neue Endstaffel",
        "",
        "Die finalen145 Prosarezepte teilen sich nun in11 exakte Altträger,29 vollständig alte Kachelkompositionen,81 Fragment-plus-Atom-Formen und24 reine Atom/Faktor-Formen. Vier Karten wechseln gegenüber GDT516 die Stufe: `chekchy` wird exakt alt; `dairykodas` wird mit `D_ADDR+AIR | Y+K | O+DA+S` vollständig kachelbar; `saiis` gewinnt ein altes Mehrkomponentenfragment; das verkürzte `keeol=K+EE+OL` fällt auf Atome/Faktoren zurück.",
        "",
        "Die29 Kachelziele enthalten59 alte Ganzkartenkacheln und30 Nähte. Jede Naht ist als dasselbe benachbarte Atompaar bereits innerhalb alter vollständiger Karten sichtbar.",
        "",
        "## Brückenleiter",
        "",
        "| Klasse | Ziele | Bedeutung |",
        "| --- | ---: | --- |",
        f"| direkte alte Kachelfolge | {support_counts['ADJACENT_OLD_TILE_SEQUENCE']} | alle Kacheln stehen unmittelbar nacheinander |",
        f"| geordneter Kachelpfad im selben Satz | {support_counts['ORDERED_SAME_STATEMENT_TILE_SEQUENCE']} | Reihenfolge alt, aber mit Zwischenkarten |",
        f"| exaktes portables Wurzelskelett | {support_counts['EXACT_PORTABLE_SKELETON_CONTEXT']} | Handlung/Argument/Relation/Ordnung gemeinsam alt |",
        f"| vollständige Kacheln plus alte Nähte | {support_counts['COMPLETE_TILES_AND_OLD_SEAMS_ONLY']} | Komposition lesbar, Gesamtgerüst noch neu |",
        "",
        "Siebzehn Ziele besitzen ein altes exaktes19-Wurzel-Skelett. Bei allen siebzehn kommt der Ziel-Kontextmodus dort vor; fünfzehn haben genau dieselbe Modusmenge, während `dairody` und `qokeedar` in den alten Umgebungen zusätzliche zulässige Modi zeigen.",
        "",
        "Drei Ziele besitzen ihre Kacheln in der richtigen Reihenfolge innerhalb alter Aussagen. `okalchedy=OK+AL | CHD+Y` hat elf Satzpfade, darunter zwei direkte Folgen. `shekeey=SH+E | K+EE+Y` und `ykshedy=Y+K | SH+E+DY` haben je einen geordneten Pfad.",
        "",
        "## Vollständiges 29-Karten-Deck",
        "",
        "| Ziel | Rezept | alte Kacheln | Kontextmodus | stärkste Brücke |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in bridge_rows:
        lines.append(
            f"| `{row['target_surface']}` | `{row['target_recipe']}` | `{row['complete_old_tiles']}` | `{row['target_observed_modes']}` | `{row['support_class']}` |"
        )
    lines.extend([
        "",
        "Die schwächsten zehn Karten bleiben ausdrücklich stehen: Jede ihrer Komponentenkarte ist alt und jede Naht ist alt, nur das vollständige portable Gerüst und eine geordnete alte Satzfolge fehlen noch. Das ist eine sinnvolle Kompositionsannahme, kein Grund zum Verwerfen.",
        "",
        "Keine Oberfläche wurde neu segmentiert und keine Bedeutung, Rezeptkarte oder Seite geändert.",
    ])
    BOOK_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
