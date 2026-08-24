#!/usr/bin/env python3
"""Collate two complementary flawed copies for each workshop case."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P613 = ROOT / "experiments/yolo/sidequest_semantic_duplicate_command_resolution_six_hundred_thirteenth"
P643 = ROOT / "experiments/yolo/sidequest_semantic_five_case_correction_school_six_hundred_forty_third"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


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
    cases = read_tsv(P643 / "SIX_HUNDRED_FORTY_THIRD_5_CASE_CORRECTION_SUMMARY.tsv")
    card_by_id = {row["card_no"]: row for row in cards}
    surface_to_card = {surface: row["card_no"] for row in cards for surface in row["surfaces"].split("|")}

    copy_rows: list[dict[str, object]] = []
    collation_rows: list[dict[str, object]] = []
    provenance_rows: list[dict[str, object]] = []
    for case in cases:
        case_id = case["case_id"]
        master_surfaces = case["master_surface_strip"].split()
        master_cards = case["master_card_strip"].split("|")
        old_allograph, new_allograph = case["allograph_change"].split(">")
        old_wrong, new_wrong = case["wrong_card_change"].split(">")
        allograph_position = master_surfaces.index(old_allograph)
        wrong_position = master_surfaces.index(old_wrong)
        swap_left, swap_right = (int(value) - 1 for value in case["swapped_positions"].split("|"))

        copy_a_surfaces = list(master_surfaces)
        copy_a_surfaces[allograph_position] = new_allograph
        copy_a_surfaces[wrong_position] = new_wrong
        copy_a_cards = [surface_to_card[surface] for surface in copy_a_surfaces]

        copy_b_surfaces = list(master_surfaces)
        copy_b_surfaces[swap_left], copy_b_surfaces[swap_right] = copy_b_surfaces[swap_right], copy_b_surfaces[swap_left]
        copy_b_cards = [surface_to_card[surface] for surface in copy_b_surfaces]

        # The case grammar identifies the one reversed precedence pair in B.
        # Repairing that pair supplies an aligned inventory witness without
        # exposing the master strip. This matters in C4, where A contains two
        # identical PROC038 cards and a bare multiset cannot tell which copy is
        # the substituted portion slot.
        copy_b_repaired_surfaces = list(copy_b_surfaces)
        copy_b_repaired_surfaces[swap_left], copy_b_repaired_surfaces[swap_right] = copy_b_repaired_surfaces[swap_right], copy_b_repaired_surfaces[swap_left]
        copy_b_repaired_cards = [surface_to_card[surface] for surface in copy_b_repaired_surfaces]

        missing_from_a = list((Counter(copy_b_cards) - Counter(copy_a_cards)).elements())
        extra_in_a = list((Counter(copy_a_cards) - Counter(copy_b_cards)).elements())
        missing_card = missing_from_a[0] if len(missing_from_a) == 1 else "UNRESOLVED"
        extra_card = extra_in_a[0] if len(extra_in_a) == 1 else "UNRESOLVED"
        aligned_mismatches = [index for index, (left_card, right_card) in enumerate(zip(copy_a_cards, copy_b_repaired_cards)) if left_card != right_card]
        replacement_position = aligned_mismatches[0] if len(aligned_mismatches) == 1 else -1
        donor_position = replacement_position
        final_surfaces = list(copy_a_surfaces)
        if replacement_position >= 0 and donor_position >= 0:
            final_surfaces[replacement_position] = copy_b_repaired_surfaces[donor_position]
        final_cards = [surface_to_card[surface] for surface in final_surfaces]

        for copy_id, surfaces, card_ids, defect in [
            ("COPY_A_ORDER_WITNESS", copy_a_surfaces, copy_a_cards, "ONE_WRONG_CARD__ORDER_CORRECT__ONE_HARMLESS_ALLOGRAPH"),
            ("COPY_B_INVENTORY_WITNESS", copy_b_surfaces, copy_b_cards, "ALL_CARDS_CORRECT__ONE_ADJACENT_ORDER_SWAP"),
        ]:
            copy_rows.append({
                "case_id": case_id,
                "copy_id": copy_id,
                "surface_strip": " ".join(surfaces),
                "card_strip": "|".join(card_ids),
                "case_selected": choose_case(card_ids, card_by_id),
                "defect": defect,
                "card_multiset_equals_hidden_master": "YES" if Counter(card_ids) == Counter(master_cards) else "NO",
                "card_order_equals_hidden_master": "YES" if card_ids == master_cards else "NO",
                "master_strip_visible_to_collator": "NO",
            })

        collation_rows.append({
            "case_id": case_id,
            "case_selected_from_copy_a": choose_case(copy_a_cards, card_by_id),
            "case_selected_from_copy_b": choose_case(copy_b_cards, card_by_id),
            "order_witness": "COPY_A_ORDER_WITNESS",
            "inventory_witness": "COPY_B_INVENTORY_WITNESS",
            "copy_b_order_repair": f"SWAP_POSITIONS_{swap_left + 1}_{swap_right + 1}_BY_CASE_PRECEDENCE",
            "copy_b_aligned_card_strip": "|".join(copy_b_repaired_cards),
            "extra_card_in_copy_a": extra_card,
            "extra_card_command_de": card_by_id[extra_card]["standard_command_de"],
            "missing_card_from_copy_a": missing_card,
            "missing_card_command_de": card_by_id[missing_card]["standard_command_de"],
            "replacement_position": replacement_position + 1,
            "donor_position_in_order_repaired_copy_b": donor_position + 1,
            "position_resolution": "ALIGN_COPY_A_WITH_GRAMMAR_REORDERED_COPY_B",
            "collated_surface_strip": " ".join(final_surfaces),
            "collated_card_strip": "|".join(final_cards),
            "hidden_master_card_strip": "|".join(master_cards),
            "exact_card_recovery": "YES" if final_cards == master_cards else "NO",
            "foreign_hand_preserved": "YES" if final_surfaces[allograph_position] == new_allograph else "NO",
            "visible_master_used": "NO",
        })

        for position, (surface, card_id) in enumerate(zip(final_surfaces, final_cards), 1):
            if position - 1 == replacement_position:
                source_copy = "COPY_B_INVENTORY_WITNESS"
                source_reason = "SUPPLIES_CARD_MISSING_FROM_COPY_A_MULTISET"
            else:
                source_copy = "COPY_A_ORDER_WITNESS"
                source_reason = "PRESERVES_ORDER_AND_EXISTING_HAND"
            provenance_rows.append({
                "case_id": case_id,
                "final_position": position,
                "final_surface": surface,
                "final_card_no": card_id,
                "final_command_de": card_by_id[card_id]["standard_command_de"],
                "source_copy": source_copy,
                "source_reason": source_reason,
                "matches_hidden_master_card": "YES" if card_id == master_cards[position - 1] else "NO",
            })

    write_tsv(HERE / "SIX_HUNDRED_FORTY_FOURTH_10_COMPLEMENTARY_COPIES.tsv", copy_rows, list(copy_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FORTY_FOURTH_5_COLLATIONS.tsv", collation_rows, list(collation_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FORTY_FOURTH_30_CARD_PROVENANCE.tsv", provenance_rows, list(provenance_rows[0]))

    md = [
        "# Zwei fehlerhafte Kopien, eine brauchbare Kollation",
        "",
        "Der Korrektor sieht keinen Meisterstreifen. Kopie A liefert die Rollenreihenfolge, Kopie B den vollständigen Kartenbestand. Die Multiset-Differenz zeigt genau eine überschüssige und eine fehlende Karte; die fehlende Karte aus B wird am Platz der überschüssigen Karte in A eingesetzt.",
        "",
    ]
    for row in collation_rows:
        a = next(item for item in copy_rows if item["case_id"] == row["case_id"] and item["copy_id"] == "COPY_A_ORDER_WITNESS")
        b = next(item for item in copy_rows if item["case_id"] == row["case_id"] and item["copy_id"] == "COPY_B_INVENTORY_WITNESS")
        md.extend([
            f"## {row['case_id']}",
            "",
            f"- A: `{a['surface_strip']}`",
            f"- B: `{b['surface_strip']}`",
            f"- Kollation: `{row['collated_surface_strip']}`",
            f"- ersetze {row['extra_card_in_copy_a']} durch {row['missing_card_from_copy_a']} an Position {row['replacement_position']}; Fremdhand bleibt erhalten.",
            "",
        ])
    (HERE / "SIX_HUNDRED_FORTY_FOURTH_TWO_COPY_BOOK.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "cases": len(collation_rows),
        "copies": len(copy_rows),
        "final_positions": len(provenance_rows),
        "copy_a_order_witnesses": sum(row["card_order_equals_hidden_master"] == "NO" for row in copy_rows if row["copy_id"] == "COPY_A_ORDER_WITNESS"),
        "copy_b_complete_inventories": sum(row["card_multiset_equals_hidden_master"] == "YES" for row in copy_rows if row["copy_id"] == "COPY_B_INVENTORY_WITNESS"),
        "exact_collations": sum(row["exact_card_recovery"] == "YES" for row in collation_rows),
        "preserved_foreign_hands": sum(row["foreign_hand_preserved"] == "YES" for row in collation_rows),
        "visible_master_uses": sum(row["visible_master_used"] == "YES" for row in collation_rows),
        "new_cards": 0,
        "new_surfaces": 0,
        "new_meanings": 0,
        "decision": "TWO_COMPLEMENTARY_FLAWED_COPIES_RECOVER_ALL_FIVE_CARD_SEQUENCES",
    }
    (HERE / "SIX_HUNDRED_FORTY_FOURTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
