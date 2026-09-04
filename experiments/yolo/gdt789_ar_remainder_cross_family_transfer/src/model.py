#!/usr/bin/env python3
"""Target-masked AR/OR and R/N transfer models for GDT789.

Every input string is a complete EVA surface label.  Arithmetic combines
folio-balanced distributions of observed complete words; it does not parse
EVA characters, assign sounds, or create unseen renderer components.
"""

from __future__ import annotations

import csv
import importlib.util
import itertools
import json
import random
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
G788_MODEL_REL = Path(
    "experiments/yolo/gdt788_dal_remainder_cross_family_transfer/src/model.py"
)
G788_MASK_REL = Path(
    "experiments/yolo/gdt788_dal_remainder_cross_family_transfer/artifacts/"
    "GDT788_996_SEMANTIC_LEAKAGE_MASK.tsv"
)
G734_DICTIONARY_REL = Path(
    "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/"
    "V99R7_1606_COMPLETE_WORD_CONFIDENCE.tsv"
)
G746_REFERENCE_REL = Path(
    "experiments/yolo/gdt746_whole_analogy_distribution_test/artifacts/"
    "CALIBRATION_782_CANDIDATE_KNOWN_SCORES.tsv"
)

SUPPORT_PRIMARY_PREFIXES = (
    "ch", "che", "chok", "chot", "cph", "cth", "k", "l", "lk", "ok",
    "okch", "oke", "ol", "op", "ot", "otch", "ote", "p", "qo", "qok",
    "qoke", "qop", "qot", "r", "s", "sh", "she", "t", "tch", "yk", "yt",
)
ROBUST_PREFIXES = (
    "al", "ch", "che", "cho", "chok", "chot", "ckh", "cph", "cth", "dar",
    "k", "kee", "l", "lch", "lk", "o", "ok", "okch", "oke", "okee", "ol",
    "op", "opch", "or", "ot", "otal", "otch", "ote", "p", "pch", "pche",
    "qo", "qok", "qoke", "qop", "qot", "qotch", "r", "s", "sh", "she",
    "shee", "t", "tch", "yche", "yk", "yt",
)
HISTORICAL_EXCLUSION_PREFIXES = (
    "al", "cho", "chok", "chot", "ckh", "cph", "cth", "dar", "kee", "l",
    "lch", "lk", "okch", "okee", "op", "opch", "or", "otal", "otch", "p",
    "pch", "pche", "qop", "qotch", "r", "s", "shee", "tch", "yche", "yk", "yt",
)
RN12_PREFIXES = ("d", "k", "ok", "ot", "qok", "qot", "s")
RN23_PREFIXES = ("d", "lk", "o", "ok", "ot", "qok")

PROFILE_FIELDS = (
    "register", "line_position", "line_third", "paragraph_boundary",
    "left_status", "right_status", "left_positive_axes", "right_positive_axes",
    "close_proximity", "right_value_binding",
)
STRUCTURAL_FIELDS = PROFILE_FIELDS[:6]
SEMANTIC_FIELDS = PROFILE_FIELDS[6:9]
CONSTRUCTION_FIELDS = ("right_value_binding",)
ROLE_FIELDS = ("line_position", "left_positive_axes", "right_positive_axes", "right_value_binding")
LOCAL_FIELDS = PROFILE_FIELDS[1:]
AUDIT_AXES = ("AMOUNT", "VALUE", "MATERIAL", "PART", "PREPARATION", "PROCESS", "CLOSE")
AXIS_ORDER = (
    "HOT", "COLD", "DRY", "MOIST", "AMOUNT", "VALUE", "PART", "MATERIAL",
    "PREPARATION", "PROCESS", "CLOSE", "PASS", "BEGIN_STAGE", "MIDDLE_STAGE",
    "END_STAGE", "LEVEL_II", "LEVEL_III",
)
MASK_TAILS = ("ar", "or", "an", "ain", "air", "aiin", "aiir", "aiiin")
LINEAGE_SOURCES = ("GDT654", "GDT693", "GDT724", "GDT759", "GDT760", "GDT788")
RETIRED_PATIENTS = ("pulver", "samen", "saat", "wurzel", "holz")
VALUE_SURFACES = {"ain": "II", "aiin": "III", "aiiin": "IV"}


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
    return {} if total <= 0 else {key: value / total for key, value in values.items()}


def _additive_profile(
    base: Mapping[str, object], positive: Mapping[str, object], negative: Mapping[str, object]
) -> dict[str, dict[str, float]]:
    output: dict[str, dict[str, float]] = {}
    for field in PROFILE_FIELDS:
        first = base[field]  # type: ignore[assignment]
        addition = positive[field]  # type: ignore[assignment]
        subtraction = negative[field]  # type: ignore[assignment]
        keys = set(first) | set(addition) | set(subtraction)
        output[field] = _normalized({
            key: max(0.0, first.get(key, 0.0) + addition.get(key, 0.0) - subtraction.get(key, 0.0))
            for key in keys
        })
    return output


def _mean_profile(profiles: Sequence[Mapping[str, object]]) -> dict[str, dict[str, float]]:
    if not profiles:
        raise AssertionError("empty profile set")
    output: dict[str, dict[str, float]] = {}
    for field in PROFILE_FIELDS:
        keys = set().union(*(set(profile[field]) for profile in profiles))  # type: ignore[arg-type]
        output[field] = _normalized({
            key: sum(profile[field].get(key, 0.0) for profile in profiles) / len(profiles)  # type: ignore[union-attr]
            for key in keys
        })
    return output


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


def _folio_bin(value: int) -> int:
    return _frequency_bin(value)


def _levenshtein(left: str, right: str) -> int:
    previous = list(range(len(right) + 1))
    for row_number, left_character in enumerate(left, 1):
        current = [row_number]
        for column, right_character in enumerate(right, 1):
            current.append(min(
                current[-1] + 1,
                previous[column] + 1,
                previous[column - 1] + (left_character != right_character),
            ))
        previous = current
    return previous[-1]


def _sign_flip_p(values: Sequence[float]) -> float:
    active = [value for value in values if abs(value) > 1e-12]
    if not active:
        return 1.0
    observed = abs(sum(active))
    if len(active) <= 20:
        extreme = sum(
            abs(sum(sign * value for sign, value in zip(signs, active))) >= observed - 1e-12
            for signs in itertools.product((-1, 1), repeat=len(active))
        )
        return extreme / (1 << len(active))
    draws = 20000
    seed = 789000 + len(active) * 1000 + int(sum(abs(value) for value in active) * 10**9) % 997
    generator = random.Random(seed)
    extreme = sum(
        abs(sum((1 if generator.getrandbits(1) else -1) * value for value in active)) >= observed - 1e-12
        for _ in range(draws)
    )
    return (extreme + 1) / (draws + 1)


def _sign_flip_method(values: Sequence[float]) -> str:
    active = sum(abs(value) > 1e-12 for value in values)
    return "EXACT_ENUMERATION" if active <= 20 else "FIXED_SEED_20000_MONTE_CARLO"


def compute(repo_root: Path | str) -> dict[str, object]:
    root = Path(repo_root).resolve()
    if not (root / "AGENTS.md").is_file() or not (root / ".git").exists():
        raise RuntimeError(f"not repository root: {root}")
    base = _load_module("gdt782_guarded_for_gdt789_model", root / G782_REL)
    score_tools = _load_module("gdt788_score_tools_for_gdt789", root / G788_MODEL_REL)
    by_line, exact, _cross, line_meta, cells, guard = base.load_context()
    if int(guard["allowed_pages"]) != 179:
        raise AssertionError(f"guard changed: {guard}")
    if any(str(token["page"]).startswith("f84") for line in by_line.values() for token in line):
        raise AssertionError("sealed f84/f84r row materialised")

    exact_counts: Counter[str] = Counter()
    exact_folios: defaultdict[str, set[str]] = defaultdict(set)
    by_surface: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for locus, line in by_line.items():
        length = len(line)
        meta = line_meta[locus]
        for index, token in enumerate(line):
            if not exact[(locus, int(token["token_index"]))]:
                continue
            surface = str(token["eva"])
            folio = _physical_folio(str(token["page"]))
            exact_counts[surface] += 1
            exact_folios[surface].add(folio)
            ordinal = index + 1

            def status(neighbour: int) -> str:
                if not 0 <= neighbour < length:
                    return "EDGE"
                other = line[neighbour]
                return "EXACT" if exact[(locus, int(other["token_index"]))] else "NONEXACT"

            by_surface[surface].append({
                "surface": surface,
                "page": str(token["page"]),
                "physical_folio": folio,
                "locus": str(locus),
                "ordinal": ordinal,
                "section": str(token["section"]),
                "language": str(token["language"]),
                "hand": str(token["hand"]),
                "line_position": "SINGLE" if length == 1 else "FIRST" if ordinal == 1 else "LAST" if ordinal == length else "MIDDLE",
                "norm_pos": 0.5 if length == 1 else (ordinal - 1) / (length - 1),
                "true_paragraph_start": str(int(meta["paragraph_start"] == "1" and ordinal == 1)),
                "true_paragraph_end": str(int(meta["paragraph_end"] == "1" and ordinal == length)),
                "left_status": status(index - 1),
                "right_status": status(index + 1),
            })

    prior_mask = {row["surface"] for row in _read_tsv(root / G788_MASK_REL)}
    raw_tail_union = {
        str(token["eva"])
        for line in by_line.values() for token in line
        if str(token["eva"]).endswith(MASK_TAILS)
    }
    dictionary_rows = _read_tsv(root / G734_DICTIONARY_REL)
    lineage = {
        row["surface"] for row in dictionary_rows
        if any(source in row["source_gdts"] for source in LINEAGE_SOURCES)
    }
    semantic_mask = prior_mask | raw_tail_union | lineage

    patterns = base.load_axis_patterns()
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
        if surface in semantic_mask or cell["unknown_v99r7"] != "0":
            return ()
        if not cell["gdt734_confidence_level"].startswith(("W2", "W3")):
            return ()
        if cell["gdt734_composition_semantic_credit"] != "0" or cell["component_export_credit"] != "0":
            return ()
        if any(patient in meaning.lower() for patient in RETIRED_PATIENTS):
            return ()
        axes = {axis for axis, pattern in patterns.items() if pattern.search(meaning)}
        axes.update(axis for axis, pattern in base.STAGE_PATTERNS.items() if pattern.search(meaning))
        selected = tuple(axis for axis in AXIS_ORDER if axis in axes)
        if selected:
            used_axis_surfaces.add(surface)
        return selected

    profiles: dict[str, dict[str, object]] = {}

    def build_profile(surface: str) -> dict[str, object] | None:
        if surface in profiles:
            return profiles[surface]
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
                line = by_line[locus]
                right = line[ordinal] if ordinal < len(line) else None
                right_value = (
                    VALUE_SURFACES.get(str(right["eva"]), "NONE")
                    if right is not None and exact[(locus, int(right["token_index"]))]
                    else "NONE"
                )
                distributions["right_value_binding"][right_value] += weight
        profile = {
            **{field: _normalized(values) for field, values in distributions.items()},
            "occurrences": len(occurrences),
            "physical_folios": len(folios),
        }
        profiles[surface] = profile
        return profile

    reference_universe = {row["known_surface"] for row in _read_tsv(root / G746_REFERENCE_REL)}
    clean_reference = {
        surface for surface in reference_universe
        if surface not in semantic_mask and exact_counts[surface] > 0
    }
    augmented = set(clean_reference)
    best_dictionary: dict[str, dict[str, str]] = {}
    for row in dictionary_rows:
        surface = row["surface"]
        current = best_dictionary.get(surface)
        if current is None or int(row["working_model_score_0_100_not_probability"] or 0) > int(current["working_model_score_0_100_not_probability"] or 0):
            best_dictionary[surface] = row
    for surface, row in best_dictionary.items():
        meaning = row["v99r7_spoken_default_de"]
        if surface in semantic_mask or not exact_counts[surface]:
            continue
        if not row["working_model_level"].startswith(("W2", "W3")):
            continue
        if row["gdt734_component_export_allowed"] != "0" or row["gdt734_composition_semantic_credit"] != "0":
            continue
        if "HOLD" in row["v99_audit_decision"] or any(patient in meaning.lower() for patient in RETIRED_PATIENTS):
            continue
        augmented.add(surface)

    required = {"ar", "or", "s"}
    required.update(prefix + tail for prefix in ROBUST_PREFIXES for tail in ("ar", "or"))
    required.update(prefix + tail for prefix in RN12_PREFIXES for tail in ("ar", "an", "air", "ain"))
    required.update(prefix + tail for prefix in RN23_PREFIXES for tail in ("air", "ain", "aiir", "aiin"))
    required.update(prefix for prefix in ROBUST_PREFIXES if exact_counts[prefix])
    for surface in sorted(required | augmented):
        build_profile(surface)
    clean_reference = {surface for surface in augmented if surface in profiles}
    if len(clean_reference) < 20:
        raise AssertionError(f"insufficient clean learned-whole pool: {len(clean_reference)}")

    def donor_set(target_surface: str) -> list[str]:
        candidates = sorted(clean_reference, key=lambda surface: (
            abs(len(surface) - len(target_surface)),
            abs(_frequency_bin(exact_counts[surface]) - _frequency_bin(exact_counts[target_surface])),
            abs(_folio_bin(len(exact_folios[surface])) - _folio_bin(len(exact_folios[target_surface]))),
            _levenshtein(target_surface, surface),
            surface,
        ))
        return candidates[:5]

    def scores(target, candidates, fields):
        values, defined = score_tools._profile_scores(target, candidates, fields)
        return values, defined

    primary_rows: list[dict[str, object]] = []
    donor_rows: list[dict[str, object]] = []
    for prefix in ROBUST_PREFIXES:
        target_surface, sister_surface = prefix + "ar", prefix + "or"
        target, sister = profiles[target_surface], profiles[sister_surface]
        additive = _additive_profile(sister, profiles["ar"], profiles["or"])
        donors = donor_set(target_surface)
        learned = _mean_profile([profiles[surface] for surface in donors])
        standalone = profiles.get(prefix)
        candidate_profiles = (additive, sister, learned)
        row: dict[str, object] = {
            "prefix": prefix,
            "target_surface": target_surface,
            "sister_surface": sister_surface,
            "support_primary_31": int(prefix in SUPPORT_PRIMARY_PREFIXES),
            "historical_exclusion_31": int(prefix in HISTORICAL_EXCLUSION_PREFIXES),
            "target_reader_exact_occurrences": target["occurrences"],
            "target_physical_folios": target["physical_folios"],
            "sister_reader_exact_occurrences": sister["occurrences"],
            "sister_physical_folios": sister["physical_folios"],
            "standalone_prefix_available": int(standalone is not None),
            "learned_whole_donors": "|".join(donors),
            "component_export_credit": 0,
        }
        for view, fields in (
            ("full", PROFILE_FIELDS), ("structural", STRUCTURAL_FIELDS),
            ("local", LOCAL_FIELDS), ("semantic", SEMANTIC_FIELDS),
            ("construction", CONSTRUCTION_FIELDS),
        ):
            values, defined = scores(target, candidate_profiles, fields)
            if values is None:
                values = [None, None, None]
            row[f"{view}_add_ar_similarity"] = values[0]
            row[f"{view}_x_or_similarity"] = values[1]
            row[f"{view}_learned_whole_similarity"] = values[2]
            row[f"{view}_target_defined_fields"] = "|".join(defined) or "NONE"
            row[f"{view}_add_beats_x_or"] = int(values[0] is not None and values[0] > values[1])
            row[f"{view}_add_beats_learned"] = int(values[0] is not None and values[0] > values[2])
            row[f"{view}_add_beats_both"] = int(values[0] is not None and values[0] > values[1] and values[0] > values[2])
            if standalone is None:
                row[f"{view}_standalone_x_similarity"] = None
            else:
                standalone_values, _ = scores(target, (standalone,), fields)
                row[f"{view}_standalone_x_similarity"] = standalone_values[0] if standalone_values else None
        adversarial = max(
            (scores(target, (profiles[surface],), PROFILE_FIELDS)[0][0], surface)  # type: ignore[index]
            for surface in sorted(clean_reference)
        )
        row["adversarial_best_similarity"] = adversarial[0]
        row["adversarial_best_surface"] = adversarial[1]
        row["full_add_beats_adversarial"] = int(float(row["full_add_ar_similarity"]) > adversarial[0])
        primary_rows.append(row)
        donor_rows.append({
            "prefix": prefix,
            "target_surface": target_surface,
            "donors": "|".join(donors),
            "donor_count": len(donors),
            "selection_features": "LENGTH|EXACT_FREQUENCY_BIN|PHYSICAL_FOLIO_BIN|LEVENSHTEIN|LEXICAL_TIEBREAK",
            "target_profile_used_for_ranking": 0,
            "semantic_value_used_for_ranking": 0,
            "semantic_eligibility_sanitization": 1,
            "all_donors_outside_mask": int(all(surface not in semantic_mask for surface in donors)),
            "component_export_credit": 0,
        })

    summary_rows: list[dict[str, object]] = []
    cohorts = {
        "SUPPORT_PRIMARY_31": set(SUPPORT_PRIMARY_PREFIXES),
        "HISTORICAL_EXCLUSION_31": set(HISTORICAL_EXCLUSION_PREFIXES),
        "ROBUST_ALL_47": set(ROBUST_PREFIXES),
    }
    for cohort, prefixes in cohorts.items():
        rows = [row for row in primary_rows if row["prefix"] in prefixes]
        for view in ("full", "structural", "local", "semantic", "construction"):
            active = [row for row in rows if row[f"{view}_add_ar_similarity"] is not None]
            summary_rows.append({
                "cohort": cohort,
                "view": view.upper(),
                "prefix_types": len(rows),
                "informative_types": len(active),
                "na_types": len(rows) - len(active),
                "add_ar_macro_similarity": statistics.mean(float(row[f"{view}_add_ar_similarity"]) for row in active),
                "x_or_macro_similarity": statistics.mean(float(row[f"{view}_x_or_similarity"]) for row in active),
                "learned_whole_macro_similarity": statistics.mean(float(row[f"{view}_learned_whole_similarity"]) for row in active),
                "add_beats_x_or": sum(int(row[f"{view}_add_beats_x_or"]) for row in active),
                "add_beats_learned": sum(int(row[f"{view}_add_beats_learned"]) for row in active),
                "add_beats_both": sum(int(row[f"{view}_add_beats_both"]) for row in active),
                "score_semantics": "TARGET_DEFINED_FIELD_JENSEN_SHANNON_SIMILARITY_NOT_PROBABILITY",
                "component_export_credit": 0,
            })

    def axis_rate(surface: str, radius: int, axis: str) -> float:
        folios: defaultdict[str, list[int]] = defaultdict(list)
        for occurrence in by_surface[surface]:
            locus, ordinal = str(occurrence["locus"]), int(occurrence["ordinal"])
            hit = any(axis in positive_axes(locus, ordinal + delta) for delta in range(-radius, radius + 1) if delta)
            folios[str(occurrence["physical_folio"])].append(int(hit))
        return statistics.mean(statistics.mean(values) for values in folios.values())

    axis_rows: list[dict[str, object]] = []
    for radius in (1, 3):
        for axis in AUDIT_AXES:
            for prefix in ROBUST_PREFIXES:
                ar_rate = axis_rate(prefix + "ar", radius, axis)
                or_rate = axis_rate(prefix + "or", radius, axis)
                axis_rows.append({
                    "radius": radius, "axis": axis, "prefix": prefix,
                    "support_primary_31": int(prefix in SUPPORT_PRIMARY_PREFIXES),
                    "historical_exclusion_31": int(prefix in HISTORICAL_EXCLUSION_PREFIXES),
                    "xar_rate": ar_rate, "xor_rate": or_rate,
                    "ar_minus_or": ar_rate - or_rate,
                    "ar_positive": int(ar_rate > or_rate),
                    "or_positive": int(or_rate > ar_rate),
                    "tie": int(abs(ar_rate - or_rate) <= 1e-12),
                    "component_export_credit": 0,
                })

    axis_summary_rows: list[dict[str, object]] = []
    for cohort, prefixes in cohorts.items():
        for radius in (1, 3):
            for axis in AUDIT_AXES:
                rows = [row for row in axis_rows if row["prefix"] in prefixes and row["radius"] == radius and row["axis"] == axis]
                differences = [float(row["ar_minus_or"]) for row in rows]
                axis_summary_rows.append({
                    "cohort": cohort, "radius": radius, "axis": axis,
                    "prefix_types": len(rows),
                    "ar_higher_types": sum(int(row["ar_positive"]) for row in rows),
                    "or_higher_types": sum(int(row["or_positive"]) for row in rows),
                    "tie_types": sum(int(row["tie"]) for row in rows),
                    "mean_ar_minus_or": statistics.mean(differences),
                    "median_ar_minus_or": statistics.median(differences),
                    "sign_flip_p": _sign_flip_p(differences),
                    "sign_flip_method": _sign_flip_method(differences),
                    "score_semantics": "FOLIO_THEN_TYPE_BALANCED_AXIS_RATE_NOT_PROBABILITY",
                    "component_export_credit": 0,
                })

    construction_rows = []
    for prefix in ROBUST_PREFIXES:
        for family, surface in (("AR", prefix + "ar"), ("OR", prefix + "or")):
            occurrences = by_surface[surface]
            per_folio: defaultdict[str, list[str]] = defaultdict(list)
            for occurrence in occurrences:
                locus, ordinal = str(occurrence["locus"]), int(occurrence["ordinal"])
                line = by_line[locus]
                right = line[ordinal] if ordinal < len(line) else None
                value = (
                    VALUE_SURFACES.get(str(right["eva"]), "NONE")
                    if right is not None and exact[(locus, int(right["token_index"]))]
                    else "NONE"
                )
                per_folio[str(occurrence["physical_folio"])].append(value)
            bound = sum(value != "NONE" for values in per_folio.values() for value in values)
            total = sum(len(values) for values in per_folio.values())
            balanced_rate = statistics.mean(
                sum(value != "NONE" for value in values) / len(values) for values in per_folio.values()
            )
            levels = Counter(value for values in per_folio.values() for value in values if value != "NONE")
            construction_rows.append({
                "prefix": prefix, "surface": surface, "family": family,
                "support_primary_31": int(prefix in SUPPORT_PRIMARY_PREFIXES),
                "historical_exclusion_31": int(prefix in HISTORICAL_EXCLUSION_PREFIXES),
                "reader_exact_occurrences": total,
                "physical_folios": len(per_folio),
                "immediate_right_value_occurrences": bound,
                "folio_balanced_right_value_rate": balanced_rate,
                "level_ii": levels["II"], "level_iii": levels["III"], "level_iv": levels["IV"],
                "specific_unit_identity_supported": 0,
                "component_export_credit": 0,
            })

    def rn_rows(prefixes: Sequence[str], tails: Sequence[str], target_tail: str, base_tail: str, positive_tail: str, negative_tail: str, cohort: str):
        output = []
        for prefix in prefixes:
            target_surface = prefix + target_tail
            target = profiles[target_surface]
            additive = _additive_profile(profiles[prefix + base_tail], profiles[prefix + positive_tail], profiles[prefix + negative_tail])
            controls = (profiles[prefix + base_tail], profiles[prefix + positive_tail])
            donors = donor_set(target_surface)
            learned = _mean_profile([profiles[surface] for surface in donors])
            candidates = (additive, controls[0], controls[1], learned)
            row: dict[str, object] = {
                "cohort": cohort, "prefix": prefix, "target_surface": target_surface,
                "formula": f"{prefix + base_tail}+{prefix + positive_tail}-{prefix + negative_tail}",
                "target_occurrences": target["occurrences"], "target_physical_folios": target["physical_folios"],
                "learned_whole_donors": "|".join(donors), "component_export_credit": 0,
            }
            for view, fields in (("full", PROFILE_FIELDS), ("structural", STRUCTURAL_FIELDS), ("semantic", SEMANTIC_FIELDS), ("construction", CONSTRUCTION_FIELDS)):
                values, defined = scores(target, candidates, fields)
                if values is None:
                    values = [None] * 4
                row[f"{view}_add_similarity"] = values[0]
                row[f"{view}_base_similarity"] = values[1]
                row[f"{view}_positive_similarity"] = values[2]
                row[f"{view}_learned_similarity"] = values[3]
                row[f"{view}_add_beats_all"] = int(values[0] is not None and values[0] > max(values[1:]))
                row[f"{view}_fields"] = "|".join(defined) or "NONE"
            output.append(row)
        return output

    rn_rows_all = rn_rows(RN12_PREFIXES, ("ar", "an", "air", "ain"), "ar", "an", "air", "ain", "RN12")
    rn_rows_all += rn_rows(RN23_PREFIXES, ("air", "ain", "aiir", "aiin"), "aiir", "aiin", "air", "ain", "RN23")
    rn_summary_rows = []
    for cohort in ("RN12", "RN23"):
        rows = [row for row in rn_rows_all if row["cohort"] == cohort]
        for view in ("full", "structural", "semantic", "construction"):
            active = [row for row in rows if row[f"{view}_add_similarity"] is not None]
            rn_summary_rows.append({
                "cohort": cohort, "view": view.upper(), "prefix_types": len(rows),
                "informative_types": len(active), "na_types": len(rows) - len(active),
                "add_beats_all": sum(int(row[f"{view}_add_beats_all"]) for row in active),
                "add_macro_similarity": statistics.mean(float(row[f"{view}_add_similarity"]) for row in active),
                "base_macro_similarity": statistics.mean(float(row[f"{view}_base_similarity"]) for row in active),
                "positive_macro_similarity": statistics.mean(float(row[f"{view}_positive_similarity"]) for row in active),
                "learned_macro_similarity": statistics.mean(float(row[f"{view}_learned_similarity"]) for row in active),
                "component_export_credit": 0,
            })

    role_classes = ("PART", "AMOUNT", "VALUE")
    anchor_groups: defaultdict[str, list[str]] = defaultdict(list)
    anchor_meanings: dict[str, str] = {}
    for surface in sorted(clean_reference):
        row = best_dictionary.get(surface)
        if row is None:
            continue
        meaning = row["v99r7_spoken_default_de"]
        roles = [role for role in role_classes if patterns[role].search(meaning)]
        if len(roles) != 1:
            continue
        anchor_groups[roles[0]].append(surface)
        anchor_meanings[surface] = meaning
    if any(len(anchor_groups[role]) < 5 for role in role_classes):
        raise AssertionError(f"insufficient role anchors: {dict(anchor_groups)}")

    def role_centroids(exclude: str | None = None) -> dict[str, dict[str, dict[str, float]]]:
        return {
            role: _mean_profile([
                profiles[surface] for surface in anchor_groups[role] if surface != exclude
            ])
            for role in role_classes
        }

    prototype_rows = []
    correct_by_role = Counter()
    total_by_role = Counter()
    for actual_role in role_classes:
        for surface in anchor_groups[actual_role]:
            centroids = role_centroids(surface)
            values, defined = scores(
                profiles[surface], tuple(centroids[role] for role in role_classes), ROLE_FIELDS
            )
            if values is None:
                raise AssertionError(f"role anchor has no fields: {surface}")
            predicted = role_classes[max(range(len(values)), key=lambda index: (values[index], -index))]
            total_by_role[actual_role] += 1
            correct_by_role[actual_role] += int(predicted == actual_role)
            prototype_rows.append({
                "surface": surface,
                "working_meaning_de": anchor_meanings[surface],
                "actual_working_role": actual_role,
                "part_similarity": values[0],
                "amount_similarity": values[1],
                "value_similarity": values[2],
                "predicted_working_role": predicted,
                "correct": int(predicted == actual_role),
                "fields": "|".join(defined),
                "anchor_meanings_are_working_defaults_not_plaintext": 1,
                "component_export_credit": 0,
            })
    recall = {
        role: correct_by_role[role] / total_by_role[role] for role in role_classes
    }
    balanced_accuracy = statistics.mean(recall.values())
    selector_usable = int(balanced_accuracy >= 0.5 and min(recall.values()) >= 0.5)
    prototype_summary_rows = [{
        "role": role,
        "anchor_surfaces": total_by_role[role],
        "loo_correct": correct_by_role[role],
        "loo_recall": recall[role],
        "balanced_accuracy_all_roles": balanced_accuracy,
        "semantic_selector_usable": selector_usable,
        "score_semantics": "LEAVE_ONE_SURFACE_OUT_WORKING_ROLE_PROFILE_NOT_PLAINTEXT",
        "component_export_credit": 0,
    } for role in role_classes]

    fixed_centroids = role_centroids()
    role_targets = ["ar", "or", "s"] + sorted({
        prefix + tail for prefix in ROBUST_PREFIXES for tail in ("ar", "or")
    })
    target_role_rows = []
    for surface in role_targets:
        profile = build_profile(surface)
        if profile is None:
            continue
        values, defined = scores(
            profile, tuple(fixed_centroids[role] for role in role_classes), ROLE_FIELDS
        )
        if values is None:
            raise AssertionError(f"role target has no fields: {surface}")
        predicted = role_classes[max(range(len(values)), key=lambda index: (values[index], -index))]
        ordered = sorted(values, reverse=True)
        target_role_rows.append({
            "surface": surface,
            "target_class": "BARE_CONTROL" if surface in {"ar", "or", "s"} else "AR_OR_LATTICE",
            "part_similarity": values[0],
            "amount_similarity": values[1],
            "value_similarity": values[2],
            "predicted_working_role": predicted,
            "winning_margin": ordered[0] - ordered[1],
            "selector_usable": selector_usable,
            "fields": "|".join(defined),
            "working_role_only_not_translation": 1,
            "component_export_credit": 0,
        })
    bare_ar_role = next(row for row in target_role_rows if row["surface"] == "ar")

    mask_rows = [{
        "surface": surface,
        "gdt788_prior_mask": int(surface in prior_mask),
        "ar_or_rn_tail_union": int(surface in raw_tail_union),
        "ar_lineage": int(surface in lineage),
        "excluded_from_semantic_neighbours": 1,
        "excluded_from_learned_whole_donors": 1,
        "component_export_credit": 0,
    } for surface in sorted(semantic_mask)]
    profile_rows = []
    profile_required = {"ar", "or"} | {prefix + tail for prefix in ROBUST_PREFIXES for tail in ("ar", "or")}
    for surface in sorted(profile_required):
        profile = profiles[surface]
        profile_rows.append({
            "surface": surface,
            "profile_role": "BARE_CORE" if surface in {"ar", "or"} else "AR_OR_LATTICE",
            "reader_exact_occurrences": profile["occurrences"],
            "physical_folios": profile["physical_folios"],
            **{field + "_json": json.dumps(profile[field], ensure_ascii=False, sort_keys=True, separators=(",", ":")) for field in PROFILE_FIELDS},
            "semantic_sources_masked": 1,
            "component_export_credit": 0,
        })

    support_full = next(row for row in summary_rows if row["cohort"] == "SUPPORT_PRIMARY_31" and row["view"] == "FULL")
    exclusion_full = next(row for row in summary_rows if row["cohort"] == "HISTORICAL_EXCLUSION_31" and row["view"] == "FULL")
    support_semantic = next(row for row in summary_rows if row["cohort"] == "SUPPORT_PRIMARY_31" and row["view"] == "SEMANTIC")
    support_structural = next(row for row in summary_rows if row["cohort"] == "SUPPORT_PRIMARY_31" and row["view"] == "STRUCTURAL")
    rn12_full = next(row for row in rn_summary_rows if row["cohort"] == "RN12" and row["view"] == "FULL")
    rn23_full = next(row for row in rn_summary_rows if row["cohort"] == "RN23" and row["view"] == "FULL")
    portable = (
        int(support_full["add_beats_both"]) >= 21
        and int(exclusion_full["add_beats_both"]) >= 21
        and int(rn12_full["add_beats_all"]) >= 5
        and int(rn23_full["add_beats_all"]) >= 4
    )
    if portable:
        recommendation = "PORTABLE_AR_ROLE_CANDIDATE"
    elif int(support_structural["add_beats_both"]) >= 21 and int(support_semantic["add_beats_both"]) < 21:
        recommendation = "AR_OR_SHELL_BOUND"
    else:
        recommendation = "WHOLE_ONLY"
    diagnostics = {
        "allowed_pages": int(guard["allowed_pages"]),
        "gdt788_prior_mask_surfaces": len(prior_mask),
        "raw_tail_union_surfaces": len(raw_tail_union),
        "ar_lineage_surfaces": len(lineage),
        "complete_semantic_mask_surfaces": len(semantic_mask),
        "reference_universe": len(reference_universe),
        "clean_reference_after_mask": len(reference_universe - semantic_mask),
        "augmented_learned_whole_pool": len(clean_reference),
        "positive_axis_surfaces_used": len(used_axis_surfaces),
        "positive_axis_surfaces_disjoint_from_mask": int(not (used_axis_surfaces & semantic_mask)),
        "robust_prefixes": len(ROBUST_PREFIXES),
        "support_primary_prefixes": len(SUPPORT_PRIMARY_PREFIXES),
        "historical_exclusion_prefixes": len(HISTORICAL_EXCLUSION_PREFIXES),
        "support_full_add_beats_both": support_full["add_beats_both"],
        "historical_exclusion_full_add_beats_both": exclusion_full["add_beats_both"],
        "support_semantic_add_beats_both": support_semantic["add_beats_both"],
        "rn12_full_add_beats_all": rn12_full["add_beats_all"],
        "rn23_full_add_beats_all": rn23_full["add_beats_all"],
        "role_anchor_part": len(anchor_groups["PART"]),
        "role_anchor_amount": len(anchor_groups["AMOUNT"]),
        "role_anchor_value": len(anchor_groups["VALUE"]),
        "role_selector_balanced_accuracy": balanced_accuracy,
        "role_selector_part_recall": recall["PART"],
        "bare_ar_profile_role": bare_ar_role["predicted_working_role"],
        "bare_ar_profile_role_margin": bare_ar_role["winning_margin"],
        "role_selector_usable": bare_ar_role["selector_usable"],
        "recommendation": recommendation,
        "component_export_credit": 0,
        "forbidden_f84_or_f84r_materialised": 0,
    }
    return {
        "primary_rows": primary_rows,
        "summary_rows": summary_rows,
        "axis_rows": axis_rows,
        "axis_summary_rows": axis_summary_rows,
        "construction_rows": construction_rows,
        "rn_rows": rn_rows_all,
        "rn_summary_rows": rn_summary_rows,
        "prototype_rows": prototype_rows,
        "prototype_summary_rows": prototype_summary_rows,
        "target_role_rows": target_role_rows,
        "donor_rows": donor_rows,
        "mask_rows": mask_rows,
        "profile_rows": profile_rows,
        "diagnostics": diagnostics,
        "used_axis_surfaces": tuple(sorted(used_axis_surfaces)),
        "exact_counts": exact_counts,
        "by_surface": dict(by_surface),
        "by_line": by_line,
        "exact": exact,
    }


if __name__ == "__main__":
    raise SystemExit("import and call compute(repo_root)")
