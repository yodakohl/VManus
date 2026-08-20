#!/usr/bin/env python3
"""Independent retained-artifact validator for GDT394.

This validator does not import the scorer or claim to refit the projections.
It independently rebuilds source joins/counts and all published fold, null,
gate, hash, and decision arithmetic.
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt394_latent_role_bottleneck_transfer_audit"
ART = BASE / "artifacts"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def readgz(path: Path) -> list[dict[str, str]]:
    with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    result_path = ART / "gdt394_result.json"
    result = json.loads(result_path.read_text(encoding="utf-8"))
    scores = read(ART / "gdt394_bottleneck_scores.tsv")
    folds = read(ART / "gdt394_fold_scores.tsv")
    nulls = read(ART / "gdt394_null_worlds.tsv")
    summaries = read(ART / "gdt394_null_summary.tsv")
    predictions = readgz(ART / "gdt394_predictions.tsv.gz")
    checks: list[tuple[str, bool, str]] = []

    def check(name: str, condition: bool, detail: object = "") -> None:
        checks.append((name, bool(condition), str(detail)))

    corema = [
        row
        for row in readgz(
            ROOT / "experiments/yolo/gdt385_corema_parent_link_consequence/artifacts/gdt385_predictions.tsv.gz"
        )
        if row["route_id"] == "CMP_PARENT_02"
    ]
    pceec = readgz(
        ROOT / "experiments/yolo/gdt387_cross_domain_parent_link_calibration/artifacts/gdt387_hidden_governor_oracle.tsv.gz"
    )
    check("source_corema_n", len(corema) == 26169, len(corema))
    check("source_pceec_n", len(pceec) == 26493, len(pceec))
    check("source_corema_folds", len({row["held_collection"] for row in corema}) == 6)
    check("source_pceec_folds", len({row["source_file"] for row in pceec}) == 84)
    check("score_rows", len(scores) == 16)
    check("fold_rows", len(folds) == 8 * (6 + 84), len(folds))
    check("null_rows", len(nulls) == 2 * 512, len(nulls))
    check("summary_rows", len(summaries) == 16)
    check("prediction_rows", len(predictions) == 26169 + 26493, len(predictions))
    check("two_domains", {row["domain"] for row in scores} == {"COREMA", "PCEEC2"})
    check("eight_models_each", all(Counter(row["domain"] for row in scores)[d] == 8 for d in ("COREMA", "PCEEC2")))

    score_map = {(row["domain"], row["model"]): row for row in scores}
    summary_map = {(row["domain"], row["model"]): row for row in summaries}
    fold_groups: dict[tuple[str, str], list[dict[str, str]]] = {}
    for row in folds:
        fold_groups.setdefault((row["domain"], row["model"]), []).append(row)
    for key, score in score_map.items():
        subset = fold_groups[key]
        gain = sum(float(row["gain_bits"]) for row in subset)
        check(f"fold_gain_{key}", abs(gain - float(score["gain_bits"])) < 1e-7, gain)
        positive = sum(float(row["gain_bits"]) > 0 for row in subset)
        check(f"fold_direction_{key}", positive == int(score["positive_folds"]), positive)
        summary = summary_map[key]
        check(
            f"null_excess_{key}",
            abs(
                float(summary["observed_gain_bits"])
                - float(summary["null_mean_gain_bits"])
                - float(summary["null_centered_excess_bits"])
            )
            < 1e-7,
        )

    reconstructed_domains = {}
    for domain in ("COREMA", "PCEEC2"):
        role = score_map[(domain, "ROLE_BOTTLENECK")]
        controls = [row for (d, m), row in score_map.items() if d == domain and m != "ROLE_BOTTLENECK"]
        domain_null = [row for row in nulls if row["domain"] == domain]
        pvalue = (1 + sum(float(row["max8_gain_bits"]) >= float(role["gain_bits"]) for row in domain_null)) / 513
        published = result["domain_results"][domain]
        check(f"pvalue_{domain}", abs(pvalue - float(published["max8_p"])) < 1e-12, pvalue)
        best_gain = max(float(row["gain_bits"]) for row in controls)
        best_excess = max(float(row["null_centered_excess_bits"]) for row in controls)
        best_mrr = max(float(row["model_mrr"]) for row in controls)
        best_top1 = max(int(row["model_top1"]) for row in controls)
        n = int(role["n"])
        gates = {
            "positive_gain": float(role["gain_bits"]) > 0,
            "beats_every_control_gain": float(role["gain_bits"]) > best_gain,
            "majority_positive_folds": int(role["positive_folds"]) >= (4 if domain == "COREMA" else 43),
            "positive_null_excess": float(role["null_centered_excess_bits"]) > 0,
            "beats_every_control_null_excess": float(role["null_centered_excess_bits"]) > best_excess,
            "max8_p": pvalue <= 0.05,
            "mrr_margin": float(role["model_mrr"]) >= best_mrr + 0.001,
            "top1_margin": int(role["model_top1"]) >= best_top1 + max(3, math.ceil(0.001 * n)),
            "not_one_fold": float(role["gain_without_largest_fold"]) > 0,
            "not_one_exact_form": float(role["gain_without_most_common_exact_form"]) > 0,
        }
        check(f"gates_{domain}", gates == published["gates"], gates)
        reconstructed_domains[domain] = all(gates.values())
    overall = all(reconstructed_domains.values())
    expected_status = (
        "ANONYMOUS_ROLE_BOTTLENECK_PORTABLE_ABOVE_MATCHED_CONTROLS"
        if overall
        else "LATENT_ROLE_COMPRESSION_NOT_DISTINCT_FROM_MATCHED_SOURCE_BOTTLENECKS"
    )
    check("decision", result["status"] == expected_status and result["overall_pass"] == overall)
    check("no_voynich", result["voynich_rows_read"] == 0 and not result["voynich_stage_authorized"])
    check("f84", not any(result["f84"].values()))
    content = dict(result)
    expected_hash = content.pop("content_sha256")
    check(
        "content_hash",
        hashlib.sha256(json.dumps(content, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == expected_hash,
    )
    for family in ("inputs", "outputs", "implementation"):
        check(
            "hashes_" + family,
            all((ROOT / path).is_file() and sha(ROOT / path) == digest for path, digest in result[family].items()),
        )
    validation = {
        "schema": "GDT394_VALIDATION_V1",
        "status": "PASS" if all(value for _, value, _ in checks) else "FAIL",
        "scope": "RETAINED_FOLD_NULL_AND_PRIMARY_ARITHMETIC_NOT_PROJECTION_REFIT",
        "checks_passed": sum(value for _, value, _ in checks),
        "checks_total": len(checks),
        "checks": {name: {"pass": value, "detail": detail} for name, value, detail in checks},
        "result_sha256": sha(result_path),
    }
    (ART / "gdt394_validation.json").write_text(
        json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({"status": validation["status"], "checks": len(checks)}, sort_keys=True))
    return 0 if validation["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
