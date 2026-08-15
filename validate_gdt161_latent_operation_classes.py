#!/usr/bin/env python3
"""Independent artifact and arithmetic validation for GDT161."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parent
DESIGN = ROOT / "gdt161_latent_class_design.json"
RESULT = ROOT / "gdt161_result.json"
REPORT = ROOT / "GDT161_LATENT_OPERATION_CLASS_REPORT.md"
OUT = ROOT / "gdt161_validation.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def rows(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def close(left: float, right: float, tolerance: float = 1e-10) -> bool:
    return math.isclose(left, right, rel_tol=tolerance, abs_tol=tolerance)


def main() -> None:
    design = json.loads(DESIGN.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    checks: list[tuple[str, bool]] = []

    def check(name: str, value: bool) -> None:
        checks.append((name, bool(value)))

    check("design_schema", design["schema"] == "GDT161_LATENT_OPERATION_CLASS_DESIGN_V1")
    check("result_schema", result["schema"] == "GDT161_LATENT_OPERATION_CLASS_RESULT_V1")
    for name, expected in design["inputs"].items():
        check("design_input_hash_" + name, sha(ROOT / name) == expected)
    for name, expected in result["inputs"].items():
        check("result_input_hash_" + name, sha(ROOT / name) == expected)
    for name, expected in result["outputs"].items():
        check("result_output_hash_" + name, sha(ROOT / name) == expected)
    content = dict(result)
    claimed = content.pop("result_content_sha256")
    check("result_content_hash", canonical_sha(content) == claimed)
    check("runner_hash", sha(ROOT / "run_gdt161_latent_operation_classes.py") == result["implementation"]["runner"])
    check("all_f84r_flags_false", all(value is False for value in result["f84r"].values()))

    graph = rows("gdt161_fold_graphs.tsv")
    score = rows("gdt161_prediction_scores.tsv")
    classes = rows("gdt161_operation_classes.tsv")
    stability = rows("gdt161_class_stability.tsv")
    summary = rows("gdt161_comparator_summary.tsv")
    top20 = rows("gdt161_top20_concentration_null.tsv")
    counters = rows("gdt161_counterexamples.tsv")
    check("six_corpora_graphs", set(row["corpus_id"] for row in graph) == {design["target"], *design["comparators"]})

    with gzip.open(ROOT / "gdt003_structural_fingerprint_corpora.json.gz", "rt", encoding="utf-8") as handle:
        old_records = json.load(handle)["records"]
    with gzip.open(ROOT / "gdt159_diplomatic_corpora.json.gz", "rt", encoding="utf-8") as handle:
        new_records = json.load(handle)["records"]
    expected_folds: dict[str, set[str]] = defaultdict(set)
    for row in old_records + new_records:
        if row["corpus_id"] in {design["target"], *design["comparators"]}:
            expected_folds[str(row["corpus_id"])].add(str(row["fold_id"]))
    check("graph_fold_inventory", all(
        {row["held_fold"] for row in graph if row["corpus_id"] == corpus} == folds
        for corpus, folds in expected_folds.items()
    ))

    g160 = {(row["corpus_id"], row["held_fold"]): row for row in rows("gdt160_fold_decomposition.tsv")}
    target_graphs = [row for row in graph if row["corpus_id"] == design["target"] and row["status"] == "SCORED"]
    check("target_12_graphs", len(target_graphs) == 12)
    check("target_graph_counts_match_gdt160", all(
        int(row["left_operations"]) == int(g160[(row["corpus_id"], row["held_fold"])]["left_operations"])
        and int(row["right_operations"]) == int(g160[(row["corpus_id"], row["held_fold"])]["right_operations"])
        and int(row["pair_cells"]) == int(g160[(row["corpus_id"], row["held_fold"])]["left_right_denominator"])
        and int(row["compatible_cells"]) == int(g160[(row["corpus_id"], row["held_fold"])]["graph_eligible_LR"])
        for row in target_graphs
    ))
    check("target_pair_total", sum(int(row["pair_cells"]) for row in target_graphs) == 496460)
    check("target_positive_total", sum(int(row["compatible_cells"]) for row in target_graphs) == 44965)
    check("capacity_status", sum(row["status"] == "INSUFFICIENT_CLASS_CAPACITY" for row in graph) == 6)

    check("opaque_class_ids", all(re.fullmatch(r"[LR][0-9a-f]{16}", row["opaque_operation_id"]) for row in classes))
    check("no_literal_operations_exported", all(
        all(marker not in row["opaque_operation_id"] for marker in (":", ">", "PREFIX", "SUFFIX")) for row in classes
    ))
    grouped_classes: dict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in classes:
        grouped_classes[(row["corpus_id"], row["held_fold"], row["side"], row["class_id"])].append(row)
    check("class_size_exact", all(len(group) == int(group[0]["class_size"]) for group in grouped_classes.values()))
    graph_lookup = {(row["corpus_id"], row["held_fold"]): row for row in graph if row["status"] == "SCORED"}
    check("operation_class_totals", all(
        sum(1 for item in classes if item["corpus_id"] == corpus and item["held_fold"] == fold and item["side"] == side)
        == int(row["left_operations" if side == "LEFT" else "right_operations"])
        for (corpus, fold), row in graph_lookup.items() for side in ("LEFT", "RIGHT")
    ))
    check("selected_k_class_count", all(
        len({item["class_id"] for item in classes if item["corpus_id"] == corpus and item["held_fold"] == fold and item["side"] == side})
        == int(next(item["selected_k"] for item in classes if item["corpus_id"] == corpus and item["held_fold"] == fold and item["side"] == side))
        for corpus, fold in graph_lookup for side in ("LEFT", "RIGHT")
    ))

    class_maps: dict[tuple[str, str, str], dict[str, str]] = defaultdict(dict)
    for row in classes:
        class_maps[(row["corpus_id"], row["side"], row["held_fold"])][row["opaque_operation_id"]] = row["class_id"]
    stability_lookup = {(row["corpus_id"], row["side"], row["fold_a"], row["fold_b"]): row for row in stability}
    stability_ok = True
    for (corpus, side, first), first_map in class_maps.items():
        for (corpus2, side2, second), second_map in class_maps.items():
            if corpus2 != corpus or side2 != side or second <= first:
                continue
            common = sorted(set(first_map) & set(second_map))
            inter = union = 0
            for i, left in enumerate(common):
                for right in common[i + 1:]:
                    a = first_map[left] == first_map[right]
                    b = second_map[left] == second_map[right]
                    inter += int(a and b); union += int(a or b)
            value = inter / union if union else 1.0
            stored = stability_lookup[(corpus, side, first, second)]
            stability_ok &= int(stored["common_operations"]) == len(common) and close(float(stored["coassignment_jaccard"]), value)
    check("stability_reconstructed", stability_ok)

    expected_models = {
        "MASKED_PAIR_CELL": {"GLOBAL", "HOST_PROFILE_LOGIT", "DEGREE_LOGIT", "HOST_BLOCK", "COMPAT_BLOCK"},
        "BOTH_OPERATIONS_UNSEEN": {"GLOBAL", "HOST_PROFILE_LOGIT", "HOST_BLOCK"},
    }
    check("score_model_sets", all(
        {row["model"] for row in score if row["corpus_id"] == corpus and row["held_fold"] == fold and row["evaluation"] == evaluation}
        == models
        for (corpus, fold) in graph_lookup for evaluation, models in expected_models.items()
    ))
    check("score_ranges", all(
        int(row["cells"]) > 0 and 0 <= int(row["positives"]) <= int(row["cells"])
        and 0 <= float(row["average_precision"]) <= 1 and float(row["log_loss_bits_per_cell"]) >= 0
        and 0 <= float(row["brier"]) <= 1 and 0 <= float(row["top_prevalence_matched_precision"]) <= 1
        for row in score
    ))

    summary_lookup = {(row["corpus_id"], row["evaluation"], row["model"]): row for row in summary}
    summary_ok = True
    for key, stored in summary_lookup.items():
        subset = [row for row in score if (row["corpus_id"], row["evaluation"], row["model"]) == key]
        total = sum(int(row["cells"]) for row in subset)
        summary_ok &= int(stored["cells"]) == total and int(stored["positives"]) == sum(int(row["positives"]) for row in subset)
        summary_ok &= close(float(stored["mean_average_precision"]), statistics.fmean(float(row["average_precision"]) for row in subset))
        for source, target in (("log_loss_bits_per_cell", "weighted_log_loss_bits_per_cell"),
                               ("brier", "weighted_brier"),
                               ("top_prevalence_matched_precision", "weighted_top_prevalence_precision")):
            value = sum(int(row["cells"]) * float(row[source]) for row in subset) / total
            summary_ok &= close(float(stored[target]), value)
    check("summary_reconstructed", summary_ok)

    node = summary_lookup[(design["target"], "BOTH_OPERATIONS_UNSEEN", "HOST_BLOCK")]
    node_base = summary_lookup[(design["target"], "BOTH_OPERATIONS_UNSEEN", "HOST_PROFILE_LOGIT")]
    cell = summary_lookup[(design["target"], "MASKED_PAIR_CELL", "COMPAT_BLOCK")]
    cell_base = summary_lookup[(design["target"], "MASKED_PAIR_CELL", "HOST_PROFILE_LOGIT")]
    effects = result["target_effects"]
    check("node_gain", close(effects["both_unseen_gain_bits_per_cell"], float(node_base["weighted_log_loss_bits_per_cell"]) - float(node["weighted_log_loss_bits_per_cell"])))
    check("node_ap_gain", close(effects["both_unseen_ap_gain"], float(node["mean_average_precision"]) - float(node_base["mean_average_precision"])))
    check("cell_gain", close(effects["masked_cell_gain_bits_per_cell"], float(cell_base["weighted_log_loss_bits_per_cell"]) - float(cell["weighted_log_loss_bits_per_cell"])))
    check("zero_positive_folds", int(effects["positive_graph_folds"]) == 0)
    check("median_k_left_grid_ceiling", close(float(effects["median_k_left"]), 32.0))
    check("median_k_right_one", close(float(effects["median_k_right"]), 1.0))
    check("full_graph_grid_ceiling", int(result["target_full_graphs_at_any_k_grid_ceiling"]) == 12)
    check("status", result["status"] == "LATENT_CLASSES_NOT_ABOVE_HOST_DEGREE_BASELINES")

    by_scope: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in top20:
        by_scope[row["scope"]].append(row)
    check("two_top20_scopes", set(by_scope) == {"FULL_PAIR_UNIVERSE", "FROZEN_GDT160_ATLAS_SCOPE"})
    check("top20_1024_each", all(len(value) == 1024 for value in by_scope.values()))
    g160_worlds = [int(row["null_eligible_pairs"]) for row in rows("gdt160_null_worlds.tsv")
                   if row["corpus_id"] == design["target"] and row["null"] == design["top20_null"]]
    full = sorted(by_scope["FULL_PAIR_UNIVERSE"], key=lambda row: int(row["world"]))
    check("null_world_totals_reproduce_gdt160", [int(row["null_eligible_pair_folds"]) for row in full] == g160_worlds)
    top_ok = True
    for scope, values in by_scope.items():
        values = sorted(values, key=lambda row: int(row["world"]))
        fractions = [float(row["top20_positive_excess_fraction"]) for row in values]
        stored = result["top20_concentration"][scope]
        observed = float(stored["observed_top20_fraction"])
        top_ok &= close(float(stored["null_mean"]), statistics.fmean(fractions))
        top_ok &= close(float(stored["null_ci025"]), float(np.quantile(fractions, 0.025)))
        top_ok &= close(float(stored["null_ci975"]), float(np.quantile(fractions, 0.975)))
        top_ok &= close(float(stored["p_at_most_observed_concentration"]), (1 + sum(value <= observed for value in fractions)) / 1025)
        top_ok &= close(float(stored["p_at_least_observed_concentration"]), (1 + sum(value >= observed for value in fractions)) / 1025)
    check("top20_summary_reconstructed", top_ok)
    published_fraction = json.loads((ROOT / "gdt160_result.json").read_text(encoding="utf-8"))["pair_excess"]["top20_fraction_positive_excess"]
    check("published_atlas_fraction_reproduced", close(result["top20_concentration"]["FROZEN_GDT160_ATLAS_SCOPE"]["observed_top20_fraction"], published_fraction, 1e-12))
    check("top20_unusually_diffuse", result["top20_concentration"]["FULL_PAIR_UNIVERSE"]["p_at_most_observed_concentration"] == 1 / 1025)

    report = REPORT.read_text(encoding="utf-8")
    check("report_status", result["status"] in report)
    check("report_no_semantic_gloss", "semantic gloss" not in report.lower())
    check("report_f84_seal", "f84r was\nnot opened" in report)
    check("counterexamples_seven", len(counters) == 7)
    check("source_freeze", result["source_freeze_commit"] == "c5bddab")
    check("source_freeze_correction", result["source_freeze_correction_commit"] == "619f800")

    failed = [name for name, ok in checks if not ok]
    validation = {
        "schema": "GDT161_LATENT_OPERATION_CLASS_VALIDATION_V1",
        "status": "PASS" if not failed else "FAIL",
        "checks_passed": sum(ok for _, ok in checks), "checks_total": len(checks),
        "failed": failed, "checks": [{"check": name, "pass": ok} for name, ok in checks],
        "result_sha256": sha(RESULT), "result_content_sha256": result["result_content_sha256"],
        "validator_sha256": sha(Path(__file__)),
        "scope": "Independent artifact, graph-count, class-accounting, score-summary, stability, GDT160-world, concentration-null, decision, hash, and seal reconstruction; model coefficients are not independently refit.",
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if failed:
        raise SystemExit("FAIL " + ",".join(failed))
    print(f"PASS {validation['checks_passed']}/{validation['checks_total']}")


if __name__ == "__main__":
    main()
