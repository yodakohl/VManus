#!/usr/bin/env python3
"""Validate GDT260 tables, exact tails, bindings, and claim state."""
import csv,hashlib,json,math
from pathlib import Path
R=Path(__file__).resolve().parent;checks=[]
def ck(n,x):checks.append((n,bool(x)));assert x,n
def read(p):
 with (R/p).open(encoding="utf-8") as f:return list(csv.DictReader(f,delimiter="\t"))
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def tail(m,k):return sum(math.comb(9,j)*math.comb(23,m-j) for j in range(k,min(9,m)+1))/math.comb(32,m) if m else 1
r=json.loads((R/"gdt260_result.json").read_text());x=read("gdt260_component_neighborhood.tsv");c=read("gdt260_component_controls.tsv");z=read("gdt260_counterexamples.tsv")
ck("status",r["status"]=="F82R_ATTACHED_LABEL_LEFT_COMPONENT_NEIGHBORHOOD_CONCENTRATES_IN_FOLLOWING_PARAGRAPH_PROVISIONAL");ck("nine_rows",len(x)==9);ck("three_readings",{q["edition"] for q in x}=={"ZL3b","IT2a","RF1b"});ck("three_reps",{q["representation"] for q in x}=={"LEFT_SPLIT_COMPONENT","RIGHT_SPLIT_COMPONENT","FULL_JOINED_LABEL"})
left=[q for q in x if q["representation"]=="LEFT_SPLIT_COMPONENT"];ck("left_hits",[(q["edition"],q["P2_hit_lines"],q["all_hit_lines"]) for q in left]==[("ZL3b","3","3"),("IT2a","4","4"),("RF1b","3","3")]);ck("left_exact_zero",all(q["exact_distance0_hit_lines"]=="0" for q in left));ck("left_codes",all(q["target_member_codes"]=="A1 C1 A1 B2" for q in left));ck("p_exact",all(abs(float(q["local_hypergeom_p"])-tail(int(q["all_hit_lines"]),int(q["P2_hit_lines"])))<5e-13 for q in x));ck("bonferroni",all(abs(float(q["three_representation_bonferroni_p"])-min(1,3*float(q["local_hypergeom_p"])))<2e-12 for q in x));ck("full_zero",all(q["all_hit_lines"]=="0" for q in x if q["representation"]=="FULL_JOINED_LABEL"));ck("right_broad",[(q["P2_hit_lines"],q["all_hit_lines"]) for q in x if q["representation"]=="RIGHT_SPLIT_COMPONENT"]==[("5","13"),("7","19"),("3","10")]);ck("family_control",len(c)==3 and all((q["P1_lines"],q["P2_lines"],q["P3_lines"])==("2","3","4") for q in c));ck("six_counter",len(z)==6);ck("zero_semantics",all(q["semantic_value"]=="UNASSIGNED" for q in x) and r["active_semantic_assignments"]==0)
dos=[q for q in read("gdt239_f82r_label_dossier.tsv") if q["locus"]=="f82r.10"];ck("source_bound",len(dos)==1 and dos[0]["ownership_evidence"]=="CONNECTED_COMPONENT" and dos[0]["human_local_comment"]=="Label on cross-shaped tube. Grove's #11.")
p=read("gdt002_grammar_projection.tsv");ck("safe_projection",{q["page"] for q in p}=={"f80r","f82r"});coord={q["locus"]:q for q in read("gdt242_f82r_paragraph_coordinate.tsv")};ck("following_p2",coord["f82r.11"]["paragraph_id"]=="P2" and coord["f82r.11"]["paragraph_line_ordinal"]=="1")
# Rebuild the headline member-window and family controls from the source rows.
expected={"ZL3b":["f82r.11","f82r.12","f82r.13"],"IT2a":["f82r.11","f82r.12","f82r.13","f82r.14"],"RF1b":["f82r.11","f82r.12","f82r.13"]}
for ed,want in expected.items():
 target=sum((q["primary_sta_codes"].split() for q in sorted([q for q in p if q["edition"]==ed and q["locus"]=="f82r.10"],key=lambda z:int(z["source_group_index"]))),[])[:4];got=set();exact=set();by={}
 for q in p:
  if q["edition"]!=ed or q["page"]!="f82r" or q["kind"]!="P" or q["locus"] not in coord:continue
  by.setdefault(q["locus"],[]).append(q);codes=q["primary_sta_codes"].split()
  for i in range(len(codes)-3):
   d=sum(a!=b for a,b in zip(target,codes[i:i+4]))
   if d<=1:got.add(q["locus"])
   if d==0:exact.add(q["locus"])
 ck("rebuild_left_"+ed,sorted(got,key=lambda z:int(z.split('.')[1]))==want and not exact)
 hist={"P1":0,"P2":0,"P3":0}
 for loc,qs in by.items():
  fam="".join(q["primary_sta_families"] for q in sorted(qs,key=lambda z:int(z["source_group_index"])))
  if "ACAB" in fam:hist[coord[loc]["paragraph_id"]]+=1
 ck("rebuild_family_"+ed,hist=={"P1":2,"P2":3,"P3":4})
for k in ("inputs","outputs","documents","implementation"):
 for fn,h in r[k].items():ck(k+"_"+fn,sha(fn)==h)
core={k:v for k,v in r.items() if k!="content_hash"};ck("content_hash",hashlib.sha256(json.dumps(core,sort_keys=True,separators=(",",":")).encode()).hexdigest()==r["content_hash"]);ck("f84",r["f84r"]=={"prior_transient_parse_disclosed":True,"new_access":False,"used":False,"scored":False,"further_access_authorized":False})
out={"status":"PASS","checks_passed":len(checks),"checks_total":len(checks),"result_sha256":sha("gdt260_result.json"),"validation_scope":"Attached-label selection, fixed component rows, exact hypergeometric tails, controls, hashes, claim state, and f84r disclosure."};out["content_hash"]=hashlib.sha256(json.dumps(out,sort_keys=True,separators=(",",":")).encode()).hexdigest();(R/"gdt260_validation.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(f"PASS {len(checks)}/{len(checks)}")
