#!/usr/bin/env python3
"""Validate GDT805's corrected context projections and deterministic replay."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
import subprocess
import tempfile
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt805_eleven_whole_context_role_discriminator"
SRC = EXP / "src"
ART = EXP / "artifacts"
RESULT = ART / "RESULT.json"
VALIDATION = ART / "VALIDATION.json"

FILES = {
    "lock": "SOURCE_LOCK.tsv",
    "query": "GDT805_GUARDED_QUERY_STATS.tsv",
    "projection": "GDT805_131_GDT739_SURFACE_PROJECTION_AUDIT.tsv",
    "atlas": "GDT805_1086_EXTERNAL_CONTEXT_ATLAS.tsv",
    "capacity": "GDT805_11_CONTEXT_CAPACITY.tsv",
    "identity": "GDT805_NEIGHBOUR_IDENTITY_PROFILE.tsv",
    "roles": "GDT805_ROLE_CONTACT_PROFILE.tsv",
    "comparisons": "GDT805_K12_ROLE_COMPARISON.tsv",
    "leads": "GDT805_ROLE_LEADS.tsv",
    "frames": "GDT805_13_REPEATED_FRAME_TYPES.tsv",
    "scores": "GDT805_CANDIDATE_SCORECARD.tsv",
    "adjudication": "GDT805_11_CANDIDATE_ADJUDICATION.tsv",
    "passages": "GDT805_45_PASSAGE_CARDS.tsv",
    "packet": "GDT805_GDT388_CONTEXT_EDGE_PACKET.tsv",
    "card": "GDT805_STRUCTURAL_CARD.tsv",
}

SCHEMAS = {
    "lock": "path sha256 purpose",
    "query": "query_id source_path selector allowed_values output_columns forbidden_prefixes selected_rows skipped_forbidden_rows skipped_not_allowed_rows",
    "projection": "projection_audit_id surface axis_tags axis_displays_de gdt739_all_radius_contacts gdt739_active_radius_contacts gdt739_active_radius_pages gdt739_active_radius_loci source_radius_tier confidence_levels gdt754_quarantined gdt738_hold is_gdt805_target primary_surface_projection_allowed projection_exclusion_reason german_working_string_imported axis_tags_derived_from_german_working_prose renderer_license semantic_credit confirmed_lexeme component_export_credit",
    "atlas": "context_id occurrence_id source_selector physical_folio locus section language hand token_index token_count position_class surface l2_surface l1_surface r1_surface r2_surface exact_five_window target_token_stable_all_three l1_token_stable_all_three r1_token_stable_all_three l1_pair_sequence_stable_all_three r1_pair_sequence_stable_all_three l2_chain_sequence_stable_all_three r2_chain_sequence_stable_all_three l1_target_r1_sequence_stable_all_three l2_to_r2_sequence_stable_all_three bol_target_stable_all_three target_eol_stable_all_three l1_anchor_kind l1_axis_tags l1_axis_default_de r1_anchor_kind r1_axis_tags r1_axis_default_de gdt804_common_mask_field_hit gdt804_positioned_amount_neighbour_hit gdt804_clean_content_contact full_zl3b_line semantic_credit confirmed_plaintext confirmed_lexeme component_export_credit",
    "capacity": "surface total_l_occurrences discovery_occurrences_subtracted external_occurrences external_source_selectors external_physical_folios target_token_stable_external l1_pair_sequence_stable_external r1_pair_sequence_stable_external l2_chain_sequence_stable_external r2_chain_sequence_stable_external two_sided_frame_sequence_stable_external five_window_sequence_stable_external left_unique_neighbours left_nonboundary_opportunities left_normalized_identity_entropy left_top1_identity_rate left_top5_identity_rate right_unique_neighbours right_nonboundary_opportunities right_normalized_identity_entropy right_top1_identity_rate right_top5_identity_rate mapped_axis_breadth capacity_decision confirmed_lexeme component_export_credit",
    "identity": "identity_profile_id surface side neighbour_surface anchor_kind axis_tags external_occurrences physical_folios target_token_stable_occurrences neighbour_token_stable_occurrences pair_sequence_stable_occurrences pair_sequence_stable_folios semantic_credit confirmed_lexeme component_export_credit",
    "roles": "surface side axis external_opportunities axis_contact_occurrences axis_contact_physical_folios raw_axis_contact_rate pair_stable_opportunities pair_stable_axis_contacts pair_stable_axis_contact_folios pair_stable_axis_contact_rate role_source semantic_credit confirmed_lexeme component_export_credit",
    "comparisons": "comparison_id surface side axis target_contacts target_contact_folios target_raw_rate target_pair_stable_contacts target_pair_stable_folios target_pair_stable_rate raw_rank_of_13 pair_stable_rank_of_13 raw_controls_equal_or_exceed pair_stable_controls_equal_or_exceed control_raw_median control_raw_max control_pair_stable_median control_pair_stable_max raw_above_all_controls pair_stable_above_all_controls dominates_all_controls_both_views control_rates control_pair_stable_rates decision semantic_credit confirmed_lexeme component_export_credit",
    "leads": "lead_id surface side axis target_contacts target_contact_folios target_raw_rate target_pair_stable_contacts target_pair_stable_folios target_pair_stable_rate raw_rank_of_13 pair_stable_rank_of_13 raw_controls_equal_or_exceed pair_stable_controls_equal_or_exceed control_raw_median control_pair_stable_median raw_above_all_controls pair_stable_above_all_controls dominates_all_controls_both_views interpretation_de role_source semantic_credit renderer_license meaning_ceiling confirmed_lexeme component_export_credit",
    "frames": "frame_id surface frame_class left_surface right_surface exact_frame occurrences physical_folios stable_sequence_occurrences loci left_axis_tags right_axis_tags meaning_ceiling confirmed_lexeme component_export_credit",
    "scores": "surface candidate_id candidate_class concrete_working_reading_de left_support_axes right_support_axes context_bridge_hypothesis literal_identity pre_gdt805_confidence countercandidate_de component_export_credit external_physical_folios mapped_axis_breadth expected_signature_count dominant_role_lead_count dominant_role_leads full_role_lead_count full_role_leads near_only_lead_count near_only_leads context_bridge_flag context_bridge_detail context_bridge_is_independent_semantics direct_content_bridge_pass candidate_score candidate_score_density score_is_probability semantic_status confirmed_lexeme",
    "adjudication": "surface decision diagnostic_top_candidate_id diagnostic_top_score_density leading_candidate_id leading_candidate_class leading_concrete_working_reading_de leading_score runner_up_candidate_id runner_up_working_reading_de runner_up_score score_margin context_role_leads dominant_role_leads context_bridge_hypothesis context_bridge_flag context_bridge_is_independent_semantics direct_content_bridge_pass safe_gdt804_default_de new_role_selected prior_role_retained confidence literal_identity confirmed_plaintext confirmed_lexeme component_export_credit",
    "passages": "passage_id surface source_selector physical_folio locus token_index exact_five_window full_zl3b_line left_complete_surface left_axis_evidence_kind left_broad_axis target_safe_role_de leading_concrete_candidate_de right_complete_surface right_axis_evidence_kind right_broad_axis safe_role_skeleton_de projected_axis_skeleton_de concrete_candidate_display_de strongest_rival_de adjudication selection_score target_token_stable_all_three left_pair_stable_all_three right_pair_stable_all_three renderer_scope confirmed_plaintext confirmed_lexeme component_export_credit",
    "packet": "edge_id batch_id page physical_folio diagram_unit_id pivot_visual_id pivot_locus target_visual_id target_locus relation_type direction_basis ownership_basis geometry_only_selection source_manifest_id page_crop_sha256 pivot_crop_sha256 target_crop_sha256 source_aware_localizer relation_reviewer relation_confidence ambiguity_state formal_access_state fold_assignment eligibility_status",
    "card": "experiment status selected_structure external_events target_token_stable gdt739_surfaces_audited primary_surface_projection_wholes exact_gdt739_context_cells projected_context_contacts k12_profile_leads dominant_k12_profile_leads real_two_sided_multifolio_frames boundary_anchored_one_sided_frames new_role_selections retained_prior_roles meaning_ceiling confirmed_lexemes confirmed_plaintext component_export_credit new_pages_images_or_transcriptions",
}
SCHEMAS = {name: fields.split() for name, fields in SCHEMAS.items()}
BUILDER_OUTPUTS = [*FILES.values(), "GDT805_GDT388_EDGE_INTAKE.json", "RESULT.json"]
TARGETS = {"chal", "chedal", "cheol", "okail", "okal", "ol", "otal", "qokeol", "qokol", "qotal", "sail"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def header(path: Path) -> list[str]:
    with path.open(encoding="utf-8", newline="") as handle:
        return next(csv.reader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(left: float | str, right: float | str) -> bool:
    return math.isclose(float(left), float(right), rel_tol=3e-10, abs_tol=1e-13)


def parse_rates(value: str) -> list[float]:
    return [float(item.rsplit(":", 1)[1]) for item in value.split("|")]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-replay", action="store_true")
    args = parser.parse_args()
    checks: list[str] = []

    def check(name: str, condition: bool) -> None:
        assert condition, name
        checks.append(name)

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    check("result_id", result["experiment_id"] == "GDT805")
    check("result_status", "75_PRIMARY_SURFACE_PROJECTIONS" in result["status"] and "0_NEW_ROLE_SELECTIONS" in result["status"])
    check("result_scope", result["new_pages_images_or_transcriptions"] == result["f84_or_f84r_rows"] == 0)
    check("result_zero_claim", result["confirmed_lexemes"] == result["confirmed_plaintext_clauses"] == result["component_export_credit"] == 0)
    check("result_output_set", set(result["output_sha256"]) == set(BUILDER_OUTPUTS) - {"RESULT.json"})
    for filename, digest in result["output_sha256"].items():
        check(f"hash:{filename}", sha(ART / filename) == digest)

    loaded: dict[str, list[dict[str, str]]] = {}
    for key, filename in FILES.items():
        check(f"schema:{key}", header(ART / filename) == SCHEMAS[key])
        rows = read_tsv(ART / filename)
        check(f"no_blank:{key}", all(all(row[field] != "" for field in SCHEMAS[key]) for row in rows))
        loaded[key] = rows

    lock = loaded["lock"]
    check("lock_count", len(lock) == 22)
    check("lock_unique", len({row["path"] for row in lock}) == 22)
    for row in lock:
        check(f"source_relative:{row['path']}", not row["path"].startswith("/") and ".." not in Path(row["path"]).parts)
        check(f"source_hash:{row['path']}", sha(ROOT / row["path"]) == row["sha256"])

    query = {row["query_id"]: row for row in loaded["query"]}
    check("query_ids", set(query) == {"ZL3B_TOKENS", "CROSS_READER_LINES"})
    check("query_allow", {row["allowed_values"] for row in query.values()} == {"179"})
    check("query_guard", {row["forbidden_prefixes"] for row in query.values()} == {"f84|f84r"})
    check("query_counts", query["ZL3B_TOKENS"]["selected_rows"] == "32339" and query["CROSS_READER_LINES"]["selected_rows"] == "4137")

    projection = loaded["projection"]
    check("projection_count", len(projection) == len({row["surface"] for row in projection}) == 131)
    check("projection_active_sources", sum(row["source_radius_tier"] == "ACTIVE_RADIUS_SOURCE" for row in projection) == 87)
    check("projection_quarantine", sum(row["gdt754_quarantined"] == "1" for row in projection) == 14)
    check("projection_holds", sum(row["gdt738_hold"] == "1" for row in projection) == 0)
    check("projection_targets", sum(row["is_gdt805_target"] == "1" for row in projection) == 4)
    check("projection_primary", sum(row["primary_surface_projection_allowed"] == "1" for row in projection) == 75)
    check("projection_credit", all(row["german_working_string_imported"] == row["renderer_license"] == row["semantic_credit"] == row["confirmed_lexeme"] == row["component_export_credit"] == "0" and row["axis_tags_derived_from_german_working_prose"] == "1" for row in projection))

    atlas = loaded["atlas"]
    check("atlas_count", len(atlas) == len({row["context_id"] for row in atlas}) == len({row["occurrence_id"] for row in atlas}) == 1086)
    check("atlas_targets", {row["surface"] for row in atlas} == TARGETS - {"okail"})
    check("atlas_no_sealed", all(not row[field].startswith("f84") for row in atlas for field in ("source_selector", "physical_folio", "locus")))
    check("atlas_zero_claim", all(row["confirmed_plaintext"] == row["confirmed_lexeme"] == row["component_export_credit"] == "0" for row in atlas))
    kind_counts = Counter(row[f"{side}_anchor_kind"] for row in atlas for side in ("l1", "r1"))
    check("atlas_exact_cells", kind_counts["GDT739_EXACT_ACTIVE_CELL"] == 6)
    check("atlas_projections", kind_counts["GDT805_EXPLORATORY_SURFACE_AXIS_PROJECTION"] == 178)
    check("atlas_target_stable", sum(row["target_token_stable_all_three"] == "1" for row in atlas) == 916)
    stable_fields = (
        "l1_pair_sequence_stable_all_three", "r1_pair_sequence_stable_all_three",
        "l2_chain_sequence_stable_all_three", "r2_chain_sequence_stable_all_three",
        "l1_target_r1_sequence_stable_all_three", "l2_to_r2_sequence_stable_all_three",
    )
    check("atlas_sequence_totals", tuple(sum(row[field] == "1" for row in atlas) for field in stable_fields) == (677, 663, 475, 461, 495, 228))
    for row in atlas:
        tokens = row["full_zl3b_line"].split()
        index = int(row["token_index"]) - 1
        check(f"atlas_target:{row['context_id']}", tokens[index] == row["surface"])
        check(f"atlas_left:{row['context_id']}", row["l1_surface"] == (tokens[index - 1] if index else "NONE"))
        check(f"atlas_right:{row['context_id']}", row["r1_surface"] == (tokens[index + 1] if index + 1 < len(tokens) else "NONE"))

    capacity = {row["surface"]: row for row in loaded["capacity"]}
    expected_external = {"chal": 41, "chedal": 21, "cheol": 141, "okail": 0, "okal": 122, "ol": 462, "otal": 117, "qokeol": 38, "qokol": 87, "qotal": 56, "sail": 1}
    expected_stable = {"chal": 34, "chedal": 14, "cheol": 117, "okail": 0, "okal": 101, "ol": 376, "otal": 107, "qokeol": 33, "qokol": 81, "qotal": 53, "sail": 0}
    check("capacity_set", set(capacity) == TARGETS)
    check("capacity_external", {key: int(row["external_occurrences"]) for key, row in capacity.items()} == expected_external)
    check("capacity_stable", {key: int(row["target_token_stable_external"]) for key, row in capacity.items()} == expected_stable)
    check("capacity_decisions", {key for key, row in capacity.items() if row["capacity_decision"] == "NO_EXTERNAL_CAPACITY"} == {"okail", "sail"})

    check("identity_count", len(loaded["identity"]) == 1455)
    check("role_count", len(loaded["roles"]) == 264)
    comparisons = loaded["comparisons"]
    check("comparison_count", len(comparisons) == 264)
    for row in comparisons:
        raw = parse_rates(row["control_rates"])
        stable = parse_rates(row["control_pair_stable_rates"])
        target_raw = float(row["target_raw_rate"])
        target_stable = float(row["target_pair_stable_rate"])
        check(f"comparison_pool:{row['comparison_id']}", len(raw) == len(stable) == 12)
        check(f"comparison_raw_rank:{row['comparison_id']}", int(row["raw_rank_of_13"]) == 1 + sum(value >= target_raw for value in raw))
        check(f"comparison_stable_rank:{row['comparison_id']}", int(row["pair_stable_rank_of_13"]) == 1 + sum(value >= target_stable for value in stable))
        check(f"comparison_raw_median:{row['comparison_id']}", close(row["control_raw_median"], statistics.median(raw)))
        check(f"comparison_stable_median:{row['comparison_id']}", close(row["control_pair_stable_median"], statistics.median(stable)))
        dominates = target_raw > max(raw) and target_stable > max(stable)
        check(f"comparison_dominance:{row['comparison_id']}", int(row["dominates_all_controls_both_views"]) == int(dominates))

    leads = loaded["leads"]
    check("lead_count", len(leads) == 21)
    check("lead_unique", len({(row["surface"], row["side"], row["axis"]) for row in leads}) == 21)
    check("lead_gate", all(int(row["target_contact_folios"]) >= 3 and int(row["target_pair_stable_folios"]) >= 3 and int(row["raw_rank_of_13"]) <= 3 and int(row["pair_stable_rank_of_13"]) <= 3 and float(row["target_raw_rate"]) > float(row["control_raw_median"]) and float(row["target_pair_stable_rate"]) > float(row["control_pair_stable_median"]) for row in leads))
    check("lead_projection_ceiling", all(row["interpretation_de"].startswith("projizierter ") and row["role_source"] == "GDT805_EXPLORATORY_SURFACE_AXIS_PROJECTION" and row["semantic_credit"] == row["renderer_license"] == row["confirmed_lexeme"] == row["component_export_credit"] == "0" for row in leads))
    dominant = {(row["surface"], row["side"], row["axis"]) for row in leads if row["dominates_all_controls_both_views"] == "1"}
    check("dominant_leads", dominant == {("okal", "L1", "HOT"), ("otal", "R1", "CLOSE")})

    frames = loaded["frames"]
    check("frame_count", len(frames) == 13)
    check("frame_classes", Counter(row["frame_class"] for row in frames) == Counter({"REAL_TWO_SIDED_FRAME": 7, "BOUNDARY_ANCHORED_ONE_SIDED_FRAME": 6}))
    check("frame_none", all((row["left_surface"] == "NONE") ^ (row["right_surface"] == "NONE") for row in frames if row["frame_class"] == "BOUNDARY_ANCHORED_ONE_SIDED_FRAME"))
    check("frame_real", all(row["left_surface"] != "NONE" and row["right_surface"] != "NONE" for row in frames if row["frame_class"] == "REAL_TWO_SIDED_FRAME"))

    scores = loaded["scores"]
    check("score_count", len(scores) == len({row["candidate_id"] for row in scores}) == 20)
    for row in scores:
        full = set() if row["full_role_leads"] == "NONE" else set(row["full_role_leads"].split("|"))
        near = set() if row["near_only_leads"] == "NONE" else set(row["near_only_leads"].split("|"))
        dominant_set = set() if row["dominant_role_leads"] == "NONE" else set(row["dominant_role_leads"].split("|"))
        check(f"score_disjoint:{row['candidate_id']}", full.isdisjoint(near) and dominant_set <= full)
        expected_score = 5 * len(dominant_set) + 2 * (len(full) - len(dominant_set)) + len(near)
        check(f"score_formula:{row['candidate_id']}", int(row["candidate_score"]) == expected_score)
        width = int(row["expected_signature_count"])
        density = expected_score / width if width else 0
        check(f"score_density:{row['candidate_id']}", close(row["candidate_score_density"], density))
        check(f"score_ceiling:{row['candidate_id']}", row["context_bridge_is_independent_semantics"] == row["direct_content_bridge_pass"] == row["score_is_probability"] == row["confirmed_lexeme"] == row["component_export_credit"] == "0")
        check(f"score_diagnostic:{row['candidate_id']}", row["semantic_status"] == "WIDTH_SCALED_AXIS_CORRELATED_RIVAL_DIAGNOSTIC_ONLY__NO_SELECTION")

    adjudication = loaded["adjudication"]
    check("adjudication_set", len(adjudication) == 11 and {row["surface"] for row in adjudication} == TARGETS)
    check("adjudication_new_zero", {row["new_role_selected"] for row in adjudication} == {"0"})
    check("adjudication_prior_two", {row["surface"] for row in adjudication if row["prior_role_retained"] == "1"} == {"okal", "ol"})
    check("adjudication_direct_zero", {row["direct_content_bridge_pass"] for row in adjudication} == {"0"})
    check("adjudication_capacity", {row["surface"] for row in adjudication if row["decision"] == "NO_EXTERNAL_CAPACITY"} == {"okail", "sail"})
    check("adjudication_no_prefer", all(not row["decision"].startswith(("SELECT_", "PREFER_")) for row in adjudication))

    passages = loaded["passages"]
    check("passage_count", len(passages) == 45)
    by_surface: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in passages:
        by_surface[row["surface"]].append(row)
        check(f"passage_scope:{row['passage_id']}", row["renderer_scope"] == "EXPLORATORY_PASSAGE_CARD__SURFACE_PROJECTION_NOT_RENDERER_LICENSE")
        check(f"passage_zero:{row['passage_id']}", row["confirmed_plaintext"] == row["confirmed_lexeme"] == row["component_export_credit"] == "0")
        if row["left_axis_evidence_kind"] == "GDT805_EXPLORATORY_SURFACE_AXIS_PROJECTION":
            check(f"passage_left_safe:{row['passage_id']}", f"[{row['left_complete_surface']}:?]" in row["safe_role_skeleton_de"])
        if row["right_axis_evidence_kind"] == "GDT805_EXPLORATORY_SURFACE_AXIS_PROJECTION":
            check(f"passage_right_safe:{row['passage_id']}", f"[{row['right_complete_surface']}:?]" in row["safe_role_skeleton_de"])
    check("passage_targets", set(by_surface) == TARGETS - {"okail", "sail"})
    check("passage_five_each", all(len(rows) == 5 and len({row["physical_folio"] for row in rows}) == 5 for rows in by_surface.values()))

    packet = loaded["packet"]
    check("packet_count", len(packet) == 184)
    check("packet_state", {row["formal_access_state"] for row in packet} == {"FORMAL_ACCESSED"} and {row["eligibility_status"] for row in packet} == {"INELIGIBLE_EXPLORATORY_TEXT_RELATION"})
    check("packet_no_sealed", all(not row[field].startswith("f84") for row in packet for field in ("page", "physical_folio", "pivot_locus", "target_locus")))
    intake = json.loads((ART / "GDT805_GDT388_EDGE_INTAKE.json").read_text(encoding="utf-8"))
    check("intake", intake["status"] == "INVALID_PACKET" and intake["packet_rows"] == 184 and intake["eligible_edges"] == 0 and not intake["score_ready"] and len(intake["errors"]) == 184)

    card = loaded["card"]
    check("card", len(card) == 1 and card[0]["new_role_selections"] == "0" and card[0]["retained_prior_roles"] == "2" and card[0]["confirmed_lexemes"] == card[0]["component_export_credit"] == "0")
    check("result_counts", result["gdt739_surfaces_audited"] == 131 and result["primary_surface_projection_wholes"] == 75 and result["exact_gdt739_context_cells"] == 6 and result["projected_context_contacts"] == 178)
    check("result_leads", result["k12_profile_leads"] == 21 and result["dominant_k12_profile_leads"] == 2 and len(result["projected_axis_profile_leads"]) == 21 and "role_leads" not in result)
    check("result_rival_key", set(result["displayed_rival_candidates_de"]) == TARGETS and "leading_concrete_candidates_de" not in result)
    check("result_roles", result["new_role_selections"] == 0 and result["retained_prior_roles"] == 2)

    report = (EXP / "REPORT.md").read_text(encoding="utf-8")
    check("report_projection", "keine unabhängige Semantik und keine" in report and "Nur 6 Flankenzellen" in report)
    check("report_correction", "Das war falsch" in report and "installiert aus den Projektionen null neue Rollen" in report)
    check("report_concrete", "bestimmtes Medium: Öl, Wasser oder Wein" in report and "Ausgangsansatz oder Stoffzubereitung" in report)
    check("report_next", "in drei getrennten Kanälen replizieren" in report and "pro disjunkter Makroklasse nur einmal" in report)

    baseline = {filename: sha(ART / filename) for filename in BUILDER_OUTPUTS}
    replay_count = 0
    if not args.skip_replay:
        for replay in range(2):
            with tempfile.TemporaryDirectory(prefix=f".gdt805_replay_{replay + 1}_", dir=EXP) as temp:
                output = Path(temp) / "artifacts"
                completed = subprocess.run(
                    ["python3", str(SRC / "run.py"), "--output-dir", str(output)],
                    cwd=ROOT, check=False, text=True,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                )
                check(f"replay_exit:{replay + 1}", completed.returncode == 0 and completed.stderr == "")
                check(f"replay_set:{replay + 1}", sorted(path.name for path in output.iterdir()) == sorted(BUILDER_OUTPUTS))
                for filename, digest in baseline.items():
                    check(f"replay_hash:{replay + 1}:{filename}", sha(output / filename) == digest)
                replay_count += 1

    validation = {
        "schema": "GDT805_VALIDATION_V1",
        "experiment": "GDT805",
        "status": "PASS",
        "checks": len(checks),
        "replays": replay_count,
        "external_context_events": 1086,
        "target_token_stable": 916,
        "audited_gdt739_surfaces": 131,
        "primary_surface_projections": 75,
        "exact_source_context_cells": 6,
        "projected_context_contacts": 178,
        "k12_profile_leads": 21,
        "dominant_k12_profile_leads": 2,
        "new_role_selections": 0,
        "retained_prior_roles": 2,
        "gdt388_score_ready": False,
        "confirmed_lexemes": 0,
        "component_exports": 0,
        "new_pages_images_or_transcriptions": 0,
        "sealed_f84_or_f84r_seen": False,
        "validated_result_hash": sha(RESULT),
        "validated_output_hashes": {
            filename: sha(ART / filename)
            for filename in BUILDER_OUTPUTS if filename != "RESULT.json"
        },
    }
    validation["content_hash"] = hashlib.sha256(
        json.dumps(validation, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PASS: {len(checks)} checks; {replay_count} byte-identical replays; 0 new roles; GDT388 not score-ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
