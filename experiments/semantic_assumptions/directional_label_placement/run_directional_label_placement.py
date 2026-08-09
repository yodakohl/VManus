#!/usr/bin/env python3
"""Control or single-target runner for DIRECTIONPLACEMENT001."""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "experiments/semantic_assumptions/directional_label_placement"
DESIGN = BASE / "SOURCE_AND_METHOD_FREEZE.md"
PAIR_PANEL = BASE / "MASKED_PAIR_PANEL.tsv"
PAIR_AUDIT = BASE / "PAIRING_AUDIT.json"
INTERLINEAR = ROOT / "experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv"
DIRECTION_SOURCE = ROOT / "experiments/semantic_assumptions/directional_label_placement_capacity/HORIZONTAL_SOURCE_PANEL.tsv"
CONTROL_RESULT = BASE / "CONTROL_RESULT.json"
CONTROL_VALIDATION = BASE / "CONTROL_VALIDATION.json"
TARGET_RESULT = BASE / "TARGET_RESULT.json"
EDITIONS = ("ZL3b", "IT2a", "RF1b")
VIEWS = ("LENGTH_ADJUSTED", "RAW")
EXPECTED_PAIR_HEADER = [
    "pair_id", "side", "physical_folio", "page", "stratum_id",
    "source_locus", "normalized_code", "object_tags", "readings",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def validate_pair_panel(rows: list[dict[str, str]]) -> None:
    if not rows or list(rows[0]) != EXPECTED_PAIR_HEADER:
        raise ValueError("masked pair-panel header drift")
    if len(rows) != 32 or len({row["source_locus"] for row in rows}) != 32:
        raise ValueError("masked pair-panel row/locus drift")
    if any("class" in row or row["readings"] != "IT2a;RF1b;ZL3b" for row in rows):
        raise ValueError("masked pair-panel class/reading drift")
    pairs = defaultdict(list)
    for row in rows:
        pairs[row["pair_id"]].append(row)
    if len(pairs) != 16:
        raise ValueError("masked pair count drift")
    for pair_id, members in pairs.items():
        if Counter(row["side"] for row in members) != {"A": 1, "B": 1}:
            raise ValueError(f"pair side drift: {pair_id}")
        for field in ("physical_folio", "page", "stratum_id", "normalized_code", "object_tags"):
            if len({row[field] for row in members}) != 1:
                raise ValueError(f"within-pair {field} drift: {pair_id}")
        if not pair_id.startswith(members[0]["stratum_id"] + "|P"):
            raise ValueError(f"pair ID/stratum drift: {pair_id}")
    if len({row["physical_folio"] for row in rows}) != 6:
        raise ValueError("physical-folio count drift")


def literal_features(token: str) -> set[str]:
    output = {f"LIT_TOKEN:{token}"}
    for size in (2, 3, 4):
        if len(token) <= size:
            continue
        output.add(f"LIT_PREFIX{size}:{token[:size]}")
        output.add(f"LIT_SUFFIX{size}:{token[-size:]}")
        output.update(
            f"LIT_INFIX{size}:{token[start:start + size]}"
            for start in range(1, len(token) - size)
        )
    return output


def sequence_features(domain: str, token: str) -> set[str]:
    atoms = token.split("+")
    output = {
        f"{domain}_TOKEN:{token}",
        f"{domain}_PREFIX:{atoms[0]}",
        f"{domain}_SUFFIX:{atoms[-1]}",
    }
    output.update(f"{domain}_ATOM:{atom}" for atom in atoms)
    output.update(
        f"{domain}_BIGRAM:{left}+{right}"
        for left, right in zip(atoms, atoms[1:])
    )
    return output


def feature_domain(feature: str) -> str:
    return feature.split("_", 1)[0]


def tokens_and_features(row: dict[str, str], domain: str):
    if domain == "LIT":
        tokens = row["surface"].split()
        return [(token, len(token), literal_features(token)) for token in tokens]
    column = "root_sequence" if domain == "ROOT" else "role_sequence"
    tokens = row[column].split()
    return [
        (token, len(token.split("+")), sequence_features(domain, token))
        for token in tokens
    ]


def canonical_matrix_hash(
    features: list[str], matrices: dict[str, dict[str, np.ndarray]]
) -> str:
    payload: list[Any] = [features]
    for view in VIEWS:
        for edition in EDITIONS:
            payload.append(view)
            payload.append(edition)
            payload.append([[f"{value:.12f}" for value in row] for row in matrices[view][edition]])
    return hashlib.sha256(
        json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def build_feature_data(pair_rows: list[dict[str, str]]) -> dict[str, Any]:
    validate_pair_panel(pair_rows)
    loci = [row["source_locus"] for row in pair_rows]
    locus_set = set(loci)
    rows = [row for row in read_tsv(INTERLINEAR) if row["locus"] in locus_set]
    expected = {(edition, locus) for edition in EDITIONS for locus in loci}
    observed = [(row["edition"], row["locus"]) for row in rows]
    if len(observed) != 96 or set(observed) != expected or len(set(observed)) != 96:
        raise ValueError("interlinear edition/locus row-contract drift")
    pair_by_locus = {row["source_locus"]: row for row in pair_rows}
    for row in rows:
        source = pair_by_locus[row["locus"]]
        if (
            row["page"] != source["page"]
            or row["code"] != source["normalized_code"]
            or row["grammar_scope"] != "DIAGNOSTIC_NONPROSE"
            or row["kind"] != "L"
        ):
            raise ValueError("interlinear page/code/scope/kind binding drift")
        widths = {
            len(row["surface"].split()),
            len(row["root_sequence"].split()),
            len(row["role_sequence"].split()),
        }
        if len(widths) != 1 or 0 in widths:
            raise ValueError("space-delimited token alignment drift")

    row_by_key = {(row["edition"], row["locus"]): row for row in rows}
    stats: dict[str, dict[str, dict[str, Any]]] = {
        edition: defaultdict(lambda: {"hits": 0, "folios": set(), "types": set()})
        for edition in EDITIONS
    }
    locus_domain: dict[tuple[str, str, str], list[tuple[str, int, set[str]]]] = {}
    for edition in EDITIONS:
        for locus in loci:
            row = row_by_key[(edition, locus)]
            folio = pair_by_locus[locus]["physical_folio"]
            for domain in ("LIT", "ROOT", "ROLE"):
                values = tokens_and_features(row, domain)
                locus_domain[(edition, locus, domain)] = values
                for token, _, token_features in values:
                    for feature in token_features:
                        stats[edition][feature]["hits"] += 1
                        stats[edition][feature]["folios"].add(folio)
                        stats[edition][feature]["types"].add(token)

    common = set.intersection(*(set(stats[edition]) for edition in EDITIONS))
    supported = []
    for feature in sorted(common):
        if not all(
            stats[edition][feature]["hits"] >= 4
            and len(stats[edition][feature]["folios"]) >= 4
            for edition in EDITIONS
        ):
            continue
        if feature.startswith(("LIT_PREFIX", "LIT_SUFFIX", "LIT_INFIX")) and not all(
            len(stats[edition][feature]["types"]) >= 3 for edition in EDITIONS
        ):
            continue
        supported.append(feature)

    raw_all: dict[str, np.ndarray] = {}
    adjusted_all: dict[str, np.ndarray] = {}
    presence_all: dict[str, np.ndarray] = {}
    for edition in EDITIONS:
        raw = np.zeros((32, len(supported)), dtype=np.float64)
        adjusted = np.zeros_like(raw)
        presence = np.zeros_like(raw, dtype=np.int8)
        global_lengths: dict[str, Counter[int]] = defaultdict(Counter)
        feature_lengths: dict[str, Counter[int]] = defaultdict(Counter)
        for locus in loci:
            for domain in ("LIT", "ROOT", "ROLE"):
                for _, size, token_features in locus_domain[(edition, locus, domain)]:
                    global_lengths[domain][size] += 1
                    for feature in token_features:
                        if feature in supported:
                            feature_lengths[feature][size] += 1
        for row_index, locus in enumerate(loci):
            for column, feature in enumerate(supported):
                domain = feature_domain(feature)
                values = locus_domain[(edition, locus, domain)]
                denominator = len(values)
                hits = sum(feature in token_features for _, _, token_features in values)
                expected_count = sum(
                    count * feature_lengths[feature][size] / global_lengths[domain][size]
                    for size, count in Counter(size for _, size, _ in values).items()
                )
                raw[row_index, column] = hits / denominator
                adjusted[row_index, column] = (hits - expected_count) / denominator
                presence[row_index, column] = int(hits > 0)
        raw_all[edition] = raw
        adjusted_all[edition] = adjusted
        presence_all[edition] = presence

    pair_order = []
    pair_indices = []
    for pair_id in dict.fromkeys(row["pair_id"] for row in pair_rows):
        members = {row["side"]: index for index, row in enumerate(pair_rows) if row["pair_id"] == pair_id}
        pair_order.append(pair_id)
        pair_indices.append((members["A"], members["B"]))
    variable_columns = []
    for column, _ in enumerate(supported):
        valid = True
        for edition in EDITIONS:
            for matrix in (raw_all[edition], adjusted_all[edition]):
                differences = np.array([matrix[a, column] - matrix[b, column] for a, b in pair_indices])
                if not np.any(np.abs(differences) > 1e-14):
                    valid = False
        if valid:
            variable_columns.append(column)
    features = [supported[column] for column in variable_columns]
    matrices = {
        "RAW": {edition: raw_all[edition][:, variable_columns] for edition in EDITIONS},
        "LENGTH_ADJUSTED": {edition: adjusted_all[edition][:, variable_columns] for edition in EDITIONS},
    }
    presence = {edition: presence_all[edition][:, variable_columns] for edition in EDITIONS}
    if not features:
        raise ValueError("zero eligible variable features")
    return {
        "rows": rows,
        "loci": loci,
        "pair_order": pair_order,
        "pair_indices": pair_indices,
        "pair_folios": [pair_rows[a]["physical_folio"] for a, _ in pair_indices],
        "features": features,
        "matrices": matrices,
        "presence": presence,
        "matrix_sha256": canonical_matrix_hash(features, matrices),
    }


def all_signs(pair_count: int) -> np.ndarray:
    numbers = np.arange(1 << pair_count, dtype=np.uint32)[:, None]
    bits = (numbers >> np.arange(pair_count, dtype=np.uint32)) & 1
    return bits.astype(np.float64) * 2.0 - 1.0


def pair_coefficients(pair_folios: list[str]) -> np.ndarray:
    counts = Counter(pair_folios)
    folio_count = len(counts)
    return np.array([1.0 / (folio_count * counts[folio]) for folio in pair_folios])


def pair_differences(data: dict[str, Any], view: str, edition: str) -> np.ndarray:
    matrix = data["matrices"][view][edition]
    return np.array([matrix[a] - matrix[b] for a, b in data["pair_indices"]])


def orbit_for_differences(signs: np.ndarray, differences: np.ndarray, coefficients: np.ndarray):
    effects = signs @ (differences * coefficients[:, None])
    scales = np.sqrt(np.mean(effects * effects, axis=0))
    standardized = np.zeros_like(effects)
    movable = scales > 1e-14
    standardized[:, movable] = effects[:, movable] / scales[movable]
    return effects, standardized


def robust_scores(standardized: dict[str, np.ndarray]) -> np.ndarray:
    values = np.stack([standardized[edition] for edition in EDITIONS])
    return np.maximum(np.minimum.reduce(values), np.minimum.reduce(-values)).clip(min=0)


def compute_orbits(data: dict[str, Any], pair_mask: list[int] | None = None):
    indices = pair_mask if pair_mask is not None else list(range(len(data["pair_order"])))
    folios = [data["pair_folios"][index] for index in indices]
    signs = all_signs(len(indices))
    coefficients = pair_coefficients(folios)
    result = {}
    for view in VIEWS:
        effects = {}
        standardized = {}
        for edition in EDITIONS:
            differences = pair_differences(data, view, edition)[indices]
            effects[edition], standardized[edition] = orbit_for_differences(signs, differences, coefficients)
        scores = robust_scores(standardized)
        result[view] = {
            "effects": effects,
            "standardized": standardized,
            "scores": scores,
            "family_max": scores.max(axis=1),
        }
    return signs, result


def sign_index(signs: np.ndarray) -> int:
    return int(sum((1 << index) for index, value in enumerate(signs) if value > 0))


def rejects_pair_rows(rows: list[dict[str, str]]) -> bool:
    try:
        validate_pair_panel(rows)
    except ValueError:
        return True
    return False


def structural_gates(
    direction: int,
    presence_by_reading: dict[str, int],
    individual_directions: dict[str, dict[str, Any]],
    nonpharma: dict[str, bool],
    deletion_direction: bool,
) -> dict[str, bool]:
    return {
        "enriched_presence_four_folios": min(presence_by_reading.values()) >= 4,
        "five_of_six_individual_folios": min(
            item["same_nonzero"] for item in individual_directions.values()
        ) >= 5,
        "both_nonpharma_folios": direction != 0 and all(nonpharma.values()),
        "deletion_direction": direction != 0 and deletion_direction,
    }


def controls(data: dict[str, Any], pair_rows: list[dict[str, str]]) -> dict[str, Any]:
    signs, orbits = compute_orbits(data)
    coefficients = pair_coefficients(data["pair_folios"])
    planted_index = 23117
    planted_direction = signs[planted_index]
    planted_difference = planted_direction[:, None]
    _, planted_z = orbit_for_differences(signs, planted_difference, coefficients)
    planted = robust_scores({edition: planted_z for edition in EDITIONS})[:, 0]
    top = planted[planted_index]
    top_indices = np.flatnonzero(np.abs(planted - top) <= 1e-12).tolist()
    disagreement = robust_scores(
        {"ZL3b": planted_z, "IT2a": planted_z, "RF1b": -planted_z}
    )

    # A feature perfectly determined by complete token length has zero residual.
    fixture_lengths = [1, 1, 2, 2]
    fixture_hits = [0, 0, 1, 1]
    length_totals = Counter(fixture_lengths)
    hit_totals = Counter(length for length, hit in zip(fixture_lengths, fixture_hits) if hit)
    fixture_residuals = [
        hit - hit_totals[length] / length_totals[length]
        for length, hit in zip(fixture_lengths, fixture_hits)
    ]

    folio_only = np.array(
        [1.0 if folio == "f99" else 0.0 for folio in data["pair_folios"]]
    )
    equal_weight_effect = float(np.sum(folio_only * coefficients))
    distributed_structural = structural_gates(
        1,
        {edition: 6 for edition in EDITIONS},
        {edition: {"same_nonzero": 6} for edition in EDITIONS},
        {edition: True for edition in EDITIONS},
        True,
    )
    one_folio_structural = structural_gates(
        1,
        {edition: 1 for edition in EDITIONS},
        {edition: {"same_nonzero": 1} for edition in EDITIONS},
        {edition: False for edition in EDITIONS},
        False,
    )
    row_missing = pair_rows[:-1]
    row_duplicate = pair_rows + [dict(pair_rows[0])]
    side_drift = [dict(row) for row in pair_rows]
    side_drift[0]["side"] = side_drift[1]["side"]
    page_drift = [dict(row) for row in pair_rows]
    page_drift[0]["page"] = "f999r"

    assertions = {
        "exact_65536_unique_swap_orbit": signs.shape == (65536, 16)
        and len({tuple(row) for row in signs}) == 65536,
        "two_sided_planted_complement_tie": len(top_indices) == 2
        and planted_index in top_indices
        and (65535 ^ planted_index) in top_indices,
        "inclusive_top_tail_is_two": int(np.sum(planted >= top - 1e-12)) == 2,
        "alternate_reading_disagreement_collapses": float(np.max(disagreement)) == 0.0,
        "pair_constant_cancels": all(
            np.allclose(orbit_for_differences(signs, np.zeros((16, 1)), coefficients)[0], 0)
            for _ in range(2)
        ),
        "length_only_fixture_cancels": max(abs(value) for value in fixture_residuals) == 0,
        "folio_equal_weighting": abs(equal_weight_effect - (1 / 6)) < 1e-12,
        "one_folio_signal_fails_structural_gates": not any(one_folio_structural.values())
        and set(folio for folio, value in zip(data["pair_folios"], folio_only) if value) == {"f99"},
        "distributed_signal_passes_structural_gates": all(distributed_structural.values())
        and {"f68", "f88"}.issubset(set(data["pair_folios"])),
        "missing_row_rejected": rejects_pair_rows(row_missing),
        "duplicate_row_rejected": rejects_pair_rows(row_duplicate),
        "side_drift_rejected": rejects_pair_rows(side_drift),
        "page_drift_rejected": rejects_pair_rows(page_drift),
        "all_feature_orbits_finite": all(
            np.isfinite(orbits[view]["family_max"]).all() for view in VIEWS
        ),
        "target_result_absent": not TARGET_RESULT.exists(),
    }
    return {
        "assertions": assertions,
        "planted_index": planted_index,
        "planted_top_indices": top_indices,
        "feature_count": len(data["features"]),
        "feature_domain_counts": dict(sorted(Counter(feature_domain(f) for f in data["features"]).items())),
        "features": data["features"],
        "matrix_sha256": data["matrix_sha256"],
        "assignment_count": len(signs),
        "family_max_quantiles": {
            view: {
                quantile: f"{np.quantile(orbits[view]['family_max'], value):.12f}"
                for quantile, value in (("p90", .90), ("p95", .95), ("p99", .99))
            }
            for view in VIEWS
        },
    }


def target_signs(pair_rows: list[dict[str, str]]) -> np.ndarray:
    source = {row["source_locus"]: row for row in read_tsv(DIRECTION_SOURCE)}
    output = []
    for pair_id in dict.fromkeys(row["pair_id"] for row in pair_rows):
        members = {row["side"]: row for row in pair_rows if row["pair_id"] == pair_id}
        classes = {side: source[row["source_locus"]]["class"] for side, row in members.items()}
        if set(classes.values()) != {"EAST", "WEST"}:
            raise ValueError(f"target source binding drift: {pair_id}")
        output.append(1.0 if classes["A"] == "EAST" else -1.0)
    return np.array(output)


def common_direction(values: list[float], tolerance: float = 1e-12) -> int:
    if all(value > tolerance for value in values):
        return 1
    if all(value < -tolerance for value in values):
        return -1
    return 0


def target(data: dict[str, Any], pair_rows: list[dict[str, str]]) -> dict[str, Any]:
    if not CONTROL_RESULT.exists() or not CONTROL_VALIDATION.exists():
        raise ValueError("validated controls required")
    control = json.loads(CONTROL_RESULT.read_text())
    validation = json.loads(CONTROL_VALIDATION.read_text())
    if (
        validation.get("status") != "PASS"
        or control.get("status") != "PASS"
        or control.get("bindings") != bindings()
        or validation.get("control_result_sha256") != sha256(CONTROL_RESULT)
    ):
        raise ValueError("control binding/validation is not current PASS")
    observed_signs = target_signs(pair_rows)
    target_assignment = sign_index(observed_signs)
    signs, orbits = compute_orbits(data)
    if not np.array_equal(signs[target_assignment], observed_signs):
        raise ValueError("target sign/index mismatch")

    pair_classes = []
    source = {row["source_locus"]: row["class"] for row in read_tsv(DIRECTION_SOURCE)}
    for row in pair_rows:
        pair_classes.append(source[row["source_locus"]])

    deletion = {}
    folios = sorted(set(data["pair_folios"]))
    for removed in folios:
        keep = [index for index, folio in enumerate(data["pair_folios"]) if folio != removed]
        deletion_signs, deletion_orbits = compute_orbits(data, keep)
        observed = observed_signs[keep]
        index = sign_index(observed)
        if not np.array_equal(deletion_signs[index], observed):
            raise ValueError("deletion target sign/index mismatch")
        deletion[removed] = {
            "effects": {
                edition: deletion_orbits["LENGTH_ADJUSTED"]["effects"][edition][index]
                for edition in EDITIONS
            },
            "family_p": np.array([
                np.mean(
                    deletion_orbits["LENGTH_ADJUSTED"]["family_max"]
                    >= deletion_orbits["LENGTH_ADJUSTED"]["scores"][index, column] - 1e-12
                )
                for column in range(len(data["features"]))
            ]),
            "assignment_count": len(deletion_signs),
        }

    rows = []
    for column, feature in enumerate(data["features"]):
        view_values = {}
        view_p = {}
        for view in VIEWS:
            view_values[view] = {
                edition: float(orbits[view]["effects"][edition][target_assignment, column])
                for edition in EDITIONS
            }
            score = orbits[view]["scores"][target_assignment, column]
            view_p[view] = float(np.mean(orbits[view]["family_max"] >= score - 1e-12))
        direction = common_direction(
            [view_values[view][edition] for view in VIEWS for edition in EDITIONS]
        )
        enriched = "EAST" if direction == 1 else "WEST" if direction == -1 else "NONE"
        presence_by_reading = {}
        individual_directions = {}
        nonpharma = {}
        for edition in EDITIONS:
            present_folios = set()
            for index, row in enumerate(pair_rows):
                if pair_classes[index] == enriched and data["presence"][edition][index, column]:
                    present_folios.add(row["physical_folio"])
            presence_by_reading[edition] = len(present_folios)
            differences = pair_differences(data, "LENGTH_ADJUSTED", edition)[:, column] * observed_signs
            folio_effects = {
                folio: float(np.mean([value for value, item_folio in zip(differences, data["pair_folios"]) if item_folio == folio]))
                for folio in folios
            }
            individual_directions[edition] = {
                "same_nonzero": sum(common_direction([value]) == direction for value in folio_effects.values()),
                "effects": folio_effects,
            }
            nonpharma[edition] = all(common_direction([folio_effects[folio]]) == direction for folio in ("f68", "f88"))
        deletion_direction = all(
            common_direction([float(deletion[removed]["effects"][edition][column])]) == direction
            for removed in folios for edition in EDITIONS
        )
        deletion_p = {removed: float(deletion[removed]["family_p"][column]) for removed in folios}
        gates = {
            "adjusted_family_p": view_p["LENGTH_ADJUSTED"] <= .025,
            "raw_family_p": view_p["RAW"] <= .05,
            "common_direction_all_readings_views": direction != 0,
            "minimum_adjusted_effect": min(abs(value) for value in view_values["LENGTH_ADJUSTED"].values()) >= .10,
            "minimum_raw_effect": min(abs(value) for value in view_values["RAW"].values()) >= .10,
            "deletion_family_p": max(deletion_p.values()) <= .05,
        }
        gates.update(
            structural_gates(
                direction,
                presence_by_reading,
                individual_directions,
                nonpharma,
                deletion_direction,
            )
        )
        rows.append({
            "feature": feature,
            "direction": enriched,
            "effects": view_values,
            "family_p": view_p,
            "presence_folios": presence_by_reading,
            "individual_folios": individual_directions,
            "nonpharma": nonpharma,
            "deletion_family_p": deletion_p,
            "gates": gates,
            "passes": all(gates.values()),
        })
    candidates = [row["feature"] for row in rows if row["passes"]]
    return {
        "status": "FINAL_CANDIDATE" if candidates else "FINAL_NONCONFIRMATION",
        "target_assignment_extracted": True,
        "target_assignment_index": target_assignment,
        "candidate_count": len(candidates),
        "candidates": candidates,
        "rows": rows,
        "deletion_assignment_counts": {removed: deletion[removed]["assignment_count"] for removed in folios},
        "claim_ceiling": "placement-associated morphology only; no direction word, ownership, lexeme, plaintext, language, or translation",
    }


def bindings() -> dict[str, str]:
    return {
        "design": sha256(DESIGN),
        "masked_pair_panel": sha256(PAIR_PANEL),
        "pairing_audit": sha256(PAIR_AUDIT),
        "interlinear": sha256(INTERLINEAR),
        "runner": sha256(Path(__file__)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("controls", "target"), required=True)
    args = parser.parse_args()
    pair_rows = read_tsv(PAIR_PANEL)
    data = build_feature_data(pair_rows)
    if args.mode == "controls":
        if TARGET_RESULT.exists():
            raise ValueError("target artifact already exists")
        result = controls(data, pair_rows)
        result.update({
            "status": "PASS" if all(result["assertions"].values()) else "FAIL",
            "bindings": bindings(),
            "source_pair_count": 16,
            "source_locus_count": 32,
            "interlinear_row_count": len(data["rows"]),
            "target_assignment_extracted": False,
            "target_result_exists_before": False,
            "target_result_exists_after": TARGET_RESULT.exists(),
        })
        CONTROL_RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        if result["status"] != "PASS":
            raise SystemExit(1)
    else:
        if TARGET_RESULT.exists():
            raise ValueError("registered target artifact already exists")
        result = target(data, pair_rows)
        result.update({
            "bindings": {**bindings(), "direction_source": sha256(DIRECTION_SOURCE), "controls": sha256(CONTROL_RESULT), "control_validation": sha256(CONTROL_VALIDATION)},
            "feature_count": len(data["features"]),
            "features": data["features"],
            "matrix_sha256": data["matrix_sha256"],
            "assignment_count": 65536,
        })
        TARGET_RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
