#!/usr/bin/env python3
"""Target-excluding co-field features for GDT767.

This module is deliberately read-only.  It loads the guarded semantic
environment inherited by GDT764, independently enumerates the GDT766 target
forms and positions in that environment, and returns Python data structures.
It never writes an artifact and never opens an image or a new transcription.

The public entry point is :func:`build_cofield`::

    result = build_cofield()
    occurrence_rows = result["atlas"]
    form_rows = result["matrix"]

Every feature count is target-excluding.  All 28 target complete forms,
``pchor``, and all 172 GDT754 productive-compound complete forms are forbidden
as feature donors.
"""

from __future__ import annotations

import csv
import importlib.util
import sys
from collections import Counter
from pathlib import Path
from types import ModuleType
from typing import Iterable, Mapping, Sequence

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    """Return the repository root without consulting user-specific paths."""

    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())

G764_RUN_REL = Path(
    "experiments/yolo/gdt764_bounded_value_field_dispatch/src/run.py"
)
G754_INVENTORY_REL = Path(
    "experiments/yolo/gdt754_active_productive_compound_provenance_sieve/"
    "artifacts/ACTIVE_172_PRODUCTIVE_COMPOUND_INVENTORY.tsv"
)

CHOR_TARGETS = frozenset({"chor", "schor", "lchor"})
EXTRA_BLOCKED_DONORS = frozenset({"pchor"})
FORBIDDEN_PAGE_PREFIXES = ("f84",)

FEATURES = (
    "DRY",
    "MOIST",
    "HOT",
    "COLD",
    "STAGE",
    "VALUE_AMOUNT",
    "CTHY_LEAF",
    "CHOR_REPRO",
    "PREP",
    "PROCESS_CLOSE",
    "H1",
    "H2",
)
SCOPES = ("D1", "R3", "LINE")

STAGE_AXES = frozenset(
    {"BEGIN_STAGE", "MIDDLE_STAGE", "END_STAGE", "LEVEL_I", "LEVEL_II", "LEVEL_III"}
)
VALUE_ROLES = frozenset({"SCALAR_VALUE", "AMOUNT_VALUE"})
VALUE_AXES = frozenset({"AMOUNT", "PART"})
PROCESS_ROLES = frozenset({"PROCESS_PASS", "CLOSE"})
PROCESS_AXES = frozenset({"PROCESS", "PASS", "CLOSE"})


def _read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _pipe_set(value: object) -> set[str]:
    return {item for item in str(value).split("|") if item and item not in {"NONE", "OPEN"}}


def load_target_occurrences(
    environment: Mapping[str, object],
) -> list[dict[str, object]]:
    """Enumerate the fixed targets directly from the guarded cache.

    The formal OFCH selector is substring containment on a complete EVA token;
    it is not a component-meaning claim.  ``pchor`` is deliberately not a
    target in this matrix.
    """

    context = environment["context"]
    selected: list[dict[str, object]] = []
    for locus, line in sorted(context.by_line.items()):
        for ordinal, token in enumerate(line, 1):
            surface = str(token["eva"])
            family = (
                "OFCH_CONTAINING"
                if "ofch" in surface
                else "CHOR_SCHOR_LCHOR"
                if surface in CHOR_TARGETS
                else ""
            )
            if not family:
                continue
            if not bool(context.exact[(locus, int(token["token_index"]))]):
                continue
            selected.append(
                {
                    "target_family": family,
                    "surface": surface,
                    "page": str(token["page"]),
                    "locus": locus,
                    "ordinal": ordinal,
                }
            )

    selected.sort(
        key=lambda row: (
            str(row["page"]),
            str(row["locus"]),
            int(row["ordinal"]),
            str(row["surface"]),
        )
    )
    output: list[dict[str, object]] = []
    for index, row in enumerate(selected, 1):
        output.append({"source_occurrence_id": f"G767-CF{index:04d}", **row})
    return output


def load_blocked_donor_surfaces(
    target_surfaces: Iterable[str], root: Path = ROOT
) -> tuple[frozenset[str], frozenset[str]]:
    """Return ``(all_blocked, gdt754_surfaces)`` for the fixed donor gate."""

    gdt754 = frozenset(
        row["surface"] for row in _read_tsv(root / G754_INVENTORY_REL)
    )
    blocked = frozenset(target_surfaces) | EXTRA_BLOCKED_DONORS | gdt754
    assert len(gdt754) == 172, "GDT754 productive-compound donor block changed"
    assert EXTRA_BLOCKED_DONORS <= blocked
    return blocked, gdt754


def donor_features(
    environment: Mapping[str, object],
    g764: ModuleType,
    locus: str,
    ordinal: int,
    blocked_donor_surfaces: frozenset[str],
) -> tuple[frozenset[str], dict[str, object] | None]:
    """Classify one independently admitted donor position.

    A blocked, non-reader-exact, or quarantined position returns no feature and
    no donor record.  Complete target spellings never contribute indirectly
    through their prior German defaults.
    """

    slot = g764.slot(environment, locus, ordinal)
    if not int(slot["reader_exact"]) or not int(slot["clean"]):
        return frozenset(), None

    surface = str(slot["surface"])
    if surface in blocked_donor_surfaces:
        return frozenset(), None

    axes = _pipe_set(slot["axes"])
    roles = _pipe_set(slot["roles"])
    state_map = environment["state_map"]
    assert isinstance(state_map, dict)
    state = state_map.get(surface)

    features: set[str] = set()
    if "DRY" in axes or (state is not None and state["polarity"] == "DRY"):
        features.add("DRY")
    if "MOIST" in axes or (state is not None and state["polarity"] == "MOIST"):
        features.add("MOIST")
    if "HOT" in axes:
        features.add("HOT")
    if "COLD" in axes:
        features.add("COLD")
    if axes & STAGE_AXES or (
        state is not None
        and any(label in state["pair_role"] for label in ("BEGIN", "MIDDLE", "END"))
    ):
        features.add("STAGE")
    if roles & VALUE_ROLES or axes & VALUE_AXES:
        features.add("VALUE_AMOUNT")
    if surface == "cthy":
        features.add("CTHY_LEAF")
    # Under the fixed target-excluding gate exact `chor` is blocked.  Keeping
    # this classifier explicit makes the resulting zero column auditable and
    # prevents chory/shor spelling analogies from silently receiving credit.
    if surface == "chor":
        features.add("CHOR_REPRO")
    if "PREPARATION" in axes:
        features.add("PREP")
    if roles & PROCESS_ROLES or axes & PROCESS_AXES:
        features.add("PROCESS_CLOSE")
    if "H1_RECORD_FORM" in roles:
        features.add("H1")
    if "H2_RECORD_FORM" in roles:
        features.add("H2")

    if not features:
        return frozenset(), None
    frozen = frozenset(features)
    return frozen, {
        "surface": surface,
        "ordinal": ordinal,
        "features": tuple(feature for feature in FEATURES if feature in frozen),
        "semantic_source": str(slot["semantic_source"]),
    }


def build_occurrence_atlas(
    environment: Mapping[str, object],
    g764: ModuleType,
    target_occurrences: Sequence[Mapping[str, object]],
    blocked_donor_surfaces: frozenset[str],
) -> list[dict[str, object]]:
    """Return one target-excluding co-field row per exact target occurrence."""

    context = environment["context"]
    atlas: list[dict[str, object]] = []
    seen: set[tuple[str, int]] = set()

    for source in target_occurrences:
        locus = str(source["locus"])
        ordinal = int(source["ordinal"])
        surface = str(source["surface"])
        page = str(source["page"])
        assert not page.startswith(FORBIDDEN_PAGE_PREFIXES), f"forbidden target page: {page}"
        assert locus in context.by_line, f"target locus absent from guarded cache: {locus}"
        line = context.by_line[locus]
        assert 1 <= ordinal <= len(line), f"target ordinal outside line: {locus}@{ordinal}"
        token = line[ordinal - 1]
        assert str(token["eva"]) == surface, f"target surface mismatch: {locus}@{ordinal}"
        assert bool(context.exact[(locus, int(token["token_index"]))]), (
            f"target is not reader-exact: {locus}@{ordinal}"
        )
        key = (locus, ordinal)
        assert key not in seen, f"duplicate target position: {locus}@{ordinal}"
        seen.add(key)

        scope_features = {scope: set() for scope in SCOPES}
        scope_donors: dict[str, list[dict[str, object]]] = {scope: [] for scope in SCOPES}
        for donor_ordinal in range(1, len(line) + 1):
            if donor_ordinal == ordinal:
                continue
            feature_set, donor = donor_features(
                environment, g764, locus, donor_ordinal, blocked_donor_surfaces
            )
            if not feature_set or donor is None:
                continue
            distance = abs(donor_ordinal - ordinal)
            donor = {**donor, "distance": distance}
            scope_features["LINE"].update(feature_set)
            scope_donors["LINE"].append(donor)
            if distance <= 3:
                scope_features["R3"].update(feature_set)
                scope_donors["R3"].append(donor)
            if distance == 1:
                scope_features["D1"].update(feature_set)
                scope_donors["D1"].append(donor)

        atlas.append(
            {
                "source_occurrence_id": str(source["source_occurrence_id"]),
                "target_family": str(source["target_family"]),
                "surface": surface,
                "page": page,
                "locus": locus,
                "ordinal": ordinal,
                "line_token_count": len(line),
                "written_line_eva": " ".join(str(item["eva"]) for item in line),
                "d1_features": tuple(
                    feature for feature in FEATURES if feature in scope_features["D1"]
                ),
                "r3_features": tuple(
                    feature for feature in FEATURES if feature in scope_features["R3"]
                ),
                "line_features": tuple(
                    feature for feature in FEATURES if feature in scope_features["LINE"]
                ),
                "d1_donors": tuple(scope_donors["D1"]),
                "r3_donors": tuple(scope_donors["R3"]),
                "line_donors": tuple(scope_donors["LINE"]),
            }
        )

    return atlas


def build_form_matrix(
    occurrence_atlas: Sequence[Mapping[str, object]],
    target_surfaces: Iterable[str],
) -> list[dict[str, object]]:
    """Aggregate occurrence presence to D1/R3/whole-line counts by form."""

    rows: list[dict[str, object]] = []
    for surface in sorted(target_surfaces):
        occurrences = [row for row in occurrence_atlas if row["surface"] == surface]
        assert occurrences, f"target form has no occurrence: {surface}"
        family_counts = Counter(str(row["target_family"]) for row in occurrences)
        assert len(family_counts) == 1
        feature_counts: dict[str, dict[str, int]] = {}
        flat_counts: dict[str, int | str] = {}
        for feature in FEATURES:
            counts = {
                "D1": sum(feature in row["d1_features"] for row in occurrences),
                "R3": sum(feature in row["r3_features"] for row in occurrences),
                "LINE": sum(feature in row["line_features"] for row in occurrences),
            }
            assert 0 <= counts["D1"] <= counts["R3"] <= counts["LINE"] <= len(occurrences)
            feature_counts[feature] = counts
            stem = feature.lower()
            flat_counts[f"{stem}_d1"] = counts["D1"]
            flat_counts[f"{stem}_r3"] = counts["R3"]
            flat_counts[f"{stem}_line"] = counts["LINE"]
            flat_counts[f"{stem}_d1_r3_line"] = (
                f"{counts['D1']}/{counts['R3']}/{counts['LINE']}"
            )
        rows.append(
            {
                "surface": surface,
                "target_family": next(iter(family_counts)),
                "reader_exact_occurrences": len(occurrences),
                "feature_counts": feature_counts,
                **flat_counts,
            }
        )
    return rows


def build_cofield(root: Path = ROOT) -> dict[str, object]:
    """Build and return the fixed GDT767 co-field universe without writing.

    Return keys:

    ``atlas``
        224 occurrence rows with target-free D1, R3 and whole-line donors.
    ``matrix``
        28 form rows with both nested and flat feature counts.
    ``summary``
        Fixed universe and donor-gate counts.
    ``target_surfaces`` / ``blocked_donor_surfaces`` / ``features`` / ``scopes``
        Deterministic metadata for a caller or validator.
    """

    g764 = _load_module("gdt764_for_gdt767_cofield", root / G764_RUN_REL)
    environment = g764.semantic_environment()
    target_occurrences = load_target_occurrences(environment)
    target_surfaces = frozenset(str(row["surface"]) for row in target_occurrences)
    blocked, gdt754 = load_blocked_donor_surfaces(target_surfaces, root)

    ofch_rows = [row for row in target_occurrences if row["target_family"] == "OFCH_CONTAINING"]
    assert len(target_surfaces) == 28, "GDT767 target form universe changed"
    assert len(target_occurrences) == 224, "GDT767 target occurrence universe changed"
    assert len(ofch_rows) == 43, "GDT767 OFCH target occurrence universe changed"
    assert len({str(row["surface"]) for row in ofch_rows}) == 25
    assert Counter(str(row["surface"]) for row in target_occurrences if row["target_family"] != "OFCH_CONTAINING") == Counter(
        {"chor": 176, "schor": 3, "lchor": 2}
    )
    assert target_surfaces <= blocked
    assert "pchor" in blocked

    atlas = build_occurrence_atlas(
        environment, g764, target_occurrences, blocked
    )
    matrix = build_form_matrix(atlas, target_surfaces)
    assert len(atlas) == 224
    assert len(matrix) == 28
    assert sum(int(row["reader_exact_occurrences"]) for row in matrix) == 224
    # `chor` belongs to the blocked target set, so no exact-chor feature may
    # self-confirm a target identity in this target-excluding pass.
    assert all(
        int(row["feature_counts"]["CHOR_REPRO"][scope]) == 0
        for row in matrix
        for scope in SCOPES
    )

    guard = dict(environment["guard"])
    return {
        "atlas": atlas,
        "matrix": matrix,
        "summary": {
            "target_forms": len(target_surfaces),
            "target_occurrences": len(atlas),
            "ofch_forms": len({str(row["surface"]) for row in ofch_rows}),
            "ofch_occurrences": len(ofch_rows),
            "chor_occurrences": 176,
            "schor_occurrences": 3,
            "lchor_occurrences": 2,
            "gdt754_blocked_surfaces": len(gdt754),
            "blocked_donor_surfaces": len(blocked),
            "guard_selected": int(guard["selected"]),
            "guard_skipped_forbidden": int(guard["skipped_forbidden"]),
            "guard_skipped_not_allowed": int(guard["skipped_not_allowed"]),
        },
        "target_surfaces": tuple(sorted(target_surfaces)),
        "blocked_donor_surfaces": tuple(sorted(blocked)),
        "features": FEATURES,
        "scopes": SCOPES,
        "donor_rule": (
            "READER_EXACT_AND_CLEAN__EXCLUDE_28_TARGETS_PCHOR_AND_GDT754_172"
        ),
    }


__all__ = (
    "FEATURES",
    "SCOPES",
    "build_cofield",
    "build_form_matrix",
    "build_occurrence_atlas",
    "donor_features",
    "load_blocked_donor_surfaces",
    "load_target_occurrences",
)
