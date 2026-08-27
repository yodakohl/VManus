#!/usr/bin/env python3
"""Compile the four GDT542 support tiers into one exact 145-surface reader."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt548_unified_145_prose_reader"
ART = EXP / "artifacts"

CONTEXT = (
    ROOT
    / "experiments/yolo/gdt540_target_surface_context_requirement_contract/artifacts"
    / "gdt540_145_surface_context_contract.tsv"
)
EXACT = (
    ROOT
    / "experiments/yolo/gdt541_old_prefix_exact_recipe_context_replay/artifacts"
    / "gdt541_11_recipe_context_profile_transfer.tsv"
)
TIERS = (
    ROOT
    / "experiments/yolo/gdt542_full_old_tile_context_bridge/artifacts"
    / "gdt542_145_final_support_tiers.tsv"
)
TILES = (
    ROOT
    / "experiments/yolo/gdt542_full_old_tile_context_bridge/artifacts"
    / "gdt542_29_full_tile_context_bridges.tsv"
)
FRAGMENTS = (
    ROOT
    / "experiments/yolo/gdt546_consolidated_fragment_reader/artifacts"
    / "gdt546_81_consolidated_fragment_reader.tsv"
)
ATOMS = (
    ROOT
    / "experiments/yolo/gdt547_atomic_factor_visible_reader/artifacts"
    / "gdt547_24_atomic_factor_reader_cards.tsv"
)

TIER_RANK = {
    "FULL_OLD_RECIPE_CARRIER": "1",
    "FULLY_TILED_BY_OLD_MULTICOMPONENT_RECIPES": "2",
    "OLD_COMPLETE_RECIPE_FRAGMENT_PLUS_ATOMS": "3",
    "ATOMS_AND_FACTORS_ONLY": "4",
}

READER_FIELDS = [
    "target_ordinal",
    "surface",
    "reader_decision",
    "support_tier",
    "support_rank",
    "support_band",
    "final_recipe",
    "target_event_count",
    "target_physical_pages",
    "observed_requirement_modes",
    "visible_action_roots",
    "visible_argument_roots",
    "future_action_contract",
    "future_argument_contract",
    "minimum_future_state_for_verbal_clause",
    "neutral_component_reading_de",
    "known_contextual_readings_de",
    "tier_route_class",
    "tier_trace",
    "tier_evidence",
    "tier_context_relation",
    "tier_caution",
    "weak_queue_candidate",
    "weak_queue_reason",
    "source_reader",
    "reading_scope",
    "guard",
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def keyed(rows: list[dict[str, str]], field: str) -> dict[str, dict[str, str]]:
    result = {row[field]: row for row in rows}
    if len(result) != len(rows):
        raise RuntimeError(f"duplicate {field} in source")
    return result


def clean_parts(*values: str) -> str:
    return " | ".join(value for value in values if value and value != "NONE") or "NONE"


def exact_support(row: dict[str, str]) -> dict[str, str]:
    return {
        "support_band": "STRONG_EXACT_OLD_RECIPE",
        "tier_route_class": row["replication_kind"],
        "tier_trace": (
            f"OLD_COMPLETE_RECIPE[{row['target_recipe']}] | "
            f"OLD_SURFACES[{row['old_surfaces']}]"
        ),
        "tier_evidence": (
            f"old_events={row['old_carrier_event_count']};"
            f"old_surfaces={row['old_surface_count']};"
            f"old_pages={row['old_page_count']};"
            f"old_statements={row['old_statement_count']}"
        ),
        "tier_context_relation": row["profile_relation"],
        "tier_caution": "NONE__COMPLETE_OLD_RECIPE_AND_CONTEXT_PROFILE",
        "weak_queue_candidate": "NO",
        "weak_queue_reason": "NONE",
        "source_reader": "GDT541_EXACT_RECIPE_PROFILE",
    }


def tile_support(row: dict[str, str]) -> dict[str, str]:
    weak = row["support_class"] == "COMPLETE_TILES_AND_OLD_SEAMS_ONLY"
    caution = (
        "NO_COMPLETE_OLD_PORTABLE_SKELETON_OR_ORDERED_STATEMENT_PATH"
        if weak
        else "NONE__OLD_CONTEXT_OR_ORDERED_TILE_BRIDGE"
    )
    return {
        "support_band": (
            "WORKING_DEFAULT_COMPLETE_OLD_TILES" if weak else "SUPPORTED_TILE_BRIDGE"
        ),
        "tier_route_class": row["support_class"],
        "tier_trace": f"OLD_TILES[{row['complete_old_tiles']}]",
        "tier_evidence": (
            f"tiles={row['tile_count']};"
            f"minimum_tile_events={row['minimum_old_tile_event_count']};"
            f"old_seams={row['seam_count']}/{row['seam_count']};"
            f"old_skeleton_events={row['old_portable_skeleton_event_count']};"
            f"ordered_statement_paths={row['ordered_same_statement_path_count']};"
            f"adjacent_paths={row['adjacent_tile_path_count']}"
        ),
        "tier_context_relation": row["portable_skeleton_mode_relation"],
        "tier_caution": caution,
        "weak_queue_candidate": "YES" if weak else "NO",
        "weak_queue_reason": (
            "COMPLETE_OLD_TILES_AND_SEAMS_ONLY" if weak else "NONE"
        ),
        "source_reader": "GDT542_FULL_TILE_BRIDGE",
    }


def fragment_support(row: dict[str, str]) -> dict[str, str]:
    weak = row["flag_resolution"].startswith("EXPLICIT_WORKING_DEFAULT")
    secondary = (
        f" | SECONDARY[{row['secondary_structural_formula']}]"
        if row["secondary_bridge_present"] == "YES"
        else ""
    )
    return {
        "support_band": (
            "WORKING_DEFAULT_FRAGMENT" if weak else "SUPPORTED_FRAGMENT_FRAME"
        ),
        "tier_route_class": row["primary_structural_support_class"],
        "tier_trace": f"PRIMARY[{row['primary_visible_formula']}]{secondary}",
        "tier_evidence": (
            f"anchor={row['primary_anchor_recipe']};"
            f"anchor_old_events={row['primary_anchor_old_event_count']};"
            f"old_interfaces={row['primary_old_supported_interfaces']}/"
            f"{row['primary_interface_count']};"
            f"recurrent_channels={row['primary_repeated_invariant_channel_count']};"
            f"secondary={row['secondary_bridge_present']}"
        ),
        "tier_context_relation": row["primary_anchor_context_relation"],
        "tier_caution": clean_parts(row["current_caution"], row["flag_resolution"]),
        "weak_queue_candidate": "YES" if weak else "NO",
        "weak_queue_reason": row["current_caution"] if weak else "NONE",
        "source_reader": "GDT546_FRAGMENT_READER",
    }


def atom_support(row: dict[str, str]) -> dict[str, str]:
    if row["surface"] == "shso":
        band = "WORKING_DEFAULT_NEW_ACTION_PAIR"
        weak = True
        weak_reason = "RAW_NEW_DIRECT_ACTION_PAIR_SH>S"
    elif row["gdt446_factor_status_in_observed_context"] == "READ_AMBER":
        band = "SUPPORTED_AMBER_LOCAL_PAIR"
        weak = False
        weak_reason = "NONE"
    elif not row["visible_route_class"].startswith("OLD26_"):
        band = "BOUNDED_SPECIAL_VISIBLE_ROUTE"
        weak = False
        weak_reason = "NONE"
    else:
        band = "SUPPORTED_VISIBLE_ATOMS"
        weak = False
        weak_reason = "NONE"
    return {
        "support_band": band,
        "tier_route_class": row["visible_route_class"],
        "tier_trace": row["visible_trace"],
        "tier_evidence": (
            f"old_cover_paths={row['old26_exact_cover_path_count']};"
            f"old_interfaces={row['old26_direct_interface_count']}/"
            f"{row['direct_interface_count']};"
            f"execution={row['current_execution_route']}"
        ),
        "tier_context_relation": "GDT540_OBSERVED_REQUIREMENT_MODE",
        "tier_caution": clean_parts(
            row["visible_route_caution"], row["execution_caution"]
        ),
        "weak_queue_candidate": "YES" if weak else "NO",
        "weak_queue_reason": weak_reason,
        "source_reader": "GDT547_ATOMIC_FACTOR_READER",
    }


def write_tsv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def build_book(rows: list[dict[str, str]], metrics: dict[str, int | str]) -> str:
    lines = [
        "# GDT548 — ein Reader für alle 145 Prosaoberflächen",
        "",
        f"Status: `{metrics['status']}`",
        "",
        "Jede bekannte Oberfläche hat genau eine vollständige Arbeitskarte. Die vier",
        "Stützstufen bleiben getrennt; die neutrale Bedeutung und die bekannte",
        "Kontextlesung stammen unverändert aus GDT540.",
        "",
        "## Staffel",
        "",
        "| Rang | Stufe | Karten |",
        "|---:|---|---:|",
    ]
    for tier, rank in sorted(TIER_RANK.items(), key=lambda item: int(item[1])):
        lines.append(f"| {rank} | `{tier}` | {metrics['tier_' + rank + '_count']} |")
    lines.extend(
        [
            "",
            f"Explizite Verbesserungswarteschlange: **{metrics['weak_queue_count']}** Karten;",
            "alle übrigen Karten behalten ebenfalls ihre konkrete Vorsichtsspur.",
        ]
    )
    for tier, rank in sorted(TIER_RANK.items(), key=lambda item: int(item[1])):
        lines.extend(["", f"## Rang {rank}: `{tier}`", ""])
        for row in rows:
            if row["support_tier"] != tier:
                continue
            lines.extend(
                [
                    f"### `{row['surface']}`",
                    "",
                    f"- Komponenten: `{row['final_recipe']}`",
                    f"- Default: {row['neutral_component_reading_de']}",
                    f"- Bekannter Kontext: {row['known_contextual_readings_de']}",
                    f"- Stützroute: `{row['tier_route_class']}`",
                    f"- Spur: `{row['tier_trace']}`",
                    f"- Kontextmodus: `{row['observed_requirement_modes']}`",
                    f"- Restvorbehalt: `{row['tier_caution']}`",
                ]
            )
    lines.extend(
        [
            "",
            "Unbekannte Oberflächen erben keine ähnlich geschriebene Karte. Sämtliche",
            "deutschen Zeilen sind Arbeitslesungen, kein behaupteter Klartext.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    context_rows = read_tsv(CONTEXT)
    tier_rows = read_tsv(TIERS)
    contexts = keyed(context_rows, "surface")
    tiers = keyed(tier_rows, "surface")
    exacts = keyed(read_tsv(EXACT), "target_surface")
    tiles = keyed(read_tsv(TILES), "target_surface")
    fragments = keyed(read_tsv(FRAGMENTS), "surface")
    atoms = keyed(read_tsv(ATOMS), "surface")

    if len(contexts) != 145 or set(contexts) != set(tiers):
        raise RuntimeError("GDT540/GDT542 145-surface inventory drift")

    cards: list[dict[str, str]] = []
    for context in sorted(context_rows, key=lambda row: int(row["surface_ordinal"])):
        surface = context["surface"]
        tier_row = tiers[surface]
        tier = tier_row["final_support_tier"]
        if context["final_recipe"] != tier_row["final_recipe"]:
            raise RuntimeError(f"recipe drift for {surface}")
        if tier == "FULL_OLD_RECIPE_CARRIER":
            support = exact_support(exacts[surface])
        elif tier == "FULLY_TILED_BY_OLD_MULTICOMPONENT_RECIPES":
            support = tile_support(tiles[surface])
        elif tier == "OLD_COMPLETE_RECIPE_FRAGMENT_PLUS_ATOMS":
            support = fragment_support(fragments[surface])
        elif tier == "ATOMS_AND_FACTORS_ONLY":
            support = atom_support(atoms[surface])
        else:
            raise RuntimeError(f"unknown support tier {tier}")

        card = {
            "target_ordinal": context["surface_ordinal"],
            "surface": surface,
            "reader_decision": "READ_KNOWN_145_PROSE_WORKING_CARD",
            "support_tier": tier,
            "support_rank": TIER_RANK[tier],
            "final_recipe": context["final_recipe"],
            "target_event_count": context["event_count"],
            "target_physical_pages": context["physical_pages"],
            "observed_requirement_modes": context["observed_requirement_modes"],
            "visible_action_roots": context["visible_action_roots"],
            "visible_argument_roots": context["visible_argument_roots"],
            "future_action_contract": context["future_action_contract"],
            "future_argument_contract": context["future_argument_contract"],
            "minimum_future_state_for_verbal_clause": context[
                "minimum_future_state_for_verbal_clause"
            ],
            "neutral_component_reading_de": context["neutral_surface_phrase_de"],
            "known_contextual_readings_de": context["known_contextual_readings_de"],
            "reading_scope": "GERMAN_WORKING_READING__NOT_PLAINTEXT",
            "guard": "EXACT_145_SURFACE_KEY_ONLY__NO_FUZZY_INHERITANCE_OR_NEW_MEANING",
            **support,
        }
        if set(card) != set(READER_FIELDS):
            raise RuntimeError(f"reader schema drift for {surface}")
        cards.append(card)

    tier_counts = Counter(row["support_tier"] for row in cards)
    weak_cards = [row for row in cards if row["weak_queue_candidate"] == "YES"]
    mode_counts = Counter(row["observed_requirement_modes"] for row in cards)
    metrics: dict[str, int | str] = {
        "status": "PASS_ONE_EXACT_KEY_READER_FOR_145_PROSE_SURFACES__23_NAMED_DEFAULTS",
        "target_surface_count": len(cards),
        "unique_surface_count": len({row["surface"] for row in cards}),
        "tier_1_count": tier_counts["FULL_OLD_RECIPE_CARRIER"],
        "tier_2_count": tier_counts["FULLY_TILED_BY_OLD_MULTICOMPONENT_RECIPES"],
        "tier_3_count": tier_counts["OLD_COMPLETE_RECIPE_FRAGMENT_PLUS_ATOMS"],
        "tier_4_count": tier_counts["ATOMS_AND_FACTORS_ONLY"],
        "exact_old_recipe_count": len(exacts),
        "full_tile_count": len(tiles),
        "fragment_reader_count": len(fragments),
        "atomic_factor_reader_count": len(atoms),
        "complete_neutral_reading_count": sum(
            bool(row["neutral_component_reading_de"]) for row in cards
        ),
        "complete_context_reading_count": sum(
            bool(row["known_contextual_readings_de"]) for row in cards
        ),
        "weak_queue_count": len(weak_cards),
        "weak_tile_default_count": sum(
            row["weak_queue_reason"] == "COMPLETE_OLD_TILES_AND_SEAMS_ONLY"
            for row in weak_cards
        ),
        "weak_fragment_default_count": sum(
            row["support_band"] == "WORKING_DEFAULT_FRAGMENT" for row in weak_cards
        ),
        "weak_atomic_pair_default_count": sum(
            row["support_band"] == "WORKING_DEFAULT_NEW_ACTION_PAIR"
            for row in weak_cards
        ),
        "nonweak_card_count": sum(row["weak_queue_candidate"] == "NO" for row in cards),
        "self_contained_only_surface_count": mode_counts["SELF_CONTAINED"],
        "active_action_surface_count": mode_counts["REQUIRES_ACTIVE_ACTION"],
        "active_argument_surface_count": mode_counts["REQUIRES_ACTIVE_ARGUMENT"],
        "active_action_and_argument_surface_count": mode_counts[
            "REQUIRES_ACTIVE_ACTION_AND_ARGUMENT"
        ],
        "multi_mode_surface_count": sum(
            "|" in row["observed_requirement_modes"] for row in cards
        ),
        "unknown_surface_policy": "STOP_UNKNOWN_145_PROSE_SURFACE",
        "new_pages": 0,
        "recipe_changes": 0,
        "root_meaning_changes": 0,
    }

    reader_path = ART / "gdt548_145_unified_prose_reader.tsv"
    weak_path = ART / "gdt548_23_named_default_queue.tsv"
    summary_path = ART / "gdt548_unified_reader_summary.tsv"
    book_path = ART / "GDT548_145_UNIFIED_PROSE_READER.md"
    result_path = ART / "gdt548_result.json"

    write_tsv(reader_path, cards, READER_FIELDS)
    write_tsv(
        weak_path,
        [
            {
                "queue_ordinal": str(index),
                "surface": row["surface"],
                "support_tier": row["support_tier"],
                "support_band": row["support_band"],
                "final_recipe": row["final_recipe"],
                "weak_queue_reason": row["weak_queue_reason"],
                "tier_trace": row["tier_trace"],
                "tier_caution": row["tier_caution"],
                "neutral_component_reading_de": row["neutral_component_reading_de"],
                "known_contextual_readings_de": row["known_contextual_readings_de"],
                "guard": "QUEUE_PRIORITIZATION_ONLY__CURRENT_READING_RETAINED",
            }
            for index, row in enumerate(weak_cards, 1)
        ],
        [
            "queue_ordinal",
            "surface",
            "support_tier",
            "support_band",
            "final_recipe",
            "weak_queue_reason",
            "tier_trace",
            "tier_caution",
            "neutral_component_reading_de",
            "known_contextual_readings_de",
            "guard",
        ],
    )
    write_tsv(
        summary_path,
        [
            {"metric": key, "value": str(value), "guard": "GDT548_REPLAYED_METRIC"}
            for key, value in metrics.items()
        ],
        ["metric", "value", "guard"],
    )
    book_path.write_text(build_book(cards, metrics), encoding="utf-8")
    result_path.write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
