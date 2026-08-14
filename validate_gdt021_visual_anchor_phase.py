#!/usr/bin/env python3
"""Independent reconstruction of the GDT021 exact matched atlas."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RES=ROOT/"gdt021_result.json";VAL=ROOT/"gdt021_validation.json"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(n):
 with (ROOT/n).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def hg(n,k,m):
 d=math.comb(n,m);return{x:Fraction(math.comb(k,x)*math.comb(n-k,m-x),d)for x in range(max(0,m-(n-k)),min(m,k)+1)}
def exact(keys,pos,ctx,outcome,exclude=None):
 strata=defaultdict(list)
 for key in keys:
  x=ctx[key]
  if exclude and x["folio"]==exclude:continue
  strata[(x["page"],x["state"],x["bin"])].append((key in pos,x[outcome]))
 dist={0:Fraction(1)};obs=0;exp=Fraction();num=den=0.;ns=0
 for v in strata.values():
  n=len(v);m=sum(a for a,y in v);k=sum(y for a,y in v)
  if not(0<m<n and 0<k<n):continue
  ns+=1;o=sum(a and y for a,y in v);obs+=o;exp+=Fraction(m*k,n);w=m*(n-m)/n;num+=w*(o/m-(k-o)/(n-m));den+=w;new=defaultdict(Fraction)
  for a,pa in dist.items():
   for b,pb in hg(n,k,m).items():new[a+b]+=pa*pb
  dist=new
 if not den:return 0.,1.,0,0.,0,0
 delta=abs(Fraction(obs)-exp);p=sum(prob for value,prob in dist.items()if abs(Fraction(value)-exp)>=delta);return num/den,float(p),obs,float(exp),ns,len(dist)
def close(a,b):return abs(float(a)-float(b))<7e-12
def main():
 checks=[];result=json.loads(RES.read_text());copy=dict(result);digest=copy.pop("result_content_sha256");checks+=[("schema",result["schema"]=="GDT021_VISUAL_ANCHOR_PHASE_RESULT_V1"),("content",digest==csha(copy))]
 for part in("inputs","implementation","outputs"):
  for n,d in result[part].items():checks.append((part+":"+n,sha(ROOT/n)==d))
 inv=read("gdt016_group_state_inventory.tsv");anchors=read("gdt013_prose_anchor_occurrences.tsv");checks.append(("f84_guard",not any(r["locus"].startswith("f84r")for r in inv+anchors)));by=defaultdict(list);row_lookup={}
 for r in inv:by[r["locus"]].append(r);row_lookup[(r["locus"],int(r["group_index"]))]=r
 ctx={};prev={}
 for locus,line in by.items():
  line.sort(key=lambda r:int(r["group_index"]));seen=after=0;future=[0]*len(line);has=0
  for i in range(len(line)-1,-1,-1):has=max(has,int(line[i]["record_state"]=="DY_RESOLUTION"));future[i]=has
  for i,r in enumerate(line):
   frac=(int(r["group_index"])-1)/(int(r["group_count"])-1)if int(r["group_count"])>1 else.5;key=(locus,int(r["group_index"]));ctx[key]={"page":r["page"],"folio":r["physical_folio"],"state":r["record_state"],"bin":min(3,int(frac*4)),"SEEN_DY":seen,"IMMEDIATE_POST_DY":after,"CLOSED_FIELD":future[i],"LINE_FINAL":int(i==len(line)-1)};prev[key]=line[i-1]["token"]if i else"LINE_START";after=int(r["record_state"]=="DY_RESOLUTION");seen=max(seen,after)
 roles=sorted({r["role_hypothesis"]for r in anchors});scopes=("UNION","SOURCE_FAMILY","RESIDUAL_HOST");outcomes=("SEEN_DY","IMMEDIATE_POST_DY","CLOSED_FIELD","LINE_FINAL");stored={(r["scope"],r["visual_anchor_role"],r["field_context"]):r for r in read("gdt021_visual_anchor_phase_atlas.tsv")}
 for scope in scopes:
  rows=anchors if scope=="UNION"else[r for r in anchors if r["anchor_model"]==scope];keys={(r["locus"],int(r["group_index"]))for r in rows};folios=sorted({ctx[k]["folio"]for k in keys})
  for role in roles:
   pos={(r["locus"],int(r["group_index"]))for r in rows if r["role_hypothesis"]==role}
   for outcome in outcomes:
    e,p,o,x,n,s=exact(keys,pos,ctx,outcome);lofo=[exact(keys,pos,ctx,outcome,f)[0]for f in folios];r=stored[(scope,role,outcome)];checks.append(("test:"+scope+":"+role+":"+outcome,close(r["conditional_effect"],e)and close(r["exact_p"],p)and int(r["observed_role_outcomes"])==o and close(r["expected_role_outcomes"],x)and int(r["informative_strata"])==n and int(r["exact_distribution_support"])==s and int(r["lofo_positive_effects"])==sum(v>0 for v in lofo)and close(r["lofo_min_effect"],min(lofo))and close(r["lofo_max_effect"],max(lofo))))
 primary=min(stored.values(),key=lambda r:(float(r["exact_p"]),-abs(float(r["conditional_effect"]))));rp=result["primary"];checks+=[("grid",len(stored)==result["tests"]==96),("primary",primary["scope"]==rp["scope"]and primary["visual_anchor_role"]==rp["visual_anchor_role"]and primary["field_context"]==rp["field_context"]and close(primary["exact_p"],rp["exact_p"])and close(primary["conditional_effect"],rp["conditional_effect"])and int(primary["observed_role_outcomes"])==int(rp["observed_role_outcomes"])),("counts",len(anchors)==result["anchor_rows"]==2860 and len({(r["locus"],int(r["group_index"]))for r in anchors})==result["union_groups"]==1502)]
 af=defaultdict(lambda:{"models":set(),"features":set()})
 for r in anchors:
  if r["role_hypothesis"]=="FIGURE":k=(r["locus"],int(r["group_index"]));af[k]["models"].add(r["anchor_model"]);af[k]["features"].add(r["formal_feature"])
 expected=[]
 for k in sorted(af):
  if ctx[k]["IMMEDIATE_POST_DY"]:r=row_lookup[k];expected.append((k[0],k[1],prev[k],r["token"],r["family_surface"],r["record_state"],"|".join(sorted(af[k]["models"])),"|".join(sorted(af[k]["features"]))))
 exported=read("gdt021_figure_postdy_examples.tsv");actual=[(r["locus"],int(r["group_index"]),r["previous_dy_token"],r["target_token"],r["target_family"],r["record_state"],r["anchor_models"],r["anchor_features"])for r in exported];checks+=[("examples",actual==expected and len(actual)==result["figure_postdy_examples"]==49),("ledger",(ROOT/"GDT002_YOLO_LEDGER.tsv").read_text().count("GDT021_CKPT001")==1),("f84_flags",result["f84r"]=={"input_contains_rows":False,"opened":False,"retained":False,"joined":False,"scored":False})]
 report=(ROOT/"GDT021_VISUAL_ANCHOR_PHASE_REPORT.md").read_text().lower();checks.append(("claims",all(x in report for x in("no prose occurrence is assigned figure meaning","equally live null","no semantic role","f84r was not opened"))))
 failures=[n for n,ok in checks if not ok];v={"schema":"GDT021_VISUAL_ANCHOR_PHASE_VALIDATION_V1","status":"PASS"if not failures else"FAIL","checks":len(checks),"failures":failures,"result_sha256":sha(RES),"validator_sha256":sha(Path(__file__)),"scope":"Independent reconstruction from frozen f84r-free inputs of all 96 exact page+state+position tests, every leave-one-folio effect, primary ordering, 49 examples, hashes, ledger, and claims."};VAL.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n");print(json.dumps(v,sort_keys=True));
 if failures:raise SystemExit(1)
if __name__=="__main__":main()
