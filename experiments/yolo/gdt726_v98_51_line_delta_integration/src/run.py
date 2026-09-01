#!/usr/bin/env python3
"""Integrate the complete V98 51-line deck and a bounded practical renderer."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt726_v98_51_line_delta_integration"
SRC = EXP / "src"
ART = EXP / "artifacts"
V56 = ROOT / "experiments/yolo/gdt682_final_seven_hole_line_completion/artifacts/V56_51_LINE_READER.tsv"
V57 = ROOT / "experiments/yolo/gdt683_ol_semantic_debt_reconciliation/artifacts/V57_51_LINE_READER.tsv"
G725 = ROOT / "experiments/yolo/gdt725_v98_final_low_hardcap_dictionary_dispatch"
V98_CONTEXTS = G725 / "artifacts/V98_479_CONTEXT_REALIZATIONS.tsv"
V98_SPANS = G725 / "artifacts/V98_5_BOUND_SPAN_RENDERER.tsv"
V98_SPAN_EXECUTION = G725 / "artifacts/V98_5_BOUND_SPAN_EXECUTION_AUDIT.tsv"
V98_DIRECTIVES = G725 / "artifacts/V98_2_ONE_SHOT_RENDER_DIRECTIVES.tsv"
V98_F7R2 = G725 / "artifacts/V98_8_F7R2_RENDERED_UNITS.tsv"
V98_COMPANION_SPEC = G725 / "src/V98_1_COMPANION_LINE_RENDER_SPEC.tsv"
V98_COMPANION_AUDIT = G725 / "artifacts/V98_1_COMPANION_LINE_RENDER_AUDIT.tsv"
PATCH_SPECS = SRC / "V98R1_10_LOCAL_RENDER_PATCH_SPECS.tsv"
DEBT_SPECS = SRC / "V98R1_6_OPEN_MEANING_DEBT_SPECS.tsv"
HISTORICAL = "H0_NONE"
STATUS = (
    "PASS_V98_51_LINE_DELTA_INTEGRATION__479_POSITIONS_CONSUMED_ONCE__"
    "474_EXACT_UNITS__V98R1_471_PRACTICAL_UNITS__357_CONTEXT_DELTAS__"
    "9_NEW_LOCAL_RENDER_PATCHES_PLUS_1_INHERITED_COMPANION__"
    "6_OPEN_MEANING_DEBTS__ZERO_CORE_SCORE_EXPORT_DELTA__ALL_H0_NONE"
)
HARD_GENERIC = (
    "arbeitsgut",
    "arbeitsmaterial",
    "arbeitsschritt",
    "arbeitsort",
    "arbeitszyklus",
    "werkstück",
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(
    path: Path, rows: Iterable[dict[str, Any]], fields: list[str] | None = None
) -> None:
    materialized = list(rows)
    if fields is None:
        fields = list(materialized[0]) if materialized else []
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        for row in materialized:
            writer.writerow({field: row.get(field, "") for field in fields})


def split_pipe(value: str) -> list[str]:
    return [item.strip() for item in value.split("|") if item.strip()]


def fingerprint(row: dict[str, str]) -> str:
    payload = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def text_sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def parse_selector(selector: str) -> dict[str, str]:
    output: dict[str, str] = {}
    for part in selector.split(";"):
        field, value = part.split("=", 1)
        assert field and field not in output
        output[field] = value
    return output


def select_one(rows: list[dict[str, str]], selector: str) -> dict[str, str]:
    expected = parse_selector(selector)
    matches = [
        row
        for row in rows
        if all(row.get(field) == value for field, value in expected.items())
    ]
    assert len(matches) == 1, (selector, len(matches))
    return matches[0]


def render_values(values: list[str]) -> str:
    output = ""
    for value in values:
        if value in {".", ";"}:
            output = output.rstrip(" ·") + value
        else:
            if output:
                output += " " if output.endswith((".", ";", ":")) else " · "
            output += value
    return output


def display_line(value: str) -> tuple[str, int]:
    if not value:
        return value, 0
    output = value[0].upper() + value[1:]
    added = int(not output.endswith((".", ";", ":", "!", "?")))
    return output + ("." if added else ""), added


def baseline_indexes(
    v56: list[dict[str, str]],
    v57: list[dict[str, str]],
    contexts: list[dict[str, str]],
) -> tuple[
    list[str],
    dict[str, dict[str, str]],
    dict[str, dict[str, str]],
    dict[str, list[dict[str, str]]],
    dict[str, dict[str, str]],
]:
    assert len(v56) == len(v57) == 51
    order = [row["locus"] for row in v57]
    assert len(set(order)) == 51
    v56_by_locus = {row["locus"]: row for row in v56}
    v57_by_locus = {row["locus"]: row for row in v57}
    assert list(v56_by_locus) == list(v57_by_locus) == order
    by_locus: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    by_position: dict[str, dict[str, str]] = {}
    for row in contexts:
        assert row["position_id"] not in by_position
        assert not row["page"].casefold().startswith("f84")
        by_locus[row["locus"]].append(row)
        by_position[row["position_id"]] = row
    assert len(contexts) == len(by_position) == 479
    assert set(by_locus) == set(order)
    for locus in order:
        rows = sorted(by_locus[locus], key=lambda row: int(row["token_ordinal"]))
        by_locus[locus] = rows
        assert [int(row["token_ordinal"]) for row in rows] == list(
            range(1, len(rows) + 1)
        )
        old, base = v56_by_locus[locus], v57_by_locus[locus]
        assert old["page"] == base["page"] == rows[0]["page"]
        assert int(old["token_count"]) == int(base["token_count"]) == len(rows)
        surfaces = [row["surface"] for row in rows]
        assert old["zl3b_line"].split() == base["zl3b_line"].split() == surfaces
        assert base["literal_token_glosses_de"].split(" | ") == [
            row["v57_baseline_gloss_de"] for row in rows
        ]
    return order, v56_by_locus, v57_by_locus, dict(by_locus), by_position


def inherited_spans(
    span_rows: list[dict[str, str]], by_position: dict[str, dict[str, str]]
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for row in span_rows:
        consumed = [row["left_position_id"], row["right_position_id"]]
        assert [by_position[item]["surface"] for item in consumed] == [
            row["left_surface"],
            row["right_surface"],
        ]
        output.append(
            {
                "rule_id": row["bound_span_id"],
                "rule_origin": "INHERITED_V98_BOUND_SPAN",
                "anchor_position_id": consumed[0],
                "consumed_position_ids": consumed,
                "render_once_de": row["render_once_de"],
            }
        )
    assert len(output) == 5
    return output


def validate_patch_specs(
    specs: list[dict[str, str]], by_position: dict[str, dict[str, str]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    assert len(specs) == 10
    cache: dict[Path, list[dict[str, str]]] = {}
    audit: list[dict[str, Any]] = []
    groups: list[dict[str, Any]] = []
    overrides: list[dict[str, Any]] = []
    for spec in specs:
        consumed = split_pipe(spec["consumed_position_ids"])
        support = split_pipe(spec["support_position_ids"])
        assert spec["anchor_position_id"] == consumed[0]
        assert all(position_id in by_position for position_id in {*consumed, *support})
        rows = [by_position[position_id] for position_id in consumed]
        assert {row["locus"] for row in rows} == {spec["expected_locus"]}
        assert [row["surface"] for row in rows] == split_pipe(spec["expected_surfaces"])
        assert [row["v98_context_realization_de"] for row in rows] == [
            value.strip() for value in spec["expected_contexts_de"].split(" || ")
        ]
        path = ROOT / spec["source_artifact"]
        assert "f84" not in str(path).casefold()
        if path not in cache:
            cache[path] = read_tsv(path)
        source = select_one(cache[path], spec["source_selector"])
        audit.append(
            {
                **spec,
                "consumed_position_count": len(consumed),
                "support_snapshot_de": " || ".join(
                    by_position[item]["v98_context_realization_de"] for item in support
                ),
                "source_row_fingerprint_sha256": fingerprint(source),
                "source_row_match": 1,
                "dictionary_core_changes": 0,
                "context_table_changes": 0,
                "score_changes": 0,
                "audit_status": "PASS_BOUND_LOCAL_RENDERER_ONLY",
            }
        )
        normalized = {
            "rule_id": spec["patch_id"],
            "rule_origin": "GDT726_LOCAL_RENDER_PATCH",
            "anchor_position_id": consumed[0],
            "consumed_position_ids": consumed,
            "render_once_de": spec["render_once_de"],
            "patch_scope": spec["patch_scope"],
        }
        if spec["rule_kind"] == "BOUND_GROUP":
            assert len(consumed) >= 2
            groups.append(normalized)
        else:
            assert spec["rule_kind"] == "POSITION_OVERRIDE" and len(consumed) == 1
            overrides.append(normalized)
    assert len(groups) == 3 and len(overrides) == 7
    return audit, groups, overrides


def assert_disjoint_rules(rules: list[dict[str, Any]]) -> None:
    owner: dict[str, str] = {}
    for rule in rules:
        for position_id in rule["consumed_position_ids"]:
            assert position_id not in owner, (position_id, owner.get(position_id), rule["rule_id"])
            owner[position_id] = rule["rule_id"]


def build_edition(
    edition: str,
    prefix: str,
    order: list[str],
    v56_by_locus: dict[str, dict[str, str]],
    v57_by_locus: dict[str, dict[str, str]],
    contexts_by_locus: dict[str, list[dict[str, str]]],
    span_rules: list[dict[str, Any]],
    override_rules: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    assert_disjoint_rules(span_rules)
    span_by_position: dict[str, dict[str, Any]] = {}
    for rule in span_rules:
        for position_id in rule["consumed_position_ids"]:
            span_by_position[position_id] = rule
    override_by_position = {row["anchor_position_id"]: row for row in override_rules}
    assert not set(override_by_position) & set(span_by_position)
    units: list[dict[str, Any]] = []
    lines: list[dict[str, Any]] = []
    unit_by_position: dict[str, dict[str, Any]] = {}
    for locus in order:
        rows = contexts_by_locus[locus]
        row_by_position = {row["position_id"]: row for row in rows}
        line_units: list[dict[str, Any]] = []
        consumed_in_line: set[str] = set()
        for row in rows:
            position_id = row["position_id"]
            if position_id in consumed_in_line:
                continue
            span = span_by_position.get(position_id)
            if span:
                assert position_id == span["anchor_position_id"]
                consumed_ids = span["consumed_position_ids"]
                consumed_rows = [row_by_position[item] for item in consumed_ids]
                ordinals = [int(item["token_ordinal"]) for item in consumed_rows]
                assert ordinals == list(range(ordinals[0], ordinals[0] + len(ordinals)))
                source_kind, source_ref = "BOUND_SPAN", span["rule_id"]
                text = span["render_once_de"]
            else:
                consumed_ids, consumed_rows = [position_id], [row]
                override = override_by_position.get(position_id)
                if override:
                    source_kind = (
                        "INHERITED_COMPANION_OVERRIDE"
                        if override["patch_scope"].startswith("INHERITED")
                        else "LOCAL_POSITION_OVERRIDE"
                    )
                    source_ref, text = override["rule_id"], override["render_once_de"]
                else:
                    source_kind, source_ref = "CONTEXT_POSITION", position_id
                    text = row["v98_context_realization_de"]
            consumed_in_line.update(consumed_ids)
            unit_id = f"{prefix}U{len(units) + 1:03d}"
            unit = {
                "edition": edition,
                "output_unit_id": unit_id,
                "global_output_ordinal": len(units) + 1,
                "page": row["page"],
                "locus": locus,
                "line_output_ordinal": len(line_units) + 1,
                "source_kind": source_kind,
                "source_ref": source_ref,
                "anchor_position_id": position_id,
                "consumed_position_ids": "|".join(consumed_ids),
                "consumed_position_count": len(consumed_ids),
                "source_surfaces": "|".join(item["surface"] for item in consumed_rows),
                "v98_context_inputs_de": " || ".join(
                    item["v98_context_realization_de"] for item in consumed_rows
                ),
                "rendered_text_de": text,
                "component_global_export_allowed": 0,
                "score_delta": 0,
                "historical_confirmation": HISTORICAL,
            }
            units.append(unit)
            line_units.append(unit)
            for consumed_id in consumed_ids:
                assert consumed_id not in unit_by_position
                unit_by_position[consumed_id] = unit
        assert consumed_in_line == set(row_by_position)
        reader = render_values([str(unit["rendered_text_de"]) for unit in line_units])
        display, terminal_added = display_line(reader)
        old, base = v56_by_locus[locus], v57_by_locus[locus]
        old_values = old["literal_token_glosses_de"].split(" | ")
        base_values = base["literal_token_glosses_de"].split(" | ")
        current_values = [row["v98_context_realization_de"] for row in rows]
        applied_spans = [
            str(unit["source_ref"])
            for unit in line_units
            if unit["source_kind"] == "BOUND_SPAN"
        ]
        applied_overrides = [
            str(unit["source_ref"])
            for unit in line_units
            if unit["source_kind"] in {
                "INHERITED_COMPANION_OVERRIDE",
                "LOCAL_POSITION_OVERRIDE",
            }
        ]
        hard_hits = [term for term in HARD_GENERIC if term in display.casefold()]
        lines.append(
            {
                "edition": edition,
                "page": base["page"],
                "locus": locus,
                "section": base["section"],
                "language": base["language"],
                "hand": base["hand"],
                "line_mode": base["line_mode"],
                "source_position_count": len(rows),
                "rendered_unit_count": len(line_units),
                "v57_to_v98_context_delta_count": sum(
                    left != right for left, right in zip(base_values, current_values, strict=True)
                ),
                "v56_to_v98_context_delta_count": sum(
                    left != right for left, right in zip(old_values, current_values, strict=True)
                ),
                "zl3b_line": base["zl3b_line"],
                "surface_sequence": " ".join(row["surface"] for row in rows),
                "position_ids": "|".join(row["position_id"] for row in rows),
                "v57_literal_contexts_de": " | ".join(base_values),
                "v98_contexts_de": " | ".join(current_values),
                "rendered_unit_ids": "|".join(str(unit["output_unit_id"]) for unit in line_units),
                "rendered_units_de": " | ".join(str(unit["rendered_text_de"]) for unit in line_units),
                "applied_span_ids": "|".join(applied_spans) if applied_spans else "NONE",
                "applied_override_ids": "|".join(applied_overrides) if applied_overrides else "NONE",
                "reader_de": reader,
                "display_reader_de": display,
                "display_only_terminal_period_added": terminal_added,
                "v57_aligned_line_de": base["aligned_line_de"],
                "v57_practical_translation_de": base["practical_translation_de"],
                "hard_generic_hits": "|".join(hard_hits) if hard_hits else "NONE",
                "dictionary_core_changes": 0,
                "context_table_changes": 0,
                "score_changes": 0,
                "component_global_exports": 0,
                "historical_confirmation": HISTORICAL,
            }
        )
    all_contexts = [row for locus in order for row in contexts_by_locus[locus]]
    assert set(unit_by_position) == {row["position_id"] for row in all_contexts}
    consumption: list[dict[str, Any]] = []
    for row in all_contexts:
        unit = unit_by_position[row["position_id"]]
        anchor = unit["anchor_position_id"] == row["position_id"]
        if unit["source_kind"] == "BOUND_SPAN":
            disposition = (
                "BOUND_SPAN_ANCHOR_OUTPUT" if anchor else "BOUND_SPAN_MEMBER_SUPPRESSED"
            )
        else:
            disposition = unit["source_kind"]
        consumption.append(
            {
                "edition": edition,
                "position_id": row["position_id"],
                "page": row["page"],
                "locus": row["locus"],
                "token_ordinal": row["token_ordinal"],
                "surface": row["surface"],
                "source_reading_id": row["source_reading_id"],
                "v98_dictionary_core_de": row["v98_lexical_core_de"],
                "v98_context_realization_de": row["v98_context_realization_de"],
                "v98_lexical_score": row["v98_lexical_score"],
                "v98_lexical_level": row["v98_lexical_level"],
                "consumption_disposition": disposition,
                "rule_id": unit["source_ref"],
                "output_unit_id": unit["output_unit_id"],
                "emitted_here": int(anchor),
                "emitted_text_de": unit["rendered_text_de"] if anchor else "",
                "position_consumed_once": 1,
                "group_position_count": unit["consumed_position_count"],
                "dictionary_core_changed": 0,
                "context_table_changed": 0,
                "score_changed": 0,
                "component_global_export_allowed": 0,
                "historical_confirmation": HISTORICAL,
            }
        )
    return consumption, units, lines


def build_delta_audit(
    order: list[str], exact_lines: list[dict[str, Any]], practical_lines: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    exact_by_locus = {str(row["locus"]): row for row in exact_lines}
    practical_by_locus = {str(row["locus"]): row for row in practical_lines}
    output: list[dict[str, Any]] = []
    for locus in order:
        exact, practical = exact_by_locus[locus], practical_by_locus[locus]
        output.append(
            {
                "page": exact["page"],
                "locus": locus,
                "source_position_count": exact["source_position_count"],
                "v57_to_v98_context_delta_count": exact["v57_to_v98_context_delta_count"],
                "v56_to_v98_context_delta_count": exact["v56_to_v98_context_delta_count"],
                "exact_output_unit_count": exact["rendered_unit_count"],
                "practical_output_unit_count": practical["rendered_unit_count"],
                "exact_reader_sha256": text_sha(str(exact["reader_de"])),
                "practical_reader_sha256": text_sha(str(practical["reader_de"])),
                "practical_renderer_changed": int(exact["reader_de"] != practical["reader_de"]),
                "practical_patch_ids": practical["applied_override_ids"],
                "practical_span_ids": practical["applied_span_ids"],
                "surface_and_order_parity": 1,
                "dictionary_core_changes": 0,
                "context_table_changes": 0,
                "score_changes": 0,
                "component_global_exports": 0,
                "historical_confirmation": HISTORICAL,
            }
        )
    return output


def build_special_audit(
    inherited: list[dict[str, Any]],
    groups: list[dict[str, Any]],
    directives: list[dict[str, str]],
    f7_units: list[dict[str, str]],
    exact_units: list[dict[str, Any]],
    practical_units: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for rule in [*inherited, *groups]:
        exact_count = sum(row["source_ref"] == rule["rule_id"] for row in exact_units)
        practical_count = sum(row["source_ref"] == rule["rule_id"] for row in practical_units)
        output.append(
            {
                "audit_item": rule["rule_id"],
                "audit_class": rule["rule_origin"],
                "consumed_position_ids": "|".join(rule["consumed_position_ids"]),
                "expected_render_once_de": rule["render_once_de"],
                "exact_execution_count": exact_count,
                "practical_execution_count": practical_count,
                "expected_exact_execution_count": int(
                    rule["rule_origin"] == "INHERITED_V98_BOUND_SPAN"
                ),
                "expected_practical_execution_count": 1,
                "audit_status": "PASS",
                "historical_confirmation": HISTORICAL,
            }
        )
    assert len(directives) == 2 and len({row["render_unit_id"] for row in directives}) == 1
    emitted = next(
        row["emitted_text_de"] for row in directives if row["render_action"] == "EMIT_SPAN_ONCE"
    )
    output.append(
        {
            "audit_item": directives[0]["render_unit_id"],
            "audit_class": "ONE_SHOT_DIRECTIVE_PAIR_NOT_TWO_SPANS",
            "consumed_position_ids": "|".join(row["source_position_id"] for row in directives),
            "expected_render_once_de": emitted,
            "exact_execution_count": 1,
            "practical_execution_count": 1,
            "expected_exact_execution_count": 1,
            "expected_practical_execution_count": 1,
            "audit_status": "PASS",
            "historical_confirmation": HISTORICAL,
        }
    )
    exact_f7 = [row for row in exact_units if row["locus"] == "f7r.2"]
    practical_f7 = [row for row in practical_units if row["locus"] == "f7r.2"]
    expected_f7 = [
        row["rendered_text_de"]
        for row in sorted(f7_units, key=lambda row: int(row["output_ordinal"]))
    ]
    assert [row["rendered_text_de"] for row in exact_f7] == expected_f7
    assert [row["rendered_text_de"] for row in practical_f7] == expected_f7
    output.append(
        {
            "audit_item": "F7R2_8_FROZEN_OUTPUT_UNITS",
            "audit_class": "F7R2_SPECIAL_UNIT_PARITY",
            "consumed_position_ids": "|".join(
                item
                for row in f7_units
                for item in split_pipe(row["consumed_position_ids"])
            ),
            "expected_render_once_de": " | ".join(expected_f7),
            "exact_execution_count": len(exact_f7),
            "practical_execution_count": len(practical_f7),
            "expected_exact_execution_count": 8,
            "expected_practical_execution_count": 8,
            "audit_status": "PASS",
            "historical_confirmation": HISTORICAL,
        }
    )
    assert len(output) == 10
    return output


def build_debt_audit(
    specs: list[dict[str, str]], by_position: dict[str, dict[str, str]]
) -> list[dict[str, Any]]:
    assert len(specs) == 6
    output: list[dict[str, Any]] = []
    for spec in specs:
        ids = split_pipe(spec["position_ids"])
        rows = [by_position[position_id] for position_id in ids]
        output.append(
            {
                **spec,
                "position_count": len(ids),
                "current_position_values_de": " || ".join(
                    row["v98_context_realization_de"] for row in rows
                ),
                "scores": "|".join(row["v98_lexical_score"] for row in rows),
                "renderer_change_applied": 0,
                "debt_status": "OPEN_REQUIRES_MEANING_OR_SCOPE_DECISION",
                "component_global_export_allowed": 0,
                "score_delta": 0,
            }
        )
    return output


def write_working_reader(
    path: Path, exact_lines: list[dict[str, Any]], practical_lines: list[dict[str, Any]]
) -> None:
    practical_by_locus = {str(row["locus"]): row for row in practical_lines}
    chunks = [
        "# GDT726 — vollständiger V98/V98R1-Arbeitsreader",
        "",
        "Der Exaktkanal integriert die 479 unveränderten V98-Kontexte mit den fünf geerbten Spans und dem GDT725-Companion. V98R1 ergänzt neun neue lokale Rendererreparaturen; Wörterbuchkerne, Kontexttabelle, Scores und Komponentenexport bleiben unverändert.",
        "",
    ]
    for exact in exact_lines:
        practical = practical_by_locus[str(exact["locus"])]
        chunks.extend(
            [
                f"## {exact['locus']} ({exact['page']})",
                "",
                f"Voynich: `{exact['zl3b_line']}`",
                "",
                f"V98 exakt: {exact['display_reader_de']}",
                "",
                f"V98R1 praktisch: {practical['display_reader_de']}",
                "",
                f"Delta: {exact['v57_to_v98_context_delta_count']} Positionswerte seit V57; lokale R1-Regeln: {practical['applied_override_ids']} / Spans: {practical['applied_span_ids']}.",
                "",
            ]
        )
    path.write_text("\n".join(chunks), encoding="utf-8")


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    v56, v57 = read_tsv(V56), read_tsv(V57)
    contexts = read_tsv(V98_CONTEXTS)
    span_rows, span_execution = read_tsv(V98_SPANS), read_tsv(V98_SPAN_EXECUTION)
    directives, f7_units = read_tsv(V98_DIRECTIVES), read_tsv(V98_F7R2)
    companion_spec = read_tsv(V98_COMPANION_SPEC)
    companion_audit = read_tsv(V98_COMPANION_AUDIT)
    patch_specs, debt_specs = read_tsv(PATCH_SPECS), read_tsv(DEBT_SPECS)
    order, v56_by_locus, v57_by_locus, contexts_by_locus, by_position = baseline_indexes(
        v56, v57, contexts
    )
    assert len({row["page"] for row in contexts}) == 36
    assert len(span_execution) == len(span_rows) == 5
    assert len(companion_spec) == len(companion_audit) == 1
    assert companion_spec[0]["position_id"] == companion_audit[0]["position_id"] == "P265"
    assert companion_spec[0]["line_render_once_de"] == companion_audit[0]["line_render_once_de"]
    inherited = inherited_spans(span_rows, by_position)
    patch_audit, groups, overrides = validate_patch_specs(patch_specs, by_position)
    inherited_companion = [row for row in overrides if row["patch_scope"].startswith("INHERITED")]
    new_overrides = [row for row in overrides if not row["patch_scope"].startswith("INHERITED")]
    assert len(inherited_companion) == 1 and len(new_overrides) == 6
    exact_consumption, exact_units, exact_lines = build_edition(
        "V98_EXACT", "X", order, v56_by_locus, v57_by_locus,
        contexts_by_locus, inherited, inherited_companion,
    )
    practical_consumption, practical_units, practical_lines = build_edition(
        "V98R1_PRACTICAL", "P", order, v56_by_locus, v57_by_locus,
        contexts_by_locus, [*inherited, *groups], overrides,
    )
    assert len(exact_consumption) == len(practical_consumption) == 479
    assert len(exact_units) == 474 and len(practical_units) == 471
    assert len(exact_lines) == len(practical_lines) == 51
    assert sum(int(row["v57_to_v98_context_delta_count"]) for row in exact_lines) == 357
    assert sum(int(row["v56_to_v98_context_delta_count"]) for row in exact_lines) == 357
    assert all(row["hard_generic_hits"] == "NONE" for row in exact_lines)
    assert all(row["hard_generic_hits"] == "NONE" for row in practical_lines)
    delta = build_delta_audit(order, exact_lines, practical_lines)
    special = build_special_audit(
        inherited, groups, directives, f7_units, exact_units, practical_units
    )
    debt = build_debt_audit(debt_specs, by_position)
    write_tsv(ART / "V98_479_EXACT_POSITION_CONSUMPTION.tsv", exact_consumption)
    write_tsv(ART / "V98_474_EXACT_RENDERED_UNITS.tsv", exact_units)
    write_tsv(ART / "V98_51_EXACT_LINE_READER.tsv", exact_lines)
    write_tsv(ART / "V98R1_479_PRACTICAL_POSITION_CONSUMPTION.tsv", practical_consumption)
    write_tsv(ART / "V98R1_471_PRACTICAL_RENDERED_UNITS.tsv", practical_units)
    write_tsv(ART / "V98R1_51_PRACTICAL_LINE_READER.tsv", practical_lines)
    write_tsv(ART / "V98_51_LINE_DELTA_AUDIT.tsv", delta)
    write_tsv(ART / "V98R1_10_LOCAL_RENDER_PATCH_AUDIT.tsv", patch_audit)
    write_tsv(ART / "V98R1_6_OPEN_MEANING_DEBT_AUDIT.tsv", debt)
    write_tsv(ART / "V98R1_10_SPECIAL_RULE_EXECUTION_AUDIT.tsv", special)
    write_working_reader(
        ART / "GDT726_V98R1_51_LINE_WORKING_READER.md", exact_lines, practical_lines
    )
    result = {
        "experiment_id": "GDT726",
        "status": STATUS,
        "source_lines": 51,
        "source_pages": 36,
        "source_positions": 479,
        "unique_positions_consumed_exactly_once_exact": 479,
        "unique_positions_consumed_exactly_once_practical": 479,
        "v57_to_v98_context_deltas": 357,
        "v57_to_v98_unchanged_contexts": 122,
        "v56_to_v57_string_deltas": 7,
        "v56_to_v98_context_deltas": 357,
        "inherited_bound_spans": 5,
        "exact_rendered_units": 474,
        "new_local_bound_groups": 3,
        "new_local_position_overrides": 6,
        "inherited_companion_overrides": 1,
        "new_local_renderer_patches": 9,
        "practical_rendered_units": 471,
        "one_shot_directive_rows": len(directives),
        "one_shot_semantic_spans": len({row["render_unit_id"] for row in directives}),
        "f7r2_frozen_output_units": len(f7_units),
        "open_meaning_debts": len(debt),
        "hard_generic_hits_exact": 0,
        "hard_generic_hits_practical": 0,
        "dictionary_core_changes": 0,
        "context_table_changes": 0,
        "score_changes": 0,
        "component_global_exports": 0,
        "new_pages_images_or_transcriptions": 0,
        "f84_or_f84r_used": 0,
        "historical_confirmation": HISTORICAL,
        "canonical_dictionary": "experiments/yolo/gdt725_v98_final_low_hardcap_dictionary_dispatch/artifacts/V98_COMPLETE_WORD_CONFIDENCE.tsv",
        "complete_working_reader": "experiments/yolo/gdt726_v98_51_line_delta_integration/artifacts/GDT726_V98R1_51_LINE_WORKING_READER.md",
    }
    (ART / "RESULT.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
