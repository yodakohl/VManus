#!/usr/bin/env python3
"""Build V93 by separating two cold-result wholes from local product heads."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt720_v93_cold_result_whole_domain_repair"
SRC = EXP / "src"
ART = EXP / "artifacts"
G719 = ROOT / "experiments/yolo/gdt719_v92_three_result_whole_dy_rejection/artifacts"

SOURCE_LEXICAL = G719 / "V92_324_ACTIVE_LEXICAL_READINGS.tsv"
SOURCE_CONTEXT = G719 / "V92_479_CONTEXT_REALIZATIONS.tsv"
SOURCE_CENSUS = G719 / "V92_61_HELD_READING_AUDIT.tsv"
SOURCE_COMPLETE = G719 / "V92_COMPLETE_WORD_CONFIDENCE.tsv"
SOURCE_SPANS = G719 / "V92_2_BOUND_SPAN_RENDERER.tsv"
SOURCE_DIRECTIVES = G719 / "V92_2_ONE_SHOT_RENDER_DIRECTIVES.tsv"
SOURCE_F7R2 = G719 / "V92_8_F7R2_RENDERED_UNITS.tsv"
SPECS = SRC / "V93_2_AUDIT_SPECS.tsv"
BINDINGS = SRC / "V93_20_PRIMARY_EVIDENCE_BINDINGS.tsv"

HISTORICAL = "H0_NONE"
STATUS = (
    "PASS_V93_2_COLD_RESULT_WHOLES_REVISED__SHARED_COOLING_MORPHOLOGY_REJECTED__"
    "2_POSITIONS_2_PAGES__56_WEAK_READINGS_REMAIN__NO_SCORE_CREDIT__ALL_H0_NONE"
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


def compact(values: Iterable[str], empty: str = "NONE") -> str:
    output: list[str] = []
    for value in values:
        if value and value not in {"NONE", "0"} and value not in output:
            output.append(value)
    return "|".join(output) if output else empty


def append_pipe(value: str, addition: str) -> str:
    return compact([*split_pipe(value), addition])


def parse_assertions(value: str) -> dict[str, str]:
    output: dict[str, str] = {}
    for part in value.split(";"):
        if not part:
            continue
        field, expected = part.split("=", 1)
        assert field and field not in output
        output[field] = expected
    return output


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


def rename_v92(row: dict[str, str]) -> dict[str, Any]:
    return {key.replace("v92", "v93").replace("V92", "V93"): value for key, value in row.items()}


def resolve_bindings(bindings: list[dict[str, str]], specs: list[dict[str, str]]) -> list[dict[str, Any]]:
    spec_ids = {row["source_reading_id"] for row in specs}
    output: list[dict[str, Any]] = []
    for binding in bindings:
        assert binding["source_reading_id"] in spec_ids
        assert binding["score_credit_family_ids"] == "NONE"
        assert "f84" not in binding["evidence_path"].lower()
        selector = parse_assertions(binding["selector"])
        assertions = parse_assertions(binding["field_assertions"])
        assert all(not value.lower().startswith("f84") for value in selector.values())
        matches = [
            row for row in read_tsv(ROOT / binding["evidence_path"])
            if all(row.get(field) == expected for field, expected in selector.items())
        ]
        assert len(matches) == 1, (binding["binding_id"], len(matches))
        source = matches[0]
        for field, expected in assertions.items():
            assert source.get(field) == expected, (binding["binding_id"], field, source.get(field), expected)
        fingerprint = hashlib.sha256(
            json.dumps(source, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        output.append({
            **binding,
            "matched_row_fingerprint_sha256": fingerprint,
            "source_row_match": 1,
            "evidence_status": "BOUND_EXACT_PRIMARY_ROW",
            "historical_confirmation": HISTORICAL,
        })
    assert len(output) == 20
    assert Counter(row["source_reading_id"] for row in output) == Counter({"etyd#1": 8, "teeedy#1": 12})
    return output


def build_lexical(
    source_rows: list[dict[str, str]], specs: list[dict[str, str]]
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    specs_by_id = {row["source_reading_id"]: row for row in specs}
    output: list[dict[str, Any]] = []
    for source in source_rows:
        row = rename_v92(source)
        source_ids = split_pipe(source["source_reading_ids"])
        spec = specs_by_id.get(source_ids[0]) if len(source_ids) == 1 else None
        if spec:
            assert source["v92_lexical_core_de"] == spec["old_lexical_core_de"]
            base = int(source["working_model_score_0_100_not_probability"])
            delta = int(spec["score_delta_lexical_core"])
            assert delta == 0 and spec["family_ids"] == "NONE" and spec["score_credit_family_ids"] == "NONE"
            score = min(base + delta, int(spec["lexical_core_cap"]))
            context_score = min(score, int(spec["context_realization_cap"]))
            row.update({
                "v93_lexical_core_de": spec["v93_lexical_core_de"],
                "v93_context_realizations_de": spec["v93_context_realization_de"],
                "family_ids": spec["family_ids"],
                "decomposition": spec["decomposition"],
                "repair_modes": spec["repair_mode"],
                "resolved_debt_atoms": spec["resolved_debt_atom"],
                "last_semantic_writer": "GDT720",
                "base_score": base,
                "score_delta_lexical_core": delta,
                "lexical_core_cap": spec["lexical_core_cap"],
                "working_model_score_0_100_not_probability": score,
                "working_model_level": level(score),
                "context_realization_cap": spec["context_realization_cap"],
                "context_realization_score_0_100_not_probability": context_score,
                "context_realization_level": level(context_score),
                "source_gdts": append_pipe(source["source_gdts"], "GDT720"),
                "positive_evidence_de": (
                    "GDT720 trennt den portablen Kälte-/Ergebniskern vom lokalen Produktkopf: "
                    + spec["evidence_de"] + " || " + source["positive_evidence_de"]
                ),
                "counterevidence_de": (
                    "GDT720 Gegenbeleg: " + spec["counterevidence_de"]
                    + " || Historisch unbestaetigte Arbeitstheorie; keine Klartextidentifikation."
                ),
                "v93_audit_decision": "REVISE",
                "v93_evidence_class": spec["evidence_class"],
                "v93_open_semantic_slots": spec["open_semantic_slots"],
                "v93_component_global_export_allowed": "0",
                "v93_prior_lexical_core_de": source["v92_lexical_core_de"],
            })
        else:
            row.update({
                "v93_audit_decision": "NOT_IN_GDT720_TRANCHE",
                "v93_evidence_class": "INHERITED_V92",
                "v93_open_semantic_slots": "NOT_EVALUATED",
                "v93_component_global_export_allowed": "NOT_EVALUATED",
                "v93_prior_lexical_core_de": source["v92_lexical_core_de"],
            })
        output.append(row)
    assert len(output) == 324
    by_source: dict[str, dict[str, Any]] = {}
    for row in output:
        for source_id in split_pipe(str(row["source_reading_ids"])):
            assert source_id not in by_source
            by_source[source_id] = row
    assert len(by_source) == 332
    return output, by_source


def build_contexts(
    source_rows: list[dict[str, str]], specs: list[dict[str, str]], lexical_by_source: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    specs_by_id = {row["source_reading_id"]: row for row in specs}
    by_locus_ordinal = {(row["locus"], int(row["token_ordinal"])): row for row in source_rows}
    seen: Counter[str] = Counter()
    output: list[dict[str, Any]] = []
    for source in source_rows:
        source_id = source["source_reading_id"]
        lexical = lexical_by_source[source_id]
        spec = specs_by_id.get(source_id)
        row = rename_v92(source)
        if spec:
            seen[source_id] += 1
            assert (source["position_id"], source["page"], source["locus"], source["token_ordinal"]) == (
                spec["expected_position_id"], spec["expected_page"], spec["expected_locus"], spec["expected_token_ordinal"]
            )
            ordinal = int(source["token_ordinal"])
            left = "<BOS>" if ordinal == 1 else by_locus_ordinal[(source["locus"], ordinal - 1)]["surface"]
            assert left == spec["expected_left_surface"]
        row.update({
            "v93_reading_id": lexical["v93_reading_id"],
            "v93_lexical_core_de": lexical["v93_lexical_core_de"],
            "v93_context_realization_de": spec["v93_context_realization_de"] if spec else source["v92_context_realization_de"],
            "v93_repair_mode": spec["repair_mode"] if spec else source["v92_repair_mode"],
            "v93_resolved_debt_atom": spec["resolved_debt_atom"] if spec else source["v92_resolved_debt_atom"],
            "v93_lexical_score": lexical["working_model_score_0_100_not_probability"],
            "v93_lexical_level": lexical["working_model_level"],
            "v93_context_score": lexical["context_realization_score_0_100_not_probability"],
            "v93_context_level": lexical["context_realization_level"],
            "v93_semantic_scope": lexical["semantic_scope"],
            "v93_semantic_applicability": lexical["semantic_applicability"],
            "v93_global_export_scope": lexical["global_export_scope"],
            "v93_lexical_bound_span_ids": lexical["bound_span_ids"],
            "v93_unconditional_global_export_allowed": lexical["unconditional_global_export_allowed"],
            "v93_historical_confirmation": HISTORICAL,
            "v93_audit_decision": "REVISE" if spec else "NOT_IN_GDT720_TRANCHE",
            "v93_evidence_class": spec["evidence_class"] if spec else "INHERITED_V92",
            "v93_open_semantic_slots": spec["open_semantic_slots"] if spec else "NOT_EVALUATED",
            "v93_component_global_export_allowed": "0" if spec else "NOT_EVALUATED",
            "v93_local_context_hypothesis": spec["local_context_hypothesis"] if spec else "NONE",
            "v93_expected_left_surface": spec["expected_left_surface"] if spec else "NONE",
        })
        output.append(row)
    assert seen == Counter({"etyd#1": 1, "teeedy#1": 1})
    assert len(output) == 479
    return output


def build_census(
    source_rows: list[dict[str, str]], specs: list[dict[str, str]], lexical_by_source: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    specs_by_id = {row["source_reading_id"]: row for row in specs}
    output: list[dict[str, Any]] = []
    for source in source_rows:
        if source["disposition"] != "HELD_FOR_LATER_REPAIR":
            continue
        source_id = source["source_reading_id"]
        lexical = lexical_by_source[source_id]
        spec = specs_by_id.get(source_id)
        row = rename_v92(source)
        if spec:
            row.update({
                "disposition": "REVISED_IN_V93",
                "repair_mode": spec["repair_mode"],
                "resolved_debt_atom": spec["resolved_debt_atom"],
                "v93_reading_id": lexical["v93_reading_id"],
                "v93_lexical_core_de": lexical["v93_lexical_core_de"],
                "v93_context_realization_de": spec["v93_context_realization_de"],
                "new_lexical_score": lexical["working_model_score_0_100_not_probability"],
                "new_lexical_level": lexical["working_model_level"],
                "new_context_score": lexical["context_realization_score_0_100_not_probability"],
                "new_context_level": lexical["context_realization_level"],
                "positive_evidence_de": spec["evidence_de"],
                "counterevidence_de": spec["counterevidence_de"],
                "v93_audit_decision": "REVISE",
                "v93_evidence_class": spec["evidence_class"],
                "v93_open_semantic_slots": spec["open_semantic_slots"],
            })
        else:
            row.update({
                "v93_reading_id": lexical["v93_reading_id"],
                "v93_lexical_core_de": lexical["v93_lexical_core_de"],
                "v93_context_realization_de": lexical["v93_context_realizations_de"],
                "new_lexical_score": lexical["working_model_score_0_100_not_probability"],
                "new_lexical_level": lexical["working_model_level"],
                "new_context_score": lexical["context_realization_score_0_100_not_probability"],
                "new_context_level": lexical["context_realization_level"],
                "v93_audit_decision": "HELD_FOR_LATER_REPAIR",
                "v93_evidence_class": "INHERITED_V92",
                "v93_open_semantic_slots": "NOT_EVALUATED",
            })
        output.append(row)
    assert len(output) == 58
    assert Counter(row["disposition"] for row in output) == Counter({"HELD_FOR_LATER_REPAIR": 56, "REVISED_IN_V93": 2})
    return output


def build_delta(
    source_rows: list[dict[str, str]], specs: list[dict[str, str]], target_by_source: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    source_by_id = {source_id: row for row in source_rows for source_id in split_pipe(row["source_reading_ids"])}
    output: list[dict[str, Any]] = []
    for spec in specs:
        source = source_by_id[spec["source_reading_id"]]
        target = target_by_source[spec["source_reading_id"]]
        output.append({
            "source_reading_id": spec["source_reading_id"], "surface": source["surface"],
            "position_id": spec["expected_position_id"], "page": spec["expected_page"],
            "locus": spec["expected_locus"], "token_ordinal": spec["expected_token_ordinal"],
            "left_surface": spec["expected_left_surface"], "old_lexical_core_de": source["v92_lexical_core_de"],
            "v93_lexical_core_de": target["v93_lexical_core_de"],
            "v93_context_realization_de": spec["v93_context_realization_de"],
            "old_score": source["working_model_score_0_100_not_probability"],
            "v93_score": target["working_model_score_0_100_not_probability"],
            "old_level": source["working_model_level"], "v93_level": target["working_model_level"],
            "family_ids": spec["family_ids"], "score_credit_family_ids": spec["score_credit_family_ids"],
            "decomposition": spec["decomposition"], "repair_mode": spec["repair_mode"],
            "resolved_debt_atom": spec["resolved_debt_atom"], "evidence_class": spec["evidence_class"],
            "evidence_de": spec["evidence_de"], "counterevidence_de": spec["counterevidence_de"],
            "open_semantic_slots": spec["open_semantic_slots"],
            "local_context_hypothesis": spec["local_context_hypothesis"],
            "component_global_export_allowed": 0, "historical_confirmation": HISTORICAL,
        })
    return output


def build_domain_decision(specs: list[dict[str, str]]) -> list[dict[str, Any]]:
    return [{
        "comparison_id": "COLD_RESULT_DOMAIN_NO_SHARED_WRITTEN_FAMILY",
        "selected_source_reading_ids": compact(row["source_reading_id"] for row in specs),
        "selected_surfaces": compact(row["source_reading_id"].split("#", 1)[0] for row in specs),
        "shared_semantic_domain_de": "gekühltes abgeschlossenes Ergebnis",
        "semantic_domain_decision": "RETAIN_FOR_BOTH_WHOLE_DEFAULTS",
        "written_family_decision": "REJECT_SHARED_COOLING_OR_CLOSURE_MORPHOLOGY",
        "reason_de": "teeedy ist eine ungelöste wiederholte Ganzform ohne reale Schwester; etyd besitzt keine zugelassene Schwester- oder Binnenanalyse. Die gemeinsame deutsche Domäne ist kein gemeinsames Schriftsegment.",
        "score_credit_family_ids": "NONE", "score_delta": 0,
        "component_global_export_allowed": 0, "historical_confirmation": HISTORICAL,
    }]


def build_rivals() -> list[dict[str, Any]]:
    return [
        {"source_reading_id": "etyd#1", "surface": "etyd", "model_id": "COLD_RESULT", "candidate_default_de": "bis Mittelstufe gekühlt; abgeschlossen", "decision": "SELECT_PORTABLE_DEFAULT", "evidence_fit_de": "Zeilenfinal nach Grad III; STATE_COLD|STATE_FINISHED|VALUE_GRADE; nominal.", "conflict_de": "Produkttyp und Binnenstruktur bleiben offen.", "portable_default_selected": 1, "score_credit": 0},
        {"source_reading_id": "etyd#1", "surface": "etyd", "model_id": "DOSE_HANDOFF", "candidate_default_de": "abgemessene Gabe für den nächsten Arbeitsgang", "decision": "REJECT_AS_DEFAULT", "evidence_fit_de": "Die alte Sidequest-Lesung erklärt die Zeilengrenze als Übergabe.", "conflict_de": "daiin trägt bereits den benachbarten Grad-/Maßwert; etyd ist nicht aktionslizenziert.", "portable_default_selected": 0, "score_credit": 0},
        {"source_reading_id": "etyd#1", "surface": "etyd", "model_id": "RESIDUE_REST", "candidate_default_de": "gekühlter Rest oder Rückstand", "decision": "KEEP_LOCAL_RIVAL_ONLY", "evidence_fit_de": "Ein zeilenfinales nominales Ergebnis kann ein Restgut sein.", "conflict_de": "Kein eigenes Rückstands-, Zeit- oder Ruhe-Signal.", "portable_default_selected": 0, "score_credit": 0},
        {"source_reading_id": "teeedy#1", "surface": "teeedy", "model_id": "COLD_RESULT", "candidate_default_de": "vollständig abgekühlt; abgeschlossen", "decision": "SELECT_PORTABLE_DEFAULT", "evidence_fit_de": "Vier Oberflächenvorkommen; exakte STATE_COLD|STATE_FINISHED-Linie; nominales Resultat.", "conflict_de": "Wiederholung beweist keine Binnenzerlegung oder Produktidentität.", "portable_default_selected": 1, "score_credit": 0},
        {"source_reading_id": "teeedy#1", "surface": "teeedy", "model_id": "DOSE_HANDOFF", "candidate_default_de": "abgekühlte Übergabeportion", "decision": "REJECT_AS_DEFAULT", "evidence_fit_de": "Die mediale Stellung vor einer Portionskarte erlaubt einen Übergabekontext.", "conflict_de": "oroiir trägt rechts bereits die Portion; teeedy selbst ist ein nominaler Zustandsblock.", "portable_default_selected": 0, "score_credit": 0},
        {"source_reading_id": "teeedy#1", "surface": "teeedy", "model_id": "RESIDUE_REST", "candidate_default_de": "vollständig abgekühlter Rückstand", "decision": "KEEP_LOCAL_RIVAL_ONLY", "evidence_fit_de": "Ein abgekühltes Zwischenprodukt kann lokal Rückstand oder Vorrat sein.", "conflict_de": "GDT691 nennt nur Auszug|Absud als offene Produktrivalen; kein Rückstandssignal.", "portable_default_selected": 0, "score_credit": 0},
    ]


def build_complete(source_rows: list[dict[str, str]], lexical: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for source in source_rows:
        if source["current_layer"] == "ACTIVE_V92_LEXICAL_CORE":
            continue
        row = rename_v92(source)
        row.update({
            "v93_audit_decision": "OUTSIDE_ACTIVE_V93_TRANCHE",
            "v93_evidence_class": "INHERITED_GLOBAL_V48",
            "v93_open_semantic_slots": "NOT_EVALUATED",
            "v93_component_global_export_allowed": "NOT_EVALUATED",
        })
        output.append(row)
    for row in lexical:
        output.append({
            "surface": row["surface"], "reading_id": row["v93_reading_id"],
            "working_meaning_de": row["v93_lexical_core_de"], "current_layer": "ACTIVE_V93_LEXICAL_CORE",
            "semantic_scope": row["semantic_scope"], "semantic_applicability": row["semantic_applicability"],
            "form_level": row["form_level"], "occurrence_count": row["occurrence_count"],
            "page_count": row["page_count"], "locus_count": row["locus_count"],
            "working_model_score_0_100_not_probability": row["working_model_score_0_100_not_probability"],
            "working_model_level": row["working_model_level"], "source_gdts": row["source_gdts"],
            "positive_evidence_de": row["positive_evidence_de"], "counterevidence_de": row["counterevidence_de"],
            "historical_confirmation": row["historical_confirmation"], "historical_analogue": row["historical_analogue"],
            "relation_word_delta": row["relation_word_delta"], "global_export_scope": row["global_export_scope"],
            "bound_span_ids": row["bound_span_ids"],
            "unconditional_global_export_allowed": row["unconditional_global_export_allowed"],
            "v93_context_realizations_de": row["v93_context_realizations_de"],
            "source_reading_ids": row["source_reading_ids"], "v93_audit_decision": row["v93_audit_decision"],
            "v93_evidence_class": row["v93_evidence_class"],
            "v93_open_semantic_slots": row["v93_open_semantic_slots"],
            "v93_component_global_export_allowed": row["v93_component_global_export_allowed"],
        })
    return sorted(output, key=lambda row: (str(row["surface"]), str(row["reading_id"])))


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    specs = read_tsv(SPECS)
    bindings = read_tsv(BINDINGS)
    assert len(specs) == 2 and {row["source_reading_id"] for row in specs} == {"etyd#1", "teeedy#1"}
    assert all(row["component_global_export_allowed"] == "0" for row in specs)
    assert all(row["score_delta_lexical_core"] == "0" for row in specs)

    source_lexical = read_tsv(SOURCE_LEXICAL)
    source_context = read_tsv(SOURCE_CONTEXT)
    source_census = read_tsv(SOURCE_CENSUS)
    source_complete = read_tsv(SOURCE_COMPLETE)
    evidence = resolve_bindings(bindings, specs)
    lexical, lexical_by_source = build_lexical(source_lexical, specs)
    contexts = build_contexts(source_context, specs, lexical_by_source)
    census = build_census(source_census, specs, lexical_by_source)
    delta = build_delta(source_lexical, specs, lexical_by_source)
    domain = build_domain_decision(specs)
    rivals = build_rivals()
    complete = build_complete(source_complete, lexical)

    write_tsv(ART / "V93_324_ACTIVE_LEXICAL_READINGS.tsv", lexical)
    write_tsv(ART / "V93_479_CONTEXT_REALIZATIONS.tsv", contexts)
    write_tsv(ART / "V93_58_HELD_READING_AUDIT.tsv", census)
    write_tsv(ART / "V93_2_COLD_RESULT_CORE_CONTEXT_DELTA.tsv", delta)
    write_tsv(ART / "V93_1_REJECTED_SHARED_COOLING_MORPHOLOGY.tsv", domain)
    write_tsv(ART / "V93_6_RIVAL_MODEL_COMPARISON.tsv", rivals)
    write_tsv(ART / "V93_20_PRIMARY_EVIDENCE_BINDINGS.tsv", evidence)
    write_tsv(ART / "V93_COMPLETE_WORD_CONFIDENCE.tsv", complete)
    shutil.copyfile(SOURCE_SPANS, ART / "V93_2_BOUND_SPAN_RENDERER.tsv")
    shutil.copyfile(SOURCE_DIRECTIVES, ART / "V93_2_ONE_SHOT_RENDER_DIRECTIVES.tsv")
    shutil.copyfile(SOURCE_F7R2, ART / "V93_8_F7R2_RENDERED_UNITS.tsv")

    levels = Counter(row["working_model_level"] for row in lexical)
    assert levels == Counter({
        "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY": 7,
        "W1_WEAK_WORKING": 135,
        "W2_PROVISIONAL_WORKING": 163,
        "W3_SOLID_WORKING_THEORY": 19,
    })
    assert len(complete) == 1586 and len({row["surface"] for row in complete}) == 1582
    assert all(row["working_meaning_de"] for row in complete)
    assert all(row["positive_evidence_de"] and row["counterevidence_de"] for row in complete)
    assert all(row["historical_confirmation"] == HISTORICAL for row in complete)

    result = {
        "experiment_id": "GDT720", "status": STATUS, "target_readings": 2,
        "target_positions": 2, "target_pages": 2, "primary_evidence_bindings": len(evidence),
        "rival_model_rows": len(rivals), "shared_semantic_domains_retained": 1,
        "shared_written_families_accepted": 0, "score_credit_families": 0,
        "score_delta_total": 0, "component_global_exports": 0,
        "active_lexical_rows": len(lexical), "active_source_readings": len(lexical_by_source),
        "context_positions": len(contexts), "non_target_lexical_rows_preserved": len(lexical) - 2,
        "non_target_context_positions_preserved": len(contexts) - 2,
        "remaining_unreviewed_weak_readings": 56, "confidence_levels": dict(sorted(levels.items())),
        "complete_dictionary_rows": len(complete),
        "complete_dictionary_surfaces": len({row["surface"] for row in complete}),
        "complete_dictionary_rows_with_default_confidence_and_evidence": sum(
            bool(row["working_meaning_de"] and row["working_model_level"] and row["positive_evidence_de"] and row["counterevidence_de"])
            for row in complete
        ),
        "bound_spans_preserved": len(read_tsv(SOURCE_SPANS)),
        "f7r2_output_units": len(read_tsv(SOURCE_F7R2)), "f84_or_f84r_used": 0,
        "historical_confirmation": HISTORICAL,
        "canonical_dictionary": "experiments/yolo/gdt720_v93_cold_result_whole_domain_repair/artifacts/V93_COMPLETE_WORD_CONFIDENCE.tsv",
    }
    (ART / "RESULT.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
