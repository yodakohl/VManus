#!/usr/bin/env python3
"""Independent validator for GDT727 V99 six-meaning-debt dispatch."""

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
sys.path.insert(0, str(ROOT))

from tools.vmanus_experiment import GuardedTSV  # noqa: E402


EXP = ROOT / "experiments/yolo/gdt727_v99_six_meaning_debt_dispatch"
SRC, ART = EXP / "src", EXP / "artifacts"
G725 = ROOT / "experiments/yolo/gdt725_v98_final_low_hardcap_dictionary_dispatch/artifacts"
G726 = ROOT / "experiments/yolo/gdt726_v98_51_line_delta_integration/artifacts"
RAW = ROOT / "transcription/voynich_zl3b_lines.tsv"
STATUS = (
    "PASS_V99_6_MEANING_DEBTS_DISPATCHED__5_LEXICAL_CORES__13_CONTEXTS__"
    "9_LINES__PORTION_FAMILY__4_BOS_PHYSICAL_DISPATCH__3_SHEKY_PATIENTS__"
    "479_POSITIONS_ONCE__471_UNITS__ZERO_SCORE_SCOPE_EXPORT_DELTA__ALL_H0_NONE"
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def split_pipe(value: str) -> list[str]:
    return [item.strip() for item in value.split("|") if item.strip() and item.strip() not in {"NONE", "0"}]


def normalized(row: dict[str, str]) -> dict[str, str]:
    return {key.replace("v99", "v98").replace("V99", "V98"): value for key, value in row.items()}


def changed_fields(old: dict[str, str], new: dict[str, str]) -> set[str]:
    normalized_new = normalized(new)
    assert set(old) == set(normalized_new)
    return {field for field in old if old[field] != normalized_new[field]}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


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


def validate_specs() -> tuple[set[str], set[str], set[str]]:
    lexical = read_tsv(SRC / "V99_5_LEXICAL_READING_SPECS.tsv")
    contexts = read_tsv(SRC / "V99_13_CONTEXT_SPECS.tsv")
    debts = read_tsv(SRC / "V99_6_DEBT_DECISION_SPECS.tsv")
    bos = read_tsv(SRC / "V99_4_BOS_PREDECESSOR_SPECS.tsv")
    lexical_ids = {row["reading_id"] for row in lexical}
    target_positions = {row["position_id"] for row in contexts}
    lexical_positions = {item for row in lexical for item in split_pipe(row["expected_position_ids"])}
    assert len(lexical) == len(lexical_ids) == 5
    assert len(contexts) == len(target_positions) == 13
    assert len(debts) == 6 and {row["debt_id"] for row in debts} == {f"M00{i}" for i in range(1, 7)}
    assert len(bos) == 4 and {row["position_id"] for row in bos} == {"P002", "P142", "P394", "P405"}
    assert lexical_ids == {"ychedaiin#1", "kodeey#1", "pchedaiin#1", "ycheeodaiin#1", "dcheey#1"}
    assert target_positions == {
        "P002", "P025", "P030", "P047", "P053", "P142", "P287",
        "P298", "P301", "P306", "P356", "P394", "P405",
    }
    assert len(lexical_positions) == 6
    assert all(row["historical_confirmation"] == "H0_NONE" for row in [*lexical, *contexts, *debts, *bos])
    return lexical_ids, target_positions, lexical_positions


def validate_lexical(lexical_ids: set[str]) -> tuple[list[dict[str, str]], set[str]]:
    base = read_tsv(G725 / "V98_324_ACTIVE_LEXICAL_READINGS.tsv")
    current = read_tsv(ART / "V99_324_ACTIVE_LEXICAL_READINGS.tsv")
    delta = read_tsv(ART / "V99_5_LEXICAL_READING_DELTA.tsv")
    assert len(base) == len(current) == 324 and len(delta) == 5
    assert [row["v98_reading_id"] for row in base] == [row["v99_reading_id"] for row in current]
    aggregate_ids = {
        "ychedaiin#1", "kodeey#1", "pchedaiin#1", "ycheeodaiin#1", "dcheey#1",
        "cpheesy#1", "tail#1", "sheky#1", "ypchesy#1", "yteedy#1",
    }
    allowed = {
        "v98_lexical_core_de", "v98_context_realizations_de", "source_gdts",
        "source_artifacts", "repair_modes", "resolved_debt_atoms", "last_semantic_writer",
        "positive_evidence_de", "counterevidence_de", "v98_audit_decision",
        "v98_evidence_class", "v98_open_semantic_slots", "v98_prior_lexical_core_de",
    }
    core_changes: set[str] = set()
    aggregate_changes: set[str] = set()
    for old, new in zip(base, current, strict=True):
        reading_id = old["v98_reading_id"]
        changes = changed_fields(old, new)
        if reading_id not in aggregate_ids:
            assert not changes, (reading_id, changes)
        else:
            assert changes and changes <= allowed, (reading_id, changes - allowed)
            aggregate_changes.add(reading_id)
        if old["v98_lexical_core_de"] != new["v99_lexical_core_de"]:
            core_changes.add(reading_id)
        for field in (
            "working_model_score_0_100_not_probability", "working_model_level",
            "semantic_scope", "semantic_applicability", "global_export_scope",
            "unconditional_global_export_allowed", "v98_component_global_export_allowed",
        ):
            assert old[field] == normalized(new)[field]
    assert core_changes == lexical_ids and aggregate_changes == aggregate_ids
    assert {row["reading_id"] for row in delta} == lexical_ids
    assert all(row["lexical_core_changed"] == "1" and row["score_scope_export_unchanged"] == "1" for row in delta)
    return current, aggregate_ids


def validate_contexts(
    current_lexical: list[dict[str, str]], target_positions: set[str], lexical_positions: set[str],
) -> list[dict[str, str]]:
    base = read_tsv(G725 / "V98_479_CONTEXT_REALIZATIONS.tsv")
    current = read_tsv(ART / "V99_479_CONTEXT_REALIZATIONS.tsv")
    delta = read_tsv(ART / "V99_13_CONTEXT_DELTA.tsv")
    assert len(base) == len(current) == 479 and len(delta) == 13
    assert [row["position_id"] for row in base] == [row["position_id"] for row in current] == [f"P{i:03d}" for i in range(1, 480)]
    lex_by_id = {row["v99_reading_id"]: row for row in current_lexical}
    allowed = {
        "working_meaning_de", "last_semantic_writer", "last_semantic_artifact",
        "semantic_change_chain", "last_writer_evidence_de", "position_assignment_writer_gdt",
        "evidence_summary_de", "v98_lexical_core_de", "v98_context_realization_de",
        "v98_repair_mode", "v98_resolved_debt_atom", "v98_audit_decision",
        "v98_evidence_class", "v98_open_semantic_slots", "v98_component_global_export_allowed",
        "v98_boundary_decision", "v98_boundary_render_once_de", "v98_local_context_hypothesis",
    }
    changed_positions: set[str] = set()
    core_changed_positions: set[str] = set()
    for old, new in zip(base, current, strict=True):
        position_id = old["position_id"]
        changes = changed_fields(old, new)
        if position_id not in target_positions:
            assert not changes, (position_id, changes)
        else:
            assert changes and changes <= allowed, (position_id, changes - allowed)
            assert new["v99_lexical_core_de"] == lex_by_id[new["v99_reading_id"]]["v99_lexical_core_de"]
            changed_positions.add(position_id)
        if old["v98_lexical_core_de"] != new["v99_lexical_core_de"]:
            core_changed_positions.add(position_id)
        for field in (
            "v98_lexical_score", "v98_lexical_level", "v98_context_score", "v98_context_level",
            "v98_semantic_scope", "v98_semantic_applicability", "v98_global_export_scope",
            "v98_unconditional_global_export_allowed", "v98_occurrence_bound_span_id",
        ):
            assert old[field] == normalized(new)[field]
    assert changed_positions == target_positions
    assert core_changed_positions == lexical_positions
    assert {row["position_id"] for row in delta} == target_positions
    assert all(row["context_changed"] == "1" and row["score_scope_export_unchanged"] == "1" for row in delta)
    assert all("Dosis" not in row["v99_context_de"] and "Dosen" not in row["v99_context_de"] for row in delta)
    sheky = [row for row in delta if row["expected_surface"] == "sheky"]
    assert len(sheky) == 3 and len({row["patient_or_source_binding"] for row in sheky}) == 3
    assert all("dreimal" not in row["v99_context_de"].casefold() for row in sheky)
    return current


def validate_complete(aggregate_ids: set[str], lexical: list[dict[str, str]]) -> None:
    base = read_tsv(G725 / "V98_COMPLETE_WORD_CONFIDENCE.tsv")
    current = read_tsv(ART / "V99_COMPLETE_WORD_CONFIDENCE.tsv")
    assert len(base) == len(current) == 1586
    assert [(row["surface"], row["reading_id"]) for row in base] == [(row["surface"], row["reading_id"]) for row in current]
    lex_by_id = {row["v99_reading_id"]: row for row in lexical}
    active_ids = set(lex_by_id)
    allowed = {
        "working_meaning_de", "current_layer", "source_gdts", "positive_evidence_de",
        "counterevidence_de", "relation_word_delta", "v98_context_realizations_de",
        "v98_audit_decision", "v98_evidence_class", "v98_open_semantic_slots",
        "v98_component_global_export_allowed", "v98_prior_lexical_core_de",
    }
    core_changes: set[str] = set()
    for old, new in zip(base, current, strict=True):
        reading_id = old["reading_id"]
        changes = changed_fields(old, new)
        if reading_id not in aggregate_ids:
            if reading_id in active_ids:
                assert changes == {"current_layer"}, (reading_id, changes)
            else:
                assert not changes, (reading_id, changes)
        else:
            assert changes and changes <= allowed, (reading_id, changes - allowed)
            assert new["working_meaning_de"] == lex_by_id[reading_id]["v99_lexical_core_de"]
        if reading_id in active_ids:
            assert new["current_layer"] == "ACTIVE_V99_LEXICAL_CORE"
            assert new["working_meaning_de"] == lex_by_id[reading_id]["v99_lexical_core_de"]
        if old["working_meaning_de"] != new["working_meaning_de"]:
            core_changes.add(reading_id)
        assert old["working_model_score_0_100_not_probability"] == new["working_model_score_0_100_not_probability"]
        assert old["working_model_level"] == new["working_model_level"]
        assert new["positive_evidence_de"] and new["counterevidence_de"]
        assert 0 <= int(new["working_model_score_0_100_not_probability"]) <= 100
    assert core_changes == {"ychedaiin#1", "kodeey#1", "pchedaiin#1", "ycheeodaiin#1", "dcheey#1"}
    assert Counter(row["current_layer"] for row in current) == Counter({
        "ACTIVE_V99_LEXICAL_CORE": 324,
        "GLOBAL_V48_DEFAULT": 1262,
    })


def validate_bos() -> None:
    specs = read_tsv(SRC / "V99_4_BOS_PREDECESSOR_SPECS.tsv")
    audit = read_tsv(ART / "V99_4_BOS_PHYSICAL_PREDECESSOR_AUDIT.tsv")
    assert len(specs) == len(audit) == 4
    allowed_pages = {row["page"] for row in specs}
    source = GuardedTSV(
        RAW, selector_column="page", allowed_values=allowed_pages,
        forbidden_prefixes=("f84",), forbidden_action="skip",
    )
    raw = list(source)
    by_locus = {row["locus"]: row for row in raw}
    for spec, row in zip(specs, audit, strict=True):
        previous, current = by_locus[spec["predecessor_locus"]], by_locus[spec["current_locus"]]
        assert previous["eva_clean"] == spec["expected_predecessor_line"]
        assert current["eva_clean"] == spec["expected_current_line"]
        assert int(current["line_number"]) == int(previous["line_number"]) + 1
        assert row["same_physical_page"] == row["immediately_adjacent"] == row["same_paragraph_code"] == "1"
        assert row["guard_status"] == "PASS_EXPLICIT_PAGE_ALLOWLIST_F84_PREFIX_SKIPPED"
        assert int(row["guard_skipped_forbidden_before_materialization"]) == source.stats.skipped_forbidden > 0
    assert Counter(row["decision"] for row in audit) == Counter({
        "DETACH_AMBIGUOUS_PREDECESSOR": 2,
        "BIND_FINAL_COLD_PREPARATION": 1,
        "BIND_FINAL_STRAINED_HOT_SHARE": 1,
    })


def validate_reader(contexts: list[dict[str, str]], target_positions: set[str], lexical_positions: set[str]) -> None:
    base_units = read_tsv(G726 / "V98R1_471_PRACTICAL_RENDERED_UNITS.tsv")
    base_lines = read_tsv(G726 / "V98R1_51_PRACTICAL_LINE_READER.tsv")
    units = read_tsv(ART / "V99_471_PRACTICAL_RENDERED_UNITS.tsv")
    lines = read_tsv(ART / "V99_51_PRACTICAL_LINE_READER.tsv")
    consumption = read_tsv(ART / "V99_479_PRACTICAL_POSITION_CONSUMPTION.tsv")
    delta = read_tsv(ART / "V99_51_LINE_DELTA_AUDIT.tsv")
    by_position = {row["position_id"]: row for row in contexts}
    assert len(base_units) == len(units) == 471
    assert len(base_lines) == len(lines) == len(delta) == 51
    assert len(consumption) == 479 and len({row["position_id"] for row in consumption}) == 479
    assert Counter(row["source_kind"] for row in units) == Counter({
        "CONTEXT_POSITION": 456, "BOUND_SPAN": 8,
        "LOCAL_POSITION_OVERRIDE": 6, "INHERITED_COMPANION_OVERRIDE": 1,
    })
    consumed = [item for row in units for item in split_pipe(row["consumed_position_ids"])]
    assert len(consumed) == len(set(consumed)) == 479 == len(by_position)
    assert set(consumed) == set(by_position)
    for old, new in zip(base_units, units, strict=True):
        assert old["output_unit_id"] == new["output_unit_id"]
        ids = split_pipe(new["consumed_position_ids"])
        assert new["v99_context_inputs_de"] == " || ".join(by_position[item]["v99_context_realization_de"] for item in ids)
        expected_text = by_position[ids[0]]["v99_context_realization_de"] if old["source_kind"] == "CONTEXT_POSITION" else old["rendered_text_de"]
        assert new["rendered_text_de"] == expected_text
    units_by_id = {row["output_unit_id"]: row for row in units}
    changed_loci: set[str] = set()
    for old, new, audit in zip(base_lines, lines, delta, strict=True):
        assert old["locus"] == new["locus"] == audit["locus"]
        line_units = [units_by_id[item] for item in split_pipe(new["rendered_unit_ids"])]
        expected = render_values([row["rendered_text_de"] for row in line_units])
        assert new["reader_de"] == expected
        ids = split_pipe(new["position_ids"])
        expected_changed = [item for item in ids if item in target_positions]
        assert split_pipe(audit["changed_position_ids"]) == expected_changed
        assert int(audit["changed_position_count"]) == len(expected_changed)
        assert audit["v98r1_reader_sha256"] == text_sha(old["reader_de"])
        assert audit["v99_reader_sha256"] == text_sha(new["reader_de"])
        if old["reader_de"] != new["reader_de"]:
            changed_loci.add(new["locus"])
        assert new["hard_generic_hits"] == "NONE"
        assert int(new["dictionary_core_changes"]) == sum(item in lexical_positions for item in ids)
        assert int(new["context_table_changes"]) == len(expected_changed)
    assert changed_loci == {
        "f104v.2", "f105r.31", "f105v.14", "f114r.26", "f7r.2",
        "f80r.17", "f86v3.18", "f86v5.4", "f86v6.25",
    }
    f7_base = read_tsv(G725 / "V98_8_F7R2_RENDERED_UNITS.tsv")
    f7 = read_tsv(ART / "V99_8_F7R2_RENDERED_UNITS.tsv")
    assert len(f7_base) == len(f7) == 8
    main_f7 = [row for row in units if row["locus"] == "f7r.2"]
    assert len(main_f7) == 8
    shared = {
        "page", "locus", "source_kind", "source_ref", "anchor_position_id",
        "consumed_position_ids", "source_surfaces", "rendered_text_de",
        "historical_confirmation",
    }
    for ordinal, (artifact, main_unit) in enumerate(zip(f7, main_f7, strict=True), start=1):
        assert artifact["output_ordinal"] == str(ordinal)
        assert all(artifact[field] == main_unit[field] for field in shared)
    changed_ordinals = [new["output_ordinal"] for old, new in zip(f7_base, f7, strict=True) if old["rendered_text_de"] != new["rendered_text_de"]]
    assert changed_ordinals == ["1"]
    assert f7[0]["rendered_text_de"] == "eine Portion vollständig trocknen und abschließen"
    assert f7[1]["rendered_text_de"] == "heiße Portion" and f7[1]["consumed_position_ids"] == "P288|P289"


def main() -> int:
    lexical_ids, target_positions, lexical_positions = validate_specs()
    lexical, aggregate_ids = validate_lexical(lexical_ids)
    contexts = validate_contexts(lexical, target_positions, lexical_positions)
    validate_complete(aggregate_ids, lexical)
    validate_bos()
    validate_reader(contexts, target_positions, lexical_positions)
    debts = read_tsv(ART / "V99_6_DEBT_DECISIONS.tsv")
    assert len(debts) == 6 and all(row["debt_status"] == "PROVISIONAL_WORKING_DEFAULT_INSTALLED" for row in debts)
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    assert result["status"] == STATUS
    assert result["lexical_core_changes"] == 5 and result["context_changes"] == 13
    assert result["changed_reader_lines"] == 9 and result["positions_consumed_exactly_once"] == 479
    output_paths = sorted(path for path in ART.iterdir() if path.is_file() and path.name != "VALIDATION.json")
    validation = {
        "experiment_id": "GDT727", "status": "PASS",
        "experiment_status": STATUS,
        "independent_generator_imported": 0,
        "lexical_rows_reconstructed": 324,
        "active_v99_dictionary_rows": 324,
        "context_rows_reconstructed": 479,
        "complete_dictionary_rows_checked_for_confidence_and_evidence": 1586,
        "position_consumption_rows_reconstructed": 479,
        "rendered_units_reconstructed": 471,
        "line_rows_reconstructed": 51,
        "lexical_core_changes": 5, "context_changes": 13,
        "changed_reader_lines": 9, "bos_raw_rows_guarded": 4,
        "f84_rows_skipped_before_materialization": 98,
        "score_scope_export_changes": 0,
        "validated_output_sha256": {str(path.relative_to(ROOT)): sha(path) for path in output_paths},
    }
    target = ART / "VALIDATION.json"
    payload = json.dumps(validation, ensure_ascii=False, indent=2) + "\n"
    if target.exists():
        assert target.read_text(encoding="utf-8") == payload
    else:
        target.write_text(payload, encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
