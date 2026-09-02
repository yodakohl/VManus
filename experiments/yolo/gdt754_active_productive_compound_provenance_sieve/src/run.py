#!/usr/bin/env python3
"""Inventory and rerender active GDT664/GDT666 productive compounds."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_REL = Path("experiments/yolo/gdt754_active_productive_compound_provenance_sieve")
EXP = ROOT / BASE_REL
DEFAULT_ARTIFACTS = EXP / "artifacts"
G753_RUN_REL = Path(
    "experiments/yolo/gdt753_qokeol_okeol_whole_role_census/src/run.py"
)
DICTIONARY_REL = Path(
    "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/"
    "V99R7_1606_COMPLETE_WORD_CONFIDENCE.tsv"
)
SOURCE_DECISIONS = {
    "GDT664:EXACT_WHOLE": Path(
        "experiments/yolo/gdt664_one_hundred_forty_residual_family_completion/"
        "artifacts/TARGET_DECISION_DECK.tsv"
    ),
    "GDT666:EXACT_WHOLE": Path(
        "experiments/yolo/gdt666_one_hundred_fifty_one_residual_family_completion/"
        "artifacts/TARGET_DECISION_DECK.tsv"
    ),
}
G737_QUARANTINE_REL = Path(
    "experiments/yolo/gdt737_held_body_record_role_transfer/artifacts/"
    "V99R7_HELD_WHOLE_QUARANTINE.tsv"
)
G738_CARDS_REL = Path(
    "experiments/yolo/gdt738_held_body_occurrence_semantic_adjudication/"
    "artifacts/ADJUDICATED_17_WHOLE_CARDS.tsv"
)
G738_PATCH_REL = Path(
    "experiments/yolo/gdt738_held_body_occurrence_semantic_adjudication/"
    "artifacts/OCCURRENCE_RENDERER_PATCH.tsv"
)
G745_CARDS_REL = Path(
    "experiments/yolo/gdt745_exact_open_content_role_expansion/artifacts/"
    "CROSS_PAGE_ROLE_CARDS.tsv"
)
G746_CENSUS_REL = Path(
    "experiments/yolo/gdt746_whole_analogy_distribution_test/artifacts/"
    "CANDIDATE_17_DISTRIBUTION_CENSUS.tsv"
)
G748_CENSUS_REL = Path(
    "experiments/yolo/gdt748_complete_whole_serial_paradigm_census/artifacts/"
    "SURFACE_PREDICTION_CENSUS.tsv"
)
G749_CENSUS_REL = Path(
    "experiments/yolo/gdt749_outside_frame_whole_role_distribution/artifacts/"
    "TARGET_OUTSIDE_ROLE_CENSUS.tsv"
)
G750_ACTIVE_REL = Path(
    "experiments/yolo/gdt750_form_gated_direct_host_dispatch/artifacts/"
    "ACTIVE_OCCURRENCE_CARDS.tsv"
)
G753_PROVENANCE_REL = Path(
    "experiments/yolo/gdt753_qokeol_okeol_whole_role_census/artifacts/"
    "INHERITED_ROLE_PROVENANCE_AUDIT.tsv"
)
OUTPUT_NAMES = (
    "ACTIVE_172_PRODUCTIVE_COMPOUND_INVENTORY.tsv",
    "LATER_WHOLE_ROLE_EVIDENCE.tsv",
    "PROVENANCE_SIEVE_172_DECISIONS.tsv",
    "CURRENT_SOURCE_PROSE_POSITION_PATCH.tsv",
    "TOP_24_HISTORICAL_VOCABULARY_BRIDGE_DECK.tsv",
    "GDT754_PRODUCTIVE_COMPOUND_READER.md",
    "RESULT.json",
)
AXIS_ORDER = (
    "HOT", "COLD", "DRY", "MOIST", "BEGIN_STAGE", "MIDDLE_STAGE",
    "END_STAGE", "LEVEL_I", "LEVEL_II", "LEVEL_III", "AMOUNT", "PART",
    "MATERIAL", "PREPARATION", "PROCESS", "CLOSE", "PASS",
)
AXIS_DE = {
    "HOT": "heiß/warm",
    "COLD": "kalt/kühl",
    "DRY": "trocken",
    "MOIST": "feucht/eingeweicht",
    "BEGIN_STAGE": "Anfangsstufe",
    "MIDDLE_STAGE": "Mittelstufe",
    "END_STAGE": "End-/Vollstufe",
    "LEVEL_I": "Index/Stufe I",
    "LEVEL_II": "Index/Stufe II",
    "LEVEL_III": "Index/Stufe III",
    "AMOUNT": "Mengen-/Maßfeld",
    "PART": "Teil-/Fraktionsfeld",
    "MATERIAL": "Stoff-/Materialrolle",
    "PREPARATION": "Zubereitungsrolle",
    "PROCESS": "Vorgangs-/Anweisungsrolle",
    "CLOSE": "Abschlussfeld",
    "PASS": "Weiterführungs-/Bezugsfeld",
}
PATIENT_MARKERS = (
    "WOOD", "ROOT", "SEED", "HERB", "LEAF", "FLOWER", "POWDER",
    "DRUG", "RAW", "MATERIAL", "PREP", "BASE", "EXTRACT", "DECOCT",
    "COMPOSITE", "MIX", "MIXTURE", "GUM", "RESIN",
)
STATUS = (
    "PARTIAL__172_ACTIVE_PRODUCTIVE_COMPOUNDS__889_SOURCE_PROSE_CELLS_159_PAGES__"
    "686_READER_EXACT__168_COMPOSITION_AXES_ONLY__1_LOCAL_ROLE_PATCH_FAMILY_42_CELLS__"
    "1_FORM_ANALOGY_ONLY__2_CORRECTED_PAIR_HYPOTHESES__12_GDT737_QUARANTINES__"
    "ZERO_SOURCE_LITERAL_PROSE_SPOKEN__172_BACKGROUND_HYPOTHESES_PRESERVED__"
    "24_HISTORICAL_BRIDGE_TARGETS__ZERO_COMPONENT_EXPORT__NO_NEW_PAGE"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


g753 = load_module("gdt753_builder_for_gdt754", ROOT / G753_RUN_REL)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(
    path: Path, rows: Iterable[dict[str, object]], fields: Iterable[str]
) -> None:
    names = list(fields)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=names, delimiter="\t", lineterminator="\n",
            extrasaction="raise",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in names})


def joined_axes(values: Iterable[str]) -> str:
    chosen = set(values)
    return "|".join(axis for axis in AXIS_ORDER if axis in chosen) or "NONE"


def split_axes(value: str) -> set[str]:
    if not value or value == "NONE":
        return set()
    return {part for part in value.split("|") if part in AXIS_ORDER}


def axes_from_composition(composition: str) -> set[str]:
    axes: set[str] = set()
    parts = [part.upper() for part in composition.split("+")]
    joined = "_".join(parts)
    for part in parts:
        tokens = set(part.split("_"))
        if "HOT" in tokens or "K" in tokens:
            axes.add("HOT")
        if "COLD" in tokens:
            axes.add("COLD")
        if "DRY" in tokens:
            axes.add("DRY")
        if tokens & {"MOIST", "WET", "SOAK"}:
            axes.add("MOIST")
        if tokens & {"START", "BEGIN"}:
            axes.add("BEGIN_STAGE")
        if "MIDDLE" in tokens:
            axes.add("MIDDLE_STAGE")
        if tokens & {"END", "FULL"}:
            axes.add("END_STAGE")
        if re.search(r"(^|_)III($|_)", part):
            axes.add("LEVEL_III")
        elif re.search(r"(^|_)II($|_)", part):
            axes.add("LEVEL_II")
        elif re.search(r"(^|_)I($|_)", part):
            axes.add("LEVEL_I")
        if tokens & {
            "MEASURE", "AMOUNT", "DOSE", "UNIT", "HAND", "GRAN", "DROP",
        }:
            axes.add("AMOUNT")
        if tokens & {"PART", "FRACTION", "PORTION"}:
            axes.add("PART")
        if tokens & set(PATIENT_MARKERS):
            axes.add("MATERIAL")
        if tokens & {"PREP", "BASE", "EXTRACT", "DECOCT", "MIX", "MIXTURE"}:
            axes.add("PREPARATION")
        if tokens & {
            "COMMAND", "ACTION", "TAKE", "ADD", "MEASURE", "STRAIN", "POUR",
            "HEAT", "COOL", "DRY", "MOIST", "FILL",
        }:
            axes.add("PROCESS")
        if tokens & {"CLOSE", "FINISH", "FINISHED", "CLOSED"}:
            axes.add("CLOSE")
        if tokens & {"REFERENCE", "SEQUENCE", "ENTRY", "PASS"}:
            axes.add("PASS")
    if "III" in joined:
        axes.discard("LEVEL_II")
        axes.discard("LEVEL_I")
    return axes


def patient_components(composition: str) -> str:
    selected = [
        part for part in composition.split("+")
        if set(part.upper().split("_")) & set(PATIENT_MARKERS)
    ]
    return "|".join(selected) or "NONE"


def axes_from_text(value: str) -> set[str]:
    low = value.lower()
    axes: set[str] = set()
    terms = (
        ("HOT", ("heiß", "erhitz", "warm", "wärme")),
        ("COLD", ("kalt", "kühl")),
        ("DRY", ("trocken", "trockn")),
        ("MOIST", ("feucht", "einweich", "angefeuchtet")),
        ("BEGIN_STAGE", ("anfang", "beginn")),
        ("MIDDLE_STAGE", ("mittelstufe", "gradmitte", "mittlere stufe")),
        ("END_STAGE", ("endstufe", "vollstufe", "gradende", "vollständig")),
        ("AMOUNT", ("menge", "maß", "dosis")),
        ("PART", ("teil", "fraktion", "portion")),
        ("MATERIAL", ("stoff", "material", "droge")),
        ("PREPARATION", ("zubereitung", "ansatz")),
        ("PROCESS", ("vorgang", "prozess", "anweisung")),
        ("CLOSE", ("abschluss", "abschließ")),
        ("PASS", ("rückbezug", "weiter")),
    )
    for axis, needles in terms:
        if any(needle in low for needle in needles):
            axes.add(axis)
    if re.search(r"(?:stufe|index)\s+iii\b", low):
        axes.add("LEVEL_III")
    elif re.search(r"(?:stufe|index)\s+ii\b", low):
        axes.add("LEVEL_II")
    return axes


def render_axes(axes: set[str], hypothesis: bool = False) -> str:
    selected = [AXIS_DE[axis] for axis in AXIS_ORDER if axis in axes]
    if not selected:
        return "Ganzformrolle offen"
    prefix = "Arbeitshypothese: " if hypothesis else ""
    return prefix + ", ".join(selected) + "; genaue Ganzformbedeutung offen"


def load_universe() -> list[dict[str, object]]:
    source_maps: dict[str, dict[str, dict[str, str]]] = {}
    for source, path in SOURCE_DECISIONS.items():
        source_maps[source] = {row["surface"]: row for row in read_tsv(ROOT / path)}
    output: list[dict[str, object]] = []
    for row in read_tsv(ROOT / DICTIONARY_REL):
        source = row["source_gdts"]
        if source not in source_maps:
            continue
        decision = source_maps[source].get(row["surface"])
        if decision is None:
            raise AssertionError(f"missing source decision {source} {row['surface']}")
        if decision["card_type"] != "PRODUCTIVE_COMPOUND":
            continue
        if decision["working_default_de"] != row["working_meaning_de"]:
            raise AssertionError(f"source/current meaning drift {row['surface']}")
        composition_axes = axes_from_composition(decision["composition"])
        output.append({
            "surface": row["surface"],
            "reading_id": row["reading_id"],
            "current_working_meaning_de": row["working_meaning_de"],
            "current_layer": row["current_layer"],
            "current_semantic_scope": row["semantic_scope"],
            "source_dictionary_occurrences": row["occurrence_count"],
            "source_dictionary_pages": row["page_count"],
            "source_dictionary_loci": row["locus_count"],
            "current_score_not_probability": row["working_model_score_0_100_not_probability"],
            "current_confidence": row["working_model_level"],
            "source_gdt": source.split(":", 1)[0],
            "source_decision_id": decision["decision_id"],
            "source_card_type": decision["card_type"],
            "source_composition": decision["composition"],
            "source_composition_axes": joined_axes(composition_axes),
            "source_patient_or_carrier_components": patient_components(decision["composition"]),
            "source_strength": decision["strength"],
            "source_status": decision["status"],
            "source_rival_de": decision["strongest_rival_de"],
            "literal_identity": "OPEN",
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    output.sort(key=lambda row: str(row["surface"]))
    if len(output) != 172:
        raise AssertionError(f"expected 172 productive compounds, got {len(output)}")
    return output


def evidence_rows(targets: set[str]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []

    def add(
        surface: str, source: str, scope: str, tier: int, axes: set[str],
        value: str, decision: str, occurrences: object = "NA", pages: object = "NA",
    ) -> None:
        if surface not in targets:
            return
        output.append({
            "evidence_id": f"G754-E{len(output) + 1:04d}",
            "surface": surface,
            "later_source": source,
            "evidence_scope": scope,
            "strength_tier_0_4": tier,
            "role_axes": joined_axes(axes),
            "working_value_de": value or "NONE",
            "source_decision": decision,
            "source_occurrences": occurrences,
            "source_pages": pages,
            "literal_identity": "OPEN",
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })

    for row in read_tsv(ROOT / G737_QUARANTINE_REL):
        add(
            row["surface"], "GDT737", "NEGATIVE_LITERAL_PROVENANCE", 0, set(),
            row["inherited_working_meaning_de"], row["gdt737_decision"],
        )
    for row in read_tsv(ROOT / G738_CARDS_REL):
        supported = row["w23_form_decision"].startswith("SUPPORTED")
        add(
            row["surface"], "GDT738", "OCCURRENCE_SCOPED_WHOLE", 4 if supported else 1,
            axes_from_text(row["selected_whole_de"]), row["selected_whole_de"],
            row["w23_form_decision"], row["reader_exact_occurrences"],
            "NA",
        )
    for row in read_tsv(ROOT / G745_CARDS_REL):
        add(
            row["candidate_surface"], "GDT745", "FORM_ANALOGY_ROLE", 1,
            split_axes(row["analogy_consensus_axes"]), row["next_working_meaning_de"],
            row["analogy_confidence_level"], row["reader_exact_occurrences"],
            row["reader_exact_pages"],
        )
    for row in read_tsv(ROOT / G746_CENSUS_REL):
        tier = 3 if row["distribution_status"].startswith(("S2_", "S3_")) else 1
        add(
            row["candidate_surface"], "GDT746", "WHOLE_DISTRIBUTION_ROLE", tier,
            split_axes(row["gdt745_consensus_axes"]), row["next_working_meaning_de"],
            row["distribution_status"], row["reader_exact_occurrences"], "NA",
        )
    for row in read_tsv(ROOT / G748_CENSUS_REL):
        if row["role_decision"] == "NO_RECURRENT_ROLE_EXPORT":
            continue
        add(
            row["target_surface"], "GDT748", "RECURRENT_SERIAL_WHOLE_ROLE", 3,
            split_axes(row["serial_consensus_axes"]), row["automatic_working_default_de"],
            row["role_decision"], row["reader_exact_evidence_units"], row["pages"],
        )
    for row in read_tsv(ROOT / G749_CENSUS_REL):
        tier = 2 if row["outside_role_status"].startswith("K2_") else 1
        add(
            row["target_surface"], "GDT749", "OUTSIDE_WHOLE_ROLE", tier,
            split_axes(row["prior_role_axes"]), row["working_decision_de"],
            row["outside_role_status"], row["outside_occurrences_reader_exact"],
            row["outside_pages_reader_exact"],
        )
    active_750: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read_tsv(ROOT / G750_ACTIVE_REL):
        active_750[row["target_surface"]].append(row)
    for surface, rows in sorted(active_750.items()):
        axes = {axis for row in rows for axis in split_axes(row["emitted_axes"])}
        add(
            surface, "GDT750", "OCCURRENCE_SCOPED_WHOLE", 4, axes,
            " || ".join(sorted({row["working_render_de"] for row in rows})),
            "FORM_GATED_DIRECT_HOST", len(rows), len({row["page"] for row in rows}),
        )
    for row in read_tsv(ROOT / G753_PROVENANCE_REL):
        add(
            row["surface"], "GDT753", "CORRECTED_COMPLETE_PAIR_HYPOTHESIS", 2,
            {"HOT", "MIDDLE_STAGE"}, row["current_working_whole_default_de"],
            row["current_spoken_disposition"], row["current_reader_exact_occurrences"],
            row["current_reader_exact_pages"],
        )
    return output


def inventory_with_footprint(
    universe: list[dict[str, object]], context: object,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    by_surface = {str(row["surface"]): row for row in universe}
    positions: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    source_positions: list[dict[str, object]] = []
    for locus, line in context.by_line.items():
        for ordinal, token in enumerate(line, start=1):
            surface = token["eva"]
            target = by_surface.get(surface)
            if target is None:
                continue
            cell = context.cells[(locus, ordinal)]
            exact = int(context.exact[(locus, int(token["token_index"]))])
            source_active = int(
                cell["gdt734_authority_id"] == target["reading_id"]
                or cell["v99r7_semantic_value_de"] == target["current_working_meaning_de"]
            )
            row = {
                "surface": surface,
                "page": token["page"],
                "locus": locus,
                "token_ordinal": ordinal,
                "token_index": token["token_index"],
                "reader_exact": exact,
                "source_prose_active": source_active,
                "current_authority": cell["gdt734_authority_id"],
                "current_dispatch": cell["gdt734_dispatch_class"],
                "current_semantic_de": cell["v99r7_semantic_value_de"],
                "current_spoken_de": cell["v99r7_spoken_cell_de"],
                "current_confidence": cell["gdt734_confidence_level"],
                "written_line_eva": " ".join(item["eva"] for item in line),
            }
            positions[surface].append(row)
            if source_active:
                source_positions.append(row)
    output: list[dict[str, object]] = []
    quarantine = {row["surface"]: row for row in read_tsv(ROOT / G737_QUARANTINE_REL)}
    for base in universe:
        surface = str(base["surface"])
        rows = positions[surface]
        active = [row for row in rows if int(row["source_prose_active"])]
        exact = [row for row in rows if int(row["reader_exact"])]
        qrow = quarantine.get(surface)
        enriched = dict(base)
        enriched.update({
            "current_cache_cells": len(rows),
            "current_cache_pages": len({str(row["page"]) for row in rows}),
            "current_reader_exact_cells": len(exact),
            "current_reader_exact_pages": len({str(row["page"]) for row in exact}),
            "current_source_prose_active_cells": len(active),
            "current_source_prose_active_pages": len({str(row["page"]) for row in active}),
            "current_authority_counts": "|".join(
                f"{name}:{count}" for name, count in sorted(
                    Counter(str(row["current_authority"]) for row in rows).items()
                )
            ) or "NONE",
            "gdt737_quarantine_decision": qrow["gdt737_decision"] if qrow else "NO_GDT737_QUARANTINE_ROW",
            "gdt737_retired_head_words": qrow["retired_head_words_detected"] if qrow else "NONE",
        })
        output.append(enriched)
    output.sort(key=lambda row: (-int(row["current_source_prose_active_cells"]), str(row["surface"])))
    return output, source_positions


def decision_rows(
    inventory: list[dict[str, object]], evidence: list[dict[str, object]],
) -> list[dict[str, object]]:
    by_surface: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for row in evidence:
        by_surface[str(row["surface"])].append(row)
    explicit_753 = {
        row["surface"]: row for row in read_tsv(ROOT / G753_PROVENANCE_REL)
    }
    output: list[dict[str, object]] = []
    for row in inventory:
        surface = str(row["surface"])
        items = by_surface[surface]
        positive = [item for item in items if int(item["strength_tier_0_4"]) > 0]
        strongest = max((int(item["strength_tier_0_4"]) for item in positive), default=0)
        high_axes = {
            axis for item in positive if int(item["strength_tier_0_4"]) >= 2
            for axis in split_axes(str(item["role_axes"]))
        }
        any_axes = {
            axis for item in positive for axis in split_axes(str(item["role_axes"]))
        }
        source_axes = split_axes(str(row["source_composition_axes"]))
        sources = sorted({str(item["later_source"]) for item in positive})
        local_sources = sorted({
            str(item["later_source"]) for item in positive
            if item["evidence_scope"] == "OCCURRENCE_SCOPED_WHOLE"
        })
        recurring_sources = sorted({
            str(item["later_source"]) for item in positive
            if item["evidence_scope"] in {
                "WHOLE_DISTRIBUTION_ROLE", "RECURRENT_SERIAL_WHOLE_ROLE",
                "OUTSIDE_WHOLE_ROLE",
            } and int(item["strength_tier_0_4"]) >= 2
        })
        if surface in explicit_753:
            disposition = "CORRECTED_PAIR_SHARED_ROLE_HYPOTHESIS"
            confidence = "H1_CORRECTED_WHOLE_PAIR_HYPOTHESIS"
            spoken = explicit_753[surface]["current_working_whole_default_de"]
            background = explicit_753[surface]["retained_background_hypothesis_de"]
            selected_axes = {"HOT", "MIDDLE_STAGE"}
        elif recurring_sources and high_axes:
            disposition = "REPLACE_LITERAL_PROSE_WITH_LATER_WHOLE_ROLE"
            confidence = "R2_LATER_RECURRENT_OR_OUTSIDE_WHOLE_ROLE"
            selected_axes = high_axes
            spoken = render_axes(selected_axes)
            background = render_axes(source_axes, hypothesis=True)
        elif local_sources and high_axes:
            disposition = "GLOBAL_COMPOSITION_HYPOTHESIS_PLUS_LOCAL_ROLE_PATCH"
            confidence = "R2_OCCURRENCE_SCOPED_ROLE_GLOBAL_HYPOTHESIS_ONLY"
            selected_axes = high_axes
            spoken = render_axes(source_axes, hypothesis=True)
            background = render_axes(source_axes, hypothesis=True)
        elif high_axes:
            disposition = "REPLACE_LITERAL_PROSE_WITH_WEAK_LATER_ROLE"
            confidence = "R1_WEAK_LATER_WHOLE_ROLE"
            selected_axes = high_axes
            spoken = render_axes(selected_axes, hypothesis=True)
            background = render_axes(source_axes, hypothesis=True)
        elif any_axes:
            disposition = "FORM_ANALOGY_ROLE_HYPOTHESIS_ONLY"
            confidence = "R1_FORM_ANALOGY_ONLY"
            selected_axes = any_axes
            spoken = render_axes(selected_axes, hypothesis=True)
            background = render_axes(source_axes, hypothesis=True)
        elif source_axes:
            disposition = "COMPOSITION_AXES_HYPOTHESIS_ONLY"
            confidence = "H0_SOURCE_COMPOSITION_BACKGROUND_ONLY"
            selected_axes = source_axes
            spoken = render_axes(selected_axes, hypothesis=True)
            background = spoken
        else:
            disposition = "OPEN_EXACT_WHOLE_AFTER_PROVENANCE_SIEVE"
            confidence = "H0_OPEN"
            selected_axes = set()
            spoken = "Ganzformrolle offen"
            background = "alte Kompositionsprosa bleibt als ersetzbare Hypothese archiviert"
        output.append({
            "surface": surface,
            "reading_id": row["reading_id"],
            "current_source_prose_de": row["current_working_meaning_de"],
            "source_composition": row["source_composition"],
            "source_composition_axes": row["source_composition_axes"],
            "source_patient_or_carrier_components": row["source_patient_or_carrier_components"],
            "current_source_prose_active_cells": row["current_source_prose_active_cells"],
            "current_source_prose_active_pages": row["current_source_prose_active_pages"],
            "current_reader_exact_cells": row["current_reader_exact_cells"],
            "gdt737_quarantine_decision": row["gdt737_quarantine_decision"],
            "later_evidence_sources": "|".join(sources) or "NONE",
            "later_local_role_sources": "|".join(local_sources) or "NONE",
            "later_recurring_role_sources": "|".join(recurring_sources) or "NONE",
            "strongest_later_evidence_tier_0_4": strongest,
            "later_role_axes_any": joined_axes(any_axes),
            "later_role_axes_selected": joined_axes(selected_axes),
            "source_literal_prose_spoken_after_gdt754": 0,
            "renderer_disposition": disposition,
            "renderer_confidence": confidence,
            "current_working_whole_default_de": spoken,
            "retained_background_hypothesis_de": background,
            "literal_identity": "OPEN",
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    output.sort(key=lambda row: (-int(row["current_source_prose_active_cells"]), str(row["surface"])))
    return output


def position_patch_rows(
    source_positions: list[dict[str, object]], decisions: list[dict[str, object]],
) -> list[dict[str, object]]:
    by_surface = {str(row["surface"]): row for row in decisions}
    g738_local: defaultdict[tuple[str, str], list[str]] = defaultdict(list)
    for row in read_tsv(ROOT / G738_PATCH_REL):
        g738_local[(row["locus"], row["token_index"])].append(
            row["gdt738_scoped_whole_render_de"]
        )
    g750_local: defaultdict[tuple[str, str], list[str]] = defaultdict(list)
    for row in read_tsv(ROOT / G750_ACTIVE_REL):
        g750_local[(row["locus"], row["token_ordinal"])].append(
            row["working_render_de"]
        )
    output: list[dict[str, object]] = []
    for number, row in enumerate(source_positions, start=1):
        decision = by_surface[str(row["surface"])]
        key_738 = (str(row["locus"]), str(row["token_index"]))
        key_750 = (str(row["locus"]), str(row["token_ordinal"]))
        if key_750 in g750_local:
            scope = "GDT750_OCCURRENCE_ROLE_PRESERVED"
            render = " / ".join(sorted(set(g750_local[key_750]))) + "; genaue Identität offen"
        elif key_738 in g738_local:
            scope = "GDT738_OCCURRENCE_ROLE_PRESERVED"
            render = " / ".join(sorted(set(g738_local[key_738])))
        else:
            scope = "GDT754_WHOLE_DEFAULT"
            render = str(decision["current_working_whole_default_de"])
        output.append({
            "gdt754_patch_id": f"G754-P{number:04d}",
            "surface": row["surface"],
            "page": row["page"],
            "locus": row["locus"],
            "token_ordinal": row["token_ordinal"],
            "token_index": row["token_index"],
            "reader_exact": row["reader_exact"],
            "current_authority": row["current_authority"],
            "old_source_prose_de": row["current_semantic_de"],
            "old_spoken_de": row["current_spoken_de"],
            "patch_scope": scope,
            "gdt754_render_de": render,
            "background_hypothesis_de": decision["retained_background_hypothesis_de"],
            "written_line_eva": row["written_line_eva"],
            "literal_identity": "OPEN",
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    return output


def bridge_family(axes: set[str]) -> tuple[str, str]:
    if axes & {"AMOUNT", "PART", "LEVEL_I", "LEVEL_II", "LEVEL_III"}:
        return (
            "MEASURE_FRACTION_OR_DEGREE_REGISTER",
            "historische Maß-, Fraktions- und Gradkürzel gegen die Ganzformrolle vergleichen",
        )
    if "PROCESS" in axes:
        return (
            "RECIPE_ACTION_OR_COMMAND_REGISTER",
            "historische Rezeptverben und gebundene Anweisungskürzel als Ganzformen vergleichen",
        )
    if axes & {"MATERIAL", "PREPARATION"}:
        return (
            "LEARNED_DRUG_OR_PREPARATION_HEADWORD_REGISTER",
            "historische Drogen- und Zubereitungslemmata ohne EVA-Initialdeutung vergleichen",
        )
    if axes & {"HOT", "COLD", "DRY", "MOIST", "BEGIN_STAGE", "MIDDLE_STAGE", "END_STAGE"}:
        return (
            "QUALITY_STATE_OR_DEGREE_REGISTER",
            "historische Qualitäts-, Zustands- und Gradfelder als Ganzformmuster vergleichen",
        )
    return (
        "OPAQUE_TECHNICAL_HEADWORD_REGISTER",
        "historische gelernte Fachlemmata und Siglenregister ohne Teilstringwert vergleichen",
    )


def bridge_deck(decisions: list[dict[str, object]]) -> list[dict[str, object]]:
    ranked = sorted(
        decisions,
        key=lambda row: (
            -int(row["current_source_prose_active_cells"]),
            -int(row["strongest_later_evidence_tier_0_4"]),
            str(row["surface"]),
        ),
    )[:24]
    output: list[dict[str, object]] = []
    for rank, row in enumerate(ranked, start=1):
        axes = split_axes(str(row["later_role_axes_selected"]))
        family, task = bridge_family(axes)
        output.append({
            "bridge_rank": rank,
            "surface": row["surface"],
            "current_source_prose_active_cells": row["current_source_prose_active_cells"],
            "current_source_prose_active_pages": row["current_source_prose_active_pages"],
            "strongest_later_evidence_tier_0_4": row["strongest_later_evidence_tier_0_4"],
            "selected_role_axes": row["later_role_axes_selected"],
            "current_working_whole_default_de": row["current_working_whole_default_de"],
            "old_source_prose_de": row["current_source_prose_de"],
            "renderer_disposition": row["renderer_disposition"],
            "historical_register_family": family,
            "next_historical_comparison_de": task,
            "comparison_unit": "EXACT_COMPLETE_SURFACE_ONLY",
            "eva_initial_or_substring_value_allowed": 0,
            "literal_identity": "OPEN",
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    return output


def write_reader(
    path: Path, decisions: list[dict[str, object]], bridge: list[dict[str, object]],
) -> None:
    counts = Counter(str(row["renderer_disposition"]) for row in decisions)
    total_cells = sum(int(row["current_source_prose_active_cells"]) for row in decisions)
    lines = [
        "# GDT754 productive-compound provenance reader", "",
        f"The active source universe contains **{len(decisions)}** GDT664/GDT666 `PRODUCTIVE_COMPOUND` whole cards and **{total_cells}** currently source-prose-active cached cells.",
        "", "## Disposition census", "",
        "| disposition | surfaces |",
        "|---|---:|",
    ]
    for name, count in sorted(counts.items()):
        lines.append(f"| {name} | {count} |")
    lines.extend([
        "", "Every old literal compound sentence leaves the spoken whole layer; none is deleted from the background hypothesis channel. Later whole-role evidence, where available, replaces literal patients and exact operations with compact role axes.",
        "", "## Highest current footprints", "",
        "| form | active cells/pages | old source prose | later tier/axes | current working default |",
        "|---|---:|---|---|---|",
    ])
    for row in decisions[:30]:
        lines.append(
            f"| `{row['surface']}` | {row['current_source_prose_active_cells']}/{row['current_source_prose_active_pages']} | "
            f"{row['current_source_prose_de']} | {row['strongest_later_evidence_tier_0_4']} / "
            f"{row['later_role_axes_selected']} | {row['current_working_whole_default_de']} |"
        )
    lines.extend([
        "", "## Next historical bridge deck", "",
        "| rank | form | role axes | comparator family |",
        "|---:|---|---|---|",
    ])
    for row in bridge:
        lines.append(
            f"| {row['bridge_rank']} | `{row['surface']}` | {row['selected_role_axes']} | "
            f"{row['historical_register_family']} |"
        )
    lines.extend([
        "", "The bridge deck compares exact whole forms and historical register functions. It does not read EVA characters as Latin initials and grants no substring or lexeme value.",
    ])
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    universe = load_universe()
    targets = {str(row["surface"]) for row in universe}
    context, _, guard = g753.g752.g751.load_context()
    inventory, source_positions = inventory_with_footprint(universe, context)
    evidence = evidence_rows(targets)
    decisions = decision_rows(inventory, evidence)
    patches = position_patch_rows(source_positions, decisions)
    bridge = bridge_deck(decisions)

    write_tsv(output_dir / OUTPUT_NAMES[0], inventory, list(inventory[0]))
    write_tsv(output_dir / OUTPUT_NAMES[1], evidence, list(evidence[0]))
    write_tsv(output_dir / OUTPUT_NAMES[2], decisions, list(decisions[0]))
    write_tsv(output_dir / OUTPUT_NAMES[3], patches, list(patches[0]))
    write_tsv(output_dir / OUTPUT_NAMES[4], bridge, list(bridge[0]))
    write_reader(output_dir / OUTPUT_NAMES[5], decisions, bridge)

    disposition_counts = Counter(str(row["renderer_disposition"]) for row in decisions)
    evidence_source_counts = Counter(str(row["later_source"]) for row in evidence)
    positive_evidence_surfaces = {
        str(row["surface"]) for row in evidence
        if int(row["strength_tier_0_4"]) > 0
    }
    negative_quarantine_surfaces = {
        str(row["surface"]) for row in evidence
        if row["evidence_scope"] == "NEGATIVE_LITERAL_PROVENANCE"
    }
    patch_scope_counts = Counter(str(row["patch_scope"]) for row in patches)
    result = {
        "schema": "GDT754_RESULT_V1",
        "status": STATUS,
        "scope": {
            "active_gdt664_gdt666_productive_compound_surfaces": len(universe),
            "source_dictionary_occurrence_sum": sum(int(row["source_dictionary_occurrences"]) for row in universe),
            "current_cache_cells_on_target_surfaces": sum(int(row["current_cache_cells"]) for row in inventory),
            "current_reader_exact_cells_on_target_surfaces": sum(int(row["current_reader_exact_cells"]) for row in inventory),
            "current_source_prose_active_cells": len(source_positions),
            "current_source_prose_active_pages": len({str(row["page"]) for row in source_positions}),
            "later_evidence_rows": len(evidence),
            "later_positive_evidence_surfaces": len(positive_evidence_surfaces),
            "gdt737_negative_quarantine_surfaces": len(negative_quarantine_surfaces),
            "historical_bridge_deck": len(bridge),
        },
        "disposition_counts": dict(sorted(disposition_counts.items())),
        "later_evidence_source_counts": dict(sorted(evidence_source_counts.items())),
        "renderer_correction": {
            "source_literal_prose_surfaces_spoken_after_gdt754": 0,
            "source_literal_prose_cells_spoken_after_gdt754": 0,
            "background_composition_hypotheses_preserved": sum(
                int(row["retained_background_hypothesis_de"] != "NONE") for row in decisions
            ),
            "position_patches": len(patches),
            "position_patch_scope_counts": dict(sorted(patch_scope_counts.items())),
        },
        "guard": guard,
        "claim_boundary": {
            "confirmed_lexemes": 0,
            "component_export_credit": 0,
            "historical_word_matches": 0,
            "plaintext_clauses": 0,
            "new_pages": 0,
            "f84_accessed": False,
            "f84r_accessed": False,
        },
    }
    (output_dir / OUTPUT_NAMES[6]).write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_ARTIFACTS)
    args = parser.parse_args()
    result = build(args.output_dir)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
