#!/usr/bin/env python3
"""Independent validator for the GDT714 V87 dictionary and span repair."""

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
EXP = ROOT / "experiments/yolo/gdt714_v87_bound_c1_core_context_repair"
SRC = EXP / "src"
ART = EXP / "artifacts"
G713 = ROOT / "experiments/yolo/gdt713_v86_measure_ckh_core_context_repair/artifacts"
G711 = ROOT / "experiments/yolo/gdt711_v84_active_weak_family_repair/artifacts"

SOURCE_LEXICAL = G713 / "V86_324_ACTIVE_LEXICAL_READINGS.tsv"
SOURCE_CONTEXT = G713 / "V86_479_CONTEXT_REALIZATIONS.tsv"
SOURCE_COMPLETE = G713 / "V86_COMPLETE_WORD_CONFIDENCE.tsv"
SOURCE_CENSUS = G713 / "V86_118_HELD_READING_AUDIT.tsv"
SOURCE_SPANS = G713 / "V86_1_BOUND_SPAN_RENDERER.tsv"
SOURCE_FAMILIES = G711 / "V84_13_STEM_FAMILY_EVIDENCE.tsv"
SPECS = SRC / "V87_18_AUDIT_SPECS.tsv"
BOUNDARY_SPECS = SRC / "V87_1_BOUNDARY_SPECS.tsv"
PRIMARY_BINDINGS = SRC / "V87_18_PRIMARY_EVIDENCE_BINDINGS.tsv"
G678_BOUNDARIES = ROOT / "experiments/yolo/gdt678_seventeen_two_hole_family_completion/artifacts/BOUNDARY_DECISIONS.tsv"
G679_BOUNDARIES = ROOT / "experiments/yolo/gdt679_eight_three_hole_family_completion/artifacts/BOUNDARY_DECISIONS.tsv"

LEXICAL = ART / "V87_324_ACTIVE_LEXICAL_READINGS.tsv"
CONTEXT = ART / "V87_479_CONTEXT_REALIZATIONS.tsv"
CENSUS = ART / "V87_109_HELD_READING_AUDIT.tsv"
DELTA = ART / "V87_18_BOUND_C1_CORE_CONTEXT_DELTA.tsv"
FAMILIES = ART / "V87_7_FAMILY_EVIDENCE.tsv"
SPANS = ART / "V87_2_BOUND_SPAN_RENDERER.tsv"
BOUNDARY_DELTA = ART / "V87_1_BOUNDARY_DELTA.tsv"
PRIMARY_EVIDENCE = ART / "V87_18_PRIMARY_EVIDENCE_BINDINGS.tsv"
ONE_SHOT_DIRECTIVES = ART / "V87_2_ONE_SHOT_RENDER_DIRECTIVES.tsv"
F7R2_RENDERED = ART / "V87_8_F7R2_RENDERED_UNITS.tsv"
COMPLETE = ART / "V87_COMPLETE_WORD_CONFIDENCE.tsv"
RESULT = ART / "RESULT.json"
REPORT = EXP / "REPORT.md"
VALIDATION = ART / "VALIDATION.json"

GENERATED = [
    LEXICAL, CONTEXT, CENSUS, DELTA, FAMILIES, SPANS, BOUNDARY_DELTA,
    PRIMARY_EVIDENCE, ONE_SHOT_DIRECTIVES, F7R2_RENDERED,
    COMPLETE, RESULT, REPORT,
]
HISTORICAL = "H0_NONE"
EXPECTED_STATUS = (
    "PASS_V87_18_BOUND_C1_READINGS_REVISED__18_TARGET_POSITIONS_12_PAGES__"
    "1_KEO_R_ONE_SHOT_SPAN__7_W0_135_W1_163_W2_19_W3__"
    "91_WEAK_READINGS_REMAIN__ALL_H0_NONE"
)
EXPECTED_TARGETS = {
    "chedaiin#1", "chodaiin#1", "cholkain#1", "chos#1", "chs#1",
    "dshees#1", "dshey#1", "kc#1", "keo#1", "kor#1", "okees#1",
    "olkaiin#1", "orchey#1", "orsheey#1", "os#1", "oteor#1",
    "oty#1", "tchedaiin#1",
}
EXPECTED_TARGET_OCCURRENCES = {
    ("f86v3", "f86v3.13", 7, "chedaiin"),
    ("f114r", "f114r.26", 4, "chodaiin"),
    ("f86v3", "f86v3.13", 11, "cholkain"),
    ("f114r", "f114r.24", 7, "chos"),
    ("f77v", "f77v.7", 8, "chs"),
    ("f105r", "f105r.2", 1, "dshees"),
    ("f95v1", "f95v1.7", 1, "dshey"),
    ("f8r", "f8r.15", 5, "kc"),
    ("f7r", "f7r.2", 2, "keo"),
    ("f23r", "f23r.6", 3, "kor"),
    ("f105r", "f105r.2", 10, "okees"),
    ("f114r", "f114r.26", 6, "olkaiin"),
    ("f75r", "f75r.3", 3, "orchey"),
    ("f86v3", "f86v3.13", 2, "orsheey"),
    ("f10r", "f10r.2", 5, "os"),
    ("f86v6", "f86v6.4", 8, "oteor"),
    ("f27r", "f27r.9", 5, "oty"),
    ("f114r", "f114r.24", 1, "tchedaiin"),
}
EXPECTED_CORES = {
    "chedaiin#1": "abgemessene Trockenmenge III, Mittelstufe",
    "chodaiin#1": "trockene Zubereitung; Mengenwert III",
    "cholkain#1": "trocken-heiß; Wert II",
    "chos#1": "trockene Zubereitung",
    "chs#1": "trockene Grundform",
    "dshees#1": "abgemessene feuchte Form, Endstufe",
    "dshey#1": "abgemessene Feuchtmenge, Mittelstufe",
    "kc#1": "heiß-trocken",
    "keo#1": "heiße Zubereitung, Mittelstufe",
    "kor#1": "heiße Portion",
    "okees#1": "heiße Zubereitung, Endstufe",
    "olkaiin#1": "heiß; Wert III",
    "orchey#1": "trockene Portion, Mittelstufe",
    "orsheey#1": "feuchte Portion, Endstufe",
    "os#1": "Zubereitung",
    "oteor#1": "kalte Portion, Mittelstufe",
    "oty#1": "kalte Zubereitung, Anfangsstufe",
    "tchedaiin#1": "abgemessene kalt-trockene Menge III, Mittelstufe",
}
RESET_LEXICAL_AUDIT_FIELDS = {
    "v86_audit_decision", "v86_evidence_class", "v86_open_semantic_slots",
    "v86_component_global_export_allowed", "v86_prior_lexical_core_de",
}
RESET_CONTEXT_AUDIT_FIELDS = {
    "v86_audit_decision", "v86_evidence_class", "v86_open_semantic_slots",
    "v86_component_global_export_allowed",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_pipe(value: str) -> list[str]:
    return [part.strip() for part in value.split("|") if part.strip() and part.strip() not in {"NONE", "0"}]


def parse_assertions(value: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for part in value.split(";"):
        if not part:
            continue
        field, expected = part.split("=", 1)
        if not field or field in result:
            raise AssertionError(f"invalid assertion list: {value}")
        result[field] = expected
    return result


def v87_key(value: str) -> str:
    return value.replace("v86", "v87").replace("V86", "V87")


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


def lexical_source_map(
    rows: list[dict[str, str]], id_field: str = "source_reading_ids"
) -> dict[str, dict[str, str]]:
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

    static_inputs = [
        SOURCE_LEXICAL, SOURCE_CONTEXT, SOURCE_COMPLETE, SOURCE_CENSUS,
        SOURCE_SPANS, SOURCE_FAMILIES, SPECS, BOUNDARY_SPECS,
        PRIMARY_BINDINGS, G678_BOUNDARIES, G679_BOUNDARIES,
    ]
    for path in static_inputs:
        check(path.is_file(), f"EXISTS:{path.relative_to(ROOT)}")
    preliminary_bindings = read_tsv(PRIMARY_BINDINGS)
    primary_source_paths = sorted({ROOT / row["evidence_path"] for row in preliminary_bindings})
    inputs = [*static_inputs, *primary_source_paths]
    for path in [*primary_source_paths, *GENERATED]:
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
    boundary_specs = read_tsv(BOUNDARY_SPECS)
    primary_bindings = read_tsv(PRIMARY_BINDINGS)
    g678_boundaries = read_tsv(G678_BOUNDARIES)
    g679_boundaries = read_tsv(G679_BOUNDARIES)
    lexical = read_tsv(LEXICAL)
    context = read_tsv(CONTEXT)
    census = read_tsv(CENSUS)
    delta = read_tsv(DELTA)
    families = read_tsv(FAMILIES)
    spans = read_tsv(SPANS)
    boundary_delta = read_tsv(BOUNDARY_DELTA)
    primary_evidence = read_tsv(PRIMARY_EVIDENCE)
    one_shot_directives = read_tsv(ONE_SHOT_DIRECTIVES)
    f7r2_rendered = read_tsv(F7R2_RENDERED)
    complete = read_tsv(COMPLETE)
    result: dict[str, Any] = json.loads(RESULT.read_text(encoding="utf-8"))

    expected_counts = {
        "source_lexical": (len(source_lexical), 324),
        "source_context": (len(source_context), 479),
        "source_complete": (len(source_complete), 1586),
        "source_census": (len(source_census), 118),
        "source_spans": (len(source_spans), 1),
        "source_families": (len(source_families), 13),
        "specs": (len(specs), 18),
        "boundary_specs": (len(boundary_specs), 1),
        "primary_bindings": (len(primary_bindings), 18),
        "lexical": (len(lexical), 324),
        "context": (len(context), 479),
        "census": (len(census), 109),
        "delta": (len(delta), 18),
        "families": (len(families), 7),
        "spans": (len(spans), 2),
        "boundary_delta": (len(boundary_delta), 1),
        "primary_evidence": (len(primary_evidence), 18),
        "one_shot_directives": (len(one_shot_directives), 2),
        "f7r2_rendered": (len(f7r2_rendered), 8),
        "complete": (len(complete), 1586),
    }
    for label, (actual, expected) in expected_counts.items():
        check(actual == expected, f"COUNT:{label}:{expected}")

    check(result["status"] == EXPECTED_STATUS, "RESULT_STATUS")
    check(
        result["f84_or_f84r_used"] == result["new_pages"]
        == result["new_images"] == result["new_transcription"] == 0,
        "RESULT_NO_NEW_OR_SEALED_MATERIAL",
    )
    check(result["relation_word_credit_gdt714"] == 0, "RESULT_ZERO_RELATION_WORD_CREDIT")
    check(result["revised_readings"] == 18 and result["held_readings"] == 0, "RESULT_DECISION_COUNTS")
    check(result["revised_positions"] == 18 and result["held_positions"] == 0, "RESULT_POSITION_PARTITION")
    check(result["remaining_unreviewed_weak_readings"] == 91, "RESULT_91_REMAIN")
    check(result["boundary_spans_added"] == 1 and result["boundary_positions_touched"] == 2, "RESULT_ONE_TWO_POSITION_SPAN")
    check(result["primary_evidence_bindings"] == 18, "RESULT_18_PRIMARY_BINDINGS")
    check(result["one_shot_directives"] == 2 and result["f7r2_rendered_units"] == 8, "RESULT_EXECUTABLE_RENDER_COUNTS")

    specs_by_id = {row["source_reading_id"]: row for row in specs}
    check(set(specs_by_id) == EXPECTED_TARGETS, "EXACT_18_TARGET_IDS")
    check(Counter(row["decision"] for row in specs) == Counter({"REVISE": 18}), "SPEC_ALL_REVISE")
    check(all(row["component_global_export_allowed"] == "0" for row in specs), "SPEC_ZERO_COMPONENT_EXPORT")
    check(all(row["occurrence_bound_span_override"] == "NONE" for row in specs), "SPEC_NO_LEXICAL_SPAN_SCOPE_REWRITE")

    bindings_by_id = {row["source_reading_id"]: row for row in primary_bindings}
    evidence_by_id = {row["source_reading_id"]: row for row in primary_evidence}
    check(set(bindings_by_id) == EXPECTED_TARGETS, "PRIMARY_BINDING_EXACT_18_TARGETS")
    check(set(evidence_by_id) == EXPECTED_TARGETS, "PRIMARY_EVIDENCE_EXACT_18_TARGETS")
    family_by_id = {row["family_id"]: row for row in source_families}
    zero_credit_modes = {
        "CORE_COMPRESSION_PLUS_PREDECLARED_BOUNDARY_RENDERER",
        "LEXICAL_CORE_CONTEXT_SPLIT",
        "CORE_CONTEXT_COMPRESSION",
        "STATE_CORE_NORMALIZATION_NO_SCORE_GAIN",
        "READER_REPAIRED_STATE_FORM_NO_SCORE_GAIN",
        "EXPLORATORY_WHOLE_READING_WITH_IDENTITY_REMOVAL",
    }
    for source_id, binding in bindings_by_id.items():
        spec = specs_by_id[source_id]
        source_path = ROOT / binding["evidence_path"]
        check(source_path in primary_source_paths, f"PRIMARY_PATH_BOUND:{source_id}")
        selector = parse_assertions(binding["selector"])
        assertions = parse_assertions(binding["field_assertions"])
        matches = [
            row for row in read_tsv(source_path)
            if all(row.get(field) == expected for field, expected in selector.items())
        ]
        check(len(matches) == 1, f"PRIMARY_EXACT_ONE_ROW:{source_id}")
        source_row = matches[0]
        check(source_row["surface"] == binding["expected_source_surface"], f"PRIMARY_SURFACE:{source_id}")
        if binding["expected_source_decomposition"] == "NONE":
            check("composition" not in source_row or source_row["composition"] in {"", "NONE"}, f"PRIMARY_NO_SOURCE_COMPOSITION:{source_id}")
        else:
            check(source_row["composition"] == binding["expected_source_decomposition"], f"PRIMARY_SOURCE_DECOMPOSITION:{source_id}")
        for field, expected in assertions.items():
            check(source_row[field] == expected, f"PRIMARY_ASSERTION:{source_id}:{field}")
        check(spec["decomposition"] == binding["normalized_decomposition"], f"PRIMARY_NORMALIZED_DECOMPOSITION:{source_id}")
        credit_families = split_pipe(binding["score_credit_family_ids"])
        check(len(credit_families) == len(set(credit_families)), f"PRIMARY_DISTINCT_SCORE_FAMILIES:{source_id}")
        check(set(credit_families).issubset(set(split_pipe(spec["family_ids"]))), f"PRIMARY_SCORE_FAMILY_SUBSET:{source_id}")
        derived_delta = sum(int(family_by_id[family]["family_bonus"]) for family in credit_families)
        check(int(spec["score_delta_lexical_core"]) == derived_delta, f"PRIMARY_DERIVED_SCORE_DELTA:{source_id}")
        if spec["repair_mode"] in zero_credit_modes:
            check(derived_delta == 0, f"PROSE_OR_BOUNDARY_REPAIR_ZERO_CREDIT:{source_id}")
        evidence = evidence_by_id[source_id]
        expected_evidence_fields = {
            "source_gdt": binding["source_gdt"],
            "evidence_path": binding["evidence_path"],
            "selector": binding["selector"],
            "source_surface": source_row["surface"],
            "source_decomposition": binding["expected_source_decomposition"],
            "normalized_decomposition": binding["normalized_decomposition"],
            "field_assertions": binding["field_assertions"],
            "score_credit_family_ids": binding["score_credit_family_ids"],
            "normalization_class": binding["normalization_class"],
            "source_row_match": "1",
            "evidence_status": "BOUND_EXACT_PRIMARY_ROW",
            "historical_confirmation": HISTORICAL,
        }
        for field, expected in expected_evidence_fields.items():
            check(evidence[field] == expected, f"PRIMARY_ARTIFACT_FIELD:{source_id}:{field}")

    g678_f7r2 = [
        row for row in g678_boundaries
        if row["locus"] == "f7r.2" and row["ordinal"] == "2" and row["surface"] == "keo"
    ]
    check(len(g678_f7r2) == 1, "G678_F7R2_EXACT_BOUNDARY_ROW")
    check(
        g678_f7r2[0]["it2a_operation"] == "MERGE_2"
        and g678_f7r2[0]["it2a_render"] == "keor"
        and g678_f7r2[0]["rf1b_operation"] == "EXACT"
        and g678_f7r2[0]["rf1b_render"] == "keo"
        and g678_f7r2[0]["reader_support"] == "RF1B_ONLY_EXACT",
        "G678_F7R2_READER_CLASS_BOUND",
    )
    g679_reader_rows = {
        row["surface"]: row for row in g679_boundaries
        if row["surface"] in {"orsheey", "kc"}
    }
    check(set(g679_reader_rows) == {"orsheey", "kc"}, "G679_TWO_READER_ROWS_BOUND")
    check(
        g679_reader_rows["orsheey"]["it2a_operation"] == "SPLIT_2"
        and g679_reader_rows["orsheey"]["rf1b_operation"] == "ONE"
        and g679_reader_rows["orsheey"]["reader_support"] == "NEITHER_EXACT",
        "G679_ORSHEEY_READER_CLASS_BOUND",
    )
    check(
        g679_reader_rows["kc"]["it2a_render"] == "kchs"
        and g679_reader_rows["kc"]["rf1b_render"] == "kchs"
        and g679_reader_rows["kc"]["reader_support"] == "NEITHER_EXACT",
        "G679_KC_READER_CLASS_BOUND",
    )

    source_by_id = lexical_source_map(source_lexical)
    target_by_id = lexical_source_map(lexical)
    check(len(source_by_id) == len(target_by_id) == 332, "LEXICAL_SOURCE_MAP_332")
    check(set(source_by_id) == set(target_by_id), "LEXICAL_SOURCE_MAP_PARITY")
    check(len({row["v87_reading_id"] for row in lexical}) == 324, "V87_READING_IDS_UNIQUE")

    source_fields = list(source_lexical[0])
    w3_rows = 0
    w3_positions = 0
    for source_id, source in source_by_id.items():
        target = target_by_id[source_id]
        if source_id not in EXPECTED_TARGETS:
            for field in source_fields:
                if field in RESET_LEXICAL_AUDIT_FIELDS:
                    continue
                check(target[v87_key(field)] == source[field], f"NON_TARGET_LEXICAL_PARITY:{source_id}:{field}")
            check(target["v87_audit_decision"] == "NOT_IN_GDT714_TRANCHE", f"NON_TARGET_DECISION:{source_id}")
        else:
            spec = specs_by_id[source_id]
            check(source["v86_lexical_core_de"] == spec["old_lexical_core_de"], f"SPEC_OLD_CORE:{source_id}")
            check(target["v87_lexical_core_de"] == spec["v87_lexical_core_de"] == EXPECTED_CORES[source_id], f"SPEC_NEW_CORE:{source_id}")
            check(target["v87_context_realizations_de"] == spec["v87_context_realization_de"], f"SPEC_CONTEXT:{source_id}")
            check(target["v87_lexical_core_de"] != source["v86_lexical_core_de"], f"REVISE_CORE_CHANGED:{source_id}")
            check(target["v87_audit_decision"] == "REVISE", f"SPEC_DECISION:{source_id}")
            check(target["v87_evidence_class"] == spec["evidence_class"], f"SPEC_EVIDENCE_CLASS:{source_id}")
            check(target["v87_open_semantic_slots"] == spec["open_semantic_slots"], f"SPEC_OPEN_SLOTS:{source_id}")
            check(target["family_ids"] == spec["family_ids"], f"SPEC_FAMILY:{source_id}")
            check(target["decomposition"] == spec["decomposition"], f"SPEC_DECOMPOSITION:{source_id}")
            base = int(source["working_model_score_0_100_not_probability"])
            expected_score = min(base + int(spec["score_delta_lexical_core"]), int(spec["lexical_core_cap"]))
            expected_context_score = min(expected_score, int(spec["context_realization_cap"]))
            check(int(target["working_model_score_0_100_not_probability"]) == expected_score, f"SPEC_SCORE:{source_id}")
            check(target["working_model_level"] == level(expected_score), f"SPEC_LEVEL:{source_id}")
            check(int(target["context_realization_score_0_100_not_probability"]) == expected_context_score, f"SPEC_CONTEXT_SCORE:{source_id}")
            check(target["context_realization_level"] == level(expected_context_score), f"SPEC_CONTEXT_LEVEL:{source_id}")
            check(target["historical_confirmation"] == HISTORICAL, f"SPEC_H0:{source_id}")
            check(target["v87_component_global_export_allowed"] == "0", f"SPEC_COMPONENT_NO_EXPORT:{source_id}")
            for field in [
                "semantic_scope", "semantic_applicability", "global_export_scope",
                "bound_span_ids", "unconditional_global_export_allowed",
            ]:
                check(target[field] == source[field], f"TARGET_SCOPE_PRESERVED:{source_id}:{field}")
        if source["working_model_level"] == "W3_SOLID_WORKING_THEORY":
            w3_rows += 1
            w3_positions += int(source["occurrence_count"])
    check(w3_rows == 19 and w3_positions == 77, "NINETEEN_W3_SEVENTY_SEVEN_POSITIONS_PRESERVED")

    expected_active_levels = Counter({
        "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY": 7,
        "W1_WEAK_WORKING": 135,
        "W2_PROVISIONAL_WORKING": 163,
        "W3_SOLID_WORKING_THEORY": 19,
    })
    check(Counter(row["working_model_level"] for row in lexical) == expected_active_levels, "ACTIVE_LEVEL_DISTRIBUTION")
    check(Counter(row["semantic_applicability"] for row in lexical) == Counter({
        "SEMANTIC_WORKING_READING": 317,
        "STRUCTURAL_OR_PUNCTUATION_READING": 5,
        "COMPOUND_ONLY_LOCAL_READING": 2,
    }), "ACTIVE_APPLICABILITY_DISTRIBUTION")
    check(Counter(row["global_export_scope"] for row in lexical) == Counter({
        "ACTIVE_WORKING_DEFAULT": 309,
        "BOUND_SPAN_ONLY_NO_GLOBAL_EXPORT": 6,
        "NAMED_CONTEXT_ONLY": 8,
        "NAMED_CONTEXT_ONLY|BOUND_SPAN_ONLY_NO_GLOBAL_EXPORT": 1,
    }), "ACTIVE_EXPORT_DISTRIBUTION")

    source_context_by_key = {occurrence_key(row): row for row in source_context}
    target_context_by_key = {occurrence_key(row): row for row in context}
    check(len(source_context_by_key) == len(target_context_by_key) == 479, "CONTEXT_KEYS_UNIQUE")
    check(set(source_context_by_key) == set(target_context_by_key), "CONTEXT_KEY_PARITY")
    base_context_fields = [field for field in source_context[0] if "v86" not in field.lower()]
    target_position_rows: list[dict[str, str]] = []
    boundary_position_ids = {"P288", "P289"}
    boundary_version_fields = {
        "v86_occurrence_bound_span_id", "v86_occurrence_bound_span_role",
        "v86_occurrence_bound_span_global_export_allowed",
    }
    for key, source in source_context_by_key.items():
        target = target_context_by_key[key]
        for field in base_context_fields:
            check(target[field] == source[field], f"CONTEXT_SOURCE_PARITY:{key}:{field}")
        source_id = source["source_reading_id"]
        lexical_target = target_by_id[source_id]
        check(target["v87_reading_id"] == lexical_target["v87_reading_id"], f"CONTEXT_LEXICAL_LINK:{key}")
        check(target["v87_lexical_core_de"] == lexical_target["v87_lexical_core_de"], f"CONTEXT_CORE:{key}")
        check(target["v87_semantic_scope"] == lexical_target["semantic_scope"], f"CONTEXT_SCOPE:{key}")
        check(target["v87_semantic_applicability"] == lexical_target["semantic_applicability"], f"CONTEXT_APPLICABILITY:{key}")
        check(target["v87_historical_confirmation"] == HISTORICAL, f"CONTEXT_H0:{key}")
        if source_id in EXPECTED_TARGETS:
            target_position_rows.append(target)
            spec = specs_by_id[source_id]
            check(target["v87_context_realization_de"] == spec["v87_context_realization_de"], f"CONTEXT_SPEC_RENDER:{key}")
            check(target["v87_audit_decision"] == "REVISE", f"CONTEXT_SPEC_DECISION:{key}")
            check(target["v68_action_license"] == "NOT_ACTION_LICENSED", f"TARGET_NOMINAL_LICENSE:{key}")
            check(target["v68_active_verb_occurrences"] == "0", f"TARGET_ZERO_ACTIVE_VERBS:{key}")
            check(target["v57_identity_signals"] == "NONE", f"TARGET_ZERO_IDENTITY:{key}")
        else:
            for field in source_context[0]:
                if "v86" not in field.lower() or field in RESET_CONTEXT_AUDIT_FIELDS:
                    continue
                if source["position_id"] in boundary_position_ids and field in boundary_version_fields:
                    continue
                check(target[v87_key(field)] == source[field], f"NON_TARGET_CONTEXT_PARITY:{key}:{field}")
    check(len(target_position_rows) == 18, "TARGET_18_POSITIONS")
    check(len({row["page"] for row in target_position_rows}) == 12, "TARGET_12_PAGES")
    check({occurrence_key(row) for row in target_position_rows} == EXPECTED_TARGET_OCCURRENCES, "TARGET_EXACT_OCCURRENCES")

    expected_span_distribution = Counter({
        "NONE": 469, "B001": 2, "B002": 2, "B003": 2,
        "G683_CHEOP_OL": 2, "G678_KEO_R_F7R2": 2,
    })
    check(Counter(row["v87_occurrence_bound_span_id"] for row in context) == expected_span_distribution, "BOUND_SPAN_POSITION_DISTRIBUTION")
    check(sum(row["v87_occurrence_bound_span_global_export_allowed"] == "0" for row in context) == 10, "TEN_BOUND_POSITION_EXPORT_STOPS")
    keo = target_context_by_key[("f7r", "f7r.2", 2, "keo")]
    r_right = target_context_by_key[("f7r", "f7r.2", 3, "r")]
    check((keo["v87_occurrence_bound_span_id"], keo["v87_occurrence_bound_span_role"]) == ("G678_KEO_R_F7R2", "LEFT"), "KEO_LEFT")
    check((r_right["v87_occurrence_bound_span_id"], r_right["v87_occurrence_bound_span_role"]) == ("G678_KEO_R_F7R2", "RIGHT"), "R_RIGHT")
    check(keo["v87_boundary_render_once_de"] == r_right["v87_boundary_render_once_de"] == "heiße Portion", "KEO_R_RENDER_ONCE")
    check(keo["v87_boundary_decision"] == r_right["v87_boundary_decision"] == "JOIN_RIGHT_KNOWN_WHOLE", "KEO_R_BOUNDARY_DECISION")
    check(target_by_id["r#1"]["v87_lexical_core_de"] == "Wurzel", "R_GLOBAL_CORE_PRESERVED")
    check(target_by_id["r#1"]["working_model_score_0_100_not_probability"] == "31", "R_GLOBAL_SCORE_PRESERVED")
    check(target_by_id["r#1"]["global_export_scope"] == "ACTIVE_WORKING_DEFAULT", "R_GLOBAL_SCOPE_PRESERVED")

    source_held_ids = {
        row["source_reading_id"] for row in source_census
        if row["disposition"] == "HELD_FOR_LATER_REPAIR"
    }
    check(len(source_held_ids) == 109, "SOURCE_109_HELD")
    check({row["source_reading_id"] for row in census} == source_held_ids, "CENSUS_SOURCE_SET_PARITY")
    check(Counter(row["disposition"] for row in census) == Counter({
        "REVISED_IN_V87": 18, "HELD_FOR_LATER_REPAIR": 91,
    }), "CENSUS_DISPOSITION_PARTITION")
    check({row["source_reading_id"] for row in delta} == EXPECTED_TARGETS, "DELTA_EXACT_TARGET_SET")
    for row in delta:
        spec = specs_by_id[row["source_reading_id"]]
        check(row["decision"] == "REVISE", f"DELTA_DECISION:{row['source_reading_id']}")
        check(row["v87_lexical_core_de"] == spec["v87_lexical_core_de"], f"DELTA_CORE:{row['source_reading_id']}")
        check(row["evidence_de"] == spec["evidence_de"], f"DELTA_EVIDENCE:{row['source_reading_id']}")
        check(row["counterevidence_de"] == spec["counterevidence_de"], f"DELTA_COUNTER:{row['source_reading_id']}")
        check(row["historical_confirmation"] == HISTORICAL, f"DELTA_H0:{row['source_reading_id']}")

    expected_family_ids = {"F_STATE", "F_STAGE", "F_O", "F_D", "F_N", "F_OL", "F_OR"}
    check({row["family_id"] for row in families} == expected_family_ids, "EXACT_7_FAMILIES")
    for row in families:
        check(row["historical_confirmation"] == HISTORICAL, f"FAMILY_H0:{row['family_id']}")
        check(row["automatic_historical_credit"] == "0", f"FAMILY_ZERO_HISTORICAL_CREDIT:{row['family_id']}")
    family_needles = {
        "F_STATE": ("_DRY", "_MOIST", "_HOT", "_COLD"),
        "F_STAGE": ("_MIDDLE", "_END", "_START", "Y_CLOSE", "EEY_"),
        "F_O": ("O_PREP", "CHO_DRY_PREP"),
        "F_D": ("D_MEASURE",),
        "F_N": ("IN_II", "IIN_III"),
        "F_OL": ("OL_", "CHOL_"),
        "F_OR": ("OR_PORTION",),
    }
    for spec in specs:
        for family in split_pipe(spec["family_ids"]):
            check(any(needle in spec["decomposition"] for needle in family_needles[family]), f"FAMILY_VISIBLE_IN_DECOMPOSITION:{spec['source_reading_id']}:{family}")

    check(spans[0] == source_spans[0], "INHERITED_SPAN_EXACT")
    check(boundary_delta == boundary_specs, "BOUNDARY_DELTA_SPEC_EXACT")
    new_span = spans[1]
    check(new_span["bound_span_id"] == "G678_KEO_R_F7R2", "NEW_SPAN_ID")
    check(new_span["page"] == "f7r" and new_span["locus"] == "f7r.2", "NEW_SPAN_LOCUS")
    check(new_span["left_position_id"] == "P288" and new_span["right_position_id"] == "P289", "NEW_SPAN_POSITIONS")
    check(new_span["left_role"] == "LEFT" and new_span["right_role"] == "RIGHT", "NEW_SPAN_ROLES")
    check(new_span["render_once_de"] == "heiße Portion", "NEW_SPAN_RENDER")
    check(new_span["global_export_allowed"] == "0" and new_span["historical_confirmation"] == HISTORICAL, "NEW_SPAN_NO_EXPORT_H0")
    check("GDT678" in split_pipe(new_span["source_gdts"]), "NEW_SPAN_GDT678_SOURCE")

    directives_by_position = {row["source_position_id"]: row for row in one_shot_directives}
    check(set(directives_by_position) == {"P288", "P289"}, "ONE_SHOT_EXACT_SOURCE_POSITIONS")
    check(len({row["render_unit_id"] for row in one_shot_directives}) == 1, "ONE_SHOT_ONE_RENDER_UNIT")
    check(len({(row["page"], row["locus"], row["bound_span_id"]) for row in one_shot_directives}) == 1, "ONE_SHOT_ONE_LOCUS_SPAN")
    expected_directives = {
        "P288": ("2", "keo", "keo#1", "LEFT", "EMIT_SPAN_ONCE", "heiße Portion"),
        "P289": ("3", "r", "r#1", "RIGHT", "CONSUME_NO_OUTPUT", ""),
    }
    context_by_position = {row["position_id"]: row for row in context}
    for position_id, expected in expected_directives.items():
        directive = directives_by_position[position_id]
        check(
            (
                directive["source_token_ordinal"], directive["source_surface"],
                directive["source_reading_id"], directive["span_role"],
                directive["render_action"], directive["emitted_text_de"],
            ) == expected,
            f"ONE_SHOT_DIRECTIVE:{position_id}",
        )
        check(directive["page"] == "f7r" and directive["locus"] == "f7r.2", f"ONE_SHOT_LOCUS:{position_id}")
        check(directive["anchor_position_id"] == "P288", f"ONE_SHOT_ANCHOR:{position_id}")
        check(directive["source_context_consumed"] == "1", f"ONE_SHOT_CONTEXT_CONSUMED:{position_id}")
        check(directive["global_export_allowed"] == "0", f"ONE_SHOT_NO_EXPORT:{position_id}")
        source = context_by_position[position_id]
        check(
            directive["source_token_ordinal"] == source["token_ordinal"]
            and directive["source_surface"] == source["surface"]
            and directive["source_reading_id"] == source["source_reading_id"]
            and directive["bound_span_id"] == source["v87_occurrence_bound_span_id"]
            and directive["span_role"] == source["v87_occurrence_bound_span_role"],
            f"ONE_SHOT_CONTEXT_JOIN:{position_id}",
        )
    check(int(directives_by_position["P289"]["source_token_ordinal"]) == int(directives_by_position["P288"]["source_token_ordinal"]) + 1, "ONE_SHOT_ADJACENT_SOURCE_ORDINALS")

    f7r2_source = sorted(
        (row for row in context if row["locus"] == "f7r.2"),
        key=lambda row: int(row["token_ordinal"]),
    )
    check(len(f7r2_source) == 9, "F7R2_NINE_SOURCE_POSITIONS")
    check([int(row["output_ordinal"]) for row in f7r2_rendered] == list(range(1, 9)), "F7R2_EIGHT_ORDERED_OUTPUT_UNITS")
    check(all(row["page"] == "f7r" and row["locus"] == "f7r.2" for row in f7r2_rendered), "F7R2_RENDER_LOCUS")
    span_outputs = [row for row in f7r2_rendered if row["source_kind"] == "BOUND_SPAN"]
    normal_outputs = [row for row in f7r2_rendered if row["source_kind"] == "CONTEXT_POSITION"]
    check(len(span_outputs) == 1 and len(normal_outputs) == 7, "F7R2_ONE_SPAN_SEVEN_NORMAL_OUTPUTS")
    span_output = span_outputs[0]
    check(
        span_output["source_ref"] == "G678_KEO_R_F7R2"
        and span_output["anchor_position_id"] == "P288"
        and span_output["consumed_position_ids"] == "P288|P289"
        and span_output["source_surfaces"] == "keo|r"
        and span_output["rendered_text_de"] == "heiße Portion",
        "F7R2_SPAN_OUTPUT_EXACT",
    )
    check({row["source_ref"] for row in normal_outputs} == {"P287", "P290", "P291", "P292", "P293", "P294", "P295"}, "F7R2_NORMAL_OUTPUT_POSITION_SET")
    rendered_texts = [row["rendered_text_de"] for row in f7r2_rendered]
    rendered_line = " · ".join(rendered_texts)
    check(rendered_texts.count("heiße Portion") == 1, "F7R2_EMITS_HOT_PORTION_ONCE")
    check("Wurzel" not in rendered_line, "F7R2_SUPPRESSES_ROOT")
    check("Heißansatz auf Mittelstufe" not in rendered_line, "F7R2_SUPPRESSES_OLD_KEO_CONTEXT")
    check("heiße Zubereitung auf Mittelstufe" not in rendered_line, "F7R2_SUPPRESSES_CURRENT_KEO_CONTEXT")
    check(f7r2_rendered[0]["source_ref"] == "P287" and f7r2_rendered[1]["source_ref"] == "G678_KEO_R_F7R2" and f7r2_rendered[2]["source_ref"] == "P290", "F7R2_SPAN_ORDER")
    check(result["f7r2_rendered_line_de"] == rendered_line, "RESULT_F7R2_RENDERED_LINE_EXACT")

    retired_nouns = re.compile(r"(?:Arznei\w*|Drogen?\w*|Dosis\w*|Charge\w*)", re.IGNORECASE)
    structural_literals = re.compile(r"(?:Kopf offen|EXACT_|BOUND_|MATERIAL_IDENTITY|PATIENT)", re.IGNORECASE)
    for spec in specs:
        for field in ("v87_lexical_core_de", "v87_context_realization_de"):
            value = spec[field]
            check(not retired_nouns.search(value), f"NO_RETIRED_NOUN:{spec['source_reading_id']}:{field}")
            check(not structural_literals.search(value), f"NO_STRUCTURAL_LITERAL_IN_GERMAN:{spec['source_reading_id']}:{field}")
        check(bool(spec["evidence_de"] and spec["counterevidence_de"] and spec["open_semantic_slots"]), f"SPEC_EVIDENCE_COMPLETE:{spec['source_reading_id']}")
    check(int(target_by_id["dshees#1"]["score_delta_lexical_core"]) == 0, "DSHEES_EXPLORATORY_ZERO_GAIN")
    check(target_by_id["cholkain#1"]["working_model_score_0_100_not_probability"] == "39", "CHOLKAIN_NO_PROMOTION")
    check(target_by_id["kc#1"]["working_model_score_0_100_not_probability"] == "39", "KC_NO_PROMOTION")
    for source_id in ("keo#1", "oteor#1", "oty#1"):
        check(int(target_by_id[source_id]["score_delta_lexical_core"]) == 0, f"PROSE_REPAIR_ZERO_GAIN:{source_id}")
    check(
        target_by_id["os#1"]["score_delta_lexical_core"] == "3"
        and target_by_id["os#1"]["working_model_score_0_100_not_probability"] == "16"
        and target_by_id["os#1"]["working_model_level"] == "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY",
        "OS_ONLY_F_O_BONUS_REMAINS_W0",
    )

    check(len({(row["surface"], row["reading_id"]) for row in complete}) == 1586, "COMPLETE_READING_KEYS_UNIQUE")
    check(len({row["surface"] for row in complete}) == 1582, "COMPLETE_1582_SURFACES")
    expected_complete_levels = Counter({
        "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY": 287,
        "W1_WEAK_WORKING": 315,
        "W2_PROVISIONAL_WORKING": 541,
        "W3_SOLID_WORKING_THEORY": 443,
    })
    check(Counter(row["working_model_level"] for row in complete) == expected_complete_levels, "COMPLETE_LEVEL_DISTRIBUTION")
    for row in complete:
        reading_key = f"{row['surface']}:{row['reading_id']}"
        check(row["working_model_score_0_100_not_probability"].isdigit(), f"COMPLETE_SCORE_PRESENT:{reading_key}")
        check(row["working_model_level"] == level(int(row["working_model_score_0_100_not_probability"])), f"COMPLETE_SCORE_LEVEL:{reading_key}")
        check(bool(row["positive_evidence_de"]), f"COMPLETE_POSITIVE_EVIDENCE:{reading_key}")
        check(bool(row["counterevidence_de"]), f"COMPLETE_COUNTEREVIDENCE:{reading_key}")
        check(row["historical_confirmation"] == HISTORICAL, f"COMPLETE_H0:{reading_key}")
    complete_active = [row for row in complete if row["current_layer"] == "ACTIVE_V87_LEXICAL_CORE"]
    check(len(complete_active) == 324, "COMPLETE_324_ACTIVE")
    complete_by_sources = lexical_source_map(complete_active)
    for source_id, lexical_row in target_by_id.items():
        complete_row = complete_by_sources[source_id]
        check(complete_row["working_meaning_de"] == lexical_row["v87_lexical_core_de"], f"COMPLETE_ACTIVE_CORE:{source_id}")
        check(complete_row["working_model_score_0_100_not_probability"] == lexical_row["working_model_score_0_100_not_probability"], f"COMPLETE_ACTIVE_SCORE:{source_id}")
        check(complete_row["positive_evidence_de"] == lexical_row["positive_evidence_de"], f"COMPLETE_ACTIVE_EVIDENCE:{source_id}")

    for row in context:
        check(not row["page"].startswith("f84") and not row["locus"].startswith("f84"), f"NO_F84_CONTEXT_SELECTOR:{row['position_id']}")
    for row in delta:
        check(all(not page.startswith("f84") for page in split_pipe(row["pages"])), f"NO_F84_DELTA_PAGE:{row['source_reading_id']}")
    for row in spans:
        check(not row["page"].startswith("f84") and not row["locus"].startswith("f84"), f"NO_F84_SPAN_SELECTOR:{row['bound_span_id']}")
    report_text = REPORT.read_text(encoding="utf-8")
    check("Ansatz auf mittlerer Heizstufe · Wurzel" not in report_text, "REPORT_RETIRES_BAD_RENDER")
    check("keo + P289 r  ->  heiße Portion" in report_text, "REPORT_SHOWS_NEW_RENDER")

    validation = {
        "experiment_id": "GDT714",
        "status": "PASS",
        "checks": len(checks),
        "deterministic_outputs": len(GENERATED),
        "audited_readings": 18,
        "audited_positions": 18,
        "audited_pages": 12,
        "revised_readings": 18,
        "held_readings": 0,
        "boundary_spans_added": 1,
        "boundary_positions_touched": 2,
        "primary_evidence_bindings": 18,
        "one_shot_directives": 2,
        "f7r2_rendered_units": 8,
        "remaining_unreviewed_weak_readings": 91,
        "active_lexical_readings": 324,
        "active_positions": 479,
        "complete_readings": 1586,
        "complete_surfaces": 1582,
        "w3_preserved_readings": w3_rows,
        "w3_preserved_positions": w3_positions,
        "historical_confirmation": HISTORICAL,
        "relation_word_credit_gdt714": 0,
        "new_pages": 0,
        "new_images": 0,
        "new_transcription": 0,
        "f84_or_f84r_used": 0,
        "output_sha256": {path.name: digest(path) for path in GENERATED},
    }
    VALIDATION.write_text(
        json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
