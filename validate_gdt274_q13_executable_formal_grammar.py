#!/usr/bin/env python3
"""Independent source-to-artifact validation of the GDT274 grammar checkpoint."""
import csv,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path

R=Path(__file__).resolve().parent
def read(name):
 with (R/name).open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(name):return hashlib.sha256((R/name).read_bytes()).hexdigest()
def chash(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def js(v):return json.dumps(v,separators=(",",":"),sort_keys=True)
def templ(ll,k):
 if k=="RAW":return js([x["source_tokens"] for x in ll])
 if k=="HOST":return js([x["page_hosts"] for x in ll])
 if k=="COMPILER":return js([x["compiler_cells"] for x in ll])
 if k=="COUNTS":return js([int(x["field_group_count"]) for x in ll])
 return js([["S12" if int(x["field_group_count"])<=2 else "L3P",x["line_field_end"]] for x in ll])

def main():
 checks=[]
 def ck(name,ok):
  checks.append({"check":name,"pass":bool(ok)})
  if not ok:raise AssertionError(name)
 src=read("gdt227_q13_abstract_interlinear.tsv");ck("source_fields_701",len(src)==701);ck("source_no_f84",all(not x["page"].startswith("f84") for x in src))
 rec=defaultdict(list)
 for x in src:rec[x["record_id"]].append(x)
 for rid in rec:rec[rid].sort(key=lambda x:int(x["field_ordinal"]));ck("ordinal_"+rid,[int(x["field_ordinal"]) for x in rec[rid]]==list(range(1,len(rec[rid])+1)))
 ck("records_33",len(rec)==33);ck("folios_9",len({x["physical_folio"] for x in src})==9);ck("groups_1896",sum(int(x["field_group_count"]) for x in src)==1896)
 lines={}
 for rid,rr in rec.items():
  for x in rr:lines.setdefault((rid,x["locus"]),[]).append(x)
 for ll in lines.values():ll.sort(key=lambda x:int(x["field_ordinal"]))
 ck("physical_lines_240",len(lines)==240)
 kinds=("RAW","HOST","COMPILER","COUNTS","COARSE");fol={k:defaultdict(set) for k in kinds};freq={k:Counter() for k in kinds}
 for (rid,locus),ll in lines.items():
  for k in kinds:t=templ(ll,k);fol[k][t].add(ll[0]["physical_folio"]);freq[k][t]+=1
 exported=read("gdt274_q13_line_templates.tsv");ck("line_rows_240",len(exported)==240);idx={(x["record_id"],x["locus"]):x for x in exported};ck("line_keys",set(idx)==set(lines))
 for key,ll in lines.items():
  x=idx[key];ck("line_counts_"+key[0]+"_"+key[1],int(x["field_count"])==len(ll) and int(x["group_count"])==sum(int(z["field_group_count"]) for z in ll))
  for k in kinds:
   q=k.lower();t=templ(ll,k);ck(q+"_template_"+key[0]+"_"+key[1],x[q+"_template"]==t and int(x[q+"_global_frequency"])==freq[k][t] and int(x[q+"_cross_folio_support"])==len(fol[k][t]) and int(x[q+"_seen_other_folio"])==int(len(fol[k][t])>=2))
 rr=read("gdt274_q13_record_parses.tsv");ck("record_rows_33",len(rr)==33);ridx={x["record_id"]:x for x in rr};ck("record_keys",set(ridx)==set(rec))
 for rid,srcrows in rec.items():
  x=ridx[rid];ck("record_counts_"+rid,int(x["field_count"])==len(srcrows) and int(x["group_count"])==sum(int(z["field_group_count"]) for z in srcrows) and int(x["line_count"])==sum(k[0]==rid for k in lines) and int(x["dy_fields"])+int(x["line_end_fields"])==len(srcrows));ck("record_content_unassigned_"+rid,x["content_assignment"]=="UNASSIGNED")
  parsed=json.loads(x["formal_parse_json"]);flat=[f for line in parsed for f in line["fields"]];ck("record_parse_fields_"+rid,[f["ordinal"] for f in flat]==[int(z["field_ordinal"]) for z in srcrows]);ck("record_parse_groups_"+rid,sum(len(f["source"]) for f in flat)==sum(int(z["field_group_count"]) for z in srcrows))
 schema=json.loads((R/"gdt274_grammar_schema.json").read_text());stored=schema.pop("content_hash");ck("schema_hash",stored==chash(schema));ck("schema_start",schema["start"]=="Q13_PAGE");ck("schema_no_semantics",schema["semantic_assignments"]=={});ck("schema_seal",schema["sealed_folio"]=="f84r")
 ev={x["claim_id"]:x for x in read("gdt274_evidence_registry.tsv")};ck("evidence_ids",set(ev)=={"HIERARCHY","GROUP_FACTOR","RECORD_FINGERPRINT","Q_RENDERER","Q_GLOBAL_STAGE","Q_DENSITY","FIRST_ORDER_FIELDS","CONTENT"});ck("content_unassigned",ev["CONTENT"]["status"]=="UNASSIGNED");ck("tested_failures",ev["Q_DENSITY"]["status"]==ev["FIRST_ORDER_FIELDS"]["status"]=="NOT_SUPPORTED")
 examples=read("gdt274_representative_parses.tsv");ck("six_examples",len(examples)==6 and all(x["record_id"]=="Q13|f75r|R01" for x in examples));ck("examples_no_semantics",all(x["semantic_parse"]=="UNASSIGNED" for x in examples))
 result=json.loads((R/"gdt274_result.json").read_text());rh=result.pop("content_hash");ck("result_hash",rh==chash(result));result["content_hash"]=rh
 ck("result_counts",(result["records"],result["physical_lines"],result["fields"],result["groups"],result["folios"])==(33,240,701,1896,9));ck("result_status",result["status"]=="Q13_HIERARCHICAL_TEMPLATE_GRAMMAR_CHECKPOINT");ck("result_no_semantics",result["semantic_assignments"]==0);ck("result_f84",all(v is False for v in result["f84r"].values()))
 expected={k:{"unique_templates":len(freq[k]),"cross_folio_types":sum(len(v)>=2 for v in fol[k].values()),"line_occurrences_seen_other_folio":sum(len(fol[k][templ(ll,k)])>=2 for ll in lines.values())} for k in kinds};ck("template_summary",result["line_template_summary"]==expected);ck("raw_host_compiler_unique",all(expected[k]["unique_templates"]==240 and expected[k]["line_occurrences_seen_other_folio"]==0 for k in ("RAW","HOST","COMPILER")));ck("coarse_reuse",expected["COARSE"]=={"unique_templates":67,"cross_folio_types":39,"line_occurrences_seen_other_folio":208})
 ck("input_hashes",all(sha(k)==v for k,v in result["inputs"].items()));ck("document_hashes",all(sha(k)==v for k,v in result["documents"].items()));ck("implementation_hash",all(sha(k)==v for k,v in result["implementation"].items()));ck("output_hashes",all(sha(k)==v for k,v in result["outputs"].items()))
 payload={"experiment":"GDT274_Q13_EXECUTABLE_FORMAL_GRAMMAR_VALIDATION","status":"PASS","checks_passed":len(checks),"checks_total":len(checks),"result_sha256":sha("gdt274_result.json"),"validator_sha256":sha(Path(__file__).name),"checks":checks};payload["content_hash"]=chash(payload);(R/"gdt274_validation.json").write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":"PASS","checks":len(checks)},sort_keys=True))
if __name__=="__main__":main()
