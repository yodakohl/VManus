#!/usr/bin/env python3
"""Independent compact validation of GDT259 outputs and exact null arithmetic."""
import bisect,csv,hashlib,json
from collections import defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;checks=[]
def ck(n,x):checks.append((n,bool(x)));assert x,n
def read(p):
 with (R/p).open(encoding="utf-8") as f:return list(csv.DictReader(f,delimiter="\t"))
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def ge_pair_one(a,b,t):
 a=sorted(a);ge=0
 for z in b:
  for i,x in enumerate(a[:-1]):ge+=len(a)-max(i+1,bisect.bisect_left(a,t-z-x,i+1))
 return ge,len(a)*(len(a)-1)//2*len(b)
r=json.loads((R/"gdt259_result.json").read_text());a=read("gdt259_bridge_addresses.tsv");n=read("gdt259_null_results.tsv");c=read("gdt259_counterexamples.tsv")
ck("status",r["status"]=="THREE_BRIDGES_SKEW_LATE_WEAKLY_WITH_NO_COMMON_PARAGRAPH_OR_FIELD_ADDRESS");ck("three",len(a)==r["bridges"]==3);ck("surfaces",[x["member_surface"] for x in a]==["okaly","olky","okal"]);ck("paragraphs",[x["paragraph_id"] for x in a]==["P2","P3","P1"]);ck("lines",[x["paragraph_line_ordinal"] for x in a]==["4","5","6"]);ck("positions",[round(float(x["normalized_paragraph_position"]),3) for x in a]==[.6,.8,.625]);ck("two_hpr2",sum(x["hpr2_address_state"].startswith("EXACT") for x in a)==2);ck("field_difference",[(x["hpr2_field_ordinal"],x["field_end"]) for x in a]==[("1","DY"),("UNRESOLVED","UNRESOLVED"),("2","LINE_END")]);ck("zero_semantics",all(x["semantic_value"]=="UNASSIGNED" for x in a) and r["active_semantic_assignments"]==0);ck("counterexamples",len(c)==5)
# Reconstruct the null from the explicitly f80r/f82r-only projection.
p=read("gdt002_grammar_projection.tsv");ck("safe_pages",{x["page"] for x in p}=={"f80r","f82r"});coord={x["locus"]:x for fn in ("gdt244_f80r_paragraph_coordinate.tsv","gdt242_f82r_paragraph_coordinate.tsv") for x in read(fn)};by=defaultdict(dict)
for x in p:by[(x["page"],x["locus"],x["source_group_index"])][x["edition"]]=x
pool=defaultdict(list)
for (page,locus,gi),v in by.items():
 if set(v)!={"ZL3b","IT2a","RF1b"} or v["ZL3b"]["kind"]!="P" or locus not in coord:continue
 if int(gi) in {1,int(v["ZL3b"]["source_group_count"])}:continue
 o=int(coord[locus]["paragraph_line_ordinal"]);z=int(coord[locus]["paragraph_line_count"]);pool[page].append(((o-1)/(z-1),locus))
obs=sum(float(x["normalized_paragraph_position"]) for x in a);ge,total=ge_pair_one([x[0] for x in pool["f80r"]],[x[0] for x in pool["f82r"]],obs);lines={q:sorted({l:v for v,l in xs}.values()) for q,xs in pool.items()};ge2,total2=ge_pair_one(lines["f80r"],lines["f82r"],obs)
ck("pool_counts",(len(pool["f80r"]),len(pool["f82r"]))==(347,212));ck("group_worlds",(ge,total)==(int(n[0]["inclusive_tail_worlds"]),int(n[0]["worlds"])));ck("group_p",abs(ge/total-r["group_weighted_exact_p"])<1e-15);ck("line_worlds",(ge2,total2)==(int(n[1]["inclusive_tail_worlds"]),int(n[1]["worlds"])));ck("line_p",abs(ge2/total2-r["line_uniform_exact_p"])<1e-15);ck("weak",r["group_weighted_exact_p"]>.1 and r["line_uniform_exact_p"]>.1);ck("no_common",not r["common_paragraph_address"] and not r["common_hpr2_address"])
for k in ("inputs","outputs","documents","implementation"):
 for fn,h in r[k].items():ck(k+"_"+fn,sha(fn)==h)
core={k:v for k,v in r.items() if k!="content_hash"};ck("content_hash",hashlib.sha256(json.dumps(core,sort_keys=True,separators=(",",":")).encode()).hexdigest()==r["content_hash"]);ck("f84",r["f84r"]=={"prior_transient_parse_disclosed":True,"new_access":False,"used":False,"scored":False,"further_access_authorized":False})
out={"status":"PASS","checks_passed":len(checks),"checks_total":len(checks),"result_sha256":sha("gdt259_result.json"),"validation_scope":"Independent bridge address, corrected paragraph position, exact page-conditioned null, hashes, claim state, and f84r disclosure."};out["content_hash"]=hashlib.sha256(json.dumps(out,sort_keys=True,separators=(",",":")).encode()).hexdigest();(R/"gdt259_validation.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(f"PASS {len(checks)}/{len(checks)}")
