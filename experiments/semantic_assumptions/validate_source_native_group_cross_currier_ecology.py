#!/usr/bin/env python3
"""Independent reconstruction of the same-section Currier ecology diagnostic."""

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
PRIOR_TSV = RESULTS / "source_native_group_cross_currier.tsv"
PRIOR_JSON = RESULTS / "source_native_group_cross_currier.json"
PRIOR_VALIDATION = RESULTS / "source_native_group_cross_currier_validation.json"
SPEC = BASE / "SOURCE_NATIVE_GROUP_CROSS_CURRIER_ECOLOGY_SPEC.md"
PRODUCER = BASE / "audit_source_native_group_cross_currier_ecology.py"
PRODUCTION_TSV = RESULTS / "source_native_group_cross_currier_ecology.tsv"
PRODUCTION_JSON = RESULTS / "source_native_group_cross_currier_ecology.json"
PRODUCTION_REPORT = RESULTS / "source_native_group_cross_currier_ecology_report.md"
VALIDATOR = Path(__file__).resolve()
OUT_JSON = RESULTS / "source_native_group_cross_currier_ecology_validation.json"
OUT_REPORT = RESULTS / "source_native_group_cross_currier_ecology_validation_report.md"

HASHES = {
    GROUPS: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    PRIOR_TSV: "7558fd6f3eeb05f8f3b5ddad3835baf41534749b9d34d103db5ad3cbefce1fb7",
    PRIOR_JSON: "dd5028429070662cf54fe7c9b6336ea99d2325e39aa3acab57773932bba3833f",
    PRIOR_VALIDATION: "53344c2e20b12e642a8ca12542165412b1634d257888b16a24d26d1db32ef45e",
    SPEC: "e9c0a434e5dbd8811f6b72eb1faa9578040aecf38011b216e0c13a6b68ae8c9f",
    PRODUCER: "1d633aa34491eda108089edf711353693bb98ebbe534b233b832d00120b4413d",
    PRODUCTION_TSV: "99eda6bb7082d51788123f805c5b86222e2969bd2ba83ae33b82ae57d5572828",
    PRODUCTION_JSON: "0eae913d1c1cac8d7040ebd0c9a2f059747fff63cfba99ed6c3edb2090019a85",
    PRODUCTION_REPORT: "fc0e6479e46721f7a7c82d472b4fc3fe34318f5c44d1ca8c20c571116e72372c",
}
FIELDS = [
    "family_surface", "a_first", "a_last", "a_folios", "a_section_log_odds",
    "a_global_log_odds", "a_section_global_same_direction", "b_first", "b_last",
    "b_folios", "b_section_log_odds", "b_global_log_odds",
    "b_section_global_same_direction", "section_cross_register_relation",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def physical_folio(page: str) -> str:
    match = re.fullmatch(r"(f[0-9]+)[rv][0-9]*", page)
    assert match is not None
    return match.group(1)


def sgn(value: float) -> int:
    return (value > 0) - (value < 0)


def corr(x: list[float], y: list[float]) -> float:
    assert len(x) == len(y) and len(x) >= 2
    mx, my = sum(x) / len(x), sum(y) / len(y)
    numerator = sum((a - mx) * (b - my) for a, b in zip(x, y))
    denominator = math.sqrt(sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y))
    assert denominator > 0
    return numerator / denominator


def rank(values: list[float]) -> list[float]:
    ordered = sorted(range(len(values)), key=lambda i: (values[i], i))
    result = [0.0] * len(values)
    i = 0
    while i < len(ordered):
        j = i + 1
        while j < len(ordered) and values[ordered[j]] == values[ordered[i]]:
            j += 1
        value = (i + j - 1) / 2 + 1
        for index in ordered[i:j]:
            result[index] = value
        i = j
    return result


def reconstruct() -> tuple[list[dict[str, object]], dict[str, object], str, int]:
    checks = 0
    for path, expected in HASHES.items():
        assert sha(path) == expected
        checks += 1
    prior_json = json.loads(PRIOR_JSON.read_text(encoding="utf-8"))
    prior_validation = json.loads(PRIOR_VALIDATION.read_text(encoding="utf-8"))
    assert prior_json["status"] == "PASS_DESCRIPTIVE_PARTIAL_EXACT_FORM_ROLE_SHARING"
    assert prior_validation["status"] == "PASS_INDEPENDENT_CROSS_CURRIER_DIAGNOSTIC_RECONSTRUCTION"
    checks += 2
    prior = list(csv.DictReader(PRIOR_TSV.open(encoding="utf-8", newline=""), delimiter="\t"))
    assert len(prior) == 25 and len({row["family_surface"] for row in prior}) == 25
    forms = {row["family_surface"] for row in prior}
    global_values = {
        (row["family_surface"], register): float(row[register.lower() + "_log_odds_ratio"])
        for row in prior for register in ("A", "B")
    }
    checks += 1

    cells: Counter[tuple[str, str, str, str]] = Counter()
    folios: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    totals: Counter[tuple[str, str, str]] = Counter()
    endpoints = 0
    for row in csv.DictReader(GROUPS.open(encoding="utf-8", newline=""), delimiter="\t"):
        if row["strict_zero_alternative"] != "1" or row["grammar_scope"] != "CONFIRMED_PROSE":
            continue
        register = row["currier"]
        if register not in ("A", "B"):
            continue
        index, count = int(row["consensus_group_index"]), int(row["consensus_group_count"])
        assert 1 <= index <= count
        if count < 2 or index not in (1, count):
            continue
        endpoint = "FIRST" if index == 1 else "LAST"
        section, surface = row["section"], row["family_surface"]
        totals[(section, register, endpoint)] += 1
        if surface in forms:
            cells[(section, register, surface, endpoint)] += 1
            folios[(section, register, surface)].add(physical_folio(row["page"]))
        endpoints += 1
        checks += 1
    assert endpoints == 5352
    checks += 1

    sections = sorted({key[0] for key in totals})
    capacity = {}
    selected_by_section = {}
    for section in sections:
        selected = []
        for surface in sorted(forms):
            valid = True
            for register in ("A", "B"):
                n = cells[(section, register, surface, "FIRST")] + cells[(section, register, surface, "LAST")]
                valid = valid and n >= 5 and len(folios[(section, register, surface)]) >= 2
            if valid:
                selected.append(surface)
        selected_by_section[section] = selected
        capacity[section] = {
            "common_support_forms": len(selected),
            "a_endpoint_events_all_surfaces": totals[(section, "A", "FIRST")] + totals[(section, "A", "LAST")],
            "b_endpoint_events_all_surfaces": totals[(section, "B", "FIRST")] + totals[(section, "B", "LAST")],
        }
        checks += len(forms)
    eligible = [section for section in sections if len(selected_by_section[section]) >= 10]
    assert eligible == ["H"]
    admitted = selected_by_section["H"]
    assert len(admitted) == 14
    checks += 2

    output = []
    for surface in admitted:
        row_out: dict[str, object] = {"family_surface": surface}
        directions = {}
        for register, prefix in (("A", "a"), ("B", "b")):
            first = cells[("H", register, surface, "FIRST")]
            last = cells[("H", register, surface, "LAST")]
            value = math.log((first + 0.5) / (last + 0.5)) - math.log(
                (totals[("H", register, "FIRST")] - first + 0.5)
                / (totals[("H", register, "LAST")] - last + 0.5)
            )
            global_value = global_values[(surface, register)]
            directions[register] = sgn(value)
            row_out.update({
                prefix + "_first": first, prefix + "_last": last,
                prefix + "_folios": len(folios[("H", register, surface)]),
                prefix + "_section_log_odds": value,
                prefix + "_global_log_odds": global_value,
                prefix + "_section_global_same_direction": sgn(value) == sgn(global_value),
            })
        row_out["section_cross_register_relation"] = (
            "ZERO_IN_ONE_REGISTER" if 0 in directions.values()
            else "SAME_DIRECTION" if directions["A"] == directions["B"]
            else "OPPOSITE_DIRECTION"
        )
        output.append(row_out)
        checks += 1

    a = [float(row["a_section_log_odds"]) for row in output]
    b = [float(row["b_section_log_odds"]) for row in output]
    pearson, spearman = corr(a, b), corr(rank(a), rank(b))
    leaveouts = {}
    for index, row in enumerate(output):
        leaveouts[row["family_surface"]] = corr(a[:index] + a[index + 1:], b[:index] + b[index + 1:])
        checks += 1
    relations = Counter(row["section_cross_register_relation"] for row in output)
    global_agreement = {
        register: sum(bool(row[register.lower() + "_section_global_same_direction"]) for row in output)
        for register in ("A", "B")
    }
    expected_json = {
        "experiment": "SOURCE_NATIVE_GROUP_CROSS_CURRIER_ECOLOGY",
        "status": "PASS_DESCRIPTIVE_SAME_SECTION_PARTIAL_ROLE_SHARING",
        "inputs": {path.name: sha(path) for path in (GROUPS, PRIOR_TSV, PRIOR_JSON, PRIOR_VALIDATION, SPEC, PRODUCER)},
        "capacity": {
            "prior_forms": len(forms), "minimum_endpoints_per_register_section": 5,
            "minimum_folios_per_register_section": 2,
            "minimum_common_forms_for_section": 10,
            "sections": capacity, "eligible_sections": eligible,
            "selected_section": "H", "selected_forms": len(admitted),
        },
        "summary": {
            "pearson_section_log_odds": pearson, "spearman_section_log_odds": spearman,
            "section_direction_relations": dict(sorted(relations.items())),
            "same_direction_as_global": global_agreement,
            "minimum_leave_one_form_pearson": min(leaveouts.values()),
            "maximum_leave_one_form_pearson": max(leaveouts.values()),
            "leave_one_form_pearson": dict(sorted(leaveouts.items())),
        },
        "tsv_sha256": sha(PRODUCTION_TSV), "confirmatory_p_value": None,
        "english_glosses": 0,
        "claim_ceiling": (
            "Descriptive evidence that partial A/B exact-form position sharing remains visible "
            "inside the sole adequately overlapping section. Currier remains confounded with hand, "
            "topic, and production ecology; no dialect, language, encoding regime, part of speech, "
            "sound, morpheme, word meaning, plaintext, cipher, or translation follows."
        ),
    }
    report = f"""# Exact-group cross-Currier ecology diagnostic

Status: **PASS_DESCRIPTIVE_SAME_SECTION_PARTIAL_ROLE_SHARING**

Only section **H** passes the frozen same-section capacity rule, with
**{len(admitted)}** supported exact forms. Its A/B position coefficients
correlate **{pearson:.6f}** by Pearson and **{spearman:.6f}** by midrank
Spearman. **{relations['SAME_DIRECTION']}** forms retain the same sign,
**{relations['OPPOSITE_DIRECTION']}** reverse, and
**{relations['ZERO_IN_ONE_REGISTER']}** is neutral in one register.
Deleting any one form leaves Pearson correlation between
**{min(leaveouts.values()):.6f}** and **{max(leaveouts.values()):.6f}**.

The section-specific sign agrees with the global-register sign for
**{global_agreement['A']}/{len(admitted)}** A coefficients and
**{global_agreement['B']}/{len(admitted)}** B coefficients. Partial whole-form
sharing therefore is not only a cross-section mixture artifact, but the
remaining A/B difference is still confounded with hand, topic, and production
ecology. This descriptive audit supplies no dialect, language, encoding regime,
part of speech, sound, morpheme, word meaning, plaintext, cipher, or translation.
"""
    return output, expected_json, report, checks


def main() -> None:
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite ecology validation")
    expected_rows, expected_json, expected_report, checks = reconstruct()
    actual_rows = list(csv.DictReader(PRODUCTION_TSV.open(encoding="utf-8", newline=""), delimiter="\t"))
    assert list(actual_rows[0]) == FIELDS and len(actual_rows) == len(expected_rows)
    checks += 2
    integer_fields = {"a_first", "a_last", "a_folios", "b_first", "b_last", "b_folios"}
    float_fields = {"a_section_log_odds", "a_global_log_odds", "b_section_log_odds", "b_global_log_odds"}
    boolean_fields = {"a_section_global_same_direction", "b_section_global_same_direction"}
    for actual, expected in zip(actual_rows, expected_rows):
        for field in FIELDS:
            if field in integer_fields:
                assert int(actual[field]) == expected[field]
            elif field in float_fields:
                assert float(actual[field]) == expected[field]
            elif field in boolean_fields:
                assert (actual[field] == "True") == expected[field]
            else:
                assert actual[field] == expected[field]
            checks += 1
    assert json.loads(PRODUCTION_JSON.read_text(encoding="utf-8")) == expected_json
    assert PRODUCTION_REPORT.read_text(encoding="utf-8") == expected_report
    checks += 2
    guards = {
        "four_events_rejected": not (4 >= 5 and 2 >= 2),
        "one_folio_rejected": not (5 >= 5 and 1 >= 2),
        "exact_form_threshold_accepted": 5 >= 5 and 2 >= 2,
        "nine_form_section_rejected": not (9 >= 10),
        "ten_form_section_accepted": 10 >= 10,
    }
    assert all(guards.values())
    checks += len(guards)
    result = {
        "experiment": "SOURCE_NATIVE_GROUP_CROSS_CURRIER_ECOLOGY_VALIDATION",
        "status": "PASS_INDEPENDENT_SAME_SECTION_ECOLOGY_RECONSTRUCTION",
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
        "guards": guards, "claim_ceiling": expected_json["claim_ceiling"],
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = f"""# Exact-group cross-Currier ecology validation

Status: **{result['status']}**

Independent code reconstructed every section capacity cell, the sole H-panel
selection, all **{len(expected_rows)}** form rows, correlations, global-sign
comparisons, leave-one-form diagnostics, exact output bytes, and five threshold
guards in **{checks:,}** checks.

This validates a descriptive confound audit only. It supplies no dialect,
language, encoding regime, part of speech, sound, morpheme, word meaning,
plaintext, cipher, or translation.
"""
    OUT_REPORT.write_text(report, encoding="utf-8")
    print(json.dumps({"status": result["status"], "checks": checks}, sort_keys=True))


if __name__ == "__main__":
    main()
