#!/usr/bin/env python3
"""Independent validator for GDT722/V95."""

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
EXP = ROOT / "experiments/yolo/gdt722_v95_op_whole_scope_and_context_separation"
SRC = EXP / "src"
ART = EXP / "artifacts"
G721 = ROOT / "experiments/yolo/gdt721_v94_four_head_construction_scope_and_b003_restore/artifacts"
HISTORICAL = "H0_NONE"
TARGET_IDS = {"op#1", "chopo#1", "qopaiin#1", "opchedaiin#1", "opchey#1"}
EXPECTED_STATUS = (
    "PASS_V95_5_OP_HOLDS_RESOLVED_AS_BOUND_WHOLE_RENDERERS__QOPAIIN_ACTION_REMOVED_FROM_"
    "LEXICAL_CORE__OPCHEY_26_PLUS_4_FORMAL_FAMILY__NO_INTERNAL_P_EXPORT__47_WEAK_"
    "READINGS_REMAIN__NO_SCORE_CREDIT__ALL_H0_NONE"
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
    return hashlib.sha256(
        json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    checks: Counter[str] = Counter()

    def check(group: str, condition: bool, detail: Any = "") -> None:
        assert condition, (group, detail)
        checks[group] += 1

    specs = read_tsv(SRC / "V95_5_AUDIT_SPECS.tsv")
    bindings_source = read_tsv(SRC / "V95_36_PRIMARY_EVIDENCE_BINDINGS.tsv")
    lexical = read_tsv(ART / "V95_324_ACTIVE_LEXICAL_READINGS.tsv")
    contexts = read_tsv(ART / "V95_479_CONTEXT_REALIZATIONS.tsv")
    census = read_tsv(ART / "V95_52_HELD_READING_AUDIT.tsv")
    delta = read_tsv(ART / "V95_5_OP_CORE_CONTEXT_DELTA.tsv")
    scope = read_tsv(ART / "V95_4_OP_SCOPE_DICTIONARY.tsv")
    rivals = read_tsv(ART / "V95_15_RIVAL_MODEL_COMPARISON.tsv")
    evidence = read_tsv(ART / "V95_36_PRIMARY_EVIDENCE_BINDINGS.tsv")
    upstream = read_tsv(ART / "V95_5_UPSTREAM_UNKNOWN_POSITION_AUDIT.tsv")
    formal = read_tsv(ART / "V95_1_FORMAL_E_RUN_FAMILY.tsv")
    renderer = read_tsv(ART / "V95_5_TARGET_RENDERER.tsv")
    complete = read_tsv(ART / "V95_COMPLETE_WORD_CONFIDENCE.tsv")
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))

    check("counts", len(specs) == 5)
    check("counts", {row["source_reading_id"] for row in specs} == TARGET_IDS)
    check("counts", len(lexical) == 324)
    check("counts", len(contexts) == 479)
    check("counts", len(census) == 52)
    check("counts", len(delta) == 5)
    check("counts", len(scope) == 4)
    check("counts", len(rivals) == 15)
    check("counts", len(evidence) == 36)
    check("counts", len(upstream) == 5)
    check("counts", len(formal) == 1)
    check("counts", len(renderer) == 5)
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
        check("target_lexical", row["surface"] == spec["surface"], source_id)
        check("target_lexical", row["v95_lexical_core_de"] == spec["v95_lexical_core_de"], source_id)
        check("target_lexical", row["v95_context_realizations_de"] == spec["v95_context_realization_de"], source_id)
        check("target_lexical", row["decomposition"] == spec["decomposition"], source_id)
        check("target_lexical", row["working_model_score_0_100_not_probability"] == "30", source_id)
        check("target_lexical", row["working_model_level"] == "W1_WEAK_WORKING", source_id)
        check("target_lexical", row["context_realization_score_0_100_not_probability"] == "30", source_id)
        check("target_lexical", row["v95_component_global_export_allowed"] == "0", source_id)
        check("target_lexical", row["global_export_scope"] == "ACTIVE_WORKING_DEFAULT", source_id)
        check("target_lexical", row["unconditional_global_export_allowed"] == "1", source_id)
        check("target_lexical", row["last_semantic_writer"] == "GDT722", source_id)
        check("target_lexical", "GDT722" in split_pipe(row["source_gdts"]), source_id)
        check("target_lexical", row["historical_confirmation"] == HISTORICAL, source_id)
    check(
        "target_lexical",
        lexical_by_source["qopaiin#1"]["v95_lexical_core_de"] == "drei Teile Pulverzubereitung",
    )
    check(
        "target_lexical",
        "nehmen" not in lexical_by_source["qopaiin#1"]["v95_lexical_core_de"].lower(),
    )
    check(
        "target_lexical",
        "nehmen" in lexical_by_source["qopaiin#1"]["v95_context_realizations_de"].lower(),
    )

    source_lexical = read_tsv(G721 / "V94_324_ACTIVE_LEXICAL_READINGS.tsv")
    check("lexical_parity", len(source_lexical) == len(lexical))
    for source, target in zip(source_lexical, lexical, strict=True):
        source_ids = split_pipe(source["source_reading_ids"])
        check("lexical_parity", source["surface"] == target["surface"], source["surface"])
        check("lexical_parity", source["source_reading_ids"] == target["source_reading_ids"], source["surface"])
        if not any(source_id in TARGET_IDS for source_id in source_ids):
            check("lexical_parity", source["v94_lexical_core_de"] == target["v95_lexical_core_de"], source["surface"])
            check("lexical_parity", source["v94_context_realizations_de"] == target["v95_context_realizations_de"], source["surface"])
            check("lexical_parity", source["working_model_score_0_100_not_probability"] == target["working_model_score_0_100_not_probability"], source["surface"])
            check("lexical_parity", source["working_model_level"] == target["working_model_level"], source["surface"])
            check("lexical_parity", target["v95_audit_decision"] == "NOT_IN_GDT722_TRANCHE", source["surface"])

    context_by_position = {row["position_id"]: row for row in contexts}
    check("context_index", len(context_by_position) == 479)
    for source_id, spec in spec_by_id.items():
        row = context_by_position[spec["expected_position_id"]]
        check("target_context", row["source_reading_id"] == source_id, source_id)
        check("target_context", row["surface"] == spec["surface"], source_id)
        check("target_context", row["page"] == spec["expected_page"], source_id)
        check("target_context", row["locus"] == spec["expected_locus"], source_id)
        check("target_context", row["token_ordinal"] == spec["expected_token_ordinal"], source_id)
        check("target_context", row["v95_lexical_core_de"] == spec["v95_lexical_core_de"], source_id)
        check("target_context", row["v95_context_realization_de"] == spec["v95_context_realization_de"], source_id)
        check("target_context", row["v95_expected_left_surface"] == spec["expected_left_surface"], source_id)
        check("target_context", row["v95_expected_right_surface"] == spec["expected_right_surface"], source_id)
        check("target_context", row["v68_action_license"] == spec["expected_action_license"], source_id)
        check("target_context", row["v95_component_global_export_allowed"] == "0", source_id)
        check("target_context", row["v95_global_export_scope"] == "ACTIVE_WORKING_DEFAULT", source_id)
        check("target_context", row["v95_unconditional_global_export_allowed"] == "1", source_id)

    source_context = read_tsv(G721 / "V94_479_CONTEXT_REALIZATIONS.tsv")
    check("context_parity", len(source_context) == len(contexts))
    for source, target in zip(source_context, contexts, strict=True):
        check("context_parity", source["position_id"] == target["position_id"], source["position_id"])
        check("context_parity", source["surface"] == target["surface"], source["position_id"])
        check("context_parity", source["source_reading_id"] == target["source_reading_id"], source["position_id"])
        if source["source_reading_id"] not in TARGET_IDS:
            check("context_parity", source["v94_lexical_core_de"] == target["v95_lexical_core_de"], source["position_id"])
            check("context_parity", source["v94_context_realization_de"] == target["v95_context_realization_de"], source["position_id"])
            check("context_parity", target["v95_audit_decision"] == "NOT_IN_GDT722_TRANCHE", source["position_id"])

    dispositions = Counter(row["disposition"] for row in census)
    check("census", dispositions == Counter({"HELD_FOR_LATER_REPAIR": 47, "REVISED_IN_V95": 5}))
    revised = {row["source_reading_id"]: row for row in census if row["disposition"] == "REVISED_IN_V95"}
    check("census", set(revised) == TARGET_IDS)
    for source_id, row in revised.items():
        check("census", row["v95_lexical_core_de"] == spec_by_id[source_id]["v95_lexical_core_de"], source_id)
        check("census", row["new_lexical_score"] == "30", source_id)
        check("census", row["new_lexical_level"] == "W1_WEAK_WORKING", source_id)

    for row in delta:
        source_id = row["source_reading_id"]
        check("delta", source_id in TARGET_IDS, source_id)
        check("delta", row["surface"] == spec_by_id[source_id]["surface"], source_id)
        check("delta", row["v95_lexical_core_de"] == spec_by_id[source_id]["v95_lexical_core_de"], source_id)
        check("delta", row["v95_context_realization_de"] == spec_by_id[source_id]["v95_context_realization_de"], source_id)
        check("delta", row["v95_score"] == row["old_score"] == "30", source_id)
        check("delta", row["score_credit_family_ids"] == "NONE", source_id)
        check("delta", row["component_global_export_allowed"] == "0", source_id)

    evidence_by_id = {row["binding_id"]: row for row in evidence}
    check("bindings", len(evidence_by_id) == 36)
    check("bindings", {row["binding_id"] for row in bindings_source} == set(evidence_by_id))
    for binding in bindings_source:
        row = evidence_by_id[binding["binding_id"]]
        check("bindings", row["source_reading_id"] == binding["source_reading_id"], binding["binding_id"])
        check("bindings", row["score_credit_family_ids"] == "NONE", binding["binding_id"])
        check("bindings", "f84" not in row["evidence_path"].lower(), binding["binding_id"])
        selector = parse_assertions(binding["selector"])
        assertions = parse_assertions(binding["field_assertions"])
        contains = parse_assertions(binding["field_contains_assertions"])
        matches = [
            source for source in read_tsv(ROOT / binding["evidence_path"])
            if all(source.get(field) == expected for field, expected in selector.items())
        ]
        check("bindings", len(matches) == 1, binding["binding_id"])
        source = matches[0]
        for field, expected in assertions.items():
            check("assertions", source.get(field) == expected, (binding["binding_id"], field))
        for field, expected in contains.items():
            check("assertions", expected in split_pipe(source.get(field, "")), (binding["binding_id"], field))
        check("fingerprints", row["matched_row_fingerprint_sha256"] == fingerprint(source), binding["binding_id"])
        check("fingerprints", row["source_row_match"] == "1", binding["binding_id"])
        check("fingerprints", row["evidence_status"] == "BOUND_EXACT_PRIMARY_ROW", binding["binding_id"])

    rival_by_target: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rivals:
        rival_by_target[row["source_reading_id"]].append(row)
        check("rivals", row["score_credit"] == "0", row["source_reading_id"])
        check("rivals", row["component_global_export_allowed"] == "0", row["source_reading_id"])
    check("rivals", set(rival_by_target) == TARGET_IDS)
    for source_id, rows in rival_by_target.items():
        check("rivals", {row["model_id"] for row in rows} == {
            "A_BOUND_WHOLE_RENDERER_NO_COMPONENT_EXPORT", "B_INTERNAL_P_COMPOSITION", "C_UNRELATED_LEXEME_OR_FORMULA"
        }, source_id)
        selected = [row for row in rows if row["portable_default_selected"] == "1"]
        check("rivals", len(selected) == 1 and selected[0]["model_id"] == "A_BOUND_WHOLE_RENDERER_NO_COMPONENT_EXPORT", source_id)
    chopo_b = next(row for row in rivals if row["source_reading_id"] == "chopo#1" and row["model_id"] == "B_INTERNAL_P_COMPOSITION")
    check("rivals", chopo_b["decision"] == "REJECT_UNPAID_RESIDUE")

    scope_by_id = {row["scope_item"]: row for row in scope}
    check("scope", set(scope_by_id) == {
        "P_INITIAL", "OP_BOUND_WHOLE_RENDERER_GROUP", "OPCH_E_RUN_FORMAL_FAMILY", "QOPAIIN_CONTEXT_ACTION"
    })
    for row in scope:
        check("scope", row["score_credit"] == "0", row["scope_item"])
        check("scope", row["component_or_substring_global_export_allowed"] == "0", row["scope_item"])
        check("scope", row["historical_confirmation"] == HISTORICAL, row["scope_item"])
    check("scope", "INNER_P" in scope_by_id["P_INITIAL"]["forbidden_scope"])
    check("scope", scope_by_id["P_INITIAL"]["exact_whole_surface_default_allowed"] == "0")
    check("scope", scope_by_id["OP_BOUND_WHOLE_RENDERER_GROUP"]["exact_whole_surface_default_allowed"] == "1")
    check("scope", scope_by_id["OP_BOUND_WHOLE_RENDERER_GROUP"]["component_or_substring_global_export_allowed"] == "0")
    check("scope", scope_by_id["OPCH_E_RUN_FORMAL_FAMILY"]["exact_whole_surface_default_allowed"] == "0")
    check("scope", scope_by_id["QOPAIIN_CONTEXT_ACTION"]["exact_whole_surface_default_allowed"] == "0")
    check("scope", "26" in scope_by_id["OPCH_E_RUN_FORMAL_FAMILY"]["allowed_scope"])
    check("scope", "P158" in scope_by_id["QOPAIIN_CONTEXT_ACTION"]["allowed_scope"])

    check("formal", formal[0]["family_id"] == "G633-EB0201")
    check("formal", formal[0]["skeleton"] == "opch<E>y")
    check("formal", formal[0]["occurrences_by_length"] == "1:26|2:4")
    check("formal", formal[0]["v95_semantic_decision"] == "FORMAL_FAMILY_ONLY_NO_COMPONENT_SEMANTICS")
    check("formal", formal[0]["component_global_export_allowed"] == "0")
    source_formal = next(row for row in read_tsv(ROOT / "experiments/yolo/gdt633_cth_interfix_semantic_contrasts/artifacts/LITERAL_E_RUN_BACKGROUND.tsv") if row["family_id"] == "G633-EB0201")
    for field in source_formal:
        check("formal", formal[0][field] == source_formal[field], field)

    upstream_source = read_tsv(ROOT / "experiments/yolo/gdt652_strict_v28_frontier_completion/artifacts/ALL_LINE_CONCRETE_COVERAGE_V29.tsv")
    for row in upstream:
        source_id = row["source_reading_id"]
        spec = spec_by_id[source_id]
        matches = [source for source in upstream_source if source["page"] == row["page"] and source["locus"] == row["locus"]]
        check("upstream", len(matches) == 1, source_id)
        check("upstream", row["surface"] in split_pipe(matches[0]["unknown_surfaces"]), source_id)
        check("upstream", row["gdt652_scope_state"] == "UNKNOWN_SURFACE", source_id)
        check("upstream", row["gdt691_route"] == "LEARNED_WHOLE_OR_UNEXPORTED", source_id)
        check("upstream", row["v95_selected_model"] == "A_BOUND_WHOLE_RENDERER_NO_COMPONENT_EXPORT", source_id)
        check("upstream", row["token_ordinal"] == spec["expected_token_ordinal"], source_id)

    renderer_by_surface = {row["surface"]: row for row in renderer}
    check("renderer", set(renderer_by_surface) == {row["surface"] for row in specs})
    for spec in specs:
        row = renderer_by_surface[spec["surface"]]
        check("renderer", row["position_id"] == spec["expected_position_id"], spec["surface"])
        check("renderer", row["portable_lexical_core_de"] == spec["v95_lexical_core_de"], spec["surface"])
        check("renderer", row["local_context_realization_de"] == spec["v95_context_realization_de"], spec["surface"])
        check("renderer", row["selected_model"] == "A_BOUND_WHOLE_RENDERER_NO_COMPONENT_EXPORT", spec["surface"])
        check("renderer", row["component_global_export_allowed"] == "0", spec["surface"])
        check("renderer", row["score"] == "30" and row["level"] == "W1_WEAK_WORKING", spec["surface"])

    levels = Counter(row["working_model_level"] for row in lexical)
    check("dictionary", levels == Counter({
        "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY": 7,
        "W1_WEAK_WORKING": 135,
        "W2_PROVISIONAL_WORKING": 163,
        "W3_SOLID_WORKING_THEORY": 19,
    }))
    active_complete = [row for row in complete if row["current_layer"] == "ACTIVE_V95_LEXICAL_CORE"]
    check("dictionary", len(active_complete) == 324)
    complete_by_reading = {row["reading_id"]: row for row in active_complete}
    for row in complete:
        check("complete", bool(row["working_meaning_de"]), row["reading_id"])
        score = int(row["working_model_score_0_100_not_probability"])
        check("complete", row["working_model_level"] == level(score), row["reading_id"])
        check("complete", bool(row["positive_evidence_de"]), row["reading_id"])
        check("complete", bool(row["counterevidence_de"]), row["reading_id"])
        check("complete", row["historical_confirmation"] == HISTORICAL, row["reading_id"])
    for source_id, lexical_row in lexical_by_source.items():
        if lexical_row["v95_reading_id"] not in complete_by_reading:
            continue
        row = complete_by_reading[lexical_row["v95_reading_id"]]
        check("dictionary", row["working_meaning_de"] == lexical_row["v95_lexical_core_de"], source_id)
        check("dictionary", row["working_model_level"] == lexical_row["working_model_level"], source_id)

    preserved = [
        (G721 / "V94_5_BOUND_SPAN_RENDERER.tsv", ART / "V95_5_BOUND_SPAN_RENDERER.tsv", 5),
        (G721 / "V94_5_BOUND_SPAN_EXECUTION_AUDIT.tsv", ART / "V95_5_BOUND_SPAN_EXECUTION_AUDIT.tsv", 5),
        (G721 / "V94_2_ONE_SHOT_RENDER_DIRECTIVES.tsv", ART / "V95_2_ONE_SHOT_RENDER_DIRECTIVES.tsv", 2),
        (G721 / "V94_8_F7R2_RENDERED_UNITS.tsv", ART / "V95_8_F7R2_RENDERED_UNITS.tsv", 8),
    ]
    for source, target, expected_rows in preserved:
        check("preserved", file_sha(source) == file_sha(target), target.name)
        check("preserved", len(read_tsv(target)) == expected_rows, target.name)

    check("result", result["experiment_id"] == "GDT722")
    check("result", result["status"] == EXPECTED_STATUS)
    check("result", result["target_readings"] == 5)
    check("result", result["target_positions"] == 5)
    check("result", result["target_pages"] == 4)
    check("result", result["primary_evidence_bindings"] == 36)
    check("result", result["bounded_unsegmented_renderers_selected"] == 5)
    check("result", result["lexical_context_separations"] == 1)
    check("result", result["internal_p_decompositions_selected"] == 0)
    check("result", result["component_global_exports"] == 0)
    check("result", result["score_delta_total"] == 0)
    check("result", result["remaining_unreviewed_weak_readings"] == 47)
    check("result", result["complete_dictionary_rows_with_default_confidence_and_evidence"] == 1586)
    check("result", result["f84_or_f84r_used"] == 0)

    report = (EXP / "REPORT.md").read_text(encoding="utf-8")
    check("report", EXPECTED_STATUS in report)
    check("report", "drei Teile Pulverzubereitung" in report)
    check("report", "drei Teile der Pulverzubereitung nehmen" in report)
    check("report", "858 Token mit innerem `p`" in report)
    check("report", "opchey   26 Vorkommen" in report)
    check("report", "opcheey   4 Vorkommen" in report)
    check("report", "47" in report)
    check("report", "exakten Ganzoberflächen" in report)
    check("report", "f84" in report and "f84r" in report)

    all_pages = {row["expected_page"] for row in specs}
    check("sealed", all(not page.lower().startswith("f84") for page in all_pages))
    check("sealed", all("f84" not in row["evidence_path"].lower() for row in evidence))
    manifest = json.loads((EXP / "experiment.json").read_text(encoding="utf-8"))
    check("sealed", manifest["sealed_data"] == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"})

    validation = {
        "experiment_id": "GDT722", "status": "PASS", "checks_passed": sum(checks.values()),
        "check_groups": dict(sorted(checks.items())), "target_readings": 5, "target_positions": 5,
        "primary_evidence_bindings_replayed": 36, "bounded_unsegmented_renderers_selected": 5,
        "lexical_context_separations": 1, "internal_p_decompositions_selected": 0,
        "component_global_exports": 0, "score_delta_total": 0,
        "formal_e_run_families": 1, "remaining_unreviewed_weak_readings": 47,
        "complete_dictionary_rows_with_default_confidence_and_evidence": 1586,
        "f84_or_f84r_used": 0,
    }
    (ART / "VALIDATION.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
