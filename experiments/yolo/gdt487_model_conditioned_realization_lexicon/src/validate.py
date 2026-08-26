#!/usr/bin/env python3
"""Validate GDT487's model-conditioned realization lexicon and routing graph."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt487_model_conditioned_realization_lexicon"
OUT = BASE / "artifacts"
G486 = ROOT / "experiments/yolo/gdt486_fluent_frame_component_contrast_deck/artifacts"
G428 = ROOT / "experiments/yolo/gdt428_within_class_action_semantic_contrasts/artifacts"
G429 = ROOT / "experiments/yolo/gdt429_nonaction_core_semantic_contrasts/artifacts"
RUN = BASE / "src/run.py"
PAIRS_IN = G486 / "gdt486_48_register_minimal_pairs.tsv"
RULES_IN = G486 / "gdt486_29_model_conditioned_contrast_rules.tsv"
ASSIGNMENTS_IN = G486 / "gdt486_135_fluent_frame_assignments.tsv"
ACTION_CONTRASTS_IN = G428 / "gdt428_6_within_class_contrasts.tsv"
NONACTION_CONTRASTS_IN = G429 / "gdt429_13_nonaction_core_contrasts.tsv"
LEXICON = OUT / "gdt487_13_component_realization_lexicon.tsv"
MODEL_CELLS = OUT / "gdt487_39_component_model_cells.tsv"
REALIZATION_FORMS = OUT / "gdt487_29_observed_realization_forms.tsv"
SINGLETON_TRIANGULATION = OUT / "gdt487_16_singleton_triangulations.tsv"
EXTERNAL_ANCHORS = OUT / "gdt487_3_external_contrast_anchors.tsv"
LOCAL_EDGES = OUT / "gdt487_13_local_recurrent_edges.tsv"
PAGE_SUPPORT = OUT / "gdt487_6_page_realization_support.tsv"
READABLE = OUT / "GDT487_MODEL_CONDITIONED_REALIZATION_LEXICON.md"
RESULT = OUT / "gdt487_result.json"
VALIDATION = OUT / "gdt487_validation.json"
STATUS = "THIRTEEN_VALUE_REALIZATION_LEXICON__FOURTEEN_SINGLETON_CYCLES__TWO_ENDPOINT_ANCHORS"
EXPECTED_VALUES = {
    "ANTEIL", "AUSGANG", "BAHN", "DANACH", "EINHEIT", "EINSTELLEN",
    "FORTSETZEN", "HALTEN", "HIER", "POSTEN", "SCHLUSS", "WERT", "ZIELORT",
}
EXPECTED_EXTERNAL = {
    "DANACH": ("GDT429", "OL~OT", "FORTSETZEN", 14, "DIRECT_TO_LOCAL_RECURRENT_GRAPH"),
    "EINSTELLEN": ("GDT428", "T~R", "MARKIEREN", 11, "EXTERNAL_ACTION_ENDPOINT_ANCHOR"),
    "HALTEN": ("GDT428", "SH~CHD", "BEARBEITEN", 14, "EXTERNAL_ACTION_ENDPOINT_ANCHOR"),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object = None) -> None:
        checks.append({"name": name, "pass": bool(condition), "detail": detail})

    generated = [LEXICON, MODEL_CELLS, REALIZATION_FORMS, SINGLETON_TRIANGULATION, EXTERNAL_ANCHORS, LOCAL_EDGES, PAGE_SUPPORT, READABLE, RESULT]
    present = all(path.is_file() for path in generated)
    check("all_outputs_present", present, [path.name for path in generated])
    if not present:
        raise RuntimeError("Run GDT487 builder first")
    before = {path.name: sha256(path) for path in generated}
    completed = subprocess.run([sys.executable, str(RUN)], cwd=ROOT, capture_output=True, text=True, check=False)
    after = {path.name: sha256(path) for path in generated}
    check("builder_exit_zero", completed.returncode == 0, completed.stderr[-1000:])
    check("deterministic_rebuild", before == after, {"before": before, "after": after})

    pairs = read_tsv(PAIRS_IN)
    rules = read_tsv(RULES_IN)
    assignments = read_tsv(ASSIGNMENTS_IN)
    action_contrasts = read_tsv(ACTION_CONTRASTS_IN)
    nonaction_contrasts = read_tsv(NONACTION_CONTRASTS_IN)
    lexicon = read_tsv(LEXICON)
    cells = read_tsv(MODEL_CELLS)
    forms = read_tsv(REALIZATION_FORMS)
    triangulations = read_tsv(SINGLETON_TRIANGULATION)
    anchors = read_tsv(EXTERNAL_ANCHORS)
    local_edges = read_tsv(LOCAL_EDGES)
    pages = read_tsv(PAGE_SUPPORT)
    readable = READABLE.read_text(encoding="utf-8")
    result = json.loads(RESULT.read_text(encoding="utf-8"))

    check("source_pair_count_48", len(pairs) == 48, len(pairs))
    check("source_rule_count_29", len(rules) == 29, len(rules))
    check("source_assignment_count_135", len(assignments) == 135, len(assignments))
    check("source_action_contrast_count_6", len(action_contrasts) == 6, len(action_contrasts))
    check("source_nonaction_contrast_count_13", len(nonaction_contrasts) == 13, len(nonaction_contrasts))
    check("lexicon_count_13", len(lexicon) == 13, len(lexicon))
    check("model_cell_count_39", len(cells) == 39, len(cells))
    check("realization_form_count_29", len(forms) == 29, len(forms))
    check("triangulation_count_16", len(triangulations) == 16, len(triangulations))
    check("external_anchor_count_3", len(anchors) == 3, len(anchors))
    check("local_edge_count_13", len(local_edges) == 13, len(local_edges))
    check("page_count_6", len(pages) == 6, len(pages))

    lexicon_map = {row["component_value"]: row for row in lexicon}
    rule_map = {row["rule_id"]: row for row in rules}
    pair_map = {row["pair_id"]: row for row in pairs}
    assignment_map = {row["record_id"]: row for row in assignments}
    check("lexicon_values_exact", set(lexicon_map) == EXPECTED_VALUES)
    check("lexicon_values_unique", len(lexicon_map) == len(lexicon))
    check("lexicon_ids_unique", len({row["lexicon_id"] for row in lexicon}) == 13)
    check("cell_ids_unique", len({row["cell_id"] for row in cells}) == 39)
    check("form_ids_unique", len({row["form_id"] for row in forms}) == 29)
    check("triangulation_ids_unique", len({row["triangulation_id"] for row in triangulations}) == 16)
    check("anchor_ids_unique", len({row["anchor_id"] for row in anchors}) == 3)
    check("edge_ids_unique", len({row["edge_id"] for row in local_edges}) == 13)

    expected_cells = {(component, model) for component in EXPECTED_VALUES for model in ("CATALOGUE", "COORDINATE", "INSTRUCTION")}
    check("component_model_grid_exact", {(row["component_value"], row["active_model"]) for row in cells} == expected_cells)
    check("cell_status_profile_exact", Counter(row["cell_status"] for row in cells) == Counter({"OBSERVED": 25, "OPEN": 14}))
    check("observed_cells_have_forms", all((row["cell_status"] == "OBSERVED") == (int(row["realization_form_count"]) > 0) for row in cells))
    check("open_cells_have_open_marker", all(row["cell_status"] != "OPEN" or (row["realization_forms_de"] == "OPEN" and row["witness_records"] == "NONE" and int(row["invented_form_count"]) == 0) for row in cells))
    check("all_cells_zero_invented", all(int(row["invented_form_count"]) == 0 for row in cells))
    check("cell_form_total_29", sum(int(row["realization_form_count"]) for row in cells) == 29)
    check("cell_witness_total_56", sum(int(row["witness_record_count"]) for row in cells) == 56)

    check("form_values_known", {row["component_value"] for row in forms} <= EXPECTED_VALUES)
    check("form_models_exact", {row["active_model"] for row in forms} == {"CATALOGUE", "COORDINATE", "INSTRUCTION"})
    check("form_keys_unique", len({(row["component_value"], row["active_model"], row["canonical_realization_de"]) for row in forms}) == 29)
    check("form_witness_total_56", sum(int(row["witness_record_count"]) for row in forms) == 56)
    check("form_witness_records_valid", all(set(row["witness_records"].split("|")) <= set(assignment_map) for row in forms))
    check("form_pages_valid", all(set(row["pages"].split("|")) <= {assignment_map[record_id]["physical_page"] for record_id in row["witness_records"].split("|")} for row in forms))
    check("form_flags_all_yes", all(row["all_forms_observed_not_invented"] == "YES" for row in forms))
    check("form_examples_present", all(row["canonical_realization_de"] and row["example_reading_de"] and row["matched_surface_forms_de"] for row in forms))

    forms_by_component: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in forms:
        forms_by_component[row["component_value"]].append(row)
    check("lexicon_form_counts_exact", all(int(row["realization_form_count"]) == len(forms_by_component[row["component_value"]]) for row in lexicon))
    check("lexicon_observed_model_counts_exact", all(int(row["observed_model_count"]) == len({form["active_model"] for form in forms_by_component[row["component_value"]]}) for row in lexicon))
    check("lexicon_open_model_partition", all(set(row["observed_models"].split("|")) | (set() if row["open_models"] == "NONE" else set(row["open_models"].split("|"))) == {"CATALOGUE", "COORDINATE", "INSTRUCTION"} for row in lexicon))
    check("lexicon_form_strings_exact", all(
        row["catalogue_forms_de"] == ("|".join(form["canonical_realization_de"] for form in forms_by_component[row["component_value"]] if form["active_model"] == "CATALOGUE") or "OPEN")
        and row["coordinate_forms_de"] == ("|".join(form["canonical_realization_de"] for form in forms_by_component[row["component_value"]] if form["active_model"] == "COORDINATE") or "OPEN")
        and row["instruction_forms_de"] == ("|".join(form["canonical_realization_de"] for form in forms_by_component[row["component_value"]] if form["active_model"] == "INSTRUCTION") or "OPEN")
        for row in lexicon
    ))
    check("lexicon_witness_record_union_47", len({record_id for row in lexicon for record_id in row["witness_records"].split("|")}) == 47)
    check("lexicon_flags_all_yes", all(row["all_forms_observed_not_invented"] == "YES" for row in lexicon))
    check("lexicon_all_values_anchored", all(row["anchor_class"] != "UNANCHORED" for row in lexicon))

    recurrent_rules = [row for row in rules if int(row["pair_count"]) > 1]
    check("source_recurrent_rule_count_13", len(recurrent_rules) == 13)
    check("local_edges_source_rules_exact", {row["source_rule_id"] for row in local_edges} == {row["rule_id"] for row in recurrent_rules})
    check("local_edge_components_exact", all({row["component_a"], row["component_b"]} == {rule_map[row["source_rule_id"]]["component_a"], rule_map[row["source_rule_id"]]["component_b"]} for row in local_edges))
    check("local_edge_counts_exact", all(row["pair_count"] == rule_map[row["source_rule_id"]]["pair_count"] and row["phrase_signature_count"] == rule_map[row["source_rule_id"]]["phrase_signature_count"] for row in local_edges))
    check("local_edge_flags_yes", all(row["recurrent_local_edge"] == "YES" for row in local_edges))
    local_nodes = {row[field] for row in local_edges for field in ("component_a", "component_b")}
    check("local_recurrent_node_count_10", len(local_nodes) == 10, sorted(local_nodes))
    check("external_only_values_exact", EXPECTED_VALUES - local_nodes == {"DANACH", "EINSTELLEN", "HALTEN"})
    check("lexicon_local_degrees_exact", all(int(row["local_recurrent_degree"]) == sum(row["component_value"] in {edge["component_a"], edge["component_b"]} for edge in local_edges) for row in lexicon))

    anchor_map = {row["component_value"]: row for row in anchors}
    check("anchor_values_exact", set(anchor_map) == set(EXPECTED_EXTERNAL))
    check("anchor_fields_exact", all(
        (row["source_experiment"], row["source_contrast_pair"], row["anchor_value"], int(row["shared_exact_substitution_frame_count"]), row["bridge_class"]) == EXPECTED_EXTERNAL[row["component_value"]]
        for row in anchors
    ))
    check("anchor_decisions_retained", all(row["decision"] == "DISTINCT_MEANINGS_RETAINED" and row["meaning_change"] == "NO" for row in anchors))
    source_contrast_map = {(row["contrast_pair"]): row for row in action_contrasts + nonaction_contrasts}
    check("anchor_source_counts_exact", all(row["shared_exact_substitution_frame_count"] == source_contrast_map[row["source_contrast_pair"]]["shared_exact_substitution_frame_count"] and row["shared_frame_event_count"] == source_contrast_map[row["source_contrast_pair"]]["shared_frame_event_count"] for row in anchors))
    check("anchor_workshop_text_exact", all(row["workshop_interpretation_de"] == source_contrast_map[row["source_contrast_pair"]]["workshop_interpretation_de"] for row in anchors))
    check("lexicon_external_anchor_classes_exact", all(lexicon_map[component]["anchor_class"] == expected[4] for component, expected in EXPECTED_EXTERNAL.items()))

    singleton_rules = [row for row in rules if int(row["pair_count"]) == 1]
    check("source_singleton_rule_count_16", len(singleton_rules) == 16)
    check("triangulation_rule_ids_exact", {row["rule_id"] for row in triangulations} == {row["rule_id"] for row in singleton_rules})
    check("triangulation_pair_links_exact", all(row["pair_id"] == rule_map[row["rule_id"]]["pair_ids"] and row["pair_id"] in pair_map for row in triangulations))
    check("triangulation_component_links_exact", all((row["component_a"], row["component_b"]) == (rule_map[row["rule_id"]]["component_a"], rule_map[row["rule_id"]]["component_b"]) for row in triangulations))
    check("triangulation_profile_exact", Counter(row["triangulation_class"] for row in triangulations) == Counter({"LOCAL_RECURRENT_CYCLE": 13, "EXTERNAL_TO_LOCAL_CYCLE": 1, "EXTERNAL_ENDPOINT_ANCHOR_ONLY": 2}))
    check("triangulation_full_path_count_14", sum(row["alternate_path_complete"] == "YES" for row in triangulations) == 14)
    check("triangulation_all_endpoints_anchored", all(row["both_endpoints_anchored"] == "YES" for row in triangulations))
    check("triangulation_zero_remap", all(row["dictionary_remap_required"] == "NO" for row in triangulations))
    check("external_cycle_exact_rule", {row["rule_id"] for row in triangulations if row["triangulation_class"] == "EXTERNAL_TO_LOCAL_CYCLE"} == {"G486-CR06"})
    check("endpoint_anchor_rules_exact", {row["rule_id"] for row in triangulations if row["triangulation_class"] == "EXTERNAL_ENDPOINT_ANCHOR_ONLY"} == {"G486-CR17", "G486-CR24"})
    check("local_cycle_uses_gdt486", all(row["external_anchor_experiment"] == "GDT486" for row in triangulations if row["triangulation_class"] == "LOCAL_RECURRENT_CYCLE"))
    check("external_routes_use_expected_sources", {(row["rule_id"], row["external_anchor_experiment"]) for row in triangulations if row["triangulation_class"] != "LOCAL_RECURRENT_CYCLE"} == {("G486-CR06", "GDT429"), ("G486-CR17", "GDT428"), ("G486-CR24", "GDT428")})
    check("triangulation_paths_nonempty", all(row["triangulation_path_de"] != "NONE" and int(row["path_edge_count"]) >= 1 for row in triangulations))

    check("page_set_exact", {row["physical_page"] for row in pages} == {row["physical_page"] for row in assignments})
    check("page_record_total_135", sum(int(row["record_count"]) for row in pages) == 135)
    check("page_witness_total_56", sum(int(row["realization_witness_count"]) for row in pages) == 56)
    check("page_support_count_4", sum(row["has_realization_support"] == "YES" for row in pages) == 4)
    check("page_zero_support_exact", {row["physical_page"] for row in pages if row["has_realization_support"] == "NO"} == {"f17r", "f77r"})

    check("readable_contains_all_values", all(f"`{value}`" in readable for value in EXPECTED_VALUES))
    check("readable_contains_all_singleton_rules", all(row["rule_id"] in readable for row in triangulations))
    check("readable_contains_all_anchor_pairs", all(row["source_contrast_pair"] in readable for row in anchors))
    check("readable_reports_core_counts", "**25 beobachtet / 14 offen**" in readable and "**29** aus **56**" in readable)
    check("readable_reports_zero_unanchored", "völlig unverankert: **0**" in readable)
    check("readable_escapes_multi_forms", "Anteils- (Koordination)<br>Anteilsangabe" in readable and "Mengenwert<br>Positionswert" in readable)

    check("result_status_exact", result.get("status") == STATUS, result.get("status"))
    check("result_lexicon_counts_exact", (result.get("component_value_count"), result.get("component_model_cell_count"), result.get("observed_model_cell_count"), result.get("open_model_cell_count"), result.get("realization_form_count")) == (13, 39, 25, 14, 29))
    check("result_witness_counts_exact", (result.get("realization_witness_count"), result.get("witness_record_count")) == (56, 47))
    check("result_network_counts_exact", (result.get("local_recurrent_edge_count"), result.get("local_recurrent_node_count"), result.get("external_anchor_count")) == (13, 10, 3))
    check("result_triangulation_counts_exact", (result.get("singleton_rule_count"), result.get("local_cycle_triangulated_count"), result.get("external_cycle_triangulated_count"), result.get("full_cycle_triangulated_count"), result.get("endpoint_anchored_only_count"), result.get("unanchored_singleton_count")) == (16, 13, 1, 14, 2, 0))
    check("result_anchor_flags_true", result.get("all_component_values_anchored") is True and result.get("all_realization_forms_observed") is True)
    check("result_page_counts_exact", result.get("page_count") == 6 and result.get("support_page_count") == 4 and set(result.get("zero_support_pages", [])) == {"f17r", "f77r"})
    unchanged = ("meaning_change_count", "active_model_change_count", "record_boundary_change_count", "surface_change_count", "recipe_change_count", "page_change_count")
    check("result_no_source_changes", all(result.get(key) == 0 for key in unchanged), {key: result.get(key) for key in unchanged})
    check("claim_ceiling_bounded", "no independent semantic confirmation" in result.get("claim_ceiling", "") and "invented form" in result.get("claim_ceiling", ""))

    failed = [row for row in checks if not row["pass"]]
    payload = {
        "status": "PASS" if not failed else "FAIL",
        "checks_passed": len(checks) - len(failed),
        "checks_total": len(checks),
        "failed_checks": [row["name"] for row in failed],
        "checks": checks,
    }
    VALIDATION.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ("status", "checks_passed", "checks_total", "failed_checks")}, indent=2, ensure_ascii=False))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
