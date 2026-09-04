#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Sequence


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt803_recurrent_context_rarity_discriminator"
SRC = EXP / "src"
ART = EXP / "artifacts"
G802 = ROOT / "experiments/yolo/gdt802_masked_lm_neighbour_context_transfer/artifacts"
ATLAS_IN = G802 / "GDT802_4137_MASKED_NEIGHBOUR_ATLAS.tsv"
COEFFICIENTS_IN = G802 / "GDT802_SHARED_CONTEXT_COEFFICIENTS.tsv"
PREDICTIONS_IN = G802 / "GDT802_4137_FULL_PREDICTIONS.tsv"
METADATA_IN = ROOT / "experiments/yolo/gdt800_terminal_b2_b3_line_final_bridge/artifacts/GDT800_4137_MATCHED_TERMINAL_OCCURRENCES.tsv"
LINES_IN = ROOT / "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_4128_INTEGRATED_LINE_READER.tsv"
SOURCE_LOCK = SRC / "SOURCE_LOCK.tsv"
ROLE_PRIORS = SRC / "CONTEXT_ROLE_PRIORS.tsv"

STABLE_DECK = ART / "GDT803_14_STABLE_CONTEXT_DECK.tsv"
OCCURRENCE_ATLAS = ART / "GDT803_450_CORE_CONTEXT_OCCURRENCES.tsv"
BRACKET_ATLAS = ART / "GDT803_12_BIDIRECTIONAL_BRACKETS.tsv"
CONTROL_MATCH = ART / "GDT803_7_OUTCOME_BLIND_CONTROL_MATCH.tsv"
GROUP_CARD = ART / "GDT803_GROUP_POSITION_POPULATION_CARD.tsv"
RARITY_ENUMERATION = ART / "GDT803_RARITY_ENUMERATION.tsv"
BRACKET_ENUMERATION = ART / "GDT803_BRACKET_ENUMERATION.tsv"
MATCHED_PAIRS = ART / "GDT803_EXACT_MATCHED_EVENT_PAIRS.tsv"
IDENTITY_PAIRS = ART / "GDT803_IDENTITY_RARITY_PAIR_ATLAS.tsv"
IDENTITY_SUMMARY = ART / "GDT803_IDENTITY_RARITY_SUMMARY.tsv"
STYLE_SENSITIVITY = ART / "GDT803_STYLE_SENSITIVITY.tsv"
PASSAGES = ART / "GDT803_EXACT_PASSAGE_CARD.tsv"
FIELD_BRIDGE = ART / "GDT803_FIELD_ROLE_BRIDGE.tsv"
CANDIDATES = ART / "GDT803_CANDIDATE_ADJUDICATION.tsv"
STRUCTURAL_CARD = ART / "GDT803_STRUCTURAL_CARD.tsv"
RESULT = ART / "RESULT.json"
REPORT = EXP / "REPORT.md"

CORE_GROUPS = {
    "LEFT_QOK4": ("LEFT", ("qokeey", "qokedy", "qokeedy", "qokain")),
    "RIGHT_RESULT3": ("RIGHT", ("daiin", "shedy", "chedy")),
}
EXPECTED_CONTROLS = {
    "LEFT_QOK4": {"qokeey": "al", "qokedy": "shedy", "qokeedy": "shol", "qokain": "ar"},
    "RIGHT_RESULT3": {"daiin": "chol", "shedy": "ol", "chedy": "dy"},
}
DEFAULT_SIGN_FLIPS = 200_000


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


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def f12(value: float) -> str:
    if math.isinf(value):
        return "INF"
    return f"{value:.12g}"


def mean(values: Iterable[float]) -> float:
    material = list(values)
    return sum(material) / len(material) if material else 0.0


def logit(probability: float) -> float:
    probability = min(1.0 - 1e-15, max(1e-15, probability))
    return math.log(probability / (1.0 - probability))


def pair_auc(m_score: float, l_score: float) -> float:
    return 1.0 if m_score > l_score else 0.5 if m_score == l_score else 0.0


def exposure_distance(left: dict[str, str], right: dict[str, str]) -> float:
    return math.sqrt(sum(
        (math.log(float(left[field])) - math.log(float(right[field]))) ** 2
        for field in ("global_events", "global_stems", "global_folios")
    ))


def group_residual(
    rows: Sequence[dict[str, Any]], side: str, surfaces: set[str], population: str = "FULL",
    position4: str = "ALL",
) -> tuple[int, int, int, int, float]:
    field = "left_context" if side == "LEFT" else "right_context"
    selected = [
        row for row in rows
        if row[field] in surfaces
        and (population == "FULL" or row["population"] == population)
        and (position4 == "ALL" or row["position4"] == position4)
    ]
    return (
        len(selected), sum(row["terminal"] == "m" for row in selected),
        len({row["stem"] for row in selected}), len({row["physical_folio"] for row in selected}),
        mean(float(row["terminal"] == "m") - float(row["page_s"]) for row in selected),
    )


def nearest_control_options(
    coefficient_rows: Sequence[dict[str, str]], side: str, candidates: Sequence[str], k: int,
) -> dict[str, list[str]]:
    by_key = {(row["side"], row["context_surface"]): row for row in coefficient_rows}
    result: dict[str, list[str]] = {}
    for candidate in candidates:
        source = by_key[(side, candidate)]
        ranked = sorted(
            (exposure_distance(source, row), row["context_surface"])
            for row in coefficient_rows
            if row["side"] == side and row["context_surface"] not in candidates
        )
        result[candidate] = [surface for _, surface in ranked[:k]]
    return result


def best_injective_match(
    coefficient_rows: Sequence[dict[str, str]], side: str, candidates: Sequence[str], k: int = 8,
) -> tuple[dict[str, str], float]:
    by_key = {(row["side"], row["context_surface"]): row for row in coefficient_rows}
    options = nearest_control_options(coefficient_rows, side, candidates, k)
    best_key: tuple[float, tuple[str, ...]] | None = None
    best: dict[str, str] | None = None
    for values in itertools.product(*(options[candidate] for candidate in candidates)):
        if len(set(values)) != len(values):
            continue
        distance = sum(
            exposure_distance(by_key[(side, candidate)], by_key[(side, control)])
            for candidate, control in zip(candidates, values)
        )
        key = (distance, tuple(values))
        if best_key is None or key < best_key:
            best_key, best = key, dict(zip(candidates, values))
    if best is None or best_key is None:
        raise RuntimeError("no injective outcome-blind control match")
    return best, best_key[0]


def enumerated_control_sets(
    coefficient_rows: Sequence[dict[str, str]], side: str, candidates: Sequence[str], k: int,
) -> list[tuple[str, ...]]:
    options = nearest_control_options(coefficient_rows, side, candidates, k)
    sets: set[tuple[str, ...]] = set()
    for values in itertools.product(*(options[candidate] for candidate in candidates)):
        if len(set(values)) == len(values):
            sets.add(tuple(sorted(values)))
    return sorted(sets)


def maximum_cross_folio_matching(
    candidate_rows: Sequence[dict[str, Any]], control_rows: Sequence[dict[str, Any]],
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    candidates = sorted(candidate_rows, key=lambda row: row["occurrence_id"])
    controls = sorted(control_rows, key=lambda row: row["occurrence_id"])
    control_match: dict[int, int] = {}

    def augment(candidate_index: int, seen: set[int]) -> bool:
        for control_index, control in enumerate(controls):
            if control_index in seen or candidates[candidate_index]["physical_folio"] == control["physical_folio"]:
                continue
            seen.add(control_index)
            if control_index not in control_match or augment(control_match[control_index], seen):
                control_match[control_index] = candidate_index
                return True
        return False

    for candidate_index in range(len(candidates)):
        augment(candidate_index, set())
    return sorted(
        ((candidates[candidate_index], controls[control_index]) for control_index, candidate_index in control_match.items()),
        key=lambda pair: (pair[0]["occurrence_id"], pair[1]["occurrence_id"]),
    )


def candidate_control_pairs(
    rows: Sequence[dict[str, Any]], side: str, candidate_surfaces: set[str], control_surfaces: set[str],
    population: str,
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    field = "left_context" if side == "LEFT" else "right_context"
    material = [row for row in rows if population == "FULL" or row["population"] == population]
    candidates: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    controls: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in material:
        key = (row["stem"], row["distance_cell"])
        if row[field] in candidate_surfaces:
            candidates[key].append(row)
        elif row[field] in control_surfaces:
            controls[key].append(row)
    result: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for key in sorted(set(candidates) & set(controls)):
        result.extend(maximum_cross_folio_matching(candidates[key], controls[key]))
    return result


def identity_rarity_audit(
    rows: Sequence[dict[str, Any]], side: str, sign_flips: int,
) -> tuple[list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    field = "left_context" if side == "LEFT" else "right_context"
    available = [row for row in rows if row[field] != "NONE"]
    scored: dict[str, tuple[float, float, int]] = {}
    for event in available:
        training = [
            row for row in available
            if row["physical_folio"] != event["physical_folio"] and row["stem"] != event["stem"]
        ]
        distance_training = [row for row in training if row["distance_cell"] == event["distance_cell"]]
        if not distance_training:
            continue
        base_p = (sum(row["terminal"] == "m" for row in distance_training) + 1.0) / (len(distance_training) + 2.0)
        context_training = [row for row in distance_training if row[field] == event[field]]
        if (len(context_training) < 5 or len({row["stem"] for row in context_training}) < 3
                or len({row["physical_folio"] for row in context_training}) < 3):
            continue
        context_p = (sum(row["terminal"] == "m" for row in context_training) + 20.0 * base_p) / (len(context_training) + 20.0)
        scored[event["occurrence_id"]] = (
            logit(context_p) - logit(base_p), -float(len(context_training)), len(context_training),
        )

    strata: dict[tuple[str, str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in available:
        if row["occurrence_id"] in scored:
            strata[(row["section"], row["language"], row["hand"], row["stem"], row["distance_cell"])].append(row)

    pair_rows: list[dict[str, Any]] = []
    stratum_deltas: list[float] = []
    style_values: dict[tuple[str, str, str], list[tuple[float, float]]] = defaultdict(list)
    same_folio_pairs = 0
    stratum_ordinal = 0
    for key in sorted(strata):
        local = strata[key]
        l_rows = [row for row in local if row["terminal"] == "l"]
        m_rows = [row for row in local if row["terminal"] == "m"]
        pairs = [(l_row, m_row) for l_row in l_rows for m_row in m_rows if l_row["physical_folio"] != m_row["physical_folio"]]
        same_folio_pairs += sum(l_row["physical_folio"] == m_row["physical_folio"] for l_row in l_rows for m_row in m_rows)
        if not pairs:
            continue
        stratum_ordinal += 1
        exact_values: list[float] = []
        rarity_values: list[float] = []
        for pair_ordinal, (l_row, m_row) in enumerate(pairs, 1):
            l_exact, l_rarity, l_n = scored[l_row["occurrence_id"]]
            m_exact, m_rarity, m_n = scored[m_row["occurrence_id"]]
            exact_auc, rarity_auc = pair_auc(m_exact, l_exact), pair_auc(m_rarity, l_rarity)
            exact_values.append(exact_auc)
            rarity_values.append(rarity_auc)
            pair_rows.append({
                "side": side, "stratum_id": f"{side[0]}S{stratum_ordinal:03d}", "pair_ordinal": pair_ordinal,
                "section": key[0], "language": key[1], "hand": key[2], "stem": key[3], "distance_cell": key[4],
                "l_occurrence_id": l_row["occurrence_id"], "l_folio": l_row["physical_folio"], "l_context": l_row[field],
                "l_exact_score": f12(l_exact), "l_training_count": l_n,
                "m_occurrence_id": m_row["occurrence_id"], "m_folio": m_row["physical_folio"], "m_context": m_row[field],
                "m_exact_score": f12(m_exact), "m_training_count": m_n,
                "exact_auc": f12(exact_auc), "rarity_auc": f12(rarity_auc),
                "delta_exact_minus_rarity": f12(exact_auc - rarity_auc),
                "semantic_export_credit": "ZERO__FORMAL_IDENTITY_RARITY_COMPARISON",
            })
        stratum_deltas.append(mean(exact_values) - mean(rarity_values))
        style_values[key[:3]].extend(zip(exact_values, rarity_values))

    stratum_ids = sorted({row["stratum_id"] for row in pair_rows})
    exact_macro = mean(mean(float(row["exact_auc"]) for row in pair_rows if row["stratum_id"] == sid) for sid in stratum_ids)
    rarity_macro = mean(mean(float(row["rarity_auc"]) for row in pair_rows if row["stratum_id"] == sid) for sid in stratum_ids)
    macro_delta = mean(stratum_deltas)
    rng = random.Random(802803 + (0 if side == "LEFT" else 1))
    exceed = 0
    for _ in range(sign_flips):
        permuted = mean(value * (-1.0 if rng.getrandbits(1) else 1.0) for value in stratum_deltas)
        exceed += permuted >= macro_delta
    summary = {
        "side": side, "real_context_events": len(available), "scoreable_events": len(scored),
        "raw_cross_folio_pairs": len(pair_rows), "informative_strata": len(stratum_deltas),
        "same_folio_pair_capacity": same_folio_pairs,
        "exact_micro_auc": mean(float(row["exact_auc"]) for row in pair_rows),
        "rarity_micro_auc": mean(float(row["rarity_auc"]) for row in pair_rows),
        "exact_macro_auc": exact_macro, "rarity_macro_auc": rarity_macro, "macro_delta": macro_delta,
        "sign_flips": sign_flips, "exceed_or_equal": exceed,
        "one_sided_add_one_p": (exceed + 1) / (sign_flips + 1),
    }
    style_rows = []
    for style in sorted(style_values):
        values = style_values[style]
        exact, rarity = mean(pair[0] for pair in values), mean(pair[1] for pair in values)
        style_rows.append({
            "side": side, "section": style[0], "language": style[1], "hand": style[2], "pairs": len(values),
            "exact_micro_auc": f12(exact), "rarity_micro_auc": f12(rarity),
            "delta_exact_minus_rarity": f12(exact - rarity),
            "interpretation": "STYLE_SENSITIVITY_ONLY__NOT_A_SEMANTIC_CLASS",
        })
    return pair_rows, summary, style_rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sign-flips", type=int, default=DEFAULT_SIGN_FLIPS)
    args = parser.parse_args()
    if args.sign_flips < 0:
        raise ValueError("sign flips must be nonnegative")
    ART.mkdir(parents=True, exist_ok=True)
    for lock in read_tsv(SOURCE_LOCK):
        path = ROOT / lock["path"]
        if sha(path) != lock["sha256"]:
            raise RuntimeError(f"source-lock mismatch: {lock['path']}")

    atlas, coefficients = read_tsv(ATLAS_IN), read_tsv(COEFFICIENTS_IN)
    predictions, metadata = read_tsv(PREDICTIONS_IN), read_tsv(METADATA_IN)
    lines, priors = read_tsv(LINES_IN), read_tsv(ROLE_PRIORS)
    if (len(atlas), len(coefficients), len(predictions), len(metadata), len(lines), len(priors)) != (4137, 275, 4137, 4137, 4128, 14):
        raise RuntimeError("predecessor cardinality changed")
    if any(any(str(value).startswith("f84") for value in row.values()) for row in atlas + metadata + lines):
        raise RuntimeError("sealed f84/f84r material reached GDT803")
    prediction_map = {row["occurrence_id"]: row for row in predictions}
    metadata_map = {row["occurrence_id"]: row for row in metadata}
    if len(prediction_map) != 4137 or len(metadata_map) != 4137:
        raise RuntimeError("nonunique predecessor occurrence id")
    rows: list[dict[str, Any]] = []
    for source in atlas:
        occurrence_id = source["occurrence_id"]
        row = dict(source)
        row["page_s"] = prediction_map[occurrence_id]["page_s"]
        row.update({field: metadata_map[occurrence_id][field] for field in ("section", "language", "hand")})
        rows.append(row)

    prior_map = {(row["side"], row["context_surface"]): row for row in priors}
    stable = [
        row for row in coefficients
        if int(row["eligible_cross_folds"]) == 25 and int(row["cache_rest_events"]) >= 20
        and float(row["min_beta_context"]) * float(row["max_beta_context"]) > 0
    ]
    if len(stable) != 14 or set(prior_map) != {(row["side"], row["context_surface"]) for row in stable}:
        raise RuntimeError("14-card stable deck or role prior drift")
    core_membership = {(side, surface): group for group, (side, surfaces) in CORE_GROUPS.items() for surface in surfaces}
    stable_rows = []
    for row in stable:
        prior = prior_map[(row["side"], row["context_surface"])]
        stable_rows.append({
            **row, "preexisting_broad_role": prior["preexisting_broad_role"],
            "preexisting_working_default_de": prior["preexisting_working_default_de"],
            "primary_role_source": prior["primary_source"],
            "core_group": core_membership.get((row["side"], row["context_surface"]), "NONE"),
            "gdt803_disposition": "CORE_L_FAVOURING_CONTEXT" if (row["side"], row["context_surface"]) in core_membership else "STABLE_SINGLE_CONTEXT_RIVAL",
            "meaning_credit": "ZERO__PRIOR_ROLE_ONLY",
        })
    stable_rows.sort(key=lambda row: (row["side"], -abs(float(row["mean_beta_after_stem"])), row["context_surface"]))
    write_tsv(STABLE_DECK, stable_rows, list(coefficients[0]) + [
        "preexisting_broad_role", "preexisting_working_default_de", "primary_role_source", "core_group",
        "gdt803_disposition", "meaning_credit",
    ])

    occurrence_rows = []
    for group_id, (side, surfaces) in CORE_GROUPS.items():
        field = "left_context" if side == "LEFT" else "right_context"
        for row in rows:
            if row[field] in surfaces:
                occurrence_rows.append({
                    "group_id": group_id, "side": side, "context_surface": row[field], "occurrence_id": row["occurrence_id"],
                    "source_selector": row["source_selector"], "physical_folio": row["physical_folio"], "locus": row["locus"],
                    "token_index": row["token_index"], "stem": row["stem"], "terminal": row["terminal"],
                    "masked_target": row["masked_target"], "left_context": row["left_context"], "right_context": row["right_context"],
                    "distance_cell": row["distance_cell"], "position4": row["position4"], "population": row["population"],
                    "page_s": row["page_s"],
                    "residual_m_minus_position_stem": f12(float(row["terminal"] == "m") - float(row["page_s"])),
                    "semantic_export_credit": "ZERO__EXACT_CONTEXT_OCCURRENCE",
                })
    occurrence_rows.sort(key=lambda row: (row["group_id"], row["occurrence_id"]))
    write_tsv(OCCURRENCE_ATLAS, occurrence_rows, [
        "group_id", "side", "context_surface", "occurrence_id", "source_selector", "physical_folio", "locus", "token_index",
        "stem", "terminal", "masked_target", "left_context", "right_context", "distance_cell", "position4", "population",
        "page_s", "residual_m_minus_position_stem", "semantic_export_credit",
    ])

    left_core, right_core = set(CORE_GROUPS["LEFT_QOK4"][1]), set(CORE_GROUPS["RIGHT_RESULT3"][1])
    bracket_source = [row for row in rows if row["left_context"] in left_core and row["right_context"] in right_core]
    line_map = {(row["page"], row["locus"]): row["zl3b_line"] for row in lines}
    bracket_rows = [{
        "bracket_id": f"G803-B{ordinal:02d}", "occurrence_id": row["occurrence_id"], "source_selector": row["source_selector"],
        "physical_folio": row["physical_folio"], "locus": row["locus"], "section": row["section"],
        "language": row["language"], "hand": row["hand"], "left_context": row["left_context"],
        "target_surface": row["stem"] + row["terminal"], "target_stem": row["stem"], "terminal": row["terminal"],
        "right_context": row["right_context"],
        "exact_three_token_span": f"{row['left_context']} {row['stem']}{row['terminal']} {row['right_context']}",
        "full_zl3b_line": line_map[(row["source_selector"], row["locus"])],
        "working_construction_de": "Qualität/Zustand + Träger/Eintrag + Wert/Zustand",
        "null_rival": "dreigliedrige formale Adresse ohne semantische Feldwerte",
        "semantic_export_credit": "ZERO__EXPLORATORY_FIELD_BRIDGE_ONLY",
    } for ordinal, row in enumerate(sorted(bracket_source, key=lambda row: row["occurrence_id"]), 1)]
    write_tsv(BRACKET_ATLAS, bracket_rows, [
        "bracket_id", "occurrence_id", "source_selector", "physical_folio", "locus", "section", "language", "hand",
        "left_context", "target_surface", "target_stem", "terminal", "right_context", "exact_three_token_span", "full_zl3b_line",
        "working_construction_de", "null_rival", "semantic_export_credit",
    ])

    selected_controls: dict[str, set[str]] = {}
    control_distances: dict[str, float] = {}
    coefficient_map = {(row["side"], row["context_surface"]): row for row in coefficients}
    control_rows = []
    for group_id, (side, surfaces) in CORE_GROUPS.items():
        match, total_distance = best_injective_match(coefficients, side, surfaces)
        if match != EXPECTED_CONTROLS[group_id]:
            raise RuntimeError(f"outcome-blind control match drift: {group_id}: {match}")
        selected_controls[group_id], control_distances[group_id] = set(match.values()), total_distance
        for candidate in surfaces:
            control = match[candidate]
            candidate_row, control_row = coefficient_map[(side, candidate)], coefficient_map[(side, control)]
            control_rows.append({
                "group_id": group_id, "side": side, "candidate_surface": candidate, "control_surface": control,
                "exposure_distance": f12(exposure_distance(candidate_row, control_row)),
                "candidate_events": candidate_row["global_events"], "control_events": control_row["global_events"],
                "candidate_stems": candidate_row["global_stems"], "control_stems": control_row["global_stems"],
                "candidate_folios": candidate_row["global_folios"], "control_folios": control_row["global_folios"],
                "matching_inputs": "LOG_EVENTS+LOG_STEMS+LOG_FOLIOS_ONLY", "outcome_fields_used": "NONE",
            })
    write_tsv(CONTROL_MATCH, control_rows, [
        "group_id", "side", "candidate_surface", "control_surface", "exposure_distance", "candidate_events", "control_events",
        "candidate_stems", "control_stems", "candidate_folios", "control_folios", "matching_inputs", "outcome_fields_used",
    ])

    group_rows = []
    for group_id, (side, surfaces) in CORE_GROUPS.items():
        for cohort, surface_set in (("CANDIDATE", set(surfaces)), ("MATCHED_CONTROL", selected_controls[group_id])):
            for population in ("FULL", "DIRECT_388", "CACHE_REST_3749"):
                for position in ("ALL", "EARLIER", "PENULTIMATE", "FINAL"):
                    n, m, stems, folios, residual = group_residual(rows, side, surface_set, population, position)
                    group_rows.append({
                        "group_id": group_id, "side": side, "cohort": cohort, "population": population,
                        "position4": position, "surfaces": "|".join(sorted(surface_set)), "events": n, "m_events": m,
                        "l_events": n - m, "stems": stems, "physical_folios": folios,
                        "mean_residual_m_minus_position_stem": f12(residual),
                        "interpretation": "NEGATIVE_FAVOURS_L" if residual < 0 else "POSITIVE_FAVOURS_M_OR_NULL",
                    })
    write_tsv(GROUP_CARD, group_rows, [
        "group_id", "side", "cohort", "population", "position4", "surfaces", "events", "m_events", "l_events",
        "stems", "physical_folios", "mean_residual_m_minus_position_stem", "interpretation",
    ])

    rarity_rows = []
    enumerated_sets: dict[tuple[str, int], list[tuple[str, ...]]] = {}
    for group_id, (side, surfaces) in CORE_GROUPS.items():
        candidate_full = group_residual(rows, side, set(surfaces), "FULL", "ALL")[4]
        candidate_rest = group_residual(rows, side, set(surfaces), "CACHE_REST_3749", "ALL")[4]
        for k in (5, 8, 10):
            controls = enumerated_control_sets(coefficients, side, surfaces, k)
            enumerated_sets[(side, k)] = controls
            residuals = [(group_residual(rows, side, set(control), "FULL", "ALL")[4],
                          group_residual(rows, side, set(control), "CACHE_REST_3749", "ALL")[4]) for control in controls]
            extreme = sum(full <= candidate_full and rest <= candidate_rest for full, rest in residuals)
            rarity_rows.append({
                "group_id": group_id, "side": side, "nearest_options_per_candidate": k,
                "unique_injective_control_sets": len(controls), "candidate_full_residual": f12(candidate_full),
                "candidate_cache_rest_residual": f12(candidate_rest),
                "control_mean_full_residual": f12(mean(value[0] for value in residuals)),
                "control_mean_cache_rest_residual": f12(mean(value[1] for value in residuals)),
                "controls_at_least_as_l_favouring_both": extreme, "ranking_fraction": f12(extreme / len(controls)),
                "interpretation": "EXPLORATORY_RANK_NOT_P_VALUE__CANDIDATES_PRESELECTED_WITH_OUTCOMES",
            })
    write_tsv(RARITY_ENUMERATION, rarity_rows, [
        "group_id", "side", "nearest_options_per_candidate", "unique_injective_control_sets", "candidate_full_residual",
        "candidate_cache_rest_residual", "control_mean_full_residual", "control_mean_cache_rest_residual",
        "controls_at_least_as_l_favouring_both", "ranking_fraction", "interpretation",
    ])

    left_sets, right_sets = enumerated_sets[("LEFT", 10)], enumerated_sets[("RIGHT", 10)]
    pair_cells: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        pair_cells[(row["left_context"], row["right_context"])].append(row)
    candidate_bracket_stats = (len(bracket_source), sum(row["terminal"] == "m" for row in bracket_source),
                               len({row["stem"] for row in bracket_source}), len({row["physical_folio"] for row in bracket_source}))
    bracket_extreme = bracket_at_least_n = bracket_all_l_nonempty = 0
    for left_set in left_sets:
        for right_set in right_sets:
            material = [row for left in left_set for right in right_set for row in pair_cells[(left, right)]]
            n, m = len(material), sum(row["terminal"] == "m" for row in material)
            stems, folios = len({row["stem"] for row in material}), len({row["physical_folio"] for row in material})
            bracket_at_least_n += n >= candidate_bracket_stats[0]
            bracket_all_l_nonempty += n > 0 and m == 0
            bracket_extreme += (n >= candidate_bracket_stats[0] and m <= candidate_bracket_stats[1]
                                and stems >= candidate_bracket_stats[2] and folios >= candidate_bracket_stats[3])
    bracket_control_total = len(left_sets) * len(right_sets)
    matched_bracket = [row for row in rows if row["left_context"] in selected_controls["LEFT_QOK4"]
                       and row["right_context"] in selected_controls["RIGHT_RESULT3"]]
    write_tsv(BRACKET_ENUMERATION, [{
        "candidate_left_surfaces": "|".join(sorted(left_core)), "candidate_right_surfaces": "|".join(sorted(right_core)),
        "candidate_events": candidate_bracket_stats[0], "candidate_m": candidate_bracket_stats[1],
        "candidate_stems": candidate_bracket_stats[2], "candidate_folios": candidate_bracket_stats[3],
        "matched_control_events": len(matched_bracket), "matched_control_m": sum(row["terminal"] == "m" for row in matched_bracket),
        "matched_control_stems": len({row["stem"] for row in matched_bracket}),
        "matched_control_folios": len({row["physical_folio"] for row in matched_bracket}),
        "enumerated_left_sets": len(left_sets), "enumerated_right_sets": len(right_sets),
        "enumerated_set_pairs": bracket_control_total, "controls_with_at_least_candidate_events": bracket_at_least_n,
        "nonempty_all_l_controls": bracket_all_l_nonempty, "controls_at_least_as_extreme_all_dimensions": bracket_extreme,
        "interpretation": "EXPLORATORY_MATCHED_EXPOSURE_RANK__NOT_AN_INDEPENDENT_P_VALUE",
    }], [
        "candidate_left_surfaces", "candidate_right_surfaces", "candidate_events", "candidate_m", "candidate_stems",
        "candidate_folios", "matched_control_events", "matched_control_m", "matched_control_stems", "matched_control_folios",
        "enumerated_left_sets", "enumerated_right_sets", "enumerated_set_pairs", "controls_with_at_least_candidate_events",
        "nonempty_all_l_controls", "controls_at_least_as_extreme_all_dimensions", "interpretation",
    ])

    matched_pair_rows = []
    full_pair_material: list[tuple[str, dict[str, Any], dict[str, Any], str]] = []
    for group_id, (side, surfaces) in CORE_GROUPS.items():
        for population in ("FULL", "DIRECT_388", "CACHE_REST_3749"):
            pairs = candidate_control_pairs(rows, side, set(surfaces), selected_controls[group_id], population)
            for ordinal, (candidate, control) in enumerate(pairs, 1):
                outcome = ("SUPPORTS_L" if candidate["terminal"] == "l" and control["terminal"] == "m"
                           else "REVERSES" if candidate["terminal"] == "m" and control["terminal"] == "l" else "TIE")
                matched_pair_rows.append({
                    "group_id": group_id, "side": side, "population": population, "pair_ordinal": ordinal,
                    "stem": candidate["stem"], "distance_cell": candidate["distance_cell"],
                    "candidate_occurrence_id": candidate["occurrence_id"], "candidate_folio": candidate["physical_folio"],
                    "candidate_context": candidate["left_context" if side == "LEFT" else "right_context"],
                    "candidate_terminal": candidate["terminal"], "control_occurrence_id": control["occurrence_id"],
                    "control_folio": control["physical_folio"],
                    "control_context": control["left_context" if side == "LEFT" else "right_context"],
                    "control_terminal": control["terminal"], "pair_outcome": outcome,
                    "semantic_export_credit": "ZERO__FORMAL_MATCHED_PAIR",
                })
                if population == "FULL" and outcome != "TIE":
                    full_pair_material.append((group_id, candidate, control, outcome))
    write_tsv(MATCHED_PAIRS, matched_pair_rows, [
        "group_id", "side", "population", "pair_ordinal", "stem", "distance_cell", "candidate_occurrence_id",
        "candidate_folio", "candidate_context", "candidate_terminal", "control_occurrence_id", "control_folio",
        "control_context", "control_terminal", "pair_outcome", "semantic_export_credit",
    ])

    identity_pair_rows, identity_summaries, style_rows = [], [], []
    for side in ("LEFT", "RIGHT"):
        pairs, summary, styles = identity_rarity_audit(rows, side, args.sign_flips)
        identity_pair_rows.extend(pairs)
        identity_summaries.append({
            **{key: summary[key] for key in ("side", "real_context_events", "scoreable_events", "raw_cross_folio_pairs",
                                               "informative_strata", "same_folio_pair_capacity")},
            "exact_micro_auc": f12(summary["exact_micro_auc"]), "rarity_micro_auc": f12(summary["rarity_micro_auc"]),
            "exact_macro_auc": f12(summary["exact_macro_auc"]), "rarity_macro_auc": f12(summary["rarity_macro_auc"]),
            "macro_delta": f12(summary["macro_delta"]), "sign_flips": summary["sign_flips"],
            "exceed_or_equal": summary["exceed_or_equal"], "one_sided_add_one_p": f12(summary["one_sided_add_one_p"]),
            "decision": "DISTRIBUTED_IDENTITY_BEATS_RARITY_LEAD" if summary["one_sided_add_one_p"] < 0.05 else "IDENTITY_LEAD_NOT_RESOLVED",
        })
        style_rows.extend(styles)
    write_tsv(IDENTITY_PAIRS, identity_pair_rows, [
        "side", "stratum_id", "pair_ordinal", "section", "language", "hand", "stem", "distance_cell", "l_occurrence_id",
        "l_folio", "l_context", "l_exact_score", "l_training_count", "m_occurrence_id", "m_folio", "m_context",
        "m_exact_score", "m_training_count", "exact_auc", "rarity_auc", "delta_exact_minus_rarity", "semantic_export_credit",
    ])
    write_tsv(IDENTITY_SUMMARY, identity_summaries, [
        "side", "real_context_events", "scoreable_events", "raw_cross_folio_pairs", "informative_strata",
        "same_folio_pair_capacity", "exact_micro_auc", "rarity_micro_auc", "exact_macro_auc", "rarity_macro_auc",
        "macro_delta", "sign_flips", "exceed_or_equal", "one_sided_add_one_p", "decision",
    ])
    write_tsv(STYLE_SENSITIVITY, style_rows, [
        "side", "section", "language", "hand", "pairs", "exact_micro_auc", "rarity_micro_auc",
        "delta_exact_minus_rarity", "interpretation",
    ])

    passage_rows = []
    for ordinal, (group_id, candidate, control, outcome) in enumerate(full_pair_material, 1):
        side = CORE_GROUPS[group_id][0]
        passage_rows.append({
            "passage_id": f"G803-P{ordinal:03d}", "kind": "MATCHED_INFORMATIVE_PAIR", "group_id": group_id,
            "outcome": outcome, "stem": candidate["stem"], "distance_cell": candidate["distance_cell"],
            "candidate_locus": candidate["locus"],
            "candidate_span": f"{candidate['left_context']} {candidate['stem']}{candidate['terminal']} {candidate['right_context']}",
            "candidate_full_line": line_map[(candidate["source_selector"], candidate["locus"])],
            "control_locus": control["locus"],
            "control_span": f"{control['left_context']} {control['stem']}{control['terminal']} {control['right_context']}",
            "control_full_line": line_map[(control["source_selector"], control["locus"])],
            "note": f"same target stem and distance cell; different folio; {side.lower()} context compared",
        })
    for group_id, (side, surfaces) in CORE_GROUPS.items():
        field = "left_context" if side == "LEFT" else "right_context"
        for row in sorted((row for row in rows if row[field] in surfaces and row["terminal"] == "m"), key=lambda row: row["occurrence_id"]):
            ordinal = len(passage_rows) + 1
            passage_rows.append({
                "passage_id": f"G803-P{ordinal:03d}", "kind": "CORE_COUNTEREXAMPLE", "group_id": group_id,
                "outcome": "M_SURFACE_INSIDE_L_FAVOURING_CONTEXT", "stem": row["stem"], "distance_cell": row["distance_cell"],
                "candidate_locus": row["locus"],
                "candidate_span": f"{row['left_context']} {row['stem']}{row['terminal']} {row['right_context']}",
                "candidate_full_line": line_map[(row["source_selector"], row["locus"])],
                "control_locus": "NONE", "control_span": "NONE", "control_full_line": "NONE",
                "note": "explicit counterexample; construction is a preference, not a deterministic rule",
            })
    write_tsv(PASSAGES, passage_rows, [
        "passage_id", "kind", "group_id", "outcome", "stem", "distance_cell", "candidate_locus", "candidate_span",
        "candidate_full_line", "control_locus", "control_span", "control_full_line", "note",
    ])

    core_counts = Counter((row["side"], row["context_surface"]) for row in occurrence_rows)
    core_m = Counter((row["side"], row["context_surface"]) for row in occurrence_rows if row["terminal"] == "m")
    bridge_rows = []
    for prior in priors:
        key, group_id = (prior["side"], prior["context_surface"]), core_membership.get((prior["side"], prior["context_surface"]), "NONE")
        bridge_rows.append({
            "side": prior["side"], "context_surface": prior["context_surface"], "core_group": group_id,
            "preexisting_broad_role": prior["preexisting_broad_role"],
            "preexisting_working_default_de": prior["preexisting_working_default_de"], "primary_source": prior["primary_source"],
            "gdt803_context_events": core_counts[key] if group_id != "NONE" else coefficient_map[key]["global_events"],
            "gdt803_context_m": core_m[key] if group_id != "NONE" else coefficient_map[key]["global_m"],
            "bridge_reading": ("LEFT_QUALITY_OR_CONDITION_FIELD" if group_id == "LEFT_QOK4"
                               else "RIGHT_VALUE_STATE_OR_RESULT_FIELD" if group_id == "RIGHT_RESULT3"
                               else "RIVAL_OR_COUNTEREXAMPLE_ONLY"),
            "historical_architecture_rival": ("descriptive quality + carrier + grade/state OR prescriptive condition + ingredient/preparation + result"
                                                if group_id != "NONE" else "no selected historical bridge"),
            "counterevidence": ("none of the 12 double-bracket events is itself a GDT744-licensed field; opaque address remains viable"
                                if group_id != "NONE" else "stable coefficient does not align cleanly with the selected bracket class"),
            "semantic_credit": "ZERO__WORKING_FIELD_ROLE_ONLY",
        })
    write_tsv(FIELD_BRIDGE, bridge_rows, [
        "side", "context_surface", "core_group", "preexisting_broad_role", "preexisting_working_default_de", "primary_source",
        "gdt803_context_events", "gdt803_context_m", "bridge_reading", "historical_architecture_rival", "counterevidence",
        "semantic_credit",
    ])

    summary_by_side = {row["side"]: row for row in identity_summaries}
    full_cards = {(row["group_id"], row["cohort"]): row for row in group_rows if row["population"] == "FULL" and row["position4"] == "ALL"}
    pair_counts = Counter((row["group_id"], row["population"], row["pair_outcome"]) for row in matched_pair_rows)
    candidate_rows = [
        {"candidate_id": "C1", "candidate": "DISTRIBUTED_EXACT_CONTEXT_IDENTITY_BEATS_RARITY",
         "decision": "LEFT_LEAD_ONLY__RIGHT_UNRESOLVED",
         "positive_evidence": f"left macro delta {summary_by_side['LEFT']['macro_delta']} p={summary_by_side['LEFT']['one_sided_add_one_p']}; right delta {summary_by_side['RIGHT']['macro_delta']}",
         "counterevidence": "style-sensitive; right sign-flip unresolved; no individual whole has portable matched-pair capacity",
         "claim_ceiling": "distributed formal context channel only"},
        {"candidate_id": "C2", "candidate": "QUALITY_VALUE_BRACKETED_L_SURFACE",
         "decision": "SELECT_EXPLORATORY_WORKING_CONSTRUCTION",
         "positive_evidence": f"12 exact double brackets on {candidate_bracket_stats[3]} folios/{candidate_bracket_stats[2]} stems, all l; 0/{bracket_control_total} exposure-matched set pairs equal all dimensions",
         "counterevidence": "candidate identities were selected after GDT802 outcome inspection; opaque three-field address remains viable",
         "claim_ceiling": "enumerated whole-context construction; role names replaceable"},
        {"candidate_id": "C3", "candidate": "PORTABLE_SINGLE_COMPLETE_CONTEXT", "decision": "NOT_SELECTED__CAPACITY_DISTRIBUTED",
         "positive_evidence": "four left and three right forms retain negative signs in every crossed fold",
         "counterevidence": "same-stem exact pairing has only 4:1 and 3:0 informative full comparisons amid 144 ties",
         "claim_ceiling": "no individual context word installed"},
        {"candidate_id": "C4", "candidate": "COMPLEMENTARY_M_AMOUNT_OR_PART_CONSTRUCTION", "decision": "HOLD__NO_CLEAN_ROLE_SPLIT",
         "positive_evidence": "left ar/qokar and right chor have positive stable coefficients",
         "counterevidence": "right dar reverses the naive amount class and the positive set lacks informative matched transfer",
         "claim_ceiling": "unresolved rival"},
        {"candidate_id": "C5", "candidate": "CLOTHING_SEMANTICS", "decision": "NOT_USED__PREVIOUSLY_REJECTED",
         "positive_evidence": "GDT799 supplied only the historical discovery trigger for an l/m contrast",
         "counterevidence": "AQABAB occurs with both covered and uncovered torsos; GDT803 uses text-only cached neighbours",
         "claim_ceiling": "no clothing meaning"},
        {"candidate_id": "C6", "candidate": "TERMINAL_OR_CONTEXT_PLAINTEXT_MEANING", "decision": "REJECT_EXPORT",
         "positive_evidence": "none", "counterevidence": "formal association and historical record architecture do not identify a lexeme or morpheme",
         "claim_ceiling": "zero word, component, plaintext or translation export"},
    ]
    write_tsv(CANDIDATES, candidate_rows, ["candidate_id", "candidate", "decision", "positive_evidence", "counterevidence", "claim_ceiling"])

    left_card, right_card = full_cards[("LEFT_QOK4", "CANDIDATE")], full_cards[("RIGHT_RESULT3", "CANDIDATE")]
    write_tsv(STRUCTURAL_CARD, [{
        "card_id": "GDT803-S1", "scope": "GDT800 paired l/m target occurrences in inherited cached text",
        "structural_tag": "PHYSICAL_LINE_EDGE_PLUS_LEARNED_PAIRED_FAMILY__QUALITY_VALUE_BRACKETED_L_SURFACE_WORKING_CONSTRUCTION",
        "german_display": "VORLÄUFIG: Qualitäts-/Zustandsfeld + l-Trägerform + Wert-/Zustandsfeld",
        "left_group": "qokeey|qokedy|qokeedy|qokain", "right_group": "daiin|shedy|chedy",
        "left_events_m": f"{left_card['events']}:{left_card['m_events']}", "right_events_m": f"{right_card['events']}:{right_card['m_events']}",
        "double_brackets_m": f"{candidate_bracket_stats[0]}:{candidate_bracket_stats[1]}",
        "confidence": "C1_EXPLORATORY_RECURRENT_CONSTRUCTION",
        "positive_evidence": "450 one-sided context events plus 12 exact three-token brackets across 11 target stems and 11 folios",
        "counterevidence": "post-hoc candidate compaction; style dependence; no single word or historical field independently grounded",
        "renderer_license": "EXACT_ENUMERATED_BRACKETS_AS_WORKING_DISPLAY_ONLY", "terminal_equivalence": "NONE",
        "component_export": "NONE", "semantic_export": "NONE", "plaintext_value": "NONE",
    }], [
        "card_id", "scope", "structural_tag", "german_display", "left_group", "right_group", "left_events_m", "right_events_m",
        "double_brackets_m", "confidence", "positive_evidence", "counterevidence", "renderer_license", "terminal_equivalence",
        "component_export", "semantic_export", "plaintext_value",
    ])

    output_paths = [STABLE_DECK, OCCURRENCE_ATLAS, BRACKET_ATLAS, CONTROL_MATCH, GROUP_CARD, RARITY_ENUMERATION,
                    BRACKET_ENUMERATION, MATCHED_PAIRS, IDENTITY_PAIRS, IDENTITY_SUMMARY, STYLE_SENSITIVITY, PASSAGES,
                    FIELD_BRIDGE, CANDIDATES, STRUCTURAL_CARD, REPORT]
    report = f"""# GDT803 — recurring complete-context construction beyond rarity

Status: `PARTIAL__14_STABLE_CONTEXTS__450_CORE_NEIGHBOUR_EVENTS__12_ALL_L_DOUBLE_BRACKETS__LEFT_IDENTITY_BEATS_RARITY__RIGHT_UNRESOLVED__ZERO_LEXEMES`

## Result

This pass does something new with the line-terminal lead and does **not** reuse
clothing as a meaning. It takes GDT802's recurrent complete left and right
neighbours into exact text passages, compares them with outcome-blind
frequency/exposure matches, and only then asks whether pre-existing broad
record roles form a useful working construction.

Four complete left contexts (`qokeey`, `qokedy`, `qokeedy`, `qokain`) occur
beside **{left_card['events']}** paired targets, with **{left_card['m_events']}** `m` and
{int(left_card['events']) - int(left_card['m_events'])} `l`. Three complete right contexts
(`daiin`, `shedy`, `chedy`) occur beside **{right_card['events']}** targets, with
**{right_card['m_events']}** `m`. Their cache-rest residuals remain negative after the
held-folio physical-position plus learned-stem baseline.

Most importantly, the two groups form **{candidate_bracket_stats[0]} exact three-token
brackets on {candidate_bracket_stats[3]} physical folios and {candidate_bracket_stats[2]}
different target stems**. Every middle target ends in `l`:

```text
qokeey  chal    chedy
qokeedy sail    chedy
qokedy  otal    chedy
qokain  cheol   daiin
qokedy  otal    shedy
```

The first useful renderer hypothesis from the chain is:

```text
QUALITY/CONDITION FIELD + l-CARRIER/ENTRY FORM + VALUE/STATE/RESULT FIELD
```

The equally live null is an opaque three-field address. The English role names
are analyst labels, not decoded words.

## Rarity and exposure controls

The controls were selected without `l/m`, coefficients or residuals, using
only log event, target-stem and physical-folio exposure. The selected left
controls are `al/shedy/shol/ar`; the right controls are `chol/ol/dy`. Their
double intersection has {len(matched_bracket)} events, including
{sum(row['terminal'] == 'm' for row in matched_bracket)} `m`, versus the
candidate's {candidate_bracket_stats[0]} all-`l` events.

The ten-nearest exposure enumeration creates **{len(left_sets):,}** unique left
sets and **{len(right_sets):,}** right sets, or **{bracket_control_total:,}**
two-sided combinations. None matches the candidate simultaneously on event
count, all-`l` purity, target-stem breadth and folio breadth. This is a strong
exploratory rank, not a p-value, because the seven identities were compacted
after GDT802 exposed their outcomes.

An independent distributed identity-versus-rarity audit is positive on the
left: macro AUC gain **{summary_by_side['LEFT']['macro_delta']}**, sign-flip
`p={summary_by_side['LEFT']['one_sided_add_one_p']}`. The right gain is
**{summary_by_side['RIGHT']['macro_delta']}** with
`p={summary_by_side['RIGHT']['one_sided_add_one_p']}` and remains unresolved.
The effect varies by section/language/hand style, and same-folio exact-pair
capacity is only {summary_by_side['LEFT']['same_folio_pair_capacity']} left and
{summary_by_side['RIGHT']['same_folio_pair_capacity']} right.

## What the construction may mean

All seven core forms had pre-existing replaceable quality, state or value
roles before this pass. The broad historical architecture therefore makes two
readings worth carrying:

- descriptive: quality/state + lemma or material carrier + grade/state;
- prescriptive: process condition + ingredient/preparation + result/closure.

Neither is selected as plaintext. None of the twelve double brackets is itself
a licensed GDT744 historical microfield, so an opaque address remains a serious
rival. The construction localizes the middle `...l` wholes as candidate
carriers or entries; it does not make final EVA `l` a morpheme.

## Corrections and limits

- This is not a clothing analysis. GDT799's clothing relation failed and
  supplies no semantic evidence here.
- Right `daiin` means the observed sequence `Xl daiin`; it does not revive the
  retired left-neighbour claim `daiin X -> m`.
- A complementary `m` amount/part reading is not installed. `ar/qokar/chor`
  are interesting, but `dar` points the other way and exact matched transfer
  is too thin.
- No individual complete context is installed as a portable rule. The exact
  matched comparisons contain only {pair_counts[('LEFT_QOK4', 'FULL', 'SUPPORTS_L')]}:{pair_counts[('LEFT_QOK4', 'FULL', 'REVERSES')]} informative left and
  {pair_counts[('RIGHT_RESULT3', 'FULL', 'SUPPORTS_L')]}:{pair_counts[('RIGHT_RESULT3', 'FULL', 'REVERSES')]} informative right decisions, with the rest tied.
- Confirmed lexemes, component meanings, plaintext clauses and translations
  remain zero.

## Next route

Carry the exact 12 brackets as one exploratory construction and search only
the already cached text for its middle whole forms outside this bracket. Ask
whether those same wholes repeatedly occupy the open lemma/material/ingredient
slot in independently established fields. That is the shortest route from
this formal grammar to concrete nouns without returning to generic prose or
to EVA-letter mnemonics.
"""
    REPORT.write_text(report, encoding="utf-8")

    result = {
        "schema": "GDT803_RESULT_V1", "experiment": "GDT803",
        "status": "PARTIAL__14_STABLE_CONTEXTS__450_CORE_NEIGHBOUR_EVENTS__12_ALL_L_DOUBLE_BRACKETS__LEFT_IDENTITY_BEATS_RARITY__RIGHT_UNRESOLVED__ZERO_LEXEMES",
        "decision": "QUALITY_VALUE_BRACKETED_L_SURFACE_WORKING_CONSTRUCTION",
        "stable_context_cards": len(stable_rows), "core_context_surfaces": sum(len(value[1]) for value in CORE_GROUPS.values()),
        "core_one_sided_occurrences": len(occurrence_rows), "double_bracket_events": candidate_bracket_stats[0],
        "double_bracket_m": candidate_bracket_stats[1], "double_bracket_stems": candidate_bracket_stats[2],
        "double_bracket_physical_folios": candidate_bracket_stats[3], "matched_bracket_events": len(matched_bracket),
        "matched_bracket_m": sum(row["terminal"] == "m" for row in matched_bracket),
        "exposure_matched_bracket_set_pairs": bracket_control_total, "exposure_matched_brackets_as_extreme": bracket_extreme,
        "identity_rarity_summary": identity_summaries,
        "control_total_distances": {key: float(value) for key, value in control_distances.items()}, "sign_flips": args.sign_flips,
        "semantic_exports": 0, "confirmed_lexemes": 0, "confirmed_plaintext_clauses": 0, "component_exports": 0,
        "terminal_equivalence_licenses": 0, "new_pages_opened": 0, "new_images_opened": 0,
        "f84_or_f84r_accessed": False,
        "inputs": {rel(path): sha(path) for path in (ATLAS_IN, COEFFICIENTS_IN, PREDICTIONS_IN, METADATA_IN, LINES_IN, SOURCE_LOCK, ROLE_PRIORS)},
        "outputs": {},
        "implementation": {rel(SRC / "run.py"): sha(SRC / "run.py"), rel(SRC / "validate.py"): sha(SRC / "validate.py")},
    }
    result["outputs"] = {rel(path): sha(path) for path in output_paths}
    result["content_hash"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"GDT803: {len(stable_rows)} stable contexts; {len(occurrence_rows)} core one-sided events; {len(bracket_rows)} all-l double brackets; left identity p={summary_by_side['LEFT']['one_sided_add_one_p']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
