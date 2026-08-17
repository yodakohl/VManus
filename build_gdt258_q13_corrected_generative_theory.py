#!/usr/bin/env python3
"""Bind the corrected q13 generative synthesis; reads only compact results."""
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent
INPUTS=["gdt243_result.json","gdt245_result.json","gdt246_result.json","gdt247_result.json","gdt249_result.json","gdt251_result.json","gdt253_result.json","gdt254_result.json","gdt255_result.json","gdt257_result.json"]
DOC="GDT258_Q13_CORRECTED_GENERATIVE_THEORY.md";OUTS=["gdt258_candidate_worlds.tsv","gdt258_evidence_matrix.tsv"]
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def main():
 d={p:json.loads((R/p).read_text()) for p in INPUTS};worlds=list(csv.DictReader((R/OUTS[0]).open(),delimiter="\t"));ev=list(csv.DictReader((R/OUTS[1]).open(),delimiter="\t"))
 assert worlds[0]["world_id"]=="HYBRID_DIAGRAM_LEGEND_PLUS_PARAGRAPH_RECORDS_WITH_SPARSE_RENDERED_REFERENCES" and all(x["semantic_assignments"]=="0" for x in worlds)
 assert d["gdt254_result.json"]["paragraphs"]==5 and d["gdt254_result.json"]["hpr2_fields"]==43
 assert d["gdt243_result.json"]["fields"]==51
 assert d["gdt247_result.json"]["exact_matches"]==3
 assert d["gdt255_result.json"]["size_threshold_correct"]==94 and d["gdt257_result.json"]["access"]["pristine_access_seal"] is False
 result={"experiment":"GDT258_Q13_CORRECTED_GENERATIVE_THEORY","status":"HYBRID_DIAGRAM_LEGEND_PLUS_PARAGRAPH_RECORDS_LEADS_CONTENT_CHANNEL_UNRESOLVED","leading_world":worlds[0]["world_id"],"candidate_worlds":len(worlds),"evidence_rows":len(ev),"corrected_pages":{"f80r":{"paragraphs":5,"labels":10,"hpr2_fields":43},"f82r":{"paragraphs":3,"labels":13,"hpr2_fields":51}},"exact_cross_scope_member_matches":3,"corrected_role_size_collapse":"94_OF_94","active_semantic_assignments":0,"next_required_evidence":"ONE_SOURCE_BOUND_INDEPENDENTLY_KNOWN_REFERENT_WITH_FULL_RENDERED_TUPLE_AND_CORRECTED_PARAGRAPH_QUERY","interpretation":"q13 is best modelled as a graphical legend layer plus independent paragraph/HPR2 records with sparse complete-group cross-scope reuse; content remains latent.","claim_ceiling":"Generative document architecture only; no field role object operation ingredient word language plaintext or translation.","f84r":{"prior_transient_parse_disclosed":True,"new_access":False,"used":False,"scored":False,"further_access_authorized":False},"inputs":{p:sha(p) for p in INPUTS},"documents":{DOC:sha(DOC)},"outputs":{p:sha(p) for p in OUTS},"implementation":{Path(__file__).name:sha(Path(__file__).name)}};result["content_hash"]=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(",",":")).encode()).hexdigest();(R/"gdt258_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":result["status"],"leading_world":result["leading_world"]},sort_keys=True))
if __name__=="__main__":main()
