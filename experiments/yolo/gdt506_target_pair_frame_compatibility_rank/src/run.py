#!/usr/bin/env python3
"""Rank eleven pair targets by old frame reduction and argument compatibility."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt506_target_pair_frame_compatibility_rank"
ART = BASE / "artifacts"
G413 = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts"
G505 = ROOT / "experiments/yolo/gdt505_carrier_neutral_pair_handgrip_atlas/artifacts"

DICTIONARY_IN = G413 / "gdt413_46_component_working_dictionary.tsv"
CARRIERS_IN = G505 / "gdt505_55_exact_pair_carriers.tsv"
HANDGRIPS_IN = G505 / "gdt505_5_carrier_neutral_handgrips.tsv"
TARGETS_IN = G505 / "gdt505_11_target_pair_handgrip_cards.tsv"

CARDS_OUT = ART / "gdt506_11_target_frame_compatibility_cards.tsv"
CANDIDATES_OUT = ART / "gdt506_84_ordered_reduction_candidates.tsv"
TIERS_OUT = ART / "gdt506_3_frame_compatibility_tier_summary.tsv"
PAIRS_OUT = ART / "gdt506_5_pair_frame_profile.tsv"
POLICY_OUT = ART / "gdt506_2_target_argument_policy_summary.tsv"
READABLE_OUT = ART / "GDT506_TARGET_PAIR_FRAME_COMPATIBILITY_RANK.md"
RESULT_OUT = ART / "gdt506_result.json"

ACTION_ROOTS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
PAIR_ORDER = ("P+CH", "S+CHD", "CH+P", "CH+CH", "CH+SH")
TIER_ORDER = (
    "A_LOCAL_ARGUMENT_COMPATIBLE_REDUCTION",
    "B_CROSS_REGISTER_ARGUMENT_COMPATIBLE_REDUCTION",
    "C_ACTION_HANDGRIP_ONLY__ARGUMENT_MODE_OPEN",
)
TIER_NOTE_DE = {
    "A_LOCAL_ARGUMENT_COMPATIBLE_REDUCTION": "Ein alter Träger im Zielregister reduziert auf das Zielrezept und hat denselben Argumentmodus.",
    "B_CROSS_REGISTER_ARGUMENT_COMPATIBLE_REDUCTION": "Die passende Rahmenreduktion ist alt, aber nur in einem anderen Register.",
    "C_ACTION_HANDGRIP_ONLY__ARGUMENT_MODE_OPEN": "Die Handlungskette ist alt; alte Träger nennen jedoch Argumente explizit, während das Ziel sie aus dem Kontext erbt.",
}
STATUS = "SEVEN_TARGET_FRAMES_HAVE_ARGUMENT_COMPATIBLE_REDUCTIONS__FOUR_CONTEXTUAL_TRANSFERS_REMAIN_OPEN"
GUARD = "FRAME_COMPATIBILITY_RANK_ONLY__OPEN_CONTEXTUAL_TARGETS_RETAINED_NOT_REJECTED"


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


def subsequence_alignment(target: list[str], carrier: list[str]) -> list[tuple[int, int]] | None:
    alignment: list[tuple[int, int]] = []
    start = 0
    for target_index, atom in enumerate(target):
        try:
            carrier_index = carrier.index(atom, start)
        except ValueError:
            return None
        alignment.append((target_index, carrier_index))
        start = carrier_index + 1
    return alignment


def argument_compatibility(
    target_arguments: list[str], carrier: dict[str, str]
) -> tuple[bool, str]:
    if target_arguments:
        explicit = [] if carrier["explicit_argument_roots"] == "NONE" else carrier["explicit_argument_roots"].split("|")
        if all(argument in explicit for argument in target_arguments):
            return True, "EXPLICIT_TARGET_ARGUMENTS_PRESENT"
        return False, "EXPLICIT_TARGET_ARGUMENT_MISSING"
    if carrier["argument_mode"] == "INHERITED_ARGUMENT":
        return True, "OLD_INHERITED_ARGUMENT"
    if carrier["argument_mode"] == "ARGUMENT_FREE":
        return True, "OLD_ARGUMENT_FREE"
    return False, "OLD_EXPLICIT_ARGUMENT_ONLY"


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    _dictionary_fields, dictionary = read_tsv(DICTIONARY_IN)
    _carrier_fields, carriers = read_tsv(CARRIERS_IN)
    _handgrip_fields, handgrips = read_tsv(HANDGRIPS_IN)
    _target_fields, targets = read_tsv(TARGETS_IN)
    if (len(dictionary), len(carriers), len(handgrips), len(targets)) != (46, 55, 5, 11):
        raise ValueError("GDT413/GDT505 source drift")

    values = {row["atom"]: row["working_value_de"] for row in dictionary}
    families = {row["atom"]: row["factor_family"] for row in dictionary}
    handgrip_by_pair = {row["ordered_action_pair"]: row for row in handgrips}
    carriers_by_pair: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in carriers:
        carriers_by_pair[row["ordered_action_pair"]].append(row)

    candidates: list[dict[str, object]] = []
    candidates_by_target: dict[str, list[dict[str, object]]] = defaultdict(list)
    target_meta: dict[str, dict[str, object]] = {}
    for target in targets:
        target_tokens = target["target_action_recipe"].split("+")
        target_arguments = [atom for atom in target_tokens if families[atom] == "ARGUMENT"]
        target_policy = "EXPLICIT_TARGET_ARGUMENTS" if target_arguments else "CONTEXTUAL_TARGET_ARGUMENT"
        target_meta[target["target_handgrip_card_id"]] = {
            "arguments": target_arguments,
            "policy": target_policy,
        }
        for carrier in carriers_by_pair[target["ordered_action_pair"]]:
            carrier_tokens = carrier["component_recipe"].split("+")
            alignment = subsequence_alignment(target_tokens, carrier_tokens)
            if alignment is None:
                continue
            used = {carrier_index for _target_index, carrier_index in alignment}
            removed_positions = [index + 1 for index in range(len(carrier_tokens)) if index not in used]
            removed = [atom for index, atom in enumerate(carrier_tokens) if index not in used]
            compatible, reason = argument_compatibility(target_arguments, carrier)
            same_register = carrier["register"] == target["target_register"]
            candidate = {
                "reduction_candidate_id": f"G506-C{len(candidates) + 1:03d}",
                "source_gdt505_target_card_id": target["target_handgrip_card_id"],
                "target_matrix_cell_id": target["target_matrix_cell_id"],
                "target_action_recipe": target["target_action_recipe"],
                "target_register": target["target_register"],
                "ordered_action_pair": target["ordered_action_pair"],
                "target_argument_policy": target_policy,
                "target_argument_roots": "+".join(target_arguments) if target_arguments else "NONE",
                "source_pair_carrier_id": carrier["pair_carrier_id"],
                "source_event_id": carrier["global_running_event_id"],
                "source_register": carrier["register"],
                "source_component_recipe": carrier["component_recipe"],
                "source_argument_mode": carrier["argument_mode"],
                "source_explicit_argument_roots": carrier["explicit_argument_roots"],
                "source_inherited_argument_root": carrier["inherited_argument_root"],
                "ordered_target_subsequence_exact": "YES",
                "aligned_carrier_positions": ",".join(str(carrier_index + 1) for _target_index, carrier_index in alignment),
                "removed_carrier_positions": ",".join(str(position) for position in removed_positions) if removed_positions else "NONE",
                "removed_carrier_atoms": "+".join(removed) if removed else "NONE",
                "removed_carrier_values_de": " · ".join(values[atom] for atom in removed) if removed else "NONE",
                "removed_carrier_atom_count": len(removed),
                "argument_mode_compatible": "YES" if compatible else "NO",
                "argument_compatibility_reason": reason,
                "target_register_relation": "SAME_REGISTER" if same_register else "CROSS_REGISTER",
                "direct_pair_in_carrier": carrier["direct_component_adjacency"],
                "carrier_neutral_handgrip_de": target["carrier_neutral_handgrip_de"],
                "foreign_frame_transferred": "NO",
                "target_phrase_changed": "NO",
                "guard": GUARD,
            }
            candidates.append(candidate)
            candidates_by_target[target["target_handgrip_card_id"]].append(candidate)

    if len(candidates) != 84:
        raise ValueError(f"expected 84 ordered reduction candidates, got {len(candidates)}")

    cards: list[dict[str, object]] = []
    for target in targets:
        group = candidates_by_target[target["target_handgrip_card_id"]]
        compatible = [row for row in group if row["argument_mode_compatible"] == "YES"]
        local_compatible = [row for row in compatible if row["target_register_relation"] == "SAME_REGISTER"]
        cross_compatible = [row for row in compatible if row["target_register_relation"] == "CROSS_REGISTER"]
        if local_compatible:
            tier = "A_LOCAL_ARGUMENT_COMPATIBLE_REDUCTION"
        elif compatible:
            tier = "B_CROSS_REGISTER_ARGUMENT_COMPATIBLE_REDUCTION"
        else:
            tier = "C_ACTION_HANDGRIP_ONLY__ARGUMENT_MODE_OPEN"

        selected = sorted(
            group,
            key=lambda row: (
                0 if row["argument_mode_compatible"] == "YES" else 1,
                0 if row["target_register_relation"] == "SAME_REGISTER" else 1,
                int(row["removed_carrier_atom_count"]),
                0 if row["direct_pair_in_carrier"] == "YES" else 1,
                str(row["source_event_id"]),
            ),
        )[0]
        meta = target_meta[target["target_handgrip_card_id"]]
        cards.append({
            "target_frame_card_id": f"G506-T{len(cards) + 1:02d}",
            "source_gdt505_target_card_id": target["target_handgrip_card_id"],
            "target_matrix_cell_id": target["target_matrix_cell_id"],
            "target_action_recipe": target["target_action_recipe"],
            "target_register": target["target_register"],
            "ordered_action_pair": target["ordered_action_pair"],
            "carrier_neutral_handgrip_de": target["carrier_neutral_handgrip_de"],
            "target_current_default_phrase_de": target["target_current_default_phrase_de"],
            "target_argument_policy": meta["policy"],
            "target_argument_roots": "+".join(meta["arguments"]) if meta["arguments"] else "NONE",
            "old_pair_carrier_event_count": target["old_pair_carrier_event_count"],
            "ordered_reduction_candidate_count": len(group),
            "argument_compatible_candidate_count": len(compatible),
            "local_argument_compatible_candidate_count": len(local_compatible),
            "cross_argument_compatible_candidate_count": len(cross_compatible),
            "target_register_old_pair_event_count": target["target_register_old_pair_event_count"],
            "compatibility_tier": tier,
            "tier_reading_de": TIER_NOTE_DE[tier],
            "selected_reduction_candidate_id": selected["reduction_candidate_id"],
            "selected_source_event_id": selected["source_event_id"],
            "selected_source_register": selected["source_register"],
            "selected_source_recipe": selected["source_component_recipe"],
            "selected_source_argument_mode": selected["source_argument_mode"],
            "selected_removed_carrier_atoms": selected["removed_carrier_atoms"],
            "selected_removed_carrier_values_de": selected["removed_carrier_values_de"],
            "selected_removed_carrier_atom_count": selected["removed_carrier_atom_count"],
            "assumption_retained": "YES",
            "target_phrase_changed": "NO",
            "target_evidence_status_retained": target["target_evidence_status_retained"],
            "working_root_meaning_changed": "NO",
            "surface_prediction_made": "NO",
            "occurrence_prediction_made": "NO",
            "guard": GUARD,
        })

    rank_order = sorted(
        cards,
        key=lambda row: (
            TIER_ORDER.index(str(row["compatibility_tier"])),
            -int(row["local_argument_compatible_candidate_count"]),
            -int(row["argument_compatible_candidate_count"]),
            int(row["selected_removed_carrier_atom_count"]),
            -int(row["old_pair_carrier_event_count"]),
            str(row["target_frame_card_id"]),
        ),
    )
    rank_by_id = {row["target_frame_card_id"]: index for index, row in enumerate(rank_order, start=1)}
    for row in cards:
        row["compatibility_priority_rank"] = rank_by_id[str(row["target_frame_card_id"])]

    tier_rows: list[dict[str, object]] = []
    for tier in TIER_ORDER:
        group = [row for row in cards if row["compatibility_tier"] == tier]
        candidate_ids = {row["source_gdt505_target_card_id"] for row in group}
        group_candidates = [row for row in candidates if row["source_gdt505_target_card_id"] in candidate_ids]
        tier_rows.append({
            "compatibility_tier": tier,
            "target_card_count": len(group),
            "target_frame_card_ids": "|".join(str(row["target_frame_card_id"]) for row in group),
            "ordered_reduction_candidate_count": len(group_candidates),
            "argument_compatible_candidate_count": sum(row["argument_mode_compatible"] == "YES" for row in group_candidates),
            "local_argument_compatible_candidate_count": sum(row["argument_mode_compatible"] == "YES" and row["target_register_relation"] == "SAME_REGISTER" for row in group_candidates),
            "selected_removed_carrier_atom_count": sum(int(row["selected_removed_carrier_atom_count"]) for row in group),
            "tier_reading_de": TIER_NOTE_DE[tier],
            "all_assumptions_retained": "YES",
            "guard": GUARD,
        })

    pair_rows: list[dict[str, object]] = []
    for pair in PAIR_ORDER:
        pair_cards = [row for row in cards if row["ordered_action_pair"] == pair]
        pair_card_ids = {row["source_gdt505_target_card_id"] for row in pair_cards}
        pair_candidates = [row for row in candidates if row["source_gdt505_target_card_id"] in pair_card_ids]
        handgrip = handgrip_by_pair[pair]
        pair_rows.append({
            "ordered_action_pair": pair,
            "carrier_neutral_handgrip_de": handgrip["carrier_neutral_handgrip_de"],
            "old_pair_carrier_event_count": handgrip["old_carrier_event_count"],
            "target_card_count": len(pair_cards),
            "ordered_reduction_candidate_count": len(pair_candidates),
            "argument_compatible_candidate_count": sum(row["argument_mode_compatible"] == "YES" for row in pair_candidates),
            "local_argument_compatible_candidate_count": sum(row["argument_mode_compatible"] == "YES" and row["target_register_relation"] == "SAME_REGISTER" for row in pair_candidates),
            "tier_a_target_count": sum(row["compatibility_tier"] == TIER_ORDER[0] for row in pair_cards),
            "tier_b_target_count": sum(row["compatibility_tier"] == TIER_ORDER[1] for row in pair_cards),
            "tier_c_target_count": sum(row["compatibility_tier"] == TIER_ORDER[2] for row in pair_cards),
            "all_assumptions_retained": "YES",
            "guard": GUARD,
        })

    policy_rows: list[dict[str, object]] = []
    for policy in ("EXPLICIT_TARGET_ARGUMENTS", "CONTEXTUAL_TARGET_ARGUMENT"):
        group = [row for row in cards if row["target_argument_policy"] == policy]
        policy_rows.append({
            "target_argument_policy": policy,
            "target_card_count": len(group),
            "cards_with_any_argument_compatible_reduction": sum(int(row["argument_compatible_candidate_count"]) > 0 for row in group),
            "cards_with_local_argument_compatible_reduction": sum(int(row["local_argument_compatible_candidate_count"]) > 0 for row in group),
            "open_argument_mode_card_count": sum(row["compatibility_tier"] == TIER_ORDER[2] for row in group),
            "ordered_reduction_candidate_count": sum(int(row["ordered_reduction_candidate_count"]) for row in group),
            "argument_compatible_candidate_count": sum(int(row["argument_compatible_candidate_count"]) for row in group),
            "all_assumptions_retained": "YES",
            "guard": GUARD,
        })

    write_tsv(CARDS_OUT, cards)
    write_tsv(CANDIDATES_OUT, candidates)
    write_tsv(TIERS_OUT, tier_rows)
    write_tsv(PAIRS_OUT, pair_rows)
    write_tsv(POLICY_OUT, policy_rows)

    lines = [
        "# GDT506 — Rahmenverträglichkeit der elf Paarziele",
        "",
        f"Status: `{STATUS}`",
        "",
        "Jedes Zielrezept wird als geordnete Teilfolge aller alten Träger seines",
        "Handgriffs gesucht. Zusätzlich muss der alte Argumentmodus zum Ziel",
        "passen. Eine offene Karte bleibt als Annahme erhalten.",
        "",
        "## Elf Karten in Prioritätsreihenfolge",
        "",
    ]
    for row in rank_order:
        lines.extend([
            f'### Rang {rank_by_id[str(row["target_frame_card_id"])]} · {row["target_frame_card_id"]} · `{row["target_action_recipe"]}` · {row["target_register"]}',
            "",
            f'**{row["target_current_default_phrase_de"]}**',
            "",
            f'- Tier: `{row["compatibility_tier"]}` — {row["tier_reading_de"]}',
            f'- Reduktionen: {row["ordered_reduction_candidate_count"]}; argumentverträglich: {row["argument_compatible_candidate_count"]}; davon lokal: {row["local_argument_compatible_candidate_count"]}.',
            f'- Bester alter Träger: `{row["selected_source_recipe"]}` · {row["selected_source_register"]}; entfernt `{row["selected_removed_carrier_atoms"]}`.',
            "",
        ])
    lines.extend(["## Arbeitsentscheidung", ""])
    lines.extend([
        "Drei Zielkarten haben eine lokale argumentverträgliche Reduktion, vier",
        "eine solche Reduktion nur in einem anderen Register. Vier Karten",
        "(`CH+CH` und `CH+SH` in Source/Pharma) behalten ihren Handgriff, aber",
        "kein alter Träger zeigt dort den Wechsel von explizitem zum geerbten",
        "Argument. Diese Annahmen bleiben stehen, werden jedoch separat markiert.",
        "",
        f"`{GUARD}`",
        "",
    ])
    READABLE_OUT.write_text("\n".join(lines), encoding="utf-8")

    result = {
        "status": STATUS,
        "target_frame_cards": len(cards),
        "ordered_reduction_candidates": len(candidates),
        "ordered_target_subsequences_exact": sum(row["ordered_target_subsequence_exact"] == "YES" for row in candidates),
        "argument_compatible_candidates": sum(row["argument_mode_compatible"] == "YES" for row in candidates),
        "local_argument_compatible_candidates": sum(row["argument_mode_compatible"] == "YES" and row["target_register_relation"] == "SAME_REGISTER" for row in candidates),
        "cross_argument_compatible_candidates": sum(row["argument_mode_compatible"] == "YES" and row["target_register_relation"] == "CROSS_REGISTER" for row in candidates),
        "tier_a_local_target_cards": sum(row["compatibility_tier"] == TIER_ORDER[0] for row in cards),
        "tier_b_cross_target_cards": sum(row["compatibility_tier"] == TIER_ORDER[1] for row in cards),
        "tier_c_open_argument_mode_cards": sum(row["compatibility_tier"] == TIER_ORDER[2] for row in cards),
        "explicit_target_argument_cards": sum(row["target_argument_policy"] == "EXPLICIT_TARGET_ARGUMENTS" for row in cards),
        "contextual_target_argument_cards": sum(row["target_argument_policy"] == "CONTEXTUAL_TARGET_ARGUMENT" for row in cards),
        "contextual_cards_with_compatible_old_mode": sum(row["target_argument_policy"] == "CONTEXTUAL_TARGET_ARGUMENT" and int(row["argument_compatible_candidate_count"]) > 0 for row in cards),
        "contextual_cards_without_compatible_old_mode": sum(row["target_argument_policy"] == "CONTEXTUAL_TARGET_ARGUMENT" and int(row["argument_compatible_candidate_count"]) == 0 for row in cards),
        "selected_removed_carrier_atoms": sum(int(row["selected_removed_carrier_atom_count"]) for row in cards),
        "assumptions_retained": sum(row["assumption_retained"] == "YES" for row in cards),
        "target_phrase_changes": 0,
        "working_root_meaning_changes": 0,
        "surface_predictions": 0,
        "occurrence_predictions": 0,
        "guard": GUARD,
    }
    RESULT_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
