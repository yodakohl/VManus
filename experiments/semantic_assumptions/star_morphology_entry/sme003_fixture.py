#!/usr/bin/env python3
"""Target-free deterministic fixtures for SME003 synthetic calibration.

This module deliberately performs no file I/O.  Callers provide the frozen
anonymous unit metadata and, for projection helpers, already residualized and
RMS-standardized anonymous matrices.  Morphology labels and target artifacts
are outside this module's interface.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import math
from typing import Mapping, Sequence

import numpy as np


RAY_LIKE = "RAY_LIKE"
TAIL_LIKE = "TAIL_LIKE"
TARGETS = (RAY_LIKE, TAIL_LIKE)

LOW = "L"
HIGH = "H"
IGNORED = "X"
STATES = (LOW, HIGH, IGNORED)

EDITIONS = ("ZL3b", "IT2a", "RF1b")

DENSE_83_DRIVER = "DENSE_83_DRIVER"
BALANCED_24_DRIVER = "BALANCED_24_DRIVER"
DRIVERS = (DENSE_83_DRIVER, BALANCED_24_DRIVER)

INDEPENDENT_PAGE = "INDEPENDENT_PAGE"
COUPLED_FOLIO = "COUPLED_FOLIO"
ENSEMBLES = (INDEPENDENT_PAGE, COUPLED_FOLIO)

WORLD_IDS = tuple(range(64))
POWER_WORLD_IDS = tuple(range(8))
CALIBRATION_ASSIGNMENTS = 8_192
PRODUCTION_ASSIGNMENTS = 65_536

PAGE_SIZES = {
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
PAGE_ORDER = tuple(sorted(PAGE_SIZES))
FOLIO_ORDER = tuple(sorted({page[:-1] for page in PAGE_ORDER}))
FOLIO_PAGES = {
    folio: tuple(page for page in PAGE_ORDER if page[:-1] == folio)
    for folio in FOLIO_ORDER
}

EXPECTED_COUNTS = {
    RAY_LIKE: {LOW: 66, HIGH: 83, IGNORED: 7},
    TAIL_LIKE: {LOW: 133, HIGH: 22, IGNORED: 1},
}
EXPECTED_INFORMATIVE_PAGES = {RAY_LIKE: 12, TAIL_LIKE: 8}
EXPECTED_INFORMATIVE_FOLIOS = {RAY_LIKE: 7, TAIL_LIKE: 6}


class FixtureError(RuntimeError):
    """Raised when a frozen SME003 fixture contract is violated."""


@dataclass(frozen=True, order=True)
class Unit:
    """Anonymous unit metadata needed by label and row-permutation fixtures."""

    page: str
    ordinal: int
    unit_id: str
    physical_folio: str


@dataclass(frozen=True)
class PairedLabelWorld:
    """One paired ray-like/tail-like synthetic label world."""

    world_id: int
    ray_labels: tuple[str, ...]
    tail_labels: tuple[str, ...]
    paired_sha256: str

    def labels(self, target: str) -> tuple[str, ...]:
        if target == RAY_LIKE:
            return self.ray_labels
        if target == TAIL_LIKE:
            return self.tail_labels
        raise FixtureError(f"unknown target: {target}")


@dataclass(frozen=True)
class LabelPanel:
    """Canonical unit order and all 64 paired label worlds."""

    units: tuple[Unit, ...]
    worlds: tuple[PairedLabelWorld, ...]

    def world(self, world_id: int) -> PairedLabelWorld:
        if not 0 <= world_id < len(self.worlds):
            raise FixtureError(f"world ID out of range: {world_id}")
        answer = self.worlds[world_id]
        if answer.world_id != world_id:
            raise FixtureError("world panel is not in canonical ID order")
        return answer


@dataclass(frozen=True)
class RotationFixture:
    """One canonical rotation matrix and its raw-byte digest."""

    ensemble: str
    page_order: tuple[str, ...]
    shifts: np.ndarray
    sha256: str
    row_attempts: tuple[int, ...]
    max_row_attempt: int


@dataclass(frozen=True)
class DriverFixture:
    """Frozen selected feature order and Rademacher signs for one driver."""

    world_id: int
    target: str
    driver: str
    features: tuple[str, ...]
    signs: tuple[int, ...]


@dataclass(frozen=True)
class BeneficialSwap:
    """One disjoint donor-row exchange between a low and high destination."""

    page: str
    low_index: int
    high_index: int
    low_unit_id: str
    high_unit_id: str
    low_projection: float
    high_projection: float
    gain: float


@dataclass(frozen=True)
class PageSwapPlan:
    """Complete and strength-truncated beneficial swaps for one page."""

    page: str
    informative: bool
    complete_swaps: tuple[BeneficialSwap, ...]
    applied_count: int

    @property
    def applied_swaps(self) -> tuple[BeneficialSwap, ...]:
        return self.complete_swaps[: self.applied_count]


@dataclass(frozen=True)
class SwapPlan:
    """A deterministic whole-row power plan in canonical unit order."""

    target: str
    strength: float
    unit_ids: tuple[str, ...]
    pages: tuple[PageSwapPlan, ...]

    @property
    def complete_swap_count(self) -> int:
        return sum(len(page.complete_swaps) for page in self.pages)

    @property
    def applied_swap_count(self) -> int:
        return sum(page.applied_count for page in self.pages)

    @property
    def applied_fraction(self) -> float:
        total = self.complete_swap_count
        return 0.0 if total == 0 else self.applied_swap_count / total

    @property
    def applied_swaps(self) -> tuple[BeneficialSwap, ...]:
        return tuple(swap for page in self.pages for swap in page.applied_swaps)


def _ascii(value: object, description: str) -> str:
    text = str(value)
    try:
        text.encode("ascii")
    except UnicodeEncodeError as error:
        raise FixtureError(f"{description} must be ASCII: {text!r}") from error
    if "\n" in text or "\r" in text:
        raise FixtureError(f"{description} may not contain a newline: {text!r}")
    return text


def _validate_world_id(world_id: int) -> None:
    if isinstance(world_id, bool) or not isinstance(world_id, int) or world_id not in WORLD_IDS:
        raise FixtureError(f"world ID must be an integer in 0..63: {world_id!r}")


def rank_digest(world_id: int, domain: str, item: str) -> bytes:
    """Return the exact frozen SHA-256 rank digest."""

    _validate_world_id(world_id)
    domain_text = _ascii(domain, "rank domain")
    item_text = _ascii(item, "rank item")
    payload = f"SME003_SYNTH_V1|{world_id}|{domain_text}|{item_text}".encode("ascii")
    return hashlib.sha256(payload).digest()


def rank_key(world_id: int, domain: str, item: str) -> tuple[bytes, str]:
    """Digest rank with the literal item as the frozen tie-break."""

    item_text = _ascii(item, "rank item")
    return rank_digest(world_id, domain, item_text), item_text


def _canonical_units(units: Sequence[Unit]) -> tuple[Unit, ...]:
    answer = tuple(units)
    if len(answer) != sum(PAGE_SIZES.values()):
        raise FixtureError(f"expected 156 units, found {len(answer)}")
    if any(not isinstance(unit, Unit) for unit in answer):
        raise FixtureError("all unit metadata entries must be Unit instances")
    page_index = {page: index for index, page in enumerate(PAGE_ORDER)}
    try:
        answer = tuple(sorted(answer, key=lambda unit: (page_index[unit.page], unit.ordinal)))
    except KeyError as error:
        raise FixtureError(f"unexpected page: {error.args[0]}") from error

    unit_ids: set[str] = set()
    for unit in answer:
        _ascii(unit.unit_id, "unit ID")
        if unit.unit_id in unit_ids:
            raise FixtureError(f"duplicate unit ID: {unit.unit_id}")
        unit_ids.add(unit.unit_id)
        if unit.physical_folio != unit.page[:-1]:
            raise FixtureError(f"page/folio mismatch for {unit.unit_id}")

    for page in PAGE_ORDER:
        page_units = [unit for unit in answer if unit.page == page]
        if len(page_units) != PAGE_SIZES[page]:
            raise FixtureError(f"page size mismatch on {page}")
        if [unit.ordinal for unit in page_units] != list(range(1, PAGE_SIZES[page] + 1)):
            raise FixtureError(f"ordinal contract mismatch on {page}")
    return answer


def _indices_by_page(units: Sequence[Unit]) -> dict[str, tuple[int, ...]]:
    return {
        page: tuple(index for index, unit in enumerate(units) if unit.page == page)
        for page in PAGE_ORDER
    }


def _rank_indices(
    world_id: int,
    domain: str,
    indices: Sequence[int],
    units: Sequence[Unit],
) -> list[int]:
    return sorted(indices, key=lambda index: rank_key(world_id, domain, units[index].unit_id))


def _generate_ray_labels(world_id: int, units: tuple[Unit, ...]) -> tuple[str, ...]:
    page_indices = _indices_by_page(units)
    protected_low: set[int] = set()
    protected_high: set[int] = set()
    for page in PAGE_ORDER:
        indices = page_indices[page]
        low = _rank_indices(world_id, f"RAY_LOW_ANCHOR|{page}", indices, units)[0]
        high_candidates = tuple(index for index in indices if index != low)
        high = _rank_indices(world_id, f"RAY_HIGH_ANCHOR|{page}", high_candidates, units)[0]
        protected_low.add(low)
        protected_high.add(high)

    unprotected = tuple(
        index for index in range(len(units))
        if index not in protected_low and index not in protected_high
    )
    thirds = set(_rank_indices(world_id, "RAY_THIRD", unprotected, units)[:7])
    remaining_candidates = tuple(
        index for index in range(len(units))
        if index not in protected_low
        and index not in protected_high
        and index not in thirds
    )
    remaining_needed = EXPECTED_COUNTS[RAY_LIKE][HIGH] - len(protected_high)
    remaining_high = set(
        _rank_indices(world_id, "RAY_REMAINING_HIGH", remaining_candidates, units)[
            :remaining_needed
        ]
    )

    labels = [LOW] * len(units)
    for index in protected_high | remaining_high:
        labels[index] = HIGH
    for index in thirds:
        labels[index] = IGNORED
    return tuple(labels)


def _generate_tail_labels(world_id: int, units: tuple[Unit, ...]) -> tuple[str, ...]:
    page_indices = _indices_by_page(units)
    omitted_folio = min(
        FOLIO_ORDER,
        key=lambda folio: rank_key(world_id, "TAIL_OMIT_FOLIO", folio),
    )
    remaining_folios = tuple(folio for folio in FOLIO_ORDER if folio != omitted_folio)

    selected_pages: set[str] = set()
    for folio in remaining_folios:
        selected_pages.add(
            min(
                FOLIO_PAGES[folio],
                key=lambda page: rank_key(
                    world_id, f"TAIL_PRIMARY_PAGE|{folio}", page
                ),
            )
        )
    extra_candidates = tuple(
        page for folio in remaining_folios for page in FOLIO_PAGES[folio]
        if page not in selected_pages
    )
    extras = sorted(
        extra_candidates,
        key=lambda page: rank_key(world_id, "TAIL_EXTRA_PAGE", page),
    )[:2]
    selected_pages.update(extras)
    if len(selected_pages) != 8:
        raise FixtureError("tail generation did not select exactly eight pages")

    noninformative_indices = tuple(
        index for index, unit in enumerate(units) if unit.page not in selected_pages
    )
    third = _rank_indices(world_id, "TAIL_THIRD", noninformative_indices, units)[0]

    protected_high: set[int] = set()
    protected_low: set[int] = set()
    for page in sorted(selected_pages):
        candidates = tuple(index for index in page_indices[page] if index != third)
        high = _rank_indices(world_id, f"TAIL_HIGH_ANCHOR|{page}", candidates, units)[0]
        low_candidates = tuple(index for index in candidates if index != high)
        low = _rank_indices(world_id, f"TAIL_LOW_ANCHOR|{page}", low_candidates, units)[0]
        protected_high.add(high)
        protected_low.add(low)

    remaining_candidates = tuple(
        index for page in sorted(selected_pages) for index in page_indices[page]
        if index not in protected_high
        and index not in protected_low
        and index != third
    )
    remaining_needed = EXPECTED_COUNTS[TAIL_LIKE][HIGH] - len(protected_high)
    remaining_high = set(
        _rank_indices(world_id, "TAIL_REMAINING_HIGH", remaining_candidates, units)[
            :remaining_needed
        ]
    )

    labels = [LOW] * len(units)
    for index in protected_high | remaining_high:
        labels[index] = HIGH
    for index in protected_low:
        labels[index] = LOW
    labels[third] = IGNORED
    return tuple(labels)


def informative_pages(units: Sequence[Unit], labels: Sequence[str]) -> tuple[str, ...]:
    """Pages containing at least one directed low and one directed high."""

    if len(units) != len(labels):
        raise FixtureError("unit/label length mismatch")
    answer = []
    for page in PAGE_ORDER:
        states = {
            labels[index] for index, unit in enumerate(units) if unit.page == page
        }
        if LOW in states and HIGH in states:
            answer.append(page)
    return tuple(answer)


def _validate_target_labels(
    units: tuple[Unit, ...], labels: tuple[str, ...], target: str
) -> None:
    if target not in TARGETS:
        raise FixtureError(f"unknown target: {target}")
    if len(labels) != len(units) or any(state not in STATES for state in labels):
        raise FixtureError(f"invalid {target} label vector")
    counts = {state: labels.count(state) for state in STATES}
    if counts != EXPECTED_COUNTS[target]:
        raise FixtureError(f"{target} state-count mismatch: {counts}")
    pages = informative_pages(units, labels)
    folios = {page[:-1] for page in pages}
    if len(pages) != EXPECTED_INFORMATIVE_PAGES[target]:
        raise FixtureError(f"{target} informative-page mismatch")
    if len(folios) != EXPECTED_INFORMATIVE_FOLIOS[target]:
        raise FixtureError(f"{target} informative-folio mismatch")


def paired_label_bytes(
    world_id: int,
    units: Sequence[Unit],
    ray_labels: Sequence[str],
    tail_labels: Sequence[str],
) -> bytes:
    """Canonical ASCII bytes used for a paired-world SHA-256 digest."""

    rows: list[str] = []
    label_sets = {RAY_LIKE: tuple(ray_labels), TAIL_LIKE: tuple(tail_labels)}
    for target in TARGETS:
        labels = label_sets[target]
        if len(labels) != len(units):
            raise FixtureError("unit/label length mismatch while hashing")
        for unit, state in zip(units, labels):
            rows.append(f"{world_id},{target},{unit.page},{unit.ordinal},{state}\n")
    return "".join(rows).encode("ascii")


def generate_label_panel(units: Sequence[Unit]) -> LabelPanel:
    """Build and validate all 64 exact paired synthetic label worlds."""

    canonical = _canonical_units(units)
    worlds: list[PairedLabelWorld] = []
    seen_pairs: set[tuple[tuple[str, ...], tuple[str, ...]]] = set()
    seen_digests: set[str] = set()
    for world_id in WORLD_IDS:
        ray = _generate_ray_labels(world_id, canonical)
        tail = _generate_tail_labels(world_id, canonical)
        _validate_target_labels(canonical, ray, RAY_LIKE)
        _validate_target_labels(canonical, tail, TAIL_LIKE)
        pair = (ray, tail)
        if pair in seen_pairs:
            raise FixtureError(f"duplicate paired synthetic world: {world_id}")
        seen_pairs.add(pair)
        digest = hashlib.sha256(
            paired_label_bytes(world_id, canonical, ray, tail)
        ).hexdigest()
        if digest in seen_digests:
            raise FixtureError(f"paired-label digest collision: {world_id}")
        seen_digests.add(digest)
        worlds.append(PairedLabelWorld(world_id, ray, tail, digest))
    return LabelPanel(canonical, tuple(worlds))


def _unbiased_rotation_value(
    ensemble: str,
    assignment: int,
    key: str,
    modulus: int,
    row_attempt: int,
) -> int:
    if modulus < 1:
        raise FixtureError("rotation modulus must be positive")
    limit = (1 << 64) - ((1 << 64) % modulus)
    counter = 0
    while True:
        if row_attempt == 0:
            text = f"SME003_ROT_V1|{ensemble}|{assignment}|{key}|{counter}"
        else:
            text = (
                f"SME003_ROT_V1|{ensemble}|{assignment}|"
                f"ROW_RETRY:{row_attempt}|{key}|{counter}"
            )
        value = int.from_bytes(hashlib.sha256(text.encode("ascii")).digest()[:8], "big")
        if value < limit:
            return value % modulus
        counter += 1


def build_rotation_fixture(ensemble: str, n_assignments: int) -> RotationFixture:
    """Build one exact unique rotation matrix and its canonical digest."""

    if ensemble not in ENSEMBLES:
        raise FixtureError(f"unknown rotation ensemble: {ensemble}")
    if isinstance(n_assignments, bool) or not isinstance(n_assignments, int) or n_assignments < 1:
        raise FixtureError("assignment count must be a positive integer")
    shifts = np.zeros((n_assignments, len(PAGE_ORDER)), dtype=np.dtype("<u2"), order="C")
    seen = {shifts[0].tobytes()}
    row_attempts = [0] * n_assignments
    for assignment in range(1, n_assignments):
        for row_attempt in range(65_536):
            candidate = np.zeros(len(PAGE_ORDER), dtype=np.dtype("<u2"))
            if ensemble == INDEPENDENT_PAGE:
                for column, page in enumerate(PAGE_ORDER):
                    candidate[column] = _unbiased_rotation_value(
                        ensemble,
                        assignment,
                        page,
                        PAGE_SIZES[page],
                        row_attempt,
                    )
            else:
                for folio in FOLIO_ORDER:
                    pages = FOLIO_PAGES[folio]
                    period = math.lcm(*(PAGE_SIZES[page] for page in pages))
                    phase = _unbiased_rotation_value(
                        ensemble,
                        assignment,
                        f"FOLIO:{folio}",
                        period,
                        row_attempt,
                    )
                    for page in pages:
                        column = PAGE_ORDER.index(page)
                        candidate[column] = (
                            phase * PAGE_SIZES[page]
                        ) // period
            row_bytes = candidate.tobytes()
            if row_bytes not in seen:
                shifts[assignment] = candidate
                seen.add(row_bytes)
                row_attempts[assignment] = row_attempt
                break
        else:
            raise FixtureError(
                f"no unique {ensemble} rotation row for assignment {assignment} "
                "through attempt 65535"
            )
    if not shifts.flags.c_contiguous or shifts.dtype != np.dtype("<u2"):
        raise FixtureError("rotation matrix lost canonical dtype/layout")
    digest = hashlib.sha256(shifts.tobytes(order="C")).hexdigest()
    shifts.setflags(write=False)
    return RotationFixture(
        ensemble=ensemble,
        page_order=PAGE_ORDER,
        shifts=shifts,
        sha256=digest,
        row_attempts=tuple(row_attempts),
        max_row_attempt=max(row_attempts),
    )


def build_calibration_rotations() -> dict[str, RotationFixture]:
    """Build both frozen 8,192-assignment calibration ensembles."""

    return {
        ensemble: build_rotation_fixture(ensemble, CALIBRATION_ASSIGNMENTS)
        for ensemble in ENSEMBLES
    }


def build_production_rotations() -> dict[str, RotationFixture]:
    """Build both frozen 65,536-assignment production ensembles."""

    return {
        ensemble: build_rotation_fixture(ensemble, PRODUCTION_ASSIGNMENTS)
        for ensemble in ENSEMBLES
    }


def apply_rotation_row(
    units: Sequence[Unit],
    labels: Sequence[str],
    shifts: Sequence[int],
) -> tuple[str, ...]:
    """Apply one row as ``numpy.roll(page_states, +shift)``.

    Destination zero-based position ``j`` receives source position
    ``(j-shift) mod page_length``, exactly as frozen after the rotation audit.
    """

    canonical = _canonical_units(units)
    if tuple(units) != canonical:
        raise FixtureError("rotation units must be in canonical page/ordinal order")
    label_tuple = tuple(labels)
    if len(label_tuple) != len(canonical) or any(state not in STATES for state in label_tuple):
        raise FixtureError("invalid label vector for rotation")
    shift_array = np.asarray(shifts)
    if shift_array.shape != (len(PAGE_ORDER),):
        raise FixtureError("rotation row must contain one shift per frozen page")
    if not np.issubdtype(shift_array.dtype, np.integer):
        raise FixtureError("rotation shifts must be integers")
    answer = list(label_tuple)
    page_indices = _indices_by_page(canonical)
    for column, page in enumerate(PAGE_ORDER):
        shift = int(shift_array[column])
        if not 0 <= shift < PAGE_SIZES[page]:
            raise FixtureError(f"out-of-range rotation shift on {page}: {shift}")
        indices = page_indices[page]
        page_states = np.asarray([label_tuple[index] for index in indices], dtype="<U1")
        rotated = np.roll(page_states, +shift)
        for index, state in zip(indices, rotated.tolist()):
            answer[index] = state
    return tuple(answer)


def _validate_feature_names(features: Sequence[str], description: str) -> tuple[str, ...]:
    answer = tuple(_ascii(feature, description) for feature in features)
    if len(set(answer)) != len(answer):
        raise FixtureError(f"duplicate {description}")
    return answer


def build_driver_fixture(
    world_id: int,
    target: str,
    driver: str,
    eligible_features: Sequence[str],
    formal_features: Sequence[str],
    root_features: Sequence[str],
) -> DriverFixture:
    """Select a frozen driver in eligible-feature order and assign its signs."""

    _validate_world_id(world_id)
    if target not in TARGETS:
        raise FixtureError(f"unknown target: {target}")
    if driver not in DRIVERS:
        raise FixtureError(f"unknown projection driver: {driver}")
    eligible = _validate_feature_names(eligible_features, "eligible feature")
    formal = set(_validate_feature_names(formal_features, "formal feature"))
    roots = set(_validate_feature_names(root_features, "root feature"))
    if len(eligible) != 83:
        raise FixtureError(f"expected 83 eligible features, found {len(eligible)}")
    if formal & roots:
        raise FixtureError("formal/root feature categories overlap")
    if any(feature not in formal | roots for feature in eligible):
        raise FixtureError("eligible feature is outside the formal/root inventory")

    if driver == DENSE_83_DRIVER:
        selected_set = set(eligible)
    else:
        eligible_formal = [feature for feature in eligible if feature in formal]
        eligible_roots = [feature for feature in eligible if feature in roots]
        if len(eligible_formal) < 12 or len(eligible_roots) < 12:
            raise FixtureError("insufficient eligible formal/root features for balanced driver")
        domain = f"DRIVER_SELECT|{target}|{driver}"
        selected_set = set(
            sorted(
                eligible_formal,
                key=lambda feature: rank_key(world_id, domain, feature),
            )[:12]
        )
        selected_set.update(
            sorted(
                eligible_roots,
                key=lambda feature: rank_key(world_id, domain, feature),
            )[:12]
        )
    selected = tuple(feature for feature in eligible if feature in selected_set)
    sign_domain = f"DRIVER_SIGN|{target}|{driver}"
    signs = tuple(
        -1 if (rank_digest(world_id, sign_domain, feature)[-1] & 1) == 0 else 1
        for feature in selected
    )
    expected_count = 83 if driver == DENSE_83_DRIVER else 24
    if len(selected) != expected_count or any(sign not in (-1, 1) for sign in signs):
        raise FixtureError("driver construction mismatch")
    return DriverFixture(world_id, target, driver, selected, signs)


def target_blind_projection_matrix(
    standardized_by_edition: Mapping[str, np.ndarray],
) -> np.ndarray:
    """Average three full-folio, target-blind standardized matrices.

    The caller is responsible for applying the frozen all-seven-folio nuisance
    fit and RMS transform before calling this function.  Labels are not an
    input, which keeps the projection construction target blind.
    """

    if set(standardized_by_edition) != set(EDITIONS):
        raise FixtureError(f"projection requires exactly these editions: {EDITIONS}")
    arrays = [np.asarray(standardized_by_edition[edition], dtype=np.float64) for edition in EDITIONS]
    shape = arrays[0].shape
    if len(shape) != 2 or shape[1] != 83 or any(array.shape != shape for array in arrays):
        raise FixtureError("standardized edition matrices must share shape (units, 83)")
    if not all(np.isfinite(array).all() for array in arrays):
        raise FixtureError("nonfinite standardized projection input")
    answer = np.zeros(shape, dtype=np.float64)
    for array in arrays:
        answer += array
    answer /= len(EDITIONS)
    if not np.isfinite(answer).all():
        raise FixtureError("nonfinite target-blind projection matrix")
    return answer


def project_units(
    projection_matrix: np.ndarray,
    eligible_features: Sequence[str],
    driver: DriverFixture,
) -> np.ndarray:
    """Project units along one hash-fixed driver in frozen feature order."""

    matrix = np.asarray(projection_matrix, dtype=np.float64)
    eligible = tuple(eligible_features)
    if matrix.ndim != 2 or matrix.shape[1] != len(eligible) or len(eligible) != 83:
        raise FixtureError("projection matrix/eligible-feature shape mismatch")
    if not np.isfinite(matrix).all():
        raise FixtureError("nonfinite projection matrix")
    feature_index = {feature: index for index, feature in enumerate(eligible)}
    if len(feature_index) != len(eligible):
        raise FixtureError("duplicate eligible feature")
    if any(feature not in feature_index for feature in driver.features):
        raise FixtureError("driver feature absent from projection matrix")
    answer = np.zeros(matrix.shape[0], dtype=np.float64)
    for feature, sign in zip(driver.features, driver.signs):
        answer += sign * matrix[:, feature_index[feature]]
    answer /= math.sqrt(len(driver.features))
    if not np.isfinite(answer).all():
        raise FixtureError("nonfinite unit projection")
    return answer


def build_beneficial_swap_plan(
    units: Sequence[Unit],
    labels: Sequence[str],
    projection: Sequence[float],
    target: str,
    strength: float,
) -> SwapPlan:
    """Build the exact gain-ranked, disjoint low/high whole-row swap plan."""

    canonical = _canonical_units(units)
    if tuple(units) != canonical:
        raise FixtureError("swap-plan units must already be in canonical page/ordinal order")
    label_tuple = tuple(labels)
    _validate_target_labels(canonical, label_tuple, target)
    projection_array = np.asarray(projection, dtype=np.float64)
    if projection_array.shape != (len(canonical),) or not np.isfinite(projection_array).all():
        raise FixtureError("projection must be one finite value per canonical unit")
    if not np.isfinite(strength) or not 0.0 <= strength <= 1.0:
        raise FixtureError("strength must be finite and in [0, 1]")

    informative = set(informative_pages(canonical, label_tuple))
    page_indices = _indices_by_page(canonical)
    page_plans: list[PageSwapPlan] = []
    for page in PAGE_ORDER:
        if page not in informative:
            page_plans.append(PageSwapPlan(page, False, (), 0))
            continue
        indices = page_indices[page]
        low_indices = [index for index in indices if label_tuple[index] == LOW]
        high_indices = [index for index in indices if label_tuple[index] == HIGH]
        low_indices.sort(
            key=lambda index: (
                -float(projection_array[index]),
                canonical[index].ordinal,
                canonical[index].unit_id,
            )
        )
        high_indices.sort(
            key=lambda index: (
                float(projection_array[index]),
                canonical[index].ordinal,
                canonical[index].unit_id,
            )
        )
        swaps: list[BeneficialSwap] = []
        for low_index, high_index in zip(low_indices, high_indices):
            low_value = float(projection_array[low_index])
            high_value = float(projection_array[high_index])
            if low_value > high_value:
                swaps.append(
                    BeneficialSwap(
                        page=page,
                        low_index=low_index,
                        high_index=high_index,
                        low_unit_id=canonical[low_index].unit_id,
                        high_unit_id=canonical[high_index].unit_id,
                        low_projection=low_value,
                        high_projection=high_value,
                        gain=low_value - high_value,
                    )
                )
        swaps.sort(
            key=lambda swap: (
                -swap.gain,
                canonical[swap.low_index].ordinal,
                canonical[swap.high_index].ordinal,
            )
        )
        applied_count = math.floor(float(strength) * len(swaps))
        page_plans.append(PageSwapPlan(page, True, tuple(swaps), applied_count))
    return SwapPlan(
        target=target,
        strength=float(strength),
        unit_ids=tuple(unit.unit_id for unit in canonical),
        pages=tuple(page_plans),
    )


def restrict_swap_plan(
    plan: SwapPlan,
    *,
    pages: Sequence[str] | None = None,
    folios: Sequence[str] | None = None,
) -> SwapPlan:
    """Keep applied swaps only on selected pages/folios for control plants."""

    if pages is None and folios is None:
        raise FixtureError("a page or folio restriction is required")
    allowed_pages = set(PAGE_ORDER if pages is None else pages)
    if any(page not in PAGE_SIZES for page in allowed_pages):
        raise FixtureError("unknown page in swap-plan restriction")
    if folios is not None:
        folio_set = set(folios)
        if any(folio not in FOLIO_ORDER for folio in folio_set):
            raise FixtureError("unknown folio in swap-plan restriction")
        allowed_pages &= {page for page in PAGE_ORDER if page[:-1] in folio_set}
    restricted = tuple(
        page if page.page in allowed_pages else replace(page, applied_count=0)
        for page in plan.pages
    )
    return replace(plan, pages=restricted)


def folio_signed_projection(
    units: Sequence[Unit],
    projection: Sequence[float],
    folio_signs: Mapping[str, int],
) -> np.ndarray:
    """Apply predeclared +/- folio signs for opposite-cluster controls."""

    canonical = _canonical_units(units)
    if tuple(units) != canonical:
        raise FixtureError("units must be in canonical order")
    if set(folio_signs) != set(FOLIO_ORDER) or any(sign not in (-1, 1) for sign in folio_signs.values()):
        raise FixtureError("folio signs must assign +/-1 to every physical folio")
    answer = np.asarray(projection, dtype=np.float64).copy()
    if answer.shape != (len(canonical),) or not np.isfinite(answer).all():
        raise FixtureError("invalid projection for folio signing")
    for index, unit in enumerate(canonical):
        answer[index] *= folio_signs[unit.physical_folio]
    return answer


def apply_whole_row_plan(
    values_by_edition: Mapping[str, np.ndarray],
    plan: SwapPlan,
    *,
    unit_ids: Sequence[str],
    editions_to_apply: Sequence[str] = EDITIONS,
) -> dict[str, np.ndarray]:
    """Apply a plan to complete feature rows, synchronously by default.

    Passing one edition implements the one-reading sensitivity.  Passing all
    three editions is the primary whole-triplet plant.
    """

    if set(values_by_edition) != set(EDITIONS):
        raise FixtureError(f"row application requires exactly these editions: {EDITIONS}")
    if tuple(unit_ids) != plan.unit_ids:
        raise FixtureError("matrix unit IDs do not match the swap plan's canonical order")
    selected_editions = tuple(editions_to_apply)
    if len(set(selected_editions)) != len(selected_editions) or any(
        edition not in EDITIONS for edition in selected_editions
    ):
        raise FixtureError("invalid edition selection")
    arrays = {
        edition: np.asarray(values_by_edition[edition]).copy(order="C")
        for edition in EDITIONS
    }
    row_count = len(plan.unit_ids)
    shapes = {array.shape for array in arrays.values()}
    if (
        len(shapes) != 1
        or any(array.ndim != 2 or array.shape != (row_count, 84) for array in arrays.values())
    ):
        raise FixtureError("edition arrays must all have shape (plan rows, 84)")
    for swap in plan.applied_swaps:
        for edition in selected_editions:
            array = arrays[edition]
            temporary = array[swap.low_index].copy()
            array[swap.low_index] = array[swap.high_index]
            array[swap.high_index] = temporary
    return arrays


def apply_edition_plans(
    values_by_edition: Mapping[str, np.ndarray],
    plans_by_edition: Mapping[str, SwapPlan],
    *,
    unit_ids: Sequence[str],
) -> dict[str, np.ndarray]:
    """Apply separate plans by reading, including the RF-reversal control."""

    if set(values_by_edition) != set(EDITIONS) or set(plans_by_edition) != set(EDITIONS):
        raise FixtureError(f"one swap plan is required for each edition: {EDITIONS}")
    reference_ids = plans_by_edition[EDITIONS[0]].unit_ids
    if any(plan.unit_ids != reference_ids for plan in plans_by_edition.values()):
        raise FixtureError("per-edition plans use different unit orders")
    if tuple(unit_ids) != reference_ids:
        raise FixtureError("matrix unit IDs do not match the plans' canonical order")
    answer = {
        edition: np.asarray(values_by_edition[edition]).copy(order="C")
        for edition in EDITIONS
    }
    if any(array.ndim != 2 or array.shape != (len(reference_ids), 84) for array in answer.values()):
        raise FixtureError("edition arrays must all have shape (plan rows, 84)")
    for edition in EDITIONS:
        for swap in plans_by_edition[edition].applied_swaps:
            array = answer[edition]
            temporary = array[swap.low_index].copy()
            array[swap.low_index] = array[swap.high_index]
            array[swap.high_index] = temporary
    return answer


def _synthetic_units() -> tuple[Unit, ...]:
    return tuple(
        Unit(page, ordinal, f"{page}:{ordinal:02d}", page[:-1])
        for page in PAGE_ORDER
        for ordinal in range(1, PAGE_SIZES[page] + 1)
    )


def self_test(*, full_rotations: bool = False) -> None:
    """Run target-free deterministic checks using fabricated anonymous rows."""

    units = _synthetic_units()
    panel = generate_label_panel(units)
    repeated = generate_label_panel(units)
    if tuple(world.paired_sha256 for world in panel.worlds) != tuple(
        world.paired_sha256 for world in repeated.worlds
    ):
        raise AssertionError("label panel is not deterministic")

    rotations = build_calibration_rotations()
    for ensemble, fixture in rotations.items():
        if fixture.shifts.shape != (CALIBRATION_ASSIGNMENTS, len(PAGE_ORDER)):
            raise AssertionError(f"bad {ensemble} calibration shape")
        if np.any(fixture.shifts[0] != 0):
            raise AssertionError(f"bad {ensemble} identity rotation")
        for column, page in enumerate(PAGE_ORDER):
            if np.any(fixture.shifts[:, column] >= PAGE_SIZES[page]):
                raise AssertionError(f"out-of-range shift on {page}")
        if len(fixture.row_attempts) != CALIBRATION_ASSIGNMENTS:
            raise AssertionError(f"bad {ensemble} row-attempt table")
        if fixture.max_row_attempt != max(fixture.row_attempts):
            raise AssertionError(f"bad {ensemble} row-attempt maximum")
    example_shifts = np.zeros(len(PAGE_ORDER), dtype=np.uint16)
    example_shifts[0] = 1
    rotated = apply_rotation_row(panel.units, panel.world(0).ray_labels, example_shifts)
    first_page_indices = [
        index for index, unit in enumerate(panel.units) if unit.page == PAGE_ORDER[0]
    ]
    original_first_page = [panel.world(0).ray_labels[index] for index in first_page_indices]
    rotated_first_page = [rotated[index] for index in first_page_indices]
    if rotated_first_page != np.roll(np.asarray(original_first_page), +1).tolist():
        raise AssertionError("positive rotation direction mismatch")
    if full_rotations:
        production = build_production_rotations()
        if any(
            fixture.shifts.shape != (PRODUCTION_ASSIGNMENTS, len(PAGE_ORDER))
            for fixture in production.values()
        ):
            raise AssertionError("bad production rotation shape")

    eligible = tuple(f"FORMAL_{index:02d}" for index in range(33)) + tuple(
        f"ROOT_{index:02d}" for index in range(50)
    )
    formal = eligible[:33]
    roots = eligible[33:]
    dense = build_driver_fixture(
        0, RAY_LIKE, DENSE_83_DRIVER, eligible, formal, roots
    )
    balanced = build_driver_fixture(
        0, RAY_LIKE, BALANCED_24_DRIVER, eligible, formal, roots
    )
    if len(dense.features) != 83 or len(balanced.features) != 24:
        raise AssertionError("driver feature counts are wrong")

    rows = len(units)
    columns = len(eligible)
    standardized = {}
    base_grid = np.arange(rows * columns, dtype=np.float64).reshape(rows, columns)
    for edition_index, edition in enumerate(EDITIONS):
        standardized[edition] = np.sin(
            (base_grid + 1.0 + edition_index * 0.25) / 37.0
        )
    projection_matrix = target_blind_projection_matrix(standardized)
    projection = project_units(projection_matrix, eligible, balanced)
    world = panel.world(0)
    ray_plan = build_beneficial_swap_plan(
        panel.units, world.ray_labels, projection, RAY_LIKE, 0.75
    )
    tail_plan = build_beneficial_swap_plan(
        panel.units, world.tail_labels, projection, TAIL_LIKE, 0.75
    )
    tail_informative = set(informative_pages(panel.units, world.tail_labels))
    if any(
        page.applied_count != 0 or page.complete_swaps
        for page in tail_plan.pages
        if page.page not in tail_informative
    ):
        raise AssertionError("tail noninformative page was planted")

    row_values = np.arange(rows * 84, dtype=np.float64).reshape(rows, 84)
    matrices = {
        edition: row_values + edition_index * 1_000_000.0
        for edition_index, edition in enumerate(EDITIONS)
    }
    planted = apply_whole_row_plan(
        matrices,
        ray_plan,
        unit_ids=tuple(unit.unit_id for unit in panel.units),
    )
    for page in PAGE_ORDER:
        indices = [index for index, unit in enumerate(panel.units) if unit.page == page]
        for edition in EDITIONS:
            before = sorted(matrices[edition][indices, 0].tolist())
            after = sorted(planted[edition][indices, 0].tolist())
            if before != after:
                raise AssertionError("whole-row plant changed a page inventory")
    donor_ids = [
        planted[edition][:, 0] - edition_index * 1_000_000.0
        for edition_index, edition in enumerate(EDITIONS)
    ]
    if not all(np.array_equal(donor_ids[0], values) for values in donor_ids[1:]):
        raise AssertionError("whole-row plant split alternate-reading triplets")


if __name__ == "__main__":
    import sys

    self_test(full_rotations="--full" in sys.argv[1:])
    print("sme003_fixture self-test: PASS")
