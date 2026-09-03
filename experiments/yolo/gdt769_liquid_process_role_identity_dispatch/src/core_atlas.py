#!/usr/bin/env python3
"""Read-only structural core for GDT769.

The module follows five complete EVA wholes through the already admitted
GDT764 guarded cache.  It exposes exact target contexts, explicit control
spans, role geometry, direct structural signatures, and leave-one-locus-out
rows.  It assigns no meaning, writes no artifact, and never opens an image or
transcription.  ``f84`` and ``f84r`` remain rejected by the inherited guard.

GDT759's three reader-exact ``ols`` preparation/value spans are exposed as a
dedicated ``VALUE`` control.  They are deliberately not merged with GDT764's
``X+daiin`` ``BOUNDED_VALUE`` field and license no ``daiin ckhy`` relation.

Semantic donors are admitted only after four independent exclusions: all five
targets, the 172 GDT754 source-composed wholes, the 80 explicitly quarantined
GDT737 literal-head cards, and every complete surface within Levenshtein
distance two of *any* panel target.  Per-current-target ED2 counts survive only
as a sensitivity diagnostic.  The larger 273-form GDT737 held cohort is
reported as provenance only; held status alone is not a semantic defect.
"""

from __future__ import annotations

import csv
import importlib.util
import sys
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path
from types import ModuleType
from typing import Iterable, Mapping, Sequence

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
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
G737_HELD_REL = Path(
    "experiments/yolo/gdt737_held_body_record_role_transfer/"
    "artifacts/HELD_273_FORM_ROLE_BRIDGE.tsv"
)
G737_QUARANTINE_REL = Path(
    "experiments/yolo/gdt737_held_body_record_role_transfer/"
    "artifacts/V99R7_HELD_WHOLE_QUARANTINE.tsv"
)
G759_AMOUNT_REL = Path(
    "experiments/yolo/gdt759_quantity_part_state_construction_atlas/"
    "artifacts/QUANTITY_96_EXACT_PAIR_ATLAS.tsv"
)
G759_CONSTRUCTION_REL = Path(
    "experiments/yolo/gdt759_quantity_part_state_construction_atlas/"
    "artifacts/EXACT_122_CONSTRUCTION_SPAN_ATLAS.tsv"
)
G764_BOUNDED_REL = Path(
    "experiments/yolo/gdt764_bounded_value_field_dispatch/"
    "artifacts/X_DAIIN_9_EXACT_BIGRAM_ATLAS.tsv"
)

TARGET_FORMS = ("ol", "ckhy", "pcheey", "ols", "otar")
TARGET_FORM_SET = frozenset(TARGET_FORMS)
STATE_ANCHORS = {
    "cheo": "DRY",
    "cheor": "DRY",
    "sheo": "MOIST",
    "sheor": "MOIST",
}
OLY_ANCHOR = "oly"
AMOUNT_HEADS = frozenset({"s", "or", "ar"})
AMOUNT_VALUES = frozenset({"an", "ain", "aiin", "aiiin"})
BOUNDED_X_FORMS = frozenset(
    {"qoty", "dal", "qopchdy", "ofchy", "oteody", "chofol"}
)
SCOPES = ("D1", "R2", "LINE")
FAMILY_EDIT_DISTANCE = 2
FORBIDDEN_PAGE_PREFIXES = ("f84",)

SIGNATURE_CHANNELS = (
    "AMOUNT",
    "VALUE",
    "STATE_DRY",
    "STATE_MOIST",
    "PROCESS",
    "CLOSE",
    "OLY",
    "BOUNDED_VALUE",
)
FEATURES = (
    "DRY",
    "MOIST",
    "HOT",
    "COLD",
    "STAGE",
    "MATERIAL",
    "PREPARATION",
    "VALUE_AMOUNT",
    "PROCESS",
    "PASS",
    "CLOSE",
    "H1",
    "H2",
    "H3",
    "H4",
    "STATE_DRY_ANCHOR",
    "STATE_MOIST_ANCHOR",
    "OLY_ANCHOR",
    "AMOUNT_SPAN_MEMBER",
    "VALUE_SPAN_MEMBER",
    "BOUNDED_VALUE_SPAN_MEMBER",
)

STAGE_AXES = frozenset(
    {"BEGIN_STAGE", "MIDDLE_STAGE", "END_STAGE", "LEVEL_I", "LEVEL_II", "LEVEL_III"}
)
VALUE_ROLES = frozenset({"SCALAR_VALUE", "AMOUNT_VALUE"})
VALUE_AXES = frozenset({"AMOUNT", "PART"})

EXPECTED_TARGET_COUNTS = {
    "ol": (463, 376),
    "ckhy": (34, 25),
    "pcheey": (3, 3),
    "ols": (17, 12),
    "otar": (123, 110),
}
EXPECTED_ANCHOR_EXACT_COUNTS = {
    "oly": 48,
    "cheo": 36,
    "cheor": 56,
    "sheo": 28,
    "sheor": 31,
}
EXPECTED_DIRECT_SIGNATURE_COUNTS = {
    "ol": {
        "AMOUNT": 9, "VALUE": 0, "STATE_DRY": 4, "STATE_MOIST": 2, "PROCESS": 8,
        "CLOSE": 12, "OLY": 2, "BOUNDED_VALUE": 0,
    },
    "ckhy": {
        "AMOUNT": 0, "VALUE": 0, "STATE_DRY": 0, "STATE_MOIST": 2, "PROCESS": 0,
        "CLOSE": 0, "OLY": 0, "BOUNDED_VALUE": 0,
    },
    "pcheey": {
        "AMOUNT": 0, "VALUE": 0, "STATE_DRY": 0, "STATE_MOIST": 2, "PROCESS": 0,
        "CLOSE": 0, "OLY": 0, "BOUNDED_VALUE": 2,
    },
    "ols": {
        "AMOUNT": 0, "VALUE": 3, "STATE_DRY": 1, "STATE_MOIST": 0, "PROCESS": 0,
        "CLOSE": 0, "OLY": 0, "BOUNDED_VALUE": 0,
    },
    "otar": {
        "AMOUNT": 4, "VALUE": 0, "STATE_DRY": 0, "STATE_MOIST": 0, "PROCESS": 2,
        "CLOSE": 4, "OLY": 1, "BOUNDED_VALUE": 1,
    },
}
EXPECTED_FAMILY_SURFACE_COUNTS = {
    "ol": 295,
    "ckhy": 131,
    "pcheey": 172,
    "ols": 192,
    "otar": 242,
}
EXPECTED_PRIMARY_GATE_TOTALS = {
    "D1": {
        "ELIGIBLE": 446,
        "GDT737_LITERAL_HEAD_QUARANTINE_BLOCK": 11,
        "GDT754_SOURCE_COMPOSED_BLOCK": 17,
        "NONEXACT": 195,
        "TARGET_FAMILY_ED2_BLOCK": 284,
        "TARGET_PANEL_BLOCK": 24,
    },
    "R2": {
        "ELIGIBLE": 838,
        "GDT737_LITERAL_HEAD_QUARANTINE_BLOCK": 14,
        "GDT754_SOURCE_COMPOSED_BLOCK": 26,
        "NONEXACT": 382,
        "TARGET_FAMILY_ED2_BLOCK": 506,
        "TARGET_PANEL_BLOCK": 50,
    },
    "LINE": {
        "ELIGIBLE": 2101,
        "GDT737_LITERAL_HEAD_QUARANTINE_BLOCK": 47,
        "GDT754_SOURCE_COMPOSED_BLOCK": 84,
        "NONEXACT": 1122,
        "TARGET_FAMILY_ED2_BLOCK": 1262,
        "TARGET_PANEL_BLOCK": 140,
    },
}


def _load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _pipe_set(value: object) -> set[str]:
    return {
        item
        for item in str(value).split("|")
        if item and item not in {"NONE", "OPEN"}
    }


def _line_position(ordinal: int, token_count: int) -> str:
    if token_count == 1:
        return "SINGLE"
    if ordinal == 1:
        return "FIRST"
    if ordinal == token_count:
        return "LAST"
    return "MIDDLE"


def _physical_folio(page: str) -> str:
    for suffix in (
        "r1", "r2", "r3", "r4", "r5", "r6",
        "v1", "v2", "v3", "v4", "v5", "v6", "r", "v",
    ):
        if page.endswith(suffix):
            return page[: -len(suffix)]
    return page


@lru_cache(maxsize=None)
def levenshtein(first: str, second: str) -> int:
    """Return ordinary character Levenshtein distance."""

    if first == second:
        return 0
    if not first:
        return len(second)
    if not second:
        return len(first)
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


def load_guarded_environment(root: Path = ROOT) -> tuple[ModuleType, dict[str, object]]:
    """Load GDT764's already admitted semantic environment and freeze its guard."""

    g764 = _load_module("gdt764_for_gdt769_core", root / G764_RUN_REL)
    environment = g764.semantic_environment()
    assert dict(environment["guard"]) == {
        "selected": 4137,
        "skipped_forbidden": 98,
        "skipped_not_allowed": 1150,
    }, "guarded cache universe changed"
    return g764, environment


def load_gdt754_source_composed_surfaces(root: Path = ROOT) -> frozenset[str]:
    rows = _read_tsv(root / G754_INVENTORY_REL)
    surfaces = frozenset(row["surface"] for row in rows)
    assert len(rows) == 172 and len(surfaces) == 172
    assert not surfaces & TARGET_FORM_SET
    return surfaces


def load_gdt737_provenance_blocks(root: Path = ROOT) -> dict[str, object]:
    """Load held provenance and block only explicit literal-head quarantines."""

    held_path = root / G737_HELD_REL
    quarantine_path = root / G737_QUARANTINE_REL
    if not held_path.is_file() or not quarantine_path.is_file():
        return {
            "available": False,
            "held_cohort_surfaces": frozenset(),
            "quarantined_surfaces": frozenset(),
            "retained_surfaces": frozenset(),
        }
    held_rows = _read_tsv(held_path)
    quarantine_rows = _read_tsv(quarantine_path)
    held = frozenset(row["form"] for row in held_rows)
    quarantined = frozenset(
        row["surface"]
        for row in quarantine_rows
        if row["gdt737_decision"] == "QUARANTINE_RETIRED_HEAD_NOUN_DERIVATION"
    )
    retained = frozenset(
        row["surface"]
        for row in quarantine_rows
        if row["gdt737_decision"] == "RETAIN_CURRENT_EXACT_WHOLE_WORKING_DEFAULT"
    )
    assert len(held_rows) == len(held) == 273
    assert len(quarantined) == 80
    assert len(retained) == 2
    assert quarantined | retained <= held
    assert not TARGET_FORM_SET & quarantined
    return {
        "available": True,
        "held_cohort_surfaces": held,
        "quarantined_surfaces": quarantined,
        "retained_surfaces": retained,
    }


def _verify_exact_position(
    environment: Mapping[str, object], locus: str, ordinal: int, surface: str
) -> None:
    context = environment["context"]
    assert locus in context.by_line, f"control locus absent from guarded cache: {locus}"
    line = context.by_line[locus]
    assert 1 <= ordinal <= len(line), f"control ordinal outside line: {locus}@{ordinal}"
    token = line[ordinal - 1]
    assert str(token["eva"]) == surface, f"control surface mismatch: {locus}@{ordinal}"
    assert bool(context.exact[(locus, int(token["token_index"]))]), (
        f"control is not reader exact: {locus}@{ordinal}"
    )
    assert not str(token["page"]).startswith(FORBIDDEN_PAGE_PREFIXES)


def load_control_spans(
    environment: Mapping[str, object], root: Path = ROOT
) -> dict[str, object]:
    """Load and rebind the exact GDT759/GDT764 structural controls."""

    amount_rows = _read_tsv(root / G759_AMOUNT_REL)
    assert len(amount_rows) == 96
    amount_spans: list[dict[str, object]] = []
    for row in amount_rows:
        locus = row["locus"]
        left_ordinal = int(row["left_token_ordinal"])
        right_ordinal = int(row["right_token_ordinal"])
        assert right_ordinal == left_ordinal + 1
        assert row["left_surface"] in AMOUNT_HEADS
        assert row["right_surface"] in AMOUNT_VALUES
        assert row["reader_exact_left"] == row["reader_exact_right"] == "1"
        _verify_exact_position(environment, locus, left_ordinal, row["left_surface"])
        _verify_exact_position(environment, locus, right_ordinal, row["right_surface"])
        amount_spans.append(
            {
                "span_id": row["construction_span_id"],
                "page": row["page"],
                "locus": locus,
                "head_ordinal": left_ordinal,
                "head_surface": row["left_surface"],
                "value_ordinal": right_ordinal,
                "value_surface": row["right_surface"],
                "value_label": row["value_label"],
                "written_span_eva": row["exact_span_eva"],
                "reader_exact": 1,
            }
        )

    construction_rows = _read_tsv(root / G759_CONSTRUCTION_REL)
    value_rows = [
        row for row in construction_rows if row["family"] == "PREPARATION_VALUE"
    ]
    assert len(construction_rows) == 122 and len(value_rows) == 3
    assert Counter(
        (row["left_surface"], row["right_surface"]) for row in value_rows
    ) == Counter({("ols", "aiin"): 2, ("ols", "aiiin"): 1})
    value_spans: list[dict[str, object]] = []
    for row in value_rows:
        locus = row["locus"]
        preparation_ordinal = int(row["left_token_ordinal"])
        value_ordinal = int(row["right_token_ordinal"])
        assert value_ordinal == preparation_ordinal + 1
        assert row["left_surface"] == "ols"
        assert row["right_surface"] in AMOUNT_VALUES
        assert row["reader_exact_left"] == row["reader_exact_right"] == "1"
        assert row["claim_scope"] == "EXACT_OBSERVED_SPAN_ONLY"
        assert row["confirmed_plaintext"] == row["component_export_credit"] == "0"
        _verify_exact_position(
            environment, locus, preparation_ordinal, row["left_surface"]
        )
        _verify_exact_position(environment, locus, value_ordinal, row["right_surface"])
        value_spans.append(
            {
                "span_id": row["construction_span_id"],
                "page": row["page"],
                "locus": locus,
                "preparation_ordinal": preparation_ordinal,
                "preparation_surface": row["left_surface"],
                "value_ordinal": value_ordinal,
                "value_surface": row["right_surface"],
                "value_label": row["value_label"],
                "written_span_eva": row["exact_span_eva"],
                "reader_exact": 1,
                "semantic_identity_credit": 0,
                "component_export_credit": 0,
            }
        )

    bounded_rows = _read_tsv(root / G764_BOUNDED_REL)
    assert len(bounded_rows) == 9
    bounded_spans: list[dict[str, object]] = []
    for row in bounded_rows:
        locus = row["locus"]
        x_ordinal = int(row["x_ordinal"])
        value_ordinal = int(row["daiin_ordinal"])
        assert value_ordinal == x_ordinal + 1
        assert row["x_surface"] in BOUNDED_X_FORMS
        assert row["daiin_fixed_value"] == "III"
        _verify_exact_position(environment, locus, x_ordinal, row["x_surface"])
        _verify_exact_position(environment, locus, value_ordinal, "daiin")
        bounded_spans.append(
            {
                "span_id": row["x_daiin_id"],
                "page": row["page"],
                "locus": locus,
                "x_ordinal": x_ordinal,
                "x_surface": row["x_surface"],
                "value_ordinal": value_ordinal,
                "value_surface": "daiin",
                "selected_local_dispatch": row["selected_local_dispatch"],
                "written_span_eva": row["written_pattern_eva"],
                "reader_exact": 1,
            }
        )
    assert not any(
        span["preparation_surface"] == "ckhy" or span["value_surface"] == "ckhy"
        for span in value_spans
    ), "unlicensed daiin-ckhy relation entered the GDT759 VALUE control"
    return {
        "amount_spans": amount_spans,
        "value_spans": value_spans,
        "bounded_value_spans": bounded_spans,
    }


def enumerate_control_anchors(
    environment: Mapping[str, object],
) -> list[dict[str, object]]:
    """Enumerate exact state and oly controls without treating them as targets."""

    context = environment["context"]
    line_meta = environment["line_meta"]
    control_forms = frozenset((*STATE_ANCHORS, OLY_ANCHOR))
    rows: list[dict[str, object]] = []
    for locus, line in sorted(context.by_line.items()):
        for index, token in enumerate(line):
            surface = str(token["eva"])
            if surface not in control_forms:
                continue
            if not bool(context.exact[(locus, int(token["token_index"]))]):
                continue
            ordinal = index + 1
            page = str(token["page"])
            assert not page.startswith(FORBIDDEN_PAGE_PREFIXES)
            rows.append(
                {
                    "anchor_occurrence_id": "",
                    "anchor_class": (
                        f"STATE_{STATE_ANCHORS[surface]}"
                        if surface in STATE_ANCHORS
                        else "OLY_PROCESS_CLOSE"
                    ),
                    "surface": surface,
                    "page": page,
                    "physical_folio": _physical_folio(page),
                    "locus": locus,
                    "line_number": int(line_meta[locus]["line_number"]),
                    "ordinal": ordinal,
                    "token_index": int(token["token_index"]),
                    "line_token_count": len(line),
                    "written_line_eva": " ".join(str(item["eva"]) for item in line),
                    "reader_exact": 1,
                    "semantic_identity_credit": 0,
                    "component_export_credit": 0,
                }
            )
    rows.sort(
        key=lambda row: (
            str(row["page"]), int(row["line_number"]), int(row["ordinal"]), str(row["surface"])
        )
    )
    for number, row in enumerate(rows, 1):
        row["anchor_occurrence_id"] = f"G769-A{number:04d}"
    counts = Counter(str(row["surface"]) for row in rows)
    assert counts == Counter(EXPECTED_ANCHOR_EXACT_COUNTS)
    assert len(rows) == 199
    return rows


def enumerate_raw_targets(
    environment: Mapping[str, object],
) -> list[dict[str, object]]:
    """Enumerate every guarded-cache target token and retain its exact flag."""

    context = environment["context"]
    line_meta = environment["line_meta"]
    rows: list[dict[str, object]] = []
    for locus, line in sorted(context.by_line.items()):
        for index, token in enumerate(line):
            surface = str(token["eva"])
            if surface not in TARGET_FORM_SET:
                continue
            ordinal = index + 1
            page = str(token["page"])
            assert not page.startswith(FORBIDDEN_PAGE_PREFIXES)
            exact = int(bool(context.exact[(locus, int(token["token_index"]))]))
            rows.append(
                {
                    "raw_occurrence_id": "",
                    "target_occurrence_id": "",
                    "surface": surface,
                    "page": page,
                    "physical_folio": _physical_folio(page),
                    "locus": locus,
                    "line_number": int(line_meta[locus]["line_number"]),
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
                    "paragraph_start_line": int(line_meta[locus]["paragraph_start"]),
                    "paragraph_end_line": int(line_meta[locus]["paragraph_end"]),
                    "true_paragraph_opener": int(
                        ordinal == 1 and int(line_meta[locus]["paragraph_start"]) == 1
                    ),
                    "true_paragraph_closer": int(
                        ordinal == len(line) and int(line_meta[locus]["paragraph_end"]) == 1
                    ),
                    "reader_exact": exact,
                    "written_line_eva": " ".join(str(item["eva"]) for item in line),
                }
            )
    rows.sort(
        key=lambda row: (
            str(row["page"]), int(row["line_number"]), int(row["ordinal"]), str(row["surface"])
        )
    )
    exact_number = 0
    for raw_number, row in enumerate(rows, 1):
        row["raw_occurrence_id"] = f"G769-R{raw_number:04d}"
        if int(row["reader_exact"]):
            exact_number += 1
            row["target_occurrence_id"] = f"G769-T{exact_number:04d}"
    counts = {
        target: (
            sum(str(row["surface"]) == target for row in rows),
            sum(str(row["surface"]) == target and int(row["reader_exact"]) for row in rows),
        )
        for target in TARGET_FORMS
    }
    assert counts == EXPECTED_TARGET_COUNTS, f"target census changed: {counts}"
    assert len(rows) == 640 and exact_number == 526
    return rows


def build_control_position_maps(
    controls: Mapping[str, object],
) -> dict[str, dict[tuple[str, int], tuple[dict[str, object], ...]]]:
    amount: defaultdict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    value: defaultdict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    bounded: defaultdict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for span in controls["amount_spans"]:
        for role, ordinal_key in (("HEAD", "head_ordinal"), ("VALUE", "value_ordinal")):
            amount[str(span["locus"]), int(span[ordinal_key])].append(
                {**span, "member_role": role}
            )
    for span in controls["value_spans"]:
        for role, ordinal_key in (
            ("PREPARATION", "preparation_ordinal"),
            ("VALUE", "value_ordinal"),
        ):
            value[str(span["locus"]), int(span[ordinal_key])].append(
                {**span, "member_role": role}
            )
    for span in controls["bounded_value_spans"]:
        for role, ordinal_key in (("X", "x_ordinal"), ("VALUE", "value_ordinal")):
            bounded[str(span["locus"]), int(span[ordinal_key])].append(
                {**span, "member_role": role}
            )
    return {
        "amount": {key: tuple(value) for key, value in amount.items()},
        "value": {key: tuple(items) for key, items in value.items()},
        "bounded": {key: tuple(value) for key, value in bounded.items()},
    }


def build_block_registry(
    environment: Mapping[str, object],
    gdt754_surfaces: frozenset[str],
    gdt737: Mapping[str, object],
) -> dict[str, object]:
    """Freeze global and target-specific donor exclusions."""

    context = environment["context"]
    guarded_surfaces = frozenset(
        str(token["eva"])
        for line in context.by_line.values()
        for token in line
    )
    gdt737_quarantined = frozenset(gdt737["quarantined_surfaces"])
    base = TARGET_FORM_SET | gdt754_surfaces | gdt737_quarantined
    family_by_target = {
        target: frozenset(
            surface
            for surface in guarded_surfaces
            if levenshtein(surface, target) <= FAMILY_EDIT_DISTANCE
        )
        for target in TARGET_FORMS
    }
    family_union = frozenset().union(*family_by_target.values())
    return {
        "guarded_surfaces": guarded_surfaces,
        "target_panel": TARGET_FORM_SET,
        "gdt754": gdt754_surfaces,
        "gdt737_quarantined": gdt737_quarantined,
        "gdt737_held_cohort": frozenset(gdt737["held_cohort_surfaces"]),
        "base_global_block": frozenset(base),
        "family_by_target": family_by_target,
        "family_union": family_union,
        "full_block_by_target": {
            target: frozenset(base | family_union) for target in TARGET_FORMS
        },
        "per_current_target_sensitivity_block": {
            target: frozenset(base | family_by_target[target]) for target in TARGET_FORMS
        },
    }


def _slot_features(
    surface: str,
    axes: set[str],
    roles: set[str],
    state_map: Mapping[str, object],
    locus: str,
    ordinal: int,
    position_maps: Mapping[str, Mapping[tuple[str, int], object]],
) -> tuple[str, ...]:
    features: set[str] = set()
    state = state_map.get(surface)
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
    if "MATERIAL" in axes:
        features.add("MATERIAL")
    if "PREPARATION" in axes:
        features.add("PREPARATION")
    if roles & VALUE_ROLES or axes & VALUE_AXES:
        features.add("VALUE_AMOUNT")
    if "PROCESS" in axes or "PROCESS_PASS" in roles:
        features.add("PROCESS")
    if "PASS" in axes or "PROCESS_PASS" in roles:
        features.add("PASS")
    if "CLOSE" in axes or "CLOSE" in roles:
        features.add("CLOSE")
    for head in ("H1", "H2", "H3", "H4"):
        if f"{head}_RECORD_FORM" in roles:
            features.add(head)
    if surface in STATE_ANCHORS:
        features.add(f"STATE_{STATE_ANCHORS[surface]}_ANCHOR")
    if surface == OLY_ANCHOR:
        features.add("OLY_ANCHOR")
    if (locus, ordinal) in position_maps["amount"]:
        features.add("AMOUNT_SPAN_MEMBER")
    if (locus, ordinal) in position_maps["value"]:
        features.add("VALUE_SPAN_MEMBER")
    if (locus, ordinal) in position_maps["bounded"]:
        features.add("BOUNDED_VALUE_SPAN_MEMBER")
    return tuple(feature for feature in FEATURES if feature in features)


def classify_donor(
    environment: Mapping[str, object],
    g764: ModuleType,
    blocks: Mapping[str, object],
    position_maps: Mapping[str, Mapping[tuple[str, int], object]],
    locus: str,
    ordinal: int,
    target_surface: str,
) -> tuple[dict[str, object] | None, str]:
    """Return a fully audited donor record and its gate status."""

    slot = g764.slot(environment, locus, ordinal)
    if str(slot["status"]) == "EDGE":
        return None, "EDGE"
    if not int(slot["reader_exact"]):
        return None, "NONEXACT"
    surface = str(slot["surface"])
    axes = _pipe_set(slot["axes"])
    roles = _pipe_set(slot["roles"])
    record: dict[str, object] = {
        "surface": surface,
        "ordinal": ordinal,
        "edit_distance_to_target": levenshtein(surface, target_surface),
        "axes": tuple(sorted(axes)),
        "roles": tuple(sorted(roles)),
        "semantic_source": str(slot["semantic_source"]),
        "current_clean": int(slot["clean"]),
        "held_cohort_member": int(surface in blocks["gdt737_held_cohort"]),
        "amount_control_memberships": tuple(
            item["span_id"] for item in position_maps["amount"].get((locus, ordinal), ())
        ),
        "value_control_memberships": tuple(
            item["span_id"] for item in position_maps["value"].get((locus, ordinal), ())
        ),
        "bounded_value_control_memberships": tuple(
            item["span_id"] for item in position_maps["bounded"].get((locus, ordinal), ())
        ),
    }
    if surface in blocks["target_panel"]:
        record["per_current_target_gate_status"] = "TARGET_PANEL_BLOCK"
        return record, "TARGET_PANEL_BLOCK"
    if surface in blocks["gdt754"]:
        record["per_current_target_gate_status"] = "GDT754_SOURCE_COMPOSED_BLOCK"
        return record, "GDT754_SOURCE_COMPOSED_BLOCK"
    if surface in blocks["gdt737_quarantined"]:
        record["per_current_target_gate_status"] = (
            "GDT737_LITERAL_HEAD_QUARANTINE_BLOCK"
        )
        return record, "GDT737_LITERAL_HEAD_QUARANTINE_BLOCK"
    if surface in blocks["family_union"]:
        if surface in blocks["family_by_target"][target_surface]:
            record["per_current_target_gate_status"] = "TARGET_FAMILY_ED2_BLOCK"
        elif not int(slot["clean"]):
            record["per_current_target_gate_status"] = "CURRENT_CLEAN_GATE_BLOCK"
        else:
            record["per_current_target_gate_status"] = "ELIGIBLE"
        return record, "TARGET_FAMILY_ED2_BLOCK"
    if not int(slot["clean"]):
        record["per_current_target_gate_status"] = "CURRENT_CLEAN_GATE_BLOCK"
        return record, "CURRENT_CLEAN_GATE_BLOCK"
    record["per_current_target_gate_status"] = "ELIGIBLE"
    record["features"] = _slot_features(
        surface,
        axes,
        roles,
        environment["state_map"],
        locus,
        ordinal,
        position_maps,
    )
    return record, "ELIGIBLE"


def _scope_names(distance: int) -> tuple[str, ...]:
    if distance == 1:
        return SCOPES
    if distance == 2:
        return ("R2", "LINE")
    return ("LINE",)


def _direct_signatures(
    occurrence: Mapping[str, object],
    environment: Mapping[str, object],
    g764: ModuleType,
    blocks: Mapping[str, object],
    position_maps: Mapping[str, Mapping[tuple[str, int], object]],
    controls: Mapping[str, object],
) -> dict[str, object]:
    locus = str(occurrence["locus"])
    target_ordinal = int(occurrence["ordinal"])
    target_surface = str(occurrence["surface"])
    line = environment["context"].by_line[locus]
    evidence: dict[str, list[dict[str, object]]] = {
        channel: [] for channel in SIGNATURE_CHANNELS
    }

    for neighbor_ordinal in (target_ordinal - 1, target_ordinal + 1):
        if not 1 <= neighbor_ordinal <= len(line):
            continue
        donor, gate = classify_donor(
            environment,
            g764,
            blocks,
            position_maps,
            locus,
            neighbor_ordinal,
            target_surface,
        )
        if donor is None:
            continue
        neighbor_surface = str(donor["surface"])
        direction = "LEFT" if neighbor_ordinal < target_ordinal else "RIGHT"
        base = {
            "kind": "EXACT_NEIGHBOR",
            "surface": neighbor_surface,
            "ordinal": neighbor_ordinal,
            "direction": direction,
            "gate_status": gate,
            "semantic_donor_eligible": int(gate == "ELIGIBLE"),
            "roles": donor["roles"],
            "axes": donor["axes"],
        }
        if neighbor_surface in STATE_ANCHORS:
            evidence[f"STATE_{STATE_ANCHORS[neighbor_surface]}"].append(base)
        if neighbor_surface == OLY_ANCHOR:
            evidence["OLY"].append(base)
        # A signature is an observed exact relation, not permission to copy a
        # meaning.  Retain current-clean process/close contacts even when the
        # global family gate bars semantic donation, and expose that gate on
        # every evidence record so the scorer can use the stricter subset.
        if int(donor["current_clean"]):
            roles = set(donor["roles"])
            axes = set(donor["axes"])
            if "PROCESS" in axes or "PASS" in axes or "PROCESS_PASS" in roles:
                evidence["PROCESS"].append(base)
            if "CLOSE" in axes or "CLOSE" in roles:
                evidence["CLOSE"].append(base)

    for span in controls["amount_spans"]:
        if str(span["locus"]) != locus:
            continue
        head_ordinal = int(span["head_ordinal"])
        value_ordinal = int(span["value_ordinal"])
        if target_ordinal not in {head_ordinal - 1, value_ordinal + 1}:
            continue
        evidence["AMOUNT"].append(
            {
                "kind": "EXACT_AMOUNT_SPAN",
                "span_id": span["span_id"],
                "written_span_eva": span["written_span_eva"],
                "head_ordinal": head_ordinal,
                "value_ordinal": value_ordinal,
                "direction": "RIGHT" if target_ordinal < head_ordinal else "LEFT",
            }
        )
    # GDT759 licenses exactly three ols+value constructions.  This is a
    # preparation/value relation of the target itself, kept separate from the
    # GDT764 X+daiin bounded-field channel.
    for span in controls["value_spans"]:
        if str(span["locus"]) != locus:
            continue
        preparation_ordinal = int(span["preparation_ordinal"])
        if target_ordinal != preparation_ordinal:
            continue
        assert target_surface == span["preparation_surface"] == "ols"
        evidence["VALUE"].append(
            {
                "kind": "EXACT_GDT759_PREPARATION_VALUE_SPAN",
                "span_id": span["span_id"],
                "written_span_eva": span["written_span_eva"],
                "preparation_ordinal": preparation_ordinal,
                "value_ordinal": span["value_ordinal"],
                "value_surface": span["value_surface"],
                "direction": "RIGHT",
                "target_member_role": "PREPARATION",
            }
        )
    for span in controls["bounded_value_spans"]:
        if str(span["locus"]) != locus:
            continue
        x_ordinal = int(span["x_ordinal"])
        value_ordinal = int(span["value_ordinal"])
        if target_ordinal not in {x_ordinal - 1, value_ordinal + 1}:
            continue
        evidence["BOUNDED_VALUE"].append(
            {
                "kind": "EXACT_BOUNDED_VALUE_SPAN",
                "span_id": span["span_id"],
                "written_span_eva": span["written_span_eva"],
                "x_ordinal": x_ordinal,
                "value_ordinal": value_ordinal,
                "direction": "RIGHT" if target_ordinal < x_ordinal else "LEFT",
            }
        )
    return {
        "signature_channels": tuple(
            channel for channel in SIGNATURE_CHANNELS if evidence[channel]
        ),
        "distinct_signature_channel_count": sum(bool(evidence[channel]) for channel in SIGNATURE_CHANNELS),
        "signature_evidence_count": sum(len(evidence[channel]) for channel in SIGNATURE_CHANNELS),
        "channel_evidence": {
            channel: tuple(evidence[channel]) for channel in SIGNATURE_CHANNELS
        },
        "semantic_donor_eligible_neighbor_evidence_counts": {
            channel: sum(
                int(item.get("semantic_donor_eligible", 0))
                for item in evidence[channel]
            )
            for channel in SIGNATURE_CHANNELS
        },
    }


def build_occurrence_atlas(
    raw_occurrences: Sequence[Mapping[str, object]],
    environment: Mapping[str, object],
    g764: ModuleType,
    blocks: Mapping[str, object],
    position_maps: Mapping[str, Mapping[tuple[str, int], object]],
    controls: Mapping[str, object],
) -> list[dict[str, object]]:
    """Attach clean D1/R2/LINE donor views and direct signatures."""

    context = environment["context"]
    output: list[dict[str, object]] = []
    for source in raw_occurrences:
        if not int(source["reader_exact"]):
            continue
        locus = str(source["locus"])
        target_ordinal = int(source["ordinal"])
        target_surface = str(source["surface"])
        line = context.by_line[locus]
        scope_eligible: dict[str, list[dict[str, object]]] = {
            scope: [] for scope in SCOPES
        }
        scope_blocked: dict[str, list[dict[str, object]]] = {
            scope: [] for scope in SCOPES
        }
        scope_gate_counts: dict[str, Counter[str]] = {
            scope: Counter() for scope in SCOPES
        }
        scope_features: dict[str, set[str]] = {scope: set() for scope in SCOPES}

        for donor_ordinal in range(1, len(line) + 1):
            if donor_ordinal == target_ordinal:
                continue
            distance = abs(donor_ordinal - target_ordinal)
            donor, gate = classify_donor(
                environment,
                g764,
                blocks,
                position_maps,
                locus,
                donor_ordinal,
                target_surface,
            )
            for scope in _scope_names(distance):
                scope_gate_counts[scope][gate] += 1
            if donor is None:
                continue
            record = {
                **donor,
                "distance": distance,
                "direction": "LEFT" if donor_ordinal < target_ordinal else "RIGHT",
                "gate_status": gate,
            }
            for scope in _scope_names(distance):
                if gate == "ELIGIBLE":
                    scope_eligible[scope].append(record)
                    scope_features[scope].update(record["features"])
                else:
                    scope_blocked[scope].append(record)

        views = {
            scope: {
                "features": tuple(
                    feature for feature in FEATURES if feature in scope_features[scope]
                ),
                "eligible_donors": tuple(scope_eligible[scope]),
                "blocked_donors": tuple(scope_blocked[scope]),
                "eligible_donor_positions": len(scope_eligible[scope]),
                "blocked_exact_donor_positions": len(scope_blocked[scope]),
                "gate_counts": dict(sorted(scope_gate_counts[scope].items())),
            }
            for scope in SCOPES
        }
        output.append(
            {
                **source,
                "context_views": views,
                "direct_signatures": _direct_signatures(
                    source, environment, g764, blocks, position_maps, controls
                ),
                "semantic_identity_credit": 0,
                "component_export_credit": 0,
            }
        )
    assert len(output) == 526
    assert Counter(str(row["surface"]) for row in output) == Counter(
        {target: exact for target, (_raw, exact) in EXPECTED_TARGET_COUNTS.items()}
    )
    return output


def build_target_census(
    raw_occurrences: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for surface in TARGET_FORMS:
        raw = [row for row in raw_occurrences if row["surface"] == surface]
        exact = [row for row in raw if int(row["reader_exact"])]
        rows.append(
            {
                "surface": surface,
                "guarded_raw_occurrences": len(raw),
                "reader_exact_occurrences": len(exact),
                "nonexact_occurrences": len(raw) - len(exact),
                "reader_exact_rate": len(exact) / len(raw),
                "guarded_raw_pages": len({str(row["page"]) for row in raw}),
                "reader_exact_pages": len({str(row["page"]) for row in exact}),
                "guarded_raw_loci": len({str(row["locus"]) for row in raw}),
                "reader_exact_loci": len({str(row["locus"]) for row in exact}),
                "semantic_identity_credit": 0,
                "component_export_credit": 0,
            }
        )
    return rows


def build_role_geometry(
    raw_occurrences: Sequence[Mapping[str, object]],
    occurrence_atlas: Sequence[Mapping[str, object]],
    environment: Mapping[str, object],
    g764: ModuleType,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for surface in TARGET_FORMS:
        raw = [row for row in raw_occurrences if row["surface"] == surface]
        exact = [row for row in occurrence_atlas if row["surface"] == surface]
        raw_positions = Counter(str(row["line_position"]) for row in raw)
        positions = Counter(str(row["line_position"]) for row in exact)
        sections = Counter(str(row["section"]) for row in exact)
        languages = Counter(str(row["language"]) for row in exact)
        hands = Counter(str(row["hand"]) for row in exact)
        target_roles: Counter[str] = Counter()
        target_axes: Counter[str] = Counter()
        for row in exact:
            slot = g764.slot(environment, str(row["locus"]), int(row["ordinal"]))
            assert int(slot["reader_exact"]) == 1 and str(slot["surface"]) == surface
            target_roles.update(_pipe_set(slot["roles"]))
            target_axes.update(_pipe_set(slot["axes"]))
        rows.append(
            {
                "surface": surface,
                "guarded_raw_occurrences": len(raw),
                "reader_exact_occurrences": len(exact),
                "raw_pages": len({str(row["page"]) for row in raw}),
                "reader_exact_pages": len({str(row["page"]) for row in exact}),
                "raw_loci": len({str(row["locus"]) for row in raw}),
                "reader_exact_loci": len({str(row["locus"]) for row in exact}),
                "raw_line_first": sum(int(row["ordinal"]) == 1 for row in raw),
                "raw_line_last": sum(
                    int(row["ordinal"]) == int(row["line_token_count"]) for row in raw
                ),
                "raw_line_position_counts": dict(sorted(raw_positions.items())),
                "raw_paragraph_start_line": sum(
                    int(row["paragraph_start_line"]) for row in raw
                ),
                "raw_paragraph_end_line": sum(
                    int(row["paragraph_end_line"]) for row in raw
                ),
                "raw_true_paragraph_opener": sum(
                    int(row["true_paragraph_opener"]) for row in raw
                ),
                "raw_true_paragraph_closer": sum(
                    int(row["true_paragraph_closer"]) for row in raw
                ),
                "raw_mean_ordinal": sum(int(row["ordinal"]) for row in raw) / len(raw),
                "raw_mean_normalized_line_position": sum(
                    float(row["normalized_line_position"]) for row in raw
                ) / len(raw),
                "line_first": sum(int(row["ordinal"]) == 1 for row in exact),
                "line_last": sum(
                    int(row["ordinal"]) == int(row["line_token_count"]) for row in exact
                ),
                "line_position_counts": dict(sorted(positions.items())),
                "paragraph_start_line": sum(int(row["paragraph_start_line"]) for row in exact),
                "paragraph_end_line": sum(int(row["paragraph_end_line"]) for row in exact),
                "true_paragraph_opener": sum(int(row["true_paragraph_opener"]) for row in exact),
                "true_paragraph_closer": sum(int(row["true_paragraph_closer"]) for row in exact),
                "mean_ordinal": sum(int(row["ordinal"]) for row in exact) / len(exact),
                "mean_normalized_line_position": sum(
                    float(row["normalized_line_position"]) for row in exact
                ) / len(exact),
                "section_counts": dict(sorted(sections.items())),
                "language_counts": dict(sorted(languages.items())),
                "hand_counts": dict(sorted(hands.items())),
                "current_target_role_occurrence_counts": dict(sorted(target_roles.items())),
                "current_target_axis_occurrence_counts": dict(sorted(target_axes.items())),
                "role_is_translation": 0,
                "component_export_credit": 0,
            }
        )
    return rows


def build_signature_support(
    occurrence_atlas: Sequence[Mapping[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    """Aggregate signatures by locus and prepare every locus leave-one-out."""

    support_loci: list[dict[str, object]] = []
    for target in TARGET_FORMS:
        selected = [row for row in occurrence_atlas if row["surface"] == target]
        by_locus: defaultdict[str, list[Mapping[str, object]]] = defaultdict(list)
        for row in selected:
            if int(row["direct_signatures"]["distinct_signature_channel_count"]):
                by_locus[str(row["locus"])].append(row)
        for locus, rows in sorted(by_locus.items()):
            channel_occurrences = {
                channel: sum(
                    channel in row["direct_signatures"]["signature_channels"] for row in rows
                )
                for channel in SIGNATURE_CHANNELS
            }
            channel_evidence = {
                channel: sum(
                    len(row["direct_signatures"]["channel_evidence"][channel])
                    for row in rows
                )
                for channel in SIGNATURE_CHANNELS
            }
            eligible_neighbor_evidence = {
                channel: sum(
                    int(
                        row["direct_signatures"]
                        ["semantic_donor_eligible_neighbor_evidence_counts"][channel]
                    )
                    for row in rows
                )
                for channel in SIGNATURE_CHANNELS
            }
            channels = tuple(
                channel for channel in SIGNATURE_CHANNELS if channel_occurrences[channel]
            )
            support_loci.append(
                {
                    "target_surface": target,
                    "page": rows[0]["page"],
                    "locus": locus,
                    "target_occurrence_ids": tuple(
                        str(row["target_occurrence_id"]) for row in rows
                    ),
                    "target_occurrences_at_locus": len(rows),
                    "signature_channels": channels,
                    "distinct_signature_channel_count": len(channels),
                    "signature_evidence_count": sum(channel_evidence.values()),
                    "channel_occurrence_counts": channel_occurrences,
                    "channel_evidence_counts": channel_evidence,
                    "semantic_donor_eligible_neighbor_evidence_counts": (
                        eligible_neighbor_evidence
                    ),
                    "written_line_eva": rows[0]["written_line_eva"],
                    "semantic_identity_credit": 0,
                    "component_export_credit": 0,
                }
            )

    summaries: list[dict[str, object]] = []
    loo_rows: list[dict[str, object]] = []
    for target in TARGET_FORMS:
        occurrences = [row for row in occurrence_atlas if row["surface"] == target]
        target_loci = [row for row in support_loci if row["target_surface"] == target]
        occurrence_counts = {
            channel: sum(
                channel in row["direct_signatures"]["signature_channels"]
                for row in occurrences
            )
            for channel in SIGNATURE_CHANNELS
        }
        evidence_counts = {
            channel: sum(
                len(row["direct_signatures"]["channel_evidence"][channel])
                for row in occurrences
            )
            for channel in SIGNATURE_CHANNELS
        }
        eligible_neighbor_evidence_counts = {
            channel: sum(
                int(
                    row["direct_signatures"]
                    ["semantic_donor_eligible_neighbor_evidence_counts"][channel]
                )
                for row in occurrences
            )
            for channel in SIGNATURE_CHANNELS
        }
        locus_counts = {
            channel: sum(
                int(row["channel_occurrence_counts"][channel]) > 0 for row in target_loci
            )
            for channel in SIGNATURE_CHANNELS
        }
        strongest = min(
            target_loci,
            key=lambda row: (
                -int(row["distinct_signature_channel_count"]),
                -int(row["signature_evidence_count"]),
                -int(row["target_occurrences_at_locus"]),
                str(row["locus"]),
            ),
        )
        strongest_locus = str(strongest["locus"])
        for left_out in target_loci:
            remaining = [row for row in target_loci if row["locus"] != left_out["locus"]]
            remaining_occurrence_counts = {
                channel: sum(
                    int(row["channel_occurrence_counts"][channel]) for row in remaining
                )
                for channel in SIGNATURE_CHANNELS
            }
            remaining_locus_counts = {
                channel: sum(
                    int(row["channel_occurrence_counts"][channel]) > 0 for row in remaining
                )
                for channel in SIGNATURE_CHANNELS
            }
            lost = tuple(
                channel
                for channel in SIGNATURE_CHANNELS
                if occurrence_counts[channel] and not remaining_occurrence_counts[channel]
            )
            loo_rows.append(
                {
                    "target_surface": target,
                    "left_out_locus": left_out["locus"],
                    "left_out_is_strongest_support_locus": int(
                        left_out["locus"] == strongest_locus
                    ),
                    "left_out_distinct_signature_channel_count": left_out[
                        "distinct_signature_channel_count"
                    ],
                    "remaining_support_loci": len(remaining),
                    "remaining_channel_occurrence_counts": remaining_occurrence_counts,
                    "remaining_channel_locus_counts": remaining_locus_counts,
                    "channels_lost": lost,
                    "all_observed_channels_survive": int(not lost),
                    "semantic_identity_credit": 0,
                    "component_export_credit": 0,
                }
            )
        strongest_loo = next(
            row
            for row in loo_rows
            if row["target_surface"] == target
            and int(row["left_out_is_strongest_support_locus"])
        )
        summaries.append(
            {
                "surface": target,
                "reader_exact_occurrences": len(occurrences),
                "any_signature_occurrences": sum(
                    bool(row["direct_signatures"]["signature_channels"])
                    for row in occurrences
                ),
                "support_loci": len(target_loci),
                "signature_occurrence_counts": occurrence_counts,
                "signature_evidence_counts": evidence_counts,
                "semantic_donor_eligible_neighbor_evidence_counts": (
                    eligible_neighbor_evidence_counts
                ),
                "signature_locus_counts": locus_counts,
                "strongest_support_locus": strongest_locus,
                "strongest_support_page": strongest["page"],
                "strongest_support_channels": strongest["signature_channels"],
                "strongest_support_distinct_channel_count": strongest[
                    "distinct_signature_channel_count"
                ],
                "strongest_support_evidence_count": strongest["signature_evidence_count"],
                "strongest_locus_channels_lost_on_loo": strongest_loo["channels_lost"],
                "strongest_locus_removal_preserves_every_observed_channel": strongest_loo[
                    "all_observed_channels_survive"
                ],
                "strongest_locus_loo_occurrence_counts": strongest_loo[
                    "remaining_channel_occurrence_counts"
                ],
                "strongest_locus_loo_locus_counts": strongest_loo[
                    "remaining_channel_locus_counts"
                ],
                "semantic_identity_credit": 0,
                "component_export_credit": 0,
            }
        )
    return summaries, support_loci, loo_rows


def _gate_exposure_summary(
    occurrence_atlas: Sequence[Mapping[str, object]],
) -> dict[str, dict[str, dict[str, int]]]:
    return {
        target: {
            scope: dict(
                sorted(
                    sum(
                        (
                            Counter(row["context_views"][scope]["gate_counts"])
                            for row in occurrence_atlas
                            if row["surface"] == target
                        ),
                        Counter(),
                    ).items()
                )
            )
            for scope in SCOPES
        }
        for target in TARGET_FORMS
    }


def _surface_set_cache_coverage(
    environment: Mapping[str, object], surfaces: Iterable[str]
) -> dict[str, int]:
    selected = frozenset(surfaces)
    context = environment["context"]
    raw: list[tuple[str, Mapping[str, object]]] = []
    exact: list[tuple[str, Mapping[str, object]]] = []
    for locus, line in context.by_line.items():
        for token in line:
            if str(token["eva"]) not in selected:
                continue
            item = (locus, token)
            raw.append(item)
            if bool(context.exact[(locus, int(token["token_index"]))]):
                exact.append(item)
    return {
        "surface_count": len(selected),
        "guarded_raw_occurrences": len(raw),
        "reader_exact_occurrences": len(exact),
        "guarded_raw_pages": len({str(token["page"]) for _locus, token in raw}),
        "reader_exact_pages": len({str(token["page"]) for _locus, token in exact}),
        "guarded_raw_loci": len({locus for locus, _token in raw}),
        "reader_exact_loci": len({locus for locus, _token in exact}),
    }


def _per_current_target_sensitivity_exposures(
    occurrence_atlas: Sequence[Mapping[str, object]],
) -> dict[str, dict[str, dict[str, int]]]:
    """Reclassify only union-family blocks for a no-map sensitivity count."""

    output: dict[str, dict[str, dict[str, int]]] = {}
    for target in TARGET_FORMS:
        output[target] = {}
        for scope in SCOPES:
            counts: Counter[str] = Counter()
            for row in occurrence_atlas:
                if row["surface"] != target:
                    continue
                view = row["context_views"][scope]
                counts.update(view["gate_counts"])
                for donor in view["blocked_donors"]:
                    if donor["gate_status"] != "TARGET_FAMILY_ED2_BLOCK":
                        continue
                    sensitivity_gate = str(donor["per_current_target_gate_status"])
                    if sensitivity_gate == "TARGET_FAMILY_ED2_BLOCK":
                        continue
                    counts["TARGET_FAMILY_ED2_BLOCK"] -= 1
                    counts[sensitivity_gate] += 1
            output[target][scope] = dict(
                sorted((gate, count) for gate, count in counts.items() if count)
            )
    return output


def build_core_atlas(root: Path = ROOT) -> dict[str, object]:
    """Build all GDT769 read-only Python structures."""

    g764, environment = load_guarded_environment(root)
    gdt754 = load_gdt754_source_composed_surfaces(root)
    gdt737 = load_gdt737_provenance_blocks(root)
    controls = load_control_spans(environment, root)
    anchors = enumerate_control_anchors(environment)
    controls = {**controls, "anchor_occurrences": anchors}
    position_maps = build_control_position_maps(controls)
    blocks = build_block_registry(environment, gdt754, gdt737)
    raw_occurrences = enumerate_raw_targets(environment)
    occurrence_atlas = build_occurrence_atlas(
        raw_occurrences, environment, g764, blocks, position_maps, controls
    )
    target_census = build_target_census(raw_occurrences)
    role_geometry = build_role_geometry(
        raw_occurrences, occurrence_atlas, environment, g764
    )
    signature_summary, support_loci, leave_one_out = build_signature_support(
        occurrence_atlas
    )

    # Global source and target-family blocks must be absolute for every emitted
    # eligible donor, including the full-line view.
    for row in occurrence_atlas:
        target = str(row["surface"])
        blocked = blocks["full_block_by_target"][target]
        for scope in SCOPES:
            assert not {
                str(donor["surface"])
                for donor in row["context_views"][scope]["eligible_donors"]
            } & blocked, f"blocked donor escaped for {target}/{scope}"
    all_pages = {
        str(row["page"])
        for row in (*raw_occurrences, *anchors)
    } | {
        str(row["page"])
        for row in (
            *controls["amount_spans"],
            *controls["value_spans"],
            *controls["bounded_value_spans"],
        )
    }
    assert not any(page.startswith(FORBIDDEN_PAGE_PREFIXES) for page in all_pages)

    gate_exposures = _gate_exposure_summary(occurrence_atlas)
    sensitivity_exposures = _per_current_target_sensitivity_exposures(
        occurrence_atlas
    )
    direct_counts = {
        row["surface"]: dict(row["signature_occurrence_counts"])
        for row in signature_summary
    }
    source_block_coverage = {
        "gdt754_source_composed": _surface_set_cache_coverage(environment, gdt754),
        "gdt737_explicit_quarantine": _surface_set_cache_coverage(
            environment, gdt737["quarantined_surfaces"]
        ),
        "combined_explicit_sources": _surface_set_cache_coverage(
            environment,
            gdt754 | frozenset(gdt737["quarantined_surfaces"]),
        ),
        "gdt737_held_provenance_cohort": _surface_set_cache_coverage(
            environment, gdt737["held_cohort_surfaces"]
        ),
    }
    assert direct_counts == EXPECTED_DIRECT_SIGNATURE_COUNTS, (
        f"direct signature census changed: {direct_counts}"
    )
    assert {
        target: len(blocks["family_by_target"][target]) for target in TARGET_FORMS
    } == EXPECTED_FAMILY_SURFACE_COUNTS
    assert len(blocks["family_union"]) == 838
    if bool(gdt737["available"]):
        assert len(gdt754 & frozenset(gdt737["quarantined_surfaces"])) == 12
        assert len(blocks["base_global_block"]) == 245
        assert len(next(iter(blocks["full_block_by_target"].values()))) == 1030
        assert source_block_coverage["combined_explicit_sources"] == {
            "surface_count": 240,
            "guarded_raw_occurrences": 1265,
            "reader_exact_occurrences": 990,
            "guarded_raw_pages": 162,
            "reader_exact_pages": 157,
            "guarded_raw_loci": 1065,
            "reader_exact_loci": 858,
        }
    primary_gate_totals = {
        scope: dict(
            sorted(
                sum(
                    (Counter(gate_exposures[target][scope]) for target in TARGET_FORMS),
                    Counter(),
                ).items()
            )
        )
        for scope in SCOPES
    }
    if bool(gdt737["available"]):
        assert primary_gate_totals == EXPECTED_PRIMARY_GATE_TOTALS, (
            f"primary gate exposure census changed: {primary_gate_totals}"
        )
    assert len(support_loci) == len(leave_one_out) == 52
    geometry_lookup = {str(row["surface"]): row for row in role_geometry}
    assert (
        geometry_lookup["ol"]["line_first"],
        geometry_lookup["ol"]["line_last"],
        geometry_lookup["ol"]["paragraph_start_line"],
        geometry_lookup["ol"]["paragraph_end_line"],
    ) == (22, 37, 33, 45)
    assert (
        geometry_lookup["pcheey"]["line_first"],
        geometry_lookup["pcheey"]["line_last"],
        geometry_lookup["pcheey"]["paragraph_start_line"],
        geometry_lookup["pcheey"]["paragraph_end_line"],
    ) == (0, 0, 3, 0)
    assert (
        geometry_lookup["ols"]["line_first"],
        geometry_lookup["ols"]["line_last"],
    ) == (0, 5)
    metadata = {
        "target_forms": TARGET_FORMS,
        "target_guarded_raw_counts": {
            target: EXPECTED_TARGET_COUNTS[target][0] for target in TARGET_FORMS
        },
        "target_reader_exact_counts": {
            target: EXPECTED_TARGET_COUNTS[target][1] for target in TARGET_FORMS
        },
        "target_guarded_raw_occurrences": len(raw_occurrences),
        "target_reader_exact_occurrences": len(occurrence_atlas),
        "target_guarded_raw_pages": len({str(row["page"]) for row in raw_occurrences}),
        "target_reader_exact_pages": len({str(row["page"]) for row in occurrence_atlas}),
        "target_guarded_raw_loci": len({str(row["locus"]) for row in raw_occurrences}),
        "target_reader_exact_loci": len({str(row["locus"]) for row in occurrence_atlas}),
        "scopes": SCOPES,
        "features": FEATURES,
        "signature_channels": SIGNATURE_CHANNELS,
        "family_edit_distance": FAMILY_EDIT_DISTANCE,
        "donor_gate_order": (
            "READER_EXACT__TARGET_PANEL__GDT754_SOURCE_COMPOSED__"
            "GDT737_EXPLICIT_LITERAL_HEAD_QUARANTINE__ANY_TARGET_ED2_FAMILY__"
            "CURRENT_CLEAN__ELIGIBLE"
        ),
        "guarded_surface_count": len(blocks["guarded_surfaces"]),
        "target_panel_blocked_surface_count": len(TARGET_FORM_SET),
        "gdt754_source_composed_surface_count": len(gdt754),
        "gdt737_artifacts_available": bool(gdt737["available"]),
        "gdt737_held_provenance_surface_count": len(gdt737["held_cohort_surfaces"]),
        "gdt737_explicit_quarantined_surface_count": len(
            gdt737["quarantined_surfaces"]
        ),
        "gdt737_retained_surface_count": len(gdt737["retained_surfaces"]),
        "base_global_blocked_unique_surface_count": len(blocks["base_global_block"]),
        "source_block_cache_coverage": source_block_coverage,
        "family_ed2_surface_counts": {
            target: len(blocks["family_by_target"][target]) for target in TARGET_FORMS
        },
        "family_ed2_union_surface_count": len(blocks["family_union"]),
        "full_blocked_surface_counts": {
            target: len(blocks["full_block_by_target"][target]) for target in TARGET_FORMS
        },
        "per_current_target_sensitivity_blocked_surface_counts": {
            target: len(blocks["per_current_target_sensitivity_block"][target])
            for target in TARGET_FORMS
        },
        "state_and_oly_anchor_occurrences": len(anchors),
        "anchor_exact_counts": dict(EXPECTED_ANCHOR_EXACT_COUNTS),
        "exact_amount_spans": len(controls["amount_spans"]),
        "exact_value_spans": len(controls["value_spans"]),
        "exact_bounded_value_spans": len(controls["bounded_value_spans"]),
        "support_locus_rows": len(support_loci),
        "leave_one_locus_out_rows": len(leave_one_out),
        "direct_signature_occurrence_counts": direct_counts,
        "gate_exposures": gate_exposures,
        "primary_gate_totals": primary_gate_totals,
        "per_current_target_sensitivity_gate_exposures": sensitivity_exposures,
        "guard": dict(environment["guard"]),
        "semantic_identity_credit": 0,
        "component_export_credit": 0,
        "f84_accessed": False,
        "f84r_accessed": False,
    }
    return {
        "raw_occurrences": raw_occurrences,
        "occurrences": occurrence_atlas,
        "target_census": target_census,
        "role_geometry": role_geometry,
        "signature_summary": signature_summary,
        "support_loci": support_loci,
        "leave_one_locus_out": leave_one_out,
        "controls": controls,
        "donor_blocks": {
            "target_panel": tuple(TARGET_FORMS),
            "gdt754_source_composed": tuple(sorted(blocks["gdt754"])),
            "gdt737_explicit_quarantine": tuple(sorted(blocks["gdt737_quarantined"])),
            "gdt737_held_provenance_cohort": tuple(sorted(blocks["gdt737_held_cohort"])),
            "family_ed2_by_target": {
                target: tuple(sorted(blocks["family_by_target"][target]))
                for target in TARGET_FORMS
            },
            "family_ed2_union": tuple(sorted(blocks["family_union"])),
            "full_block_by_target": {
                target: tuple(sorted(blocks["full_block_by_target"][target]))
                for target in TARGET_FORMS
            },
            "per_current_target_sensitivity_block": {
                target: tuple(
                    sorted(blocks["per_current_target_sensitivity_block"][target])
                )
                for target in TARGET_FORMS
            },
        },
        "metadata": metadata,
    }


__all__ = (
    "BOUNDED_X_FORMS",
    "FEATURES",
    "FAMILY_EDIT_DISTANCE",
    "SCOPES",
    "SIGNATURE_CHANNELS",
    "STATE_ANCHORS",
    "TARGET_FORMS",
    "build_block_registry",
    "build_control_position_maps",
    "build_core_atlas",
    "build_occurrence_atlas",
    "build_role_geometry",
    "build_signature_support",
    "build_target_census",
    "classify_donor",
    "enumerate_control_anchors",
    "enumerate_raw_targets",
    "levenshtein",
    "load_control_spans",
    "load_gdt737_provenance_blocks",
    "load_gdt754_source_composed_surfaces",
    "load_guarded_environment",
)
