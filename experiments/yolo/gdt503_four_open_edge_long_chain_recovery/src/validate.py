#!/usr/bin/env python3
"""Independently validate the GDT503 broader-chain recovery of four open edges."""

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
BASE = ROOT / "experiments/yolo/gdt503_four_open_edge_long_chain_recovery"
ART = BASE / "artifacts"
G416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts"
G421 = ROOT / "experiments/yolo/gdt421_ordered_action_pair_slot_license/artifacts"
G422 = ROOT / "experiments/yolo/gdt422_multi_action_chain_pair_reduction/artifacts"
G425 = ROOT / "experiments/yolo/gdt425_complete_factorized_action_portability/artifacts"
G426 = ROOT / "experiments/yolo/gdt426_typed_action_family_prediction/artifacts"
G427 = ROOT / "experiments/yolo/gdt427_typed_prediction_specificity_repair/artifacts"
G444 = ROOT / "experiments/yolo/gdt444_focus_separated_action_pair_atlas/artifacts"
G502 = ROOT / "experiments/yolo/gdt502_supported_frontier_comparison_cards/artifacts"

OPEN_IN = G502 / "gdt502_4_open_frontier_cards.tsv"
CLAUSES_IN = G416 / "gdt416_4576_imperative_clauses.tsv"
PAIR421_IN = G421 / "gdt421_81_ordered_pair_profiles.tsv"
GAPS422_IN = G422 / "gdt422_11_pair_gap_adjudications.tsv"
ADJ425_IN = G425 / "gdt425_649_adjacent_pair_portability.tsv"
PAIR426_IN = G426 / "gdt426_81_exact_action_pair_status.tsv"
LEAVEOUT427_IN = G427 / "gdt427_15_singleton_pair_leaveout.tsv"
SEP_SUMMARY444_IN = G444 / "gdt444_44_pair_separator_summary.tsv"
SEP_MATRIX444_IN = G444 / "gdt444_484_focus_separated_pair_matrix.tsv"
CARDS_OUT = ART / "gdt503_4_corrected_open_edge_cards.tsv"
PAIR_OUT = ART / "gdt503_2_directional_pair_support_summaries.tsv"
WITNESS_OUT = ART / "gdt503_2_long_chain_clause_witnesses.tsv"
PEER_OUT = ART / "gdt503_8_peer_pair_analogies.tsv"
REVERSE_OUT = ART / "gdt503_2_reverse_order_contrasts.tsv"
SEPARATOR_OUT = ART / "gdt503_11_ch_chd_separator_routes.tsv"
READABLE_OUT = ART / "GDT503_FOUR_OPEN_EDGE_RECOVERY_CARDS.md"
RESULT_OUT = ART / "gdt503_result.json"
VALIDATION_OUT = ART / "gdt503_validation.json"

TARGET_PAIRS = ("CH>CHD", "CH>OK")
STATUS = "BOTH_OPEN_RECIPES_HAVE_ONE_OLD_DIRECTIONAL_CHAIN__DIRECT_AND_SEPARATOR_SUPPORT_DISTINGUISHED"
GUARD = "BROADER_CHAIN_SUPPORT_ONLY__TWO_HEAD_TARGETS_REMAIN_COMPOSED__NO_SURFACE_PREDICTION"


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames is None:
            raise ValueError(f"missing header: {path}")
        return list(reader.fieldnames), list(reader)


def main() -> int:
    _open_fields, open_source = read_tsv(OPEN_IN)
    _clause_fields, clauses = read_tsv(CLAUSES_IN)
    _p421_fields, pairs421 = read_tsv(PAIR421_IN)
    _gap_fields, gaps422 = read_tsv(GAPS422_IN)
    _adj_fields, adjacent425 = read_tsv(ADJ425_IN)
    _p426_fields, pairs426 = read_tsv(PAIR426_IN)
    _leaveout_fields, leaveout427 = read_tsv(LEAVEOUT427_IN)
    _sep_sum_fields, sep_summaries = read_tsv(SEP_SUMMARY444_IN)
    _sep_matrix_fields, sep_matrix = read_tsv(SEP_MATRIX444_IN)
    card_fields, cards = read_tsv(CARDS_OUT)
    pair_fields, pair_rows = read_tsv(PAIR_OUT)
    witness_fields, witnesses = read_tsv(WITNESS_OUT)
    peer_fields, peers = read_tsv(PEER_OUT)
    reverse_fields, reverse_rows = read_tsv(REVERSE_OUT)
    separator_fields, separator_rows = read_tsv(SEPARATOR_OUT)
    readable = READABLE_OUT.read_text(encoding="utf-8")
    result = json.loads(RESULT_OUT.read_text(encoding="utf-8"))

    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    counts = (
        len(open_source), len(clauses), len(pairs421), len(gaps422), len(adjacent425),
        len(pairs426), len(leaveout427), len(sep_summaries), len(sep_matrix),
        len(cards), len(pair_rows), len(witnesses), len(peers), len(reverse_rows), len(separator_rows),
    )
    check("all_table_counts_exact", counts == (4, 4576, 81, 11, 649, 81, 15, 44, 484, 4, 2, 2, 8, 2, 11), f"actual={counts}")
    check("card_schema_complete", {"corrected_open_card_id", "direct_component_adjacency", "corrected_support_class"} <= set(card_fields), f"fields={len(card_fields)}")
    check("pair_schema_complete", {"pair_summary_id", "gdt421_exact_two_head_event_count", "gdt426_broad_action_chain_event_count"} <= set(pair_fields), f"fields={len(pair_fields)}")
    check("witness_schema_complete", {"long_chain_witness_id", "global_running_event_id", "gdt416_roundtrip_exact"} <= set(witness_fields), f"fields={len(witness_fields)}")
    check("peer_schema_complete", {"peer_analogy_id", "target_typed_transition", "peer_event_count"} <= set(peer_fields), f"fields={len(peer_fields)}")
    check("reverse_schema_complete", {"reverse_contrast_id", "reverse_ordered_pair", "order_collapsed"} <= set(reverse_fields), f"fields={len(reverse_fields)}")
    check("separator_schema_complete", {"separator_route_id", "separator_focus", "direct_pair_promoted"} <= set(separator_fields), f"fields={len(separator_fields)}")
    check("output_ids_exact", [row["corrected_open_card_id"] for row in cards] == [f"G503-C{i:02d}" for i in range(1, 5)] and [row["pair_summary_id"] for row in pair_rows] == ["G503-P01", "G503-P02"] and [row["long_chain_witness_id"] for row in witnesses] == ["G503-W01", "G503-W02"] and [row["peer_analogy_id"] for row in peers] == [f"G503-A{i:02d}" for i in range(1, 9)] and [row["reverse_contrast_id"] for row in reverse_rows] == ["G503-R01", "G503-R02"] and [row["separator_route_id"] for row in separator_rows] == [f"G503-S{i:02d}" for i in range(1, 12)], "all sequential IDs")

    p421 = {row["ordered_pair"].replace("+", ">", 1): row for row in pairs421}
    p426 = {row["ordered_pair"]: row for row in pairs426}
    gaps = {row["missing_pair"].replace("+", ">", 1): row for row in gaps422}
    leaveouts = {row["ordered_pair"]: row for row in leaveout427}
    sep_summary = {row["direct_pair"]: row for row in sep_summaries}
    sep_by_pair: dict[str, list[dict[str, str]]] = defaultdict(list)
    adj_by_pair: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in sep_matrix:
        sep_by_pair[row["direct_pair"]].append(row)
    for row in adjacent425:
        adj_by_pair[row["ordered_pair"]].append(row)
    clause_by_id = {row["global_running_event_id"]: row for row in clauses}
    pair_output = {row["ordered_action_pair"]: row for row in pair_rows}
    witness_output = {row["ordered_action_pair"]: row for row in witnesses}
    peers_by_target: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in peers:
        peers_by_target[row["target_ordered_pair"]].append(row)

    for index, pair_key in enumerate(TARGET_PAIRS, start=1):
        left, right = pair_key.split(">")
        exact = p421[pair_key]
        broad = p426[pair_key]
        gap = gaps[pair_key]
        event_id = gap["global_running_event_ids"]
        clause = clause_by_id[event_id]
        direct = adj_by_pair[pair_key]
        leaveout = leaveouts[pair_key]
        reverse = p426[f"{right}>{left}"]
        output = pair_output[pair_key]
        expected_direct = pair_key == "CH>OK"
        expected_class = "EMBEDDED_DIRECT_COMPONENT_ADJACENCY" if expected_direct else "ORDERED_ACTION_CHAIN_WITH_VISIBLE_SEPARATOR"
        check(
            f"pair_{index}_source_scope_exact",
            exact["status"] == "PAIR_ABSENT"
            and exact["event_count"] == "0"
            and exact["exact_recipe_type_count"] == "0"
            and broad["pair_status"] == "ATTESTED_ONE_PAGE"
            and broad["event_count"] == "1"
            and gap["event_count"] == "1"
            and (len(direct) == 1) == expected_direct
            and (gap["between_atoms"] == "NONE") == expected_direct,
            pair_key,
        )
        check(
            f"pair_{index}_summary_exact",
            output["ordered_action_pair"] == pair_key
            and output["portable_pair_reading_de"] == exact["ordered_reading_de"]
            and output["gdt421_exact_two_head_status"] == exact["status"]
            and output["gdt421_exact_two_head_event_count"] == "0"
            and output["gdt421_exact_two_head_recipe_type_count"] == "0"
            and output["gdt426_broad_action_chain_status"] == broad["pair_status"]
            and output["gdt426_broad_action_chain_event_count"] == "1"
            and output["gdt426_broad_action_chain_pages"] == broad["pages"]
            and output["gdt422_long_recipe"] == gap["component_recipe"]
            and output["gdt422_action_chain"] == gap["action_chain"]
            and output["gdt422_between_atoms"] == gap["between_atoms"]
            and output["gdt422_repair_rule"] == gap["repair_rule"]
            and output["long_chain_event_id"] == event_id
            and output["long_chain_page"] == gap["pages"]
            and output["long_chain_register"] == gap["registers"]
            and output["direct_component_adjacency"] == ("YES" if expected_direct else "NO")
            and output["direct_adjacency_gdt425_status"] == (direct[0]["portability_status"] if direct else "NONE")
            and output["corrected_support_class"] == expected_class
            and output["gdt427_leaveout_prediction"] == leaveout["prediction"]
            and output["gdt427_typed_transition"] == leaveout["typed_transition"]
            and output["peer_transition_other_support_pages"] == leaveout["other_support_pages"]
            and output["reverse_order_pair"] == reverse["ordered_pair"]
            and output["reverse_order_event_count"] == reverse["event_count"]
            and output["reverse_order_pages"] == reverse["pages"],
            expected_class,
        )
        if pair_key == "CH>CHD":
            summary = sep_summary[pair_key]
            check("ch_chd_separator_summary_exact", output["accepted_single_separator_count"] == summary["accepted_separator_count"] == "11" and output["direct_pair_remains_unlicensed_after_separator_test"] == summary["direct_pair_remains_unlicensed"] == "YES", "11 accepted, direct unlicensed")
        else:
            check("ch_ok_separator_not_applicable_exact", output["accepted_single_separator_count"] == "NOT_APPLICABLE_DIRECT_LOCAL_PAIR" and output["direct_pair_remains_unlicensed_after_separator_test"] == "NOT_APPLICABLE_DIRECT_LOCAL_PAIR", "direct local pair")
        check(
            f"pair_{index}_guards_exact",
            output["target_two_head_recipe_observed"] == "NO"
            and output["target_evidence_status_retained"] == "COMPOSED_WORKING"
            and output["working_root_meaning_changed"] == "NO"
            and output["surface_prediction_made"] == "NO"
            and output["occurrence_prediction_made"] == "NO"
            and output["guard"] == GUARD,
            GUARD,
        )
        witness = witness_output[pair_key]
        check(
            f"pair_{index}_long_clause_witness_exact",
            witness["global_running_event_id"] == event_id
            and witness["physical_page"] == clause["physical_page"]
            and witness["register"] == clause["register"]
            and witness["surface"] == clause["surface"]
            and witness["component_recipe"] == clause["component_recipe"] == gap["component_recipe"]
            and witness["explicit_action_roots"] == clause["explicit_action_roots"]
            and witness["between_atoms"] == gap["between_atoms"]
            and witness["repair_rule"] == gap["repair_rule"]
            and witness["imperative_clause_de"] == clause["imperative_clause_de"]
            and witness["owner_local_atom_reading_de"] == clause["owner_local_atom_reading_de"]
            and witness["portable_back_projection_de"] == clause["portable_back_projection_de"]
            and witness["gdt416_roundtrip_exact"] == clause["roundtrip_exact"] == "YES"
            and witness["direct_component_adjacency"] == ("YES" if expected_direct else "NO")
            and witness["guard"] == GUARD,
            event_id,
        )
        expected_peers = [row for row in pairs426 if row["left_class"] == broad["left_class"] and row["right_class"] == broad["right_class"] and row["ordered_pair"] != pair_key]
        actual_peers = peers_by_target[pair_key]
        check(f"pair_{index}_peer_count_exact", len(actual_peers) == len(expected_peers), f"peers={len(expected_peers)}")
        for peer_index, (actual, expected) in enumerate(zip(actual_peers, expected_peers), start=1):
            check(
                f"pair_{index}_peer_{peer_index}_exact",
                actual["target_typed_transition"] == f'{broad["left_class"]}>{broad["right_class"]}'
                and actual["peer_ordered_pair"] == expected["ordered_pair"]
                and actual["peer_event_count"] == expected["event_count"]
                and actual["peer_page_count"] == expected["page_count"]
                and actual["peer_pages"] == expected["pages"]
                and actual["peer_surface_count"] == expected["surface_count"]
                and actual["peer_pair_status"] == expected["pair_status"]
                and actual["same_typed_transition"] == "YES"
                and actual["target_pair_promoted"] == "NO"
                and actual["guard"] == GUARD,
                expected["ordered_pair"],
            )

    check("all_peer_analogies_attested", all(int(row["peer_event_count"]) > 0 and row["peer_pair_status"].startswith("ATTESTED") for row in peers), "8/8")
    for index, row in enumerate(reverse_rows, start=1):
        target = p426[row["target_ordered_pair"]]
        reverse = p426[row["reverse_ordered_pair"]]
        check(
            f"reverse_{index}_exact",
            row["target_broad_chain_event_count"] == target["event_count"]
            and row["reverse_broad_chain_event_count"] == reverse["event_count"]
            and row["reverse_page_count"] == reverse["page_count"]
            and row["reverse_pages"] == reverse["pages"]
            and row["order_collapsed"] == "NO"
            and row["guard"] == GUARD,
            row["reverse_ordered_pair"],
        )

    expected_separator_source = sep_by_pair["CH>CHD"]
    check("separator_source_count_exact", len(expected_separator_source) == 11, "11 routes")
    for index, (actual, source) in enumerate(zip(separator_rows, expected_separator_source), start=1):
        check(
            f"separator_{index:02d}_exact",
            actual["target_ordered_pair"] == "CH>CHD"
            and actual["separator_focus"] == source["separator_focus"]
            and actual["separated_recipe"] == source["separated_recipe"]
            and actual["separated_factor_gate_status"] == source["separated_factor_gate_status"]
            and actual["separator_decision"] == source["separator_decision"]
            and actual["scope_selector_rules"] == source["scope_selector_rules"]
            and actual["portable_factor_rules"] == source["portable_factor_rules"]
            and actual["ordered_literal_reading_de"] == source["ordered_literal_reading_de"]
            and actual["direct_pair_promoted"] == source["direct_pair_promoted"] == "NO"
            and actual["surface_or_occurrence_prediction"] == source["surface_or_occurrence_prediction"] == "NO"
            and actual["guard"] == GUARD,
            source["separator_focus"],
        )

    summary_by_pair = {row["ordered_action_pair"]: row for row in pair_rows}
    check("card_source_order_exact", [row["source_gdt502_open_card_id"] for row in cards] == [row["open_card_id"] for row in open_source], "G502 O01..O04")
    for index, (source, card) in enumerate(zip(open_source, cards), start=1):
        pair_key = source["ordered_action_pair"].replace("+", ">", 1)
        summary = summary_by_pair[pair_key]
        check(
            f"card_{index}_exact",
            card["target_matrix_cell_id"] == source["target_matrix_cell_id"]
            and card["target_action_recipe"] == source["target_action_recipe"]
            and card["target_register"] == source["target_register"]
            and card["target_portable_trace_de"] == source["target_portable_trace_de"]
            and card["target_owner_local_trace_de"] == source["target_owner_local_trace_de"]
            and card["target_current_default_phrase_de"] == source["target_current_default_phrase_de"]
            and card["ordered_action_pair"] == pair_key
            and card["gdt421_two_head_event_count"] == summary["gdt421_exact_two_head_event_count"] == "0"
            and card["broader_old_chain_event_count"] == summary["gdt426_broad_action_chain_event_count"] == "1"
            and card["broader_old_chain_event_id"] == summary["long_chain_event_id"]
            and card["broader_old_chain_recipe"] == summary["gdt422_long_recipe"]
            and card["broader_old_chain_page"] == summary["long_chain_page"]
            and card["direct_component_adjacency"] == summary["direct_component_adjacency"]
            and card["corrected_support_class"] == summary["corrected_support_class"]
            and card["corrected_support_reading_de"] == summary["corrected_support_reading_de"]
            and card["assumption_retained"] == "YES"
            and card["target_two_head_recipe_observed"] == "NO"
            and card["target_current_phrase_changed"] == "NO"
            and card["target_evidence_status_retained"] == "COMPOSED_WORKING"
            and card["working_root_meaning_changed"] == "NO"
            and card["surface_prediction_made"] == "NO"
            and card["occurrence_prediction_made"] == "NO"
            and card["guard"] == GUARD,
            card["target_matrix_cell_id"],
        )
        check(f"card_{index}_readable_present", card["target_current_default_phrase_de"] in readable and card["corrected_support_reading_de"] in readable, card["corrected_open_card_id"])

    expected_result = {
        "status": STATUS,
        "corrected_open_cards": 4,
        "target_pair_recipes": 2,
        "gdt421_exact_two_head_events": sum(int(row["gdt421_exact_two_head_event_count"]) for row in pair_rows),
        "broader_old_directional_chain_events": sum(int(row["gdt426_broad_action_chain_event_count"]) for row in pair_rows),
        "concrete_long_chain_clause_witnesses": 2,
        "direct_component_adjacency_pair_types": sum(row["direct_component_adjacency"] == "YES" for row in pair_rows),
        "visible_separator_pair_types": sum(row["corrected_support_class"] == "ORDERED_ACTION_CHAIN_WITH_VISIBLE_SEPARATOR" for row in pair_rows),
        "peer_pair_analogies": 8,
        "peer_pair_analogy_events": sum(int(row["peer_event_count"]) for row in peers),
        "reverse_order_contrasts": 2,
        "reverse_order_events": sum(int(row["reverse_broad_chain_event_count"]) for row in reverse_rows),
        "ch_chd_accepted_single_separator_routes": 11,
        "all_separator_routes_keep_direct_pair_unpromoted": sum(row["direct_pair_promoted"] == "NO" for row in separator_rows),
        "gdt416_long_chain_roundtrips_exact": sum(row["gdt416_roundtrip_exact"] == "YES" for row in witnesses),
        "target_current_phrases_retained": sum(row["target_current_phrase_changed"] == "NO" for row in cards),
        "composed_labels_retained": sum(row["target_evidence_status_retained"] == "COMPOSED_WORKING" for row in cards),
        "open_assumptions_retained": sum(row["assumption_retained"] == "YES" for row in cards),
        "target_two_head_recipes_observed": sum(row["target_two_head_recipe_observed"] == "YES" for row in cards),
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
