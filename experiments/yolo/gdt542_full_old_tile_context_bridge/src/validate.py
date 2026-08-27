#!/usr/bin/env python3
"""Validate the GDT542 complete-old-tile context bridge."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
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

TIER = OUT / "gdt542_145_final_support_tiers.tsv"
BRIDGE = OUT / "gdt542_29_full_tile_context_bridges.tsv"
TILE = OUT / "gdt542_59_old_complete_tile_instances.tsv"
SEAM = OUT / "gdt542_30_intertile_seam_support.tsv"
PATH = OUT / "gdt542_13_ordered_same_statement_tile_paths.tsv"
SKELETON = OUT / "gdt542_17_portable_skeleton_context_profiles.tsv"
SUMMARY = OUT / "gdt542_full_tile_context_summary.tsv"
BOOK = OUT / "GDT542_FULL_OLD_TILE_CONTEXT_BOOK.md"
RESULT = OUT / "gdt542_result.json"
VALIDATION = OUT / "gdt542_validation.json"
RUN = BASE / "src/run.py"
READER = BASE / "src/tile_bridge.py"
STATUS = "PASS_29_FULL_TILE_TARGETS_BRIDGED__17_CONTEXT_SHELLS_AND_30_OLD_SEAMS"

ACTION_ROOTS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
ARGUMENT_ROOTS = {"Y", "AIIN", "AIN", "OR"}
PORTABLE_ROOTS = {
    "Y", "OK", "OL", "OT", "AL", "AR", "AIIN", "AIN", "OR", "L",
    "AIR", "CH", "SH", "K", "S", "CHD", "T", "R", "P",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def atoms(recipe: str) -> tuple[str, ...]:
    return tuple(recipe.split("+"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def best_tiles(
    recipe: tuple[str, ...], old: set[tuple[str, ...]]
) -> tuple[int, tuple[tuple[str, ...], ...]]:
    states: list[tuple[int, tuple[tuple[str, ...], ...]]] = [(-1, tuple())] * (
        len(recipe) + 1
    )
    states[0] = (0, tuple())

    def rank(value: tuple[int, tuple[tuple[str, ...], ...]]) -> tuple[object, ...]:
        rendered = tuple("+".join(tile) for tile in value[1])
        return value[0], -len(rendered), tuple(reversed(rendered))

    for start in range(len(recipe)):
        covered, tiles = states[start]
        if covered < 0:
            continue
        if rank((covered, tiles)) > rank(states[start + 1]):
            states[start + 1] = (covered, tiles)
        for end in range(start + 2, len(recipe) + 1):
            chunk = recipe[start:end]
            if chunk in old:
                candidate = (covered + len(chunk), tiles + (chunk,))
                if rank(candidate) > rank(states[end]):
                    states[end] = candidate
    return states[-1]


def longest(recipe: tuple[str, ...], old: set[tuple[str, ...]]) -> int:
    return max(
        (
            end - start
            for start in range(len(recipe))
            for end in range(start + 2, len(recipe) + 1)
            if recipe[start:end] in old
        ),
        default=0,
    )


def final_tier(recipe: tuple[str, ...], old: set[tuple[str, ...]]) -> str:
    coverage, _ = best_tiles(recipe, old)
    if recipe in old:
        return "FULL_OLD_RECIPE_CARRIER"
    if coverage == len(recipe):
        return "FULLY_TILED_BY_OLD_MULTICOMPONENT_RECIPES"
    if longest(recipe, old) >= 2:
        return "OLD_COMPLETE_RECIPE_FRAGMENT_PLUS_ATOMS"
    return "ATOMS_AND_FACTORS_ONLY"


def requirement(inherited_action: str, inherited_argument: str) -> str:
    if inherited_action and inherited_argument:
        return "REQUIRES_ACTIVE_ACTION_AND_ARGUMENT"
    if inherited_action:
        return "REQUIRES_ACTIVE_ACTION"
    if inherited_argument:
        return "REQUIRES_ACTIVE_ARGUMENT"
    return "SELF_CONTAINED"


def run_reader(surface: str) -> tuple[int, dict[str, object]]:
    proc = subprocess.run(
        [sys.executable, str(READER), surface],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return proc.returncode, json.loads(proc.stdout)


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    old_events = read_tsv(OLD_EVENTS_IN)
    old_statements = read_tsv(OLD_STATEMENTS_IN)
    atlas = read_tsv(G516_ATLAS_IN)
    targets = read_tsv(TARGET_IN)
    tiers = read_tsv(TIER)
    bridges = read_tsv(BRIDGE)
    tiles = read_tsv(TILE)
    seams = read_tsv(SEAM)
    paths = read_tsv(PATH)
    skeletons = read_tsv(SKELETON)
    summary = read_tsv(SUMMARY)
    result = json.loads(RESULT.read_text(encoding="utf-8"))

    check("old_event_count", len(old_events) == 4576, len(old_events))
    check("old_statement_count", len(old_statements) == 715, len(old_statements))
    check("gdt516_atlas_count", len(atlas) == 159, len(atlas))
    check("target_count", len(targets) == 145, len(targets))
    check("tier_row_count", len(tiers) == 145, len(tiers))
    check("bridge_count", len(bridges) == 29, len(bridges))
    check("tile_instance_count", len(tiles) == 59, len(tiles))
    check("seam_count", len(seams) == 30, len(seams))
    check("path_count", len(paths) == 13, len(paths))
    check("skeleton_count", len(skeletons) == 17, len(skeletons))

    old_complete = {atoms(row["component_recipe"]) for row in old_events}
    target_by_surface = {row["surface"]: row for row in targets}
    tier_by_surface = {row["surface"]: row for row in tiers}
    check("target_surface_uniqueness", len(target_by_surface) == 145, len(target_by_surface))
    check("tier_surface_set", set(tier_by_surface) == set(target_by_surface), len(set(tier_by_surface) ^ set(target_by_surface)))
    tier_errors = []
    for surface, target in target_by_surface.items():
        row = tier_by_surface[surface]
        expected = final_tier(atoms(target["final_recipe"]), old_complete)
        coverage, selected_tiles = best_tiles(atoms(target["final_recipe"]), old_complete)
        if (
            row["final_support_tier"] != expected
            or row["final_old_tile_coverage_atoms"] != str(coverage)
            or row["final_best_old_tiles"]
            != (" | ".join("+".join(tile) for tile in selected_tiles) or "NONE")
        ):
            tier_errors.append(surface)
    check("independent_final_tier_replay", not tier_errors, tier_errors)
    final_counts = Counter(row["final_support_tier"] for row in tiers)
    expected_final_counts = Counter({
        "FULL_OLD_RECIPE_CARRIER": 11,
        "FULLY_TILED_BY_OLD_MULTICOMPONENT_RECIPES": 29,
        "OLD_COMPLETE_RECIPE_FRAGMENT_PLUS_ATOMS": 81,
        "ATOMS_AND_FACTORS_ONLY": 24,
    })
    check("final_tier_distribution", final_counts == expected_final_counts, dict(final_counts))
    original_counts = Counter(row["gdt516_support_tier"] for row in tiers)
    expected_original_counts = Counter({
        "FULL_OLD_RECIPE_CARRIER": 10,
        "FULLY_TILED_BY_OLD_MULTICOMPONENT_RECIPES": 28,
        "OLD_COMPLETE_RECIPE_FRAGMENT_PLUS_ATOMS": 83,
        "ATOMS_AND_FACTORS_ONLY": 24,
    })
    check("original_prose_tier_distribution", original_counts == expected_original_counts, dict(original_counts))
    migrations = {
        row["surface"]: (row["gdt516_support_tier"], row["final_support_tier"])
        for row in tiers
        if row["support_tier_changed"] == "YES"
    }
    expected_migrations = {
        "chekchy": ("OLD_COMPLETE_RECIPE_FRAGMENT_PLUS_ATOMS", "FULL_OLD_RECIPE_CARRIER"),
        "dairykodas": ("OLD_COMPLETE_RECIPE_FRAGMENT_PLUS_ATOMS", "FULLY_TILED_BY_OLD_MULTICOMPONENT_RECIPES"),
        "keeol": ("OLD_COMPLETE_RECIPE_FRAGMENT_PLUS_ATOMS", "ATOMS_AND_FACTORS_ONLY"),
        "saiis": ("ATOMS_AND_FACTORS_ONLY", "OLD_COMPLETE_RECIPE_FRAGMENT_PLUS_ATOMS"),
    }
    check("tier_migration_inventory", migrations == expected_migrations, migrations)

    bridge_by_surface = {row["target_surface"]: row for row in bridges}
    expected_bridge_surfaces = {
        surface
        for surface, row in tier_by_surface.items()
        if row["final_support_tier"] == "FULLY_TILED_BY_OLD_MULTICOMPONENT_RECIPES"
    }
    check("bridge_surface_set", set(bridge_by_surface) == expected_bridge_surfaces, len(set(bridge_by_surface) ^ expected_bridge_surfaces))
    tiles_by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in tiles:
        tiles_by_surface[row["target_surface"]].append(row)
    tile_errors = []
    for surface, material in tiles_by_surface.items():
        material.sort(key=lambda row: int(row["tile_index_in_target"]))
        joined_recipe = "+".join(row["tile_recipe"] for row in material)
        if joined_recipe != bridge_by_surface[surface]["target_recipe"]:
            tile_errors.append((surface, "join"))
        for row in material:
            if atoms(row["tile_recipe"]) not in old_complete or int(row["tile_atom_count"]) < 2:
                tile_errors.append((surface, row["tile_recipe"]))
            actual_count = sum(event["component_recipe"] == row["tile_recipe"] for event in old_events)
            if int(row["old_tile_event_count"]) != actual_count:
                tile_errors.append((surface, "count:" + row["tile_recipe"]))
    check("tile_complete_recipe_replay", not tile_errors, tile_errors)
    check("unique_tile_recipe_count", len({row["tile_recipe"] for row in tiles}) == 42, len({row["tile_recipe"] for row in tiles}))
    check("dairykodas_final_tiling", bridge_by_surface["dairykodas"]["complete_old_tiles"] == "D_ADDR+AIR | Y+K | O+DA+S", bridge_by_surface["dairykodas"]["complete_old_tiles"])

    pair_events: Counter[tuple[str, str]] = Counter()
    for event in old_events:
        sequence = atoms(event["component_recipe"])
        for boundary in set(zip(sequence, sequence[1:])):
            pair_events[boundary] += 1
    seam_errors = []
    seams_by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in seams:
        seams_by_surface[row["target_surface"]].append(row)
        left, right = row["boundary_pair"].split(">")
        if pair_events[(left, right)] != int(row["old_boundary_event_count"]):
            seam_errors.append((row["target_surface"], row["boundary_pair"]))
        if row["boundary_supported"] != "YES" or int(row["old_boundary_event_count"]) <= 0:
            seam_errors.append((row["target_surface"], "unsupported"))
    check("all_seam_counts_replay", not seam_errors, seam_errors)
    check("all_bridges_have_all_seams", all(row["all_seams_old"] == "YES" for row in bridges), len(bridges))
    check("seam_cardinality_per_target", all(len(seams_by_surface[surface]) == int(row["tile_count"]) - 1 for surface, row in bridge_by_surface.items()), {surface: len(seams_by_surface[surface]) for surface in bridge_by_surface})
    check("rare_seam_air_o", next(row for row in seams if row["target_surface"] == "dairody")["old_boundary_event_count"] == "1", next(row for row in seams if row["target_surface"] == "dairody"))

    # Independent old context modes indexed by exact portable skeleton.
    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in old_events:
        events_by_statement[event["source_statement_id"]].append(event)
    for material in events_by_statement.values():
        material.sort(key=lambda row: int(row["global_running_ordinal"]))
    context_modes: dict[str, str] = {}
    for statement in old_statements:
        active_action = ""
        active_argument = ""
        for event in events_by_statement[statement["source_statement_id"]]:
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
            context_modes[event["global_running_event_id"]] = requirement(inherited_action, inherited_argument)
    old_by_skeleton: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for event in old_events:
        old_by_skeleton[tuple(atom for atom in atoms(event["component_recipe"]) if atom in PORTABLE_ROOTS)].append(event)
    skeleton_errors = []
    for row in skeletons:
        skeleton = tuple(row["portable_skeleton"].split("+")) if row["portable_skeleton"] != "NONE" else tuple()
        events = old_by_skeleton[skeleton]
        modes = {context_modes[event["global_running_event_id"]] for event in events}
        target_modes = set(row["target_observed_modes"].split("|"))
        if int(row["old_skeleton_event_count"]) != len(events) or set(row["old_skeleton_modes"].split("|")) != modes or not target_modes <= modes:
            skeleton_errors.append(row["target_surface"])
    check("portable_skeleton_replay", not skeleton_errors, skeleton_errors)
    relation_counts = Counter(row["mode_relation"] for row in skeletons)
    check("skeleton_relation_distribution", relation_counts == Counter({"TARGET_MODE_INCLUDED__EXACT_SET": 15, "TARGET_MODE_INCLUDED__OLD_ADDS_MODES": 2}), dict(relation_counts))
    extra_mode_surfaces = [row["target_surface"] for row in skeletons if row["mode_relation"] == "TARGET_MODE_INCLUDED__OLD_ADDS_MODES"]
    check("skeleton_extra_mode_inventory", extra_mode_surfaces == ["dairody", "qokeedar"], extra_mode_surfaces)
    check("skeleton_compatible_all", all(row["mode_relation"].startswith("TARGET_MODE_INCLUDED") for row in skeletons), len(skeletons))

    statement_by_global = {row["global_statement_id"]: row for row in old_statements}
    old_by_global_event = {row["global_running_event_id"]: row for row in old_events}
    path_errors = []
    for row in paths:
        statement = statement_by_global[row["old_statement_id"]]
        material = events_by_statement[statement["source_statement_id"]]
        ordinals = [int(value) for value in row["tile_card_ordinals"].split("|")]
        event_ids = row["tile_event_ids"].split("|")
        recipes = row["tile_sequence"].split(" | ")
        if not all(material[ordinal - 1]["global_running_event_id"] == event_id and old_by_global_event[event_id]["component_recipe"] == recipe for ordinal, event_id, recipe in zip(ordinals, event_ids, recipes)):
            path_errors.append(row["path_ordinal"])
        adjacent = all(right == left + 1 for left, right in zip(ordinals, ordinals[1:]))
        if (row["adjacent_complete_tile_sequence"] == "YES") != adjacent:
            path_errors.append(row["path_ordinal"] + ":adj")
    check("ordered_path_replay", not path_errors, path_errors)
    check("path_target_inventory", Counter(row["target_surface"] for row in paths) == Counter({"okalchedy": 11, "shekeey": 1, "ykshedy": 1}), dict(Counter(row["target_surface"] for row in paths)))
    check("adjacent_path_inventory", Counter(row["target_surface"] for row in paths if row["adjacent_complete_tile_sequence"] == "YES") == Counter({"okalchedy": 2}), dict(Counter(row["target_surface"] for row in paths if row["adjacent_complete_tile_sequence"] == "YES")))

    support_counts = Counter(row["support_class"] for row in bridges)
    expected_support = Counter({
        "ADJACENT_OLD_TILE_SEQUENCE": 1,
        "ORDERED_SAME_STATEMENT_TILE_SEQUENCE": 2,
        "EXACT_PORTABLE_SKELETON_CONTEXT": 16,
        "COMPLETE_TILES_AND_OLD_SEAMS_ONLY": 10,
    })
    check("support_class_distribution", support_counts == expected_support, dict(support_counts))
    check("adjacent_support_surface", [row["target_surface"] for row in bridges if row["support_class"] == "ADJACENT_OLD_TILE_SEQUENCE"] == ["okalchedy"], [row["target_surface"] for row in bridges if row["support_class"] == "ADJACENT_OLD_TILE_SEQUENCE"])
    check("ordered_support_surfaces", [row["target_surface"] for row in bridges if row["support_class"] == "ORDERED_SAME_STATEMENT_TILE_SEQUENCE"] == ["shekeey", "ykshedy"], [row["target_surface"] for row in bridges if row["support_class"] == "ORDERED_SAME_STATEMENT_TILE_SEQUENCE"])

    summary_map = {row["metric"]: row["value"] for row in summary}
    required_summary = {
        "target_surface_count": "145",
        "final_exact_recipe_count": "11",
        "final_full_tile_recipe_count": "29",
        "final_fragment_plus_atoms_count": "81",
        "final_atoms_factors_only_count": "24",
        "tier_migration_count": "4",
        "complete_old_tile_instance_count": "59",
        "unique_complete_old_tile_recipe_count": "42",
        "intertile_seam_count": "30",
        "old_supported_seam_count": "30",
        "portable_skeleton_target_count": "17",
        "portable_skeleton_mode_compatible_count": "17",
        "ordered_same_statement_target_count": "3",
        "ordered_same_statement_path_count": "13",
        "adjacent_tile_target_count": "1",
        "adjacent_tile_path_count": "2",
    }
    check("summary_required_metrics", all(summary_map.get(key) == value for key, value in required_summary.items()), {key: summary_map.get(key) for key in required_summary})

    book = BOOK.read_text(encoding="utf-8")
    check("book_status", STATUS in book, STATUS)
    check("book_bridge_inventory", all(f"`{surface}`" in book for surface in bridge_by_surface), len(bridge_by_surface))
    check("book_migrations", all(surface in book for surface in expected_migrations), sorted(expected_migrations))

    code, data = run_reader("dairykodas")
    check("reader_dairykodas", code == 0 and [row["recipe"] for row in data["tiles"]] == ["D_ADDR+AIR", "Y+K", "O+DA+S"] and len(data["seams"]) == 2, data)
    code, data = run_reader("okalchedy")
    check("reader_okalchedy", code == 0 and data["support_class"] == "ADJACENT_OLD_TILE_SEQUENCE" and data["ordered_same_statement_path_count"] == 11 and data["adjacent_tile_path_count"] == 2, data)
    code, data = run_reader("choraly")
    check("reader_choraly", code == 0 and data["support_class"] == "COMPLETE_TILES_AND_OLD_SEAMS_ONLY" and data["portable_skeleton_mode_relation"] == "NO_EXACT_PORTABLE_SKELETON", data)
    code, data = run_reader("qokees")
    check("reader_exact_tier_delegates", code == 2 and data["status"] == "NO_GDT542_FULL_TILE_BRIDGE", data)

    expected_result = {
        "status": STATUS,
        "target_surface_count": 145,
        "final_tier_counts": dict(sorted(expected_final_counts.items())),
        "original_gdt516_tier_counts_on_prose_targets": dict(sorted(expected_original_counts.items())),
        "tier_migration_count": 4,
        "tier_migrations": [
            {"surface": surface, "from": old, "to": new}
            for surface, (old, new) in expected_migrations.items()
        ],
        "full_tile_target_count": 29,
        "complete_old_tile_instance_count": 59,
        "unique_complete_old_tile_recipe_count": 42,
        "intertile_seam_count": 30,
        "old_supported_seam_count": 30,
        "portable_skeleton_target_count": 17,
        "portable_skeleton_mode_compatible_count": 17,
        "portable_skeleton_exact_mode_set_count": 15,
        "portable_skeleton_old_adds_modes_count": 2,
        "ordered_same_statement_target_count": 3,
        "ordered_same_statement_path_count": 13,
        "adjacent_tile_target_count": 1,
        "adjacent_tile_path_count": 2,
        "support_class_counts": dict(sorted(expected_support.items())),
        "new_pages": 0,
        "recipe_changes": 0,
        "root_meaning_changes": 0,
    }
    check("result_exact", result == expected_result, result)

    generated = [TIER, BRIDGE, TILE, SEAM, PATH, SKELETON, SUMMARY, BOOK, RESULT]
    before = {path.name: sha256(path) for path in generated}
    rerun = subprocess.run(
        [sys.executable, str(RUN)], cwd=ROOT, text=True, capture_output=True, check=False
    )
    after = {path.name: sha256(path) for path in generated}
    check("generator_rerun_exit", rerun.returncode == 0, rerun.stdout + rerun.stderr)
    check("generator_byte_determinism", before == after, after)

    failed = [item for item in checks if not item["passed"]]
    validation = {
        "status": "PASS" if not failed else "FAIL",
        "check_count": len(checks),
        "passed_count": len(checks) - len(failed),
        "failed_count": len(failed),
        "checks": checks,
    }
    VALIDATION.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
