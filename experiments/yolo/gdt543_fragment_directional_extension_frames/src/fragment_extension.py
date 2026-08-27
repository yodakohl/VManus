#!/usr/bin/env python3
"""Read one GDT543 learned-fragment extension card."""

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
OUT = ROOT / "experiments/yolo/gdt543_fragment_directional_extension_frames/artifacts"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def lookup(surface: str) -> dict[str, object]:
    cards = {row["surface"]: row for row in read_tsv(OUT / "gdt543_81_fragment_extension_cards.tsv")}
    if surface not in cards:
        return {
            "status": "NO_GDT543_FRAGMENT_EXTENSION_CARD",
            "surface": surface,
            "delegation": "GDT542_FULL_TILE_OR_GDT541_EXACT_OR_GDT540_BASE_CONTRACT",
        }
    card = cards[surface]
    arms = [
        row
        for row in read_tsv(OUT / "gdt543_93_directional_extension_arms.tsv")
        if row["target_surface"] == surface
    ]
    return {
        "status": "GDT543_FRAGMENT_EXTENSION_CARD",
        "surface": surface,
        "recipe": card["final_recipe"],
        "observed_context_modes": card["observed_requirement_modes"],
        "anchor": {
            "recipe": card["anchor_recipe"],
            "old_event_count": int(card["old_anchor_event_count"]),
            "old_surfaces": card["old_anchor_surfaces"],
            "context_modes": card["anchor_context_modes"],
            "context_relation": card["anchor_context_relation"],
        },
        "visible_stem": {
            "status": card["visible_stem_status"],
            "surface": card["visible_stem_surface"],
            "left": card["visible_left_extension"],
            "right": card["visible_right_extension"],
        },
        "arms": [
            {
                "side": row["side"],
                "recipe": row["extension_recipe"],
                "visible_affix": row["aligned_visible_affix"],
                "interface": row["interface_pair"],
                "old_interface_event_count": int(row["old_interface_event_count"]),
                "visible_channel_class": row["visible_channel_class"],
                "visible_channel_recipe_variants": row[
                    "visible_channel_recipe_variants"
                ],
            }
            for row in arms
        ],
        "old_supercard": {
            "event_count": int(card["old_supercard_event_count"]),
            "recipes": card["old_supercard_recipes"],
            "context_relation": card["old_supercard_context_relation"],
        },
        "structural_support_class": card["structural_support_class"],
        "neutral_phrase_de": card["neutral_surface_phrase_de"],
        "contextual_reading_de": card["known_contextual_readings_de"],
        "guard": card["guard"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("surface")
    args = parser.parse_args()
    print(json.dumps(lookup(args.surface), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
