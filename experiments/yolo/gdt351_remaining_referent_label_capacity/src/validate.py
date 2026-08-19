#!/usr/bin/env python3
"""Independent table-level validator for GDT351."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import GuardedTSV  # noqa: E402
EXP = ROOT / "experiments/yolo/gdt351_remaining_referent_label_capacity"
ART = EXP / "artifacts"


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def stable(o): return (json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=False)+"\n").encode()


def main():
    result = json.loads((ART / "gdt351_result.json").read_text())
    rows = read_tsv(ART / "gdt351_capacity.tsv")
    cand = read_tsv(ROOT / "gdt169_external_referent_candidates.tsv")
    exact_guard = GuardedTSV(
        ROOT / "experiments/semantic_assumptions/results/existing_human_exact_locus_annotations.tsv",
        selector_column="page", allowed_values={"f102r1", "f102r2", "f89v2"},
        forbidden_prefixes=("f84",), forbidden_action="skip")
    exact = list(exact_guard)
    checks=[]
    def ck(name, ok, detail=""): checks.append({"name":name,"pass":bool(ok),"detail":detail})
    expected=[r for r in cand if r["evidence_panel"]=="HERBAL_TO_PHARMA" and r["assertion_strength"]=="ASSERTED_SAME" and r["local_query_locus"]=="NONE"]
    ck("four_expected_source_rows", len(expected)==4, len(expected))
    ck("candidate_ids_exact", {r["candidate_id"] for r in rows}=={r["candidate_id"] for r in expected})
    ck("three_without_label", sum(r["capacity_status"]=="NO_SEPARATE_TARGET_LABEL" for r in rows)==3)
    ck("one_ambiguous", sum(r["capacity_status"]=="AMBIGUOUS_PROXIMITY_ONLY" for r in rows)==1)
    ck("zero_eligible", all(r["singular_owned_locus"]=="NONE" for r in rows))
    ck("no_images", all(r["image_opened"]=="0" for r in rows))
    ck("no_formal_score", all(r["formal_identity_opened_or_scored"]=="0" for r in rows))
    e28=next(r for r in exact if r["locus"]=="f89v2.28")
    ck("f89v2_28_between_two_plants", "[3,3] and <f89v2>[3,4]" in e28["local_comment"])
    ck("status", result["status"]=="STOP_ZERO_NEW_SINGULAR_OWNED_REFERENT_LABELS")
    ck("counts", result["counts"]=={"frozen_relations":4,"no_separate_target_label":3,"ambiguous_proximity_only":1,"eligible_new_local_queries":0})
    for rel,h in result["inputs"].items(): ck("input_hash:"+rel, sha(ROOT/rel)==h)
    for rel,h in result["outputs"].items(): ck("output_hash:"+rel, sha(ROOT/rel)==h)
    for rel,h in result["documents"].items(): ck("document_hash:"+rel, sha(ROOT/rel)==h)
    for rel,h in result["implementation"].items(): ck("implementation_hash:"+rel, sha(ROOT/rel)==h)
    content=dict(result); claimed=content.pop("result_content_sha256")
    ck("result_content_hash", hashlib.sha256(stable(content)).hexdigest()==claimed)
    ck("f84_absent", all("f84" not in "\t".join(r.values()).lower() for r in rows))
    ck("final_guard_skipped_f84", exact_guard.stats.skipped_forbidden > 0, exact_guard.stats.__dict__)
    ck("correction_disclosed", result["source_access"]["prepublication_first_local_build_parsed_global_human_rows_including_f84"] is True)
    ck("superseded_hashes_bound", set(result["superseded_prepublication_local_bytes"]) == {"capacity_sha256","result_sha256","validation_sha256"})
    out={"experiment":"GDT351","schema":"GDT351_VALIDATION_V1","status":"PASS" if all(x["pass"] for x in checks) else "FAIL","scope":"Independent source-selection, ambiguity, accounting, seal, and hash reconstruction; not an independent visual review.","checks_passed":sum(x["pass"] for x in checks),"checks_failed":sum(not x["pass"] for x in checks),"checks":checks,"result_sha256":sha(ART/"gdt351_result.json"),"implementation_sha256":sha(Path(__file__))}
    (ART/"gdt351_validation.json").write_bytes(stable(out))
    print(out["status"], out["checks_passed"], out["checks_failed"])
    if out["status"]!="PASS": raise SystemExit(1)


if __name__=="__main__": main()
