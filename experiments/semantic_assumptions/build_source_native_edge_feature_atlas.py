#!/usr/bin/env python3
"""Extract conservative structural features from the confirmed edge model."""

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
BUILDER = Path(__file__).resolve()
OUT_TSV = RESULTS / "source_native_edge_feature_atlas.tsv"
OUT_JSON = RESULTS / "source_native_edge_feature_atlas.json"
OUT_REPORT = RESULTS / "source_native_edge_feature_atlas_report.md"

FROZEN = {
    GROUPS: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    EDGE: "2a4a246bf1d8de1f2bed76e4e790d44832e9c5ba85cc8d3ad6f2e832b035ea88",
    EDGE_VALIDATION: "0a87ffb2c23fdc6882887e5a854112d678cb6c1de1946407068462ce91fca712",
    RULES: "7f37853510144fb3e2dc3ee9458d634f41e6d95bc1fbf1c4b8f479a53a021f81",
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


def folio(page: str) -> str:
    match = re.fullmatch(r"(f\d+)[rv]\d*", page)
    if match is None:
        raise ValueError(f"bad page: {page}")
    return match.group(1)


def features(surface: str) -> dict[str, str]:
    return {
        "P1": surface[0], "P2": surface[:2],
        "S1": surface[-1], "S2": surface[-2:],
        "LEN": str(len(surface)) if len(surface) <= 7 else "8+",
    }


def family_members() -> dict[str, list[str]]:
    result = defaultdict(list)
    for raw in RULES.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 1)
        if len(parts) != 2 or not re.fullmatch(r"[A-Z][0-9A-Za-z]", parts[0]):
            continue
        result[parts[0][0]].append(f"{parts[0]}={parts[1].strip()}")
    return {key: values for key, values in sorted(result.items())}


def main() -> None:
    if any(path.exists() for path in (OUT_TSV, OUT_JSON, OUT_REPORT)):
        raise SystemExit("refusing to overwrite feature-atlas artifacts")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen input mismatch: {path.name}")
    edge = json.loads(EDGE.read_text(encoding="utf-8"))
    validation = json.loads(EDGE_VALIDATION.read_text(encoding="utf-8"))
    if edge["decision"] != "CONFIRMED_SOURCE_NATIVE_PRODUCTIVE_EDGE_GRAMMAR" or not all(edge["target_gates"].values()):
        raise SystemExit("edge grammar is not confirmed")
    if validation["status"] != "PASS_INDEPENDENT_SOURCE_NATIVE_EDGE_RECONSTRUCTION":
        raise SystemExit("edge validation is not PASS")

    with GROUPS.open(encoding="utf-8", newline="") as handle:
        source = list(csv.DictReader(handle, delimiter="\t"))
    grouped = defaultdict(list)
    for row in source:
        if row["strict_zero_alternative"] == "1":
            grouped[row["locus"]].append(row)
    endpoints = []
    for locus in sorted(grouped):
        rows = sorted(grouped[locus], key=lambda row: int(row["consensus_group_index"]))
        if len(rows) < 2:
            continue
        held = folio(rows[0]["page"])
        endpoints.append((held, "FIRST", rows[0]["family_surface"]))
        endpoints.append((held, "LAST", rows[-1]["family_surface"]))
    if len(endpoints) != 5746:
        raise ValueError("endpoint count drift")

    counts = Counter()
    held_counts = Counter()
    totals = Counter()
    held_totals = Counter()
    values_by_namespace = defaultdict(set)
    for held, role, surface in endpoints:
        for namespace, value in features(surface).items():
            counts[(role, namespace, value)] += 1
            held_counts[(held, role, namespace, value)] += 1
            totals[(role, namespace)] += 1
            held_totals[(held, role, namespace)] += 1
            values_by_namespace[namespace].add(value)
    folios = sorted({held for held, _, _ in endpoints})
    if len(folios) != 102:
        raise ValueError("folio count drift")
    member_map = family_members()
    output = []
    for namespace in ("P1", "P2", "S1", "S2", "LEN"):
        for value in sorted(values_by_namespace[namespace]):
            full = {}
            for role in ("FIRST", "LAST"):
                full[role] = math.log(
                    (counts[(role, namespace, value)] + 0.5)
                    / (totals[(role, namespace)] + 0.5 * VOCAB[namespace])
                )
            full_coefficient = full["FIRST"] - full["LAST"]
            fold_values = []
            for held in folios:
                logs = {}
                for role in ("FIRST", "LAST"):
                    count = counts[(role, namespace, value)] - held_counts[(held, role, namespace, value)]
                    total = totals[(role, namespace)] - held_totals[(held, role, namespace)]
                    logs[role] = math.log((count + 0.5) / (total + 0.5 * VOCAB[namespace]))
                fold_values.append(logs["FIRST"] - logs["LAST"])
            first_n = counts[("FIRST", namespace, value)]
            last_n = counts[("LAST", namespace, value)]
            total_n = first_n + last_n
            positive = sum(number > 0 for number in fold_values)
            negative = sum(number < 0 for number in fold_values)
            if total_n >= 20 and abs(full_coefficient) >= 0.5 and positive >= 95:
                label = "OPEN_EDGE_ASSOCIATED"
            elif total_n >= 20 and abs(full_coefficient) >= 0.5 and negative >= 95:
                label = "CLOSE_EDGE_ASSOCIATED"
            else:
                label = "UNRESOLVED"
            family_examples = []
            if namespace != "LEN":
                for family in dict.fromkeys(value):
                    family_examples.extend(member_map.get(family, [])[:4])
            output.append({
                "feature_id": f"{namespace}:{value}",
                "namespace": namespace,
                "value": value,
                "first_count": first_n,
                "last_count": last_n,
                "total_count": total_n,
                "full_log_likelihood_ratio": full_coefficient,
                "positive_folds": positive,
                "negative_folds": negative,
                "zero_folds": len(fold_values) - positive - negative,
                "minimum_fold_coefficient": min(fold_values),
                "maximum_fold_coefficient": max(fold_values),
                "mean_fold_coefficient": sum(fold_values) / len(fold_values),
                "structural_label": label,
                "family_member_examples": ";".join(family_examples),
            })
    with OUT_TSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)
    label_counts = Counter(row["structural_label"] for row in output)
    selected = [row for row in output if row["structural_label"] != "UNRESOLVED"]
    strongest_open = sorted(
        (row for row in selected if row["structural_label"] == "OPEN_EDGE_ASSOCIATED"),
        key=lambda row: (-row["full_log_likelihood_ratio"], row["feature_id"]),
    )[:12]
    strongest_close = sorted(
        (row for row in selected if row["structural_label"] == "CLOSE_EDGE_ASSOCIATED"),
        key=lambda row: (row["full_log_likelihood_ratio"], row["feature_id"]),
    )[:12]
    result = {
        "experiment": "SOURCE_NATIVE_EDGE_FEATURE_ATLAS",
        "status": "PASS_DESCRIPTIVE_CONFIRMED_MODEL_DECOMPOSITION",
        "inputs": {path.name: sha(path) for path in (*FROZEN, BUILDER)},
        "counts": {
            "endpoint_occurrences": len(endpoints),
            "physical_folios": len(folios),
            "features": len(output),
            "labels": dict(sorted(label_counts.items())),
        },
        "classification_rule": {
            "minimum_total_occurrences": 20,
            "minimum_absolute_full_log_likelihood_ratio": 0.5,
            "minimum_same_direction_held_folios": 95,
            "separately_confirmatory": False,
        },
        "strongest_open": strongest_open,
        "strongest_close": strongest_close,
        "tsv_sha256": sha(OUT_TSV),
        "english_glosses": 0,
        "claim_ceiling": (
            "Descriptive decomposition of the already confirmed combined source-native edge model. "
            "OPEN_EDGE_ASSOCIATED and CLOSE_EDGE_ASSOCIATED are stable structural associations, not "
            "separately confirmed operators, START/STOP meanings, sounds, words, linguistic morphemes, "
            "parts of speech, lexemes, plaintext, language, cipher, or translation."
        ),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    open_text = ", ".join(row["feature_id"] for row in strongest_open[:8])
    close_text = ", ".join(row["feature_id"] for row in strongest_close[:8])
    report = f"""# Source-native edge feature atlas

Status: **PASS_DESCRIPTIVE_CONFIRMED_MODEL_DECOMPOSITION**

The confirmed combined edge model contains **{label_counts['OPEN_EDGE_ASSOCIATED']}**
high-support opening-associated and **{label_counts['CLOSE_EDGE_ASSOCIATED']}**
high-support closing-associated feature values under the fixed descriptive
rule. The strongest opening-associated values are {open_text}. The strongest
closing-associated values are {close_text}.

The clearest single-family initial is `P1:P` (official STA P-family examples
include `P1=p` and `P2=f`): **{counts[('FIRST','P1','P')]}** first versus
**{counts[('LAST','P1','P')]}** last endpoints. The clearest common terminal
family contrast is `S1:B`: **{counts[('FIRST','S1','B')]}** first versus
**{counts[('LAST','S1','B')]}** last endpoints.

These are structural associations extracted from a combined model that already
passed held unseen-form validation. Individual values are descriptive, not
separately confirmed operators, words, sounds, meanings, lexemes, plaintext,
language, cipher, or translation.
"""
    OUT_REPORT.write_text(report, encoding="utf-8")
    print(json.dumps({"status": result["status"], "features": len(output), "labels": result["counts"]["labels"]}, sort_keys=True))


if __name__ == "__main__":
    main()
