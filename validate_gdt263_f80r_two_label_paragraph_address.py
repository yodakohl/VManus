#!/usr/bin/env python3
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;checks=[]
def ck(n,x):checks.append((n,bool(x)));assert x,n
def read(p):
 with (R/p).open(encoding="utf-8") as f:return list(csv.DictReader(f,delimiter="\t"))
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
r=json.loads((R/"gdt263_result.json").read_text());a=read("gdt263_label_paragraph_assignments.tsv");n=read("gdt263_shift_null.tsv");c=read("gdt263_counterexamples.tsv")
ck("status",r["status"]=="F80R_TWO_LABELS_PER_PARAGRAPH_ADDRESS_LATTICE_FAILS");ck("rows",len(a)==30);ck("ten_each",all(len([x for x in a if x["edition"]==ed])==10 for ed in ("ZL3b","IT2a","RF1b")));ck("map",all(x["predicted_paragraph"]==f'P{(int(x["label_locus"].split(".")[1])+1)//2}' for x in a));ck("windows",all(sum(int(x["unique_four_member_windows"]) for x in a if x["edition"]==ed)==20 for ed in ("ZL3b","IT2a","RF1b")));ck("no_lead",all(float(x["within_label_adjusted_p"])>=.1 for x in a) and r["individual_rows_adjusted_below_0_1"]==0);ck("p",r["circular_p"]=={"ZL3b":.697674418605,"IT2a":.418604651163,"RF1b":.790697674419});ck("null",[(x["equal_or_stronger_worlds"],x["circular_worlds"]) for x in n]==[("30","43"),("18","43"),("34","43")]);ck("counter",len(c)==4);ck("zero_semantics",all(x["semantic_value"]=="UNASSIGNED" for x in a) and r["active_semantic_assignments"]==0)
coord=read("gdt244_f80r_paragraph_coordinate.tsv");ck("paragraph_sizes",[len([x for x in coord if x["paragraph_id"]==f"P{i}"]) for i in range(1,6)]==[17,6,6,7,7]);p=read("gdt002_grammar_projection.tsv");ck("safe",{x["page"] for x in p}=={"f80r","f82r"})
for k in ("inputs","outputs","documents","implementation"):
 for fn,h in r[k].items():ck(k+"_"+fn,sha(fn)==h)
core={k:v for k,v in r.items() if k!="content_hash"};ck("content_hash",hashlib.sha256(json.dumps(core,sort_keys=True,separators=(",",":")).encode()).hexdigest()==r["content_hash"]);ck("f84",r["f84r"]=={"prior_transient_parse_disclosed":True,"new_access":False,"used":False,"scored":False,"further_access_authorized":False})
o={"status":"PASS","checks_passed":len(checks),"checks_total":len(checks),"result_sha256":sha("gdt263_result.json"),"validation_scope":"Ten-to-five mapping, window counts, stored circular ranks, hashes, claim state, and f84r disclosure."};o["content_hash"]=hashlib.sha256(json.dumps(o,sort_keys=True,separators=(",",":")).encode()).hexdigest();(R/"gdt263_validation.json").write_text(json.dumps(o,indent=2,sort_keys=True)+"\n");print(f"PASS {len(checks)}/{len(checks)}")
