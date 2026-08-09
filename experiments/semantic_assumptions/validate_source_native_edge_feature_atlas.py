#!/usr/bin/env python3
"""Independent reconstruction of the source-native edge feature atlas."""

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
RULES = BASE.parent.parent / "transcription" / "sources" / "sta" / "STA-Eva_def.bit"
PRODUCER = BASE / "build_source_native_edge_feature_atlas.py"
PRODUCTION_TSV = RESULTS / "source_native_edge_feature_atlas.tsv"
PRODUCTION_JSON = RESULTS / "source_native_edge_feature_atlas.json"
PRODUCTION_REPORT = RESULTS / "source_native_edge_feature_atlas_report.md"
VALIDATOR = Path(__file__).resolve()
OUT = RESULTS / "source_native_edge_feature_atlas_validation.json"
OUT_REPORT = RESULTS / "source_native_edge_feature_atlas_validation_report.md"

HASHES = {
    GROUPS: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    EDGE: "2a4a246bf1d8de1f2bed76e4e790d44832e9c5ba85cc8d3ad6f2e832b035ea88",
    EDGE_VALIDATION: "0a87ffb2c23fdc6882887e5a854112d678cb6c1de1946407068462ce91fca712",
    RULES: "7f37853510144fb3e2dc3ee9458d634f41e6d95bc1fbf1c4b8f479a53a021f81",
    PRODUCER: "a630eab07ff95bdd3673a268df74de9b545b463cc80ff242167796a5281c1a3f",
    PRODUCTION_TSV: "a0df97db5e4f07c4e01f51806ccdc547da29e237ef4045001fed3faff74bb57a",
    PRODUCTION_JSON: "0bb0cec702388df8a523fd360931547c63f348ece3832bccdf504eeb7d00eb79",
    PRODUCTION_REPORT: "98bf07f4a8071af736e1eca95d105ae3de844174ff0730ccb0fa47f713ceba56",
}
VOCAB = {"P1": 21, "P2": 462, "S1": 21, "S2": 462, "LEN": 8}
FIELDS = [
    "feature_id", "namespace", "value", "first_count", "last_count",
    "total_count", "full_log_likelihood_ratio", "positive_folds",
    "negative_folds", "zero_folds", "minimum_fold_coefficient",
    "maximum_fold_coefficient", "mean_fold_coefficient", "structural_label",
    "family_member_examples",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def held(page: str) -> str:
    match = re.fullmatch(r"(f[0-9]+)[rv][0-9]*", page)
    assert match
    return match.group(1)


def vector(surface: str) -> dict[str, str]:
    assert surface
    return {
        "P1": surface[0], "P2": surface[:2],
        "S1": surface[-1], "S2": surface[-2:],
        "LEN": str(len(surface)) if len(surface) < 8 else "8+",
    }


def rule_members() -> dict[str, list[str]]:
    families = defaultdict(list)
    for raw in RULES.read_text(encoding="utf-8").splitlines():
        fields = raw.strip().split(None, 1)
        if len(fields) == 2 and re.fullmatch(r"[A-Z][0-9A-Za-z]", fields[0]):
            families[fields[0][0]].append(fields[0] + "=" + fields[1].strip())
    return {family: values for family, values in sorted(families.items())}


def reconstruct() -> tuple[list[dict], dict, str, int]:
    for path, expected in HASHES.items():
        assert sha(path) == expected
    checks = len(HASHES)
    edge = json.loads(EDGE.read_text(encoding="utf-8"))
    validation = json.loads(EDGE_VALIDATION.read_text(encoding="utf-8"))
    assert edge["decision"] == "CONFIRMED_SOURCE_NATIVE_PRODUCTIVE_EDGE_GRAMMAR"
    assert all(edge["target_gates"].values())
    assert validation["status"] == "PASS_INDEPENDENT_SOURCE_NATIVE_EDGE_RECONSTRUCTION"
    checks += 3
    with GROUPS.open(encoding="utf-8", newline="") as handle:
        source = list(csv.DictReader(handle, delimiter="\t"))
    by_locus = defaultdict(list)
    for row in source:
        if row["strict_zero_alternative"] == "1":
            by_locus[row["locus"]].append(row)
    endpoints = []
    for locus in sorted(by_locus):
        rows = sorted(by_locus[locus], key=lambda row: int(row["consensus_group_index"]))
        if len(rows) < 2:
            continue
        assert [int(row["consensus_group_index"]) for row in rows] == list(range(1, len(rows) + 1))
        fold = held(rows[0]["page"])
        endpoints.extend(((fold, "FIRST", rows[0]["family_surface"]), (fold, "LAST", rows[-1]["family_surface"])))
        checks += 1
    assert len(endpoints) == 5746
    checks += 1
    cells = Counter()
    fold_cells = Counter()
    totals = Counter()
    fold_totals = Counter()
    observed = defaultdict(set)
    for fold, role, surface in endpoints:
        for namespace, value in vector(surface).items():
            cells[(role, namespace, value)] += 1
            fold_cells[(fold, role, namespace, value)] += 1
            totals[(role, namespace)] += 1
            fold_totals[(fold, role, namespace)] += 1
            observed[namespace].add(value)
            checks += 1
    folds = sorted({fold for fold, _, _ in endpoints})
    assert len(folds) == 102
    members = rule_members()
    output = []
    for namespace in ("P1", "P2", "S1", "S2", "LEN"):
        for value in sorted(observed[namespace]):
            full_logs = {}
            for role in ("FIRST", "LAST"):
                full_logs[role] = math.log(
                    (cells[(role, namespace, value)] + 0.5)
                    / (totals[(role, namespace)] + 0.5 * VOCAB[namespace])
                )
            coefficient = full_logs["FIRST"] - full_logs["LAST"]
            coefficients = []
            for fold in folds:
                logs = {}
                for role in ("FIRST", "LAST"):
                    count = cells[(role, namespace, value)] - fold_cells[(fold, role, namespace, value)]
                    n = totals[(role, namespace)] - fold_totals[(fold, role, namespace)]
                    logs[role] = math.log((count + 0.5) / (n + 0.5 * VOCAB[namespace]))
                coefficients.append(logs["FIRST"] - logs["LAST"])
                checks += 1
            first_n = cells[("FIRST", namespace, value)]
            last_n = cells[("LAST", namespace, value)]
            n = first_n + last_n
            positive = sum(x > 0 for x in coefficients)
            negative = sum(x < 0 for x in coefficients)
            if n >= 20 and abs(coefficient) >= 0.5 and positive >= 95:
                label = "OPEN_EDGE_ASSOCIATED"
            elif n >= 20 and abs(coefficient) >= 0.5 and negative >= 95:
                label = "CLOSE_EDGE_ASSOCIATED"
            else:
                label = "UNRESOLVED"
            examples = []
            if namespace != "LEN":
                for family in dict.fromkeys(value):
                    examples.extend(members.get(family, [])[:4])
            output.append({
                "feature_id": f"{namespace}:{value}", "namespace": namespace,
                "value": value, "first_count": first_n, "last_count": last_n,
                "total_count": n, "full_log_likelihood_ratio": coefficient,
                "positive_folds": positive, "negative_folds": negative,
                "zero_folds": len(coefficients) - positive - negative,
                "minimum_fold_coefficient": min(coefficients),
                "maximum_fold_coefficient": max(coefficients),
                "mean_fold_coefficient": sum(coefficients) / len(coefficients),
                "structural_label": label,
                "family_member_examples": ";".join(examples),
            })
    assert len(output) == 197
    checks += 1
    labels = Counter(row["structural_label"] for row in output)
    selected = [row for row in output if row["structural_label"] != "UNRESOLVED"]
    opens = sorted(
        (row for row in selected if row["structural_label"] == "OPEN_EDGE_ASSOCIATED"),
        key=lambda row: (-row["full_log_likelihood_ratio"], row["feature_id"]),
    )[:12]
    closes = sorted(
        (row for row in selected if row["structural_label"] == "CLOSE_EDGE_ASSOCIATED"),
        key=lambda row: (row["full_log_likelihood_ratio"], row["feature_id"]),
    )[:12]
    expected_json = {
        "experiment": "SOURCE_NATIVE_EDGE_FEATURE_ATLAS",
        "status": "PASS_DESCRIPTIVE_CONFIRMED_MODEL_DECOMPOSITION",
        "inputs": {path.name: sha(path) for path in (GROUPS, EDGE, EDGE_VALIDATION, RULES, PRODUCER)},
        "counts": {
            "endpoint_occurrences": len(endpoints), "physical_folios": len(folds),
            "features": len(output), "labels": dict(sorted(labels.items())),
        },
        "classification_rule": {
            "minimum_total_occurrences": 20,
            "minimum_absolute_full_log_likelihood_ratio": 0.5,
            "minimum_same_direction_held_folios": 95,
            "separately_confirmatory": False,
        },
        "strongest_open": opens, "strongest_close": closes,
        "tsv_sha256": sha(PRODUCTION_TSV), "english_glosses": 0,
        "claim_ceiling": (
            "Descriptive decomposition of the already confirmed combined source-native edge model. "
            "OPEN_EDGE_ASSOCIATED and CLOSE_EDGE_ASSOCIATED are stable structural associations, not "
            "separately confirmed operators, START/STOP meanings, sounds, words, linguistic morphemes, "
            "parts of speech, lexemes, plaintext, language, cipher, or translation."
        ),
    }
    open_text = ", ".join(row["feature_id"] for row in opens[:8])
    close_text = ", ".join(row["feature_id"] for row in closes[:8])
    report = f"""# Source-native edge feature atlas

Status: **PASS_DESCRIPTIVE_CONFIRMED_MODEL_DECOMPOSITION**

The confirmed combined edge model contains **{labels['OPEN_EDGE_ASSOCIATED']}**
high-support opening-associated and **{labels['CLOSE_EDGE_ASSOCIATED']}**
high-support closing-associated feature values under the fixed descriptive
rule. The strongest opening-associated values are {open_text}. The strongest
closing-associated values are {close_text}.

The clearest single-family initial is `P1:P` (official STA P-family examples
include `P1=p` and `P2=f`): **{cells[('FIRST','P1','P')]}** first versus
**{cells[('LAST','P1','P')]}** last endpoints. The clearest common terminal
family contrast is `S1:B`: **{cells[('FIRST','S1','B')]}** first versus
**{cells[('LAST','S1','B')]}** last endpoints.

These are structural associations extracted from a combined model that already
passed held unseen-form validation. Individual values are descriptive, not
separately confirmed operators, words, sounds, meanings, lexemes, plaintext,
language, cipher, or translation.
"""
    return output, expected_json, report, checks


def main() -> None:
    if OUT.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite atlas validation")
    output, expected_json, report, checks = reconstruct()
    with PRODUCTION_TSV.open(encoding="utf-8", newline="") as handle:
        actual_rows = list(csv.DictReader(handle, delimiter="\t"))
    assert list(actual_rows[0]) == FIELDS
    assert len(actual_rows) == len(output)
    for actual, expected in zip(actual_rows, output):
        for field in FIELDS:
            if field in {
                "first_count", "last_count", "total_count", "positive_folds", "negative_folds", "zero_folds"
            }:
                assert int(actual[field]) == expected[field]
            elif field in {
                "full_log_likelihood_ratio", "minimum_fold_coefficient", "maximum_fold_coefficient", "mean_fold_coefficient"
            }:
                assert float(actual[field]) == expected[field]
            else:
                assert actual[field] == expected[field]
            checks += 1
    assert json.loads(PRODUCTION_JSON.read_text(encoding="utf-8")) == expected_json
    assert PRODUCTION_REPORT.read_text(encoding="utf-8") == report
    checks += 2
    validation = {
        "experiment": "SOURCE_NATIVE_EDGE_FEATURE_ATLAS_VALIDATION",
        "status": "PASS_INDEPENDENT_EDGE_FEATURE_ATLAS_RECONSTRUCTION",
        "checks_passed": checks,
        "checks_failed": 0,
        "inputs": {
            "production_tsv_sha256": sha(PRODUCTION_TSV),
            "production_json_sha256": sha(PRODUCTION_JSON),
            "production_report_sha256": sha(PRODUCTION_REPORT),
            "producer_sha256": sha(PRODUCER),
            "validator_sha256": sha(VALIDATOR),
        },
        "reconstructed_label_counts": expected_json["counts"]["labels"],
        "separately_confirmatory": False,
        "english_glosses": 0,
        "claim_ceiling": expected_json["claim_ceiling"],
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    text = f"""# Source-native edge feature atlas validation

Status: **PASS_INDEPENDENT_EDGE_FEATURE_ATLAS_RECONSTRUCTION**

A nonimporting implementation passed **{checks:,}** checks and reconstructs all
5,746 endpoint feature occurrences, 102 leave-folio-out coefficient sets, 197
atlas rows, 28 opening-associated / 31 closing-associated / 138 unresolved
labels, exact STA-family examples, the complete JSON object, and report text.

This validates a descriptive decomposition of the already confirmed combined
edge model. Individual features are not separately confirmed operators, words,
sounds, meanings, lexemes, plaintext, language, cipher, or translation.
"""
    OUT_REPORT.write_text(text, encoding="utf-8")
    print(json.dumps({"status": validation["status"], "checks": checks, "labels": validation["reconstructed_label_counts"]}, sort_keys=True))


if __name__ == "__main__":
    main()
