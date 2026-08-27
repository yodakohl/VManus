#!/usr/bin/env python3
"""Read one exact GDT546 fragment surface without fuzzy inheritance."""

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
READER = (
    ROOT
    / "experiments/yolo/gdt546_consolidated_fragment_reader/artifacts"
    / "gdt546_81_consolidated_fragment_reader.tsv"
)


def load_cards() -> dict[str, dict[str, str]]:
    with READER.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    cards = {row["surface"]: row for row in rows}
    if len(rows) != 81 or len(cards) != 81:
        raise RuntimeError("GDT546 reader artifact drift")
    return cards


def text_card(card: dict[str, str]) -> str:
    lines = [
        "READ_KNOWN_FRAGMENT_WORKING_CARD",
        f"Oberfläche: {card['surface']}",
        f"Komponenten: {card['final_recipe']}",
        f"Arbeitslesung: {card['neutral_component_reading_de']}",
        f"Im bekannten Kontext: {card['known_contextual_readings_de']}",
        f"Hauptzerlegung: {card['primary_structural_formula']}",
        f"Sichtbare Spur: {card['primary_visible_formula']}",
        f"Hauptstamm: {card['primary_anchor_recipe']} ~ {card['primary_visible_stem_surface']}",
        (
            "Alte Andockkanten: "
            f"{card['primary_old_supported_interfaces']}/{card['primary_interface_count']}"
        ),
        (
            "Stammkontext: "
            f"{card['primary_anchor_context_relation']} "
            f"({card['primary_anchor_context_modes']})"
        ),
    ]
    if card["secondary_bridge_present"] == "YES":
        lines.extend(
            [
                f"Zweite Herleitung: {card['secondary_structural_formula']}",
                (
                    "Zweiter sichtbarer Stamm: "
                    f"{card['secondary_visible_stem_surface']} "
                    f"({card['secondary_visible_stem_status']})"
                ),
                f"Reparierte Dimension: {card['secondary_repaired_dimension']}",
            ]
        )
    else:
        lines.append("Zweite Herleitung: NONE")
    lines.extend(
        [
            f"Status der Restlücke: {card['flag_resolution']}",
            f"Vorsicht: {card['current_caution']}",
            "Reichweite: deutsche Arbeitslesung, kein behaupteter Klartext.",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read one exact surface from the 81-card GDT546 fragment deck."
    )
    parser.add_argument("--surface", help="exact Voynich surface key")
    parser.add_argument(
        "--format",
        choices=("text", "json", "tsv"),
        default="text",
        help="output format",
    )
    parser.add_argument(
        "--list-surfaces",
        action="store_true",
        help="print the 81 exact accepted keys and exit",
    )
    args = parser.parse_args()
    cards = load_cards()

    if args.list_surfaces:
        for surface in sorted(cards, key=lambda value: int(cards[value]["target_ordinal"])):
            print(surface)
        return 0
    if not args.surface:
        parser.error("--surface is required unless --list-surfaces is used")

    card = cards.get(args.surface)
    if card is None:
        stopped = {
            "status": "STOP_UNKNOWN_FRAGMENT_SURFACE",
            "surface": args.surface,
            "known_surface_count": len(cards),
            "guard": "EXACT_SURFACE_KEY_ONLY__NO_FUZZY_INHERITANCE",
        }
        if args.format == "json":
            print(json.dumps(stopped, ensure_ascii=False, indent=2, sort_keys=True))
        elif args.format == "tsv":
            print("status\tsurface\tknown_surface_count\tguard")
            print("\t".join(str(stopped[key]) for key in stopped))
        else:
            print(f"STOP_UNKNOWN_FRAGMENT_SURFACE: {args.surface}")
            print("Keine ähnliche Karte wird automatisch geerbt.")
        return 2

    if args.format == "json":
        print(json.dumps(card, ensure_ascii=False, indent=2, sort_keys=True))
    elif args.format == "tsv":
        print("\t".join(card))
        print("\t".join(card.values()))
    else:
        print(text_card(card))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
