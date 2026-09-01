#!/usr/bin/env python3
"""Independent validator for GDT721/V94."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt721_v94_four_head_construction_scope_and_b003_restore"
SRC = EXP / "src"
ART = EXP / "artifacts"
G720 = ROOT / "experiments/yolo/gdt720_v93_cold_result_whole_domain_repair/artifacts"
G695 = ROOT / "experiments/yolo/gdt695_fixed_v67_clause_realization/artifacts"
STATUS = (
    "PASS_V94_4_HEAD_READINGS_REPAIRED__POL_POWDER_MATERIAL__LOR_WOOD_PORTION__"
    "L_R_ACTIVE_OCCURRENCES_BOUND__3_LEGACY_SPANS_RESTORED__52_WEAK_READINGS_REMAIN__"
    "NO_SCORE_CREDIT__ALL_H0_NONE"
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def parse_assertions(value: str) -> dict[str, str]:
    output: dict[str, str] = {}
    for part in value.split(";"):
        if part:
            field, expected = part.split("=", 1)
            assert field and field not in output
            output[field] = expected
    return output


def rename_v93(row: dict[str, str]) -> dict[str, str]:
    return {key.replace("v93", "v94").replace("V93", "V94"): value for key, value in row.items()}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    groups: Counter[str] = Counter()

    def check(condition: bool, group: str, message: str) -> None:
        if not condition:
            raise AssertionError(f"{group}: {message}")
        groups[group] += 1

    specs = read_tsv(SRC / "V94_4_AUDIT_SPECS.tsv")
    bindings = read_tsv(SRC / "V94_30_PRIMARY_EVIDENCE_BINDINGS.tsv")
    bound = read_tsv(ART / "V94_30_PRIMARY_EVIDENCE_BINDINGS.tsv")
    source_lex = read_tsv(G720 / "V93_324_ACTIVE_LEXICAL_READINGS.tsv")
    target_lex = read_tsv(ART / "V94_324_ACTIVE_LEXICAL_READINGS.tsv")
    source_ctx = read_tsv(G720 / "V93_479_CONTEXT_REALIZATIONS.tsv")
    target_ctx = read_tsv(ART / "V94_479_CONTEXT_REALIZATIONS.tsv")
    census = read_tsv(ART / "V94_56_HELD_READING_AUDIT.tsv")
    delta = read_tsv(ART / "V94_4_HEAD_CORE_CONTEXT_DELTA.tsv")
    construction = read_tsv(ART / "V94_5_SCOPED_CONSTRUCTION_DICTIONARY.tsv")
    rivals = read_tsv(ART / "V94_12_RIVAL_MODEL_COMPARISON.tsv")
    spans = read_tsv(ART / "V94_5_BOUND_SPAN_RENDERER.tsv")
    span_execution = read_tsv(ART / "V94_5_BOUND_SPAN_EXECUTION_AUDIT.tsv")
    span_audit = read_tsv(ART / "V94_3_LEGACY_SPAN_RESTORE_AUDIT.tsv")
    complete = read_tsv(ART / "V94_COMPLETE_WORD_CONFIDENCE.tsv")
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))

    expected = {
        "pol#1": {
            "surface": "pol", "core": "Pulverstoff", "context": "Pulverstoff",
            "position": "P267", "page": "f77r", "locus": "f77r.38", "ordinal": "1", "left": "<BOS>",
            "score": "31", "family": "GDT635_FOUR_HEAD_OL_GRID",
            "decomposition": "P_INITIAL_POWDER + OL_MATERIAL_BODY",
            "scope": "SCOPED_PRODUCTIVE_HEAD_COMPOSITION", "export": "ACTIVE_WORKING_DEFAULT",
            "bound": "NONE", "unconditional": "1", "occurrence_span": "NONE", "occurrence_role": "NONE",
        },
        "lor#1": {
            "surface": "lor", "core": "Holzportion", "context": "Holzportion",
            "position": "P079", "page": "f107r", "locus": "f107r.2", "ordinal": "13", "left": "qeeey",
            "score": "31", "family": "GDT635_FOUR_HEAD_OR_GRID|GDT693_OR_PORTION_CONTROL",
            "decomposition": "L_INITIAL_WOOD + OR_PORTION_BODY",
            "scope": "SCOPED_PRODUCTIVE_HEAD_COMPOSITION", "export": "ACTIVE_WORKING_DEFAULT",
            "bound": "NONE", "unconditional": "1", "occurrence_span": "NONE", "occurrence_role": "NONE",
        },
        "l#1": {
            "surface": "l", "core": "Holz / holziger Pflanzenteil (nur als Kompositionskopf)",
            "context": "keine Einzelausgabe; Gesamtspan l|karchees: vollständig getrocknete Charge aus Anteil I der erhitzten Holzdroge",
            "position": "P435", "page": "f86v6", "locus": "f86v6.4", "ordinal": "10", "left": "chdar",
            "score": "32", "family": "GDT635_L_INITIAL_WOOD_HEAD",
            "decomposition": "L_INITIAL_WOOD_HEAD__ACTIVE_TOKEN_CONSUMED_BY_B003",
            "scope": "SCOPED_INITIAL_HEAD_PRIOR_WITH_BOUND_ACTIVE_OCCURRENCE", "export": "BOUND_SPAN_ONLY_NO_GLOBAL_EXPORT",
            "bound": "B003", "unconditional": "0", "occurrence_span": "B003", "occurrence_role": "LEFT",
        },
        "r#1": {
            "surface": "r", "core": "Wurzel / Wurzeldroge (nur als Kompositionskopf)",
            "context": "keine Einzelausgabe; Gesamtspan keo|r: heiße Portion",
            "position": "P289", "page": "f7r", "locus": "f7r.2", "ordinal": "3", "left": "keo",
            "score": "31", "family": "GDT635_R_INITIAL_ROOT_HEAD",
            "decomposition": "R_INITIAL_ROOT_HEAD__ACTIVE_TOKEN_CONSUMED_BY_G678_KEO_R_F7R2",
            "scope": "SCOPED_INITIAL_HEAD_PRIOR_WITH_BOUND_ACTIVE_OCCURRENCE", "export": "BOUND_SPAN_ONLY_NO_GLOBAL_EXPORT",
            "bound": "G678_KEO_R_F7R2", "unconditional": "0", "occurrence_span": "G678_KEO_R_F7R2", "occurrence_role": "RIGHT",
        },
    }

    check(len(specs) == 4, "spec", "four specs")
    check({row["source_reading_id"] for row in specs} == set(expected), "spec", "target ids")
    for row in specs:
        exp = expected[row["source_reading_id"]]
        check(row["v94_lexical_core_de"] == exp["core"], "spec", f"{row['source_reading_id']} core")
        check(row["v94_context_realization_de"] == exp["context"], "spec", f"{row['source_reading_id']} context")
        check(row["family_ids"] == exp["family"], "spec", f"{row['source_reading_id']} family")
        check(row["decomposition"] == exp["decomposition"], "spec", f"{row['source_reading_id']} decomposition")
        check(row["score_credit_family_ids"] == "NONE" and row["score_delta_lexical_core"] == "0", "score", f"{row['source_reading_id']} no credit")
        check(row["target_semantic_scope"] == exp["scope"], "scope", f"{row['source_reading_id']} scope")
        check(row["target_global_export_scope"] == exp["export"], "scope", f"{row['source_reading_id']} export")
        check(row["target_bound_span_ids"] == exp["bound"], "scope", f"{row['source_reading_id']} bound")
        check(row["target_unconditional_global_export_allowed"] == exp["unconditional"], "scope", f"{row['source_reading_id']} unconditional")
        check(row["component_global_export_allowed"] == "0", "scope", f"{row['source_reading_id']} component")
        check(not row["expected_page"].lower().startswith("f84"), "sealed", f"{row['source_reading_id']} page")

    check(len(bindings) == len(bound) == 30, "bindings", "thirty bindings")
    check(Counter(row["source_reading_id"] for row in bindings) == Counter({"pol#1": 8, "lor#1": 10, "l#1": 6, "r#1": 6}), "bindings", "distribution")
    bound_by_id = {row["binding_id"]: row for row in bound}
    check(len(bound_by_id) == 30, "bindings", "binding ids unique")
    for binding in bindings:
        check("f84" not in binding["evidence_path"].lower(), "sealed", f"{binding['binding_id']} path")
        selector = parse_assertions(binding["selector"])
        assertions = parse_assertions(binding["field_assertions"])
        check(all(not value.lower().startswith("f84") for value in selector.values()), "sealed", f"{binding['binding_id']} selector")
        matches = [
            row for row in read_tsv(ROOT / binding["evidence_path"])
            if all(row.get(field) == expected_value for field, expected_value in selector.items())
        ]
        check(len(matches) == 1, "bindings", f"{binding['binding_id']} unique source")
        source = matches[0]
        for field, expected_value in assertions.items():
            check(source.get(field) == expected_value, "assertions", f"{binding['binding_id']} {field}")
        fingerprint = hashlib.sha256(
            json.dumps(source, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        output = bound_by_id[binding["binding_id"]]
        check(output["matched_row_fingerprint_sha256"] == fingerprint, "fingerprints", binding["binding_id"])
        check(output["source_row_match"] == "1" and output["evidence_status"] == "BOUND_EXACT_PRIMARY_ROW", "bindings", f"{binding['binding_id']} status")
        check(output["score_credit_family_ids"] == "NONE", "score", f"{binding['binding_id']} no credit")
        check(output["historical_confirmation"] == "H0_NONE", "history", binding["binding_id"])

    source_lex_by_surface = {row["surface"]: row for row in source_lex}
    target_lex_by_surface = {row["surface"]: row for row in target_lex}
    check(len(source_lex) == len(target_lex) == 324, "counts", "lexical rows")
    check(set(source_lex_by_surface) == set(target_lex_by_surface), "lexical_parity", "surface set")
    target_surfaces = {item["surface"] for item in expected.values()}
    lexical_exceptions = {
        "v94_audit_decision", "v94_evidence_class", "v94_open_semantic_slots",
        "v94_component_global_export_allowed", "v94_prior_lexical_core_de",
    }
    for surface, source in source_lex_by_surface.items():
        output = target_lex_by_surface[surface]
        if surface in target_surfaces:
            exp = expected[output["source_reading_ids"]]
            check(output["v94_lexical_core_de"] == exp["core"], "target_lexical", f"{surface} core")
            check(output["v94_context_realizations_de"] == exp["context"], "target_lexical", f"{surface} context")
            check(output["family_ids"] == exp["family"] and output["decomposition"] == exp["decomposition"], "target_lexical", f"{surface} composition")
            check(output["semantic_scope"] == exp["scope"] and output["global_export_scope"] == exp["export"], "scope", f"{surface} scope")
            check(output["bound_span_ids"] == exp["bound"] and output["unconditional_global_export_allowed"] == exp["unconditional"], "scope", f"{surface} bound export")
            check(output["last_semantic_writer"] == "GDT721", "target_lexical", f"{surface} writer")
            check(output["working_model_score_0_100_not_probability"] == exp["score"] and output["working_model_level"] == "W1_WEAK_WORKING", "score", f"{surface} unchanged")
            check(output["score_delta_lexical_core"] == "0" and output["v94_component_global_export_allowed"] == "0", "score", f"{surface} no delta/export")
        else:
            renamed = rename_v93(source)
            for field, value in renamed.items():
                if field not in lexical_exceptions:
                    check(output.get(field) == value, "lexical_parity", f"{surface} {field}")

    source_ctx_by_position = {row["position_id"]: row for row in source_ctx}
    target_ctx_by_position = {row["position_id"]: row for row in target_ctx}
    check(len(source_ctx) == len(target_ctx) == 479, "counts", "context rows")
    check(set(source_ctx_by_position) == set(target_ctx_by_position), "context_parity", "position set")
    target_positions = {item["position"] for item in expected.values()}
    context_exceptions = {
        "v94_audit_decision", "v94_evidence_class", "v94_open_semantic_slots",
        "v94_component_global_export_allowed", "v94_local_context_hypothesis", "v94_expected_left_surface",
    }
    for position_id, source in source_ctx_by_position.items():
        output = target_ctx_by_position[position_id]
        if position_id in target_positions:
            exp = next(value for value in expected.values() if value["position"] == position_id)
            check(output["surface"] == exp["surface"], "target_context", f"{position_id} surface")
            check(output["v94_lexical_core_de"] == exp["core"] and output["v94_context_realization_de"] == exp["context"], "target_context", f"{position_id} meanings")
            check((output["page"], output["locus"], output["token_ordinal"]) == (exp["page"], exp["locus"], exp["ordinal"]), "target_context", f"{position_id} locus")
            check(output["v94_expected_left_surface"] == exp["left"], "target_context", f"{position_id} left")
            check(output["v94_occurrence_bound_span_id"] == exp["occurrence_span"] and output["v94_occurrence_bound_span_role"] == exp["occurrence_role"], "scope", f"{position_id} occurrence span")
            check(output["v94_global_export_scope"] == exp["export"] and output["v94_unconditional_global_export_allowed"] == exp["unconditional"], "scope", f"{position_id} export")
            check(output["v68_clause_type"] == "NOMINAL_BLOCK" and output["v68_action_license"] == "NOT_ACTION_LICENSED", "target_context", f"{position_id} nominal")
        else:
            renamed = rename_v93(source)
            for field, value in renamed.items():
                if field not in context_exceptions:
                    check(output.get(field) == value, "context_parity", f"{position_id} {field}")

    check(len(census) == 56, "census", "audit rows")
    check(Counter(row["disposition"] for row in census) == Counter({"HELD_FOR_LATER_REPAIR": 52, "REVISED_IN_V94": 4}), "census", "dispositions")
    check({row["source_reading_id"] for row in census if row["disposition"] == "REVISED_IN_V94"} == set(expected), "census", "revised ids")
    check(len(delta) == 4, "delta", "four rows")
    for row in delta:
        exp = expected[row["source_reading_id"]]
        check(row["v94_lexical_core_de"] == exp["core"], "delta", f"{row['source_reading_id']} core")
        check(row["old_score"] == row["v94_score"] == exp["score"], "score", f"{row['source_reading_id']} unchanged")
        check(row["score_credit_family_ids"] == "NONE" and row["component_global_export_allowed"] == "0", "score", f"{row['source_reading_id']} no credit/export")

    expected_atoms = {
        "P_INITIAL": "Pulver / Pulverform", "L_INITIAL": "Holz / holziger Pflanzenteil",
        "R_INITIAL": "Wurzel / Wurzeldroge", "OL_BODY": "Stoff / Material", "OR_BODY": "Teil / Portion",
    }
    check(len(construction) == 5, "construction", "five atoms")
    check({row["construction_atom"]: row["working_value_de"] for row in construction} == expected_atoms, "construction", "values")
    for row in construction:
        check(row["score_credit"] == "0" and row["global_export_allowed"] == "0", "construction", f"{row['construction_atom']} scoped")
        check(bool(row["productive_predictions"] and row["evidence_summary_de"]), "construction", f"{row['construction_atom']} predictive evidence")
        check("historical_analogue" not in row and bool(row["working_mnemonic_not_historical_evidence"]), "construction", f"{row['construction_atom']} mnemonic separated")
        check(row["historical_confirmation"] == "H0_NONE", "history", row["construction_atom"])

    check(len(rivals) == 12, "rivals", "twelve rows")
    check(Counter(row["source_reading_id"] for row in rivals) == Counter({key: 3 for key in expected}), "rivals", "three models each")
    check(Counter(row["portable_default_selected"] for row in rivals) == Counter({"0": 8, "1": 4}), "rivals", "one selected each")
    for row in rivals:
        check(row["score_credit"] == "0", "score", f"rival {row['source_reading_id']} {row['model_id']}")

    source_spans = read_tsv(G720 / "V93_2_BOUND_SPAN_RENDERER.tsv")
    spans_by_id = {row["bound_span_id"]: row for row in spans}
    check(len(spans) == len(spans_by_id) == 5, "renderer", "five unique spans")
    check(set(spans_by_id) == {"B001", "B002", "B003", "G683_CHEOP_OL", "G678_KEO_R_F7R2"}, "renderer", "span ids")
    for source in source_spans:
        check(spans_by_id[source["bound_span_id"]] == source, "renderer", f"{source['bound_span_id']} preserved row")
    legacy_by_id = {row["span_id"]: row for row in read_tsv(G695 / "V68_3_BOUND_SPAN_FREEZE.tsv")}
    audit_by_id = {row["bound_span_id"]: row for row in span_audit}
    check(len(audit_by_id) == 3 and set(audit_by_id) == set(legacy_by_id), "renderer", "restore audit ids")
    for span_id, source in legacy_by_id.items():
        target = spans_by_id[span_id]
        audit = audit_by_id[span_id]
        check(target["locus"] == source["locus"] and f"{target['left_surface']}|{target['right_surface']}" == source["surfaces"], "renderer", f"{span_id} boundary")
        check(target["render_once_de"] == source["v68_selected_gloss_de"], "renderer", f"{span_id} exact render")
        check(target["global_export_allowed"] == "0" and target["historical_confirmation"] == "H0_NONE", "renderer", f"{span_id} scoped")
        check(audit["v93_context_reference_positions"] == "2" and audit["present_in_v93_renderer"] == "0" and audit["restored_in_v94_renderer"] == "1", "renderer", f"{span_id} restored")
        check(audit["render_byte_identical"] == "1", "renderer", f"{span_id} byte exact")
    bound_counts = Counter(row["v94_occurrence_bound_span_id"] for row in target_ctx if row["v94_occurrence_bound_span_id"] != "NONE")
    check(bound_counts == Counter({span_id: 2 for span_id in spans_by_id}), "renderer", "two context positions per span")
    check(all(row["v94_occurrence_bound_span_global_export_allowed"] == "0" for row in target_ctx if row["v94_occurrence_bound_span_id"] != "NONE"), "renderer", "all bound exports stopped")
    execution_by_id = {row["bound_span_id"]: row for row in span_execution}
    check(len(span_execution) == len(execution_by_id) == 5 and set(execution_by_id) == set(spans_by_id), "renderer", "five execution rows")
    for span_id, span in spans_by_id.items():
        execution = execution_by_id[span_id]
        check(execution["source_surfaces"] == f"{span['left_surface']}|{span['right_surface']}", "renderer", f"{span_id} execution surfaces")
        check(execution["consumed_position_ids"] == f"{span['left_position_id']}|{span['right_position_id']}", "renderer", f"{span_id} execution positions")
        check(execution["consumed_position_count"] == "2" and execution["left_role_count"] == execution["right_role_count"] == "1", "renderer", f"{span_id} execution roles")
        check(execution["standalone_outputs_suppressed"] == "2" and execution["emitted_output_units"] == "1", "renderer", f"{span_id} render once")
        check(execution["render_once_de"] == span["render_once_de"] and execution["execution_status"] == "EXECUTABLE_RENDER_ONCE", "renderer", f"{span_id} exact output")
    check(sha256(G720 / "V93_2_ONE_SHOT_RENDER_DIRECTIVES.tsv") == sha256(ART / "V94_2_ONE_SHOT_RENDER_DIRECTIVES.tsv"), "renderer", "directives byte exact")
    check(sha256(G720 / "V93_8_F7R2_RENDERED_UNITS.tsv") == sha256(ART / "V94_8_F7R2_RENDERED_UNITS.tsv"), "renderer", "f7r2 byte exact")

    check(len(complete) == 1586, "complete", "complete rows")
    check(len({row["surface"] for row in complete}) == 1582, "complete", "complete surfaces")
    for row in complete:
        check(bool(row["working_meaning_de"]), "dictionary", f"{row['reading_id']} default")
        check(bool(row["working_model_level"] and row["working_model_score_0_100_not_probability"]), "dictionary", f"{row['reading_id']} confidence")
        check(bool(row["positive_evidence_de"] and row["counterevidence_de"]), "dictionary", f"{row['reading_id']} evidence")
        check(row["historical_confirmation"] == "H0_NONE", "history", row["reading_id"])
    active_complete = {row["reading_id"]: row for row in complete if row["current_layer"] == "ACTIVE_V94_LEXICAL_CORE"}
    check(len(active_complete) == 324, "complete", "active complete rows")
    for source_id, exp in expected.items():
        check(active_complete[source_id]["working_meaning_de"] == exp["core"], "complete", f"{source_id} core")
        check(active_complete[source_id]["global_export_scope"] == exp["export"], "complete", f"{source_id} export")

    check(result["status"] == STATUS, "result", "status")
    for field, value in {
        "target_readings": 4, "target_positions": 4, "target_pages": 4,
        "primary_evidence_bindings": 30, "rival_model_rows": 12,
        "construction_atoms_retained": 5, "predicted_compound_wholes_retained": 2,
        "bound_active_occurrences_corrected": 2, "score_credit_families": 0,
        "score_delta_total": 0, "component_global_exports": 0,
        "active_lexical_rows": 324, "active_source_readings": 332, "context_positions": 479,
        "non_target_lexical_rows_preserved": 320, "non_target_context_positions_preserved": 475,
        "remaining_unreviewed_weak_readings": 52, "complete_dictionary_rows": 1586,
        "complete_dictionary_surfaces": 1582,
        "complete_dictionary_rows_with_default_confidence_and_evidence": 1586,
        "bound_spans_preserved": 2, "legacy_bound_spans_restored": 3, "bound_spans_total": 5,
        "bound_span_execution_rows": 5, "bound_positions_consumed_once": 10,
        "f7r2_output_units": 8, "f84_or_f84r_used": 0,
    }.items():
        check(result[field] == value, "result", field)
    check(result["confidence_levels"] == {
        "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY": 7,
        "W1_WEAK_WORKING": 135,
        "W2_PROVISIONAL_WORKING": 163,
        "W3_SOLID_WORKING_THEORY": 19,
    }, "result", "confidence levels")

    report = (EXP / "REPORT.md").read_text(encoding="utf-8")
    check(STATUS in report, "report", "status named")
    for phrase in ("Pulverstoff", "Holzportion", "Holz / holziger Pflanzenteil", "Wurzel / Wurzeldroge", "B001", "B002", "B003", "52 weak readings remain"):
        check(phrase in report, "report", phrase)

    validation = {
        "experiment_id": "GDT721", "status": "PASS",
        "checks_passed": sum(groups.values()), "check_groups": dict(sorted(groups.items())),
        "target_readings": 4, "target_positions": 4,
        "primary_evidence_bindings_replayed": 30, "rival_model_rows": 12,
        "construction_atoms_retained": 5, "score_delta_total": 0, "component_global_exports": 0,
        "non_target_lexical_rows_preserved": 320, "non_target_context_positions_preserved": 475,
        "remaining_unreviewed_weak_readings": 52,
        "complete_dictionary_rows_with_default_confidence_and_evidence": 1586,
        "legacy_bound_spans_restored": 3, "bound_spans_total": 5,
        "bound_span_execution_rows": 5, "bound_positions_consumed_once": 10,
        "f7r2_output_units": 8, "f84_or_f84r_used": 0,
    }
    (ART / "VALIDATION.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
