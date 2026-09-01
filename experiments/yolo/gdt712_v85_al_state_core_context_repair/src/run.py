#!/usr/bin/env python3
"""Build V85 by repairing the AL and state/carrier weak-reading tranche."""

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
EXP = ROOT / "experiments/yolo/gdt712_v85_al_state_core_context_repair"
SRC = EXP / "src"
ART = EXP / "artifacts"
G711 = ROOT / "experiments/yolo/gdt711_v84_active_weak_family_repair/artifacts"

SOURCE_LEXICAL = G711 / "V84_324_ACTIVE_LEXICAL_READINGS.tsv"
SOURCE_CONTEXT = G711 / "V84_479_CONTEXT_REALIZATIONS.tsv"
SOURCE_COMPLETE = G711 / "V84_COMPLETE_WORD_CONFIDENCE.tsv"
SOURCE_CENSUS = G711 / "V84_181_WEAK_READING_REPAIR_CENSUS.tsv"
SOURCE_FAMILIES = G711 / "V84_13_STEM_FAMILY_EVIDENCE.tsv"
SPECS = SRC / "V85_33_AUDIT_SPECS.tsv"

HISTORICAL = "H0_NONE"
STATUS = (
    "PASS_V85_33_AL_STATE_READINGS_AUDITED__30_REVISED_3_HELD__"
    "38_POSITIONS_23_PAGES__8_W0_149_W1_148_W2_19_W3__"
    "CHEOP_OL_LEFT_RIGHT_BOUND__ALL_H0_NONE"
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


def v85_key(value: str) -> str:
    return value.replace("v84", "v85").replace("V84", "V85")


def rename_v84_fields(row: dict[str, str]) -> dict[str, str]:
    return {v85_key(key): value for key, value in row.items()}


def lexical_rows(
    source_rows: list[dict[str, str]], specs: list[dict[str, str]]
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    specs_by_id = {row["source_reading_id"]: row for row in specs}
    output: list[dict[str, Any]] = []
    for source in source_rows:
        row: dict[str, Any] = rename_v84_fields(source)
        source_ids = split_pipe(source["source_reading_ids"])
        spec = specs_by_id.get(source_ids[0]) if len(source_ids) == 1 else None
        if spec:
            assert source["v84_lexical_core_de"] == spec["old_lexical_core_de"]
            base = int(source["working_model_score_0_100_not_probability"])
            score = min(base + int(spec["score_delta_lexical_core"]), int(spec["lexical_core_cap"]))
            context_score = min(score, int(spec["context_realization_cap"]))
            row.update({
                "v85_lexical_core_de": spec["v85_lexical_core_de"],
                "v85_context_realizations_de": spec["v85_context_realization_de"],
                "family_ids": spec["family_ids"],
                "decomposition": spec["decomposition"],
                "repair_modes": spec["repair_mode"],
                "resolved_debt_atoms": spec["resolved_debt_atom"],
                "last_semantic_writer": "GDT712",
                "base_score": base,
                "score_delta_lexical_core": spec["score_delta_lexical_core"],
                "lexical_core_cap": spec["lexical_core_cap"],
                "working_model_score_0_100_not_probability": score,
                "working_model_level": level(score),
                "context_realization_cap": spec["context_realization_cap"],
                "context_realization_score_0_100_not_probability": context_score,
                "context_realization_level": level(context_score),
                "source_gdts": append_pipe(source["source_gdts"], "GDT712"),
                "positive_evidence_de": (
                    "GDT712 trennt erneut Wortkern und lokale Realisierung: "
                    + spec["evidence_de"] + " || " + source["positive_evidence_de"]
                ),
                "counterevidence_de": (
                    "GDT712 Gegenbeleg: " + spec["counterevidence_de"]
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
                "v85_audit_decision": spec["decision"],
                "v85_evidence_class": spec["evidence_class"],
                "v85_open_semantic_slots": spec["open_semantic_slots"],
                "v85_component_global_export_allowed": spec["component_global_export_allowed"],
                "v85_prior_lexical_core_de": source["v84_lexical_core_de"],
            })
        else:
            row.update({
                "v85_audit_decision": "NOT_IN_GDT712_TRANCHE",
                "v85_evidence_class": "INHERITED_V84",
                "v85_open_semantic_slots": "NOT_EVALUATED",
                "v85_component_global_export_allowed": "NOT_EVALUATED",
                "v85_prior_lexical_core_de": source["v84_lexical_core_de"],
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
        row: dict[str, Any] = rename_v84_fields(source)
        source_id = source["source_reading_id"]
        lexical = lexical_by_source[source_id]
        spec = specs_by_id.get(source_id)
        row.update({
            "v85_reading_id": lexical["v85_reading_id"],
            "v85_lexical_core_de": lexical["v85_lexical_core_de"],
            "v85_context_realization_de": spec["v85_context_realization_de"] if spec else source["v84_context_realization_de"],
            "v85_repair_mode": spec["repair_mode"] if spec else source["v84_repair_mode"],
            "v85_resolved_debt_atom": spec["resolved_debt_atom"] if spec else source["v84_resolved_debt_atom"],
            "v85_lexical_score": lexical["working_model_score_0_100_not_probability"],
            "v85_lexical_level": lexical["working_model_level"],
            "v85_context_score": lexical["context_realization_score_0_100_not_probability"],
            "v85_context_level": lexical["context_realization_level"],
            "v85_semantic_scope": lexical["semantic_scope"],
            "v85_semantic_applicability": lexical["semantic_applicability"],
            "v85_global_export_scope": lexical["global_export_scope"],
            "v85_lexical_bound_span_ids": lexical["bound_span_ids"],
            "v85_unconditional_global_export_allowed": lexical["unconditional_global_export_allowed"],
            "v85_historical_confirmation": HISTORICAL,
            "v85_audit_decision": spec["decision"] if spec else "NOT_IN_GDT712_TRANCHE",
            "v85_evidence_class": spec["evidence_class"] if spec else "INHERITED_V84",
            "v85_open_semantic_slots": spec["open_semantic_slots"] if spec else "NOT_EVALUATED",
            "v85_component_global_export_allowed": spec["component_global_export_allowed"] if spec else "NOT_EVALUATED",
        })
        if spec and spec["occurrence_bound_span_override"] != "NONE":
            row.update({
                "v85_occurrence_bound_span_id": spec["occurrence_bound_span_override"],
                "v85_occurrence_bound_span_role": spec["occurrence_bound_span_role_override"],
                "v85_occurrence_bound_span_global_export_allowed": spec["occurrence_bound_span_export_override"],
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
        row: dict[str, Any] = rename_v84_fields(source)
        source_id = source["source_reading_id"]
        lexical = lexical_by_source[source_id]
        spec = specs_by_id.get(source_id)
        if spec:
            row.update({
                "disposition": "REVISED_IN_V85" if spec["decision"] == "REVISE" else "AUDITED_HOLD_IN_V85",
                "repair_mode": spec["repair_mode"],
                "resolved_debt_atom": spec["resolved_debt_atom"],
                "v85_reading_id": lexical["v85_reading_id"],
                "v85_lexical_core_de": lexical["v85_lexical_core_de"],
                "v85_context_realization_de": spec["v85_context_realization_de"],
                "new_lexical_score": lexical["working_model_score_0_100_not_probability"],
                "new_lexical_level": lexical["working_model_level"],
                "new_context_score": lexical["context_realization_score_0_100_not_probability"],
                "new_context_level": lexical["context_realization_level"],
                "positive_evidence_de": spec["evidence_de"],
                "counterevidence_de": spec["counterevidence_de"],
                "v85_audit_decision": spec["decision"],
                "v85_evidence_class": spec["evidence_class"],
                "v85_open_semantic_slots": spec["open_semantic_slots"],
            })
        else:
            row.update({
                "v85_reading_id": lexical["v85_reading_id"],
                "v85_lexical_core_de": lexical["v85_lexical_core_de"],
                "v85_context_realization_de": lexical["v85_context_realizations_de"],
                "new_lexical_score": lexical["working_model_score_0_100_not_probability"],
                "new_lexical_level": lexical["working_model_level"],
                "new_context_score": lexical["context_realization_score_0_100_not_probability"],
                "new_context_level": lexical["context_realization_level"],
                "v85_audit_decision": "HELD_FOR_LATER_REPAIR",
                "v85_evidence_class": "INHERITED_V84",
                "v85_open_semantic_slots": "NOT_EVALUATED",
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
            "old_lexical_core_de": source["v84_lexical_core_de"],
            "v85_lexical_core_de": target["v85_lexical_core_de"],
            "v85_context_realization_de": spec["v85_context_realization_de"],
            "old_score": source["working_model_score_0_100_not_probability"],
            "v85_score": target["working_model_score_0_100_not_probability"],
            "old_level": source["working_model_level"],
            "v85_level": target["working_model_level"],
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
            "v85_semantic_scope": target["semantic_scope"],
            "old_global_export_scope": source["global_export_scope"],
            "v85_global_export_scope": target["global_export_scope"],
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
        row: dict[str, Any] = rename_v84_fields(source)
        selected = specs_by_family[family]
        selected_ids = [spec["source_reading_id"] for spec in selected]
        selected_positions = [position for source_id in selected_ids for position in occurrences[source_id]]
        row.update({
            "selected_source_readings": len(selected_ids),
            "selected_lexical_readings": len({lexical_by_source[source_id]["v85_reading_id"] for source_id in selected_ids}),
            "selected_positions": len(selected_positions),
            "selected_pages": len({position["page"] for position in selected_positions}),
            "selected_source_reading_ids": ordered_compact(selected_ids),
            "selected_surfaces": ordered_compact(sorted({position["surface"] for position in selected_positions})),
            "selected_v85_reading_ids": ordered_compact(sorted({str(lexical_by_source[source_id]["v85_reading_id"]) for source_id in selected_ids})),
            "selected_v85_levels": ordered_compact(sorted({str(lexical_by_source[source_id]["working_model_level"]) for source_id in selected_ids})),
            "automatic_historical_credit": 0,
            "historical_confirmation": HISTORICAL,
            "v85_decisions": ordered_compact(spec["decision"] for spec in selected),
        })
        output.append(row)
    return output


def complete_rows(source_rows: list[dict[str, str]], lexical: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for source in source_rows:
        if source["current_layer"] == "ACTIVE_V84_LEXICAL_CORE":
            continue
        row: dict[str, Any] = rename_v84_fields(source)
        row.update({
            "v85_audit_decision": "OUTSIDE_ACTIVE_V85_TRANCHE",
            "v85_evidence_class": "INHERITED_GLOBAL_V48",
            "v85_open_semantic_slots": "NOT_EVALUATED",
            "v85_component_global_export_allowed": "NOT_EVALUATED",
        })
        output.append(row)
    for row in lexical:
        output.append({
            "surface": row["surface"],
            "reading_id": row["v85_reading_id"],
            "working_meaning_de": row["v85_lexical_core_de"],
            "current_layer": "ACTIVE_V85_LEXICAL_CORE",
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
            "v85_context_realizations_de": row["v85_context_realizations_de"],
            "source_reading_ids": row["source_reading_ids"],
            "v85_audit_decision": row["v85_audit_decision"],
            "v85_evidence_class": row["v85_evidence_class"],
            "v85_open_semantic_slots": row["v85_open_semantic_slots"],
            "v85_component_global_export_allowed": row["v85_component_global_export_allowed"],
        })
    return sorted(output, key=lambda item: (str(item["surface"]), str(item["reading_id"])))


def report_text(result: dict[str, Any]) -> str:
    return f"""# GDT712 — V85 AL/state core-context repair

Status: `{STATUS}`

## Ergebnis

V85 arbeitet die naechsten 33 schwachen Lesungen vollstaendig ab: alle 15 AL-/DAL-nahe Formen und alle 18 Zustands-/Traegerformen, zusammen 38 unveraenderte Positionen auf 23 bereits zugelassenen Seiten. 30 Lesungen werden kompakter oder in Wortkern und lokale Realisierung getrennt; drei konkrete, aber ausserhalb des produktiven Gradrasters liegende Ganzwoerter (`keeey`, `qokeeey`, `okol`) bleiben stehen.

Die wichtigste neue Defaultregel lautet `AL -> Material I` und, nur in den zugelassenen DAL-Schwestern, `DAL -> abgemessenes Material I`. Dadurch verschwinden `Rohstoffklasse`, `Rohdroge`, `Drogenrohstoff`, erfundene Dosis- und Mengenkoepfe, ohne eine konkrete Zutat einzusetzen. Zehn atlasgestuetzte Formen erhalten den vorhandenen F_AL-Familienkredit; fuenf spaetere Ganzformen werden nur lexikalisch bereinigt und nicht hochgestuft.

Bei den Zustandsformen bleibt die greifbare Information sichtbar: heiß, kalt, trocken, feucht sowie Anfang, Mitte, Ende und Wert II/III. `Droge`, `Gut` und aktive Prozessformulierungen werden dort entfernt, wo die aktuelle Position nur einen nominalen Zustand traegt. Strukturelle Restfragen stehen separat in `v85_open_semantic_slots`, nicht in der deutschen Uebersetzung.

## Wichtige Einzelkorrektur

Die einzige `cheop`-Position ist nach beiden Alternativlesern die linke Haelfte von `cheop ol`. V85 markiert deshalb f115r.1#5 als `G683_CHEOP_OL LEFT`; das bereits gebundene `ol#2` bleibt RIGHT. Der lokale Span rendert einmal als `bis zur Mittelstufe getrockneter Pulverstoff`, beide Komponenten sind nicht global exportierbar. Freies `ol#1` bleibt unveraendert.

## Bestand

- auditierte Lesungen / Positionen / Seiten: {result['audited_readings']} / {result['audited_positions']} / {result['audited_pages']}
- revidiert / bewusst gehalten: {result['revised_readings']} / {result['held_readings']}
- aktive Lesungen / Positionen: {result['active_lexical_readings']} / {result['active_positions']}
- aktive Confidence-Stufen: `{json.dumps(result['active_level_counts'], ensure_ascii=False, sort_keys=True)}`
- komplettes Woerterbuch: {result['complete_surfaces']} Oberflaechen / {result['complete_readings']} Lesungen
- noch nicht in V84/V85 einzeln bearbeitete schwache Lesungen: {result['remaining_unreviewed_weak_readings']}

## Grenze

Das ist die konkrete Arbeitsuebersetzung des aktuellen Modells, kein bestaetigter Klartext. Confidence bleibt ein interner Evidenzindex, keine Wahrscheinlichkeit. Keine Komponente wird als freies Voynich-Wort exportiert; alle historischen Felder bleiben `H0_NONE`. Es wurden keine neue Seite, kein Bild, keine neue Transkription, kein `f84` und kein `f84r` benutzt.
"""


def main() -> int:
    source_lexical = read_tsv(SOURCE_LEXICAL)
    source_context = read_tsv(SOURCE_CONTEXT)
    source_complete = read_tsv(SOURCE_COMPLETE)
    source_census = read_tsv(SOURCE_CENSUS)
    source_families = read_tsv(SOURCE_FAMILIES)
    specs = read_tsv(SPECS)

    assert (len(source_lexical), len(source_context), len(source_complete), len(source_census), len(source_families), len(specs)) == (324, 479, 1586, 181, 13, 33)
    assert len({row["source_reading_id"] for row in specs}) == 33
    assert Counter(row["decision"] for row in specs) == Counter({"REVISE": 30, "HOLD": 3})
    assert all(row["component_global_export_allowed"] == "0" for row in specs)
    assert all(not row["page"].startswith("f84") and not row["locus"].startswith("f84") for row in source_context)

    lexical, lexical_by_source = lexical_rows(source_lexical, specs)
    contexts = context_rows(source_context, specs, lexical_by_source)
    census = census_rows(source_census, specs, lexical_by_source)
    delta = delta_rows(specs, source_lexical, lexical_by_source, source_context)
    families = family_rows(source_families, specs, source_context, lexical_by_source)
    complete = complete_rows(source_complete, lexical)
    bound_spans = [{
        "bound_span_id": "G683_CHEOP_OL", "page": "f115r", "locus": "f115r.1",
        "left_position_id": "P167", "left_surface": "cheop", "left_reading_id": "cheop#1", "left_role": "LEFT",
        "right_position_id": "P168", "right_surface": "ol", "right_reading_id": "ol#2", "right_role": "RIGHT",
        "render_once_de": "bis zur Mittelstufe getrockneter Pulverstoff",
        "source_gdts": "GDT683|GDT711|GDT712", "global_export_allowed": 0,
        "historical_confirmation": HISTORICAL,
    }]

    target_ids = {row["source_reading_id"] for row in specs}
    selected_positions = [row for row in source_context if row["source_reading_id"] in target_ids]
    active_levels = Counter(str(row["working_model_level"]) for row in lexical)
    complete_levels = Counter(str(row["working_model_level"]) for row in complete)
    assert len(selected_positions) == 38 and len({row["page"] for row in selected_positions}) == 23
    assert len(census) == 151 and len(families) == 7
    assert len(complete) == 1586 and len({row["surface"] for row in complete}) == 1582
    assert active_levels == Counter({
        "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY": 8, "W1_WEAK_WORKING": 149,
        "W2_PROVISIONAL_WORKING": 148, "W3_SOLID_WORKING_THEORY": 19,
    })
    assert complete_levels == Counter({
        "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY": 288, "W1_WEAK_WORKING": 329,
        "W2_PROVISIONAL_WORKING": 526, "W3_SOLID_WORKING_THEORY": 443,
    })

    lexical_fields = [v85_key(field) for field in source_lexical[0]] + [
        "v85_audit_decision", "v85_evidence_class", "v85_open_semantic_slots",
        "v85_component_global_export_allowed", "v85_prior_lexical_core_de",
    ]
    context_fields = [v85_key(field) for field in source_context[0]] + [
        "v85_audit_decision", "v85_evidence_class", "v85_open_semantic_slots",
        "v85_component_global_export_allowed",
    ]
    census_fields = [v85_key(field) for field in source_census[0]] + [
        "v85_audit_decision", "v85_evidence_class", "v85_open_semantic_slots",
    ]
    family_fields = [v85_key(field) for field in source_families[0]] + ["v85_decisions"]
    complete_fields = [v85_key(field) for field in source_complete[0]] + [
        "v85_audit_decision", "v85_evidence_class", "v85_open_semantic_slots",
        "v85_component_global_export_allowed",
    ]
    write_tsv(ART / "V85_324_ACTIVE_LEXICAL_READINGS.tsv", lexical_fields, lexical)
    write_tsv(ART / "V85_479_CONTEXT_REALIZATIONS.tsv", context_fields, contexts)
    write_tsv(ART / "V85_151_HELD_READING_AUDIT.tsv", census_fields, census)
    write_tsv(ART / "V85_33_AL_STATE_CORE_CONTEXT_DELTA.tsv", list(delta[0]), delta)
    write_tsv(ART / "V85_7_FAMILY_EVIDENCE.tsv", family_fields, families)
    write_tsv(ART / "V85_1_BOUND_SPAN_RENDERER.tsv", list(bound_spans[0]), bound_spans)
    write_tsv(ART / "V85_COMPLETE_WORD_CONFIDENCE.tsv", complete_fields, complete)

    result = {
        "experiment_id": "GDT712", "status": STATUS,
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
        "remaining_unreviewed_weak_readings": sum(row["v85_audit_decision"] == "HELD_FOR_LATER_REPAIR" for row in census),
        "complete_readings": len(complete), "complete_surfaces": len({row["surface"] for row in complete}),
        "complete_level_counts": dict(sorted(complete_levels.items())),
        "family_evidence_rows": len(families), "bound_span_renderers": len(bound_spans),
        "historical_confirmation_counts": dict(sorted(Counter(str(row["historical_confirmation"]) for row in complete).items())),
        "relation_word_credit_gdt712": 0, "new_pages": 0, "f84_or_f84r_used": 0,
    }
    (ART / "RESULT.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (EXP / "REPORT.md").write_text(report_text(result), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
