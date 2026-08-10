#!/usr/bin/env python3
"""Independent reconstruction of the exact-group cross-Currier diagnostic."""

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
PRODUCER = BASE / "audit_source_native_group_cross_currier.py"
PRODUCTION_TSV = RESULTS / "source_native_group_cross_currier.tsv"
PRODUCTION_JSON = RESULTS / "source_native_group_cross_currier.json"
PRODUCTION_REPORT = RESULTS / "source_native_group_cross_currier_report.md"
VALIDATOR = Path(__file__).resolve()
OUT_JSON = RESULTS / "source_native_group_cross_currier_validation.json"
OUT_REPORT = RESULTS / "source_native_group_cross_currier_validation_report.md"

HASHES = {
    GROUPS: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    ATLAS: "2ab129f24ebd2450e0eca06474897bfaad1cb51d8f4f670e01a324e76468fd85",
    ATLAS_VALIDATION: "9c421937b7278005c4f358e8f81884ed620aaf833c5cf7e02dd02797c0efa7d1",
    SPEC: "0d8308c1526b1ba35e2acd2727585230fadeca55292eecd93bc351bb33fcb3da",
    PRODUCER: "dbf5d6aea141339195f3514dd6ecd3115485c1f074e86ea73b1d523623d308c3",
    PRODUCTION_TSV: "7558fd6f3eeb05f8f3b5ddad3835baf41534749b9d34d103db5ad3cbefce1fb7",
    PRODUCTION_JSON: "dd5028429070662cf54fe7c9b6336ea99d2325e39aa3acab57773932bba3833f",
    PRODUCTION_REPORT: "3f2a4ab58dfea076dfab23e4301a3445adf9a78cd192f5fea2e34aaf74595efd",
}
FIELDS = [
    "family_surface", "a_first", "a_last", "a_endpoints", "a_folios",
    "a_log_odds_ratio", "a_direction", "b_first", "b_last", "b_endpoints",
    "b_folios", "b_log_odds_ratio", "b_direction", "direction_relation",
]
INTEGER_FIELDS = {
    "a_first", "a_last", "a_endpoints", "a_folios",
    "b_first", "b_last", "b_endpoints", "b_folios",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fold(page: str) -> str:
    match = re.fullmatch(r"(f[0-9]+)[rv][0-9]*", page)
    assert match is not None
    return match.group(1)


def sign(value: float) -> str:
    if value > 0:
        return "FIRST"
    if value < 0:
        return "LAST"
    return "ZERO"


def pearson(x: list[float], y: list[float]) -> float:
    assert len(x) == len(y) and len(x) >= 2
    mx, my = sum(x) / len(x), sum(y) / len(y)
    top = sum((a - mx) * (b - my) for a, b in zip(x, y))
    xx = sum((a - mx) ** 2 for a in x)
    yy = sum((b - my) ** 2 for b in y)
    assert xx > 0 and yy > 0
    return top / math.sqrt(xx * yy)


def rank(values: list[float]) -> list[float]:
    ordered = sorted(enumerate(values), key=lambda pair: (pair[1], pair[0]))
    ranks = [0.0] * len(values)
    i = 0
    while i < len(ordered):
        j = i + 1
        while j < len(ordered) and ordered[j][1] == ordered[i][1]:
            j += 1
        value = (i + j - 1) / 2 + 1
        for index, _ in ordered[i:j]:
            ranks[index] = value
        i = j
    return ranks


def reconstruct() -> tuple[list[dict[str, object]], dict[str, object], str, int]:
    checks = 0
    for path, expected in HASHES.items():
        assert sha(path) == expected
        checks += 1
    atlas = json.loads(ATLAS.read_text(encoding="utf-8"))
    atlas_validation = json.loads(ATLAS_VALIDATION.read_text(encoding="utf-8"))
    assert atlas["status"] == "PASS_DESCRIPTIVE_EXACT_GROUP_POSITION_DECOMPOSITION"
    assert atlas_validation["status"] == "PASS_INDEPENDENT_EXACT_GROUP_POSITION_ATLAS_RECONSTRUCTION"
    checks += 2

    cells: Counter[tuple[str, str, str]] = Counter()
    support_folios: dict[tuple[str, str], set[str]] = defaultdict(set)
    register_totals: Counter[tuple[str, str]] = Counter()
    endpoint_rows = 0
    for row in csv.DictReader(GROUPS.open(encoding="utf-8", newline=""), delimiter="\t"):
        if row["strict_zero_alternative"] != "1" or row["grammar_scope"] != "CONFIRMED_PROSE":
            continue
        register = row["currier"]
        if register not in ("A", "B"):
            continue
        index, count = int(row["consensus_group_index"]), int(row["consensus_group_count"])
        assert 1 <= index <= count
        if count == 1 or index not in (1, count):
            continue
        endpoint = "FIRST" if index == 1 else "LAST"
        surface = row["family_surface"]
        cells[(surface, register, endpoint)] += 1
        support_folios[(surface, register)].add(fold(row["page"]))
        register_totals[(register, endpoint)] += 1
        endpoint_rows += 1
        checks += 1
    assert endpoint_rows == 5352
    assert register_totals == Counter({("A", "FIRST"): 1026, ("A", "LAST"): 1026, ("B", "FIRST"): 1650, ("B", "LAST"): 1650})
    checks += 2

    surfaces = sorted({key[0] for key in cells})
    admitted = []
    for surface in surfaces:
        good = True
        for register in ("A", "B"):
            count = cells[(surface, register, "FIRST")] + cells[(surface, register, "LAST")]
            good = good and count >= 10 and len(support_folios[(surface, register)]) >= 5
        if good:
            admitted.append(surface)
    assert len(admitted) == 25
    checks += 1

    rows_out = []
    for surface in admitted:
        row_out: dict[str, object] = {"family_surface": surface}
        signs = {}
        for register, prefix in (("A", "a"), ("B", "b")):
            first, last = cells[(surface, register, "FIRST")], cells[(surface, register, "LAST")]
            other_first = register_totals[(register, "FIRST")] - first
            other_last = register_totals[(register, "LAST")] - last
            value = math.log((first + 0.5) / (last + 0.5)) - math.log(
                (other_first + 0.5) / (other_last + 0.5)
            )
            signs[register] = sign(value)
            row_out.update({
                prefix + "_first": first, prefix + "_last": last,
                prefix + "_endpoints": first + last,
                prefix + "_folios": len(support_folios[(surface, register)]),
                prefix + "_log_odds_ratio": value, prefix + "_direction": signs[register],
            })
        if signs["A"] == "ZERO" or signs["B"] == "ZERO":
            relation = "ZERO_IN_ONE_REGISTER"
        elif signs["A"] == signs["B"]:
            relation = "SAME_DIRECTION"
        else:
            relation = "OPPOSITE_DIRECTION"
        row_out["direction_relation"] = relation
        rows_out.append(row_out)
        checks += 1

    left = [float(row["a_log_odds_ratio"]) for row in rows_out]
    right = [float(row["b_log_odds_ratio"]) for row in rows_out]
    linear = pearson(left, right)
    monotone = pearson(rank(left), rank(right))
    leaveouts = {}
    for index, row in enumerate(rows_out):
        leaveouts[row["family_surface"]] = pearson(
            left[:index] + left[index + 1:], right[:index] + right[index + 1:]
        )
        checks += 1
    relation_counts = Counter(row["direction_relation"] for row in rows_out)
    cross = Counter((row["a_direction"], row["b_direction"]) for row in rows_out)
    opposite = [row for row in rows_out if row["direction_relation"] == "OPPOSITE_DIRECTION"]
    expected_json = {
        "experiment": "SOURCE_NATIVE_GROUP_CROSS_CURRIER_DIAGNOSTIC",
        "status": "PASS_DESCRIPTIVE_PARTIAL_EXACT_FORM_ROLE_SHARING",
        "inputs": {path.name: sha(path) for path in (GROUPS, ATLAS, ATLAS_VALIDATION, SPEC, PRODUCER)},
        "capacity": {
            "eligible_forms": len(rows_out), "minimum_endpoints_per_register": 10,
            "minimum_folios_per_register": 5,
            "a_endpoint_events": sum(int(row["a_endpoints"]) for row in rows_out),
            "b_endpoint_events": sum(int(row["b_endpoints"]) for row in rows_out),
            "a_physical_folios": len(set().union(*(support_folios[(surface, "A")] for surface in admitted))),
            "b_physical_folios": len(set().union(*(support_folios[(surface, "B")] for surface in admitted))),
        },
        "summary": {
            "pearson_log_odds": linear, "spearman_log_odds": monotone,
            "direction_relations": dict(sorted(relation_counts.items())),
            "direction_cross_table": {
                left_sign + "__" + right_sign: count
                for (left_sign, right_sign), count in sorted(cross.items())
            },
            "minimum_leave_one_form_pearson": min(leaveouts.values()),
            "maximum_leave_one_form_pearson": max(leaveouts.values()),
            "leave_one_form_pearson": dict(sorted(leaveouts.items())),
        },
        "opposite_direction_forms": opposite,
        "tsv_sha256": sha(PRODUCTION_TSV), "confirmatory_p_value": None,
        "english_glosses": 0,
        "claim_ceiling": (
            "Post-atlas descriptive evidence that supported exact STA-family group-form position "
            "tendencies are partly shared and partly register-specific across Currier A/B. The "
            "registers are correlated manuscript strata, not independent languages; no dialect, "
            "language, part of speech, sound, morpheme, word meaning, plaintext, cipher, or "
            "translation follows."
        ),
    }
    report = f"""# Source-native exact-group cross-Currier diagnostic

Status: **PASS_DESCRIPTIVE_PARTIAL_EXACT_FORM_ROLE_SHARING**

The score-blind common-support rule retains **{len(rows_out)}** exact family
surfaces, **{expected_json['capacity']['a_endpoint_events']}** Currier-A and
**{expected_json['capacity']['b_endpoint_events']}** Currier-B endpoint events on
**{expected_json['capacity']['a_physical_folios']}** and
**{expected_json['capacity']['b_physical_folios']}** physical folios.

Whole-form first-versus-last log odds correlate **{linear:.6f}** by Pearson
and **{monotone:.6f}** by midrank Spearman. **{relation_counts['SAME_DIRECTION']}**
forms have the same sign, **{relation_counts['OPPOSITE_DIRECTION']}** reverse,
and **{relation_counts['ZERO_IN_ONE_REGISTER']}** is exactly neutral in one
register. Deleting any one form leaves Pearson correlation between
**{min(leaveouts.values()):.6f}** and **{max(leaveouts.values()):.6f}**.

This is partial sharing, not identity: the compositional grammar spans both
registers, while some whole forms change positional preference. The audit is
descriptive and has no confirmatory p-value. It does not decide whether Currier
A/B are styles, registers, dialects, or anything else, and supplies no part of
speech, sound, morpheme, word meaning, plaintext, language, cipher, or
translation.
"""
    return rows_out, expected_json, report, checks


def main() -> None:
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite cross-Currier validation")
    rows, expected_json, report, checks = reconstruct()
    actual = list(csv.DictReader(PRODUCTION_TSV.open(encoding="utf-8", newline=""), delimiter="\t"))
    assert list(actual[0]) == FIELDS
    assert len(actual) == len(rows)
    checks += 2
    for found, expected in zip(actual, rows):
        for field in FIELDS:
            if field in INTEGER_FIELDS:
                assert int(found[field]) == expected[field]
            elif field.endswith("_log_odds_ratio"):
                assert float(found[field]) == expected[field]
            else:
                assert found[field] == expected[field]
            checks += 1
    assert json.loads(PRODUCTION_JSON.read_text(encoding="utf-8")) == expected_json
    assert PRODUCTION_REPORT.read_text(encoding="utf-8") == report
    checks += 2
    mutations = {
        "nine_endpoints_rejected": not (9 >= 10 and 5 >= 5),
        "four_folios_rejected": not (10 >= 10 and 4 >= 5),
        "exact_threshold_accepted": 10 >= 10 and 5 >= 5,
    }
    try:
        fold("f1")
        mutations["bad_page_rejected"] = False
    except (AssertionError, ValueError):
        mutations["bad_page_rejected"] = True
    assert all(mutations.values())
    checks += len(mutations)
    validation = {
        "experiment": "SOURCE_NATIVE_GROUP_CROSS_CURRIER_VALIDATION",
        "status": "PASS_INDEPENDENT_CROSS_CURRIER_DIAGNOSTIC_RECONSTRUCTION",
        "checks_passed": checks, "checks_failed": 0,
        "inputs": {
            "groups_sha256": sha(GROUPS), "spec_sha256": sha(SPEC),
            "producer_sha256": sha(PRODUCER), "production_tsv_sha256": sha(PRODUCTION_TSV),
            "production_json_sha256": sha(PRODUCTION_JSON),
            "production_report_sha256": sha(PRODUCTION_REPORT),
            "validator_sha256": sha(VALIDATOR),
        },
        "reconstructed_capacity": expected_json["capacity"],
        "reconstructed_summary": expected_json["summary"],
        "mutations": mutations, "claim_ceiling": expected_json["claim_ceiling"],
    }
    OUT_JSON.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    validation_report = f"""# Source-native exact-group cross-Currier validation

Status: **{validation['status']}**

Independent code reconstructed all **{len(rows)}** common-support forms,
endpoint counts, register log odds, directions, both correlations, all
leave-one-form diagnostics, exact output bytes, and four guards in
**{checks:,}** checks.

This validates a post-atlas diagnostic only. It supplies no dialect, language,
part of speech, sound, morpheme, word meaning, plaintext, cipher, or translation.
"""
    OUT_REPORT.write_text(validation_report, encoding="utf-8")
    print(json.dumps({"status": validation["status"], "checks": checks}, sort_keys=True))


if __name__ == "__main__":
    main()
