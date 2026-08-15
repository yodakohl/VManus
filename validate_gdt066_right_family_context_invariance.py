#!/usr/bin/env python3
"""Integrity and independent headline validation for GDT066."""
from __future__ import annotations
import csv, hashlib, json
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parent
RESULT=ROOT/"gdt066_result.json"; SOURCE=ROOT/"gdt062_right_family_inventory.tsv"
PAIRS=ROOT/"gdt066_right_family_context_pairs.tsv"; CELLS=ROOT/"gdt066_right_family_context_cells.tsv"
VARIANTS=ROOT/"gdt066_variant_log.tsv"; LEDGER=ROOT/"GDT002_YOLO_LEDGER.tsv"
VALIDATION=ROOT/"gdt066_validation.json"
def read(path):
    with path.open(encoding="utf-8",newline="") as handle:return list(csv.DictReader(handle,delimiter="\t"))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def csha(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def close(a,b,tol=5e-9):return abs(float(a)-float(b))<=tol

def main():
    result=json.loads(RESULT.read_text()); src=read(SOURCE); pairs=read(PAIRS); cells=read(CELLS); checks={}
    checks["source_and_seal"]=len(src)==result["groups"]==15592 and not any(r["locus"].startswith("f84r") for r in src) and not any(result["f84r"].values())
    units={(r["page"],r["page_host"],r["right_family"],r["wrapper"],r["local_frame"]) for r in src}
    checks["unit_count"]=len(units)==result["units"]==11470
    checks["pair_cell_counts"]=len(pairs)==result["supported_pairs"]==30627 and len(cells)==result["cells"]==291
    checks["supported_pairs"]=all(int(r["control_units"])>0 for r in pairs)
    pair_counts=Counter((r["host"],r["register"],r["wrapper"],r["frame"],r["pair_type"]) for r in pairs)
    checks["cell_pair_binding"]=all(int(r["different_right_pairs"])==pair_counts[(r["host"],r["register"],r["wrapper"],r["frame"],"DIFF_RIGHT_FAMILY")] and int(r["same_right_pairs"])==pair_counts[(r["host"],r["register"],r["wrapper"],r["frame"],"SAME_RIGHT_FAMILY")] for r in cells)
    diff=sum(float(r["different_right_mean_similarity"]) for r in cells)/len(cells)
    ctrl=sum(float(r["matched_control_mean_similarity"]) for r in cells)/len(cells)
    both=[r for r in cells if r["same_right_available"]=="1"]
    same=sum(float(r["same_right_mean_similarity"]) for r in both)/len(both)
    checks["headline_means"]=close(diff,result["mean_different_right_similarity"]) and close(ctrl,result["mean_matched_control_similarity"]) and close(diff-ctrl,result["different_minus_control"]) and close(same,result["mean_same_right_similarity"]) and close(diff-same,result["different_minus_same"])
    checks["directions"]=sum(float(r["different_minus_control"])>0 for r in cells)==result["positive_cells"]==181 and len(both)==result["same_right_cells"]==216
    byreg=defaultdict(list)
    for row in cells:byreg[row["register"]].append(float(row["different_minus_control"]))
    expected={k:{"cells":len(v),"positive":sum(x>0 for x in v),"mean_gain":sum(v)/len(v)} for k,v in sorted(byreg.items())}
    checks["register_diagnostics"]=set(expected)==set(result["register_diagnostics"]) and all(expected[k]["cells"]==result["register_diagnostics"][k]["cells"] and expected[k]["positive"]==result["register_diagnostics"][k]["positive"] and close(expected[k]["mean_gain"],result["register_diagnostics"][k]["mean_gain"]) for k in expected)
    lead={h:[r for r in cells if r["host"]==h] for h in ("d","ok")}
    checks["postselected_leads"]=result["postselected_lead_cells"]=={h:len(z) for h,z in lead.items()} and result["postselected_lead_positive"]=={h:sum(float(r["different_minus_control"])>0 for r in z) for h,z in lead.items()}
    checks["variant_log"]={r["variant_id"]:r["status"] for r in read(VARIANTS)}=={"V00":"PRIMARY","V01":"RUN_CONTROL","V02":"RUN_SENSITIVITY","V03":"POSTSELECTED_DISPLAY","V04":"NOT_RUN"}
    checks["status_and_ceiling"]=result["status"]=="RIGHT_FAMILY_INTERNAL_CONTEXT_INVARIANCE_SUPPORTED" and result["different_minus_control"]>0 and result["different_minus_same"]<0 and "external content neutrality remains unconfirmed" in result["interpretation"] and "No role" in result["claim_ceiling"]
    body=dict(result); claimed=body.pop("result_content_sha256"); checks["result_content_hash"]=csha(body)==claimed
    checks["bound_hashes"]=all(sha(ROOT/name)==digest for family in ("inputs","outputs","documents","implementation") for name,digest in result[family].items())
    ledger=[r for r in read(LEDGER) if r["checkpoint_id"]=="GDT066_CKPT001"]
    checks["ledger_exact"]=len(ledger)==1 and ledger[0]["status"]==result["status"] and ledger[0]["result_artifact"]==RESULT.name
    passed=all(checks.values())
    out={"schema":"GDT066_RIGHT_FAMILY_CONTEXT_INVARIANCE_VALIDATION_V1","status":"PASS_INTEGRITY_AND_INDEPENDENT_HEADLINE_CHECKS" if passed else "FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Independently checks inventory/unit, supported pair/cell bindings, aggregate means, register and lead diagnostics, variant log, f84 seal, hashes, ledger, status and ceiling. It does not recompute every weighted-Jaccard pair."}
    VALIDATION.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":out["status"],"checks":f'{out["checks_passed"]}/{out["checks_total"]}'},sort_keys=True))
    if not passed:raise SystemExit(1)
if __name__=="__main__":main()
