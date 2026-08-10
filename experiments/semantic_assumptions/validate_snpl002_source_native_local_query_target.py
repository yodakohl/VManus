#!/usr/bin/env python3
"""Independent validator for the frozen SNPL002 target; no production import."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments" / "semantic_assumptions"
RESULTS = BASE / "results"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
SPEC = BASE / "SNPL002_SOURCE_NATIVE_LOCAL_QUERY_TARGET_SPEC.md"
PROD = RESULTS / "snpl002_source_native_local_query_target.json"
PROD_MD = RESULTS / "snpl002_source_native_local_query_target.md"
OUT = RESULTS / "snpl002_source_native_local_query_target_validation.json"
OUT_MD = RESULTS / "snpl002_source_native_local_query_target_validation.md"
READINGS = ("ZL3b", "IT2a", "RF1b")
COLUMNS = {"ZL3b": "zl_sta_codes", "IT2a": "it_sta_codes", "RF1b": "rf_sta_codes"}
LABELS = ("f89v2.6", "f102r2.21", "f102r2.22", "f102v1.17")
TARGETS = ("f48v", "f18v", "f23r", "f19r")
STRATA = (("B", "5"), ("A", "1"), ("A", "1"), ("A", "1"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def windows(sequence):
    return tuple(sorted({sequence[i:i + n] for n in (4, 5) for i in range(max(0, len(sequence) - n + 1))}, key=lambda x: (len(x), x)))


def has(group, motif):
    return any(group[i:i + len(motif)] == motif for i in range(len(group) - len(motif) + 1))


def page_raw(groups, motifs, weights):
    total = sum(weights)
    return max((sum(weight for motif, weight in zip(motifs, weights) if has(group, motif)) / total for group in groups), default=0.0)


def score(query, candidate, references):
    motifs = windows(query)
    n = len(references)
    dfs = [sum(any(has(group, motif) for group in groups) for groups in references.values()) for motif in motifs]
    weights = [math.log((n + 1) / (df + 1)) for df in dfs]
    observed = page_raw(candidate, motifs, weights)
    null = [page_raw(groups, motifs, weights) for groups in references.values()]
    rank = (sum(value < observed for value in null) + 0.5 * sum(value == observed for value in null) + 0.5) / (n + 1)
    return {"raw": observed, "midrank": rank, "reference_pages": n, "motif_df": dfs, "motif_weights": weights}, motifs, weights


def assignments(matrix):
    perms = list(itertools.permutations(range(4)))
    values = [sum(matrix[label][page] for label, page in enumerate(perm)) for perm in perms]
    diagonal = values[0]
    count = sum(value >= diagonal - 1e-15 for value in values)
    wrong = values[1:]
    return {"diagonal": diagonal, "best_wrong": max(wrong), "margin": diagonal - max(wrong), "exceed_or_tie": count, "p": count / 24, "unique_top": count == 1, "scores_sha256": hashlib.sha256(b"".join(float(value).hex().encode() + b"\n" for value in values)).hexdigest()}


def main():
    if OUT.exists() or OUT_MD.exists():
        raise RuntimeError("validation output exists")
    prod = json.loads(PROD.read_text())
    checks = 0

    def check(value, name):
        nonlocal checks
        if not value:
            raise AssertionError(name)
        checks += 1

    check(prod["spec_sha256"] == sha(SPEC), "spec")
    for relative, digest in prod["frozen_files"].items():
        check(sha(ROOT / relative) == digest, "frozen input")
    check(prod["relation_order"] == [{"label": label, "target_page": page} for label, page in zip(LABELS, TARGETS)], "order")

    labels = {}
    background = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    target_groups = {page: {reading: [] for reading in READINGS} for page in TARGETS}
    target_meta = {page: [] for page in TARGETS}
    expected_strata = dict(zip(TARGETS, STRATA))
    with GROUPS.open(newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["locus"] in LABELS:
                check(row["locus"] not in labels, "label unique")
                labels[row["locus"]] = {reading: tuple(row[column].split()) for reading, column in COLUMNS.items()}
                continue
            if row["page"] in TARGETS:
                check((row["currier"], row["hand"]) == expected_strata[row["page"]], "target stratum")
                if row["grammar_scope"] == "CONFIRMED_PROSE" and row["strict_zero_alternative"] == "1":
                    target_meta[row["page"]].append({"consensus_group_id": row["consensus_group_id"], "locus": row["locus"], "family_surface": row["family_surface"]})
                    for reading, column in COLUMNS.items():
                        target_groups[row["page"]][reading].append(tuple(row[column].split()))
                continue
            if row["section"] == "H" and row["grammar_scope"] == "CONFIRMED_PROSE" and row["strict_zero_alternative"] == "1":
                stratum = (row["currier"], row["hand"])
                for reading, column in COLUMNS.items():
                    background[stratum][reading][row["page"]].append(tuple(row[column].split()))
    background = {s: {r: {p: tuple(g) for p, g in pages.items()} for r, pages in readings.items()} for s, readings in background.items()}
    check(set(labels) == set(LABELS), "labels")
    check(prod["target_group_counts"] == {page: len(target_meta[page]) for page in TARGETS}, "target counts")

    matrices = {reading: [[0.0] * 4 for _ in range(4)] for reading in READINGS}
    details = {reading: {} for reading in READINGS}
    for reading in READINGS:
        for page_index, (page, stratum) in enumerate(zip(TARGETS, STRATA)):
            candidate = tuple(target_groups[page][reading])
            references = background[stratum][reading]
            for label_index, locus in enumerate(LABELS):
                query = labels[locus][reading]
                scored, motifs, weights = score(query, candidate, references)
                matrices[reading][label_index][page_index] = scored["midrank"]
                rows = []
                for group, meta in zip(candidate, target_meta[page]):
                    matched = [motif for motif in motifs if has(group, motif)]
                    coverage = sum(weight for motif, weight in zip(motifs, weights) if motif in matched) / sum(weights)
                    rows.append({**meta, "sequence": " ".join(group), "coverage": coverage, "matched_motifs": [" ".join(value) for value in matched]})
                maximum = max(row["coverage"] for row in rows)
                details[reading][f"{label_index}:{page_index}"] = {"score": scored, "diagnostic": {"maximum_coverage": maximum, "best_groups": [row for row in rows if row["coverage"] == maximum]}}
    pooled = [[sum(matrices[reading][i][j] for reading in READINGS) / 3 for j in range(4)] for i in range(4)]
    matrices["POOLED"] = pooled
    reconstructed_assignments = {reading: assignments(matrix) for reading, matrix in matrices.items()}
    gates = {
        "pooled_unique_top": reconstructed_assignments["POOLED"]["unique_top"],
        "every_reading_unique_top": all(reconstructed_assignments[reading]["unique_top"] for reading in READINGS),
        "three_explicit_true_labels_unique_page_best": all(pooled[i][i] > max(pooled[k][i] for k in range(4) if k != i) + 1e-15 for i in (1, 2, 3)),
        "three_explicit_true_midranks_at_least_075": all(pooled[i][i] >= 0.75 for i in (1, 2, 3)),
        "ambiguous_f89_true_midrank_at_least_050": pooled[0][0] >= 0.50,
    }
    check(matrices == prod["matrices"], "matrices")
    check(reconstructed_assignments == prod["assignments"], "assignments")
    check(details == prod["details"], "details")
    check(gates == prod["gates"], "gates")
    check(prod["passes"] == all(gates.values()), "pass")
    expected_decision = "PROVISIONAL_SAME_PLANT_REFERENCE_SIGNAL" if all(gates.values()) else "NO_SOURCE_NATIVE_LOCAL_REFERENCE_RECOVERY"
    check(prod["decision"] == expected_decision and prod["status"] == expected_decision, "decision")
    check(prod["target_rows_accessed"] is True, "target read")
    check(prod["morphology_or_plant_name_join_performed"] is False, "no morphology")
    check(prod["ocr_or_automated_vision_used"] is False, "no vision")
    ceiling = prod["claim_ceiling"].lower()
    check("plant name" in ceiling and "translation" in ceiling, "ceiling")

    validation = {"status": "PASS_INDEPENDENT_SNPL002_TARGET_RECONSTRUCTION", "checks": checks, "failures": [], "production_sha256": sha(PROD), "production_report_sha256": sha(PROD_MD), "decision": prod["decision"], "target_rows_accessed": True, "morphology_or_plant_name_join_performed": False}
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    OUT_MD.write_text(
        "# SNPL002 target independent validation\n\n"
        f"PASS: **{checks}** checks reconstruct every target group, member-window score, "
        "background midrank, 4x4 matrix, 24-way assignment, diagnostic, gate, decision, "
        "frozen hash, and claim ceiling.\n\n"
        f"Stored decision: **{prod['decision']}**. No plant name, English word, sound, "
        "language, cipher, plaintext, or translation follows from validation alone.\n"
    )


if __name__ == "__main__":
    main()
