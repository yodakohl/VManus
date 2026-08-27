#!/usr/bin/env python3
"""Read one exact GDT548 prose surface and resolve its same-statement state."""

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
    / "experiments/yolo/gdt548_unified_145_prose_reader/artifacts"
    / "gdt548_145_unified_prose_reader.tsv"
)


def roots(value: str) -> list[str]:
    return [] if value == "NONE" else value.split("|")


def load_cards() -> dict[str, dict[str, str]]:
    with READER.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    cards = {row["surface"]: row for row in rows}
    if len(rows) != 145 or len(cards) != 145:
        raise RuntimeError("GDT548 reader artifact drift")
    return cards


def resolve_context(
    card: dict[str, str], active_action: str, active_argument: str
) -> dict[str, str]:
    visible_actions = roots(card["visible_action_roots"])
    visible_arguments = roots(card["visible_argument_roots"])
    supplied_action = "" if active_action == "NONE" else active_action
    supplied_argument = "" if active_argument == "NONE" else active_argument

    if visible_actions:
        resolved_action = visible_actions[-1]
        action_source = "VISIBLE_SURFACE"
    elif supplied_action:
        resolved_action = supplied_action
        action_source = "SAME_STATEMENT_STATE"
    else:
        resolved_action = "NONE"
        action_source = "MISSING"

    if visible_arguments:
        resolved_argument = visible_arguments[-1]
        argument_source = "VISIBLE_SURFACE"
    elif supplied_argument:
        resolved_argument = supplied_argument
        argument_source = "SAME_STATEMENT_STATE"
    else:
        resolved_argument = "NONE"
        argument_source = "OBJECTLESS"

    status = (
        "READY_FOR_CONTEXTUAL_WORKING_READING"
        if resolved_action != "NONE"
        else "NEUTRAL_DEFAULT_ONLY__MISSING_ACTIVE_ACTION"
    )
    return {
        "context_status": status,
        "input_active_action": active_action,
        "input_active_argument": active_argument,
        "resolved_action_root": resolved_action,
        "action_source": action_source,
        "resolved_argument_root": resolved_argument,
        "argument_source": argument_source,
    }


def text_card(card: dict[str, str], context: dict[str, str]) -> str:
    return "\n".join(
        [
            "READ_KNOWN_145_PROSE_WORKING_CARD",
            f"Oberfläche: {card['surface']}",
            f"Stützstufe: {card['support_rank']} — {card['support_tier']}",
            f"Komponenten: {card['final_recipe']}",
            f"Defaultbedeutung: {card['neutral_component_reading_de']}",
            f"Im bekannten Kontext: {card['known_contextual_readings_de']}",
            f"Kontextmodus: {card['observed_requirement_modes']}",
            f"Aufgelöste Handlung: {context['resolved_action_root']} ({context['action_source']})",
            f"Aufgelöstes Argument: {context['resolved_argument_root']} ({context['argument_source']})",
            f"Kontextstatus: {context['context_status']}",
            f"Stützroute: {card['tier_route_class']}",
            f"Spur: {card['tier_trace']}",
            f"Evidenz: {card['tier_evidence']}",
            f"Restvorbehalt: {card['tier_caution']}",
            f"Verbesserungswarteschlange: {card['weak_queue_candidate']}",
            "Reichweite: deutsche Arbeitslesung, kein behaupteter Klartext.",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read one exact surface from the unified 145-card prose deck."
    )
    parser.add_argument("--surface", help="exact accepted surface key")
    parser.add_argument("--active-action", default="NONE")
    parser.add_argument("--active-argument", default="NONE")
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
            "status": "STOP_UNKNOWN_145_PROSE_SURFACE",
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
            print(f"STOP_UNKNOWN_145_PROSE_SURFACE: {args.surface}")
            print("Keine ähnlich geschriebene Karte wird übernommen.")
        return 2

    context = resolve_context(card, args.active_action, args.active_argument)
    if args.format == "json":
        print(
            json.dumps(
                {"card": card, "context_resolution": context},
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
        )
    elif args.format == "tsv":
        merged = {**card, **context}
        print("\t".join(merged))
        print("\t".join(merged.values()))
    else:
        print(text_card(card, context))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
