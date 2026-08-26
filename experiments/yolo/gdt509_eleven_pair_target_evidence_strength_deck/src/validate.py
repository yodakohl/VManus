#!/usr/bin/env python3
"""Independent validator for the GDT509 eleven-card evidence deck."""

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
VALIDATION_OUT = ART / "gdt509_validation.json"

ROUTE_ORDER = {
    "A_LOCAL_FRAME_REDUCTION": 1,
    "B_CROSS_REGISTER_FRAME_REDUCTION": 2,
    "C_LOCAL_CONTEXT_BRIDGE": 3,
    "D_LOCAL_REPEATED_PACKAGE_PROJECTION": 4,
}
EXPECTED_ROUTE_COUNTS = {
    "A_LOCAL_FRAME_REDUCTION": 3,
    "B_CROSS_REGISTER_FRAME_REDUCTION": 4,
    "C_LOCAL_CONTEXT_BRIDGE": 3,
    "D_LOCAL_REPEATED_PACKAGE_PROJECTION": 1,
}
STATUS = "ELEVEN_PAIR_TARGETS_UNIFIED_IN_FOUR_EVIDENCE_ROUTES__ALL_DEFAULTS_RETAINED"
GUARD = "EVIDENCE_STRENGTH_CONSOLIDATION_ONLY__ALL_TARGET_RECIPES_REMAIN_UNOBSERVED"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    dictionary = read_tsv(DICTIONARY_IN)
    targets = read_tsv(TARGETS_IN)
    contexts = read_tsv(CONTEXT_IN)
    package_rows = read_tsv(PACKAGE_IN)
    deck = read_tsv(DECK_OUT)
    routes = read_tsv(ROUTES_OUT)
    handgrips = read_tsv(HANDGRIPS_OUT)
    result = json.loads(RESULT_OUT.read_text(encoding="utf-8"))
    readable = READABLE_OUT.read_text(encoding="utf-8")

    values = {row["atom"]: row["working_value_de"] for row in dictionary}
    target_by_id = {row["target_frame_card_id"]: row for row in targets}
    context_by_id = {row["source_gdt506_target_frame_card_id"]: row for row in contexts}
    package = package_rows[0]

    checks: list[tuple[str, bool]] = []

    def check(name: str, condition: bool) -> None:
        checks.append((name, bool(condition)))

    check("dictionary_count", len(dictionary) == 46)
    check("target_source_count", len(targets) == 11)
    check("context_source_count", len(contexts) == 4)
    check("package_source_count", len(package_rows) == 1)
    check("deck_count", len(deck) == 11)
    check("route_count", len(routes) == 4)
    check("handgrip_count", len(handgrips) == 5)
    check("card_ids_unique", len({row["evidence_strength_card_id"] for row in deck}) == 11)
    check("source_ids_unique", len({row["source_gdt506_target_frame_card_id"] for row in deck}) == 11)
    check("source_set_complete", {row["source_gdt506_target_frame_card_id"] for row in deck} == set(target_by_id))
    check("matrix_cells_unique", len({row["target_matrix_cell_id"] for row in deck}) == 11)
    check("guard_all_cards", all(row["guard"] == GUARD for row in deck))

    prior_sort: tuple[int, int, str] | None = None
    for index, card in enumerate(deck, start=1):
        prefix = f"card_{index:02d}"
        source = target_by_id[card["source_gdt506_target_frame_card_id"]]
        trace = " · ".join(values[atom] for atom in source["target_action_recipe"].split("+"))
        check(prefix + "_id", card["evidence_strength_card_id"] == f"G509-C{index:02d}")
        check(prefix + "_identity", card["target_matrix_cell_id"] == source["target_matrix_cell_id"] and card["target_register"] == source["target_register"] and card["target_action_recipe"] == source["target_action_recipe"])
        check(prefix + "_pair", card["ordered_action_pair"] == source["ordered_action_pair"])
        check(prefix + "_literal_trace", card["literal_component_trace_de"] == trace)
        check(prefix + "_handgrip", card["carrier_neutral_handgrip_de"] == source["carrier_neutral_handgrip_de"])
        check(prefix + "_translation", card["working_translation_de"] == source["target_current_default_phrase_de"])
        check(prefix + "_argument_policy", card["target_argument_policy"] == source["target_argument_policy"] and card["target_argument_roots"] == source["target_argument_roots"])
        check(prefix + "_old_tier", card["old_gdt506_compatibility_tier"] == source["compatibility_tier"])
        check(prefix + "_old_counts", card["old_pair_carrier_event_count"] == source["old_pair_carrier_event_count"] and card["old_ordered_reduction_candidate_count"] == source["ordered_reduction_candidate_count"] and card["old_argument_compatible_candidate_count"] == source["argument_compatible_candidate_count"])
        check(prefix + "_route_rank", int(card["evidence_route_rank"]) == ROUTE_ORDER[card["evidence_route"]])
        sort_key = (int(card["evidence_route_rank"]), int(card["old_gdt506_priority_rank"]), card["target_matrix_cell_id"])
        check(prefix + "_sort_order", prior_sort is None or sort_key >= prior_sort)
        prior_sort = sort_key

        if source["compatibility_tier"] == "A_LOCAL_ARGUMENT_COMPATIBLE_REDUCTION":
            check(prefix + "_route_a", card["evidence_route"] == "A_LOCAL_FRAME_REDUCTION" and card["support_locality"] == "LOCAL_TARGET_REGISTER")
            check(prefix + "_source_event", card["source_evidence_ids"] == source["selected_source_event_id"])
        elif source["compatibility_tier"] == "B_CROSS_REGISTER_ARGUMENT_COMPATIBLE_REDUCTION":
            check(prefix + "_route_b", card["evidence_route"] == "B_CROSS_REGISTER_FRAME_REDUCTION" and card["support_locality"] == "CROSS_REGISTER")
            check(prefix + "_source_event", card["source_evidence_ids"] == source["selected_source_event_id"])
        elif source["target_matrix_cell_id"] == package["target_matrix_cell_id"]:
            check(prefix + "_route_d", card["evidence_route"] == "D_LOCAL_REPEATED_PACKAGE_PROJECTION" and card["support_locality"] == "LOCAL_SOURCE_PACKAGE_LEVEL")
            check(prefix + "_package_evidence", package["selected_exact_duplicate_event_ids"] in card["source_evidence_ids"] and package["corroborating_event_ids"] in card["source_evidence_ids"])
        else:
            context = context_by_id[source["target_frame_card_id"]]
            check(prefix + "_route_c", card["evidence_route"] == "C_LOCAL_CONTEXT_BRIDGE" and card["support_locality"] == "LOCAL_TARGET_REGISTER")
            check(prefix + "_context_evidence", context["selected_pair_order_event_id"] in card["source_evidence_ids"] and context["selected_context_left_event_id"] in card["source_evidence_ids"] and context["selected_context_right_event_id"] in card["source_evidence_ids"])

        check(prefix + "_keep", card["default_decision"] == "KEEP_CURRENT_WORKING_TRANSLATION")
        check(prefix + "_status", card["translation_status"] == "EXPLORATORY_COMPOSED_DEFAULT__TARGET_UNOBSERVED")
        check(prefix + "_evidence_retained", card["target_evidence_status_retained"] == source["target_evidence_status_retained"] == "COMPOSED_WORKING")
        check(prefix + "_invariants", card["target_phrase_changed"] == card["working_root_meaning_changed"] == card["surface_prediction_made"] == card["occurrence_prediction_made"] == "NO")
        check(prefix + "_guard", card["guard"] == GUARD)

    route_counts = Counter(row["evidence_route"] for row in deck)
    check("route_distribution", dict(route_counts) == EXPECTED_ROUTE_COUNTS)
    route_by_name = {row["evidence_route"]: row for row in routes}
    check("route_set", set(route_by_name) == set(ROUTE_ORDER))
    for route, count in EXPECTED_ROUTE_COUNTS.items():
        row = route_by_name[route]
        group = [card for card in deck if card["evidence_route"] == route]
        check(route + "_rank", int(row["evidence_route_rank"]) == ROUTE_ORDER[route])
        check(route + "_count", int(row["target_card_count"]) == count == len(group))
        check(route + "_registers", row["target_registers"] == "|".join(sorted({card["target_register"] for card in group})))
        check(route + "_pairs", row["ordered_action_pairs"] == "|".join(sorted({card["ordered_action_pair"] for card in group})))
        check(route + "_local_cross", int(row["local_target_card_count"]) == sum(card["support_locality"] != "CROSS_REGISTER" for card in group) and int(row["cross_register_target_card_count"]) == sum(card["support_locality"] == "CROSS_REGISTER" for card in group))
        check(route + "_retained", row["all_defaults_retained"] == "YES")
        check(route + "_guard", row["guard"] == GUARD)

    handgrip_by_pair = {row["ordered_action_pair"]: row for row in handgrips}
    expected_pairs = {"P+CH", "S+CHD", "CH+P", "CH+CH", "CH+SH"}
    check("handgrip_pair_set", set(handgrip_by_pair) == expected_pairs)
    covered_cards = 0
    for pair in expected_pairs:
        row = handgrip_by_pair[pair]
        group = [card for card in deck if card["ordered_action_pair"] == pair]
        covered_cards += len(group)
        check(pair + "_handgrip_count", int(row["target_card_count"]) == len(group))
        check(pair + "_handgrip_text", row["carrier_neutral_handgrip_de"] == group[0]["carrier_neutral_handgrip_de"])
        check(pair + "_handgrip_registers", row["target_registers"] == "|".join(sorted({card["target_register"] for card in group})))
        check(pair + "_handgrip_routes", set(row["evidence_routes"].split("|")) == {card["evidence_route"] for card in group})
        check(pair + "_handgrip_ceiling", row["all_target_recipes_unobserved"] == row["all_defaults_retained"] == "YES")
        check(pair + "_handgrip_guard", row["guard"] == GUARD)
    check("handgrip_coverage_complete", covered_cards == 11)

    check("seven_local_cards", sum(row["support_locality"] != "CROSS_REGISTER" for row in deck) == 7)
    check("four_cross_only_cards", sum(row["support_locality"] == "CROSS_REGISTER" for row in deck) == 4)
    check("all_defaults_keep", all(row["default_decision"] == "KEEP_CURRENT_WORKING_TRANSLATION" for row in deck))
    check("result_status", result["status"] == STATUS)
    check("result_counts", result["pair_target_cards"] == 11 and result["evidence_routes"] == 4 and result["ordered_pair_handgrips"] == 5)
    check("result_route_counts", result["local_frame_reduction_cards"] == 3 and result["cross_register_frame_reduction_cards"] == 4 and result["local_context_bridge_cards"] == 3 and result["local_repeated_package_projection_cards"] == 1)
    check("result_locality", result["cards_with_local_support"] == 7 and result["cards_with_cross_register_only_support"] == 4)
    check("result_defaults", result["defaults_retained"] == 11)
    check("result_ceiling", result["target_recipe_observations"] == result["target_phrases_changed"] == result["working_root_meanings_changed"] == result["surface_predictions"] == result["occurrence_predictions"] == 0)
    check("result_guard", result["guard"] == GUARD)
    check("readable_status", STATUS in readable)
    check("readable_all_cells", all(row["target_matrix_cell_id"] in readable for row in deck))
    check("readable_all_phrases", all(row["working_translation_de"] in readable for row in deck))

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
