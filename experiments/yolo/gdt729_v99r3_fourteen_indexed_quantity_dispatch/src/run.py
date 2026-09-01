#!/usr/bin/env python3
"""Build V99R3 by resolving fourteen inherited quantity/value whole readings."""

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
EXP = ROOT / "experiments/yolo/gdt729_v99r3_fourteen_indexed_quantity_dispatch"
SRC, ART = EXP / "src", EXP / "artifacts"
G627 = ROOT / "experiments/yolo/gdt627_value_head_role_atlas"
G661 = ROOT / "experiments/yolo/gdt661_forty_eight_residual_family_completion"
G663 = ROOT / "experiments/yolo/gdt663_one_hundred_two_residual_family_completion"
G665 = ROOT / "experiments/yolo/gdt665_one_hundred_forty_eight_residual_family_completion"
G686 = ROOT / "experiments/yolo/gdt686_v59_dain_daiin_qodaiin_value_head_dispatch"
G693 = ROOT / "experiments/yolo/gdt693_ar_head_semantic_tournament"
G727 = ROOT / "experiments/yolo/gdt727_v99_six_meaning_debt_dispatch/artifacts"
G728 = ROOT / "experiments/yolo/gdt728_v99r2_inherited_unit_term_dispatch"
BASE = G728 / "artifacts/V99R2_COMPLETE_WORD_CONFIDENCE.tsv"
SPECS = SRC / "V99R3_14_QUANTITY_DISPATCH_SPECS.tsv"
HISTORICAL = G728 / "artifacts/HISTORICAL_QUANTITY_COMPARATORS.tsv"
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


def build_dictionary(base: list[dict[str, str]], specs: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    assert len(base) == 1586 and len(specs) == 14
    assert tuple(row["surface"] for row in specs) == TARGET_SURFACES
    assert Counter(row["dispatch_class"] for row in specs) == EXPECTED_DISPATCH
    spec_by_id = {row["reading_id"]: row for row in specs}
    assert len(spec_by_id) == 14
    base_by_id = {row["reading_id"]: row for row in base}
    assert set(spec_by_id) <= set(base_by_id)

    output: list[dict[str, str]] = []
    audit: list[dict[str, Any]] = []
    for source in base:
        spec = spec_by_id.get(source["reading_id"])
        if spec is None:
            output.append(dict(source))
            continue
        assert source["surface"] == spec["surface"]
        assert source["current_layer"] == "GLOBAL_V48_DEFAULT"
        assert source["working_meaning_de"] == source["v99_context_realizations_de"] == spec["expected_old_meaning_de"]
        assert spec["dispatch_class"] in DISPATCH_CLASSES
        assert spec["component_export_credit"] == "0"
        assert spec["historical_confirmation"] == "H0_NONE"
        assert "/" not in spec["new_meaning_de"]

        row = dict(source)
        row["working_meaning_de"] = spec["new_meaning_de"]
        row["source_gdts"] = append_pipe(source["source_gdts"], "GDT729")
        row["relation_word_delta"] = "0_GDT696_TO_GDT729"
        row["v99_context_realizations_de"] = spec["new_meaning_de"]
        row["v99_audit_decision"] = f"GDT729_{spec['dispatch_class']}_SCOPED_WHOLE_DISPATCH"
        row["v99_evidence_class"] = "SCOPED_HEAD_VALUE_WHOLE_DISPATCH"
        row["v99_open_semantic_slots"] = spec["open_slot_de"]
        row["v99_lineage_class"] = "INHERITED_GLOBAL_V48__GDT729_QUANTITY_VALUE_DISPATCH"
        row["v99_value_kind"] = spec["dispatch_class"]
        changes = {field for field in source if source[field] != row[field]}
        assert changes == ALLOWED_TARGET_CHANGES, (source["reading_id"], changes)
        output.append(row)
        audit.append({
            **spec,
            "observed_occurrence_count": source["occurrence_count"],
            "observed_page_count": source["page_count"],
            "observed_locus_count": source["locus_count"],
            "working_model_score_0_100_not_probability": source["working_model_score_0_100_not_probability"],
            "working_model_level": source["working_model_level"],
            "semantic_scope": source["semantic_scope"],
            "unconditional_global_export_allowed": source["unconditional_global_export_allowed"],
            "source_gdts_before": source["source_gdts"],
            "changed_fields": "|".join(field for field in source if field in changes),
            "score_level_evidence_scope_export_unchanged": 1,
            "base_row_sha256": row_sha(source),
            "new_row_sha256": row_sha(row),
            "positive_evidence_sha256": hashlib.sha256(source["positive_evidence_de"].encode()).hexdigest(),
            "counterevidence_sha256": hashlib.sha256(source["counterevidence_de"].encode()).hexdigest(),
        })
    assert len(output) == 1586 and len(audit) == 14
    decision_order = {row["decision_id"]: index for index, row in enumerate(specs)}
    audit.sort(key=lambda row: decision_order[row["decision_id"]])
    return output, audit


def build_dispatch_summary(audit: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in audit:
        grouped[row["dispatch_class"]].append(row)
    output: list[dict[str, Any]] = []
    for dispatch_class in DISPATCH_CLASSES:
        members = grouped.get(dispatch_class, [])
        output.append({
            "dispatch_class": dispatch_class,
            "target_rows": len(members),
            "summed_occurrence_count": sum(int(row["observed_occurrence_count"]) for row in members),
            "exact_surfaces": "|".join(row["surface"] for row in members) or "NONE",
            "head_roles": "|".join(sorted({row["head_role"] for row in members})) or "NONE",
            "all_component_export_credit_zero": int(all(row["component_export_credit"] == "0" for row in members)),
            "all_historical_confirmation_h0_none": int(all(row["historical_confirmation"] == "H0_NONE" for row in members)),
        })
    return output


def build_head_evidence() -> list[dict[str, Any]]:
    atlas = read_tsv(G627 / "artifacts/HEAD_ROLE_ATLAS.tsv")
    by_head = {row["head"]: row for row in atlas}
    family663 = read_tsv(G663 / "artifacts/FAMILY_COMPOSITION_ATLAS.tsv")
    by_surface663 = {row["surface"]: row for row in family663}
    accepted665 = read_tsv(G665 / "artifacts/ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv")
    by_surface665 = {row["surface"]: row for row in accepted665}
    tdain = next(row for row in read_tsv(G661 / "artifacts/ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv") if row["surface"] == "tdain")
    report627 = (G627 / "REPORT.md").read_text(encoding="utf-8")
    report686 = (G686 / "REPORT.md").read_text(encoding="utf-8")
    report693 = (G693 / "REPORT.md").read_text(encoding="utf-8")
    assert by_head["ctha"]["role"] == by_head["chora"]["role"] == "PLANT_PART_VALUE"
    assert "Those compounds may encode amount, pharmacological strength, size, maturity" in report627
    assert "head-dependent grade, amount or batch" in report693
    assert "kein universelles `Grad III`" in report686
    assert by_surface665["arain"]["strongest_rival_de"] == "zwei Teile der ersten Drogenfraktion"
    assert {by_surface663[s]["working_default_de"] for s in ("olain", "olaiin")} == {"Drogenstoff, Menge II", "Drogenstoff, Menge III"}
    assert tdain["strength"] == "LOW_EXPLORATORY"
    return [
        {"evidence_id": "G729-E01", "source": "GDT627:HEAD_ROLE_ATLAS:ctha", "observed_form_or_family": "ctha", "observed_role": by_head["ctha"]["role"], "observed_count": by_head["ctha"]["occurrences"], "dispatch_supported": "OPEN_VALUE", "use_de": "CTH hält Blattgut und Index sichtbar", "restriction_de": "keine globale Mengen-, Reife-, Stärke- oder Klassenachse ausgewählt", "relation_credit": 0},
        {"evidence_id": "G729-E02", "source": "GDT627:HEAD_ROLE_ATLAS:chora", "observed_form_or_family": "chora", "observed_role": by_head["chora"]["role"], "observed_count": by_head["chora"]["occurrences"], "dispatch_supported": "OPEN_VALUE", "use_de": "CHOR hält Blütenteil und Index sichtbar", "restriction_de": "keine globale Organanzahl oder Sachachse ausgewählt", "relation_credit": 0},
        {"evidence_id": "G729-E03", "source": "GDT686:HEAD_DEPENDENT_AXIS", "observed_form_or_family": "dan|dain|daiin|daiiin", "observed_role": "D_VALUE_OUTER_HEAD_OPEN", "observed_count": 948, "dispatch_supported": "OPEN_VALUE", "use_de": "nackte D-Form nennt nur die Wertstufe", "restriction_de": "lokaler sichtbarer Kopf darf Grad oder Menge wählen; kein universelles Maß", "relation_credit": 0},
        {"evidence_id": "G729-E04", "source": "GDT665:ACCEPTED_WHOLE_SURFACE_DEFAULTS:arain", "observed_form_or_family": "arain", "observed_role": "AR_FRACTION_I+AIN_II", "observed_count": by_surface665["arain"]["occurrences"], "dispatch_supported": "INDEXED_SHARE_AMOUNT", "use_de": "Quellrival schreibt zwei Teile der ersten Fraktion aus", "restriction_de": "AR und AIN erhalten keinen freien Komponentenexport", "relation_credit": 0},
        {"evidence_id": "G729-E05", "source": "GDT663:FAMILY_COMPOSITION_ATLAS:olain|olaiin", "observed_form_or_family": "olain|olaiin", "observed_role": "OL_BASE+A+II/III", "observed_count": int(by_surface663["olain"]["occurrences"]) + int(by_surface663["olaiin"]["occurrences"]), "dispatch_supported": "CARDINAL_AMOUNT", "use_de": "gelernte Stoffganzformen tragen II/III als praktische Teilezahl", "restriction_de": "absolute Einheit und freie OL/AIN/AIIN-Werte bleiben offen", "relation_credit": 0},
        {"evidence_id": "G729-E06", "source": "GDT693:AR_OR_HEAD_SEMANTIC_TOURNAMENT", "observed_form_or_family": "OR", "observed_role": "DIVIDED_PORTION_HEAD", "observed_count": 10, "dispatch_supported": "CARDINAL_AMOUNT", "use_de": "OR bleibt Portion im R/OR-Kontrast", "restriction_de": "keine freie OR- oder AIIN-Bedeutung außerhalb gelernter Ganzformen", "relation_credit": 0},
        {"evidence_id": "G729-E07", "source": "GDT663:FAMILY_COMPOSITION_ATLAS:qoraiin", "observed_form_or_family": "qoraiin", "observed_role": by_surface663["qoraiin"]["card_type"], "observed_count": by_surface663["qoraiin"]["occurrences"], "dispatch_supported": "CARDINAL_AMOUNT", "use_de": "Handlung, Patient und Menge werden einmal in der Ganzform realisiert", "restriction_de": "Singleton und Drogenidentität bleiben schwach", "relation_credit": 0},
        {"evidence_id": "G729-E08", "source": "GDT663:FAMILY_COMPOSITION_ATLAS:solaiin", "observed_form_or_family": "solaiin", "observed_role": by_surface663["solaiin"]["card_type"], "observed_count": by_surface663["solaiin"]["occurrences"], "dispatch_supported": "CARDINAL_AMOUNT", "use_de": "Salz-Default plus drei Teile wird als drei Portionen ausgesprochen", "restriction_de": "Saatgut, Charge III bleibt gleichstarker Singleton-Rivale", "relation_credit": 0},
        {"evidence_id": "G729-E09", "source": "GDT661:ACCEPTED_WHOLE_SURFACE_DEFAULTS:tdain", "observed_form_or_family": "tdain", "observed_role": "T_COLD+D_VALUE_II", "observed_count": tdain["occurrences"], "dispatch_supported": "QUALITY_GRADE", "use_de": "sichtbarer Kältekopf wählt Grad II", "restriction_de": "LOW_EXPLORATORY; Score und Confidence bleiben unverändert", "relation_credit": 0},
    ]


def build_parity() -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for name in PARITY_INPUTS:
        path = G727 / name
        row_count = len(read_tsv(path)) if path.suffix == ".tsv" else sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.startswith("## "))
        output.append({
            "source_artifact": str(path.relative_to(ROOT)),
            "row_or_section_count": row_count,
            "sha256": file_sha(path),
            "gdt729_semantic_edits": 0,
            "parity_status": "BYTE_STABLE_INPUT_NOT_REWRITTEN",
        })
    return output


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    base = read_tsv(BASE)
    specs = read_tsv(SPECS)
    historical = read_tsv(HISTORICAL)
    current, audit = build_dictionary(base, specs)
    summary = build_dispatch_summary(audit)
    evidence = build_head_evidence()
    parity = build_parity()
    assert sum(int(row["observed_occurrence_count"]) for row in audit) == 140
    assert Counter(row["semantic_scope"] for row in audit) == Counter({"KNOWN_EXACT_WHOLE": 7, "KNOWN_CONTEXT_LICENSED": 7})
    assert Counter(row["working_model_level"] for row in audit) == Counter({"W3_SOLID_WORKING_THEORY": 4, "W2_PROVISIONAL_WORKING": 7, "W1_WEAK_WORKING": 2, "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY": 1})
    assert len(historical) == 5 and all(row["voynich_relation_credit"] == "0" and row["historical_confirmation"] == "H0_NONE" for row in historical)
    assert Counter(row["current_layer"] for row in current) == Counter({"ACTIVE_V99_LEXICAL_CORE": 324, "GLOBAL_V48_DEFAULT": 1262})

    write_tsv(ART / "V99R3_COMPLETE_WORD_CONFIDENCE.tsv", current, list(base[0]))
    write_tsv(ART / "V99R3_14_QUANTITY_DISPATCH_AUDIT.tsv", audit)
    write_tsv(ART / "V99R3_DISPATCH_SUMMARY.tsv", summary)
    write_tsv(ART / "V99R3_9_HEAD_RULE_EVIDENCE.tsv", evidence)
    write_tsv(ART / "HISTORICAL_QUANTITY_COMPARATORS.tsv", historical)
    write_tsv(ART / "V99R3_ACTIVE_READER_PARITY.tsv", parity)
    counts = Counter(row["dispatch_class"] for row in specs)
    result = {
        "experiment_id": "GDT729", "status": STATUS,
        "complete_dictionary_rows": 1586, "complete_dictionary_surfaces": 1582,
        "target_rows": 14, "target_summed_occurrences": 140,
        "target_scope_counts": dict(Counter(row["semantic_scope"] for row in audit)),
        "target_confidence_counts": dict(Counter(row["working_model_level"] for row in audit)),
        "dispatch_counts": {key: counts.get(key, 0) for key in DISPATCH_CLASSES},
        "slash_ambiguity_in_target_meanings": 0,
        "active_v99_rows_byte_stable": 324, "non_target_global_rows_byte_stable": 1248,
        "score_changes": 0, "confidence_level_changes": 0, "evidence_changes": 0,
        "scope_changes": 0, "export_changes": 0, "component_relation_credit": 0,
        "historical_comparators": 5, "historical_confirmation": "H0_NONE",
        "active_reader_artifacts_byte_stable": len(parity),
        "canonical_dictionary": "experiments/yolo/gdt729_v99r3_fourteen_indexed_quantity_dispatch/artifacts/V99R3_COMPLETE_WORD_CONFIDENCE.tsv",
    }
    (ART / "RESULT.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
