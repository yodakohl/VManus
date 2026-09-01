#!/usr/bin/env python3
"""Independent validator for the GDT712 V85 dictionary repair."""

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
EXP = ROOT / "experiments/yolo/gdt712_v85_al_state_core_context_repair"
SRC = EXP / "src"
ART = EXP / "artifacts"
G711 = ROOT / "experiments/yolo/gdt711_v84_active_weak_family_repair/artifacts"

SOURCE_LEXICAL = G711 / "V84_324_ACTIVE_LEXICAL_READINGS.tsv"
SOURCE_CONTEXT = G711 / "V84_479_CONTEXT_REALIZATIONS.tsv"
SOURCE_COMPLETE = G711 / "V84_COMPLETE_WORD_CONFIDENCE.tsv"
SOURCE_CENSUS = G711 / "V84_181_WEAK_READING_REPAIR_CENSUS.tsv"
SOURCE_FAMILIES = G711 / "V84_13_STEM_FAMILY_EVIDENCE.tsv"
SPECS = SRC / "V85_33_AUDIT_SPECS.tsv"

LEXICAL = ART / "V85_324_ACTIVE_LEXICAL_READINGS.tsv"
CONTEXT = ART / "V85_479_CONTEXT_REALIZATIONS.tsv"
CENSUS = ART / "V85_151_HELD_READING_AUDIT.tsv"
DELTA = ART / "V85_33_AL_STATE_CORE_CONTEXT_DELTA.tsv"
FAMILIES = ART / "V85_7_FAMILY_EVIDENCE.tsv"
SPANS = ART / "V85_1_BOUND_SPAN_RENDERER.tsv"
COMPLETE = ART / "V85_COMPLETE_WORD_CONFIDENCE.tsv"
RESULT = ART / "RESULT.json"
REPORT = EXP / "REPORT.md"
VALIDATION = ART / "VALIDATION.json"

GENERATED = [LEXICAL, CONTEXT, CENSUS, DELTA, FAMILIES, SPANS, COMPLETE, RESULT, REPORT]
HISTORICAL = "H0_NONE"
EXPECTED_STATUS = (
    "PASS_V85_33_AL_STATE_READINGS_AUDITED__30_REVISED_3_HELD__"
    "38_POSITIONS_23_PAGES__8_W0_149_W1_148_W2_19_W3__"
    "CHEOP_OL_LEFT_RIGHT_BOUND__ALL_H0_NONE"
)
EXPECTED_TARGETS = {
    "al#1", "alched#1", "chal#1", "daiidal#1", "dalam#1", "dchal#1",
    "kal#1", "oldal#1", "otal#1", "qoal#1", "qokal#1", "shal#1",
    "shdal#1", "shedal#1", "tal#1", "cheol#1", "cheop#1", "ches#1",
    "cholches#1", "dolkain#1", "kchey#1", "keeaiin#1", "keeey#1",
    "okol#1", "qokchy#1", "qokeeey#1", "qotaiin#1", "sheeey#1",
    "sheey#1", "shkeol#1", "shy#1", "tshey#1", "tshol#1",
}
EXPECTED_HOLDS = {"keeey#1", "okol#1", "qokeeey#1"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_pipe(value: str) -> list[str]:
    return [part.strip() for part in value.split("|") if part.strip() and part.strip() not in {"NONE", "0"}]


def v85_key(value: str) -> str:
    return value.replace("v84", "v85").replace("V84", "V85")


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

    for path in [SOURCE_LEXICAL, SOURCE_CONTEXT, SOURCE_COMPLETE, SOURCE_CENSUS, SOURCE_FAMILIES, SPECS, *GENERATED]:
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
        "source_complete": (len(source_complete), 1586), "source_census": (len(source_census), 181),
        "source_families": (len(source_families), 13), "specs": (len(specs), 33),
        "lexical": (len(lexical), 324), "context": (len(context), 479),
        "census": (len(census), 151), "delta": (len(delta), 33),
        "families": (len(families), 7), "spans": (len(spans), 1),
        "complete": (len(complete), 1586),
    }
    for label, (actual, expected) in expected_counts.items():
        check(actual == expected, f"COUNT:{label}:{expected}")

    check(result["status"] == EXPECTED_STATUS, "RESULT_STATUS")
    check(result["f84_or_f84r_used"] == 0 and result["new_pages"] == 0, "RESULT_NO_NEW_OR_SEALED_PAGE")
    check(result["relation_word_credit_gdt712"] == 0, "RESULT_ZERO_RELATION_WORD_CREDIT")
    check(result["revised_readings"] == 30 and result["held_readings"] == 3, "RESULT_DECISION_COUNTS")
    check(result["revised_positions"] == 34 and result["held_positions"] == 4, "RESULT_POSITION_PARTITION")

    specs_by_id = {row["source_reading_id"]: row for row in specs}
    check(set(specs_by_id) == EXPECTED_TARGETS, "EXACT_33_TARGET_IDS")
    check({row["source_reading_id"] for row in specs if row["decision"] == "HOLD"} == EXPECTED_HOLDS, "EXACT_3_HOLD_IDS")
    check(Counter(row["decision"] for row in specs) == Counter({"REVISE": 30, "HOLD": 3}), "SPEC_DECISION_COUNTS")
    check(all(row["component_global_export_allowed"] == "0" for row in specs), "SPEC_ZERO_COMPONENT_EXPORT")

    source_by_id = lexical_source_map(source_lexical)
    target_by_id = lexical_source_map(lexical)
    check(len(source_by_id) == len(target_by_id) == 332, "LEXICAL_SOURCE_MAP_332")
    check(set(source_by_id) == set(target_by_id), "LEXICAL_SOURCE_MAP_PARITY")
    check(len({row["v85_reading_id"] for row in lexical}) == 324, "V85_READING_IDS_UNIQUE")

    source_fields = list(source_lexical[0])
    w3_rows = 0
    w3_positions = 0
    for source_id, source in source_by_id.items():
        target = target_by_id[source_id]
        if source_id not in EXPECTED_TARGETS:
            for field in source_fields:
                check(target[v85_key(field)] == source[field], f"NON_TARGET_LEXICAL_PARITY:{source_id}:{field}")
            check(target["v85_audit_decision"] == "NOT_IN_GDT712_TRANCHE", f"NON_TARGET_DECISION:{source_id}")
        else:
            spec = specs_by_id[source_id]
            check(source["v84_lexical_core_de"] == spec["old_lexical_core_de"], f"SPEC_OLD_CORE:{source_id}")
            check(target["v85_lexical_core_de"] == spec["v85_lexical_core_de"], f"SPEC_NEW_CORE:{source_id}")
            check(target["v85_context_realizations_de"] == spec["v85_context_realization_de"], f"SPEC_CONTEXT:{source_id}")
            check(target["v85_audit_decision"] == spec["decision"], f"SPEC_DECISION:{source_id}")
            check(target["v85_evidence_class"] == spec["evidence_class"], f"SPEC_EVIDENCE_CLASS:{source_id}")
            check(target["v85_open_semantic_slots"] == spec["open_semantic_slots"], f"SPEC_OPEN_SLOTS:{source_id}")
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
            check(target["v85_component_global_export_allowed"] == "0", f"SPEC_COMPONENT_NO_EXPORT:{source_id}")
            if spec["decision"] == "HOLD":
                check(target["v85_lexical_core_de"] == source["v84_lexical_core_de"], f"HOLD_CORE_EXACT:{source_id}")
                check(expected_score == base, f"HOLD_SCORE_EXACT:{source_id}")
            else:
                check(target["v85_lexical_core_de"] != source["v84_lexical_core_de"], f"REVISE_CORE_CHANGED:{source_id}")
            if int(spec["score_delta_lexical_core"]) > 0:
                check(spec["resolved_debt_atom"] != "NONE" or spec["evidence_class"] == "ATLAS_FAMILY_INTERSECTION", f"POSITIVE_DELTA_NAMED_BASIS:{source_id}")
            if source_id == "cheop#1":
                check(target["semantic_scope"] == "BOUND_SPAN_LOCAL_READING", "CHEOP_LEXICAL_SCOPE")
                check(target["semantic_applicability"] == "COMPOUND_ONLY_LOCAL_READING", "CHEOP_LEXICAL_APPLICABILITY")
                check(target["global_export_scope"] == "BOUND_SPAN_ONLY_NO_GLOBAL_EXPORT", "CHEOP_LEXICAL_EXPORT")
                check(target["bound_span_ids"] == "G683_CHEOP_OL", "CHEOP_LEXICAL_SPAN")
                check(target["unconditional_global_export_allowed"] == "0", "CHEOP_LEXICAL_NO_GLOBAL")
            else:
                for field in ["semantic_scope", "semantic_applicability", "global_export_scope", "bound_span_ids", "unconditional_global_export_allowed"]:
                    check(target[field] == source[field], f"TARGET_SCOPE_PRESERVED:{source_id}:{field}")
        if source["working_model_level"] == "W3_SOLID_WORKING_THEORY":
            w3_rows += 1
            w3_positions += int(source["occurrence_count"])
    check(w3_rows == 19 and w3_positions == 77, "NINETEEN_W3_SEVENTY_SEVEN_POSITIONS_PRESERVED")

    expected_active_levels = Counter({
        "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY": 8, "W1_WEAK_WORKING": 149,
        "W2_PROVISIONAL_WORKING": 148, "W3_SOLID_WORKING_THEORY": 19,
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
    base_context_fields = [field for field in source_context[0] if "v84" not in field.lower()]
    target_position_rows: list[dict[str, str]] = []
    for key, source in source_context_by_key.items():
        target = target_context_by_key[key]
        for field in base_context_fields:
            check(target[field] == source[field], f"CONTEXT_SOURCE_PARITY:{key}:{field}")
        source_id = source["source_reading_id"]
        lexical_target = target_by_id[source_id]
        check(target["v85_reading_id"] == lexical_target["v85_reading_id"], f"CONTEXT_LEXICAL_LINK:{key}")
        check(target["v85_lexical_core_de"] == lexical_target["v85_lexical_core_de"], f"CONTEXT_CORE:{key}")
        check(target["v85_semantic_scope"] == lexical_target["semantic_scope"], f"CONTEXT_SCOPE:{key}")
        check(target["v85_semantic_applicability"] == lexical_target["semantic_applicability"], f"CONTEXT_APPLICABILITY:{key}")
        check(target["v85_historical_confirmation"] == HISTORICAL, f"CONTEXT_H0:{key}")
        if source_id in EXPECTED_TARGETS:
            target_position_rows.append(target)
            spec = specs_by_id[source_id]
            check(target["v85_context_realization_de"] == spec["v85_context_realization_de"], f"CONTEXT_SPEC_RENDER:{key}")
            check(target["v85_audit_decision"] == spec["decision"], f"CONTEXT_SPEC_DECISION:{key}")
            check(target["v68_action_license"] == "NOT_ACTION_LICENSED", f"TARGET_NOMINAL_LICENSE:{key}")
            check(target["v68_active_verb_occurrences"] == "0", f"TARGET_ZERO_ACTIVE_VERBS:{key}")
            check(target["v57_identity_signals"] == "NONE", f"TARGET_ZERO_IDENTITY:{key}")
        else:
            for field in source_context[0]:
                if "v84" in field.lower():
                    check(target[v85_key(field)] == source[field], f"NON_TARGET_CONTEXT_PARITY:{key}:{field}")
    check(len(target_position_rows) == 38, "TARGET_38_POSITIONS")
    check(len({row["page"] for row in target_position_rows}) == 23, "TARGET_23_PAGES")
    check(Counter(row["v85_occurrence_bound_span_id"] for row in context) == Counter({
        "NONE": 471, "B001": 2, "B002": 2, "B003": 2, "G683_CHEOP_OL": 2,
    }), "BOUND_SPAN_POSITION_DISTRIBUTION")
    check(sum(row["v85_occurrence_bound_span_global_export_allowed"] == "0" for row in context) == 8, "EIGHT_BOUND_POSITION_EXPORT_STOPS")
    cheop = target_context_by_key[("f115r", "f115r.1", 5, "cheop")]
    ol_bound = target_context_by_key[("f115r", "f115r.1", 6, "ol")]
    check((cheop["v85_occurrence_bound_span_id"], cheop["v85_occurrence_bound_span_role"]) == ("G683_CHEOP_OL", "LEFT"), "CHEOP_LEFT")
    check((ol_bound["v85_occurrence_bound_span_id"], ol_bound["v85_occurrence_bound_span_role"]) == ("G683_CHEOP_OL", "RIGHT"), "OL2_RIGHT")
    check(cheop["v85_occurrence_bound_span_global_export_allowed"] == ol_bound["v85_occurrence_bound_span_global_export_allowed"] == "0", "CHEOP_OL_NO_EXPORT")

    source_held_ids = {row["source_reading_id"] for row in source_census if row["disposition"] == "HELD_FOR_LATER_REPAIR"}
    check(len(source_held_ids) == 151, "SOURCE_151_HELD")
    check({row["source_reading_id"] for row in census} == source_held_ids, "CENSUS_SOURCE_SET_PARITY")
    check(Counter(row["disposition"] for row in census) == Counter({
        "REVISED_IN_V85": 30, "AUDITED_HOLD_IN_V85": 3, "HELD_FOR_LATER_REPAIR": 118,
    }), "CENSUS_DISPOSITION_PARTITION")
    check({row["source_reading_id"] for row in delta} == EXPECTED_TARGETS, "DELTA_EXACT_TARGET_SET")
    for row in delta:
        spec = specs_by_id[row["source_reading_id"]]
        check(row["decision"] == spec["decision"], f"DELTA_DECISION:{row['source_reading_id']}")
        check(row["v85_lexical_core_de"] == spec["v85_lexical_core_de"], f"DELTA_CORE:{row['source_reading_id']}")
        check(row["evidence_de"] == spec["evidence_de"], f"DELTA_EVIDENCE:{row['source_reading_id']}")
        check(row["counterevidence_de"] == spec["counterevidence_de"], f"DELTA_COUNTER:{row['source_reading_id']}")
        check(row["historical_confirmation"] == HISTORICAL, f"DELTA_H0:{row['source_reading_id']}")

    expected_family_ids = {"F_AL", "F_STATE", "F_STAGE", "F_O", "F_N", "F_OL", "F_REF"}
    check({row["family_id"] for row in families} == expected_family_ids, "EXACT_7_FAMILIES")
    for row in families:
        check(row["historical_confirmation"] == HISTORICAL, f"FAMILY_H0:{row['family_id']}")
        check(row["automatic_historical_credit"] == "0", f"FAMILY_ZERO_HISTORICAL_CREDIT:{row['family_id']}")
    family_needles = {
        "F_AL": ("AL",), "F_STATE": ("CH", "SH", "K", "T"),
        "F_STAGE": ("+Y", "+E+Y", "+EE+Y"), "F_O": ("O",),
        "F_N": ("AIN", "AIIN"), "F_OL": ("OL",), "F_REF": ("QO", "QOK"),
    }
    for spec in specs:
        for family in split_pipe(spec["family_ids"]):
            check(any(needle in spec["decomposition"] for needle in family_needles[family]), f"FAMILY_VISIBLE_IN_DECOMPOSITION:{spec['source_reading_id']}:{family}")

    span = spans[0]
    check(span["bound_span_id"] == "G683_CHEOP_OL", "SPAN_ID")
    check(span["left_position_id"] == "P167" and span["right_position_id"] == "P168", "SPAN_POSITIONS")
    check(span["left_role"] == "LEFT" and span["right_role"] == "RIGHT", "SPAN_ROLES")
    check(span["render_once_de"] == "bis zur Mittelstufe getrockneter Pulverstoff", "SPAN_RENDER_ONCE")
    check(span["global_export_allowed"] == "0" and span["historical_confirmation"] == HISTORICAL, "SPAN_NO_EXPORT_H0")

    check(len({(row["surface"], row["reading_id"]) for row in complete}) == 1586, "COMPLETE_READING_KEYS_UNIQUE")
    check(len({row["surface"] for row in complete}) == 1582, "COMPLETE_1582_SURFACES")
    expected_complete_levels = Counter({
        "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY": 288, "W1_WEAK_WORKING": 329,
        "W2_PROVISIONAL_WORKING": 526, "W3_SOLID_WORKING_THEORY": 443,
    })
    check(Counter(row["working_model_level"] for row in complete) == expected_complete_levels, "COMPLETE_LEVEL_DISTRIBUTION")
    for row in complete:
        reading_key = f"{row['surface']}:{row['reading_id']}"
        check(row["working_model_score_0_100_not_probability"].isdigit(), f"COMPLETE_SCORE_PRESENT:{reading_key}")
        check(row["working_model_level"] == level(int(row["working_model_score_0_100_not_probability"])), f"COMPLETE_SCORE_LEVEL:{reading_key}")
        check(bool(row["positive_evidence_de"]), f"COMPLETE_POSITIVE_EVIDENCE:{reading_key}")
        check(bool(row["counterevidence_de"]), f"COMPLETE_COUNTEREVIDENCE:{reading_key}")
        check(row["historical_confirmation"] == HISTORICAL, f"COMPLETE_H0:{reading_key}")
    complete_active = [row for row in complete if row["current_layer"] == "ACTIVE_V85_LEXICAL_CORE"]
    check(len(complete_active) == 324, "COMPLETE_324_ACTIVE")
    complete_by_sources = lexical_source_map(complete_active)
    for source_id, lexical_row in target_by_id.items():
        complete_row = complete_by_sources[source_id]
        check(complete_row["working_meaning_de"] == lexical_row["v85_lexical_core_de"], f"COMPLETE_ACTIVE_CORE:{source_id}")
        check(complete_row["working_model_score_0_100_not_probability"] == lexical_row["working_model_score_0_100_not_probability"], f"COMPLETE_ACTIVE_SCORE:{source_id}")
        check(complete_row["positive_evidence_de"] == lexical_row["positive_evidence_de"], f"COMPLETE_ACTIVE_EVIDENCE:{source_id}")

    forbidden_translation_literals = re.compile(r"\b(?:Kopf offen|EXACT|BOUND|QO_ROLE|MATERIAL_IDENTITY|PATIENT)\b", re.IGNORECASE)
    forbidden_revised_nouns = re.compile(r"\b(?:Rohstoffklasse|Rohdroge|Drogenrohstoff|Drogenstoff|Drogenmaterial|Dosis|Gut)\b", re.IGNORECASE)
    for spec in specs:
        for field in ("v85_lexical_core_de", "v85_context_realization_de"):
            value = spec[field]
            check(not forbidden_translation_literals.search(value), f"NO_STRUCTURAL_LITERAL_IN_GERMAN:{spec['source_reading_id']}:{field}")
            if spec["decision"] == "REVISE":
                check(not forbidden_revised_nouns.search(value), f"NO_RETIRED_NOUN_IN_REVISED_GERMAN:{spec['source_reading_id']}:{field}")
        check(bool(spec["evidence_de"] and spec["counterevidence_de"]), f"SPEC_EVIDENCE_COMPLETE:{spec['source_reading_id']}")

    for row in context:
        check(not row["page"].startswith("f84") and not row["locus"].startswith("f84"), f"NO_F84_CONTEXT_SELECTOR:{row['position_id']}")
    for row in delta:
        check(all(not page.startswith("f84") for page in split_pipe(row["pages"])), f"NO_F84_DELTA_PAGE:{row['source_reading_id']}")
    for row in spans:
        check(not row["page"].startswith("f84") and not row["locus"].startswith("f84"), "NO_F84_SPAN_SELECTOR")

    validation = {
        "experiment_id": "GDT712",
        "status": "PASS",
        "checks": len(checks),
        "deterministic_outputs": len(GENERATED),
        "audited_readings": 33,
        "audited_positions": 38,
        "audited_pages": 23,
        "revised_readings": 30,
        "held_readings": 3,
        "active_lexical_readings": 324,
        "active_positions": 479,
        "complete_readings": 1586,
        "complete_surfaces": 1582,
        "w3_preserved_readings": w3_rows,
        "w3_preserved_positions": w3_positions,
        "historical_confirmation": HISTORICAL,
        "relation_word_credit_gdt712": 0,
        "new_pages": 0,
        "f84_or_f84r_used": 0,
        "output_sha256": {path.name: digest(path) for path in GENERATED},
    }
    VALIDATION.write_text(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
