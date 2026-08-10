#!/usr/bin/env python3
"""Execute the single frozen SNPL002 four-pair target."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

from snpl002_core import (
    COLUMNS, EXPLICIT_INDICES, LABEL_LOCI, READINGS, STRATA, TARGET_PAGES,
    assignment_summary, calibrated_score, contains, load_panel, query_motifs,
)


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments" / "semantic_assumptions"
RESULTS = BASE / "results"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
CORE = BASE / "snpl002_core.py"
SPEC = BASE / "SNPL002_SOURCE_NATIVE_LOCAL_QUERY_TARGET_SPEC.md"
PREFLIGHT = RESULTS / "snpl002_source_native_local_query_preflight.json"
PREFLIGHT_VALIDATION = RESULTS / "snpl002_source_native_local_query_preflight_validation.json"
SOURCE_CAPACITY = RESULTS / "public_repeated_plant_source_native_capacity.json"
OUT = RESULTS / "snpl002_source_native_local_query_target.json"
OUT_MD = RESULTS / "snpl002_source_native_local_query_target.md"
EXPECTED = {
    GROUPS: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    CORE: "2428f77378453d6f430a81a0f782acc922e57dda79030d289e80b77fe49b0050",
    PREFLIGHT: "3f15388b0559a959e39e83ce71f3840e5b5bd76e166f441e6eef6faaa51bce06",
    PREFLIGHT_VALIDATION: "6a9e22bf6017bd6a5f70fe0b4f0cadc857d1e1bec64ef0578eca5ded11fcfea2",
    SOURCE_CAPACITY: "a16700eafc88653c3b95f8fcd840a4c86a185ca240a0e19123e880a46373cb2e",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_targets() -> dict:
    expected_strata = dict(zip(TARGET_PAGES, STRATA))
    values = {page: {reading: [] for reading in READINGS} for page in TARGET_PAGES}
    metadata = {page: [] for page in TARGET_PAGES}
    with GROUPS.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            page = row["page"]
            if page not in values:
                continue
            if (row["currier"], row["hand"]) != expected_strata[page]:
                raise RuntimeError(("target stratum", page, row["currier"], row["hand"]))
            if row["section"] != "H":
                raise RuntimeError(("target section", page, row["section"]))
            if row["grammar_scope"] != "CONFIRMED_PROSE" or row["strict_zero_alternative"] != "1":
                continue
            metadata[page].append({
                "consensus_group_id": row["consensus_group_id"],
                "locus": row["locus"],
                "family_surface": row["family_surface"],
            })
            for reading, column in COLUMNS.items():
                values[page][reading].append(tuple(row[column].split()))
    for page in TARGET_PAGES:
        if not metadata[page]:
            raise RuntimeError(("empty target", page))
        if not all(len(values[page][reading]) == len(metadata[page]) for reading in READINGS):
            raise RuntimeError(("reading alignment", page))
    return {"groups": values, "metadata": metadata}


def diagnostic(query, groups, metadata, references):
    query_windows = query_motifs(query)
    n = len(references)
    frequencies = [
        sum(any(contains(group, motif) for group in page_groups) for page_groups in references.values())
        for motif in query_windows
    ]
    weights = [math.log((n + 1) / (frequency + 1)) for frequency in frequencies]
    denominator = sum(weights)
    rows = []
    for group, meta in zip(groups, metadata):
        matched = [motif for motif in query_windows if contains(group, motif)]
        coverage = sum(weight for motif, weight in zip(query_windows, weights) if motif in matched) / denominator
        rows.append({
            **meta,
            "sequence": " ".join(group),
            "coverage": coverage,
            "matched_motifs": [" ".join(value) for value in matched],
        })
    maximum = max(row["coverage"] for row in rows)
    return {"maximum_coverage": maximum, "best_groups": [row for row in rows if row["coverage"] == maximum]}


def main() -> None:
    if OUT.exists() or OUT_MD.exists():
        raise RuntimeError("target output already exists")
    for path, digest in EXPECTED.items():
        if sha(path) != digest:
            raise RuntimeError(("frozen hash", path.name, sha(path), digest))
    preflight = json.loads(PREFLIGHT.read_text())
    validation = json.loads(PREFLIGHT_VALIDATION.read_text())
    if preflight["decision"] != "GO_FREEZE_SNPL002_TARGET" or not validation["status"].startswith("PASS_"):
        raise RuntimeError("preflight gate")

    panel = load_panel(GROUPS)
    targets = load_targets()
    matrices = {reading: [[0.0] * 4 for _ in range(4)] for reading in READINGS}
    details = {reading: {} for reading in READINGS}
    for reading in READINGS:
        for page_index, (page, stratum) in enumerate(zip(TARGET_PAGES, STRATA)):
            candidate = tuple(targets["groups"][page][reading])
            references = panel.background[stratum][reading]
            for label_index, locus in enumerate(LABEL_LOCI):
                query = panel.labels[locus][reading]
                score = calibrated_score(query, candidate, references)
                matrices[reading][label_index][page_index] = score["midrank"]
                details[reading][f"{label_index}:{page_index}"] = {
                    "score": score,
                    "diagnostic": diagnostic(query, candidate, targets["metadata"][page], references),
                }

    pooled = [[sum(matrices[reading][i][j] for reading in READINGS) / 3 for j in range(4)] for i in range(4)]
    matrices["POOLED"] = pooled
    assignments = {reading: assignment_summary(matrix) for reading, matrix in matrices.items()}
    gates = {
        "pooled_unique_top": assignments["POOLED"]["unique_top"],
        "every_reading_unique_top": all(assignments[reading]["unique_top"] for reading in READINGS),
        "three_explicit_true_labels_unique_page_best": all(
            pooled[index][index] > max(pooled[label][index] for label in range(4) if label != index) + 1e-15
            for index in EXPLICIT_INDICES
        ),
        "three_explicit_true_midranks_at_least_075": all(pooled[index][index] >= 0.75 for index in EXPLICIT_INDICES),
        "ambiguous_f89_true_midrank_at_least_050": pooled[0][0] >= 0.50,
    }
    passed = all(gates.values())
    decision = "PROVISIONAL_SAME_PLANT_REFERENCE_SIGNAL" if passed else "NO_SOURCE_NATIVE_LOCAL_REFERENCE_RECOVERY"
    result = {
        "experiment": "SNPL002_SOURCE_NATIVE_LOCAL_QUERY_TARGET",
        "status": decision,
        "frozen_files": {str(path.relative_to(ROOT)): digest for path, digest in EXPECTED.items()},
        "spec_sha256": sha(SPEC),
        "relation_order": [
            {"label": label, "target_page": page} for label, page in zip(LABEL_LOCI, TARGET_PAGES)
        ],
        "target_group_counts": {page: len(targets["metadata"][page]) for page in TARGET_PAGES},
        "matrices": matrices,
        "matrix_sha256": hashlib.sha256(
            b"".join(float(value).hex().encode() + b"\n" for row in pooled for value in row)
        ).hexdigest(),
        "assignments": assignments,
        "gates": gates,
        "passes": passed,
        "details": details,
        "decision": decision,
        "target_rows_accessed": True,
        "morphology_or_plant_name_join_performed": False,
        "ocr_or_automated_vision_used": False,
        "claim_ceiling": (
            "If passed, the frozen result is evidence only for anonymous manuscript-internal "
            "same-plant reference signal under four public relations, with f89v2.6 ownership "
            "ambiguity retained. If failed, it closes only local four/five-member source-STA "
            "reuse for this panel. Neither outcome supplies a plant name, English word, sound, "
            "language, cipher, plaintext, or translation."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    OUT_MD.write_text(
        "# SNPL002 source-native local-query target\n\n"
        f"Decision: **{decision}**.\n\n"
        f"Pooled exact assignment p = {assignments['POOLED']['p']:.6f}; margin over the best "
        f"wrong assignment = {assignments['POOLED']['margin']:.6f}. Gates: "
        + ", ".join(f"{name}={value}" for name, value in gates.items()) + ".\n\n"
        "The source and claim ceiling permit only anonymous same-plant reference signal on a "
        "full pass. No plant name, English word, sound, language, cipher, plaintext, or "
        "translation follows.\n"
    )


if __name__ == "__main__":
    main()
