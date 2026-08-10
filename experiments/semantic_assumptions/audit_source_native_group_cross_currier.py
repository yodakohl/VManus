#!/usr/bin/env python3
"""Describe cross-Currier stability of exact source-native group positions."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
ATLAS = RESULTS / "source_native_group_position_atlas.json"
ATLAS_VALIDATION = RESULTS / "source_native_group_position_atlas_validation.json"
SPEC = BASE / "SOURCE_NATIVE_GROUP_CROSS_CURRIER_DIAGNOSTIC_SPEC.md"
AUDITOR = Path(__file__).resolve()
OUT_TSV = RESULTS / "source_native_group_cross_currier.tsv"
OUT_JSON = RESULTS / "source_native_group_cross_currier.json"
OUT_REPORT = RESULTS / "source_native_group_cross_currier_report.md"

FROZEN = {
    GROUPS: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    ATLAS: "2ab129f24ebd2450e0eca06474897bfaad1cb51d8f4f670e01a324e76468fd85",
    ATLAS_VALIDATION: "9c421937b7278005c4f358e8f81884ed620aaf833c5cf7e02dd02797c0efa7d1",
}
FIELDS = [
    "family_surface", "a_first", "a_last", "a_endpoints", "a_folios",
    "a_log_odds_ratio", "a_direction", "b_first", "b_last", "b_endpoints",
    "b_folios", "b_log_odds_ratio", "b_direction", "direction_relation",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def folio(page: str) -> str:
    match = re.fullmatch(r"(f\d+)[rv]\d*", page)
    if match is None:
        raise ValueError(page)
    return match.group(1)


def direction(value: float) -> str:
    return "FIRST" if value > 0 else "LAST" if value < 0 else "ZERO"


def correlation(left: list[float], right: list[float]) -> float:
    if len(left) != len(right) or len(left) < 2:
        raise ValueError("correlation capacity")
    mean_left = sum(left) / len(left)
    mean_right = sum(right) / len(right)
    numerator = sum((a - mean_left) * (b - mean_right) for a, b in zip(left, right))
    denominator = math.sqrt(
        sum((a - mean_left) ** 2 for a in left)
        * sum((b - mean_right) ** 2 for b in right)
    )
    if denominator == 0:
        raise ValueError("zero correlation variance")
    return numerator / denominator


def midranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda index: (values[index], index))
    result = [0.0] * len(values)
    start = 0
    while start < len(order):
        stop = start + 1
        while stop < len(order) and values[order[stop]] == values[order[start]]:
            stop += 1
        rank = (start + stop - 1) / 2.0 + 1.0
        for index in order[start:stop]:
            result[index] = rank
        start = stop
    return result


def main() -> None:
    if any(path.exists() for path in (OUT_TSV, OUT_JSON, OUT_REPORT)):
        raise SystemExit("refusing to overwrite cross-Currier diagnostic")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen input mismatch: {path.name}")
    atlas = json.loads(ATLAS.read_text(encoding="utf-8"))
    validation = json.loads(ATLAS_VALIDATION.read_text(encoding="utf-8"))
    if atlas["status"] != "PASS_DESCRIPTIVE_EXACT_GROUP_POSITION_DECOMPOSITION":
        raise SystemExit("group-position atlas is not PASS")
    if validation["status"] != "PASS_INDEPENDENT_EXACT_GROUP_POSITION_ATLAS_RECONSTRUCTION":
        raise SystemExit("group-position validation is not PASS")

    rows = list(csv.DictReader(GROUPS.open(encoding="utf-8", newline=""), delimiter="\t"))
    counts: Counter[tuple[str, str, str]] = Counter()
    folios: dict[tuple[str, str], set[str]] = defaultdict(set)
    totals: Counter[tuple[str, str]] = Counter()
    for row in rows:
        if row["strict_zero_alternative"] != "1" or row["grammar_scope"] != "CONFIRMED_PROSE":
            continue
        register = row["currier"]
        if register not in {"A", "B"}:
            continue
        index = int(row["consensus_group_index"])
        count = int(row["consensus_group_count"])
        if count < 2 or index not in {1, count}:
            continue
        role = "FIRST" if index == 1 else "LAST"
        surface = row["family_surface"]
        counts[(surface, register, role)] += 1
        folios[(surface, register)].add(folio(row["page"]))
        totals[(register, role)] += 1

    all_surfaces = sorted({surface for surface, _, _ in counts})
    eligible = [
        surface for surface in all_surfaces
        if all(
            counts[(surface, register, "FIRST")] + counts[(surface, register, "LAST")] >= 10
            and len(folios[(surface, register)]) >= 5
            for register in ("A", "B")
        )
    ]
    if len(eligible) != 25:
        raise ValueError("common-support count drift")

    output = []
    for surface in eligible:
        item: dict[str, object] = {"family_surface": surface}
        directions = {}
        for register, prefix in (("A", "a"), ("B", "b")):
            first = counts[(surface, register, "FIRST")]
            last = counts[(surface, register, "LAST")]
            other_first = totals[(register, "FIRST")] - first
            other_last = totals[(register, "LAST")] - last
            coefficient = math.log((first + 0.5) / (last + 0.5)) - math.log(
                (other_first + 0.5) / (other_last + 0.5)
            )
            state = direction(coefficient)
            directions[register] = state
            item.update({
                f"{prefix}_first": first, f"{prefix}_last": last,
                f"{prefix}_endpoints": first + last,
                f"{prefix}_folios": len(folios[(surface, register)]),
                f"{prefix}_log_odds_ratio": coefficient,
                f"{prefix}_direction": state,
            })
        if "ZERO" in directions.values():
            relation = "ZERO_IN_ONE_REGISTER"
        elif directions["A"] == directions["B"]:
            relation = "SAME_DIRECTION"
        else:
            relation = "OPPOSITE_DIRECTION"
        item["direction_relation"] = relation
        output.append(item)

    with OUT_TSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)

    a_values = [float(row["a_log_odds_ratio"]) for row in output]
    b_values = [float(row["b_log_odds_ratio"]) for row in output]
    pearson = correlation(a_values, b_values)
    spearman = correlation(midranks(a_values), midranks(b_values))
    leave_one = {}
    for index, row in enumerate(output):
        leave_one[row["family_surface"]] = correlation(
            a_values[:index] + a_values[index + 1:],
            b_values[:index] + b_values[index + 1:],
        )
    relation_counts = Counter(row["direction_relation"] for row in output)
    direction_table = Counter((row["a_direction"], row["b_direction"]) for row in output)
    reversals = [
        row for row in output if row["direction_relation"] == "OPPOSITE_DIRECTION"
    ]
    result = {
        "experiment": "SOURCE_NATIVE_GROUP_CROSS_CURRIER_DIAGNOSTIC",
        "status": "PASS_DESCRIPTIVE_PARTIAL_EXACT_FORM_ROLE_SHARING",
        "inputs": {path.name: sha(path) for path in (*FROZEN, SPEC, AUDITOR)},
        "capacity": {
            "eligible_forms": len(output),
            "minimum_endpoints_per_register": 10,
            "minimum_folios_per_register": 5,
            "a_endpoint_events": sum(int(row["a_endpoints"]) for row in output),
            "b_endpoint_events": sum(int(row["b_endpoints"]) for row in output),
            "a_physical_folios": len(set().union(*(folios[(surface, "A")] for surface in eligible))),
            "b_physical_folios": len(set().union(*(folios[(surface, "B")] for surface in eligible))),
        },
        "summary": {
            "pearson_log_odds": pearson,
            "spearman_log_odds": spearman,
            "direction_relations": dict(sorted(relation_counts.items())),
            "direction_cross_table": {
                f"{left}__{right}": count
                for (left, right), count in sorted(direction_table.items())
            },
            "minimum_leave_one_form_pearson": min(leave_one.values()),
            "maximum_leave_one_form_pearson": max(leave_one.values()),
            "leave_one_form_pearson": dict(sorted(leave_one.items())),
        },
        "opposite_direction_forms": reversals,
        "tsv_sha256": sha(OUT_TSV),
        "confirmatory_p_value": None,
        "english_glosses": 0,
        "claim_ceiling": (
            "Post-atlas descriptive evidence that supported exact STA-family group-form position "
            "tendencies are partly shared and partly register-specific across Currier A/B. The "
            "registers are correlated manuscript strata, not independent languages; no dialect, "
            "language, part of speech, sound, morpheme, word meaning, plaintext, cipher, or "
            "translation follows."
        ),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = f"""# Source-native exact-group cross-Currier diagnostic

Status: **PASS_DESCRIPTIVE_PARTIAL_EXACT_FORM_ROLE_SHARING**

The score-blind common-support rule retains **{len(output)}** exact family
surfaces, **{result['capacity']['a_endpoint_events']}** Currier-A and
**{result['capacity']['b_endpoint_events']}** Currier-B endpoint events on
**{result['capacity']['a_physical_folios']}** and
**{result['capacity']['b_physical_folios']}** physical folios.

Whole-form first-versus-last log odds correlate **{pearson:.6f}** by Pearson
and **{spearman:.6f}** by midrank Spearman. **{relation_counts['SAME_DIRECTION']}**
forms have the same sign, **{relation_counts['OPPOSITE_DIRECTION']}** reverse,
and **{relation_counts['ZERO_IN_ONE_REGISTER']}** is exactly neutral in one
register. Deleting any one form leaves Pearson correlation between
**{min(leave_one.values()):.6f}** and **{max(leave_one.values()):.6f}**.

This is partial sharing, not identity: the compositional grammar spans both
registers, while some whole forms change positional preference. The audit is
descriptive and has no confirmatory p-value. It does not decide whether Currier
A/B are styles, registers, dialects, or anything else, and supplies no part of
speech, sound, morpheme, word meaning, plaintext, language, cipher, or
translation.
"""
    OUT_REPORT.write_text(report, encoding="utf-8")
    print(json.dumps({
        "status": result["status"], "forms": len(output),
        "pearson": pearson, "relations": result["summary"]["direction_relations"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
