#!/usr/bin/env python3
"""Independent nonimporting target validator for DIRECTIONPLACEMENT001."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "experiments/semantic_assumptions/directional_label_placement"
TARGET = BASE / "TARGET_RESULT.json"
OUTPUT = BASE / "TARGET_VALIDATION.json"
CONTROL = BASE / "CONTROL_RESULT.json"
CONTROL_VALIDATION = BASE / "CONTROL_VALIDATION.json"
DESIGN = BASE / "SOURCE_AND_METHOD_FREEZE.md"
PANEL = BASE / "MASKED_PAIR_PANEL.tsv"
PAIR_AUDIT = BASE / "PAIRING_AUDIT.json"
RUNNER = BASE / "run_directional_label_placement.py"
INTERLINEAR = ROOT / "experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv"
SOURCE = ROOT / "experiments/semantic_assumptions/directional_label_placement_capacity/HORIZONTAL_SOURCE_PANEL.tsv"
EDITIONS = ("ZL3b", "IT2a", "RF1b")
VIEWS = ("LENGTH_ADJUSTED", "RAW")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tsv(path: Path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def marks(domain: str, token: str) -> set[str]:
    if domain == "LIT":
        result = {f"LIT_TOKEN:{token}"}
        for size in (2, 3, 4):
            if len(token) > size:
                result.add(f"LIT_PREFIX{size}:{token[:size]}")
                result.add(f"LIT_SUFFIX{size}:{token[-size:]}")
                result.update(
                    f"LIT_INFIX{size}:{token[offset:offset + size]}"
                    for offset in range(1, len(token) - size)
                )
        return result
    atoms = token.split("+")
    result = {
        f"{domain}_TOKEN:{token}",
        f"{domain}_PREFIX:{atoms[0]}",
        f"{domain}_SUFFIX:{atoms[-1]}",
    }
    result.update(f"{domain}_ATOM:{atom}" for atom in atoms)
    result.update(
        f"{domain}_BIGRAM:{atoms[index]}+{atoms[index + 1]}"
        for index in range(len(atoms) - 1)
    )
    return result


def token_data(row: dict[str, str], domain: str):
    column = {"LIT": "surface", "ROOT": "root_sequence", "ROLE": "role_sequence"}[domain]
    result = []
    for token in row[column].split():
        size = len(token) if domain == "LIT" else len(token.split("+"))
        result.append((size, marks(domain, token)))
    return result


def matrix_hash(features, matrices):
    payload: list[Any] = [features]
    for view in VIEWS:
        for edition in EDITIONS:
            payload.extend((view, edition))
            payload.append([[f"{value:.12f}" for value in row] for row in matrices[view][edition]])
    return hashlib.sha256(json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def rebuild(features: list[str], panel: list[dict[str, str]]):
    loci = [row["source_locus"] for row in panel]
    panel_by_locus = {row["source_locus"]: row for row in panel}
    selected = [row for row in tsv(INTERLINEAR) if row["locus"] in set(loci)]
    keyed = defaultdict(list)
    for row in selected:
        keyed[(row["edition"], row["locus"])].append(row)
    expected = {(edition, locus) for edition in EDITIONS for locus in loci}
    if set(keyed) != expected or len(selected) != 96 or any(len(value) != 1 for value in keyed.values()):
        raise ValueError("target-validator row contract failed")
    if not all(
        row["page"] == panel_by_locus[row["locus"]]["page"]
        and row["code"] == panel_by_locus[row["locus"]]["normalized_code"]
        and row["grammar_scope"] == "DIAGNOSTIC_NONPROSE"
        and row["kind"] == "L"
        for row in selected
    ):
        raise ValueError("target-validator metadata contract failed")

    cache = {}
    for edition in EDITIONS:
        for locus in loci:
            row = keyed[(edition, locus)][0]
            for domain in ("LIT", "ROOT", "ROLE"):
                cache[(edition, locus, domain)] = token_data(row, domain)

    matrices = {view: {} for view in VIEWS}
    presence = {}
    for edition in EDITIONS:
        raw = np.zeros((32, len(features)))
        adjusted = np.zeros_like(raw)
        seen = np.zeros_like(raw, dtype=int)
        length_total = defaultdict(Counter)
        length_feature = defaultdict(Counter)
        for locus in loci:
            for domain in ("LIT", "ROOT", "ROLE"):
                for size, token_marks in cache[(edition, locus, domain)]:
                    length_total[domain][size] += 1
                    for feature in features:
                        if feature in token_marks:
                            length_feature[feature][size] += 1
        for locus_index, locus in enumerate(loci):
            for feature_index, feature in enumerate(features):
                domain = feature.split("_", 1)[0]
                items = cache[(edition, locus, domain)]
                observed = sum(feature in item_marks for _, item_marks in items)
                local_lengths = Counter(size for size, _ in items)
                expected_count = sum(
                    count * length_feature[feature][size] / length_total[domain][size]
                    for size, count in local_lengths.items()
                )
                raw[locus_index, feature_index] = observed / len(items)
                adjusted[locus_index, feature_index] = (observed - expected_count) / len(items)
                seen[locus_index, feature_index] = observed > 0
        matrices["RAW"][edition] = raw
        matrices["LENGTH_ADJUSTED"][edition] = adjusted
        presence[edition] = seen

    pair_ids = list(dict.fromkeys(row["pair_id"] for row in panel))
    pair_indices = []
    pair_folios = []
    for pair_id in pair_ids:
        side = {row["side"]: index for index, row in enumerate(panel) if row["pair_id"] == pair_id}
        pair_indices.append((side["A"], side["B"]))
        pair_folios.append(panel[side["A"]]["physical_folio"])
    return selected, matrices, presence, pair_ids, pair_indices, pair_folios


def sign_matrix(count: int):
    result = np.empty((1 << count, count), dtype=float)
    for number in range(1 << count):
        for bit in range(count):
            result[number, bit] = 1.0 if number & (1 << bit) else -1.0
    return result


def orbits(matrices, pair_indices, pair_folios, keep=None):
    chosen = list(range(len(pair_indices))) if keep is None else keep
    folios = [pair_folios[index] for index in chosen]
    counts = Counter(folios)
    coefficients = np.array([1 / (len(counts) * counts[folio]) for folio in folios])
    signs = sign_matrix(len(chosen))
    output = {}
    for view in VIEWS:
        effect_by_reading = {}
        z_by_reading = {}
        for edition in EDITIONS:
            matrix = matrices[view][edition]
            difference = np.array([matrix[a] - matrix[b] for a, b in pair_indices])[chosen]
            effect = signs @ (difference * coefficients[:, None])
            scale = np.sqrt(np.mean(effect * effect, axis=0))
            z = np.zeros_like(effect)
            movable = scale > 1e-14
            z[:, movable] = effect[:, movable] / scale[movable]
            effect_by_reading[edition] = effect
            z_by_reading[edition] = z
        stack = np.stack([z_by_reading[edition] for edition in EDITIONS])
        score = np.maximum(np.min(stack, axis=0), np.min(-stack, axis=0)).clip(min=0)
        output[view] = {
            "effects": effect_by_reading,
            "score": score,
            "family": score.max(axis=1),
        }
    return signs, output


def index_for(values):
    return sum(1 << index for index, value in enumerate(values) if value > 0)


def direction(values):
    if all(value > 1e-12 for value in values):
        return 1
    if all(value < -1e-12 for value in values):
        return -1
    return 0


def deep_close(left, right) -> bool:
    if isinstance(left, dict) and isinstance(right, dict):
        return set(left) == set(right) and all(deep_close(left[key], right[key]) for key in left)
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(deep_close(a, b) for a, b in zip(left, right))
    if isinstance(left, bool) or isinstance(right, bool):
        return left is right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return abs(float(left) - float(right)) <= 1e-12
    return left == right


def main() -> None:
    stored = json.loads(TARGET.read_text())
    controls = json.loads(CONTROL.read_text())
    control_validation = json.loads(CONTROL_VALIDATION.read_text())
    panel = tsv(PANEL)
    features = controls["features"]
    selected, matrices, presence, pair_ids, pair_indices, pair_folios = rebuild(features, panel)
    signs, full = orbits(matrices, pair_indices, pair_folios)
    source_class = {row["source_locus"]: row["class"] for row in tsv(SOURCE)}
    observed = []
    locus_classes = []
    for pair_id in pair_ids:
        members = {row["side"]: row for row in panel if row["pair_id"] == pair_id}
        classes = {side: source_class[row["source_locus"]] for side, row in members.items()}
        if set(classes.values()) != {"EAST", "WEST"}:
            raise ValueError("target-validator pair class binding failed")
        observed.append(1.0 if classes["A"] == "EAST" else -1.0)
    for row in panel:
        locus_classes.append(source_class[row["source_locus"]])
    observed = np.array(observed)
    target_index = index_for(observed)
    if not np.array_equal(signs[target_index], observed):
        raise ValueError("target-validator target index failed")

    folios = sorted(set(pair_folios))
    deletions = {}
    deletion_counts = {}
    for removed in folios:
        keep = [index for index, folio in enumerate(pair_folios) if folio != removed]
        deletion_signs, deletion_orbit = orbits(matrices, pair_indices, pair_folios, keep)
        deletion_observed = observed[keep]
        deletion_index = index_for(deletion_observed)
        if not np.array_equal(deletion_signs[deletion_index], deletion_observed):
            raise ValueError("target-validator deletion index failed")
        deletions[removed] = (deletion_orbit, deletion_index)
        deletion_counts[removed] = len(deletion_signs)

    expected_rows = []
    for column, feature in enumerate(features):
        effects = {
            view: {
                edition: float(full[view]["effects"][edition][target_index, column])
                for edition in EDITIONS
            }
            for view in VIEWS
        }
        family_p = {
            view: float(np.mean(full[view]["family"] >= full[view]["score"][target_index, column] - 1e-12))
            for view in VIEWS
        }
        common = direction([effects[view][edition] for view in VIEWS for edition in EDITIONS])
        enriched = "EAST" if common == 1 else "WEST" if common == -1 else "NONE"
        presence_folios = {}
        individual = {}
        nonpharma = {}
        for edition in EDITIONS:
            present = {
                row["physical_folio"]
                for index, row in enumerate(panel)
                if locus_classes[index] == enriched and presence[edition][index, column]
            }
            presence_folios[edition] = len(present)
            base_difference = np.array([
                matrices["LENGTH_ADJUSTED"][edition][a, column]
                - matrices["LENGTH_ADJUSTED"][edition][b, column]
                for a, b in pair_indices
            ]) * observed
            folio_effect = {
                folio: float(np.mean([value for value, own_folio in zip(base_difference, pair_folios) if own_folio == folio]))
                for folio in folios
            }
            individual[edition] = {
                "same_nonzero": sum(direction([value]) == common for value in folio_effect.values()),
                "effects": folio_effect,
            }
            nonpharma[edition] = all(direction([folio_effect[folio]]) == common for folio in ("f68", "f88"))
        deletion_p = {
            removed: float(np.mean(
                deletion_data[0]["LENGTH_ADJUSTED"]["family"]
                >= deletion_data[0]["LENGTH_ADJUSTED"]["score"][deletion_data[1], column] - 1e-12
            ))
            for removed, deletion_data in deletions.items()
        }
        deletion_direction = all(
            direction([float(deletion_data[0]["LENGTH_ADJUSTED"]["effects"][edition][deletion_data[1], column])]) == common
            for deletion_data in deletions.values() for edition in EDITIONS
        )
        gates = {
            "adjusted_family_p": family_p["LENGTH_ADJUSTED"] <= .025,
            "raw_family_p": family_p["RAW"] <= .05,
            "common_direction_all_readings_views": common != 0,
            "minimum_adjusted_effect": min(abs(value) for value in effects["LENGTH_ADJUSTED"].values()) >= .10,
            "minimum_raw_effect": min(abs(value) for value in effects["RAW"].values()) >= .10,
            "deletion_family_p": max(deletion_p.values()) <= .05,
            "enriched_presence_four_folios": min(presence_folios.values()) >= 4,
            "five_of_six_individual_folios": min(value["same_nonzero"] for value in individual.values()) >= 5,
            "both_nonpharma_folios": common != 0 and all(nonpharma.values()),
            "deletion_direction": common != 0 and deletion_direction,
        }
        expected_rows.append({
            "feature": feature,
            "direction": enriched,
            "effects": effects,
            "family_p": family_p,
            "presence_folios": presence_folios,
            "individual_folios": individual,
            "nonpharma": nonpharma,
            "deletion_family_p": deletion_p,
            "gates": gates,
            "passes": all(gates.values()),
        })

    expected_bindings = {
        "design": sha(DESIGN), "masked_pair_panel": sha(PANEL),
        "pairing_audit": sha(PAIR_AUDIT), "interlinear": sha(INTERLINEAR),
        "runner": sha(RUNNER), "direction_source": sha(SOURCE),
        "controls": sha(CONTROL), "control_validation": sha(CONTROL_VALIDATION),
    }
    candidates = [row["feature"] for row in expected_rows if row["passes"]]
    checks = {
        "bindings": stored["bindings"] == expected_bindings,
        "controls_current_pass": controls["status"] == "PASS" and control_validation["status"] == "PASS" and control_validation["control_result_sha256"] == sha(CONTROL),
        "interlinear_rows_96": len(selected) == 96,
        "feature_identity": stored["features"] == features and stored["feature_count"] == len(features) == 13,
        "matrix_hash": stored["matrix_sha256"] == controls["matrix_sha256"] == matrix_hash(features, matrices),
        "full_assignment_count": stored["assignment_count"] == len(signs) == 65536,
        "target_binding_index": stored["target_assignment_extracted"] is True and stored["target_assignment_index"] == target_index == 60549,
        "deletion_counts": stored["deletion_assignment_counts"] == deletion_counts,
        "all_rows_reconstructed": deep_close(stored["rows"], expected_rows),
        "candidate_identity": stored["candidates"] == candidates == [] and stored["candidate_count"] == 0,
        "final_nonconfirmation": stored["status"] == "FINAL_NONCONFIRMATION",
        "claim_ceiling": stored["claim_ceiling"] == "placement-associated morphology only; no direction word, ownership, lexeme, plaintext, language, or translation",
        "best_adjusted_feature": min(expected_rows, key=lambda row: row["family_p"]["LENGTH_ADJUSTED"])["feature"] == "ROLE_ATOM:BOUND_E",
        "best_adjusted_p": abs(min(row["family_p"]["LENGTH_ADJUSTED"] for row in expected_rows) - 0.0989990234375) < 1e-15,
        "best_raw_p": abs(min(row["family_p"]["RAW"] for row in expected_rows) - 0.06640625) < 1e-15,
        "zero_pass_rows": all(not row["passes"] for row in expected_rows),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    payload = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "checks": checks,
        "target_result_sha256": sha(TARGET),
        "candidate_count": len(candidates),
        "decision": "VALIDATED_FINAL_NONCONFIRMATION" if all(checks.values()) else "INVALID",
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
