#!/usr/bin/env python3
"""Unify eleven pair targets into one evidence-strength working deck."""

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
BASE = ROOT / "experiments/yolo/gdt509_eleven_pair_target_evidence_strength_deck"
ART = BASE / "artifacts"
G413 = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts"
G506 = ROOT / "experiments/yolo/gdt506_target_pair_frame_compatibility_rank/artifacts"
G507 = ROOT / "experiments/yolo/gdt507_contextual_pair_argument_bridge_atlas/artifacts"
G508 = ROOT / "experiments/yolo/gdt508_source_chch_repeated_package_bridge/artifacts"

DICTIONARY_IN = G413 / "gdt413_46_component_working_dictionary.tsv"
TARGETS_IN = G506 / "gdt506_11_target_frame_compatibility_cards.tsv"
CONTEXT_IN = G507 / "gdt507_4_target_context_bridge_cards.tsv"
PACKAGE_IN = G508 / "gdt508_1_source_chch_local_bridge_card.tsv"

DECK_OUT = ART / "gdt509_11_pair_target_evidence_strength_cards.tsv"
ROUTES_OUT = ART / "gdt509_4_evidence_route_summary.tsv"
HANDGRIPS_OUT = ART / "gdt509_5_handgrip_target_coverage.tsv"
READABLE_OUT = ART / "GDT509_ELEVEN_PAIR_WORKING_TRANSLATION_DECK.md"
RESULT_OUT = ART / "gdt509_result.json"

ROUTE_ORDER = {
    "A_LOCAL_FRAME_REDUCTION": 1,
    "B_CROSS_REGISTER_FRAME_REDUCTION": 2,
    "C_LOCAL_CONTEXT_BRIDGE": 3,
    "D_LOCAL_REPEATED_PACKAGE_PROJECTION": 4,
}
STATUS = "ELEVEN_PAIR_TARGETS_UNIFIED_IN_FOUR_EVIDENCE_ROUTES__ALL_DEFAULTS_RETAINED"
GUARD = "EVIDENCE_STRENGTH_CONSOLIDATION_ONLY__ALL_TARGET_RECIPES_REMAIN_UNOBSERVED"


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames is None:
            raise ValueError(f"missing header: {path}")
        return list(reader.fieldnames), list(reader)


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty table: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    _dictionary_fields, dictionary = read_tsv(DICTIONARY_IN)
    _target_fields, targets = read_tsv(TARGETS_IN)
    _context_fields, contexts = read_tsv(CONTEXT_IN)
    _package_fields, package_rows = read_tsv(PACKAGE_IN)
    if (len(dictionary), len(targets), len(contexts), len(package_rows)) != (46, 11, 4, 1):
        raise ValueError("GDT413/GDT506/GDT507/GDT508 source drift")

    values = {row["atom"]: row["working_value_de"] for row in dictionary}
    context_by_g506 = {row["source_gdt506_target_frame_card_id"]: row for row in contexts}
    package = package_rows[0]
    if package["target_matrix_cell_id"] != "G498-M456":
        raise ValueError("GDT508 package target drift")

    provisional: list[dict[str, object]] = []
    for target in targets:
        old_tier = target["compatibility_tier"]
        if old_tier == "A_LOCAL_ARGUMENT_COMPATIBLE_REDUCTION":
            route = "A_LOCAL_FRAME_REDUCTION"
            locality = "LOCAL_TARGET_REGISTER"
            mechanism = "ARGUMENT_COMPATIBLE_ORDERED_FRAME_REDUCTION"
            evidence_ids = target["selected_source_event_id"]
            support_de = "Ein alter Träger im Zielregister reduziert geordnet auf den Zielrahmen und behält denselben Argumentmodus."
            residual_de = "Das nackte Zielrezept selbst ist nicht beobachtet."
        elif old_tier == "B_CROSS_REGISTER_ARGUMENT_COMPATIBLE_REDUCTION":
            route = "B_CROSS_REGISTER_FRAME_REDUCTION"
            locality = "CROSS_REGISTER"
            mechanism = "ARGUMENT_COMPATIBLE_ORDERED_FRAME_REDUCTION"
            evidence_ids = target["selected_source_event_id"]
            support_de = "Ein alter Träger in einem anderen Register reduziert geordnet auf den Zielrahmen und behält denselben Argumentmodus."
            residual_de = "Der vollständige Rahmenmechanismus ist im Zielregister noch nicht alt belegt."
        else:
            context = context_by_g506[target["target_frame_card_id"]]
            if target["target_matrix_cell_id"] == package["target_matrix_cell_id"]:
                route = "D_LOCAL_REPEATED_PACKAGE_PROJECTION"
                locality = "LOCAL_SOURCE_PACKAGE_LEVEL"
                mechanism = "REPEATED_PACKAGE_CANCELLATION_PLUS_CROSS_REGISTER_PAIR_ORDER"
                evidence_ids = f"{context['selected_pair_order_event_id']}|{package['selected_exact_duplicate_event_ids']}|{package['corroborating_event_ids']}"
                support_de = "Die Paarordnung ist alt; im Source-Register wiederholt ein exaktes CH-tragendes Paket denselben geerbten Wert, und je ein CH-Slot bleibt erhalten."
                residual_de = "Die lokale Brücke liegt auf Paketprojektionsebene, nicht als nacktes CH+CH-Ereignis."
            else:
                route = "C_LOCAL_CONTEXT_BRIDGE"
                locality = "LOCAL_TARGET_REGISTER"
                mechanism = "PAIR_ORDER_PLUS_LOCAL_SAME_ARGUMENT_CONTEXT_CHAIN"
                evidence_ids = f"{context['selected_pair_order_event_id']}|{context['selected_context_left_event_id']}→{context['selected_context_right_event_id']}"
                support_de = "Die Paarordnung ist alt; im Zielregister trägt eine konkrete gleiche-Argument-Folge die fehlende Kontextmechanik."
                residual_de = "Paarordnung und Kontextmechanik können auf verschiedene alte Karten verteilt sein."

        recipe_atoms = target["target_action_recipe"].split("+")
        provisional.append({
            "source_gdt506_target_frame_card_id": target["target_frame_card_id"],
            "target_matrix_cell_id": target["target_matrix_cell_id"],
            "target_register": target["target_register"],
            "target_action_recipe": target["target_action_recipe"],
            "ordered_action_pair": target["ordered_action_pair"],
            "literal_component_trace_de": " · ".join(values[atom] for atom in recipe_atoms),
            "carrier_neutral_handgrip_de": target["carrier_neutral_handgrip_de"],
            "working_translation_de": target["target_current_default_phrase_de"],
            "target_argument_policy": target["target_argument_policy"],
            "target_argument_roots": target["target_argument_roots"],
            "evidence_route": route,
            "evidence_route_rank": ROUTE_ORDER[route],
            "support_locality": locality,
            "support_mechanism": mechanism,
            "source_evidence_ids": evidence_ids,
            "support_reading_de": support_de,
            "residual_weakness_de": residual_de,
            "old_gdt506_compatibility_tier": old_tier,
            "old_pair_carrier_event_count": target["old_pair_carrier_event_count"],
            "old_ordered_reduction_candidate_count": target["ordered_reduction_candidate_count"],
            "old_argument_compatible_candidate_count": target["argument_compatible_candidate_count"],
            "default_decision": "KEEP_CURRENT_WORKING_TRANSLATION",
            "translation_status": "EXPLORATORY_COMPOSED_DEFAULT__TARGET_UNOBSERVED",
            "target_evidence_status_retained": target["target_evidence_status_retained"],
            "target_phrase_changed": "NO",
            "working_root_meaning_changed": "NO",
            "surface_prediction_made": "NO",
            "occurrence_prediction_made": "NO",
            "guard": GUARD,
            "old_gdt506_priority_rank": target["compatibility_priority_rank"],
        })

    provisional.sort(key=lambda row: (int(row["evidence_route_rank"]), int(row["old_gdt506_priority_rank"]), str(row["target_matrix_cell_id"])))
    deck: list[dict[str, object]] = []
    for index, row in enumerate(provisional, start=1):
        deck.append({"evidence_strength_card_id": f"G509-C{index:02d}", **row})

    route_rows: list[dict[str, object]] = []
    for route in ROUTE_ORDER:
        group = [row for row in deck if row["evidence_route"] == route]
        route_rows.append({
            "evidence_route": route,
            "evidence_route_rank": ROUTE_ORDER[route],
            "target_card_count": len(group),
            "target_registers": "|".join(sorted({str(row["target_register"]) for row in group})),
            "ordered_action_pairs": "|".join(sorted({str(row["ordered_action_pair"]) for row in group})),
            "local_target_card_count": sum(row["support_locality"] != "CROSS_REGISTER" for row in group),
            "cross_register_target_card_count": sum(row["support_locality"] == "CROSS_REGISTER" for row in group),
            "all_defaults_retained": "YES" if all(row["target_phrase_changed"] == "NO" for row in group) else "NO",
            "route_ceiling_de": str(group[0]["residual_weakness_de"]),
            "guard": GUARD,
        })

    handgrip_rows: list[dict[str, object]] = []
    for pair in ("P+CH", "S+CHD", "CH+P", "CH+CH", "CH+SH"):
        group = [row for row in deck if row["ordered_action_pair"] == pair]
        handgrip_rows.append({
            "ordered_action_pair": pair,
            "carrier_neutral_handgrip_de": group[0]["carrier_neutral_handgrip_de"],
            "target_card_count": len(group),
            "target_registers": "|".join(sorted({str(row["target_register"]) for row in group})),
            "evidence_routes": "|".join(sorted({str(row["evidence_route"]) for row in group}, key=lambda route: ROUTE_ORDER[route])),
            "working_translations": " || ".join(str(row["working_translation_de"]) for row in group),
            "all_target_recipes_unobserved": "YES",
            "all_defaults_retained": "YES",
            "guard": GUARD,
        })

    write_tsv(DECK_OUT, deck)
    write_tsv(ROUTES_OUT, route_rows)
    write_tsv(HANDGRIPS_OUT, handgrip_rows)

    readable = [
        "# GDT509 — Elf Paarziele, vier klar getrennte Beweiswege",
        "",
        f"Status: `{STATUS}`",
        "",
        "Alle elf Arbeitsübersetzungen bleiben stehen. Die Karten sind nicht gleich stark und werden deshalb nach Mechanismus statt nach einem künstlichen Gesamtscore sortiert.",
        "",
    ]
    route_titles = {
        "A_LOCAL_FRAME_REDUCTION": "A · lokaler Rahmenabbau",
        "B_CROSS_REGISTER_FRAME_REDUCTION": "B · registerübergreifender Rahmenabbau",
        "C_LOCAL_CONTEXT_BRIDGE": "C · lokale Kontextfolge",
        "D_LOCAL_REPEATED_PACKAGE_PROJECTION": "D · lokale Paketwiederholung",
    }
    for route in ROUTE_ORDER:
        readable.extend([f"## {route_titles[route]}", ""])
        for row in [card for card in deck if card["evidence_route"] == route]:
            readable.extend([
                f"### `{row['target_matrix_cell_id']}` · {row['target_register']} · `{row['target_action_recipe']}`",
                "",
                f"**Arbeitsübersetzung:** {row['working_translation_de']}",
                "",
                f"Komponenten: `{row['literal_component_trace_de']}`",
                "",
                f"Brücke: {row['support_reading_de']}",
                "",
                f"Rest: {row['residual_weakness_de']}",
                "",
            ])
    readable.extend([
        "## Gemeinsame Grenze",
        "",
        "Keine der elf Zielkarten ist als nacktes Rezept beobachtet. Die Ausgabe bewahrt daher `COMPOSED_WORKING`, nennt keine neue Wurzelbedeutung und macht keine Oberflächen- oder Vorkunftsvorhersage.",
    ])
    READABLE_OUT.write_text("\n".join(readable) + "\n", encoding="utf-8")

    route_counts = Counter(str(row["evidence_route"]) for row in deck)
    result = {
        "status": STATUS,
        "pair_target_cards": len(deck),
        "evidence_routes": len(route_rows),
        "local_frame_reduction_cards": route_counts["A_LOCAL_FRAME_REDUCTION"],
        "cross_register_frame_reduction_cards": route_counts["B_CROSS_REGISTER_FRAME_REDUCTION"],
        "local_context_bridge_cards": route_counts["C_LOCAL_CONTEXT_BRIDGE"],
        "local_repeated_package_projection_cards": route_counts["D_LOCAL_REPEATED_PACKAGE_PROJECTION"],
        "cards_with_local_support": sum(row["support_locality"] != "CROSS_REGISTER" for row in deck),
        "cards_with_cross_register_only_support": sum(row["support_locality"] == "CROSS_REGISTER" for row in deck),
        "ordered_pair_handgrips": len(handgrip_rows),
        "target_recipe_observations": 0,
        "defaults_retained": sum(row["default_decision"] == "KEEP_CURRENT_WORKING_TRANSLATION" for row in deck),
        "target_phrases_changed": 0,
        "working_root_meanings_changed": 0,
        "surface_predictions": 0,
        "occurrence_predictions": 0,
        "guard": GUARD,
    }
    RESULT_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
