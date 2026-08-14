#!/usr/bin/env python3
"""Independent nonimporting validation of GDT023."""
from __future__ import annotations
import csv, hashlib, json, math
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent; RES=ROOT/"gdt023_result.json"; VAL=ROOT/"gdt023_validation.json"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v): return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(n):
 with (ROOT/n).open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def has(r,m,f):
 if f.startswith("FAMILY_EXACT:"):return m=="SOURCE_FAMILY"and r["family_surface"]==f.split(":",1)[1]
 if f.startswith("HOST_EXACT:"):return m=="RESIDUAL_HOST"and r["residual_host"]==f.split(":",1)[1]
 tag,text=("F",r["family_surface"])if m=="SOURCE_FAMILY"else("H",r["residual_host"])
 if not f.startswith(tag):return False
 n=int(f[1:f.index(":")]);x=f.split(":",1)[1];p="^"+text+"$";return any(p[i:i+n]==x for i in range(len(p)-n+1))
def pmf(n,k,m):
 a=np.zeros(min(m,k)+1);d=math.comb(n,m)
 for x in range(max(0,m-(n-k)),min(m,k)+1):a[x]=math.comb(k,x)*math.comb(n-k,m-x)/d
 return a
def score(keys,pos,ctx,omit=None,prob=True):
 strata=defaultdict(list)
 for k in keys:
  x=ctx[k]
  if omit and x["folio"]==omit:continue
  strata[(x["page"],x["state"],x["bin"])].append((k in pos,x["post"]))
 law=np.array([1.]);obs=0;exp=num=den=0.;ns=0
 for v in strata.values():
  n=len(v);m=sum(a for a,y in v);k=sum(y for a,y in v)
  if not(0<m<n and 0<k<n):continue
  ns+=1;o=sum(a and y for a,y in v);obs+=o;exp+=m*k/n;w=m*(n-m)/n;num+=w*(o/m-(k-o)/(n-m));den+=w
  if prob:law=np.convolve(law,pmf(n,k,m))
 effect=num/den if den else 0.;p=1.
 if prob and den:
  d=abs(obs-exp);p=min(1.,float(law[np.abs(np.arange(len(law))-exp)>=d-1e-12].sum()))
 return effect,p,obs,exp,ns
def close(a,b):return abs(float(a)-float(b))<7e-12
def main():
 checks=[];r=json.loads(RES.read_text());body=dict(r);digest=body.pop("result_content_sha256");checks+=[("schema",r["schema"]=="GDT023_ANCHOR_SPECIFICITY_PHASE_RESULT_V1"),("content",digest==csha(body))]
 for part in("inputs","implementation","outputs"):
  for n,d in r[part].items():checks.append((part+":"+n,sha(ROOT/n)==d))
 inv=read("gdt016_group_state_inventory.tsv");anchors=read("gdt013_role_anchors.tsv");checks+=[("counts",len(inv)==15592 and len(anchors)==80),("f84",not any(x["locus"].startswith("f84r")for x in inv))]
 lookup={(x["locus"],int(x["group_index"])):x for x in inv};lines=defaultdict(list)
 for x in inv:lines[x["locus"]].append(x)
 ctx={};prev={}
 for loc,line in lines.items():
  line.sort(key=lambda x:int(x["group_index"]));after=0
  for i,x in enumerate(line):
   n=int(x["group_count"]);z=(int(x["group_index"])-1)/(n-1)if n>1 else.5;k=(loc,int(x["group_index"]));ctx[k]={"page":x["page"],"folio":x["physical_folio"],"state":x["record_state"],"bin":min(3,int(z*4)),"post":after};prev[k]=line[i-1]if i else None;after=int(x["record_state"]=="DY_RESOLUTION")
 roles=defaultdict(set);matches={}
 for a in anchors:
  pair=(a["selected_model"],a["formal_feature"]);roles[pair].add(a["role"]);matches[pair]={k for k,x in lookup.items()if has(x,*pair)};checks.append(("total:"+":".join(pair),len(matches[pair])==int(a["prose_occurrence_total"])))
 fig=sorted(p for p,v in roles.items()if"FIGURE"in v);q=("SOURCE_FAMILY","F3:QJB");k=("RESIDUAL_HOST","H3:kal");o=("RESIDUAL_HOST","HOST_EXACT:okal")
 specs=[("FIGURE_ALL_10",fig),("FIGURE_ROLE_UNIQUE",[p for p in fig if len(roles[p])==1]),("FIGURE_ROLE_SHARED",[p for p in fig if len(roles[p])>1]),("FIGURE_WITHOUT_QJB",[p for p in fig if p!=q]),("FIGURE_WITHOUT_KAL_OR_OKAL",[p for p in fig if p not in(k,o)]),("FIGURE_WITHOUT_QJB_KAL_OKAL",[p for p in fig if p not in(q,k,o)]),("QJB_ONLY",[q]),("KAL_ONLY",[k]),("OKAL_ONLY",[o])]
 stored={x["test_id"]:x for x in read("gdt023_anchor_ablation_tests.tsv")};folios=sorted({x["physical_folio"]for x in inv});allkeys=set(lookup)
 for name,fs in specs:
  pos=set().union(*(matches[p]for p in fs))if fs else set();e,p,ob,ex,ns=score(allkeys,pos,ctx);lo=[score(allkeys,pos,ctx,f,False)[0]for f in folios];x=stored[name]
  checks.append(("ablation:"+name,int(x["feature_count"])==len(fs)and int(x["full_occurrences"])==len(pos)and close(x["conditional_effect"],e)and close(x["exact_p"],p)and int(x["observed_postdy"])==ob and close(x["expected_postdy"],ex)and int(x["informative_strata"])==ns and int(x["lofo_positive_effects"])==sum(v>0 for v in lo)and close(x["lofo_min_effect"],min(lo))and close(x["lofo_max_effect"],max(lo))))
 checks+=[("ablation_count",len(stored)==r["ablation_tests"]==9),("figure_counts",len(fig)==r["figure_anchor_features"]==10 and sum(roles[p]=={"FIGURE"}for p in fig)==r["figure_unique_features"]==1),("overlap",len(matches[q]&matches[k])==r["qjb_kal_overlap"]==0)]
 overlap={(x["anchor_model"],x["formal_feature"]):x for x in read("gdt023_figure_anchor_role_overlap.tsv")}
 for pair in fig:
  x=overlap[pair];checks.append(("role_overlap:"+":".join(pair),x["selected_for_roles"]=="|".join(sorted(roles[pair]))and int(x["selected_role_count"])==len(roles[pair])and int(x["figure_channel_unique"])==int(roles[pair]=={"FIGURE"})and int(x["complete_prose_occurrences"])==len(matches[pair])))
 summary={x["branch"]:x for x in read("gdt023_postdy_branch_summary.tsv")};branches=[("QJB",q,matches[q]),("KAL",k,matches[k]),("OKAL",o,matches[o]),("KAL_NON_OKAL",k,matches[k]-matches[o])]
 expected_examples=set()
 for name,pair,keys in branches:
  post={key for key in keys if ctx[key]["post"]};states=Counter(lookup[key]["record_state"]for key in keys);prefix=Counter(lookup[key]["stripped_prefix"]for key in keys);x=summary[name]
  checks.append(("branch:"+name,int(x["occurrences"])==len(keys)and int(x["postdy_occurrences"])==len(post)and int(x["physical_folios"])==len({lookup[key]["physical_folio"]for key in keys})and int(x["dy_resolution_occurrences"])==states["DY_RESOLUTION"]and int(x["al_state_occurrences"])==states["AL_STATE"]and int(x["q_prefix_occurrences"])==prefix["q"]and int(x["no_prefix_occurrences"])==prefix["NONE"]))
  expected_examples|={(name,key[0],key[1],lookup[key]["token"],prev[key]["token"])for key in post}
 actual={(x["branch"],x["locus"],int(x["group_index"]),x["target_token"],x["previous_dy_token"])for x in read("gdt023_postdy_branch_examples.tsv")};checks.append(("examples",actual==expected_examples))
 report=" ".join((ROOT/"GDT023_ANCHOR_SPECIFICITY_PHASE_REPORT.md").read_text().lower().split());ledger=(ROOT/"GDT002_YOLO_LEDGER.tsv").read_text();checks+=[("claims",all(t in report for t in("not figure-specific","zero groups","speculative","f84r was not opened","no figure"))),("f84_flags",r["f84r"]=={"input_contains_rows":False,"opened":False,"retained":False,"joined":False,"scored":False}),("ledger",ledger.count("GDT023_CKPT001")==1)]
 fail=[n for n,ok in checks if not ok];v={"schema":"GDT023_ANCHOR_SPECIFICITY_PHASE_VALIDATION_V1","status":"PASS"if not fail else"FAIL","checks":len(checks),"failures":fail,"result_sha256":sha(RES),"validator_sha256":sha(Path(__file__)),"scope":"Independent nonimporting reconstruction of anchor-role overlap, nine complete-census ablations, all LOFO effects, QJB/KAL/OKAL branches, concrete examples, hashes, f84r exclusion, ledger, and claims."};VAL.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n");print(json.dumps(v,sort_keys=True));
 if fail:raise SystemExit(1)
if __name__=="__main__":main()
