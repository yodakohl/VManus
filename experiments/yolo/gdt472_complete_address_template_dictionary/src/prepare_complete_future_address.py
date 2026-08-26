#!/usr/bin/env python3
"""Prepare one ranked future-address row from the complete 107-label deck."""

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
BASE = ROOT / "experiments/yolo/gdt472_complete_address_template_dictionary"
G466 = ROOT / "experiments/yolo/gdt466_future_address_mixed_dictionary_intake"
G468 = ROOT / "experiments/yolo/gdt468_shell_recipe_carrier_support_atlas"
G469 = ROOT / "experiments/yolo/gdt469_provenance_aware_address_reader"
G470 = ROOT / "experiments/yolo/gdt470_future_address_intake_worksheet"
G471 = ROOT / "experiments/yolo/gdt471_empirical_address_shell_phrasebook"
sys.path.insert(0, str(G466 / "src"))
sys.path.insert(0, str(G469 / "src"))
sys.path.insert(0, str(G470 / "src"))
sys.path.insert(0, str(G471 / "src"))
sys.path.insert(0, str(BASE / "src"))

from intake_lib import intake, read_tsv, select_function_channels  # noqa: E402
from support_lib import supported_intake  # noqa: E402
from worksheet_lib import make_worksheet_row  # noqa: E402
from template_lib import attach_familiarity, derive_template  # noqa: E402
from complete_lib import attach_complete_metadata  # noqa: E402


CONTENT_CLASSES = (
    "STAR_BEARING_RING_POSITION",
    "DRUG_OR_INGREDIENT_OBJECT",
    "BATH_OR_OUTLET_STATION",
    "PICTURED_PLANT",
    "UNKNOWN_LOCAL_ADDRESS",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("surface")
    parser.add_argument("content_class", choices=CONTENT_CLASSES)
    parser.add_argument("--batch-id", default="FUTURE_BATCH")
    parser.add_argument("--page-slot", default="UNASSIGNED")
    parser.add_argument("--item-slot", default="UNASSIGNED")
    parser.add_argument("--page-id", default="UNRELEASED")
    parser.add_argument("--locus-id", default="UNASSIGNED")
    parser.add_argument("--owner-description", default="UNRECORDED")
    parser.add_argument("--zl3b", default="")
    parser.add_argument("--it2a", default="")
    parser.add_argument("--rf1b", default="")
    parser.add_argument("--notes", default="")
    args = parser.parse_args()

    rules = read_tsv(G466 / "artifacts/gdt466_44_function_channel_deck.tsv")
    families = read_tsv(G466 / "artifacts/gdt466_18_owner_family_channel_deck.tsv")
    labels = read_tsv(G466 / "artifacts/gdt466_107_intake_dictionary.tsv")
    recipes = read_tsv(G468 / "artifacts/gdt468_2300_recipe_support_atlas.tsv")
    shells = read_tsv(G468 / "artifacts/gdt468_2760_supported_shell_phrasebook.tsv")
    surface_templates = read_tsv(BASE / "artifacts/gdt472_87_transferable_surface_templates.tsv")
    component_templates = read_tsv(BASE / "artifacts/gdt472_85_transferable_component_templates.tsv")
    topologies = read_tsv(BASE / "artifacts/gdt472_20_transferable_topologies.tsv")
    assignments = read_tsv(BASE / "artifacts/gdt472_107_complete_template_assignments.tsv")
    packages = read_tsv(BASE / "artifacts/gdt472_2_exact_package_cards.tsv")
    reading = supported_intake(
        args.surface,
        args.content_class,
        rules,
        families,
        {row["surface"]: row for row in labels},
        {row["flattened_recipe_trace"]: row for row in recipes},
        {row["exact_channel_signature"]: row for row in shells},
        intake,
        select_function_channels,
    )
    template = derive_template(args.surface, rules, select_function_channels)
    empirical = attach_familiarity(
        reading,
        template,
        {row["surface_template"]: row for row in surface_templates},
        {row["component_template"]: row for row in component_templates},
        {row["slot_topology"]: row for row in topologies},
    )
    row = make_worksheet_row(
        reading,
        batch_id=args.batch_id,
        page_slot=args.page_slot,
        item_slot=args.item_slot,
        page_id=args.page_id,
        locus_id=args.locus_id,
        owner_description=args.owner_description,
        surface_zl3b=args.zl3b,
        surface_it2a=args.it2a,
        surface_rf1b=args.rf1b,
        notes=args.notes,
    )
    row.update(empirical)
    row.update(attach_complete_metadata(
        reading,
        empirical,
        {item["surface"]: item for item in assignments},
        {item["surface"]: item for item in packages},
    ))
    print(json.dumps(row, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
