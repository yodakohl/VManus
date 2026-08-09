#!/usr/bin/env python3
"""Label-agnostic SME003 transform and cross-folio scoring core.

The module reads only caller-supplied anonymous matrix/inventory paths.  It
does not know morphology paths, generate labels or plants, or write results.
Production and validation drivers are responsible for source/result manifests
and target-artifact absence checks.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

import numpy as np


EDITIONS = ("ZL3b", "IT2a", "RF1b")
TARGET_IDS = ("RAY_LIKE", "TAIL_LIKE")
ENSEMBLE_IDS = ("INDEPENDENT_PAGE", "COUPLED_FOLIO")
META_FIELDS = ("unit_id", "page", "physical_folio", "star_ordinal", "locus", "edition")
EXPECTED_INPUT_HASHES = {
    "anonymous_paragraph_matrix.tsv": "b246456b181b07e847c6d5a49b959b0346eff6a4c6febb8a543de104c505a26a",
    "anonymous_feature_inventory.json": "088232b431b4b9746bb94a08328cb969fb7c21c6a28cd112286da40d6429fea5",
}
EXPECTED_PAGE_SIZES = {
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
EXPECTED_FOLIOS = ("f104", "f105", "f107", "f112", "f113", "f114", "f115")
EXPECTED_INELIGIBLE = ("OPEN_FIRST_HAS_Q",)
SCALE_TOL = 1e-10
NUM_TOL = 1e-15
TAIL_TIE_TOL = 1e-12
MATERIAL_THRESHOLD = 0.05
ORIENTATION_THRESHOLD = 0.10


@dataclass(frozen=True)
class TargetRule:
    low: int
    high: int
    ignored: int
    informative_pages: int
    informative_folios: int
    common_support: int


TARGET_RULES = {
    "RAY_LIKE": TargetRule(66, 83, 7, 12, 7, 5),
    "TAIL_LIKE": TargetRule(133, 22, 1, 8, 6, 4),
}


@dataclass(frozen=True)
class AnonymousPanel:
    unit_ids: tuple[str, ...]
    pages: np.ndarray
    folios: np.ndarray
    ordinals: np.ndarray
    loci: tuple[str, ...]
    editions: tuple[str, ...]
    features: tuple[str, ...]
    formal_features: tuple[str, ...]
    root_atom_features: tuple[str, ...]
    root_word_features: tuple[str, ...]
    values: np.ndarray  # unit x edition x feature
    page_names: tuple[str, ...]
    folio_names: tuple[str, ...]
    page_positions: tuple[np.ndarray, ...]  # ordinal-sorted positions
    input_hashes: Mapping[str, str]


@dataclass(frozen=True)
class FoldTransform:
    held_folio: str
    training_mask: np.ndarray
    residuals: np.ndarray  # unit x edition x all input features, before RMS scaling
    standardized: np.ndarray  # edition x unit x eligible feature
    scales: np.ndarray  # edition x all input features
    weights: np.ndarray  # edition x eligible feature x eligible feature
    diagnostics: tuple[Mapping[str, float | int | bool | str], ...]
    digests: Mapping[str, str]


@dataclass(frozen=True)
class AllFolioTransform:
    residuals: np.ndarray  # unit x edition x all input features, before RMS scaling
    standardized: np.ndarray  # edition x unit x eligible feature
    scales: np.ndarray  # edition x all input features
    digests: Mapping[str, str]


@dataclass(frozen=True)
class TransformBundle:
    panel: AnonymousPanel
    eligible_mask: np.ndarray
    eligible_features: tuple[str, ...]
    folds: Mapping[str, FoldTransform]
    all_folio: AllFolioTransform
    digests: Mapping[str, str]


@dataclass(frozen=True)
class TargetSupport:
    target: str
    informative_pages: tuple[str, ...]
    informative_folios: tuple[str, ...]
    pages_per_folio: Mapping[str, int]


@dataclass(frozen=True)
class PairedLabels:
    """Two caller-supplied state vectors bound to the panel's canonical units."""

    unit_ids: tuple[str, ...]
    targets: Mapping[str, Sequence[str]]


@dataclass(frozen=True)
class EnsembleScore:
    ensemble: str
    target_ids: tuple[str, ...]
    T: np.ndarray  # target x edition x assignment
    z: np.ndarray  # target x edition x assignment
    robust_R: np.ndarray  # target x assignment
    family_M: np.ndarray  # assignment
    contributions: np.ndarray  # target x edition x assignment x panel folio
    deletion_T: np.ndarray  # target x edition x assignment x panel folio
    raw_T: np.ndarray  # target x edition
    raw_A: np.ndarray  # target x edition
    family_p: Mapping[str, float]
    orientation_cosines: Mapping[str, Mapping[str, float]]
    common_positive_folios: Mapping[str, tuple[str, ...]]
    gates: Mapping[str, Mapping[str, bool]]
    target_pass: Mapping[str, bool]
    supports: Mapping[str, TargetSupport]
    digests: Mapping[str, str | Mapping[str, str]]


@dataclass(frozen=True)
class DualEnsembleScore:
    ensembles: Mapping[str, EnsembleScore]
    target_pass: Mapping[str, bool]
    any_target_pass: bool
    gates: Mapping[str, bool]
    digests: Mapping[str, str]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            block = stream.read(1 << 20)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def array_sha256(values: np.ndarray, dtype: str = "<f8") -> str:
    canonical = np.asarray(values, dtype=np.dtype(dtype), order="C")
    return hashlib.sha256(canonical.tobytes(order="C")).hexdigest()


def string_list_sha256(values: Sequence[str]) -> str:
    payload = "".join(value + "\n" for value in values).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def digest_map_sha256(values: Mapping[str, str]) -> str:
    payload = json.dumps(values, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def _page_center(values: np.ndarray, pages: np.ndarray) -> np.ndarray:
    centered = np.empty_like(values, dtype=np.float64)
    for page in sorted(set(pages.tolist())):
        mask = pages == page
        centered[mask] = values[mask] - np.mean(values[mask], axis=0, keepdims=True)
    return centered


def _readonly(values: np.ndarray) -> np.ndarray:
    values.setflags(write=False)
    return values


def load_anonymous_panel(
    matrix_path: str | Path,
    inventory_path: str | Path,
    *,
    require_frozen_hashes: bool = True,
) -> AnonymousPanel:
    """Load and strictly validate the frozen anonymous 156-unit panel."""
    matrix = Path(matrix_path)
    inventory_file = Path(inventory_path)
    hashes = {
        "anonymous_paragraph_matrix.tsv": sha256_file(matrix),
        "anonymous_feature_inventory.json": sha256_file(inventory_file),
    }
    if require_frozen_hashes and hashes != EXPECTED_INPUT_HASHES:
        raise ValueError(f"anonymous input hash mismatch: {hashes}")

    with matrix.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        header = list(reader.fieldnames or ())
        rows = [dict(row) for row in reader if row.get("page") != "f106r"]
    inventory = json.loads(inventory_file.read_text(encoding="utf-8"))
    if tuple(header[:len(META_FIELDS)]) != META_FIELDS:
        raise ValueError("anonymous metadata fields or order changed")
    features = tuple(header[len(META_FIELDS):])
    formal = tuple(inventory["formal_features"])
    atoms = tuple(inventory["root_atom_features"])
    words = tuple(inventory["root_compound_word_features"])
    if (len(formal), len(atoms), len(words)) != (34, 32, 18):
        raise ValueError("feature partition must be exactly 34 formal + 32 atom + 18 word")
    partition = formal + tuple("ROOT_ATOM_RATE__" + name for name in atoms) + tuple(
        "ROOT_WORD_RATE__" + name for name in words
    )
    if len(features) != 84 or features != tuple(inventory["all_features"]) or features != partition:
        raise ValueError("ordered 84-feature inventory contract failed")

    unit_ids = tuple(sorted({row["unit_id"] for row in rows}))
    lookup: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        key = (row["unit_id"], row["edition"])
        if key in lookup:
            raise ValueError(f"duplicate anonymous unit/edition row: {key}")
        lookup[key] = row
    if len(unit_ids) != 156 or len(rows) != 468 or len(lookup) != 468:
        raise ValueError("anonymous matrix must contain 156 units and 468 unique reading rows")
    for unit in unit_ids:
        if {edition for candidate, edition in lookup if candidate == unit} != set(EDITIONS):
            raise ValueError(f"unit lacks exact three-reading coverage: {unit}")

    first = [lookup[(unit, EDITIONS[0])] for unit in unit_ids]
    pages = np.asarray([row["page"] for row in first], dtype=object)
    folios = np.asarray([row["physical_folio"] for row in first], dtype=object)
    ordinals = np.asarray([int(row["star_ordinal"]) for row in first], dtype=np.int64)
    loci = tuple(row["locus"] for row in first)
    page_names = tuple(sorted(set(pages.tolist())))
    folio_names = tuple(sorted(set(folios.tolist())))
    sizes = {page: int(np.count_nonzero(pages == page)) for page in page_names}
    if sizes != EXPECTED_PAGE_SIZES or folio_names != EXPECTED_FOLIOS:
        raise ValueError("exact page-size or seven-folio contract failed")
    page_positions: list[np.ndarray] = []
    for page in page_names:
        positions = np.flatnonzero(pages == page)
        if set(folios[positions].tolist()) != {page[:-1]}:
            raise ValueError(f"page-to-folio drift on {page}")
        order = np.argsort(ordinals[positions], kind="stable")
        positions = positions[order]
        if ordinals[positions].tolist() != list(range(1, sizes[page] + 1)):
            raise ValueError(f"ordinal gap or duplicate on {page}")
        page_positions.append(_readonly(positions))

    values = np.empty((156, 3, 84), dtype=np.float64)
    for unit_index, unit in enumerate(unit_ids):
        for edition_index, edition in enumerate(EDITIONS):
            row = lookup[(unit, edition)]
            if (
                row["page"] != pages[unit_index]
                or row["physical_folio"] != folios[unit_index]
                or int(row["star_ordinal"]) != ordinals[unit_index]
                or row["locus"] != loci[unit_index]
            ):
                raise ValueError(f"alternate-reading metadata drift for {unit}/{edition}")
            try:
                values[unit_index, edition_index] = [float(row[feature]) for feature in features]
            except (KeyError, ValueError) as error:
                raise ValueError(f"invalid anonymous numeric row for {unit}/{edition}") from error
    if not np.isfinite(values).all():
        raise ValueError("nonfinite anonymous feature cell")
    word_index = features.index("PARA_WORD_COUNT")
    if np.any(values[:, :, word_index] < 0.0):
        raise ValueError("PARA_WORD_COUNT must be nonnegative")

    return AnonymousPanel(
        unit_ids=unit_ids,
        pages=_readonly(pages),
        folios=_readonly(folios),
        ordinals=_readonly(ordinals),
        loci=loci,
        editions=EDITIONS,
        features=features,
        formal_features=formal,
        root_atom_features=atoms,
        root_word_features=words,
        values=_readonly(values),
        page_names=page_names,
        folio_names=folio_names,
        page_positions=tuple(page_positions),
        input_hashes=hashes,
    )


def formal_nuisance_design(panel: AnonymousPanel) -> np.ndarray:
    """Return the frozen page-centered 11-column position design."""
    page_sizes = EXPECTED_PAGE_SIZES
    relative = np.asarray([
        (ordinal - 0.5) / page_sizes[page]
        for page, ordinal in zip(panel.pages, panel.ordinals)
    ], dtype=np.float64)
    absolute = (panel.ordinals.astype(np.float64) - 0.5) / 16.0
    early = np.asarray([
        ordinal <= page_sizes[page] / 2.0
        for page, ordinal in zip(panel.pages, panel.ordinals)
    ], dtype=np.float64)
    quarter = np.minimum((relative * 4.0).astype(np.int64), 3)
    design = np.column_stack((
        relative,
        relative ** 2,
        relative ** 3,
        absolute,
        absolute ** 2,
        absolute ** 3,
        (panel.ordinals % 2 == 1).astype(np.float64),
        early,
        (quarter == 1).astype(np.float64),
        (quarter == 2).astype(np.float64),
        (quarter == 3).astype(np.float64),
    ))
    design = _page_center(design, panel.pages)
    if design.shape != (156, 11) or not np.isfinite(design).all():
        raise ValueError("invalid formal nuisance design")
    return design


def _residualize(
    panel: AnonymousPanel,
    values: np.ndarray,
    training_mask: np.ndarray,
    formal_design: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    if training_mask.shape != (156,) or training_mask.dtype != np.bool_ or not np.any(training_mask):
        raise ValueError("invalid nuisance training mask")
    residuals = np.empty_like(values, dtype=np.float64)
    scales = np.empty((3, 84), dtype=np.float64)
    word_index = panel.features.index("PARA_WORD_COUNT")
    for edition_index in range(3):
        centered_values = _page_center(values[:, edition_index, :], panel.pages)
        log_length = np.log1p(values[:, edition_index, word_index])
        length_design = _page_center(np.column_stack((
            log_length,
            log_length ** 2,
            log_length ** 3,
        )), panel.pages)
        if not np.isfinite(length_design).all():
            raise ValueError("nonfinite root-length nuisance design")
        for feature_index in range(84):
            if feature_index < 34:
                design = formal_design
            else:
                design = np.concatenate((formal_design, length_design), axis=1)
            beta = np.linalg.lstsq(
                design[training_mask], centered_values[training_mask, feature_index], rcond=None
            )[0]
            residuals[:, edition_index, feature_index] = (
                centered_values[:, feature_index] - design @ beta
            )
        scales[edition_index] = np.sqrt(np.mean(
            residuals[training_mask, edition_index, :] ** 2, axis=0
        ))
    return residuals, scales


def analytic_oas(training: np.ndarray) -> tuple[np.ndarray, Mapping[str, float | int | bool]]:
    """Frozen population-covariance analytic shrinkage and precision matrix."""
    if training.ndim != 2 or training.shape[0] < 2 or training.shape[1] < 1:
        raise ValueError("OAS input must be a nonempty two-dimensional training matrix")
    if not np.isfinite(training).all():
        raise ValueError("nonfinite OAS input")
    n, p = training.shape
    covariance = (training.T @ training) / n
    if not np.isfinite(covariance).all():
        raise ValueError("nonfinite population covariance")
    mu = float(np.trace(covariance) / p)
    if not np.isfinite(mu) or mu <= NUM_TOL:
        raise ValueError("nonpositive covariance trace")
    alpha = float(np.mean(covariance * covariance))
    denominator = float((n + 1) * (alpha - mu * mu / p))
    rho = 1.0 if denominator <= NUM_TOL else min(1.0, (alpha + mu * mu) / denominator)
    shrunk = (1.0 - rho) * covariance + rho * mu * np.eye(p)
    if not np.isfinite(shrunk).all():
        raise ValueError("nonfinite shrunk covariance")
    eigenvalues = np.linalg.eigvalsh(shrunk)
    if eigenvalues[0] <= NUM_TOL:
        raise ValueError("nonpositive shrunk covariance")
    weight = np.linalg.inv(shrunk)
    if not np.isfinite(weight).all():
        raise ValueError("nonfinite covariance inverse")
    weight *= p / float(np.trace(weight))
    weight_eigenvalues = np.linalg.eigvalsh(weight)
    symmetry = float(np.max(np.abs(weight - weight.T)))
    trace = float(np.trace(weight))
    if weight_eigenvalues[0] <= NUM_TOL or symmetry > 1e-10 or abs(trace - p) > 1e-8:
        raise ValueError("invalid normalized precision matrix")
    diagnostics: Mapping[str, float | int | bool] = {
        "n": n,
        "p": p,
        "mu": mu,
        "alpha": alpha,
        "denominator": denominator,
        "rho": rho,
        "covariance_min_eigenvalue": float(eigenvalues[0]),
        "covariance_max_eigenvalue": float(eigenvalues[-1]),
        "covariance_condition": float(eigenvalues[-1] / eigenvalues[0]),
        "weight_symmetry_max_abs": symmetry,
        "weight_trace": trace,
        "weight_min_eigenvalue": float(weight_eigenvalues[0]),
        "finite_covariance": True,
        "finite_weight": True,
    }
    return weight, diagnostics


def build_transforms(
    panel: AnonymousPanel,
    values: np.ndarray | None = None,
    *,
    require_exact_eligibility: bool = True,
) -> TransformBundle:
    """Fit all seven held-folio coordinates and the all-folio coordinate."""
    candidate = panel.values if values is None else np.asarray(values, dtype=np.float64)
    if candidate.shape != (156, 3, 84) or not np.isfinite(candidate).all():
        raise ValueError("candidate anonymous matrix must be finite with shape 156x3x84")
    word_index = panel.features.index("PARA_WORD_COUNT")
    if np.any(candidate[:, :, word_index] < 0.0):
        raise ValueError("PARA_WORD_COUNT must be nonnegative before log1p")
    design = formal_nuisance_design(panel)

    residuals_by_folio: dict[str, np.ndarray] = {}
    scales_by_folio: dict[str, np.ndarray] = {}
    for held_folio in panel.folio_names:
        training = np.asarray(panel.folios != held_folio, dtype=bool)
        residuals, scales = _residualize(panel, candidate, training, design)
        residuals_by_folio[held_folio] = residuals
        scales_by_folio[held_folio] = scales

    eligible = np.ones(84, dtype=bool)
    for scales in scales_by_folio.values():
        eligible &= np.all(np.isfinite(scales) & (scales > SCALE_TOL), axis=0)
    eligible_features = tuple(feature for feature, keep in zip(panel.features, eligible) if keep)
    ineligible = tuple(feature for feature, keep in zip(panel.features, eligible) if not keep)
    formal_count = sum(feature in panel.formal_features for feature in eligible_features)
    root_count = len(eligible_features) - formal_count
    if formal_count < 24 or root_count < 32:
        raise ValueError("eligible feature capacity below frozen floor")
    expected_eligible = tuple(feature for feature in panel.features if feature not in EXPECTED_INELIGIBLE)
    if require_exact_eligibility and (
        eligible_features != expected_eligible
        or ineligible != EXPECTED_INELIGIBLE
        or (formal_count, root_count) != (33, 50)
    ):
        raise ValueError("world changed the exact validated 83-feature eligibility intersection")

    folds: dict[str, FoldTransform] = {}
    fold_digest_manifest: dict[str, str] = {}
    for held_folio in panel.folio_names:
        training = np.asarray(panel.folios != held_folio, dtype=bool)
        standardized = np.empty((3, 156, len(eligible_features)), dtype=np.float64)
        weights = np.empty((3, len(eligible_features), len(eligible_features)), dtype=np.float64)
        diagnostics: list[Mapping[str, float | int | bool | str]] = []
        digests: dict[str, str] = {
            "training_units": string_list_sha256(sorted(np.asarray(panel.unit_ids, dtype=object)[training].tolist())),
            "held_units": string_list_sha256(sorted(np.asarray(panel.unit_ids, dtype=object)[~training].tolist())),
        }
        for edition_index, edition in enumerate(panel.editions):
            scales = scales_by_folio[held_folio][edition_index, eligible]
            standardized[edition_index] = (
                residuals_by_folio[held_folio][:, edition_index, eligible] / scales
            )
            if not np.isfinite(standardized[edition_index]).all():
                raise ValueError(f"nonfinite standardized fold matrix {held_folio}/{edition}")
            weight, diagnostic = analytic_oas(standardized[edition_index, training])
            weights[edition_index] = weight
            diagnostic = dict(diagnostic)
            diagnostic.update({
                "eligible_scale_min": float(np.min(scales)),
                "eligible_scale_max": float(np.max(scales)),
                "finite_standardized": True,
            })
            diagnostics.append(diagnostic)
            digests[f"residual__{edition}"] = array_sha256(
                residuals_by_folio[held_folio][:, edition_index, :]
            )
            digests[f"training_residual__{edition}"] = array_sha256(
                residuals_by_folio[held_folio][training, edition_index, :]
            )
            digests[f"standardized__{edition}"] = array_sha256(standardized[edition_index])
            digests[f"training_standardized__{edition}"] = array_sha256(standardized[edition_index, training])
            digests[f"scales__{edition}"] = array_sha256(scales)
            digests[f"weight__{edition}"] = array_sha256(weight)
        digests["combined"] = digest_map_sha256(digests)
        fold_digest_manifest[held_folio] = digests["combined"]
        folds[held_folio] = FoldTransform(
            held_folio=held_folio,
            training_mask=_readonly(training),
            residuals=_readonly(residuals_by_folio[held_folio]),
            standardized=_readonly(standardized),
            scales=_readonly(scales_by_folio[held_folio]),
            weights=_readonly(weights),
            diagnostics=tuple(diagnostics),
            digests=digests,
        )

    all_training = np.ones(156, dtype=bool)
    all_residuals, all_scales = _residualize(panel, candidate, all_training, design)
    all_standardized = np.empty((3, 156, len(eligible_features)), dtype=np.float64)
    all_digests: dict[str, str] = {}
    for edition_index, edition in enumerate(panel.editions):
        scales = all_scales[edition_index, eligible]
        if not np.isfinite(scales).all() or np.any(scales <= SCALE_TOL):
            raise ValueError(f"invalid all-folio scale for {edition}")
        all_standardized[edition_index] = all_residuals[:, edition_index, eligible] / scales
        if not np.isfinite(all_standardized[edition_index]).all():
            raise ValueError(f"nonfinite all-folio standardized transform for {edition}")
        all_digests[f"standardized__{edition}"] = array_sha256(all_standardized[edition_index])
        all_digests[f"residual__{edition}"] = array_sha256(all_residuals[:, edition_index, :])
        all_digests[f"scales__{edition}"] = array_sha256(scales)
    all_digests["combined"] = digest_map_sha256(all_digests)
    transform_digests = {
        **{"fold__" + folio: digest for folio, digest in fold_digest_manifest.items()},
        "all_folio": all_digests["combined"],
        "eligible_features": string_list_sha256(eligible_features),
    }
    transform_digests["combined"] = digest_map_sha256(transform_digests)
    return TransformBundle(
        panel=panel,
        eligible_mask=_readonly(eligible),
        eligible_features=eligible_features,
        folds=folds,
        all_folio=AllFolioTransform(
            residuals=_readonly(all_residuals),
            standardized=_readonly(all_standardized),
            scales=_readonly(all_scales),
            digests=all_digests,
        ),
        digests=transform_digests,
    )


def load_anonymous(
    matrix_path: str | Path,
    inventory_path: str | Path,
    *,
    require_frozen_hashes: bool = True,
) -> AnonymousPanel:
    """Stable compact API alias for :func:`load_anonymous_panel`."""
    return load_anonymous_panel(
        matrix_path, inventory_path, require_frozen_hashes=require_frozen_hashes
    )


def transform(
    panel: AnonymousPanel,
    matrix: np.ndarray | None = None,
    *,
    require_exact_eligibility: bool = True,
) -> TransformBundle:
    """Stable compact API for one baseline or planted anonymous matrix."""
    return build_transforms(
        panel, matrix, require_exact_eligibility=require_exact_eligibility
    )


def validate_rotations(
    panel: AnonymousPanel,
    rotations: np.ndarray,
    *,
    ensemble: str,
    expected_assignments: int | None = None,
) -> str:
    """Validate a supplied canonical rotation matrix and return its digest."""
    if ensemble not in ENSEMBLE_IDS:
        raise ValueError(f"unknown rotation ensemble: {ensemble}")
    if not isinstance(rotations, np.ndarray):
        raise TypeError("rotations must be a NumPy array")
    if rotations.dtype.kind != "u" or rotations.dtype.itemsize != 2:
        raise ValueError("rotations must use unsigned 16-bit storage")
    if rotations.dtype.byteorder == ">" or (rotations.dtype.byteorder == "=" and sys.byteorder != "little"):
        raise ValueError("rotations must use little-endian storage")
    if not rotations.flags.c_contiguous:
        raise ValueError("rotations must be C-contiguous")
    if rotations.ndim != 2 or rotations.shape[1] != len(panel.page_names):
        raise ValueError("rotation shape must be assignments x 12 sorted pages")
    if expected_assignments is not None and rotations.shape[0] != expected_assignments:
        raise ValueError("unexpected assignment count")
    if rotations.shape[0] < 2 or np.any(rotations[0] != 0):
        raise ValueError("rotation assignment zero must be the all-zero identity")
    if np.unique(rotations, axis=0).shape[0] != rotations.shape[0]:
        raise ValueError("rotation rows must be unique")
    for page_index, page in enumerate(panel.page_names):
        if np.any(rotations[:, page_index] >= EXPECTED_PAGE_SIZES[page]):
            raise ValueError(f"out-of-range rotation for {page}")
    if ensemble == "COUPLED_FOLIO":
        page_index = {page: index for index, page in enumerate(panel.page_names)}
        for folio in panel.folio_names:
            folio_pages = tuple(page for page in panel.page_names if page[:-1] == folio)
            grid = math.lcm(*(EXPECTED_PAGE_SIZES[page] for page in folio_pages))
            allowed = {
                tuple((phase * EXPECTED_PAGE_SIZES[page]) // grid for page in folio_pages)
                for phase in range(grid)
            }
            for row in rotations:
                actual = tuple(int(row[page_index[page]]) for page in folio_pages)
                if actual not in allowed:
                    raise ValueError(f"invalid coupled-folio floor phase for {folio}: {actual}")
    return array_sha256(rotations, "<u2")


def _encode_targets(
    panel: AnonymousPanel,
    targets: Mapping[str, Sequence[str]],
    label_unit_ids: Sequence[str],
    *,
    validate_directed_counts: bool,
) -> tuple[np.ndarray, Mapping[str, TargetSupport]]:
    if tuple(label_unit_ids) != panel.unit_ids:
        raise ValueError("label unit order must exactly equal the anonymous panel order")
    if set(targets) != set(TARGET_IDS):
        raise ValueError(f"targets must be exactly {TARGET_IDS}")
    encoded = np.empty((2, 156), dtype=np.int8)
    code = {"X": 0, "L": 1, "H": 2}
    supports: dict[str, TargetSupport] = {}
    for target_index, target in enumerate(TARGET_IDS):
        states = tuple(targets[target])
        if len(states) != 156 or any(state not in code for state in states):
            raise ValueError(f"invalid state vector for {target}")
        encoded[target_index] = [code[state] for state in states]
        rule = TARGET_RULES[target]
        counts = tuple(states.count(state) for state in ("L", "H", "X"))
        if validate_directed_counts and counts != (rule.low, rule.high, rule.ignored):
            raise ValueError(f"directed state counts failed for {target}: {counts}")
        if not validate_directed_counts and sorted(counts[:2]) != sorted((rule.low, rule.high)):
            raise ValueError(f"complement state counts failed for {target}: {counts}")
        if counts[2] != rule.ignored:
            raise ValueError(f"ignored-state count failed for {target}")
        informative_pages: list[str] = []
        for page, positions in zip(panel.page_names, panel.page_positions):
            page_states = encoded[target_index, positions]
            if np.any(page_states == 1) and np.any(page_states == 2):
                informative_pages.append(page)
        informative_folios = tuple(sorted({page[:-1] for page in informative_pages}))
        if len(informative_pages) != rule.informative_pages or len(informative_folios) != rule.informative_folios:
            raise ValueError(f"informative page/folio support failed for {target}")
        if target == "TAIL_LIKE":
            ignored_pages = {
                panel.pages[position]
                for position in np.flatnonzero(encoded[target_index] == 0)
            }
            if any(page in informative_pages for page in ignored_pages):
                raise ValueError("TAIL_LIKE ignored state must lie on a noninformative page")
        pages_per_folio = {
            folio: sum(page[:-1] == folio for page in informative_pages)
            for folio in informative_folios
        }
        supports[target] = TargetSupport(
            target=target,
            informative_pages=tuple(informative_pages),
            informative_folios=informative_folios,
            pages_per_folio=pages_per_folio,
        )
    return encoded, supports


def _page_contrast_tables(
    panel: AnonymousPanel,
    encoded: np.ndarray,
) -> tuple[np.ndarray, ...]:
    """Build target x possible-shift x page-position contrast lookup tables."""
    tables: list[np.ndarray] = []
    for positions in panel.page_positions:
        page_length = len(positions)
        shifts = np.arange(page_length, dtype=np.int64)
        source = (
            np.arange(page_length, dtype=np.int64)[None, :]
            - shifts[:, None]
        ) % page_length
        table = np.zeros((2, page_length, page_length), dtype=np.float64)
        for target_index in range(2):
            rotated = encoded[target_index, positions][source]
            low_count = np.sum(rotated == 1, axis=1)
            high_count = np.sum(rotated == 2, axis=1)
            local = np.zeros_like(rotated, dtype=np.float64)
            informative = (low_count > 0) & (high_count > 0)
            if np.any(informative):
                local[informative] = (
                    (rotated[informative] == 2) / high_count[informative, None]
                    - (rotated[informative] == 1) / low_count[informative, None]
                )
            table[target_index] = local
        tables.append(_readonly(table))
    return tuple(tables)


def _identity_directions(
    bundle: TransformBundle,
    contrast_tables: tuple[np.ndarray, ...],
    supports: Mapping[str, TargetSupport],
) -> Mapping[str, np.ndarray]:
    panel = bundle.panel
    page_index = {page: index for index, page in enumerate(panel.page_names)}
    answer: dict[str, np.ndarray] = {}
    for target_index, target in enumerate(TARGET_IDS):
        support = supports[target]
        directions = np.empty((3, len(bundle.eligible_features)), dtype=np.float64)
        for edition_index in range(3):
            standardized = bundle.all_folio.standardized[edition_index]
            folio_vectors: list[np.ndarray] = []
            for folio in support.informative_folios:
                pages = [page for page in support.informative_pages if page[:-1] == folio]
                page_vectors = []
                for page in pages:
                    index = page_index[page]
                    positions = panel.page_positions[index]
                    page_vectors.append(
                        contrast_tables[index][target_index, 0] @ standardized[positions]
                    )
                folio_vectors.append(np.mean(page_vectors, axis=0))
            directions[edition_index] = np.mean(folio_vectors, axis=0)
        answer[target] = _readonly(directions)
    return answer


def _orientation_cosines(
    directions_by_target: Mapping[str, np.ndarray],
) -> tuple[Mapping[str, Mapping[str, float]], Mapping[str, str]]:
    cosines: dict[str, Mapping[str, float]] = {}
    direction_digests: dict[str, str] = {}
    pairs = ((0, 1), (0, 2), (1, 2))
    for target in TARGET_IDS:
        directions = directions_by_target[target]
        for edition_index, edition in enumerate(EDITIONS):
            direction_digests[f"{target}__{edition}"] = array_sha256(directions[edition_index])
        target_cosines: dict[str, float] = {}
        for left, right in pairs:
            denominator = float(np.linalg.norm(directions[left]) * np.linalg.norm(directions[right]))
            value = float(np.dot(directions[left], directions[right]) / denominator) if denominator > NUM_TOL else math.nan
            target_cosines[f"{EDITIONS[left]}__{EDITIONS[right]}"] = value
        cosines[target] = target_cosines
    return cosines, direction_digests


def score_rotations(
    bundle: TransformBundle,
    targets: Mapping[str, Sequence[str]],
    rotations: np.ndarray,
    *,
    ensemble: str,
    label_unit_ids: Sequence[str],
    expected_assignments: int | None = None,
    validate_directed_counts: bool = True,
) -> EnsembleScore:
    """Score both supplied target sequences under one supplied phase ensemble."""
    panel = bundle.panel
    rotation_digest = validate_rotations(
        panel, rotations, ensemble=ensemble, expected_assignments=expected_assignments
    )
    encoded, supports = _encode_targets(
        panel, targets, label_unit_ids, validate_directed_counts=validate_directed_counts
    )
    contrast_tables = _page_contrast_tables(panel, encoded)
    n_assignments = rotations.shape[0]
    p = len(bundle.eligible_features)
    if p != 83:
        raise ValueError("SME003 scorer requires the exact 83-feature coordinate")
    folio_index = {folio: index for index, folio in enumerate(panel.folio_names)}
    T = np.empty((2, 3, n_assignments), dtype=np.float64)
    contributions = np.full((2, 3, n_assignments, 7), np.nan, dtype=np.float64)
    deletion_T = np.full((2, 3, n_assignments, 7), np.nan, dtype=np.float64)
    training_direction_digests: dict[str, str] = {}
    page_index = {page: index for index, page in enumerate(panel.page_names)}
    page_delta_cache: dict[tuple[str, int], tuple[np.ndarray, ...]] = {}
    for held_folio in panel.folio_names:
        fold = bundle.folds[held_folio]
        for edition_index in range(3):
            standardized = fold.standardized[edition_index]
            page_delta_cache[(held_folio, edition_index)] = tuple(
                contrast_tables[index] @ standardized[positions]
                for index, positions in enumerate(panel.page_positions)
            )

    for target_index, target in enumerate(TARGET_IDS):
        support = supports[target]
        informative = support.informative_folios
        k_folios = len(informative)
        deletion_sums = np.zeros((3, n_assignments, k_folios), dtype=np.float64)
        for held_index, held_folio in enumerate(informative):
            fold = bundle.folds[held_folio]
            for edition_index, edition in enumerate(panel.editions):
                page_delta_tables = page_delta_cache[(held_folio, edition_index)]
                deltas = np.empty((n_assignments, k_folios, p), dtype=np.float64)
                for source_index, source_folio in enumerate(informative):
                    source_pages = [
                        page for page in support.informative_pages if page[:-1] == source_folio
                    ]
                    source_delta = np.zeros((n_assignments, p), dtype=np.float64)
                    for page in source_pages:
                        index = page_index[page]
                        source_delta += page_delta_tables[index][
                            target_index, rotations[:, index].astype(np.int64), :
                        ]
                    deltas[:, source_index, :] = source_delta / len(source_pages)
                total_direction = np.sum(deltas, axis=1)
                held_vector = deltas[:, held_index, :]
                training_direction = (total_direction - held_vector) / (k_folios - 1)
                training_direction_digests[
                    f"{target}__{held_folio}__{edition}"
                ] = array_sha256(training_direction)
                weight = fold.weights[edition_index]
                held_weighted = held_vector @ weight
                held_contribution = np.sum(
                    held_weighted * training_direction, axis=1
                ) / p
                contributions[
                    target_index, edition_index, :, folio_index[held_folio]
                ] = held_contribution
                for deleted_index in range(k_folios):
                    if deleted_index == held_index:
                        continue
                    reduced_direction = (
                        total_direction - held_vector - deltas[:, deleted_index, :]
                    ) / (k_folios - 2)
                    deletion_sums[edition_index, :, deleted_index] += np.sum(
                        held_weighted * reduced_direction, axis=1
                    ) / p
        for edition_index in range(3):
            target_contributions = contributions[target_index, edition_index][
                :, [folio_index[folio] for folio in informative]
            ]
            T[target_index, edition_index] = np.mean(target_contributions, axis=1)
            for deleted_index, deleted_folio in enumerate(informative):
                deletion_T[
                    target_index, edition_index, :, folio_index[deleted_folio]
                ] = deletion_sums[edition_index, :, deleted_index] / (k_folios - 1)

    if not np.isfinite(T).all():
        raise ValueError("nonfinite cross-folio T")
    means = np.mean(T, axis=2, keepdims=True)
    standard_deviations = np.std(T, axis=2, ddof=0, keepdims=True)
    if not np.isfinite(standard_deviations).all() or np.any(standard_deviations <= NUM_TOL):
        raise ValueError("zero or nonfinite assignment population SD")
    z = (T - means) / standard_deviations
    robust_R = np.min(z, axis=1)
    family_M = np.max(robust_R, axis=0)
    family_p = {
        target: float((1 + np.count_nonzero(
            family_M[1:] >= robust_R[target_index, 0] - TAIL_TIE_TOL
        )) / n_assignments)
        for target_index, target in enumerate(TARGET_IDS)
    }
    raw_T = T[:, :, 0]
    raw_A = np.sign(raw_T) * np.sqrt(np.abs(raw_T))
    directions_by_target = _identity_directions(bundle, contrast_tables, supports)
    orientation_cosines, orientation_digests = _orientation_cosines(directions_by_target)

    common_positive: dict[str, tuple[str, ...]] = {}
    gates: dict[str, Mapping[str, bool]] = {}
    target_pass: dict[str, bool] = {}
    for target_index, target in enumerate(TARGET_IDS):
        support = supports[target]
        common = tuple(
            folio for folio in support.informative_folios
            if np.all(contributions[target_index, :, 0, folio_index[folio]] > NUM_TOL)
        )
        common_positive[target] = common
        deletion_identity = np.asarray([
            deletion_T[target_index, :, 0, folio_index[folio]]
            for folio in support.informative_folios
        ])
        target_gates = {
            "family_p_at_most_0_05": family_p[target] <= 0.05,
            "every_reading_raw_T_positive": bool(np.all(raw_T[target_index] > NUM_TOL)),
            "weakest_reading_material_at_least_0_05": bool(
                np.min(raw_A[target_index]) >= MATERIAL_THRESHOLD - NUM_TOL
            ),
            "all_orientation_cosines_finite": bool(all(
                np.isfinite(value) for value in orientation_cosines[target].values()
            )),
            "all_orientation_cosines_at_least_0_10": bool(all(
                value >= ORIENTATION_THRESHOLD - NUM_TOL
                for value in orientation_cosines[target].values()
            )),
            "common_positive_folio_support": len(common) >= TARGET_RULES[target].common_support,
            "every_conditional_deletion_positive": bool(np.all(deletion_identity > NUM_TOL)),
        }
        gates[target] = target_gates
        target_pass[target] = all(target_gates.values())

    digests: dict[str, str | Mapping[str, str]] = {
        "rotations": rotation_digest,
        "T": array_sha256(T),
        "z": array_sha256(z),
        "robust_R": array_sha256(robust_R),
        "family_M": array_sha256(family_M),
        "contributions": array_sha256(np.nan_to_num(contributions, nan=np.inf)),
        "deletion_T": array_sha256(np.nan_to_num(deletion_T, nan=np.inf)),
        "raw_T": array_sha256(raw_T),
        "raw_A": array_sha256(raw_A),
        "training_directions": training_direction_digests,
        "orientation_vectors": orientation_digests,
    }
    scalar_digests = {key: value for key, value in digests.items() if isinstance(value, str)}
    nested_digests = {
        key: digest_map_sha256(value)
        for key, value in digests.items()
        if isinstance(value, Mapping)
    }
    digests["combined"] = digest_map_sha256({**scalar_digests, **nested_digests})
    return EnsembleScore(
        ensemble=ensemble,
        target_ids=TARGET_IDS,
        T=_readonly(T),
        z=_readonly(z),
        robust_R=_readonly(robust_R),
        family_M=_readonly(family_M),
        contributions=_readonly(contributions),
        deletion_T=_readonly(deletion_T),
        raw_T=_readonly(raw_T),
        raw_A=_readonly(raw_A),
        family_p=family_p,
        orientation_cosines=orientation_cosines,
        common_positive_folios=common_positive,
        gates=gates,
        target_pass=target_pass,
        supports=supports,
        digests=digests,
    )


def score_dual_ensembles(
    bundle: TransformBundle,
    targets: Mapping[str, Sequence[str]],
    rotations: Mapping[str, np.ndarray],
    *,
    label_unit_ids: Sequence[str],
    expected_assignments: int | None = None,
    validate_directed_counts: bool = True,
) -> DualEnsembleScore:
    """Apply the complete dual-phase decision to the same two target vectors."""
    if set(rotations) != set(ENSEMBLE_IDS):
        raise ValueError(f"rotation ensembles must be exactly {ENSEMBLE_IDS}")
    scores = {
        ensemble: score_rotations(
            bundle,
            targets,
            rotations[ensemble],
            ensemble=ensemble,
            label_unit_ids=label_unit_ids,
            expected_assignments=expected_assignments,
            validate_directed_counts=validate_directed_counts,
        )
        for ensemble in ENSEMBLE_IDS
    }
    target_pass = {
        target: all(scores[ensemble].target_pass[target] for ensemble in ENSEMBLE_IDS)
        for target in TARGET_IDS
    }
    gates = {
        "both_phase_ensembles_present": set(scores) == set(ENSEMBLE_IDS),
        "all_scores_finite": all(np.isfinite(score.T).all() for score in scores.values()),
        "full_two_target_family": all(score.target_ids == TARGET_IDS for score in scores.values()),
    }
    digest_parts = {
        ensemble: str(scores[ensemble].digests["combined"])
        for ensemble in ENSEMBLE_IDS
    }
    return DualEnsembleScore(
        ensembles=scores,
        target_pass=target_pass,
        any_target_pass=any(target_pass.values()),
        gates=gates,
        digests={**digest_parts, "combined": digest_map_sha256(digest_parts)},
    )


def score_world(
    transforms: TransformBundle,
    paired_labels: PairedLabels,
    rotations_by_ensemble: Mapping[str, np.ndarray],
    *,
    expected_assignments: int | None = 8192,
    validate_directed_counts: bool = True,
) -> DualEnsembleScore:
    """Stable compact API for a complete two-target, dual-ensemble world."""
    return score_dual_ensembles(
        transforms,
        paired_labels.targets,
        rotations_by_ensemble,
        label_unit_ids=paired_labels.unit_ids,
        expected_assignments=expected_assignments,
        validate_directed_counts=validate_directed_counts,
    )


def realized_driver_rms(
    transforms: TransformBundle,
    paired_labels: PairedLabels,
    driver_features: Mapping[str, Sequence[str]],
    *,
    validate_directed_counts: bool = True,
) -> Mapping[str, Mapping[str, Mapping[str, float | None]]]:
    """Per-reading population RMS of all-folio identity D inside/outside drivers.

    This is a diagnostic only.  It performs no across-reading aggregation and
    returns ``None`` outside a dense 83-feature driver.
    """
    panel = transforms.panel
    encoded, supports = _encode_targets(
        panel,
        paired_labels.targets,
        paired_labels.unit_ids,
        validate_directed_counts=validate_directed_counts,
    )
    if set(driver_features) != set(TARGET_IDS):
        raise ValueError(f"driver feature map must contain exactly {TARGET_IDS}")
    contrast_tables = _page_contrast_tables(panel, encoded)
    directions = _identity_directions(transforms, contrast_tables, supports)
    feature_index = {feature: index for index, feature in enumerate(transforms.eligible_features)}
    result: dict[str, Mapping[str, Mapping[str, float | None]]] = {}
    for target in TARGET_IDS:
        selected_names = tuple(driver_features[target])
        if not selected_names or len(set(selected_names)) != len(selected_names):
            raise ValueError(f"driver must be nonempty without duplicates for {target}")
        try:
            selected = np.asarray([feature_index[name] for name in selected_names], dtype=np.int64)
        except KeyError as error:
            raise ValueError(f"driver includes an ineligible/unknown feature: {error.args[0]}") from error
        outside = np.asarray(
            [index for index in range(83) if index not in set(selected.tolist())], dtype=np.int64
        )
        editions: dict[str, Mapping[str, float | None]] = {}
        for edition_index, edition in enumerate(EDITIONS):
            vector = directions[target][edition_index]
            editions[edition] = {
                "inside": float(np.sqrt(np.mean(vector[selected] ** 2))),
                "outside": (
                    float(np.sqrt(np.mean(vector[outside] ** 2))) if len(outside) else None
                ),
            }
        result[target] = editions
    return result


def compare_transform_invariance(
    reference: TransformBundle,
    candidate: TransformBundle,
) -> Mapping[str, object]:
    """Return exhaustive raw-residual/scale/standardized/weight differences."""
    if reference.panel.unit_ids != candidate.panel.unit_ids:
        raise ValueError("cannot compare transforms with different unit order")
    if reference.eligible_features != candidate.eligible_features:
        raise ValueError("cannot compare transforms with different eligibility")
    folds: dict[str, Mapping[str, Mapping[str, float | bool]]] = {}
    for folio in reference.panel.folio_names:
        left = reference.folds[folio]
        right = candidate.folds[folio]
        editions: dict[str, Mapping[str, float | bool]] = {}
        for edition_index, edition in enumerate(EDITIONS):
            residual_max = float(np.max(np.abs(
                left.residuals[:, edition_index, :] - right.residuals[:, edition_index, :]
            )))
            editions[edition] = {
                "residual_max_abs": residual_max,
                "scale_max_abs": float(np.max(np.abs(
                    left.scales[edition_index] - right.scales[edition_index]
                ))),
                "standardized_max_abs": float(np.max(np.abs(
                    left.standardized[edition_index] - right.standardized[edition_index]
                ))),
                "weight_max_abs": float(np.max(np.abs(
                    left.weights[edition_index] - right.weights[edition_index]
                ))),
                "residual_digest_equal": (
                    left.digests[f"residual__{edition}"] == right.digests[f"residual__{edition}"]
                ),
            }
        folds[folio] = editions
    all_folio = {
        edition: {
            "residual_max_abs": float(np.max(np.abs(
                reference.all_folio.residuals[:, edition_index, :]
                - candidate.all_folio.residuals[:, edition_index, :]
            ))),
            "standardized_max_abs": float(np.max(np.abs(
                reference.all_folio.standardized[edition_index]
                - candidate.all_folio.standardized[edition_index]
            ))),
            "residual_digest_equal": (
                reference.all_folio.digests[f"residual__{edition}"]
                == candidate.all_folio.digests[f"residual__{edition}"]
            ),
        }
        for edition_index, edition in enumerate(EDITIONS)
    }
    return {
        "folds": folds,
        "all_folio": all_folio,
        "combined_digest_equal": reference.digests["combined"] == candidate.digests["combined"],
    }


def compare_score_invariance(
    reference: EnsembleScore,
    candidate: EnsembleScore,
) -> Mapping[str, object]:
    """Compare every assignment-level aggregate and all decision gates."""
    if reference.ensemble != candidate.ensemble or reference.target_ids != candidate.target_ids:
        raise ValueError("cannot compare scores from different ensemble/family definitions")
    arrays = {
        "T": (reference.T, candidate.T),
        "z": (reference.z, candidate.z),
        "robust_R": (reference.robust_R, candidate.robust_R),
        "family_M": (reference.family_M, candidate.family_M),
        "contributions": (reference.contributions, candidate.contributions),
        "deletion_T": (reference.deletion_T, candidate.deletion_T),
        "raw_T": (reference.raw_T, candidate.raw_T),
        "raw_A": (reference.raw_A, candidate.raw_A),
    }
    maxima: dict[str, float] = {}
    for name, (left, right) in arrays.items():
        if left.shape != right.shape or not np.array_equal(np.isnan(left), np.isnan(right)):
            raise ValueError(f"score array shape/defined-mask drift: {name}")
        finite = np.isfinite(left) & np.isfinite(right)
        maxima[name] = float(np.max(np.abs(left[finite] - right[finite]))) if np.any(finite) else 0.0
    return {
        "max_abs": maxima,
        "family_p_equal": reference.family_p == candidate.family_p,
        "orientation_cosines_equal": reference.orientation_cosines == candidate.orientation_cosines,
        "common_positive_folios_equal": (
            reference.common_positive_folios == candidate.common_positive_folios
        ),
        "gates_equal": reference.gates == candidate.gates,
        "target_pass_equal": reference.target_pass == candidate.target_pass,
        "combined_digest_equal": reference.digests["combined"] == candidate.digests["combined"],
    }


def compact_score_summary(score: EnsembleScore) -> Mapping[str, object]:
    """Return only aggregate, non-feature-level quantities safe for artifacts."""
    return {
        "ensemble": score.ensemble,
        "target_ids": list(score.target_ids),
        "assignments": int(score.T.shape[2]),
        "family_p": dict(score.family_p),
        "raw_T": {
            target: {
                edition: float(score.raw_T[target_index, edition_index])
                for edition_index, edition in enumerate(EDITIONS)
            }
            for target_index, target in enumerate(TARGET_IDS)
        },
        "raw_A": {
            target: {
                edition: float(score.raw_A[target_index, edition_index])
                for edition_index, edition in enumerate(EDITIONS)
            }
            for target_index, target in enumerate(TARGET_IDS)
        },
        "orientation_cosines": score.orientation_cosines,
        "common_positive_folios": {
            target: list(folios) for target, folios in score.common_positive_folios.items()
        },
        "gates": score.gates,
        "target_pass": score.target_pass,
        "digests": score.digests,
        "claim_ceiling": "anonymous synthetic calibration statistic only; no feature meaning or morphology association",
    }


def _self_test() -> None:
    # Numeric OAS definition and canonical digest behavior, without file access.
    training = np.asarray([[1.0, -1.0], [-1.0, 1.0], [0.5, 0.25]], dtype=np.float64)
    weight, diagnostics = analytic_oas(training)
    assert weight.shape == (2, 2)
    assert np.isfinite(weight).all()
    assert abs(float(np.trace(weight)) - 2.0) <= 1e-12
    assert diagnostics["rho"] >= 0.0 and diagnostics["rho"] <= 1.0
    assert array_sha256(np.asarray([1.0], dtype=np.float64)) == array_sha256(
        np.asarray([1.0], dtype=np.dtype("<f8"))
    )
    print("PASS_SME003_CORE_SELF_TEST")


if __name__ == "__main__":
    _self_test()
