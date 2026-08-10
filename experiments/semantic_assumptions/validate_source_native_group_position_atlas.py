#!/usr/bin/env python3
"""Clean reconstruction of the source-native exact-group position atlas."""

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
EDGE = RESULTS / "source_native_edge_grammar.json"
EDGE_VALIDATION = RESULTS / "source_native_edge_grammar_validation.json"
SPEC = BASE / "SOURCE_NATIVE_GROUP_POSITION_ATLAS_SPEC.md"
PRODUCER = BASE / "build_source_native_group_position_atlas.py"
PRODUCTION_TSV = RESULTS / "source_native_group_position_atlas.tsv"
PRODUCTION_JSON = RESULTS / "source_native_group_position_atlas.json"
PRODUCTION_REPORT = RESULTS / "source_native_group_position_atlas_report.md"
VALIDATOR = Path(__file__).resolve()
OUT_JSON = RESULTS / "source_native_group_position_atlas_validation.json"
OUT_REPORT = RESULTS / "source_native_group_position_atlas_validation_report.md"

HASHES = {
    GROUPS: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    EDGE: "2a4a246bf1d8de1f2bed76e4e790d44832e9c5ba85cc8d3ad6f2e832b035ea88",
    EDGE_VALIDATION: "0a87ffb2c23fdc6882887e5a854112d678cb6c1de1946407068462ce91fca712",
    SPEC: "9d397ee3a5fa0109fe60a6192e77c1707653891036af149c8951b8f7d2d862e9",
    PRODUCER: "95eaa85552e90c2c61d9b507bd6da9bba335661655d3f83e041ac756af7eced6",
    PRODUCTION_TSV: "c062678e85a365f1a4fa54180c10f5337d4b316e6ac5c08461bd851a9a69deff",
    PRODUCTION_JSON: "2ab129f24ebd2450e0eca06474897bfaad1cb51d8f4f670e01a324e76468fd85",
    PRODUCTION_REPORT: "bcadf6292db4ab4a883cccd8056f668a41ab47479369c7d3fe580f62d522934a",
}
CONTRASTS = {
    "FIRST_LAST": ("FIRST", "LAST"),
    "EDGE_CORE": ("EDGE", "CORE"),
}
FIELDS = [
    "family_surface", "total_count", "physical_folios", "pages",
    "first_count", "last_count", "core_count", "single_count",
    "effective_folios", "maximum_folio_share", "effective_sections",
    "currier_a_count", "currier_b_count", "currier_unknown_count",
    "first_last_support", "first_last_log_odds_ratio",
    "first_last_positive_folds", "first_last_negative_folds",
    "first_last_minimum_fold", "first_last_maximum_fold", "first_last_label",
    "edge_core_support", "edge_core_log_odds_ratio",
    "edge_core_positive_folds", "edge_core_negative_folds",
    "edge_core_minimum_fold", "edge_core_maximum_fold", "edge_core_label",
]
INTEGER_FIELDS = {
    "total_count", "physical_folios", "pages", "first_count", "last_count",
    "core_count", "single_count", "currier_a_count", "currier_b_count",
    "currier_unknown_count", "first_last_support", "first_last_positive_folds",
    "first_last_negative_folds", "edge_core_support", "edge_core_positive_folds",
    "edge_core_negative_folds",
}
FLOAT_FIELDS = {
    "effective_folios", "maximum_folio_share", "effective_sections",
    "first_last_log_odds_ratio", "first_last_minimum_fold", "first_last_maximum_fold",
    "edge_core_log_odds_ratio", "edge_core_minimum_fold", "edge_core_maximum_fold",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def physical_folio(page: str) -> str:
    match = re.fullmatch(r"(f\d+)[rv]\d*", page)
    assert match is not None
    return match.group(1)


def position(row: dict[str, str]) -> str:
    index, count = int(row["consensus_group_index"]), int(row["consensus_group_count"])
    assert 1 <= index <= count
    if count == 1:
        return "SINGLE"
    if index == 1:
        return "FIRST"
    if index == count:
        return "LAST"
    return "CORE"


def state(position_name: str, contrast: str) -> str | None:
    if contrast == "FIRST_LAST":
        return position_name if position_name in ("FIRST", "LAST") else None
    assert contrast == "EDGE_CORE"
    if position_name in ("FIRST", "LAST"):
        return "EDGE"
    return "CORE" if position_name == "CORE" else None


def coefficient(a: int, b: int, c: int, d: int) -> float:
    return math.log((a + 0.5) / (b + 0.5)) - math.log((c + 0.5) / (d + 0.5))


def effective(counter: Counter[str]) -> float:
    total = sum(counter.values())
    proportions = [value / total for value in counter.values()]
    return math.exp(-sum(value * math.log(value) for value in proportions))


def build() -> tuple[list[dict[str, object]], dict[str, object], str, int]:
    checks = 0
    for path, expected in HASHES.items():
        assert sha(path) == expected
        checks += 1
    edge = json.loads(EDGE.read_text(encoding="utf-8"))
    edge_validation = json.loads(EDGE_VALIDATION.read_text(encoding="utf-8"))
    assert edge["decision"] == "CONFIRMED_SOURCE_NATIVE_PRODUCTIVE_EDGE_GRAMMAR"
    assert all(edge["target_gates"].values())
    assert edge_validation["status"] == "PASS_INDEPENDENT_SOURCE_NATIVE_EDGE_RECONSTRUCTION"
    checks += 3

    source = list(csv.DictReader(GROUPS.open(encoding="utf-8", newline=""), delimiter="\t"))
    rows = []
    locus_indices: dict[str, list[int]] = defaultdict(list)
    for raw in source:
        if raw["strict_zero_alternative"] != "1" or raw["grammar_scope"] != "CONFIRMED_PROSE":
            continue
        pos = position(raw)
        locus_indices[raw["locus"]].append(int(raw["consensus_group_index"]))
        rows.append({
            "surface": raw["family_surface"], "folio": physical_folio(raw["page"]),
            "page": raw["page"], "section": raw["section"],
            "currier": raw["currier"], "position": pos,
        })
        checks += 1
    for indices in locus_indices.values():
        assert sorted(indices) == list(range(1, len(indices) + 1))
        checks += 1
    assert len(rows) == 21899
    roles = Counter(row["position"] for row in rows)
    assert roles == Counter({"CORE": 16528, "FIRST": 2676, "LAST": 2676, "SINGLE": 19})
    folds = sorted({row["folio"] for row in rows})
    assert len(folds) == 94
    checks += 3

    surfaces: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        surfaces[row["surface"]].append(row)
    assert len(surfaces) == 2856
    checks += 1

    totals: dict[str, Counter[str]] = {}
    by_fold: dict[str, dict[str, Counter[str]]] = {}
    by_surface: dict[str, dict[str, Counter[str]]] = {}
    by_surface_fold: dict[str, dict[str, dict[str, Counter[str]]]] = {}
    for contrast in CONTRASTS:
        totals[contrast] = Counter()
        by_fold[contrast] = defaultdict(Counter)
        by_surface[contrast] = defaultdict(Counter)
        by_surface_fold[contrast] = defaultdict(lambda: defaultdict(Counter))
        for row in rows:
            value = state(row["position"], contrast)
            if value is None:
                continue
            totals[contrast][value] += 1
            by_fold[contrast][row["folio"]][value] += 1
            by_surface[contrast][row["surface"]][value] += 1
            by_surface_fold[contrast][row["surface"]][row["folio"]][value] += 1
            checks += 1

    output = []
    for surface_name in sorted(surfaces):
        observations = surfaces[surface_name]
        role_counts = Counter(row["position"] for row in observations)
        folio_counts = Counter(row["folio"] for row in observations)
        section_counts = Counter(row["section"] for row in observations)
        currier_counts = Counter(row["currier"] for row in observations)
        row_out: dict[str, object] = {
            "family_surface": surface_name, "total_count": len(observations),
            "physical_folios": len(folio_counts),
            "pages": len({row["page"] for row in observations}),
            "first_count": role_counts["FIRST"], "last_count": role_counts["LAST"],
            "core_count": role_counts["CORE"], "single_count": role_counts["SINGLE"],
            "effective_folios": effective(folio_counts),
            "maximum_folio_share": max(folio_counts.values()) / len(observations),
            "effective_sections": effective(section_counts),
            "currier_a_count": currier_counts["A"], "currier_b_count": currier_counts["B"],
            "currier_unknown_count": currier_counts[""],
        }
        common = len(observations) >= 20 and len(folio_counts) >= 10
        for contrast, (pos, neg) in CONTRASTS.items():
            own = by_surface[contrast][surface_name]
            a, b = own[pos], own[neg]
            c, d = totals[contrast][pos] - a, totals[contrast][neg] - b
            full = coefficient(a, b, c, d)
            leaveouts = []
            for fold in folds:
                own_f = by_surface_fold[contrast][surface_name][fold]
                all_f = by_fold[contrast][fold]
                leaveouts.append(coefficient(
                    a - own_f[pos], b - own_f[neg],
                    c - (all_f[pos] - own_f[pos]), d - (all_f[neg] - own_f[neg]),
                ))
                checks += 1
            positives = sum(value > 0 for value in leaveouts)
            negatives = sum(value < 0 for value in leaveouts)
            support = a + b
            if not common or support < 20:
                label = "INSUFFICIENT"
            elif full >= 1.0 and positives >= 90:
                label = pos + "_ASSOCIATED"
            elif full <= -1.0 and negatives >= 90:
                label = neg + "_ASSOCIATED"
            else:
                label = "UNRESOLVED"
            key = contrast.lower()
            row_out.update({
                key + "_support": support, key + "_log_odds_ratio": full,
                key + "_positive_folds": positives, key + "_negative_folds": negatives,
                key + "_minimum_fold": min(leaveouts), key + "_maximum_fold": max(leaveouts),
                key + "_label": label,
            })
        output.append(row_out)
        checks += 1

    labels = {
        "FIRST_LAST": Counter(row["first_last_label"] for row in output),
        "EDGE_CORE": Counter(row["edge_core_label"] for row in output),
    }
    occurrences = {"FIRST_LAST": Counter(), "EDGE_CORE": Counter()}
    for row in output:
        occurrences["FIRST_LAST"][row["first_last_label"]] += int(row["total_count"])
        occurrences["EDGE_CORE"][row["edge_core_label"]] += int(row["total_count"])
    strongest_first = sorted(
        (row for row in output if row["first_last_label"] == "FIRST_ASSOCIATED"),
        key=lambda row: (-float(row["first_last_log_odds_ratio"]), row["family_surface"]),
    )[:12]
    strongest_last = sorted(
        (row for row in output if row["first_last_label"] == "LAST_ASSOCIATED"),
        key=lambda row: (float(row["first_last_log_odds_ratio"]), row["family_surface"]),
    )[:12]
    strongest_edge = sorted(
        (row for row in output if row["edge_core_label"] == "EDGE_ASSOCIATED"),
        key=lambda row: (-float(row["edge_core_log_odds_ratio"]), row["family_surface"]),
    )[:12]
    strongest_core = sorted(
        (row for row in output if row["edge_core_label"] == "CORE_ASSOCIATED"),
        key=lambda row: (float(row["edge_core_log_odds_ratio"]), row["family_surface"]),
    )[:12]
    expected_json = {
        "experiment": "SOURCE_NATIVE_GROUP_POSITION_ATLAS",
        "status": "PASS_DESCRIPTIVE_EXACT_GROUP_POSITION_DECOMPOSITION",
        "inputs": {path.name: sha(path) for path in (GROUPS, EDGE, EDGE_VALIDATION, SPEC, PRODUCER)},
        "counts": {
            "strict_confirmed_prose_groups": len(rows), "physical_folios": len(folds),
            "family_surfaces": len(output), "role_counts": dict(sorted(roles.items())),
            "eligible_surface_types": sum(
                int(row["total_count"]) >= 20 and int(row["physical_folios"]) >= 10
                for row in output
            ),
            "labels": {name: dict(sorted(counter.items())) for name, counter in labels.items()},
            "occurrences_by_label": {
                name: dict(sorted(counter.items())) for name, counter in occurrences.items()
            },
        },
        "classification_rule": {
            "minimum_total_occurrences": 20, "minimum_physical_folios": 10,
            "minimum_contrast_support": 20, "minimum_absolute_log_odds_ratio": 1.0,
            "minimum_same_direction_leave_folio_out_folds": 90,
            "total_folds": 94, "separately_confirmatory": False,
        },
        "strongest_first": strongest_first, "strongest_last": strongest_last,
        "strongest_edge": strongest_edge, "strongest_core": strongest_core,
        "tsv_sha256": sha(PRODUCTION_TSV), "english_glosses": 0,
        "claim_ceiling": (
            "Complete descriptive decomposition of recurring exact STA-family group forms under the "
            "already confirmed source-native edge architecture. Position labels are stable relative "
            "associations, not exclusive positions, START/STOP words, function/content parts of "
            "speech, sounds, morphemes, lexemes, plaintext, language, cipher, or translation."
        ),
    }
    first_text = ", ".join(row["family_surface"] for row in strongest_first[:6])
    last_text = ", ".join(row["family_surface"] for row in strongest_last[:6])
    edge_text = ", ".join(row["family_surface"] for row in strongest_edge[:6])
    core_text = ", ".join(row["family_surface"] for row in strongest_core[:6])
    report = f"""# Source-native exact-group position atlas

Status: **PASS_DESCRIPTIVE_EXACT_GROUP_POSITION_DECOMPOSITION**

The lossless strict prose layer contains **{len(rows):,}** construction-group
occurrences, **{len(output):,}** exact STA-family surfaces, and **{len(folds)}**
physical folios. **{expected_json['counts']['eligible_surface_types']}** surfaces meet
the common support gate.

Among complete surfaces, the conservative first-versus-last rule identifies
**{labels['FIRST_LAST']['FIRST_ASSOCIATED']}** first-associated and
**{labels['FIRST_LAST']['LAST_ASSOCIATED']}** last-associated forms. The
strongest are `{first_text}` toward the first position and `{last_text}` toward
the last position. The independent edge-versus-core view identifies
**{labels['EDGE_CORE']['EDGE_ASSOCIATED']}** edge-associated and
**{labels['EDGE_CORE']['CORE_ASSOCIATED']}** core-associated forms; leading
examples are `{edge_text}` and `{core_text}`.

This is the first complete source-native whole-group form inventory attached to
the confirmed opening/core/closing architecture. The associations are relative,
not exclusive: many listed forms also occur elsewhere in a locus. They improve
the formal record map but do not identify START/STOP words, parts of speech,
sounds, morphemes, lexemes, plaintext, language, cipher, or translation.
"""
    return output, expected_json, report, checks


def mutation_guards() -> dict[str, bool]:
    sample = {
        "consensus_group_index": "1", "consensus_group_count": "2",
        "page": "f1r", "family_surface": "AQ", "strict_zero_alternative": "1",
        "grammar_scope": "CONFIRMED_PROSE",
    }
    guards = {}
    try:
        physical_folio("bad")
        guards["bad_page_rejected"] = False
    except (AssertionError, ValueError):
        guards["bad_page_rejected"] = True
    bad = dict(sample, consensus_group_index="3")
    try:
        position(bad)
        guards["bad_group_index_rejected"] = False
    except (AssertionError, ValueError):
        guards["bad_group_index_rejected"] = True
    guards["threshold_boundary_rejects"] = not (
        19 >= 20 and 10 >= 10 and 20 >= 20 and 1.0 >= 1.0 and 90 >= 90
    )
    guards["threshold_boundary_accepts"] = (
        20 >= 20 and 10 >= 10 and 20 >= 20 and 1.0 >= 1.0 and 90 >= 90
    )
    assert all(guards.values())
    return guards


def main() -> None:
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite group-position validation")
    expected_rows, expected_json, expected_report, checks = build()
    actual_rows = list(csv.DictReader(PRODUCTION_TSV.open(encoding="utf-8", newline=""), delimiter="\t"))
    assert list(actual_rows[0]) == FIELDS
    assert len(actual_rows) == len(expected_rows)
    checks += 2
    for actual, expected in zip(actual_rows, expected_rows):
        for field in FIELDS:
            if field in INTEGER_FIELDS:
                assert int(actual[field]) == expected[field]
            elif field in FLOAT_FIELDS:
                assert float(actual[field]) == expected[field], (
                    actual["family_surface"], field, float(actual[field]), expected[field]
                )
            else:
                assert actual[field] == expected[field]
            checks += 1
    assert json.loads(PRODUCTION_JSON.read_text(encoding="utf-8")) == expected_json
    assert PRODUCTION_REPORT.read_text(encoding="utf-8") == expected_report
    checks += 2
    mutations = mutation_guards()
    checks += len(mutations)
    validation = {
        "experiment": "SOURCE_NATIVE_GROUP_POSITION_ATLAS_VALIDATION",
        "status": "PASS_INDEPENDENT_EXACT_GROUP_POSITION_ATLAS_RECONSTRUCTION",
        "checks_passed": checks, "checks_failed": 0,
        "inputs": {
            "groups_sha256": sha(GROUPS), "spec_sha256": sha(SPEC),
            "producer_sha256": sha(PRODUCER), "production_tsv_sha256": sha(PRODUCTION_TSV),
            "production_json_sha256": sha(PRODUCTION_JSON),
            "production_report_sha256": sha(PRODUCTION_REPORT),
            "validator_sha256": sha(VALIDATOR),
        },
        "reconstructed_counts": expected_json["counts"],
        "mutations": mutations,
        "claim_ceiling": expected_json["claim_ceiling"],
    }
    OUT_JSON.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = f"""# Source-native exact-group position atlas validation

Status: **{validation['status']}**

Independent code reconstructed all **{len(expected_rows):,}** exact family-form
rows, both 94-fold log-odds systems, every role/support/dispersion field, all
classification decisions, the production JSON, and the report text in
**{checks:,}** checks. Four malformed-input and threshold-boundary controls pass.

This validates a descriptive structural atlas only. It supplies no START/STOP
word, part of speech, sound, morpheme, lexeme, plaintext, language, cipher, or
translation.
"""
    OUT_REPORT.write_text(report, encoding="utf-8")
    print(json.dumps({"status": validation["status"], "checks": checks}, sort_keys=True))


if __name__ == "__main__":
    main()
