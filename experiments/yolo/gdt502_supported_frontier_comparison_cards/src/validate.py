#!/usr/bin/env python3
"""Independently validate the GDT502 supported-frontier comparison cards."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt502_supported_frontier_comparison_cards"
ART = BASE / "artifacts"
G416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts"
G501 = ROOT / "experiments/yolo/gdt501_old_value_frontier_partial_support_atlas/artifacts"

CLAUSES_IN = G416 / "gdt416_4576_imperative_clauses.tsv"
RANKED_IN = G501 / "gdt501_50_ranked_frontier_cells.tsv"
CANDIDATE_IN = G501 / "gdt501_partial_subrecipe_candidates.tsv"
WITNESS_IN = G501 / "gdt501_exact_partial_recipe_witnesses.tsv"
PAIR_IN = G501 / "gdt501_ordered_action_pair_support.tsv"
CARDS_OUT = ART / "gdt502_46_supported_frontier_cards.tsv"
SELECTED_OUT = ART / "gdt502_46_selected_old_clause_witnesses.tsv"
OPEN_OUT = ART / "gdt502_4_open_frontier_cards.tsv"
CHANNEL_OUT = ART / "gdt502_support_channel_coverage.tsv"
FRAME_OUT = ART / "gdt502_5_frame_card_coverage.tsv"
READABLE_OUT = ART / "GDT502_FORTY_SIX_SUPPORTED_FRONTIER_COMPARISON_CARDS.md"
RESULT_OUT = ART / "gdt502_result.json"
VALIDATION_OUT = ART / "gdt502_validation.json"

ACTION_ROOTS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
CHANNEL_ORDER = {
    "LOCAL_NEAR_ACTION_RECIPE": 0,
    "LOCAL_ACTION_PARTIAL_RECIPE": 1,
    "ORDERED_PAIR_TARGET_REGISTER": 2,
    "CROSS_NEAR_ACTION_RECIPE": 3,
    "ORDERED_PAIR_OTHER_REGISTER": 4,
    "CROSS_ACTION_PARTIAL_RECIPE": 5,
    "LOCAL_FRAME_BACKBONE_RECIPE": 6,
}
STATUS = "FORTY_SIX_SUPPORTED_FRONTIER_CARDS_HAVE_CONCRETE_OLD_CLAUSES__FOUR_OPEN_EDGES_RETAINED"
GUARD = "COMPARISON_CARD_ONLY__CURRENT_TARGET_PHRASE_AND_COMPOSED_STATUS_RETAINED"


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames is None:
            raise ValueError(f"missing header: {path}")
        return list(reader.fieldnames), list(reader)


def page_key(page: str) -> tuple[int, int, int, str]:
    match = re.fullmatch(r"f(\d+)([rv])(\d*)", page)
    if match:
        return int(match.group(1)), 0 if match.group(2) == "r" else 1, int(match.group(3) or 0), page
    return 10**9, 0, 0, page


def select_phrase(rows: list[dict[str, str]]) -> tuple[str, int]:
    counts = Counter(row["imperative_clause_de"] for row in rows)
    return sorted(counts.items(), key=lambda item: (-item[1], len(item[0].split()), len(item[0]), item[0]))[0]


def expected_payload(rows: list[dict[str, str]]) -> dict[str, str]:
    selected, carriers = select_phrase(rows)
    pages = sorted({row["physical_page"] for row in rows}, key=page_key)
    return {
        "support_event_count": str(len(rows)),
        "support_clause_form_count": str(len({row["imperative_clause_de"] for row in rows})),
        "selected_old_clause_de": selected,
        "selected_old_clause_carrier_count": str(carriers),
        "all_old_clauses_de": " || ".join(sorted({row["imperative_clause_de"] for row in rows})),
        "support_event_ids": "|".join(row["global_running_event_id"] for row in rows),
        "support_pages": "|".join(pages),
        "support_page_count": str(len(pages)),
        "support_surfaces": "|".join(sorted({row["surface"] for row in rows})),
        "support_surface_count": str(len({row["surface"] for row in rows})),
        "support_roundtrip_exact": "YES" if all(row["roundtrip_exact"] == "YES" for row in rows) else "NO",
    }


def main() -> int:
    _clause_fields, clauses = read_tsv(CLAUSES_IN)
    _ranked_fields, ranked = read_tsv(RANKED_IN)
    _candidate_fields, candidates = read_tsv(CANDIDATE_IN)
    _witness_fields, witnesses = read_tsv(WITNESS_IN)
    _pair_fields, pairs = read_tsv(PAIR_IN)
    card_fields, cards = read_tsv(CARDS_OUT)
    selected_fields, selected = read_tsv(SELECTED_OUT)
    open_fields, open_cards = read_tsv(OPEN_OUT)
    _channel_fields, channel_rows = read_tsv(CHANNEL_OUT)
    _frame_fields, frame_rows = read_tsv(FRAME_OUT)
    readable = READABLE_OUT.read_text(encoding="utf-8")
    result = json.loads(RESULT_OUT.read_text(encoding="utf-8"))

    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    counts = (len(clauses), len(ranked), len(candidates), len(witnesses), len(pairs), len(cards), len(selected), len(open_cards), len(channel_rows), len(frame_rows))
    check("all_table_counts_exact", counts == (4576, 50, 167, 285, 30, 46, 46, 4, 6, 5), f"actual={counts}")
    check("card_schema_complete", {"comparison_card_id", "support_channel", "selected_old_clause_de"} <= set(card_fields), f"fields={len(card_fields)}")
    check("selected_schema_complete", {"selected_witness_id", "comparison_card_id", "support_event_ids"} <= set(selected_fields), f"fields={len(selected_fields)}")
    check("open_schema_complete", {"open_card_id", "assumption_retained", "open_reason"} <= set(open_fields), f"fields={len(open_fields)}")
    check("card_ids_exact", [row["comparison_card_id"] for row in cards] == [f"G502-F{i:02d}" for i in range(1, 47)], "F01..F46")
    check("selected_ids_exact", [row["selected_witness_id"] for row in selected] == [f"G502-W{i:02d}" for i in range(1, 47)], "W01..W46")
    check("open_ids_exact", [row["open_card_id"] for row in open_cards] == [f"G502-O{i:02d}" for i in range(1, 5)], "O01..O04")

    supported = [row for row in ranked if row["frontier_support_tier"] != "D_ATOMIC_VALUES_ONLY"]
    opened = [row for row in ranked if row["frontier_support_tier"] == "D_ATOMIC_VALUES_ONLY"]
    check("supported_target_order_exact", [row["target_matrix_cell_id"] for row in cards] == [row["source_matrix_cell_id"] for row in supported], "46 GDT501 order")
    check("open_target_order_exact", [row["target_matrix_cell_id"] for row in open_cards] == [row["source_matrix_cell_id"] for row in opened], "4 GDT501 order")

    candidates_by_target: dict[str, list[dict[str, str]]] = defaultdict(list)
    witnesses_by_candidate: dict[str, list[dict[str, str]]] = defaultdict(list)
    pair_by_target = {row["target_matrix_cell_id"]: row for row in pairs}
    clauses_by_recipe_register: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    pair_groups: dict[str, dict[tuple[str, str], list[dict[str, str]]]] = defaultdict(lambda: defaultdict(list))
    for row in candidates:
        candidates_by_target[row["target_matrix_cell_id"]].append(row)
    for row in witnesses:
        witnesses_by_candidate[row["partial_candidate_id"]].append(row)
    for row in clauses:
        clauses_by_recipe_register[(row["component_recipe"], row["register"])].append(row)
        roots = row["explicit_action_roots"].split("|")
        if len(roots) == 2:
            pair_groups["+".join(roots)][(row["component_recipe"], row["register"])].append(row)

    selected_by_card = {row["comparison_card_id"]: row for row in selected}
    for index, (target, card) in enumerate(zip(supported, cards), start=1):
        options: list[dict[str, object]] = []
        for candidate in candidates_by_target[target["source_matrix_cell_id"]]:
            carrier_links = witnesses_by_candidate[candidate["partial_candidate_id"]]
            local = [row for row in carrier_links if row["witness_relation"] == "SAME_REGISTER"]
            cross = [row for row in carrier_links if row["witness_relation"] == "CROSS_REGISTER"]
            contains_action = candidate["contains_target_action_root"] == "YES"
            near = candidate["near_single_deletion"] == "YES"
            if local and contains_action:
                options.append({"channel": "LOCAL_NEAR_ACTION_RECIPE" if near else "LOCAL_ACTION_PARTIAL_RECIPE", "candidate": candidate, "witness": local[0]})
            if cross and contains_action:
                witness = sorted(cross, key=lambda row: (-int(row["observed_event_count"]), -int(row["observed_clause_form_count"]), -int(row["observed_page_count"]), row["witness_register"]))[0]
                options.append({"channel": "CROSS_NEAR_ACTION_RECIPE" if near else "CROSS_ACTION_PARTIAL_RECIPE", "candidate": candidate, "witness": witness})
            if local and not contains_action:
                options.append({"channel": "LOCAL_FRAME_BACKBONE_RECIPE", "candidate": candidate, "witness": local[0]})
        pair = pair_by_target.get(target["source_matrix_cell_id"])
        if pair and pair["pair_status"] == "PAIR_ATTESTED":
            channel = "ORDERED_PAIR_TARGET_REGISTER" if pair["pair_attested_in_target_register"] == "YES" else "ORDERED_PAIR_OTHER_REGISTER"
            key, rows = sorted(
                pair_groups[pair["ordered_action_pair"]].items(),
                key=lambda item: (0 if item[0][1] == target["register"] else 1, len(item[0][0].split("+")), -len(item[1]), len({row["imperative_clause_de"] for row in item[1]}), item[0][0], item[0][1]),
            )[0]
            options.append({"channel": channel, "pair": pair, "key": key, "rows": rows})

        def option_key(option: dict[str, object]) -> tuple[object, ...]:
            channel = str(option["channel"])
            if "candidate" in option:
                candidate = option["candidate"]
                witness = option["witness"]
                return (CHANNEL_ORDER[channel], -int(candidate["partial_component_count"]), -int(witness["observed_event_count"]), 0 if candidate["contiguous_in_target"] == "YES" else 1, candidate["partial_candidate_id"], witness["witness_register"])
            key = option["key"]
            return (CHANNEL_ORDER[channel], -2, -len(option["rows"]), 0, key[0], key[1])

        chosen = sorted(options, key=option_key)[0]
        channel = str(chosen["channel"])
        if "candidate" in chosen:
            candidate = chosen["candidate"]
            witness = chosen["witness"]
            support_recipe = witness["partial_recipe"]
            support_register = witness["witness_register"]
            source_rows = clauses_by_recipe_register[(support_recipe, support_register)]
            relation = witness["witness_relation"]
            candidate_id = candidate["partial_candidate_id"]
            removed_positions = candidate["removal_position_sets"]
            added_components = candidate["removed_token_sets"]
            basis = "EXACT_COMPLETE_GDT416_PARTIAL_RECIPE"
        else:
            pair = chosen["pair"]
            support_recipe, support_register = chosen["key"]
            source_rows = chosen["rows"]
            relation = "SAME_REGISTER" if support_register == target["register"] else "CROSS_REGISTER"
            candidate_id = "NONE"
            removed_positions = "NONE"
            added_components = "+".join(token for token in target["action_recipe"].split("+") if token not in ACTION_ROOTS) or "NONE"
            basis = "EXACT_GDT416_CLAUSE_WITH_ATTESTED_GDT421_ORDERED_PAIR"
        payload = expected_payload(source_rows)
        check(
            f"card_{index:02d}_target_exact",
            card["gdt501_frontier_priority_rank"] == target["frontier_priority_rank"]
            and card["gdt501_frontier_support_tier"] == target["frontier_support_tier"]
            and card["target_frame"] == target["frozen_frame"]
            and card["target_action_root"] == target["action_root"]
            and card["target_action_recipe"] == target["action_recipe"]
            and card["target_register"] == target["register"]
            and card["target_portable_trace_de"] == target["portable_component_trace_de"]
            and card["target_owner_local_trace_de"] == target["owner_local_component_trace_de"]
            and card["target_current_default_phrase_de"] == target["current_default_phrase_de"],
            target["source_matrix_cell_id"],
        )
        check(
            f"card_{index:02d}_selected_support_exact",
            card["support_channel"] == channel
            and card["support_channel_basis"] == basis
            and card["support_partial_candidate_id"] == candidate_id
            and card["support_recipe"] == support_recipe
            and card["support_register_relation"] == relation
            and card["support_register"] == support_register
            and int(card["support_component_count"]) == len(support_recipe.split("+"))
            and card["target_component_count"] == target["component_count"]
            and card["target_removed_position_sets"] == removed_positions
            and card["target_added_component_sets"] == added_components,
            f"{channel} {support_recipe} {support_register}",
        )
        check(f"card_{index:02d}_clause_payload_exact", all(card[key] == value for key, value in payload.items()), payload["selected_old_clause_de"])
        check(
            f"card_{index:02d}_guards_exact",
            card["target_current_phrase_changed"] == "NO"
            and card["target_evidence_status_retained"] == "COMPOSED_WORKING"
            and card["working_root_meaning_changed"] == "NO"
            and card["surface_prediction_made"] == "NO"
            and card["occurrence_prediction_made"] == "NO"
            and card["guard"] == GUARD,
            GUARD,
        )
        witness = selected_by_card[card["comparison_card_id"]]
        check(
            f"card_{index:02d}_selected_witness_exact",
            witness["target_matrix_cell_id"] == target["source_matrix_cell_id"]
            and witness["support_channel"] == channel
            and witness["support_recipe"] == support_recipe
            and witness["support_register"] == support_register
            and witness["support_event_count"] == payload["support_event_count"]
            and witness["support_event_ids"] == payload["support_event_ids"]
            and witness["support_pages"] == payload["support_pages"]
            and witness["support_surfaces"] == payload["support_surfaces"]
            and witness["selected_old_clause_de"] == payload["selected_old_clause_de"]
            and witness["selected_old_clause_carrier_count"] == payload["selected_old_clause_carrier_count"]
            and witness["all_old_clauses_de"] == payload["all_old_clauses_de"]
            and witness["support_roundtrip_exact"] == "YES"
            and witness["guard"] == GUARD,
            witness["selected_witness_id"],
        )
        check(f"card_{index:02d}_readable_present", card["target_current_default_phrase_de"] in readable and card["selected_old_clause_de"] in readable, card["comparison_card_id"])

    for index, (source, row) in enumerate(zip(opened, open_cards), start=1):
        check(
            f"open_{index:02d}_exact",
            row["gdt501_frontier_priority_rank"] == source["frontier_priority_rank"]
            and row["target_matrix_cell_id"] == source["source_matrix_cell_id"]
            and row["target_action_recipe"] == source["action_recipe"]
            and row["target_register"] == source["register"]
            and row["target_portable_trace_de"] == source["portable_component_trace_de"]
            and row["target_owner_local_trace_de"] == source["owner_local_component_trace_de"]
            and row["target_current_default_phrase_de"] == source["current_default_phrase_de"]
            and row["ordered_action_pair"] == source["ordered_action_pair"]
            and row["ordered_pair_old_event_count"] == "0"
            and row["open_reason"] == "NO_EXACT_MULTIATOM_PARTIAL_AND_ORDERED_PAIR_UNATTESTED"
            and row["assumption_retained"] == "YES"
            and row["target_current_phrase_changed"] == "NO"
            and row["target_evidence_status_retained"] == "COMPOSED_WORKING"
            and row["working_root_meaning_changed"] == "NO"
            and row["surface_prediction_made"] == "NO"
            and row["occurrence_prediction_made"] == "NO"
            and row["guard"] == GUARD,
            row["target_action_recipe"],
        )
        check(f"open_{index:02d}_readable_present", row["target_current_default_phrase_de"] in readable, row["open_card_id"])

    expected_channels: list[dict[str, str]] = []
    for channel in sorted({row["support_channel"] for row in cards}, key=lambda value: CHANNEL_ORDER[value]):
        group = [row for row in cards if row["support_channel"] == channel]
        expected_channels.append({
            "support_channel": channel,
            "card_count": str(len(group)),
            "support_event_count": str(sum(int(row["support_event_count"]) for row in group)),
            "support_page_union_count": str(len({page for row in group for page in row["support_pages"].split("|")})),
            "same_register_card_count": str(sum(row["support_register_relation"] == "SAME_REGISTER" for row in group)),
            "cross_register_card_count": str(sum(row["support_register_relation"] == "CROSS_REGISTER" for row in group)),
            "all_roundtrips_exact": "YES" if all(row["support_roundtrip_exact"] == "YES" for row in group) else "NO",
            "all_target_phrases_retained": "YES",
        })
    check("channel_summary_exact", channel_rows == expected_channels, "six channels")

    expected_frames: list[dict[str, str]] = []
    for frame in sorted({row["target_frame"] for row in cards} | {row["frozen_frame"] for row in opened}):
        closed = [row for row in cards if row["target_frame"] == frame]
        open_group = [row for row in opened if row["frozen_frame"] == frame]
        expected_frames.append({
            "frozen_frame": frame,
            "supported_card_count": str(len(closed)),
            "open_card_count": str(len(open_group)),
            "selected_old_clause_event_count": str(sum(int(row["support_event_count"]) for row in closed)),
            "support_channel_count": str(len({row["support_channel"] for row in closed})),
            "all_target_phrases_retained": "YES",
        })
    check("frame_summary_exact", frame_rows == expected_frames, "five frames")
    check("readable_status_guard_exact", STATUS in readable and GUARD in readable, "status and guard")

    channels = Counter(row["support_channel"] for row in cards)
    expected_result = {
        "status": STATUS,
        "supported_comparison_cards": 46,
        "selected_old_clause_witnesses": 46,
        "open_cards_retained": 4,
        "local_near_action_cards": channels["LOCAL_NEAR_ACTION_RECIPE"],
        "local_action_partial_cards": channels["LOCAL_ACTION_PARTIAL_RECIPE"],
        "ordered_pair_target_register_cards": channels["ORDERED_PAIR_TARGET_REGISTER"],
        "cross_near_action_cards": channels["CROSS_NEAR_ACTION_RECIPE"],
        "ordered_pair_other_register_cards": channels["ORDERED_PAIR_OTHER_REGISTER"],
        "cross_action_partial_cards": channels["CROSS_ACTION_PARTIAL_RECIPE"],
        "local_frame_backbone_cards": channels["LOCAL_FRAME_BACKBONE_RECIPE"],
        "selected_old_clause_events": sum(int(row["support_event_count"]) for row in cards),
        "selected_old_clause_unique_event_ids": len({event for row in cards for event in row["support_event_ids"].split("|")}),
        "selected_old_clause_page_union": len({page for row in cards for page in row["support_pages"].split("|")}),
        "all_support_roundtrips_exact": sum(row["support_roundtrip_exact"] == "YES" for row in cards),
        "target_current_phrases_retained": sum(row["target_current_phrase_changed"] == "NO" for row in cards) + sum(row["target_current_phrase_changed"] == "NO" for row in open_cards),
        "composed_labels_retained": sum(row["target_evidence_status_retained"] == "COMPOSED_WORKING" for row in cards) + sum(row["target_evidence_status_retained"] == "COMPOSED_WORKING" for row in open_cards),
        "open_assumptions_retained": sum(row["assumption_retained"] == "YES" for row in open_cards),
        "working_root_meaning_changes": 0,
        "surface_predictions": 0,
        "occurrence_predictions": 0,
        "support_channel_count": 6,
        "frame_count": 5,
        "guard": GUARD,
    }
    check("result_exact", result == expected_result, json.dumps(expected_result, ensure_ascii=False, sort_keys=True))

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
