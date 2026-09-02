#!/usr/bin/env python3
"""Crosswalk GDT754's top 24 complete forms against historical register expressions."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
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
BASE_REL = Path("experiments/yolo/gdt755_top24_historical_register_crosswalk")
EXP = ROOT / BASE_REL
SRC = EXP / "src"
DEFAULT_ARTIFACTS = EXP / "artifacts"
G753_RUN_REL = Path(
    "experiments/yolo/gdt753_qokeol_okeol_whole_role_census/src/run.py"
)
G754_TOP_REL = Path(
    "experiments/yolo/gdt754_active_productive_compound_provenance_sieve/"
    "artifacts/TOP_24_HISTORICAL_VOCABULARY_BRIDGE_DECK.tsv"
)
G754_INVENTORY_REL = Path(
    "experiments/yolo/gdt754_active_productive_compound_provenance_sieve/"
    "artifacts/ACTIVE_172_PRODUCTIVE_COMPOUND_INVENTORY.tsv"
)
OUTPUT_NAMES = (
    "TOP24_448_OCCURRENCE_FIELDS.tsv",
    "TOP24_CHANNEL_CENSUS.tsv",
    "EXACT_FORM_INITIAL_POSITION_COMPARATOR.tsv",
    "TOP24_CANDIDATE_RANKING.tsv",
    "TOP24_WORKING_GLOSS_UPDATE.tsv",
    "CONCRETE_VOCABULARY_SLOT_AUDIT.tsv",
    "TOP24_448_CANDIDATE_RENDERER.tsv",
    "GDT755_HISTORICAL_REGISTER_READER.md",
    "RESULT.json",
)
AXIS_ORDER = (
    "HOT", "COLD", "DRY", "MOIST", "AMOUNT", "PART", "MATERIAL",
    "PREPARATION", "PROCESS", "CLOSE", "PASS", "BEGIN_STAGE",
    "MIDDLE_STAGE", "END_STAGE", "LEVEL_I", "LEVEL_II", "LEVEL_III",
    "LIQUID", "WATER", "WINE", "OIL", "SALT", "PLANT_PART", "ROOT",
    "LEAF", "SEED", "WOOD", "POWDER", "VESSEL", "PERSON", "FEMALE",
    "DISEASE", "TREATMENT", "BATH", "HONEY", "INGREDIENT",
)
CONTENT_AUDIT = (
    ("Wasser", "E029"), ("Wein", "E030"), ("Oel", "E028"),
    ("Salz", "E031"), ("Wurzel", "E034"), ("Blatt", "E032"),
    ("Samen", "E033"), ("Holz", "E035"), ("Pulver", "E036"),
    ("Honig", "E042"), ("Aqua vitae", "E045"), ("Gefaess", "E037"),
    ("Frau", "E041"), ("Krankheit", "E038"),
    ("Heilmittel oder Behandlung", "E040"), ("Salbe", "E026"),
    ("Latwerge", "E039"), ("nimm", "E016"), ("mischen", "E018"),
    ("zerreiben", "E044"), ("erwaermen oder kochen", "E021"),
    ("abkuehlen", "E020"), ("trocknen", "E043"),
    ("einweichen", "E023"), ("aufbewahren", "E027"),
    ("baden", "E052"),
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


g753 = load_module("gdt753_builder_for_gdt755", ROOT / G753_RUN_REL)


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


def values(text: str) -> set[str]:
    return {value for value in text.split("|") if value and value != "NONE"}


def joined(items: Iterable[str]) -> str:
    chosen = set(items)
    ordered = [axis for axis in AXIS_ORDER if axis in chosen]
    ordered.extend(sorted(chosen - set(ordered)))
    return "|".join(ordered) or "NONE"


def line_position(ordinal: int, length: int) -> str:
    if length == 1:
        return "SINGLE"
    if ordinal == 1:
        return "FIRST"
    if ordinal == length:
        return "LAST"
    return "MIDDLE"


def scan_side(
    context: object,
    locus: str,
    target_ordinal: int,
    direction: int,
    suspect_surfaces: set[str],
) -> tuple[list[dict[str, object]], str]:
    line = context.by_line[locus]
    output: list[dict[str, object]] = []
    boundary = "RADIUS5_CENSORED"
    for distance in range(1, 6):
        ordinal = target_ordinal + direction * distance
        if not 1 <= ordinal <= len(line):
            boundary = f"LINE_EDGE_AFTER_R{distance - 1}"
            break
        token, cell, raw_axes = g753.g752.clean_cell(context, locus, ordinal)
        surface = token["eva"]
        if g753.g752.g751.g750.g749.g746.g745.g739.strict_initial_head(surface):
            boundary = f"STRICT_INITIAL_BEFORE_R{distance}"
            break
        excluded = surface in suspect_surfaces
        axes = set() if excluded else set(raw_axes)
        if direction == -1 and "CLOSE" in axes:
            boundary = f"PRIOR_CLOSE_BEFORE_R{distance}"
            break
        output.append({
            "side": "L" if direction == -1 else "R",
            "distance": distance,
            "ordinal": ordinal,
            "surface": surface,
            "semantic": cell["v99r7_semantic_value_de"],
            "confidence": cell["gdt734_confidence_level"],
            "unknown": int(cell["unknown_v99r7"]),
            "axes": axes,
            "suspect_compound_axes_excluded": int(excluded and bool(raw_axes)),
        })
        if direction == 1 and "CLOSE" in axes:
            boundary = f"CURRENT_CLOSE_INCLUDED_R{distance}"
            break
    return output, boundary


def build_occurrences(
    deck: list[dict[str, str]],
    suspect_surfaces: set[str],
    context: object,
    line_meta: dict[str, dict[str, str]],
    rules: list[dict[str, str]],
) -> list[dict[str, object]]:
    targets = {row["surface"]: row for row in deck}
    output: list[dict[str, object]] = []
    number = 0
    for locus, line in context.by_line.items():
        written = " ".join(token["eva"] for token in line)
        for ordinal, token in enumerate(line, start=1):
            target = targets.get(token["eva"])
            if target is None:
                continue
            if not context.exact[(locus, int(token["token_index"]))]:
                continue
            number += 1
            left, left_reason = scan_side(
                context, locus, ordinal, -1, suspect_surfaces
            )
            right, right_reason = scan_side(
                context, locus, ordinal, 1, suspect_surfaces
            )
            span = left + right
            anchors = [item for item in span if item["axes"]]
            tags = {axis for item in anchors for axis in item["axes"]}
            channel = g753.g752.g744.channel_for(tags, rules)
            evidence = " || ".join(
                f"{item['side']}{item['distance']} {item['surface']}="
                f"{item['semantic']} [{joined(item['axes'])};{item['confidence']}]"
                for item in sorted(anchors, key=lambda item: int(item["ordinal"]))
            ) or "NONE"
            complete = int(
                not left_reason.startswith("RADIUS5")
                and not right_reason.startswith("RADIUS5")
            )
            meta = line_meta[locus]
            cell = context.cells[(locus, ordinal)]
            output.append({
                "gdt755_occurrence_id": f"G755-O{number:04d}",
                "bridge_rank": target["bridge_rank"],
                "surface": token["eva"],
                "selected_role_axes_not_used_as_self_anchor": target["selected_role_axes"],
                "gdt754_whole_default_not_used_as_self_anchor": target["current_working_whole_default_de"],
                "page": token["page"],
                "physical_folio": g753.g752.g751.g750.g749.g746.g745.physical_folio(token["page"]),
                "locus": locus,
                "token_ordinal": ordinal,
                "line_token_count": len(line),
                "normalized_position": f"{(ordinal - 1) / max(1, len(line) - 1):.6f}",
                "line_position": line_position(ordinal, len(line)),
                "paragraph_first_token": int(meta["paragraph_start"] == "1" and ordinal == 1),
                "paragraph_last_token": int(meta["paragraph_end"] == "1" and ordinal == len(line)),
                "section": token["section"],
                "language": token["language"],
                "hand": token["hand"],
                "written_line_eva": written,
                "left_extent": len(left),
                "right_extent": len(right),
                "left_boundary_reason": left_reason,
                "right_boundary_reason": right_reason,
                "boundary_complete": complete,
                "independent_anchor_count": len(anchors),
                "independent_anchor_surfaces": "|".join(
                    str(item["surface"]) for item in anchors
                ) or "NONE",
                "independent_anchor_tags": joined(tags),
                "independent_anchor_evidence": evidence,
                "field_channel": channel,
                "slot_class": g753.g752.g744.content_slot_class(channel, tags),
                "suspect_172_neighbor_cells_with_axes_excluded": sum(
                    int(item["suspect_compound_axes_excluded"]) for item in span
                ),
                "unknown_neighbor_cells": sum(int(item["unknown"]) for item in span),
                "target_current_cache_value_not_used_as_anchor": cell["v99r7_semantic_value_de"],
                "target_current_cache_confidence_not_used_as_anchor": cell["gdt734_confidence_level"],
                "all_172_productive_compound_axes_excluded_from_field": 1,
                "reader_exact_target": 1,
                "literal_identity": "OPEN",
                "confirmed_lexeme": 0,
                "component_export_credit": 0,
            })
    return output


def count_text(values_in: Iterable[str]) -> str:
    counts = Counter(values_in)
    return "|".join(f"{key}:{counts[key]}" for key in sorted(counts)) or "NONE"


def axis_count_text(rows: Iterable[dict[str, object]]) -> str:
    counts: Counter[str] = Counter()
    for row in rows:
        counts.update(values(str(row["independent_anchor_tags"])))
    return "|".join(
        f"{axis}:{counts[axis]}" for axis in AXIS_ORDER if counts[axis]
    ) or "NONE"


def build_census(
    deck: list[dict[str, str]], occurrences: list[dict[str, object]]
) -> list[dict[str, object]]:
    grouped: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for row in occurrences:
        grouped[str(row["surface"])].append(row)
    output: list[dict[str, object]] = []
    for target in deck:
        surface = target["surface"]
        rows = grouped[surface]
        complete = [row for row in rows if int(row["boundary_complete"])]
        nonopen = [row for row in complete if row["field_channel"] != "OPEN"]
        nonopen_counts = Counter(str(row["field_channel"]) for row in nonopen)
        dominant = (
            sorted(nonopen_counts, key=lambda key: (-nonopen_counts[key], key))[0]
            if nonopen_counts else "NONE"
        )
        output.append({
            "bridge_rank": target["bridge_rank"],
            "surface": surface,
            "selected_role_axes": target["selected_role_axes"],
            "gdt754_historical_register_family": target["historical_register_family"],
            "strongest_later_evidence_tier_0_4": target["strongest_later_evidence_tier_0_4"],
            "reader_exact_occurrences": len(rows),
            "reader_exact_pages": len({str(row["page"]) for row in rows}),
            "complete_independent_fields": len(complete),
            "complete_independent_field_pages": len({str(row["page"]) for row in complete}),
            "anchored_complete_fields": sum(int(row["independent_anchor_count"]) > 0 for row in complete),
            "nonopen_complete_fields": len(nonopen),
            "nonopen_complete_field_rate": f"{len(nonopen) / len(complete):.6f}" if complete else "0.000000",
            "dominant_nonopen_channel": dominant,
            "dominant_nonopen_channel_count": nonopen_counts[dominant] if nonopen_counts else 0,
            "complete_channel_counts": count_text(str(row["field_channel"]) for row in complete),
            "all_field_channel_counts": count_text(str(row["field_channel"]) for row in rows),
            "complete_independent_anchor_axis_counts": axis_count_text(complete),
            "line_first_occurrences": sum(row["line_position"] in {"FIRST", "SINGLE"} for row in rows),
            "line_last_occurrences": sum(row["line_position"] in {"LAST", "SINGLE"} for row in rows),
            "paragraph_first_occurrences": sum(int(row["paragraph_first_token"]) for row in rows),
            "paragraph_last_occurrences": sum(int(row["paragraph_last_token"]) for row in rows),
            "mean_normalized_position": f"{sum(float(row['normalized_position']) for row in rows) / len(rows):.6f}",
            "section_counts": count_text(str(row["section"]) for row in rows),
            "suspect_neighbor_axes_excluded": sum(int(row["suspect_172_neighbor_cells_with_axes_excluded"]) for row in rows),
            "all_172_productive_compound_axes_excluded_from_fields": 1,
            "literal_identity": "OPEN",
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    return output


def build_position_comparator(
    context: object,
    line_meta: dict[str, dict[str, str]],
    target_surfaces: set[str],
    suspect_surfaces: set[str],
) -> list[dict[str, object]]:
    grouped: defaultdict[str, list[tuple[int, int, int, str]]] = defaultdict(list)
    for locus, line in context.by_line.items():
        meta = line_meta[locus]
        for ordinal, token in enumerate(line, start=1):
            if not context.exact[(locus, int(token["token_index"]))]:
                continue
            grouped[token["eva"]].append((
                int(ordinal == 1),
                int(ordinal == len(line)),
                int(meta["paragraph_start"] == "1" and ordinal == 1),
                token["section"],
            ))
    eligible = [
        (surface, rows) for surface, rows in grouped.items() if len(rows) >= 10
    ]
    eligible.sort(key=lambda item: (
        -sum(row[0] for row in item[1]) / len(item[1]),
        -len(item[1]), item[0],
    ))
    output: list[dict[str, object]] = []
    for rank, (surface, rows) in enumerate(eligible, start=1):
        first = sum(row[0] for row in rows)
        output.append({
            "line_initial_rate_rank": rank,
            "surface": surface,
            "reader_exact_occurrences": len(rows),
            "line_first_occurrences": first,
            "line_first_rate": f"{first / len(rows):.6f}",
            "line_last_occurrences": sum(row[1] for row in rows),
            "paragraph_first_occurrences": sum(row[2] for row in rows),
            "section_counts": count_text(row[3] for row in rows),
            "top24_target": int(surface in target_surfaces),
            "gdt754_productive_compound_surface": int(surface in suspect_surfaces),
            "comparison_used_semantics": 0,
            "reader_exact_minimum_occurrences": 10,
            "confirmed_lexeme": 0,
        })
    return output


def layout_match(position: str, preferred: set[str]) -> bool:
    if not preferred or "ANY" in preferred:
        return True
    if position == "SINGLE":
        return bool({"FIRST", "LAST", "SINGLE"} & preferred)
    return position in preferred


def build_rankings(
    deck: list[dict[str, str]],
    priors: list[dict[str, str]],
    bank: dict[str, dict[str, str]],
    sources: dict[str, dict[str, str]],
    occurrences: list[dict[str, object]],
) -> list[dict[str, object]]:
    target_by_surface = {row["surface"]: row for row in deck}
    occurrence_by_surface: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for row in occurrences:
        occurrence_by_surface[str(row["surface"])].append(row)
    output: list[dict[str, object]] = []
    for prior in priors:
        surface = prior["surface"]
        target = target_by_surface[surface]
        target_axes = values(target["selected_role_axes"])
        target_rows = occurrence_by_surface[surface]
        complete = [row for row in target_rows if int(row["boundary_complete"])]
        candidate_ids = (
            prior["primary_candidate_id"], prior["alternate_candidate_1"],
            prior["alternate_candidate_2"],
        )
        for candidate_rank, candidate_id in enumerate(candidate_ids, start=1):
            candidate = bank[candidate_id]
            required_all = values(candidate["required_all_axes"])
            required_any = values(candidate["required_any_axes"])
            preferred_axes = values(candidate["preferred_axes"])
            preferred_channels = values(candidate["preferred_channels"])
            preferred_layout = values(candidate["preferred_layout"])
            hard_fit = required_all <= target_axes and (
                not required_any or bool(required_any & target_axes)
            )
            channel_hits = sum(
                str(row["field_channel"]) in preferred_channels for row in complete
            ) if preferred_channels else len(complete)
            channel_rate = channel_hits / len(complete) if complete else 0.0
            layout_hits = sum(
                layout_match(str(row["line_position"]), preferred_layout)
                for row in target_rows
            )
            layout_rate = layout_hits / len(target_rows) if target_rows else 0.0
            register_match = int(
                candidate["historical_register_family"]
                == target["historical_register_family"]
            )
            content_axis = candidate["content_slot_axis"]
            content_supported = int(
                content_axis == "NONE" or bool(values(content_axis) & target_axes)
            )
            preferred_overlap = preferred_axes & target_axes
            score = (
                30.0 * int(hard_fit)
                + min(15.0, 5.0 * len(required_all & target_axes))
                + min(10.0, 2.0 * len(preferred_overlap))
                + 20.0 * channel_rate + 15.0 * layout_rate
                + 8.0 * register_match + 4.0 * int(candidate["date_tier_0_3"])
                - 30.0 * int(not content_supported)
            )
            score = max(0.0, min(100.0, score))
            source_summary = " || ".join(
                f"{source_id}: {sources[source_id]['work']} ({sources[source_id]['date_band']})"
                for source_id in sorted(values(candidate["source_ids"]))
            )
            counter: list[str] = []
            if not hard_fit:
                counter.append("required target axes incomplete")
            if not content_supported:
                counter.append(f"literal {content_axis} axis absent")
            if complete and channel_hits == 0:
                counter.append("zero preferred-channel complete fields")
            if not complete:
                counter.append("zero complete fields")
            if not register_match:
                counter.append("changes GDT754 broad register family")
            output.append({
                "surface": surface,
                "bridge_rank": target["bridge_rank"],
                "candidate_rank": candidate_rank,
                "selected_primary": int(candidate_rank == 1),
                "candidate_id": candidate_id,
                "historical_expression": candidate["normalized_expression"],
                "candidate_base_gloss_de": candidate["working_gloss_de"],
                "target_specific_working_candidate_de": (
                    prior["working_candidate_de"] if candidate_rank == 1
                    else candidate["working_gloss_de"]
                ),
                "working_confidence_if_primary": prior["working_confidence"] if candidate_rank == 1 else "ALTERNATE_NOT_SELECTED",
                "candidate_kind": candidate["candidate_kind"],
                "candidate_register_family": candidate["historical_register_family"],
                "gdt754_register_family": target["historical_register_family"],
                "register_family_match": register_match,
                "target_role_axes": target["selected_role_axes"],
                "candidate_required_all_axes": candidate["required_all_axes"],
                "candidate_required_any_axes": candidate["required_any_axes"],
                "hard_role_fit": int(hard_fit),
                "preferred_axis_overlap": joined(preferred_overlap),
                "content_slot_axis": content_axis,
                "literal_content_axis_supported": content_supported,
                "reader_exact_occurrences": len(target_rows),
                "complete_independent_fields": len(complete),
                "preferred_channel_hits": channel_hits,
                "preferred_channel_rate": f"{channel_rate:.6f}",
                "layout_hits": layout_hits,
                "layout_rate": f"{layout_rate:.6f}",
                "historical_date_tier_0_3": candidate["date_tier_0_3"],
                "historical_source_ids": candidate["source_ids"],
                "historical_source_summary": source_summary,
                "attested_form": candidate["attested_form"],
                "historical_locator": candidate["locator"],
                "attestation_scope": candidate["attestation_scope"],
                "fit_score_0_100_diagnostic": f"{score:.3f}",
                "selection_reason_if_primary": prior["selection_reason"] if candidate_rank == 1 else "ALTERNATE_RIVAL",
                "counterevidence": "; ".join(counter) or "NONE",
                "comparison_unit": "EXACT_COMPLETE_SURFACE_ROLE_NOT_EVA_SPELLING",
                "historical_graphic_match_claimed": 0,
                "literal_identity": "OPEN",
                "confirmed_lexeme": 0,
                "component_export_credit": 0,
            })
    return output


def build_gloss_updates(
    deck: list[dict[str, str]],
    priors: list[dict[str, str]],
    rankings: list[dict[str, object]],
    census: list[dict[str, object]],
) -> list[dict[str, object]]:
    prior_by_surface = {row["surface"]: row for row in priors}
    primary = {
        str(row["surface"]): row for row in rankings if int(row["selected_primary"])
    }
    census_by_surface = {str(row["surface"]): row for row in census}
    output: list[dict[str, object]] = []
    for target in deck:
        surface = target["surface"]
        prior = prior_by_surface[surface]
        candidate = primary[surface]
        stats = census_by_surface[surface]
        evidence = (
            f"whole axes {target['selected_role_axes']}; {stats['reader_exact_occurrences']} exact occurrences, "
            f"{stats['complete_independent_fields']} complete external fields; complete channels "
            f"{stats['complete_channel_counts']}; layout first/last "
            f"{stats['line_first_occurrences']}/{stats['line_last_occurrences']}; historical "
            f"{candidate['attested_form']} ({candidate['historical_source_ids']})"
        )
        counter = str(candidate["counterevidence"])
        if prior["working_confidence"] == "C0_FORCED_DEFAULT":
            counter = (
                ("; " if counter != "NONE" else "")
                + "forced concrete default remains easy to replace"
            ).lstrip("; ")
        output.append({
            "bridge_rank": target["bridge_rank"],
            "surface": surface,
            "gdt754_working_whole_default_de": target["current_working_whole_default_de"],
            "gdt755_primary_historical_expression": candidate["historical_expression"],
            "gdt755_working_candidate_de": prior["working_candidate_de"],
            "gdt755_spoken_candidate_render_de": f"Arbeitshypothese: {prior['working_candidate_de']}",
            "working_confidence": prior["working_confidence"],
            "evidence": evidence,
            "selection_reason": prior["selection_reason"],
            "counterevidence": counter,
            "alternate_candidate_1": prior["alternate_candidate_1"],
            "alternate_candidate_2": prior["alternate_candidate_2"],
            "candidate_register_family": candidate["candidate_register_family"],
            "register_migration_from_gdt754": int(not int(candidate["register_family_match"])),
            "candidate_layer_scope": "EXACT_COMPLETE_SURFACE_ON_ENUMERATED_READER_EXACT_POSITIONS",
            "historical_graphic_match_claimed": 0,
            "literal_identity": "OPEN",
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    return output


def candidate_role_fit(candidate: dict[str, str], axes: set[str]) -> bool:
    required_all = values(candidate["required_all_axes"])
    required_any = values(candidate["required_any_axes"])
    return required_all <= axes and (not required_any or bool(required_any & axes))


def build_slot_audit(
    deck: list[dict[str, str]],
    bank: dict[str, dict[str, str]],
    priors: list[dict[str, str]],
) -> list[dict[str, object]]:
    axes_by_surface = {
        row["surface"]: values(row["selected_role_axes"]) for row in deck
    }
    primary_by_candidate: defaultdict[str, list[str]] = defaultdict(list)
    for prior in priors:
        primary_by_candidate[prior["primary_candidate_id"]].append(prior["surface"])
    output: list[dict[str, object]] = []
    for concept, candidate_id in CONTENT_AUDIT:
        candidate = bank[candidate_id]
        structural = sorted(
            surface for surface, axes in axes_by_surface.items()
            if candidate_role_fit(candidate, axes)
        )
        content_axes = values(candidate["content_slot_axis"])
        literal = sorted(
            surface for surface in structural
            if not content_axes or bool(content_axes & axes_by_surface[surface])
        )
        used = sorted(primary_by_candidate.get(candidate_id, []))
        if content_axes and structural and not literal:
            disposition = "STRUCTURAL_SLOT_EXISTS_LITERAL_IDENTITY_UNSUPPORTED"
        elif structural:
            disposition = "ROLE_SLOT_EXISTS_OPERATION_OR_FIELD_STILL_AMBIGUOUS"
        else:
            disposition = "NO_TOP24_ROLE_SLOT"
        if used and content_axes and not literal:
            disposition = "FORCED_PRIMARY_LITERAL_CANDIDATE_WITHOUT_SPECIFIC_AXIS"
        output.append({
            "concept_de": concept,
            "candidate_id": candidate_id,
            "historical_expression": candidate["normalized_expression"],
            "candidate_kind": candidate["candidate_kind"],
            "required_all_axes": candidate["required_all_axes"],
            "required_any_axes": candidate["required_any_axes"],
            "specific_content_axis": candidate["content_slot_axis"],
            "structurally_compatible_top24_surfaces": "|".join(structural) or "NONE",
            "structurally_compatible_count": len(structural),
            "literal_axis_supported_top24_surfaces": "|".join(literal) or "NONE",
            "literal_axis_supported_count": len(literal),
            "used_as_primary_top24_surfaces": "|".join(used) or "NONE",
            "disposition": disposition,
            "historical_source_ids": candidate["source_ids"],
            "practical_reading": (
                "A process/formula slot exists, but exact operation remains a candidate."
                if structural and not content_axes else
                "A broad carrier slot exists, but this concrete noun lacks its own axis."
                if structural else
                "Search other recurrent learned wholes; the top-24 deck lacks the required role."
            ),
            "historical_graphic_match_claimed": 0,
            "confirmed_lexeme": 0,
        })
    return output


def hybrid_line(
    context: object,
    locus: str,
    gloss_by_surface: dict[str, str],
) -> str:
    rendered: list[str] = []
    for token in context.by_line[locus]:
        surface = token["eva"]
        if (
            surface in gloss_by_surface
            and context.exact[(locus, int(token["token_index"]))]
        ):
            rendered.append(f"[{gloss_by_surface[surface]}]")
        else:
            rendered.append(f"<{surface}>")
    return " ".join(rendered)


def build_candidate_renderer(
    occurrences: list[dict[str, object]],
    gloss_updates: list[dict[str, object]],
    context: object,
) -> list[dict[str, object]]:
    update_by_surface = {str(row["surface"]): row for row in gloss_updates}
    gloss = {
        surface: str(row["gdt755_working_candidate_de"])
        for surface, row in update_by_surface.items()
    }
    output: list[dict[str, object]] = []
    for row in occurrences:
        update = update_by_surface[str(row["surface"])]
        output.append({
            "gdt755_occurrence_id": row["gdt755_occurrence_id"],
            "surface": row["surface"],
            "page": row["page"],
            "locus": row["locus"],
            "token_ordinal": row["token_ordinal"],
            "line_position": row["line_position"],
            "field_channel": row["field_channel"],
            "boundary_complete": row["boundary_complete"],
            "selected_role_axes": row["selected_role_axes_not_used_as_self_anchor"],
            "historical_expression": update["gdt755_primary_historical_expression"],
            "working_candidate_de": update["gdt755_working_candidate_de"],
            "working_confidence": update["working_confidence"],
            "spoken_candidate_render_de": update["gdt755_spoken_candidate_render_de"],
            "written_line_eva": row["written_line_eva"],
            "candidate_hybrid_line_de": hybrid_line(
                context, str(row["locus"]), gloss
            ),
            "unmapped_tokens_preserved_as_eva": 1,
            "candidate_layer_not_plaintext": 1,
            "literal_identity": "OPEN",
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    return output


def write_reader(
    path: Path,
    sources: list[dict[str, str]],
    bank_rows: list[dict[str, str]],
    glosses: list[dict[str, object]],
    census: list[dict[str, object]],
    slot_audit: list[dict[str, object]],
    renderer: list[dict[str, object]],
    position_comparator: list[dict[str, object]],
) -> None:
    census_by_surface = {str(row["surface"]): row for row in census}
    lines = [
        "# GDT755 historical-register candidate reader", "",
        "This is the first concrete complete-form candidate layer after the GDT754 provenance correction. It gives every one of the 24 fixed wholes a concise default and two rivals. Brackets in the sample lines are candidate readings; angle brackets are deliberately unmapped EVA tokens.",
        "", "## Twenty-four concrete working candidates", "",
        "| rank | whole | candidate | historical expression | confidence | exact / complete fields | first / last | complete channels |",
        "|---:|---|---|---|---|---:|---:|---|",
    ]
    for row in glosses:
        stats = census_by_surface[str(row["surface"])]
        lines.append(
            f"| {row['bridge_rank']} | `{row['surface']}` | {row['gdt755_working_candidate_de']} | "
            f"`{row['gdt755_primary_historical_expression']}` | `{row['working_confidence']}` | "
            f"{stats['reader_exact_occurrences']} / {stats['complete_independent_fields']} | "
            f"{stats['line_first_occurrences']} / {stats['line_last_occurrences']} | "
            f"{stats['complete_channel_counts']} |"
        )
    ychor = census_by_surface["ychor"]
    ychor_position = next(
        row for row in position_comparator if row["surface"] == "ychor"
    )
    lines.extend([
        "", "## Most useful changes", "",
        f"- `ychor` is no longer best treated as an abstract part/pass label. It is line-initial at {ychor['line_first_occurrences']}/{ychor['reader_exact_occurrences']} exact occurrences, ranks {ychor_position['line_initial_rate_rank']} of {len(position_comparator)} recurrent forms by initial rate, is the only 100% line-initial form in that comparison, and has three prescriptive-recipe fields among eight complete external fields. It is paragraph-initial at 0/13, so the current first candidate is the line-level recipe macro `Recipe` = nimm rather than a section heading.",
        "- `lkaiin`, `okeol`, `qokeol`, `chky`, and `otaly` now have compact Galenic quality-degree candidates rather than drug-wood or generic work prose.",
        "- `okam` and `chdam` are treated as dose/measure candidates because their amount/value roles combine with strongly final placement; `chdam` is final in all four observed exact occurrences.",
        "- `cthody=Salbe` is intentionally bold and C0. Its preparation-noun slot is plausible, but the specific ointment identity has no independent OINTMENT axis.",
        "", "## Concrete vocabulary slot audit", "",
        "| concept | historical expression | structural top-24 slots | literal-axis slots | disposition |",
        "|---|---|---:|---:|---|",
    ])
    for row in slot_audit:
        lines.append(
            f"| {row['concept_de']} | `{row['historical_expression']}` | "
            f"{row['structurally_compatible_count']} | {row['literal_axis_supported_count']} | "
            f"`{row['disposition']}` |"
        )
    line_groups: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for row in renderer:
        line_groups[str(row["locus"])].append(row)
    ranked_lines = sorted(
        line_groups.items(),
        key=lambda item: (
            -len(item[1]),
            -sum(int(row["boundary_complete"]) for row in item[1]),
            item[0],
        ),
    )[:16]
    lines.extend([
        "", "## Hybrid line samples", "",
        "These lines are not presented as translations. They expose exactly how much concrete candidate text the 24-form layer contributes without filling the rest with generic prose.", "",
    ])
    for locus, rows in ranked_lines:
        exemplar = rows[0]
        lines.extend([
            f"### {locus}", "",
            f"EVA: `{exemplar['written_line_eva']}`", "",
            f"Candidate layer: {exemplar['candidate_hybrid_line_de']}", "",
        ])
    lines.extend([
        "## Historical control", "",
        f"The expression bank contains {len(bank_rows)} expression classes from {len(sources)} registered sources. The strongest architecture result is not that all content was abbreviated alike: the aligned later plague-recipes show especially stable formulaic abbreviations for drachm, ana, Recipe, semis, and ounce, while ingredient abbreviations vary more. That is why line-initial `ychor` and final amount candidates receive more leverage than arbitrary plant-name guesses.", "",
        "No spelling resemblance between EVA and Latin is scored. No character or substring inherits a Latin value. All 24 readings remain replaceable complete-form hypotheses.",
    ])
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    deck = read_tsv(ROOT / G754_TOP_REL)
    inventory = read_tsv(ROOT / G754_INVENTORY_REL)
    priors = read_tsv(SRC / "TARGET_CANDIDATE_PRIORS.tsv")
    bank_rows = read_tsv(SRC / "HISTORICAL_EXPRESSION_BANK.tsv")
    source_rows = read_tsv(SRC / "HISTORICAL_SOURCE_REGISTRY.tsv")
    bank = {row["candidate_id"]: row for row in bank_rows}
    sources = {row["source_id"]: row for row in source_rows}
    suspect_surfaces = {row["surface"] for row in inventory}

    if len(deck) != 24 or len({row["surface"] for row in deck}) != 24:
        raise AssertionError("fixed top-24 deck changed")
    if len(inventory) != 172 or len(suspect_surfaces) != 172:
        raise AssertionError("fixed 172-form suspect inventory changed")
    if {row["surface"] for row in priors} != {row["surface"] for row in deck}:
        raise AssertionError("candidate prior deck does not cover top 24 exactly")
    if len(priors) != 24 or len(bank_rows) != 52 or len(source_rows) != 13:
        raise AssertionError("historical source or candidate inventory changed")
    for candidate in bank_rows:
        missing_sources = values(candidate["source_ids"]) - set(sources)
        if missing_sources:
            raise AssertionError(
                f"{candidate['candidate_id']} missing sources {sorted(missing_sources)}"
            )
    for prior in priors:
        for field in (
            "primary_candidate_id", "alternate_candidate_1", "alternate_candidate_2"
        ):
            if prior[field] not in bank:
                raise AssertionError(f"{prior['surface']} missing candidate {prior[field]}")

    context, line_meta, line_guard = g753.g752.g751.load_context()
    rules = g753.g752.g744.load_channel_rules()
    occurrences = build_occurrences(deck, suspect_surfaces, context, line_meta, rules)
    census = build_census(deck, occurrences)
    position_comparator = build_position_comparator(
        context, line_meta, {row["surface"] for row in deck}, suspect_surfaces
    )
    rankings = build_rankings(deck, priors, bank, sources, occurrences)
    glosses = build_gloss_updates(deck, priors, rankings, census)
    slot_audit = build_slot_audit(deck, bank, priors)
    renderer = build_candidate_renderer(occurrences, glosses, context)

    primary_rankings = [row for row in rankings if int(row["selected_primary"])]
    if len(occurrences) != 448 or sum(int(row["boundary_complete"]) for row in occurrences) != 198:
        raise AssertionError("fixed 448-occurrence or 198-field census changed")
    if len(rankings) != 72 or len(primary_rankings) != 24:
        raise AssertionError("three-candidate ranking deck changed")
    if any(not int(row["hard_role_fit"]) for row in primary_rankings):
        raise AssertionError("a primary candidate lacks its required whole-role fit")
    ychor_position = next(
        row for row in position_comparator if row["surface"] == "ychor"
    )
    if (
        len(position_comparator) != 373
        or int(ychor_position["line_initial_rate_rank"]) != 1
        or int(ychor_position["line_first_occurrences"]) != 13
        or sum(row["line_first_rate"] == "1.000000" for row in position_comparator) != 1
    ):
        raise AssertionError("fixed recurrent-form position comparator changed")

    write_tsv(output_dir / OUTPUT_NAMES[0], occurrences, list(occurrences[0]))
    write_tsv(output_dir / OUTPUT_NAMES[1], census, list(census[0]))
    write_tsv(
        output_dir / OUTPUT_NAMES[2], position_comparator,
        list(position_comparator[0]),
    )
    write_tsv(output_dir / OUTPUT_NAMES[3], rankings, list(rankings[0]))
    write_tsv(output_dir / OUTPUT_NAMES[4], glosses, list(glosses[0]))
    write_tsv(output_dir / OUTPUT_NAMES[5], slot_audit, list(slot_audit[0]))
    write_tsv(output_dir / OUTPUT_NAMES[6], renderer, list(renderer[0]))
    write_reader(
        output_dir / OUTPUT_NAMES[7], source_rows, bank_rows, glosses, census,
        slot_audit, renderer, position_comparator,
    )

    confidence_counts = Counter(row["working_confidence"] for row in glosses)
    register_migrations = [
        str(row["surface"]) for row in glosses
        if int(row["register_migration_from_gdt754"])
    ]
    content_rows = [row for row in slot_audit if values(str(row["specific_content_axis"]))]
    literal_supported_concepts = [
        str(row["concept_de"]) for row in content_rows
        if int(row["literal_axis_supported_count"])
    ]
    status = (
        "PARTIAL__24_CONCRETE_COMPLETE_FORM_CANDIDATES__"
        "448_EXACT_OCCURRENCES__198_COMPLETE_INDEPENDENT_FIELDS__"
        "52_HISTORICAL_EXPRESSIONS__13_SOURCES__"
        "2_C2_15_C1_7_C0__YCHOR_UNIQUE_13_OF_13_INITIAL_RANK1_OF373__"
        "ZERO_CONFIRMED_LEXEMES__NO_NEW_PAGE"
    )
    ychor = next(row for row in census if row["surface"] == "ychor")
    result = {
        "schema": "GDT755_RESULT_V1",
        "status": status,
        "scope": {
            "top_complete_forms": len(deck),
            "reader_exact_occurrences": len(occurrences),
            "reader_exact_pages": len({str(row["page"]) for row in occurrences}),
            "complete_independent_fields": sum(int(row["boundary_complete"]) for row in occurrences),
            "historical_expression_classes": len(bank_rows),
            "historical_sources": len(source_rows),
            "candidate_rows": len(rankings),
            "working_gloss_updates": len(glosses),
            "candidate_renderer_positions": len(renderer),
            "concrete_slot_audit_concepts": len(slot_audit),
            "position_comparator_forms_min10": len(position_comparator),
        },
        "candidate_confidence_counts": dict(sorted(confidence_counts.items())),
        "register_migrations_from_gdt754": register_migrations,
        "strongest_new_lead": {
            "surface": "ychor", "candidate": "Recipe / nimm",
            "line_first_occurrences": int(ychor["line_first_occurrences"]),
            "reader_exact_occurrences": int(ychor["reader_exact_occurrences"]),
            "complete_prescriptive_recipe_fields": sum(
                int(row["surface"] == "ychor" and row["boundary_complete"] and row["field_channel"] == "PRESCRIPTIVE_RECIPE")
                for row in occurrences
            ),
            "line_initial_rate_rank_among_forms_min10": int(ychor_position["line_initial_rate_rank"]),
            "forms_min10_with_100_percent_line_initial": sum(
                row["line_first_rate"] == "1.000000" for row in position_comparator
            ),
            "paragraph_first_occurrences": int(ychor_position["paragraph_first_occurrences"]),
            "status": "STRONG_EXPLORATORY_COMPLETE_WHOLE_CANDIDATE",
        },
        "content_slot_result": {
            "specific_content_concepts_audited": len(content_rows),
            "specific_content_concepts_with_literal_axis_in_top24": literal_supported_concepts,
            "interpretation": "Concrete substance patient vessel and person nouns mostly require other learned-whole slots; process and formula roles are available in this top-24 deck.",
        },
        "independence_controls": {
            "gdt754_productive_compound_surfaces_excluded_as_field_anchors": len(suspect_surfaces),
            "target_self_meanings_used_as_field_anchors": 0,
            "eva_spelling_or_substring_matches_scored": 0,
            "old_literal_source_prose_used_to_select_historical_word": 0,
        },
        "guard": line_guard,
        "claim_boundary": {
            "concrete_working_defaults": 24, "confirmed_lexemes": 0,
            "confirmed_historical_graphic_matches": 0,
            "literal_content_identifications": 0, "plaintext_clauses": 0,
            "component_export_credit": 0, "new_pages": 0,
            "f84_accessed": False, "f84r_accessed": False,
        },
    }
    (output_dir / OUTPUT_NAMES[8]).write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_ARTIFACTS)
    args = parser.parse_args()
    result = build(args.output_dir)
    print(json.dumps({
        "status": result["status"], "scope": result["scope"],
        "confidence": result["candidate_confidence_counts"],
        "strongest_lead": result["strongest_new_lead"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
