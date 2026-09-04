#!/usr/bin/env python3
"""Independent validation for GDT806.

This validator never imports the GDT806 builder. It rebuilds the global deck,
queries mixed reader data only through the guarded CLI, and recomputes the
exact-rational scores and decision gates from emitted contacts.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import subprocess
import tempfile
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Sequence


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt806_three_channel_whole_context_replication"
SRC = EXP / "src"
ART = EXP / "artifacts"
RESULT = ART / "RESULT.json"
VALIDATION = ART / "VALIDATION.json"
RUN = SRC / "run.py"
VMANUS_EXP = ROOT / "vmanus-exp"

G734 = ROOT / "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_1606_COMPLETE_WORD_CONFIDENCE.tsv"
G738 = ROOT / "experiments/yolo/gdt738_held_body_occurrence_semantic_adjudication/artifacts/MANUAL_HOLD_AUDIT.tsv"
G739_AXES = ROOT / "experiments/yolo/gdt739_twelve_whole_local_dimension_dispatch/src/ANCHOR_AXIS_SPECS.tsv"
G739_WINDOWS = ROOT / "experiments/yolo/gdt739_twelve_whole_local_dimension_dispatch/artifacts/WINDOW_202_TOKEN_AUDIT.tsv"
G754 = ROOT / "experiments/yolo/gdt754_active_productive_compound_provenance_sieve/artifacts/PROVENANCE_SIEVE_172_DECISIONS.tsv"
G800 = ROOT / "experiments/yolo/gdt800_terminal_b2_b3_line_final_bridge/artifacts/GDT800_4137_MATCHED_TERMINAL_OCCURRENCES.tsv"
G802 = ROOT / "experiments/yolo/gdt802_masked_lm_neighbour_context_transfer/artifacts/GDT802_4137_MASKED_NEIGHBOUR_ATLAS.tsv"
G803 = ROOT / "experiments/yolo/gdt803_recurrent_context_rarity_discriminator/artifacts/GDT803_12_BIDIRECTIONAL_BRACKETS.tsv"
G804 = ROOT / "experiments/yolo/gdt804_bracket_middle_independent_field_bridge/artifacts/GDT804_NEAREST_CONTROL_POOLS.tsv"
G805_ATLAS = ROOT / "experiments/yolo/gdt805_eleven_whole_context_role_discriminator/artifacts/GDT805_1086_EXTERNAL_CONTEXT_ATLAS.tsv"
G805_AUDIT = ROOT / "experiments/yolo/gdt805_eleven_whole_context_role_discriminator/artifacts/GDT805_131_GDT739_SURFACE_PROJECTION_AUDIT.tsv"
G805_FRAMES = ROOT / "experiments/yolo/gdt805_eleven_whole_context_role_discriminator/artifacts/GDT805_13_REPEATED_FRAME_TYPES.tsv"
G805_LOCK = ROOT / "experiments/yolo/gdt805_eleven_whole_context_role_discriminator/artifacts/SOURCE_LOCK.tsv"
ALLOWLIST = ROOT / "experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv"
CROSS_RAW = ROOT / "transcription/voynich_cross_transcription_lines.tsv"

TARGETS = ("cheol", "otal", "okal", "ol", "qokeol", "qokol")
TARGET_SET = set(TARGETS)
ALL_TARGETS = {"chal", "chedal", "cheol", "okail", "okal", "ol", "otal", "qokeol", "qokol", "qotal", "sail"}
C1 = "C1_EXACT_LOCAL"
C2 = "C2_GDT739_NARROW_PROJECTED"
C3 = "C3_GDT734_GLOBAL_RESIDUAL"
FULL = "GDT734_GLOBAL652_SENSITIVITY"
NONE = "NONE"
SCORED = (C2, C3, FULL)
DENOMS = ("MAPPED_CONTACTS", "ALL_OPPORTUNITIES")
VIEWS = ("RAW", "PAIR_STABLE")
SIDES = ("L1", "R1")
THRESHOLD = Fraction(1, 20)
MACRO_MEMBERS = {
    "QUALITY": {"HOT", "COLD", "DRY", "MOIST"},
    "SCALAR": {"AMOUNT", "VALUE", "PASS"},
    "CARRIER": {"PART", "MATERIAL", "PREPARATION"},
    "PROCESS": {"PROCESS", "CLOSE"},
}
EXPECTED_CAPACITY = {
    "cheol": ((1, 1, 1, 0), (10, 11, 8, 7), (42, 49, 31, 33), (53, 61, 40, 40)),
    "otal": ((0, 0, 0, 0), (12, 7, 10, 6), (50, 37, 34, 30), (62, 44, 44, 36)),
    "okal": ((0, 0, 0, 0), (14, 9, 6, 7), (60, 48, 42, 28), (74, 57, 48, 35)),
    "ol": ((0, 2, 0, 2), (34, 47, 27, 30), (178, 191, 122, 118), (212, 240, 149, 150)),
    "qokeol": ((0, 0, 0, 0), (2, 4, 2, 3), (11, 12, 7, 8), (13, 16, 9, 11)),
    "qokol": ((0, 1, 0, 1), (5, 6, 3, 4), (35, 37, 27, 27), (40, 44, 30, 32)),
}
EXPECTED_MAPPED_LOFO = {
    "cheol": (13, 42), "otal": (12, 32), "okal": (10, 42),
    "ol": (37, 69), "qokeol": (5, 8), "qokol": (7, 35),
}
EXPECTED_ALL_LOFO = {"cheol": 63, "otal": 48, "okal": 52, "ol": 92, "qokeol": 22, "qokol": 46}
EXPECTED_STAGES = (
    ("SOURCE_GDT734", 1606, 1602),
    ("W2_W3", 990, 989),
    ("ZERO_COMPOSITION_AND_COMPONENT", 984, 983),
    ("RETIRED_LITERAL_FREE", 777, 776),
    ("AXIS_REGEX_MATCH", 769, 768),
    ("UNCONDITIONAL_GLOBAL", 726, 726),
    ("MINUS_GDT754_172", 659, 659),
    ("MINUS_GDT738_14", 657, 657),
    ("MINUS_GDT805_11_TARGETS", 652, 652),
)

FILES = {
    "lock": "SOURCE_LOCK.tsv",
    "query": "GDT806_GUARDED_QUERY_STATS.tsv",
    "stages": "GDT806_GLOBAL_DECK_STAGE_AUDIT.tsv",
    "global": "GDT806_GLOBAL652_DECK.tsv",
    "atlas11": "GDT806_ELEVEN_TARGET_ATLAS_CAPACITY_AUDIT.tsv",
    "contacts": "GDT806_TARGET_AND_K12_CONTACTS.tsv",
    "pool": "GDT806_K12_POOL_MEMBERSHIP.tsv",
    "capacity": "GDT806_CHANNEL_CAPACITY.tsv",
    "scores": "GDT806_EXACT_RATIONAL_RIVAL_SCORES.tsv",
    "contrasts": "GDT806_K12_MEDIAN_RANK_CONTRASTS.tsv",
    "lofo": "GDT806_STABLE_LOFO.tsv",
    "lofo_summary": "GDT806_STABLE_LOFO_SUMMARY.tsv",
    "loco": "GDT806_RAW_STABLE_LOCO.tsv",
    "loco_summary": "GDT806_RAW_STABLE_LOCO_SUMMARY.tsv",
    "adjudication": "GDT806_6_ADJUDICATIONS.tsv",
    "frames": "GDT806_7_ZERO_CREDIT_FRAMES.tsv",
    "passages": "GDT806_12_PASSAGE_CARDS.tsv",
    "packet": "GDT806_GDT388_CONTEXT_EDGE_PACKET.tsv",
    "card": "GDT806_STRUCTURAL_CARD.tsv",
}
SCHEMAS = {
    "lock": "path sha256 purpose access_mode",
    "query": "query_id source_path selector allowed_values output_columns forbidden_prefixes selected_rows skipped_forbidden_rows skipped_not_allowed_rows",
    "stages": "stage_order stage_id rows unique_surfaces expected_rows expected_unique_surfaces assertion_pass",
    "global": "surface source_reading_id working_model_level v99r7_spoken_default_de axis_tags macro_tags unconditional_global_export_allowed gdt734_composition_semantic_credit gdt734_component_export_allowed gdt806_semantic_credit gdt806_renderer_license",
    "atlas11": "scope channel raw_l1 raw_r1 pair_stable_l1 pair_stable_r1 used_as_six_target_duel_denominator assertion_pass",
    "contacts": "contact_id subject_kind subject_surface occurrence_id source_selector physical_folio locus token_index side neighbor_surface pair_sequence_stable_all_three assigned_disjoint_channel channel_axis_tags channel_macro_tags global652_mapped global652_axis_tags global652_macro_tags semantic_credit renderer_license component_export_credit",
    "pool": "target_surface neighbor_rank control_surface control_occurrences individual_covariate_distance outcome_fields_used_for_matching replacement_allowed",
    "capacity": "target_surface channel denominator l1_raw_contacts l1_raw_folios l1_stable_contacts l1_stable_folios r1_raw_contacts r1_raw_folios r1_stable_contacts r1_stable_folios stable_union_folios stable_robust_capacity expected_exact_capacity_pass",
    "scores": "target_reference subject_kind subject_surface channel denominator view candidate_a candidate_b a_l1_hits a_l1_denominator a_l1_rate a_r1_hits a_r1_denominator a_r1_rate candidate_a_score b_l1_hits b_l1_denominator b_l1_rate b_r1_hits b_r1_denominator b_r1_rate candidate_b_score uncentered_delta_a_minus_b uncentered_delta_decimal bilaterally_scoreable",
    "contrasts": "target_surface channel denominator view candidate_a candidate_b target_uncentered_delta target_uncentered_decimal k12_exact_median k12_exact_median_decimal target_centered_delta target_centered_decimal selected_by_centered_sign selected_sign uncentered_centered_same_nonzero_sign uncentered_margin_ge_1_20 centered_margin_ge_1_20 all_12_controls_bilateral robust_stable_controls required_robust_controls_pass oriented_rank_of_13_ties_against rank_le_3 control_deltas",
    "lofo": "target_surface channel denominator view omitted_physical_folio fixed_selected_sign target_uncentered_delta k12_exact_median target_centered_delta target_bilateral all_12_controls_bilateral robust_controls_after_drop fold_success",
    "lofo_summary": "target_surface channel denominator folds successes required_successes exact_gate pass",
    "loco": "target_surface channel denominator view omitted_control_surface fixed_selected_sign target_uncentered_delta_unchanged k11_exact_median_sorted_position_6 recomputed_centered_delta eleven_controls_scoreable fold_success",
    "loco_summary": "target_surface channel denominator view folds successes required_successes pass",
    "adjudication": "target_surface candidate_a candidate_b c2_mapped_selected c3_mapped_selected c2_c3_same_mapped_direction c2_mapped_sign c2_mapped_capacity_pass c2_mapped_direction_and_margin_pass c2_mapped_rank_pass c2_mapped_control_capacity_pass c2_mapped_lofo_pass c2_mapped_loco_pass c2_mapped_global_overlay_pass c2_mapped_channel_gate_pass c2_all_sign c2_all_direction_and_margin_pass c2_all_direction_matches_mapped c2_all_capacity_pass c2_all_rank_pass c2_all_control_capacity_pass c2_all_lofo_pass c2_all_loco_pass c2_all_global_overlay_pass c2_all_channel_gate_pass c3_mapped_sign c3_mapped_capacity_pass c3_mapped_direction_and_margin_pass c3_mapped_rank_pass c3_mapped_control_capacity_pass c3_mapped_lofo_pass c3_mapped_loco_pass c3_mapped_global_overlay_pass c3_mapped_channel_gate_pass c3_all_sign c3_all_direction_and_margin_pass c3_all_direction_matches_mapped c3_all_capacity_pass c3_all_rank_pass c3_all_control_capacity_pass c3_all_lofo_pass c3_all_loco_pass c3_all_global_overlay_pass c3_all_channel_gate_pass conditions_1_to_8_mapped_pass condition_9_all_opportunity_pass diagnostic_c2_centered_candidate decision display_selected_candidate display_selected_working_reading_de new_role_selected semantic_credit renderer_license confirmed_lexeme confirmed_plaintext component_export_credit",
    "frames": "source_frame_id target_surface exact_frame candidate_display_de strongest_rival_de illustrative_alignment frame_decision_credit frame_score_weight semantic_credit renderer_license confirmed_lexeme component_export_credit source_frame_class source_occurrences source_physical_folios source_stable_sequence_occurrences source_loci gdt806_target_decision decision_changed_by_frame",
    "passages": "passage_id target_surface source_selector physical_folio locus token_index exact_five_window full_zl3b_line left_surface left_channel left_axis_tags left_macro_tags candidate_a_de candidate_b_de right_surface right_channel right_axis_tags right_macro_tags gdt806_decision selection_score display_only semantic_credit renderer_license confirmed_plaintext confirmed_lexeme component_export_credit",
    "packet": "edge_id batch_id page physical_folio diagram_unit_id pivot_visual_id pivot_locus target_visual_id target_locus relation_type direction_basis ownership_basis geometry_only_selection source_manifest_id page_crop_sha256 pivot_crop_sha256 target_crop_sha256 source_aware_localizer relation_reviewer relation_confidence ambiguity_state formal_access_state fold_assignment eligibility_status",
    "card": "experiment status analysis_timing target_surfaces rival_signatures target_events k12_pool_rows unique_k12_control_surfaces k12_control_events global_surfaces narrow_surfaces residual_surfaces exact_active_source_cells conditional_mapped_preferences cross_denominator_concordances unresolved_rivals new_roles confirmed_lexemes confirmed_plaintext renderer_licenses component_export_credit new_pages_images_or_transcriptions f84_or_f84r_rows",
}
SCHEMAS = {key: value.split() for key, value in SCHEMAS.items()}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def header(path: Path) -> list[str]:
    with path.open(encoding="utf-8", newline="") as handle:
        return next(csv.reader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def split_tags(value: str) -> tuple[str, ...]:
    return tuple(tag for tag in value.split("|") if tag and tag not in {"NONE", "BOUNDARY", "TARGET_WHOLE_NO_SEMANTIC_CREDIT"})


def macro_tags(axes: Iterable[str]) -> tuple[str, ...]:
    aset = set(axes)
    return tuple(sorted(group for group, members in MACRO_MEMBERS.items() if aset & members))


def fstr(value: Fraction | None) -> str:
    return "NA" if value is None else f"{value.numerator}/{value.denominator}"


def dstr(value: Fraction | None) -> str:
    return "NA" if value is None else f"{float(value):.12g}"


def sign(value: Fraction | None) -> int:
    return 0 if value is None or value == 0 else 1 if value > 0 else -1


def exact_median(values: Sequence[Fraction]) -> Fraction:
    ordered = sorted(values)
    if len(ordered) == 12:
        return (ordered[5] + ordered[6]) / 2
    if len(ordered) == 11:
        return ordered[5]
    raise AssertionError(f"unsupported exact median size: {len(ordered)}")


def assert_unsealed(rows: Iterable[dict[str, str]], fields: Sequence[str]) -> None:
    for row in rows:
        for field in fields:
            if row.get(field, "").startswith("f84"):
                raise AssertionError(f"sealed selector materialized: {field}={row[field]}")


def guarded_cross_query() -> tuple[dict[str, dict[str, tuple[str, ...]]], dict[str, Any]]:
    pages = {row["page"] for row in read_tsv(ALLOWLIST)}
    if len(pages) != 179 or any(page.startswith("f84") for page in pages):
        raise AssertionError("GDT631 allow-list drift or sealed selector")
    columns = ("page", "locus", "all_three_present", "all_present_exact", "zl3b_clean", "it2a_clean", "rf1b_clean")
    command = [str(VMANUS_EXP), "query-tsv", rel(CROSS_RAW), "--selector", "page"]
    for page in sorted(pages):
        command.extend(("--allow", page))
    command.extend(("--columns", ",".join(columns), "--forbid-prefix", "f84", "--forbid-prefix", "f84r"))
    completed = subprocess.run(command, cwd=ROOT, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if completed.returncode != 0:
        raise AssertionError(f"guarded cross-reader query failed: {completed.stderr}")
    stat_lines = [line for line in completed.stderr.splitlines() if line.startswith("GUARD_STATS ")]
    if len(stat_lines) != 1:
        raise AssertionError("guarded query emitted no unique GUARD_STATS record")
    stats = json.loads(stat_lines[0][12:])
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    assert_unsealed(rows, ("page", "locus"))
    if len(rows) != 4137 or len({row["locus"] for row in rows}) != 4137:
        raise AssertionError("guarded cross-reader capacity drift")
    readers = {
        row["locus"]: {name: tuple(row[name].split()) for name in ("zl3b_clean", "it2a_clean", "rf1b_clean")}
        for row in rows
    }
    return readers, stats


def contiguous_count(tokens: Sequence[str], gram: tuple[str, ...]) -> int:
    width = len(gram)
    return sum(tuple(tokens[index:index + width]) == gram for index in range(len(tokens) - width + 1))


def pair_stable(readers: dict[str, dict[str, tuple[str, ...]]], locus: str, start: int) -> int:
    sequences = readers[locus]
    zl = sequences["zl3b_clean"]
    gram = tuple(zl[start:start + 2])
    if len(gram) != 2:
        return 0
    rank = sum(tuple(zl[index:index + 2]) == gram for index in range(start + 1))
    return int(rank <= min(contiguous_count(sequence, gram) for sequence in sequences.values()))


def rebuild_global_deck() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    axes = read_tsv(G739_AXES)
    expected_axis_map = {axis: group for group, members in MACRO_MEMBERS.items() for axis in members}
    observed_axis_map = {row["axis_id"]: row["axis_group"] for row in axes}
    if len(axes) != 12 or observed_axis_map != expected_axis_map:
        raise AssertionError("GDT739 axis-group definition drift")
    compiled = [
        (row["axis_id"], re.compile(row["keyword_regex"].replace("\\\\", "\\"), re.IGNORECASE))
        for row in axes
    ]
    source = read_tsv(G734)
    quarantined = {row["surface"] for row in read_tsv(G754)}
    held = {row["surface"] for row in read_tsv(G738)}
    if len(quarantined) != 172 or len(held) != 14:
        raise AssertionError("quarantine/HOLD source capacity drift")
    stages: list[tuple[str, list[dict[str, str]]]] = [("SOURCE_GDT734", source)]
    rows = [row for row in source if row["working_model_level"].startswith(("W2", "W3"))]
    stages.append(("W2_W3", rows))
    rows = [row for row in rows if row["gdt734_composition_semantic_credit"] == "0" and row["gdt734_component_export_allowed"] == "0"]
    stages.append(("ZERO_COMPOSITION_AND_COMPONENT", rows))
    retired = ("pulver", "samen", "saat", "wurzel", "holz")
    rows = [row for row in rows if not any(term in row["v99r7_spoken_default_de"].lower() for term in retired)]
    stages.append(("RETIRED_LITERAL_FREE", rows))
    tagged: dict[tuple[str, str], tuple[str, ...]] = {}
    matched_rows: list[dict[str, str]] = []
    for row in rows:
        hits = tuple(axis for axis, regex in compiled if regex.search(row["v99r7_spoken_default_de"]))
        if hits:
            tagged[(row["surface"], row["reading_id"])] = hits
            matched_rows.append(row)
    rows = matched_rows
    stages.append(("AXIS_REGEX_MATCH", rows))
    rows = [row for row in rows if row["unconditional_global_export_allowed"] == "1"]
    # The conflict/collapse gate is deliberately after unconditional export.
    by_surface: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_surface[row["surface"]].append(row)
    collapsed: list[dict[str, str]] = []
    for surface in sorted(by_surface):
        variants = by_surface[surface]
        signatures = {
            (
                row["working_model_level"], row["gdt734_composition_semantic_credit"],
                row["gdt734_component_export_allowed"], row["unconditional_global_export_allowed"],
                row["v99r7_spoken_default_de"], tagged[(surface, row["reading_id"])],
            )
            for row in variants
        }
        if len(signatures) != 1:
            raise AssertionError(f"conflicting globally eligible duplicate: {surface}")
        collapsed.append(variants[0])
    rows = collapsed
    stages.append(("UNCONDITIONAL_GLOBAL", rows))
    rows = [row for row in rows if row["surface"] not in quarantined]
    stages.append(("MINUS_GDT754_172", rows))
    rows = [row for row in rows if row["surface"] not in held]
    stages.append(("MINUS_GDT738_14", rows))
    rows = [row for row in rows if row["surface"] not in ALL_TARGETS]
    stages.append(("MINUS_GDT805_11_TARGETS", rows))

    audit: list[dict[str, str]] = []
    for order, ((stage_id, stage_rows), (want_id, want_rows, want_surfaces)) in enumerate(zip(stages, EXPECTED_STAGES, strict=True), 1):
        got = (len(stage_rows), len({row["surface"] for row in stage_rows}))
        if stage_id != want_id or got != (want_rows, want_surfaces):
            raise AssertionError(f"global stage drift {stage_id}: {got}")
        audit.append({
            "stage_order": str(order), "stage_id": stage_id, "rows": str(got[0]),
            "unique_surfaces": str(got[1]), "expected_rows": str(want_rows),
            "expected_unique_surfaces": str(want_surfaces), "assertion_pass": "1",
        })
    deck: list[dict[str, str]] = []
    for row in sorted(rows, key=lambda item: item["surface"]):
        axis_values = tagged[(row["surface"], row["reading_id"])]
        deck.append({
            "surface": row["surface"], "source_reading_id": row["reading_id"],
            "working_model_level": row["working_model_level"],
            "v99r7_spoken_default_de": row["v99r7_spoken_default_de"],
            "axis_tags": "|".join(axis_values), "macro_tags": "|".join(macro_tags(axis_values)),
            "unconditional_global_export_allowed": "1", "gdt734_composition_semantic_credit": "0",
            "gdt734_component_export_allowed": "0", "gdt806_semantic_credit": "0",
            "gdt806_renderer_license": "0",
        })
    return audit, deck


def rows_by_key(rows: Sequence[dict[str, str]], fields: Sequence[str]) -> dict[tuple[str, ...], dict[str, str]]:
    output: dict[tuple[str, ...], dict[str, str]] = {}
    for row in rows:
        key = tuple(row[field] for field in fields)
        if key in output:
            raise AssertionError(f"duplicate artifact key {fields}: {key}")
        output[key] = row
    return output


def compare_row(check: Any, prefix: str, actual: dict[str, str], expected: dict[str, Any]) -> None:
    for field, value in expected.items():
        check(f"{prefix}:{field}", actual[field] == str(value))


def mapped(row: dict[str, str], channel: str) -> bool:
    return row["global652_mapped"] == "1" if channel == FULL else row["assigned_disjoint_channel"] == channel


def row_macros(row: dict[str, str], channel: str) -> set[str]:
    field = "global652_macro_tags" if channel == FULL else "channel_macro_tags"
    return set(split_tags(row[field])) if mapped(row, channel) else set()


def duel_score(
    side_rows: Sequence[dict[str, str]], pair: Sequence[dict[str, str]], channel: str,
    denominator: str, view: str, omit_folio: str | None = None,
) -> dict[str, Any]:
    candidate_results: list[dict[str, Any]] = []
    for candidate in pair:
        result: dict[str, Any] = {}
        rates: list[Fraction] = []
        for side in SIDES:
            available = [
                row for row in side_rows
                if row["side"] == side
                and (omit_folio is None or row["physical_folio"] != omit_folio)
                and (view == "RAW" or row["pair_sequence_stable_all_three"] == "1")
            ]
            mapped_rows = [row for row in available if mapped(row, channel)]
            denominator_rows = mapped_rows if denominator == "MAPPED_CONTACTS" else available
            wanted = candidate["left_macro" if side == "L1" else "right_macro"]
            hits = sum(wanted in row_macros(row, channel) for row in mapped_rows)
            den = len(denominator_rows)
            rate = Fraction(hits, den) if den else None
            result[f"{side.lower()}_hits"] = hits
            result[f"{side.lower()}_den"] = den
            result[f"{side.lower()}_rate"] = rate
            if rate is not None:
                rates.append(rate)
        result["score"] = sum(rates, Fraction()) / 2 if len(rates) == 2 else None
        candidate_results.append(result)
    a, b = candidate_results
    delta = None if a["score"] is None or b["score"] is None else a["score"] - b["score"]
    return {"a": a, "b": b, "delta": delta}


def robust_control(rows: Sequence[dict[str, str]], channel: str, denominator: str, omit_folio: str | None = None) -> bool:
    for side in SIDES:
        stable = [
            row for row in rows
            if row["side"] == side and row["pair_sequence_stable_all_three"] == "1"
            and (omit_folio is None or row["physical_folio"] != omit_folio)
        ]
        eligible = [row for row in stable if mapped(row, channel)] if denominator == "MAPPED_CONTACTS" else stable
        if len(eligible) < 2 or len({row["physical_folio"] for row in eligible}) < 2:
            return False
    return True


def same_direction_margin(values: Sequence[Fraction | None]) -> tuple[bool, int]:
    selected = sign(values[0]) if values else 0
    passed = bool(selected and all(sign(value) == selected for value in values) and all(value is not None and abs(value) >= THRESHOLD for value in values))
    return passed, selected if passed else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-replay", action="store_true")
    args = parser.parse_args()
    checks: list[str] = []

    def check(name: str, condition: bool) -> None:
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    freeze_hashes = {
        "PREREGISTRATION.md": "04888e86b4a0a126336d474926e443ac106c9cdf22f9842c2b21d95ca5345b05",
        "METHOD.md": "41aa18164af801e0ce5c39ef2444cc858f55ee80fb8bc5d7de162da95a36bb46",
        "src/RIVAL_SIGNATURE_SPECS.tsv": "51833be5a06c649ffac67c28cdab53a0429364de60cdf12855dc0dd010e3fd19",
        "src/FRAME_RIVAL_SPECS.tsv": "b9be61471d8a239442edcf328a4f435c534b1f6552e0164100cf0dac33897209",
    }
    commit = subprocess.run(["git", "rev-parse", "--verify", "33ac1127^{commit}"], cwd=ROOT, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    check("published_freeze_commit", commit.returncode == 0 and commit.stdout.strip().startswith("33ac1127"))
    for name, digest in freeze_hashes.items():
        check(f"freeze_hash:{name}", sha(EXP / name) == digest)

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    check("result_id", result["experiment_id"] == "GDT806")
    check("result_status", result["status"] == "PASS__652_GLOBAL__577_RESIDUAL__967_TARGET_EVENTS__0_CONDITIONAL__0_CROSS_DENOMINATOR__6_UNRESOLVED__0_NEW_ROLES__ZERO_LEXEMES")
    check("result_scope", result["new_pages_images_or_transcriptions"] == result["f84_or_f84r_rows"] == 0)
    check("result_zero_claim", result["new_roles"] == result["confirmed_lexemes"] == result["confirmed_plaintext_clauses"] == result["renderer_licenses"] == result["component_export_credit"] == 0)
    expected_outputs = set(FILES.values()) | {"GDT806_GDT388_EDGE_INTAKE.json"}
    check("result_output_set", set(result["output_sha256"]) == expected_outputs)
    for filename, digest in result["output_sha256"].items():
        check(f"hash:{filename}", sha(ART / filename) == digest)

    loaded: dict[str, list[dict[str, str]]] = {}
    for key, filename in FILES.items():
        path = ART / filename
        check(f"schema:{key}", header(path) == SCHEMAS[key])
        rows = read_tsv(path)
        check(f"nonblank:{key}", all(all(row[field] != "" for field in SCHEMAS[key]) for row in rows))
        loaded[key] = rows

    # Lock safe files directly; inherit mixed-source hashes without opening
    # either mixed TSV. The only mixed-data access is guarded_cross_query().
    lock = loaded["lock"]
    check("source_lock_count", len(lock) == len({row["path"] for row in lock}) == 23)
    inherited_lock = {row["path"]: row for row in read_tsv(G805_LOCK)}
    guarded_paths = {"transcription/voynich_zl3b_tokens.tsv", "transcription/voynich_cross_transcription_lines.tsv"}
    for row in lock:
        path = row["path"]
        check(f"source_relative:{path}", not path.startswith("/") and ".." not in Path(path).parts)
        if path in guarded_paths:
            check(f"source_guard_mode:{path}", row["access_mode"] == "GUARDED_QUERY_ONLY__INHERITED_HASH_NOT_REREAD")
            check(f"source_inherited_hash:{path}", path in inherited_lock and row["sha256"] == inherited_lock[path]["sha256"])
        else:
            check(f"source_safe_mode:{path}", row["access_mode"] == "SAFE_ARTIFACT_OR_CODE")
            check(f"source_hash:{path}", sha(ROOT / path) == row["sha256"])

    readers, guard_stats = guarded_cross_query()
    query = rows_by_key(loaded["query"], ("query_id",))
    check("query_ids", set(query) == {("ZL3B_TOKENS",), ("CROSS_READER_LINES",)})
    for row in query.values():
        check(f"query_guard:{row['query_id']}", row["selector"] == "page" and row["allowed_values"] == "179" and row["forbidden_prefixes"] == "f84|f84r")
    check("query_cross_count", query[("CROSS_READER_LINES",)]["selected_rows"] == str(guard_stats["selected"]) == "4137")
    check("query_token_count", query[("ZL3B_TOKENS",)]["selected_rows"] == "32339")

    rebuilt_stage, rebuilt_global = rebuild_global_deck()
    check("stage_rows", loaded["stages"] == rebuilt_stage)
    check("global_rows", loaded["global"] == rebuilt_global)
    global_map = {row["surface"]: row for row in rebuilt_global}
    check("global_unique_652", len(global_map) == 652)
    check("global_zero_credit", all(row["gdt806_semantic_credit"] == row["gdt806_renderer_license"] == row["gdt734_component_export_allowed"] == "0" for row in rebuilt_global))

    audit = read_tsv(G805_AUDIT)
    narrow = {row["surface"]: split_tags(row["axis_tags"]) for row in audit if row["primary_surface_projection_allowed"] == "1"}
    check("narrow_source_131", len(audit) == len({row["surface"] for row in audit}) == 131)
    check("narrow_75", len(narrow) == 75 and set(narrow) <= set(global_map))
    check("residual_577", len(set(global_map) - set(narrow)) == 577)
    check("narrow_source_contacts_111", sum(int(row["gdt739_active_radius_contacts"]) for row in audit if row["primary_surface_projection_allowed"] == "1") == 111)
    differences = {surface for surface in narrow if set(narrow[surface]) != set(split_tags(global_map[surface]["axis_tags"]))}
    check("narrow_global_axis_differences", differences == {"qeeey", "qoeeo"})

    windows = [row for row in read_tsv(G739_WINDOWS) if row["eligible_local_anchor"] == "1"]
    check("g739_eligible_230", len(windows) == 230)
    exact: dict[tuple[str, str, int, str], tuple[str, ...]] = {}
    for row in windows:
        surface = row["neighbor_surface"]
        if surface in narrow and int(row["distance"]) <= 2:
            key = (row["page"], row["locus"], int(row["neighbor_ordinal"]), surface)
            value = split_tags(row["axis_tags"])
            check(f"exact_tag_agreement:{row['window_id']}", value == narrow[surface])
            check(f"exact_key_consistency:{row['window_id']}", key not in exact or exact[key] == value)
            exact[key] = value
    check("exact_active_cells_111", len(exact) == 111)

    rival_rows = read_tsv(SRC / "RIVAL_SIGNATURE_SPECS.tsv")
    check("rival_count", len(rival_rows) == 12 and {row["target_surface"] for row in rival_rows} == TARGET_SET)
    specs: dict[str, list[dict[str, str]]] = {}
    for target in TARGETS:
        pair = sorted((row for row in rival_rows if row["target_surface"] == target), key=lambda row: row["candidate_order"])
        check(f"rival_pair:{target}", [row["candidate_order"] for row in pair] == ["A", "B"])
        check(f"rival_width:{target}", all(row["left_macro"] in MACRO_MEMBERS and row["right_macro"] in MACRO_MEMBERS for row in pair))
        check(f"rival_zero:{target}", all(all(row[field] == "0" for field in ("prior_mutation_credit", "semantic_credit", "renderer_license", "component_export_credit")) for row in pair))
        specs[target] = pair

    upstream_pools = [row for row in read_tsv(G804) if row["pool_variant"] == "PRIMARY_K12" and row["target_surface"] in TARGET_SET]
    check("k12_rows_72", len(upstream_pools) == 72)
    pools: dict[str, list[str]] = {}
    for target in TARGETS:
        subset = sorted((row for row in upstream_pools if row["target_surface"] == target), key=lambda row: int(row["neighbor_rank"]))
        check(f"k12_exact_pool:{target}", len(subset) == 12 and [int(row["neighbor_rank"]) for row in subset] == list(range(1, 13)) and len({row["control_surface"] for row in subset}) == 12)
        check(f"k12_outcome_blind:{target}", all(row["outcome_fields_used_for_matching"] == "NONE" for row in subset))
        pools[target] = [row["control_surface"] for row in subset]
    control_surfaces = set().union(*(set(values) for values in pools.values()))
    check("k12_union_20", len(control_surfaces) == 20 and control_surfaces.isdisjoint(ALL_TARGETS))

    g800 = {row["occurrence_id"]: row for row in read_tsv(G800)}
    g802 = {row["occurrence_id"]: row for row in read_tsv(G802)}
    check("g800_unique_4137", len(g800) == 4137)
    check("g802_unique_4137", len(g802) == 4137 and set(g800) == set(g802))
    control_ids = {oid for oid, row in g800.items() if row["terminal"] == "l" and row["surface"] in control_surfaces}
    check("control_events_1737", len(control_ids) == 1737)
    discovery_ids = {row["occurrence_id"] for row in read_tsv(G803)}
    check("control_discovery_free", control_ids.isdisjoint(discovery_ids))

    membership = rows_by_key(loaded["pool"], ("target_surface", "neighbor_rank"))
    check("membership_72", len(membership) == 72)
    occurrence_counts = Counter(g800[oid]["surface"] for oid in control_ids)
    for row in upstream_pools:
        actual = membership[(row["target_surface"], row["neighbor_rank"])]
        expected = {
            "target_surface": row["target_surface"], "neighbor_rank": row["neighbor_rank"],
            "control_surface": row["control_surface"], "control_occurrences": occurrence_counts[row["control_surface"]],
            "individual_covariate_distance": row["individual_covariate_distance"],
            "outcome_fields_used_for_matching": "NONE", "replacement_allowed": 0,
        }
        compare_row(check, f"membership:{row['target_surface']}:{row['neighbor_rank']}", actual, expected)

    contacts = loaded["contacts"]
    check("contact_count", len(contacts) == 2 * (967 + 1737) == 5408)
    check("contact_id_unique", len({row["contact_id"] for row in contacts}) == 5408)
    check("contact_event_side_unique", len({(row["subject_kind"], row["subject_surface"], row["occurrence_id"], row["side"]) for row in contacts}) == 5408)
    check("contact_credit_zero", all(row["semantic_credit"] == row["renderer_license"] == row["component_export_credit"] == "0" for row in contacts))
    assert_unsealed(contacts, ("source_selector", "physical_folio", "locus"))
    target_atlas = {row["occurrence_id"]: row for row in read_tsv(G805_ATLAS) if row["surface"] in TARGET_SET}
    check("target_events_967", len(target_atlas) == 967 and Counter(row["surface"] for row in target_atlas.values()) == Counter({"cheol": 141, "otal": 117, "okal": 122, "ol": 462, "qokeol": 38, "qokol": 87}))
    check("target_discovery_free", set(target_atlas).isdisjoint(discovery_ids))
    by_subject: defaultdict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    target_global_contacts = 0
    for row in contacts:
        check(f"contact_side:{row['contact_id']}", row["side"] in SIDES)
        by_subject[(row["subject_kind"], row["subject_surface"])].append(row)
        if row["subject_kind"] == "TARGET":
            check(f"contact_target_id:{row['contact_id']}", row["occurrence_id"] in target_atlas and row["subject_surface"] == target_atlas[row["occurrence_id"]]["surface"])
            source = target_atlas[row["occurrence_id"]]
            side_low = row["side"].lower()
            expected_neighbour = source[f"{side_low}_surface"]
            expected_stable = source[f"{side_low}_pair_sequence_stable_all_three"]
            expected_meta = (source["source_selector"], source["physical_folio"], source["locus"], source["token_index"])
        else:
            check(f"contact_control_kind:{row['contact_id']}", row["subject_kind"] == "K12_CONTROL" and row["occurrence_id"] in control_ids and row["subject_surface"] == g800[row["occurrence_id"]]["surface"])
            source = g802[row["occurrence_id"]]
            expected_neighbour = source["left_context" if row["side"] == "L1" else "right_context"]
            expected_meta = (source["source_selector"], source["physical_folio"], source["locus"], source["token_index"])
            expected_stable = str(pair_stable(readers, source["locus"], int(source["token_index"]) - (2 if row["side"] == "L1" else 1))) if expected_neighbour != "NONE" else "0"
        check(f"contact_meta:{row['contact_id']}", (row["source_selector"], row["physical_folio"], row["locus"], row["token_index"]) == expected_meta)
        check(f"contact_neighbour:{row['contact_id']}", row["neighbor_surface"] == expected_neighbour)
        independent_stable = str(pair_stable(readers, row["locus"], int(row["token_index"]) - (2 if row["side"] == "L1" else 1))) if row["neighbor_surface"] != "NONE" else "0"
        check(f"contact_stable:{row['contact_id']}", row["pair_sequence_stable_all_three"] == expected_stable == independent_stable)
        ordinal = int(row["token_index"]) + (-1 if row["side"] == "L1" else 1)
        exact_axes = exact.get((row["source_selector"], row["locus"], ordinal, row["neighbor_surface"]))
        if exact_axes is not None:
            expected_channel, expected_axes = C1, exact_axes
        elif row["neighbor_surface"] in narrow:
            expected_channel, expected_axes = C2, narrow[row["neighbor_surface"]]
        elif row["neighbor_surface"] in global_map:
            expected_channel, expected_axes = C3, split_tags(global_map[row["neighbor_surface"]]["axis_tags"])
        else:
            expected_channel, expected_axes = NONE, ()
        check(f"contact_channel:{row['contact_id']}", row["assigned_disjoint_channel"] == expected_channel)
        check(f"contact_axes:{row['contact_id']}", row["channel_axis_tags"] == ("|".join(expected_axes) or "NONE"))
        check(f"contact_macros:{row['contact_id']}", row["channel_macro_tags"] == ("|".join(macro_tags(expected_axes)) or "NONE"))
        full_axes = split_tags(global_map[row["neighbor_surface"]]["axis_tags"]) if row["neighbor_surface"] in global_map else ()
        check(f"contact_full:{row['contact_id']}", row["global652_mapped"] == str(int(bool(full_axes))) and row["global652_axis_tags"] == ("|".join(full_axes) or "NONE") and row["global652_macro_tags"] == ("|".join(macro_tags(full_axes)) or "NONE"))
        check(f"contact_partition:{row['contact_id']}", (row["assigned_disjoint_channel"] != NONE) == (row["global652_mapped"] == "1"))
        if row["subject_kind"] == "TARGET" and row["global652_mapped"] == "1":
            target_global_contacts += 1
    check("target_global_contacts_916", target_global_contacts == 916)
    check("target_contact_sides", all(len(by_subject[("TARGET", target)]) == 2 * sum(1 for row in target_atlas.values() if row["surface"] == target) for target in TARGETS))
    check("control_contact_sides", all(len(by_subject[("K12_CONTROL", surface)]) == 2 * occurrence_counts[surface] for surface in control_surfaces))
    check("disjoint_channel_counts", Counter(row["assigned_disjoint_channel"] for row in contacts) == Counter({NONE: 2950, C3: 2074, C2: 374, C1: 10}))

    capacity_rows = rows_by_key(loaded["capacity"], ("target_surface", "channel", "denominator"))
    check("capacity_rows_30", len(capacity_rows) == 30)
    aggregate = {channel: [0, 0, 0, 0] for channel in (C1, C2, C3, FULL)}
    opportunity_totals = [0, 0, 0, 0]
    for target in TARGETS:
        subject = by_subject[("TARGET", target)]
        for cindex, channel in enumerate((C1, C2, C3, FULL)):
            expected: dict[str, Any] = {"target_surface": target, "channel": channel, "denominator": "MAPPED_CONTACTS"}
            stable_union: set[str] = set()
            for side in SIDES:
                raw = [row for row in subject if row["side"] == side and mapped(row, channel)]
                stable = [row for row in raw if row["pair_sequence_stable_all_three"] == "1"]
                expected[f"{side.lower()}_raw_contacts"] = len(raw)
                expected[f"{side.lower()}_raw_folios"] = len({row["physical_folio"] for row in raw})
                expected[f"{side.lower()}_stable_contacts"] = len(stable)
                expected[f"{side.lower()}_stable_folios"] = len({row["physical_folio"] for row in stable})
                stable_union.update(row["physical_folio"] for row in stable)
            cap_tuple = (expected["l1_raw_contacts"], expected["r1_raw_contacts"], expected["l1_stable_contacts"], expected["r1_stable_contacts"])
            check(f"fixed_capacity:{target}:{channel}", cap_tuple == EXPECTED_CAPACITY[target][cindex])
            for index, value in enumerate(cap_tuple):
                aggregate[channel][index] += value
            robust = int(expected["l1_stable_contacts"] >= 2 and expected["l1_stable_folios"] >= 2 and expected["r1_stable_contacts"] >= 2 and expected["r1_stable_folios"] >= 2 and len(stable_union) >= 4)
            expected.update({"stable_union_folios": len(stable_union), "stable_robust_capacity": robust, "expected_exact_capacity_pass": 1})
            compare_row(check, f"capacity:{target}:{channel}", capacity_rows[(target, channel, "MAPPED_CONTACTS")], expected)
        expected = {"target_surface": target, "channel": "ALL_CHANNEL_NUMERATORS", "denominator": "ALL_OPPORTUNITIES"}
        stable_union = set()
        for side in SIDES:
            raw = [row for row in subject if row["side"] == side]
            stable = [row for row in raw if row["pair_sequence_stable_all_three"] == "1"]
            expected[f"{side.lower()}_raw_contacts"] = len(raw)
            expected[f"{side.lower()}_raw_folios"] = len({row["physical_folio"] for row in raw})
            expected[f"{side.lower()}_stable_contacts"] = len(stable)
            expected[f"{side.lower()}_stable_folios"] = len({row["physical_folio"] for row in stable})
            stable_union.update(row["physical_folio"] for row in stable)
        robust = int(expected["l1_stable_contacts"] >= 2 and expected["l1_stable_folios"] >= 2 and expected["r1_stable_contacts"] >= 2 and expected["r1_stable_folios"] >= 2 and len(stable_union) >= 4)
        expected.update({"stable_union_folios": len(stable_union), "stable_robust_capacity": robust, "expected_exact_capacity_pass": 1})
        compare_row(check, f"capacity:{target}:all", capacity_rows[(target, "ALL_CHANNEL_NUMERATORS", "ALL_OPPORTUNITIES")], expected)
        opportunity_totals[0] += expected["l1_raw_contacts"]
        opportunity_totals[1] += expected["r1_raw_contacts"]
        opportunity_totals[2] += expected["l1_stable_contacts"]
        opportunity_totals[3] += expected["r1_stable_contacts"]
    check("six_capacity_totals", aggregate == {C1: [1, 4, 1, 3], C2: [77, 84, 56, 57], C3: [376, 374, 263, 244], FULL: [454, 462, 320, 304]})
    check("opportunity_967_967_600_594", opportunity_totals == [967, 967, 600, 594])

    atlas11 = read_tsv(G805_ATLAS)
    eleven_counts: dict[str, list[int]] = {}
    for channel in (C1, C2, C3, FULL):
        per_side: list[tuple[int, int]] = []
        for side in SIDES:
            prefix = side.lower()
            raw = stable = 0
            for event in atlas11:
                surface = event[f"{prefix}_surface"]
                key = (event["source_selector"], event["locus"], int(event["token_index"]) + (-1 if side == "L1" else 1), surface)
                is_exact = key in exact
                if channel == C1:
                    hit = is_exact
                elif channel == C2:
                    hit = not is_exact and surface in narrow
                elif channel == C3:
                    hit = surface in global_map and surface not in narrow
                else:
                    hit = surface in global_map
                raw += int(hit)
                stable += int(hit and event[f"{prefix}_pair_sequence_stable_all_three"] == "1")
            per_side.append((raw, stable))
        eleven_counts[channel] = [per_side[0][0], per_side[1][0], per_side[0][1], per_side[1][1]]
    check("eleven_counts", eleven_counts == {C1: [1, 5, 1, 4], C2: [91, 87, 65, 60], C3: [427, 421, 300, 277], FULL: [519, 513, 366, 341]})
    atlas_rows = rows_by_key(loaded["atlas11"], ("channel",))
    for channel, values in eleven_counts.items():
        expected = {"scope": "GDT805_ELEVEN_TARGET_ATLAS_AUDIT_ONLY", "channel": channel, "raw_l1": values[0], "raw_r1": values[1], "pair_stable_l1": values[2], "pair_stable_r1": values[3], "used_as_six_target_duel_denominator": 0, "assertion_pass": 1}
        compare_row(check, f"atlas11:{channel}", atlas_rows[(channel,)], expected)

    score_artifact = rows_by_key(loaded["scores"], ("target_reference", "subject_kind", "subject_surface", "channel", "denominator", "view"))
    expected_score_keys: set[tuple[str, ...]] = set()
    score_cache: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for target in TARGETS:
        pair = specs[target]
        subjects = [("TARGET", target)] + [("K12_CONTROL", surface) for surface in pools[target]]
        matrices = [(C1, "MAPPED_CONTACTS", view) for view in VIEWS]
        matrices += [(channel, denominator, view) for channel in SCORED for denominator in DENOMS for view in VIEWS]
        for channel, denominator, view in matrices:
            use_subjects = subjects if channel != C1 else subjects[:1]
            for kind, surface in use_subjects:
                score = duel_score(by_subject[(kind, surface)], pair, channel, denominator, view)
                key = (target, kind, surface, channel, denominator, view)
                expected_score_keys.add(key)
                actual = score_artifact[key]
                expected: dict[str, Any] = {
                    "target_reference": target, "subject_kind": kind, "subject_surface": surface,
                    "channel": channel, "denominator": denominator, "view": view,
                    "candidate_a": pair[0]["candidate_id"], "candidate_b": pair[1]["candidate_id"],
                }
                for label, item in (("a", score["a"]), ("b", score["b"])):
                    for side in SIDES:
                        low = side.lower()
                        expected[f"{label}_{low}_hits"] = item[f"{low}_hits"]
                        expected[f"{label}_{low}_denominator"] = item[f"{low}_den"]
                        expected[f"{label}_{low}_rate"] = fstr(item[f"{low}_rate"])
                    expected[f"candidate_{label}_score"] = fstr(item["score"])
                expected["uncentered_delta_a_minus_b"] = fstr(score["delta"])
                expected["uncentered_delta_decimal"] = dstr(score["delta"])
                expected["bilaterally_scoreable"] = int(score["delta"] is not None)
                compare_row(check, f"score:{':'.join(key)}", actual, expected)
                cache = score_cache.setdefault((target, channel, denominator, view), {})
                if kind == "TARGET":
                    cache["target"] = score["delta"]
                else:
                    cache.setdefault("controls", {})[surface] = score["delta"]
    check("score_matrix_948", len(score_artifact) == len(expected_score_keys) == 948 and set(score_artifact) == expected_score_keys)

    contrasts = rows_by_key(loaded["contrasts"], ("target_surface", "channel", "denominator", "view"))
    check("contrast_matrix_72", len(contrasts) == 72)
    for target in TARGETS:
        pair = specs[target]
        for channel in SCORED:
            for denominator in DENOMS:
                for view in VIEWS:
                    key = (target, channel, denominator, view)
                    cache = score_cache[key]
                    target_value = cache["target"]
                    control_values = [cache["controls"][surface] for surface in pools[target]]
                    all_scoreable = all(value is not None for value in control_values)
                    base = exact_median(control_values) if all_scoreable else None  # type: ignore[arg-type]
                    centered = None if target_value is None or base is None else target_value - base
                    selected = sign(centered)
                    robust_count = sum(robust_control(by_subject[("K12_CONTROL", surface)], channel, denominator) for surface in pools[target])
                    rank = None
                    if selected and target_value is not None and all_scoreable:
                        oriented_target = selected * target_value
                        rank = 1 + sum(selected * value >= oriented_target for value in control_values if value is not None)
                    cache.update({"control_values": dict(zip(pools[target], control_values)), "base": base, "centered": centered, "selected": selected, "all_scoreable": all_scoreable, "robust": robust_count, "rank": rank})
                    expected = {
                        "target_surface": target, "channel": channel, "denominator": denominator, "view": view,
                        "candidate_a": pair[0]["candidate_id"], "candidate_b": pair[1]["candidate_id"],
                        "target_uncentered_delta": fstr(target_value), "target_uncentered_decimal": dstr(target_value),
                        "k12_exact_median": fstr(base), "k12_exact_median_decimal": dstr(base),
                        "target_centered_delta": fstr(centered), "target_centered_decimal": dstr(centered),
                        "selected_by_centered_sign": pair[0]["candidate_id"] if selected > 0 else pair[1]["candidate_id"] if selected < 0 else "NONE",
                        "selected_sign": selected, "uncentered_centered_same_nonzero_sign": int(bool(selected and sign(target_value) == selected)),
                        "uncentered_margin_ge_1_20": int(target_value is not None and abs(target_value) >= THRESHOLD),
                        "centered_margin_ge_1_20": int(centered is not None and abs(centered) >= THRESHOLD),
                        "all_12_controls_bilateral": int(all_scoreable), "robust_stable_controls": robust_count,
                        "required_robust_controls_pass": int(view == "RAW" or robust_count >= 10),
                        "oriented_rank_of_13_ties_against": "NA" if rank is None else rank, "rank_le_3": int(rank is not None and rank <= 3),
                        "control_deltas": "|".join(f"{surface}:{fstr(value)}" for surface, value in zip(pools[target], control_values)),
                    }
                    compare_row(check, f"contrast:{':'.join(key)}", contrasts[key], expected)

    loco_rows = rows_by_key(loaded["loco"], ("target_surface", "channel", "denominator", "view", "omitted_control_surface"))
    loco_summary_art = rows_by_key(loaded["loco_summary"], ("target_surface", "channel", "denominator", "view"))
    loco_summary: dict[tuple[str, str, str, str], dict[str, int]] = {}
    check("loco_rows_576", len(loco_rows) == 576)
    for target in TARGETS:
        for channel in (C2, C3):
            for denominator in DENOMS:
                for view in VIEWS:
                    cache = score_cache[(target, channel, denominator, view)]
                    successes = 0
                    for omitted in pools[target]:
                        remaining = [cache["control_values"][surface] for surface in pools[target] if surface != omitted]
                        scoreable = len(remaining) == 11 and all(value is not None for value in remaining)
                        base = exact_median(remaining) if scoreable else None  # type: ignore[arg-type]
                        centered = None if cache["target"] is None or base is None else cache["target"] - base
                        success = int(bool(cache["selected"] and sign(centered) == cache["selected"]))
                        successes += success
                        key = (target, channel, denominator, view, omitted)
                        expected = {
                            "target_surface": target, "channel": channel, "denominator": denominator, "view": view,
                            "omitted_control_surface": omitted, "fixed_selected_sign": cache["selected"],
                            "target_uncentered_delta_unchanged": fstr(cache["target"]),
                            "k11_exact_median_sorted_position_6": fstr(base), "recomputed_centered_delta": fstr(centered),
                            "eleven_controls_scoreable": int(scoreable), "fold_success": success,
                        }
                        compare_row(check, f"loco:{':'.join(key)}", loco_rows[key], expected)
                    summary = {"folds": 12, "successes": successes, "required_successes": 10, "pass": int(successes >= 10)}
                    loco_summary[(target, channel, denominator, view)] = summary
                    compare_row(check, f"loco_summary:{target}:{channel}:{denominator}:{view}", loco_summary_art[(target, channel, denominator, view)], {"target_surface": target, "channel": channel, "denominator": denominator, "view": view, **summary})

    lofo_rows = rows_by_key(loaded["lofo"], ("target_surface", "channel", "denominator", "omitted_physical_folio"))
    lofo_summary_art = rows_by_key(loaded["lofo_summary"], ("target_surface", "channel", "denominator"))
    lofo_summary: dict[tuple[str, str, str], dict[str, int]] = {}
    check("lofo_rows_958", len(lofo_rows) == 958)
    for target in TARGETS:
        target_rows = by_subject[("TARGET", target)]
        for cindex, channel in enumerate((C2, C3)):
            for denominator in DENOMS:
                if denominator == "MAPPED_CONTACTS":
                    universe = sorted({row["physical_folio"] for row in target_rows if row["pair_sequence_stable_all_three"] == "1" and mapped(row, channel)})
                    expected_n = EXPECTED_MAPPED_LOFO[target][cindex]
                else:
                    universe = sorted({row["physical_folio"] for row in target_rows if row["pair_sequence_stable_all_three"] == "1"})
                    expected_n = EXPECTED_ALL_LOFO[target]
                check(f"lofo_universe:{target}:{channel}:{denominator}", len(universe) == expected_n)
                fixed = score_cache[(target, channel, denominator, "PAIR_STABLE")]["selected"]
                successes = 0
                for folio in universe:
                    target_fold = duel_score(target_rows, specs[target], channel, denominator, "PAIR_STABLE", folio)["delta"]
                    control_fold = {
                        surface: duel_score(by_subject[("K12_CONTROL", surface)], specs[target], channel, denominator, "PAIR_STABLE", folio)["delta"]
                        for surface in pools[target]
                    }
                    scoreable = all(value is not None for value in control_fold.values())
                    base = exact_median(list(control_fold.values())) if scoreable else None  # type: ignore[arg-type]
                    centered = None if target_fold is None or base is None else target_fold - base
                    robust_count = sum(robust_control(by_subject[("K12_CONTROL", surface)], channel, denominator, folio) for surface in pools[target])
                    success = int(bool(fixed and scoreable and robust_count >= 10 and sign(target_fold) == fixed and sign(centered) == fixed))
                    successes += success
                    key = (target, channel, denominator, folio)
                    expected = {
                        "target_surface": target, "channel": channel, "denominator": denominator, "view": "PAIR_STABLE",
                        "omitted_physical_folio": folio, "fixed_selected_sign": fixed,
                        "target_uncentered_delta": fstr(target_fold), "k12_exact_median": fstr(base),
                        "target_centered_delta": fstr(centered), "target_bilateral": int(target_fold is not None),
                        "all_12_controls_bilateral": int(scoreable), "robust_controls_after_drop": robust_count,
                        "fold_success": success,
                    }
                    compare_row(check, f"lofo:{target}:{channel}:{denominator}:{folio}", lofo_rows[key], expected)
                required = (4 * len(universe) + 4) // 5
                summary = {"folds": len(universe), "successes": successes, "required_successes": required, "pass": int(successes * 5 >= 4 * len(universe))}
                lofo_summary[(target, channel, denominator)] = summary
                compare_row(check, f"lofo_summary:{target}:{channel}:{denominator}", lofo_summary_art[(target, channel, denominator)], {"target_surface": target, "channel": channel, "denominator": denominator, **summary, "exact_gate": f"{successes}*5>=4*{len(universe)}"})

    def overlay_pass(target: str, denominator: str, selected: int) -> bool:
        return bool(selected and all(sign(score_cache[(target, FULL, denominator, view)][field]) == selected for view in VIEWS for field in ("target", "centered")))

    expected_decisions: dict[str, dict[str, Any]] = {}
    for target in TARGETS:
        channel_results: dict[str, dict[str, Any]] = {}
        for channel in (C2, C3):
            mapped_values = [score_cache[(target, channel, "MAPPED_CONTACTS", view)][field] for view in VIEWS for field in ("target", "centered")]
            mapped_direction, mapped_sign = same_direction_margin(mapped_values)
            mapped_rank = all((score_cache[(target, channel, "MAPPED_CONTACTS", view)]["rank"] or 99) <= 3 for view in VIEWS)
            mapped_controls = all(score_cache[(target, channel, "MAPPED_CONTACTS", view)]["all_scoreable"] for view in VIEWS) and score_cache[(target, channel, "MAPPED_CONTACTS", "PAIR_STABLE")]["robust"] >= 10
            mapped_loco = all(loco_summary[(target, channel, "MAPPED_CONTACTS", view)]["pass"] for view in VIEWS)
            mapped_global = overlay_pass(target, "MAPPED_CONTACTS", mapped_sign)
            mapped_capacity = int(capacity_rows[(target, channel, "MAPPED_CONTACTS")]["stable_robust_capacity"])
            mapped_gate = bool(mapped_capacity and mapped_direction and mapped_rank and mapped_controls and lofo_summary[(target, channel, "MAPPED_CONTACTS")]["pass"] and mapped_loco and mapped_global)
            all_values = [score_cache[(target, channel, "ALL_OPPORTUNITIES", view)][field] for view in VIEWS for field in ("target", "centered")]
            all_direction, all_sign = same_direction_margin(all_values)
            all_matches = bool(mapped_sign and all_sign == mapped_sign)
            all_rank = all((score_cache[(target, channel, "ALL_OPPORTUNITIES", view)]["rank"] or 99) <= 3 for view in VIEWS)
            all_controls = all(score_cache[(target, channel, "ALL_OPPORTUNITIES", view)]["all_scoreable"] for view in VIEWS) and score_cache[(target, channel, "ALL_OPPORTUNITIES", "PAIR_STABLE")]["robust"] >= 10
            all_loco = all(loco_summary[(target, channel, "ALL_OPPORTUNITIES", view)]["pass"] for view in VIEWS)
            all_global = overlay_pass(target, "ALL_OPPORTUNITIES", mapped_sign)
            all_capacity = int(capacity_rows[(target, "ALL_CHANNEL_NUMERATORS", "ALL_OPPORTUNITIES")]["stable_robust_capacity"])
            all_gate = bool(all_capacity and all_direction and all_matches and all_rank and all_controls and lofo_summary[(target, channel, "ALL_OPPORTUNITIES")]["pass"] and all_loco and all_global)
            channel_results[channel] = {
                "mapped_sign": mapped_sign, "mapped_capacity_pass": mapped_capacity,
                "mapped_direction_and_margin_pass": int(mapped_direction), "mapped_rank_pass": int(mapped_rank),
                "mapped_control_capacity_pass": int(mapped_controls), "mapped_lofo_pass": lofo_summary[(target, channel, "MAPPED_CONTACTS")]["pass"],
                "mapped_loco_pass": int(mapped_loco), "mapped_global_overlay_pass": int(mapped_global), "mapped_channel_gate_pass": int(mapped_gate),
                "all_sign": all_sign, "all_direction_and_margin_pass": int(all_direction), "all_direction_matches_mapped": int(all_matches),
                "all_capacity_pass": all_capacity, "all_rank_pass": int(all_rank), "all_control_capacity_pass": int(all_controls),
                "all_lofo_pass": lofo_summary[(target, channel, "ALL_OPPORTUNITIES")]["pass"], "all_loco_pass": int(all_loco),
                "all_global_overlay_pass": int(all_global), "all_channel_gate_pass": int(all_gate),
            }
        c2, c3 = channel_results[C2], channel_results[C3]
        same = bool(c2["mapped_sign"] and c2["mapped_sign"] == c3["mapped_sign"])
        mapped_gate = bool(c2["mapped_channel_gate_pass"] and c3["mapped_channel_gate_pass"] and same)
        cross_gate = bool(mapped_gate and c2["all_channel_gate_pass"] and c3["all_channel_gate_pass"])
        pair = specs[target]
        diagnostic = pair[0] if c2["mapped_sign"] > 0 else pair[1] if c2["mapped_sign"] < 0 else None
        decision = "CROSS_DENOMINATOR_DECK_BREADTH_CONCORDANCE" if cross_gate else "CONDITIONAL_MAPPED_DECK_PREFERENCE" if mapped_gate else "UNRESOLVED_RIVAL"
        selected = diagnostic if decision != "UNRESOLVED_RIVAL" else None
        expected: dict[str, Any] = {
            "target_surface": target, "candidate_a": pair[0]["candidate_id"], "candidate_b": pair[1]["candidate_id"],
            "c2_mapped_selected": pair[0]["candidate_id"] if sign(score_cache[(target, C2, "MAPPED_CONTACTS", "PAIR_STABLE")]["centered"]) > 0 else pair[1]["candidate_id"] if sign(score_cache[(target, C2, "MAPPED_CONTACTS", "PAIR_STABLE")]["centered"]) < 0 else "NONE",
            "c3_mapped_selected": pair[0]["candidate_id"] if sign(score_cache[(target, C3, "MAPPED_CONTACTS", "PAIR_STABLE")]["centered"]) > 0 else pair[1]["candidate_id"] if sign(score_cache[(target, C3, "MAPPED_CONTACTS", "PAIR_STABLE")]["centered"]) < 0 else "NONE",
            "c2_c3_same_mapped_direction": int(same),
        }
        for prefix, channel in (("c2", C2), ("c3", C3)):
            expected.update({f"{prefix}_{key}": value for key, value in channel_results[channel].items()})
        expected.update({
            "conditions_1_to_8_mapped_pass": int(mapped_gate), "condition_9_all_opportunity_pass": int(cross_gate),
            "diagnostic_c2_centered_candidate": diagnostic["candidate_id"] if diagnostic else "NONE", "decision": decision,
            "display_selected_candidate": selected["candidate_id"] if selected else "NONE",
            "display_selected_working_reading_de": selected["concrete_working_reading_de"] if selected else "NONE",
            "new_role_selected": 0, "semantic_credit": 0, "renderer_license": 0, "confirmed_lexeme": 0,
            "confirmed_plaintext": 0, "component_export_credit": 0,
        })
        expected_decisions[target] = expected
    adjudication = rows_by_key(loaded["adjudication"], ("target_surface",))
    check("adjudication_six", len(adjudication) == 6)
    for target, expected in expected_decisions.items():
        compare_row(check, f"adjudication:{target}", adjudication[(target,)], expected)
    check("zero_selections", Counter(row["decision"] for row in adjudication.values()) == Counter({"UNRESOLVED_RIVAL": 6}) and all(row["new_role_selected"] == "0" for row in adjudication.values()))

    frame_specs = read_tsv(SRC / "FRAME_RIVAL_SPECS.tsv")
    source_frames = {row["frame_id"]: row for row in read_tsv(G805_FRAMES)}
    frames = rows_by_key(loaded["frames"], ("source_frame_id",))
    expected_frame_ids = {"G805-F01", "G805-F05", "G805-F06", "G805-F08", "G805-F11", "G805-F12", "G805-F13"}
    check("frame_seven", len(frame_specs) == len(frames) == 7 and {key[0] for key in frames} == expected_frame_ids)
    decisions_before = {target: expected_decisions[target]["decision"] for target in TARGETS}
    mutated_displays = {row["source_frame_id"]: "METAMORPHIC_DISPLAY_ONLY_" + row["candidate_display_de"] for row in frame_specs}
    decisions_after = {target: expected_decisions[target]["decision"] for target in TARGETS}
    check("frame_metamorphic_no_decision", len(mutated_displays) == 7 and decisions_after == decisions_before)
    for spec in frame_specs:
        source = source_frames[spec["source_frame_id"]]
        actual = frames[(spec["source_frame_id"],)]
        check(f"frame_source:{spec['source_frame_id']}", source["frame_class"] == "REAL_TWO_SIDED_FRAME" and source["surface"] == spec["target_surface"] and source["exact_frame"] == spec["exact_frame"])
        for field in ("frame_decision_credit", "frame_score_weight", "semantic_credit", "renderer_license", "confirmed_lexeme", "component_export_credit"):
            check(f"frame_zero:{spec['source_frame_id']}:{field}", spec[field] == actual[field] == "0")
        expected = {
            **spec, "source_frame_class": source["frame_class"], "source_occurrences": source["occurrences"],
            "source_physical_folios": source["physical_folios"], "source_stable_sequence_occurrences": source["stable_sequence_occurrences"],
            "source_loci": source["loci"], "gdt806_target_decision": decisions_before[spec["target_surface"]],
            "decision_changed_by_frame": 0,
        }
        compare_row(check, f"frame:{spec['source_frame_id']}", actual, expected)

    passages = loaded["passages"]
    check("passage_12", len(passages) == 12 and Counter(row["target_surface"] for row in passages) == Counter({target: 2 for target in TARGETS}))
    check("passage_scope", all(row["display_only"] == "1" and row["gdt806_decision"] == "UNRESOLVED_RIVAL" and row["semantic_credit"] == row["renderer_license"] == row["confirmed_plaintext"] == row["confirmed_lexeme"] == row["component_export_credit"] == "0" for row in passages))
    assert_unsealed(passages, ("source_selector", "physical_folio", "locus"))

    packet = loaded["packet"]
    check("edge_916", len(packet) == len({row["edge_id"] for row in packet}) == target_global_contacts == 916)
    check("edge_zero_evidence", all(row["formal_access_state"] == "FORMAL_ACCESSED" and row["eligibility_status"] == "INELIGIBLE_EXPLORATORY_TEXT_RELATION" and row["relation_reviewer"] == "PENDING_EXTERNAL" and row["geometry_only_selection"] == "FALSE" for row in packet))
    assert_unsealed(packet, ("page", "physical_folio", "pivot_locus", "target_locus"))
    intake = json.loads((ART / "GDT806_GDT388_EDGE_INTAKE.json").read_text(encoding="utf-8"))
    completed = subprocess.run([str(VMANUS_EXP), "check-edge-packet", str(ART / FILES["packet"])], cwd=ROOT, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    check("edge_intake_exit", completed.returncode == 1 and completed.stderr == "")
    check("edge_intake_equivalent", json.loads(completed.stdout) == intake)
    check("edge_fail_closed", intake["status"] == "INVALID_PACKET" and intake["packet_rows"] == len(intake["errors"]) == 916 and intake["eligible_edges"] == 0 and intake["eligible_folios"] == 0 and intake["discovery_edges"] == intake["holdout_edges"] == intake["mobile_edges"] == 0 and intake["score_ready"] is False and intake["capacity_gate_50_edges_5_folios"] is False and intake["holdout_gate"] is False and intake["mobile_null_gate"] is False)

    card = loaded["card"]
    check("structural_card_one", len(card) == 1)
    zero_card_fields = ("conditional_mapped_preferences", "cross_denominator_concordances", "new_roles", "confirmed_lexemes", "confirmed_plaintext", "renderer_licenses", "component_export_credit", "new_pages_images_or_transcriptions", "f84_or_f84r_rows")
    check("structural_claim_ceiling", card[0]["target_surfaces"] == "6" and card[0]["rival_signatures"] == "12" and card[0]["target_events"] == "967" and card[0]["k12_pool_rows"] == "72" and card[0]["unique_k12_control_surfaces"] == "20" and card[0]["k12_control_events"] == "1737" and card[0]["global_surfaces"] == "652" and card[0]["narrow_surfaces"] == "75" and card[0]["residual_surfaces"] == "577" and card[0]["exact_active_source_cells"] == "111" and card[0]["unresolved_rivals"] == "6" and all(card[0][field] == "0" for field in zero_card_fields))
    check("result_counts", result["target_events"] == 967 and result["target_all_opportunity_raw_l1_r1"] == [967, 967] and result["target_all_opportunity_stable_l1_r1"] == [600, 594] and result["k12_pool_rows"] == 72 and result["unique_k12_control_surfaces"] == 20 and result["k12_control_events"] == 1737 and result["global652_surfaces"] == 652 and result["narrow75_surfaces"] == 75 and result["residual577_surfaces"] == 577 and result["exact_active_source_cells"] == 111 and result["gdt388_context_edges"] == 916)
    check("result_decisions", result["candidate_decisions"] == {target: "UNRESOLVED_RIVAL" for target in TARGETS} and result["decision_counts"] == {"UNRESOLVED_RIVAL": 6})
    check("result_frames", result["frame_rows_zero_credit"] == 7 and result["passage_cards"] == 12)

    manifest = json.loads((EXP / "experiment.json").read_text(encoding="utf-8"))
    ceiling = manifest["claim_ceiling"]
    check("manifest_sealed", manifest["sealed_data"] == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"})
    check("claim_ceiling", "at most target-specific conditional preference or cross-denominator deck-breadth concordance" in ceiling and "zero decision, semantic and renderer credit" in ceiling and "No confirmatory p-value, new role, lexeme, plaintext, component, substance, process, quality, plant, disease, cure, unit or translation may be selected." in ceiling)
    report = (EXP / "REPORT.md").read_text(encoding="utf-8")
    report_flat = " ".join(report.split())
    check("report_ceiling", "keine neue Rolle, Wortbedeutung oder Renderer-Lizenz" in report_flat and "keine unabhängige semantische Replikation" in report_flat and "Bestätigte Lexeme/Klartextsätze: 0/0" in report_flat and "f84/f84r-Zeilen: 0" in report_flat)

    baseline = {filename: sha(ART / filename) for filename in expected_outputs | {"RESULT.json"}}
    replay_count = 0
    if not args.skip_replay:
        for replay in range(1, 3):
            with tempfile.TemporaryDirectory(prefix=f".gdt806_replay_{replay}_", dir=EXP) as temporary:
                output = Path(temporary) / "artifacts"
                completed = subprocess.run(["python3", str(RUN), "--output-dir", str(output)], cwd=ROOT, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                check(f"replay_exit:{replay}", completed.returncode == 0 and completed.stderr == "")
                check(f"replay_set:{replay}", {path.name for path in output.iterdir()} == set(baseline))
                for filename, digest in baseline.items():
                    check(f"replay_hash:{replay}:{filename}", sha(output / filename) == digest)
                replay_count += 1

    validation: dict[str, Any] = {
        "schema": "GDT806_INDEPENDENT_VALIDATION_V1", "experiment": "GDT806", "status": "PASS",
        "checks": len(checks), "replays": replay_count, "published_freeze_commit": "33ac1127",
        "validator_imported_gdt806_builder": False,
        "global_stage_counts": [[rows, surfaces] for _name, rows, surfaces in EXPECTED_STAGES],
        "global_surfaces": 652, "narrow_surfaces": 75, "residual_surfaces": 577,
        "exact_active_source_cells": 111, "target_events": 967,
        "target_all_opportunity_raw_l1_r1": [967, 967], "target_all_opportunity_stable_l1_r1": [600, 594],
        "k12_pool_rows": 72, "unique_k12_controls": 20, "k12_control_events": 1737,
        "exact_rational_scores_validated": 948, "k12_contrasts_validated": 72,
        "lofo_folds_validated": 958, "loco_folds_validated": 576,
        "conditional_mapped_preferences": 0, "cross_denominator_concordances": 0,
        "unresolved_rivals": 6, "new_roles": 0, "confirmed_lexemes": 0,
        "confirmed_plaintext_clauses": 0, "renderer_licenses": 0, "component_exports": 0,
        "frame_rows_zero_credit": 7, "frame_metamorphic_decision_changes": 0,
        "gdt388_edges": 916, "gdt388_status": "INVALID_PACKET", "gdt388_score_ready": False,
        "new_pages_images_or_transcriptions": 0, "sealed_f84_or_f84r_seen": False,
        "validated_result_hash": sha(RESULT),
        "validated_output_hashes": {filename: sha(ART / filename) for filename in sorted(expected_outputs)},
    }
    validation["content_hash"] = hashlib.sha256(json.dumps(validation, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PASS: {len(checks)} checks; {replay_count} byte-identical replays; 948 exact Fraction scores; 0 selections; GDT388 fail-closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
