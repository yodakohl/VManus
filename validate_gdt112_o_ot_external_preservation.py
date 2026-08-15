#!/usr/bin/env python3
"""Independent census/arithmetic validator for GDT112."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gdt062_right_family_inventory.tsv"
PAGES = ROOT / "experiments/semantic_assumptions/results/existing_human_page_role_matrix.tsv"
UNITS = ROOT / "gdt112_o_ot_units.tsv"
SCORES = ROOT / "gdt112_o_ot_scores.tsv"
TAGS = ROOT / "gdt112_o_ot_tag_scores.tsv"
FOLDS = ROOT / "gdt112_o_ot_folio_scores.tsv"
RESULT = ROOT / "gdt112_result.json"
VALIDATION = ROOT / "gdt112_validation.json"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    result = json.loads(RESULT.read_text(encoding="utf-8")); checks = []
    def check(name: str, passed: bool, detail: object = "") -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    pages = {row["page"]: row for row in read(PAGES) if not row["page"].startswith("f84r")}
    expected = {}
    for row in read(SOURCE):
        if row["page"] in pages and row["local_frame"] in {"O", "OT"}:
            expected[row["page"], row["page_host"], row["local_frame"]] = (row["physical_folio"], row["register"])
    units = read(UNITS)
    actual = {(row["page"], row["page_host"], row["frame"]): (row["physical_folio"], row["register"]) for row in units}
    check("unit_census_exact", actual == expected, len(actual))
    check("unit_count", len(units) == 1033)
    check("page_count", len({row["page"] for row in units}) == 189)
    check("folio_count", len({row["physical_folio"] for row in units}) == 92)
    check("f84_absent", not any(row["page"].startswith("f84r") for row in units))
    check("roles_unassigned", all(row["semantic_role"] == "UNASSIGNED" for row in units))
    counts = Counter(row["page"] for row in units)
    check("reciprocal_page_weights", all(abs(float(row["page_weight"]) - 1 / counts[row["page"]]) < 1e-10 for row in units))

    unique_pages = sorted(counts)
    candidates = sorted({tag for row in units for tag in row["source_tags"].split(";") if tag})
    eligible = [tag for tag in candidates if 10 <= sum(tag in pages[page]["source_tags"].split(";") for page in unique_pages) <= len(unique_pages) - 10]
    check("eligible_tags_exact", eligible == result["external_tags"], eligible)
    check("five_tags", len(eligible) == 5)

    scores = read(SCORES); by_mode = {row["mode"]: row for row in scores}
    check("three_modes", set(by_mode) == {"CROSS_FRAME", "SAME_FRAME", "ANY_FRAME"})
    check("score_arithmetic", all(abs(float(row["nuisance_bits"]) - float(row["held_bits"]) - float(row["gain_bits"])) < 1e-8 for row in scores))
    check("selector_arithmetic", all(abs(float(row["selector_paid_gain_bits"]) - (float(row["gain_bits"]) - math.log2(3))) < 1e-8 for row in scores))
    check("all_modes_negative", all(float(row["gain_bits"]) < 0 for row in scores))
    check("cross_least_negative", scores[0]["mode"] == "CROSS_FRAME")
    check("cross_coverage", int(by_mode["CROSS_FRAME"]["scored_predictions"]) == 1024)
    check("cross_positive_folios", int(by_mode["CROSS_FRAME"]["positive_gain_folios"]) == 4)
    check("status_exact", result["status"] == "O_OT_EXACT_HOST_EXTERNAL_ASSOCIATION_NOT_PRESERVED")

    tag_rows = read(TAGS); folds = read(FOLDS)
    check("tag_grid", len(tag_rows) == 3 * 5)
    check("fold_grid", len(folds) == 3 * 92)
    check("tag_totals", all(abs(sum(float(row["gain_bits"]) for row in tag_rows if row["mode"] == mode) - float(by_mode[mode]["gain_bits"])) < 1e-8 for mode in by_mode))
    check("fold_totals", all(abs(sum(float(row["gain_bits"]) for row in folds if row["mode"] == mode) - float(by_mode[mode]["gain_bits"])) < 1e-8 for mode in by_mode))

    for group in ("inputs", "outputs", "documents", "implementation"):
        for name, digest in result[group].items():
            path = ROOT / name
            check(f"hash:{name}", path.exists() and sha(path) == digest)
    check("f84_flags_false", all(value is False for value in result["f84r"].values()))
    check("report_ceiling", "No semantic role" in (ROOT / "GDT112_O_OT_EXTERNAL_PRESERVATION_REPORT.md").read_text(encoding="utf-8"))

    passed = all(row["passed"] for row in checks)
    validation = {"schema": "GDT112_O_OT_EXTERNAL_PRESERVATION_VALIDATION_V1", "status": "PASS" if passed else "FAIL",
                  "checks_passed": sum(row["passed"] for row in checks), "checks_total": len(checks),
                  "result_sha256": sha(RESULT), "checks": checks}
    VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": validation["status"], "checks": f"{validation['checks_passed']}/{validation['checks_total']}"}, sort_keys=True))
    if not passed: raise SystemExit(1)


if __name__ == "__main__":
    main()
