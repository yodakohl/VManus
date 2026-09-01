#!/usr/bin/env python3
"""Independent validator for the GDT713 V86 dictionary repair."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt713_v86_measure_ckh_core_context_repair"
SRC = EXP / "src"
ART = EXP / "artifacts"
G712 = ROOT / "experiments/yolo/gdt712_v85_al_state_core_context_repair/artifacts"
G711 = ROOT / "experiments/yolo/gdt711_v84_active_weak_family_repair/artifacts"

SOURCE_LEXICAL = G712 / "V85_324_ACTIVE_LEXICAL_READINGS.tsv"
SOURCE_CONTEXT = G712 / "V85_479_CONTEXT_REALIZATIONS.tsv"
SOURCE_COMPLETE = G712 / "V85_COMPLETE_WORD_CONFIDENCE.tsv"
SOURCE_CENSUS = G712 / "V85_151_HELD_READING_AUDIT.tsv"
SOURCE_SPANS = G712 / "V85_1_BOUND_SPAN_RENDERER.tsv"
SOURCE_FAMILIES = G711 / "V84_13_STEM_FAMILY_EVIDENCE.tsv"
SPECS = SRC / "V86_9_AUDIT_SPECS.tsv"

LEXICAL = ART / "V86_324_ACTIVE_LEXICAL_READINGS.tsv"
CONTEXT = ART / "V86_479_CONTEXT_REALIZATIONS.tsv"
CENSUS = ART / "V86_118_HELD_READING_AUDIT.tsv"
DELTA = ART / "V86_9_MEASURE_CKH_CORE_CONTEXT_DELTA.tsv"
FAMILIES = ART / "V86_8_FAMILY_EVIDENCE.tsv"
SPANS = ART / "V86_1_BOUND_SPAN_RENDERER.tsv"
COMPLETE = ART / "V86_COMPLETE_WORD_CONFIDENCE.tsv"
RESULT = ART / "RESULT.json"
REPORT = EXP / "REPORT.md"
VALIDATION = ART / "VALIDATION.json"

GENERATED = [LEXICAL, CONTEXT, CENSUS, DELTA, FAMILIES, SPANS, COMPLETE, RESULT, REPORT]
HISTORICAL = "H0_NONE"
EXPECTED_STATUS = (
    "PASS_V86_9_MEASURE_CKH_READINGS_AUDITED__8_REVISED_1_HELD__"
    "10_POSITIONS_7_PAGES__7_W0_143_W1_155_W2_19_W3__"
    "109_WEAK_READINGS_REMAIN__ALL_H0_NONE"
)
EXPECTED_TARGETS = {
    "checkhy#1", "cheockhy#1", "ckhy#1", "cphochy#1", "cphy#1",
    "dol#1", "oram#1", "otam#1", "sheckhy#1",
}
EXPECTED_HOLDS = {"dol#1"}
EXPECTED_TARGET_OCCURRENCES = {
    ("f104v", "f104v.2", 10, "oram"),
    ("f107r", "f107r.2", 8, "cheockhy"),
    ("f112r", "f112r.36", 3, "checkhy"),
    ("f114r", "f114r.24", 6, "cphochy"),
    ("f114r", "f114r.24", 12, "cphy"),
    ("f80r", "f80r.17", 2, "sheckhy"),
    ("f86v5", "f86v5.2", 11, "otam"),
    ("f86v5", "f86v5.2", 12, "otam"),
    ("f8r", "f8r.15", 8, "dol"),
    ("f8r", "f8r.15", 10, "ckhy"),
}
RESET_LEXICAL_AUDIT_FIELDS = {
    "v85_audit_decision", "v85_evidence_class", "v85_open_semantic_slots",
    "v85_component_global_export_allowed", "v85_prior_lexical_core_de",
}
RESET_CONTEXT_AUDIT_FIELDS = {
    "v85_audit_decision", "v85_evidence_class", "v85_open_semantic_slots",
    "v85_component_global_export_allowed",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_pipe(value: str) -> list[str]:
    return [part.strip() for part in value.split("|") if part.strip() and part.strip() not in {"NONE", "0"}]


def v86_key(value: str) -> str:
    return value.replace("v85", "v86").replace("V85", "V86")


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


def occurrence_key(row: dict[str, str]) -> tuple[str, str, int, str]:
    return row["page"], row["locus"], int(row["token_ordinal"]), row["surface"]


def lexical_source_map(rows: list[dict[str, str]], id_field: str = "source_reading_ids") -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for row in rows:
        for source_id in split_pipe(row[id_field]):
            if source_id in result:
                raise AssertionError(f"duplicate lexical source mapping: {source_id}")
            result[source_id] = row
    return result


def main() -> int:
    checks: list[str] = []

    def check(condition: bool, label: str) -> None:
        if not condition:
            raise AssertionError(label)
        checks.append(label)

    for path in [SOURCE_LEXICAL, SOURCE_CONTEXT, SOURCE_COMPLETE, SOURCE_CENSUS, SOURCE_SPANS, SOURCE_FAMILIES, SPECS, *GENERATED]:
        check(path.is_file(), f"EXISTS:{path.relative_to(ROOT)}")

    before = {path: digest(path) for path in GENERATED}
    replay = subprocess.run(
        [sys.executable, str(SRC / "run.py")], cwd=ROOT,
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    check(replay.returncode == 0, f"DETERMINISTIC_REPLAY_EXIT:{replay.stderr}")
    after = {path: digest(path) for path in GENERATED}
    for path in GENERATED:
        check(before[path] == after[path], f"DETERMINISTIC_REPLAY_HASH:{path.name}")

    source_lexical = read_tsv(SOURCE_LEXICAL)
    source_context = read_tsv(SOURCE_CONTEXT)
    source_complete = read_tsv(SOURCE_COMPLETE)
    source_census = read_tsv(SOURCE_CENSUS)
    source_spans = read_tsv(SOURCE_SPANS)
    source_families = read_tsv(SOURCE_FAMILIES)
    specs = read_tsv(SPECS)
    lexical = read_tsv(LEXICAL)
    context = read_tsv(CONTEXT)
    census = read_tsv(CENSUS)
    delta = read_tsv(DELTA)
    families = read_tsv(FAMILIES)
    spans = read_tsv(SPANS)
    complete = read_tsv(COMPLETE)
    result: dict[str, Any] = json.loads(RESULT.read_text(encoding="utf-8"))

    expected_counts = {
        "source_lexical": (len(source_lexical), 324), "source_context": (len(source_context), 479),
        "source_complete": (len(source_complete), 1586), "source_census": (len(source_census), 151),
        "source_spans": (len(source_spans), 1),
        "source_families": (len(source_families), 13), "specs": (len(specs), 9),
        "lexical": (len(lexical), 324), "context": (len(context), 479),
        "census": (len(census), 118), "delta": (len(delta), 9),
        "families": (len(families), 8), "spans": (len(spans), 1),
        "complete": (len(complete), 1586),
    }
    for label, (actual, expected) in expected_counts.items():
        check(actual == expected, f"COUNT:{label}:{expected}")

    check(result["status"] == EXPECTED_STATUS, "RESULT_STATUS")
    check(result["f84_or_f84r_used"] == 0 and result["new_pages"] == 0, "RESULT_NO_NEW_OR_SEALED_PAGE")
    check(result["relation_word_credit_gdt713"] == 0, "RESULT_ZERO_RELATION_WORD_CREDIT")
    check(result["revised_readings"] == 8 and result["held_readings"] == 1, "RESULT_DECISION_COUNTS")
    check(result["revised_positions"] == 9 and result["held_positions"] == 1, "RESULT_POSITION_PARTITION")
    check(result["remaining_unreviewed_weak_readings"] == 109, "RESULT_109_REMAIN")

    specs_by_id = {row["source_reading_id"]: row for row in specs}
    check(set(specs_by_id) == EXPECTED_TARGETS, "EXACT_9_TARGET_IDS")
    check({row["source_reading_id"] for row in specs if row["decision"] == "HOLD"} == EXPECTED_HOLDS, "EXACT_1_HOLD_ID")
    check(Counter(row["decision"] for row in specs) == Counter({"REVISE": 8, "HOLD": 1}), "SPEC_DECISION_COUNTS")
    check(all(row["component_global_export_allowed"] == "0" for row in specs), "SPEC_ZERO_COMPONENT_EXPORT")

    source_by_id = lexical_source_map(source_lexical)
    target_by_id = lexical_source_map(lexical)
    check(len(source_by_id) == len(target_by_id) == 332, "LEXICAL_SOURCE_MAP_332")
    check(set(source_by_id) == set(target_by_id), "LEXICAL_SOURCE_MAP_PARITY")
    check(len({row["v86_reading_id"] for row in lexical}) == 324, "V86_READING_IDS_UNIQUE")

    source_fields = list(source_lexical[0])
    w3_rows = 0
    w3_positions = 0
    for source_id, source in source_by_id.items():
        target = target_by_id[source_id]
        if source_id not in EXPECTED_TARGETS:
            for field in source_fields:
                if field in RESET_LEXICAL_AUDIT_FIELDS:
                    continue
                check(target[v86_key(field)] == source[field], f"NON_TARGET_LEXICAL_PARITY:{source_id}:{field}")
            check(target["v86_audit_decision"] == "NOT_IN_GDT713_TRANCHE", f"NON_TARGET_DECISION:{source_id}")
        else:
            spec = specs_by_id[source_id]
            check(source["v85_lexical_core_de"] == spec["old_lexical_core_de"], f"SPEC_OLD_CORE:{source_id}")
            check(target["v86_lexical_core_de"] == spec["v86_lexical_core_de"], f"SPEC_NEW_CORE:{source_id}")
            check(target["v86_context_realizations_de"] == spec["v86_context_realization_de"], f"SPEC_CONTEXT:{source_id}")
            check(target["v86_audit_decision"] == spec["decision"], f"SPEC_DECISION:{source_id}")
            check(target["v86_evidence_class"] == spec["evidence_class"], f"SPEC_EVIDENCE_CLASS:{source_id}")
            check(target["v86_open_semantic_slots"] == spec["open_semantic_slots"], f"SPEC_OPEN_SLOTS:{source_id}")
            check(target["family_ids"] == spec["family_ids"], f"SPEC_FAMILY:{source_id}")
            check(target["decomposition"] == spec["decomposition"], f"SPEC_DECOMPOSITION:{source_id}")
            base = int(source["working_model_score_0_100_not_probability"])
            expected_score = min(base + int(spec["score_delta_lexical_core"]), int(spec["lexical_core_cap"]))
            expected_context = min(expected_score, int(spec["context_realization_cap"]))
            check(int(target["working_model_score_0_100_not_probability"]) == expected_score, f"SPEC_SCORE:{source_id}")
            check(target["working_model_level"] == level(expected_score), f"SPEC_LEVEL:{source_id}")
            check(int(target["context_realization_score_0_100_not_probability"]) == expected_context, f"SPEC_CONTEXT_SCORE:{source_id}")
            check(target["context_realization_level"] == level(expected_context), f"SPEC_CONTEXT_LEVEL:{source_id}")
            check(target["historical_confirmation"] == HISTORICAL, f"SPEC_H0:{source_id}")
            check(target["v86_component_global_export_allowed"] == "0", f"SPEC_COMPONENT_NO_EXPORT:{source_id}")
            if spec["decision"] == "HOLD":
                check(target["v86_lexical_core_de"] == source["v85_lexical_core_de"], f"HOLD_CORE_EXACT:{source_id}")
                check(source_id == "dol#1" and expected_score == 23, f"DOL_HOLD_EXACT_WHOLE_EVIDENCE_SCORE:{source_id}")
            else:
                check(target["v86_lexical_core_de"] != source["v85_lexical_core_de"], f"REVISE_CORE_CHANGED:{source_id}")
            if int(spec["score_delta_lexical_core"]) > 0:
                check(
                    spec["resolved_debt_atom"] not in {"", "NONE"}
                    or spec["evidence_class"] == "EXACT_WHOLE_FAMILY_CONFIRMATION",
                    f"POSITIVE_DELTA_NAMED_BASIS:{source_id}",
                )
            for field in ["semantic_scope", "semantic_applicability", "global_export_scope", "bound_span_ids", "unconditional_global_export_allowed"]:
                check(target[field] == source[field], f"TARGET_SCOPE_PRESERVED:{source_id}:{field}")
        if source["working_model_level"] == "W3_SOLID_WORKING_THEORY":
            w3_rows += 1
            w3_positions += int(source["occurrence_count"])
    check(w3_rows == 19 and w3_positions == 77, "NINETEEN_W3_SEVENTY_SEVEN_POSITIONS_PRESERVED")

    expected_active_levels = Counter({
        "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY": 7, "W1_WEAK_WORKING": 143,
        "W2_PROVISIONAL_WORKING": 155, "W3_SOLID_WORKING_THEORY": 19,
    })
    check(Counter(row["working_model_level"] for row in lexical) == expected_active_levels, "ACTIVE_LEVEL_DISTRIBUTION")
    check(Counter(row["semantic_applicability"] for row in lexical) == Counter({
        "SEMANTIC_WORKING_READING": 317, "STRUCTURAL_OR_PUNCTUATION_READING": 5,
        "COMPOUND_ONLY_LOCAL_READING": 2,
    }), "ACTIVE_APPLICABILITY_DISTRIBUTION")
    check(Counter(row["global_export_scope"] for row in lexical) == Counter({
        "ACTIVE_WORKING_DEFAULT": 309, "BOUND_SPAN_ONLY_NO_GLOBAL_EXPORT": 6,
        "NAMED_CONTEXT_ONLY": 8, "NAMED_CONTEXT_ONLY|BOUND_SPAN_ONLY_NO_GLOBAL_EXPORT": 1,
    }), "ACTIVE_EXPORT_DISTRIBUTION")

    source_context_by_key = {occurrence_key(row): row for row in source_context}
    target_context_by_key = {occurrence_key(row): row for row in context}
    check(len(source_context_by_key) == len(target_context_by_key) == 479, "CONTEXT_KEYS_UNIQUE")
    check(set(source_context_by_key) == set(target_context_by_key), "CONTEXT_KEY_PARITY")
    base_context_fields = [field for field in source_context[0] if "v85" not in field.lower()]
    target_position_rows: list[dict[str, str]] = []
    for key, source in source_context_by_key.items():
        target = target_context_by_key[key]
        for field in base_context_fields:
            check(target[field] == source[field], f"CONTEXT_SOURCE_PARITY:{key}:{field}")
        source_id = source["source_reading_id"]
        lexical_target = target_by_id[source_id]
        check(target["v86_reading_id"] == lexical_target["v86_reading_id"], f"CONTEXT_LEXICAL_LINK:{key}")
        check(target["v86_lexical_core_de"] == lexical_target["v86_lexical_core_de"], f"CONTEXT_CORE:{key}")
        check(target["v86_semantic_scope"] == lexical_target["semantic_scope"], f"CONTEXT_SCOPE:{key}")
        check(target["v86_semantic_applicability"] == lexical_target["semantic_applicability"], f"CONTEXT_APPLICABILITY:{key}")
        check(target["v86_historical_confirmation"] == HISTORICAL, f"CONTEXT_H0:{key}")
        if source_id in EXPECTED_TARGETS:
            target_position_rows.append(target)
            spec = specs_by_id[source_id]
            check(target["v86_context_realization_de"] == spec["v86_context_realization_de"], f"CONTEXT_SPEC_RENDER:{key}")
            check(target["v86_audit_decision"] == spec["decision"], f"CONTEXT_SPEC_DECISION:{key}")
            check(target["v68_action_license"] == "NOT_ACTION_LICENSED", f"TARGET_NOMINAL_LICENSE:{key}")
            check(target["v68_active_verb_occurrences"] == "0", f"TARGET_ZERO_ACTIVE_VERBS:{key}")
            check(target["v57_identity_signals"] == "NONE", f"TARGET_ZERO_IDENTITY:{key}")
        else:
            for field in source_context[0]:
                if "v85" in field.lower() and field not in RESET_CONTEXT_AUDIT_FIELDS:
                    check(target[v86_key(field)] == source[field], f"NON_TARGET_CONTEXT_PARITY:{key}:{field}")
    check(len(target_position_rows) == 10, "TARGET_10_POSITIONS")
    check(len({row["page"] for row in target_position_rows}) == 7, "TARGET_7_PAGES")
    check({occurrence_key(row) for row in target_position_rows} == EXPECTED_TARGET_OCCURRENCES, "TARGET_EXACT_OCCURRENCES")
    check(Counter(row["v86_occurrence_bound_span_id"] for row in context) == Counter({
        "NONE": 471, "B001": 2, "B002": 2, "B003": 2, "G683_CHEOP_OL": 2,
    }), "BOUND_SPAN_POSITION_DISTRIBUTION")
    check(sum(row["v86_occurrence_bound_span_global_export_allowed"] == "0" for row in context) == 8, "EIGHT_BOUND_POSITION_EXPORT_STOPS")
    cheop = target_context_by_key[("f115r", "f115r.1", 5, "cheop")]
    ol_bound = target_context_by_key[("f115r", "f115r.1", 6, "ol")]
    check((cheop["v86_occurrence_bound_span_id"], cheop["v86_occurrence_bound_span_role"]) == ("G683_CHEOP_OL", "LEFT"), "CHEOP_LEFT")
    check((ol_bound["v86_occurrence_bound_span_id"], ol_bound["v86_occurrence_bound_span_role"]) == ("G683_CHEOP_OL", "RIGHT"), "OL2_RIGHT")
    check(cheop["v86_occurrence_bound_span_global_export_allowed"] == ol_bound["v86_occurrence_bound_span_global_export_allowed"] == "0", "CHEOP_OL_NO_EXPORT")

    source_held_ids = {row["source_reading_id"] for row in source_census if row["disposition"] == "HELD_FOR_LATER_REPAIR"}
    check(len(source_held_ids) == 118, "SOURCE_118_HELD")
    check({row["source_reading_id"] for row in census} == source_held_ids, "CENSUS_SOURCE_SET_PARITY")
    check(Counter(row["disposition"] for row in census) == Counter({
        "REVISED_IN_V86": 8, "AUDITED_HOLD_IN_V86": 1, "HELD_FOR_LATER_REPAIR": 109,
    }), "CENSUS_DISPOSITION_PARTITION")
    check({row["source_reading_id"] for row in delta} == EXPECTED_TARGETS, "DELTA_EXACT_TARGET_SET")
    for row in delta:
        spec = specs_by_id[row["source_reading_id"]]
        check(row["decision"] == spec["decision"], f"DELTA_DECISION:{row['source_reading_id']}")
        check(row["v86_lexical_core_de"] == spec["v86_lexical_core_de"], f"DELTA_CORE:{row['source_reading_id']}")
        check(row["evidence_de"] == spec["evidence_de"], f"DELTA_EVIDENCE:{row['source_reading_id']}")
        check(row["counterevidence_de"] == spec["counterevidence_de"], f"DELTA_COUNTER:{row['source_reading_id']}")
        check(row["historical_confirmation"] == HISTORICAL, f"DELTA_H0:{row['source_reading_id']}")

    expected_family_ids = {"F_CKH", "F_STATE", "F_STAGE", "F_O", "F_D", "F_OL", "F_OR", "F_AM"}
    check({row["family_id"] for row in families} == expected_family_ids, "EXACT_8_FAMILIES")
    for row in families:
        check(row["historical_confirmation"] == HISTORICAL, f"FAMILY_H0:{row['family_id']}")
        check(row["automatic_historical_credit"] == "0", f"FAMILY_ZERO_HISTORICAL_CREDIT:{row['family_id']}")
    family_needles = {
        "F_CKH": ("CKH", "CPH"), "F_STATE": ("CH", "SH", "+T+"),
        "F_STAGE": ("+Y",), "F_O": ("O_PREP",), "F_D": ("D+",),
        "F_OL": ("OL",), "F_OR": ("OR+",), "F_AM": ("AM",),
    }
    for spec in specs:
        for family in split_pipe(spec["family_ids"]):
            check(any(needle in spec["decomposition"] for needle in family_needles[family]), f"FAMILY_VISIBLE_IN_DECOMPOSITION:{spec['source_reading_id']}:{family}")

    check(spans == source_spans, "BOUND_SPAN_TABLE_INHERITED_EXACT")
    span = spans[0]
    check(span["bound_span_id"] == "G683_CHEOP_OL", "SPAN_ID")
    check(span["left_position_id"] == "P167" and span["right_position_id"] == "P168", "SPAN_POSITIONS")
    check(span["left_role"] == "LEFT" and span["right_role"] == "RIGHT", "SPAN_ROLES")
    check(span["render_once_de"] == "bis zur Mittelstufe getrockneter Pulverstoff", "SPAN_RENDER_ONCE")
    check(span["global_export_allowed"] == "0" and span["historical_confirmation"] == HISTORICAL, "SPAN_NO_EXPORT_H0")

    check(len({(row["surface"], row["reading_id"]) for row in complete}) == 1586, "COMPLETE_READING_KEYS_UNIQUE")
    check(len({row["surface"] for row in complete}) == 1582, "COMPLETE_1582_SURFACES")
    expected_complete_levels = Counter({
        "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY": 287, "W1_WEAK_WORKING": 323,
        "W2_PROVISIONAL_WORKING": 533, "W3_SOLID_WORKING_THEORY": 443,
    })
    check(Counter(row["working_model_level"] for row in complete) == expected_complete_levels, "COMPLETE_LEVEL_DISTRIBUTION")
    for row in complete:
        reading_key = f"{row['surface']}:{row['reading_id']}"
        check(row["working_model_score_0_100_not_probability"].isdigit(), f"COMPLETE_SCORE_PRESENT:{reading_key}")
        check(row["working_model_level"] == level(int(row["working_model_score_0_100_not_probability"])), f"COMPLETE_SCORE_LEVEL:{reading_key}")
        check(bool(row["positive_evidence_de"]), f"COMPLETE_POSITIVE_EVIDENCE:{reading_key}")
        check(bool(row["counterevidence_de"]), f"COMPLETE_COUNTEREVIDENCE:{reading_key}")
        check(row["historical_confirmation"] == HISTORICAL, f"COMPLETE_H0:{reading_key}")
    complete_active = [row for row in complete if row["current_layer"] == "ACTIVE_V86_LEXICAL_CORE"]
    check(len(complete_active) == 324, "COMPLETE_324_ACTIVE")
    complete_by_sources = lexical_source_map(complete_active)
    for source_id, lexical_row in target_by_id.items():
        complete_row = complete_by_sources[source_id]
        check(complete_row["working_meaning_de"] == lexical_row["v86_lexical_core_de"], f"COMPLETE_ACTIVE_CORE:{source_id}")
        check(complete_row["working_model_score_0_100_not_probability"] == lexical_row["working_model_score_0_100_not_probability"], f"COMPLETE_ACTIVE_SCORE:{source_id}")
        check(complete_row["positive_evidence_de"] == lexical_row["positive_evidence_de"], f"COMPLETE_ACTIVE_EVIDENCE:{source_id}")

    forbidden_translation_literals = re.compile(r"\b(?:Kopf offen|EXACT|BOUND|QO_ROLE|MATERIAL_IDENTITY|PATIENT)\b", re.IGNORECASE)
    forbidden_revised_nouns = re.compile(r"\b(?:Arznei\w*|Rohdroge|Drogenstoff|Dosis)\b", re.IGNORECASE)
    for spec in specs:
        for field in ("v86_lexical_core_de", "v86_context_realization_de"):
            value = spec[field]
            check(not forbidden_translation_literals.search(value), f"NO_STRUCTURAL_LITERAL_IN_GERMAN:{spec['source_reading_id']}:{field}")
            if spec["decision"] == "REVISE":
                check(not forbidden_revised_nouns.search(value), f"NO_RETIRED_NOUN_IN_REVISED_GERMAN:{spec['source_reading_id']}:{field}")
        check(bool(spec["evidence_de"] and spec["counterevidence_de"]), f"SPEC_EVIDENCE_COMPLETE:{spec['source_reading_id']}")

    expected_cores = {
        "checkhy#1": "trockene Mischung, Anfangsstufe",
        "cheockhy#1": "trockene Mischung, Anfangsstufe",
        "ckhy#1": "Mischung, Anfangsstufe",
        "cphochy#1": "trockene Mischung, Grundstufe",
        "cphy#1": "Mischung, Grundform",
        "dol#1": "Materialmaß",
        "oram#1": "Maßportion",
        "otam#1": "kalt; Maß I",
        "sheckhy#1": "feuchte Mischung, Anfangsstufe",
    }
    for source_id, core in expected_cores.items():
        check(target_by_id[source_id]["v86_lexical_core_de"] == core, f"EXPECTED_COMPACT_CORE:{source_id}")
    for source_id in {"checkhy#1", "cheockhy#1", "ckhy#1", "cphochy#1", "cphy#1", "sheckhy#1"}:
        check("Misch" in target_by_id[source_id]["v86_lexical_core_de"], f"CKH_CPH_MIXTURE_HEAD:{source_id}")
        check(not re.search(r"Arznei|Droge", target_by_id[source_id]["v86_lexical_core_de"], re.IGNORECASE), f"CKH_CPH_NO_DRUG_IDENTITY:{source_id}")
    check(target_by_id["oram#1"]["v86_context_realizations_de"] == "eine Maßportion", "ORAM_NO_ANSATZ_CONTEXT")
    check(target_by_id["otam#1"]["v86_context_realizations_de"] == "ein Maß kalten Ansatzes", "OTAM_LOCAL_CONCRETE_CONTEXT")
    for source_id in {"am#1", "dam#1", "chckhy#1", "shckhy#1"}:
        source = source_by_id[source_id]
        target = target_by_id[source_id]
        for field in source_fields:
            if field in RESET_LEXICAL_AUDIT_FIELDS:
                continue
            check(target[v86_key(field)] == source[field], f"PRIOR_REPAIR_BYTE_VALUE_PRESERVED:{source_id}:{field}")

    for row in context:
        check(not row["page"].startswith("f84") and not row["locus"].startswith("f84"), f"NO_F84_CONTEXT_SELECTOR:{row['position_id']}")
    for row in delta:
        check(all(not page.startswith("f84") for page in split_pipe(row["pages"])), f"NO_F84_DELTA_PAGE:{row['source_reading_id']}")
    for row in spans:
        check(not row["page"].startswith("f84") and not row["locus"].startswith("f84"), "NO_F84_SPAN_SELECTOR")

    validation = {
        "experiment_id": "GDT713",
        "status": "PASS",
        "checks": len(checks),
        "deterministic_outputs": len(GENERATED),
        "audited_readings": 9,
        "audited_positions": 10,
        "audited_pages": 7,
        "revised_readings": 8,
        "held_readings": 1,
        "remaining_unreviewed_weak_readings": 109,
        "active_lexical_readings": 324,
        "active_positions": 479,
        "complete_readings": 1586,
        "complete_surfaces": 1582,
        "w3_preserved_readings": w3_rows,
        "w3_preserved_positions": w3_positions,
        "historical_confirmation": HISTORICAL,
        "relation_word_credit_gdt713": 0,
        "new_pages": 0,
        "f84_or_f84r_used": 0,
        "output_sha256": {path.name: digest(path) for path in GENERATED},
    }
    VALIDATION.write_text(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
