#!/usr/bin/env python3
"""Transparent model scoring for GDT768.

The module is deliberately read-only.  It consumes the in-memory structures
returned by :mod:`core_atlas` plus already loaded TSV specification rows and
returns JSON-serialisable Python objects.  It does not open a transcription,
an image, or an artifact path and it never writes a file.

The five scores rank working explanations of the *complete* words ``chor``
and ``shor``.  They do not identify a lexeme, a sound, an EVA component, or a
flower/seed plaintext.  In particular, historical rows supply architecture
fit only and symmetric flower/seed evidence cannot choose M02 over M03.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any


TARGETS = ("chor", "shor")
RADII = (0, 1, 2)
SCOPES = ("D1", "R3", "LINE")
NON_ANCHOR_FEATURES = (
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
)
EXPECTED_MODELS = ("M01", "M02", "M03", "M04", "M05")
ROOT_CONTROLS = ("dair", "kooiin", "koaiin")
DRY_STATE_WHOLES = ("chol", "qokchol", "cheor")
MOIST_STATE_WHOLES = ("shol", "sheol", "sheor")
NAMED_STATE_WHOLES = DRY_STATE_WHOLES + MOIST_STATE_WHOLES


def _clip(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return min(high, max(low, float(value)))


def _rounded(value: float) -> float:
    return round(float(value), 6)


def _pipe(value: object) -> tuple[str, ...]:
    return tuple(
        item
        for item in str(value or "").split("|")
        if item and item not in {"NONE", "OPEN"}
    )


def _weight_map(value: object) -> dict[str, float]:
    result: dict[str, float] = {}
    for item in _pipe(value):
        if ":" not in item:
            raise ValueError(f"invalid feature-weight item: {item!r}")
        feature_id, raw_weight = item.split(":", 1)
        weight = float(raw_weight)
        if weight < 0:
            raise ValueError(f"negative feature weight: {item!r}")
        result[feature_id] = weight
    return result


def _safe_rate(numerator: float, denominator: float) -> float:
    return 0.0 if denominator <= 0 else float(numerator) / float(denominator)


def _polarity(dry: float, moist: float) -> float:
    total = float(dry) + float(moist)
    return 0.0 if total <= 0 else (float(dry) - float(moist)) / total


def _expected_signed_match(observed: float, expected: float) -> float:
    """Match two values in [-1, 1] on a [0, 1] scale."""

    return _clip(1.0 - abs(float(observed) - float(expected)) / 2.0)


def _cosine(first: Sequence[float], second: Sequence[float]) -> float:
    dot = sum(a * b for a, b in zip(first, second, strict=True))
    first_norm = math.sqrt(sum(value * value for value in first))
    second_norm = math.sqrt(sum(value * value for value in second))
    if first_norm == 0.0 or second_norm == 0.0:
        return 0.0
    return _clip(dot / (first_norm * second_norm))


def _weighted_jaccard(first: Sequence[float], second: Sequence[float]) -> float:
    numerator = sum(min(a, b) for a, b in zip(first, second, strict=True))
    denominator = sum(max(a, b) for a, b in zip(first, second, strict=True))
    return 0.0 if denominator == 0 else _clip(numerator / denominator)


def _distribution(counts: Mapping[str, object], keys: Sequence[str]) -> list[float]:
    values = [float(counts.get(key, 0)) for key in keys]
    total = sum(values)
    if total == 0:
        return [0.0 for _ in values]
    return [value / total for value in values]


def _binary_distribution(successes: int, total: int) -> list[float]:
    success_rate = _safe_rate(successes, total)
    return [success_rate, 1.0 - success_rate]


def _js_similarity(first: Sequence[float], second: Sequence[float]) -> float:
    """One minus base-two Jensen-Shannon divergence, in [0, 1]."""

    if len(first) != len(second):
        raise ValueError("distribution lengths differ")
    first_total = sum(first)
    second_total = sum(second)
    if first_total == 0.0 and second_total == 0.0:
        return 1.0
    if first_total == 0.0 or second_total == 0.0:
        return 0.0
    p = [value / first_total for value in first]
    q = [value / second_total for value in second]
    middle = [(a + b) / 2.0 for a, b in zip(p, q, strict=True)]

    def divergence(values: Sequence[float]) -> float:
        return sum(
            value * math.log2(value / midpoint)
            for value, midpoint in zip(values, middle, strict=True)
            if value > 0.0 and midpoint > 0.0
        )

    return _clip(1.0 - 0.5 * (divergence(p) + divergence(q)))


def _normalised_entropy(counts: Mapping[str, object], keys: Sequence[str]) -> float:
    distribution = _distribution(counts, keys)
    populated = len(distribution)
    if populated <= 1:
        return 0.0
    entropy = -sum(value * math.log2(value) for value in distribution if value > 0)
    return _clip(entropy / math.log2(populated))


def _require_rows(
    rows: Sequence[Mapping[str, object]], key: str, expected: Sequence[str], label: str
) -> dict[str, Mapping[str, object]]:
    lookup: dict[str, Mapping[str, object]] = {}
    for row in rows:
        row_key = str(row.get(key, ""))
        if not row_key:
            raise ValueError(f"{label} row lacks {key}")
        if row_key in lookup:
            raise ValueError(f"duplicate {label} {key}: {row_key}")
        lookup[row_key] = row
    missing = set(expected) - set(lookup)
    if missing:
        raise ValueError(f"missing {label} rows: {sorted(missing)}")
    return lookup


def _core_lookups(core: Mapping[str, object]) -> dict[str, object]:
    ablation_rows = list(core.get("family_ablation", ()))
    role_rows = list(core.get("role_geometry", ()))
    pair_rows = list(core.get("pair_summary", ()))
    if not ablation_rows or not role_rows or not pair_rows:
        raise ValueError("core lacks family_ablation, role_geometry, or pair_summary")

    ablation: dict[tuple[str, int, str], Mapping[str, object]] = {}
    for row in ablation_rows:
        key = (
            str(row["target_surface"]),
            int(row["family_radius"]),
            str(row["scope"]),
        )
        if key in ablation:
            raise ValueError(f"duplicate family-ablation row: {key}")
        ablation[key] = row

    for target in TARGETS:
        for radius in RADII:
            for scope in SCOPES:
                if (target, radius, scope) not in ablation:
                    raise ValueError(
                        f"core lacks family-ablation row: {(target, radius, scope)}"
                    )

    roles = {str(row["surface"]): row for row in role_rows}
    for target in TARGETS:
        if target not in roles:
            raise ValueError(f"core lacks role geometry for {target}")

    pairs: dict[frozenset[str], Mapping[str, object]] = {}
    for row in pair_rows:
        pair_key = frozenset((str(row["first_surface"]), str(row["second_surface"])))
        if len(pair_key) != 2:
            raise ValueError(f"invalid pair row: {row}")
        pairs[pair_key] = row

    return {"ablation": ablation, "roles": roles, "pairs": pairs}


def _feature_counts(
    lookups: Mapping[str, object], target: str, radius: int, scope: str
) -> Mapping[str, object]:
    ablation = lookups["ablation"]
    assert isinstance(ablation, dict)
    row = ablation[(target, radius, scope)]
    counts = row["feature_occurrence_counts"]
    if not isinstance(counts, Mapping):
        raise TypeError("feature_occurrence_counts must be a mapping")
    return counts


def _donor_surface_counts(
    lookups: Mapping[str, object], target: str, radius: int, scope: str
) -> Mapping[str, object]:
    ablation = lookups["ablation"]
    assert isinstance(ablation, dict)
    counts = ablation[(target, radius, scope)]["donor_surface_counts"]
    if not isinstance(counts, Mapping):
        raise TypeError("donor_surface_counts must be a mapping")
    return counts


def _pair_row(
    lookups: Mapping[str, object], first: str, second: str
) -> Mapping[str, object]:
    pairs = lookups["pairs"]
    assert isinstance(pairs, dict)
    key = frozenset((first, second))
    if key not in pairs:
        raise ValueError(f"core lacks pair summary for {first}/{second}")
    return pairs[key]


def _metric_row(
    metric_id: str,
    feature_id: str,
    metric_group: str,
    target_or_pair: str,
    scope: str,
    family_radius: int | str,
    numerator: float | int | str,
    denominator: float | int | str,
    value: float,
    display: str,
    interpretation: str,
    source: str,
) -> dict[str, object]:
    return {
        "metric_id": metric_id,
        "feature_id": feature_id,
        "metric_group": metric_group,
        "target_or_pair": target_or_pair,
        "scope": scope,
        "family_radius": family_radius,
        "numerator": numerator,
        "denominator": denominator,
        "value": _rounded(value),
        "display": display,
        "interpretation": interpretation,
        "source": source,
        "flower_vs_seed_identity_credit": 0,
        "component_credit": 0,
    }


def _observed_state_and_cofield_metrics(
    lookups: Mapping[str, object]
) -> tuple[list[dict[str, object]], dict[str, object]]:
    rows: list[dict[str, object]] = []
    state_polarities: dict[tuple[str, int, str], float] = {}
    cofield_cosines: dict[tuple[int, str], float] = {}
    cofield_jaccards: dict[tuple[int, str], float] = {}

    for target in TARGETS:
        feature_id = "CF01" if target == "chor" else "CF02"
        for radius in RADII:
            for scope in ("D1", "LINE"):
                counts = _feature_counts(lookups, target, radius, scope)
                dry = int(counts.get("DRY", 0))
                moist = int(counts.get("MOIST", 0))
                polarity = _polarity(dry, moist)
                state_polarities[target, radius, scope] = polarity
                rows.append(
                    _metric_row(
                        f"{feature_id}_{target.upper()}_{scope}_ED{radius}",
                        feature_id if scope == "D1" else "CF03",
                        "DRY_MOIST_POLARITY",
                        target,
                        scope,
                        radius,
                        dry - moist,
                        dry + moist,
                        polarity,
                        f"DRY {dry} / MOIST {moist}; polarity {polarity:.6f}",
                        "Positive is dry-affine; negative is moist-affine.",
                        "GDT768_CORE_FAMILY_ABLATION",
                    )
                )

    for radius in RADII:
        for scope in SCOPES:
            vectors: dict[str, list[float]] = {}
            for target in TARGETS:
                counts = _feature_counts(lookups, target, radius, scope)
                target_total = int(
                    lookups["ablation"][(target, radius, scope)]["target_occurrences"]
                )
                vectors[target] = [
                    _safe_rate(float(counts.get(feature, 0)), target_total)
                    for feature in NON_ANCHOR_FEATURES
                ]
            cosine = _cosine(vectors["chor"], vectors["shor"])
            jaccard = _weighted_jaccard(vectors["chor"], vectors["shor"])
            cofield_cosines[radius, scope] = cosine
            cofield_jaccards[radius, scope] = jaccard
            rows.append(
                _metric_row(
                    f"CF10_COSINE_{scope}_ED{radius}",
                    "CF10",
                    "OUTWARD_COFIELD_SIMILARITY",
                    "chor|shor",
                    scope,
                    radius,
                    "DOT_PRODUCT",
                    "L2_NORMS",
                    cosine,
                    f"12D non-anchor cosine {cosine:.6f}",
                    "High values mean similar target-excluding technical environments; no noun identity follows.",
                    "GDT768_CORE_FAMILY_ABLATION",
                )
            )
            rows.append(
                _metric_row(
                    f"CF10_JACCARD_{scope}_ED{radius}",
                    "CF10",
                    "OUTWARD_COFIELD_SIMILARITY",
                    "chor|shor",
                    scope,
                    radius,
                    "SUM_MIN_RATE",
                    "SUM_MAX_RATE",
                    jaccard,
                    f"12D non-anchor weighted Jaccard {jaccard:.6f}",
                    "A second transparent similarity view; ANCHOR dimensions are excluded.",
                    "GDT768_CORE_FAMILY_ABLATION",
                )
            )

    derived = {
        "state_polarities": state_polarities,
        "cofield_cosines": cofield_cosines,
        "cofield_jaccards": cofield_jaccards,
    }
    return rows, derived


def _observed_part_state_metrics(
    lookups: Mapping[str, object]
) -> tuple[list[dict[str, object]], dict[str, object]]:
    """Measure CF04 from exact D1 donor surfaces at every ablation radius.

    ``chol``/``qokchol``/``cheor`` and ``shol``/``sheol``/``sheor`` are an
    explicit comparison deck inherited from the admitted part/state route.
    They are complete written forms here, not decomposed lexemes.  The M01
    score is conjunctive: both sides must retain their expected state-whole
    family at ED2.  The symmetric M02/M03 score instead asks whether the two
    targets retain a similar *named-state-whole* rate profile at ED2.
    """

    rows: list[dict[str, object]] = []
    desired_counts: dict[tuple[str, int], int] = {}
    named_counts: dict[tuple[str, int], int] = {}
    named_vectors: dict[str, list[float]] = {}
    surface_coverage: dict[str, float] = {}

    for target in TARGETS:
        expected = DRY_STATE_WHOLES if target == "chor" else MOIST_STATE_WHOLES
        rival = MOIST_STATE_WHOLES if target == "chor" else DRY_STATE_WHOLES
        for radius in RADII:
            counts = _donor_surface_counts(lookups, target, radius, "D1")
            expected_detail = {name: int(counts.get(name, 0)) for name in expected}
            rival_detail = {name: int(counts.get(name, 0)) for name in rival}
            expected_total = sum(expected_detail.values())
            rival_total = sum(rival_detail.values())
            named_total = expected_total + rival_total
            desired_counts[target, radius] = expected_total
            named_counts[target, radius] = named_total
            local_alignment = _safe_rate(expected_total, named_total)
            expected_label = "dry" if target == "chor" else "moist"
            rival_label = "moist" if target == "chor" else "dry"
            rows.append(
                _metric_row(
                    f"CF04_{target.upper()}_D1_ED{radius}_NAMED_STATE_WHOLES",
                    "CF04",
                    "EXACT_PART_STATE_FAMILY_PERSISTENCE",
                    target,
                    "D1",
                    radius,
                    expected_total,
                    named_total,
                    local_alignment,
                    (
                        f"expected {expected_label}: "
                        + ", ".join(
                            f"{name}={expected_detail[name]}" for name in expected
                        )
                        + f" (total {expected_total}); rival {rival_label}: "
                        + ", ".join(
                            f"{name}={rival_detail[name]}" for name in rival
                        )
                        + f" (total {rival_total})"
                    ),
                    (
                        "Exact complete-form donor counts measure local state-family alignment; "
                        "they do not assign a plaintext value to any EVA substring."
                    ),
                    "GDT768_CORE_FAMILY_ABLATION_DONOR_SURFACES",
                )
            )

        ed0_counts = _donor_surface_counts(lookups, target, 0, "D1")
        surface_coverage[target] = _safe_rate(
            sum(int(ed0_counts.get(name, 0)) > 0 for name in NAMED_STATE_WHOLES),
            len(NAMED_STATE_WHOLES),
        )
        ed2_counts = _donor_surface_counts(lookups, target, 2, "D1")
        total_occurrences = int(lookups["ablation"][(target, 2, "D1")]["target_occurrences"])
        named_vectors[target] = [
            _safe_rate(int(ed2_counts.get(name, 0)), total_occurrences)
            for name in NAMED_STATE_WHOLES
        ]

    retention = {
        target: _safe_rate(desired_counts[target, 2], desired_counts[target, 0])
        for target in TARGETS
    }
    family_persistent_state_pair_score = min(retention.values())
    nominal_compatibility = _weighted_jaccard(
        named_vectors["chor"], named_vectors["shor"]
    )

    rows.extend(
        (
            _metric_row(
                "CF04_FAMILY_PERSISTENT_STATE_PAIR_SCORE",
                "CF04",
                "EXACT_PART_STATE_FAMILY_PERSISTENCE",
                "chor|shor",
                "D1",
                "ED0_TO_ED2",
                (
                    f"MIN(chor {desired_counts['chor', 2]}/{desired_counts['chor', 0]},"
                    f"shor {desired_counts['shor', 2]}/{desired_counts['shor', 0]})"
                ),
                "CONJUNCTIVE_TARGET_RETENTION",
                family_persistent_state_pair_score,
                (
                    f"chor expected-family retention {retention['chor']:.6f}; "
                    f"shor expected-family retention {retention['shor']:.6f}; "
                    f"conjunctive score {family_persistent_state_pair_score:.6f}"
                ),
                (
                    "M01 receives only the weaker target's ED2/ED0 retention: an expected "
                    "state pair is not persistent when either side disappears."
                ),
                "GDT768_CORE_FAMILY_ABLATION_DONOR_SURFACES",
            ),
            _metric_row(
                "CF04_FORM_CONDITIONED_NOMINAL_COMPATIBILITY_ED2",
                "CF04",
                "EXACT_PART_STATE_NOMINAL_COMPATIBILITY",
                "chor|shor",
                "D1",
                2,
                "SUM_MIN_TARGET_NORMALISED_NAMED_STATE_RATES",
                "SUM_MAX_TARGET_NORMALISED_NAMED_STATE_RATES",
                nominal_compatibility,
                (
                    f"ED2 named-state-whole weighted Jaccard {nominal_compatibility:.6f}; "
                    f"chor named donors {named_counts['chor', 2]}, shor named donors {named_counts['shor', 2]}"
                ),
                (
                    "Measured surviving form conditioning can support symmetric nominal "
                    "compatibility, but it gives zero flower-versus-seed direction credit."
                ),
                "GDT768_CORE_FAMILY_ABLATION_DONOR_SURFACES",
            ),
        )
    )

    return rows, {
        "part_state_desired_counts": desired_counts,
        "part_state_named_counts": named_counts,
        "part_state_target_retention": retention,
        "family_persistent_state_pair_score": family_persistent_state_pair_score,
        "form_conditioned_nominal_compatibility": nominal_compatibility,
        "chor_named_state_surface_coverage": surface_coverage["chor"],
        "shor_named_state_surface_coverage": surface_coverage["shor"],
    }


def _observed_pair_metrics(
    lookups: Mapping[str, object], role_rows: Mapping[str, Mapping[str, object]]
) -> tuple[list[dict[str, object]], dict[str, object]]:
    rows: list[dict[str, object]] = []
    pair_rates: dict[tuple[str, str], float] = {}
    target_totals = {
        target: int(role_rows[target]["reader_exact_occurrences"]) for target in TARGETS
    }

    pair_specs = (
        ("CF05", "chor", "cthy"),
        ("CF05", "shor", "cthy"),
        ("CF11", "chor", "shor"),
        *(('CF06', target, control) for target in TARGETS for control in ROOT_CONTROLS),
    )
    for feature_id, first, second in pair_specs:
        pair = _pair_row(lookups, first, second)
        target = first if first in TARGETS else second
        total = target_totals[target]
        line_count = int(pair["line_count"])
        direct_count = int(pair["direct_pair_count"])
        line_rate = _safe_rate(line_count, total)
        pair_rates[first, second] = line_rate
        rows.append(
            _metric_row(
                f"{feature_id}_{first.upper()}_{second.upper()}_LINE_RATE",
                feature_id,
                "EXACT_ANCHOR_PAIRING",
                f"{first}|{second}",
                "LINE",
                "NA",
                line_count,
                total,
                line_rate,
                (
                    f"{line_count} lines / {int(pair['page_count'])} pages / "
                    f"{direct_count} direct pairs; target-normalised line rate {line_rate:.6f}"
                ),
                "Parallel occurrence supports a shared register or part list, not a specific identity.",
                "GDT768_CORE_PAIR_SUMMARY",
            )
        )

    mutual = _pair_row(lookups, "chor", "shor")
    order_total = int(mutual["first_before_second"]) + int(mutual["second_before_first"])
    order_balance = 0.0
    if order_total:
        order_balance = 1.0 - abs(
            int(mutual["first_before_second"]) - int(mutual["second_before_first"])
        ) / order_total
    pair_replication = _clip(
        0.45 * min(1.0, int(mutual["line_count"]) / 5.0)
        + 0.35 * min(1.0, int(mutual["direct_pair_count"]) / 3.0)
        + 0.20 * order_balance
    )

    chor_cthy_rate = pair_rates["chor", "cthy"]
    shor_cthy_rate = pair_rates["shor", "cthy"]
    cthy_rate_similarity = _safe_rate(
        min(chor_cthy_rate, shor_cthy_rate),
        max(chor_cthy_rate, shor_cthy_rate),
    )

    root_vectors: dict[str, list[float]] = {}
    for target in TARGETS:
        root_vectors[target] = [
            pair_rates[target, control] for control in ROOT_CONTROLS
        ]
    root_profile_similarity = _cosine(root_vectors["chor"], root_vectors["shor"])
    chor_root_breadth = sum(value > 0 for value in root_vectors["chor"])
    shor_root_breadth = sum(value > 0 for value in root_vectors["shor"])

    derived = {
        "pair_rates": pair_rates,
        "pair_replication": pair_replication,
        "mutual_order_balance": order_balance,
        "cthy_rate_similarity": cthy_rate_similarity,
        "root_profile_similarity": root_profile_similarity,
        "chor_root_breadth": chor_root_breadth,
        "shor_root_breadth": shor_root_breadth,
    }
    return rows, derived


def _observed_role_metrics(
    lookups: Mapping[str, object]
) -> tuple[list[dict[str, object]], dict[str, object]]:
    roles_raw = lookups["roles"]
    assert isinstance(roles_raw, dict)
    roles: dict[str, Mapping[str, object]] = {
        target: roles_raw[target] for target in TARGETS
    }
    rows: list[dict[str, object]] = []

    line_keys = ("FIRST", "MIDDLE", "LAST", "SINGLE")
    position_components = [
        _js_similarity(
            _distribution(roles["chor"]["line_position_counts"], line_keys),
            _distribution(roles["shor"]["line_position_counts"], line_keys),
        )
    ]
    for field in ("paragraph_start_line", "paragraph_end_line"):
        position_components.append(
            _js_similarity(
                _binary_distribution(
                    int(roles["chor"][field]),
                    int(roles["chor"]["reader_exact_occurrences"]),
                ),
                _binary_distribution(
                    int(roles["shor"][field]),
                    int(roles["shor"]["reader_exact_occurrences"]),
                ),
            )
        )
    position_similarity = sum(position_components) / len(position_components)
    position_divergence = 1.0 - position_similarity

    section_keys = tuple(
        sorted(
            set(roles["chor"]["section_counts"])
            | set(roles["shor"]["section_counts"])
        )
    )
    section_similarity = _js_similarity(
        _distribution(roles["chor"]["section_counts"], section_keys),
        _distribution(roles["shor"]["section_counts"], section_keys),
    )
    section_divergence = 1.0 - section_similarity
    chor_section_entropy = _normalised_entropy(
        roles["chor"]["section_counts"], section_keys
    )
    shor_section_entropy = _normalised_entropy(
        roles["shor"]["section_counts"], section_keys
    )

    for target in TARGETS:
        total = int(roles[target]["reader_exact_occurrences"])
        first = int(roles[target]["line_first"])
        paragraph_start = int(roles[target]["paragraph_start_line"])
        rows.append(
            _metric_row(
                f"CF08_{target.upper()}_LINE_FIRST_RATE",
                "CF08",
                "RECORD_POSITION",
                target,
                "LINE",
                "NA",
                first,
                total,
                _safe_rate(first, total),
                f"line-first {first}/{total}; paragraph-start-line {paragraph_start}/{total}",
                "Position is a record-role measurement, not a noun gloss.",
                "GDT768_CORE_ROLE_GEOMETRY",
            )
        )

    rows.extend(
        (
            _metric_row(
                "CF08_POSITION_JS_SIMILARITY",
                "CF08",
                "RECORD_POSITION",
                "chor|shor",
                "LINE_AND_PARAGRAPH",
                "NA",
                "ONE_MINUS_JS",
                "THREE_POSITION_COMPONENTS",
                position_similarity,
                f"position similarity {position_similarity:.6f}",
                "High similarity supports parallel nominal roles; only repeated divergence supports M05.",
                "GDT768_CORE_ROLE_GEOMETRY",
            ),
            _metric_row(
                "CF09_SECTION_JS_SIMILARITY",
                "CF09",
                "SECTION_PROFILE",
                "chor|shor",
                "GLOBAL",
                "NA",
                "ONE_MINUS_JS",
                "H_P_S_T_B_C_PROFILE",
                section_similarity,
                f"section similarity {section_similarity:.6f}",
                "Shared concentration supports a common technical register but no plant-part identity.",
                "GDT768_CORE_ROLE_GEOMETRY",
            ),
        )
    )

    derived = {
        "roles": roles,
        "position_similarity": position_similarity,
        "position_divergence": position_divergence,
        "section_similarity": section_similarity,
        "section_divergence": section_divergence,
        "chor_section_entropy": chor_section_entropy,
        "shor_section_entropy": shor_section_entropy,
    }
    return rows, derived


def _observed_amount_metrics(
    lookups: Mapping[str, object]
) -> tuple[list[dict[str, object]], dict[str, object]]:
    rows: list[dict[str, object]] = []
    rates: dict[tuple[str, str], float] = {}
    radius = 2
    for scope in SCOPES:
        for target in TARGETS:
            row = lookups["ablation"][(target, radius, scope)]
            counts = row["feature_occurrence_counts"]
            total = int(row["target_occurrences"])
            count = int(counts.get("VALUE_AMOUNT", 0))
            rate = _safe_rate(count, total)
            rates[target, scope] = rate
            rows.append(
                _metric_row(
                    f"CF07_{target.upper()}_{scope}_ED2",
                    "CF07",
                    "BROAD_VALUE_AMOUNT_PROXY",
                    target,
                    scope,
                    radius,
                    count,
                    total,
                    rate,
                    f"broad VALUE_AMOUNT proxy {count}/{total}; rate {rate:.6f}",
                    "This is not a bound quantity formula; it is a broad register proxy and cannot identify flower versus seed.",
                    "GDT768_CORE_FAMILY_ABLATION",
                )
            )
    direction_deltas = {
        scope: rates["chor", scope] - rates["shor", scope] for scope in SCOPES
    }
    mean_absolute_delta = sum(abs(value) for value in direction_deltas.values()) / len(
        direction_deltas
    )
    return rows, {
        "amount_rates": rates,
        "amount_direction_deltas_chor_minus_shor": direction_deltas,
        "amount_mean_absolute_delta": mean_absolute_delta,
    }


def _declared_prior_metrics(
    model_specs: Mapping[str, Mapping[str, object]],
    comparison_specs: Mapping[str, Mapping[str, object]],
    historical_specs: Mapping[str, Mapping[str, object]],
) -> tuple[list[dict[str, object]], dict[str, object]]:
    rows: list[dict[str, object]] = []
    visual_declared = "CF12" in comparison_specs and "shor" in _pipe(
        comparison_specs["CF12"].get("targets")
    )
    rows.append(
        _metric_row(
            "CF12_DECLARED_CACHED_VISUAL_REPRODUCTIVE_PRIOR",
            "CF12",
            "DECLARED_VISUAL_PRIOR",
            "shor",
            "CACHED_ADJUDICATION_ONLY",
            "NA",
            int(visual_declared),
            1,
            float(visual_declared),
            "shor has a declared broad reproductive-part visual prior" if visual_declared else "no declared visual prior",
            "The prior supports only a broad reproductive class and is symmetric for flower versus seed or fruit.",
            "GDT768_COMPARISON_FEATURE_SPECS",
        )
    )

    historical_coverage: dict[str, float] = {}
    for model_id, model in model_specs.items():
        requested = _pipe(model.get("historical_signature_ids"))
        present = [signature for signature in requested if signature in historical_specs]
        coverage = _safe_rate(len(present), len(requested)) if requested else 0.0
        historical_coverage[model_id] = coverage
        rows.append(
            _metric_row(
                f"CF13_{model_id}_DECLARED_HISTORY_COVERAGE",
                "CF13",
                "HISTORICAL_ARCHITECTURE_PRIOR",
                model_id,
                "DECLARED_SIGNATURES",
                "NA",
                len(present),
                len(requested),
                coverage,
                f"{len(present)}/{len(requested)} declared historical signatures present",
                "Coverage verifies an attested comparison architecture; it supplies zero target-word identity credit.",
                "GDT768_HISTORICAL_PART_SIGNATURES",
            )
        )
    return rows, {
        "visual_reproductive_prior_declared": visual_declared,
        "historical_signature_coverage": historical_coverage,
    }


def _derive_summary_metrics(derived: Mapping[str, object]) -> dict[str, float]:
    state = derived["state_polarities"]
    assert isinstance(state, dict)
    chor_dry_match = sum(
        _expected_signed_match(float(state["chor", radius, "D1"]), 1.0)
        for radius in RADII
    ) / len(RADII)
    shor_moist_match = sum(
        _expected_signed_match(float(state["shor", radius, "D1"]), -1.0)
        for radius in RADII
    ) / len(RADII)
    opposite_fraction = sum(
        float(state["chor", radius, "D1"])
        * float(state["shor", radius, "D1"])
        < 0
        for radius in RADII
    ) / len(RADII)

    cofield = derived["cofield_cosines"]
    assert isinstance(cofield, dict)
    radius_two_cofield_mean = sum(
        float(cofield[2, scope]) for scope in SCOPES
    ) / len(SCOPES)

    position_similarity = float(derived["position_similarity"])
    section_similarity = float(derived["section_similarity"])
    cthy_similarity = float(derived["cthy_rate_similarity"])
    pair_replication = float(derived["pair_replication"])
    root_profile_similarity = float(derived["root_profile_similarity"])
    amount_delta = float(derived["amount_mean_absolute_delta"])
    family_persistent_state_pair_score = float(
        derived["family_persistent_state_pair_score"]
    )
    nominal_state_compatibility = float(
        derived["form_conditioned_nominal_compatibility"]
    )

    chor_breadth = int(derived["chor_root_breadth"])
    shor_breadth = int(derived["shor_root_breadth"])
    breadth_advantage = _clip(0.5 + 0.25 * (chor_breadth - shor_breadth))
    register_entropy_advantage = _clip(
        0.5
        + 0.5
        * (
            float(derived["chor_section_entropy"])
            - float(derived["shor_section_entropy"])
        )
    )

    return {
        "chor_dry_persistence_match": chor_dry_match,
        "shor_moist_persistence_match": shor_moist_match,
        "opposite_state_sign_fraction": opposite_fraction,
        "shared_part_state_alignment": (
            chor_dry_match + shor_moist_match + opposite_fraction
        )
        / 3.0,
        "family_persistent_state_pair_score": family_persistent_state_pair_score,
        "form_conditioned_nominal_compatibility": nominal_state_compatibility,
        "chor_named_state_surface_coverage": float(
            derived["chor_named_state_surface_coverage"]
        ),
        "shor_named_state_surface_coverage": float(
            derived["shor_named_state_surface_coverage"]
        ),
        "cthy_parallel_similarity": cthy_similarity,
        "root_profile_similarity": root_profile_similarity,
        "chor_breadth_advantage": breadth_advantage,
        "amount_profile_divergence": _clip(amount_delta * 4.0),
        "position_similarity": position_similarity,
        "position_divergence": 1.0 - position_similarity,
        "section_similarity": section_similarity,
        "section_divergence": 1.0 - section_similarity,
        "chor_register_breadth_advantage": register_entropy_advantage,
        "radius_two_cofield_similarity": radius_two_cofield_mean,
        "radius_two_cofield_divergence": 1.0 - radius_two_cofield_mean,
        "mutual_pair_replication": pair_replication,
    }


def _feature_match(
    model_id: str,
    feature_id: str,
    summary: Mapping[str, float],
    priors: Mapping[str, object],
) -> tuple[float, str, str, int]:
    """Return match, supporting text, counterevidence, historical-only flag."""

    chor_dry = summary["chor_dry_persistence_match"]
    shor_moist = summary["shor_moist_persistence_match"]
    opposite = summary["opposite_state_sign_fraction"]
    state_pair_persistence = summary["family_persistent_state_pair_score"]
    nominal_state_compatibility = summary["form_conditioned_nominal_compatibility"]
    cthy_similarity = summary["cthy_parallel_similarity"]
    root_similarity = summary["root_profile_similarity"]
    amount_divergence = summary["amount_profile_divergence"]
    position_similarity = summary["position_similarity"]
    position_divergence = summary["position_divergence"]
    section_similarity = summary["section_similarity"]
    section_divergence = summary["section_divergence"]
    cofield_similarity = summary["radius_two_cofield_similarity"]
    cofield_divergence = summary["radius_two_cofield_divergence"]
    pair_replication = summary["mutual_pair_replication"]

    if model_id == "M01":
        table = {
            "CF01": (
                chor_dry,
                "chor remains dry-affine through all three family-ablation radii.",
                "The dry excess shrinks as nearby forms are removed.",
                0,
            ),
            "CF02": (
                shor_moist,
                "shor is moist-affine only before near-family donors are removed.",
                "shor reverses to dry-affine at edit-family radii one and two.",
                0,
            ),
            "CF03": (
                opposite,
                "The targets have opposite direct state signs at radius zero.",
                "The opposition survives only one of three family-ablation radii.",
                0,
            ),
            "CF04": (
                state_pair_persistence,
                "The exact named state-whole deck is measured at all three D1 ablation radii.",
                "At ED2 qokchol remains beside chor twice and shor once, while the expected shor-side moist family is absent; conjunctive pair persistence is zero.",
                0,
            ),
            "CF05": (
                cthy_similarity,
                "Both targets repeatedly parallel the independent cthy part control.",
                "cthy parallelism names neither a shared reproductive part nor its state.",
                0,
            ),
            "CF08": (
                position_similarity,
                "The complete wholes have broadly compatible nominal line geometry.",
                "shor is appreciably more line-initial and paragraph-start-line biased.",
                0,
            ),
            "CF09": (
                section_similarity,
                "Both targets concentrate in the plant-heavy register.",
                "Their section profiles are not identical.",
                0,
            ),
            "CF10": (
                cofield_similarity,
                "Their non-anchor 12D cofields remain nearly identical at radius two.",
                "Cofield similarity supports a shared technical register, not dry/moist identity.",
                0,
            ),
            "CF11": (
                pair_replication,
                "chor and shor share eight exact lines and three direct pairs.",
                "Mutual pairing is equally compatible with two parallel part fields.",
                0,
            ),
            "CF12": (
                0.75 if priors["visual_reproductive_prior_declared"] else 0.0,
                "Cached visual adjudications support shor as broadly reproductive.",
                "They do not show that chor and shor name one part or choose flower versus fruit.",
                0,
            ),
            "CF13": (
                0.75,
                "Period comparators attest plant-part heads with bound state and degree fields.",
                "No comparator identifies chor/shor as a dry/moist pair.",
                1,
            ),
        }
    elif model_id in {"M02", "M03"}:
        direction = "chor=flower, shor=seed/fruit" if model_id == "M02" else "chor=seed/fruit, shor=flower"
        table = {
            "CF04": (
                nominal_state_compatibility,
                "At ED2 both complete wholes retain a measured, target-normalised named-state-whole profile.",
                "Only qokchol survives in this deck, and the symmetric compatibility cannot select either flower/seed direction.",
                0,
            ),
            "CF05": (
                (1.0 + cthy_similarity) / 2.0,
                "Both targets repeatedly stand apart from the cthy leaf control.",
                "Leaf contrast identifies only a non-leaf or broader part class.",
                0,
            ),
            "CF07": (
                0.5,
                "The broad amount profile is measured and reported for both targets.",
                f"Amount ecology cannot choose {direction}; flower-versus-seed identity credit is fixed to zero.",
                0,
            ),
            "CF08": (
                position_similarity,
                "Both behave as nominal record fields rather than true paragraph openers.",
                "Their initial-position rates differ, but not in a historically directional flower/seed way.",
                0,
            ),
            "CF09": (
                section_similarity,
                "Both share a strong Herbal/plant-register concentration.",
                "Register similarity cannot order flower against seed or fruit.",
                0,
            ),
            "CF10": (
                cofield_similarity,
                "Near-identical radius-two cofields fit parallel plant-part rubrics.",
                "The symmetry leaves the two directional assignments tied.",
                0,
            ),
            "CF11": (
                pair_replication,
                "Repeated same-line and direct pairing fits neighboring part entries.",
                "The same observation also fits a state contrast.",
                0,
            ),
            "CF12": (
                0.75 if priors["visual_reproductive_prior_declared"] else 0.0,
                "Cached images support only shor's broad reproductive class.",
                "Visible reproductive organs do not distinguish flower from fruit or seed.",
                0,
            ),
            "CF13": (
                0.80,
                "Circa-1400 rubrics place flowers, seeds and fruits in parallel named part classes.",
                "The historical layout is exactly symmetric with respect to M02 and M03.",
                1,
            ),
        }
    elif model_id == "M04":
        general_hierarchy = _clip(0.5 * cthy_similarity + 0.5 * summary["chor_breadth_advantage"])
        moderate_similarity_match = _clip(1.0 - abs(cofield_similarity - 0.65) / 0.35)
        table = {
            "CF04": (
                summary["chor_named_state_surface_coverage"],
                "Four of the six declared named state wholes occur around chor at ED0.",
                "shor also contacts four of six, so this measured breadth does not establish a chor-over-shor hierarchy.",
                0,
            ),
            "CF05": (
                general_hierarchy,
                "chor repeatedly co-occurs with cthy and could in principle scope a leaf subfield.",
                "shor also parallels cthy at a similar exposure-adjusted rate.",
                0,
            ),
            "CF06": (
                _clip(0.5 * root_similarity + 0.5 * summary["chor_breadth_advantage"]),
                "Both targets encounter more than one root/fraction control.",
                "chor has no unique breadth advantage; dair is not a secure root word.",
                0,
            ),
            "CF08": (
                _clip(0.5 * position_similarity + 0.5 * (1.0 - position_divergence)),
                "chor is predominantly medial, compatible with a content head.",
                "shor, not chor, is the more line-initial form, contrary to a simple general-heading prediction.",
                0,
            ),
            "CF09": (
                summary["chor_register_breadth_advantage"],
                "chor occurs across several technical sections.",
                "After normalization shor is at least as register-diverse, so raw chor frequency cannot count as breadth.",
                0,
            ),
            "CF10": (
                moderate_similarity_match,
                "The targets inhabit the same broad technical ecology.",
                "Their radius-two cofields are too similar for a strong general-head versus specific-subpart split.",
                0,
            ),
            "CF11": (
                0.65 * pair_replication,
                "Direct pairing could represent a whole-herb head beside one subpart.",
                "No direction or scope marker establishes that hierarchy.",
                0,
            ),
            "CF12": (
                0.75 if priors["visual_reproductive_prior_declared"] else 0.0,
                "Cached visual evidence supports shor as broadly reproductive.",
                "It supplies no independent whole-herb identification for chor.",
                0,
            ),
            "CF13": (
                0.70,
                "Period records attest herba or learned simples beside specific part and state fields.",
                "The architecture does not identify chor as the general member.",
                1,
            ),
        }
    elif model_id == "M05":
        table = {
            "CF05": (
                1.0 - cthy_similarity,
                "The two complete wholes need not have identical leaf-control relations.",
                "Their cthy rates are similar, so distinct opaque roles gain little support.",
                0,
            ),
            "CF06": (
                1.0 - root_similarity,
                "Different learned wholes could select different internal controls.",
                "Their sparse root/fraction profiles do not show a robust split.",
                0,
            ),
            "CF07": (
                amount_divergence,
                "A measured amount-profile difference is allowed to support role divergence.",
                "The observed normalized difference is small; mere uncertainty scores zero.",
                0,
            ),
            "CF08": (
                position_divergence,
                "shor is more initial than chor.",
                "Overall line and paragraph geometry remains substantially similar and both have zero true opener events.",
                0,
            ),
            "CF09": (
                section_divergence,
                "Some minor-section proportions differ.",
                "Both are dominated by the same plant-heavy register.",
                0,
            ),
            "CF10": (
                cofield_divergence,
                "A genuinely low outward similarity would support two unrelated learned roles.",
                "Observed radius-two similarity is near one, directly opposing M05.",
                0,
            ),
            "CF11": (
                0.0,
                "A learned field sequence is historically possible.",
                "Nothing in the mutual pair census identifies a role sequence, so possibility earns no score.",
                0,
            ),
            "CF13": (
                0.50,
                "Learned materia wholes plus bound specialist fields are historically attested.",
                "Architecture alone cannot rescue M05 against the observed high cofield similarity.",
                1,
            ),
        }
    else:
        raise ValueError(f"unsupported fixed model: {model_id}")

    if feature_id not in table:
        return 0.0, "No applicable evidence component.", "Not scored for this model.", 0
    match, evidence, counterevidence, historical_only = table[feature_id]
    return _clip(float(match)), evidence, counterevidence, int(historical_only)


def _minimum_support(
    model_id: str, summary: Mapping[str, float], score: float
) -> tuple[bool, str]:
    if model_id == "M01":
        passed = (
            summary["opposite_state_sign_fraction"] >= 2.0 / 3.0
            and summary["shor_moist_persistence_match"] >= 0.6
            and (
                summary["radius_two_cofield_similarity"] >= 0.8
                or summary["mutual_pair_replication"] >= 0.7
            )
        )
        return passed, (
            "Requires opposite polarity through at least two ablation radii and a persistent shor-moist match."
        )
    if model_id in {"M02", "M03"}:
        return False, (
            "Directional minimum failed; shared two-part relation supported."
        )
    if model_id == "M04":
        passed = (
            summary["chor_breadth_advantage"] > 0.5
            and summary["chor_register_breadth_advantage"] > 0.55
        )
        return passed, "Requires exposure-controlled chor breadth on both part and register axes."
    if model_id == "M05":
        passed = (
            summary["position_divergence"] >= 0.35
            and summary["radius_two_cofield_divergence"] >= 0.35
        )
        return passed, "Requires two observed divergence channels; unknown identity itself contributes nothing."
    raise ValueError(model_id)


def _rank_with_ties(rows: list[dict[str, object]]) -> None:
    rows.sort(key=lambda row: (-float(row["score_0_1"]), str(row["model_id"])))
    previous: float | None = None
    previous_rank = 0
    for ordinal, row in enumerate(rows, 1):
        score = float(row["score_0_1"])
        if previous is None or not math.isclose(score, previous, abs_tol=1e-9):
            previous_rank = ordinal
            previous = score
        row["rank"] = previous_rank


def build_model_evidence(
    core: Mapping[str, object],
    model_specs: list[dict],
    comparison_specs: list[dict],
    historical_specs: list[dict],
) -> dict:
    """Build transparent GDT768 evidence rows and the five-model scoreboard.

    All returned scores are bounded to ``[0, 1]``.  A high score ranks an
    exploratory model; it never supplies lexical confirmation.  M02 and M03
    deliberately receive identical directional evidence because no admitted
    metric distinguishes flower from seed/fruit.  M05 receives points only
    for observed divergence, never for an unknown or missing identity.
    """

    models = _require_rows(model_specs, "model_id", EXPECTED_MODELS, "model")
    comparisons = _require_rows(
        comparison_specs,
        "feature_id",
        tuple(f"CF{number:02d}" for number in range(1, 14)),
        "comparison feature",
    )
    histories = _require_rows(
        historical_specs,
        "signature_id",
        tuple(f"HP{number:02d}" for number in range(1, 10)),
        "historical signature",
    )

    for model_id, model in models.items():
        unknown_features = set(_weight_map(model.get("feature_weights"))) - set(
            comparisons
        )
        if unknown_features:
            raise ValueError(
                f"{model_id} references unknown features: {sorted(unknown_features)}"
            )
        unknown_history = set(_pipe(model.get("historical_signature_ids"))) - set(
            histories
        )
        if unknown_history:
            raise ValueError(
                f"{model_id} references unknown historical signatures: {sorted(unknown_history)}"
            )

    lookups = _core_lookups(core)
    role_lookup = lookups["roles"]
    assert isinstance(role_lookup, dict)

    observed_rows: list[dict[str, object]] = []
    state_rows, state_derived = _observed_state_and_cofield_metrics(lookups)
    part_state_rows, part_state_derived = _observed_part_state_metrics(lookups)
    pair_rows, pair_derived = _observed_pair_metrics(lookups, role_lookup)
    role_rows, role_derived = _observed_role_metrics(lookups)
    amount_rows, amount_derived = _observed_amount_metrics(lookups)
    prior_rows, prior_derived = _declared_prior_metrics(
        models, comparisons, histories
    )
    observed_rows.extend(state_rows)
    observed_rows.extend(part_state_rows)
    observed_rows.extend(pair_rows)
    observed_rows.extend(role_rows)
    observed_rows.extend(amount_rows)
    observed_rows.extend(prior_rows)
    observed_rows.sort(key=lambda row: str(row["metric_id"]))

    all_derived: dict[str, object] = {}
    for source in (
        state_derived,
        part_state_derived,
        pair_derived,
        role_derived,
        amount_derived,
        prior_derived,
    ):
        all_derived.update(source)
    summary = _derive_summary_metrics(all_derived)

    feature_evidence: list[dict[str, object]] = []
    scoreboard: list[dict[str, object]] = []
    for model_id in EXPECTED_MODELS:
        model = models[model_id]
        weights = _weight_map(model.get("feature_weights"))
        weighted_sum = 0.0
        applicable_weight = 0.0
        evidence_fragments: list[str] = []
        counter_fragments: list[str] = []

        for feature_id in sorted(comparisons):
            comparison = comparisons[feature_id]
            weight = float(weights.get(feature_id, 0.0))
            applicable = int(feature_id in weights and weight > 0.0)
            match, evidence, counterevidence, historical_only = _feature_match(
                model_id, feature_id, summary, prior_derived
            )
            if applicable:
                weighted_sum += weight * match
                applicable_weight += weight
                evidence_fragments.append(f"{feature_id}: {evidence}")
                counter_fragments.append(f"{feature_id}: {counterevidence}")
            feature_evidence.append(
                {
                    "model_id": model_id,
                    "model_label": str(model["model_label"]),
                    "feature_id": feature_id,
                    "feature_label": (
                        "BROAD_VALUE_AMOUNT_PROXY"
                        if feature_id == "CF07"
                        else str(comparison["feature_label"])
                    ),
                    "applicable": applicable,
                    "weight": _rounded(weight),
                    "match_score_0_1": _rounded(match if applicable else 0.0),
                    "weighted_evidence": _rounded(weight * match if applicable else 0.0),
                    "evidence": evidence,
                    "counterevidence": counterevidence,
                    "historical_or_visual_prior_only": historical_only,
                    "flower_vs_seed_identity_credit": 0,
                    "confirmed_lexeme": 0,
                    "component_export_credit": 0,
                }
            )

        if applicable_weight <= 0:
            raise ValueError(f"model has no applicable weight: {model_id}")
        score = _clip(weighted_sum / applicable_weight)
        support_met, support_rule = _minimum_support(model_id, summary, score)
        scoreboard.append(
            {
                "rank": 0,
                "model_id": model_id,
                "model_label": str(model["model_label"]),
                "score_0_1": _rounded(score),
                "weighted_sum": _rounded(weighted_sum),
                "applicable_weight": _rounded(applicable_weight),
                "minimum_interpretive_support_met": int(support_met),
                "minimum_interpretive_support_rule": support_rule,
                "chor_portable_de": str(model["chor_portable_de"]),
                "shor_portable_de": str(model["shor_portable_de"]),
                "chor_bold_de": str(model["chor_bold_de"]),
                "shor_bold_de": str(model["shor_bold_de"]),
                "evidence": " | ".join(evidence_fragments),
                "counterevidence": " | ".join(counter_fragments),
                "replacement_rule_de": str(model["replacement_rule_de"]),
                "flower_vs_seed_identity_credit": 0,
                "confirmed_lexeme": 0,
                "component_export_credit": 0,
            }
        )

    _rank_with_ties(scoreboard)
    score_lookup = {str(row["model_id"]): float(row["score_0_1"]) for row in scoreboard}
    direction_gap = abs(score_lookup["M02"] - score_lookup["M03"])
    directional_tie = direction_gap < 0.10
    m01_support = next(
        int(row["minimum_interpretive_support_met"])
        for row in scoreboard
        if row["model_id"] == "M01"
    )
    m05_support = next(
        int(row["minimum_interpretive_support_met"])
        for row in scoreboard
        if row["model_id"] == "M05"
    )

    if directional_tie:
        preferred_reading = (
            "chor und shor bleiben parallele reproduktive oder andere Pflanzenteil-Ganzwörter; "
            "Blüte gegen Samen oder Frucht ist ungerichtet"
        )
        decision = "PARALLEL_PART_REGISTER__FLOWER_VS_SEED_DIRECTION_TIED"
    else:
        leader = "M02" if score_lookup["M02"] > score_lookup["M03"] else "M03"
        preferred_reading = str(models[leader]["model_label"])
        decision = f"DIRECTIONAL_LEAD_{leader}__IDENTITY_CREDIT_ZERO"

    dictionary_replacement_allowed = 0
    for row in scoreboard:
        model_id = str(row["model_id"])
        if model_id in {"M02", "M03"} and directional_tie:
            row["decision"] = "TIED_DIRECTIONAL_MODEL__NO_IDENTITY_REPLACEMENT"
        elif model_id == "M01" and not m01_support:
            row["decision"] = "LIVE_RIVAL__DRY_MOIST_PERSISTENCE_RULE_FAILED"
        elif model_id == "M04" and not int(row["minimum_interpretive_support_met"]):
            row["decision"] = "LIVE_RIVAL__CHOR_BREADTH_RULE_FAILED"
        elif model_id == "M05" and not m05_support:
            row["decision"] = "DISFAVORED__OBSERVED_DIVERGENCE_RULE_FAILED"
        else:
            row["decision"] = "RANKED_EXPLORATORY_MODEL"
        row["dictionary_replacement_allowed"] = dictionary_replacement_allowed

    metadata = core.get("metadata", {})
    if not isinstance(metadata, Mapping):
        raise TypeError("core metadata must be a mapping")
    return {
        "observed_metrics": observed_rows,
        "derived_summary": {key: _rounded(value) for key, value in summary.items()},
        "feature_by_model_evidence": feature_evidence,
        "scoreboard": scoreboard,
        "decision": {
            "decision": decision,
            "preferred_working_reading_de": preferred_reading,
            "m02_m03_score_gap": _rounded(direction_gap),
            "flower_vs_seed_direction_tied": int(directional_tie),
            "dry_moist_same_part_minimum_support_met": m01_support,
            "role_distinct_learned_wholes_minimum_support_met": m05_support,
            "dictionary_replacement_allowed": dictionary_replacement_allowed,
            "flower_vs_seed_identity_credit": 0,
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        },
        "metadata": {
            "model_count": len(scoreboard),
            "observed_metric_count": len(observed_rows),
            "feature_evidence_row_count": len(feature_evidence),
            "score_range": "ZERO_TO_ONE",
            "target_occurrences": int(metadata.get("target_occurrences", 0)),
            "target_pages": int(metadata.get("target_pages", 0)),
            "family_ablation_radii": list(metadata.get("family_ablation_radii", RADII)),
            "f84_accessed": bool(metadata.get("f84_accessed", False)),
            "f84r_accessed": bool(metadata.get("f84r_accessed", False)),
            "historical_relation_credit": 0,
            "flower_vs_seed_identity_credit": 0,
            "component_export_credit": 0,
            "writes_artifacts": False,
        },
    }


__all__ = ("build_model_evidence",)
