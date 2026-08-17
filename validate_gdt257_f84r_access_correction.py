#!/usr/bin/env python3
"""Validate only the correction record; deliberately reads no data table."""
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;P=R/"gdt257_result.json";checks=[]
def ck(n,x):checks.append((n,bool(x)));assert x,n
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
r=json.loads(P.read_text());a=r["access"]
ck("status",r["status"]=="F84R_SEAL_BREACH_TRANSIENT_GLOBAL_TABLE_PARSE_NO_VALUES_DISPLAYED_OR_SCORED");ck("parsed",a["f84r_rows_transiently_parsed_by_subprocess"]);ck("not_pristine",not a["pristine_access_seal"]);ck("not_displayed",not a["f84r_values_printed_in_tool_output"]);ck("not_inspected",not a["f84r_values_manually_inspected"]);ck("not_joined",not a["f84r_selected_or_joined"]);ck("not_scored",not a["f84r_scored"]);ck("no_artifact",not a["f84r_result_artifact_written"] and r["attempted_route_status"]=="ABORTED_NO_ARTIFACT");ck("prohibition",r["continuing_prohibition"]=="NO_FURTHER_F84R_ACCESS_WITHOUT_EXPLICIT_USER_AUTHORIZATION")
for p,h in r["documents"].items():ck("doc_hash_"+p,sha(p)==h)
for p,h in r["implementation"].items():ck("impl_hash_"+p,sha(p)==h)
core={k:v for k,v in r.items() if k!="content_hash"};ck("content_hash",hashlib.sha256(json.dumps(core,sort_keys=True,separators=(",",":")).encode()).hexdigest()==r["content_hash"])
out={"status":"PASS","checks_passed":len(checks),"checks_total":len(checks),"result_sha256":hashlib.sha256(P.read_bytes()).hexdigest(),"validation_scope":"Correction literals and hashes only; validator deliberately reads no Voynich data table."};out["content_hash"]=hashlib.sha256(json.dumps(out,sort_keys=True,separators=(",",":")).encode()).hexdigest();(R/"gdt257_validation.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(f"PASS {len(checks)}/{len(checks)}")
