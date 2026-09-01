#!/usr/bin/env python3
"""Build V87 by repairing eighteen bound-C1 readings and one local join."""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

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

HISTORICAL = "H0_NONE"
STATUS = (
    "PASS_V87_18_BOUND_C1_READINGS_REVISED__18_TARGET_POSITIONS_12_PAGES__"
    "1_KEO_R_ONE_SHOT_SPAN__7_W0_135_W1_163_W2_19_W3__"
    "91_WEAK_READINGS_REMAIN__ALL_H0_NONE"
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, fields: list[str], rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for source in rows:
            writer.writerow({field: source.get(field, "") for field in fields})


def split_pipe(value: str) -> list[str]:
    return [part.strip() for part in value.split("|") if part.strip() and part.strip() not in {"NONE", "0"}]


def parse_assertions(value: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for part in value.split(";"):
        if not part:
            continue
        field, expected = part.split("=", 1)
        assert field and field not in result
        result[field] = expected
    return result


def ordered_compact(values: Iterable[str], separator: str = "|", empty: str = "NONE") -> str:
    result: list[str] = []
    seen: set[str] = set()
    for raw in values:
        value = raw.strip()
        if value and value not in {"NONE", "0"} and value not in seen:
            seen.add(value)
            result.append(value)
    return separator.join(result) if result else empty


def append_pipe(value: str, addition: str) -> str:
    return ordered_compact([*split_pipe(value), addition])


def unique_fields(fields: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(fields))


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


def v87_key(value: str) -> str:
    return value.replace("v86", "v87").replace("V86", "V87")


def rename_v86_fields(row: dict[str, str]) -> dict[str, str]:
    return {v87_key(key): value for key, value in row.items()}


def family_v87_key(value: str) -> str:
    return value.replace("v84", "v87").replace("V84", "V87")


def lexical_rows(
    source_rows: list[dict[str, str]],
    specs: list[dict[str, str]],
    derived_score_deltas: dict[str, int],
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    specs_by_id = {row["source_reading_id"]: row for row in specs}
    output: list[dict[str, Any]] = []
    for source in source_rows:
        row: dict[str, Any] = rename_v86_fields(source)
        source_ids = split_pipe(source["source_reading_ids"])
        spec = specs_by_id.get(source_ids[0]) if len(source_ids) == 1 else None
        if spec:
            assert source["v86_lexical_core_de"] == spec["old_lexical_core_de"]
            base = int(source["working_model_score_0_100_not_probability"])
            score_delta = derived_score_deltas[spec["source_reading_id"]]
            assert score_delta == int(spec["score_delta_lexical_core"])
            score = min(base + score_delta, int(spec["lexical_core_cap"]))
            context_score = min(score, int(spec["context_realization_cap"]))
            row.update({
                "v87_lexical_core_de": spec["v87_lexical_core_de"],
                "v87_context_realizations_de": spec["v87_context_realization_de"],
                "family_ids": spec["family_ids"],
                "decomposition": spec["decomposition"],
                "repair_modes": spec["repair_mode"],
                "resolved_debt_atoms": spec["resolved_debt_atom"],
                "last_semantic_writer": "GDT714",
                "base_score": base,
                "score_delta_lexical_core": score_delta,
                "lexical_core_cap": spec["lexical_core_cap"],
                "working_model_score_0_100_not_probability": score,
                "working_model_level": level(score),
                "context_realization_cap": spec["context_realization_cap"],
                "context_realization_score_0_100_not_probability": context_score,
                "context_realization_level": level(context_score),
                "source_gdts": append_pipe(source["source_gdts"], "GDT714"),
                "positive_evidence_de": (
                    "GDT714 trennt erneut Wortkern und lokale Realisierung: "
                    + spec["evidence_de"] + " || " + source["positive_evidence_de"]
                ),
                "counterevidence_de": (
                    "GDT714 Gegenbeleg: " + spec["counterevidence_de"]
                    + " || Historisch unbestaetigte Arbeitstheorie; keine Klartextidentifikation."
                ),
            })
            if spec["occurrence_bound_span_override"] != "NONE":
                row.update({
                    "semantic_scope": "BOUND_SPAN_LOCAL_READING",
                    "semantic_applicability": "COMPOUND_ONLY_LOCAL_READING",
                    "global_export_scope": "BOUND_SPAN_ONLY_NO_GLOBAL_EXPORT",
                    "bound_span_ids": spec["occurrence_bound_span_override"],
                    "unconditional_global_export_allowed": 0,
                })
            row.update({
                "v87_audit_decision": spec["decision"],
                "v87_evidence_class": spec["evidence_class"],
                "v87_open_semantic_slots": spec["open_semantic_slots"],
                "v87_component_global_export_allowed": spec["component_global_export_allowed"],
                "v87_prior_lexical_core_de": source["v86_lexical_core_de"],
            })
        else:
            row.update({
                "v87_audit_decision": "NOT_IN_GDT714_TRANCHE",
                "v87_evidence_class": "INHERITED_V86",
                "v87_open_semantic_slots": "NOT_EVALUATED",
                "v87_component_global_export_allowed": "NOT_EVALUATED",
                "v87_prior_lexical_core_de": source["v86_lexical_core_de"],
            })
        output.append(row)

    by_source: dict[str, dict[str, Any]] = {}
    for row in output:
        for source_id in split_pipe(str(row["source_reading_ids"])):
            assert source_id not in by_source
            by_source[source_id] = row
    assert len(by_source) == 332
    return output, by_source


def context_rows(
    source_rows: list[dict[str, str]],
    specs: list[dict[str, str]],
    lexical_by_source: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    specs_by_id = {row["source_reading_id"]: row for row in specs}
    output: list[dict[str, Any]] = []
    for source in source_rows:
        row: dict[str, Any] = rename_v86_fields(source)
        source_id = source["source_reading_id"]
        lexical = lexical_by_source[source_id]
        spec = specs_by_id.get(source_id)
        row.update({
            "v87_reading_id": lexical["v87_reading_id"],
            "v87_lexical_core_de": lexical["v87_lexical_core_de"],
            "v87_context_realization_de": spec["v87_context_realization_de"] if spec else source["v86_context_realization_de"],
            "v87_repair_mode": spec["repair_mode"] if spec else source["v86_repair_mode"],
            "v87_resolved_debt_atom": spec["resolved_debt_atom"] if spec else source["v86_resolved_debt_atom"],
            "v87_lexical_score": lexical["working_model_score_0_100_not_probability"],
            "v87_lexical_level": lexical["working_model_level"],
            "v87_context_score": lexical["context_realization_score_0_100_not_probability"],
            "v87_context_level": lexical["context_realization_level"],
            "v87_semantic_scope": lexical["semantic_scope"],
            "v87_semantic_applicability": lexical["semantic_applicability"],
            "v87_global_export_scope": lexical["global_export_scope"],
            "v87_lexical_bound_span_ids": lexical["bound_span_ids"],
            "v87_unconditional_global_export_allowed": lexical["unconditional_global_export_allowed"],
            "v87_historical_confirmation": HISTORICAL,
            "v87_audit_decision": spec["decision"] if spec else "NOT_IN_GDT714_TRANCHE",
            "v87_evidence_class": spec["evidence_class"] if spec else "INHERITED_V86",
            "v87_open_semantic_slots": spec["open_semantic_slots"] if spec else "NOT_EVALUATED",
            "v87_component_global_export_allowed": spec["component_global_export_allowed"] if spec else "NOT_EVALUATED",
            "v87_boundary_decision": "NONE",
            "v87_boundary_render_once_de": "NONE",
        })
        if spec and spec["occurrence_bound_span_override"] != "NONE":
            row.update({
                "v87_occurrence_bound_span_id": spec["occurrence_bound_span_override"],
                "v87_occurrence_bound_span_role": spec["occurrence_bound_span_role_override"],
                "v87_occurrence_bound_span_global_export_allowed": spec["occurrence_bound_span_export_override"],
            })
        output.append(row)
    return output


def apply_boundary_specs(
    rows: list[dict[str, Any]], boundary_specs: list[dict[str, str]]
) -> list[dict[str, Any]]:
    """Install only the enumerated occurrence-local LEFT/RIGHT joins."""
    by_position = {str(row["position_id"]): row for row in rows}
    assert len(by_position) == len(rows)
    for spec in boundary_specs:
        for side in ("left", "right"):
            position_id = spec[f"{side}_position_id"]
            row = by_position[position_id]
            assert row["page"] == spec["page"] and row["locus"] == spec["locus"]
            assert row["surface"] == spec[f"{side}_surface"]
            assert row["source_reading_id"] == spec[f"{side}_reading_id"]
            assert row["v87_occurrence_bound_span_id"] == "NONE"
            row.update({
                "v87_occurrence_bound_span_id": spec["bound_span_id"],
                "v87_occurrence_bound_span_role": spec[f"{side}_role"],
                "v87_occurrence_bound_span_global_export_allowed": spec["global_export_allowed"],
                "v87_boundary_decision": spec["resolution_class"],
                "v87_boundary_render_once_de": spec["render_once_de"],
            })
    return rows


def bound_span_rows(
    source_rows: list[dict[str, str]], boundary_specs: list[dict[str, str]]
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = [dict(row) for row in source_rows]
    known = {row["bound_span_id"] for row in output}
    for spec in boundary_specs:
        assert spec["bound_span_id"] not in known
        output.append({field: spec[field] for field in source_rows[0]})
        known.add(spec["bound_span_id"])
    return output


def primary_evidence_rows(
    bindings: list[dict[str, str]], specs: list[dict[str, str]]
) -> list[dict[str, Any]]:
    """Resolve every authored claim against one exact pre-GDT714 table row."""
    specs_by_id = {row["source_reading_id"]: row for row in specs}
    output: list[dict[str, Any]] = []
    for binding in bindings:
        source_id = binding["source_reading_id"]
        spec = specs_by_id[source_id]
        source_path = ROOT / binding["evidence_path"]
        selector = parse_assertions(binding["selector"])
        assertions = parse_assertions(binding["field_assertions"])
        matches = [
            row for row in read_tsv(source_path)
            if all(row.get(field) == expected for field, expected in selector.items())
        ]
        assert len(matches) == 1
        source = matches[0]
        assert source["surface"] == binding["expected_source_surface"]
        if binding["expected_source_decomposition"] == "NONE":
            assert "composition" not in source or source["composition"] in {"", "NONE"}
        else:
            assert source["composition"] == binding["expected_source_decomposition"]
        for field, expected in assertions.items():
            assert source[field] == expected
        assert spec["decomposition"] == binding["normalized_decomposition"]
        assert spec["family_ids"] == binding["score_credit_family_ids"] or set(
            split_pipe(binding["score_credit_family_ids"])
        ).issubset(set(split_pipe(spec["family_ids"])))
        output.append({
            "source_reading_id": source_id,
            "source_gdt": binding["source_gdt"],
            "evidence_path": binding["evidence_path"],
            "selector": binding["selector"],
            "source_surface": source["surface"],
            "source_decomposition": binding["expected_source_decomposition"],
            "normalized_decomposition": binding["normalized_decomposition"],
            "field_assertions": binding["field_assertions"],
            "score_credit_family_ids": binding["score_credit_family_ids"],
            "normalization_class": binding["normalization_class"],
            "source_row_match": 1,
            "evidence_status": "BOUND_EXACT_PRIMARY_ROW",
            "historical_confirmation": HISTORICAL,
        })
    return output


def derived_score_deltas(
    bindings: list[dict[str, str]], source_families: list[dict[str, str]]
) -> dict[str, int]:
    bonus_by_family = {
        row["family_id"]: int(row["family_bonus"])
        for row in source_families
    }
    output: dict[str, int] = {}
    for binding in bindings:
        credit_families = split_pipe(binding["score_credit_family_ids"])
        assert len(credit_families) == len(set(credit_families))
        output[binding["source_reading_id"]] = sum(
            bonus_by_family[family] for family in credit_families
        )
    return output


def one_shot_directive_rows(
    contexts: list[dict[str, Any]], boundary_specs: list[dict[str, str]]
) -> list[dict[str, Any]]:
    by_position = {str(row["position_id"]): row for row in contexts}
    output: list[dict[str, Any]] = []
    for span in boundary_specs:
        for side, action in (("left", "EMIT_SPAN_ONCE"), ("right", "CONSUME_NO_OUTPUT")):
            source = by_position[span[f"{side}_position_id"]]
            output.append({
                "render_unit_id": f"R_{span['bound_span_id']}",
                "page": span["page"],
                "locus": span["locus"],
                "bound_span_id": span["bound_span_id"],
                "anchor_position_id": span["left_position_id"],
                "source_position_id": source["position_id"],
                "source_token_ordinal": source["token_ordinal"],
                "source_surface": source["surface"],
                "source_reading_id": source["source_reading_id"],
                "span_role": span[f"{side}_role"],
                "render_action": action,
                "emitted_text_de": span["render_once_de"] if side == "left" else "",
                "source_context_consumed": 1,
                "global_export_allowed": span["global_export_allowed"],
            })
    return output


def rendered_locus_rows(
    contexts: list[dict[str, Any]], directives: list[dict[str, Any]], locus: str
) -> list[dict[str, Any]]:
    source_rows = sorted(
        (row for row in contexts if row["locus"] == locus),
        key=lambda row: int(row["token_ordinal"]),
    )
    directives_by_position = {row["source_position_id"]: row for row in directives}
    output: list[dict[str, Any]] = []
    for source in source_rows:
        directive = directives_by_position.get(str(source["position_id"]))
        if directive and directive["render_action"] == "CONSUME_NO_OUTPUT":
            continue
        if directive:
            span_positions = [
                row["source_position_id"] for row in directives
                if row["render_unit_id"] == directive["render_unit_id"]
            ]
            span_surfaces = [
                row["source_surface"] for row in directives
                if row["render_unit_id"] == directive["render_unit_id"]
            ]
            rendered = directive["emitted_text_de"]
            source_kind = "BOUND_SPAN"
            source_ref = directive["bound_span_id"]
        else:
            span_positions = [str(source["position_id"])]
            span_surfaces = [str(source["surface"])]
            rendered = source["v87_context_realization_de"]
            source_kind = "CONTEXT_POSITION"
            source_ref = source["position_id"]
        output.append({
            "output_ordinal": len(output) + 1,
            "page": source["page"],
            "locus": source["locus"],
            "source_kind": source_kind,
            "source_ref": source_ref,
            "anchor_position_id": source["position_id"],
            "consumed_position_ids": ordered_compact(span_positions),
            "source_surfaces": ordered_compact(span_surfaces),
            "rendered_text_de": rendered,
            "historical_confirmation": HISTORICAL,
        })
    return output


def census_rows(
    source_rows: list[dict[str, str]],
    specs: list[dict[str, str]],
    lexical_by_source: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    specs_by_id = {row["source_reading_id"]: row for row in specs}
    output: list[dict[str, Any]] = []
    for source in source_rows:
        if source["disposition"] != "HELD_FOR_LATER_REPAIR":
            continue
        row: dict[str, Any] = rename_v86_fields(source)
        source_id = source["source_reading_id"]
        lexical = lexical_by_source[source_id]
        spec = specs_by_id.get(source_id)
        if spec:
            row.update({
                "disposition": "REVISED_IN_V87" if spec["decision"] == "REVISE" else "AUDITED_HOLD_IN_V87",
                "repair_mode": spec["repair_mode"],
                "resolved_debt_atom": spec["resolved_debt_atom"],
                "v87_reading_id": lexical["v87_reading_id"],
                "v87_lexical_core_de": lexical["v87_lexical_core_de"],
                "v87_context_realization_de": spec["v87_context_realization_de"],
                "new_lexical_score": lexical["working_model_score_0_100_not_probability"],
                "new_lexical_level": lexical["working_model_level"],
                "new_context_score": lexical["context_realization_score_0_100_not_probability"],
                "new_context_level": lexical["context_realization_level"],
                "positive_evidence_de": spec["evidence_de"],
                "counterevidence_de": spec["counterevidence_de"],
                "v87_audit_decision": spec["decision"],
                "v87_evidence_class": spec["evidence_class"],
                "v87_open_semantic_slots": spec["open_semantic_slots"],
            })
        else:
            row.update({
                "v87_reading_id": lexical["v87_reading_id"],
                "v87_lexical_core_de": lexical["v87_lexical_core_de"],
                "v87_context_realization_de": lexical["v87_context_realizations_de"],
                "new_lexical_score": lexical["working_model_score_0_100_not_probability"],
                "new_lexical_level": lexical["working_model_level"],
                "new_context_score": lexical["context_realization_score_0_100_not_probability"],
                "new_context_level": lexical["context_realization_level"],
                "v87_audit_decision": "HELD_FOR_LATER_REPAIR",
                "v87_evidence_class": "INHERITED_V86",
                "v87_open_semantic_slots": "NOT_EVALUATED",
            })
        output.append(row)
    return output


def delta_rows(
    specs: list[dict[str, str]],
    source_lexical: list[dict[str, str]],
    target_lexical_by_source: dict[str, dict[str, Any]],
    source_context: list[dict[str, str]],
) -> list[dict[str, Any]]:
    source_by_id: dict[str, dict[str, str]] = {}
    for row in source_lexical:
        for source_id in split_pipe(row["source_reading_ids"]):
            source_by_id[source_id] = row
    occurrences: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in source_context:
        occurrences[row["source_reading_id"]].append(row)
    output: list[dict[str, Any]] = []
    for spec in specs:
        source = source_by_id[spec["source_reading_id"]]
        target = target_lexical_by_source[spec["source_reading_id"]]
        positions = occurrences[spec["source_reading_id"]]
        output.append({
            "source_reading_id": spec["source_reading_id"],
            "surface": source["surface"],
            "decision": spec["decision"],
            "occurrence_count": len(positions),
            "page_count": len({row["page"] for row in positions}),
            "pages": ordered_compact(sorted({row["page"] for row in positions})),
            "positions": ordered_compact(f"{row['locus']}#{row['token_ordinal']}" for row in positions),
            "old_lexical_core_de": source["v86_lexical_core_de"],
            "v87_lexical_core_de": target["v87_lexical_core_de"],
            "v87_context_realization_de": spec["v87_context_realization_de"],
            "old_score": source["working_model_score_0_100_not_probability"],
            "v87_score": target["working_model_score_0_100_not_probability"],
            "old_level": source["working_model_level"],
            "v87_level": target["working_model_level"],
            "family_ids": spec["family_ids"],
            "decomposition": spec["decomposition"],
            "repair_mode": spec["repair_mode"],
            "resolved_debt_atom": spec["resolved_debt_atom"],
            "evidence_class": spec["evidence_class"],
            "evidence_de": spec["evidence_de"],
            "counterevidence_de": spec["counterevidence_de"],
            "open_semantic_slots": spec["open_semantic_slots"],
            "component_global_export_allowed": spec["component_global_export_allowed"],
            "old_semantic_scope": source["semantic_scope"],
            "v87_semantic_scope": target["semantic_scope"],
            "old_global_export_scope": source["global_export_scope"],
            "v87_global_export_scope": target["global_export_scope"],
            "occurrence_bound_span_override": spec["occurrence_bound_span_override"],
            "historical_confirmation": HISTORICAL,
        })
    return output


def family_rows(
    source_rows: list[dict[str, str]],
    specs: list[dict[str, str]],
    source_context: list[dict[str, str]],
    lexical_by_source: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    wanted = {family for spec in specs for family in split_pipe(spec["family_ids"])}
    specs_by_family: dict[str, list[dict[str, str]]] = defaultdict(list)
    for spec in specs:
        for family in split_pipe(spec["family_ids"]):
            specs_by_family[family].append(spec)
    occurrences: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in source_context:
        occurrences[row["source_reading_id"]].append(row)
    output: list[dict[str, Any]] = []
    for source in source_rows:
        family = source["family_id"]
        if family not in wanted:
            continue
        row: dict[str, Any] = {family_v87_key(key): value for key, value in source.items()}
        selected = specs_by_family[family]
        selected_ids = [spec["source_reading_id"] for spec in selected]
        selected_positions = [position for source_id in selected_ids for position in occurrences[source_id]]
        row.update({
            "selected_source_readings": len(selected_ids),
            "selected_lexical_readings": len({lexical_by_source[source_id]["v87_reading_id"] for source_id in selected_ids}),
            "selected_positions": len(selected_positions),
            "selected_pages": len({position["page"] for position in selected_positions}),
            "selected_source_reading_ids": ordered_compact(selected_ids),
            "selected_surfaces": ordered_compact(sorted({position["surface"] for position in selected_positions})),
            "selected_v87_reading_ids": ordered_compact(sorted({str(lexical_by_source[source_id]["v87_reading_id"]) for source_id in selected_ids})),
            "selected_v87_levels": ordered_compact(sorted({str(lexical_by_source[source_id]["working_model_level"]) for source_id in selected_ids})),
            "automatic_historical_credit": 0,
            "historical_confirmation": HISTORICAL,
            "v87_decisions": ordered_compact(spec["decision"] for spec in selected),
        })
        output.append(row)
    return output


def complete_rows(source_rows: list[dict[str, str]], lexical: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for source in source_rows:
        if source["current_layer"] == "ACTIVE_V86_LEXICAL_CORE":
            continue
        row: dict[str, Any] = rename_v86_fields(source)
        row.update({
            "v87_audit_decision": "OUTSIDE_ACTIVE_V87_TRANCHE",
            "v87_evidence_class": "INHERITED_GLOBAL_V48",
            "v87_open_semantic_slots": "NOT_EVALUATED",
            "v87_component_global_export_allowed": "NOT_EVALUATED",
        })
        output.append(row)
    for row in lexical:
        output.append({
            "surface": row["surface"],
            "reading_id": row["v87_reading_id"],
            "working_meaning_de": row["v87_lexical_core_de"],
            "current_layer": "ACTIVE_V87_LEXICAL_CORE",
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
            "v87_context_realizations_de": row["v87_context_realizations_de"],
            "source_reading_ids": row["source_reading_ids"],
            "v87_audit_decision": row["v87_audit_decision"],
            "v87_evidence_class": row["v87_evidence_class"],
            "v87_open_semantic_slots": row["v87_open_semantic_slots"],
            "v87_component_global_export_allowed": row["v87_component_global_export_allowed"],
        })
    return sorted(output, key=lambda item: (str(item["surface"]), str(item["reading_id"])))


def report_text(result: dict[str, Any]) -> str:
    return f"""# GDT714 — V87 bound-C1 core/context repair

Status: `{STATUS}`

## Ergebnis

V87 bearbeitet die naechsten 18 schwachen C1-Ganzwortlesungen an 18
unveraenderten Positionen auf zwoelf bereits zugelassenen Seiten. Die 18
Kerne werden semantisch kompakter und kompositionell einheitlicher. Unbelegte Identitaeten
wie Droge, Arznei, Dosis und Charge verschwinden; erhalten bleiben die im
Arbeitsmodell sichtbaren Felder Menge, Portion, Zubereitung, trocken,
feucht, heiß, kalt sowie Anfangs-, Mittel- und Endstufe.

Beispiele:

```text
chedaiin   abgemessene Trockenmenge III, Mittelstufe
dshey      abgemessene Feuchtmenge, Mittelstufe
kor        heiße Portion
okees      heiße Zubereitung, Endstufe
orchey     trockene Portion, Mittelstufe
oteor      kalte Portion, Mittelstufe
oty        kalte Zubereitung, Anfangsstufe
```

`dshees` bleibt bewusst W1: `abgemessene Feuchtform, Endstufe` ist eine
brauchbare Default-Komposition, aber die interne Grenze D-SH-EE-S ist nicht
unabhaengig gesichert und gibt deshalb null neue Scorepunkte. `cholkain`,
`kc`, `keo`, `oteor` und `oty` werden sprachlich oder kontextuell repariert,
ohne Confidence-Promotion. `os` erhaelt ausschliesslich den maschinengeprueften
F_O-Bonus von drei Punkten und bleibt W0.

## Konkrete Rendererreparatur

GDT678 hatte den f7r.2-Rand bereits explizit entschieden. V87 macht diese
Entscheidung nun im kanonischen Kontextstrom ausfuehrbar:

```text
P288 keo + P289 r  ->  heiße Portion        (einmal)
```

Der neue Consumer-Trace konsumiert beide Quellpositionen, ersetzt P288 durch
genau diese eine Ausgabe und laesst P289 ohne eigene Ausgabe. Die komplette
f7r.2-Ausgabe besitzt dadurch acht statt neun Einheiten:

```text
{result['f7r2_rendered_line_de']}
```

Damit wird an dieser Stelle weder `heiße Zubereitung auf Mittelstufe` noch
`Wurzel` gedruckt. Der Span ist lokal und nicht exportierbar. Die globalen
Arbeitswerte bleiben erhalten: `keo = heiße Zubereitung, Mittelstufe` fuer seine
anderen GDT678-Kontexte und `r = Wurzel` fuer die 129 GDT661-Kontexte. Es wird
also weder ein freies `keo+r`-Gesetz noch ein neuer historischer Wortwert
erfunden.

## Bestand

- auditierte Lesungen / Positionen / Seiten: {result['audited_readings']} / {result['audited_positions']} / {result['audited_pages']}
- revidiert / bewusst gehalten: {result['revised_readings']} / {result['held_readings']}
- neue lokale Einmal-Spans / beruehrte Positionen: {result['boundary_spans_added']} / {result['boundary_positions_touched']}
- One-shot-Directives / tatsaechliche f7r.2-Ausgabeeinheiten: {result['one_shot_directives']} / {result['f7r2_rendered_units']}
- direkt gebundene Primaerevidenzzeilen: {result['primary_evidence_bindings']}
- aktive Lesungen / Positionen: {result['active_lexical_readings']} / {result['active_positions']}
- aktive Confidence-Stufen: `{json.dumps(result['active_level_counts'], ensure_ascii=False, sort_keys=True)}`
- komplettes Woerterbuch: {result['complete_surfaces']} Oberflaechen / {result['complete_readings']} Lesungen
- noch nicht einzeln bearbeitete schwache Lesungen: {result['remaining_unreviewed_weak_readings']}

## Grenze

Das ist die konkrete Arbeitsuebersetzung des aktuellen Modells, kein
bestaetigter Klartext. Confidence bleibt ein interner Evidenzindex, keine
Wahrscheinlichkeit. Keine neue Komponente wird als freies Voynich-Wort
exportiert; alle historischen Felder bleiben `H0_NONE`. Es wurden keine neue
Seite, kein Bild, keine neue Transkription, kein `f84` und kein `f84r` benutzt.
"""


def main() -> int:
    source_lexical = read_tsv(SOURCE_LEXICAL)
    source_context = read_tsv(SOURCE_CONTEXT)
    source_complete = read_tsv(SOURCE_COMPLETE)
    source_census = read_tsv(SOURCE_CENSUS)
    source_spans = read_tsv(SOURCE_SPANS)
    source_families = read_tsv(SOURCE_FAMILIES)
    specs = read_tsv(SPECS)
    boundary_specs = read_tsv(BOUNDARY_SPECS)
    primary_bindings = read_tsv(PRIMARY_BINDINGS)

    assert (
        len(source_lexical), len(source_context), len(source_complete),
        len(source_census), len(source_spans), len(source_families), len(specs),
        len(boundary_specs), len(primary_bindings),
    ) == (324, 479, 1586, 118, 1, 13, 18, 1, 18)
    assert len({row["source_reading_id"] for row in specs}) == 18
    assert Counter(row["decision"] for row in specs) == Counter({"REVISE": 18})
    assert all(row["component_global_export_allowed"] == "0" for row in specs)
    assert all(row["occurrence_bound_span_override"] == "NONE" for row in specs)
    assert all(row["global_export_allowed"] == "0" for row in boundary_specs)
    assert all(not row["page"].startswith("f84") and not row["locus"].startswith("f84") for row in source_context)
    assert {row["source_reading_id"] for row in primary_bindings} == {
        row["source_reading_id"] for row in specs
    }

    primary_evidence = primary_evidence_rows(primary_bindings, specs)
    score_deltas = derived_score_deltas(primary_bindings, source_families)
    lexical, lexical_by_source = lexical_rows(source_lexical, specs, score_deltas)
    contexts = context_rows(source_context, specs, lexical_by_source)
    contexts = apply_boundary_specs(contexts, boundary_specs)
    one_shot_directives = one_shot_directive_rows(contexts, boundary_specs)
    f7r2_rendered = rendered_locus_rows(contexts, one_shot_directives, "f7r.2")
    census = census_rows(source_census, specs, lexical_by_source)
    delta = delta_rows(specs, source_lexical, lexical_by_source, source_context)
    families = family_rows(source_families, specs, source_context, lexical_by_source)
    complete = complete_rows(source_complete, lexical)
    bound_spans = bound_span_rows(source_spans, boundary_specs)

    target_ids = {row["source_reading_id"] for row in specs}
    selected_positions = [row for row in source_context if row["source_reading_id"] in target_ids]
    active_levels = Counter(str(row["working_model_level"]) for row in lexical)
    complete_levels = Counter(str(row["working_model_level"]) for row in complete)
    assert len(selected_positions) == 18 and len({row["page"] for row in selected_positions}) == 12
    assert len(census) == 109 and len(families) == 7
    assert len(bound_spans) == 2
    assert len(primary_evidence) == 18 and len(one_shot_directives) == 2
    assert len(f7r2_rendered) == 8
    assert len(complete) == 1586 and len({row["surface"] for row in complete}) == 1582
    assert active_levels == Counter({
        "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY": 7, "W1_WEAK_WORKING": 135,
        "W2_PROVISIONAL_WORKING": 163, "W3_SOLID_WORKING_THEORY": 19,
    })
    assert complete_levels == Counter({
        "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY": 287, "W1_WEAK_WORKING": 315,
        "W2_PROVISIONAL_WORKING": 541, "W3_SOLID_WORKING_THEORY": 443,
    })

    lexical_fields = unique_fields([v87_key(field) for field in source_lexical[0]] + [
        "v87_audit_decision", "v87_evidence_class", "v87_open_semantic_slots",
        "v87_component_global_export_allowed", "v87_prior_lexical_core_de",
    ])
    context_fields = unique_fields([v87_key(field) for field in source_context[0]] + [
        "v87_audit_decision", "v87_evidence_class", "v87_open_semantic_slots",
        "v87_component_global_export_allowed", "v87_boundary_decision",
        "v87_boundary_render_once_de",
    ])
    census_fields = unique_fields([v87_key(field) for field in source_census[0]] + [
        "v87_audit_decision", "v87_evidence_class", "v87_open_semantic_slots",
    ])
    family_fields = [family_v87_key(field) for field in source_families[0]] + ["v87_decisions"]
    complete_fields = unique_fields([v87_key(field) for field in source_complete[0]] + [
        "v87_audit_decision", "v87_evidence_class", "v87_open_semantic_slots",
        "v87_component_global_export_allowed",
    ])
    write_tsv(ART / "V87_324_ACTIVE_LEXICAL_READINGS.tsv", lexical_fields, lexical)
    write_tsv(ART / "V87_479_CONTEXT_REALIZATIONS.tsv", context_fields, contexts)
    write_tsv(ART / "V87_109_HELD_READING_AUDIT.tsv", census_fields, census)
    write_tsv(ART / "V87_18_BOUND_C1_CORE_CONTEXT_DELTA.tsv", list(delta[0]), delta)
    write_tsv(ART / "V87_7_FAMILY_EVIDENCE.tsv", family_fields, families)
    write_tsv(ART / "V87_2_BOUND_SPAN_RENDERER.tsv", list(bound_spans[0]), bound_spans)
    write_tsv(ART / "V87_1_BOUNDARY_DELTA.tsv", list(boundary_specs[0]), boundary_specs)
    write_tsv(ART / "V87_18_PRIMARY_EVIDENCE_BINDINGS.tsv", list(primary_evidence[0]), primary_evidence)
    write_tsv(ART / "V87_2_ONE_SHOT_RENDER_DIRECTIVES.tsv", list(one_shot_directives[0]), one_shot_directives)
    write_tsv(ART / "V87_8_F7R2_RENDERED_UNITS.tsv", list(f7r2_rendered[0]), f7r2_rendered)
    write_tsv(ART / "V87_COMPLETE_WORD_CONFIDENCE.tsv", complete_fields, complete)

    result = {
        "experiment_id": "GDT714", "status": STATUS,
        "claim_ceiling": "EXPLORATORY_WORKING_DICTIONARY_ONLY_NOT_PLAINTEXT",
        "audited_readings": len(specs), "audited_positions": len(selected_positions),
        "audited_pages": len({row["page"] for row in selected_positions}),
        "revised_readings": sum(row["decision"] == "REVISE" for row in specs),
        "held_readings": sum(row["decision"] == "HOLD" for row in specs),
        "revised_positions": sum(sum(position["source_reading_id"] == row["source_reading_id"] for position in selected_positions) for row in specs if row["decision"] == "REVISE"),
        "held_positions": sum(sum(position["source_reading_id"] == row["source_reading_id"] for position in selected_positions) for row in specs if row["decision"] == "HOLD"),
        "boundary_spans_added": len(boundary_specs),
        "boundary_positions_touched": 2 * len(boundary_specs),
        "additional_non_target_boundary_positions": 1,
        "primary_evidence_bindings": len(primary_evidence),
        "one_shot_directives": len(one_shot_directives),
        "f7r2_rendered_units": len(f7r2_rendered),
        "f7r2_rendered_line_de": " · ".join(str(row["rendered_text_de"]) for row in f7r2_rendered),
        "active_lexical_readings": len(lexical), "active_positions": len(contexts),
        "active_level_counts": dict(sorted(active_levels.items())),
        "active_applicability_counts": dict(sorted(Counter(str(row["semantic_applicability"]) for row in lexical).items())),
        "active_export_scope_counts": dict(sorted(Counter(str(row["global_export_scope"]) for row in lexical).items())),
        "active_weak_readings": active_levels["W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY"] + active_levels["W1_WEAK_WORKING"],
        "remaining_unreviewed_weak_readings": sum(row["v87_audit_decision"] == "HELD_FOR_LATER_REPAIR" for row in census),
        "complete_readings": len(complete), "complete_surfaces": len({row["surface"] for row in complete}),
        "complete_level_counts": dict(sorted(complete_levels.items())),
        "family_evidence_rows": len(families), "bound_span_renderers": len(bound_spans),
        "historical_confirmation_counts": dict(sorted(Counter(str(row["historical_confirmation"]) for row in complete).items())),
        "relation_word_credit_gdt714": 0, "new_pages": 0, "new_images": 0,
        "new_transcription": 0, "f84_or_f84r_used": 0,
    }
    (ART / "RESULT.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (EXP / "REPORT.md").write_text(report_text(result), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
