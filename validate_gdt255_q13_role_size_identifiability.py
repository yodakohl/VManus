#!/usr/bin/env python3
import csv,hashlib,json
from collections import Counter
from pathlib import Path
R=Path(__file__).resolve().parent;RES="gdt255_result.json";checks=[]
def ck(n,x):checks.append((n,bool(x)));assert x,n
def rd(p):
 with (R/p).open(encoding="utf-8") as f:return list(csv.DictReader(f,delimiter="\t"))
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def main():
 f=rd("gdt254_f80r_role_projection.tsv")+rd("gdt243_f82r_missingness_role_projection.tsv");ck("94_fields",len(f)==94);ck("no_f84",all(not x["page"].startswith("f84") for x in f));pred=["SHORT_ARGUMENT_LIKE" if int(x["field_group_count"])<=2 else "INSTRUCTION_CLAUSE_LIKE" for x in f];ck("exact_size_rule",all(a==x["robust_abstract_role_like"] for a,x in zip(pred,f)));ck("counts",Counter(pred)==Counter({"SHORT_ARGUMENT_LIKE":49,"INSTRUCTION_CLAUSE_LIKE":45}))
 atlas=rd("gdt255_shared_host_role_atlas.tsv");ck("13_shared_hosts",len(atlas)==13);ol=next(x for x in atlas if x["page_host"]=="olche");ck("olche",ol["occurrences"]=="4" and ol["f80r_occurrences"]=="2" and ol["f82r_occurrences"]=="2" and ol["size_threshold_fraction"]=="1.000000000000")
 r=json.loads((R/RES).read_text());ck("status",r["status"]=="CORRECTED_Q13_ROLE_ANALOGIES_COLLAPSE_EXACTLY_TO_FIELD_SIZE_ZERO_HOST_SEMANTIC_RESIDUAL");ck("result_counts",r["size_threshold_correct"]==94 and r["shared_hosts_min2_each_page"]==13);ck("zero_semantics",r["active_semantic_assignments"]==0);ck("f84_flags",not any(r["f84"].values()))
 for p,h in r["inputs"].items():ck("input_hash_"+p,sha(p)==h)
 for p,h in r["outputs"].items():ck("output_hash_"+p,sha(p)==h)
 for p,h in r["documents"].items():ck("doc_hash_"+p,sha(p)==h)
 for p,h in r["implementation"].items():ck("impl_hash_"+p,sha(p)==h)
 core={k:v for k,v in r.items() if k!="content_hash"};ck("content_hash",hashlib.sha256(json.dumps(core,sort_keys=True,separators=(",",":")).encode()).hexdigest()==r["content_hash"]);out={"status":"PASS","checks_passed":len(checks),"checks_total":len(checks),"result_sha256":sha(RES),"validation_scope":"Independent 94-field size-rule reconstruction, shared-host capacity, olche confound, hashes, f84 flags, and claim state."};out["content_hash"]=hashlib.sha256(json.dumps(out,sort_keys=True,separators=(",",":")).encode()).hexdigest();(R/"gdt255_validation.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(f"PASS {len(checks)}/{len(checks)}")
if __name__=="__main__":main()
