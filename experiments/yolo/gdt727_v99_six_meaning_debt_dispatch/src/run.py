#!/usr/bin/env python3
"""Build V99 by assigning concrete defaults to the six GDT726 meaning debts."""

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
sys.path.insert(0, str(ROOT))

from tools.vmanus_experiment import GuardedTSV  # noqa: E402


EXP = ROOT / "experiments/yolo/gdt727_v99_six_meaning_debt_dispatch"
SRC = EXP / "src"
ART = EXP / "artifacts"
G725 = ROOT / "experiments/yolo/gdt725_v98_final_low_hardcap_dictionary_dispatch/artifacts"
G726 = ROOT / "experiments/yolo/gdt726_v98_51_line_delta_integration/artifacts"
V56_PATH = ROOT / "experiments/yolo/gdt682_final_seven_hole_line_completion/artifacts/V56_51_LINE_READER.tsv"
RAW_LINES = ROOT / "transcription/voynich_zl3b_lines.tsv"
BASE_LEXICAL = G725 / "V98_324_ACTIVE_LEXICAL_READINGS.tsv"
BASE_CONTEXTS = G725 / "V98_479_CONTEXT_REALIZATIONS.tsv"
BASE_COMPLETE = G725 / "V98_COMPLETE_WORD_CONFIDENCE.tsv"
BASE_CONSUMPTION = G726 / "V98R1_479_PRACTICAL_POSITION_CONSUMPTION.tsv"
BASE_UNITS = G726 / "V98R1_471_PRACTICAL_RENDERED_UNITS.tsv"
BASE_LINES = G726 / "V98R1_51_PRACTICAL_LINE_READER.tsv"
LEXICAL_SPECS = SRC / "V99_5_LEXICAL_READING_SPECS.tsv"
CONTEXT_SPECS = SRC / "V99_13_CONTEXT_SPECS.tsv"
DEBT_SPECS = SRC / "V99_6_DEBT_DECISION_SPECS.tsv"
BOS_SPECS = SRC / "V99_4_BOS_PREDECESSOR_SPECS.tsv"
HISTORICAL = "H0_NONE"
STATUS = (
    "PASS_V99_6_MEANING_DEBTS_DISPATCHED__5_LEXICAL_CORES__13_CONTEXTS__"
    "9_LINES__PORTION_FAMILY__4_BOS_PHYSICAL_DISPATCH__3_SHEKY_PATIENTS__"
    "479_POSITIONS_ONCE__471_UNITS__ZERO_SCORE_SCOPE_EXPORT_DELTA__ALL_H0_NONE"
)
HARD_GENERIC = (
    "arbeitsgut", "arbeitsmaterial", "arbeitsschritt", "arbeitsort",
    "arbeitszyklus", "werkstück",
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


def append_note(value: str, addition: str) -> str:
    return f"{value} || {addition}" if value else addition


def rename_v98(row: dict[str, str]) -> dict[str, Any]:
    return {key.replace("v98", "v99").replace("V98", "V99"): value for key, value in row.items()}


def fingerprint(row: dict[str, str]) -> str:
    payload = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def text_sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def display_line(value: str) -> tuple[str, int]:
    if not value:
        return value, 0
    output = value[0].upper() + value[1:]
    added = int(not output.endswith((".", ";", ":", "!", "?")))
    return output + ("." if added else ""), added


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


def aggregate_contexts(context_specs: list[dict[str, str]]) -> dict[str, str]:
    grouped: defaultdict[str, list[str]] = defaultdict(list)
    for spec in context_specs:
        value = spec["v99_context_de"]
        if value not in grouped[spec["expected_reading_id"]]:
            grouped[spec["expected_reading_id"]].append(value)
    return {reading_id: " || ".join(values) for reading_id, values in grouped.items()}


def build_lexical(
    base: list[dict[str, str]], lexical_specs: list[dict[str, str]],
    context_specs: list[dict[str, str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    assert len(base) == 324 and len(lexical_specs) == 5
    lexical_by_id = {row["v98_reading_id"]: row for row in base}
    spec_by_id = {row["reading_id"]: row for row in lexical_specs}
    aggregates = aggregate_contexts(context_specs)
    assert set(spec_by_id) == {
        "ychedaiin#1", "kodeey#1", "pchedaiin#1", "ycheeodaiin#1", "dcheey#1"
    }
    assert set(aggregates) == {
        *spec_by_id, "cpheesy#1", "tail#1", "sheky#1", "ypchesy#1", "yteedy#1"
    }
    output: list[dict[str, Any]] = []
    delta: list[dict[str, Any]] = []
    for source in base:
        row = rename_v98(source)
        reading_id = source["v98_reading_id"]
        if reading_id in aggregates:
            spec = spec_by_id.get(reading_id)
            old_core = source["v98_lexical_core_de"]
            new_core = spec["v99_lexical_core_de"] if spec else old_core
            if spec:
                assert source["surface"] == spec["surface"]
                assert old_core == spec["expected_old_core_de"]
                expected_positions = split_pipe(spec["expected_position_ids"])
                assert int(source["occurrence_count"]) == len(expected_positions)
                evidence = spec["positive_evidence_de"]
                counter = spec["counterevidence_de"]
                atoms = spec["resolved_debt_atoms"]
                decision = spec["decision_class"]
            else:
                related = [item for item in context_specs if item["expected_reading_id"] == reading_id]
                evidence = "GDT727 positionsgebundener Kontext-Dispatch: " + " || ".join(item["evidence_de"] for item in related)
                counter = "GDT727 Grenze: " + " || ".join(item["counterevidence_de"] for item in related)
                atoms = "|".join(dict.fromkeys(atom for item in related for atom in split_pipe(item["resolved_debt_atoms"])))
                decision = "CONTEXT_ONLY_MEANING_DEBT_DISPATCH"
            row["v99_lexical_core_de"] = new_core
            row["v99_context_realizations_de"] = aggregates[reading_id]
            row["source_gdts"] = append_pipe(source["source_gdts"], "GDT727")
            row["source_artifacts"] = append_pipe(source["source_artifacts"], "V99_13_CONTEXT_DELTA.tsv")
            row["repair_modes"] = append_pipe(source["repair_modes"], "GDT727_SIX_DEBT_DISPATCH")
            row["resolved_debt_atoms"] = append_pipe(source["resolved_debt_atoms"], atoms)
            row["last_semantic_writer"] = "GDT727"
            row["positive_evidence_de"] = append_note(source["positive_evidence_de"], "GDT727: " + evidence)
            row["counterevidence_de"] = append_note(source["counterevidence_de"], "GDT727: " + counter)
            row["v99_audit_decision"] = decision
            row["v99_evidence_class"] = "EXACT_WHOLE_PLUS_POSITION_DISPATCH"
            row["v99_open_semantic_slots"] = counter
            row["v99_prior_lexical_core_de"] = old_core
            assert row["working_model_score_0_100_not_probability"] == source["working_model_score_0_100_not_probability"]
        output.append(row)
    assert len(output) == 324
    for spec in lexical_specs:
        old = lexical_by_id[spec["reading_id"]]
        new = next(row for row in output if row["v99_reading_id"] == spec["reading_id"])
        delta.append({
            **spec,
            "old_context_aggregate_de": old["v98_context_realizations_de"],
            "old_score": old["working_model_score_0_100_not_probability"],
            "new_score": new["working_model_score_0_100_not_probability"],
            "old_level": old["working_model_level"],
            "new_level": new["working_model_level"],
            "old_scope": old["global_export_scope"],
            "new_scope": new["global_export_scope"],
            "old_component_export": old["v98_component_global_export_allowed"],
            "new_component_export": new["v99_component_global_export_allowed"],
            "lexical_core_changed": int(old["v98_lexical_core_de"] != new["v99_lexical_core_de"]),
            "score_scope_export_unchanged": 1,
        })
    assert all(int(row["lexical_core_changed"]) == 1 for row in delta)
    return output, delta


def build_contexts(
    base: list[dict[str, str]], lexical: list[dict[str, Any]], specs: list[dict[str, str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    assert len(base) == 479 and len(specs) == 13
    spec_by_position = {row["position_id"]: row for row in specs}
    assert len(spec_by_position) == 13
    lexical_by_id = {row["v99_reading_id"]: row for row in lexical}
    output: list[dict[str, Any]] = []
    delta: list[dict[str, Any]] = []
    for source in base:
        row = rename_v98(source)
        spec = spec_by_position.get(source["position_id"])
        if spec:
            assert (source["page"], source["locus"], source["token_ordinal"], source["surface"], source["source_reading_id"]) == (
                spec["expected_page"], spec["expected_locus"], spec["expected_token_ordinal"],
                spec["expected_surface"], spec["expected_reading_id"],
            )
            assert source["v98_context_realization_de"] == spec["expected_old_context_de"]
            lex = lexical_by_id[spec["expected_reading_id"]]
            row["working_meaning_de"] = spec["v99_context_de"]
            row["last_semantic_writer"] = "GDT727"
            row["last_semantic_artifact"] = "V99_13_CONTEXT_DELTA.tsv"
            row["semantic_change_chain"] = append_pipe(source["semantic_change_chain"], "GDT727")
            row["last_writer_evidence_de"] = spec["evidence_de"]
            row["position_assignment_writer_gdt"] = "GDT727"
            row["evidence_summary_de"] = append_note(source["evidence_summary_de"], "GDT727: " + spec["evidence_de"])
            row["v99_lexical_core_de"] = lex["v99_lexical_core_de"]
            row["v99_context_realization_de"] = spec["v99_context_de"]
            row["v99_repair_mode"] = spec["dispatch_classes"]
            row["v99_resolved_debt_atom"] = spec["resolved_debt_atoms"]
            row["v99_audit_decision"] = "GDT727_PROVISIONAL_DEFAULT_ASSIGNED"
            row["v99_evidence_class"] = "EXACT_WHOLE_PLUS_LOCAL_DISPATCH"
            row["v99_open_semantic_slots"] = spec["counterevidence_de"]
            row["v99_component_global_export_allowed"] = "0"
            row["v99_boundary_decision"] = spec["dispatch_classes"]
            row["v99_boundary_render_once_de"] = spec["v99_context_de"] if "BOS_" in spec["dispatch_classes"] else source["v98_boundary_render_once_de"]
            row["v99_local_context_hypothesis"] = spec["patient_or_source_binding"]
            assert source["v98_lexical_score"] == row["v99_lexical_score"]
            assert source["v98_lexical_level"] == spec["confidence_level"]
            delta.append({
                **spec,
                "old_lexical_core_de": source["v98_lexical_core_de"],
                "v99_lexical_core_de": row["v99_lexical_core_de"],
                "lexical_core_changed": int(source["v98_lexical_core_de"] != row["v99_lexical_core_de"]),
                "context_changed": 1,
                "score_before": source["v98_lexical_score"],
                "score_after": row["v99_lexical_score"],
                "scope_before": source["v98_global_export_scope"],
                "scope_after": row["v99_global_export_scope"],
                "component_export_before": source["v98_component_global_export_allowed"],
                "component_export_after": row["v99_component_global_export_allowed"],
                "score_scope_export_unchanged": 1,
            })
        output.append(row)
    assert len(output) == 479 and len(delta) == 13
    return output, delta


def build_complete(
    base: list[dict[str, str]], lexical: list[dict[str, Any]], context_specs: list[dict[str, str]],
) -> list[dict[str, Any]]:
    assert len(base) == 1586
    lexical_by_id = {row["v99_reading_id"]: row for row in lexical}
    aggregates = aggregate_contexts(context_specs)
    output: list[dict[str, Any]] = []
    seen: set[str] = set()
    for source in base:
        row = rename_v98(source)
        reading_id = source["reading_id"]
        if reading_id in lexical_by_id:
            row["current_layer"] = "ACTIVE_V99_LEXICAL_CORE"
        if reading_id in aggregates:
            lex = lexical_by_id[reading_id]
            old_meaning = source["working_meaning_de"]
            row["working_meaning_de"] = lex["v99_lexical_core_de"]
            row["source_gdts"] = append_pipe(source["source_gdts"], "GDT727")
            row["positive_evidence_de"] = lex["positive_evidence_de"]
            row["counterevidence_de"] = lex["counterevidence_de"]
            row["relation_word_delta"] = "0_GDT696_TO_GDT727"
            row["v99_context_realizations_de"] = aggregates[reading_id]
            row["v99_audit_decision"] = lex["v99_audit_decision"]
            row["v99_evidence_class"] = lex["v99_evidence_class"]
            row["v99_open_semantic_slots"] = lex["v99_open_semantic_slots"]
            row["v99_component_global_export_allowed"] = "0"
            row["v99_prior_lexical_core_de"] = old_meaning
            seen.add(reading_id)
            assert source["working_model_score_0_100_not_probability"] == row["working_model_score_0_100_not_probability"]
        output.append(row)
    assert seen == set(aggregates)
    return output


def best_dictionary_entry(rows: list[dict[str, str]], surface: str) -> dict[str, str] | None:
    matches = [row for row in rows if row["surface"] == surface]
    if not matches:
        return None
    matches.sort(key=lambda row: (
        row["current_layer"].startswith("ACTIVE_V99"),
        int(row["working_model_score_0_100_not_probability"]),
    ), reverse=True)
    return matches[0]


def build_bos_audit(specs: list[dict[str, str]], complete: list[dict[str, str]]) -> list[dict[str, Any]]:
    allowed_pages = {row["page"] for row in specs}
    assert allowed_pages == {"f104v", "f114r", "f86v5", "f86v6"}
    source = GuardedTSV(
        RAW_LINES,
        selector_column="page",
        allowed_values=allowed_pages,
        forbidden_prefixes=("f84",),
        forbidden_action="skip",
    )
    raw = list(source)
    by_locus = {row["locus"]: row for row in raw}
    output: list[dict[str, Any]] = []
    for spec in specs:
        current = by_locus[spec["current_locus"]]
        previous = by_locus[spec["predecessor_locus"]]
        assert current["page"] == previous["page"] == spec["page"]
        assert int(current["line_number"]) == int(previous["line_number"]) + 1
        assert current["eva_clean"] == spec["expected_current_line"]
        assert previous["eva_clean"] == spec["expected_predecessor_line"]
        assert current["code"].endswith(spec["expected_paragraph_id"])
        assert previous["code"].endswith(spec["expected_paragraph_id"])
        support_entries = [best_dictionary_entry(complete, token) for token in split_pipe(spec["support_tokens"])]
        assert all(entry is not None for entry in support_entries)
        missing = split_pipe(spec["missing_or_ambiguous_tokens"])
        missing_states = [best_dictionary_entry(complete, token) is None for token in missing]
        output.append({
            **spec,
            "current_line_number": current["line_number"],
            "predecessor_line_number": previous["line_number"],
            "same_physical_page": 1,
            "immediately_adjacent": 1,
            "same_paragraph_code": 1,
            "support_meanings_de": " || ".join(
                f"{token}={entry['working_meaning_de']} ({entry['working_model_score_0_100_not_probability']})"
                for token, entry in zip(split_pipe(spec["support_tokens"]), support_entries, strict=True)
            ),
            "missing_in_v98_complete_count": sum(missing_states),
            "predecessor_row_fingerprint_sha256": fingerprint(previous),
            "current_row_fingerprint_sha256": fingerprint(current),
            "guard_selected_rows": source.stats.selected,
            "guard_skipped_forbidden_before_materialization": source.stats.skipped_forbidden,
            "guard_status": "PASS_EXPLICIT_PAGE_ALLOWLIST_F84_PREFIX_SKIPPED",
            "component_global_export_allowed": 0,
            "score_delta": 0,
        })
    assert len(output) == 4 and source.stats.skipped_forbidden > 0
    return output


def build_debts(specs: list[dict[str, str]], context_delta: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_position = {row["position_id"]: row for row in context_delta}
    output: list[dict[str, Any]] = []
    for spec in specs:
        ids = split_pipe(spec["position_ids"])
        assert all(item in by_position for item in ids)
        output.append({
            **spec,
            "position_count": len(ids),
            "v99_position_values_de": " || ".join(by_position[item]["v99_context_de"] for item in ids),
            "scores": "|".join(by_position[item]["score_after"] for item in ids),
            "score_delta": 0,
            "component_global_export_allowed": 0,
            "debt_status": "PROVISIONAL_WORKING_DEFAULT_INSTALLED",
        })
    assert len(output) == 6
    return output


def build_reader(
    contexts: list[dict[str, Any]], base_consumption: list[dict[str, str]],
    base_units: list[dict[str, str]], base_lines: list[dict[str, str]],
    v56_lines: list[dict[str, str]], target_positions: set[str], lexical_positions: set[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    by_position = {row["position_id"]: row for row in contexts}
    assert len(by_position) == 479
    units: list[dict[str, Any]] = []
    for source in base_units:
        row = rename_v98(source)
        consumed = split_pipe(source["consumed_position_ids"])
        row["edition"] = "V99_PRACTICAL"
        row["v99_context_inputs_de"] = " || ".join(by_position[item]["v99_context_realization_de"] for item in consumed)
        if source["source_kind"] == "CONTEXT_POSITION":
            assert len(consumed) == 1
            row["rendered_text_de"] = by_position[consumed[0]]["v99_context_realization_de"]
        row["score_delta"] = "0"
        row["component_global_export_allowed"] = "0"
        units.append(row)
    assert len(units) == 471
    unit_by_id = {row["output_unit_id"]: row for row in units}
    unit_by_position: dict[str, dict[str, Any]] = {}
    for unit in units:
        for position_id in split_pipe(unit["consumed_position_ids"]):
            assert position_id not in unit_by_position
            unit_by_position[position_id] = unit
    assert set(unit_by_position) == set(by_position)
    consumption: list[dict[str, Any]] = []
    for source in base_consumption:
        row = rename_v98(source)
        position_id = source["position_id"]
        context = by_position[position_id]
        unit = unit_by_position[position_id]
        emitted = unit["anchor_position_id"] == position_id
        row["edition"] = "V99_PRACTICAL"
        row["v99_dictionary_core_de"] = context["v99_lexical_core_de"]
        row["v99_context_realization_de"] = context["v99_context_realization_de"]
        row["emitted_text_de"] = unit["rendered_text_de"] if emitted else ""
        row["dictionary_core_changed"] = int(position_id in lexical_positions)
        row["context_table_changed"] = int(position_id in target_positions)
        row["score_changed"] = 0
        consumption.append(row)
    assert len(consumption) == 479
    v56_by_locus = {row["locus"]: row for row in v56_lines}
    unit_by_id = {row["output_unit_id"]: row for row in units}
    lines: list[dict[str, Any]] = []
    delta: list[dict[str, Any]] = []
    for base in base_lines:
        row = rename_v98(base)
        position_ids = split_pipe(base["position_ids"])
        line_units = [unit_by_id[item] for item in split_pipe(base["rendered_unit_ids"])]
        current_values = [by_position[item]["v99_context_realization_de"] for item in position_ids]
        v57_values = base["v57_literal_contexts_de"].split(" | ")
        v56_values = v56_by_locus[base["locus"]]["literal_token_glosses_de"].split(" | ")
        assert len(current_values) == len(v57_values) == len(v56_values)
        reader = render_values([str(unit["rendered_text_de"]) for unit in line_units])
        display, terminal = display_line(reader)
        changed_ids = [item for item in position_ids if item in target_positions]
        lexical_ids = [item for item in position_ids if item in lexical_positions]
        row["edition"] = "V99_PRACTICAL"
        row["v57_to_v99_context_delta_count"] = sum(a != b for a, b in zip(v57_values, current_values, strict=True))
        row["v56_to_v99_context_delta_count"] = sum(a != b for a, b in zip(v56_values, current_values, strict=True))
        row["v99_contexts_de"] = " | ".join(current_values)
        row["rendered_units_de"] = " | ".join(str(unit["rendered_text_de"]) for unit in line_units)
        row["reader_de"] = reader
        row["display_reader_de"] = display
        row["display_only_terminal_period_added"] = terminal
        row["hard_generic_hits"] = "|".join(term for term in HARD_GENERIC if term in display.casefold()) or "NONE"
        row["dictionary_core_changes"] = len(lexical_ids)
        row["context_table_changes"] = len(changed_ids)
        row["score_changes"] = 0
        lines.append(row)
        delta.append({
            "page": base["page"],
            "locus": base["locus"],
            "position_count": len(position_ids),
            "changed_position_ids": "|".join(changed_ids) if changed_ids else "NONE",
            "changed_position_count": len(changed_ids),
            "lexical_core_changed_position_ids": "|".join(lexical_ids) if lexical_ids else "NONE",
            "lexical_core_changed_position_count": len(lexical_ids),
            "v98r1_reader_sha256": text_sha(base["reader_de"]),
            "v99_reader_sha256": text_sha(reader),
            "reader_changed": int(base["reader_de"] != reader),
            "v98r1_reader_de": base["reader_de"],
            "v99_reader_de": reader,
            "score_changes": 0,
            "component_global_exports": 0,
            "historical_confirmation": HISTORICAL,
        })
    assert len(lines) == len(delta) == 51
    assert sum(int(row["reader_changed"]) for row in delta) == 9
    f7_units: list[dict[str, Any]] = []
    for ordinal, unit in enumerate((row for row in units if row["locus"] == "f7r.2"), start=1):
        f7_units.append({
            "output_ordinal": ordinal,
            "page": unit["page"], "locus": unit["locus"],
            "source_kind": unit["source_kind"], "source_ref": unit["source_ref"],
            "anchor_position_id": unit["anchor_position_id"],
            "consumed_position_ids": unit["consumed_position_ids"],
            "source_surfaces": unit["source_surfaces"],
            "rendered_text_de": unit["rendered_text_de"],
            "historical_confirmation": HISTORICAL,
        })
    assert len(f7_units) == 8
    return consumption, units, lines, delta, f7_units


def write_reader(path: Path, old_lines: list[dict[str, str]], new_lines: list[dict[str, Any]]) -> None:
    new_by_locus = {row["locus"]: row for row in new_lines}
    chunks = [
        "# GDT727 — vollständiger V99-Arbeitsreader", "",
        "V99 ersetzt die sechs offenen GDT726-Bedeutungsgruppen durch konkrete Arbeitsdefaults: Portion statt Dosis, neutrale Produktköpfe, vier physisch geprüfte BOS-Anschlüsse und drei lokale sheky-Patienten. Alle 479 Positionen bleiben erhalten; historische Bestätigung wird nicht behauptet.", "",
    ]
    for old in old_lines:
        new = new_by_locus[old["locus"]]
        changed = old["reader_de"] != new["reader_de"]
        chunks.extend([
            f"## {old['locus']} ({old['page']})", "",
            f"Voynich: `{old['zl3b_line']}`", "",
            f"V99: {new['display_reader_de']}", "",
            f"V98R1 davor: {old['display_reader_de']}", "" if changed else "Unverändert.", "",
        ])
    path.write_text("\n".join(chunks), encoding="utf-8")


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    lexical_specs, context_specs = read_tsv(LEXICAL_SPECS), read_tsv(CONTEXT_SPECS)
    debt_specs, bos_specs = read_tsv(DEBT_SPECS), read_tsv(BOS_SPECS)
    base_lexical, base_contexts, base_complete = read_tsv(BASE_LEXICAL), read_tsv(BASE_CONTEXTS), read_tsv(BASE_COMPLETE)
    lexical, lexical_delta = build_lexical(base_lexical, lexical_specs, context_specs)
    contexts, context_delta = build_contexts(base_contexts, lexical, context_specs)
    complete = build_complete(base_complete, lexical, context_specs)
    bos = build_bos_audit(bos_specs, complete)
    debts = build_debts(debt_specs, context_delta)
    target_positions = {row["position_id"] for row in context_specs}
    lexical_positions = {item for row in lexical_specs for item in split_pipe(row["expected_position_ids"])}
    consumption, units, lines, line_delta, f7_units = build_reader(
        contexts, read_tsv(BASE_CONSUMPTION), read_tsv(BASE_UNITS), read_tsv(BASE_LINES),
        read_tsv(V56_PATH), target_positions, lexical_positions,
    )
    assert len(lexical_positions) == 6
    assert sum(row["v99_lexical_core_de"] != source["v98_lexical_core_de"] for row, source in zip(lexical, base_lexical, strict=True)) == 5
    assert sum(row["v99_context_realization_de"] != source["v98_context_realization_de"] for row, source in zip(contexts, base_contexts, strict=True)) == 13
    assert all(row["hard_generic_hits"] == "NONE" for row in lines)
    write_tsv(ART / "V99_5_LEXICAL_READING_DELTA.tsv", lexical_delta)
    write_tsv(ART / "V99_13_CONTEXT_DELTA.tsv", context_delta)
    write_tsv(ART / "V99_6_DEBT_DECISIONS.tsv", debts)
    write_tsv(ART / "V99_4_BOS_PHYSICAL_PREDECESSOR_AUDIT.tsv", bos)
    write_tsv(ART / "V99_324_ACTIVE_LEXICAL_READINGS.tsv", lexical)
    write_tsv(ART / "V99_479_CONTEXT_REALIZATIONS.tsv", contexts)
    write_tsv(ART / "V99_COMPLETE_WORD_CONFIDENCE.tsv", complete)
    write_tsv(ART / "V99_479_PRACTICAL_POSITION_CONSUMPTION.tsv", consumption)
    write_tsv(ART / "V99_471_PRACTICAL_RENDERED_UNITS.tsv", units)
    write_tsv(ART / "V99_51_PRACTICAL_LINE_READER.tsv", lines)
    write_tsv(ART / "V99_51_LINE_DELTA_AUDIT.tsv", line_delta)
    write_tsv(ART / "V99_8_F7R2_RENDERED_UNITS.tsv", f7_units)
    write_reader(ART / "GDT727_V99_51_LINE_WORKING_READER.md", read_tsv(BASE_LINES), lines)
    result = {
        "experiment_id": "GDT727", "status": STATUS,
        "source_pages": 36, "source_lines": 51, "source_positions": 479,
        "active_lexical_readings": 324, "complete_dictionary_rows": 1586,
        "meaning_debts_dispatched": 6, "lexical_records_updated": 10,
        "lexical_core_changes": 5,
        "lexical_core_changed_positions": 6, "context_changes": 13,
        "changed_reader_lines": 9, "bos_positions_physically_checked": 4,
        "bos_deictics_detached": 2, "bos_physical_predecessor_carries": 2,
        "sheky_local_patient_dispatches": 3, "portion_family_positions": 6,
        "positions_consumed_exactly_once": 479, "practical_rendered_units": 471,
        "f7r2_rendered_units": 8, "score_changes": 0, "scope_changes": 0,
        "component_global_exports": 0, "historical_confirmation": HISTORICAL,
        "f84_or_f84r_used": 0,
        "canonical_dictionary": "experiments/yolo/gdt727_v99_six_meaning_debt_dispatch/artifacts/V99_COMPLETE_WORD_CONFIDENCE.tsv",
        "complete_working_reader": "experiments/yolo/gdt727_v99_six_meaning_debt_dispatch/artifacts/GDT727_V99_51_LINE_WORKING_READER.md",
    }
    (ART / "RESULT.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
