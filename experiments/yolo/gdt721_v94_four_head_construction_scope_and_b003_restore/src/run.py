#!/usr/bin/env python3
"""Build V94 by repairing the four-head construction scope and legacy spans."""

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
EXP = ROOT / "experiments/yolo/gdt721_v94_four_head_construction_scope_and_b003_restore"
SRC = EXP / "src"
ART = EXP / "artifacts"
G720 = ROOT / "experiments/yolo/gdt720_v93_cold_result_whole_domain_repair/artifacts"

SOURCE_LEXICAL = G720 / "V93_324_ACTIVE_LEXICAL_READINGS.tsv"
SOURCE_CONTEXT = G720 / "V93_479_CONTEXT_REALIZATIONS.tsv"
SOURCE_CENSUS = G720 / "V93_58_HELD_READING_AUDIT.tsv"
SOURCE_COMPLETE = G720 / "V93_COMPLETE_WORD_CONFIDENCE.tsv"
SOURCE_SPANS = G720 / "V93_2_BOUND_SPAN_RENDERER.tsv"
SOURCE_DIRECTIVES = G720 / "V93_2_ONE_SHOT_RENDER_DIRECTIVES.tsv"
SOURCE_F7R2 = G720 / "V93_8_F7R2_RENDERED_UNITS.tsv"
LEGACY_SPANS = ROOT / "experiments/yolo/gdt695_fixed_v67_clause_realization/artifacts/V68_3_BOUND_SPAN_FREEZE.tsv"
SPECS = SRC / "V94_4_AUDIT_SPECS.tsv"
BINDINGS = SRC / "V94_30_PRIMARY_EVIDENCE_BINDINGS.tsv"

HISTORICAL = "H0_NONE"
STATUS = (
    "PASS_V94_4_HEAD_READINGS_REPAIRED__POL_POWDER_MATERIAL__LOR_WOOD_PORTION__"
    "L_R_ACTIVE_OCCURRENCES_BOUND__3_LEGACY_SPANS_RESTORED__52_WEAK_READINGS_REMAIN__"
    "NO_SCORE_CREDIT__ALL_H0_NONE"
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


def rename_v93(row: dict[str, str]) -> dict[str, Any]:
    return {key.replace("v93", "v94").replace("V93", "V94"): value for key, value in row.items()}


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
    assert len(output) == 30
    assert Counter(row["source_reading_id"] for row in output) == Counter({
        "pol#1": 8, "lor#1": 10, "l#1": 6, "r#1": 6,
    })
    return output


def build_lexical(
    source_rows: list[dict[str, str]], specs: list[dict[str, str]]
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    specs_by_id = {row["source_reading_id"]: row for row in specs}
    output: list[dict[str, Any]] = []
    for source in source_rows:
        row = rename_v93(source)
        source_ids = split_pipe(source["source_reading_ids"])
        spec = specs_by_id.get(source_ids[0]) if len(source_ids) == 1 else None
        if spec:
            assert source["v93_lexical_core_de"] == spec["old_lexical_core_de"]
            base = int(source["working_model_score_0_100_not_probability"])
            delta = int(spec["score_delta_lexical_core"])
            assert delta == 0 and spec["score_credit_family_ids"] == "NONE"
            score = min(base + delta, int(spec["lexical_core_cap"]))
            context_score = min(score, int(spec["context_realization_cap"]))
            row.update({
                "v94_lexical_core_de": spec["v94_lexical_core_de"],
                "v94_context_realizations_de": spec["v94_context_realization_de"],
                "family_ids": spec["family_ids"],
                "decomposition": spec["decomposition"],
                "semantic_scope": spec["target_semantic_scope"],
                "semantic_applicability": spec["target_semantic_applicability"],
                "global_export_scope": spec["target_global_export_scope"],
                "bound_span_ids": spec["target_bound_span_ids"],
                "unconditional_global_export_allowed": spec["target_unconditional_global_export_allowed"],
                "repair_modes": spec["repair_mode"],
                "resolved_debt_atoms": spec["resolved_debt_atom"],
                "last_semantic_writer": "GDT721",
                "base_score": base,
                "score_delta_lexical_core": delta,
                "lexical_core_cap": spec["lexical_core_cap"],
                "working_model_score_0_100_not_probability": score,
                "working_model_level": level(score),
                "context_realization_cap": spec["context_realization_cap"],
                "context_realization_score_0_100_not_probability": context_score,
                "context_realization_level": level(context_score),
                "source_gdts": append_pipe(source["source_gdts"], "GDT721"),
                "positive_evidence_de": (
                    "GDT721 bindet den konkreten Vier-Kopf-Wert an seine zulässige Konstruktion: "
                    + spec["evidence_de"] + " || " + source["positive_evidence_de"]
                ),
                "counterevidence_de": (
                    "GDT721 Gegenbeleg und Grenze: " + spec["counterevidence_de"]
                    + " || Historisch unbestaetigte Arbeitstheorie; keine Klartextidentifikation."
                ),
                "v94_audit_decision": "REVISE",
                "v94_evidence_class": spec["evidence_class"],
                "v94_open_semantic_slots": spec["open_semantic_slots"],
                "v94_component_global_export_allowed": "0",
                "v94_prior_lexical_core_de": source["v93_lexical_core_de"],
            })
        else:
            row.update({
                "v94_audit_decision": "NOT_IN_GDT721_TRANCHE",
                "v94_evidence_class": "INHERITED_V93",
                "v94_open_semantic_slots": "NOT_EVALUATED",
                "v94_component_global_export_allowed": "NOT_EVALUATED",
                "v94_prior_lexical_core_de": source["v93_lexical_core_de"],
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
        row = rename_v93(source)
        if spec:
            seen[source_id] += 1
            assert (source["position_id"], source["page"], source["locus"], source["token_ordinal"]) == (
                spec["expected_position_id"], spec["expected_page"], spec["expected_locus"], spec["expected_token_ordinal"]
            )
            ordinal = int(source["token_ordinal"])
            left = "<BOS>" if ordinal == 1 else by_locus_ordinal[(source["locus"], ordinal - 1)]["surface"]
            assert left == spec["expected_left_surface"]
        row.update({
            "v94_reading_id": lexical["v94_reading_id"],
            "v94_lexical_core_de": lexical["v94_lexical_core_de"],
            "v94_context_realization_de": spec["v94_context_realization_de"] if spec else source["v93_context_realization_de"],
            "v94_repair_mode": spec["repair_mode"] if spec else source["v93_repair_mode"],
            "v94_resolved_debt_atom": spec["resolved_debt_atom"] if spec else source["v93_resolved_debt_atom"],
            "v94_lexical_score": lexical["working_model_score_0_100_not_probability"],
            "v94_lexical_level": lexical["working_model_level"],
            "v94_context_score": lexical["context_realization_score_0_100_not_probability"],
            "v94_context_level": lexical["context_realization_level"],
            "v94_semantic_scope": lexical["semantic_scope"],
            "v94_semantic_applicability": lexical["semantic_applicability"],
            "v94_global_export_scope": lexical["global_export_scope"],
            "v94_lexical_bound_span_ids": lexical["bound_span_ids"],
            "v94_unconditional_global_export_allowed": lexical["unconditional_global_export_allowed"],
            "v94_occurrence_bound_span_id": spec["occurrence_bound_span_id"] if spec else source["v93_occurrence_bound_span_id"],
            "v94_occurrence_bound_span_role": spec["occurrence_bound_span_role"] if spec else source["v93_occurrence_bound_span_role"],
            "v94_occurrence_bound_span_global_export_allowed": spec["occurrence_bound_span_global_export_allowed"] if spec else source["v93_occurrence_bound_span_global_export_allowed"],
            "v94_historical_confirmation": HISTORICAL,
            "v94_audit_decision": "REVISE" if spec else "NOT_IN_GDT721_TRANCHE",
            "v94_evidence_class": spec["evidence_class"] if spec else "INHERITED_V93",
            "v94_open_semantic_slots": spec["open_semantic_slots"] if spec else "NOT_EVALUATED",
            "v94_component_global_export_allowed": "0" if spec else "NOT_EVALUATED",
            "v94_local_context_hypothesis": spec["local_context_hypothesis"] if spec else "NONE",
            "v94_expected_left_surface": spec["expected_left_surface"] if spec else "NONE",
        })
        output.append(row)
    assert seen == Counter({"pol#1": 1, "lor#1": 1, "l#1": 1, "r#1": 1})
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
        row = rename_v93(source)
        if spec:
            row.update({
                "disposition": "REVISED_IN_V94",
                "repair_mode": spec["repair_mode"],
                "resolved_debt_atom": spec["resolved_debt_atom"],
                "v94_reading_id": lexical["v94_reading_id"],
                "v94_lexical_core_de": lexical["v94_lexical_core_de"],
                "v94_context_realization_de": spec["v94_context_realization_de"],
                "new_lexical_score": lexical["working_model_score_0_100_not_probability"],
                "new_lexical_level": lexical["working_model_level"],
                "new_context_score": lexical["context_realization_score_0_100_not_probability"],
                "new_context_level": lexical["context_realization_level"],
                "positive_evidence_de": spec["evidence_de"],
                "counterevidence_de": spec["counterevidence_de"],
                "v94_audit_decision": "REVISE",
                "v94_evidence_class": spec["evidence_class"],
                "v94_open_semantic_slots": spec["open_semantic_slots"],
            })
        else:
            row.update({
                "v94_reading_id": lexical["v94_reading_id"],
                "v94_lexical_core_de": lexical["v94_lexical_core_de"],
                "v94_context_realization_de": lexical["v94_context_realizations_de"],
                "new_lexical_score": lexical["working_model_score_0_100_not_probability"],
                "new_lexical_level": lexical["working_model_level"],
                "new_context_score": lexical["context_realization_score_0_100_not_probability"],
                "new_context_level": lexical["context_realization_level"],
                "v94_audit_decision": "HELD_FOR_LATER_REPAIR",
                "v94_evidence_class": "INHERITED_V93",
                "v94_open_semantic_slots": "NOT_EVALUATED",
            })
        output.append(row)
    assert len(output) == 56
    assert Counter(row["disposition"] for row in output) == Counter({"HELD_FOR_LATER_REPAIR": 52, "REVISED_IN_V94": 4})
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
            "left_surface": spec["expected_left_surface"], "old_lexical_core_de": source["v93_lexical_core_de"],
            "v94_lexical_core_de": target["v94_lexical_core_de"],
            "v94_context_realization_de": spec["v94_context_realization_de"],
            "old_score": source["working_model_score_0_100_not_probability"],
            "v94_score": target["working_model_score_0_100_not_probability"],
            "old_level": source["working_model_level"], "v94_level": target["working_model_level"],
            "family_ids": spec["family_ids"], "score_credit_family_ids": spec["score_credit_family_ids"],
            "decomposition": spec["decomposition"], "repair_mode": spec["repair_mode"],
            "resolved_debt_atom": spec["resolved_debt_atom"], "evidence_class": spec["evidence_class"],
            "evidence_de": spec["evidence_de"], "counterevidence_de": spec["counterevidence_de"],
            "open_semantic_slots": spec["open_semantic_slots"],
            "local_context_hypothesis": spec["local_context_hypothesis"],
            "target_semantic_scope": spec["target_semantic_scope"],
            "target_global_export_scope": spec["target_global_export_scope"],
            "target_bound_span_ids": spec["target_bound_span_ids"],
            "target_unconditional_global_export_allowed": spec["target_unconditional_global_export_allowed"],
            "occurrence_bound_span_id": spec["occurrence_bound_span_id"],
            "occurrence_bound_span_role": spec["occurrence_bound_span_role"],
            "component_global_export_allowed": 0, "historical_confirmation": HISTORICAL,
        })
    return output


def build_construction_dictionary() -> list[dict[str, Any]]:
    return [
        {
            "construction_atom": "P_INITIAL", "visible_pattern": "p-",
            "working_value_de": "Pulver / Pulverform", "working_mnemonic_not_historical_evidence": "GDT635:pulvis",
            "allowed_scope": "TOKEN_INITIAL_IN_ADMITTED_FOUR_HEAD_COMPOSITION",
            "forbidden_scope": "STANDALONE_P|INNER_P|TERMINAL_P|SH",
            "evidence_summary_de": "GDT635: 503 Anfangsvorkommen, 277 Typen, 140 Seiten und 361 lesergenau; das pol/sol/rol/lol-Gitter reproduziert pol kompositionell.",
            "productive_predictions": "pol=Pulverstoff|por=Pulverportion",
            "score_credit": 0, "global_export_allowed": 0, "historical_confirmation": HISTORICAL,
        },
        {
            "construction_atom": "L_INITIAL", "visible_pattern": "l-",
            "working_value_de": "Holz / holziger Pflanzenteil", "working_mnemonic_not_historical_evidence": "GDT635:lignum",
            "allowed_scope": "TOKEN_INITIAL_IN_ADMITTED_FOUR_HEAD_COMPOSITION",
            "forbidden_scope": "STANDALONE_L|INNER_L|TERMINAL_L|SH",
            "evidence_summary_de": "GDT635: 1.224 Anfangsvorkommen, 344 Typen, 104 Seiten und 923 lesergenau; 163 nackte l sind ausdrücklich getrennt.",
            "productive_predictions": "lol=Holzstoff|lor=Holzportion",
            "score_credit": 0, "global_export_allowed": 0, "historical_confirmation": HISTORICAL,
        },
        {
            "construction_atom": "R_INITIAL", "visible_pattern": "r-",
            "working_value_de": "Wurzel / Wurzeldroge", "working_mnemonic_not_historical_evidence": "GDT635:radix",
            "allowed_scope": "TOKEN_INITIAL_IN_ADMITTED_FOUR_HEAD_COMPOSITION",
            "forbidden_scope": "STANDALONE_R|INNER_R|TERMINAL_R|SH",
            "evidence_summary_de": "GDT635: 332 Anfangsvorkommen, 116 Typen, 68 Seiten und 216 lesergenau; 129 nackte r sind ausdrücklich getrennt.",
            "productive_predictions": "rol=Wurzelstoff|ror=Wurzelportion",
            "score_credit": 0, "global_export_allowed": 0, "historical_confirmation": HISTORICAL,
        },
        {
            "construction_atom": "OL_BODY", "visible_pattern": "-ol",
            "working_value_de": "Stoff / Material", "working_mnemonic_not_historical_evidence": "NONE",
            "allowed_scope": "EXACT_OL_REMAINDER_IN_ADMITTED_FOUR_HEAD_GRID",
            "forbidden_scope": "FREE_OL_SUBSTRING_EXPORT|ARBITRARY_INTERNAL_OL",
            "evidence_summary_de": "GDT635: vollständiges pol/sol/rol/lol-Gitter mit 128 Kopfvorkommen; nacktes ol 463-mal belegt.",
            "productive_predictions": "pol=Pulverstoff|sol=Samenmaterial|rol=Wurzelstoff|lol=Holzstoff",
            "score_credit": 0, "global_export_allowed": 0, "historical_confirmation": HISTORICAL,
        },
        {
            "construction_atom": "OR_BODY", "visible_pattern": "-or",
            "working_value_de": "Teil / Portion", "working_mnemonic_not_historical_evidence": "NONE",
            "allowed_scope": "EXACT_OR_REMAINDER_IN_ADMITTED_FOUR_HEAD_GRID",
            "forbidden_scope": "O_PLUS_R_DECOMPOSITION|FREE_INTERNAL_OR_EXPORT",
            "evidence_summary_de": "GDT635: vollständiges por/sor/ror/lor-Gitter mit 100 Kopfvorkommen; GDT693 bewahrt OR als getrennten geerbten Portions-Kontrollfall.",
            "productive_predictions": "por=Pulverportion|sor=Samenportion|ror=Wurzelportion|lor=Holzportion",
            "score_credit": 0, "global_export_allowed": 0, "historical_confirmation": HISTORICAL,
        },
    ]


def build_rivals() -> list[dict[str, Any]]:
    return [
        {"source_reading_id": "pol#1", "surface": "pol", "model_id": "SCOPED_COMPOSITION", "candidate_default_de": "Pulverstoff", "decision": "SELECT_PORTABLE_WHOLE", "evidence_fit_de": "p+ol sagt pol im vollständigen Vier-Kopf-Gitter voraus; 16 Vorkommen, 12 Seiten, 13 lesergenau.", "conflict_de": "p und ol bleiben außerhalb dieser Konstruktion nicht frei.", "portable_default_selected": 1, "score_credit": 0},
        {"source_reading_id": "pol#1", "surface": "pol", "model_id": "ATOMIC_WHOLE", "candidate_default_de": "Pulverstoff als gelerntes Ganzwort", "decision": "KEEP_RIVAL", "evidence_fit_de": "Der konkrete lokale Wert bleibt gleich.", "conflict_de": "Erklärt die belegten pol/sol/rol/lol-Wechsel nicht.", "portable_default_selected": 0, "score_credit": 0},
        {"source_reading_id": "pol#1", "surface": "pol", "model_id": "POTIO_PILULA", "candidate_default_de": "Trank oder Pille", "decision": "KEEP_HISTORICAL_RIVAL", "evidence_fit_de": "GDT635 bewahrt potio/pilula als p-Rivalen.", "conflict_de": "OL-Gitter und BOS-Materialrolle sprechen stärker für Pulverstoff.", "portable_default_selected": 0, "score_credit": 0},
        {"source_reading_id": "lor#1", "surface": "lor", "model_id": "SCOPED_COMPOSITION", "candidate_default_de": "Holzportion", "decision": "SELECT_PORTABLE_WHOLE", "evidence_fit_de": "l+or sagt lor im vollständigen Vier-Kopf-Gitter voraus; 38 Vorkommen, 28 Seiten, 30 lesergenau.", "conflict_de": "l und or bleiben konstruktionsgebunden.", "portable_default_selected": 1, "score_credit": 0},
        {"source_reading_id": "lor#1", "surface": "lor", "model_id": "LIQUOR_EXTRACT", "candidate_default_de": "Auszugsportion", "decision": "KEEP_HISTORICAL_RIVAL", "evidence_fit_de": "liquor/Auszug ist der lebende l-Rivale.", "conflict_de": "Keine Flüssigkeits- oder Entnahmemarkierung an P079; OR-Kontrolle ergibt Portion.", "portable_default_selected": 0, "score_credit": 0},
        {"source_reading_id": "lor#1", "surface": "lor", "model_id": "ATOMIC_WHOLE", "candidate_default_de": "Holzportion als gelerntes Ganzwort", "decision": "KEEP_RIVAL", "evidence_fit_de": "Passt der einzelnen Fundstelle.", "conflict_de": "Verliert die Vorhersage des por/sor/ror/lor-Gitters.", "portable_default_selected": 0, "score_credit": 0},
        {"source_reading_id": "l#1", "surface": "l", "model_id": "WOOD_HEAD_PLUS_BOUND_OCCURRENCE", "candidate_default_de": "Holz-Kopf; aktive Stelle nur im B003-Ganzspan", "decision": "SELECT_SCOPE_SPLIT", "evidence_fit_de": "Produktiver l-Anfangskopf ist großflächig belegt; beide Alternativleser verschmelzen die aktive Stelle mit karchees.", "conflict_de": "Das nackte l selbst ist kein Beleg für freien Holzexport.", "portable_default_selected": 1, "score_credit": 0},
        {"source_reading_id": "l#1", "surface": "l", "model_id": "FREE_WOOD", "candidate_default_de": "Holz", "decision": "REJECT_FREE_EXPORT", "evidence_fit_de": "Der B003-Gesamtwert enthält Holzdroge.", "conflict_de": "163 nackte l sind vom Initialkopf getrennt; Einzelausgabe würde B003 doppeln.", "portable_default_selected": 0, "score_credit": 0},
        {"source_reading_id": "l#1", "surface": "l", "model_id": "WEIGHT_UNIT", "candidate_default_de": "Pfund / Gewichtseinheit", "decision": "KEEP_LOCAL_RIVAL", "evidence_fit_de": "Die ältere f66r-Lesung liefert einen Mengenrivalen.", "conflict_de": "Passt dem B003-Holzdrogenverband an P435 schlechter.", "portable_default_selected": 0, "score_credit": 0},
        {"source_reading_id": "r#1", "surface": "r", "model_id": "ROOT_HEAD_PLUS_BOUND_OCCURRENCE", "candidate_default_de": "Wurzel-Kopf; aktive Stelle nur im keo-r-Ganzspan", "decision": "SELECT_SCOPE_SPLIT", "evidence_fit_de": "Produktiver r-Anfangskopf ist großflächig belegt; aktive Leser verschmelzen keo r zu keor.", "conflict_de": "Die aktive nackte Stelle trägt Wurzel nicht selbständig.", "portable_default_selected": 1, "score_credit": 0},
        {"source_reading_id": "r#1", "surface": "r", "model_id": "FREE_ROOT", "candidate_default_de": "Wurzel", "decision": "REJECT_FREE_EXPORT", "evidence_fit_de": "GDT635 stützt r=radix in Initialkompositionen.", "conflict_de": "129 nackte r sind getrennt; P289 wird vom Span vollständig konsumiert.", "portable_default_selected": 0, "score_credit": 0},
        {"source_reading_id": "r#1", "surface": "r", "model_id": "R_EQUALS_PORTION", "candidate_default_de": "Portion", "decision": "REJECT_COMPONENT_VALUE", "evidence_fit_de": "Der lokale Gesamtspan lautet heiße Portion.", "conflict_de": "GDT693 bindet Portion an OR, nicht R; der Wert gehört keo r als Ganzem.", "portable_default_selected": 0, "score_credit": 0},
    ]


def build_spans(source_rows: list[dict[str, str]], context_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = [dict(row) for row in source_rows]
    present = {row["bound_span_id"] for row in output}
    legacy = read_tsv(LEGACY_SPANS)
    for source in legacy:
        span_id = source["span_id"]
        assert span_id not in present
        positions = sorted(
            (row for row in context_rows if row["v93_occurrence_bound_span_id"] == span_id),
            key=lambda row: int(row["token_ordinal"]),
        )
        assert len(positions) == 2
        left, right = positions
        assert left["v93_occurrence_bound_span_role"] == "LEFT"
        assert right["v93_occurrence_bound_span_role"] == "RIGHT"
        assert f"{left['surface']}|{right['surface']}" == source["surfaces"]
        assert int(left["token_ordinal"]) == int(source["start_ordinal"])
        assert int(right["token_ordinal"]) == int(source["end_ordinal"])
        output.append({
            "bound_span_id": span_id, "page": left["page"], "locus": source["locus"],
            "left_position_id": left["position_id"], "left_surface": left["surface"],
            "left_reading_id": left["source_reading_id"], "left_role": "LEFT",
            "right_position_id": right["position_id"], "right_surface": right["surface"],
            "right_reading_id": right["source_reading_id"], "right_role": "RIGHT",
            "render_once_de": source["v68_selected_gloss_de"],
            "source_gdts": "GDT693|GDT694|GDT695|GDT721" if span_id != "B003" else "GDT678|GDT694|GDT695|GDT721",
            "global_export_allowed": 0, "historical_confirmation": HISTORICAL,
        })
        present.add(span_id)
    assert present == {"B001", "B002", "B003", "G683_CHEOP_OL", "G678_KEO_R_F7R2"}
    return output


def build_span_restore_audit(source_spans: list[dict[str, str]], target_spans: list[dict[str, Any]], context_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    source_ids = {row["bound_span_id"] for row in source_spans}
    target_by_id = {row["bound_span_id"]: row for row in target_spans}
    output: list[dict[str, Any]] = []
    for source in read_tsv(LEGACY_SPANS):
        span_id = source["span_id"]
        target = target_by_id[span_id]
        output.append({
            "bound_span_id": span_id, "locus": source["locus"], "surfaces": source["surfaces"],
            "v93_context_reference_positions": sum(row["v93_occurrence_bound_span_id"] == span_id for row in context_rows),
            "present_in_v93_renderer": int(span_id in source_ids), "restored_in_v94_renderer": 1,
            "v68_render_once_de": source["v68_selected_gloss_de"], "v94_render_once_de": target["render_once_de"],
            "render_byte_identical": int(source["v68_selected_gloss_de"] == target["render_once_de"]),
            "global_export_allowed": target["global_export_allowed"], "historical_confirmation": HISTORICAL,
        })
    return output


def build_span_execution_audit(spans: list[dict[str, Any]], context_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for span in spans:
        span_id = str(span["bound_span_id"])
        positions = sorted(
            (row for row in context_rows if row["v94_occurrence_bound_span_id"] == span_id),
            key=lambda row: int(row["token_ordinal"]),
        )
        assert len(positions) == 2
        left, right = positions
        assert (left["position_id"], left["v94_occurrence_bound_span_role"]) == (span["left_position_id"], "LEFT")
        assert (right["position_id"], right["v94_occurrence_bound_span_role"]) == (span["right_position_id"], "RIGHT")
        assert left["v94_occurrence_bound_span_global_export_allowed"] == "0"
        assert right["v94_occurrence_bound_span_global_export_allowed"] == "0"
        output.append({
            "bound_span_id": span_id, "page": span["page"], "locus": span["locus"],
            "source_surfaces": f"{span['left_surface']}|{span['right_surface']}",
            "consumed_position_ids": f"{left['position_id']}|{right['position_id']}",
            "consumed_position_count": 2, "left_role_count": 1, "right_role_count": 1,
            "standalone_outputs_suppressed": 2, "emitted_output_units": 1,
            "render_once_de": span["render_once_de"], "global_export_allowed": 0,
            "execution_status": "EXECUTABLE_RENDER_ONCE", "historical_confirmation": HISTORICAL,
        })
    return output


def build_complete(source_rows: list[dict[str, str]], lexical: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for source in source_rows:
        if source["current_layer"] == "ACTIVE_V93_LEXICAL_CORE":
            continue
        row = rename_v93(source)
        row.update({
            "v94_audit_decision": "OUTSIDE_ACTIVE_V94_TRANCHE",
            "v94_evidence_class": "INHERITED_GLOBAL_V48",
            "v94_open_semantic_slots": "NOT_EVALUATED",
            "v94_component_global_export_allowed": "NOT_EVALUATED",
        })
        output.append(row)
    for row in lexical:
        output.append({
            "surface": row["surface"], "reading_id": row["v94_reading_id"],
            "working_meaning_de": row["v94_lexical_core_de"], "current_layer": "ACTIVE_V94_LEXICAL_CORE",
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
            "v94_context_realizations_de": row["v94_context_realizations_de"],
            "source_reading_ids": row["source_reading_ids"], "v94_audit_decision": row["v94_audit_decision"],
            "v94_evidence_class": row["v94_evidence_class"],
            "v94_open_semantic_slots": row["v94_open_semantic_slots"],
            "v94_component_global_export_allowed": row["v94_component_global_export_allowed"],
        })
    return sorted(output, key=lambda row: (str(row["surface"]), str(row["reading_id"])))


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    specs = read_tsv(SPECS)
    bindings = read_tsv(BINDINGS)
    assert len(specs) == 4 and {row["source_reading_id"] for row in specs} == {"pol#1", "lor#1", "l#1", "r#1"}
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
    construction = build_construction_dictionary()
    rivals = build_rivals()
    complete = build_complete(source_complete, lexical)
    spans = build_spans(read_tsv(SOURCE_SPANS), source_context)
    span_restore = build_span_restore_audit(read_tsv(SOURCE_SPANS), spans, source_context)
    span_execution = build_span_execution_audit(spans, contexts)

    write_tsv(ART / "V94_324_ACTIVE_LEXICAL_READINGS.tsv", lexical)
    write_tsv(ART / "V94_479_CONTEXT_REALIZATIONS.tsv", contexts)
    write_tsv(ART / "V94_56_HELD_READING_AUDIT.tsv", census)
    write_tsv(ART / "V94_4_HEAD_CORE_CONTEXT_DELTA.tsv", delta)
    write_tsv(ART / "V94_5_SCOPED_CONSTRUCTION_DICTIONARY.tsv", construction)
    write_tsv(ART / "V94_12_RIVAL_MODEL_COMPARISON.tsv", rivals)
    write_tsv(ART / "V94_30_PRIMARY_EVIDENCE_BINDINGS.tsv", evidence)
    write_tsv(ART / "V94_3_LEGACY_SPAN_RESTORE_AUDIT.tsv", span_restore)
    write_tsv(ART / "V94_5_BOUND_SPAN_EXECUTION_AUDIT.tsv", span_execution)
    write_tsv(ART / "V94_COMPLETE_WORD_CONFIDENCE.tsv", complete)
    write_tsv(ART / "V94_5_BOUND_SPAN_RENDERER.tsv", spans)
    shutil.copyfile(SOURCE_DIRECTIVES, ART / "V94_2_ONE_SHOT_RENDER_DIRECTIVES.tsv")
    shutil.copyfile(SOURCE_F7R2, ART / "V94_8_F7R2_RENDERED_UNITS.tsv")

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
        "experiment_id": "GDT721", "status": STATUS, "target_readings": 4,
        "target_positions": 4, "target_pages": 4, "primary_evidence_bindings": len(evidence),
        "rival_model_rows": len(rivals), "construction_atoms_retained": len(construction),
        "predicted_compound_wholes_retained": 2, "bound_active_occurrences_corrected": 2,
        "score_credit_families": 0,
        "score_delta_total": 0, "component_global_exports": 0,
        "active_lexical_rows": len(lexical), "active_source_readings": len(lexical_by_source),
        "context_positions": len(contexts), "non_target_lexical_rows_preserved": len(lexical) - 4,
        "non_target_context_positions_preserved": len(contexts) - 4,
        "remaining_unreviewed_weak_readings": 52, "confidence_levels": dict(sorted(levels.items())),
        "complete_dictionary_rows": len(complete),
        "complete_dictionary_surfaces": len({row["surface"] for row in complete}),
        "complete_dictionary_rows_with_default_confidence_and_evidence": sum(
            bool(row["working_meaning_de"] and row["working_model_level"] and row["positive_evidence_de"] and row["counterevidence_de"])
            for row in complete
        ),
        "bound_spans_preserved": len(read_tsv(SOURCE_SPANS)),
        "legacy_bound_spans_restored": len(span_restore), "bound_spans_total": len(spans),
        "bound_span_execution_rows": len(span_execution),
        "bound_positions_consumed_once": sum(int(row["consumed_position_count"]) for row in span_execution),
        "f7r2_output_units": len(read_tsv(SOURCE_F7R2)), "f84_or_f84r_used": 0,
        "historical_confirmation": HISTORICAL,
        "canonical_dictionary": "experiments/yolo/gdt721_v94_four_head_construction_scope_and_b003_restore/artifacts/V94_COMPLETE_WORD_CONFIDENCE.tsv",
    }
    (ART / "RESULT.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
