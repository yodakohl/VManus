#!/usr/bin/env python3
"""Independent validator for GDT511's complete local-linkage atlas."""

from __future__ import annotations

import csv
import json
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt511_schd_local_linkage_strength_atlas"
ART = BASE / "artifacts"
G416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts"
G436 = ROOT / "experiments/yolo/gdt436_streaming_context_intake_driver/artifacts"
G507 = ROOT / "experiments/yolo/gdt507_contextual_pair_argument_bridge_atlas/artifacts"
G510 = ROOT / "experiments/yolo/gdt510_four_cross_frame_local_factor_bridges/artifacts"

CLAUSES_IN = G416 / "gdt416_4576_imperative_clauses.tsv"
STREAM_IN = G436 / "gdt436_4576_oracle_free_stream_readings.tsv"
BENCHMARK_IN = G507 / "gdt507_13_adjacent_event_same_argument_bridges.tsv"
RECTANGLES_IN = G510 / "gdt510_3_schd_local_head_argument_rectangles.tsv"
UPGRADES_IN = G510 / "gdt510_4_cross_frame_target_local_upgrade_cards.tsv"

CANDIDATES_OUT = ART / "gdt511_62_schd_local_linkage_candidates.tsv"
CARDS_OUT = ART / "gdt511_3_register_linkage_strength_cards.tsv"
CORRIDORS_OUT = ART / "gdt511_88_selected_link_corridor_events.tsv"
BENCHMARK_OUT = ART / "gdt511_1_gdt507_immediate_bridge_benchmark.tsv"
READABLE_OUT = ART / "GDT511_SCHD_LOCAL_LINKAGE_STRENGTH_ATLAS.md"
RESULT_OUT = ART / "gdt511_result.json"
VALIDATION_OUT = ART / "gdt511_validation.json"

STATUS = "SOURCE_SAME_STATEMENT__PHARMA_SAME_OWNER_PAGE__CELESTIAL_SAME_PAGE__ZERO_IMMEDIATE_OR_Y_CONTINUOUS"
GUARD = "LINKAGE_STRENGTH_ONLY__LOCAL_HEAD_RECTANGLES_NOT_PROMOTED_TO_LOCAL_PAIR"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def y_mode(row: dict[str, str]) -> str | None:
    explicit = [] if row["explicit_argument_roots"] == "NONE" else row["explicit_argument_roots"].split("|")
    if "Y" in explicit:
        return "EXPLICIT_Y"
    if row["inherited_argument_root"] == "Y":
        return "INHERITED_Y"
    return None


def frame_atoms(row: dict[str, str], head: str) -> list[str]:
    atoms = row["component_recipe"].split("+")
    atoms.remove(head)
    if y_mode(row) == "EXPLICIT_Y":
        atoms.remove("Y")
    return atoms


def collapse(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if not result or result[-1] != value:
            result.append(value)
    return result


def expected_tier(row: dict[str, str]) -> str:
    if row["s_before_chd"] != "YES":
        return "R_REVERSE_CHD_BEFORE_S"
    if row["same_statement"] == "YES":
        return "A_LONG_SAME_STATEMENT_OWNER_PAGE"
    if row["same_owner"] == row["same_page"] == "YES":
        return "B_LONG_SAME_OWNER_PAGE"
    if row["same_page"] == "YES":
        return "C_LONG_SAME_PAGE_CROSS_OWNER"
    return "D_REGISTER_ONLY_CROSS_PAGE"


def main() -> int:
    clauses = read_tsv(CLAUSES_IN)
    stream = read_tsv(STREAM_IN)
    source_benchmark = read_tsv(BENCHMARK_IN)
    source_rectangles = read_tsv(RECTANGLES_IN)
    source_upgrades = read_tsv(UPGRADES_IN)
    candidates = read_tsv(CANDIDATES_OUT)
    cards = read_tsv(CARDS_OUT)
    corridors = read_tsv(CORRIDORS_OUT)
    benchmark = read_tsv(BENCHMARK_OUT)
    result = json.loads(RESULT_OUT.read_text(encoding="utf-8"))
    readable = READABLE_OUT.read_text(encoding="utf-8")

    clause_by_event = {row["global_running_event_id"]: row for row in clauses}
    stream_by_event = {row["event_id"]: row for row in stream}
    stream_position = {row["event_id"]: index for index, row in enumerate(stream)}
    rectangle_by_card = {row["source_gdt509_card_id"]: row for row in source_rectangles}
    targets = sorted(
        (row for row in source_upgrades if row["target_action_recipe"] == "S+CHD+Y"),
        key=lambda row: row["target_register"],
    )
    target_by_register = {row["target_register"]: row for row in targets}
    card_by_register = {row["target_register"]: row for row in cards}

    checks: list[tuple[str, bool]] = []

    def check(name: str, condition: bool) -> None:
        checks.append((name, bool(condition)))

    check("clause_count", len(clauses) == 4576)
    check("stream_count", len(stream) == 4576)
    check("source_benchmark_count", len(source_benchmark) == 13)
    check("source_rectangle_count", len(source_rectangles) == 3)
    check("source_upgrade_count", len(source_upgrades) == 4)
    check("target_count", len(targets) == 3)
    check("candidate_count", len(candidates) == 62)
    check("card_count", len(cards) == 3)
    check("corridor_count", len(corridors) == 88)
    check("benchmark_count", len(benchmark) == 1)
    check("register_set", set(card_by_register) == {"CELESTIAL", "PHARMA", "SOURCE_SECTION_T"})
    check("candidate_ids", [row["linkage_candidate_id"] for row in candidates] == [f"G511-L{i:03d}" for i in range(1, 63)])
    check("card_ids", [row["register_linkage_strength_card_id"] for row in cards] == [f"G511-C{i:02d}" for i in range(1, 4)])
    check("corridor_ids", [row["selected_corridor_event_id"] for row in corridors] == [f"G511-E{i:03d}" for i in range(1, 89)])
    check("all_guards", all(row["guard"] == GUARD for rows in (candidates, cards, corridors, benchmark) for row in rows))
    check("no_sealed_source_page", all(not row["physical_page"].startswith("f84") for row in clauses))

    candidate_by_key = {(row["target_register"], row["s_event_id"], row["chd_event_id"]): row for row in candidates}
    expected_keys: set[tuple[str, str, str]] = set()
    for register, target in target_by_register.items():
        s_events = [row for row in clauses if row["register"] == register and row["explicit_action_roots"] == "S" and y_mode(row)]
        chd_events = [row for row in clauses if row["register"] == register and row["explicit_action_roots"] == "CHD" and y_mode(row)]
        source_rectangle = rectangle_by_card[target["source_gdt509_card_id"]]
        check(register + "_source_head_counts", len(s_events) == int(source_rectangle["local_s_on_y_event_count"]) and len(chd_events) == int(source_rectangle["local_chd_on_y_event_count"]))
        for s_event in s_events:
            for chd_event in chd_events:
                s_id = s_event["global_running_event_id"]
                chd_id = chd_event["global_running_event_id"]
                key = (register, s_id, chd_id)
                expected_keys.add(key)
                row = candidate_by_key[key]
                label = row["linkage_candidate_id"]
                left = stream_position[s_id]
                right = stream_position[chd_id]
                low, high = sorted((left, right))
                interval = stream[low : high + 1]
                after = [item["active_argument_after"] for item in interval]
                runs = collapse(after)
                s_before = left < right
                same_page = s_event["physical_page"] == chd_event["physical_page"]
                same_owner = s_event["owner_de"] == chd_event["owner_de"]
                same_statement = s_event["global_statement_id"] == chd_event["global_statement_id"]
                gap = abs(right - left) - 1
                uninterrupted = all(value == "Y" for value in after)
                immediate = s_before and gap == 0 and same_page and same_owner and same_statement and uninterrupted
                gdt507_grade = immediate and y_mode(s_event) == y_mode(chd_event) == "INHERITED_Y"
                check(label + "_source_links", row["source_gdt510_rectangle_id"] == source_rectangle["local_head_argument_rectangle_id"] and row["source_gdt510_card_id"] == target["source_gdt509_card_id"] and row["target_matrix_cell_id"] == target["target_matrix_cell_id"])
                check(label + "_target", row["target_register"] == register and row["target_action_recipe"] == "S+CHD+Y")
                check(label + "_event_recipes", row["s_component_recipe"] == s_event["component_recipe"] and row["chd_component_recipe"] == chd_event["component_recipe"])
                check(label + "_y_modes", row["s_y_mode"] == y_mode(s_event) and row["chd_y_mode"] == y_mode(chd_event))
                check(label + "_frames", row["s_frame_atoms"] == ("+".join(frame_atoms(s_event, "S")) if frame_atoms(s_event, "S") else "NONE") and row["chd_frame_atoms"] == ("+".join(frame_atoms(chd_event, "CHD")) if frame_atoms(chd_event, "CHD") else "NONE"))
                check(label + "_direction", row["s_before_chd"] == ("YES" if s_before else "NO"))
                check(label + "_gap", int(row["intervening_event_count"]) == gap)
                check(label + "_locality_flags", row["same_page"] == ("YES" if same_page else "NO") and row["same_owner"] == ("YES" if same_owner else "NO") and row["same_statement"] == ("YES" if same_statement else "NO"))
                check(label + "_interval_counts", int(row["corridor_event_count"]) == len(interval) and int(row["corridor_page_count"]) == len({item["physical_page"] for item in interval}) and int(row["corridor_owner_count"]) == len({item["owner_de"] for item in interval}) and int(row["corridor_statement_count"]) == len({item["statement_id"] for item in interval}))
                check(label + "_argument_roots", row["corridor_argument_after_roots"] == "|".join(sorted(set(after))))
                check(label + "_argument_runs", row["corridor_argument_run_trace"] == ">".join(runs) and int(row["corridor_argument_state_change_count"]) == len(runs) - 1)
                check(label + "_argument_counts", int(row["corridor_active_y_event_count"]) == sum(value == "Y" for value in after) and int(row["corridor_non_y_event_count"]) == sum(value != "Y" for value in after))
                check(label + "_uninterrupted", row["active_y_uninterrupted"] == ("YES" if uninterrupted else "NO"))
                check(label + "_immediate", row["immediate_same_statement_same_y"] == ("YES" if immediate else "NO"))
                check(label + "_gdt507_grade", row["gdt507_grade_immediate_shared_inherited_argument"] == ("YES" if gdt507_grade else "NO"))
                check(label + "_tier", row["locality_tier"] == expected_tier(row))
    check("candidate_key_coverage", set(candidate_by_key) == expected_keys)

    total_ordered = 0
    total_reverse = 0
    total_same_page = 0
    total_same_owner = 0
    total_same_statement = 0
    total_immediate = 0
    total_one_gap = 0
    total_uninterrupted = 0
    total_within_forward = 0
    selected_expectation = {
        "CELESTIAL": ("G407-E1243", "G407-E1276", "C_LONG_SAME_PAGE_CROSS_OWNER", 32, 2, 2, 15),
        "PHARMA": ("G407-E3999", "G407-E4028", "B_LONG_SAME_OWNER_PAGE", 28, 4, 1, 11),
        "SOURCE_SECTION_T": ("G407-E0079", "G407-E0102", "A_LONG_SAME_STATEMENT_OWNER_PAGE", 22, 1, 1, 11),
    }
    for register, card in card_by_register.items():
        group = [row for row in candidates if row["target_register"] == register]
        ordered = [row for row in group if row["s_before_chd"] == "YES"]
        reverse = [row for row in group if row["s_before_chd"] == "NO"]
        selected = min(
            ordered,
            key=lambda row: (
                row["same_statement"] != "YES",
                row["same_owner"] != "YES",
                row["same_page"] != "YES",
                int(row["intervening_event_count"]),
                int(row["corridor_non_y_event_count"]),
                row["s_event_id"],
                row["chd_event_id"],
            ),
        )
        same_page_count = sum(row["same_page"] == "YES" for row in ordered)
        same_owner_count = sum(row["same_owner"] == "YES" for row in ordered)
        same_statement_count = sum(row["same_statement"] == "YES" for row in ordered)
        immediate_count = sum(int(row["intervening_event_count"]) == 0 for row in ordered)
        one_gap_count = sum(int(row["intervening_event_count"]) <= 1 for row in ordered)
        uninterrupted_count = sum(row["active_y_uninterrupted"] == "YES" for row in ordered)
        within_forward = 0
        within_reverse = 0
        for clause in clauses:
            if clause["register"] != register:
                continue
            actions = [] if clause["explicit_action_roots"] == "NONE" else clause["explicit_action_roots"].split("|")
            for index, left in enumerate(actions):
                for right in actions[index + 1 :]:
                    within_forward += (left, right) == ("S", "CHD")
                    within_reverse += (left, right) == ("CHD", "S")
        total_ordered += len(ordered)
        total_reverse += len(reverse)
        total_same_page += same_page_count
        total_same_owner += same_owner_count
        total_same_statement += same_statement_count
        total_immediate += immediate_count
        total_one_gap += one_gap_count
        total_uninterrupted += uninterrupted_count
        total_within_forward += within_forward
        source_rectangle = rectangle_by_card[card["source_gdt510_card_id"]]
        expected = selected_expectation[register]
        check(register + "_counts", int(card["local_rectangle_candidate_count"]) == len(group) and int(card["ordered_s_before_chd_candidate_count"]) == len(ordered) and int(card["reverse_chd_before_s_candidate_count"]) == len(reverse))
        check(register + "_local_counts", int(card["ordered_same_page_count"]) == same_page_count and int(card["ordered_same_owner_count"]) == same_owner_count and int(card["ordered_same_statement_count"]) == same_statement_count)
        check(register + "_close_counts", int(card["ordered_immediate_count"]) == immediate_count and int(card["ordered_zero_or_one_gap_count"]) == one_gap_count and int(card["ordered_uninterrupted_y_count"]) == uninterrupted_count and int(card["gdt507_grade_bridge_count"]) == 0)
        check(register + "_within_event_counts", int(card["target_register_within_event_s_before_chd_count"]) == within_forward and int(card["target_register_within_event_chd_before_s_count"]) == within_reverse)
        check(register + "_selected_algorithm", card["selected_linkage_candidate_id"] == selected["linkage_candidate_id"] and card["selected_s_event_id"] == selected["s_event_id"] and card["selected_chd_event_id"] == selected["chd_event_id"])
        check(register + "_selected_expected", (card["selected_s_event_id"], card["selected_chd_event_id"], card["selected_linkage_tier"], int(card["selected_intervening_event_count"]), int(card["selected_corridor_statement_count"]), int(card["selected_corridor_owner_count"]), int(card["selected_corridor_non_y_event_count"])) == expected)
        check(register + "_selected_run", card["selected_corridor_argument_run_trace"] == selected["corridor_argument_run_trace"])
        check(register + "_old_selection", card["gdt510_selected_s_event_id"] == source_rectangle["selected_s_event_id"] and card["gdt510_selected_chd_event_id"] == source_rectangle["selected_chd_event_id"])
        check(register + "_cross_pair", card["cross_register_pair_order_event_id"] == source_rectangle["cross_register_pair_order_evidence_ids"] == "G407-E1883")
        check(register + "_translation", card["working_translation_de"] == target_by_register[register]["working_translation_de"])
        check(register + "_status", card["linkage_status"] == "LOCAL_HEAD_INVENTORY_LINK_ONLY__CROSS_REGISTER_PAIR_ORDER_RETAINED")
        check(register + "_invariants", card["target_recipe_observed_exactly"] == card["target_phrase_changed"] == card["working_root_meaning_changed"] == card["surface_prediction_made"] == card["occurrence_prediction_made"] == "NO")

    check("total_ordered", total_ordered == 46)
    check("total_reverse", total_reverse == 16)
    check("total_same_page", total_same_page == 12)
    check("total_same_owner", total_same_owner == 2)
    check("total_same_statement", total_same_statement == 1)
    check("total_immediate", total_immediate == 0)
    check("total_one_gap", total_one_gap == 0)
    check("total_uninterrupted", total_uninterrupted == 0)
    check("total_within_forward", total_within_forward == 0)

    corridor_by_card: dict[str, list[dict[str, str]]] = {}
    for row in corridors:
        corridor_by_card.setdefault(row["register_linkage_strength_card_id"], []).append(row)
    check("corridor_card_coverage", set(corridor_by_card) == {row["register_linkage_strength_card_id"] for row in cards})
    for card in cards:
        group = corridor_by_card[card["register_linkage_strength_card_id"]]
        left = stream_position[card["selected_s_event_id"]]
        right = stream_position[card["selected_chd_event_id"]]
        expected_stream = stream[left : right + 1]
        check(card["target_register"] + "_corridor_length", len(group) == len(expected_stream))
        check(card["target_register"] + "_corridor_offsets", [int(row["corridor_offset"]) for row in group] == list(range(len(group))))
        for row, source in zip(group, expected_stream):
            label = row["selected_corridor_event_id"]
            endpoint = "S_ENDPOINT" if source["event_id"] == card["selected_s_event_id"] else "CHD_ENDPOINT" if source["event_id"] == card["selected_chd_event_id"] else "INTERVENING"
            check(label + "_card", row["target_register"] == card["target_register"] and row["selected_linkage_candidate_id"] == card["selected_linkage_candidate_id"])
            check(label + "_event", row["event_id"] == source["event_id"] and row["corridor_endpoint_role"] == endpoint)
            check(label + "_context", row["statement_id"] == source["statement_id"] and row["physical_page"] == source["physical_page"] and row["owner_de"] == source["owner_de"])
            check(label + "_surface_recipe", row["surface"] == source["surface"] and row["component_recipe"] == source["component_recipe"])
            check(label + "_roots", row["explicit_action_roots"] == source["explicit_action_roots"] and row["explicit_argument_roots"] == source["explicit_argument_roots"] and row["inherited_argument_root"] == source["inherited_argument_root"])
            check(label + "_state", row["active_argument_before"] == source["active_argument_before"] and row["active_argument_after"] == source["active_argument_after"] and row["active_argument_after_is_y"] == ("YES" if source["active_argument_after"] == "Y" else "NO"))
            check(label + "_reference", row["state_matches_reference"] == source["state_matches_reference"] == "YES")

    b = benchmark[0]
    check("benchmark_id", b["benchmark_card_id"] == "G511-B01")
    check("benchmark_source_count", int(b["source_gdt507_adjacent_bridge_count"]) == len(source_benchmark) == 13)
    check("benchmark_pairs", b["source_gdt507_ordered_pairs"] == "|".join(sorted({row["ordered_action_pair"] for row in source_benchmark})) == "CH+CH|CH+SH")
    check("benchmark_consecutive", b["source_gdt507_all_stream_consecutive"] == "YES" and all(row["stream_ordinals_consecutive"] == "YES" for row in source_benchmark))
    check("benchmark_shared_inherited", b["source_gdt507_all_shared_inherited_argument"] == "YES" and all(row["shared_inherited_argument_root"] != "NONE" for row in source_benchmark))
    check("benchmark_new_counts", int(b["gdt511_schd_ordered_rectangle_count"]) == total_ordered and int(b["gdt511_schd_same_statement_count"]) == total_same_statement and int(b["gdt511_schd_stream_consecutive_count"]) == total_immediate and int(b["gdt511_schd_uninterrupted_y_count"]) == total_uninterrupted and int(b["gdt511_gdt507_grade_bridge_count"]) == 0)
    check("benchmark_status", b["comparison_status"] == "NO_SCHD_LINK_MATCHES_GDT507_IMMEDIATE_SHARED_ARGUMENT_GRADE")

    check("target_recipes_absent", all(not any(row["register"] == target["target_register"] and row["component_recipe"] == "S+CHD+Y" for row in clauses) for target in targets))
    check("result_status", result["status"] == STATUS)
    check("result_base_counts", result["target_register_cards"] == 3 and result["local_rectangle_candidates"] == 62 and result["selected_corridor_events"] == 88)
    check("result_direction_counts", result["ordered_s_before_chd_candidates"] == total_ordered and result["reverse_chd_before_s_candidates"] == total_reverse)
    check("result_local_counts", result["ordered_same_page_candidates"] == total_same_page and result["ordered_same_owner_candidates"] == total_same_owner and result["ordered_same_statement_candidates"] == total_same_statement)
    check("result_zero_counts", result["ordered_immediate_candidates"] == result["ordered_zero_or_one_gap_candidates"] == result["ordered_uninterrupted_y_candidates"] == result["target_register_within_event_s_before_chd"] == result["gdt507_grade_bridges"] == 0)
    check("result_tiers", result["source_linkage_tier"] == "A_LONG_SAME_STATEMENT_OWNER_PAGE" and result["pharma_linkage_tier"] == "B_LONG_SAME_OWNER_PAGE" and result["celestial_linkage_tier"] == "C_LONG_SAME_PAGE_CROSS_OWNER")
    check("result_invariants", result["target_recipe_observations"] == result["target_phrases_changed"] == result["working_root_meanings_changed"] == result["surface_predictions"] == result["occurrence_predictions"] == 0)
    check("result_guard", result["guard"] == GUARD)
    check("readable_status", STATUS in readable)
    check("readable_selected", all(card["selected_s_event_id"] in readable and card["selected_chd_event_id"] in readable for card in cards))
    check("readable_cross_pair", "G407-E1883" in readable)
    check("readable_zero_claim", "Keines der 46" in readable)

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
