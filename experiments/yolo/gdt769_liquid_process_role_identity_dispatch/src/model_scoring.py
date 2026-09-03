#!/usr/bin/env python3
"""Transparent, read-only model dispatch for GDT769.

The scorer consumes the in-memory structures built by :mod:`core_atlas` and
the already loaded specification rows.  It performs no file or network I/O,
writes nothing, and returns only JSON-serialisable Python values.

Frames describe exact whole-form relations.  They are not word translations.
Historical predictions are reported as comparison metadata and never create a
Voynich observation.  A concrete identity card can win only after its role,
two independent observational axes, and strongest-locus leave-one-out gates
all survive.
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from typing import Any


TARGETS = ("ol", "ckhy", "pcheey", "ols", "otar")
FRAME_IDS = tuple(f"F{number:02d}" for number in range(1, 17))
ROLE_PREFIXES = ("R01", "R02", "R03", "R04", "R05")

# Frames in one family are useful observations but not independent identity
# axes.  In particular AMOUNT and VALUE cannot by themselves manufacture a
# two-axis liquid identity.
FRAME_AXIS_FAMILY = {
    "F01_AMOUNT_DIRECT": "MEASURE_VALUE",
    "F02_VALUE_DIRECT": "MEASURE_VALUE",
    "F03_DRY_R2": "DRY_STATE",
    "F04_MOIST_R2": "MOIST_STATE",
    "F05_PROCESS_SLOT_FINAL": "LEFT_PATIENT_PROCESS_DIRECTION",
    "F06_TARGET_BEFORE_PROCESS": "RIGHT_PROCESS_DIRECTION",
    "F07_LINE_FINAL_OR_CLOSE": "TERMINAL_GEOMETRY",
    "F08_HOT_R2": "HOT_STATE",
    "F09_COLD_R2": "COLD_STATE",
    "F10_PART_OR_CONTENT_R2": "CONTENT_CONTACT",
    "F11_H1_BOUNDED_VALUE": "BOUNDED_RECORD",
    "F12_PARALLEL_VALUE_CELL": "PARALLEL_RECORD",
    "F13_SECOND_PAGE_AFTER_ABLATION": "REPLICATION_CONTROL",
    "F14_MEDIAL_TWO_SIDED_LINKER": "TWO_SIDED_LINKER_GEOMETRY",
    "F15_STATE_TRANSITION_BRIDGE": "STATE_TRANSITION_DIRECTION",
    "F16_RELATIONAL_AMOUNT_ORDER": "RELATIONAL_AMOUNT_ORDER",
}

STATE_FEATURES = ("DRY", "MOIST", "HOT", "COLD")
NOMINAL_FEATURES = ("MATERIAL", "PREPARATION")
CLAIM_ZERO_FIELDS = {
    "default_is_translation": 0,
    "eva_latin_credit": 0,
    "substring_export_credit": 0,
    "confirmed_lexeme": 0,
    "confirmed_plaintext": 0,
    "component_export_credit": 0,
}

# The historical comparison deck and the identity deck deliberately use
# different category vocabularies. These are declared semantic category
# families, not EVA spelling aliases and not substring rules.
HISTORICAL_TYPE_FAMILIES: dict[str, tuple[str, ...]] = {
    "AQUEOUS_SOLVENT": ("MEDICINAL_WATER",),
    "FERMENTED_SOLVENT": ("WINE_SOLVENT",),
    "FERMENTED_ACID_SOLVENT": ("VINEGAR_SOLVENT",),
    "FERMENTED_MEDIUM": ("FERMENTED_OR_ACID_MEDIUM",),
    "DRY_POWDER": ("DRY_POWDER", "DRY_DRUG"),
    "GENERIC_TERMINAL_PRODUCT": ("TERMINAL_LIQUID_PREPARATION",),
    "PORTABLE_SEQUENCE_BASELINE": ("SEQUENCE_CONNECTOR_DEINDE_POSTEA",),
    "SEQUENCE_ADVERB": ("SEQUENCE_CONNECTOR_DEINDE_POSTEA",),
    "TERMINATIVE_LINKER": ("ENDPOINT_SUBORDINATOR_DONEC",),
    "PLANT_JUICE_OR_EXTRACT": ("PLANT_JUICE", "PLANT_EXTRACT"),
    "DECOCTION_PRODUCT": ("DECOCTION", "DECOCTION_PRODUCT"),
    "INFUSION_OR_DECOCTION": ("INFUSION_DECOCTION_NOUN",),
    "FINISHED_LIQUID_PREPARATION": ("TERMINAL_LIQUID_PREPARATION",),
    "JUICE_EXTRACT_PRODUCT": (
        "PLANT_JUICE_EXTRACT_PRODUCT",
        "DECOCTION_PRODUCT",
    ),
    "MEDICINAL_WATER_EXTRACT": (
        "MEDICINAL_WATER",
        "PLANT_JUICE_EXTRACT",
        "DECOCTION",
    ),
    "DRY_PREPARATION_PRODUCT": ("DRY_POWDER", "DRY_DRUG"),
}
HISTORICAL_TARGET_TYPE_FAMILIES: dict[tuple[str, str], tuple[str, ...]] = {
    ("ckhy", "PORTABLE_BASELINE"): ("COMPOUND_PREPARATION",),
    ("pcheey", "PORTABLE_BASELINE"): ("BOUND_FORM_QUALITY_FIELD",),
    ("otar", "PORTABLE_BASELINE"): ("COLD_FRACTION",),
}

_TOKEN_RE = re.compile(r"NOT|AND|OR|\(|\)|[A-Z][A-Z0-9_]*")


def _as_int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _rounded(value: float) -> float:
    return round(float(value), 6)


def _pipe(value: object) -> list[str]:
    return [
        item
        for item in str(value or "").split("|")
        if item and item not in {"NONE", "OPEN"}
    ]


def _unique_rows(
    rows: Sequence[Mapping[str, object]], key: str, label: str
) -> dict[str, Mapping[str, object]]:
    lookup: dict[str, Mapping[str, object]] = {}
    for row in rows:
        value = str(row.get(key, ""))
        if not value:
            raise ValueError(f"{label} row lacks {key}")
        if value in lookup:
            raise ValueError(f"duplicate {label} {key}: {value}")
        lookup[value] = row
    return lookup


def _normalise_expression(expression: object) -> str:
    text = str(expression or "NONE").upper().strip()
    # This suffix occurs in the R02 contradiction.  Make the conjunction
    # explicit so the ordinary Boolean parser can expose it independently.
    text = re.sub(
        r"\)\s+ON_TWO_PAGES_WITHOUT_DIRECTION\b",
        ") AND ON_TWO_PAGES_WITHOUT_DIRECTION",
        text,
    )
    text = re.sub(
        r"\)\s+ON_SAME_TARGET_OCCURRENCE\b",
        ") AND ON_SAME_TARGET_OCCURRENCE",
        text,
    )
    return text


def _expression_identifiers(expression: object) -> list[str]:
    return [
        token
        for token in _TOKEN_RE.findall(_normalise_expression(expression))
        if token not in {"AND", "OR", "NOT", "NONE"}
    ]


def _evaluate_expression(expression: object, truth: Mapping[str, bool]) -> bool:
    """Evaluate the tiny AND/OR/NOT specification language without ``eval``."""

    text = _normalise_expression(expression)
    if text in {"", "NONE"}:
        return False
    tokens = _TOKEN_RE.findall(text)
    if not tokens:
        return False
    index = 0

    def primary() -> bool:
        nonlocal index
        if index >= len(tokens):
            raise ValueError(f"incomplete expression: {text}")
        token = tokens[index]
        if token == "NOT":
            index += 1
            return not primary()
        if token == "(":
            index += 1
            value = parse_or()
            if index >= len(tokens) or tokens[index] != ")":
                raise ValueError(f"unclosed expression: {text}")
            index += 1
            return value
        if token in {"AND", "OR", ")"}:
            raise ValueError(f"unexpected token {token!r} in {text!r}")
        index += 1
        return bool(truth.get(token, False))

    def parse_and() -> bool:
        nonlocal index
        value = primary()
        while index < len(tokens) and tokens[index] == "AND":
            index += 1
            right = primary()
            value = value and right
        return value

    def parse_or() -> bool:
        nonlocal index
        value = parse_and()
        while index < len(tokens) and tokens[index] == "OR":
            index += 1
            right = parse_and()
            value = value or right
        return value

    result = parse_or()
    if index != len(tokens):
        raise ValueError(f"unparsed expression tail in {text!r}: {tokens[index:]}")
    return result


def _frame_key(frame_id: str) -> str:
    return frame_id.split("_", 1)[0]


def _role_key(role_id: str) -> str:
    return "ROLE_" + role_id.split("_", 1)[0]


def _features(donor: Mapping[str, object]) -> set[str]:
    return {str(item) for item in donor.get("features", ())}


def _eligible_donors(
    occurrence: Mapping[str, object], scope: str
) -> list[Mapping[str, object]]:
    views = occurrence.get("context_views", {})
    if not isinstance(views, Mapping) or scope not in views:
        return []
    view = views[scope]
    if not isinstance(view, Mapping):
        return []
    return [
        donor
        for donor in view.get("eligible_donors", ())
        if isinstance(donor, Mapping) and str(donor.get("gate_status")) == "ELIGIBLE"
    ]


def _channel_items(
    occurrence: Mapping[str, object], channel: str
) -> list[Mapping[str, object]]:
    signatures = occurrence.get("direct_signatures", {})
    if not isinstance(signatures, Mapping):
        return []
    channels = signatures.get("channel_evidence", {})
    if not isinstance(channels, Mapping):
        return []
    return [item for item in channels.get(channel, ()) if isinstance(item, Mapping)]


def _eligible_signature_items(
    occurrence: Mapping[str, object], channel: str, direction: str | None = None
) -> list[Mapping[str, object]]:
    rows: list[Mapping[str, object]] = []
    for item in _channel_items(occurrence, channel):
        if direction is not None and str(item.get("direction")) != direction:
            continue
        # Structural span controls do not have a semantic donor.  Neighbor
        # controls must pass the UNION-ED2 donor gate to carry a semantic role.
        if str(item.get("kind", "")).startswith("EXACT_") and "NEIGHBOR" not in str(
            item.get("kind", "")
        ):
            rows.append(item)
        elif _as_int(item.get("semantic_donor_eligible")) == 1 or str(
            item.get("gate_status")
        ) == "ELIGIBLE":
            rows.append(item)
    return rows


def _axis_donors(
    occurrence: Mapping[str, object],
    scope: str,
    features: Iterable[str],
    *,
    direction: str | None = None,
    maximum_distance: int | None = None,
) -> list[Mapping[str, object]]:
    wanted = set(features)
    output: list[Mapping[str, object]] = []
    for donor in _eligible_donors(occurrence, scope):
        if direction is not None and str(donor.get("direction")) != direction:
            continue
        if maximum_distance is not None and _as_int(donor.get("distance"), 9999) > maximum_distance:
            continue
        if _features(donor) & wanted:
            output.append(donor)
    return output


def _donor_brief(donor: Mapping[str, object]) -> dict[str, object]:
    return {
        "surface": str(donor.get("surface", "")),
        "ordinal": _as_int(donor.get("ordinal")),
        "distance": _as_int(donor.get("distance")),
        "direction": str(donor.get("direction", "")),
        "features": sorted(_features(donor)),
        "semantic_source": str(donor.get("semantic_source", "")),
        "gate_status": str(donor.get("gate_status", "ELIGIBLE")),
    }


def _evidence_record(
    occurrence: Mapping[str, object],
    frame_id: str,
    axes: Iterable[str],
    detail: Mapping[str, object],
) -> dict[str, object]:
    return {
        "frame_id": frame_id,
        "target_surface": str(occurrence["surface"]),
        "target_occurrence_id": str(occurrence.get("target_occurrence_id", "")),
        "page": str(occurrence["page"]),
        "locus": str(occurrence["locus"]),
        "ordinal": _as_int(occurrence["ordinal"]),
        "axis_families": sorted(set(axes)),
        "detail": dict(detail),
        "reader_exact": 1,
        "target_excluding_evidence": 1,
        **CLAIM_ZERO_FIELDS,
    }


def _target_is_control_member(
    occurrence: Mapping[str, object], core: Mapping[str, object]
) -> bool:
    locus = str(occurrence["locus"])
    ordinal = _as_int(occurrence["ordinal"])
    controls = core.get("controls", {})
    if not isinstance(controls, Mapping):
        return False
    for key in ("amount_spans", "value_spans", "bounded_value_spans"):
        for span in controls.get(key, ()):
            if not isinstance(span, Mapping) or str(span.get("locus")) != locus:
                continue
            ordinal_fields = (
                "head_ordinal",
                "value_ordinal",
                "preparation_ordinal",
                "x_ordinal",
            )
            if ordinal in {
                _as_int(span.get(field), -1)
                for field in ordinal_fields
                if field in span
            }:
                return True
    return False


def _target_has_own_value_binding(
    occurrence: Mapping[str, object], core: Mapping[str, object]
) -> bool:
    # An AMOUNT control next to the target is relational evidence (F01/F16),
    # not a value cell owned by the target.  Only the separate target VALUE
    # channel or actual membership in a bounded/value control cell counts as
    # own binding. Merely standing next to a bounded cell is still relational.
    return bool(
        _channel_items(occurrence, "VALUE")
        or _target_is_control_member(occurrence, core)
    )


def _left_licensed_measure_frames(
    occurrence: Mapping[str, object], core: Mapping[str, object], radius: int = 2
) -> list[dict[str, object]]:
    locus = str(occurrence["locus"])
    target_ordinal = _as_int(occurrence["ordinal"])
    controls = core.get("controls", {})
    if not isinstance(controls, Mapping):
        return []
    output: list[dict[str, object]] = []
    for cell_class, key in (
        ("AMOUNT", "amount_spans"),
        ("PREPARATION_VALUE", "value_spans"),
    ):
        for span in controls.get(key, ()):
            if not isinstance(span, Mapping) or str(span.get("locus")) != locus:
                continue
            end = _as_int(span.get("value_ordinal"), -999)
            distance = target_ordinal - end
            if 1 <= distance <= radius:
                output.append(
                    {
                        "cell_class": cell_class,
                        "span_id": str(span.get("span_id", "")),
                        "end_ordinal": end,
                        "distance_to_target": distance,
                        "written_span_eva": str(span.get("written_span_eva", "")),
                    }
                )
    return output


def _target_h1_surfaces(core: Mapping[str, object]) -> set[str]:
    output: set[str] = set()
    for row in core.get("role_geometry", ()):
        if not isinstance(row, Mapping):
            continue
        role_counts = row.get("current_target_role_occurrence_counts", {})
        if isinstance(role_counts, Mapping) and _as_int(role_counts.get("H1_RECORD_FORM")):
            output.add(str(row.get("surface")))
    return output


def _value_cells_by_locus(core: Mapping[str, object]) -> dict[str, list[dict[str, object]]]:
    """Return deduplicated amount/value/bounded cells for F12 parallelism."""

    result: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    seen: set[tuple[str, str, str]] = set()
    controls = core.get("controls", {})
    if isinstance(controls, Mapping):
        decks = (
            ("AMOUNT", "amount_spans"),
            ("PREPARATION_VALUE", "value_spans"),
            ("BOUNDED_VALUE", "bounded_value_spans"),
        )
        for cell_class, key in decks:
            for span in controls.get(key, ()):
                if not isinstance(span, Mapping):
                    continue
                locus = str(span.get("locus", ""))
                span_id = str(span.get("span_id", ""))
                start_ordinal = _as_int(
                    span.get(
                        "head_ordinal",
                        span.get("preparation_ordinal", span.get("x_ordinal")),
                    )
                )
                value_ordinal = _as_int(span.get("value_ordinal"))
                identity = (locus, str(start_ordinal), str(value_ordinal))
                if identity in seen:
                    continue
                seen.add(identity)
                result[locus].append(
                    {
                        "cell_class": cell_class,
                        "span_id": span_id,
                        "start_ordinal": start_ordinal,
                        "value_ordinal": value_ordinal,
                        "head_surface": str(
                            span.get(
                                "head_surface",
                                span.get(
                                    "preparation_surface", span.get("x_surface", "")
                                ),
                            )
                        ),
                        "value_surface": str(span.get("value_surface", "")),
                    }
                )
    return dict(result)


def _state_label(donor: Mapping[str, object]) -> tuple[str, ...]:
    return tuple(feature for feature in STATE_FEATURES if feature in _features(donor))


def _transition_pairs(
    occurrence: Mapping[str, object]
) -> list[dict[str, object]]:
    left = [
        donor
        for donor in _eligible_donors(occurrence, "LINE")
        if str(donor.get("direction")) == "LEFT" and _state_label(donor)
    ]
    right = [
        donor
        for donor in _eligible_donors(occurrence, "LINE")
        if str(donor.get("direction")) == "RIGHT" and _state_label(donor)
    ]
    transitions: list[dict[str, object]] = []
    seen: set[tuple[str, str, int, int]] = set()
    for left_donor in left:
        for right_donor in right:
            for left_state in _state_label(left_donor):
                for right_state in _state_label(right_donor):
                    key = (
                        left_state,
                        right_state,
                        _as_int(left_donor.get("ordinal")),
                        _as_int(right_donor.get("ordinal")),
                    )
                    if key in seen:
                        continue
                    seen.add(key)
                    transitions.append(
                        {
                            "direction": f"{left_state}_TO_{right_state}",
                            "left": _donor_brief(left_donor),
                            "right": _donor_brief(right_donor),
                        }
                    )
    return transitions


def _frame_occurrence_evidence(
    core: Mapping[str, object]
) -> dict[tuple[str, str], list[dict[str, object]]]:
    """Construct the fifteen observational frames occurrence by occurrence."""

    output: defaultdict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    h1_surfaces = _target_h1_surfaces(core)
    value_cells_by_locus = _value_cells_by_locus(core)

    for occurrence in core.get("occurrences", ()):
        if not isinstance(occurrence, Mapping):
            continue
        target = str(occurrence.get("surface"))
        if target not in TARGETS:
            continue

        amount = _channel_items(occurrence, "AMOUNT")
        value = _channel_items(occurrence, "VALUE")
        bounded = _channel_items(occurrence, "BOUNDED_VALUE")
        if amount:
            output[target, "F01_AMOUNT_DIRECT"].append(
                _evidence_record(
                    occurrence,
                    "F01_AMOUNT_DIRECT",
                    ("MEASURE_VALUE",),
                    {"exact_span_evidence": [dict(item) for item in amount]},
                )
            )
            orientation_counts = Counter(
                "TARGET_BEFORE_AMOUNT"
                if str(item.get("direction")) == "RIGHT"
                else "AMOUNT_BEFORE_TARGET"
                for item in amount
            )
            output[target, "F16_RELATIONAL_AMOUNT_ORDER"].append(
                _evidence_record(
                    occurrence,
                    "F16_RELATIONAL_AMOUNT_ORDER",
                    ("RELATIONAL_AMOUNT_ORDER",),
                    {
                        "exact_adjacent_amount_spans": [
                            dict(item) for item in amount
                        ],
                        "direction_labels": sorted(orientation_counts),
                        "orientation_counts": dict(sorted(orientation_counts.items())),
                        "amount_adjacency_is_relational_not_own_binding": 1,
                        "repetition_without_amount_or_transition_credit": 0,
                    },
                )
            )
        if value:
            output[target, "F02_VALUE_DIRECT"].append(
                _evidence_record(
                    occurrence,
                    "F02_VALUE_DIRECT",
                    ("MEASURE_VALUE",),
                    {
                        "exact_value_evidence": [dict(item) for item in value],
                        "separate_from_amount_and_bounded": 1,
                    },
                )
            )

        for frame_id, feature, axis in (
            ("F03_DRY_R2", "DRY", "DRY_STATE"),
            ("F04_MOIST_R2", "MOIST", "MOIST_STATE"),
            ("F08_HOT_R2", "HOT", "HOT_STATE"),
            ("F09_COLD_R2", "COLD", "COLD_STATE"),
        ):
            donors = _axis_donors(occurrence, "R2", (feature,))
            if donors:
                output[target, frame_id].append(
                    _evidence_record(
                        occurrence,
                        frame_id,
                        (axis,),
                        {"eligible_donors": [_donor_brief(item) for item in donors]},
                    )
                )

        left_nominal = _axis_donors(
            occurrence, "R2", NOMINAL_FEATURES, direction="LEFT"
        )
        left_measure_frames = _left_licensed_measure_frames(occurrence, core)
        close_right = _eligible_signature_items(occurrence, "CLOSE", "RIGHT")
        own_value = _target_has_own_value_binding(occurrence, core)
        line_final = str(occurrence.get("line_position")) in {"LAST", "SINGLE"}
        if (left_nominal or left_measure_frames) and (line_final or close_right) and not own_value:
            output[target, "F05_PROCESS_SLOT_FINAL"].append(
                _evidence_record(
                    occurrence,
                    "F05_PROCESS_SLOT_FINAL",
                    ("LEFT_PATIENT_PROCESS_DIRECTION", "TERMINAL_GEOMETRY"),
                    {
                        "left_nominal_donors": [
                            _donor_brief(item) for item in left_nominal
                        ],
                        "left_licensed_amount_or_value_frames": left_measure_frames,
                        "line_final": int(line_final),
                        "right_close_evidence": [dict(item) for item in close_right],
                        "own_value_binding": 0,
                    },
                )
            )

        right_process = _axis_donors(
            occurrence,
            "LINE",
            ("PROCESS", "PASS", "CLOSE"),
            direction="RIGHT",
            maximum_distance=3,
        )
        # ``oly`` is an explicit whole-form process control.  UNION-ED2 blocks
        # it as a semantic donor near ``ol``/``ols``, but its observed exact
        # whole relation may still establish direction.  No ol+y split enters.
        right_oly = [
            item
            for item in _channel_items(occurrence, "OLY")
            if str(item.get("direction")) == "RIGHT"
        ]
        if right_process or right_oly:
            output[target, "F06_TARGET_BEFORE_PROCESS"].append(
                _evidence_record(
                    occurrence,
                    "F06_TARGET_BEFORE_PROCESS",
                    ("RIGHT_PROCESS_DIRECTION",),
                    {
                        "eligible_right_process_or_close_donors": [
                            _donor_brief(item) for item in right_process
                        ],
                        "exact_oly_whole_controls": [dict(item) for item in right_oly],
                        "oly_component_inference": 0,
                    },
                )
            )

        if line_final or close_right:
            output[target, "F07_LINE_FINAL_OR_CLOSE"].append(
                _evidence_record(
                    occurrence,
                    "F07_LINE_FINAL_OR_CLOSE",
                    ("TERMINAL_GEOMETRY",),
                    {
                        "line_final": int(line_final),
                        "eligible_right_close_evidence": [
                            dict(item) for item in close_right
                        ],
                    },
                )
            )

        content = [
            donor
            for donor in _eligible_donors(occurrence, "R2")
            if str(donor.get("surface")) in {"cthy", "chor", "shor"}
        ]
        if content:
            output[target, "F10_PART_OR_CONTENT_R2"].append(
                _evidence_record(
                    occurrence,
                    "F10_PART_OR_CONTENT_R2",
                    ("CONTENT_CONTACT",),
                    {
                        "eligible_complete_content_donors": [
                            _donor_brief(item) for item in content
                        ],
                        "concrete_part_identity_imported": 0,
                    },
                )
            )

        h1_bounded = bool(
            target in h1_surfaces
            and any(str(item.get("direction")) == "RIGHT" for item in bounded)
        )
        if h1_bounded:
            output[target, "F11_H1_BOUNDED_VALUE"].append(
                _evidence_record(
                    occurrence,
                    "F11_H1_BOUNDED_VALUE",
                    ("BOUNDED_RECORD",),
                    {
                        "h1_target": 1,
                        "exact_right_x_daiin": [
                            dict(item)
                            for item in bounded
                            if str(item.get("direction")) == "RIGHT"
                        ],
                    },
                )
            )

        locus = str(occurrence["locus"])
        parallel = value_cells_by_locus.get(locus, [])
        if len(parallel) >= 2 and _target_is_control_member(occurrence, core):
            output[target, "F12_PARALLEL_VALUE_CELL"].append(
                _evidence_record(
                    occurrence,
                    "F12_PARALLEL_VALUE_CELL",
                    ("PARALLEL_RECORD",),
                    {
                        "exact_value_cells_on_line": [dict(item) for item in parallel],
                        "parallel_cell_count": len(parallel),
                    },
                )
            )

        left_donors = [
            donor
            for donor in _eligible_donors(occurrence, "LINE")
            if str(donor.get("direction")) == "LEFT"
        ]
        right_donors = [
            donor
            for donor in _eligible_donors(occurrence, "LINE")
            if str(donor.get("direction")) == "RIGHT"
        ]
        medial = str(occurrence.get("line_position")) == "MIDDLE"
        if medial and left_donors and right_donors and not own_value:
            output[target, "F14_MEDIAL_TWO_SIDED_LINKER"].append(
                _evidence_record(
                    occurrence,
                    "F14_MEDIAL_TWO_SIDED_LINKER",
                    ("TWO_SIDED_LINKER_GEOMETRY",),
                    {
                        "medial": 1,
                        "left_eligible_donor_count": len(left_donors),
                        "right_eligible_donor_count": len(right_donors),
                        "left_nearest": _donor_brief(
                            min(left_donors, key=lambda item: _as_int(item.get("distance"), 9999))
                        ),
                        "right_nearest": _donor_brief(
                            min(right_donors, key=lambda item: _as_int(item.get("distance"), 9999))
                        ),
                        "own_value_or_bounded_cell_binding": 0,
                    },
                )
            )

        transitions = _transition_pairs(occurrence)
        if transitions:
            output[target, "F15_STATE_TRANSITION_BRIDGE"].append(
                _evidence_record(
                    occurrence,
                    "F15_STATE_TRANSITION_BRIDGE",
                    ("STATE_TRANSITION_DIRECTION",),
                    {
                        "transitions": transitions,
                        "direction_labels": sorted(
                            {str(item["direction"]) for item in transitions}
                        ),
                    },
                )
            )
    return dict(output)


def _strongest_locus(
    evidence: Sequence[Mapping[str, object]], frame_ids: set[str] | None = None
) -> str:
    by_locus: defaultdict[str, list[Mapping[str, object]]] = defaultdict(list)
    for row in evidence:
        if frame_ids is not None and str(row.get("frame_id")) not in frame_ids:
            continue
        by_locus[str(row.get("locus"))].append(row)
    if not by_locus:
        return "NONE"

    def score(item: tuple[str, list[Mapping[str, object]]]) -> tuple[int, int, int, str]:
        locus, rows = item
        axes = {
            str(axis)
            for row in rows
            for axis in row.get("axis_families", ())
        }
        details = sum(
            len(row.get("detail", {})) if isinstance(row.get("detail"), Mapping) else 0
            for row in rows
        )
        return (-len(axes), -len(rows), -details, locus)

    return min(by_locus.items(), key=score)[0]


def _aggregate_frame(
    target: str,
    frame_id: str,
    spec: Mapping[str, object],
    evidence: Sequence[Mapping[str, object]],
    target_occurrences: int,
) -> dict[str, object]:
    pages = sorted({str(row["page"]) for row in evidence})
    loci = sorted({str(row["locus"]) for row in evidence})
    strongest = _strongest_locus(evidence)
    remaining = [row for row in evidence if str(row["locus"]) != strongest]
    remaining_pages = sorted({str(row["page"]) for row in remaining})
    remaining_loci = sorted({str(row["locus"]) for row in remaining})
    axes = sorted(
        {
            str(axis)
            for row in evidence
            for axis in row.get("axis_families", ())
        }
    )
    remaining_axes = sorted(
        {
            str(axis)
            for row in remaining
            for axis in row.get("axis_families", ())
        }
    )
    minimum_pages = _as_int(spec.get("minimum_distinct_pages_total"), 2)
    minimum_remaining = _as_int(spec.get("minimum_remaining_support_pages"), 1)
    total_gate = len(pages) >= minimum_pages
    loo_gate = len(remaining_pages) >= minimum_remaining
    selected = bool(evidence) and total_gate and loo_gate

    direction_counts: Counter[str] = Counter()
    direction_pages: defaultdict[str, set[str]] = defaultdict(set)
    for row in evidence:
        detail = row.get("detail", {})
        if not isinstance(detail, Mapping):
            continue
        for label in detail.get("direction_labels", ()):
            direction_counts[str(label)] += 1
            direction_pages[str(label)].add(str(row["page"]))
    direction_total = sum(direction_counts.values())
    majority_direction = "NONE"
    majority_count = 0
    if direction_counts:
        majority_direction, majority_count = min(
            direction_counts.items(), key=lambda item: (-item[1], item[0])
        )
    majority_share = 0.0 if direction_total == 0 else majority_count / direction_total

    failure_reasons: list[str] = []
    if not evidence:
        failure_reasons.append("NO_OBSERVED_FRAME")
    if evidence and not total_gate:
        failure_reasons.append("TOTAL_PAGE_GATE_FAILED")
    if evidence and not loo_gate:
        failure_reasons.append("STRONGEST_LOCUS_LOO_FAILED")

    return {
        "target_surface": target,
        "frame_id": frame_id,
        "frame_name_de": str(spec.get("frame_name_de", "")),
        "radius": str(spec.get("radius", "")),
        "direction_rule": str(spec.get("direction", "")),
        "count_unit": str(spec.get("count_unit", "")),
        "support_occurrences": len(evidence),
        "target_reader_exact_occurrences": target_occurrences,
        "normalised_support_rate": _rounded(
            0.0 if target_occurrences == 0 else len(evidence) / target_occurrences
        ),
        "support_loci": len(loci),
        "support_pages": len(pages),
        "support_page_list": pages,
        "observed_axis_families": axes,
        "strongest_support_locus": strongest,
        "strongest_support_page": next(
            (
                str(row["page"])
                for row in evidence
                if str(row["locus"]) == strongest
            ),
            "NONE",
        ),
        "strongest_locus_support_occurrences": sum(
            str(row["locus"]) == strongest for row in evidence
        ),
        "loo_remaining_occurrences": len(remaining),
        "loo_remaining_loci": len(remaining_loci),
        "loo_remaining_pages": len(remaining_pages),
        "loo_remaining_page_list": remaining_pages,
        "loo_remaining_axis_families": remaining_axes,
        "minimum_distinct_pages_total": minimum_pages,
        "minimum_remaining_support_pages": minimum_remaining,
        "passes_total_page_gate": int(total_gate),
        "passes_strongest_locus_loo": int(loo_gate),
        "frame_selected": int(selected),
        "failure_reasons": failure_reasons,
        "state_transition_direction_counts": dict(sorted(direction_counts.items())),
        "state_transition_direction_page_counts": {
            key: len(value) for key, value in sorted(direction_pages.items())
        },
        "majority_transition_direction": majority_direction,
        "majority_transition_share": _rounded(majority_share),
        "description_de": str(spec.get("description_de", "")),
        "anchor_source": str(spec.get("anchor_source", "")),
        "union_ed2_donor_gate_required": _as_int(
            spec.get("target_and_form_family_donors_blocked"), 1
        ),
        **CLAIM_ZERO_FIELDS,
    }


def _meta_replication_frame(
    target: str,
    spec: Mapping[str, object],
    evidence: Sequence[Mapping[str, object]],
    target_occurrences: int,
) -> dict[str, object]:
    strongest = _strongest_locus(evidence)
    remaining = [row for row in evidence if str(row.get("locus")) != strongest]
    pages = sorted({str(row["page"]) for row in evidence})
    remaining_pages = sorted({str(row["page"]) for row in remaining})
    axes = sorted(
        {
            str(axis)
            for row in remaining
            for axis in row.get("axis_families", ())
            if str(axis) != "REPLICATION_CONTROL"
        }
    )
    passed = len(pages) >= 2 and len(remaining_pages) >= 1 and bool(axes)
    return {
        "target_surface": target,
        "frame_id": "F13_SECOND_PAGE_AFTER_ABLATION",
        "frame_name_de": str(spec.get("frame_name_de", "")),
        "radius": "META",
        "direction_rule": "NONE",
        "count_unit": str(spec.get("count_unit", "")),
        "support_occurrences": len(evidence),
        "target_reader_exact_occurrences": target_occurrences,
        "normalised_support_rate": _rounded(
            0.0 if target_occurrences == 0 else len(evidence) / target_occurrences
        ),
        "support_loci": len({str(row["locus"]) for row in evidence}),
        "support_pages": len(pages),
        "support_page_list": pages,
        "observed_axis_families": sorted(
            {
                str(axis)
                for row in evidence
                for axis in row.get("axis_families", ())
            }
        ),
        "strongest_support_locus": strongest,
        "strongest_support_page": next(
            (str(row["page"]) for row in evidence if str(row["locus"]) == strongest),
            "NONE",
        ),
        "strongest_locus_support_occurrences": sum(
            str(row["locus"]) == strongest for row in evidence
        ),
        "loo_remaining_occurrences": len(remaining),
        "loo_remaining_loci": len({str(row["locus"]) for row in remaining}),
        "loo_remaining_pages": len(remaining_pages),
        "loo_remaining_page_list": remaining_pages,
        "loo_remaining_axis_families": axes,
        "minimum_distinct_pages_total": 2,
        "minimum_remaining_support_pages": 1,
        "passes_total_page_gate": int(len(pages) >= 2),
        "passes_strongest_locus_loo": int(len(remaining_pages) >= 1),
        "frame_selected": int(passed),
        "failure_reasons": [] if passed else ["NO_REPLICATED_OBSERVATIONAL_FRAME"],
        "state_transition_direction_counts": {},
        "state_transition_direction_page_counts": {},
        "majority_transition_direction": "NONE",
        "majority_transition_share": 0.0,
        "description_de": str(spec.get("description_de", "")),
        "anchor_source": str(spec.get("anchor_source", "")),
        "union_ed2_donor_gate_required": 1,
        **CLAIM_ZERO_FIELDS,
    }


def _build_frame_tables(
    core: Mapping[str, object], frame_specs: Sequence[Mapping[str, object]]
) -> tuple[
    list[dict[str, object]],
    list[dict[str, object]],
    dict[tuple[str, str], list[dict[str, object]]],
]:
    specs = _unique_rows(frame_specs, "frame_id", "frame")
    if {_frame_key(key) for key in specs} != set(FRAME_IDS):
        raise ValueError("frame specs must contain exactly F01 through F15")
    by_short = {_frame_key(key): key for key in specs}
    evidence = _frame_occurrence_evidence(core)
    exact_counts = Counter(
        str(row.get("surface"))
        for row in core.get("occurrences", ())
        if isinstance(row, Mapping)
    )
    frame_rows: list[dict[str, object]] = []
    evidence_rows: list[dict[str, object]] = []
    for target in TARGETS:
        target_all_evidence: list[dict[str, object]] = []
        for short in FRAME_IDS:
            full = by_short[short]
            if short == "F13":
                continue
            selected = evidence.get((target, full), [])
            target_all_evidence.extend(selected)
            frame_rows.append(
                _aggregate_frame(target, full, specs[full], selected, exact_counts[target])
            )
            evidence_rows.extend(selected)
        f13 = by_short["F13"]
        frame_rows.append(
            _meta_replication_frame(
                target, specs[f13], target_all_evidence, exact_counts[target]
            )
        )
    frame_rows.sort(key=lambda row: (str(row["target_surface"]), str(row["frame_id"])))
    evidence_rows.sort(
        key=lambda row: (
            str(row["target_surface"]),
            str(row["frame_id"]),
            str(row["page"]),
            str(row["locus"]),
            _as_int(row["ordinal"]),
        )
    )
    return frame_rows, evidence_rows, evidence


def _frame_ids_in_expression(expression: object) -> set[str]:
    return {
        token
        for token in _expression_identifiers(expression)
        if token.startswith("F") and token[:3] in FRAME_IDS
    }


def _evidence_after_locus(
    evidence: Mapping[tuple[str, str], list[dict[str, object]]],
    target: str,
    frame_id: str,
    excluded_locus: str,
) -> list[dict[str, object]]:
    return [
        row
        for row in evidence.get((target, frame_id), [])
        if str(row.get("locus")) != excluded_locus
    ]


def _transition_consistency(
    rows: Sequence[Mapping[str, object]], minimum_share: float = 0.75
) -> dict[str, object]:
    counts: Counter[str] = Counter()
    pages: defaultdict[str, set[str]] = defaultdict(set)
    for row in rows:
        detail = row.get("detail", {})
        if not isinstance(detail, Mapping):
            continue
        for direction in set(str(item) for item in detail.get("direction_labels", ())):
            counts[direction] += 1
            pages[direction].add(str(row.get("page")))
    total = sum(counts.values())
    if not counts:
        return {
            "direction_counts": {},
            "majority_direction": "NONE",
            "majority_count": 0,
            "majority_pages": 0,
            "majority_share": 0.0,
            "consistent": False,
        }
    direction, count = min(counts.items(), key=lambda item: (-item[1], item[0]))
    share = count / total
    return {
        "direction_counts": dict(sorted(counts.items())),
        "majority_direction": direction,
        "majority_count": count,
        "majority_pages": len(pages[direction]),
        "majority_share": _rounded(share),
        "consistent": bool(share >= minimum_share and len(pages[direction]) >= 2),
    }


def _own_binding_pages(core: Mapping[str, object], target: str) -> set[str]:
    pages: set[str] = set()
    for row in core.get("occurrences", ()):
        if not isinstance(row, Mapping) or str(row.get("surface")) != target:
            continue
        if _target_has_own_value_binding(row, core):
            pages.add(str(row.get("page")))
    return pages


def _build_role_scoreboard(
    core: Mapping[str, object],
    role_specs: Sequence[Mapping[str, object]],
    frame_rows: Sequence[Mapping[str, object]],
    evidence: Mapping[tuple[str, str], list[dict[str, object]]],
) -> tuple[list[dict[str, object]], dict[str, str]]:
    specs = _unique_rows(role_specs, "role_model_id", "role")
    if {key.split("_", 1)[0] for key in specs} != set(ROLE_PREFIXES):
        raise ValueError("role specs must contain exactly R01 through R05")
    frames = {
        (str(row["target_surface"]), str(row["frame_id"])): row
        for row in frame_rows
    }
    rows: list[dict[str, object]] = []

    for target in TARGETS:
        base_truth = {
            _frame_key(frame_id): bool(_as_int(row["frame_selected"]))
            for (surface, frame_id), row in frames.items()
            if surface == target
        }
        base_truth.update(
            {
                frame_id: bool(_as_int(row["frame_selected"]))
                for (surface, frame_id), row in frames.items()
                if surface == target
            }
        )
        base_truth["ON_TWO_PAGES_WITHOUT_DIRECTION"] = bool(
            len(
                {
                    str(item["page"])
                    for frame_id in (
                        "F01_AMOUNT_DIRECT",
                        "F02_VALUE_DIRECT",
                        "F11_H1_BOUNDED_VALUE",
                    )
                    for item in evidence.get((target, frame_id), [])
                }
            )
            >= 2
        )
        base_truth["ON_SAME_TARGET_OCCURRENCE"] = True
        own_pages = _own_binding_pages(core, target)

        for role_id, spec in specs.items():
            positive_expression = str(spec.get("positive_signature_expression", ""))
            contradiction_expression = str(
                spec.get("contradictory_signature_expression", "NONE")
            )
            positive_frames = _frame_ids_in_expression(positive_expression)
            contradiction_frames = _frame_ids_in_expression(contradiction_expression)
            relevant_frames = positive_frames | contradiction_frames
            if role_id.startswith("R04_"):
                # F12 is corroboration for a value-bearing record cell, never
                # a prerequisite and never a substitute for F02/F11.
                relevant_frames.add("F12_PARALLEL_VALUE_CELL")
            if role_id.startswith("R05_"):
                relevant_frames.update(
                    {
                        "F14_MEDIAL_TWO_SIDED_LINKER",
                        "F15_STATE_TRANSITION_BRIDGE",
                        "F16_RELATIONAL_AMOUNT_ORDER",
                    }
                )
            role_evidence = [
                item
                for frame_id in relevant_frames
                for item in evidence.get((target, frame_id), [])
            ]
            strongest = _strongest_locus(role_evidence, relevant_frames)
            role_pages = {str(item["page"]) for item in role_evidence}
            remaining_rows = [
                item for item in role_evidence if str(item["locus"]) != strongest
            ]
            remaining_pages = {str(item["page"]) for item in remaining_rows}

            loo_truth: dict[str, bool] = {}
            for frame_id in {
                str(row["frame_id"])
                for row in frame_rows
                if str(row["target_surface"]) == target
            }:
                remaining = _evidence_after_locus(
                    evidence, target, frame_id, strongest
                )
                value = bool(remaining)
                loo_truth[frame_id] = value
                loo_truth[_frame_key(frame_id)] = value
            loo_truth["ON_TWO_PAGES_WITHOUT_DIRECTION"] = bool(
                len(
                    {
                        str(item["page"])
                        for frame_id in (
                            "F01_AMOUNT_DIRECT",
                            "F02_VALUE_DIRECT",
                            "F11_H1_BOUNDED_VALUE",
                        )
                        for item in _evidence_after_locus(
                            evidence, target, frame_id, strongest
                        )
                    }
                )
                >= 2
            )
            loo_truth["ON_SAME_TARGET_OCCURRENCE"] = True

            positive = _evaluate_expression(positive_expression, base_truth)
            contradiction = _evaluate_expression(contradiction_expression, base_truth)
            positive_loo = _evaluate_expression(positive_expression, loo_truth)

            conjunction_detail: dict[str, object] = {}
            if role_id.startswith("R03_"):
                # PRODUCT/RESULT is a context claim: value/amount evidence at
                # one occurrence cannot be joined to process/terminal evidence
                # from another page.  Build both the total and LOO gates from
                # complete same-occurrence signatures only.
                occurrence_truth = _candidate_occurrence_truth(
                    target,
                    positive_expression,
                    positive_frames,
                    evidence,
                    {},
                )
                supporting_ids = {
                    occurrence_id
                    for occurrence_id, detail in occurrence_truth.items()
                    if _as_int(detail.get("expression_pass"))
                }
                role_evidence = [
                    item
                    for frame_id in positive_frames
                    for item in evidence.get((target, frame_id), [])
                    if str(item.get("target_occurrence_id")) in supporting_ids
                ]
                strongest = _strongest_locus(role_evidence, positive_frames)
                role_pages = {str(item["page"]) for item in role_evidence}
                remaining_rows = [
                    item
                    for item in role_evidence
                    if str(item.get("locus")) != strongest
                ]
                remaining_pages = {str(item["page"]) for item in remaining_rows}
                loo_occurrence_truth = _candidate_occurrence_truth(
                    target,
                    positive_expression,
                    positive_frames,
                    evidence,
                    {},
                    strongest,
                )
                loo_supporting_ids = {
                    occurrence_id
                    for occurrence_id, detail in loo_occurrence_truth.items()
                    if _as_int(detail.get("expression_pass"))
                }
                positive = bool(supporting_ids)
                positive_loo = bool(loo_supporting_ids)
                conjunction_detail = {
                    "same_occurrence_conjunction_required": 1,
                    "supporting_occurrence_ids": sorted(supporting_ids),
                    "supporting_occurrence_count": len(supporting_ids),
                    "supporting_pages": sorted(role_pages),
                    "loo_supporting_occurrence_ids": sorted(loo_supporting_ids),
                    "loo_supporting_occurrence_count": len(loo_supporting_ids),
                    "loo_supporting_pages": sorted(remaining_pages),
                }
            minimum_pages = _as_int(spec.get("minimum_distinct_pages_total"), 2)
            minimum_remaining = _as_int(
                spec.get("minimum_remaining_support_pages"), 1
            )
            total_page_gate = len(role_pages) >= minimum_pages
            loo_gate = len(remaining_pages) >= minimum_remaining and positive_loo

            r05_detail: dict[str, object] = {}
            if role_id.startswith("R05_"):
                f14 = evidence.get((target, "F14_MEDIAL_TWO_SIDED_LINKER"), [])
                f15 = evidence.get((target, "F15_STATE_TRANSITION_BRIDGE"), [])
                f16 = evidence.get((target, "F16_RELATIONAL_AMOUNT_ORDER"), [])
                f14_occurrence_ids = {
                    str(item.get("target_occurrence_id")) for item in f14
                }
                local_f15 = [
                    item
                    for item in f15
                    if str(item.get("target_occurrence_id")) in f14_occurrence_ids
                ]
                local_f16 = [
                    item
                    for item in f16
                    if str(item.get("target_occurrence_id")) in f14_occurrence_ids
                ]
                # F14 supplies only the local conjunction gate.  It contributes
                # no page, locus, or ablation support of its own.
                role_evidence = [*local_f15, *local_f16]
                strongest = _strongest_locus(role_evidence)
                role_pages = {str(item["page"]) for item in role_evidence}
                remaining_rows = [
                    item
                    for item in role_evidence
                    if str(item.get("locus")) != strongest
                ]
                remaining_pages = {str(item["page"]) for item in remaining_rows}
                f15_loo = [
                    item
                    for item in local_f15
                    if str(item.get("locus")) != strongest
                ]
                f16_loo = [
                    item
                    for item in local_f16
                    if str(item.get("locus")) != strongest
                ]
                consistency = _transition_consistency(local_f15)
                amount_orientation = _transition_consistency(local_f16)
                # F14 is common background geometry.  R05 is selectable only
                # with an independent state-transition or relational-amount
                # frame.  Adjacent AMOUNT is positive F16 evidence, not an own
                # binding; only repeated VALUE/BOUNDED binding contradicts.
                f15_branch = bool(local_f15)
                f16_branch = bool(local_f16)
                positive = bool(role_evidence and len(own_pages) < 2)
                consistency_loo = _transition_consistency(f15_loo)
                f15_loo_branch = bool(f15_loo)
                f16_loo_branch = bool(f16_loo)
                positive_loo = bool(
                    (f15_loo_branch or f16_loo_branch)
                    and len(own_pages) < 2
                )
                contradiction = len(own_pages) >= 2
                total_page_gate = len(role_pages) >= minimum_pages
                loo_gate = len(remaining_pages) >= minimum_remaining and positive_loo
                conjunction_detail = {
                    "same_occurrence_conjunction_required": 1,
                    "f14_contributes_support_pages": 0,
                    "local_discriminating_occurrence_ids": sorted(
                        {
                            str(item.get("target_occurrence_id"))
                            for item in role_evidence
                        }
                    ),
                    "supporting_pages": sorted(role_pages),
                    "loo_supporting_pages": sorted(remaining_pages),
                }
                r05_detail = {
                    "f14_support_occurrences": len(f14),
                    "f15_support_occurrences": len(f15),
                    "f16_support_occurrences": len(f16),
                    "local_f14_and_f15_occurrences": len(local_f15),
                    "local_f14_and_f16_occurrences": len(local_f16),
                    "f14_normalised_rate": _rounded(
                        len(f14)
                        / max(
                            1,
                            sum(
                                str(item.get("surface")) == target
                                for item in core.get("occurrences", ())
                                if isinstance(item, Mapping)
                            ),
                        )
                    ),
                    "f15_normalised_rate": _rounded(
                        len(f15)
                        / max(
                            1,
                            sum(
                                str(item.get("surface")) == target
                                for item in core.get("occurrences", ())
                                if isinstance(item, Mapping)
                            ),
                        )
                    ),
                    "f16_normalised_rate": _rounded(
                        len(f16)
                        / max(
                            1,
                            sum(
                                str(item.get("surface")) == target
                                for item in core.get("occurrences", ())
                                if isinstance(item, Mapping)
                            ),
                        )
                    ),
                    "transition_consistency": consistency,
                    "loo_transition_consistency": consistency_loo,
                    "amount_orientation_counts": amount_orientation,
                    "f15_branch_pass": int(f15_branch),
                    "f16_branch_pass": int(f16_branch),
                    "loo_f15_branch_pass": int(f15_loo_branch),
                    "loo_f16_branch_pass": int(f16_loo_branch),
                    "own_value_or_bounded_pages": sorted(own_pages),
                    "r05_requires_f14_and_f15_or_f16": 1,
                    "r05_rough_f14_alone_has_zero_selection_credit": 1,
                    "f16_amount_adjacency_is_not_own_binding": 1,
                }

            selected = bool(
                positive
                and not contradiction
                and total_page_gate
                and loo_gate
            )
            rough_rival = bool(
                role_id.startswith("R05_")
                and evidence.get((target, "F14_MEDIAL_TWO_SIDED_LINKER"), [])
                and not selected
            )
            reinforcement = int(
                role_id.startswith("R04_")
                and base_truth.get("F12_PARALLEL_VALUE_CELL", False)
            )
            score = _rounded(min(1.0,
                0.35 * int(positive)
                + 0.20 * int(total_page_gate)
                + 0.25 * int(loo_gate)
                + 0.20 * int(not contradiction)
                + 0.05 * reinforcement
            ))
            reasons: list[str] = []
            if not positive:
                reasons.append("POSITIVE_SIGNATURE_FAILED")
            if contradiction:
                reasons.append("CONTRADICTORY_SIGNATURE_TRIGGERED")
            if not total_page_gate:
                reasons.append("TOTAL_PAGE_GATE_FAILED")
            if not loo_gate:
                reasons.append("STRONGEST_LOCUS_LOO_FAILED")
            if rough_rival:
                reasons.append("RIVAL_ONLY_F14_NONDISCRIMINATIVE")
            rows.append(
                {
                    "target_surface": target,
                    "role_model_id": role_id,
                    "role_name_de": str(spec.get("role_name_de", "")),
                    "positive_signature_expression": positive_expression,
                    "contradictory_signature_expression": contradiction_expression,
                    "positive_signature_pass": int(positive),
                    "contradictory_signature_triggered": int(contradiction),
                    "support_pages": len(role_pages),
                    "support_loci": len({str(item["locus"]) for item in role_evidence}),
                    "strongest_support_locus": strongest,
                    "loo_remaining_pages": len(remaining_pages),
                    "loo_positive_signature_pass": int(positive_loo),
                    "passes_total_page_gate": int(total_page_gate),
                    "passes_strongest_locus_loo": int(loo_gate),
                    "role_score": score,
                    "dispatch_priority": _as_int(spec.get("dispatch_priority"), 99),
                    "role_gate_pass": int(selected),
                    "role_selected": 0,
                    "role_disposition": (
                        "SELECTABLE_PENDING_PRIORITY"
                        if selected
                        else "RIVAL_ONLY"
                        if rough_rival
                        else "NOT_SELECTED"
                    ),
                    "failure_reasons": reasons,
                    "portable_output_de": str(spec.get("portable_output_de", "")),
                    "failure_output_de": str(spec.get("failure_output_de", "")),
                    "special_gate_detail": r05_detail,
                    "same_context_conjunction_detail": conjunction_detail,
                    "f12_parallel_value_reinforcement": reinforcement,
                    **CLAIM_ZERO_FIELDS,
                }
            )

    winners: dict[str, str] = {}
    for target in TARGETS:
        target_rows = [row for row in rows if row["target_surface"] == target]
        ranked = sorted(
            target_rows,
            key=lambda row: (
                -_as_int(row["role_gate_pass"]),
                _as_int(row["dispatch_priority"], 99),
                -float(row["role_score"]),
                str(row["role_model_id"]),
            ),
        )
        for rank, row in enumerate(ranked, 1):
            row["role_rank"] = rank
        if _as_int(ranked[0]["role_gate_pass"]):
            winners[target] = str(ranked[0]["role_model_id"])
            ranked[0]["role_selected"] = 1
            ranked[0]["role_disposition"] = "SELECTED_BY_DISPATCH_PRIORITY"
            for rival in ranked[1:]:
                if _as_int(rival["role_gate_pass"]):
                    rival["role_disposition"] = "SUPPORTED_RIVAL_LOWER_PRIORITY"
        else:
            winners[target] = "OPEN"
    rows.sort(key=lambda row: (str(row["target_surface"]), _as_int(row["role_rank"])))
    return rows, winners


def _historical_rows_for_candidate(
    predictions: Sequence[Mapping[str, object]], candidate: Mapping[str, object]
) -> list[dict[str, object]]:
    target = str(candidate.get("target_surface", ""))
    candidate_class = str(candidate.get("candidate_class", ""))
    accepted_types = {candidate_class}
    accepted_types.update(HISTORICAL_TYPE_FAMILIES.get(candidate_class, ()))
    accepted_types.update(
        HISTORICAL_TARGET_TYPE_FAMILIES.get((target, candidate_class), ())
    )
    output: list[dict[str, object]] = []
    for row in predictions:
        # The actual historical deck is target-specific.  A blank or different
        # target must never be copied onto every identity card.
        if str(row.get("target_surface", "")) != target:
            continue
        historical_type = str(row.get("candidate_type", ""))
        if historical_type not in accepted_types:
            continue
        source_ids = _pipe(row.get("historical_source_ids"))
        necessary = str(row.get("necessary_observable_frames", ""))
        frame_references = sorted(
            set(re.findall(r"\bF\d{2}_[A-Za-z0-9_]+\b", necessary))
        )
        independent_references = sorted(
            set(re.findall(r"\bindependent_[A-Za-z0-9_]+\b", necessary))
        )
        preserved_fields = {
            str(key): (
                value
                if value is None or isinstance(value, (str, int, float, bool))
                else str(value)
            )
            for key, value in row.items()
        }
        output.append(
            {
                **preserved_fields,
                "target_surface": target,
                "candidate_type": historical_type,
                "candidate_label_de": str(row.get("candidate_label_de", "")),
                "renderer_de": str(row.get("renderer_de", "")),
                "historical_source_id_list": source_ids,
                "observable_frame_references": frame_references,
                "independent_observable_requirements": independent_references,
                "identity_candidate_class": candidate_class,
                "match_basis": (
                    "EXACT_CANDIDATE_TYPE"
                    if historical_type == candidate_class
                    else "DECLARED_TYPE_FAMILY"
                ),
                "historical_analogy_only": 1,
                "historical_category_fit_credit": 0,
                "independent_voynich_discriminator": 0,
                "creates_voynich_evidence": 0,
                "eva_latin_credit": 0,
                "substring_export_credit": 0,
                "confirmed_lexeme": 0,
            }
        )
    return output


def _historical_prediction_metadata(
    predictions: Sequence[Mapping[str, object]],
    identity_rows: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    """Expose real comparison-deck provenance without scoring it."""

    fields = sorted({str(key) for row in predictions for key in row})
    target_counts = Counter(str(row.get("target_surface", "")) for row in predictions)
    source_ids = sorted(
        {
            source_id
            for row in predictions
            for source_id in _pipe(row.get("historical_source_ids"))
        }
    )
    frame_references = sorted(
        {
            reference
            for row in predictions
            for reference in re.findall(
                r"\bF\d{2}_[A-Za-z0-9_]+\b",
                str(row.get("necessary_observable_frames", "")),
            )
        }
    )
    independent_references = sorted(
        {
            reference
            for row in predictions
            for reference in re.findall(
                r"\bindependent_[A-Za-z0-9_]+\b",
                str(row.get("necessary_observable_frames", "")),
            )
        }
    )
    input_ids = {
        str(row.get("prediction_id", ""))
        for row in predictions
        if str(row.get("prediction_id", ""))
    }
    matched_ids = {
        str(history.get("prediction_id", ""))
        for identity in identity_rows
        for history in identity.get("historical_predictions", ())
        if isinstance(history, Mapping) and str(history.get("prediction_id", ""))
    }
    return {
        "input_fields": fields,
        "input_prediction_ids": sorted(input_ids),
        "input_target_counts": dict(sorted(target_counts.items())),
        "historical_source_ids": source_ids,
        "observable_frame_references": frame_references,
        "independent_observable_requirements": independent_references,
        "matched_prediction_ids": sorted(matched_ids),
        "unmatched_prediction_ids": sorted(input_ids - matched_ids),
        "matched_unique_prediction_count": len(matched_ids),
        "candidate_attachment_count": sum(
            _as_int(row.get("historical_prediction_count"))
            for row in identity_rows
        ),
        "target_exact_match_required": 1,
        "declared_type_family_match_required": 1,
        "historical_predictions_create_voynich_evidence": 0,
    }


def _candidate_occurrence_truth(
    target: str,
    expression: str,
    frame_ids: set[str],
    evidence: Mapping[tuple[str, str], list[dict[str, object]]],
    role_truth: Mapping[str, bool],
    excluded_locus: str = "NONE",
) -> dict[str, dict[str, object]]:
    occurrence_ids = {
        str(row["target_occurrence_id"])
        for frame_id in frame_ids
        for row in evidence.get((target, frame_id), [])
        if str(row.get("locus")) != excluded_locus
    }
    result: dict[str, dict[str, object]] = {}
    for occurrence_id in sorted(occurrence_ids):
        truth = dict(role_truth)
        truth["ON_SAME_TARGET_OCCURRENCE"] = True
        axes: set[str] = set()
        contributing_frames: list[str] = []
        occurrence_rows: list[Mapping[str, object]] = []
        for frame_id in frame_ids:
            matching = [
                row
                for row in evidence.get((target, frame_id), [])
                if str(row.get("target_occurrence_id")) == occurrence_id
                and str(row.get("locus")) != excluded_locus
            ]
            present = bool(matching)
            truth[frame_id] = present
            truth[_frame_key(frame_id)] = present
            if present:
                occurrence_rows.extend(matching)
                contributing_frames.append(frame_id)
                axes.add(FRAME_AXIS_FAMILY.get(frame_id, frame_id))
        passed = _evaluate_expression(expression, truth)
        result[occurrence_id] = {
            "expression_pass": int(passed),
            "axis_families": sorted(axes),
            "contributing_frames": sorted(contributing_frames),
            "page": str(occurrence_rows[0]["page"]) if occurrence_rows else "NONE",
            "locus": str(occurrence_rows[0]["locus"]) if occurrence_rows else "NONE",
        }
    return result


def _candidate_fatal_counter(
    candidate: Mapping[str, object],
    core: Mapping[str, object],
    target: str,
    frame_lookup: Mapping[tuple[str, str], Mapping[str, object]],
    evidence: Mapping[tuple[str, str], list[dict[str, object]]],
    candidate_loo_pass: bool,
    loo_axis_count: int,
    historical_rows: Sequence[Mapping[str, object]],
) -> tuple[bool, list[str]]:
    text = str(candidate.get("fatal_counter_signature", "NONE")).upper()
    if text in {"", "NONE"}:
        return False, []
    reasons: list[str] = []
    structural_replication_failed = not candidate_loo_pass or loo_axis_count < 2
    if "NO_SECOND_PAGE" in text and structural_replication_failed:
        reasons.append("NO_SECOND_PAGE_SIGNATURE_AFTER_ABLATION")
    if "ONLY_ONE_AMOUNT_PLUS_PROCESS_LOCUS" in text:
        loci = {
            str(row["locus"])
            for frame_id in ("F01_AMOUNT_DIRECT", "F06_TARGET_BEFORE_PROCESS")
            for row in evidence.get((target, frame_id), [])
        }
        if len(loci) <= 1:
            reasons.append("ONLY_ONE_AMOUNT_PLUS_PROCESS_LOCUS")
    if "ONLY_POST_MOIST_H1_FIELD" in text:
        if not (
            _as_int(frame_lookup[target, "F03_DRY_R2"]["frame_selected"])
            and (
                _as_int(frame_lookup[target, "F01_AMOUNT_DIRECT"]["frame_selected"])
                or _as_int(frame_lookup[target, "F02_VALUE_DIRECT"]["frame_selected"])
            )
        ):
            reasons.append("ONLY_POST_MOIST_H1_FIELD_WITHOUT_DRY_AMOUNT")
    if "NO_PROCESS_PASS_CLOSE_OR_RESULT_GEOMETRY" in text:
        if not (
            _as_int(frame_lookup[target, "F06_TARGET_BEFORE_PROCESS"]["frame_selected"])
            or _as_int(frame_lookup[target, "F07_LINE_FINAL_OR_CLOSE"]["frame_selected"])
        ):
            reasons.append("NO_PROCESS_PASS_CLOSE_OR_RESULT_GEOMETRY")
    if "REPEATED_AMOUNT_OR_BOUND_VALUE_WITHOUT_PROCESS_DIRECTION" in text:
        if len(_own_binding_pages(core, target)) >= 2 and not (
            _as_int(frame_lookup[target, "F05_PROCESS_SLOT_FINAL"]["frame_selected"])
            or _as_int(frame_lookup[target, "F06_TARGET_BEFORE_PROCESS"]["frame_selected"])
        ):
            reasons.append("REPEATED_VALUE_BINDING_WITHOUT_PROCESS_DIRECTION")
    if "REPEATED_OWN_EXACT_VALUE_OR_BOUNDED_FIELD" in text:
        if len(_own_binding_pages(core, target)) >= 2:
            reasons.append("REPEATED_OWN_EXACT_VALUE_OR_BOUNDED_FIELD")
    if "NO_INDEPENDENT_SEPARATION_PROCESS" in text:
        oly_pages = {
            str(row["page"])
            for row in evidence.get((target, "F06_TARGET_BEFORE_PROCESS"), [])
            if any(
                item.get("exact_oly_whole_controls")
                for item in (row.get("detail", {}),)
                if isinstance(item, Mapping)
            )
        }
        if len(oly_pages) < 2:
            reasons.append("NO_INDEPENDENT_SEPARATION_PROCESS")
    if any(
        marker in text
        for marker in (
            "NO_INDEPENDENT_ACID",
            "NO_INDEPENDENT_ALCOHOL",
            "NO_INDEPENDENT_ALCOHOL_OR_ACID",
        )
    ):
        independent = any(
            _as_int(row.get("independent_voynich_discriminator"))
            for row in historical_rows
        )
        if not independent:
            reasons.append("NO_INDEPENDENT_ALCOHOL_OR_ACID_DISCRIMINATOR")
    if "RIGHT_STATE_REQUIRED_AT_NEARLY_EVERY_LINKER_OCCURRENCE" in text:
        f14 = len(evidence.get((target, "F14_MEDIAL_TWO_SIDED_LINKER"), []))
        f15 = len(evidence.get((target, "F15_STATE_TRANSITION_BRIDGE"), []))
        if f14 and f15 / f14 >= 0.8:
            reasons.append("RIGHT_STATE_AT_NEARLY_EVERY_LINKER_OCCURRENCE")
    if "MIXED_OR_REVERSED_STATE_DIRECTIONS" in text:
        consistency = _transition_consistency(
            evidence.get((target, "F15_STATE_TRANSITION_BRIDGE"), [])
        )
        if not consistency["consistent"]:
            reasons.append("MIXED_STATE_TRANSITION_DIRECTIONS")
    # Spelling/substring warnings do not auto-fail independently supported
    # cards.  They have zero evidence credit and become fatal only when the
    # observational two-axis gate has already failed.
    if any(marker in text for marker in ("EVA_SPELLING_ONLY", "VISIBLE_OL_SUBSTRING_ONLY")):
        if structural_replication_failed:
            reasons.append("SPELLING_OR_SUBSTRING_ONLY_AFTER_STRUCTURAL_FAILURE")
    return bool(reasons), reasons


def _build_identity_scoreboard(
    core: Mapping[str, object],
    identity_specs: Sequence[Mapping[str, object]],
    frame_rows: Sequence[Mapping[str, object]],
    evidence: Mapping[tuple[str, str], list[dict[str, object]]],
    role_winners: Mapping[str, str],
    historical_predictions: Sequence[Mapping[str, object]],
) -> tuple[list[dict[str, object]], dict[str, str]]:
    specs = _unique_rows(identity_specs, "identity_id", "identity")
    frame_lookup = {
        (str(row["target_surface"]), str(row["frame_id"])): row
        for row in frame_rows
    }
    rows: list[dict[str, object]] = []
    for identity_id, spec in specs.items():
        target = str(spec.get("target_surface", ""))
        if target not in TARGETS:
            raise ValueError(f"identity {identity_id} has invalid target: {target}")
        role_id = str(spec.get("required_role_model", ""))
        role_won = role_winners.get(target) == role_id
        expression = str(spec.get("required_two_axis_signature", ""))
        frame_ids = _frame_ids_in_expression(expression)
        truth: dict[str, bool] = {
            frame_id: bool(_as_int(frame_lookup[target, frame_id]["frame_selected"]))
            for frame_id in frame_ids
        }
        truth.update({_frame_key(key): value for key, value in list(truth.items())})
        for role_prefix in ROLE_PREFIXES:
            truth[f"ROLE_{role_prefix}"] = bool(
                role_won and role_id.startswith(role_prefix + "_")
            )
        expression_pass = _evaluate_expression(expression, truth)

        candidate_evidence = [
            row
            for frame_id in frame_ids
            for row in evidence.get((target, frame_id), [])
        ]
        strongest = _strongest_locus(candidate_evidence, frame_ids)
        role_truth = {_role_key(role_id): role_won}
        occurrence_truth = _candidate_occurrence_truth(
            target, expression, frame_ids, evidence, role_truth
        )
        historical_category = bool(_as_int(spec.get("historical_category_only")))
        minimum_axes = 2 if historical_category else 1
        supporting_occurrences = [
            occurrence_id
            for occurrence_id, value in occurrence_truth.items()
            if _as_int(value["expression_pass"])
            and len(value["axis_families"]) >= minimum_axes
        ]
        candidate_evidence = [
            row
            for row in candidate_evidence
            if str(row.get("target_occurrence_id")) in supporting_occurrences
        ]
        strongest = _strongest_locus(candidate_evidence, frame_ids)
        loo_occurrence_truth = _candidate_occurrence_truth(
            target, expression, frame_ids, evidence, role_truth, strongest
        )
        loo_supporting_occurrences = [
            occurrence_id
            for occurrence_id, value in loo_occurrence_truth.items()
            if _as_int(value["expression_pass"])
            and len(value["axis_families"]) >= minimum_axes
        ]
        supporting_pages = sorted(
            {str(occurrence_truth[item]["page"]) for item in supporting_occurrences}
        )
        loo_supporting_pages = sorted(
            {
                str(loo_occurrence_truth[item]["page"])
                for item in loo_supporting_occurrences
            }
        )
        observed_axes = {
            FRAME_AXIS_FAMILY.get(frame_id, frame_id)
            for frame_id in frame_ids
            if truth.get(frame_id, False)
        }
        loo_axes = {
            axis
            for occurrence_id in loo_supporting_occurrences
            for axis in loo_occurrence_truth[occurrence_id]["axis_families"]
        }
        minimum_pages = _as_int(spec.get("minimum_distinct_pages_total"), 2)
        minimum_remaining = _as_int(
            spec.get("minimum_remaining_support_pages"), 1
        )
        page_gate = len(supporting_pages) >= minimum_pages
        loo_gate = len(loo_supporting_pages) >= minimum_remaining
        axis_gate = len(observed_axes) >= minimum_axes and len(loo_axes) >= minimum_axes
        history = _historical_rows_for_candidate(historical_predictions, spec)
        fatal, fatal_reasons = _candidate_fatal_counter(
            spec,
            core,
            target,
            frame_lookup,
            evidence,
            loo_gate,
            len(loo_axes),
            history,
        )
        gate_pass = bool(
            role_won
            and expression_pass
            and page_gate
            and loo_gate
            and axis_gate
            and not fatal
        )
        score = _rounded(
            0.20 * int(role_won)
            + 0.20 * int(expression_pass)
            + 0.15 * int(page_gate)
            + 0.20 * int(loo_gate)
            + 0.20 * int(axis_gate)
            + 0.05 * int(not fatal)
        )
        failures: list[str] = []
        if not role_won:
            failures.append("REQUIRED_ROLE_DID_NOT_WIN")
        if not expression_pass:
            failures.append("REQUIRED_SIGNATURE_FAILED")
        if not page_gate:
            failures.append("TOTAL_PAGE_GATE_FAILED")
        if not loo_gate:
            failures.append("STRONGEST_LOCUS_LOO_FAILED")
        if not axis_gate:
            failures.append("INDEPENDENT_TWO_AXIS_GATE_FAILED")
        if fatal:
            failures.append("FATAL_COUNTER_SIGNATURE_TRIGGERED")
        rows.append(
            {
                "identity_id": identity_id,
                "target_surface": target,
                "required_role_model": role_id,
                "candidate_class": str(spec.get("candidate_class", "")),
                "candidate_label_de": str(spec.get("candidate_label_de", "")),
                "candidate_renderer_de": str(spec.get("candidate_renderer_de", "")),
                "candidate_status": str(spec.get("candidate_status", "")),
                "required_two_axis_signature": expression,
                "required_frame_ids": sorted(frame_ids),
                "required_role_won": int(role_won),
                "required_signature_pass": int(expression_pass),
                "minimum_independent_axis_families": minimum_axes,
                "observed_independent_axis_families": sorted(observed_axes),
                "observed_independent_axis_count": len(observed_axes),
                "supporting_pages_with_complete_signature": supporting_pages,
                "supporting_page_count": len(supporting_pages),
                "supporting_occurrence_ids_with_complete_signature": supporting_occurrences,
                "supporting_occurrence_count": len(supporting_occurrences),
                "strongest_support_locus": strongest,
                "loo_supporting_pages_with_complete_signature": loo_supporting_pages,
                "loo_supporting_page_count": len(loo_supporting_pages),
                "loo_supporting_occurrence_ids_with_complete_signature": (
                    loo_supporting_occurrences
                ),
                "loo_supporting_occurrence_count": len(loo_supporting_occurrences),
                "loo_independent_axis_families": sorted(loo_axes),
                "loo_independent_axis_count": len(loo_axes),
                "passes_total_page_gate": int(page_gate),
                "passes_strongest_locus_loo": int(loo_gate),
                "passes_independent_axis_gate": int(axis_gate),
                "fatal_counter_signature": str(
                    spec.get("fatal_counter_signature", "NONE")
                ),
                "fatal_counter_triggered": int(fatal),
                "fatal_counter_reasons": fatal_reasons,
                "historical_predictions": history,
                "historical_prediction_count": len(history),
                "historical_predictions_create_voynich_evidence": 0,
                "identity_score": score,
                "identity_gate_pass": int(gate_pass),
                "identity_selected": 0,
                "failure_reasons": failures,
                "evidence_rationale_de": str(spec.get("evidence_rationale_de", "")),
                "counterevidence_de": str(spec.get("counterevidence_de", "")),
                "tie_policy_de": str(spec.get("tie_policy_de", "")),
                **CLAIM_ZERO_FIELDS,
            }
        )

    winners: dict[str, str] = {}
    for target in TARGETS:
        target_rows = [row for row in rows if row["target_surface"] == target]
        ranked = sorted(
            target_rows,
            key=lambda row: (
                -_as_int(row["identity_gate_pass"]),
                -float(row["identity_score"]),
                -int(
                    str(row["candidate_status"])
                    in {"CURRENT_CONCRETE_DEFAULT", "REVIVED_GDT625_BASELINE"}
                ),
                str(row["identity_id"]),
            ),
        )
        for rank, row in enumerate(ranked, 1):
            row["identity_rank"] = rank
        passing = [row for row in ranked if _as_int(row["identity_gate_pass"])]
        if passing:
            top_score = float(passing[0]["identity_score"])
            tied = [row for row in passing if float(row["identity_score"]) == top_score]
            # A baseline wins exact ties.  If THEN and UNTIL tie without a
            # baseline, retain their explicit ambiguity rather than forcing a
            # connective lexeme.
            baselines = [
                row
                for row in tied
                if str(row["candidate_status"])
                in {"CURRENT_CONCRETE_DEFAULT", "REVIVED_GDT625_BASELINE"}
            ]
            winner = baselines[0] if baselines else tied[0]
            if target == "otar" and {
                str(row["identity_id"]) for row in tied
            } >= {"I24_OTAR_THEN", "I25_OTAR_UNTIL"}:
                winners[target] = "AMBIGUOUS_OTAR_THEN_UNTIL"
            else:
                winner["identity_selected"] = 1
                winners[target] = str(winner["identity_id"])
        else:
            winners[target] = "OPEN"
    rows.sort(
        key=lambda row: (str(row["target_surface"]), _as_int(row["identity_rank"]))
    )
    return rows, winners


def _build_dictionary_decisions(
    role_rows: Sequence[Mapping[str, object]],
    identity_rows: Sequence[Mapping[str, object]],
    role_winners: Mapping[str, str],
    identity_winners: Mapping[str, str],
) -> list[dict[str, object]]:
    roles = {
        (str(row["target_surface"]), str(row["role_model_id"])): row
        for row in role_rows
    }
    identities = {str(row["identity_id"]): row for row in identity_rows}
    output: list[dict[str, object]] = []
    for target in TARGETS:
        role_id = role_winners.get(target, "OPEN")
        identity_id = identity_winners.get(target, "OPEN")
        role = roles.get((target, role_id))
        target_role_rows = [
            row for row in role_rows if str(row.get("target_surface")) == target
        ]
        passing_role_rows = [
            row for row in target_role_rows if _as_int(row.get("role_gate_pass"))
        ]
        selected_role_score = (
            float(role.get("role_score", 0.0)) if role is not None else 0.0
        )
        tied_top_role_rows = [
            row
            for row in passing_role_rows
            if float(row.get("role_score", 0.0)) == selected_role_score
        ]
        role_is_priority_tiebreak = bool(
            role is not None and len(tied_top_role_rows) > 1
        )
        supported_role_rivals = [
            str(row.get("role_model_id"))
            for row in passing_role_rows
            if str(row.get("role_model_id")) != role_id
        ]
        selected_identity = identities.get(identity_id)
        target_cards = [row for row in identity_rows if row["target_surface"] == target]
        compatible_cards = [
            row
            for row in target_cards
            if role_id == "OPEN" or str(row.get("required_role_model")) == role_id
        ]
        baseline_cards = [
            row
            for row in compatible_cards
            if str(row.get("candidate_status"))
            in {"CURRENT_CONCRETE_DEFAULT", "REVIVED_GDT625_BASELINE"}
        ]
        baseline = (
            min(
                baseline_cards or compatible_cards,
                key=lambda row: (
                    -float(row.get("identity_score", 0.0)),
                    str(row.get("identity_id")),
                ),
            )
            if compatible_cards
            else None
        )

        if identity_id == "AMBIGUOUS_OTAR_THEN_UNTIL":
            working_default = "dann/bis"
            identity_label = "Folge- oder Terminativverbinder; Richtung offen"
            identity_disposition = "AMBIGUOUS_RIVAL_CLASS"
            evidence = (
                "THEN und UNTIL bestanden gleich stark; die Richtung trennt sie nicht."
            )
            counterevidence = "Keine einzelne Konnektorlesung wird erzwungen."
        elif selected_identity is not None:
            if str(selected_identity.get("required_role_model")) != role_id:
                raise ValueError(
                    f"identity/role dispatch mismatch for {target}: "
                    f"{identity_id} requires {selected_identity.get('required_role_model')}, "
                    f"role winner is {role_id}"
                )
            working_default = str(selected_identity["candidate_renderer_de"])
            identity_label = str(selected_identity["candidate_label_de"])
            identity_disposition = "SELECTED_REPLACEABLE_WHOLE_DEFAULT"
            evidence = str(selected_identity.get("evidence_rationale_de", ""))
            counterevidence = str(selected_identity.get("counterevidence_de", ""))
        elif baseline is not None:
            working_default = str(baseline.get("candidate_renderer_de", ""))
            identity_label = str(baseline.get("candidate_label_de", ""))
            identity_disposition = "PRIOR_DEFAULT_RIVAL_ONLY"
            evidence = str(baseline.get("evidence_rationale_de", ""))
            counterevidence = str(baseline.get("counterevidence_de", ""))
        else:
            working_default = (
                str(role.get("portable_output_de", ""))
                if role is not None
                else "Bedeutung offen"
            )
            identity_label = "keine rollenkompatible Identitätskarte ausgewählt"
            identity_disposition = "ROLE_ONLY_IDENTITY_OPEN"
            evidence = "Der Rollensieger besitzt noch keine bestandene Identitätskarte."
            counterevidence = (
                "Inkompatible Defaults anderer Rollen werden nicht gerendert."
            )

        role_output = (
            str(role.get("portable_output_de", ""))
            if role is not None
            else "Rolle offen; vorläufigen Ganzwortdefault nur als Rivalenkarte behalten"
        )
        rendered_identity_id = (
            str(selected_identity.get("identity_id"))
            if selected_identity is not None
            else str(baseline.get("identity_id"))
            if baseline is not None
            else "NONE"
        )
        rival_candidates = [
            row
            for row in compatible_cards
            if str(row.get("identity_id")) != rendered_identity_id
            and str(row.get("candidate_label_de")) != identity_label
            and str(row.get("candidate_status")) != "REFINEMENT_NOT_RIVAL"
        ]
        if not rival_candidates:
            rival_candidates = [
                row
                for row in target_cards
                if str(row.get("identity_id")) != rendered_identity_id
                and str(row.get("candidate_label_de")) != identity_label
                and str(row.get("candidate_status")) != "REFINEMENT_NOT_RIVAL"
            ]
            rival_candidates.sort(
                key=lambda row: (
                    -int(
                        str(row.get("candidate_class"))
                        in {"PORTABLE_BASELINE", "PORTABLE_SEQUENCE_BASELINE"}
                    ),
                    -int(
                        str(row.get("candidate_status"))
                        in {
                            "CURRENT_CONCRETE_DEFAULT",
                            "REVIVED_GDT625_BASELINE",
                        }
                    ),
                    _as_int(row.get("identity_rank"), 999),
                    str(row.get("identity_id")),
                )
            )
        primary_rival = rival_candidates[0] if rival_candidates else None
        primary_rival_label = (
            str(primary_rival.get("candidate_label_de", ""))
            if primary_rival is not None
            else "NONE"
        )
        if primary_rival_label == identity_label:
            raise ValueError(f"selected identity cannot rival itself: {target}")
        output.append(
            {
                "surface": target,
                "selected_role_model": role_id,
                "role_disposition": (
                    "SELECTED_WORKING_SPECIFICITY_TIEBREAK"
                    if role_is_priority_tiebreak
                    else "SELECTED_REPLACEABLE_WHOLE_ROLE"
                    if role_id != "OPEN"
                    else "ROLE_OPEN"
                ),
                "role_selection_basis": (
                    "SPECIFICITY_DISPATCH_PRIORITY_AMONG_EQUAL_GATE_SCORES"
                    if role_is_priority_tiebreak
                    else "UNIQUE_TOP_ROLE_GATE"
                    if role_id != "OPEN"
                    else "NO_ROLE_GATE_PASSED"
                ),
                "role_evidence_superiority": int(
                    role_id != "OPEN" and not role_is_priority_tiebreak
                ),
                "supported_role_rivals": (
                    "|".join(supported_role_rivals)
                    if supported_role_rivals
                    else "NONE"
                ),
                "portable_role_de": role_output,
                "selected_identity_id": identity_id,
                "identity_disposition": identity_disposition,
                "working_identity_label_de": identity_label,
                "working_default_de": working_default,
                "working_confidence": (
                    "C1_LOCAL_FRAME__C0_ROLE_TIEBREAK"
                    if selected_identity is not None and role_is_priority_tiebreak
                    else "C1_REPLICATED_REPLACEABLE"
                    if selected_identity is not None
                    else "C0_RIVAL_ONLY"
                ),
                "positive_evidence_de": evidence,
                "counterevidence_de": counterevidence,
                "primary_rival_de": primary_rival_label,
                "primary_rival_identity_id": (
                    str(primary_rival.get("identity_id"))
                    if primary_rival is not None
                    else "NONE"
                ),
                "identity_role_consistent": int(
                    selected_identity is None
                    or str(selected_identity.get("required_role_model")) == role_id
                ),
                "whole_form_only": 1,
                "structural_only": 0,
                **CLAIM_ZERO_FIELDS,
            }
        )
    return output


def _verify_core_boundary(core: Mapping[str, object]) -> dict[str, object]:
    metadata = core.get("metadata", {})
    if not isinstance(metadata, Mapping):
        raise ValueError("core lacks metadata")
    target_counts = metadata.get("target_reader_exact_counts", {})
    if not isinstance(target_counts, Mapping) or set(target_counts) != set(TARGETS):
        raise ValueError("core target panel differs from GDT769 five-whole panel")
    if _as_int(metadata.get("f84_accessed")) or _as_int(metadata.get("f84r_accessed")):
        raise ValueError("sealed f84/f84r access is forbidden")
    donor_blocks = core.get("donor_blocks", {})
    if not isinstance(donor_blocks, Mapping):
        raise ValueError("core lacks donor block registry")
    family_union = set(str(item) for item in donor_blocks.get("family_ed2_union", ()))
    if not family_union:
        raise ValueError("core lacks UNION-ED2 family block")
    leakage: list[str] = []
    for occurrence in core.get("occurrences", ()):
        if not isinstance(occurrence, Mapping):
            continue
        for scope, view in occurrence.get("context_views", {}).items():
            if not isinstance(view, Mapping):
                continue
            for donor in view.get("eligible_donors", ()):
                if isinstance(donor, Mapping) and str(donor.get("surface")) in family_union:
                    leakage.append(
                        f"{occurrence.get('target_occurrence_id')}:{scope}:{donor.get('surface')}"
                    )
    if leakage:
        raise ValueError(f"UNION-ED2 donor leakage: {leakage[:3]}")
    controls = core.get("controls", {})
    value_spans = controls.get("value_spans", ()) if isinstance(controls, Mapping) else ()
    return {
        "target_forms": list(TARGETS),
        "reader_exact_target_counts": {
            target: _as_int(target_counts[target]) for target in TARGETS
        },
        "reader_exact_target_occurrences": sum(
            _as_int(target_counts[target]) for target in TARGETS
        ),
        "family_ed2_union_surface_count": len(family_union),
        "gdt754_source_composed_surface_count": _as_int(
            metadata.get("gdt754_source_composed_surface_count")
        ),
        "gdt737_explicit_quarantined_surface_count": _as_int(
            metadata.get("gdt737_explicit_quarantined_surface_count")
        ),
        "separate_value_span_count": len(value_spans),
        "separate_value_spans_are_ols_only": int(
            bool(value_spans)
            and all(
                isinstance(row, Mapping)
                and str(row.get("preparation_surface")) == "ols"
                for row in value_spans
            )
        ),
        "union_ed2_verified": 1,
        "f84_accessed": False,
        "f84r_accessed": False,
    }


def build_model_dispatch(
    core: Mapping[str, object],
    role_specs: Sequence[Mapping[str, object]],
    identity_specs: Sequence[Mapping[str, object]],
    frame_specs: Sequence[Mapping[str, object]],
    historical_predictions: Sequence[Mapping[str, object]] = (),
) -> dict[str, object]:
    """Evaluate all supplied GDT769 frames, roles, and identity cards.

    The identity deck is deliberately dynamic: successive expanded decks use
    the same API.  Every returned value
    is accepted by :func:`json.dumps` without a custom encoder.
    """

    boundary = _verify_core_boundary(core)
    frame_specs_list = [dict(row) for row in frame_specs]
    role_specs_list = [dict(row) for row in role_specs]
    identity_specs_list = [dict(row) for row in identity_specs]
    history_list = [dict(row) for row in historical_predictions]
    frame_rows, frame_evidence, evidence_map = _build_frame_tables(
        core, frame_specs_list
    )
    role_rows, role_winners = _build_role_scoreboard(
        core, role_specs_list, frame_rows, evidence_map
    )
    identity_rows, identity_winners = _build_identity_scoreboard(
        core,
        identity_specs_list,
        frame_rows,
        evidence_map,
        role_winners,
        history_list,
    )
    historical_metadata = _historical_prediction_metadata(
        history_list, identity_rows
    )
    dictionary = _build_dictionary_decisions(
        role_rows, identity_rows, role_winners, identity_winners
    )

    # F14 is explicitly recorded as background geometry, not a discriminator.
    f14_rates = {
        str(row["target_surface"]): float(row["normalised_support_rate"])
        for row in frame_rows
        if str(row["frame_id"]) == "F14_MEDIAL_TWO_SIDED_LINKER"
    }
    f15_rates = {
        str(row["target_surface"]): float(row["normalised_support_rate"])
        for row in frame_rows
        if str(row["frame_id"]) == "F15_STATE_TRANSITION_BRIDGE"
    }
    result: dict[str, object] = {
        "frame_evidence": frame_rows,
        "frame_locus_evidence": frame_evidence,
        "role_scoreboard": role_rows,
        "identity_scoreboard": identity_rows,
        "dictionary_decisions": dictionary,
        "metadata": {
            **boundary,
            "frame_spec_count": len(frame_specs_list),
            "frame_evaluation_count": len(frame_rows),
            "role_spec_count": len(role_specs_list),
            "role_evaluation_count": len(role_rows),
            "identity_spec_count": len(identity_specs_list),
            "identity_evaluation_count": len(identity_rows),
            "dictionary_decision_count": len(dictionary),
            "historical_prediction_count": len(history_list),
            "historical_prediction_metadata": historical_metadata,
            "f14_normalised_support_rates": f14_rates,
            "f15_normalised_support_rates": f15_rates,
            "f16_normalised_support_rates": {
                str(row["target_surface"]): float(row["normalised_support_rate"])
                for row in frame_rows
                if str(row["frame_id"]) == "F16_RELATIONAL_AMOUNT_ORDER"
            },
            "f14_alone_has_sequence_role_selection_credit": 0,
            "r05_requires_f14_and_f15_or_f16": 1,
            "concrete_identity_requires_two_independent_axes": 1,
            "historical_predictions_create_voynich_evidence": 0,
            "eva_latin_identity_credit": 0,
            "substring_identity_export_credit": 0,
            "confirmed_lexemes": 0,
            "confirmed_plaintext_clauses": 0,
        },
    }

    # Keep the contract honest even when callers pass custom specification
    # rows: the standard panel is 16x5 frames and 5x5 roles; identity count is
    # intentionally whatever the current deck declares.
    if len(frame_specs_list) != 16 or len(frame_rows) != 80:
        raise ValueError("GDT769 requires 16 frames evaluated for five targets")
    if len(role_specs_list) != 5 or len(role_rows) != 25:
        raise ValueError("GDT769 requires five roles evaluated for five targets")
    if len(dictionary) != 5 or len(identity_rows) != len(identity_specs_list):
        raise ValueError("incomplete GDT769 model dispatch")
    return result


__all__ = (
    "FRAME_AXIS_FAMILY",
    "FRAME_IDS",
    "ROLE_PREFIXES",
    "TARGETS",
    "build_model_dispatch",
)
