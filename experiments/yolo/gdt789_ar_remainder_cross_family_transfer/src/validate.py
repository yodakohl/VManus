#!/usr/bin/env python3
"""Validate GDT789 locks, artifacts, claim ceiling, and byte replay."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Mapping

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
EXP = ROOT / "experiments/yolo/gdt789_ar_remainder_cross_family_transfer"
SRC, ART, REPORT = EXP / "src", EXP / "artifacts", EXP / "REPORT.md"
RUN = SRC / "run.py"
SOURCE_LOCK = SRC / "SOURCE_LOCK.tsv"
OVERRIDES = SRC / "DEFAULT_OVERRIDES.tsv"
RELATION_INTAKE = ROOT / "tools/relation_edge_intake.py"

GENERATED = (
    "GDT789_285_AR_FAMILY_CENSUS.tsv",
    "GDT789_1348_AR_EXACT_OCCURRENCES.tsv",
    "GDT789_40_GDT788_SQUARE_REFERENCE.tsv",
    "GDT789_94_ROBUST_AR_OR_LATTICE.tsv",
    "GDT789_28_RN12_LATTICE.tsv",
    "GDT789_24_RN23_LATTICE.tsv",
    "GDT789_318_RAW_X_AR_SPANS.tsv",
    "GDT789_192_EXACT_X_AR_SPANS.tsv",
    "GDT789_20_FUSED_SPLIT_FAMILIES.tsv",
    "GDT789_1348_STOLFI_BOUNDARY_OCCURRENCES.tsv",
    "GDT789_225_STOLFI_BOUNDARY_SUMMARY.tsv",
    "GDT789_13_BARE_HEAD_CONSTRUCTIONS.tsv",
    "GDT789_96_FOLIO_BALANCED_PROFILES.tsv",
    "GDT789_2140_SEMANTIC_LEAKAGE_MASK.tsv",
    "GDT789_47_LEARNED_WHOLE_CONTROLS.tsv",
    "GDT789_47_AR_OR_TRANSFER.tsv",
    "GDT789_15_TRANSFER_SUMMARY.tsv",
    "GDT789_658_AXIS_CONTRASTS.tsv",
    "GDT789_42_AXIS_SUMMARY.tsv",
    "GDT789_94_VALUE_BINDING_SIGNATURES.tsv",
    "GDT789_13_RN_TRANSFER.tsv",
    "GDT789_8_RN_SUMMARY.tsv",
    "GDT789_253_ROLE_PROTOTYPE_LOO.tsv",
    "GDT789_3_ROLE_PROTOTYPE_SUMMARY.tsv",
    "GDT789_97_TARGET_ROLE_PROFILES.tsv",
    "GDT789_285_WORKING_DICTIONARY.tsv",
    "GDT789_225_PRACTICAL_PASSAGES.tsv",
    "GDT789_2_HISTORICAL_ARCHITECTURE_CONTROLS.tsv",
    "GDT789_GUARDED_SOURCE_STATS.tsv",
    "GDT789_GDT388_192_SEPARATED_SPAN_PACKET.tsv",
    "GDT789_RELATION_EDGE_CROSSWALK.tsv",
    "RELATION_PACKET_INTAKE.json",
    "RESULT.json",
    "README.md",
)

ZERO_FIELDS = (
    "default_is_translation", "confirmed_lexeme", "confirmed_plaintext",
    "specific_substance_confirmed", "historical_word_credit",
    "phonetic_or_eva_letter_credit", "component_export_credit",
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Audit:
    def __init__(self) -> None:
        self.checks = 0
        self.messages: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        self.checks += 1
        if not condition:
            raise AssertionError(message)
        self.messages.append(message)


def zeros(row: Mapping[str, str], fields=ZERO_FIELDS) -> bool:
    return all(row.get(field) == "0" for field in fields)


def close(left: float, right: float, tolerance: float = 5e-12) -> bool:
    return abs(left - right) <= tolerance


def unique(rows: list[dict[str, str]], fields: tuple[str, ...]) -> bool:
    keys = [tuple(row[field] for field in fields) for row in rows]
    return len(keys) == len(set(keys))


def main() -> int:
    audit = Audit()
    locks = read_tsv(SOURCE_LOCK)
    audit.check(len(locks) == 22, "22 source locks")
    for row in locks:
        relative = Path(row["path"])
        audit.check(not relative.is_absolute() and ".." not in relative.parts, f"safe source-lock path {relative}")
        audit.check((ROOT / relative).is_file(), f"locked source exists {relative}")
        audit.check(sha256(ROOT / relative) == row["expected_sha256"], f"locked source hash {relative}")

    corpus_module = load_module("gdt789_corpus_validation", SRC / "corpus.py")
    model_module = load_module("gdt789_model_validation", SRC / "model.py")
    run_module = load_module("gdt789_run_validation", RUN)
    corpus = corpus_module.compute(ROOT)
    model = model_module.compute(ROOT)
    audit.check(tuple(run_module.OUTPUT_NAMES) == GENERATED, "runner output registry")

    cd = corpus["diagnostics"]
    audit.check(cd["allowed_pages"] == 179, "179 guarded source pages")
    audit.check((cd["raw_family_surfaces"], cd["raw_family_occurrences"]) == (285, 1698), "285 raw forms / 1698 tokens")
    audit.check((cd["raw_family_page_labels"], cd["raw_family_physical_folios"]) == (153, 85), "raw family spans 153 page labels / 85 folios")
    audit.check((cd["reader_exact_family_surfaces"], cd["reader_exact_family_occurrences"]) == (225, 1348), "225 exact forms / 1348 tokens")
    audit.check((cd["reader_exact_family_page_labels"], cd["reader_exact_family_physical_folios"], cd["reader_exact_family_loci"]) == (146, 83, 997), "exact family spans 146 pages / 83 folios / 997 loci")
    audit.check((cd["bare_ar_raw_occurrences"], cd["bare_ar_reader_exact_occurrences"]) == (321, 242), "bare ar 321 raw / 242 exact")
    audit.check((cd["reader_exact_nonbare_surfaces"], cd["reader_exact_nonbare_occurrences"]) == (224, 1106), "224 nonbare forms / 1106 exact tokens")
    audit.check((cd["reader_exact_nonbare_recurrent_surfaces"], cd["reader_exact_nonbare_singleton_surfaces"]) == (80, 144), "80 recurrent / 144 singleton nonbare forms")
    audit.check((cd["square_primary_cells"], cd["square_primary_exact_occurrences"]) == (40, 422), "GDT788 square retained as 40-cell reference only")
    audit.check((cd["square_sensitivity_cells"], cd["square_sensitivity_exact_occurrences"]) == (64, 468), "unreported square sensitivity remains diagnostic")
    audit.check((cd["ar_or_robust_cells"], cd["ar_or_robust_prefixes"], cd["ar_or_robust_exact_occurrences"]) == (94, 47, 1647), "47-prefix AR/OR lattice has 94 cells / 1647 tokens")
    audit.check((cd["ar_or_support_primary_prefixes"], cd["ar_or_historical_exclusion_prefixes"]) == (31, 31), "31 support / 31 historical-exclusion prefixes")
    audit.check((cd["rn12_cells"], cd["rn23_cells"]) == (28, 24), "R/N grids have 28 / 24 cells")
    audit.check((cd["raw_separated_spans"], cd["clean_exact_separated_spans"], cd["clean_exact_separated_left_types"]) == (318, 192, 126), "318 raw / 192 exact X ar spans / 126 left types")
    audit.check(cd["fused_and_separated_left_types"] == 20, "20 fused/separated families")
    audit.check((cd["current_alternate_reader_split_candidates"], cd["current_alternate_reader_split_surfaces"]) == (15, 14), "15 current-reader alternate split candidates / 14 surfaces")
    audit.check((cd["stolfi_requested_pages"], cd["stolfi_selected_rows"]) == (146, 1673), "Stolfi guarded query covers 146 pages / 1673 rows")
    audit.check((cd["stolfi_nonbare_fused_occurrences"], cd["stolfi_nonbare_split_occurrences"]) == (327, 1), "Stolfi nonbare boundary evidence 327 fused / one split")
    audit.check(cd["construction_rows"] == 13, "13 bare-head constructions")
    audit.check(cd["sealed_f84_rows_materialised"] == 0, "corpus materialised no f84/f84r")

    md = model["diagnostics"]
    audit.check(md["recommendation"] == "WHOLE_ONLY", "model selects whole-only")
    audit.check((md["gdt788_prior_mask_surfaces"], md["raw_tail_union_surfaces"], md["ar_lineage_surfaces"], md["complete_semantic_mask_surfaces"]) == (996, 1622, 54, 2140), "996 / 1622 / 54 inputs form 2140-surface leakage mask")
    audit.check((md["reference_universe"], md["clean_reference_after_mask"], md["augmented_learned_whole_pool"]) == (46, 31, 443), "46 reference / 31 clean / 443 augmented learned wholes")
    audit.check(md["positive_axis_surfaces_used"] == 408 and md["positive_axis_surfaces_disjoint_from_mask"] == 1, "408 positive-axis sources disjoint from mask")
    audit.check((md["robust_prefixes"], md["support_primary_prefixes"], md["historical_exclusion_prefixes"]) == (47, 31, 31), "model cohort sizes 47 / 31 / 31")
    audit.check((md["support_full_add_beats_both"], md["historical_exclusion_full_add_beats_both"], md["support_semantic_add_beats_both"]) == (7, 8, 8), "ADD_AR both-null wins 7 / 8 / 8")
    audit.check((md["rn12_full_add_beats_all"], md["rn23_full_add_beats_all"]) == (0, 0), "both R/N full replications have zero all-null wins")
    audit.check((md["role_anchor_part"], md["role_anchor_amount"], md["role_anchor_value"]) == (12, 33, 208), "role anchors 12 PART / 33 AMOUNT / 208 VALUE")
    audit.check(close(md["role_selector_balanced_accuracy"], 0.6437937062937062), "role selector balanced accuracy")
    audit.check(close(md["role_selector_part_recall"], 0.75), "role selector PART recall")
    audit.check(md["bare_ar_profile_role"] == "VALUE" and md["role_selector_usable"] == 0, "bare ar profile cannot license a role identity")
    audit.check(md["component_export_credit"] == md["forbidden_f84_or_f84r_materialised"] == 0, "model exports no component and no f84 rows")

    expected_counts = {
        "GDT789_285_AR_FAMILY_CENSUS.tsv": 285,
        "GDT789_1348_AR_EXACT_OCCURRENCES.tsv": 1348,
        "GDT789_40_GDT788_SQUARE_REFERENCE.tsv": 40,
        "GDT789_94_ROBUST_AR_OR_LATTICE.tsv": 94,
        "GDT789_28_RN12_LATTICE.tsv": 28,
        "GDT789_24_RN23_LATTICE.tsv": 24,
        "GDT789_318_RAW_X_AR_SPANS.tsv": 318,
        "GDT789_192_EXACT_X_AR_SPANS.tsv": 192,
        "GDT789_20_FUSED_SPLIT_FAMILIES.tsv": 20,
        "GDT789_1348_STOLFI_BOUNDARY_OCCURRENCES.tsv": 1348,
        "GDT789_225_STOLFI_BOUNDARY_SUMMARY.tsv": 225,
        "GDT789_13_BARE_HEAD_CONSTRUCTIONS.tsv": 13,
        "GDT789_96_FOLIO_BALANCED_PROFILES.tsv": 96,
        "GDT789_2140_SEMANTIC_LEAKAGE_MASK.tsv": 2140,
        "GDT789_47_LEARNED_WHOLE_CONTROLS.tsv": 47,
        "GDT789_47_AR_OR_TRANSFER.tsv": 47,
        "GDT789_15_TRANSFER_SUMMARY.tsv": 15,
        "GDT789_658_AXIS_CONTRASTS.tsv": 658,
        "GDT789_42_AXIS_SUMMARY.tsv": 42,
        "GDT789_94_VALUE_BINDING_SIGNATURES.tsv": 94,
        "GDT789_13_RN_TRANSFER.tsv": 13,
        "GDT789_8_RN_SUMMARY.tsv": 8,
        "GDT789_253_ROLE_PROTOTYPE_LOO.tsv": 253,
        "GDT789_3_ROLE_PROTOTYPE_SUMMARY.tsv": 3,
        "GDT789_97_TARGET_ROLE_PROFILES.tsv": 97,
        "GDT789_285_WORKING_DICTIONARY.tsv": 285,
        "GDT789_225_PRACTICAL_PASSAGES.tsv": 225,
        "GDT789_2_HISTORICAL_ARCHITECTURE_CONTROLS.tsv": 2,
        "GDT789_GUARDED_SOURCE_STATS.tsv": 4,
        "GDT789_GDT388_192_SEPARATED_SPAN_PACKET.tsv": 192,
        "GDT789_RELATION_EDGE_CROSSWALK.tsv": 192,
    }
    artifacts: dict[str, list[dict[str, str]]] = {}
    for name, count in expected_counts.items():
        artifacts[name] = read_tsv(ART / name)
        audit.check(len(artifacts[name]) == count, f"{name} row count")

    family = artifacts["GDT789_285_AR_FAMILY_CENSUS.tsv"]
    audit.check(unique(family, ("surface",)), "family surfaces unique")
    audit.check(sum(int(row["raw_occurrences"]) for row in family) == 1698, "family raw total")
    audit.check(sum(int(row["reader_exact_occurrences"]) for row in family) == 1348, "family exact total")
    audit.check(sum(int(row["reader_exact_surface"]) for row in family) == 225, "family has 225 exact surfaces")
    audit.check(all(row["surface"].endswith("ar") and not row["surface"].endswith("dar") for row in family), "longest-ending ar partition excludes dar")
    audit.check(all(row["component_export_credit"] == "0" for row in family), "family census exports no component")

    exact_rows = artifacts["GDT789_1348_AR_EXACT_OCCURRENCES.tsv"]
    audit.check(unique(exact_rows, ("occurrence_id",)), "exact occurrence IDs unique")
    audit.check(unique(exact_rows, ("page", "locus", "token_index")), "exact natural occurrence keys unique")
    audit.check(all(row["reader_exact"] == "1" and row["surface"].endswith("ar") and not row["surface"].endswith("dar") for row in exact_rows), "exact atlas longest-ending ar contract")
    audit.check(not any(row["page"].startswith("f84") for row in exact_rows), "exact atlas excludes f84/f84r")
    positions = Counter(row["line_position"] for row in exact_rows if row["surface"] == "ar")
    audit.check(positions == Counter({"MIDDLE": 223, "FIRST": 1, "LAST": 18}), "bare ar line positions 1 / 223 / 18")
    audit.check(not any(row["true_paragraph_start"] == "1" or row["true_paragraph_end"] == "1" for row in exact_rows if row["surface"] == "ar"), "bare ar never occupies a true paragraph boundary")

    square = artifacts["GDT789_40_GDT788_SQUARE_REFERENCE.tsv"]
    audit.check(unique(square, ("prefix", "tail")) and {row["cohort"] for row in square} == {"PRIMARY_SQUARE"} and all(row["candidate_semantic_credit"] == row["component_export_credit"] == "0" for row in square), "40-cell square is unique and retained without score credit")
    square_totals = Counter()
    for row in square:
        square_totals[row["tail"]] += int(row["reader_exact_occurrences"])
    audit.check(square_totals == Counter({"ar": 167, "al": 112, "dar": 79, "dal": 64}), "reference square tail totals")

    lattice = artifacts["GDT789_94_ROBUST_AR_OR_LATTICE.tsv"]
    audit.check(unique(lattice, ("prefix", "tail")) and {row["tail"] for row in lattice} == {"ar", "or"}, "AR/OR lattice keys and tails")
    audit.check(len({row["prefix"] for row in lattice}) == 47, "AR/OR lattice has 47 prefixes")
    audit.check(all(int(row["reader_exact_occurrences"]) >= 2 and int(row["reader_exact_physical_folio_count"]) >= 2 for row in lattice), "every AR/OR cell meets robust coverage gate")
    lattice_totals = Counter()
    for row in lattice:
        lattice_totals[row["tail"]] += int(row["reader_exact_occurrences"])
    audit.check(lattice_totals == Counter({"ar": 861, "or": 786}), "AR/OR lattice tail totals 861 / 786")
    audit.check(sum(row["support_primary_31"] == "1" for row in lattice) == 62 and sum(row["historical_exclusion_31"] == "1" for row in lattice) == 62, "31-pair cohort flags cover 62 cells each")

    rn12 = artifacts["GDT789_28_RN12_LATTICE.tsv"]
    rn23 = artifacts["GDT789_24_RN23_LATTICE.tsv"]
    audit.check(unique(rn12, ("prefix", "tail")) and {row["tail"] for row in rn12} == {"ar", "an", "air", "ain"}, "RN12 dimensions")
    audit.check(unique(rn23, ("prefix", "tail")) and {row["tail"] for row in rn23} == {"air", "ain", "aiir", "aiin"}, "RN23 dimensions")
    rn12_totals = Counter()
    rn23_totals = Counter()
    for row in rn12:
        rn12_totals[row["tail"]] += int(row["reader_exact_occurrences"])
    for row in rn23:
        rn23_totals[row["tail"]] += int(row["reader_exact_occurrences"])
    audit.check(rn12_totals == Counter({"ain": 754, "ar": 668, "air": 143, "an": 34}), "RN12 tail totals")
    audit.check(rn23_totals == Counter({"aiin": 1208, "ain": 642, "air": 120, "aiir": 23}), "RN23 tail totals")

    raw_spans = artifacts["GDT789_318_RAW_X_AR_SPANS.tsv"]
    clean_spans = artifacts["GDT789_192_EXACT_X_AR_SPANS.tsv"]
    span_key = ("page", "locus", "left_token_ordinal", "right_token_ordinal")
    audit.check(unique(raw_spans, span_key) and unique(clean_spans, span_key), "span natural keys unique")
    raw_keys = {tuple(row[field] for field in span_key) for row in raw_spans}
    clean_keys = {tuple(row[field] for field in span_key) for row in clean_spans}
    audit.check(clean_keys < raw_keys, "exact spans are a strict raw subset")
    audit.check(all(row["right_surface"] == "ar" and row["both_tokens_reader_exact"] == row["all_three_readers_preserve_pair"] == row["clean_exact_span"] == "1" for row in clean_spans), "clean X ar span admission gate")
    audit.check(len({row["left_surface"] for row in clean_spans}) == 126, "clean spans have 126 left complete surfaces")

    fused = artifacts["GDT789_20_FUSED_SPLIT_FAMILIES.tsv"]
    audit.check(unique(fused, ("left_surface",)) and all(row["fused_surface"] == row["left_surface"] + "ar" for row in fused), "20 fused/separated surface families")
    audit.check(all(row["boundary_bridge_only"] == "1" and row["semantic_credit"] == row["component_export_credit"] == "0" for row in fused), "fused/separated rows carry boundary credit only")

    stolfi_occ = artifacts["GDT789_1348_STOLFI_BOUNDARY_OCCURRENCES.tsv"]
    stolfi_summary = artifacts["GDT789_225_STOLFI_BOUNDARY_SUMMARY.tsv"]
    audit.check(unique(stolfi_occ, ("occurrence_id",)) and {row["occurrence_id"] for row in stolfi_occ} == {row["occurrence_id"] for row in exact_rows}, "Stolfi occurrence atlas is 1:1 with exact atlas")
    audit.check(unique(stolfi_summary, ("surface",)) and {row["surface"] for row in stolfi_summary} == {row["surface"] for row in exact_rows}, "Stolfi summary covers all exact surfaces")
    stolfi_all = Counter(row["boundary_status"] for row in stolfi_occ)
    audit.check(stolfi_all == Counter({"NO_STOLFI_ROWS_FOR_PAGE": 591, "NO_SAME_LOCUS_ROW": 335, "FUSED_WHOLE_AT_SAME_LOCUS": 327, "BARE_AR_AT_SAME_LOCUS": 67, "ALTERNATE_READING_AT_SAME_LOCUS": 22, "OTHER_AR_BOUNDARY_AT_SAME_LOCUS": 5, "SPLIT_LEFT_AR_AT_SAME_LOCUS": 1}), "Stolfi all-occurrence partition")
    stolfi_nonbare = Counter(row["boundary_status"] for row in stolfi_occ if row["surface"] != "ar")
    audit.check(stolfi_nonbare == Counter({"NO_STOLFI_ROWS_FOR_PAGE": 469, "NO_SAME_LOCUS_ROW": 285, "FUSED_WHOLE_AT_SAME_LOCUS": 327, "ALTERNATE_READING_AT_SAME_LOCUS": 20, "OTHER_AR_BOUNDARY_AT_SAME_LOCUS": 4, "SPLIT_LEFT_AR_AT_SAME_LOCUS": 1}), "Stolfi nonbare partition")
    same_locus_nonbare = 1106 - stolfi_nonbare["NO_STOLFI_ROWS_FOR_PAGE"] - stolfi_nonbare["NO_SAME_LOCUS_ROW"]
    same_locus_bare = 242 - sum(stolfi_all[key] - stolfi_nonbare.get(key, 0) for key in ("NO_STOLFI_ROWS_FOR_PAGE", "NO_SAME_LOCUS_ROW"))
    audit.check((same_locus_nonbare, same_locus_bare, same_locus_nonbare + same_locus_bare) == (352, 70, 422), "Stolfi same-locus split is 352 longer + 70 bare = 422")
    split = [row for row in stolfi_occ if row["boundary_status"] == "SPLIT_LEFT_AR_AT_SAME_LOCUS"]
    audit.check(len(split) == 1 and split[0]["surface"] == "oar" and split[0]["locus"] == "f5r.1" and split[0]["stolfi_raw_split_separator"] == "," and split[0]["stolfi_split_left_ar_count"] == "1", "sole Stolfi split is oar -> o,ar at f5r.1")

    constructions = artifacts["GDT789_13_BARE_HEAD_CONSTRUCTIONS.tsv"]
    audit.check(unique(constructions, ("construction_id",)) and Counter(row["construction_family"] for row in constructions) == Counter({"VALUE": 9, "HEAD_NESTING": 4}), "construction deck has 9 value / 4 nesting rows")
    values = {(row["left_complete_surface"], row["right_complete_surface"]): row for row in constructions if row["construction_family"] == "VALUE"}
    audit.check(sum(int(values[("ar", value)]["reader_exact_separated_occurrences"]) for value in ("ain", "aiin", "aiiin")) == 27, "ar has 27 exact separated value spans")
    audit.check(sum(int(values[("or", value)]["reader_exact_separated_occurrences"]) for value in ("ain", "aiin", "aiiin")) == 42, "or has 42 exact separated value spans")
    audit.check(sum(int(values[("s", value)]["reader_exact_separated_occurrences"]) for value in ("ain", "aiin", "aiiin")) == 25, "s has 25 exact separated value spans")
    audit.check(sum(int(values[("ar", value)]["fused_reader_exact_occurrences"]) for value in ("ain", "aiin", "aiiin")) == 4, "ar value fusions total four")
    audit.check(sum(int(values[("or", value)]["fused_reader_exact_occurrences"]) for value in ("ain", "aiin", "aiiin")) == 36, "or value fusions total 36")
    audit.check(sum(int(values[("s", value)]["fused_reader_exact_occurrences"]) for value in ("ain", "aiin", "aiiin")) == 143, "s value fusions total 143")
    nesting = {(row["left_complete_surface"], row["right_complete_surface"]): row for row in constructions if row["construction_family"] == "HEAD_NESTING"}
    audit.check([int(nesting[pair]["reader_exact_separated_occurrences"]) for pair in (("ar", "ar"), ("ar", "or"), ("or", "ar"), ("or", "or"))] == [6, 8, 5, 3], "head nesting exact separated counts 6 / 8 / 5 / 3")
    audit.check([int(nesting[pair]["fused_reader_exact_occurrences"]) for pair in (("ar", "ar"), ("ar", "or"), ("or", "ar"), ("or", "or"))] == [1, 5, 5, 2], "head nesting fused counts 1 / 5 / 5 / 2")
    audit.check(all(row["supports_specific_unit_identity"] == row["component_export_credit"] == "0" for row in constructions), "construction deck names no unit and exports no component")
    audit.check({(row["left_complete_surface"], row["right_complete_surface"]) for row in constructions if row["supports_distinct_or_nested_heads"] == "1"} == {("ar", "or"), ("or", "ar")}, "mixed nesting only flags distinct-or-nested heads")

    profiles = artifacts["GDT789_96_FOLIO_BALANCED_PROFILES.tsv"]
    audit.check(unique(profiles, ("surface",)) and Counter(row["profile_role"] for row in profiles) == Counter({"AR_OR_LATTICE": 94, "BARE_CORE": 2}), "profile rows are 94 lattice + 2 bare cores")
    for row in profiles:
        for field in model_module.PROFILE_FIELDS:
            distribution = json.loads(row[field + "_json"])
            audit.check(not distribution or close(sum(float(value) for value in distribution.values()), 1.0), f"normalised profile {row['surface']} {field}")

    mask = artifacts["GDT789_2140_SEMANTIC_LEAKAGE_MASK.tsv"]
    audit.check(unique(mask, ("surface",)), "2140 mask surfaces unique")
    audit.check(sum(int(row["gdt788_prior_mask"]) for row in mask) == 996, "mask carries 996 prior surfaces")
    audit.check(sum(int(row["ar_or_rn_tail_union"]) for row in mask) == 1622, "mask carries 1622 raw tail surfaces")
    audit.check(sum(int(row["ar_lineage"]) for row in mask) == 54, "mask carries 54 AR-lineage surfaces")
    audit.check(all(row["excluded_from_semantic_neighbours"] == row["excluded_from_learned_whole_donors"] == "1" and row["component_export_credit"] == "0" for row in mask), "mask exclusions explicit")
    masked_surfaces = {row["surface"] for row in mask}

    donors = artifacts["GDT789_47_LEARNED_WHOLE_CONTROLS.tsv"]
    audit.check(unique(donors, ("prefix",)) and {row["prefix"] for row in donors} == {row["prefix"] for row in lattice}, "one donor row per robust prefix")
    audit.check(all(row["target_profile_used_for_ranking"] == row["semantic_value_used_for_ranking"] == "0" and row["semantic_eligibility_sanitization"] == row["all_donors_outside_mask"] == "1" for row in donors), "donor ranking is target/meaning blind after semantic eligibility sanitisation")
    audit.check(not any(surface in masked_surfaces for row in donors for surface in row["donors"].split("|")), "all learned donors lie outside leakage mask")

    transfer = artifacts["GDT789_47_AR_OR_TRANSFER.tsv"]
    audit.check(unique(transfer, ("prefix",)) and {row["prefix"] for row in transfer} == {row["prefix"] for row in donors}, "47 transfer rows match donor prefixes")
    audit.check(sum(row["support_primary_31"] == "1" for row in transfer) == 31 and sum(row["historical_exclusion_31"] == "1" for row in transfer) == 31, "transfer has 31 support / 31 historical-exclusion rows")
    audit.check(sum(row["full_add_beats_both"] == "1" for row in transfer if row["support_primary_31"] == "1") == 7, "support full ADD_AR beats both controls 7/31")
    audit.check(sum(row["full_add_beats_both"] == "1" for row in transfer if row["historical_exclusion_31"] == "1") == 8, "historical-exclusion full ADD_AR beats both controls 8/31")
    audit.check(sum(row["full_add_beats_both"] == "1" for row in transfer) == 9, "all robust full ADD_AR beats both controls 9/47")
    audit.check({row["prefix"] for row in transfer if row["support_primary_31"] == row["full_add_beats_both"] == "1"} == {"l", "op", "otch", "p", "qop", "s", "she"}, "support winners fixed")
    audit.check({row["prefix"] for row in transfer if row["historical_exclusion_31"] == row["full_add_beats_both"] == "1"} == {"cho", "kee", "l", "op", "otch", "p", "qop", "s"}, "historical-exclusion winners fixed")
    audit.check(all(row["component_export_credit"] == "0" and row["full_target_defined_fields"] for row in transfer), "transfer rows score target-defined fields and export nothing")

    summaries = {(row["cohort"], row["view"]): row for row in artifacts["GDT789_15_TRANSFER_SUMMARY.tsv"]}
    audit.check(set(summaries) == {(cohort, view) for cohort in ("SUPPORT_PRIMARY_31", "HISTORICAL_EXCLUSION_31", "ROBUST_ALL_47") for view in ("FULL", "STRUCTURAL", "LOCAL", "SEMANTIC", "CONSTRUCTION")}, "15 transfer summary cells")
    support_full = summaries[("SUPPORT_PRIMARY_31", "FULL")]
    exclusion_full = summaries[("HISTORICAL_EXCLUSION_31", "FULL")]
    audit.check((support_full["add_beats_x_or"], support_full["add_beats_learned"], support_full["add_beats_both"]) == ("21", "11", "7"), "support FULL wins 21 / 11 / 7")
    audit.check((exclusion_full["add_beats_x_or"], exclusion_full["add_beats_learned"], exclusion_full["add_beats_both"]) == ("21", "13", "8"), "historical-exclusion FULL wins 21 / 13 / 8")
    audit.check(close(float(support_full["add_ar_macro_similarity"]), 0.7868061317257343) and close(float(support_full["x_or_macro_similarity"]), 0.7626822933037535) and close(float(support_full["learned_whole_macro_similarity"]), 0.8104157456373056), "support FULL macro similarities")
    audit.check(close(float(exclusion_full["add_ar_macro_similarity"]), 0.7553156739309876) and close(float(exclusion_full["x_or_macro_similarity"]), 0.7250548613346078) and close(float(exclusion_full["learned_whole_macro_similarity"]), 0.7676137003100006), "historical-exclusion FULL macro similarities")
    audit.check((summaries[("SUPPORT_PRIMARY_31", "SEMANTIC")]["informative_types"], summaries[("SUPPORT_PRIMARY_31", "SEMANTIC")]["na_types"], summaries[("SUPPORT_PRIMARY_31", "SEMANTIC")]["add_beats_both"]) == ("29", "2", "8"), "support semantic 29 informative / two NA / eight wins")

    axis_rows = artifacts["GDT789_658_AXIS_CONTRASTS.tsv"]
    axis_summary = {(row["cohort"], row["radius"], row["axis"]): row for row in artifacts["GDT789_42_AXIS_SUMMARY.tsv"]}
    audit.check(unique(axis_rows, ("radius", "axis", "prefix")), "658 axis contrast keys unique")
    audit.check(set(axis_summary) == {(cohort, str(radius), axis) for cohort in ("SUPPORT_PRIMARY_31", "HISTORICAL_EXCLUSION_31", "ROBUST_ALL_47") for radius in (1, 3) for axis in model_module.AUDIT_AXES}, "42 axis summary cells")
    expected_axis = {
        ("1", "PART"): (6, 1, 24, 0.007748376439, 0.234375),
        ("1", "AMOUNT"): (6, 4, 21, 0.016618676273, 0.08984375),
        ("3", "PART"): (9, 6, 16, 0.007543753049, 0.642883300781),
        ("3", "AMOUNT"): (10, 8, 13, 0.022639521887, 0.2373046875),
    }
    for (radius, axis), expected in expected_axis.items():
        row = axis_summary[("SUPPORT_PRIMARY_31", radius, axis)]
        audit.check((int(row["ar_higher_types"]), int(row["or_higher_types"]), int(row["tie_types"])) == expected[:3], f"axis direction counts {radius} {axis}")
        audit.check(close(float(row["mean_ar_minus_or"]), expected[3]) and close(float(row["sign_flip_p"]), expected[4]), f"axis effect and sign-flip p {radius} {axis}")
    audit.check(all(row["component_export_credit"] == "0" for row in axis_rows + list(axis_summary.values())), "axis decks export no component")

    bindings = artifacts["GDT789_94_VALUE_BINDING_SIGNATURES.tsv"]
    audit.check(unique(bindings, ("prefix", "family")) and Counter(row["family"] for row in bindings) == Counter({"AR": 47, "OR": 47}), "94 AR/OR value-binding signatures")
    audit.check(all(row["specific_unit_identity_supported"] == row["component_export_credit"] == "0" for row in bindings), "value bindings identify no unit")

    rn_transfer = artifacts["GDT789_13_RN_TRANSFER.tsv"]
    rn_summary = {(row["cohort"], row["view"]): row for row in artifacts["GDT789_8_RN_SUMMARY.tsv"]}
    audit.check(unique(rn_transfer, ("cohort", "prefix")) and Counter(row["cohort"] for row in rn_transfer) == Counter({"RN12": 7, "RN23": 6}), "13 R/N transfer rows")
    audit.check(set(rn_summary) == {(cohort, view) for cohort in ("RN12", "RN23") for view in ("FULL", "STRUCTURAL", "SEMANTIC", "CONSTRUCTION")}, "eight R/N summary cells")
    audit.check(rn_summary[("RN12", "FULL")]["add_beats_all"] == rn_summary[("RN23", "FULL")]["add_beats_all"] == "0", "R/N FULL transfer has zero all-null wins")
    audit.check(rn_summary[("RN23", "STRUCTURAL")]["add_beats_all"] == "2", "RN23 structural transfer has only 2/6 wins")

    prototypes = artifacts["GDT789_253_ROLE_PROTOTYPE_LOO.tsv"]
    prototype_summary = {row["role"]: row for row in artifacts["GDT789_3_ROLE_PROTOTYPE_SUMMARY.tsv"]}
    audit.check(unique(prototypes, ("surface",)) and Counter(row["actual_working_role"] for row in prototypes) == Counter({"VALUE": 208, "AMOUNT": 33, "PART": 12}), "253 leave-one-out role anchors")
    audit.check(set(prototype_summary) == {"PART", "AMOUNT", "VALUE"}, "three role summaries")
    audit.check((prototype_summary["PART"]["loo_correct"], prototype_summary["AMOUNT"]["loo_correct"], prototype_summary["VALUE"]["loo_correct"]) == ("9", "9", "189"), "role correct counts 9 / 9 / 189")
    audit.check(close(float(prototype_summary["PART"]["loo_recall"]), 0.75) and close(float(prototype_summary["AMOUNT"]["loo_recall"]), 9 / 33) and close(float(prototype_summary["VALUE"]["loo_recall"]), 189 / 208), "role recalls 0.75 / 0.273 / 0.909")
    audit.check(all(row["semantic_selector_usable"] == row["component_export_credit"] == "0" for row in prototype_summary.values()), "role selector explicitly unusable")
    targets = artifacts["GDT789_97_TARGET_ROLE_PROFILES.tsv"]
    audit.check(unique(targets, ("surface",)) and len(targets) == 97, "97 unique target-role profiles")
    bare_roles = {row["surface"]: row["predicted_working_role"] for row in targets if row["surface"] in {"ar", "or", "s"}}
    audit.check(bare_roles == {"ar": "VALUE", "or": "VALUE", "s": "VALUE"}, "unusable selector maps all three bare controls to VALUE")
    audit.check(all(row["selector_usable"] == row["component_export_credit"] == "0" and row["working_role_only_not_translation"] == "1" for row in targets), "target role profiles remain non-translations")

    override_rows = read_tsv(OVERRIDES)
    dictionary = artifacts["GDT789_285_WORKING_DICTIONARY.tsv"]
    audit.check(unique(override_rows, ("surface",)) and len(override_rows) == 19, "19 unique complete-whole overrides")
    audit.check(unique(dictionary, ("surface",)) and {row["surface"] for row in dictionary} == {row["surface"] for row in family}, "dictionary covers all 285 raw forms")
    audit.check(Counter(row["card_class"] for row in dictionary) == Counter({"EXPLICIT_COMPLETE_WHOLE": 19, "RECURRENT_WHOLE_FALLBACK": 63, "EXACT_SINGLETON_FALLBACK": 143, "RAW_ONLY_FALLBACK": 60}), "dictionary dispatch 19 / 63 / 143 / 60")
    audit.check(not any(row["card_class"] == "PROFILE_GUIDED_COMPLETE_WHOLE" for row in dictionary), "failed role selector controls no preferred default")
    audit.check(Counter(row["display_scope"] for row in dictionary) == Counter({"READER_EXACT_COMPLETE_WHOLE_ONLY": 225, "RAW_READER_WARNING_ONLY": 60}), "dictionary exact/warning scopes 225 / 60")
    audit.check(all(row["preferred_working_default_de"] and row["positive_evidence_de"] and row["counterevidence_de"] for row in dictionary), "every card has a nonempty default and evidence")
    audit.check(all(len({row["preferred_working_default_de"], row["rival_1_de"], row["rival_2_de"], row["rival_3_de"]}) == 4 for row in dictionary), "every card has three distinct semantic rivals")
    audit.check(all(len({row["preferred_mechanism"], row["mechanism_rival_1"], row["mechanism_rival_2"], row["mechanism_rival_3"]}) == 4 for row in dictionary), "every card has three distinct mechanism rivals")
    audit.check(all(zeros(row) and row["replaceable"] == "1" and row["gdt789_new_renderer_license"] == row["portable_ar_component_used"] == "0" for row in dictionary), "dictionary claim ceiling and zero AR component use")
    audit.check(all(0 <= int(row["confidence_0_100_not_probability"]) <= 100 and row["confidence_basis"] == "EDITORIAL_EVIDENCE_WEIGHT_NOT_FORMULA_NOT_PROBABILITY" for row in dictionary), "editorial confidence is bounded and explicitly non-probabilistic")
    cards = {row["surface"]: row for row in dictionary}
    audit.check(cards["ar"]["preferred_working_default_de"] == "Anteil" and cards["ar"]["confidence_0_100_not_probability"] == "64", "bare ar default Anteil at editorial confidence 64")
    expected_cards = {
        "qokar": "heißer Anteil", "otar": "kalter Zubereitungsanteil",
        "okar": "Anteil des heißen Ansatzes", "char": "trockener Anteil",
        "sar": "wiederkehrendes Verhältnisfeld", "lar": "wiederkehrendes Verhältnisfeld",
        "par": "wiederkehrendes Verhältnisfeld",
        "arar": "Anteil eines Anteils", "otarar": "Unteranteil des kalten Ansatzes",
    }
    audit.check(all(cards[surface]["preferred_working_default_de"] == default for surface, default in expected_cards.items()), "named complete-whole examples fixed")
    preferred_defaults = "\n".join(row["preferred_working_default_de"].lower() for row in dictionary)
    audit.check(not any(term in preferred_defaults for term in ("drogen", "holz", "samen", "saat", "wurzel", "pulver")), "retired automatic patients absent from preferred defaults")

    passages = artifacts["GDT789_225_PRACTICAL_PASSAGES.tsv"]
    audit.check(unique(passages, ("surface",)) and {row["surface"] for row in passages} == {row["surface"] for row in dictionary if row["reader_exact_surface"] == "1"}, "one passage per exact dictionary card")
    audit.check(all(f"⟦{row['surface']} = {row['working_default_de']}⟧" in row["target_focused_line"] for row in passages), "passages focus one complete whole")
    audit.check(all(zeros(row) and row["gdt789_new_renderer_license"] == row["portable_ar_component_used"] == "0" for row in passages), "passages remain display-only and export no component")

    historical = artifacts["GDT789_2_HISTORICAL_ARCHITECTURE_CONTROLS.tsv"]
    audit.check({row["source_id"] for row in historical} == {"HSR008", "HSR010"}, "two historical architecture controls")
    audit.check(all(zeros(row) and row["selects_ar_identity"] == row["selects_ar_segmentation"] == "0" for row in historical), "historical controls give no EVA identity credit")

    source_stats = {row["source"]: row for row in artifacts["GDT789_GUARDED_SOURCE_STATS.tsv"]}
    audit.check(set(source_stats) == {"tokens", "cross", "lines", "stolfi"}, "four guarded source stats")
    audit.check((source_stats["tokens"]["selected_rows"], source_stats["tokens"]["skipped_forbidden"], source_stats["tokens"]["skipped_not_allowed"]) == ("32339", "709", "5940"), "token guard counts")
    audit.check((source_stats["cross"]["selected_rows"], source_stats["cross"]["skipped_forbidden"], source_stats["cross"]["skipped_not_allowed"]) == ("4137", "98", "1151"), "cross guard counts")
    audit.check((source_stats["lines"]["selected_rows"], source_stats["lines"]["skipped_forbidden"], source_stats["lines"]["skipped_not_allowed"]) == ("4137", "98", "1150"), "line guard counts")
    audit.check((source_stats["stolfi"]["selected_rows"], source_stats["stolfi"]["skipped_forbidden"], source_stats["stolfi"]["skipped_not_allowed"], source_stats["stolfi"]["query_allow_pages"]) == ("1673", "33", "1311", "146"), "Stolfi guard and 146-page query")
    audit.check(all(row["base_allowed_pages"] == "179" and row["f84_rows_materialised"] == "0" for row in source_stats.values()), "all source paths retain 179-page guard and zero f84 rows")

    packet_path = ART / "GDT789_GDT388_192_SEPARATED_SPAN_PACKET.tsv"
    packet = artifacts["GDT789_GDT388_192_SEPARATED_SPAN_PACKET.tsv"]
    crosswalk = artifacts["GDT789_RELATION_EDGE_CROSSWALK.tsv"]
    audit.check(unique(packet, ("edge_id",)) and unique(crosswalk, ("edge_id",)) and {row["edge_id"] for row in packet} == {row["edge_id"] for row in crosswalk}, "packet/crosswalk edge IDs 1:1")
    audit.check(all(row["relation_type"] == "X_PRECEDES_AR_SEPARATED" and row["geometry_only_selection"] == "FALSE" and row["eligibility_status"] == "INELIGIBLE_EXPLORATORY_TEXT_RELATION" for row in packet), "packet fixed ineligible text-relation fields")
    audit.check(all(zeros(row) and row["semantic_score_eligible"] == "0" and row["working_ar_default_de"] == "Anteil" for row in crosswalk), "crosswalk has Anteil display and zero semantic credit")
    intake_module = load_module("gdt789_relation_validation", RELATION_INTAKE)
    intake = intake_module.validate_relation_edge_packet(packet_path)
    audit.check(intake["status"] == "VALID_ACQUISITION_NOT_SCORE_READY", "direct relation intake status")
    audit.check(intake["packet_rows"] == 192 and intake["eligible_edges"] == 0 and not intake["score_ready"] and not intake["errors"], "relation packet ineligible and error-free")
    committed_intake = json.loads((ART / "RELATION_PACKET_INTAKE.json").read_text(encoding="utf-8"))
    audit.check(committed_intake == intake, "committed relation intake equals direct intake")
    completed = subprocess.run([str(ROOT / "vmanus-exp"), "check-edge-packet", str(packet_path)], cwd=ROOT, text=True, capture_output=True)
    audit.check(completed.returncode == 0, "vmanus-exp check-edge-packet succeeds")
    audit.check(json.loads(completed.stdout) == intake, "CLI relation intake equals direct intake")

    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    audit.check(result["experiment_id"] == "GDT789" and result["status"].startswith("PARTIAL__285_RAW_FORMS__1698_RAW"), "result identity and status")
    audit.check(result["model"]["recommendation"] == "WHOLE_ONLY" and result["adjudication"]["portable_ar_remainder"] == "C0_INACTIVE__WHOLE_ONLY", "result whole-only decision")
    audit.check(result["adjudication"]["bare_ar_default_de"] == "Anteil" and result["adjudication"]["implicit_level_i"] == "REMOVED", "result retains Anteil and removes implicit level I")
    audit.check(result["dictionary"]["raw_forms_with_nonempty_defaults"] == 285 and result["dictionary"]["reader_exact_display_cards"] == 225 and result["dictionary"]["raw_reader_warning_cards"] == 60, "result dictionary coverage")
    audit.check(result["dictionary"]["new_renderer_licenses"] == result["dictionary"]["portable_component_exports"] == 0, "result dictionary grants no renderer or component license")
    audit.check(result["confirmed_lexemes"] == result["confirmed_plaintext_clauses"] == result["specific_substances"] == result["component_exports"] == 0, "result semantic ceiling")
    audit.check(result["new_pages"] == result["new_images"] == result["new_ocr"] == result["new_transcriptions"] == result["sealed_pages_accessed"] == 0, "result records no new or sealed access")
    audit.check(result["adjudication"]["next_remainder"] == "ol", "result routes next to ol")

    report = REPORT.read_text(encoding="utf-8")
    audit.check("WHOLE_ONLY" in report and "`ar = Anteil`" in report, "report states decision and bare working default")
    audit.check("7/31" in report and "8/31" in report and "2.140" in report, "report states main wins and leakage mask")
    audit.check("352 längere Formen" in report and "70 das nackte `ar`" in report and "oar → o,ar" in report, "report states corrected Stolfi partition and sole split")
    audit.check("global in den laufenden Renderer exportiert" in report and "Als Nächstes folgt `ol`" in report, "report states renderer limit and next route")

    private_home = "/" + "home" + "/"
    key_marker = "BEGIN " + "PRIVATE KEY"
    for path in sorted(p for p in EXP.rglob("*") if p.is_file() and p != ART / "VALIDATION.json"):
        data = path.read_bytes()
        audit.check(private_home.encode() not in data and key_marker.encode() not in data, f"privacy markers absent {path.relative_to(EXP)}")

    with tempfile.TemporaryDirectory(prefix="gdt789-replay-") as directory:
        replay_artifacts = Path(directory) / "artifacts"
        completed = subprocess.run([sys.executable, "-B", str(RUN), "--artifacts-dir", str(replay_artifacts)], cwd=ROOT, text=True, capture_output=True)
        audit.check(completed.returncode == 0, "runner replay succeeds")
        if completed.returncode != 0:
            raise AssertionError(completed.stderr)
        for name in GENERATED:
            audit.check((replay_artifacts / name).read_bytes() == (ART / name).read_bytes(), f"byte replay {name}")

    validation = {
        "experiment_id": "GDT789",
        "status": "PASS",
        "checks": audit.checks,
        "messages": audit.messages,
        "source_locks": len(locks),
        "runner_outputs_replayed": len(GENERATED),
        "relation_packet_status": intake["status"],
        "sealed_pages_accessed": 0,
    }
    (ART / "VALIDATION.json").write_text(
        json.dumps(validation, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
