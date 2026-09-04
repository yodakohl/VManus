#!/usr/bin/env python3
"""Leakage-controlled cross-family profile model for GDT788.

EVA surfaces are opaque complete written forms.  For each of ten independently
observed X rows, this model predicts the external profile of ``Xdal`` from the
three complete sister wholes ``Xal``, ``Xar`` and ``Xdar``::

    P_hat(Xdal) = normalize(clip(P(Xal) + P(Xdar) - P(Xar)))

The comparison is against the corresponding complete ``Xal`` whole, a
form-matched learned-whole control, and an adversarial best whole. Occurrences are reader-exact and are
balanced first by physical folio and then by X type.  All raw ``al/dal/ar/dar``
ending surfaces, provenance-sieve surfaces, quarantined cards, and the full
DAL lineage are excluded from semantic neighbour evidence and learned-whole
donors.  This prevents the hypothesis from scoring against prose descended
from itself.

Similarity scores describe external distributions.  They are not confidence
levels, translations, probabilities, or evidence for EVA letter values.
"""

from __future__ import annotations

import csv
import importlib.util
import itertools
import json
import math
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Mapping, Sequence

sys.dont_write_bytecode = True

G782_REL = Path(
    "experiments/yolo/"
    "gdt782_recurrent_six_target_external_field_adjudication/src/run.py"
)
G734_DICTIONARY_REL = Path(
    "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/"
    "V99R7_1606_COMPLETE_WORD_CONFIDENCE.tsv"
)
G746_REFERENCE_REL = Path(
    "experiments/yolo/gdt746_whole_analogy_distribution_test/artifacts/"
    "CALIBRATION_782_CANDIDATE_KNOWN_SCORES.tsv"
)
G754_PROVENANCE_REL = Path(
    "experiments/yolo/gdt754_active_productive_compound_provenance_sieve/"
    "artifacts/PROVENANCE_SIEVE_172_DECISIONS.tsv"
)
G737_QUARANTINE_REL = Path(
    "experiments/yolo/gdt737_held_body_record_role_transfer/artifacts/"
    "V99R7_HELD_WHOLE_QUARANTINE.tsv"
)

X_ROWS = ("ch", "che", "o", "oke", "ol", "ote", "qo", "qoke", "sh", "she")
TAILS = ("al", "dal", "ar", "dar")
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
SEMANTIC_FIELDS = PROFILE_FIELDS[6:]
LOCAL_FIELDS = PROFILE_FIELDS[1:]
LINEAGE_SOURCES = ("GDT653", "GDT654", "GDT655", "GDT711", "GDT764")
RETIRED_PATIENTS = ("pulver", "samen", "saat", "wurzel", "holz")
AUDIT_AXES = ("AMOUNT", "VALUE", "MATERIAL", "PART", "PREPARATION", "PROCESS", "CLOSE")
AXIS_ORDER = (
    "HOT", "COLD", "DRY", "MOIST", "AMOUNT", "VALUE", "PART",
    "MATERIAL", "PREPARATION", "PROCESS", "CLOSE", "PASS",
    "BEGIN_STAGE", "MIDDLE_STAGE", "END_STAGE", "LEVEL_II", "LEVEL_III",
)


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
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


def _normalized(values: Mapping[str, float]) -> dict[str, float]:
    total = sum(values.values())
    if total <= 0:
        return {}
    return {key: value / total for key, value in values.items()}


def _js_similarity(left: Mapping[str, float], right: Mapping[str, float]) -> float:
    """Return 1-JSD; the caller controls which target-defined fields exist."""
    p, q = _normalized(left), _normalized(right)
    if not p:
        raise AssertionError("target-defined field unexpectedly empty")
    if not q:
        return 0.0
    keys = set(p) | set(q)
    middle = {key: (p.get(key, 0.0) + q.get(key, 0.0)) / 2 for key in keys}

    def divergence(source: Mapping[str, float]) -> float:
        return sum(
            value * math.log2(value / middle[key])
            for key, value in source.items()
            if value > 0
        )

    score = 1.0 - (divergence(p) + divergence(q)) / 2
    return min(1.0, max(0.0, score))


def _profile_scores(
    target: Mapping[str, object],
    candidates: Sequence[Mapping[str, object]],
    fields: Iterable[str],
) -> tuple[list[float] | None, tuple[str, ...]]:
    """Score all candidates on one common, target-defined set of fields.

    A field empty in the target is NA for every model, rather than being
    included selectively for whichever model also happens to be empty.  A
    target-populated field absent from a candidate scores zero.
    """
    defined = tuple(field for field in fields if target[field])
    if not defined:
        return None, ()
    scores = [
        sum(
            _js_similarity(
                target[field],  # type: ignore[arg-type]
                candidate[field],  # type: ignore[arg-type]
            )
            for field in defined
        ) / len(defined)
        for candidate in candidates
    ]
    return scores, defined


def _additive_profile(
    xal: Mapping[str, object],
    xdar: Mapping[str, object],
    xar: Mapping[str, object],
) -> dict[str, dict[str, float]]:
    output: dict[str, dict[str, float]] = {}
    for field in PROFILE_FIELDS:
        first = xal[field]  # type: ignore[assignment]
        measured_part = xdar[field]  # type: ignore[assignment]
        part = xar[field]  # type: ignore[assignment]
        keys = set(first) | set(measured_part) | set(part)
        output[field] = _normalized({
            key: max(
                0.0,
                first.get(key, 0.0)
                + measured_part.get(key, 0.0)
                - part.get(key, 0.0),
            )
            for key in keys
        })
    return output


def _mean_profile(
    profiles: Sequence[Mapping[str, object]],
) -> dict[str, dict[str, float]]:
    if not profiles:
        raise AssertionError("empty learned-whole donor set")
    output: dict[str, dict[str, float]] = {}
    for field in PROFILE_FIELDS:
        keys = set().union(
            *(set(profile[field]) for profile in profiles)  # type: ignore[arg-type]
        )
        output[field] = _normalized({
            key: sum(
                profile[field].get(key, 0.0)  # type: ignore[union-attr]
                for profile in profiles
            ) / len(profiles)
            for key in keys
        })
    return output


def _levenshtein(left: str, right: str) -> int:
    previous = list(range(len(right) + 1))
    for row_number, left_character in enumerate(left, 1):
        current = [row_number]
        for column, right_character in enumerate(right, 1):
            current.append(min(
                current[-1] + 1,
                previous[column] + 1,
                previous[column - 1] + int(left_character != right_character),
            ))
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


def _sign_flip_p(values: Sequence[float]) -> float:
    active = [value for value in values if abs(value) > 1e-12]
    if not active:
        return 1.0
    observed = abs(sum(active))
    extreme = sum(
        abs(sum(sign * value for sign, value in zip(signs, active))) >= observed - 1e-12
        for signs in itertools.product((-1, 1), repeat=len(active))
    )
    return extreme / (1 << len(active))


def compute(repo_root: Path | str) -> dict[str, object]:
    root = Path(repo_root).resolve()
    if not (root / "AGENTS.md").is_file() or not (root / ".git").exists():
        raise RuntimeError(f"not repository root: {root}")
    g782 = _load_module("gdt782_guarded_for_gdt788_model", root / G782_REL)
    by_line, exact, _cross, line_meta, cells, guard = g782.load_context()
    if int(guard["allowed_pages"]) != 179:
        raise AssertionError(f"guard changed: {guard}")
    if any(
        str(token["page"]).startswith("f84")
        for line in by_line.values() for token in line
    ):
        raise AssertionError("sealed f84/f84r row materialised")

    exact_counts: Counter[str] = Counter()
    by_surface: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for locus, line in by_line.items():
        length = len(line)
        meta = line_meta[locus]
        for index, token in enumerate(line):
            if not exact[(locus, int(token["token_index"]))]:
                continue
            surface = str(token["eva"])
            exact_counts[surface] += 1
            ordinal = index + 1

            def status(neighbour: int) -> str:
                if not 0 <= neighbour < length:
                    return "EDGE"
                other = line[neighbour]
                return (
                    "EXACT"
                    if exact[(locus, int(other["token_index"]))]
                    else "NONEXACT"
                )

            by_surface[surface].append({
                "surface": surface,
                "page": str(token["page"]),
                "physical_folio": _physical_folio(str(token["page"])),
                "locus": str(locus),
                "ordinal": ordinal,
                "section": str(token["section"]),
                "language": str(token["language"]),
                "hand": str(token["hand"]),
                "line_position": (
                    "SINGLE" if length == 1 else "FIRST" if ordinal == 1
                    else "LAST" if ordinal == length else "MIDDLE"
                ),
                "norm_pos": 0.5 if length == 1 else (ordinal - 1) / (length - 1),
                "true_paragraph_start": str(int(meta["paragraph_start"] == "1" and ordinal == 1)),
                "true_paragraph_end": str(int(meta["paragraph_end"] == "1" and ordinal == length)),
                "left_status": status(index - 1),
                "right_status": status(index + 1),
            })

    raw_family = {
        str(token["eva"])
        for line in by_line.values() for token in line
        if str(token["eva"]).endswith(TAILS)
    }
    provenance = {
        row["surface"] for row in _read_tsv(root / G754_PROVENANCE_REL)
    }
    quarantine = {
        row["surface"] for row in _read_tsv(root / G737_QUARANTINE_REL)
    }
    dictionary_rows = _read_tsv(root / G734_DICTIONARY_REL)
    lineage = {
        row["surface"] for row in dictionary_rows
        if any(source in row["source_gdts"] for source in LINEAGE_SOURCES)
    }
    base_mask = raw_family | provenance | quarantine
    semantic_mask = base_mask | lineage
    if (len(raw_family), len(provenance), len(quarantine), len(base_mask), len(lineage), len(semantic_mask)) != (742, 172, 82, 958, 55, 996):
        raise AssertionError("semantic leakage-mask contract changed")

    patterns = g782.load_axis_patterns()
    used_axis_surfaces: set[str] = set()

    def positive_axes(locus: str, ordinal: int) -> tuple[str, ...]:
        line = by_line[locus]
        if not 1 <= ordinal <= len(line):
            return ()
        token = line[ordinal - 1]
        if not exact[(locus, int(token["token_index"]))]:
            return ()
        cell = cells[(locus, ordinal)]
        surface = str(cell["surface"])
        meaning = str(cell["v99r7_semantic_value_de"])
        if surface in semantic_mask:
            return ()
        if cell["unknown_v99r7"] != "0":
            return ()
        if not cell["gdt734_confidence_level"].startswith(("W2", "W3")):
            return ()
        if cell["gdt734_composition_semantic_credit"] != "0":
            return ()
        if cell["component_export_credit"] != "0":
            return ()
        if any(patient in meaning.lower() for patient in RETIRED_PATIENTS):
            return ()
        axes = {axis for axis, pattern in patterns.items() if pattern.search(meaning)}
        axes.update(
            axis for axis, pattern in g782.STAGE_PATTERNS.items()
            if pattern.search(meaning)
        )
        selected = tuple(axis for axis in AXIS_ORDER if axis in axes)
        if selected:
            used_axis_surfaces.add(surface)
        return selected

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
                locus, ordinal = str(occurrence["locus"]), int(occurrence["ordinal"])
                progress = float(occurrence["norm_pos"])
                categories = {
                    "register": f"{occurrence['section']}|{occurrence['language']}|{occurrence['hand']}",
                    "line_position": str(occurrence["line_position"]),
                    "line_third": "F" if progress < 1/3 else "M" if progress < 2/3 else "L",
                    "paragraph_boundary": f"{occurrence['true_paragraph_start']}|{occurrence['true_paragraph_end']}",
                    "left_status": str(occurrence["left_status"]),
                    "right_status": str(occurrence["right_status"]),
                }
                for field, category in categories.items():
                    distributions[field][category] += weight
                for field, axes in (
                    ("left_positive_axes", positive_axes(locus, ordinal - 1)),
                    ("right_positive_axes", positive_axes(locus, ordinal + 1)),
                ):
                    for axis in axes:
                        distributions[field][axis] += weight / len(axes)
                close_hits = [
                    delta for delta in (-5, -4, -3, -2, -1, 1, 2, 3, 4, 5)
                    if "CLOSE" in positive_axes(locus, ordinal + delta)
                ]
                if close_hits:
                    distance = min(abs(delta) for delta in close_hits)
                    sides = {"L" if delta < 0 else "R" for delta in close_hits if abs(delta) == distance}
                    side = "B" if len(sides) == 2 else next(iter(sides))
                    band = "1" if distance == 1 else "2" if distance == 2 else "3"
                    distributions["close_proximity"][side + band] += weight
        return {
            **{field: _normalized(values) for field, values in distributions.items()},
            "occurrences": len(occurrences),
            "physical_folios": len(folios),
        }

    reference_universe = {
        row["known_surface"] for row in _read_tsv(root / G746_REFERENCE_REL)
    }
    clean_reference = reference_universe - semantic_mask
    profiles: dict[str, dict[str, object]] = {}
    for surface in sorted(clean_reference):
        profile = build_profile(surface)
        if profile is not None:
            profiles[surface] = profile
    clean_reference = set(profiles)
    if len(reference_universe) != 46 or len(clean_reference) != 32:
        raise AssertionError(
            f"learned-whole reference contract changed: {len(reference_universe)}/{len(clean_reference)}"
        )

    required = {"al", "dal"} | {
        surface for x in X_ROWS for surface in (x + tail for tail in TAILS)
    }
    for surface in sorted(required):
        profile = build_profile(surface)
        if profile is None:
            raise AssertionError(f"required surface absent: {surface}")
        profiles[surface] = profile

    factorial_rows: list[dict[str, object]] = []
    for x in X_ROWS:
        names = {tail: x + tail for tail in TAILS}
        target = profiles[names["dal"]]
        shift = _additive_profile(
            profiles[names["al"]], profiles[names["dar"]], profiles[names["ar"]]
        )
        core = _additive_profile(
            profiles[names["al"]], profiles["dal"], profiles["al"]
        )

        eligible = [
            surface for surface in clean_reference
            if abs(len(surface) - len(names["dal"])) <= 1
            and abs(_frequency_bin(exact_counts[surface]) - _frequency_bin(exact_counts[names["dal"]])) <= 1
        ]
        if not eligible:
            eligible = [
                surface for surface in clean_reference
                if abs(len(surface) - len(names["dal"])) <= 2
            ]
        if not eligible:
            raise AssertionError(f"no learned-whole donor for {x}")
        ranked = sorted(eligible, key=lambda surface: (
            _levenshtein(names["dal"], surface),
            abs(_frequency_bin(exact_counts[surface]) - _frequency_bin(exact_counts[names["dal"]])),
            abs(len(surface) - len(names["dal"])),
            surface,
        ))
        minimum_distance = _levenshtein(names["dal"], ranked[0])
        donors = [
            surface for surface in ranked
            if _levenshtein(names["dal"], surface) == minimum_distance
        ][:3]
        learned = _mean_profile([profiles[surface] for surface in donors])

        candidate_profiles = (shift, core, profiles[names["al"]], learned)
        full_scores, full_fields = _profile_scores(target, candidate_profiles, PROFILE_FIELDS)
        structural_scores, structural_fields = _profile_scores(target, candidate_profiles, STRUCTURAL_FIELDS)
        local_scores, local_fields = _profile_scores(target, candidate_profiles, LOCAL_FIELDS)
        semantic_scores, semantic_fields = _profile_scores(target, candidate_profiles, SEMANTIC_FIELDS)
        if full_scores is None or structural_scores is None or local_scores is None:
            raise AssertionError(f"required model fields absent for {x}")

        adversarial = max(
            (
                _profile_scores(target, (profiles[surface],), PROFILE_FIELDS)[0][0],  # type: ignore[index]
                surface,
            )
            for surface in sorted(clean_reference)
        )
        shift_score, core_score, xal_score, learned_score = full_scores
        factorial_rows.append({
            "x": x,
            "target_surface": names["dal"],
            "target_reader_exact_occurrences": target["occurrences"],
            "target_physical_folios": target["physical_folios"],
            "xal_reader_exact_occurrences": exact_counts[names["al"]],
            "xar_reader_exact_occurrences": exact_counts[names["ar"]],
            "xdar_reader_exact_occurrences": exact_counts[names["dar"]],
            "shift_similarity": shift_score,
            "core_similarity": core_score,
            "xal_similarity": xal_score,
            "learned_whole_similarity": learned_score,
            "learned_whole_min_edit_distance": minimum_distance,
            "learned_whole_donors": "|".join(donors),
            "shift_beats_xal": int(shift_score > xal_score),
            "shift_beats_learned_whole": int(shift_score > learned_score),
            "shift_beats_both": int(shift_score > xal_score and shift_score > learned_score),
            "core_beats_xal": int(core_score > xal_score),
            "core_beats_learned_whole": int(core_score > learned_score),
            "core_beats_both": int(core_score > xal_score and core_score > learned_score),
            "structural_shift_similarity": structural_scores[0],
            "structural_core_similarity": structural_scores[1],
            "structural_xal_similarity": structural_scores[2],
            "structural_learned_whole_similarity": structural_scores[3],
            "local_shift_similarity": local_scores[0],
            "local_core_similarity": local_scores[1],
            "local_xal_similarity": local_scores[2],
            "local_learned_whole_similarity": local_scores[3],
            "semantic_shift_similarity": semantic_scores[0] if semantic_scores else None,
            "semantic_core_similarity": semantic_scores[1] if semantic_scores else None,
            "semantic_xal_similarity": semantic_scores[2] if semantic_scores else None,
            "semantic_learned_whole_similarity": semantic_scores[3] if semantic_scores else None,
            "full_target_defined_fields": "|".join(full_fields),
            "structural_target_defined_fields": "|".join(structural_fields),
            "local_target_defined_fields": "|".join(local_fields),
            "semantic_target_defined_fields": "|".join(semantic_fields) or "NONE",
            "adversarial_best_similarity": adversarial[0],
            "adversarial_best_surface": adversarial[1],
            "shift_beats_adversarial_best": int(shift_score > adversarial[0]),
            "core_beats_adversarial_best": int(core_score > adversarial[0]),
            "score_semantics": "TARGET_DEFINED_FIELD_JENSEN_SHANNON_SIMILARITY_NOT_PROBABILITY",
            "component_export_credit": 0,
        })

    def summarize(
        view: str, shift_key: str, core_key: str, xal_key: str,
        learned_key: str, fields: Sequence[str]
    ) -> dict[str, object]:
        selected = [
            row for row in factorial_rows
            if row[shift_key] is not None and row[core_key] is not None
            and row[xal_key] is not None and row[learned_key] is not None
        ]
        shift = [float(row[shift_key]) for row in selected]
        core = [float(row[core_key]) for row in selected]
        xal = [float(row[xal_key]) for row in selected]
        learned = [float(row[learned_key]) for row in selected]
        return {
            "view": view,
            "profile_fields": "|".join(fields),
            "x_types_total": len(factorial_rows),
            "x_types_informative": len(selected),
            "x_types_na": len(factorial_rows) - len(selected),
            "shift_macro_similarity": sum(shift) / len(shift),
            "core_macro_similarity": sum(core) / len(core),
            "xal_macro_similarity": sum(xal) / len(xal),
            "learned_whole_macro_similarity": sum(learned) / len(learned),
            "shift_beats_xal": sum(a > b for a, b in zip(shift, xal)),
            "shift_beats_learned_whole": sum(a > b for a, b in zip(shift, learned)),
            "shift_beats_both": sum(a > b and a > c for a, b, c in zip(shift, xal, learned)),
            "core_beats_xal": sum(a > b for a, b in zip(core, xal)),
            "core_beats_learned_whole": sum(a > b for a, b in zip(core, learned)),
            "core_beats_both": sum(a > b and a > c for a, b, c in zip(core, xal, learned)),
            "score_semantics": "TARGET_DEFINED_FIELD_JENSEN_SHANNON_SIMILARITY_NOT_PROBABILITY",
        }

    summaries = [
        summarize("FULL", "shift_similarity", "core_similarity", "xal_similarity", "learned_whole_similarity", PROFILE_FIELDS),
        summarize("STRUCTURAL", "structural_shift_similarity", "structural_core_similarity", "structural_xal_similarity", "structural_learned_whole_similarity", STRUCTURAL_FIELDS),
        summarize("LOCAL_NO_REGISTER", "local_shift_similarity", "local_core_similarity", "local_xal_similarity", "local_learned_whole_similarity", LOCAL_FIELDS),
        summarize("SEMANTIC_ONLY", "semantic_shift_similarity", "semantic_core_similarity", "semantic_xal_similarity", "semantic_learned_whole_similarity", SEMANTIC_FIELDS),
    ]

    def axis_rate(surface: str, radius: int, axis: str) -> float:
        folios: defaultdict[str, list[int]] = defaultdict(list)
        for occurrence in by_surface[surface]:
            locus, ordinal = str(occurrence["locus"]), int(occurrence["ordinal"])
            hit = any(
                axis in positive_axes(locus, ordinal + delta)
                for delta in range(-radius, radius + 1) if delta
            )
            folios[str(occurrence["physical_folio"])].append(int(hit))
        return statistics.mean(
            statistics.mean(values) for values in folios.values()
        )

    axis_rows: list[dict[str, object]] = []
    for radius in (1, 3):
        for axis in AUDIT_AXES:
            for x in X_ROWS:
                rates = {
                    tail: axis_rate(x + tail, radius, axis) for tail in TAILS
                }
                informative = any(value > 0 for value in rates.values())
                d_al = rates["dal"] - rates["al"]
                d_ar = rates["dar"] - rates["ar"]
                shared_d = (d_al + d_ar) / 2
                did = d_al - d_ar
                carrier = (
                    rates["al"] + rates["dal"]
                    - rates["ar"] - rates["dar"]
                ) / 2
                aligned_carrier = -carrier if axis == "PART" else carrier
                axis_rows.append({
                    "radius": radius,
                    "axis": axis,
                    "x": x,
                    "informative": int(informative),
                    "xal_rate": rates["al"],
                    "xdal_rate": rates["dal"],
                    "xar_rate": rates["ar"],
                    "xdar_rate": rates["dar"],
                    "dal_minus_al": d_al if informative else None,
                    "dar_minus_ar": d_ar if informative else None,
                    "shared_d_effect": shared_d if informative else None,
                    "difference_in_differences": did if informative else None,
                    "same_nonzero_direction": int(informative and d_al * d_ar > 0),
                    "both_positive_d_effect": int(informative and d_al > 0 and d_ar > 0),
                    "al_carrier_minus_ar_carrier": carrier if informative else None,
                    "axis_aligned_carrier_contrast": aligned_carrier if informative else None,
                    "component_export_credit": 0,
                })

    axis_summaries: list[dict[str, object]] = []
    for radius in (1, 3):
        for axis in AUDIT_AXES:
            selected = [
                row for row in axis_rows
                if row["radius"] == radius and row["axis"] == axis and row["informative"]
            ]
            did = [float(row["difference_in_differences"]) for row in selected]
            shared = [float(row["shared_d_effect"]) for row in selected]
            carrier = [float(row["axis_aligned_carrier_contrast"]) for row in selected]
            axis_summaries.append({
                "radius": radius,
                "axis": axis,
                "type_rows": len(X_ROWS),
                "informative_types": len(selected),
                "na_types": len(X_ROWS) - len(selected),
                "mean_difference_in_differences": statistics.mean(did) if did else None,
                "mean_absolute_difference_in_differences": statistics.mean(abs(value) for value in did) if did else None,
                "same_nonzero_direction_types": sum(int(row["same_nonzero_direction"]) for row in selected),
                "both_positive_d_effect_types": sum(int(row["both_positive_d_effect"]) for row in selected),
                "mean_shared_d_effect": statistics.mean(shared) if shared else None,
                "shared_d_effect_sign_flip_p": _sign_flip_p(shared) if shared else None,
                "mean_axis_aligned_carrier_contrast": statistics.mean(carrier) if carrier else None,
                "carrier_contrast_sign_flip_p": _sign_flip_p(carrier) if carrier else None,
                "score_semantics": "FOLIO_THEN_TYPE_BALANCED_DIRECTIONAL_RATE_NOT_PROBABILITY",
                "component_export_credit": 0,
            })
    primary = summaries[0]
    recommendation = (
        "PORTABLE_REMAINDER_CANDIDATE"
        if max(int(primary["shift_beats_both"]), int(primary["core_beats_both"])) >= 7
        else "WHOLE_ONLY"
    )
    diagnostics = {
        "allowed_pages": int(guard["allowed_pages"]),
        "raw_suffix_family_surfaces_masked": len(raw_family),
        "gdt754_provenance_surfaces_masked": len(provenance),
        "gdt737_quarantine_surfaces_masked": len(quarantine),
        "base_mask_union_surfaces": len(base_mask),
        "dal_lineage_surfaces": len(lineage),
        "dal_lineage_new_surfaces_masked": len(lineage - base_mask),
        "complete_semantic_mask_surfaces": len(semantic_mask),
        "reader_exact_suffix_family_surfaces": sum(
            surface.endswith(TAILS) for surface in exact_counts
        ),
        "reader_exact_suffix_family_occurrences": sum(
            count for surface, count in exact_counts.items() if surface.endswith(TAILS)
        ),
        "reader_exact_dal_surfaces": sum(surface.endswith("dal") for surface in exact_counts),
        "reader_exact_dal_occurrences": sum(count for surface, count in exact_counts.items() if surface.endswith("dal")),
        "reader_exact_dar_surfaces": sum(surface.endswith("dar") for surface in exact_counts),
        "reader_exact_dar_occurrences": sum(count for surface, count in exact_counts.items() if surface.endswith("dar")),
        "reader_exact_al_only_surfaces": sum(surface.endswith("al") and not surface.endswith("dal") for surface in exact_counts),
        "reader_exact_al_only_occurrences": sum(count for surface, count in exact_counts.items() if surface.endswith("al") and not surface.endswith("dal")),
        "reader_exact_ar_only_surfaces": sum(surface.endswith("ar") and not surface.endswith("dar") for surface in exact_counts),
        "reader_exact_ar_only_occurrences": sum(count for surface, count in exact_counts.items() if surface.endswith("ar") and not surface.endswith("dar")),
        "sanitized_axis_wholes_used": len(used_axis_surfaces),
        "used_axis_surfaces_disjoint_from_semantic_mask": int(not (used_axis_surfaces & semantic_mask)),
        "learned_whole_reference_universe": len(reference_universe),
        "learned_whole_reference_surfaces_after_mask": len(clean_reference),
        "primary_x_types": len(factorial_rows),
        "primary_shift_beats_xal": primary["shift_beats_xal"],
        "primary_shift_beats_learned_whole": primary["shift_beats_learned_whole"],
        "primary_shift_beats_both": primary["shift_beats_both"],
        "primary_core_beats_xal": primary["core_beats_xal"],
        "primary_core_beats_learned_whole": primary["core_beats_learned_whole"],
        "primary_core_beats_both": primary["core_beats_both"],
        "primary_shift_macro_similarity": primary["shift_macro_similarity"],
        "primary_core_macro_similarity": primary["core_macro_similarity"],
        "primary_xal_macro_similarity": primary["xal_macro_similarity"],
        "primary_learned_whole_macro_similarity": primary["learned_whole_macro_similarity"],
        "shift_beats_adversarial_best": sum(int(row["shift_beats_adversarial_best"]) for row in factorial_rows),
        "core_beats_adversarial_best": sum(int(row["core_beats_adversarial_best"]) for row in factorial_rows),
        "recommendation": recommendation,
        "component_export_credit": 0,
        "forbidden_f84_or_f84r_materialised": 0,
    }
    profile_rows = []
    for surface in ("al", "dal", *(x + tail for x in X_ROWS for tail in TAILS)):
        profile = profiles[surface]
        pair = (
            None if surface in {"al", "dal"}
            else next((x, tail) for x in X_ROWS for tail in TAILS if surface == x + tail)
        )
        profile_rows.append({
            "surface": surface,
            "profile_role": "BARE_CORE" if surface in {"al", "dal"} else "PRIMARY_LATTICE",
            "prefix": "NONE" if pair is None else pair[0],
            "tail": surface if pair is None else pair[1],
            "reader_exact_occurrences": profile["occurrences"],
            "physical_folios": profile["physical_folios"],
            **{
                field + "_json": json.dumps(profile[field], ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                for field in PROFILE_FIELDS
            },
            "semantic_sources_masked": 1,
            "component_export_credit": 0,
        })
    mask_rows = [{
        "surface": surface,
        "raw_suffix_family": int(surface in raw_family),
        "gdt754_provenance": int(surface in provenance),
        "gdt737_quarantine": int(surface in quarantine),
        "dal_lineage": int(surface in lineage),
        "excluded_from_semantic_neighbours": 1,
        "excluded_from_learned_whole_donors": 1,
        "component_export_credit": 0,
    } for surface in sorted(semantic_mask)]
    control_rows = [{
        "x": row["x"],
        "target_surface": row["target_surface"],
        "learned_whole_donors": row["learned_whole_donors"],
        "learned_whole_min_edit_distance": row["learned_whole_min_edit_distance"],
        "selection_features": "LENGTH|EXACT_FREQUENCY_BIN|LEVENSHTEIN|LEXICAL_TIEBREAK",
        "target_similarity_used_for_selection": 0,
        "semantic_value_used_for_selection": 0,
        "all_donors_outside_996_mask": int(all(
            donor not in semantic_mask
            for donor in str(row["learned_whole_donors"]).split("|")
        )),
        "component_export_credit": 0,
    } for row in factorial_rows]
    return {
        "factorial_rows": factorial_rows,
        "summary_rows": summaries,
        "axis_rows": axis_rows,
        "axis_summary_rows": axis_summaries,
        "profile_rows": profile_rows,
        "mask_rows": mask_rows,
        "control_rows": control_rows,
        "diagnostics": diagnostics,
        "used_axis_surfaces": tuple(sorted(used_axis_surfaces)),
        "by_line": by_line,
        "exact": exact,
        "by_surface": dict(by_surface),
        "exact_counts": exact_counts,
    }


__all__ = ["compute", "X_ROWS", "TAILS"]
