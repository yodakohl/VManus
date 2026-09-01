#!/usr/bin/env python3
"""Build V99R4 from the explicit 94-row ambiguity-default dispatch."""
from __future__ import annotations

import csv, hashlib, json, re, sys
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
EXP = ROOT / "experiments/yolo/gdt730_v99r4_ninety_four_ambiguity_default_dispatch"
SRC, ART = EXP / "src", EXP / "artifacts"
G729 = ROOT / "experiments/yolo/gdt729_v99r3_fourteen_indexed_quantity_dispatch/artifacts"
G727 = ROOT / "experiments/yolo/gdt727_v99_six_meaning_debt_dispatch/artifacts"
G728 = ROOT / "experiments/yolo/gdt728_v99r2_inherited_unit_term_dispatch/artifacts"
G631 = ROOT / "experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts"
G632 = ROOT / "experiments/yolo/gdt632_cth_interfix_lattice/artifacts"
BASE = G729 / "V99R3_COMPLETE_WORD_CONFIDENCE.tsv"
SPECS = SRC / "V99R4_94_AMBIGUITY_DEFAULT_SPECS.tsv"
FALSE_ID = "cphol#GLOBAL"
PARITY_INPUTS = ("V99_324_ACTIVE_LEXICAL_READINGS.tsv", "V99_479_CONTEXT_REALIZATIONS.tsv",
                 "V99_471_PRACTICAL_RENDERED_UNITS.tsv", "V99_51_PRACTICAL_LINE_READER.tsv",
                 "GDT727_V99_51_LINE_WORKING_READER.md")
STATUS = ("PASS_V99R4_94_AMBIGUOUS_GLOBAL_WHOLES__1039_OCCURRENCES__TECHNICAL_"
          "SELECTOR_95_ROWS_1050_OCCURRENCES__CPHOL_LEXICAL_FALSE_POSITIVE__MAIN_"
          "AND_CONTEXT_DEFAULTS_AMBIGUITY_FREE__GDT730_PROVENANCE_APPENDED__SCORE_"
          "CONFIDENCE_EVIDENCE_SCOPE_EXPORT_SPAN_STRUCTURE_ACTION_UNCHANGED__ZERO_COMPONENT_CREDIT")
TARGET_CHANGE_FIELDS = {
    "working_meaning_de", "source_gdts", "relation_word_delta", "v99_context_realizations_de",
    "v99_audit_decision", "v99_evidence_class", "v99_open_semantic_slots",
    "v99_lineage_class", "v99_value_kind",
}

def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))

def write_tsv(path: Path, rows: Iterable[dict[str, Any]], fields: list[str] | None = None) -> None:
    data = list(rows); fields = fields or (list(data[0]) if data else [])
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in data: writer.writerow({field: row.get(field, "") for field in fields})

def row_sha(row: dict[str, str]) -> str:
    raw = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()

def file_sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()

def append_pipe(value: str, addition: str) -> str:
    items = [part.strip() for part in value.split("|") if part.strip() and part.strip() not in {"0", "NONE"}]
    if addition not in items: items.append(addition)
    return "|".join(items) if items else "NONE"

def selector_reasons(row: dict[str, str]) -> list[str]:
    if row["current_layer"] != "GLOBAL_V48_DEFAULT": return []
    meaning = row["working_meaning_de"]; out = []
    if "/" in meaning: out.append("SLASH")
    if re.search(r"(?i)(?<!\w)oder(?!\w)", meaning): out.append("STANDALONE_ODER")
    # Intentionally broad technical selector; catches cphol's zusammengesetzter.
    if "menge" in meaning.casefold(): out.append("LEXICAL_MENGE")
    return out

def build_selector(base: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    selected, audit = [], []
    for row in base:
        reasons = selector_reasons(row)
        if not reasons: continue
        selected.append(row); false = row["reading_id"] == FALSE_ID
        audit.append({"reading_id": row["reading_id"], "surface": row["surface"],
          "working_meaning_de": row["working_meaning_de"], "selector_reasons": "|".join(reasons),
          "occurrence_count": row["occurrence_count"],
          "classification": "LEXICAL_FALSE_POSITIVE" if false else "TRUE_AMBIGUITY_TARGET",
          "dispatch_allowed": int(not false),
          "explanation_de": ("menge steht nur als Buchstabenfolge in zusammengesetzter; kein Mengenlabel"
                             if false else "vorregistrierter technischer Ambiguitätsselektor erfüllt")})
    assert len(selected) == 95 and sum(int(r["occurrence_count"]) for r in selected) == 1050
    false = [r for r in selected if r["reading_id"] == FALSE_ID]
    assert len(false) == 1 and false[0]["working_meaning_de"] == "zusammengesetzter Drogenstoff"
    assert int(false[0]["occurrence_count"]) == 11
    return selected, audit

def build_dictionary(base: list[dict[str, str]], specs: list[dict[str, str]], targets: list[dict[str, str]]):
    assert len(base) == 1586 and len(specs) == len(targets) == 94
    by_id = {r["reading_id"]: r for r in specs}
    assert len(by_id) == 94 and set(by_id) == {r["reading_id"] for r in targets}
    output, audit = [], []
    for source in base:
        spec = by_id.get(source["reading_id"])
        if spec is None: output.append(dict(source)); continue
        assert source["surface"] == spec["surface"]
        assert source["working_meaning_de"] == spec["expected_old_meaning_de"]
        assert spec["new_meaning_de"] and spec["new_meaning_de"] != spec["expected_old_meaning_de"]
        assert spec["component_export_credit"] == "0" and spec["historical_confirmation"] == "H0_NONE"
        assert not selector_reasons({**source, "working_meaning_de": spec["new_meaning_de"]})
        row = dict(source)
        row["working_meaning_de"] = spec["new_meaning_de"]
        row["source_gdts"] = append_pipe(source["source_gdts"], "GDT730")
        row["relation_word_delta"] = "0_GDT696_TO_GDT730"
        row["v99_context_realizations_de"] = spec["new_meaning_de"]
        row["v99_audit_decision"] = f"GDT730_{spec['family']}_SINGLE_DEFAULT_DISPATCH"
        row["v99_evidence_class"] = "INHERITED_WHOLE_AMBIGUITY_DEFAULT_DISPATCH"
        row["v99_open_semantic_slots"] = spec["strongest_rival_de"]
        row["v99_lineage_class"] = "INHERITED_GLOBAL_V48__GDT730_SINGLE_DEFAULT_DISPATCH"
        row["v99_value_kind"] = spec["family"]
        changes = {k for k in source if source[k] != row[k]}
        assert changes == TARGET_CHANGE_FIELDS, (source["reading_id"], changes)
        assert not selector_reasons({**source, "working_meaning_de": row["v99_context_realizations_de"]})
        output.append(row)
        audit.append({**spec, "observed_occurrence_count": source["occurrence_count"],
          "observed_page_count": source["page_count"], "observed_locus_count": source["locus_count"],
          "working_model_score_0_100_not_probability": source["working_model_score_0_100_not_probability"],
          "working_model_level": source["working_model_level"], "semantic_scope": source["semantic_scope"],
          "source_gdts_before": source["source_gdts"], "source_gdts_after": row["source_gdts"],
          "changed_fields": "|".join(k for k in source if k in changes),
          "base_row_sha256": row_sha(source), "new_row_sha256": row_sha(row)})
    assert len(output) == 1586 and len(audit) == 94
    order = {r["reading_id"]: i for i, r in enumerate(specs)}
    audit.sort(key=lambda r: order[r["reading_id"]])
    return output, audit

def build_family_summary(audit: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups = defaultdict(list)
    for row in audit: groups[row["family"]].append(row)
    return [{"family": family, "target_rows": len(rows),
      "summed_occurrence_count": sum(int(r["observed_occurrence_count"]) for r in rows),
      "surfaces": "|".join(r["surface"] for r in rows),
      "confidence_levels": "|".join(sorted({r["working_model_level"] for r in rows})),
      "all_component_export_credit_zero": int(all(r["component_export_credit"] == "0" for r in rows)),
      "all_historical_confirmation_h0_none": int(all(r["historical_confirmation"] == "H0_NONE" for r in rows))}
      for family, rows in sorted(groups.items())]

def build_evidence(audit: list[dict[str, Any]], base_by_id: dict[str, dict[str, str]]) -> list[dict[str, Any]]:
    out = []
    for spec in audit:
        row = base_by_id[spec["reading_id"]]
        bundle = {k: row[k] for k in ("working_model_score_0_100_not_probability", "working_model_level",
          "positive_evidence_de", "counterevidence_de", "historical_confirmation",
          "historical_analogue", "semantic_scope", "global_export_scope", "unconditional_global_export_allowed",
          "v99_component_global_export_allowed", "bound_span_ids", "source_reading_ids", "v99_structural_tag",
          "v99_action_default_allowed")}
        out.append({"decision_id": spec["decision_id"], "reading_id": spec["reading_id"],
          "surface": spec["surface"], "family": spec["family"], "source_evidence": spec["source_evidence"],
          "decision_basis": spec["decision_basis"], "strongest_rival_de": spec["strongest_rival_de"],
          **bundle, "bundle_sha256": hashlib.sha256(json.dumps(bundle, ensure_ascii=False,
          sort_keys=True).encode()).hexdigest(), "all_preserved": 1, "component_relation_credit": 0})
    return out

def build_reader_parity() -> list[dict[str, Any]]:
    out = []
    for name in PARITY_INPUTS:
        path = G727 / name
        count = len(read_tsv(path)) if path.suffix == ".tsv" else sum(
            line.startswith("## ") for line in path.read_text(encoding="utf-8").splitlines())
        out.append({"source_artifact": str(path.relative_to(ROOT)), "row_or_section_count": count,
                    "sha256": file_sha(path), "gdt730_edits": 0,
                    "parity_status": "BYTE_STABLE_INPUT_NOT_REWRITTEN"})
    return out

def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    base, specs = read_tsv(BASE), read_tsv(SPECS)
    technical, selector_audit = build_selector(base)
    targets = [r for r in technical if r["reading_id"] != FALSE_ID]
    assert len(targets) == 94 and sum(int(r["occurrence_count"]) for r in targets) == 1039
    current, audit = build_dictionary(base, specs, targets)
    target_ids = {r["reading_id"] for r in targets}
    assert [r["reading_id"] for r in current] == [r["reading_id"] for r in base]
    assert [r["surface"] for r in current] == [r["surface"] for r in base]
    for before, after in zip(base, current, strict=True):
        changed = {k for k in before if before[k] != after[k]}
        assert changed == (TARGET_CHANGE_FIELDS if before["reading_id"] in target_ids else set())
    assert Counter(r["current_layer"] for r in current) == Counter(
        {"ACTIVE_V99_LEXICAL_CORE": 324, "GLOBAL_V48_DEFAULT": 1262})
    family = build_family_summary(audit); evidence = build_evidence(audit, {r["reading_id"]: r for r in base})
    parity = build_reader_parity()
    historical_composition = read_tsv(G631 / "HISTORICAL_COMPOSITION_COMPARATORS.tsv")
    historical_hybrid = read_tsv(G632 / "HISTORICAL_HYBRID_COMPARATORS.tsv")
    historical_quantity = read_tsv(G729 / "HISTORICAL_QUANTITY_COMPARATORS.tsv")
    assert all(r["historical_confirmation"] == "H0_NONE" and r["voynich_relation_credit"] == "0"
               for r in historical_quantity)
    # GDT631/632 are inherited byte-for-byte; their older schemas encode the
    # same ceiling in `limit`/`limit_de` rather than relation-credit columns.
    assert len(historical_composition) == 3 and len(historical_hybrid) == 2
    write_tsv(ART / "V99R4_COMPLETE_WORD_CONFIDENCE.tsv", current, list(base[0]))
    write_tsv(ART / "V99R4_94_AMBIGUITY_DEFAULT_AUDIT.tsv", audit)
    write_tsv(ART / "V99R4_FAMILY_SUMMARY.tsv", family)
    write_tsv(ART / "V99R4_SELECTOR_FALSE_POSITIVE_AUDIT.tsv", selector_audit)
    write_tsv(ART / "V99R4_ACTIVE_READER_PARITY.tsv", parity)
    write_tsv(ART / "V99R4_EVIDENCE_BINDINGS.tsv", evidence)
    write_tsv(ART / "HISTORICAL_COMPOSITION_COMPARATORS.tsv", historical_composition)
    write_tsv(ART / "HISTORICAL_HYBRID_COMPARATORS.tsv", historical_hybrid)
    write_tsv(ART / "HISTORICAL_QUANTITY_COMPARATORS.tsv", historical_quantity)
    result = {"experiment_id": "GDT730", "status": STATUS, "complete_dictionary_rows": 1586,
      "complete_dictionary_surfaces": len({r["surface"] for r in current}),
      "technical_selector_rows": 95, "technical_selector_summed_occurrences": 1050,
      "lexical_false_positive_rows": 1, "lexical_false_positive_occurrences": 11,
      "target_rows": 94, "target_summed_occurrences": 1039,
      "target_confidence_counts": dict(Counter(r["working_model_level"] for r in audit)),
      "family_count": len(family), "active_v99_rows_byte_stable": 324,
      "non_target_global_rows_byte_stable": 1168, "all_non_target_rows_byte_stable": 1492,
      "changed_fields": sorted(TARGET_CHANGE_FIELDS), "target_main_meanings_ambiguity_free": 94,
      "target_context_meanings_ambiguity_free": 94, "score_changes": 0, "confidence_level_changes": 0,
      "evidence_changes": 0, "scope_changes": 0, "export_changes": 0, "component_relation_credit": 0,
      "historical_comparator_artifacts": 3, "historical_comparator_relation_credit": 0,
      "historical_confirmation": "H0_NONE",
      "active_reader_artifacts_byte_stable": len(parity),
      "canonical_dictionary": "experiments/yolo/gdt730_v99r4_ninety_four_ambiguity_default_dispatch/artifacts/V99R4_COMPLETE_WORD_CONFIDENCE.tsv"}
    (ART / "RESULT.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True)); return 0

if __name__ == "__main__": raise SystemExit(main())
