#!/usr/bin/env python3
"""Validate the compact GDT258 synthesis without opening source tables."""
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;P=R/"gdt258_result.json";checks=[]
def ck(n,x):checks.append((n,bool(x)));assert x,n
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
r=json.loads(P.read_text());w=list(csv.DictReader((R/"gdt258_candidate_worlds.tsv").open(),delimiter="\t"));e=list(csv.DictReader((R/"gdt258_evidence_matrix.tsv").open(),delimiter="\t"))
ck("status",r["status"]=="HYBRID_DIAGRAM_LEGEND_PLUS_PARAGRAPH_RECORDS_LEADS_CONTENT_CHANNEL_UNRESOLVED");ck("leading_world",r["leading_world"]==w[0]["world_id"]);ck("four_worlds",len(w)==4==r["candidate_worlds"]);ck("eight_evidence",len(e)==8==r["evidence_rows"]);ck("zero_world_semantics",all(x["semantic_assignments"]=="0" for x in w));ck("zero_active_semantics",r["active_semantic_assignments"]==0);ck("counts",r["corrected_pages"]=={"f80r":{"paragraphs":5,"labels":10,"hpr2_fields":43},"f82r":{"paragraphs":3,"labels":13,"hpr2_fields":51}});ck("three_bridges",r["exact_cross_scope_member_matches"]==3);ck("size_collapse",r["corrected_role_size_collapse"]=="94_OF_94");ck("f84_disclosure",r["f84r"]["prior_transient_parse_disclosed"] and not r["f84r"]["new_access"] and not r["f84r"]["used"] and not r["f84r"]["scored"] and not r["f84r"]["further_access_authorized"])
for p,h in r["inputs"].items():ck("input_hash_"+p,sha(p)==h)
for p,h in r["documents"].items():ck("doc_hash_"+p,sha(p)==h)
for p,h in r["outputs"].items():ck("output_hash_"+p,sha(p)==h)
for p,h in r["implementation"].items():ck("impl_hash_"+p,sha(p)==h)
core={k:v for k,v in r.items() if k!="content_hash"};ck("content_hash",hashlib.sha256(json.dumps(core,sort_keys=True,separators=(",",":")).encode()).hexdigest()==r["content_hash"]);out={"status":"PASS","checks_passed":len(checks),"checks_total":len(checks),"result_sha256":hashlib.sha256(P.read_bytes()).hexdigest(),"validation_scope":"Compact result inheritance, candidate-world/evidence tables, f84r correction disclosure, hashes, and claim state; no source table opened."};out["content_hash"]=hashlib.sha256(json.dumps(out,sort_keys=True,separators=(",",":")).encode()).hexdigest();(R/"gdt258_validation.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(f"PASS {len(checks)}/{len(checks)}")
