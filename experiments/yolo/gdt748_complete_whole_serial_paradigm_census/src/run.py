#!/usr/bin/env python3
"""Enumerate complete-whole serial paradigms with exactly one open slot."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import re
import subprocess
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
BASE_REL = Path("experiments/yolo/gdt748_complete_whole_serial_paradigm_census")
EXP = ROOT / BASE_REL
DEFAULT_ARTIFACTS = EXP / "artifacts"
G747_RUN_REL = Path(
    "experiments/yolo/gdt747_supported_whole_passage_application/src/run.py"
)
G743_PATCH_REL = Path(
    "experiments/yolo/gdt743_r2_run_intersection_adjudication/artifacts/"
    "TARGET_202_RENDERER_PATCH_V5.tsv"
)
G747_VALUES_REL = Path(
    "experiments/yolo/gdt747_supported_whole_passage_application/artifacts/"
    "SUPPORTED_12_PASSAGE_VALUES.tsv"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


g747 = load_module("gdt747_builder_for_gdt748", ROOT / G747_RUN_REL)

AXIS_ORDER = tuple(g747.AXIS_ORDER)
QUALITY_AXES = {"HOT", "COLD", "DRY", "MOIST"}
STAGE_AXES = {"BEGIN_STAGE", "MIDDLE_STAGE", "END_STAGE", "LEVEL_II", "LEVEL_III"}
PREDICTABLE_AXES = QUALITY_AXES | STAGE_AXES
OPPOSITIONS = (
    ("HOT", "COLD", "THERMAL"),
    ("DRY", "MOIST", "MOISTURE"),
    ("BEGIN_STAGE", "MIDDLE_STAGE", "STAGE"),
    ("BEGIN_STAGE", "END_STAGE", "STAGE"),
    ("MIDDLE_STAGE", "END_STAGE", "STAGE"),
    ("LEVEL_II", "LEVEL_III", "LEVEL"),
)
OUTPUT_NAMES = (
    "ELIGIBLE_ONE_OPEN_FRAME_CENSUS.tsv",
    "PREDICTIVE_SERIAL_FRAME_CENSUS.tsv",
    "COLLAPSED_POSITION_EVIDENCE.tsv",
    "FORM_BRIDGED_POSITION_EVIDENCE.tsv",
    "SURFACE_PREDICTION_CENSUS.tsv",
    "HELD_12_SERIAL_AUDIT.tsv",
    "KNOWN_LEAVE_ONE_OUT_CALIBRATION.tsv",
    "FORM_BRIDGE_CALIBRATION_CENSUS.tsv",
    "GDT748_COMPLETE_WHOLE_SERIAL_READER.md",
    "GDT748_GDT388_SERIAL_EDGE_PACKET.tsv",
    "GDT748_GDT388_EDGE_INTAKE.json",
)


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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def split_values(value: str) -> set[str]:
    return set() if value in {"", "NONE", "OPEN", "NA"} else set(value.split("|"))


def joined(values: Iterable[str]) -> str:
    members = set(values)
    ordered = [axis for axis in AXIS_ORDER if axis in members]
    ordered.extend(sorted(members - set(AXIS_ORDER)))
    return "|".join(ordered) or "NONE"


def count_string(counter: Counter[str]) -> str:
    return "|".join(
        f"{axis}:{counter[axis]}" for axis in AXIS_ORDER if counter[axis]
    ) or "NONE"


def semantic_axes(text: str, patterns: dict[str, object]) -> set[str]:
    axes = set(g747.semantic_axes(text, patterns))
    if re.search(r"koch|ausgekoch", text, re.I):
        axes.add("HOT")
    return axes


def known_card(
    locus: str,
    ordinal: int,
    cell: dict[str, str],
    patch_map: dict[tuple[str, int], dict[str, str]],
    patterns: dict[str, object],
) -> dict[str, object]:
    patch = patch_map.get((locus, ordinal))
    if patch is not None:
        text = patch["gdt743_working_render_de"]
        axes = semantic_axes(text, patterns)
        if g747.safe_semantic(text) and axes:
            return {
                "known": 1,
                "source_class": "GDT743_OCCURRENCE_WHOLE",
                "axes": axes,
                "render_de": text,
                "retired_literal_withheld": 0,
            }

    text = cell["v99r7_semantic_value_de"]
    retired = not g747.safe_semantic(text) and any(
        word in text.lower() for word in g747.RETIRED_LITERAL_WORDS
    )
    clean = (
        cell["unknown_v99r7"] == "0"
        and cell["gdt734_composition_semantic_credit"] == "0"
        and cell["component_export_credit"] == "0"
        and g747.safe_semantic(text)
    )
    axes = semantic_axes(text, patterns) if clean else set()
    if clean and axes and cell["gdt734_confidence_level"].startswith(("W2", "W3")):
        return {
            "known": 1,
            "source_class": "GDT734_W23_SAFE_WHOLE",
            "axes": axes,
            "render_de": text,
            "retired_literal_withheld": 0,
        }
    if clean and axes:
        source = "GDT734_WEAK_AXIS_TARGET"
        render = f"[{text}; schwach]"
    elif retired:
        source = "WITHHELD_RETIRED_LITERAL_TARGET"
        render = f"[{cell['surface']}: zurückgehaltene Altidentität]"
    else:
        source = "OPEN_TARGET"
        render = f"[{cell['surface']}:?]"
    return {
        "known": 0,
        "source_class": source,
        "axes": axes,
        "render_de": render,
        "retired_literal_withheld": int(retired),
    }


def contrast_dimensions(known_axes: set[str]) -> tuple[str, ...]:
    return tuple(
        name for left, right, name in OPPOSITIONS
        if left in known_axes and right in known_axes
    )


def frame_tier(all_reader_exact: int, known_count: int, distinct_known: int) -> str:
    if all_reader_exact and known_count == 3 and distinct_known == 3:
        return "F4_THREE_DISTINCT_EXACT_CARDS"
    if all_reader_exact and known_count == 3:
        return "F3_THREE_EXACT_CARDS"
    if all_reader_exact:
        return "F2_TWO_EXACT_CARDS"
    return "F1_READER_VARIABLE_CARDS"


def form_bridge_metrics(target: str, known_surfaces: set[str]) -> dict[str, object]:
    distances = sorted(
        g747.g745.levenshtein(target, surface) for surface in known_surfaces
    )
    minimum = distances[0]
    within_one = sum(distance <= 1 for distance in distances)
    within_two = sum(distance <= 2 for distance in distances)
    if within_two >= 2:
        tier = "B3_MULTIPLE_EDIT2_WHOLE_BRIDGES"
    elif minimum == 1:
        tier = "B2_DIRECT_EDIT1_WHOLE_BRIDGE"
    elif minimum == 2:
        tier = "B1_DIRECT_EDIT2_WHOLE_BRIDGE"
    else:
        tier = "B0_NO_WHOLE_FORM_BRIDGE"
    return {
        "minimum_whole_edit_distance": minimum,
        "known_wholes_within_edit1": within_one,
        "known_wholes_within_edit2": within_two,
        "whole_form_bridge_tier": tier,
    }


def form_bridge_weight(tier: str) -> int:
    return {
        "B3_MULTIPLE_EDIT2_WHOLE_BRIDGES": 3,
        "B2_DIRECT_EDIT1_WHOLE_BRIDGE": 2,
        "B1_DIRECT_EDIT2_WHOLE_BRIDGE": 1,
        "B0_NO_WHOLE_FORM_BRIDGE": 0,
    }[tier]


def opposition_conflict(predicted: set[str], actual: set[str]) -> bool:
    return any(
        (left in predicted and right in actual)
        or (right in predicted and left in actual)
        for left, right, _ in OPPOSITIONS
    )


def automatic_default(axes: set[str]) -> str:
    labels = []
    for axis, label in (
        ("HOT", "heiß/warm"), ("COLD", "kalt/gekühlt"),
        ("DRY", "trocken"), ("MOIST", "feucht"),
        ("BEGIN_STAGE", "Anfangs-/Grundstufe"),
        ("MIDDLE_STAGE", "Mittelstufe"),
        ("END_STAGE", "End-/Vollstufe"),
        ("LEVEL_II", "Stufe II"), ("LEVEL_III", "Stufe III"),
    ):
        if axis in axes:
            labels.append(label)
    if not labels:
        return "Serienwert widersprüchlich; Funktion offen"
    return "; ".join(labels) + "; genaue Funktion und Identität offen"


def build_cards() -> tuple[
    dict[str, list[dict[str, object]]],
    dict[tuple[str, int], dict[str, object]],
    dict[str, object],
]:
    by_line, exact, guard = g747.g745.g739.g738.token_context()
    cells = g747.g745.g739.g738.compact_cells()
    _, patterns = g747.g745.g739.load_axis_specs()
    patch_map = {
        (row["locus"], int(row["token_ordinal"])): row
        for row in read_tsv(ROOT / G743_PATCH_REL)
    }
    line_cards: dict[str, list[dict[str, object]]] = {}
    coordinate_cards: dict[tuple[str, int], dict[str, object]] = {}
    for locus, tokens in by_line.items():
        rows = []
        for ordinal, token in enumerate(tokens, start=1):
            cell = cells[(locus, ordinal)]
            if token["eva"] != cell["surface"]:
                raise AssertionError(f"raw/cache mismatch at {locus}:{ordinal}")
            card = known_card(locus, ordinal, cell, patch_map, patterns)
            row = {
                "page": cell["page"],
                "locus": locus,
                "token_ordinal": ordinal,
                "token_index": int(token["token_index"]),
                "surface": cell["surface"],
                "reader_exact": exact[(locus, int(token["token_index"]))],
                **card,
            }
            rows.append(row)
            coordinate_cards[(locus, ordinal)] = row
        line_cards[locus] = rows
    if len(coordinate_cards) != 32339:
        raise AssertionError("complete token-card atlas changed size")
    return line_cards, coordinate_cards, guard


def enumerate_frames(
    line_cards: dict[str, list[dict[str, object]]],
    held_map: dict[str, dict[str, str]],
) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, int]]:
    eligible: list[dict[str, object]] = []
    predictive: list[dict[str, object]] = []
    total_windows = 0
    one_open_windows = 0
    for locus in sorted(line_cards):
        line = line_cards[locus]
        for window_length in (3, 4):
            for start_index in range(0, len(line) - window_length + 1):
                total_windows += 1
                window = line[start_index:start_index + window_length]
                known = [row for row in window if int(row["known"])]
                targets = [row for row in window if not int(row["known"])]
                if len(targets) != 1:
                    continue
                one_open_windows += 1
                target = targets[0]
                distinct_known = {str(row["surface"]) for row in known}
                if len(distinct_known) < 2 or str(target["surface"]) in distinct_known:
                    continue
                common = set.intersection(*(set(row["axes"]) for row in known))
                predicted_axes = common & PREDICTABLE_AXES
                union_axes = set.union(*(set(row["axes"]) for row in known))
                all_exact = int(all(int(row["reader_exact"]) for row in window))
                prior = held_map.get(str(target["surface"]))
                prior_axes = split_values(prior["passage_core_axes"]) if prior else set()
                if not prior:
                    prior_comparison = "NO_GDT747_PRIOR"
                elif not prior_axes:
                    prior_comparison = "GDT747_PRIOR_OPEN"
                elif predicted_axes & prior_axes:
                    prior_comparison = "GDT747_PRIOR_REINFORCED"
                elif predicted_axes:
                    prior_comparison = "GDT747_PRIOR_CONFLICT"
                else:
                    prior_comparison = "NO_SERIAL_PREDICTION"
                target_position = int(target["token_ordinal"])
                target_position_in_window = target_position - int(window[0]["token_ordinal"]) + 1
                if target_position_in_window == 1:
                    target_window_slot = "FIRST"
                elif target_position_in_window == window_length:
                    target_window_slot = "LAST"
                else:
                    target_window_slot = "INNER"
                bridge = form_bridge_metrics(str(target["surface"]), distinct_known)
                row = {
                    "frame_id": f"G748-F{len(eligible) + 1:05d}",
                    "page": target["page"],
                    "physical_folio": g747.g745.physical_folio(str(target["page"])),
                    "locus": locus,
                    "window_start_ordinal": int(window[0]["token_ordinal"]),
                    "window_end_ordinal": int(window[-1]["token_ordinal"]),
                    "window_length": window_length,
                    "target_ordinal": target_position,
                    "target_position_in_window": target_position_in_window,
                    "target_window_slot": target_window_slot,
                    "target_surface": target["surface"],
                    "target_reader_exact": target["reader_exact"],
                    "target_source_before": target["source_class"],
                    "target_render_before_de": target["render_de"],
                    "target_axes_before": joined(set(target["axes"])),
                    "retired_literal_withheld": target["retired_literal_withheld"],
                    "known_card_count": len(known),
                    "distinct_known_surfaces": len(distinct_known),
                    "known_surfaces": joined(str(item["surface"]) for item in known),
                    "known_signed_offsets": joined(
                        str(int(item["token_ordinal"]) - target_position) for item in known
                    ),
                    "known_source_classes": joined(str(item["source_class"]) for item in known),
                    **bridge,
                    "known_card_axes": " || ".join(
                        f"{item['surface']}={joined(set(item['axes']))}" for item in known
                    ),
                    "known_card_values_de": " || ".join(
                        f"{item['surface']}={item['render_de']}" for item in known
                    ),
                    "shared_all_axes": joined(common),
                    "predicted_quality_stage_axes": joined(predicted_axes),
                    "known_union_axes": joined(union_axes),
                    "contrast_dimensions": "|".join(contrast_dimensions(union_axes)) or "NONE",
                    "all_reader_exact": all_exact,
                    "frame_tier": frame_tier(all_exact, len(known), len(distinct_known)),
                    "gdt747_prior_axes": joined(prior_axes),
                    "gdt747_prior_value_de": prior["passage_safe_value_de"] if prior else "NONE",
                    "gdt747_prior_comparison": prior_comparison,
                    "eva_window": " ".join(str(item["surface"]) for item in window),
                    "literal_identity": "OPEN",
                    "confirmed_lexeme": 0,
                    "component_export_credit": 0,
                }
                eligible.append(row)
                if predicted_axes:
                    predictive.append(dict(row))
    diagnostics = {
        "all_length3_4_windows": total_windows,
        "windows_with_exactly_one_non_w23_card": one_open_windows,
        "eligible_two_distinct_known_wholes": len(eligible),
        "predictive_quality_or_stage_frames": len(predictive),
    }
    return eligible, predictive, diagnostics


def collapse_positions(
    frames: list[dict[str, object]],
) -> list[dict[str, object]]:
    groups: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in frames:
        groups[(str(row["locus"]), int(row["target_ordinal"]))].append(row)
    tier_rank = {
        "F4_THREE_DISTINCT_EXACT_CARDS": 4,
        "F3_THREE_EXACT_CARDS": 3,
        "F2_TWO_EXACT_CARDS": 2,
        "F1_READER_VARIABLE_CARDS": 1,
    }
    output = []
    for key in sorted(groups):
        rows = groups[key]
        ranked = sorted(
            rows,
            key=lambda row: (
                -int(row["known_wholes_within_edit2"]),
                int(row["minimum_whole_edit_distance"]),
                -tier_rank[str(row["frame_tier"])],
                -int(row["distinct_known_surfaces"]),
                len(split_values(str(row["predicted_quality_stage_axes"]))),
                int(row["window_length"]),
                str(row["frame_id"]),
            ),
        )
        best = ranked[0]
        prediction_union = set().union(*(
            split_values(str(row["predicted_quality_stage_axes"])) for row in rows
        ))
        prediction_intersection = set.intersection(*(
            split_values(str(row["predicted_quality_stage_axes"])) for row in rows
        ))
        output.append({
            "evidence_id": f"G748-E{len(output) + 1:04d}",
            "page": best["page"],
            "physical_folio": best["physical_folio"],
            "locus": best["locus"],
            "target_ordinal": best["target_ordinal"],
            "target_position_in_window": best["target_position_in_window"],
            "target_window_slot": best["target_window_slot"],
            "target_surface": best["target_surface"],
            "target_reader_exact": best["target_reader_exact"],
            "target_source_before": best["target_source_before"],
            "target_render_before_de": best["target_render_before_de"],
            "target_axes_before": best["target_axes_before"],
            "retired_literal_withheld": best["retired_literal_withheld"],
            "overlapping_predictive_frames": len(rows),
            "frame_ids": "|".join(str(row["frame_id"]) for row in rows),
            "best_frame_id": best["frame_id"],
            "best_frame_tier": best["frame_tier"],
            "best_window_length": best["window_length"],
            "best_known_card_count": best["known_card_count"],
            "best_known_surfaces": best["known_surfaces"],
            "best_known_signed_offsets": best["known_signed_offsets"],
            "minimum_whole_edit_distance": best["minimum_whole_edit_distance"],
            "known_wholes_within_edit1": best["known_wholes_within_edit1"],
            "known_wholes_within_edit2": best["known_wholes_within_edit2"],
            "whole_form_bridge_tier": best["whole_form_bridge_tier"],
            "whole_form_bridge_weight": form_bridge_weight(
                str(best["whole_form_bridge_tier"])
            ),
            "best_known_card_axes": best["known_card_axes"],
            "best_known_card_values_de": best["known_card_values_de"],
            "predicted_axes_intersection_across_frames": joined(prediction_intersection),
            "predicted_axes_union_across_frames": joined(prediction_union),
            "best_predicted_axes": best["predicted_quality_stage_axes"],
            "best_contrast_dimensions": best["contrast_dimensions"],
            "gdt747_prior_axes": best["gdt747_prior_axes"],
            "gdt747_prior_value_de": best["gdt747_prior_value_de"],
            "gdt747_prior_comparison": best["gdt747_prior_comparison"],
            "eva_window": best["eva_window"],
            "working_prediction_de": automatic_default(
                split_values(str(best["predicted_quality_stage_axes"]))
            ),
            "literal_identity": "OPEN",
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    return output


def leave_one_out_calibration(
    line_cards: dict[str, list[dict[str, object]]],
) -> tuple[list[dict[str, object]], list[dict[str, object]], int]:
    raw: list[dict[str, object]] = []
    for locus in sorted(line_cards):
        line = line_cards[locus]
        for window_length in (3, 4):
            for start_index in range(0, len(line) - window_length + 1):
                window = line[start_index:start_index + window_length]
                if not all(int(row["known"]) for row in window):
                    continue
                for target_index, target in enumerate(window):
                    known = window[:target_index] + window[target_index + 1:]
                    known_surfaces = {str(row["surface"]) for row in known}
                    if (
                        len(known_surfaces) < 2
                        or str(target["surface"]) in known_surfaces
                    ):
                        continue
                    predicted = set.intersection(*(
                        set(row["axes"]) for row in known
                    )) & PREDICTABLE_AXES
                    if not predicted:
                        continue
                    actual = set(target["axes"]) & PREDICTABLE_AXES
                    union_axes = set.union(*(set(row["axes"]) for row in known))
                    bridge = form_bridge_metrics(str(target["surface"]), known_surfaces)
                    all_exact = int(all(int(row["reader_exact"]) for row in window))
                    target_position = int(target["token_ordinal"])
                    target_position_in_window = target_index + 1
                    target_slot = (
                        "FIRST" if target_index == 0
                        else "LAST" if target_index == window_length - 1
                        else "INNER"
                    )
                    raw.append({
                        "page": target["page"],
                        "locus": locus,
                        "target_ordinal": target_position,
                        "target_surface": target["surface"],
                        "target_reader_exact": target["reader_exact"],
                        "window_length": window_length,
                        "target_position_in_window": target_position_in_window,
                        "target_window_slot": target_slot,
                        "known_surfaces": joined(known_surfaces),
                        "known_card_values_de": " || ".join(
                            f"{row['surface']}={row['render_de']}" for row in known
                        ),
                        "predicted_axes": joined(predicted),
                        "actual_target_axes": joined(actual),
                        "known_union_axes": joined(union_axes),
                        "contrast_dimensions": (
                            "|".join(contrast_dimensions(union_axes)) or "NONE"
                        ),
                        "all_reader_exact": all_exact,
                        "frame_tier": frame_tier(
                            all_exact, len(known), len(known_surfaces)
                        ),
                        **bridge,
                        "eva_window": " ".join(
                            str(row["surface"]) for row in window
                        ),
                    })
    grouped: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in raw:
        grouped[(str(row["locus"]), int(row["target_ordinal"]))].append(row)
    tier_rank = {
        "F4_THREE_DISTINCT_EXACT_CARDS": 4,
        "F3_THREE_EXACT_CARDS": 3,
        "F2_TWO_EXACT_CARDS": 2,
        "F1_READER_VARIABLE_CARDS": 1,
    }
    selected = []
    for key in sorted(grouped):
        ranked = sorted(
            grouped[key],
            key=lambda row: (
                -int(row["known_wholes_within_edit2"]),
                int(row["minimum_whole_edit_distance"]),
                -tier_rank[str(row["frame_tier"])],
                len(split_values(str(row["predicted_axes"]))),
                -int(row["window_length"]),
            ),
        )
        best = ranked[0]
        predicted = split_values(str(best["predicted_axes"]))
        actual = split_values(str(best["actual_target_axes"]))
        selected.append({
            "calibration_id": f"G748-C{len(selected) + 1:04d}",
            **best,
            "overlapping_calibration_frames": len(grouped[key]),
            "any_axis_hit": int(bool(predicted & actual)),
            "full_prediction_subset_of_actual": int(predicted <= actual),
            "opposition_contradiction": int(opposition_conflict(predicted, actual)),
            "literal_identity_credit": 0,
            "component_export_credit": 0,
        })

    class_specs = (
        ("UNCONDITIONED_ALL", lambda row: True),
        ("READER_EXACT_ALL", lambda row: int(row["all_reader_exact"]) == 1),
        ("NO_FORM_BRIDGE", lambda row: int(row["known_wholes_within_edit2"]) == 0),
        ("FORM_BRIDGE_ANY", lambda row: int(row["known_wholes_within_edit2"]) >= 1),
        ("FORM_BRIDGE_READER_EXACT", lambda row: (
            int(row["known_wholes_within_edit2"]) >= 1
            and int(row["all_reader_exact"]) == 1
        )),
        ("DIRECT_EDIT1_BRIDGE", lambda row: int(row["minimum_whole_edit_distance"]) == 1),
        ("DIRECT_EDIT2_ONLY_BRIDGE", lambda row: int(row["minimum_whole_edit_distance"]) == 2),
        ("MULTIPLE_EDIT2_BRIDGES", lambda row: int(row["known_wholes_within_edit2"]) >= 2),
    )
    census = []
    for name, predicate in class_specs:
        rows = [row for row in selected if predicate(row)]
        if not rows:
            continue
        hits = sum(int(row["any_axis_hit"]) for row in rows)
        subsets = sum(int(row["full_prediction_subset_of_actual"]) for row in rows)
        contradictions = sum(int(row["opposition_contradiction"]) for row in rows)
        hit_rate = hits / len(rows)
        contradiction_rate = contradictions / len(rows)
        if name == "FORM_BRIDGE_ANY" and hit_rate >= 0.70:
            interpretation = "USE_AS_EXPLORATORY_WHOLE_ROLE_BRIDGE"
        elif name == "MULTIPLE_EDIT2_BRIDGES" and hit_rate >= 0.80:
            interpretation = "STRONGEST_EXPLORATORY_BRIDGE_CLASS"
        elif name == "NO_FORM_BRIDGE":
            interpretation = "DO_NOT_EXPORT_SERIAL_AXIS_AS_WORD_VALUE"
        else:
            interpretation = "CALIBRATION_ONLY"
        census.append({
            "calibration_class": name,
            "positions": len(rows),
            "reader_exact_positions": sum(int(row["all_reader_exact"]) for row in rows),
            "any_axis_hits": hits,
            "any_axis_hit_rate": f"{hit_rate:.6f}",
            "full_prediction_subsets": subsets,
            "full_prediction_subset_rate": f"{subsets / len(rows):.6f}",
            "opposition_contradictions": contradictions,
            "opposition_contradiction_rate": f"{contradiction_rate:.6f}",
            "interpretation": interpretation,
            "literal_identity_credit": 0,
            "component_export_credit": 0,
        })
    return selected, census, len(raw)


def surface_census(
    evidence: list[dict[str, object]],
) -> list[dict[str, object]]:
    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in evidence:
        groups[str(row["target_surface"])].append(row)
    output = []
    for surface in sorted(groups):
        rows = groups[surface]
        axis_counts: Counter[str] = Counter(
            axis for row in rows
            for axis in split_values(str(row["best_predicted_axes"]))
        )
        unweighted_consensus = {
            axis for axis, count in axis_counts.items()
            if count / len(rows) >= 0.60
        }
        weighted_axis_counts: Counter[str] = Counter()
        total_bridge_weight = 0
        for row in rows:
            weight = int(row["whole_form_bridge_weight"])
            total_bridge_weight += weight
            for axis in split_values(str(row["best_predicted_axes"])):
                weighted_axis_counts[axis] += weight
        consensus = {
            axis for axis, count in weighted_axis_counts.items()
            if count / total_bridge_weight >= 0.60
            and (len(rows) == 1 or axis_counts[axis] >= 2)
        }
        strongest_row = max(
            rows,
            key=lambda row: (
                int(row["whole_form_bridge_weight"]),
                int(row["target_reader_exact"]),
                -len(split_values(str(row["best_predicted_axes"]))),
                str(row["evidence_id"]),
            ),
        )
        strongest_axes = split_values(str(strongest_row["best_predicted_axes"]))
        conflicts = sorted({
            name for left, right, name in OPPOSITIONS
            if axis_counts[left] and axis_counts[right]
        })
        pages = {str(row["page"]) for row in rows}
        exact_rows = sum(int(row["target_reader_exact"]) for row in rows)
        if consensus and len(rows) >= 3 and len(pages) >= 2 and not conflicts:
            status = "S3_RECURRENT_CROSS_PAGE_SERIAL_CONSENSUS"
        elif consensus and len(rows) >= 2 and not conflicts:
            status = "S2_RECURRENT_SERIAL_CONSENSUS"
        elif consensus and len(rows) == 1:
            status = "S1_SINGLE_WRITTEN_SERIAL_LEAD"
        elif consensus:
            status = "S1_CONSENSUS_WITH_DIMENSION_CONFLICT"
        else:
            status = "S0_MIXED_SERIAL_PREDICTIONS"
        short_form_control_rival = int(len(surface) <= 2)
        if short_form_control_rival:
            status = "S1_SHORT_FORM_CONTROL_RIVAL"
        prior_axis_hits = sum(
            bool(
                split_values(str(row["best_predicted_axes"]))
                & split_values(str(row["target_axes_before"]))
            )
            for row in rows
        )
        prior_axis_conflicts = sum(
            opposition_conflict(
                split_values(str(row["best_predicted_axes"])),
                split_values(str(row["target_axes_before"])),
            )
            for row in rows
        )
        target_sources = Counter(str(row["target_source_before"]) for row in rows)
        target_prior_union = set().union(*(
            split_values(str(row["target_axes_before"])) for row in rows
        ))
        if status.startswith(("S2_", "S3_")):
            if set(target_sources) == {"OPEN_TARGET"}:
                role_decision = "NEW_OPEN_WHOLE_ROLE_LEAD"
            elif set(target_sources) == {"WITHHELD_RETIRED_LITERAL_TARGET"}:
                role_decision = "REPLACE_RETIRED_LITERAL_WITH_AXIS_ROLE_LEAD"
            elif consensus & target_prior_union:
                role_decision = "REINFORCE_OR_NARROW_WEAK_AXIS_CARD"
            else:
                role_decision = "CONTEXTUAL_RIVAL_TO_WEAK_AXIS_CARD"
        else:
            role_decision = "NO_RECURRENT_ROLE_EXPORT"
        prior_axes = split_values(str(rows[0]["gdt747_prior_axes"]))
        if not prior_axes:
            prior_result = (
                "GDT747_PRIOR_OPEN" if rows[0]["gdt747_prior_comparison"] == "GDT747_PRIOR_OPEN"
                else "NO_GDT747_PRIOR"
            )
        elif consensus & prior_axes:
            prior_result = "GDT747_PRIOR_REINFORCED"
        elif strongest_axes & prior_axes:
            prior_result = "GDT747_PRIOR_STRONGEST_FRAME_REINFORCED_WITH_RIVALS"
        else:
            prior_result = "GDT747_PRIOR_CONFLICT"
        output.append({
            "surface_id": f"G748-S{len(output) + 1:04d}",
            "target_surface": surface,
            "position_evidence_units": len(rows),
            "pages": len(pages),
            "physical_folios": len({str(row["physical_folio"]) for row in rows}),
            "reader_exact_evidence_units": exact_rows,
            "minimum_whole_edit_distance": min(
                int(row["minimum_whole_edit_distance"]) for row in rows
            ),
            "multi_bridge_evidence_units": sum(
                int(row["known_wholes_within_edit2"]) >= 2 for row in rows
            ),
            "whole_form_bridge_tier_counts": "|".join(
                f"{key}:{value}" for key, value in sorted(Counter(
                    str(row["whole_form_bridge_tier"]) for row in rows
                ).items())
            ),
            "best_frame_tier_counts": "|".join(
                f"{key}:{value}" for key, value in sorted(Counter(
                    str(row["best_frame_tier"]) for row in rows
                ).items())
            ),
            "axis_prediction_counts": count_string(axis_counts),
            "total_whole_form_bridge_weight": total_bridge_weight,
            "weighted_axis_prediction_counts": count_string(weighted_axis_counts),
            "serial_consensus_axes_unweighted": joined(unweighted_consensus),
            "serial_consensus_axes": joined(consensus),
            "strongest_single_evidence_axes": joined(strongest_axes),
            "strongest_single_evidence_id": strongest_row["evidence_id"],
            "dimension_conflicts": "|".join(conflicts) or "NONE",
            "serial_status": status,
            "short_form_control_rival": short_form_control_rival,
            "role_decision": role_decision,
            "automatic_working_default_de": automatic_default(consensus),
            "target_source_before_counts": "|".join(
                f"{key}:{value}" for key, value in sorted(target_sources.items())
            ),
            "target_axes_before_counts": count_string(Counter(
                axis for row in rows
                for axis in split_values(str(row["target_axes_before"]))
            )),
            "serial_hits_target_axes_before": prior_axis_hits,
            "serial_conflicts_target_axes_before": prior_axis_conflicts,
            "target_values_before_de": " || ".join(dict.fromkeys(
                str(row["target_render_before_de"]) for row in rows
            )),
            "gdt747_prior_axes": rows[0]["gdt747_prior_axes"],
            "gdt747_prior_value_de": rows[0]["gdt747_prior_value_de"],
            "gdt747_prior_result": prior_result,
            "evidence_ids": "|".join(str(row["evidence_id"]) for row in rows),
            "evidence_loci": "|".join(sorted({str(row["locus"]) for row in rows})),
            "best_evidence_de": (
                f"{rows[0]['locus']} {rows[0]['eva_window']} :: "
                f"{rows[0]['best_known_card_values_de']}"
            ),
            "literal_identity": "OPEN",
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    return output


def held_audit(
    held_rows: list[dict[str, str]],
    surface_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    surface_map = {str(row["target_surface"]): row for row in surface_rows}
    output = []
    for held in sorted(held_rows, key=lambda row: row["candidate_surface"]):
        surface = held["candidate_surface"]
        found = surface_map.get(surface)
        output.append({
            "held_id": f"G748-H{len(output) + 1:02d}",
            "candidate_surface": surface,
            "gdt747_passage_core_axes": held["passage_core_axes"],
            "gdt747_passage_value_de": held["passage_safe_value_de"],
            "serial_position_evidence_units": found["position_evidence_units"] if found else 0,
            "serial_pages": found["pages"] if found else 0,
            "serial_consensus_axes": found["serial_consensus_axes"] if found else "NONE",
            "strongest_single_evidence_axes": (
                found["strongest_single_evidence_axes"] if found else "NONE"
            ),
            "serial_status": found["serial_status"] if found else "H0_NO_ELIGIBLE_SERIAL_FRAME",
            "serial_prior_result": found["gdt747_prior_result"] if found else "NO_SERIAL_TEST",
            "serial_working_default_de": found["automatic_working_default_de"] if found else "NONE",
            "best_serial_evidence_de": found["best_evidence_de"] if found else "NONE",
            "literal_identity": "OPEN",
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    return output


def write_reader(
    path: Path,
    surfaces: list[dict[str, object]],
    held: list[dict[str, object]],
    evidence: list[dict[str, object]],
) -> None:
    status_rank = {
        "S3_RECURRENT_CROSS_PAGE_SERIAL_CONSENSUS": 4,
        "S2_RECURRENT_SERIAL_CONSENSUS": 3,
        "S1_SINGLE_WRITTEN_SERIAL_LEAD": 2,
        "S1_CONSENSUS_WITH_DIMENSION_CONFLICT": 1,
        "S1_SHORT_FORM_CONTROL_RIVAL": 1,
        "S0_MIXED_SERIAL_PREDICTIONS": 0,
    }
    ranked = sorted(
        surfaces,
        key=lambda row: (
            -status_rank[str(row["serial_status"])],
            -int(row["position_evidence_units"]),
            -int(row["pages"]),
            str(row["target_surface"]),
        ),
    )
    lines = [
        "# GDT748 complete-whole serial reader", "",
        "Jede Vorhersage stammt aus zwei oder drei vollständig geschriebenen,",
        "bereits gestützten Nachbarwörtern und besitzt zusätzlich mindestens eine",
        "vollständige Nachbarform in Editdistanz eins oder zwei. EVA-Teilstrings",
        "werden nicht zerlegt.", "",
        "## Oberflächen mit wiederholter Serienstütze", "",
    ]
    recurrent = [row for row in ranked if int(row["position_evidence_units"]) >= 2]
    if not recurrent:
        lines.append("Keine Oberfläche besitzt zwei unabhängige Positionsbelege.")
    for row in recurrent:
        lines.append(
            f"- `{row['target_surface']}` — {row['serial_status']}: "
            f"{row['automatic_working_default_de']} "
            f"({row['position_evidence_units']} Stellen/{row['pages']} Seiten; "
            f"GDT747: {row['gdt747_prior_result']})"
        )
    lines.extend(["", "## Audit der zwölf GDT747-Kandidaten", ""])
    for row in held:
        lines.append(
            f"- `{row['candidate_surface']}` — {row['serial_prior_result']}; "
            f"Serie `{row['serial_consensus_axes']}` aus "
            f"{row['serial_position_evidence_units']} Stelle(n), stärkster Einzelrahmen "
            f"`{row['strongest_single_evidence_axes']}`."
        )
    lines.extend(["", "## Die 40 stärksten geschriebenen Stellen", ""])
    evidence_map = {str(row["evidence_id"]): row for row in evidence}
    shown = 0
    for surface in ranked:
        for evidence_id in str(surface["evidence_ids"]).split("|"):
            if evidence_id not in evidence_map:
                continue
            row = evidence_map[evidence_id]
            lines.extend([
                f"### `{row['locus']}@{row['target_ordinal']}` — `{row['target_surface']}`", "",
                f"`{row['eva_window']}`", "",
                f"Bekannte Karten: {row['best_known_card_values_de']}", "",
                f"Arbeitsvorhersage: **{row['working_prediction_de']}**", "",
            ])
            shown += 1
            if shown >= 40:
                break
        if shown >= 40:
            break
    lines.extend([
        "## Grenze", "",
        "Die Karten benennen Zustands- und Stufenachsen, keine Pflanzen, Stoffe,",
        "Gefäße, Krankheiten, Handlungen oder Klartextwörter. Wiederholte Evidenz",
        "bleibt eine Ganzwort-Arbeitshypothese.", "",
    ])
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def edge_packet(
    output_dir: Path,
    evidence: list[dict[str, object]],
) -> dict[str, object]:
    rows = []
    for item in evidence:
        known_offset = int(str(item["best_known_signed_offsets"]).split("|")[0])
        known_ordinal = int(item["target_ordinal"]) + known_offset
        if known_ordinal == int(item["target_ordinal"]):
            raise AssertionError("serial edge did not select a distinct known whole")
        rows.append({
            "edge_id": f"G748E{len(rows) + 1:04d}",
            "batch_id": "GDT748_COMPLETE_WHOLE_SERIAL",
            "page": item["page"],
            "physical_folio": item["physical_folio"],
            "diagram_unit_id": "CACHED_TEXT_SERIAL_FRAME",
            "pivot_visual_id": f"OPEN_WHOLE_{item['target_surface']}",
            "pivot_locus": f"{item['locus']}@{item['target_ordinal']}",
            "target_visual_id": f"KNOWN_WHOLE_FRAME_{item['best_frame_id']}",
            "target_locus": f"{item['locus']}@{known_ordinal}",
            "relation_type": "SERIAL_COMPLETE_WHOLE_SHARED_AXIS",
            "direction_basis": "WRITTEN_CONSECUTIVE_THREE_OR_FOUR_WHOLES",
            "ownership_basis": "EXACTLY_ONE_NON_W23_COMPLETE_WHOLE",
            "geometry_only_selection": "FALSE",
            "source_manifest_id": "GDT748",
            "page_crop_sha256": "NONE",
            "pivot_crop_sha256": "NONE",
            "target_crop_sha256": "NONE",
            "source_aware_localizer": "GDT748_BUILDER",
            "relation_reviewer": "PENDING_EXTERNAL",
            "relation_confidence": item["best_frame_tier"],
            "ambiguity_state": "AXIS_ONLY_LITERAL_IDENTITY_OPEN",
            "formal_access_state": "FORMAL_ACCESSED",
            "fold_assignment": "NONE",
            "eligibility_status": "INELIGIBLE_FORMAL_CONTEXT_RELATION",
        })
    if not rows:
        raise AssertionError("no predictive serial relations")
    path = output_dir / "GDT748_GDT388_SERIAL_EDGE_PACKET.tsv"
    write_tsv(path, rows, list(rows[0]))
    completed = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", str(path)], cwd=ROOT,
        check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if completed.returncode not in {0, 1} or not completed.stdout:
        raise AssertionError(f"edge intake failed: {completed.stderr}")
    intake = json.loads(completed.stdout)
    if intake["status"] != "INVALID_PACKET" or intake["score_ready"]:
        raise AssertionError("serial packet unexpectedly score-ready")
    (output_dir / "GDT748_GDT388_EDGE_INTAKE.json").write_text(
        json.dumps(intake, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return intake


def build(output_dir: Path) -> dict[str, object]:
    held_rows = read_tsv(ROOT / G747_VALUES_REL)
    if len(held_rows) != 12:
        raise AssertionError("GDT747 held candidate count changed")
    held_map = {row["candidate_surface"]: row for row in held_rows}
    line_cards, coordinate_cards, guard = build_cards()
    eligible, predictive, diagnostics = enumerate_frames(line_cards, held_map)
    evidence = collapse_positions(predictive)
    form_bridged = [
        row for row in evidence if int(row["known_wholes_within_edit2"]) >= 1
    ]
    calibration, calibration_census, raw_calibration_frames = (
        leave_one_out_calibration(line_cards)
    )
    surfaces = surface_census(form_bridged)
    held = held_audit(held_rows, surfaces)

    output_dir.mkdir(parents=True, exist_ok=True)
    eligible_fields = list(eligible[0]) if eligible else []
    write_tsv(output_dir / OUTPUT_NAMES[0], eligible, eligible_fields)
    predictive_fields = list(predictive[0]) if predictive else eligible_fields
    write_tsv(output_dir / OUTPUT_NAMES[1], predictive, predictive_fields)
    evidence_fields = list(evidence[0]) if evidence else []
    write_tsv(output_dir / OUTPUT_NAMES[2], evidence, evidence_fields)
    write_tsv(output_dir / OUTPUT_NAMES[3], form_bridged, evidence_fields)
    surface_fields = list(surfaces[0]) if surfaces else []
    write_tsv(output_dir / OUTPUT_NAMES[4], surfaces, surface_fields)
    write_tsv(output_dir / OUTPUT_NAMES[5], held, list(held[0]))
    write_tsv(output_dir / OUTPUT_NAMES[6], calibration, list(calibration[0]))
    write_tsv(
        output_dir / OUTPUT_NAMES[7], calibration_census,
        list(calibration_census[0]),
    )
    write_reader(output_dir / OUTPUT_NAMES[8], surfaces, held, form_bridged)
    intake = edge_packet(output_dir, form_bridged)

    status_counts = Counter(str(row["serial_status"]) for row in surfaces)
    decision_counts = Counter(str(row["role_decision"]) for row in surfaces)
    prior_counts = Counter(str(row["serial_prior_result"]) for row in held)
    result = {
        "schema": "GDT748_RESULT_V1",
        "status": "PARTIAL_UNCONDITIONED_SERIAL_RULE_WEAK_FORM_BRIDGE_RETAINS_EXPLORATORY_LEADS",
        "scope": {
            **diagnostics,
            "allowed_pages": len({str(row["page"]) for row in coordinate_cards.values()}),
            "token_cards": len(coordinate_cards),
            "unconditioned_predictive_position_evidence_units": len(evidence),
            "form_bridged_position_evidence_units": len(form_bridged),
            "form_bridged_target_surfaces": len(surfaces),
            "raw_leave_one_out_frames": raw_calibration_frames,
            "collapsed_leave_one_out_positions": len(calibration),
            "held_candidates": len(held),
        },
        "surface_status_counts": dict(sorted(status_counts.items())),
        "role_decision_counts": dict(sorted(decision_counts.items())),
        "held_prior_result_counts": dict(sorted(prior_counts.items())),
        "recurrent_surface_count": sum(
            int(row["position_evidence_units"]) >= 2 for row in surfaces
        ),
        "cross_page_recurrent_surface_count": sum(
            int(row["pages"]) >= 2 and int(row["position_evidence_units"]) >= 2
            for row in surfaces
        ),
        "reader_exact_evidence_units": sum(
            int(row["target_reader_exact"]) for row in form_bridged
        ),
        "retired_literal_targets_withheld": sum(
            int(row["retired_literal_withheld"]) for row in form_bridged
        ),
        "calibration_census": calibration_census,
        "guard": guard,
        "edge_intake": intake,
        "top_recurrent_surfaces": [
            {
                "surface": row["target_surface"],
                "evidence_units": row["position_evidence_units"],
                "pages": row["pages"],
                "axes": row["serial_consensus_axes"],
                "status": row["serial_status"],
                "role_decision": row["role_decision"],
                "default_de": row["automatic_working_default_de"],
            }
            for row in sorted(
                surfaces,
                key=lambda item: (
                    -int(item["position_evidence_units"]),
                    -int(item["pages"]), str(item["target_surface"]),
                ),
            )[:25]
        ],
        "claim_ceiling": {
            "confirmed_lexemes": 0,
            "literal_identifications": 0,
            "component_export_credit": 0,
            "unseen_form_predictions": 0,
        },
        "output_sha256": {
            name: sha256(output_dir / name) for name in OUTPUT_NAMES
        },
    }
    (output_dir / "RESULT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_ARTIFACTS)
    args = parser.parse_args()
    result = build(args.output_dir.resolve())
    print(json.dumps({
        "scope": result["scope"],
        "surface_status_counts": result["surface_status_counts"],
        "role_decision_counts": result["role_decision_counts"],
        "held_prior_result_counts": result["held_prior_result_counts"],
        "recurrent_surface_count": result["recurrent_surface_count"],
        "status": result["status"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
