#!/usr/bin/env python3
"""Validate GDT769 and byte-replay every output declared by run.py."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from types import ModuleType
from typing import Callable, Mapping, Sequence

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt769_liquid_process_role_identity_dispatch"
SRC = EXP / "src"
DEFAULT_ARTIFACTS = EXP / "artifacts"
RUN_PATH = SRC / "run.py"

TARGETS = ("ol", "ckhy", "pcheey", "ols", "otar")
RAW_COUNTS = Counter({"ol": 463, "ckhy": 34, "pcheey": 3, "ols": 17, "otar": 123})
EXACT_COUNTS = Counter({"ol": 376, "ckhy": 25, "pcheey": 3, "ols": 12, "otar": 110})
READER_TARGET_COUNTS = Counter({"ol": 2, "ckhy": 2, "pcheey": 3, "ols": 2, "otar": 3})


def fields(text: str) -> tuple[str, ...]:
    return tuple(text.split())


SOURCE_SCHEMAS = {
    "TARGET_5_ROLE_IDENTITY_SPECS.tsv": fields(
        """target_id surface prior_reader_exact_occurrences prior_scope_note
        portable_null_de concrete_default_de role_lead identity_status
        primary_rival_de secondary_rival_de tertiary_rival_de positive_prior_de
        counterevidence_de required_role_gate required_identity_gate
        minimum_distinct_pages_total ablate_strongest_locus
        minimum_remaining_support_pages target_and_form_family_donors_blocked
        evidence_must_be_target_excluding default_is_translation eva_latin_credit
        substring_export_credit confirmed_lexeme"""
    ),
    "ROLE_5_MODEL_SPECS.tsv": fields(
        """role_model_id role_name_de role_definition_de
        positive_signature_expression contradictory_signature_expression
        dispatch_priority portable_output_de minimum_distinct_pages_total
        ablate_strongest_locus minimum_remaining_support_pages
        identity_dispatch_allowed selection_rule_de failure_output_de
        whole_form_only target_and_family_donors_blocked
        evidence_must_be_target_excluding eva_latin_credit
        substring_export_credit confirmed_role"""
    ),
    "FRAME_SIGNATURE_SPECS.tsv": fields(
        """frame_id frame_name_de radius direction anchor_source
        anchor_surfaces_or_rule count_unit minimum_distinct_pages_total
        ablate_strongest_locus minimum_remaining_support_pages
        reader_exact_required target_and_form_family_donors_blocked
        evidence_must_be_target_excluding description_de positive_for_roles
        negative_for_roles identity_uses eva_latin_credit substring_export_credit
        confirmed_plaintext"""
    ),
    "IDENTITY_CANDIDATE_SPECS.tsv": fields(
        """identity_id target_surface required_role_model candidate_class
        candidate_label_de candidate_renderer_de candidate_status
        required_two_axis_signature fatal_counter_signature
        minimum_distinct_pages_total ablate_strongest_locus
        minimum_remaining_support_pages evidence_rationale_de counterevidence_de
        tie_policy_de historical_category_only default_is_translation
        eva_latin_credit substring_export_credit confirmed_lexeme"""
    ),
    "HISTORICAL_SOURCE_REGISTRY.tsv": fields(
        """source_id source_title dating register url
        relevant_expression_or_category observation_de caveat_de"""
    ),
    "HISTORICAL_IDENTITY_PREDICTIONS.tsv": fields(
        """prediction_id target_surface candidate_label_de candidate_type
        required_role_model historical_source_ids necessary_observable_frames
        counterindications_de renderer_de specificity candidate_status
        tie_policy_de minimum_distinct_pages_total ablate_strongest_locus
        minimum_remaining_support_pages target_and_family_donors_blocked
        evidence_must_be_target_excluding historical_analogy_only
        eva_latin_credit substring_export_credit confirmed_lexeme"""
    ),
    "HISTORICAL_RELATOR_ANALOGUES.tsv": fields(
        """analogue_id date_or_witness source source_locator url class
        historical_architecture_de prediction_for_reader_de discriminates_de
        caveat_de"""
    ),
    "LINE_READER_DEFAULT_SPECS.tsv": fields(
        """line_rank locus line_class ordinal surface reader_exact portable_de
        concrete_default_de primary_rival_de secondary_rival_de evidence_source
        evidence_de counterevidence_de confidence target_flag replaceable
        confirmed_lexeme component_export_credit line_working_reader_de
        line_finding_de"""
    ),
}

SOURCE_COUNTS = {
    "TARGET_5_ROLE_IDENTITY_SPECS.tsv": 5,
    "ROLE_5_MODEL_SPECS.tsv": 5,
    "FRAME_SIGNATURE_SPECS.tsv": 16,
    "HISTORICAL_SOURCE_REGISTRY.tsv": 17,
    "HISTORICAL_IDENTITY_PREDICTIONS.tsv": 35,
    "HISTORICAL_RELATOR_ANALOGUES.tsv": 17,
    "LINE_READER_DEFAULT_SPECS.tsv": 109,
}

EXPECTED_OUTPUTS = (
    "TARGET_640_RAW_OCCURRENCE_ATLAS.tsv",
    "TARGET_526_EXACT_CONTEXT_ATLAS.tsv",
    "TARGET_5_CENSUS.tsv",
    "TARGET_5_ROLE_GEOMETRY.tsv",
    "SIGNATURE_5_SUMMARY.tsv",
    "SUPPORT_52_LOCUS_ATLAS.tsv",
    "LEAVE_ONE_LOCUS_OUT.tsv",
    "CONTROL_SPAN_ATLAS.tsv",
    "DONOR_BLOCK_REGISTRY.tsv",
    "FRAME_16X5_EVIDENCE.tsv",
    "FRAME_LOCUS_EVIDENCE.tsv",
    "ROLE_5X5_SCOREBOARD.tsv",
    "IDENTITY_CANDIDATE_SCOREBOARD.tsv",
    "GDT769_5_WORKING_DICTIONARY.tsv",
    "TWELVE_COMPLETE_LINE_READER.tsv",
    "HISTORICAL_ROLE_IDENTITY_READER.md",
    "RESULT.json",
)

OUTPUT_COUNTS = {
    "TARGET_640_RAW_OCCURRENCE_ATLAS.tsv": 640,
    "TARGET_526_EXACT_CONTEXT_ATLAS.tsv": 526,
    "TARGET_5_CENSUS.tsv": 5,
    "TARGET_5_ROLE_GEOMETRY.tsv": 5,
    "SIGNATURE_5_SUMMARY.tsv": 5,
    "SUPPORT_52_LOCUS_ATLAS.tsv": 52,
    "LEAVE_ONE_LOCUS_OUT.tsv": 52,
    "CONTROL_SPAN_ATLAS.tsv": 307,
    "DONOR_BLOCK_REGISTRY.tsv": 1095,
    "FRAME_16X5_EVIDENCE.tsv": 80,
    "FRAME_LOCUS_EVIDENCE.tsv": 711,
    "ROLE_5X5_SCOREBOARD.tsv": 25,
    "GDT769_5_WORKING_DICTIONARY.tsv": 5,
    "TWELVE_COMPLETE_LINE_READER.tsv": 109,
}

REQUIRED_OUTPUT_COLUMNS = {
    "TARGET_640_RAW_OCCURRENCE_ATLAS.tsv": fields(
        "raw_occurrence_id target_occurrence_id surface page locus ordinal "
        "reader_exact written_line_eva"
    ),
    "TARGET_526_EXACT_CONTEXT_ATLAS.tsv": fields(
        "raw_occurrence_id target_occurrence_id surface page locus ordinal "
        "reader_exact context_views direct_signatures semantic_identity_credit "
        "component_export_credit"
    ),
    "TARGET_5_CENSUS.tsv": fields(
        "surface guarded_raw_occurrences reader_exact_occurrences "
        "nonexact_occurrences guarded_raw_pages reader_exact_pages "
        "guarded_raw_loci reader_exact_loci semantic_identity_credit "
        "component_export_credit"
    ),
    "FRAME_16X5_EVIDENCE.tsv": fields(
        "target_surface frame_id support_occurrences support_loci support_pages "
        "strongest_support_locus loo_remaining_occurrences loo_remaining_loci "
        "loo_remaining_pages minimum_distinct_pages_total "
        "minimum_remaining_support_pages passes_total_page_gate "
        "passes_strongest_locus_loo frame_selected default_is_translation "
        "eva_latin_credit substring_export_credit confirmed_lexeme "
        "confirmed_plaintext component_export_credit"
    ),
    "FRAME_LOCUS_EVIDENCE.tsv": fields(
        "frame_id target_surface target_occurrence_id page locus ordinal "
        "reader_exact target_excluding_evidence default_is_translation "
        "eva_latin_credit substring_export_credit confirmed_lexeme "
        "confirmed_plaintext component_export_credit"
    ),
    "ROLE_5X5_SCOREBOARD.tsv": fields(
        "target_surface role_model_id positive_signature_pass "
        "contradictory_signature_triggered support_pages support_loci "
        "strongest_support_locus loo_remaining_pages passes_total_page_gate "
        "passes_strongest_locus_loo role_gate_pass role_selected "
        "special_gate_detail same_context_conjunction_detail role_rank "
        "default_is_translation eva_latin_credit substring_export_credit "
        "confirmed_lexeme confirmed_plaintext component_export_credit"
    ),
    "IDENTITY_CANDIDATE_SCOREBOARD.tsv": fields(
        "identity_id target_surface required_role_model candidate_label_de "
        "historical_predictions historical_prediction_count "
        "historical_predictions_create_voynich_evidence identity_gate_pass "
        "identity_selected default_is_translation eva_latin_credit "
        "substring_export_credit confirmed_lexeme confirmed_plaintext "
        "component_export_credit"
    ),
    "GDT769_5_WORKING_DICTIONARY.tsv": fields(
        "surface selected_role_model role_disposition role_selection_basis "
        "role_evidence_superiority supported_role_rivals selected_identity_id "
        "working_identity_label_de working_default_de working_confidence "
        "primary_rival_de primary_rival_identity_id identity_role_consistent "
        "whole_form_only structural_only default_is_translation "
        "eva_latin_credit substring_export_credit confirmed_lexeme "
        "confirmed_plaintext component_export_credit"
    ),
    "TWELVE_COMPLETE_LINE_READER.tsv": fields(
        "line_rank locus ordinal surface reader_exact portable_de "
        "concrete_default_de primary_rival_de secondary_rival_de "
        "evidence_source evidence_de counterevidence_de confidence target_flag "
        "replaceable written_line_eva line_working_reader_de line_finding_de "
        "dictionary_selected_role dictionary_working_default_de "
        "dictionary_working_confidence default_is_translation "
        "confirmed_lexeme confirmed_plaintext component_export_credit"
    ),
}

EXPECTED_DICTIONARY = {
    "ol": (
        "R05_SEQUENCE_FIELD_LINKER",
        "I36_OL_FIELD_RELATOR",
        "und/mit; nach einer Menge von/aus",
        "C1_LOCAL_FRAME__C0_ROLE_TIEBREAK",
        "Zubereitungsbasis",
    ),
    "ckhy": ("OPEN", "OPEN", "mischen", "C0_RIVAL_ONLY", "Mischung oder Kompositum"),
    "pcheey": (
        "R04_BOUND_RECORD_FIELD",
        "I10_PCHEEY_FIELD",
        "gebundenes Zubereitungs-/Form-II-Feld",
        "C1_REPLICATED_REPLACEABLE",
        "Paste, Salben- oder Mischform II",
    ),
    "ols": ("R04_BOUND_RECORD_FIELD", "OPEN", "Maß-/Produktposten", "C0_RIVAL_ONLY", "Abschlussprodukt"),
    "otar": (
        "R05_SEQUENCE_FIELD_LINKER",
        "I23_OTAR_LINKER",
        "weiter/dann",
        "C1_LOCAL_FRAME__C0_ROLE_TIEBREAK",
        "bis",
    ),
}

EXPECTED_SOURCE_DEFAULTS = {
    "ol": ("und/mit; nach einer Menge von/aus", "R05_SEQUENCE_FIELD_LINKER"),
    "ckhy": ("mischen", "R02_PROCESS_OPERATION"),
    "pcheey": ("gebundenes Zubereitungs-/Form-II-Feld", "R04_BOUND_RECORD_FIELD"),
    "ols": ("Maß-/Produktposten", "R04_BOUND_RECORD_FIELD"),
    "otar": ("weiter/dann", "R05_SEQUENCE_FIELD_LINKER"),
}

ZERO_FIELDS = {
    "semantic_identity_credit",
    "component_export_credit",
    "component_exports",
    "default_is_translation",
    "role_is_translation",
    "eva_latin_credit",
    "eva_latin_identity_credit",
    "substring_export_credit",
    "substring_identity_export_credit",
    "confirmed_role",
    "confirmed_lexeme",
    "confirmed_lexemes",
    "confirmed_plaintext",
    "confirmed_plaintext_clauses",
    "historical_predictions_create_voynich_evidence",
    "historical_category_fit_credit",
    "independent_voynich_discriminator",
    "creates_voynich_evidence",
}

FRAME_REF = re.compile(r"\bF\d{2}_[A-Za-z0-9_]+\b")
SEALED = re.compile(r"(?i)(?:^|[^a-z0-9])f84(?:r)?(?:[^a-z0-9]|$)")
BANNED_GENERIC = ("arbeitsgut", "arbeitsschritt", "arbeitsgegenstand", "work item")


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_tsv(path: Path) -> tuple[tuple[str, ...], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        header = tuple(reader.fieldnames or ())
        rows = list(reader)
    if not header or len(header) != len(set(header)):
        raise AssertionError(f"invalid TSV header: {path.name}")
    if any(None in row for row in rows):
        raise AssertionError(f"row wider than header: {path.name}")
    return header, rows


def is_zero(value: object) -> bool:
    return value is False or value == 0 or str(value).strip().casefold() in {
        "",
        "0",
        "false",
        "none",
        "zero",
    }


def parse_json(value: str, label: str) -> object:
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"invalid JSON in {label}: {exc}") from exc


def recursive_zero(
    value: object, check: Callable[[bool, str], None], path: str = "result"
) -> int:
    count = 0
    if isinstance(value, Mapping):
        for key, item in value.items():
            name = str(key).casefold()
            child = f"{path}.{key}"
            if name in ZERO_FIELDS or name.startswith("confirmed_"):
                check(is_zero(item), f"nonzero claim {child}: {item!r}")
                count += 1
            count += recursive_zero(item, check, child)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            count += recursive_zero(item, check, f"{path}[{index}]")
    return count


def resolve_path(path: Path) -> Path:
    return path.resolve() if path.is_absolute() else (ROOT / path).resolve()


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return "<external-artifact-dir>"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACTS)
    parser.add_argument(
        "--output",
        type=Path,
        help="explicit validation report path; otherwise only normal artifacts get VALIDATION.json",
    )
    parser.add_argument("--quiet", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    artifact_dir = resolve_path(args.artifact_dir)
    checks = 0

    def check(condition: bool, message: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            raise AssertionError(message)

    run = load_module("gdt769_run_for_validation", RUN_PATH)
    declared = tuple(str(name) for name in run.OUTPUT_NAMES)
    check(declared == EXPECTED_OUTPUTS, "run.py output contract changed")
    check(len(declared) == len(set(declared)), "duplicate output names")
    check("VALIDATION.json" not in declared, "VALIDATION.json is not a builder output")
    check(artifact_dir.is_dir(), f"artifact directory missing: {artifact_dir}")
    for name in declared:
        check(Path(name).name == name, f"unsafe output name: {name}")
        check((artifact_dir / name).is_file(), f"missing output: {name}")
        check((artifact_dir / name).stat().st_size > 0, f"empty output: {name}")

    source_tables: dict[str, tuple[tuple[str, ...], list[dict[str, str]]]] = {}
    for name, schema in SOURCE_SCHEMAS.items():
        header, rows = read_tsv(SRC / name)
        source_tables[name] = header, rows
        check(header == schema, f"source schema/order changed: {name}")
        if name == "IDENTITY_CANDIDATE_SPECS.tsv":
            check(len(rows) >= 37, "identity deck fell below 37 candidates")
        else:
            check(len(rows) == SOURCE_COUNTS[name], f"source count changed: {name}")
        for number, row in enumerate(rows, 2):
            check(all(row[field].strip() for field in header), f"blank source cell {name}:{number}")

    targets = source_tables["TARGET_5_ROLE_IDENTITY_SPECS.tsv"][1]
    roles = source_tables["ROLE_5_MODEL_SPECS.tsv"][1]
    frames = source_tables["FRAME_SIGNATURE_SPECS.tsv"][1]
    identities = source_tables["IDENTITY_CANDIDATE_SPECS.tsv"][1]
    histories = source_tables["HISTORICAL_IDENTITY_PREDICTIONS.tsv"][1]
    historical_sources = source_tables["HISTORICAL_SOURCE_REGISTRY.tsv"][1]
    reader_specs = source_tables["LINE_READER_DEFAULT_SPECS.tsv"][1]

    target_by_surface = {row["surface"]: row for row in targets}
    role_by_id = {row["role_model_id"]: row for row in roles}
    frame_by_id = {row["frame_id"]: row for row in frames}
    identity_by_id = {row["identity_id"]: row for row in identities}
    source_ids = {row["source_id"] for row in historical_sources}
    history_ids = {row["prediction_id"] for row in histories}
    check(tuple(row["surface"] for row in targets) == TARGETS, "target order changed")
    check(len(target_by_surface) == 5, "duplicate target surface")
    check(len(role_by_id) == 5, "duplicate role ID")
    check(len(frame_by_id) == 16, "duplicate frame ID")
    check(len(identity_by_id) == len(identities), "duplicate identity ID")
    check(len(source_ids) == 17 and len(history_ids) == 35, "duplicate historical ID")
    check(
        {key.split("_", 1)[0] for key in role_by_id} == {f"R{i:02d}" for i in range(1, 6)},
        "roles are not R01..R05",
    )
    check(
        {key.split("_", 1)[0] for key in frame_by_id} == {f"F{i:02d}" for i in range(1, 17)},
        "frames are not F01..F16",
    )
    for surface, (default, lead) in EXPECTED_SOURCE_DEFAULTS.items():
        row = target_by_surface[surface]
        check(row["concrete_default_de"] == default, f"source default changed: {surface}")
        check(row["role_lead"] == lead, f"source role lead changed: {surface}")
        check(int(row["prior_reader_exact_occurrences"]) == EXACT_COUNTS[surface], f"source prior changed: {surface}")
    for row in roles:
        role_expression = (
            row["positive_signature_expression"]
            + " "
            + row["contradictory_signature_expression"]
        )
        check(
            set(FRAME_REF.findall(role_expression)) <= set(frame_by_id),
            f"unknown frame in {row['role_model_id']}",
        )
    for row in identities:
        check(row["target_surface"] in TARGETS, f"unknown identity target: {row['identity_id']}")
        check(row["required_role_model"] in role_by_id, f"unknown identity role: {row['identity_id']}")
        check(set(FRAME_REF.findall(row["required_two_axis_signature"])) <= set(frame_by_id), f"unknown identity frame: {row['identity_id']}")
    for row in histories:
        check(row["target_surface"] in TARGETS, f"unknown historical target: {row['prediction_id']}")
        check(set(row["historical_source_ids"].split("|")) <= source_ids, f"unknown historical source: {row['prediction_id']}")
        check(set(FRAME_REF.findall(row["necessary_observable_frames"])) <= set(frame_by_id), f"unknown historical frame: {row['prediction_id']}")
        check(row["historical_analogy_only"] == "1", f"historical row became evidence: {row['prediction_id']}")

    r03_spec = next(row for row in roles if row["role_model_id"].startswith("R03_"))
    r05_spec = next(row for row in roles if row["role_model_id"].startswith("R05_"))
    check("ON_SAME_TARGET_OCCURRENCE" in r03_spec["positive_signature_expression"], "R03 same-occurrence rule missing")
    check("selben Targetvorkommen" in r03_spec["selection_rule_de"], "R03 prose gate missing")
    check("F14_MEDIAL_TWO_SIDED_LINKER" in r05_spec["positive_signature_expression"], "R05 F14 gate missing")
    check("F15_STATE_TRANSITION_BRIDGE" in r05_spec["positive_signature_expression"], "R05 F15 gate missing")
    check("F16_RELATIONAL_AMOUNT_ORDER" in r05_spec["positive_signature_expression"], "R05 F16 gate missing")
    check(int(r05_spec["minimum_distinct_pages_total"]) == 3, "R05 total page gate != 3")
    check(int(r05_spec["minimum_remaining_support_pages"]) == 2, "R05 LOO page gate != 2")

    for name, (header, rows) in source_tables.items():
        zero_columns = set(header) & ZERO_FIELDS
        if not name.startswith("HISTORICAL_SOURCE") and not name.startswith("HISTORICAL_RELATOR"):
            check(bool(zero_columns), f"source lacks a zero-credit field: {name}")
        for number, row in enumerate(rows, 2):
            for column in zero_columns:
                check(is_zero(row[column]), f"nonzero source claim {name}:{number}.{column}")

    # Every token gets a concrete default, evidence, confidence, and two rivals.
    reader_groups: defaultdict[int, list[dict[str, str]]] = defaultdict(list)
    for row in reader_specs:
        reader_groups[int(row["line_rank"])].append(row)
        check(row["target_flag"] == str(int(row["surface"] in TARGETS)), f"target flag mismatch {row['locus']}@{row['ordinal']}")
        for column in (
            "portable_de",
            "concrete_default_de",
            "primary_rival_de",
            "secondary_rival_de",
            "evidence_source",
            "evidence_de",
            "counterevidence_de",
            "confidence",
        ):
            check(bool(row[column].strip()), f"reader lacks {column}: {row['locus']}@{row['ordinal']}")
        values = {
            row["concrete_default_de"].strip().casefold(),
            row["primary_rival_de"].strip().casefold(),
            row["secondary_rival_de"].strip().casefold(),
        }
        check(len(values) == 3, f"reader default/rival collision {row['locus']}@{row['ordinal']}")
        check(row["confidence"].startswith("C"), f"reader confidence malformed {row['locus']}@{row['ordinal']}")
        check(row["replaceable"] == "1", f"reader token not replaceable {row['locus']}@{row['ordinal']}")
        active = (row["portable_de"] + " " + row["concrete_default_de"] + " " + row["line_working_reader_de"]).casefold()
        check(not any(term in active for term in BANNED_GENERIC), f"generic reader filler {row['locus']}@{row['ordinal']}")
    check(sorted(reader_groups) == list(range(1, 13)), "reader ranks are not 1..12")
    check(len({rows[0]["locus"] for rows in reader_groups.values()}) == 12, "reader does not contain 12 unique lines")
    for rank, rows in reader_groups.items():
        check([int(row["ordinal"]) for row in rows] == list(range(1, len(rows) + 1)), f"reader ordinals broken at rank {rank}")
        check(len({row["line_working_reader_de"] for row in rows}) == 1, f"multiple line readers at rank {rank}")
        check(len({row["line_finding_de"] for row in rows}) == 1, f"multiple line findings at rank {rank}")
    check(len(reader_specs) == 109, "reader token count != 109")
    check(sum(int(row["reader_exact"]) for row in reader_specs) == 106, "reader exact count != 106")
    check(Counter(row["surface"] for row in reader_specs if row["target_flag"] == "1") == READER_TARGET_COUNTS, "reader target coverage changed")

    sain = next(row for row in reader_specs if row["locus"] == "f10v.1" and row["surface"] == "sain")
    sain_active = " ".join(sain[column] for column in ("portable_de", "concrete_default_de", "line_working_reader_de")).casefold()
    check(sain["concrete_default_de"] == "zwei Drachmen", "sain fused default changed")
    check("saat" not in sain_active and "samen" not in sain_active, "sain leaked a seed reading")
    check(sain["confidence"] == "C1_RECURRENT_FUSED_VALUE__C0_UNIT", "sain confidence changed")
    chekar = next(row for row in reader_specs if row["locus"] == "f75r.43" and row["surface"] == "chekar")
    check(chekar["concrete_default_de"] == "Zwischenzubereitung", "chekar local C0 changed")
    check(chekar["confidence"] == "C0_LOCAL_FORCED_DEFAULT", "chekar is not forced C0")
    check("SOURCE_COMPOSED_QUARANTINE" in chekar["evidence_source"], "chekar quarantine missing")
    check("heiß" not in chekar["concrete_default_de"].casefold() and "trocken" not in chekar["concrete_default_de"].casefold(), "chekar exported composition semantics")

    tables: dict[str, tuple[tuple[str, ...], list[dict[str, str]]]] = {}
    for name in declared:
        if not name.endswith(".tsv"):
            continue
        header, rows = read_tsv(artifact_dir / name)
        tables[name] = header, rows
        if name == "IDENTITY_CANDIDATE_SCOREBOARD.tsv":
            check(len(rows) == len(identities) and len(rows) >= 37, "dynamic identity scoreboard count changed")
        else:
            check(len(rows) == OUTPUT_COUNTS[name], f"output count changed: {name}")
        required = REQUIRED_OUTPUT_COLUMNS.get(name, ())
        check(set(required) <= set(header), f"output schema missing columns: {name}")

    raw = tables["TARGET_640_RAW_OCCURRENCE_ATLAS.tsv"][1]
    exact = tables["TARGET_526_EXACT_CONTEXT_ATLAS.tsv"][1]
    census = tables["TARGET_5_CENSUS.tsv"][1]
    frame_rows = tables["FRAME_16X5_EVIDENCE.tsv"][1]
    frame_evidence = tables["FRAME_LOCUS_EVIDENCE.tsv"][1]
    role_rows = tables["ROLE_5X5_SCOREBOARD.tsv"][1]
    identity_rows = tables["IDENTITY_CANDIDATE_SCOREBOARD.tsv"][1]
    dictionary_rows = tables["GDT769_5_WORKING_DICTIONARY.tsv"][1]
    reader_rows = tables["TWELVE_COMPLETE_LINE_READER.tsv"][1]

    check(Counter(row["surface"] for row in raw) == RAW_COUNTS, "five raw target counts changed")
    check(Counter(row["surface"] for row in exact) == EXACT_COUNTS, "five exact target counts changed")
    check(sum(RAW_COUNTS.values()) == 640 and sum(EXACT_COUNTS.values()) == 526, "640/526 totals changed")
    exact_raw = [row for row in raw if row["reader_exact"] == "1"]
    check(len(exact_raw) == 526, "raw atlas exact split changed")
    check(all(row["target_occurrence_id"] for row in exact_raw), "exact raw row lacks exact ID")
    check(all(not row["target_occurrence_id"] for row in raw if row["reader_exact"] == "0"), "nonexact raw row has exact ID")
    exact_by_id = {row["target_occurrence_id"]: row for row in exact}
    check(len(exact_by_id) == 526, "exact occurrence IDs are not unique")
    check({row["target_occurrence_id"] for row in exact_raw} == set(exact_by_id), "raw/exact identity sets differ")
    census_by_surface = {row["surface"]: row for row in census}
    check(set(census_by_surface) == set(TARGETS), "census target set changed")
    for surface in TARGETS:
        row = census_by_surface[surface]
        check(int(row["guarded_raw_occurrences"]) == RAW_COUNTS[surface], f"census raw mismatch {surface}")
        check(int(row["reader_exact_occurrences"]) == EXACT_COUNTS[surface], f"census exact mismatch {surface}")
        check(int(row["nonexact_occurrences"]) == RAW_COUNTS[surface] - EXACT_COUNTS[surface], f"census nonexact mismatch {surface}")

    frame_matrix = {(row["target_surface"], row["frame_id"]): row for row in frame_rows}
    role_matrix = {(row["target_surface"], row["role_model_id"]): row for row in role_rows}
    check(len(frame_matrix) == 80, "frame matrix is not 16x5")
    check(len(role_matrix) == 25, "role matrix is not 5x5")
    check(set(frame_matrix) == {(surface, frame_id) for surface in TARGETS for frame_id in frame_by_id}, "frame matrix keys incomplete")
    check(set(role_matrix) == {(surface, role_id) for surface in TARGETS for role_id in role_by_id}, "role matrix keys incomplete")

    evidence_by_key: defaultdict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    occurrence_frames: defaultdict[tuple[str, str], set[str]] = defaultdict(set)
    for row in frame_evidence:
        key = (row["target_surface"], row["frame_id"])
        check(key in frame_matrix, f"orphan frame evidence {key}")
        occurrence_id = row["target_occurrence_id"]
        check(occurrence_id in exact_by_id, f"unknown frame occurrence {occurrence_id}")
        occurrence = exact_by_id[occurrence_id]
        check((row["target_surface"], row["page"], row["locus"], row["ordinal"]) == (occurrence["surface"], occurrence["page"], occurrence["locus"], occurrence["ordinal"]), f"frame evidence location mismatch {occurrence_id}")
        check(row["reader_exact"] == "1" and row["target_excluding_evidence"] == "1", f"unguarded frame evidence {occurrence_id}")
        evidence_by_key[key].append(row)
        occurrence_frames[(row["target_surface"], occurrence_id)].add(row["frame_id"])
    for key, row in frame_matrix.items():
        if key[1] == "F13_SECOND_PAGE_AFTER_ABLATION":
            # F13 is the declared replication meta-frame.  Its support is the
            # full multiset of evidence from the other fifteen frames and is
            # therefore intentionally absent from FRAME_LOCUS_EVIDENCE itself.
            evidence = [
                item
                for (target, frame_id), items in evidence_by_key.items()
                if target == key[0] and frame_id != key[1]
                for item in items
            ]
        else:
            evidence = evidence_by_key[key]
        strongest = row["strongest_support_locus"]
        remaining = [item for item in evidence if item["locus"] != strongest]
        check(int(row["support_occurrences"]) == len(evidence), f"frame support mismatch {key}")
        check(int(row["support_loci"]) == len({item["locus"] for item in evidence}), f"frame loci mismatch {key}")
        check(int(row["support_pages"]) == len({item["page"] for item in evidence}), f"frame pages mismatch {key}")
        check(int(row["loo_remaining_occurrences"]) == len(remaining), f"frame LOO occurrence mismatch {key}")
        check(int(row["loo_remaining_loci"]) == len({item["locus"] for item in remaining}), f"frame LOO loci mismatch {key}")
        check(int(row["loo_remaining_pages"]) == len({item["page"] for item in remaining}), f"frame LOO pages mismatch {key}")
        total_gate = int(row["support_pages"]) >= int(row["minimum_distinct_pages_total"])
        loo_gate = int(row["loo_remaining_pages"]) >= int(row["minimum_remaining_support_pages"])
        check(int(row["passes_total_page_gate"]) == int(total_gate), f"frame total gate mismatch {key}")
        check(int(row["passes_strongest_locus_loo"]) == int(loo_gate), f"frame LOO gate mismatch {key}")
        if key[1] == "F13_SECOND_PAGE_AFTER_ABLATION":
            axes = {
                axis
                for item in remaining
                for axis in parse_json(item["axis_families"], f"{key}.axis_families")
                if axis != "REPLICATION_CONTROL"
            }
            selected = total_gate and loo_gate and bool(axes)
        else:
            selected = total_gate and loo_gate
        check(int(row["frame_selected"]) == int(selected), f"frame selection mismatch {key}")

    # R03 is reconstructed from occurrence IDs, never from separately pooled pages.
    r03_id = r03_spec["role_model_id"]
    left = {"F01_AMOUNT_DIRECT", "F02_VALUE_DIRECT"}
    right = {"F06_TARGET_BEFORE_PROCESS", "F07_LINE_FINAL_OR_CLOSE"}
    for surface in TARGETS:
        row = role_matrix[(surface, r03_id)]
        detail = parse_json(row["same_context_conjunction_detail"], f"{surface}.R03")
        check(isinstance(detail, dict), f"R03 detail is not an object: {surface}")
        assert isinstance(detail, dict)
        expected_ids = {
            occurrence_id
            for (target, occurrence_id), present in occurrence_frames.items()
            if target == surface and present & left and present & right
        }
        check(detail.get("same_occurrence_conjunction_required") == 1, f"R03 conjunction disabled: {surface}")
        check(set(detail.get("supporting_occurrence_ids", [])) == expected_ids, f"R03 cross-occurrence pooling: {surface}")
        check(int(detail.get("supporting_occurrence_count", -1)) == len(expected_ids), f"R03 support count mismatch: {surface}")
        pages = {exact_by_id[item]["page"] for item in expected_ids}
        check(int(row["support_pages"]) == len(pages), f"R03 page count mismatch: {surface}")
        strongest = row["strongest_support_locus"]
        remaining = {item for item in expected_ids if exact_by_id[item]["locus"] != strongest}
        check(set(detail.get("loo_supporting_occurrence_ids", [])) == remaining, f"R03 LOO mismatch: {surface}")
    check(role_matrix[("ol", r03_id)]["role_gate_pass"] == "1", "ol R03 supported rival changed")
    check(all(role_matrix[(surface, r03_id)]["role_gate_pass"] == "0" for surface in TARGETS if surface != "ol"), "unexpected R03 winner outside ol")

    # R05 gets pages only from F15/F16 occurrences that are also locally F14.
    r05_id = r05_spec["role_model_id"]
    expected_r05_pages = {"ol": (29, 29), "ckhy": (2, 1), "pcheey": (1, 0), "ols": (0, 0), "otar": (7, 6)}
    for surface in TARGETS:
        row = role_matrix[(surface, r05_id)]
        detail = parse_json(row["same_context_conjunction_detail"], f"{surface}.R05")
        special = parse_json(row["special_gate_detail"], f"{surface}.R05.special")
        check(isinstance(detail, dict) and isinstance(special, dict), f"R05 detail malformed: {surface}")
        assert isinstance(detail, dict) and isinstance(special, dict)
        f14 = {item["target_occurrence_id"] for item in evidence_by_key[(surface, "F14_MEDIAL_TWO_SIDED_LINKER")]}
        f15 = {item["target_occurrence_id"] for item in evidence_by_key[(surface, "F15_STATE_TRANSITION_BRIDGE")]}
        f16 = {item["target_occurrence_id"] for item in evidence_by_key[(surface, "F16_RELATIONAL_AMOUNT_ORDER")]}
        local = f14 & (f15 | f16)
        check(set(detail.get("local_discriminating_occurrence_ids", [])) == local, f"R05 local conjunction mismatch: {surface}")
        check(detail.get("f14_contributes_support_pages") == 0, f"F14 contributes pages: {surface}")
        pages = {exact_by_id[item]["page"] for item in local}
        strongest = row["strongest_support_locus"]
        remaining_pages = {exact_by_id[item]["page"] for item in local if exact_by_id[item]["locus"] != strongest}
        check((len(pages), len(remaining_pages)) == expected_r05_pages[surface], f"R05 F15/F16 page evidence changed: {surface}")
        check((int(row["support_pages"]), int(row["loo_remaining_pages"])) == expected_r05_pages[surface], f"R05 counted F14 pages: {surface}")
        check(special.get("r05_rough_f14_alone_has_zero_selection_credit") == 1, f"F14-alone gate disabled: {surface}")
        check(special.get("r05_requires_f14_and_f15_or_f16") == 1, f"R05 local discriminator gate disabled: {surface}")
    check({surface for surface in TARGETS if role_matrix[(surface, r05_id)]["role_gate_pass"] == "1"} == {"ol", "otar"}, "R05 pass set changed")

    identity_rows_by_id = {row["identity_id"]: row for row in identity_rows}
    check(set(identity_rows_by_id) == set(identity_by_id), "identity source/output IDs differ")
    prediction_attachments = 0
    for identity_id, row in identity_rows_by_id.items():
        check(row["target_surface"] == identity_by_id[identity_id]["target_surface"], f"identity target rebound mismatch {identity_id}")
        check(row["required_role_model"] == identity_by_id[identity_id]["required_role_model"], f"identity role rebound mismatch {identity_id}")
        attached = parse_json(row["historical_predictions"], f"{identity_id}.history")
        check(isinstance(attached, list), f"identity history malformed {identity_id}")
        assert isinstance(attached, list)
        check(int(row["historical_prediction_count"]) == len(attached), f"history attachment count mismatch {identity_id}")
        check(row["historical_predictions_create_voynich_evidence"] == "0", f"history scored for {identity_id}")
        prediction_attachments += len(attached)
        for item in attached:
            check(isinstance(item, dict), f"history attachment is not an object {identity_id}")
            assert isinstance(item, dict)
            check(item.get("prediction_id") in history_ids, f"unknown attached history {identity_id}")
            check(item.get("target_surface") == row["target_surface"], f"cross-target history {identity_id}")
            for column in (
                "historical_category_fit_credit",
                "independent_voynich_discriminator",
                "creates_voynich_evidence",
                "eva_latin_credit",
                "substring_export_credit",
                "confirmed_lexeme",
            ):
                check(is_zero(item.get(column)), f"historical evidence credit {identity_id}.{column}")
    check(prediction_attachments > 0, "historical registry was not attached as analogy")

    dictionary = {row["surface"]: row for row in dictionary_rows}
    check(set(dictionary) == set(TARGETS), "dictionary target set changed")
    selected_roles = {(row["target_surface"], row["role_model_id"]) for row in role_rows if row["role_selected"] == "1"}
    selected_identities = {row["identity_id"] for row in identity_rows if row["identity_selected"] == "1"}
    check(len(selected_roles) == 4, "selected role count != 4")
    check(len(selected_identities) == 3, "selected identity count != 3")
    tied_role_targets = {"ol", "ols", "otar"}
    for surface, expected in EXPECTED_DICTIONARY.items():
        row = dictionary[surface]
        actual = (
            row["selected_role_model"],
            row["selected_identity_id"],
            row["working_default_de"],
            row["working_confidence"],
            row["primary_rival_de"],
        )
        check(actual == expected, f"dictionary outcome changed: {surface}")
        check(row["identity_role_consistent"] == "1", f"role/identity inconsistency: {surface}")
        check(row["whole_form_only"] == "1", f"non-whole dictionary entry: {surface}")
        if surface in tied_role_targets:
            check(
                row["role_disposition"] == "SELECTED_WORKING_SPECIFICITY_TIEBREAK",
                f"role tie hidden for {surface}",
            )
            check(
                row["role_selection_basis"]
                == "SPECIFICITY_DISPATCH_PRIORITY_AMONG_EQUAL_GATE_SCORES",
                f"role tie basis changed for {surface}",
            )
            check(row["role_evidence_superiority"] == "0", f"false role superiority for {surface}")
            check(row["supported_role_rivals"] != "NONE", f"supported role rival hidden for {surface}")
        elif surface == "pcheey":
            check(row["role_selection_basis"] == "UNIQUE_TOP_ROLE_GATE", "pcheey is no longer the unique role result")
            check(row["role_evidence_superiority"] == "1", "pcheey unique-role flag changed")
        else:
            check(row["role_selection_basis"] == "NO_ROLE_GATE_PASSED", "ckhy OPEN basis changed")
            check(row["role_evidence_superiority"] == "0", "ckhy claims role superiority")
        selected_identity = row["selected_identity_id"]
        rival_identity = row["primary_rival_identity_id"]
        check(rival_identity in identity_by_id, f"unknown rival identity: {surface}")
        check(identity_by_id[rival_identity]["target_surface"] == surface, f"cross-target rival: {surface}")
        check(identity_by_id[rival_identity]["candidate_label_de"] == row["primary_rival_de"], f"rival label mismatch: {surface}")
        check(selected_identity != rival_identity, f"self-rival identity: {surface}")
        check(row["working_identity_label_de"].casefold() != row["primary_rival_de"].casefold(), f"self-rival label: {surface}")
        if selected_identity != "OPEN":
            check(selected_identity in selected_identities, f"dictionary identity not selected: {surface}")
            check(identity_by_id[selected_identity]["required_role_model"] == row["selected_role_model"], f"dictionary identity role mismatch: {surface}")
        if row["selected_role_model"] != "OPEN":
            check((surface, row["selected_role_model"]) in selected_roles, f"dictionary role not selected: {surface}")
    check(dictionary["otar"]["primary_rival_identity_id"] == "I25_OTAR_UNTIL", "otar primary rival is not the endpoint rival")
    check("I24_OTAR_THEN" != dictionary["otar"]["primary_rival_identity_id"], "otar selected its synonym as primary rival")
    check(
        "R01_NOMINAL_SUBSTANCE_PREPARATION" in dictionary["otar"]["supported_role_rivals"].split("|"),
        "otar nominal supported-role rival is hidden",
    )

    reader_by_key = {(row["line_rank"], row["locus"], row["ordinal"]): row for row in reader_rows}
    check(len(reader_by_key) == 109, "reader output keys are not unique")
    for source in reader_specs:
        key = (source["line_rank"], source["locus"], source["ordinal"])
        check(key in reader_by_key, f"reader output missing {key}")
        actual = reader_by_key[key]
        for column in SOURCE_SCHEMAS["LINE_READER_DEFAULT_SPECS.tsv"]:
            check(actual[column] == source[column], f"reader rebound mismatch {key}.{column}")
        if source["target_flag"] == "1":
            decision = dictionary[source["surface"]]
            check(actual["dictionary_selected_role"] == decision["selected_role_model"], f"reader role mismatch {key}")
            check(actual["dictionary_working_default_de"] == decision["working_default_de"], f"reader dictionary default mismatch {key}")
        else:
            check(actual["dictionary_selected_role"] == "NOT_TARGET", f"non-target dictionary role {key}")
    check(sum(int(row["reader_exact"]) for row in reader_rows) == 106, "rendered reader exact count != 106")
    check(len({row["locus"] for row in reader_rows}) == 12, "rendered reader line count != 12")

    # Explicit zero claims and sealed-page absence across all output locations.
    zero_cells = 0
    for name, (header, rows) in tables.items():
        zero_columns = set(header) & ZERO_FIELDS
        for number, row in enumerate(rows, 2):
            for column in zero_columns:
                check(is_zero(row[column]), f"nonzero output claim {name}:{number}.{column}")
                zero_cells += 1
            for column in header:
                if "page" in column or "locus" in column or "folio" in column:
                    check(not SEALED.search(row[column]), f"f84/f84r leaked into {name}:{number}.{column}")
    check(zero_cells > 1000, "too few explicit zero-credit cells checked")

    result = json.loads((artifact_dir / "RESULT.json").read_text(encoding="utf-8"))
    check(result["experiment_id"] == "GDT769", "result ID changed")
    check(result["status"] == run.STATUS, "result status differs from run.py")
    expected_counts = {
        "raw_target_occurrences": 640,
        "reader_exact_target_occurrences": 526,
        "target_forms": 5,
        "support_loci": 52,
        "frame_specs": 16,
        "frame_evaluations": 80,
        "role_specs": 5,
        "role_evaluations": 25,
        "identity_specs": len(identities),
        "identity_evaluations": len(identities),
        "reader_lines": 12,
        "reader_tokens": 109,
        "reader_exact_tokens": 106,
        "historical_source_rows": 17,
        "historical_relator_rows": 17,
    }
    check(result["counts"] == expected_counts, "result counts changed")
    scope = result["scope"]
    check(scope["new_pages_opened"] == 0, "result reports new pages")
    check(scope["new_images_opened"] == 0, "result reports new images")
    check(scope["new_transcriptions_opened"] == 0, "result reports new transcriptions")
    check(scope["f84_accessed"] is False and scope["f84r_accessed"] is False, "result reports f84/f84r access")
    for surface, expected in EXPECTED_DICTIONARY.items():
        selected = result["selected_working_defaults"][surface]
        check(
            (selected["role"], selected["identity"], selected["reader"], selected["confidence"], selected["rival"])
            == expected,
            f"result dictionary changed: {surface}",
        )
        check(selected["role_identity_consistent"] is True, f"result role inconsistency: {surface}")
    check(recursive_zero(result, check) >= 7, "result lacks zero-claim guards")

    human = (artifact_dir / "HISTORICAL_ROLE_IDENTITY_READER.md").read_text(encoding="utf-8")
    check(not any(term in human.casefold() for term in BANNED_GENERIC), "generic filler in human reader")
    check("Bestätigte Lexeme: **0**" in human, "human reader lacks zero-lexeme ceiling")
    check("zwei Drachmen" in human and "Zwischenzubereitung" in human, "human reader lacks corrected local defaults")

    hashes: dict[str, str] = {}
    with tempfile.TemporaryDirectory(prefix="gdt769_validation_replay_") as temp:
        replay_dir = Path(temp)
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        replay = subprocess.run(
            [sys.executable, str(RUN_PATH), "--output-dir", str(replay_dir), "--quiet"],
            cwd=ROOT,
            env=environment,
            text=True,
            capture_output=True,
            check=False,
        )
        check(replay.returncode == 0, "builder replay failed: " + (replay.stderr or replay.stdout)[-2000:])
        check(not replay.stdout.strip(), "quiet replay emitted stdout")
        check({path.name for path in replay_dir.iterdir()} == set(declared), "replay output set changed")
        for name in declared:
            actual_hash = digest(artifact_dir / name)
            replay_hash = digest(replay_dir / name)
            check(actual_hash == replay_hash, f"byte replay mismatch: {name}")
            hashes[name] = replay_hash

    validation = {
        "schema": "GDT769_VALIDATION_V1",
        "status": "PASS",
        "checks": checks,
        "artifact_dir": display_path(artifact_dir),
        "byte_identical_replay": True,
        "declared_builder_outputs": len(declared),
        "counts": expected_counts,
        "target_raw_counts": dict(RAW_COUNTS),
        "target_exact_counts": dict(EXACT_COUNTS),
        "selected_working_defaults": result["selected_working_defaults"],
        "guards": {
            "r03_same_occurrence": True,
            "r05_f14_alone_selection_credit": 0,
            "r05_f15_f16_discriminating_pages_only": True,
            "historical_predictions_create_voynich_evidence": 0,
            "eva_latin_credit": 0,
            "substring_export_credit": 0,
            "confirmed_lexemes": 0,
            "confirmed_plaintext_clauses": 0,
            "f84_accessed": False,
            "f84r_accessed": False,
        },
        "replay_sha256": hashes,
    }

    if args.output is not None:
        output_path: Path | None = resolve_path(args.output)
    elif artifact_dir == DEFAULT_ARTIFACTS.resolve():
        output_path = DEFAULT_ARTIFACTS / "VALIDATION.json"
    else:
        output_path = None
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if not args.quiet:
        print(json.dumps(validation, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
