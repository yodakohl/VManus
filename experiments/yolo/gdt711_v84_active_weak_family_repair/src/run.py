#!/usr/bin/env python3
"""Build V84: separate lexical cores from occurrence-bound renderings.

This is an exploratory working-dictionary repair.  Scores are deterministic
audit indices, not probabilities or claims of historical decipherment.
"""

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
EXP = ROOT / "experiments/yolo/gdt711_v84_active_weak_family_repair"
SRC = EXP / "src"
ART = EXP / "artifacts"
G710 = ROOT / "experiments/yolo/gdt710_v83_complete_dictionary_confidence_evidence/artifacts"

READINGS = G710 / "V83_332_LIVE_READING_CONFIDENCE.tsv"
OCCURRENCES = G710 / "V83_479_LIVE_OCCURRENCE_EVIDENCE.tsv"
COMPLETE = G710 / "V83_COMPLETE_WORD_CONFIDENCE.tsv"
MASTER = G710 / "V83_2115_MASTER_CARD_CONFIDENCE.tsv"
STEMS = SRC / "V84_STEM_RULES.tsv"
SPECS = SRC / "V84_30_REPAIR_SPECS.tsv"

HISTORICAL = "H0_NONE"
RELATION_DELTA = "0_GDT696_TO_GDT709"
STATUS = (
    "PASS_V84_181_WEAK_AUDITED__30_SOURCE_READINGS_49_POSITIONS_REPAIRED__"
    "332_TO_324_ACTIVE_LEXICAL_READINGS__1594_TO_1586_COMPLETE_READINGS__"
    "11_W0_149_W1_145_W2_19_W3__19_W3_PRESERVED__ALL_H0_NONE"
)


QUEUE_ROWS = [
    (1, "AL_CLASS_RETREAT", "AR008 AR009 AR016 AR065 AR079 AR080 AR083 AR101 AR141 AR162 AR193 AR217 AR234 AR273 AR275 AR279 AR301"),
    (2, "STATE_AND_NEUTRAL_CARRIER", "AR034 AR035 AR037 AR045 AR056 AR090 AR106 AR109 AR110 AR153 AR241 AR244 AR253 AR282 AR284 AR288 AR295 AR310 AR311"),
    (3, "MEASURE_FAMILY", "AR010 AR081 AR088 AR182 AR194"),
    (4, "CKH_CPH_EXACT_FAMILY", "AR019 AR025 AR032 AR057 AR060 AR061 AR274 AR277"),
    (5, "ABSTRACT_VALUE_AXIS", "AR002 AR067 AR068 AR069 AR070 AR071 AR072 AR073 AR074 AR075 AR076 AR222 AR318"),
    (6, "BOUND_C1_COMPOUNDS", "AR028 AR041 AR046 AR049 AR052 AR092 AR093 AR104 AR113 AR115 AR150 AR163 AR183 AR187 AR188 AR204 AR207 AR304"),
    (7, "ACTION_WITH_OPEN_PATIENT", "AR089 AR214 AR216 AR219 AR221 AR324"),
    (8, "HEAD_AND_OL_HOLD", "AR116 AR126 AR155 AR156 AR211 AR262"),
    (9, "CLOSED_PREPARATION_HEAD_ROUTE", "AR001 AR040 AR042 AR043 AR047 AR097 AR107 AR108 AR111 AR136 AR139 AR140 AR146 AR148 AR152 AR172 AR178 AR179 AR180 AR185 AR189 AR198 AR199 AR200 AR202 AR205 AR206 AR220 AR227 AR249 AR258 AR286 AR289 AR293 AR296 AR307 AR322 AR327"),
    (10, "CLOSED_AR_SHARE_ROUTE", "AR006 AR007 AR012 AR013 AR015 AR017 AR022 AR024 AR050 AR066 AR078 AR099 AR102 AR103 AR121 AR123 AR127 AR134 AR135 AR137 AR149 AR164 AR165 AR184 AR195 AR196 AR197 AR212 AR218 AR223 AR232 AR270 AR272"),
    (11, "LOW_STRUCTURAL_OR_MANUAL_HARDCAP", "AR003 AR051 AR059 AR064 AR095 AR096 AR114 AR186 AR209 AR261 AR294 AR299 AR300 AR309 AR312 AR313 AR319 AR326"),
]


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


def compact(values: Iterable[str], empty: str = "NONE") -> str:
    cleaned = sorted({value.strip() for value in values if value and value.strip() not in {"NONE", "0"}})
    return "|".join(cleaned) if cleaned else empty


def ordered_compact(values: Iterable[str], separator: str = "|", empty: str = "NONE") -> str:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        value = value.strip()
        if value and value not in {"NONE", "0"} and value not in seen:
            seen.add(value)
            result.append(value)
    return separator.join(result) if result else empty


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


def issue_cluster(row: dict[str, str]) -> str:
    rival = row["live_rivals_de"] not in {"", "NONE", "0"}
    debt = row["gdt684_current_debt_counts"] not in {"", "NONE", "0"}
    low = int(row["low_source_positions"] or "0") > 0
    if rival:
        return "LIVE_RIVAL"
    if debt and low:
        return "CURRENT_DEBT_PLUS_LOW"
    if debt:
        return "CURRENT_DEBT_ONLY"
    return "NO_LISTED_DEBT_LOW_OR_RIVAL"


def make_queue_map() -> dict[str, tuple[int, str]]:
    result: dict[str, tuple[int, str]] = {}
    for rank, name, ids in QUEUE_ROWS:
        for entity_id in ids.split():
            if entity_id in result:
                raise AssertionError(f"duplicate queue member: {entity_id}")
            result[entity_id] = rank, name
    return result


def semantic_card_links(
    weak: list[dict[str, str]], master: list[dict[str, str]]
) -> list[dict[str, Any]]:
    excluded_kind_fragments = (
        "PRACTICAL_RENDERING", "OCCURRENCE_SCOPED_CONTEXT", "CONTEXTUAL_NAKED", "LABEL"
    )
    by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    for card in master:
        normalized = card["entry"].split("@", 1)[0].strip()
        if not normalized or "/" in normalized or "(" in normalized or "+" in normalized:
            continue
        if any(fragment in card["kind"].upper() for fragment in excluded_kind_fragments):
            continue
        if card["semantic_applicability"] == "RENDERER_NOT_WORD_MEANING":
            continue
        by_surface[normalized].append(card)

    rows: list[dict[str, Any]] = []
    for reading in weak:
        for card in sorted(by_surface.get(reading["surface"], []), key=lambda item: item["entity_id"]):
            rows.append({
                "source_reading_id": reading["reading_id"],
                "source_entity_id": reading["entity_id"],
                "surface": reading["surface"],
                "master_card_id": card["entity_id"],
                "master_entry": card["entry"],
                "master_kind": card["kind"],
                "master_working_meaning_de": card["working_meaning_de"],
                "master_score": card["working_model_score_0_100_not_probability"],
                "master_level": card["working_model_level"],
                "link_reason": "EXACT_NORMALIZED_SURFACE_ONLY",
                "used_as_automatic_score_credit": 0,
                "score_credit": 0,
                "interpretation": "NAVIGATION_AND_MANUAL_FAMILY_EVIDENCE_ONLY",
            })
    return rows


def build_lexical_rows(
    readings: list[dict[str, str]],
    occurrences: list[dict[str, str]],
    specs: list[dict[str, str]],
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    specs_by_id = {row["source_reading_id"]: row for row in specs}
    occ_by_reading: dict[str, list[dict[str, str]]] = defaultdict(list)
    for occurrence in occurrences:
        occ_by_reading[occurrence["reading_id"]].append(occurrence)

    groups: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for reading in readings:
        spec = specs_by_id.get(reading["reading_id"])
        if spec:
            group_key = ("REPAIRED", reading["surface"], spec["v84_lexical_core_de"])
        else:
            group_key = ("RETAINED", reading["reading_id"], reading["working_meaning_de"])
        groups[group_key].append(reading)

    provisional: list[dict[str, Any]] = []
    for group_key, source_rows in groups.items():
        source_rows = sorted(source_rows, key=lambda item: item["entity_id"])
        selected_specs = [specs_by_id[row["reading_id"]] for row in source_rows if row["reading_id"] in specs_by_id]
        repaired = bool(selected_specs)
        surface = source_rows[0]["surface"]
        if repaired:
            lexical_core = selected_specs[0]["v84_lexical_core_de"]
            assert all(spec["v84_lexical_core_de"] == lexical_core for spec in selected_specs)
            if len(source_rows) > 1:
                v84_reading_id = f"{surface}#V84_CORE"
            else:
                old_suffix = source_rows[0]["reading_id"].split("#", 1)[-1]
                v84_reading_id = f"{surface}#V84_{old_suffix}"
        else:
            lexical_core = source_rows[0]["working_meaning_de"]
            v84_reading_id = source_rows[0]["reading_id"]

        source_ids = [row["reading_id"] for row in source_rows]
        source_entity_ids = [row["entity_id"] for row in source_rows]
        group_occurrences = [occ for rid in source_ids for occ in occ_by_reading[rid]]
        assert group_occurrences
        if repaired:
            contexts = [spec["v84_context_realization_de"] for spec in selected_specs]
            base_score = max(int(row["working_model_score_0_100_not_probability"]) for row in source_rows)
            delta = max(int(spec["score_delta_lexical_core"]) for spec in selected_specs)
            lexical_cap = min(int(spec["lexical_core_cap"]) for spec in selected_specs)
            context_cap = min(int(spec["context_realization_cap"]) for spec in selected_specs)
            score = min(base_score + delta, lexical_cap)
            context_score = min(score, context_cap)
            family_ids = ordered_compact(
                family for spec in selected_specs for family in split_pipe(spec["family_ids"])
            )
            decompositions = ordered_compact(spec["decomposition"] for spec in selected_specs)
            modes = ordered_compact(spec["repair_mode"] for spec in selected_specs)
            debt_atoms = ordered_compact(spec["resolved_debt_atom"] for spec in selected_specs)
            positive = ordered_compact(
                ["GDT711 trennt den kompakten Wortkern von der positionsgebundenen Satzrealisierung."]
                + [spec["evidence_de"] for spec in selected_specs], separator=" || "
            )
            counter = ordered_compact(
                ["Historisch unbestätigte Arbeitstheorie; keine Klartextidentifikation."]
                + [spec["counterevidence_de"] for spec in selected_specs], separator=" || "
            )
            last_writer = "GDT711"
        else:
            contexts = [source_rows[0]["working_meaning_de"]]
            base_score = int(source_rows[0]["working_model_score_0_100_not_probability"])
            delta = 0
            lexical_cap = 79
            context_cap = 79
            score = base_score
            context_score = score
            family_ids = "NONE"
            decompositions = "UNCHANGED_V83_READING"
            modes = "RETAIN_V83"
            debt_atoms = "NONE"
            positive = source_rows[0]["positive_evidence_de"]
            counter = source_rows[0]["counterevidence_de"]
            last_writer = source_rows[0]["last_semantic_writer"]

        pages = sorted({occ["page"] for occ in group_occurrences})
        loci = sorted({occ["locus"] for occ in group_occurrences})
        source_scopes = ordered_compact(row["semantic_scope"] for row in source_rows)
        source_applicabilities = ordered_compact(row["semantic_applicability"] for row in source_rows)
        source_export_scopes = ordered_compact(row["global_export_scope"] for row in source_rows)
        source_bound_spans = ordered_compact(
            span for row in source_rows for span in split_pipe(row["bound_span_ids"])
        )
        if repaired and any(spec["repair_mode"] == "BOUND_ONLY_NO_GLOBAL_EXPORT" for spec in selected_specs):
            semantic_scope = "BOUND_SPAN_LOCAL_READING"
            semantic_applicability = "COMPOUND_ONLY_LOCAL_READING"
            global_export_scope = "BOUND_SPAN_ONLY_NO_GLOBAL_EXPORT"
            bound_span_ids = "G683_CHEOP_OL"
            unconditional_export = 0
        else:
            semantic_scope = source_scopes
            semantic_applicability = source_applicabilities
            global_export_scope = source_export_scopes
            bound_span_ids = source_bound_spans
            unconditional_export = int(
                set(split_pipe(source_export_scopes)) == {"ACTIVE_WORKING_DEFAULT"}
            )
        sample_loci = ordered_compact(
            [f"{occ['locus']}#{occ['token_ordinal']}" for occ in sorted(
                group_occurrences,
                key=lambda item: (item["page"], item["locus"], int(item["token_ordinal"])),
            )[:12]]
        )
        provisional.append({
            "entity_type": "ACTIVE_LEXICAL_READING",
            "v84_reading_id": v84_reading_id,
            "surface": surface,
            "v84_lexical_core_de": lexical_core,
            "v84_context_realizations_de": ordered_compact(contexts),
            "source_reading_ids": ordered_compact(source_ids),
            "source_entity_ids": ordered_compact(source_entity_ids),
            "source_working_meanings_de": ordered_compact(
                [row["working_meaning_de"] for row in source_rows], separator=" || "
            ),
            "source_gdts": compact(
                [gdt for row in source_rows for gdt in split_pipe(row["source_gdts"])]
                + (["GDT711"] if repaired else [])
            ),
            "source_artifacts": compact(
                artifact for row in source_rows for artifact in split_pipe(row["source_artifacts"])
            ),
            "source_semantic_scopes": source_scopes,
            "source_semantic_applicabilities": source_applicabilities,
            "source_global_export_scopes": source_export_scopes,
            "source_bound_span_ids": source_bound_spans,
            "semantic_scope": semantic_scope,
            "semantic_applicability": semantic_applicability,
            "global_export_scope": global_export_scope,
            "bound_span_ids": bound_span_ids,
            "unconditional_global_export_allowed": unconditional_export,
            "source_reading_count": len(source_rows),
            "occurrence_count": len(group_occurrences),
            "page_count": len(pages),
            "locus_count": len(loci),
            "pages": "|".join(pages),
            "sample_loci": sample_loci,
            "family_ids": family_ids,
            "decomposition": decompositions,
            "repair_modes": modes,
            "resolved_debt_atoms": debt_atoms,
            "last_semantic_writer": last_writer,
            "base_score": base_score,
            "score_delta_lexical_core": delta,
            "lexical_core_cap": lexical_cap,
            "working_model_score_0_100_not_probability": score,
            "working_model_level": level(score),
            "context_realization_cap": context_cap,
            "context_realization_score_0_100_not_probability": context_score,
            "context_realization_level": level(context_score),
            "form_level": "F3_EXACT_ACTIVE_ZL3B_TOKEN",
            "historical_confirmation": HISTORICAL,
            "historical_analogue": "NONE",
            "relation_word_delta": RELATION_DELTA,
            "positive_evidence_de": positive,
            "counterevidence_de": counter,
        })

    rows = sorted(provisional, key=lambda item: (item["surface"], item["v84_reading_id"]))
    by_source: dict[str, dict[str, Any]] = {}
    for row in rows:
        for source_id in split_pipe(row["source_reading_ids"]):
            assert source_id not in by_source
            by_source[source_id] = row
    return rows, by_source


def build_occurrence_rows(
    occurrences: list[dict[str, str]],
    specs: list[dict[str, str]],
    lexical_by_source: dict[str, dict[str, Any]],
) -> tuple[list[str], list[dict[str, Any]]]:
    specs_by_id = {row["source_reading_id"]: row for row in specs}
    source_fields = list(occurrences[0])
    extra_fields = [
        "source_reading_id", "v84_reading_id", "v84_lexical_core_de",
        "v84_context_realization_de", "v84_repair_mode", "v84_resolved_debt_atom",
        "v84_lexical_score", "v84_lexical_level", "v84_context_score",
        "v84_context_level", "v84_semantic_scope", "v84_semantic_applicability",
        "v84_global_export_scope", "v84_lexical_bound_span_ids",
        "v84_unconditional_global_export_allowed", "v84_historical_confirmation",
        "v84_occurrence_bound_span_id", "v84_occurrence_bound_span_role",
        "v84_occurrence_bound_span_global_export_allowed",
    ]
    rows: list[dict[str, Any]] = []
    for source in occurrences:
        row: dict[str, Any] = dict(source)
        reading_id = source["reading_id"]
        lexical = lexical_by_source[reading_id]
        spec = specs_by_id.get(reading_id)
        row.update({
            "source_reading_id": reading_id,
            "v84_reading_id": lexical["v84_reading_id"],
            "v84_lexical_core_de": lexical["v84_lexical_core_de"],
            "v84_context_realization_de": spec["v84_context_realization_de"] if spec else source["working_meaning_de"],
            "v84_repair_mode": spec["repair_mode"] if spec else "RETAIN_V83",
            "v84_resolved_debt_atom": spec["resolved_debt_atom"] if spec else "NONE",
            "v84_lexical_score": lexical["working_model_score_0_100_not_probability"],
            "v84_lexical_level": lexical["working_model_level"],
            "v84_context_score": lexical["context_realization_score_0_100_not_probability"],
            "v84_context_level": lexical["context_realization_level"],
            "v84_semantic_scope": lexical["semantic_scope"],
            "v84_semantic_applicability": lexical["semantic_applicability"],
            "v84_global_export_scope": lexical["global_export_scope"],
            "v84_lexical_bound_span_ids": lexical["bound_span_ids"],
            "v84_unconditional_global_export_allowed": lexical["unconditional_global_export_allowed"],
            "v84_historical_confirmation": HISTORICAL,
        })
        if reading_id == "ol#2":
            row["v84_occurrence_bound_span_id"] = "G683_CHEOP_OL"
            row["v84_occurrence_bound_span_role"] = "RIGHT"
            row["v84_occurrence_bound_span_global_export_allowed"] = 0
        else:
            row["v84_occurrence_bound_span_id"] = source["bound_span_id"]
            row["v84_occurrence_bound_span_role"] = source["bound_span_role"]
            row["v84_occurrence_bound_span_global_export_allowed"] = source["bound_span_global_export_allowed"]
        rows.append(row)
    return source_fields + extra_fields, rows


def build_census(
    weak: list[dict[str, str]],
    specs: list[dict[str, str]],
    card_links: list[dict[str, Any]],
    lexical_by_source: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    specs_by_id = {row["source_reading_id"]: row for row in specs}
    queue_map = make_queue_map()
    link_counts = Counter(row["source_reading_id"] for row in card_links)
    rows: list[dict[str, Any]] = []
    for source in sorted(weak, key=lambda item: item["entity_id"]):
        spec = specs_by_id.get(source["reading_id"])
        lexical = lexical_by_source[source["reading_id"]]
        rank, queue = queue_map[source["entity_id"]]
        rows.append({
            "source_entity_id": source["entity_id"],
            "source_reading_id": source["reading_id"],
            "surface": source["surface"],
            "original_working_meaning_de": source["working_meaning_de"],
            "occurrence_count": source["occurrence_count"],
            "page_count": source["page_count"],
            "issue_cluster": issue_cluster(source),
            "repair_queue_rank": rank,
            "repair_queue": queue,
            "exact_normalized_master_card_links": link_counts[source["reading_id"]],
            "master_card_automatic_score_credit": 0,
            "disposition": "REPAIRED_IN_V84" if spec else "HELD_FOR_LATER_REPAIR",
            "repair_mode": spec["repair_mode"] if spec else "NONE",
            "resolved_debt_atom": spec["resolved_debt_atom"] if spec else "NONE",
            "v84_reading_id": lexical["v84_reading_id"],
            "v84_lexical_core_de": lexical["v84_lexical_core_de"],
            "v84_context_realization_de": spec["v84_context_realization_de"] if spec else source["working_meaning_de"],
            "old_score": source["working_model_score_0_100_not_probability"],
            "old_level": source["working_model_level"],
            "new_lexical_score": lexical["working_model_score_0_100_not_probability"],
            "new_lexical_level": lexical["working_model_level"],
            "new_context_score": lexical["context_realization_score_0_100_not_probability"],
            "new_context_level": lexical["context_realization_level"],
            "historical_confirmation": HISTORICAL,
            "positive_evidence_de": spec["evidence_de"] if spec else source["positive_evidence_de"],
            "counterevidence_de": spec["counterevidence_de"] if spec else source["counterevidence_de"],
        })
    return rows


def build_family_rows(
    stems: list[dict[str, str]],
    specs: list[dict[str, str]],
    readings_by_id: dict[str, dict[str, str]],
    occurrences: list[dict[str, str]],
    lexical_by_source: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    occ_by_reading: dict[str, list[dict[str, str]]] = defaultdict(list)
    for occurrence in occurrences:
        occ_by_reading[occurrence["reading_id"]].append(occurrence)
    rows: list[dict[str, Any]] = []
    for stem in stems:
        family_id = stem["family_id"]
        selected = [spec for spec in specs if family_id in split_pipe(spec["family_ids"])]
        selected_ids = [spec["source_reading_id"] for spec in selected]
        selected_occurrences = [occ for rid in selected_ids for occ in occ_by_reading[rid]]
        lexical_ids = {lexical_by_source[rid]["v84_reading_id"] for rid in selected_ids}
        row: dict[str, Any] = dict(stem)
        row.update({
            "selected_source_readings": len(selected_ids),
            "selected_lexical_readings": len(lexical_ids),
            "selected_positions": len(selected_occurrences),
            "selected_pages": len({occ["page"] for occ in selected_occurrences}),
            "selected_source_reading_ids": ordered_compact(selected_ids),
            "selected_surfaces": compact(readings_by_id[rid]["surface"] for rid in selected_ids),
            "selected_v84_reading_ids": compact(lexical_ids),
            "selected_v84_levels": compact(lexical_by_source[rid]["working_model_level"] for rid in selected_ids),
            "automatic_historical_credit": 0,
            "historical_confirmation": HISTORICAL,
        })
        rows.append(row)
    return rows


def build_complete(
    complete: list[dict[str, str]], lexical_rows: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    global_rows: list[dict[str, Any]] = []
    for source in complete:
        if source["current_layer"] == "ACTIVE_V68_READING":
            continue
        row: dict[str, Any] = dict(source)
        exact_global = (
            source["semantic_scope"] == "KNOWN_EXACT_WHOLE"
            and source["form_level"] == "F3_EXACT_ZL3B_WHOLE"
        )
        row.update({
            "global_export_scope": (
                "GLOBAL_V48_EXACT_WHOLE_DEFAULT"
                if exact_global
                else f"GLOBAL_V48_{source['semantic_scope']}_NO_UNCONDITIONAL_EXPORT"
            ),
            "bound_span_ids": "NONE",
            "unconditional_global_export_allowed": int(exact_global),
            "v84_context_realizations_de": source["working_meaning_de"],
            "source_reading_ids": source["reading_id"],
        })
        global_rows.append(row)
    for lexical in lexical_rows:
        global_rows.append({
            "surface": lexical["surface"],
            "reading_id": lexical["v84_reading_id"],
            "working_meaning_de": lexical["v84_lexical_core_de"],
            "current_layer": "ACTIVE_V84_LEXICAL_CORE",
            "semantic_scope": lexical["semantic_scope"],
            "semantic_applicability": lexical["semantic_applicability"],
            "form_level": lexical["form_level"],
            "occurrence_count": lexical["occurrence_count"],
            "page_count": lexical["page_count"],
            "locus_count": lexical["locus_count"],
            "working_model_score_0_100_not_probability": lexical["working_model_score_0_100_not_probability"],
            "working_model_level": lexical["working_model_level"],
            "source_gdts": lexical["source_gdts"],
            "positive_evidence_de": lexical["positive_evidence_de"],
            "counterevidence_de": lexical["counterevidence_de"],
            "historical_confirmation": HISTORICAL,
            "historical_analogue": "NONE",
            "relation_word_delta": RELATION_DELTA,
            "global_export_scope": lexical["global_export_scope"],
            "bound_span_ids": lexical["bound_span_ids"],
            "unconditional_global_export_allowed": lexical["unconditional_global_export_allowed"],
            "v84_context_realizations_de": lexical["v84_context_realizations_de"],
            "source_reading_ids": lexical["source_reading_ids"],
        })
    return sorted(global_rows, key=lambda item: (item["surface"], item["reading_id"]))


def report_text(result: dict[str, Any]) -> str:
    return f"""# GDT711 — V84 active weak-family repair

Status: `{STATUS}`

## Outcome

V84 audits all 181 active W0/W1 readings and repairs the first 30 source readings (49 unchanged token positions on 25 pages). The central correction is architectural: the dictionary now stores a compact lexical core, while the occurrence table stores the practical local realization. Thus the seven active `daiin` senses collapse to one lexical core `Wert III`, with `Grad III` or `drei` retained only as context realizations; the three `dain` senses analogously collapse to `Wert II`.

The active dictionary contracts from 332 to 324 lexical readings without deleting or resegmenting any of the 479 token positions. The complete dictionary contracts from 1,594 to 1,586 readings while retaining 1,582 surfaces. Active levels are 11 W0, 149 W1, 145 W2 and 19 W3. Every historical confirmation remains `H0_NONE`, and GDT696–GDT709 still contribute zero word-confidence points.

## Material repairs

- Value family: `dain/daiin` become abstract values II/III; local grade-versus-count rendering is separate. `qodaiin` remains a distinct W1 `Wert III` reading; its decomposition field keeps `qod|aiin` versus `qo|daiin` open and QO receives no free semantic credit.
- Unsupported nouns and units are deleted: no automatic Gummi, Gran, Handvoll, Dosis, Mazerat, Absud or Auszug identity survives merely because a fluent renderer used it.
- `am/dam/dal/oidal` retain only visible measure/material structure; no historical unit is claimed.
- CKH forms retain exact-family `Mischgut/Mischung`, never a free universal CKH word or an identified medicine.
- `olkar` retains the intersection shared by both live rivals—hot, wood, share I—while Ansatz versus Auszug is removed. Free `ol` stays W1; bound `ol#2` stays W0 and nonportable.

## Guardrails

Exact normalized master-card matches are published as navigation links only and always receive automatic score credit 0. All 19 prior W3 readings and their 77 positions preserve meaning, score, semantic scope, applicability, export boundary, bound spans, writer and provenance. Structural readings remain structural; the compound-only `ol#2` is explicitly non-exportable. No new page, spelling, segmentation, historical analogue, plaintext identification, `f84`, or `f84r` is used.

## Counts

- weak-source issue partition: `{json.dumps(result['weak_issue_partition'], ensure_ascii=False, sort_keys=True)}`
- selected source readings / positions / pages: {result['selected_source_readings']} / {result['selected_positions']} / {result['selected_pages']}
- active lexical readings / positions: {result['active_lexical_readings']} / {result['active_positions']}
- complete readings / surfaces: {result['complete_readings']} / {result['complete_surfaces']}
- active levels: `{json.dumps(result['active_level_counts'], ensure_ascii=False, sort_keys=True)}`
- active semantic applicability: `{json.dumps(result['active_applicability_counts'], ensure_ascii=False, sort_keys=True)}`
- active export scopes: `{json.dumps(result['active_export_scope_counts'], ensure_ascii=False, sort_keys=True)}`
- complete levels: `{json.dumps(result['complete_level_counts'], ensure_ascii=False, sort_keys=True)}`
"""


def main() -> int:
    readings = read_tsv(READINGS)
    occurrences = read_tsv(OCCURRENCES)
    complete = read_tsv(COMPLETE)
    master = read_tsv(MASTER)
    stems = read_tsv(STEMS)
    specs = read_tsv(SPECS)

    assert (len(readings), len(occurrences), len(complete), len(master), len(stems), len(specs)) == (332, 479, 1594, 2115, 13, 30)
    for collection in (readings, occurrences, complete):
        assert all(not row.get("page", "").startswith("f84") for row in collection)
        assert all(not row.get("locus", "").startswith("f84") for row in collection)

    readings_by_id = {row["reading_id"]: row for row in readings}
    assert len(readings_by_id) == 332
    assert len({row["source_reading_id"] for row in specs}) == 30
    for spec in specs:
        source = readings_by_id[spec["source_reading_id"]]
        assert source["working_meaning_de"] == spec["old_working_meaning_de"]

    weak = [row for row in readings if int(row["working_model_score_0_100_not_probability"]) < 40]
    assert len(weak) == 181
    assert sum(int(row["occurrence_count"]) for row in weak) == 211
    queue_map = make_queue_map()
    assert set(queue_map) == {row["entity_id"] for row in weak}
    issue_counts = Counter(issue_cluster(row) for row in weak)
    assert issue_counts == Counter({
        "CURRENT_DEBT_ONLY": 75,
        "CURRENT_DEBT_PLUS_LOW": 13,
        "LIVE_RIVAL": 88,
        "NO_LISTED_DEBT_LOW_OR_RIVAL": 5,
    })

    card_links = semantic_card_links(weak, master)
    lexical_rows, lexical_by_source = build_lexical_rows(readings, occurrences, specs)
    assert len(lexical_rows) == 324
    assert len(lexical_by_source) == 332
    occurrence_fields, occurrence_rows = build_occurrence_rows(occurrences, specs, lexical_by_source)
    census_rows = build_census(weak, specs, card_links, lexical_by_source)
    family_rows = build_family_rows(stems, specs, readings_by_id, occurrences, lexical_by_source)
    complete_rows = build_complete(complete, lexical_rows)

    selected_ids = {row["source_reading_id"] for row in specs}
    selected_occurrences = [row for row in occurrences if row["reading_id"] in selected_ids]
    active_levels = Counter(row["working_model_level"] for row in lexical_rows)
    complete_levels = Counter(row["working_model_level"] for row in complete_rows)
    assert len(selected_occurrences) == 49
    assert len({row["page"] for row in selected_occurrences}) == 25
    assert active_levels == Counter({
        "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY": 11,
        "W1_WEAK_WORKING": 149,
        "W2_PROVISIONAL_WORKING": 145,
        "W3_SOLID_WORKING_THEORY": 19,
    })
    assert complete_levels == Counter({
        "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY": 291,
        "W1_WEAK_WORKING": 329,
        "W2_PROVISIONAL_WORKING": 523,
        "W3_SOLID_WORKING_THEORY": 443,
    })
    assert len(complete_rows) == 1586
    assert len({row["surface"] for row in complete_rows}) == 1582
    assert all(row["historical_confirmation"] == HISTORICAL for row in lexical_rows)
    assert all(row["relation_word_delta"] == RELATION_DELTA for row in lexical_rows)

    family_fields = list(stems[0]) + [
        "selected_source_readings", "selected_lexical_readings", "selected_positions",
        "selected_pages", "selected_source_reading_ids", "selected_surfaces",
        "selected_v84_reading_ids", "selected_v84_levels",
        "automatic_historical_credit", "historical_confirmation",
    ]
    link_fields = [
        "source_reading_id", "source_entity_id", "surface", "master_card_id",
        "master_entry", "master_kind", "master_working_meaning_de", "master_score",
        "master_level", "link_reason", "used_as_automatic_score_credit",
        "score_credit", "interpretation",
    ]
    census_fields = list(census_rows[0])
    lexical_fields = list(lexical_rows[0])
    complete_fields = list(complete[0]) + [
        "global_export_scope", "bound_span_ids", "unconditional_global_export_allowed",
        "v84_context_realizations_de", "source_reading_ids",
    ]

    write_tsv(ART / "V84_13_STEM_FAMILY_EVIDENCE.tsv", family_fields, family_rows)
    write_tsv(ART / "V84_NORMALIZED_CARD_LINKS.tsv", link_fields, card_links)
    write_tsv(ART / "V84_181_WEAK_READING_REPAIR_CENSUS.tsv", census_fields, census_rows)
    write_tsv(ART / "V84_324_ACTIVE_LEXICAL_READINGS.tsv", lexical_fields, lexical_rows)
    write_tsv(ART / "V84_479_CONTEXT_REALIZATIONS.tsv", occurrence_fields, occurrence_rows)
    write_tsv(ART / "V84_COMPLETE_WORD_CONFIDENCE.tsv", complete_fields, complete_rows)

    result = {
        "experiment_id": "GDT711",
        "status": STATUS,
        "claim_ceiling": "EXPLORATORY_WORKING_DICTIONARY_ONLY_NOT_PLAINTEXT",
        "source_active_readings": len(readings),
        "source_active_positions": len(occurrences),
        "weak_source_readings": len(weak),
        "weak_source_positions": sum(int(row["occurrence_count"]) for row in weak),
        "weak_issue_partition": dict(sorted(issue_counts.items())),
        "repair_queue_counts": dict(sorted(Counter(name for _, name in queue_map.values()).items())),
        "selected_source_readings": len(selected_ids),
        "selected_positions": len(selected_occurrences),
        "selected_pages": len({row["page"] for row in selected_occurrences}),
        "selected_source_level_changes": sum(
            readings_by_id[rid]["working_model_level"] != lexical_by_source[rid]["working_model_level"]
            for rid in selected_ids
        ),
        "active_lexical_readings": len(lexical_rows),
        "active_positions": len(occurrence_rows),
        "active_level_counts": dict(sorted(active_levels.items())),
        "active_applicability_counts": dict(sorted(Counter(row["semantic_applicability"] for row in lexical_rows).items())),
        "active_export_scope_counts": dict(sorted(Counter(row["global_export_scope"] for row in lexical_rows).items())),
        "complete_readings": len(complete_rows),
        "complete_surfaces": len({row["surface"] for row in complete_rows}),
        "complete_level_counts": dict(sorted(complete_levels.items())),
        "stem_families": len(family_rows),
        "normalized_card_links": len(card_links),
        "normalized_card_links_with_automatic_credit": sum(int(row["used_as_automatic_score_credit"]) for row in card_links),
        "historical_confirmation_counts": dict(Counter(row["historical_confirmation"] for row in complete_rows)),
        "relation_word_delta_nonzero": sum(row["relation_word_delta"] != RELATION_DELTA for row in complete_rows),
        "w3_active_readings": active_levels["W3_SOLID_WORKING_THEORY"],
        "new_pages": 0,
        "f84_or_f84r_used": 0,
    }
    (ART / "RESULT.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (EXP / "REPORT.md").write_text(report_text(result), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
