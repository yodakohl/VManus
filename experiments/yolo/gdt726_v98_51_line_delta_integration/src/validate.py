#!/usr/bin/env python3
"""Independent validator for GDT726.

This script deliberately does not import run.py. It rebuilds both editions from
the upstream tables and the small local rule specifications, then compares every
generated row with the committed artifacts.
"""

from __future__ import annotations

import csv
import hashlib
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
EXP = ROOT / "experiments/yolo/gdt726_v98_51_line_delta_integration"
SRC = EXP / "src"
ART = EXP / "artifacts"
V56_PATH = ROOT / "experiments/yolo/gdt682_final_seven_hole_line_completion/artifacts/V56_51_LINE_READER.tsv"
V57_PATH = ROOT / "experiments/yolo/gdt683_ol_semantic_debt_reconciliation/artifacts/V57_51_LINE_READER.tsv"
G725 = ROOT / "experiments/yolo/gdt725_v98_final_low_hardcap_dictionary_dispatch"
CONTEXT_PATH = G725 / "artifacts/V98_479_CONTEXT_REALIZATIONS.tsv"
SPAN_PATH = G725 / "artifacts/V98_5_BOUND_SPAN_RENDERER.tsv"
SPAN_EXEC_PATH = G725 / "artifacts/V98_5_BOUND_SPAN_EXECUTION_AUDIT.tsv"
DIRECTIVE_PATH = G725 / "artifacts/V98_2_ONE_SHOT_RENDER_DIRECTIVES.tsv"
F7_PATH = G725 / "artifacts/V98_8_F7R2_RENDERED_UNITS.tsv"
COMPANION_SPEC_PATH = G725 / "src/V98_1_COMPANION_LINE_RENDER_SPEC.tsv"
COMPANION_AUDIT_PATH = G725 / "artifacts/V98_1_COMPANION_LINE_RENDER_AUDIT.tsv"
PATCH_PATH = SRC / "V98R1_10_LOCAL_RENDER_PATCH_SPECS.tsv"
DEBT_PATH = SRC / "V98R1_6_OPEN_MEANING_DEBT_SPECS.tsv"
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


def split_pipe(value: str) -> list[str]:
    return [piece.strip() for piece in value.split("|") if piece.strip()]


def as_strings(row: dict[str, Any]) -> dict[str, str]:
    return {key: str(value) for key, value in row.items()}


def rows_as_strings(rows: Iterable[dict[str, Any]]) -> list[dict[str, str]]:
    return [as_strings(row) for row in rows]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def compare_rows(label: str, actual: list[dict[str, str]], expected: list[dict[str, Any]]) -> None:
    normalized = rows_as_strings(expected)
    require(len(actual) == len(normalized), f"{label}: row count {len(actual)} != {len(normalized)}")
    for ordinal, (left, right) in enumerate(zip(actual, normalized, strict=True), 1):
        require(list(left) == list(right), f"{label} row {ordinal}: field order/schema mismatch")
        if left != right:
            differing = [field for field in left if left[field] != right[field]]
            preview = ", ".join(f"{field}={left[field]!r}!={right[field]!r}" for field in differing[:4])
            raise AssertionError(f"{label} row {ordinal}: {preview}")


def fingerprint(row: dict[str, str]) -> str:
    payload = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def text_sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def parse_selector(selector: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for clause in selector.split(";"):
        require("=" in clause, f"invalid selector clause: {clause}")
        field, value = clause.split("=", 1)
        require(bool(field) and field not in parsed, f"invalid selector field: {field}")
        parsed[field] = value
    return parsed


def select_one(rows: list[dict[str, str]], selector: str) -> dict[str, str]:
    wanted = parse_selector(selector)
    matches = [row for row in rows if all(row.get(field) == value for field, value in wanted.items())]
    require(len(matches) == 1, f"selector {selector!r}: {len(matches)} matches")
    return matches[0]


def render_line(values: list[str]) -> str:
    rendered = ""
    for value in values:
        if value in {".", ";"}:
            rendered = rendered.rstrip(" ·") + value
        elif rendered:
            rendered += " " if rendered.endswith((".", ";", ":")) else " · "
            rendered += value
        else:
            rendered = value
    return rendered


def display_line(value: str) -> tuple[str, int]:
    require(bool(value), "empty line reader")
    rendered = value[0].upper() + value[1:]
    added = int(not rendered.endswith((".", ";", ":", "!", "?")))
    return rendered + ("." if added else ""), added


def validate_baselines(
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
    require(len(v56) == len(v57) == 51, "baseline line count")
    order56 = [row["locus"] for row in v56]
    order57 = [row["locus"] for row in v57]
    require(order56 == order57 and len(set(order57)) == 51, "V56/V57 locus identity or order")
    by56 = {row["locus"]: row for row in v56}
    by57 = {row["locus"]: row for row in v57}
    require(len(contexts) == 479, "V98 context count")
    expected_ids = [f"P{ordinal:03d}" for ordinal in range(1, 480)]
    require([row["position_id"] for row in contexts] == expected_ids, "V98 position identity/order")
    require(len({row["page"] for row in contexts}) == 36, "V98 page count")
    require(all(not row["page"].casefold().startswith(("f84", "f84r")) for row in contexts), "forbidden held page present")
    grouped: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    by_position: dict[str, dict[str, str]] = {}
    for row in contexts:
        grouped[row["locus"]].append(row)
        require(row["position_id"] not in by_position, "duplicate position")
        by_position[row["position_id"]] = row
        require(row["v98_historical_confirmation"] == HISTORICAL, "context historical claim")
    require(set(grouped) == set(order57), "context/baseline locus set")
    v56_to_v57 = 0
    v57_to_v98 = 0
    v56_to_v98 = 0
    changed_loci = 0
    for locus in order57:
        line_rows = sorted(grouped[locus], key=lambda row: int(row["token_ordinal"]))
        grouped[locus] = line_rows
        require([int(row["token_ordinal"]) for row in line_rows] == list(range(1, len(line_rows) + 1)), f"{locus}: token ordinals")
        old, base = by56[locus], by57[locus]
        require(old["page"] == base["page"] == line_rows[0]["page"], f"{locus}: page parity")
        require(int(old["token_count"]) == int(base["token_count"]) == len(line_rows), f"{locus}: token count")
        surfaces = [row["surface"] for row in line_rows]
        require(old["zl3b_line"].split() == base["zl3b_line"].split() == surfaces, f"{locus}: surface/order parity")
        old_values = old["literal_token_glosses_de"].split(" | ")
        base_values = base["literal_token_glosses_de"].split(" | ")
        current_values = [row["v98_context_realization_de"] for row in line_rows]
        require(base_values == [row["v57_baseline_gloss_de"] for row in line_rows], f"{locus}: embedded V57 baseline mismatch")
        v56_to_v57 += sum(a != b for a, b in zip(old_values, base_values, strict=True))
        local_delta = sum(a != b for a, b in zip(base_values, current_values, strict=True))
        v57_to_v98 += local_delta
        v56_to_v98 += sum(a != b for a, b in zip(old_values, current_values, strict=True))
        changed_loci += int(local_delta > 0)
    require(v56_to_v57 == 7, f"V56→V57 delta {v56_to_v57}")
    require(v57_to_v98 == 357 and v56_to_v98 == 357, "V98 baseline delta totals")
    require(changed_loci == 50, f"V98 changed loci {changed_loci}")
    return order57, by56, by57, dict(grouped), by_position


def validate_inherited_rules(
    spans: list[dict[str, str]],
    executions: list[dict[str, str]],
    by_position: dict[str, dict[str, str]],
) -> list[dict[str, Any]]:
    require(len(spans) == len(executions) == 5, "inherited span count")
    execution_by_id = {row["bound_span_id"]: row for row in executions}
    require(len(execution_by_id) == 5, "inherited execution identities")
    rules: list[dict[str, Any]] = []
    for span in spans:
        span_id = span["bound_span_id"]
        consumed = [span["left_position_id"], span["right_position_id"]]
        source_rows = [by_position[item] for item in consumed]
        require({row["locus"] for row in source_rows} == {span["locus"]}, f"{span_id}: locus")
        require([row["surface"] for row in source_rows] == [span["left_surface"], span["right_surface"]], f"{span_id}: surfaces")
        require(int(source_rows[1]["token_ordinal"]) == int(source_rows[0]["token_ordinal"]) + 1, f"{span_id}: adjacency")
        execution = execution_by_id[span_id]
        require(execution["consumed_position_ids"] == "|".join(consumed), f"{span_id}: execution positions")
        require(execution["render_once_de"] == span["render_once_de"], f"{span_id}: execution text")
        require(execution["execution_status"] == "EXECUTABLE_RENDER_ONCE", f"{span_id}: execution status")
        require(execution["emitted_output_units"] == "1" and execution["standalone_outputs_suppressed"] == "2", f"{span_id}: execution cardinality")
        require(span["global_export_allowed"] == execution["global_export_allowed"] == "0", f"{span_id}: export")
        require(span["historical_confirmation"] == execution["historical_confirmation"] == HISTORICAL, f"{span_id}: historical")
        rules.append({
            "rule_id": span_id,
            "rule_origin": "INHERITED_V98_BOUND_SPAN",
            "anchor_position_id": consumed[0],
            "consumed_position_ids": consumed,
            "render_once_de": span["render_once_de"],
        })
    return rules


def validate_patch_rules(
    specs: list[dict[str, str]],
    artifact: list[dict[str, str]],
    by_position: dict[str, dict[str, str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    require(len(specs) == len(artifact) == 10, "patch row count")
    source_cache: dict[Path, list[dict[str, str]]] = {}
    expected_audit: list[dict[str, Any]] = []
    groups: list[dict[str, Any]] = []
    overrides: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for spec in specs:
        patch_id = spec["patch_id"]
        require(patch_id not in seen_ids, f"duplicate patch {patch_id}")
        seen_ids.add(patch_id)
        consumed = split_pipe(spec["consumed_position_ids"])
        support = split_pipe(spec["support_position_ids"])
        require(spec["anchor_position_id"] == consumed[0], f"{patch_id}: anchor")
        require(all(item in by_position for item in consumed + support), f"{patch_id}: position reference")
        consumed_rows = [by_position[item] for item in consumed]
        require({row["locus"] for row in consumed_rows} == {spec["expected_locus"]}, f"{patch_id}: locus")
        require([row["surface"] for row in consumed_rows] == split_pipe(spec["expected_surfaces"]), f"{patch_id}: surfaces")
        expected_contexts = [piece.strip() for piece in spec["expected_contexts_de"].split(" || ")]
        require([row["v98_context_realization_de"] for row in consumed_rows] == expected_contexts, f"{patch_id}: context snapshots")
        ordinals = [int(row["token_ordinal"]) for row in consumed_rows]
        require(ordinals == list(range(ordinals[0], ordinals[0] + len(ordinals))), f"{patch_id}: adjacency")
        source_path = ROOT / spec["source_artifact"]
        require("f84" not in str(source_path).casefold(), f"{patch_id}: forbidden source path")
        source_cache.setdefault(source_path, read_tsv(source_path))
        source_row = select_one(source_cache[source_path], spec["source_selector"])
        expected_audit.append({
            **spec,
            "consumed_position_count": len(consumed),
            "support_snapshot_de": " || ".join(by_position[item]["v98_context_realization_de"] for item in support),
            "source_row_fingerprint_sha256": fingerprint(source_row),
            "source_row_match": 1,
            "dictionary_core_changes": 0,
            "context_table_changes": 0,
            "score_changes": 0,
            "audit_status": "PASS_BOUND_LOCAL_RENDERER_ONLY",
        })
        rule = {
            "rule_id": patch_id,
            "rule_origin": "GDT726_LOCAL_RENDER_PATCH",
            "anchor_position_id": consumed[0],
            "consumed_position_ids": consumed,
            "render_once_de": spec["render_once_de"],
            "patch_scope": spec["patch_scope"],
        }
        if spec["rule_kind"] == "BOUND_GROUP":
            require(len(consumed) == 2, f"{patch_id}: bound group size")
            groups.append(rule)
        else:
            require(spec["rule_kind"] == "POSITION_OVERRIDE" and len(consumed) == 1, f"{patch_id}: override cardinality")
            overrides.append(rule)
        require(spec["component_global_export_allowed"] == spec["score_delta"] == "0", f"{patch_id}: forbidden delta")
        require(spec["historical_confirmation"] == HISTORICAL, f"{patch_id}: historical")
    require(len(groups) == 3 and len(overrides) == 7, "patch kind totals")
    require(sum(rule["patch_scope"].startswith("INHERITED") for rule in overrides) == 1, "companion count")
    compare_rows("patch audit", artifact, expected_audit)
    return groups, overrides


def validate_companion(
    specs: list[dict[str, str]],
    audits: list[dict[str, str]],
    by_position: dict[str, dict[str, str]],
    overrides: list[dict[str, Any]],
) -> None:
    require(len(specs) == len(audits) == 1, "companion cardinality")
    spec, audit = specs[0], audits[0]
    context = by_position["P265"]
    require(spec["position_id"] == audit["position_id"] == context["position_id"] == "P265", "companion position")
    require(context["surface"] == "daiin" and context["v98_lexical_core_de"] == "Wert III", "companion core")
    require(context["v98_context_realization_de"] == "drei" and context["v98_lexical_score"] == "42", "companion context/score")
    require(spec["line_render_once_de"] == audit["line_render_once_de"], "companion text parity")
    local = [rule for rule in overrides if rule["rule_id"] == "R010_G725_COMPANION_P265"]
    require(len(local) == 1 and local[0]["render_once_de"] == spec["line_render_once_de"], "local companion inheritance")
    require(spec["component_global_export_allowed"] == audit["component_global_export_allowed"] == "0", "companion export")
    require(audit["score_delta"] == audit["score_credit"] == "0", "companion score")
    require(spec["historical_confirmation"] == audit["historical_confirmation"] == HISTORICAL, "companion historical")


def assert_rule_disjoint(rules: list[dict[str, Any]]) -> None:
    owner: dict[str, str] = {}
    for rule in rules:
        for position_id in rule["consumed_position_ids"]:
            require(position_id not in owner, f"overlap {position_id}: {owner.get(position_id)} / {rule['rule_id']}")
            owner[position_id] = rule["rule_id"]


def reconstruct_edition(
    edition: str,
    prefix: str,
    order: list[str],
    by56: dict[str, dict[str, str]],
    by57: dict[str, dict[str, str]],
    contexts_by_locus: dict[str, list[dict[str, str]]],
    spans: list[dict[str, Any]],
    overrides: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    assert_rule_disjoint(spans)
    span_owner = {position_id: rule for rule in spans for position_id in rule["consumed_position_ids"]}
    override_owner = {rule["anchor_position_id"]: rule for rule in overrides}
    require(len(override_owner) == len(overrides), f"{edition}: duplicate override")
    require(not set(span_owner) & set(override_owner), f"{edition}: span/override overlap")
    units: list[dict[str, Any]] = []
    lines: list[dict[str, Any]] = []
    position_to_unit: dict[str, dict[str, Any]] = {}
    for locus in order:
        source_rows = contexts_by_locus[locus]
        local_by_position = {row["position_id"]: row for row in source_rows}
        local_units: list[dict[str, Any]] = []
        handled: set[str] = set()
        for source in source_rows:
            position_id = source["position_id"]
            if position_id in handled:
                continue
            rule = span_owner.get(position_id)
            if rule is not None:
                require(position_id == rule["anchor_position_id"], f"{edition}/{position_id}: non-anchor encountered first")
                consumed = rule["consumed_position_ids"]
                consumed_rows = [local_by_position[item] for item in consumed]
                source_kind = "BOUND_SPAN"
                source_ref = rule["rule_id"]
                rendered = rule["render_once_de"]
            else:
                consumed = [position_id]
                consumed_rows = [source]
                override = override_owner.get(position_id)
                if override is None:
                    source_kind = "CONTEXT_POSITION"
                    source_ref = position_id
                    rendered = source["v98_context_realization_de"]
                else:
                    source_kind = "INHERITED_COMPANION_OVERRIDE" if override["patch_scope"].startswith("INHERITED") else "LOCAL_POSITION_OVERRIDE"
                    source_ref = override["rule_id"]
                    rendered = override["render_once_de"]
            handled.update(consumed)
            unit = {
                "edition": edition,
                "output_unit_id": f"{prefix}U{len(units) + 1:03d}",
                "global_output_ordinal": len(units) + 1,
                "page": source["page"],
                "locus": locus,
                "line_output_ordinal": len(local_units) + 1,
                "source_kind": source_kind,
                "source_ref": source_ref,
                "anchor_position_id": position_id,
                "consumed_position_ids": "|".join(consumed),
                "consumed_position_count": len(consumed),
                "source_surfaces": "|".join(row["surface"] for row in consumed_rows),
                "v98_context_inputs_de": " || ".join(row["v98_context_realization_de"] for row in consumed_rows),
                "rendered_text_de": rendered,
                "component_global_export_allowed": 0,
                "score_delta": 0,
                "historical_confirmation": HISTORICAL,
            }
            units.append(unit)
            local_units.append(unit)
            for item in consumed:
                require(item not in position_to_unit, f"{edition}: double consumption {item}")
                position_to_unit[item] = unit
        require(handled == set(local_by_position), f"{edition}/{locus}: incomplete line consumption")
        base, old = by57[locus], by56[locus]
        base_values = base["literal_token_glosses_de"].split(" | ")
        old_values = old["literal_token_glosses_de"].split(" | ")
        current_values = [row["v98_context_realization_de"] for row in source_rows]
        reader = render_line([str(unit["rendered_text_de"]) for unit in local_units])
        display, terminal_added = display_line(reader)
        applied_spans = [str(unit["source_ref"]) for unit in local_units if unit["source_kind"] == "BOUND_SPAN"]
        applied_overrides = [str(unit["source_ref"]) for unit in local_units if unit["source_kind"] in {"INHERITED_COMPANION_OVERRIDE", "LOCAL_POSITION_OVERRIDE"}]
        hard_hits = [term for term in HARD_GENERIC if term in display.casefold()]
        lines.append({
            "edition": edition,
            "page": base["page"],
            "locus": locus,
            "section": base["section"],
            "language": base["language"],
            "hand": base["hand"],
            "line_mode": base["line_mode"],
            "source_position_count": len(source_rows),
            "rendered_unit_count": len(local_units),
            "v57_to_v98_context_delta_count": sum(a != b for a, b in zip(base_values, current_values, strict=True)),
            "v56_to_v98_context_delta_count": sum(a != b for a, b in zip(old_values, current_values, strict=True)),
            "zl3b_line": base["zl3b_line"],
            "surface_sequence": " ".join(row["surface"] for row in source_rows),
            "position_ids": "|".join(row["position_id"] for row in source_rows),
            "v57_literal_contexts_de": " | ".join(base_values),
            "v98_contexts_de": " | ".join(current_values),
            "rendered_unit_ids": "|".join(str(unit["output_unit_id"]) for unit in local_units),
            "rendered_units_de": " | ".join(str(unit["rendered_text_de"]) for unit in local_units),
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
        })
    all_contexts = [row for locus in order for row in contexts_by_locus[locus]]
    require(set(position_to_unit) == {row["position_id"] for row in all_contexts}, f"{edition}: global position coverage")
    consumption: list[dict[str, Any]] = []
    for source in all_contexts:
        unit = position_to_unit[source["position_id"]]
        emitted_here = unit["anchor_position_id"] == source["position_id"]
        if unit["source_kind"] == "BOUND_SPAN":
            disposition = "BOUND_SPAN_ANCHOR_OUTPUT" if emitted_here else "BOUND_SPAN_MEMBER_SUPPRESSED"
        else:
            disposition = unit["source_kind"]
        consumption.append({
            "edition": edition,
            "position_id": source["position_id"],
            "page": source["page"],
            "locus": source["locus"],
            "token_ordinal": source["token_ordinal"],
            "surface": source["surface"],
            "source_reading_id": source["source_reading_id"],
            "v98_dictionary_core_de": source["v98_lexical_core_de"],
            "v98_context_realization_de": source["v98_context_realization_de"],
            "v98_lexical_score": source["v98_lexical_score"],
            "v98_lexical_level": source["v98_lexical_level"],
            "consumption_disposition": disposition,
            "rule_id": unit["source_ref"],
            "output_unit_id": unit["output_unit_id"],
            "emitted_here": int(emitted_here),
            "emitted_text_de": unit["rendered_text_de"] if emitted_here else "",
            "position_consumed_once": 1,
            "group_position_count": unit["consumed_position_count"],
            "dictionary_core_changed": 0,
            "context_table_changed": 0,
            "score_changed": 0,
            "component_global_export_allowed": 0,
            "historical_confirmation": HISTORICAL,
        })
    return consumption, units, lines


def validate_unit_coverage(
    label: str,
    consumption: list[dict[str, Any]],
    units: list[dict[str, Any]],
    expected_dispositions: dict[str, int],
    expected_kinds: dict[str, int],
) -> None:
    require(Counter(str(row["consumption_disposition"]) for row in consumption) == Counter(expected_dispositions), f"{label}: disposition counts")
    require(Counter(str(row["source_kind"]) for row in units) == Counter(expected_kinds), f"{label}: unit kind counts")
    consumed = [item for row in units for item in split_pipe(str(row["consumed_position_ids"]))]
    require(Counter(consumed) == Counter(f"P{ordinal:03d}" for ordinal in range(1, 480)), f"{label}: output coverage")
    require(all(int(row["position_consumed_once"]) == 1 for row in consumption), f"{label}: consumed-once flag")


def expected_delta_rows(
    order: list[str],
    exact_lines: list[dict[str, Any]],
    practical_lines: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    exact_by_locus = {str(row["locus"]): row for row in exact_lines}
    practical_by_locus = {str(row["locus"]): row for row in practical_lines}
    rows: list[dict[str, Any]] = []
    for locus in order:
        exact = exact_by_locus[locus]
        practical = practical_by_locus[locus]
        rows.append({
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
        })
    return rows


def expected_special_rows(
    inherited: list[dict[str, Any]],
    groups: list[dict[str, Any]],
    directives: list[dict[str, str]],
    f7_source: list[dict[str, str]],
    exact_units: list[dict[str, Any]],
    practical_units: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for rule in inherited + groups:
        old_rule = rule["rule_origin"] == "INHERITED_V98_BOUND_SPAN"
        rows.append({
            "audit_item": rule["rule_id"],
            "audit_class": rule["rule_origin"],
            "consumed_position_ids": "|".join(rule["consumed_position_ids"]),
            "expected_render_once_de": rule["render_once_de"],
            "exact_execution_count": sum(unit["source_ref"] == rule["rule_id"] for unit in exact_units),
            "practical_execution_count": sum(unit["source_ref"] == rule["rule_id"] for unit in practical_units),
            "expected_exact_execution_count": int(old_rule),
            "expected_practical_execution_count": 1,
            "audit_status": "PASS",
            "historical_confirmation": HISTORICAL,
        })
    require(len(directives) == 2, "directive row count")
    require(len({row["render_unit_id"] for row in directives}) == 1, "directives describe more than one unit")
    require(Counter(row["render_action"] for row in directives) == Counter({"EMIT_SPAN_ONCE": 1, "CONSUME_NO_OUTPUT": 1}), "directive actions")
    emitter = next(row for row in directives if row["render_action"] == "EMIT_SPAN_ONCE")
    require({row["bound_span_id"] for row in directives} == {"G678_KEO_R_F7R2"}, "directive span identity")
    require([row["source_position_id"] for row in directives] == ["P288", "P289"], "directive positions")
    rows.append({
        "audit_item": directives[0]["render_unit_id"],
        "audit_class": "ONE_SHOT_DIRECTIVE_PAIR_NOT_TWO_SPANS",
        "consumed_position_ids": "|".join(row["source_position_id"] for row in directives),
        "expected_render_once_de": emitter["emitted_text_de"],
        "exact_execution_count": 1,
        "practical_execution_count": 1,
        "expected_exact_execution_count": 1,
        "expected_practical_execution_count": 1,
        "audit_status": "PASS",
        "historical_confirmation": HISTORICAL,
    })
    expected_f7 = [row["rendered_text_de"] for row in sorted(f7_source, key=lambda row: int(row["output_ordinal"]))]
    exact_f7 = [row for row in exact_units if row["locus"] == "f7r.2"]
    practical_f7 = [row for row in practical_units if row["locus"] == "f7r.2"]
    require(len(f7_source) == len(exact_f7) == len(practical_f7) == 8, "f7r.2 unit count")
    for source, exact, practical in zip(f7_source, exact_f7, practical_f7, strict=True):
        for field in ("page", "locus", "source_kind", "source_ref", "anchor_position_id", "consumed_position_ids", "source_surfaces", "rendered_text_de", "historical_confirmation"):
            require(source[field] == str(exact[field]) == str(practical[field]), f"f7r.2 parity field {field}")
    rows.append({
        "audit_item": "F7R2_8_FROZEN_OUTPUT_UNITS",
        "audit_class": "F7R2_SPECIAL_UNIT_PARITY",
        "consumed_position_ids": "|".join(item for row in f7_source for item in split_pipe(row["consumed_position_ids"])),
        "expected_render_once_de": " | ".join(expected_f7),
        "exact_execution_count": 8,
        "practical_execution_count": 8,
        "expected_exact_execution_count": 8,
        "expected_practical_execution_count": 8,
        "audit_status": "PASS",
        "historical_confirmation": HISTORICAL,
    })
    require(len(rows) == 10, "special audit total")
    return rows


def validate_debts(
    specs: list[dict[str, str]],
    artifact: list[dict[str, str]],
    by_position: dict[str, dict[str, str]],
) -> None:
    require(len(specs) == len(artifact) == 6, "meaning debt count")
    expected: list[dict[str, Any]] = []
    for spec in specs:
        ids = split_pipe(spec["position_ids"])
        rows = [by_position[item] for item in ids]
        expected.append({
            **spec,
            "position_count": len(ids),
            "current_position_values_de": " || ".join(row["v98_context_realization_de"] for row in rows),
            "scores": "|".join(row["v98_lexical_score"] for row in rows),
            "renderer_change_applied": 0,
            "debt_status": "OPEN_REQUIRES_MEANING_OR_SCOPE_DECISION",
            "component_global_export_allowed": 0,
            "score_delta": 0,
        })
    compare_rows("meaning debt audit", artifact, expected)
    require(all(row["renderer_change_applied"] == "0" for row in artifact), "debt hidden by renderer")


def expected_working_reader(exact_lines: list[dict[str, Any]], practical_lines: list[dict[str, Any]]) -> str:
    practical_by_locus = {str(row["locus"]): row for row in practical_lines}
    chunks = [
        "# GDT726 — vollständiger V98/V98R1-Arbeitsreader",
        "",
        "Der Exaktkanal integriert die 479 unveränderten V98-Kontexte mit den fünf geerbten Spans und dem GDT725-Companion. V98R1 ergänzt neun neue lokale Rendererreparaturen; Wörterbuchkerne, Kontexttabelle, Scores und Komponentenexport bleiben unverändert.",
        "",
    ]
    for exact in exact_lines:
        practical = practical_by_locus[str(exact["locus"])]
        chunks.extend([
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
        ])
    return "\n".join(chunks)


def validate_result(result: dict[str, Any]) -> None:
    expected = {
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
        "one_shot_directive_rows": 2,
        "one_shot_semantic_spans": 1,
        "f7r2_frozen_output_units": 8,
        "open_meaning_debts": 6,
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
    require(result == expected, "RESULT.json mismatch")


def main() -> int:
    v56 = read_tsv(V56_PATH)
    v57 = read_tsv(V57_PATH)
    contexts = read_tsv(CONTEXT_PATH)
    spans = read_tsv(SPAN_PATH)
    span_executions = read_tsv(SPAN_EXEC_PATH)
    directives = read_tsv(DIRECTIVE_PATH)
    f7_source = read_tsv(F7_PATH)
    companion_specs = read_tsv(COMPANION_SPEC_PATH)
    companion_audits = read_tsv(COMPANION_AUDIT_PATH)
    patch_specs = read_tsv(PATCH_PATH)
    debt_specs = read_tsv(DEBT_PATH)
    patch_artifact = read_tsv(ART / "V98R1_10_LOCAL_RENDER_PATCH_AUDIT.tsv")
    debt_artifact = read_tsv(ART / "V98R1_6_OPEN_MEANING_DEBT_AUDIT.tsv")
    order, by56, by57, contexts_by_locus, by_position = validate_baselines(v56, v57, contexts)
    inherited = validate_inherited_rules(spans, span_executions, by_position)
    groups, overrides = validate_patch_rules(patch_specs, patch_artifact, by_position)
    validate_companion(companion_specs, companion_audits, by_position, overrides)
    inherited_companion = [rule for rule in overrides if rule["patch_scope"].startswith("INHERITED")]
    exact_consumption, exact_units, exact_lines = reconstruct_edition(
        "V98_EXACT", "X", order, by56, by57, contexts_by_locus, inherited, inherited_companion
    )
    practical_consumption, practical_units, practical_lines = reconstruct_edition(
        "V98R1_PRACTICAL", "P", order, by56, by57, contexts_by_locus, inherited + groups, overrides
    )
    exact_consumption_art = read_tsv(ART / "V98_479_EXACT_POSITION_CONSUMPTION.tsv")
    exact_units_art = read_tsv(ART / "V98_474_EXACT_RENDERED_UNITS.tsv")
    exact_lines_art = read_tsv(ART / "V98_51_EXACT_LINE_READER.tsv")
    practical_consumption_art = read_tsv(ART / "V98R1_479_PRACTICAL_POSITION_CONSUMPTION.tsv")
    practical_units_art = read_tsv(ART / "V98R1_471_PRACTICAL_RENDERED_UNITS.tsv")
    practical_lines_art = read_tsv(ART / "V98R1_51_PRACTICAL_LINE_READER.tsv")
    compare_rows("exact position consumption", exact_consumption_art, exact_consumption)
    compare_rows("exact rendered units", exact_units_art, exact_units)
    compare_rows("exact line reader", exact_lines_art, exact_lines)
    compare_rows("practical position consumption", practical_consumption_art, practical_consumption)
    compare_rows("practical rendered units", practical_units_art, practical_units)
    compare_rows("practical line reader", practical_lines_art, practical_lines)
    require(len(exact_units) == 474 and len(practical_units) == 471, "unit totals")
    validate_unit_coverage(
        "exact",
        exact_consumption,
        exact_units,
        {"CONTEXT_POSITION": 468, "BOUND_SPAN_ANCHOR_OUTPUT": 5, "BOUND_SPAN_MEMBER_SUPPRESSED": 5, "INHERITED_COMPANION_OVERRIDE": 1},
        {"CONTEXT_POSITION": 468, "BOUND_SPAN": 5, "INHERITED_COMPANION_OVERRIDE": 1},
    )
    validate_unit_coverage(
        "practical",
        practical_consumption,
        practical_units,
        {"CONTEXT_POSITION": 456, "BOUND_SPAN_ANCHOR_OUTPUT": 8, "BOUND_SPAN_MEMBER_SUPPRESSED": 8, "LOCAL_POSITION_OVERRIDE": 6, "INHERITED_COMPANION_OVERRIDE": 1},
        {"CONTEXT_POSITION": 456, "BOUND_SPAN": 8, "LOCAL_POSITION_OVERRIDE": 6, "INHERITED_COMPANION_OVERRIDE": 1},
    )
    delta_expected = expected_delta_rows(order, exact_lines, practical_lines)
    compare_rows("line delta audit", read_tsv(ART / "V98_51_LINE_DELTA_AUDIT.tsv"), delta_expected)
    special_expected = expected_special_rows(inherited, groups, directives, f7_source, exact_units, practical_units)
    compare_rows("special execution audit", read_tsv(ART / "V98R1_10_SPECIAL_RULE_EXECUTION_AUDIT.tsv"), special_expected)
    validate_debts(debt_specs, debt_artifact, by_position)
    require(all(row["hard_generic_hits"] == "NONE" for row in exact_lines_art + practical_lines_art), "hard generic text present")
    require(all(row["historical_confirmation"] == HISTORICAL for row in exact_lines_art + practical_lines_art), "line historical claim")
    require(sum(int(row["practical_renderer_changed"]) for row in delta_expected) == 8, "changed practical line count")
    for rule in inherited:
        require(sum(unit["source_ref"] == rule["rule_id"] for unit in exact_units) == 1, f"{rule['rule_id']}: exact occurrence")
        require(sum(unit["source_ref"] == rule["rule_id"] for unit in practical_units) == 1, f"{rule['rule_id']}: practical occurrence")
    for rule in groups:
        require(sum(unit["source_ref"] == rule["rule_id"] for unit in exact_units) == 0, f"{rule['rule_id']}: leaked into exact")
        require(sum(unit["source_ref"] == rule["rule_id"] for unit in practical_units) == 1, f"{rule['rule_id']}: practical occurrence")
    for rule in overrides:
        exact_expected_count = int(rule["patch_scope"].startswith("INHERITED"))
        require(sum(unit["source_ref"] == rule["rule_id"] for unit in exact_units) == exact_expected_count, f"{rule['rule_id']}: exact override count")
        require(sum(unit["source_ref"] == rule["rule_id"] for unit in practical_units) == 1, f"{rule['rule_id']}: practical override count")
    f116 = next(row for row in practical_lines if row["locus"] == "f116r.12")
    require("heißer Ansatz, Grad II" in str(f116["reader_de"]), "f116r.12 lost grade II")
    require("davon zwei Portionen" in str(f116["reader_de"]), "f116r.12 lost first quantity")
    require("zwei Portionen des Materials I im kalten Anfangsansatz" in str(f116["reader_de"]), "f116r.12 lost second quantity")
    reader_expected = expected_working_reader(exact_lines, practical_lines)
    reader_actual = (ART / "GDT726_V98R1_51_LINE_WORKING_READER.md").read_text(encoding="utf-8")
    require(reader_actual == reader_expected, "working reader mismatch")
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    validate_result(result)
    validation = {
        "experiment_id": "GDT726",
        "status": "PASS",
        "generator_imported": 0,
        "artifact_tables_reconstructed_row_for_row": 10,
        "artifact_rows_compared": 2082,
        "working_reader_reconstructed": 1,
        "result_object_reconstructed": 1,
        "exact_positions_consumed_once": 479,
        "practical_positions_consumed_once": 479,
        "exact_rendered_units": 474,
        "practical_rendered_units": 471,
        "f7r2_frozen_units_matched": 8,
        "dictionary_core_changes": 0,
        "context_table_changes": 0,
        "score_changes": 0,
        "component_global_exports": 0,
        "f84_or_f84r_used": 0,
        "historical_confirmation": HISTORICAL,
    }
    validation_path = ART / "VALIDATION.json"
    if validation_path.is_file():
        require(
            json.loads(validation_path.read_text(encoding="utf-8")) == validation,
            "existing VALIDATION.json mismatch",
        )
    else:
        validation_path.write_text(
            json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print(STATUS)
    print("validated: 51 lines; 479 positions; 474 exact units; 471 practical units; 10 special rules; 6 open meaning debts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
