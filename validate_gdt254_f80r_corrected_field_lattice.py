#!/usr/bin/env python3
"""Independent structural/integrity validator for GDT254; no scorer import."""
import csv,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent
SRC="gdt016_group_state_inventory.tsv";CENS="gdt246_f80r_complete_locus_inventory.tsv";COORD="gdt244_f80r_paragraph_coordinate.tsv";PROJ="gdt002_grammar_projection.tsv";RES="gdt254_result.json"
checks=[]
def ck(n,x):checks.append((n,bool(x)));assert x,n
def rd(p):
 with (R/p).open(encoding="utf-8") as f:return list(csv.DictReader(f,delimiter="\t"))
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def main():
 census=rd(CENS);prose={x["locus"] for x in census if x["page"]=="f80r" and x["kind"]=="P"};coord=rd(COORD)
 ck("43_prose",len(prose)==43==len(coord));ck("five_paragraph_counts",[sum(x["paragraph_id"]==f"P{i}" for x in coord) for i in range(1,6)]==[17,6,6,7,7])
 src=rd(SRC);ck("source_has_zero_f84r",sum(x["page"]=="f84r" for x in src)==0)
 by=defaultdict(list)
 for x in src:
  if x["page"]=="f80r" and x["locus"] in prose:by[x["locus"]].append(x)
 ck("covered_loci",len(by)==23)
 expected=[]
 for locus in sorted(by,key=lambda x:int(x.split(".")[1])):
  gg=sorted(by[locus],key=lambda x:int(x["group_index"]));cur=[];fs=[]
  for g in gg:
   cur.append(g)
   if g["dy_closure"]=="1":fs.append(cur);cur=[]
  if cur:fs.append(cur)
  for i,z in enumerate(fs,1):expected.append((locus,i,len(fs),len(z),"|".join(g["token"] for g in z),"DY" if z[-1]["dy_closure"]=="1" else "LINE_END"))
 got=rd("gdt254_f80r_hpr2_fields.tsv");ck("43_fields",len(expected)==len(got)==43)
 ck("field_segmentation",expected==[(x["locus"],int(x["line_field_ordinal"]),int(x["line_field_count"]),int(x["field_group_count"]),x["source_tokens"],x["line_field_end"]) for x in got])
 maxg=defaultdict(int)
 for x in rd(PROJ):
  if x["page"]=="f80r" and x["kind"]=="P":maxg[x["locus"]]=max(maxg[x["locus"]],int(x["source_group_count"]))
 para=rd("gdt254_f80r_paragraph_uncertainty.tsv")
 for p in para:
  z=[x for x in coord if x["paragraph_id"]==p["paragraph_id"]];covered=[x for x in z if x["locus"] in by];missing=[x for x in z if x["locus"] not in by]
  ck("paragraph_"+p["paragraph_id"],int(p["physical_lines"])==len(z) and int(p["covered_lines"])==len(covered) and int(p["missing_lines"])==len(missing) and int(p["missing_field_max"])==sum(maxg[x["locus"]] for x in missing))
 role=rd("gdt254_f80r_role_projection.tsv");cnt=Counter(x["robust_abstract_role_like"] for x in role)
 ck("role_rows",len(role)==43);ck("role_counts",cnt==Counter({"INSTRUCTION_CLAUSE_LIKE":25,"SHORT_ARGUMENT_LIKE":18}));ck("role_unassigned",all(x["semantic_value"]=="UNASSIGNED" for x in role));ck("allowed_role_classes",set(cnt)<={"INSTRUCTION_CLAUSE_LIKE","SHORT_ARGUMENT_LIKE","UNRESOLVED_EDGE_CLASS","RECORD_CLOSER_LIKE","UNRESOLVED_MISSINGNESS_SENSITIVE"})
 result=json.loads((R/RES).read_text());ck("status",result["status"]=="F80R_FIVE_PARAGRAPH_HPR2_LATTICE_REBUILT_FORMAL_ANALOGY_ONLY");ck("result_counts",result["hpr2_covered_loci"]==23 and result["hpr2_fields"]==43 and result["missing_loci"]==20 and result["role_counts"]==dict(sorted(cnt.items())));ck("no_semantics",result["active_semantic_assignments"]==0);ck("f84r_flags",result["f84r"]["input_rows"]==0 and not any(v for k,v in result["f84r"].items() if k!="input_rows"))
 for p,h in result["inputs"].items():ck("input_hash_"+p,sha(p)==h)
 for p,h in result["outputs"].items():ck("output_hash_"+p,sha(p)==h)
 for p,h in result["documents"].items():ck("doc_hash_"+p,sha(p)==h)
 for p,h in result["implementation"].items():ck("impl_hash_"+p,sha(p)==h)
 core={k:v for k,v in result.items() if k!="content_hash"};ck("content_hash",hashlib.sha256(json.dumps(core,sort_keys=True,separators=(",",":")).encode()).hexdigest()==result["content_hash"])
 out={"status":"PASS","checks_passed":len(checks),"checks_total":len(checks),"result_sha256":sha(RES),"validation_scope":"Independent f80r source field segmentation, five-paragraph missingness arithmetic, retained-class accounting, hashes, f84r guard, and claim state; external classifier coefficients are not independently refit."};out["content_hash"]=hashlib.sha256(json.dumps(out,sort_keys=True,separators=(",",":")).encode()).hexdigest();(R/"gdt254_validation.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(f"PASS {len(checks)}/{len(checks)}")
if __name__=="__main__":main()
