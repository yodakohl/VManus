#!/usr/bin/env python3
"""Validate the complete context-safe 110-cell GDT497 default deck."""

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
BASE = ROOT / "experiments/yolo/gdt497_complete_context_safe_tr_default_deck"
ART = BASE / "artifacts"
G493 = ROOT / "experiments/yolo/gdt493_owner_dependent_tr_realization_deck/artifacts"
G496 = ROOT / "experiments/yolo/gdt496_semantic_action_substitution_atlas/artifacts"

CELLS_IN = G493 / "gdt493_110_owner_frame_realization_cells.tsv"
STATE_FRAMES_IN = G493 / "gdt493_4_state_dependent_frames.tsv"
G496_CONTEXT_IN = G496 / "gdt496_9_context_safe_defaults.tsv"
DECK_OUT = ART / "gdt497_110_current_default_cells.tsv"
GENERALIZED_OUT = ART / "gdt497_23_context_generalized_composed_cells.tsv"
OBSERVED_STATE_OUT = ART / "gdt497_17_observed_state_examples.tsv"
PAIRS_OUT = ART / "gdt497_55_current_tr_pairs.tsv"
FRAMES_OUT = ART / "gdt497_11_frame_default_coverage.tsv"
REGISTERS_OUT = ART / "gdt497_5_register_default_coverage.tsv"
READABLE_OUT = ART / "GDT497_COMPLETE_CONTEXT_SAFE_TR_DEFAULT_DECK.md"
RESULT_OUT = ART / "gdt497_result.json"
VALIDATION_OUT = ART / "gdt497_validation.json"

STATUS = "ONE_HUNDRED_TEN_CURRENT_DEFAULTS__TWENTY_THREE_CONTEXT_GENERALIZED__THIRTY_SEVEN_OBSERVED_RETAINED"
GUARD = "CURRENT_WORKING_DEFAULT__NO_SURFACE_OR_OCCURRENCE_PREDICTION"


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames is None:
            raise ValueError(f"missing header: {path}")
        return list(reader.fieldnames), list(reader)


def generalize_phrase(phrase: str, frame: str) -> tuple[str, str, int]:
    pattern = r"\b(?:den|die|das) [^.;]+? \[wie zuvor\]"
    matches = list(re.finditer(pattern, phrase))
    expected = 2 if frame == "CH+@ACTION" else 1
    if len(matches) != expected:
        raise ValueError(f"inherited-noun count drift: {frame} {phrase}")
    index = 0

    def replace(_match: re.Match[str]) -> str:
        nonlocal index
        index += 1
        return "das zuvor Genannte" if index == 1 else "es"

    output = re.sub(pattern, replace, phrase)
    change = "COMPOSED_CONTEXT_NOUN_GENERALIZED"
    if frame == "@ACTION+OL":
        replacements = {
            "Weiter stelle das zuvor Genannte ein.": "Fahre fort, das zuvor Genannte einzustellen.",
            "Weiter kennzeichne das zuvor Genannte.": "Fahre fort, das zuvor Genannte zu kennzeichnen.",
            "Weiter markiere das zuvor Genannte.": "Fahre fort, das zuvor Genannte zu markieren.",
        }
        output = replacements[output]
        change = "COMPOSED_CONTEXT_NOUN_AND_CONTINUATION_FLUENCY"
    return output, change, expected


def main() -> int:
    _source_fields, source_cells = read_tsv(CELLS_IN)
    _state_fields, state_frames = read_tsv(STATE_FRAMES_IN)
    _g496_fields, g496_rows = read_tsv(G496_CONTEXT_IN)
    deck_fields, deck_rows = read_tsv(DECK_OUT)
    generalized_fields, generalized_rows = read_tsv(GENERALIZED_OUT)
    observed_fields, observed_rows = read_tsv(OBSERVED_STATE_OUT)
    pair_fields, pair_rows = read_tsv(PAIRS_OUT)
    _frame_fields, frame_rows = read_tsv(FRAMES_OUT)
    _register_fields, register_rows = read_tsv(REGISTERS_OUT)
    readable = READABLE_OUT.read_text(encoding="utf-8")
    result = json.loads(RESULT_OUT.read_text(encoding="utf-8"))

    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    check("source_cells_110", len(source_cells) == 110, f"rows={len(source_cells)}")
    check("source_state_frames_4", len(state_frames) == 4, f"rows={len(state_frames)}")
    check("gdt496_context_rows_9", len(g496_rows) == 9, f"rows={len(g496_rows)}")
    check("deck_rows_110", len(deck_rows) == 110, f"rows={len(deck_rows)}")
    check("generalized_rows_23", len(generalized_rows) == 23, f"rows={len(generalized_rows)}")
    check("observed_state_rows_17", len(observed_rows) == 17, f"rows={len(observed_rows)}")
    check("pair_rows_55", len(pair_rows) == 55, f"rows={len(pair_rows)}")
    check("frame_rows_11", len(frame_rows) == 11, f"rows={len(frame_rows)}")
    check("register_rows_5", len(register_rows) == 5, f"rows={len(register_rows)}")
    check("deck_ids_exact", [row["current_default_id"] for row in deck_rows] == [f"G497-D{i:03d}" for i in range(1, 111)], "D001..D110")
    check("context_ids_exact", [row["context_generalization_id"] for row in generalized_rows] == [f"G497-C{i:02d}" for i in range(1, 24)], "C01..C23")
    check("observed_ids_exact", [row["observed_state_example_id"] for row in observed_rows] == [f"G497-O{i:02d}" for i in range(1, 18)], "O01..O17")
    check("pair_ids_exact", [row["current_pair_id"] for row in pair_rows] == [f"G497-TR{i:02d}" for i in range(1, 56)], "TR01..TR55")

    required_deck = {
        "source_realization_cell_id",
        "previous_display_phrase_de",
        "current_default_phrase_de",
        "current_default_policy",
        "editorial_change_type",
        "context_argument_policy",
        "guard",
    }
    required_generalized = {
        "previous_y_default_phrase_de",
        "context_safe_default_phrase_de",
        "same_frame_observed_argument_roots",
        "observed_state_examples_de",
    }
    required_observed = {"observed_phrase_de", "observed_inherited_argument_roots", "observed_event_ids"}
    required_pair = {"t_current_phrase_de", "r_current_phrase_de", "current_phrases_distinct"}
    check("deck_schema_complete", required_deck <= set(deck_fields), f"fields={len(deck_fields)}")
    check("generalized_schema_complete", required_generalized <= set(generalized_fields), f"fields={len(generalized_fields)}")
    check("observed_schema_complete", required_observed <= set(observed_fields), f"fields={len(observed_fields)}")
    check("pair_schema_complete", required_pair <= set(pair_fields), f"fields={len(pair_fields)}")

    source_by_id = {row["realization_cell_id"]: row for row in source_cells}
    deck_by_source = {row["source_realization_cell_id"]: row for row in deck_rows}
    generalized_by_source = {row["source_realization_cell_id"]: row for row in generalized_rows}
    observed_by_source = {row["source_realization_cell_id"]: row for row in observed_rows}
    observed_state_source = [
        row for row in source_cells
        if row["state_requirement"] == "ACTIVE_ARGUMENT_REQUIRED" and row["evidence_status"] == "OBSERVED_CLAUSE"
    ]
    composed_state_source = [
        row for row in source_cells
        if row["state_requirement"] == "ACTIVE_ARGUMENT_REQUIRED" and row["evidence_status"] == "COMPOSED_WORKING"
    ]
    check("source_state_partition_17_23", len(observed_state_source) == 17 and len(composed_state_source) == 23, f"observed={len(observed_state_source)} composed={len(composed_state_source)}")

    policy_counts: Counter[str] = Counter()
    for index, deck in enumerate(deck_rows, start=1):
        source = source_by_id[deck["source_realization_cell_id"]]
        if source["evidence_status"] == "OBSERVED_CLAUSE":
            expected_phrase = source["display_phrase_de"]
            expected_policy = "OBSERVED_CLAUSE_RETAINED"
            expected_change = "UNCHANGED_OBSERVED"
            expected_nouns = 0
            expected_context_policy = "USE_EXACT_OBSERVED_ARGUMENT"
        elif source["state_requirement"] == "SELF_CONTAINED_ARGUMENT":
            expected_phrase = source["display_phrase_de"]
            expected_policy = "COMPOSED_SELF_CONTAINED_RETAINED"
            expected_change = "UNCHANGED_SELF_CONTAINED"
            expected_nouns = 0
            expected_context_policy = "EXPLICIT_IN_RECIPE"
        else:
            expected_phrase, expected_change, expected_nouns = generalize_phrase(source["display_phrase_de"], source["frozen_frame"])
            expected_policy = "COMPOSED_CONTEXT_SAFE_GENERALIZED"
            expected_context_policy = "INHERIT_LIVE_ARGUMENT"
        policy_counts[deck["current_default_policy"]] += 1
        check(
            f"deck_{index:03d}_source_fields_exact",
            deck["frame_id"] == source["frame_id"]
            and deck["frozen_frame"] == source["frozen_frame"]
            and deck["action_root"] == source["action_root"]
            and deck["action_recipe"] == source["action_recipe"]
            and deck["register"] == source["register"]
            and deck["portable_component_trace_de"] == source["portable_component_trace_de"]
            and deck["owner_local_slot_trace_de"] == source["owner_local_slot_trace_de"]
            and deck["state_requirement"] == source["state_requirement"],
            source["realization_cell_id"],
        )
        check(
            f"deck_{index:03d}_default_policy_exact",
            deck["previous_display_phrase_de"] == source["display_phrase_de"]
            and deck["current_default_phrase_de"] == expected_phrase
            and deck["current_default_policy"] == expected_policy
            and deck["editorial_change_type"] == expected_change
            and int(deck["generalized_inherited_noun_count"]) == expected_nouns
            and deck["context_argument_policy"] == expected_context_policy,
            f"{expected_policy}: {expected_phrase}",
        )
        check(
            f"deck_{index:03d}_evidence_exact",
            deck["evidence_status_retained"] == source["evidence_status"]
            and deck["display_phrase_provenance_retained"] == source["display_phrase_provenance"]
            and deck["observed_event_count_retained"] == source["observed_event_count"]
            and deck["observed_clause_form_count_retained"] == source["observed_clause_form_count"]
            and deck["observed_pages_retained"] == source["observed_pages"]
            and deck["observed_event_ids_retained"] == source["observed_event_ids"]
            and deck["all_observed_clause_forms_de_retained"] == source["all_observed_clause_forms_de"]
            and deck["observed_inherited_argument_roots_retained"] == source["observed_inherited_argument_roots"],
            source["realization_cell_id"],
        )
        check(
            f"deck_{index:03d}_integrity_guards",
            deck["all_recipe_value_cells_observed"] == "YES"
            and deck["new_slot_value_required"] == "NO"
            and deck["working_root_meaning_changed"] == "NO"
            and deck["formal_frame_changed"] == "NO"
            and deck["evidence_status_changed"] == "NO"
            and deck["surface_prediction_made"] == "NO"
            and deck["occurrence_prediction_made"] == "NO"
            and deck["guard"] == GUARD,
            source["realization_cell_id"],
        )
        check(
            f"deck_{index:03d}_readable_present",
            deck["current_default_id"] in readable and deck["current_default_phrase_de"] in readable,
            deck["current_default_id"],
        )

    check("policy_counts_37_50_23", policy_counts == Counter({"COMPOSED_SELF_CONTAINED_RETAINED": 50, "OBSERVED_CLAUSE_RETAINED": 37, "COMPOSED_CONTEXT_SAFE_GENERALIZED": 23}), str(policy_counts))
    check("all_observed_phrases_byte_retained", all(deck_by_source[row["realization_cell_id"]]["current_default_phrase_de"] == row["display_phrase_de"] for row in source_cells if row["evidence_status"] == "OBSERVED_CLAUSE"), "37/37")
    check("all_self_contained_composed_phrases_retained", all(deck_by_source[row["realization_cell_id"]]["current_default_phrase_de"] == row["display_phrase_de"] for row in source_cells if row["evidence_status"] == "COMPOSED_WORKING" and row["state_requirement"] == "SELF_CONTAINED_ARGUMENT"), "50/50")
    check("all_composed_state_phrases_changed", all(deck_by_source[row["realization_cell_id"]]["current_default_phrase_de"] != row["display_phrase_de"] for row in composed_state_source), "23/23")
    check("all_composed_state_phrases_use_context_referent", all("das zuvor Genannte" in deck_by_source[row["realization_cell_id"]]["current_default_phrase_de"] for row in composed_state_source), "23/23")
    check("no_generalized_phrase_retains_wie_zuvor", all("[wie zuvor]" not in deck_by_source[row["realization_cell_id"]]["current_default_phrase_de"] for row in composed_state_source), "23/23")

    observed_by_frame: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in observed_state_source:
        observed_by_frame[row["frozen_frame"]].append(row)
    for index, row in enumerate(generalized_rows, start=1):
        source = source_by_id[row["source_realization_cell_id"]]
        deck = deck_by_source[source["realization_cell_id"]]
        frame_examples = observed_by_frame[source["frozen_frame"]]
        same_register = [item for item in frame_examples if item["register"] == source["register"]]
        same_action = [item for item in frame_examples if item["action_root"] == source["action_root"]]
        frame_roots = sorted({root for item in frame_examples for root in item["observed_inherited_argument_roots"].split("|") if root and root != "NONE"})
        check(
            f"generalized_{index:02d}_source_and_phrase_exact",
            row["current_default_id"] == deck["current_default_id"]
            and row["previous_y_default_phrase_de"] == source["display_phrase_de"]
            and row["context_safe_default_phrase_de"] == deck["current_default_phrase_de"]
            and row["editorial_change_type"] == deck["editorial_change_type"]
            and row["generalized_inherited_noun_count"] == deck["generalized_inherited_noun_count"],
            source["realization_cell_id"],
        )
        check(
            f"generalized_{index:02d}_frame_examples_exact",
            int(row["same_frame_observed_state_cell_count"]) == len(frame_examples)
            and row["same_frame_observed_state_cell_ids"] == "|".join(item["realization_cell_id"] for item in frame_examples)
            and row["same_frame_observed_argument_roots"] == "|".join(frame_roots)
            and int(row["same_register_observed_state_cell_count"]) == len(same_register)
            and row["same_register_observed_state_cell_ids"] == ("|".join(item["realization_cell_id"] for item in same_register) or "NONE")
            and int(row["same_action_observed_state_cell_count"]) == len(same_action)
            and row["same_action_observed_state_cell_ids"] == "|".join(item["realization_cell_id"] for item in same_action),
            f"frame={source['frozen_frame']} examples={len(frame_examples)}",
        )
        check(
            f"generalized_{index:02d}_guards",
            row["working_root_meaning_changed"] == "NO"
            and row["formal_frame_changed"] == "NO"
            and row["evidence_status_retained"] == "COMPOSED_WORKING"
            and row["surface_prediction_made"] == "NO"
            and row["occurrence_prediction_made"] == "NO"
            and row["guard"] == GUARD,
            row["context_generalization_id"],
        )
        check(
            f"generalized_{index:02d}_readable_present",
            row["context_generalization_id"] in readable
            and row["previous_y_default_phrase_de"] in readable
            and row["context_safe_default_phrase_de"] in readable,
            row["context_generalization_id"],
        )

    for index, row in enumerate(observed_rows, start=1):
        source = source_by_id[row["source_realization_cell_id"]]
        deck = deck_by_source[source["realization_cell_id"]]
        check(
            f"observed_state_{index:02d}_exact",
            source["evidence_status"] == "OBSERVED_CLAUSE"
            and source["state_requirement"] == "ACTIVE_ARGUMENT_REQUIRED"
            and row["current_default_id"] == deck["current_default_id"]
            and row["observed_phrase_de"] == source["display_phrase_de"]
            and row["all_observed_clause_forms_de"] == source["all_observed_clause_forms_de"]
            and row["observed_inherited_argument_roots"] == source["observed_inherited_argument_roots"]
            and row["observed_event_count"] == source["observed_event_count"]
            and row["observed_pages"] == source["observed_pages"]
            and row["observed_event_ids"] == source["observed_event_ids"]
            and row["observed_phrase_retained_exactly"] == "YES"
            and row["guard"] == GUARD,
            source["realization_cell_id"],
        )
    check("observed_state_source_set_exact", set(observed_by_source) == {row["realization_cell_id"] for row in observed_state_source}, "17 exact state cells")

    seen_pair_keys: set[tuple[str, str]] = set()
    for index, pair in enumerate(pair_rows, start=1):
        key = (pair["frozen_frame"], pair["register"])
        seen_pair_keys.add(key)
        targets = [row for row in deck_rows if row["frozen_frame"] == key[0] and row["register"] == key[1]]
        by_action = {row["action_root"]: row for row in targets}
        check(
            f"pair_{index:02d}_exact",
            len(targets) == 2
            and pair["t_current_default_id"] == by_action["T"]["current_default_id"]
            and pair["r_current_default_id"] == by_action["R"]["current_default_id"]
            and pair["t_current_phrase_de"] == by_action["T"]["current_default_phrase_de"]
            and pair["r_current_phrase_de"] == by_action["R"]["current_default_phrase_de"]
            and pair["current_phrases_distinct"] == "YES"
            and pair["formal_remainder_unchanged"] == "YES"
            and pair["both_context_safe"] == "YES"
            and pair["working_root_meaning_changed"] == "NO"
            and pair["guard"] == GUARD,
            f"{key[0]} {key[1]}",
        )
    check("pair_key_coverage_55", len(seen_pair_keys) == 55, f"keys={len(seen_pair_keys)}")

    check("frame_summary_cards_110", sum(int(row["current_default_count"]) for row in frame_rows) == 110, "sum=110")
    check("frame_summary_policies", sum(int(row["observed_retained_count"]) for row in frame_rows) == 37 and sum(int(row["composed_self_contained_retained_count"]) for row in frame_rows) == 50 and sum(int(row["composed_context_generalized_count"]) for row in frame_rows) == 23, "37/50/23")
    check("frame_summary_integrity", all(row["all_context_safe"] == row["all_meanings_retained"] == row["all_evidence_statuses_retained"] == "YES" for row in frame_rows), "11/11")
    check("register_summary_cards_110", sum(int(row["current_default_count"]) for row in register_rows) == 110, "sum=110")
    check("register_summary_policies", sum(int(row["observed_retained_count"]) for row in register_rows) == 37 and sum(int(row["composed_self_contained_retained_count"]) for row in register_rows) == 50 and sum(int(row["composed_context_generalized_count"]) for row in register_rows) == 23, "37/50/23")
    check("register_summary_integrity", all(row["all_context_safe"] == row["all_meanings_retained"] == row["all_evidence_statuses_retained"] == "YES" for row in register_rows), "5/5")
    check("readable_110_deck_rows", len(re.findall(r"^\| G497-D\d{3} \|", readable, flags=re.MULTILINE)) == 110, "110 table rows")
    check("readable_23_context_sections", len(re.findall(r"^### G497-C\d{2}", readable, flags=re.MULTILINE)) == 23, "23 sections")
    check("readable_17_observed_examples", all(row["observed_state_example_id"] in readable for row in observed_rows), "17 IDs")
    check("readable_no_f84", "f84" not in readable.lower(), "sealed folio absent")

    g496_by_key = {(row["action_recipe"], row["register"]): row for row in g496_rows}
    overlaps = [row for row in generalized_rows if (row["action_recipe"], row["register"]) in g496_by_key]
    expected_result = {
        "status": STATUS,
        "current_default_cells": 110,
        "observed_clauses_retained": 37,
        "composed_self_contained_retained": 50,
        "composed_context_generalized": 23,
        "state_dependent_cells": 40,
        "observed_state_examples": 17,
        "composed_state_defaults": 23,
        "inherited_noun_occurrences_generalized": sum(int(row["generalized_inherited_noun_count"]) for row in generalized_rows),
        "continuation_fluency_changes": sum(row["editorial_change_type"] == "COMPOSED_CONTEXT_NOUN_AND_CONTINUATION_FLUENCY" for row in generalized_rows),
        "gdt496_overlap_cells": len(overlaps),
        "gdt496_overlap_with_same_context_referent": sum("das zuvor Genannte" in row["context_safe_default_phrase_de"] for row in overlaps),
        "gdt496_overlap_exact_phrase": sum(row["context_safe_default_phrase_de"] == g496_by_key[(row["action_recipe"], row["register"])]["context_safe_default_de"] for row in overlaps),
        "current_tr_pairs": 55,
        "distinct_current_tr_pairs": sum(row["current_phrases_distinct"] == "YES" for row in pair_rows),
        "generalized_cells_with_frame_examples": sum(int(row["same_frame_observed_state_cell_count"]) > 0 for row in generalized_rows),
        "generalized_cells_with_same_action_examples": sum(int(row["same_action_observed_state_cell_count"]) > 0 for row in generalized_rows),
        "generalized_cells_with_same_register_examples": sum(int(row["same_register_observed_state_cell_count"]) > 0 for row in generalized_rows),
        "working_root_meaning_changes": sum(row["working_root_meaning_changed"] == "YES" for row in deck_rows),
        "formal_frame_changes": sum(row["formal_frame_changed"] == "YES" for row in deck_rows),
        "evidence_status_changes": sum(row["evidence_status_changed"] == "YES" for row in deck_rows),
        "surface_predictions": sum(row["surface_prediction_made"] == "YES" for row in deck_rows),
        "occurrence_predictions": sum(row["occurrence_prediction_made"] == "YES" for row in deck_rows),
        "frame_count": len(frame_rows),
        "register_count": len(register_rows),
        "guard": GUARD,
    }
    check("result_exact", result == expected_result, "result JSON reconstructed")
    check("result_31_noun_occurrences", result["inherited_noun_occurrences_generalized"] == 31, f"count={result['inherited_noun_occurrences_generalized']}")
    check("result_5_continuation_fluency_changes", result["continuation_fluency_changes"] == 5, f"count={result['continuation_fluency_changes']}")
    check("result_all_55_pairs_distinct", result["current_tr_pairs"] == result["distinct_current_tr_pairs"] == 55, "55/55")
    check("result_all_23_have_frame_and_action_examples", result["generalized_cells_with_frame_examples"] == result["generalized_cells_with_same_action_examples"] == 23, "23/23")
    check("result_zero_semantic_or_prediction_changes", all(result[key] == 0 for key in ("working_root_meaning_changes", "formal_frame_changes", "evidence_status_changes", "surface_predictions", "occurrence_predictions")), "all zero")

    failed = [entry for entry in checks if not entry["passed"]]
    payload = {
        "status": "PASS" if not failed else "FAIL",
        "checks_passed": len(checks) - len(failed),
        "checks_total": len(checks),
        "failed_checks": [entry["name"] for entry in failed],
        "checks": checks,
    }
    VALIDATION_OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ("status", "checks_passed", "checks_total", "failed_checks")}, ensure_ascii=False, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
