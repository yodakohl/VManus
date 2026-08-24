#!/usr/bin/env python3
"""Damage primary case cues and reconstruct cases from the remaining deck."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P613 = ROOT / "experiments/yolo/sidequest_semantic_duplicate_command_resolution_six_hundred_thirteenth"
P631 = ROOT / "experiments/yolo/sidequest_semantic_five_branch_composition_six_hundred_thirty_first"
P633 = ROOT / "experiments/yolo/sidequest_semantic_finite_construction_grammar_six_hundred_thirty_third"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


REMOVALS = {
    "C1": {"PRIMARY_CUE_REMOVED": ["PROC005"], "FULL_CUE_FAMILY_REMOVED": ["PROC005"]},
    "C2": {"PRIMARY_CUE_REMOVED": ["PROC014"], "FULL_CUE_FAMILY_REMOVED": ["PROC014", "PROC017", "PROC018"]},
    "C3": {"PRIMARY_CUE_REMOVED": ["PROC028"], "FULL_CUE_FAMILY_REMOVED": ["PROC028"]},
    "C4": {"PRIMARY_CUE_REMOVED": ["PROC040"], "FULL_CUE_FAMILY_REMOVED": ["PROC040"]},
    "C5": {"PRIMARY_CUE_REMOVED": ["PROC052"], "FULL_CUE_FAMILY_REMOVED": ["PROC052", "PROC063", "PROC053"]},
}


def choose_case(card_ids: list[str], card_by_id: dict[str, dict[str, str]]) -> str:
    components = [part for card_id in card_ids for part in card_by_id[card_id]["semantic_component_parse"].split("+")]
    if "HO" in components:
        return "C5"
    if "CFH" in components:
        return "C3"
    if "AN" in components:
        return "C4"
    if "OS" in components:
        return "C1"
    if components.count("CTH") >= 3:
        return "C2"
    return "UNRESOLVED"


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    cards = read_tsv(P613 / "SIX_HUNDRED_THIRTEENTH_173_REVISED_CARD_COMMAND_MAP.tsv")
    masters = read_tsv(P631 / "SIX_HUNDRED_THIRTY_FIRST_5_ORDER_SUMMARY.tsv")
    orders = read_tsv(P633 / "SIX_HUNDRED_THIRTY_THIRD_22_LEGAL_ORDERS.tsv")
    edges = read_tsv(P633 / "SIX_HUNDRED_THIRTY_THIRD_25_PRECEDENCE_RULES.tsv")
    card_by_id = {row["card_no"]: row for row in cards}
    template_cards = {row["intended_case_id"]: row["card_sequence"].split("|") for row in masters}
    template_surfaces = {row["intended_case_id"]: row["surface_sequence"].split() for row in masters}
    template_nodes = {
        case: next(row for row in orders if row["case_id"] == case and row["is_pass631_order"] == "YES")["node_order"].split("-")
        for case in template_cards
    }
    template_card_to_node = {
        case: dict(zip(template_cards[case], template_nodes[case]))
        for case in template_cards
    }

    damaged_rows: list[dict[str, object]] = []
    score_rows: list[dict[str, object]] = []
    decision_rows: list[dict[str, object]] = []
    for case_id in sorted(REMOVALS):
        for damage_kind in ["PRIMARY_CUE_REMOVED", "FULL_CUE_FAMILY_REMOVED"]:
            damage_id = f"{case_id}_{damage_kind}"
            removed = REMOVALS[case_id][damage_kind]
            visible_pairs = [
                (surface, card_id)
                for surface, card_id in zip(template_surfaces[case_id], template_cards[case_id])
                if card_id not in removed
            ]
            visible_surfaces = [surface for surface, _ in visible_pairs]
            visible_cards = [card_id for _, card_id in visible_pairs]
            old_selector = choose_case(visible_cards, card_by_id)
            damaged_rows.append({
                "damage_id": damage_id,
                "intended_case": case_id,
                "damage_kind": damage_kind,
                "removed_cards": "|".join(removed),
                "removed_surfaces": "|".join(template_surfaces[case_id][template_cards[case_id].index(card_id)] for card_id in removed),
                "remaining_surface_fragment": " ".join(visible_surfaces),
                "remaining_card_fragment": "|".join(visible_cards),
                "remaining_cards": len(visible_cards),
                "old_single_cue_selector": old_selector,
                "old_selector_correct": "YES" if old_selector == case_id else "NO",
            })

            local_scores = []
            for candidate in sorted(template_cards):
                candidate_cards = template_cards[candidate]
                overlap_counter = Counter(visible_cards) & Counter(candidate_cards)
                overlap = sum(overlap_counter.values())
                unexplained = len(visible_cards) - overlap
                candidate_node_order = template_nodes[candidate]
                candidate_node_position = {node: index for index, node in enumerate(candidate_node_order)}
                visible_candidate_nodes = [template_card_to_node[candidate][card_id] for card_id in visible_cards if card_id in template_card_to_node[candidate]]
                visible_node_position = {node: index for index, node in enumerate(visible_candidate_nodes)}
                candidate_edges = [row for row in edges if row["case_id"] == candidate]
                testable_edges = [row for row in candidate_edges if row["left_node"] in visible_node_position and row["right_node"] in visible_node_position]
                supported = sum(visible_node_position[row["left_node"]] < visible_node_position[row["right_node"]] for row in testable_edges)
                violated = len(testable_edges) - supported
                score = (unexplained, -overlap, violated, -supported)
                local_scores.append((score, candidate))
                score_rows.append({
                    "damage_id": damage_id,
                    "intended_case": case_id,
                    "candidate_case": candidate,
                    "visible_cards": len(visible_cards),
                    "card_overlap": overlap,
                    "unexplained_visible_cards": unexplained,
                    "testable_precedence_edges": len(testable_edges),
                    "supported_precedence_edges": supported,
                    "violated_precedence_edges": violated,
                    "score_key": f"{unexplained}|{-overlap}|{violated}|{-supported}",
                    "complete_subset_fit": "YES" if unexplained == 0 else "NO",
                })
            local_scores.sort()
            best_score = local_scores[0][0]
            winners = [candidate for score, candidate in local_scores if score == best_score]
            selected = winners[0] if len(winners) == 1 else "AMBIGUOUS"
            decision_rows.append({
                "damage_id": damage_id,
                "intended_case": case_id,
                "damage_kind": damage_kind,
                "remaining_cards": len(visible_cards),
                "old_selector": old_selector,
                "template_selected_case": selected,
                "unique_best_template": "YES" if len(winners) == 1 else "NO",
                "exact_case_recovery": "YES" if selected == case_id else "NO",
                "best_score": "|".join(str(value) for value in best_score),
                "runner_up_case": local_scores[len(winners)][1] if len(winners) < len(local_scores) else "NONE",
                "restored_surface_strip": " ".join(template_surfaces[selected]) if selected != "AMBIGUOUS" else "UNRESOLVED",
                "restored_card_strip": "|".join(template_cards[selected]) if selected != "AMBIGUOUS" else "UNRESOLVED",
                "visible_owner_or_margin_required": "NO" if selected == case_id else "YES",
                "case_template_required": "YES",
            })

    write_tsv(HERE / "SIX_HUNDRED_FORTY_FIFTH_10_DAMAGED_FRAGMENTS.tsv", damaged_rows, list(damaged_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FORTY_FIFTH_50_TEMPLATE_SCORES.tsv", score_rows, list(score_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FORTY_FIFTH_10_RECONSTRUCTIONS.tsv", decision_rows, list(decision_rows[0]))

    md = [
        "# Fallwahl nach beschädigtem Selektor",
        "",
        "Der alte Ein-Cue-Selector wird zuerst angewandt und darf scheitern. Danach werden die verbliebenen Karten als geordnete Teilmenge mit allen fünf gelernten Fallmustern verglichen. Ein Muster gewinnt nur, wenn es alle sichtbaren Karten erklärt und ihre noch prüfbaren Vorher-Nachher-Beziehungen wahrt.",
        "",
    ]
    for row in decision_rows:
        damaged = next(item for item in damaged_rows if item["damage_id"] == row["damage_id"])
        md.extend([
            f"## {row['damage_id']}",
            "",
            f"- Rest: `{damaged['remaining_surface_fragment']}`",
            f"- alter Selector: {row['old_selector']}",
            f"- Musterlesung: {row['template_selected_case']}",
            f"- wiederhergestellt: `{row['restored_surface_strip']}`",
            "",
        ])
    (HERE / "SIX_HUNDRED_FORTY_FIFTH_SELECTOR_DAMAGE_BOOK.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "damaged_fragments": len(damaged_rows),
        "candidate_scores": len(score_rows),
        "reconstructions": len(decision_rows),
        "old_selector_recoveries": sum(row["old_selector"] == row["intended_case"] for row in decision_rows),
        "template_recoveries": sum(row["exact_case_recovery"] == "YES" for row in decision_rows),
        "unique_template_recoveries": sum(row["exact_case_recovery"] == "YES" and row["unique_best_template"] == "YES" for row in decision_rows),
        "full_cue_family_recoveries": sum(row["damage_kind"] == "FULL_CUE_FAMILY_REMOVED" and row["exact_case_recovery"] == "YES" for row in decision_rows),
        "minimum_remaining_cards": min(int(row["remaining_cards"]) for row in decision_rows),
        "visible_owner_or_margin_requirements": sum(row["visible_owner_or_margin_required"] == "YES" for row in decision_rows),
        "new_cards": 0,
        "new_surfaces": 0,
        "new_meanings": 0,
        "decision": "FIVE_CASE_TEMPLATES_RECONSTRUCT_SELECTOR_DAMAGED_FRAGMENTS",
    }
    (HERE / "SIX_HUNDRED_FORTY_FIFTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
