#!/usr/bin/env python3
"""Read one address surface and return its GDT468 recipe provenance."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt469_provenance_aware_address_reader"
G466 = ROOT / "experiments/yolo/gdt466_future_address_mixed_dictionary_intake"
G468 = ROOT / "experiments/yolo/gdt468_shell_recipe_carrier_support_atlas"
sys.path.insert(0, str(G466 / "src"))
sys.path.insert(0, str(BASE / "src"))

from intake_lib import intake, read_tsv, select_function_channels  # noqa: E402
from support_lib import supported_intake  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("surface")
    parser.add_argument(
        "content_class",
        choices=("STAR_BEARING_RING_POSITION", "DRUG_OR_INGREDIENT_OBJECT", "BATH_OR_OUTLET_STATION", "PICTURED_PLANT", "UNKNOWN_LOCAL_ADDRESS"),
    )
    args = parser.parse_args()
    rules = read_tsv(G466 / "artifacts/gdt466_44_function_channel_deck.tsv")
    families = read_tsv(G466 / "artifacts/gdt466_18_owner_family_channel_deck.tsv")
    labels = read_tsv(G466 / "artifacts/gdt466_107_intake_dictionary.tsv")
    recipes = read_tsv(G468 / "artifacts/gdt468_2300_recipe_support_atlas.tsv")
    shells = read_tsv(G468 / "artifacts/gdt468_2760_supported_shell_phrasebook.tsv")
    result = supported_intake(
        args.surface, args.content_class, rules, families, {row["surface"]: row for row in labels},
        {row["flattened_recipe_trace"]: row for row in recipes},
        {row["exact_channel_signature"]: row for row in shells}, intake, select_function_channels,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
