#!/usr/bin/env python3
"""Independent validator for GDT729's fourteen scoped quantity decisions."""

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
EXP = ROOT / "experiments/yolo/gdt729_v99r3_fourteen_indexed_quantity_dispatch"
SRC, ART = EXP / "src", EXP / "artifacts"
G727 = ROOT / "experiments/yolo/gdt727_v99_six_meaning_debt_dispatch/artifacts"
G728 = ROOT / "experiments/yolo/gdt728_v99r2_inherited_unit_term_dispatch"
BASE = G728 / "artifacts/V99R2_COMPLETE_WORD_CONFIDENCE.tsv"
CURRENT = ART / "V99R3_COMPLETE_WORD_CONFIDENCE.tsv"
STATUS = (
    "PASS_V99R3_14_QUANTITY_READINGS__5_CARDINAL_1_INDEXED_SHARE_7_OPEN_VALUE_"
    "1_QUALITY_GRADE_0_MEASURE_0_HOLD__140_OCCURRENCES__NO_SLASH_AMBIGUITY_IN_"
    "TARGET_MEANINGS__324_ACTIVE_1248_OTHER_GLOBAL_BYTE_STABLE__SCORE_EVIDENCE_"
    "SCOPE_EXPORT_UNCHANGED__ZERO_COMPONENT_CREDIT__ALL_H0_NONE"
)
TARGET_SURFACES = (
    "arain", "chorain", "choraiin", "cthan", "cthain", "cthaiin", "dan",
    "daiiin", "olain", "olaiin", "oraiin", "qoraiin", "solaiin", "tdain",
)
DISPATCH_CLASSES = (
    "CARDINAL_AMOUNT", "INDEXED_SHARE_AMOUNT", "OPEN_VALUE", "QUALITY_GRADE",
    "LICENSED_MEASURE", "HOLD",
)
EXPECTED_DISPATCH = Counter({
    "CARDINAL_AMOUNT": 5, "INDEXED_SHARE_AMOUNT": 1, "OPEN_VALUE": 7,
    "QUALITY_GRADE": 1,
})
ALLOWED_TARGET_CHANGES = {
    "working_meaning_de", "source_gdts", "relation_word_delta",
    "v99_context_realizations_de", "v99_audit_decision", "v99_evidence_class",
    "v99_open_semantic_slots", "v99_lineage_class", "v99_value_kind",
}
PRESERVED_FIELDS = (
    "surface", "reading_id", "current_layer", "semantic_scope", "semantic_applicability",
    "form_level", "occurrence_count", "page_count", "locus_count",
    "working_model_score_0_100_not_probability", "working_model_level",
    "positive_evidence_de", "counterevidence_de", "historical_confirmation",
    "historical_analogue", "global_export_scope", "bound_span_ids",
    "unconditional_global_export_allowed", "source_reading_ids",
    "v99_component_global_export_allowed", "v99_exact_whole_surface_default_allowed",
    "v99_structural_tag", "v99_action_default_allowed",
)
PARITY_NAMES = (
    "V99_324_ACTIVE_LEXICAL_READINGS.tsv",
    "V99_479_CONTEXT_REALIZATIONS.tsv",
    "V99_471_PRACTICAL_RENDERED_UNITS.tsv",
    "V99_51_PRACTICAL_LINE_READER.tsv",
    "GDT727_V99_51_LINE_WORKING_READER.md",
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def split_pipe(value: str) -> list[str]:
    return [item.strip() for item in value.split("|") if item.strip() and item.strip() not in {"0", "NONE"}]


def append_pipe(value: str, addition: str) -> str:
    output: list[str] = []
    for item in [*split_pipe(value), *split_pipe(addition)]:
        if item not in output:
            output.append(item)
    return "|".join(output) if output else "NONE"


def row_sha(row: dict[str, str]) -> str:
    payload = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_specs(base: list[dict[str, str]]) -> tuple[list[dict[str, str]], set[str]]:
    specs = read_tsv(SRC / "V99R3_14_QUANTITY_DISPATCH_SPECS.tsv")
    assert len(specs) == 14
    assert [row["decision_id"] for row in specs] == [f"G729-D{i:03d}" for i in range(1, 15)]
    assert tuple(row["surface"] for row in specs) == TARGET_SURFACES
    assert len({row["surface"] for row in specs}) == len({row["reading_id"] for row in specs}) == 14
    assert Counter(row["dispatch_class"] for row in specs) == EXPECTED_DISPATCH
    assert all(row["dispatch_class"] in DISPATCH_CLASSES for row in specs)
    assert all(row["component_export_credit"] == "0" and row["historical_confirmation"] == "H0_NONE" for row in specs)
    assert all("/" not in row["new_meaning_de"] for row in specs)
    assert {row["surface"] for row in specs if row["dispatch_class"] == "OPEN_VALUE"} == {
        "chorain", "choraiin", "cthan", "cthain", "cthaiin", "dan", "daiiin",
    }
    assert {row["surface"] for row in specs if row["dispatch_class"] == "CARDINAL_AMOUNT"} == {
        "olain", "olaiin", "oraiin", "qoraiin", "solaiin",
    }
    assert {row["surface"] for row in specs if row["dispatch_class"] == "INDEXED_SHARE_AMOUNT"} == {"arain"}
    assert {row["surface"] for row in specs if row["dispatch_class"] == "QUALITY_GRADE"} == {"tdain"}
    base_by_id = {row["reading_id"]: row for row in base}
    for spec in specs:
        source = base_by_id[spec["reading_id"]]
        assert source["surface"] == spec["surface"]
        assert source["current_layer"] == "GLOBAL_V48_DEFAULT"
        assert source["working_meaning_de"] == source["v99_context_realizations_de"] == spec["expected_old_meaning_de"]
    assert sum(int(base_by_id[row["reading_id"]]["occurrence_count"]) for row in specs) == 140
    return specs, {row["reading_id"] for row in specs}


def validate_dictionary(base: list[dict[str, str]], specs: list[dict[str, str]], target_ids: set[str]) -> None:
    current = read_tsv(CURRENT)
    assert len(base) == len(current) == 1586
    assert list(base[0]) == list(current[0])
    assert [(row["surface"], row["reading_id"]) for row in base] == [(row["surface"], row["reading_id"]) for row in current]
    specs_by_id = {row["reading_id"]: row for row in specs}
    active_count = non_target_global_count = 0
    for old, new in zip(base, current, strict=True):
        assert set(old) == set(new)
        changes = {field for field in old if old[field] != new[field]}
        if old["reading_id"] in target_ids:
            spec = specs_by_id[old["reading_id"]]
            assert changes == ALLOWED_TARGET_CHANGES, (old["reading_id"], changes)
            assert new["working_meaning_de"] == new["v99_context_realizations_de"] == spec["new_meaning_de"]
            assert new["source_gdts"] == append_pipe(old["source_gdts"], "GDT729")
            assert new["relation_word_delta"] == "0_GDT696_TO_GDT729"
            assert new["v99_audit_decision"] == f"GDT729_{spec['dispatch_class']}_SCOPED_WHOLE_DISPATCH"
            assert new["v99_evidence_class"] == "SCOPED_HEAD_VALUE_WHOLE_DISPATCH"
            assert new["v99_open_semantic_slots"] == spec["open_slot_de"]
            assert new["v99_lineage_class"] == "INHERITED_GLOBAL_V48__GDT729_QUANTITY_VALUE_DISPATCH"
            assert new["v99_value_kind"] == spec["dispatch_class"]
        else:
            assert not changes, (old["reading_id"], changes)
            if old["current_layer"] == "ACTIVE_V99_LEXICAL_CORE":
                active_count += 1
            elif old["current_layer"] == "GLOBAL_V48_DEFAULT":
                non_target_global_count += 1
        for field in PRESERVED_FIELDS:
            assert old[field] == new[field], (old["reading_id"], field)
        assert new["positive_evidence_de"] and new["counterevidence_de"]
        assert 0 <= int(new["working_model_score_0_100_not_probability"]) <= 100
    assert active_count == 324 and non_target_global_count == 1248
    assert Counter(row["current_layer"] for row in current) == Counter({"ACTIVE_V99_LEXICAL_CORE": 324, "GLOBAL_V48_DEFAULT": 1262})
    assert len({row["surface"] for row in current}) == 1582
    assert Counter(row["working_model_level"] for row in base) == Counter(row["working_model_level"] for row in current)

    current_by_id = {row["reading_id"]: row for row in current}
    base_by_id = {row["reading_id"]: row for row in base}
    prior_60 = {row["reading_id"] for row in read_tsv(G728 / "src/V99R2_60_UNIT_TERM_SPECS.tsv")}
    assert not prior_60 & target_ids and len(prior_60) == 60
    assert all(current_by_id[reading_id] == base_by_id[reading_id] for reading_id in prior_60)
    explicit_controls = {"ain#GLOBAL", "an#GLOBAL", "orain#GLOBAL", "oraiiin#GLOBAL", "odan#GLOBAL", "odain#GLOBAL", "odaiin#GLOBAL"}
    assert all(current_by_id[reading_id] == base_by_id[reading_id] for reading_id in explicit_controls)
    component_surfaces = {"a", "ain", "an", "ar", "d", "dain", "daiin", "or"}
    for old, new in zip(base, current, strict=True):
        if old["surface"] in component_surfaces:
            assert old == new


def validate_audit(base: list[dict[str, str]], specs: list[dict[str, str]]) -> None:
    current = read_tsv(CURRENT)
    audit = read_tsv(ART / "V99R3_14_QUANTITY_DISPATCH_AUDIT.tsv")
    summary = read_tsv(ART / "V99R3_DISPATCH_SUMMARY.tsv")
    base_by_id = {row["reading_id"]: row for row in base}
    current_by_id = {row["reading_id"]: row for row in current}
    assert len(audit) == 14 and [row["decision_id"] for row in audit] == [row["decision_id"] for row in specs]
    assert sum(int(row["observed_occurrence_count"]) for row in audit) == 140
    assert Counter(row["semantic_scope"] for row in audit) == Counter({"KNOWN_EXACT_WHOLE": 7, "KNOWN_CONTEXT_LICENSED": 7})
    assert Counter(row["working_model_level"] for row in audit) == Counter({"W3_SOLID_WORKING_THEORY": 4, "W2_PROVISIONAL_WORKING": 7, "W1_WEAK_WORKING": 2, "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY": 1})
    assert all(row["score_level_evidence_scope_export_unchanged"] == "1" for row in audit)
    for row in audit:
        source = base_by_id[row["reading_id"]]
        assert row["base_row_sha256"] == row_sha(source)
        assert row["new_row_sha256"] == row_sha(current_by_id[row["reading_id"]])
        assert row["positive_evidence_sha256"] == hashlib.sha256(source["positive_evidence_de"].encode()).hexdigest()
        assert row["counterevidence_sha256"] == hashlib.sha256(source["counterevidence_de"].encode()).hexdigest()
        assert set(row["changed_fields"].split("|")) == ALLOWED_TARGET_CHANGES
    assert len(summary) == len(DISPATCH_CLASSES)
    assert [row["dispatch_class"] for row in summary] == list(DISPATCH_CLASSES)
    assert {row["dispatch_class"]: int(row["target_rows"]) for row in summary} == {
        "CARDINAL_AMOUNT": 5, "INDEXED_SHARE_AMOUNT": 1, "OPEN_VALUE": 7,
        "QUALITY_GRADE": 1, "LICENSED_MEASURE": 0, "HOLD": 0,
    }
    assert sum(int(row["summed_occurrence_count"]) for row in summary) == 140
    assert all(row["all_component_export_credit_zero"] == "1" and row["all_historical_confirmation_h0_none"] == "1" for row in summary)


def validate_evidence_historical_and_parity() -> None:
    evidence = read_tsv(ART / "V99R3_9_HEAD_RULE_EVIDENCE.tsv")
    historical = read_tsv(ART / "HISTORICAL_QUANTITY_COMPARATORS.tsv")
    inherited_historical = read_tsv(G728 / "artifacts/HISTORICAL_QUANTITY_COMPARATORS.tsv")
    parity = read_tsv(ART / "V99R3_ACTIVE_READER_PARITY.tsv")
    assert len(evidence) == 9 and [row["evidence_id"] for row in evidence] == [f"G729-E{i:02d}" for i in range(1, 10)]
    assert Counter(row["dispatch_supported"] for row in evidence) == Counter({"CARDINAL_AMOUNT": 4, "OPEN_VALUE": 3, "INDEXED_SHARE_AMOUNT": 1, "QUALITY_GRADE": 1})
    assert all(row["relation_credit"] == "0" and row["restriction_de"] for row in evidence)
    assert historical == inherited_historical and len(historical) == 5
    assert all(row["source_url"].startswith("https://") for row in historical)
    assert all(row["voynich_relation_credit"] == "0" and row["historical_confirmation"] == "H0_NONE" for row in historical)
    assert len(parity) == len(PARITY_NAMES) == 5
    for name, row in zip(PARITY_NAMES, parity, strict=True):
        source = G727 / name
        assert row["source_artifact"] == str(source.relative_to(ROOT))
        assert row["sha256"] == file_sha(source)
        assert row["gdt729_semantic_edits"] == "0"
        assert row["parity_status"] == "BYTE_STABLE_INPUT_NOT_REWRITTEN"


def main() -> int:
    base = read_tsv(BASE)
    specs, target_ids = validate_specs(base)
    validate_dictionary(base, specs, target_ids)
    validate_audit(base, specs)
    validate_evidence_historical_and_parity()
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    assert result["status"] == STATUS
    assert result["target_rows"] == 14 and result["target_summed_occurrences"] == 140
    assert result["dispatch_counts"] == {
        "CARDINAL_AMOUNT": 5, "INDEXED_SHARE_AMOUNT": 1, "OPEN_VALUE": 7,
        "QUALITY_GRADE": 1, "LICENSED_MEASURE": 0, "HOLD": 0,
    }
    assert result["slash_ambiguity_in_target_meanings"] == 0
    output_paths = sorted(path for path in ART.iterdir() if path.is_file() and path.name != "VALIDATION.json")
    validation = {
        "experiment_id": "GDT729", "status": "PASS", "result_status": STATUS,
        "checks": 104, "target_rows": 14, "target_occurrences": 140,
        "active_v99_rows_byte_stable": 324, "non_target_global_rows_byte_stable": 1248,
        "prior_gdt728_target_rows_byte_stable": 60, "explicit_scope_controls_byte_stable": 7,
        "score_evidence_scope_export_changes": 0, "component_relation_credit": 0,
        "historical_confirmation": "H0_NONE",
        "validated_output_sha256": {str(path.relative_to(ROOT)): file_sha(path) for path in output_paths},
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
