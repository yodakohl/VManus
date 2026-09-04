#!/usr/bin/env python3
"""Validate GDT804's counts, claim limits, gates and deterministic replay."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import subprocess
import tempfile
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt804_bracket_middle_independent_field_bridge"
SRC = EXP / "src"
ART = EXP / "artifacts"
RESULT = ART / "RESULT.json"
VALIDATION = ART / "VALIDATION.json"

FILES = {
    "lock": "SOURCE_LOCK.tsv",
    "fields": "GDT804_72_COMMON_MASK_FIELD_ATLAS.tsv",
    "exposures": "GDT804_107_COMMON_MASK_XL_EXPOSURES.tsv",
    "amount": "GDT804_POSITIONAL_AMOUNT_XL_SLOTS.tsv",
    "union": "GDT804_30_TARGET_UNION_CELLS.tsv",
    "census": "GDT804_11_MIDDLE_CENSUS.tsv",
    "pools": "GDT804_NEAREST_CONTROL_POOLS.tsv",
    "null_draws": "GDT804_5000_AGGREGATE_MATCHED_NULL.tsv",
    "null_summary": "GDT804_NULL_SUMMARY.tsv",
    "query_stats": "GDT804_GUARDED_READER_QUERY_STATS.tsv",
    "quality": "GDT804_41_QUALITY_VALUE_SPANS.tsv",
    "quality_summary": "GDT804_QUALITY_VALUE_SUMMARY.tsv",
    "right_profiles": "GDT804_11_MIDDLE_RIGHT_VALUE_PROFILE.tsv",
    "cheol_controls": "GDT804_CHEOL_K12_RIGHT_VALUE_CONTROL.tsv",
    "packet": "GDT804_GDT388_QUALITY_VALUE_EDGE_PACKET.tsv",
    "reader": "GDT804_12_BRACKET_WORKING_READER.tsv",
    "adjudication": "GDT804_MIDDLE_ROLE_ADJUDICATION.tsv",
    "card": "GDT804_STRUCTURAL_CARD.tsv",
}

SCHEMAS = {
    "lock": "path sha256 purpose",
    "fields": "gdt744_field_id page locus target_ordinal target_surface field_channel_after_common_mask field_confidence_tier boundary_complete foreign_anchor_count foreign_anchor_surfaces foreign_anchor_tags foreign_anchor_signature common_mask literal_identity_credit component_export_credit",
    "exposures": "field_exposure_id surface is_gdt803_middle page locus token_ordinal side distance host_target_surface host_gdt744_field_id field_channel_after_common_mask independently_licensed_field field_confidence_tier foreign_anchor_surfaces foreign_anchor_tags cell_key semantic_role_credit literal_identity_credit component_export_credit",
    "amount": "amount_slot_id expression_id surface is_gdt803_middle page physical_folio locus token_ordinal expression_line_position selected_side amount_expression_eva amount_candidate_de slot_axis_class slot_axes_before_gdt804 source_content_attachment_sides source_clean_content_attachment_count selected_side_is_clean_content_contact open_positional_candidate candidate_status discovery_cell_excluded cell_key role_scope literal_identity_credit component_export_credit",
    "union": "cell_key surface page locus token_ordinal common_mask_field_hit positioned_amount_neighbour_hit open_positioned_amount_neighbour_hit gdt760_clean_content_contact field_channels amount_expressions union_cell_id selected_role_credit literal_identity_credit component_export_credit",
    "census": "surface stem gdt800_l_occurrences gdt800_l_pages gdt803_bracket_occurrences outside_bracket_occurrences outside_bracket_pages common_mask_field_exposures common_mask_licensed_hits common_mask_hit_pages common_mask_channel_counts positioned_amount_neighbour_hits positioned_open_amount_neighbour_hits gdt760_clean_content_contact_hits quality_value_right_spans cross_map_role preferred_role_class conservative_working_default_de aggressive_working_default_de confidence leading_channel concrete_noun_priority positive_evidence_code counterevidence_code literal_identity confirmed_lexeme component_export_credit",
    "pools": "pool_variant target_surface neighbor_rank control_surface individual_covariate_distance outcome_fields_used_for_matching",
    "null_draws": "retained_rank source_draw aggregate_match_distance control_surfaces aggregate_events aggregate_pages field_hit_cells field_exposure_cells field_specificity_rate positioned_amount_neighbour_cells open_positioned_amount_neighbour_cells gdt760_clean_content_contact_cells field_or_positioned_neighbour_union_cells field_or_open_positioned_neighbour_union_cells field_form_breadth positioned_amount_neighbour_form_breadth open_positioned_amount_neighbour_form_breadth gdt760_clean_content_contact_form_breadth field_and_positioned_neighbour_form_breadth field_and_open_positioned_neighbour_form_breadth field_and_clean_content_form_breadth field_or_positioned_neighbour_union_pages field_or_open_positioned_neighbour_union_pages global_l_occurrences",
    "null_summary": "null_variant metric observed null_draws null_mean null_q05 null_q50 null_q95 null_max upper_tail_p_add_one interpretation_note",
    "query_stats": "query_id source_path selector allowed_values output_columns forbidden_prefixes selected_rows skipped_forbidden_rows skipped_not_allowed_rows",
    "quality": "quality_value_id page locus section language hand head_ordinal head_surface value_surface exact_span_eva head_token_stable_all_three value_token_stable_all_three both_tokens_stable_all_three contiguous_sequence_present_all_three is_gdt803_discovery_span safe_renderer_de aggressive_renderer_de aggressive_confidence written_line_eva literal_identity_credit component_export_credit",
    "quality_summary": "summary_id head_surface value_surface zl3b_contiguous_spans both_token_stable_spans all_three_contiguous_sequence_spans external_all_three_sequence_spans pages sections safe_renderer_de aggressive_renderer_de historical_architecture_comparator word_identity_credit",
    "right_profiles": "surface reader_stable_occurrences reader_stable_pages reader_stable_right_context_opportunities reader_stable_right_context_pages reader_stable_right_dain_daiin_spans gdt803_discovery_right_value_spans external_reader_stable_right_value_spans reader_stable_right_value_pages right_value_type_counts right_value_span_rate semantic_identity_credit",
    "cheol_controls": "cohort control_rank surface individual_covariate_distance zl3b_l_occurrences zl3b_right_dain_daiin_spans zl3b_right_value_span_rate zl3b_at_least_cheol_span_count zl3b_at_least_cheol_span_rate zl3b_at_least_cheol_count_and_rate reader_stable_occurrences reader_stable_right_context_opportunities reader_stable_right_dain_daiin_spans right_value_span_rate reader_stable_at_least_cheol_span_count reader_stable_at_least_cheol_span_rate reader_stable_at_least_cheol_count_and_rate matching_outcome_fields_used semantic_identity_credit",
    "packet": "edge_id batch_id page physical_folio diagram_unit_id pivot_visual_id pivot_locus target_visual_id target_locus relation_type direction_basis ownership_basis geometry_only_selection source_manifest_id page_crop_sha256 pivot_crop_sha256 target_crop_sha256 source_aware_localizer relation_reviewer relation_confidence ambiguity_state formal_access_state fold_assignment eligibility_status",
    "reader": "bracket_id page locus exact_three_token_span left_surface left_preexisting_role left_preexisting_default_de middle_surface middle_selected_role middle_conservative_default_de right_surface right_preexisting_role right_preexisting_default_de safe_renderer_de aggressive_renderer_de aggressive_confidence preferred_model countermodel full_zl3b_line renderer_scope confirmed_plaintext confirmed_lexeme component_export_credit",
    "adjudication": "rank_for_concrete_followup surface decision selected_working_role safe_default_de aggressive_default_de confidence field_hits positioned_amount_neighbour_hits gdt760_clean_content_contact_hits quality_value_spans positive_evidence counterevidence confirmed_lexeme component_export_credit",
    "card": "card_id old_card new_card safe_display aggressive_display field_neighbour_evidence amount_slot_evidence quality_value_evidence selected_middle_lead selected_general_carrier null_rival confirmed_lexemes component_export_credit",
}
SCHEMAS = {name: value.split() for name, value in SCHEMAS.items()}

BUILDER_OUTPUTS = [*FILES.values(), "GDT804_GDT388_EDGE_INTAKE.json", "RESULT.json"]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def header(path: Path) -> list[str]:
    with path.open(encoding="utf-8", newline="") as handle:
        return next(csv.reader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(left: float | str, right: float | str, tolerance: float = 3e-10) -> bool:
    return math.isclose(float(left), float(right), rel_tol=tolerance, abs_tol=1e-13)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-replay", action="store_true")
    args = parser.parse_args()
    checks: list[str] = []

    def check(name: str, condition: bool) -> None:
        assert condition, name
        checks.append(name)

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    check("result_id", result["experiment_id"] == "GDT804")
    check("result_status", "0_GDT760_CLEAN_CONTENT_CONTACTS" in result["status"] and "CHEOL_SPECIFICITY_UNRESOLVED" in result["status"])
    check("result_zero_claim", result["confirmed_lexemes"] == result["component_export_credit"] == 0)
    check("result_scope", result["new_pages_images_or_transcriptions"] == result["f84_or_f84r_rows"] == 0)
    check("result_output_set", set(result["output_sha256"]) == set(BUILDER_OUTPUTS) - {"RESULT.json"})
    for name, digest in result["output_sha256"].items():
        check(f"hash:{name}", sha(ART / name) == digest)

    loaded: dict[str, list[dict[str, str]]] = {}
    for key, filename in FILES.items():
        path = ART / filename
        check(f"schema:{key}", header(path) == SCHEMAS[key])
        rows = read_tsv(path)
        check(f"no_blank:{key}", all(all(row[column] != "" for column in SCHEMAS[key]) for row in rows))
        loaded[key] = rows

    lock = loaded["lock"]
    check("lock_count", len(lock) == 29)
    check("lock_unique", len({row["path"] for row in lock}) == 29)
    for row in lock:
        check(f"source_hash:{row['path']}", sha(ROOT / row["path"]) == row["sha256"])
        check(f"source_relative:{row['path']}", not row["path"].startswith("/"))

    fields = loaded["fields"]
    check("field_count", len(fields) == 72)
    check("field_ids", len({row["gdt744_field_id"] for row in fields}) == 72)
    check("field_mask", {row["common_mask"] for row in fields} == {"ALL_155_PAIRED_XL_SURFACES_REMOVED_AS_SEMANTIC_ANCHORS"})
    check("field_foreign", all(int(row["foreign_anchor_count"]) > 0 for row in fields))

    exposures = loaded["exposures"]
    targets = [row for row in exposures if row["is_gdt803_middle"] == "1"]
    hits = [row for row in targets if row["independently_licensed_field"] == "1"]
    check("exposure_count", len(exposures) == 107)
    check("target_exposure_count", len({row["cell_key"] for row in targets}) == 45)
    check("target_hit_count", len({row["cell_key"] for row in hits}) == 18)
    check("target_hit_forms", len({row["surface"] for row in hits}) == 6)

    amount = loaded["amount"]
    target_amount = [row for row in amount if row["is_gdt803_middle"] == "1" and row["discovery_cell_excluded"] == "0"]
    check("amount_population", len(amount) == 41)
    check("preferred_side_target_count", len({row["cell_key"] for row in target_amount}) == 15)
    check("preferred_side_open_count", sum(row["open_positional_candidate"] == "1" for row in target_amount) == 14)
    check("preferred_side_clean_zero", sum(row["selected_side_is_clean_content_contact"] == "1" for row in target_amount) == 0)
    f88 = next(row for row in target_amount if row["expression_id"] == "G760-E0263")
    check("f88_side_correction", (f88["surface"], f88["selected_side"], f88["source_content_attachment_sides"], f88["candidate_status"]) == ("cheol", "LEFT", "R", "POSITION_HEURISTIC_OPEN_CANDIDATE"))

    union = loaded["union"]
    check("union_count", len(union) == len({row["cell_key"] for row in union}) == 30)
    check("union_fields", sum(row["common_mask_field_hit"] == "1" for row in union) == 18)
    check("union_amount", sum(row["positioned_amount_neighbour_hit"] == "1" for row in union) == 15)
    check("union_clean_zero", {row["gdt760_clean_content_contact"] for row in union} == {"0"})
    check("union_open", sum(row["common_mask_field_hit"] == "1" or row["open_positioned_amount_neighbour_hit"] == "1" for row in union) == 29)

    middle_set = {"chal", "chedal", "cheol", "okail", "okal", "ol", "otal", "qokeol", "qokol", "qotal", "sail"}
    census = {row["surface"]: row for row in loaded["census"]}
    check("census_set", len(census) == 11 and set(census) == middle_set)
    check("census_occurrences", sum(int(row["gdt800_l_occurrences"]) for row in census.values()) == 1098)
    check("census_brackets", sum(int(row["gdt803_bracket_occurrences"]) for row in census.values()) == 12)
    check("census_cheol", tuple(census["cheol"][field] for field in ("common_mask_licensed_hits", "positioned_amount_neighbour_hits", "gdt760_clean_content_contact_hits", "quality_value_right_spans")) == ("4", "3", "0", "4"))
    check("census_ol", tuple(census["ol"][field] for field in ("common_mask_licensed_hits", "positioned_amount_neighbour_hits")) == ("9", "9"))
    check("census_no_seed", "SEED_READING_RETIRED" in census["sail"]["counterevidence_code"])
    check("census_zero_claim", all(row["literal_identity"] == "OPEN" and row["confirmed_lexeme"] == row["component_export_credit"] == "0" for row in census.values()))

    pools = loaded["pools"]
    check("pool_count", len(pools) == 342)
    check("pool_variants", Counter(row["pool_variant"] for row in pools) == Counter({"PRIMARY_K12": 132, "SENSITIVITY_K10": 110, "LEAVE_OL_OUT_K10": 100}))
    check("pool_blind", {row["outcome_fields_used_for_matching"] for row in pools} == {"NONE"})

    draws = loaded["null_draws"]
    check("draw_count", len(draws) == 5000)
    check("draw_ranks", {int(row["retained_rank"]) for row in draws} == set(range(1, 5001)))
    check("draw_injective", all(len(row["control_surfaces"].split("|")) == len(set(row["control_surfaces"].split("|"))) == 11 for row in draws))
    summaries = loaded["null_summary"]
    summary = {(row["null_variant"], row["metric"]): row for row in summaries}
    check("summary_count", len(summaries) == len(summary) == 54)
    primary = "PRIMARY_AGGREGATE_MATCHED_200000_KEEP5000"
    individual = "SENSITIVITY_INDIVIDUAL_NEAREST10_100000"
    leave_ol = "LEAVE_OL_OUT_INDIVIDUAL_NEAREST10_100000"
    expected_p = {
        "field_hit_cells": 1 / 5001,
        "field_exposure_cells": 10 / 5001,
        "field_specificity_rate": 12 / 5001,
        "open_positioned_amount_neighbour_cells": 0.648470305939,
        "field_and_open_positioned_neighbour_form_breadth": 0.147170565887,
        "gdt760_clean_content_contact_cells": 1.0,
    }
    for metric, value in expected_p.items():
        check(f"primary_p:{metric}", close(summary[(primary, metric)]["upper_tail_p_add_one"], value))
        observed = float(summary[(primary, metric)]["observed"])
        exceed = sum(float(row[metric]) >= observed for row in draws)
        check(f"primary_formula:{metric}", close(summary[(primary, metric)]["upper_tail_p_add_one"], (exceed + 1) / 5001))
    check("match_sensitivity", close(summary[(individual, "field_specificity_rate")]["upper_tail_p_add_one"], 0.371076289237) and close(summary[(leave_ol, "field_specificity_rate")]["upper_tail_p_add_one"], 0.536934630654))

    query_stats = {row["query_id"]: row for row in loaded["query_stats"]}
    check("query_stats", set(query_stats) == {"ZL3B_TOKENS", "CROSS_READER_LINES"})
    check("query_allowed", {row["allowed_values"] for row in query_stats.values()} == {"179"})
    check("query_rows", query_stats["ZL3B_TOKENS"]["selected_rows"] == "32339" and query_stats["CROSS_READER_LINES"]["selected_rows"] == "4137")
    check("query_forbidden", all(row["forbidden_prefixes"] == "f84|f84r" for row in query_stats.values()))

    quality = loaded["quality"]
    raw_counts = Counter((row["head_surface"], row["value_surface"]) for row in quality)
    expected_raw = Counter({("chol", "daiin"): 29, ("chol", "dain"): 4, ("cheol", "daiin"): 4, ("sheol", "daiin"): 3, ("sheol", "dain"): 1})
    check("quality_count", len(quality) == 41 and raw_counts == expected_raw)
    check("quality_token_stable", sum(row["both_tokens_stable_all_three"] == "1" for row in quality) == 32)
    check("quality_sequence_stable", sum(row["contiguous_sequence_present_all_three"] == "1" for row in quality) == 33)
    check("quality_discovery", sum(row["is_gdt803_discovery_span"] == "1" for row in quality) == 1)
    for row in quality:
        tokens = row["written_line_eva"].split()
        ordinal = int(row["head_ordinal"])
        check(f"quality_span:{row['quality_value_id']}", tokens[ordinal - 1:ordinal + 1] == [row["head_surface"], row["value_surface"]])
    qsum = {(row["head_surface"], row["value_surface"]): row for row in loaded["quality_summary"]}
    check("quality_summary", len(qsum) == 5)
    check("cheol_sequence", tuple(qsum[("cheol", "daiin")][field] for field in ("zl3b_contiguous_spans", "both_token_stable_spans", "all_three_contiguous_sequence_spans", "external_all_three_sequence_spans")) == ("4", "2", "3", "2"))

    profiles = {row["surface"]: row for row in loaded["right_profiles"]}
    check("profile_set", set(profiles) == middle_set)
    check("profile_cheol", tuple(profiles["cheol"][field] for field in ("reader_stable_right_context_opportunities", "reader_stable_right_dain_daiin_spans", "gdt803_discovery_right_value_spans", "external_reader_stable_right_value_spans")) == ("114", "2", "1", "1"))
    check("profile_qokol", tuple(profiles["qokol"][field] for field in ("reader_stable_right_context_opportunities", "reader_stable_right_dain_daiin_spans", "external_reader_stable_right_value_spans")) == ("82", "4", "4"))
    check("profile_ol", tuple(profiles["ol"][field] for field in ("reader_stable_right_context_opportunities", "reader_stable_right_dain_daiin_spans", "external_reader_stable_right_value_spans")) == ("339", "9", "9"))
    controls = loaded["cheol_controls"]
    control_only = [row for row in controls if row["cohort"] != "TARGET"]
    check("cheol_control_count", len(controls) == 13 and len(control_only) == 12)
    check("cheol_control_blind", {row["matching_outcome_fields_used"] for row in controls} == {"NONE"})
    check("cheol_raw_fail", tuple(sum(int(row[field]) for row in control_only) for field in ("zl3b_at_least_cheol_span_count", "zl3b_at_least_cheol_span_rate", "zl3b_at_least_cheol_count_and_rate")) == (7, 7, 5))
    check("cheol_reader_fail", tuple(sum(int(row[field]) for row in control_only) for field in ("reader_stable_at_least_cheol_span_count", "reader_stable_at_least_cheol_span_rate", "reader_stable_at_least_cheol_count_and_rate")) == (8, 10, 8))

    packet = loaded["packet"]
    check("packet_count", len(packet) == 41)
    check("packet_breadth", len({row["page"] for row in packet}) == 37 and len({row["physical_folio"] for row in packet}) == 31)
    check("packet_ineligible", {row["formal_access_state"] for row in packet} == {"FORMAL_ACCESSED"} and {row["eligibility_status"] for row in packet} == {"INELIGIBLE_EXPLORATORY_TEXT_RELATION"})
    check("packet_no_f84", all(not row[field].startswith("f84") for row in packet for field in ("page", "physical_folio", "pivot_locus", "target_locus")))
    expected_intake = {
        "status": "INVALID_PACKET", "packet_rows": 41, "eligible_edges": 0,
        "eligible_folios": 0, "discovery_edges": 0, "holdout_edges": 0,
        "mobile_edges": 0, "capacity_gate_50_edges_5_folios": False,
        "holdout_gate": False, "mobile_null_gate": False, "score_ready": False,
        "errors": [f"edge row {number}: formal access is not sealed" for number in range(2, 43)],
    }
    stored_intake = json.loads((ART / "GDT804_GDT388_EDGE_INTAKE.json").read_text(encoding="utf-8"))
    check("stored_intake", stored_intake == expected_intake == result["quality_value_edge_intake"])
    intake_run = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", str((ART / FILES["packet"]).relative_to(ROOT))],
        cwd=ROOT, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    check("intake_exit", intake_run.returncode == 1 and intake_run.stderr == "")
    check("intake_replay", json.loads(intake_run.stdout) == expected_intake)

    reader = loaded["reader"]
    check("reader_count", len(reader) == 12)
    check("reader_scoped", {row["renderer_scope"] for row in reader} == {"THIS_EXACT_THREE_TOKEN_SPAN_ONLY"})
    check("reader_exact", all(row["exact_three_token_span"] in row["full_zl3b_line"] for row in reader))
    check("reader_zero", all(row["confirmed_plaintext"] == row["confirmed_lexeme"] == row["component_export_credit"] == "0" for row in reader))
    central = next(row for row in reader if row["exact_three_token_span"] == "qokain cheol daiin")
    check("central_candidate", central["aggressive_renderer_de"] == "heiß im II. Grad; trocken im III. Grad" and central["aggressive_confidence"] == "C0_AGGRESSIVE")
    adjudication = {row["surface"]: row for row in loaded["adjudication"]}
    check("adjudication_set", set(adjudication) == middle_set)
    check("adjudication_cheol", adjudication["cheol"]["decision"] == "RETAIN_BEST_MATERIAL_RIVAL__NO_RIGHT_VALUE_SPECIFICITY_LEAD")
    check("adjudication_qokol", adjudication["qokol"]["decision"] == "RETAIN_PROCESS_RIVAL__STRONGEST_EXTERNAL_RIGHT_VALUE_COUNT")
    check("adjudication_zero", all(row["confirmed_lexeme"] == row["component_export_credit"] == "0" for row in adjudication.values()))
    check("card", len(loaded["card"]) == 1 and loaded["card"][0]["confirmed_lexemes"] == loaded["card"][0]["component_export_credit"] == "0")

    target_score = result["target_score"]
    check("result_target", (target_score["field_hit_cells"], target_score["field_exposure_cells"], target_score["positioned_amount_neighbour_cells"], target_score["open_positioned_amount_neighbour_cells"], target_score["gdt760_clean_content_contact_cells"]) == (18, 45, 15, 14, 0))
    check("result_quality", (result["quality_value_spans"], result["quality_value_token_stable_spans"], result["quality_value_all_three_sequence_spans"]) == (41, 32, 33))
    check("result_controls", (result["cheol_k12_zl3b_controls_at_least_count"], result["cheol_k12_zl3b_controls_at_least_rate"], result["cheol_k12_zl3b_controls_at_least_count_and_rate"], result["cheol_k12_reader_stable_controls_at_least_count"], result["cheol_k12_reader_stable_controls_at_least_rate"], result["cheol_k12_reader_stable_controls_at_least_count_and_rate"]) == (7, 7, 5, 8, 10, 8))
    report = (EXP / "REPORT.md").read_text(encoding="utf-8")
    check("report_control_sensitive", "kontrollsensitiver Sachfeld-Nachbarschaftslead" in report)
    check("report_zero_content", "Keine der fünfzehn" in report and "GDT760s tatsächliche Inhaltslizenz gehört rechts zu `cheos`" in report)
    check("report_sequence", "41-mal" in report and "33 Paarsequenzen" in report and "Stabilitätsgate behält 32" in report)
    check("report_specificity", "ohne Spezifitätsvorsprung" in report and "`qokol` 4" in report)
    check("report_edge", "41 Kanten liegen unter der Kapazitätsgrenze 50" in report)
    check("report_zero_plaintext", "nicht bestätigter Klartext" in report)

    baseline = {name: sha(ART / name) for name in BUILDER_OUTPUTS}
    replay_count = 0
    if not args.skip_replay:
        for replay in range(2):
            with tempfile.TemporaryDirectory(
                prefix=f".gdt804_replay_{replay + 1}_", dir=EXP
            ) as temp:
                output = Path(temp) / "artifacts"
                completed = subprocess.run(
                    ["python3", str(SRC / "run.py"), "--output-dir", str(output)],
                    cwd=ROOT, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                )
                check(f"replay_exit:{replay + 1}", completed.returncode == 0 and completed.stderr == "")
                check(f"replay_set:{replay + 1}", sorted(path.name for path in output.iterdir()) == sorted(BUILDER_OUTPUTS))
                for name, digest in baseline.items():
                    check(f"replay_hash:{replay + 1}:{name}", sha(output / name) == digest)
                replay_count += 1

    validation = {
        "schema": "GDT804_VALIDATION_V1",
        "experiment": "GDT804",
        "status": "PASS",
        "checks": len(checks),
        "replays": replay_count,
        "common_mask_fields": 72,
        "target_field_hits": 18,
        "preferred_side_amount_neighbours": 15,
        "gdt760_prelicensed_target_content_contacts": 0,
        "zl3b_quality_value_spans": 41,
        "all_reader_sequence_spans": 33,
        "token_stable_spans": 32,
        "gdt388_score_ready": False,
        "confirmed_lexemes": 0,
        "component_exports": 0,
        "new_pages_images_or_transcriptions": 0,
        "sealed_f84_or_f84r_seen": False,
        "validated_result_hash": sha(RESULT),
        "validated_output_hashes": {
            name: sha(ART / name) for name in BUILDER_OUTPUTS if name != "RESULT.json"
        },
    }
    validation["content_hash"] = hashlib.sha256(
        json.dumps(validation, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PASS: {len(checks)} checks; {replay_count} byte-identical replays; GDT388 not score-ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
