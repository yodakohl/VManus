#!/usr/bin/env python3
"""Independent arithmetic and integrity validation for GDT160 outputs."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "gdt160_result.json"
DESIGN = ROOT / "gdt160_null_design.json"
FOLDS = ROOT / "gdt160_fold_decomposition.tsv"
SUMMARY = ROOT / "gdt160_null_summary.tsv"
WORLDS = ROOT / "gdt160_null_worlds.tsv"
PAIRS = ROOT / "gdt160_pair_excess.tsv"
COUNTER = ROOT / "gdt160_counterexamples.tsv"
REPORT = ROOT / "GDT160_COMPATIBILITY_PAIRING_NULL_REPORT.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def close(left: float, right: float, tolerance: float = 1e-12) -> bool:
    return abs(left - right) <= tolerance * max(1.0, abs(left), abs(right))


def main() -> None:
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    design = json.loads(DESIGN.read_text(encoding="utf-8"))
    folds, summary, worlds, pairs = read(FOLDS), read(SUMMARY), read(WORLDS), read(PAIRS)
    checks: list[tuple[str, bool]] = []

    def check(name: str, value: bool) -> None:
        checks.append((name, bool(value)))

    check("schema", result["schema"] == "GDT160_COMPATIBILITY_PAIRING_NULL_RESULT_V1")
    check("result_content", canonical_sha({key: value for key, value in result.items() if key != "result_content_sha256"}) == result["result_content_sha256"])
    for name, expected in result["inputs"].items():
        check("input_" + name, sha(ROOT / name) == expected)
    for name, expected in result["outputs"].items():
        check("output_" + name, sha(ROOT / name) == expected)
    check("runner_hash", sha(ROOT / "run_gdt160_compatibility_pairing_null.py") == result["implementation"]["runner"])
    check("core_hash", sha(ROOT / "run_gdt003_nested_heldout.py") == result["implementation"]["gdt003_core"])
    check("fingerprint_runner_hash", sha(ROOT / "run_gdt003_structural_fingerprint_comparator.py") == result["implementation"]["gdt003_fingerprint_runner"])
    check("six_corpora", {row["corpus_id"] for row in folds} == {design["target"], *design["comparators"]})
    fold_counts = Counter(row["corpus_id"] for row in folds)
    check("fold_counts", fold_counts[design["target"]] == 12 and sorted(fold_counts[name] for name in design["comparators"]) == [6, 6, 6, 12, 12])
    check("world_rows", len(worlds) == 6 * 3 * design["worlds"])
    check("summary_rows", len(summary) == 18)

    published: dict[str, float] = {}
    for path in (ROOT / "gdt003_structural_fingerprints.tsv", ROOT / "gdt159_structural_fingerprints.tsv"):
        for row in read(path):
            published[row["corpus_id"]] = float(row["compatible_pair_density"])

    world_by: dict[tuple[str, str], list[int]] = defaultdict(list)
    for row in worlds:
        world_by[row["corpus_id"], row["null"]].append(int(row["null_eligible_pairs"]))
    summary_by = {(row["corpus_id"], row["null"]): row for row in summary}
    for corpus, null in sorted(summary_by):
        row = summary_by[corpus, null]
        corpus_folds = [item for item in folds if item["corpus_id"] == corpus]
        denominator = sum(int(item["all_pair_denominator"]) for item in corpus_folds)
        semantic = sum(int(item["semantic_eligible_all"]) for item in corpus_folds)
        graph = sum(int(item["graph_eligible_LR"]) + int(item["semantic_eligible_LL"]) + int(item["semantic_eligible_RR"]) for item in corpus_folds)
        values = world_by[corpus, null]
        check(f"{corpus}_{null}_world_count", len(values) == design["worlds"])
        check(f"{corpus}_{null}_denominator", int(row["all_pair_denominator"]) == denominator)
        check(f"{corpus}_{null}_semantic", int(row["semantic_eligible_pairs"]) == semantic)
        check(f"{corpus}_{null}_graph", int(row["graph_observed_eligible_pairs"]) == graph)
        check(f"{corpus}_{null}_published_density", close(semantic / denominator, published[corpus]))
        mean = statistics.fmean(values)
        sd = statistics.pstdev(values)
        check(f"{corpus}_{null}_mean", close(float(row["null_mean_eligible_pairs"]), mean))
        check(f"{corpus}_{null}_density", close(float(row["null_mean_all_pair_density"]), mean / denominator))
        check(f"{corpus}_{null}_survival", close(float(row["null_survival_fraction_of_graph_observed"]), mean / max(1, graph)))
        check(f"{corpus}_{null}_ratio", close(float(row["graph_to_null_ratio"]), graph / max(1e-12, mean)))
        if row["z_score"] != "NA":
            check(f"{corpus}_{null}_z", close(float(row["z_score"]), (graph - mean) / sd))
        check(f"{corpus}_{null}_p", close(float(row["inclusive_empirical_p"]), (1 + sum(value >= graph for value in values)) / (len(values) + 1)))
        check(f"{corpus}_{null}_quantiles", close(float(row["null_ci025_density"]), float(np.quantile(values, .025, method="linear")) / denominator) and close(float(row["null_ci975_density"]), float(np.quantile(values, .975, method="linear")) / denominator))

    target_folds = [row for row in folds if row["corpus_id"] == design["target"]]
    decomposition = {
        "LEFT_LEFT": sum(int(row["semantic_eligible_LL"]) for row in target_folds),
        "LEFT_RIGHT": sum(int(row["semantic_eligible_LR"]) for row in target_folds),
        "RIGHT_RIGHT": sum(int(row["semantic_eligible_RR"]) for row in target_folds),
    }
    check("exact_decomposition", decomposition == result["exact_decomposition"])
    check("all_target_pairs_are_lr", decomposition["LEFT_RIGHT"] > 0 and decomposition["LEFT_LEFT"] == decomposition["RIGHT_RIGHT"] == 0)
    check("target_published_exact", close(sum(decomposition.values()) / sum(int(row["all_pair_denominator"]) for row in target_folds), 0.04529064872820362))
    check("pair_order", [int(row["excess_rank"]) for row in pairs] == list(range(1, len(pairs) + 1)))
    check("pair_sorted", all(float(pairs[index]["graph_excess_eligible_folds"]) >= float(pairs[index + 1]["graph_excess_eligible_folds"]) for index in range(len(pairs) - 1)))
    check("pair_support", all(int(row["selected_folds"]) >= int(row["semantic_eligible_folds"]) and int(row["selected_folds"]) >= int(row["graph_eligible_folds"]) for row in pairs))
    primary = summary_by[design["target"], "RIGHT_LABEL_SWITCH_LENGTH_EXACT"]
    reverse = summary_by[design["target"], "LEFT_LABEL_SWITCH_LENGTH_EXACT"]
    expected_gates = {
        "primary_mobility_at_least_25pct": float(primary["mean_switchable_fraction"]) >= .25,
        "positive_at_least_9_of_12": int(primary["positive_fold_directions"]) >= 9,
        "primary_p_at_most_point01": float(primary["inclusive_empirical_p"]) <= .01,
        "primary_survival_below_75pct": float(primary["null_survival_fraction_of_graph_observed"]) < .75,
        "reverse_direction_agrees": float(reverse["graph_excess_all_pair_density"]) > 0 and float(reverse["inclusive_empirical_p"]) <= .01,
    }
    check("gates", result["gates"] == expected_gates)
    external_excess = max(
        float(row["graph_excess_all_pair_density"])
        for (corpus, null), row in summary_by.items()
        if corpus != design["target"] and null == "RIGHT_LABEL_SWITCH_LENGTH_EXACT"
    )
    check("cross_corpus_excess", close(result["cross_corpus_excess"]["largest_external_excess_density"], external_excess) and close(result["cross_corpus_excess"]["target_to_largest_external_excess_ratio"], float(primary["graph_excess_all_pair_density"]) / external_excess))
    if float(primary["mean_switchable_fraction"]) < .25:
        expected_status = "INSUFFICIENT_NULL_MOBILITY"
    elif all(expected_gates.values()):
        expected_status = "SPECIFIC_LEFT_RIGHT_PAIRING_EXCESS_SUPPORTED"
    elif float(primary["graph_excess_all_pair_density"]) > 0:
        expected_status = "PAIRING_EXCESS_PRESENT_BUT_DIFFUSE_OR_UNSTABLE"
    else:
        expected_status = "PAIRING_EXCESS_NOT_ABOVE_DEGREE_NULL"
    check("status", result["status"] == expected_status)
    check("f84_flags", all(value is False for value in result["f84r"].values()))
    provenance = json.loads((ROOT / "gdt003_structural_fingerprint_source_provenance.json").read_text(encoding="utf-8"))
    target_source = next(row for row in provenance["sources"] if row["corpus_id"] == design["target"])
    check("source_excludes_f84r", target_source["f84r_retained_or_sampled"] is False)
    check("counterexample_seal", any(row["claim"] == "F84R_USED" for row in read(COUNTER)))
    check("report_claim_ceiling", "establishes no morpheme" in REPORT.read_text(encoding="utf-8"))

    failed = [name for name, ok in checks if not ok]
    output = {
        "schema": "GDT160_COMPATIBILITY_PAIRING_NULL_VALIDATION_V1",
        "status": "PASS_INDEPENDENT_AGGREGATE_NULL_AND_DECISION_RECONSTRUCTION" if not failed else "FAIL",
        "checks_passed": sum(ok for _, ok in checks),
        "checks_total": len(checks),
        "failed": failed,
        "checks": [{"check": name, "pass": ok} for name, ok in checks],
        "result_sha256": sha(RESULT),
    }
    (ROOT / "gdt160_validation.json").write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if failed:
        raise SystemExit("FAIL " + ",".join(failed))
    print(f"PASS {output['checks_passed']}/{output['checks_total']}")


if __name__ == "__main__":
    main()
