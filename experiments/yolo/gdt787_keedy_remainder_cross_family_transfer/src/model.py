#!/usr/bin/env python3
"""Type-balanced external-profile model for the GDT787 ``Xkeedy`` test.

The model treats every transcription surface as an opaque complete written
form.  It asks whether the external profile of ``Xkeedy`` can be reconstructed
from the three observed sister wholes ``Xkey``, ``Xkeey`` and ``Xkedy`` via

    P(Xkeedy) = P(Xkeey) + P(Xkedy) - P(Xkey).

Negative predicted cells are clipped to zero and every conceptual field is
renormalized.  The reported scores are Jensen--Shannon *similarities* in the
closed interval 0--1.  They are descriptive similarities, not probabilities,
confidence levels, lexical evidence, or component meanings.

Only reader-exact occurrences reconstructed through GDT782's guarded loader
enter the model.  Occurrences are first balanced within physical folio and
then every X row receives one vote.  All observed ``*keedy`` meanings and all
GDT754 provenance-sieve surfaces are masked when positive neighbour axes are
built.  A pair of empty positive-axis fields is NA rather than a perfect
shared-zero match.

``compute`` is deliberately read-only and returns TSV-friendly rows.  It does
not create artifacts or export an EVA letter/subword value.
"""

from __future__ import annotations

import csv
import importlib.util
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Mapping

sys.dont_write_bytecode = True


G782_RUN_REL = Path(
    "experiments/yolo/gdt782_recurrent_six_target_external_field_adjudication/"
    "src/run.py"
)
G746_REFERENCE_REL = Path(
    "experiments/yolo/gdt746_whole_analogy_distribution_test/artifacts/"
    "CALIBRATION_782_CANDIDATE_KNOWN_SCORES.tsv"
)
G754_PROVENANCE_REL = Path(
    "experiments/yolo/gdt754_active_productive_compound_provenance_sieve/"
    "artifacts/PROVENANCE_SIEVE_172_DECISIONS.tsv"
)

X_ROWS = ("che", "cho", "l", "o", "ol", "qo", "qol", "sol", "y")
SISTER_SUFFIXES = ("key", "keey", "kedy", "keedy")

PROFILE_FIELDS = (
    "register",
    "line_position",
    "line_third",
    "paragraph_boundary",
    "left_status",
    "right_status",
    "left_positive_axes",
    "right_positive_axes",
    "close_proximity",
)
STRUCTURAL_FIELDS = PROFILE_FIELDS[:6]
LOCAL_FIELDS = PROFILE_FIELDS[1:]

EXPECTED_TARGET_SURFACES = 27
EXPECTED_PROVENANCE_SURFACES = 172
EXPECTED_REFERENCE_SURFACES = 37
EXPECTED_PRIMARY_WINS = {
    "additive_beats_same_x": 5,
    "additive_beats_learned_whole": 4,
    "additive_beats_both": 3,
}
EXPECTED_PRIMARY_MACRO = {
    "additive": 0.678,
    "same_x": 0.701,
    "learned_whole": 0.675,
}


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _physical_folio(page: str) -> str:
    match = re.match(r"^(f\d+)", page)
    return match.group(1) if match else page


def _reconstruct_exact(g782) -> dict[str, object]:
    """Reconstruct the admitted reader-exact cache directly through GDT782."""
    by_line, exact, _cross, line_meta, cells, guard = g782.load_context()
    if int(guard["allowed_pages"]) != 179:
        raise AssertionError(f"guarded page count changed: {guard}")
    if any(
        str(token["page"]).startswith(("f84", "f84r"))
        for line in by_line.values()
        for token in line
    ):
        raise AssertionError("sealed f84/f84r row materialized")

    exact_counts: Counter[str] = Counter()
    occurrences: list[dict[str, object]] = []
    by_surface: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for locus, line in by_line.items():
        meta = line_meta[locus]
        line_length = len(line)
        for index, token in enumerate(line):
            if not exact[locus, int(token["token_index"])]:
                continue
            surface = str(token["eva"])
            exact_counts[surface] += 1
            ordinal = index + 1
            line_position = (
                "SINGLE" if line_length == 1
                else "FIRST" if ordinal == 1
                else "LAST" if ordinal == line_length
                else "MIDDLE"
            )

            def status(neighbour_index: int) -> str:
                if not 0 <= neighbour_index < line_length:
                    return "EDGE"
                neighbour = line[neighbour_index]
                return (
                    "EXACT"
                    if exact[locus, int(neighbour["token_index"])]
                    else "NONEXACT"
                )

            row = {
                "surface": surface,
                "page": str(token["page"]),
                "physical_folio": _physical_folio(str(token["page"])),
                "locus": str(locus),
                "ordinal": ordinal,
                "section": str(token["section"]),
                "language": str(token["language"]),
                "hand": str(token["hand"]),
                "line_position": line_position,
                "norm_pos": (
                    0.5 if line_length == 1
                    else (ordinal - 1) / (line_length - 1)
                ),
                "true_paragraph_start": str(
                    int(meta["paragraph_start"] == "1" and ordinal == 1)
                ),
                "true_paragraph_end": str(
                    int(meta["paragraph_end"] == "1" and ordinal == line_length)
                ),
                "left_status": status(index - 1),
                "right_status": status(index + 1),
            }
            occurrences.append(row)
            by_surface[surface].append(row)
    return {
        "by_line": by_line,
        "exact": exact,
        "guard": guard,
        "exact_counts": exact_counts,
        "occurrences": occurrences,
        "by_surface": dict(by_surface),
        "cells": cells,
    }


def _normalized(values: Mapping[str, float]) -> dict[str, float]:
    total = sum(values.values())
    if total <= 0:
        return {}
    return {key: value / total for key, value in values.items()}


def _js_similarity(
    left: Mapping[str, float], right: Mapping[str, float]
) -> float | None:
    """Return 1-JSD; two empty positive fields are explicitly unscored."""
    p = _normalized(left)
    q = _normalized(right)
    if not p and not q:
        return None
    if not p or not q:
        return 0.0
    keys = set(p) | set(q)
    middle = {key: (p.get(key, 0.0) + q.get(key, 0.0)) / 2 for key in keys}

    def divergence(source: Mapping[str, float]) -> float:
        return sum(
            value * math.log2(value / middle[key])
            for key, value in source.items()
            if value > 0
        )

    similarity = 1.0 - (divergence(p) + divergence(q)) / 2
    return min(1.0, max(0.0, similarity))


def _profile_similarity(
    left: Mapping[str, object],
    right: Mapping[str, object],
    fields: Iterable[str] = PROFILE_FIELDS,
) -> tuple[float, dict[str, float | None]]:
    components = {
        field: _js_similarity(
            left[field],  # type: ignore[arg-type]
            right[field],  # type: ignore[arg-type]
        )
        for field in fields
    }
    defined = [value for value in components.values() if value is not None]
    if not defined:
        raise AssertionError("profile comparison contains no defined fields")
    return sum(defined) / len(defined), components


def _additive_profile(
    xkeey: Mapping[str, object],
    xkedy: Mapping[str, object],
    xkey: Mapping[str, object],
) -> dict[str, dict[str, float]]:
    output: dict[str, dict[str, float]] = {}
    for field in PROFILE_FIELDS:
        end = xkeey[field]  # type: ignore[assignment]
        closed = xkedy[field]  # type: ignore[assignment]
        base = xkey[field]  # type: ignore[assignment]
        keys = set(end) | set(closed) | set(base)
        clipped = {
            key: max(
                0.0,
                end.get(key, 0.0)
                + closed.get(key, 0.0)
                - base.get(key, 0.0),
            )
            for key in keys
        }
        output[field] = _normalized(clipped)
    return output


def _mean_profile(
    profiles: list[Mapping[str, object]],
) -> dict[str, dict[str, float]]:
    if not profiles:
        raise AssertionError("empty learned-whole donor set")
    output: dict[str, dict[str, float]] = {}
    for field in PROFILE_FIELDS:
        keys = set().union(
            *(set(profile[field]) for profile in profiles)  # type: ignore[arg-type]
        )
        values = {
            key: sum(
                profile[field].get(key, 0.0)  # type: ignore[union-attr]
                for profile in profiles
            )
            / len(profiles)
            for key in keys
        }
        output[field] = _normalized(values)
    return output


def _levenshtein(left: str, right: str) -> int:
    previous = list(range(len(right) + 1))
    for row_number, left_char in enumerate(left, start=1):
        current = [row_number]
        for column, right_char in enumerate(right, start=1):
            current.append(
                min(
                    current[-1] + 1,
                    previous[column] + 1,
                    previous[column - 1] + int(left_char != right_char),
                )
            )
        previous = current
    return previous[-1]


def _frequency_bin(value: int) -> int:
    if value <= 1:
        return 0
    if value <= 2:
        return 1
    if value <= 5:
        return 2
    if value <= 15:
        return 3
    if value <= 45:
        return 4
    return 5


def compute(repo_root: Path) -> dict[str, object]:
    """Return the complete read-only GDT787 model result.

    The returned row dictionaries contain only scalar values and can be passed
    directly to a TSV writer.  No returned score is a probability.
    """
    root = Path(repo_root).resolve()
    if not (root / "AGENTS.md").is_file() or not (root / ".git").exists():
        raise RuntimeError(f"not a VManus repository root: {root}")

    g782 = _load_module("gdt782_guarded_for_gdt787_model", root / G782_RUN_REL)
    context = _reconstruct_exact(g782)
    exact_counts: Counter[str] = context["exact_counts"]  # type: ignore[assignment]
    by_surface: Mapping[str, list[dict[str, object]]] = context["by_surface"]  # type: ignore[assignment]
    by_line: Mapping[str, list[dict[str, str]]] = context["by_line"]  # type: ignore[assignment]
    exact: Mapping[tuple[str, int], int] = context["exact"]  # type: ignore[assignment]
    cells: Mapping[tuple[str, int], dict[str, str]] = context["cells"]  # type: ignore[assignment]
    guard: Mapping[str, object] = context["guard"]  # type: ignore[assignment]

    provenance_rows = _read_tsv(root / G754_PROVENANCE_REL)
    provenance_surfaces = {row["surface"] for row in provenance_rows}
    if len(provenance_surfaces) != EXPECTED_PROVENANCE_SURFACES:
        raise AssertionError(
            "GDT754 provenance surface set changed: "
            f"{len(provenance_surfaces)}"
        )
    target_surfaces = {
        surface for surface in exact_counts if surface.endswith("keedy")
    }
    if len(target_surfaces) != EXPECTED_TARGET_SURFACES:
        raise AssertionError(
            f"reader-exact *keedy target set changed: {len(target_surfaces)}"
        )

    axis_lines, axis_exact, axis_guard = by_line, exact, guard
    patterns = g782.load_axis_patterns()
    if int(axis_guard["allowed_pages"]) != 179:
        raise AssertionError(f"axis cache guard changed: {axis_guard}")
    if any(
        str(cell["page"]).startswith(("f84", "f84r"))
        for cell in cells.values()
    ):
        raise AssertionError("sealed f84/f84r cell entered axis cache")

    def clean_axes(cell: dict[str, str], reader_exact: int) -> tuple[str, ...]:
        semantic = cell["v99r7_semantic_value_de"]
        if not reader_exact or cell["unknown_v99r7"] != "0":
            return ()
        if not cell["gdt734_confidence_level"].startswith(("W2", "W3")):
            return ()
        if cell["gdt734_composition_semantic_credit"] != "0":
            return ()
        if cell["component_export_credit"] != "0":
            return ()
        if any(word in semantic.lower() for word in ("pulver", "samen", "saat", "wurzel", "holz")):
            return ()
        # Reproduce GDT746's clean-axis contract without importing its deep
        # builder chain.  In particular, that contract did not add the later
        # special ``koch/ausgekoch`` HOT synonym.
        axes = {
            axis for axis, pattern in patterns.items() if pattern.search(semantic)
        }
        axes.update(
            axis for axis, pattern in g782.STAGE_PATTERNS.items()
            if pattern.search(semantic)
        )
        return tuple(axis for axis in g782.AXIS_ORDER if axis in axes)

    def positive_axes(locus: str, ordinal: int) -> tuple[str, ...]:
        if not 1 <= ordinal <= len(axis_lines[locus]):
            return ()
        cell = cells[(locus, ordinal)]
        surface = str(cell["surface"])
        if surface in target_surfaces or surface in provenance_surfaces:
            return ()
        token = axis_lines[locus][ordinal - 1]
        return clean_axes(cell, axis_exact[(locus, int(token["token_index"]))])

    def build_profile(surface: str) -> dict[str, object] | None:
        occurrences = list(by_surface.get(surface, []))
        if not occurrences:
            return None
        folios: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
        for occurrence in occurrences:
            folios[str(occurrence["physical_folio"])].append(occurrence)
        distributions: dict[str, defaultdict[str, float]] = {
            field: defaultdict(float) for field in PROFILE_FIELDS
        }
        for folio_occurrences in folios.values():
            for occurrence in folio_occurrences:
                weight = 1 / len(folios) / len(folio_occurrences)
                locus = str(occurrence["locus"])
                ordinal = int(occurrence["ordinal"])
                progress = float(occurrence["norm_pos"])
                categories = {
                    "register": (
                        f"{occurrence['section']}|{occurrence['language']}|"
                        f"{occurrence['hand']}"
                    ),
                    "line_position": str(occurrence["line_position"]),
                    "line_third": (
                        "F" if progress < 1 / 3
                        else "M" if progress < 2 / 3
                        else "L"
                    ),
                    "paragraph_boundary": (
                        f"{occurrence['true_paragraph_start']}|"
                        f"{occurrence['true_paragraph_end']}"
                    ),
                    "left_status": str(occurrence["left_status"]),
                    "right_status": str(occurrence["right_status"]),
                }
                for field, category in categories.items():
                    distributions[field][category] += weight

                for field, axes in (
                    ("left_positive_axes", positive_axes(locus, ordinal - 1)),
                    ("right_positive_axes", positive_axes(locus, ordinal + 1)),
                ):
                    if axes:
                        for axis in axes:
                            distributions[field][axis] += weight / len(axes)

                close_hits = [
                    delta
                    for delta in (-5, -4, -3, -2, -1, 1, 2, 3, 4, 5)
                    if "CLOSE" in positive_axes(locus, ordinal + delta)
                ]
                if close_hits:
                    distance = min(abs(delta) for delta in close_hits)
                    sides = {
                        "L" if delta < 0 else "R"
                        for delta in close_hits
                        if abs(delta) == distance
                    }
                    side = "B" if len(sides) == 2 else next(iter(sides))
                    band = "1" if distance == 1 else "2" if distance == 2 else "3"
                    distributions["close_proximity"][side + band] += weight

        return {
            **{
                field: _normalized(values)
                for field, values in distributions.items()
            },
            "occurrences": len(occurrences),
            "physical_folios": len(folios),
        }

    reference_surfaces = {
        row["known_surface"]
        for row in _read_tsv(root / G746_REFERENCE_REL)
    }
    reference_surfaces -= target_surfaces
    reference_surfaces -= provenance_surfaces
    profiles: dict[str, dict[str, object]] = {}
    for surface in sorted(reference_surfaces):
        profile = build_profile(surface)
        if profile is not None:
            profiles[surface] = profile
    reference_surfaces = set(profiles)
    if len(reference_surfaces) != EXPECTED_REFERENCE_SURFACES:
        raise AssertionError(
            f"clean learned-whole reference set changed: {len(reference_surfaces)}"
        )

    required_surfaces = {
        surface
        for x in X_ROWS
        for surface in (x, *(x + suffix for suffix in SISTER_SUFFIXES))
    }
    for surface in sorted(required_surfaces):
        profile = build_profile(surface)
        if profile is None:
            raise AssertionError(f"required factorial surface absent: {surface}")
        profiles[surface] = profile

    def own_axes(surface: str) -> tuple[set[str], int]:
        axes: set[str] = set()
        clean_cells = 0
        for cell in cells.values():
            if str(cell["surface"]) != surface:
                continue
            locus = str(cell["locus"])
            ordinal = int(cell["token_ordinal"])
            token = axis_lines[locus][ordinal - 1]
            values = (
                ()
                if surface in target_surfaces or surface in provenance_surfaces
                else clean_axes(
                    cell, axis_exact[(locus, int(token["token_index"]))]
                )
            )
            if values:
                clean_cells += 1
                axes.update(values)
        return axes, clean_cells

    def radius_two_axis_rate(surface: str, axis: str) -> float | None:
        occurrences = list(by_surface.get(surface, []))
        if not occurrences:
            return None
        folios: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
        for occurrence in occurrences:
            folios[str(occurrence["physical_folio"])].append(occurrence)
        rate = 0.0
        for folio_occurrences in folios.values():
            for occurrence in folio_occurrences:
                weight = 1 / len(folios) / len(folio_occurrences)
                locus = str(occurrence["locus"])
                ordinal = int(occurrence["ordinal"])
                surrounding: set[str] = set()
                for delta in (-2, -1, 1, 2):
                    surrounding.update(positive_axes(locus, ordinal + delta))
                if axis in surrounding:
                    rate += weight
        return rate

    factorial_rows: list[dict[str, object]] = []
    contrast_rows: list[dict[str, object]] = []
    for x in X_ROWS:
        surfaces = {suffix: x + suffix for suffix in SISTER_SUFFIXES}
        target = profiles[surfaces["keedy"]]
        additive = _additive_profile(
            profiles[surfaces["keey"]],
            profiles[surfaces["kedy"]],
            profiles[surfaces["key"]],
        )
        additive_score, components = _profile_similarity(target, additive)
        same_x_score, _ = _profile_similarity(target, profiles[x])

        eligible = [
            surface
            for surface in reference_surfaces
            if abs(len(surface) - len(surfaces["keedy"])) <= 1
            and abs(
                _frequency_bin(exact_counts[surface])
                - _frequency_bin(exact_counts[surfaces["keedy"]])
            ) <= 1
            and surface not in set(surfaces.values())
        ]
        if not eligible:
            eligible = [
                surface
                for surface in reference_surfaces
                if abs(len(surface) - len(surfaces["keedy"])) <= 2
            ]
        if not eligible:
            raise AssertionError(f"no learned-whole control for {x}")
        ranked = sorted(
            eligible,
            key=lambda surface: (
                _levenshtein(surfaces["keedy"], surface),
                abs(
                    _frequency_bin(exact_counts[surface])
                    - _frequency_bin(exact_counts[surfaces["keedy"]])
                ),
                abs(len(surface) - len(surfaces["keedy"])),
                surface,
            ),
        )
        minimum_distance = _levenshtein(surfaces["keedy"], ranked[0])
        learned_donors = [
            surface
            for surface in ranked
            if _levenshtein(surfaces["keedy"], surface) == minimum_distance
        ][:3]
        learned_profile = _mean_profile(
            [profiles[surface] for surface in learned_donors]
        )
        learned_score, _ = _profile_similarity(target, learned_profile)

        structural_additive, _ = _profile_similarity(
            target, additive, STRUCTURAL_FIELDS
        )
        structural_same_x, _ = _profile_similarity(
            target, profiles[x], STRUCTURAL_FIELDS
        )
        structural_learned, _ = _profile_similarity(
            target, learned_profile, STRUCTURAL_FIELDS
        )
        local_additive, _ = _profile_similarity(target, additive, LOCAL_FIELDS)
        local_same_x, _ = _profile_similarity(target, profiles[x], LOCAL_FIELDS)
        local_learned, _ = _profile_similarity(
            target, learned_profile, LOCAL_FIELDS
        )

        adversarial_scores = [
            (_profile_similarity(target, profiles[surface])[0], surface)
            for surface in sorted(reference_surfaces)
        ]
        adversarial_score, adversarial_surface = max(adversarial_scores)
        beats_same = int(additive_score > same_x_score)
        beats_learned = int(additive_score > learned_score)
        factorial_rows.append({
            "x": x,
            "target_surface": surfaces["keedy"],
            "target_reader_exact_occurrences": target["occurrences"],
            "target_physical_folios": target["physical_folios"],
            "x_reader_exact_occurrences": exact_counts[x],
            "xkey_reader_exact_occurrences": exact_counts[surfaces["key"]],
            "xkeey_reader_exact_occurrences": exact_counts[surfaces["keey"]],
            "xkedy_reader_exact_occurrences": exact_counts[surfaces["kedy"]],
            "additive_similarity": additive_score,
            "same_x_similarity": same_x_score,
            "learned_whole_similarity": learned_score,
            "learned_whole_min_edit_distance": minimum_distance,
            "learned_whole_donors": "|".join(learned_donors),
            "additive_beats_same_x": beats_same,
            "additive_beats_learned_whole": beats_learned,
            "additive_beats_both": int(beats_same and beats_learned),
            "structural_additive_similarity": structural_additive,
            "structural_same_x_similarity": structural_same_x,
            "structural_learned_whole_similarity": structural_learned,
            "local_additive_similarity": local_additive,
            "local_same_x_similarity": local_same_x,
            "local_learned_whole_similarity": local_learned,
            "adversarial_best_similarity": adversarial_score,
            "adversarial_best_surface": adversarial_surface,
            "additive_beats_adversarial_best": int(
                additive_score > adversarial_score
            ),
            "defined_profile_fields": sum(
                value is not None for value in components.values()
            ),
            "score_semantics": "JENSEN_SHANNON_SIMILARITY_NOT_PROBABILITY",
        })

        key_axes, key_axis_cells = own_axes(surfaces["key"])
        keey_axes, keey_axis_cells = own_axes(surfaces["keey"])
        kedy_axes, kedy_axis_cells = own_axes(surfaces["kedy"])
        donor_end = (
            "NA"
            if not key_axis_cells or not keey_axis_cells
            else "YES"
            if "END_STAGE" in keey_axes and "END_STAGE" not in key_axes
            else "NO"
        )
        donor_close = (
            "NA"
            if not key_axis_cells or not kedy_axis_cells
            else "YES"
            if "CLOSE" in kedy_axes and "CLOSE" not in key_axes
            else "NO"
        )
        rates: dict[tuple[str, str], float | None] = {
            (suffix, axis): radius_two_axis_rate(surfaces[suffix], axis)
            for suffix in SISTER_SUFFIXES
            for axis in ("END_STAGE", "CLOSE")
        }

        def directional_delta(axis: str) -> float | None:
            values = [rates[suffix, axis] for suffix in SISTER_SUFFIXES]
            if any(value is None for value in values):
                return None
            numeric = [float(value) for value in values if value is not None]
            if sum(numeric) == 0:
                return None
            if axis == "END_STAGE":
                return (
                    float(rates["keey", axis])
                    + float(rates["keedy", axis])
                    - float(rates["key", axis])
                    - float(rates["kedy", axis])
                ) / 2
            return (
                float(rates["kedy", axis])
                + float(rates["keedy", axis])
                - float(rates["key", axis])
                - float(rates["keey", axis])
            ) / 2

        end_delta = directional_delta("END_STAGE")
        close_delta = directional_delta("CLOSE")

        contrast_rows.append({
            "x": x,
            "key_clean_own_axis_cells": key_axis_cells,
            "key_positive_own_axes": "|".join(sorted(key_axes)) or "NONE",
            "keey_clean_own_axis_cells": keey_axis_cells,
            "keey_positive_own_axes": "|".join(sorted(keey_axes)) or "NONE",
            "kedy_clean_own_axis_cells": kedy_axis_cells,
            "kedy_positive_own_axes": "|".join(sorted(kedy_axes)) or "NONE",
            "donor_end_direction": donor_end,
            "donor_close_direction": donor_close,
            "key_radius2_end_rate": rates["key", "END_STAGE"],
            "keey_radius2_end_rate": rates["keey", "END_STAGE"],
            "kedy_radius2_end_rate": rates["kedy", "END_STAGE"],
            "keedy_radius2_end_rate": rates["keedy", "END_STAGE"],
            "external_end_direction_delta": (
                end_delta if end_delta is not None else "NA"
            ),
            "key_radius2_close_rate": rates["key", "CLOSE"],
            "keey_radius2_close_rate": rates["keey", "CLOSE"],
            "kedy_radius2_close_rate": rates["kedy", "CLOSE"],
            "keedy_radius2_close_rate": rates["keedy", "CLOSE"],
            "external_close_direction_delta": (
                close_delta if close_delta is not None else "NA"
            ),
            "expected_direction": "POSITIVE",
        })

    if len(factorial_rows) != 9 or len(contrast_rows) != 9:
        raise AssertionError("factorial core is no longer nine X rows")

    views = (
        (
            "FULL",
            "additive_similarity",
            "same_x_similarity",
            "learned_whole_similarity",
            "|".join(PROFILE_FIELDS),
        ),
        (
            "STRUCTURAL",
            "structural_additive_similarity",
            "structural_same_x_similarity",
            "structural_learned_whole_similarity",
            "|".join(STRUCTURAL_FIELDS),
        ),
        (
            "LOCAL_NO_REGISTER",
            "local_additive_similarity",
            "local_same_x_similarity",
            "local_learned_whole_similarity",
            "|".join(LOCAL_FIELDS),
        ),
    )
    summary_rows: list[dict[str, object]] = []
    for view, additive_key, same_key, learned_key, fields in views:
        additive_values = [float(row[additive_key]) for row in factorial_rows]
        same_values = [float(row[same_key]) for row in factorial_rows]
        learned_values = [float(row[learned_key]) for row in factorial_rows]
        summary_rows.append({
            "view": view,
            "profile_fields": fields,
            "x_types": len(factorial_rows),
            "additive_macro_similarity": sum(additive_values) / len(additive_values),
            "same_x_macro_similarity": sum(same_values) / len(same_values),
            "learned_whole_macro_similarity": (
                sum(learned_values) / len(learned_values)
            ),
            "additive_beats_same_x": sum(
                additive > same
                for additive, same in zip(additive_values, same_values)
            ),
            "additive_beats_learned_whole": sum(
                additive > learned
                for additive, learned in zip(additive_values, learned_values)
            ),
            "additive_beats_both": sum(
                additive > same and additive > learned
                for additive, same, learned in zip(
                    additive_values, same_values, learned_values
                )
            ),
            "score_semantics": "JENSEN_SHANNON_SIMILARITY_NOT_PROBABILITY",
        })

    primary = summary_rows[0]
    for field, expected in EXPECTED_PRIMARY_WINS.items():
        if int(primary[field]) != expected:
            raise AssertionError(
                f"primary {field} changed: {primary[field]} != {expected}"
            )
    for field, expected in (
        ("additive_macro_similarity", EXPECTED_PRIMARY_MACRO["additive"]),
        ("same_x_macro_similarity", EXPECTED_PRIMARY_MACRO["same_x"]),
        (
            "learned_whole_macro_similarity",
            EXPECTED_PRIMARY_MACRO["learned_whole"],
        ),
    ):
        if round(float(primary[field]), 3) != expected:
            raise AssertionError(
                f"primary macro changed: {field}={primary[field]} != ~{expected}"
            )

    donor_end_counts = Counter(
        str(row["donor_end_direction"]) for row in contrast_rows
    )
    donor_close_counts = Counter(
        str(row["donor_close_direction"]) for row in contrast_rows
    )
    diagnostics = {
        "guard_loader": "GDT782_LOAD_CONTEXT",
        "guard_allowed_pages": int(guard["allowed_pages"]),
        "axis_guard_allowed_pages": int(axis_guard["allowed_pages"]),
        "reader_exact_keedy_targets_masked": len(target_surfaces),
        "gdt754_provenance_surfaces_masked": len(provenance_surfaces),
        "learned_whole_reference_types": len(reference_surfaces),
        "factorial_x_types": len(factorial_rows),
        "folio_balancing": "EQUAL_FOLIO_THEN_EQUAL_OCCURRENCE_WITHIN_FOLIO",
        "type_balancing": "ONE_VOTE_PER_X",
        "shared_zero_policy": "BOTH_EMPTY_POSITIVE_AXIS_FIELDS_ARE_NA",
        "score_semantics": "SIMILARITY_NOT_PROBABILITY",
        "primary_additive_beats_same_x": int(primary["additive_beats_same_x"]),
        "primary_additive_beats_learned_whole": int(
            primary["additive_beats_learned_whole"]
        ),
        "primary_additive_beats_both": int(primary["additive_beats_both"]),
        "primary_additive_macro_similarity": float(
            primary["additive_macro_similarity"]
        ),
        "primary_same_x_macro_similarity": float(
            primary["same_x_macro_similarity"]
        ),
        "primary_learned_whole_macro_similarity": float(
            primary["learned_whole_macro_similarity"]
        ),
        "additive_beats_adversarial_best": sum(
            int(row["additive_beats_adversarial_best"])
            for row in factorial_rows
        ),
        "donor_end_yes_no_na": (
            f"{donor_end_counts['YES']}|{donor_end_counts['NO']}|"
            f"{donor_end_counts['NA']}"
        ),
        "donor_close_yes_no_na": (
            f"{donor_close_counts['YES']}|{donor_close_counts['NO']}|"
            f"{donor_close_counts['NA']}"
        ),
        "recommendation": "WHOLE_ONLY",
        "component_export_credit": 0,
        "forbidden_f84_or_f84r_materialized": 0,
    }
    if diagnostics["additive_beats_adversarial_best"] != 2:
        raise AssertionError(
            "adversarial learned-whole sensitivity changed: "
            f"{diagnostics['additive_beats_adversarial_best']} != 2"
        )
    return {
        "factorial_rows": factorial_rows,
        "summary_rows": summary_rows,
        "contrast_rows": contrast_rows,
        "diagnostics": diagnostics,
    }


__all__ = ["compute"]
