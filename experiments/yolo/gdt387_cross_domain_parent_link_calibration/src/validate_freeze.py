#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];BASE=ROOT/"experiments/yolo/gdt387_cross_domain_parent_link_calibration";ART=BASE/"artifacts";P=ART/"gdt387_pre_score_freeze.json"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
c=[]
def ck(n,x):assert x,n;c.append(n)
r=json.loads(P.read_text());q=dict(r);h=q.pop("content_hash");ck("content",h==hashlib.sha256(json.dumps(q,sort_keys=True,separators=(",",":")).encode()).hexdigest())
for p,h in r["inputs"].items():ck("input:"+p,sha(ROOT/p)==h)
for p,h in r["documents"].items():ck("document:"+p,sha(ROOT/p)==h)
for p,h in r["implementation"].items():ck("implementation:"+p,sha(ROOT/p)==h)
ck("source",r["source"]["commit"]=="bf79d1c46e8ef983a7347b0664d0d80243f32831" and r["source"]["parsed_files"]==84)
ck("capacity",r["sampling"]["observation_pceec2_rows"]==27518 and r["sampling"]["hidden_role_pivots"]==110 and r["sampling"]["hidden_role_files"]==47)
ck("gate",r["gate"]=={"governor_gain_positive":True,"maximum_p":0.05,"minimum_mobile_fraction":0.2,"minimum_positive_files":42,"minimum_role_auc":0.65,"minimum_role_files":40,"minimum_role_pivots":100,"minimum_target_mrr_delta":0.0,"role_gain_positive":True})
ck("no_target",r["voynich_rows_authorized"]==0 and not any(r["f84"].values()))
out={"schema":"GDT387_FREEZE_VALIDATION_V1","status":"PASS","checks_passed":len(c),"checks_total":len(c),"checks":c,"freeze_hash":sha(P)};(ART/"gdt387_pre_score_freeze_validation.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(f"PASS {len(c)}/{len(c)}")
