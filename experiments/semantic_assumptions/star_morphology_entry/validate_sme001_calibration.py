#!/usr/bin/env python3
"""Independent, nonimporting reconstruction of SME001 target-free calibration."""

from __future__ import annotations

import hashlib
import json
import math
import multiprocessing as mp
import os
from collections import defaultdict
from pathlib import Path

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
RESULT = HERE / "sme001_calibration_result.json"
OUT = HERE / "sme001_calibration_validation.json"
REPORT = ROOT / "experiments/semantic_assumptions/results/sme001_calibration_validation.md"

EDITIONS = ("ZL3b", "IT2a", "RF1b")
PAGES = (
    "s01r", "s01v", "s02r", "s02v", "s03r", "s04r",
    "s05r", "s05v", "s06r", "s06v", "s07r", "s07v",
)
BASE_RAY = ("7", "8", "8", "7", "7", "8", "7", "8", "8", "7", "8", "7")
RAY_SHIFTS = (0, 3, 7, 1, 9, 5, 2, 10, 6, 4, 11, 8)
TAIL_PAGES = ("s01r", "s01v", "s02r", "s03r", "s04r", "s05r", "s06r", "s06v")
TAIL_HIGH = (
    {1, 4, 7, 10}, {1, 6, 8, 11}, {2, 5, 7, 12}, {3, 4, 9, 10},
    {1, 2, 8, 9}, {3, 6, 7, 12}, {2, 3, 10, 11}, {4, 5, 8, 9},
)
TARGET_SPECS = {
    "RAY_8_MINUS_7": ("7", "8"),
    "TAIL_2_MINUS_1": ("1", "2"),
}
LEVELS = (0.100, 0.149, 0.151, 0.200, 0.300, 0.500)
ROTATION_COUNT = 8192
NUM_TOL = 1e-15
TIE_TOL = 1e-12
FLOAT_TOL = 2e-10

EXPECTED_FILE_HASHES = {
    "experiments/semantic_assumptions/hypotheses/SME001_STAR_MORPHOLOGY_PARAGRAPH_PREREGISTRATION.md": "6a874fe326950a6bf216ff290f99dfaba7e54065097cb4f420dc8126c89719e7",
    "experiments/semantic_assumptions/star_morphology_entry/SME001_CONTROL_SPEC.md": "888159281207b06c7be8c1ecbec4da7a7fb3ba3df787f60f0da88eaa39264bdb",
    "experiments/semantic_assumptions/star_morphology_entry/sme001_core.py": "739eeacd2f8c01a0e9a97e05d9d3b9a165042826a0ac783480c1d1e5ebc0aa44",
    "experiments/semantic_assumptions/star_morphology_entry/run_sme001_anonymous_controls.py": "3153dc7280b226f12d27e79079e2b0000d8cf92b48bc48d4d69d11a03cdaadd9",
    "experiments/semantic_assumptions/star_morphology_entry/sme001_anonymous_control_result.json": "1f074a0aa37f8dd02afa7b77581fdd00d1af056e44466f920c2d0e63529994df",
    "experiments/semantic_assumptions/star_morphology_entry/run_sme001_calibration.py": "6676ebbc88a384af4155c4a4f2ac476859e2d07fca0c6b3ce7e2652c35f738ea",
    "experiments/semantic_assumptions/star_morphology_entry/sme001_calibration_result.json": "6e6a124855d2683c472cc3071414697f4bd85b79c20d8131c8f82f58ccd607ac",
    "experiments/semantic_assumptions/results/sme001_calibration_report.md": "72d1165f9db40765420619296f4e8e6bd1730a0c1e5cd4e8ae90d76be6452df1",
}
OPAQUE_TARGET_HASHES = {
    "target_source_binding.tsv": "315ea24a10995caaa86a77a5a93ecfc0e666351c1ce6a44b078b08686c1d6f3b",
    "target_source_capacity.json": "e2322d841d4af6ca08737697e5eb32a104dd61178ff9f281e879dc0c5c364d44",
    "target_source_validation.json": "38cc174f38607731005e9a2567eed113d02a47114e8640e2e97fc472ede0a74b",
    "anonymous_paragraph_matrix.tsv": "b246456b181b07e847c6d5a49b959b0346eff6a4c6febb8a543de104c505a26a",
    "anonymous_feature_inventory.json": "088232b431b4b9746bb94a08328cb969fb7c21c6a28cd112286da40d6429fea5",
    "anonymous_matrix_capacity.json": "7043fd8d2f8b6b829a2ecd1724b701d3ab811ad4545434720222e1ad03138828",
    "anonymous_matrix_validation.json": "c5a5bb236dd61ecdf8a76ff05e697b8b3a636aa03145fe019a6348fac74aa3d9",
}
TARGET_ARTIFACTS = (
    HERE / "TARGET_RESULT.json",
    HERE / "SME001_TARGET_RESULT.json",
    HERE / "sme001_target_result.tsv",
    ROOT / "experiments/semantic_assumptions/results/sme001_star_morphology_paragraph_result.md",
    ROOT / "experiments/semantic_assumptions/results/sme001_star_morphology_paragraph_validation.md",
)

FIXTURE = None
ROTATIONS_PAGE = None
ROTATIONS_FOLIO = None


def file_hash(path: Path) -> str:
    state = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            state.update(block)
    return state.hexdigest()


def hash_json(value) -> str:
    encoded = json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def stable_noise(domain: str, world: int, feature: str, edition: str, unit: str) -> float:
    payload = f"{domain}|{world}|{feature}|{edition}|{unit}".encode()
    value = int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")
    return 2.0 * value / ((1 << 64) - 1) - 1.0


def unbiased_shift(index: int, key: str, length: int) -> int:
    limit = (1 << 64) - ((1 << 64) % length)
    counter = 0
    while True:
        payload = f"SME001_ROTATION_V1|{index}|{key}|{counter}".encode()
        value = int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")
        if value < limit:
            return value % length
        counter += 1


def make_rotations(coupled: bool) -> np.ndarray:
    output = np.zeros((ROTATION_COUNT, len(PAGES)), dtype=np.uint16)
    if not coupled:
        for index in range(1, ROTATION_COUNT):
            for column, page in enumerate(PAGES):
                output[index, column] = unbiased_shift(index, page, 12)
        return output
    grouped = defaultdict(list)
    for page in PAGES:
        grouped[page[:-1]].append(page)
    page_column = {page: index for index, page in enumerate(PAGES)}
    for index in range(1, ROTATION_COUNT):
        for folio in sorted(grouped):
            phase_bins = math.lcm(*(12 for _page in grouped[folio]))
            phase = unbiased_shift(index, f"FOLIO:{folio}", phase_bins)
            for page in grouped[folio]:
                output[index, page_column[page]] = phase * 12 // phase_bins
    return output


def rotation_digest(rotations: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(rotations, dtype="<u2", order="C").tobytes()).hexdigest()


def build_fixture() -> dict:
    unit_ids, pages, folios, ordinals, rays, tails = [], [], [], [], [], []
    tail_positions = dict(zip(TAIL_PAGES, TAIL_HIGH))
    for page_index, page in enumerate(PAGES):
        shift = RAY_SHIFTS[page_index]
        sequence = BASE_RAY[shift:] + BASE_RAY[:shift]
        for ordinal in range(1, 13):
            unit_ids.append(f"{page}.S{ordinal:02d}")
            pages.append(page)
            folios.append(page[:-1])
            ordinals.append(ordinal)
            ray = sequence[ordinal - 1]
            if page == "s01r" and ordinal == 5:
                ray = "6"
            if page == "s02v" and ordinal == 11:
                ray = "9"
            rays.append(ray)
            tail = "2" if ordinal in tail_positions.get(page, set()) else "1"
            if page == "s07r" and ordinal == 12:
                tail = "-"
            tails.append(tail)
    page_rows = {
        page: np.asarray([index for index, value in enumerate(pages) if value == page], dtype=np.int64)
        for page in PAGES
    }
    return {
        "unit_ids": unit_ids,
        "pages": pages,
        "folios": folios,
        "ordinals": np.asarray(ordinals, dtype=np.int64),
        "labels": {"RAY_8_MINUS_7": rays, "TAIL_2_MINUS_1": tails},
        "page_rows": page_rows,
        "page_column": {page: index for index, page in enumerate(PAGES)},
    }


def page_centered_scale(values: np.ndarray) -> np.ndarray:
    residual = np.empty_like(values)
    for page in PAGES:
        indices = FIXTURE["page_rows"][page]
        residual[indices] = values[indices] - values[indices].mean(axis=0, keepdims=True)
    return np.sqrt(np.mean(residual * residual, axis=0))


def variable_folios(values: np.ndarray) -> np.ndarray:
    per_folio = defaultdict(lambda: np.zeros((len(EDITIONS), values.shape[2]), dtype=bool))
    for page in PAGES:
        indices = FIXTURE["page_rows"][page]
        per_folio[page[:-1]] |= np.ptp(values[indices], axis=0) > NUM_TOL
    return np.sum(np.stack([per_folio[folio] for folio in sorted(per_folio)]), axis=0)


def page_contrasts(labels: list[str], values: np.ndarray, low: str, high: str):
    answer = {}
    informative = []
    for page in PAGES:
        indices = FIXTURE["page_rows"][page]
        sequence = np.asarray([labels[index] for index in indices], dtype=object)
        if low not in sequence or high not in sequence:
            continue
        informative.append(page)
        page_values = values[indices]
        contrasts = np.empty((12, len(EDITIONS), values.shape[2]), dtype=np.float64)
        for shift in range(12):
            rotated = np.roll(sequence, -shift)
            contrasts[shift] = (
                page_values[rotated == high].mean(axis=0)
                - page_values[rotated == low].mean(axis=0)
            )
        answer[page] = contrasts
    return answer, informative


def aggregate(page_values: dict, informative: list[str], rotations: np.ndarray) -> np.ndarray:
    folio_pages = defaultdict(list)
    for page in informative:
        folio_pages[page[:-1]].append(page)
    shape = next(iter(page_values.values())).shape[1:]
    result = np.zeros((rotations.shape[0], *shape), dtype=np.float64)
    for folio in sorted(folio_pages):
        current = np.zeros_like(result)
        for page in folio_pages[folio]:
            current += page_values[page][rotations[:, FIXTURE["page_column"][page]]]
        result += current / len(folio_pages[folio])
    return result / len(folio_pages)


def physical_effect(labels, values, low, high):
    contrasts, informative = page_contrasts(labels, values, low, high)
    return aggregate(contrasts, informative, np.zeros((1, len(PAGES)), dtype=np.uint16))[0]


def ordinal_residual(values: np.ndarray) -> np.ndarray:
    ordinals = FIXTURE["ordinals"]
    columns = [(ordinals == level).astype(np.float64) for level in range(2, 13)]
    relative = (ordinals - 0.5) / 12.0
    columns.extend((relative, relative ** 2, relative ** 3))
    columns.append((ordinals % 2 == 1).astype(np.float64))
    columns.append((ordinals <= 6).astype(np.float64))
    quarter = np.minimum((relative * 4).astype(np.int64), 3)
    columns.extend((quarter == value).astype(np.float64) for value in (1, 2, 3))
    design = np.stack(columns, axis=1)
    centered_design = np.empty_like(design)
    centered_values = np.empty_like(values)
    for page in PAGES:
        indices = FIXTURE["page_rows"][page]
        centered_design[indices] = design[indices] - design[indices].mean(axis=0, keepdims=True)
        centered_values[indices] = values[indices] - values[indices].mean(axis=0, keepdims=True)
    flat = centered_values.reshape(len(ordinals), -1)
    coefficients = np.linalg.lstsq(centered_design, flat, rcond=None)[0]
    return (flat - centered_design @ coefficients).reshape(values.shape)


def subset_effect(labels, values, low, high, name):
    per_folio = defaultdict(list)
    for page in PAGES:
        indices = FIXTURE["page_rows"][page]
        if name == "ODD":
            indices = indices[FIXTURE["ordinals"][indices] % 2 == 1]
        elif name == "EVEN":
            indices = indices[FIXTURE["ordinals"][indices] % 2 == 0]
        elif name == "EARLY":
            indices = indices[FIXTURE["ordinals"][indices] <= 6]
        else:
            indices = indices[FIXTURE["ordinals"][indices] > 6]
        sequence = np.asarray([labels[index] for index in indices], dtype=object)
        if low not in sequence or high not in sequence:
            continue
        per_folio[page[:-1]].append(
            values[indices[sequence == high]].mean(axis=0)
            - values[indices[sequence == low]].mean(axis=0)
        )
    if not per_folio:
        return None, 0
    return np.mean([
        np.mean(per_folio[folio], axis=0) for folio in sorted(per_folio)
    ], axis=0), len(per_folio)


def common_statistics(values: np.ndarray) -> dict:
    scale = page_centered_scale(values)
    variation = variable_folios(values)
    base_eligible = np.all(variation >= 4, axis=0) & np.all(scale > NUM_TOL, axis=0)
    residual = ordinal_residual(values)
    targets = {}
    zero = np.zeros((1, len(PAGES)), dtype=np.uint16)
    for target, (low, high) in TARGET_SPECS.items():
        labels = FIXTURE["labels"][target]
        contrasts, informative = page_contrasts(labels, values, low, high)
        observed = aggregate(contrasts, informative, zero)[0]
        direction = np.zeros(values.shape[2], dtype=np.int8)
        direction[np.all(observed > NUM_TOL, axis=0)] = 1
        direction[np.all(observed < -NUM_TOL, axis=0)] = -1
        material = np.zeros(values.shape[2])
        material[base_eligible] = np.min(
            np.abs(observed[:, base_eligible]) / scale[:, base_eligible], axis=0
        )
        residual_contrasts, residual_informative = page_contrasts(labels, residual, low, high)
        residual_effect = aggregate(residual_contrasts, residual_informative, zero)[0]
        residual_material = np.zeros(values.shape[2])
        residual_material[base_eligible] = np.min(
            np.abs(residual_effect[:, base_eligible]) / scale[:, base_eligible], axis=0
        )
        ordinal_ok = (
            (direction != 0)
            & np.all(residual_effect * direction[None, :] > NUM_TOL, axis=0)
            & (residual_material >= 0.15)
        )
        subset_ok = direction != 0
        for name in ("ODD", "EVEN", "EARLY", "LATE"):
            effect, folio_count = subset_effect(labels, values, low, high, name)
            subset_ok &= (
                folio_count >= 4
                and np.all(effect * direction[None, :] > NUM_TOL, axis=0)
            )
        per_folio_lists = defaultdict(list)
        for page in informative:
            per_folio_lists[page[:-1]].append(contrasts[page][0])
        per_folio = {
            folio: np.mean(per_folio_lists[folio], axis=0)
            for folio in sorted(per_folio_lists)
        }
        folios = sorted(per_folio)
        deletion_ok = direction != 0
        for omitted in folios:
            effect = np.mean([per_folio[folio] for folio in folios if folio != omitted], axis=0)
            deletion_ok &= np.all(effect * direction[None, :] > NUM_TOL, axis=0)
        common_support = np.zeros(values.shape[2], dtype=np.int64)
        for folio in folios:
            common_support += np.all(
                per_folio[folio] * direction[None, :] > NUM_TOL, axis=0
            )
        required = 5 if target.startswith("RAY_") else 4
        targets[target] = {
            "contrasts": contrasts,
            "informative": informative,
            "observed": observed,
            "direction": direction,
            "material": material,
            "residual_material": residual_material,
            "ordinal_ok": ordinal_ok,
            "subset_ok": subset_ok,
            "deletion_ok": deletion_ok,
            "common_support": common_support,
            "support_ok": (direction != 0) & (common_support >= required),
        }
    return {"scale": scale, "base_eligible": base_eligible, "targets": targets}


def robust_statistic(z: np.ndarray) -> np.ndarray:
    return np.maximum(np.maximum(np.min(z, axis=1), np.min(-z, axis=1)), 0.0)


def score_ensemble(common: dict, rotations: np.ndarray) -> dict:
    calculated = {}
    robust_null = {}
    for target, shared in common["targets"].items():
        effects = aggregate(shared["contrasts"], shared["informative"], rotations)
        sums = np.zeros_like(effects[0])
        sums_sq = np.zeros_like(effects[0])
        for start in range(1, ROTATION_COUNT, 2048):
            chunk = effects[start:start + 2048]
            sums += chunk.sum(axis=0)
            sums_sq += np.square(chunk).sum(axis=0)
        mean = sums / (ROTATION_COUNT - 1)
        variance = np.maximum(sums_sq / (ROTATION_COUNT - 1) - mean * mean, 0.0)
        sd = np.sqrt(variance)
        eligible = common["base_eligible"] & np.all(sd > NUM_TOL, axis=0)
        z_observed = np.divide(
            shared["observed"] - mean, sd,
            out=np.zeros_like(mean), where=sd > NUM_TOL,
        )
        observed_robust = robust_statistic(z_observed[None, :, :])[0]
        z_null = np.divide(
            effects[1:] - mean[None, :, :], sd[None, :, :],
            out=np.zeros_like(effects[1:]), where=sd[None, :, :] > NUM_TOL,
        )
        null_robust = robust_statistic(z_null)
        null_robust[:, ~eligible] = 0.0
        calculated[target] = {
            "eligible": eligible,
            "z": z_observed,
            "robust": observed_robust,
            "raw_p": (
                1 + np.sum(null_robust >= observed_robust[None, :] - TIE_TOL, axis=0)
            ) / ROTATION_COUNT,
        }
        robust_null[target] = null_robust
    family_max = np.zeros(ROTATION_COUNT - 1)
    for target, item in calculated.items():
        if np.any(item["eligible"]):
            family_max = np.maximum(
                family_max, np.max(robust_null[target][:, item["eligible"]], axis=1)
            )
    output = {}
    for target, item in calculated.items():
        shared = common["targets"][target]
        family_p = (
            1 + np.sum(family_max[:, None] >= item["robust"][None, :] - TIE_TOL, axis=0)
        ) / ROTATION_COUNT
        direction = shared["direction"]
        z_direction = (
            (direction != 0)
            & np.all(item["z"] * direction[None, :] > NUM_TOL, axis=0)
        )
        gates = {
            "eligible": item["eligible"],
            "same_reading_direction": direction != 0,
            "z_matches_raw_direction": z_direction,
            "robust_z": item["robust"] >= 2.5,
            "raw_p": item["raw_p"] <= 0.01,
            "family_p": family_p <= 0.05,
            "material": shared["material"] >= 0.15,
            "parity_and_early_late": shared["subset_ok"],
            "folio_deletions": shared["deletion_ok"],
            "folio_support": shared["support_ok"],
            "ordinal_residual_material": shared["ordinal_ok"],
            "root_length_residual": np.ones(len(item["eligible"]), dtype=bool),
        }
        passing = np.logical_and.reduce(list(gates.values()))
        output[target] = {
            "z": item["z"],
            "robust": item["robust"],
            "raw_p": item["raw_p"],
            "family_p": family_p,
            "gates": gates,
            "passing": passing,
        }
    return output


def compact_row(common: dict, scored: dict, target: str, feature_index: int) -> dict:
    shared = common["targets"][target]
    item = scored[target]
    return {
        "effects": {edition: float(shared["observed"][i, feature_index]) for i, edition in enumerate(EDITIONS)},
        "z": {edition: float(item["z"][i, feature_index]) for i, edition in enumerate(EDITIONS)},
        "robust_z": float(item["robust"][feature_index]),
        "raw_p": float(item["raw_p"][feature_index]),
        "family_p": float(item["family_p"][feature_index]),
        "material_effect": float(shared["material"][feature_index]),
        "ordinal_residual_material_effect": float(shared["residual_material"][feature_index]),
        "common_folio_support_count": int(shared["common_support"][feature_index]),
        "statistical_gates": {
            name: bool(values[feature_index]) for name, values in item["gates"].items()
        },
        "statistical_passes": bool(item["passing"][feature_index]),
    }


def make_null_values(world: int):
    features = ["PARA_WORD_COUNT"] + [f"FORMAL_NULL_WORLD_{index:03d}" for index in range(83)]
    values = np.empty((144, len(EDITIONS), len(features)), dtype=np.float64)
    for row, unit in enumerate(FIXTURE["unit_ids"]):
        for edition_index, edition in enumerate(EDITIONS):
            noise = stable_noise("SME001_NULL_WORLD_V1", world, "PARA_WORD_COUNT", edition, unit)
            values[row, edition_index, 0] = 40.0 + int((noise + 1.0) * 5.0)
            for feature_index, feature in enumerate(features[1:], 1):
                values[row, edition_index, feature_index] = 0.5 + 0.1 * stable_noise(
                    "SME001_NULL_WORLD_V1", world, feature, edition, unit
                )
    return features, values


def centered_signal_noise(world: int, target: str) -> np.ndarray:
    values = np.empty((144, len(EDITIONS)), dtype=np.float64)
    labels = FIXTURE["labels"][target]
    low, high = TARGET_SPECS[target]
    for row, unit in enumerate(FIXTURE["unit_ids"]):
        for edition_index, edition in enumerate(EDITIONS):
            values[row, edition_index] = stable_noise(
                "SME001_POWER_GRID_V1", world, target, edition, unit
            )
    for page in PAGES:
        indices = FIXTURE["page_rows"][page]
        for edition_index in range(len(EDITIONS)):
            for label in (low, high):
                group = np.asarray([index for index in indices if labels[index] == label])
                if len(group):
                    values[group, edition_index] -= values[group, edition_index].mean()
    return values


def signal_material(labels, values, low, high) -> float:
    effect = physical_effect(labels, values[:, :, None], low, high)[:, 0]
    scale = page_centered_scale(values[:, :, None])[:, 0]
    return float(np.min(np.abs(effect) / scale))


def calibrated_signal(world: int, target: str, requested: float):
    labels = FIXTURE["labels"][target]
    low, high = TARGET_SPECS[target]
    score = np.asarray([
        -1.0 if label == low else 1.0 if label == high else 0.0
        for label in labels
    ])
    base = centered_signal_noise(world, target)
    lower, upper = 0.0, 10.0
    for _ in range(80):
        middle = (lower + upper) / 2.0
        material = signal_material(labels, base + middle * score[:, None], low, high)
        if material < requested:
            lower = middle
        else:
            upper = middle
    values = base + upper * score[:, None]
    return values, upper, signal_material(labels, values, low, high)


def make_power_values(target: str, world: int, requested: float):
    features = ["PARA_WORD_COUNT", "FORMAL_GRID_SIGNAL"] + [
        f"FORMAL_GRID_NULL_{index:03d}" for index in range(82)
    ]
    values = np.empty((144, len(EDITIONS), len(features)), dtype=np.float64)
    signal, amplitude, material = calibrated_signal(world, target, requested)
    values[:, :, 1] = signal
    for row, unit in enumerate(FIXTURE["unit_ids"]):
        for edition_index, edition in enumerate(EDITIONS):
            noise = stable_noise("SME001_POWER_GRID_NULL_V1", world, "PARA_WORD_COUNT", edition, unit)
            values[row, edition_index, 0] = 40.0 + int((noise + 1.0) * 5.0)
            for feature_index, feature in enumerate(features[2:], 2):
                values[row, edition_index, feature_index] = 0.5 + 0.1 * stable_noise(
                    "SME001_POWER_GRID_NULL_V1", world, feature, edition, unit
                )
    return features, values, amplitude, material


def reconstruct_task(task):
    kind = task[0]
    if kind == "null":
        world = task[1]
        _features, values = make_null_values(world)
        common = common_statistics(values)
        page = score_ensemble(common, ROTATIONS_PAGE)
        folio = score_ensemble(common, ROTATIONS_FOLIO)
        page_pass = {
            (target, feature)
            for target in TARGET_SPECS
            for feature in range(84)
            if page[target]["passing"][feature]
        }
        folio_pass = {
            (target, feature)
            for target in TARGET_SPECS
            for feature in range(84)
            if folio[target]["passing"][feature]
        }
        names = ["PARA_WORD_COUNT"] + [f"FORMAL_NULL_WORLD_{index:03d}" for index in range(83)]
        return {
            "kind": "null", "world": world,
            "page_pass_count": len(page_pass), "folio_pass_count": len(folio_pass),
            "joint_passing": [
                [target, names[index]] for target, index in sorted(page_pass & folio_pass)
            ],
        }
    target, world, requested = task[1:]
    _features, values, amplitude, material = make_power_values(target, world, requested)
    common = common_statistics(values)
    page = score_ensemble(common, ROTATIONS_PAGE)
    folio = score_ensemble(common, ROTATIONS_FOLIO)
    page_row = compact_row(common, page, target, 1)
    folio_row = compact_row(common, folio, target, 1)
    return {
        "kind": "power", "target": target, "world": world,
        "requested_material": requested, "calibrated_material": material,
        "amplitude": amplitude, "page": page_row, "folio": folio_row,
        "joint_pass": bool(page_row["statistical_passes"] and folio_row["statistical_passes"]),
    }


def close_float(left, right) -> bool:
    return math.isclose(float(left), float(right), rel_tol=0.0, abs_tol=FLOAT_TOL)


def compare_power(actual: dict, expected: dict) -> tuple[bool, int]:
    comparisons = 0
    for key in ("kind", "target", "world", "requested_material", "joint_pass"):
        comparisons += 1
        if actual[key] != expected[key]:
            return False, comparisons
    for key in ("amplitude", "calibrated_material"):
        comparisons += 1
        if not close_float(actual[key], expected[key]):
            return False, comparisons
    for mode in ("page", "folio"):
        left, right = actual[mode], expected[mode]
        for key in ("effects", "z"):
            for edition in EDITIONS:
                comparisons += 1
                if not close_float(left[key][edition], right[key][edition]):
                    return False, comparisons
        for key in (
            "robust_z", "raw_p", "family_p", "material_effect",
            "ordinal_residual_material_effect",
        ):
            comparisons += 1
            if not close_float(left[key], right[key]):
                return False, comparisons
        comparisons += 1
        if left["common_folio_support_count"] != right["common_folio_support_count"]:
            return False, comparisons
        comparisons += len(right["statistical_gates"])
        if left["statistical_gates"] != right["statistical_gates"]:
            return False, comparisons
        comparisons += 1
        if left["statistical_passes"] != right["statistical_passes"]:
            return False, comparisons
    return True, comparisons


def main() -> None:
    checks = {}

    def check(name: str, condition: bool) -> None:
        checks[name] = bool(condition)
        if not condition:
            raise AssertionError(name)

    actual_file_hashes = {
        relative: file_hash(ROOT / relative) for relative in EXPECTED_FILE_HASHES
    }
    check("frozen source result and script hashes", actual_file_hashes == EXPECTED_FILE_HASHES)
    actual_target_hashes = {
        name: file_hash(HERE / name) for name in OPAQUE_TARGET_HASHES
    }
    check("opaque target file hashes", actual_target_hashes == OPAQUE_TARGET_HASHES)
    check("target artifacts absent before reconstruction", all(not path.exists() for path in TARGET_ARTIFACTS))

    stored = json.loads(RESULT.read_text(encoding="utf-8"))
    check("stored target non-parsing and non-join", stored["target_files_parsed"] is False and stored["target_join_performed"] is False)
    check("stored world and family contract", (
        stored["rotation_count_per_ensemble"] == 8192
        and stored["null_world_count"] == 64
        and stored["power_worlds_per_level"] == 8
        and stored["levels"] == list(LEVELS)
        and len(stored["null_worlds"]) == 64
        and len(stored["power_worlds"]) == 96
    ))

    global FIXTURE, ROTATIONS_PAGE, ROTATIONS_FOLIO
    FIXTURE = build_fixture()
    ROTATIONS_PAGE = make_rotations(False)
    ROTATIONS_FOLIO = make_rotations(True)
    page_digest = rotation_digest(ROTATIONS_PAGE)
    folio_digest = rotation_digest(ROTATIONS_FOLIO)
    check("independent page rotation shape and digest", (
        ROTATIONS_PAGE.shape == (8192, 12)
        and page_digest == stored["page_rotation_digest"]
        and page_digest == "ff5d289a083fea9d23837255297f8017b183d8f9751cc7d09248dcdfe7e6de70"
    ))
    check("coupled folio rotation shape and digest", (
        ROTATIONS_FOLIO.shape == (8192, 12)
        and folio_digest == stored["folio_rotation_digest"]
        and folio_digest == "baa9452729e09f4cacd1102fac241bbc2622bd28bf6682d0b76cd9f9a332509c"
    ))
    check("physical rows and coupled equal-page phases", (
        np.all(ROTATIONS_PAGE[0] == 0)
        and np.all(ROTATIONS_FOLIO[0] == 0)
        and all(
            np.array_equal(
                ROTATIONS_FOLIO[:, PAGES.index(page)],
                ROTATIONS_FOLIO[:, PAGES.index(page[:-1] + "v")],
            )
            for page in PAGES if page.endswith("r") and page[:-1] + "v" in PAGES
        )
    ))

    tasks = [("null", world) for world in range(64)]
    tasks.extend(
        ("power", target, world, level)
        for target in TARGET_SPECS for world in range(8) for level in LEVELS
    )
    workers = min(16, os.cpu_count() or 1)
    with mp.get_context("fork").Pool(workers) as pool:
        reconstructed = list(pool.imap_unordered(reconstruct_task, tasks, chunksize=1))
    null_worlds = sorted(
        (row for row in reconstructed if row["kind"] == "null"),
        key=lambda row: row["world"],
    )
    power_worlds = sorted(
        (row for row in reconstructed if row["kind"] == "power"),
        key=lambda row: (row["target"], row["world"], row["requested_material"]),
    )
    check("all 160 worlds independently reconstructed", len(null_worlds) == 64 and len(power_worlds) == 96)
    check("all null-world pass sets exact", null_worlds == stored["null_worlds"])

    numeric_comparisons = 0
    exact_power = True
    for actual, expected in zip(power_worlds, stored["power_worlds"]):
        matched, compared = compare_power(actual, expected)
        numeric_comparisons += compared
        exact_power &= matched
    check("all stored power statistics and gates reproduced", exact_power)
    check("all requested-material bisections reproduced", all(
        abs(row["calibrated_material"] - row["requested_material"]) <= 1e-6
        for row in power_worlds
    ))

    joint_counts = {
        target: {
            f"{level:.3f}": sum(
                row["joint_pass"] for row in power_worlds
                if row["target"] == target and row["requested_material"] == level
            )
            for level in LEVELS
        }
        for target in TARGET_SPECS
    }
    null_joint_worlds = [row["world"] for row in null_worlds if row["joint_passing"]]
    check("null joint-world count and acceptance exact", (
        null_joint_worlds == stored["null_worlds_with_joint_pass"] == []
        and len(null_joint_worlds) <= 8
    ))
    check("power joint-pass counts exact", joint_counts == stored["joint_pass_counts"])
    reconstructed_checks = {
        "world_counts": len(null_worlds) == 64 and len(power_worlds) == 96,
        "full_family": all(
            not row["joint_passing"] or all(len(pair) == 2 for pair in row["joint_passing"])
            for row in null_worlds
        ),
        "null_world_acceptance": len(null_joint_worlds) <= 8,
        "material_bisection": all(
            abs(row["calibrated_material"] - row["requested_material"]) <= 1e-6
            for row in power_worlds
        ),
        "below_boundary_zero_pass": all(
            not row["joint_pass"] for row in power_worlds if row["requested_material"] < 0.15
        ),
        "nondecreasing_ray_power": all(
            joint_counts["RAY_8_MINUS_7"][f"{left:.3f}"]
            <= joint_counts["RAY_8_MINUS_7"][f"{right:.3f}"]
            for left, right in zip(LEVELS, LEVELS[1:])
        ),
        "nondecreasing_tail_power": all(
            joint_counts["TAIL_2_MINUS_1"][f"{left:.3f}"]
            <= joint_counts["TAIL_2_MINUS_1"][f"{right:.3f}"]
            for left, right in zip(LEVELS, LEVELS[1:])
        ),
        "ray_high_power": joint_counts["RAY_8_MINUS_7"]["0.500"] >= 7,
        "tail_high_power": joint_counts["TAIL_2_MINUS_1"]["0.500"] >= 6,
        "target_artifacts_absent": all(not path.exists() for path in TARGET_ARTIFACTS),
        "frozen_target_hashes": actual_target_hashes == OPAQUE_TARGET_HASHES,
    }
    check("every stored calibration gate exact", reconstructed_checks == stored["checks"])
    failures = sorted(name for name, passed in reconstructed_checks.items() if not passed)
    check("underpowered failure and decision exact", (
        failures == stored["failures"] == ["ray_high_power", "tail_high_power"]
        and stored["status"] == "FAIL_TARGET_FREE_NULL_AND_POWER_CALIBRATION"
    ))
    check("target artifacts absent after reconstruction", all(not path.exists() for path in TARGET_ARTIFACTS))

    payload = {
        "experiment": "SME001",
        "status": "PASS_INDEPENDENT_VALIDATION_OF_UNDERPOWERED_DECISION",
        "nonimporting": True,
        "target_files_parsed": False,
        "target_join_performed": False,
        "workers": workers,
        "checks": checks,
        "check_count": len(checks),
        "source_result_script_hashes": actual_file_hashes,
        "opaque_target_hashes": actual_target_hashes,
        "validator_sha256": file_hash(Path(__file__)),
        "page_rotation_digest": page_digest,
        "folio_rotation_digest": folio_digest,
        "null_worlds_reconstructed": len(null_worlds),
        "power_worlds_reconstructed": len(power_worlds),
        "coverage": {
            "null": (
                "64 worlds x 2 ensembles x 2 targets x 84 features = 21,504 "
                "target-feature ensemble rows; all statistics and gates were recomputed, "
                "while the stored artifact exposes final page/folio pass counts and joint sets"
            ),
            "power": (
                "96 worlds x 2 ensembles x 2 targets x 84 features = 32,256 "
                "target-feature ensemble rows; full-family maxima were recomputed and all "
                "5,472 stored planted-row fields/comparisons were checked"
            ),
        },
        "stored_power_field_comparisons": numeric_comparisons,
        "null_world_summary_sha256": hash_json(null_worlds),
        "power_world_summary_sha256": hash_json(power_worlds),
        "null_worlds_with_joint_pass": null_joint_worlds,
        "joint_pass_counts": joint_counts,
        "reconstructed_calibration_checks": reconstructed_checks,
        "reconstructed_failures": failures,
        "decision": "UNDERPOWERED_TARGET_FORBIDDEN",
        "target_artifact_absence": {
            str(path.relative_to(ROOT)): not path.exists() for path in TARGET_ARTIFACTS
        },
        "claim_ceiling": "independent validation of synthetic calibration failure only; no manuscript association or meaning",
    }
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# SME001 calibration independent validation\n\n"
        f"**PASS — {len(checks)}/{len(checks)} nonimporting checks validate the underpowered decision.**\n\n"
        "A separate implementation reconstructed both 8,192-assignment phase ensembles, "
        "all 64 complete 84-feature null worlds, all 96 target/strength power worlds, "
        "every stored planted-row statistic and gate, requested-material bisections, joint "
        "pass counts, calibration gates, and the two high-power failures. The seven frozen "
        "manuscript-side inputs were read only as opaque bytes for SHA-256; no target row "
        "or anonymous feature value was parsed or joined, and no target artifact exists.\n\n"
        "Coverage was complete: 21,504 null and 32,256 power target-feature/ensemble rows "
        "were rescored. The null artifact stores only final page/folio pass counts and joint "
        "sets; those matched exactly. For power worlds, all full-family maxima were rebuilt "
        "and all 5,472 stored planted-row field comparisons matched.\n\n"
        "The reconstruction confirms 0/64 null worlds with a joint pass, but only 5/8 ray "
        "and 0/8 tail worlds passing at requested material .500, below the frozen 7/8 and "
        "6/8 requirements. SME001 therefore closes as underpowered without a manuscript score.\n\n"
        "This validates synthetic calibration behavior only and supplies no manuscript "
        "association, marker function, meaning, lexeme, plaintext, language, or translation.\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": payload["status"],
        "checks": len(checks),
        "null_worlds": len(null_worlds),
        "power_worlds": len(power_worlds),
        "failures": failures,
        "target_join_performed": False,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
