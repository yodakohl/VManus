#!/usr/bin/env python3
"""Integrity and independent headline validation for GDT065."""
from __future__ import annotations
import csv, hashlib, json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "gdt065_result.json"
SOURCE = ROOT / "gdt062_right_family_inventory.tsv"
PAIRS = ROOT / "gdt065_o_ot_context_pairs.tsv"
CELLS = ROOT / "gdt065_o_ot_context_cells.tsv"
VARIANTS = ROOT / "gdt065_variant_log.tsv"
LEDGER = ROOT / "GDT002_YOLO_LEDGER.tsv"
VALIDATION = ROOT / "gdt065_validation.json"

def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def csha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True,
                                      separators=(",", ":")).encode()).hexdigest()
def close(a, b, tol=5e-9): return abs(float(a) - float(b)) <= tol

def main():
    result = json.loads(RESULT.read_text())
    src, pairs, cells = read(SOURCE), read(PAIRS), read(CELLS)
    checks = {}
    checks["source_count_and_seal"] = len(src) == result["groups"] == 15592 and not any(
        row["locus"].startswith("f84r") for row in src)
    units = {(r["page"], r["page_host"], r["local_frame"], r["wrapper"])
             for r in src if r["local_frame"] in {"O", "OT"}}
    checks["unit_count"] = len(units) == result["units"] == 1446
    checks["pair_cell_counts"] = len(pairs) == result["pairs"] == 485 and len(cells) == result["cells"] == 53
    checks["all_pairs_have_controls"] = all(int(r["control_units"]) > 0 for r in pairs)
    pair_counts = Counter((r["host"], r["wrapper"], r["register"]) for r in pairs)
    checks["cell_pair_binding"] = all(int(r["cross_folio_o_ot_pairs"]) == pair_counts[(r["host"], r["wrapper"], r["register"])] for r in cells)
    same = sum(float(r["mean_context_similarity"]) for r in cells) / len(cells)
    control = sum(float(r["mean_matched_control_similarity"]) for r in cells) / len(cells)
    checks["mean_reconstruction"] = close(same, result["mean_same_host_o_ot_similarity"]) and close(control, result["mean_matched_control_similarity"]) and close(same-control, result["gain_vs_control"])
    checks["direction_reconstruction"] = sum(float(r["gain_vs_control"]) > 0 for r in cells) == result["positive_cells"] == 34
    byreg = defaultdict(list)
    for row in cells: byreg[row["register"]].append(float(row["gain_vs_control"]))
    expected = {k: {"cells": len(v), "positive": sum(x > 0 for x in v), "mean_gain": sum(v)/len(v)} for k, v in sorted(byreg.items())}
    checks["register_diagnostics"] = set(expected) == set(result["register_diagnostics"]) and all(
        expected[k]["cells"] == result["register_diagnostics"][k]["cells"] and
        expected[k]["positive"] == result["register_diagnostics"][k]["positive"] and
        close(expected[k]["mean_gain"], result["register_diagnostics"][k]["mean_gain"])
        for k in expected)
    variants = {r["variant_id"]: r["status"] for r in read(VARIANTS)}
    checks["variant_audit"] = variants == {"V00":"PRIMARY", "V01":"REJECTED_IMPLEMENTATION_DIAGNOSTIC", "V02":"NOT_RUN_CAPACITY_LIMIT"}
    checks["status_and_ceiling"] = result["status"] == "O_OT_PAGE_CONTEXT_PRESERVATION_WEAK_OR_UNSTABLE" and result["sign_test_p"] > .05 and "external content preservation remains unscored" in result["interpretation"] and "No role" in result["claim_ceiling"]
    checks["f84_flags"] = not any(result["f84r"].values())
    body = dict(result); claimed = body.pop("result_content_sha256")
    checks["result_content_hash"] = csha(body) == claimed
    checks["bound_hashes"] = all(sha(ROOT/name) == digest for family in ("inputs", "outputs", "documents", "implementation") for name, digest in result[family].items())
    ledger = [r for r in read(LEDGER) if r["checkpoint_id"] == "GDT065_CKPT001"]
    checks["ledger_exact"] = len(ledger) == 1 and ledger[0]["status"] == result["status"] and ledger[0]["result_artifact"] == RESULT.name
    passed = all(checks.values())
    out = {"schema":"GDT065_O_OT_PAGE_CONTEXT_PRESERVATION_VALIDATION_V1",
           "status":"PASS_INTEGRITY_AND_INDEPENDENT_HEADLINE_CHECKS" if passed else "FAIL",
           "checks":checks, "checks_passed":sum(checks.values()), "checks_total":len(checks),
           "result_sha256":sha(RESULT), "validator_sha256":sha(Path(__file__)),
           "scope":"Independently checks inventory/unit counts, supported pair/cell binding, aggregate means, register diagnostics, correction log, seal, hashes, ledger, status, and claim ceiling. It does not independently recompute every page-context Jaccard."}
    VALIDATION.write_text(json.dumps(out, indent=2, sort_keys=True)+"\n")
    print(json.dumps({"status":out["status"], "checks":f'{out["checks_passed"]}/{out["checks_total"]}'}, sort_keys=True))
    if not passed: raise SystemExit(1)

if __name__ == "__main__": main()
