#!/usr/bin/env python3
"""Same-section confound audit for exact-group Currier role sharing."""

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
AUDITOR = Path(__file__).resolve()
OUT_TSV = RESULTS / "source_native_group_cross_currier_ecology.tsv"
OUT_JSON = RESULTS / "source_native_group_cross_currier_ecology.json"
OUT_REPORT = RESULTS / "source_native_group_cross_currier_ecology_report.md"

FROZEN = {
    GROUPS: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    PRIOR_TSV: "7558fd6f3eeb05f8f3b5ddad3835baf41534749b9d34d103db5ad3cbefce1fb7",
    PRIOR_JSON: "dd5028429070662cf54fe7c9b6336ea99d2325e39aa3acab57773932bba3833f",
    PRIOR_VALIDATION: "53344c2e20b12e642a8ca12542165412b1634d257888b16a24d26d1db32ef45e",
}
FIELDS = [
    "family_surface", "a_first", "a_last", "a_folios", "a_section_log_odds",
    "a_global_log_odds", "a_section_global_same_direction", "b_first", "b_last",
    "b_folios", "b_section_log_odds", "b_global_log_odds",
    "b_section_global_same_direction", "section_cross_register_relation",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def folio(page: str) -> str:
    match = re.fullmatch(r"(f\d+)[rv]\d*", page)
    if match is None:
        raise ValueError(page)
    return match.group(1)


def sign(value: float) -> int:
    return 1 if value > 0 else -1 if value < 0 else 0


def correlation(left: list[float], right: list[float]) -> float:
    mean_left, mean_right = sum(left) / len(left), sum(right) / len(right)
    numerator = sum((a - mean_left) * (b - mean_right) for a, b in zip(left, right))
    denominator = math.sqrt(
        sum((a - mean_left) ** 2 for a in left)
        * sum((b - mean_right) ** 2 for b in right)
    )
    if denominator == 0:
        raise ValueError("zero variance")
    return numerator / denominator


def midranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda index: (values[index], index))
    ranks = [0.0] * len(values)
    start = 0
    while start < len(order):
        stop = start + 1
        while stop < len(order) and values[order[stop]] == values[order[start]]:
            stop += 1
        rank = (start + stop - 1) / 2 + 1
        for index in order[start:stop]:
            ranks[index] = rank
        start = stop
    return ranks


def main() -> None:
    if any(path.exists() for path in (OUT_TSV, OUT_JSON, OUT_REPORT)):
        raise SystemExit("refusing to overwrite ecology diagnostic")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen input mismatch: {path.name}")
    prior = json.loads(PRIOR_JSON.read_text(encoding="utf-8"))
    validation = json.loads(PRIOR_VALIDATION.read_text(encoding="utf-8"))
    if prior["status"] != "PASS_DESCRIPTIVE_PARTIAL_EXACT_FORM_ROLE_SHARING":
        raise SystemExit("prior diagnostic is not PASS")
    if validation["status"] != "PASS_INDEPENDENT_CROSS_CURRIER_DIAGNOSTIC_RECONSTRUCTION":
        raise SystemExit("prior validation is not PASS")
    prior_rows = list(csv.DictReader(PRIOR_TSV.open(encoding="utf-8", newline=""), delimiter="\t"))
    prior_forms = {row["family_surface"] for row in prior_rows}
    if len(prior_forms) != 25 or len(prior_rows) != 25:
        raise ValueError("prior form panel drift")
    global_coefficients = {
        (row["family_surface"], register): float(row[f"{register.lower()}_log_odds_ratio"])
        for row in prior_rows for register in ("A", "B")
    }

    cells: Counter[tuple[str, str, str, str]] = Counter()
    support_folios: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    totals: Counter[tuple[str, str, str]] = Counter()
    for row in csv.DictReader(GROUPS.open(encoding="utf-8", newline=""), delimiter="\t"):
        if row["strict_zero_alternative"] != "1" or row["grammar_scope"] != "CONFIRMED_PROSE":
            continue
        register, surface = row["currier"], row["family_surface"]
        if register not in {"A", "B"}:
            continue
        index, count = int(row["consensus_group_index"]), int(row["consensus_group_count"])
        if count < 2 or index not in {1, count}:
            continue
        endpoint = "FIRST" if index == 1 else "LAST"
        section = row["section"]
        totals[(section, register, endpoint)] += 1
        if surface in prior_forms:
            cells[(section, register, surface, endpoint)] += 1
            support_folios[(section, register, surface)].add(folio(row["page"]))

    sections = sorted({key[0] for key in totals})
    capacity = {}
    section_forms = {}
    for section in sections:
        admitted = [
            surface for surface in sorted(prior_forms)
            if all(
                cells[(section, register, surface, "FIRST")]
                + cells[(section, register, surface, "LAST")] >= 5
                and len(support_folios[(section, register, surface)]) >= 2
                for register in ("A", "B")
            )
        ]
        section_forms[section] = admitted
        capacity[section] = {
            "common_support_forms": len(admitted),
            "a_endpoint_events_all_surfaces": totals[(section, "A", "FIRST")]
            + totals[(section, "A", "LAST")],
            "b_endpoint_events_all_surfaces": totals[(section, "B", "FIRST")]
            + totals[(section, "B", "LAST")],
        }
    eligible_sections = [section for section in sections if len(section_forms[section]) >= 10]
    if eligible_sections != ["H"]:
        raise ValueError(f"same-section capacity stop: {eligible_sections}")
    section = "H"
    admitted = section_forms[section]
    if len(admitted) != 14:
        raise ValueError("H form capacity drift")

    output = []
    for surface in admitted:
        item: dict[str, object] = {"family_surface": surface}
        section_signs = {}
        for register, prefix in (("A", "a"), ("B", "b")):
            first = cells[(section, register, surface, "FIRST")]
            last = cells[(section, register, surface, "LAST")]
            other_first = totals[(section, register, "FIRST")] - first
            other_last = totals[(section, register, "LAST")] - last
            value = math.log((first + 0.5) / (last + 0.5)) - math.log(
                (other_first + 0.5) / (other_last + 0.5)
            )
            global_value = global_coefficients[(surface, register)]
            section_signs[register] = sign(value)
            item.update({
                f"{prefix}_first": first, f"{prefix}_last": last,
                f"{prefix}_folios": len(support_folios[(section, register, surface)]),
                f"{prefix}_section_log_odds": value,
                f"{prefix}_global_log_odds": global_value,
                f"{prefix}_section_global_same_direction": sign(value) == sign(global_value),
            })
        item["section_cross_register_relation"] = (
            "ZERO_IN_ONE_REGISTER" if 0 in section_signs.values()
            else "SAME_DIRECTION" if section_signs["A"] == section_signs["B"]
            else "OPPOSITE_DIRECTION"
        )
        output.append(item)

    with OUT_TSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)

    a_values = [float(row["a_section_log_odds"]) for row in output]
    b_values = [float(row["b_section_log_odds"]) for row in output]
    pearson = correlation(a_values, b_values)
    spearman = correlation(midranks(a_values), midranks(b_values))
    leaveouts = {}
    for index, row in enumerate(output):
        leaveouts[row["family_surface"]] = correlation(
            a_values[:index] + a_values[index + 1:],
            b_values[:index] + b_values[index + 1:],
        )
    relation_counts = Counter(row["section_cross_register_relation"] for row in output)
    global_agreement = {
        register: sum(bool(row[f"{register.lower()}_section_global_same_direction"]) for row in output)
        for register in ("A", "B")
    }
    result = {
        "experiment": "SOURCE_NATIVE_GROUP_CROSS_CURRIER_ECOLOGY",
        "status": "PASS_DESCRIPTIVE_SAME_SECTION_PARTIAL_ROLE_SHARING",
        "inputs": {path.name: sha(path) for path in (*FROZEN, SPEC, AUDITOR)},
        "capacity": {
            "prior_forms": len(prior_forms), "minimum_endpoints_per_register_section": 5,
            "minimum_folios_per_register_section": 2,
            "minimum_common_forms_for_section": 10,
            "sections": capacity, "eligible_sections": eligible_sections,
            "selected_section": section, "selected_forms": len(admitted),
        },
        "summary": {
            "pearson_section_log_odds": pearson,
            "spearman_section_log_odds": spearman,
            "section_direction_relations": dict(sorted(relation_counts.items())),
            "same_direction_as_global": global_agreement,
            "minimum_leave_one_form_pearson": min(leaveouts.values()),
            "maximum_leave_one_form_pearson": max(leaveouts.values()),
            "leave_one_form_pearson": dict(sorted(leaveouts.items())),
        },
        "tsv_sha256": sha(OUT_TSV), "confirmatory_p_value": None,
        "english_glosses": 0,
        "claim_ceiling": (
            "Descriptive evidence that partial A/B exact-form position sharing remains visible "
            "inside the sole adequately overlapping section. Currier remains confounded with hand, "
            "topic, and production ecology; no dialect, language, encoding regime, part of speech, "
            "sound, morpheme, word meaning, plaintext, cipher, or translation follows."
        ),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = f"""# Exact-group cross-Currier ecology diagnostic

Status: **PASS_DESCRIPTIVE_SAME_SECTION_PARTIAL_ROLE_SHARING**

Only section **H** passes the frozen same-section capacity rule, with
**{len(admitted)}** supported exact forms. Its A/B position coefficients
correlate **{pearson:.6f}** by Pearson and **{spearman:.6f}** by midrank
Spearman. **{relation_counts['SAME_DIRECTION']}** forms retain the same sign,
**{relation_counts['OPPOSITE_DIRECTION']}** reverse, and
**{relation_counts['ZERO_IN_ONE_REGISTER']}** is neutral in one register.
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
    OUT_REPORT.write_text(report, encoding="utf-8")
    print(json.dumps({
        "status": result["status"], "section": section, "forms": len(admitted),
        "pearson": pearson, "relations": result["summary"]["section_direction_relations"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
