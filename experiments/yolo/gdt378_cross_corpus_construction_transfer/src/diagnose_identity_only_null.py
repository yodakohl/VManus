#!/usr/bin/env python3
"""Post-hoc non-promoting diagnosis of GDT378's slot-degenerate global null."""
from __future__ import annotations

import csv
import gzip
import hashlib
import io
import importlib.util
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt378_cross_corpus_construction_transfer"
ART = BASE / "artifacts"
SOURCE = ROOT / "gdt327_joint_tuple_interlinear.tsv"
EVENTS = ART / "gdt378_voynich_event_scores.tsv.gz"
CANDIDATES = ART / "gdt378_voynich_candidate_atlas.tsv"
PRIMARY_NULL = ART / "gdt378_voynich_null.tsv.gz"
PRIMARY_RESULT = ART / "gdt378_voynich_target_result.json"
RUNNER = BASE / "src/run_voynich_target.py"
RESOLUTIONS = ["ATOMIC_JOINT_TUPLE", "SOURCE_GROUP", "FIELD_CONSTRUCTION_SPAN"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, rows):
    if path.suffix == ".gz":
        raw = path.open("wb")
        gz = gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0)
        handle = io.TextIOWrapper(gz, encoding="utf-8", newline="")
    else:
        handle = path.open("w", encoding="utf-8", newline="")
    with handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_runner():
    spec = importlib.util.spec_from_file_location("gdt378_target_frozen", RUNNER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def content(obj):
    clone = dict(obj)
    clone.pop("content_hash", None)
    return hashlib.sha256(json.dumps(clone, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main():
    primary = json.loads(PRIMARY_RESULT.read_text())
    assert primary["promoted_candidates"] == 0 and primary["null_worlds"] == 4096
    primary_null = read(PRIMARY_NULL)
    primary_values = [float(row["max_abs_residual_statistic"]) for row in primary_null]
    assert len(set(primary_values)) == 1
    source = read(SOURCE)
    assert len(source) == 8448 and not any(any(row[key].lower().startswith("f84") for key in ("page", "physical_folio", "locus")) for row in source)
    events = read(EVENTS)
    candidates = read(CANDIDATES)
    signatures = sorted({row["signature_id"] for row in events})
    event_lookup = {(row["signature_id"], row["base_resolution"], row["unit_id"]): row for row in events}
    runner = load_runner()
    elements = {resolution: runner.build_elements(source, resolution) for resolution in RESOLUTIONS}
    powered = {
        (row["signature_id"], row["resolution"], row["candidate_id"]): row
        for row in candidates if row["powered"] == "1" and row["resolution"] in RESOLUTIONS
    }
    panels = {}
    for resolution in RESOLUTIONS:
        values = elements[resolution]
        candidate_ids = [row["candidate_id"] for row in values]
        unique = sorted(set(candidate_ids))
        lookup = {candidate: i for i, candidate in enumerate(unique)}
        codes = np.asarray([lookup[candidate] for candidate in candidate_ids], int)
        counts = np.bincount(codes)
        for signature in signatures:
            rows = [event_lookup[(signature, resolution, row["unit_id"])] for row in values]
            residual = np.asarray([float(row["placement_residual"]) for row in rows])
            strata = defaultdict(list)
            for i, row in enumerate(rows):
                strata[row["null_stratum_id"]].append(i)
            mobile = [np.asarray(ids, int) for ids in strata.values() if len(ids) > 1]
            eligible = np.asarray([i for i, candidate in enumerate(unique) if (signature, resolution, candidate) in powered], int)
            panels[(signature, resolution)] = (residual, mobile, codes, counts, unique, eligible)

    maxima = []
    for world in range(4096):
        world_max = 0.0
        permutations = {}
        for resolution in RESOLUTIONS:
            # Strata do not differ by signature at a fixed resolution.
            example = panels[(signatures[0], resolution)]
            rng = np.random.default_rng(378500000 + world * 7 + RESOLUTIONS.index(resolution))
            permutation = np.arange(len(example[0]))
            for ids in example[1]:
                permutation[ids] = rng.permutation(ids)
            permutations[resolution] = permutation
        for signature in signatures:
            for resolution in RESOLUTIONS:
                residual, _, codes, counts, _, eligible = panels[(signature, resolution)]
                if not len(eligible):
                    continue
                values = residual[permutations[resolution]]
                means = np.bincount(codes, weights=values, minlength=len(counts)) / counts
                second = np.bincount(codes, weights=values * values, minlength=len(counts)) / counts
                sd = np.sqrt(np.maximum(second - means * means, 1e-18))
                stats = np.abs(means[eligible]) / (sd[eligible] / np.sqrt(counts[eligible]))
                world_max = max(world_max, float(np.max(stats)))
        maxima.append(world_max)

    output = []
    for (signature, resolution, candidate), row in powered.items():
        observed = float(row["residual_statistic_abs"])
        p = (1 + sum(value >= observed for value in maxima)) / 4097
        output.append({
            "signature_id": signature, "resolution": resolution,
            "candidate_family": row["candidate_family"], "candidate_id": candidate,
            "events": row["events"], "physical_folios": row["physical_folios"], "registers": row["registers"],
            "mean_placement_residual": row["mean_placement_residual"],
            "held_sse_gain_over_placement": row["held_sse_gain_over_placement"],
            "positive_gain_folio_fraction": row["positive_gain_folio_fraction"],
            "residual_statistic_abs": row["residual_statistic_abs"],
            "identity_only_max_family_p": f"{p:.12f}",
            "status": "POSTHOC_DIAGNOSTIC_NOT_PROMOTION", "semantic_state": "UNASSIGNED",
        })
    output.sort(key=lambda row: (float(row["identity_only_max_family_p"]), -float(row["mean_placement_residual"]), row["signature_id"], row["resolution"], row["candidate_id"]))
    null_rows = [{"world": i, "identity_only_max_abs_statistic": f"{value:.12f}"} for i, value in enumerate(maxima)]
    out_path = ART / "gdt378_identity_only_diagnostic.tsv"
    null_path = ART / "gdt378_identity_only_null.tsv.gz"
    write(out_path, output)
    write(null_path, null_rows)
    result = {
        "schema": "GDT378_IDENTITY_ONLY_DIAGNOSTIC_V1",
        "status": "POSTHOC_NONPROMOTING_NULL_DIAGNOSIS",
        "reason": "The frozen primary maxT is invariant because slot labels are fixed by the exact position/closure strata; this diagnostic excludes only the deterministic slot panels and cannot promote a candidate.",
        "primary_null_unique_maxima": len(set(primary_values)),
        "identity_only_null_unique_maxima": len({row["identity_only_max_abs_statistic"] for row in null_rows}),
        "powered_identity_candidates": len(output),
        "minimum_identity_only_p": min(float(row["identity_only_max_family_p"]) for row in output),
        "primary_decision_unchanged": True,
        "semantic_assignments": 0,
        "f84": {"opened": False, "parsed": False, "retained": False, "scored": False},
        "inputs": {str(path.relative_to(ROOT)): sha(path) for path in [SOURCE, EVENTS, CANDIDATES, PRIMARY_NULL, PRIMARY_RESULT]},
        "outputs": {str(path.relative_to(ROOT)): sha(path) for path in [out_path, null_path]},
        "implementation": {str(Path(__file__).relative_to(ROOT)): sha(Path(__file__))},
        "claim_ceiling": "POSTHOC_IDENTITY_ONLY_NULL_DIAGNOSTIC_NO_PROMOTION_OR_FUNCTION",
    }
    result["content_hash"] = content(result)
    (ART / "gdt378_identity_only_diagnostic_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "candidates": len(output), "min_p": result["minimum_identity_only_p"], "null_unique": result["identity_only_null_unique_maxima"]}))


if __name__ == "__main__":
    main()
