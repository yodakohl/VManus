#!/usr/bin/env python3
"""Independent validator for GDT720/V93."""

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
EXP = ROOT / "experiments/yolo/gdt720_v93_cold_result_whole_domain_repair"
SRC = EXP / "src"
ART = EXP / "artifacts"
G719 = ROOT / "experiments/yolo/gdt719_v92_three_result_whole_dy_rejection/artifacts"
STATUS = (
    "PASS_V93_2_COLD_RESULT_WHOLES_REVISED__SHARED_COOLING_MORPHOLOGY_REJECTED__"
    "2_POSITIONS_2_PAGES__56_WEAK_READINGS_REMAIN__NO_SCORE_CREDIT__ALL_H0_NONE"
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


def rename_v92(row: dict[str, str]) -> dict[str, str]:
    return {key.replace("v92", "v93").replace("V92", "V93"): value for key, value in row.items()}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    groups: Counter[str] = Counter()

    def check(condition: bool, group: str, message: str) -> None:
        if not condition:
            raise AssertionError(f"{group}: {message}")
        groups[group] += 1

    specs = read_tsv(SRC / "V93_2_AUDIT_SPECS.tsv")
    bindings = read_tsv(SRC / "V93_20_PRIMARY_EVIDENCE_BINDINGS.tsv")
    bound = read_tsv(ART / "V93_20_PRIMARY_EVIDENCE_BINDINGS.tsv")
    source_lex = read_tsv(G719 / "V92_324_ACTIVE_LEXICAL_READINGS.tsv")
    target_lex = read_tsv(ART / "V93_324_ACTIVE_LEXICAL_READINGS.tsv")
    source_ctx = read_tsv(G719 / "V92_479_CONTEXT_REALIZATIONS.tsv")
    target_ctx = read_tsv(ART / "V93_479_CONTEXT_REALIZATIONS.tsv")
    census = read_tsv(ART / "V93_58_HELD_READING_AUDIT.tsv")
    delta = read_tsv(ART / "V93_2_COLD_RESULT_CORE_CONTEXT_DELTA.tsv")
    domain = read_tsv(ART / "V93_1_REJECTED_SHARED_COOLING_MORPHOLOGY.tsv")
    rivals = read_tsv(ART / "V93_6_RIVAL_MODEL_COMPARISON.tsv")
    complete = read_tsv(ART / "V93_COMPLETE_WORD_CONFIDENCE.tsv")
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))

    expected = {
        "etyd#1": {
            "surface": "etyd", "core": "bis Mittelstufe gekühlt; abgeschlossen",
            "context": "bis zur Mittelstufe gekühlte, abgeschlossene Zubereitung",
            "position": "P099", "page": "f10r", "locus": "f10r.2", "ordinal": "10", "left": "daiin",
            "decomposition": "LEARNED_WHOLE_COLD_GRADE_RESULT_NO_DECOMPOSITION",
        },
        "teeedy#1": {
            "surface": "teeedy", "core": "vollständig abgekühlt; abgeschlossen",
            "context": "vollständig abgekühlte Zubereitung, fertig",
            "position": "P169", "page": "f115r", "locus": "f115r.1", "ordinal": "7", "left": "ol",
            "decomposition": "LEARNED_WHOLE_COLD_RESULT_UNRESOLVED_NO_SISTER",
        },
    }

    check(len(specs) == 2, "spec", "two specs")
    check({row["source_reading_id"] for row in specs} == set(expected), "spec", "target ids")
    for row in specs:
        exp = expected[row["source_reading_id"]]
        check(row["v93_lexical_core_de"] == exp["core"], "spec", f"{row['source_reading_id']} core")
        check(row["v93_context_realization_de"] == exp["context"], "spec", f"{row['source_reading_id']} context")
        check(row["decomposition"] == exp["decomposition"], "spec", f"{row['source_reading_id']} decomposition")
        check(row["family_ids"] == "NONE" and row["score_credit_family_ids"] == "NONE", "score", "no family credit")
        check(row["score_delta_lexical_core"] == "0", "score", "zero delta")
        check(row["component_global_export_allowed"] == "0", "scope", "no component export")
        check(not row["expected_page"].lower().startswith("f84"), "sealed", "target page allowed")

    check(len(bindings) == len(bound) == 20, "bindings", "twenty bindings")
    bound_by_id = {row["binding_id"]: row for row in bound}
    check(len(bound_by_id) == 20, "bindings", "binding ids unique")
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
        "v93_audit_decision", "v93_evidence_class", "v93_open_semantic_slots",
        "v93_component_global_export_allowed", "v93_prior_lexical_core_de",
    }
    for surface, source in source_lex_by_surface.items():
        output = target_lex_by_surface[surface]
        if surface in target_surfaces:
            source_id = output["source_reading_ids"]
            exp = expected[source_id]
            check(output["v93_lexical_core_de"] == exp["core"], "target_lexical", f"{surface} core")
            check(output["v93_context_realizations_de"] == exp["context"], "target_lexical", f"{surface} context")
            check(output["decomposition"] == exp["decomposition"], "target_lexical", f"{surface} decomposition")
            check(output["last_semantic_writer"] == "GDT720", "target_lexical", f"{surface} writer")
            check(output["working_model_score_0_100_not_probability"] == "30", "score", f"{surface} score")
            check(output["working_model_level"] == "W1_WEAK_WORKING", "score", f"{surface} level")
            check(output["family_ids"] == "NONE" and output["score_delta_lexical_core"] == "0", "score", f"{surface} no delta")
            check(output["v93_component_global_export_allowed"] == "0", "scope", f"{surface} export")
        else:
            renamed = rename_v92(source)
            for field, value in renamed.items():
                if field not in lexical_exceptions:
                    check(output.get(field) == value, "lexical_parity", f"{surface} {field}")

    check(target_lex_by_surface["otsheody"]["v93_lexical_core_de"] == source_lex_by_surface["otsheody"]["v92_lexical_core_de"], "separation", "otsheody core unchanged")
    check("otsheody" not in "|".join(row["source_reading_id"] for row in specs), "separation", "otsheody absent from specs")

    source_ctx_by_position = {row["position_id"]: row for row in source_ctx}
    target_ctx_by_position = {row["position_id"]: row for row in target_ctx}
    check(len(source_ctx) == len(target_ctx) == 479, "counts", "context rows")
    check(set(source_ctx_by_position) == set(target_ctx_by_position), "context_parity", "position set")
    target_positions = {item["position"] for item in expected.values()}
    context_exceptions = {
        "v93_audit_decision", "v93_evidence_class", "v93_open_semantic_slots",
        "v93_component_global_export_allowed", "v93_local_context_hypothesis", "v93_expected_left_surface",
    }
    for position_id, source in source_ctx_by_position.items():
        output = target_ctx_by_position[position_id]
        if position_id in target_positions:
            exp = next(value for value in expected.values() if value["position"] == position_id)
            check(output["surface"] == exp["surface"], "target_context", f"{position_id} surface")
            check(output["v93_lexical_core_de"] == exp["core"], "target_context", f"{position_id} core")
            check(output["v93_context_realization_de"] == exp["context"], "target_context", f"{position_id} context")
            check(output["page"] == exp["page"] and output["locus"] == exp["locus"] and output["token_ordinal"] == exp["ordinal"], "target_context", f"{position_id} locus")
            check(output["v68_clause_type"] == "NOMINAL_BLOCK" and output["v68_action_license"] == "NOT_ACTION_LICENSED", "target_context", f"{position_id} nominal")
            check(output["v93_expected_left_surface"] == exp["left"], "target_context", f"{position_id} left")
            check(output["v93_component_global_export_allowed"] == "0", "scope", f"{position_id} export")
        else:
            renamed = rename_v92(source)
            for field, value in renamed.items():
                if field not in context_exceptions:
                    check(output.get(field) == value, "context_parity", f"{position_id} {field}")

    check(len(census) == 58, "census", "census rows")
    check(Counter(row["disposition"] for row in census) == Counter({"HELD_FOR_LATER_REPAIR": 56, "REVISED_IN_V93": 2}), "census", "dispositions")
    check({row["source_reading_id"] for row in census if row["disposition"] == "REVISED_IN_V93"} == set(expected), "census", "revised ids")
    check(len(delta) == 2, "delta", "delta rows")
    for row in delta:
        exp = expected[row["source_reading_id"]]
        check(row["v93_lexical_core_de"] == exp["core"], "delta", f"{row['source_reading_id']} core")
        check(row["old_score"] == row["v93_score"] == "30", "score", f"{row['source_reading_id']} unchanged")
        check(row["family_ids"] == row["score_credit_family_ids"] == "NONE", "score", f"{row['source_reading_id']} family")
        check(row["component_global_export_allowed"] == "0", "scope", f"{row['source_reading_id']} component")

    check(len(domain) == 1, "domain", "one domain decision")
    check(domain[0]["semantic_domain_decision"] == "RETAIN_FOR_BOTH_WHOLE_DEFAULTS", "domain", "semantic domain retained")
    check(domain[0]["written_family_decision"] == "REJECT_SHARED_COOLING_OR_CLOSURE_MORPHOLOGY", "domain", "morphology rejected")
    check(domain[0]["score_delta"] == "0" and domain[0]["component_global_export_allowed"] == "0", "domain", "no credit/export")
    check("otsheody" not in domain[0]["selected_surfaces"], "separation", "otsheody outside domain")

    check(len(rivals) == 6, "rivals", "six rows")
    check(Counter(row["source_reading_id"] for row in rivals) == Counter({"etyd#1": 3, "teeedy#1": 3}), "rivals", "three models each")
    check(Counter(row["model_id"] for row in rivals) == Counter({"COLD_RESULT": 2, "DOSE_HANDOFF": 2, "RESIDUE_REST": 2}), "rivals", "model balance")
    selected = [row for row in rivals if row["portable_default_selected"] == "1"]
    check(len(selected) == 2 and all(row["model_id"] == "COLD_RESULT" for row in selected), "rivals", "cold selected")
    for row in rivals:
        check(row["score_credit"] == "0", "score", f"rival {row['source_reading_id']} {row['model_id']}")

    check(len(complete) == 1586, "complete", "complete rows")
    check(len({row["surface"] for row in complete}) == 1582, "complete", "complete surfaces")
    for row in complete:
        check(bool(row["working_meaning_de"]), "dictionary", f"{row['reading_id']} default")
        check(bool(row["working_model_level"]), "dictionary", f"{row['reading_id']} level")
        check(bool(row["working_model_score_0_100_not_probability"]), "dictionary", f"{row['reading_id']} score")
        check(bool(row["positive_evidence_de"]), "dictionary", f"{row['reading_id']} evidence")
        check(bool(row["counterevidence_de"]), "dictionary", f"{row['reading_id']} counterevidence")
        check(row["historical_confirmation"] == "H0_NONE", "history", row["reading_id"])
    active_complete = {row["reading_id"]: row for row in complete if row["current_layer"] == "ACTIVE_V93_LEXICAL_CORE"}
    check(len(active_complete) == 324, "complete", "active complete rows")
    for source_id, exp in expected.items():
        check(active_complete[source_id]["working_meaning_de"] == exp["core"], "complete", f"{source_id} core")

    check(sha256(G719 / "V92_2_BOUND_SPAN_RENDERER.tsv") == sha256(ART / "V93_2_BOUND_SPAN_RENDERER.tsv"), "renderer", "spans byte exact")
    check(sha256(G719 / "V92_2_ONE_SHOT_RENDER_DIRECTIVES.tsv") == sha256(ART / "V93_2_ONE_SHOT_RENDER_DIRECTIVES.tsv"), "renderer", "directives byte exact")
    check(sha256(G719 / "V92_8_F7R2_RENDERED_UNITS.tsv") == sha256(ART / "V93_8_F7R2_RENDERED_UNITS.tsv"), "renderer", "f7r2 byte exact")

    g689_forms = read_tsv(ROOT / "experiments/yolo/gdt689_v62_bound_dy_sister_endpoint_dispatch/artifacts/SURFACE_DY_60_FORM_INVENTORY.tsv")
    g689_positions = read_tsv(ROOT / "experiments/yolo/gdt689_v62_bound_dy_sister_endpoint_dispatch/artifacts/SURFACE_DY_74_POSITION_INVENTORY.tsv")
    check("etyd" not in {row["surface"] for row in g689_forms}, "negative_scope", "etyd absent from GDT689 forms")
    check("etyd" not in {row["surface"] for row in g689_positions}, "negative_scope", "etyd absent from GDT689 positions")
    teeedy_form = next(row for row in g689_forms if row["surface"] == "teeedy")
    check(teeedy_form["formal_dy_status"] == "UNRESOLVED" and teeedy_form["pair_status"] == "NO_REAL_SISTER", "negative_scope", "teeedy unresolved no sister")

    check(result["status"] == STATUS, "result", "status")
    for field, value in {
        "target_readings": 2, "target_positions": 2, "target_pages": 2,
        "primary_evidence_bindings": 20, "rival_model_rows": 6,
        "shared_semantic_domains_retained": 1, "shared_written_families_accepted": 0,
        "score_credit_families": 0, "score_delta_total": 0, "component_global_exports": 0,
        "active_lexical_rows": 324, "active_source_readings": 332, "context_positions": 479,
        "non_target_lexical_rows_preserved": 322, "non_target_context_positions_preserved": 477,
        "remaining_unreviewed_weak_readings": 56, "complete_dictionary_rows": 1586,
        "complete_dictionary_surfaces": 1582,
        "complete_dictionary_rows_with_default_confidence_and_evidence": 1586,
        "bound_spans_preserved": 2, "f7r2_output_units": 8, "f84_or_f84r_used": 0,
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
    check("bis Mittelstufe gekühlt; abgeschlossen" in report, "report", "etyd named")
    check("vollständig abgekühlt; abgeschlossen" in report, "report", "teeedy named")
    check("30→30" in report, "report", "zero score visible")
    check("56 weak readings remain" in report, "report", "remaining holds named")

    validation = {
        "experiment_id": "GDT720",
        "status": "PASS",
        "checks_passed": sum(groups.values()),
        "check_groups": dict(sorted(groups.items())),
        "target_readings": 2,
        "target_positions": 2,
        "primary_evidence_bindings_replayed": 20,
        "rival_model_rows": 6,
        "shared_written_families_accepted": 0,
        "score_delta_total": 0,
        "component_global_exports": 0,
        "non_target_lexical_rows_preserved": 322,
        "non_target_context_positions_preserved": 477,
        "remaining_unreviewed_weak_readings": 56,
        "complete_dictionary_rows_with_default_confidence_and_evidence": 1586,
        "bound_spans_preserved": 2,
        "f7r2_output_units": 8,
        "f84_or_f84r_used": 0,
    }
    (ART / "VALIDATION.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
