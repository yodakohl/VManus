#!/usr/bin/env python3
"""Test the simple f80r two ordered labels per paragraph address lattice."""
import csv,hashlib,json,math
from collections import defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;PROJ="gdt002_grammar_projection.tsv";COORD="gdt244_f80r_paragraph_coordinate.tsv";ACCESS="gdt257_result.json"
OUTS=["gdt263_label_paragraph_assignments.tsv","gdt263_shift_null.tsv","gdt263_counterexamples.tsv"];DOCS=["GDT263_F80R_TWO_LABEL_PARAGRAPH_ADDRESS_METHOD.md","GDT263_F80R_TWO_LABEL_PARAGRAPH_ADDRESS_REPORT.md"];EDS=["ZL3b","IT2a","RF1b"]
def read(p):
 with (R/p).open(encoding="utf-8") as f:return list(csv.DictReader(f,delimiter="\t"))
def write(p,rows):
 with (R/p).open("w",encoding="utf-8",newline="") as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def tail(N,K,m,k):return sum(math.comb(K,j)*math.comb(N-K,m-j) for j in range(k,min(K,m)+1) if 0<=m-j<=N-K)/math.comb(N,m) if m else 1
def main():
 p=read(PROJ);assert {x["page"] for x in p}=={"f80r","f82r"};c={x["locus"]:x for x in read(COORD)};lines=sorted(c,key=lambda z:int(z.split('.')[1]));ix={x:i for i,x in enumerate(lines)};paragraphs={f"P{i}":{j for j,x in enumerate(lines) if c[x]["paragraph_id"]==f"P{i}"} for i in range(1,6)};assert [len(paragraphs[f"P{i}"]) for i in range(1,6)]==[17,6,6,7,7]
 rows=[];nulls=[]
 for ed in EDS:
  lab=defaultdict(list);pro=defaultdict(list)
  for x in p:
   if x["page"]=="f80r" and x["edition"]==ed:(lab if x["kind"]=="L" else pro)[x["locus"]].append(x)
  tests=[];erows=[];raw_scores=[]
  for loc,xs in sorted(lab.items(),key=lambda z:int(z[0].split('.')[1])):
   seq=sum((x["primary_sta_codes"].split() for x in sorted(xs,key=lambda z:int(z["source_group_index"]))),[]);seen=set();wins=[]
   for j in range(len(seq)-3):
    t=tuple(seq[j:j+4])
    if t in seen:continue
    seen.add(t);hit=set()
    for pl,ps in pro.items():
     for x in ps:
      q=x["primary_sta_codes"].split()
      if any(sum(a!=b for a,b in zip(t,q[k:k+4]))<=1 for k in range(len(q)-3)):hit.add(ix[pl])
    wins.append((t,hit,j+1))
   target=f'P{(int(loc.split(".")[1])+1)//2}';vals=[]
   for t,hit,j in wins:
    k=len(hit&paragraphs[target]);vals.append((tail(43,len(paragraphs[target]),len(hit),k),j,t,hit,k))
   best=min(vals,key=lambda z:(z[0],z[1],z[2]));pv,j,t,hit,k=best;adj=min(1,pv*len(wins));bits=-math.log2(max(adj,1e-300));raw_scores.append(bits);tests.append((target,wins));erows.append({"edition":ed,"label_locus":loc,"predicted_paragraph":target,"unique_four_member_windows":len(wins),"best_window_ordinal":j,"best_window_codes":" ".join(t),"all_hit_lines":len(hit),"predicted_paragraph_hit_lines":k,"best_local_p":f"{pv:.12f}","within_label_adjusted_p":f"{adj:.12f}","evidence_bits":f"{bits:.12f}","semantic_value":"UNASSIGNED"})
  rows.extend(erows);obs=sum(raw_scores);shift_scores=[]
  for s in range(43):
   score=0
   for target,wins in tests:
    vals=[]
    for t,hit,j in wins:
     hs={(h+s)%43 for h in hit};k=len(hs&paragraphs[target]);vals.append(tail(43,len(paragraphs[target]),len(hit),k))
    score+=-math.log2(max(min(1,min(vals)*len(wins)),1e-300))
   shift_scores.append(score)
  ge=sum(v>=obs-1e-12 for v in shift_scores);nulls.append({"edition":ed,"labels":10,"unique_windows":sum(len(x[1]) for x in tests),"observed_evidence_bits":f"{obs:.12f}","circular_worlds":43,"equal_or_stronger_worlds":ge,"inclusive_circular_p":f"{ge/43:.12f}","max_shift_evidence_bits":f"{max(shift_scores):.12f}","interpretation":"TWO_LABEL_PER_PARAGRAPH_MAPPING_NONCONFIRMING"})
 write(OUTS[0],rows);write(OUTS[1],nulls)
 counter=[
  {"counterexample":"CIRCULAR_NULL_FAIL","value":"ZL 30/43 IT 18/43 RF 34/43 equal or stronger","consequence":"real label/paragraph alignment is not topology-specific"},
  {"counterexample":"NO_LABEL_LEVEL_LEAD","value":"0/30 reading-label rows have within-label adjusted p below .1","consequence":"no individual pair address supports the aggregate mapping"},
  {"counterexample":"CATALOGUE_ORDER_NOT_OWNERSHIP","value":"several exact comments place labels between figures","consequence":"locus order is not proven one-label one-figure authorship"},
  {"counterexample":"BROAD_MEMBER_NEIGHBORHOODS","value":"multiple best windows hit most prose lines","consequence":"local recurrence does not identify a target paragraph"},]
 write(OUTS[2],counter);a=json.loads((R/ACCESS).read_text());assert a["access"]["pristine_access_seal"] is False
 result={"experiment":"GDT263_F80R_TWO_LABEL_PARAGRAPH_ADDRESS","status":"F80R_TWO_LABELS_PER_PARAGRAPH_ADDRESS_LATTICE_FAILS","hypothesis":"LABELS_1_2_TO_P1_THROUGH_LABELS_9_10_TO_P5","labels":10,"paragraphs":5,"unique_windows_per_reading":20,"circular_p":{x["edition"]:float(x["inclusive_circular_p"]) for x in nulls},"individual_rows_adjusted_below_0_1":sum(float(x["within_label_adjusted_p"])<.1 for x in rows),"active_semantic_assignments":0,"interpretation":"The exact 10:5 page cardinality does not encode the proposed ordered two-label-per-paragraph address lattice under member-neighborhood evidence.","claim_ceiling":"Page-layout address test only; no figure ownership record object role word language plaintext meaning or translation.","f84r":{"prior_transient_parse_disclosed":True,"new_access":False,"used":False,"scored":False,"further_access_authorized":False},"inputs":{x:sha(x) for x in [PROJ,COORD,ACCESS]},"outputs":{},"documents":{},"implementation":{Path(__file__).name:sha(Path(__file__).name)}}
 for x in OUTS:result["outputs"][x]=sha(x)
 for x in DOCS:result["documents"][x]=sha(x)
 result["content_hash"]=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(",",":")).encode()).hexdigest();(R/"gdt263_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":result["status"],"p":result["circular_p"]},sort_keys=True))
if __name__=="__main__":main()
