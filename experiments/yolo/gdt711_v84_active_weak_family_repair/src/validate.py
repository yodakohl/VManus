#!/usr/bin/env python3
"""Independent validator for GDT711 V84 artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt711_v84_active_weak_family_repair"
SRC = EXP / "src"
ART = EXP / "artifacts"
G710 = ROOT / "experiments/yolo/gdt710_v83_complete_dictionary_confidence_evidence/artifacts"

SOURCE_READINGS = G710 / "V83_332_LIVE_READING_CONFIDENCE.tsv"
SOURCE_OCCURRENCES = G710 / "V83_479_LIVE_OCCURRENCE_EVIDENCE.tsv"
SOURCE_COMPLETE = G710 / "V83_COMPLETE_WORD_CONFIDENCE.tsv"
SOURCE_MASTER = G710 / "V83_2115_MASTER_CARD_CONFIDENCE.tsv"
G683_BOUNDARY = ROOT / "experiments/yolo/gdt683_ol_semantic_debt_reconciliation/src/N_BOUNDARY_OVERRIDE_SPECS.tsv"
SPECS = SRC / "V84_30_REPAIR_SPECS.tsv"
STEMS = SRC / "V84_STEM_RULES.tsv"

FAMILIES = ART / "V84_13_STEM_FAMILY_EVIDENCE.tsv"
LINKS = ART / "V84_NORMALIZED_CARD_LINKS.tsv"
CENSUS = ART / "V84_181_WEAK_READING_REPAIR_CENSUS.tsv"
LEXICAL = ART / "V84_324_ACTIVE_LEXICAL_READINGS.tsv"
CONTEXT = ART / "V84_479_CONTEXT_REALIZATIONS.tsv"
OUT_COMPLETE = ART / "V84_COMPLETE_WORD_CONFIDENCE.tsv"
RESULT = ART / "RESULT.json"
REPORT = EXP / "REPORT.md"

GENERATED = [FAMILIES, LINKS, CENSUS, LEXICAL, CONTEXT, OUT_COMPLETE, RESULT, REPORT]
HISTORICAL = "H0_NONE"
RELATION_DELTA = "0_GDT696_TO_GDT709"
EXPECTED_STATUS = (
    "PASS_V84_181_WEAK_AUDITED__30_SOURCE_READINGS_49_POSITIONS_REPAIRED__"
    "332_TO_324_ACTIVE_LEXICAL_READINGS__1594_TO_1586_COMPLETE_READINGS__"
    "11_W0_149_W1_145_W2_19_W3__19_W3_PRESERVED__ALL_H0_NONE"
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_pipe(value: str) -> list[str]:
    return [part for part in value.split("|") if part and part not in {"NONE", "0"}]


def key(row: dict[str, str]) -> tuple[str, str, int, str]:
    return row["page"], row["locus"], int(row["token_ordinal"]), row["surface"]


def level(score: int) -> str:
    if score < 20:
        return "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY"
    if score < 40:
        return "W1_WEAK_WORKING"
    if score < 60:
        return "W2_PROVISIONAL_WORKING"
    if score < 80:
        return "W3_SOLID_WORKING_THEORY"
    return "W4_STRONG_WORKING_THEORY"


def main() -> int:
    checks: list[str] = []

    def check(condition: bool, label: str) -> None:
        if not condition:
            raise AssertionError(label)
        checks.append(label)

    for path in [
        SOURCE_READINGS, SOURCE_OCCURRENCES, SOURCE_COMPLETE, SOURCE_MASTER,
        G683_BOUNDARY, SPECS, STEMS, *GENERATED,
    ]:
        check(path.is_file(), f"EXISTS:{path.relative_to(ROOT)}")

    before = {path: digest(path) for path in GENERATED}
    replay = subprocess.run(
        [sys.executable, str(SRC / "run.py")], cwd=ROOT,
        text=True, capture_output=True, check=False,
    )
    check(replay.returncode == 0, f"DETERMINISTIC_REPLAY_EXIT:{replay.stderr}")
    after = {path: digest(path) for path in GENERATED}
    for path in GENERATED:
        check(before[path] == after[path], f"DETERMINISTIC_REPLAY_HASH:{path.name}")

    source_readings = read_tsv(SOURCE_READINGS)
    source_occurrences = read_tsv(SOURCE_OCCURRENCES)
    source_complete = read_tsv(SOURCE_COMPLETE)
    source_master = read_tsv(SOURCE_MASTER)
    g683_boundaries = read_tsv(G683_BOUNDARY)
    specs = read_tsv(SPECS)
    stems = read_tsv(STEMS)
    families = read_tsv(FAMILIES)
    links = read_tsv(LINKS)
    census = read_tsv(CENSUS)
    lexical = read_tsv(LEXICAL)
    context = read_tsv(CONTEXT)
    complete = read_tsv(OUT_COMPLETE)
    result: dict[str, Any] = json.loads(RESULT.read_text(encoding="utf-8"))

    expected_lengths = {
        "source_readings": (len(source_readings), 332),
        "source_occurrences": (len(source_occurrences), 479),
        "source_complete": (len(source_complete), 1594),
        "source_master": (len(source_master), 2115),
        "specs": (len(specs), 30),
        "stems": (len(stems), 13),
        "families": (len(families), 13),
        "census": (len(census), 181),
        "lexical": (len(lexical), 324),
        "context": (len(context), 479),
        "complete": (len(complete), 1586),
    }
    for label, (actual, expected) in expected_lengths.items():
        check(actual == expected, f"COUNT:{label}:{expected}")

    check(result["status"] == EXPECTED_STATUS, "RESULT_STATUS")
    check(result["f84_or_f84r_used"] == 0 and result["new_pages"] == 0, "NO_NEW_OR_SEALED_PAGES")
    check(result["normalized_card_links_with_automatic_credit"] == 0, "CARD_LINKS_ZERO_AUTOMATIC_CREDIT")

    for path, rows in [
        (SOURCE_READINGS, source_readings), (SOURCE_OCCURRENCES, source_occurrences),
        (SOURCE_COMPLETE, source_complete), (LEXICAL, lexical), (CONTEXT, context),
        (OUT_COMPLETE, complete),
    ]:
        for row_number, row in enumerate(rows, start=2):
            check(not row.get("page", "").startswith("f84"), f"NO_F84_PAGE:{path.name}:{row_number}")
            check(not row.get("locus", "").startswith("f84"), f"NO_F84_LOCUS:{path.name}:{row_number}")

    readings_by_id = {row["reading_id"]: row for row in source_readings}
    check(len(readings_by_id) == 332, "SOURCE_READING_IDS_UNIQUE")
    specs_by_id = {row["source_reading_id"]: row for row in specs}
    check(len(specs_by_id) == 30, "SPEC_IDS_UNIQUE")
    for reading_id, spec in specs_by_id.items():
        check(reading_id in readings_by_id, f"SPEC_SOURCE_EXISTS:{reading_id}")
        check(
            readings_by_id[reading_id]["working_meaning_de"] == spec["old_working_meaning_de"],
            f"SPEC_OLD_MEANING_EXACT:{reading_id}",
        )

    lexical_by_v84 = {row["v84_reading_id"]: row for row in lexical}
    check(len(lexical_by_v84) == 324, "V84_READING_IDS_UNIQUE")
    lexical_by_source: dict[str, dict[str, str]] = {}
    for row in lexical:
        check(row["historical_confirmation"] == HISTORICAL, f"LEXICAL_H0:{row['v84_reading_id']}")
        check(row["relation_word_delta"] == RELATION_DELTA, f"LEXICAL_RELATION_ZERO:{row['v84_reading_id']}")
        check(row["form_level"] == "F3_EXACT_ACTIVE_ZL3B_TOKEN", f"LEXICAL_FORM_FIXED:{row['v84_reading_id']}")
        check(level(int(row["working_model_score_0_100_not_probability"])) == row["working_model_level"], f"LEXICAL_LEVEL_SCORE:{row['v84_reading_id']}")
        check(level(int(row["context_realization_score_0_100_not_probability"])) == row["context_realization_level"], f"CONTEXT_LEVEL_SCORE:{row['v84_reading_id']}")
        for source_id in split_pipe(row["source_reading_ids"]):
            check(source_id not in lexical_by_source, f"SOURCE_MAP_UNIQUE:{source_id}")
            lexical_by_source[source_id] = row
    check(set(lexical_by_source) == set(readings_by_id), "ALL_332_SOURCE_READINGS_MAP_ONCE")

    source_occ_fields = list(source_occurrences[0])
    source_occ_by_key = {key(row): row for row in source_occurrences}
    context_by_key = {key(row): row for row in context}
    check(len(source_occ_by_key) == len(context_by_key) == 479, "OCCURRENCE_KEYS_UNIQUE_AND_FIXED")
    check(set(source_occ_by_key) == set(context_by_key), "OCCURRENCE_KEY_PARITY")
    for occurrence_key, source in source_occ_by_key.items():
        target = context_by_key[occurrence_key]
        for field in source_occ_fields:
            check(source[field] == target[field], f"SOURCE_OCC_FIELD_BYTE_PARITY:{occurrence_key}:{field}")
        lexical_row = lexical_by_source[source["reading_id"]]
        check(target["v84_reading_id"] == lexical_row["v84_reading_id"], f"OCC_LEXICAL_LINK:{occurrence_key}")
        check(target["v84_lexical_core_de"] == lexical_row["v84_lexical_core_de"], f"OCC_LEXICAL_CORE:{occurrence_key}")
        check(target["v84_semantic_scope"] == lexical_row["semantic_scope"], f"OCC_SCOPE:{occurrence_key}")
        check(target["v84_semantic_applicability"] == lexical_row["semantic_applicability"], f"OCC_APPLICABILITY:{occurrence_key}")
        check(target["v84_global_export_scope"] == lexical_row["global_export_scope"], f"OCC_EXPORT_SCOPE:{occurrence_key}")
        check(target["v84_lexical_bound_span_ids"] == lexical_row["bound_span_ids"], f"OCC_LEXICAL_BOUND_SPANS:{occurrence_key}")
        if source["reading_id"] == "ol#2":
            expected_span_id, expected_span_role, expected_span_export = "G683_CHEOP_OL", "RIGHT", "0"
        else:
            expected_span_id = source["bound_span_id"]
            expected_span_role = source["bound_span_role"]
            expected_span_export = source["bound_span_global_export_allowed"]
        check(target["v84_occurrence_bound_span_id"] == expected_span_id, f"OCC_EXACT_BOUND_SPAN_ID:{occurrence_key}")
        check(target["v84_occurrence_bound_span_role"] == expected_span_role, f"OCC_EXACT_BOUND_SPAN_ROLE:{occurrence_key}")
        check(target["v84_occurrence_bound_span_global_export_allowed"] == expected_span_export, f"OCC_EXACT_BOUND_SPAN_EXPORT:{occurrence_key}")
        check(target["v84_historical_confirmation"] == HISTORICAL, f"OCC_H0:{occurrence_key}")
    check(Counter(row["v84_occurrence_bound_span_id"] for row in context) == Counter({
        "NONE": 472, "B001": 2, "B002": 2, "B003": 2, "G683_CHEOP_OL": 1,
    }), "POSITION_EXACT_BOUND_SPAN_DISTRIBUTION")
    check(sum(row["v84_occurrence_bound_span_global_export_allowed"] == "0" for row in context) == 7, "SEVEN_POSITION_BOUND_EXPORT_STOPS")

    occ_by_reading: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in source_occurrences:
        occ_by_reading[row["reading_id"]].append(row)
    for source_id, lexical_row in lexical_by_source.items():
        source = readings_by_id[source_id]
        check(len(occ_by_reading[source_id]) == int(source["occurrence_count"]), f"SOURCE_OCC_COUNT:{source_id}")
        source_ids = split_pipe(lexical_row["source_reading_ids"])
        group_occ = [occ for rid in source_ids for occ in occ_by_reading[rid]]
        check(len(group_occ) == int(lexical_row["occurrence_count"]), f"LEXICAL_OCC_COUNT:{lexical_row['v84_reading_id']}")
        check(len({occ["page"] for occ in group_occ}) == int(lexical_row["page_count"]), f"LEXICAL_PAGE_COUNT:{lexical_row['v84_reading_id']}")
        check(len({occ["locus"] for occ in group_occ}) == int(lexical_row["locus_count"]), f"LEXICAL_LOCUS_COUNT:{lexical_row['v84_reading_id']}")

    selected_occ = [row for row in source_occurrences if row["reading_id"] in specs_by_id]
    check(len(selected_occ) == 49, "SELECTED_49_POSITIONS")
    check(len({row["page"] for row in selected_occ}) == 25, "SELECTED_25_PAGES")
    repaired_lexical_ids = {lexical_by_source[source_id]["v84_reading_id"] for source_id in specs_by_id}
    check(len(repaired_lexical_ids) == 22, "THIRTY_SOURCE_TO_TWENTY_TWO_LEXICAL")
    repaired_level_changes = 0
    for v84_id in repaired_lexical_ids:
        row = lexical_by_v84[v84_id]
        old_levels = {readings_by_id[rid]["working_model_level"] for rid in split_pipe(row["source_reading_ids"])}
        check(len(old_levels) == 1, f"REPAIR_GROUP_OLD_LEVEL_UNIFORM:{v84_id}")
        if row["working_model_level"] not in old_levels:
            repaired_level_changes += 1
    check(repaired_level_changes == 18, "EIGHTEEN_LEXICAL_LEVEL_CHANGES")

    for source_id, source in readings_by_id.items():
        if source_id in specs_by_id:
            continue
        target = lexical_by_source[source_id]
        check(target["source_reading_count"] == "1", f"UNREPAIRED_NOT_MERGED:{source_id}")
        check(target["v84_reading_id"] == source_id, f"UNREPAIRED_ID_PRESERVED:{source_id}")
        check(target["v84_lexical_core_de"] == source["working_meaning_de"], f"UNREPAIRED_MEANING_PRESERVED:{source_id}")
        check(target["v84_context_realizations_de"] == source["working_meaning_de"], f"UNREPAIRED_CONTEXT_PRESERVED:{source_id}")
        check(target["working_model_score_0_100_not_probability"] == source["working_model_score_0_100_not_probability"], f"UNREPAIRED_SCORE_PRESERVED:{source_id}")
        check(target["working_model_level"] == source["working_model_level"], f"UNREPAIRED_LEVEL_PRESERVED:{source_id}")
        check(target["semantic_scope"] == source["semantic_scope"], f"UNREPAIRED_SCOPE_PRESERVED:{source_id}")
        check(target["semantic_applicability"] == source["semantic_applicability"], f"UNREPAIRED_APPLICABILITY_PRESERVED:{source_id}")
        check(target["global_export_scope"] == source["global_export_scope"], f"UNREPAIRED_EXPORT_PRESERVED:{source_id}")
        check(target["bound_span_ids"] == source["bound_span_ids"], f"UNREPAIRED_BOUND_SPANS_PRESERVED:{source_id}")
        check(target["last_semantic_writer"] == source["last_semantic_writer"], f"UNREPAIRED_WRITER_PRESERVED:{source_id}")
        check(target["source_gdts"] == source["source_gdts"], f"UNREPAIRED_SOURCE_GDTS_PRESERVED:{source_id}")
        check(target["positive_evidence_de"] == source["positive_evidence_de"], f"UNREPAIRED_POSITIVE_EVIDENCE_PRESERVED:{source_id}")
        check(target["counterevidence_de"] == source["counterevidence_de"], f"UNREPAIRED_COUNTEREVIDENCE_PRESERVED:{source_id}")

    repaired_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for spec in specs:
        target = lexical_by_source[spec["source_reading_id"]]
        repaired_groups[target["v84_reading_id"]].append(spec)
        check(target["v84_lexical_core_de"] == spec["v84_lexical_core_de"], f"SPEC_TO_CORE:{spec['source_reading_id']}")
        matching_occurrences = [row for row in context if row["source_reading_id"] == spec["source_reading_id"]]
        check(bool(matching_occurrences), f"SPEC_HAS_CONTEXT_OCCURRENCE:{spec['source_reading_id']}")
        for occurrence in matching_occurrences:
            check(occurrence["v84_context_realization_de"] == spec["v84_context_realization_de"], f"SPEC_TO_CONTEXT:{spec['source_reading_id']}:{occurrence['position_id']}")
            check(occurrence["v84_repair_mode"] == spec["repair_mode"], f"SPEC_TO_REPAIR_MODE:{spec['source_reading_id']}:{occurrence['position_id']}")
    for v84_id, group_specs in repaired_groups.items():
        target = lexical_by_v84[v84_id]
        source_rows = [readings_by_id[spec["source_reading_id"]] for spec in group_specs]
        expected_base = max(int(row["working_model_score_0_100_not_probability"]) for row in source_rows)
        expected_delta = max(int(spec["score_delta_lexical_core"]) for spec in group_specs)
        expected_cap = min(int(spec["lexical_core_cap"]) for spec in group_specs)
        expected_score = min(expected_base + expected_delta, expected_cap)
        expected_context_cap = min(int(spec["context_realization_cap"]) for spec in group_specs)
        check(target["base_score"] == str(expected_base), f"REPAIR_SCORE_BASE:{v84_id}")
        check(target["score_delta_lexical_core"] == str(expected_delta), f"REPAIR_SCORE_DELTA:{v84_id}")
        check(target["lexical_core_cap"] == str(expected_cap), f"REPAIR_SCORE_CAP:{v84_id}")
        check(target["working_model_score_0_100_not_probability"] == str(expected_score), f"REPAIR_SCORE_FINAL:{v84_id}")
        check(target["context_realization_cap"] == str(expected_context_cap), f"REPAIR_CONTEXT_CAP:{v84_id}")
        check(target["context_realization_score_0_100_not_probability"] == str(min(expected_score, expected_context_cap)), f"REPAIR_CONTEXT_SCORE:{v84_id}")

    expected_active_levels = Counter({
        "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY": 11,
        "W1_WEAK_WORKING": 149,
        "W2_PROVISIONAL_WORKING": 145,
        "W3_SOLID_WORKING_THEORY": 19,
    })
    expected_complete_levels = Counter({
        "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY": 291,
        "W1_WEAK_WORKING": 329,
        "W2_PROVISIONAL_WORKING": 523,
        "W3_SOLID_WORKING_THEORY": 443,
    })
    check(Counter(row["working_model_level"] for row in lexical) == expected_active_levels, "ACTIVE_LEVEL_DISTRIBUTION")
    check(Counter(row["semantic_applicability"] for row in lexical) == Counter({
        "SEMANTIC_WORKING_READING": 318,
        "STRUCTURAL_OR_PUNCTUATION_READING": 5,
        "COMPOUND_ONLY_LOCAL_READING": 1,
    }), "ACTIVE_APPLICABILITY_DISTRIBUTION")
    check(Counter(row["semantic_scope"] for row in lexical) == Counter({
        "ACTIVE_EXACT_WHOLE_READING": 314,
        "NAMED_CONTEXT_DISPATCH": 9,
        "BOUND_SPAN_LOCAL_READING": 1,
    }), "ACTIVE_SCOPE_DISTRIBUTION")
    check(Counter(row["global_export_scope"] for row in lexical) == Counter({
        "ACTIVE_WORKING_DEFAULT": 310,
        "NAMED_CONTEXT_ONLY": 8,
        "BOUND_SPAN_ONLY_NO_GLOBAL_EXPORT": 5,
        "NAMED_CONTEXT_ONLY|BOUND_SPAN_ONLY_NO_GLOBAL_EXPORT": 1,
    }), "ACTIVE_EXPORT_SCOPE_DISTRIBUTION")
    check(Counter(row["working_model_level"] for row in complete) == expected_complete_levels, "COMPLETE_LEVEL_DISTRIBUTION")
    check(len({row["surface"] for row in complete}) == 1582, "COMPLETE_1582_SURFACES")
    check(all(row["historical_confirmation"] == HISTORICAL for row in complete), "COMPLETE_ALL_H0")
    check(all(row["relation_word_delta"] == RELATION_DELTA for row in complete), "COMPLETE_ALL_RELATION_ZERO")

    source_global = {
        (row["surface"], row["reading_id"]): row
        for row in source_complete if row["current_layer"] == "GLOBAL_V48_DEFAULT"
    }
    target_global = {
        (row["surface"], row["reading_id"]): row
        for row in complete if row["current_layer"] == "GLOBAL_V48_DEFAULT"
    }
    check(set(source_global) == set(target_global), "ALL_1262_GLOBAL_ROW_KEYS_IDENTICAL")
    source_complete_fields = list(source_complete[0])
    for global_key, source in source_global.items():
        target = target_global[global_key]
        for field in source_complete_fields:
            check(source[field] == target[field], f"GLOBAL_SOURCE_FIELD_BYTE_IDENTICAL:{global_key}:{field}")
        exact_global = (
            source["semantic_scope"] == "KNOWN_EXACT_WHOLE"
            and source["form_level"] == "F3_EXACT_ZL3B_WHOLE"
        )
        expected_export_scope = (
            "GLOBAL_V48_EXACT_WHOLE_DEFAULT"
            if exact_global
            else f"GLOBAL_V48_{source['semantic_scope']}_NO_UNCONDITIONAL_EXPORT"
        )
        check(target["global_export_scope"] == expected_export_scope, f"GLOBAL_EXPORT_SCOPE:{global_key}")
        check(target["unconditional_global_export_allowed"] == str(int(exact_global)), f"GLOBAL_EXPORT_ALLOWED:{global_key}")
    check(sum(row["unconditional_global_export_allowed"] == "1" for row in target_global.values()) == 1178, "GLOBAL_1178_EXACT_EXPORTABLE")
    check(sum(row["unconditional_global_export_allowed"] == "0" for row in target_global.values()) == 84, "GLOBAL_84_SCOPED_OR_UNSTABLE_NOT_EXPORTABLE")
    target_active = [row for row in complete if row["current_layer"] == "ACTIVE_V84_LEXICAL_CORE"]
    check(len(target_active) == 324, "COMPLETE_HAS_324_V84_ACTIVE_ROWS")
    for row in target_active:
        lexical_row = lexical_by_v84[row["reading_id"]]
        check(row["surface"] == lexical_row["surface"], f"COMPLETE_ACTIVE_SURFACE:{row['reading_id']}")
        check(row["working_meaning_de"] == lexical_row["v84_lexical_core_de"], f"COMPLETE_ACTIVE_CORE:{row['reading_id']}")
        check(row["working_model_score_0_100_not_probability"] == lexical_row["working_model_score_0_100_not_probability"], f"COMPLETE_ACTIVE_SCORE:{row['reading_id']}")
        check(row["semantic_scope"] == lexical_row["semantic_scope"], f"COMPLETE_ACTIVE_SCOPE:{row['reading_id']}")
        check(row["semantic_applicability"] == lexical_row["semantic_applicability"], f"COMPLETE_ACTIVE_APPLICABILITY:{row['reading_id']}")
        check(row["global_export_scope"] == lexical_row["global_export_scope"], f"COMPLETE_ACTIVE_EXPORT_SCOPE:{row['reading_id']}")
        check(row["bound_span_ids"] == lexical_row["bound_span_ids"], f"COMPLETE_ACTIVE_BOUND_SPANS:{row['reading_id']}")
        check(row["source_gdts"] == lexical_row["source_gdts"], f"COMPLETE_ACTIVE_SOURCE_GDTS:{row['reading_id']}")

    source_w3 = [row for row in source_readings if row["working_model_level"] == "W3_SOLID_WORKING_THEORY"]
    check(len(source_w3) == 19, "SOURCE_19_W3")
    check(sum(int(row["occurrence_count"]) for row in source_w3) == 77, "SOURCE_W3_77_POSITIONS")
    for source in source_w3:
        target = lexical_by_source[source["reading_id"]]
        check(target["source_reading_count"] == "1", f"W3_NOT_MERGED:{source['reading_id']}")
        check(target["v84_lexical_core_de"] == source["working_meaning_de"], f"W3_MEANING_PRESERVED:{source['reading_id']}")
        check(target["working_model_score_0_100_not_probability"] == source["working_model_score_0_100_not_probability"], f"W3_SCORE_PRESERVED:{source['reading_id']}")
        check(target["working_model_level"] == source["working_model_level"], f"W3_LEVEL_PRESERVED:{source['reading_id']}")
        check(target["last_semantic_writer"] == source["last_semantic_writer"], f"W3_WRITER_PRESERVED:{source['reading_id']}")
        check(target["occurrence_count"] == source["occurrence_count"], f"W3_OCCURRENCES_PRESERVED:{source['reading_id']}")
        check(target["semantic_scope"] == source["semantic_scope"], f"W3_SCOPE_PRESERVED:{source['reading_id']}")
        check(target["semantic_applicability"] == source["semantic_applicability"], f"W3_APPLICABILITY_PRESERVED:{source['reading_id']}")
        check(target["global_export_scope"] == source["global_export_scope"], f"W3_EXPORT_SCOPE_PRESERVED:{source['reading_id']}")
        check(target["bound_span_ids"] == source["bound_span_ids"], f"W3_BOUND_SPANS_PRESERVED:{source['reading_id']}")
        check(target["source_gdts"] == source["source_gdts"], f"W3_SOURCE_GDTS_PRESERVED:{source['reading_id']}")

    daiin = lexical_by_v84["daiin#V84_CORE"]
    dain = lexical_by_v84["dain#V84_CORE"]
    check(daiin["v84_lexical_core_de"] == "Wert III", "DAIIN_CORE_VALUE_III")
    check(set(split_pipe(daiin["v84_context_realizations_de"])) == {"Grad III", "drei"}, "DAIIN_TWO_CONTEXT_REALIZATIONS")
    check(daiin["source_reading_count"] == "7" and daiin["occurrence_count"] == "7", "DAIIN_SEVEN_TO_ONE")
    check(daiin["working_model_level"] == "W2_PROVISIONAL_WORKING" and daiin["context_realization_level"] == "W1_WEAK_WORKING", "DAIIN_CORE_CONTEXT_CONFIDENCE_SPLIT")
    check(dain["v84_lexical_core_de"] == "Wert II", "DAIN_CORE_VALUE_II")
    check(set(split_pipe(dain["v84_context_realizations_de"])) == {"Grad II", "zwei"}, "DAIN_TWO_CONTEXT_REALIZATIONS")
    check(dain["source_reading_count"] == "3" and dain["occurrence_count"] == "3", "DAIN_THREE_TO_ONE")

    expected_critical = {
        "ol#V84_1": ("Ansatz", "W1_WEAK_WORKING", "39"),
        "ol#V84_2": ("Stoffkopf", "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY", "19"),
        "olkar#V84_1": ("heißer Holzanteil I", "W2_PROVISIONAL_WORKING", "53"),
        "shx#V84_1": ("eingeweicht", "W1_WEAK_WORKING", "29"),
        "am#V84_1": ("Maß I", "W1_WEAK_WORKING", "22"),
        "dam#V84_1": ("abgemessenes Maß I", "W1_WEAK_WORKING", "25"),
        "ckhol#V84_1": ("Mischgut", "W2_PROVISIONAL_WORKING", "43"),
        "qoteed#V84_1": ("vollständig abkühlen und abziehen", "W2_PROVISIONAL_WORKING", "44"),
        "qodaiin#V84_1": ("Wert III", "W1_WEAK_WORKING", "36"),
        "orom#V84_1": ("Portion", "W2_PROVISIONAL_WORKING", "42"),
    }
    for reading_id, (meaning, expected_level, score) in expected_critical.items():
        row = lexical_by_v84[reading_id]
        check(row["v84_lexical_core_de"] == meaning, f"CRITICAL_MEANING:{reading_id}")
        check(row["working_model_level"] == expected_level, f"CRITICAL_LEVEL:{reading_id}")
        check(row["working_model_score_0_100_not_probability"] == score, f"CRITICAL_SCORE:{reading_id}")

    banned_specificities = ["Gummi", "Gran", "Handvoll", "Dosis", "Mazerat", "Absud", "Auszug", "Arzneikompositum"]
    repaired_cores = "\n".join(lexical_by_v84[v84_id]["v84_lexical_core_de"] for v84_id in repaired_lexical_ids)
    for term in banned_specificities:
        check(term.lower() not in repaired_cores.lower(), f"UNSUPPORTED_SPECIFICITY_REMOVED:{term}")
    check("Pulver" not in lexical_by_v84["ol#V84_2"]["v84_lexical_core_de"], "BOUND_OL_DOES_NOT_EXPORT_POWDER")
    bound_ol = lexical_by_v84["ol#V84_2"]
    check(bound_ol["semantic_scope"] == "BOUND_SPAN_LOCAL_READING", "BOUND_OL_SCOPE")
    check(bound_ol["semantic_applicability"] == "COMPOUND_ONLY_LOCAL_READING", "BOUND_OL_APPLICABILITY")
    check(bound_ol["global_export_scope"] == "BOUND_SPAN_ONLY_NO_GLOBAL_EXPORT", "BOUND_OL_EXPORT_SCOPE")
    check(bound_ol["bound_span_ids"] == "G683_CHEOP_OL", "BOUND_OL_EXPLICIT_GDT683_SPAN")
    check(bound_ol["unconditional_global_export_allowed"] == "0", "BOUND_OL_NOT_GLOBALLY_EXPORTABLE")
    g683_cheop_ol = [
        row for row in g683_boundaries
        if row["locus"] == "f115r.1" and row["render_span_tokens"] == "cheop|ol"
    ]
    check(len(g683_cheop_ol) == 1, "GDT683_CHEOP_OL_EXACT_SOURCE")
    check(g683_cheop_ol[0]["export_policy"] == "LOCAL_COMPOUND_ONLY", "GDT683_CHEOP_OL_LOCAL_ONLY")
    check(g683_cheop_ol[0]["reader_scope"] == "BILATERAL_LEFT_BOUND", "GDT683_CHEOP_OL_READER_BOUND")
    qodaiin = lexical_by_v84["qodaiin#V84_1"]
    check(qodaiin["family_ids"] == "F_N", "QODAIIN_NO_FREE_QO_SEMANTIC_CREDIT")
    check(qodaiin["decomposition"] == "QOD+[VALUE_III] / QO+D+AIIN OPEN", "QODAIIN_INTERNAL_BOUNDARY_OPEN")
    check(qodaiin["global_export_scope"] == "BOUND_SPAN_ONLY_NO_GLOBAL_EXPORT", "QODAIIN_BOUND_ONLY")
    orom = lexical_by_v84["orom#V84_1"]
    check(orom["family_ids"] == "F_OR", "OROM_NOT_FALSELY_LINKED_TO_OL")
    check(orom["decomposition"] == "OR+[OM_OPEN]", "OROM_OM_HEAD_EXPLICITLY_OPEN")

    family_licensed_tokens = {
        "F_STATE": {"CH", "SH", "K", "T"},
        "F_STAGE": {"Y", "EY", "EEY", "DY", "EDY", "EEDY"},
        "F_O": {"O"},
        "F_AL": {"AL", "DAL"},
        "F_AM": {"AM", "DAM"},
        "F_R": {"AR", "AIR", "AIIR", "AIIIR"},
        "F_OR": {"OR"},
        "F_N": {"AIN", "AIIN", "AIIIN", "DAIN", "DAIIN", "VALUE_II", "VALUE_III", "VALUE_IV"},
        "F_CKH": {"CKH", "CPH"},
        "F_MATERIA": {"P", "S", "R", "L", "F", "CTH"},
        "F_OL": {"OL", "OL_BOUND"},
        "F_D": {"D"},
        "F_REF": {"QO", "Y"},
    }
    for spec in specs:
        tokens = set(re.findall(r"[A-Z]+(?:_[A-Z0-9]+)?", spec["decomposition"].upper()))
        for family_id in split_pipe(spec["family_ids"]):
            check(
                bool(tokens & family_licensed_tokens[family_id]),
                f"FAMILY_TAG_LICENSED_BY_DECLARED_COMPONENT:{spec['source_reading_id']}:{family_id}",
            )

    weak_source = [row for row in source_readings if int(row["working_model_score_0_100_not_probability"]) < 40]
    check(len(weak_source) == 181, "WEAK_SOURCE_181")
    check(sum(int(row["occurrence_count"]) for row in weak_source) == 211, "WEAK_SOURCE_211_POSITIONS")
    check({row["source_entity_id"] for row in census} == {row["entity_id"] for row in weak_source}, "CENSUS_EXACT_WEAK_UNIVERSE")
    check(Counter(row["issue_cluster"] for row in census) == Counter({
        "CURRENT_DEBT_ONLY": 75,
        "CURRENT_DEBT_PLUS_LOW": 13,
        "LIVE_RIVAL": 88,
        "NO_LISTED_DEBT_LOW_OR_RIVAL": 5,
    }), "CENSUS_ISSUE_PARTITION")
    check(Counter(row["disposition"] for row in census) == Counter({"HELD_FOR_LATER_REPAIR": 151, "REPAIRED_IN_V84": 30}), "CENSUS_DISPOSITION")
    check(all(row["master_card_automatic_score_credit"] == "0" for row in census), "CENSUS_CARD_CREDIT_ZERO")

    master_by_id = {row["entity_id"]: row for row in source_master}
    check(len(links) > 0, "NORMALIZED_LINKS_NONEMPTY")
    check(result["normalized_card_links"] == len(links), "RESULT_CARD_LINK_COUNT_BOUND")
    for row in links:
        check(row["source_reading_id"] in readings_by_id, f"LINK_READING_EXISTS:{row['source_reading_id']}")
        check(row["master_card_id"] in master_by_id, f"LINK_CARD_EXISTS:{row['master_card_id']}")
        card = master_by_id[row["master_card_id"]]
        check(card["entry"].split("@", 1)[0].strip() == row["surface"], f"LINK_EXACT_NORMALIZED_SURFACE:{row['source_reading_id']}:{row['master_card_id']}")
        check(row["used_as_automatic_score_credit"] == "0" and row["score_credit"] == "0", f"LINK_ZERO_CREDIT:{row['source_reading_id']}:{row['master_card_id']}")

    stem_by_id = {row["family_id"]: row for row in stems}
    family_by_id = {row["family_id"]: row for row in families}
    check(len(stem_by_id) == len(family_by_id) == 13, "THIRTEEN_UNIQUE_FAMILIES")
    check(set(stem_by_id) == set(family_by_id), "FAMILY_ID_PARITY")
    for family_id, source in stem_by_id.items():
        target = family_by_id[family_id]
        for field in source:
            check(source[field] == target[field], f"FAMILY_SOURCE_FIELD_PARITY:{family_id}:{field}")
        for artifact in split_pipe(source["support_artifacts"]):
            check((ROOT / artifact).is_file(), f"FAMILY_SUPPORT_EXISTS:{family_id}:{artifact}")
        check(target["automatic_historical_credit"] == "0", f"FAMILY_HISTORICAL_CREDIT_ZERO:{family_id}")
        check(target["historical_confirmation"] == HISTORICAL, f"FAMILY_H0:{family_id}")

    validation = {
        "experiment_id": "GDT711",
        "status": "PASS",
        "checks_passed": len(checks),
        "runner_replay_exit": replay.returncode,
        "deterministic_artifact_hashes": {
            path.relative_to(ROOT).as_posix(): after[path] for path in GENERATED
        },
        "validated_counts": {
            "source_active_readings": 332,
            "source_positions": 479,
            "weak_readings": 181,
            "weak_positions": 211,
            "repair_specs": 30,
            "repaired_positions": 49,
            "repaired_pages": 25,
            "active_lexical_readings": 324,
            "complete_readings": 1586,
            "complete_surfaces": 1582,
            "preserved_w3_readings": 19,
            "preserved_w3_positions": 77,
        },
        "sealed_data": {"f84": "FORBIDDEN_AND_UNUSED", "f84r": "FORBIDDEN_AND_UNUSED"},
        "historical_confirmation": "ALL_H0_NONE",
    }
    (ART / "VALIDATION.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
