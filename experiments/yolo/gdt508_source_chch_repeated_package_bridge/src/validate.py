#!/usr/bin/env python3
"""Independent validator for GDT508's Source repeated-package bridge."""

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
BASE = ROOT / "experiments/yolo/gdt508_source_chch_repeated_package_bridge"
ART = BASE / "artifacts"
G413 = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts"
G416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts"
G425 = ROOT / "experiments/yolo/gdt425_complete_factorized_action_portability/artifacts"
G436 = ROOT / "experiments/yolo/gdt436_streaming_context_intake_driver/artifacts"
G500 = ROOT / "experiments/yolo/gdt500_repeated_action_fluency_matrix/artifacts"
G507 = ROOT / "experiments/yolo/gdt507_contextual_pair_argument_bridge_atlas/artifacts"

DICTIONARY_IN = G413 / "gdt413_46_component_working_dictionary.tsv"
CLAUSES_IN = G416 / "gdt416_4576_imperative_clauses.tsv"
FACTORS_IN = G425 / "gdt425_4576_event_factorized_action_replay.tsv"
STREAM_IN = G436 / "gdt436_4576_oracle_free_stream_readings.tsv"
FLUENCY_IN = G500 / "gdt500_15_repeated_action_fluency_cards.tsv"
TARGETS_IN = G507 / "gdt507_4_target_context_bridge_cards.tsv"

PAIRS_OUT = ART / "gdt508_2_source_repeated_ch_package_pairs.tsv"
ARMS_OUT = ART / "gdt508_4_package_cancellation_arms.tsv"
TARGET_OUT = ART / "gdt508_1_source_chch_local_bridge_card.tsv"
READABLE_OUT = ART / "GDT508_SOURCE_CHCH_REPEATED_PACKAGE_BRIDGE.md"
RESULT_OUT = ART / "gdt508_result.json"
VALIDATION_OUT = ART / "gdt508_validation.json"

STATUS = "SOURCE_CHCH_GAINS_LOCAL_REPEATED_PACKAGE_BRIDGE__ALL_FOUR_CONTEXT_TARGETS_HAVE_LOCAL_SUPPORT"
GUARD = "LOCAL_PACKAGE_PROJECTION_ONLY__BARE_SOURCE_CHCH_TARGET_REMAINS_UNOBSERVED"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    dictionary = read_tsv(DICTIONARY_IN)
    clauses = read_tsv(CLAUSES_IN)
    factors = read_tsv(FACTORS_IN)
    stream = read_tsv(STREAM_IN)
    fluency = read_tsv(FLUENCY_IN)
    targets = read_tsv(TARGETS_IN)
    pairs = read_tsv(PAIRS_OUT)
    arms = read_tsv(ARMS_OUT)
    target_rows = read_tsv(TARGET_OUT)
    result = json.loads(RESULT_OUT.read_text(encoding="utf-8"))
    readable = READABLE_OUT.read_text(encoding="utf-8")

    values = {row["atom"]: row["working_value_de"] for row in dictionary}
    clause_by_event = {row["global_running_event_id"]: row for row in clauses}
    factor_by_event = {row["global_running_event_id"]: row for row in factors}
    stream_by_event = {row["event_id"]: row for row in stream}
    fluency_card = next(row for row in fluency if row["source_matrix_cell_id"] == "G498-M456")
    old_target = next(row for row in targets if row["target_matrix_cell_id"] == "G498-M456")

    checks: list[tuple[str, bool]] = []

    def check(name: str, condition: bool) -> None:
        checks.append((name, bool(condition)))

    check("dictionary_count", len(dictionary) == 46)
    check("clause_count", len(clauses) == 4576)
    check("factor_count", len(factors) == 4576)
    check("stream_count", len(stream) == 4576)
    check("fluency_count", len(fluency) == 15)
    check("old_target_count", len(targets) == 4)
    check("pair_output_count", len(pairs) == 2)
    check("arm_output_count", len(arms) == 4)
    check("target_output_count", len(target_rows) == 1)
    check("pair_ids_unique", len({row["source_repeated_package_pair_id"] for row in pairs}) == 2)
    check("arm_ids_unique", len({row["package_cancellation_arm_id"] for row in arms}) == 4)
    check("sealed_pages_absent", all(not row["physical_page"].startswith("f84") for row in clauses))

    expected: set[tuple[str, str]] = set()
    for left_index, left in enumerate(clauses):
        for gap in (0, 1):
            right_index = left_index + gap + 1
            if right_index >= len(clauses):
                continue
            right = clauses[right_index]
            if left["register"] != right["register"] or left["register"] != "SOURCE_SECTION_T":
                continue
            if (left["physical_page"], left["global_statement_id"], left["owner_class"], left["owner_de"]) != (right["physical_page"], right["global_statement_id"], right["owner_class"], right["owner_de"]):
                continue
            if int(right["card_ordinal_in_statement"]) != int(left["card_ordinal_in_statement"]) + gap + 1:
                continue
            if left["explicit_action_roots"] != right["explicit_action_roots"]:
                continue
            action_trace = left["explicit_action_roots"].split("|")
            if action_trace.count("CH") != 1 or not action_trace or action_trace[0] != "CH":
                continue
            if left["explicit_argument_roots"] != right["explicit_argument_roots"] or left["explicit_argument_roots"] != "NONE":
                continue
            if left["inherited_argument_root"] == "NONE" or left["inherited_argument_root"] != right["inherited_argument_root"]:
                continue
            expected.add((left["global_running_event_id"], right["global_running_event_id"]))
    check("candidate_set_complete", {(row["left_event_id"], row["right_event_id"]) for row in pairs} == expected)
    check("expected_candidate_ids", expected == {("G407-E0019", "G407-E0020"), ("G407-E0187", "G407-E0189")})

    arms_by_pair: dict[str, list[dict[str, str]]] = {}
    for row in arms:
        arms_by_pair.setdefault(row["source_repeated_package_pair_id"], []).append(row)
    for index, pair in enumerate(pairs, start=1):
        prefix = f"pair_{index:02d}"
        left = clause_by_event[pair["left_event_id"]]
        right = clause_by_event[pair["right_event_id"]]
        left_state = stream_by_event[pair["left_event_id"]]
        right_state = stream_by_event[pair["right_event_id"]]
        gap = int(pair["intervening_card_count"])
        left_index = clauses.index(left)
        middle = clauses[left_index + 1 : left_index + 1 + gap]
        check(prefix + "_same_source_context", left["register"] == right["register"] == pair["register"] == "SOURCE_SECTION_T" and left["global_statement_id"] == right["global_statement_id"] == pair["global_statement_id"])
        check(prefix + "_same_owner", left["owner_de"] == right["owner_de"] == pair["owner_de"] and left["owner_class"] == right["owner_class"] == pair["owner_class"])
        check(prefix + "_ordinal_gap", int(right["card_ordinal_in_statement"]) == int(left["card_ordinal_in_statement"]) + gap + 1)
        check(prefix + "_shared_action_trace", left["explicit_action_roots"] == right["explicit_action_roots"] == pair["shared_action_roots"] == "CH|T")
        check(prefix + "_one_ch_per_endpoint", left["component_recipe"].split("+").count("CH") == right["component_recipe"].split("+").count("CH") == 1)
        check(prefix + "_no_explicit_arguments", left["explicit_argument_roots"] == right["explicit_argument_roots"] == "NONE")
        check(prefix + "_shared_inherited_argument", left["inherited_argument_root"] == right["inherited_argument_root"] == pair["shared_inherited_argument_root"] == "AIIN")
        check(prefix + "_state_left", left_state["active_argument_before"] == left_state["active_argument_after"] == "AIIN")
        check(prefix + "_state_right", right_state["active_argument_before"] == right_state["active_argument_after"] == "AIIN")
        check(prefix + "_factor_left", pair["left_factorized_action_replay_status"] == factor_by_event[pair["left_event_id"]]["factorized_action_replay_status"] == "CROSS_PAGE_ACTION_FACTORS_COMPLETE")
        check(prefix + "_factor_right", pair["right_factorized_action_replay_status"] == factor_by_event[pair["right_event_id"]]["factorized_action_replay_status"] == "CROSS_PAGE_ACTION_FACTORS_COMPLETE")
        check(prefix + "_source_recipes", pair["left_component_recipe"] == left["component_recipe"] and pair["right_component_recipe"] == right["component_recipe"])
        check(prefix + "_source_clauses", pair["left_imperative_clause_de"] == left["imperative_clause_de"] and pair["right_imperative_clause_de"] == right["imperative_clause_de"])
        check(prefix + "_middle_count", len(middle) == gap)
        if middle:
            check(prefix + "_middle_id", pair["intervening_event_ids"] == "|".join(row["global_running_event_id"] for row in middle))
            check(prefix + "_middle_argument", all(stream_by_event[row["global_running_event_id"]]["active_argument_after"] == "AIIN" for row in middle) and pair["middle_preserves_or_reasserts_argument"] == "YES")
        else:
            check(prefix + "_no_middle", pair["intervening_event_ids"] == "NONE")
        if pair["package_relation"] == "EXACT_DUPLICATED_PACKAGE":
            check(prefix + "_exact_repeat", left["surface"] == right["surface"] and left["component_recipe"] == right["component_recipe"] and left["imperative_clause_de"] == right["imperative_clause_de"])
            check(prefix + "_exact_flags", pair["same_surface"] == pair["same_component_recipe"] == pair["same_imperative_clause"] == "YES")
        else:
            check(prefix + "_prefix_extension", right["component_recipe"].startswith(left["component_recipe"] + "+") and pair["shared_component_prefix"] == left["component_recipe"])
            check(prefix + "_extension_flags", pair["same_surface"] == pair["same_component_recipe"] == pair["same_imperative_clause"] == "NO")
        check(prefix + "_projection", pair["projected_target_action_recipe"] == "CH+CH" and pair["projected_fluent_default_de"] == fluency_card["current_default_phrase_de"])
        check(prefix + "_guard", pair["guard"] == GUARD)
        pair_arms = arms_by_pair[pair["source_repeated_package_pair_id"]]
        check(prefix + "_two_arms", len(pair_arms) == 2 and {row["side"] for row in pair_arms} == {"LEFT", "RIGHT"})

    for index, arm in enumerate(arms, start=1):
        prefix = f"arm_{index:02d}"
        source = clause_by_event[arm["source_event_id"]]
        recipe = source["component_recipe"].split("+")
        removed = recipe.copy()
        removed.remove("CH")
        state = stream_by_event[arm["source_event_id"]]
        check(prefix + "_source_recipe", arm["source_component_recipe"] == source["component_recipe"])
        check(prefix + "_retained_ch", arm["retained_target_action_root"] == "CH" and int(arm["retained_ch_component_position"]) == recipe.index("CH") + 1)
        check(prefix + "_removed_atoms", arm["removed_package_atoms"] == "+".join(removed) and int(arm["removed_package_atom_count"]) == len(removed))
        check(prefix + "_removed_values", arm["removed_package_values_de"] == " · ".join(values[atom] for atom in removed))
        check(prefix + "_argument", arm["inherited_argument_root"] == source["inherited_argument_root"] == "AIIN")
        check(prefix + "_state", arm["stream_active_argument_before"] == state["active_argument_before"] == "AIIN" and arm["stream_active_argument_after"] == state["active_argument_after"] == "AIIN")
        check(prefix + "_slot", arm["target_action_slot_retained"] == "YES" and int(arm["target_action_slot_ordinal"]) in {1, 2})
        check(prefix + "_frame_not_transferred", arm["foreign_package_frame_transferred"] == "NO")
        check(prefix + "_guard", arm["guard"] == GUARD)

    target = target_rows[0]
    check("target_source_link", target["source_gdt507_target_context_bridge_card_id"] == old_target["target_context_bridge_card_id"])
    check("target_identity", target["target_matrix_cell_id"] == old_target["target_matrix_cell_id"] == "G498-M456" and target["target_action_recipe"] == "CH+CH" and target["target_register"] == "SOURCE_SECTION_T")
    check("target_phrase", target["target_current_default_phrase_de"] == old_target["target_current_default_phrase_de"] == fluency_card["current_default_phrase_de"])
    check("target_compression", target["gdt500_compression_rule"] == fluency_card["compression_rule"] == "CH_CH_ACTIVE_ARGUMENT_TO_ZWEIMAL")
    check("target_old_cross", target["old_gdt507_context_bridge_locality"] == old_target["context_bridge_locality"] == "CROSS_REGISTER")
    check("target_new_local", target["new_context_support_locality"] == "LOCAL_SOURCE_PACKAGE_LEVEL" and target["target_bridge_status"] == "LOCAL_CONTEXT_BRIDGED_WORKING__TARGET_RECIPE_UNOBSERVED")
    check("target_selected_exact", target["selected_exact_duplicate_event_ids"] == "G407-E0019→G407-E0020")
    check("target_selected_gap", target["corroborating_event_ids"] == "G407-E0187→G407-E0188→G407-E0189")
    check("target_slots", int(target["retained_target_action_slots"]) == 2)
    check("target_all_local", target["all_four_gdt507_context_targets_have_local_support"] == "YES")
    check("target_status_retained", target["target_evidence_status_retained"] == old_target["target_evidence_status_retained"] == "COMPOSED_WORKING")
    check("target_invariants", target["target_phrase_changed"] == target["working_root_meaning_changed"] == target["surface_prediction_made"] == target["occurrence_prediction_made"] == "NO")
    check("target_guard", target["guard"] == GUARD)

    relations = Counter(row["package_relation"] for row in pairs)
    check("relation_counts", relations == Counter({"EXACT_DUPLICATED_PACKAGE": 1, "SHARED_PREFIX_PACKAGE_WITH_RIGHT_EXTENSION": 1}))
    check("result_status", result["status"] == STATUS)
    check("result_pair_counts", result["source_repeated_ch_package_pairs"] == 2 and result["exact_duplicated_package_pairs"] == 1 and result["one_intervening_card_package_pairs"] == 1)
    check("result_arm_counts", result["package_cancellation_arms"] == result["retained_ch_action_slots"] == 4)
    check("result_target", result["source_chch_target_cards"] == result["all_four_context_targets_have_local_support"] == 1)
    check("result_ceiling", result["target_recipe_observations"] == result["target_phrases_changed"] == result["working_root_meanings_changed"] == result["surface_predictions"] == result["occurrence_predictions"] == 0)
    check("result_guard", result["guard"] == GUARD)
    check("readable_status", STATUS in readable)
    check("readable_witnesses", all(event in readable for event in ("G407-E0019", "G407-E0020", "G407-E0187", "G407-E0188", "G407-E0189")))

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
