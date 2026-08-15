#!/usr/bin/env python3
"""Independent integrity and arithmetic validator for GDT109."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "gdt109_result.json"
VALIDATION = ROOT / "gdt109_validation.json"
LABELS = ROOT / "experiments/semantic_assumptions/results/existing_human_label_annotations.tsv"
CROSSWALK = ROOT / "experiments/semantic_assumptions/results/existing_human_current_locus_crosswalk.tsv"
ANN = ROOT / "gdt012_annotated_core_inventory.tsv"
TARGETS = ROOT / "gdt109_target_inventory.tsv"
SCORES = ROOT / "gdt109_representation_scores.tsv"
TOKENS = ROOT / "gdt109_token_scores.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def physical_folio(page: str) -> str:
    match = re.match(r"(f\d+)", page)
    return match.group(1) if match else page


def main() -> None:
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object = "") -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    labels = {row["source_record_id"]: row for row in read(LABELS)}
    used = {row["locus"] for row in read(ANN)}
    expected = []
    for row in read(CROSSWALK):
        source = labels.get(row["source_record_id"])
        if not source or row["primary_eligible"] != "1" or row["current_locus"] in used or row["current_locus"].startswith("f84r"):
            continue
        if source["certainty"] == "UNHEDGED" and source["object_class"] == "P":
            expected.append((row["source_record_id"], row["current_locus"], row["current_page"], physical_folio(row["current_page"])))
    expected.sort()
    targets = read(TARGETS)
    actual = sorted((row["source_record_id"], row["locus"], row["page"], row["physical_folio"]) for row in targets)
    check("fixed_target_exact", actual == expected, len(actual))
    check("fixed_target_count", len(targets) == 44, len(targets))
    check("target_unique_loci", len({row["locus"] for row in targets}) == 44)
    check("target_six_folios", len({row["physical_folio"] for row in targets}) == 6)
    check("target_outside_gdt012", not ({row["locus"] for row in targets} & used))
    check("f84_absent_target", not any(row["locus"].startswith("f84r") for row in targets))
    check("surface_agreement_count", sum(int(row["all_reading_surface_agreement"]) for row in targets) == 9)
    check("family_agreement_count", sum(int(row["all_reading_family_agreement"]) for row in targets) == 33)
    check("three_readings_present", all(row["zl3b_forms"] and row["it2a_forms"] and row["rf1b_forms"] for row in targets))
    check("roles_unassigned", all(row["semantic_role"] == "UNASSIGNED" for row in targets))

    scores = read(SCORES)
    token_rows = read(TOKENS)
    check("score_grid_count", len(scores) == 2 * 4 * 8, len(scores))
    check("token_grid_count", len(token_rows) == (19 + 8) * 4 * 8, len(token_rows))
    primary = [row for row in scores if row["panel"] == "ALL_GDT095_TOKENS" and row["reading_mode"] == "AVERAGED"]
    check("primary_eight_representations", len(primary) == 8)
    check("score_arithmetic", all(abs(float(row["baseline_bits"]) - float(row["held_bits"]) - float(row["gain_bits"])) < 1e-8 for row in scores))
    check("selector_arithmetic", all(row["reading_mode"] != "AVERAGED" or abs(float(row["selector_paid_gain_bits"]) - (float(row["gain_bits"]) - 3.0)) < 1e-8 for row in scores))
    best = max(primary, key=lambda row: (float(row["gain_bits"]), row["representation"]))
    check("primary_best_raw", best["representation"] == "RAW_CHAR3", best["gain_bits"])
    check("primary_best_negative", float(best["gain_bits"]) < 0)
    page_host = next(row for row in primary if row["representation"] == "PAGE_HOST_CHAR3")
    compiler = next(row for row in primary if row["representation"] == "COMPILER_ACTIVE")
    check("page_host_negative", float(page_host["gain_bits"]) < 0, page_host["gain_bits"])
    check("compiler_negative_all_folios", float(compiler["gain_bits"]) < 0 and int(compiler["positive_gain_folios"]) == 0)
    check("status_exact", result["status"] == "LEGACY_OUT_OF_PANEL_HPR2_TRANSFER_NO_SELECTOR_PAID_WINNER")
    check("result_primary_matches", result["primary_best"]["representation"] == best["representation"] and abs(result["primary_best"]["gain_bits"] - float(best["gain_bits"])) < 1e-8)

    for group in ("inputs", "outputs", "documents", "implementation"):
        for name, digest in result[group].items():
            path = ROOT / name
            check(f"hash:{name}", path.exists() and sha(path) == digest)
    check("f84_flags_false", all(value is False for value in result["f84r"].values()))
    check("report_claim_ceiling", "No semantic class, role, gloss" in (ROOT / "GDT109_LEGACY_OUT_OF_PANEL_DESCRIPTOR_TRANSFER_REPORT.md").read_text(encoding="utf-8"))

    passed = all(row["passed"] for row in checks)
    validation = {"schema": "GDT109_LEGACY_OUT_OF_PANEL_DESCRIPTOR_TRANSFER_VALIDATION_V1",
                  "status": "PASS" if passed else "FAIL", "checks_passed": sum(row["passed"] for row in checks),
                  "checks_total": len(checks), "result_sha256": sha(RESULT), "checks": checks}
    VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": validation["status"], "checks": f"{validation['checks_passed']}/{validation['checks_total']}"}, sort_keys=True))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
