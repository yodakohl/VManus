#!/usr/bin/env python3
"""Independent aggregate/provenance validator for GDT383 Stage A."""
import csv,gzip,hashlib,json
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/"experiments/yolo/gdt383_repaired_local_role_transfer"
ART=BASE/"artifacts"
ENDPOINTS=["FUNCTION_WORD","ALTERNATIVE_OR","POLARITY_EXCLUSION","UNTIL_STATE_GATE","COORDINATOR","REF_ANAPHORA"]
OUTCOMES=["POST_RETURN_ABC_A","POST_PERSIST_THEN_EXIT","POST_HOMOGENEOUS_3","POST_LOW_DIVERSITY_3","POST_ANY_BOUNDARY_3","POST_WRAPPER_CHANGE_3","POST_RENDERER_STABLE_3","POST_TERMINUS_3"]

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def content(d):
 q=dict(d);q.pop("content_hash",None)
 return hashlib.sha256(json.dumps(q,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def read(name): return list(csv.DictReader((ART/name).open(),delimiter="\t"))
def outcomes(a,b,c):
 hs=[a["host_id"],b["host_id"],c["host_id"]]
 return {
  "POST_RETURN_ABC_A":int(hs[0]==hs[2] and hs[0]!=hs[1]),
  "POST_PERSIST_THEN_EXIT":int(hs[0]==hs[1] and hs[1]!=hs[2]),
  "POST_HOMOGENEOUS_3":int(len(set(hs))==1),
  "POST_LOW_DIVERSITY_3":int(len(set(hs))<=2),
  "POST_ANY_BOUNDARY_3":int(any(x["boundary_state"]!="B00" for x in [a,b,c])),
  "POST_WRAPPER_CHANGE_3":int(len({x["wrapper_state"] for x in [a,b,c]})>1),
  "POST_RENDERER_STABLE_3":int(len({x["renderer_variant"] for x in [a,b,c]})==1),
  "POST_TERMINUS_3":int(any(x["positional_state"]=="END" for x in [a,b,c]))}

def main():
 checks=[]
 def ck(name,value): checks.append((name,bool(value)))
 result=json.loads((ART/"gdt383_stage_a_result.json").read_text())
 freeze=json.loads((ART/"gdt383_stage_a_freeze.json").read_text())
 ck("result_content_hash",result["content_hash"]==content(result));ck("failed_stop",result["status"]=="STAGE_A_FAILED_STOP_BEFORE_VOYNICH")
 for section in ["inputs","outputs","documents","implementation"]:
  for p,h in result[section].items(): ck(section+":"+p,(ROOT/p).is_file() and sha(ROOT/p)==h)
 role=read("gdt383_role_recovery.tsv");res=read("gdt383_resolution_diagnostics.tsv");channels=read("gdt383_channel_treatments.tsv");controls=read("gdt383_realization_controls.tsv");overlap=read("gdt383_outcome_overlap.tsv");down=read("gdt383_downstream_transfer.tsv");null=read("gdt383_null_worlds.tsv")
 ck("role_rows",len(role)==30);ck("resolution_rows",len(res)==30);ck("channel_rows",len(channels)==126);ck("realization_rows",len(controls)==42);ck("overlap_rows",len(overlap)==40);ck("downstream_rows",len(down)==144);ck("null_rows",len(null)==1024)
 ck("role_key_coverage",len({(x["endpoint"],x["model"]) for x in role})==30);ck("channel_key_coverage",len({(x["endpoint"],x["channel"],x["treatment"]) for x in channels})==126);ck("selected_one_per_role",all(sum(x["selected_on_development"]=="1" for x in down if x["endpoint"]==e)==1 for e in ENDPOINTS))
 rmax=[float(x["world_max"]) for x in null if x["family"]=="ROLE_MEMBERSHIP"];dmax=[float(x["world_max"]) for x in null if x["family"]=="SELECTED_DOWNSTREAM"]
 ck("null_512_each",len(rmax)==len(dmax)==512)
 rg={}
 for e in ENDPOINTS:
  h=next(x for x in role if x["endpoint"]==e and x["model"]=="HIERARCHICAL_EVIDENCE");j=next(x for x in role if x["endpoint"]==e and x["model"]=="EXACT_JOINT_ONLY");u=next(x for x in role if x["endpoint"]==e and x["model"]=="STRICT_UNIVERSAL")
  p=(1+sum(v>=float(h["macro_auc"]) for v in rmax))/513
  ck("role_null_p:"+e,abs(p-float(h["max_family_p"]))<1e-12)
  rg[e]=float(h["macro_auc"])>=.80 and float(h["gain_bits"])>0 and int(h["positive_domains"])>=3 and float(h["macro_auc"])-float(j["macro_auc"])>=.02 and float(h["macro_auc"])-float(u["macro_auc"])>=.10 and p<=.05
 ck("role_gates",rg==result["role_gates"] and sum(rg.values())==2)
 ctrl_ok=len(controls)==42 and all(float(x["macro_auc"])>=.90 and float(x["gain_bits"])>0 for x in controls)
 ck("realization_gate",ctrl_ok==result["realization_gate_pass"] and result["realization_cells_passing"]==42)
 dg={}
 for e in ENDPOINTS:
  x=next(x for x in down if x["endpoint"]==e and x["selected_on_development"]=="1")
  p=(1+sum(v>=float(x["confirmation_total_gain_bits"]) for v in dmax))/513
  ck("downstream_null_p:"+e,abs(p-float(x["confirmation_max_family_p"]))<1e-12)
  conf=[float(q["source_only_auc"]) for q in overlap if q["outcome"]==x["outcome"] and q["domain"] in freeze["confirmation_domains"] and q["source_only_auc"]!="NA"]
  dg[e]=len(conf)==2 and sum(conf)/2<=.65 and float(x["confirmation_harleian_gain_bits"])>0 and float(x["confirmation_quinte_gain_bits"])>0 and p<=.05
 ck("downstream_gates",dg==result["downstream_gates"] and not any(dg.values()))
 # Independently reconstruct the observation census and every post-only outcome
 # count directly from the frozen encoded layer, without importing the runner.
 enc=ROOT/next(p for p in result["inputs"] if p.endswith("gdt382_voynichified_observation_layer.tsv.gz"));rows=[];bad=0
 with gzip.open(enc,"rt",encoding="utf-8",newline="") as f:
  for x in csv.DictReader(f,delimiter="\t"):
   rows.append(x);bad+=("f84" in (x["domain"]+x["collection_id"]+x["record_id"]+x["element_key"]).lower())
 ck("encoded_rows",len(rows)==result["rows"]==133183);ck("oracle_blind",{x["encoder_used_oracle"] for x in rows}=={"0"});ck("no_f84_provenance",bad==0)
 byrec=defaultdict(list)
 for x in rows: byrec[(x["domain"],x["collection_id"],x["record_id"])].append(x)
 counts=defaultdict(lambda:[0,0]);pivots=0
 for rr in byrec.values():
  rr.sort(key=lambda x:int(x["element_ordinal"]))
  for j in range(len(rr)-3):
   pivots+=1
   for name,v in outcomes(rr[j+1],rr[j+2],rr[j+3]).items(): counts[(name,rr[j]["domain"])][0]+=1;counts[(name,rr[j]["domain"])][1]+=v
 ck("records",len(byrec)==result["records"]==3235);ck("pivots",pivots==result["pivots"]==123478)
 for x in overlap:
  n,p=counts[(x["outcome"],x["domain"])];ck("outcome_count:"+x["outcome"]+":"+x["domain"],n==int(x["n"]) and p==int(x["positives"]))
 ck("stage_b_locked",not result["stage_a_pass"] and not result["voynich_stage_b_authorized"] and not result["voynich_stage_b_created"] and result["voynich_rows_read"]==0 and not result["voynich_scored"])
 ck("gdt381_not_read",not result["gdt381_target_artifacts_read"]);ck("f84_sealed",not any(result["f84"].values()))
 out={"schema":"GDT383_STAGE_A_VALIDATION_V1","status":"PASS" if all(v for _,v in checks) else "FAIL","checks":len(checks),"passed":sum(v for _,v in checks),"details":{k:v for k,v in checks},"result_hash":sha(ART/"gdt383_stage_a_result.json"),"validator_hash":sha(BASE/"src/validate_stage_a.py")}
 out["content_hash"]=content(out);(ART/"gdt383_stage_a_validation.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"status":out["status"],"passed":out["passed"],"checks":out["checks"]}))
 if out["status"]!="PASS": raise SystemExit(1)

if __name__=="__main__": main()
