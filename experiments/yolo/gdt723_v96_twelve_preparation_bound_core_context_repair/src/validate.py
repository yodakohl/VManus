#!/usr/bin/env python3
"""Independent validator for GDT723/V96."""

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
sys.path.insert(0, str(ROOT))

from tools.vmanus_experiment import GuardedTSV  # noqa: E402


EXP = ROOT / "experiments/yolo/gdt723_v96_twelve_preparation_bound_core_context_repair"
SRC = EXP / "src"
ART = EXP / "artifacts"
G722 = ROOT / "experiments/yolo/gdt722_v95_op_whole_scope_and_context_separation/artifacts"
HISTORICAL = "H0_NONE"
ACTION_IDS = {"qocho#1", "ykcho#1", "ytcho#1"}
TARGET_IDS = {
    "adeeody#1", "chockhy#1", "ofchedy#1", "okeeeey#1", "okiin#1", "olord#1",
    "otsheody#1", "qocho#1", "shotchey#1", "solchedy#1", "ykcho#1", "ytcho#1",
}
EXPECTED_STATUS = (
    "PASS_V96_12_PREPARATION_HOLDS_REVISED__10_LATER_BOUND_WHOLES_PLUS_1_EXACT_O_CKH_"
    "GRID_PLUS_1_BOUNDARY_SEED_HEAD__3_LOCAL_ACTIONS_SEPARATED__35_WEAK_READINGS_REMAIN__"
    "NO_COMPONENT_EXPORT_NO_SCORE_CREDIT__ALL_H0_NONE"
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def split_pipe(value: str) -> list[str]:
    return [part.strip() for part in value.split("|") if part.strip() and part.strip() not in {"NONE", "0"}]


def parse_assertions(value: str) -> dict[str, str]:
    if not value or value == "NONE":
        return {}
    output: dict[str, str] = {}
    for part in value.split(";"):
        field, expected = part.split("=", 1)
        assert field and field not in output
        output[field] = expected
    return output


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


def fingerprint(row: dict[str, str]) -> str:
    payload = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def guarded_rows(path: Path, selector: str, allowed: set[str]) -> list[dict[str, str]]:
    assert allowed and all(not value.lower().startswith("f84") for value in allowed)
    source = GuardedTSV(
        path,
        selector_column=selector,
        allowed_values=allowed,
        forbidden_prefixes=("f84",),
        forbidden_action="skip",
    )
    return list(source)


def main() -> int:
    checks: Counter[str] = Counter()

    def check(group: str, condition: bool, detail: Any = "") -> None:
        assert condition, (group, detail)
        checks[group] += 1

    specs = read_tsv(SRC / "V96_12_AUDIT_SPECS.tsv")
    lexical = read_tsv(ART / "V96_324_ACTIVE_LEXICAL_READINGS.tsv")
    contexts = read_tsv(ART / "V96_479_CONTEXT_REALIZATIONS.tsv")
    census = read_tsv(ART / "V96_47_HELD_READING_AUDIT.tsv")
    delta = read_tsv(ART / "V96_12_PREPARATION_CORE_CONTEXT_DELTA.tsv")
    scope = read_tsv(ART / "V96_6_SCOPE_DICTIONARY.tsv")
    rivals = read_tsv(ART / "V96_36_RIVAL_MODEL_COMPARISON.tsv")
    evidence = read_tsv(ART / "V96_61_PRIMARY_EVIDENCE_BINDINGS.tsv")
    lineage = read_tsv(ART / "V96_12_LINEAGE_AUDIT.tsv")
    renderer = read_tsv(ART / "V96_12_TARGET_RENDERER.tsv")
    separation = read_tsv(ART / "V96_12_ACTION_HEAD_SEPARATION.tsv")
    complete = read_tsv(ART / "V96_COMPLETE_WORD_CONFIDENCE.tsv")
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    source_lexical = read_tsv(G722 / "V95_324_ACTIVE_LEXICAL_READINGS.tsv")
    source_context = read_tsv(G722 / "V95_479_CONTEXT_REALIZATIONS.tsv")

    check("counts", len(specs) == 12)
    check("counts", {row["source_reading_id"] for row in specs} == TARGET_IDS)
    check("counts", len(lexical) == 324)
    check("counts", len(contexts) == 479)
    check("counts", len(census) == 47)
    check("counts", len(delta) == 12)
    check("counts", len(scope) == 6)
    check("counts", len(rivals) == 36)
    check("counts", len(evidence) == 61)
    check("counts", len(lineage) == 12)
    check("counts", len(renderer) == 12)
    check("counts", len(separation) == 12)
    check("counts", len(complete) == 1586)
    check("counts", len({row["surface"] for row in complete}) == 1582)

    spec_by_id = {row["source_reading_id"]: row for row in specs}
    lexical_by_source: dict[str, dict[str, str]] = {}
    for row in lexical:
        for source_id in split_pipe(row["source_reading_ids"]):
            check("lexical_index", source_id not in lexical_by_source, source_id)
            lexical_by_source[source_id] = row
    check("lexical_index", len(lexical_by_source) == 332)

    for source_id, spec in spec_by_id.items():
        row = lexical_by_source[source_id]
        expected_score = spec["expected_old_score"]
        check("target_lexical", row["surface"] == spec["surface"], source_id)
        check("target_lexical", row["v96_lexical_core_de"] == spec["v96_lexical_core_de"], source_id)
        check("target_lexical", row["v96_context_realizations_de"] == spec["v96_context_realization_de"], source_id)
        check("target_lexical", row["decomposition"] == spec["decomposition"], source_id)
        check("target_lexical", row["v96_lineage_class"] == spec["lineage_class"], source_id)
        check("target_lexical", row["working_model_score_0_100_not_probability"] == expected_score, source_id)
        check("target_lexical", row["working_model_level"] == "W1_WEAK_WORKING", source_id)
        check("target_lexical", row["context_realization_score_0_100_not_probability"] == expected_score, source_id)
        check("target_lexical", row["v96_component_global_export_allowed"] == "0", source_id)
        check("target_lexical", row["v96_exact_whole_surface_default_allowed"] == "1", source_id)
        check("target_lexical", row["global_export_scope"] == "ACTIVE_WORKING_DEFAULT", source_id)
        check("target_lexical", row["unconditional_global_export_allowed"] == "1", source_id)
        check("target_lexical", row["last_semantic_writer"] == "GDT723", source_id)
        check("target_lexical", "GDT723" in split_pipe(row["source_gdts"]), source_id)
        check("target_lexical", row["historical_confirmation"] == HISTORICAL, source_id)
        check("target_lexical", row["v96_prior_lexical_core_de"] == spec["expected_old_core_de"], source_id)

    action_words = {
        "qocho#1": "nehmen",
        "ykcho#1": "bereiten",
        "ytcho#1": "herstellen",
    }
    for source_id, word in action_words.items():
        row = lexical_by_source[source_id]
        check("action_separation", word not in row["v96_lexical_core_de"].lower(), source_id)
        check("action_separation", word in row["v96_context_realizations_de"].lower(), source_id)
    check("action_separation", "geführt" not in lexical_by_source["okeeeey#1"]["v96_lexical_core_de"])
    check("action_separation", "geführt" not in lexical_by_source["okeeeey#1"]["v96_context_realizations_de"])
    check("action_separation", lexical_by_source["chockhy#1"]["v96_lexical_core_de"] == "trockene Mischung, Anfangsstufe")
    check("action_separation", lexical_by_source["solchedy#1"]["v96_lexical_core_de"] == "Samenmaterial; bis zur Mittelstufe getrocknet")

    check("lexical_parity", len(source_lexical) == len(lexical))
    for source, target in zip(source_lexical, lexical, strict=True):
        source_ids = split_pipe(source["source_reading_ids"])
        targeted = any(source_id in TARGET_IDS for source_id in source_ids)
        check("lexical_parity", source["surface"] == target["surface"], source["surface"])
        check("lexical_parity", source["source_reading_ids"] == target["source_reading_ids"], source["surface"])
        check("lexical_parity", source["occurrence_count"] == target["occurrence_count"], source["surface"])
        check("lexical_parity", source["page_count"] == target["page_count"], source["surface"])
        check("lexical_parity", source["locus_count"] == target["locus_count"], source["surface"])
        check("lexical_parity", source["working_model_score_0_100_not_probability"] == target["working_model_score_0_100_not_probability"], source["surface"])
        check("lexical_parity", source["working_model_level"] == target["working_model_level"], source["surface"])
        check("lexical_parity", source["historical_confirmation"] == target["historical_confirmation"], source["surface"])
        if not targeted:
            check("lexical_parity", source["v95_lexical_core_de"] == target["v96_lexical_core_de"], source["surface"])
            check("lexical_parity", source["v95_context_realizations_de"] == target["v96_context_realizations_de"], source["surface"])
            check("lexical_parity", source["family_ids"] == target["family_ids"], source["surface"])
            check("lexical_parity", source["decomposition"] == target["decomposition"], source["surface"])
            check("lexical_parity", target["v96_audit_decision"] == "NOT_IN_GDT723_TRANCHE", source["surface"])

    context_by_position = {row["position_id"]: row for row in contexts}
    check("context_index", len(context_by_position) == 479)
    for source_id, spec in spec_by_id.items():
        row = context_by_position[spec["expected_position_id"]]
        check("target_context", row["source_reading_id"] == source_id, source_id)
        check("target_context", row["surface"] == spec["surface"], source_id)
        check("target_context", row["page"] == spec["expected_page"], source_id)
        check("target_context", row["locus"] == spec["expected_locus"], source_id)
        check("target_context", row["token_ordinal"] == spec["expected_token_ordinal"], source_id)
        check("target_context", row["v96_lexical_core_de"] == spec["v96_lexical_core_de"], source_id)
        check("target_context", row["v96_context_realization_de"] == spec["v96_context_realization_de"], source_id)
        check("target_context", row["v96_expected_left_surface"] == spec["expected_left_surface"], source_id)
        check("target_context", row["v96_expected_right_surface"] == spec["expected_right_surface"], source_id)
        check("target_context", row["v68_action_license"] == spec["expected_action_license"], source_id)
        check("target_context", row["v96_component_global_export_allowed"] == "0", source_id)
        check("target_context", row["v96_exact_whole_surface_default_allowed"] == "1", source_id)
        check("target_context", row["v96_lineage_class"] == spec["lineage_class"], source_id)

    check("context_parity", len(source_context) == len(contexts))
    for source, target in zip(source_context, contexts, strict=True):
        targeted = source["source_reading_id"] in TARGET_IDS
        check("context_parity", source["position_id"] == target["position_id"], source["position_id"])
        check("context_parity", source["page"] == target["page"], source["position_id"])
        check("context_parity", source["locus"] == target["locus"], source["position_id"])
        check("context_parity", source["token_ordinal"] == target["token_ordinal"], source["position_id"])
        check("context_parity", source["surface"] == target["surface"], source["position_id"])
        check("context_parity", source["source_reading_id"] == target["source_reading_id"], source["position_id"])
        check("context_parity", source["v68_action_license"] == target["v68_action_license"], source["position_id"])
        if not targeted:
            check("context_parity", source["v95_lexical_core_de"] == target["v96_lexical_core_de"], source["position_id"])
            check("context_parity", source["v95_context_realization_de"] == target["v96_context_realization_de"], source["position_id"])
            check("context_parity", source["v95_lexical_score"] == target["v96_lexical_score"], source["position_id"])
            check("context_parity", source["v95_context_score"] == target["v96_context_score"], source["position_id"])
            check("context_parity", target["v96_audit_decision"] == "NOT_IN_GDT723_TRANCHE", source["position_id"])

    dispositions = Counter(row["disposition"] for row in census)
    check("census", dispositions == Counter({"HELD_FOR_LATER_REPAIR": 35, "REVISED_IN_V96": 12}))
    revised = {row["source_reading_id"]: row for row in census if row["disposition"] == "REVISED_IN_V96"}
    check("census", set(revised) == TARGET_IDS)
    for source_id, row in revised.items():
        spec = spec_by_id[source_id]
        check("census", row["v96_lexical_core_de"] == spec["v96_lexical_core_de"], source_id)
        check("census", row["v96_context_realization_de"] == spec["v96_context_realization_de"], source_id)
        check("census", row["new_lexical_score"] == spec["expected_old_score"], source_id)
        check("census", row["new_lexical_level"] == "W1_WEAK_WORKING", source_id)

    delta_by_id = {row["source_reading_id"]: row for row in delta}
    check("delta", set(delta_by_id) == TARGET_IDS)
    for source_id, row in delta_by_id.items():
        spec = spec_by_id[source_id]
        check("delta", row["surface"] == spec["surface"], source_id)
        check("delta", row["old_lexical_core_de"] == spec["expected_old_core_de"], source_id)
        check("delta", row["v96_lexical_core_de"] == spec["v96_lexical_core_de"], source_id)
        check("delta", row["v96_context_realization_de"] == spec["v96_context_realization_de"], source_id)
        check("delta", row["v96_score"] == row["old_score"] == spec["expected_old_score"], source_id)
        check("delta", row["score_credit_family_ids"] == "NONE", source_id)
        check("delta", row["component_global_export_allowed"] == "0", source_id)
        check("delta", row["exact_whole_surface_default_allowed"] == "1", source_id)
        check("delta", row["historical_confirmation"] == HISTORICAL, source_id)

    lineage_by_id = {row["source_reading_id"]: row for row in lineage}
    check("lineage", set(lineage_by_id) == TARGET_IDS)
    check("lineage", Counter(row["gdt652_scope_state"] for row in lineage) == Counter({
        "UNKNOWN_SURFACE": 10, "KNOWN_EXACT_WHOLE": 1, "READER_BOUNDARY_UNSTABLE": 1,
    }))
    check("lineage", lineage_by_id["chockhy#1"]["gdt652_scope_state"] == "KNOWN_EXACT_WHOLE")
    check("lineage", lineage_by_id["solchedy#1"]["gdt652_scope_state"] == "READER_BOUNDARY_UNSTABLE")
    for source_id, row in lineage_by_id.items():
        spec = spec_by_id[source_id]
        check("lineage", row["surface"] == spec["surface"], source_id)
        check("lineage", row["gdt691_rule_id"] == spec["gdt691_rule_id"], source_id)
        check("lineage", row["gdt691_formal_route"] == spec["gdt691_formal_route"], source_id)
        check("lineage", row["gdt691_practical_head_de"] == spec["gdt691_practical_head_de"], source_id)
        check("lineage", row["v96_lineage_class"] == spec["lineage_class"], source_id)
        check("lineage", row["v96_selected_portable_core_de"] == spec["v96_lexical_core_de"], source_id)
        check("lineage", row["v96_selected_local_renderer_de"] == spec["v96_context_realization_de"], source_id)
        check("lineage", row["component_global_export_allowed"] == "0", source_id)
        check("lineage", row["score_credit"] == "0", source_id)

    lexical_source_by_id = {
        source_id: row for row in source_lexical for source_id in split_pipe(row["source_reading_ids"])
    }
    context_source_by_position = {row["position_id"]: row for row in source_context}
    g691_reader_path = ROOT / "experiments/yolo/gdt691_preparation_head_role_dispatch/artifacts/V64_479_TOKEN_READER.tsv"
    g691_rules_path = ROOT / "experiments/yolo/gdt691_preparation_head_role_dispatch/src/V64_EXACT_TOKEN_RULES.tsv"
    g652_path = ROOT / "experiments/yolo/gdt652_strict_v28_frontier_completion/artifacts/ALL_LINE_CONCRETE_COVERAGE_V29.tsv"
    g713_family_path = ROOT / "experiments/yolo/gdt713_v86_measure_ckh_core_context_repair/artifacts/V86_8_FAMILY_EVIDENCE.tsv"
    allowed_loci = {row["expected_locus"] for row in specs}
    g691_reader = {
        (row["locus"], row["token_ordinal"]): row
        for row in guarded_rows(g691_reader_path, "locus", allowed_loci)
    }
    g691_rules = {row["rule_id"]: row for row in read_tsv(g691_rules_path)}
    g652 = {row["locus"]: row for row in guarded_rows(g652_path, "locus", allowed_loci)}
    g713_family = {row["family_id"]: row for row in read_tsv(g713_family_path)}
    replay_rows: dict[tuple[str, str], dict[str, str]] = {}
    for source_id, spec in spec_by_id.items():
        replay_rows[(source_id, "V95_ACTIVE_LEXICAL")] = lexical_source_by_id[source_id]
        replay_rows[(source_id, "V95_EXACT_CONTEXT")] = context_source_by_position[spec["expected_position_id"]]
        replay_rows[(source_id, "GDT691_TOKEN_READER")] = g691_reader[(spec["expected_locus"], spec["expected_token_ordinal"])]
        replay_rows[(source_id, "GDT691_EXACT_RULE")] = g691_rules[spec["gdt691_rule_id"]]
        replay_rows[(source_id, "GDT652_POSITION_LINEAGE")] = g652[spec["expected_locus"]]
    replay_rows[("chockhy#1", "GDT713_CKH_FAMILY_CONTROL")] = g713_family["F_CKH"]
    binding_ids: set[str] = set()
    for row in evidence:
        binding_id = row["binding_id"]
        check("bindings", binding_id not in binding_ids, binding_id)
        binding_ids.add(binding_id)
        source_id = row["source_reading_id"]
        check("bindings", source_id in TARGET_IDS, binding_id)
        check("bindings", "f84" not in row["evidence_path"].lower(), binding_id)
        check("bindings", row["score_credit_family_ids"] == "NONE", binding_id)
        check("bindings", row["source_row_match"] == "1", binding_id)
        expected_status = "BOUND_EXACT_FAMILY_ROW" if row["evidence_role"] == "GDT713_CKH_FAMILY_CONTROL" else "BOUND_EXACT_PRIMARY_ROW"
        check("bindings", row["evidence_status"] == expected_status, binding_id)
        check("bindings", row["historical_confirmation"] == HISTORICAL, binding_id)
        source = replay_rows[(source_id, row["evidence_role"])]
        selector = parse_assertions(row["selector"])
        for field, expected in selector.items():
            check("bindings", field in source, (binding_id, field))
            check("bindings", source[field] == expected, (binding_id, field))
        projection = parse_assertions(row["position_projection"])
        if row["evidence_role"] == "GDT652_POSITION_LINEAGE":
            check("bindings", set(projection) == {"token_ordinal", "gdt652_scope_state"}, binding_id)
            ordinal = int(projection["token_ordinal"])
            states = split_pipe(source["scope_states"])
            check("bindings", 1 <= ordinal <= len(states), binding_id)
            check("bindings", states[ordinal - 1] == projection["gdt652_scope_state"], binding_id)
        else:
            check("bindings", not projection, binding_id)
        check("fingerprints", row["matched_row_fingerprint_sha256"] == fingerprint(source), binding_id)
    check("bindings", len(binding_ids) == 61)
    check("bindings", Counter(row["source_reading_id"] for row in evidence) == Counter({
        **{source_id: 5 for source_id in TARGET_IDS}, "chockhy#1": 6,
    }))
    check("bindings", Counter(row["evidence_role"] for row in evidence) == Counter({
        "V95_ACTIVE_LEXICAL": 12,
        "V95_EXACT_CONTEXT": 12,
        "GDT691_TOKEN_READER": 12,
        "GDT691_EXACT_RULE": 12,
        "GDT652_POSITION_LINEAGE": 12,
        "GDT713_CKH_FAMILY_CONTROL": 1,
    }))

    rival_by_target: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rivals:
        rival_by_target[row["source_reading_id"]].append(row)
        check("rivals", row["score_credit"] == "0", row["source_reading_id"])
        check("rivals", row["component_global_export_allowed"] == "0", row["source_reading_id"])
    check("rivals", set(rival_by_target) == TARGET_IDS)
    for source_id, rows in rival_by_target.items():
        check("rivals", {row["model_id"] for row in rows} == {
            "A_BOUND_CORE_PLUS_EXACT_LOCAL_RENDERER",
            "B_OLD_FULL_PRODUCT_OR_ACTION_AS_PORTABLE_WORD",
            "C_UNRELATED_LEARNED_TECHNICAL_WHOLE",
        }, source_id)
        selected = [row for row in rows if row["portable_default_selected"] == "1"]
        check("rivals", len(selected) == 1 and selected[0]["model_id"] == "A_BOUND_CORE_PLUS_EXACT_LOCAL_RENDERER", source_id)

    scope_by_id = {row["scope_item"]: row for row in scope}
    check("scope", set(scope_by_id) == {
        "TEN_LATER_BOUND_WHOLES", "CHOCKHY_EXACT_O_CKH_GRID", "SOLCHEDY_BOUNDARY_SEED_HEAD",
        "YKCHO_YTCHO_PAIRED_WHOLES", "LOCAL_PRODUCT_HEADS", "LOCAL_ACTION_AND_SOURCE_WORDING",
    })
    for row in scope:
        check("scope", row["score_credit"] == "0", row["scope_item"])
        check("scope", row["component_or_substring_global_export_allowed"] == "0", row["scope_item"])
        check("scope", row["historical_confirmation"] == HISTORICAL, row["scope_item"])
    check("scope", "GDT652_KNOWN_EXACT_WHOLE" in scope_by_id["CHOCKHY_EXACT_O_CKH_GRID"]["lineage"])
    check("scope", "READER_BOUNDARY_UNSTABLE" in scope_by_id["SOLCHEDY_BOUNDARY_SEED_HEAD"]["lineage"])
    check("scope", scope_by_id["YKCHO_YTCHO_PAIRED_WHOLES"]["status"] == "PAIR_ONLY_NO_K_T_CHO_EXPORT")

    renderer_by_id = {row["source_reading_id"] if "source_reading_id" in row else row["surface"]: row for row in renderer}
    renderer_by_surface = {row["surface"]: row for row in renderer}
    check("renderer", set(renderer_by_surface) == {row["surface"] for row in specs})
    for spec in specs:
        row = renderer_by_surface[spec["surface"]]
        check("renderer", row["position_id"] == spec["expected_position_id"], spec["surface"])
        check("renderer", row["portable_lexical_core_de"] == spec["v96_lexical_core_de"], spec["surface"])
        check("renderer", row["local_context_realization_de"] == spec["v96_context_realization_de"], spec["surface"])
        check("renderer", row["component_global_export_allowed"] == "0", spec["surface"])
        check("renderer", row["score"] == spec["expected_old_score"], spec["surface"])
        check("renderer", row["level"] == "W1_WEAK_WORKING", spec["surface"])

    separation_by_id = {row["source_reading_id"]: row for row in separation}
    check("separation", set(separation_by_id) == TARGET_IDS)
    check("separation", sum(row["position_is_action_licensed"] == "1" for row in separation) == 3)
    for source_id, row in separation_by_id.items():
        check("separation", row["portable_action_export_allowed"] == "0", source_id)
        check("separation", row["portable_product_head_export_allowed"] == "0", source_id)
        check("separation", row["component_global_export_allowed"] == "0", source_id)
        for local_word in split_pipe(row["local_only_words_or_heads"]):
            check("separation", local_word.lower() in row["local_context_realization_de"].lower(), (source_id, local_word))
            check("separation", local_word.lower() not in row["portable_lexical_core_de"].lower(), (source_id, local_word))
        expected = "PASS_LOCAL_ACTION_SEPARATED" if source_id in ACTION_IDS else "PASS_NOMINAL_NO_HIDDEN_ACTION"
        check("separation", row["audit_status"] == expected, source_id)

    levels = Counter(row["working_model_level"] for row in lexical)
    check("dictionary", levels == Counter({
        "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY": 7,
        "W1_WEAK_WORKING": 135,
        "W2_PROVISIONAL_WORKING": 163,
        "W3_SOLID_WORKING_THEORY": 19,
    }))
    active_complete = [row for row in complete if row["current_layer"] == "ACTIVE_V96_LEXICAL_CORE"]
    check("dictionary", len(active_complete) == 324)
    complete_by_reading = {row["reading_id"]: row for row in active_complete}
    check("dictionary", len(complete_by_reading) == 324)
    for row in complete:
        check("complete", bool(row["working_meaning_de"]), row["reading_id"])
        score = int(row["working_model_score_0_100_not_probability"])
        check("complete", row["working_model_level"] == level(score), row["reading_id"])
        check("complete", bool(row["positive_evidence_de"]), row["reading_id"])
        check("complete", bool(row["counterevidence_de"]), row["reading_id"])
        check("complete", row["historical_confirmation"] == HISTORICAL, row["reading_id"])
    for source_id, lexical_row in lexical_by_source.items():
        reading_id = lexical_row["v96_reading_id"]
        if reading_id not in complete_by_reading:
            continue
        row = complete_by_reading[reading_id]
        check("dictionary", row["working_meaning_de"] == lexical_row["v96_lexical_core_de"], source_id)
        check("dictionary", row["working_model_score_0_100_not_probability"] == lexical_row["working_model_score_0_100_not_probability"], source_id)
        check("dictionary", row["working_model_level"] == lexical_row["working_model_level"], source_id)
        check("dictionary", row["positive_evidence_de"] == lexical_row["positive_evidence_de"], source_id)
        check("dictionary", row["counterevidence_de"] == lexical_row["counterevidence_de"], source_id)

    preserved = [
        (G722 / "V95_5_BOUND_SPAN_RENDERER.tsv", ART / "V96_5_BOUND_SPAN_RENDERER.tsv", 5),
        (G722 / "V95_5_BOUND_SPAN_EXECUTION_AUDIT.tsv", ART / "V96_5_BOUND_SPAN_EXECUTION_AUDIT.tsv", 5),
        (G722 / "V95_2_ONE_SHOT_RENDER_DIRECTIVES.tsv", ART / "V96_2_ONE_SHOT_RENDER_DIRECTIVES.tsv", 2),
        (G722 / "V95_8_F7R2_RENDERED_UNITS.tsv", ART / "V96_8_F7R2_RENDERED_UNITS.tsv", 8),
    ]
    for source, target, expected_rows in preserved:
        check("preserved", file_sha(source) == file_sha(target), target.name)
        check("preserved", len(read_tsv(target)) == expected_rows, target.name)

    check("result", result["experiment_id"] == "GDT723")
    check("result", result["status"] == EXPECTED_STATUS)
    check("result", result["target_readings"] == 12)
    check("result", result["target_positions"] == 12)
    check("result", result["target_pages"] == 10)
    check("result", result["primary_evidence_bindings"] == 61)
    check("result", result["earlier_exact_o_ckh_grid_rows"] == 1)
    check("result", result["earlier_boundary_seed_head_rows"] == 1)
    check("result", result["action_positions_with_lexical_action_separation"] == 3)
    check("result", result["nominal_positions_without_hidden_action"] == 9)
    check("result", result["component_global_exports"] == 0)
    check("result", result["score_delta_total"] == 0)
    check("result", result["remaining_unreviewed_weak_readings"] == 35)
    check("result", result["complete_dictionary_rows_with_default_confidence_and_evidence"] == 1586)
    check("result", result["f84_or_f84r_used"] == 0)

    report = (EXP / "REPORT.md").read_text(encoding="utf-8")
    check("report", EXPECTED_STATUS in report)
    check("report", "trockene Mischung, Anfangsstufe" in report)
    check("report", "Samenmaterial; bis zur Mittelstufe getrocknet" in report)
    check("report", "warme Trockenmischung" in report and "kalte Trockenmischung" in report)
    check("report", "35" in report)
    check("report", "f84" in report and "f84r" in report)

    all_pages = {row["expected_page"] for row in specs}
    check("sealed", all(not page.lower().startswith("f84") for page in all_pages))
    check("sealed", all("f84" not in row["evidence_path"].lower() for row in evidence))
    manifest = json.loads((EXP / "experiment.json").read_text(encoding="utf-8"))
    check("sealed", manifest["sealed_data"] == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"})
    check("sealed", manifest["experiment_id"] == "GDT723")

    validation = {
        "experiment_id": "GDT723",
        "status": "PASS",
        "checks_passed": sum(checks.values()),
        "check_groups": dict(sorted(checks.items())),
        "target_readings": 12,
        "target_positions": 12,
        "primary_evidence_bindings_replayed": 61,
        "upstream_scope_states": {"KNOWN_EXACT_WHOLE": 1, "READER_BOUNDARY_UNSTABLE": 1, "UNKNOWN_SURFACE": 10},
        "action_positions_with_lexical_action_separation": 3,
        "nominal_positions_without_hidden_action": 9,
        "exact_whole_surface_defaults_allowed": 12,
        "component_global_exports": 0,
        "score_delta_total": 0,
        "remaining_unreviewed_weak_readings": 35,
        "complete_dictionary_rows_with_default_confidence_and_evidence": 1586,
        "f84_or_f84r_used": 0,
    }
    (ART / "VALIDATION.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(validation, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
