#!/usr/bin/env python3
"""Validate GDT788 locks, artifacts, semantic ceiling and byte replay."""

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
EXP = ROOT / "experiments/yolo/gdt788_dal_remainder_cross_family_transfer"
SRC, ART, REPORT = EXP / "src", EXP / "artifacts", EXP / "REPORT.md"
RUN, SOURCE_LOCK, OVERRIDES = SRC / "run.py", SRC / "SOURCE_LOCK.tsv", SRC / "DEFAULT_OVERRIDES.tsv"
RELATION_INTAKE = ROOT / "tools/relation_edge_intake.py"

GENERATED = (
    "GDT788_107_DAL_FAMILY_CENSUS.tsv",
    "GDT788_304_DAL_EXACT_OCCURRENCES.tsv",
    "GDT788_40_PRIMARY_AL_DAL_AR_DAR_LATTICE.tsv",
    "GDT788_64_EXPANDED_AL_DAL_AR_DAR_LATTICE.tsv",
    "GDT788_185_RAW_X_DAL_SPANS.tsv",
    "GDT788_115_EXACT_X_DAL_SPANS.tsv",
    "GDT788_4_FUSED_SPLIT_FAMILIES.tsv",
    "GDT788_304_STOLFI_BOUNDARY_OCCURRENCES.tsv",
    "GDT788_80_STOLFI_BOUNDARY_SUMMARY.tsv",
    "GDT788_42_FOLIO_BALANCED_PROFILES.tsv",
    "GDT788_996_SEMANTIC_LEAKAGE_MASK.tsv",
    "GDT788_10_LEARNED_WHOLE_CONTROLS.tsv",
    "GDT788_10_PRIMARY_FACTORIAL_TRANSFER.tsv",
    "GDT788_4_MODEL_SUMMARY.tsv",
    "GDT788_140_AXIS_DID_CONTRASTS.tsv",
    "GDT788_14_AXIS_DID_SUMMARY.tsv",
    "GDT788_107_WORKING_DICTIONARY.tsv",
    "GDT788_80_PRACTICAL_PASSAGES.tsv",
    "GDT788_2_HISTORICAL_ARCHITECTURE_CONTROLS.tsv",
    "GDT788_GUARDED_SOURCE_STATS.tsv",
    "GDT788_GDT388_115_SEPARATED_SPAN_PACKET.tsv",
    "GDT788_RELATION_EDGE_CROSSWALK.tsv",
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
    audit.check(len(locks) == 23, "23 source locks")
    for row in locks:
        relative = Path(row["path"])
        audit.check(not relative.is_absolute() and ".." not in relative.parts, f"safe source-lock path {relative}")
        audit.check((ROOT / relative).is_file(), f"locked source exists {relative}")
        audit.check(sha256(ROOT / relative) == row["expected_sha256"], f"locked source hash {relative}")

    corpus = load_module("gdt788_corpus_validation", SRC / "corpus.py").compute(ROOT)
    model = load_module("gdt788_model_validation", SRC / "model.py").compute(ROOT)
    run_module = load_module("gdt788_run_validation", RUN)
    audit.check(tuple(run_module.OUTPUT_NAMES) == GENERATED, "runner output registry")

    cd = corpus["diagnostics"]
    audit.check((cd["raw_family_surfaces"], cd["raw_family_occurrences"]) == (107, 415), "107 raw forms / 415 tokens")
    audit.check((cd["reader_exact_family_surfaces"], cd["reader_exact_family_occurrences"]) == (80, 304), "80 exact forms / 304 tokens")
    audit.check((cd["bare_dal_raw_occurrences"], cd["bare_dal_reader_exact_occurrences"]) == (191, 147), "bare dal 191 raw / 147 exact")
    audit.check((cd["reader_exact_nonbare_surfaces"], cd["reader_exact_nonbare_occurrences"]) == (79, 157), "79 nonbare exact forms / 157 tokens")
    audit.check((cd["reader_exact_nonbare_recurrent_surfaces"], cd["reader_exact_nonbare_singleton_surfaces"]) == (24, 55), "24 recurrent / 55 singleton nonbare exact forms")
    audit.check((cd["primary_lattice_cells"], cd["primary_lattice_exact_occurrences"]) == (40, 422), "40 primary lattice cells / 422 tokens")
    audit.check((cd["sensitivity_lattice_cells"], cd["sensitivity_lattice_exact_occurrences"]) == (64, 468), "64 expanded cells / 468 tokens")
    audit.check((cd["raw_separated_spans"], cd["clean_exact_separated_spans"]) == (185, 115), "185 raw / 115 exact separated spans")
    audit.check(cd["fused_and_separated_left_types"] == 4, "four fused/separated families")
    audit.check((cd["current_alternate_reader_split_candidates"], cd["current_alternate_reader_split_candidates_reader_exact"]) == (1, 0), "one raw alternate split / zero exact")
    audit.check((cd["stolfi_nonbare_fused_occurrences"], cd["stolfi_nonbare_split_occurrences"]) == (47, 0), "Stolfi 47 fused / zero split")
    audit.check(cd["sealed_f84_rows_materialised"] == 0, "corpus materialised no f84/f84r")

    md = model["diagnostics"]
    audit.check(md["recommendation"] == "WHOLE_ONLY", "model selects whole-only")
    audit.check((md["primary_shift_beats_xal"], md["primary_shift_beats_learned_whole"], md["primary_shift_beats_both"]) == (4, 5, 2), "SHIFT wins 4/5/2")
    audit.check((md["primary_core_beats_xal"], md["primary_core_beats_learned_whole"], md["primary_core_beats_both"]) == (6, 7, 4), "CORE wins 6/7/4")
    audit.check(close(md["primary_shift_macro_similarity"], 0.7179701541686327), "SHIFT macro")
    audit.check(close(md["primary_core_macro_similarity"], 0.7291215901148703), "CORE macro")
    audit.check(close(md["primary_xal_macro_similarity"], 0.7095675565978526), "Xal macro")
    audit.check(close(md["primary_learned_whole_macro_similarity"], 0.7025795636371038), "learned macro")
    audit.check((md["raw_suffix_family_surfaces_masked"], md["base_mask_union_surfaces"], md["complete_semantic_mask_surfaces"]) == (742, 958, 996), "742/958/996 leakage masks")
    audit.check((md["gdt754_provenance_surfaces_masked"], md["gdt737_quarantine_surfaces_masked"], md["dal_lineage_surfaces"], md["dal_lineage_new_surfaces_masked"]) == (172, 82, 55, 38), "provenance/quarantine/lineage mask counts")
    audit.check((md["reader_exact_suffix_family_surfaces"], md["reader_exact_suffix_family_occurrences"]) == (568, 3110), "568 exact ending forms / 3110 tokens")
    audit.check((md["reader_exact_dal_surfaces"], md["reader_exact_dal_occurrences"]) == (80, 304), "longest-tail dal partition")
    audit.check((md["reader_exact_dar_surfaces"], md["reader_exact_dar_occurrences"]) == (92, 395), "longest-tail dar partition")
    audit.check((md["reader_exact_al_only_surfaces"], md["reader_exact_al_only_occurrences"]) == (171, 1063), "longest-tail al partition")
    audit.check((md["reader_exact_ar_only_surfaces"], md["reader_exact_ar_only_occurrences"]) == (225, 1348), "longest-tail ar partition")
    audit.check(md["learned_whole_reference_surfaces_after_mask"] == 32, "32 clean learned-whole references")
    audit.check(md["used_axis_surfaces_disjoint_from_semantic_mask"] == 1, "positive-axis sources disjoint from 996 mask")
    audit.check(md["forbidden_f84_or_f84r_materialised"] == 0, "model materialised no f84/f84r")

    expected_counts = {
        "GDT788_107_DAL_FAMILY_CENSUS.tsv": 107,
        "GDT788_304_DAL_EXACT_OCCURRENCES.tsv": 304,
        "GDT788_40_PRIMARY_AL_DAL_AR_DAR_LATTICE.tsv": 40,
        "GDT788_64_EXPANDED_AL_DAL_AR_DAR_LATTICE.tsv": 64,
        "GDT788_185_RAW_X_DAL_SPANS.tsv": 185,
        "GDT788_115_EXACT_X_DAL_SPANS.tsv": 115,
        "GDT788_4_FUSED_SPLIT_FAMILIES.tsv": 4,
        "GDT788_304_STOLFI_BOUNDARY_OCCURRENCES.tsv": 304,
        "GDT788_80_STOLFI_BOUNDARY_SUMMARY.tsv": 80,
        "GDT788_42_FOLIO_BALANCED_PROFILES.tsv": 42,
        "GDT788_996_SEMANTIC_LEAKAGE_MASK.tsv": 996,
        "GDT788_10_LEARNED_WHOLE_CONTROLS.tsv": 10,
        "GDT788_10_PRIMARY_FACTORIAL_TRANSFER.tsv": 10,
        "GDT788_4_MODEL_SUMMARY.tsv": 4,
        "GDT788_140_AXIS_DID_CONTRASTS.tsv": 140,
        "GDT788_14_AXIS_DID_SUMMARY.tsv": 14,
        "GDT788_107_WORKING_DICTIONARY.tsv": 107,
        "GDT788_80_PRACTICAL_PASSAGES.tsv": 80,
        "GDT788_2_HISTORICAL_ARCHITECTURE_CONTROLS.tsv": 2,
        "GDT788_GUARDED_SOURCE_STATS.tsv": 4,
        "GDT788_GDT388_115_SEPARATED_SPAN_PACKET.tsv": 115,
        "GDT788_RELATION_EDGE_CROSSWALK.tsv": 115,
    }
    artifacts: dict[str, list[dict[str, str]]] = {}
    for name, count in expected_counts.items():
        artifacts[name] = read_tsv(ART / name)
        audit.check(len(artifacts[name]) == count, f"{name} row count")

    family = artifacts["GDT788_107_DAL_FAMILY_CENSUS.tsv"]
    audit.check(unique(family, ("surface",)), "family surfaces unique")
    audit.check(sum(int(row["raw_occurrences"]) for row in family) == 415, "family raw total")
    audit.check(sum(int(row["reader_exact_occurrences"]) for row in family) == 304, "family exact total")
    audit.check(sum(int(row["reader_exact_surface"]) for row in family) == 80, "family has 80 exact surfaces")
    audit.check(all(row["surface"].endswith("dal") and row["component_export_credit"] == "0" for row in family), "family ending and zero export")

    exact_rows = artifacts["GDT788_304_DAL_EXACT_OCCURRENCES.tsv"]
    audit.check(unique(exact_rows, ("occurrence_id",)), "exact occurrence IDs unique")
    audit.check(unique(exact_rows, ("page", "locus", "token_index")), "exact natural occurrence keys unique")
    audit.check(all(row["reader_exact"] == "1" and row["surface"].endswith("dal") for row in exact_rows), "exact atlas contract")
    audit.check(not any(row["page"].startswith("f84") for row in exact_rows), "exact atlas excludes f84/f84r")

    primary = artifacts["GDT788_40_PRIMARY_AL_DAL_AR_DAR_LATTICE.tsv"]
    expected_prefixes = {"ch", "che", "o", "oke", "ol", "ote", "qo", "qoke", "sh", "she"}
    audit.check(unique(primary, ("prefix", "tail")), "primary lattice keys unique")
    audit.check({row["prefix"] for row in primary} == expected_prefixes and {row["tail"] for row in primary} == {"al", "dal", "ar", "dar"}, "primary dimensions")
    audit.check(all(int(row["reader_exact_occurrences"]) >= 2 and int(row["reader_exact_physical_folio_count"]) >= 2 for row in primary), "primary cell coverage")
    primary_tails = Counter()
    for row in primary:
        primary_tails[row["tail"]] += int(row["reader_exact_occurrences"])
    audit.check(primary_tails == Counter({"al": 112, "dal": 64, "ar": 167, "dar": 79}), "primary tail totals")

    expanded = artifacts["GDT788_64_EXPANDED_AL_DAL_AR_DAR_LATTICE.tsv"]
    audit.check(unique(expanded, ("prefix", "tail")), "expanded lattice keys unique")
    audit.check(len({row["prefix"] for row in expanded}) == 16 and all(int(row["reader_exact_occurrences"]) >= 1 for row in expanded), "expanded dimensions and coverage")
    expanded_tails = Counter()
    for row in expanded:
        expanded_tails[row["tail"]] += int(row["reader_exact_occurrences"])
    audit.check(expanded_tails == Counter({"al": 122, "dal": 76, "ar": 180, "dar": 90}), "expanded tail totals")

    raw_spans = artifacts["GDT788_185_RAW_X_DAL_SPANS.tsv"]
    clean_spans = artifacts["GDT788_115_EXACT_X_DAL_SPANS.tsv"]
    span_key = ("page", "locus", "left_token_ordinal", "right_token_ordinal")
    audit.check(unique(raw_spans, span_key) and unique(clean_spans, span_key), "span natural keys unique")
    raw_keys = {tuple(row[field] for field in span_key) for row in raw_spans}
    clean_keys = {tuple(row[field] for field in span_key) for row in clean_spans}
    audit.check(clean_keys < raw_keys, "exact spans are a strict raw subset")
    audit.check(all(row["both_tokens_reader_exact"] == row["all_three_readers_preserve_pair"] == row["clean_exact_span"] == "1" for row in clean_spans), "clean span admission gate")
    special = [row for row in raw_spans if row["locus"] == "f78v.2" and row["separated_pair"] == "dal dal"]
    audit.check(len(special) == 1 and special[0]["both_tokens_reader_exact"] == "1" and special[0]["all_three_readers_preserve_pair"] == "0" and tuple(special[0][field] for field in span_key) not in clean_keys, "f78v.2 dal dal correctly excluded")

    fused = artifacts["GDT788_4_FUSED_SPLIT_FAMILIES.tsv"]
    audit.check({row["left_whole"] for row in fused} == {"cheo", "chol", "ol", "y"}, "four fused/split left wholes")
    audit.check(all(row["semantic_credit"] == row["component_export_credit"] == "0" for row in fused), "fused/split rows carry no semantic credit")

    stolfi_occ = artifacts["GDT788_304_STOLFI_BOUNDARY_OCCURRENCES.tsv"]
    stolfi_summary = artifacts["GDT788_80_STOLFI_BOUNDARY_SUMMARY.tsv"]
    audit.check(unique(stolfi_occ, ("occurrence_id",)) and {row["occurrence_id"] for row in stolfi_occ} == {row["occurrence_id"] for row in exact_rows}, "Stolfi occurrence 1:1 atlas")
    audit.check(unique(stolfi_summary, ("surface",)) and {row["surface"] for row in stolfi_summary} == {row["surface"] for row in exact_rows}, "Stolfi summary surface coverage")
    nonbare = Counter(row["boundary_status"] for row in stolfi_occ if row["surface"] != "dal")
    audit.check(nonbare == Counter({"NO_STOLFI_ROWS_FOR_PAGE": 70, "FUSED_WHOLE_AT_SAME_LOCUS": 47, "NO_SAME_LOCUS_ROW": 34, "ALTERNATE_READING_AT_SAME_LOCUS": 5, "OTHER_DAL_BOUNDARY_AT_SAME_LOCUS": 1}), "Stolfi nonbare partition")

    profiles = artifacts["GDT788_42_FOLIO_BALANCED_PROFILES.tsv"]
    audit.check(unique(profiles, ("surface",)), "42 profile surfaces unique")
    audit.check(Counter(row["profile_role"] for row in profiles) == Counter({"PRIMARY_LATTICE": 40, "BARE_CORE": 2}), "profile roles 40+2")
    for row in profiles:
        for field in run_module.load_module("gdt788_model_profile_fields", SRC / "model.py").PROFILE_FIELDS:
            values = json.loads(row[field + "_json"])
            audit.check(not values or close(sum(float(value) for value in values.values()), 1.0), f"normalised profile {row['surface']} {field}")

    mask = artifacts["GDT788_996_SEMANTIC_LEAKAGE_MASK.tsv"]
    audit.check(unique(mask, ("surface",)), "996 mask surfaces unique")
    audit.check(sum(int(row["raw_suffix_family"]) for row in mask) == 742, "mask contains 742 raw family surfaces")
    audit.check(sum(int(row["gdt754_provenance"]) for row in mask) == 172, "mask contains 172 provenance surfaces")
    audit.check(sum(int(row["gdt737_quarantine"]) for row in mask) == 82, "mask contains 82 quarantine surfaces")
    audit.check(sum(int(row["dal_lineage"]) for row in mask) == 55, "mask contains 55 lineage surfaces")
    audit.check(all(row["excluded_from_semantic_neighbours"] == row["excluded_from_learned_whole_donors"] == "1" for row in mask), "mask exclusions explicit")
    masked_surfaces = {row["surface"] for row in mask}

    controls = artifacts["GDT788_10_LEARNED_WHOLE_CONTROLS.tsv"]
    expected_donors = {
        "ch": "chtol", "che": "cheeol", "o": "alam|chl|oteol",
        "oke": "oteeo|oteos", "ol": "chtol|oteeo|oteos",
        "ote": "oteeo|oteos|okeeol", "qo": "alam|chtol|oteol",
        "qoke": "chckhd|keeody|dsheey", "sh": "chtol|sheeo",
        "she": "cheeol|dshedy|sheedy",
    }
    audit.check(unique(controls, ("x",)) and {row["x"]: row["learned_whole_donors"] for row in controls} == expected_donors, "clean donor assignments")
    audit.check(all(row["target_similarity_used_for_selection"] == row["semantic_value_used_for_selection"] == "0" and row["all_donors_outside_996_mask"] == "1" for row in controls), "donor selection blind to target and semantics")
    audit.check(not any(donor in masked_surfaces for row in controls for donor in row["learned_whole_donors"].split("|")), "all learned donors outside mask")

    factorial = artifacts["GDT788_10_PRIMARY_FACTORIAL_TRANSFER.tsv"]
    audit.check(unique(factorial, ("x",)) and {row["x"] for row in factorial} == expected_prefixes, "ten factorial rows")
    audit.check(sum(int(row["shift_beats_both"]) for row in factorial) == 2 and sum(int(row["core_beats_both"]) for row in factorial) == 4, "factorial both-null wins 2/4")
    audit.check({row["x"] for row in factorial if row["semantic_shift_similarity"] == "NA"} == {"ote", "qoke"}, "semantic NA rows ote/qoke")
    audit.check(all(row["score_semantics"] == "TARGET_DEFINED_FIELD_JENSEN_SHANNON_SIMILARITY_NOT_PROBABILITY" and row["component_export_credit"] == "0" for row in factorial), "factorial score and export semantics")

    summaries = {row["view"]: row for row in artifacts["GDT788_4_MODEL_SUMMARY.tsv"]}
    audit.check(set(summaries) == {"FULL", "STRUCTURAL", "LOCAL_NO_REGISTER", "SEMANTIC_ONLY"}, "four model summaries")
    audit.check((summaries["SEMANTIC_ONLY"]["x_types_informative"], summaries["SEMANTIC_ONLY"]["x_types_na"]) == ("8", "2"), "semantic summary 8 informative / 2 NA")
    audit.check(close(float(summaries["FULL"]["shift_macro_similarity"]), 0.7179701541686327) and close(float(summaries["FULL"]["core_macro_similarity"]), 0.7291215901148703), "artifact full model scores")

    axis_rows = artifacts["GDT788_140_AXIS_DID_CONTRASTS.tsv"]
    axis_summary = {(row["radius"], row["axis"]): row for row in artifacts["GDT788_14_AXIS_DID_SUMMARY.tsv"]}
    audit.check(unique(axis_rows, ("radius", "axis", "x")), "140 axis row keys unique")
    audit.check(set(axis_summary) == {(str(radius), axis) for radius in (1, 3) for axis in ("AMOUNT", "VALUE", "MATERIAL", "PART", "PREPARATION", "PROCESS", "CLOSE")}, "14 axis summary cells")
    expected_axis = {
        ("1", "AMOUNT"): (8, 0, 0.019330018041),
        ("3", "AMOUNT"): (9, 2, 0.015416247945),
        ("1", "MATERIAL"): (8, 0, -0.061984131938),
        ("3", "MATERIAL"): (9, 4, -0.038956590404),
        ("1", "PART"): (5, 0, 0.007558407513),
        ("3", "PART"): (7, 0, -0.025018068096),
        ("1", "VALUE"): (10, 5, 0.008581706520),
        ("3", "VALUE"): (10, 5, -0.009055003276),
    }
    for key, expected in expected_axis.items():
        row = axis_summary[key]
        audit.check((int(row["informative_types"]), int(row["same_nonzero_direction_types"])) == expected[:2], f"axis counts {key}")
        audit.check(close(float(row["mean_shared_d_effect"]), expected[2]), f"axis shared effect {key}")
    audit.check(all(row["component_export_credit"] == "0" for row in axis_rows + list(axis_summary.values())), "axis deck exports no component")

    override_rows = read_tsv(OVERRIDES)
    dictionary = artifacts["GDT788_107_WORKING_DICTIONARY.tsv"]
    audit.check(unique(override_rows, ("surface",)) and len(override_rows) == 37, "37 unique override specs")
    audit.check(unique(dictionary, ("surface",)) and {row["surface"] for row in dictionary} == {row["surface"] for row in family}, "dictionary covers all 107 surfaces")
    audit.check(Counter(row["card_class"] for row in dictionary) == Counter({"EXPLICIT_OVERRIDE": 37, "EXACT_SINGLETON_FALLBACK": 46, "RAW_ONLY_FALLBACK": 24}), "dictionary dispatch 37/46/24")
    audit.check(Counter(row["display_scope"] for row in dictionary) == Counter({"READER_EXACT_COMPLETE_WHOLE_ONLY": 80, "RAW_READER_WARNING_ONLY": 27}), "dictionary exact/warning scopes 80/27")
    audit.check(all(row["preferred_working_default_de"] and row["positive_evidence_de"] and row["counterevidence_de"] for row in dictionary), "every card has default and evidence")
    audit.check(all(len({row["preferred_working_default_de"], row["rival_1_de"], row["rival_2_de"]}) == 3 for row in dictionary), "every card has two distinct semantic rivals")
    audit.check(all(row["mechanism_rival_1"] != row["mechanism_rival_2"] and row["preferred_mechanism"] for row in dictionary), "every card has distinct mechanism rivals")
    audit.check(all(zeros(row) and row["replaceable"] == "1" and row["gdt788_new_renderer_license"] == row["portable_dal_component_used"] == "0" for row in dictionary), "dictionary semantic ceiling")
    audit.check(all(0 <= int(row["confidence_0_100_not_probability"]) <= 100 and row["confidence_basis"] == "EDITORIAL_EVIDENCE_WEIGHT_NOT_FORMULA_NOT_PROBABILITY" for row in dictionary), "editorial confidence explicit")
    card = {row["surface"]: row for row in dictionary}
    audit.check(card["dal"]["preferred_working_default_de"] == "Material I, abgemessen" and card["dal"]["confidence_0_100_not_probability"] == "72", "bare dal default and confidence")
    defaults = "\n".join(row["preferred_working_default_de"].lower() for row in dictionary)
    audit.check(not any(term in defaults for term in ("drogenholz", "wurzelrohstoff", "samenrohstoff", "pulverposten")), "retired automatic patient defaults absent")

    passages = artifacts["GDT788_80_PRACTICAL_PASSAGES.tsv"]
    audit.check(unique(passages, ("surface",)) and {row["surface"] for row in passages} == {row["surface"] for row in dictionary if row["reader_exact_surface"] == "1"}, "one passage per exact card")
    audit.check(all(f"⟦{row['surface']} = {row['working_default_de']}⟧" in row["target_focused_line"] for row in passages), "passages focus complete whole")
    audit.check(all(zeros(row) and row["gdt788_new_renderer_license"] == row["portable_dal_component_used"] == "0" for row in passages), "passage semantic ceiling")

    historical = artifacts["GDT788_2_HISTORICAL_ARCHITECTURE_CONTROLS.tsv"]
    audit.check({row["source_id"] for row in historical} == {"HSR008", "HSR010"}, "two historical architecture controls")
    audit.check(all(zeros(row) and row["selects_dal_identity"] == row["selects_dal_segmentation"] == "0" for row in historical), "historical controls give no identity credit")

    source_stats = {row["source"]: row for row in artifacts["GDT788_GUARDED_SOURCE_STATS.tsv"]}
    audit.check(set(source_stats) == {"tokens", "cross", "lines", "stolfi"}, "four guarded source stats")
    audit.check((source_stats["tokens"]["selected_rows"], source_stats["tokens"]["skipped_forbidden"], source_stats["tokens"]["skipped_not_allowed"]) == ("32339", "709", "5940"), "token guard counts")
    audit.check((source_stats["cross"]["selected_rows"], source_stats["cross"]["skipped_forbidden"], source_stats["cross"]["skipped_not_allowed"]) == ("4137", "98", "1151"), "cross guard counts")
    audit.check((source_stats["lines"]["selected_rows"], source_stats["lines"]["skipped_forbidden"], source_stats["lines"]["skipped_not_allowed"]) == ("4137", "98", "1150"), "line guard counts")
    audit.check((source_stats["stolfi"]["selected_rows"], source_stats["stolfi"]["skipped_forbidden"], source_stats["stolfi"]["skipped_not_allowed"], source_stats["stolfi"]["query_allow_pages"]) == ("1220", "33", "1764", "105"), "Stolfi guard and 105-page query")
    audit.check(all(row["base_allowed_pages"] == "179" and row["f84_rows_materialised"] == "0" for row in source_stats.values()), "179-page base and zero f84 rows")

    packet_path = ART / "GDT788_GDT388_115_SEPARATED_SPAN_PACKET.tsv"
    packet = artifacts["GDT788_GDT388_115_SEPARATED_SPAN_PACKET.tsv"]
    crosswalk = artifacts["GDT788_RELATION_EDGE_CROSSWALK.tsv"]
    audit.check(unique(packet, ("edge_id",)) and unique(crosswalk, ("edge_id",)) and {row["edge_id"] for row in packet} == {row["edge_id"] for row in crosswalk}, "packet/crosswalk edge IDs 1:1")
    audit.check(all(row["relation_type"] == "X_PRECEDES_DAL_SEPARATED" and row["geometry_only_selection"] == "FALSE" and row["eligibility_status"] == "INELIGIBLE_EXPLORATORY_TEXT_RELATION" for row in packet), "packet fixed ineligible relation fields")
    audit.check(all(zeros(row) and row["semantic_score_eligible"] == "0" for row in crosswalk), "crosswalk semantic ceiling")
    intake_module = load_module("gdt788_relation_validation", RELATION_INTAKE)
    intake = intake_module.validate_relation_edge_packet(packet_path)
    audit.check(intake["status"] == "VALID_ACQUISITION_NOT_SCORE_READY", "direct relation intake status")
    audit.check(intake["packet_rows"] == 115 and intake["eligible_edges"] == 0 and not intake["score_ready"] and not intake["errors"], "relation packet ineligible and error-free")
    committed_intake = json.loads((ART / "RELATION_PACKET_INTAKE.json").read_text(encoding="utf-8"))
    audit.check(committed_intake == intake, "committed relation intake equals direct intake")
    completed = subprocess.run([str(ROOT / "vmanus-exp"), "check-edge-packet", str(packet_path)], cwd=ROOT, text=True, capture_output=True)
    audit.check(completed.returncode == 0, "vmanus-exp check-edge-packet succeeds")
    audit.check(json.loads(completed.stdout) == intake, "CLI relation intake equals direct intake")

    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    audit.check(result["experiment_id"] == "GDT788" and result["status"].startswith("PARTIAL__107_RAW_FORMS__415_RAW"), "result identity and status")
    audit.check(result["model"]["recommendation"] == "WHOLE_ONLY" and result["adjudication"]["portable_dal_remainder"] == "C0_INACTIVE__WHOLE_ONLY", "result whole-only decision")
    audit.check(result["dictionary"]["raw_forms_with_nonempty_defaults"] == 107 and result["dictionary"]["new_renderer_licenses"] == result["dictionary"]["portable_component_exports"] == 0, "result dictionary coverage and ceiling")
    audit.check(result["confirmed_lexemes"] == result["confirmed_plaintext_clauses"] == result["specific_substances"] == result["component_exports"] == 0, "result semantic ceiling")
    audit.check(result["new_pages"] == result["new_images"] == result["new_ocr"] == result["new_transcriptions"] == result["sealed_pages_accessed"] == 0, "result no new or sealed access")

    report = REPORT.read_text(encoding="utf-8")
    audit.check("WHOLE_ONLY" in report and "Material I, abgemessen" in report, "report states decision and bare default")
    audit.check("2/10" in report and "4/10" in report and "996" in report, "report states primary wins and mask")
    audit.check("null gesplittete" in report and "keine neue globale Renderer-Lizenz" in report, "report states boundary and renderer limits")
    audit.check("Als nächstes folgt `ar`" in report, "report names ar next")

    private_home = "/" + "home" + "/"
    key_marker = "BEGIN " + "PRIVATE KEY"
    for path in sorted(p for p in EXP.rglob("*") if p.is_file() and p != ART / "VALIDATION.json"):
        data = path.read_bytes()
        audit.check(private_home.encode() not in data and key_marker.encode() not in data, f"privacy markers absent {path.relative_to(EXP)}")

    with tempfile.TemporaryDirectory(prefix="gdt788-replay-") as directory:
        replay_artifacts = Path(directory) / "artifacts"
        completed = subprocess.run([sys.executable, "-B", str(RUN), "--artifacts-dir", str(replay_artifacts)], cwd=ROOT, text=True, capture_output=True)
        audit.check(completed.returncode == 0, "runner replay succeeds")
        if completed.returncode != 0:
            raise AssertionError(completed.stderr)
        for name in GENERATED:
            audit.check((replay_artifacts / name).read_bytes() == (ART / name).read_bytes(), f"byte replay {name}")

    validation = {
        "experiment_id": "GDT788",
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
