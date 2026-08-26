#!/usr/bin/env python3
"""Independently validate GDT506 frame reductions and compatibility ranks."""

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
VALIDATION_OUT = ART / "gdt506_validation.json"

PAIR_ORDER = ("P+CH", "S+CHD", "CH+P", "CH+CH", "CH+SH")
TIER_ORDER = (
    "A_LOCAL_ARGUMENT_COMPATIBLE_REDUCTION",
    "B_CROSS_REGISTER_ARGUMENT_COMPATIBLE_REDUCTION",
    "C_ACTION_HANDGRIP_ONLY__ARGUMENT_MODE_OPEN",
)
STATUS = "SEVEN_TARGET_FRAMES_HAVE_ARGUMENT_COMPATIBLE_REDUCTIONS__FOUR_CONTEXTUAL_TRANSFERS_REMAIN_OPEN"
GUARD = "FRAME_COMPATIBILITY_RANK_ONLY__OPEN_CONTEXTUAL_TARGETS_RETAINED_NOT_REJECTED"


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames is None:
            raise ValueError(f"missing header: {path}")
        return list(reader.fieldnames), list(reader)


def alignment(target: list[str], carrier: list[str]) -> list[int] | None:
    result: list[int] = []
    start = 0
    for atom in target:
        try:
            position = carrier.index(atom, start)
        except ValueError:
            return None
        result.append(position)
        start = position + 1
    return result


def compatibility(arguments: list[str], carrier: dict[str, str]) -> tuple[bool, str]:
    if arguments:
        explicit = [] if carrier["explicit_argument_roots"] == "NONE" else carrier["explicit_argument_roots"].split("|")
        return (
            (True, "EXPLICIT_TARGET_ARGUMENTS_PRESENT")
            if all(argument in explicit for argument in arguments)
            else (False, "EXPLICIT_TARGET_ARGUMENT_MISSING")
        )
    if carrier["argument_mode"] == "INHERITED_ARGUMENT":
        return True, "OLD_INHERITED_ARGUMENT"
    if carrier["argument_mode"] == "ARGUMENT_FREE":
        return True, "OLD_ARGUMENT_FREE"
    return False, "OLD_EXPLICIT_ARGUMENT_ONLY"


def main() -> int:
    dict_fields, dictionary = read_tsv(DICTIONARY_IN)
    carrier_fields, carriers = read_tsv(CARRIERS_IN)
    handgrip_fields, handgrips = read_tsv(HANDGRIPS_IN)
    target_fields, targets = read_tsv(TARGETS_IN)
    card_fields, cards = read_tsv(CARDS_OUT)
    candidate_fields, candidates = read_tsv(CANDIDATES_OUT)
    tier_fields, tiers = read_tsv(TIERS_OUT)
    pair_fields, pairs = read_tsv(PAIRS_OUT)
    policy_fields, policies = read_tsv(POLICY_OUT)
    readable = READABLE_OUT.read_text(encoding="utf-8")
    result = json.loads(RESULT_OUT.read_text(encoding="utf-8"))

    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    check("all_table_counts_exact", (len(dictionary), len(carriers), len(handgrips), len(targets), len(cards), len(candidates), len(tiers), len(pairs), len(policies)) == (46, 55, 5, 11, 11, 84, 3, 5, 2), "46/55/5/11 -> 11/84/3/5/2")
    check("input_schemas_complete", {"atom", "working_value_de", "factor_family"} <= set(dict_fields) and {"pair_carrier_id", "argument_mode", "component_recipe"} <= set(carrier_fields) and {"handgrip_id", "ordered_action_pair"} <= set(handgrip_fields) and {"target_handgrip_card_id", "target_action_recipe"} <= set(target_fields), "four input schemas")
    check("output_schemas_complete", {"target_frame_card_id", "compatibility_tier", "selected_reduction_candidate_id"} <= set(card_fields) and {"reduction_candidate_id", "argument_mode_compatible", "removed_carrier_atoms"} <= set(candidate_fields) and {"compatibility_tier", "target_card_count"} <= set(tier_fields) and {"ordered_action_pair", "target_card_count"} <= set(pair_fields) and {"target_argument_policy", "target_card_count"} <= set(policy_fields), "five output schemas")
    check("card_ids_exact", [row["target_frame_card_id"] for row in cards] == [f"G506-T{i:02d}" for i in range(1, 12)], "T01..T11")
    check("candidate_ids_exact", [row["reduction_candidate_id"] for row in candidates] == [f"G506-C{i:03d}" for i in range(1, 85)], "C001..C084")
    check("tier_order_exact", [row["compatibility_tier"] for row in tiers] == list(TIER_ORDER), "three tiers")
    check("pair_order_exact", [row["ordered_action_pair"] for row in pairs] == list(PAIR_ORDER), "five pairs")
    check("policy_order_exact", [row["target_argument_policy"] for row in policies] == ["EXPLICIT_TARGET_ARGUMENTS", "CONTEXTUAL_TARGET_ARGUMENT"], "two policies")

    values = {row["atom"]: row["working_value_de"] for row in dictionary}
    families = {row["atom"]: row["factor_family"] for row in dictionary}
    carriers_by_pair: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in carriers:
        carriers_by_pair[row["ordered_action_pair"]].append(row)
    handgrip_by_pair = {row["ordered_action_pair"]: row for row in handgrips}
    candidates_by_target: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in candidates:
        candidates_by_target[row["source_gdt505_target_card_id"]].append(row)

    expected_candidates: list[dict[str, object]] = []
    expected_by_target: dict[str, list[dict[str, object]]] = defaultdict(list)
    for target in targets:
        target_tokens = target["target_action_recipe"].split("+")
        target_arguments = [atom for atom in target_tokens if families[atom] == "ARGUMENT"]
        policy = "EXPLICIT_TARGET_ARGUMENTS" if target_arguments else "CONTEXTUAL_TARGET_ARGUMENT"
        for carrier in carriers_by_pair[target["ordered_action_pair"]]:
            carrier_tokens = carrier["component_recipe"].split("+")
            positions = alignment(target_tokens, carrier_tokens)
            if positions is None:
                continue
            used = set(positions)
            removed_positions = [index + 1 for index in range(len(carrier_tokens)) if index not in used]
            removed = [atom for index, atom in enumerate(carrier_tokens) if index not in used]
            compatible, reason = compatibility(target_arguments, carrier)
            expected = {
                "target": target,
                "carrier": carrier,
                "positions": positions,
                "removed_positions": removed_positions,
                "removed": removed,
                "compatible": compatible,
                "reason": reason,
                "policy": policy,
                "arguments": target_arguments,
            }
            expected_candidates.append(expected)
            expected_by_target[target["target_handgrip_card_id"]].append(expected)

    check("independent_candidate_total", len(expected_candidates) == 84, f"actual={len(expected_candidates)}")
    for index, (expected, row) in enumerate(zip(expected_candidates, candidates), start=1):
        target = expected["target"]
        carrier = expected["carrier"]
        removed = expected["removed"]
        prefix = f"candidate_{index:03d}"
        check(f"{prefix}_source_exact", row["source_gdt505_target_card_id"] == target["target_handgrip_card_id"] and row["target_action_recipe"] == target["target_action_recipe"] and row["target_register"] == target["target_register"] and row["ordered_action_pair"] == target["ordered_action_pair"] and row["source_pair_carrier_id"] == carrier["pair_carrier_id"] and row["source_event_id"] == carrier["global_running_event_id"], f"{target['target_handgrip_card_id']}/{carrier['pair_carrier_id']}")
        check(f"{prefix}_alignment_exact", row["ordered_target_subsequence_exact"] == "YES" and row["aligned_carrier_positions"] == ",".join(str(position + 1) for position in expected["positions"]) and row["removed_carrier_positions"] == (",".join(str(position) for position in expected["removed_positions"]) or "NONE") and row["removed_carrier_atoms"] == ("+".join(removed) or "NONE") and int(row["removed_carrier_atom_count"]) == len(removed), f"positions={expected['positions']},removed={removed}")
        check(f"{prefix}_values_exact", row["removed_carrier_values_de"] == (" · ".join(values[atom] for atom in removed) or "NONE") and row["target_argument_policy"] == expected["policy"] and row["target_argument_roots"] == ("+".join(expected["arguments"]) or "NONE"), row["removed_carrier_values_de"])
        check(f"{prefix}_argument_exact", row["source_argument_mode"] == carrier["argument_mode"] and row["source_explicit_argument_roots"] == carrier["explicit_argument_roots"] and row["source_inherited_argument_root"] == carrier["inherited_argument_root"] and row["argument_mode_compatible"] == ("YES" if expected["compatible"] else "NO") and row["argument_compatibility_reason"] == expected["reason"], expected["reason"])
        check(f"{prefix}_relation_guard", row["target_register_relation"] == ("SAME_REGISTER" if carrier["register"] == target["target_register"] else "CROSS_REGISTER") and row["direct_pair_in_carrier"] == carrier["direct_component_adjacency"] and row["foreign_frame_transferred"] == row["target_phrase_changed"] == "NO" and row["guard"] == GUARD, GUARD)

    card_by_source = {row["source_gdt505_target_card_id"]: row for row in cards}
    recomputed_card_info: dict[str, dict[str, object]] = {}
    for index, target in enumerate(targets, start=1):
        row = card_by_source[target["target_handgrip_card_id"]]
        group = candidates_by_target[target["target_handgrip_card_id"]]
        compatible = [item for item in group if item["argument_mode_compatible"] == "YES"]
        local = [item for item in compatible if item["target_register_relation"] == "SAME_REGISTER"]
        cross = [item for item in compatible if item["target_register_relation"] == "CROSS_REGISTER"]
        tier = TIER_ORDER[0] if local else TIER_ORDER[1] if compatible else TIER_ORDER[2]
        selected = sorted(group, key=lambda item: (0 if item["argument_mode_compatible"] == "YES" else 1, 0 if item["target_register_relation"] == "SAME_REGISTER" else 1, int(item["removed_carrier_atom_count"]), 0 if item["direct_pair_in_carrier"] == "YES" else 1, item["source_event_id"]))[0]
        target_arguments = [atom for atom in target["target_action_recipe"].split("+") if families[atom] == "ARGUMENT"]
        policy = "EXPLICIT_TARGET_ARGUMENTS" if target_arguments else "CONTEXTUAL_TARGET_ARGUMENT"
        recomputed_card_info[row["target_frame_card_id"]] = {"tier": tier, "group": group, "compatible": compatible, "local": local, "cross": cross, "selected": selected, "policy": policy}
        prefix = f"target_{index:02d}"
        check(f"{prefix}_source_exact", row["target_frame_card_id"] == f"G506-T{index:02d}" and row["source_gdt505_target_card_id"] == target["target_handgrip_card_id"] and row["target_action_recipe"] == target["target_action_recipe"] and row["target_current_default_phrase_de"] == target["target_current_default_phrase_de"], target["target_handgrip_card_id"])
        check(f"{prefix}_counts_exact", int(row["ordered_reduction_candidate_count"]) == len(group) and int(row["argument_compatible_candidate_count"]) == len(compatible) and int(row["local_argument_compatible_candidate_count"]) == len(local) and int(row["cross_argument_compatible_candidate_count"]) == len(cross), f"{len(group)}/{len(compatible)}/{len(local)}/{len(cross)}")
        check(f"{prefix}_tier_exact", row["compatibility_tier"] == tier and row["target_argument_policy"] == policy and row["target_argument_roots"] == ("+".join(target_arguments) or "NONE"), tier)
        check(f"{prefix}_selection_exact", row["selected_reduction_candidate_id"] == selected["reduction_candidate_id"] and row["selected_source_event_id"] == selected["source_event_id"] and row["selected_source_recipe"] == selected["source_component_recipe"] and row["selected_removed_carrier_atoms"] == selected["removed_carrier_atoms"] and int(row["selected_removed_carrier_atom_count"]) == int(selected["removed_carrier_atom_count"]), selected["reduction_candidate_id"])
        check(f"{prefix}_guards_exact", row["assumption_retained"] == "YES" and row["target_phrase_changed"] == row["working_root_meaning_changed"] == row["surface_prediction_made"] == row["occurrence_prediction_made"] == "NO" and row["target_evidence_status_retained"] == "COMPOSED_WORKING" and row["guard"] == GUARD, GUARD)
        check(f"{prefix}_readable", row["target_current_default_phrase_de"] in readable and tier in readable and row["selected_source_recipe"] in readable, target["target_handgrip_card_id"])

    rank_order = sorted(cards, key=lambda row: (TIER_ORDER.index(row["compatibility_tier"]), -int(row["local_argument_compatible_candidate_count"]), -int(row["argument_compatible_candidate_count"]), int(row["selected_removed_carrier_atom_count"]), -int(row["old_pair_carrier_event_count"]), row["target_frame_card_id"]))
    expected_ranks = {row["target_frame_card_id"]: index for index, row in enumerate(rank_order, start=1)}
    check("priority_ranks_exact", all(int(row["compatibility_priority_rank"]) == expected_ranks[row["target_frame_card_id"]] for row in cards), str(expected_ranks))

    tier_by_name = {row["compatibility_tier"]: row for row in tiers}
    for tier in TIER_ORDER:
        group = [row for row in cards if row["compatibility_tier"] == tier]
        source_ids = {row["source_gdt505_target_card_id"] for row in group}
        group_candidates = [row for row in candidates if row["source_gdt505_target_card_id"] in source_ids]
        summary = tier_by_name[tier]
        check(f"tier_{tier}", int(summary["target_card_count"]) == len(group) and int(summary["ordered_reduction_candidate_count"]) == len(group_candidates) and int(summary["argument_compatible_candidate_count"]) == sum(row["argument_mode_compatible"] == "YES" for row in group_candidates) and int(summary["local_argument_compatible_candidate_count"]) == sum(row["argument_mode_compatible"] == "YES" and row["target_register_relation"] == "SAME_REGISTER" for row in group_candidates) and summary["all_assumptions_retained"] == "YES" and summary["guard"] == GUARD, f"cards={len(group)}")

    pair_by_name = {row["ordered_action_pair"]: row for row in pairs}
    for pair in PAIR_ORDER:
        group = [row for row in cards if row["ordered_action_pair"] == pair]
        source_ids = {row["source_gdt505_target_card_id"] for row in group}
        group_candidates = [row for row in candidates if row["source_gdt505_target_card_id"] in source_ids]
        summary = pair_by_name[pair]
        check(f"pair_{pair}", summary["carrier_neutral_handgrip_de"] == handgrip_by_pair[pair]["carrier_neutral_handgrip_de"] and int(summary["old_pair_carrier_event_count"]) == int(handgrip_by_pair[pair]["old_carrier_event_count"]) and int(summary["target_card_count"]) == len(group) and int(summary["ordered_reduction_candidate_count"]) == len(group_candidates) and int(summary["argument_compatible_candidate_count"]) == sum(row["argument_mode_compatible"] == "YES" for row in group_candidates) and summary["all_assumptions_retained"] == "YES" and summary["guard"] == GUARD, f"cards={len(group)}")

    policy_by_name = {row["target_argument_policy"]: row for row in policies}
    for policy in ("EXPLICIT_TARGET_ARGUMENTS", "CONTEXTUAL_TARGET_ARGUMENT"):
        group = [row for row in cards if row["target_argument_policy"] == policy]
        summary = policy_by_name[policy]
        check(f"policy_{policy}", int(summary["target_card_count"]) == len(group) and int(summary["cards_with_any_argument_compatible_reduction"]) == sum(int(row["argument_compatible_candidate_count"]) > 0 for row in group) and int(summary["cards_with_local_argument_compatible_reduction"]) == sum(int(row["local_argument_compatible_candidate_count"]) > 0 for row in group) and int(summary["open_argument_mode_card_count"]) == sum(row["compatibility_tier"] == TIER_ORDER[2] for row in group) and summary["all_assumptions_retained"] == "YES" and summary["guard"] == GUARD, f"cards={len(group)}")

    expected_result = {
        "status": STATUS,
        "target_frame_cards": 11,
        "ordered_reduction_candidates": 84,
        "ordered_target_subsequences_exact": 84,
        "argument_compatible_candidates": 40,
        "local_argument_compatible_candidates": 7,
        "cross_argument_compatible_candidates": 33,
        "tier_a_local_target_cards": 3,
        "tier_b_cross_target_cards": 4,
        "tier_c_open_argument_mode_cards": 4,
        "explicit_target_argument_cards": 5,
        "contextual_target_argument_cards": 6,
        "contextual_cards_with_compatible_old_mode": 2,
        "contextual_cards_without_compatible_old_mode": 4,
        "selected_removed_carrier_atoms": 19,
        "assumptions_retained": 11,
        "target_phrase_changes": 0,
        "working_root_meaning_changes": 0,
        "surface_predictions": 0,
        "occurrence_predictions": 0,
        "guard": GUARD,
    }
    check("result_exact", result == expected_result, json.dumps(expected_result, ensure_ascii=False, sort_keys=True))
    check("readable_status_guard_exact", STATUS in readable and GUARD in readable, "status and guard")

    failed = [item for item in checks if not item["passed"]]
    payload = {
        "status": "PASS" if not failed else "FAIL",
        "checks_total": len(checks),
        "checks_passed": len(checks) - len(failed),
        "checks_failed": len(failed),
        "failed_checks": failed,
    }
    VALIDATION_OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
