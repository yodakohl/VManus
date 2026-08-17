#!/usr/bin/env python3
"""Build an executable, evidence-tiered q13 formal grammar checkpoint."""
import csv,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path

R=Path(__file__).resolve().parent
SRC="gdt227_q13_abstract_interlinear.tsv"
METHOD="GDT274_Q13_EXECUTABLE_FORMAL_GRAMMAR_METHOD.md"
CONTEXT=["gdt264_result.json","gdt270_result.json","gdt271_result.json","gdt272_result.json","gdt273_result.json"]

def read(name):
 with (R/name).open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def write(name,rows):
 with (R/name).open("w",encoding="utf-8",newline="") as h:
  w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(name):return hashlib.sha256((R/name).read_bytes()).hexdigest()
def chash(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def j(v):return json.dumps(v,separators=(",",":"),sort_keys=True)

def main():
 rows=read(SRC);assert len(rows)==701 and all(not x["page"].startswith("f84") for x in rows)
 records=defaultdict(list)
 for x in rows:records[x["record_id"]].append(x)
 for rr in records.values():rr.sort(key=lambda x:int(x["field_ordinal"]));assert [int(x["field_ordinal"]) for x in rr]==list(range(1,len(rr)+1))
 assert len(records)==33 and len({x["physical_folio"] for x in rows})==9

 lines={}
 for rid,rr in records.items():
  for x in rr:
   key=(rid,x["locus"]);lines.setdefault(key,[]).append(x)
 for ll in lines.values():ll.sort(key=lambda x:int(x["field_ordinal"]))
 assert len(lines)==240

 def template(ll,kind):
  if kind=="RAW":return j([x["source_tokens"] for x in ll])
  if kind=="HOST":return j([x["page_hosts"] for x in ll])
  if kind=="COMPILER":return j([x["compiler_cells"] for x in ll])
  if kind=="COUNTS":return j([int(x["field_group_count"]) for x in ll])
  return j([["S12" if int(x["field_group_count"])<=2 else "L3P",x["line_field_end"]] for x in ll])
 kinds=("RAW","HOST","COMPILER","COUNTS","COARSE")
 folios={k:defaultdict(set) for k in kinds};freqs={k:Counter() for k in kinds}
 for (rid,locus),ll in lines.items():
  fol=ll[0]["physical_folio"]
  for k in kinds:t=template(ll,k);folios[k][t].add(fol);freqs[k][t]+=1

 line_rows=[]
 for (rid,locus),ll in sorted(lines.items(),key=lambda z:(z[1][0]["page"],int(z[1][0]["field_ordinal"]))):
  row={"record_id":rid,"page":ll[0]["page"],"physical_folio":ll[0]["physical_folio"],"locus":locus,"line_ordinal_in_record":sum(1 for (r,l),x in lines.items() if r==rid and int(x[0]["field_ordinal"])<=int(ll[0]["field_ordinal"])),"field_count":len(ll),"group_count":sum(int(x["field_group_count"]) for x in ll)}
  for k in kinds:
   t=template(ll,k);q=k.lower();row[q+"_template"]=t;row[q+"_global_frequency"]=freqs[k][t];row[q+"_cross_folio_support"]=len(folios[k][t]);row[q+"_seen_other_folio"]=int(len(folios[k][t])>=2)
  line_rows.append(row)

 record_rows=[]
 for rid,rr in sorted(records.items()):
  lr=[(key,ll) for key,ll in lines.items() if key[0]==rid];lr.sort(key=lambda z:int(z[1][0]["field_ordinal"]))
  parse=[]
  for (_,locus),ll in lr:
   parse.append({"locus":locus,"fields":[{"ordinal":int(x["field_ordinal"]),"groups":int(x["field_group_count"]),"end":x["line_field_end"],"source":x["source_tokens"].split("|"),"hosts":x["page_hosts"].split("|"),"compiler":x["compiler_cells"].split("|")} for x in ll]})
  record_rows.append({"record_id":rid,"page":rr[0]["page"],"physical_folio":rr[0]["physical_folio"],"line_count":len(lr),"field_count":len(rr),"group_count":sum(int(x["field_group_count"]) for x in rr),"dy_fields":sum(x["line_field_end"]=="DY" for x in rr),"line_end_fields":sum(x["line_field_end"]=="LINE_END" for x in rr),"formal_parse_json":j(parse),"content_assignment":"UNASSIGNED"})

 evidence=[
  {"claim_id":"HIERARCHY","status":"CONFIRMED_FORMAL","claim":"page > mechanical record > physical line > field > source group","support":"GDT227 complete parse; 33 records, 240 lines, 701 fields, 1896 groups","limit":"record and field are formal units, not linguistic paragraphs or clauses"},
  {"claim_id":"GROUP_FACTOR","status":"CONFIRMED_FORMAL","claim":"group = compiler coordinates applied to opaque PAGE_HOST","support":"HPR2/GDT227 full coverage","limit":"factorization is source-native formal parsing, not morphology or semantics"},
  {"claim_id":"RECORD_FINGERPRINT","status":"EXPLORATORY_REGISTER_LOCAL","claim":"compiler ecology carries within-page q13 record identity","support":"GDT264 compiler coarse top1 90/144 max6 p .0034","limit":"within-page exposed retrieval, strongest post-hoc block wrapper"},
  {"claim_id":"Q_RENDERER","status":"EXPLORATORY_REGISTER_LOCAL","claim":"q is a separable earlier-record-associated outer renderer in q13","support":"GDT270 exact host and other-compiler matching OR 3.030 max14 p .0448","limit":"Q20 transfer failed page gate; no semantic value"},
  {"claim_id":"Q_GLOBAL_STAGE","status":"WEAK_NONCONFIRMING_TRANSFER","claim":"q has a same-direction aggregate Q20 stage echo","support":"GDT271 aggregate positive but 7/13 pages, max3 p .1354","limit":"not a universal operator"},
  {"claim_id":"Q_DENSITY","status":"NOT_SUPPORTED","claim":"q marks a general expansion/density contrast","support":"GDT272 all three density predictors transfer in wrong direction","limit":"q function unresolved"},
  {"claim_id":"FIRST_ORDER_FIELDS","status":"NOT_SUPPORTED","claim":"coarse previous field state predicts the next field on an unseen q13 folio","support":"GDT273 all four held gains negative","limit":"nonrandom endpoint/size topology survives; higher order remains open"},
  {"claim_id":"CONTENT","status":"UNASSIGNED","claim":"PAGE_HOST or full tuple content value","support":"no independently repeated content endpoint","limit":"no word, role, language, plaintext, or translation"},
 ]

 schema={"experiment":"GDT274_Q13_EXECUTABLE_FORMAL_GRAMMAR","version":1,"start":"Q13_PAGE","productions":{"Q13_PAGE":["RECORD+"],"RECORD":["PHYSICAL_LINE+"],"PHYSICAL_LINE":["FIELD+"],"FIELD":["GROUP{1..}"],"GROUP":["COMPILER_CELL(PAGE_HOST)"],"COMPILER_CELL":["WRAPPER","O_OT_FRAME","INNER_D","PAGE_HOST","RIGHT_FAMILY","DY","B3"]},"opaque_symbols":["PAGE_HOST"],"nonlinguistic_boundaries":["source separator","DY-derived field boundary","physical line reset","mechanical record boundary"],"semantic_assignments":{},"unsupported_rules":["portable first-order coarse field-state chain","universal q record-stage operator","q density/expansion value"],"sealed_folio":"f84r"};schema["content_hash"]=chash(schema)
 write("gdt274_q13_record_parses.tsv",record_rows);write("gdt274_q13_line_templates.tsv",line_rows);write("gdt274_evidence_registry.tsv",evidence);(R/"gdt274_grammar_schema.json").write_text(json.dumps(schema,indent=2,sort_keys=True)+"\n")
 examples=[]
 for x in records["Q13|f75r|R01"][:6]:examples.append({"record_id":x["record_id"],"field_ordinal":x["field_ordinal"],"locus":x["locus"],"field_group_count":x["field_group_count"],"endpoint":x["line_field_end"],"source_tokens":x["source_tokens"],"page_hosts":x["page_hosts"],"compiler_cells":x["compiler_cells"],"semantic_parse":"UNASSIGNED"})
 write("gdt274_representative_parses.tsv",examples)
 summary={k:{"unique_templates":len(freqs[k]),"cross_folio_types":sum(len(v)>=2 for v in folios[k].values()),"line_occurrences_seen_other_folio":sum(len(folios[k][template(ll,k)])>=2 for ll in lines.values())} for k in kinds}
 report=["# GDT274 — executable q13 formal grammar checkpoint","", "Status: **Q13_HIERARCHICAL_TEMPLATE_GRAMMAR_CHECKPOINT**.","","## Executable inventory","",f"The grammar parses **{len(records)} records**, **{len(lines)} physical lines**, **{len(rows)} fields**, and **{sum(int(x['field_group_count']) for x in rows)} source groups** on nine physical folios.","","```text","PAGE -> RECORD+ -> PHYSICAL_LINE+ -> FIELD+ -> GROUP+","GROUP -> COMPILER_CELL(PAGE_HOST)","COMPILER_CELL -> WRAPPER × O/OT × INNER_D × RIGHT × DY × B3","```","","Every content value remains `UNASSIGNED`.","","## What repeats across folios","","| line representation | unique templates | cross-folio template types | line occurrences with other-folio support |","|---|---:|---:|---:|"]
 labels={"RAW":"raw source groups","HOST":"PAGE_HOSTs","COMPILER":"compiler cells","COUNTS":"exact field sizes","COARSE":"S12/L3P + endpoint"}
 for k in kinds:report.append(f"| {labels[k]} | {summary[k]['unique_templates']} | {summary[k]['cross_folio_types']} | {summary[k]['line_occurrences_seen_other_folio']}/{len(lines)} |")
 report += ["","The sharp architectural fact is scale-dependent reuse.  All 240 exact raw, PAGE_HOST, and compiler-cell line sequences are unique, while 208/240 coarse size-plus-endpoint line templates have an identical realization on another folio.  Exact field-size sequences sit between them (124/240).  The manuscript therefore reuses a coarse line scaffold without repeating complete rendered sentences.","","## Current best grammar statement","","q13 is generated by nested physical records and lines, DY/line-end fields, and factored rendered groups.  Compiler ecology is record-local; `q` is a separable q13 outer renderer with an earlier-record tendency.  Neither coarse adjacent-field order nor the q density interpretation transfers.  This is closer to a record/template language than an ordinary sequence of independently meaningful words, but it does not identify what a record says.","","No word, clause, object, process, language, plaintext, meaning, or translation is assigned.  No f84r material was opened, retained, queried, joined, or scored.",""]
 (R/"GDT274_Q13_EXECUTABLE_FORMAL_GRAMMAR_REPORT.md").write_text("\n".join(report),encoding="utf-8")
 outputs=["gdt274_q13_record_parses.tsv","gdt274_q13_line_templates.tsv","gdt274_evidence_registry.tsv","gdt274_grammar_schema.json","gdt274_representative_parses.tsv","GDT274_Q13_EXECUTABLE_FORMAL_GRAMMAR_REPORT.md"]
 result={"experiment":"GDT274_Q13_EXECUTABLE_FORMAL_GRAMMAR","status":"Q13_HIERARCHICAL_TEMPLATE_GRAMMAR_CHECKPOINT","records":len(records),"physical_lines":len(lines),"fields":len(rows),"groups":sum(int(x["field_group_count"]) for x in rows),"folios":9,"line_template_summary":summary,"semantic_assignments":0,"claim_ceiling":"Executable formal hierarchy and reuse scale only; no linguistic word clause role meaning plaintext or translation.","f84r":{"new_access":False,"used":False,"scored":False},"inputs":{SRC:sha(SRC),**{x:sha(x) for x in CONTEXT}},"documents":{METHOD:sha(METHOD)},"implementation":{Path(__file__).name:sha(Path(__file__).name)},"outputs":{x:sha(x) for x in outputs}};result["content_hash"]=chash(result);(R/"gdt274_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":result["status"],"counts":[len(records),len(lines),len(rows)],"coarse":summary["COARSE"]},sort_keys=True))
if __name__=="__main__":main()
