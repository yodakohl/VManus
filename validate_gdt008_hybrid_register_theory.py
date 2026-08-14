#!/usr/bin/env python3
"""Independent integrity and claim-scope validator for GDT008 theory synthesis."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "gdt008_result.json"
VALIDATION = ROOT / "gdt008_validation.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def read_tsv(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    checks: list[tuple[str, bool]] = []
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    normalized = dict(result)
    recorded = normalized.pop("result_content_sha256")
    checks.append(("schema", result["schema"] == "GDT008_HYBRID_REGISTER_THEORY_RESULT_V1"))
    checks.append(("content_hash", recorded == canonical_sha(normalized)))
    for section in ("inputs", "implementation", "outputs"):
        for name, digest in result[section].items():
            checks.append((f"{section}:{name}", sha(ROOT / name) == digest))

    evidence = read_tsv("gdt008_evidence_map.tsv")
    comparison = read_tsv("gdt008_theory_comparison.tsv")
    roles = read_tsv("gdt008_provisional_roles.tsv")
    parses = read_tsv("gdt008_representative_parses.tsv")
    predictions = read_tsv("gdt008_novel_predictions.tsv")
    occurrences = read_tsv("gdt002_morphology_occurrences.tsv")
    model = json.loads((ROOT / "gdt008_hybrid_register_model.json").read_text(encoding="utf-8"))
    report = (ROOT / "GDT008_HYBRID_REGISTER_THEORY_REPORT.md").read_text(encoding="utf-8")

    penalties = {
        "COMPRESSED_ABBREVIATED_NATURAL_LANGUAGE": 2.0,
        "SEMANTIC_TECHNICAL_NOTATION": 2.5,
        "HYBRID_REGISTER": 4.0,
    }
    fields = {
        "COMPRESSED_ABBREVIATED_NATURAL_LANGUAGE": "compressed_language_fit",
        "SEMANTIC_TECHNICAL_NOTATION": "notation_fit",
        "HYBRID_REGISTER": "hybrid_fit",
    }
    recomputed: dict[str, float] = {}
    for architecture, field in fields.items():
        recomputed[architecture] = sum(float(row["weight"]) * float(row[field]) for row in evidence) - penalties[architecture]
    comparison_by_id = {row["architecture"]: row for row in comparison}
    checks.append(("three_architectures", set(comparison_by_id) == set(fields)))
    checks.append(("scores_exact", all(abs(float(comparison_by_id[key]["net_abductive_score"]) - value) < 1e-12 for key, value in recomputed.items())))
    expected = sorted(recomputed, key=lambda key: (-recomputed[key], key))
    observed = [row["architecture"] for row in sorted(comparison, key=lambda row: int(row["rank"]))]
    checks.append(("rank_exact", observed == expected))
    checks.append(("hybrid_selected", expected[0] == "HYBRID_REGISTER" and result["leading_theory"] == "HPR1_HYBRID_PROCEDURAL_REGISTER"))

    daldy = [
        row for row in occurrences
        if row["module"] == "DAL"
        and row["ZL3b_token"] == row["IT2a_token"] == row["RF1b_token"] == "daldy"
    ]
    checks.append(("daldy_reconstructed", len(daldy) == result["daldy_all_reading_exact_groups"] == 13))
    checks.append(("all_inputs_exclude_f84r_occurrences", not any(row["locus"].startswith("f84r") for row in occurrences)))
    checks.append(("f84_sealed", model["f84r_access"] == {"formal_payload_opened": False, "formal_payload_joined": False, "formal_payload_scored": False, "prediction_packet_frozen": True}))
    checks.append(("prediction_count", len(predictions) == result["novel_predictions"] == 10))
    checks.append(("four_sealed_predictions", sum(row["target_scope"] == "SEALED_F84R" for row in predictions) == 4))
    checks.append(("predictions_unrun", all("NOT_RUN" in row["status"] or "UNOPENED" in row["status"] for row in predictions)))
    checks.append(("roles_explicitly_provisional", len(roles) == result["provisional_roles"] == 15 and all(row["confidence"] for row in roles)))
    checks.append(("parses_have_counterparses", len(parses) == result["representative_parses"] == 13 and all(row["counterparse"] for row in parses)))
    checks.append(("prior_results_preserved", result["prior_results_preserved"]["GDT002"] == "FORMAL_REUSE_SUPPORTED_SEMANTIC_SLOT_SYSTEM_NOT_SUPPORTED" and result["prior_results_preserved"]["GDT003"] == "NOT DISTINGUISHABLE FROM STRING STATISTICS"))
    checks.append(("report_selects_one_theory", "HPR-1: Hybrid Procedural Register" in report and "strongest present generative explanation" in report))
    checks.append(("awkward_evidence_retained", "Awkward observations" in report and "context mixer" in report and "worse than strong string" in report))
    checks.append(("claim_ceiling", all(term in result["claim_ceiling"].lower() for term in ("exploratory", "no confirmed language", "plaintext", "translation"))))
    ledger = (ROOT / "GDT002_YOLO_LEDGER.tsv").read_text(encoding="utf-8")
    checks.append(("branch_ledger", ledger.count("GDT008_CKPT001") == 1))

    failures = [name for name, passed in checks if not passed]
    validation = {
        "schema": "GDT008_HYBRID_REGISTER_THEORY_VALIDATION_V1",
        "status": "PASS" if not failures else "FAIL",
        "checks": len(checks),
        "failures": failures,
        "result_sha256": sha(RESULT),
        "validator_sha256": sha(Path(__file__)),
        "scope": "Independent artifact hashes, abductive-score arithmetic, selected architecture, daldy count, f84 sealing, prediction freeze, parse alternatives, preserved prior conclusions, ledger, and claim ceiling. Does not confirm proposed functions or meanings.",
    }
    VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(validation, sort_keys=True))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
