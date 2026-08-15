#!/usr/bin/env python3
"""Integrity and claim validator for GDT113 synthesis."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "gdt113_result.json"
MODEL = ROOT / "gdt113_page_conditioned_record_code_model.json"
MATRIX = ROOT / "gdt113_hpr2_hypothesis_matrix.tsv"
VALIDATION = ROOT / "gdt113_validation.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    result = json.loads(RESULT.read_text(encoding="utf-8")); model = json.loads(MODEL.read_text(encoding="utf-8"))
    with MATRIX.open(encoding="utf-8", newline="") as handle: matrix = list(csv.DictReader(handle, delimiter="\t"))
    checks = []
    def check(name: str, passed: bool, detail: object = "") -> None: checks.append({"check": name, "passed": bool(passed), "detail": detail})

    check("status_exact", result["status"] == "PAGE_CONDITIONED_RECORD_CODE_IS_LEADING_GENERATIVE_THEORY")
    check("leader_exact", model["leading_theory"] == result["leading_theory"] == "PAGE_CONDITIONED_RECORD_CODE")
    check("four_theories", len(model["theory_comparison"]) == 4)
    check("leader_score_highest", max(model["theory_comparison"], key=lambda row: row["abductive_score_10"])["theory"] == model["leading_theory"])
    check("ten_hypotheses", len(matrix) == result["hypotheses"] == 10)
    check("roles_unassigned", all(row["semantic_role"] == "UNASSIGNED" for row in matrix))
    check("dy_transition_failed", next(row for row in matrix if row["hypothesis"] == "H4_DY_PRE_POST_TRANSITION")["status"] == "FAILED_TESTED_TRANSITION_ALGEBRA")
    check("o_ot_not_supported", next(row for row in matrix if row["hypothesis"] == "H2_O_OT_PRESERVES_HOST_CONTENT")["status"] == "NOT_SUPPORTED_BROAD_TAGS")
    check("page_host_renamed", next(row for row in matrix if row["hypothesis"] == "H1_PAGE_HOST_EXTERNAL_CONTENT")["model_action"] == "RENAME_PAGE_HOST_TO_CODEWORD_BODY")
    check("grammar_complete", len(model["generative_grammar"]) == 9)
    check("components_count", len(model["formal_components"]) == result["formal_components"] == 9)
    check("representative_parses", len(model["representative_parses"]) == result["representative_parses"] == 5)
    check("predictions_count", len(model["frozen_non_f84_predictions"]) == result["frozen_predictions"] == 5)
    check("semantic_assignments_empty", model["semantic_assignments"] == [] and result["semantic_assignments"] == 0)
    check("translation_strategy_record_level", any("record" in row.lower() for row in model["translation_strategy"]))
    check("f84_flags_false", all(value is False for value in model["f84r"].values()))
    check("report_sealed", "completely sealed" in (ROOT / "GDT113_PAGE_CONDITIONED_RECORD_CODE_REPORT.md").read_text(encoding="utf-8"))

    for group in ("inputs", "outputs", "documents", "implementation"):
        for name, digest in result[group].items():
            path = ROOT / name
            check(f"hash:{name}", path.exists() and sha(path) == digest)
    passed = all(row["passed"] for row in checks)
    validation = {"schema": "GDT113_PAGE_CONDITIONED_RECORD_CODE_VALIDATION_V1", "status": "PASS" if passed else "FAIL",
                  "checks_passed": sum(row["passed"] for row in checks), "checks_total": len(checks),
                  "result_sha256": sha(RESULT), "checks": checks}
    VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": validation["status"], "checks": f"{validation['checks_passed']}/{validation['checks_total']}"}, sort_keys=True))
    if not passed: raise SystemExit(1)


if __name__ == "__main__":
    main()
