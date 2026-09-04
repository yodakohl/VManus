#!/usr/bin/env python3
"""Build GDT804's independent-field audit and bracket working reader."""

from __future__ import annotations

import argparse
import csv
import hashlib
import heapq
import importlib.util
import io
import json
import math
import random
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Sequence


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt804_bracket_middle_independent_field_bridge"
SRC = EXP / "src"
ART = EXP / "artifacts"

G800 = ROOT / "experiments/yolo/gdt800_terminal_b2_b3_line_final_bridge/artifacts"
G803 = ROOT / "experiments/yolo/gdt803_recurrent_context_rarity_discriminator"
G739 = ROOT / "experiments/yolo/gdt739_twelve_whole_local_dimension_dispatch/artifacts"
G743 = ROOT / "experiments/yolo/gdt743_r2_run_intersection_adjudication/artifacts"
G744 = ROOT / "experiments/yolo/gdt744_historical_microfield_channel_bridge"
G745 = ROOT / "experiments/yolo/gdt745_exact_open_content_role_expansion/artifacts"
G760 = ROOT / "experiments/yolo/gdt760_quantity_bilateral_content_attachment/artifacts"
G734 = ROOT / "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts"
G759 = ROOT / "experiments/yolo/gdt759_quantity_part_state_construction_atlas/artifacts"
G762 = ROOT / "experiments/yolo/gdt762_moist_medium_candidate_discrimination/artifacts"
G753 = ROOT / "experiments/yolo/gdt753_qokeol_okeol_whole_role_census/artifacts"
G764 = ROOT / "experiments/yolo/gdt764_bounded_value_field_dispatch/artifacts"
G793 = ROOT / "experiments/yolo/gdt793_okal_whole_record_candidate_discriminator/artifacts"

STEM_SUMMARY = G800 / "GDT800_155_MATCHED_STEM_SUMMARY.tsv"
OCCURRENCES = G800 / "GDT800_4137_MATCHED_TERMINAL_OCCURRENCES.tsv"
BRACKETS = G803 / "artifacts/GDT803_12_BIDIRECTIONAL_BRACKETS.tsv"
CONTEXT_PRIORS = G803 / "src/CONTEXT_ROLE_PRIORS.tsv"
WINDOWS = G739 / "WINDOW_202_TOKEN_AUDIT.tsv"
PATCHES = G743 / "TARGET_202_RENDERER_PATCH_V5.tsv"
G744_RUN = G744 / "src/run.py"
G744_RULES = G744 / "src/FIELD_CHANNEL_RULES.tsv"
G744_SUPPLEMENTS = G744 / "src/WHOLE_HISTORICAL_ROLE_SUPPLEMENTS.tsv"
G744_OPEN_SLOTS = G744 / "artifacts/UNRESOLVED_CONTENT_SLOT_CANDIDATES.tsv"
G745_OPEN_ROLES = G745 / "CONTENT_41_ROLE_CENSUS.tsv"
G760_EXPRESSIONS = G760 / "QUANTITY_281_EXPRESSION_ATLAS.tsv"
LINES = G734 / "V99R7_4128_INTEGRATED_LINE_READER.tsv"
G759_PART_STATES = G759 / "PART_STATE_23_EXACT_PAIR_ATLAS.tsv"
G762_CARRIERS = G762 / "THREE_CANDIDATE_WORKING_REVISION.tsv"
G753_WHOLE_ROLES = G753 / "SURFACE_22_ROLE_CENSUS.tsv"
G764_HISTORICAL = G764 / "HISTORICAL_REGISTER_TEMPLATE_MAP.tsv"
G793_ADJUDICATION = G793 / "GDT793_CANDIDATE_ADJUDICATION.tsv"
G631 = ROOT / "experiments/yolo/gdt631_prefixed_cth_quality_parts"
G636_DICT = ROOT / "experiments/yolo/gdt636_residual_four_head_semantics/artifacts/WORKING_DICTIONARY_V13.tsv"
PAGE_ALLOWLIST = G631 / "artifacts/PAGE_ALLOWLIST.tsv"
TOKENS_RAW = ROOT / "transcription/voynich_zl3b_tokens.tsv"
CROSS_RAW = ROOT / "transcription/voynich_cross_transcription_lines.tsv"
G634_RUN = ROOT / "experiments/yolo/gdt634_known_core_terminal_semantics/src/run.py"
EDGE_VALIDATOR = ROOT / "tools/relation_edge_intake.py"
GUARDED_QUERY_TOOL = ROOT / "tools/guarded_tsv_query.py"
EXPERIMENT_TOOL = ROOT / "tools/vmanus_experiment.py"
VMANUS_EXP = ROOT / "vmanus-exp"
MIDDLE_PRIORS = SRC / "MIDDLE_ROLE_PRIORS.tsv"
BRACKET_READINGS = SRC / "BRACKET_WORKING_READINGS.tsv"

OUTPUT_NAMES = (
    "SOURCE_LOCK.tsv",
    "GDT804_72_COMMON_MASK_FIELD_ATLAS.tsv",
    "GDT804_107_COMMON_MASK_XL_EXPOSURES.tsv",
    "GDT804_POSITIONAL_AMOUNT_XL_SLOTS.tsv",
    "GDT804_30_TARGET_UNION_CELLS.tsv",
    "GDT804_11_MIDDLE_CENSUS.tsv",
    "GDT804_NEAREST_CONTROL_POOLS.tsv",
    "GDT804_5000_AGGREGATE_MATCHED_NULL.tsv",
    "GDT804_NULL_SUMMARY.tsv",
    "GDT804_GUARDED_READER_QUERY_STATS.tsv",
    "GDT804_41_QUALITY_VALUE_SPANS.tsv",
    "GDT804_QUALITY_VALUE_SUMMARY.tsv",
    "GDT804_11_MIDDLE_RIGHT_VALUE_PROFILE.tsv",
    "GDT804_CHEOL_K12_RIGHT_VALUE_CONTROL.tsv",
    "GDT804_GDT388_QUALITY_VALUE_EDGE_PACKET.tsv",
    "GDT804_GDT388_EDGE_INTAKE.json",
    "GDT804_12_BRACKET_WORKING_READER.tsv",
    "GDT804_MIDDLE_ROLE_ADJUDICATION.tsv",
    "GDT804_STRUCTURAL_CARD.tsv",
    "RESULT.json",
)

STATUS = (
    "PARTIAL__11_BRACKET_MIDDLES__0_OPEN_SLOT_INTERSECTION__"
    "72_COMMON_MASK_FIELDS__18_OF_45_FIELD_CELLS__15_POSITIONAL_AMOUNT_NEIGHBOURS__"
    "0_GDT760_CLEAN_CONTENT_CONTACTS__"
    "FIELD_ASSOCIATION_MATCH_SENSITIVE__CONTENT_SLOT_UNRESOLVED__"
    "41_ZL3B_QUALITY_VALUE_SPANS__33_CROSS_READER_SEQUENCES__"
    "CHEOL_SPECIFICITY_UNRESOLVED__ZERO_LEXEMES"
)

PRIMARY_SEED = 804804
PRIMARY_DRAWS = 200_000
PRIMARY_KEEP = 5_000
PRIMARY_K = 12
SENSITIVITY_SEED = 804
SENSITIVITY_DRAWS = 100_000
SENSITIVITY_K = 10
ABLATION_SEED = 805

EDGE_FIELDS = (
    "edge_id", "batch_id", "page", "physical_folio", "diagram_unit_id",
    "pivot_visual_id", "pivot_locus", "target_visual_id", "target_locus",
    "relation_type", "direction_basis", "ownership_basis",
    "geometry_only_selection", "source_manifest_id", "page_crop_sha256",
    "pivot_crop_sha256", "target_crop_sha256", "source_aware_localizer",
    "relation_reviewer", "relation_confidence", "ambiguity_state",
    "formal_access_state", "fold_assignment", "eligibility_status",
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: Sequence[dict[str, Any]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def guarded_query(
    path: Path, pages: set[str], columns: Sequence[str], label: str,
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    command = [str(VMANUS_EXP), "query-tsv", relative(path), "--selector", "page"]
    for page in sorted(pages):
        command.extend(("--allow", page))
    command.extend((
        "--columns", ",".join(columns),
        "--forbid-prefix", "f84", "--forbid-prefix", "f84r",
    ))
    completed = subprocess.run(
        command, cwd=ROOT, check=False, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if completed.returncode:
        raise RuntimeError(completed.stderr or f"guarded {label} query failed")
    stats_lines = [line for line in completed.stderr.splitlines() if line.startswith("GUARD_STATS ")]
    if len(stats_lines) != 1:
        raise RuntimeError(f"guard statistics missing for {label}")
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    assert_unsealed(rows)
    stats = json.loads(stats_lines[0][12:])
    return rows, {
        "query_id": label,
        "source_path": relative(path),
        "selector": "page",
        "allowed_values": len(pages),
        "output_columns": ",".join(columns),
        "forbidden_prefixes": "f84|f84r",
        "selected_rows": stats["selected"],
        "skipped_forbidden_rows": stats["skipped_forbidden"],
        "skipped_not_allowed_rows": stats["skipped_not_allowed"],
    }


def load_reader_context() -> tuple[
    list[dict[str, str]], dict[tuple[str, int], int], dict[str, dict[str, str]],
    list[dict[str, Any]],
]:
    pages = {row["page"] for row in read_tsv(PAGE_ALLOWLIST)}
    if len(pages) != 179 or any(page.startswith("f84") for page in pages):
        raise AssertionError("inherited 179-page allow-list drift")
    token_columns = ("page", "locus", "token_index", "eva", "section", "language", "hand")
    cross_columns = (
        "page", "locus", "all_three_present", "all_present_exact",
        "zl3b_clean", "it2a_clean", "rf1b_clean",
    )
    tokens, token_stats = guarded_query(TOKENS_RAW, pages, token_columns, "ZL3B_TOKENS")
    cross, cross_stats = guarded_query(CROSS_RAW, pages, cross_columns, "CROSS_READER_LINES")
    if len(tokens) != 32339 or len(cross) != 4137:
        raise AssertionError("guarded reader-context capacity drift")
    cross_by_locus = {row["locus"]: row for row in cross}
    if len(cross_by_locus) != len(cross):
        raise AssertionError("cross-reader loci are not unique")
    ordinals: Counter[tuple[str, str]] = Counter()
    exact: dict[tuple[str, int], int] = {}
    for row in sorted(tokens, key=lambda item: (item["locus"], int(item["token_index"]))):
        locus, surface = row["locus"], row["eva"]
        ordinals[locus, surface] += 1
        reader_line = cross_by_locus[locus]
        caps = [
            reader_line[field].split().count(surface)
            for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")
        ]
        exact[(locus, int(row["token_index"]))] = int(ordinals[locus, surface] <= min(caps))
    return tokens, exact, cross_by_locus, [token_stats, cross_stats]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def f12(value: float) -> str:
    return f"{value:.12g}"


def load_g744_module() -> Any:
    spec = importlib.util.spec_from_file_location("gdt744_locked_builder", G744_RUN)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import locked GDT744 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def assert_unsealed(rows: Iterable[dict[str, Any]]) -> None:
    for row in rows:
        for field in ("page", "source_selector", "locus", "physical_folio"):
            value = str(row.get(field, ""))
            if value.startswith("f84"):
                raise AssertionError(f"sealed selector reached GDT804: {field}={value}")


def source_lock() -> list[dict[str, str]]:
    inputs = (
        STEM_SUMMARY, OCCURRENCES, BRACKETS, CONTEXT_PRIORS, WINDOWS, PATCHES,
        G744_RUN, G744_RULES, G744_SUPPLEMENTS, G744_OPEN_SLOTS, G745_OPEN_ROLES,
        G760_EXPRESSIONS, LINES, G759_PART_STATES, G762_CARRIERS,
        G753_WHOLE_ROLES, G764_HISTORICAL, G793_ADJUDICATION,
        MIDDLE_PRIORS, BRACKET_READINGS, G636_DICT, PAGE_ALLOWLIST, TOKENS_RAW, CROSS_RAW,
        G634_RUN, EDGE_VALIDATOR, GUARDED_QUERY_TOOL, EXPERIMENT_TOOL, VMANUS_EXP,
    )
    purposes = {
        STEM_SUMMARY: "paired-Xl universe and form exposure",
        OCCURRENCES: "surface style and line-position covariates",
        BRACKETS: "twelve GDT803 discovery constructions",
        CONTEXT_PRIORS: "pre-GDT804 broad outer-field roles",
        WINDOWS: "GDT739 token windows for the common semantic mask",
        PATCHES: "GDT743 fixed 202 target positions",
        G744_RUN: "locked clipping, anchor and recurrent-channel algorithm",
        G744_RULES: "historical field-channel rules",
        G744_SUPPLEMENTS: "two locked whole-role supplements",
        G744_OPEN_SLOTS: "published GDT744 open-slot identity check",
        G745_OPEN_ROLES: "published GDT745 open-centre identity check",
        G760_EXPRESSIONS: "fixed position-conditioned amount-neighbour map",
        LINES: "cached exact ZL3b line order for quality-value spans",
        G759_PART_STATES: "pre-existing chor/chol construction evidence",
        G762_CARRIERS: "pre-existing ol carrier correction",
        G753_WHOLE_ROLES: "pre-existing qokeol whole-role correction",
        G764_HISTORICAL: "attested historical register architecture E010",
        G793_ADJUDICATION: "pre-existing exact okal system-entry rival",
        MIDDLE_PRIORS: "manual replaceable middle-whole role deck",
        BRACKET_READINGS: "manual safe and aggressive bracket renderer deck",
        G636_DICT: "source of the inherited qokain hot-degree-II aggressive rival",
        PAGE_ALLOWLIST: "inherited 179-page selector allow-list",
        TOKENS_RAW: "guarded ZL3b token source for reader stability",
        CROSS_RAW: "guarded alternate-reader line source for sequence stability",
        G634_RUN: "published token-stability map definition",
        EDGE_VALIDATOR: "GDT388 relation-packet intake validator",
        GUARDED_QUERY_TOOL: "selector-before-materialization TSV query implementation",
        EXPERIMENT_TOOL: "sealed-selector guard implementation",
        VMANUS_EXP: "guarded edge-packet command dispatcher",
    }
    return [
        {"path": relative(path), "sha256": sha256(path), "purpose": purposes[path]}
        for path in inputs
    ]


def mask_and_build_fields(
    universe: set[str], g744: Any,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    windows = read_tsv(WINDOWS)
    for row in windows:
        if row["neighbor_surface"] in universe:
            row.update({
                "neighbor_unknown_v99r7": "1",
                "neighbor_confidence_level": "NA",
                "axis_tags": "NONE",
                "eligible_local_anchor": "0",
            })
    patches = read_tsv(PATCHES)
    fields = g744.build_initial_fields(
        patches, windows, g744.load_channel_rules(), g744.load_whole_supplements()
    )
    fields, _, _, _ = g744.decorate_fields(fields, g744.load_channel_rules())
    return fields, windows


def flatten_licensed_fields(fields: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for row in fields:
        if not int(row["template_backed_field_reading"]):
            continue
        output.append({
            "gdt744_field_id": row["gdt744_field_id"],
            "page": row["page"],
            "locus": row["locus"],
            "target_ordinal": row["target_ordinal"],
            "target_surface": row["surface"],
            "field_channel_after_common_mask": row["raw_field_channel"],
            "field_confidence_tier": row["field_confidence_tier"],
            "boundary_complete": row["boundary_complete"],
            "foreign_anchor_count": row["strong_anchor_count"],
            "foreign_anchor_surfaces": row["strong_anchor_surfaces"],
            "foreign_anchor_tags": row["strong_anchor_tags"],
            "foreign_anchor_signature": row["strong_anchor_signature"],
            "common_mask": "ALL_155_PAIRED_XL_SURFACES_REMOVED_AS_SEMANTIC_ANCHORS",
            "literal_identity_credit": 0,
            "component_export_credit": 0,
        })
    return output


def field_exposures(
    fields: list[dict[str, Any]], universe: set[str], target: set[str], g744: Any,
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str, str, str]] = set()
    for field in fields:
        for neighbor in field["_span"]:
            surface = neighbor["neighbor_surface"]
            if surface not in universe or not g744.unresolved_candidate(neighbor):
                continue
            key = (
                str(field["gdt744_field_id"]), str(field["page"]),
                str(field["locus"]), str(neighbor["neighbor_ordinal"]), surface,
            )
            if key in seen:
                raise AssertionError("duplicate common-mask field exposure")
            seen.add(key)
            output.append({
                "field_exposure_id": f"G804-FX{len(output) + 1:04d}",
                "surface": surface,
                "is_gdt803_middle": int(surface in target),
                "page": field["page"],
                "locus": field["locus"],
                "token_ordinal": neighbor["neighbor_ordinal"],
                "side": neighbor["side"],
                "distance": neighbor["distance"],
                "host_target_surface": field["surface"],
                "host_gdt744_field_id": field["gdt744_field_id"],
                "field_channel_after_common_mask": field["raw_field_channel"],
                "independently_licensed_field": int(field["template_backed_field_reading"]),
                "field_confidence_tier": field["field_confidence_tier"],
                "foreign_anchor_surfaces": field["strong_anchor_surfaces"],
                "foreign_anchor_tags": field["strong_anchor_tags"],
                "cell_key": f"{field['page']}|{field['locus']}|{neighbor['neighbor_ordinal']}|{surface}",
                "semantic_role_credit": "FIELD_NEIGHBOUR_ONLY",
                "literal_identity_credit": 0,
                "component_export_credit": 0,
            })
    output.sort(key=lambda row: (row["page"], row["locus"], int(row["token_ordinal"]), row["surface"]))
    for index, row in enumerate(output, start=1):
        row["field_exposure_id"] = f"G804-FX{index:04d}"
    return output


def positional_amount_slots(
    universe: set[str], target: set[str], discovery_cells: set[str],
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for expression in read_tsv(G760_EXPRESSIONS):
        position = expression["expression_line_position"]
        side = "right" if position == "FIRST" else "left" if position == "MIDDLE" else ""
        if not side:
            continue
        surface = expression[f"{side}_surface"]
        if (
            surface not in universe
            or expression[f"{side}_reader_exact"] != "1"
            or expression[f"{side}_source_composed_quarantined"] != "0"
            or surface == "LINE_EDGE"
        ):
            continue
        ordinal = expression[f"{side}_ordinal"]
        cell_key = f"{expression['page']}|{expression['locus']}|{ordinal}|{surface}"
        side_code = "R" if side == "right" else "L"
        clean_sides = set(expression["content_attachment_sides"].split("|"))
        selected_clean_contact = int(side_code in clean_sides)
        axis_class = expression[f"{side}_axis_class"]
        output.append({
            "amount_slot_id": f"G804-AS{len(output) + 1:04d}",
            "expression_id": expression["expression_id"],
            "surface": surface,
            "is_gdt803_middle": int(surface in target),
            "page": expression["page"],
            "physical_folio": expression["physical_folio"],
            "locus": expression["locus"],
            "token_ordinal": ordinal,
            "expression_line_position": position,
            "selected_side": side.upper(),
            "amount_expression_eva": expression["source_expression_eva"],
            "amount_candidate_de": expression["amount_candidate_de"],
            "slot_axis_class": axis_class,
            "slot_axes_before_gdt804": expression[f"{side}_axes"],
            "source_content_attachment_sides": expression["content_attachment_sides"],
            "source_clean_content_attachment_count": expression["clean_content_attachment_count"],
            "selected_side_is_clean_content_contact": selected_clean_contact,
            "open_positional_candidate": int(axis_class == "OPEN"),
            "candidate_status": (
                "GDT760_LICENSED_CONTENT_CONTACT" if selected_clean_contact
                else "POSITION_HEURISTIC_OPEN_CANDIDATE" if axis_class == "OPEN"
                else "POSITION_HEURISTIC_NONOPEN_CANDIDATE"
            ),
            "discovery_cell_excluded": int(cell_key in discovery_cells),
            "cell_key": cell_key,
            "role_scope": "POSITION_CONDITIONED_AMOUNT_NEIGHBOUR_CANDIDATE_ONLY",
            "literal_identity_credit": 0,
            "component_export_credit": 0,
        })
    return sorted(output, key=lambda row: (row["page"], row["locus"], int(row["token_ordinal"]), row["surface"]))


def maps_by_surface(
    field_rows: list[dict[str, Any]], amount_rows: list[dict[str, Any]], universe: set[str],
) -> tuple[dict[str, set[str]], dict[str, set[str]], dict[str, set[str]], dict[str, set[str]], dict[str, set[str]]]:
    exposure = {surface: set() for surface in universe}
    field = {surface: set() for surface in universe}
    amount = {surface: set() for surface in universe}
    amount_open = {surface: set() for surface in universe}
    amount_clean = {surface: set() for surface in universe}
    for row in field_rows:
        surface = str(row["surface"])
        exposure[surface].add(str(row["cell_key"]))
        if int(row["independently_licensed_field"]):
            field[surface].add(str(row["cell_key"]))
    for row in amount_rows:
        if int(row["discovery_cell_excluded"]):
            continue
        surface = str(row["surface"])
        amount[surface].add(str(row["cell_key"]))
        if int(row["open_positional_candidate"]):
            amount_open[surface].add(str(row["cell_key"]))
        if int(row["selected_side_is_clean_content_contact"]):
            amount_clean[surface].add(str(row["cell_key"]))
    return exposure, field, amount, amount_open, amount_clean


def cell_pages(cells: Iterable[str]) -> set[str]:
    return {cell.split("|", 1)[0] for cell in cells}


def score_set(
    surfaces: Sequence[str], summary: dict[str, dict[str, str]],
    exposure: dict[str, set[str]], field: dict[str, set[str]],
    amount: dict[str, set[str]], amount_open: dict[str, set[str]],
    amount_clean: dict[str, set[str]],
) -> dict[str, float | int]:
    field_cells = set().union(*(field[surface] for surface in surfaces))
    exposure_cells = set().union(*(exposure[surface] for surface in surfaces))
    amount_cells = set().union(*(amount[surface] for surface in surfaces))
    amount_open_cells = set().union(*(amount_open[surface] for surface in surfaces))
    amount_clean_cells = set().union(*(amount_clean[surface] for surface in surfaces))
    field_forms = {cell.rsplit("|", 1)[1] for cell in field_cells}
    amount_forms = {cell.rsplit("|", 1)[1] for cell in amount_cells}
    amount_open_forms = {cell.rsplit("|", 1)[1] for cell in amount_open_cells}
    amount_clean_forms = {cell.rsplit("|", 1)[1] for cell in amount_clean_cells}
    union = field_cells | amount_cells
    union_open = field_cells | amount_open_cells
    return {
        "field_hit_cells": len(field_cells),
        "field_exposure_cells": len(exposure_cells),
        "field_specificity_rate": len(field_cells) / len(exposure_cells) if exposure_cells else 0.0,
        "positioned_amount_neighbour_cells": len(amount_cells),
        "open_positioned_amount_neighbour_cells": len(amount_open_cells),
        "gdt760_clean_content_contact_cells": len(amount_clean_cells),
        "field_or_positioned_neighbour_union_cells": len(union),
        "field_or_open_positioned_neighbour_union_cells": len(union_open),
        "field_form_breadth": len(field_forms),
        "positioned_amount_neighbour_form_breadth": len(amount_forms),
        "open_positioned_amount_neighbour_form_breadth": len(amount_open_forms),
        "gdt760_clean_content_contact_form_breadth": len(amount_clean_forms),
        "field_and_positioned_neighbour_form_breadth": len(field_forms & amount_forms),
        "field_and_open_positioned_neighbour_form_breadth": len(field_forms & amount_open_forms),
        "field_and_clean_content_form_breadth": len(field_forms & amount_clean_forms),
        "field_or_positioned_neighbour_union_pages": len(cell_pages(union)),
        "field_or_open_positioned_neighbour_union_pages": len(cell_pages(union_open)),
        "global_l_occurrences": sum(int(summary[surface]["l_occurrences"]) for surface in surfaces),
    }


def covariates(
    universe: set[str], occurrences: list[dict[str, str]], summary: dict[str, dict[str, str]],
) -> tuple[dict[str, dict[str, Any]], list[tuple[str, str, str]], list[str]]:
    styles = sorted({
        (row["section"], row["language"], row["hand"])
        for row in occurrences if row["terminal"] == "l"
    })
    bins = ["0", "1", "2", "3", "4", "5+"]
    by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in occurrences:
        if row["terminal"] == "l":
            by_surface[row["surface"]].append(row)
    output: dict[str, dict[str, Any]] = {}
    for surface in sorted(universe):
        rows = by_surface[surface]
        count = len(rows)
        if count != int(summary[surface]["l_occurrences"]):
            raise AssertionError(f"GDT800 count drift for {surface}")
        style_counts = Counter((row["section"], row["language"], row["hand"]) for row in rows)
        distance_counts = Counter(
            str(int(row["distance_from_end"])) if int(row["distance_from_end"]) < 5 else "5+"
            for row in rows
        )
        output[surface] = {
            "events": count,
            "pages": {row["page"] for row in rows},
            "style_counts": style_counts,
            "distance_counts": distance_counts,
            "style_profile": tuple(style_counts[key] / count for key in styles),
            "distance_profile": tuple(distance_counts[key] / count for key in bins),
        }
    return output, styles, bins


def total_variation(left: Sequence[float], right: Sequence[float]) -> float:
    return 0.5 * sum(abs(a - b) for a, b in zip(left, right))


def individual_distance(left: dict[str, Any], right: dict[str, Any]) -> float:
    return (
        abs(math.log1p(left["events"]) - math.log1p(right["events"]))
        + abs(math.log1p(len(left["pages"])) - math.log1p(len(right["pages"])))
        + total_variation(left["style_profile"], right["style_profile"])
        + total_variation(left["distance_profile"], right["distance_profile"])
    )


def nearest_pools(
    targets: Sequence[str], universe: set[str], features: dict[str, dict[str, Any]], k: int,
) -> dict[str, list[tuple[str, float]]]:
    controls = universe - set(targets)
    return {
        target: sorted(
            ((surface, individual_distance(features[target], features[surface])) for surface in controls),
            key=lambda item: (item[1], item[0]),
        )[:k]
        for target in targets
    }


def draw_injective(
    targets: Sequence[str], pools: dict[str, list[tuple[str, float]]], rng: random.Random,
) -> tuple[str, ...] | None:
    order = list(targets)
    rng.shuffle(order)
    used: set[str] = set()
    selected: list[str] = []
    for target in order:
        available = [surface for surface, _ in pools[target] if surface not in used]
        if not available:
            return None
        choice = rng.choice(available)
        used.add(choice)
        selected.append(choice)
    return tuple(sorted(selected))


def aggregate_profile(
    surfaces: Sequence[str], features: dict[str, dict[str, Any]],
    styles: Sequence[tuple[str, str, str]], bins: Sequence[str],
) -> dict[str, Any]:
    events = sum(features[surface]["events"] for surface in surfaces)
    pages = set().union(*(features[surface]["pages"] for surface in surfaces))
    style_counts: Counter[tuple[str, str, str]] = Counter()
    distance_counts: Counter[str] = Counter()
    for surface in surfaces:
        style_counts.update(features[surface]["style_counts"])
        distance_counts.update(features[surface]["distance_counts"])
    return {
        "events": events,
        "pages": len(pages),
        "style_profile": tuple(style_counts[key] / events for key in styles),
        "distance_profile": tuple(distance_counts[key] / events for key in bins),
    }


def aggregate_distance(left: dict[str, Any], right: dict[str, Any]) -> float:
    return (
        abs(math.log1p(left["events"]) - math.log1p(right["events"]))
        + abs(math.log1p(left["pages"]) - math.log1p(right["pages"]))
        + total_variation(left["style_profile"], right["style_profile"])
        + total_variation(left["distance_profile"], right["distance_profile"])
    )


def primary_aggregate_null(
    targets: Sequence[str], universe: set[str], features: dict[str, dict[str, Any]],
    styles: Sequence[tuple[str, str, str]], bins: Sequence[str],
    summary: dict[str, dict[str, str]], exposure: dict[str, set[str]],
    field: dict[str, set[str]], amount: dict[str, set[str]], amount_open: dict[str, set[str]],
    amount_clean: dict[str, set[str]],
    seed: int, draws: int, keep: int, k: int,
) -> tuple[list[dict[str, Any]], dict[str, list[tuple[str, float]]]]:
    pools = nearest_pools(targets, universe, features, k)
    target_profile = aggregate_profile(targets, features, styles, bins)
    rng = random.Random(seed)
    heap: list[tuple[float, int, tuple[str, ...]]] = []
    valid = 0
    for draw in range(1, draws + 1):
        selected = draw_injective(targets, pools, rng)
        if selected is None:
            continue
        valid += 1
        distance = aggregate_distance(
            aggregate_profile(selected, features, styles, bins), target_profile
        )
        item = (-distance, -draw, selected)
        if len(heap) < keep:
            heapq.heappush(heap, item)
        elif item > heap[0]:
            heapq.heapreplace(heap, item)
    if valid != draws or len(heap) != keep:
        raise AssertionError("aggregate null capacity changed")
    retained = sorted((-distance, -draw, selected) for distance, draw, selected in heap)
    rows: list[dict[str, Any]] = []
    for rank, (distance, draw, selected) in enumerate(retained, start=1):
        profile = aggregate_profile(selected, features, styles, bins)
        score = score_set(selected, summary, exposure, field, amount, amount_open, amount_clean)
        rows.append({
            "retained_rank": rank,
            "source_draw": draw,
            "aggregate_match_distance": f12(distance),
            "control_surfaces": "|".join(selected),
            "aggregate_events": profile["events"],
            "aggregate_pages": profile["pages"],
            **{name: f12(value) if isinstance(value, float) else value for name, value in score.items()},
        })
    return rows, pools


def metric_summary(
    variant: str, observed: dict[str, float | int], null_scores: Sequence[dict[str, float | int]],
    note: str,
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for metric in observed:
        values = sorted(float(row[metric]) for row in null_scores)
        obs = float(observed[metric])
        output.append({
            "null_variant": variant,
            "metric": metric,
            "observed": f12(obs),
            "null_draws": len(values),
            "null_mean": f12(sum(values) / len(values)),
            "null_q05": f12(values[int(0.05 * (len(values) - 1))]),
            "null_q50": f12(values[int(0.50 * (len(values) - 1))]),
            "null_q95": f12(values[int(0.95 * (len(values) - 1))]),
            "null_max": f12(values[-1]),
            "upper_tail_p_add_one": f12((1 + sum(value >= obs for value in values)) / (len(values) + 1)),
            "interpretation_note": note,
        })
    return output


def simple_null_scores(
    targets: Sequence[str], universe: set[str], features: dict[str, dict[str, Any]],
    summary: dict[str, dict[str, str]], exposure: dict[str, set[str]],
    field: dict[str, set[str]], amount: dict[str, set[str]], amount_open: dict[str, set[str]],
    amount_clean: dict[str, set[str]],
    seed: int, draws: int, k: int,
) -> tuple[list[dict[str, float | int]], dict[str, list[tuple[str, float]]]]:
    pools = nearest_pools(targets, universe, features, k)
    rng = random.Random(seed)
    scores: list[dict[str, float | int]] = []
    for _ in range(draws):
        selected = draw_injective(targets, pools, rng)
        if selected is None:
            raise AssertionError("simple null injective capacity changed")
        scores.append(score_set(selected, summary, exposure, field, amount, amount_open, amount_clean))
    return scores, pools


def target_union_rows(
    target: set[str], field_rows: list[dict[str, Any]], amount_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    cells: dict[str, dict[str, Any]] = {}
    for row in field_rows:
        if row["surface"] not in target or not int(row["independently_licensed_field"]):
            continue
        cell = cells.setdefault(str(row["cell_key"]), {
            "cell_key": row["cell_key"], "surface": row["surface"], "page": row["page"],
            "locus": row["locus"], "token_ordinal": row["token_ordinal"],
            "common_mask_field_hit": 0, "positioned_amount_neighbour_hit": 0,
            "open_positioned_amount_neighbour_hit": 0, "gdt760_clean_content_contact": 0,
            "field_channels": set(), "amount_expressions": set(),
        })
        cell["common_mask_field_hit"] = 1
        cell["field_channels"].add(row["field_channel_after_common_mask"])
    for row in amount_rows:
        if row["surface"] not in target or int(row["discovery_cell_excluded"]):
            continue
        cell = cells.setdefault(str(row["cell_key"]), {
            "cell_key": row["cell_key"], "surface": row["surface"], "page": row["page"],
            "locus": row["locus"], "token_ordinal": row["token_ordinal"],
            "common_mask_field_hit": 0, "positioned_amount_neighbour_hit": 0,
            "open_positioned_amount_neighbour_hit": 0, "gdt760_clean_content_contact": 0,
            "field_channels": set(), "amount_expressions": set(),
        })
        cell["positioned_amount_neighbour_hit"] = 1
        cell["open_positioned_amount_neighbour_hit"] = max(
            cell["open_positioned_amount_neighbour_hit"], int(row["open_positional_candidate"])
        )
        cell["gdt760_clean_content_contact"] = max(
            cell["gdt760_clean_content_contact"], int(row["selected_side_is_clean_content_contact"])
        )
        cell["amount_expressions"].add(row["amount_expression_eva"])
    output = []
    for index, cell in enumerate(sorted(cells.values(), key=lambda x: x["cell_key"]), start=1):
        output.append({
            **cell,
            "union_cell_id": f"G804-U{index:03d}",
            "field_channels": "|".join(sorted(cell["field_channels"])) or "NONE",
            "amount_expressions": "|".join(sorted(cell["amount_expressions"])) or "NONE",
            "selected_role_credit": "FIELD_OR_POSITIONAL_AMOUNT_NEIGHBOUR_CANDIDATE_ONLY",
            "literal_identity_credit": 0,
            "component_export_credit": 0,
        })
    return output


def contiguous_pair_count(text: str, head: str, value: str) -> int:
    tokens = text.split()
    return sum(tokens[index:index + 2] == [head, value] for index in range(len(tokens) - 1))


def quality_value_spans(
    lines: list[dict[str, str]], exact: dict[tuple[str, int], int],
    cross_by_locus: dict[str, dict[str, str]], discovery_cells: set[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    heads = {
        "chol": ("Trockenheits-/Trockengutfeld", "trocken"),
        "cheol": ("Stoff-/Zubereitungs- oder Trockenheitsfeld", "trocken oder Trockengut"),
        "sheol": ("Feuchtigkeits-/Feuchtgutfeld", "feucht oder eingeweicht"),
    }
    values = {"dain": ("II", "zweiter Grad"), "daiin": ("III", "dritter Grad")}
    output: list[dict[str, Any]] = []
    pair_ordinals: Counter[tuple[str, str, str]] = Counter()
    for line in lines:
        tokens = line["zl3b_line"].split()
        for index in range(len(tokens) - 1):
            head, value = tokens[index], tokens[index + 1]
            if head not in heads or value not in values:
                continue
            pair_key = (line["locus"], head, value)
            pair_ordinals[pair_key] += 1
            reader_line = cross_by_locus[line["locus"]]
            reader_pair_caps = [
                contiguous_pair_count(reader_line[field], head, value)
                for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")
            ]
            head_ordinal = index + 1
            cell_key = f"{line['page']}|{line['locus']}|{head_ordinal}|{head}"
            output.append({
                "quality_value_id": f"G804-QV{len(output) + 1:03d}",
                "page": line["page"],
                "locus": line["locus"],
                "section": line["section"],
                "language": line["language"],
                "hand": line["hand"],
                "head_ordinal": head_ordinal,
                "head_surface": head,
                "value_surface": value,
                "exact_span_eva": f"{head} {value}",
                "head_token_stable_all_three": exact[(line["locus"], head_ordinal)],
                "value_token_stable_all_three": exact[(line["locus"], head_ordinal + 1)],
                "both_tokens_stable_all_three": int(
                    exact[(line["locus"], head_ordinal)]
                    and exact[(line["locus"], head_ordinal + 1)]
                ),
                "contiguous_sequence_present_all_three": int(
                    pair_ordinals[pair_key] <= min(reader_pair_caps)
                ),
                "is_gdt803_discovery_span": int(cell_key in discovery_cells),
                "safe_renderer_de": f"{heads[head][0]}, Wert {values[value][0]}",
                "aggressive_renderer_de": f"{heads[head][1]}, {values[value][1]}",
                "aggressive_confidence": "C1" if head == "chol" else "C0",
                "written_line_eva": line["zl3b_line"],
                "literal_identity_credit": 0,
                "component_export_credit": 0,
            })
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in output:
        groups[(row["head_surface"], row["value_surface"])].append(row)
    summary = []
    for index, ((head, value), rows) in enumerate(sorted(groups.items()), start=1):
        summary.append({
            "summary_id": f"G804-QVS{index:02d}",
            "head_surface": head,
            "value_surface": value,
            "zl3b_contiguous_spans": len(rows),
            "both_token_stable_spans": sum(int(row["both_tokens_stable_all_three"]) for row in rows),
            "all_three_contiguous_sequence_spans": sum(
                int(row["contiguous_sequence_present_all_three"]) for row in rows
            ),
            "external_all_three_sequence_spans": sum(
                int(row["contiguous_sequence_present_all_three"])
                and not int(row["is_gdt803_discovery_span"])
                for row in rows
            ),
            "pages": len({row["page"] for row in rows}),
            "sections": "|".join(sorted({row["section"] for row in rows})),
            "safe_renderer_de": rows[0]["safe_renderer_de"],
            "aggressive_renderer_de": rows[0]["aggressive_renderer_de"],
            "historical_architecture_comparator": "GDT764:E010",
            "word_identity_credit": 0,
        })
    return output, summary


def right_value_profiles(
    surfaces: Sequence[str], tokens: list[dict[str, str]],
    exact: dict[tuple[str, int], int], discovery_cells: set[str],
) -> list[dict[str, Any]]:
    selected = set(surfaces)
    by_locus: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in tokens:
        by_locus[row["locus"]].append(row)
    occurrences: Counter[str] = Counter()
    pages: defaultdict[str, set[str]] = defaultdict(set)
    opportunities: Counter[str] = Counter()
    opportunity_pages: defaultdict[str, set[str]] = defaultdict(set)
    spans: Counter[str] = Counter()
    span_pages: defaultdict[str, set[str]] = defaultdict(set)
    discovery: Counter[str] = Counter()
    value_types: defaultdict[str, Counter[str]] = defaultdict(Counter)
    for locus, line in by_locus.items():
        line.sort(key=lambda row: int(row["token_index"]))
        for index, row in enumerate(line):
            surface = row["eva"]
            ordinal = int(row["token_index"])
            if surface in selected and exact[(locus, ordinal)]:
                occurrences[surface] += 1
                pages[surface].add(row["page"])
            if surface not in selected or index + 1 >= len(line):
                continue
            right = line[index + 1]
            right_ordinal = int(right["token_index"])
            if exact[(locus, ordinal)]:
                opportunities[surface] += 1
                opportunity_pages[surface].add(row["page"])
            if (
                right["eva"] in {"dain", "daiin"}
                and exact[(locus, ordinal)] and exact[(locus, right_ordinal)]
            ):
                spans[surface] += 1
                span_pages[surface].add(row["page"])
                value_types[surface][right["eva"]] += 1
                cell_key = f"{row['page']}|{locus}|{ordinal}|{surface}"
                discovery[surface] += int(cell_key in discovery_cells)
    output = []
    for surface in surfaces:
        count = occurrences[surface]
        output.append({
            "surface": surface,
            "reader_stable_occurrences": count,
            "reader_stable_pages": len(pages[surface]),
            "reader_stable_right_context_opportunities": opportunities[surface],
            "reader_stable_right_context_pages": len(opportunity_pages[surface]),
            "reader_stable_right_dain_daiin_spans": spans[surface],
            "gdt803_discovery_right_value_spans": discovery[surface],
            "external_reader_stable_right_value_spans": spans[surface] - discovery[surface],
            "reader_stable_right_value_pages": len(span_pages[surface]),
            "right_value_type_counts": "|".join(
                f"{value}:{value_types[surface][value]}" for value in sorted(value_types[surface])
            ) or "NONE",
            "right_value_span_rate": f12(
                spans[surface] / opportunities[surface] if opportunities[surface] else 0.0
            ),
            "semantic_identity_credit": 0,
        })
    return output


def cheol_control_rows(
    primary_pools: dict[str, list[tuple[str, float]]],
    tokens: list[dict[str, str]], exact: dict[tuple[str, int], int],
    discovery_cells: set[str], lines: list[dict[str, str]],
    summary: dict[str, dict[str, str]],
) -> list[dict[str, Any]]:
    controls = primary_pools["cheol"]
    surfaces = ["cheol", *(surface for surface, _ in controls)]
    profiles = {
        row["surface"]: row
        for row in right_value_profiles(surfaces, tokens, exact, discovery_cells)
    }
    target = profiles["cheol"]
    raw_pairs: Counter[str] = Counter()
    for line in lines:
        line_tokens = line["zl3b_line"].split()
        for index in range(len(line_tokens) - 1):
            if line_tokens[index] in surfaces and line_tokens[index + 1] in {"dain", "daiin"}:
                raw_pairs[line_tokens[index]] += 1
    target_raw_count = raw_pairs["cheol"]
    target_raw_occurrences = int(summary["cheol"]["l_occurrences"])
    target_raw_rate = target_raw_count / target_raw_occurrences
    output = []
    for rank, (surface, distance) in enumerate([("cheol", 0.0), *controls]):
        row = profiles[surface]
        output.append({
            "cohort": "TARGET" if surface == "cheol" else "OUTCOME_BLIND_PRIMARY_K12_CONTROL",
            "control_rank": rank,
            "surface": surface,
            "individual_covariate_distance": f12(distance),
            "zl3b_l_occurrences": summary[surface]["l_occurrences"],
            "zl3b_right_dain_daiin_spans": raw_pairs[surface],
            "zl3b_right_value_span_rate": f12(
                raw_pairs[surface] / int(summary[surface]["l_occurrences"])
            ),
            "zl3b_at_least_cheol_span_count": int(raw_pairs[surface] >= target_raw_count),
            "zl3b_at_least_cheol_span_rate": int(
                raw_pairs[surface] / int(summary[surface]["l_occurrences"]) >= target_raw_rate
            ),
            "zl3b_at_least_cheol_count_and_rate": int(
                raw_pairs[surface] >= target_raw_count
                and raw_pairs[surface] / int(summary[surface]["l_occurrences"]) >= target_raw_rate
            ),
            "reader_stable_occurrences": row["reader_stable_occurrences"],
            "reader_stable_right_context_opportunities": row["reader_stable_right_context_opportunities"],
            "reader_stable_right_dain_daiin_spans": row["reader_stable_right_dain_daiin_spans"],
            "right_value_span_rate": row["right_value_span_rate"],
            "reader_stable_at_least_cheol_span_count": int(
                int(row["reader_stable_right_dain_daiin_spans"])
                >= int(target["reader_stable_right_dain_daiin_spans"])
            ),
            "reader_stable_at_least_cheol_span_rate": int(
                float(row["right_value_span_rate"]) >= float(target["right_value_span_rate"])
            ),
            "reader_stable_at_least_cheol_count_and_rate": int(
                int(row["reader_stable_right_dain_daiin_spans"])
                >= int(target["reader_stable_right_dain_daiin_spans"])
                and float(row["right_value_span_rate"]) >= float(target["right_value_span_rate"])
            ),
            "matching_outcome_fields_used": "NONE",
            "semantic_identity_credit": 0,
        })
    return output


def quality_value_edge_packet(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Encode the written adjacencies for the mandatory GDT388 intake gate.

    These are already inspected formal text relations, not sealed visual
    acquisitions.  They are deliberately marked ineligible; the intake is
    retained to make that limitation executable instead of tacit.
    """
    output: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        page = str(row["page"])
        physical_match = re.match(r"^(f\d+)", page)
        if physical_match is None:
            raise AssertionError(f"cannot derive physical folio from {page}")
        head_ordinal = int(row["head_ordinal"])
        value_ordinal = head_ordinal + 1
        output.append({
            "edge_id": f"G804E{index:03d}",
            "batch_id": "GDT804_QUALITY_VALUE_TEXT_ORDER",
            "page": page,
            "physical_folio": physical_match.group(1),
            "diagram_unit_id": "CACHED_TEXT_LINE",
            "pivot_visual_id": f"TOKEN_{row['head_surface']}_{head_ordinal}",
            "pivot_locus": f"{row['locus']}@{head_ordinal}",
            "target_visual_id": f"TOKEN_{row['value_surface']}_{value_ordinal}",
            "target_locus": f"{row['locus']}@{value_ordinal}",
            "relation_type": "EXACT_CONTIGUOUS_TEXT_ORDER",
            "direction_basis": "WRITTEN_LEFT_TO_RIGHT",
            "ownership_basis": "SAME_CACHED_TEXT_LINE",
            "geometry_only_selection": "FALSE",
            "source_manifest_id": "GDT804",
            "page_crop_sha256": "NONE",
            "pivot_crop_sha256": "NONE",
            "target_crop_sha256": "NONE",
            "source_aware_localizer": "GDT804_BUILDER",
            "relation_reviewer": "PENDING_EXTERNAL",
            "relation_confidence": "EXACT_TRANSCRIPTION_ADJACENCY",
            "ambiguity_state": "SEMANTICALLY_UNRESOLVED",
            "formal_access_state": "FORMAL_ACCESSED",
            "fold_assignment": "NONE",
            "eligibility_status": "INELIGIBLE_EXPLORATORY_TEXT_RELATION",
        })
    return output


def run_edge_intake(packet_path: Path, intake_path: Path, packet_rows: int) -> dict[str, Any]:
    completed = subprocess.run(
        [str(VMANUS_EXP), "check-edge-packet", str(packet_path)],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    expected = {
        "status": "INVALID_PACKET",
        "packet_rows": packet_rows,
        "eligible_edges": 0,
        "eligible_folios": 0,
        "discovery_edges": 0,
        "holdout_edges": 0,
        "mobile_edges": 0,
        "capacity_gate_50_edges_5_folios": False,
        "holdout_gate": False,
        "mobile_null_gate": False,
        "score_ready": False,
        "errors": [
            f"edge row {number}: formal access is not sealed"
            for number in range(2, packet_rows + 2)
        ],
    }
    if completed.returncode != 1 or completed.stderr or json.loads(completed.stdout) != expected:
        raise AssertionError("GDT388 quality-value edge intake drift")
    intake_path.write_text(
        json.dumps(expected, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return expected


def middle_census(
    targets: Sequence[str], brackets: list[dict[str, str]], occurrences: list[dict[str, str]],
    summary: dict[str, dict[str, str]], field_rows: list[dict[str, Any]],
    amount_rows: list[dict[str, Any]], quality_rows: list[dict[str, Any]],
    priors: dict[str, dict[str, str]],
) -> list[dict[str, Any]]:
    bracket_ids = {row["occurrence_id"] for row in brackets}
    output: list[dict[str, Any]] = []
    for surface in targets:
        all_occ = [row for row in occurrences if row["surface"] == surface and row["terminal"] == "l"]
        outside = [row for row in all_occ if row["occurrence_id"] not in bracket_ids]
        exposures = [row for row in field_rows if row["surface"] == surface]
        field_hits = [row for row in exposures if int(row["independently_licensed_field"])]
        amount_hits = [
            row for row in amount_rows
            if row["surface"] == surface and not int(row["discovery_cell_excluded"])
        ]
        open_amount = [row for row in amount_hits if int(row["open_positional_candidate"])]
        clean_amount = [row for row in amount_hits if int(row["selected_side_is_clean_content_contact"])]
        qv = [row for row in quality_rows if row["head_surface"] == surface]
        channels = Counter(row["field_channel_after_common_mask"] for row in field_hits)
        prior = priors[surface]
        output.append({
            "surface": surface,
            "stem": summary[surface]["stem"],
            "gdt800_l_occurrences": len(all_occ),
            "gdt800_l_pages": len({row["page"] for row in all_occ}),
            "gdt803_bracket_occurrences": len(all_occ) - len(outside),
            "outside_bracket_occurrences": len(outside),
            "outside_bracket_pages": len({row["page"] for row in outside}),
            "common_mask_field_exposures": len(exposures),
            "common_mask_licensed_hits": len(field_hits),
            "common_mask_hit_pages": len({row["page"] for row in field_hits}),
            "common_mask_channel_counts": "|".join(f"{key}:{channels[key]}" for key in sorted(channels)) or "NONE",
            "positioned_amount_neighbour_hits": len(amount_hits),
            "positioned_open_amount_neighbour_hits": len(open_amount),
            "gdt760_clean_content_contact_hits": len(clean_amount),
            "quality_value_right_spans": len(qv),
            "cross_map_role": (
                "FIELD_AND_POSITIONAL_AMOUNT_NEIGHBOUR" if field_hits and amount_hits else
                "FIELD_ONLY" if field_hits else
                "POSITIONAL_AMOUNT_NEIGHBOUR_ONLY" if amount_hits else "NO_INDEPENDENT_MAP_HIT"
            ),
            **prior,
        })
    return output


def bracket_reader(
    brackets: list[dict[str, str]], contexts: dict[tuple[str, str], dict[str, str]],
    middle_priors: dict[str, dict[str, str]], readings: dict[str, dict[str, str]],
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for row in brackets:
        left = contexts[("LEFT", row["left_context"])]
        right = contexts[("RIGHT", row["right_context"])]
        middle = middle_priors[row["target_surface"]]
        manual = readings[row["bracket_id"]]
        output.append({
            "bracket_id": row["bracket_id"],
            "page": row["source_selector"],
            "locus": row["locus"],
            "exact_three_token_span": row["exact_three_token_span"],
            "left_surface": row["left_context"],
            "left_preexisting_role": left["preexisting_broad_role"],
            "left_preexisting_default_de": left["preexisting_working_default_de"],
            "middle_surface": row["target_surface"],
            "middle_selected_role": middle["preferred_role_class"],
            "middle_conservative_default_de": middle["conservative_working_default_de"],
            "right_surface": row["right_context"],
            "right_preexisting_role": right["preexisting_broad_role"],
            "right_preexisting_default_de": right["preexisting_working_default_de"],
            "safe_renderer_de": manual["safe_renderer_de"],
            "aggressive_renderer_de": manual["aggressive_renderer_de"],
            "aggressive_confidence": manual["aggressive_confidence"],
            "preferred_model": manual["preferred_model"],
            "countermodel": manual["countermodel"],
            "full_zl3b_line": row["full_zl3b_line"],
            "renderer_scope": "THIS_EXACT_THREE_TOKEN_SPAN_ONLY",
            "confirmed_plaintext": 0,
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    return output


def adjudication_rows(census: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output = []
    for row in census:
        field_hits = int(row["common_mask_licensed_hits"])
        amount_hits = int(row["positioned_amount_neighbour_hits"])
        clean_content_hits = int(row["gdt760_clean_content_contact_hits"])
        if row["surface"] == "cheol":
            decision = "RETAIN_BEST_MATERIAL_RIVAL__NO_RIGHT_VALUE_SPECIFICITY_LEAD"
        elif row["surface"] == "ol":
            decision = "RETAIN_GENERAL_QUANTITY_BEARING_CARRIER"
        elif row["surface"] == "qokol":
            decision = "RETAIN_PROCESS_RIVAL__STRONGEST_EXTERNAL_RIGHT_VALUE_COUNT"
        elif row["surface"] in {"sail", "okal", "okail"}:
            decision = "RETAIN_OPAQUE_ENTRY_MODEL"
        elif field_hits:
            decision = "RETAIN_WHOLE_SPECIFIC_FIELD_LEAD"
        elif amount_hits:
            decision = "RETAIN_POSITIONAL_AMOUNT_NEIGHBOUR_CANDIDATE"
        else:
            decision = "RETAIN_OPEN_ROLE_RIVAL"
        output.append({
            "rank_for_concrete_followup": row["concrete_noun_priority"],
            "surface": row["surface"],
            "decision": decision,
            "selected_working_role": row["preferred_role_class"],
            "safe_default_de": row["conservative_working_default_de"],
            "aggressive_default_de": row["aggressive_working_default_de"],
            "confidence": row["confidence"],
            "field_hits": field_hits,
            "positioned_amount_neighbour_hits": amount_hits,
            "gdt760_clean_content_contact_hits": clean_content_hits,
            "quality_value_spans": row["quality_value_right_spans"],
            "positive_evidence": row["positive_evidence_code"],
            "counterevidence": row["counterevidence_code"],
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    return sorted(output, key=lambda row: (int(row["rank_for_concrete_followup"]), row["surface"]))


def write_report(
    path: Path, target_score: dict[str, float | int], null_summary: list[dict[str, Any]],
    quality_summary: list[dict[str, Any]], census: list[dict[str, Any]],
    middle_right_profiles: list[dict[str, Any]], cheol_controls: list[dict[str, Any]],
) -> None:
    by_variant = {
        variant: {row["metric"]: row for row in null_summary if row["null_variant"] == variant}
        for variant in {row["null_variant"] for row in null_summary}
    }
    primary = by_variant["PRIMARY_AGGREGATE_MATCHED_200000_KEEP5000"]
    individual = by_variant["SENSITIVITY_INDIVIDUAL_NEAREST10_100000"]
    without_ol = by_variant["LEAVE_OL_OUT_INDIVIDUAL_NEAREST10_100000"]
    quality_counts = {(row["head_surface"], row["value_surface"]): row for row in quality_summary}
    right_profile = {row["surface"]: row for row in middle_right_profiles}
    control_only = [row for row in cheol_controls if row["cohort"] != "TARGET"]
    lines = [
        "# GDT804 — wholespezifische Klammermitten, kein pauschaler Stoffslot", "",
        f"Status: `{STATUS}`", "", "## Ergebnis", "",
        "Die elf Mittelwörter der zwölf GDT803-Klammern sind **nicht** einfach elf",
        "bereits bestätigte Pflanzen- oder Zutatennamen. Ihre exakte Schnittmenge mit",
        "dem identischen offenen Oberflächendeck aus GDT744/GDT745 ist **null**. Das",
        "heißt nur, dass sie dort nicht vorselektiert waren; es widerlegt keine",
        "Inhaltsrolle. Der neue gemeinsame",
        "Maskenlauf entfernt deshalb alle 155 gepaarten `Xl`-Formen gleichzeitig als",
        "Bedeutungsanker. Trotzdem bleiben 72 von GDT744s Feldern durch fremde Anker",
        "lizenziert.", "",
        f"In diesen unabhängigen Feldern liegen {target_score['field_hit_cells']} von",
        f"{target_score['field_exposure_cells']} exponierten Mittelwortzellen. Gegen die",
        f"5.000 am besten aggregiert gematchten Kontrollsets sind es im Mittel",
        f"{primary['field_hit_cells']['null_mean']} Treffer",
        f"(`p={primary['field_hit_cells']['upper_tail_p_add_one']}`). Aber auch die bloße",
        f"Feldexposition ist ungewöhnlich hoch (Nullmittel",
        f"{primary['field_exposure_cells']['null_mean']};",
        f"`p={primary['field_exposure_cells']['upper_tail_p_add_one']}`), und die",
        f"Trefferquote {target_score['field_specificity_rate']:.3f} liegt im aggregierten",
        f"Matching ebenfalls hoch (`p={primary['field_specificity_rate']['upper_tail_p_add_one']}`).",
        "Das Resultat ist jedoch match-sensitiv: Unter dem individuellen Zehn-Nachbarn-",
        f"Matching fällt die Trefferquote auf `p={individual['field_specificity_rate']['upper_tail_p_add_one']}`;",
        "im individuellen Leave-`ol`-out-Lauf auf",
        f"`p={without_ol['field_specificity_rate']['upper_tail_p_add_one']}`. Die Rohcounts werden",
        "von `ol` dominiert; Richtung und Stärke hängen aber vom Kontrollmodell ab.",
        "Installiert wird deshalb nur ein **kontrollsensitiver Sachfeld-Nachbarschaftslead**," ,
        "kein Lemma- oder",
        "Zutatenbeweis.", "", "## Die Mengenkarte bestätigt keinen einheitlichen Stoffslot", "",
        f"GDT804 findet {target_score['positioned_amount_neighbour_cells']} Nachbarn auf",
        "der von GDT760 bevorzugten Seite (FIRST→rechts, MIDDLE→links), davon",
        f"{target_score['open_positioned_amount_neighbour_cells']} zuvor offene Kandidaten.",
        "Das sind **keine automatisch lizenzierten Inhaltsplätze**: Keine der fünfzehn",
        "ausgewählten Mittelformseiten war in GDT760 bereits ein sauberer CONTENT_PREP-",
        "Kontakt. In `f88r.10` steht zwar `cheol` auf der bevorzugten linken Seite, aber",
        "GDT760s tatsächliche Inhaltslizenz gehört rechts zu `cheos`. Die offenen",
        f"Positionsnachbarn liegen im aggregierten Null bei {primary['open_positioned_amount_neighbour_cells']['null_mean']}",
        f"(`p={primary['open_positioned_amount_neighbour_cells']['upper_tail_p_add_one']}`).",
        "Damit fällt der behauptete einheitliche Stoffslot weg.", "",
        "## Die Zwei-Achsen-Lesung bleibt Kandidat, nicht Ergebnis", "",
        "Im ZL3b-Cache stehen `chol`, `cheol` und `sheol` 41-mal direkt vor",
        "`dain/daiin`. Davon sind 33 Paarsequenzen in allen drei Leserfassungen",
        "vorhanden; der strengere tokenweise Stabilitätsgate behält 32:", "",
        "| Paar | ZL3b | beide Tokens stabil | Sequenz in allen drei | extern zur GDT803-Entdeckung |",
        "|---|---:|---:|---:|---:|",
        *[
            f"| `{head} {value}` | {quality_counts[(head, value)]['zl3b_contiguous_spans']} | "
            f"{quality_counts[(head, value)]['both_token_stable_spans']} | "
            f"{quality_counts[(head, value)]['all_three_contiguous_sequence_spans']} | "
            f"{quality_counts[(head, value)]['external_all_three_sequence_spans']} |"
            for head, value in sorted(quality_counts)
        ], "",
        "GDT759 hatte zwei `chor chol daiin`-Stellen bereits explorativ als Pflanzenteil",
        "plus Trockenheitszustand plus Wert III gerendert. GDT764s historischer Comparator",
        "E010 belegt nur die passende Rezeptbucharchitektur aus Qualität und Grad, nicht",
        "die Voynich-Wortwerte. Außerdem war die Familie `chol/cheol/sheol` semantisch",
        "post hoc gewählt. Im gleichberechtigten Zensus aller elf Klammermitten besitzt",
        f"`ol` {right_profile['ol']['external_reader_stable_right_value_spans']} externe",
        f"extern positionsstabile rechte Werte und `qokol` {right_profile['qokol']['external_reader_stable_right_value_spans']},",
        f"`cheol` dagegen nur {right_profile['cheol']['external_reader_stable_right_value_spans']}.",
        "Damit bleibt folgende Lesung ein konkreter Satzkandidat, aber kein ausgewählter",
        "Wortwert:", "", "```text",
        "qokain cheol daiin", "≈ heiß im II. Grad; trocken im III. Grad", "```", "",
        "Die sichere Ausgabe bleibt `qokain-Qualitätsfeld; cheol-Feld, Wert III`.",
        "`qokain=heiß II` stammt aus GDT636 und ist eine geerbte interne Ganzwort-/Kompositionstheorie,",
        "nicht unabhängig als Klartext bestätigt. `cheol` selbst ist gegen seine zwölf",
        "outcome-blind K12-Kontrollen ohne Spezifitätsvorsprung: Im rohen ZL3b-Zensus werden",
        f"Count/Rate/beides von {sum(int(row['zl3b_at_least_cheol_span_count']) for row in control_only)}/"

        f"{sum(int(row['zl3b_at_least_cheol_span_rate']) for row in control_only)}/"
        f"{sum(int(row['zl3b_at_least_cheol_count_and_rate']) for row in control_only)} der zwölf Kontrollen",
        "erreicht oder übertroffen; im strengeren positionsstabilen Zensus sogar von",
        f"{sum(int(row['reader_stable_at_least_cheol_span_count']) for row in control_only)}/"
        f"{sum(int(row['reader_stable_at_least_cheol_span_rate']) for row in control_only)}/"
        f"{sum(int(row['reader_stable_at_least_cheol_count_and_rate']) for row in control_only)}.",
        "Sichere und aggressive Lesung bleiben deshalb getrennt.", "", "## Elf wholespezifische Arbeitswerte", "",
        "| Form | gegenwärtiger Default | unabhängige Felder | bevorzugte Mengenseite | GDT760-Inhaltskontakt | beide Tokens positionsstabil vor dain/daiin | Entscheidung |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for row in sorted(census, key=lambda item: int(item["concrete_noun_priority"])):
        lines.append(
            f"| `{row['surface']}` | {row['conservative_working_default_de']} | "
            f"{row['common_mask_licensed_hits']} | {row['positioned_amount_neighbour_hits']} | "
            f"{row['gdt760_clean_content_contact_hits']} | "
            f"{right_profile[row['surface']]['reader_stable_right_dain_daiin_spans']} | "
            f"{row['preferred_role_class']} |"
        )
    lines.extend([
        "", "`cheol` bleibt wegen vier fremd verankerten Feldern der beste",
        "**Materialrivale** der Klammermitten; GDT760 fügt keinen lizenzierten",
        "Inhaltskontakt hinzu. Seine",
        "Trockenheits-/Zwei-Achsen-Lesung erhält jedoch keinen Spezifitätsvorsprung. `ol` bleibt",
        "der stärkste allgemeine mengenfähige Träger, aber gerade deshalb kein guter Kandidat",
        "für ein einzelnes konkretes Medium wie Öl, Wasser oder Wein. `sail`, `okal` und",
        "`okail` bleiben opake Einträge; insbesondere wird die verworfene Samenlesung von",
        "`sail` nicht wiederbelebt.", "", "## Nächste Route", "",
        "Alle elf Mittelwörter werden gleich behandelt. Ihre zwölf Entdeckungsstellen",
        "bleiben markiert und werden abgezogen; positionsstabile rechte Kontexte werden",
        "gegen dieselben K12-Kontrollen verglichen. `qokol`, `ol` und `cheol` gehen als",
        "gleichberechtigte Prozess-, Träger- und Materialrivalen hinein. Erst wenn eine",
        "Ganzform dieselbe konkrete Rolle in mehreren unabhängigen Konstruktionen hält,",
        "wird ein Stoff- oder Eigenschaftswert eingesetzt.", "",
        "Die 41 Textadjazenzen wurden außerdem als GDT388-Paket eingereicht. Der Intake",
        "bleibt erwartungsgemäß `INVALID_PACKET`: Die Auswahl erfolgte nach Formalzugriff,",
        "es gibt keine mobile Null und 41 Kanten liegen unter der Kapazitätsgrenze 50.",
        "Sie zählen deshalb als interne Textbeobachtung, nicht als scorefähige unabhängige",
        "Relationsevidenz.", "",
        "Keine neue Seite, kein Bild und keine Transkription wurde geöffnet; `f84/f84r`",
        "bleiben ausgeschlossen. Alle deutschen Werte sind ersetzbare Arbeitsrenderer,",
        "nicht bestätigter Klartext.",
    ])
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def build(output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    g744 = load_g744_module()
    stem_rows = read_tsv(STEM_SUMMARY)
    occurrence_rows = read_tsv(OCCURRENCES)
    bracket_rows = read_tsv(BRACKETS)
    line_rows = read_tsv(LINES)
    reader_tokens, reader_exact, cross_by_locus, reader_query_stats = load_reader_context()
    for material in (occurrence_rows, bracket_rows, line_rows):
        assert_unsealed(material)
    if len(stem_rows) != 155 or len(occurrence_rows) != 4137 or len(bracket_rows) != 12:
        raise AssertionError("locked GDT800/GDT803 population drift")
    universe = {row["l_surface"] for row in stem_rows}
    targets = sorted({row["target_surface"] for row in bracket_rows})
    target = set(targets)
    if len(universe) != 155 or len(targets) != 11 or not target <= universe:
        raise AssertionError("paired-Xl or middle cohort drift")
    summary = {row["l_surface"]: row for row in stem_rows}
    middle_prior_rows = read_tsv(MIDDLE_PRIORS)
    middle_priors = {row["surface"]: row for row in middle_prior_rows}
    if set(middle_priors) != target:
        raise AssertionError("middle role deck does not equal GDT803 cohort")
    bracket_reading_rows = read_tsv(BRACKET_READINGS)
    bracket_readings = {row["bracket_id"]: row for row in bracket_reading_rows}
    if set(bracket_readings) != {row["bracket_id"] for row in bracket_rows}:
        raise AssertionError("bracket renderer deck drift")

    g744_open = {row["candidate_surface"] for row in read_tsv(G744_OPEN_SLOTS)}
    g745_open = {row["candidate_surface"] for row in read_tsv(G745_OPEN_ROLES)}
    if target & g744_open or target & g745_open:
        raise AssertionError("middle/open-slot zero intersection changed")

    fields, _ = mask_and_build_fields(universe, g744)
    licensed_fields = flatten_licensed_fields(fields)
    exposures = field_exposures(fields, universe, target, g744)
    if len(licensed_fields) != 72 or len(exposures) != 107:
        raise AssertionError("common-mask field capacity drift")

    occurrence_by_id = {row["occurrence_id"]: row for row in occurrence_rows}
    discovery_cells = {
        f"{row['source_selector']}|{row['locus']}|{occurrence_by_id[row['occurrence_id']]['token_index']}|{row['target_surface']}"
        for row in bracket_rows
    }
    amount_slots = positional_amount_slots(universe, target, discovery_cells)
    exposure_map, field_map, amount_map, amount_open_map, amount_clean_map = maps_by_surface(
        exposures, amount_slots, universe
    )
    target_score = score_set(
        targets, summary, exposure_map, field_map, amount_map, amount_open_map, amount_clean_map
    )
    expected_target = {
        "field_hit_cells": 18, "field_exposure_cells": 45,
        "positioned_amount_neighbour_cells": 15,
        "open_positioned_amount_neighbour_cells": 14,
        "gdt760_clean_content_contact_cells": 0,
        "field_or_positioned_neighbour_union_cells": 30,
        "field_or_open_positioned_neighbour_union_cells": 29,
        "field_form_breadth": 6, "field_and_positioned_neighbour_form_breadth": 5,
        "field_and_open_positioned_neighbour_form_breadth": 4,
        "gdt760_clean_content_contact_form_breadth": 0,
        "field_and_clean_content_form_breadth": 0,
        "global_l_occurrences": 1098,
    }
    for name, expected in expected_target.items():
        if target_score[name] != expected:
            raise AssertionError(f"target score drift: {name}")
    union_rows = target_union_rows(target, exposures, amount_slots)
    if len(union_rows) != 30:
        raise AssertionError("target union cell count drift")

    features, styles, bins = covariates(universe, occurrence_rows, summary)
    primary_rows, primary_pools = primary_aggregate_null(
        targets, universe, features, styles, bins, summary, exposure_map, field_map,
        amount_map, amount_open_map, amount_clean_map,
        PRIMARY_SEED, PRIMARY_DRAWS, PRIMARY_KEEP, PRIMARY_K,
    )
    primary_scores = [{name: float(row[name]) for name in target_score} for row in primary_rows]
    null_summary = metric_summary(
        "PRIMARY_AGGREGATE_MATCHED_200000_KEEP5000", target_score, primary_scores,
        "Outcome-blind aggregate match on total events, union pages, style and line-end distance",
    )
    simple_scores, simple_pools = simple_null_scores(
        targets, universe, features, summary, exposure_map, field_map, amount_map,
        amount_open_map, amount_clean_map,
        SENSITIVITY_SEED, SENSITIVITY_DRAWS, SENSITIVITY_K,
    )
    null_summary.extend(metric_summary(
        "SENSITIVITY_INDIVIDUAL_NEAREST10_100000", target_score, simple_scores,
        "Individual outcome-blind nearest pools; retains aggregate frequency imbalance",
    ))
    ablated_targets = [surface for surface in targets if surface != "ol"]
    ablated_score = score_set(
        ablated_targets, summary, exposure_map, field_map, amount_map, amount_open_map,
        amount_clean_map,
    )
    ablated_scores, ablated_pools = simple_null_scores(
        ablated_targets, universe - {"ol"}, features, summary, exposure_map, field_map,
        amount_map, amount_open_map, amount_clean_map,
        ABLATION_SEED, SENSITIVITY_DRAWS, SENSITIVITY_K,
    )
    null_summary.extend(metric_summary(
        "LEAVE_OL_OUT_INDIVIDUAL_NEAREST10_100000", ablated_score, ablated_scores,
        "Sensitivity showing the cohort's raw cell counts are ol-sensitive",
    ))

    pool_rows: list[dict[str, Any]] = []
    for variant, pools in (("PRIMARY_K12", primary_pools), ("SENSITIVITY_K10", simple_pools), ("LEAVE_OL_OUT_K10", ablated_pools)):
        for target_surface in sorted(pools):
            for rank, (control, distance) in enumerate(pools[target_surface], start=1):
                pool_rows.append({
                    "pool_variant": variant, "target_surface": target_surface,
                    "neighbor_rank": rank, "control_surface": control,
                    "individual_covariate_distance": f12(distance),
                    "outcome_fields_used_for_matching": "NONE",
                })

    quality_rows, quality_summary = quality_value_spans(
        line_rows, reader_exact, cross_by_locus, discovery_cells
    )
    if len(quality_rows) != 41:
        raise AssertionError("quality-value span capacity drift")
    if sum(int(row["both_tokens_stable_all_three"]) for row in quality_rows) != 32:
        raise AssertionError("token-stable quality-value span capacity drift")
    if sum(int(row["contiguous_sequence_present_all_three"]) for row in quality_rows) != 33:
        raise AssertionError("cross-reader quality-value sequence capacity drift")
    if not any(row["locus"] == "f111v.23" and row["exact_span_eva"] == "cheol daiin" for row in quality_rows):
        raise AssertionError("central cheol daiin passage missing")
    historical = {row["historical_candidate_id"]: row for row in read_tsv(G764_HISTORICAL)}
    if historical["E010"]["attested_form"] != "Calide in 3o gradu; c. et s. in iii gradu":
        raise AssertionError("historical E010 comparator drift")
    if not any(row["exact_span_eva"] == "chor chol" and row["immediate_right_context"] == "daiin" for row in read_tsv(G759_PART_STATES)):
        raise AssertionError("GDT759 chor chol daiin bridge missing")
    if not any(
        row["entry"] == "qokain"
        and row["working_meaning_de"] == "heiß, Grad II"
        for row in read_tsv(G636_DICT)
    ):
        raise AssertionError("GDT636 qokain aggressive rival missing")
    middle_right_profiles = right_value_profiles(
        targets, reader_tokens, reader_exact, discovery_cells
    )
    middle_right_by_surface = {row["surface"]: row for row in middle_right_profiles}
    expected_right_counts = {
        "chal": (29, 1, 1), "chedal": (14, 1, 1), "cheol": (114, 2, 1),
        "okail": (1, 0, 0), "okal": (91, 0, 0), "ol": (339, 9, 9),
        "otal": (99, 1, 1), "qokeol": (33, 1, 1), "qokol": (82, 4, 4),
        "qotal": (49, 1, 1), "sail": (1, 0, 0),
    }
    for surface, expected in expected_right_counts.items():
        observed = middle_right_by_surface[surface]
        if tuple(int(observed[field]) for field in (
            "reader_stable_right_context_opportunities", "reader_stable_right_dain_daiin_spans",
            "external_reader_stable_right_value_spans",
        )) != expected:
            raise AssertionError(f"middle right-value profile drift for {surface}")
    cheol_controls = cheol_control_rows(
        primary_pools, reader_tokens, reader_exact, discovery_cells, line_rows, summary
    )
    control_only = [row for row in cheol_controls if row["cohort"] != "TARGET"]
    if (
        sum(int(row["zl3b_at_least_cheol_span_count"]) for row in control_only) != 7
        or sum(int(row["zl3b_at_least_cheol_span_rate"]) for row in control_only) != 7
        or sum(int(row["zl3b_at_least_cheol_count_and_rate"]) for row in control_only) != 5
        or sum(int(row["reader_stable_at_least_cheol_span_count"]) for row in control_only) != 8
        or sum(int(row["reader_stable_at_least_cheol_span_rate"]) for row in control_only) != 10
        or sum(int(row["reader_stable_at_least_cheol_count_and_rate"]) for row in control_only) != 8
    ):
        raise AssertionError("cheol K12 right-value specificity drift")
    edge_rows = quality_value_edge_packet(quality_rows)
    if len(edge_rows) != 41 or len({row["page"] for row in edge_rows}) != 37:
        raise AssertionError("quality-value edge packet capacity drift")
    if len({row["physical_folio"] for row in edge_rows}) != 31:
        raise AssertionError("quality-value edge physical-folio capacity drift")

    census = middle_census(targets, bracket_rows, occurrence_rows, summary, exposures, amount_slots, quality_rows, middle_priors)
    contexts = {(row["side"], row["context_surface"]): row for row in read_tsv(CONTEXT_PRIORS)}
    bracket_output = bracket_reader(bracket_rows, contexts, middle_priors, bracket_readings)
    adjudication = adjudication_rows(census)
    if not any(row["surface"] == "ol" and row["new_role"] == "QUANTITY_BEARING_PREPARATION_OR_CONTENT_CARRIER" for row in read_tsv(G762_CARRIERS)):
        raise AssertionError("GDT762 ol carrier prior missing")
    if not any(row["surface"] == "qokeol" for row in read_tsv(G753_WHOLE_ROLES)):
        raise AssertionError("GDT753 qokeol role census missing")
    if not any(row["model_id"] == "CLASS_SLOT_ENTRY_CODE" and row["status_after_gdt793"] == "SELECT_C0_WORKING_DEFAULT" for row in read_tsv(G793_ADJUDICATION)):
        raise AssertionError("GDT793 okal code prior missing")

    structural = [{
        "card_id": "G804-S01",
        "old_card": "QUALITY_VALUE_BRACKETED_L_SURFACE_WORKING_CONSTRUCTION",
        "new_card": "OUTER_FIELD_PLUS_WHOLE_SPECIFIC_MIDDLE_HEAD_PLUS_RIGHT_STATE_OR_VALUE",
        "safe_display": "left quality/condition field | whole-specific middle field | right state/value",
        "aggressive_display": "descriptive two-axis record OR prescriptive preparation record OR opaque address",
        "field_neighbour_evidence": "18/45 target cells in 72 common-mask licensed fields",
        "amount_slot_evidence": "15 preferred-side neighbours; 14 open candidates; 0 GDT760-licensed target content contacts",
        "quality_value_evidence": "41 ZL3b spans; 33 all-reader sequences; cheol obtains no specificity lead versus K12 controls",
        "selected_middle_lead": "cheol=material/preparation rival; qokol has stronger external right-value count",
        "selected_general_carrier": "ol=quantity-bearing preparation/content carrier",
        "null_rival": "opaque three-field record address",
        "confirmed_lexemes": 0,
        "component_export_credit": 0,
    }]

    lock_rows = source_lock()
    write_tsv(output_dir / "SOURCE_LOCK.tsv", lock_rows, ("path", "sha256", "purpose"))
    write_tsv(output_dir / "GDT804_72_COMMON_MASK_FIELD_ATLAS.tsv", licensed_fields, tuple(licensed_fields[0]))
    write_tsv(output_dir / "GDT804_107_COMMON_MASK_XL_EXPOSURES.tsv", exposures, tuple(exposures[0]))
    write_tsv(output_dir / "GDT804_POSITIONAL_AMOUNT_XL_SLOTS.tsv", amount_slots, tuple(amount_slots[0]))
    write_tsv(output_dir / "GDT804_30_TARGET_UNION_CELLS.tsv", union_rows, tuple(union_rows[0]))
    write_tsv(output_dir / "GDT804_11_MIDDLE_CENSUS.tsv", census, tuple(census[0]))
    write_tsv(output_dir / "GDT804_NEAREST_CONTROL_POOLS.tsv", pool_rows, tuple(pool_rows[0]))
    write_tsv(output_dir / "GDT804_5000_AGGREGATE_MATCHED_NULL.tsv", primary_rows, tuple(primary_rows[0]))
    write_tsv(output_dir / "GDT804_NULL_SUMMARY.tsv", null_summary, tuple(null_summary[0]))
    write_tsv(
        output_dir / "GDT804_GUARDED_READER_QUERY_STATS.tsv",
        reader_query_stats, tuple(reader_query_stats[0]),
    )
    write_tsv(output_dir / "GDT804_41_QUALITY_VALUE_SPANS.tsv", quality_rows, tuple(quality_rows[0]))
    write_tsv(output_dir / "GDT804_QUALITY_VALUE_SUMMARY.tsv", quality_summary, tuple(quality_summary[0]))
    write_tsv(
        output_dir / "GDT804_11_MIDDLE_RIGHT_VALUE_PROFILE.tsv",
        middle_right_profiles, tuple(middle_right_profiles[0]),
    )
    write_tsv(
        output_dir / "GDT804_CHEOL_K12_RIGHT_VALUE_CONTROL.tsv",
        cheol_controls, tuple(cheol_controls[0]),
    )
    edge_packet_path = output_dir / "GDT804_GDT388_QUALITY_VALUE_EDGE_PACKET.tsv"
    write_tsv(edge_packet_path, edge_rows, EDGE_FIELDS)
    edge_intake = run_edge_intake(
        edge_packet_path,
        output_dir / "GDT804_GDT388_EDGE_INTAKE.json",
        len(edge_rows),
    )
    write_tsv(output_dir / "GDT804_12_BRACKET_WORKING_READER.tsv", bracket_output, tuple(bracket_output[0]))
    write_tsv(output_dir / "GDT804_MIDDLE_ROLE_ADJUDICATION.tsv", adjudication, tuple(adjudication[0]))
    write_tsv(output_dir / "GDT804_STRUCTURAL_CARD.tsv", structural, tuple(structural[0]))

    primary_by_metric = {row["metric"]: row for row in null_summary if row["null_variant"] == "PRIMARY_AGGREGATE_MATCHED_200000_KEEP5000"}
    result: dict[str, Any] = {
        "experiment_id": "GDT804", "status": STATUS,
        "paired_xl_universe": len(universe), "middle_surfaces": targets,
        "brackets": len(bracket_rows),
        "gdt744_open_slot_intersection": len(target & g744_open),
        "gdt745_open_centre_intersection": len(target & g745_open),
        "common_mask_licensed_fields": len(licensed_fields),
        "common_mask_all_xl_exposures": len(exposures), "target_score": target_score,
        "primary_null": {
            "seed": PRIMARY_SEED, "draws": PRIMARY_DRAWS, "retained": PRIMARY_KEEP,
            "nearest_pool_k": PRIMARY_K,
            "field_hit_p": primary_by_metric["field_hit_cells"]["upper_tail_p_add_one"],
            "field_exposure_p": primary_by_metric["field_exposure_cells"]["upper_tail_p_add_one"],
            "field_specificity_rate_p": primary_by_metric["field_specificity_rate"]["upper_tail_p_add_one"],
            "open_positioned_amount_neighbour_p": primary_by_metric["open_positioned_amount_neighbour_cells"]["upper_tail_p_add_one"],
            "field_or_open_positioned_neighbour_union_p": primary_by_metric["field_or_open_positioned_neighbour_union_cells"]["upper_tail_p_add_one"],
            "field_and_open_positioned_neighbour_form_p": primary_by_metric["field_and_open_positioned_neighbour_form_breadth"]["upper_tail_p_add_one"],
            "gdt760_clean_content_contact_p": primary_by_metric["gdt760_clean_content_contact_cells"]["upper_tail_p_add_one"],
        },
        "quality_value_spans": len(quality_rows),
        "quality_value_token_stable_spans": sum(
            int(row["both_tokens_stable_all_three"]) for row in quality_rows
        ),
        "quality_value_all_three_sequence_spans": sum(
            int(row["contiguous_sequence_present_all_three"]) for row in quality_rows
        ),
        "quality_value_pages": len({row["page"] for row in quality_rows}),
        "quality_value_physical_folios": len({row["physical_folio"] for row in edge_rows}),
        "quality_value_types": {
            f"{row['head_surface']} {row['value_surface']}": {
                "zl3b": int(row["zl3b_contiguous_spans"]),
                "token_stable": int(row["both_token_stable_spans"]),
                "all_three_sequence": int(row["all_three_contiguous_sequence_spans"]),
                "external_all_three_sequence": int(row["external_all_three_sequence_spans"]),
            }
            for row in quality_summary
        },
        "cheol_reader_stable_right_value": middle_right_by_surface["cheol"],
        "qokol_reader_stable_right_value": middle_right_by_surface["qokol"],
        "ol_reader_stable_right_value": middle_right_by_surface["ol"],
        "cheol_k12_zl3b_controls_at_least_count": 7,
        "cheol_k12_zl3b_controls_at_least_rate": 7,
        "cheol_k12_zl3b_controls_at_least_count_and_rate": 5,
        "cheol_k12_reader_stable_controls_at_least_count": 8,
        "cheol_k12_reader_stable_controls_at_least_rate": 10,
        "cheol_k12_reader_stable_controls_at_least_count_and_rate": 8,
        "quality_value_edge_intake": edge_intake,
        "best_safe_reading": "qokain-Qualitätsfeld; cheol-Feld, Wert III",
        "best_aggressive_reading_de": "heiß im II. Grad; trocken im III. Grad",
        "selected_middle_model": "WHOLE_SPECIFIC_FIELD_HEAD__UNIFORM_CONTENT_SLOT_REJECTED",
        "selected_concrete_followup": "cheol_material_rival__qokol_right_value_rival__ol_general_carrier",
        "confirmed_lexemes": 0, "component_export_credit": 0,
        "new_pages_images_or_transcriptions": 0, "f84_or_f84r_rows": 0,
        "output_sha256": {},
    }
    for name in OUTPUT_NAMES:
        if name != "RESULT.json":
            result["output_sha256"][name] = sha256(output_dir / name)
    (output_dir / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ART)
    args = parser.parse_args()
    result = build(args.output_dir)
    if args.output_dir.resolve() == ART.resolve():
        write_report(
            EXP / "REPORT.md", result["target_score"],
            read_tsv(ART / "GDT804_NULL_SUMMARY.tsv"),
            read_tsv(ART / "GDT804_QUALITY_VALUE_SUMMARY.tsv"),
            read_tsv(ART / "GDT804_11_MIDDLE_CENSUS.tsv"),
            read_tsv(ART / "GDT804_11_MIDDLE_RIGHT_VALUE_PROFILE.tsv"),
            read_tsv(ART / "GDT804_CHEOL_K12_RIGHT_VALUE_CONTROL.tsv"),
        )
    print(json.dumps(result, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
