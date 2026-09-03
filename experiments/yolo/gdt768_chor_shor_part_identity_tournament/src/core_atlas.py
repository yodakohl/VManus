#!/usr/bin/env python3
"""Read-only structural core for GDT768.

The module enumerates six *complete* reader-exact EVA surfaces from the
already admitted guarded cache and builds the controls needed by the GDT768
runner.  It does not write artifacts, open images, or read a new
transcription.  In particular, ``f84`` and ``f84r`` remain rejected by the
inherited context loader.

The 172 GDT754 source-composed surfaces are globally barred before any family
test.  The remaining family ablation is deliberately target-specific.  At
radius zero only the same complete target surface is barred as a donor; at
radii one and two every complete donor surface within that Levenshtein
distance of the current target is barred.  Edit distance is an EVA-shape
control only and receives no component, sound, or semantic credit.

Public entry point::

    core = build_core_atlas()

The returned mapping contains Python rows only.  Artifact serialization is the
responsibility of ``src/run.py``.
"""

from __future__ import annotations

import csv
import importlib.util
import sys
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path
from types import ModuleType
from typing import Mapping, Sequence

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    """Locate the repository without embedding private machine paths."""

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

TARGET_FORMS = ("chor", "shor", "cthy", "dair", "kooiin", "koaiin")
TARGET_FORM_SET = frozenset(TARGET_FORMS)
ABLATION_RADII = (0, 1, 2)
SCOPES = ("D1", "R3", "LINE")
FORBIDDEN_PAGE_PREFIXES = ("f84",)

FEATURES = (
    "DRY",
    "MOIST",
    "HOT",
    "COLD",
    "STAGE",
    "VALUE_AMOUNT",
    "PREP",
    "PROCESS_CLOSE",
    "H1",
    "H2",
    "H3",
    "H4",
    "ANCHOR_CHOR",
    "ANCHOR_SHOR",
    "ANCHOR_CTHY",
    "ANCHOR_DAIR",
    "ANCHOR_KOOIIN",
    "ANCHOR_KOAIIN",
)

STAGE_AXES = frozenset(
    {
        "BEGIN_STAGE",
        "MIDDLE_STAGE",
        "END_STAGE",
        "LEVEL_I",
        "LEVEL_II",
        "LEVEL_III",
    }
)
VALUE_ROLES = frozenset({"SCALAR_VALUE", "AMOUNT_VALUE"})
VALUE_AXES = frozenset({"AMOUNT", "PART"})
PROCESS_ROLES = frozenset({"PROCESS_PASS", "CLOSE"})
PROCESS_AXES = frozenset({"PROCESS", "PASS", "CLOSE"})

# Counts established by the independent preliminary census.  These are
# assertions about the fixed guarded cache, not semantic claims.
EXPECTED_TARGET_COUNTS = {
    "chor": 176,
    "shor": 77,
    "cthy": 85,
    "dair": 63,
    "kooiin": 2,
    "koaiin": 1,
}
EXPECTED_PAIR_COUNTS = {
    ("chor", "cthy"): (14, 11, 5),
    ("cthy", "shor"): (8, 7, 3),
    ("chor", "shor"): (8, 8, 3),
    ("chor", "dair"): (5, 5, 2),
}
# Corrected values after the global GDT754 gate.  They equal the preliminary
# values because every GDT754 exposure in these target lines was already
# quarantined by the inherited clean-cell gate; the explicit provenance gate
# changes classification and auditability rather than these feature counts.
EXPECTED_CORRECTED_D1_DRY_MOIST = {
    ("chor", 0): (45, 9),
    ("shor", 0): (8, 12),
    ("chor", 1): (28, 9),
    ("shor", 1): (8, 5),
    ("chor", 2): (12, 7),
    ("shor", 2): (7, 2),
}
EXPECTED_GDT754_BLOCKED_DONOR_POSITIONS = {
    ("chor", "D1"): 8,
    ("chor", "R3"): 18,
    ("chor", "LINE"): 26,
    ("shor", "D1"): 0,
    ("shor", "R3"): 4,
    ("shor", "LINE"): 9,
    ("cthy", "D1"): 7,
    ("cthy", "R3"): 8,
    ("cthy", "LINE"): 11,
    ("dair", "D1"): 1,
    ("dair", "R3"): 1,
    ("dair", "LINE"): 8,
    ("kooiin", "D1"): 0,
    ("kooiin", "R3"): 0,
    ("kooiin", "LINE"): 0,
    ("koaiin", "D1"): 0,
    ("koaiin", "R3"): 0,
    ("koaiin", "LINE"): 0,
}


def _load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _pipe_set(value: object) -> set[str]:
    return {
        item
        for item in str(value).split("|")
        if item and item not in {"NONE", "OPEN"}
    }


def load_gdt754_source_composed_surfaces(
    root: Path = ROOT,
) -> frozenset[str]:
    """Load the fixed global donor quarantine from GDT754."""

    path = root / G754_INVENTORY_REL
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    surfaces = frozenset(row["surface"] for row in rows)
    assert len(rows) == 172, "GDT754 source-composed row count changed"
    assert len(surfaces) == 172, "GDT754 source-composed surfaces are not unique"
    assert not TARGET_FORM_SET & surfaces, (
        "a GDT768 target entered the GDT754 source-composed quarantine"
    )
    return surfaces


@lru_cache(maxsize=None)
def levenshtein(first: str, second: str) -> int:
    """Return ordinary character Levenshtein distance deterministically."""

    if first == second:
        return 0
    if not first:
        return len(second)
    if not second:
        return len(first)
    # Keep the inner vector on the shorter string.
    if len(first) < len(second):
        first, second = second, first
    previous = list(range(len(second) + 1))
    for row_index, first_char in enumerate(first, 1):
        current = [row_index]
        for column_index, second_char in enumerate(second, 1):
            current.append(
                min(
                    current[-1] + 1,
                    previous[column_index] + 1,
                    previous[column_index - 1] + (first_char != second_char),
                )
            )
        previous = current
    return previous[-1]


def _line_position(ordinal: int, token_count: int) -> str:
    if token_count == 1:
        return "SINGLE"
    if ordinal == 1:
        return "FIRST"
    if ordinal == token_count:
        return "LAST"
    return "MIDDLE"


def _physical_folio(page: str) -> str:
    """Mirror the inherited helper while keeping this module self-contained."""

    for suffix in ("r1", "r2", "r3", "r4", "r5", "r6", "v1", "v2", "v3", "v4", "v5", "v6", "r", "v"):
        if page.endswith(suffix):
            return page[: -len(suffix)]
    return page


def load_guarded_environment(root: Path = ROOT) -> tuple[ModuleType, dict[str, object]]:
    """Load the existing GDT764 semantic environment and verify its guard."""

    g764 = _load_module("gdt764_for_gdt768_core", root / G764_RUN_REL)
    environment = g764.semantic_environment()
    guard = dict(environment["guard"])
    assert guard == {
        "selected": 4137,
        "skipped_forbidden": 98,
        "skipped_not_allowed": 1150,
    }, "guarded cache universe changed"
    return g764, environment


def enumerate_exact_targets(
    environment: Mapping[str, object],
) -> list[dict[str, object]]:
    """Enumerate all six exact complete-word targets from the guarded cache."""

    context = environment["context"]
    line_meta = environment["line_meta"]
    rows: list[dict[str, object]] = []
    seen: set[tuple[str, int]] = set()

    for locus, line in sorted(context.by_line.items()):
        meta = line_meta[locus]
        for index, token in enumerate(line):
            surface = str(token["eva"])
            if surface not in TARGET_FORM_SET:
                continue
            if not bool(context.exact[(locus, int(token["token_index"]))]):
                continue
            ordinal = index + 1
            page = str(token["page"])
            assert not page.startswith(FORBIDDEN_PAGE_PREFIXES), (
                f"forbidden target page reached guarded cache: {page}"
            )
            key = (locus, ordinal)
            assert key not in seen, f"duplicate target position: {locus}@{ordinal}"
            seen.add(key)
            rows.append(
                {
                    "target_occurrence_id": "",
                    "surface": surface,
                    "page": page,
                    "physical_folio": _physical_folio(page),
                    "locus": locus,
                    "line_number": int(meta["line_number"]),
                    "section": str(token["section"]),
                    "language": str(token["language"]),
                    "hand": str(token["hand"]),
                    "ordinal": ordinal,
                    "token_index": int(token["token_index"]),
                    "line_token_count": len(line),
                    "line_position": _line_position(ordinal, len(line)),
                    "normalized_line_position": (
                        0.0 if len(line) == 1 else (ordinal - 1) / (len(line) - 1)
                    ),
                    "paragraph_start_line": int(meta["paragraph_start"]),
                    "paragraph_end_line": int(meta["paragraph_end"]),
                    "true_paragraph_opener": int(
                        ordinal == 1 and int(meta["paragraph_start"]) == 1
                    ),
                    "true_paragraph_closer": int(
                        ordinal == len(line) and int(meta["paragraph_end"]) == 1
                    ),
                    "written_line_eva": " ".join(str(item["eva"]) for item in line),
                }
            )

    rows.sort(
        key=lambda row: (
            str(row["page"]),
            int(row["line_number"]),
            int(row["ordinal"]),
            str(row["surface"]),
        )
    )
    for number, row in enumerate(rows, 1):
        row["target_occurrence_id"] = f"G768-T{number:04d}"

    counts = Counter(str(row["surface"]) for row in rows)
    assert len(rows) == 404, "GDT768 six-target occurrence universe changed"
    assert counts == Counter(EXPECTED_TARGET_COUNTS), (
        f"GDT768 target counts changed: {dict(counts)}"
    )
    return rows


def donor_features(
    environment: Mapping[str, object],
    g764: ModuleType,
    locus: str,
    ordinal: int,
    target_surface: str,
    family_radius: int,
    source_composed_surfaces: frozenset[str],
) -> tuple[frozenset[str], dict[str, object] | None, str]:
    """Classify one potential donor after provenance and family gates.

    Returns ``(features, donor_record, gate_status)``.  An admitted donor has a
    record even if it carries no current feature, which lets callers audit
    exposure independently of feature availability.  The GDT754 provenance
    block precedes edit-family classification, so a source-composed form can
    never escape merely because it is distant from the current target.
    """

    if family_radius not in ABLATION_RADII:
        raise ValueError(f"unsupported family radius: {family_radius}")
    slot = g764.slot(environment, locus, ordinal)
    if str(slot["status"]) == "EDGE":
        return frozenset(), None, "EDGE"
    if not int(slot["reader_exact"]):
        return frozenset(), None, "NONEXACT"

    surface = str(slot["surface"])
    if surface in source_composed_surfaces:
        return frozenset(), {
            "surface": surface,
            "ordinal": ordinal,
            "provenance_source": "GDT754_ACTIVE_172_PRODUCTIVE_COMPOUND_INVENTORY",
        }, "GDT754_SOURCE_COMPOSED_BLOCK"
    if not int(slot["clean"]):
        return frozenset(), None, "QUARANTINED"

    distance_to_target = levenshtein(surface, target_surface)
    if distance_to_target <= family_radius:
        return frozenset(), {
            "surface": surface,
            "ordinal": ordinal,
            "edit_distance_to_target": distance_to_target,
        }, "TARGET_FAMILY_BLOCK"

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
    if "PREPARATION" in axes:
        features.add("PREP")
    if roles & PROCESS_ROLES or axes & PROCESS_AXES:
        features.add("PROCESS_CLOSE")
    for head in ("H1", "H2", "H3", "H4"):
        if f"{head}_RECORD_FORM" in roles:
            features.add(head)
    if surface in TARGET_FORM_SET:
        features.add(f"ANCHOR_{surface.upper()}")

    frozen = frozenset(features)
    return frozen, {
        "surface": surface,
        "ordinal": ordinal,
        "edit_distance_to_target": distance_to_target,
        "features": tuple(feature for feature in FEATURES if feature in frozen),
        "axes": tuple(sorted(axes)),
        "roles": tuple(sorted(roles)),
        "semantic_source": str(slot["semantic_source"]),
    }, "ELIGIBLE"


def build_occurrence_feature_atlas(
    environment: Mapping[str, object],
    g764: ModuleType,
    target_occurrences: Sequence[Mapping[str, object]],
    source_composed_surfaces: frozenset[str],
) -> list[dict[str, object]]:
    """Attach target-specific edit-family feature views to each occurrence."""

    context = environment["context"]
    output: list[dict[str, object]] = []
    for source in target_occurrences:
        locus = str(source["locus"])
        target_ordinal = int(source["ordinal"])
        target_surface = str(source["surface"])
        line = context.by_line[locus]
        views: dict[int, dict[str, object]] = {}

        for radius in ABLATION_RADII:
            scope_features: dict[str, set[str]] = {scope: set() for scope in SCOPES}
            scope_donors: dict[str, list[dict[str, object]]] = {
                scope: [] for scope in SCOPES
            }
            scope_blocked: dict[str, list[dict[str, object]]] = {
                scope: [] for scope in SCOPES
            }
            scope_source_blocked: dict[str, list[dict[str, object]]] = {
                scope: [] for scope in SCOPES
            }
            gate_counts: Counter[str] = Counter()

            for donor_ordinal in range(1, len(line) + 1):
                if donor_ordinal == target_ordinal:
                    continue
                distance = abs(donor_ordinal - target_ordinal)
                features, donor, gate = donor_features(
                    environment,
                    g764,
                    locus,
                    donor_ordinal,
                    target_surface,
                    radius,
                    source_composed_surfaces,
                )
                gate_counts[gate] += 1
                if donor is not None:
                    donor = {
                        **donor,
                        "distance": distance,
                        "direction": "LEFT" if donor_ordinal < target_ordinal else "RIGHT",
                    }
                if gate == "TARGET_FAMILY_BLOCK" and donor is not None:
                    scope_blocked["LINE"].append(donor)
                    if distance <= 3:
                        scope_blocked["R3"].append(donor)
                    if distance == 1:
                        scope_blocked["D1"].append(donor)
                    continue
                if gate == "GDT754_SOURCE_COMPOSED_BLOCK" and donor is not None:
                    scope_source_blocked["LINE"].append(donor)
                    if distance <= 3:
                        scope_source_blocked["R3"].append(donor)
                    if distance == 1:
                        scope_source_blocked["D1"].append(donor)
                    continue
                if gate != "ELIGIBLE" or donor is None:
                    continue

                scope_donors["LINE"].append(donor)
                scope_features["LINE"].update(features)
                if distance <= 3:
                    scope_donors["R3"].append(donor)
                    scope_features["R3"].update(features)
                if distance == 1:
                    scope_donors["D1"].append(donor)
                    scope_features["D1"].update(features)

            scope_view = {
                scope: {
                    "features": tuple(
                        feature for feature in FEATURES if feature in scope_features[scope]
                    ),
                    "donors": tuple(scope_donors[scope]),
                    "blocked_family_donors": tuple(scope_blocked[scope]),
                    "blocked_source_composed_donors": tuple(
                        scope_source_blocked[scope]
                    ),
                    "eligible_donor_positions": len(scope_donors[scope]),
                    "family_blocked_positions": len(scope_blocked[scope]),
                    "source_composed_blocked_positions": len(
                        scope_source_blocked[scope]
                    ),
                }
                for scope in SCOPES
            }
            views[radius] = {
                "target_surface": target_surface,
                "family_radius": radius,
                "scope": scope_view,
                "line_gate_counts": dict(sorted(gate_counts.items())),
            }

        output.append({**source, "family_views": views})

    assert len(output) == 404
    return output


def build_family_ablation(
    occurrence_atlas: Sequence[Mapping[str, object]],
    environment: Mapping[str, object],
    source_composed_surfaces: frozenset[str],
) -> list[dict[str, object]]:
    """Aggregate feature presence and donor exposure for every ablation."""

    context = environment["context"]
    reader_exact_surfaces = {
        str(token["eva"])
        for locus, line in context.by_line.items()
        for token in line
        if bool(context.exact[(locus, int(token["token_index"]))])
    }
    rows: list[dict[str, object]] = []

    for target in TARGET_FORMS:
        occurrences = [row for row in occurrence_atlas if row["surface"] == target]
        assert len(occurrences) == EXPECTED_TARGET_COUNTS[target]
        for radius in ABLATION_RADII:
            blocked_surfaces = tuple(
                sorted(
                    surface
                    for surface in reader_exact_surfaces
                    if levenshtein(surface, target) <= radius
                )
            )
            assert target in blocked_surfaces
            for scope in SCOPES:
                feature_occurrence_counts = {
                    feature: sum(
                        feature
                        in row["family_views"][radius]["scope"][scope]["features"]
                        for row in occurrences
                    )
                    for feature in FEATURES
                }
                donor_surface_counts: Counter[str] = Counter()
                blocked_surface_counts: Counter[str] = Counter()
                source_blocked_surface_counts: Counter[str] = Counter()
                eligible_positions = 0
                family_blocked_positions = 0
                source_composed_blocked_positions = 0
                feature_donor_counts: Counter[str] = Counter()
                for row in occurrences:
                    view = row["family_views"][radius]["scope"][scope]
                    donors = view["donors"]
                    blocked = view["blocked_family_donors"]
                    source_blocked = view["blocked_source_composed_donors"]
                    eligible_positions += len(donors)
                    family_blocked_positions += len(blocked)
                    source_composed_blocked_positions += len(source_blocked)
                    donor_surface_counts.update(str(donor["surface"]) for donor in donors)
                    blocked_surface_counts.update(str(donor["surface"]) for donor in blocked)
                    source_blocked_surface_counts.update(
                        str(donor["surface"]) for donor in source_blocked
                    )
                    for donor in donors:
                        feature_donor_counts.update(str(item) for item in donor["features"])

                rows.append(
                    {
                        "target_surface": target,
                        "family_radius": radius,
                        "scope": scope,
                        "target_occurrences": len(occurrences),
                        "global_family_blocked_surface_count": len(blocked_surfaces),
                        "global_family_blocked_surfaces": blocked_surfaces,
                        "global_source_composed_blocked_surface_count": len(
                            source_composed_surfaces
                        ),
                        "eligible_donor_positions": eligible_positions,
                        "family_blocked_donor_positions": family_blocked_positions,
                        "source_composed_blocked_donor_positions": (
                            source_composed_blocked_positions
                        ),
                        "eligible_unique_donor_surfaces": len(donor_surface_counts),
                        "feature_occurrence_counts": feature_occurrence_counts,
                        "feature_donor_counts": {
                            feature: feature_donor_counts[feature]
                            for feature in FEATURES
                        },
                        "donor_surface_counts": dict(sorted(donor_surface_counts.items())),
                        "blocked_surface_counts": dict(
                            sorted(blocked_surface_counts.items())
                        ),
                        "source_composed_blocked_surface_counts": dict(
                            sorted(source_blocked_surface_counts.items())
                        ),
                    }
                )

    assert len(rows) == len(TARGET_FORMS) * len(ABLATION_RADII) * len(SCOPES)
    lookup = {
        (str(row["target_surface"]), int(row["family_radius"]), str(row["scope"])): row
        for row in rows
    }
    for key, expected in EXPECTED_CORRECTED_D1_DRY_MOIST.items():
        target, radius = key
        counts = lookup[target, radius, "D1"]["feature_occurrence_counts"]
        observed = (int(counts["DRY"]), int(counts["MOIST"]))
        assert observed == expected, (
            f"D1 dry/moist ablation changed for {target} radius {radius}: "
            f"{observed} != {expected}"
        )
    for key, expected in EXPECTED_GDT754_BLOCKED_DONOR_POSITIONS.items():
        target, scope = key
        # The global provenance gate precedes family distance, so its exposure
        # count must be identical at every edit-radius ablation.
        observed_by_radius = {
            int(lookup[target, radius, scope]["source_composed_blocked_donor_positions"])
            for radius in ABLATION_RADII
        }
        assert observed_by_radius == {expected}, (
            f"GDT754 donor block changed for {target} {scope}: "
            f"{sorted(observed_by_radius)} != {[expected]}"
        )
    return rows


def build_multi_anchor_lines(
    environment: Mapping[str, object],
) -> list[dict[str, object]]:
    """Return lines containing at least two distinct reader-exact anchors."""

    context = environment["context"]
    line_meta = environment["line_meta"]
    rows: list[dict[str, object]] = []
    for locus, line in sorted(context.by_line.items()):
        all_target_tokens: list[dict[str, object]] = []
        exact_anchor_tokens: list[dict[str, object]] = []
        for index, token in enumerate(line):
            surface = str(token["eva"])
            if surface not in TARGET_FORM_SET:
                continue
            exact = int(bool(context.exact[(locus, int(token["token_index"]))]))
            item = {
                "surface": surface,
                "ordinal": index + 1,
                "token_index": int(token["token_index"]),
                "reader_exact": exact,
            }
            all_target_tokens.append(item)
            if exact:
                exact_anchor_tokens.append(item)

        distinct_exact = {str(item["surface"]) for item in exact_anchor_tokens}
        if len(distinct_exact) < 2:
            continue
        page = str(line[0]["page"])
        assert not page.startswith(FORBIDDEN_PAGE_PREFIXES)
        meta = line_meta[locus]
        rows.append(
            {
                "multi_anchor_line_id": "",
                "page": page,
                "physical_folio": _physical_folio(page),
                "locus": locus,
                "line_number": int(meta["line_number"]),
                "section": str(line[0]["section"]),
                "language": str(line[0]["language"]),
                "hand": str(line[0]["hand"]),
                "paragraph_start_line": int(meta["paragraph_start"]),
                "paragraph_end_line": int(meta["paragraph_end"]),
                "line_token_count": len(line),
                "distinct_exact_anchor_count": len(distinct_exact),
                "exact_anchor_occurrence_count": len(exact_anchor_tokens),
                "exact_anchor_surfaces": tuple(
                    str(item["surface"]) for item in exact_anchor_tokens
                ),
                "exact_anchor_ordinals": tuple(
                    int(item["ordinal"]) for item in exact_anchor_tokens
                ),
                "exact_anchor_flags": tuple(
                    int(item["reader_exact"]) for item in exact_anchor_tokens
                ),
                "exact_anchor_counts": dict(
                    sorted(Counter(str(item["surface"]) for item in exact_anchor_tokens).items())
                ),
                "all_target_tokens": tuple(all_target_tokens),
                "exact_anchor_tokens": tuple(exact_anchor_tokens),
                "written_line_eva": " ".join(str(item["eva"]) for item in line),
            }
        )

    rows.sort(key=lambda row: (str(row["page"]), int(row["line_number"])))
    for number, row in enumerate(rows, 1):
        row["multi_anchor_line_id"] = f"G768-M{number:02d}"
    assert len(rows) == 33, "GDT768 multi-anchor line count changed"
    assert len({str(row["page"]) for row in rows}) == 26, (
        "GDT768 multi-anchor page count changed"
    )
    f17 = [row for row in rows if row["locus"] == "f17r.5"]
    assert len(f17) == 1
    assert f17[0]["exact_anchor_surfaces"] == ("cthy", "chor", "shor", "dair")
    return rows


def build_pair_summary(
    environment: Mapping[str, object],
) -> list[dict[str, object]]:
    """Summarize all fifteen unordered cross-anchor pairs."""

    context = environment["context"]
    per_pair: dict[tuple[str, str], dict[str, object]] = {}
    for first_index, first in enumerate(TARGET_FORMS):
        for second in TARGET_FORMS[first_index + 1 :]:
            per_pair[first, second] = {
                "loci": set(),
                "pages": set(),
                "occurrence_pairs": 0,
                "direct_pairs": 0,
                "first_before_second": 0,
                "second_before_first": 0,
            }

    for locus, line in sorted(context.by_line.items()):
        by_surface: defaultdict[str, list[int]] = defaultdict(list)
        for ordinal, token in enumerate(line, 1):
            surface = str(token["eva"])
            if surface not in TARGET_FORM_SET:
                continue
            if bool(context.exact[(locus, int(token["token_index"]))]):
                by_surface[surface].append(ordinal)
        page = str(line[0]["page"])
        for pair, record in per_pair.items():
            first, second = pair
            if first not in by_surface or second not in by_surface:
                continue
            record["loci"].add(locus)
            record["pages"].add(page)
            for first_ordinal in by_surface[first]:
                for second_ordinal in by_surface[second]:
                    record["occurrence_pairs"] += 1
                    record["direct_pairs"] += int(
                        abs(first_ordinal - second_ordinal) == 1
                    )
                    if first_ordinal < second_ordinal:
                        record["first_before_second"] += 1
                    else:
                        record["second_before_first"] += 1

    rows: list[dict[str, object]] = []
    for number, pair in enumerate(per_pair, 1):
        first, second = pair
        record = per_pair[pair]
        rows.append(
            {
                "pair_id": f"G768-P{number:02d}",
                "first_surface": first,
                "second_surface": second,
                "line_count": len(record["loci"]),
                "page_count": len(record["pages"]),
                "occurrence_pair_count": int(record["occurrence_pairs"]),
                "direct_pair_count": int(record["direct_pairs"]),
                "first_before_second": int(record["first_before_second"]),
                "second_before_first": int(record["second_before_first"]),
                "loci": tuple(sorted(str(item) for item in record["loci"])),
                "pages": tuple(sorted(str(item) for item in record["pages"])),
            }
        )

    assert len(rows) == 15
    lookup = {
        frozenset((str(row["first_surface"]), str(row["second_surface"]))): row
        for row in rows
    }
    for pair, expected in EXPECTED_PAIR_COUNTS.items():
        row = lookup[frozenset(pair)]
        observed = (
            int(row["line_count"]),
            int(row["page_count"]),
            int(row["direct_pair_count"]),
        )
        assert observed == expected, f"pair census changed for {pair}: {observed}"
    return rows


def build_role_geometry(
    occurrence_atlas: Sequence[Mapping[str, object]],
    multi_anchor_lines: Sequence[Mapping[str, object]],
    environment: Mapping[str, object],
    g764: ModuleType,
) -> list[dict[str, object]]:
    """Aggregate line/paragraph placement and current whole-role geometry."""

    multi_loci = {str(row["locus"]) for row in multi_anchor_lines}
    rows: list[dict[str, object]] = []
    for surface in TARGET_FORMS:
        selected = [row for row in occurrence_atlas if row["surface"] == surface]
        positions = Counter(str(row["line_position"]) for row in selected)
        sections = Counter(str(row["section"]) for row in selected)
        languages = Counter(str(row["language"]) for row in selected)
        hands = Counter(str(row["hand"]) for row in selected)
        target_roles: Counter[str] = Counter()
        target_axes: Counter[str] = Counter()
        for row in selected:
            target_slot = g764.slot(
                environment, str(row["locus"]), int(row["ordinal"])
            )
            assert int(target_slot["reader_exact"]) == 1
            assert str(target_slot["surface"]) == surface
            target_roles.update(_pipe_set(target_slot["roles"]))
            target_axes.update(_pipe_set(target_slot["axes"]))

        rows.append(
            {
                "surface": surface,
                "reader_exact_occurrences": len(selected),
                "pages": len({str(row["page"]) for row in selected}),
                "physical_folios": len(
                    {str(row["physical_folio"]) for row in selected}
                ),
                "loci": len({str(row["locus"]) for row in selected}),
                "line_first": sum(int(row["ordinal"]) == 1 for row in selected),
                "line_last": sum(
                    int(row["ordinal"]) == int(row["line_token_count"])
                    for row in selected
                ),
                "line_position_counts": dict(sorted(positions.items())),
                "paragraph_start_line": sum(
                    int(row["paragraph_start_line"]) for row in selected
                ),
                "paragraph_end_line": sum(
                    int(row["paragraph_end_line"]) for row in selected
                ),
                "true_paragraph_opener": sum(
                    int(row["true_paragraph_opener"]) for row in selected
                ),
                "true_paragraph_closer": sum(
                    int(row["true_paragraph_closer"]) for row in selected
                ),
                "multi_anchor_line_occurrences": sum(
                    str(row["locus"]) in multi_loci for row in selected
                ),
                "multi_anchor_loci": len(
                    {str(row["locus"]) for row in selected if str(row["locus"]) in multi_loci}
                ),
                "mean_ordinal": sum(int(row["ordinal"]) for row in selected)
                / len(selected),
                "mean_normalized_line_position": sum(
                    float(row["normalized_line_position"]) for row in selected
                )
                / len(selected),
                "section_counts": dict(sorted(sections.items())),
                "language_counts": dict(sorted(languages.items())),
                "hand_counts": dict(sorted(hands.items())),
                "current_target_role_occurrence_counts": dict(
                    sorted(target_roles.items())
                ),
                "current_target_axis_occurrence_counts": dict(
                    sorted(target_axes.items())
                ),
            }
        )

    lookup = {str(row["surface"]): row for row in rows}
    assert (
        lookup["shor"]["line_first"],
        lookup["shor"]["paragraph_start_line"],
    ) == (16, 26), "shor role geometry changed"
    assert (
        lookup["chor"]["line_first"],
        lookup["chor"]["paragraph_start_line"],
    ) == (10, 25), "chor role geometry changed"
    return rows


def build_core_atlas(root: Path = ROOT) -> dict[str, object]:
    """Build all GDT768 core structures without writing any artifact."""

    g764, environment = load_guarded_environment(root)
    source_composed_surfaces = load_gdt754_source_composed_surfaces(root)
    targets = enumerate_exact_targets(environment)
    occurrence_atlas = build_occurrence_feature_atlas(
        environment, g764, targets, source_composed_surfaces
    )
    multi_anchor_lines = build_multi_anchor_lines(environment)
    pair_summary = build_pair_summary(environment)
    family_ablation = build_family_ablation(
        occurrence_atlas, environment, source_composed_surfaces
    )
    role_geometry = build_role_geometry(
        occurrence_atlas, multi_anchor_lines, environment, g764
    )

    assert all(
        str(donor["surface"]) not in source_composed_surfaces
        for row in occurrence_atlas
        for radius in ABLATION_RADII
        for scope in SCOPES
        for donor in row["family_views"][radius]["scope"][scope]["donors"]
    ), "a GDT754 source-composed surface escaped the donor gate"

    source_blocked_target_contexts = sum(
        len(row["family_views"][0]["scope"]["LINE"]["blocked_source_composed_donors"])
        for row in occurrence_atlas
    )
    unique_source_blocked_positions = {
        (
            str(row["locus"]),
            int(donor["ordinal"]),
            str(donor["surface"]),
        )
        for row in occurrence_atlas
        for donor in row["family_views"][0]["scope"]["LINE"][
            "blocked_source_composed_donors"
        ]
    }
    assert source_blocked_target_contexts == 54
    assert len(unique_source_blocked_positions) == 48
    assert len({surface for _, _, surface in unique_source_blocked_positions}) == 27

    guard = dict(environment["guard"])
    return {
        "occurrences": occurrence_atlas,
        "multi_anchor_lines": multi_anchor_lines,
        "pair_summary": pair_summary,
        "family_ablation": family_ablation,
        "role_geometry": role_geometry,
        "metadata": {
            "target_forms": TARGET_FORMS,
            "anchor_counts": dict(EXPECTED_TARGET_COUNTS),
            "target_occurrences": len(occurrence_atlas),
            "target_pages": len({str(row["page"]) for row in occurrence_atlas}),
            "target_loci": len({str(row["locus"]) for row in occurrence_atlas}),
            "multi_anchor_lines": len(multi_anchor_lines),
            "multi_anchor_pages": len(
                {str(row["page"]) for row in multi_anchor_lines}
            ),
            "features": FEATURES,
            "scopes": SCOPES,
            "family_ablation_radii": ABLATION_RADII,
            "family_rule": (
                "PER_TARGET_COMPLETE_SURFACE_LEVENSHTEIN_DISTANCE_GREATER_THAN_RADIUS"
            ),
            "donor_gate_order": (
                "READER_EXACT__GDT754_SOURCE_COMPOSED_BLOCK__CURRENT_CLEAN__"
                "PER_TARGET_EDIT_FAMILY_BLOCK__ELIGIBLE"
            ),
            "gdt754_source_composed_surface_count": len(
                source_composed_surfaces
            ),
            "gdt754_source_composed_target_context_exposures": (
                source_blocked_target_contexts
            ),
            "gdt754_source_composed_unique_target_line_positions": len(
                unique_source_blocked_positions
            ),
            "gdt754_source_composed_unique_target_line_surfaces": len(
                {surface for _, _, surface in unique_source_blocked_positions}
            ),
            "edit_distance_semantic_credit": 0,
            "component_export_credit": 0,
            "guard": guard,
            "f84_accessed": False,
            "f84r_accessed": False,
        },
    }


__all__ = (
    "ABLATION_RADII",
    "FEATURES",
    "SCOPES",
    "TARGET_FORMS",
    "build_core_atlas",
    "build_family_ablation",
    "build_multi_anchor_lines",
    "build_occurrence_feature_atlas",
    "build_pair_summary",
    "build_role_geometry",
    "donor_features",
    "enumerate_exact_targets",
    "levenshtein",
    "load_gdt754_source_composed_surfaces",
    "load_guarded_environment",
)
