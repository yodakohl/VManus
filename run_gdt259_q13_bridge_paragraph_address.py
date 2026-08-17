#!/usr/bin/env python3
"""Test whether the three exact q13 label/prose bridges share an address."""
import bisect,csv,hashlib,itertools,json
from collections import defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent
MATCH="gdt247_exact_label_prose_member_matches.tsv"
PROJ="gdt002_grammar_projection.tsv"
C80="gdt244_f80r_paragraph_coordinate.tsv";C82="gdt242_f82r_paragraph_coordinate.tsv"
F80="gdt254_f80r_hpr2_fields.tsv";F82="gdt241_f82r_hpr2_fields.tsv"
ACCESS="gdt257_result.json"
OUTS=["gdt259_bridge_addresses.tsv","gdt259_null_results.tsv","gdt259_counterexamples.tsv"]
DOCS=["GDT259_Q13_BRIDGE_PARAGRAPH_ADDRESS_METHOD.md","GDT259_Q13_BRIDGE_PARAGRAPH_ADDRESS_REPORT.md"]
EDS={"ZL3b","IT2a","RF1b"}
def read(p):
 with (R/p).open(encoding="utf-8") as f:return list(csv.DictReader(f,delimiter="\t"))
def write(p,rows):
 with (R/p).open("w",encoding="utf-8",newline="") as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def norm(c):
 o=int(c["paragraph_line_ordinal"]);n=int(c["paragraph_line_count"]);return (o-1)/(n-1) if n>1 else 0.0
def ge_pair_one(a,b,threshold):
 # Exact count of unordered pairs from a plus one value from b meeting threshold.
 a=sorted(a);total=len(a)*(len(a)-1)//2*len(b);ge=0
 for z in b:
  t=threshold-z
  for i,x in enumerate(a[:-1]):ge+=len(a)-max(i+1,bisect.bisect_left(a,t-x,i+1))
 return ge,total
def main():
 m=read(MATCH);assert [(x["label_locus"],x["prose_locus"]) for x in m]==[("f80r.3","f80r.31"),("f80r.7","f80r.38"),("f82r.36","f82r.6")]
 coords={x["locus"]:x for p in (C80,C82) for x in read(p)}
 fields=defaultdict(list)
 for p in (F80,F82):
  for x in read(p):fields[x["locus"]].append(x)
 addresses=[]
 for x in m:
  c=coords[x["prose_locus"]];found=[]
  for f in fields.get(x["prose_locus"],[]):
   toks=f["source_tokens"].split("|")
   for i,t in enumerate(toks,1):
    if t==x["member_surface"]:found.append((f,i,len(toks)))
  if len(found)==1:
   f,i,n=found[0];hstate="EXACT_SURFACE_UNIQUE_IN_PUBLISHED_HPR2";fo=f["line_field_ordinal"];fc=f["line_field_count"];gp=str(i);gc=str(n);dist=str(n-i);end=f["line_field_end"]
  else:hstate="HPR2_ADDRESS_UNAVAILABLE";fo=fc=gp=gc=dist=end="UNRESOLVED"
  addresses.append({"label_locus":x["label_locus"],"member_surface":x["member_surface"],"neutral_visual_description":x["neutral_visual_description"],"prose_locus":x["prose_locus"],"paragraph_id":c["paragraph_id"],"paragraph_line_ordinal":c["paragraph_line_ordinal"],"paragraph_line_count":c["paragraph_line_count"],"normalized_paragraph_position":f"{norm(c):.9f}","prose_group_index":x["prose_group_index"],"prose_group_count":x["prose_group_count"],"hpr2_address_state":hstate,"hpr2_field_ordinal":fo,"hpr2_field_count":fc,"within_field_group_ordinal":gp,"within_field_group_count":gc,"groups_before_field_end":dist,"field_end":end,"semantic_value":"UNASSIGNED"})
 write(OUTS[0],addresses)
 proj=read(PROJ);assert {x["page"] for x in proj}=={"f80r","f82r"} and all(not x["page"].startswith("f84") for x in proj)
 by=defaultdict(dict)
 for x in proj:by[(x["page"],x["locus"],x["source_group_index"])][x["edition"]]=x
 pools=defaultdict(list)
 for (page,locus,gi),v in by.items():
  if set(v)!=EDS or v["ZL3b"]["kind"]!="P" or locus not in coords:continue
  gi=int(gi);gc=int(v["ZL3b"]["source_group_count"])
  if gi in {1,gc}:continue
  pools[page].append((norm(coords[locus]),locus))
 obs=sum(float(x["normalized_paragraph_position"]) for x in addresses)
 ge,total=ge_pair_one([x[0] for x in pools["f80r"]],[x[0] for x in pools["f82r"]],obs)
 # Give each physical line one vote; equal normalized coordinates in different
 # paragraphs remain distinct physical lines.
 lp={p:sorted({l:v for v,l in xs}.values()) for p,xs in pools.items()}
 ge2,total2=ge_pair_one(lp["f80r"],lp["f82r"],obs)
 nulls=[
  {"null_id":"GROUP_WEIGHTED_PAGE_COMPOSITION","f80_candidates":len(pools["f80r"]),"f82_candidates":len(pools["f82r"]),"worlds":total,"observed_mean_normalized_position":f"{obs/3:.9f}","inclusive_tail_worlds":ge,"inclusive_one_sided_p":f"{ge/total:.9f}","interpretation":"LOCAL_EXPOSED_DISCOVERY_DIAGNOSTIC"},
  {"null_id":"PHYSICAL_LINE_UNIFORM_SENSITIVITY","f80_candidates":len(lp["f80r"]),"f82_candidates":len(lp["f82r"]),"worlds":total2,"observed_mean_normalized_position":f"{obs/3:.9f}","inclusive_tail_worlds":ge2,"inclusive_one_sided_p":f"{ge2/total2:.9f}","interpretation":"LOCAL_EXPOSED_DISCOVERY_DIAGNOSTIC"},]
 write(OUTS[1],nulls)
 counter=[
  {"counterexample":"NO_COMMON_PARAGRAPH","value":"P2;P3;P1","consequence":"not a fixed paragraph address"},
  {"counterexample":"NO_COMMON_LINE_ORDINAL","value":"4;5;6","consequence":"not a fixed within-paragraph line address"},
  {"counterexample":"NO_COMMON_HPR2_FIELD","value":"field 1/2 DY;unresolved;field 2/2 LINE_END","consequence":"not a fixed field or closure address"},
  {"counterexample":"LATE_SKEW_WEAK","value":f"group p={ge/total:.6f};line p={ge2/total2:.6f}","consequence":"late placement is compatible with chance in this exposed three-item search"},
  {"counterexample":"SPARSE_INTERFACE","value":"3/23 aligned labels from GDT247","consequence":"cannot execute a general label-to-prose reference rule"},]
 write(OUTS[2],counter)
 access=json.loads((R/ACCESS).read_text());assert access["access"]["pristine_access_seal"] is False
 result={"experiment":"GDT259_Q13_BRIDGE_PARAGRAPH_ADDRESS","status":"THREE_BRIDGES_SKEW_LATE_WEAKLY_WITH_NO_COMMON_PARAGRAPH_OR_FIELD_ADDRESS","bridges":3,"normalized_positions":[float(x["normalized_paragraph_position"]) for x in addresses],"mean_normalized_position":obs/3,"group_weighted_exact_p":ge/total,"line_uniform_exact_p":ge2/total2,"hpr2_addresses_resolved":sum(x["hpr2_address_state"].startswith("EXACT") for x in addresses),"common_paragraph_address":False,"common_hpr2_address":False,"active_semantic_assignments":0,"interpretation":"The exact rendered-group bridges lean late in their physical paragraphs but do not share an executable paragraph or HPR2 field address; the sparse-reference world remains possible rather than identified.","claim_ceiling":"Paragraph and field address only; no referent function object role word language plaintext or translation.","f84r":{"prior_transient_parse_disclosed":True,"new_access":False,"used":False,"scored":False,"further_access_authorized":False},"inputs":{p:sha(p) for p in [MATCH,PROJ,C80,C82,F80,F82,ACCESS]},"outputs":{},"documents":{},"implementation":{Path(__file__).name:sha(Path(__file__).name)}}
 for p in OUTS:result["outputs"][p]=sha(p)
 for p in DOCS:result["documents"][p]=sha(p)
 result["content_hash"]=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(",",":")).encode()).hexdigest();(R/"gdt259_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"status":result["status"],"mean":result["mean_normalized_position"],"p":result["group_weighted_exact_p"]},sort_keys=True))
if __name__=="__main__":main()
