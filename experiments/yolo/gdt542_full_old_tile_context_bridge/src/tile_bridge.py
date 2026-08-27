#!/usr/bin/env python3
"""Inspect one GDT542 full-old-tile target."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
OUT = ROOT / "experiments/yolo/gdt542_full_old_tile_context_bridge/artifacts"
BRIDGES = OUT / "gdt542_29_full_tile_context_bridges.tsv"
TILES = OUT / "gdt542_59_old_complete_tile_instances.tsv"
SEAMS = OUT / "gdt542_30_intertile_seam_support.tsv"
PATHS = OUT / "gdt542_13_ordered_same_statement_tile_paths.tsv"


def load(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Return the complete-old-card tile bridge for one target surface."
    )
    parser.add_argument("surface")
    args = parser.parse_args()
    bridge = next(
        (row for row in load(BRIDGES) if row["target_surface"] == args.surface),
        None,
    )
    if bridge is None:
        print(json.dumps({
            "status": "NO_GDT542_FULL_TILE_BRIDGE",
            "surface": args.surface,
            "delegation": "GDT541_EXACT_OR_GDT540_BASE_CONTRACT",
        }, ensure_ascii=False, indent=2))
        return 2
    tiles = [row for row in load(TILES) if row["target_surface"] == args.surface]
    seams = [row for row in load(SEAMS) if row["target_surface"] == args.surface]
    paths = [row for row in load(PATHS) if row["target_surface"] == args.surface]
    print(json.dumps({
        "status": "GDT542_FULL_OLD_TILE_CONTEXT_BRIDGE",
        "surface": bridge["target_surface"],
        "recipe": bridge["target_recipe"],
        "observed_context_modes": bridge["target_observed_modes"],
        "support_class": bridge["support_class"],
        "tiles": [
            {
                "index": int(row["tile_index_in_target"]),
                "recipe": row["tile_recipe"],
                "old_event_count": int(row["old_tile_event_count"]),
                "old_surfaces": row["old_tile_surfaces"],
            }
            for row in tiles
        ],
        "seams": [
            {
                "pair": row["boundary_pair"],
                "old_event_count": int(row["old_boundary_event_count"]),
            }
            for row in seams
        ],
        "portable_skeleton": bridge["portable_skeleton"],
        "old_portable_skeleton_event_count": int(
            bridge["old_portable_skeleton_event_count"]
        ),
        "portable_skeleton_mode_relation": bridge[
            "portable_skeleton_mode_relation"
        ],
        "ordered_same_statement_path_count": len(paths),
        "adjacent_tile_path_count": sum(
            row["adjacent_complete_tile_sequence"] == "YES" for row in paths
        ),
        "guard": "WORKING_TILE_BRIDGE__NO_WHOLE_RECIPE_OCCURRENCE_CLAIM",
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
