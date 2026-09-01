#!/usr/bin/env python3
"""Build V95 by resolving five OP/P holds as bound whole renderers."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

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

SOURCE_LEXICAL = G721 / "V94_324_ACTIVE_LEXICAL_READINGS.tsv"
SOURCE_CONTEXT = G721 / "V94_479_CONTEXT_REALIZATIONS.tsv"
SOURCE_CENSUS = G721 / "V94_56_HELD_READING_AUDIT.tsv"
SOURCE_COMPLETE = G721 / "V94_COMPLETE_WORD_CONFIDENCE.tsv"
SOURCE_SPANS = G721 / "V94_5_BOUND_SPAN_RENDERER.tsv"
SOURCE_SPAN_EXECUTION = G721 / "V94_5_BOUND_SPAN_EXECUTION_AUDIT.tsv"
SOURCE_DIRECTIVES = G721 / "V94_2_ONE_SHOT_RENDER_DIRECTIVES.tsv"
SOURCE_F7R2 = G721 / "V94_8_F7R2_RENDERED_UNITS.tsv"
G652_COVERAGE = ROOT / "experiments/yolo/gdt652_strict_v28_frontier_completion/artifacts/ALL_LINE_CONCRETE_COVERAGE_V29.tsv"
G633_E_RUN = ROOT / "experiments/yolo/gdt633_cth_interfix_semantic_contrasts/artifacts/LITERAL_E_RUN_BACKGROUND.tsv"
SPECS = SRC / "V95_5_AUDIT_SPECS.tsv"
BINDINGS = SRC / "V95_36_PRIMARY_EVIDENCE_BINDINGS.tsv"

HISTORICAL = "H0_NONE"
TARGET_IDS = {"op#1", "chopo#1", "qopaiin#1", "opchedaiin#1", "opchey#1"}
STATUS = (
    "PASS_V95_5_OP_HOLDS_RESOLVED_AS_BOUND_WHOLE_RENDERERS__QOPAIIN_ACTION_REMOVED_FROM_"
    "LEXICAL_CORE__OPCHEY_26_PLUS_4_FORMAL_FAMILY__NO_INTERNAL_P_EXPORT__47_WEAK_"
    "READINGS_REMAIN__NO_SCORE_CREDIT__ALL_H0_NONE"
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: Iterable[dict[str, Any]], fields: list[str] | None = None) -> None:
    materialized = list(rows)
    if fields is None:
        fields = list(materialized[0]) if materialized else []
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in materialized:
            writer.writerow({field: row.get(field, "") for field in fields})


def split_pipe(value: str) -> list[str]:
    return [part.strip() for part in value.split("|") if part.strip() and part.strip() not in {"NONE", "0"}]


def compact(values: Iterable[str], empty: str = "NONE") -> str:
    output: list[str] = []
    for value in values:
        if value and value not in {"NONE", "0"} and value not in output:
            output.append(value)
    return "|".join(output) if output else empty


def append_pipe(value: str, addition: str) -> str:
    return compact([*split_pipe(value), addition])


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


def rename_v94(row: dict[str, str]) -> dict[str, Any]:
    return {key.replace("v94", "v95").replace("V94", "V95"): value for key, value in row.items()}


def resolve_bindings(bindings: list[dict[str, str]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for binding in bindings:
        assert binding["source_reading_id"] in TARGET_IDS
        assert binding["score_credit_family_ids"] == "NONE"
        assert "f84" not in binding["evidence_path"].lower()
        selector = parse_assertions(binding["selector"])
        assertions = parse_assertions(binding["field_assertions"])
        contains = parse_assertions(binding["field_contains_assertions"])
        assert all(not value.lower().startswith("f84") for value in selector.values())
        matches = [
            row for row in read_tsv(ROOT / binding["evidence_path"])
            if all(row.get(field) == expected for field, expected in selector.items())
        ]
        assert len(matches) == 1, (binding["binding_id"], len(matches))
        source = matches[0]
        for field, expected in assertions.items():
            assert source.get(field) == expected, (binding["binding_id"], field, source.get(field), expected)
        for field, expected in contains.items():
            assert expected in split_pipe(source.get(field, "")), (
                binding["binding_id"], field, source.get(field), expected
            )
        fingerprint = hashlib.sha256(
            json.dumps(source, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        output.append({
            **binding,
            "matched_row_fingerprint_sha256": fingerprint,
            "source_row_match": 1,
            "evidence_status": "BOUND_EXACT_PRIMARY_ROW",
            "historical_confirmation": HISTORICAL,
        })
    assert len(output) == 36
    assert Counter(row["source_reading_id"] for row in output) == Counter({
        "opchedaiin#1": 7, "chopo#1": 7, "op#1": 7, "qopaiin#1": 7, "opchey#1": 8,
    })
    return output


def build_lexical(
    source_rows: list[dict[str, str]], specs: list[dict[str, str]]
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    specs_by_id = {row["source_reading_id"]: row for row in specs}
    output: list[dict[str, Any]] = []
    for source in source_rows:
        row = rename_v94(source)
        source_ids = split_pipe(source["source_reading_ids"])
        spec = specs_by_id.get(source_ids[0]) if len(source_ids) == 1 else None
        if spec:
            assert source["v94_lexical_core_de"] == spec["old_lexical_core_de"]
            base = int(source["working_model_score_0_100_not_probability"])
            delta = int(spec["score_delta_lexical_core"])
            assert delta == 0 and spec["score_credit_family_ids"] == "NONE"
            score = min(base + delta, int(spec["lexical_core_cap"]))
            context_score = min(score, int(spec["context_realization_cap"]))
            row.update({
                "v95_lexical_core_de": spec["v95_lexical_core_de"],
                "v95_context_realizations_de": spec["v95_context_realization_de"],
                "family_ids": spec["family_ids"],
                "decomposition": spec["decomposition"],
                "semantic_scope": spec["target_semantic_scope"],
                "semantic_applicability": spec["target_semantic_applicability"],
                "global_export_scope": spec["target_global_export_scope"],
                "unconditional_global_export_allowed": spec["target_unconditional_global_export_allowed"],
                "repair_modes": spec["repair_mode"],
                "resolved_debt_atoms": spec["resolved_debt_atom"],
                "last_semantic_writer": "GDT722",
                "base_score": base,
                "score_delta_lexical_core": delta,
                "lexical_core_cap": spec["lexical_core_cap"],
                "working_model_score_0_100_not_probability": score,
                "working_model_level": level(score),
                "context_realization_cap": spec["context_realization_cap"],
                "context_realization_score_0_100_not_probability": context_score,
                "context_realization_level": level(context_score),
                "source_gdts": append_pipe(source["source_gdts"], "GDT722"),
                "positive_evidence_de": (
                    "GDT722 schließt die Form als konkreten gebundenen, nicht zerlegten Rendererwert: "
                    + spec["evidence_de"] + " || " + source["positive_evidence_de"]
                ),
                "counterevidence_de": (
                    "GDT722 Grenze: " + spec["counterevidence_de"]
                    + " || Historisch unbestaetigte Arbeitstheorie; keine Klartextidentifikation."
                ),
                "v95_audit_decision": "REVISE" if source_ids[0] == "qopaiin#1" else "RETAIN_SCOPED_WHOLE",
                "v95_evidence_class": spec["evidence_class"],
                "v95_open_semantic_slots": spec["open_semantic_slots"],
                "v95_component_global_export_allowed": "0",
                "v95_prior_lexical_core_de": source["v94_lexical_core_de"],
            })
        else:
            row.update({
                "v95_audit_decision": "NOT_IN_GDT722_TRANCHE",
                "v95_evidence_class": "INHERITED_V94",
                "v95_open_semantic_slots": "NOT_EVALUATED",
                "v95_component_global_export_allowed": "NOT_EVALUATED",
                "v95_prior_lexical_core_de": source["v94_lexical_core_de"],
            })
        output.append(row)
    assert len(output) == 324
    by_source: dict[str, dict[str, Any]] = {}
    for row in output:
        for source_id in split_pipe(str(row["source_reading_ids"])):
            assert source_id not in by_source
            by_source[source_id] = row
    assert len(by_source) == 332
    return output, by_source


def build_contexts(
    source_rows: list[dict[str, str]], specs: list[dict[str, str]], lexical_by_source: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    specs_by_id = {row["source_reading_id"]: row for row in specs}
    by_locus_ordinal = {(row["locus"], int(row["token_ordinal"])): row for row in source_rows}
    seen: Counter[str] = Counter()
    output: list[dict[str, Any]] = []
    for source in source_rows:
        source_id = source["source_reading_id"]
        lexical = lexical_by_source[source_id]
        spec = specs_by_id.get(source_id)
        row = rename_v94(source)
        if spec:
            seen[source_id] += 1
            assert (source["position_id"], source["page"], source["locus"], source["token_ordinal"]) == (
                spec["expected_position_id"], spec["expected_page"], spec["expected_locus"],
                spec["expected_token_ordinal"],
            )
            ordinal = int(source["token_ordinal"])
            left = "<BOS>" if ordinal == 1 else by_locus_ordinal[(source["locus"], ordinal - 1)]["surface"]
            right = "<EOS>" if (source["locus"], ordinal + 1) not in by_locus_ordinal else by_locus_ordinal[(source["locus"], ordinal + 1)]["surface"]
            assert (left, right, source["v68_action_license"]) == (
                spec["expected_left_surface"], spec["expected_right_surface"], spec["expected_action_license"],
            )
        row.update({
            "v95_reading_id": lexical["v95_reading_id"],
            "v95_lexical_core_de": lexical["v95_lexical_core_de"],
            "v95_context_realization_de": spec["v95_context_realization_de"] if spec else source["v94_context_realization_de"],
            "v95_repair_mode": spec["repair_mode"] if spec else source["v94_repair_mode"],
            "v95_resolved_debt_atom": spec["resolved_debt_atom"] if spec else source["v94_resolved_debt_atom"],
            "v95_lexical_score": lexical["working_model_score_0_100_not_probability"],
            "v95_lexical_level": lexical["working_model_level"],
            "v95_context_score": lexical["context_realization_score_0_100_not_probability"],
            "v95_context_level": lexical["context_realization_level"],
            "v95_semantic_scope": lexical["semantic_scope"],
            "v95_semantic_applicability": lexical["semantic_applicability"],
            "v95_global_export_scope": lexical["global_export_scope"],
            "v95_lexical_bound_span_ids": lexical["bound_span_ids"],
            "v95_unconditional_global_export_allowed": lexical["unconditional_global_export_allowed"],
            "v95_historical_confirmation": HISTORICAL,
            "v95_audit_decision": "REVISE" if spec and source_id == "qopaiin#1" else (
                "RETAIN_SCOPED_WHOLE" if spec else "NOT_IN_GDT722_TRANCHE"
            ),
            "v95_evidence_class": spec["evidence_class"] if spec else "INHERITED_V94",
            "v95_open_semantic_slots": spec["open_semantic_slots"] if spec else "NOT_EVALUATED",
            "v95_component_global_export_allowed": "0" if spec else "NOT_EVALUATED",
            "v95_local_context_hypothesis": spec["local_context_hypothesis"] if spec else "NONE",
            "v95_expected_left_surface": spec["expected_left_surface"] if spec else "NONE",
            "v95_expected_right_surface": spec["expected_right_surface"] if spec else "NONE",
        })
        output.append(row)
    assert seen == Counter({target: 1 for target in TARGET_IDS})
    assert len(output) == 479
    return output


def build_census(
    source_rows: list[dict[str, str]], specs: list[dict[str, str]], lexical_by_source: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    specs_by_id = {row["source_reading_id"]: row for row in specs}
    output: list[dict[str, Any]] = []
    for source in source_rows:
        if source["disposition"] != "HELD_FOR_LATER_REPAIR":
            continue
        source_id = source["source_reading_id"]
        lexical = lexical_by_source[source_id]
        spec = specs_by_id.get(source_id)
        row = rename_v94(source)
        if spec:
            row.update({
                "disposition": "REVISED_IN_V95",
                "repair_mode": spec["repair_mode"],
                "resolved_debt_atom": spec["resolved_debt_atom"],
                "v95_reading_id": lexical["v95_reading_id"],
                "v95_lexical_core_de": lexical["v95_lexical_core_de"],
                "v95_context_realization_de": spec["v95_context_realization_de"],
                "new_lexical_score": lexical["working_model_score_0_100_not_probability"],
                "new_lexical_level": lexical["working_model_level"],
                "new_context_score": lexical["context_realization_score_0_100_not_probability"],
                "new_context_level": lexical["context_realization_level"],
                "positive_evidence_de": spec["evidence_de"],
                "counterevidence_de": spec["counterevidence_de"],
                "v95_audit_decision": "REVISE" if source_id == "qopaiin#1" else "RETAIN_SCOPED_WHOLE",
                "v95_evidence_class": spec["evidence_class"],
                "v95_open_semantic_slots": spec["open_semantic_slots"],
            })
        else:
            row.update({
                "v95_reading_id": lexical["v95_reading_id"],
                "v95_lexical_core_de": lexical["v95_lexical_core_de"],
                "v95_context_realization_de": lexical["v95_context_realizations_de"],
                "new_lexical_score": lexical["working_model_score_0_100_not_probability"],
                "new_lexical_level": lexical["working_model_level"],
                "new_context_score": lexical["context_realization_score_0_100_not_probability"],
                "new_context_level": lexical["context_realization_level"],
                "v95_audit_decision": "HELD_FOR_LATER_REPAIR",
                "v95_evidence_class": "INHERITED_V94",
                "v95_open_semantic_slots": "NOT_EVALUATED",
            })
        output.append(row)
    assert len(output) == 52
    assert Counter(row["disposition"] for row in output) == Counter({
        "HELD_FOR_LATER_REPAIR": 47, "REVISED_IN_V95": 5,
    })
    return output


def build_delta(
    source_rows: list[dict[str, str]], specs: list[dict[str, str]], target_by_source: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    source_by_id = {source_id: row for row in source_rows for source_id in split_pipe(row["source_reading_ids"])}
    output: list[dict[str, Any]] = []
    for spec in specs:
        source = source_by_id[spec["source_reading_id"]]
        target = target_by_source[spec["source_reading_id"]]
        output.append({
            "source_reading_id": spec["source_reading_id"], "surface": spec["surface"],
            "position_id": spec["expected_position_id"], "page": spec["expected_page"],
            "locus": spec["expected_locus"], "token_ordinal": spec["expected_token_ordinal"],
            "left_surface": spec["expected_left_surface"], "right_surface": spec["expected_right_surface"],
            "old_lexical_core_de": source["v94_lexical_core_de"],
            "v95_lexical_core_de": target["v95_lexical_core_de"],
            "v95_context_realization_de": spec["v95_context_realization_de"],
            "portable_role": spec["portable_role"], "old_score": source["working_model_score_0_100_not_probability"],
            "v95_score": target["working_model_score_0_100_not_probability"],
            "old_level": source["working_model_level"], "v95_level": target["working_model_level"],
            "family_ids": spec["family_ids"], "score_credit_family_ids": spec["score_credit_family_ids"],
            "decomposition": spec["decomposition"], "repair_mode": spec["repair_mode"],
            "evidence_de": spec["evidence_de"], "counterevidence_de": spec["counterevidence_de"],
            "open_semantic_slots": spec["open_semantic_slots"],
            "component_global_export_allowed": spec["component_global_export_allowed"],
            "historical_confirmation": HISTORICAL,
        })
    return output


def build_scope_dictionary() -> list[dict[str, Any]]:
    return [
        {
            "scope_item": "P_INITIAL", "visible_pattern": "p-", "working_value_de": "Pulver / Pulverform",
            "allowed_scope": "TOKEN_INITIAL_IN_ADMITTED_FOUR_HEAD_COMPOSITION",
            "forbidden_scope": "INNER_P|STANDALONE_P|TERMINAL_P|ARBITRARY_OP_DECOMPOSITION",
            "evidence_summary_de": "GDT635: 503 Anfangsvorkommen, 277 Typen, 140 Seiten und 361 lesergenau; 858 innere p-Token sind ausdrücklich getrennt.",
            "status": "RETAIN_NARROW_SCOPE", "exact_whole_surface_default_allowed": 0,
            "component_or_substring_global_export_allowed": 0, "score_credit": 0,
            "historical_confirmation": HISTORICAL,
        },
        {
            "scope_item": "OP_BOUND_WHOLE_RENDERER_GROUP", "visible_pattern": "op|qop...|...op...",
            "working_value_de": "Pulverprodukt oder Pulverzubereitung nur je exakter Ganzoberfläche",
            "allowed_scope": "FIVE_EXACT_GDT722_TARGET_SURFACES",
            "forbidden_scope": "GLOBAL_OP_PREFIX|O_PLUS_P_COMPONENT_EXPORT|NEW_SURFACE_PREDICTION",
            "evidence_summary_de": "Fünf gebundene GDT691-Tokenregeln liefern konkrete Pulverwerte; vier sind nominal, nur qopaiin ist lokal aktionslizenziert.",
            "status": "RETAIN_BOUND_WHOLE_RENDERERS", "exact_whole_surface_default_allowed": 1,
            "component_or_substring_global_export_allowed": 0, "score_credit": 0,
            "historical_confirmation": HISTORICAL,
        },
        {
            "scope_item": "OPCH_E_RUN_FORMAL_FAMILY", "visible_pattern": "opch<E>y",
            "working_value_de": "formale E-Stufenfamilie ohne Teilbedeutung",
            "allowed_scope": "OPCHEY_26_OCCURRENCES|OPCHEEY_4_OCCURRENCES",
            "forbidden_scope": "FREE_OP|FREE_CH|FREE_E|FREE_Y_SEMANTICS",
            "evidence_summary_de": "GDT633 G633-EB0201: opchey/opcheey, 26/4 Vorkommen, zwei formale E-Längen.",
            "status": "FORMAL_ONLY", "exact_whole_surface_default_allowed": 0,
            "component_or_substring_global_export_allowed": 0, "score_credit": 0,
            "historical_confirmation": HISTORICAL,
        },
        {
            "scope_item": "QOPAIIN_CONTEXT_ACTION", "visible_pattern": "qopaiin at P158",
            "working_value_de": "Wortkern: drei Teile Pulverzubereitung; Kontext: nehmen",
            "allowed_scope": "P158_ACTION_CLAUSE_ONLY",
            "forbidden_scope": "FREE_Q_ACTION|FREE_OP_ACTION|FREE_AIIN_ACTION|OTHER_QOPAIIN_OCCURRENCES",
            "evidence_summary_de": "P158 ist die einzige aktive aktionslizenzierte Zielposition; nehmen wird aus dem portablen Wortkern entfernt.",
            "status": "LEXICAL_CONTEXT_SEPARATED", "exact_whole_surface_default_allowed": 0,
            "component_or_substring_global_export_allowed": 0, "score_credit": 0,
            "historical_confirmation": HISTORICAL,
        },
    ]


def build_rivals(specs: list[dict[str, str]]) -> list[dict[str, Any]]:
    compositional_candidate = {
        "opchedaiin#1": "O_PREP + P_INTERNAL + CHEDAIIN",
        "chopo#1": "CH + O_PREP + P_INTERNAL + O",
        "op#1": "O_PREP + P_INTERNAL",
        "qopaiin#1": "Q + O_PREP + P_INTERNAL + AIIN",
        "opchey#1": "O_PREP + P_INTERNAL + CHEY",
    }
    rival_meaning = {
        "opchedaiin#1": "drei Portionen getrocknete Pulverzubereitung",
        "chopo#1": "trockene Pulverzubereitung aus unbekanntem O-Rest",
        "op#1": "Ansatz des Pulverstoffs",
        "qopaiin#1": "drei Teile eines Pulveransatzes nehmen",
        "opchey#1": "Pulverzubereitung, trockene Form I",
    }
    output: list[dict[str, Any]] = []
    for spec in specs:
        source_id = spec["source_reading_id"]
        output.extend([
            {
                "source_reading_id": source_id, "surface": spec["surface"],
                "model_id": "A_BOUND_WHOLE_RENDERER_NO_COMPONENT_EXPORT", "candidate_default_de": spec["v95_lexical_core_de"],
                "decision": "SELECT", "evidence_fit_de": spec["evidence_de"],
                "conflict_de": spec["counterevidence_de"], "portable_default_selected": 1,
                "score_credit": 0, "component_global_export_allowed": 0,
            },
            {
                "source_reading_id": source_id, "surface": spec["surface"],
                "model_id": "B_INTERNAL_P_COMPOSITION", "candidate_default_de": rival_meaning[source_id],
                "decision": "REJECT_UNPAID_RESIDUE" if source_id == "chopo#1" else "KEEP_LIVE_RIVAL_NOT_SELECTED",
                "evidence_fit_de": "Die wiederkehrende Pulverdomäne wäre mit einem inneren p-Kopf vereinbar.",
                "conflict_de": compositional_candidate[source_id] + " ist nicht lizenziert; GDT635 trennt innere p von p-Initialköpfen.",
                "portable_default_selected": 0, "score_credit": 0, "component_global_export_allowed": 0,
            },
            {
                "source_reading_id": source_id, "surface": spec["surface"],
                "model_id": "C_UNRELATED_LEXEME_OR_FORMULA", "candidate_default_de": "unabhängiges Lexem oder Formelmarker",
                "decision": "KEEP_COUNTERMODEL", "evidence_fit_de": "Die Form kann als gelerntes technisches Zeichen ohne innere Segmentierung funktionieren.",
                "conflict_de": "Verliert den konkreten Pulverbefund und erklärt die lokale op/qopaiin-Verbindung nicht besser.",
                "portable_default_selected": 0, "score_credit": 0, "component_global_export_allowed": 0,
            },
        ])
    assert len(output) == 15
    return output


def build_upstream_unknown(specs: list[dict[str, str]]) -> list[dict[str, Any]]:
    coverage = read_tsv(G652_COVERAGE)
    output: list[dict[str, Any]] = []
    for spec in specs:
        matches = [row for row in coverage if row["page"] == spec["expected_page"] and row["locus"] == spec["expected_locus"]]
        assert len(matches) == 1
        source = matches[0]
        assert spec["surface"] in split_pipe(source["unknown_surfaces"])
        output.append({
            "source_reading_id": spec["source_reading_id"], "surface": spec["surface"],
            "page": source["page"], "locus": source["locus"], "token_ordinal": spec["expected_token_ordinal"],
            "gdt652_scope_state": "UNKNOWN_SURFACE", "gdt652_unknown_tokens_on_line": source["unknown_tokens"],
            "gdt691_route": "LEARNED_WHOLE_OR_UNEXPORTED", "v95_selected_model": "A_BOUND_WHOLE_RENDERER_NO_COMPONENT_EXPORT",
            "lineage_interpretation_de": "Der konkrete Default entsteht erst als spätere gebundene Rollenentscheidung; gelernter Ganzwert gegen unexportierte Komposition bleibt formal offen.",
            "score_credit": 0, "historical_confirmation": HISTORICAL,
        })
    return output


def build_formal_family() -> list[dict[str, Any]]:
    matches = [row for row in read_tsv(G633_E_RUN) if row["family_id"] == "G633-EB0201"]
    assert len(matches) == 1
    source = matches[0]
    assert (source["skeleton"], source["surfaces_by_length"], source["occurrences_by_length"]) == (
        "opch<E>y", "1:opchey|2:opcheey", "1:26|2:4",
    )
    return [{
        **source,
        "v95_semantic_decision": "FORMAL_FAMILY_ONLY_NO_COMPONENT_SEMANTICS",
        "selected_whole_default_de": "opchey=Trockenpulver, Form I",
        "sister_semantic_value_de": "OFFEN",
        "component_global_export_allowed": 0,
        "score_credit": 0,
        "historical_confirmation": HISTORICAL,
    }]


def build_target_renderer(contexts: list[dict[str, Any]], specs: list[dict[str, str]]) -> list[dict[str, Any]]:
    by_position = {row["position_id"]: row for row in contexts}
    output: list[dict[str, Any]] = []
    for spec in specs:
        row = by_position[spec["expected_position_id"]]
        output.append({
            "position_id": row["position_id"], "page": row["page"], "locus": row["locus"],
            "token_ordinal": row["token_ordinal"], "surface": row["surface"],
            "left_surface": spec["expected_left_surface"], "right_surface": spec["expected_right_surface"],
            "portable_lexical_core_de": row["v95_lexical_core_de"],
            "local_context_realization_de": row["v95_context_realization_de"],
            "action_license": row["v68_action_license"],
            "selected_model": "A_BOUND_WHOLE_RENDERER_NO_COMPONENT_EXPORT", "decomposition": spec["decomposition"],
            "component_global_export_allowed": 0, "score": row["v95_lexical_score"],
            "level": row["v95_lexical_level"], "historical_confirmation": HISTORICAL,
        })
    return output


def build_complete(source_rows: list[dict[str, str]], lexical: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for source in source_rows:
        if source["current_layer"] == "ACTIVE_V94_LEXICAL_CORE":
            continue
        row = rename_v94(source)
        row.update({
            "v95_audit_decision": "OUTSIDE_ACTIVE_V95_TRANCHE",
            "v95_evidence_class": "INHERITED_GLOBAL_V48",
            "v95_open_semantic_slots": "NOT_EVALUATED",
            "v95_component_global_export_allowed": "NOT_EVALUATED",
        })
        output.append(row)
    for row in lexical:
        output.append({
            "surface": row["surface"], "reading_id": row["v95_reading_id"],
            "working_meaning_de": row["v95_lexical_core_de"], "current_layer": "ACTIVE_V95_LEXICAL_CORE",
            "semantic_scope": row["semantic_scope"], "semantic_applicability": row["semantic_applicability"],
            "form_level": row["form_level"], "occurrence_count": row["occurrence_count"],
            "page_count": row["page_count"], "locus_count": row["locus_count"],
            "working_model_score_0_100_not_probability": row["working_model_score_0_100_not_probability"],
            "working_model_level": row["working_model_level"], "source_gdts": row["source_gdts"],
            "positive_evidence_de": row["positive_evidence_de"], "counterevidence_de": row["counterevidence_de"],
            "historical_confirmation": row["historical_confirmation"], "historical_analogue": row["historical_analogue"],
            "relation_word_delta": row["relation_word_delta"], "global_export_scope": row["global_export_scope"],
            "bound_span_ids": row["bound_span_ids"],
            "unconditional_global_export_allowed": row["unconditional_global_export_allowed"],
            "v95_context_realizations_de": row["v95_context_realizations_de"],
            "source_reading_ids": row["source_reading_ids"], "v95_audit_decision": row["v95_audit_decision"],
            "v95_evidence_class": row["v95_evidence_class"],
            "v95_open_semantic_slots": row["v95_open_semantic_slots"],
            "v95_component_global_export_allowed": row["v95_component_global_export_allowed"],
        })
    return sorted(output, key=lambda row: (str(row["surface"]), str(row["reading_id"])))


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    specs = read_tsv(SPECS)
    bindings = read_tsv(BINDINGS)
    assert len(specs) == 5 and {row["source_reading_id"] for row in specs} == TARGET_IDS
    assert all(row["component_global_export_allowed"] == "0" for row in specs)
    assert all(row["score_delta_lexical_core"] == "0" for row in specs)

    source_lexical = read_tsv(SOURCE_LEXICAL)
    source_context = read_tsv(SOURCE_CONTEXT)
    source_census = read_tsv(SOURCE_CENSUS)
    source_complete = read_tsv(SOURCE_COMPLETE)
    evidence = resolve_bindings(bindings)
    lexical, lexical_by_source = build_lexical(source_lexical, specs)
    contexts = build_contexts(source_context, specs, lexical_by_source)
    census = build_census(source_census, specs, lexical_by_source)
    delta = build_delta(source_lexical, specs, lexical_by_source)
    scope_dictionary = build_scope_dictionary()
    rivals = build_rivals(specs)
    upstream_unknown = build_upstream_unknown(specs)
    formal_family = build_formal_family()
    target_renderer = build_target_renderer(contexts, specs)
    complete = build_complete(source_complete, lexical)

    write_tsv(ART / "V95_324_ACTIVE_LEXICAL_READINGS.tsv", lexical)
    write_tsv(ART / "V95_479_CONTEXT_REALIZATIONS.tsv", contexts)
    write_tsv(ART / "V95_52_HELD_READING_AUDIT.tsv", census)
    write_tsv(ART / "V95_5_OP_CORE_CONTEXT_DELTA.tsv", delta)
    write_tsv(ART / "V95_4_OP_SCOPE_DICTIONARY.tsv", scope_dictionary)
    write_tsv(ART / "V95_15_RIVAL_MODEL_COMPARISON.tsv", rivals)
    write_tsv(ART / "V95_36_PRIMARY_EVIDENCE_BINDINGS.tsv", evidence)
    write_tsv(ART / "V95_5_UPSTREAM_UNKNOWN_POSITION_AUDIT.tsv", upstream_unknown)
    write_tsv(ART / "V95_1_FORMAL_E_RUN_FAMILY.tsv", formal_family)
    write_tsv(ART / "V95_5_TARGET_RENDERER.tsv", target_renderer)
    write_tsv(ART / "V95_COMPLETE_WORD_CONFIDENCE.tsv", complete)
    shutil.copyfile(SOURCE_SPANS, ART / "V95_5_BOUND_SPAN_RENDERER.tsv")
    shutil.copyfile(SOURCE_SPAN_EXECUTION, ART / "V95_5_BOUND_SPAN_EXECUTION_AUDIT.tsv")
    shutil.copyfile(SOURCE_DIRECTIVES, ART / "V95_2_ONE_SHOT_RENDER_DIRECTIVES.tsv")
    shutil.copyfile(SOURCE_F7R2, ART / "V95_8_F7R2_RENDERED_UNITS.tsv")

    levels = Counter(row["working_model_level"] for row in lexical)
    assert levels == Counter({
        "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY": 7,
        "W1_WEAK_WORKING": 135,
        "W2_PROVISIONAL_WORKING": 163,
        "W3_SOLID_WORKING_THEORY": 19,
    })
    assert len(complete) == 1586 and len({row["surface"] for row in complete}) == 1582
    assert all(row["working_meaning_de"] for row in complete)
    assert all(row["positive_evidence_de"] and row["counterevidence_de"] for row in complete)
    assert all(row["historical_confirmation"] == HISTORICAL for row in complete)

    result = {
        "experiment_id": "GDT722", "status": STATUS, "target_readings": 5,
        "target_positions": 5, "target_pages": 4, "primary_evidence_bindings": len(evidence),
        "rival_model_rows": len(rivals), "scope_dictionary_rows": len(scope_dictionary),
        "bounded_unsegmented_renderers_selected": 5, "lexical_context_separations": 1,
        "internal_p_decompositions_selected": 0, "component_global_exports": 0,
        "score_credit_families": 0, "score_delta_total": 0,
        "formal_e_run_families": len(formal_family), "opchey_formal_occurrences": 26,
        "opcheey_formal_occurrences": 4, "upstream_unknown_position_rows": len(upstream_unknown),
        "active_lexical_rows": len(lexical), "active_source_readings": len(lexical_by_source),
        "context_positions": len(contexts), "non_target_lexical_rows_preserved": len(lexical) - 5,
        "non_target_context_positions_preserved": len(contexts) - 5,
        "remaining_unreviewed_weak_readings": 47, "confidence_levels": dict(sorted(levels.items())),
        "complete_dictionary_rows": len(complete),
        "complete_dictionary_surfaces": len({row["surface"] for row in complete}),
        "complete_dictionary_rows_with_default_confidence_and_evidence": sum(
            bool(row["working_meaning_de"] and row["working_model_level"] and row["positive_evidence_de"] and row["counterevidence_de"])
            for row in complete
        ),
        "bound_spans_preserved": len(read_tsv(SOURCE_SPANS)),
        "bound_span_execution_rows_preserved": len(read_tsv(SOURCE_SPAN_EXECUTION)),
        "one_shot_directives_preserved": len(read_tsv(SOURCE_DIRECTIVES)),
        "f7r2_output_units": len(read_tsv(SOURCE_F7R2)), "f84_or_f84r_used": 0,
        "historical_confirmation": HISTORICAL,
        "canonical_dictionary": "experiments/yolo/gdt722_v95_op_whole_scope_and_context_separation/artifacts/V95_COMPLETE_WORD_CONFIDENCE.tsv",
    }
    (ART / "RESULT.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
