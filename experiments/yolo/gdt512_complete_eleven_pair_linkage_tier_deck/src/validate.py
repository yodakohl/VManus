#!/usr/bin/env python3
"""Independent validator for GDT512's revised complete eleven-card deck."""

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
VALIDATION_OUT = ART / "gdt512_validation.json"

STATUS = "ELEVEN_PAIR_CARDS_REISSUED_IN_SEVEN_SUPPORT_TIERS__THREE_RETAIN_CROSS_PAIR_ORDER"
GUARD = "COMPLETE_PAIR_TIER_REVISION_ONLY__ALL_TARGET_RECIPES_UNOBSERVED"

TIER_ORDER = {
    "T1_LOCAL_ARGUMENT_COMPATIBLE_FRAME_REDUCTION": 1,
    "T2_LOCAL_CONTEXT_BRIDGE": 2,
    "T3_LOCAL_REPEATED_PACKAGE_PROJECTION": 3,
    "T4_LOCAL_CONTIGUOUS_SUFFIX_REDUCTION": 4,
    "T5_LOCAL_LONG_SAME_STATEMENT_HEAD_INVENTORY": 5,
    "T6_LOCAL_LONG_SAME_OWNER_PAGE_HEAD_INVENTORY": 6,
    "T7_LOCAL_LONG_SAME_PAGE_CROSS_OWNER_HEAD_INVENTORY": 7,
}

LINK_TO_TIER = {
    "A_LONG_SAME_STATEMENT_OWNER_PAGE": "T5_LOCAL_LONG_SAME_STATEMENT_HEAD_INVENTORY",
    "B_LONG_SAME_OWNER_PAGE": "T6_LOCAL_LONG_SAME_OWNER_PAGE_HEAD_INVENTORY",
    "C_LONG_SAME_PAGE_CROSS_OWNER": "T7_LOCAL_LONG_SAME_PAGE_CROSS_OWNER_HEAD_INVENTORY",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def split_evidence(value: str) -> set[str]:
    return {item for item in value.replace("→", "|").split("|") if item and item != "NONE"}


def main() -> int:
    old_deck = read_tsv(DECK_IN)
    upgrades = read_tsv(UPGRADES_IN)
    links = read_tsv(LINKS_IN)
    deck = read_tsv(DECK_OUT)
    tiers = read_tsv(TIERS_OUT)
    handgrips = read_tsv(HANDGRIPS_OUT)
    result = json.loads(RESULT_OUT.read_text(encoding="utf-8"))
    readable = READABLE_OUT.read_text(encoding="utf-8")

    old_by_id = {row["evidence_strength_card_id"]: row for row in old_deck}
    upgrade_by_id = {row["source_gdt509_card_id"]: row for row in upgrades}
    link_by_id = {row["source_gdt510_card_id"]: row for row in links}
    deck_by_old_id = {row["source_gdt509_card_id"]: row for row in deck}

    checks: list[tuple[str, bool]] = []

    def check(name: str, condition: bool) -> None:
        checks.append((name, bool(condition)))

    check("old_deck_count", len(old_deck) == 11)
    check("upgrade_count", len(upgrades) == 4)
    check("link_count", len(links) == 3)
    check("deck_count", len(deck) == 11)
    check("tier_count", len(tiers) == 7)
    check("handgrip_count", len(handgrips) == 5)
    check("source_coverage", set(deck_by_old_id) == set(old_by_id))
    check("card_ids", [row["current_pair_card_id"] for row in deck] == [f"G512-C{i:02d}" for i in range(1, 12)])
    check("tier_ids", [row["support_tier_summary_id"] for row in tiers] == [f"G512-T{i:02d}" for i in range(1, 8)])
    check("handgrip_ids", [row["handgrip_tier_coverage_id"] for row in handgrips] == [f"G512-H{i:02d}" for i in range(1, 6)])
    check("guard_all", all(row["guard"] == GUARD for rows in (deck, tiers, handgrips) for row in rows))

    prior_key: tuple[int, int] | None = None
    for row in deck:
        old = old_by_id[row["source_gdt509_card_id"]]
        upgrade = upgrade_by_id.get(row["source_gdt509_card_id"])
        link = link_by_id.get(row["source_gdt509_card_id"])
        label = row["current_pair_card_id"]
        identity_fields = [
            "source_gdt506_target_frame_card_id",
            "target_matrix_cell_id",
            "target_register",
            "target_action_recipe",
            "ordered_action_pair",
            "literal_component_trace_de",
            "carrier_neutral_handgrip_de",
            "working_translation_de",
            "target_argument_policy",
            "target_argument_roots",
        ]
        check(label + "_identity", all(row[field] == old[field] for field in identity_fields))
        check(label + "_old_route", row["old_gdt509_evidence_route"] == old["evidence_route"])
        check(label + "_tier_order", int(row["current_support_tier_order"]) == TIER_ORDER[row["current_support_tier"]])
        sort_key = (int(row["current_support_tier_order"]), int(old["old_gdt506_priority_rank"]))
        check(label + "_sort", prior_key is None or sort_key >= prior_key)
        prior_key = sort_key
        check(label + "_local_support", row["target_register_local_support_present"] == "YES")
        check(label + "_decisions", row["default_decision"] == old["default_decision"] == "KEEP_CURRENT_WORKING_TRANSLATION" and row["translation_status"] == old["translation_status"])
        check(label + "_evidence_label", row["target_evidence_status_retained"] == old["target_evidence_status_retained"] == "COMPOSED_WORKING")
        check(label + "_invariants", row["target_recipe_observed_exactly"] == row["target_phrase_changed"] == row["working_root_meaning_changed"] == row["surface_prediction_made"] == row["occurrence_prediction_made"] == "NO")

        if old["evidence_route"] == "A_LOCAL_FRAME_REDUCTION":
            expected_tier = "T1_LOCAL_ARGUMENT_COMPATIBLE_FRAME_REDUCTION"
            check(label + "_form", row["target_register_local_support_form"] == "LOCAL_ARGUMENT_COMPATIBLE_ORDERED_FRAME_REDUCTION")
            check(label + "_order_locality", row["pair_order_locality"] == "LOCAL_TARGET_REGISTER_CARRIER" and row["support_span_class"] == "SINGLE_EVENT_REDUCTION")
            check(label + "_evidence", split_evidence(row["current_evidence_ids"]) == split_evidence(old["source_evidence_ids"]))
            check(label + "_source_extensions", row["source_gdt510_upgrade_card_id"] == row["source_gdt511_linkage_card_id"] == "NONE")
        elif old["evidence_route"] == "C_LOCAL_CONTEXT_BRIDGE":
            expected_tier = "T2_LOCAL_CONTEXT_BRIDGE"
            check(label + "_form", row["target_register_local_support_form"] == "LOCAL_WITHIN_OR_IMMEDIATE_SAME_ARGUMENT_CONTEXT_BRIDGE")
            check(label + "_order_locality", row["pair_order_locality"] == "LOCAL_TARGET_REGISTER_CONTEXT_CHAIN" and row["support_span_class"] == "SINGLE_EVENT_AND_OR_IMMEDIATE_EVENTS")
            check(label + "_evidence", split_evidence(row["current_evidence_ids"]) == split_evidence(old["source_evidence_ids"]))
            check(label + "_source_extensions", row["source_gdt510_upgrade_card_id"] == row["source_gdt511_linkage_card_id"] == "NONE")
        elif old["evidence_route"] == "D_LOCAL_REPEATED_PACKAGE_PROJECTION":
            expected_tier = "T3_LOCAL_REPEATED_PACKAGE_PROJECTION"
            check(label + "_form", row["target_register_local_support_form"] == "LOCAL_REPEATED_CH_PACKAGE_PROJECTION")
            check(label + "_order_locality", row["pair_order_locality"] == "LOCAL_TARGET_REGISTER_PACKAGE_PROJECTION" and row["support_span_class"] == "ZERO_OR_ONE_GAP_REPEATED_PACKAGES")
            check(label + "_evidence", split_evidence(row["current_evidence_ids"]) == split_evidence(old["source_evidence_ids"]))
            check(label + "_source_extensions", row["source_gdt510_upgrade_card_id"] == row["source_gdt511_linkage_card_id"] == "NONE")
        elif old["target_action_recipe"] == "P+CH+E+Y":
            expected_tier = "T4_LOCAL_CONTIGUOUS_SUFFIX_REDUCTION"
            check(label + "_upgrade_exists", upgrade is not None and link is None)
            check(label + "_form", row["target_register_local_support_form"] == "LOCAL_CONTIGUOUS_TARGET_SUFFIX_IN_LONGER_EVENT")
            check(label + "_order_locality", row["pair_order_locality"] == "LOCAL_TARGET_REGISTER_CONTIGUOUS_INTERVAL" and row["support_span_class"] == "SINGLE_EVENT_CONTIGUOUS_SUFFIX")
            check(label + "_evidence", split_evidence(row["current_evidence_ids"]) == split_evidence(old["source_evidence_ids"]) | split_evidence(upgrade["local_and_cross_evidence_ids"]))
            check(label + "_source_extensions", row["source_gdt510_upgrade_card_id"] == upgrade["cross_frame_local_upgrade_card_id"] and row["source_gdt511_linkage_card_id"] == "NONE")
        else:
            check(label + "_sources_exist", upgrade is not None and link is not None)
            expected_tier = LINK_TO_TIER[link["selected_linkage_tier"]]
            check(label + "_form", row["target_register_local_support_form"] == "LOCAL_S_ON_Y_AND_CHD_ON_Y_HEAD_INVENTORY")
            check(label + "_order_locality", row["pair_order_locality"] == "CROSS_REGISTER_CARRIER_ONLY" and row["support_span_class"] == "LONG_MULTI_EVENT_HEAD_INVENTORY")
            expected_evidence = split_evidence(upgrade["local_and_cross_evidence_ids"]) | {link["selected_s_event_id"], link["selected_chd_event_id"]}
            check(label + "_evidence", split_evidence(row["current_evidence_ids"]) == expected_evidence)
            check(label + "_source_extensions", row["source_gdt510_upgrade_card_id"] == upgrade["cross_frame_local_upgrade_card_id"] and row["source_gdt511_linkage_card_id"] == link["register_linkage_strength_card_id"])
            check(label + "_linkage_fields", row["selected_local_linkage_tier"] == link["selected_linkage_tier"] and row["selected_local_linkage_event_ids"] == f"{link['selected_s_event_id']}|{link['selected_chd_event_id']}" and row["selected_local_linkage_gap"] == link["selected_intervening_event_count"])
            check(label + "_cross_event", "G407-E1883" in split_evidence(row["current_evidence_ids"]) and "G407-E1883" in row["current_support_reading_de"])
        check(label + "_tier", row["current_support_tier"] == expected_tier)
        if link is None:
            check(label + "_no_link_fields", row["selected_local_linkage_tier"] == row["selected_local_linkage_event_ids"] == row["selected_local_linkage_gap"] == "NOT_APPLICABLE")

    expected_tier_counts = {
        "T1_LOCAL_ARGUMENT_COMPATIBLE_FRAME_REDUCTION": 3,
        "T2_LOCAL_CONTEXT_BRIDGE": 3,
        "T3_LOCAL_REPEATED_PACKAGE_PROJECTION": 1,
        "T4_LOCAL_CONTIGUOUS_SUFFIX_REDUCTION": 1,
        "T5_LOCAL_LONG_SAME_STATEMENT_HEAD_INVENTORY": 1,
        "T6_LOCAL_LONG_SAME_OWNER_PAGE_HEAD_INVENTORY": 1,
        "T7_LOCAL_LONG_SAME_PAGE_CROSS_OWNER_HEAD_INVENTORY": 1,
    }
    check("tier_distribution", dict(Counter(row["current_support_tier"] for row in deck)) == expected_tier_counts)
    tier_by_name = {row["current_support_tier"]: row for row in tiers}
    check("tier_coverage", set(tier_by_name) == set(TIER_ORDER))
    for tier, expected_count in expected_tier_counts.items():
        row = tier_by_name[tier]
        group = [card for card in deck if card["current_support_tier"] == tier]
        check(tier + "_id_order", row["support_tier_summary_id"] == f"G512-T{TIER_ORDER[tier]:02d}" and int(row["current_support_tier_order"]) == TIER_ORDER[tier])
        check(tier + "_count", int(row["pair_card_count"]) == expected_count == len(group))
        check(tier + "_source_ids", row["source_gdt509_card_ids"] == "|".join(card["source_gdt509_card_id"] for card in group))
        check(tier + "_registers", row["target_registers"] == "|".join(sorted({card["target_register"] for card in group})))
        check(tier + "_pairs", row["ordered_action_pairs"] == "|".join(sorted({card["ordered_action_pair"] for card in group})))
        check(tier + "_locality", row["pair_order_localities"] == "|".join(sorted({card["pair_order_locality"] for card in group})))
        check(tier + "_support_counts", int(row["target_register_local_support_count"]) == len(group) and int(row["cross_register_pair_order_only_count"]) == sum(card["pair_order_locality"] == "CROSS_REGISTER_CARRIER_ONLY" for card in group))
        check(tier + "_ceiling", row["all_target_recipes_unobserved"] == row["all_working_translations_retained"] == "YES")

    handgrip_by_pair = {row["ordered_action_pair"]: row for row in handgrips}
    expected_pairs = {"P+CH", "S+CHD", "CH+P", "CH+CH", "CH+SH"}
    check("handgrip_pairs", set(handgrip_by_pair) == expected_pairs)
    for pair, row in handgrip_by_pair.items():
        group = [card for card in deck if card["ordered_action_pair"] == pair]
        check(pair + "_count", int(row["pair_card_count"]) == len(group))
        check(pair + "_handgrip", row["carrier_neutral_handgrip_de"] == group[0]["carrier_neutral_handgrip_de"])
        check(pair + "_registers", row["target_registers"] == "|".join(sorted({card["target_register"] for card in group})))
        expected_tiers = "|".join(sorted({card["current_support_tier"] for card in group}, key=lambda tier: TIER_ORDER[tier]))
        check(pair + "_tiers", row["current_support_tiers"] == expected_tiers)
        local_count = sum(card["pair_order_locality"] != "CROSS_REGISTER_CARRIER_ONLY" for card in group)
        check(pair + "_local_cross", int(row["target_register_pair_order_or_projection_count"]) == local_count and int(row["cross_register_pair_order_only_count"]) == len(group) - local_count)
        check(pair + "_phrases", row["working_translations_de"] == " | ".join(card["working_translation_de"] for card in group))
        check(pair + "_ceiling", row["all_target_recipes_unobserved"] == "YES")

    check("all_local_support", sum(row["target_register_local_support_present"] == "YES" for row in deck) == 11)
    check("eight_local_order_or_projection", sum(row["pair_order_locality"] != "CROSS_REGISTER_CARRIER_ONLY" for row in deck) == 8)
    check("three_cross_order", sum(row["pair_order_locality"] == "CROSS_REGISTER_CARRIER_ONLY" for row in deck) == 3)
    check("all_defaults", sum(row["default_decision"] == "KEEP_CURRENT_WORKING_TRANSLATION" for row in deck) == 11)
    check("result_status", result["status"] == STATUS)
    check("result_counts", result["pair_translation_cards"] == 11 and result["support_tiers"] == 7 and result["ordered_pair_handgrips"] == 5)
    check("result_locality", result["cards_with_target_register_local_support"] == 11 and result["cards_with_target_register_pair_order_interval_or_projection"] == 8 and result["cards_with_cross_register_pair_order_only"] == 3)
    check("result_tier_counts", result["local_frame_reduction_cards"] == 3 and result["local_context_bridge_cards"] == 3 and result["local_repeated_package_cards"] == 1 and result["local_contiguous_suffix_cards"] == 1 and result["local_long_head_inventory_cards"] == 3)
    check("result_defaults", result["defaults_retained"] == 11 and result["pair_front_currently_consolidated"] == 1)
    check("result_invariants", result["target_recipe_observations"] == result["target_phrases_changed"] == result["working_root_meanings_changed"] == result["surface_predictions"] == result["occurrence_predictions"] == 0)
    check("result_guard", result["guard"] == GUARD)
    check("readable_status", STATUS in readable)
    check("readable_tiers", all(tier in readable for tier in TIER_ORDER))
    check("readable_cards", all(row["working_translation_de"] in readable and row["target_action_recipe"] in readable for row in deck))
    check("readable_cross_event", "G407-E1883" in readable)

    failed = [name for name, passed in checks if not passed]
    validation = {
        "status": "PASS" if not failed else "FAIL",
        "checks_total": len(checks),
        "checks_passed": len(checks) - len(failed),
        "checks_failed": len(failed),
        "failed_checks": failed,
    }
    VALIDATION_OUT.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
