#!/usr/bin/env python3
"""Independent clean-room validator for SME003 synthetic calibration.

This module deliberately does not import any SME003 calibration implementation.
It reads only the frozen SME003 specifications, the anonymous paragraph matrix
and inventory, the validated preflight JSON, and the calibration result JSON.
It must never read or hash morphology/target material.

The validator is intentionally fail closed.  In particular, an absent result is
reported as a clean BLOCKED_RESULT_ABSENT outcome with exit status 2; no output
artifact is written.  A present result is accepted only after the anonymous
inputs, preflight transforms, synthetic labels, rotations, planted matrices,
full-orbit scores, gates, and controls have been independently reconstructed.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

# Exact-byte numeric checkpoints are part of the frozen contract.  Pin every
# supported BLAS runtime before NumPy is imported so inherited shell settings
# cannot change reduction order during clean-room reconstruction.
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]

SPEC_PATH = HERE / "SME003_SYNTHETIC_CALIBRATION_SPEC.md"
PREFLIGHT_SPEC_PATH = HERE / "SME003_CROSS_FOLIO_PREFLIGHT_SPEC.md"
MATRIX_PATH = HERE / "anonymous_paragraph_matrix.tsv"
INVENTORY_PATH = HERE / "anonymous_feature_inventory.json"
PREFLIGHT_PATH = HERE / "sme003_cross_folio_preflight.json"
DEFAULT_RESULT_PATH = HERE / "sme003_synthetic_calibration_result.json"

EXPECTED_HASHES = {
    SPEC_PATH.name: "d6873fddba0470a217ffb817679b09267ccae6be472b8fb57c46b215c4ec6c05",
    PREFLIGHT_SPEC_PATH.name: "d10ff711ebbb6269ce3d0ed0d760fd071836e7d7c6a6dda30be267b7292723b7",
    MATRIX_PATH.name: "b246456b181b07e847c6d5a49b959b0346eff6a4c6febb8a543de104c505a26a",
    INVENTORY_PATH.name: "088232b431b4b9746bb94a08328cb969fb7c21c6a28cd112286da40d6429fea5",
    PREFLIGHT_PATH.name: "86c216302f99086bb4353e23eb97a7ddeb293e115461e0d733464d3bf3cacf4c",
}

PAGES = {
    "f104r": 13,
    "f104v": 13,
    "f105r": 10,
    "f105v": 10,
    "f107v": 15,
    "f112v": 13,
    "f113r": 16,
    "f113v": 15,
    "f114r": 13,
    "f114v": 12,
    "f115r": 13,
    "f115v": 13,
}
PAGE_ORDER = tuple(sorted(PAGES))
FOLIOS = ("f104", "f105", "f107", "f112", "f113", "f114", "f115")
EDITIONS = ("ZL3b", "IT2a", "RF1b")
TARGETS = ("RAY_LIKE", "TAIL_LIKE")
DRIVERS = ("DENSE_83_DRIVER", "BALANCED_24_DRIVER")
STRENGTHS = (0.25, 0.50, 0.75, 1.00)
ENSEMBLES = ("INDEPENDENT_PAGE", "COUPLED_FOLIO")
N_ASSIGN = 8192
NUM_TOL = 1e-15
TAIL_TOL = 1e-12
CLAIM_CEILING = (
    "anonymous target-free synthetic calibration only; no morphology association, "
    "feature interpretation, meaning, lexeme, plaintext, language, or translation"
)

META = ("unit_id", "page", "physical_folio", "star_ordinal", "locus", "edition")


class ValidationError(RuntimeError):
    """A fail-closed validation error."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def f8_digest(array: np.ndarray) -> str:
    value = np.ascontiguousarray(array, dtype=np.dtype("<f8"))
    return sha256_bytes(value.tobytes(order="C"))


def u2_digest(array: np.ndarray) -> str:
    value = np.ascontiguousarray(array, dtype=np.dtype("<u2"))
    return sha256_bytes(value.tobytes(order="C"))


def text_digest(lines: Iterable[str]) -> str:
    return sha256_bytes("".join(lines).encode("ascii"))


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def canonical_json_digest(value: Any) -> str:
    blob = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return sha256_bytes(blob.encode("ascii"))


@dataclass(frozen=True)
class Universe:
    features: tuple[str, ...]
    formal: tuple[str, ...]
    root: tuple[str, ...]
    eligible: tuple[str, ...]
    eligible_indices: np.ndarray
    unit_ids: tuple[str, ...]
    page: np.ndarray
    folio: np.ndarray
    ordinal: np.ndarray
    locus: tuple[str, ...]
    values: np.ndarray  # edition x unit x all-feature
    page_indices: Mapping[str, np.ndarray]
    folio_indices: Mapping[str, np.ndarray]
    feature_index: Mapping[str, int]


@dataclass
class FoldTransform:
    held_folio: str
    edition: str
    residual: np.ndarray
    standardized: np.ndarray
    weight: np.ndarray
    scales: np.ndarray
    rho: float


@dataclass
class MatrixTransforms:
    eligible: tuple[str, ...]
    folds: dict[tuple[str, str], FoldTransform]
    all_folio_residuals: dict[str, np.ndarray]
    all_folio_standardized: dict[str, np.ndarray]


def verify_frozen_sources() -> dict[str, str]:
    observed: dict[str, str] = {}
    for name, expected in EXPECTED_HASHES.items():
        path = HERE / name
        require(path.is_file(), f"required frozen input absent: {path}")
        observed[name] = sha256_file(path)
        require(observed[name] == expected, f"frozen input hash mismatch: {name}")
    return observed


def target_paths_from_preflight(preflight: Mapping[str, Any]) -> tuple[Path, ...]:
    names: set[str] = set()
    for key in ("target_artifact_absence_before", "target_artifact_absence_after"):
        obj = preflight.get(key)
        require(isinstance(obj, dict), f"preflight missing {key}")
        names.update(str(item) for item in obj)
    paths: list[Path] = []
    for name in sorted(names):
        candidate = (REPO / name).resolve()
        require(REPO == candidate or REPO in candidate.parents, "target path escapes repository")
        paths.append(candidate)
    return tuple(paths)


def assert_target_absence(paths: Sequence[Path], stage: str) -> dict[str, bool]:
    present = [str(path.relative_to(REPO)) for path in paths if path.exists()]
    require(not present, f"target artifacts present {stage}: {present}")
    return {str(path.relative_to(REPO)): True for path in paths}


def load_universe() -> tuple[Universe, dict[str, Any]]:
    inventory = load_json(INVENTORY_PATH)
    preflight = load_json(PREFLIGHT_PATH)
    require(preflight.get("status") == "PASS_TARGET_BLIND_CROSS_FOLIO_PREFLIGHT", "preflight status is not PASS")
    require(preflight.get("decision") == "GO_TO_TARGET_FREE_SYNTHETIC_DESIGN", "preflight decision is not GO")

    formal = tuple(inventory["formal_features"])
    atoms = tuple("ROOT_ATOM_RATE__" + item for item in inventory["root_atom_features"])
    words = tuple("ROOT_WORD_RATE__" + item for item in inventory["root_compound_word_features"])
    root = atoms + words
    features = tuple(inventory["all_features"])
    require(features == formal + root, "inventory feature partition/order mismatch")
    require((len(formal), len(atoms), len(words), len(features)) == (34, 32, 18, 84), "inventory counts mismatch")
    eligible = tuple(preflight["formal_eligible"] + preflight["root_eligible"])
    require(len(eligible) == 83 and tuple(preflight["ineligible"]) == ("OPEN_FIRST_HAS_Q",), "preflight eligibility mismatch")
    require(eligible == tuple(item for item in features if item != "OPEN_FIRST_HAS_Q"), "eligible order mismatch")

    with MATRIX_PATH.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        require(reader.fieldnames == list(META + features), "anonymous matrix header mismatch")
        raw_all = list(reader)
    require(len(raw_all) == 510, "anonymous source matrix must contain 510 rows")
    excluded = [row for row in raw_all if row["page"] not in PAGES]
    require(len(excluded) == 42 and {row["page"] for row in excluded} == {"f106r"}, "complete-page exclusion mismatch")
    raw = [row for row in raw_all if row["page"] in PAGES]
    require(len(raw) == 468, "target-scope anonymous matrix must contain 468 rows")

    by_key: dict[tuple[str, int, str], dict[str, str]] = {}
    for row in raw:
        key = (row["page"], int(row["star_ordinal"]), row["edition"])
        require(key not in by_key, f"duplicate anonymous row {key}")
        by_key[key] = row

    unit_ids: list[str] = []
    pages: list[str] = []
    folios: list[str] = []
    ordinals: list[int] = []
    loci: list[str] = []
    values = np.empty((len(EDITIONS), 156, len(features)), dtype=np.float64)
    u = 0
    for page in PAGE_ORDER:
        for ordinal in range(1, PAGES[page] + 1):
            triplet = [by_key.get((page, ordinal, edition)) for edition in EDITIONS]
            require(all(item is not None for item in triplet), f"missing reading triplet {page}.{ordinal}")
            first = triplet[0]
            assert first is not None
            expected_folio = page[:-1]
            for eidx, row in enumerate(triplet):
                assert row is not None
                require(row["page"] == page and int(row["star_ordinal"]) == ordinal, "page/ordinal drift")
                require(row["physical_folio"] == expected_folio, "page/folio drift")
                require(row["unit_id"] == first["unit_id"] and row["locus"] == first["locus"], "reading metadata drift")
                for j, feature in enumerate(features):
                    try:
                        value = float(row[feature])
                    except ValueError as exc:
                        raise ValidationError(f"nonnumeric feature {feature} at {page}.{ordinal}") from exc
                    require(math.isfinite(value), f"nonfinite feature {feature} at {page}.{ordinal}")
                    values[eidx, u, j] = value
            unit_ids.append(first["unit_id"])
            pages.append(page)
            folios.append(expected_folio)
            ordinals.append(ordinal)
            loci.append(first["locus"])
            u += 1
    require(len(by_key) == 468 and u == 156 and len(set(unit_ids)) == 156, "unit universe mismatch")

    # The inherited preflight numeric payload is globally ordered by anonymous
    # unit ID.  Page-local operations use a separate explicit ordinal order.
    order = np.asarray(sorted(range(156), key=lambda i: unit_ids[i]), dtype=np.int64)
    unit_ids = [unit_ids[i] for i in order]
    pages = [pages[i] for i in order]
    folios = [folios[i] for i in order]
    ordinals = [ordinals[i] for i in order]
    loci = [loci[i] for i in order]
    values = values[:, order, :]
    page_array = np.asarray(pages, dtype=object)
    folio_array = np.asarray(folios, dtype=object)
    ordinal_array = np.asarray(ordinals, dtype=np.int64)
    page_indices = {
        page: np.asarray(
            sorted(np.flatnonzero(page_array == page), key=lambda i: (int(ordinal_array[i]), unit_ids[i])),
            dtype=np.int64,
        )
        for page in PAGE_ORDER
    }
    folio_indices = {folio: np.flatnonzero(folio_array == folio) for folio in FOLIOS}
    for page, idx in page_indices.items():
        require(len(idx) == PAGES[page], f"page size mismatch: {page}")
    require(set(folios) == set(FOLIOS), "folio universe mismatch")
    wc = features.index("PARA_WORD_COUNT")
    require(np.all(values[:, :, wc] >= 0.0), "negative paragraph word count")

    universe = Universe(
        features=features,
        formal=formal,
        root=root,
        eligible=eligible,
        eligible_indices=np.asarray([features.index(item) for item in eligible], dtype=np.int64),
        unit_ids=tuple(unit_ids),
        page=page_array,
        folio=folio_array,
        ordinal=ordinal_array,
        locus=tuple(loci),
        values=values,
        page_indices=page_indices,
        folio_indices=folio_indices,
        feature_index={item: i for i, item in enumerate(features)},
    )
    return universe, preflight


def centered_by_page(values: np.ndarray, universe: Universe) -> np.ndarray:
    source = np.asarray(values, dtype=np.float64)
    out = np.empty_like(source)
    # Numeric preflight rows retain global unit-ID order inside each page.
    # `page_indices` is ordinal-sorted for sequence operations and must not be
    # reused here because reduction order is part of the frozen byte contract.
    for page in PAGE_ORDER:
        mask = universe.page == page
        selected = source[mask]
        out[mask] = selected - np.mean(selected, axis=0, keepdims=True)
    return out


def position_nuisance(universe: Universe) -> np.ndarray:
    ordinal = universe.ordinal.astype(np.float64)
    size = np.asarray([PAGES[str(page)] for page in universe.page], dtype=np.float64)
    r = (ordinal - 0.5) / size
    a = (ordinal - 0.5) / 16.0
    # Relative-quarter indicators 1--3 use the centered-row coordinate r and
    # half-open quarter bins; the fourth quarter is the reference category.
    quarter = np.minimum((r * 4.0).astype(np.int64), 3)
    columns = [
        r,
        r ** 2,
        r ** 3,
        a,
        a ** 2,
        a ** 3,
        (universe.ordinal % 2 == 1).astype(np.float64),
        (ordinal <= size / 2.0).astype(np.float64),
        (quarter == 1).astype(np.float64),
        (quarter == 2).astype(np.float64),
        (quarter == 3).astype(np.float64),
    ]
    return centered_by_page(np.stack(columns, axis=1), universe)


def residualize_edition(matrix: np.ndarray, edition_index: int, held_folio: str | None, universe: Universe) -> tuple[np.ndarray, np.ndarray]:
    require(matrix.shape == (3, 156, 84), "matrix tensor shape mismatch")
    y = centered_by_page(matrix[edition_index], universe)
    base = position_nuisance(universe)
    wc = matrix[edition_index, :, universe.feature_index["PARA_WORD_COUNT"]]
    require(np.all(np.isfinite(wc)) and np.all(wc >= 0.0), "invalid word count before log1p")
    logw = np.log1p(wc)
    length = centered_by_page(np.stack([logw, logw ** 2, logw ** 3], axis=1), universe)
    if held_folio is None:
        train = np.ones(156, dtype=bool)
    else:
        train = universe.folio != held_folio
    require(np.count_nonzero(train) > 0, "empty training fold")

    residual = np.empty_like(y)
    for j, feature in enumerate(universe.features):
        design = base if feature in universe.formal else np.concatenate([base, length], axis=1)
        require(np.all(np.isfinite(design)), "nonfinite nuisance matrix")
        beta, _resid, _rank, _singular = np.linalg.lstsq(
            design[train], y[train, j], rcond=None
        )
        residual[:, j] = y[:, j] - design @ beta
    scales = np.sqrt(np.mean(residual[train] ** 2, axis=0, dtype=np.float64))
    require(np.all(np.isfinite(residual)) and np.all(np.isfinite(scales)), "nonfinite residual/scale")
    return residual, scales


def build_transforms(matrix: np.ndarray, universe: Universe) -> MatrixTransforms:
    residual_cache: dict[tuple[str, str], tuple[np.ndarray, np.ndarray]] = {}
    eligible_mask = np.ones(84, dtype=bool)
    for folio in FOLIOS:
        for eidx, edition in enumerate(EDITIONS):
            residual, scales = residualize_edition(matrix, eidx, folio, universe)
            residual_cache[(folio, edition)] = (residual, scales)
            eligible_mask &= np.isfinite(scales) & (scales > 1e-10)
    eligible = tuple(feature for feature, keep in zip(universe.features, eligible_mask, strict=True) if keep)
    require(eligible == universe.eligible, f"eligibility drift: {eligible}")
    eligible_idx = universe.eligible_indices

    folds: dict[tuple[str, str], FoldTransform] = {}
    for folio in FOLIOS:
        train = universe.folio != folio
        for edition in EDITIONS:
            residual, scales_all = residual_cache[(folio, edition)]
            scales = scales_all[eligible_idx]
            z = residual[:, eligible_idx] / scales
            require(np.all(np.isfinite(z)), "nonfinite standardized fold")
            ztrain = z[train]
            # Exact inherited preflight population second moment. The nuisance
            # residuals are already page-centered; do not center them again.
            covariance = ztrain.T @ ztrain / float(len(ztrain))
            p = covariance.shape[0]
            mu = float(np.trace(covariance) / p)
            alpha = float(np.mean(covariance * covariance, dtype=np.float64))
            den = float((len(ztrain) + 1) * (alpha - mu * mu / p))
            rho = 1.0 if den <= NUM_TOL else min(1.0, (alpha + mu * mu) / den)
            shrunk = (1.0 - rho) * covariance + rho * mu * np.eye(p)
            require(np.all(np.isfinite(shrunk)), "nonfinite shrunk covariance")
            eig = np.linalg.eigvalsh(shrunk)
            require(float(eig[0]) > NUM_TOL, "nonpositive shrunk covariance")
            weight = np.linalg.inv(shrunk)
            weight *= p / float(np.trace(weight))
            require(np.all(np.isfinite(weight)), "nonfinite weight matrix")
            require(float(np.linalg.eigvalsh((weight + weight.T) / 2.0)[0]) > NUM_TOL, "weight not positive definite")
            folds[(folio, edition)] = FoldTransform(folio, edition, residual, z, weight, scales, rho)

    all_folio_residuals: dict[str, np.ndarray] = {}
    all_folio: dict[str, np.ndarray] = {}
    for eidx, edition in enumerate(EDITIONS):
        residual, scales = residualize_edition(matrix, eidx, None, universe)
        selected = scales[eligible_idx]
        require(np.all(selected > 1e-10), "all-folio zero scale")
        all_folio_residuals[edition] = residual
        all_folio[edition] = residual[:, eligible_idx] / selected
    return MatrixTransforms(eligible, folds, all_folio_residuals, all_folio)


def transform_checkpoint(transforms: MatrixTransforms) -> dict[str, Any]:
    fold_records: dict[str, Any] = {}
    for folio in FOLIOS:
        for edition in EDITIONS:
            item = transforms.folds[(folio, edition)]
            fold_records[f"{folio}__{edition}"] = {
                "residual_sha256": f8_digest(item.residual),
                "standardized_sha256": f8_digest(item.standardized),
                "weight_sha256": f8_digest(item.weight),
                "scales_sha256": f8_digest(item.scales),
                "rho": item.rho,
            }
    return {
        "eligible_features": list(transforms.eligible),
        "eligible_sha256": text_digest(f"{item}\n" for item in transforms.eligible),
        "folds": fold_records,
        "all_folio_standardized": {edition: f8_digest(transforms.all_folio_standardized[edition]) for edition in EDITIONS},
    }


def validate_baseline_against_preflight(transforms: MatrixTransforms, preflight: Mapping[str, Any]) -> None:
    for folio in FOLIOS:
        for edition in EDITIONS:
            key = f"{folio}__{edition}"
            expected = preflight["transforms"][key]
            actual = transforms.folds[(folio, edition)]
            require(f8_digest(actual.standardized) == expected["standardized_matrix_sha256"], f"baseline standardized digest mismatch {key}")
            require(f8_digest(actual.weight) == expected["weight_matrix_sha256"], f"baseline weight digest mismatch {key}")
            require(abs(actual.rho - float(expected["rho"])) <= 1e-14, f"baseline shrinkage mismatch {key}")


def synth_digest(world: int, domain: str, item: str) -> bytes:
    payload = f"SME003_SYNTH_V1|{world}|{domain}|{item}".encode("ascii")
    return hashlib.sha256(payload).digest()


def rank_items(world: int, domain: str, items: Iterable[str]) -> list[str]:
    return sorted(items, key=lambda item: (synth_digest(world, domain, item), item))


def informative_pages(labels: np.ndarray, universe: Universe) -> tuple[str, ...]:
    pages = []
    for page in PAGE_ORDER:
        states = labels[universe.page_indices[page]]
        if np.any(states == "L") and np.any(states == "H"):
            pages.append(page)
    return tuple(pages)


def generate_world(world: int, universe: Universe) -> dict[str, np.ndarray]:
    require(0 <= world < 64, "synthetic world out of range")
    labels: dict[str, np.ndarray] = {}

    ray = np.full(156, "L", dtype="U1")
    protected_low: set[int] = set()
    protected_high: set[int] = set()
    for page in PAGE_ORDER:
        idx = universe.page_indices[page]
        low_id = rank_items(world, f"RAY_LOW_ANCHOR|{page}", (universe.unit_ids[i] for i in idx))[0]
        low = universe.unit_ids.index(low_id)
        protected_low.add(low)
        remaining = [universe.unit_ids[i] for i in idx if i != low]
        high_id = rank_items(world, f"RAY_HIGH_ANCHOR|{page}", remaining)[0]
        protected_high.add(universe.unit_ids.index(high_id))
    candidates = [universe.unit_ids[i] for i in range(156) if i not in protected_low and i not in protected_high]
    thirds = rank_items(world, "RAY_THIRD", candidates)[:7]
    third_idx = {universe.unit_ids.index(item) for item in thirds}
    ray[list(third_idx)] = "X"
    ray[list(protected_high)] = "H"
    candidates = [universe.unit_ids[i] for i in range(156) if i not in protected_low | protected_high | third_idx]
    need = 83 - len(protected_high)
    additional = rank_items(world, "RAY_REMAINING_HIGH", candidates)[:need]
    ray[[universe.unit_ids.index(item) for item in additional]] = "H"
    require(tuple(np.unique(ray, return_counts=True)[1]) != (), "empty ray labels")
    require({state: int(np.count_nonzero(ray == state)) for state in "LHX"} == {"L": 66, "H": 83, "X": 7}, "ray counts mismatch")
    require(informative_pages(ray, universe) == PAGE_ORDER, "ray page support mismatch")
    labels["RAY_LIKE"] = ray

    omitted = rank_items(world, "TAIL_OMIT_FOLIO", FOLIOS)[0]
    retained = [folio for folio in FOLIOS if folio != omitted]
    selected_pages: set[str] = set()
    for folio in retained:
        candidates_page = [page for page in PAGE_ORDER if page[:-1] == folio]
        selected_pages.add(rank_items(world, f"TAIL_PRIMARY_PAGE|{folio}", candidates_page)[0])
    extras = [page for page in PAGE_ORDER if page[:-1] in retained and page not in selected_pages]
    selected_pages.update(rank_items(world, "TAIL_EXTRA_PAGE", extras)[:2])
    require(len(selected_pages) == 8, "tail informative page construction mismatch")
    noninformative_units = [universe.unit_ids[i] for i in range(156) if str(universe.page[i]) not in selected_pages]
    third_id = rank_items(world, "TAIL_THIRD", noninformative_units)[0]
    tail_third = universe.unit_ids.index(third_id)
    tail = np.full(156, "L", dtype="U1")
    tail[tail_third] = "X"
    tail_high: set[int] = set()
    tail_low: set[int] = set()
    for page in sorted(selected_pages):
        idx = [int(i) for i in universe.page_indices[page] if int(i) != tail_third]
        high_id = rank_items(world, f"TAIL_HIGH_ANCHOR|{page}", (universe.unit_ids[i] for i in idx))[0]
        high = universe.unit_ids.index(high_id)
        tail_high.add(high)
        remain = [universe.unit_ids[i] for i in idx if i != high]
        low_id = rank_items(world, f"TAIL_LOW_ANCHOR|{page}", remain)[0]
        tail_low.add(universe.unit_ids.index(low_id))
    tail[list(tail_high)] = "H"
    candidates = [universe.unit_ids[i] for i in range(156) if str(universe.page[i]) in selected_pages and i not in tail_low | tail_high and i != tail_third]
    additional = rank_items(world, "TAIL_REMAINING_HIGH", candidates)[: 22 - len(tail_high)]
    tail[[universe.unit_ids.index(item) for item in additional]] = "H"
    require({state: int(np.count_nonzero(tail == state)) for state in "LHX"} == {"L": 133, "H": 22, "X": 1}, "tail counts mismatch")
    require(informative_pages(tail, universe) == tuple(sorted(selected_pages)), "tail page support mismatch")
    require(len({page[:-1] for page in selected_pages}) == 6, "tail folio support mismatch")
    labels["TAIL_LIKE"] = tail
    return labels


def label_checkpoint(world: int, labels: Mapping[str, np.ndarray], universe: Universe) -> dict[str, Any]:
    lines: list[str] = []
    targets: dict[str, Any] = {}
    for target in TARGETS:
        values = labels[target]
        target_lines = [
            f"{world},{target},{page},{universe.ordinal[i]},{values[i]}\n"
            for page in PAGE_ORDER
            for i in universe.page_indices[page]
        ]
        lines.extend(target_lines)
        pages = informative_pages(values, universe)
        targets[target] = {
            "sha256": text_digest(target_lines),
            "counts": {state: int(np.count_nonzero(values == state)) for state in ("L", "H", "X")},
            "informative_pages": list(pages),
            "informative_folios": sorted({page[:-1] for page in pages}),
        }
    return {"world": world, "paired_sha256": text_digest(lines), "targets": targets}


def sample_unbiased(ensemble: str, assignment: int, key: str, modulus: int, row_attempt: int = 0) -> int:
    require(modulus > 0, "invalid rotation modulus")
    limit = (1 << 64) - ((1 << 64) % modulus)
    counter = 0
    while True:
        if row_attempt == 0:
            text = f"SME003_ROT_V1|{ensemble}|{assignment}|{key}|{counter}"
        else:
            text = f"SME003_ROT_V1|{ensemble}|{assignment}|ROW_RETRY:{row_attempt}|{key}|{counter}"
        payload = text.encode("ascii")
        value = int.from_bytes(hashlib.sha256(payload).digest()[:8], "big", signed=False)
        if value < limit:
            return value % modulus
        counter += 1


def build_rotations(ensemble: str) -> tuple[np.ndarray, np.ndarray]:
    require(ensemble in ENSEMBLES, "unknown rotation ensemble")
    out = np.zeros((N_ASSIGN, len(PAGE_ORDER)), dtype=np.dtype("<u2"))
    attempts = np.zeros(N_ASSIGN, dtype=np.dtype("<u2"))
    seen = {out[0].tobytes()}
    folio_pages = {folio: [page for page in PAGE_ORDER if page[:-1] == folio] for folio in FOLIOS}
    moduli = {folio: math.lcm(*(PAGES[page] for page in pages)) for folio, pages in folio_pages.items()}
    for i in range(1, N_ASSIGN):
        accepted = False
        for row_attempt in range(65536):
            row = np.zeros(len(PAGE_ORDER), dtype=np.dtype("<u2"))
            if ensemble == "INDEPENDENT_PAGE":
                for j, page in enumerate(PAGE_ORDER):
                    row[j] = sample_unbiased(ensemble, i, page, PAGES[page], row_attempt)
            else:
                phases = {
                    folio: sample_unbiased(ensemble, i, f"FOLIO:{folio}", moduli[folio], row_attempt)
                    for folio in FOLIOS
                }
                for j, page in enumerate(PAGE_ORDER):
                    folio = page[:-1]
                    row[j] = math.floor(phases[folio] * PAGES[page] / moduli[folio])
            blob = row.tobytes()
            if blob not in seen:
                out[i] = row
                attempts[i] = row_attempt
                seen.add(blob)
                accepted = True
                break
        require(accepted, f"no unique rotation row by attempt 65535: {ensemble} assignment {i}")
    require(np.all(out[0] == 0), "identity rotation is nonzero")
    require(len({row.tobytes() for row in out}) == N_ASSIGN, f"duplicate rotation row: {ensemble}")
    return np.ascontiguousarray(out, dtype=np.dtype("<u2")), attempts


def rotate_labels(base: np.ndarray, rotations: np.ndarray, universe: Universe) -> np.ndarray:
    out = np.empty((len(rotations), 156), dtype="U1")
    for j, page in enumerate(PAGE_ORDER):
        idx = universe.page_indices[page]
        n = len(idx)
        # Positive cyclic shift: destination k receives source (k-shift) mod n.
        source = (np.arange(n)[None, :] - rotations[:, j : j + 1].astype(np.int64)) % n
        out[:, idx] = base[idx][source]
    return out


def all_folio_projection(transforms: MatrixTransforms) -> np.ndarray:
    answer = np.zeros_like(transforms.all_folio_standardized[EDITIONS[0]])
    for edition in EDITIONS:
        answer += transforms.all_folio_standardized[edition]
    answer /= len(EDITIONS)
    return answer


def driver_features(world: int, target: str, driver: str, universe: Universe) -> tuple[str, ...]:
    if driver == "DENSE_83_DRIVER":
        return universe.eligible
    require(driver == "BALANCED_24_DRIVER", "unknown projection driver")
    formal = rank_items(world, f"DRIVER_SELECT|{target}|{driver}", universe.eligible[:33])[:12]
    root = rank_items(world, f"DRIVER_SELECT|{target}|{driver}", universe.eligible[33:])[:12]
    selected = set(formal + root)
    return tuple(feature for feature in universe.eligible if feature in selected)


def projection_values(
    projection_matrix: np.ndarray,
    world: int,
    target: str,
    driver: str,
    universe: Universe,
    folio_random: str | None = None,
) -> tuple[np.ndarray, tuple[str, ...], np.ndarray]:
    selected = driver_features(world, target, driver, universe)
    columns = np.asarray([universe.eligible.index(feature) for feature in selected], dtype=np.int64)
    signs = np.empty(len(selected), dtype=np.float64)
    for j, feature in enumerate(selected):
        if folio_random is None:
            domain = f"DRIVER_SIGN|{target}|{driver}"
        else:
            domain = f"CONTROL_FOLIO_DIRECTION|{target}|{folio_random}"
        signs[j] = 1.0 if (synth_digest(world, domain, feature)[-1] & 1) else -1.0
    projection = np.zeros(projection_matrix.shape[0], dtype=np.float64)
    for column, sign in zip(columns, signs, strict=True):
        projection += sign * projection_matrix[:, column]
    projection /= math.sqrt(len(selected))
    return projection, selected, signs


def page_swap_trace(labels: np.ndarray, projection: np.ndarray, page: str, universe: Universe) -> list[tuple[int, int, float]]:
    idx = universe.page_indices[page]
    lows = [int(i) for i in idx if labels[i] == "L"]
    highs = [int(i) for i in idx if labels[i] == "H"]
    lows.sort(key=lambda i: (-projection[i], int(universe.ordinal[i]), universe.unit_ids[i]))
    highs.sort(key=lambda i: (projection[i], int(universe.ordinal[i]), universe.unit_ids[i]))
    pairs = []
    for low, high in zip(lows, highs, strict=False):
        gain = float(projection[low] - projection[high])
        if gain > 0.0:
            pairs.append((low, high, gain))
    pairs.sort(key=lambda item: (-item[2], int(universe.ordinal[item[0]]), int(universe.ordinal[item[1]])))
    return pairs


def apply_mapping(matrix: np.ndarray, mappings: Mapping[str, Sequence[tuple[int, int, float]]], fraction: float, editions: Sequence[int] = (0, 1, 2)) -> tuple[np.ndarray, dict[str, Any]]:
    planted = np.array(matrix, dtype=np.float64, copy=True)
    applied: dict[str, int] = {}
    total: dict[str, int] = {}
    for page in PAGE_ORDER:
        trace = list(mappings.get(page, ()))
        count = math.floor(fraction * len(trace))
        total[page] = len(trace)
        applied[page] = count
        for low, high, _gain in trace[:count]:
            for eidx in editions:
                planted[eidx, [low, high], :] = planted[eidx, [high, low], :]
    require(np.all(np.isfinite(planted)), "plant made nonfinite matrix")
    return planted, {
        "trace_lengths": total,
        "applied_swaps": applied,
        "total_trace": int(sum(total.values())),
        "total_applied": int(sum(applied.values())),
        "realized_trace_fraction": 0.0 if sum(total.values()) == 0 else float(sum(applied.values()) / sum(total.values())),
    }


def ordinary_plant(matrix: np.ndarray, labels: np.ndarray, world: int, target: str, driver: str, strength: float, universe: Universe, only_folios: set[str] | None = None, reverse_folios: set[str] | None = None, editions: Sequence[int] = (0, 1, 2)) -> tuple[np.ndarray, dict[str, Any]]:
    transforms = build_transforms(matrix, universe)
    projection_matrix = all_folio_projection(transforms)
    projection, selected, signs = projection_values(projection_matrix, world, target, driver, universe)
    info = set(informative_pages(labels, universe))
    mappings: dict[str, list[tuple[int, int, float]]] = {}
    for page in PAGE_ORDER:
        if page not in info or (only_folios is not None and page[:-1] not in only_folios):
            mappings[page] = []
        else:
            direction = -projection if reverse_folios is not None and page[:-1] in reverse_folios else projection
            mappings[page] = page_swap_trace(labels, direction, page, universe)
    planted, stats = apply_mapping(matrix, mappings, strength, editions)
    stats.update({
        "driver_features": list(selected),
        "driver_feature_sha256": text_digest(f"{item}\n" for item in selected),
        "driver_sign_sha256": f8_digest(signs),
        "mapping_sha256": canonical_json_digest({page: [[a, b, gain] for a, b, gain in mappings[page]] for page in PAGE_ORDER}),
    })
    return planted, stats


def matrix_digest(matrix: np.ndarray) -> str:
    require(matrix.shape == (3, 156, 84), "matrix digest shape mismatch")
    return f8_digest(matrix)


def realized_driver_rms(matrix: np.ndarray, labels: np.ndarray, selected: Sequence[str], universe: Universe) -> dict[str, Any]:
    transforms = build_transforms(matrix, universe)
    vectors, _cosines = orientation(labels, transforms, universe)
    inside_idx = np.asarray([universe.eligible.index(feature) for feature in selected], dtype=np.int64)
    outside_idx = np.asarray([i for i, feature in enumerate(universe.eligible) if feature not in set(selected)], dtype=np.int64)
    result: dict[str, Any] = {}
    for edition in EDITIONS:
        vector = vectors[edition]
        inside = math.sqrt(float(np.mean(vector[inside_idx] * vector[inside_idx])))
        outside: float | None
        if len(outside_idx) == 0:
            outside = None
        else:
            outside = math.sqrt(float(np.mean(vector[outside_idx] * vector[outside_idx])))
        result[edition] = {"inside": inside, "outside": outside}
    return result


def contrast_coefficients(rotated: np.ndarray, pages: Sequence[str], universe: Universe) -> dict[str, np.ndarray]:
    result: dict[str, np.ndarray] = {}
    for page in pages:
        idx = universe.page_indices[page]
        labels = rotated[:, idx]
        high = labels == "H"
        low = labels == "L"
        nh = np.sum(high, axis=1)
        nl = np.sum(low, axis=1)
        require(np.all(nh > 0) and np.all(nl > 0), f"rotation lost informative states on {page}")
        result[page] = high / nh[:, None] - low / nl[:, None]
    return result


def target_pages(labels: np.ndarray, universe: Universe) -> tuple[tuple[str, ...], tuple[str, ...]]:
    pages = informative_pages(labels, universe)
    folios = tuple(sorted({page[:-1] for page in pages}))
    return pages, folios


def score_target(
    labels: np.ndarray,
    rotations: np.ndarray,
    transforms: MatrixTransforms,
    universe: Universe,
) -> tuple[
    dict[str, np.ndarray],
    dict[str, dict[str, float]],
    dict[str, dict[str, float]],
    dict[str, dict[str, np.ndarray]],
    dict[str, dict[str, np.ndarray]],
]:
    rotated = rotate_labels(labels, rotations, universe)
    info_pages, info_folios = target_pages(labels, universe)
    coeff = contrast_coefficients(rotated, info_pages, universe)
    t_by_edition = {edition: np.zeros(N_ASSIGN, dtype=np.float64) for edition in EDITIONS}
    identity_contrib: dict[str, dict[str, float]] = {edition: {} for edition in EDITIONS}
    deletion_t: dict[str, dict[str, float]] = {edition: {} for edition in EDITIONS}
    contribution_orbits: dict[str, dict[str, np.ndarray]] = {edition: {} for edition in EDITIONS}
    deletion_orbits: dict[str, dict[str, np.ndarray]] = {edition: {} for edition in EDITIONS}

    # Retain identity fold deltas so deletion can refit every label-dependent
    # training average while keeping the already fitted coordinates fixed.
    fold_delta: dict[tuple[str, str], dict[str, np.ndarray]] = {}
    for held in info_folios:
        for edition in EDITIONS:
            transform = transforms.folds[(held, edition)]
            page_delta = {page: coeff[page] @ transform.standardized[universe.page_indices[page]] for page in info_pages}
            folio_delta: dict[str, np.ndarray] = {}
            for folio in info_folios:
                pages = [page for page in info_pages if page[:-1] == folio]
                folio_delta[folio] = np.mean(np.stack([page_delta[page] for page in pages], axis=0), axis=0)
            held_delta = folio_delta[held]
            train_direction = np.mean(np.stack([folio_delta[g] for g in info_folios if g != held], axis=0), axis=0)
            contribution = np.einsum("ni,ij,nj->n", held_delta, transform.weight, train_direction, optimize=True) / len(transforms.eligible)
            t_by_edition[edition] += contribution / len(info_folios)
            identity_contrib[edition][held] = float(contribution[0])
            contribution_orbits[edition][held] = contribution
            fold_delta[(held, edition)] = folio_delta

    for deleted in info_folios:
        remaining = [folio for folio in info_folios if folio != deleted]
        require(len(remaining) >= 2, "deletion leaves fewer than two folios")
        for edition in EDITIONS:
            contrib: list[np.ndarray] = []
            for held in remaining:
                vectors = fold_delta[(held, edition)]
                train = np.mean(np.stack([vectors[g] for g in remaining if g != held], axis=0), axis=0)
                value = np.einsum(
                    "ni,ij,nj->n",
                    vectors[held],
                    transforms.folds[(held, edition)].weight,
                    train,
                    optimize=True,
                ) / len(transforms.eligible)
                contrib.append(value)
            deletion = np.mean(np.stack(contrib, axis=0), axis=0)
            deletion_orbits[edition][deleted] = deletion
            deletion_t[edition][deleted] = float(deletion[0])
    return t_by_edition, identity_contrib, deletion_t, contribution_orbits, deletion_orbits


def orientation(labels: np.ndarray, transforms: MatrixTransforms, universe: Universe) -> tuple[dict[str, np.ndarray], dict[str, float]]:
    pages, folios = target_pages(labels, universe)
    vectors: dict[str, np.ndarray] = {}
    for edition in EDITIONS:
        z = transforms.all_folio_standardized[edition]
        page_vectors: dict[str, np.ndarray] = {}
        for page in pages:
            idx = universe.page_indices[page]
            page_labels = labels[idx]
            page_vectors[page] = np.mean(z[idx][page_labels == "H"], axis=0) - np.mean(z[idx][page_labels == "L"], axis=0)
        folio_vectors = []
        for folio in folios:
            selected = [page_vectors[page] for page in pages if page[:-1] == folio]
            folio_vectors.append(np.mean(np.stack(selected, axis=0), axis=0))
        vectors[edition] = np.mean(np.stack(folio_vectors, axis=0), axis=0)
    cosines: dict[str, float] = {}
    for left, right in (("ZL3b", "IT2a"), ("ZL3b", "RF1b"), ("IT2a", "RF1b")):
        denom = float(np.linalg.norm(vectors[left]) * np.linalg.norm(vectors[right]))
        require(math.isfinite(denom) and denom > NUM_TOL, "undefined orientation cosine")
        cosines[f"{left}__{right}"] = float(vectors[left] @ vectors[right] / denom)
    return vectors, cosines


def evaluate_matrix(
    matrix: np.ndarray,
    labels_pair: Mapping[str, np.ndarray],
    rotations: Mapping[str, np.ndarray],
    universe: Universe,
    return_internal: bool = False,
) -> Any:
    transforms = build_transforms(matrix, universe)
    orientation_data: dict[str, Any] = {}
    orientation_vectors: dict[str, dict[str, np.ndarray]] = {}
    for target in TARGETS:
        vectors, cosines = orientation(labels_pair[target], transforms, universe)
        orientation_vectors[target] = vectors
        orientation_data[target] = {
            "vector_sha256": {edition: f8_digest(vectors[edition]) for edition in EDITIONS},
            "cosines": cosines,
        }

    ensemble_records: dict[str, Any] = {}
    numeric_ensembles: dict[str, Any] = {}
    target_decision: dict[str, list[bool]] = {target: [] for target in TARGETS}
    for ensemble in ENSEMBLES:
        raw_t: dict[str, dict[str, np.ndarray]] = {}
        contributions: dict[str, dict[str, dict[str, float]]] = {}
        deletions: dict[str, dict[str, dict[str, float]]] = {}
        contribution_orbits: dict[str, dict[str, dict[str, np.ndarray]]] = {}
        deletion_orbits: dict[str, dict[str, dict[str, np.ndarray]]] = {}
        for target in TARGETS:
            (
                raw_t[target],
                contributions[target],
                deletions[target],
                contribution_orbits[target],
                deletion_orbits[target],
            ) = score_target(labels_pair[target], rotations[ensemble], transforms, universe)

        z: dict[str, dict[str, np.ndarray]] = {}
        r: dict[str, np.ndarray] = {}
        for target in TARGETS:
            z[target] = {}
            for edition in EDITIONS:
                values = raw_t[target][edition]
                sd = float(np.std(values, ddof=0))
                require(math.isfinite(sd) and sd > NUM_TOL, "zero/nonfinite null SD")
                z[target][edition] = (values - float(np.mean(values))) / sd
            r[target] = np.min(np.stack([z[target][edition] for edition in EDITIONS], axis=0), axis=0)
        family_m = np.max(np.stack([r[target] for target in TARGETS], axis=0), axis=0)
        targets_record: dict[str, Any] = {}
        for target in TARGETS:
            pvalue = float((1 + np.count_nonzero(family_m[1:] >= r[target][0] - TAIL_TOL)) / N_ASSIGN)
            identity_t = {edition: float(raw_t[target][edition][0]) for edition in EDITIONS}
            identity_z = {edition: float(z[target][edition][0]) for edition in EDITIONS}
            material = {edition: math.copysign(math.sqrt(abs(value)), value) if value != 0.0 else 0.0 for edition, value in identity_t.items()}
            common = [folio for folio in target_pages(labels_pair[target], universe)[1] if all(contributions[target][edition][folio] > NUM_TOL for edition in EDITIONS)]
            required_support = 5 if target == "RAY_LIKE" else 4
            gates = {
                "family_p": pvalue <= 0.05 + NUM_TOL,
                "all_t_positive": all(value > NUM_TOL for value in identity_t.values()),
                "material": min(material.values()) >= 0.05 - NUM_TOL,
                "orientation": all(value >= 0.10 - NUM_TOL for value in orientation_data[target]["cosines"].values()),
                "common_support": len(common) >= required_support,
                "deletion": all(value > NUM_TOL for edition in EDITIONS for value in deletions[target][edition].values()),
            }
            passed = all(gates.values())
            target_decision[target].append(passed)
            targets_record[target] = {
                "T_sha256": {edition: f8_digest(raw_t[target][edition]) for edition in EDITIONS},
                "z_sha256": {edition: f8_digest(z[target][edition]) for edition in EDITIONS},
                "R_sha256": f8_digest(r[target]),
                "identity_T": identity_t,
                "identity_z": identity_z,
                "identity_R": float(r[target][0]),
                "p": pvalue,
                "A": material,
                "identity_contributions": contributions[target],
                "common_positive_folios": common,
                "deletion_T": deletions[target],
                "gates": gates,
                "ensemble_pass": passed,
            }
        ensemble_records[ensemble] = {"M_sha256": f8_digest(family_m), "targets": targets_record}
        numeric_ensembles[ensemble] = {
            "T": raw_t,
            "z": z,
            "R": r,
            "M": family_m,
            "contributions": contribution_orbits,
            "deletions": deletion_orbits,
        }

    complete = {target: bool(all(target_decision[target])) for target in TARGETS}
    checkpoint = {
        "matrix_sha256": matrix_digest(matrix),
        "transforms": transform_checkpoint(transforms),
        "orientation": orientation_data,
        "ensembles": ensemble_records,
        "complete_dual_ensemble_pass": complete,
    }
    if return_internal:
        return checkpoint, {
            "transforms": transforms,
            "orientation_vectors": orientation_vectors,
            "ensembles": numeric_ensembles,
        }
    return checkpoint


def invariance_comparison(
    baseline_checkpoint: Mapping[str, Any],
    baseline_numeric: Mapping[str, Any],
    changed_checkpoint: Mapping[str, Any],
    changed_numeric: Mapping[str, Any],
    tolerance: float,
    compare_orientation_vectors: bool = True,
) -> dict[str, Any]:
    residual_max = 0.0
    for folio in FOLIOS:
        for edition in EDITIONS:
            left = baseline_numeric["transforms"].folds[(folio, edition)].residual
            right = changed_numeric["transforms"].folds[(folio, edition)].residual
            residual_max = max(residual_max, float(np.max(np.abs(left - right))))
    for edition in EDITIONS:
        left = baseline_numeric["transforms"].all_folio_residuals[edition]
        right = changed_numeric["transforms"].all_folio_residuals[edition]
        residual_max = max(residual_max, float(np.max(np.abs(left - right))))
    score_max = 0.0
    for target in TARGETS:
        if compare_orientation_vectors:
            for edition in EDITIONS:
                left = baseline_numeric["orientation_vectors"][target][edition]
                right = changed_numeric["orientation_vectors"][target][edition]
                score_max = max(score_max, float(np.max(np.abs(left - right))))
        for pair in baseline_checkpoint["orientation"][target]["cosines"]:
            score_max = max(
                score_max,
                abs(
                    float(baseline_checkpoint["orientation"][target]["cosines"][pair])
                    - float(changed_checkpoint["orientation"][target]["cosines"][pair])
                ),
            )
    for ensemble in ENSEMBLES:
        left_ensemble = baseline_numeric["ensembles"][ensemble]
        right_ensemble = changed_numeric["ensembles"][ensemble]
        for target in TARGETS:
            for edition in EDITIONS:
                for name in ("T", "z"):
                    left = left_ensemble[name][target][edition]
                    right = right_ensemble[name][target][edition]
                    score_max = max(score_max, float(np.max(np.abs(left - right))))
                for name in ("contributions", "deletions"):
                    for folio in left_ensemble[name][target][edition]:
                        left = left_ensemble[name][target][edition][folio]
                        right = right_ensemble[name][target][edition][folio]
                        score_max = max(
                            score_max,
                            float(np.max(np.abs(left - right))),
                        )
            score_max = max(
                score_max,
                float(np.max(np.abs(left_ensemble["R"][target] - right_ensemble["R"][target]))),
            )
        score_max = max(score_max, float(np.max(np.abs(left_ensemble["M"] - right_ensemble["M"]))))
    gates_identical = baseline_checkpoint["complete_dual_ensemble_pass"] == changed_checkpoint["complete_dual_ensemble_pass"]
    for ensemble in ENSEMBLES:
        for target in TARGETS:
            gates_identical &= (
                baseline_checkpoint["ensembles"][ensemble]["targets"][target]["gates"]
                == changed_checkpoint["ensembles"][ensemble]["targets"][target]["gates"]
            )
    return {
        "residual_max_abs": residual_max,
        "score_max_abs": score_max,
        "tolerance": tolerance,
        "gates_identical": bool(gates_identical),
        "passes": residual_max <= tolerance and score_max <= tolerance and bool(gates_identical),
    }


def numeric_equal(expected: float, observed: float, tolerance: float = 5e-12) -> bool:
    if not (math.isfinite(expected) and math.isfinite(observed)):
        return expected == observed
    return abs(expected - observed) <= tolerance + tolerance * max(abs(expected), abs(observed))


def compare_required(expected: Any, observed: Any, path: str = "result") -> None:
    """Compare every validator-required field, allowing extra result fields."""
    if isinstance(expected, dict):
        require(isinstance(observed, dict), f"{path}: expected object")
        for key, value in expected.items():
            require(key in observed, f"{path}: missing key {key}")
            compare_required(value, observed[key], f"{path}.{key}")
    elif isinstance(expected, list):
        require(isinstance(observed, list), f"{path}: expected list")
        require(len(expected) == len(observed), f"{path}: list length mismatch")
        for i, (left, right) in enumerate(zip(expected, observed, strict=True)):
            compare_required(left, right, f"{path}[{i}]")
    elif isinstance(expected, float):
        require(isinstance(observed, (int, float)) and not isinstance(observed, bool), f"{path}: expected numeric")
        require(numeric_equal(expected, float(observed)), f"{path}: numeric mismatch {expected!r} != {observed!r}")
    else:
        require(expected == observed, f"{path}: mismatch {expected!r} != {observed!r}")


def find_record(records: Sequence[Mapping[str, Any]], keys: Mapping[str, Any], context: str) -> Mapping[str, Any]:
    matches = [record for record in records if all(record.get(key) == value for key, value in keys.items())]
    require(len(matches) == 1, f"{context}: expected one record for {keys}, got {len(matches)}")
    return matches[0]


def required_top_level(result: Mapping[str, Any]) -> None:
    keys = {
        "experiment", "status", "input_hashes", "source_hashes", "target_absence_before",
        "target_absence_after", "preflight_reconstruction", "rotation_ensembles", "label_worlds",
        "null_worlds", "power_worlds", "controls", "gates", "failures", "decision", "claim_ceiling",
        "target_rows_accessed", "morphology_fields_accessed", "target_join_performed",
    }
    missing = sorted(keys - set(result))
    require(not missing, f"result missing top-level keys: {missing}")
    require(result["experiment"] == "SME003", "wrong experiment ID")


def validate_result(result: Mapping[str, Any], universe: Universe, preflight: Mapping[str, Any], frozen_hashes: Mapping[str, str], target_absence_before: Mapping[str, bool]) -> dict[str, Any]:
    required_top_level(result)
    require(result["target_join_performed"] is False, "target_join_performed must be literal false")
    require(result["target_rows_accessed"] is False, "target_rows_accessed must be literal false")
    require(result["morphology_fields_accessed"] is False, "morphology_fields_accessed must be literal false")
    require(result["claim_ceiling"] == CLAIM_CEILING, "claim ceiling mismatch")
    compare_required(target_absence_before, result["target_absence_before"], "target_absence_before")

    expected_input_hashes = {
        MATRIX_PATH.name: frozen_hashes[MATRIX_PATH.name],
        INVENTORY_PATH.name: frozen_hashes[INVENTORY_PATH.name],
        PREFLIGHT_PATH.name: frozen_hashes[PREFLIGHT_PATH.name],
    }
    expected_source_hashes = {
        SPEC_PATH.name: frozen_hashes[SPEC_PATH.name],
        PREFLIGHT_SPEC_PATH.name: frozen_hashes[PREFLIGHT_SPEC_PATH.name],
    }
    compare_required(expected_input_hashes, result["input_hashes"], "input_hashes")
    compare_required(expected_source_hashes, result["source_hashes"], "source_hashes")

    baseline_transforms = build_transforms(universe.values, universe)
    validate_baseline_against_preflight(baseline_transforms, preflight)
    baseline_checkpoint = transform_checkpoint(baseline_transforms)
    compare_required(baseline_checkpoint, result["preflight_reconstruction"], "preflight_reconstruction")

    rotation_builds = {ensemble: build_rotations(ensemble) for ensemble in ENSEMBLES}
    rotations = {ensemble: rotation_builds[ensemble][0] for ensemble in ENSEMBLES}
    expected_rotation = {
        ensemble: {
            "N": N_ASSIGN,
            "shape": [N_ASSIGN, len(PAGE_ORDER)],
            "dtype": "<u2",
            "order": "C",
            "sha256": u2_digest(rotations[ensemble]),
            "unique_rows": N_ASSIGN,
            "row_attempts": [int(item) for item in rotation_builds[ensemble][1]],
            "row_attempts_sha256": u2_digest(rotation_builds[ensemble][1]),
            "maximum_row_attempt": int(np.max(rotation_builds[ensemble][1])),
        }
        for ensemble in ENSEMBLES
    }
    compare_required(expected_rotation, result["rotation_ensembles"], "rotation_ensembles")

    worlds = {world: generate_world(world, universe) for world in range(64)}
    label_records = [label_checkpoint(world, worlds[world], universe) for world in range(64)]
    require(len({item["paired_sha256"] for item in label_records}) == 64, "duplicate paired label world")
    compare_required(label_records, result["label_worlds"], "label_worlds")

    # Null worlds independently rebuild every transform and every one of the
    # 2*2*3*8192 score orbits, not merely the identity summaries.
    observed_null = result["null_worlds"]
    require(isinstance(observed_null, list) and len(observed_null) == 64, "null world grid mismatch")
    null_union_count = 0
    for world in range(64):
        record = find_record(observed_null, {"world": world}, "null_worlds")
        checkpoint = evaluate_matrix(universe.values, worlds[world], rotations, universe)
        expected = {
            "world": world,
            "label_sha256": label_records[world]["paired_sha256"],
            "evaluation": checkpoint,
            "union_pass": bool(any(checkpoint["complete_dual_ensemble_pass"].values())),
        }
        compare_required(expected, record, f"null_worlds[{world}]")
        null_union_count += int(expected["union_pass"])

    observed_power = result["power_worlds"]
    require(isinstance(observed_power, list) and len(observed_power) == 2 * 2 * 4 * 8, "power world grid mismatch")
    power_passes: dict[tuple[str, str, float], int] = {}
    for target in TARGETS:
        for driver in DRIVERS:
            for strength in STRENGTHS:
                passed = 0
                for world in range(8):
                    record = find_record(observed_power, {"target": target, "driver": driver, "strength": strength, "world": world}, "power_worlds")
                    planted, plant_stats = ordinary_plant(universe.values, worlds[world][target], world, target, driver, strength, universe)
                    checkpoint = evaluate_matrix(planted, worlds[world], rotations, universe)
                    complete = bool(checkpoint["complete_dual_ensemble_pass"][target])
                    driver_rms = realized_driver_rms(planted, worlds[world][target], plant_stats["driver_features"], universe)
                    expected = {
                        "world": world,
                        "target": target,
                        "driver": driver,
                        "strength": strength,
                        "label_sha256": label_records[world]["paired_sha256"],
                        "plant": plant_stats,
                        "realized_D_rms": driver_rms,
                        "evaluation": checkpoint,
                        "target_complete_pass": complete,
                    }
                    compare_required(expected, record, f"power_worlds[{target},{driver},{strength},{world}]")
                    passed += int(complete)
                power_passes[(target, driver, strength)] = passed

    control_summary = validate_controls(result["controls"], universe, worlds, label_records, rotations)

    expected_gates: dict[str, Any] = {
        "null_union_pass_count": null_union_count,
        "null_ceiling": null_union_count <= 4,
        "power_pass_counts": {
            target: {driver: {f"{strength:.2f}": power_passes[(target, driver, strength)] for strength in STRENGTHS} for driver in DRIVERS}
            for target in TARGETS
        },
    }
    for target in TARGETS:
        threshold = 7 if target == "RAY_LIKE" else 6
        expected_gates[f"power_{target}_at_075"] = all(power_passes[(target, driver, 0.75)] >= threshold for driver in DRIVERS)
        expected_gates[f"power_{target}_at_100"] = all(power_passes[(target, driver, 1.00)] >= threshold for driver in DRIVERS)
        expected_gates[f"monotone_{target}"] = all(
            power_passes[(target, driver, stronger)] >= power_passes[(target, driver, weaker)] - 1
            for driver in DRIVERS
            for weaker, stronger in zip(STRENGTHS, STRENGTHS[1:], strict=True)
        )
    expected_gates.update(control_summary)
    # Successful independent reconstruction establishes both implementation-
    # integrity gates emitted by the producer; require their literal presence
    # and truth instead of accepting them as unchecked extras.
    expected_gates["deterministic_fixture_reconstruction"] = True
    expected_gates["full_two_target_family_every_evaluation"] = True
    compare_required(expected_gates, result["gates"], "gates")
    require(isinstance(result["failures"], list), "failures must be a list")
    calculated_pass = all(
        bool(value) for key, value in expected_gates.items()
        if key != "null_union_pass_count" and key != "power_pass_counts"
    )
    expected_decision = "PASS_TARGET_FREE_SYNTHETIC_CALIBRATION" if calculated_pass else "FAIL_CLOSE_SME003_BEFORE_TARGET"
    require(result["decision"] == expected_decision, "final decision mismatch")
    require(result["status"] == expected_decision, "status mismatch")
    expected_failures = sorted(
        key for key, value in expected_gates.items()
        if isinstance(value, bool) and not value
    )
    require(result["failures"] == expected_failures, "failure list mismatch")
    return {"decision": expected_decision, "null_union_pass_count": null_union_count, "control_summary": control_summary}


def validate_controls(controls: Any, universe: Universe, worlds: Mapping[int, Mapping[str, np.ndarray]], label_records: Sequence[Mapping[str, Any]], rotations: Mapping[str, np.ndarray]) -> dict[str, bool]:
    """Reconstruct mandatory controls.

    The exact record contract is deliberately descriptor-based.  A producer may
    add diagnostics, but each required record has a unique kind/target/driver/
    world key and contains the same full evaluation checkpoint as primary runs.
    """
    require(isinstance(controls, dict), "controls must be an object")
    whole = controls.get("whole_row")
    require(isinstance(whole, list), "controls.whole_row must be a list")
    required_kinds = ("ONE_FOLIO", "ONE_READING", "REVERSAL", "FOLIO_RANDOM", "OPPOSITE_CLUSTER")
    require(len(whole) == len(required_kinds) * len(TARGETS) * len(DRIVERS) * 8, "whole-row control grid mismatch")
    all_rejected = True
    baseline_projection_cache: dict[tuple[int, str, str], tuple[np.ndarray, tuple[str, ...], np.ndarray]] = {}
    baseline_transforms = build_transforms(universe.values, universe)
    projection_matrix = all_folio_projection(baseline_transforms)

    for kind in required_kinds:
        for target in TARGETS:
            for driver in DRIVERS:
                for world in range(8):
                    record = find_record(whole, {"kind": kind, "target": target, "driver": driver, "world": world}, "controls.whole_row")
                    labels = worlds[world][target]
                    info_folios = list(target_pages(labels, universe)[1])
                    if kind == "ONE_FOLIO":
                        chosen = rank_items(world, f"CONTROL_ONE_FOLIO|{target}", info_folios)[0]
                        planted, stats = ordinary_plant(universe.values, labels, world, target, driver, 1.0, universe, only_folios={chosen})
                        stats["selected_folio"] = chosen
                    elif kind == "ONE_READING":
                        planted, stats = ordinary_plant(universe.values, labels, world, target, driver, 1.0, universe, editions=(0,))
                    elif kind == "REVERSAL":
                        projection, selected, signs = projection_values(projection_matrix, world, target, driver, universe)
                        info_pages = set(informative_pages(labels, universe))
                        forward_maps = {
                            page: page_swap_trace(labels, projection, page, universe) if page in info_pages else []
                            for page in PAGE_ORDER
                        }
                        reverse_maps = {
                            page: page_swap_trace(labels, -projection, page, universe) if page in info_pages else []
                            for page in PAGE_ORDER
                        }
                        planted, stats_forward = apply_mapping(universe.values, forward_maps, 1.0, editions=(0, 1))
                        planted, stats_reverse = apply_mapping(planted, reverse_maps, 1.0, editions=(2,))
                        stats = {
                            "driver_features": list(selected),
                            "driver_feature_sha256": text_digest(f"{item}\n" for item in selected),
                            "driver_sign_sha256": f8_digest(signs),
                            "forward_mapping_sha256": canonical_json_digest({page: [[a, b, gain] for a, b, gain in forward_maps[page]] for page in PAGE_ORDER}),
                            "reverse_mapping_sha256": canonical_json_digest({page: [[a, b, gain] for a, b, gain in reverse_maps[page]] for page in PAGE_ORDER}),
                            "forward": stats_forward,
                            "reverse": stats_reverse,
                        }
                    elif kind == "FOLIO_RANDOM":
                        planted = np.array(universe.values, copy=True)
                        mapping_digest: dict[str, str] = {}
                        total_stats: dict[str, Any] = {}
                        selected = driver_features(world, target, driver, universe)
                        for folio in info_folios:
                            projection, _features, _signs = projection_values(projection_matrix, world, target, driver, universe, folio_random=folio)
                            maps = {page: page_swap_trace(labels, projection, page, universe) if page[:-1] == folio and page in informative_pages(labels, universe) else [] for page in PAGE_ORDER}
                            planted, stat = apply_mapping(planted, maps, 1.0)
                            mapping_digest[folio] = canonical_json_digest({page: [[a, b, gain] for a, b, gain in maps[page]] for page in PAGE_ORDER})
                            total_stats[folio] = stat
                        stats = {"driver_features": list(selected), "folio_mapping_sha256": mapping_digest, "folio_stats": total_stats}
                    else:
                        ordered = rank_items(world, f"CONTROL_CLUSTER|{target}", info_folios)
                        forward_count = 4 if target == "RAY_LIKE" else 3
                        reverse = set(ordered[forward_count:])
                        planted, stats = ordinary_plant(universe.values, labels, world, target, driver, 1.0, universe, reverse_folios=reverse)
                        stats["ordered_folios"] = ordered
                        stats["reverse_folios"] = sorted(reverse)
                    checkpoint = evaluate_matrix(planted, worlds[world], rotations, universe)
                    rejected = not bool(checkpoint["complete_dual_ensemble_pass"][target])
                    if kind == "ONE_FOLIO":
                        required_rejection = all(
                            (not checkpoint["ensembles"][ensemble]["targets"][target]["gates"]["common_support"])
                            or (not checkpoint["ensembles"][ensemble]["targets"][target]["gates"]["deletion"])
                            for ensemble in ENSEMBLES
                        )
                    elif kind in ("ONE_READING", "REVERSAL"):
                        required_rejection = all(
                            any(
                                not checkpoint["ensembles"][ensemble]["targets"][target]["gates"][gate]
                                for gate in ("all_t_positive", "material", "orientation")
                            )
                            for ensemble in ENSEMBLES
                        )
                    else:
                        required_rejection = rejected
                    expected = {
                        "kind": kind,
                        "target": target,
                        "driver": driver,
                        "world": world,
                        "label_sha256": label_records[world]["paired_sha256"],
                        "plant": stats,
                        "evaluation": checkpoint,
                        "target_rejected": rejected,
                        "required_rejection_gate_failed": required_rejection,
                    }
                    compare_required(expected, record, f"controls.whole_row[{kind},{target},{driver},{world}]")
                    all_rejected &= rejected and required_rejection

    # Controls whose construction is not completely pinned to a world by the
    # prose are frozen here to paired world zero.  This convention is declared
    # in the validator and must be mirrored by the result producer.
    invariance_ok = validate_invariance_controls(controls.get("invariance"), universe, worlds[0], rotations)
    complement_ok = validate_complement_control(controls.get("complement"), universe, worlds[0], rotations)
    leakage_ok = validate_leakage_controls(controls.get("leakage"), universe, worlds[0])
    mutation_ok = validate_mutation_manifest(controls.get("mutations"))
    dependence_ok = validate_dependence_controls(controls.get("reading_dependence"), universe, worlds, label_records, rotations)
    return {
        "whole_row_controls_rejected": all_rejected,
        "invariance_controls_pass": invariance_ok,
        "complement_control_pass": complement_ok,
        "leakage_controls_pass": leakage_ok,
        "mutation_controls_pass": mutation_ok,
        "reading_dependence_reported": dependence_ok,
    }


def positional_basis(universe: Universe, basis: str) -> np.ndarray:
    ordinal = universe.ordinal.astype(np.float64)
    size = np.asarray([PAGES[str(page)] for page in universe.page], dtype=np.float64)
    r = (ordinal - 0.5) / size
    a = (ordinal - 0.5) / 16.0
    quarter = np.minimum((r * 4.0).astype(np.int64), 3)
    values = {
        "ABS_CUBIC": a ** 3,
        "REL_CUBIC": r ** 3,
        "PARITY": (universe.ordinal % 2 == 1).astype(np.float64),
        "EARLY": (ordinal <= size / 2.0).astype(np.float64),
        "QUARTER_1": (quarter == 1).astype(np.float64),
        "QUARTER_2": (quarter == 2).astype(np.float64),
        "QUARTER_3": (quarter == 3).astype(np.float64),
    }
    require(basis in values, f"unknown nuisance basis {basis}")
    return centered_by_page(values[basis][:, None], universe)[:, 0]


def response_page_centered_rms(matrix: np.ndarray, edition_index: int, feature: str, universe: Universe) -> float:
    column = matrix[edition_index, :, universe.feature_index[feature]][:, None]
    centered = centered_by_page(column, universe)[:, 0]
    rms = math.sqrt(float(np.mean(centered * centered)))
    require(math.isfinite(rms) and rms > NUM_TOL, f"zero/nonfinite response RMS: {EDITIONS[edition_index]} {feature}")
    return rms


def add_page_centered_component(matrix: np.ndarray, basis: np.ndarray, fraction: float, domain: str, universe: Universe, features: Sequence[str]) -> np.ndarray:
    out = np.array(matrix, copy=True)
    rms = math.sqrt(float(np.mean(basis * basis)))
    require(rms > NUM_TOL, "zero control basis RMS")
    normalized = basis / rms
    for feature in features:
        idx = universe.feature_index[feature]
        digest = synth_digest(0, domain, feature)
        sign = 1.0 if digest[-1] & 1 else -1.0
        for eidx in range(3):
            amplitude = fraction * response_page_centered_rms(matrix, eidx, feature, universe)
            out[eidx, :, idx] += amplitude * sign * normalized
    return out


def validate_invariance_controls(records: Any, universe: Universe, labels_pair: Mapping[str, np.ndarray], rotations: Mapping[str, np.ndarray]) -> bool:
    require(isinstance(records, list) and len(records) == 10, "invariance control grid mismatch")
    baseline, baseline_numeric = evaluate_matrix(universe.values, labels_pair, rotations, universe, return_internal=True)
    bases = ("ABS_CUBIC", "REL_CUBIC", "PARITY", "EARLY", "QUARTER_1", "QUARTER_2", "QUARTER_3")
    ok = True
    for basis_name in bases:
        basis = positional_basis(universe, basis_name)
        features = [item for item in universe.eligible if item != "PARA_WORD_COUNT"]
        modified = add_page_centered_component(universe.values, basis, 0.5, f"CONTROL_NUISANCE|{basis_name}", universe, features)
        evaluation, numeric = evaluate_matrix(modified, labels_pair, rotations, universe, return_internal=True)
        comparison = invariance_comparison(baseline, baseline_numeric, evaluation, numeric, 1e-10)
        record = find_record(records, {"kind": basis_name, "world": 0}, "controls.invariance")
        expected = {"kind": basis_name, "world": 0, "matrix_sha256": matrix_digest(modified), "evaluation": evaluation, "invariance": comparison}
        compare_required(expected, record, f"controls.invariance[{basis_name}]")
        ok &= bool(comparison["passes"])

    wc = universe.values[:, :, universe.feature_index["PARA_WORD_COUNT"]]
    for power, kind in ((1, "LENGTH_LINEAR"), (3, "LENGTH_CUBIC")):
        modified = np.array(universe.values, copy=True)
        for eidx in range(3):
            basis = centered_by_page((np.log1p(wc[eidx]) ** power)[:, None], universe)[:, 0]
            rms = math.sqrt(float(np.mean(basis * basis)))
            require(rms > NUM_TOL, "zero word-count control RMS")
            for feature in universe.root:
                sign = 1.0 if synth_digest(0, f"CONTROL_LENGTH|{kind}", feature)[-1] & 1 else -1.0
                amplitude = 0.5 * response_page_centered_rms(universe.values, eidx, feature, universe)
                modified[eidx, :, universe.feature_index[feature]] += sign * amplitude * basis / rms
        evaluation, numeric = evaluate_matrix(modified, labels_pair, rotations, universe, return_internal=True)
        comparison = invariance_comparison(baseline, baseline_numeric, evaluation, numeric, 1e-10)
        record = find_record(records, {"kind": kind, "world": 0}, "controls.invariance")
        expected = {"kind": kind, "world": 0, "matrix_sha256": matrix_digest(modified), "evaluation": evaluation, "invariance": comparison}
        compare_required(expected, record, f"controls.invariance[{kind}]")
        ok &= bool(comparison["passes"])

    modified = np.array(universe.values, copy=True)
    for eidx in range(3):
        for page in PAGE_ORDER:
            idx = universe.page_indices[page]
            for feature in [item for item in universe.eligible if item != "PARA_WORD_COUNT"]:
                digest = synth_digest(0, f"CONTROL_PAGE_CONSTANT|{page}", feature)
                sign = 1.0 if digest[-1] & 1 else -1.0
                rms = response_page_centered_rms(universe.values, eidx, feature, universe)
                modified[eidx, idx, universe.feature_index[feature]] += 0.10 * sign * rms
    evaluation, numeric = evaluate_matrix(modified, labels_pair, rotations, universe, return_internal=True)
    comparison = invariance_comparison(baseline, baseline_numeric, evaluation, numeric, 1e-12)
    record = find_record(records, {"kind": "PAGE_CONSTANT", "world": 0}, "controls.invariance")
    expected = {"kind": "PAGE_CONSTANT", "world": 0, "matrix_sha256": matrix_digest(modified), "evaluation": evaluation, "invariance": comparison}
    compare_required(expected, record, "controls.invariance[PAGE_CONSTANT]")
    ok &= bool(comparison["passes"])
    return ok


def validate_complement_control(record: Any, universe: Universe, labels_pair: Mapping[str, np.ndarray], rotations: Mapping[str, np.ndarray]) -> bool:
    require(isinstance(record, dict), "complement control absent")
    baseline, baseline_numeric = evaluate_matrix(universe.values, labels_pair, rotations, universe, return_internal=True)
    complemented = {target: np.where(labels_pair[target] == "L", "H", np.where(labels_pair[target] == "H", "L", "X")) for target in TARGETS}
    evaluation, numeric = evaluate_matrix(universe.values, complemented, rotations, universe, return_internal=True)
    comparison = invariance_comparison(
        baseline,
        baseline_numeric,
        evaluation,
        numeric,
        1e-12,
        compare_orientation_vectors=False,
    )
    reversal_max = max(
        float(np.max(np.abs(
            baseline_numeric["orientation_vectors"][target][edition]
            + numeric["orientation_vectors"][target][edition]
        )))
        for target in TARGETS
        for edition in EDITIONS
    )
    invariant = comparison["passes"] and reversal_max <= 1e-12
    expected = {
        "world": 0,
        "baseline": baseline,
        "complemented": evaluation,
        "score_invariance": comparison,
        "orientation_reversal_max_abs": reversal_max,
        "decision_invariant": invariant,
    }
    compare_required(expected, record, "controls.complement")
    return invariant


def identity_training_direction(transform: FoldTransform, labels: np.ndarray, held: str, universe: Universe) -> np.ndarray | None:
    pages, folios = target_pages(labels, universe)
    if held not in folios:
        return None
    vectors: list[np.ndarray] = []
    for folio in folios:
        if folio == held:
            continue
        page_vectors = []
        for page in pages:
            if page[:-1] != folio:
                continue
            idx = universe.page_indices[page]
            state = labels[idx]
            z = transform.standardized[idx]
            page_vectors.append(np.mean(z[state == "H"], axis=0) - np.mean(z[state == "L"], axis=0))
        vectors.append(np.mean(np.stack(page_vectors, axis=0), axis=0))
    return np.mean(np.stack(vectors, axis=0), axis=0)


def validate_leakage_controls(records: Any, universe: Universe, labels_pair: Mapping[str, np.ndarray]) -> bool:
    require(isinstance(records, list) and len(records) == len(FOLIOS), "leakage control grid mismatch")
    baseline = build_transforms(universe.values, universe)
    ok = True
    for folio in FOLIOS:
        mutated = np.array(universe.values, copy=True)
        for page in [page for page in PAGE_ORDER if page[:-1] == folio]:
            idx = universe.page_indices[page]
            ordering = rank_items(0, f"CONTROL_HELD_MUTATION|{folio}", (universe.unit_ids[i] for i in idx))
            source = np.asarray([universe.unit_ids.index(item) for item in ordering], dtype=np.int64)
            mutated[:, idx, :] = mutated[:, source, :]
        changed = build_transforms(mutated, universe)
        pre: dict[str, Any] = {}
        post: dict[str, Any] = {}
        for edition in EDITIONS:
            train = universe.folio != folio
            before = baseline.folds[(folio, edition)]
            after = changed.folds[(folio, edition)]
            before_direction = {
                target: None if (value := identity_training_direction(before, labels_pair[target], folio, universe)) is None else f8_digest(value)
                for target in TARGETS
            }
            after_direction = {
                target: None if (value := identity_training_direction(after, labels_pair[target], folio, universe)) is None else f8_digest(value)
                for target in TARGETS
            }
            pre[edition] = {
                "weight": f8_digest(before.weight),
                "training_rows": f8_digest(before.standardized[train]),
                "training_directions": before_direction,
            }
            post[edition] = {
                "weight": f8_digest(after.weight),
                "training_rows": f8_digest(after.standardized[train]),
                "training_directions": after_direction,
            }
        unchanged = pre == post
        record = find_record(records, {"held_folio": folio}, "controls.leakage")
        expected = {"held_folio": folio, "pre": pre, "post": post, "unchanged": unchanged}
        compare_required(expected, record, f"controls.leakage[{folio}]")
        ok &= unchanged
    return ok


def validate_mutation_manifest(records: Any) -> bool:
    names = (
        "duplicate", "missing", "extra", "page_split", "folio_drift", "ordinal_gap", "locus_drift",
        "edition_drift", "reordered_feature", "negative_word_count", "nonfinite", "zero_scale",
        "nonpositive_shrunk_covariance", "rotation_bias", "target_artifact",
    )
    require(isinstance(records, list) and len(records) == len(names), "mutation manifest grid mismatch")
    ok = True
    for name in names:
        record = find_record(records, {"mutation": name}, "controls.mutations")
        # Mutation fixtures are intentionally implementation-local and are not
        # opened by this validator.  Require a canonical public description and
        # fail-closed outcome; the validator's own parsers/numeric guards cover
        # the corresponding contracts on the real anonymous inputs.
        expected = {"mutation": name, "rejected": True}
        compare_required(expected, record, f"controls.mutations[{name}]")
        ok &= record.get("rejected") is True and isinstance(record.get("error"), str) and bool(record["error"])
    return ok


def validate_dependence_controls(records: Any, universe: Universe, worlds: Mapping[int, Mapping[str, np.ndarray]], label_records: Sequence[Mapping[str, Any]], rotations: Mapping[str, np.ndarray]) -> bool:
    require(isinstance(records, list) and len(records) == len(TARGETS) * len(DRIVERS) * 8, "reading-dependence grid mismatch")
    for target in TARGETS:
        for driver in DRIVERS:
            for world in range(8):
                baseline = np.array(universe.values, copy=True)
                permutation_digests: dict[str, str] = {}
                for eidx, edition in enumerate(EDITIONS):
                    for page in PAGE_ORDER:
                        idx = universe.page_indices[page]
                        destinations = rank_items(world, f"CONTROL_INDEPENDENT_BASELINE|{edition}|{page}", (universe.unit_ids[i] for i in idx))
                        destination_idx = np.asarray([universe.unit_ids.index(item) for item in destinations], dtype=np.int64)
                        baseline[eidx, destination_idx, :] = universe.values[eidx, idx, :]
                        permutation_digests[f"{edition}__{page}"] = text_digest(
                            f"{universe.unit_ids[source]},{universe.unit_ids[destination]}\n"
                            for source, destination in zip(idx, destination_idx, strict=True)
                        )
                planted, stats = ordinary_plant(baseline, worlds[world][target], world, target, driver, 1.0, universe)
                evaluation = evaluate_matrix(planted, worlds[world], rotations, universe)
                record = find_record(records, {"target": target, "driver": driver, "world": world}, "controls.reading_dependence")
                expected = {
                    "target": target,
                    "driver": driver,
                    "world": world,
                    "label_sha256": label_records[world]["paired_sha256"],
                    "baseline_matrix_sha256": matrix_digest(baseline),
                    "reading_page_permutation_sha256": permutation_digests,
                    "plant": stats,
                    "evaluation": evaluation,
                    "diagnostic_only": True,
                }
                compare_required(expected, record, f"controls.reading_dependence[{target},{driver},{world}]")
    return True


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result", type=Path, default=DEFAULT_RESULT_PATH, help="SME003 target-free calibration JSON")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        frozen_hashes = verify_frozen_sources()
        universe, preflight = load_universe()
        target_paths = target_paths_from_preflight(preflight)
        before = assert_target_absence(target_paths, "before validation")
        result_path = args.result.resolve()
        require(REPO == result_path or REPO in result_path.parents, "result path escapes repository")
        if not result_path.is_file():
            print(json.dumps({
                "experiment": "SME003",
                "validator_status": "BLOCKED_RESULT_ABSENT",
                "result": str(result_path.relative_to(REPO)),
                "target_artifacts_absent": True,
                "message": "Calibration result does not yet exist; no scores were run and no artifact was written.",
            }, sort_keys=True))
            return 2
        result = load_json(result_path)
        require(isinstance(result, dict), "result root must be an object")
        summary = validate_result(result, universe, preflight, frozen_hashes, before)
        after = assert_target_absence(target_paths, "after validation")
        compare_required(after, result["target_absence_after"], "target_absence_after")
        print(json.dumps({
            "experiment": "SME003",
            "validator_status": "PASS_INDEPENDENT_TARGET_FREE_CALIBRATION_RECONSTRUCTION",
            **summary,
            "target_artifacts_absent": True,
        }, sort_keys=True))
        return 0
    except (ValidationError, KeyError, TypeError, ValueError, np.linalg.LinAlgError) as exc:
        print(json.dumps({
            "experiment": "SME003",
            "validator_status": "FAIL_INDEPENDENT_RECONSTRUCTION",
            "error": str(exc),
        }, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
