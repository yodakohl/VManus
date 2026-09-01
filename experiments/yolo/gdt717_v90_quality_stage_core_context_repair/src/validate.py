#!/usr/bin/env python3
"""Independent evidence, parity, confidence, and renderer checks for GDT717."""

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
EXP = ROOT / "experiments/yolo/gdt717_v90_quality_stage_core_context_repair"
SRC = EXP / "src"
ART = EXP / "artifacts"
G716 = ROOT / "experiments/yolo/gdt716_v89_indexed_share_core_context_repair/artifacts"
G711 = ROOT / "experiments/yolo/gdt711_v84_active_weak_family_repair/artifacts"

SOURCE_LEXICAL = G716 / "V89_324_ACTIVE_LEXICAL_READINGS.tsv"
SOURCE_CONTEXT = G716 / "V89_479_CONTEXT_REALIZATIONS.tsv"
SOURCE_COMPLETE = G716 / "V89_COMPLETE_WORD_CONFIDENCE.tsv"
SOURCE_CENSUS = G716 / "V89_84_HELD_READING_AUDIT.tsv"
SOURCE_SPANS = G716 / "V89_2_BOUND_SPAN_RENDERER.tsv"
SOURCE_FAMILIES = G711 / "V84_13_STEM_FAMILY_EVIDENCE.tsv"
SPECS = SRC / "V90_7_AUDIT_SPECS.tsv"
BINDINGS = SRC / "V90_34_PRIMARY_EVIDENCE_BINDINGS.tsv"

TARGET_LEXICAL = ART / "V90_324_ACTIVE_LEXICAL_READINGS.tsv"
TARGET_CONTEXT = ART / "V90_479_CONTEXT_REALIZATIONS.tsv"
TARGET_CENSUS = ART / "V90_71_HELD_READING_AUDIT.tsv"
TARGET_DELTA = ART / "V90_7_QUALITY_STAGE_CORE_CONTEXT_DELTA.tsv"
TARGET_EVIDENCE = ART / "V90_34_PRIMARY_EVIDENCE_BINDINGS.tsv"
TARGET_FAMILIES = ART / "V90_2_FAMILY_EVIDENCE.tsv"
TARGET_SPANS = ART / "V90_2_BOUND_SPAN_RENDERER.tsv"
TARGET_DIRECTIVES = ART / "V90_2_ONE_SHOT_RENDER_DIRECTIVES.tsv"
TARGET_RENDER = ART / "V90_8_F7R2_RENDERED_UNITS.tsv"
TARGET_COMPLETE = ART / "V90_COMPLETE_WORD_CONFIDENCE.tsv"
RESULT = ART / "RESULT.json"
REPORT = EXP / "REPORT.md"

HISTORICAL = "H0_NONE"
STATUS = (
    "PASS_V90_7_QUALITY_STAGE_READINGS_REVISED__5_GRID_PLUS_2_SISTER_WHOLES__"
    "7_POSITIONS_7_PAGES__64_WEAK_READINGS_REMAIN__F7R2_RERENDERED__ALL_H0_NONE"
)
GRID_IDS = {"otchy#1", "otchey#1", "otchdy#1", "okchedy#1", "otshey#1"}
SISTER_IDS = {"chody#1", "sheody#1"}


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


def v90_key(value: str) -> str:
    return value.replace("v89", "v90").replace("V89", "V90")


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


def rows_by_source(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    output: dict[str, dict[str, str]] = {}
    for row in rows:
        for source_id in split_pipe(row["source_reading_ids"]):
            assert source_id not in output
            output[source_id] = row
    return output


class Audit:
    def __init__(self) -> None:
        self.checks = 0
        self.groups: Counter[str] = Counter()

    def check(self, condition: bool, message: str, group: str = "general") -> None:
        self.checks += 1
        self.groups[group] += 1
        if not condition:
            raise AssertionError(message)


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
        "source lexical": (len(source_lexical), 324), "source context": (len(source_context), 479),
        "source complete": (len(source_complete), 1586), "source census": (len(source_census), 84),
        "source spans": (len(source_spans), 2), "source families": (len(source_families), 13),
        "specs": (len(specs), 7), "bindings": (len(bindings), 34),
        "lexical": (len(lexical), 324), "contexts": (len(contexts), 479),
        "census": (len(census), 71), "delta": (len(delta), 7),
        "evidence": (len(evidence), 34), "families": (len(families), 2),
        "spans": (len(spans), 2), "directives": (len(directives), 2),
        "rendered": (len(rendered), 8), "complete": (len(complete), 1586),
    }
    for name, (actual, expected) in expected_counts.items():
        audit.check(actual == expected, f"{name}: {actual} != {expected}", "counts")

    spec_by_id = {row["source_reading_id"]: row for row in specs}
    target_ids = set(spec_by_id)
    audit.check(len(spec_by_id) == 7, "duplicate target spec", "spec")
    audit.check(target_ids == GRID_IDS | SISTER_IDS, "target set", "spec")
    audit.check(all(row["decision"] == "REVISE" for row in specs), "non-revise target", "spec")
    audit.check(all(row["component_global_export_allowed"] == "0" for row in specs), "component export", "spec")
    audit.check(len({row["expected_position_id"] for row in specs}) == 7, "duplicate target position", "spec")
    audit.check(len({row["expected_page"] for row in specs}) == 7, "target page count", "spec")
    audit.check({row["source_reading_id"] for row in delta} == target_ids, "delta coverage", "spec")
    audit.check({row["source_reading_id"] for row in bindings} == target_ids, "binding coverage", "spec")
    for source_id in GRID_IDS:
        audit.check(set(split_pipe(spec_by_id[source_id]["score_credit_family_ids"])) == {"F_STATE", "F_STAGE"}, f"grid families {source_id}", "spec")
    for source_id in SISTER_IDS:
        audit.check(split_pipe(spec_by_id[source_id]["score_credit_family_ids"]) == ["F_STATE"], f"sister families {source_id}", "spec")

    output_evidence_by_id = {row["binding_id"]: row for row in evidence}
    audit.check(len(output_evidence_by_id) == 34, "duplicate output binding", "evidence")
    audit.check(len({row["binding_id"] for row in bindings}) == 34, "duplicate input binding", "evidence")
    credits_by_source: dict[str, list[str]] = defaultdict(list)
    for binding in bindings:
        binding_id = binding["binding_id"]
        audit.check(binding_id in output_evidence_by_id, f"missing output binding {binding_id}", "evidence")
        audit.check("f84" not in binding["evidence_path"].lower(), f"sealed path {binding_id}", "sealed")
        selector = parse_assertions(binding["selector"])
        assertions = parse_assertions(binding["field_assertions"])
        audit.check(bool(selector), f"empty selector {binding_id}", "evidence")
        audit.check(all(not value.lower().startswith("f84") for value in selector.values()), f"sealed selector {binding_id}", "sealed")
        source_path = ROOT / binding["evidence_path"]
        audit.check(source_path.is_file(), f"missing evidence source {binding_id}", "evidence")
        matches = [row for row in read_tsv(source_path) if all(row.get(field) == expected for field, expected in selector.items())]
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

    source_family_by_id = {row["family_id"]: row for row in source_families}
    for family_id in ("F_STATE", "F_STAGE"):
        audit.check(source_family_by_id[family_id]["family_bonus"] == "4", f"{family_id} bonus", "family")
        audit.check(source_family_by_id[family_id]["family_cap"] == "59", f"{family_id} cap", "family")
    for source_id in GRID_IDS:
        audit.check(credits_by_source[source_id] == ["F_STATE", "F_STAGE"], f"grid credit multiset {source_id}", "score")
    for source_id in SISTER_IDS:
        audit.check(credits_by_source[source_id] == ["F_STATE"], f"sister credit multiset {source_id}", "score")
    audit.check(sum(value.count("F_STATE") for value in credits_by_source.values()) == 7, "F_STATE total", "score")
    audit.check(sum(value.count("F_STAGE") for value in credits_by_source.values()) == 5, "F_STAGE total", "score")

    source_lexical_by_id = rows_by_source(source_lexical)
    lexical_by_id = rows_by_source(lexical)
    audit.check(len(source_lexical_by_id) == 332 and len(lexical_by_id) == 332, "source-reading cardinality", "lexical")
    expected_scores: dict[str, int] = {}
    for source_id, spec in spec_by_id.items():
        source = source_lexical_by_id[source_id]
        target = lexical_by_id[source_id]
        expected_delta = 8 if source_id in GRID_IDS else 4
        expected_score = min(int(source["working_model_score_0_100_not_probability"]) + expected_delta, int(spec["lexical_core_cap"]))
        expected_scores[source_id] = expected_score
        expectations = {
            "surface": source["surface"], "v90_lexical_core_de": spec["v90_lexical_core_de"],
            "v90_context_realizations_de": spec["v90_context_realization_de"],
            "family_ids": spec["family_ids"], "decomposition": spec["decomposition"],
            "repair_modes": spec["repair_mode"], "resolved_debt_atoms": spec["resolved_debt_atom"],
            "last_semantic_writer": "GDT717", "base_score": source["working_model_score_0_100_not_probability"],
            "score_delta_lexical_core": str(expected_delta), "lexical_core_cap": spec["lexical_core_cap"],
            "working_model_score_0_100_not_probability": str(expected_score),
            "working_model_level": "W1_WEAK_WORKING", "context_realization_cap": spec["context_realization_cap"],
            "context_realization_score_0_100_not_probability": str(expected_score),
            "context_realization_level": "W1_WEAK_WORKING", "v90_audit_decision": "REVISE",
            "v90_evidence_class": spec["evidence_class"], "v90_open_semantic_slots": spec["open_semantic_slots"],
            "v90_component_global_export_allowed": "0", "v90_prior_lexical_core_de": spec["old_lexical_core_de"],
            "historical_confirmation": HISTORICAL,
        }
        for field, expected in expectations.items():
            audit.check(target[field] == expected, f"target lexical {source_id}:{field}", "target_lexical")
        audit.check(source["v89_lexical_core_de"] == spec["old_lexical_core_de"], f"old core {source_id}", "target_lexical")
        audit.check("GDT717" in split_pipe(target["source_gdts"]), f"missing GDT717 {source_id}", "target_lexical")
        audit.check(spec["evidence_de"] in target["positive_evidence_de"], f"missing evidence {source_id}", "target_lexical")
        audit.check(spec["counterevidence_de"] in target["counterevidence_de"], f"missing counterevidence {source_id}", "target_lexical")
        for field in ("semantic_scope", "semantic_applicability", "global_export_scope", "bound_span_ids", "unconditional_global_export_allowed"):
            audit.check(target[field] == source[field], f"scope drift {source_id}:{field}", "scope")

    forbidden_heads = ("zubereitung", "ansatz", "mazerat", "auszug", "masse", "droge", "material", "stoff")
    for source_id in target_ids:
        core = lexical_by_id[source_id]["v90_lexical_core_de"].lower()
        audit.check(not any(word in core for word in forbidden_heads), f"product head leaked into {source_id}: {core}", "head_boundary")
        audit.check(any(stem in core for stem in ("trock", "feucht")), f"state absent {source_id}: {core}", "composition")
    audit.check("Anfangsstufe" in lexical_by_id["otchy#1"]["v90_lexical_core_de"], "otchy start", "composition")
    audit.check("Mittelstufe" in lexical_by_id["otchey#1"]["v90_lexical_core_de"], "otchey middle", "composition")
    audit.check("erreicht" in lexical_by_id["otchdy#1"]["v90_lexical_core_de"], "otchdy endpoint", "composition")
    audit.check("erreicht" in lexical_by_id["okchedy#1"]["v90_lexical_core_de"], "okchedy endpoint", "composition")
    audit.check("Mittelstufe" in lexical_by_id["otshey#1"]["v90_lexical_core_de"], "otshey middle", "composition")
    audit.check("abgeschlossen" in lexical_by_id["chody#1"]["v90_lexical_core_de"], "chody result", "composition")
    audit.check("Anfangsstufe abgeschlossen" in lexical_by_id["sheody#1"]["v90_lexical_core_de"], "sheody result", "composition")

    lexical_audit_fields = {
        "v90_audit_decision", "v90_evidence_class", "v90_open_semantic_slots",
        "v90_component_global_export_allowed", "v90_prior_lexical_core_de",
    }
    non_target_lexical = 0
    for source in source_lexical:
        source_ids = split_pipe(source["source_reading_ids"])
        target = lexical_by_id[source_ids[0]]
        if len(source_ids) == 1 and source_ids[0] in target_ids:
            continue
        non_target_lexical += 1
        for source_field, expected in source.items():
            target_field = v90_key(source_field)
            if target_field in lexical_audit_fields:
                continue
            audit.check(target[target_field] == expected, f"non-target lexical drift {source['surface']}:{target_field}", "lexical_parity")
    audit.check(non_target_lexical == 317, "non-target lexical count", "lexical_parity")

    source_context_by_position = {row["position_id"]: row for row in source_context}
    context_by_position = {row["position_id"]: row for row in contexts}
    audit.check(len(source_context_by_position) == 479 and len(context_by_position) == 479, "position uniqueness", "context")
    by_locus_ordinal = {(row["locus"], int(row["token_ordinal"])): row for row in source_context}
    target_position_ids = {row["expected_position_id"] for row in specs}
    for source_id, spec in spec_by_id.items():
        source = source_context_by_position[spec["expected_position_id"]]
        target = context_by_position[spec["expected_position_id"]]
        ordinal = int(spec["expected_token_ordinal"])
        left = "<BOS>" if ordinal == 1 else by_locus_ordinal[(spec["expected_locus"], ordinal - 1)]["surface"]
        expectations = {
            "source_reading_id": source_id, "surface": source["surface"], "page": spec["expected_page"],
            "locus": spec["expected_locus"], "token_ordinal": spec["expected_token_ordinal"],
            "v90_lexical_core_de": spec["v90_lexical_core_de"],
            "v90_context_realization_de": spec["v90_context_realization_de"],
            "v90_lexical_score": str(expected_scores[source_id]), "v90_lexical_level": "W1_WEAK_WORKING",
            "v90_context_score": str(expected_scores[source_id]), "v90_context_level": "W1_WEAK_WORKING",
            "v90_audit_decision": "REVISE", "v90_evidence_class": spec["evidence_class"],
            "v90_open_semantic_slots": spec["open_semantic_slots"], "v90_component_global_export_allowed": "0",
            "v90_local_context_hypothesis": spec["local_context_hypothesis"],
            "v90_expected_left_surface": spec["expected_left_surface"], "v90_historical_confirmation": HISTORICAL,
        }
        for field, expected in expectations.items():
            audit.check(target[field] == expected, f"target context {source_id}:{field}", "target_context")
        audit.check(left == spec["expected_left_surface"], f"left context {source_id}", "target_context")
        audit.check(source["v68_clause_type"] == "NOMINAL_BLOCK", f"target became action {source_id}", "nominality")
        audit.check(source["v68_action_license"] == "NOT_ACTION_LICENSED", f"action license {source_id}", "nominality")

    context_audit_fields = {
        "v90_audit_decision", "v90_evidence_class", "v90_open_semantic_slots",
        "v90_component_global_export_allowed", "v90_local_context_hypothesis", "v90_expected_left_surface",
    }
    non_target_context = 0
    for source in source_context:
        if source["position_id"] in target_position_ids:
            continue
        non_target_context += 1
        target = context_by_position[source["position_id"]]
        for source_field, expected in source.items():
            target_field = v90_key(source_field)
            if target_field in context_audit_fields:
                continue
            audit.check(target[target_field] == expected, f"non-target context drift {source['position_id']}:{target_field}", "context_parity")
    audit.check(non_target_context == 472, "non-target context count", "context_parity")

    source_held_ids = {row["source_reading_id"] for row in source_census if row["disposition"] == "HELD_FOR_LATER_REPAIR"}
    audit.check(len(source_held_ids) == 71, "source held count", "census")
    audit.check({row["source_reading_id"] for row in census} == source_held_ids, "census universe", "census")
    audit.check(Counter(row["disposition"] for row in census) == Counter({"REVISED_IN_V90": 7, "HELD_FOR_LATER_REPAIR": 64}), "census disposition", "census")
    audit.check({row["source_reading_id"] for row in census if row["disposition"] == "REVISED_IN_V90"} == target_ids, "census revised set", "census")

    family_by_id = {row["family_id"]: row for row in families}
    audit.check(set(family_by_id) == {"F_STATE", "F_STAGE"}, "family set", "family")
    audit.check(family_by_id["F_STATE"]["selected_source_readings"] == "7", "F_STATE selection count", "family")
    audit.check(family_by_id["F_STAGE"]["selected_source_readings"] == "5", "F_STAGE selection count", "family")
    audit.check(set(split_pipe(family_by_id["F_STATE"]["selected_source_reading_ids"])) == target_ids, "F_STATE selections", "family")
    audit.check(set(split_pipe(family_by_id["F_STAGE"]["selected_source_reading_ids"])) == GRID_IDS, "F_STAGE selections", "family")
    for family_id in family_by_id:
        row = family_by_id[family_id]
        audit.check(row["family_bonus"] == "4" and row["selected_v90_levels"] == "W1_WEAK_WORKING", f"family score/level {family_id}", "family")
        audit.check(row["automatic_historical_credit"] == "0" and row["historical_confirmation"] == HISTORICAL, f"family historical {family_id}", "family")

    audit.check(spans == source_spans, "bound span drift", "renderer")
    span = next(row for row in spans if row["bound_span_id"] == "G678_KEO_R_F7R2")
    audit.check(span["left_position_id"] == "P288" and span["right_position_id"] == "P289", "f7r2 span", "renderer")
    audit.check(span["render_once_de"] == "heiße Portion" and span["global_export_allowed"] == "0", "span meaning/export", "renderer")
    directives_by_position = {row["source_position_id"]: row for row in directives}
    audit.check(set(directives_by_position) == {"P288", "P289"}, "directive positions", "renderer")
    audit.check(directives_by_position["P288"]["render_action"] == "EMIT_SPAN_ONCE", "left directive", "renderer")
    audit.check(directives_by_position["P288"]["emitted_text_de"] == "heiße Portion", "left emission", "renderer")
    audit.check(directives_by_position["P289"]["render_action"] == "CONSUME_NO_OUTPUT", "right directive", "renderer")
    audit.check(directives_by_position["P289"]["emitted_text_de"] == "", "right emission", "renderer")
    expected_render: list[dict[str, str]] = []
    f7r2_positions = sorted((row for row in contexts if row["locus"] == "f7r.2"), key=lambda row: int(row["token_ordinal"]))
    audit.check(len(f7r2_positions) == 9, "f7r2 source positions", "renderer")
    for source in f7r2_positions:
        directive = directives_by_position.get(source["position_id"])
        if directive and directive["render_action"] == "CONSUME_NO_OUTPUT":
            continue
        if directive:
            expected_render.append({
                "source_kind": "BOUND_SPAN", "source_ref": span["bound_span_id"],
                "anchor_position_id": "P288", "consumed_position_ids": "P288|P289",
                "source_surfaces": "keo|r", "rendered_text_de": "heiße Portion",
            })
        else:
            expected_render.append({
                "source_kind": "CONTEXT_POSITION", "source_ref": source["position_id"],
                "anchor_position_id": source["position_id"], "consumed_position_ids": source["position_id"],
                "source_surfaces": source["surface"], "rendered_text_de": source["v90_context_realization_de"],
            })
    audit.check(len(expected_render) == 8, "render output count", "renderer")
    for ordinal, (expected, actual) in enumerate(zip(expected_render, rendered), start=1):
        audit.check(actual["output_ordinal"] == str(ordinal), f"render ordinal {ordinal}", "renderer")
        audit.check(actual["page"] == "f7r" and actual["locus"] == "f7r.2", f"render locus {ordinal}", "renderer")
        audit.check(actual["historical_confirmation"] == HISTORICAL, f"render historical {ordinal}", "renderer")
        for field, value in expected.items():
            audit.check(actual[field] == value, f"render {ordinal}:{field}", "renderer")
    render_text = " · ".join(row["rendered_text_de"] for row in rendered)
    audit.check(render_text.count("heiße Portion") == 1, "span not rendered exactly once", "renderer")
    audit.check("kalt-trockene Zubereitung, Anfangsstufe" in render_text, "V90 otchy output absent", "renderer")
    source_render_text = " · ".join(
        row["v89_context_realization_de"] for row in sorted(
            (row for row in source_context if row["locus"] == "f7r.2" and row["position_id"] not in {"P289"}),
            key=lambda row: int(row["token_ordinal"]),
        )
    )
    audit.check("kalt-trockene Zubereitung am Anfang des Grades" in source_render_text, "source otchy control absent", "renderer")

    complete_keys = {(row["surface"], row["reading_id"]) for row in complete}
    audit.check(len(complete_keys) == 1586, "complete key uniqueness", "complete")
    audit.check(len({row["surface"] for row in complete}) == 1582, "complete surface count", "complete")
    for row in complete:
        key = f"{row['surface']}:{row['reading_id']}"
        audit.check(bool(row["working_meaning_de"].strip()), f"missing default meaning {key}", "dictionary_evidence")
        audit.check(row["working_model_score_0_100_not_probability"].isdigit(), f"missing score {key}", "dictionary_evidence")
        score = int(row["working_model_score_0_100_not_probability"])
        audit.check(0 <= score <= 100, f"score range {key}", "dictionary_evidence")
        audit.check(row["working_model_level"] == level(score), f"wrong level {key}", "dictionary_evidence")
        audit.check(bool(row["positive_evidence_de"].strip()), f"missing evidence {key}", "dictionary_evidence")
        audit.check(bool(row["counterevidence_de"].strip()), f"missing counterevidence {key}", "dictionary_evidence")
        audit.check(row["historical_confirmation"] == HISTORICAL, f"historical leak {key}", "dictionary_evidence")
    active_complete = [row for row in complete if row["current_layer"] == "ACTIVE_V90_LEXICAL_CORE"]
    audit.check(len(active_complete) == 324, "active complete count", "complete")
    active_complete_by_id = {row["reading_id"]: row for row in active_complete}
    audit.check(len(active_complete_by_id) == 324, "active complete ids", "complete")
    for row in lexical:
        dictionary_row = active_complete_by_id[row["v90_reading_id"]]
        audit.check(dictionary_row["working_meaning_de"] == row["v90_lexical_core_de"], f"dictionary meaning {row['surface']}", "complete_parity")
        audit.check(dictionary_row["working_model_score_0_100_not_probability"] == row["working_model_score_0_100_not_probability"], f"dictionary score {row['surface']}", "complete_parity")
        audit.check(dictionary_row["positive_evidence_de"] == row["positive_evidence_de"], f"dictionary evidence {row['surface']}", "complete_parity")
        audit.check(dictionary_row["counterevidence_de"] == row["counterevidence_de"], f"dictionary counterevidence {row['surface']}", "complete_parity")

    source_complete_by_key = {(row["surface"], row["reading_id"]): row for row in source_complete}
    nonactive_target = [row for row in complete if row["current_layer"] != "ACTIVE_V90_LEXICAL_CORE"]
    audit.check(len(nonactive_target) == 1262, "nonactive complete count", "complete_parity")
    complete_audit_fields = {"v90_audit_decision", "v90_evidence_class", "v90_open_semantic_slots", "v90_component_global_export_allowed"}
    for target in nonactive_target:
        source = source_complete_by_key[(target["surface"], target["reading_id"])]
        for source_field, expected in source.items():
            target_field = v90_key(source_field)
            if target_field in complete_audit_fields:
                continue
            audit.check(target[target_field] == expected, f"nonactive complete drift {target['reading_id']}:{target_field}", "complete_parity")

    expected_active_levels = Counter({
        "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY": 7, "W1_WEAK_WORKING": 135,
        "W2_PROVISIONAL_WORKING": 163, "W3_SOLID_WORKING_THEORY": 19,
    })
    expected_complete_levels = Counter({
        "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY": 287, "W1_WEAK_WORKING": 315,
        "W2_PROVISIONAL_WORKING": 541, "W3_SOLID_WORKING_THEORY": 443,
    })
    audit.check(Counter(row["working_model_level"] for row in lexical) == expected_active_levels, "active levels", "score")
    audit.check(Counter(row["working_model_level"] for row in complete) == expected_complete_levels, "complete levels", "score")

    expected_promotions = {source_id: (8 if source_id in GRID_IDS else 4) for source_id in target_ids}
    result_expectations: dict[str, Any] = {
        "experiment_id": "GDT717", "status": STATUS,
        "claim_ceiling": "EXPLORATORY_WORKING_DICTIONARY_ONLY_NOT_PLAINTEXT",
        "audited_readings": 7, "audited_positions": 7, "audited_pages": 7,
        "grid_readings": 5, "sister_whole_readings": 2, "primary_evidence_bindings": 34,
        "score_families": ["F_STATE", "F_STAGE"], "score_promotions": expected_promotions,
        "active_lexical_readings": 324, "active_positions": 479,
        "active_level_counts": dict(sorted(expected_active_levels.items())),
        "remaining_unreviewed_weak_readings": 64, "complete_readings": 1586, "complete_surfaces": 1582,
        "complete_level_counts": dict(sorted(expected_complete_levels.items())),
        "bound_span_renderers": 2, "one_shot_directives": 2, "f7r2_rendered_units": 8,
        "f7r2_rendered_line_de": render_text, "relation_word_credit_gdt717": 0,
        "historical_confirmation": HISTORICAL, "new_pages": 0, "new_images": 0,
        "new_transcription": 0, "f84_or_f84r_used": 0,
    }
    for field, expected in result_expectations.items():
        audit.check(result[field] == expected, f"result {field}", "result")
    report = REPORT.read_text(encoding="utf-8")
    for source_id, spec in spec_by_id.items():
        audit.check(f"`{source_id.removesuffix('#1')}`" in report, f"report surface {source_id}", "report")
        audit.check(spec["v90_context_realization_de"] in report, f"report context {source_id}", "report")
    for needle in (STATUS, "34", "1586", "64", "F_STATE +4", "F_STAGE +4"):
        audit.check(needle in report, f"report missing {needle}", "report")

    output_files = [
        EXP / "README.md", EXP / "METHOD.md", EXP / "REPORT.md", EXP / "experiment.json",
        SRC / "run.py", SRC / "validate.py", SPECS, BINDINGS, ART / "README.md",
        TARGET_LEXICAL, TARGET_CONTEXT, TARGET_CENSUS, TARGET_DELTA, TARGET_EVIDENCE,
        TARGET_FAMILIES, TARGET_SPANS, TARGET_DIRECTIVES, TARGET_RENDER, TARGET_COMPLETE, RESULT,
    ]
    private_markers = ("/" + "home/", "/" + "Users/")
    for path in output_files:
        text = path.read_text(encoding="utf-8")
        audit.check(not any(marker in text for marker in private_markers), f"absolute private path in {path.name}", "privacy")
    for row in contexts:
        audit.check(not row["page"].startswith("f84") and not row["locus"].startswith("f84"), f"sealed context {row['position_id']}", "sealed")

    validation = {
        "experiment_id": "GDT717", "status": "PASS", "checks_passed": audit.checks,
        "check_groups": dict(sorted(audit.groups.items())), "target_readings": 7,
        "grid_readings": 5, "sister_whole_readings": 2,
        "primary_evidence_bindings_replayed": 34,
        "unique_F_STATE_score_credits": 7, "unique_F_STAGE_score_credits": 5,
        "non_target_lexical_rows_preserved": non_target_lexical,
        "non_target_context_positions_preserved": non_target_context,
        "complete_dictionary_rows_with_default_confidence_and_evidence": len(complete),
        "bound_spans_preserved": len(spans), "f7r2_source_positions": len(f7r2_positions),
        "f7r2_output_units": len(rendered), "remaining_unreviewed_weak_readings": 64,
        "f84_or_f84r_used": 0,
    }
    (ART / "VALIDATION.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(validation, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
