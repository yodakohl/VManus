#!/usr/bin/env python3
"""Aggressively sanitized outside-axis audit for GDT787.

This read-only sensitivity removes the old family prose that could otherwise
make a ``*keedy`` hypothesis agree with itself.  It then compares complete
same-X wholes and asks separately about HOT, END and CLOSE.  A target type,
not an occurrence, is the unit of the final summary.
"""

from __future__ import annotations

import csv
import importlib.util
import itertools
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Mapping

sys.dont_write_bytecode = True


G782_REL = Path(
    "experiments/yolo/gdt782_recurrent_six_target_external_field_adjudication/"
    "src/run.py"
)
DICTIONARY_REL = Path(
    "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/"
    "artifacts/V99R7_1606_COMPLETE_WORD_CONFIDENCE.tsv"
)
G754_REL = Path(
    "experiments/yolo/gdt754_active_productive_compound_provenance_sieve/"
    "artifacts/PROVENANCE_SIEVE_172_DECISIONS.tsv"
)
G737_REL = Path(
    "experiments/yolo/gdt737_held_body_record_role_transfer/artifacts/"
    "V99R7_HELD_WHOLE_QUARANTINE.tsv"
)

MASKED_SOURCE_FAMILIES = (
    "GDT647", "GDT652", "GDT661", "GDT663", "GDT664", "GDT665",
)
RETIRED_PATIENTS = ("pulver", "samen", "saat", "wurzel", "holz")
MASKED_ENDING = re.compile(r"(?:teedy|keedy|kedy|keey|key)$")
CONTRASTS = (
    ("HOT", "teedy", "HOT", "COLD"),
    ("END", "kedy", "END_STAGE", "MIDDLE_STAGE"),
    ("CLOSE", "keey", "CLOSE", None),
)
EXPECTED_TYPES = {"HOT": 6, "END": 9, "CLOSE": 16}


def _load_module(path: Path):
    spec = importlib.util.spec_from_file_location("gdt782_for_gdt787_axis", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _physical_folio(page: str) -> str:
    match = re.match(r"^(f\d+)", page)
    if match is None:
        raise AssertionError(page)
    return match.group(1)


def _sign_flip_p(values: list[float]) -> float:
    active = [value for value in values if abs(value) > 1e-12]
    if not active:
        return 1.0
    observed = abs(sum(active))
    extreme = 0
    total = 1 << len(active)
    for signs in itertools.product((-1, 1), repeat=len(active)):
        if abs(sum(sign * value for sign, value in zip(signs, active))) >= observed - 1e-12:
            extreme += 1
    return extreme / total


def compute(repo_root: Path) -> dict[str, object]:
    root = Path(repo_root).resolve()
    g782 = _load_module(root / G782_REL)
    by_line, exact, _cross, _line_meta, _cells, guard = g782.load_context()
    if int(guard["allowed_pages"]) != 179:
        raise AssertionError(f"guard changed: {guard}")
    if any(
        str(token["page"]).startswith("f84")
        for line in by_line.values() for token in line
    ):
        raise AssertionError("sealed page materialized")

    patterns = g782.load_axis_patterns()
    g754 = {row["surface"] for row in _read_tsv(root / G754_REL)}
    g737 = {row["surface"] for row in _read_tsv(root / G737_REL)}
    grouped: defaultdict[str, list[set[str]]] = defaultdict(list)
    admitted_rows = 0
    for row in _read_tsv(root / DICTIONARY_REL):
        surface = row["surface"]
        meaning = row["working_meaning_de"]
        if not row["working_model_level"].startswith(("W2", "W3")):
            continue
        if row["gdt734_composition_semantic_credit"] != "0":
            continue
        if row["gdt734_component_export_allowed"] != "0":
            continue
        if row["gdt734_renderer_decision"] == "HOLD_UNCHANGED":
            continue
        if surface in g754 or surface in g737 or MASKED_ENDING.search(surface):
            continue
        if any(source in row["source_gdts"] for source in MASKED_SOURCE_FAMILIES):
            continue
        if any(patient in meaning.lower() for patient in RETIRED_PATIENTS):
            continue
        axes = g782.semantic_axes(meaning, patterns)
        if not axes:
            continue
        grouped[surface].append(set(axes))
        admitted_rows += 1
    pool = {
        surface: set.intersection(*axis_sets)
        for surface, axis_sets in grouped.items()
        if set.intersection(*axis_sets)
    }
    if (admitted_rows, len(pool)) != (413, 412):
        raise AssertionError(
            f"sanitized pool changed: rows={admitted_rows}, wholes={len(pool)}"
        )

    exact_counts: Counter[str] = Counter()
    target_occurrences: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for locus, line in by_line.items():
        for index, token in enumerate(line):
            if not exact[locus, int(token["token_index"])]:
                continue
            surface = str(token["eva"])
            exact_counts[surface] += 1
            if not MASKED_ENDING.search(surface):
                continue
            occurrence: dict[str, object] = {
                "folio": _physical_folio(str(token["page"])),
            }
            for radius in (1, 3):
                surrounding: set[str] = set()
                for neighbour_index in range(
                    max(0, index - radius), min(len(line), index + radius + 1)
                ):
                    if neighbour_index == index:
                        continue
                    neighbour = line[neighbour_index]
                    neighbour_surface = str(neighbour["eva"])
                    if not exact[locus, int(neighbour["token_index"])]:
                        continue
                    if MASKED_ENDING.search(neighbour_surface):
                        continue
                    surrounding.update(pool.get(neighbour_surface, set()))
                for axis in g782.AXIS_ORDER:
                    occurrence[f"r{radius}_{axis}"] = int(axis in surrounding)
            target_occurrences[surface].append(occurrence)

    def rate(surface: str, radius: int, axis: str) -> float:
        rows = target_occurrences[surface]
        by_folio: defaultdict[str, list[int]] = defaultdict(list)
        for row in rows:
            by_folio[str(row["folio"])].append(int(row[f"r{radius}_{axis}"]))
        if not by_folio:
            raise AssertionError(f"no profile for {surface}")
        return statistics.mean(
            statistics.mean(values) for values in by_folio.values()
        )

    exact_targets = sorted(
        surface for surface, count in exact_counts.items()
        if count and surface.endswith("keedy")
    )
    rows: list[dict[str, object]] = []
    for contrast, control_tail, positive_axis, opposing_axis in CONTRASTS:
        eligible: list[tuple[str, str, str]] = []
        for target_surface in exact_targets:
            prefix = target_surface[:-5]
            if not prefix:
                continue
            control_surface = prefix + control_tail
            if exact_counts[control_surface]:
                eligible.append((prefix, target_surface, control_surface))
        if len(eligible) != EXPECTED_TYPES[contrast]:
            raise AssertionError(
                f"{contrast} pair types changed: {len(eligible)}"
            )
        for prefix, target_surface, control_surface in eligible:
            for radius in (1, 3):
                target_positive = rate(target_surface, radius, positive_axis)
                control_positive = rate(control_surface, radius, positive_axis)
                target_opposing = (
                    rate(target_surface, radius, opposing_axis)
                    if opposing_axis else 0.0
                )
                control_opposing = (
                    rate(control_surface, radius, opposing_axis)
                    if opposing_axis else 0.0
                )
                target_score = target_positive - target_opposing
                control_score = control_positive - control_opposing
                delta = target_score - control_score
                informative = any(
                    value > 0
                    for value in (
                        target_positive, target_opposing,
                        control_positive, control_opposing,
                    )
                )
                rows.append({
                    "contrast": contrast,
                    "radius": radius,
                    "prefix_x": prefix,
                    "target_surface": target_surface,
                    "control_surface": control_surface,
                    "target_exact_occurrences": exact_counts[target_surface],
                    "control_exact_occurrences": exact_counts[control_surface],
                    "positive_axis": positive_axis,
                    "opposing_axis": opposing_axis or "NONE",
                    "target_positive_rate": target_positive,
                    "target_opposing_rate": target_opposing,
                    "control_positive_rate": control_positive,
                    "control_opposing_rate": control_opposing,
                    "directional_delta": delta,
                    "direction": (
                        "NA" if not informative
                        else "POSITIVE" if delta > 1e-12
                        else "NEGATIVE" if delta < -1e-12
                        else "ZERO"
                    ),
                    "type_weight": int(informative),
                    "score_is_probability": 0,
                    "component_export_credit": 0,
                })

    summary_rows: list[dict[str, object]] = []
    for contrast, _control, positive_axis, opposing_axis in CONTRASTS:
        for radius in (1, 3):
            selected = [
                row for row in rows
                if row["contrast"] == contrast and row["radius"] == radius
            ]
            informative = [row for row in selected if row["direction"] != "NA"]
            deltas = [float(row["directional_delta"]) for row in informative]
            counts = Counter(str(row["direction"]) for row in selected)
            summary_rows.append({
                "contrast": contrast,
                "radius": radius,
                "type_pairs": len(selected),
                "informative_type_pairs": len(informative),
                "na": counts["NA"],
                "positive": counts["POSITIVE"],
                "zero": counts["ZERO"],
                "negative": counts["NEGATIVE"],
                "mean_directional_delta": statistics.mean(deltas) if deltas else None,
                "median_directional_delta": statistics.median(deltas) if deltas else None,
                "exact_two_sided_sign_flip_p": _sign_flip_p(deltas) if deltas else None,
                "interpretation": (
                    "BEST_WEAK_LEAD_NOT_EXPORTABLE" if contrast == "END"
                    else "MIXED_NOT_EXPORTABLE" if contrast == "HOT"
                    else "MOSTLY_UNINFORMATIVE_NOT_EXPORTABLE"
                ),
                "score_is_probability": 0,
                "component_export_credit": 0,
            })

    diagnostics = {
        "allowed_pages": int(guard["allowed_pages"]),
        "sanitized_dictionary_rows": admitted_rows,
        "sanitized_axis_wholes": len(pool),
        "gdt754_surfaces_masked": len(g754),
        "gdt737_surfaces_masked": len(g737),
        "reader_exact_keedy_surfaces": len(exact_targets),
        "contrast_type_rows": len(rows) // 2,
        "radius_specific_rows": len(rows),
        "decision": "NO_AXIS_EXPORT__END_BEST_WEAK_LEAD",
        "component_export_credit": 0,
        "forbidden_f84_or_f84r_materialized": 0,
    }
    if len(exact_targets) != 27 or len(rows) != 62:
        raise AssertionError(f"axis audit shape changed: {diagnostics}")
    return {
        "contrast_rows": rows,
        "summary_rows": summary_rows,
        "diagnostics": diagnostics,
    }


__all__ = ["compute"]
