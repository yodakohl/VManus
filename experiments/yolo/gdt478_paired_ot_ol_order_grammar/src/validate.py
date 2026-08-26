#!/usr/bin/env python3
"""Validate the GDT478 paired OT/OL order grammar."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt478_paired_ot_ol_order_grammar"
OUT = BASE / "artifacts"
RUN = BASE / "src/run.py"
G460 = ROOT / "experiments/yolo/gdt460_learned_label_edge_stem_atlas/artifacts"
G461 = ROOT / "experiments/yolo/gdt461_internal_stem_residual_bridge/artifacts"
G474 = ROOT / "experiments/yolo/gdt474_locus_bundle_meaning_triptych/artifacts"
G475 = ROOT / "experiments/yolo/gdt475_ot_ol_page_microrecord_itineraries/artifacts"
G476 = ROOT / "experiments/yolo/gdt476_boundary_context_tie_resolution/artifacts"
G477 = ROOT / "experiments/yolo/gdt477_ol_directional_scope_phrasebook/artifacts"
EDGES_IN = G460 / "gdt460_27_calibrated_edge_stems.tsv"
INTERNALS_IN = G461 / "gdt461_9_calibrated_internal_stems.tsv"
EVENTS_IN = G474 / "gdt474_183_event_meaning_triptych.tsv"
ORDER_IN = G475 / "gdt475_69_order_occurrence_positions.tsv"
BOUNDARIES_IN = G475 / "gdt475_146_bundle_boundary_roles.tsv"
DECISIONS_IN = G476 / "gdt476_64_tie_context_decisions.tsv"
OL_SCOPE_IN = G477 / "gdt477_28_ol_directional_scope_occurrences.tsv"
OL_RULES_IN = G477 / "gdt477_3_directional_scope_rules.tsv"
PAIRED = OUT / "gdt478_69_paired_order_scope_occurrences.tsv"
EVENTS = OUT / "gdt478_60_paired_order_event_editions.tsv"
RULES = OUT / "gdt478_5_paired_order_scope_rules.tsv"
JOINT = OUT / "gdt478_7_ot_ol_joint_events.tsv"
PAGES = OUT / "gdt478_6_page_order_summary.tsv"
READABLE = OUT / "GDT478_PAIRED_OT_OL_ORDER_GRAMMAR.md"
RESULT = OUT / "gdt478_result.json"
VALIDATION = OUT / "gdt478_validation.json"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object) -> None:
        checks.append({"name": name, "pass": bool(condition), "detail": detail})

    generated = [PAIRED, EVENTS, RULES, JOINT, PAGES, READABLE, RESULT]
    check("all_outputs_present", all(path.is_file() for path in generated), [path.name for path in generated])
    if not all(path.is_file() for path in generated):
        raise RuntimeError("Run GDT478 builder before validation")
    before = {path.name: sha256(path) for path in generated}
    completed = subprocess.run([sys.executable, str(RUN)], cwd=ROOT, capture_output=True, text=True, check=False)
    after = {path.name: sha256(path) for path in generated}
    check("builder_exit_zero", completed.returncode == 0, completed.stderr[-1000:])
    check("deterministic_rebuild", before == after, {"before": before, "after": after})

    edges = read_tsv(EDGES_IN)
    internals = read_tsv(INTERNALS_IN)
    source_events = read_tsv(EVENTS_IN)
    source_order = read_tsv(ORDER_IN)
    boundaries = read_tsv(BOUNDARIES_IN)
    decisions = read_tsv(DECISIONS_IN)
    ol_scope = read_tsv(OL_SCOPE_IN)
    ol_rules = read_tsv(OL_RULES_IN)
    paired = read_tsv(PAIRED)
    events = read_tsv(EVENTS)
    rules = read_tsv(RULES)
    joint = read_tsv(JOINT)
    pages = read_tsv(PAGES)
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    event_map = {row["source_event_id"]: row for row in source_events}
    boundary_map = {row["bundle_id"]: row for row in boundaries}
    decision_map = {row["bundle_id"]: row for row in decisions}
    ol_map = {row["order_occurrence_id"]: row for row in ol_scope}

    check("input_edges_27", len(edges) == 27, len(edges))
    check("input_internals_9", len(internals) == 9, len(internals))
    check("input_events_183", len(source_events) == 183, len(source_events))
    check("input_order_69", len(source_order) == 69, len(source_order))
    check("input_boundaries_146", len(boundaries) == 146, len(boundaries))
    check("input_decisions_64", len(decisions) == 64, len(decisions))
    check("input_ol_scope_28", len(ol_scope) == 28, len(ol_scope))
    check("input_ol_rules_3", len(ol_rules) == 3, len(ol_rules))
    check("paired_rows_69", len(paired) == 69, len(paired))
    check("paired_ids_unique", len({row["paired_scope_id"] for row in paired}) == 69, len({row["paired_scope_id"] for row in paired}))
    check("occurrence_order_exact", [row["order_occurrence_id"] for row in paired] == [row["order_occurrence_id"] for row in source_order], "69/69")
    check("root_sequence_exact", [row["root"] for row in paired] == [row["root"] for row in source_order], "69/69")
    check("root_counts_41_28", Counter(row["root"] for row in paired) == Counter({"OT": 41, "OL": 28}), dict(Counter(row["root"] for row in paired)))
    for field in ("source_event_id", "bundle_id", "record_id", "physical_page", "locus", "surface", "working_recipe"):
        check(f"source_{field}_exact", all(row[field] == source[field] for row, source in zip(paired, source_order, strict=True)), "69/69")
    check("source_literal_exact", all(row["literal_working_reading_de"] == event_map[row["source_event_id"]]["literal_working_reading_de"] for row in paired), "69/69")
    check("boundary_roles_exact", all(row["boundary_role"] == boundary_map[row["bundle_id"]]["boundary_role"] for row in paired), "69/69")
    check("position_roles_exact", all(row["gdt475_position_role"] == source["position_role"] for row, source in zip(paired, source_order, strict=True)), "69/69")
    check("stream_interpretations_exact", all(row["gdt475_stream_interpretation"] == source["stream_interpretation"] for row, source in zip(paired, source_order, strict=True)), "69/69")

    ot = [row for row in paired if row["root"] == "OT"]
    ol = [row for row in paired if row["root"] == "OL"]
    check("ot_scope_counts_40_1", Counter(row["scope_orientation"] for row in ot) == Counter({"FORWARD_OPEN": 40, "BRIDGE_LEFT_TO_RIGHT": 1}), dict(Counter(row["scope_orientation"] for row in ot)))
    check("ot_no_backward", not any(row["scope_orientation"] == "BACKWARD_HOLD" for row in ot), "0")
    check("ot_name_counts_25_15_1", Counter(row["name_relative_position"] for row in ot) == Counter({"NAME_FREE": 25, "PRE_NAME": 15, "BETWEEN_NAMES": 1}), dict(Counter(row["name_relative_position"] for row in ot)))
    check("ot_no_post_name", not any(row["name_relative_position"] == "POST_NAME" for row in ot), "0")
    check("ot_all_have_right_successor", all(row["right_token"] != "NONE" for row in ot), "41/41")
    check("ot_forward_literal_first", all(int(row["literal_token_ordinal"]) == 1 for row in ot if row["scope_orientation"] == "FORWARD_OPEN"), "40/40")
    check("ot_bridge_literal_medial", all(1 < int(row["literal_token_ordinal"]) < int(row["literal_token_count"]) for row in ot if row["scope_orientation"] == "BRIDGE_LEFT_TO_RIGHT"), "1/1")
    check("ot_forward_positions_39_1", Counter(row["gdt475_position_role"] for row in ot if row["scope_orientation"] == "FORWARD_OPEN") == Counter({"BUNDLE_LEADING": 39, "LATER_EVENT_LEADING": 1}), dict(Counter(row["gdt475_position_role"] for row in ot if row["scope_orientation"] == "FORWARD_OPEN")))
    bridge = [row for row in ot if row["scope_orientation"] == "BRIDGE_LEFT_TO_RIGHT"]
    check("ot_bridge_is_dotedy", len(bridge) == 1 and bridge[0]["surface"] == "dotedy" and bridge[0]["left_token"] == "[BADSTATIONSNAME:d]" and bridge[0]["right_token"] == "[BADSTATIONSNAME:edy]", bridge)
    check("ot_bridge_phrase_exact", bridge[0]["directional_scope_phrase_de"] == "nach Badstation »d« folgt Badstation »edy«", bridge[0]["directional_scope_phrase_de"])
    check("ot_model_counts", Counter(row["context_selected_model"] for row in ot) == Counter({"COORDINATE": 21, "CATALOGUE": 16, "INSTRUCTION": 4}), dict(Counter(row["context_selected_model"] for row in ot)))
    check("ot_context_readings_match", all(row["context_selected_event_reading_de"] == event_map[row["source_event_id"]][f"{row['context_selected_model'].lower()}_event_reading_de"] for row in ot), "41/41")

    check("ol_fields_replay_gdt477", all(
        row["scope_orientation"] == ol_map[row["order_occurrence_id"]]["scope_orientation"]
        and row["name_relative_position"] == ol_map[row["order_occurrence_id"]]["name_relative_position"]
        and row["directional_scope_phrase_de"] == ol_map[row["order_occurrence_id"]]["directional_scope_phrase_de"]
        and row["marked_literal_working_reading_de"] == ol_map[row["order_occurrence_id"]]["marked_literal_working_reading_de"]
        for row in ol
    ), "28/28")
    check("ol_scope_counts_9_10_9", Counter(row["scope_orientation"] for row in ol) == Counter({"BRIDGE_LEFT_TO_RIGHT": 10, "FORWARD_OPEN": 9, "BACKWARD_HOLD": 9}), dict(Counter(row["scope_orientation"] for row in ol)))
    check("state_operations_exact", Counter(row["state_operation"] for row in paired) == Counter({"START_FRESH_SIBLING": 41, "KEEP_ACTIVE_UNIT": 28}), dict(Counter(row["state_operation"] for row in paired)))
    check("state_operation_by_root", all((row["root"] == "OT") == (row["state_operation"] == "START_FRESH_SIBLING") for row in paired), "69/69")
    check("all_scope_phrases_nonempty", all(row["scope_formula_de"].strip() and row["directional_scope_phrase_de"].strip() for row in paired), "69/69")
    check("marked_literals_exact_one", all(row["marked_literal_working_reading_de"].count("⟦") == 1 and row["marked_literal_working_reading_de"].count("⟧") == 1 for row in paired), "69/69")
    check("root_meaning_changes_zero", all(row["root_meaning_change"] == "NO" for row in paired), "69/69")
    check("learned_name_changes_zero", all(row["learned_name_change"] == "NO" for row in paired), "69/69")
    check("claim_status_exact", all(row["claim_status"] == "PAIRED_ORDER_SCOPE_DEFAULT__ROOT_MEANINGS_UNCHANGED" for row in paired), "69/69")

    edge_map = {(row["edge"], row["surface_stem"]): row for row in edges}
    internal_map = {row["surface_stem"]: row for row in internals}
    prefix = edge_map[("PREFIX", "ot")]
    internal = internal_map["ot"]
    check("prefix_ot_support_66_of_66", (int(prefix["running_extension_type_count"]), int(prefix["running_matching_type_count"]), int(prefix["running_matching_event_count"]), len(prefix["running_matching_pages"].split("|"))) == (66, 66, 211, 24), {key: prefix[key] for key in ("running_extension_type_count", "running_matching_type_count", "running_matching_event_count", "running_matching_pages")})
    check("internal_ot_support_55_of_56", (int(internal["running_internal_extension_type_count"]), int(internal["running_matching_type_count"]), int(internal["running_matching_event_count"]), len(internal["running_matching_pages"].split("|"))) == (56, 55, 150, 19), {key: internal[key] for key in ("running_internal_extension_type_count", "running_matching_type_count", "running_matching_event_count", "running_matching_pages")})

    check("event_rows_60", len(events) == 60, len(events))
    check("event_ids_unique", len({row["paired_event_id"] for row in events}) == 60, len({row["paired_event_id"] for row in events}))
    check("event_occurrences_total_69", sum(int(row["order_occurrence_count"]) for row in events) == 69, sum(int(row["order_occurrence_count"]) for row in events))
    check("event_size_distribution", Counter(int(row["order_occurrence_count"]) for row in events) == Counter({1: 52, 2: 7, 3: 1}), dict(Counter(int(row["order_occurrence_count"]) for row in events)))
    root_sets = Counter(tuple(sorted(set(row["order_root_sequence"].split("|")))) for row in events)
    check("event_root_set_counts", root_sets == Counter({("OT",): 34, ("OL",): 19, ("OL", "OT"): 7}), {"|".join(key): value for key, value in root_sets.items()})
    check("event_source_exact", all(row["surface"] == event_map[row["source_event_id"]]["surface"] and row["working_recipe"] == event_map[row["source_event_id"]]["working_recipe"] for row in events), "60/60")
    check("event_readings_complete", all(row["paired_order_event_reading_de"].strip().endswith(".") and "Reihenfolge:" in row["paired_order_event_reading_de"] for row in events), "60/60")

    expected_joint_surfaces = {"otolam", "otol", "otolaiin", "otokol", "otoldy", "otold", "otolarol"}
    check("joint_rows_7", len(joint) == 7, len(joint))
    check("joint_surfaces_exact", {row["surface"] for row in joint} == expected_joint_surfaces, sorted(row["surface"] for row in joint))
    check("joint_ot_always_precedes_ol", all(row["ot_precedes_every_ol"] == "YES" for row in joint), "7/7")
    check("joint_root_sequences_6_1", Counter(row["order_root_sequence"] for row in joint) == Counter({"OT|OL": 6, "OT|OL|OL": 1}), dict(Counter(row["order_root_sequence"] for row in joint)))
    check("joint_operations_start_then_keep", all(row["state_operation_sequence"].split("|")[0] == "START_FRESH_SIBLING" and set(row["state_operation_sequence"].split("|")[1:]) == {"KEEP_ACTIVE_UNIT"} for row in joint), "7/7")
    check("joint_claim_status_exact", all(row["claim_status"] == "NEXT_UNIT_THEN_KEEP_ACTIVE__NO_COMPOUND_LEXEME_CLAIM" for row in joint), "7/7")

    check("rule_rows_5", len(rules) == 5, len(rules))
    expected_rule_keys = [("OT", "FORWARD_OPEN", 40), ("OT", "BRIDGE_LEFT_TO_RIGHT", 1), ("OL", "FORWARD_OPEN", 9), ("OL", "BRIDGE_LEFT_TO_RIGHT", 10), ("OL", "BACKWARD_HOLD", 9)]
    check("rule_keys_counts_exact", [(row["root"], row["scope_orientation"], int(row["occurrence_count"])) for row in rules] == expected_rule_keys, [(row["root"], row["scope_orientation"], row["occurrence_count"]) for row in rules])
    check("rule_root_meanings_exact", all(row["working_meaning_de"] == ("DANACH" if row["root"] == "OT" else "FORTSETZEN") for row in rules), "5/5")
    check("rule_operations_exact", all(row["state_operation"] == ("START_FRESH_SIBLING" if row["root"] == "OT" else "KEEP_ACTIVE_UNIT") for row in rules), "5/5")
    check("rule_no_new_meanings", all(row["new_root_meaning"] == "NO" for row in rules), "5/5")

    expected_pages = {
        "f17r": (1, 1, 1, 0, 0),
        "f71v": (8, 8, 6, 2, 0),
        "f72r": (28, 26, 17, 11, 1),
        "f77r": (9, 7, 6, 3, 2),
        "f88v": (7, 6, 6, 1, 1),
        "f89r": (16, 12, 5, 11, 3),
    }
    actual_pages = {row["physical_page"]: (int(row["order_occurrence_count"]), int(row["order_event_count"]), int(row["ot_occurrence_count"]), int(row["ol_occurrence_count"]), int(row["joint_ot_ol_event_count"])) for row in pages}
    check("page_rows_6", len(pages) == 6, len(pages))
    check("page_counts_exact", actual_pages == expected_pages, actual_pages)
    check("page_defaults_complete", all(row["all_order_slots_have_default"] == "YES" for row in pages), "6/6")
    check("no_new_pages", set(actual_pages) == {"f17r", "f71v", "f72r", "f77r", "f88v", "f89r"}, sorted(actual_pages))
    check("sealed_pages_absent", not any(page.startswith("f84") for page in actual_pages), sorted(actual_pages))

    check("result_status", result["status"] == "OT_STARTS_NEXT_UNIT__OL_KEEPS_CURRENT_UNIT__PAIRED_ORDER_GRAMMAR_COMPLETE", result["status"])
    check("result_core_counts", result["order_occurrence_count"] == 69 and result["order_event_count"] == 60 and result["ot_occurrence_count"] == 41 and result["ol_occurrence_count"] == 28 and result["paired_rule_count"] == 5, result)
    check("result_ot_counts", result["ot_scope_counts"] == {"FORWARD_OPEN": 40, "BRIDGE_LEFT_TO_RIGHT": 1} and result["ot_right_successor_count"] == 41 and result["ot_backward_hold_count"] == 0, {key: result[key] for key in ("ot_scope_counts", "ot_right_successor_count", "ot_backward_hold_count")})
    check("result_joint_counts", result["joint_ot_ol_event_count"] == 7 and result["joint_ot_precedes_ol_count"] == 7 and result["joint_root_sequence_counts"] == {"OT|OL": 6, "OT|OL|OL": 1}, {key: result[key] for key in ("joint_ot_ol_event_count", "joint_ot_precedes_ol_count", "joint_root_sequence_counts")})
    check("result_operations", result["state_operation_counts"] == {"START_FRESH_SIBLING": 41, "KEEP_ACTIVE_UNIT": 28}, result["state_operation_counts"])
    check("result_ot_support", result["running_ot_support"]["PREFIX_OT"]["matching_types"] == 66 and result["running_ot_support"]["INTERNAL_OT"]["matching_types"] == 55, result["running_ot_support"])
    check("result_no_changes", all(result[key] == 0 for key in ("component_meaning_change_count", "learned_name_change_count", "surface_change_count", "recipe_change_count", "selected_model_change_count", "new_page_count")), {key: result[key] for key in ("component_meaning_change_count", "learned_name_change_count", "surface_change_count", "recipe_change_count", "selected_model_change_count", "new_page_count")})

    readable = READABLE.read_text(encoding="utf-8")
    check("readable_has_all_pages", all(f"### {page}" in readable for page in expected_pages), sorted(expected_pages))
    check("readable_has_all_joint_surfaces", all(f"`{surface}`" in readable for surface in expected_joint_surfaces), sorted(expected_joint_surfaces))
    check("readable_has_all_ot_surfaces", all(f"`{row['surface']}`" in readable for row in ot), "41/41")

    passed = sum(bool(row["pass"]) for row in checks)
    validation = {
        "status": "PASS" if passed == len(checks) else "FAIL",
        "checks": len(checks),
        "passed": passed,
        "failed": len(checks) - passed,
        "details": checks,
    }
    VALIDATION.write_text(json.dumps(validation, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: validation[key] for key in ("status", "checks", "passed", "failed")}, sort_keys=True))
    return 0 if validation["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
