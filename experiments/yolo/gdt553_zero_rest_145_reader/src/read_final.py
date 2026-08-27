#!/usr/bin/env python3
"""Read one exact GDT553 card and resolve its same-statement slots."""

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
    / "experiments/yolo/gdt553_zero_rest_145_reader/artifacts"
    / "gdt553_145_zero_rest_reader.tsv"
)


def roots(value: str) -> list[str]:
    return [] if value == "NONE" else value.split("|")


def load_cards() -> dict[str, dict[str, str]]:
    with READER.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    cards = {row["surface"]: row for row in rows}
    if len(rows) != 145 or len(cards) != 145:
        raise RuntimeError("GDT553 reader artifact drift")
    return cards


def resolve_context(
    card: dict[str, str], active_action: str, active_argument: str
) -> dict[str, str]:
    visible_actions = roots(card["visible_action_roots"])
    visible_arguments = roots(card["visible_argument_roots"])
    supplied_action = "" if active_action == "NONE" else active_action
    supplied_argument = "" if active_argument == "NONE" else active_argument
    if visible_actions:
        action, action_source = visible_actions[-1], "VISIBLE_SURFACE"
    elif supplied_action:
        action, action_source = supplied_action, "SAME_STATEMENT_STATE"
    else:
        action, action_source = "NONE", "MISSING"
    if visible_arguments:
        argument, argument_source = visible_arguments[-1], "VISIBLE_SURFACE"
    elif supplied_argument:
        argument, argument_source = supplied_argument, "SAME_STATEMENT_STATE"
    else:
        argument, argument_source = "NONE", "OBJECTLESS"
    return {
        "context_status": (
            "READY_FOR_CONTEXTUAL_WORKING_READING"
            if action != "NONE"
            else "NEUTRAL_DEFAULT_ONLY__MISSING_ACTIVE_ACTION"
        ),
        "input_active_action": active_action,
        "input_active_argument": active_argument,
        "resolved_action_root": action,
        "action_source": action_source,
        "resolved_argument_root": argument,
        "argument_source": argument_source,
    }


def text_card(card: dict[str, str], context: dict[str, str]) -> str:
    return "\n".join(
        [
            "READ_KNOWN_ZERO_REST_145_WORKING_CARD",
            f"Oberfläche: {card['surface']}",
            f"Komponenten: {card['final_recipe']}",
            f"Defaultbedeutung: {card['neutral_component_reading_de']}",
            f"Im bekannten Kontext: {card['known_contextual_readings_de']}",
            f"Aufgelöste Handlung: {context['resolved_action_root']} ({context['action_source']})",
            f"Aufgelöstes Argument: {context['resolved_argument_root']} ({context['argument_source']})",
            f"Kontextstatus: {context['context_status']}",
            f"Provenienzgeneration: {card['resolution_generation']}",
            f"Stärkste Provenienz: {card['strongest_current_provenance']}",
            f"Route: {card['current_route_trace']}",
            f"Evidenz: {card['current_evidence_trace']}",
            f"Reichweitengrenze: {card['retained_scope_limit']}",
            f"Offener Stützrest: {card['support_rest_status']}",
            "Lesestatus: deutsche Arbeitslesung, kein behaupteter Klartext.",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read one exact surface from the GDT553 zero-rest deck."
    )
    parser.add_argument("--surface")
    parser.add_argument("--active-action", default="NONE")
    parser.add_argument("--active-argument", default="NONE")
    parser.add_argument("--format", choices=("text", "json", "tsv"), default="text")
    parser.add_argument("--list-surfaces", action="store_true")
    args = parser.parse_args()
    cards = load_cards()
    if args.list_surfaces:
        for surface in sorted(cards, key=lambda key: int(cards[key]["target_ordinal"])):
            print(surface)
        return 0
    if not args.surface:
        parser.error("--surface is required unless --list-surfaces is used")
    card = cards.get(args.surface)
    if card is None:
        payload = {
            "status": "STOP_UNKNOWN_ZERO_REST_145_SURFACE",
            "surface": args.surface,
            "known_surface_count": len(cards),
            "guard": "EXACT_SURFACE_KEY_ONLY__NO_FUZZY_INHERITANCE",
        }
        if args.format == "json":
            print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        elif args.format == "tsv":
            print("\t".join(payload))
            print("\t".join(str(payload[key]) for key in payload))
        else:
            print(f"STOP_UNKNOWN_ZERO_REST_145_SURFACE: {args.surface}")
            print("Keine ähnlich geschriebene Karte wird übernommen.")
        return 2
    context = resolve_context(card, args.active_action, args.active_argument)
    if args.format == "json":
        print(json.dumps({"card": card, "context_resolution": context}, ensure_ascii=False, indent=2, sort_keys=True))
    elif args.format == "tsv":
        merged = {**card, **context}
        print("\t".join(merged))
        print("\t".join(merged.values()))
    else:
        print(text_card(card, context))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
