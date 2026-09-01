#!/usr/bin/env python3
"""Build V86 by repairing the remaining measure and CKH/CPH weak tranche."""

from __future__ import annotations

import csv
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
EXP = ROOT / "experiments/yolo/gdt713_v86_measure_ckh_core_context_repair"
SRC = EXP / "src"
ART = EXP / "artifacts"
G712 = ROOT / "experiments/yolo/gdt712_v85_al_state_core_context_repair/artifacts"
G711 = ROOT / "experiments/yolo/gdt711_v84_active_weak_family_repair/artifacts"

SOURCE_LEXICAL = G712 / "V85_324_ACTIVE_LEXICAL_READINGS.tsv"
SOURCE_CONTEXT = G712 / "V85_479_CONTEXT_REALIZATIONS.tsv"
SOURCE_COMPLETE = G712 / "V85_COMPLETE_WORD_CONFIDENCE.tsv"
SOURCE_CENSUS = G712 / "V85_151_HELD_READING_AUDIT.tsv"
SOURCE_SPANS = G712 / "V85_1_BOUND_SPAN_RENDERER.tsv"
SOURCE_FAMILIES = G711 / "V84_13_STEM_FAMILY_EVIDENCE.tsv"
SPECS = SRC / "V86_9_AUDIT_SPECS.tsv"

HISTORICAL = "H0_NONE"
STATUS = (
    "PASS_V86_9_MEASURE_CKH_READINGS_AUDITED__8_REVISED_1_HELD__"
    "10_POSITIONS_7_PAGES__7_W0_143_W1_155_W2_19_W3__"
    "109_WEAK_READINGS_REMAIN__ALL_H0_NONE"
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, fields: list[str], rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for source in rows:
            writer.writerow({field: source.get(field, "") for field in fields})


def split_pipe(value: str) -> list[str]:
    return [part.strip() for part in value.split("|") if part.strip() and part.strip() not in {"NONE", "0"}]


def ordered_compact(values: Iterable[str], separator: str = "|", empty: str = "NONE") -> str:
    result: list[str] = []
    seen: set[str] = set()
    for raw in values:
        value = raw.strip()
        if value and value not in {"NONE", "0"} and value not in seen:
            seen.add(value)
            result.append(value)
    return separator.join(result) if result else empty


def append_pipe(value: str, addition: str) -> str:
    return ordered_compact([*split_pipe(value), addition])


def unique_fields(fields: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(fields))


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


def v86_key(value: str) -> str:
    return value.replace("v85", "v86").replace("V85", "V86")


def rename_v85_fields(row: dict[str, str]) -> dict[str, str]:
    return {v86_key(key): value for key, value in row.items()}


def family_v86_key(value: str) -> str:
    return value.replace("v84", "v86").replace("V84", "V86")


def lexical_rows(
    source_rows: list[dict[str, str]], specs: list[dict[str, str]]
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    specs_by_id = {row["source_reading_id"]: row for row in specs}
    output: list[dict[str, Any]] = []
    for source in source_rows:
        row: dict[str, Any] = rename_v85_fields(source)
        source_ids = split_pipe(source["source_reading_ids"])
        spec = specs_by_id.get(source_ids[0]) if len(source_ids) == 1 else None
        if spec:
            assert source["v85_lexical_core_de"] == spec["old_lexical_core_de"]
            base = int(source["working_model_score_0_100_not_probability"])
            score = min(base + int(spec["score_delta_lexical_core"]), int(spec["lexical_core_cap"]))
            context_score = min(score, int(spec["context_realization_cap"]))
            row.update({
                "v86_lexical_core_de": spec["v86_lexical_core_de"],
                "v86_context_realizations_de": spec["v86_context_realization_de"],
                "family_ids": spec["family_ids"],
                "decomposition": spec["decomposition"],
                "repair_modes": spec["repair_mode"],
                "resolved_debt_atoms": spec["resolved_debt_atom"],
                "last_semantic_writer": "GDT713",
                "base_score": base,
                "score_delta_lexical_core": spec["score_delta_lexical_core"],
                "lexical_core_cap": spec["lexical_core_cap"],
                "working_model_score_0_100_not_probability": score,
                "working_model_level": level(score),
                "context_realization_cap": spec["context_realization_cap"],
                "context_realization_score_0_100_not_probability": context_score,
                "context_realization_level": level(context_score),
                "source_gdts": append_pipe(source["source_gdts"], "GDT713"),
                "positive_evidence_de": (
                    "GDT713 trennt erneut Wortkern und lokale Realisierung: "
                    + spec["evidence_de"] + " || " + source["positive_evidence_de"]
                ),
                "counterevidence_de": (
                    "GDT713 Gegenbeleg: " + spec["counterevidence_de"]
                    + " || Historisch unbestaetigte Arbeitstheorie; keine Klartextidentifikation."
                ),
            })
            if spec["occurrence_bound_span_override"] != "NONE":
                row.update({
                    "semantic_scope": "BOUND_SPAN_LOCAL_READING",
                    "semantic_applicability": "COMPOUND_ONLY_LOCAL_READING",
                    "global_export_scope": "BOUND_SPAN_ONLY_NO_GLOBAL_EXPORT",
                    "bound_span_ids": spec["occurrence_bound_span_override"],
                    "unconditional_global_export_allowed": 0,
                })
            row.update({
                "v86_audit_decision": spec["decision"],
                "v86_evidence_class": spec["evidence_class"],
                "v86_open_semantic_slots": spec["open_semantic_slots"],
                "v86_component_global_export_allowed": spec["component_global_export_allowed"],
                "v86_prior_lexical_core_de": source["v85_lexical_core_de"],
            })
        else:
            row.update({
                "v86_audit_decision": "NOT_IN_GDT713_TRANCHE",
                "v86_evidence_class": "INHERITED_V85",
                "v86_open_semantic_slots": "NOT_EVALUATED",
                "v86_component_global_export_allowed": "NOT_EVALUATED",
                "v86_prior_lexical_core_de": source["v85_lexical_core_de"],
            })
        output.append(row)

    by_source: dict[str, dict[str, Any]] = {}
    for row in output:
        for source_id in split_pipe(str(row["source_reading_ids"])):
            assert source_id not in by_source
            by_source[source_id] = row
    assert len(by_source) == 332
    return output, by_source


def context_rows(
    source_rows: list[dict[str, str]],
    specs: list[dict[str, str]],
    lexical_by_source: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    specs_by_id = {row["source_reading_id"]: row for row in specs}
    output: list[dict[str, Any]] = []
    for source in source_rows:
        row: dict[str, Any] = rename_v85_fields(source)
        source_id = source["source_reading_id"]
        lexical = lexical_by_source[source_id]
        spec = specs_by_id.get(source_id)
        row.update({
            "v86_reading_id": lexical["v86_reading_id"],
            "v86_lexical_core_de": lexical["v86_lexical_core_de"],
            "v86_context_realization_de": spec["v86_context_realization_de"] if spec else source["v85_context_realization_de"],
            "v86_repair_mode": spec["repair_mode"] if spec else source["v85_repair_mode"],
            "v86_resolved_debt_atom": spec["resolved_debt_atom"] if spec else source["v85_resolved_debt_atom"],
            "v86_lexical_score": lexical["working_model_score_0_100_not_probability"],
            "v86_lexical_level": lexical["working_model_level"],
            "v86_context_score": lexical["context_realization_score_0_100_not_probability"],
            "v86_context_level": lexical["context_realization_level"],
            "v86_semantic_scope": lexical["semantic_scope"],
            "v86_semantic_applicability": lexical["semantic_applicability"],
            "v86_global_export_scope": lexical["global_export_scope"],
            "v86_lexical_bound_span_ids": lexical["bound_span_ids"],
            "v86_unconditional_global_export_allowed": lexical["unconditional_global_export_allowed"],
            "v86_historical_confirmation": HISTORICAL,
            "v86_audit_decision": spec["decision"] if spec else "NOT_IN_GDT713_TRANCHE",
            "v86_evidence_class": spec["evidence_class"] if spec else "INHERITED_V85",
            "v86_open_semantic_slots": spec["open_semantic_slots"] if spec else "NOT_EVALUATED",
            "v86_component_global_export_allowed": spec["component_global_export_allowed"] if spec else "NOT_EVALUATED",
        })
        if spec and spec["occurrence_bound_span_override"] != "NONE":
            row.update({
                "v86_occurrence_bound_span_id": spec["occurrence_bound_span_override"],
                "v86_occurrence_bound_span_role": spec["occurrence_bound_span_role_override"],
                "v86_occurrence_bound_span_global_export_allowed": spec["occurrence_bound_span_export_override"],
            })
        output.append(row)
    return output


def census_rows(
    source_rows: list[dict[str, str]],
    specs: list[dict[str, str]],
    lexical_by_source: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    specs_by_id = {row["source_reading_id"]: row for row in specs}
    output: list[dict[str, Any]] = []
    for source in source_rows:
        if source["disposition"] != "HELD_FOR_LATER_REPAIR":
            continue
        row: dict[str, Any] = rename_v85_fields(source)
        source_id = source["source_reading_id"]
        lexical = lexical_by_source[source_id]
        spec = specs_by_id.get(source_id)
        if spec:
            row.update({
                "disposition": "REVISED_IN_V86" if spec["decision"] == "REVISE" else "AUDITED_HOLD_IN_V86",
                "repair_mode": spec["repair_mode"],
                "resolved_debt_atom": spec["resolved_debt_atom"],
                "v86_reading_id": lexical["v86_reading_id"],
                "v86_lexical_core_de": lexical["v86_lexical_core_de"],
                "v86_context_realization_de": spec["v86_context_realization_de"],
                "new_lexical_score": lexical["working_model_score_0_100_not_probability"],
                "new_lexical_level": lexical["working_model_level"],
                "new_context_score": lexical["context_realization_score_0_100_not_probability"],
                "new_context_level": lexical["context_realization_level"],
                "positive_evidence_de": spec["evidence_de"],
                "counterevidence_de": spec["counterevidence_de"],
                "v86_audit_decision": spec["decision"],
                "v86_evidence_class": spec["evidence_class"],
                "v86_open_semantic_slots": spec["open_semantic_slots"],
            })
        else:
            row.update({
                "v86_reading_id": lexical["v86_reading_id"],
                "v86_lexical_core_de": lexical["v86_lexical_core_de"],
                "v86_context_realization_de": lexical["v86_context_realizations_de"],
                "new_lexical_score": lexical["working_model_score_0_100_not_probability"],
                "new_lexical_level": lexical["working_model_level"],
                "new_context_score": lexical["context_realization_score_0_100_not_probability"],
                "new_context_level": lexical["context_realization_level"],
                "v86_audit_decision": "HELD_FOR_LATER_REPAIR",
                "v86_evidence_class": "INHERITED_V85",
                "v86_open_semantic_slots": "NOT_EVALUATED",
            })
        output.append(row)
    return output


def delta_rows(
    specs: list[dict[str, str]],
    source_lexical: list[dict[str, str]],
    target_lexical_by_source: dict[str, dict[str, Any]],
    source_context: list[dict[str, str]],
) -> list[dict[str, Any]]:
    source_by_id: dict[str, dict[str, str]] = {}
    for row in source_lexical:
        for source_id in split_pipe(row["source_reading_ids"]):
            source_by_id[source_id] = row
    occurrences: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in source_context:
        occurrences[row["source_reading_id"]].append(row)
    output: list[dict[str, Any]] = []
    for spec in specs:
        source = source_by_id[spec["source_reading_id"]]
        target = target_lexical_by_source[spec["source_reading_id"]]
        positions = occurrences[spec["source_reading_id"]]
        output.append({
            "source_reading_id": spec["source_reading_id"],
            "surface": source["surface"],
            "decision": spec["decision"],
            "occurrence_count": len(positions),
            "page_count": len({row["page"] for row in positions}),
            "pages": ordered_compact(sorted({row["page"] for row in positions})),
            "positions": ordered_compact(f"{row['locus']}#{row['token_ordinal']}" for row in positions),
            "old_lexical_core_de": source["v85_lexical_core_de"],
            "v86_lexical_core_de": target["v86_lexical_core_de"],
            "v86_context_realization_de": spec["v86_context_realization_de"],
            "old_score": source["working_model_score_0_100_not_probability"],
            "v86_score": target["working_model_score_0_100_not_probability"],
            "old_level": source["working_model_level"],
            "v86_level": target["working_model_level"],
            "family_ids": spec["family_ids"],
            "decomposition": spec["decomposition"],
            "repair_mode": spec["repair_mode"],
            "resolved_debt_atom": spec["resolved_debt_atom"],
            "evidence_class": spec["evidence_class"],
            "evidence_de": spec["evidence_de"],
            "counterevidence_de": spec["counterevidence_de"],
            "open_semantic_slots": spec["open_semantic_slots"],
            "component_global_export_allowed": spec["component_global_export_allowed"],
            "old_semantic_scope": source["semantic_scope"],
            "v86_semantic_scope": target["semantic_scope"],
            "old_global_export_scope": source["global_export_scope"],
            "v86_global_export_scope": target["global_export_scope"],
            "occurrence_bound_span_override": spec["occurrence_bound_span_override"],
            "historical_confirmation": HISTORICAL,
        })
    return output


def family_rows(
    source_rows: list[dict[str, str]],
    specs: list[dict[str, str]],
    source_context: list[dict[str, str]],
    lexical_by_source: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    wanted = {family for spec in specs for family in split_pipe(spec["family_ids"])}
    specs_by_family: dict[str, list[dict[str, str]]] = defaultdict(list)
    for spec in specs:
        for family in split_pipe(spec["family_ids"]):
            specs_by_family[family].append(spec)
    occurrences: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in source_context:
        occurrences[row["source_reading_id"]].append(row)
    output: list[dict[str, Any]] = []
    for source in source_rows:
        family = source["family_id"]
        if family not in wanted:
            continue
        row: dict[str, Any] = {family_v86_key(key): value for key, value in source.items()}
        selected = specs_by_family[family]
        selected_ids = [spec["source_reading_id"] for spec in selected]
        selected_positions = [position for source_id in selected_ids for position in occurrences[source_id]]
        row.update({
            "selected_source_readings": len(selected_ids),
            "selected_lexical_readings": len({lexical_by_source[source_id]["v86_reading_id"] for source_id in selected_ids}),
            "selected_positions": len(selected_positions),
            "selected_pages": len({position["page"] for position in selected_positions}),
            "selected_source_reading_ids": ordered_compact(selected_ids),
            "selected_surfaces": ordered_compact(sorted({position["surface"] for position in selected_positions})),
            "selected_v86_reading_ids": ordered_compact(sorted({str(lexical_by_source[source_id]["v86_reading_id"]) for source_id in selected_ids})),
            "selected_v86_levels": ordered_compact(sorted({str(lexical_by_source[source_id]["working_model_level"]) for source_id in selected_ids})),
            "automatic_historical_credit": 0,
            "historical_confirmation": HISTORICAL,
            "v86_decisions": ordered_compact(spec["decision"] for spec in selected),
        })
        output.append(row)
    return output


def complete_rows(source_rows: list[dict[str, str]], lexical: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for source in source_rows:
        if source["current_layer"] == "ACTIVE_V85_LEXICAL_CORE":
            continue
        row: dict[str, Any] = rename_v85_fields(source)
        row.update({
            "v86_audit_decision": "OUTSIDE_ACTIVE_V86_TRANCHE",
            "v86_evidence_class": "INHERITED_GLOBAL_V48",
            "v86_open_semantic_slots": "NOT_EVALUATED",
            "v86_component_global_export_allowed": "NOT_EVALUATED",
        })
        output.append(row)
    for row in lexical:
        output.append({
            "surface": row["surface"],
            "reading_id": row["v86_reading_id"],
            "working_meaning_de": row["v86_lexical_core_de"],
            "current_layer": "ACTIVE_V86_LEXICAL_CORE",
            "semantic_scope": row["semantic_scope"],
            "semantic_applicability": row["semantic_applicability"],
            "form_level": row["form_level"],
            "occurrence_count": row["occurrence_count"],
            "page_count": row["page_count"],
            "locus_count": row["locus_count"],
            "working_model_score_0_100_not_probability": row["working_model_score_0_100_not_probability"],
            "working_model_level": row["working_model_level"],
            "source_gdts": row["source_gdts"],
            "positive_evidence_de": row["positive_evidence_de"],
            "counterevidence_de": row["counterevidence_de"],
            "historical_confirmation": row["historical_confirmation"],
            "historical_analogue": row["historical_analogue"],
            "relation_word_delta": row["relation_word_delta"],
            "global_export_scope": row["global_export_scope"],
            "bound_span_ids": row["bound_span_ids"],
            "unconditional_global_export_allowed": row["unconditional_global_export_allowed"],
            "v86_context_realizations_de": row["v86_context_realizations_de"],
            "source_reading_ids": row["source_reading_ids"],
            "v86_audit_decision": row["v86_audit_decision"],
            "v86_evidence_class": row["v86_evidence_class"],
            "v86_open_semantic_slots": row["v86_open_semantic_slots"],
            "v86_component_global_export_allowed": row["v86_component_global_export_allowed"],
        })
    return sorted(output, key=lambda item: (str(item["surface"]), str(item["reading_id"])))


def report_text(result: dict[str, Any]) -> str:
    return f"""# GDT713 — V86 measure/CKH core-context repair

Status: `{STATUS}`

## Ergebnis

V86 auditiert die tatsaechlich noch offenen drei Massformen und sechs
CKH/CPH-Formen: neun Lesungen an zehn unveraenderten Positionen auf sieben
bereits zugelassenen Seiten. Acht Wortkerne werden repariert; `dol =
Materialmaß` bleibt als bereits kleinster sinnvoller Kern stehen und gewinnt
nur den expliziten D+OL-Ganzformbeleg hinzu.

Die sechs CKH/CPH-Ganzformen tragen jetzt den gelernten Familienkopf
`Mischung`, nie `Arznei`. Sichtbare Trocken-/Feucht- und Grund-/Anfangsfelder
bleiben erhalten. E_ATTR und O_PREP bleiben Strukturmetadaten; sie werden nicht
zu freien deutschen Woertern. Wo der O-Rahmen lokal praktisch lesbar ist,
steht `Ansatz` nur in der Fundstellenrealisierung.

Bei den Massformen wird `oram` zu `Maßportion` verdichtet; der unbelegte
Ansatzkopf und der lexikalisierte Artikel verschwinden aus dem Wortkern.
`otam` traegt als Kern `kalt; Maß I` und rendert an beiden benachbarten Stellen
weiter konkret als `ein Maß kalten Ansatzes`. Inhalt und historische Einheit
bleiben offene Slots, nicht erfundene Substantive.

## Warum `dol` gehalten wird

GDT638 hatte `dol` bereits ueber 76 Vorkommen als exakte D+OL-Ganzform
auditiert: Wert-/Masskopf plus Materialtraeger, bewusst ohne Dosis, Messverb
oder historische Einheit. Darum waere eine neue Umschreibung keine
Verbesserung. V86 erhoeht nur den Evidenzindex `18 -> 23`; D und OL bleiben
familiengebunden und nicht frei exportierbar.

## Bestand

- auditierte Lesungen / Positionen / Seiten: {result['audited_readings']} / {result['audited_positions']} / {result['audited_pages']}
- revidiert / bewusst gehalten: {result['revised_readings']} / {result['held_readings']}
- aktive Lesungen / Positionen: {result['active_lexical_readings']} / {result['active_positions']}
- aktive Confidence-Stufen: `{json.dumps(result['active_level_counts'], ensure_ascii=False, sort_keys=True)}`
- komplettes Woerterbuch: {result['complete_surfaces']} Oberflaechen / {result['complete_readings']} Lesungen
- noch nicht einzeln bearbeitete schwache Lesungen: {result['remaining_unreviewed_weak_readings']}

## Grenze

Das ist die konkrete Arbeitsuebersetzung des aktuellen Modells, kein
bestaetigter Klartext. Confidence bleibt ein interner Evidenzindex, keine
Wahrscheinlichkeit. Keine Komponente wird als freies Voynich-Wort exportiert;
alle historischen Felder bleiben `H0_NONE`. Es wurden keine neue Seite, kein
Bild, keine neue Transkription, kein `f84` und kein `f84r` benutzt.
"""


def main() -> int:
    source_lexical = read_tsv(SOURCE_LEXICAL)
    source_context = read_tsv(SOURCE_CONTEXT)
    source_complete = read_tsv(SOURCE_COMPLETE)
    source_census = read_tsv(SOURCE_CENSUS)
    source_spans = read_tsv(SOURCE_SPANS)
    source_families = read_tsv(SOURCE_FAMILIES)
    specs = read_tsv(SPECS)

    assert (
        len(source_lexical), len(source_context), len(source_complete),
        len(source_census), len(source_spans), len(source_families), len(specs),
    ) == (324, 479, 1586, 151, 1, 13, 9)
    assert len({row["source_reading_id"] for row in specs}) == 9
    assert Counter(row["decision"] for row in specs) == Counter({"REVISE": 8, "HOLD": 1})
    assert all(row["component_global_export_allowed"] == "0" for row in specs)
    assert all(not row["page"].startswith("f84") and not row["locus"].startswith("f84") for row in source_context)

    lexical, lexical_by_source = lexical_rows(source_lexical, specs)
    contexts = context_rows(source_context, specs, lexical_by_source)
    census = census_rows(source_census, specs, lexical_by_source)
    delta = delta_rows(specs, source_lexical, lexical_by_source, source_context)
    families = family_rows(source_families, specs, source_context, lexical_by_source)
    complete = complete_rows(source_complete, lexical)
    bound_spans = source_spans

    target_ids = {row["source_reading_id"] for row in specs}
    selected_positions = [row for row in source_context if row["source_reading_id"] in target_ids]
    active_levels = Counter(str(row["working_model_level"]) for row in lexical)
    complete_levels = Counter(str(row["working_model_level"]) for row in complete)
    assert len(selected_positions) == 10 and len({row["page"] for row in selected_positions}) == 7
    assert len(census) == 118 and len(families) == 8
    assert len(complete) == 1586 and len({row["surface"] for row in complete}) == 1582
    assert active_levels == Counter({
        "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY": 7, "W1_WEAK_WORKING": 143,
        "W2_PROVISIONAL_WORKING": 155, "W3_SOLID_WORKING_THEORY": 19,
    })
    assert complete_levels == Counter({
        "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY": 287, "W1_WEAK_WORKING": 323,
        "W2_PROVISIONAL_WORKING": 533, "W3_SOLID_WORKING_THEORY": 443,
    })

    lexical_fields = unique_fields([v86_key(field) for field in source_lexical[0]] + [
        "v86_audit_decision", "v86_evidence_class", "v86_open_semantic_slots",
        "v86_component_global_export_allowed", "v86_prior_lexical_core_de",
    ])
    context_fields = unique_fields([v86_key(field) for field in source_context[0]] + [
        "v86_audit_decision", "v86_evidence_class", "v86_open_semantic_slots",
        "v86_component_global_export_allowed",
    ])
    census_fields = unique_fields([v86_key(field) for field in source_census[0]] + [
        "v86_audit_decision", "v86_evidence_class", "v86_open_semantic_slots",
    ])
    family_fields = [family_v86_key(field) for field in source_families[0]] + ["v86_decisions"]
    complete_fields = unique_fields([v86_key(field) for field in source_complete[0]] + [
        "v86_audit_decision", "v86_evidence_class", "v86_open_semantic_slots",
        "v86_component_global_export_allowed",
    ])
    write_tsv(ART / "V86_324_ACTIVE_LEXICAL_READINGS.tsv", lexical_fields, lexical)
    write_tsv(ART / "V86_479_CONTEXT_REALIZATIONS.tsv", context_fields, contexts)
    write_tsv(ART / "V86_118_HELD_READING_AUDIT.tsv", census_fields, census)
    write_tsv(ART / "V86_9_MEASURE_CKH_CORE_CONTEXT_DELTA.tsv", list(delta[0]), delta)
    write_tsv(ART / "V86_8_FAMILY_EVIDENCE.tsv", family_fields, families)
    write_tsv(ART / "V86_1_BOUND_SPAN_RENDERER.tsv", list(bound_spans[0]), bound_spans)
    write_tsv(ART / "V86_COMPLETE_WORD_CONFIDENCE.tsv", complete_fields, complete)

    result = {
        "experiment_id": "GDT713", "status": STATUS,
        "claim_ceiling": "EXPLORATORY_WORKING_DICTIONARY_ONLY_NOT_PLAINTEXT",
        "audited_readings": len(specs), "audited_positions": len(selected_positions),
        "audited_pages": len({row["page"] for row in selected_positions}),
        "revised_readings": sum(row["decision"] == "REVISE" for row in specs),
        "held_readings": sum(row["decision"] == "HOLD" for row in specs),
        "revised_positions": sum(sum(position["source_reading_id"] == row["source_reading_id"] for position in selected_positions) for row in specs if row["decision"] == "REVISE"),
        "held_positions": sum(sum(position["source_reading_id"] == row["source_reading_id"] for position in selected_positions) for row in specs if row["decision"] == "HOLD"),
        "active_lexical_readings": len(lexical), "active_positions": len(contexts),
        "active_level_counts": dict(sorted(active_levels.items())),
        "active_applicability_counts": dict(sorted(Counter(str(row["semantic_applicability"]) for row in lexical).items())),
        "active_export_scope_counts": dict(sorted(Counter(str(row["global_export_scope"]) for row in lexical).items())),
        "active_weak_readings": active_levels["W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY"] + active_levels["W1_WEAK_WORKING"],
        "remaining_unreviewed_weak_readings": sum(row["v86_audit_decision"] == "HELD_FOR_LATER_REPAIR" for row in census),
        "complete_readings": len(complete), "complete_surfaces": len({row["surface"] for row in complete}),
        "complete_level_counts": dict(sorted(complete_levels.items())),
        "family_evidence_rows": len(families), "bound_span_renderers": len(bound_spans),
        "historical_confirmation_counts": dict(sorted(Counter(str(row["historical_confirmation"]) for row in complete).items())),
        "relation_word_credit_gdt713": 0, "new_pages": 0, "f84_or_f84r_used": 0,
    }
    (ART / "RESULT.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (EXP / "REPORT.md").write_text(report_text(result), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
