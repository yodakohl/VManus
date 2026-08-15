#!/usr/bin/env python3
"""Integrity and independent headline validation for GDT067."""
from __future__ import annotations
import csv,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RESULT=ROOT/"gdt067_result.json";SOURCE=ROOT/"gdt062_right_family_inventory.tsv";PAIRS=ROOT/"gdt067_b3_context_pairs.tsv";CELLS=ROOT/"gdt067_b3_context_cells.tsv";VARIANTS=ROOT/"gdt067_variant_log.tsv";LEDGER=ROOT/"GDT002_YOLO_LEDGER.tsv";VALIDATION=ROOT/"gdt067_validation.json"
def read(p):
 with p.open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def close(a,b,t=5e-9):return abs(float(a)-float(b))<=t
def main():
 r=json.loads(RESULT.read_text());src=read(SOURCE);pairs=read(PAIRS);cells=read(CELLS);checks={}
 checks["source_units_seal"]=len(src)==r["groups"]==15592 and len({(x["page"],x["page_host"],x["b3"],x["wrapper"],x["local_frame"],x["right_family"])for x in src})==r["units"]==11480 and not any(x["locus"].startswith("f84r")for x in src)and not any(r["f84r"].values())
 checks["pair_cell_counts"]=len(pairs)==r["supported_pairs"]==210 and len(cells)==r["cells"]==20 and all(int(x["control_units"])>0 for x in pairs)
 counts=Counter((x["host"],x["register"],x["wrapper"],x["frame"],x["right_family"])for x in pairs);checks["cell_pair_binding"]=all(int(x["supported_pairs"])==counts[(x["host"],x["register"],x["wrapper"],x["frame"],x["right_family"])]for x in cells)
 sim=sum(float(x["mean_context_similarity"])for x in cells)/len(cells);ctrl=sum(float(x["mean_matched_control_similarity"])for x in cells)/len(cells);checks["means"]=close(sim,r["mean_exact_host_similarity"])and close(ctrl,r["mean_matched_control_similarity"])and close(sim-ctrl,r["gain_vs_control"])
 checks["directions"]=sum(float(x["gain_vs_control"])>0 for x in cells)==r["positive_cells"]==12
 by=defaultdict(list)
 for x in cells:by[x["register"]].append(float(x["gain_vs_control"]))
 exp={k:{"cells":len(v),"positive":sum(q>0 for q in v),"mean_gain":sum(v)/len(v)}for k,v in sorted(by.items())};checks["registers"]=set(exp)==set(r["register_diagnostics"])and all(exp[k]["cells"]==r["register_diagnostics"][k]["cells"]and exp[k]["positive"]==r["register_diagnostics"][k]["positive"]and close(exp[k]["mean_gain"],r["register_diagnostics"][k]["mean_gain"])for k in exp)
 checks["variants"]={x["variant_id"]:x["status"]for x in read(VARIANTS)}=={"V00":"PRIMARY","V01":"RUN_CONTROL","V02":"INHERITED_FORMAL","V03":"NOT_RUN"}
 checks["status_ceiling"]=r["status"]=="B3_CONTENT_NEUTRALITY_NOT_SUPPORTED_BY_INTERNAL_CONTEXT"and r["sign_test_p"]>.05 and"external content neutrality remains unconfirmed"in r["interpretation"]and"No role"in r["claim_ceiling"]
 body=dict(r);claim=body.pop("result_content_sha256");checks["content_hash"]=csha(body)==claim;checks["bound_hashes"]=all(sha(ROOT/name)==digest for fam in("inputs","outputs","documents","implementation")for name,digest in r[fam].items())
 z=[x for x in read(LEDGER)if x["checkpoint_id"]=="GDT067_CKPT001"];checks["ledger"]=len(z)==1 and z[0]["status"]==r["status"]and z[0]["result_artifact"]==RESULT.name
 passed=all(checks.values());v={"schema":"GDT067_B3_PAGE_HOST_CONTEXT_VALIDATION_V1","status":"PASS_INTEGRITY_AND_INDEPENDENT_HEADLINE_CHECKS"if passed else"FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Checks inventory/unit, supported pair/cell binding, means, register diagnostics, variants, seal, hashes, ledger, status and ceiling; does not recompute every Jaccard pair."};VALIDATION.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":v["status"],"checks":f'{v["checks_passed"]}/{v["checks_total"]}'},sort_keys=True));
 if not passed:raise SystemExit(1)
if __name__=="__main__":main()
