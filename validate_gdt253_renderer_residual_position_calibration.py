#!/usr/bin/env python3
"""Independent source reconstruction for GDT253; does not import the scorer."""
import csv, hashlib, json, random
from collections import Counter, defaultdict
from pathlib import Path

R=Path(__file__).resolve().parent
A="experiments/semantic_assumptions/results/special_circle_text_blind_array_inventory.tsv"
O="gdt235_label_object_inventory.tsv"
G="experiments/semantic_assumptions/results/source_sta_group_alignment.tsv"
RES="gdt253_result.json"; EDITIONS=("ZL3b","IT2a","RF1b"); WORLDS=65536
checks=[]
def ck(name,x): checks.append((name,bool(x))); assert x,name
def sha(p): return hashlib.sha256((R/p).read_bytes()).hexdigest()
def rd(p):
 with (R/p).open(encoding="utf-8") as f:return list(csv.DictReader(f,delimiter="\t"))
def mx(rows):
 d=defaultdict(set)
 for r in rows:d[(r["sig"],r["res"],r["slot"])].add(r["folio"])
 return max(map(len,d.values()),default=0)
def world(rows,mode,rng):
 z=[dict(r) for r in rows];q=defaultdict(list)
 for i,r in enumerate(z):q[r["array"]].append(i)
 for ix in q.values():
  if mode.startswith("INDEPENDENT"):
   a=[z[i]["sig"] for i in ix];b=[z[i]["res"] for i in ix];rng.shuffle(a);rng.shuffle(b)
   for j,i in enumerate(ix):z[i]["sig"],z[i]["res"]=a[j],b[j]
  else:
   a=[(z[i]["sig"],z[i]["res"]) for i in ix];rng.shuffle(a)
   for j,i in enumerate(ix):z[i]["sig"],z[i]["res"]=a[j]
 return z
def main():
 arr=rd(A);obj={r["locus"]:r for r in rd(O)};ga=defaultdict(lambda:defaultdict(list))
 allowed={a["locus"] for a in arr if a["slot_count"]=="10" and a["locus"] in obj and obj[a["locus"]]["transferred_prefix"]!="NONE"}
 for r in rd(G):
  if r["locus"] in allowed:ga[r["locus"]][r["edition"]].append(r)
 ck("source_guard_no_f84",all(not x.startswith("f84") for x in allowed))
 by=defaultdict(list)
 for a in arr:
  if a["locus"] not in allowed:continue
  o=obj[a["locus"]];k=len(o["transferred_prefix"])
  for ed in EDITIONS:
   gs=sorted(ga[a["locus"]].get(ed,[]),key=lambda x:int(x["source_group_index"]));codes=[]
   for g in gs:codes+=g["primary_sta_codes"].split()
   if len(codes)<k:continue
   by[ed].append({"array":a["array_id"],"folio":a["physical_folio"],"locus":a["locus"],"slot":int(a["slot_index"]),"sig":" ".join(codes[:k]),"res":o["strict_residual"]})
 result=json.loads((R/RES).read_text())
 ck("status",result["status"]=="GDT252_POSITION_LEAD_MAXT_BORDERLINE_AND_RF_READING_UNSTABLE_NO_POSITION_KEY")
 ck("row_counts",{e:len(by[e]) for e in EDITIONS}==result["eligible_rows_by_edition"])
 ck("observed",mx(by["ZL3b"])==2 and mx(by["IT2a"])==2 and mx(by["RF1b"])==1)
 for ed in EDITIONS:
  key=defaultdict(list)
  for r in by[ed]:key[(r["sig"],r["res"])].append(r)
  recurrent=[z for z in key.values() if len({x["folio"] for x in z})>=2]
  ck("recurrent_"+ed,len(recurrent)==(1 if ed in ("ZL3b","IT2a") else 0))
 null=rd("gdt253_null_results.tsv")
 for ei,ed in enumerate(EDITIONS):
  for mi,mode in enumerate(("INDEPENDENT_RENDERER_RESIDUAL_WITHIN_ARRAY","WHOLE_PAIR_POSITION_WITHIN_ARRAY")):
   rng=random.Random(253000+ei*100+mi);hist=Counter();obs=mx(by[ed])
   for _ in range(WORLDS):hist[mx(world(by[ed],mode,rng))]+=1
   got=next(r for r in null if r["edition"]==ed and r["null_model"]==mode)
   ck("null_hist_"+ed+"_"+str(mi),json.loads(got["null_score_histogram"])=={str(k):v for k,v in sorted(hist.items())})
   ge=sum(v for k,v in hist.items() if k>=obs)
   ck("null_p_"+ed+"_"+str(mi),abs(float(got["inclusive_p"])-(ge+1)/(WORLDS+1))<5e-13)
 ck("candidate_reading_sensitivity",result["gdt252_pair_exact_member_support_readings"]==["ZL3b","IT2a"] and result["gdt252_pair_failed_exact_member_readings"]==["RF1b"])
 ck("f84_flags",not any(result["f84"].values()))
 for p,h in result["inputs"].items():ck("input_hash_"+p,sha(p)==h)
 for p,h in result["outputs"].items():ck("output_hash_"+p,sha(p)==h)
 for p,h in result["documents"].items():ck("doc_hash_"+p,sha(p)==h)
 for p,h in result["implementation"].items():ck("impl_hash_"+p,sha(p)==h)
 core={k:v for k,v in result.items() if k!="content_hash"};ck("content_hash",hashlib.sha256(json.dumps(core,sort_keys=True,separators=(",",":")).encode()).hexdigest()==result["content_hash"])
 out={"status":"PASS","checks_passed":len(checks),"checks_total":len(checks),"result_sha256":sha(RES),"validation_scope":"Independent source join, alternate-reading signatures, max statistic, both 65,536-world nulls, hashes, and claim state."}
 out["content_hash"]=hashlib.sha256(json.dumps(out,sort_keys=True,separators=(",",":")).encode()).hexdigest();(R/"gdt253_validation.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print(f"PASS {len(checks)}/{len(checks)}")
if __name__=="__main__":main()
