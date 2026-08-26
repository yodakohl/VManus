#!/usr/bin/env python3
"""Validate the GDT477 directional OL scope phrasebook."""

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
BASE = ROOT / "experiments/yolo/gdt477_ol_directional_scope_phrasebook"
OUT = BASE / "artifacts"
RUN = BASE / "src/run.py"
G460 = ROOT / "experiments/yolo/gdt460_learned_label_edge_stem_atlas/artifacts"
G474 = ROOT / "experiments/yolo/gdt474_locus_bundle_meaning_triptych/artifacts"
G475 = ROOT / "experiments/yolo/gdt475_ot_ol_page_microrecord_itineraries/artifacts"
G476 = ROOT / "experiments/yolo/gdt476_boundary_context_tie_resolution/artifacts"
EDGES_IN = G460 / "gdt460_27_calibrated_edge_stems.tsv"
EVENTS_IN = G474 / "gdt474_183_event_meaning_triptych.tsv"
OCCURRENCES_IN = G475 / "gdt475_69_order_occurrence_positions.tsv"
BOUNDARIES_IN = G475 / "gdt475_146_bundle_boundary_roles.tsv"
DECISIONS_IN = G476 / "gdt476_64_tie_context_decisions.tsv"
SCOPE = OUT / "gdt477_28_ol_directional_scope_occurrences.tsv"
EVENTS = OUT / "gdt477_26_ol_event_scope_editions.tsv"
RULES = OUT / "gdt477_3_directional_scope_rules.tsv"
PAGES = OUT / "gdt477_5_page_scope_summary.tsv"
READABLE = OUT / "GDT477_OL_DIRECTIONAL_SCOPE_PHRASEBOOK.md"
RESULT = OUT / "gdt477_result.json"
VALIDATION = OUT / "gdt477_validation.json"


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

    generated = [SCOPE, EVENTS, RULES, PAGES, READABLE, RESULT]
    check("all_outputs_present", all(path.is_file() for path in generated), [path.name for path in generated])
    if not all(path.is_file() for path in generated):
        raise RuntimeError("Run GDT477 builder before validation")
    before = {path.name: sha256(path) for path in generated}
    completed = subprocess.run([sys.executable, str(RUN)], cwd=ROOT, capture_output=True, text=True, check=False)
    after = {path.name: sha256(path) for path in generated}
    check("builder_exit_zero", completed.returncode == 0, completed.stderr[-1000:])
    check("deterministic_rebuild", before == after, {"before": before, "after": after})

    edges = read_tsv(EDGES_IN)
    source_events = read_tsv(EVENTS_IN)
    source_occurrences = read_tsv(OCCURRENCES_IN)
    boundaries = read_tsv(BOUNDARIES_IN)
    decisions = read_tsv(DECISIONS_IN)
    scope = read_tsv(SCOPE)
    events = read_tsv(EVENTS)
    rules = read_tsv(RULES)
    pages = read_tsv(PAGES)
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    event_map = {row["source_event_id"]: row for row in source_events}
    boundary_map = {row["bundle_id"]: row for row in boundaries}
    decision_map = {row["bundle_id"]: row for row in decisions}
    ol_source = [row for row in source_occurrences if row["root"] == "OL"]

    check("input_edges_27", len(edges) == 27, len(edges))
    check("input_events_183", len(source_events) == 183, len(source_events))
    check("input_order_occurrences_69", len(source_occurrences) == 69, len(source_occurrences))
    check("input_ol_occurrences_28", len(ol_source) == 28, len(ol_source))
    check("input_boundaries_146", len(boundaries) == 146, len(boundaries))
    check("input_decisions_64", len(decisions) == 64, len(decisions))
    check("scope_rows_28", len(scope) == 28, len(scope))
    check("scope_ids_unique", len({row["scope_id"] for row in scope}) == 28, len({row["scope_id"] for row in scope}))
    check("source_occurrence_order_exact", [row["order_occurrence_id"] for row in scope] == [row["order_occurrence_id"] for row in ol_source], "28/28")
    check("source_event_ids_exact", [row["source_event_id"] for row in scope] == [row["source_event_id"] for row in ol_source], "28/28")
    for field in ("bundle_id", "record_id", "physical_page", "locus", "surface", "working_recipe"):
        check(f"source_{field}_exact", all(row[field] == source[field] for row, source in zip(scope, ol_source, strict=True)), "28/28")
    check("literal_readings_exact", all(row["literal_working_reading_de"] == event_map[row["source_event_id"]]["literal_working_reading_de"] for row in scope), "28/28")
    check("boundary_roles_exact", all(row["boundary_role"] == boundary_map[row["bundle_id"]]["boundary_role"] for row in scope), "28/28")
    check("gdt475_positions_exact", all(row["gdt475_position_role"] == source["position_role"] for row, source in zip(scope, ol_source, strict=True)), "28/28")
    check("gdt475_interpretations_exact", all(row["gdt475_stream_interpretation"] == source["stream_interpretation"] for row, source in zip(scope, ol_source, strict=True)), "28/28")

    orientations = Counter(row["scope_orientation"] for row in scope)
    names = Counter(row["name_relative_position"] for row in scope)
    positions = Counter((row["scope_orientation"], row["gdt475_position_role"]) for row in scope)
    check("orientation_counts_9_10_9", orientations == Counter({"BRIDGE_LEFT_TO_RIGHT": 10, "FORWARD_OPEN": 9, "BACKWARD_HOLD": 9}), dict(orientations))
    check("name_position_counts_13_10_5", names == Counter({"NAME_FREE": 13, "PRE_NAME": 10, "POST_NAME": 5}), dict(names))
    check("no_between_name_ol", names["BETWEEN_NAMES"] == 0, dict(names))
    check("forward_is_literal_first", all(int(row["ol_literal_token_ordinal"]) == 1 for row in scope if row["scope_orientation"] == "FORWARD_OPEN"), "9/9")
    check("backward_is_literal_last", all(int(row["ol_literal_token_ordinal"]) == int(row["literal_token_count"]) for row in scope if row["scope_orientation"] == "BACKWARD_HOLD"), "9/9")
    check("bridge_is_literal_medial", all(1 < int(row["ol_literal_token_ordinal"]) < int(row["literal_token_count"]) for row in scope if row["scope_orientation"] == "BRIDGE_LEFT_TO_RIGHT"), "10/10")
    check("forward_left_boundary", all(row["left_token"] == "NONE" and row["left_token_type"] == "BOUNDARY" for row in scope if row["scope_orientation"] == "FORWARD_OPEN"), "9/9")
    check("backward_right_boundary", all(row["right_token"] == "NONE" and row["right_token_type"] == "BOUNDARY" for row in scope if row["scope_orientation"] == "BACKWARD_HOLD"), "9/9")
    check("bridge_has_two_carriers", all(row["left_token"] != "NONE" and row["right_token"] != "NONE" for row in scope if row["scope_orientation"] == "BRIDGE_LEFT_TO_RIGHT"), "10/10")
    check("pre_name_never_backward", not any(row["name_relative_position"] == "PRE_NAME" and row["scope_orientation"] == "BACKWARD_HOLD" for row in scope), "0")
    check("post_name_never_forward", not any(row["name_relative_position"] == "POST_NAME" and row["scope_orientation"] == "FORWARD_OPEN" for row in scope), "0")
    expected_positions = Counter({
        ("FORWARD_OPEN", "BUNDLE_LEADING"): 8,
        ("FORWARD_OPEN", "LATER_EVENT_LEADING"): 1,
        ("BRIDGE_LEFT_TO_RIGHT", "BUNDLE_LEADING"): 2,
        ("BRIDGE_LEFT_TO_RIGHT", "EVENT_INTERNAL"): 8,
        ("BACKWARD_HOLD", "BUNDLE_LEADING"): 1,
        ("BACKWARD_HOLD", "EVENT_INTERNAL"): 8,
    })
    check("orientation_position_cross_exact", positions == expected_positions, {"|".join(key): value for key, value in positions.items()})
    check("forward_opens_events_9_of_9", all(row["gdt475_position_role"] != "EVENT_INTERNAL" for row in scope if row["scope_orientation"] == "FORWARD_OPEN"), "9/9")
    check("internal_is_bridge_or_backward_16_of_16", all(row["scope_orientation"] in {"BRIDGE_LEFT_TO_RIGHT", "BACKWARD_HOLD"} for row in scope if row["gdt475_position_role"] == "EVENT_INTERNAL") and sum(row["gdt475_position_role"] == "EVENT_INTERNAL" for row in scope) == 16, "16/16")
    check("bundle_leading_orientations_8_2_1", Counter(row["scope_orientation"] for row in scope if row["gdt475_position_role"] == "BUNDLE_LEADING") == Counter({"FORWARD_OPEN": 8, "BRIDGE_LEFT_TO_RIGHT": 2, "BACKWARD_HOLD": 1}), dict(Counter(row["scope_orientation"] for row in scope if row["gdt475_position_role"] == "BUNDLE_LEADING")))

    check("all_scope_formulas_nonempty", all(row["scope_formula_de"].strip() and row["directional_scope_phrase_de"].strip() for row in scope), "28/28")
    check("marked_literal_has_one_selected_slot", all(row["marked_literal_working_reading_de"].count("⟦FORTSETZEN⟧") == 1 for row in scope), "28/28")
    check("all_marked_literals_preserve_other_tokens", all(row["marked_literal_working_reading_de"].replace("⟦FORTSETZEN⟧", "FORTSETZEN") == row["literal_working_reading_de"] for row in scope), "28/28")
    check("context_models_valid", all(row["context_selected_model"] in {"COORDINATE", "INSTRUCTION", "CATALOGUE"} for row in scope), "28/28")
    check("context_model_occurrence_counts", Counter(row["context_selected_model"] for row in scope) == Counter({"INSTRUCTION": 15, "COORDINATE": 7, "CATALOGUE": 6}), dict(Counter(row["context_selected_model"] for row in scope)))
    check("context_readings_match_models", all(row["context_selected_event_reading_de"] == event_map[row["source_event_id"]][f"{row['context_selected_model'].lower()}_event_reading_de"] for row in scope), "28/28")
    check("gdt476_models_applied_when_present", all(row["context_selected_model"] == decision_map[row["bundle_id"]]["context_selected_model"] for row in scope if row["bundle_id"] in decision_map), "tied bundles")
    check("root_meaning_changes_zero", all(row["root_meaning_change"] == "NO" for row in scope), "28/28")
    check("learned_name_changes_zero", all(row["learned_name_change"] == "NO" for row in scope), "28/28")
    check("scope_claim_status_exact", all(row["claim_status"] == "POSITIONAL_SCOPE_RECAST__OL_MEANING_UNCHANGED" for row in scope), "28/28")

    check("event_rows_26", len(events) == 26, len(events))
    check("event_ids_unique", len({row["scope_event_id"] for row in events}) == 26, len({row["scope_event_id"] for row in events}))
    check("event_occurrence_total_28", sum(int(row["ol_occurrence_count"]) for row in events) == 28, sum(int(row["ol_occurrence_count"]) for row in events))
    check("two_double_ol_events", Counter(int(row["ol_occurrence_count"]) for row in events) == Counter({1: 24, 2: 2}), dict(Counter(int(row["ol_occurrence_count"]) for row in events)))
    check("double_ol_surfaces_exact", {row["surface"] for row in events if int(row["ol_occurrence_count"]) == 2} == {"ykolairol", "otolarol"}, sorted(row["surface"] for row in events if int(row["ol_occurrence_count"]) == 2))
    check("event_model_counts", Counter(row["context_selected_model"] for row in events) == Counter({"INSTRUCTION": 14, "COORDINATE": 6, "CATALOGUE": 6}), dict(Counter(row["context_selected_model"] for row in events)))
    check("event_refined_readings_complete", all(row["direction_refined_event_reading_de"].strip().endswith(".") and "OL-Scope:" in row["direction_refined_event_reading_de"] for row in events), "26/26")
    check("event_source_fields_exact", all(row["surface"] == event_map[row["source_event_id"]]["surface"] and row["working_recipe"] == event_map[row["source_event_id"]]["working_recipe"] for row in events), "26/26")

    edge_map = {(row["edge"], row["surface_stem"]): row for row in edges}
    prefix = edge_map[("PREFIX", "ol")]
    suffix = edge_map[("SUFFIX", "ol")]
    check("prefix_ol_support_exact", (int(prefix["running_extension_type_count"]), int(prefix["running_matching_type_count"]), int(prefix["running_matching_event_count"]), len(prefix["running_matching_pages"].split("|"))) == (56, 54, 138, 20), {key: prefix[key] for key in ("running_extension_type_count", "running_matching_type_count", "running_matching_event_count", "running_matching_pages")})
    check("suffix_ol_support_exact", (int(suffix["running_extension_type_count"]), int(suffix["running_matching_type_count"]), int(suffix["running_matching_event_count"]), len(suffix["running_matching_pages"].split("|"))) == (111, 102, 338, 24), {key: suffix[key] for key in ("running_extension_type_count", "running_matching_type_count", "running_matching_event_count", "running_matching_pages")})
    check("rule_rows_3", len(rules) == 3, len(rules))
    check("rule_orientation_order", [row["scope_orientation"] for row in rules] == ["FORWARD_OPEN", "BRIDGE_LEFT_TO_RIGHT", "BACKWARD_HOLD"], [row["scope_orientation"] for row in rules])
    check("rule_counts_exact", [int(row["occurrence_count"]) for row in rules] == [9, 10, 9] and [int(row["event_count"]) for row in rules] == [9, 10, 9], [(row["occurrence_count"], row["event_count"]) for row in rules])
    check("one_root_meaning_all_rules", all(row["working_root_meaning_de"] == "FORTSETZEN" and row["new_root_meaning"] == "NO" for row in rules), "3/3")

    expected_pages = {
        "f71v": (2, 2, 0, 2, 0, 0),
        "f72r": (11, 10, 6, 3, 2, 6),
        "f77r": (3, 3, 1, 1, 1, 1),
        "f88v": (1, 1, 0, 0, 1, 0),
        "f89r": (11, 10, 2, 4, 5, 4),
    }
    actual_pages = {row["physical_page"]: (int(row["occurrence_count"]), int(row["event_count"]), int(row["forward_open_count"]), int(row["bridge_count"]), int(row["backward_hold_count"]), int(row["cross_locus_record_binding_count"])) for row in pages}
    check("page_rows_5", len(pages) == 5, len(pages))
    check("page_counts_exact", actual_pages == expected_pages, actual_pages)
    check("page_defaults_complete", all(row["all_occurrences_have_directional_default"] == "YES" for row in pages), "5/5")
    check("no_new_pages", set(actual_pages) == {"f71v", "f72r", "f77r", "f88v", "f89r"}, sorted(actual_pages))
    check("sealed_pages_absent", not any(page.startswith("f84") for page in actual_pages), sorted(actual_pages))

    check("result_status", result["status"] == "OL_HAS_THREE_POSITIONAL_SCOPE_REALIZATIONS__ONE_ROOT_MEANING", result["status"])
    check("result_counts_exact", result["ol_occurrence_count"] == 28 and result["ol_event_count"] == 26 and result["scope_orientation_counts"] == dict(orientations) and result["name_relative_position_counts"] == dict(names), result)
    check("result_forward_open_exact", result["forward_open_event_opening_count"] == 9 and result["forward_open_event_internal_count"] == 0, {key: result[key] for key in ("forward_open_event_opening_count", "forward_open_event_internal_count")})
    check("result_internal_split_8_8", result["event_internal_bridge_count"] == 8 and result["event_internal_backward_count"] == 8, {key: result[key] for key in ("event_internal_bridge_count", "event_internal_backward_count")})
    check("result_cross_locus_8_2_1", result["cross_locus_orientation_counts"] == {"FORWARD_OPEN": 8, "BRIDGE_LEFT_TO_RIGHT": 2, "BACKWARD_HOLD": 1}, result["cross_locus_orientation_counts"])
    check("result_running_edges_exact", result["running_edge_support"]["PREFIX_OL"]["matching_types"] == 54 and result["running_edge_support"]["SUFFIX_OL"]["matching_types"] == 102, result["running_edge_support"])
    check("result_no_changes", all(result[key] == 0 for key in ("component_meaning_change_count", "learned_name_change_count", "surface_change_count", "recipe_change_count", "selected_model_change_count", "new_page_count")), {key: result[key] for key in ("component_meaning_change_count", "learned_name_change_count", "surface_change_count", "recipe_change_count", "selected_model_change_count", "new_page_count")})

    readable = READABLE.read_text(encoding="utf-8")
    check("readable_has_all_pages", all(f"### {page}" in readable for page in expected_pages), sorted(expected_pages))
    check("readable_has_all_occurrence_surfaces", all(f"`{row['surface']}`" in readable for row in scope), "28/28")
    check("readable_has_all_three_rules", all(row["scope_orientation"] in readable for row in rules), "3/3")

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
