#!/usr/bin/env python3
"""Build V96 by separating twelve preparation-whole cores from local heads/actions."""

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
sys.path.insert(0, str(ROOT))

from tools.vmanus_experiment import GuardedTSV  # noqa: E402


EXP = ROOT / "experiments/yolo/gdt723_v96_twelve_preparation_bound_core_context_repair"
SRC = EXP / "src"
ART = EXP / "artifacts"
G722 = ROOT / "experiments/yolo/gdt722_v95_op_whole_scope_and_context_separation/artifacts"

SOURCE_LEXICAL = G722 / "V95_324_ACTIVE_LEXICAL_READINGS.tsv"
SOURCE_CONTEXT = G722 / "V95_479_CONTEXT_REALIZATIONS.tsv"
SOURCE_CENSUS = G722 / "V95_52_HELD_READING_AUDIT.tsv"
SOURCE_COMPLETE = G722 / "V95_COMPLETE_WORD_CONFIDENCE.tsv"
SOURCE_SPANS = G722 / "V95_5_BOUND_SPAN_RENDERER.tsv"
SOURCE_SPAN_EXECUTION = G722 / "V95_5_BOUND_SPAN_EXECUTION_AUDIT.tsv"
SOURCE_DIRECTIVES = G722 / "V95_2_ONE_SHOT_RENDER_DIRECTIVES.tsv"
SOURCE_F7R2 = G722 / "V95_8_F7R2_RENDERED_UNITS.tsv"
G691_READER = ROOT / "experiments/yolo/gdt691_preparation_head_role_dispatch/artifacts/V64_479_TOKEN_READER.tsv"
G691_RULES = ROOT / "experiments/yolo/gdt691_preparation_head_role_dispatch/src/V64_EXACT_TOKEN_RULES.tsv"
G652_COVERAGE = ROOT / "experiments/yolo/gdt652_strict_v28_frontier_completion/artifacts/ALL_LINE_CONCRETE_COVERAGE_V29.tsv"
G713_FAMILY = ROOT / "experiments/yolo/gdt713_v86_measure_ckh_core_context_repair/artifacts/V86_8_FAMILY_EVIDENCE.tsv"
SPECS = SRC / "V96_12_AUDIT_SPECS.tsv"

HISTORICAL = "H0_NONE"
ACTION_IDS = {"qocho#1", "ykcho#1", "ytcho#1"}
STATUS = (
    "PASS_V96_12_PREPARATION_HOLDS_REVISED__10_LATER_BOUND_WHOLES_PLUS_1_EXACT_O_CKH_"
    "GRID_PLUS_1_BOUNDARY_SEED_HEAD__3_LOCAL_ACTIONS_SEPARATED__35_WEAK_READINGS_REMAIN__"
    "NO_COMPONENT_EXPORT_NO_SCORE_CREDIT__ALL_H0_NONE"
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


def append_pipe(value: str, addition: str) -> str:
    output: list[str] = []
    for item in [*split_pipe(value), *split_pipe(addition)]:
        if item not in output:
            output.append(item)
    return "|".join(output) if output else "NONE"


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


def rename_v95(row: dict[str, str]) -> dict[str, Any]:
    return {key.replace("v95", "v96").replace("V95", "V96"): value for key, value in row.items()}


def fingerprint(row: dict[str, str]) -> str:
    payload = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def guarded_rows(path: Path, selector: str, allowed: set[str]) -> list[dict[str, str]]:
    assert allowed and all(not value.lower().startswith("f84") for value in allowed)
    source = GuardedTSV(
        path,
        selector_column=selector,
        allowed_values=allowed,
        forbidden_prefixes=("f84",),
        forbidden_action="skip",
    )
    rows = list(source)
    assert all(not row[selector].lower().startswith("f84") for row in rows)
    return rows


def build_lineage(
    specs: list[dict[str, str]],
) -> tuple[list[dict[str, Any]], dict[str, dict[str, str]], dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    allowed_loci = {spec["expected_locus"] for spec in specs}
    coverage_rows = guarded_rows(G652_COVERAGE, "locus", allowed_loci)
    reader_rows = guarded_rows(G691_READER, "locus", allowed_loci)
    rule_rows = read_tsv(G691_RULES)
    coverage_by_locus = {row["locus"]: row for row in coverage_rows}
    reader_by_key = {(row["locus"], row["token_ordinal"]): row for row in reader_rows}
    rule_by_id = {row["rule_id"]: row for row in rule_rows}
    assert len(coverage_by_locus) == 10
    output: list[dict[str, Any]] = []
    target_reader: dict[str, dict[str, str]] = {}
    target_rules: dict[str, dict[str, str]] = {}
    target_coverage: dict[str, dict[str, str]] = {}
    for spec in specs:
        source_id = spec["source_reading_id"]
        coverage = coverage_by_locus[spec["expected_locus"]]
        ordinal = int(spec["expected_token_ordinal"])
        scope_states = split_pipe(coverage["scope_states"])
        glosses = split_pipe(coverage["token_glosses_de"])
        assert len(scope_states) == int(coverage["token_count"])
        assert len(glosses) == int(coverage["token_count"])
        upstream_scope = scope_states[ordinal - 1]
        assert upstream_scope == spec["gdt652_scope_expected"]
        if upstream_scope == "UNKNOWN_SURFACE":
            assert spec["surface"] in split_pipe(coverage["unknown_surfaces"])
            assert str(ordinal) in split_pipe(coverage["unknown_ordinals"])
        elif upstream_scope == "KNOWN_EXACT_WHOLE":
            assert source_id == "chockhy#1"
        elif upstream_scope == "READER_BOUNDARY_UNSTABLE":
            assert source_id == "solchedy#1"
        else:
            raise AssertionError((source_id, upstream_scope))

        reader = reader_by_key[(spec["expected_locus"], spec["expected_token_ordinal"])]
        rule = rule_by_id[spec["gdt691_rule_id"]]
        assert reader["surface"] == spec["surface"] == rule["surface"]
        assert reader["v64_rule_id"] == spec["gdt691_rule_id"]
        assert reader["formal_routes"] == spec["gdt691_formal_route"]
        assert reader["practical_head_de"] == spec["gdt691_practical_head_de"]
        assert rule["v64_main_gloss_de"] == reader["v64_token_gloss_de"]
        target_reader[source_id] = reader
        target_rules[source_id] = rule
        target_coverage[source_id] = coverage
        output.append({
            "source_reading_id": source_id,
            "surface": spec["surface"],
            "position_id": spec["expected_position_id"],
            "page": spec["expected_page"],
            "locus": spec["expected_locus"],
            "token_ordinal": ordinal,
            "gdt652_scope_state": upstream_scope,
            "gdt652_position_gloss_de": glosses[ordinal - 1],
            "gdt691_rule_id": reader["v64_rule_id"],
            "gdt691_decision_class": reader["decision_class"],
            "gdt691_formal_route": reader["formal_routes"],
            "gdt691_practical_head_de": reader["practical_head_de"],
            "gdt691_live_rivals_de": reader["live_rivals_de"],
            "v96_lineage_class": spec["lineage_class"],
            "v96_selected_portable_core_de": spec["v96_lexical_core_de"],
            "v96_selected_local_renderer_de": spec["v96_context_realization_de"],
            "exact_whole_surface_default_allowed": 1,
            "component_global_export_allowed": 0,
            "score_credit": 0,
            "historical_confirmation": HISTORICAL,
        })
    assert Counter(row["gdt652_scope_state"] for row in output) == Counter({
        "UNKNOWN_SURFACE": 10,
        "KNOWN_EXACT_WHOLE": 1,
        "READER_BOUNDARY_UNSTABLE": 1,
    })
    return output, target_reader, target_rules, target_coverage


def build_evidence_bindings(
    specs: list[dict[str, str]],
    source_lexical: list[dict[str, str]],
    source_context: list[dict[str, str]],
    target_reader: dict[str, dict[str, str]],
    target_rules: dict[str, dict[str, str]],
    target_coverage: dict[str, dict[str, str]],
) -> list[dict[str, Any]]:
    lexical_by_id = {
        source_id: row
        for row in source_lexical
        for source_id in split_pipe(row["source_reading_ids"])
    }
    context_by_position = {row["position_id"]: row for row in source_context}
    output: list[dict[str, Any]] = []
    paths = {
        "V95_ACTIVE_LEXICAL": SOURCE_LEXICAL,
        "V95_EXACT_CONTEXT": SOURCE_CONTEXT,
        "GDT691_TOKEN_READER": G691_READER,
        "GDT691_EXACT_RULE": G691_RULES,
        "GDT652_POSITION_LINEAGE": G652_COVERAGE,
    }
    for target_number, spec in enumerate(specs, start=1):
        source_id = spec["source_reading_id"]
        rows = {
            "V95_ACTIVE_LEXICAL": lexical_by_id[source_id],
            "V95_EXACT_CONTEXT": context_by_position[spec["expected_position_id"]],
            "GDT691_TOKEN_READER": target_reader[source_id],
            "GDT691_EXACT_RULE": target_rules[source_id],
            "GDT652_POSITION_LINEAGE": target_coverage[source_id],
        }
        selectors = {
            "V95_ACTIVE_LEXICAL": f"source_reading_ids={source_id}",
            "V95_EXACT_CONTEXT": f"position_id={spec['expected_position_id']}",
            "GDT691_TOKEN_READER": f"locus={spec['expected_locus']};token_ordinal={spec['expected_token_ordinal']}",
            "GDT691_EXACT_RULE": f"rule_id={spec['gdt691_rule_id']}",
            "GDT652_POSITION_LINEAGE": f"locus={spec['expected_locus']}",
        }
        for binding_number, role in enumerate(paths, start=1):
            row = rows[role]
            assert "f84" not in str(paths[role]).lower()
            assert all(not value.lower().startswith("f84") for key, value in row.items() if key in {"page", "locus"})
            output.append({
                "binding_id": f"E{target_number:02d}{binding_number}",
                "source_reading_id": source_id,
                "surface": spec["surface"],
                "evidence_role": role,
                "evidence_path": str(paths[role].relative_to(ROOT)),
                "selector": selectors[role],
                "position_projection": (
                    f"token_ordinal={spec['expected_token_ordinal']};gdt652_scope_state={spec['gdt652_scope_expected']}"
                    if role == "GDT652_POSITION_LINEAGE" else "NONE"
                ),
                "matched_row_fingerprint_sha256": fingerprint(row),
                "source_row_match": 1,
                "score_credit_family_ids": "NONE",
                "evidence_status": "BOUND_EXACT_PRIMARY_ROW",
                "historical_confirmation": HISTORICAL,
            })
    family_matches = [row for row in read_tsv(G713_FAMILY) if row["family_id"] == "F_CKH"]
    assert len(family_matches) == 1
    family = family_matches[0]
    assert family["scope"] == "learned_family_head"
    assert family["minimal_working_value_de"] == "technisches Mischgut oder Kompositum"
    assert family["automatic_historical_credit"] == "0"
    output.append({
        "binding_id": "E02X",
        "source_reading_id": "chockhy#1",
        "surface": "chockhy",
        "evidence_role": "GDT713_CKH_FAMILY_CONTROL",
        "evidence_path": str(G713_FAMILY.relative_to(ROOT)),
        "selector": "family_id=F_CKH",
        "position_projection": "NONE",
        "matched_row_fingerprint_sha256": fingerprint(family),
        "source_row_match": 1,
        "score_credit_family_ids": "NONE",
        "evidence_status": "BOUND_EXACT_FAMILY_ROW",
        "historical_confirmation": HISTORICAL,
    })
    assert len(output) == 61
    assert Counter(row["source_reading_id"] for row in output) == Counter({
        **{spec["source_reading_id"]: 5 for spec in specs},
        "chockhy#1": 6,
    })
    return output


def build_lexical(
    source_rows: list[dict[str, str]], specs: list[dict[str, str]]
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    specs_by_id = {row["source_reading_id"]: row for row in specs}
    output: list[dict[str, Any]] = []
    for source in source_rows:
        row = rename_v95(source)
        source_ids = split_pipe(source["source_reading_ids"])
        spec = specs_by_id.get(source_ids[0]) if len(source_ids) == 1 else None
        if spec:
            source_id = source_ids[0]
            assert source["v95_lexical_core_de"] == spec["expected_old_core_de"]
            score = int(source["working_model_score_0_100_not_probability"])
            assert score == int(spec["expected_old_score"])
            assert source["working_model_level"] == level(score) == "W1_WEAK_WORKING"
            row.update({
                "v96_lexical_core_de": spec["v96_lexical_core_de"],
                "v96_context_realizations_de": spec["v96_context_realization_de"],
                "family_ids": append_pipe(source["family_ids"], spec["family_ids"]),
                "decomposition": spec["decomposition"],
                "repair_modes": spec["repair_mode"],
                "resolved_debt_atoms": spec["resolved_debt_atom"],
                "last_semantic_writer": "GDT723",
                "base_score": score,
                "score_delta_lexical_core": 0,
                "working_model_score_0_100_not_probability": score,
                "working_model_level": level(score),
                "context_realization_score_0_100_not_probability": score,
                "context_realization_level": level(score),
                "source_gdts": append_pipe(source["source_gdts"], "GDT723"),
                "positive_evidence_de": (
                    "GDT723 trennt portablen Kern und exakte Fundstellenausgabe: "
                    + spec["evidence_de"] + " || " + source["positive_evidence_de"]
                ),
                "counterevidence_de": (
                    "GDT723 Grenze: " + spec["counterevidence_de"]
                    + " || Historisch unbestaetigte Arbeitstheorie; keine Klartextidentifikation."
                ),
                "v96_audit_decision": "REVISE_CORE_AND_CONTEXT_SCOPE",
                "v96_evidence_class": spec["evidence_class"],
                "v96_open_semantic_slots": spec["open_semantic_slots"],
                "v96_component_global_export_allowed": "0",
                "v96_exact_whole_surface_default_allowed": "1",
                "v96_lineage_class": spec["lineage_class"],
                "v96_prior_lexical_core_de": source["v95_lexical_core_de"],
            })
            if source_id in ACTION_IDS:
                forbidden = ("nehmen", "bereiten", "herstellen", "hieraus")
                assert not any(word in spec["v96_lexical_core_de"].lower() for word in forbidden)
        else:
            row.update({
                "v96_audit_decision": "NOT_IN_GDT723_TRANCHE",
                "v96_evidence_class": "INHERITED_V95",
                "v96_open_semantic_slots": "NOT_EVALUATED",
                "v96_component_global_export_allowed": "NOT_EVALUATED",
                "v96_exact_whole_surface_default_allowed": "NOT_EVALUATED",
                "v96_lineage_class": "INHERITED_V95",
                "v96_prior_lexical_core_de": source["v95_lexical_core_de"],
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
        row = rename_v95(source)
        if spec:
            seen[source_id] += 1
            assert (source["position_id"], source["page"], source["locus"], source["token_ordinal"]) == (
                spec["expected_position_id"], spec["expected_page"], spec["expected_locus"], spec["expected_token_ordinal"]
            )
            ordinal = int(source["token_ordinal"])
            left = "<BOS>" if ordinal == 1 else by_locus_ordinal[(source["locus"], ordinal - 1)]["surface"]
            right = "<EOS>" if (source["locus"], ordinal + 1) not in by_locus_ordinal else by_locus_ordinal[(source["locus"], ordinal + 1)]["surface"]
            assert (left, right, source["v68_action_license"]) == (
                spec["expected_left_surface"], spec["expected_right_surface"], spec["expected_action_license"]
            )
            if source_id in ACTION_IDS:
                assert source["v68_clause_type"] == "ACTION_CLAUSE"
            else:
                assert source["v68_clause_type"] == "NOMINAL_BLOCK"
        row.update({
            "v96_reading_id": lexical["v96_reading_id"],
            "v96_lexical_core_de": lexical["v96_lexical_core_de"],
            "v96_context_realization_de": spec["v96_context_realization_de"] if spec else source["v95_context_realization_de"],
            "v96_repair_mode": spec["repair_mode"] if spec else source["v95_repair_mode"],
            "v96_resolved_debt_atom": spec["resolved_debt_atom"] if spec else source["v95_resolved_debt_atom"],
            "v96_lexical_score": lexical["working_model_score_0_100_not_probability"],
            "v96_lexical_level": lexical["working_model_level"],
            "v96_context_score": lexical["context_realization_score_0_100_not_probability"],
            "v96_context_level": lexical["context_realization_level"],
            "v96_semantic_scope": lexical["semantic_scope"],
            "v96_semantic_applicability": lexical["semantic_applicability"],
            "v96_global_export_scope": lexical["global_export_scope"],
            "v96_lexical_bound_span_ids": lexical["bound_span_ids"],
            "v96_unconditional_global_export_allowed": lexical["unconditional_global_export_allowed"],
            "v96_historical_confirmation": HISTORICAL,
            "v96_audit_decision": "REVISE_CORE_AND_CONTEXT_SCOPE" if spec else "NOT_IN_GDT723_TRANCHE",
            "v96_evidence_class": spec["evidence_class"] if spec else "INHERITED_V95",
            "v96_open_semantic_slots": spec["open_semantic_slots"] if spec else "NOT_EVALUATED",
            "v96_component_global_export_allowed": "0" if spec else "NOT_EVALUATED",
            "v96_exact_whole_surface_default_allowed": "1" if spec else "NOT_EVALUATED",
            "v96_lineage_class": spec["lineage_class"] if spec else "INHERITED_V95",
            "v96_local_context_hypothesis": spec["local_context_hypothesis"] if spec else "NONE",
            "v96_expected_left_surface": spec["expected_left_surface"] if spec else "NONE",
            "v96_expected_right_surface": spec["expected_right_surface"] if spec else "NONE",
        })
        output.append(row)
    assert len(output) == 479
    assert seen == Counter({source_id: 1 for source_id in specs_by_id})
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
        row = rename_v95(source)
        if spec:
            row.update({
                "disposition": "REVISED_IN_V96",
                "repair_mode": spec["repair_mode"],
                "resolved_debt_atom": spec["resolved_debt_atom"],
                "v96_reading_id": lexical["v96_reading_id"],
                "v96_lexical_core_de": lexical["v96_lexical_core_de"],
                "v96_context_realization_de": spec["v96_context_realization_de"],
                "new_lexical_score": lexical["working_model_score_0_100_not_probability"],
                "new_lexical_level": lexical["working_model_level"],
                "new_context_score": lexical["context_realization_score_0_100_not_probability"],
                "new_context_level": lexical["context_realization_level"],
                "positive_evidence_de": spec["evidence_de"],
                "counterevidence_de": spec["counterevidence_de"],
                "v96_audit_decision": "REVISE_CORE_AND_CONTEXT_SCOPE",
                "v96_evidence_class": spec["evidence_class"],
                "v96_open_semantic_slots": spec["open_semantic_slots"],
                "v96_lineage_class": spec["lineage_class"],
            })
        else:
            row.update({
                "v96_reading_id": lexical["v96_reading_id"],
                "v96_lexical_core_de": lexical["v96_lexical_core_de"],
                "v96_context_realization_de": lexical["v96_context_realizations_de"],
                "new_lexical_score": lexical["working_model_score_0_100_not_probability"],
                "new_lexical_level": lexical["working_model_level"],
                "new_context_score": lexical["context_realization_score_0_100_not_probability"],
                "new_context_level": lexical["context_realization_level"],
                "v96_audit_decision": "HELD_FOR_LATER_REPAIR",
                "v96_evidence_class": "INHERITED_V95",
                "v96_open_semantic_slots": "NOT_EVALUATED",
                "v96_lineage_class": "INHERITED_V95",
            })
        output.append(row)
    assert len(output) == 47
    assert Counter(row["disposition"] for row in output) == Counter({
        "HELD_FOR_LATER_REPAIR": 35,
        "REVISED_IN_V96": 12,
    })
    return output


def build_delta(
    source_rows: list[dict[str, str]], specs: list[dict[str, str]], lexical_by_source: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    source_by_id = {
        source_id: row for row in source_rows for source_id in split_pipe(row["source_reading_ids"])
    }
    output: list[dict[str, Any]] = []
    for spec in specs:
        source = source_by_id[spec["source_reading_id"]]
        target = lexical_by_source[spec["source_reading_id"]]
        output.append({
            "source_reading_id": spec["source_reading_id"],
            "surface": spec["surface"],
            "position_id": spec["expected_position_id"],
            "page": spec["expected_page"],
            "locus": spec["expected_locus"],
            "token_ordinal": spec["expected_token_ordinal"],
            "left_surface": spec["expected_left_surface"],
            "right_surface": spec["expected_right_surface"],
            "old_lexical_core_de": source["v95_lexical_core_de"],
            "v96_lexical_core_de": target["v96_lexical_core_de"],
            "v96_context_realization_de": spec["v96_context_realization_de"],
            "portable_role": spec["portable_role"],
            "old_score": source["working_model_score_0_100_not_probability"],
            "v96_score": target["working_model_score_0_100_not_probability"],
            "old_level": source["working_model_level"],
            "v96_level": target["working_model_level"],
            "family_ids": spec["family_ids"],
            "score_credit_family_ids": "NONE",
            "decomposition": spec["decomposition"],
            "lineage_class": spec["lineage_class"],
            "repair_mode": spec["repair_mode"],
            "evidence_de": spec["evidence_de"],
            "counterevidence_de": spec["counterevidence_de"],
            "open_semantic_slots": spec["open_semantic_slots"],
            "exact_whole_surface_default_allowed": 1,
            "component_global_export_allowed": 0,
            "historical_confirmation": HISTORICAL,
        })
    return output


def build_scope_dictionary() -> list[dict[str, Any]]:
    return [
        {
            "scope_item": "TEN_LATER_BOUND_WHOLES",
            "surfaces": "adeeody|ofchedy|okeeeey|okiin|olord|otsheody|qocho|shotchey|ykcho|ytcho",
            "portable_value_de": "exakter Mengen-, Material- oder Zustandskern je Ganzoberfläche",
            "local_only_content_de": "Zubereitung|Masse|Holzauszug|Mazerat|Droge|Quelle|Aktionsverb",
            "lineage": "GDT691_LEARNED_WHOLE_OR_UNEXPORTED_OR_PROVISIONAL_LOCAL_SCOPE",
            "status": "BOUND_EXACT_SURFACE_DEFAULTS",
            "exact_whole_surface_default_allowed": 1,
            "component_or_substring_global_export_allowed": 0,
            "score_credit": 0,
            "historical_confirmation": HISTORICAL,
        },
        {
            "scope_item": "CHOCKHY_EXACT_O_CKH_GRID",
            "surfaces": "chockhy",
            "portable_value_de": "trockene Mischung, Anfangsstufe",
            "local_only_content_de": "Arzneizubereitung",
            "lineage": "GDT652_KNOWN_EXACT_WHOLE|GDT691_GDT652_EXACT_O_PREP_SURFACE|GDT713_CKH_MIXTURE_CORE",
            "status": "EARLIER_EXACT_GRID_BOUND",
            "exact_whole_surface_default_allowed": 1,
            "component_or_substring_global_export_allowed": 0,
            "score_credit": 0,
            "historical_confirmation": HISTORICAL,
        },
        {
            "scope_item": "SOLCHEDY_BOUNDARY_SEED_HEAD",
            "surfaces": "solchedy",
            "portable_value_de": "Samenmaterial; bis zur Mittelstufe getrocknet",
            "local_only_content_de": "Samenmasse",
            "lineage": "GDT652_READER_BOUNDARY_UNSTABLE|GDT691_PRODUCTIVE_HEAD",
            "status": "BOUND_SEED_HEAD_NO_FREE_CHEDY_DY",
            "exact_whole_surface_default_allowed": 1,
            "component_or_substring_global_export_allowed": 0,
            "score_credit": 0,
            "historical_confirmation": HISTORICAL,
        },
        {
            "scope_item": "YKCHO_YTCHO_PAIRED_WHOLES",
            "surfaces": "ykcho|ytcho",
            "portable_value_de": "warme Trockenmischung|kalte Trockenmischung",
            "local_only_content_de": "hieraus|bereiten|herstellen",
            "lineage": "GDT691_PAIRED_LEARNED_WHOLE_CONTRAST",
            "status": "PAIR_ONLY_NO_K_T_CHO_EXPORT",
            "exact_whole_surface_default_allowed": 1,
            "component_or_substring_global_export_allowed": 0,
            "score_credit": 0,
            "historical_confirmation": HISTORICAL,
        },
        {
            "scope_item": "LOCAL_PRODUCT_HEADS",
            "surfaces": "all_12_targets",
            "portable_value_de": "state|stage|quantity|material identity where active",
            "local_only_content_de": "Arzneizubereitung|Zubereitung|Masse|Holzauszug|Mazerat|Droge",
            "lineage": "EXACT_POSITION_RENDERER_CHOICE",
            "status": "LOCAL_HEADS_RETAINED_AS_WORKING_RENDERERS",
            "exact_whole_surface_default_allowed": 1,
            "component_or_substring_global_export_allowed": 0,
            "score_credit": 0,
            "historical_confirmation": HISTORICAL,
        },
        {
            "scope_item": "LOCAL_ACTION_AND_SOURCE_WORDING",
            "surfaces": "qocho|ykcho|ytcho",
            "portable_value_de": "Trockengut|warme Trockenmischung|kalte Trockenmischung",
            "local_only_content_de": "nehmen|hieraus bereiten|hieraus herstellen",
            "lineage": "P238|P242|P209_ACTION_LICENSE_ONLY",
            "status": "LEXICAL_CONTEXT_SEPARATED",
            "exact_whole_surface_default_allowed": 1,
            "component_or_substring_global_export_allowed": 0,
            "score_credit": 0,
            "historical_confirmation": HISTORICAL,
        },
    ]


def build_rivals(specs: list[dict[str, str]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for spec in specs:
        output.extend([
            {
                "source_reading_id": spec["source_reading_id"],
                "surface": spec["surface"],
                "model_id": "A_BOUND_CORE_PLUS_EXACT_LOCAL_RENDERER",
                "candidate_portable_default_de": spec["v96_lexical_core_de"],
                "candidate_local_renderer_de": spec["v96_context_realization_de"],
                "decision": "SELECT",
                "evidence_fit_de": spec["evidence_de"],
                "conflict_de": spec["counterevidence_de"],
                "portable_default_selected": 1,
                "component_global_export_allowed": 0,
                "score_credit": 0,
            },
            {
                "source_reading_id": spec["source_reading_id"],
                "surface": spec["surface"],
                "model_id": "B_OLD_FULL_PRODUCT_OR_ACTION_AS_PORTABLE_WORD",
                "candidate_portable_default_de": spec["expected_old_core_de"],
                "candidate_local_renderer_de": spec["expected_old_core_de"],
                "decision": "REJECT_AS_PORTABLE_KEEP_WHERE_LOCAL",
                "evidence_fit_de": "Bleibt an der bekannten Einzelposition praktisch lesbar.",
                "conflict_de": "Schreibt einen ersetzbaren Produktkopf, eine Quelle oder ein Aktionsverb in den portablen Wortwert ein.",
                "portable_default_selected": 0,
                "component_global_export_allowed": 0,
                "score_credit": 0,
            },
            {
                "source_reading_id": spec["source_reading_id"],
                "surface": spec["surface"],
                "model_id": "C_UNRELATED_LEARNED_TECHNICAL_WHOLE",
                "candidate_portable_default_de": "anderer gelernter technischer Ganzwert",
                "candidate_local_renderer_de": "offen",
                "decision": "KEEP_COUNTERMODEL",
                "evidence_fit_de": "Singleton- oder gebundene Ganzformherkunft bleibt mit einem nicht segmentierten Codebookwert vereinbar.",
                "conflict_de": "Erklaert die bereits gebundenen Mengen-, Material-, Zustands- und Stufensignale nicht besser.",
                "portable_default_selected": 0,
                "component_global_export_allowed": 0,
                "score_credit": 0,
            },
        ])
    assert len(output) == 36
    return output


def build_target_renderer(
    contexts: list[dict[str, Any]], specs: list[dict[str, str]]
) -> list[dict[str, Any]]:
    by_position = {row["position_id"]: row for row in contexts}
    output: list[dict[str, Any]] = []
    for spec in specs:
        row = by_position[spec["expected_position_id"]]
        output.append({
            "position_id": row["position_id"],
            "page": row["page"],
            "locus": row["locus"],
            "token_ordinal": row["token_ordinal"],
            "surface": row["surface"],
            "left_surface": spec["expected_left_surface"],
            "right_surface": spec["expected_right_surface"],
            "portable_lexical_core_de": row["v96_lexical_core_de"],
            "local_context_realization_de": row["v96_context_realization_de"],
            "action_license": row["v68_action_license"],
            "lineage_class": spec["lineage_class"],
            "decomposition": spec["decomposition"],
            "exact_whole_surface_default_allowed": 1,
            "component_global_export_allowed": 0,
            "score": row["v96_lexical_score"],
            "level": row["v96_lexical_level"],
            "historical_confirmation": HISTORICAL,
        })
    return output


def build_action_head_separation(specs: list[dict[str, str]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    local_leak = {
        "adeeody#1": "Zubereitung",
        "chockhy#1": "Arzneizubereitung",
        "ofchedy#1": "Masse",
        "okeeeey#1": "Zubereitung",
        "okiin#1": "Zubereitung",
        "olord#1": "Holzauszug",
        "otsheody#1": "Mazerat",
        "qocho#1": "Droge|nehmen",
        "shotchey#1": "Mazerat",
        "solchedy#1": "Masse",
        "ykcho#1": "hieraus|bereiten",
        "ytcho#1": "hieraus|herstellen",
    }
    for spec in specs:
        source_id = spec["source_reading_id"]
        action = source_id in ACTION_IDS
        output.append({
            "source_reading_id": source_id,
            "surface": spec["surface"],
            "position_id": spec["expected_position_id"],
            "position_is_action_licensed": int(action),
            "portable_lexical_core_de": spec["v96_lexical_core_de"],
            "local_context_realization_de": spec["v96_context_realization_de"],
            "local_only_words_or_heads": local_leak[source_id],
            "portable_action_export_allowed": 0,
            "portable_product_head_export_allowed": 0,
            "component_global_export_allowed": 0,
            "audit_status": "PASS_LOCAL_ACTION_SEPARATED" if action else "PASS_NOMINAL_NO_HIDDEN_ACTION",
            "historical_confirmation": HISTORICAL,
        })
    assert sum(row["position_is_action_licensed"] for row in output) == 3
    return output


def build_complete(source_rows: list[dict[str, str]], lexical: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for source in source_rows:
        if source["current_layer"] == "ACTIVE_V95_LEXICAL_CORE":
            continue
        row = rename_v95(source)
        row.update({
            "v96_audit_decision": "OUTSIDE_ACTIVE_V96_TRANCHE",
            "v96_evidence_class": "INHERITED_GLOBAL_V48",
            "v96_open_semantic_slots": "NOT_EVALUATED",
            "v96_component_global_export_allowed": "NOT_EVALUATED",
            "v96_exact_whole_surface_default_allowed": "NOT_EVALUATED",
            "v96_lineage_class": "INHERITED_GLOBAL_V48",
        })
        output.append(row)
    for row in lexical:
        output.append({
            "surface": row["surface"],
            "reading_id": row["v96_reading_id"],
            "working_meaning_de": row["v96_lexical_core_de"],
            "current_layer": "ACTIVE_V96_LEXICAL_CORE",
            "semantic_scope": row["semantic_scope"],
            "semantic_applicability": row["semantic_applicability"],
            "form_level": row["form_level"],
            "occurrence_count": row["occurrence_count"],
            "page_count": row["page_count"],
            "locus_count": row["locus_count"],
            "working_model_score_0_100_not_probability": row["working_model_score_0_100_not_probability"],
            "working_model_level": row["working_model_level"],
            "source_gdts": row["source_gdts"],
            "positive_evidence_de": row["positive_evidence_de"],
            "counterevidence_de": row["counterevidence_de"],
            "historical_confirmation": row["historical_confirmation"],
            "historical_analogue": row["historical_analogue"],
            "relation_word_delta": row["relation_word_delta"],
            "global_export_scope": row["global_export_scope"],
            "bound_span_ids": row["bound_span_ids"],
            "unconditional_global_export_allowed": row["unconditional_global_export_allowed"],
            "v96_context_realizations_de": row["v96_context_realizations_de"],
            "source_reading_ids": row["source_reading_ids"],
            "v96_audit_decision": row["v96_audit_decision"],
            "v96_evidence_class": row["v96_evidence_class"],
            "v96_open_semantic_slots": row["v96_open_semantic_slots"],
            "v96_component_global_export_allowed": row["v96_component_global_export_allowed"],
            "v96_exact_whole_surface_default_allowed": row["v96_exact_whole_surface_default_allowed"],
            "v96_lineage_class": row["v96_lineage_class"],
        })
    return sorted(output, key=lambda row: (str(row["surface"]), str(row["reading_id"])))


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    specs = read_tsv(SPECS)
    assert len(specs) == 12
    assert len({row["source_reading_id"] for row in specs}) == 12
    assert {row["source_reading_id"] for row in specs} == {
        "adeeody#1", "chockhy#1", "ofchedy#1", "okeeeey#1", "okiin#1", "olord#1",
        "otsheody#1", "qocho#1", "shotchey#1", "solchedy#1", "ykcho#1", "ytcho#1",
    }
    assert all("f84" not in row["expected_page"].lower() for row in specs)

    source_lexical = read_tsv(SOURCE_LEXICAL)
    source_context = read_tsv(SOURCE_CONTEXT)
    source_census = read_tsv(SOURCE_CENSUS)
    source_complete = read_tsv(SOURCE_COMPLETE)
    lineage, target_reader, target_rules, target_coverage = build_lineage(specs)
    evidence = build_evidence_bindings(
        specs, source_lexical, source_context, target_reader, target_rules, target_coverage
    )
    lexical, lexical_by_source = build_lexical(source_lexical, specs)
    contexts = build_contexts(source_context, specs, lexical_by_source)
    census = build_census(source_census, specs, lexical_by_source)
    delta = build_delta(source_lexical, specs, lexical_by_source)
    scope_dictionary = build_scope_dictionary()
    rivals = build_rivals(specs)
    target_renderer = build_target_renderer(contexts, specs)
    action_head = build_action_head_separation(specs)
    complete = build_complete(source_complete, lexical)

    write_tsv(ART / "V96_324_ACTIVE_LEXICAL_READINGS.tsv", lexical)
    write_tsv(ART / "V96_479_CONTEXT_REALIZATIONS.tsv", contexts)
    write_tsv(ART / "V96_47_HELD_READING_AUDIT.tsv", census)
    write_tsv(ART / "V96_12_PREPARATION_CORE_CONTEXT_DELTA.tsv", delta)
    write_tsv(ART / "V96_6_SCOPE_DICTIONARY.tsv", scope_dictionary)
    write_tsv(ART / "V96_36_RIVAL_MODEL_COMPARISON.tsv", rivals)
    write_tsv(ART / "V96_61_PRIMARY_EVIDENCE_BINDINGS.tsv", evidence)
    write_tsv(ART / "V96_12_LINEAGE_AUDIT.tsv", lineage)
    write_tsv(ART / "V96_12_TARGET_RENDERER.tsv", target_renderer)
    write_tsv(ART / "V96_12_ACTION_HEAD_SEPARATION.tsv", action_head)
    write_tsv(ART / "V96_COMPLETE_WORD_CONFIDENCE.tsv", complete)
    shutil.copyfile(SOURCE_SPANS, ART / "V96_5_BOUND_SPAN_RENDERER.tsv")
    shutil.copyfile(SOURCE_SPAN_EXECUTION, ART / "V96_5_BOUND_SPAN_EXECUTION_AUDIT.tsv")
    shutil.copyfile(SOURCE_DIRECTIVES, ART / "V96_2_ONE_SHOT_RENDER_DIRECTIVES.tsv")
    shutil.copyfile(SOURCE_F7R2, ART / "V96_8_F7R2_RENDERED_UNITS.tsv")

    levels = Counter(row["working_model_level"] for row in lexical)
    assert levels == Counter({
        "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY": 7,
        "W1_WEAK_WORKING": 135,
        "W2_PROVISIONAL_WORKING": 163,
        "W3_SOLID_WORKING_THEORY": 19,
    })
    assert len(complete) == 1586 and len({row["surface"] for row in complete}) == 1582
    assert all(row["working_meaning_de"] for row in complete)
    assert all(row["working_model_level"] for row in complete)
    assert all(row["positive_evidence_de"] and row["counterevidence_de"] for row in complete)
    assert all(row["historical_confirmation"] == HISTORICAL for row in complete)
    assert all(row["component_global_export_allowed"] == 0 for row in delta)
    assert all(int(row["old_score"]) == int(row["v96_score"]) for row in delta)

    result = {
        "experiment_id": "GDT723",
        "status": STATUS,
        "target_readings": 12,
        "target_positions": 12,
        "target_pages": len({row["expected_page"] for row in specs}),
        "primary_evidence_bindings": len(evidence),
        "rival_model_rows": len(rivals),
        "scope_dictionary_rows": len(scope_dictionary),
        "later_bound_whole_or_local_scope_rows": 10,
        "earlier_exact_o_ckh_grid_rows": 1,
        "earlier_boundary_seed_head_rows": 1,
        "action_positions_with_lexical_action_separation": 3,
        "nominal_positions_without_hidden_action": 9,
        "exact_whole_surface_defaults_allowed": 12,
        "component_global_exports": 0,
        "score_credit_families": 0,
        "score_delta_total": 0,
        "upstream_scope_states": dict(sorted(Counter(row["gdt652_scope_state"] for row in lineage).items())),
        "active_lexical_rows": len(lexical),
        "active_source_readings": len(lexical_by_source),
        "context_positions": len(contexts),
        "non_target_lexical_rows_preserved": len(lexical) - 12,
        "non_target_context_positions_preserved": len(contexts) - 12,
        "remaining_unreviewed_weak_readings": 35,
        "confidence_levels": dict(sorted(levels.items())),
        "complete_dictionary_rows": len(complete),
        "complete_dictionary_surfaces": len({row["surface"] for row in complete}),
        "complete_dictionary_rows_with_default_confidence_and_evidence": sum(
            bool(row["working_meaning_de"] and row["working_model_level"] and row["positive_evidence_de"] and row["counterevidence_de"])
            for row in complete
        ),
        "bound_spans_preserved": len(read_tsv(SOURCE_SPANS)),
        "bound_span_execution_rows_preserved": len(read_tsv(SOURCE_SPAN_EXECUTION)),
        "one_shot_directives_preserved": len(read_tsv(SOURCE_DIRECTIVES)),
        "f7r2_output_units": len(read_tsv(SOURCE_F7R2)),
        "f84_or_f84r_used": 0,
        "historical_confirmation": HISTORICAL,
        "canonical_dictionary": "experiments/yolo/gdt723_v96_twelve_preparation_bound_core_context_repair/artifacts/V96_COMPLETE_WORD_CONFIDENCE.tsv",
    }
    (ART / "RESULT.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
