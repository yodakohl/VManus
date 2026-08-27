#!/usr/bin/env python3
"""Read one exact surface from the GDT547 24-card atomic/factor deck."""

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
    / "experiments/yolo/gdt547_atomic_factor_visible_reader/artifacts"
    / "gdt547_24_atomic_factor_reader_cards.tsv"
)


def load_cards() -> dict[str, dict[str, str]]:
    with READER.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    cards = {row["surface"]: row for row in rows}
    if len(rows) != 24 or len(cards) != 24:
        raise RuntimeError("GDT547 reader artifact drift")
    return cards


def text_card(card: dict[str, str]) -> str:
    return "\n".join(
        [
            "READ_KNOWN_ATOMIC_FACTOR_WORKING_CARD",
            f"Oberfläche: {card['surface']}",
            f"Komponenten: {card['final_recipe']}",
            f"Sichtbare Route: {card['visible_trace']}",
            f"Routenklasse: {card['visible_route_class']}",
            (
                "Alte direkte Nähte: "
                f"{card['old26_direct_interface_count']}/{card['direct_interface_count']}"
            ),
            f"Neue direkte Nähte: {card['new_direct_interfaces']}",
            f"Arbeitslesung: {card['neutral_component_reading_de']}",
            f"Im bekannten Kontext: {card['known_contextual_readings_de']}",
            f"Kontextmodus: {card['observed_requirement_modes']}",
            f"Ausführungsroute: {card['current_execution_route']}",
            f"Sichtbarer Vorbehalt: {card['visible_route_caution']}",
            f"Ausführungsvorbehalt: {card['execution_caution']}",
            "Reichweite: deutsche Arbeitslesung, kein behaupteter Klartext.",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read one exact surface from the GDT547 atomic/factor deck."
    )
    parser.add_argument("--surface", help="exact accepted surface key")
    parser.add_argument("--format", choices=("text", "json", "tsv"), default="text")
    parser.add_argument("--list-surfaces", action="store_true")
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
        payload = {
            "status": "STOP_UNKNOWN_ATOMIC_FACTOR_SURFACE",
            "surface": args.surface,
            "known_surface_count": len(cards),
            "guard": "EXACT_SURFACE_KEY_ONLY__NO_FUZZY_INHERITANCE",
        }
        if args.format == "json":
            print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        elif args.format == "tsv":
            print("status\tsurface\tknown_surface_count\tguard")
            print("\t".join(str(payload[key]) for key in payload))
        else:
            print(f"STOP_UNKNOWN_ATOMIC_FACTOR_SURFACE: {args.surface}")
            print("Keine ähnlich geschriebene Karte wird übernommen.")
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
