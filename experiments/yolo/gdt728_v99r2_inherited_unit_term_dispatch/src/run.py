#!/usr/bin/env python3
"""Build V99R2 by dispatching inherited dose terminology by exact whole."""

from __future__ import annotations

import csv
import hashlib
import json
import re
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
EXP = ROOT / "experiments/yolo/gdt728_v99r2_inherited_unit_term_dispatch"
SRC, ART = EXP / "src", EXP / "artifacts"
G627 = ROOT / "experiments/yolo/gdt627_value_head_role_atlas/artifacts"
G662 = ROOT / "experiments/yolo/gdt662_seventy_six_residual_family_completion/artifacts"
G667 = ROOT / "experiments/yolo/gdt667_one_hundred_one_residual_family_completion/artifacts"
G727 = ROOT / "experiments/yolo/gdt727_v99_six_meaning_debt_dispatch/artifacts"
BASE_COMPLETE = G727 / "V99_COMPLETE_WORD_CONFIDENCE.tsv"
UNIT_SPECS = SRC / "V99R2_60_UNIT_TERM_SPECS.tsv"
HISTORICAL_SPECS = SRC / "HISTORICAL_QUANTITY_COMPARATOR_SPECS.tsv"
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
PARITY_INPUTS = (
    "V99_324_ACTIVE_LEXICAL_READINGS.tsv",
    "V99_479_CONTEXT_REALIZATIONS.tsv",
    "V99_471_PRACTICAL_RENDERED_UNITS.tsv",
    "V99_51_PRACTICAL_LINE_READER.tsv",
    "GDT727_V99_51_LINE_WORKING_READER.md",
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


def dose_hits(value: str) -> int:
    return len(DOSE_RE.findall(value))


def semantic_target(row: dict[str, str]) -> bool:
    return bool(dose_hits(row["working_meaning_de"]) or dose_hits(row["v99_context_realizations_de"]))


def build_dictionary(
    base: list[dict[str, str]], specs: list[dict[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    assert len(base) == 1586 and len(specs) == 60
    spec_by_id = {row["reading_id"]: row for row in specs}
    assert len(spec_by_id) == 60
    semantic_targets = {
        row["reading_id"] for row in base
        if row["current_layer"] == "GLOBAL_V48_DEFAULT" and semantic_target(row)
    }
    assert semantic_targets == set(spec_by_id)

    output: list[dict[str, str]] = []
    audit: list[dict[str, Any]] = []
    for source in base:
        spec = spec_by_id.get(source["reading_id"])
        if not spec:
            output.append(dict(source))
            continue
        assert source["surface"] == spec["surface"]
        assert source["current_layer"] == "GLOBAL_V48_DEFAULT"
        assert source["working_meaning_de"] == spec["expected_old_meaning_de"]
        assert source["v99_context_realizations_de"] == spec["expected_old_meaning_de"]
        assert spec["dispatch_class"] in {"PORTION", "TEIL", "MASS", "WERT", "HOLD"}
        assert spec["component_export_credit"] == "0"
        assert spec["historical_confirmation"] == "H0_NONE"

        row = dict(source)
        row["working_meaning_de"] = spec["new_meaning_de"]
        row["source_gdts"] = append_pipe(source["source_gdts"], "GDT728")
        row["relation_word_delta"] = "0_GDT696_TO_GDT728"
        row["v99_context_realizations_de"] = spec["new_meaning_de"]
        row["v99_audit_decision"] = f"GDT728_{spec['dispatch_class']}_EXACT_WHOLE_DISPATCH"
        row["v99_evidence_class"] = "EXACT_WHOLE_UNIT_TERM_DISPATCH"
        row["v99_open_semantic_slots"] = spec["open_slot_de"]
        row["v99_lineage_class"] = "INHERITED_GLOBAL_V48__GDT728_UNIT_TERM_DISPATCH"
        row["v99_value_kind"] = spec["dispatch_class"]
        changes = {field for field in source if source[field] != row[field]}
        assert changes == ALLOWED_TARGET_CHANGES
        output.append(row)
        audit.append({
            **spec,
            "observed_occurrence_count": source["occurrence_count"],
            "observed_page_count": source["page_count"],
            "working_model_score_0_100_not_probability": source["working_model_score_0_100_not_probability"],
            "working_model_level": source["working_model_level"],
            "semantic_scope": source["semantic_scope"],
            "source_gdts_before": source["source_gdts"],
            "semantic_dose_hits_before_meaning": dose_hits(source["working_meaning_de"]),
            "semantic_dose_hits_before_context": dose_hits(source["v99_context_realizations_de"]),
            "semantic_dose_hits_after_meaning": dose_hits(row["working_meaning_de"]),
            "semantic_dose_hits_after_context": dose_hits(row["v99_context_realizations_de"]),
            "changed_fields": "|".join(field for field in source if field in changes),
            "score_level_scope_export_evidence_unchanged": 1,
            "base_row_sha256": row_sha(source),
            "new_row_sha256": row_sha(row),
            "positive_evidence_sha256": hashlib.sha256(source["positive_evidence_de"].encode()).hexdigest(),
            "counterevidence_sha256": hashlib.sha256(source["counterevidence_de"].encode()).hexdigest(),
        })
    assert len(output) == 1586 and len(audit) == 60
    return output, audit


def build_dispatch_summary(audit: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in audit:
        grouped[row["dispatch_class"]].append(row)
    rows: list[dict[str, Any]] = []
    for dispatch_class in ("PORTION", "TEIL", "MASS", "WERT", "HOLD"):
        members = grouped.get(dispatch_class, [])
        rows.append({
            "dispatch_class": dispatch_class,
            "target_rows": len(members),
            "summed_occurrence_count": sum(int(row["observed_occurrence_count"]) for row in members),
            "input_categories": "|".join(sorted({row["input_category"] for row in members})) or "NONE",
            "exact_surfaces": "|".join(row["surface"] for row in members) or "NONE",
            "all_component_export_credit_zero": int(all(row["component_export_credit"] == "0" for row in members)),
            "all_historical_confirmation_h0_none": int(all(row["historical_confirmation"] == "H0_NONE" for row in members)),
        })
    return rows


def build_family_evidence() -> list[dict[str, Any]]:
    atlas627 = read_tsv(G627 / "HEAD_ROLE_ATLAS.tsv")
    atlas662 = read_tsv(G662 / "FAMILY_COMPOSITION_ATLAS.tsv")
    atlas667 = read_tsv(G667 / "FAMILY_COMPOSITION_ATLAS.tsv")
    delta727 = read_tsv(G727 / "V99_5_LEXICAL_READING_DELTA.tsv")
    da = next(row for row in atlas627 if row["head"] == "da")
    oda = next(row for row in atlas627 if row["head"] == "oda")
    doly = next(row for row in atlas662 if row["surface"] == "doly")
    dolas = next(row for row in atlas667 if row["surface"] == "dolas")
    ddor = next(row for row in atlas667 if row["surface"] == "ddor")
    assert da["role"] == "FREE_MEASURE_OR_DEGREE_HEAD"
    assert oda["role"] == "OPEN_VALUE_HEAD" and oda["default_policy"] == "KEEP_HEAD_OPEN__COMPOSE_VALUE_ONLY"
    assert doly["family"] == dolas["family"] == ddor["family"] == "MEASURE"
    assert len(delta727) == 5 and all("Dosis" not in row["v99_lexical_core_de"] and "Dosen" not in row["v99_lexical_core_de"] for row in delta727)
    return [
        {
            "evidence_id": "G728-E01", "source": "GDT627:HEAD_ROLE_ATLAS:da",
            "observed_form_or_family": da["head"], "observed_role": da["role"],
            "observed_count": da["occurrences"], "dispatch_supported": "PORTION",
            "use_de": "sichtbarer Stoff- oder Teilkopf darf den freien Wert lokal als Arbeitsmenge lesen",
            "restriction_de": "d, dain und daiin erhalten keinen freien Portionswert", "relation_credit": 0,
        },
        {
            "evidence_id": "G728-E02", "source": "GDT627:HEAD_ROLE_ATLAS:oda",
            "observed_form_or_family": oda["head"], "observed_role": oda["role"],
            "observed_count": oda["occurrences"], "dispatch_supported": "WERT",
            "use_de": "der offene od-Kopf trägt eine Wertstufe ohne festgelegte Sachachse",
            "restriction_de": "odan, odain und odaiin werden nicht zu Portionen hochgerechnet", "relation_credit": 0,
        },
        {
            "evidence_id": "G728-E03", "source": "GDT662:FAMILY_COMPOSITION_ATLAS:doly",
            "observed_form_or_family": doly["surface"], "observed_role": doly["family"],
            "observed_count": doly["occurrences"], "dispatch_supported": "MASS",
            "use_de": "exakte Ganzform im Messfamilienregister mit Abguss als Produktkopf",
            "restriction_de": "Maß bleibt auf doly als Ganzform begrenzt; keine historische Einheit", "relation_credit": 0,
        },
        {
            "evidence_id": "G728-E04", "source": "GDT667:FAMILY_COMPOSITION_ATLAS:dolas",
            "observed_form_or_family": dolas["surface"], "observed_role": dolas["composition"],
            "observed_count": dolas["occurrences"], "dispatch_supported": "TEIL",
            "use_de": "der exakte Ganzformpfad enthält einen Teil-/Verhältnislink A_PART_OR_LINK",
            "restriction_de": "Gleichheit wird nicht behauptet; Teil bleibt auf dolas als Ganzform begrenzt", "relation_credit": 0,
        },
        {
            "evidence_id": "G728-E05", "source": "GDT667:FAMILY_COMPOSITION_ATLAS:ddor",
            "observed_form_or_family": ddor["surface"], "observed_role": ddor["composition"],
            "observed_count": ddor["occurrences"], "dispatch_supported": "PORTION",
            "use_de": "OR_PORTION ist bereits der Objektkopf; das zusätzliche Wort Dosis ist redundant",
            "restriction_de": "Messhandlung identifiziert keine absolute Maßeinheit", "relation_credit": 0,
        },
        {
            "evidence_id": "G728-E06", "source": "GDT727:V99_5_LEXICAL_READING_DELTA",
            "observed_form_or_family": "|".join(row["surface"] for row in delta727),
            "observed_role": "ACTIVE_EXACT_WHOLE_PORTION_PRECEDENT", "observed_count": len(delta727),
            "dispatch_supported": "PORTION",
            "use_de": "fünf aktive Ganzwortkerne wurden bereits kontrolliert von Dosis zu Portion gesetzt",
            "restriction_de": "dieser Präzedenzfall ist keine substringbasierte Exportregel", "relation_credit": 0,
        },
    ]


def build_parity() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for name in PARITY_INPUTS:
        path = G727 / name
        if path.suffix == ".tsv":
            row_count = len(read_tsv(path))
        else:
            row_count = sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.startswith("## "))
        rows.append({
            "source_artifact": str(path.relative_to(ROOT)),
            "row_or_section_count": row_count,
            "sha256": file_sha(path),
            "gdt728_semantic_edits": 0,
            "parity_status": "BYTE_STABLE_INPUT_NOT_REWRITTEN",
        })
    return rows


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    base = read_tsv(BASE_COMPLETE)
    specs = read_tsv(UNIT_SPECS)
    historical = read_tsv(HISTORICAL_SPECS)
    current, audit = build_dictionary(base, specs)
    summary = build_dispatch_summary(audit)
    evidence = build_family_evidence()
    parity = build_parity()

    assert Counter(row["input_category"] for row in specs) == Counter({
        "COUNTED_PLURAL": 24, "SINGULAR_OBJECT": 18, "ROMAN_AXIS": 11,
        "COMPOUND": 6, "REDUNDANT": 1,
    })
    assert Counter(row["dispatch_class"] for row in specs) == Counter({
        "PORTION": 55, "WERT": 3, "TEIL": 1, "MASS": 1,
    })
    assert sum(int(row["observed_occurrence_count"]) for row in audit) == 293
    assert sum(int(row["semantic_dose_hits_before_meaning"]) for row in audit) == 61
    assert sum(int(row["semantic_dose_hits_before_context"]) for row in audit) == 61
    assert not any(semantic_target(row) for row in current)
    assert Counter(row["current_layer"] for row in current) == Counter({
        "ACTIVE_V99_LEXICAL_CORE": 324, "GLOBAL_V48_DEFAULT": 1262,
    })
    assert len(historical) == 5 and all(row["voynich_relation_credit"] == "0" and row["historical_confirmation"] == "H0_NONE" for row in historical)

    write_tsv(ART / "V99R2_COMPLETE_WORD_CONFIDENCE.tsv", current, list(base[0]))
    write_tsv(ART / "V99R2_60_UNIT_TERM_AUDIT.tsv", audit)
    write_tsv(ART / "V99R2_DISPATCH_SUMMARY.tsv", summary)
    write_tsv(ART / "V99R2_6_FAMILY_EVIDENCE.tsv", evidence)
    write_tsv(ART / "HISTORICAL_QUANTITY_COMPARATORS.tsv", historical)
    write_tsv(ART / "V99R2_ACTIVE_READER_PARITY.tsv", parity)
    counts = Counter(row["dispatch_class"] for row in specs)
    result = {
        "experiment_id": "GDT728", "status": STATUS,
        "complete_dictionary_rows": 1586, "complete_dictionary_surfaces": 1582,
        "inherited_global_rows": 1262, "active_v99_rows_byte_stable": 324,
        "target_exact_whole_rows": 60, "target_summed_occurrences": 293,
        "input_category_counts": dict(Counter(row["input_category"] for row in specs)),
        "dispatch_counts": {key: counts.get(key, 0) for key in ("PORTION", "TEIL", "MASS", "WERT", "HOLD")},
        "dose_tokens_removed_working_meaning": 61,
        "dose_tokens_removed_context_realizations": 61,
        "semantic_dose_tokens_remaining": 0,
        "historical_comparators": 5, "historical_confirmation": "H0_NONE",
        "score_changes": 0, "confidence_level_changes": 0, "evidence_changes": 0,
        "scope_changes": 0, "export_changes": 0, "component_relation_credit": 0,
        "active_reader_artifacts_byte_stable": len(parity),
        "canonical_dictionary": "experiments/yolo/gdt728_v99r2_inherited_unit_term_dispatch/artifacts/V99R2_COMPLETE_WORD_CONFIDENCE.tsv",
    }
    (ART / "RESULT.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
