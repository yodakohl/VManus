#!/usr/bin/env python3
"""Independent validator for GDT510's four target-register factor bridges."""

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
BASE = ROOT / "experiments/yolo/gdt510_four_cross_frame_local_factor_bridges"
ART = BASE / "artifacts"
G413 = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts"
G416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts"
G425 = ROOT / "experiments/yolo/gdt425_complete_factorized_action_portability/artifacts"
G436 = ROOT / "experiments/yolo/gdt436_streaming_context_intake_driver/artifacts"
G509 = ROOT / "experiments/yolo/gdt509_eleven_pair_target_evidence_strength_deck/artifacts"

DICTIONARY_IN = G413 / "gdt413_46_component_working_dictionary.tsv"
CLAUSES_IN = G416 / "gdt416_4576_imperative_clauses.tsv"
FACTORS_IN = G425 / "gdt425_4576_event_factorized_action_replay.tsv"
STREAM_IN = G436 / "gdt436_4576_oracle_free_stream_readings.tsv"
DECK_IN = G509 / "gdt509_11_pair_target_evidence_strength_cards.tsv"

SUFFIX_OUT = ART / "gdt510_1_celestial_pch_local_suffix_carrier.tsv"
RECTANGLES_OUT = ART / "gdt510_3_schd_local_head_argument_rectangles.tsv"
WITNESSES_OUT = ART / "gdt510_6_schd_selected_head_witnesses.tsv"
UPGRADES_OUT = ART / "gdt510_4_cross_frame_target_local_upgrade_cards.tsv"
READABLE_OUT = ART / "GDT510_FOUR_CROSS_FRAME_LOCAL_FACTOR_BRIDGES.md"
RESULT_OUT = ART / "gdt510_result.json"
VALIDATION_OUT = ART / "gdt510_validation.json"

STATUS = "CELESTIAL_PCH_HAS_LOCAL_SUFFIX__THREE_SCHD_TARGETS_HAVE_LOCAL_HEAD_ARGUMENT_RECTANGLES"
GUARD = "LOCAL_FACTOR_BRIDGE_ONLY__BARE_TARGETS_UNOBSERVED__CROSS_PAIR_ORDER_RETAINED_WHERE_NEEDED"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def event_number(event_id: str) -> int:
    return int(event_id.rsplit("E", 1)[1])


def y_mode(row: dict[str, str]) -> str | None:
    explicit = [] if row["explicit_argument_roots"] == "NONE" else row["explicit_argument_roots"].split("|")
    if "Y" in explicit:
        return "EXPLICIT_Y"
    if row["inherited_argument_root"] == "Y":
        return "INHERITED_Y"
    return None


def residual_frame(row: dict[str, str], head: str) -> list[str]:
    atoms = row["component_recipe"].split("+")
    atoms.remove(head)
    if y_mode(row) == "EXPLICIT_Y":
        atoms.remove("Y")
    return atoms


def preferred_pair(pair: tuple[dict[str, str], dict[str, str]]) -> tuple[object, ...]:
    left, right = pair
    return (
        left["owner_de"] != right["owner_de"],
        left["physical_page"] != right["physical_page"],
        left["global_statement_id"] != right["global_statement_id"],
        event_number(left["global_running_event_id"]) > event_number(right["global_running_event_id"]),
        len(residual_frame(left, "S")) + len(residual_frame(right, "CHD")),
        abs(event_number(left["global_running_event_id"]) - event_number(right["global_running_event_id"])),
        left["global_running_event_id"],
        right["global_running_event_id"],
    )


def main() -> int:
    dictionary = read_tsv(DICTIONARY_IN)
    clauses = read_tsv(CLAUSES_IN)
    factors = read_tsv(FACTORS_IN)
    stream = read_tsv(STREAM_IN)
    deck = read_tsv(DECK_IN)
    suffix_rows = read_tsv(SUFFIX_OUT)
    rectangles = read_tsv(RECTANGLES_OUT)
    witnesses = read_tsv(WITNESSES_OUT)
    upgrades = read_tsv(UPGRADES_OUT)
    result = json.loads(RESULT_OUT.read_text(encoding="utf-8"))
    readable = READABLE_OUT.read_text(encoding="utf-8")

    values = {row["atom"]: row["working_value_de"] for row in dictionary}
    clause_by_event = {row["global_running_event_id"]: row for row in clauses}
    factor_by_event = {row["global_running_event_id"]: row for row in factors}
    stream_by_event = {row["event_id"]: row for row in stream}
    cross_cards = [row for row in deck if row["evidence_route"] == "B_CROSS_REGISTER_FRAME_REDUCTION"]
    cross_by_id = {row["evidence_strength_card_id"]: row for row in cross_cards}

    checks: list[tuple[str, bool]] = []

    def check(name: str, condition: bool) -> None:
        checks.append((name, bool(condition)))

    check("dictionary_count", len(dictionary) == 46)
    check("clause_count", len(clauses) == 4576)
    check("factor_count", len(factors) == 4576)
    check("stream_count", len(stream) == 4576)
    check("deck_count", len(deck) == 11)
    check("cross_card_count", len(cross_cards) == 4)
    check("cross_card_shape", {(r["target_register"], r["target_action_recipe"]) for r in cross_cards} == {
        ("CELESTIAL", "P+CH+E+Y"),
        ("CELESTIAL", "S+CHD+Y"),
        ("PHARMA", "S+CHD+Y"),
        ("SOURCE_SECTION_T", "S+CHD+Y"),
    })
    check("suffix_count", len(suffix_rows) == 1)
    check("rectangle_count", len(rectangles) == 3)
    check("witness_count", len(witnesses) == 6)
    check("upgrade_count", len(upgrades) == 4)
    check("guards", all(row["guard"] == GUARD for rows in (suffix_rows, rectangles, witnesses, upgrades) for row in rows))
    check("no_sealed_pages_in_sources", all(not row["physical_page"].startswith("f84") for row in clauses))

    pch = next(row for row in cross_cards if row["target_action_recipe"] == "P+CH+E+Y")
    target_atoms = pch["target_action_recipe"].split("+")
    local_hits: list[tuple[dict[str, str], int]] = []
    for clause in clauses:
        if clause["register"] != pch["target_register"]:
            continue
        atoms = clause["component_recipe"].split("+")
        for start in range(len(atoms) - len(target_atoms) + 1):
            if atoms[start : start + len(target_atoms)] == target_atoms:
                local_hits.append((clause, start))
    check("pch_unique_local_contiguous_hit", len(local_hits) == 1)
    source, start = local_hits[0]
    suffix = suffix_rows[0]
    source_atoms = source["component_recipe"].split("+")
    prefix_atoms = source_atoms[:start]
    trailing_atoms = source_atoms[start + len(target_atoms) :]
    check("suffix_source_card", suffix["source_gdt509_card_id"] == pch["evidence_strength_card_id"])
    check("suffix_target_identity", suffix["target_matrix_cell_id"] == pch["target_matrix_cell_id"] and suffix["target_register"] == pch["target_register"] and suffix["target_action_recipe"] == pch["target_action_recipe"])
    check("suffix_event_identity", suffix["global_running_event_id"] == source["global_running_event_id"] == "G407-E0966")
    check("suffix_source_identity", suffix["physical_page"] == source["physical_page"] and suffix["owner_de"] == source["owner_de"] and suffix["surface"] == source["surface"] and suffix["source_component_recipe"] == source["component_recipe"])
    check("suffix_positions", int(suffix["target_contiguous_start_position"]) == start + 1 and int(suffix["target_contiguous_end_position"]) == start + len(target_atoms))
    check("suffix_exact_flag", suffix["target_contiguous_exact"] == "YES")
    check("suffix_removed_atoms", suffix["removed_prefix_atoms"] == "+".join(prefix_atoms) and suffix["removed_suffix_atoms"] == ("+".join(trailing_atoms) if trailing_atoms else "NONE"))
    check("suffix_removed_values", suffix["removed_prefix_values_de"] == " · ".join(values[atom] for atom in prefix_atoms))
    check("suffix_retained_atoms", suffix["retained_target_atoms"] == "+".join(target_atoms))
    check("suffix_action_roots", suffix["source_explicit_action_roots"] == source["explicit_action_roots"] == "T|P|CH")
    check("suffix_argument_fields", suffix["explicit_argument_roots"] == source["explicit_argument_roots"] and suffix["inherited_argument_root"] == source["inherited_argument_root"])
    check("suffix_stream_fields", suffix["stream_active_argument_before"] == stream_by_event[source["global_running_event_id"]]["active_argument_before"] and suffix["stream_active_argument_after"] == stream_by_event[source["global_running_event_id"]]["active_argument_after"])
    check("suffix_stream_valid", suffix["stream_state_matches_reference"] == stream_by_event[source["global_running_event_id"]]["state_matches_reference"] == "YES")
    check("suffix_factor_valid", suffix["factorized_action_replay_status"] == factor_by_event[source["global_running_event_id"]]["factorized_action_replay_status"] == "CROSS_PAGE_ACTION_FACTORS_COMPLETE")
    check("suffix_translation_retained", suffix["target_working_translation_de"] == pch["working_translation_de"])
    check("suffix_upgrade_status", suffix["upgrade_status"] == "LOCAL_BROADER_CHAIN_CONTIGUOUS_SUFFIX_REDUCTION")
    check("suffix_target_unobserved", suffix["target_recipe_observed_exactly"] == "NO")

    rectangle_by_card = {row["source_gdt509_card_id"]: row for row in rectangles}
    witness_by_rectangle: dict[str, list[dict[str, str]]] = {}
    for witness in witnesses:
        witness_by_rectangle.setdefault(witness["local_head_argument_rectangle_id"], []).append(witness)
    schd_cards = sorted((row for row in cross_cards if row["target_action_recipe"] == "S+CHD+Y"), key=lambda row: row["target_register"])
    check("schd_card_count", len(schd_cards) == 3)
    check("rectangle_card_coverage", set(rectangle_by_card) == {row["evidence_strength_card_id"] for row in schd_cards})
    total_s = 0
    total_chd = 0
    total_pairs = 0
    for index, card in enumerate(schd_cards, start=1):
        prefix = f"schd_{index:02d}"
        rectangle = rectangle_by_card[card["evidence_strength_card_id"]]
        register = card["target_register"]
        s_rows = [row for row in clauses if row["register"] == register and row["explicit_action_roots"] == "S" and y_mode(row)]
        chd_rows = [row for row in clauses if row["register"] == register and row["explicit_action_roots"] == "CHD" and y_mode(row)]
        pairs = [(left, right) for left in s_rows for right in chd_rows]
        selected_s, selected_chd = min(pairs, key=preferred_pair)
        total_s += len(s_rows)
        total_chd += len(chd_rows)
        total_pairs += len(pairs)
        check(prefix + "_id", rectangle["local_head_argument_rectangle_id"] == f"G510-R{index:02d}")
        check(prefix + "_target_identity", rectangle["target_matrix_cell_id"] == card["target_matrix_cell_id"] and rectangle["target_register"] == register and rectangle["target_action_recipe"] == card["target_action_recipe"])
        check(prefix + "_counts", int(rectangle["local_s_on_y_event_count"]) == len(s_rows) and int(rectangle["local_chd_on_y_event_count"]) == len(chd_rows) and int(rectangle["local_s_chd_y_candidate_pair_count"]) == len(pairs))
        check(prefix + "_selected_events", rectangle["selected_s_event_id"] == selected_s["global_running_event_id"] and rectangle["selected_chd_event_id"] == selected_chd["global_running_event_id"])
        check(prefix + "_selected_pages", rectangle["selected_s_page"] == selected_s["physical_page"] and rectangle["selected_chd_page"] == selected_chd["physical_page"])
        check(prefix + "_selected_owners", rectangle["selected_s_owner_de"] == selected_s["owner_de"] and rectangle["selected_chd_owner_de"] == selected_chd["owner_de"])
        check(prefix + "_same_page", rectangle["selected_same_page"] == ("YES" if selected_s["physical_page"] == selected_chd["physical_page"] else "NO"))
        check(prefix + "_same_owner", rectangle["selected_same_owner"] == ("YES" if selected_s["owner_de"] == selected_chd["owner_de"] else "NO"))
        check(prefix + "_same_statement", rectangle["selected_same_statement"] == ("YES" if selected_s["global_statement_id"] == selected_chd["global_statement_id"] else "NO"))
        check(prefix + "_order", rectangle["selected_s_before_chd_in_stream"] == ("YES" if event_number(selected_s["global_running_event_id"]) < event_number(selected_chd["global_running_event_id"]) else "NO"))
        check(prefix + "_y_modes", rectangle["selected_s_y_mode"] == y_mode(selected_s) and rectangle["selected_chd_y_mode"] == y_mode(selected_chd))
        check(prefix + "_recipes", rectangle["selected_s_component_recipe"] == selected_s["component_recipe"] and rectangle["selected_chd_component_recipe"] == selected_chd["component_recipe"])
        check(prefix + "_frames", rectangle["selected_s_frame_atoms"] == ("+".join(residual_frame(selected_s, "S")) if residual_frame(selected_s, "S") else "NONE") and rectangle["selected_chd_frame_atoms"] == ("+".join(residual_frame(selected_chd, "CHD")) if residual_frame(selected_chd, "CHD") else "NONE"))
        check(prefix + "_cross_order", rectangle["cross_register_pair_order_evidence_ids"] == card["source_evidence_ids"] == "G407-E1883")
        check(prefix + "_translation", rectangle["target_working_translation_de"] == card["working_translation_de"])
        check(prefix + "_status", rectangle["rectangle_status"] == "LOCAL_S_ON_Y_PLUS_CHD_ON_Y__CROSS_REGISTER_S_TO_CHD_ORDER")
        check(prefix + "_target_unobserved", rectangle["target_recipe_observed_exactly"] == "NO")

        selected_witnesses = witness_by_rectangle.get(rectangle["local_head_argument_rectangle_id"], [])
        check(prefix + "_two_witnesses", len(selected_witnesses) == 2 and {row["action_head"] for row in selected_witnesses} == {"S", "CHD"})
        for witness in selected_witnesses:
            head = witness["action_head"]
            selected = selected_s if head == "S" else selected_chd
            event_id = selected["global_running_event_id"]
            check(prefix + "_" + head + "_event", witness["global_running_event_id"] == event_id)
            check(prefix + "_" + head + "_identity", witness["global_statement_id"] == selected["global_statement_id"] and witness["physical_page"] == selected["physical_page"] and witness["owner_de"] == selected["owner_de"] and witness["surface"] == selected["surface"])
            check(prefix + "_" + head + "_recipe", witness["component_recipe"] == selected["component_recipe"] and witness["y_mode"] == y_mode(selected))
            check(prefix + "_" + head + "_arguments", witness["explicit_argument_roots"] == selected["explicit_argument_roots"] and witness["inherited_argument_root"] == selected["inherited_argument_root"])
            frame = residual_frame(selected, head)
            check(prefix + "_" + head + "_frame", witness["non_head_non_y_frame_atoms"] == ("+".join(frame) if frame else "NONE") and witness["non_head_non_y_frame_values_de"] == (" · ".join(values[atom] for atom in frame) if frame else "NONE"))
            check(prefix + "_" + head + "_stream", witness["stream_active_argument_before"] == stream_by_event[event_id]["active_argument_before"] and witness["stream_active_argument_after"] == stream_by_event[event_id]["active_argument_after"] and witness["stream_state_matches_reference"] == stream_by_event[event_id]["state_matches_reference"] == "YES")
            check(prefix + "_" + head + "_factor", witness["factorized_action_replay_status"] == factor_by_event[event_id]["factorized_action_replay_status"] == "CROSS_PAGE_ACTION_FACTORS_COMPLETE")
            check(prefix + "_" + head + "_clause", witness["imperative_clause_de"] == selected["imperative_clause_de"])

    check("recomputed_s_total", total_s == 27)
    check("recomputed_chd_total", total_chd == 7)
    check("recomputed_pair_total", total_pairs == 62)
    check("all_selected_same_page", all(row["selected_same_page"] == "YES" for row in rectangles))
    check("two_selected_same_owner", sum(row["selected_same_owner"] == "YES" for row in rectangles) == 2)
    check("one_selected_same_statement", sum(row["selected_same_statement"] == "YES" for row in rectangles) == 1)
    check("all_selected_ordered", all(row["selected_s_before_chd_in_stream"] == "YES" for row in rectangles))

    upgrade_by_card = {row["source_gdt509_card_id"]: row for row in upgrades}
    check("upgrade_card_coverage", set(upgrade_by_card) == set(cross_by_id))
    check("upgrade_ids_unique", {row["cross_frame_local_upgrade_card_id"] for row in upgrades} == {f"G510-T{i:02d}" for i in range(1, 5)})
    for card_id, card in cross_by_id.items():
        upgrade = upgrade_by_card[card_id]
        label = card["target_register"] + "_" + card["ordered_action_pair"]
        check(label + "_upgrade_identity", upgrade["target_matrix_cell_id"] == card["target_matrix_cell_id"] and upgrade["target_register"] == card["target_register"] and upgrade["target_action_recipe"] == card["target_action_recipe"])
        check(label + "_upgrade_translation", upgrade["working_translation_de"] == card["working_translation_de"])
        check(label + "_old_route", upgrade["old_gdt509_evidence_route"] == card["evidence_route"] == "B_CROSS_REGISTER_FRAME_REDUCTION")
        if card["target_action_recipe"] == "P+CH+E+Y":
            check(label + "_mechanism", upgrade["new_local_support_mechanism"] == "LOCAL_BROADER_CHAIN_CONTIGUOUS_SUFFIX_REDUCTION" and upgrade["new_support_locality"] == "LOCAL_TARGET_REGISTER")
            check(label + "_evidence", upgrade["local_and_cross_evidence_ids"] == source["global_running_event_id"])
        else:
            rectangle = rectangle_by_card[card_id]
            expected_ids = f"{rectangle['selected_s_event_id']}|{rectangle['selected_chd_event_id']}|{card['source_evidence_ids']}"
            check(label + "_mechanism", upgrade["new_local_support_mechanism"] == "LOCAL_HEAD_ARGUMENT_RECTANGLE_PLUS_CROSS_REGISTER_PAIR_ORDER" and upgrade["new_support_locality"] == "LOCAL_HEAD_ARGUMENT_FACTORS__CROSS_PAIR_ORDER")
            check(label + "_evidence", upgrade["local_and_cross_evidence_ids"] == expected_ids)
        check(label + "_status", upgrade["target_bridge_status"] == "LOCAL_FACTOR_BRIDGED_WORKING__TARGET_RECIPE_UNOBSERVED")
        check(label + "_evidence_retained", upgrade["target_evidence_status_retained"] == card["target_evidence_status_retained"] == "COMPOSED_WORKING")
        check(label + "_invariants", upgrade["target_phrase_changed"] == upgrade["working_root_meaning_changed"] == upgrade["surface_prediction_made"] == upgrade["occurrence_prediction_made"] == "NO")

    check("all_target_recipes_absent", all(not any(row["register"] == card["target_register"] and row["component_recipe"] == card["target_action_recipe"] for row in clauses) for card in cross_cards))
    check("result_status", result["status"] == STATUS)
    check("result_primary_counts", result["cross_frame_target_cards"] == 4 and result["celestial_pch_local_contiguous_suffix_carriers"] == 1 and result["schd_local_head_argument_rectangles"] == 3)
    check("result_recomputed_counts", result["schd_local_s_on_y_events"] == total_s and result["schd_local_chd_on_y_events"] == total_chd and result["schd_local_candidate_head_pairs"] == total_pairs)
    check("result_witness_upgrade_counts", result["selected_local_head_witnesses"] == 6 and result["upgraded_target_cards"] == 4)
    check("result_local_ceiling", result["all_eleven_pair_targets_now_have_some_local_support"] == 1 and result["schd_cards_still_using_cross_register_pair_order"] == 3)
    check("result_no_changes", result["target_recipe_observations"] == result["target_phrases_changed"] == result["working_root_meanings_changed"] == result["surface_predictions"] == result["occurrence_predictions"] == 0)
    check("result_guard", result["guard"] == GUARD)
    check("readable_status", STATUS in readable)
    check("readable_suffix", source["global_running_event_id"] in readable and source["component_recipe"] in readable)
    check("readable_rectangles", all(row["selected_s_event_id"] in readable and row["selected_chd_event_id"] in readable for row in rectangles))
    check("readable_cross_order", "G407-E1883" in readable)
    check("readable_target_phrases", pch["working_translation_de"] in readable)

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
