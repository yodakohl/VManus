#!/usr/bin/env python3
"""Compile the final zero-rest exact-key 145-card working reader."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Iterable


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt553_zero_rest_145_reader"
ART = EXP / "artifacts"
G548 = ROOT / "experiments/yolo/gdt548_unified_145_prose_reader/artifacts"
G549 = ROOT / "experiments/yolo/gdt549_default_queue_visible_peer_bridges/artifacts"
G550 = ROOT / "experiments/yolo/gdt550_recurrent_sequence_frame_bridges/artifacts"
G551 = ROOT / "experiments/yolo/gdt551_context_contract_normalization/artifacts"
G552 = ROOT / "experiments/yolo/gdt552_interface_boundary_family_bridges/artifacts"

BASE_IN = G548 / "gdt548_145_unified_prose_reader.tsv"
PEER_IN = G549 / "gdt549_4_promoted_peer_cards.tsv"
FRAME_IN = G550 / "gdt550_10_promoted_sequence_cards.tsv"
CONTEXT_IN = G551 / "gdt551_4_promoted_context_cards.tsv"
INTERFACE_IN = G552 / "gdt552_5_selected_interface_bridges.tsv"

READER_OUT = ART / "gdt553_145_zero_rest_reader.tsv"
RESOLVED_OUT = ART / "gdt553_23_resolved_queue_cards.tsv"
PROVENANCE_OUT = ART / "gdt553_5_provenance_generations.tsv"
SUMMARY_OUT = ART / "gdt553_zero_rest_summary.tsv"
BOOK_OUT = ART / "GDT553_145_ZERO_REST_READER.md"
RESULT_OUT = ART / "gdt553_result.json"

STATUS = "PASS_ZERO_REST_145_CARD_READER__23_REPAIRS_PARTITION_EXACT"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty table {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def keyed(rows: list[dict[str, str]], field: str) -> dict[str, dict[str, str]]:
    result = {row[field]: row for row in rows}
    if len(result) != len(rows):
        raise RuntimeError(f"Duplicate {field}")
    return result


def join(values: Iterable[str]) -> str:
    material = sorted({str(value) for value in values if str(value)})
    return "|".join(material) if material else "NONE"


def build_book(
    cards: list[dict[str, object]],
    generations: list[dict[str, object]],
    metrics: dict[str, object],
) -> str:
    lines = [
        "# GDT553 — 145-card zero-rest working reader",
        "",
        "## Bestand",
        "",
        "Every exact admitted prose surface now has one common card containing its "
        "unchanged recipe, context slots, neutral German working meaning, known "
        "contextual reading, current route, strongest bounded provenance and explicit "
        "scope limit. Zero rest means no named support task remains; it does not mean "
        "plaintext or license an unknown spelling.",
        "",
        "| Generation | Cards | Meaning |",
        "|---|---:|---|",
    ]
    descriptions = {
        "BASE_GDT548": "already outside the GDT548 improvement queue",
        "GDT549_CURRENT_PEER": "current exact context/interface peers",
        "GDT550_RECURRENT_FRAME": "recurrent visible frame plus same-mode peers",
        "GDT551_SLOT_CONTRACT": "instance states normalized to slot contracts",
        "GDT552_BOUNDARY_FAMILY": "target-specific boundary or family bridge",
    }
    for row in generations:
        lines.append(
            f"| `{row['resolution_generation']}` | {row['card_count']} | "
            f"{descriptions[str(row['resolution_generation'])]} |"
        )
    lines.extend(
        [
            "",
            "## Complete exact-key deck",
            "",
            "| # | Surface | Recipe | Neutral working meaning | Provenance | Rest |",
            "|---:|---|---|---|---|---|",
        ]
    )
    for row in cards:
        neutral = str(row["neutral_component_reading_de"]).replace("|", "\\|")
        lines.append(
            f"| {row['target_ordinal']} | `{row['surface']}` | `{row['final_recipe']}` | "
            f"{neutral} | `{row['resolution_generation']}` | `NONE` |"
        )
    lines.extend(
        [
            "",
            "## Reader contract",
            "",
            "The executable reader accepts only one of these 145 exact keys. It uses the "
            "unchanged visible-action/visible-argument rule and can resolve a supplied "
            "same-statement action or argument. Unknown keys stop. Every card remains a "
            "German working reading, not asserted historical plaintext.",
            "",
            f"Validation target: {metrics['reader_card_count']} cards, "
            f"{metrics['resolved_former_queue_count']} later resolutions, "
            f"{metrics['support_rest_count']} rests.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    base_rows = read_tsv(BASE_IN)
    peer = keyed(read_tsv(PEER_IN), "surface")
    frame = keyed(read_tsv(FRAME_IN), "surface")
    context = keyed(read_tsv(CONTEXT_IN), "surface")
    interface = keyed(read_tsv(INTERFACE_IN), "surface")
    if [len(base_rows), len(peer), len(frame), len(context), len(interface)] != [145, 4, 10, 4, 5]:
        raise RuntimeError("Input inventory drift")
    promotion_sets = [set(peer), set(frame), set(context), set(interface)]
    if sum(len(group) for group in promotion_sets) != len(set().union(*promotion_sets)):
        raise RuntimeError("Promotion generations overlap")
    source_queue = {row["surface"] for row in base_rows if row["weak_queue_candidate"] == "YES"}
    promoted_union = set().union(*promotion_sets)
    if len(source_queue) != 23 or source_queue != promoted_union:
        raise RuntimeError("Promotion union does not equal GDT548 queue")

    cards: list[dict[str, object]] = []
    for base in base_rows:
        surface = base["surface"]
        if surface in peer:
            item = peer[surface]
            generation = "GDT549_CURRENT_PEER"
            provenance = "CURRENT_EXACT_CONTEXT_AND_OR_INTERFACE_PEER"
            trace_scope = "EXACT_VISIBLE_ROUTE"
            route_trace = item["visible_route"]
            evidence_trace = (
                f"context={item['context_bridge']};interface={item['interface_bridge']}"
            )
            scope_limit = "CURRENT_ADMITTED_PEER_SUPPORT_ONLY__NOT_UNIVERSAL_RULE"
            resolution_source = "GDT549"
        elif surface in frame:
            item = frame[surface]
            generation = "GDT550_RECURRENT_FRAME"
            provenance = "RECURRENT_VISIBLE_FRAME_PLUS_SAME_MODE_STRONG_PEER"
            trace_scope = "EXACT_VISIBLE_ROUTE"
            route_trace = item["exact_visible_route"]
            evidence_trace = (
                f"frame={item['frame_id']}:{item['visible_frame']}→{item['recipe_frame']};"
                f"position={item['frame_position']};same_mode_peers={item['same_mode_peer_count']}"
            )
            scope_limit = item["retained_caution"]
            resolution_source = "GDT550"
        elif surface in context:
            item = context[surface]
            generation = "GDT551_SLOT_CONTRACT"
            provenance = "GDT540_SLOT_CONTRACT_NORMALIZATION"
            trace_scope = "EXACT_VISIBLE_ROUTE"
            route_trace = item["selected_visible_trace"]
            evidence_trace = (
                f"anchor={item['primary_anchor_recipe']};"
                f"contract={item['contract_relation']};"
                f"resolution={item['context_resolution']}"
            )
            scope_limit = "INSTANCE_MODE_IS_INCOMING_STATE__NO_LEXICAL_CONTEXT_SWITCH"
            resolution_source = "GDT551"
        elif surface in interface:
            item = interface[surface]
            generation = "GDT552_BOUNDARY_FAMILY"
            provenance = item["bridge_class"]
            trace_scope = "EXACT_VISIBLE_ROUTE"
            route_trace = item["selected_visible_trace"]
            evidence_trace = item["gate_trace"]
            scope_limit = (
                "OLD_DIRECT_WITHIN_CARD_PAIR_ABSENT__"
                "TARGET_SPECIFIC_BRIDGE_ONLY__NO_UNIVERSAL_PAIR_LICENSE"
            )
            resolution_source = "GDT552"
        else:
            generation = "BASE_GDT548"
            provenance = f"GDT548_{base['support_tier']}"
            trace_scope = "BASE_TIER_TRACE"
            route_trace = base["tier_trace"]
            evidence_trace = base["tier_evidence"]
            scope_limit = base["tier_caution"]
            resolution_source = base["source_reader"]

        cards.append(
            {
                "target_ordinal": base["target_ordinal"],
                "surface": surface,
                "reader_decision": "READ_KNOWN_ZERO_REST_145_WORKING_CARD",
                "support_tier": base["support_tier"],
                "support_rank": base["support_rank"],
                "support_band": base["support_band"],
                "final_recipe": base["final_recipe"],
                "target_event_count": base["target_event_count"],
                "target_physical_pages": base["target_physical_pages"],
                "observed_requirement_modes": base["observed_requirement_modes"],
                "visible_action_roots": base["visible_action_roots"],
                "visible_argument_roots": base["visible_argument_roots"],
                "future_action_contract": base["future_action_contract"],
                "future_argument_contract": base["future_argument_contract"],
                "minimum_future_state_for_verbal_clause": base[
                    "minimum_future_state_for_verbal_clause"
                ],
                "neutral_component_reading_de": base[
                    "neutral_component_reading_de"
                ],
                "known_contextual_readings_de": base[
                    "known_contextual_readings_de"
                ],
                "original_tier_route_class": base["tier_route_class"],
                "original_tier_trace": base["tier_trace"],
                "original_tier_evidence": base["tier_evidence"],
                "original_tier_context_relation": base["tier_context_relation"],
                "original_tier_caution": base["tier_caution"],
                "former_queue_candidate": base["weak_queue_candidate"],
                "former_queue_reason": base["weak_queue_reason"],
                "resolution_generation": generation,
                "resolution_source": resolution_source,
                "strongest_current_provenance": provenance,
                "current_route_trace_scope": trace_scope,
                "current_route_trace": route_trace,
                "current_evidence_trace": evidence_trace,
                "retained_scope_limit": scope_limit,
                "support_rest_status": "NONE__BOUNDED_WORKING_ROUTE_DOCUMENTED",
                "reading_scope": "GERMAN_WORKING_READING__NOT_PLAINTEXT",
                "guard": "EXACT_145_SURFACE_KEY_ONLY__NO_FUZZY_INHERITANCE_OR_NEW_MEANING",
            }
        )

    generation_counts = Counter(row["resolution_generation"] for row in cards)
    tier_counts = Counter(row["support_tier"] for row in cards)
    expected_generations = {
        "BASE_GDT548": 122,
        "GDT549_CURRENT_PEER": 4,
        "GDT550_RECURRENT_FRAME": 10,
        "GDT551_SLOT_CONTRACT": 4,
        "GDT552_BOUNDARY_FAMILY": 5,
    }
    if dict(generation_counts) != expected_generations:
        raise RuntimeError(f"Generation count drift: {generation_counts}")

    generation_order = list(expected_generations)
    provenance_rows: list[dict[str, object]] = []
    for ordinal, generation in enumerate(generation_order, 1):
        material = [row for row in cards if row["resolution_generation"] == generation]
        provenance_rows.append(
            {
                "generation_ordinal": ordinal,
                "resolution_generation": generation,
                "card_count": len(material),
                "surface_count": len({row["surface"] for row in material}),
                "complete_neutral_meaning_count": sum(bool(row["neutral_component_reading_de"]) for row in material),
                "complete_context_meaning_count": sum(bool(row["known_contextual_readings_de"]) for row in material),
                "support_rest_count": sum(not str(row["support_rest_status"]).startswith("NONE") for row in material),
                "surfaces": join(str(row["surface"]) for row in material),
                "guard": "PROVENANCE_GENERATION_IS_SUPPORT_HISTORY__NOT_SEMANTIC_CLASS",
            }
        )

    resolved_rows = [row for row in cards if row["former_queue_candidate"] == "YES"]
    metrics: dict[str, object] = {
        "status": STATUS,
        "reader_card_count": len(cards),
        "exact_surface_key_count": len({row["surface"] for row in cards}),
        "base_outside_queue_count": generation_counts["BASE_GDT548"],
        "gdt549_peer_resolution_count": generation_counts["GDT549_CURRENT_PEER"],
        "gdt550_frame_resolution_count": generation_counts["GDT550_RECURRENT_FRAME"],
        "gdt551_contract_resolution_count": generation_counts["GDT551_SLOT_CONTRACT"],
        "gdt552_boundary_resolution_count": generation_counts["GDT552_BOUNDARY_FAMILY"],
        "resolved_former_queue_count": len(resolved_rows),
        "resolution_generation_count": len(generation_counts),
        "full_recipe_tier_count": tier_counts["FULL_COMPLETE_RECIPE_CARRIER"] + tier_counts["FULL_OLD_RECIPE_CARRIER"],
        "fully_tiled_tier_count": tier_counts["FULLY_TILED_BY_OLD_MULTICOMPONENT_RECIPES"],
        "fragment_tier_count": tier_counts["OLD_COMPLETE_RECIPE_FRAGMENT_PLUS_ATOMS"],
        "atomic_tier_count": tier_counts["ATOMS_AND_FACTORS_ONLY"],
        "complete_neutral_meaning_count": sum(bool(row["neutral_component_reading_de"]) for row in cards),
        "complete_context_meaning_count": sum(bool(row["known_contextual_readings_de"]) for row in cards),
        "support_rest_count": sum(not str(row["support_rest_status"]).startswith("NONE") for row in cards),
        "new_pages": 0,
        "recipe_changes": 0,
        "root_meaning_changes": 0,
    }
    # The GDT548 tier spelling is fixed at FULL_OLD_RECIPE_CARRIER.
    metrics["full_recipe_tier_count"] = tier_counts["FULL_OLD_RECIPE_CARRIER"]

    write_tsv(READER_OUT, cards)
    write_tsv(RESOLVED_OUT, resolved_rows)
    write_tsv(PROVENANCE_OUT, provenance_rows)
    write_tsv(
        SUMMARY_OUT,
        [
            {"metric": key, "value": str(value), "guard": "GDT553_REPLAYED_METRIC"}
            for key, value in metrics.items()
        ],
    )
    BOOK_OUT.write_text(build_book(cards, provenance_rows, metrics), encoding="utf-8")
    RESULT_OUT.write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
