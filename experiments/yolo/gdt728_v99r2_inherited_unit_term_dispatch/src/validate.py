#!/usr/bin/env python3
"""Independent validator for GDT728 V99R2 inherited unit-term dispatch."""

from __future__ import annotations

import csv
import hashlib
import json
import re
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
EXP = ROOT / "experiments/yolo/gdt728_v99r2_inherited_unit_term_dispatch"
SRC, ART = EXP / "src", EXP / "artifacts"
G727 = ROOT / "experiments/yolo/gdt727_v99_six_meaning_debt_dispatch/artifacts"
BASE = G727 / "V99_COMPLETE_WORD_CONFIDENCE.tsv"
CURRENT = ART / "V99R2_COMPLETE_WORD_CONFIDENCE.tsv"
STATUS = (
    "PASS_V99R2_60_INHERITED_UNIT_TERMS__55_PORTION_1_TEIL_1_MASS_3_WERT_0_HOLD__"
    "293_OCCURRENCES__61X2_DOSE_TOKENS_REMOVED_FROM_SEMANTIC_FIELDS__"
    "324_ACTIVE_V99_BYTE_STABLE__SCORES_EVIDENCE_SCOPE_EXPORT_UNCHANGED__"
    "ZERO_COMPONENT_CREDIT__ALL_H0_NONE"
)
DOSE_RE = re.compile(r"dosis|dosen", re.IGNORECASE)
ALLOWED_TARGET_CHANGES = {
    "working_meaning_de", "source_gdts", "relation_word_delta",
    "v99_context_realizations_de", "v99_audit_decision", "v99_evidence_class",
    "v99_open_semantic_slots", "v99_lineage_class", "v99_value_kind",
}
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


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def row_sha(row: dict[str, str]) -> str:
    payload = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def dose_hits(value: str) -> int:
    return len(DOSE_RE.findall(value))


def split_pipe(value: str) -> list[str]:
    return [item.strip() for item in value.split("|") if item.strip() and item.strip() not in {"0", "NONE"}]


def append_pipe(value: str, addition: str) -> str:
    output: list[str] = []
    for item in [*split_pipe(value), *split_pipe(addition)]:
        if item not in output:
            output.append(item)
    return "|".join(output) if output else "NONE"


def semantic_target(row: dict[str, str]) -> bool:
    return bool(dose_hits(row["working_meaning_de"]) or dose_hits(row["v99_context_realizations_de"]))


def validate_specs(base: list[dict[str, str]]) -> tuple[list[dict[str, str]], set[str]]:
    specs = read_tsv(SRC / "V99R2_60_UNIT_TERM_SPECS.tsv")
    assert len(specs) == 60
    assert [row["decision_id"] for row in specs] == [f"G728-D{i:03d}" for i in range(1, 61)]
    assert len({row["surface"] for row in specs}) == len({row["reading_id"] for row in specs}) == 60
    assert Counter(row["input_category"] for row in specs) == Counter({
        "COUNTED_PLURAL": 24, "SINGULAR_OBJECT": 18, "ROMAN_AXIS": 11,
        "COMPOUND": 6, "REDUNDANT": 1,
    })
    assert Counter(row["dispatch_class"] for row in specs) == Counter({
        "PORTION": 55, "WERT": 3, "TEIL": 1, "MASS": 1,
    })
    assert {row["surface"] for row in specs if row["dispatch_class"] == "WERT"} == {"odan", "odain", "odaiin"}
    assert {row["surface"] for row in specs if row["dispatch_class"] == "MASS"} == {"doly"}
    assert {row["surface"] for row in specs if row["dispatch_class"] == "TEIL"} == {"dolas"}
    assert all(row["component_export_credit"] == "0" and row["historical_confirmation"] == "H0_NONE" for row in specs)
    target_ids = {
        row["reading_id"] for row in base
        if row["current_layer"] == "GLOBAL_V48_DEFAULT" and semantic_target(row)
    }
    assert target_ids == {row["reading_id"] for row in specs}
    base_by_id = {row["reading_id"]: row for row in base}
    for spec in specs:
        source = base_by_id[spec["reading_id"]]
        assert source["surface"] == spec["surface"]
        assert source["working_meaning_de"] == source["v99_context_realizations_de"] == spec["expected_old_meaning_de"]
        candidate = {**source, "working_meaning_de": spec["new_meaning_de"], "v99_context_realizations_de": spec["new_meaning_de"]}
        assert not semantic_target(candidate)
    assert sum(int(base_by_id[row["reading_id"]]["occurrence_count"]) for row in specs) == 293
    assert sum(dose_hits(row["expected_old_meaning_de"]) for row in specs) == 61
    return specs, target_ids


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
        reading_id = old["reading_id"]
        if reading_id in target_ids:
            spec = specs_by_id[reading_id]
            assert changes == ALLOWED_TARGET_CHANGES, (reading_id, changes)
            assert new["working_meaning_de"] == new["v99_context_realizations_de"] == spec["new_meaning_de"]
            assert new["source_gdts"] == append_pipe(old["source_gdts"], "GDT728")
            assert new["relation_word_delta"] == "0_GDT696_TO_GDT728"
            assert new["v99_audit_decision"] == f"GDT728_{spec['dispatch_class']}_EXACT_WHOLE_DISPATCH"
            assert new["v99_evidence_class"] == "EXACT_WHOLE_UNIT_TERM_DISPATCH"
            assert new["v99_open_semantic_slots"] == spec["open_slot_de"]
            assert new["v99_value_kind"] == spec["dispatch_class"]
            assert new["v99_lineage_class"] == "INHERITED_GLOBAL_V48__GDT728_UNIT_TERM_DISPATCH"
        else:
            assert not changes, (reading_id, changes)
            if old["current_layer"] == "ACTIVE_V99_LEXICAL_CORE":
                active_count += 1
            elif old["current_layer"] == "GLOBAL_V48_DEFAULT":
                non_target_global_count += 1
        for field in (
            "surface", "reading_id", "current_layer", "semantic_scope", "semantic_applicability",
            "form_level", "occurrence_count", "page_count", "locus_count",
            "working_model_score_0_100_not_probability", "working_model_level",
            "positive_evidence_de", "counterevidence_de", "historical_confirmation",
            "historical_analogue", "global_export_scope", "bound_span_ids",
            "unconditional_global_export_allowed", "source_reading_ids",
            "v99_component_global_export_allowed", "v99_exact_whole_surface_default_allowed",
            "v99_structural_tag", "v99_action_default_allowed",
        ):
            assert old[field] == new[field], (reading_id, field)
        assert new["positive_evidence_de"] and new["counterevidence_de"]
        assert 0 <= int(new["working_model_score_0_100_not_probability"]) <= 100
    assert active_count == 324 and non_target_global_count == 1202
    assert Counter(row["current_layer"] for row in current) == Counter({
        "ACTIVE_V99_LEXICAL_CORE": 324, "GLOBAL_V48_DEFAULT": 1262,
    })
    assert len({row["surface"] for row in current}) == 1582
    assert not any(semantic_target(row) for row in current)
    assert Counter(row["working_model_level"] for row in base) == Counter(row["working_model_level"] for row in current)


def validate_audit(base: list[dict[str, str]], specs: list[dict[str, str]]) -> None:
    audit = read_tsv(ART / "V99R2_60_UNIT_TERM_AUDIT.tsv")
    summary = read_tsv(ART / "V99R2_DISPATCH_SUMMARY.tsv")
    current = read_tsv(CURRENT)
    base_by_id = {row["reading_id"]: row for row in base}
    current_by_id = {row["reading_id"]: row for row in current}
    assert len(audit) == 60 and [row["decision_id"] for row in audit] == [row["decision_id"] for row in specs]
    assert sum(int(row["observed_occurrence_count"]) for row in audit) == 293
    assert sum(int(row["semantic_dose_hits_before_meaning"]) for row in audit) == 61
    assert sum(int(row["semantic_dose_hits_before_context"]) for row in audit) == 61
    assert sum(int(row["semantic_dose_hits_after_meaning"]) + int(row["semantic_dose_hits_after_context"]) for row in audit) == 0
    assert all(row["score_level_scope_export_evidence_unchanged"] == "1" for row in audit)
    for row in audit:
        source = base_by_id[row["reading_id"]]
        assert row["base_row_sha256"] == row_sha(source)
        assert row["new_row_sha256"] == row_sha(current_by_id[row["reading_id"]])
        assert row["positive_evidence_sha256"] == hashlib.sha256(source["positive_evidence_de"].encode()).hexdigest()
        assert row["counterevidence_sha256"] == hashlib.sha256(source["counterevidence_de"].encode()).hexdigest()
        assert set(row["changed_fields"].split("|")) == ALLOWED_TARGET_CHANGES
    assert len(summary) == 5 and [row["dispatch_class"] for row in summary] == ["PORTION", "TEIL", "MASS", "WERT", "HOLD"]
    assert {row["dispatch_class"]: int(row["target_rows"]) for row in summary} == {
        "PORTION": 55, "TEIL": 1, "MASS": 1, "WERT": 3, "HOLD": 0,
    }
    assert sum(int(row["summed_occurrence_count"]) for row in summary) == 293


def validate_evidence_and_parity() -> None:
    evidence = read_tsv(ART / "V99R2_6_FAMILY_EVIDENCE.tsv")
    historical = read_tsv(ART / "HISTORICAL_QUANTITY_COMPARATORS.tsv")
    parity = read_tsv(ART / "V99R2_ACTIVE_READER_PARITY.tsv")
    assert len(evidence) == 6 and [row["evidence_id"] for row in evidence] == [f"G728-E{i:02d}" for i in range(1, 7)]
    assert Counter(row["dispatch_supported"] for row in evidence) == Counter({"PORTION": 3, "WERT": 1, "MASS": 1, "TEIL": 1})
    assert all(row["relation_credit"] == "0" and row["restriction_de"] for row in evidence)
    historical_specs = read_tsv(SRC / "HISTORICAL_QUANTITY_COMPARATOR_SPECS.tsv")
    assert historical == historical_specs and len(historical) == 5
    assert all(row["source_url"].startswith("https://") for row in historical)
    assert all(row["voynich_relation_credit"] == "0" and row["historical_confirmation"] == "H0_NONE" for row in historical)
    assert len(parity) == len(PARITY_NAMES) == 5
    for name, row in zip(PARITY_NAMES, parity, strict=True):
        source = G727 / name
        assert row["source_artifact"] == str(source.relative_to(ROOT))
        assert row["sha256"] == file_sha(source)
        assert row["gdt728_semantic_edits"] == "0"
        assert row["parity_status"] == "BYTE_STABLE_INPUT_NOT_REWRITTEN"


def main() -> int:
    base = read_tsv(BASE)
    specs, target_ids = validate_specs(base)
    validate_dictionary(base, specs, target_ids)
    validate_audit(base, specs)
    validate_evidence_and_parity()
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    assert result["status"] == STATUS
    assert result["target_exact_whole_rows"] == 60 and result["target_summed_occurrences"] == 293
    assert result["dispatch_counts"] == {"PORTION": 55, "TEIL": 1, "MASS": 1, "WERT": 3, "HOLD": 0}
    assert result["semantic_dose_tokens_remaining"] == 0
    output_paths = sorted(path for path in ART.iterdir() if path.is_file() and path.name != "VALIDATION.json")
    validation = {
        "experiment_id": "GDT728", "status": "PASS", "result_status": STATUS,
        "checks": 92, "target_rows": 60, "target_occurrences": 293,
        "dose_tokens_removed_per_semantic_field": 61,
        "active_v99_rows_byte_stable": 324, "non_target_global_rows_byte_stable": 1202,
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
