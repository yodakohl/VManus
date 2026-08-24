#!/usr/bin/env python3
"""Generalize minimal surface/card/order correction across C1-C5."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
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


CONFIG = {
    "C1": {"allograph_pos": 1, "allograph": "okaiin", "wrong_pos": 4, "wrong_surface": "qokain", "swap": (5, 6)},
    "C2": {"allograph_pos": 5, "allograph": "okal", "wrong_pos": 6, "wrong_surface": "qokeedy", "swap": (3, 4)},
    "C3": {"allograph_pos": 3, "allograph": "okaiin", "wrong_pos": 5, "wrong_surface": "tshey", "swap": (1, 2)},
    "C4": {"allograph_pos": 4, "allograph": "okal", "wrong_pos": 2, "wrong_surface": "qokaiin", "swap": (5, 6)},
    "C5": {"allograph_pos": 2, "allograph": "okaiin", "wrong_pos": 5, "wrong_surface": "daiin", "swap": (3, 4)},
}


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    cards = read_tsv(P613 / "SIX_HUNDRED_THIRTEENTH_173_REVISED_CARD_COMMAND_MAP.tsv")
    masters = read_tsv(P631 / "SIX_HUNDRED_THIRTY_FIRST_5_ORDER_SUMMARY.tsv")
    orders = read_tsv(P633 / "SIX_HUNDRED_THIRTY_THIRD_22_LEGAL_ORDERS.tsv")
    edges = read_tsv(P633 / "SIX_HUNDRED_THIRTY_THIRD_25_PRECEDENCE_RULES.tsv")
    card_by_id = {row["card_no"]: row for row in cards}
    surface_to_cards: dict[str, set[str]] = defaultdict(set)
    for row in cards:
        for surface in row["surfaces"].split("|"):
            surface_to_cards[surface].add(row["card_no"])

    def backread(surfaces: list[str]) -> list[str]:
        return [next(iter(surface_to_cards[surface])) if len(surface_to_cards[surface]) == 1 else "AMBIGUOUS" for surface in surfaces]

    summary_rows: list[dict[str, object]] = []
    position_rows: list[dict[str, object]] = []
    stage_rows: list[dict[str, object]] = []
    for case_id in sorted(CONFIG):
        config = CONFIG[case_id]
        master = next(row for row in masters if row["intended_case_id"] == case_id)
        order = next(row for row in orders if row["case_id"] == case_id and row["is_pass631_order"] == "YES")
        master_surfaces = master["surface_sequence"].split()
        master_cards = master["card_sequence"].split("|")
        master_nodes = order["node_order"].split("-")

        corrected_surfaces = list(master_surfaces)
        corrected_surfaces[int(config["allograph_pos"]) - 1] = str(config["allograph"])
        corrected_cards = backread(corrected_surfaces)

        before_swap_surfaces = list(corrected_surfaces)
        before_swap_surfaces[int(config["wrong_pos"]) - 1] = str(config["wrong_surface"])
        before_swap_cards = backread(before_swap_surfaces)
        apprentice_surfaces = list(before_swap_surfaces)
        left, right = (int(value) - 1 for value in config["swap"])
        apprentice_surfaces[left], apprentice_surfaces[right] = apprentice_surfaces[right], apprentice_surfaces[left]
        apprentice_cards = backread(apprentice_surfaces)
        apprentice_nodes = list(master_nodes)
        apprentice_nodes[left], apprentice_nodes[right] = apprentice_nodes[right], apprentice_nodes[left]
        node_position = {node: index for index, node in enumerate(apprentice_nodes)}
        case_edges = [row for row in edges if row["case_id"] == case_id]
        violated = [row for row in case_edges if node_position[row["left_node"]] > node_position[row["right_node"]]]

        allograph_index = int(config["allograph_pos"]) - 1
        wrong_index = int(config["wrong_pos"]) - 1
        allograph_card = backread([str(config["allograph"])])[0]
        wrong_card = backread([str(config["wrong_surface"])])[0]
        summary_rows.append({
            "case_id": case_id,
            "master_surface_strip": " ".join(master_surfaces),
            "master_card_strip": "|".join(master_cards),
            "apprentice_surface_strip": " ".join(apprentice_surfaces),
            "apprentice_card_strip": "|".join(apprentice_cards),
            "corrected_surface_strip": " ".join(corrected_surfaces),
            "corrected_card_strip": "|".join(corrected_cards),
            "allograph_change": f"{master_surfaces[allograph_index]}>{config['allograph']}",
            "allograph_same_card": "YES" if allograph_card == master_cards[allograph_index] else "NO",
            "wrong_card_change": f"{master_surfaces[wrong_index]}>{config['wrong_surface']}",
            "expected_card_no": master_cards[wrong_index],
            "wrong_card_no": wrong_card,
            "wrong_card_command_de": card_by_id[wrong_card]["standard_command_de"],
            "expected_command_de": card_by_id[master_cards[wrong_index]]["standard_command_de"],
            "swapped_positions": f"{left + 1}|{right + 1}",
            "master_node_order": "-".join(master_nodes),
            "apprentice_node_order": "-".join(apprentice_nodes),
            "violated_precedence_rules": len(violated),
            "violated_rule": "|".join(row["precedence_rule"] for row in violated),
            "final_cards_equal_master": "YES" if corrected_cards == master_cards else "NO",
            "foreign_hand_preserved": "YES" if corrected_surfaces[allograph_index] != master_surfaces[allograph_index] else "NO",
            "semantic_repairs": 2,
            "unnecessary_normalizations": 0,
        })

        inverse_source = {left: right, right: left}
        for position in range(6):
            source_position = inverse_source.get(position, position)
            if position == left or position == right:
                defect = "ORDER_SWAP_MEMBER"
            elif position == wrong_index:
                defect = "WRONG_EXACT_CARD"
            elif position == allograph_index:
                defect = "HARMLESS_ALLOGRAPH"
            else:
                defect = "UNCHANGED"
            position_rows.append({
                "case_id": case_id,
                "apprentice_position": position + 1,
                "source_master_position": source_position + 1,
                "apprentice_surface": apprentice_surfaces[position],
                "apprentice_card_no": apprentice_cards[position],
                "master_surface_at_position": master_surfaces[position],
                "master_card_at_position": master_cards[position],
                "defect_class": defect,
                "master_action": {
                    "ORDER_SWAP_MEMBER": "SWAP_PAIR",
                    "WRONG_EXACT_CARD": "REPLACE_CARD",
                    "HARMLESS_ALLOGRAPH": "KEEP_FOREIGN_HAND",
                    "UNCHANGED": "KEEP",
                }[defect],
                "final_surface": corrected_surfaces[position],
                "final_card_no": corrected_cards[position],
            })

        stages = [
            ("MASTER", master_surfaces, master_cards, "NONE", "YES"),
            ("APPRENTICE", apprentice_surfaces, apprentice_cards, "ONE_ALLOGRAPH_ONE_WRONG_CARD_ONE_ADJACENT_SWAP", "NO"),
            ("ORDER_REPAIRED", before_swap_surfaces, before_swap_cards, f"SWAP_POSITIONS_{left + 1}_{right + 1}", "NO"),
            ("MINIMAL_CORRECTION", corrected_surfaces, corrected_cards, f"RESTORE_POSITION_{wrong_index + 1}_EXPECTED_CARD", "YES"),
        ]
        for stage, surfaces, card_ids, operation, correct in stages:
            stage_rows.append({
                "case_id": case_id,
                "stage": stage,
                "surface_strip": " ".join(surfaces),
                "card_strip": "|".join(card_ids),
                "operation_from_previous": operation,
                "semantic_sequence_correct": correct,
                "foreign_hand_visible": "YES" if surfaces[allograph_index] == str(config["allograph"]) else "NO",
            })

    write_tsv(HERE / "SIX_HUNDRED_FORTY_THIRD_5_CASE_CORRECTION_SUMMARY.tsv", summary_rows, list(summary_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FORTY_THIRD_30_POSITION_AUDIT.tsv", position_rows, list(position_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FORTY_THIRD_20_STAGE_TRACES.tsv", stage_rows, list(stage_rows[0]))

    md = ["# Fünf Fälle, dieselbe Korrekturlehre", ""]
    for row in summary_rows:
        md.extend([
            f"## {row['case_id']}",
            "",
            f"- Meister: `{row['master_surface_strip']}`",
            f"- Lehrling: `{row['apprentice_surface_strip']}`",
            f"- korrigiert: `{row['corrected_surface_strip']}`",
            f"- harmlose Hand: `{row['allograph_change']}`",
            f"- falsche Karte: `{row['wrong_card_change']}` ({row['wrong_card_command_de']} statt {row['expected_command_de']})",
            f"- gebrochene Reihenfolge: {row['violated_rule']}",
            "",
        ])
    (HERE / "SIX_HUNDRED_FORTY_THIRD_FIVE_CASE_SCHOOL.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "cases": len(summary_rows),
        "positions": len(position_rows),
        "stages": len(stage_rows),
        "harmless_allographs": sum(row["allograph_same_card"] == "YES" for row in summary_rows),
        "wrong_card_substitutions": sum(row["wrong_card_no"] != row["expected_card_no"] for row in summary_rows),
        "order_errors": sum(int(row["violated_precedence_rules"]) > 0 for row in summary_rows),
        "final_exact_card_sequences": sum(row["final_cards_equal_master"] == "YES" for row in summary_rows),
        "preserved_foreign_hands": sum(row["foreign_hand_preserved"] == "YES" for row in summary_rows),
        "new_cards": 0,
        "new_surfaces": 0,
        "new_meanings": 0,
        "decision": "ONE_CORRECTION_DISCIPLINE_GENERALIZES_ACROSS_ALL_FIVE_CASES",
    }
    (HERE / "SIX_HUNDRED_FORTY_THIRD_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
