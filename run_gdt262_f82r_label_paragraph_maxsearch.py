#!/usr/bin/env python3
"""Calibrate the complete f82r four-member label/paragraph search."""
import csv,hashlib,json,math,random
from collections import defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;PROJ="gdt002_grammar_projection.tsv";COORD="gdt242_f82r_paragraph_coordinate.tsv";ACCESS="gdt257_result.json"
OUTS=["gdt262_label_window_atlas.tsv","gdt262_null_results.tsv","gdt262_counterexamples.tsv"];DOCS=["GDT262_F82R_LABEL_PARAGRAPH_MAXSEARCH_METHOD.md","GDT262_F82R_LABEL_PARAGRAPH_MAXSEARCH_REPORT.md"];EDS=["ZL3b","IT2a","RF1b"]
def read(p):
 with (R/p).open(encoding="utf-8") as f:return list(csv.DictReader(f,delimiter="\t"))
def write(p,rows):
 with (R/p).open("w",encoding="utf-8",newline="") as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def tail(K,m,k):return sum(math.comb(K,j)*math.comb(32-K,m-j) for j in range(k,min(K,m)+1) if 0<=m-j<=32-K)/math.comb(32,m) if m else 1.0
def main():
 p=read(PROJ);assert {x["page"] for x in p}=={"f80r","f82r"};c={x["locus"]:x for x in read(COORD)};lines=sorted(c,key=lambda z:int(z.split('.')[1]));ix={x:i for i,x in enumerate(lines)};p2={i for i,x in enumerate(lines) if c[x]["paragraph_id"]=="P2"};p3={i for i,x in enumerate(lines) if c[x]["paragraph_id"]=="P3"};assert (len(lines),len(p2),len(p3))==(32,9,14)
 atlas=[];nulls=[]
 for ei,ed in enumerate(EDS):
  lab=defaultdict(list);pro=defaultdict(list)
  for x in p:
   if x["page"]=="f82r" and x["edition"]==ed:(lab if x["kind"]=="L" else pro)[x["locus"]].append(x)
  tests=[];label_rows=[]
  for loc,xs in lab.items():
   seq=sum((x["primary_sta_codes"].split() for x in sorted(xs,key=lambda z:int(z["source_group_index"]))),[]);seen=set();local=[]
   for j in range(len(seq)-3):
    t=tuple(seq[j:j+4])
    if t in seen:continue
    seen.add(t);hit=set()
    for pl,ps in pro.items():
     for x in ps:
      q=x["primary_sta_codes"].split()
      if any(sum(a!=b for a,b in zip(t,q[k:k+4]))<=1 for k in range(len(q)-3)):hit.add(ix[pl])
    target=p2 if loc=="f82r.10" else p3;K=len(target);cnt=len(hit&target);pv=tail(K,len(hit),cnt);local.append((pv,j+1,t,hit,cnt));tests.append((target,K,hit,loc,j+1,t,pv))
   if local:
    best=min(local,key=lambda z:(z[0],z[1],z[2]));pv,j,t,hit,cnt=best
    label_rows.append({"edition":ed,"label_locus":loc,"target_paragraph":"P2" if loc=="f82r.10" else "P3","unique_four_member_windows":len(local),"best_window_ordinal":j,"best_window_codes":" ".join(t),"all_hit_lines":len(hit),"target_hit_lines":cnt,"best_local_p":f"{pv:.12f}","within_label_bonferroni_p":f"{min(1,pv*len(local)):.12f}","rank_within_reading":0,"semantic_value":"UNASSIGNED"})
  label_rows.sort(key=lambda z:(float(z["best_local_p"]),z["label_locus"]));
  for rank,x in enumerate(label_rows,1):x["rank_within_reading"]=rank
  atlas.extend(label_rows);assert len(tests)==32 and label_rows[0]["label_locus"]=="f82r.10"
  obs=min(x[6] for x in tests);arr=list(range(32));rng=random.Random(262000+ei);worlds=100000;ge=0
  for _ in range(worlds):
   rng.shuffle(arr);rp2=set(arr[:9]);rp3=set(arr[18:]);mn=1.0
   for target,K,hit,loc,j,t,pv in tests:
    k=len(hit&(rp2 if loc=="f82r.10" else rp3));mn=min(mn,tail(K,len(hit),k))
   ge+=mn<=obs+1e-15
  shifts=[]
  for s in range(32):
   mn=1.0
   for target,K,hit,loc,j,t,pv in tests:
    hs={(v+s)%32 for v in hit};mn=min(mn,tail(K,len(hit),len(hs&target)))
   shifts.append(mn)
  sg=sum(v<=obs+1e-15 for v in shifts)
  nulls.extend([
   {"edition":ed,"null":"UNCONSTRAINED_PARAGRAPH_ASSIGNMENT_MAX32","tests":32,"worlds":worlds,"observed_min_local_p":f"{obs:.12f}","inclusive_extreme_worlds":ge,"inclusive_maxT_p":f"{(ge+1)/(worlds+1):.12f}","preserves":"paragraph sizes only","interpretation":"ATTRACTIVE_BUT_DESTROYS_PAGE_ORDER"},
   {"edition":ed,"null":"CIRCULAR_LINE_SHIFT_MAX32","tests":32,"worlds":32,"observed_min_local_p":f"{obs:.12f}","inclusive_extreme_worlds":sg,"inclusive_maxT_p":f"{sg/32:.12f}","preserves":"line order clustering and opportunity","interpretation":"PRIMARY_TOPOLOGY_SENSITIVITY_NONCONFIRMING"},
   {"edition":ed,"null":"ANALYTIC_BONFERRONI_32","tests":32,"worlds":32,"observed_min_local_p":f"{obs:.12f}","inclusive_extreme_worlds":"NA","inclusive_maxT_p":f"{min(1,32*obs):.12f}","preserves":"none analytic bound","interpretation":"CONSERVATIVE_REFERENCE"}])
 write(OUTS[0],atlas);write(OUTS[1],nulls)
 counter=[
  {"counterexample":"TOPOLOGY_SHIFT_NULL","value":"ZL .3125 IT .28125 RF .40625","consequence":"physical clustering and line opportunity explain equally strong page minima"},
  {"counterexample":"INDEPENDENT_FOLIO_FAIL","value":"GDT261 f83r saiin 0/3 target lines; ol p=.88","consequence":"no general adjacent-paragraph transfer"},
  {"counterexample":"NO_EXACT_LEFT_COPY","value":"GDT260 exact distance-zero copies = 0","consequence":"lead depends on edit radius one"},
  {"counterexample":"FAMILY_CONTROL_BROAD","value":"ACAB line counts P1=2 P2=3 P3=4","consequence":"coarse construction family has no paragraph specificity"},
  {"counterexample":"EXPOSED_SEARCH","value":"13 labels and 32 windows scored after page exposure","consequence":"hypothesis ranking only"}]
 write(OUTS[2],counter);a=json.loads((R/ACCESS).read_text());assert a["access"]["pristine_access_seal"] is False
 best={ed:next(x for x in atlas if x["edition"]==ed and x["rank_within_reading"]==1) for ed in EDS};circ={x["edition"]:float(x["inclusive_maxT_p"]) for x in nulls if x["null"]=="CIRCULAR_LINE_SHIFT_MAX32"};rnd={x["edition"]:float(x["inclusive_maxT_p"]) for x in nulls if x["null"]=="UNCONSTRAINED_PARAGRAPH_ASSIGNMENT_MAX32"}
 result={"experiment":"GDT262_F82R_LABEL_PARAGRAPH_MAXSEARCH","status":"F82R10_UNIQUE_LABEL_WINDOW_LEAD_TOPOLOGY_PRESERVING_NULL_NONCONFIRMING","labels_per_reading":13,"four_member_windows_per_reading":32,"unique_best_label_all_readings":"f82r.10","observed_min_local_p":{ed:float(best[ed]["best_local_p"]) for ed in EDS},"unconstrained_maxT_p":rnd,"circular_shift_maxT_p":circ,"active_semantic_assignments":0,"interpretation":"f82r.10 is the unique strongest attached-label/paragraph member-window alignment, but physical-order-preserving shifts routinely yield equal or stronger page-wide minima; retain only a page-local clue.","claim_ceiling":"Exposed page-local max-search calibration only; no component name topic reference function object word language plaintext meaning or translation.","f84r":{"prior_transient_parse_disclosed":True,"new_access":False,"used":False,"scored":False,"further_access_authorized":False},"inputs":{x:sha(x) for x in [PROJ,COORD,ACCESS]},"outputs":{},"documents":{},"implementation":{Path(__file__).name:sha(Path(__file__).name)}}
 for x in OUTS:result["outputs"][x]=sha(x)
 for x in DOCS:result["documents"][x]=sha(x)
 result["content_hash"]=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(",",":")).encode()).hexdigest();(R/"gdt262_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":result["status"],"circular":circ,"random":rnd},sort_keys=True))
if __name__=="__main__":main()
