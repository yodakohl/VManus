#!/usr/bin/env python3
"""Integrity and independent headline validation for GDT059."""
from __future__ import annotations
import csv, hashlib, json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "gdt059_result.json"
INVENTORY = ROOT / "gdt059_hpr2_external_inventory.tsv"
SCORES = ROOT / "gdt059_representation_scores.tsv"
SUMMARY = ROOT / "gdt059_representation_summary.tsv"
RENDERER = ROOT / "gdt059_renderer_preservation.tsv"
VARIANTS = ROOT / "gdt059_variant_log.tsv"
LEDGER = ROOT / "GDT002_YOLO_LEDGER.tsv"
VALIDATION = ROOT / "gdt059_validation.json"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value):
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True,
                     separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def close(left, right, tol=5e-9):
    return abs(float(left) - float(right)) <= tol


def main():
    result = json.loads(RESULT.read_text())
    inventory = read(INVENTORY)
    scores = read(SCORES)
    summary = read(SUMMARY)
    renderer = read(RENDERER)
    variants = read(VARIANTS)
    checks = {}

    checks["panel_counts"] = result["panels"] == {
        "exact_local_all": 560,
        "exact_local_unhedged": 316,
        "page_catalogue": 194,
    }
    checks["inventory_count"] = len(inventory) == 671
    checks["score_grid"] = len(scores) == 210 and Counter(
        row["panel"] for row in scores
    ) == Counter({"EXACT_LOCAL_ALL": 80,
                  "EXACT_LOCAL_UNHEDGED": 80,
                  "PAGE_CATALOGUE": 50})
    checks["summary_grid"] = len(summary) == 30
    checks["renderer_grid"] = len(renderer) == 24
    checks["f84_excluded"] = (
        not any(row["locus"].startswith("f84r") for row in inventory)
        and not any(result["f84r"].values())
    )

    by = {(row["panel"], row["representation"]): row for row in summary}
    checks["local_headline"] = (
        close(by["EXACT_LOCAL_ALL", "RAW_CHAR3"]["descriptive_total_gain_bits"],
              111.32120154593908)
        and close(by["EXACT_LOCAL_ALL", "PAGE_HOST_CHAR3"]["descriptive_total_gain_bits"],
                  109.06312575245175)
        and float(by["EXACT_LOCAL_ALL", "RAW_CHAR3"]["descriptive_total_gain_bits"])
        > float(by["EXACT_LOCAL_ALL", "PAGE_HOST_CHAR3"]["descriptive_total_gain_bits"])
    )
    page_scores = [row for row in scores if row["panel"] == "PAGE_CATALOGUE"
                   and row["external_axis"].startswith("SOURCE_")]
    page_content = Counter()
    for row in page_scores:
        page_content[row["representation"]] += float(row["gain_vs_nuisance_bits"])
    checks["page_content_reconstruction"] = all(
        close(page_content[representation], values["descriptive_total_gain_bits"])
        for representation, values in result["page_content_summary"].items()
    )
    checks["negative_control_failure"] = (
        page_content["B3_ONLY"] > page_content["PAGE_HOST_CHAR3"]
        and page_content["RIGHT_FAMILY_ONLY"] > page_content["PAGE_HOST_CHAR3"]
        and close(page_content["B3_ONLY"], 22.908529081605685)
    )
    checks["o_ot_zero_capacity"] = (
        result["o_ot_cross_folio_capacity"] == 0
        and all(int(row["eligible_predictions"]) == 0
                for row in renderer if row["renderer_contrast"] == "O_VS_OT")
    )
    checks["variant_history"] = (
        {row["variant_id"]: row["status"] for row in variants}.get("V00")
        == "SUPERSEDED_LENGTH_LAYOUT_LEAKAGE"
        and {row["variant_id"]: row["status"] for row in variants}.get("V08")
        == "PRIMARY"
    )
    body = dict(result)
    claimed = body.pop("result_content_sha256")
    checks["result_content_hash"] = csha(body) == claimed
    checks["bound_hashes"] = all(
        sha(ROOT / name) == digest
        for family in ("inputs", "outputs", "documents", "implementation")
        for name, digest in result[family].items()
    )
    checks["status_and_ceiling"] = (
        result["status"] == "PAGE_HOST_SPECIFIC_EXTERNAL_INFORMATION_LOCALIZATION_NOT_SUPPORTED"
        and "does not outperform" in result["localization_decision"]
        and "No PAGE_HOST gloss" in result["claim_ceiling"]
    )
    ledger_rows = [row for row in read(LEDGER)
                   if row["checkpoint_id"] == "GDT059_CKPT001"]
    checks["ledger_exact"] = (
        len(ledger_rows) == 1
        and ledger_rows[0]["status"] == result["status"]
        and ledger_rows[0]["result_artifact"] == RESULT.name
    )

    passed = all(checks.values())
    validation = {
        "schema": "GDT059_HPR2_EXTERNAL_INFORMATION_LOCALIZATION_VALIDATION_V1",
        "status": "PASS_INTEGRITY_AND_INDEPENDENT_HEADLINE_CHECKS" if passed else "FAIL",
        "checks": checks,
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "result_sha256": sha(RESULT),
        "validator_sha256": sha(Path(__file__)),
        "scope": "Independently checks counts, score grids, headline sums, content-only negative-control failure, zero O/OT capacity, hashes, f84 exclusion, history, ledger, and claim ceiling; it does not independently rerun the nearest-neighbour scorer.",
    }
    VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": validation["status"],
                      "checks": f'{validation["checks_passed"]}/{validation["checks_total"]}'},
                     sort_keys=True))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
