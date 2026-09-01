#!/usr/bin/env python3
"""Build V90 by separating seven quality/stage cores from product heads."""

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
EXP = ROOT / "experiments/yolo/gdt717_v90_quality_stage_core_context_repair"
SRC = EXP / "src"
ART = EXP / "artifacts"
G716 = ROOT / "experiments/yolo/gdt716_v89_indexed_share_core_context_repair/artifacts"
G711 = ROOT / "experiments/yolo/gdt711_v84_active_weak_family_repair/artifacts"

SOURCE_LEXICAL = G716 / "V89_324_ACTIVE_LEXICAL_READINGS.tsv"
SOURCE_CONTEXT = G716 / "V89_479_CONTEXT_REALIZATIONS.tsv"
SOURCE_COMPLETE = G716 / "V89_COMPLETE_WORD_CONFIDENCE.tsv"
SOURCE_CENSUS = G716 / "V89_84_HELD_READING_AUDIT.tsv"
SOURCE_SPANS = G716 / "V89_2_BOUND_SPAN_RENDERER.tsv"
SOURCE_FAMILIES = G711 / "V84_13_STEM_FAMILY_EVIDENCE.tsv"
SPECS = SRC / "V90_7_AUDIT_SPECS.tsv"
BINDINGS = SRC / "V90_34_PRIMARY_EVIDENCE_BINDINGS.tsv"

HISTORICAL = "H0_NONE"
STATUS = (
    "PASS_V90_7_QUALITY_STAGE_READINGS_REVISED__5_GRID_PLUS_2_SISTER_WHOLES__"
    "7_POSITIONS_7_PAGES__64_WEAK_READINGS_REMAIN__F7R2_RERENDERED__ALL_H0_NONE"
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, fields: list[str], rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def split_pipe(value: str) -> list[str]:
    return [part.strip() for part in value.split("|") if part.strip() and part.strip() not in {"NONE", "0"}]


def parse_assertions(value: str) -> dict[str, str]:
    output: dict[str, str] = {}
    for part in value.split(";"):
        if not part:
            continue
        field, expected = part.split("=", 1)
        assert field and field not in output
        output[field] = expected
    return output


def ordered_compact(values: Iterable[str], empty: str = "NONE") -> str:
    output: list[str] = []
    seen: set[str] = set()
    for raw in values:
        value = str(raw).strip()
        if value and value not in {"NONE", "0"} and value not in seen:
            seen.add(value)
            output.append(value)
    return "|".join(output) if output else empty


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


def v90_key(value: str) -> str:
    return value.replace("v89", "v90").replace("V89", "V90")


def rename_v89_fields(row: dict[str, str]) -> dict[str, str]:
    return {v90_key(key): value for key, value in row.items()}


def family_v90_key(value: str) -> str:
    return value.replace("v84", "v90").replace("V84", "V90")


def resolve_evidence(
    bindings: list[dict[str, str]], specs: list[dict[str, str]], source_families: list[dict[str, str]]
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    spec_ids = {row["source_reading_id"] for row in specs}
    credits: dict[str, list[str]] = defaultdict(list)
    output: list[dict[str, Any]] = []
    for binding in bindings:
        assert binding["source_reading_id"] in spec_ids
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
        credits[binding["source_reading_id"]].extend(split_pipe(binding["score_credit_family_ids"]))
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
    bonuses = {row["family_id"]: int(row["family_bonus"]) for row in source_families}
    deltas: dict[str, int] = {}
    for spec in specs:
        source_id = spec["source_reading_id"]
        families = credits[source_id]
        assert len(families) == len(set(families))
        assert set(families) == set(split_pipe(spec["score_credit_family_ids"]))
        deltas[source_id] = sum(bonuses[family] for family in families)
        assert deltas[source_id] == int(spec["score_delta_lexical_core"])
    return output, deltas


def build_lexical(
    source_rows: list[dict[str, str]], specs: list[dict[str, str]], deltas: dict[str, int]
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    specs_by_id = {row["source_reading_id"]: row for row in specs}
    output: list[dict[str, Any]] = []
    for source in source_rows:
        row: dict[str, Any] = rename_v89_fields(source)
        source_ids = split_pipe(source["source_reading_ids"])
        spec = specs_by_id.get(source_ids[0]) if len(source_ids) == 1 else None
        if spec:
            assert source["v89_lexical_core_de"] == spec["old_lexical_core_de"]
            base = int(source["working_model_score_0_100_not_probability"])
            score_delta = deltas[spec["source_reading_id"]]
            score = min(base + score_delta, int(spec["lexical_core_cap"]))
            context_score = min(score, int(spec["context_realization_cap"]))
            row.update({
                "v90_lexical_core_de": spec["v90_lexical_core_de"],
                "v90_context_realizations_de": spec["v90_context_realization_de"],
                "family_ids": spec["family_ids"],
                "decomposition": spec["decomposition"],
                "repair_modes": spec["repair_mode"],
                "resolved_debt_atoms": spec["resolved_debt_atom"],
                "last_semantic_writer": "GDT717",
                "base_score": base,
                "score_delta_lexical_core": score_delta,
                "lexical_core_cap": spec["lexical_core_cap"],
                "working_model_score_0_100_not_probability": score,
                "working_model_level": level(score),
                "context_realization_cap": spec["context_realization_cap"],
                "context_realization_score_0_100_not_probability": context_score,
                "context_realization_level": level(context_score),
                "source_gdts": append_pipe(source["source_gdts"], "GDT717"),
                "positive_evidence_de": (
                    "GDT717 trennt den wiederholten Qualitaets-/Stufenkern vom Produktkopf: "
                    + spec["evidence_de"] + " || " + source["positive_evidence_de"]
                ),
                "counterevidence_de": (
                    "GDT717 Gegenbeleg: " + spec["counterevidence_de"]
                    + " || Historisch unbestaetigte Arbeitstheorie; keine Klartextidentifikation."
                ),
                "v90_audit_decision": "REVISE",
                "v90_evidence_class": spec["evidence_class"],
                "v90_open_semantic_slots": spec["open_semantic_slots"],
                "v90_component_global_export_allowed": "0",
                "v90_prior_lexical_core_de": source["v89_lexical_core_de"],
            })
        else:
            row.update({
                "v90_audit_decision": "NOT_IN_GDT717_TRANCHE",
                "v90_evidence_class": "INHERITED_V89",
                "v90_open_semantic_slots": "NOT_EVALUATED",
                "v90_component_global_export_allowed": "NOT_EVALUATED",
                "v90_prior_lexical_core_de": source["v89_lexical_core_de"],
            })
        output.append(row)
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
        spec = specs_by_id.get(source_id)
        lexical = lexical_by_source[source_id]
        row: dict[str, Any] = rename_v89_fields(source)
        if spec:
            seen[source_id] += 1
            assert (source["position_id"], source["page"], source["locus"], source["token_ordinal"]) == (
                spec["expected_position_id"], spec["expected_page"], spec["expected_locus"], spec["expected_token_ordinal"]
            )
            ordinal = int(source["token_ordinal"])
            left = "<BOS>" if ordinal == 1 else by_locus_ordinal[(source["locus"], ordinal - 1)]["surface"]
            assert left == spec["expected_left_surface"]
        row.update({
            "v90_reading_id": lexical["v90_reading_id"],
            "v90_lexical_core_de": lexical["v90_lexical_core_de"],
            "v90_context_realization_de": spec["v90_context_realization_de"] if spec else source["v89_context_realization_de"],
            "v90_repair_mode": spec["repair_mode"] if spec else source["v89_repair_mode"],
            "v90_resolved_debt_atom": spec["resolved_debt_atom"] if spec else source["v89_resolved_debt_atom"],
            "v90_lexical_score": lexical["working_model_score_0_100_not_probability"],
            "v90_lexical_level": lexical["working_model_level"],
            "v90_context_score": lexical["context_realization_score_0_100_not_probability"],
            "v90_context_level": lexical["context_realization_level"],
            "v90_semantic_scope": lexical["semantic_scope"],
            "v90_semantic_applicability": lexical["semantic_applicability"],
            "v90_global_export_scope": lexical["global_export_scope"],
            "v90_lexical_bound_span_ids": lexical["bound_span_ids"],
            "v90_unconditional_global_export_allowed": lexical["unconditional_global_export_allowed"],
            "v90_historical_confirmation": HISTORICAL,
            "v90_audit_decision": "REVISE" if spec else "NOT_IN_GDT717_TRANCHE",
            "v90_evidence_class": spec["evidence_class"] if spec else "INHERITED_V89",
            "v90_open_semantic_slots": spec["open_semantic_slots"] if spec else "NOT_EVALUATED",
            "v90_component_global_export_allowed": "0" if spec else "NOT_EVALUATED",
            "v90_local_context_hypothesis": spec["local_context_hypothesis"] if spec else "NONE",
            "v90_expected_left_surface": spec["expected_left_surface"] if spec else "NONE",
        })
        output.append(row)
    assert seen == Counter({row["source_reading_id"]: 1 for row in specs})
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
        spec = specs_by_id.get(source_id)
        lexical = lexical_by_source[source_id]
        row: dict[str, Any] = rename_v89_fields(source)
        if spec:
            row.update({
                "disposition": "REVISED_IN_V90",
                "repair_mode": spec["repair_mode"],
                "resolved_debt_atom": spec["resolved_debt_atom"],
                "v90_reading_id": lexical["v90_reading_id"],
                "v90_lexical_core_de": lexical["v90_lexical_core_de"],
                "v90_context_realization_de": spec["v90_context_realization_de"],
                "new_lexical_score": lexical["working_model_score_0_100_not_probability"],
                "new_lexical_level": lexical["working_model_level"],
                "new_context_score": lexical["context_realization_score_0_100_not_probability"],
                "new_context_level": lexical["context_realization_level"],
                "positive_evidence_de": spec["evidence_de"],
                "counterevidence_de": spec["counterevidence_de"],
                "v90_audit_decision": "REVISE",
                "v90_evidence_class": spec["evidence_class"],
                "v90_open_semantic_slots": spec["open_semantic_slots"],
            })
        else:
            row.update({
                "v90_reading_id": lexical["v90_reading_id"],
                "v90_lexical_core_de": lexical["v90_lexical_core_de"],
                "v90_context_realization_de": lexical["v90_context_realizations_de"],
                "new_lexical_score": lexical["working_model_score_0_100_not_probability"],
                "new_lexical_level": lexical["working_model_level"],
                "new_context_score": lexical["context_realization_score_0_100_not_probability"],
                "new_context_level": lexical["context_realization_level"],
                "v90_audit_decision": "HELD_FOR_LATER_REPAIR",
                "v90_evidence_class": "INHERITED_V89",
                "v90_open_semantic_slots": "NOT_EVALUATED",
            })
        output.append(row)
    return output


def build_delta(
    specs: list[dict[str, str]], source_lexical: list[dict[str, str]], target_by_source: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    source_by_id = {source_id: row for row in source_lexical for source_id in split_pipe(row["source_reading_ids"])}
    output: list[dict[str, Any]] = []
    for spec in specs:
        source = source_by_id[spec["source_reading_id"]]
        target = target_by_source[spec["source_reading_id"]]
        output.append({
            "source_reading_id": spec["source_reading_id"], "surface": source["surface"],
            "position_id": spec["expected_position_id"], "page": spec["expected_page"],
            "locus": spec["expected_locus"], "token_ordinal": spec["expected_token_ordinal"],
            "left_surface": spec["expected_left_surface"], "old_lexical_core_de": source["v89_lexical_core_de"],
            "v90_lexical_core_de": target["v90_lexical_core_de"],
            "v90_context_realization_de": spec["v90_context_realization_de"],
            "old_score": source["working_model_score_0_100_not_probability"],
            "v90_score": target["working_model_score_0_100_not_probability"],
            "old_level": source["working_model_level"], "v90_level": target["working_model_level"],
            "family_ids": spec["family_ids"], "score_credit_family_ids": spec["score_credit_family_ids"],
            "decomposition": spec["decomposition"], "repair_mode": spec["repair_mode"],
            "resolved_debt_atom": spec["resolved_debt_atom"], "evidence_class": spec["evidence_class"],
            "evidence_de": spec["evidence_de"], "counterevidence_de": spec["counterevidence_de"],
            "open_semantic_slots": spec["open_semantic_slots"],
            "local_context_hypothesis": spec["local_context_hypothesis"],
            "component_global_export_allowed": "0", "historical_confirmation": HISTORICAL,
        })
    return output


def build_families(
    source_families: list[dict[str, str]], specs: list[dict[str, str]], target_by_source: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for family_id in ("F_STATE", "F_STAGE"):
        selected = [spec for spec in specs if family_id in split_pipe(spec["score_credit_family_ids"])]
        source = next(row for row in source_families if row["family_id"] == family_id)
        row: dict[str, Any] = {family_v90_key(key): value for key, value in source.items()}
        row.update({
            "selected_source_readings": len(selected), "selected_lexical_readings": len(selected),
            "selected_positions": len(selected), "selected_pages": len({spec["expected_page"] for spec in selected}),
            "selected_source_reading_ids": ordered_compact(spec["source_reading_id"] for spec in selected),
            "selected_surfaces": ordered_compact(target_by_source[spec["source_reading_id"]]["surface"] for spec in selected),
            "selected_v90_reading_ids": ordered_compact(target_by_source[spec["source_reading_id"]]["v90_reading_id"] for spec in selected),
            "selected_v90_levels": ordered_compact(target_by_source[spec["source_reading_id"]]["working_model_level"] for spec in selected),
            "automatic_historical_credit": 0, "historical_confirmation": HISTORICAL,
            "v90_decisions": "REVISE",
        })
        output.append(row)
    return output


def build_complete(source_rows: list[dict[str, str]], lexical: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for source in source_rows:
        if source["current_layer"] == "ACTIVE_V89_LEXICAL_CORE":
            continue
        row: dict[str, Any] = rename_v89_fields(source)
        row.update({
            "v90_audit_decision": "OUTSIDE_ACTIVE_V90_TRANCHE",
            "v90_evidence_class": "INHERITED_GLOBAL_V48",
            "v90_open_semantic_slots": "NOT_EVALUATED",
            "v90_component_global_export_allowed": "NOT_EVALUATED",
        })
        output.append(row)
    for row in lexical:
        output.append({
            "surface": row["surface"], "reading_id": row["v90_reading_id"],
            "working_meaning_de": row["v90_lexical_core_de"], "current_layer": "ACTIVE_V90_LEXICAL_CORE",
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
            "v90_context_realizations_de": row["v90_context_realizations_de"],
            "source_reading_ids": row["source_reading_ids"], "v90_audit_decision": row["v90_audit_decision"],
            "v90_evidence_class": row["v90_evidence_class"], "v90_open_semantic_slots": row["v90_open_semantic_slots"],
            "v90_component_global_export_allowed": row["v90_component_global_export_allowed"],
        })
    return sorted(output, key=lambda row: (str(row["surface"]), str(row["reading_id"])))


def build_directives(contexts: list[dict[str, Any]], spans: list[dict[str, str]]) -> list[dict[str, Any]]:
    span = next(row for row in spans if row["locus"] == "f7r.2")
    by_position = {str(row["position_id"]): row for row in contexts}
    output: list[dict[str, Any]] = []
    for side, action in (("left", "EMIT_SPAN_ONCE"), ("right", "CONSUME_NO_OUTPUT")):
        source = by_position[span[f"{side}_position_id"]]
        output.append({
            "render_unit_id": f"R_{span['bound_span_id']}", "page": span["page"], "locus": span["locus"],
            "bound_span_id": span["bound_span_id"], "anchor_position_id": span["left_position_id"],
            "source_position_id": source["position_id"], "source_token_ordinal": source["token_ordinal"],
            "source_surface": source["surface"], "source_reading_id": source["source_reading_id"],
            "span_role": span[f"{side}_role"], "render_action": action,
            "emitted_text_de": span["render_once_de"] if side == "left" else "",
            "source_context_consumed": 1, "global_export_allowed": span["global_export_allowed"],
        })
    return output


def render_f7r2(contexts: list[dict[str, Any]], directives: list[dict[str, Any]]) -> list[dict[str, Any]]:
    source_rows = sorted((row for row in contexts if row["locus"] == "f7r.2"), key=lambda row: int(row["token_ordinal"]))
    by_position = {row["source_position_id"]: row for row in directives}
    output: list[dict[str, Any]] = []
    for source in source_rows:
        directive = by_position.get(str(source["position_id"]))
        if directive and directive["render_action"] == "CONSUME_NO_OUTPUT":
            continue
        if directive:
            rendered = directive["emitted_text_de"]
            source_kind, source_ref = "BOUND_SPAN", directive["bound_span_id"]
            positions, surfaces = "P288|P289", "keo|r"
        else:
            rendered = source["v90_context_realization_de"]
            source_kind, source_ref = "CONTEXT_POSITION", source["position_id"]
            positions, surfaces = source["position_id"], source["surface"]
        output.append({
            "output_ordinal": len(output) + 1, "page": source["page"], "locus": source["locus"],
            "source_kind": source_kind, "source_ref": source_ref, "anchor_position_id": source["position_id"],
            "consumed_position_ids": positions, "source_surfaces": surfaces,
            "rendered_text_de": rendered, "historical_confirmation": HISTORICAL,
        })
    return output


def report_text(result: dict[str, Any], delta: list[dict[str, Any]]) -> str:
    table = "\n".join(
        f"| `{row['surface']}` | {row['v90_lexical_core_de']} | {row['v90_context_realization_de']} | {row['old_score']}→{row['v90_score']} |"
        for row in delta
    )
    return f"""# GDT717 — V90 quality/stage core-context repair

Status: `{STATUS}`

## Ergebnis

Sieben singletonlastige Produktformulierungen werden auf ein wiederholtes,
vorhersagbares Zustands-/Stufenmodell zurueckgefuehrt. Der portable Kern sagt
heiß/kalt, trocken/feucht und Anfang/Mitte/erreicht; der konkrete
Zubereitungskopf bleibt nur in der Fundstellenausgabe.

| Form | portabler Kern | konkrete Fundstelle | Score |
|---|---|---|---:|
{table}

`otchy/otchey/otchdy` bilden Anfang, Mitte und erreichte Anfangsstufe derselben
kalt-trockenen O-Rahmenfamilie. `okchedy` liefert die heiß-trockene erreichte
Mittelzelle, `otshey` die kalt-feuchte offene Mittelzelle. Diese fuenf Karten
erhalten je einmal `F_STATE +4` und `F_STAGE +4`.

`chody` und `sheody` behalten ihre exakten GDT689-Schwesterresultate, aber ihr
sichtbares `dy` ist kein formales DY. Deshalb erhalten sie nur `F_STATE +4` und
keinen Stufenbonus. Kein Ziel erhaelt Punkte fuer geloeschtes `Ansatz`,
`Zubereitung`, `Mazerat` oder fluessigere Prosa; alle sieben bleiben W1.

## Bestand

- 7 Lesungen / 7 Positionen / 7 Seiten
- {result['primary_evidence_bindings']} exakt aufgeloeste Primaerevidenzbindungen
- 317 nicht betroffene Kerne und 472 nicht betroffene Kontexte unveraendert
- beide Spans erhalten; f7r.2 erneut als acht Einheiten ausgegeben
- V90 aktiv: `{json.dumps(result['active_level_counts'], ensure_ascii=False, sort_keys=True)}`
- komplettes Woerterbuch: {result['complete_readings']} Lesungen; jede mit
  Defaultbedeutung, Score, Confidence-Stufe, Evidenz und Gegenbeleg
- verbleibende schwache Einzelreparaturen: {result['remaining_unreviewed_weak_readings']}

## Grenze

Die Rasterfelder sind gebundene Arbeitswerte exakter Ganzformen, keine freien
Woerter. Der lokale Kopf Zubereitung ist weiterhin ersetzbar; ein bestimmtes
Produkt oder historisches Stufenvokabular ist nicht bestaetigt. Alle
historischen Felder bleiben `H0_NONE`; keine neue Seite oder Transkription
wurde benutzt.
"""


def main() -> int:
    source_lexical, source_context = read_tsv(SOURCE_LEXICAL), read_tsv(SOURCE_CONTEXT)
    source_complete, source_census = read_tsv(SOURCE_COMPLETE), read_tsv(SOURCE_CENSUS)
    source_spans, source_families = read_tsv(SOURCE_SPANS), read_tsv(SOURCE_FAMILIES)
    specs, bindings = read_tsv(SPECS), read_tsv(BINDINGS)
    assert (
        len(source_lexical), len(source_context), len(source_complete), len(source_census),
        len(source_spans), len(source_families), len(specs), len(bindings)
    ) == (324, 479, 1586, 84, 2, 13, 7, 34)
    assert all(row["decision"] == "REVISE" and row["component_global_export_allowed"] == "0" for row in specs)
    assert all(not row["page"].startswith("f84") and not row["locus"].startswith("f84") for row in source_context)

    evidence, deltas = resolve_evidence(bindings, specs, source_families)
    lexical, lexical_by_source = build_lexical(source_lexical, specs, deltas)
    contexts = build_contexts(source_context, specs, lexical_by_source)
    census = build_census(source_census, specs, lexical_by_source)
    delta = build_delta(specs, source_lexical, lexical_by_source)
    families = build_families(source_families, specs, lexical_by_source)
    complete = build_complete(source_complete, lexical)
    spans = [dict(row) for row in source_spans]
    directives = build_directives(contexts, spans)
    rendered = render_f7r2(contexts, directives)

    active_levels = Counter(str(row["working_model_level"]) for row in lexical)
    complete_levels = Counter(str(row["working_model_level"]) for row in complete)
    assert len(census) == 71 and Counter(row["disposition"] for row in census) == Counter({"HELD_FOR_LATER_REPAIR": 64, "REVISED_IN_V90": 7})
    assert len(families) == 2 and {row["family_id"] for row in families} == {"F_STATE", "F_STAGE"}
    assert len(directives) == 2 and len(rendered) == 8 and spans == source_spans
    assert len(complete) == 1586 and len({row["surface"] for row in complete}) == 1582
    assert active_levels == Counter({"W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY": 7, "W1_WEAK_WORKING": 135, "W2_PROVISIONAL_WORKING": 163, "W3_SOLID_WORKING_THEORY": 19})
    assert complete_levels == Counter({"W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY": 287, "W1_WEAK_WORKING": 315, "W2_PROVISIONAL_WORKING": 541, "W3_SOLID_WORKING_THEORY": 443})

    lexical_fields = unique_fields([v90_key(field) for field in source_lexical[0]] + ["v90_audit_decision", "v90_evidence_class", "v90_open_semantic_slots", "v90_component_global_export_allowed", "v90_prior_lexical_core_de"])
    context_fields = unique_fields([v90_key(field) for field in source_context[0]] + ["v90_audit_decision", "v90_evidence_class", "v90_open_semantic_slots", "v90_component_global_export_allowed", "v90_local_context_hypothesis", "v90_expected_left_surface"])
    census_fields = unique_fields([v90_key(field) for field in source_census[0]] + ["v90_audit_decision", "v90_evidence_class", "v90_open_semantic_slots"])
    family_fields = unique_fields([family_v90_key(field) for field in source_families[0]] + ["v90_decisions"])
    complete_fields = unique_fields([v90_key(field) for field in source_complete[0]] + ["v90_audit_decision", "v90_evidence_class", "v90_open_semantic_slots", "v90_component_global_export_allowed"])

    write_tsv(ART / "V90_324_ACTIVE_LEXICAL_READINGS.tsv", lexical_fields, lexical)
    write_tsv(ART / "V90_479_CONTEXT_REALIZATIONS.tsv", context_fields, contexts)
    write_tsv(ART / "V90_71_HELD_READING_AUDIT.tsv", census_fields, census)
    write_tsv(ART / "V90_7_QUALITY_STAGE_CORE_CONTEXT_DELTA.tsv", list(delta[0]), delta)
    write_tsv(ART / "V90_34_PRIMARY_EVIDENCE_BINDINGS.tsv", list(evidence[0]), evidence)
    write_tsv(ART / "V90_2_FAMILY_EVIDENCE.tsv", family_fields, families)
    write_tsv(ART / "V90_2_BOUND_SPAN_RENDERER.tsv", list(spans[0]), spans)
    write_tsv(ART / "V90_2_ONE_SHOT_RENDER_DIRECTIVES.tsv", list(directives[0]), directives)
    write_tsv(ART / "V90_8_F7R2_RENDERED_UNITS.tsv", list(rendered[0]), rendered)
    write_tsv(ART / "V90_COMPLETE_WORD_CONFIDENCE.tsv", complete_fields, complete)

    result = {
        "experiment_id": "GDT717", "status": STATUS,
        "claim_ceiling": "EXPLORATORY_WORKING_DICTIONARY_ONLY_NOT_PLAINTEXT",
        "audited_readings": 7, "audited_positions": 7, "audited_pages": 7,
        "grid_readings": 5, "sister_whole_readings": 2,
        "primary_evidence_bindings": len(evidence),
        "score_families": ["F_STATE", "F_STAGE"],
        "score_promotions": {row["source_reading_id"]: deltas[row["source_reading_id"]] for row in specs},
        "active_lexical_readings": len(lexical), "active_positions": len(contexts),
        "active_level_counts": dict(sorted(active_levels.items())),
        "remaining_unreviewed_weak_readings": sum(row["v90_audit_decision"] == "HELD_FOR_LATER_REPAIR" for row in census),
        "complete_readings": len(complete), "complete_surfaces": len({row["surface"] for row in complete}),
        "complete_level_counts": dict(sorted(complete_levels.items())),
        "bound_span_renderers": len(spans), "one_shot_directives": len(directives),
        "f7r2_rendered_units": len(rendered),
        "f7r2_rendered_line_de": " · ".join(row["rendered_text_de"] for row in rendered),
        "relation_word_credit_gdt717": 0, "historical_confirmation": HISTORICAL,
        "new_pages": 0, "new_images": 0, "new_transcription": 0, "f84_or_f84r_used": 0,
    }
    (ART / "RESULT.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (EXP / "REPORT.md").write_text(report_text(result, delta), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
