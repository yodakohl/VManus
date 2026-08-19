#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];BASE=ROOT/"experiments/yolo/gdt383_repaired_local_role_transfer";ART=BASE/"artifacts"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def content(d):q=dict(d);q.pop("content_hash",None);return hashlib.sha256(json.dumps(q,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def main():
 d=json.loads((ART/"gdt383_stage_a_freeze.json").read_text());c=[]
 def ck(n,v):c.append((n,bool(v)))
 ck("content_hash",d["content_hash"]==content(d));ck("status",d["status"]=="FROZEN_BEFORE_POSITIVE_CONTROL_EVALUATION");ck("six_roles",len(d["endpoints"])==6);ck("five_resolutions",len(d["resolutions"])==5);ck("eight_post_outcomes",len(d["post_only_outcomes"])==8);ck("seven_channels",len(d["grammar_channels"])==7);ck("three_treatments",len(d["channel_treatments"])==3);ck("seven_modes",len(d["realization_modes"])==7);ck("leakage_ceiling",d["leakage_ceiling_source_only_auc"]==.65);ck("512_worlds",d["null"]["worlds"]==512);ck("disjoint",d["source_x"]=="PIVOT_AND_PRE_PIVOT_ONLY" and d["outcome_y"]=="STRICTLY_J_PLUS_1_TO_J_PLUS_3_ONLY");ck("gdt381_forbidden",not d["gdt381_target_artifacts_allowed"]);ck("stage_b_locked",not d["voynich_stage_b_authorized"] and d["voynich_rows_read"]==0);ck("f84_false",not any(d["f84"].values()))
 for grp in ["inputs","documents","implementation"]:
  def walk(x):
   for k,v in x.items():
    if isinstance(v,dict):yield from walk(v)
    else:yield k,v
  for p,h in walk(d[grp]):
   ck("hash:"+p,sha(ROOT/p)==h)
 out={"schema":"GDT383_STAGE_A_FREEZE_VALIDATION_V1","status":"PASS" if all(v for _,v in c) else "FAIL","checks":len(c),"passed":sum(v for _,v in c),"details":dict(c),"freeze_hash":sha(ART/"gdt383_stage_a_freeze.json")};out["content_hash"]=content(out);(ART/"gdt383_stage_a_freeze_validation.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":out["status"],"passed":out["passed"],"checks":out["checks"]}));
 if out["status"]!="PASS":raise SystemExit(1)
if __name__=="__main__":main()
