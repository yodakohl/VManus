#!/usr/bin/env python3
"""Look up one GDT541 target surface or exact recipe profile."""

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
OUT = ROOT / "experiments/yolo/gdt541_old_prefix_exact_recipe_context_replay/artifacts"
PROFILE = OUT / "gdt541_11_recipe_context_profile_transfer.tsv"
EVENTS = OUT / "gdt541_49_old_exact_recipe_context_events.tsv"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Return the old-prefix context profile for a target surface or recipe."
    )
    parser.add_argument("key", help="target surface such as qokees or exact recipe such as OK+EE+S")
    args = parser.parse_args()
    with PROFILE.open(encoding="utf-8", newline="") as handle:
        profiles = list(csv.DictReader(handle, delimiter="\t"))
    profile = next(
        (
            row
            for row in profiles
            if row["target_surface"] == args.key or row["target_recipe"] == args.key
        ),
        None,
    )
    if profile is None:
        print(json.dumps({
            "status": "NO_OLD_EXACT_RECIPE_PROFILE",
            "key": args.key,
            "covered_target_recipe_count": len(profiles),
            "delegation": "GDT540_SURFACE_CONTRACT",
        }, ensure_ascii=False, indent=2))
        return 2
    with EVENTS.open(encoding="utf-8", newline="") as handle:
        events = [
            row
            for row in csv.DictReader(handle, delimiter="\t")
            if row["target_surface"] == profile["target_surface"]
        ]
    print(json.dumps({
        "status": "OLD_EXACT_RECIPE_CONTEXT_PROFILE",
        "target_surface": profile["target_surface"],
        "target_recipe": profile["target_recipe"],
        "target_observed_modes": profile["target_observed_modes"],
        "old_observed_modes": profile["old_observed_modes"],
        "profile_relation": profile["profile_relation"],
        "old_carrier_event_count": int(profile["old_carrier_event_count"]),
        "old_surfaces": profile["old_surfaces"],
        "old_pages": profile["old_pages"],
        "old_events": [
            {
                "event_id": row["old_global_event_id"],
                "page": row["physical_page"],
                "surface": row["old_surface"],
                "mode": row["old_requirement_mode"],
                "incoming_action": row["incoming_action_root"],
                "incoming_argument": row["incoming_argument_root"],
            }
            for row in events
        ],
        "guard": "OBSERVED_PROFILE_SET__NO_NEW_MEANING",
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
