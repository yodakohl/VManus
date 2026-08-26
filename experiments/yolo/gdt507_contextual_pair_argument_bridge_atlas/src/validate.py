#!/usr/bin/env python3
"""Independent validation for GDT507's contextual pair bridge atlas."""

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
BASE = ROOT / "experiments/yolo/gdt507_contextual_pair_argument_bridge_atlas"
ART = BASE / "artifacts"
G416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts"
G425 = ROOT / "experiments/yolo/gdt425_complete_factorized_action_portability/artifacts"
G426 = ROOT / "experiments/yolo/gdt426_typed_action_family_prediction/artifacts"
G436 = ROOT / "experiments/yolo/gdt436_streaming_context_intake_driver/artifacts"
G506 = ROOT / "experiments/yolo/gdt506_target_pair_frame_compatibility_rank/artifacts"

CLAUSES_IN = G416 / "gdt416_4576_imperative_clauses.tsv"
FACTORS_IN = G425 / "gdt425_4576_event_factorized_action_replay.tsv"
PAIR_STATUS_IN = G426 / "gdt426_81_exact_action_pair_status.tsv"
STREAM_IN = G436 / "gdt436_4576_oracle_free_stream_readings.tsv"
TARGETS_IN = G506 / "gdt506_11_target_frame_compatibility_cards.tsv"

WITHIN_OUT = ART / "gdt507_65_within_event_chch_context_carriers.tsv"
ADJACENT_OUT = ART / "gdt507_13_adjacent_event_same_argument_bridges.tsv"
PAIR_SUMMARY_OUT = ART / "gdt507_2_pair_context_bridge_summary.tsv"
TARGET_OUT = ART / "gdt507_4_target_context_bridge_cards.tsv"
READABLE_OUT = ART / "GDT507_CONTEXTUAL_PAIR_ARGUMENT_BRIDGE_ATLAS.md"
RESULT_OUT = ART / "gdt507_result.json"
VALIDATION_OUT = ART / "gdt507_validation.json"

ACTION_ROOTS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
STATUS = "FOUR_CONTEXTUAL_TARGETS_HAVE_CONCRETE_BRIDGES__THREE_LOCAL_ONE_CROSS"
GUARD = "WORKING_CONTEXT_BRIDGE_ONLY__TARGETS_REMAIN_COMPOSED_AND_UNOBSERVED"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def mode(row: dict[str, str]) -> str:
    if row["explicit_argument_roots"] != "NONE":
        return "EXPLICIT_ARGUMENTS"
    if row["inherited_argument_root"] != "NONE":
        return "INHERITED_ARGUMENT"
    return "ARGUMENT_FREE"


def actions(row: dict[str, str]) -> list[str]:
    return [atom for atom in row["component_recipe"].split("+") if atom in ACTION_ROOTS]


def pair_count(row: dict[str, str], left: str, right: str) -> int:
    roots = actions(row)
    return sum((a, b) == (left, right) for a, b in zip(roots, roots[1:]))


def main() -> int:
    clauses = read_tsv(CLAUSES_IN)
    factors = read_tsv(FACTORS_IN)
    pair_status_rows = read_tsv(PAIR_STATUS_IN)
    stream = read_tsv(STREAM_IN)
    targets = read_tsv(TARGETS_IN)
    within = read_tsv(WITHIN_OUT)
    adjacent = read_tsv(ADJACENT_OUT)
    pair_summary = read_tsv(PAIR_SUMMARY_OUT)
    target_cards = read_tsv(TARGET_OUT)
    result = json.loads(RESULT_OUT.read_text(encoding="utf-8"))
    readable = READABLE_OUT.read_text(encoding="utf-8")

    clause_by_id = {row["global_running_event_id"]: row for row in clauses}
    factor_by_id = {row["global_running_event_id"]: row for row in factors}
    stream_by_id = {row["event_id"]: row for row in stream}
    pair_status = {row["ordered_pair"].replace(">", "+"): row for row in pair_status_rows}
    target_by_id = {row["target_frame_card_id"]: row for row in targets}
    clause_index = {row["global_running_event_id"]: index for index, row in enumerate(clauses)}

    checks: list[tuple[str, bool]] = []

    def check(name: str, condition: bool) -> None:
        checks.append((name, bool(condition)))

    check("source_clause_count", len(clauses) == 4576)
    check("source_factor_count", len(factors) == 4576)
    check("source_pair_profile_count", len(pair_status_rows) == 81)
    check("source_stream_count", len(stream) == 4576)
    check("source_target_count", len(targets) == 11)
    check("within_output_count", len(within) == 65)
    check("adjacent_output_count", len(adjacent) == 13)
    check("pair_summary_count", len(pair_summary) == 2)
    check("target_output_count", len(target_cards) == 4)
    check("within_ids_unique", len({row["within_event_carrier_id"] for row in within}) == len(within))
    check("within_event_ids_unique", len({row["global_running_event_id"] for row in within}) == len(within))
    check("adjacent_ids_unique", len({row["adjacent_bridge_id"] for row in adjacent}) == len(adjacent))
    check("adjacent_event_pairs_unique", len({(row["left_event_id"], row["right_event_id"]) for row in adjacent}) == len(adjacent))
    check("target_ids_unique", len({row["target_context_bridge_card_id"] for row in target_cards}) == len(target_cards))
    check("sealed_pages_absent", all(not row["physical_page"].startswith("f84") for row in clauses))

    expected_within_events = {
        row["global_running_event_id"]
        for row in clauses
        if pair_count(row, "CH", "CH")
    }
    check("within_complete_event_set", {row["global_running_event_id"] for row in within} == expected_within_events)
    check("gdt426_chch_count_match", int(pair_status["CH+CH"]["event_count"]) == len(within) == 65)

    for index, row in enumerate(within, start=1):
        prefix = f"within_{index:02d}"
        source = clause_by_id[row["global_running_event_id"]]
        factor = factor_by_id[row["global_running_event_id"]]
        state = stream_by_id[row["global_running_event_id"]]
        source_actions = actions(source)
        check(prefix + "_source_recipe", row["component_recipe"] == source["component_recipe"])
        check(prefix + "_source_register", row["register"] == source["register"])
        check(prefix + "_pair_present", pair_count(source, "CH", "CH") == 1)
        check(prefix + "_action_trace", row["explicit_action_roots"] == source["explicit_action_roots"] == "|".join(source_actions))
        check(prefix + "_mode", row["argument_mode"] == mode(source))
        check(prefix + "_context_flag", (row["context_compatible"] == "YES") == (mode(source) != "EXPLICIT_ARGUMENTS"))
        check(prefix + "_arguments", row["explicit_argument_roots"] == source["explicit_argument_roots"] and row["inherited_argument_root"] == source["inherited_argument_root"])
        check(prefix + "_stream_before", row["stream_active_argument_before"] == state["active_argument_before"])
        check(prefix + "_stream_after", row["stream_active_argument_after"] == state["active_argument_after"])
        check(prefix + "_stream_reference", row["stream_state_matches_reference"] == state["state_matches_reference"] == "YES" and row["stream_clause_matches_reference"] == state["clause_matches_reference"] == "YES")
        check(prefix + "_factor", row["factorized_action_replay_status"] == factor["factorized_action_replay_status"] == "CROSS_PAGE_ACTION_FACTORS_COMPLETE")
        check(prefix + "_clause", row["imperative_clause_de"] == source["imperative_clause_de"])
        check(prefix + "_guard", row["guard"] == GUARD)
        if row["argument_mode"] == "INHERITED_ARGUMENT":
            check(prefix + "_inherited_state_live", state["active_argument_before"] == source["inherited_argument_root"] != "NONE")

    recomputed_adjacent: set[tuple[str, str]] = set()
    for left, right in zip(clauses, clauses[1:]):
        if left["explicit_action_roots"] != "CH" or right["explicit_action_roots"] not in {"CH", "SH"}:
            continue
        if left["global_statement_id"] != right["global_statement_id"]:
            continue
        if int(right["card_ordinal_in_statement"]) != int(left["card_ordinal_in_statement"]) + 1:
            continue
        if (left["physical_page"], left["register"], left["owner_class"], left["owner_de"]) != (right["physical_page"], right["register"], right["owner_class"], right["owner_de"]):
            continue
        if left["explicit_argument_roots"] != "NONE" or right["explicit_argument_roots"] != "NONE":
            continue
        if left["inherited_argument_root"] == "NONE" or left["inherited_argument_root"] != right["inherited_argument_root"]:
            continue
        recomputed_adjacent.add((left["global_running_event_id"], right["global_running_event_id"]))
    check("adjacent_complete_pair_set", {(row["left_event_id"], row["right_event_id"]) for row in adjacent} == recomputed_adjacent)

    for index, row in enumerate(adjacent, start=1):
        prefix = f"adjacent_{index:02d}"
        left = clause_by_id[row["left_event_id"]]
        right = clause_by_id[row["right_event_id"]]
        left_state = stream_by_id[row["left_event_id"]]
        right_state = stream_by_id[row["right_event_id"]]
        check(prefix + "_source_consecutive", clause_index[row["right_event_id"]] == clause_index[row["left_event_id"]] + 1)
        check(prefix + "_ordinal_consecutive", int(right["card_ordinal_in_statement"]) == int(left["card_ordinal_in_statement"]) + 1)
        check(prefix + "_same_statement", left["global_statement_id"] == right["global_statement_id"] == row["global_statement_id"])
        check(prefix + "_same_owner", left["owner_de"] == right["owner_de"] == row["owner_de"] and left["owner_class"] == right["owner_class"] == row["owner_class"])
        check(prefix + "_same_register_page", left["register"] == right["register"] == row["register"] and left["physical_page"] == right["physical_page"] == row["physical_page"])
        check(prefix + "_single_heads", left["explicit_action_roots"] == "CH" and right["explicit_action_roots"] in {"CH", "SH"})
        check(prefix + "_pair_label", row["ordered_action_pair"] == f"CH+{right['explicit_action_roots']}")
        check(prefix + "_no_explicit_arguments", left["explicit_argument_roots"] == right["explicit_argument_roots"] == "NONE")
        check(prefix + "_same_inherited_argument", left["inherited_argument_root"] == right["inherited_argument_root"] == row["shared_inherited_argument_root"] != "NONE")
        check(prefix + "_stream_consecutive", int(right_state["stream_ordinal"]) == int(left_state["stream_ordinal"]) + 1 and row["stream_ordinals_consecutive"] == "YES")
        check(prefix + "_left_state", left_state["active_argument_before"] == left_state["active_argument_after"] == row["shared_inherited_argument_root"])
        check(prefix + "_right_state", right_state["active_argument_before"] == right_state["active_argument_after"] == row["shared_inherited_argument_root"])
        check(prefix + "_state_reference", row["left_stream_state_matches_reference"] == row["right_stream_state_matches_reference"] == "YES")
        check(prefix + "_factor_left", row["left_factorized_action_replay_status"] == factor_by_id[row["left_event_id"]]["factorized_action_replay_status"] == "CROSS_PAGE_ACTION_FACTORS_COMPLETE")
        check(prefix + "_factor_right", row["right_factorized_action_replay_status"] == factor_by_id[row["right_event_id"]]["factorized_action_replay_status"] == "CROSS_PAGE_ACTION_FACTORS_COMPLETE")
        check(prefix + "_recipes", row["left_component_recipe"] == left["component_recipe"] and row["right_component_recipe"] == right["component_recipe"])
        check(prefix + "_clauses", row["left_imperative_clause_de"] == left["imperative_clause_de"] and row["right_imperative_clause_de"] == right["imperative_clause_de"])
        check(prefix + "_guard", row["guard"] == GUARD)

    mode_counts = Counter(row["argument_mode"] for row in within)
    adjacent_counts = Counter(row["ordered_action_pair"] for row in adjacent)
    check("within_mode_counts", mode_counts == Counter({"EXPLICIT_ARGUMENTS": 53, "INHERITED_ARGUMENT": 11, "ARGUMENT_FREE": 1}))
    check("adjacent_pair_counts", adjacent_counts == Counter({"CH+SH": 9, "CH+CH": 4}))
    check("adjacent_page_count", len({row["physical_page"] for row in adjacent}) == 10)
    check("adjacent_register_count", len({row["register"] for row in adjacent}) == 5)

    summary_by_pair = {row["ordered_action_pair"]: row for row in pair_summary}
    check("summary_pairs", set(summary_by_pair) == {"CH+CH", "CH+SH"})
    for pair in ("CH+CH", "CH+SH"):
        left, right = pair.split("+")
        source_group = [row for row in clauses if pair_count(row, left, right)]
        compatible = [row for row in source_group if mode(row) != "EXPLICIT_ARGUMENTS"]
        adjacent_group = [row for row in adjacent if row["ordered_action_pair"] == pair]
        summary = summary_by_pair[pair]
        check(pair + "_summary_within", int(summary["within_event_pair_event_count"]) == len(source_group) == int(pair_status[pair]["event_count"]))
        check(pair + "_summary_explicit", int(summary["within_event_explicit_argument_count"]) == sum(mode(row) == "EXPLICIT_ARGUMENTS" for row in source_group))
        check(pair + "_summary_inherited", int(summary["within_event_inherited_argument_count"]) == sum(mode(row) == "INHERITED_ARGUMENT" for row in source_group))
        check(pair + "_summary_free", int(summary["within_event_argument_free_count"]) == sum(mode(row) == "ARGUMENT_FREE" for row in source_group))
        check(pair + "_summary_compatible", int(summary["within_event_context_compatible_count"]) == len(compatible))
        check(pair + "_summary_adjacent", int(summary["adjacent_same_statement_context_chain_count"]) == len(adjacent_group))
        check(pair + "_summary_pages", int(summary["adjacent_context_page_count"]) == len({row["physical_page"] for row in adjacent_group}))
        check(pair + "_summary_registers", int(summary["adjacent_context_register_count"]) == len({row["register"] for row in adjacent_group}))
        check(pair + "_summary_guard", summary["guard"] == GUARD)

    open_targets = {
        row["target_frame_card_id"]: row
        for row in targets
        if row["compatibility_tier"] == "C_ACTION_HANDGRIP_ONLY__ARGUMENT_MODE_OPEN"
    }
    check("four_open_sources", len(open_targets) == 4)
    check("target_source_set", {row["source_gdt506_target_frame_card_id"] for row in target_cards} == set(open_targets))
    adjacent_by_id = {row["adjacent_bridge_id"]: row for row in adjacent}
    for index, card in enumerate(target_cards, start=1):
        prefix = f"target_{index:02d}"
        source = target_by_id[card["source_gdt506_target_frame_card_id"]]
        pair = card["ordered_action_pair"]
        pair_event = clause_by_id[card["selected_pair_order_event_id"]]
        context = adjacent_by_id[card["selected_context_bridge_id"]]
        left, right = pair.split("+")
        check(prefix + "_source_fields", card["target_matrix_cell_id"] == source["target_matrix_cell_id"] and card["target_register"] == source["target_register"] and card["target_action_recipe"] == source["target_action_recipe"])
        check(prefix + "_phrase_retained", card["target_current_default_phrase_de"] == source["target_current_default_phrase_de"] and card["target_phrase_changed"] == "NO")
        check(prefix + "_old_tier", card["old_gdt506_compatibility_tier"] == source["compatibility_tier"] == "C_ACTION_HANDGRIP_ONLY__ARGUMENT_MODE_OPEN")
        check(prefix + "_pair_event", pair_count(pair_event, left, right) >= 1)
        check(prefix + "_pair_event_fields", card["selected_pair_order_register"] == pair_event["register"] and card["selected_pair_order_recipe"] == pair_event["component_recipe"] and card["selected_pair_order_argument_mode"] == mode(pair_event))
        check(prefix + "_context_pair", context["ordered_action_pair"] == pair)
        check(prefix + "_context_fields", card["selected_context_left_event_id"] == context["left_event_id"] and card["selected_context_right_event_id"] == context["right_event_id"] and card["selected_context_shared_argument_root"] == context["shared_inherited_argument_root"])
        check(prefix + "_target_status", card["target_bridge_status"] == "CONTEXT_BRIDGED_WORKING__TARGET_RECIPE_UNOBSERVED")
        check(prefix + "_evidence_retained", card["target_evidence_status_retained"] == source["target_evidence_status_retained"] == "COMPOSED_WORKING")
        check(prefix + "_invariants", card["working_root_meaning_changed"] == card["surface_prediction_made"] == card["occurrence_prediction_made"] == "NO")
        check(prefix + "_guard", card["guard"] == GUARD)
        if card["context_bridge_locality"] == "LOCAL":
            check(prefix + "_local_context", context["register"] == card["target_register"])
        else:
            check(prefix + "_cross_context", context["register"] != card["target_register"])
        if pair == "CH+CH":
            check(prefix + "_chch_pair_context", mode(pair_event) in {"INHERITED_ARGUMENT", "ARGUMENT_FREE"} and card["pair_order_event_also_context_compatible"] == "YES")
        else:
            check(prefix + "_chsh_pair_explicit", mode(pair_event) == "EXPLICIT_ARGUMENTS" and card["pair_order_event_also_context_compatible"] == "NO")

    check("three_local_targets", sum(row["context_bridge_locality"] == "LOCAL" for row in target_cards) == 3)
    check("one_cross_target", sum(row["context_bridge_locality"] == "CROSS_REGISTER" for row in target_cards) == 1)
    check("source_chsh_local_chains", int(next(row for row in target_cards if row["target_register"] == "SOURCE_SECTION_T" and row["ordered_action_pair"] == "CH+SH")["adjacent_target_register_chain_count"]) == 3)
    check("pharma_chsh_local_chains", int(next(row for row in target_cards if row["target_register"] == "PHARMA" and row["ordered_action_pair"] == "CH+SH")["adjacent_target_register_chain_count"]) == 1)
    check("result_status", result["status"] == STATUS)
    check("result_within_counts", result["within_event_chch_carriers"] == 65 and result["within_event_chch_inherited_argument_carriers"] == 11 and result["within_event_chch_argument_free_carriers"] == 1)
    check("result_adjacent_counts", result["adjacent_same_argument_bridge_chains"] == 13 and result["adjacent_chch_bridge_chains"] == 4 and result["adjacent_chsh_bridge_chains"] == 9)
    check("result_target_counts", result["target_context_bridge_cards"] == 4 and result["local_target_context_bridges"] == 3 and result["cross_register_target_context_bridges"] == 1)
    check("result_invariants", result["target_phrases_changed"] == result["working_root_meanings_changed"] == result["surface_predictions"] == result["occurrence_predictions"] == 0)
    check("result_guard", result["guard"] == GUARD)
    check("readable_status", STATUS in readable)
    check("readable_examples", all(event in readable for event in ("G407-E0117", "G407-E0118", "G407-E3857", "G407-E3858")))

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
