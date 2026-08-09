#!/usr/bin/env python3
"""Frozen scoring primitives for SME001. This module performs no file I/O."""

from __future__ import annotations

import hashlib
import math
from collections import defaultdict

import numpy as np

EDITIONS = ("ZL3b", "IT2a", "RF1b")
ROTATION_DOMAIN = "SME001_ROTATION_V1"
TIE_TOL = 1e-12
NUM_TOL = 1e-15


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _unbiased_shift(index: int, page: str, length: int) -> int:
    require(index >= 1 and length >= 1, "invalid rotation index or length")
    limit = (1 << 64) - ((1 << 64) % length)
    counter = 0
    while True:
        payload = f"{ROTATION_DOMAIN}|{index}|{page}|{counter}".encode()
        value = int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")
        if value < limit:
            return value % length
        counter += 1


def make_rotations(pages: list[str], lengths: dict[str, int], total: int) -> np.ndarray:
    """Return physical row zero plus deterministic random rotations."""
    require(total >= 2 and pages == sorted(pages), "invalid page rotation request")
    require(
        all(1 <= lengths[page] <= np.iinfo(np.uint16).max for page in pages),
        "invalid page length",
    )
    out = np.zeros((total, len(pages)), dtype=np.uint16)
    for index in range(1, total):
        for column, page in enumerate(pages):
            out[index, column] = _unbiased_shift(index, page, lengths[page])
    return out


def make_folio_phase_rotations(
    pages: list[str], lengths: dict[str, int], page_folio: dict[str, str], total: int,
) -> np.ndarray:
    """Return rotations coupled to one exact normalized phase per folio."""
    require(total >= 2 and pages == sorted(pages), "invalid folio rotation request")
    require(set(page_folio) == set(pages), "incomplete page-folio map")
    grouped = defaultdict(list)
    for page in pages:
        require(1 <= lengths[page] <= np.iinfo(np.uint16).max, "invalid page length")
        grouped[page_folio[page]].append(page)
    out = np.zeros((total, len(pages)), dtype=np.uint16)
    page_column = {page: index for index, page in enumerate(pages)}
    for index in range(1, total):
        for folio in sorted(grouped):
            phase_bins = math.lcm(*(lengths[page] for page in grouped[folio]))
            phase = _unbiased_shift(index, f"FOLIO:{folio}", phase_bins)
            for page in grouped[folio]:
                out[index, page_column[page]] = phase * lengths[page] // phase_bins
    return out


def rotation_digest(rotations: np.ndarray) -> str:
    canonical = np.asarray(rotations, dtype="<u2", order="C")
    return hashlib.sha256(canonical.tobytes()).hexdigest()


def matrix_contract(unit_ids, pages_by_unit, folios_by_unit, ordinals, values, features) -> bool:
    unit_ids = list(unit_ids)
    pages_by_unit = list(pages_by_unit)
    folios_by_unit = list(folios_by_unit)
    ordinals = np.asarray(ordinals)
    values = np.asarray(values)
    if len(unit_ids) == 0 or len(unit_ids) != len(set(unit_ids)):
        return False
    if not (len(unit_ids) == len(pages_by_unit) == len(folios_by_unit) == len(ordinals) == values.shape[0]):
        return False
    if values.ndim != 3 or values.shape[1] != len(EDITIONS) or values.shape[2] != len(features):
        return False
    if len(features) != len(set(features)) or not np.isfinite(values).all():
        return False
    if any(folio != page[:-1] for folio, page in zip(folios_by_unit, pages_by_unit)):
        return False
    grouped = defaultdict(list)
    for page, ordinal in zip(pages_by_unit, ordinals):
        if int(ordinal) != ordinal or ordinal < 1:
            return False
        grouped[page].append(int(ordinal))
    return all(sorted(items) == list(range(1, len(items) + 1)) for items in grouped.values())


def exact_matrix_contract(
    unit_ids, pages_by_unit, folios_by_unit, ordinals, values, features,
    expected_rows,
) -> bool:
    """Require the ordinary contract and one exact predeclared row sequence."""
    if not matrix_contract(
        unit_ids, pages_by_unit, folios_by_unit, ordinals, values, features
    ):
        return False
    observed = [
        (str(unit), str(page), str(folio), int(ordinal))
        for unit, page, folio, ordinal in zip(
            unit_ids, pages_by_unit, folios_by_unit, ordinals
        )
    ]
    expected = [
        (str(unit), str(page), str(folio), int(ordinal))
        for unit, page, folio, ordinal in expected_rows
    ]
    return observed == expected and len(expected) == len(set(expected))


def _page_layout(pages_by_unit, folios_by_unit, ordinals):
    pages = sorted(set(pages_by_unit))
    page_indices = {}
    page_folio = {}
    for page in pages:
        indices = [i for i, value in enumerate(pages_by_unit) if value == page]
        indices.sort(key=lambda i: int(ordinals[i]))
        assert [int(ordinals[i]) for i in indices] == list(range(1, len(indices) + 1))
        page_indices[page] = np.asarray(indices, dtype=np.int64)
        folios = {folios_by_unit[i] for i in indices}
        assert len(folios) == 1
        page_folio[page] = next(iter(folios))
    return pages, page_indices, page_folio


def _page_contrasts(labels, values, pages, page_indices, low, high):
    answer = {}
    informative = []
    for page in pages:
        indices = page_indices[page]
        seq = np.asarray([labels[i] for i in indices], dtype=object)
        if low not in seq or high not in seq:
            continue
        informative.append(page)
        page_values = values[indices, :, :]
        contrasts = np.empty((len(indices), values.shape[1], values.shape[2]), dtype=np.float64)
        for shift in range(len(indices)):
            rotated = np.roll(seq, -shift)
            lo = rotated == low
            hi = rotated == high
            assert lo.any() and hi.any()
            contrasts[shift] = page_values[hi].mean(axis=0) - page_values[lo].mean(axis=0)
        answer[page] = contrasts
    return answer, informative


def _aggregate_effects(page_contrasts, informative_pages, page_folio, pages, shifts):
    page_column = {page: index for index, page in enumerate(pages)}
    folio_pages = defaultdict(list)
    for page in informative_pages:
        folio_pages[page_folio[page]].append(page)
    assert folio_pages
    n = shifts.shape[0]
    sample = next(iter(page_contrasts.values()))
    result = np.zeros((n, sample.shape[1], sample.shape[2]), dtype=np.float64)
    for folio in sorted(folio_pages):
        current = np.zeros_like(result)
        for page in folio_pages[folio]:
            current += page_contrasts[page][shifts[:, page_column[page]]]
        result += current / len(folio_pages[folio])
    return result / len(folio_pages)


def _observed_per_folio(page_contrasts, informative_pages, page_folio):
    grouped = defaultdict(list)
    for page in informative_pages:
        grouped[page_folio[page]].append(page_contrasts[page][0])
    return {folio: np.mean(grouped[folio], axis=0) for folio in sorted(grouped)}


def _page_centered_scale(values, pages_by_unit):
    residual = np.empty_like(values, dtype=np.float64)
    for page in sorted(set(pages_by_unit)):
        indices = np.asarray([i for i, value in enumerate(pages_by_unit) if value == page], dtype=np.int64)
        residual[indices] = values[indices] - values[indices].mean(axis=0, keepdims=True)
    return np.sqrt(np.mean(residual * residual, axis=0))


def _variable_folios(values, pages_by_unit, folios_by_unit):
    result = np.zeros((values.shape[1], values.shape[2]), dtype=np.int64)
    for edition in range(values.shape[1]):
        for feature in range(values.shape[2]):
            folios = set()
            for page in sorted(set(pages_by_unit)):
                indices = [i for i, value in enumerate(pages_by_unit) if value == page]
                if np.ptp(values[indices, edition, feature]) > NUM_TOL:
                    folios.add(folios_by_unit[indices[0]])
            result[edition, feature] = len(folios)
    return result


def _robust(z):
    positive = np.min(z, axis=1)
    negative = np.min(-z, axis=1)
    return np.maximum(np.maximum(positive, negative), 0.0)


def raw_direction(effects) -> int:
    effects = np.asarray(effects, dtype=np.float64)
    signs = np.sign(effects[np.abs(effects) > NUM_TOL])
    return int(signs[0]) if len(signs) == len(EDITIONS) and np.all(signs == signs[0]) else 0


def z_matches_raw_direction(z, direction: int) -> bool:
    z = np.asarray(z, dtype=np.float64)
    return bool(direction != 0 and np.all(z * direction > NUM_TOL))


def _subset_effect(labels, values, pages, page_indices, page_folio, low, high, keep):
    per_folio = defaultdict(list)
    for page in pages:
        indices = np.asarray([index for index in page_indices[page] if keep(index)], dtype=np.int64)
        if len(indices) == 0:
            continue
        page_labels = np.asarray([labels[index] for index in indices], dtype=object)
        lo = page_labels == low
        hi = page_labels == high
        if not lo.any() or not hi.any():
            continue
        contrast = values[indices[hi]].mean(axis=0) - values[indices[lo]].mean(axis=0)
        per_folio[page_folio[page]].append(contrast)
    if not per_folio:
        return None, 0
    effects = np.mean([np.mean(per_folio[folio], axis=0) for folio in sorted(per_folio)], axis=0)
    return effects, len(per_folio)


def _fixed_effect_residual_values(values, pages_by_unit, covariates):
    covariates = np.asarray(covariates, dtype=np.float64)
    require(
        covariates.ndim == 3
        and covariates.shape[:2] == values.shape[:2]
        and np.isfinite(covariates).all(),
        "invalid residual covariates",
    )
    result = np.empty_like(values, dtype=np.float64)
    for edition in range(values.shape[1]):
        x = covariates[:, edition, :]
        xc = np.empty_like(x)
        for page in sorted(set(pages_by_unit)):
            indices = np.asarray([i for i, value in enumerate(pages_by_unit) if value == page], dtype=np.int64)
            xc[indices] = x[indices] - x[indices].mean(axis=0, keepdims=True)
        for feature in range(values.shape[2]):
            y = values[:, edition, feature]
            yc = np.empty_like(y)
            for page in sorted(set(pages_by_unit)):
                indices = np.asarray([i for i, value in enumerate(pages_by_unit) if value == page], dtype=np.int64)
                yc[indices] = y[indices] - y[indices].mean()
            beta = np.linalg.lstsq(xc, yc, rcond=None)[0]
            result[:, edition, feature] = yc - xc @ beta
    return result


def _length_residual_values(values, pages_by_unit, word_count_index, degree):
    x = np.log1p(values[:, :, word_count_index])
    covariates = np.stack([x ** power for power in range(1, degree + 1)], axis=2)
    return _fixed_effect_residual_values(values, pages_by_unit, covariates)


def _ordinal_residual_values(values, pages_by_unit, ordinals):
    ordinals = np.asarray(ordinals, dtype=np.int64)
    page_max = {
        page: max(int(ordinals[index]) for index, value in enumerate(pages_by_unit) if value == page)
        for page in sorted(set(pages_by_unit))
    }
    maximum = int(np.max(ordinals))
    columns = []
    for level in range(2, maximum + 1):
        columns.append((ordinals == level).astype(np.float64))
    relative = np.asarray([
        (int(ordinals[index]) - 0.5) / page_max[page]
        for index, page in enumerate(pages_by_unit)
    ])
    columns.extend([relative, relative ** 2, relative ** 3])
    columns.append((ordinals % 2 == 1).astype(np.float64))
    columns.append(np.asarray([
        int(ordinals[index]) <= page_max[page] / 2
        for index, page in enumerate(pages_by_unit)
    ], dtype=np.float64))
    quarter = np.minimum((relative * 4).astype(np.int64), 3)
    columns.extend([(quarter == value).astype(np.float64) for value in (1, 2, 3)])
    base = np.stack(columns, axis=1)
    covariates = np.repeat(base[:, None, :], len(EDITIONS), axis=1)
    return _fixed_effect_residual_values(values, pages_by_unit, covariates)


def evaluate(
    *, unit_ids, pages_by_unit, folios_by_unit, ordinals, values, features,
    label_sets, target_specs, rotations, chunk_size=4096,
):
    """Score all targets/features and return compact statistics and gates."""
    values = np.asarray(values, dtype=np.float64)
    raw_ordinals = np.asarray(ordinals)
    require(
        matrix_contract(
            unit_ids, pages_by_unit, folios_by_unit, raw_ordinals, values, features
        ),
        "matrix contract failed",
    )
    ordinals = raw_ordinals.astype(np.int64)
    pages, page_indices, page_folio = _page_layout(pages_by_unit, folios_by_unit, ordinals)
    require(
        rotations.ndim == 2
        and rotations.shape[1] == len(pages)
        and np.all(rotations[0] == 0),
        "rotation contract failed",
    )
    for column, page in enumerate(pages):
        require(
            np.all(rotations[:, column] < len(page_indices[page])),
            "rotation exceeds page length",
        )
    require(set(label_sets) == set(target_specs), "target set mismatch")
    require(
        all(len(label_sets[target]) == len(unit_ids) for target in label_sets),
        "target row count mismatch",
    )

    residual_scale = _page_centered_scale(values, pages_by_unit)
    variable_folios = _variable_folios(values, pages_by_unit, folios_by_unit)
    word_count_index = features.index("PARA_WORD_COUNT") if "PARA_WORD_COUNT" in features else None
    if word_count_index is not None:
        require(np.all(values[:, :, word_count_index] >= 0.0), "negative paragraph word count")
    require(
        word_count_index is not None
        or not any(
            feature.startswith("ROOT_ATOM_RATE__")
            or feature.startswith("ROOT_WORD_RATE__")
            for feature in features
        ),
        "root features require PARA_WORD_COUNT",
    )
    base_eligible = np.all(variable_folios >= 4, axis=0) & np.all(residual_scale > NUM_TOL, axis=0)

    target_data = {}
    for target in sorted(target_specs):
        low, high = target_specs[target]
        page_contrasts, informative_pages = _page_contrasts(
            label_sets[target], values, pages, page_indices, low, high
        )
        target_data[target] = {
            "low": low, "high": high, "page_contrasts": page_contrasts,
            "informative_pages": informative_pages,
            "informative_folios": sorted({page_folio[page] for page in informative_pages}),
            "observed_per_folio": _observed_per_folio(page_contrasts, informative_pages, page_folio),
        }

    random_count = rotations.shape[0] - 1
    require(random_count >= 1, "no random rotations")
    sums = {target: np.zeros((values.shape[1], values.shape[2])) for target in target_data}
    sums_sq = {target: np.zeros((values.shape[1], values.shape[2])) for target in target_data}
    for start in range(1, rotations.shape[0], chunk_size):
        chunk = rotations[start:start + chunk_size]
        for target, data in target_data.items():
            effects = _aggregate_effects(
                data["page_contrasts"], data["informative_pages"], page_folio, pages, chunk
            )
            sums[target] += effects.sum(axis=0)
            sums_sq[target] += np.square(effects).sum(axis=0)

    for target, data in target_data.items():
        mean = sums[target] / random_count
        variance = np.maximum(sums_sq[target] / random_count - mean * mean, 0.0)
        sd = np.sqrt(variance)
        eligible = base_eligible & np.all(sd > NUM_TOL, axis=0)
        observed = _aggregate_effects(
            data["page_contrasts"], data["informative_pages"], page_folio, pages, rotations[:1]
        )[0]
        z = np.divide(observed - mean, sd, out=np.zeros_like(observed), where=sd > NUM_TOL)
        data.update({"null_mean": mean, "null_sd": sd, "eligible": eligible, "observed": observed, "z": z, "robust": _robust(z[None, :, :])[0]})
        require(
            all(np.isfinite(item).all() for item in (mean, sd, observed, z, data["robust"])),
            "nonfinite target statistic",
        )

    raw_counts = {target: np.zeros(values.shape[2], dtype=np.int64) for target in target_data}
    family_max_values = []
    for start in range(1, rotations.shape[0], chunk_size):
        chunk = rotations[start:start + chunk_size]
        robust_by_target = {}
        family_max = np.zeros(len(chunk), dtype=np.float64)
        for target, data in target_data.items():
            effects = _aggregate_effects(
                data["page_contrasts"], data["informative_pages"], page_folio, pages, chunk
            )
            z = np.divide(
                effects - data["null_mean"][None, :, :],
                data["null_sd"][None, :, :],
                out=np.zeros_like(effects),
                where=data["null_sd"][None, :, :] > NUM_TOL,
            )
            robust = _robust(z)
            robust[:, ~data["eligible"]] = 0.0
            robust_by_target[target] = robust
            if np.any(data["eligible"]):
                family_max = np.maximum(family_max, np.max(robust[:, data["eligible"]], axis=1))
        family_max_values.append(family_max)
        for target, data in target_data.items():
            raw_counts[target] += np.sum(
                robust_by_target[target] >= data["robust"][None, :] - TIE_TOL, axis=0
            )
    family_max_all = np.concatenate(family_max_values)
    require(np.isfinite(family_max_all).all(), "nonfinite family statistic")

    ordinal_residual = _ordinal_residual_values(values, pages_by_unit, ordinals)
    length_residual_linear = (
        _length_residual_values(values, pages_by_unit, word_count_index, 1)
        if word_count_index is not None else None
    )
    length_residual_cubic = (
        _length_residual_values(values, pages_by_unit, word_count_index, 3)
        if word_count_index is not None else None
    )
    require(np.isfinite(ordinal_residual).all(), "nonfinite ordinal residual")
    require(
        length_residual_linear is None
        or (
            np.isfinite(length_residual_linear).all()
            and np.isfinite(length_residual_cubic).all()
        ),
        "nonfinite length residual",
    )
    results = []
    for target, data in target_data.items():
        labels = label_sets[target]
        low, high = data["low"], data["high"]
        max_ord = {page: max(int(ordinals[index]) for index in page_indices[page]) for page in pages}
        subsets = {
            "ODD": lambda index: int(ordinals[index]) % 2 == 1,
            "EVEN": lambda index: int(ordinals[index]) % 2 == 0,
            "EARLY": lambda index: int(ordinals[index]) <= max_ord[pages_by_unit[index]] / 2,
            "LATE": lambda index: int(ordinals[index]) > max_ord[pages_by_unit[index]] / 2,
        }
        subset_effects = {}
        subset_folios = {}
        for name, keep in subsets.items():
            subset_effects[name], subset_folios[name] = _subset_effect(
                labels, values, pages, page_indices, page_folio, low, high, keep
            )
        pc, ip = _page_contrasts(labels, ordinal_residual, pages, page_indices, low, high)
        ordinal_effect = _aggregate_effects(pc, ip, page_folio, pages, rotations[:1])[0]
        length_effect_linear = None
        length_effect_cubic = None
        if length_residual_linear is not None:
            pc, ip = _page_contrasts(labels, length_residual_linear, pages, page_indices, low, high)
            length_effect_linear = _aggregate_effects(pc, ip, page_folio, pages, rotations[:1])[0]
            pc, ip = _page_contrasts(labels, length_residual_cubic, pages, page_indices, low, high)
            length_effect_cubic = _aggregate_effects(pc, ip, page_folio, pages, rotations[:1])[0]

        per_folio = data["observed_per_folio"]
        folios = sorted(per_folio)
        for feature_index, feature in enumerate(features):
            effects = data["observed"][:, feature_index]
            direction = raw_direction(effects)
            z_direction_ok = z_matches_raw_direction(data["z"][:, feature_index], direction)
            material = float(np.min(np.abs(effects) / residual_scale[:, feature_index])) if base_eligible[feature_index] else 0.0
            ordinal_values = ordinal_effect[:, feature_index]
            ordinal_material = (
                float(np.min(np.abs(ordinal_values) / residual_scale[:, feature_index]))
                if base_eligible[feature_index] else 0.0
            )
            ordinal_ok = (
                direction != 0
                and np.all(ordinal_values * direction > NUM_TOL)
                and ordinal_material >= 0.15
            )
            raw_p = (1 + raw_counts[target][feature_index]) / (random_count + 1)
            family_p = (1 + np.sum(family_max_all >= data["robust"][feature_index] - TIE_TOL)) / (random_count + 1)
            strata_ok = direction != 0
            strata_detail = {}
            for name in ("ODD", "EVEN", "EARLY", "LATE"):
                effect = subset_effects[name]
                same = effect is not None and subset_folios[name] >= 4 and np.all(effect[:, feature_index] * direction > NUM_TOL)
                strata_ok &= bool(same)
                strata_detail[name] = {"folios": subset_folios[name], "effects": [] if effect is None else [float(v) for v in effect[:, feature_index]], "same_direction": bool(same)}
            deletion_ok = direction != 0
            deletion_effects = {}
            for omitted in folios:
                kept = [per_folio[folio] for folio in folios if folio != omitted]
                effect = np.mean(kept, axis=0)[:, feature_index]
                same = np.all(effect * direction > NUM_TOL)
                deletion_ok &= bool(same)
                deletion_effects[omitted] = [float(v) for v in effect]
            required = 5 if target.startswith("RAY_") else 4
            support_counts = [sum(per_folio[folio][edition, feature_index] * direction > NUM_TOL for folio in folios) for edition in range(len(EDITIONS))] if direction else [0, 0, 0]
            common_support_count = sum(
                np.all(per_folio[folio][:, feature_index] * direction > NUM_TOL)
                for folio in folios
            ) if direction else 0
            support_ok = direction != 0 and common_support_count >= required
            root_feature = feature.startswith("ROOT_ATOM_RATE__") or feature.startswith("ROOT_WORD_RATE__")
            length_ok = True
            length_values_linear = []
            length_values_cubic = []
            length_material_linear = None
            length_material_cubic = None
            if root_feature:
                length_values_linear = [float(v) for v in length_effect_linear[:, feature_index]]
                length_values_cubic = [float(v) for v in length_effect_cubic[:, feature_index]]
                if base_eligible[feature_index]:
                    length_material_linear = float(np.min(
                        np.abs(length_effect_linear[:, feature_index]) / residual_scale[:, feature_index]
                    ))
                    length_material_cubic = float(np.min(
                        np.abs(length_effect_cubic[:, feature_index]) / residual_scale[:, feature_index]
                    ))
                else:
                    length_material_linear = 0.0
                    length_material_cubic = 0.0
                length_ok = (
                    direction != 0
                    and np.all(length_effect_linear[:, feature_index] * direction > NUM_TOL)
                    and np.all(length_effect_cubic[:, feature_index] * direction > NUM_TOL)
                    and length_material_linear >= 0.15
                    and length_material_cubic >= 0.15
                )
            gates = {
                "eligible": bool(data["eligible"][feature_index]),
                "same_reading_direction": direction != 0,
                "z_matches_raw_direction": bool(z_direction_ok),
                "robust_z": float(data["robust"][feature_index]) >= 2.5,
                "raw_p": raw_p <= 0.01,
                "family_p": family_p <= 0.05,
                "material": material >= 0.15,
                "parity_and_early_late": bool(strata_ok),
                "folio_deletions": bool(deletion_ok),
                "folio_support": bool(support_ok),
                "ordinal_residual_material": bool(ordinal_ok),
                "root_length_residual": bool(length_ok),
            }
            results.append({
                "target": target, "feature": feature, "eligible": bool(data["eligible"][feature_index]),
                "effects": {edition: float(effects[i]) for i, edition in enumerate(EDITIONS)},
                "null_means": {edition: float(data["null_mean"][i, feature_index]) for i, edition in enumerate(EDITIONS)},
                "null_sds": {edition: float(data["null_sd"][i, feature_index]) for i, edition in enumerate(EDITIONS)},
                "z": {edition: float(data["z"][i, feature_index]) for i, edition in enumerate(EDITIONS)},
                "direction": direction, "robust_z": float(data["robust"][feature_index]),
                "raw_p": float(raw_p), "family_p": float(family_p), "material_effect": material,
                "strata": strata_detail, "deletion_effects": deletion_effects,
                "folio_support_counts": dict(zip(EDITIONS, support_counts)),
                "common_folio_support_count": int(common_support_count),
                "ordinal_residual_effects": dict(zip(EDITIONS, map(float, ordinal_values))),
                "ordinal_residual_material_effect": ordinal_material,
                "length_linear_residual_effects": dict(zip(EDITIONS, length_values_linear)) if root_feature else {},
                "length_cubic_residual_effects": dict(zip(EDITIONS, length_values_cubic)) if root_feature else {},
                "length_linear_residual_material_effect": length_material_linear,
                "length_cubic_residual_material_effect": length_material_cubic,
                "statistical_gates": gates, "statistical_passes": all(gates.values()),
            })
    return {
        "rotation_digest": rotation_digest(rotations),
        "rotation_count": int(rotations.shape[0]),
        "random_rotation_count": int(random_count),
        "pages": pages,
        "features": list(features),
        "base_eligible_features": [features[i] for i in range(len(features)) if base_eligible[i]],
        "target_eligible_features": {target: [features[i] for i in range(len(features)) if data["eligible"][i]] for target, data in target_data.items()},
        "results": results,
        "statistical_passing": [
            {"target": row["target"], "feature": row["feature"]}
            for row in results if row["statistical_passes"]
        ],
    }
