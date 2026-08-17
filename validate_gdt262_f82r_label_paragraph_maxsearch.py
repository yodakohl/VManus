#!/usr/bin/env python3
import csv,hashlib,json,math
from pathlib import Path
R=Path(__file__).resolve().parent;checks=[]
def ck(n,x):checks.append((n,bool(x)));assert x,n
def read(p):
 with (R/p).open(encoding="utf-8") as f:return list(csv.DictReader(f,delimiter="\t"))
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def tail(K,m,k):return sum(math.comb(K,j)*math.comb(32-K,m-j) for j in range(k,min(K,m)+1) if 0<=m-j<=32-K)/math.comb(32,m) if m else 1
r=json.loads((R/"gdt262_result.json").read_text());a=read("gdt262_label_window_atlas.tsv");n=read("gdt262_null_results.tsv");c=read("gdt262_counterexamples.tsv")
ck("status",r["status"]=="F82R10_UNIQUE_LABEL_WINDOW_LEAD_TOPOLOGY_PRESERVING_NULL_NONCONFIRMING");ck("atlas",len(a)==39);ck("labels",all(len([x for x in a if x["edition"]==ed])==13 for ed in ("ZL3b","IT2a","RF1b")));ck("best",all(next(x for x in a if x["edition"]==ed and x["rank_within_reading"]=="1")["label_locus"]=="f82r.10" for ed in ("ZL3b","IT2a","RF1b")));ck("windows",all(sum(int(x["unique_four_member_windows"]) for x in a if x["edition"]==ed)==32 for ed in ("ZL3b","IT2a","RF1b")));ck("null_rows",len(n)==9);ck("circ",r["circular_shift_maxT_p"]=={"ZL3b":.3125,"IT2a":.28125,"RF1b":.40625});ck("random",all(0<float(r["unconstrained_maxT_p"][ed])<.05 for ed in r["unconstrained_maxT_p"]));ck("counter",len(c)==5);ck("zero_semantics",all(x["semantic_value"]=="UNASSIGNED" for x in a) and r["active_semantic_assignments"]==0)
# Recompute every exact circular-shift minimum from the exported fixed tests by
# rebuilding source masks, independently of the producer's stored null rows.
p=read("gdt002_grammar_projection.tsv");coord={x["locus"]:x for x in read("gdt242_f82r_paragraph_coordinate.tsv")};lines=sorted(coord,key=lambda z:int(z.split('.')[1]));ix={x:i for i,x in enumerate(lines)};p2={i for i,x in enumerate(lines) if coord[x]["paragraph_id"]=="P2"};p3={i for i,x in enumerate(lines) if coord[x]["paragraph_id"]=="P3"}
for ed in ("ZL3b","IT2a","RF1b"):
 lab={};pro={}
 for x in p:
  if x["page"]!="f82r" or x["edition"]!=ed:continue
  (lab if x["kind"]=="L" else pro).setdefault(x["locus"],[]).append(x)
 tests=[]
 for loc,xs in lab.items():
  seq=sum((x["primary_sta_codes"].split() for x in sorted(xs,key=lambda z:int(z["source_group_index"]))),[]);seen=set()
  for j in range(len(seq)-3):
   t=tuple(seq[j:j+4])
   if t in seen:continue
   seen.add(t);hit=set()
   for pl,ps in pro.items():
    if any(any(sum(a!=b for a,b in zip(t,q["primary_sta_codes"].split()[k:k+4]))<=1 for k in range(len(q["primary_sta_codes"].split())-3)) for q in ps):hit.add(ix[pl])
   target=p2 if loc=="f82r.10" else p3;tests.append((target,len(target),hit))
 vals=[]
 for s in range(32):vals.append(min(tail(K,len(hit),len({(v+s)%32 for v in hit}&target)) for target,K,hit in tests))
 obs=vals[0];got=sum(v<=obs+1e-15 for v in vals)/32;ck("rebuild_circ_"+ed,abs(got-r["circular_shift_maxT_p"][ed])<1e-15)
for k in ("inputs","outputs","documents","implementation"):
 for fn,h in r[k].items():ck(k+"_"+fn,sha(fn)==h)
core={k:v for k,v in r.items() if k!="content_hash"};ck("content_hash",hashlib.sha256(json.dumps(core,sort_keys=True,separators=(",",":")).encode()).hexdigest()==r["content_hash"]);ck("f84",r["f84r"]=={"prior_transient_parse_disclosed":True,"new_access":False,"used":False,"scored":False,"further_access_authorized":False})
o={"status":"PASS","checks_passed":len(checks),"checks_total":len(checks),"result_sha256":sha("gdt262_result.json"),"validation_scope":"Label/window census, unique best row, exact topology-preserving max-search, hashes, claim state, and f84r disclosure."};o["content_hash"]=hashlib.sha256(json.dumps(o,sort_keys=True,separators=(",",":")).encode()).hexdigest();(R/"gdt262_validation.json").write_text(json.dumps(o,indent=2,sort_keys=True)+"\n");print(f"PASS {len(checks)}/{len(checks)}")
