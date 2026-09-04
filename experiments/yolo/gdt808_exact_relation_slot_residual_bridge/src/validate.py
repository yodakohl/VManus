#!/usr/bin/env python3
"""Independent, fail-closed validation for GDT808.

The validator never imports the experiment builder. It reconstructs the
admitted corpus through guarded TSV queries, rebuilds the registered carrier
populations, focal events, feature decks, held predictions, and nulls, then
audits the published artifacts.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import multiprocessing
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt808_exact_relation_slot_residual_bridge"
SRC = BASE / "src"
ART = BASE / "artifacts"
MANIFEST = BASE / "experiment.json"
VALIDATION = ART / "VALIDATION.json"
VMANUS_EXP = ROOT / "vmanus-exp"
ALLOWLIST = ROOT / "experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv"
LINES_RAW = ROOT / "transcription/voynich_zl3b_lines.tsv"
CROSS_RAW = ROOT / "transcription/voynich_cross_transcription_lines.tsv"
TOKENS_RAW = ROOT / "transcription/voynich_zl3b_tokens.tsv"
G759 = ROOT / "experiments/yolo/gdt759_quantity_part_state_construction_atlas/artifacts/EXACT_122_CONSTRUCTION_SPAN_ATLAS.tsv"
G768 = ROOT / "experiments/yolo/gdt768_chor_shor_part_identity_tournament/artifacts/ANCHOR_404_OCCURRENCE_ATLAS.tsv"
G757 = ROOT / "experiments/yolo/gdt757_initial_formula_role_atlas/artifacts/INITIAL_FORMULA_79_OCCURRENCE_ATLAS.tsv"
MODEL_SPECS = SRC / "RELATION_MODEL_SPECS.tsv"
CORE_SPECS = SRC / "CORE_CARRIER_SPECS.tsv"
QUARANTINE_SPECS = SRC / "QUARANTINE_SPECS.tsv"
IMPLEMENTATION_SPECS = SRC / "IMPLEMENTATION_SPECS.tsv"
FEATURE_SPECS = SRC / "FEATURE_DECK_SPECS.tsv"
CONTROL_SPECS = SRC / "CONTROL_SPECS.tsv"
RIVAL_SPECS = SRC / "RIVAL_DECISION_SPECS.tsv"
SEMANTIC_SPECS = SRC / "SEMANTIC_RIVAL_SPECS.tsv"
HISTORICAL_SPECS = SRC / "HISTORICAL_TOPOLOGY_SPECS.tsv"

OUTPUT_NAMES = (
    "SOURCE_LOCK.tsv", "GDT808_IMPLEMENTATION_CLARIFICATIONS.tsv",
    "GDT808_GUARDED_QUERY_STATS.tsv", "GDT808_SOURCE_CENSUS.tsv",
    "GDT808_RAW35_ALL28_CORE13_CARRIER_CENSUS.tsv",
    "GDT808_Q152_EXACT_QUARANTINE.tsv", "GDT808_1777_CORE_EVENT_ATLAS.tsv",
    "GDT808_FEATURE_DECK_CAPACITY.tsv", "GDT808_COMPONENT_HELD_FOLDS.tsv",
    "GDT808_HELD_PREDICTIONS.tsv", "GDT808_DECK_SCORE_SUMMARY.tsv",
    "GDT808_CONDITIONAL_CONCORDANCE.tsv", "GDT808_POSITION_MASK_SLOT_ABLATIONS.tsv",
    "GDT808_CARRIER_DIRECTION_DIAGNOSTICS.tsv", "GDT808_NULL_STRATUM_AUDIT.tsv",
    "GDT808_NULL_SCORES.tsv", "GDT808_ALL28_SENSITIVITY.tsv",
    "GDT808_ED1_SENSITIVITY.tsv", "GDT808_THIN_KOL_TAL.tsv",
    "GDT808_LEARNED_CHEOL_OTAL.tsv", "GDT808_HISTORICAL_RIVAL_CARD.tsv",
    "GDT808_GDT388_RELATION_PACKET.tsv", "GDT808_GDT388_EDGE_INTAKE.json",
    "GDT808_STRUCTURAL_CARD.tsv", "RESULT.json")

TAILS = ("eody", "eol", "edy", "ol")

SOURCE_CENSUS_FIELDS = (
    "scope", "item", "count", "expected", "status", "raw_parsed",
    "outside_strict", "strict_parsed", "rank_stable", "unique_forced_lcs",
    "own_family_singleton", "rank_stable_rate_strict_prefilter",
    "accepted_paragraphs", "accepted_focal_lines",
    "strict_candidate_physical_folios")
SUMMARY_FIELDS = (
    "model_id", "population", "source_axis", "target_axis", "score_channel",
    "events", "positive_events", "negative_events", "micro_auc",
    "carrier_macro_auc", "balanced_accuracy", "balanced_log_loss",
    "carriers_scored", "carriers_auc_above_half", "carriers_auc_below_half",
    "post_score_sign_flip", "semantic_credit", "component_export_credit")
CONTROL_FIELDS = (
    "row_type", "carrier", "surface_positive", "surface_negative", "events",
    "positive_events", "negative_events", "physical_folios", "score_channel",
    "micro_auc", "carrier_macro_auc", "balanced_accuracy", "balanced_log_loss",
    "holdout", "selection_credit", "semantic_credit")
HISTORICAL_FIELDS = (
    "row_type", "rival_id", "rank", "total_points", "evidence_id", "metric",
    "observed_value", "operator", "threshold", "points_available",
    "points_awarded", "passed", "working_theory", "historical_sources",
    "selection_credit", "semantic_credit")
EDGE_FIELDS = (
    "edge_id", "batch_id", "page", "physical_folio", "diagram_unit_id",
    "pivot_visual_id", "pivot_locus", "target_visual_id", "target_locus",
    "relation_type", "direction_basis", "ownership_basis",
    "geometry_only_selection", "source_manifest_id", "page_crop_sha256",
    "pivot_crop_sha256", "target_crop_sha256", "source_aware_localizer",
    "relation_reviewer", "relation_confidence", "ambiguity_state",
    "formal_access_state", "fold_assignment", "eligibility_status")
EXPECTED_TSV_SCHEMAS = {
    "SOURCE_LOCK.tsv": ("path", "sha256", "purpose", "access_mode", "manifest_hash_match"),
    "GDT808_IMPLEMENTATION_CLARIFICATIONS.tsv": ("issue", "resolution", "selection_credit"),
    "GDT808_GUARDED_QUERY_STATS.tsv": (
        "query_id", "source_path", "selector_column", "allowed_value_count",
        "output_columns", "forbidden_prefixes", "selected_rows",
        "skipped_forbidden_rows", "skipped_not_allowed_rows", "query_returncode"),
    "GDT808_SOURCE_CENSUS.tsv": SOURCE_CENSUS_FIELDS,
    "GDT808_RAW35_ALL28_CORE13_CARRIER_CENSUS.tsv": (
        "carrier", "raw_complete", "all28_stable_complete", "core13",
        "semantic_credit", "component_export_credit",
        *(field for tail in TAILS for field in (
            f"{tail}_raw_occurrences", f"{tail}_stable_occurrences",
            f"{tail}_stable_physical_folios")),
        "eligible_events", *(f"{tail}_eligible_events" for tail in TAILS)),
    "GDT808_Q152_EXACT_QUARANTINE.tsv": (
        "surface", "raw35_four_cell_member", "thin9_pair_member",
        "deduplicated_overlap6", "quarantine_rule", "substring_rule",
        "semantic_credit", "component_export_credit"),
    "GDT808_1777_CORE_EVENT_ATLAS.tsv": (
        "event_id", "carrier", "tail", "axis", "expanded_label", "surface",
        "page", "physical_folio", "paragraph_id", "locus", "line_number",
        "token_index", "line_token_count", "paragraph_line_index", "section",
        "language", "hand", "rank_stable_all_three",
        "it2a_unique_forced_exact_ordinal", "rf1b_unique_forced_exact_ordinal",
        "own_family_raw_line_count", "targetfree_line_length_bin",
        "topic_feature_count", "topic_feature_sha256", "template_feature_count",
        "template_feature_sha256", "form_regime_feature_count",
        "form_regime_feature_sha256", "slot_hole_feature_count",
        "slot_hole_feature_sha256", "mask_status_audit_feature_count",
        "mask_status_audit_feature_sha256", "raw_slot_sensitivity_feature_count",
        "raw_slot_sensitivity_feature_sha256", "semantic_credit",
        "component_export_credit"),
    "GDT808_FEATURE_DECK_CAPACITY.tsv": (
        "population", "deck_id", "events", "nonempty_events", "empty_events",
        "feature_types", "global_two_carrier_two_folio_supported_types",
        "mean_features_per_event", "max_features_per_event", "feature_value"),
    "GDT808_COMPONENT_HELD_FOLDS.tsv": (
        "model_id", "population", "source_axis", "target_axis", "held_carrier",
        "held_physical_folio", "train_events", "train_positive_events",
        "train_negative_events", "train_carriers", "train_physical_folios",
        "test_events", "test_positive_events", "test_negative_events",
        "carrier_excluded", "physical_folio_excluded", "topic_vocabulary",
        "template_vocabulary", "form_vocabulary", "slot_vocabulary",
        "union_nuisance_vocabulary", "union_augmented_vocabulary",
        "fold_scoreable"),
    "GDT808_HELD_PREDICTIONS.tsv": (
        "prediction_id", "model_id", "population", "source_axis", "target_axis",
        "event_id", "carrier", "target_tail", "true_label", "page",
        "physical_folio", "paragraph_id", "locus", "line_number", "token_index",
        "section", "language", "hand", "targetfree_line_length_bin", "variant",
        "topic_score", "topic_known", "template_score", "template_known",
        "form_score", "form_known", "slot_score", "slot_known",
        "union_nuisance_score", "union_nuisance_known", "union_augmented_score",
        "union_augmented_known", "form_base_score", "form_base_known",
        "position_score", "position_known", "mask_score", "mask_known",
        "raw_slot_score", "raw_slot_known", "nuisance_score", "augmented_score",
        "nuisance_without_position_score", "nuisance_plus_mask_score",
        "augmented_raw_score"),
    "GDT808_DECK_SCORE_SUMMARY.tsv": SUMMARY_FIELDS,
    "GDT808_CONDITIONAL_CONCORDANCE.tsv": (
        "row_type", "model_id", "score_channel", "carrier", "section",
        "language", "hand", "targetfree_line_length_bin", "events",
        "positive_events", "negative_events", "comparable_pairs", "concordance",
        "pooled_pair_concordance_audit"),
    "GDT808_POSITION_MASK_SLOT_ABLATIONS.tsv": (
        "model_id", "audit_channel", "events", "micro_auc", "carrier_macro_auc",
        "balanced_accuracy", "balanced_log_loss",
        "increment_over_primary_nuisance_macro_auc", "selection_credit"),
    "GDT808_CARRIER_DIRECTION_DIAGNOSTICS.tsv": (
        "model_id", "population", "carrier", "score_channel", "events",
        "positive_events", "negative_events", "auc", "direction",
        "semantic_credit", "component_export_credit"),
    "GDT808_NULL_STRATUM_AUDIT.tsv": (
        "null_family", "null_id", "model_id", "target_axis", "carrier", "section",
        "language", "hand", "targetfree_line_length_bin", "stratum_events",
        "offset_mod_n", "moved_labels", "identity_labels",
        "flipped_source_carriers"),
    "GDT808_NULL_SCORES.tsv": (
        "null_family", "null_id", "model_id", "carrier_macro_auc",
        "nuisance_carrier_macro_auc", "slot_carrier_macro_auc", "local_gain",
        "conditional_local_gain", "changed_labels", "changed_fraction",
        "mobility_warning", "observed_reference", "ties_count_against_target"),
    "GDT808_ALL28_SENSITIVITY.tsv": SUMMARY_FIELDS,
    "GDT808_ED1_SENSITIVITY.tsv": SUMMARY_FIELDS,
    "GDT808_THIN_KOL_TAL.tsv": CONTROL_FIELDS,
    "GDT808_LEARNED_CHEOL_OTAL.tsv": CONTROL_FIELDS,
    "GDT808_HISTORICAL_RIVAL_CARD.tsv": HISTORICAL_FIELDS,
    "GDT808_GDT388_RELATION_PACKET.tsv": EDGE_FIELDS,
    "GDT808_STRUCTURAL_CARD.tsv": (
        "card_id", "formal_scope", "decision", "joint_topology",
        "leading_historical_rival", "metrics_json", "claim_ceiling",
        "semantic_credit", "renderer_credit"),
}

MIXED_PATHS = {path.resolve() for path in
               (LINES_RAW, CROSS_RAW, TOKENS_RAW, G759, G768, G757)}
THIN_TAILS = ("kol", "tal")
DECKS = ("TOPIC", "TEMPLATE", "FORM_REGIME", "SLOT_HOLE")
ALPHA = 0.5
FLOAT_TOL = 5e-10
EXPECTED = {
    "selectors": 179, "raw_lines": 4137, "raw_tokens": 32339,
    "strict_paragraphs": 665, "strict_lines": 3807, "strict_tokens": 31938,
    "outside_lines": 330, "outside_tokens": 401, "raw35": 35,
    "all28": 28, "core13": 13, "q152": 152, "core_events": 1777,
    "core_event_paragraphs": 559, "core_event_lines": 1403,
    "core_event_folios": 169, "all28_events": 2208,
    "all28_event_paragraphs": 596,
}
MIXED_MANIFEST_HASHES = {
    "transcription/voynich_zl3b_lines.tsv": "7520dd4c11f4d23c8492e4b2a52cc0fcbda6d9fc88a96ead8f1c31081a4d7ed2",
    "transcription/voynich_cross_transcription_lines.tsv": "ff3a4559004a29764c60102326de154b29fbba06a2a206bdd76d7feda432e16c",
    "transcription/voynich_zl3b_tokens.tsv": "6a061a26edc05ff37dc386c2215774c229a5ff087d3091e68bdd4983a6c007aa",
    "experiments/yolo/gdt759_quantity_part_state_construction_atlas/artifacts/EXACT_122_CONSTRUCTION_SPAN_ATLAS.tsv": "456ffe9569f953ef69ac86d82e6d428fda22f41a7531d4722833a024eaed77c4",
    "experiments/yolo/gdt768_chor_shor_part_identity_tournament/artifacts/ANCHOR_404_OCCURRENCE_ATLAS.tsv": "65d07e01bc3354efe71681684b9800ebc57513d6d99487d4dd502ef8482c70df",
    "experiments/yolo/gdt757_initial_formula_role_atlas/artifacts/INITIAL_FORMULA_79_OCCURRENCE_ATLAS.tsv": "2d85ad8af96262ceb3a17761ef7b56d64062852cc0d9849c09fb99aa42d5af11",
}


@dataclass(frozen=True)
class Line:
    page: str
    locus: str
    number: int
    section: str
    language: str
    hand: str
    paragraph_start: bool
    paragraph_end: bool
    tokens: tuple[str, ...]
    stable: tuple[bool, ...]
    alternate: Mapping[str, tuple[str, ...]]


@dataclass(frozen=True)
class Paragraph:
    paragraph_id: str
    page: str
    physical_folio: str
    ordinal_on_page: int
    section: str
    language: str
    hand: str
    lines: tuple[Line, ...]


@dataclass(frozen=True)
class Event:
    event_id: str
    ordinal: int
    carrier: str
    tail: str
    surface: str
    paragraph: Paragraph
    line: Line
    line_index: int
    token_index: int
    feature_decks: Mapping[str, frozenset[str]]
    feature_decks_ed1: Mapping[str, frozenset[str]]
    mask_status: frozenset[str]
    raw_slot: frozenset[str]
    line_length_bin: int
    ed1_line_length_bin: int
    it2a_ordinal: int
    rf1b_ordinal: int

    @property
    def physical_folio(self) -> str:
        return self.paragraph.physical_folio


@dataclass(frozen=True)
class ModelSpec:
    model_id: str
    source_axis: str
    target_axis: str
    positive_source: str
    negative_source: str
    positive_target: str
    negative_target: str
    population: str


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    if path.resolve() in MIXED_PATHS:
        raise AssertionError(f"mixed TSV must be guarded: {rel(path)}")
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def natural_page_key(value: str) -> tuple[int, int, int, str]:
    match = re.fullmatch(r"f(\d+)([rv])(\d*)", value)
    if match is None:
        return (10**9, 9, 9, value)
    return (int(match.group(1)), 0 if match.group(2) == "r" else 1,
            int(match.group(3) or 0), value)


def physical_folio(page: str) -> str:
    match = re.match(r"^(f[0-9]+[rv])", page)
    if match is None:
        raise AssertionError(f"cannot normalize physical folio: {page}")
    return match.group(1)


def leaf_folio(page: str) -> str:
    match = re.match(r"^(f[0-9]+)", page)
    if match is None:
        raise AssertionError(f"cannot normalize leaf folio: {page}")
    return match.group(1)


def truth(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "pass"}


def guarded_query(path: Path, pages: Sequence[str], columns: Sequence[str]) -> tuple[list[dict[str, str]], dict[str, Any]]:
    command = [str(VMANUS_EXP), "query-tsv", rel(path), "--selector", "page"]
    for page in sorted(pages, key=natural_page_key):
        command.extend(("--allow", page))
    command.extend(("--columns", ",".join(columns), "--forbid-prefix", "f84",
                    "--forbid-prefix", "f84r"))
    completed = subprocess.run(command, cwd=ROOT, check=False, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if completed.returncode:
        raise AssertionError(f"guarded query failed for {rel(path)}: {completed.stderr[-2000:]}")
    stat_lines = [line for line in completed.stderr.splitlines() if line.startswith("GUARD_STATS ")]
    if len(stat_lines) != 1:
        raise AssertionError(f"missing or duplicate guard stats: {rel(path)}")
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    if rows and tuple(rows[0]) != tuple(columns):
        raise AssertionError(f"guarded output schema drift: {rel(path)}")
    for row in rows:
        if any(str(row.get(key, "")).startswith("f84") for key in ("page", "locus")):
            raise AssertionError("sealed selector/locus materialized")
    return rows, json.loads(stat_lines[0][12:])


def lcs_table(left: Sequence[str], right: Sequence[str]) -> list[list[int]]:
    table = [[0] * (len(right) + 1) for _ in range(len(left) + 1)]
    for i in range(len(left) - 1, -1, -1):
        for j in range(len(right) - 1, -1, -1):
            table[i][j] = (1 + table[i + 1][j + 1] if left[i] == right[j]
                           else max(table[i + 1][j], table[i][j + 1]))
    return table


def unique_forced_lcs_ordinal(reference: Sequence[str], alternate: Sequence[str],
                              index: int) -> int | None:
    suffix = lcs_table(reference, alternate)
    optimum = suffix[0][0]
    without = tuple(reference[:index]) + tuple(reference[index + 1:])
    if lcs_table(without, alternate)[0][0] >= optimum:
        return None
    prefix = [[0] * (len(alternate) + 1) for _ in range(len(reference) + 1)]
    for i, left in enumerate(reference):
        for j, right in enumerate(alternate):
            prefix[i + 1][j + 1] = (1 + prefix[i][j] if left == right
                                     else max(prefix[i][j + 1], prefix[i + 1][j]))
    partners = [j for j, value in enumerate(alternate)
                if value == reference[index]
                and prefix[index][j] + 1 + suffix[index + 1][j + 1] == optimum]
    return partners[0] + 1 if len(partners) == 1 else None


def unique_forced_lcs(reference: Sequence[str], alternate: Sequence[str], index: int) -> bool:
    return unique_forced_lcs_ordinal(reference, alternate, index) is not None


def parse_relation(surface: str) -> tuple[str, str] | None:
    for tail in TAILS:
        if surface.endswith(tail) and len(surface) > len(tail):
            return surface[:-len(tail)], tail
    return None


def load_guarded_corpus() -> tuple[list[Line], list[Paragraph], list[Line], dict[str, Any]]:
    allow = read_tsv(ALLOWLIST)
    if not allow or list(allow[0]) != ["page"]:
        raise AssertionError("allow-list schema drift")
    pages = [row["page"] for row in allow]
    if len(pages) != EXPECTED["selectors"] or len(set(pages)) != len(pages):
        raise AssertionError("allow-list cardinality/uniqueness drift")
    if any(page.startswith("f84") for page in pages):
        raise AssertionError("sealed page present in allow-list")
    line_columns = ("page", "locus", "line_number", "section", "language", "hand",
                    "paragraph_start", "paragraph_end", "token_count", "eva_clean")
    token_columns = ("page", "locus", "token_index", "eva", "section", "language", "hand")
    cross_columns = ("page", "locus", "all_three_present", "all_present_exact",
                     "zl3b_clean", "it2a_clean", "rf1b_clean")
    line_rows, line_stats = guarded_query(LINES_RAW, pages, line_columns)
    token_rows, token_stats = guarded_query(TOKENS_RAW, pages, token_columns)
    cross_rows, cross_stats = guarded_query(CROSS_RAW, pages, cross_columns)
    if len(line_rows) != EXPECTED["raw_lines"] or len(cross_rows) != EXPECTED["raw_lines"]:
        raise AssertionError("guarded line/cross census drift")
    if len(token_rows) != EXPECTED["raw_tokens"]:
        raise AssertionError("guarded token census drift")
    token_map: defaultdict[tuple[str, str], list[tuple[int, str]]] = defaultdict(list)
    for row in token_rows:
        token_map[(row["page"], row["locus"])].append((int(row["token_index"]), row["eva"]))
    tokens: dict[tuple[str, str], tuple[str, ...]] = {}
    for key, values in token_map.items():
        values.sort()
        if [index for index, _ in values] != list(range(1, len(values) + 1)):
            raise AssertionError(f"non-contiguous token ordinals: {key}")
        tokens[key] = tuple(value for _, value in values)
    cross: dict[tuple[str, str], dict[str, tuple[str, ...]]] = {}
    for row in cross_rows:
        key = (row["page"], row["locus"])
        if key in cross:
            raise AssertionError(f"duplicate cross-reader line: {key}")
        cross[key] = {name: tuple(row[column].split()) for name, column in (
            ("zl3b", "zl3b_clean"), ("it2a", "it2a_clean"), ("rf1b", "rf1b_clean"))}
    lines: list[Line] = []
    seen: set[tuple[str, str]] = set()
    for row in sorted(line_rows, key=lambda item: (natural_page_key(item["page"]),
                                                    int(item["line_number"]), item["locus"])):
        key = (row["page"], row["locus"])
        if key in seen or key not in cross:
            raise AssertionError(f"line identity/cross parity failure: {key}")
        seen.add(key)
        line_tokens = tokens.get(key, ())
        if line_tokens != tuple(row["eva_clean"].split()) or line_tokens != cross[key]["zl3b"]:
            raise AssertionError(f"guarded line/token/cross mismatch: {key}")
        if len(line_tokens) != int(row["token_count"]):
            raise AssertionError(f"line token count mismatch: {key}")
        ranks: Counter[str] = Counter()
        stable: list[bool] = []
        for surface in line_tokens:
            ranks[surface] += 1
            stable.append(ranks[surface] <= min(reader.count(surface) for reader in cross[key].values()))
        lines.append(Line(row["page"], row["locus"], int(row["line_number"]),
                          row["section"], row["language"], row["hand"],
                          truth(row["paragraph_start"]), truth(row["paragraph_end"]),
                          line_tokens, tuple(stable), cross[key]))
    if set(cross) != seen or set(tokens) - seen:
        raise AssertionError("guarded source key-set mismatch")
    paragraphs: list[Paragraph] = []
    outside: list[Line] = []
    by_page: defaultdict[str, list[Line]] = defaultdict(list)
    for line in lines:
        by_page[line.page].append(line)
    for page in sorted(by_page, key=natural_page_key):
        active: list[Line] | None = None
        page_ordinal = 0
        for line in sorted(by_page[page], key=lambda item: (item.number, item.locus)):
            if line.paragraph_start:
                if active is not None:
                    raise AssertionError(f"nested strict paragraph: {line.locus}")
                active = []
            if active is None:
                outside.append(line)
                if line.paragraph_end:
                    raise AssertionError(f"paragraph end without start: {line.locus}")
                continue
            active.append(line)
            if line.paragraph_end:
                metadata = {(item.section, item.language, item.hand) for item in active}
                if len(metadata) != 1:
                    raise AssertionError(f"heterogeneous strict paragraph: {line.locus}")
                section, language, hand = next(iter(metadata))
                page_ordinal += 1
                paragraphs.append(Paragraph(f"G808-P{len(paragraphs) + 1:04d}", page,
                                            physical_folio(page), page_ordinal, section,
                                            language, hand, tuple(active)))
                active = None
        if active is not None:
            raise AssertionError(f"unclosed paragraph at page boundary: {page}")
    census = {"strict_paragraphs": len(paragraphs),
              "strict_lines": sum(len(p.lines) for p in paragraphs),
              "strict_tokens": sum(len(line.tokens) for p in paragraphs for line in p.lines),
              "outside_lines": len(outside),
              "outside_tokens": sum(len(line.tokens) for line in outside)}
    for name, value in census.items():
        if value != EXPECTED[name]:
            raise AssertionError(f"strict corpus drift {name}: {value} != {EXPECTED[name]}")
    return lines, paragraphs, outside, {
        "allowlist_selectors": len(pages), "raw_lines": len(line_rows),
        "raw_tokens": len(token_rows), "guarded_queries": {
            "lines": line_stats, "tokens": token_stats, "cross": cross_stats}, **census}


def length_bin(count: int) -> int:
    return int(math.floor(math.log2(count + 1)))


def quartile(index: int, count: int) -> int:
    if not 1 <= index <= count:
        raise AssertionError(f"quartile ordinal outside count: {index}/{count}")
    return min(4, 1 + int(math.floor(4 * (index - 1) / count)))


def index_bin(index: int) -> str:
    return str(index) if index <= 4 else "5PLUS"


def word_length_bin(surface: str) -> str:
    return str(len(surface)) if len(surface) <= 6 else "7PLUS"


def count_bin(count: int) -> str:
    return str(count) if count <= 2 else "3PLUS"


def q12(value: float) -> float:
    """Replay the builder's 12-significant-digit event-score serialization."""
    return float(f"{value:.12g}")


def feature_surface(feature: str) -> str | None:
    if "=" not in feature:
        return None
    prefix, value = feature.split("=", 1)
    if prefix in {"TOPIC:WHOLE", "TEMPLATE:L3", "TEMPLATE:L4",
                  "TEMPLATE:L5PLUS", "TEMPLATE:R3", "TEMPLATE:R4",
                  "TEMPLATE:R5PLUS", "SLOT:L1", "SLOT:L2",
                  "SLOT:R1", "SLOT:R2", "RAW_SLOT:L1", "RAW_SLOT:L2",
                  "RAW_SLOT:R1", "RAW_SLOT:R2"} and ">" not in value:
        return value
    return None


def canonical_features(paragraph: Paragraph, line: Line, token_index: int,
                       carrier: str, q152: frozenset[str],
                       end_classes: Sequence[str],
                       own_family: Iterable[str] | None = None) -> tuple[dict[str, frozenset[str]], frozenset[str], frozenset[str], int]:
    zero = token_index - 1
    family = (frozenset(own_family) if own_family is not None
              else frozenset(carrier + tail for tail in TAILS))
    topic_words: set[str] = set()
    for other in paragraph.lines:
        if other.locus == line.locus or set(other.tokens) & family:
            continue
        topic_words.update(surface for surface in other.tokens if surface not in q152)
    topic = frozenset("TOPIC:WHOLE=" + surface for surface in topic_words)
    template: set[str] = set()
    for position, surface in enumerate(line.tokens):
        distance = position - zero
        if abs(distance) < 3 or surface in q152:
            continue
        side = "L" if distance < 0 else "R"
        magnitude = abs(distance)
        bucket = str(magnitude) if magnitude in (3, 4) else "5PLUS"
        template.add(f"TEMPLATE:{side}{bucket}={surface}")
    line_free = [surface for surface in line.tokens if surface not in q152]
    paragraph_free = [surface for item in paragraph.lines for surface in item.tokens
                      if surface not in q152]
    line_ordinal = next(index for index, item in enumerate(paragraph.lines, 1)
                        if item.locus == line.locus)
    token_count = len(line.tokens)
    line_class = ('SINGLE' if len(paragraph.lines) == 1 else
                  'FIRST' if line_ordinal == 1 else
                  'LAST' if line_ordinal == len(paragraph.lines) else 'MIDDLE')
    form_base = {
        f"FORM:SECTION={paragraph.section}", f"FORM:LANGUAGE={paragraph.language}",
        f"FORM:HAND={paragraph.hand}", f"FORM:JOINT={paragraph.section}/{paragraph.language}/{paragraph.hand}",
        f"FORM:TARGETFREE_LINE_LENGTH_BIN={length_bin(len(line_free))}",
        f"FORM:TARGETFREE_PARAGRAPH_LENGTH_BIN={length_bin(len(paragraph_free))}",
        f"FORM:PARAGRAPH_LINE_POSITION={line_class}",
        f"FORM:PARAGRAPH_LINE_QUARTILE={quartile(line_ordinal, len(paragraph.lines))}",
    }
    position = {
        f"POSITION:FOCAL_HOLE={'SINGLE' if token_count == 1 else 'FIRST' if token_index == 1 else 'LAST' if token_index == token_count else 'MIDDLE'}",
        f"POSITION:FORWARD_INDEX={index_bin(token_index)}",
        f"POSITION:REVERSE_INDEX={index_bin(token_count - token_index + 1)}",
        f"POSITION:QUARTILE={quartile(token_index, token_count)}",
    }
    for scope, values in (("LINE", line_free), ("PARAGRAPH", paragraph_free)):
        lengths = Counter(word_length_bin(surface) for surface in values)
        endings = Counter(surface[-1] for surface in values)
        for bucket in ("1", "2", "3", "4", "5", "6", "7PLUS"):
            form_base.add(f"FORM:{scope}_WORD_LENGTH_{bucket}_COUNT={count_bin(lengths[bucket])}")
        for ending in end_classes:
            form_base.add(f"FORM:{scope}_END_{ending}_COUNT={count_bin(endings[ending])}")
    stable_neighbours: dict[int, str] = {}
    raw_neighbours: dict[int, str] = {}
    status: set[str] = set()
    for offset in (-2, -1, 1, 2):
        slot_position = zero + offset
        name = ("L" if offset < 0 else "R") + str(abs(offset))
        if not 0 <= slot_position < token_count:
            status.add("MASK:" + name + "=BOUNDARY")
            continue
        surface = line.tokens[slot_position]
        if surface in q152:
            status.add("MASK:" + name + "=QUARANTINED")
            continue
        raw_neighbours[offset] = surface
        if line.stable[slot_position]:
            stable_neighbours[offset] = surface
            status.add("MASK:" + name + "=VISIBLE_STABLE")
        else:
            status.add("MASK:" + name + "=UNSTABLE")
    status.add("MASK:LINE_Q_COUNT=" + count_bin(sum(surface in q152 for surface in line.tokens)))
    status.add("MASK:LINE_UNSTABLE_COUNT=" + count_bin(sum(not value for value in line.stable)))

    def packet(neighbours: Mapping[int, str], namespace: str) -> frozenset[str]:
        output = {(namespace + ":" + ("L" if offset < 0 else "R")
                   + str(abs(offset)) + "=" + surface)
                  for offset, surface in neighbours.items()}
        for left, right, name in ((-2, -1, "L2_L1"), (-1, 1, "L1_R1"),
                                  (1, 2, "R1_R2")):
            if left in neighbours and right in neighbours:
                output.add(f"{namespace}:{name}={neighbours[left]}>{neighbours[right]}")
        return frozenset(output)

    decks = {"TOPIC": topic, "TEMPLATE": frozenset(template),
             "FORM_REGIME": frozenset(form_base | position),
             "FORM_BASE": frozenset(form_base), "POSITION": frozenset(position),
             "SLOT_HOLE": packet(stable_neighbours, "SLOT"),
             "RAW_SLOT": packet(raw_neighbours, "RAW_SLOT"),
             "MASK_STATUS": frozenset(status)}
    return decks, frozenset(status), packet(raw_neighbours, "RAW_SLOT"), length_bin(len(line_free))


def relation_populations(lines: Sequence[Line], paragraphs: Sequence[Paragraph]) -> dict[str, Any]:
    qrows = {row["identifier"]: row for row in read_tsv(QUARANTINE_SPECS)}
    expected_raw = tuple(qrows["RAW35"]["surfaces_or_rule"].split("|"))
    expected_all = tuple(qrows["ALL28"]["surfaces_or_rule"].split("|"))
    expected_core = tuple(row["carrier"] for row in read_tsv(CORE_SPECS))
    thin9 = tuple(qrows["THIN9"]["surfaces_or_rule"].split("|"))
    raw_counts: defaultdict[str, Counter[str]] = defaultdict(Counter)
    stable_counts: defaultdict[str, Counter[str]] = defaultdict(Counter)
    stable_folios: defaultdict[tuple[str, str], set[str]] = defaultdict(set)
    for line in lines:
        for index, surface in enumerate(line.tokens):
            parsed = parse_relation(surface)
            if parsed is None:
                continue
            carrier, tail = parsed
            raw_counts[carrier][tail] += 1
            if line.stable[index]:
                stable_counts[carrier][tail] += 1
                stable_folios[carrier, tail].add(physical_folio(line.page))
    raw35 = tuple(sorted(carrier for carrier, counts in raw_counts.items()
                         if all(counts[tail] > 0 for tail in TAILS)))
    all28 = tuple(sorted(carrier for carrier, counts in stable_counts.items()
                         if all(counts[tail] > 0 for tail in TAILS)))
    core13 = tuple(sorted(carrier for carrier in all28
                          if all(stable_counts[carrier][tail] >= 3
                                 and len(stable_folios[carrier, tail]) >= 3 for tail in TAILS)))
    if tuple(sorted(expected_raw)) != raw35 or len(raw35) != EXPECTED["raw35"]:
        raise AssertionError("RAW35 independent reconstruction drift")
    if tuple(sorted(expected_all)) != all28 or len(all28) != EXPECTED["all28"]:
        raise AssertionError("ALL28 independent reconstruction drift")
    if tuple(sorted(expected_core)) != core13 or len(core13) != EXPECTED["core13"]:
        raise AssertionError("CORE13 independent reconstruction drift")
    main = {carrier + tail for carrier in raw35 for tail in TAILS}
    thin = {carrier + tail for carrier in thin9 for tail in THIN_TAILS}
    q152 = frozenset(main | thin)
    overlap = sorted(main & thin)
    if len(q152) != EXPECTED["q152"] or overlap != sorted(qrows["OVERLAP6"]["surfaces_or_rule"].split("|")):
        raise AssertionError("Q152 independent construction drift")
    paragraph_by_locus = {line.locus: paragraph for paragraph in paragraphs for line in paragraph.lines}
    end_classes = tuple(sorted({surface[-1] for line in lines for surface in line.tokens
                                if surface and surface not in q152}))
    observed_surfaces = {surface for line in lines for surface in line.tokens}
    ed1 = frozenset(surface for surface in observed_surfaces if surface not in q152
                    and any(levenshtein(surface, blocked) <= 1 for blocked in q152))

    def build_events(population: Sequence[str], prefix: str) -> tuple[list[Event], dict[str, int]]:
        permitted = set(population)
        preliminary: list[tuple[str, str, str, Paragraph, Line, int, int, int]] = []
        audit = Counter()
        raw_population_occurrences = 0
        for line in lines:
            paragraph = paragraph_by_locus.get(line.locus)
            for index, surface in enumerate(line.tokens):
                parsed = parse_relation(surface)
                if parsed is None or parsed[0] not in permitted:
                    continue
                raw_population_occurrences += 1
                carrier, tail = parsed
                # The registered funnel first restricts to strictly closed
                # paragraphs.  This ordering matters for the two unstable
                # occurrences that are also outside a strict paragraph.
                if paragraph is None:
                    audit["outside_strict_paragraph"] += 1
                    continue
                if not line.stable[index]:
                    audit["unstable"] += 1
                    continue
                it2a_ordinal = unique_forced_lcs_ordinal(
                    line.tokens, line.alternate["it2a"], index)
                rf1b_ordinal = unique_forced_lcs_ordinal(
                    line.tokens, line.alternate["rf1b"], index)
                if it2a_ordinal is None or rf1b_ordinal is None:
                    audit["not_unique_forced_lcs"] += 1
                    continue
                family = {carrier + member for member in TAILS}
                if sum(token in family for token in line.tokens) != 1:
                    audit["not_own_family_singleton"] += 1
                    continue
                preliminary.append((carrier, tail, surface, paragraph, line, index + 1,
                                    it2a_ordinal, rf1b_ordinal))
        preliminary.sort(key=lambda item: (natural_page_key(item[4].page),
                                           item[4].number, item[5], item[0], item[1]))
        events = []
        for ordinal, (carrier, tail, surface, paragraph, line, token_index,
                      it2a_ordinal, rf1b_ordinal) in enumerate(preliminary, 1):
            decks, status, raw_slot, free_length = canonical_features(
                paragraph, line, token_index, carrier, q152, end_classes)
            ed1_decks, _, _, ed1_free_length = canonical_features(
                paragraph, line, token_index, carrier, frozenset(q152 | ed1), end_classes)
            events.append(Event(f"{prefix}-E{ordinal:04d}", ordinal, carrier, tail,
                                surface, paragraph, line,
                                next(i for i, item in enumerate(paragraph.lines, 1)
                                     if item.locus == line.locus),
                                token_index, decks, ed1_decks, status, raw_slot,
                                free_length, ed1_free_length,
                                it2a_ordinal, rf1b_ordinal))
        funnel = {"raw_population_occurrences": raw_population_occurrences, **audit,
                  "eligible_events": len(events)}
        if raw_population_occurrences - sum(audit.values()) != len(events):
            raise AssertionError("event funnel is not exhaustive")
        return events, funnel

    # Event ids are assigned once on the complete ALL28 accepted stream.  The
    # CORE13 atlas is a subset and therefore intentionally retains gaps in the
    # G808-E#### sequence rather than being independently renumbered.
    core_probe, core_funnel = build_events(core13, "G808-CORE-PROBE")
    all_events, all_funnel = build_events(all28, "G808")
    core_events = [event for event in all_events if event.carrier in set(core13)]
    probe_keys = {(event.line.page, event.line.locus, event.token_index,
                   event.carrier, event.tail) for event in core_probe}
    core_keys = {(event.line.page, event.line.locus, event.token_index,
                  event.carrier, event.tail) for event in core_events}
    if probe_keys != core_keys:
        raise AssertionError("CORE13 subset identity drift inside ALL28 stream")

    def axis_funnel(population: Sequence[str], axis: str) -> dict[str, int]:
        selected_tails = {"ol", "eol"} if axis == "L" else {"edy", "eody"}
        permitted = set(population)
        values = Counter()
        for line in lines:
            paragraph = paragraph_by_locus.get(line.locus)
            for index, surface in enumerate(line.tokens):
                parsed = parse_relation(surface)
                if parsed is None or parsed[0] not in permitted or parsed[1] not in selected_tails:
                    continue
                carrier, _ = parsed
                values["raw"] += 1
                if paragraph is None:
                    values["outside"] += 1
                    continue
                values["strict"] += 1
                if not line.stable[index]:
                    continue
                values["stable"] += 1
                if not (unique_forced_lcs(line.tokens, line.alternate["it2a"], index)
                        and unique_forced_lcs(line.tokens, line.alternate["rf1b"], index)):
                    continue
                values["lcs"] += 1
                if sum(token in {carrier + tail for tail in TAILS} for token in line.tokens) != 1:
                    continue
                values["singleton"] += 1
        return dict(values)

    core_axis_funnels = {axis: axis_funnel(core13, axis) for axis in ("L", "DY")}
    all28_axis_funnels = {axis: axis_funnel(all28, axis) for axis in ("L", "DY")}
    if core_axis_funnels != {
        "L": {"raw": 1335, "outside": 7, "strict": 1328, "stable": 1169,
              "lcs": 1154, "singleton": 914},
        "DY": {"raw": 1834, "outside": 9, "strict": 1825, "stable": 1124,
               "lcs": 1063, "singleton": 863},
    }:
        raise AssertionError(f"CORE13 axis-funnel drift: {core_axis_funnels}")
    if all28_axis_funnels != {
        "L": {"raw": 1541, "outside": 8, "strict": 1533, "stable": 1352,
              "lcs": 1337, "singleton": 1091},
        "DY": {"raw": 2262, "outside": 12, "strict": 2250, "stable": 1395,
               "lcs": 1331, "singleton": 1117},
    }:
        raise AssertionError(f"ALL28 axis-funnel drift: {all28_axis_funnels}")
    if len(core_events) != EXPECTED["core_events"]:
        raise AssertionError(f"CORE13 event drift: {len(core_events)}")
    if Counter(event.tail for event in core_events) != Counter(
            {"ol": 641, "eol": 273, "edy": 715, "eody": 148}):
        raise AssertionError("CORE13 event cell-count drift")
    if len({event.paragraph.paragraph_id for event in core_events}) != EXPECTED["core_event_paragraphs"]:
        raise AssertionError("CORE13 event paragraph census drift")
    if len({event.line.locus for event in core_events}) != EXPECTED["core_event_lines"]:
        raise AssertionError("CORE13 event line census drift")
    if len({event.physical_folio for event in core_events}) != EXPECTED["core_event_folios"]:
        raise AssertionError("CORE13 event folio census drift")
    if len(all_events) != EXPECTED["all28_events"]:
        raise AssertionError("ALL28 event-count drift")
    if len({event.paragraph.paragraph_id for event in all_events}) != EXPECTED["all28_event_paragraphs"]:
        raise AssertionError("ALL28 event paragraph census drift")
    return {"raw_counts": raw_counts, "stable_counts": stable_counts,
            "stable_folios": stable_folios, "raw35": raw35, "all28": all28,
            "core13": core13, "thin9": thin9, "q152": q152,
            "ed1": ed1, "end_classes": end_classes, "core_events": core_events,
            "all28_events": all_events, "core_funnel": core_funnel,
            "all28_funnel": all_funnel, "core_axis_funnels": core_axis_funnels,
            "all28_axis_funnels": all28_axis_funnels}


def levenshtein(left: str, right: str) -> int:
    if len(left) < len(right):
        left, right = right, left
    previous = list(range(len(right) + 1))
    for i, a in enumerate(left, 1):
        current = [i]
        for j, b in enumerate(right, 1):
            current.append(min(current[-1] + 1, previous[j] + 1,
                               previous[j - 1] + int(a != b)))
        previous = current
    return previous[-1]


def read_model_specs() -> list[ModelSpec]:
    output = [ModelSpec(row["model_id"], row["source_axis"], row["target_axis"],
                        row["positive_source_tail"], row["negative_source_tail"],
                        row["positive_target_tail"], row["negative_target_tail"],
                        row["population"]) for row in read_tsv(MODEL_SPECS)]
    if len(output) != 8:
        raise AssertionError("relation-model spec cardinality drift")
    return output


def event_features(event: Event, deck: str, view: str,
                   ed1_quarantine: frozenset[str]) -> frozenset[str]:
    if view == "ED1":
        # Full canonical rebuild with Q152+ED1 has already updated topic,
        # template, target-free lengths/histograms, SLOT atoms and brackets.
        return event.feature_decks_ed1[deck]
    values = event.raw_slot if deck == "SLOT_HOLE" and view == "RAW_NEIGHBOUR" else event.feature_decks[deck]
    return values


def labels_for(events: Sequence[Event], positive: str, negative: str) -> dict[str, int]:
    return {event.event_id: int(event.tail == positive) for event in events
            if event.tail in {positive, negative}}


def vocabulary(training: Sequence[Event], deck: str, view: str,
               ed1_quarantine: frozenset[str]) -> tuple[str, ...]:
    carriers: defaultdict[str, set[str]] = defaultdict(set)
    folios: defaultdict[str, set[str]] = defaultdict(set)
    for event in training:
        for feature in event_features(event, deck, view, ed1_quarantine):
            carriers[feature].add(event.carrier)
            folios[feature].add(event.physical_folio)
    return tuple(sorted(feature for feature in carriers
                        if len(carriers[feature]) >= 2 and len(folios[feature]) >= 2))


def train_mnb(training: Sequence[Event], labels: Mapping[str, int], deck: str,
              view: str, ed1_quarantine: frozenset[str]) -> tuple[dict[str, float], int]:
    vocab = vocabulary(training, deck, view, ed1_quarantine)
    if not vocab:
        return {}, 0
    allowed = set(vocab)
    cell_counts = Counter((event.carrier, labels[event.event_id]) for event in training)
    counts = {0: Counter(), 1: Counter()}
    for event in training:
        label = labels[event.event_id]
        weight = 1.0 / cell_counts[event.carrier, label]
        used = event_features(event, deck, view, ed1_quarantine) & allowed
        for feature in used:
            counts[label][feature] += weight
    # Match the registered builder's deterministic floating-point route: its
    # class denominator is derived from the finished per-feature Counter.
    totals = {label: math.fsum(counts[label].values()) for label in (0, 1)}
    width = len(vocab)
    weights = {feature: math.log((counts[1][feature] + ALPHA) /
                                 (totals[1] + ALPHA * width))
                        - math.log((counts[0][feature] + ALPHA) /
                                   (totals[0] + ALPHA * width)) for feature in vocab}
    return weights, width


def train_union_mnb(training: Sequence[Event], labels: Mapping[str, int],
                    include_slot: bool, view: str = "PRIMARY",
                    ed1_quarantine: frozenset[str] = frozenset()) -> tuple[dict[str, float], int]:
    decks = DECKS if include_slot else DECKS[:3]
    decorated = {event.event_id: frozenset(deck + "::" + feature for deck in decks
                                           for feature in event_features(
                                               event, deck, view, ed1_quarantine))
                 for event in training}
    carriers: defaultdict[str, set[str]] = defaultdict(set)
    folios: defaultdict[str, set[str]] = defaultdict(set)
    for event in training:
        for feature in decorated[event.event_id]:
            carriers[feature].add(event.carrier)
            folios[feature].add(event.physical_folio)
    vocab = tuple(sorted(feature for feature in carriers
                         if len(carriers[feature]) >= 2 and len(folios[feature]) >= 2))
    if not vocab:
        return {}, 0
    allowed = set(vocab)
    cells = Counter((event.carrier, labels[event.event_id]) for event in training)
    counts = {0: Counter(), 1: Counter()}
    for event in training:
        label = labels[event.event_id]
        weight = 1.0 / cells[event.carrier, label]
        used = decorated[event.event_id] & allowed
        for feature in used:
            counts[label][feature] += weight
    totals = {label: math.fsum(counts[label].values()) for label in (0, 1)}
    width = len(vocab)
    return ({feature: math.log((counts[1][feature] + ALPHA) /
                               (totals[1] + ALPHA * width))
                      - math.log((counts[0][feature] + ALPHA) /
                                 (totals[0] + ALPHA * width)) for feature in vocab}, width)


def score(features: Iterable[str], weights: Mapping[str, float]) -> tuple[float, int]:
    values = [weights[feature] for feature in features if feature in weights]
    return (math.fsum(values) / len(values), len(values)) if values else (0.0, 0)


def auc(labels: Sequence[int], scores: Sequence[float]) -> float | None:
    positives = [value for label, value in zip(labels, scores) if label == 1]
    negatives = [value for label, value in zip(labels, scores) if label == 0]
    if not positives or not negatives:
        return None
    wins = math.fsum(1.0 if positive > negative else 0.5 if positive == negative else 0.0
                     for positive in positives for negative in negatives)
    return wins / (len(positives) * len(negatives))


def balanced_accuracy(labels: Sequence[int], scores: Sequence[float]) -> float | None:
    positives, negatives = sum(labels), len(labels) - sum(labels)
    if not positives or not negatives:
        return None
    pos = sum(1.0 if value > 0 else 0.5 if value == 0 else 0.0
              for label, value in zip(labels, scores) if label) / positives
    neg = sum(1.0 if value < 0 else 0.5 if value == 0 else 0.0
              for label, value in zip(labels, scores) if not label) / negatives
    return 0.5 * (pos + neg)


def log_loss(labels: Sequence[int], scores: Sequence[float]) -> float | None:
    if not labels:
        return None
    losses = []
    for label, value in zip(labels, scores):
        signed = value if label else -value
        losses.append(math.log1p(math.exp(-abs(signed))) + max(-signed, 0.0))
    return math.fsum(losses) / len(losses)


def carrier_class_log_loss(predictions: Sequence[Mapping[str, Any]], score_name: str,
                           labels: Sequence[int]) -> float | None:
    """Carrier-class weighted BCE, preserving the registered float route."""
    if not labels:
        return None
    cells = Counter((str(row["carrier"]), int(label))
                    for row, label in zip(predictions, labels))
    weighted = 0.0
    weights = 0.0
    for row, label in zip(predictions, labels):
        value = float(row[score_name])
        probability = 1.0 / (1.0 + math.exp(-max(-35.0, min(35.0, value))))
        loss = -(label * math.log(max(probability, 1e-15))
                 + (1 - label) * math.log(max(1.0 - probability, 1e-15)))
        weight = 1.0 / cells[(str(row["carrier"]), int(label))]
        weighted += weight * loss
        weights += weight
    return weighted / weights


def metric_bundle(predictions: Sequence[Mapping[str, Any]], score_name: str,
                  label_override: Mapping[str, int] | None = None) -> dict[str, Any]:
    labels = [int(label_override[row["event_id"]]) if label_override is not None
              else int(row["target_label"]) for row in predictions]
    scores = [float(row[score_name]) for row in predictions]
    by_carrier = {}
    for carrier in sorted({str(row["carrier"]) for row in predictions}):
        indices = [index for index, row in enumerate(predictions) if row["carrier"] == carrier]
        by_carrier[carrier] = auc([labels[index] for index in indices],
                                  [scores[index] for index in indices])
    defined = [value for value in by_carrier.values() if value is not None]
    return {"micro_auc": auc(labels, scores),
            "carrier_macro_auc": math.fsum(defined) / len(defined) if defined else None,
            "balanced_accuracy": balanced_accuracy(labels, scores),
            "log_loss": carrier_class_log_loss(predictions, score_name, labels),
            "micro_log_loss": log_loss(labels, scores), "carrier_auc": by_carrier,
            "carriers_above_half": sum(value is not None and value > 0.5
                                       for value in by_carrier.values()),
            "zero_votes": sum(value == 0 for value in scores)}


def conditional_auc(predictions: Sequence[Mapping[str, Any]], score_name: str,
                    label_override: Mapping[str, int] | None = None) -> dict[str, Any]:
    strata: defaultdict[tuple[str, str, str, str, int], list[Mapping[str, Any]]] = defaultdict(list)
    for row in predictions:
        strata[(str(row["carrier"]), str(row["section"]), str(row["language"]),
                str(row["hand"]), int(row["line_length_bin"]))].append(row)
    by_carrier_wins: Counter[str] = Counter()
    by_carrier_pairs: Counter[str] = Counter()
    by_carrier_cells: Counter[str] = Counter()
    for key, rows in strata.items():
        labels = [(label_override or {}).get(str(row["event_id"]), int(row["target_label"]))
                  for row in rows]
        positive = [row for row, label in zip(rows, labels) if label == 1]
        negative = [row for row, label in zip(rows, labels) if label == 0]
        if not positive or not negative:
            continue
        carrier = key[0]
        by_carrier_cells[carrier] += 1
        for left in positive:
            for right in negative:
                a, b = float(left[score_name]), float(right[score_name])
                by_carrier_wins[carrier] += 1.0 if a > b else 0.5 if a == b else 0.0
                by_carrier_pairs[carrier] += 1
    all_carriers = sorted({str(row["carrier"]) for row in predictions})
    carrier_auc = {carrier: (by_carrier_wins[carrier] / by_carrier_pairs[carrier]
                             if by_carrier_pairs[carrier] else None)
                   for carrier in all_carriers}
    defined = [value for value in carrier_auc.values() if value is not None]
    macro = math.fsum(defined) / len(defined) if defined else None
    wins = math.fsum(by_carrier_wins.values())
    pairs = sum(by_carrier_pairs.values())
    return {"auc": macro, "carrier_macro_auc": macro,
            "pooled_pair_auc": wins / pairs if pairs else None,
            "matched_pairs": int(pairs),
            "scoreable_strata": int(sum(by_carrier_cells.values())),
            "scoreable_carriers": len(defined),
            "carrier_auc": carrier_auc,
            "carrier_pair_count": {carrier: int(by_carrier_pairs[carrier])
                                   for carrier in all_carriers},
            "carrier_stratum_count": {carrier: int(by_carrier_cells[carrier])
                                      for carrier in all_carriers}}


def ed1_surface_set(events: Sequence[Event], q152: frozenset[str]) -> frozenset[str]:
    observed = {surface for event in events for deck in DECKS
                for feature in event.feature_decks[deck]
                for surface in [feature_surface(feature)] if surface is not None}
    return frozenset(surface for surface in observed
                     if any(levenshtein(surface, blocked) <= 1 for blocked in q152))


_FOLD_STATE: dict[str, Any] = {}


def score_fold_worker(key: tuple[str, str]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    state = _FOLD_STATE
    spec: ModelSpec = state["spec"]
    source: Sequence[Event] = state["source"]
    target: Sequence[Event] = state["target"]
    base_labels: Mapping[str, int] = state["base_labels"]
    target_labels: Mapping[str, int] = state["target_labels"]
    view, ed1 = state["view"], state["ed1"]
    union, auxiliary = state["union"], state["auxiliary"]
    source_label_flips = state["source_label_flips"]
    held_carrier, held_folio = key
    training = [event for event in source
                if event.carrier != held_carrier and event.physical_folio != held_folio]
    testing = sorted(
        (event for event in target
         if event.carrier == held_carrier and event.physical_folio == held_folio),
        key=lambda event: (natural_page_key(event.line.page), event.line.number,
                           event.token_index, event.event_id))
    train_labels = dict(base_labels)
    if source_label_flips is not None:
        flipped = source_label_flips.get(held_carrier, set())
        for event in training:
            if event.carrier in flipped:
                train_labels[event.event_id] = 1 - train_labels[event.event_id]
    if {train_labels[event.event_id] for event in training} != {0, 1}:
        raise AssertionError(f"unscoreable fold {spec.model_id}:{held_carrier}:{held_folio}")
    if any(event.carrier == held_carrier or event.physical_folio == held_folio
           for event in training):
        raise AssertionError("component/folio holdout leakage")
    if union:
        union_nuis = train_union_mnb(training, train_labels, False, view, ed1)
        union_aug = train_union_mnb(training, train_labels, True, view, ed1)
    else:
        deck_models = {deck: train_mnb(training, train_labels, deck, view, ed1)
                       for deck in DECKS}
        if auxiliary:
            auxiliary_models = {deck: train_mnb(training, train_labels, deck, view, ed1)
                                for deck in ("FORM_BASE", "POSITION", "MASK_STATUS", "RAW_SLOT")}
            union_nuis = train_union_mnb(training, train_labels, False, view, ed1)
            union_aug = train_union_mnb(training, train_labels, True, view, ed1)
    predictions = []
    for event in testing:
        row = {"event_id": event.event_id, "carrier": event.carrier,
               "physical_folio": event.physical_folio, "page": event.line.page,
               "locus": event.line.locus, "line_number": event.line.number,
               "token_index": event.token_index, "section": event.paragraph.section,
               "language": event.paragraph.language, "hand": event.paragraph.hand,
               "line_length_bin": event.line_length_bin,
               "target_label": target_labels[event.event_id], "target_tail": event.tail}
        if union:
            nf = frozenset(deck + "::" + feature for deck in DECKS[:3]
                           for feature in event_features(event, deck, view, ed1))
            af = nf | frozenset("SLOT_HOLE::" + feature
                                for feature in event_features(event, "SLOT_HOLE", view, ed1))
            row["nuisance_score"], row["nuisance_known"] = score(nf, union_nuis[0])
            row["augmented_score"], row["augmented_known"] = score(af, union_aug[0])
        else:
            for deck in DECKS:
                row[deck + "_score"], row[deck + "_known"] = score(
                    event_features(event, deck, view, ed1), deck_models[deck][0])
            row["nuisance_score"] = math.fsum(row[deck + "_score"] for deck in DECKS[:3])
            row["augmented_score"] = row["nuisance_score"] + row["SLOT_HOLE_score"]
            if auxiliary:
                for deck in ("FORM_BASE", "POSITION", "MASK_STATUS", "RAW_SLOT"):
                    row[deck + "_score"], row[deck + "_known"] = score(
                        event_features(event, deck, view, ed1), auxiliary_models[deck][0])
                nuisance_features = frozenset(
                    deck + "::" + feature for deck in DECKS[:3]
                    for feature in event_features(event, deck, view, ed1))
                augmented_features = nuisance_features | frozenset(
                    "SLOT_HOLE::" + feature
                    for feature in event_features(event, "SLOT_HOLE", view, ed1))
                row["union_nuisance_score"], row["union_nuisance_known"] = score(
                    nuisance_features, union_nuis[0])
                row["union_augmented_score"], row["union_augmented_known"] = score(
                    augmented_features, union_aug[0])
                row["nuisance_without_position_score"] = math.fsum((
                    row["TOPIC_score"], row["TEMPLATE_score"], row["FORM_BASE_score"]))
                row["nuisance_plus_mask_score"] = row["nuisance_score"] + row["MASK_STATUS_score"]
                row["augmented_raw_score"] = row["nuisance_score"] + row["RAW_SLOT_score"]
                for official, local in (("topic", "TOPIC"), ("template", "TEMPLATE"),
                                        ("form", "FORM_REGIME"), ("slot", "SLOT_HOLE"),
                                        ("form_base", "FORM_BASE"), ("position", "POSITION"),
                                        ("mask", "MASK_STATUS"), ("raw_slot", "RAW_SLOT")):
                    row[official + "_score"] = row[local + "_score"]
                    row[official + "_known"] = row[local + "_known"]
        for field in tuple(row):
            if field.endswith("_score"):
                row[field] = q12(float(row[field]))
        predictions.append(row)
    fold = {"held_carrier": held_carrier, "held_physical_folio": held_folio,
            "train_events": len(training), "test_events": len(testing),
            "train_carriers": len({event.carrier for event in training}),
            "train_folios": len({event.physical_folio for event in training}),
            "positive_train_events": sum(train_labels[event.event_id] for event in training),
            "negative_train_events": sum(1 - train_labels[event.event_id] for event in training)}
    if union:
        fold.update(vocab_nuisance=union_nuis[1], vocab_augmented=union_aug[1])
    else:
        fold.update({"vocab_" + deck: deck_models[deck][1] for deck in DECKS})
        if auxiliary:
            fold.update({"vocab_" + deck: auxiliary_models[deck][1]
                         for deck in ("FORM_BASE", "POSITION", "MASK_STATUS", "RAW_SLOT")})
            fold.update(vocab_union_nuisance=union_nuis[1],
                        vocab_union_augmented=union_aug[1])
    return predictions, fold


def score_model(spec: ModelSpec, events: Sequence[Event], q152: frozenset[str],
                view: str = "PRIMARY", source_label_flips: Mapping[str, set[str]] | None = None,
                union: bool = False, auxiliary: bool = True) -> dict[str, Any]:
    source = [event for event in events if event.tail in {spec.positive_source, spec.negative_source}]
    target = [event for event in events if event.tail in {spec.positive_target, spec.negative_target}]
    base_labels = labels_for(source, spec.positive_source, spec.negative_source)
    target_labels = labels_for(target, spec.positive_target, spec.negative_target)
    ed1 = ed1_surface_set(events, q152) if view == "ED1" else frozenset()
    predictions = []
    folds = []
    keys = sorted({(event.carrier, event.physical_folio) for event in target})
    expected_sizes = {
        "M01_L_TO_L": (914, 914, 569),
        "M02_DY_TO_DY": (863, 863, 394),
        "M03_L_TO_DY": (914, 863, 394),
        "M04_DY_TO_L": (863, 914, 569),
        "M05_L_TO_L_ALL28": (1091, 1091, 729),
        "M06_DY_TO_DY_ALL28": (1117, 1117, 577),
        "M07_L_TO_DY_ALL28": (1091, 1117, 577),
        "M08_DY_TO_L_ALL28": (1117, 1091, 729),
    }
    observed_sizes = (len(source), len(target), len(keys))
    if observed_sizes != expected_sizes[spec.model_id]:
        raise AssertionError(f"model capacity drift {spec.model_id}: {observed_sizes}")
    global _FOLD_STATE
    _FOLD_STATE = {"spec": spec, "source": source, "target": target,
                   "base_labels": base_labels, "target_labels": target_labels,
                   "view": view, "ed1": ed1, "union": union,
                   "auxiliary": auxiliary, "source_label_flips": source_label_flips}
    requested_workers = int(os.environ.get("GDT808_VALIDATOR_WORKERS", "32"))
    workers = max(1, min(requested_workers, len(keys), os.cpu_count() or 1))
    if workers == 1:
        outputs = [score_fold_worker(key) for key in keys]
    else:
        context = multiprocessing.get_context("fork")
        chunk = max(1, len(keys) // (workers * 4))
        with context.Pool(processes=workers) as pool:
            outputs = pool.map(score_fold_worker, keys, chunksize=chunk)
    _FOLD_STATE = {}
    for model_predictions, fold in outputs:
        predictions.extend(model_predictions)
        folds.append(fold)
    if len(predictions) != len(target):
        raise AssertionError(f"prediction coverage drift: {spec.model_id}")
    names = (("nuisance_score", "augmented_score") if union else
             tuple(deck + "_score" for deck in DECKS)
             + ("nuisance_score", "augmented_score")
             + (("union_nuisance_score", "union_augmented_score") if auxiliary else ()))
    metrics = {}
    for name in names:
        metrics[name] = metric_bundle(predictions, name)
        metrics[name]["conditional"] = conditional_auc(predictions, name)
    metrics["local_gain"] = (metrics["augmented_score"]["carrier_macro_auc"]
                             - metrics["nuisance_score"]["carrier_macro_auc"])
    metrics["log_loss_gain"] = (metrics["nuisance_score"]["log_loss"]
                                - metrics["augmented_score"]["log_loss"])
    a = metrics["augmented_score"]["conditional"]["auc"]
    n = metrics["nuisance_score"]["conditional"]["auc"]
    metrics["conditional_gain"] = a - n if a is not None and n is not None else None
    return {"spec": spec, "predictions": predictions, "folds": folds,
            "metrics": metrics, "source_events": len(source), "target_events": len(target)}


def rotate_target_labels(result: Mapping[str, Any]) -> list[dict[str, Any]]:
    predictions = list(result["predictions"])
    strata: defaultdict[tuple[str, str, str, str, int], list[Mapping[str, Any]]] = defaultdict(list)
    for row in predictions:
        strata[(str(row["carrier"]), str(row["section"]), str(row["language"]),
                str(row["hand"]), int(row["line_length_bin"]))].append(row)
    output = []
    for offset in range(1, 25):
        labels = {}
        moved = identities = 0
        for key in sorted(strata):
            rows = sorted(strata[key], key=lambda row: (
                natural_page_key(str(row["page"])), int(row["line_number"]),
                int(row["token_index"]), str(row["event_id"])))
            original = [int(row["target_label"]) for row in rows]
            shift = offset % len(rows)
            assigned = original[-shift:] + original[:-shift] if shift else original[:]
            for row, old, new in zip(rows, original, assigned):
                labels[str(row["event_id"])] = new
                moved += int(old != new)
                identities += int(old == new)
        nuisance = metric_bundle(predictions, "nuisance_score", labels)
        augmented = metric_bundle(predictions, "augmented_score", labels)
        slot = metric_bundle(predictions, "SLOT_HOLE_score", labels)
        conditional_nuisance = conditional_auc(predictions, "nuisance_score", labels)["auc"]
        conditional_augmented = conditional_auc(predictions, "augmented_score", labels)["auc"]
        changed_fraction = moved / len(predictions) if predictions else 0.0
        output.append({"offset": offset, "moved_labels": moved,
                       "identity_labels": identities,
                       "changed_fraction": changed_fraction,
                       "mobility_status": ("LOW_MOBILITY" if changed_fraction < 0.20
                                           else "ADEQUATE_MOBILITY"),
                       "nuisance_macro_auc": nuisance["carrier_macro_auc"],
                       "augmented_macro_auc": augmented["carrier_macro_auc"],
                       "slot_macro_auc": slot["carrier_macro_auc"],
                       "local_gain": augmented["carrier_macro_auc"] - nuisance["carrier_macro_auc"],
                       "conditional_local_gain": (
                           conditional_augmented - conditional_nuisance
                           if conditional_augmented is not None and conditional_nuisance is not None
                           else None)})
    return output


def carrier_flip_maps(population: Sequence[str]) -> list[dict[str, set[str]]]:
    result = []
    for rotation in range(12):
        mapping = {}
        for held in sorted(population):
            remaining = sorted(set(population) - {held})
            if len(remaining) != 12:
                raise AssertionError("carrier-sign null requires twelve source carriers")
            mapping[held] = {remaining[(rotation + offset) % 12] for offset in range(6)}
        result.append(mapping)
    return result


def contact_overlays(events: Sequence[Event], q152: frozenset[str]) -> dict[str, Any]:
    """Rebuild corrected exact overlay contacts; GDT757 remains audit-only."""
    by_location = {(event.line.page, event.line.locus, event.token_index): event for event in events}
    admitted_pages = sorted((row["page"] for row in read_tsv(ALLOWLIST)),
                            key=natural_page_key)
    contacts = {event.event_id: {"amount": False, "quality": False,
                                 "part": False, "formula_audit": False}
                for event in events}
    audit = Counter()
    g759_rows, g759_stats = guarded_query(
        G759, admitted_pages,
        ("page", "locus", "left_token_ordinal", "right_token_ordinal",
         "left_surface", "right_surface", "family"))
    for row in g759_rows:
        page, locus = row["page"], row["locus"]
        left, right = int(row["left_token_ordinal"]), int(row["right_token_ordinal"])
        endpoints = {row["left_surface"], row["right_surface"]}
        if endpoints & q152:
            audit["g759_q152_dropped"] += 1
            continue
        for index in (left - 2, left - 1, right + 1, right + 2):
            event = by_location.get((page, locus, index))
            if event is None or left <= event.token_index <= right:
                continue
            if physical_folio(page) != event.physical_folio:
                raise AssertionError("G759 physical-folio recomputation mismatch")
            distance = min(abs(event.token_index - left), abs(event.token_index - right))
            if distance not in (1, 2):
                continue
            family = row["family"]
            if family == "QUANTITY_VALUE":
                contacts[event.event_id]["amount"] = True
            elif family in {"PART_STATE", "PREPARATION_VALUE"}:
                contacts[event.event_id]["quality"] = True
    g768_rows, g768_stats = guarded_query(
        G768, admitted_pages,
        ("page", "locus", "token_index", "surface", "reader_exact"))
    for row in g768_rows:
        if row["reader_exact"] != "1":
            audit["g768_reader_inexact_dropped"] += 1
            continue
        page, locus, anchor = row["page"], row["locus"], int(row["token_index"])
        if row["surface"] in q152:
            audit["g768_q152_dropped"] += 1
            continue
        for index in (anchor - 2, anchor - 1, anchor + 1, anchor + 2):
            event = by_location.get((page, locus, index))
            if event is None or event.token_index == anchor:
                continue
            if physical_folio(page) != event.physical_folio:
                raise AssertionError("G768 physical-folio recomputation mismatch")
            contacts[event.event_id]["part"] = True
    g757_rows, g757_stats = guarded_query(
        G757, admitted_pages, ("page", "locus", "surface", "written_line_eva"))
    for row in g757_rows:
        page, locus = row["page"], row["locus"]
        line_tokens = tuple(row["written_line_eva"].split())
        positions = [index for index, surface in enumerate(line_tokens, 1)
                     if surface == row["surface"]]
        if positions != [1]:
            raise AssertionError(
                f"GDT757 opener must be the unique ordinal-one token: "
                f"{page}:{locus}:{positions}")
        anchor = positions[0]
        if row["surface"] in q152:
            audit["g757_q152_dropped"] += 1
            continue
        for index in (anchor - 2, anchor - 1, anchor + 1, anchor + 2):
            event = by_location.get((page, locus, index))
            if event is not None and event.token_index != anchor:
                contacts[event.event_id]["formula_audit"] = True

    def axis_stat(kind: str, negative: str, positive: str) -> dict[str, Any]:
        selected = [event for event in events if event.tail in {negative, positive}]
        values = Counter()
        folios = set()
        for event in selected:
            label = "positive" if event.tail == positive else "negative"
            hit = contacts[event.event_id][kind]
            values[label + "_contact"] += int(hit)
            values[label + "_no_contact"] += int(not hit)
            if hit:
                folios.add(event.physical_folio)
        total_contact = values["positive_contact"] + values["negative_contact"]
        if total_contact == 0:
            log_or = None
        else:
            log_or = math.log(((values["positive_contact"] + 0.5)
                               * (values["negative_no_contact"] + 0.5))
                              / ((values["positive_no_contact"] + 0.5)
                                 * (values["negative_contact"] + 0.5)))
        return {**values, "total_contact": total_contact,
                "contact_folios": len(folios), "log_or": log_or,
                "abs_log_or": abs(log_or) if log_or is not None else None}

    axes = {}
    for axis, negative, positive in (("L", "ol", "eol"), ("DY", "edy", "eody")):
        axes[axis] = {kind: axis_stat(kind, negative, positive)
                      for kind in ("amount", "quality", "part", "formula_audit")}
    expected_cells = {
        ("L", "amount"): (4, 269, 4, 637, 7),
        ("DY", "amount"): (4, 144, 1, 714, 4),
        ("L", "quality"): (0, 273, 0, 641, 0),
        ("DY", "quality"): (0, 148, 0, 715, 0),
        ("L", "part"): (10, 263, 59, 582, 48),
        ("DY", "part"): (5, 143, 11, 704, 10),
        ("L", "formula_audit"): (4, 269, 3, 638, 7),
        ("DY", "formula_audit"): (0, 148, 1, 714, 1),
    }
    for key, expected in expected_cells.items():
        values = axes[key[0]][key[1]]
        observed = (values.get("positive_contact", 0),
                    values.get("positive_no_contact", 0),
                    values.get("negative_contact", 0),
                    values.get("negative_no_contact", 0),
                    values.get("contact_folios", 0))
        if observed != expected:
            raise AssertionError(f"corrected contact census drift {key}: {observed} != {expected}")
    return {"event_contacts": contacts, "axis_stats": axes, "audit": dict(audit),
            "guarded_query_stats": {"g759": g759_stats, "g768": g768_stats,
                                    "g757": g757_stats}}


def model_decision(primary: Mapping[str, Any], all28: Mapping[str, Any],
                   union: Mapping[str, Any], target_nulls: Sequence[Mapping[str, Any]],
                   carrier_nulls: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    metrics = primary["metrics"]
    observed_gain = metrics["local_gain"]
    gain_rank = 1 + sum(float(row["local_gain"]) >= observed_gain for row in target_nulls)
    nuisance_auc = metrics["nuisance_score"]["carrier_macro_auc"]
    portability_rank = 1 + sum(float(row["nuisance_macro_auc"]) >= nuisance_auc for row in carrier_nulls)
    gates = {
        "augmented_macro_ge_060": metrics["augmented_score"]["carrier_macro_auc"] >= 0.60,
        "local_gain_ge_002": observed_gain >= 0.02,
        "positive_log_loss_gain": metrics["log_loss_gain"] > 0,
        "slot_carriers_above_half_ge_9": metrics["SLOT_HOLE_score"]["carriers_above_half"] >= 9,
        "conditional_gain_ge_002": metrics["conditional_gain"] is not None and metrics["conditional_gain"] >= 0.02,
        "target_null_rank_1": gain_rank == 1,
        "all28_augmented_ge_055": all28["metrics"]["augmented_score"]["carrier_macro_auc"] >= 0.55,
        "all28_positive_gain": all28["metrics"]["local_gain"] > 0,
        "union_positive_gain": union["metrics"]["local_gain"] > 0,
    }
    direction_gain = (gates["augmented_macro_ge_060"] and gates["local_gain_ge_002"]
                      and gates["positive_log_loss_gain"]
                      and gates["slot_carriers_above_half_ge_9"]
                      and gates["conditional_gain_ge_002"]
                      and gates["all28_augmented_ge_055"] and gates["all28_positive_gain"])
    if all(gates.values()):
        decision = "PORTABLE_LOCAL_SLOT_RELATION"
    elif direction_gain and (gain_rank in (2, 3)
                             or (gain_rank == 1 and not gates["union_positive_gain"])):
        decision = "PROVISIONAL_OR_SCORER_SENSITIVE_LOCAL_LEAD"
    else:
        record = {"nuisance_macro_ge_060": nuisance_auc >= 0.60,
                  "nuisance_carriers_above_half_ge_9": metrics["nuisance_score"]["carriers_above_half"] >= 9,
                  "all28_nuisance_ge_055": all28["metrics"]["nuisance_score"]["carrier_macro_auc"] >= 0.55,
                  "portability_rank_le_3": portability_rank <= 3,
                  "no_local_increment": observed_gain < 0.02}
        gates.update(record)
        decision = "PORTABLE_RECORD_OR_FORM_RELATION" if all(record.values()) else "NO_PORTABLE_RELATION_SIGNAL"
    return {"decision": decision, "gates": gates, "target_null_rank": gain_rank,
            "portability_null_rank": portability_rank}


def winning_contact_axis(overlays: Mapping[str, Any], kind: str) -> dict[str, Any]:
    candidates = []
    for axis in sorted(overlays["axis_stats"]):
        values = overlays["axis_stats"][axis][kind]
        absolute = values["abs_log_or"]
        # No-contact axes are ineligible rather than converted into a
        # half-count signal.  Lexical axis order resolves an exact tie.
        if absolute is not None:
            candidates.append((-float(absolute), axis, values))
    if not candidates:
        return {"axis": None, "abs_log_or": None, "contact_folios": 0}
    _, axis, values = min(candidates)
    return {"axis": axis, "abs_log_or": values["abs_log_or"],
            "contact_folios": values["contact_folios"]}


def registered_rival_metrics(models: Mapping[str, Mapping[str, Any]],
                             overlays: Mapping[str, Any],
                             populations: Mapping[str, Any]) -> dict[str, Any]:
    m01, m02 = models["M01_L_TO_L"], models["M02_DY_TO_DY"]
    m03, m04 = models["M03_L_TO_DY"], models["M04_DY_TO_L"]

    def macro(model: Mapping[str, Any], score_name: str) -> float:
        return float(model["metrics"][score_name]["carrier_macro_auc"])

    amount = winning_contact_axis(overlays, "amount")
    quality = winning_contact_axis(overlays, "quality")
    part = winning_contact_axis(overlays, "part")
    reversed_count = max(
        sum(value is not None and value < 0.5
            for value in model["metrics"]["augmented_score"]["carrier_auc"].values())
        for model in (m01, m02))
    stable_l = (populations["core_axis_funnels"]["L"]["stable"]
                / populations["core_axis_funnels"]["L"]["strict"])
    stable_dy = (populations["core_axis_funnels"]["DY"]["stable"]
                 / populations["core_axis_funnels"]["DY"]["strict"])
    topic_or_form = [max(macro(model, "TOPIC_score"),
                         macro(model, "FORM_REGIME_score"))
                     for model in (m01, m02)]
    local_gains = [float(model["metrics"]["local_gain"]) for model in (m01, m02)]
    within_nuisance = [macro(model, "nuisance_score") for model in (m01, m02)]
    cross_slot = [macro(model, "SLOT_HOLE_score") for model in (m03, m04)]
    cross_nuisance = [macro(model, "nuisance_score") for model in (m03, m04)]
    within_form = [macro(model, "FORM_REGIME_score") for model in (m01, m02)]
    return {
        "MIN_WITHIN_NUISANCE_MACRO_AUC": min(within_nuisance),
        "DY_LOCAL_GAIN": local_gains[1], "L_LOCAL_GAIN": local_gains[0],
        "MIN_CROSS_SLOT_MACRO_AUC": min(cross_slot),
        "MIN_LOCAL_GAIN": min(local_gains),
        "QUALITY_VALUE_CONTACT_ABS_LOG_OR": quality["abs_log_or"],
        "QUALITY_VALUE_CONTACT_FOLIOS": quality["contact_folios"],
        "PART_FORM_CONTACT_ABS_LOG_OR": part["abs_log_or"],
        "PART_FORM_CONTACT_FOLIOS": part["contact_folios"],
        "AMOUNT_CONTACT_ABS_LOG_OR": amount["abs_log_or"],
        "AMOUNT_CONTACT_FOLIOS": amount["contact_folios"],
        "MIN_WITHIN_TOPIC_OR_FORM_MACRO_AUC": min(topic_or_form),
        "MAX_LOCAL_GAIN": max(local_gains),
        "MAX_CROSS_NUISANCE_INVERTED_AUC": max(1.0 - value for value in cross_nuisance),
        "MIN_WITHIN_FORM_MACRO_AUC": min(within_form),
        "MIN_TARGET_READER_STABLE_RATE": min(stable_l, stable_dy),
        "MAX_WITHIN_NUISANCE_MACRO_AUC": max(within_nuisance),
        "MAX_REVERSED_CARRIER_COUNT": reversed_count,
    }


def historical_rival_scores(metrics: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = read_tsv(RIVAL_SPECS)
    awarded: defaultdict[str, int] = defaultdict(int)
    evidence: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        value = metrics[row["metric"]]
        threshold = float(row["threshold"])
        passed = (value is not None and
                  ((row["operator"] == "GE" and float(value) >= threshold)
                   or (row["operator"] == "LT" and float(value) < threshold)))
        points = int(row["points"]) if passed else 0
        awarded[row["rival_id"]] += points
        evidence[row["rival_id"]].append({"evidence_id": row["evidence_id"],
                                           "metric": row["metric"], "value": value,
                                           "pass": passed, "points": points})
    theories = {row["rival_id"]: row for row in read_tsv(SEMANTIC_SPECS)}
    output = [{"rival_id": rival, "points": awarded[rival],
               "working_theory": theories[rival]["working_theory"],
               "semantic_credit": 0, "evidence": evidence[rival]}
              for rival in theories]
    output.sort(key=lambda row: (-int(row["points"]), str(row["rival_id"])))
    for rank, row in enumerate(output, 1):
        row["rank"] = rank
    return output


def joint_topology(decisions: Mapping[str, Mapping[str, Any]],
                   models: Mapping[str, Mapping[str, Any]]) -> str:
    transfers = [decisions[model_id]["decision"] != "NO_PORTABLE_RELATION_SIGNAL"
                 for model_id in ("M01_L_TO_L", "M02_DY_TO_DY")]
    cross_slot = [models[model_id]["metrics"]["SLOT_HOLE_score"]["carrier_macro_auc"]
                  for model_id in ("M03_L_TO_DY", "M04_DY_TO_L")]
    cross_nuisance = [models[model_id]["metrics"]["nuisance_score"]["carrier_macro_auc"]
                      for model_id in ("M03_L_TO_DY", "M04_DY_TO_L")]
    if all(transfers) and min(cross_slot) >= 0.60:
        return "SHARED_EXPANDED_SIDE_DIRECTION"
    if all(transfers) and max(cross_slot) <= 0.40:
        return "OPPOSED_LOCAL_RELATIONS"
    if all(transfers) and max(cross_nuisance) <= 0.40:
        return "OPPOSED_REGISTER_DIRECTIONS__NO_SHARED_SLOT_INFERENCE"
    if all(transfers):
        return "TWO_DISTINCT_OR_AXIS_BOUND_RELATIONS"
    if any(transfers):
        return "ONE_AXIS_TRANSFERABLE_RELATION"
    return "NO_PORTABLE_RELATION_SIGNAL"


def artifact_snapshot() -> dict[str, tuple[int, int, str]]:
    return {path.name: (path.stat().st_size, path.stat().st_mtime_ns, sha256(path))
            for path in ART.glob("*") if path.is_file() and path.name != "VALIDATION.json"}


def builder_active() -> bool:
    completed = subprocess.run(["ps", "-eo", "pid=,args="], check=True, text=True,
                               stdout=subprocess.PIPE)
    needle = "gdt808_exact_relation_slot_residual_bridge/src/run.py"
    for line in completed.stdout.splitlines():
        pid_text, _, command = line.strip().partition(" ")
        try:
            pid = int(pid_text)
        except ValueError:
            continue
        if pid != os.getpid() and needle in command:
            return True
    return False


def manifest_checks() -> list[str]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("experiment_id") != "GDT808":
        raise AssertionError("manifest experiment id drift")
    if manifest.get("sealed_data") != {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}:
        raise AssertionError("manifest sealed-data gate drift")
    seen = set()
    for item in manifest.get("inputs", []):
        path = ROOT / item["path"]
        if not path.is_file():
            raise AssertionError(f"manifest input absent: {item['path']}")
        seen.add(item["path"])
        if path.resolve() in MIXED_PATHS:
            if item["sha256"] != MIXED_MANIFEST_HASHES[item["path"]]:
                raise AssertionError(f"mixed manifest lock drift: {item['path']}")
        elif sha256(path) != item["sha256"]:
            raise AssertionError(f"manifest input hash drift: {item['path']}")
    if len(seen) != len(manifest.get("inputs", [])):
        raise AssertionError("duplicate manifest input path")
    required = {rel(path) for path in (ALLOWLIST, LINES_RAW, CROSS_RAW, TOKENS_RAW,
                G759, G768, G757, MODEL_SPECS, CORE_SPECS, QUARANTINE_SPECS,
                IMPLEMENTATION_SPECS, FEATURE_SPECS, CONTROL_SPECS, RIVAL_SPECS,
                SEMANTIC_SPECS, HISTORICAL_SPECS)}
    if not required <= seen:
        raise AssertionError(f"manifest missing locks: {sorted(required - seen)}")
    registered_outputs = {item["path"]: item for item in manifest.get("outputs", [])}
    for runtime_path in (SRC / "run.py", SRC / "validate.py"):
        path_text = rel(runtime_path)
        item = registered_outputs.get(path_text)
        if item is None or item.get("sha256") != sha256(runtime_path):
            raise AssertionError(f"manifest runtime implementation hash drift: {path_text}")
    if len(read_tsv(FEATURE_SPECS)) != 4 or len(read_tsv(CONTROL_SPECS)) != 8:
        raise AssertionError("feature/control spec cardinality drift")
    implementation = {row["key"]: row["value"] for row in read_tsv(IMPLEMENTATION_SPECS)}
    required_values = {"TAIL_PARSE_ORDER": "eody|eol|edy|ol", "NB_ALPHA": "0.5",
                       "FEATURE_SUPPORT": "at least two training carriers and two training physical folios",
                       "DECK_EVENT_SCORE": "mean known-feature log likelihood ratio; all-OOV equals zero",
                       "LABEL_NULL_DIRECTION": "destination i receives source i-k modulo stratum size; inherited GDT807 right rotation",
                       "FIXED_LOGLOSS": "carrier-class-weighted binary cross entropy of sigmoid(sum of relevant mean-LLR deck scores)",
                       "SLOT_ED1_ORDER": "delete ED1 atomic neighbours before building L2_L1 L1_R1 R1_R2 brackets"}
    if any(implementation.get(key) != value for key, value in required_values.items()):
        raise AssertionError("implementation-spec lock drift")
    return ["manifest_identity_and_sealed_gate", "manifest_input_locks",
            "manifest_runtime_implementation_locks",
            "registered_specs_replayed"]


def tsv_with_schema(path: Path) -> tuple[tuple[str, ...], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fields = tuple(reader.fieldnames or ())
        if not fields or len(fields) != len(set(fields)):
            raise AssertionError(f"invalid TSV schema: {path.name}")
        rows = list(reader)
    return fields, rows


def expect_int(value: Any, expected: int, context: str) -> None:
    try:
        observed = int(value)
    except (TypeError, ValueError) as error:
        raise AssertionError(f"non-integer {context}: {value!r}") from error
    if observed != expected:
        raise AssertionError(f"integer mismatch {context}: {observed} != {expected}")


def expect_float(value: Any, expected: float | None, context: str,
                 tolerance: float = FLOAT_TOL) -> None:
    if expected is None:
        if str(value) not in {"NA", "", "None", "null"}:
            raise AssertionError(f"expected NA {context}, observed {value!r}")
        return
    try:
        observed = float(value)
    except (TypeError, ValueError) as error:
        raise AssertionError(f"non-numeric {context}: {value!r}") from error
    if not math.isfinite(observed) or abs(observed - expected) > tolerance:
        raise AssertionError(f"numeric mismatch {context}: {observed} != {expected}")


def expect_f12(value: Any, expected: float | None, context: str) -> None:
    wanted = "NA" if expected is None else f"{expected:.12g}"
    if str(value) != wanted:
        raise AssertionError(f"serialized f12 mismatch {context}: {value!r} != {wanted!r}")


def pipe_values(values: Iterable[Any]) -> str:
    material = [str(value) for value in values if str(value)]
    return "|".join(material) if material else "NONE"


def feature_fingerprint(values: Iterable[str]) -> tuple[int, str]:
    material = sorted(values)
    payload = "\n".join(material).encode("utf-8")
    return len(material), hashlib.sha256(payload).hexdigest()


def compare_event_atlas(rows: Sequence[Mapping[str, str]], rebuilt: Mapping[str, Any]) -> None:
    events = rebuilt["populations"]["core_events"]
    if len(rows) != len(events):
        raise AssertionError(f"event-atlas row drift: {len(rows)} != {len(events)}")
    official = {row["event_id"]: row for row in rows}
    if len(official) != len(rows) or set(official) != {event.event_id for event in events}:
        raise AssertionError("complete CORE13 event-id identity mismatch")
    for event in events:
        row = official[event.event_id]
        feature_packets = {
            "topic": event.feature_decks["TOPIC"],
            "template": event.feature_decks["TEMPLATE"],
            "form_regime": event.feature_decks["FORM_REGIME"],
            "slot_hole": event.feature_decks["SLOT_HOLE"],
            "mask_status_audit": event.feature_decks["MASK_STATUS"],
            "raw_slot_sensitivity": event.feature_decks["RAW_SLOT"],
        }
        fingerprints = {
            field + "_feature_" + suffix: str(value)
            for field, packet in feature_packets.items()
            for suffix, value in zip(("count", "sha256"), feature_fingerprint(packet))
        }
        scalar = {
            "carrier": event.carrier, "tail": event.tail,
            "axis": "L" if event.tail in {"ol", "eol"} else "DY",
            "expanded_label": str(int(event.tail in {"eol", "eody"})),
            "surface": event.surface, "page": event.line.page,
            "physical_folio": event.physical_folio,
            "paragraph_id": event.paragraph.paragraph_id, "locus": event.line.locus,
            "line_number": str(event.line.number), "token_index": str(event.token_index),
            "line_token_count": str(len(event.line.tokens)),
            "paragraph_line_index": str(event.line_index),
            "section": event.paragraph.section, "language": event.paragraph.language,
            "hand": event.paragraph.hand, "rank_stable_all_three": "1",
            "it2a_unique_forced_exact_ordinal": str(event.it2a_ordinal),
            "rf1b_unique_forced_exact_ordinal": str(event.rf1b_ordinal),
            "own_family_raw_line_count": "1",
            "targetfree_line_length_bin": str(event.line_length_bin),
            **fingerprints,
            "semantic_credit": "0", "component_export_credit": "0",
        }
        for field, expected in scalar.items():
            if str(row.get(field, "")) != expected:
                raise AssertionError(
                    f"event mismatch {event.event_id}:{field}: {row.get(field)!r} != {expected!r}")


def compare_carrier_census(rows: Sequence[Mapping[str, str]], rebuilt: Mapping[str, Any]) -> None:
    populations = rebuilt["populations"]
    raw_counts, stable_counts = populations["raw_counts"], populations["stable_counts"]
    folios = populations["stable_folios"]
    carriers = sorted(raw_counts)
    official = {row["carrier"]: row for row in rows}
    if len(official) != len(rows) or set(official) != set(carriers):
        raise AssertionError("complete parsed-carrier census identity mismatch")
    all_events = populations["all28_events"]
    for carrier in carriers:
        row = official[carrier]
        expect_int(row["raw_complete"], int(carrier in populations["raw35"]), f"carrier:{carrier}:raw")
        expect_int(row["all28_stable_complete"], int(carrier in populations["all28"]), f"carrier:{carrier}:all28")
        expect_int(row["core13"], int(carrier in populations["core13"]), f"carrier:{carrier}:core13")
        expected_eligible = sum(event.carrier == carrier for event in all_events)
        expect_int(row["eligible_events"], expected_eligible, f"carrier:{carrier}:eligible")
        for tail in TAILS:
            expect_int(row[f"{tail}_raw_occurrences"], raw_counts[carrier][tail],
                       f"carrier:{carrier}:{tail}:raw")
            expect_int(row[f"{tail}_stable_occurrences"], stable_counts[carrier][tail],
                       f"carrier:{carrier}:{tail}:stable")
            expect_int(row[f"{tail}_stable_physical_folios"], len(folios[carrier, tail]),
                       f"carrier:{carrier}:{tail}:folios")
            expect_int(row[f"{tail}_eligible_events"],
                       sum(event.carrier == carrier and event.tail == tail for event in all_events),
                       f"carrier:{carrier}:{tail}:eligible")
        expect_int(row["semantic_credit"], 0, f"carrier:{carrier}:semantic")
        expect_int(row["component_export_credit"], 0, f"carrier:{carrier}:component")


def compare_q152(rows: Sequence[Mapping[str, str]], rebuilt: Mapping[str, Any]) -> None:
    populations = rebuilt["populations"]
    q152, main = set(populations["q152"]), {
        carrier + tail for carrier in populations["raw35"] for tail in TAILS}
    thin = {carrier + tail for carrier in populations["thin9"] for tail in THIN_TAILS}
    official = {row["surface"]: row for row in rows}
    if len(rows) != 152 or set(official) != q152:
        raise AssertionError("Q152 exact surface identity mismatch")
    for surface in sorted(q152):
        row = official[surface]
        for field, expected in (("raw35_four_cell_member", int(surface in main)),
                                ("thin9_pair_member", int(surface in thin)),
                                ("deduplicated_overlap6", int(surface in main & thin)),
                                ("substring_rule", 0), ("semantic_credit", 0),
                                ("component_export_credit", 0)):
            expect_int(row[field], expected, f"q152:{surface}:{field}")
        if row["quarantine_rule"] != "EXACT_COMPLETE_SURFACE_ONLY":
            raise AssertionError(f"Q152 rule drift: {surface}")


def compare_implementation_clarifications(rows: Sequence[Mapping[str, str]]) -> None:
    expected = [
        ("FORM_REGIME_POSITION", "Position geometry is primary FORM_REGIME and separately audited; FORM_BASE omits it.", "PRIMARY_AND_AUDIT"),
        ("HISTOGRAM_SCOPE", "Word-length and end-class buckets are separate for target-free focal line and strict paragraph.", "PRIMARY"),
        ("CONDITIONAL_AGGREGATION", "Same-stratum pairs pool within carrier, then carrier concordances macro-average; pooled-all-pair result is audit only.", "PRIMARY"),
        ("UNION_SUPPORT", "Union MNB uses the same two-carrier and two-physical-folio support gate.", "REQUIRED_SENSITIVITY"),
        ("LEARNED_CONTROL_SUPPORT", "cheol and otal are descriptive class-carrier identities for support/cell weighting; only physical folio is held.", "CALIBRATION_ONLY"),
        ("OVERLAY_SELF_EXCLUSION", "Exact page+locus+ordinal join; nonzero outside-span distance; every overlay surface Q152-clean; winning-axis folios coupled.", "TOPOLOGY_ONLY"),
        ("READER_STABILITY", "Minimum strict parsed CORE13 axis stable rate is measured before stable/LCS/singleton filters.", "TOPOLOGY_ONLY"),
        ("SOURCE_LOCK_TIMING", "Manifest inputs plus registered builder/validator hashes are verified before corpus loading or model fitting.", "REQUIRED"),
        ("GDT388_PACKET", "Nineteen same-page distinct-locus formal pairs must fail only as formally accessed nonvisual evidence.", "AUDIT_ONLY"),
    ]
    observed = [(row["issue"], row["resolution"], row["selection_credit"])
                for row in rows]
    if observed != expected:
        raise AssertionError("implementation-clarification contract mismatch")


def compare_guarded_query_stats(rows: Sequence[Mapping[str, str]], rebuilt: Mapping[str, Any]) -> None:
    source_stats = rebuilt["source_census"]["guarded_queries"]
    overlay_stats = rebuilt["contact_overlays"]["guarded_query_stats"]
    definitions = [
        ("ZL3B_LINES_179", LINES_RAW,
         ("page", "locus", "line_number", "section", "language", "hand",
          "paragraph_start", "paragraph_end", "token_count", "eva_clean"),
         source_stats["lines"]),
        ("ZL3B_TOKENS_179", TOKENS_RAW,
         ("page", "locus", "token_index", "eva", "section", "language", "hand"),
         source_stats["tokens"]),
        ("CROSS_READER_LINES_179", CROSS_RAW,
         ("page", "locus", "all_three_present", "all_present_exact", "zl3b_clean",
          "it2a_clean", "rf1b_clean"), source_stats["cross"]),
        ("gdt759_overlay", G759,
         ("page", "locus", "left_token_ordinal", "right_token_ordinal",
          "left_surface", "right_surface", "family"), overlay_stats["g759"]),
        ("gdt768_overlay", G768,
         ("page", "locus", "token_index", "surface", "reader_exact"),
         overlay_stats["g768"]),
        ("gdt757_overlay", G757,
         ("page", "locus", "surface", "written_line_eva"), overlay_stats["g757"]),
    ]
    expected_ids = {item[0] for item in definitions}
    official = {row["query_id"]: row for row in rows}
    if len(rows) != len(official) or set(official) != expected_ids:
        raise AssertionError("guarded-query-stat identity/cardinality mismatch")
    for query_id, path, columns, stats in definitions:
        row = official[query_id]
        exact = {"source_path": rel(path), "selector_column": "page",
                 "output_columns": ",".join(columns),
                 "forbidden_prefixes": "f84|f84r"}
        for field, expected in exact.items():
            if row[field] != expected:
                raise AssertionError(f"guarded-query metadata mismatch {query_id}:{field}")
        for field, expected in (("allowed_value_count", 179),
                                ("selected_rows", int(stats["selected"])),
                                ("skipped_forbidden_rows", int(stats["skipped_forbidden"])),
                                ("skipped_not_allowed_rows", int(stats["skipped_not_allowed"])),
                                ("query_returncode", 0)):
            expect_int(row[field], expected, f"guarded-query:{query_id}:{field}")


def compare_source_census(rows: Sequence[Mapping[str, str]], rebuilt: Mapping[str, Any]) -> None:
    populations, source = rebuilt["populations"], rebuilt["source_census"]
    official = {(row["scope"], row["item"]): row for row in rows}
    base = {
        ("ALLOWLIST", "selectors"): (179, 179, "PASS"),
        ("GUARDED_SOURCE", "lines"): (4137, 4137, "PASS"),
        ("GUARDED_SOURCE", "tokens"): (32339, 32339, "PASS"),
        ("STRICT", "paragraphs"): (665, 665, "PASS"),
        ("STRICT", "lines"): (3807, 3807, "PASS"),
        ("STRICT", "tokens"): (31938, 31938, "PASS"),
        ("CORE13", "eligible_events"): (1777, 1777, "PASS"),
        ("ALL28", "eligible_events"): (2208, 2208, "PASS"),
        ("Q152", "exact_surfaces"): (152, 152, "PASS"),
        ("ED1", "additional_observed_surfaces"): (len(populations["ed1"]), None, "AUDIT"),
    }
    funnel_keys = {(population, axis + "_FILTER_FUNNEL")
                   for population in ("CORE13", "ALL28") for axis in ("L", "DY")}
    if len(official) != len(rows) or set(official) != set(base) | funnel_keys or len(rows) != 14:
        raise AssertionError("source-census exact fourteen-cell identity mismatch")
    extended = SOURCE_CENSUS_FIELDS[5:]
    for key, (count, expected, status) in base.items():
        if key not in official:
            raise AssertionError(f"source census cell absent: {key}")
        row = official[key]
        expect_int(row["count"], count, f"source-census:{key}:count")
        if expected is not None:
            expect_int(row["expected"], expected, f"source-census:{key}:expected")
        elif row["expected"] != "NA":
            raise AssertionError(f"source-census expected marker drift: {key}")
        if row["status"] != status:
            raise AssertionError(f"source-census status drift: {key}")
        if any(row[field] != "" for field in extended):
            raise AssertionError(f"source-census base row has unexpected funnel values: {key}")
    paragraph_by_locus = {line.locus: paragraph for paragraph in rebuilt["paragraphs"]
                          for line in paragraph.lines}
    for population, funnels_name, events_name in (("CORE13", "core_axis_funnels", "core_events"),
                                                   ("ALL28", "all28_axis_funnels", "all28_events")):
        events = populations[events_name]
        admitted_carriers = set(populations["core13"] if population == "CORE13"
                                else populations["all28"])
        for axis in ("L", "DY"):
            key = (population, axis + "_FILTER_FUNNEL")
            if key not in official:
                raise AssertionError(f"source funnel absent: {key}")
            row, values = official[key], populations[funnels_name][axis]
            expect_int(row["count"], values["singleton"], f"source-funnel:{key}:count")
            expect_int(row["expected"], values["singleton"], f"source-funnel:{key}:expected")
            if row["status"] != "PASS":
                raise AssertionError(f"source-funnel status drift: {key}")
            for field, source_field in (("raw_parsed", "raw"), ("outside_strict", "outside"),
                                        ("strict_parsed", "strict"), ("rank_stable", "stable"),
                                        ("unique_forced_lcs", "lcs"),
                                        ("own_family_singleton", "singleton")):
                expect_int(row[field], values[source_field], f"source-funnel:{key}:{field}")
            expect_f12(row["rank_stable_rate_strict_prefilter"],
                         values["stable"] / values["strict"], f"source-funnel:{key}:stable-rate")
            selected = [event for event in events
                        if ("L" if event.tail in {"ol", "eol"} else "DY") == axis]
            expect_int(row["accepted_paragraphs"],
                       len({event.paragraph.paragraph_id for event in selected}),
                       f"source-funnel:{key}:paragraphs")
            expect_int(row["accepted_focal_lines"],
                       len({(event.line.page, event.line.locus) for event in selected}),
                       f"source-funnel:{key}:lines")
            allowed_tails = {"ol", "eol"} if axis == "L" else {"edy", "eody"}
            strict_folios = {
                physical_folio(line.page)
                for line in rebuilt["lines"] if line.locus in paragraph_by_locus
                for surface in line.tokens
                for parsed in [parse_relation(surface)]
                if parsed is not None and parsed[0] in admitted_carriers
                and parsed[1] in allowed_tails
            }
            expect_int(row["strict_candidate_physical_folios"], len(strict_folios),
                       f"source-funnel:{key}:strict-folios")
    if source["allowlist_selectors"] != 179:
        raise AssertionError("independent guarded source census internal drift")


def compare_held_predictions(rows: Sequence[Mapping[str, str]], rebuilt: Mapping[str, Any]) -> None:
    independent = {(model_id, row["event_id"]): row
                   for model_id, result in rebuilt["models"].items()
                   for row in result["predictions"]}
    official = {(row["model_id"], row["event_id"]): row for row in rows}
    if len(official) != len(rows) or set(official) != set(independent):
        raise AssertionError(
            f"held-prediction identity mismatch: official={len(official)} independent={len(independent)}")
    float_fields = ("topic_score", "template_score", "form_score", "slot_score",
                    "union_nuisance_score", "union_augmented_score", "form_base_score",
                    "position_score", "mask_score", "raw_slot_score", "nuisance_score",
                    "augmented_score", "nuisance_without_position_score",
                    "nuisance_plus_mask_score", "augmented_raw_score")
    known_fields = ("topic_known", "template_known", "form_known", "slot_known",
                    "union_nuisance_known", "union_augmented_known", "form_base_known",
                    "position_known", "mask_known", "raw_slot_known")
    specs = {spec.model_id: spec for spec in read_model_specs()}
    event_maps = {
        "CORE13": {event.event_id: event for event in rebuilt["populations"]["core_events"]},
        "ALL28": {event.event_id: event for event in rebuilt["populations"]["all28_events"]},
    }
    for key, expected in independent.items():
        row, spec = official[key], specs[key[0]]
        exact = {
            "prediction_id": f"{key[0]}:{key[1]}", "population": spec.population,
            "source_axis": spec.source_axis, "target_axis": spec.target_axis,
            "carrier": expected["carrier"], "target_tail": expected["target_tail"],
            "true_label": str(expected["target_label"]), "page": expected["page"],
            "physical_folio": expected["physical_folio"], "locus": expected["locus"],
            "line_number": str(expected["line_number"]),
            "token_index": str(expected["token_index"]), "section": expected["section"],
            "language": expected["language"], "hand": expected["hand"],
            "targetfree_line_length_bin": str(expected["line_length_bin"]), "variant": "EXACT",
        }
        event = event_maps[spec.population][key[1]]
        exact["paragraph_id"] = event.paragraph.paragraph_id
        for field, value in exact.items():
            if str(row.get(field, "")) != str(value):
                raise AssertionError(f"prediction metadata mismatch {key}:{field}")
        for field in float_fields:
            expect_f12(row[field], float(expected[field]), f"prediction:{key}:{field}")
        for field in known_fields:
            expect_int(row[field], int(expected[field]), f"prediction:{key}:{field}")


def compare_feature_capacity(rows: Sequence[Mapping[str, str]], rebuilt: Mapping[str, Any]) -> None:
    deck_map = {"TOPIC": "TOPIC", "TEMPLATE": "TEMPLATE",
                "FORM_REGIME": "FORM_REGIME", "SLOT_HOLE": "SLOT_HOLE",
                "RAW_SLOT": "RAW_SLOT", "POSITION": "POSITION",
                "MASK_STATUS": "MASK_STATUS"}
    official = {(row["population"], row["deck_id"]): row for row in rows}
    expected_keys = {(population, deck) for population in ("CORE13", "ALL28")
                     for deck in deck_map}
    if len(rows) != 14 or set(official) != expected_keys:
        raise AssertionError("feature-capacity 2x7 identity mismatch")
    for population, events_name in (("CORE13", "core_events"), ("ALL28", "all28_events")):
        events = rebuilt["populations"][events_name]
        for deck, local in deck_map.items():
            row = official[population, deck]
            packets = [event.feature_decks[local] for event in events]
            types = {feature for packet in packets for feature in packet}
            carriers: defaultdict[str, set[str]] = defaultdict(set)
            folios: defaultdict[str, set[str]] = defaultdict(set)
            for event, packet in zip(events, packets):
                for feature in packet:
                    carriers[feature].add(event.carrier)
                    folios[feature].add(event.physical_folio)
            supported = {feature for feature in types
                         if len(carriers[feature]) >= 2 and len(folios[feature]) >= 2}
            values = [len(packet) for packet in packets]
            for field, expected in (("events", len(events)),
                                    ("nonempty_events", sum(value > 0 for value in values)),
                                    ("empty_events", sum(value == 0 for value in values)),
                                    ("feature_types", len(types)),
                                    ("global_two_carrier_two_folio_supported_types", len(supported)),
                                    ("max_features_per_event", max(values, default=0))):
                expect_int(row[field], expected, f"feature-capacity:{population}:{deck}:{field}")
            expect_f12(row["mean_features_per_event"], math.fsum(values) / len(values),
                         f"feature-capacity:{population}:{deck}:mean")
            if row["feature_value"] != "BINARY_PRESENCE":
                raise AssertionError(f"feature-value drift: {population}:{deck}")


def compare_folds(rows: Sequence[Mapping[str, str]], rebuilt: Mapping[str, Any]) -> None:
    official = {(row["model_id"], row["held_carrier"], row["held_physical_folio"]): row
                for row in rows}
    expected = {(model_id, str(fold["held_carrier"]), str(fold["held_physical_folio"])): fold
                for model_id, result in rebuilt["models"].items() for fold in result["folds"]}
    if len(rows) != len(official) or set(official) != set(expected):
        raise AssertionError(f"held-fold identity mismatch: {len(rows)} != {len(expected)}")
    specs = {spec.model_id: spec for spec in read_model_specs()}
    for key, fold in expected.items():
        row, spec = official[key], specs[key[0]]
        tests = [prediction for prediction in rebuilt["models"][key[0]]["predictions"]
                 if prediction["carrier"] == key[1]
                 and prediction["physical_folio"] == key[2]]
        exact = {"population": spec.population, "source_axis": spec.source_axis,
                 "target_axis": spec.target_axis, "train_events": fold["train_events"],
                 "train_positive_events": fold["positive_train_events"],
                 "train_negative_events": fold["negative_train_events"],
                 "train_carriers": fold["train_carriers"],
                 "train_physical_folios": fold["train_folios"],
                 "test_events": fold["test_events"],
                 "test_positive_events": sum(int(item["target_label"]) for item in tests),
                 "test_negative_events": sum(1 - int(item["target_label"]) for item in tests),
                 "carrier_excluded": 1, "physical_folio_excluded": 1,
                 "topic_vocabulary": fold["vocab_TOPIC"],
                 "template_vocabulary": fold["vocab_TEMPLATE"],
                 "form_vocabulary": fold["vocab_FORM_REGIME"],
                 "slot_vocabulary": fold["vocab_SLOT_HOLE"],
                 "union_nuisance_vocabulary": fold["vocab_union_nuisance"],
                 "union_augmented_vocabulary": fold["vocab_union_augmented"],
                 "fold_scoreable": 1}
        for field, value in exact.items():
            if isinstance(value, int):
                expect_int(row[field], value, f"fold:{key}:{field}")
            elif row[field] != value:
                raise AssertionError(f"fold metadata mismatch {key}:{field}")


SUMMARY_CHANNELS = {
    "TOPIC": "TOPIC_score", "TEMPLATE": "TEMPLATE_score",
    "FORM_REGIME": "FORM_REGIME_score", "SLOT_HOLE": "SLOT_HOLE_score",
    "NUISANCE": "nuisance_score", "AUGMENTED": "augmented_score",
    "UNION_NUISANCE": "union_nuisance_score",
    "UNION_AUGMENTED": "union_augmented_score",
}


def compare_model_summary(rows: Sequence[Mapping[str, str]], rebuilt: Mapping[str, Any]) -> None:
    official = {(row["model_id"], row["score_channel"]): row for row in rows}
    expected_keys = {(model_id, channel) for model_id in rebuilt["models"]
                     for channel in SUMMARY_CHANNELS}
    if len(rows) != len(official) or set(official) != expected_keys:
        raise AssertionError("complete 8x8 model-summary identity mismatch")
    specs = {spec.model_id: spec for spec in read_model_specs()}
    for (model_id, channel), row in official.items():
        result, spec = rebuilt["models"][model_id], specs[model_id]
        metric = result["metrics"][SUMMARY_CHANNELS[channel]]
        labels = [int(item["target_label"]) for item in result["predictions"]]
        exact = {"population": spec.population, "source_axis": spec.source_axis,
                 "target_axis": spec.target_axis, "events": len(labels),
                 "positive_events": sum(labels), "negative_events": len(labels) - sum(labels),
                 "carriers_scored": len([x for x in metric["carrier_auc"].values()
                                         if x is not None]),
                 "carriers_auc_above_half": metric["carriers_above_half"],
                 "carriers_auc_below_half": sum(x is not None and x < .5
                                                for x in metric["carrier_auc"].values()),
                 "post_score_sign_flip": 0, "semantic_credit": 0,
                 "component_export_credit": 0}
        for field, value in exact.items():
            if isinstance(value, int):
                expect_int(row[field], value, f"summary:{model_id}:{channel}:{field}")
            elif row[field] != value:
                raise AssertionError(f"summary metadata mismatch {model_id}:{channel}:{field}")
        for field, value in (("micro_auc", metric["micro_auc"]),
                             ("carrier_macro_auc", metric["carrier_macro_auc"]),
                             ("balanced_accuracy", metric["balanced_accuracy"]),
                             ("balanced_log_loss", metric["log_loss"])):
            expect_f12(row[field], value, f"summary:{model_id}:{channel}:{field}")


def compare_score_subset(rows: Sequence[Mapping[str, str]],
                         models: Mapping[str, Mapping[str, Any]], context: str) -> None:
    official = {(row["model_id"], row["score_channel"]): row for row in rows}
    expected_keys = {(model_id, channel) for model_id in models for channel in SUMMARY_CHANNELS}
    if len(rows) != len(official) or set(official) != expected_keys:
        raise AssertionError(f"{context} score-summary identity mismatch")
    specs = {spec.model_id: spec for spec in read_model_specs()}
    for (model_id, channel), row in official.items():
        result, metric, spec = (models[model_id],
                                models[model_id]["metrics"][SUMMARY_CHANNELS[channel]],
                                specs[model_id])
        labels = [int(item["target_label"]) for item in result["predictions"]]
        for field, expected in (("events", len(labels)), ("positive_events", sum(labels)),
                                ("negative_events", len(labels) - sum(labels)),
                                ("carriers_scored", sum(value is not None
                                                        for value in metric["carrier_auc"].values())),
                                ("carriers_auc_above_half", metric["carriers_above_half"]),
                                ("carriers_auc_below_half", sum(value is not None and value < .5
                                                                for value in metric["carrier_auc"].values()))):
            expect_int(row[field], expected, f"{context}:{model_id}:{channel}:{field}")
        if row["population"] != spec.population or row["source_axis"] != spec.source_axis \
                or row["target_axis"] != spec.target_axis:
            raise AssertionError(f"{context} model metadata mismatch: {model_id}:{channel}")
        for field, expected in (("post_score_sign_flip", 0), ("semantic_credit", 0),
                                ("component_export_credit", 0)):
            expect_int(row[field], expected, f"{context}:{model_id}:{channel}:{field}")
        for field, expected in (("micro_auc", metric["micro_auc"]),
                                ("carrier_macro_auc", metric["carrier_macro_auc"]),
                                ("balanced_accuracy", metric["balanced_accuracy"]),
                                ("balanced_log_loss", metric["log_loss"])):
            expect_f12(row[field], expected, f"{context}:{model_id}:{channel}:{field}")


def compare_ablation_rows(rows: Sequence[Mapping[str, str]], rebuilt: Mapping[str, Any]) -> None:
    channels = {"SLOT_STABLE_ONLY": "slot_score", "SLOT_RAW_ONLY": "raw_slot_score",
                "POSITION_ONLY": "position_score", "MASK_STATUS_ONLY": "mask_score",
                "FORM_WITHOUT_POSITION": "form_base_score",
                "FORM_REGIME_PRIMARY": "form_score",
                "NUISANCE_WITHOUT_POSITION": "nuisance_without_position_score",
                "NUISANCE_PRIMARY": "nuisance_score",
                "NUISANCE_PLUS_MASK": "nuisance_plus_mask_score",
                "AUGMENTED_STABLE": "augmented_score", "AUGMENTED_RAW": "augmented_raw_score"}
    official = {(row["model_id"], row["audit_channel"]): row for row in rows}
    expected_keys = {(model_id, channel) for model_id in ("M01_L_TO_L", "M02_DY_TO_DY")
                     for channel in channels}
    if len(rows) != 22 or set(official) != expected_keys:
        raise AssertionError("position/mask/slot ablation identity mismatch")
    for (model_id, channel), row in official.items():
        predictions = rebuilt["models"][model_id]["predictions"]
        metric = metric_bundle(predictions, channels[channel])
        nuisance = rebuilt["models"][model_id]["metrics"]["nuisance_score"]["carrier_macro_auc"]
        expect_int(row["events"], len(predictions), f"ablation:{model_id}:{channel}:events")
        for field, value in (("micro_auc", metric["micro_auc"]),
                             ("carrier_macro_auc", metric["carrier_macro_auc"]),
                             ("balanced_accuracy", metric["balanced_accuracy"]),
                             ("balanced_log_loss", metric["log_loss"]),
                             ("increment_over_primary_nuisance_macro_auc",
                             metric["carrier_macro_auc"] - nuisance)):
            expect_f12(row[field], value, f"ablation:{model_id}:{channel}:{field}")
        expected_credit = ("PRIMARY" if channel in {
            "SLOT_STABLE_ONLY", "AUGMENTED_STABLE", "NUISANCE_PRIMARY"}
                           else "AUDIT_ONLY")
        if row["selection_credit"] != expected_credit:
            raise AssertionError(f"ablation selection-credit drift: {model_id}:{channel}")


def compare_carrier_directions(rows: Sequence[Mapping[str, str]], rebuilt: Mapping[str, Any]) -> None:
    channel_fields = {"NUISANCE": "nuisance_score", "SLOT_HOLE": "slot_score",
                      "AUGMENTED": "augmented_score",
                      "UNION_AUGMENTED": "union_augmented_score"}
    official = {(row["model_id"], row["carrier"], row["score_channel"]): row for row in rows}
    expected_keys = {(model_id, carrier, channel)
                     for model_id, result in rebuilt["models"].items()
                     for carrier in {str(item["carrier"]) for item in result["predictions"]}
                     for channel in channel_fields}
    if len(rows) != len(official) or set(official) != expected_keys:
        raise AssertionError("carrier-direction diagnostic identity mismatch")
    specs = {spec.model_id: spec for spec in read_model_specs()}
    for (model_id, carrier, channel), row in official.items():
        subset = [item for item in rebuilt["models"][model_id]["predictions"]
                  if item["carrier"] == carrier]
        metric = metric_bundle(subset, channel_fields[channel])
        value = metric["micro_auc"]
        direction = ("EXPANDED" if value is not None and value > .5 else
                     "BASE" if value is not None and value < .5 else "TIE_OR_UNSCORABLE")
        for field, expected in (("events", len(subset)),
                                ("positive_events", sum(int(item["target_label"]) for item in subset)),
                                ("negative_events", sum(1 - int(item["target_label"]) for item in subset))):
            expect_int(row[field], expected, f"carrier-direction:{model_id}:{carrier}:{field}")
        expect_f12(row["auc"], value, f"carrier-direction:{model_id}:{carrier}:{channel}:auc")
        if row["direction"] != direction or row["population"] != specs[model_id].population:
            raise AssertionError(f"carrier direction/metadata mismatch: {model_id}:{carrier}:{channel}")
        if row["semantic_credit"] != "0" or row["component_export_credit"] != "0":
            raise AssertionError(f"carrier direction credit drift: {model_id}:{carrier}:{channel}")


def compare_conditional_rows(rows: Sequence[Mapping[str, str]], rebuilt: Mapping[str, Any]) -> None:
    channels = {"NUISANCE": "nuisance_score", "SLOT_HOLE": "slot_score",
                "AUGMENTED": "augmented_score"}
    if any(row["row_type"] not in {"SUMMARY", "CARRIER", "STRATUM"} for row in rows):
        raise AssertionError("unknown conditional-concordance row type")
    summaries = {(row["model_id"], row["score_channel"]): row for row in rows
                 if row["row_type"] == "SUMMARY"}
    expected_summary = {(model_id, channel) for model_id in rebuilt["models"] for channel in channels}
    if set(summaries) != expected_summary or len(summaries) != 24:
        raise AssertionError("conditional summary identity mismatch")
    carriers = {(row["model_id"], row["score_channel"], row["carrier"]): row
                for row in rows if row["row_type"] == "CARRIER"}
    expected_carriers = {(model_id, channel, carrier)
                         for model_id, result in rebuilt["models"].items()
                         for channel in channels
                         for carrier in {str(item["carrier"]) for item in result["predictions"]}}
    if set(carriers) != expected_carriers or len(carriers) != len(expected_carriers):
        raise AssertionError("conditional all-carrier identity mismatch")
    strata = {(row["model_id"], row["score_channel"], row["carrier"], row["section"],
               row["language"], row["hand"], row["targetfree_line_length_bin"]): row
              for row in rows if row["row_type"] == "STRATUM"}
    if len(strata) != sum(row["row_type"] == "STRATUM" for row in rows):
        raise AssertionError("duplicate conditional-concordance stratum")
    expected_strata = set()
    for model_id, result in rebuilt["models"].items():
        predictions = result["predictions"]
        for channel, field in channels.items():
            metric = conditional_auc(predictions, field)
            summary = summaries[model_id, channel]
            expect_int(summary["events"], len(predictions), f"conditional:{model_id}:{channel}:events")
            expect_int(summary["positive_events"], sum(int(row["target_label"]) for row in predictions),
                       f"conditional:{model_id}:{channel}:positive")
            expect_int(summary["negative_events"], sum(1 - int(row["target_label"]) for row in predictions),
                       f"conditional:{model_id}:{channel}:negative")
            expect_int(summary["comparable_pairs"], metric["matched_pairs"],
                       f"conditional:{model_id}:{channel}:pairs")
            expect_f12(summary["concordance"], metric["auc"],
                       f"conditional:{model_id}:{channel}:macro")
            expect_f12(summary["pooled_pair_concordance_audit"], metric["pooled_pair_auc"],
                       f"conditional:{model_id}:{channel}:pooled")
            if any(summary[name] != "ALL" for name in (
                    "carrier", "section", "language", "hand",
                    "targetfree_line_length_bin")):
                raise AssertionError(f"conditional summary ALL metadata drift: {model_id}:{channel}")
            for carrier in sorted(metric["carrier_auc"]):
                row = carriers[model_id, channel, carrier]
                subset = [item for item in predictions if item["carrier"] == carrier]
                expect_int(row["events"], len(subset),
                           f"conditional-carrier:{model_id}:{channel}:{carrier}:events")
                expect_int(row["positive_events"], sum(int(item["target_label"]) for item in subset),
                           f"conditional-carrier:{model_id}:{channel}:{carrier}:positive")
                expect_int(row["negative_events"], sum(1 - int(item["target_label"]) for item in subset),
                           f"conditional-carrier:{model_id}:{channel}:{carrier}:negative")
                expect_int(row["comparable_pairs"], metric["carrier_pair_count"][carrier],
                           f"conditional-carrier:{model_id}:{channel}:{carrier}:pairs")
                expect_f12(row["concordance"], metric["carrier_auc"][carrier],
                             f"conditional-carrier:{model_id}:{channel}:{carrier}:auc")
                expect_f12(row["pooled_pair_concordance_audit"],
                             metric["carrier_auc"][carrier],
                             f"conditional-carrier:{model_id}:{channel}:{carrier}:pooled")
                if any(row[name] != "ALL" for name in (
                        "section", "language", "hand", "targetfree_line_length_bin")):
                    raise AssertionError(
                        f"conditional carrier ALL metadata drift: {model_id}:{channel}:{carrier}")
            groups: defaultdict[tuple[str, str, str, str, int], list[Mapping[str, Any]]] = defaultdict(list)
            for prediction in predictions:
                groups[(str(prediction["carrier"]), str(prediction["section"]),
                        str(prediction["language"]), str(prediction["hand"]),
                        int(prediction["line_length_bin"]))].append(prediction)
            for key, values in sorted(groups.items()):
                positives = [item for item in values if int(item["target_label"]) == 1]
                negatives = [item for item in values if int(item["target_label"]) == 0]
                pairs = len(positives) * len(negatives)
                if not pairs:
                    continue
                artifact_key = (model_id, channel, key[0], key[1], key[2], key[3], str(key[4]))
                expected_strata.add(artifact_key)
                row = strata.get(artifact_key)
                if row is None:
                    raise AssertionError(f"conditional stratum absent: {artifact_key}")
                wins = math.fsum(
                    1.0 if float(positive[field]) > float(negative[field])
                    else 0.5 if float(positive[field]) == float(negative[field]) else 0.0
                    for positive in positives for negative in negatives)
                for name, expected in (("events", len(values)),
                                       ("positive_events", len(positives)),
                                       ("negative_events", len(negatives)),
                                       ("comparable_pairs", pairs)):
                    expect_int(row[name], expected,
                               f"conditional-stratum:{artifact_key}:{name}")
                expect_f12(row["concordance"], wins / pairs,
                             f"conditional-stratum:{artifact_key}:concordance")
                if row["pooled_pair_concordance_audit"] != "NA":
                    raise AssertionError(f"conditional stratum pooled marker drift: {artifact_key}")
    if set(strata) != expected_strata:
        raise AssertionError(
            f"conditional exact stratum identity mismatch: {len(strata)} != {len(expected_strata)}")
    if len(rows) != len(summaries) + len(carriers) + len(strata):
        raise AssertionError("conditional row accounting mismatch")


def compare_null_scores(rows: Sequence[Mapping[str, str]], rebuilt: Mapping[str, Any]) -> None:
    official = {(row["model_id"], row["null_family"], row["null_id"]): row for row in rows}
    expected_keys = {
        (model_id, family, null_id)
        for model_id in ("M01_L_TO_L", "M02_DY_TO_DY")
        for family, identifiers in (
            ("C01_TARGET_LABEL_ROTATION", tuple(f"K{k:02d}" for k in range(1, 25))),
            ("C02_CARRIER_SIGN_ROTATION", tuple(f"R{k:02d}" for k in range(12))),
            ("OBSERVED", ("OBSERVED_PRIMARY",)), ("RANK", ("EXACT_RANKS",)))
        for null_id in identifiers
    }
    if len(official) != len(rows) or len(rows) != 76 or set(official) != expected_keys:
        raise AssertionError(f"null-score identity/cardinality drift: {len(rows)}")
    for model_id in ("M01_L_TO_L", "M02_DY_TO_DY"):
        for expected in rebuilt["target_nulls"][model_id]:
            key = (model_id, "C01_TARGET_LABEL_ROTATION", f"K{expected['offset']:02d}")
            row = official[key]
            for field, value in (("carrier_macro_auc", expected["augmented_macro_auc"]),
                                 ("nuisance_carrier_macro_auc", expected["nuisance_macro_auc"]),
                                 ("slot_carrier_macro_auc", expected["slot_macro_auc"]),
                                 ("local_gain", expected["local_gain"]),
                                 ("conditional_local_gain", expected["conditional_local_gain"]),
                                 ("changed_fraction", expected["changed_fraction"])):
                expect_f12(row[field], value, f"target-null:{key}:{field}")
            expect_int(row["changed_labels"], expected["moved_labels"], f"target-null:{key}:moved")
            warning = "LOW_MOBILITY" if expected["changed_fraction"] < .20 else "NONE"
            if (row["mobility_warning"] != warning or row["observed_reference"] != "0"
                    or row["ties_count_against_target"] != "1"):
                raise AssertionError(f"target-null mobility mismatch: {key}")
        for expected in rebuilt["carrier_nulls"][model_id]:
            key = (model_id, "C02_CARRIER_SIGN_ROTATION", f"R{expected['rotation']:02d}")
            row = official[key]
            expect_f12(row["carrier_macro_auc"], expected["nuisance_macro_auc"],
                         f"carrier-null:{key}:auc")
            expect_f12(row["nuisance_carrier_macro_auc"], expected["nuisance_macro_auc"],
                         f"carrier-null:{key}:nuisance")
            for field in ("slot_carrier_macro_auc", "local_gain",
                          "conditional_local_gain", "changed_labels", "changed_fraction"):
                if row[field] != "NA":
                    raise AssertionError(f"carrier-null NA contract drift: {key}:{field}")
            if (row["mobility_warning"] != "NA" or row["observed_reference"] != "0"
                    or row["ties_count_against_target"] != "1"):
                raise AssertionError(f"carrier-null metadata mismatch: {key}")
        decision = rebuilt["decisions"][model_id]
        primary = rebuilt["models"][model_id]
        observed = official[(model_id, "OBSERVED", "OBSERVED_PRIMARY")]
        observed_values = {
            "carrier_macro_auc": primary["metrics"]["augmented_score"]["carrier_macro_auc"],
            "nuisance_carrier_macro_auc": primary["metrics"]["nuisance_score"]["carrier_macro_auc"],
            "slot_carrier_macro_auc": primary["metrics"]["SLOT_HOLE_score"]["carrier_macro_auc"],
            "local_gain": primary["metrics"]["local_gain"],
            "conditional_local_gain": primary["metrics"]["conditional_gain"],
            "changed_fraction": 0.0,
        }
        for field, value in observed_values.items():
            expect_f12(observed[field], value, f"observed-null:{model_id}:{field}")
        if (observed["changed_labels"] != "0" or observed["mobility_warning"] != "OBSERVED"
                or observed["observed_reference"] != "1"
                or observed["ties_count_against_target"] != "1"):
            raise AssertionError(f"observed-null metadata mismatch: {model_id}")
        rank = official[(model_id, "RANK", "EXACT_RANKS")]
        expect_int(rank["local_gain"], decision["target_null_rank"], f"rank:{model_id}:local")
        expect_int(rank["conditional_local_gain"], decision["portability_null_rank"],
                   f"rank:{model_id}:portability")
        for field in ("carrier_macro_auc", "nuisance_carrier_macro_auc",
                      "slot_carrier_macro_auc", "changed_labels", "changed_fraction"):
            if rank[field] != "NA":
                raise AssertionError(f"rank-null NA contract drift: {model_id}:{field}")
        if (rank["mobility_warning"] != "NA" or rank["observed_reference"] != "1"
                or rank["ties_count_against_target"] != "1"):
            raise AssertionError(f"rank-null metadata mismatch: {model_id}")


def compare_null_strata(rows: Sequence[Mapping[str, str]], rebuilt: Mapping[str, Any]) -> None:
    official = {(row["null_family"], row["null_id"], row["model_id"], row["carrier"],
                 row["section"], row["language"], row["hand"],
                 row["targetfree_line_length_bin"]): row for row in rows}
    if len(official) != len(rows):
        raise AssertionError("null-stratum audit keys are not unique")
    expected_keys = set()
    for model_id in ("M01_L_TO_L", "M02_DY_TO_DY"):
        predictions = rebuilt["models"][model_id]["predictions"]
        groups: defaultdict[tuple[str, str, str, str, int], list[Mapping[str, Any]]] = defaultdict(list)
        for row in predictions:
            groups[(str(row["carrier"]), str(row["section"]), str(row["language"]),
                    str(row["hand"]), int(row["line_length_bin"]))].append(row)
        target_axis = rebuilt["models"][model_id]["spec"].target_axis
        for offset in range(1, 25):
            for key, values in sorted(groups.items()):
                ordered = sorted(values, key=lambda row: (
                    natural_page_key(str(row["page"])), int(row["line_number"]),
                    int(row["token_index"]), str(row["event_id"])))
                labels = [int(row["target_label"]) for row in ordered]
                shift = offset % len(labels)
                assigned = labels[-shift:] + labels[:-shift] if shift else labels[:]
                moved = sum(left != right for left, right in zip(labels, assigned))
                artifact_key = ("C01_TARGET_LABEL_ROTATION", f"K{offset:02d}", model_id,
                                key[0], key[1], key[2], key[3], str(key[4]))
                expected_keys.add(artifact_key)
                row = official.get(artifact_key)
                if row is None:
                    raise AssertionError(f"target-null stratum absent: {artifact_key}")
                for field, expected in (("stratum_events", len(labels)),
                                        ("offset_mod_n", shift), ("moved_labels", moved),
                                        ("identity_labels", len(labels) - moved)):
                    expect_int(row[field], expected, f"null-stratum:{artifact_key}:{field}")
                if row["target_axis"] != target_axis or row["flipped_source_carriers"] != "NA":
                    raise AssertionError(f"target-null stratum metadata mismatch: {artifact_key}")
        flip_maps = carrier_flip_maps(rebuilt["populations"]["core13"])
        for rotation, mapping in enumerate(flip_maps):
            for carrier, flipped in sorted(mapping.items()):
                artifact_key = ("C02_CARRIER_SIGN_ROTATION", f"R{rotation:02d}", model_id,
                                carrier, "ALL", "ALL", "ALL", "ALL")
                expected_keys.add(artifact_key)
                row = official.get(artifact_key)
                if row is None:
                    raise AssertionError(f"carrier-null audit row absent: {artifact_key}")
                if row["flipped_source_carriers"] != pipe_values(sorted(flipped)):
                    raise AssertionError(f"carrier-null flipped block mismatch: {artifact_key}")
                expect_int(row["offset_mod_n"], rotation, f"carrier-null:{artifact_key}:rotation")
                if (row["target_axis"] != target_axis or row["stratum_events"] != "NA"
                        or row["moved_labels"] != "NA" or row["identity_labels"] != "NA"):
                    raise AssertionError(f"carrier-null audit metadata mismatch: {artifact_key}")
    if set(official) != expected_keys:
        raise AssertionError("null-stratum audit contains unknown or missing rows")


def expected_clean_contacts(rebuilt: Mapping[str, Any]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for official, local in (("AMOUNT", "amount"), ("QUALITY", "quality"),
                            ("PART", "part"), ("FORMULA", "formula_audit")):
        winner = winning_contact_axis(rebuilt["contact_overlays"], local)
        output[official + "_ABS_LOG_OR"] = winner["abs_log_or"]
        output[official + "_FOLIOS"] = winner["contact_folios"]
        output[official + "_WINNING_AXIS"] = winner["axis"] or "NONE"
    return output


def compare_historical_rivals(rows: Sequence[Mapping[str, str]], rebuilt: Mapping[str, Any]) -> None:
    allowed_types = {"RIVAL", "EVIDENCE_POINT", "HISTORICAL_SOURCE", "CONTACT_AUDIT"}
    if any(row["row_type"] not in allowed_types for row in rows):
        raise AssertionError("unknown historical-rival row type")
    theories = {row["rival_id"]: row for row in read_tsv(SEMANTIC_SPECS)}
    historical_specs = read_tsv(HISTORICAL_SPECS)
    rules = read_tsv(RIVAL_SPECS)
    role_map = {
        "R01_ATTRIBUTIVE_BINDING_PLUS_PREPARATION": {"QUALITY_DEGREE", "PART_FORM_SCOPE", "RECORD_CHANNEL"},
        "R02_SHARED_FORM_STAGE": {"RELATION_SUBSTITUTE", "PART_FORM_SCOPE"},
        "R03_QUALITY_OR_DEGREE": {"QUALITY_DEGREE"},
        "R04_PART_OR_FORM_SCOPE": {"PART_FORM_SCOPE"},
        "R05_GROUP_DOSE_OR_UNIT_VALUE": {"GROUP_DOSE", "UNIT_VALUE"},
        "R06_RECORD_CHANNEL": {"RECORD_CHANNEL"},
        "R07_BREVIGRAPH_OR_ORTHOGRAPHY": set(),
        "R08_CARRIER_BOUND_LEARNED_WHOLES": set(),
    }
    rivals = {row["rival_id"]: row for row in rows if row["row_type"] == "RIVAL"}
    if len(rivals) != 8:
        raise AssertionError("historical rival-card must contain eight ranked rivals")
    for expected in rebuilt["rival_scores"]:
        row = rivals[expected["rival_id"]]
        expect_int(row["rank"], expected["rank"], f"rival:{expected['rival_id']}:rank")
        expect_int(row["total_points"], expected["points"], f"rival:{expected['rival_id']}:points")
        expect_int(row["semantic_credit"], 0, f"rival:{expected['rival_id']}:semantic")
        rival_id = expected["rival_id"]
        relevant_sources = [source["source_id"] for source in historical_specs
                            if set(source["mapped_role"].split("|")) & role_map[rival_id]]
        evidence_labels = [f"{item['evidence_id']}={'PASS' if item['pass'] else 'FAIL'}"
                           for item in expected["evidence"]]
        exact = {"evidence_id": pipe_values(evidence_labels), "metric": "POINT_TOTAL",
                 "observed_value": str(expected["points"]), "operator": "DESC",
                 "threshold": "NA",
                 "points_available": str(sum(int(rule["points"]) for rule in rules
                                             if rule["rival_id"] == rival_id)),
                 "points_awarded": str(expected["points"]), "passed": "NA",
                 "working_theory": theories[rival_id]["working_theory"],
                 "historical_sources": pipe_values(relevant_sources),
                 "selection_credit": "REPLACEABLE_WORKING_RIVAL"}
        for field, value in exact.items():
            if row[field] != value:
                raise AssertionError(f"rival row mismatch {rival_id}:{field}")
    evidence_rows = {(row["rival_id"], row["evidence_id"]): row for row in rows
                     if row["row_type"] == "EVIDENCE_POINT"}
    if len(evidence_rows) != 20:
        raise AssertionError("historical rival evidence cardinality mismatch")
    for rule in rules:
        key = (rule["rival_id"], rule["evidence_id"])
        row, value = evidence_rows[key], rebuilt["rival_metrics"][rule["metric"]]
        expect_f12(row["observed_value"], value, f"rival-evidence:{key}:value")
        passed = (value is not None and
                  ((rule["operator"] == "GE" and float(value) >= float(rule["threshold"]))
                   or (rule["operator"] == "LT" and float(value) < float(rule["threshold"]))))
        expect_int(row["passed"], int(passed), f"rival-evidence:{key}:pass")
        expect_int(row["points_awarded"], int(rule["points"]) if passed else 0,
                   f"rival-evidence:{key}:points")
        exact = {"rank": "NA", "total_points": "NA", "metric": rule["metric"],
                 "operator": rule["operator"], "threshold": rule["threshold"],
                 "points_available": rule["points"],
                 "working_theory": theories[rule["rival_id"]]["working_theory"],
                 "historical_sources": "NONE", "selection_credit": "TOPOLOGY_ONLY",
                 "semantic_credit": "0"}
        for field, expected in exact.items():
            if row[field] != expected:
                raise AssertionError(f"rival evidence mismatch {key}:{field}")
    sources = [row for row in rows if row["row_type"] == "HISTORICAL_SOURCE"]
    if len(sources) != len(historical_specs):
        raise AssertionError("historical source-card cardinality mismatch")
    source_map = {row["evidence_id"]: row for row in sources}
    if set(source_map) != {row["source_id"] for row in historical_specs}:
        raise AssertionError("historical source identity mismatch")
    for source in historical_specs:
        row = source_map[source["source_id"]]
        exact = {"rival_id": "NONE", "rank": source["rank"], "total_points": "NA",
                 "metric": source["mapped_role"],
                 "observed_value": source["attested_architecture"], "operator": "NA",
                 "threshold": "NA", "points_available": "0", "points_awarded": "0",
                 "passed": "NA", "working_theory": source["fit_to_relation"],
                 "historical_sources": source["primary_url"],
                 "selection_credit": "TOPOLOGY_ONLY", "semantic_credit": "0"}
        for field, expected in exact.items():
            if row[field] != expected:
                raise AssertionError(f"historical source mismatch {source['source_id']}:{field}")
    contacts = {(row["evidence_id"].rsplit("_", 1)[0],
                 row["evidence_id"].rsplit("_", 1)[1]): row
                for row in rows if row["row_type"] == "CONTACT_AUDIT"}
    if len(contacts) != 8:
        raise AssertionError("clean contact audit cardinality mismatch")
    kind_map = {"AMOUNT": "amount", "QUALITY": "quality", "PART": "part",
                "FORMULA": "formula_audit"}
    for official_kind, local_kind in kind_map.items():
        for axis in ("L", "DY"):
            row = contacts[official_kind, axis]
            values = rebuilt["contact_overlays"]["axis_stats"][axis][local_kind]
            expect_f12(row["observed_value"], values["abs_log_or"],
                         f"contact-audit:{official_kind}:{axis}:logor")
            detail = json.loads(row["working_theory"])
            for field, expected in (("expanded_contact", values.get("positive_contact", 0)),
                                    ("expanded_no_contact", values.get("positive_no_contact", 0)),
                                    ("base_contact", values.get("negative_contact", 0)),
                                    ("base_no_contact", values.get("negative_no_contact", 0)),
                                    ("contact_physical_folios", values["contact_folios"])):
                expect_int(detail[field], expected, f"contact-audit:{official_kind}:{axis}:{field}")
            winner = winning_contact_axis(rebuilt["contact_overlays"], local_kind)
            expected_selection = "AUDIT_ONLY" if official_kind == "FORMULA" else "TOPOLOGY_ONLY"
            exact = {"rival_id": "NONE", "rank": "NA", "total_points": "NA",
                     "metric": "CLEAN_EXACT_ORDINAL_CONTACT", "operator": "NA",
                     "threshold": "NA", "points_available": "0", "points_awarded": "0",
                     "passed": "NA", "historical_sources": "NONE",
                     "selection_credit": expected_selection, "semantic_credit": "0"}
            for field, expected in exact.items():
                if row[field] != expected:
                    raise AssertionError(f"contact audit mismatch {official_kind}/{axis}:{field}")
            expected_detail = {
                "contact_kind": official_kind, "axis": axis,
                "expanded_contact": values.get("positive_contact", 0),
                "expanded_no_contact": values.get("positive_no_contact", 0),
                "base_contact": values.get("negative_contact", 0),
                "base_no_contact": values.get("negative_no_contact", 0),
                "haldane_log_or": ("NA" if values["log_or"] is None
                                    else f"{values['log_or']:.12g}"),
                "absolute_log_or": ("NA" if values["abs_log_or"] is None
                                     else f"{values['abs_log_or']:.12g}"),
                "contact_physical_folios": values["contact_folios"],
                "winning_axis": int(winner["axis"] == axis),
                "selection_credit": expected_selection,
            }
            if detail != expected_detail:
                raise AssertionError(f"contact audit JSON mismatch {official_kind}/{axis}")
    if len(rows) != len(rivals) + len(evidence_rows) + len(sources) + len(contacts):
        raise AssertionError("historical rival-card row accounting mismatch")


def independent_axis_card(model_id: str, all28_id: str,
                          rebuilt: Mapping[str, Any]) -> dict[str, Any]:
    result, all28 = rebuilt["models"][model_id], rebuilt["models"][all28_id]
    metrics = result["metrics"]
    nuisance = metrics["nuisance_score"]["carrier_macro_auc"]
    augmented = metrics["augmented_score"]["carrier_macro_auc"]
    all_nuisance = all28["metrics"]["nuisance_score"]["carrier_macro_auc"]
    all_augmented = all28["metrics"]["augmented_score"]["carrier_macro_auc"]
    conditional_gain = (metrics["augmented_score"]["conditional"]["auc"]
                        - metrics["nuisance_score"]["conditional"]["auc"])
    union_gain = (metrics["union_augmented_score"]["carrier_macro_auc"]
                  - metrics["union_nuisance_score"]["carrier_macro_auc"])
    direction_gates = (augmented >= .60 and augmented - nuisance >= .02
                       and metrics["log_loss_gain"] > 0
                       and metrics["SLOT_HOLE_score"]["carriers_above_half"] >= 9
                       and conditional_gain >= .02 and all_augmented >= .55
                       and all_augmented - all_nuisance > 0)
    decision = rebuilt["decisions"][model_id]
    return {"nuisance_macro_auc": nuisance, "augmented_macro_auc": augmented,
            "local_gain": augmented - nuisance,
            "fixed_logloss_gain": metrics["log_loss_gain"],
            "slot_carriers_above_half": metrics["SLOT_HOLE_score"]["carriers_above_half"],
            "conditional_gain": conditional_gain,
            "local_gain_rank_of_25": decision["target_null_rank"],
            "nuisance_rank_of_13": decision["portability_null_rank"],
            "all28_augmented_macro_auc": all_augmented,
            "all28_local_gain": all_augmented - all_nuisance,
            "union_local_gain": union_gain,
            "direction_gates_pass": int(direction_gates),
            "record_no_local_increment": int(augmented - nuisance < .02)}


def compare_structural_card(rows: Sequence[Mapping[str, str]], rebuilt: Mapping[str, Any]) -> None:
    official = {row["card_id"]: row for row in rows}
    if set(official) != {"L_AXIS", "DY_AXIS", "JOINT"} or len(rows) != 3:
        raise AssertionError("structural-card identity mismatch")
    leading = rebuilt["rival_scores"][0]["rival_id"]
    for card_id, model_id, all28_id in (("L_AXIS", "M01_L_TO_L", "M05_L_TO_L_ALL28"),
                                        ("DY_AXIS", "M02_DY_TO_DY", "M06_DY_TO_DY_ALL28")):
        row = official[card_id]
        expected_scope = "Xol::Xeol" if card_id == "L_AXIS" else "Xedy::Xeody"
        if row["decision"] != rebuilt["decisions"][model_id]["decision"]:
            raise AssertionError(f"structural axis decision mismatch: {card_id}")
        values = json.loads(row["metrics_json"])
        expected = independent_axis_card(model_id, all28_id, rebuilt)
        if set(values) != set(expected):
            raise AssertionError(f"structural metrics schema mismatch: {card_id}")
        for field, value in expected.items():
            if isinstance(value, int):
                expect_int(values[field], value, f"structural:{card_id}:{field}")
            else:
                expect_float(values[field], value, f"structural:{card_id}:{field}")
        if row["joint_topology"] != rebuilt["joint_topology"] or row["leading_historical_rival"] != leading:
            raise AssertionError(f"structural topology/rival mismatch: {card_id}")
        if (row["formal_scope"] != expected_scope
                or row["claim_ceiling"] != "FORMAL_RELATION_ONLY"
                or row["semantic_credit"] != "0" or row["renderer_credit"] != "0"):
            raise AssertionError(f"structural axis scope/credit mismatch: {card_id}")
    joint = official["JOINT"]
    if joint["decision"] != rebuilt["joint_topology"] or joint["joint_topology"] != rebuilt["joint_topology"]:
        raise AssertionError("joint structural topology mismatch")
    values = json.loads(joint["metrics_json"])
    if set(values) != set(rebuilt["rival_metrics"]):
        raise AssertionError("joint rival-metric schema mismatch")
    for field, expected in rebuilt["rival_metrics"].items():
        expect_float(values[field], expected, f"structural:JOINT:{field}")
    if (joint["formal_scope"] != "L_AND_DY_RECTANGLE"
            or joint["leading_historical_rival"] != leading
            or joint["claim_ceiling"] != "ZERO_LEXEMES_ZERO_COMPONENT_EXPORT"
            or joint["semantic_credit"] != "0" or joint["renderer_credit"] != "0"):
        raise AssertionError("joint structural scope/credit mismatch")


def pair_control_events(rebuilt: Mapping[str, Any],
                        pairs: Mapping[str, tuple[str, str]],
                        prefix: str, learned: bool = False) -> list[Event]:
    paragraph_by_locus = {line.locus: paragraph for paragraph in rebuilt["paragraphs"]
                          for line in paragraph.lines}
    surface_map = {surface: (carrier, label) for carrier, pair in pairs.items()
                   for label, surface in enumerate((pair[1], pair[0]))}
    preliminary = []
    for line in rebuilt["lines"]:
        paragraph = paragraph_by_locus.get(line.locus)
        if paragraph is None:
            continue
        for index, surface in enumerate(line.tokens):
            if surface not in surface_map or not line.stable[index]:
                continue
            carrier, label = surface_map[surface]
            if sum(token in pairs[carrier] for token in line.tokens) != 1:
                continue
            it2a = unique_forced_lcs_ordinal(line.tokens, line.alternate["it2a"], index)
            rf1b = unique_forced_lcs_ordinal(line.tokens, line.alternate["rf1b"], index)
            if it2a is None or rf1b is None:
                continue
            preliminary.append((carrier, surface, label, paragraph, line, index + 1,
                                it2a, rf1b, tuple(pairs[carrier])))
    preliminary.sort(key=lambda item: (natural_page_key(item[4].page), item[4].number,
                                       item[5], item[1]))
    output = []
    populations = rebuilt["populations"]
    for ordinal, (base_carrier, surface, label, paragraph, line, token_index,
                  it2a, rf1b, own_family) in enumerate(preliminary, 1):
        carrier = surface if learned else base_carrier
        decks, status, raw_slot, free_length = canonical_features(
            paragraph, line, token_index, carrier, populations["q152"],
            populations["end_classes"], own_family)
        ed1_decks, _, _, ed1_free_length = canonical_features(
            paragraph, line, token_index, carrier,
            frozenset(populations["q152"] | populations["ed1"]),
            populations["end_classes"], own_family)
        output.append(Event(
            f"G808-{prefix}-E{ordinal:04d}", ordinal, carrier,
            "POS" if label else "NEG", surface, paragraph, line,
            next(i for i, item in enumerate(paragraph.lines, 1)
                 if item.locus == line.locus), token_index, decks, ed1_decks,
            status, raw_slot, free_length, ed1_free_length, it2a, rf1b))
    return output


def score_pair_control(events: Sequence[Event], mode: str) -> dict[str, Any]:
    groups: defaultdict[tuple[str, str], list[Event]] = defaultdict(list)
    for event in events:
        held = event.carrier if mode == "COMPONENT_AND_FOLIO_HELD" else "ALL_CARRIERS"
        groups[(held, event.physical_folio)].append(event)
    predictions = []
    labels = {event.event_id: int(event.tail == "POS") for event in events}
    for (held_carrier, folio), tests in sorted(groups.items()):
        training = [event for event in events if event.physical_folio != folio
                    and (mode != "COMPONENT_AND_FOLIO_HELD"
                         or event.carrier != held_carrier)]
        if {labels[event.event_id] for event in training} != {0, 1}:
            raise AssertionError(f"control fold lost a class: {mode}:{held_carrier}:{folio}")
        models = {deck: train_mnb(training, labels, deck, "PRIMARY", frozenset())
                  for deck in DECKS}
        union_nuisance = train_union_mnb(training, labels, False)
        union_augmented = train_union_mnb(training, labels, True)
        for event in tests:
            row: dict[str, Any] = {"event_id": event.event_id,
                                   "carrier": event.carrier,
                                   "target_label": labels[event.event_id]}
            for deck in DECKS:
                row[deck + "_score"] = score(event.feature_decks[deck], models[deck][0])[0]
            row["nuisance_score"] = math.fsum(row[deck + "_score"] for deck in DECKS[:3])
            row["augmented_score"] = row["nuisance_score"] + row["SLOT_HOLE_score"]
            nuisance_features = frozenset(
                deck + "::" + feature for deck in DECKS[:3]
                for feature in event.feature_decks[deck])
            augmented_features = nuisance_features | frozenset(
                "SLOT_HOLE::" + feature for feature in event.feature_decks["SLOT_HOLE"])
            row["union_nuisance_score"] = score(nuisance_features, union_nuisance[0])[0]
            row["union_augmented_score"] = score(augmented_features, union_augmented[0])[0]
            for field in tuple(row):
                if field.endswith("_score"):
                    row[field] = q12(float(row[field]))
            predictions.append(row)
    metrics = {field: metric_bundle(predictions, field) for field in SUMMARY_CHANNELS.values()}
    return {"events": list(events), "predictions": predictions, "metrics": metrics}


def compare_pair_control(rows: Sequence[Mapping[str, str]], rebuilt: Mapping[str, Any],
                         control: str) -> None:
    if control == "THIN":
        pairs = {carrier: (carrier + "kol", carrier + "tal")
                 for carrier in rebuilt["populations"]["thin9"]}
        occurrences = pair_control_events(rebuilt, pairs, "THIN")
        expected_holdout, expected_events = "COMPONENT_AND_FOLIO_HELD", 306
    else:
        pairs = {"LEARNED_PAIR": ("cheol", "otal")}
        occurrences = pair_control_events(rebuilt, pairs, "LEARNED", learned=True)
        expected_holdout, expected_events = "LEAVE_ONE_PHYSICAL_FOLIO_OUT", len(occurrences)
    if len(occurrences) != expected_events:
        raise AssertionError(f"{control} control event census drift: {len(occurrences)}")
    scored = score_pair_control(occurrences, expected_holdout)
    census = {row["carrier"]: row for row in rows if row["row_type"] == "CENSUS"}
    expected_carriers = sorted({item.carrier for item in occurrences})
    if set(census) != set(expected_carriers) or len(census) != len(expected_carriers):
        raise AssertionError(f"{control} control carrier census identity mismatch")
    for carrier in expected_carriers:
        values = [item for item in occurrences if item.carrier == carrier]
        row = census[carrier]
        for field, expected in (("events", len(values)),
                                ("positive_events", sum(item.tail == "POS" for item in values)),
                                ("negative_events", sum(item.tail == "NEG" for item in values)),
                                ("physical_folios", len({item.physical_folio for item in values}))):
            expect_int(row[field], expected, f"{control}:{carrier}:{field}")
        expected_positive = next((item.surface for item in values if item.tail == "POS"), "NA")
        expected_negative = next((item.surface for item in values if item.tail == "NEG"), "NA")
        if (row["surface_positive"] != expected_positive
                or row["surface_negative"] != expected_negative
                or row["score_channel"] != "NA"
                or any(row[field] != "NA" for field in (
                    "micro_auc", "carrier_macro_auc", "balanced_accuracy",
                    "balanced_log_loss"))):
            raise AssertionError(f"{control} census surface/NA contract drift: {carrier}")
        if (row["holdout"] != expected_holdout
                or row["selection_credit"] != "CALIBRATION_ONLY"
                or row["semantic_credit"] != "0"):
            raise AssertionError(f"{control} holdout drift: {carrier}")
    scores = {row["score_channel"]: row for row in rows if row["row_type"] == "SCORE"}
    if set(scores) != set(SUMMARY_CHANNELS) or len(scores) != 8:
        raise AssertionError(f"{control} score-channel identity mismatch")
    for channel, row in scores.items():
        expect_int(row["events"], expected_events, f"{control}:{channel}:events")
        expect_int(row["positive_events"], sum(item.tail == "POS" for item in occurrences),
                   f"{control}:{channel}:positive")
        expect_int(row["negative_events"], sum(item.tail == "NEG" for item in occurrences),
                   f"{control}:{channel}:negative")
        expect_int(row["physical_folios"], len({item.physical_folio for item in occurrences}),
                   f"{control}:{channel}:folios")
        metric = scored["metrics"][SUMMARY_CHANNELS[channel]]
        for field, expected in (("micro_auc", metric["micro_auc"]),
                                ("carrier_macro_auc", metric["carrier_macro_auc"]),
                                ("balanced_accuracy", metric["balanced_accuracy"]),
                                ("balanced_log_loss", metric["log_loss"])):
            expect_f12(row[field], expected, f"{control}:{channel}:{field}")
        if (row["surface_positive"] != "NA" or row["surface_negative"] != "NA"
                or row["holdout"] != expected_holdout
                or row["selection_credit"] != "CALIBRATION_ONLY"
                or row["semantic_credit"] != "0"):
            raise AssertionError(f"{control} score metadata drift: {channel}")
    if len(rows) != len(census) + len(scores):
        raise AssertionError(f"{control} contains unknown row types or duplicates")


def compare_edge_packet(fields: Sequence[str], rows: Sequence[Mapping[str, str]],
                        rebuilt: Mapping[str, Any]) -> None:
    if tuple(fields) != EDGE_FIELDS or len(rows) != 19:
        raise AssertionError("GDT388 relation packet schema/cardinality drift")
    events = rebuilt["populations"]["core_events"]
    expected = []
    for carrier in sorted({event.carrier for event in events}):
        for axis, tails in (("L", {"ol", "eol"}), ("DY", {"edy", "eody"})):
            values = [event for event in events
                      if event.carrier == carrier and event.tail in tails]
            common_pages = sorted(
                {event.line.page for event in values if event.tail in {"eol", "eody"}}
                & {event.line.page for event in values if event.tail in {"ol", "edy"}},
                key=natural_page_key)
            pair = next(((expanded, base)
                         for page in common_pages
                         for expanded in values for base in values
                         if expanded.line.page == base.line.page == page
                         and expanded.tail in {"eol", "eody"}
                         and base.tail in {"ol", "edy"}
                         and expanded.line.locus != base.line.locus), None)
            if pair is None:
                continue
            expanded, base = pair
            expected.append({
                "edge_id": f"G808E{len(expected) + 1:04d}",
                "batch_id": "GDT808_EXACT_FORMAL_RECTANGLE",
                "page": expanded.line.page,
                "physical_folio": leaf_folio(expanded.line.page),
                "diagram_unit_id": f"FORMAL_RECTANGLE_{carrier}_{axis}",
                "pivot_visual_id": f"EXACT_BASE_{base.surface}",
                "pivot_locus": f"{base.line.locus}@{base.token_index}",
                "target_visual_id": f"EXACT_EXPANDED_{expanded.surface}",
                "target_locus": f"{expanded.line.locus}@{expanded.token_index}",
                "relation_type": f"FORMAL_{axis}_BASE_TO_EXPANDED",
                "direction_basis": "REGISTERED_EXACT_SURFACE_AXIS",
                "ownership_basis": "ANALYST_CARRIER_RECTANGLE_NOT_IMAGE_OWNERSHIP",
                "geometry_only_selection": "FALSE", "source_manifest_id": "GDT808",
                "page_crop_sha256": "NONE", "pivot_crop_sha256": "NONE",
                "target_crop_sha256": "NONE",
                "source_aware_localizer": "GDT808_GUARDED_TRANSCRIPTION_BUILDER",
                "relation_reviewer": "PENDING_EXTERNAL",
                "relation_confidence": "EXACT_FORMAL_SURFACE_PAIR_ZERO_SEMANTIC_CREDIT",
                "ambiguity_state": "FORMAL_TEXT_RELATION_NOT_AUTHORIAL_VISUAL_EDGE",
                "formal_access_state": "FORMAL_ACCESSED",
                "fold_assignment": "COMPONENT_AND_PHYSICAL_FOLIO_HELD",
                "eligibility_status": "INELIGIBLE_EXPLORATORY_TEXT_RELATION",
            })
    if len(expected) != 19:
        raise AssertionError(f"independent GDT388 edge capacity drift: {len(expected)}")
    for index, (row, wanted) in enumerate(zip(rows, expected), 1):
        if dict(row) != wanted:
            mismatches = {field: (row.get(field), wanted.get(field))
                          for field in EDGE_FIELDS if row.get(field) != wanted.get(field)}
            raise AssertionError(f"GDT388 edge {index} mismatch: {mismatches}")


def compare_source_lock(rows: Sequence[Mapping[str, str]]) -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    locked = {item["path"]: item for item in manifest["inputs"]}
    runtime = {
        rel(SRC / "run.py"): "official GDT808 builder",
        rel(SRC / "validate.py"): "independent GDT808 result validator",
    }
    official = {row["path"]: row for row in rows}
    if (set(official) != set(locked) | set(runtime) or len(official) != len(rows)
            or len(rows) != len(locked) + 2):
        raise AssertionError("SOURCE_LOCK manifest inventory mismatch")
    guarded = {rel(path) for path in (LINES_RAW, CROSS_RAW, TOKENS_RAW, G759, G768, G757)}
    for path_text, item in locked.items():
        row = official[path_text]
        if row["sha256"] != item["sha256"] or sha256(ROOT / path_text) != item["sha256"]:
            raise AssertionError(f"SOURCE_LOCK hash mismatch: {path_text}")
        expect_int(row["manifest_hash_match"], 1, f"SOURCE_LOCK:{path_text}:manifest")
        expected_mode = ("MANIFEST_HASH__TSV_GUARDED_QUERY_ONLY"
                         if path_text in guarded else "DIRECT_SAFE_INPUT")
        if row["access_mode"] != expected_mode or row["purpose"] != item["role"]:
            raise AssertionError(f"SOURCE_LOCK role/access mismatch: {path_text}")
    manifest_outputs = {item["path"]: item for item in manifest["outputs"]}
    for path_text, purpose in runtime.items():
        row = official[path_text]
        registered = manifest_outputs.get(path_text)
        if registered is None or row["sha256"] != registered["sha256"]:
            raise AssertionError(f"SOURCE_LOCK runtime not registered: {path_text}")
        if row["purpose"] != purpose \
                or row["access_mode"] != "MANIFEST_HASHED_RUNTIME_IMPLEMENTATION":
            raise AssertionError(f"SOURCE_LOCK runtime metadata mismatch: {path_text}")
        expect_int(row["manifest_hash_match"], 1, f"SOURCE_LOCK:{path_text}:manifest")
    for path_text, row in official.items():
        if Path(path_text).is_absolute() or not (ROOT / path_text).is_file():
            raise AssertionError(f"SOURCE_LOCK private/absent path: {path_text}")
        if sha256(ROOT / path_text) != row["sha256"]:
            raise AssertionError(f"SOURCE_LOCK runtime hash mismatch: {path_text}")


def compare_artifacts(rebuilt: Mapping[str, Any]) -> list[str]:
    required = set(OUTPUT_NAMES)
    present = {path.name for path in ART.glob("*") if path.is_file()}
    missing = required - present
    if missing:
        raise AssertionError(f"official artifacts unavailable: {sorted(missing)}")
    allowed_nonbuilder = {"README.md", "REGISTERED_VALIDATION.json", "VALIDATION.json"}
    unknown = present - required - allowed_nonbuilder
    if unknown:
        raise AssertionError(f"unknown GDT808 artifacts fail closed: {sorted(unknown)}")

    tables: dict[str, list[dict[str, str]]] = {}
    for name, expected_schema in EXPECTED_TSV_SCHEMAS.items():
        fields, rows = tsv_with_schema(ART / name)
        if tuple(fields) != tuple(expected_schema):
            raise AssertionError(
                f"artifact schema mismatch {name}: {tuple(fields)!r} != {tuple(expected_schema)!r}")
        tables[name] = rows
    source_lock_rows = tables["SOURCE_LOCK.tsv"]
    clarification_rows = tables["GDT808_IMPLEMENTATION_CLARIFICATIONS.tsv"]
    query_rows = tables["GDT808_GUARDED_QUERY_STATS.tsv"]
    census_rows = tables["GDT808_SOURCE_CENSUS.tsv"]
    carrier_rows = tables["GDT808_RAW35_ALL28_CORE13_CARRIER_CENSUS.tsv"]
    q_rows = tables["GDT808_Q152_EXACT_QUARANTINE.tsv"]
    event_rows = tables["GDT808_1777_CORE_EVENT_ATLAS.tsv"]
    feature_rows = tables["GDT808_FEATURE_DECK_CAPACITY.tsv"]
    fold_rows = tables["GDT808_COMPONENT_HELD_FOLDS.tsv"]
    prediction_rows = tables["GDT808_HELD_PREDICTIONS.tsv"]
    summary_rows = tables["GDT808_DECK_SCORE_SUMMARY.tsv"]
    conditional_rows = tables["GDT808_CONDITIONAL_CONCORDANCE.tsv"]
    ablation_rows = tables["GDT808_POSITION_MASK_SLOT_ABLATIONS.tsv"]
    direction_rows = tables["GDT808_CARRIER_DIRECTION_DIAGNOSTICS.tsv"]
    null_strata_rows = tables["GDT808_NULL_STRATUM_AUDIT.tsv"]
    null_rows = tables["GDT808_NULL_SCORES.tsv"]
    all28_rows = tables["GDT808_ALL28_SENSITIVITY.tsv"]
    ed1_rows = tables["GDT808_ED1_SENSITIVITY.tsv"]
    thin_rows = tables["GDT808_THIN_KOL_TAL.tsv"]
    learned_rows = tables["GDT808_LEARNED_CHEOL_OTAL.tsv"]
    historical_rows = tables["GDT808_HISTORICAL_RIVAL_CARD.tsv"]
    structural_rows = tables["GDT808_STRUCTURAL_CARD.tsv"]
    edge_fields = EXPECTED_TSV_SCHEMAS["GDT808_GDT388_RELATION_PACKET.tsv"]
    edge_rows = tables["GDT808_GDT388_RELATION_PACKET.tsv"]
    compare_source_lock(source_lock_rows)
    compare_implementation_clarifications(clarification_rows)
    compare_guarded_query_stats(query_rows, rebuilt)
    compare_source_census(census_rows, rebuilt)
    compare_carrier_census(carrier_rows, rebuilt)
    compare_q152(q_rows, rebuilt)
    compare_event_atlas(event_rows, rebuilt)
    compare_feature_capacity(feature_rows, rebuilt)
    compare_folds(fold_rows, rebuilt)
    compare_held_predictions(prediction_rows, rebuilt)
    compare_model_summary(summary_rows, rebuilt)
    compare_conditional_rows(conditional_rows, rebuilt)
    compare_ablation_rows(ablation_rows, rebuilt)
    compare_carrier_directions(direction_rows, rebuilt)
    compare_null_strata(null_strata_rows, rebuilt)
    compare_null_scores(null_rows, rebuilt)
    compare_score_subset(all28_rows,
                         {model_id: rebuilt["models"][model_id] for model_id in
                          ("M05_L_TO_L_ALL28", "M06_DY_TO_DY_ALL28",
                           "M07_L_TO_DY_ALL28", "M08_DY_TO_L_ALL28")}, "ALL28")
    compare_score_subset(ed1_rows, rebuilt["ed1_models"], "ED1")
    compare_pair_control(thin_rows, rebuilt, "THIN")
    compare_pair_control(learned_rows, rebuilt, "LEARNED")
    compare_historical_rivals(historical_rows, rebuilt)
    compare_structural_card(structural_rows, rebuilt)
    compare_edge_packet(edge_fields, edge_rows, rebuilt)
    intake = json.loads((ART / "GDT808_GDT388_EDGE_INTAKE.json").read_text(encoding="utf-8"))
    intake_fields = {"status", "packet_rows", "eligible_edges", "eligible_folios",
                     "discovery_edges", "holdout_edges", "mobile_edges",
                     "capacity_gate_50_edges_5_folios", "holdout_gate",
                     "mobile_null_gate", "score_ready", "errors"}
    if set(intake) != intake_fields:
        raise AssertionError("GDT388 intake JSON schema mismatch")
    if (intake.get("status") != "INVALID_PACKET" or intake.get("packet_rows") != 19
            or intake.get("eligible_edges") != 0 or intake.get("score_ready") is not False):
        raise AssertionError("GDT388 intake did not fail closed exactly")
    zero_fields = ("eligible_folios", "discovery_edges", "holdout_edges", "mobile_edges")
    if any(intake[field] != 0 for field in zero_fields) or any(
            intake[field] is not False for field in (
                "capacity_gate_50_edges_5_folios", "holdout_gate", "mobile_null_gate")):
        raise AssertionError("GDT388 intake gate/capacity fields mismatch")
    expected_intake_errors = [f"edge row {number}: formal access is not sealed"
                              for number in range(2, 21)]
    if intake.get("errors") != expected_intake_errors:
        raise AssertionError(
            f"GDT388 intake failed for non-contract reasons: {intake.get('errors')!r}")

    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    expected_result_fields = {
        "experiment_id", "status", "runtime_seconds", "sealed_data", "counts",
        "axis_decisions", "joint_topology", "leading_historical_rival",
        "reader_stable_rate_strict_prefilter_min_axis", "clean_contacts",
        "gdt388_intake", "claim_ceiling", "artifact_sha256"}
    if set(result) != expected_result_fields:
        raise AssertionError(f"RESULT top-level schema mismatch: {sorted(result)}")
    if result.get("experiment_id") != "GDT808" or result.get("sealed_data") != {
            "f84": "FORBIDDEN", "f84r": "FORBIDDEN"}:
        raise AssertionError("RESULT identity/sealed gate drift")
    expected_prediction_count = sum(len(model["predictions"])
                                    for model in rebuilt["models"].values())
    expected_fold_count = sum(len(model["folds"]) for model in rebuilt["models"].values())
    expected_counts = {"strict_paragraphs": 665, "raw_complete_carriers": 35,
                       "all28_carriers": 28, "core13_carriers": 13,
                       "q152_surfaces": 152,
                       "ed1_additional_surfaces": len(rebuilt["populations"]["ed1"]),
                       "core_events": 1777,
                       "all28_events": 2208, "core_event_paragraphs": 559,
                       "core_event_focal_lines": 1403, "core_event_physical_folios": 169,
                       "held_predictions": expected_prediction_count,
                       "held_folds": expected_fold_count, "thin_events": 306,
                       "learned_events": 205, "target_rotation_models": 2,
                       "target_rotations_each": 24, "carrier_null_models": 2,
                       "carrier_null_repetitions_each": 12, "gdt388_packet_rows": 19}
    if set(result.get("counts", {})) != set(expected_counts):
        raise AssertionError("RESULT counts schema mismatch")
    for field, expected in expected_counts.items():
        expect_int(result["counts"][field], expected, f"RESULT.counts.{field}")
    if result.get("joint_topology") != rebuilt["joint_topology"]:
        raise AssertionError("RESULT joint-topology mismatch")
    if set(result.get("axis_decisions", {})) != {"L", "DY"}:
        raise AssertionError("RESULT axis-decision schema mismatch")
    for axis, model_id, all28_id in (("L", "M01_L_TO_L", "M05_L_TO_L_ALL28"),
                                     ("DY", "M02_DY_TO_DY", "M06_DY_TO_DY_ALL28")):
        observed_axis = result["axis_decisions"][axis]
        expected_axis = {"decision": rebuilt["decisions"][model_id]["decision"],
                         **independent_axis_card(model_id, all28_id, rebuilt)}
        if set(observed_axis) != set(expected_axis):
            raise AssertionError(f"RESULT axis-decision field schema mismatch: {axis}")
        if observed_axis["decision"] != expected_axis["decision"]:
            raise AssertionError(f"RESULT axis decision mismatch: {axis}")
        for field, expected in expected_axis.items():
            if field == "decision":
                continue
            if isinstance(expected, int):
                expect_int(observed_axis[field], expected, f"RESULT.axis.{axis}.{field}")
            else:
                expect_float(observed_axis[field], expected, f"RESULT.axis.{axis}.{field}")
    stable = min(1169 / 1328, 1124 / 1825)
    expect_float(result["reader_stable_rate_strict_prefilter_min_axis"], stable,
                 "RESULT reader stability")
    clean = expected_clean_contacts(rebuilt)
    if set(result.get("clean_contacts", {})) != set(clean):
        raise AssertionError("RESULT clean-contact schema mismatch")
    for field, expected in clean.items():
        if field.endswith("_WINNING_AXIS"):
            if result["clean_contacts"][field] != expected:
                raise AssertionError(f"RESULT contact axis mismatch: {field}")
        elif field.endswith("_FOLIOS"):
            expect_int(result["clean_contacts"][field], int(expected), f"RESULT.contacts.{field}")
        else:
            expect_float(result["clean_contacts"][field], expected, f"RESULT.contacts.{field}")
    expected_status = (f"{rebuilt['joint_topology']}"
                       f"__L_{rebuilt['decisions']['M01_L_TO_L']['decision']}"
                       f"__DY_{rebuilt['decisions']['M02_DY_TO_DY']['decision']}")
    if result["status"] != expected_status:
        raise AssertionError("RESULT status composition mismatch")
    leading = rebuilt["rival_scores"][0]["rival_id"]
    if result["leading_historical_rival"] != leading:
        raise AssertionError("RESULT leading historical rival mismatch")
    expected_intake_summary = {"status": "INVALID_PACKET", "eligible_edges": 0,
                               "score_ready": False}
    if result["gdt388_intake"] != expected_intake_summary:
        raise AssertionError("RESULT GDT388 intake summary mismatch")
    hashes = result.get("artifact_sha256", {})
    expected_hash_paths = {rel(ART / name) for name in OUTPUT_NAMES if name != "RESULT.json"}
    if set(hashes) != expected_hash_paths:
        raise AssertionError("RESULT artifact-hash inventory mismatch")
    for path_text, digest in hashes.items():
        if sha256(ROOT / path_text) != digest:
            raise AssertionError(f"RESULT artifact hash mismatch: {path_text}")
    expected_ceiling = ("formal carrier-held relations and zero-semantic role-family ranking only; "
                        "zero lexemes, component values, plaintext, translation, or renderer credit")
    if result.get("claim_ceiling") != expected_ceiling:
        raise AssertionError("RESULT semantic claim ceiling mismatch")
    return ["official_25_artifact_inventory_exact", "source_lock_hashes_replayed",
            "source_census_replayed",
            "carrier_census_replayed",
            "q152_artifact_replayed", "complete_core_event_atlas_replayed",
            "feature_capacity_replayed", "all_component_folio_folds_replayed",
            "all_held_predictions_numerically_replayed", "eight_by_eight_model_summary_replayed",
            "conditional_carrier_concordance_replayed", "position_mask_slot_ablations_replayed",
            "carrier_directions_replayed", "target_and_carrier_null_scores_replayed",
            "target_and_carrier_null_strata_replayed",
            "all28_and_ed1_score_sensitivities_replayed",
            "thin_and_learned_control_censuses_replayed",
            "historical_rivals_and_clean_contacts_replayed", "structural_card_replayed",
            "gdt388_packet_and_fail_closed_intake_replayed",
            "result_decisions_contacts_and_hashes_replayed"]


def reconstruct(run_nulls: bool = True) -> dict[str, Any]:
    lines, paragraphs, outside, source_census = load_guarded_corpus()
    populations = relation_populations(lines, paragraphs)
    specs = read_model_specs()
    models = {}
    for spec in specs:
        events = populations["core_events"] if spec.population == "CORE13" else populations["all28_events"]
        models[spec.model_id] = score_model(spec, events, populations["q152"])
    union = {}
    target_nulls = {}
    carrier_nulls = {}
    decisions = {}
    ed1_models = {}
    if run_nulls:
        by_id = {spec.model_id: spec for spec in specs}
        for model_id in ("M01_L_TO_L", "M02_DY_TO_DY"):
            spec = by_id[model_id]
            union[model_id] = score_model(spec, populations["core_events"], populations["q152"], union=True)
            target_nulls[model_id] = rotate_target_labels(models[model_id])
            null_rows = []
            for rotation, mapping in enumerate(carrier_flip_maps(populations["core13"])):
                result = score_model(spec, populations["core_events"], populations["q152"],
                                     source_label_flips=mapping, auxiliary=False)
                null_rows.append({"rotation": rotation,
                                  "nuisance_macro_auc": result["metrics"]["nuisance_score"]["carrier_macro_auc"],
                                  "local_gain": result["metrics"]["local_gain"]})
            carrier_nulls[model_id] = null_rows
            all28_id = "M05_L_TO_L_ALL28" if model_id == "M01_L_TO_L" else "M06_DY_TO_DY_ALL28"
            decisions[model_id] = model_decision(models[model_id], models[all28_id],
                                                 union[model_id], target_nulls[model_id],
                                                 carrier_nulls[model_id])
            ed1_models[model_id] = score_model(
                spec, populations["core_events"], populations["q152"],
                view="ED1", auxiliary=True)
    overlays = contact_overlays(populations["core_events"], populations["q152"])
    rival_metrics = registered_rival_metrics(models, overlays, populations)
    rival_scores = historical_rival_scores(rival_metrics)
    topology = joint_topology(decisions, models) if decisions else None
    return {"lines": lines, "paragraphs": paragraphs, "outside": outside,
            "source_census": source_census, "populations": populations,
            "models": models, "union": union, "target_nulls": target_nulls,
            "carrier_nulls": carrier_nulls, "decisions": decisions,
            "ed1_models": ed1_models, "joint_topology": topology,
            "contact_overlays": overlays, "rival_metrics": rival_metrics,
            "rival_scores": rival_scores}


def compact_payload(rebuilt: Mapping[str, Any], checks: Sequence[str]) -> dict[str, Any]:
    populations = rebuilt["populations"]
    summary = {model_id: {"source_events": result["source_events"],
                          "target_events": result["target_events"],
                          "scoreable_folds": len(result["folds"]),
                          "nuisance_macro_auc": result["metrics"]["nuisance_score"]["carrier_macro_auc"],
                          "augmented_macro_auc": result["metrics"]["augmented_score"]["carrier_macro_auc"],
                          "local_gain": result["metrics"]["local_gain"]}
               for model_id, result in rebuilt["models"].items()}
    return {"experiment": "GDT808", "status": "PASS", "check_count": len(checks),
            "checks_passed": list(checks), "validator_independent_of_builder_import": True,
            "mixed_sources_accessed_only_by_guarded_query": True,
            "sealed_f84_rows_materialized": 0, "sealed_f84r_rows_materialized": 0,
            "source_census": rebuilt["source_census"],
            "population_census": {"raw35": len(populations["raw35"]),
                                   "all28": len(populations["all28"]),
                                   "core13": len(populations["core13"]),
                                   "q152": len(populations["q152"]),
                                   "core_events": len(populations["core_events"]),
                                   "core_event_paragraphs": len({event.paragraph.paragraph_id for event in populations["core_events"]}),
                                   "all28_events": len(populations["all28_events"])},
            "model_summary": summary, "decisions": rebuilt["decisions"],
            "contact_overlays": rebuilt["contact_overlays"]["axis_stats"],
            "historical_rival_metrics": rebuilt["rival_metrics"],
            "historical_rival_ranking": rebuilt["rival_scores"],
            "claim_ceiling": "formal held relation and zero-semantic historical topology only; no lexeme, component meaning, plaintext, renderer licence or translation"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-only", action="store_true")
    parser.add_argument("--skip-nulls", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    if builder_active():
        raise SystemExit("GDT808 builder active; refusing moving artifacts")
    before = artifact_snapshot()
    checks = manifest_checks()
    rebuilt = reconstruct(run_nulls=not args.skip_nulls)
    checks.extend(["guarded_source_census_reconstructed", "strict_paragraphs_reconstructed",
                   "raw35_all28_core13_q152_reconstructed", "core1777_and_all28_2208_reconstructed",
                   "four_disjoint_decks_reconstructed", "component_and_folio_holdouts_reconstructed",
                   "fixed_mnb_scores_reconstructed", "corrected_contact_overlays_reconstructed"])
    if args.source_only:
        checks.append("official_artifact_comparison_explicitly_skipped_source_only")
    else:
        checks.extend(compare_artifacts(rebuilt))
    if before != artifact_snapshot():
        raise AssertionError("artifact tree changed during validation")
    checks.append("artifact_tree_stable_during_validation")
    payload = compact_payload(rebuilt, checks)
    if not args.no_write and not args.source_only and not args.skip_nulls:
        temporary = VALIDATION.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temporary.replace(VALIDATION)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
