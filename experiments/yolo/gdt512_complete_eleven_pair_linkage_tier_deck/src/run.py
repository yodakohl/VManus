#!/usr/bin/env python3
"""Reissue all eleven pair translations with GDT510-511's current support tiers."""

from __future__ import annotations

import csv
import json
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt512_complete_eleven_pair_linkage_tier_deck"
ART = BASE / "artifacts"
G509 = ROOT / "experiments/yolo/gdt509_eleven_pair_target_evidence_strength_deck/artifacts"
G510 = ROOT / "experiments/yolo/gdt510_four_cross_frame_local_factor_bridges/artifacts"
G511 = ROOT / "experiments/yolo/gdt511_schd_local_linkage_strength_atlas/artifacts"

DECK_IN = G509 / "gdt509_11_pair_target_evidence_strength_cards.tsv"
UPGRADES_IN = G510 / "gdt510_4_cross_frame_target_local_upgrade_cards.tsv"
LINKS_IN = G511 / "gdt511_3_register_linkage_strength_cards.tsv"

DECK_OUT = ART / "gdt512_11_current_pair_translation_cards.tsv"
TIERS_OUT = ART / "gdt512_7_support_tier_summary.tsv"
HANDGRIPS_OUT = ART / "gdt512_5_handgrip_current_tier_coverage.tsv"
READABLE_OUT = ART / "GDT512_COMPLETE_ELEVEN_PAIR_LINKAGE_TIER_DECK.md"
RESULT_OUT = ART / "gdt512_result.json"

STATUS = "ELEVEN_PAIR_CARDS_REISSUED_IN_SEVEN_SUPPORT_TIERS__THREE_RETAIN_CROSS_PAIR_ORDER"
GUARD = "COMPLETE_PAIR_TIER_REVISION_ONLY__ALL_TARGET_RECIPES_UNOBSERVED"

TIER_META = {
    "T1_LOCAL_ARGUMENT_COMPATIBLE_FRAME_REDUCTION": (1, "Lokaler argumentkompatibler Rahmenabbau"),
    "T2_LOCAL_CONTEXT_BRIDGE": (2, "Lokale unmittelbare/innerhalb-Karte-Kontextbrücke"),
    "T3_LOCAL_REPEATED_PACKAGE_PROJECTION": (3, "Lokale Wiederholung eines größeren Pakets"),
    "T4_LOCAL_CONTIGUOUS_SUFFIX_REDUCTION": (4, "Lokaler exakter zusammenhängender Suffix"),
    "T5_LOCAL_LONG_SAME_STATEMENT_HEAD_INVENTORY": (5, "Langes lokales Kopf-Inventar in derselben Anweisung"),
    "T6_LOCAL_LONG_SAME_OWNER_PAGE_HEAD_INVENTORY": (6, "Langes lokales Kopf-Inventar bei demselben Besitzer"),
    "T7_LOCAL_LONG_SAME_PAGE_CROSS_OWNER_HEAD_INVENTORY": (7, "Langes lokales Kopf-Inventar nur auf derselben Seite"),
}

LINK_TIER_TO_CURRENT = {
    "A_LONG_SAME_STATEMENT_OWNER_PAGE": "T5_LOCAL_LONG_SAME_STATEMENT_HEAD_INVENTORY",
    "B_LONG_SAME_OWNER_PAGE": "T6_LOCAL_LONG_SAME_OWNER_PAGE_HEAD_INVENTORY",
    "C_LONG_SAME_PAGE_CROSS_OWNER": "T7_LOCAL_LONG_SAME_PAGE_CROSS_OWNER_HEAD_INVENTORY",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty table: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def unique_ids(*chunks: str) -> str:
    values: list[str] = []
    for chunk in chunks:
        for value in chunk.replace("→", "|").split("|"):
            if value and value != "NONE" and value not in values:
                values.append(value)
    return "|".join(values)


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    old_deck = read_tsv(DECK_IN)
    upgrades = read_tsv(UPGRADES_IN)
    links = read_tsv(LINKS_IN)
    if (len(old_deck), len(upgrades), len(links)) != (11, 4, 3):
        raise ValueError("GDT509/GDT510/GDT511 source drift")

    upgrade_by_card = {row["source_gdt509_card_id"]: row for row in upgrades}
    link_by_card = {row["source_gdt510_card_id"]: row for row in links}
    drafted: list[dict[str, object]] = []
    for old in old_deck:
        old_id = old["evidence_strength_card_id"]
        upgrade = upgrade_by_card.get(old_id)
        link = link_by_card.get(old_id)
        if old["evidence_route"] == "A_LOCAL_FRAME_REDUCTION":
            tier = "T1_LOCAL_ARGUMENT_COMPATIBLE_FRAME_REDUCTION"
            support_form = "LOCAL_ARGUMENT_COMPATIBLE_ORDERED_FRAME_REDUCTION"
            pair_order_locality = "LOCAL_TARGET_REGISTER_CARRIER"
            span = "SINGLE_EVENT_REDUCTION"
            evidence = old["source_evidence_ids"]
            reading = old["support_reading_de"]
            residual = old["residual_weakness_de"]
        elif old["evidence_route"] == "C_LOCAL_CONTEXT_BRIDGE":
            tier = "T2_LOCAL_CONTEXT_BRIDGE"
            support_form = "LOCAL_WITHIN_OR_IMMEDIATE_SAME_ARGUMENT_CONTEXT_BRIDGE"
            pair_order_locality = "LOCAL_TARGET_REGISTER_CONTEXT_CHAIN"
            span = "SINGLE_EVENT_AND_OR_IMMEDIATE_EVENTS"
            evidence = old["source_evidence_ids"]
            reading = old["support_reading_de"]
            residual = old["residual_weakness_de"]
        elif old["evidence_route"] == "D_LOCAL_REPEATED_PACKAGE_PROJECTION":
            tier = "T3_LOCAL_REPEATED_PACKAGE_PROJECTION"
            support_form = "LOCAL_REPEATED_CH_PACKAGE_PROJECTION"
            pair_order_locality = "LOCAL_TARGET_REGISTER_PACKAGE_PROJECTION"
            span = "ZERO_OR_ONE_GAP_REPEATED_PACKAGES"
            evidence = old["source_evidence_ids"]
            reading = old["support_reading_de"]
            residual = old["residual_weakness_de"]
        elif old["target_action_recipe"] == "P+CH+E+Y":
            if upgrade is None:
                raise ValueError("missing GDT510 suffix upgrade")
            tier = "T4_LOCAL_CONTIGUOUS_SUFFIX_REDUCTION"
            support_form = "LOCAL_CONTIGUOUS_TARGET_SUFFIX_IN_LONGER_EVENT"
            pair_order_locality = "LOCAL_TARGET_REGISTER_CONTIGUOUS_INTERVAL"
            span = "SINGLE_EVENT_CONTIGUOUS_SUFFIX"
            evidence = unique_ids(upgrade["local_and_cross_evidence_ids"], old["source_evidence_ids"])
            reading = "Der vollständige Zielrahmen steht im Zielregister als exakter zusammenhängender Suffix einer längeren Karte."
            residual = upgrade["residual_weakness_de"]
        else:
            if upgrade is None or link is None:
                raise ValueError(f"missing GDT510/GDT511 head-inventory upgrade for {old_id}")
            tier = LINK_TIER_TO_CURRENT[link["selected_linkage_tier"]]
            support_form = "LOCAL_S_ON_Y_AND_CHD_ON_Y_HEAD_INVENTORY"
            pair_order_locality = "CROSS_REGISTER_CARRIER_ONLY"
            span = "LONG_MULTI_EVENT_HEAD_INVENTORY"
            evidence = unique_ids(
                upgrade["local_and_cross_evidence_ids"],
                link["selected_s_event_id"],
                link["selected_chd_event_id"],
            )
            reading = link["linkage_reading_de"] + " Die gerichtete Paarordnung bleibt bei G407-E1883."
            residual = "Die lokalen Köpfe bilden weder ein unmittelbares noch ein Y-kontinuierliches Paar; das nackte Zielrezept bleibt unbelegt."

        tier_order, tier_title = TIER_META[tier]
        drafted.append({
            "current_pair_card_id": "PENDING",
            "source_gdt509_card_id": old_id,
            "source_gdt506_target_frame_card_id": old["source_gdt506_target_frame_card_id"],
            "target_matrix_cell_id": old["target_matrix_cell_id"],
            "target_register": old["target_register"],
            "target_action_recipe": old["target_action_recipe"],
            "ordered_action_pair": old["ordered_action_pair"],
            "literal_component_trace_de": old["literal_component_trace_de"],
            "carrier_neutral_handgrip_de": old["carrier_neutral_handgrip_de"],
            "working_translation_de": old["working_translation_de"],
            "target_argument_policy": old["target_argument_policy"],
            "target_argument_roots": old["target_argument_roots"],
            "old_gdt509_evidence_route": old["evidence_route"],
            "current_support_tier": tier,
            "current_support_tier_order": tier_order,
            "current_support_tier_title_de": tier_title,
            "target_register_local_support_form": support_form,
            "pair_order_locality": pair_order_locality,
            "support_span_class": span,
            "current_evidence_ids": evidence,
            "current_support_reading_de": reading,
            "current_residual_weakness_de": residual,
            "source_gdt510_upgrade_card_id": upgrade["cross_frame_local_upgrade_card_id"] if upgrade else "NONE",
            "source_gdt511_linkage_card_id": link["register_linkage_strength_card_id"] if link else "NONE",
            "selected_local_linkage_tier": link["selected_linkage_tier"] if link else "NOT_APPLICABLE",
            "selected_local_linkage_event_ids": f"{link['selected_s_event_id']}|{link['selected_chd_event_id']}" if link else "NOT_APPLICABLE",
            "selected_local_linkage_gap": link["selected_intervening_event_count"] if link else "NOT_APPLICABLE",
            "target_register_local_support_present": "YES",
            "default_decision": old["default_decision"],
            "translation_status": old["translation_status"],
            "target_evidence_status_retained": old["target_evidence_status_retained"],
            "target_recipe_observed_exactly": "NO",
            "target_phrase_changed": "NO",
            "working_root_meaning_changed": "NO",
            "surface_prediction_made": "NO",
            "occurrence_prediction_made": "NO",
            "guard": GUARD,
        })

    drafted.sort(key=lambda row: (int(row["current_support_tier_order"]), int(next(old["old_gdt506_priority_rank"] for old in old_deck if old["evidence_strength_card_id"] == row["source_gdt509_card_id"]))))
    for index, row in enumerate(drafted, start=1):
        row["current_pair_card_id"] = f"G512-C{index:02d}"

    tier_rows: list[dict[str, object]] = []
    for tier, (tier_order, tier_title) in TIER_META.items():
        group = [row for row in drafted if row["current_support_tier"] == tier]
        if not group:
            raise ValueError(f"empty support tier {tier}")
        tier_rows.append({
            "support_tier_summary_id": f"G512-T{tier_order:02d}",
            "current_support_tier": tier,
            "current_support_tier_order": tier_order,
            "current_support_tier_title_de": tier_title,
            "pair_card_count": len(group),
            "source_gdt509_card_ids": "|".join(str(row["source_gdt509_card_id"]) for row in group),
            "target_registers": "|".join(sorted({str(row["target_register"]) for row in group})),
            "ordered_action_pairs": "|".join(sorted({str(row["ordered_action_pair"]) for row in group})),
            "pair_order_localities": "|".join(sorted({str(row["pair_order_locality"]) for row in group})),
            "target_register_local_support_count": sum(row["target_register_local_support_present"] == "YES" for row in group),
            "cross_register_pair_order_only_count": sum(row["pair_order_locality"] == "CROSS_REGISTER_CARRIER_ONLY" for row in group),
            "all_target_recipes_unobserved": "YES",
            "all_working_translations_retained": "YES",
            "guard": GUARD,
        })

    handgrip_rows: list[dict[str, object]] = []
    for pair in sorted({str(row["ordered_action_pair"]) for row in drafted}):
        group = [row for row in drafted if row["ordered_action_pair"] == pair]
        handgrip_rows.append({
            "handgrip_tier_coverage_id": f"G512-H{len(handgrip_rows) + 1:02d}",
            "ordered_action_pair": pair,
            "carrier_neutral_handgrip_de": group[0]["carrier_neutral_handgrip_de"],
            "pair_card_count": len(group),
            "target_registers": "|".join(sorted({str(row["target_register"]) for row in group})),
            "current_support_tiers": "|".join(sorted({str(row["current_support_tier"]) for row in group}, key=lambda tier: TIER_META[tier][0])),
            "target_register_pair_order_or_projection_count": sum(row["pair_order_locality"] != "CROSS_REGISTER_CARRIER_ONLY" for row in group),
            "cross_register_pair_order_only_count": sum(row["pair_order_locality"] == "CROSS_REGISTER_CARRIER_ONLY" for row in group),
            "working_translations_de": " | ".join(str(row["working_translation_de"]) for row in group),
            "all_target_recipes_unobserved": "YES",
            "guard": GUARD,
        })

    write_tsv(DECK_OUT, drafted)
    write_tsv(TIERS_OUT, tier_rows)
    write_tsv(HANDGRIPS_OUT, handgrip_rows)

    readable = [
        "# GDT512 — Aktuelles Elf-Karten-Blatt in sieben Stützstufen",
        "",
        f"Status: `{STATUS}`",
        "",
        "| Stufe | Karten | Bedeutung | Paarordnung nur fremd |",
        "|---|---:|---|---:|",
    ]
    for tier in tier_rows:
        readable.append(f"| {tier['current_support_tier']} | {tier['pair_card_count']} | {tier['current_support_tier_title_de']} | {tier['cross_register_pair_order_only_count']} |")
    for tier in tier_rows:
        readable.extend(["", f"## {tier['current_support_tier_title_de']}", ""])
        for card in [row for row in drafted if row["current_support_tier"] == tier["current_support_tier"]]:
            readable.extend([
                f"- **{card['target_register']} `{card['target_action_recipe']}`:** {card['working_translation_de']}",
                f"  - Stütze: {card['current_support_reading_de']}",
                f"  - Rest: {card['current_residual_weakness_de']}",
            ])
    readable.extend([
        "",
        "## Gemeinsame Grenze",
        "",
        "Alle elf Zielrezepte bleiben unbeobachtete `COMPOSED_WORKING`-Karten. Acht besitzen im Zielregister eine gerichtete Paar-, Intervall- oder Paketprojektion; bei den drei `S+CHD+Y`-Karten bleiben nur die Einzelköpfe lokal und die Paarordnung kommt weiterhin aus `G407-E1883`. Keine Phrase oder Wurzelbedeutung ändert sich.",
    ])
    READABLE_OUT.write_text("\n".join(readable) + "\n", encoding="utf-8")

    result = {
        "status": STATUS,
        "pair_translation_cards": len(drafted),
        "support_tiers": len(tier_rows),
        "ordered_pair_handgrips": len(handgrip_rows),
        "cards_with_target_register_local_support": sum(row["target_register_local_support_present"] == "YES" for row in drafted),
        "cards_with_target_register_pair_order_interval_or_projection": sum(row["pair_order_locality"] != "CROSS_REGISTER_CARRIER_ONLY" for row in drafted),
        "cards_with_cross_register_pair_order_only": sum(row["pair_order_locality"] == "CROSS_REGISTER_CARRIER_ONLY" for row in drafted),
        "local_frame_reduction_cards": sum(row["current_support_tier"].startswith("T1_") for row in drafted),
        "local_context_bridge_cards": sum(row["current_support_tier"].startswith("T2_") for row in drafted),
        "local_repeated_package_cards": sum(row["current_support_tier"].startswith("T3_") for row in drafted),
        "local_contiguous_suffix_cards": sum(row["current_support_tier"].startswith("T4_") for row in drafted),
        "local_long_head_inventory_cards": sum(str(row["current_support_tier"]).startswith(("T5_", "T6_", "T7_")) for row in drafted),
        "defaults_retained": sum(row["default_decision"] == "KEEP_CURRENT_WORKING_TRANSLATION" for row in drafted),
        "target_recipe_observations": 0,
        "target_phrases_changed": 0,
        "working_root_meanings_changed": 0,
        "surface_predictions": 0,
        "occurrence_predictions": 0,
        "pair_front_currently_consolidated": 1,
        "guard": GUARD,
    }
    RESULT_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
