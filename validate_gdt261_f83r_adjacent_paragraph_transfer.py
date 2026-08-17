#!/usr/bin/env python3
import csv,hashlib,json,math
from pathlib import Path
R=Path(__file__).resolve().parent;checks=[]
def ck(n,x):checks.append((n,bool(x)));assert x,n
def read(p):
 with (R/p).open(encoding="utf-8") as f:return list(csv.DictReader(f,delimiter="\t"))
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def tail(m,k):return sum(math.comb(3,j)*math.comb(22,m-j) for j in range(k,min(3,m)+1) if 0<=m-j<=22)/math.comb(25,m) if m else 1
r=json.loads((R/"gdt261_result.json").read_text());x=read("gdt261_f83r_transfer.tsv");c=read("gdt261_counterexamples.tsv")
ck("status",r["status"]=="F83R_EXPOSED_ADJACENT_PARAGRAPH_SENSITIVITY_FAILS_GDT260_COMPONENT_TRANSFER");ck("three",len(x)==3);ck("reps",[(q["representation"],q["target_surface"]) for q in x]==[("LEFT_MODULE","ol"),("RIGHT_REMAINDER","saiin"),("FULL_LABEL","olsaiin")]);ck("counts",[(q["all_hit_lines"],q["target_hit_lines"]) for q in x]==[("24","3"),("12","0"),("0","0")]);ck("p",all(abs(float(q["local_hypergeom_p"])-tail(int(q["all_hit_lines"]),int(q["target_hit_lines"])))<5e-13 for q in x));ck("left_p",x[0]["local_hypergeom_p"]=="0.880000000000");ck("five_counter",len(c)==5);ck("zero_semantics",all(q["semantic_value"]=="UNASSIGNED" for q in x) and r["active_semantic_assignments"]==0)
frame_loci={q["locus"] for q in read("gdt046_line_frames.tsv") if q["page"]=="f83r"};lines=[q for q in read("gdt020_line_phase_parses.tsv") if q["page"]=="f83r" and q["locus"] in frame_loci];ck("lines",len(lines)==25);target={"f83r.47","f83r.48","f83r.49"};got=set()
for q in lines:
 for tok in [z.strip() for z in q["tokens"].split("|")]:
  for i in range(len(tok)-1):
   if sum(a!=b for a,b in zip("ol",tok[i:i+2]))<=1:got.add(q["locus"])
ck("rebuild_left",len(got)==24 and target<=got);ck("f84_source_free",not any(q["page"].startswith("f84r") for q in read("gdt020_line_phase_parses.tsv")) and not any(q["page"].startswith("f84r") for q in read("gdt046_line_frames.tsv")))
for k in ("inputs","outputs","documents","implementation"):
 for fn,h in r[k].items():ck(k+"_"+fn,sha(fn)==h)
core={k:v for k,v in r.items() if k!="content_hash"};ck("content_hash",hashlib.sha256(json.dumps(core,sort_keys=True,separators=(",",":")).encode()).hexdigest()==r["content_hash"]);ck("f84",r["f84r"]=={"prior_transient_parse_disclosed":True,"new_access":False,"used":False,"scored":False,"further_access_authorized":False})
o={"status":"PASS","checks_passed":len(checks),"checks_total":len(checks),"result_sha256":sha("gdt261_result.json"),"validation_scope":"Exposed f83r target, display-window counts, exact tails, hashes, claim state, and f84r exclusion."};o["content_hash"]=hashlib.sha256(json.dumps(o,sort_keys=True,separators=(",",":")).encode()).hexdigest();(R/"gdt261_validation.json").write_text(json.dumps(o,indent=2,sort_keys=True)+"\n");print(f"PASS {len(checks)}/{len(checks)}")
