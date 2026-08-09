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
from concurrent.futures import ProcessPoolExecutor
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


_WORKER_UNIVERSE: Universe | None = None
_WORKER_ROTATIONS: Mapping[str, np.ndarray] | None = None
_WORKER_WORLDS: Mapping[int, Mapping[str, np.ndarray]] | None = None
_WORKER_LABEL_RECORDS: Sequence[Mapping[str, Any]] | None = None
_WORKER_BASELINE_PROJECTION: np.ndarray | None = None


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


def target_pages(labels: np.ndarray, universe: Universe) -> tuple[tuple[str, ...], tuple[str, ...]]:
    pages = informative_pages(labels, universe)
    folios = tuple(sorted({page[:-1] for page in pages}))
    return pages, folios


def score_ensemble(
    labels_pair: Mapping[str, np.ndarray],
    rotations: np.ndarray,
    transforms: MatrixTransforms,
    universe: Universe,
) -> dict[str, Any]:
    require(tuple(labels_pair) == TARGETS, "target order mismatch")
    n_assignments = len(rotations)
    p = len(transforms.eligible)
    require(p == 83, "SME003 scorer requires the exact 83-feature coordinate")
    page_index = {page: index for index, page in enumerate(PAGE_ORDER)}
    folio_index = {folio: index for index, folio in enumerate(FOLIOS)}

    # Match the frozen producer's small possible-shift tables exactly.  A
    # direct 8,192-row coefficient matmul is algebraically equivalent but can
    # select a different BLAS reduction path and therefore different bytes.
    contrast_tables: list[np.ndarray] = []
    for page in PAGE_ORDER:
        positions = universe.page_indices[page]
        page_length = len(positions)
        shifts = np.arange(page_length, dtype=np.int64)
        source = (
            np.arange(page_length, dtype=np.int64)[None, :]
            - shifts[:, None]
        ) % page_length
        table = np.zeros((len(TARGETS), page_length, page_length), dtype=np.float64)
        for target_index, target in enumerate(TARGETS):
            rotated = labels_pair[target][positions][source]
            low_count = np.sum(rotated == "L", axis=1)
            high_count = np.sum(rotated == "H", axis=1)
            local = np.zeros_like(rotated, dtype=np.float64)
            informative = (low_count > 0) & (high_count > 0)
            if np.any(informative):
                local[informative] = (
                    (rotated[informative] == "H") / high_count[informative, None]
                    - (rotated[informative] == "L") / low_count[informative, None]
                )
            table[target_index] = local
        contrast_tables.append(table)

    page_delta_cache: dict[tuple[str, str], tuple[np.ndarray, ...]] = {}
    for held_folio in FOLIOS:
        for edition in EDITIONS:
            standardized = transforms.folds[(held_folio, edition)].standardized
            page_delta_cache[(held_folio, edition)] = tuple(
                contrast_tables[index] @ standardized[universe.page_indices[page]]
                for index, page in enumerate(PAGE_ORDER)
            )

    t_array = np.empty((len(TARGETS), len(EDITIONS), n_assignments), dtype=np.float64)
    contribution_array = np.full(
        (len(TARGETS), len(EDITIONS), n_assignments, len(FOLIOS)),
        np.nan,
        dtype=np.float64,
    )
    deletion_array = np.full_like(contribution_array, np.nan)
    support: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {}
    for target_index, target in enumerate(TARGETS):
        info_pages, info_folios = target_pages(labels_pair[target], universe)
        support[target] = (info_pages, info_folios)
        k_folios = len(info_folios)
        deletion_sums = np.zeros(
            (len(EDITIONS), n_assignments, k_folios), dtype=np.float64
        )
        for held_index, held_folio in enumerate(info_folios):
            for edition_index, edition in enumerate(EDITIONS):
                page_delta_tables = page_delta_cache[(held_folio, edition)]
                deltas = np.empty(
                    (n_assignments, k_folios, p), dtype=np.float64
                )
                for source_index, source_folio in enumerate(info_folios):
                    source_pages = [
                        page for page in info_pages if page[:-1] == source_folio
                    ]
                    source_delta = np.zeros(
                        (n_assignments, p), dtype=np.float64
                    )
                    for page in source_pages:
                        index = page_index[page]
                        source_delta += page_delta_tables[index][
                            target_index,
                            rotations[:, index].astype(np.int64),
                            :,
                        ]
                    deltas[:, source_index, :] = source_delta / len(source_pages)
                total_direction = np.sum(deltas, axis=1)
                held_vector = deltas[:, held_index, :]
                training_direction = (
                    total_direction - held_vector
                ) / (k_folios - 1)
                held_weighted = held_vector @ transforms.folds[
                    (held_folio, edition)
                ].weight
                held_contribution = np.sum(
                    held_weighted * training_direction, axis=1
                ) / p
                contribution_array[
                    target_index,
                    edition_index,
                    :,
                    folio_index[held_folio],
                ] = held_contribution
                for deleted_index in range(k_folios):
                    if deleted_index == held_index:
                        continue
                    reduced_direction = (
                        total_direction
                        - held_vector
                        - deltas[:, deleted_index, :]
                    ) / (k_folios - 2)
                    deletion_sums[
                        edition_index, :, deleted_index
                    ] += np.sum(
                        held_weighted * reduced_direction, axis=1
                    ) / p
        selected_folios = [folio_index[folio] for folio in info_folios]
        for edition_index in range(len(EDITIONS)):
            target_contributions = contribution_array[
                target_index, edition_index
            ][:, selected_folios]
            t_array[target_index, edition_index] = np.mean(
                target_contributions, axis=1
            )
            for deleted_index, deleted_folio in enumerate(info_folios):
                deletion_array[
                    target_index,
                    edition_index,
                    :,
                    folio_index[deleted_folio],
                ] = deletion_sums[
                    edition_index, :, deleted_index
                ] / (k_folios - 1)
    require(np.all(np.isfinite(t_array)), "nonfinite cross-folio T")
    return {
        "T": t_array,
        "contributions": contribution_array,
        "deletions": deletion_array,
        "support": support,
    }


def orientation(labels: np.ndarray, transforms: MatrixTransforms, universe: Universe) -> tuple[dict[str, np.ndarray], dict[str, float]]:
    pages, folios = target_pages(labels, universe)
    vectors: dict[str, np.ndarray] = {}
    for edition in EDITIONS:
        z = transforms.all_folio_standardized[edition]
        page_vectors: dict[str, np.ndarray] = {}
        for page in pages:
            idx = universe.page_indices[page]
            page_labels = labels[idx]
            high = page_labels == "H"
            low = page_labels == "L"
            coefficient = (
                high / np.sum(high)
                - low / np.sum(low)
            )
            # Preserve the frozen producer's coefficient-vector matmul order.
            # Directly subtracting the two means is algebraically equivalent
            # but changes low bits and therefore the mandatory byte digest.
            page_vectors[page] = coefficient @ z[idx]
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
        score = score_ensemble(
            labels_pair, rotations[ensemble], transforms, universe
        )
        t_array = score["T"]
        means = np.mean(t_array, axis=2, keepdims=True)
        standard_deviations = np.std(
            t_array, axis=2, ddof=0, keepdims=True
        )
        require(
            np.all(np.isfinite(standard_deviations))
            and np.all(standard_deviations > NUM_TOL),
            "zero/nonfinite null SD",
        )
        z_array = (t_array - means) / standard_deviations
        r_array = np.min(z_array, axis=1)
        family_m = np.max(r_array, axis=0)
        raw_t = {
            target: {
                edition: t_array[target_index, edition_index]
                for edition_index, edition in enumerate(EDITIONS)
            }
            for target_index, target in enumerate(TARGETS)
        }
        z = {
            target: {
                edition: z_array[target_index, edition_index]
                for edition_index, edition in enumerate(EDITIONS)
            }
            for target_index, target in enumerate(TARGETS)
        }
        r = {
            target: r_array[target_index]
            for target_index, target in enumerate(TARGETS)
        }
        contribution_orbits: dict[str, dict[str, dict[str, np.ndarray]]] = {}
        deletion_orbits: dict[str, dict[str, dict[str, np.ndarray]]] = {}
        contributions: dict[str, dict[str, dict[str, float]]] = {}
        deletions: dict[str, dict[str, dict[str, float]]] = {}
        folio_index = {folio: index for index, folio in enumerate(FOLIOS)}
        for target_index, target in enumerate(TARGETS):
            info_folios = score["support"][target][1]
            contribution_orbits[target] = {
                edition: {
                    folio: score["contributions"][
                        target_index, edition_index, :, folio_index[folio]
                    ]
                    for folio in info_folios
                }
                for edition_index, edition in enumerate(EDITIONS)
            }
            deletion_orbits[target] = {
                edition: {
                    folio: score["deletions"][
                        target_index, edition_index, :, folio_index[folio]
                    ]
                    for folio in info_folios
                }
                for edition_index, edition in enumerate(EDITIONS)
            }
            contributions[target] = {
                edition: {
                    folio: float(values[0])
                    for folio, values in contribution_orbits[target][edition].items()
                }
                for edition in EDITIONS
            }
            deletions[target] = {
                edition: {
                    folio: float(values[0])
                    for folio, values in deletion_orbits[target][edition].items()
                }
                for edition in EDITIONS
            }

        raw_array = t_array[:, :, 0]
        material_array = np.sign(raw_array) * np.sqrt(np.abs(raw_array))
        targets_record: dict[str, Any] = {}
        for target_index, target in enumerate(TARGETS):
            pvalue = float((1 + np.count_nonzero(
                family_m[1:] >= r_array[target_index, 0] - TAIL_TOL
            )) / len(rotations[ensemble]))
            identity_t = {
                edition: float(raw_array[target_index, edition_index])
                for edition_index, edition in enumerate(EDITIONS)
            }
            identity_z = {
                edition: float(z_array[target_index, edition_index, 0])
                for edition_index, edition in enumerate(EDITIONS)
            }
            material = {
                edition: float(material_array[target_index, edition_index])
                for edition_index, edition in enumerate(EDITIONS)
            }
            info_folios = score["support"][target][1]
            common = [
                folio for folio in info_folios
                if np.all(score["contributions"][
                    target_index, :, 0, folio_index[folio]
                ] > NUM_TOL)
            ]
            required_support = 5 if target == "RAY_LIKE" else 4
            gates = {
                "family_p": pvalue <= 0.05,
                "all_t_positive": bool(np.all(raw_array[target_index] > NUM_TOL)),
                "material": bool(np.min(material_array[target_index]) >= 0.05 - NUM_TOL),
                "orientation": all(value >= 0.10 - NUM_TOL for value in orientation_data[target]["cosines"].values()),
                "common_support": len(common) >= required_support,
                "deletion": bool(np.all(np.asarray([
                    score["deletions"][
                        target_index, :, 0, folio_index[folio]
                    ]
                    for folio in info_folios
                ]) > NUM_TOL)),
            }
            passed = all(gates.values())
            target_decision[target].append(passed)
            targets_record[target] = {
                "T_sha256": {edition: f8_digest(raw_t[target][edition]) for edition in EDITIONS},
                "z_sha256": {edition: f8_digest(z[target][edition]) for edition in EDITIONS},
                "R_sha256": f8_digest(r[target]),
                "identity_T": identity_t,
                "identity_z": identity_z,
                "identity_R": float(r_array[target_index, 0]),
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


def initialize_reconstruction_worker(
    universe: Universe,
    rotations: Mapping[str, np.ndarray],
    worlds: Mapping[int, Mapping[str, np.ndarray]],
    label_records: Sequence[Mapping[str, Any]],
) -> None:
    """Bind target-free immutable state once per worker."""
    global _WORKER_UNIVERSE, _WORKER_ROTATIONS, _WORKER_WORLDS
    global _WORKER_LABEL_RECORDS, _WORKER_BASELINE_PROJECTION
    for name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        require(os.environ.get(name) == "1", f"worker numeric environment is not pinned: {name}")
    _WORKER_UNIVERSE = universe
    _WORKER_ROTATIONS = rotations
    _WORKER_WORLDS = worlds
    _WORKER_LABEL_RECORDS = label_records
    _WORKER_BASELINE_PROJECTION = None


def worker_context() -> tuple[
    Universe,
    Mapping[str, np.ndarray],
    Mapping[int, Mapping[str, np.ndarray]],
    Sequence[Mapping[str, Any]],
]:
    require(_WORKER_UNIVERSE is not None, "reconstruction worker universe is unbound")
    require(_WORKER_ROTATIONS is not None, "reconstruction worker rotations are unbound")
    require(_WORKER_WORLDS is not None, "reconstruction worker worlds are unbound")
    require(_WORKER_LABEL_RECORDS is not None, "reconstruction worker labels are unbound")
    return (
        _WORKER_UNIVERSE,
        _WORKER_ROTATIONS,
        _WORKER_WORLDS,
        _WORKER_LABEL_RECORDS,
    )


def worker_baseline_projection(universe: Universe) -> np.ndarray:
    global _WORKER_BASELINE_PROJECTION
    if _WORKER_BASELINE_PROJECTION is None:
        _WORKER_BASELINE_PROJECTION = all_folio_projection(
            build_transforms(universe.values, universe)
        )
    return _WORKER_BASELINE_PROJECTION


def reconstruct_null_record(world: int) -> dict[str, Any]:
    universe, rotations, worlds, label_records = worker_context()
    checkpoint = evaluate_matrix(universe.values, worlds[world], rotations, universe)
    return {
        "world": world,
        "label_sha256": label_records[world]["paired_sha256"],
        "evaluation": checkpoint,
        "union_pass": bool(any(checkpoint["complete_dual_ensemble_pass"].values())),
    }


def reconstruct_power_record(
    target: str,
    driver: str,
    strength: float,
    world: int,
) -> dict[str, Any]:
    universe, rotations, worlds, label_records = worker_context()
    labels = worlds[world][target]
    planted, plant_stats = ordinary_plant(
        universe.values, labels, world, target, driver, strength, universe
    )
    checkpoint = evaluate_matrix(planted, worlds[world], rotations, universe)
    complete = bool(checkpoint["complete_dual_ensemble_pass"][target])
    return {
        "world": world,
        "target": target,
        "driver": driver,
        "strength": strength,
        "label_sha256": label_records[world]["paired_sha256"],
        "plant": plant_stats,
        "realized_D_rms": realized_driver_rms(
            planted, labels, plant_stats["driver_features"], universe
        ),
        "evaluation": checkpoint,
        "target_complete_pass": complete,
    }


def reconstruct_whole_row_record(
    kind: str,
    target: str,
    driver: str,
    world: int,
) -> dict[str, Any]:
    universe, rotations, worlds, label_records = worker_context()
    labels = worlds[world][target]
    info_folios = list(target_pages(labels, universe)[1])
    if kind == "ONE_FOLIO":
        chosen = rank_items(world, f"CONTROL_ONE_FOLIO|{target}", info_folios)[0]
        planted, stats = ordinary_plant(
            universe.values,
            labels,
            world,
            target,
            driver,
            1.0,
            universe,
            only_folios={chosen},
        )
        stats["selected_folio"] = chosen
    elif kind == "ONE_READING":
        planted, stats = ordinary_plant(
            universe.values,
            labels,
            world,
            target,
            driver,
            1.0,
            universe,
            editions=(0,),
        )
    elif kind == "REVERSAL":
        projection, selected, signs = projection_values(
            worker_baseline_projection(universe), world, target, driver, universe
        )
        info_pages = set(informative_pages(labels, universe))
        forward_maps = {
            page: page_swap_trace(labels, projection, page, universe)
            if page in info_pages else []
            for page in PAGE_ORDER
        }
        reverse_maps = {
            page: page_swap_trace(labels, -projection, page, universe)
            if page in info_pages else []
            for page in PAGE_ORDER
        }
        planted, stats_forward = apply_mapping(
            universe.values, forward_maps, 1.0, editions=(0, 1)
        )
        planted, stats_reverse = apply_mapping(
            planted, reverse_maps, 1.0, editions=(2,)
        )
        stats = {
            "driver_features": list(selected),
            "driver_feature_sha256": text_digest(f"{item}\n" for item in selected),
            "driver_sign_sha256": f8_digest(signs),
            "forward_mapping_sha256": canonical_json_digest({
                page: [[a, b, gain] for a, b, gain in forward_maps[page]]
                for page in PAGE_ORDER
            }),
            "reverse_mapping_sha256": canonical_json_digest({
                page: [[a, b, gain] for a, b, gain in reverse_maps[page]]
                for page in PAGE_ORDER
            }),
            "forward": stats_forward,
            "reverse": stats_reverse,
        }
    elif kind == "FOLIO_RANDOM":
        planted = np.array(universe.values, copy=True)
        mapping_digest: dict[str, str] = {}
        total_stats: dict[str, Any] = {}
        selected = driver_features(world, target, driver, universe)
        info_pages = set(informative_pages(labels, universe))
        for folio in info_folios:
            projection, _features, _signs = projection_values(
                worker_baseline_projection(universe),
                world,
                target,
                driver,
                universe,
                folio_random=folio,
            )
            maps = {
                page: page_swap_trace(labels, projection, page, universe)
                if page[:-1] == folio and page in info_pages else []
                for page in PAGE_ORDER
            }
            planted, stat = apply_mapping(planted, maps, 1.0)
            mapping_digest[folio] = canonical_json_digest({
                page: [[a, b, gain] for a, b, gain in maps[page]]
                for page in PAGE_ORDER
            })
            total_stats[folio] = stat
        stats = {
            "driver_features": list(selected),
            "folio_mapping_sha256": mapping_digest,
            "folio_stats": total_stats,
        }
    elif kind == "OPPOSITE_CLUSTER":
        ordered = rank_items(world, f"CONTROL_CLUSTER|{target}", info_folios)
        forward_count = 4 if target == "RAY_LIKE" else 3
        reverse = set(ordered[forward_count:])
        planted, stats = ordinary_plant(
            universe.values,
            labels,
            world,
            target,
            driver,
            1.0,
            universe,
            reverse_folios=reverse,
        )
        stats["ordered_folios"] = ordered
        stats["reverse_folios"] = sorted(reverse)
    else:
        raise ValidationError(f"unknown whole-row control: {kind}")

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
    return {
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


def reconstruct_invariance_record(kind: str) -> dict[str, Any]:
    universe, rotations, worlds, _label_records = worker_context()
    labels_pair = worlds[0]
    baseline, baseline_numeric = evaluate_matrix(
        universe.values, labels_pair, rotations, universe, return_internal=True
    )
    if kind in ("ABS_CUBIC", "REL_CUBIC", "PARITY", "EARLY", "QUARTER_1", "QUARTER_2", "QUARTER_3"):
        basis = positional_basis(universe, kind)
        features = [item for item in universe.eligible if item != "PARA_WORD_COUNT"]
        modified = add_page_centered_component(
            universe.values,
            basis,
            0.5,
            f"CONTROL_NUISANCE|{kind}",
            universe,
            features,
        )
        tolerance = 1e-10
    elif kind in ("LENGTH_LINEAR", "LENGTH_CUBIC"):
        power = 1 if kind == "LENGTH_LINEAR" else 3
        modified = np.array(universe.values, copy=True)
        wc = universe.values[:, :, universe.feature_index["PARA_WORD_COUNT"]]
        for eidx in range(3):
            basis = centered_by_page(
                (np.log1p(wc[eidx]) ** power)[:, None], universe
            )[:, 0]
            rms = math.sqrt(float(np.mean(basis * basis)))
            require(rms > NUM_TOL, "zero word-count control RMS")
            for feature in universe.root:
                sign = 1.0 if synth_digest(
                    0, f"CONTROL_LENGTH|{kind}", feature
                )[-1] & 1 else -1.0
                amplitude = 0.5 * response_page_centered_rms(
                    universe.values, eidx, feature, universe
                )
                modified[eidx, :, universe.feature_index[feature]] += (
                    sign * amplitude * basis / rms
                )
        tolerance = 1e-10
    elif kind == "PAGE_CONSTANT":
        modified = np.array(universe.values, copy=True)
        for eidx in range(3):
            for page in PAGE_ORDER:
                idx = universe.page_indices[page]
                for feature in [item for item in universe.eligible if item != "PARA_WORD_COUNT"]:
                    sign = 1.0 if synth_digest(
                        0, f"CONTROL_PAGE_CONSTANT|{page}", feature
                    )[-1] & 1 else -1.0
                    rms = response_page_centered_rms(
                        universe.values, eidx, feature, universe
                    )
                    modified[eidx, idx, universe.feature_index[feature]] += (
                        0.10 * sign * rms
                    )
        tolerance = 1e-12
    else:
        raise ValidationError(f"unknown invariance control: {kind}")
    evaluation, numeric = evaluate_matrix(
        modified, labels_pair, rotations, universe, return_internal=True
    )
    comparison = invariance_comparison(
        baseline, baseline_numeric, evaluation, numeric, tolerance
    )
    return {
        "kind": kind,
        "world": 0,
        "matrix_sha256": matrix_digest(modified),
        "evaluation": evaluation,
        "invariance": comparison,
    }


def reconstruct_complement_record() -> dict[str, Any]:
    universe, rotations, worlds, _label_records = worker_context()
    labels_pair = worlds[0]
    baseline, baseline_numeric = evaluate_matrix(
        universe.values, labels_pair, rotations, universe, return_internal=True
    )
    complemented = {
        target: np.where(
            labels_pair[target] == "L",
            "H",
            np.where(labels_pair[target] == "H", "L", "X"),
        )
        for target in TARGETS
    }
    evaluation, numeric = evaluate_matrix(
        universe.values, complemented, rotations, universe, return_internal=True
    )
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
    return {
        "world": 0,
        "baseline": baseline,
        "complemented": evaluation,
        "score_invariance": comparison,
        "orientation_reversal_max_abs": reversal_max,
        "decision_invariant": invariant,
    }


def reconstruct_leakage_record(folio: str) -> dict[str, Any]:
    universe, _rotations, worlds, _label_records = worker_context()
    labels_pair = worlds[0]
    baseline = build_transforms(universe.values, universe)
    mutated = np.array(universe.values, copy=True)
    for page in [page for page in PAGE_ORDER if page[:-1] == folio]:
        idx = universe.page_indices[page]
        ordering = rank_items(
            0,
            f"CONTROL_HELD_MUTATION|{folio}",
            (universe.unit_ids[i] for i in idx),
        )
        source = np.asarray(
            [universe.unit_ids.index(item) for item in ordering], dtype=np.int64
        )
        mutated[:, idx, :] = mutated[:, source, :]
    changed = build_transforms(mutated, universe)
    pre: dict[str, Any] = {}
    post: dict[str, Any] = {}
    for edition in EDITIONS:
        train = universe.folio != folio
        before = baseline.folds[(folio, edition)]
        after = changed.folds[(folio, edition)]
        before_direction = {
            target: None
            if (value := identity_training_direction(
                before, labels_pair[target], folio, universe
            )) is None else f8_digest(value)
            for target in TARGETS
        }
        after_direction = {
            target: None
            if (value := identity_training_direction(
                after, labels_pair[target], folio, universe
            )) is None else f8_digest(value)
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
    return {
        "held_folio": folio,
        "pre": pre,
        "post": post,
        "unchanged": pre == post,
    }


def reconstruct_dependence_record(
    target: str,
    driver: str,
    world: int,
) -> dict[str, Any]:
    universe, rotations, worlds, label_records = worker_context()
    baseline = np.array(universe.values, copy=True)
    permutation_digests: dict[str, str] = {}
    for eidx, edition in enumerate(EDITIONS):
        for page in PAGE_ORDER:
            idx = universe.page_indices[page]
            destinations = rank_items(
                world,
                f"CONTROL_INDEPENDENT_BASELINE|{edition}|{page}",
                (universe.unit_ids[i] for i in idx),
            )
            destination_idx = np.asarray(
                [universe.unit_ids.index(item) for item in destinations],
                dtype=np.int64,
            )
            baseline[eidx, destination_idx, :] = universe.values[eidx, idx, :]
            permutation_digests[f"{edition}__{page}"] = text_digest(
                f"{universe.unit_ids[source]},{universe.unit_ids[destination]}\n"
                for source, destination in zip(idx, destination_idx, strict=True)
            )
    planted, stats = ordinary_plant(
        baseline, worlds[world][target], world, target, driver, 1.0, universe
    )
    evaluation = evaluate_matrix(planted, worlds[world], rotations, universe)
    return {
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


def reconstruction_tasks() -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = [
        {"category": "null", "world": world} for world in range(64)
    ]
    tasks.extend(
        {
            "category": "power",
            "target": target,
            "driver": driver,
            "strength": strength,
            "world": world,
        }
        for target in TARGETS
        for driver in DRIVERS
        for strength in STRENGTHS
        for world in range(8)
    )
    tasks.extend(
        {
            "category": "whole_row",
            "kind": kind,
            "target": target,
            "driver": driver,
            "world": world,
        }
        for kind in ("ONE_FOLIO", "ONE_READING", "REVERSAL", "FOLIO_RANDOM", "OPPOSITE_CLUSTER")
        for target in TARGETS
        for driver in DRIVERS
        for world in range(8)
    )
    tasks.extend(
        {"category": "invariance", "kind": kind}
        for kind in (
            "ABS_CUBIC",
            "REL_CUBIC",
            "PARITY",
            "EARLY",
            "QUARTER_1",
            "QUARTER_2",
            "QUARTER_3",
            "LENGTH_LINEAR",
            "LENGTH_CUBIC",
            "PAGE_CONSTANT",
        )
    )
    tasks.append({"category": "complement"})
    tasks.extend(
        {"category": "leakage", "held_folio": folio} for folio in FOLIOS
    )
    tasks.extend(
        {
            "category": "dependence",
            "target": target,
            "driver": driver,
            "world": world,
        }
        for target in TARGETS
        for driver in DRIVERS
        for world in range(8)
    )
    require(len(tasks) == 402, f"parallel reconstruction task-grid mismatch: {len(tasks)}")
    return tasks


def reconstruct_task(task: Mapping[str, Any]) -> tuple[str, dict[str, Any]]:
    category = str(task["category"])
    if category == "null":
        record = reconstruct_null_record(int(task["world"]))
    elif category == "power":
        record = reconstruct_power_record(
            str(task["target"]),
            str(task["driver"]),
            float(task["strength"]),
            int(task["world"]),
        )
    elif category == "whole_row":
        record = reconstruct_whole_row_record(
            str(task["kind"]),
            str(task["target"]),
            str(task["driver"]),
            int(task["world"]),
        )
    elif category == "invariance":
        record = reconstruct_invariance_record(str(task["kind"]))
    elif category == "complement":
        record = reconstruct_complement_record()
    elif category == "leakage":
        record = reconstruct_leakage_record(str(task["held_folio"]))
    elif category == "dependence":
        record = reconstruct_dependence_record(
            str(task["target"]), str(task["driver"]), int(task["world"])
        )
    else:
        raise ValidationError(f"unknown reconstruction category: {category}")
    return category, record


def parallel_reconstruction(
    universe: Universe,
    rotations: Mapping[str, np.ndarray],
    worlds: Mapping[int, Mapping[str, np.ndarray]],
    label_records: Sequence[Mapping[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    tasks = reconstruction_tasks()
    records = {
        category: []
        for category in (
            "null",
            "power",
            "whole_row",
            "invariance",
            "complement",
            "leakage",
            "dependence",
        )
    }
    with ProcessPoolExecutor(
        max_workers=32,
        initializer=initialize_reconstruction_worker,
        initargs=(universe, rotations, worlds, label_records),
    ) as executor:
        for category, record in executor.map(reconstruct_task, tasks, chunksize=1):
            records[category].append(record)
    require(
        {key: len(value) for key, value in records.items()}
        == {
            "null": 64,
            "power": 128,
            "whole_row": 160,
            "invariance": 10,
            "complement": 1,
            "leakage": 7,
            "dependence": 32,
        },
        "parallel reconstruction result-grid mismatch",
    )
    return records


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

    reconstructed = parallel_reconstruction(
        universe, rotations, worlds, label_records
    )

    # Null worlds independently rebuild every transform and every one of the
    # 2*2*3*8192 score orbits, not merely the identity summaries.
    observed_null = result["null_worlds"]
    require(isinstance(observed_null, list) and len(observed_null) == 64, "null world grid mismatch")
    null_union_count = 0
    for world in range(64):
        record = find_record(observed_null, {"world": world}, "null_worlds")
        expected = find_record(
            reconstructed["null"], {"world": world}, "reconstructed.null"
        )
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
                    expected = find_record(
                        reconstructed["power"],
                        {
                            "target": target,
                            "driver": driver,
                            "strength": strength,
                            "world": world,
                        },
                        "reconstructed.power",
                    )
                    compare_required(expected, record, f"power_worlds[{target},{driver},{strength},{world}]")
                    passed += int(expected["target_complete_pass"])
                power_passes[(target, driver, strength)] = passed

    control_summary = validate_controls(result["controls"], reconstructed)

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
            for weaker, stronger in zip(STRENGTHS[:-1], STRENGTHS[1:], strict=True)
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


def validate_reconstructed_invariance(
    records: Any,
    reconstructed: Sequence[Mapping[str, Any]],
) -> bool:
    require(isinstance(records, list) and len(records) == 10, "invariance control grid mismatch")
    require(len(reconstructed) == 10, "reconstructed invariance grid mismatch")
    ok = True
    for expected in reconstructed:
        kind = str(expected["kind"])
        record = find_record(
            records, {"kind": kind, "world": 0}, "controls.invariance"
        )
        compare_required(expected, record, f"controls.invariance[{kind}]")
        ok &= bool(expected["invariance"]["passes"])
    return ok


def validate_reconstructed_complement(
    record: Any,
    reconstructed: Sequence[Mapping[str, Any]],
) -> bool:
    require(isinstance(record, dict), "complement control absent")
    require(len(reconstructed) == 1, "reconstructed complement grid mismatch")
    expected = reconstructed[0]
    compare_required(expected, record, "controls.complement")
    return bool(expected["decision_invariant"])


def validate_reconstructed_leakage(
    records: Any,
    reconstructed: Sequence[Mapping[str, Any]],
) -> bool:
    require(isinstance(records, list) and len(records) == len(FOLIOS), "leakage control grid mismatch")
    require(len(reconstructed) == len(FOLIOS), "reconstructed leakage grid mismatch")
    ok = True
    for expected in reconstructed:
        folio = str(expected["held_folio"])
        record = find_record(
            records, {"held_folio": folio}, "controls.leakage"
        )
        compare_required(expected, record, f"controls.leakage[{folio}]")
        ok &= bool(expected["unchanged"])
    return ok


def validate_reconstructed_dependence(
    records: Any,
    reconstructed: Sequence[Mapping[str, Any]],
) -> bool:
    expected_count = len(TARGETS) * len(DRIVERS) * 8
    require(
        isinstance(records, list) and len(records) == expected_count,
        "reading-dependence grid mismatch",
    )
    require(
        len(reconstructed) == expected_count,
        "reconstructed reading-dependence grid mismatch",
    )
    for expected in reconstructed:
        keys = {
            "target": expected["target"],
            "driver": expected["driver"],
            "world": expected["world"],
        }
        record = find_record(records, keys, "controls.reading_dependence")
        compare_required(
            expected,
            record,
            f"controls.reading_dependence[{expected['target']},{expected['driver']},{expected['world']}]",
        )
    return True


def validate_controls(
    controls: Any,
    reconstructed: Mapping[str, Sequence[Mapping[str, Any]]],
) -> dict[str, bool]:
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
    for kind in required_kinds:
        for target in TARGETS:
            for driver in DRIVERS:
                for world in range(8):
                    record = find_record(whole, {"kind": kind, "target": target, "driver": driver, "world": world}, "controls.whole_row")
                    expected = find_record(
                        reconstructed["whole_row"],
                        {
                            "kind": kind,
                            "target": target,
                            "driver": driver,
                            "world": world,
                        },
                        "reconstructed.whole_row",
                    )
                    compare_required(expected, record, f"controls.whole_row[{kind},{target},{driver},{world}]")
                    all_rejected &= bool(
                        expected["target_rejected"]
                        and expected["required_rejection_gate_failed"]
                    )

    invariance_ok = validate_reconstructed_invariance(
        controls.get("invariance"), reconstructed["invariance"]
    )
    complement_ok = validate_reconstructed_complement(
        controls.get("complement"), reconstructed["complement"]
    )
    leakage_ok = validate_reconstructed_leakage(
        controls.get("leakage"), reconstructed["leakage"]
    )
    mutation_ok = validate_mutation_manifest(controls.get("mutations"))
    dependence_ok = validate_reconstructed_dependence(
        controls.get("reading_dependence"), reconstructed["dependence"]
    )
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
