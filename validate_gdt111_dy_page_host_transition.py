#!/usr/bin/env python3
"""Independent census/arithmetic validator for GDT111."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gdt062_right_family_inventory.tsv"
INVENTORY = ROOT / "gdt111_boundary_inventory.tsv"
SCORES = ROOT / "gdt111_transition_model_scores.tsv"
FOLDS = ROOT / "gdt111_transition_folio_scores.tsv"
REGISTERS = ROOT / "gdt111_transition_register_scores.tsv"
RESULT = ROOT / "gdt111_result.json"
VALIDATION = ROOT / "gdt111_validation.json"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    result = json.loads(RESULT.read_text(encoding="utf-8")); checks = []
    def check(name: str, passed: bool, detail: object = "") -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    source = read(SOURCE); by = defaultdict(list)
    for row in source: by[row["locus"]].append(row)
    expected = []
    for locus, rows in sorted(by.items()):
        rows.sort(key=lambda row: int(row["group_index"]))
        for i, (previous, following) in enumerate(zip(rows, rows[1:])):
            if int(following["group_index"]) != int(previous["group_index"]) + 1: continue
            expected.append((f"{locus}|B{i + 1:03d}", int(previous["dy_closure"]), previous["page_host"], following["page_host"]))
    inventory = read(INVENTORY)
    actual = [(row["boundary_id"], int(row["dy_boundary"]), row["previous_page_host"], row["next_page_host"]) for row in inventory]
    check("boundary_census_exact", actual == expected, len(actual))
    check("event_count", len(inventory) == 12645, len(inventory))
    check("dy_count", sum(int(row["dy_boundary"]) for row in inventory) == 2255)
    check("folio_count", len({row["physical_folio"] for row in inventory}) == 93)
    check("f84_absent", not any(row["locus"].startswith("f84r") for row in inventory))
    check("roles_unassigned", all(row["semantic_role"] == "UNASSIGNED" for row in inventory))

    scores = read(SCORES); by_model = {row["model"]: row for row in scores}
    check("ten_models", len(scores) == 10 and len(by_model) == 10)
    check("score_arithmetic", all(abs(float(row["nuisance_bits"]) - float(row["held_bits"]) - float(row["gain_vs_nuisance_bits"])) < 1e-7 for row in scores))
    check("selector_arithmetic", all(abs(float(row["selector_paid_gain_bits"]) - (float(row["gain_vs_nuisance_bits"]) - 3.321928094887362)) < 1e-7 for row in scores))
    check("previous_final_best", scores[0]["model"] == "PREV_HOST_FINAL")
    check("previous_final_all_registers", int(by_model["PREV_HOST_FINAL"]["positive_gain_registers"]) == 5)
    check("next_host_negative", float(by_model["NEXT_PAGE_HOST_CHAR3"]["gain_vs_nuisance_bits"]) < 0)
    check("next_raw_negative", float(by_model["NEXT_RAW_CHAR3"]["gain_vs_nuisance_bits"]) < 0)
    check("full_worse_than_previous_host", float(by_model["NEXT_PREV_PAGE_HOST_EDGE_PAIR"]["held_bits"]) > float(by_model["PREV_PAGE_HOST_CHAR3"]["held_bits"]))
    check("post_increment_negative", float(result["post_host_increment_given_previous_bits"]) < 0)
    check("full_increment_negative", float(result["full_increment_given_previous_host_bits"]) < 0)
    check("status_exact", result["status"] == "DY_IS_PREVIOUS_EDGE_LICENSING_NOT_TRANSITION_ALGEBRA")

    folds = read(FOLDS); registers = read(REGISTERS)
    check("fold_grid", len(folds) == 10 * 93, len(folds))
    check("register_grid", len(registers) == 10 * 5, len(registers))
    check("fold_totals", all(sum(int(row["events"]) for row in folds if row["model"] == model) == 12645 for model in by_model))
    check("register_totals", all(sum(int(row["events"]) for row in registers if row["model"] == model) == 12645 for model in by_model))

    for group in ("inputs", "outputs", "documents", "implementation"):
        for name, digest in result[group].items():
            path = ROOT / name
            check(f"hash:{name}", path.exists() and sha(path) == digest)
    check("f84_flags_false", all(value is False for value in result["f84r"].values()))
    check("report_ceiling", "No semantic" in (ROOT / "GDT111_DY_PAGE_HOST_TRANSITION_REPORT.md").read_text(encoding="utf-8"))

    passed = all(row["passed"] for row in checks)
    validation = {"schema": "GDT111_DY_PAGE_HOST_TRANSITION_VALIDATION_V1", "status": "PASS" if passed else "FAIL",
                  "checks_passed": sum(row["passed"] for row in checks), "checks_total": len(checks),
                  "result_sha256": sha(RESULT), "checks": checks}
    VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": validation["status"], "checks": f"{validation['checks_passed']}/{validation['checks_total']}"}, sort_keys=True))
    if not passed: raise SystemExit(1)


if __name__ == "__main__":
    main()
