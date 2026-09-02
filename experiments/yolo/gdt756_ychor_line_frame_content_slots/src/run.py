#!/usr/bin/env python3
"""Test ychor as a continuation formula and render all thirteen line bodies."""

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
BASE_REL = Path("experiments/yolo/gdt756_ychor_line_frame_content_slots")
EXP = ROOT / BASE_REL
SRC = EXP / "src"
DEFAULT_ARTIFACTS = EXP / "artifacts"
G755_RUN_REL = Path(
    "experiments/yolo/gdt755_top24_historical_register_crosswalk/src/run.py"
)
G755_OCC_REL = Path(
    "experiments/yolo/gdt755_top24_historical_register_crosswalk/"
    "artifacts/TOP24_448_OCCURRENCE_FIELDS.tsv"
)
G755_GLOSS_REL = Path(
    "experiments/yolo/gdt755_top24_historical_register_crosswalk/"
    "artifacts/TOP24_WORKING_GLOSS_UPDATE.tsv"
)
G755_POSITION_REL = Path(
    "experiments/yolo/gdt755_top24_historical_register_crosswalk/"
    "artifacts/EXACT_FORM_INITIAL_POSITION_COMPARATOR.tsv"
)
G754_INVENTORY_REL = Path(
    "experiments/yolo/gdt754_active_productive_compound_provenance_sieve/"
    "artifacts/ACTIVE_172_PRODUCTIVE_COMPOUND_INVENTORY.tsv"
)
OUTPUT_NAMES = (
    "YCHOR_13_LINE_ATLAS.tsv",
    "YCHOR_71_BODY_TOKEN_CANDIDATES.tsv",
    "YCHOR_53_BODY_WHOLE_CANDIDATES.tsv",
    "YCHOR_247_MATCHED_CONTINUATION_CONTROLS.tsv",
    "YCHOR_FRAME_FEATURE_COMPARISON.tsv",
    "LINE_INITIAL_RECIPE_TRIAD_RANKING.tsv",
    "YCHOR_FORMULA_CANDIDATE_RANKING.tsv",
    "GDT756_YCHOR_FRAME_READER.md",
    "RESULT.json",
)
CONTENT_AXES = {
    "MATERIAL", "PREPARATION", "PLANT_PART", "ROOT", "LEAF", "SEED",
    "WOOD", "POWDER", "LIQUID", "WATER", "WINE", "OIL", "SALT",
    "INGREDIENT", "HONEY", "VESSEL", "PERSON", "DISEASE", "TREATMENT",
}
AMOUNT_AXES = {"AMOUNT", "PART", "LEVEL_I", "LEVEL_II", "LEVEL_III"}
PROCESS_AXES = {"PROCESS", "PASS", "CLOSE", "BATH"}
QUALITY_AXES = {
    "HOT", "COLD", "DRY", "MOIST", "BEGIN_STAGE", "MIDDLE_STAGE",
    "END_STAGE",
}
FEATURES = (
    ("CONTENT", CONTENT_AXES),
    ("AMOUNT_OR_LEVEL", AMOUNT_AXES),
    ("PROCESS", PROCESS_AXES),
    ("QUALITY_OR_STAGE", QUALITY_AXES),
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


g755 = load_module("gdt755_builder_for_gdt756", ROOT / G755_RUN_REL)


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


def joined(items: Iterable[str]) -> str:
    chosen = set(items)
    ordered = [axis for axis in g755.AXIS_ORDER if axis in chosen]
    ordered.extend(sorted(chosen - set(ordered)))
    return "|".join(ordered) or "NONE"


def count_text(items: Iterable[str]) -> str:
    counts = Counter(items)
    return "|".join(f"{item}:{counts[item]}" for item in sorted(counts)) or "NONE"


def paragraph_line_indices(
    context: object, line_meta: dict[str, dict[str, str]]
) -> dict[str, int]:
    by_page: defaultdict[str, list[str]] = defaultdict(list)
    for locus, line in context.by_line.items():
        by_page[str(line[0]["page"])].append(locus)
    output: dict[str, int] = {}
    for loci in by_page.values():
        loci.sort(key=lambda locus: int(line_meta[locus]["line_number"]))
        index = 0
        for locus in loci:
            index = 1 if line_meta[locus]["paragraph_start"] == "1" else index + 1
            output[locus] = index
    return output


def body_features(
    context: object,
    locus: str,
    suspect_surfaces: set[str],
) -> dict[str, object]:
    line = context.by_line[locus]
    axes_by_token: list[set[str]] = []
    exact_body = 0
    excluded = 0
    for ordinal, token in enumerate(line[1:], start=2):
        exact = bool(context.exact[(locus, int(token["token_index"]))])
        exact_body += int(exact)
        _token, _cell, raw_axes = g755.g753.g752.clean_cell(
            context, locus, ordinal
        )
        if not exact or token["eva"] in suspect_surfaces:
            excluded += int(exact and token["eva"] in suspect_surfaces and bool(raw_axes))
            axes_by_token.append(set())
        else:
            axes_by_token.append(set(raw_axes))
    axes = set().union(*axes_by_token) if axes_by_token else set()
    feature_values = {
        name: int(bool(axes & family)) for name, family in FEATURES
    }
    recipe_triad = int(
        feature_values["CONTENT"]
        and feature_values["AMOUNT_OR_LEVEL"]
        and feature_values["PROCESS"]
    )
    return {
        "body_token_count": len(line) - 1,
        "reader_exact_body_tokens": exact_body,
        "independent_axis_body_tokens": sum(bool(value) for value in axes_by_token),
        "independent_body_axes": axes,
        "content_present": feature_values["CONTENT"],
        "amount_or_level_present": feature_values["AMOUNT_OR_LEVEL"],
        "process_present": feature_values["PROCESS"],
        "quality_or_stage_present": feature_values["QUALITY_OR_STAGE"],
        "recipe_content_amount_process_triad": recipe_triad,
        "suspect_axis_tokens_excluded": excluded,
    }


def global_surface_stats(context: object) -> dict[str, dict[str, object]]:
    grouped: defaultdict[str, list[tuple[int, int, str]]] = defaultdict(list)
    for locus, line in context.by_line.items():
        for ordinal, token in enumerate(line, start=1):
            if not context.exact[(locus, int(token["token_index"]))]:
                continue
            grouped[str(token["eva"])].append((
                int(ordinal == 1), int(ordinal == len(line)), str(token["section"])
            ))
    output: dict[str, dict[str, object]] = {}
    for surface, rows in grouped.items():
        output[surface] = {
            "global_reader_exact_occurrences": len(rows),
            "global_reader_exact_line_initial": sum(row[0] for row in rows),
            "global_reader_exact_line_final": sum(row[1] for row in rows),
            "global_section_counts": count_text(row[2] for row in rows),
            "global_herbal_occurrences": sum(row[2] == "H" for row in rows),
        }
    return output


def build_body_tokens(
    context: object,
    ychor_loci: list[str],
    priors: dict[str, dict[str, str]],
    g755_glosses: dict[str, dict[str, str]],
    suspect_surfaces: set[str],
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    number = 0
    for locus in ychor_loci:
        line = context.by_line[locus]
        for ordinal, token in enumerate(line[1:], start=2):
            number += 1
            surface = str(token["eva"])
            prior = priors[surface]
            _token, cell, raw_axes = g755.g753.g752.clean_cell(
                context, locus, ordinal
            )
            exact = int(context.exact[(locus, int(token["token_index"]))])
            suspect = int(surface in suspect_surfaces)
            independent_axes = set(raw_axes) if exact and not suspect else set()
            g755_row = g755_glosses.get(surface)
            selected_candidate = (
                str(g755_row["gdt755_working_candidate_de"])
                if g755_row is not None else prior["working_candidate_de"]
            )
            selected_confidence = (
                str(g755_row["working_confidence"])
                if g755_row is not None else prior["confidence"]
            )
            output.append({
                "gdt756_body_token_id": f"G756-B{number:03d}",
                "page": token["page"],
                "locus": locus,
                "token_ordinal": ordinal,
                "body_offset_after_ychor": ordinal - 1,
                "line_token_count": len(line),
                "line_position": g755.line_position(ordinal, len(line)),
                "surface": surface,
                "reader_exact": exact,
                "gdt754_suspect_surface": suspect,
                "independent_axes_at_position": joined(independent_axes),
                "raw_axes_not_counted_when_variant_or_suspect": joined(raw_axes),
                "active_cache_value_background": cell["v99r7_semantic_value_de"],
                "active_cache_confidence_background": cell["gdt734_confidence_level"],
                "working_candidate_de": selected_candidate,
                "alternate_1_de": prior["alternate_1_de"],
                "alternate_2_de": prior["alternate_2_de"],
                "working_confidence": selected_confidence,
                "semantic_role": prior["semantic_role"],
                "selection_basis": prior["selection_basis"],
                "candidate_source": "GDT755_TOP24" if g755_row else "GDT756_BODY_PRIOR",
                "candidate_not_plaintext": 1,
                "literal_identity": "OPEN",
                "confirmed_lexeme": 0,
                "component_export_credit": 0,
            })
    return output


def build_line_atlas(
    context: object,
    line_meta: dict[str, dict[str, str]],
    ychor_rows: dict[str, dict[str, str]],
    ychor_loci: list[str],
    body_tokens: list[dict[str, object]],
    paragraph_indices: dict[str, int],
    suspect_surfaces: set[str],
) -> list[dict[str, object]]:
    by_locus: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for row in body_tokens:
        by_locus[str(row["locus"])].append(row)
    output: list[dict[str, object]] = []
    for locus in ychor_loci:
        line = context.by_line[locus]
        rows = sorted(by_locus[locus], key=lambda row: int(row["token_ordinal"]))
        features = body_features(context, locus, suspect_surfaces)
        candidates = [str(row["working_candidate_de"]) for row in rows]
        item_render = "ferner: " + "; ".join(candidates)
        take_render = "nimm: " + "; ".join(candidates)
        item_take_render = "ferner, nimm: " + "; ".join(candidates)
        source = ychor_rows[locus]
        output.append({
            "page": line[0]["page"],
            "locus": locus,
            "section": line[0]["section"],
            "language": line[0]["language"],
            "hand": line[0]["hand"],
            "paragraph_line_index": paragraph_indices[locus],
            "paragraph_start": line_meta[locus]["paragraph_start"],
            "paragraph_end": line_meta[locus]["paragraph_end"],
            "line_token_count": len(line),
            "written_line_eva": " ".join(str(token["eva"]) for token in line),
            "immediate_follower_surface": rows[0]["surface"],
            "immediate_follower_candidate_de": rows[0]["working_candidate_de"],
            "line_final_surface": rows[-1]["surface"],
            "line_final_candidate_de": rows[-1]["working_candidate_de"],
            "gdt755_external_field_channel": source["field_channel"],
            "gdt755_external_field_complete": source["boundary_complete"],
            "independent_body_axes": joined(features["independent_body_axes"]),
            "body_token_count": features["body_token_count"],
            "reader_exact_body_tokens": features["reader_exact_body_tokens"],
            "independent_axis_body_tokens": features["independent_axis_body_tokens"],
            "content_present": features["content_present"],
            "amount_or_level_present": features["amount_or_level_present"],
            "process_present": features["process_present"],
            "quality_or_stage_present": features["quality_or_stage_present"],
            "recipe_content_amount_process_triad": features["recipe_content_amount_process_triad"],
            "suspect_axis_tokens_excluded": features["suspect_axis_tokens_excluded"],
            "selected_item_marker_render_de": item_render,
            "recipe_command_rival_render_de": take_render,
            "item_plus_command_rival_render_de": item_take_render,
            "all_written_tokens_have_candidate_default": 1,
            "candidate_line_not_plaintext": 1,
            "confirmed_lexeme": 0,
        })
    return output


def build_controls(
    context: object,
    line_meta: dict[str, dict[str, str]],
    ychor_loci: list[str],
    suspect_surfaces: set[str],
) -> list[dict[str, object]]:
    ordered = list(context.by_line)
    order_index = {locus: index for index, locus in enumerate(ordered)}
    eligible = [
        locus for locus in ordered
        if context.by_line[locus]
        and context.exact[(
            locus, int(context.by_line[locus][0]["token_index"])
        )]
    ]
    output: list[dict[str, object]] = []
    number = 0
    for target_locus in ychor_loci:
        target = context.by_line[target_locus]
        target_head = target[0]
        pool: list[tuple[int, int, str]] = []
        for locus in eligible:
            line = context.by_line[locus]
            head = line[0]
            if head["eva"] == "ychor":
                continue
            if (
                head["section"] == target_head["section"]
                and head["language"] == target_head["language"]
                and head["hand"] == target_head["hand"]
                and line_meta[locus]["paragraph_start"] == "0"
                and abs(len(line) - len(target)) <= 1
            ):
                pool.append((
                    abs(order_index[locus] - order_index[target_locus]),
                    abs(len(line) - len(target)), locus,
                ))
        for distance, length_delta, locus in sorted(pool)[:20]:
            number += 1
            line = context.by_line[locus]
            features = body_features(context, locus, suspect_surfaces)
            output.append({
                "gdt756_control_id": f"G756-C{number:03d}",
                "target_ychor_locus": target_locus,
                "control_page": line[0]["page"],
                "control_locus": locus,
                "control_initial_surface": line[0]["eva"],
                "same_section_language_hand": 1,
                "both_paragraph_continuations": 1,
                "line_length_delta": length_delta,
                "global_line_order_distance": distance,
                "control_line_token_count": len(line),
                "control_written_line_eva": " ".join(
                    str(token["eva"]) for token in line
                ),
                "independent_body_axes": joined(features["independent_body_axes"]),
                "body_token_count": features["body_token_count"],
                "reader_exact_body_tokens": features["reader_exact_body_tokens"],
                "independent_axis_body_tokens": features["independent_axis_body_tokens"],
                "content_present": features["content_present"],
                "amount_or_level_present": features["amount_or_level_present"],
                "process_present": features["process_present"],
                "quality_or_stage_present": features["quality_or_stage_present"],
                "recipe_content_amount_process_triad": features["recipe_content_amount_process_triad"],
                "suspect_axis_tokens_excluded": features["suspect_axis_tokens_excluded"],
                "comparison_uses_initial_surface_meaning": 0,
                "confirmed_lexeme": 0,
            })
    return output


def feature_comparison(
    lines: list[dict[str, object]], controls: list[dict[str, object]]
) -> list[dict[str, object]]:
    specs = (
        ("CONTENT_PRESENT", "content_present"),
        ("AMOUNT_OR_LEVEL_PRESENT", "amount_or_level_present"),
        ("PROCESS_PRESENT", "process_present"),
        ("QUALITY_OR_STAGE_PRESENT", "quality_or_stage_present"),
        ("CONTENT_AMOUNT_PROCESS_TRIAD", "recipe_content_amount_process_triad"),
    )
    output: list[dict[str, object]] = []
    for feature, field in specs:
        target_hits = sum(int(row[field]) for row in lines)
        control_hits = sum(int(row[field]) for row in controls)
        target_rate = target_hits / len(lines)
        control_rate = control_hits / len(controls)
        output.append({
            "feature": feature,
            "ychor_line_hits": target_hits,
            "ychor_lines": len(lines),
            "ychor_rate": f"{target_rate:.6f}",
            "matched_control_hits": control_hits,
            "matched_control_rows": len(controls),
            "matched_control_rate": f"{control_rate:.6f}",
            "descriptive_rate_ratio": (
                f"{target_rate / control_rate:.6f}" if control_rate else "INF"
            ),
            "interpretation": (
                "Recipe-like complete role triad is enriched after ychor."
                if feature == "CONTENT_AMOUNT_PROCESS_TRIAD" else
                "Component diagnostic; not a lexical identification."
            ),
            "initial_surface_semantics_used": 0,
            "confirmed_lexeme": 0,
        })
    return output


def initial_triad_ranking(
    context: object,
    suspect_surfaces: set[str],
) -> list[dict[str, object]]:
    global_stats = global_surface_stats(context)
    grouped: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for locus, line in context.by_line.items():
        if not line or not context.exact[(locus, int(line[0]["token_index"]))]:
            continue
        grouped[str(line[0]["eva"])].append(
            body_features(context, locus, suspect_surfaces)
        )
    eligible = [(surface, rows) for surface, rows in grouped.items() if len(rows) >= 5]
    eligible.sort(key=lambda item: (
        -sum(int(row["recipe_content_amount_process_triad"]) for row in item[1]) / len(item[1]),
        -sum(int(row["recipe_content_amount_process_triad"]) for row in item[1]),
        -len(item[1]), item[0],
    ))
    output: list[dict[str, object]] = []
    for rank, (surface, rows) in enumerate(eligible, start=1):
        stats = global_stats[surface]
        triad_hits = sum(
            int(row["recipe_content_amount_process_triad"]) for row in rows
        )
        output.append({
            "recipe_triad_rate_rank": rank,
            "initial_surface": surface,
            "reader_exact_initial_lines": len(rows),
            "recipe_triad_lines": triad_hits,
            "recipe_triad_rate": f"{triad_hits / len(rows):.6f}",
            "content_lines": sum(int(row["content_present"]) for row in rows),
            "amount_or_level_lines": sum(int(row["amount_or_level_present"]) for row in rows),
            "process_lines": sum(int(row["process_present"]) for row in rows),
            "quality_or_stage_lines": sum(int(row["quality_or_stage_present"]) for row in rows),
            "global_reader_exact_occurrences": stats["global_reader_exact_occurrences"],
            "global_reader_exact_line_initial": stats["global_reader_exact_line_initial"],
            "global_line_initial_purity": f"{int(stats['global_reader_exact_line_initial']) / int(stats['global_reader_exact_occurrences']):.6f}",
            "comparison_uses_initial_surface_meaning": 0,
            "body_axes_exclude_gdt754_suspect_surfaces": 1,
            "confirmed_lexeme": 0,
        })
    return output


def build_whole_candidates(
    body_tokens: list[dict[str, object]],
    priors: dict[str, dict[str, str]],
    global_stats: dict[str, dict[str, object]],
    g755_glosses: dict[str, dict[str, str]],
) -> list[dict[str, object]]:
    grouped: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for row in body_tokens:
        grouped[str(row["surface"])].append(row)
    output: list[dict[str, object]] = []
    for surface in sorted(grouped, key=lambda value: (-len(grouped[value]), value)):
        rows = grouped[surface]
        prior = priors[surface]
        stats = global_stats.get(surface, {
            "global_reader_exact_occurrences": 0,
            "global_reader_exact_line_initial": 0,
            "global_reader_exact_line_final": 0,
            "global_section_counts": "NONE",
            "global_herbal_occurrences": 0,
        })
        exact_count = sum(int(row["reader_exact"]) for row in rows)
        global_count = int(stats["global_reader_exact_occurrences"])
        output.append({
            "surface": surface,
            "ychor_body_occurrences": len(rows),
            "ychor_body_reader_exact_occurrences": exact_count,
            "ychor_immediate_follower_occurrences": sum(int(row["body_offset_after_ychor"]) == 1 for row in rows),
            "ychor_line_final_occurrences": sum(row["line_position"] in {"LAST", "SINGLE"} for row in rows),
            "ychor_pages": len({str(row["page"]) for row in rows}),
            "ychor_independent_axis_profiles": count_text(str(row["independent_axes_at_position"]) for row in rows),
            "global_reader_exact_occurrences": global_count,
            "global_reader_exact_line_initial": stats["global_reader_exact_line_initial"],
            "global_reader_exact_line_final": stats["global_reader_exact_line_final"],
            "global_section_counts": stats["global_section_counts"],
            "global_herbal_share": f"{int(stats['global_herbal_occurrences']) / global_count:.6f}" if global_count else "0.000000",
            "working_candidate_de": rows[0]["working_candidate_de"],
            "alternate_1_de": prior["alternate_1_de"],
            "alternate_2_de": prior["alternate_2_de"],
            "working_confidence": rows[0]["working_confidence"],
            "semantic_role": prior["semantic_role"],
            "selection_basis": prior["selection_basis"],
            "candidate_source": "GDT755_TOP24" if surface in g755_glosses else "GDT756_BODY_PRIOR",
            "eva_spelling_used_to_select_candidate": 0,
            "literal_identity": "OPEN",
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    return output


def formula_ranking(
    formula_priors: list[dict[str, str]],
    historical_sources: dict[str, dict[str, str]],
    lines: list[dict[str, object]],
    frame_comparison: list[dict[str, object]],
) -> list[dict[str, object]]:
    triad = next(
        row for row in frame_comparison
        if row["feature"] == "CONTENT_AMOUNT_PROCESS_TRIAD"
    )
    all_initial = int(all(row["written_line_eva"].startswith("ychor ") for row in lines))
    all_continuations = int(all(row["paragraph_start"] == "0" for row in lines))
    cross_section = int(len({str(row["section"]) for row in lines}) >= 4)
    one_whole_points = {"YF001": 12, "YF002": 12, "YF003": 4, "YF004": 12}
    penalties = {"YF001": 0, "YF002": 0, "YF003": 12, "YF004": 10}
    output: list[dict[str, object]] = []
    for prior in formula_priors:
        candidate_id = prior["candidate_id"]
        local_source_ids = [
            item for item in prior["source_ids"].split("|")
            if item in historical_sources
        ]
        historical_points = min(18, 6 * len(prior["source_ids"].split("|")))
        initial_points = 20 if all_initial and prior["expected_line_initial"] == "1" else 0
        continuation_points = (
            20 if all_continuations and prior["expected_paragraph_continuation"] == "1"
            else 4 if all_continuations else 0
        )
        triad_points = (
            18 if prior["expected_recipe_triad"] == "1" and float(triad["descriptive_rate_ratio"]) > 1
            else 6
        )
        section_points = 8 if cross_section else 0
        score = (
            initial_points + continuation_points + triad_points
            + historical_points + section_points + one_whole_points[candidate_id]
            - penalties[candidate_id]
        )
        output.append({
            "candidate_id": candidate_id,
            "historical_expression": prior["historical_expression"],
            "working_candidate_de": prior["working_candidate_de"],
            "register_role": prior["register_role"],
            "line_initial_fit_points": initial_points,
            "paragraph_continuation_fit_points": continuation_points,
            "recipe_triad_fit_points": triad_points,
            "historical_attestation_points": historical_points,
            "cross_section_fit_points": section_points,
            "single_whole_fit_points": one_whole_points[candidate_id],
            "specificity_penalty": penalties[candidate_id],
            "fit_score_0_100_diagnostic": score,
            "source_ids": prior["source_ids"],
            "local_historical_source_count": len(local_source_ids),
            "selection_note": prior["selection_note"],
            "counterevidence": prior["counterevidence"],
            "reader_exact_occurrences": len(lines),
            "line_initial_occurrences": len(lines),
            "paragraph_initial_occurrences": sum(int(row["paragraph_start"]) for row in lines),
            "recipe_triad_lines": triad["ychor_line_hits"],
            "matched_recipe_triad_controls": triad["matched_control_hits"],
            "historical_graphic_match_claimed": 0,
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    output.sort(key=lambda row: (-int(row["fit_score_0_100_diagnostic"]), str(row["candidate_id"])))
    for rank, row in enumerate(output, start=1):
        row["candidate_rank"] = rank
        row["selected_primary"] = int(rank == 1)
        row["working_confidence_if_primary"] = "C2_STRONG_EXPLORATORY" if rank == 1 else "ALTERNATE_NOT_SELECTED"
    fields = ["candidate_rank", "selected_primary", *[key for key in output[0] if key not in {"candidate_rank", "selected_primary"}]]
    return [{field: row[field] for field in fields} for row in output]


def write_reader(
    path: Path,
    lines: list[dict[str, object]],
    formulae: list[dict[str, object]],
    comparison: list[dict[str, object]],
    whole_candidates: list[dict[str, object]],
    controls: list[dict[str, object]],
    initial_ranking: list[dict[str, object]],
) -> None:
    ychor_rank = next(
        row for row in initial_ranking if row["initial_surface"] == "ychor"
    )
    immediate = [
        row for row in whole_candidates
        if int(row["ychor_immediate_follower_occurrences"])
    ]
    text = [
        "# GDT756 ychor line-frame reader", "",
        "## Working result", "",
        "The best current whole-form reading is **`ychor = ferner / ebenso`**, comparable to the medieval recipe marker `Item`. The prior `nimm` reading remains the main rival, and `ferner: nimm` remains a third live possibility. This is a candidate ranking, not a deciphered Latin spelling.", "",
        f"All 13 exact occurrences start a line and none starts a coded paragraph. The bodies contain content+amount+process together in 4/13 lines, against 22/{len(controls)} locally matched continuation controls. Among {len(initial_ranking)} initial forms with at least five initial lines, ychor ranks {ychor_rank['recipe_triad_rate_rank']} by this body-triad rate.", "",
        "## Formula candidates", "",
        "| rank | complete-form candidate | working German | score | decisive fit |",
        "|---:|---|---|---:|---|",
    ]
    for row in formulae:
        text.append(
            f"| {row['candidate_rank']} | `{row['historical_expression']}` | {row['working_candidate_de']} | {row['fit_score_0_100_diagnostic']} | {row['selection_note']} |"
        )
    text.extend([
        "", "## Frame comparison", "",
        "| body feature | ychor lines | matched continuation controls | rate ratio |",
        "|---|---:|---:|---:|",
    ])
    for row in comparison:
        text.append(
            f"| {row['feature']} | {row['ychor_line_hits']}/{row['ychor_lines']} | {row['matched_control_hits']}/{row['matched_control_rows']} | {row['descriptive_rate_ratio']} |"
        )
    text.extend([
        "", "The controls match section, Currier language, hand, continuation status, local corpus neighbourhood and line length within one token. Their repeated use is intentional matched weighting; 247 control rows represent 236 distinct lines.", "",
        "## Direct followers after ychor", "",
        "| whole | occurrences | candidate | rivals | confidence |",
        "|---|---:|---|---|---|",
    ])
    for row in sorted(immediate, key=lambda item: (-int(item["ychor_immediate_follower_occurrences"]), str(item["surface"]))):
        text.append(
            f"| `{row['surface']}` | {row['ychor_immediate_follower_occurrences']} | {row['working_candidate_de']} | {row['alternate_1_de']} / {row['alternate_2_de']} | `{row['working_confidence']}` |"
        )
    text.extend([
        "", "## All thirteen fully candidate-filled lines", "",
        "Every written token has a default here. Semicolons deliberately expose a compact register/list reading rather than pretending that German prose order is known.", "",
    ])
    for row in lines:
        text.extend([
            f"### {row['locus']}", "",
            f"EVA: `{row['written_line_eva']}`", "",
            f"Primary (`Item`): {row['selected_item_marker_render_de']}", "",
            f"Command rival (`Recipe`): {row['recipe_command_rival_render_de']}", "",
        ])
    text.extend([
        "## Interpretation boundary", "",
        f"The body deck covers all 71 post-ychor token positions with 53 complete-form defaults. Six weak or formerly unread forms receive explicit C0 context candidates instead of question marks. Concrete words such as Blätter, Wurzel, Samen, Wein, Holz and Pulver are hypotheses chosen for a slot and accompanied by rivals; they are not inferred from EVA initials or substrings.", "",
        "The practical gain is a testable recipe/list frame: continuation marker, content or operation, then optional quality, quantity and process material. The result identifies no plaintext sentence, language, sound or confirmed lexeme.",
    ])
    path.write_text("\n".join(text).rstrip() + "\n", encoding="utf-8")


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    context, line_meta, guard = g755.g753.g752.g751.load_context()
    g755_occurrences = read_tsv(ROOT / G755_OCC_REL)
    g755_gloss_rows = read_tsv(ROOT / G755_GLOSS_REL)
    g755_positions = read_tsv(ROOT / G755_POSITION_REL)
    inventory = read_tsv(ROOT / G754_INVENTORY_REL)
    historical_rows = read_tsv(SRC / "HISTORICAL_ITEM_COMPARATORS.tsv")
    formula_priors = read_tsv(SRC / "YCHOR_FORMULA_PRIORS.tsv")
    body_prior_rows = read_tsv(SRC / "YCHOR_BODY_CANDIDATE_PRIORS.tsv")
    historical_sources = {row["source_id"]: row for row in historical_rows}
    body_priors = {row["surface"]: row for row in body_prior_rows}
    g755_glosses = {row["surface"]: row for row in g755_gloss_rows}
    suspect_surfaces = {row["surface"] for row in inventory}
    ychor_occurrences = [row for row in g755_occurrences if row["surface"] == "ychor"]
    ychor_rows = {row["locus"]: row for row in ychor_occurrences}
    ychor_loci = [
        locus for locus, line in context.by_line.items()
        if line and line[0]["eva"] == "ychor"
        and context.exact[(locus, int(line[0]["token_index"]))]
    ]

    if len(ychor_loci) != 13 or set(ychor_loci) != set(ychor_rows):
        raise AssertionError("GDT755 ychor universe changed")
    if len(body_prior_rows) != len(body_priors):
        raise AssertionError("duplicate ychor body candidate prior")
    body_surfaces = {
        str(token["eva"])
        for locus in ychor_loci for token in context.by_line[locus][1:]
    }
    if body_surfaces != set(body_priors):
        raise AssertionError(
            f"body prior mismatch missing={sorted(body_surfaces-set(body_priors))} "
            f"extra={sorted(set(body_priors)-body_surfaces)}"
        )
    if len(historical_sources) != 3 or len(formula_priors) != 4:
        raise AssertionError("historical formula comparator inventory changed")

    paragraph_indices = paragraph_line_indices(context, line_meta)
    body_tokens = build_body_tokens(
        context, ychor_loci, body_priors, g755_glosses, suspect_surfaces
    )
    lines = build_line_atlas(
        context, line_meta, ychor_rows, ychor_loci, body_tokens,
        paragraph_indices, suspect_surfaces,
    )
    controls = build_controls(context, line_meta, ychor_loci, suspect_surfaces)
    comparison = feature_comparison(lines, controls)
    initial_ranking = initial_triad_ranking(context, suspect_surfaces)
    global_stats = global_surface_stats(context)
    whole_candidates = build_whole_candidates(
        body_tokens, body_priors, global_stats, g755_glosses
    )
    formulae = formula_ranking(
        formula_priors, historical_sources, lines, comparison
    )

    ychor_position = next(row for row in g755_positions if row["surface"] == "ychor")
    ychor_triad = next(
        row for row in comparison
        if row["feature"] == "CONTENT_AMOUNT_PROCESS_TRIAD"
    )
    ychor_initial_rank = next(
        row for row in initial_ranking if row["initial_surface"] == "ychor"
    )
    if len(body_tokens) != 71 or len(whole_candidates) != 53:
        raise AssertionError("fixed ychor body universe changed")
    if len(controls) != 247 or len({row["control_locus"] for row in controls}) != 236:
        raise AssertionError("matched control universe changed")
    if len(initial_ranking) != 113 or int(ychor_initial_rank["recipe_triad_rate_rank"]) != 4:
        raise AssertionError("initial-frame comparator changed")
    if (
        ychor_triad["ychor_line_hits"] != 4
        or ychor_triad["matched_control_hits"] != 22
        or ychor_position["line_first_occurrences"] != "13"
        or ychor_position["paragraph_first_occurrences"] != "0"
    ):
        raise AssertionError("ychor fixed placement or frame result changed")
    if formulae[0]["candidate_id"] != "YF001" or formulae[0]["fit_score_0_100_diagnostic"] != 96:
        raise AssertionError("Item candidate no longer leads")
    if not all(int(row["all_written_tokens_have_candidate_default"]) for row in lines):
        raise AssertionError("candidate renderer has a missing token")

    write_tsv(output_dir / OUTPUT_NAMES[0], lines, list(lines[0]))
    write_tsv(output_dir / OUTPUT_NAMES[1], body_tokens, list(body_tokens[0]))
    write_tsv(
        output_dir / OUTPUT_NAMES[2], whole_candidates,
        list(whole_candidates[0]),
    )
    write_tsv(output_dir / OUTPUT_NAMES[3], controls, list(controls[0]))
    write_tsv(output_dir / OUTPUT_NAMES[4], comparison, list(comparison[0]))
    write_tsv(
        output_dir / OUTPUT_NAMES[5], initial_ranking,
        list(initial_ranking[0]),
    )
    write_tsv(output_dir / OUTPUT_NAMES[6], formulae, list(formulae[0]))
    write_reader(
        output_dir / OUTPUT_NAMES[7], lines, formulae, comparison,
        whole_candidates, controls, initial_ranking,
    )

    confidence = Counter(row["working_confidence"] for row in whole_candidates)
    status = (
        "PARTIAL__YCHOR_ITEM_LEAD__13_OF13_LINE_INITIAL_0_OF13_PARAGRAPH_INITIAL__"
        "4_OF13_RECIPE_TRIADS_VS22_OF247_MATCHED__RANK4_OF113_INITIAL_FRAME_FORMS__"
        "71_OF71_BODY_TOKENS_CANDIDATE_RENDERED__53_BODY_WHOLES__"
        "ZERO_CONFIRMED_LEXEMES__NO_NEW_PAGE"
    )
    result = {
        "schema": "GDT756_RESULT_V1",
        "status": status,
        "scope": {
            "ychor_exact_occurrences": len(lines),
            "ychor_pages": len({str(row["page"]) for row in lines}),
            "ychor_sections": len({str(row["section"]) for row in lines}),
            "post_ychor_body_tokens": len(body_tokens),
            "post_ychor_unique_body_wholes": len(whole_candidates),
            "body_tokens_with_candidate_default": len(body_tokens),
            "historical_item_sources": len(historical_sources),
            "formula_candidates": len(formulae),
            "matched_control_rows": len(controls),
            "matched_control_unique_lines": len({str(row["control_locus"]) for row in controls}),
            "initial_surface_groups_min5": len(initial_ranking),
        },
        "primary_formula_candidate": {
            "surface": "ychor",
            "historical_expression": "Item",
            "working_candidate_de": "ferner / ebenso",
            "confidence": "C2_STRONG_EXPLORATORY",
            "fit_score_0_100_diagnostic": 96,
            "reader_exact_occurrences": 13,
            "line_initial_occurrences": 13,
            "paragraph_initial_occurrences": 0,
            "paragraph_final_occurrences": sum(int(row["paragraph_end"]) for row in lines),
            "sections": count_text(str(row["section"]) for row in lines),
            "previous_primary_retained_as_rival": "Recipe / Accipe = nimm",
        },
        "frame_result": {
            "ychor_content_amount_process_triad_lines": 4,
            "ychor_total_lines": 13,
            "matched_control_triad_rows": 22,
            "matched_control_rows": 247,
            "descriptive_rate_ratio": ychor_triad["descriptive_rate_ratio"],
            "ychor_triad_rank_among_initial_forms_min5": int(ychor_initial_rank["recipe_triad_rate_rank"]),
            "initial_form_groups": len(initial_ranking),
        },
        "body_candidate_confidence_counts": dict(sorted(confidence.items())),
        "independence_controls": {
            "ychor_meaning_used_to_classify_body": 0,
            "gdt754_suspect_surfaces_excluded_from_independent_body_axes": len(suspect_surfaces),
            "eva_spelling_used_to_select_historical_word": 0,
            "all_concrete_body_defaults_have_two_rivals": True,
        },
        "guard": guard,
        "claim_boundary": {
            "confirmed_lexemes": 0,
            "plaintext_lines": 0,
            "confirmed_literal_content_words": 0,
            "component_export_credit": 0,
            "new_pages": 0,
            "f84_accessed": False,
            "f84r_accessed": False,
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
        "status": result["status"],
        "scope": result["scope"],
        "primary": result["primary_formula_candidate"],
        "frame": result["frame_result"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
