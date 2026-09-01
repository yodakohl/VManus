#!/usr/bin/env python3
"""Independent parity, evidence, confidence, and renderer checks for GDT715."""

from __future__ import annotations

import csv
import hashlib
import json
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
EXP = ROOT / "experiments/yolo/gdt715_v88_axis_action_patient_core_context_repair"
SRC = EXP / "src"
ART = EXP / "artifacts"
G714 = ROOT / "experiments/yolo/gdt714_v87_bound_c1_core_context_repair/artifacts"
G711 = ROOT / "experiments/yolo/gdt711_v84_active_weak_family_repair/artifacts"

SOURCE_LEXICAL = G714 / "V87_324_ACTIVE_LEXICAL_READINGS.tsv"
SOURCE_CONTEXT = G714 / "V87_479_CONTEXT_REALIZATIONS.tsv"
SOURCE_COMPLETE = G714 / "V87_COMPLETE_WORD_CONFIDENCE.tsv"
SOURCE_CENSUS = G714 / "V87_109_HELD_READING_AUDIT.tsv"
SOURCE_SPANS = G714 / "V87_2_BOUND_SPAN_RENDERER.tsv"
SOURCE_FAMILIES = G711 / "V84_13_STEM_FAMILY_EVIDENCE.tsv"
SPECS = SRC / "V88_7_AUDIT_SPECS.tsv"
BINDINGS = SRC / "V88_19_PRIMARY_EVIDENCE_BINDINGS.tsv"

TARGET_LEXICAL = ART / "V88_324_ACTIVE_LEXICAL_READINGS.tsv"
TARGET_CONTEXT = ART / "V88_479_CONTEXT_REALIZATIONS.tsv"
TARGET_CENSUS = ART / "V88_91_HELD_READING_AUDIT.tsv"
TARGET_DELTA = ART / "V88_7_AXIS_ACTION_CORE_CONTEXT_DELTA.tsv"
TARGET_EVIDENCE = ART / "V88_19_PRIMARY_EVIDENCE_BINDINGS.tsv"
TARGET_FAMILIES = ART / "V88_2_FAMILY_EVIDENCE.tsv"
TARGET_SPANS = ART / "V88_2_BOUND_SPAN_RENDERER.tsv"
TARGET_DIRECTIVES = ART / "V88_2_ONE_SHOT_RENDER_DIRECTIVES.tsv"
TARGET_RENDER = ART / "V88_8_F7R2_RENDERED_UNITS.tsv"
TARGET_COMPLETE = ART / "V88_COMPLETE_WORD_CONFIDENCE.tsv"
RESULT = ART / "RESULT.json"
REPORT = EXP / "REPORT.md"

STATUS = (
    "PASS_V88_7_AXIS_ACTION_READINGS_REVISED__2_VALUE_CORES_5_ACTION_CORES__"
    "7_TARGET_POSITIONS_7_PAGES__84_WEAK_READINGS_REMAIN__"
    "F7R2_RERENDERED__ALL_H0_NONE"
)
HISTORICAL = "H0_NONE"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def split_pipe(value: str) -> list[str]:
    return [part.strip() for part in value.split("|") if part.strip() and part.strip() not in {"NONE", "0"}]


def parse_assertions(value: str) -> dict[str, str]:
    output: dict[str, str] = {}
    for part in value.split(";"):
        if not part:
            continue
        field, expected = part.split("=", 1)
        assert field and field not in output
        output[field] = expected
    return output


def v88_key(value: str) -> str:
    return value.replace("v87", "v88").replace("V87", "V88")


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


class Audit:
    def __init__(self) -> None:
        self.checks = 0
        self.groups: Counter[str] = Counter()

    def check(self, condition: bool, message: str, group: str = "general") -> None:
        self.checks += 1
        self.groups[group] += 1
        if not condition:
            raise AssertionError(message)


def rows_by_source(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    output: dict[str, dict[str, str]] = {}
    for row in rows:
        for source_id in split_pipe(row["source_reading_ids"]):
            assert source_id not in output
            output[source_id] = row
    return output


def mapped_source_value(source: dict[str, str], target_field: str) -> str:
    reverse = target_field.replace("v88", "v87").replace("V88", "V87")
    return source[reverse]


def main() -> int:
    audit = Audit()
    source_lexical = read_tsv(SOURCE_LEXICAL)
    source_context = read_tsv(SOURCE_CONTEXT)
    source_complete = read_tsv(SOURCE_COMPLETE)
    source_census = read_tsv(SOURCE_CENSUS)
    source_spans = read_tsv(SOURCE_SPANS)
    source_families = read_tsv(SOURCE_FAMILIES)
    specs = read_tsv(SPECS)
    bindings = read_tsv(BINDINGS)
    lexical = read_tsv(TARGET_LEXICAL)
    contexts = read_tsv(TARGET_CONTEXT)
    census = read_tsv(TARGET_CENSUS)
    delta = read_tsv(TARGET_DELTA)
    evidence = read_tsv(TARGET_EVIDENCE)
    families = read_tsv(TARGET_FAMILIES)
    spans = read_tsv(TARGET_SPANS)
    directives = read_tsv(TARGET_DIRECTIVES)
    rendered = read_tsv(TARGET_RENDER)
    complete = read_tsv(TARGET_COMPLETE)
    result = json.loads(RESULT.read_text(encoding="utf-8"))

    expected_counts = {
        "source lexical": (len(source_lexical), 324),
        "source context": (len(source_context), 479),
        "source complete": (len(source_complete), 1586),
        "source census": (len(source_census), 109),
        "source spans": (len(source_spans), 2),
        "source families": (len(source_families), 13),
        "specs": (len(specs), 7),
        "bindings": (len(bindings), 19),
        "lexical": (len(lexical), 324),
        "contexts": (len(contexts), 479),
        "census": (len(census), 91),
        "delta": (len(delta), 7),
        "evidence": (len(evidence), 19),
        "families": (len(families), 2),
        "spans": (len(spans), 2),
        "directives": (len(directives), 2),
        "rendered": (len(rendered), 8),
        "complete": (len(complete), 1586),
    }
    for name, (actual, expected) in expected_counts.items():
        audit.check(actual == expected, f"{name}: {actual} != {expected}", "counts")

    spec_by_id = {row["source_reading_id"]: row for row in specs}
    target_ids = set(spec_by_id)
    audit.check(len(spec_by_id) == 7, "duplicate target spec", "spec")
    audit.check(all(row["decision"] == "REVISE" for row in specs), "non-revise target", "spec")
    audit.check(all(row["component_global_export_allowed"] == "0" for row in specs), "component export", "spec")
    audit.check({row["source_reading_id"] for row in delta} == target_ids, "delta target mismatch", "spec")
    audit.check({row["source_reading_id"] for row in bindings} == target_ids, "binding coverage mismatch", "spec")

    # Every evidence row must independently resolve to one exact source row.
    output_evidence_by_id = {row["binding_id"]: row for row in evidence}
    credits_by_source: dict[str, list[str]] = defaultdict(list)
    for binding in bindings:
        binding_id = binding["binding_id"]
        audit.check(binding_id in output_evidence_by_id, f"missing evidence {binding_id}", "evidence")
        audit.check("f84" not in binding["evidence_path"].lower(), f"sealed path {binding_id}", "sealed")
        selector = parse_assertions(binding["selector"])
        assertions = parse_assertions(binding["field_assertions"])
        audit.check(all(not value.lower().startswith("f84") for value in selector.values()), f"sealed selector {binding_id}", "sealed")
        rows = read_tsv(ROOT / binding["evidence_path"])
        matches = [row for row in rows if all(row.get(field) == expected for field, expected in selector.items())]
        audit.check(len(matches) == 1, f"{binding_id} matched {len(matches)} rows", "evidence")
        source = matches[0]
        for field, expected in assertions.items():
            audit.check(source.get(field) == expected, f"{binding_id}:{field}", "evidence_assertion")
        fingerprint = hashlib.sha256(
            json.dumps(source, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        actual = output_evidence_by_id[binding_id]
        for field, expected in binding.items():
            audit.check(actual[field] == expected, f"evidence copy {binding_id}:{field}", "evidence_copy")
        audit.check(actual["matched_row_fingerprint_sha256"] == fingerprint, f"fingerprint {binding_id}", "evidence")
        audit.check(actual["source_row_match"] == "1", f"source match {binding_id}", "evidence")
        audit.check(actual["evidence_status"] == "BOUND_EXACT_PRIMARY_ROW", f"status {binding_id}", "evidence")
        audit.check(actual["historical_confirmation"] == HISTORICAL, f"historical {binding_id}", "evidence")
        credits_by_source[binding["source_reading_id"]].extend(split_pipe(binding["score_credit_family_ids"]))

    bonus_by_family = {row["family_id"]: int(row["family_bonus"]) for row in source_families}
    source_lexical_by_id = rows_by_source(source_lexical)
    lexical_by_id = rows_by_source(lexical)
    audit.check(len(source_lexical_by_id) == 332 and len(lexical_by_id) == 332, "source-reading cardinality", "lexical")

    expected_scores: dict[str, int] = {}
    for source_id, spec in spec_by_id.items():
        source = source_lexical_by_id[source_id]
        target = lexical_by_id[source_id]
        credits = credits_by_source[source_id]
        audit.check(len(credits) == len(set(credits)), f"duplicate score credit {source_id}", "score")
        audit.check(set(credits) == set(split_pipe(spec["score_credit_family_ids"])), f"score family mismatch {source_id}", "score")
        derived_delta = sum(bonus_by_family[family] for family in credits)
        audit.check(derived_delta == int(spec["score_delta_lexical_core"]), f"score delta spec {source_id}", "score")
        expected_score = min(
            int(source["working_model_score_0_100_not_probability"]) + derived_delta,
            int(spec["lexical_core_cap"]),
        )
        expected_scores[source_id] = expected_score
        checks = {
            "surface": source["surface"],
            "v88_lexical_core_de": spec["v88_lexical_core_de"],
            "v88_context_realizations_de": spec["v88_context_realization_de"],
            "family_ids": spec["family_ids"],
            "decomposition": spec["decomposition"],
            "repair_modes": spec["repair_mode"],
            "resolved_debt_atoms": spec["resolved_debt_atom"],
            "last_semantic_writer": "GDT715",
            "base_score": source["working_model_score_0_100_not_probability"],
            "score_delta_lexical_core": str(derived_delta),
            "lexical_core_cap": spec["lexical_core_cap"],
            "working_model_score_0_100_not_probability": str(expected_score),
            "working_model_level": level(expected_score),
            "context_realization_cap": spec["context_realization_cap"],
            "context_realization_score_0_100_not_probability": str(min(expected_score, int(spec["context_realization_cap"]))),
            "v88_audit_decision": "REVISE",
            "v88_evidence_class": spec["evidence_class"],
            "v88_open_semantic_slots": spec["open_semantic_slots"],
            "v88_component_global_export_allowed": "0",
            "v88_prior_lexical_core_de": spec["old_lexical_core_de"],
            "historical_confirmation": HISTORICAL,
        }
        for field, expected in checks.items():
            audit.check(target[field] == expected, f"target lexical {source_id}:{field}", "target_lexical")
        audit.check("GDT715" in split_pipe(target["source_gdts"]), f"missing source GDT {source_id}", "target_lexical")
        audit.check(spec["evidence_de"] in target["positive_evidence_de"], f"missing positive evidence {source_id}", "target_lexical")
        audit.check(spec["counterevidence_de"] in target["counterevidence_de"], f"missing counterevidence {source_id}", "target_lexical")
        audit.check(target["semantic_scope"] == source["semantic_scope"], f"scope changed {source_id}", "scope")
        audit.check(target["semantic_applicability"] == source["semantic_applicability"], f"applicability changed {source_id}", "scope")
        audit.check(target["global_export_scope"] == source["global_export_scope"], f"export scope changed {source_id}", "scope")
        audit.check(target["bound_span_ids"] == source["bound_span_ids"], f"span scope changed {source_id}", "scope")
        audit.check(target["unconditional_global_export_allowed"] == source["unconditional_global_export_allowed"], f"whole export changed {source_id}", "scope")

    action_ids = {"dold#1", "qckhedy#1", "qey#1", "qochedain#1", "yky#1"}
    forbidden_patient_words = ("droge", "arznei", "material", " gut", "portion", "blüte", "pulver", "posten")
    for source_id in action_ids:
        core = lexical_by_id[source_id]["v88_lexical_core_de"].lower()
        audit.check(not any(term in core for term in forbidden_patient_words), f"patient leaked into {source_id}: {core}", "patient_boundary")
        audit.check(int(lexical_by_id[source_id]["score_delta_lexical_core"]) == 0, f"prose promotion {source_id}", "score")
    audit.check(lexical_by_id["aiiin#1"]["v88_lexical_core_de"] == "Wert IV", "aiiin core", "value_axis")
    audit.check(lexical_by_id["aiiin#1"]["v88_context_realizations_de"] == "Menge IV", "aiiin context", "value_axis")
    audit.check(lexical_by_id["ydaiin#1"]["v88_lexical_core_de"] == "Bezugswert III", "ydaiin core", "value_axis")
    audit.check("Maß" not in lexical_by_id["ydaiin#1"]["v88_lexical_core_de"], "ydaiin measure leak", "value_axis")

    # All 317 non-target lexical rows retain every inherited non-audit field.
    lexical_audit_fields = {
        "v88_audit_decision", "v88_evidence_class", "v88_open_semantic_slots",
        "v88_component_global_export_allowed", "v88_prior_lexical_core_de",
    }
    for source in source_lexical:
        source_ids = split_pipe(source["source_reading_ids"])
        target = lexical_by_id[source_ids[0]]
        if len(source_ids) == 1 and source_ids[0] in target_ids:
            continue
        for source_field in source:
            target_field = v88_key(source_field)
            if target_field in lexical_audit_fields:
                continue
            audit.check(target[target_field] == source[source_field], f"non-target lexical drift {source['surface']}:{target_field}", "lexical_parity")

    # Context positions: exact target locality plus non-target parity.
    source_context_by_position = {row["position_id"]: row for row in source_context}
    context_by_position = {row["position_id"]: row for row in contexts}
    audit.check(len(source_context_by_position) == 479 and len(context_by_position) == 479, "position uniqueness", "context")
    target_position_ids = {spec["expected_position_id"] for spec in specs}
    audit.check(len(target_position_ids) == 7, "target position duplication", "context")
    by_locus_ordinal = {(row["locus"], int(row["token_ordinal"])): row for row in source_context}
    for source_id, spec in spec_by_id.items():
        position = context_by_position[spec["expected_position_id"]]
        source = source_context_by_position[spec["expected_position_id"]]
        left = by_locus_ordinal[(spec["expected_locus"], int(spec["expected_token_ordinal"]) - 1)]
        expectations = {
            "source_reading_id": source_id,
            "surface": source["surface"],
            "page": spec["expected_page"],
            "locus": spec["expected_locus"],
            "token_ordinal": spec["expected_token_ordinal"],
            "v88_lexical_core_de": spec["v88_lexical_core_de"],
            "v88_context_realization_de": spec["v88_context_realization_de"],
            "v88_lexical_score": str(expected_scores[source_id]),
            "v88_lexical_level": level(expected_scores[source_id]),
            "v88_audit_decision": "REVISE",
            "v88_evidence_class": spec["evidence_class"],
            "v88_open_semantic_slots": spec["open_semantic_slots"],
            "v88_component_global_export_allowed": "0",
            "v88_local_context_hypothesis": spec["local_context_hypothesis"],
            "v88_expected_left_surface": spec["expected_left_surface"],
            "v88_historical_confirmation": HISTORICAL,
        }
        for field, expected in expectations.items():
            audit.check(position[field] == expected, f"target context {source_id}:{field}", "target_context")
        audit.check(left["surface"] == spec["expected_left_surface"], f"left context {source_id}", "target_context")

    context_audit_fields = {
        "v88_audit_decision", "v88_evidence_class", "v88_open_semantic_slots",
        "v88_component_global_export_allowed", "v88_local_context_hypothesis",
        "v88_expected_left_surface",
    }
    for source in source_context:
        if source["position_id"] in target_position_ids:
            continue
        target = context_by_position[source["position_id"]]
        for source_field in source:
            target_field = v88_key(source_field)
            if target_field in context_audit_fields:
                continue
            audit.check(target[target_field] == source[source_field], f"non-target context drift {source['position_id']}:{target_field}", "context_parity")

    # Held queue and family tables.
    audit.check(Counter(row["disposition"] for row in census) == Counter({"HELD_FOR_LATER_REPAIR": 84, "REVISED_IN_V88": 7}), "census dispositions", "census")
    audit.check({row["source_reading_id"] for row in census if row["disposition"] == "REVISED_IN_V88"} == target_ids, "census revised targets", "census")
    source_held_ids = {row["source_reading_id"] for row in source_census if row["disposition"] == "HELD_FOR_LATER_REPAIR"}
    audit.check({row["source_reading_id"] for row in census} == source_held_ids, "census source universe", "census")
    family_by_id = {row["family_id"]: row for row in families}
    audit.check(set(family_by_id) == {"F_N", "F_REF"}, "family set", "family")
    audit.check(family_by_id["F_N"]["selected_source_reading_ids"] == "aiiin#1|ydaiin#1", "F_N selections", "family")
    audit.check(family_by_id["F_REF"]["selected_source_reading_ids"] == "ydaiin#1", "F_REF selection", "family")
    audit.check(family_by_id["F_N"]["family_bonus"] == "3", "F_N bonus", "family")
    audit.check(family_by_id["F_REF"]["family_bonus"] == "0", "F_REF bonus", "family")

    # Bound spans are inherited byte-for-byte at the table level.
    audit.check(spans == source_spans, "bound span drift", "renderer")
    span = next(row for row in spans if row["bound_span_id"] == "G678_KEO_R_F7R2")
    audit.check(span["left_position_id"] == "P288" and span["right_position_id"] == "P289", "f7r2 span positions", "renderer")
    audit.check(span["render_once_de"] == "heiße Portion" and span["global_export_allowed"] == "0", "f7r2 span value/export", "renderer")
    directives_by_position = {row["source_position_id"]: row for row in directives}
    audit.check(set(directives_by_position) == {"P288", "P289"}, "directive positions", "renderer")
    audit.check(directives_by_position["P288"]["render_action"] == "EMIT_SPAN_ONCE", "left directive", "renderer")
    audit.check(directives_by_position["P288"]["emitted_text_de"] == "heiße Portion", "left emission", "renderer")
    audit.check(directives_by_position["P289"]["render_action"] == "CONSUME_NO_OUTPUT", "right directive", "renderer")
    audit.check(directives_by_position["P289"]["emitted_text_de"] == "", "right emits text", "renderer")
    audit.check(all(row["global_export_allowed"] == "0" for row in directives), "directive export", "renderer")

    expected_render: list[dict[str, str]] = []
    source_f7r2 = sorted((row for row in contexts if row["locus"] == "f7r.2"), key=lambda row: int(row["token_ordinal"]))
    for source in source_f7r2:
        directive = directives_by_position.get(source["position_id"])
        if directive and directive["render_action"] == "CONSUME_NO_OUTPUT":
            continue
        if directive:
            expected = {
                "source_kind": "BOUND_SPAN",
                "source_ref": span["bound_span_id"],
                "anchor_position_id": "P288",
                "consumed_position_ids": "P288|P289",
                "source_surfaces": "keo|r",
                "rendered_text_de": "heiße Portion",
            }
        else:
            expected = {
                "source_kind": "CONTEXT_POSITION",
                "source_ref": source["position_id"],
                "anchor_position_id": source["position_id"],
                "consumed_position_ids": source["position_id"],
                "source_surfaces": source["surface"],
                "rendered_text_de": source["v88_context_realization_de"],
            }
        expected_render.append(expected)
    audit.check(len(expected_render) == 8, "expected render units", "renderer")
    for ordinal, (expected, actual) in enumerate(zip(expected_render, rendered), start=1):
        audit.check(actual["output_ordinal"] == str(ordinal), f"render ordinal {ordinal}", "renderer")
        audit.check(actual["page"] == "f7r" and actual["locus"] == "f7r.2", f"render locus {ordinal}", "renderer")
        audit.check(actual["historical_confirmation"] == HISTORICAL, f"render historical {ordinal}", "renderer")
        for field, value in expected.items():
            audit.check(actual[field] == value, f"render {ordinal}:{field}", "renderer")
    render_text = " · ".join(row["rendered_text_de"] for row in rendered)
    audit.check("diese Blüte abmessen und abschließen" in render_text, "DOLD context absent", "renderer")
    audit.check("Drogenstoff" not in render_text and "Wurzel" not in render_text, "stale generic/span output", "renderer")

    # Complete dictionary: every row has confidence and both evidence channels.
    audit.check(len({(row["surface"], row["reading_id"]) for row in complete}) == 1586, "complete key uniqueness", "complete")
    audit.check(len({row["surface"] for row in complete}) == 1582, "complete surface count", "complete")
    for row in complete:
        audit.check(row["working_model_score_0_100_not_probability"].isdigit(), f"missing score {row['surface']}:{row['reading_id']}", "dictionary_evidence")
        score = int(row["working_model_score_0_100_not_probability"])
        audit.check(row["working_model_level"] == level(score), f"wrong level {row['surface']}:{row['reading_id']}", "dictionary_evidence")
        audit.check(bool(row["positive_evidence_de"].strip()), f"missing evidence {row['surface']}:{row['reading_id']}", "dictionary_evidence")
        audit.check(bool(row["counterevidence_de"].strip()), f"missing counterevidence {row['surface']}:{row['reading_id']}", "dictionary_evidence")
        audit.check(row["historical_confirmation"] == HISTORICAL, f"historical leak {row['surface']}:{row['reading_id']}", "dictionary_evidence")
    active_complete = [row for row in complete if row["current_layer"] == "ACTIVE_V88_LEXICAL_CORE"]
    audit.check(len(active_complete) == 324, "active complete count", "complete")
    active_complete_by_id = {row["reading_id"]: row for row in active_complete}
    for row in lexical:
        dictionary_row = active_complete_by_id[row["v88_reading_id"]]
        audit.check(dictionary_row["working_meaning_de"] == row["v88_lexical_core_de"], f"dictionary meaning {row['surface']}", "complete_parity")
        audit.check(dictionary_row["working_model_score_0_100_not_probability"] == row["working_model_score_0_100_not_probability"], f"dictionary score {row['surface']}", "complete_parity")
        audit.check(dictionary_row["positive_evidence_de"] == row["positive_evidence_de"], f"dictionary evidence {row['surface']}", "complete_parity")
        audit.check(dictionary_row["counterevidence_de"] == row["counterevidence_de"], f"dictionary counterevidence {row['surface']}", "complete_parity")

    active_levels = Counter(row["working_model_level"] for row in lexical)
    complete_levels = Counter(row["working_model_level"] for row in complete)
    audit.check(active_levels == Counter({
        "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY": 7,
        "W1_WEAK_WORKING": 135,
        "W2_PROVISIONAL_WORKING": 163,
        "W3_SOLID_WORKING_THEORY": 19,
    }), "active level distribution", "score")
    audit.check(complete_levels == Counter({
        "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY": 287,
        "W1_WEAK_WORKING": 315,
        "W2_PROVISIONAL_WORKING": 541,
        "W3_SOLID_WORKING_THEORY": 443,
    }), "complete level distribution", "score")

    # Compact result/report and sealed/private hygiene.
    result_expectations: dict[str, Any] = {
        "experiment_id": "GDT715",
        "status": STATUS,
        "audited_readings": 7,
        "audited_positions": 7,
        "audited_pages": 7,
        "value_cores_revised": 2,
        "action_cores_revised": 5,
        "primary_evidence_bindings": 19,
        "active_lexical_readings": 324,
        "active_positions": 479,
        "remaining_unreviewed_weak_readings": 84,
        "complete_readings": 1586,
        "complete_surfaces": 1582,
        "bound_span_renderers": 2,
        "one_shot_directives": 2,
        "f7r2_rendered_units": 8,
        "f7r2_rendered_line_de": render_text,
        "relation_word_credit_gdt715": 0,
        "historical_confirmation": HISTORICAL,
        "new_pages": 0,
        "new_images": 0,
        "new_transcription": 0,
        "f84_or_f84r_used": 0,
    }
    for field, expected in result_expectations.items():
        audit.check(result[field] == expected, f"result {field}", "result")
    audit.check(result["score_promotions"] == {"aiiin#1": 3, "ydaiin#1": 3}, "score promotions result", "result")
    report = REPORT.read_text(encoding="utf-8")
    for needle in ("`aiiin`", "`ydaiin`", "diese Blüte abmessen und abschließen", "84", STATUS):
        audit.check(needle in report, f"report missing {needle}", "report")

    output_files = [
        EXP / "README.md", EXP / "METHOD.md", EXP / "REPORT.md", EXP / "experiment.json",
        SRC / "run.py", SRC / "validate.py", SPECS, BINDINGS, ART / "README.md",
        TARGET_LEXICAL, TARGET_CONTEXT, TARGET_CENSUS, TARGET_DELTA, TARGET_EVIDENCE,
        TARGET_FAMILIES, TARGET_SPANS, TARGET_DIRECTIVES, TARGET_RENDER, TARGET_COMPLETE, RESULT,
    ]
    private_path_markers = ("/" + "home/", "/" + "Users/")
    for path in output_files:
        text = path.read_text(encoding="utf-8")
        audit.check(not any(marker in text for marker in private_path_markers), f"absolute private path in {path.name}", "privacy")
    for row in contexts:
        audit.check(not row["page"].startswith("f84") and not row["locus"].startswith("f84"), f"sealed context {row['position_id']}", "sealed")

    validation = {
        "experiment_id": "GDT715",
        "status": "PASS",
        "checks_passed": audit.checks,
        "check_groups": dict(sorted(audit.groups.items())),
        "target_readings": 7,
        "primary_evidence_bindings_replayed": 19,
        "non_target_lexical_rows_preserved": 317,
        "non_target_context_positions_preserved": 472,
        "complete_dictionary_rows_with_confidence_and_evidence": 1586,
        "bound_spans_preserved": 2,
        "f7r2_source_positions": 9,
        "f7r2_output_units": 8,
        "remaining_unreviewed_weak_readings": 84,
        "f84_or_f84r_used": 0,
    }
    (ART / "VALIDATION.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
