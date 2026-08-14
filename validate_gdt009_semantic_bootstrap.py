#!/usr/bin/env python3
"""Independent arithmetic/integrity validator for GDT009 semantic bootstrap."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "gdt009_result.json"
VALIDATION = ROOT / "gdt009_validation.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def read_tsv(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def tagged(value: str, key: str) -> str:
    for part in value.split(";"):
        if part.startswith(key + ":"):
            return part.split(":", 1)[1]
    return ""


def main() -> None:
    checks: list[tuple[str, bool]] = []
    result = json.loads(RESULT.read_text())
    normalized = dict(result)
    recorded = normalized.pop("result_content_sha256")
    checks.append(("schema", result["schema"] == "GDT009_SEMANTIC_BOOTSTRAP_RESULT_V1"))
    checks.append(("result_content_hash", recorded == canonical_sha(normalized)))
    for section in ("inputs", "implementation", "outputs"):
        for name, digest in result[section].items():
            checks.append((f"{section}:{name}", sha(ROOT / name) == digest))

    occurrences = read_tsv("gdt002_morphology_occurrences.tsv")
    units = read_tsv("gdt009_unit_evidence.tsv")
    evidence = read_tsv("gdt009_world_evidence.tsv")
    worlds = read_tsv("gdt009_joint_worlds.tsv")
    candidates = read_tsv("gdt009_semantic_candidates.tsv")
    parses = read_tsv("gdt009_locus_parses.tsv")
    counters = read_tsv("gdt009_counterexamples.tsv")
    predictions = read_tsv("gdt009_predictions.tsv")
    model = json.loads((ROOT / "gdt009_semantic_model.json").read_text())
    report = (ROOT / "GDT009_SEMANTIC_BOOTSTRAP_REPORT.md").read_text()

    checks.append(("no_f84_occurrences", not any(row["locus"].startswith("f84r") for row in occurrences)))
    checks.append(("no_f84_parses", not any(row["locus"].startswith("f84r") for row in parses)))
    checks.append(("f84_sealed", model["f84r"] == {"opened":False,"joined":False,"scored":False,"prior_predictions_unchanged":True}))
    checks.append(("eight_units", {row["unit"] for row in units} == {"AR","OL","DAL","DAR","SY","TE","TEE","DY"}))
    for row in units:
        source = [x for x in occurrences if x["module"] == row["unit"]]
        exact = [x for x in source if x["ZL3b_token"] and x["ZL3b_token"] == x["IT2a_token"] == x["RF1b_token"]]
        checks.append((f"unit_rows:{row['unit']}", int(row["physical_occurrence_rows"]) == len(source)))
        checks.append((f"unit_exact:{row['unit']}", int(row["all_reading_exact_rows"]) == len(exact)))
        first = sum(int(x["source_group_index"]) == 1 for x in exact) / len(exact)
        last = sum(int(x["source_group_index"]) == int(tagged(x["source_group_count_by_reading"], "ZL3b")) for x in exact) / len(exact)
        checks.append((f"unit_position:{row['unit']}", abs(float(row["line_first_share_exact"])-first)<5e-7 and abs(float(row["line_final_share_exact"])-last)<5e-7))

    penalties = {"W1_PROCEDURAL_REFERENCE_STATE":4.5,"W2_QUANTIFIED_CATALOGUE":3.5,"W3_SPATIAL_FLOW_DIAGRAM":3.0,"W4_OBJECT_NOMENCLATURE":2.0,"W5_PURE_TEMPLATE_NO_SEMANTICS":2.0}
    fields = {"W1_PROCEDURAL_REFERENCE_STATE":"procedural_reference_fit","W2_QUANTIFIED_CATALOGUE":"quantified_catalogue_fit","W3_SPATIAL_FLOW_DIAGRAM":"spatial_flow_fit","W4_OBJECT_NOMENCLATURE":"object_nomenclature_fit","W5_PURE_TEMPLATE_NO_SEMANTICS":"pure_template_fit"}
    scores = {world:sum(float(r["weight"])*float(r[field]) for r in evidence)-penalties[world] for world,field in fields.items()}
    by_id = {row["world_id"]:row for row in worlds}
    checks.append(("five_worlds", set(by_id) == set(fields)))
    checks.append(("world_scores", all(abs(float(by_id[k]["net_abductive_score"])-v)<1e-12 for k,v in scores.items())))
    order = sorted(scores,key=lambda key:(-scores[key],key))
    checks.append(("world_rank", [r["world_id"] for r in sorted(worlds,key=lambda x:int(x["rank"]))] == order))
    checks.append(("prs_selected", order[0] == result["leading_world"] == "W1_PROCEDURAL_REFERENCE_STATE"))
    checks.append(("explicit_functions", len(candidates) == result["semantic_candidates"] == 18 and all(r["claim_class"] == "PROVISIONAL_FUNCTION_NOT_TRANSLATION" for r in candidates)))
    checks.append(("counterparsed_loci", len(parses) == result["representative_parses"] == 14 and all(r["counterparse_or_caveat"] for r in parses)))
    checks.append(("counterexamples", len(counters) == result["counterexamples"] == 10 and sum(r["status"].startswith("FAILED") for r in counters) >= 5))
    checks.append(("predictions", len(predictions) == result["novel_predictions"] == 10 and all(r["status"] == "FROZEN_FOR_FUTURE_VALIDATION" for r in predictions)))
    checks.append(("prior_results", result["prior_results_preserved"]["GDT002"] == "FORMAL_REUSE_SUPPORTED_SEMANTIC_SLOT_SYSTEM_NOT_SUPPORTED" and result["prior_results_preserved"]["GDT003"] == "NOT DISTINGUISHABLE FROM STRING STATISTICS"))
    checks.append(("report_concrete", "q    under the current record/frame" in report and "`AROL` therefore means roughly" in report))
    checks.append(("claim_ceiling", all(term in result["claim_ceiling"].lower() for term in ("speculative","not a confirmed language","plaintext","translation"))))
    ledger = (ROOT / "GDT002_YOLO_LEDGER.tsv").read_text()
    checks.append(("branch_ledger", ledger.count("GDT009_CKPT001") == 1))

    failures = [name for name, ok in checks if not ok]
    validation = {"schema":"GDT009_SEMANTIC_BOOTSTRAP_VALIDATION_V1","status":"PASS" if not failures else "FAIL","checks":len(checks),"failures":failures,"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Independently checks artifact hashes, non-f84 scope, module counts/positions, world-score arithmetic, selected world, explicit provisional functions, counterparses, falsifiers, frozen predictions, prior-result preservation, and branch ledger. It does not confirm the proposed meanings."}
    VALIDATION.write_text(json.dumps(validation,indent=2,sort_keys=True)+"\n")
    print(json.dumps(validation,sort_keys=True))
    if failures: raise SystemExit(1)


if __name__ == "__main__":
    main()
