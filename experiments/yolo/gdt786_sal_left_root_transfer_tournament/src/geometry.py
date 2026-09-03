#!/usr/bin/env python3
"""Independent guarded geometry audit for the GDT786 ``sal+X`` cohort.

This module deliberately contains no renderer meanings and writes no files.
It reconstructs the admitted cache through GDT782's guarded ``query-tsv``
loader, builds target-masked formal features, and returns plain Python data for
``run.py`` or an independent validator.

Primary question
================

Does an observed complete form ``salX`` have the outer geometry expected from
a productive left ``sal`` core, or is it explained as well by complete forms
with the same remainder ``X``?

The primary cohort has ten complete types and twelve reader-exact occurrences.
``salf`` and ``salshcthdy`` are sensitivity-only because no other admitted
frequency-matched three-character root forms a complete ``R+X`` control.

Gower feature definition
=========================

Every categorical feature contributes 0 when equal and 1 when unequal.
``norm_pos`` is the sole numeric feature and contributes its absolute
difference on the already-normalized 0--1 scale.  Distances are arithmetic
means.  The primary ``FULL_FEATURE`` distance weights every conceptual feature
once; ``SIDE_BALANCED`` gives the root-facing and right-facing groups one half
each.

Root-facing/global group (14 features):

``section, language, hand, line_pos, line_len_bin, pstart_line,
pend_line, true_pstart, true_pend, norm_pos, left_dist, left_status,
left_len, left_freq``.

Right-facing/remainder group (4 features):

``right_dist, right_status, right_len, right_freq``.

Distance and length are coarsened before scoring.  Immediate-neighbour status
is one of ``EDGE``, ``EXACT`` and ``NONEXACT``; no neighbour spelling or
semantic/renderer field enters the decision features.

Models and nulls
================

``ADDITIVE``
    Root-facing features are compared with the 33 standalone ``sal``
    occurrences; right-facing features are compared with standalone ``X``.
``ROOT_ONLY`` / ``REMAINDER_ONLY``
    Both groups are compared with standalone ``sal`` or standalone ``X``.
``FAMILY_LOTO``
    Leave the target complete type out, then compare with every other primary
    ``sal+Y`` type.  Each complete type has equal weight.
``EXACT_WHOLE``
    Leave the occurrence out and compare only with another occurrence of the
    identical complete surface.  It is defined only for ``salo`` and ``saly``.
``WHOLE_BACKOFF``
    Use ``EXACT_WHOLE`` where possible and the same-remainder null otherwise.
``SAME_X_NULL``
    Compare with observed ``R+X`` complete forms whose roots are the other
    GDT785 frequency-matched three-character roots.  Each complete surface has
    equal weight, so e.g. 64 ``chody`` occurrences cannot dominate two
    ``loldy`` occurrences.
``LEN_FREQ_NULL``
    Compare with all non-``sal`` surfaces of the same written length and exact
    global frequency, again complete-type weighted.

Root recognition ranks an observed ``R+X`` complete type against standalone
root prototypes available in that same X column.  Mean occurrence distance is
used; ties are broken lexically.  The normalized rank is ``(rank-1)/(k-1)``.
The exact rank-null enumerates independent uniform ranks 1..k for all ten sal
columns.  Paired model comparisons use an exact 2^n sign-flip distribution of
the type-level distance differences.

No value is assigned to an EVA character or substring.  ``chorcholsal`` is not
in a target or control cohort.  ``f84`` and ``f84r`` remain rejected before
rows are materialized by the inherited guarded loader.
"""

from __future__ import annotations

import csv
import importlib.util
import itertools
import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Mapping, Sequence

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
G782_RUN = ROOT / "experiments/yolo/gdt782_recurrent_six_target_external_field_adjudication/src/run.py"
G785_FAMILY = ROOT / "experiments/yolo/gdt785_sal_exact_whole_field_census/artifacts/GDT785_23_SAL_STRING_FAMILY.tsv"
G785_ROOTS = ROOT / "experiments/yolo/gdt785_sal_exact_whole_field_census/artifacts/GDT785_12_TRIGRAM_ROOT_CONTROLS.tsv"

ROOT_FIELDS = (
    "section", "language", "hand", "line_pos", "line_len_bin",
    "pstart_line", "pend_line", "true_pstart", "true_pend", "norm_pos",
    "left_dist", "left_status", "left_len", "left_freq",
)
RIGHT_FIELDS = ("right_dist", "right_status", "right_len", "right_freq")
NO_REGISTER_ROOT_FIELDS = tuple(
    field for field in ROOT_FIELDS if field not in {"section", "language", "hand"}
)
PLACEMENT_ROOT_FIELDS = (
    "line_pos", "line_len_bin", "pstart_line", "pend_line",
    "true_pstart", "true_pend", "norm_pos", "left_dist",
)
PLACEMENT_RIGHT_FIELDS = ("right_dist",)
FLANK_ROOT_FIELDS = ("left_status", "left_len", "left_freq")
FLANK_RIGHT_FIELDS = ("right_status", "right_len", "right_freq")

EXPECTED_ROOTS = (
    "air", "cho", "dam", "kar", "lol", "lor",
    "ody", "sal", "sar", "sor", "tar", "tol",
)
EXPECTED_PRIMARY = {
    "salal": "al", "salar": "ar", "saldal": "dal", "saldam": "dam",
    "saldy": "dy", "salkeedy": "keedy", "salo": "o", "salol": "ol",
    "saltar": "tar", "saly": "y",
}
EXPECTED_SECONDARY = {"salf": "f", "salshcthdy": "shcthdy"}
EXPECTED_CONTROLS = {
    "al": ("airal", "karal", "loral", "saral", "soral", "taral"),
    "ar": ("choar", "karar", "sarar", "tarar"),
    "dal": ("chodal", "toldal"),
    "dam": ("chodam",),
    "dy": ("chody", "loldy", "toldy"),
    "keedy": ("chokeedy",),
    "o": ("saro",),
    "ol": ("airol", "sarol", "tarol", "tolol"),
    "tar": ("chotar",),
    "y": ("airy", "choy", "kary", "loly", "lory", "sary"),
}
NUMERIC_FIELDS = frozenset({"norm_pos"})


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def load_g782():
    spec = importlib.util.spec_from_file_location("gdt782_guarded_for_gdt786", G782_RUN)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import guarded GDT782 loader")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _length_bin(value: int) -> str:
    if value == 0:
        return "0"
    return str(value) if value <= 5 else "6+"


def _frequency_bin(value: int) -> str:
    if value == 0:
        return "0"
    if value <= 2:
        return str(value)
    if value <= 5:
        return "3-5"
    if value <= 15:
        return "6-15"
    if value <= 45:
        return "16-45"
    return "46+"


def _distance_bin(value: int) -> str:
    return str(value) if value <= 3 else "4+"


def _line_length_bin(value: int) -> str:
    if value == 1:
        return "1"
    if value <= 5:
        return "2-5"
    if value <= 9:
        return "6-9"
    if value <= 13:
        return "10-13"
    return "14+"


def _physical_folio(page: str) -> str:
    match = re.match(r"^(f\d+)", page)
    return match.group(1) if match else page


def reconstruct_guarded() -> dict[str, object]:
    """Return exact occurrence features reconstructed through the guard."""
    base = load_g782()
    by_line, exact, _cross, line_meta, _cells, guard = base.load_context()
    if int(guard["allowed_pages"]) != 179:
        raise AssertionError(f"guarded page count changed: {guard}")
    if any(
        token["page"].startswith("f84")
        for line in by_line.values()
        for token in line
    ):
        raise AssertionError("sealed f84/f84r row materialized")

    exact_counts: Counter[str] = Counter()
    for locus, line in by_line.items():
        for token in line:
            if exact[locus, int(token["token_index"])]:
                exact_counts[token["eva"]] += 1

    occurrences: list[dict[str, object]] = []
    for locus, line in by_line.items():
        meta = line_meta[locus]
        line_length = len(line)
        for index, token in enumerate(line):
            if not exact[locus, int(token["token_index"])]:
                continue
            ordinal = index + 1

            def neighbor(offset: int) -> tuple[str, str, str]:
                neighbor_index = index + offset
                if neighbor_index < 0 or neighbor_index >= line_length:
                    return "EDGE", "0", "0"
                item = line[neighbor_index]
                is_exact = exact[locus, int(item["token_index"])]
                return (
                    "EXACT" if is_exact else "NONEXACT",
                    _length_bin(len(item["eva"])),
                    _frequency_bin(exact_counts[item["eva"]]),
                )

            left = neighbor(-1)
            right = neighbor(1)
            line_position = (
                "SINGLE" if line_length == 1 else
                "FIRST" if ordinal == 1 else
                "LAST" if ordinal == line_length else "MIDDLE"
            )
            occurrences.append({
                "surface": token["eva"],
                "page": token["page"],
                "physical_folio": _physical_folio(token["page"]),
                "locus": locus,
                "ordinal": ordinal,
                "line_length": line_length,
                "section": token["section"],
                "language": token["language"],
                "hand": token["hand"],
                "line_pos": line_position,
                "line_len_bin": _line_length_bin(line_length),
                "pstart_line": meta["paragraph_start"],
                "pend_line": meta["paragraph_end"],
                "true_pstart": str(int(meta["paragraph_start"] == "1" and ordinal == 1)),
                "true_pend": str(int(meta["paragraph_end"] == "1" and ordinal == line_length)),
                "norm_pos": 0.5 if line_length == 1 else (ordinal - 1) / (line_length - 1),
                "left_dist": _distance_bin(ordinal - 1),
                "right_dist": _distance_bin(line_length - ordinal),
                "left_status": left[0], "left_len": left[1], "left_freq": left[2],
                "right_status": right[0], "right_len": right[1], "right_freq": right[2],
            })

    by_surface: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for row in occurrences:
        by_surface[str(row["surface"])].append(row)
    return {
        "base": base,
        "guard": guard,
        "exact_counts": exact_counts,
        "occurrences": occurrences,
        "by_surface": dict(by_surface),
        "by_line": by_line,
        "exact": exact,
    }


def gower_fields(
    left: Mapping[str, object], right: Mapping[str, object], fields: Sequence[str]
) -> float:
    values = []
    for field in fields:
        if field in NUMERIC_FIELDS:
            values.append(abs(float(left[field]) - float(right[field])))
        else:
            values.append(float(left[field] != right[field]))
    return statistics.mean(values) if values else 0.0


def split_gower(
    left: Mapping[str, object],
    right: Mapping[str, object],
    root_fields: Sequence[str],
    remainder_fields: Sequence[str],
    side_balanced: bool = False,
) -> float:
    root_distance = gower_fields(left, right, root_fields)
    remainder_distance = gower_fields(left, right, remainder_fields)
    if side_balanced:
        return (root_distance + remainder_distance) / 2
    return (
        len(root_fields) * root_distance
        + len(remainder_fields) * remainder_distance
    ) / (len(root_fields) + len(remainder_fields))


def _prototype_distance(
    target: Mapping[str, object],
    training: Sequence[Mapping[str, object]],
    root_fields: Sequence[str],
    remainder_fields: Sequence[str],
    side_balanced: bool,
) -> float:
    if not training:
        raise AssertionError("empty prototype")
    return statistics.mean(
        split_gower(target, donor, root_fields, remainder_fields, side_balanced)
        for donor in training
    )


def _type_balanced_distance(
    target: Mapping[str, object],
    surfaces: Sequence[str],
    by_surface: Mapping[str, Sequence[Mapping[str, object]]],
    root_fields: Sequence[str],
    remainder_fields: Sequence[str],
    side_balanced: bool,
    exclude: Mapping[str, object] | None = None,
    occurrence_weighted: bool = False,
) -> float:
    if occurrence_weighted:
        donors = [
            row for surface in surfaces for row in by_surface[surface]
            if row is not exclude
        ]
        return _prototype_distance(
            target, donors, root_fields, remainder_fields, side_balanced
        )
    type_distances = []
    for surface in surfaces:
        donors = [row for row in by_surface[surface] if row is not exclude]
        if donors:
            type_distances.append(_prototype_distance(
                target, donors, root_fields, remainder_fields, side_balanced
            ))
    if not type_distances:
        raise AssertionError("empty type-balanced prototype")
    return statistics.mean(type_distances)


def build_cohorts(context: Mapping[str, object]) -> dict[str, object]:
    exact_counts: Mapping[str, int] = context["exact_counts"]  # type: ignore[assignment]
    family_rows = read_tsv(G785_FAMILY)
    prefix = {
        row["surface"]: row["outer_remainder"]
        for row in family_rows if row["sal_string_class"] == "PREFIX_CORE"
    }
    roots = tuple(row["root"] for row in read_tsv(G785_ROOTS))
    if roots != EXPECTED_ROOTS:
        raise AssertionError(f"GDT785 root control changed: {roots}")
    controls = {
        remainder: tuple(
            root + remainder for root in roots
            if root != "sal" and exact_counts.get(root + remainder, 0) > 0
        )
        for remainder in set(prefix.values())
    }
    primary = {
        surface: remainder for surface, remainder in prefix.items()
        if controls[remainder]
    }
    secondary = {
        surface: remainder for surface, remainder in prefix.items()
        if not controls[remainder]
    }
    if primary != EXPECTED_PRIMARY or secondary != EXPECTED_SECONDARY:
        raise AssertionError(
            f"target cohort changed: primary={primary}; secondary={secondary}"
        )
    if {key: controls[key] for key in EXPECTED_CONTROLS} != EXPECTED_CONTROLS:
        raise AssertionError(f"same-X control matrix changed: {controls}")
    by_surface: Mapping[str, Sequence[Mapping[str, object]]] = context["by_surface"]  # type: ignore[assignment]
    if sum(len(by_surface[surface]) for surface in primary) != 12:
        raise AssertionError("expected 10 primary types / 12 occurrences")
    if sum(len(by_surface[surface]) for surface in secondary) != 2:
        raise AssertionError("expected 2 sensitivity types / 2 occurrences")
    return {
        "roots": roots,
        "prefix": prefix,
        "primary": primary,
        "secondary": secondary,
        "controls": controls,
    }


def _additive_distance(
    target: Mapping[str, object],
    remainder: str,
    by_surface: Mapping[str, Sequence[Mapping[str, object]]],
    root_fields: Sequence[str],
    remainder_fields: Sequence[str],
    side_balanced: bool,
) -> float:
    root_distance = statistics.mean(
        gower_fields(target, donor, root_fields) for donor in by_surface["sal"]
    )
    remainder_distance = statistics.mean(
        gower_fields(target, donor, remainder_fields)
        for donor in by_surface[remainder]
    )
    if side_balanced:
        return (root_distance + remainder_distance) / 2
    return (
        len(root_fields) * root_distance
        + len(remainder_fields) * remainder_distance
    ) / (len(root_fields) + len(remainder_fields))


def model_rows(
    context: Mapping[str, object],
    cohorts: Mapping[str, object],
    roots: Sequence[str],
    root_fields: Sequence[str] = ROOT_FIELDS,
    remainder_fields: Sequence[str] = RIGHT_FIELDS,
    side_balanced: bool = False,
    occurrence_weighted: bool = False,
    subset: str = "ALL",
) -> list[dict[str, object]]:
    exact_counts: Mapping[str, int] = context["exact_counts"]  # type: ignore[assignment]
    by_surface: Mapping[str, Sequence[Mapping[str, object]]] = context["by_surface"]  # type: ignore[assignment]
    prefix: Mapping[str, str] = cohorts["prefix"]  # type: ignore[assignment]
    controls = {
        remainder: tuple(
            root + remainder for root in roots
            if root != "sal" and exact_counts.get(root + remainder, 0) > 0
        )
        for remainder in set(prefix.values())
    }
    primary = {
        surface: remainder for surface, remainder in prefix.items()
        if controls[remainder]
    }
    if subset == "NO_SINGLE_SURFACE":
        primary = {
            surface: remainder for surface, remainder in primary.items()
            if all(row["line_pos"] != "SINGLE" for row in by_surface[surface])
        }
    elif subset == "NO_REPEATED_TYPE":
        primary = {
            surface: remainder for surface, remainder in primary.items()
            if len(by_surface[surface]) == 1
        }
    elif subset not in {"ALL", "NO_SINGLE_OCCURRENCE"}:
        raise ValueError(f"unknown subset: {subset}")

    target_surfaces = tuple(sorted(primary))
    output = []
    for surface in target_surfaces:
        remainder = primary[surface]
        values: defaultdict[str, list[float]] = defaultdict(list)
        scored_occurrences = 0
        for target in by_surface[surface]:
            if subset == "NO_SINGLE_OCCURRENCE" and target["line_pos"] == "SINGLE":
                continue
            scored_occurrences += 1
            values["ADDITIVE"].append(_additive_distance(
                target, remainder, by_surface, root_fields,
                remainder_fields, side_balanced,
            ))
            values["ROOT_ONLY"].append(_prototype_distance(
                target, by_surface["sal"], root_fields,
                remainder_fields, side_balanced,
            ))
            values["REMAINDER_ONLY"].append(_prototype_distance(
                target, by_surface[remainder], root_fields,
                remainder_fields, side_balanced,
            ))
            values["FAMILY_LOTO"].append(_type_balanced_distance(
                target,
                tuple(item for item in target_surfaces if item != surface),
                by_surface, root_fields, remainder_fields, side_balanced,
                occurrence_weighted=occurrence_weighted,
            ))
            values["SAME_X_NULL"].append(_type_balanced_distance(
                target, controls[remainder], by_surface, root_fields,
                remainder_fields, side_balanced,
                occurrence_weighted=occurrence_weighted,
            ))
            same_surface = [row for row in by_surface[surface] if row is not target]
            if same_surface:
                exact_whole = _prototype_distance(
                    target, same_surface, root_fields,
                    remainder_fields, side_balanced,
                )
                values["EXACT_WHOLE"].append(exact_whole)
                values["WHOLE_BACKOFF"].append(exact_whole)
            else:
                values["WHOLE_BACKOFF"].append(values["SAME_X_NULL"][-1])
            length_frequency_pool = tuple(
                item for item, count in exact_counts.items()
                if item != surface
                and "sal" not in item
                and len(item) == len(surface)
                and count == exact_counts[surface]
            )
            values["LEN_FREQ_NULL"].append(_type_balanced_distance(
                target, length_frequency_pool, by_surface, root_fields,
                remainder_fields, side_balanced,
                occurrence_weighted=occurrence_weighted,
            ))
        if not scored_occurrences:
            continue
        row: dict[str, object] = {
            "surface": surface,
            "remainder": remainder,
            "surface_exact_occurrences": len(by_surface[surface]),
            "scored_occurrences": scored_occurrences,
            "same_x_control_types": len(controls[remainder]),
            "same_x_control_surfaces": "|".join(controls[remainder]),
        }
        for model, distances in values.items():
            row[f"{model.lower()}_distance"] = statistics.mean(distances)
            row[f"{model.lower()}_similarity"] = 1 - statistics.mean(distances)
        output.append(row)
    return output


def exact_sign_flip_p(differences: Sequence[float]) -> float:
    """One-sided exact P(null-control distance advantage >= observed)."""
    observed = statistics.mean(differences)
    at_least = 0
    for signs in itertools.product((-1, 1), repeat=len(differences)):
        permuted = statistics.mean(
            difference * sign for difference, sign in zip(differences, signs)
        )
        at_least += int(permuted >= observed - 1e-12)
    return at_least / (2 ** len(differences))


def summarize_models(rows: Sequence[Mapping[str, object]]) -> dict[str, object]:
    models = (
        "ADDITIVE", "ROOT_ONLY", "REMAINDER_ONLY", "FAMILY_LOTO",
        "WHOLE_BACKOFF", "SAME_X_NULL", "LEN_FREQ_NULL",
    )
    result: dict[str, object] = {
        "types": len(rows),
        "scored_occurrences": sum(int(row["scored_occurrences"]) for row in rows),
    }
    for model in models:
        distance = statistics.mean(
            float(row[f"{model.lower()}_distance"]) for row in rows
        )
        result[f"{model.lower()}_macro_distance"] = distance
        result[f"{model.lower()}_macro_similarity"] = 1 - distance
    for comparator in ("FAMILY_LOTO", "WHOLE_BACKOFF", "SAME_X_NULL", "LEN_FREQ_NULL"):
        differences = [
            float(row[f"{comparator.lower()}_distance"])
            - float(row["additive_distance"])
            for row in rows
        ]
        leave_one_out = [
            statistics.mean(value for index, value in enumerate(differences) if index != omitted)
            for omitted in range(len(differences))
        ] if len(differences) > 1 else list(differences)
        prefix = comparator.lower()
        result[f"additive_advantage_over_{prefix}"] = statistics.mean(differences)
        result[f"additive_wins_over_{prefix}"] = sum(value > 0 for value in differences)
        result[f"additive_ties_{prefix}"] = sum(value == 0 for value in differences)
        result[f"additive_vs_{prefix}_exact_sign_flip_p"] = exact_sign_flip_p(differences)
        result[f"additive_advantage_over_{prefix}_jackknife_min"] = min(leave_one_out)
        result[f"additive_advantage_over_{prefix}_jackknife_max"] = max(leave_one_out)
    return result


def root_recognition(
    context: Mapping[str, object], cohorts: Mapping[str, object]
) -> tuple[list[dict[str, object]], dict[str, object]]:
    exact_counts: Mapping[str, int] = context["exact_counts"]  # type: ignore[assignment]
    by_surface: Mapping[str, Sequence[Mapping[str, object]]] = context["by_surface"]  # type: ignore[assignment]
    roots: Sequence[str] = cohorts["roots"]  # type: ignore[assignment]
    primary: Mapping[str, str] = cohorts["primary"]  # type: ignore[assignment]
    rows: list[dict[str, object]] = []
    for remainder in sorted(set(primary.values())):
        eligible_roots = tuple(
            root for root in roots if exact_counts.get(root + remainder, 0) > 0
        )
        for actual_root in eligible_roots:
            surface = actual_root + remainder
            distances = {
                candidate: statistics.mean(
                    statistics.mean(
                        gower_fields(target, donor, ROOT_FIELDS)
                        for donor in by_surface[candidate]
                    )
                    for target in by_surface[surface]
                )
                for candidate in eligible_roots
            }
            order = tuple(sorted(eligible_roots, key=lambda item: (distances[item], item)))
            rank = order.index(actual_root) + 1
            normalized_rank = 0.0 if len(order) == 1 else (rank - 1) / (len(order) - 1)
            rows.append({
                "surface": surface,
                "remainder": remainder,
                "actual_root": actual_root,
                "surface_exact_occurrences": len(by_surface[surface]),
                "eligible_roots": "|".join(eligible_roots),
                "eligible_root_count": len(eligible_roots),
                "rank_order": "|".join(order),
                "actual_root_rank": rank,
                "actual_root_normalized_rank": normalized_rank,
                "actual_root_distance": distances[actual_root],
                "candidate_distances": "|".join(
                    f"{candidate}:{distances[candidate]:.12f}" for candidate in order
                ),
                "is_sal_target": int(actual_root == "sal"),
            })
    sal_rows = [row for row in rows if int(row["is_sal_target"])]
    control_rows = [row for row in rows if not int(row["is_sal_target"])]
    if len(sal_rows) != 10 or len(control_rows) != 29:
        raise AssertionError(
            f"expected 10 sal / 29 control recognition cells: {len(sal_rows)}/{len(control_rows)}"
        )
    candidate_sizes = [int(row["eligible_root_count"]) for row in sal_rows]
    observed = statistics.mean(float(row["actual_root_normalized_rank"]) for row in sal_rows)
    states = 0
    at_least_as_good = 0
    at_least_as_bad = 0
    for ranks in itertools.product(*(range(size) for size in candidate_sizes)):
        value = statistics.mean(
            rank / (size - 1) for rank, size in zip(ranks, candidate_sizes)
        )
        states += 1
        at_least_as_good += int(value <= observed + 1e-12)
        at_least_as_bad += int(value >= observed - 1e-12)

    def group_summary(group: Sequence[Mapping[str, object]]) -> dict[str, object]:
        return {
            "cells": len(group),
            "top_1": sum(int(row["actual_root_rank"]) == 1 for row in group),
            "top_2": sum(int(row["actual_root_rank"]) <= 2 for row in group),
            "mean_normalized_rank": statistics.mean(
                float(row["actual_root_normalized_rank"]) for row in group
            ),
            "mean_actual_root_distance": statistics.mean(
                float(row["actual_root_distance"]) for row in group
            ),
        }
    summary = {
        "sal": group_summary(sal_rows),
        "controls": group_summary(control_rows),
        "sal_candidate_sizes": candidate_sizes,
        "rank_null_states": states,
        "sal_exact_p_at_least_as_good": at_least_as_good / states,
        "sal_exact_p_at_least_as_bad": at_least_as_bad / states,
    }
    return rows, summary


def target_rows(
    context: Mapping[str, object], cohorts: Mapping[str, object]
) -> list[dict[str, object]]:
    by_surface: Mapping[str, Sequence[Mapping[str, object]]] = context["by_surface"]  # type: ignore[assignment]
    primary: Mapping[str, str] = cohorts["primary"]  # type: ignore[assignment]
    secondary: Mapping[str, str] = cohorts["secondary"]  # type: ignore[assignment]
    controls: Mapping[str, Sequence[str]] = cohorts["controls"]  # type: ignore[assignment]
    output = []
    for surface, remainder in sorted({**primary, **secondary}.items()):
        for occurrence in by_surface[surface]:
            output.append({
                "surface": surface,
                "remainder": remainder,
                "cohort": "PRIMARY" if surface in primary else "SENSITIVITY_ONLY",
                "page": occurrence["page"],
                "physical_folio": occurrence["physical_folio"],
                "locus": occurrence["locus"],
                "register": "|".join(str(occurrence[field]) for field in ("section", "language", "hand")),
                "line_pos": occurrence["line_pos"],
                "ordinal_over_length": f"{occurrence['ordinal']}/{occurrence['line_length']}",
                "paragraph_start_end_line": f"{occurrence['pstart_line']}/{occurrence['pend_line']}",
                "true_paragraph_start_end": f"{occurrence['true_pstart']}/{occurrence['true_pend']}",
                "left_signature": f"{occurrence['left_status']}/{occurrence['left_len']}/{occurrence['left_freq']}",
                "right_signature": f"{occurrence['right_status']}/{occurrence['right_len']}/{occurrence['right_freq']}",
                "same_x_control_surfaces": "|".join(controls[remainder]) or "NONE",
            })
    if len(output) != 14:
        raise AssertionError(f"expected 14 target occurrences: {len(output)}")
    return output


def control_rows(
    context: Mapping[str, object], cohorts: Mapping[str, object]
) -> list[dict[str, object]]:
    exact_counts: Mapping[str, int] = context["exact_counts"]  # type: ignore[assignment]
    controls: Mapping[str, Sequence[str]] = cohorts["controls"]  # type: ignore[assignment]
    output = []
    for remainder in sorted(EXPECTED_CONTROLS):
        for surface in controls[remainder]:
            output.append({
                "remainder": remainder,
                "surface": surface,
                "root": surface[:-len(remainder)],
                "reader_exact_occurrences": exact_counts[surface],
                "type_weight": 1,
            })
    if len(output) != 29:
        raise AssertionError(f"expected 29 same-X controls: {len(output)}")
    return output


def repeat_coherence(context: Mapping[str, object]) -> dict[str, object]:
    exact_counts: Mapping[str, int] = context["exact_counts"]  # type: ignore[assignment]
    by_surface: Mapping[str, Sequence[Mapping[str, object]]] = context["by_surface"]  # type: ignore[assignment]
    pool = sorted(
        surface for surface, count in exact_counts.items()
        if len(surface) == 4 and count == 2
    )
    distances = {
        surface: split_gower(
            by_surface[surface][0], by_surface[surface][1],
            ROOT_FIELDS, RIGHT_FIELDS,
        )
        for surface in pool
    }
    output: dict[str, object] = {
        "same_length_exact_count_2_pool": len(pool),
        "pool_median_pair_distance": statistics.median(distances.values()),
        "targets": [],
    }
    for surface in ("salo", "saly"):
        distance = distances[surface]
        rank = 1 + sum(value < distance for value in distances.values())
        output["targets"].append({  # type: ignore[union-attr]
            "surface": surface,
            "pair_distance": distance,
            "ascending_distance_rank": rank,
            "pool_size": len(pool),
            "ascending_rank_fraction": rank / len(pool),
        })
    return output


def split_diagnostic(context: Mapping[str, object], cohorts: Mapping[str, object]) -> dict[str, object]:
    by_line: Mapping[str, Sequence[Mapping[str, str]]] = context["by_line"]  # type: ignore[assignment]
    exact: Mapping[tuple[str, int], int] = context["exact"]  # type: ignore[assignment]
    prefix: Mapping[str, str] = cohorts["prefix"]  # type: ignore[assignment]
    forward = []
    reverse = []
    for locus, line in by_line.items():
        for index in range(len(line) - 1):
            left, right = line[index], line[index + 1]
            if not (
                exact[locus, int(left["token_index"])]
                and exact[locus, int(right["token_index"])]
            ):
                continue
            for remainder in set(prefix.values()):
                if left["eva"] == "sal" and right["eva"] == remainder:
                    forward.append((locus, remainder))
                if left["eva"] == remainder and right["eva"] == "sal":
                    reverse.append((locus, remainder))
    return {
        "exact_sal_then_remainder": len(forward),
        "forward_loci": [f"{locus}:{remainder}" for locus, remainder in forward],
        "exact_remainder_then_sal": len(reverse),
        "reverse_loci": [f"{locus}:{remainder}" for locus, remainder in reverse],
    }


def run_geometry_audit() -> dict[str, object]:
    context = reconstruct_guarded()
    cohorts = build_cohorts(context)
    by_surface: Mapping[str, Sequence[Mapping[str, object]]] = context["by_surface"]  # type: ignore[assignment]
    exact_counts: Mapping[str, int] = context["exact_counts"]  # type: ignore[assignment]
    expanded_roots = tuple(sorted(
        surface for surface, count in exact_counts.items()
        if len(surface) == 3 and 20 <= count <= 50
    ))
    if len(expanded_roots) != 17:
        raise AssertionError(f"expanded root sensitivity changed: {expanded_roots}")

    specifications = (
        ("FULL_STRICT", cohorts["roots"], ROOT_FIELDS, RIGHT_FIELDS, False, False, "ALL"),
        ("SIDE_BALANCED", cohorts["roots"], ROOT_FIELDS, RIGHT_FIELDS, True, False, "ALL"),
        ("NO_REGISTER", cohorts["roots"], NO_REGISTER_ROOT_FIELDS, RIGHT_FIELDS, False, False, "ALL"),
        ("PLACEMENT_ONLY", cohorts["roots"], PLACEMENT_ROOT_FIELDS, PLACEMENT_RIGHT_FIELDS, False, False, "ALL"),
        ("FLANK_ONLY", cohorts["roots"], FLANK_ROOT_FIELDS, FLANK_RIGHT_FIELDS, False, False, "ALL"),
        ("EXPANDED_ROOTS_20_50", expanded_roots, ROOT_FIELDS, RIGHT_FIELDS, False, False, "ALL"),
        ("OCCURRENCE_WEIGHTED", cohorts["roots"], ROOT_FIELDS, RIGHT_FIELDS, False, True, "ALL"),
        ("NO_SINGLE_SURFACE", cohorts["roots"], ROOT_FIELDS, RIGHT_FIELDS, False, False, "NO_SINGLE_SURFACE"),
        ("NO_SINGLE_OCCURRENCE", cohorts["roots"], ROOT_FIELDS, RIGHT_FIELDS, False, False, "NO_SINGLE_OCCURRENCE"),
        ("NO_REPEATED_TYPE", cohorts["roots"], ROOT_FIELDS, RIGHT_FIELDS, False, False, "NO_REPEATED_TYPE"),
        ("NO_CHO_ROOT", tuple(root for root in cohorts["roots"] if root != "cho"), ROOT_FIELDS, RIGHT_FIELDS, False, False, "ALL"),
    )
    sensitivity_rows = []
    primary_rows = []
    for name, roots, root_fields, remainder_fields, side_balanced, weighted, subset in specifications:
        rows = model_rows(
            context, cohorts, roots, root_fields, remainder_fields,
            side_balanced, weighted, subset,
        )
        summary = summarize_models(rows)
        sensitivity_rows.append({
            "sensitivity": name,
            "root_pool": "|".join(roots),
            "root_fields": "|".join(root_fields),
            "remainder_fields": "|".join(remainder_fields),
            "side_balanced": int(side_balanced),
            "occurrence_weighted": int(weighted),
            "subset": subset,
            **summary,
        })
        if name == "FULL_STRICT":
            primary_rows = rows

    recognition_rows, recognition_summary = root_recognition(context, cohorts)
    main_summary = next(
        row for row in sensitivity_rows if row["sensitivity"] == "FULL_STRICT"
    )
    expanded_summary = next(
        row for row in sensitivity_rows if row["sensitivity"] == "EXPANDED_ROOTS_20_50"
    )
    no_single_summary = next(
        row for row in sensitivity_rows if row["sensitivity"] == "NO_SINGLE_OCCURRENCE"
    )
    green_gates = {
        "main_same_x_wins_at_least_8_of_10": int(main_summary["additive_wins_over_same_x_null"]) >= 8,
        "main_same_x_exact_sign_flip_p_at_most_0_05": float(main_summary["additive_vs_same_x_null_exact_sign_flip_p"]) <= 0.05,
        "sal_root_top2_at_least_8_of_10": int(recognition_summary["sal"]["top_2"]) >= 8,  # type: ignore[index]
        "sal_root_mean_normalized_rank_below_0_35": float(recognition_summary["sal"]["mean_normalized_rank"]) < 0.35,  # type: ignore[index]
        "expanded_same_x_advantage_positive": float(expanded_summary["additive_advantage_over_same_x_null"]) > 0,
        "no_single_occurrence_same_x_advantage_positive": float(no_single_summary["additive_advantage_over_same_x_null"]) > 0,
    }
    recommendation = (
        "GREEN_PRODUCTIVE_LEFT_CORE"
        if all(green_gates.values())
        else "RED_PRODUCTIVE_LEFT_CORE__YELLOW_FORMAL_STRING_FAMILY_ONLY"
    )
    return {
        "guard": context["guard"],
        "feature_specification": {
            "root_fields": list(ROOT_FIELDS),
            "remainder_fields": list(RIGHT_FIELDS),
            "categorical_distance": "0_EQUAL__1_UNEQUAL",
            "numeric_fields": sorted(NUMERIC_FIELDS),
            "numeric_distance": "ABSOLUTE_DIFFERENCE_ON_0_1_SCALE",
            "primary_weighting": "EQUAL_CONCEPTUAL_FEATURE_WEIGHT",
            "target_weighting": "EQUAL_COMPLETE_SURFACE_TYPE_WEIGHT",
            "same_x_control_weighting": "EQUAL_COMPLETE_SURFACE_TYPE_WEIGHT",
        },
        "targets": target_rows(context, cohorts),
        "same_x_controls": control_rows(context, cohorts),
        "primary_model_rows": primary_rows,
        "primary_model_summary": main_summary,
        "sensitivity_summaries": sensitivity_rows,
        "root_recognition_rows": recognition_rows,
        "root_recognition_summary": recognition_summary,
        "repeat_coherence": repeat_coherence(context),
        "split_diagnostic": split_diagnostic(context, cohorts),
        "green_gates": green_gates,
        "recommendation": recommendation,
        "component_export_credit": 0,
        "confirmed_lexeme": 0,
    }


def compute() -> dict[str, object]:
    """Public runner API: reconstruct guarded sources and return all rows.

    The returned dictionary contains guarded source statistics, the exact
    target/control rows, primary model profiles, root-recognition rows,
    repeated-whole and split diagnostics, every sensitivity summary, and the
    final traffic-light recommendation.  This function has no write side
    effects; the parent ``run.py`` owns artifact and report serialization.
    """
    return run_geometry_audit()


def main() -> int:
    print(json.dumps(compute(), ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
